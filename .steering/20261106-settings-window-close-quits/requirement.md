# 要件: 招待の説明と設定の窓を × で閉じるとアプリ全体が終わる

## 背景

2026-11-06、R1（`feature/nudge-default-off`）の実機の確かめ（手順 3）で、トレイの「印の説明と設定」から開いた窓（題名「GSE」・label `invitation-settings`）の × を AX で押したところ、アプリ全体が終了した。ログは `main window close requested -> shutting down`。

原因: `lib.rs` の builder の `.on_window_event` が、`CloseRequested` のとき `overlay` だけを除いて `shutdown_and_exit` を呼ぶ。設定の窓には窓ごとの handler（`prevent_close` して隠す）があるが、builder 側の handler も同じ事件で走る。EH3 の設定の窓を足した `f96c0675`（2026-10-11）から main にある。R1 はこの窓を通常のモードの第 2 週でも使う。

被験者が設定の窓を × で閉じると、記録がそこで止まる。

## ゴール

本体の窓（label `main`）が閉じられたときだけアプリを終える。他の窓（`overlay`・`invitation-settings`・今後足す窓）の close では終えない。

## 受け入れ条件

- [x] 終了するかの判定を純粋な関数にし、`main` で真・`overlay`・`invitation-settings` と未知の label で偽を検査する（先に赤を見る）
- [x] 実機で、設定の窓の × で窓が隠れるだけでアプリが動き続け、トレイから開き直せる
- [x] 本体の窓の × では従来どおり終了する（2026-08-08 の「窓を閉じても動き続けた」問題を戻さない）
