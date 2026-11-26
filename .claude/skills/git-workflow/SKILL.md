---
name: git-workflow
description: >
  GSE プロジェクトの git 運用規約。コミットする・ブランチを作る・PR を出す・
  バージョン番号を付ける際に必須参照。以下の状況で必須参照:
  - コミットメッセージを書くとき（type/scope フォーマット確認）
  - 作業ブランチを作成するとき（feature/fix/refactor/docs/chore）
  - バージョン番号 (vX.XX) を付与するとき
  - .steering/ への作業記録を残すとき（Refs: の書き方）
  - main ブランチへのマージ前チェックリストを確認するとき
  - ★ タスク完了時に push → PR → CI 緑なら merge を行うとき（ルール 6・研究者の既定指示で自動実行）
  - git/Bash などターミナル系のツールを呼ぶとき（ツール呼び出し書式 antml:invoke の確認・冒頭§参照）
allowed-tools: Bash(git *), Bash(gh pr *), Bash(gh run *), Bash(gh api *), Read, Glob
---

# Git ワークフロー規約

## ⚠️ 最重要・ツール呼び出し書式 (Bash/git 操作の前に必ず確認)

git/Bash を含む**すべてのツール呼び出しは `antml:invoke` / `antml:parameter` という `antml:` 接頭辞付き
タグで出すこと**。`court` や 接頭辞なしの `invoke`、`parameter` で書くと**ハーネスがパースできず
"malformed / could not be parsed" でツールが実行されない**(2026-06-24 に多発・ユーザー強い指摘)。

- 開始タグ: `antml:invoke name="Bash"` / 引数: `antml:parameter name="command"` / 閉じ: `/antml:invoke`。
- **散文の直後の最初のツール呼び出しで誤記しやすい**。git コマンドを出す直前に書式を確認してから出力する。
- 1 ターンで連続失敗したら、書式を確認し直してから再送する (盲目的に再試行しない)。
- 関連メモリ: `feedback-tool-call-tag-format`。

## このスキルの目的

GSE の git 履歴を読みやすく・追跡可能に保つ。
コミットメッセージと .steering/ 作業記録を連動させることで、
実装の背景・意図が後から追えるようにする。

## 適用範囲

### 適用するもの
- すべての git コミット・ブランチ作成・マージ
- .steering/ 作業記録との連動

### 適用しないもの
- GitHub Actions / CI の設定（現時点では未整備）

---

## 主要なルール

### ルール 1: コミットメッセージフォーマット

```
[type]([scope]): [短い説明]

- 変更内容 1
- 変更内容 2

Refs: .steering/[YYYYMMDD]-[task-name]/
```

**type:**
| type | 用途 |
|---|---|
| feat | 新機能追加 |
| fix | バグ修正 |
| refactor | 振る舞いを変えないコード改善 |
| docs | ドキュメントのみの変更 |
| chore | ビルド・設定・依存更新 |
| test | テストの追加・修正 |

**scope（GSE 固有）:**

★ 規約上の一覧（`docs/agent-shared.md` = **SSOT**）:
`engine`, `hook`, `ime`, `overlay`, `frontend`, `logger`, `probe` 等

> ⚠️★★★ **`wall` は 2026-09-01 に削除された**（ADR-015 D1 で Wall / Zen Timer /
> `wall_server.rs` が全削除され、`InterventionAction` は `None / Nudge / Defer` の 3 値になった）。
> ★ SSOT は `docs/agent-shared.md` の「git ワークフロー基本」節
> （⚠️ 2026-09-12 まで **この Skill だけが追随していなかった**）。
> ★ 削除後に `(wall)` を使ったコミットは **0 件**（実測）。

> ⚠️★★★ **上の一覧は「コード領域」だけで、実績の大半を覆っていない。**
> ★ 直近 400 コミットの実測（2026-09-12・`git log --format=%s | grep -oE '^[a-z]+\([a-z0-9-]+\)'`）:
>
> | scope | 件数 | | scope | 件数 |
> |---|---|---|---|---|
> | `steering` | **113** | | `g1` | 11 |
> | `o1` | 24 | | `hook` | 9 |
> | `experiments` | 22 | | `ime` | 8 |
> | `mitou` | 17 | | `adr` | 7 |
> | `ci` | **16** | | `expr` | 6 |
> | `handoff` | 12 | | | |
>
> → ★ **迷ったら実測する**（上のコマンドを叩く）。⚠️ 一覧を暗記して当てはめない。
> ★ 新しい scope を作るのは、**既存のどれにも当たらないと確かめてから**。

