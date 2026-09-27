# 設計 — o1-release-tag-recut

v0.1.36 の手順（`.steering/20260927-g1-o1-release-and-o1-resilience/tasklist.md` T1・
`experiments/20260801-controlled-friction-task/distribution-tag.md`）をそのまま O1 に当てはめる。

- 変更対象: `src-tauri/Cargo.toml` / `src-tauri/tauri.conf.json` / `package.json` / `src-tauri/Cargo.lock`（版番号のみ）、`docs/o1-distribution-tag.md`（新設）。
- ⚠️ タグは merge 後の main コミットに打つ（版上げ PR の head ではなく）。ゲートは `origin/main` と比べるので、タグ以降に docs 以外のコード変更が無いこと。
- ⚠️ `docs/o1-distribution-tag.md` の追加は tag 後の別コミットになるが、ゲートが見るパスは `src-tauri/src` / `src-tauri/Cargo.toml` / `src` のみなので鮮度判定は赤くならない。
- テスト: O1 ゲート再実行（Done 条件）・Release 資産の byte レベル検証（`LC_ALL=C grep -a`・v0.1.36 を対照）・zip 展開後の独立再検算。
