# 設計

- `lib.rs` に `fn close_request_shuts_down(label: &str) -> bool { label == MAIN_WINDOW_LABEL }`（`MAIN_WINDOW_LABEL = "main"`・tauri.conf.json に label が無いので Tauri の既定）を足し、builder の `.on_window_event` はこれが偽なら return する。
- 「overlay を除く」の除外の列挙から、「main だけで終える」の許可の形に変える。今後窓を足しても道連れにしない（除外の列挙は足し忘れると今回と同じ事故になる）。
- 窓ごとの handler（設定の窓の `prevent_close` と hide）は変えない。
- テスト: 判定の関数の単体の検査。変異（許可の形を元の除外に戻す）で赤になることを見る。実機は R1 の確かめの手順 3 で。
