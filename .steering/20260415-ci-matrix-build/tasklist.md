# タスクリスト — CI Matrix Build 拡充

## 準備
- [x] 既存 `.github/workflows/ci.yml` を精読、変更範囲を特定
- [x] 受け入れ条件と影響範囲を design.md にまとめ

## 実装
- [x] W-1: `check` ジョブの matrix を `include` 形式に変更 (os + target ペア)
- [x] W-2: `cargo check` を `cargo build --target ${{ matrix.target }}` に置換
- [x] W-3: `cargo test --workspace --target ${{ matrix.target }}` を追加
- [x] W-4: `cargo run --bin gse-replay --target ${{ matrix.target }} -- tests/fixtures/minimal.ndjson --snapshot tests/snapshots/minimal.json` を追加
- [x] W-5: 新規 `frontend-check` ジョブ (Ubuntu) を追加: npm ci + tsc + build
- [x] W-6: workflow yaml の lint 確認 (インデント・キー名)

## 検証
- [ ] V-1: push → GitHub Actions run を観測
- [ ] V-2: macOS 側緑確認
- [ ] V-3: Windows 側緑確認 (初回失敗時は fix 追加コミット)
- [ ] V-4: frontend-check 側緑確認
- [ ] V-5: 所要時間がキャッシュウォーム後に 5 分以内に収束

## レビュー
- [x] R-1: 既存 build-windows / build-macos / release ジョブが意図せず変わっていないことを diff で確認

## 完了処理
- [x] decisions.md: 採用した matrix 形式・snapshot を CI に含めた根拠を記録
- [ ] git commit + push (main 直 push で Actions をすぐ走らせる)
- [ ] Actions の run を URL で確認
- [ ] 結果に応じて CLAUDE.md の「技術的制約」セクションに CI の位置付けを追記 (任意)

## スコープ外 (別タスク)
- Rust toolchain pin 止め / MSRV 定義
- `cargo audit` 等のセキュリティスキャン CI
- コードカバレッジ
- Tauri build (bundle 生成) の push トリガー追加
