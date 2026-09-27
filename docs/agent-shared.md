# プロジェクト共通コンテキスト (Claude Code / Codex CLI 共通)

このファイルは **Claude Code と Codex CLI の両方** が読みます。
プロジェクトの **不変的な事実** だけを記載してください。
Claude / Codex 固有の動作プロトコルはここに書きません
(それぞれ `CLAUDE.md` / `AGENTS.md` に書きます)。

## プロジェクト概要

- **名称**: GSE (Generative Struggle Engine)
- **目的**: キーストローク動態から認知状態 (Flow / Incubation / Stuck) を推定し、
  **Nudge** (視覚的ヒント) と **Physical Anchor** (身体的回帰への方向づけ) で「生産的苦闘」を守る、
  **不便益を設計思想として引く** HCI フレームワーク
  (⚠️★★★ **Lv2 Wall は 2026-08-23 に削除された** — ADR-015。
   ⚠️★★★ **段階呼称 Lv1〜Lv4 は 2026-08-30 に廃止方向** — ADR-018 D7。★ **実体名で呼ぶ**。
   ⚠️★★★ **「*段階的* 介入」とも書かない** — Wall が消え、Physical Anchor が完了条件を持たなくなった
   (ADR-018 D1) 結果、**強度が単調に上がる「段」の構造は現存しない**。
   ★ **現行で稼働するのは Nudge のみ**で、**不便を担う Physical Anchor は未実装**。
   → ★ **「不便益 HCI である」とは書かない** — `docs/glossary.md` 禁止用語)
- **主要技術**: Tauri 2.0 + Rust (Backend: KB Hook / HMM / ONNX) + React/TypeScript (Frontend)
  + Python/PyTorch (ML 学習) + Flutter (ストレッチ: Physical Anchor)
- **ターゲット**: Windows 11 (Surface Pro 8 + Type Cover) + macOS 13+ (Accessibility / Input Monitoring)
- **チーム規模**: 小規模 (2-3 人)
- **重視する品質特性**: 正確性 (認知状態推定の精度、誤判定の最小化)
- **現フェーズ**: v0.3 較正 (キャリブレーション)。データ収集より先に設計懸念に対応する v2 再設計を実装中。

## アーキテクチャ要約

入力層 (`input/`) が OS 固有のキーボード/IME フックでイベントを捕捉し、Atomic + channel で
分析層 (`analysis/`) に渡す。分析層は 30 秒ローリングウィンドウで 5 特徴量を抽出し、HMM
(Forward Algorithm) で 3 状態確率を推定、1Hz ゲートで `FeatSnapshot` を生成する。`intervention`
が介入要否を判定し、`logger` が NDJSON にセッションを記録する。
⚠️ **Lv2 Wall と `wall_server.rs` は 2026-08-23 に削除された** (ADR-015)。現行の介入は **Nudge のみ**。
`analysis/` は **プラットフォーム非依存** (OS API は `input/` + `sensors*.rs` に隔離)。
詳細は `docs/architecture.md`。

## 主要ディレクトリ

- `src/` — React/TypeScript フロントエンド (UI / Tauri IPC のみ。ビジネスロジック禁止)
- `src-tauri/src/input/` — OS レベル入力キャプチャ (`hook_*` / `ime_*`、プラットフォーム固有)
  ★ 非打鍵チャネルもここ: `observe.rs` / `observe_windows.rs` / `observe_macos.rs` (フォーカス遷移・ポインタ)、
  `clipboard.rs` (文字数のみ)、`liveness.rs` (フック生存監視)
- `src-tauri/src/analysis/` — 認知状態推定 (features / engine / loop_step / intervention / probe_scheduler / metrics、OS 非依存)
  ★ 加えて `heads/` (**ADR-006: `task_kind` が domain head を選ぶ**・`writing.rs` / `coding.rs` が β を所有)、
  `key_gate.rs`、`pointer_bin.rs` (ポインタ 1 秒ビン)、`anonymize.rs` (`KeyCategory`)、
  `intervention_eval.rs` (HIR / Precision)、`calibration_eval.rs`、`cohort.rs`
