# 設計（v1）—— プローブの配線（ADR-031 M5）と日の終わりの問い

行番号は main（`be9f14de`）のもの。R1（`feature/nudge-default-off`・`767bdb67`）の行番号は「R1:」を付けて書く。値はすべて探索用の仮の定数で、確定は R6 の後の R6′（事前登録 S1-A1 ほか）。

## 0 一次で確かめた前提

| # | 事実 | 出典 |
|---|---|---|
| P1 | O1 でプローブが出ないのは、`start_session` が O1 で拒まれ `SESSION_START_MS` が 0 のままで、プローブのスレッドが `session_start == 0` で待ち続けるため。launcher の `GSE_DISABLE_PROBES=1` は多重防御で、Windows の自動起動には乗らない | `lib.rs:3443`・`lib.rs:5555`・`autostart.rs:17-19` |
| P2 | O1 で `SESSION_START_MS` を立てると、0 に戻す経路が無く、自動提出が止まる | `lib.rs:3438-3442` の注 |
| P3 | `realtime_label` などラベルの行は O1 では門で落ちる（`label_row_allowed(o1_mode) = !o1_mode`） | `o1.rs:233`・`lib.rs:2953/3155/3198/3310` |
| P4 | 6 択の門 `activity_label_allowed(o1_mode, consent_approved)` は型 `EsmConsent` を返す。同意の承認は「ビルド時の定数や true 直書きにしない」。今の承認の門は `scripts/check-o1-release-readiness.sh` の `<!-- o1-esm-consent: approved -->` | `o1.rs:245-270`・`check-o1-release-readiness.sh:106-134` |
| P5 | `LAST_KEY_MS` は特徴量のキーに限らず全てのキーで更新される | `hook_macos.rs:530-538`・`hook_windows.rs:581` |
| P6 | 無作為の時刻の生成は `ProbeScheduler::poll`。棄却の理由（away・too_early・gap・cap）は今は区別して返さない。乱数は `StdRng` で、招待の無作為の契機（R1 の `SplitMix64`）とは共有しない | `probe_scheduler.rs:365-410`・impact-analyzer の報告 |
| P7 | R1 は Nudge を既定で無効にし（R1:126）、O1 では明示的に false（R1:4136）。通常のモードの招待は `normal_invitation_allowed(declared, o1, g1, eh3, config)` で O1 を除く（R1 `invitation_trigger.rs:106`） | impact-analyzer の報告（R1 の行番号） |
| P8 | main の 188 コミットは `src-tauri/`・`src/` を変えていない（merge-base `3767e471`）。R1 の rebase の衝突は文書だけ | `git diff --stat 3767e471 origin/main -- src-tauri src` が空 |
| P9 | ローカルの日付の純粋な関数は `eh3::local_day(ts_ms, utc_offset_secs)`・`local_minute_of_day` にある（時刻帯は呼び出し側が OS から取る） | `eh3.rs:352-360` |
| P10 | 区間の削除は `realtime_label` を `ts`、`probe_assignment` を `scheduled_ts`、`activity_label` を `recall_window_*` ∪ `t` で消す。一時停止中は `is_writable_while_paused` が `recording_pause`・`meta` 以外を止める | `redaction.rs:164-208`・`recording.rs:64` |

## 1 実装アプローチ（v1 の骨格）

新しいモードを「O1 の変種」として作る。O1 の提出・自動起動・インストール ID・削除・日次のローテーション・Nudge と招待を出さない仕組みをそのまま使い、変種の印でプローブと日の終わりの問いだけを足す。

