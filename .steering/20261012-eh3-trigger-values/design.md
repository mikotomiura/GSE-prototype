# 設計: EH3 の招待の契機の値（試作の段）

## 1. 段の切り替え（研究者の決定: `eh3.mode` に目印を足す・判断 1 #2）

- `analysis/invitation.rs`: 契機の値の組 `Trigger { p_stuck, hold_ms }` を置き、`Trigger::MAIN`（0.60・30 秒＝これまでの定数）と `Trigger::PROTO`（試作の段）を持つ。`InvitationMachine::with_trigger` で段の値を渡す。`new()` と `Default` は本番のまま。
  - 区間の終わり（閾値未満が 60 秒）も段の閾値で決める（区間の始まりと同じ閾値。区間の定義を 1 つに保つ）。
  - `TickOutput::triggered` を足す（区間が契機を満たした tick。出したかどうかに依らない）。殻は使わず、記録にも書かない。数える道具だけが読む。
- `eh3.rs`: 印に任意のキー `trigger`（`main` | `proto`）。無ければ本番。重複・未知の値・空は他のキーと同じく拒む。`Assignment::trigger` に持つが、`canonical` には含めない（段を替えても、数えた稼働日の台帳を捨てない）。
- `lib.rs`: `InvitationRunner::new` に割り当ての段の値を渡す。
- `logger.rs` / `schema_dto.rs`: EH3 の `meta` 行に `invitation_trigger`（`"main"` | `"proto"`）を常に書く。解析で段を分けるため。EH3 でない記録は 1 バイトも変わらない。schema の再生成と gse-dataset 側との parity を確かめる。
- `metrics.rs` の `p_stuck_trigger: 0.60`（Stuck エピソードの定義）は変えない。

## 2. 値の根拠を数える道具

`src-tauri/examples/invitation_trigger_sweep.rs`（`cargo run --example` だけ・配布物に入らない）。`feat` 行と `key` 行の時刻と押下だけを読み、閾値 {0.50, 0.55, 0.60} × 継続 {10, 15, 20, 30 秒} の格子で本番の状態機械をそのまま回す。殻と同じく 30 秒以上の `feat` の欠けと 4:00 の日の区切りでセッションを区切る。出すのは集計の数だけ。

## 3. テスト

- 段ごとに、閾値ちょうど・継続ちょうどで出る、1 秒足りない・閾値をわずかに下回ると出ない（`each_stage_presents_exactly_at_its_threshold_and_hold`）。
- 試作の段だけが届く列で本番は出さない。区間の終わりも段の閾値で決まる。
- 本番の値（0.60・30 秒）と既定が本番であること。既存のテスト（本番の値で書かれている）が緑のまま。
- 印: 段の任意キー・重複・未知・空・大文字を拒む・`canonical` に入らず台帳を捨てない。
- `meta` の断片が `invitation_trigger` を持ち JSON として読める。
- 変異: 閾値の比較を `>` に・継続を 1 秒ずらす・`with_trigger` が段を無視する、で落ちることを確かめる。