- `src-tauri/src/` — `lib.rs` (統合・IPC・スレッド起動)、`logger.rs`、`schema_dto.rs`、
  `g1.rs` (G1 統制タスク実験モードの判定・OS API 非依存)、
  ★ **`o1.rs`** (**O1 = 継続的自然作業収集**・ADR-014)、`recording.rs` / `redaction.rs` (一時停止・区間削除)、
  `submission.rs` / `packaging.rs` / `reconcile.rs` (匿名化 → age 暗号化 → 提出)、`applog.rs`、`tray.rs`、
  `capabilities.rs` (収集能力の自己記述・ADR-013)、`overlay_panel.rs`
- `src-tauri/src/bin/` — `gse-replay` (回帰/評価 CLI)、`gse-cohort` (被験者横断判定)、`emit_schema` (JSON Schema 生成)、
  `gse-package` / `gse-unpack` / `gse-submit` (`--features package`)
- `docs/` — 永続ドキュメント (**21 md** + `architecture/` + `adr/` + `literature/` + `mitou_submission/` + ★ `theory/`)
  ★ `docs/theory/` は理論の文書（**theory candidate・`EH0`・SSOT の主張ではない**。2026-09-19 に `.idea/` から移した）
- `.steering/` — タスク単位の作業記録 (`[YYYYMMDD]-[task-name]/`)
- `.claude/` — Claude Code 用 (skills / agents / commands / hooks)
- `.codex/` — Codex CLI 用 (config.toml / hooks)
- `scripts/` — 同期・検証スクリプト (sync-session.* / check_schema_parity.py 等)

詳細は `docs/repository-structure.md`。

## 技術的制約 (厳守 — 両エージェント共通)

1. **Windows API**: `windows` crate (v0.58+) のみ。`winapi` は禁止
2. **macOS API**: `core-graphics` + `core-foundation`。低レベル FFI は `#[link]` 宣言
3. **unsafe**: Win32 API / macOS FFI 呼び出しに限定し、ラッパー構造体内に隔離
4. **フックコールバック**: Atomic 操作 + channel send のみ。ブロッキング禁止 (Win/mac 共通)
5. **GCD dispatch_sync_f**: メインスレッドからの呼び出し禁止 (デッドロック)
6. **TCC 権限**: Input Monitoring → Accessibility のフォールバックチェーンを維持
7. **他プロセスの TSF composition は観測不可 / グローバルフックによる `WM_IME_*` 傍受も禁止** (Windows のみ)
   - ⚠️★★★ **2026-08-22 に理由を訂正した。** 旧文は「グローバル TSF フック禁止: **UIPI でブロックされる**」だったが、
     ★ **UIPI の禁止リスト**（*Windows Integrity Mechanism Design* 逐語: window handle validation /
     `SendMessage`・`PostMessage` / thread hooks / journal hooks / **DLL injection** の 5 項目）に
     **TSF も COM も WinEvent out-of-context も含まれていない**。⚠️ かつ UIPI は
     「**at the same privilege (or integrity) level では一切干渉しない**」ので、
     同一整合性レベルの通常環境では**発動すらしない**。→ ★ **禁止の結論は変えないが、理由が違う。**
   - ★ **真の障壁はアーキテクチャである**: `ITfThreadMgr::Activate` は逐語
     「**Activates TSF for the calling thread**」であり、`ITfSource::AdviseSink` に
     **リモート対象を指定する引数が構文上存在しない**。Microsoft 自身が
     「**To access the composition string managed in TSF, the assistive technology products must create
     the `ITfThreadMgr` in the process of creating the target TSF-enabled applications**」と明記している
     (*IME and TSF Accessibility in Windows XP*)。
     ⚠️ **権限を上げても・UIAccess を付けても・管理者で実行しても取得できない**（そういう API が無い）。
   - ⚠️ **唯一の迂回は自前 TIP（in-proc COM DLL）を全プロセスに常駐させること**だが、
     **仮名漢字変換エンジンの自作**・**32/64bit 二重配布**（⚠️ 片方欠けると*無音で失敗*）・
     コード署名・EDR 誤検知・被験者の入力方式の置換という代償があり、**採用しない**。
   - ⚠️ **DLL 注入を伴うグローバルフック**（`WH_GETMESSAGE` / `WH_CALLWNDPROC`）で `WM_IME_*` を拾うのは
     **別途禁止** —— ★ こちらは **UIPI 第 5 項（DLL injection）に直撃**する（旧文が部分的に指していたのはこれ）。
   - ★ **採る手段は WinEvent (`WINEVENT_OUTOFCONTEXT`)**: DLL 注入不要・プロセス跨ぎ可・
     **コールバック引数に文字列が 1 つも無く content-free が構造的に保証される**。
     詳細と macOS 側（**公開 API が存在しない**）は
     `.steering/20260821-workspace-behavior-triage/survey-input-channels.md §7`。