```
// ✅ 良い例
feat(engine): add ONNX Runtime inference path (v3.0)

- analysis::engine の update() を ONNX Runtime に差し替え
- FeatureExtractor との境界は変更なし

Refs: .steering/20260415-onnx-migration/

// ❌ 悪い例
fix stuff
update engine
```

---

### ルール 2: ブランチ命名

```
[type]/[task-name]
```

```
// ✅ 良い例
feature/onnx-inference
fix/ime-polling-crash
refactor/feature-extractor
docs/add-glossary

// ❌ 悪い例
my-fix
test-branch
new-feature
```

---

### ルール 3: バージョニング

- README の changelog でバージョンを管理（v2.0〜）
- **重要な機能変更のコミット**にのみ `(vX.XX)` を末尾付与
- 細かい修正・docs 変更にはバージョン不要

```
// ✅ 重要機能変更（バージョン付与）
feat(metrics): add receipt_free_resumption competing-risk outcome (v0.32)

// ✅ 細かい修正（バージョン不要）
fix(engine): correct typo in emission matrix comment

// ❌ すべてのコミットにバージョンを付ける
fix(docs): fix typo (v2.22)
```

---

### ルール 4: main ブランチは常にビルド可能な状態を維持

main へのマージ前チェック:
- [ ] `cargo build` が成功する
- [ ] `cargo clippy` の警告がない
- [ ] `npm run build` が成功する
- [ ] フックコールバック内にブロッキング処理がない

---

### ルール 5: .steering/ との連動

.steering/ にタスク記録がある場合、コミットの `Refs:` にパスを記載する。
作業記録なしのコミット（typo 修正等の軽微なもの）は Refs 省略可。

---

### ルール 6: ★★★ タスク完了時の出荷フロー（**commit → push → PR → CI 緑なら merge** を自動で行う）

★ **研究者の既定指示（2026-09-26）**: 「push、PR、CI 緑なら merge。今後 Git 関連はこの形で動く」。
→ ★ `/finish-task` の Step 3（`/cross-review` ＋ security-checker ＋ テスト）が通ったら、**都度の承認を求めずに**以下を最後まで実行する。
⚠️ 下の「止まる条件」に 1 つでも当たったら**その場で止まって報告する**（★ 自動化は「緑のときだけ進む」であって「何としても通す」ではない）。

1. **commit**: 明示ステージング（`git add <具体的なパス>`。⚠️ `git add -A` / `git add <dir>` は使わない —— 作業ツリーに別トラックの未追跡物がある）。
   ★ `.codex/budget.json` の記帳は台帳なので**含めてコミットする**（⚠️ `git checkout --` で戻さない）。
2. **push**: `git push -u origin <作業ブランチ>`（⚠️ `--force` / `--force-with-lease` は使わない）。
3. **PR**: `gh pr create --base main --head <作業ブランチ>`。本文は `.steering/<task>/` から要約（背景・変更点・検証方法・レビュー結果・残課題）し、末尾に attribution を付ける。
   ★ 同じブランチに open の PR が既にあれば新規作成せず、それに push したものとして扱う。
4. **CI 待ち**: `gh pr checks <番号> --watch`（★ self-hosted が offline なら 30 秒で hosted へ fallback する設計 —— memory `project_ci_exhausted`）。
   ★ チェックが 1 件も作られないまま数分経つなら、`gh run list --branch <作業ブランチ>` で確かめてから判断する（2026-11-19 から `feature/*` の push では CI が走らないので、出てくるのは PR の run だけ）。
