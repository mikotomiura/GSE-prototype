# 設計（v1）—— M5 の 2 本目: 段 1 の駆動役と画面

土台は計画の `.steering/20261105-gse-m5-probe-wiring-plan/design.md`（v2 ハイブリッド）と 1 本目の `.steering/20261106-gse-m5-s1-core/`。ここには 2 本目の組み方だけを書く。行番号は main `e067f4bc`。

## アプローチ

### 0 骨格

1. 駆動役は新しいモジュール `src-tauri/src/s1_driver.rs`（最上位・Tauri と IO を持つ。`analysis/` には置かない）。1 秒ごとに `TickInput` を作って `Arbiter::tick` を回し、`Action` を行と画面の状態に変える。
2. 画面の真実は backend が持つ。駆動役が「いま出すカード」を 1 つだけ持ち（`S1Card`: 無し・プローブ・日の問い）、変わるたびに `s1_card_changed` を emit する。画面は受けた状態をそのまま描き、起動直後とイベントの取りこぼしに備えて `get_s1_card` で引き直す。命令型のイベント（出せ・閉じろ）を並べない（伏せと出し直しの順序を画面に持たせない）。
3. 回答の行（`realtime_label`・`activity_label`・`day_question`）は `lib.rs` のコマンドが書く。6 択の行の構築（`activity_label_answered`・`activity_label_skipped`）は `lib.rs` に置く（O1 の配布の門 `check-o1-release-readiness.sh:124-139` の `EMITTER=lib.rs` と、`capabilities` の検査が見る場所）。駆動役が書くのは `probe_frame`・`probe_suppressed`・`probe_assignment` と `superseded` の 2 行だけで、`superseded` の構築は `lib.rs` の関数 `write_superseded_labels` を呼ぶ。
4. 状態の共有: `static S1_RUNTIME: Mutex<Option<S1Runtime>>`。中身は `Arbiter`・いまのカード・カードごとの控え（`probe_id`・`stratum`・窓・表示時刻・`card_id` など）・前の tick の一時停止。駆動役の tick とコマンドは同じ `Mutex` を取る（1 秒に 1 回と人の操作なので競合は小さい）。

### 1 起動と枠（`probe_frame`）

- 今のプローブのスレッドの条件に `is_s1()` を足す（`lib.rs:5726` の `probes_disabled` に `disabled_by_s1`、`tracing::warn!` の理由にも出す）。`capabilities.rs:133` の理由の表も合わせる。
- 駆動スレッドは `is_s1()` のときだけ起こす（`setup` の中・O1 の日次ローテートのスレッドの近く）。`GSE_DISABLE_PROBES` が立っていたら warn を 1 行（計画の判断 6）。EH3 との排他は `s1::resolve_with_eh3`（`lib.rs:4176-4189`）に頼り、コメントで指す。
- 同意の印（`submission::s1_probe_consent_acknowledged()`）が無い間は `S1Runtime` を作らない（行 0・カード 0）。
- 調停器を作る時: `anchor_ms = O1_LOG_OPENED_MS`、`frame_seed = frame_seed_from_entropy(rand::random())`、`probe_frame` の行の `t = anchor_ms`（本タスクの判断 1）。
- ローテート: `o1_rotate`（`lib.rs:1967`）で `S1_FRAME_GEN` を進める（`EH3_REEMIT_GEN` の隣・`lib.rs:2028`）。駆動役は世代が変わったら新しい seed と新しい `anchor_ms` で `Arbiter` を作り直し、日の問いの状態（`DayQuestion`）は `std::mem::replace(arbiter.day_question_mut(), …)` で引き継ぐ。開いているカードはそのまま（回答の行は新しいファイルに入る）。
- 同意を押した時点（記録の途中）: 判断 6 で「同意を押したら O1 のローテートを 1 回起こし、新しいファイルの起点で枠を作る」。そうしないと、起点（ファイルを開いた時刻）から今までの溜まった候補を一度に判定することになり、何時間も前の候補が「直前の 30 秒」として出うる（調停器は候補の時刻以前の最後の押下で離席を判定するので、古い候補が発火しうる）。ローテートにすると `t = anchor_ms` が本人の操作の時刻と近くなるが、ファイルを開いた時刻は `meta` に既にある（区間の削除でも消えない）ので、新しく残る事実は無い。

