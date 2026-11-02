# GSE (Generative Struggle Engine) — CLAUDE.md

## このファイルについて

このファイルは Claude Code がセッション開始時に自動で読み込む指示書です。
**Claude Code 固有の動作プロトコル** に集中して書きます。

- プロジェクト共通の情報 (概要 / アーキテクチャ / 技術制約 / 規約 / テスト / git) は
  `@docs/agent-shared.md` を参照してください。Codex CLI も同じファイルを読みます。
- Codex CLI 固有の動作 (sandbox / approval / rescue) は `AGENTS.md` を見てください。

目的は **Claude が探索を始める起点を示すこと** であり、全情報を含むことではありません。

## 共通コンテキスト

@docs/agent-shared.md

(プロジェクト概要・アーキテクチャ・技術制約・規約・テスト方針・git ワークフロー・
公式 Skill 一覧 (`@docs/external-skills.md`) はここから参照されます)

## セッション開始時の行動規範

タスク/セッション開始時、メインエージェントは以下を **必ずこの順** で実行してください。
全部自分でやろうとしないこと。

1. **コマンド選定**: 今回の作業に該当するスラッシュコマンド (`/start-task`, `/add-feature`,
   `/fix-bug`, `/refactor`, `/review-changes` 等) があれば **必ずそれを起動する**。
   該当コマンドを使わずに作業を始めない。実装系タスクは必ず `/start-task` が先。
2. **docs/ の先読み**: 闇雲にコードを読まず、`@docs/agent-shared.md` のリンクハブから
   該当 docs を先に読んで文脈を把握する。
3. **Skill 参照**: 実装・レビュー・テスト等、該当する Skill があれば
   `.claude/skills/[name]/SKILL.md` を Read で参照してから手を動かす。
   GSE 固有領域には専用 Skill がある (下記)。公式 Skill で済む領域は自前を作らない。
4. **サブエージェントへの委譲**: 以下はメインではなくサブエージェントで実行する。
   ⚠️ **渡し方の契約は `subagent-delegation` Skill**（★ model の明示・範囲と禁止事項・締切）。
   - 複数ファイル横断の探索 → `file-finder`、影響範囲調査 → `impact-analyzer`、
     依存関係 → `dependency-checker`
   - レビュー → `code-reviewer` + `security-checker` を **並列**起動
   - テスト → `test-runner`、ビルド → `build-executor`、ログ解析 → `log-analyzer`
   独立した調査・レビューは 1 メッセージで並列に投げる。
5. **破壊と構築**: 設計判断・アーキテクチャ選択・難しいバグなど高難度タスクでは
   `/reimagine` をプラン段階で起動し、初回案を破棄して再生成した案と比較する (実装着手前専用)。
6. **Codex 併用**: 設計の第二意見は `codex-consult` (任意)、2 回以上詰まった実装の rescue は
   `codex-rescue` (要明示承認)。**diff の独立レビュー `/cross-review` は各タスク完了時に必須**
   (`/finish-task` Step 3 で code-reviewer と並んで起動。code-reviewer/security-checker だけで
   完了しない)。安全ゲート (proprietary/機密混入・予算超過・codex/jq 不在) でブロックされた場合のみ
   Claude 単独へ縮退し、**skip 理由を完了報告に明記**する。
   `docs/external-skills.md` で送信「禁止」の出力・NDJSON 生ログを Codex 入力に含めない。

## GSE 固有 Skill (必須参照)

