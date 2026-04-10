# tasklist: GSE デプロイ自動化

## 完了済み

- [x] GitHub Actions ワークフロー設計（v1 → v2 批判的再構築）
- [x] `cross-platform.yml` 削除
- [x] `ci.yml` 作成（check / build-windows / build-macos / release）
- [x] commit & push（main ブランチ）

## 未実施（次の手順）

- [ ] `git tag v0.1.0 && git push --tags` で初回リリース試行
- [ ] GitHub Actions で build-windows / build-macos が成功することを確認
- [ ] GitHub Releases に .msi と .dmg が添付されることを確認
- [ ] Windows PC でインストール・起動確認
- [ ] macOS で インストール・起動・Input Monitoring 許可・動作確認

## 今後のリリース手順（運用ルール）

### リリース時（バージョンアップのたびに実施）

```bash
# 1. 3ファイルのバージョンを統一（必須）
#    - package.json              "version": "X.Y.Z"
#    - src-tauri/tauri.conf.json "version": "X.Y.Z"
#    - src-tauri/Cargo.toml      version = "X.Y.Z"

# 2. コミット
git add -A
git commit -m "chore: bump version to vX.Y.Z"

# 3. タグ & プッシュ（CI が自動でビルド → Release 作成）
git tag vX.Y.Z
git push && git push --tags
```

### 各 PC でのインストール手順

**Windows**
1. https://github.com/mikotomiura/GSE-prototype/releases を開く
2. `gse-next_X.Y.Z_x64_en-US.msi` をダウンロード
3. 実行 → SmartScreen「詳細情報」→「実行」
4. スタートメニューから起動

**macOS (Apple Silicon)**
1. 同 Releases ページから `.dmg` をダウンロード
2. DMG を開いて Applications にドラッグ
3. 初回起動 → Gatekeeper に弾かれる
   → システム設定 → プライバシーとセキュリティ → 「このまま開く」
4. **Input Monitoring を許可（必須）**
   → システム設定 → プライバシーとセキュリティ → Input Monitoring → gse-next をオン
   → アプリを再起動
