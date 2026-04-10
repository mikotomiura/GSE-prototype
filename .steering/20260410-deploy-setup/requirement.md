# requirement: GSE デプロイ自動化

## 背景

GSE プロトタイプを自分の複数 PC（Windows + macOS Apple Silicon）で
いつでも実行できる状態にしたい。

## ゴール

- `git tag` を打つだけで Windows MSI と macOS DMG が自動生成される
- GitHub Releases からダウンロードしてインストールできる
- 署名なし（自分用）で動作する

## 受け入れ条件

- [ ] `git push` で cargo check が Win/Mac 両方通る
- [ ] `git push --tags` で GitHub Release に .msi と .dmg が添付される
- [ ] 各 PC でダウンロード → インストール → GSE が起動する
- [ ] macOS で Input Monitoring を許可すればキーボードフックが動く
