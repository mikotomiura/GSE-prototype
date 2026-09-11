# タスクリスト — G-GEAR ブランチ取り込み

## 調査
- [x] `merge-base..branch` で規模を実測し直す (199 ファイル / +28,054 / −670)
- [x] main ⇄ branch の重複 23 件のうち、実際に内容が違う 6 件を特定
- [x] Rust 改名の実体と `FeatSnapshot` 非関与を確認
- [x] 下流の消費者 (`build_analysis_db.py` / fixtures / docs) を洗い出す

## PR-A `feat/ggear-intake-rust`
- [x] Rust 5 ＋ 下流の消費者を main の上に展開
- [x] `docs/architecture.md` の改名追随 (2 行)
- [x] `cargo fmt --check` / `clippy` / `cargo test --workspace` (599 passed)
- [x] `gse-replay --snapshot` × 6 本 byte-equal
- [x] ⚠️ 陽性対照で snapshot ゲートが赤になることを確認
- [x] `test_build_analysis_db` を duckdb 有りで skip=0 実行 (19/19)
- [x] 旧名 fixture (P104) が NULL 化しないことを実測
- [x] commit
- [x] push ＋ PR 作成

## PR-B `docs/ggear-intake-records`
- [x] steering / experiments / docs / ADR / scripts / .claude / .codex を展開
- [x] 衝突 6 件を判断 3・4 に従って解決
- [x] `secrets-filter-test.sh`
- [x] schema parity (`emit_schema` ↔ `schema/current.json`)
- [x] ADR 023–028 の番号衝突が無いことを確認
- [x] `citation-ssot` の採番衝突を確認
- [x] commit
- [x] push ＋ PR 作成

## スコープ外 (研究者判断)
- [ ] 2 本の PR の merge (CI 確認後)
- [ ] 引き継ぎメモ §3 の残雑務
