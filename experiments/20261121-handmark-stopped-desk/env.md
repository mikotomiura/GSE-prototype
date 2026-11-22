# 環境

- 漏れの机上の道具（`../20261115-handmark-leak-desk/env.md`）と同じ: Rust は `src-tauri/Cargo.lock`（`cargo build --bin gse-replay --bin gse-handmark-table`・debug）、Python は numpy 2.5.2（`requirements.txt`・venv は repo の外・`PYTHON` で変えられる）、Node は .ts の型を除いて読む版（22.18 以上）、`@napi-rs/canvas` 1.0.13（このディレクトリと漏れの道具のディレクトリの両方で `npm ci --ignore-scripts`。`overlay.mjs` は漏れの道具の `pixels.mjs` から読みと窓の値の関数を借りる）。
- HMM: `HMM_VERSION = 0.5.0`（漏れの検査の対象は記録の `feat`・合成では計算し直す）。
- 描画: `src/components/handmarkStageDraw.ts` の `drawFrame` → `src/components/handmarkStoppedDraw.ts` の `drawStopped`（画面と同じ純関数・同じ順・`scripts/handmark-stopped-draw.test.mjs` が順を縛る）。
- 合成の対照を回した機械（2026-11-22）: Windows 11（G-GEAR）・Python 3.13.13・numpy 2.5.2・Node 24.14.1。本人の記録を回す機械は回したときに書く。
- スレッド: BLAS の並列は 1 に固定（run.sh）。
