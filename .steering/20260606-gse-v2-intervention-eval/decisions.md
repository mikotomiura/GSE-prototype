# 重要な設計判断

## D1: p_stuck は logged feat から取る（design.md の「HMM 再生出力」を上書き）

- **判断**: `decide()` に渡す `p_stuck` は logged feat (`FeatSnapshot.p_stuck`) を使う。
  `run_replay` の virtual-clock step() 再生成は使わない。
- **根拠**:
  - logged feat には `p_stuck / f3 / f4 / f6 / timestamp` が全て揃っており、入力一式を
    **単一の wall-clock 時間軸**で再構成できる。
  - `.steering/20260416-replay-feat-alignment-bug/decisions.md` D1: virtual-clock の
    再生 feat は user_label と時刻軸が揃わず取りこぼす。GT join も logged feat の時間軸で
    行うため、p_stuck だけ別ストリームにすると 2 軸を再整列する必要が生じ、まさに同 bug を
    再導入する。
  - production の `decide()` も「engine 現在状態の p_stuck + 直近 logged feat の f3/f4/f6」を
    入力しており、logged feat の同一行から全部取る方が反実仮想として素直で忠実。
- **影響**: design.md「入力の再構成」の p_stuck 行を本判断で更新。ユーザー承認済み (2026-06-06)。

## D2: GT は point label から forward-fill で区間導出（range segments は失われている）

- **判断**: HIR / Precision の GT は、NDJSON の疎な point `user_label` を **forward-fill** で
  区間化して用いる。各 label がその時刻から次の label まで状態を保持するとみなし、
  先頭 label はセッション先頭へ、末尾 label はセッション末尾へ延伸して全区間をカバーする。
- **背景**: Phase 1 baseline で主力だった range GT (`.segments.txt`) は当時の手動ラベル付け
  セッションの一時成果物で、dataset の `labeled/` は空 (`.gitkeep` のみ)、`.range.metrics.json`
  (算出結果) のみ残り入力 segments は失われている。13 セッションに残る GT は point label
  (合計 ~83 個、1 セッションは 0 個) のみ。
- **却下案**:
  - point 厳密マッチのみ: defer-first の v2 では ACT が疎で、HIR の n が極小になり結論が出ない。
  - segments 手動再ラベル: 最高精度だが人手アノテーションが必要で本コーディングタスク外。
- **限界 (明記)**: 自己申告状態が次申告まで持続するという仮定を置く。本評価は verdict ではなく
  **screening**。0 label セッションは HIR/Precision 算出不能 (n/a・warning)。ユーザー承認済み。

## D3: 評価は decision×GT の 2×2 で、3 クラス macro-F1 は使わない

- ACT={nudge,wall} / HOLD={none,defer}、PROTECT={flow,inc} / STALL={stuck}。
- v2 のコストは非対称 (有害介入 ≫ 見送り) なので対称 macro-F1 は目的関数として不適。
- HIR = FP/(FP+TP) = ACT∩PROTECT / labeled-ACT（最重要・安全性）。
- Precision = TP/(TP+FP)。labeled-ACT 上で HIR+Precision=1 になる。
- coverage = labeled-decisions / total-decisions と act_unlabeled を併記して検定力を可視化。

## D4: idle_ms は key press 間隔から復元（production と同セマンティクス）

- production の `get_keyboard_idle_ms` は `now - last_key_ms()`、`last_key_ms` は **press** で更新。
- オフラインも `collect_key_timestamps`（press のみ収集）を再利用し、
  `idle = feat.ts - (直前 press ts <= feat.ts)`、無ければ 0。

## D5: 回復窓 W は暫定で DEFAULT_RECOVERY_WINDOW_MS (15分) を流用

- W の pre-registration は別タスク（スコープ外）。今回は素の指標算出までなので暫定既定値。
- セッション長 (1.5–8.5 分) では実質「session 末尾までに p_flow>0.5 へ回復したか」を測る。
- `compute_recovered_at`（p_flow>0.5 の最初の feat）を defer 区間先頭から再利用。
- **回復起点 = defer onset（区間先頭の timestamp）**。「defer 後 W 秒以内」の "後" は
  「defer を下した時刻から W 以内」と定義する。defer は `need=p_stuck>=0.60` のときのみ
  生じる（intervention.rs 分岐順）ため、run 内 feat は必ず `p_flow<=0.40<0.5` で回復閾値を
  満たさず、回復は構造上 run の後に限られる（code-reviewer HIGH#1 を不変条件で解消、
  intervention_eval.rs の evaluate_defer_runs doc に明記）。NUDGE_NEED_THRESHOLD を 0.50
  未満へ下げる場合のみ起点を run 終端へ要変更。

## D6: 評価ロジックは新規 `analysis/intervention_eval.rs` に分離

- metrics.rs を肥大化させず、intervention 評価専用の純関数群を新ファイルに置く。
- `analysis/` 内のみ依存 (loop_step / metrics / intervention)。OS API 無し・`anyhow` 不使用
  (bin 層と対称の軽量シグネチャ)。architecture-rules 準拠。