8. **Rust ログ**: `tracing` のみ。`println!` / `eprintln!` 禁止
9. **エラーハンドリング**: `anyhow::Result` を使用
10. **Tauri 2.0**: capabilities で権限管理。v1 allowlist は使わない
11. **レイヤー分離**: `analysis/` 内で OS API を直接呼ばない (OS 依存は `input/` + `sensors*.rs` + `overlay_panel.rs` + `lib.rs` の `#[cfg]` ブロックに限る（★ **不変なのは「`analysis/` に置かない」**）)

## コーディング規約サマリ

- 命名: Rust=`snake_case.rs` (プラットフォーム固有は `{module}_{platform}.rs`)、
  React=`PascalCase.tsx`、TS ユーティリティ=`camelCase.ts`、docs=`kebab-case.md`
- 1 関数 1 責任。TypeScript は `any` 禁止 (型を明示)
- エラーは握りつぶさず `anyhow::Result` で伝播。ログは `tracing`

詳細は `docs/development-guidelines.md` §1。

## テスト方針サマリ (Replay-as-Truth)

ゴールデンセッション NDJSON を `gse-replay` CLI で再実行し、`FeatSnapshot` 列の
**byte-equal 一致** で回帰保護するのが背骨。リプレイ 1 本が単体/統合/回帰/GT 評価/チューニングを兼ねる。

⚠️ ★ **`Cargo.toml` は repo 直下に無い (`src-tauri/` にある)。**
repo 直下で `cargo test --workspace` を叩くと
`error: could not find 'Cargo.toml' in <repo> or any parent directory` で**即座に空振りする**
(2026-08-06 に Windows / macOS の**両方で実測**)。→ 下記のどちらかで実行する。

```bash
cd src-tauri     # ★ 以下は src-tauri/ から実行する
# 回帰検証 (最優先)
cargo run --bin gse-replay -- tests/fixtures/minimal.ndjson --snapshot tests/snapshots/minimal.json
# 単体テスト
cargo test --workspace
# Schema drift check (gse-dataset 整合)
cargo run --bin emit_schema   # 出力を src-tauri/schema/current.json と byte-equal 比較
```

repo 直下から動かずに叩くなら `--manifest-path` を付ける
(★ `run.sh` はこの形を使っている):

```bash
cargo test --manifest-path src-tauri/Cargo.toml --workspace
```

- モード系フラグ (`--snapshot` / `--metrics` / `--segments` / `--intervention`) は相互排他
- HMM 挙動を変えたら `HMM_VERSION` を bump → ゴールデン再生成 → 差分が意図通りか `.steering/` に記録
- `input/` の OS フックは実機手動確認。`analysis/` は `cargo test` で両 OS 共通検証

詳細は `docs/development-guidelines.md` §3。

## git ワークフロー基本

- **メイン**: `main` (常にビルド可能)。作業ブランチ: `[type]/[task-name]`
  (type = feature / fix / refactor / docs / chore)
- **コミット**: `[type]([scope]): [説明]` + 本文 + `Refs: .steering/[YYYYMMDD]-[task-name]/`
  (type = feat / fix / refactor / docs / chore / test、scope = engine / hook / ime / overlay / frontend / logger / probe 等（⚠️ **2026-09-01: `wall` を削除** — ADR-015 D1）)
- 1 コミット 1 論理単位。バージョンは README changelog + 重要変更時にコミット末尾 `(vX.XX)`

