# EH3 の実装の後（読み替えの確認・実機の残り・ADR-035・見本の選択・凍結まで）

## 背景

EH3 の実装は PR #350〜#353 で main に入った（`.steering/20261011-portrait-eh3-impl/`）。
実装のタスクで研究者の決定を読み替えた点があり、Windows の実機の確認は自動でできる範囲だけが済んでいる。
引き継ぎ `.steering/_handoff/next-session-portrait-eh3-after-impl.md` §2 の手順を、凍結の直前まで進める。

## ゴール

- 実装のタスクの読み替え（判断 9）と稿 §10.1 の値を研究者が確かめた記録を残す。
- Windows の実機の残りを、研究者の了承と手を借りて確かめ、元の壁紙に戻ったことを確かめる。
- ADR-035 の見直しと Accepted、F-1・F-3 の選択、稿 §10 の残りを、研究者の決定の順に進める。

## スコープ

### 含むもの
- 引き継ぎ §2 の 1〜2・4〜6 の記録と、研究者の決定に従った文書の更新
- 稿 `experiments/20261011-portrait-eh3/preregistration-draft.md` §10.1 の確認の記録

### 含まないもの
- macOS の実機（Mac 用の引き継ぎ `next-session-portrait-eh3-macos-verification.md`）
- 研究者の決定の中身の変更（prereg の判断 1・2、impl の判断 1・2・3・6）

## 受け入れ条件

- [ ] 判断 9 の読み替えと稿 §10.1 の値について、研究者の決定が decisions.md にある
- [ ] Windows の実機の残りの結果と、元の壁紙に戻ったこと（パスと SHA-256）が記録にある
- [ ] ADR-035・F-1・F-3 の状態が研究者の決定どおりに記録されている

## 関連ドキュメント

- `.steering/20261011-portrait-eh3-impl/`（decisions 判断 1〜10・design §10〜11）
- `.steering/20261011-portrait-eh3-prereg/implementation-requirements.md`
- `experiments/20261011-portrait-eh3/preregistration-draft.md` §10・§10.1
- `docs/adr/ADR-035*`
