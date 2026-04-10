# design: GitHub Actions CI/Release パイプライン

## 実装アプローチ

`.github/workflows/ci.yml` に4ジョブ構成のワークフローを配置。

### ジョブ構成

```
push main/feature/* or PR
  └─ check (cargo check × Win + Mac, 20分タイムアウト)

push v* タグ
  ├─ build-windows (npx tauri build --bundles msi, 40分)
  ├─ build-macos   (npx tauri build --bundles dmg, 40分)
  └─ release       (GitHub Release 作成、片方成功でも実行)
```

### 設計判断

| 決定 | 根拠 |
|---|---|
| `tauri-apps/tauri-action` 不採用 | 部分失敗ハンドリング不可 + 黒箱でデバッグ困難 |
| `--bundles msi` / `--bundles dmg` | `targets: "all"` だと不要な成果物まで生成される |
| `CARGO_BUILD_JOBS=2` | ローカルは `jobs=1`（8GB RAM保護）だが CI は release profile で codegen-units=16 のため 2 並列可 |
| `Swatinem/rust-cache@v2` | 依存関係変化がなければ 20 分 → 3-8 分に短縮 |
| 独立ジョブ（matrix 不採用） | matrix だと片方失敗で release ジョブがスキップされる |
| `always()` + 個別 result チェック | 片方成功のみでも Release を作成できる |

### 変更ファイル

- **削除**: `.github/workflows/cross-platform.yml`
- **作成**: `.github/workflows/ci.yml`