1. モード: 配布フォルダの `o1.mode` の隣に `s1.mode` を置くと、O1 の変種「段 1」になる（開発用は `GSE_O1_MODE=1` と `GSE_S1_MODE=1`）。`s1.mode` だけで `o1.mode` が無いときは、立てずに警告する（fail-closed）。`meta` 行に `o1_variant: "stage1"` を書く（今の O1 は書かない＝キーの不在が素の O1）。
2. プローブの起点: `SESSION_START_MS` を使わない（P1・P2）。段 1 では起点を「今のログファイルを開いた時刻」（日次のローテーションごとに更新）にし、プローブのスレッドはこの起点で `ProbeScheduler` を作り直す。`decide_probe_init` の session_meta の待ちは段 1 では飛ばす（O1 には較正の条件が無い）。
3. 門: `label_row_allowed` を「素の O1 では落とし、段 1 では通す」に改める。`activity_label_allowed` の第 1 引数を「段 1 か」に替え、素の O1 では `None`（ADR-043 D8）。同意の承認は配布フォルダの承認の印（`s1-consent.approved`）の有無を起動時に読み、配布物の門（`check-s1-release-readiness.sh`・O1 の門から分ける）が同意文書の承認の印との 1 対 1 を検査する。
4. 介入: 段 1 は O1 なので、R1 の仕組みで Nudge と招待は出ない（P7）。追加の配線は要らないが、検査で固定する（下の T-9）。
5. 問い: 毎回 Q1・Q2・6 択の 3 問を 1 枚のカードで。1 回の回答で `realtime_label` と `activity_label` を同じ `probe_id` で書く。
6. 無作為の枠と層化と問わない区間と日の終わりの問いを、`analysis/` の純粋な関数で調停する（§3）。
7. 抑制は `probe_suppressed` に記録する。日の終わりの問いは新しい行種 `daily_check` に記録する。問わない区間は `probe_holdout` に記録する（既定は無効なので、無効の配布物では 0 行）。

## 2 変更対象

### 修正するファイル

| ファイル | 何を変えるか |
|---|---|
| `src-tauri/src/o1.rs` | `S1_MARKER_FILE_NAME`・`decide_variant(o1, s1_marker, s1_env) -> Result<O1Variant, VariantConflict>`・`is_stage1()`・`label_row_allowed(o1_mode, stage1)`・`activity_label_allowed(stage1, consent_approved)`・`read_s1_consent_marker`（IO は呼び出し側） |
| `src-tauri/src/analysis/probe_scheduler.rs` | `poll` が `PollOutcome { Idle, Fired(FiredProbe), Rejected(RejectReason) }` を返す版 `poll_outcome` を足す（今の `poll` は薄い包みとして残し、乱数の列を変えない）。`RejectReason { Away, Warmup, Gap, Cap }` |
| `src-tauri/src/lib.rs` | プローブの起動の節（`5496-5665`）: 段 1 の起点・層化の判定・調停・`probe_suppressed` の送出・`probe_triggered` の payload に `stratum`。日の終わりの問いのスレッド（または同じスレッドの 1 Hz の段）。記録のコマンド `record_probe_answer`（Q1・Q2・6 択をまとめて受ける）・`record_daily_check_answer`・`record_daily_check_skip`。起動時の変種の判定と `meta` |
| `src-tauri/src/logger.rs` | 行種 `probe_suppressed`・`daily_check`・`probe_holdout` と整形の関数。`meta` に `o1_variant`。`ProbeStratum` は 3 値のまま |
| `src-tauri/src/schema_dto.rs`・`src-tauri/schema/current.json` | 上の 3 行種と `meta.o1_variant`。`current.json` は手で解かず `emit_schema` で作る |
| `src-tauri/src/capabilities.rs` | `activity_label` を `emitterless` から外し、`probe_suppressed`・`daily_check`・`probe_holdout` とともに段 1 だけの `config_gated` で宣言（`eh3_line_types_are_declared_only_in_eh3` と同じ型の `stage1_line_types_are_declared_only_in_stage1`） |
| `src-tauri/src/recording.rs` | `paused_blocks_every_data_line_type` の列挙に新しい行種を足す（新しい行種は既定で止まるが、検査は名前の列挙なので） |
| `src-tauri/src/redaction.rs` | `probe_suppressed` は `t`、`probe_holdout` は `[block_start_ms, block_end_ms]` と重なれば消す、`daily_check` は `shown_ts` か `answer_ts` が区間に入れば消す。別名の明示列挙（ADR-031 D6） |
| `src-tauri/src/bin/replay.rs` | `--s1-strata`: 記録（`key` 行の特徴量のキーと `focus_transition` 行）から層化の引き金を再現し、記録の `probe_assignment.stratum` と照合する。`--daily-check`: 日の終わりの問いの契機と、回答の後の打鍵の量を数える |
| `src/components/ProbeCard.tsx` | 6 択を足す（固定 6 択・自由記述なし・理由を問わない・ADR-031 D3）。文は「直前の30秒」を 6 択にもかける |
| `src/components/Overlay.tsx` | 日の終わりの問いのカードを同じ overlay の窓で出す（窓はカードの実寸に縮める既存の型） |
| `scripts/check-o1-release-readiness.sh` | 段 1 の門を別の `check-s1-release-readiness.sh` に分け、O1 の門は「`s1.mode` を含まない」ことを足す |
| `docs/architecture.md`・`docs/architecture/gse-design-map.md` | 段 1 の変種・新しい行種 |

