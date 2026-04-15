# CI Matrix Build 拡充 — design

## 実装アプローチ

### 既存 `check` ジョブの置き換え

現行:
```yaml
check:
  strategy:
    matrix:
      os: [windows-latest, macos-latest]
  steps:
    - cargo check
```

変更後:
```yaml
check:
  strategy:
    matrix:
      include:
        - os: windows-latest
          target: x86_64-pc-windows-msvc
        - os: macos-latest
          target: aarch64-apple-darwin
  steps:
    - cargo build --target ${{ matrix.target }}
    - cargo test --workspace --target ${{ matrix.target }}
    - cargo run --bin gse-replay --target ${{ matrix.target }} -- tests/fixtures/minimal.ndjson --snapshot tests/snapshots/minimal.json
```

`strategy.matrix.include` 形式で OS ごとに target を明示的に紐付ける。ホストトリプル自動推論に頼らず、将来 Apple Silicon 以外でもズレない設計。

### 新規 `frontend-check` ジョブ

```yaml
frontend-check:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-node@v4 (node 22, cache: npm)
    - run: npm ci
    - run: npx tsc --noEmit
    - run: npm run build
```

Frontend は OS 非依存のため Ubuntu で十分 (実行時間最短、無料枠に優しい)。`npm run build` = `tsc && vite build` なので型検査 + Vite ビルドが同時に走る。

### キャッシュ戦略

既存 `Swatinem/rust-cache@v2` をそのまま使う。target ごとに別キャッシュが切られるため matrix include でも自然に動く。初回は Windows 8-10 分、2 回目以降 3-4 分。

### 既存ジョブへの影響

- `check`: 大幅拡充（cargo check → build + test + snapshot）
- `build-windows` / `build-macos` / `release`: **変更なし**。タグ push 時のみ走るリリースパイプラインの責務を維持

## 変更対象

### 修正するファイル

- `.github/workflows/ci.yml`
  - `check` ジョブ: `matrix.os` → `matrix.include` 形式、`cargo check` を 3 ステップに置換
  - 新規 `frontend-check` ジョブ追加
  - `env` / `concurrency` / `on` は変更なし

### 新規作成するファイル

- `.steering/20260415-ci-matrix-build/{requirement,design,decisions,tasklist}.md`

### 削除するファイル
なし

## 影響範囲

| 影響先 | レベル | 根拠 | 対処 |
|---|---|---|---|
| push/PR の CI 所要時間 | MEDIUM | cargo check (1-2 分) → build+test+snapshot (5-8 分) | キャッシュで 3-4 分に収束する見込み |
| 既存 tag push リリース | NONE | build-windows / build-macos / release ジョブは変更なし | — |
| 開発者体験 | POSITIVE | Windows build 失敗を main に入る前にブロックできる | — |
| Actions 無料枠 (private repo) | LOW | 10 分/回 × 月数十 push で ~300 分、2000 分枠に余裕 | public repo なら無制限 |

## 既存パターンとの整合性

- matrix 書式は既存 check ジョブの `strategy.matrix.os` を踏襲（include 形式に拡張）
- `dtolnay/rust-toolchain@stable` + `Swatinem/rust-cache@v2` の組み合わせは build-windows / build-macos と同じ
- Frontend ジョブは `actions/setup-node@v4` + `cache: npm` と既存 build ジョブの Node セットアップを踏襲

## 初回失敗時の想定

Windows で何か落ちる可能性の高い箇所:

1. `tauri-plugin-global-shortcut` の `RegisterHotKey` 呼び出し — 依存の `global-hotkey` crate が内部で Win32 API を使う。コンパイルは通るはず（クロス解決済み）
2. `windows` crate v0.58 の feature 指定漏れ — `Cargo.toml` の `[target.'cfg(windows)'.dependencies]` 内を確認
3. macOS 専用 `#[path]` 分岐が Windows 側で参照される事故 — `hook.rs` / `ime.rs` / `sensors.rs` の cfg を確認

失敗したら該当箇所を fix して緑化する。事前チェックとして設計レベルでの危険箇所リストを記録。

## テスト戦略

- **自己検証**: workflow 変更後に `feature/ci-matrix-build` ブランチで push して Actions の run を観測
- **初回緑化**: 失敗したら `cargo build --target x86_64-pc-windows-msvc` を手元の rust-cache にのせて再現（macOS からは `cargo install cross` + Docker 不要、Windows ターゲットはクロス不可なので Actions 経由でしか検証できない）
- **回帰検知**: 以降の push で Windows 固有の事故を自動検知

## ロールバック計画

- ci.yml の変更を `git revert` で即時ロールバック（tag push ジョブには手を触れないのでリリース機能は維持される）

## 既知の Open 点

- **Rust toolchain version ピン止め**: 現状 `dtolnay/rust-toolchain@stable` で latest stable。将来 rust 更新で壊れた場合は `toolchain: 1.82.0` のように pin する方針は別タスク
- **Artifact 出力**: check ジョブでのバイナリアップロードは不要（tag push の build ジョブが担当）
- **MSRV**: rust-toolchain.toml がプロジェクトルートにないので MSRV 未定義。将来必要になったら追加
