# 判断

## 判断 1: R1 の枝で直す（研究者の決定・2026-11-06）

候補は R1 の枝で直す／main への別の PR／記録だけ残して確かめを先に。研究者は R1 の枝を採った。R1 が main に入れば EH3 の設定の窓も直る。

## 判断 2: 除外の列挙から、本体の窓だけを許す形へ

元は `window.label() == "overlay"` だけを除いていた。設定の窓を足したとき（`f96c0675`・2026-10-11）に除外へ足し忘れて今回の事故になった。除外の列挙は窓を足すたびに足し忘れうるので、`main` だけで終える形にした。

## 判断 3: 確かめの記録（2026-11-06・AX で操作）

- 検査 `close_request_tests::only_main_window_close_shuts_down` は直す前に赤（設定の窓の場合）、直した後に緑。`cargo test --workspace` 1055 passed・0 failed、clippy 0、fmt 適用。
- 実機（開発版・識別子 `com.johnd.gse-next.dev`・記録は作業用のフォルダ）: 設定の窓の × で窓が隠れるだけでプロセスは生き続け、トレイから開き直せた（「出す」「出さない」の両方）。本体の窓の × では `main window close requested -> shutting down` で従来どおり終了した。

## 判断 4: レビューの指摘の採否（2026-11-06）

code-reviewer（HIGH 無し）と /cross-review（Claude・Codex とも HIGH 無し。Codex は 1 回・21,317 トークン・メインの台帳へ写した）。

- 採る（MEDIUM・code-reviewer ／ LOW 2・Codex）: 判定の検査は「本体の窓の label が本当に main か」を守らない。→ `tauri.conf.json` を読み、label が `main`（label 無しを含む）の窓がちょうど 1 つあることを確かめる検査 `main_window_label_matches_tauri_conf` を足した。conf の label を `app` に変える変異で赤になることを見て、conf を戻した。conf に `"label": "main"` を明記する案は、検査で守れるので採らない（設定の差分を増やさない）。
- 採る（LOW）: builder の handler の上の注「overlay の × は無視する」と、定数の注の capabilities のファイル名（実際は `capabilities/invitation-settings.json`）が古い。直した。
- 採らない（LOW・Codex 1）: builder の handler がこの関数を使い続けるかは検査しない。handler は 1 行で、実機の確かめ（判断 3）で補う。

検証: `cargo test --workspace` 1056 passed・0 failed、clippy 0、fmt 適用。
