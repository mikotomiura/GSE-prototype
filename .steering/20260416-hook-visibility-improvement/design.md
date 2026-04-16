# 設計 (v2: ゼロから再設計)

## 実装アプローチ: Preflight Dashboard 方式

根本発想: hook を「個別の番兵」ではなく「毎ターンのプリフライトチェック」として統合する。

### 核心のアイデア

**UserPromptSubmit を中央ゲートにする。** 毎ターン1つのスクリプトが全チェックを一括実行し、
構造化されたダッシュボード形式で結果を表示する。個別の hook は補助的な役割に留める。

```
[preflight] task: 20260416-hook-visibility-improvement (3/3 files)
[preflight] uncommitted: 2 files | design.md: edited 1h ago
[preflight] reimagine: applied (design-v1.md exists)
```

### 3 層構造

1. **Preflight 層 (UserPromptSubmit)**: `preflight.sh` が毎ターン実行
   - .steering/ タスクディレクトリの存在と必須ファイル (3/3)
   - 未コミット変更数
   - design.md がテンプレートのままかどうか
   - /reimagine 適用状態 (design-v1.md or design-comparison.md の有無)
   - 出力は常に 2-3 行のコンパクトなダッシュボード
   - **WARNING** は出すが **BLOCK はしない** (プロンプト送信自体をブロックすると作業不能になる)

2. **Guard 層 (PreToolUse)**: 既存の steering + banned チェックを維持
   - 変更点: パス時に 1 行の `[guard] PASS: steering (task: ...)` を出力
   - BLOCKED 時の動作は変更なし
   - Guard 層はファイル編集時のみ発火（従来通り）

3. **Report 層 (PostToolUse / Stop)**: 実行結果の報告
   - PostToolUse: `cargo fmt` 実行後、変更があった場合のみ `[fmt] formatted: N files` を表示
   - Stop: 既存の clippy/tsc チェックを維持（すでに明示的）

### なぜこの構造か

- **問題の本質**: ユーザーは「hook が動いているか」を毎ターン確認したい。しかし PreToolUse は Edit/Write 時にしか発火しない。質問やリサーチだけのターンでは一切出力がない。
- **解決**: UserPromptSubmit (毎ターン発火) を中央ゲートにすることで、**どんなターンでも**状態が見える。
- **BLOCK vs WARNING**: UserPromptSubmit で BLOCK すると作業自体ができなくなる（質問すらできない）。WARNING + 毎ターン可視化で「気づかない」問題を解決しつつ、作業は妨げない。
- **PreToolUse の PASS 表示**: 実際にファイル編集が走る時のみ、guard が通ったことを明示。

## 変更対象

### 修正するファイル
- `.claude/settings.json` — UserPromptSubmit を `preflight.sh` に差し替え、PostToolUse に fmt 報告を追加
- `.claude/hooks/pre-edit-steering.sh` — exit 0 の直前に `[guard] PASS` 行を追加
- `.claude/hooks/pre-edit-banned.sh` — exit 0 の直前に `[guard] PASS` 行を追加
- `docs/development-guidelines.md` §9 — 3 層構造の説明に更新
- `CLAUDE.md` — hook セクションに preflight の説明を追記

### 新規作成するファイル
- `.claude/hooks/preflight.sh` — UserPromptSubmit 用の中央チェックスクリプト

### 削除するファイル
- なし

## 既存パターンとの整合性

- 出力プレフィックスを統一: `[preflight]`, `[guard]`, `[fmt]`
- exit code 規約は維持: 0=通過, 2=BLOCKED (guard 層のみ)
- preflight 層は常に exit 0 (WARNING は出すが BLOCK しない)

## テスト戦略

- preflight テスト: .steering/ がない状態、ある状態、テンプレートのまま の 3 パターンで出力確認
- guard PASS テスト: 正常な .rs 編集で `[guard] PASS` が表示されることを確認
- guard BLOCKED テスト: println! を含む編集で BLOCKED が表示されることを確認
- fmt テスト: 未フォーマットの .rs を Edit して `[fmt]` 出力を確認

## ロールバック計画

settings.json と hooks/ を git revert。preflight.sh を削除。コア機能への影響なし。

## 設計判断の履歴
- 実行回数: 1 回目
- 採用: v2 (Preflight Dashboard 方式)
- 根拠: 毎ターン発火する preflight が「hook が動いているか分からない」問題を直接解決。Edit なしターンでも可視化される点が v1 にない決定的な利点。/reimagine 自動検出機能も v2 のみ。変更規模も小さい。