### 2 入力（`TickInput`）

- 押下: 分析スレッドの `out.key`（`lib.rs:4466-4471`・特徴量に流れる押下）のうち `is_press && !is_paused()` を、段 1 のときだけ `S1_KEY_TX`（`bounded(1024)`・`try_send`・溢れは数えて warn）へ送る。駆動役は tick ごとに drain して昇順に並べる。`LAST_KEY_MS` は使わない（全キーで更新され、1 秒の中の複数の押下を失う）。
- フォーカスの遷移: observe のドレイン（`lib.rs:5011-5034`）の絞り込みを `eh3::is_eh3() || s1::is_s1()` にし、通った遷移を段 1 のときだけ `S1_FOCUS_TX` へも送る（行に残る遷移と検出器が見る遷移を一致させる）。
- 一時停止: `recording::is_paused()`。前の tick との差で `resumed` を立て、止まった縁で `day_question_mut().on_pause(...)` を呼ぶ。
- 電源: `power::start` は 1 回しか登録できない（`input/power.rs:38-43`・2 回目は黙って何もしない）。EH3 の肖像（`lib.rs:4369-4372`）と段 1 は排他なので、段 1 の駆動役が `is_s1()` のときだけ自分の `rx` で `power::start` を呼ぶ。両方が同時に真になれないことを `s1::resolve_with_eh3` の検査と、呼び出しの直前の `debug_assert!(!eh3::is_eh3())` で示す。
- `local_day`・`local_minute`: 純粋な関数 `s1_driver::local_day_minute(now_ms, offset_secs) -> (i64, u32)`（`eh3::local_day`・`eh3::local_minute_of_day` を同じ `now_ms` から）。JST と UTC の検査を置く（引き継ぎ §2 の 4）。時差は `UtcOffsetCache`（`lib.rs:632`・`pub(crate)` にする）。
- `app_started`: 駆動役の最初の tick。`open_card`: いまのカードから（伏せている日の問いがあれば、無作為のカードを開いている間は `Random`・引き継ぎ §2 の 8）。

### 3 出力（`Action` → 行と画面）

| Action | 行 | 画面 |
|---|---|---|
| `Suppress` | `probe_suppressed` | なし |
| `FireProbe` | `probe_assignment`（`stratum` を写す・`session_elapsed_ms = scheduled_ts − anchor_ms`） | プローブのカード。窓は無作為なら今の `random_probe_window` と同じ形、層化は引き金の押下の時刻で終わる 30 秒 |
| `SupersedeOpenStrat` | `realtime_label`・`activity_label`（未回答・`skip_reason = superseded`） | 層化のカードを下ろす（次の `FireProbe` が上書き） |
| `ShowDayQuestion` | なし（閉じたときに書く） | 日の問いのカード。プローブが出ていれば伏せて控え、プローブが閉じたら出し直す |
| `CloseDayQuestion` | `day_question`（`closed_by = day_end`・`answered = false`） | 下ろす。持っていない `card_id` は無視 |

- `probe_id` は駆動役が entropy から作る（1 本目の判断 5）。
- 日の問いのカードは `card_id` で扱う。閉じたら（回答・閉じる・終了・待ちの切れ）`on_closed(card_id, target_day, answered)` を呼ぶ（引き継ぎ §2 の 8）。
- `in_window` を `DayQuestionRow::in_eod_window` に写す。`shown_local_minute` は書かない。
- 状態ファイル `s1_day_state.rs`: 起動時に読み（壊れていたら `DayQuestion::disabled()`）、tick の後に `arbiter.day_question().state()` が前回書いたものと違えば書く（一時ファイル → 置き換え → `sync_all`・`eh3::save_ledger` の作法）。

### 4 コマンド（`lib.rs`）