| Skill | いつ参照するか |
|---|---|
| `architecture-rules` | `*.rs` 追加 / モジュール境界 / mod.rs 更新 / Tauri コマンド追加 |
| `rust-standards` | `src-tauri/src/` の Rust を書く (unsafe / windows crate / anyhow / tracing) |
| `typescript-standards` | `src/` の `*.tsx`/`*.ts` を書く (Tauri IPC / any 禁止) |
| `hook-constraints` | `hook_*.rs` / `ime_*.rs` のコールバック内 / Atomic フラグ操作 |
| `hmm-analysis` | `features.rs` / `engine.rs` の特徴量・遷移/放出行列・量子化 |
| `ml-workflow` | HMM チューニング根拠 / ONNX 移行 / Python 学習スクリプト |
| `intervention-design` | Nudge / 介入判定 / HIR (⚠️ Wall は ADR-015 で削除) |
| `data-privacy` | `logger.rs` / `hook.rs` / 匿名化 / 外部送信・ML データ収集 |
| `git-workflow` | コミット / ブランチ / バージョン / `.steering/` 記録 |
| `physical-anchor` | Lv3/Lv4 Physical Anchor / Flutter 連携 |
| `project-status` | 現在の git / タスク / 進捗を動的に把握したい時 |
| `implementation-workflow` | 実装タスクの共通骨格 (調査→設計→実装→テスト→レビュー) |
| ★ `verify-before-claiming` | **事実を断定する前**（「不要」「壊れる」「既知」「〜になる」）／削除・簡略化の提案／memory を根拠に使う時 ／ ★★★ **ADR・裁定・仕様を確定する時**（⚠️ **長い一次資料を 1 節だけ読んで代表させない**＝ルール 7 ／ ⚠️ **「核心」「閉じた」と書く前に同じ語で全文 grep**＝ルール 8。★ 2026-09-13 に ADR-030 で 2 回踏み抜いた） |
| ★ `browser-verification` | **`mcp__claude-in-chrome__*` を使う時**（最初の 1 回で必ず）／GAS・フォーム・シートの配備検証／生成 HTML の表示確認 |
| ★ `subagent-delegation` | **サブエージェントへ仕事を渡す *前*** （★ 下記 4 の実行時に必ず）／レビュー系の起動／サーヴェイの fan-out ／「投げるか自分でやるか」を迷った時。⚠️ **model の明示・範囲と禁止事項・締切・戻り値の裏取り**の契約 |

### 研究トラック Skill (docs/ の研究文書・`experiments/` を触る時)

| Skill | いつ参照するか |
|---|---|
| `citation-ssot` | 理論・手法・先行研究に依拠する記述を書く (`[Pn]`/`[Vn]` 採番・append-only)。⚠️★★★ **ADR も対象**（★ 先例 `ADR-010 D5` は [V66]/[V68]/[V69]/[V72] に接地。⚠️ ADR-030 は引用ゼロで書いて後から接地し直した） |
| `literature-card` | 論文/文献を精読してカード化する (`docs/literature/`・落合フォーマット) |
| `reproducibility-discipline` | `experiments/` 配下・較正スモーク・seed/lockfile/HMM_VERSION 固定 |
| `empirical-prompt-tuning` | Skill / コマンド / プロンプトを新規作成・大幅改訂した直後の検証 |
| `paper-write` | 論文の原稿を書く・組み直す・結果を入れる・指摘で改訂する時（投稿先の適合を一次で調べる・主張と新規性を先に確定・本文と補足資料を分ける・但し書きを 1 か所に・語数を測る）。直しは足すより移す |
| `attack-me` | 論文（`papers/`）の**事前登録を凍結する前**・原稿の外枠を書いた後・投稿の前・改訂の後のプレ査読（実在の論文で接地した立場の査読者 3 人＋本文だけを読む編集者 1 人（prereg では省く）＋意図の監査役・指摘は一次で裏取り）。⚠️ 実在の個人を名乗らせない・査読の結果を証拠にしない |

## 作業記録の運用ルール (重要)

**すべての実装作業は `.steering/` 配下に記録を残してください。**

- ディレクトリ: `.steering/[YYYYMMDD]-[task-name]/`
- 必須: `requirement.md` (背景・ゴール・受け入れ条件) / `design.md` (アプローチ・変更対象・
  テスト戦略) / `tasklist.md` (チェックボックス)
- 任意: `blockers.md` (詰まりと解決) / `decisions.md` (設計判断と根拠)
- 作成は `/start-task` で自動化、最終化は `/finish-task`。テンプレートは `.steering/_template/`。

## モデル選択ルール

| タスク種別 | モデル | 理由 |
|---|---|---|
| Plan Mode、設計判断、`/reimagine` | Opus | 推論深度が必要 |
| 実装、テスト、リファクタ | Sonnet | バランス最良 |
| リネーム、フォーマット | Haiku | 速度優先 |

## コンテキスト管理ルール