詳細は `docs/development-guidelines.md` §2 / `git-workflow` Skill。

## データ repo (gse-dataset) 連携

セッション NDJSON は本リポジトリに **コミットしない**。共有アーティファクトは
`gse-replay --metrics --json` 出力 (`metrics.json`) のみで、
[mikotomiura/gse-dataset](https://github.com/mikotomiura/gse-dataset) (private) の
`metrics/P*/<os>/` に置く。NDJSON Schema は `schema_dto.rs` から `emit_schema` で機械生成
(CI が drift 検知)。キーストローク内容・NDJSON 生ログは外部 LLM に送信しない。
詳細は `docs/development-guidelines.md` §10 / `data-privacy` Skill。

## CI / 運用上の注意

- ⚠️★★★ **workflow は 2 枚ある** (2026-09-12): `ci.yml` (ビルド / テスト / リリース) と
  ★ `supply-chain.yml` (**週次**の供給網検知 = toolchain advisory / `cargo audit` / `npm audit`)。
  ⚠️ 後者は **branch protection が無いので門ではなく信号**であり、赤でもマージは止まらない。
  ★ 手元で同じ 3 本を回す手順は `docs/verification-runbook.md` §1 (g)。
- CI は GitHub Actions (`.github/workflows/ci.yml`) で稼働中。⚠️ ★ 2026-08-10 に
  「無料枠 (3000h) 超過でクラウド CI 利用不可」という**古い記述を訂正**した
  (PR #94 で `check` (windows / macOS) / `frontend-check` の実行を確認済み)。
- ⚠️★★ **手元の検証は CI の代替にならない。** macOS では `hook_windows.rs` が 1 行も
  コンパイルされず、逆に `#[cfg]` を付けないテストは**相手側の OS でも走る**
  (2026-08-10 に macOS 前提のテストが Windows CI で赤になった)。
  → OS ごとに規則が違うロジックは **両 OS に対のテスト**を置く
  (`docs/development-guidelines.md` §3)。
- Hook はすべて bash 前提。Windows では **git-bash 必須** (PowerShell では動かない)。

## 詳細ドキュメント (リンクハブ)

| ファイル | いつ読むか |
|---|---|
| `docs/functional-design.md` | 機能の意図・要件・ユースケースを確認したい時 |
| `docs/architecture.md` | アーキテクチャ・スレッドモデル・データフローを確認したい時 |
| `docs/repository-structure.md` | ファイル配置・命名規則・モジュール依存方向を確認したい時 |
| `docs/development-guidelines.md` | コーディング規約・テスト方針・レビュー基準を確認したい時 |
| `docs/glossary.md` | 用語の正確な定義を確認したい時 (禁止用語の確認も含む) |
| `docs/external-skills.md` | 公式 (anthropics/skills) 由来の Skill 一覧、外部 LLM 送信可否 |
| `docs/research-positioning.md` | 研究の問い・差分・主張範囲 (機会保存/学習効果の分離) を確認したい時 |
| `docs/preregistration-v0.3.md` | Phase1 の凍結された合否契約 (PreReg-1..8・GATE1–3) を確認したい時 |
| `docs/preregistration-p1-episode.md` | ★ **P1 の episode 定義パラメータ** (`W` / `q` / `B` / `hole_gap_ms` / `warmup_count` / 分位点の推定法 / `T1a` の窓) を確認する時。⚠️ **v0.3 とは別の契約**（向こうは較正スモークの合否、こちらは P1 の解析パラメータで**合否を判定しない**）。★ 値の SSOT は `src-tauri/prereg/p1-episode.json`（`gse-replay --features` が既定として読む）。一致は `scripts/check_prereg_parity.py` が検査する |
| `docs/wbs-verification-halfyear.md` | 検証の 26 週マイルストーン・WBS・改訂予定を確認したい時 |
| `docs/references.md` | 出典を引く / 追加する時 (中央書誌 SSOT・`[Pn]`/`[Vn]` 名前空間) |
| `docs/literature/_index.md` | 先行研究の精読カード一覧・各ラウンドの「やり残し」を確認したい時 |
| `docs/experiment-tracking.md` | 実験を回す / 記録する / 再現する時の規約 (`experiments/`) |
| `docs/adr/README.md` | 確定した設計判断 (**ADR-001〜036**) の根拠を確認したい時 |
| `docs/theory/README.md` | 理論（生成的返権論ほか・theory candidate）を読む時。⚠️ **SSOT の主張ではない**（RP §1 は問いとして参照するだけ） |
| `docs/architecture/gse-v2-overview.md` | v2 再設計 (ドメイン分離・介入決定エンジン) の全体像 |
| `docs/architecture/workspace-behavior-observation.md` | R3 (自然作業の常時収集) の観測空間・ラベル・評価設計を確認する時 (形成的トラック) |
| `docs/o1-deletion-ledger.md` | ⚠️★★★ **進行中の O1 の削除保証台帳**。被験者からの削除要求に対応する時（★ 同意文書が逐語で約束している「記録に残します」の実体） |
| `docs/g1-deletion-ledger.md` | ⚠️★★★ **G1 の削除保証台帳**。G1 の被験者からの削除要求に対応する時（★ O1 版と対になる文書・前提条件 8） |
| `docs/person-lifecycle-ledger-template.md` | 人単位のライフサイクル台帳（G1/O1 それぞれの進み具合・「やめた」「削除の求め」の記録）を構築・参照する時 |
| `docs/architecture/intervention-decision-engine.md` | 介入決定エンジン (Layer 5-7) の設計を確認する時 |
| `docs/architecture/domain-adapter-boundary.md` | ドメインアダプタ境界 (Layer 0-3) の設計を確認する時 |
| `docs/architecture/personalization-and-online-learning.md` | 個人化・オンライン学習 (ADR-008 / ADR-009) を確認する時 |
| `docs/architecture/task-adaptation-and-scope-gating.md` | task_kind 適応・scope gating (ADR-010) を確認する時 |
| `docs/verification-runbook.md` | ★ **リリース前・マージ前の検証**を上から実行する時 |
| `docs/pilot-runbook.md` | パイロットの受領 → 復号 → metrics 結合を行う時（★ `.age` の復号手順はここ） |
| `docs/calibration-smoke-runbook.md` | 較正スモークを回す時・研究者デバッグ起動の手順 |
| `docs/participant-setup-guide.md` | 被験者のセットアップを案内する時（★ **被験者向け文書は契約**） |
| `docs/loop-engineering.md` | issue 単位の自律ループを回す時（★ 用語 / Done・Stop / budget の SSOT） |
| `docs/design-history.md` / `docs/design-history.ja.md` | ⚠️ **履歴文書**。過去の実装 (v2.1–v2.22) を調べる時のみ（★ 現行仕様の根拠には使わない） |
| `docs/architecture/expression-channel.md` | 表現チャネル (媒体分離・PC↔スマホ境界・復帰後の差分の扱い・曝露予算) を確認する時。⚠️★★★ **決定は ADR-017 だけではない** —— ★ **現行の裁定は ADR-021 (未決 11 件を確定) / ADR-022 (層 A の媒体実装制約) / ADR-025 (層 A に数値を添えない) / ADR-026 (招待を差し出す PC 面の要件) / ★★★ ADR-027 (境界イベントの発火・初期同期・解除) / ★★★ ADR-028 (生存を信号で示さず、失効を曝露の契機で判定する ＝ `W-3` を閉じた)**。⚠️ **ADR-017 単独で読むと古い契約を掴む** (例: `level` の 4 値は ADR-021 D4 が「作業状態 3 値 ＋ `invitation` 二値」へ改訂済み。★ **発火条件「`level` が変わったときだけ」も ADR-027 D1 が「意味フィールドの組が変わったとき」へ改訂済み**)。★ ADR 本文は書き換えない規約なので、**必ず番号の大きい方まで読む** |

## 公式 Skill (Phase 2 で導入)

公式 Skill の一覧と「外部 LLM への送信可否」の単一真実源は `@docs/external-skills.md` を参照。
全て Apache 2.0 で送信制限なし。ただし NDJSON セッションログ・キーストローク内容は送信禁止
(`data-privacy` Skill 参照)。
