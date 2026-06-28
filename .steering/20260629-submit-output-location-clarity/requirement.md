# 提出ツール 出力先の明示と自動オープン

## 背景
被験者テストで gse-submit が `[OK]` を出したのに、生成された `.age` が「見当たらない」。
原因候補: ターミナル出力の見落とし、および Windows OneDrive / macOS iCloud による
「ドキュメント」フォルダのリダイレクト (USERPROFILE\Documents の実体が Explorer の
「ドキュメント」と異なる) で、出力先 `~/Documents/GSE-submissions/` を参加者が見つけられない。

## ゴール
1. 生成された `.age` の **絶対パスを目立たせて明示**する。
2. 生成後に **格納フォルダをファイルマネージャで自動オープン** (ファイルを選択状態で reveal)。
3. OneDrive/iCloud リダイレクトの可能性を一言案内する。

## 受け入れ条件
- `gse-submit` 成功時に絶対パスが明示され、Finder(mac)/Explorer(win) が当該ファイルを
  選択した状態で開く。
- 既存の匿名化/暗号化ロジック・出力先決定は不変 (表示と reveal の追加のみ)。
- `cargo build --features package --bin gse-submit` が通る。