### 新規作成するファイル

| ファイル | 役割 |
|---|---|
| `src-tauri/src/analysis/probe_stratify.rs` | 層化の引き金の純粋な状態機械（§3.2） |
| `src-tauri/src/analysis/probe_arbiter.rs` | 無作為・層化・問わない区間の調停（§3.3）と問わない区間の割付（§3.4） |
| `src-tauri/src/analysis/daily_check.rs` | 日の終わりの問いの契機と拾い直しの純粋な関数（§4） |
| `src-tauri/src/daily_check_state.rs` | 日の終わりの問いの状態（対象の日・尋ねた回数）を再起動をまたいで持つ小さなファイルの読み書き（IO） |
| `src/components/DailyCheckCard.tsx` | 日の終わりの問いのカード |
| `scripts/check-s1-release-readiness.sh` | 段 1 の配布物の門 |

`analysis/` に置くものは OS の API を呼ばない（時刻帯は呼び出し側が渡す・P9）。

## 3 C4 のプローブ

### 3.1 仮の定数（`analysis/probe_arbiter.rs` に集める）

| 名前 | 仮の値 | 事前登録 |
|---|---|---|
| 無作為の枠 | 既定の `ProbeConfig`（6 分空け・20 分に 2 回・最大 22 分） | S1-A1 |
| `LOW_OP_MIN_MS`（低操作の区間の長さ） | 90 秒 | S1-A1 |
| `RESUMPTION_MIN_MS`（フォーカスの遷移から打鍵の戻りまで） | 30 秒 | S1-A1 |
| `STRAT_GAP_MS`（直前のプローブからの空け） | 6 分 | S1-A1 |
| `STRAT_CAP`（層化の上限） | 60 分に 2 回 | S1-A1 |
| `STRAT_RANDOM_LOOKAHEAD_MS`（次の無作為の候補が近ければ層化を控える） | 2 分 | S1-A1 |
| `HOLDOUT_ENABLED` | false | S1-A6 |
| `HOLDOUT_BLOCK_MS`・`HOLDOUT_P` | 2 時間・0.2 | S1-A6 |

同意文書に書く 1 時間の最大の合計（判断 8）は、無作為の上限と層化の上限の和から求め、定数の検査（T-6）で固定する。

### 3.2 層化の引き金（`probe_stratify.rs`）

- 入力は 1 Hz の刻みごとに `(now_ms, last_feature_key_ms, last_focus_transition_ms, away)`。`last_feature_key_ms` は `key_gate::is_feature_key` を通ったキーの時刻で、`LAST_KEY_MS` は使わない（P5）。推定器の出力は読まない（ADR-031 D2）。
- `low_operation_end`: 特徴量のキーの無い区間が `LOW_OP_MIN_MS` 以上続いた後、特徴量のキーが戻った刻み。
- `resumption`: フォーカスの遷移の後、`RESUMPTION_MIN_MS` 以上たってから特徴量のキーが戻った刻み。両方に当たる刻みは `resumption` を優先する（遷移という追加の観測があるため）。
- 同じ関数を `gse-replay --s1-strata` が記録から呼ぶ。実機と再生で同じ引き金になることを検査する（T-3）。

### 3.3 調停（`probe_arbiter.rs`）

- 無作為の枠は `ProbeScheduler` だけが決める。層化と問わない区間は無作為の候補の時刻と件数を変えない（判断 8）。無作為の `poll_outcome` の `Rejected(reason)` は `probe_suppressed` に `stratum = random` で書く。
- 層化の候補は次のどれかで控え、`probe_suppressed` に `stratum = low_operation_end | resumption` と理由を書く: 直前 `STRAT_GAP_MS` に無作為か層化のプローブがある（`gap`）・層化の上限（`cap`）・次の無作為の候補が `STRAT_RANDOM_LOOKAHEAD_MS` 以内（`yielded`）・離席（`away`）・ウォームアップ（`warmup`）・問わない区間（`holdout`）・カードが出ている（`card_open`）。
- 無作為の候補が出た時に層化のカードが開いていたら、無作為を優先してカードを差し替える。層化の側は `realtime_label` の未回答（既存の `skip_reason` の値で `superseded` を足す）で閉じる。
- 判断 9 の理由の列（away / warmup / gap / cap / 層化が譲った）に、`holdout`・`card_open`・`superseded` を足すことになる。足すかは研究者に確かめる（§7 の 2）。

