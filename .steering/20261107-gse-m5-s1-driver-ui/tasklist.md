# タスクリスト —— M5 の 2 本目（駆動役と画面）

場面ごとに使うもの（完了の前にこの表と照合する）:

| 場面 | 使うもの |
|---|---|
| `*.rs` を書く | `rust-standards`・`architecture-rules`（`s1_driver.rs`・`s1_day_state.rs` の新規） |
| `lib.rs` の行・一時停止・自己申告の選択肢 | `data-privacy` |
| `*.tsx` を書く | `typescript-standards` |
| 区切りの点検 | `code-reviewer` ＋ `security-checker` を並列 |
| 完了 | `/finish-task`（`/cross-review`・Codex に記録の本文を送らない） |
| 画面の確かめ | macOS は自分で AX と画面の取得、Windows は CI と研究者の手 |

## R 駆動役（Rust）

- [x] R1 `probe_arbiter.rs`: `Arbiter::into_day_question(self)`
- [x] R2 `s1_day_state.rs`: 読み書き（原子的・`Broken`）と検査
- [x] R3 `recording.rs`: `PAUSE_EPOCH`
- [x] R4 `s1_driver.rs`: `S1Driver`（カードの状態・`open_card_for_arbiter`・`visible_card`・`apply -> Vec<Effect>`・`close_day`・一時停止・終了）・`local_clock`・遅れの切り出し・定数・検査（JST/UTC・伏せと出し直し・`card_id`・superseded の順・ローテート）
- [x] R5 `submission.rs`: `remove_s1_probe_consent`
- [x] R6 `lib.rs`: static（`S1_DRIVER`・`S1_FRAME_GEN`・`S1_PRESS_TX`・`S1_FOCUS_TX`・`S1_POWER_RESUMED_GEN`）・`o1_rotate` で世代・押下の送り・observe のフィルタ・電源の受け口のまとめ
- [x] R7 `lib.rs`: 駆動スレッド・`Effect` の実行（行の組み立て・6 択の門・emit・状態の保存）
- [x] R8 `lib.rs`: コマンド（`get_s1_mode`・`get_s1_consent`・`get_s1_card`・`acknowledge_s1_probe_consent`・`revoke_s1_probe_consent`・`record_probe_response`・`record_probe_skip`・`record_day_question`）と登録・一時停止のコマンドから `on_pause_requested`
- [x] R9 `lib.rs`: overlay の表示（画面外 1×1 → `show()`・`set_content_protected`）・`shutdown` の `s1_finish_before_end`・`request_quit` と `tray.rs`・起動ログの文（§2 の 2）・今のプローブのスレッドの停止条件・debug の口
- [x] R10 `capabilities.rs`: `s1_line_types`・`emitterless` から外す・検査の入れ替え（§2 の 1）
- [x] R11 本文の検査（6 択の門の引数・送出元の関数・`power::start` 1 回・停止条件）
- [x] R12 `scripts/check-o1-release-readiness.sh`: 判断 4 と selftest の対照
- [x] R13 `cargo test --workspace`・clippy・fmt・`emit_schema`・`--snapshot`

## U 画面

- [x] U1 `probeTypes.ts`: `S1CardState`・6 択・`DayTrigger`
- [x] U2 `ProbeCard.tsx`: 段 1 の 3 問 1 枚（props で受ける）
- [x] U3 `DayQuestionCard.tsx`
- [x] U4 `S1CardHost.tsx`・`Overlay.tsx`
- [x] U5 `RecordingControls.tsx`（同意と取り消し）・`App.tsx`（`get_s1_mode`）
- [x] U6 `npx tsc --noEmit`・`npm run build`

## V 確かめと点検

- [ ] V1 code-reviewer ＋ security-checker（並列）・指摘への対応
- [ ] V2 画面の確かめ（macOS）: 同意の前は出ない・見える・押せる・背後を奪わない・伏せと出し直し・一時停止・「答えずに終了」が 60 秒以内・取り消し・NDJSON の行
- [ ] V3 引き継ぎ §2 の 1〜8 の照合
- [ ] V4 docs（`functional-design.md`・`glossary.md` に新しい語があれば）
- [ ] V5 `/finish-task`（push と PR は研究者に確かめてから・`[skip ci]` を付けない）
