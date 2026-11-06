# 判断

## 判断 1: R1 の枝で直す（研究者の決定・2026-11-06）

候補は R1 の枝で直す／main への別の PR／記録だけ残して確かめを先に。研究者は R1 の枝を採った。R1 が main に入れば EH3 の設定の窓も直る。

## 判断 2: 除外の列挙から、本体の窓だけを許す形へ

元は `window.label() == "overlay"` だけを除いていた。設定の窓を足したとき（`f96c0675`・2026-10-11）に除外へ足し忘れて今回の事故になった。除外の列挙は窓を足すたびに足し忘れうるので、`main` だけで終える形にした。

## 判断 3: 確かめの記録（2026-11-06・AX で操作）

- 検査 `close_request_tests::only_main_window_close_shuts_down` は直す前に赤（設定の窓の場合）、直した後に緑。`cargo test --workspace` 1055 passed・0 failed、clippy 0、fmt 適用。
- 実機（開発版・識別子 `com.johnd.gse-next.dev`・記録は作業用のフォルダ）: 設定の窓の × で窓が隠れるだけでプロセスは生き続け、トレイから開き直せた（「出す」「出さない」の両方）。本体の窓の × では `main window close requested -> shutting down` で従来どおり終了した。