### 3.4 問わない区間（S1-A6・既定は無効）

- 日付と配布ごとの seed から、`HOLDOUT_BLOCK_MS` の塊ごとに確率 `HOLDOUT_P` で「問わない」を引く。塊の始まりに `probe_holdout`（`block_start_ms`・`block_end_ms`・`holdout: bool`）を書く。`HOLDOUT_ENABLED = false` の配布物では塊を引かず、行も書かない。
- 問わない塊の中の無作為の候補は `probe_suppressed`（`holdout`）に書く。無作為の枠の確保（S1-A1）との兼ね合いは、事前登録で決める。

### 3.5 カードと記録

- `probe_triggered` の payload に `stratum` を足す。カードは Q1・Q2・6 択の 3 問（ADR-031 D8 の上限）。
- 回答は `record_probe_answer(probe_id, q1, q2, activity)` 1 本で受け、バックエンドで `realtime_label` と `activity_label` を同じ `probe_id` で書く。6 択は `EsmConsent` が無ければ書かず、`realtime_label` だけを書く（その場合カードに 6 択を出さない）。
- 未回答・遅れは既存の `answered`・`skip_reason`・`latency_ms`。

## 4 日の終わりの問い（判断 1）

### 4.1 仮の定数（`analysis/daily_check.rs`）

| 名前 | 仮の値 | 事前登録 |
|---|---|---|
| `EVENING_START_MIN`・`EVENING_END_MIN` | 17:00・24:00（ローカル） | S1-F5 |
| `EVENING_GAP_MS`（打鍵の途切れ） | 10 分（離席候補 180 秒と区別・S1-F5） | S1-F5 |
| 補助の契機（一時停止） | 夕方の時間帯の中で、当日まだ尋ねていないとき | S1-F5 |
| `DAY_CUTOFF_MIN`（日付の切れ目） | 04:00（ローカル） | S1-F6・S1-D1 |
| 拾い直しの対象 | 直前の 1 日だけ（それより前は欠測） | S1-F6 |

### 4.2 契機と拾い直し

- 当日: 夕方の時間帯に、特徴量のキーの途切れが `EVENING_GAP_MS` に達した刻みで 1 回だけカードを出す。カードは答えるか閉じるまで残す。閉じたら当日はもう出さない。
- 補助: 夕方の時間帯の一時停止で、当日まだ尋ねていなければ出す。トレイの終了は終了を遅らせない方針で、契機にしない（終了の後は翌日の拾い直しで拾う）。トレイの終了を契機にするかは研究者に確かめる（§7 の 3）。
- 拾い直し: 日付の切れ目の後の最初の利用（起動・スリープからの復帰・打鍵の再開のうち最初のもの）で、直前の 1 日に答えが無ければ 1 回だけ「昨日の作業について」と尋ね、`late: true` を付ける。1 つの対象の日について、当日 1 回と拾い直し 1 回まで（ADR-048 D3）。回答は更新させない。
- 状態（対象の日・当日に尋ねたか・拾い直したか）は `daily_check_state.rs` が小さなファイルで持つ。中身は日付と真偽だけで、本文や回答の値は持たない。
- スリープからの復帰は `input/power_*.rs` の通知を使う（何を通知するかは実装のタスクで確かめる）。

### 4.3 記録 `daily_check`

`{target_day: "YYYY-MM-DD", kind: same_day|recovery, trigger: evening_gap|pause|next_day_first_use, shown_ts, answered, answer_ts, latency_ms, items: [{item_id, value}], skip_reason}`。`latency_ms` は表示から回答まで。回答の後の打鍵の量は `key` 行から `gse-replay --daily-check` が数える（行に持たない）。

### 4.4 項目（仮の文）

S-DQ の候補の表（`docs/literature/20261105-daily-end-of-day-items.md`）から、前期の動機づけを 1〜2 項目。手跡は前期に無いので、同期・共存の項目は入れない（後期の R10 で足す）。`item_id` は文の版を含め（例 `motivation_today_v0`）、文を差し替えたら版を上げる（S1-F7）。