1. **`/context` を見る習慣**: セッション開始時・実装前・compact 前に使用率を確認する。
2. **タスク切り替え時は `/clear`**: 文脈が変わるなら `/compact` ではなく `/clear`。
   (本機は 1M context モデル。区切りごとの惰性的な圧縮より、タスク境界での `/clear` を優先)
3. **長大化したら `/smart-compact`**: 単一タスクが長引き使用率が高くなってきたら、設計判断・
   進捗を保持したまま `/smart-compact` で中間圧縮する。
4. **Plan → Execute の徹底**: 複雑なタスクは Plan Mode (Opus) で計画承認 → Sonnet で実装。

## 禁止事項

- 既存のテストを無断で削除しない
- ドキュメント化されていない設計判断を勝手に変更しない
- `.steering/` への記録を省略しない
- 曖昧な指示に対して推測で実装しない (質問する)
- `analysis/` 内で Windows API / macOS フレームワークを直接呼ばない (OS 依存は `input/` に閉じる)
- `winapi` crate / `println!` / `eprintln!` / `any` 型を使わない (詳細は `@docs/agent-shared.md`)

## Hook による自動強制

Hook は 3 層で動作し、全層の出力がユーザーに明示される (Windows は git-bash 必須):

1. **Preflight** (`UserPromptSubmit`): 毎ターン タスク状態・git 状態を表示
2. **Guard** (`PreToolUse`): Edit/Write 時に `[guard] PASS` または `BLOCKED:` を明示
3. **Report** (`PostToolUse` / `Stop`): cargo fmt 適用報告、clippy/tsc 結果

`BLOCKED:` で拒否されたらメッセージに従い修正して再試行。詳細は `docs/development-guidelines.md` §9。

## 利用可能なコマンド / サブエージェント

- **コマンド**: 実装=`/start-task` `/add-feature` `/fix-bug` `/refactor` `/reimagine`
  `/review-changes` `/cross-review` `/smart-compact` `/finish-task` /
  研究=`/literature-review` (サーヴェイ 1 ラウンド) (詳細は `.claude/commands/`)
- **サブエージェント**: 収集=`file-finder` `dependency-checker` `impact-analyzer` /
  レビュー=`code-reviewer` `test-analyzer` `security-checker` `cross-reviewer` /
  実行=`test-runner` `build-executor` `log-analyzer` /
  研究=`paper-reviewer` (`attack-me` の査読者役・編集者・監査役。道具は Read・Grep・Glob だけ) (詳細は `.claude/agents/`)

<!-- loop:begin -->
## Loop Engineering (issue 単位ループ)

複数 issue に割って自律ループで回す作業は、**必ず** `docs/loop-engineering.md` を Read してから
始めてください (用語 / Done・Stop / budget / events 契約 / モデル割当の単一 SSOT)。

- **入口**: `/start-task` の grill でゴールを確定 → `to-prd` → `to-issues` で縦切り issue に分解する。
  曖昧なゴールのままループを回さない (間違った方向に効率よく走るだけ)。
- **分解は Opus**: issue-slicing は切り方を誤ると全ループが無駄になるため Opus で行う。
  7 基準 (縦切り / 粒度 / Allowed Files 非交差 / AC↔test / verify_level / DAG / 単独 merge 可) は
  `docs/loop-engineering.md` を参照。
- **セッション境界**: issue 分解と loop 実行は **別セッション**。分解が終わったら `/clear` し、
  新セッションで実行を始める。設計文脈を実行に持ち込まない。
  *issue ファイルだけを読んで実行が成立しないなら、分解が失敗している。*
- **実行**: C(無人)=`bash scripts/loop-run.sh <task>` / B=新セッションで `/model sonnet` → `/loop-orchestrate` /
  A=端末ごとに `scripts/loop-spawn.sh --task <task> <id>` → `/loop-issue <id>`
  (⚠️★★★ **`--task` を落とすと fail-closed で止まる** —— 2026-09-21・起票 23) (GSE は A+B+C を採用・L5 で実体化)。
- **監視**: `/loop-status` が board の単一書き手。worker は events に append のみ。
- **done を自己申告で信じない**: `issue_done` は必ず `loop-watchdog` の客観再検証を通す。
<!-- loop:end -->