| コマンド | 門 | 書く行 |
|---|---|---|
| `get_s1_mode` | なし | なし（`{ s1, consent }`） |
| `get_s1_card` | `is_s1()` | なし |
| `acknowledge_s1_probe_consent` | `is_s1()` | 印のファイル・O1 のローテート（判断 6） |
| `revoke_s1_probe_consent` | `is_s1()` | 印を消す。`S1Runtime` を捨て、開いているカードを行なしで下ろす（本タスクの判断 2） |
| `record_probe_response(probe_id, q1, q2, category, latency_ms)` | `is_s1()`・`o1::activity_label_allowed(s1::is_s1(), submission::s1_probe_consent_acknowledged())`・`probe_id` がいまのカードと一致 | `realtime_label`（回答）＋ `activity_label`（回答） |
| `record_probe_skip(probe_id, reason, latency_ms)` | 同上。`reason` は `dont_remember`・`dismissed` だけ（`superseded` は拒む） | `realtime_label`（skip）＋ `activity_label`（未回答） |
| `record_day_question(card_id, motivation, closed_by, latency_ms, duration_ms)` | `is_s1()`・`card_id` がいまのカード | `day_question` |

- 6 択の門の引数に `o1::is_o1()` を渡さないことを、`lib.rs` の本文を `include_str!` で読む検査で縛る（引き継ぎ §2 の 3）。
- 一時停止の間はコマンドを拒む（行が落ちるため。カードは一時停止の間は下ろす）。

### 5 overlay の表示

- 段 1 で同意があるとき、`setup` の NSPanel 化（`lib.rs:5981-5988`）の後に、窓を画面外・1×1 に置いてから `show()`。同意を押したときも同じ手順。Overlay.tsx の idle の退避（D10）に任せる。先に置いてから見せるのは、Windows で透明窓が一瞬クリックを奪うのを防ぐため（impact-analyzer の指摘）。
- 段 1 でない走行では呼ばない（印の無い O1 の overlay は今のまま見せない）。

### 6 トレイの終了の補助（計画の判断 10）

- トレイの「終了」（`tray.rs:193-195`）だけを段 1 のとき `s1_driver::on_tray_quit(app)` へ渡す。時間帯の中・一時停止でない・カードが出ていない・当日まだ尋ねていない（`on_quit` が `Some`）なら、日の問いのカードを「答えて終了／答えずに終了」で出し、60 秒の時計を起こす。押されるか 60 秒で `shutdown_and_exit`。行は `shutdown` の前に書く（`End` の後は書けない）。
- 尋ねないときと、画面の「GSE を終了」・main の ×・2 度目のトレイの終了は、今のまま `shutdown_and_exit`。待っている間に別の終了経路が来たら、`closed_by = quit`・未回答の行を書いてから進む。
- `claim_shutdown` は待ちの後に取る（先に取るとトレイの更新が止まる）。

### 7 画面（B5）

- `src/s1Types.ts`（新規）: `S1Card` の判別共用体・6 択の固定の列（値と表示の文。表示の文は ADR-031 の「熟考・詰まり・外部資料・会話・離席・回答不能」と `logger::ActivityCategory` の doc）。
- `ProbeCard.tsx`: 今の `probe_triggered` の経路は変えない。段 1 のときは `s1_card_changed` を受ける内側のコンポーネント（同じファイル）で、Q1・Q2 の目盛りと 6 択を 1 枚に出す。文は「直前の30秒」。`stratum` は見せない。
- `DayQuestionCard.tsx`（新規）: 動機づけの 1 項目（1..5）・「答える」「今日は答えない」。終了のときは「答えて終了」「答えずに終了」。拾い直しのときは「昨日の作業について」。
- `Overlay.tsx`: 段 1 のカードの有無を `probeActive` と同じく箱の表示に入れる。プローブと日の問いは backend が 1 つしか出さないので画面では排他を持たない。
- 登録の画面（`RecordingControls.tsx` の O1 の登録の近く）: 段 1 のときだけ、問いへの同意の項目と取り消しのボタン。`App.tsx` で `get_s1_mode`。

### 8 capabilities とログ

- `activity_label`・`probe_frame`・`probe_suppressed`・`day_question` を `emitterless`（両 OS・`capabilities.rs:505-529`）から外し、`s1_line_types(is_s1())` を `config_gated()` に足す（EH3 の `eh3_line_types` の型・`capabilities.rs:270-296`）。検査 `activity_label_has_no_emitter_until_it_is_wired` を消し、`s1_line_types_are_declared_only_in_s1` を足す（引き継ぎ §2 の 1）。
- 起動のログの文（`lib.rs:4199`）を「問いを出す」に戻す（引き継ぎ §2 の 2）。