## 5 影響範囲

- 素の O1: 挙動を変えない。プローブは今どおり出ない（起点を段 1 だけで立てる）。`label_row_allowed` の引数が増えるので呼び出し 4 か所を直す。`meta` に `o1_variant` が出ないことを検査で固定する。
- G1・EH3・通常のモード: 変えない。プローブの起動の節の止める条件は残す。
- R1 との衝突（impact-analyzer の報告）: `logger.rs` の `LogEntry` の末尾・`type_name`・整形・書き出しの match・全列挙のテスト、`schema_dto.rs` の末尾、`capabilities.rs` の `KNOWN_LINE_TYPES`、`redaction.rs` の `matches!`、`lib.rs` の `record_session_meta`。R1 が main に入ってから書けば行の衝突は起きない。`current.json` は `emit_schema` で作る。
- R3: 新しい 3 行種と `meta.o1_variant` を gse-dataset の schema に同期する。
- 被験者向けの文書: 段 1 の同意文書（R4）に、頻度の最大（定数と一致）・6 択・日の終わりの問いを書く。本人の試しでは同意文書の代わりに研究者が承認の印を置く。

## 6 テスト戦略

| # | 検査 | 種類 |
|---|---|---|
| T-1 | `poll_outcome` を足しても、同じ seed の無作為の発火の時刻の列が今と同じ | 単体（`probe_scheduler.rs`） |
| T-2 | 層化の候補をどう出しても、無作為の候補の時刻と件数が変わらない（判断 8） | 単体・性質の検査（seed を回す） |
| T-3 | 層化の引き金が、合成の記録の再生と 1 Hz の刻みで一致する | 単体 ＋ `gse-replay --s1-strata` の fixture |
| T-4 | 推定器の出力が層化の関数の入力に無い（型で固定） | コンパイル |
| T-5 | 素の O1 で `activity_label_allowed` が `None`・ラベルの行が落ちる・プローブが 0・`meta` に `o1_variant` が無い | 単体 |
| T-6 | 1 時間の最大の合計が同意文書の数と一致（定数を 1 か所から引く） | 単体 ＋ 配布物の門 |
| T-7 | 新しい行種の 3 点セット（`line_type`・`KNOWN_LINE_TYPES`・一時停止の遮断）と段 1 だけの宣言 | 単体（`capabilities.rs`・`recording.rs`） |
| T-8 | 区間の削除で `probe_suppressed`・`probe_holdout`・`daily_check` が消える | 単体（`redaction.rs`） |
| T-9 | 段 1 で Nudge と招待が出ない（`normal_invitation_allowed` が false・`INTERVENTION_ENABLED` が false） | 単体 |
| T-10 | 日の終わりの問い: 当日 1 回・拾い直し 1 回まで・日付の切れ目・直前の 1 日だけ・時刻帯のずれ（JST と UTC の両方） | 単体（`daily_check.rs`） |
| T-11 | `HOLDOUT_ENABLED = false` で `probe_holdout` が 0 行・候補が `holdout` で落ちない | 単体 |
| T-12 | Replay-as-Truth: 既存のゴールデンの byte-equal を保つ（`gse-replay --snapshot`） | 回帰 |
| T-13 | schema の parity（`emit_schema` と `current.json`・gse-dataset） | CI |
| T-14 | 画面: macOS と Windows の実機で、カード（3 問）と日の終わりの問いが見え、押せ、背後のクリックを奪わない | 手動（研究者の手を含む） |

## 7 実装の前に研究者に確かめること（この計画の中では決めない）

1. `/reimagine` の v2 との比べ（モードを O1 の変種にするか、独立のモードにするか、など）。
2. `probe_suppressed` の理由の値に `holdout`・`card_open` を、`skip_reason` に `superseded` を足してよいか（判断 9 の列の拡張）。
3. トレイの終了を日の終わりの問いの補助の契機にするか（終了を遅らせることになる）。
4. 日の終わりの問いの仮の文（S-DQ の候補の表から何を選ぶか）。

## 8 ロールバック計画

- 段 1 は `s1.mode` が無ければ立たないので、配布物から印を外せば素の O1 に戻る。
- コードは 1 つの枝で入れ、問題があれば revert する。schema は追加だけなので、古い記録は読める（新しい行種は gse-replay で無視できる既存の作法）。