5. **merge**: 全チェックが緑なら `gh pr merge <番号> --merge`（★ 既存の PR と同じマージコミット方式。⚠️ `--admin` / `--squash` / `--rebase` は使わない）。
6. **main の CI 発火確認**: `/finish-task` Step 5 を必ず実行する（★ run = 0 のまま「CI は緑」と書かない）。
7. **後片づけ**: `git switch main && git pull --ff-only`（★ 作業ブランチは消さない —— 研究者が消すまで残す）。完了報告に PR 番号・merge コミット・main の run を書く。

#### ⚠️ 止まる条件（★ 1 つでも当たれば merge しない・報告して判断を仰ぐ）

- CI のチェックが**赤**・キャンセル・タイムアウト（⚠️ 再実行で緑になるまで回す、はしない。1 回だけ原因を見て報告する）
- `/cross-review`・code-reviewer・security-checker の **CRITICAL / HIGH が未対応**、またはテストが赤
- push が non-fast-forward で拒否された（⚠️ force しない）／ merge が conflict・`mergeable: false`
- merge に `--admin` 等の保護の迂回が要る
- 現在のブランチが `main` そのもの（★ 先に作業ブランチを切る）
- ステージ対象に機密（`.env` / `*.pem` / `*.key` / credentials）や NDJSON 生ログが混ざる
- 研究者が「merge しないで」「PR まで」などと明示した（★ その指示が常に優先）

---

## チェックリスト

- [ ] type が feat/fix/refactor/docs/chore/test のいずれかか
- [ ] scope が GSE の既知モジュール名か
- [ ] 重要機能変更にはバージョン番号が付いているか
- [ ] ブランチ名が `[type]/[task-name]` 形式か
- [ ] .steering/ 記録があれば Refs: に記載したか
- [ ] main へのマージ前ビルドチェックを通過したか
- [ ] ★ タスク完了時は**ルール 6 の出荷フロー**（push → PR → CI 緑なら merge → main の CI 確認）を最後まで回したか。止まる条件に当たったら報告したか

---

## 補足資料

- `checklist.md` — マージ前の完全チェックリスト

## 関連する他の Skill

- `architecture-rules` — ファイル追加時の mod.rs 更新ルール

<!-- loop:begin -->
## Loop worktree policy
- **1 issue = 1 branch = 1 worktree = 1 PR**。混ぜない。
- base branch は `_loop-config.json` / `LOOP_BASE_BRANCH` で pin。既定は origin/HEAD→main→master。
- **dirty tree**: spawn 前に main checkout を commit/stash してクリーンに近づける (共有 index 事故防止)。
- **remote 同期**: spawn 前に `git fetch origin <base>`。長命な worktree は定期的に base へ rebase。
- **命名**: branch `loop/[id]-[short]` / worktree `../wt/[repo]-[id]-[short]`。
- **stale cleanup**: merge 後は `scripts/loop-spawn.sh --cleanup [id]` で worktree remove + branch -d + prune。
- ⚠️★★★ **worktree を切るときは `--task <task>` を名指す** (`scripts/loop-spawn.sh --task <task> <id>`)。★ `.steering/` に `_loop-config.json` が
  1 件以上あるときに落とすと **fail-closed で止まる** (⚠️ 旧実装は `tail -1` で黙って 1 つ拾い、
  **完了済みタスクの枝から worktree を切っていた** —— 2026-09-21・起票 23)。
  ★ `--cleanup` は `--task` を使わない（撤去は base の解決に到達しない）。
- **並行 resource 隔離** (`_loop-config.json.resource_isolation`):
  - `per-worktree` → DB 名 / port を worktree ごとに分離 (例 `PORT=$((5432+id))`、schema/db 名に id 付与)。
    GSE では Wall Server の待受ポート等が該当。
  - `serialize` → resource-heavy な test は排他ロックで直列化 (同時実行数は budget.parallel 内でも 1)。
    `gse-replay --snapshot` の対象ゴールデンが共有ファイルの場合はこちら。
  - 共有 fixture の破壊を避けるため、隔離できない test は AC recheck 時のみ実行する。
- この節は `.claude/commands/loop-issue.md` / `.claude/agents/loop-worker.md` / `scripts/loop-spawn.sh` /
  `scripts/loop-run.sh` から参照される SSOT。二重化しない。
<!-- loop:end -->
