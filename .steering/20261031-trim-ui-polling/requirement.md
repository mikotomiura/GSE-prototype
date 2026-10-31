# 要件 — 画面の 500ms ごとの取得から、使っていない分を削る

## 背景
- CPU の内訳（`.steering/20261030-gse-cpu-profile/` の results.md 6）で、記録中の増分（1〜3%）の大きな部分は、画面の 500ms ごとの状態の取得（`App.tsx` の統合ポーリング: `get_cognitive_state`・`get_keyboard_idle_ms`・`get_intervention_decision`）と見られた（相関で、因果は未確認）。
- 調べて分かったこと（2026-10-31）:
  - 主窓の `get_intervention_decision` は表示用の読み出しではなく、介入の判定を進める時計で、判定の行の記録もここで起きる。止めると通常運用で Nudge が出なくなる。
  - overlay の窓は判定の結果（`interventionDecision`）しか使わないのに、3 本とも取得している。overlay の判定の呼び出しは `last_decision` を読むだけ（`FORCE_NUDGE` のときだけ強制の判定を作る）。
  - O1 では介入を必ず切っている（`lib.rs` の O1 の初期化で `INTERVENTION_ENABLED=false`）。主窓の判定の呼び出しは安全な既定値を返すだけになる。
- 研究者の選択（2026-10-31・AskUserQuestion）: 「無駄な取得だけ削る」。判定の時計を Rust へ移す案は採らない。

## ゴール
- overlay の窓は `get_intervention_decision` だけを取得する。
- 主窓は、窓が見えない間（`document.visibilityState === "hidden"`）は表示用の 2 本（状態・無打鍵の時間）を取らない。判定の時計はそのまま 500ms で回す。
- O1 では、主窓が見えない間は判定の呼び出しも取らない。
- 見えるようになったら、次の 500ms を待たずにすぐ取り直す。
- 介入の振る舞い（判定の時刻・行の記録）を通常運用で変えない。

## 受け入れ条件
- 直す前後で、O1 の形の開発版の記録中の CPU（本体と WebKit の子）を、主窓が見える・最小化の 2 つの状態で 60 秒 × 2 ずつ測り、呼び出しの回数（一時的な計装 IPC-DIAG）とあわせて results.md に書く。
- 最小化で WKWebView の `visibilityState` が hidden になるかを、呼び出しの回数で確かめる（ならなければ、見えない間の削りは効かないと書く）。
- 通常運用（非 O1）で、主窓を最小化しても判定の呼び出しが 500ms ごとに続くことを、回数で確かめる。
- tsc・cargo fmt・clippy・cargo test が緑。計装は外してからコミットする。

## スコープ外
- 判定の時計を Rust へ移すこと。
- ダッシュボードの 1 秒ごとの表示の更新、ポインタのタップ、待ち合わせのスレッド（CPU の内訳の候補 3〜5）。
- Windows での計測（引き継ぎに書く）。

## 運用メモ
- /reimagine 適用: No
- 理由: 範囲を研究者が選び、判定の時計に触れない形に絞った。設計の選択肢はもう閉じている。
- G-GEAR の処理中なので PR は出さず push まで。枝は `fix/pause-auto-resume` の上に切った `refactor/trim-ui-polling`（両方が `App.tsx` を触るので重ねた）。
