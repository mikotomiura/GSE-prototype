# 設計

## アプローチ

文書だけの変更（コード・フォーム・凍結された事前登録には触れない）。

1. **段 1 の表**（`.steering/20261007-research-use-and-release/tier1-item-table.md`・新規）
   - 行 = 段 1 の候補の表現（`FeatSnapshot` のフィールド・30 秒窓の特徴量・`gse-replay` の出力の列・その他の中間表現）。
   - 列 = 中身・定義の一次（パス:行）・使う事前登録の数値（O1 / P1 / G1）・生の打鍵が要るか・公開の候補か。
   - 収集は Explore（sonnet）に委ね、戻り値の主要な行はメインが一次で裏取りする。
   - 2 本目の論文の解析計画ができたら差し替える前提を冒頭に書く。段 1 も関門（ADR-039 D6）にかける前提を書く。
2. **同意文 v2**（`consent-v2-draft.md`）: 第 2 層に集計値の点検、第 3 層を ADR-039 の 2026-10-09 の裁定と 2 つの実測に合わせて改訂（判断 2〜4）。
3. **ADR-039**: 本文は書き換えず、D4 の下に日付つきの注（第 3 層の語と対象・草案の改訂の所在）。
4. **issue #333**: コメントで結果を返し、本文のチェックボックスを更新する。

## 変更対象

- `.steering/20261007-research-use-and-release/tier1-item-table.md`（新規）
- `.steering/20261007-research-use-and-release/consent-v2-draft.md`
- `docs/adr/ADR-039-research-use-and-release.md`（注の追記だけ）
- `.steering/20261010-release-tier1-table-consent-v2/`

## テスト戦略

- 文書なので自動テストは無い。受け入れ条件（requirement.md）を、表の各行の一次の行番号と ADR-039 の裁定に照らしてメインが確かめる。
- /cross-review（Claude ∥ Codex）で、ADR-039 と同意文の矛盾、表の行と一次の食い違いを見る。
