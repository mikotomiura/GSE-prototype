# Tasklist

- [x] `.steering/20260606-gse-v2-opportunity-mvp/` を作成
- [x] requirement / design / tasklist を作成
- [x] `analysis::intervention` を追加
- [x] Rust state / Tauri command / logger / schema / replay を更新
- [x] Frontend を `InterventionDecision` 駆動へ移行
- [x] Nudge UI を全画面ビネットから右端サイドカードへ変更
- [x] docs を GSE v2 方針へ更新
- [x] README / README.ja を GSE v2 と side-card Nudge に更新
- [x] schema current を再生成
- [x] Rust / TypeScript の検証を実行
- [x] 結果を tasklist / final に記録

## 検証結果

- `cargo fmt`: PASS
- `cargo test`: PASS (69 lib tests + 9 replay tests)
- `cmd /c npm run build`: PASS
- `cargo run --bin emit_schema`: PASS (`src-tauri/schema/current.json` regenerated as UTF-8)
- 既存 warning: `src/input/ime_windows.rs::is_ime_active_check` is never used (今回変更由来ではない)
