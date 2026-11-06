# 引き継ぎ —— M5 の 2 本目: 段 1 の駆動役と画面（計画の tasklist の B4・B5）

> 作成: 2026-11-06（Mac のセッション）。このメモを一次資料にしない。設計は計画の `.steering/20261105-gse-m5-probe-wiring-plan/`（design.md v2 ハイブリッド・decisions 判断 0〜10・tasklist の B4・B5）と、1 本目の `.steering/20261106-gse-m5-s1-core/`（design.md の「計画から変えた点」・decisions 判断 1〜10）。

## 0 入口の文

```
/Users/johnd/GSE-prototype/.steering/_handoff/next-session-gse-m5-part2-driver-ui.md を読んで、§2 から始めて。
```

（このファイルは 1 本目の枝 `feature/gse-m5-s1-core` にある。1 本目が main に入ってから読む。）

## 1 1 本目で入ったもの（main に入った後の前提）

- `s1.rs`（`resolve_with_eh3`・`is_s1()`）、起動時の判定（`lib.rs` の EH3 の判定の直後）、`meta.s1_mode`。
- `analysis/probe_arbiter.rs`（`Arbiter::tick(&TickInput) -> Vec<Action>`・`DayQuestion::on_pause`・`on_quit`・`on_closed`・`DayState`・`local_at`）。
- 行種 `probe_frame`・`probe_suppressed`・`day_question`（`LogEntry::DayQuestion(DayQuestionRow)`）、`SkipReason::Superseded`、`submission::s1_probe_consent_acknowledged`・`write_s1_probe_consent`。
- `o1::activity_label_allowed(stage1_mode, consent_ack)`（引数の意味を変えた）。

## 2 2 本目で必ずすること（1 本目で約束したこと）

1. capabilities: 送出元を作ったら `capabilities::tests::activity_label_has_no_emitter_until_it_is_wired` が赤になる。そのとき `activity_label`・`probe_frame`・`probe_suppressed`・`day_question` を `emitterless`（両 OS）から外し、段 1 のときだけ `config_gated` に入れる（EH3 の `eh3_line_types_are_declared_only_in_eh3` の型にならう）。検査を消す（1 本目の判断 2）。
2. `lib.rs` の段 1 の起動のログの文「this build records the mode only; ... NOT wired yet」を、駆動役を作ったら「問いを出す」に戻す（1 本目の判断 10）。
3. 6 択の送出元で `activity_label_allowed(crate::s1::is_s1(), crate::submission::s1_probe_consent_acknowledged())` を渡す。`o1::is_o1()` を渡さないことを本文の検査で縛る（security-checker の勧め）。
4. 駆動役が `TickInput` を作るとき: `local_day`・`local_minute` は `eh3::local_day`・`eh3::local_minute_of_day` で計算する。JST と UTC の両方の検査は駆動役の側に置く（1 本目の判断 4）。`key_presses_ms` は特徴量に流れるキーの押下だけ・昇順。`focus_transitions_ms` は `eh3::focus_row_allowed` で自分の窓を除いたもの（計画 design §1）。一時停止の間は `paused`、再開の tick は `resumed`、スリープの復帰は `power_resumed`。
5. `Action::ShowDayQuestion { in_window }` を `DayQuestionRow::in_eod_window` に写す。`shown_local_minute` は書かない（1 本目の判断 9・時差を出さない）。
6. `Action::SupersedeOpenStrat` で、開いている層化のカードの `realtime_label` と `activity_label` を `skip_reason = "superseded"` で書く。UI の `record_realtime_skip` は `superseded` を拒むので、段 1 の新しいコマンド（`record_probe_skip`）の側で書く。
7. security-checker の LOW 2 件を決める: (a) 同意の時点で出す `probe_frame` の行の `t` を、本人が押した時刻ではなく `anchor_ms`（ファイルを開いた時刻）にそろえるか。`probe_frame` は区間の削除で消えないので、`t` が本人の操作の時刻だと削除した区間の中の操作の事実が残る。推奨は `anchor_ms` にそろえる。(b) 同意の取り消し（印のファイルを消す）を登録の画面と一緒に置く。
8. 無作為が出たとき、日の問いのカードは駆動役が伏せて保ち、無作為に答えた後で出し直す（調停器は出し直しの指示を出さない。調停器は `DayQuestion` の中で出したまま閉じていない対象の日を覚えていて、日の切れ目で `CloseDayQuestion { day_end }` を出す）。日の問いのカードは通し番号 `card_id` で扱う: `ShowDayQuestion { card_id, .. }` を受けたら番号を持ち、閉じたら（回答・閉じる・終了・待ちの切れのすべてで）`day_question_mut().on_closed(card_id, target_day, answered)` を呼ぶ。`CloseDayQuestion { day_end }` のカードは調停器が既に覚えを捨てているので呼ばなくてよい。`open_card` は画面の実際（伏せている間は `Random`）を正しく渡す（「無い」と言うと調停器は覚えを捨てる）。
9. schema parity: gse-dataset の schema は EH3・R1・段 1 の行種を欠いている（2026-11-06 時点・R3 未了）。研究者の判断で R3 は 3 本目でまとめて行う。
10. 段 1 の回答率（S1-A4・A7）を出すとき（3 本目の `--probes` でも）、`superseded` を本人の未回答と分ける。`calibration_eval` の回答率は Phase1 用で、`superseded` を未回答に数える（1 本目では変えていない）。

## 3 残りの手順

計画の tasklist の B4（駆動役・`s1_day_state.rs`・コマンド・overlay・トレイの終了の補助）と B5（`ProbeCard.tsx`・`DayQuestionCard.tsx`・`Overlay.tsx`・`App.tsx`・登録の画面の同意の項目・画面の確かめ）。場面ごとに使うもの（Skill・レビュー）は計画の tasklist の B の表。UI を変えたら画面を見るまで完了にしない（macOS は AX と画面の取得、Windows は研究者の手か CI）。

## 4 守ること

- 返答・問い・記録は日本語で。決めることは AskUserQuestion で 1 問ずつ、推奨と理由を添えて。
- Codex に O1・段 1 の記録の本文を送らない。
- push は研究者に確かめてから。`src/` を変えるので PR に `[skip ci]` を付けない（Windows の CI は 11 月中 hosted）。