## 研究者が決めたこと（decisions 判断 4〜6）

- Q1（判断 4）: O1 の配布の門を段 1 に合わせて直す（本 PR）。
- Q2（判断 5）: 日の問いの文は「今日の作業にどのくらい熱意を持てましたか」1「まったく」〜5「とても」。拾い直しは「昨日の作業に」。
- Q3（判断 6）: 同意を押したら O1 のローテートを 1 回起こし、新しいファイルの起点で枠を作る。

## 変更対象ファイル

| ファイル | 変更 |
|---|---|
| `src-tauri/src/s1_driver.rs` | 新規。駆動スレッド・`S1Runtime`・入力の channel・`local_day_minute`・トレイの終了の補助・検査 |
| `src-tauri/src/s1_day_state.rs` | 新規。状態ファイルの読み書き（原子的・壊れていたら `Broken`） |
| `src-tauri/src/lib.rs` | `mod`・今のスレッドの条件・駆動の起動・押下とフォーカスの送り・`S1_FRAME_GEN`・`UtcOffsetCache` を `pub(crate)`・コマンドと登録・overlay の表示・起動ログの文・`write_superseded_labels` |
| `src-tauri/src/submission.rs` | `revoke_s1_probe_consent` |
| `src-tauri/src/capabilities.rs` | 宣言と検査 |
| `src-tauri/src/tray.rs` | 終了を段 1 で駆動役へ |
| `src/s1Types.ts`・`src/components/DayQuestionCard.tsx` | 新規 |
| `src/components/ProbeCard.tsx`・`Overlay.tsx`・`RecordingControls.tsx`・`src/App.tsx` | 修正 |
| `scripts/check-o1-release-readiness.sh` | 6 択の送出元が段 1 の門だけを通るなら O1 の承認の印を求めない・O1 の配布物に `s1.mode` が無い・selftest の対照（判断 4） |

## 既存パターンとの整合

- O1 の上の層は EH3 の先例（`eh3_focus_filter`・`EH3_REEMIT_GEN`・`load_ledger`/`save_ledger`・`eh3_line_types`）。
- 純粋な判断は `analysis/probe_arbiter.rs`、効果は駆動役（`o1.rs:13`・`eh3.rs:10` の作法）。
- 6 択の門は型 `EsmConsent`（`o1.rs:270`）。UI と IPC の両方で塞ぐ。
- カードの送信の失敗（カードを残して再押下）は今の `ProbeCard.tsx` に揃える。

## テスト戦略

- `s1_driver.rs` の純粋な部分: `local_day_minute` の JST・UTC（日の切れ目 4:00 の前後）、`Action` → 行の写し、カードの状態機械（伏せ・出し直し・`card_id` の照合・持っていない `card_id` の無視・回答で `on_closed`）、ローテートで日の問いの状態を引き継ぐこと、同意が無いと調停器を作らないこと。
- `lib.rs` の本文の検査: 6 択の門の引数（`s1::is_s1()` を渡し `o1::is_o1()` を渡さない）。
- `capabilities`: `s1_line_types_are_declared_only_in_s1`・既存の分割の検査。
- `s1_day_state.rs`: 往復・壊れたファイルで `Broken`。
- `cargo test --workspace`・clippy・fmt・`npx tsc --noEmit`・`emit_schema` の byte-equal・既存のゴールデンの `--snapshot`。
- 画面（macOS・自分で AX と画面の取得）: 段 1 と O1 の env と隔離した HOME で起動 → 同意の前はカードが出ない → 同意 → debug の口（`debug_force_s1_probe`・`debug_force_s1_day_question`・`ensure_debug_enabled` の下）で出す → 見える・押せる・背後のクリックを奪わない → 一時停止の間は出ない → トレイの「答えずに終了」が 60 秒以内に終わる → NDJSON の行を確かめる。Windows は CI と研究者の手。

## ロールバック

- PR を `git revert`。印 `s1.mode` が無ければ駆動スレッドは起きず、overlay も見せない。
