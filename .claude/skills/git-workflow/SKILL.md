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
  - git/Bash などターミナル系のツールを呼ぶとき（ツール呼び出し書式 antml:invoke の確認・冒頭§参照）
allowed-tools: Bash(git *), Read, Glob
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
`engine`, `hook`, `ime`, `wall`, `frontend`, `logger`, `features`, `analysis`

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
feat(wall): add early-unlock button to Zen Timer phone page (v2.21)

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

## チェックリスト

- [ ] type が feat/fix/refactor/docs/chore/test のいずれかか
- [ ] scope が GSE の既知モジュール名か
- [ ] 重要機能変更にはバージョン番号が付いているか
- [ ] ブランチ名が `[type]/[task-name]` 形式か
- [ ] .steering/ 記録があれば Refs: に記載したか
- [ ] main へのマージ前ビルドチェックを通過したか

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
- **並行 resource 隔離** (`_loop-config.json.resource_isolation`):
  - `per-worktree` → DB 名 / port を worktree ごとに分離 (例 `PORT=$((5432+id))`、schema/db 名に id 付与)。
    GSE では Wall Server の待受ポート等が該当。
  - `serialize` → resource-heavy な test は排他ロックで直列化 (同時実行数は budget.parallel 内でも 1)。
    `gse-replay --snapshot` の対象ゴールデンが共有ファイルの場合はこちら。
  - 共有 fixture の破壊を避けるため、隔離できない test は AC recheck 時のみ実行する。
- この節は `.claude/commands/loop-issue.md` / `.claude/agents/loop-worker.md` / `scripts/loop-spawn.sh` /
  `scripts/loop-run.sh` から参照される SSOT。二重化しない。
<!-- loop:end -->
