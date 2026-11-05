# 設計

- 停滞の分解の中間（打鍵の時刻と category・`pointer_bin`・`focus_transition`・観測区間・C0 の停滞の始まり）だけで作る。NDJSON は SHA-256 の照合だけ。
- `stall_onset.rs` の検出の構造（観測区間ごと・頭の W を評価しない・因果のプール分位・不応期）を Python に写した共通の検出器に、条件 A と θ の標本の流れを差し替えて C1・C6 を作る。C2 は C0 の停滞を C1 の条件 A で絞る。
- 写しの正しさは、同じ検出器で C0 を出して `gse-replay` の onsets と全件一致することで確かめる（止める）。
- 陽性対照は合成の記録（K7）と、変異で赤になることの確かめ。
- 出力は集計値だけ（`results/candidates.json`）。日の値は値で並べる。
- テスト戦略: `candidates.py --selftest`（`run.sh` が実データの前に走らせる）。
