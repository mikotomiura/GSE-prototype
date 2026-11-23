# 設計（PR 1 の再生・v2 を土台にしたハイブリッド）

作り方: v1 を書いたメインの文脈から離すため、v1 を読ませない Plan エージェント（Opus）に requirement.md・decisions 判断 2・3・コードだけから作らせ、メインが主張を一次で確かめて書き直した（確かめた結果は各所に「確かめ」と書く）。

## 実装アプローチ

調停器 `Arbiter` だけを再生で回す。開いているカード（`TickInput.open_card`）は再生が自分の発火から作らず、**記録から作って渡す**。カードを閉じるのは本人の操作で、その情報は記録にしかない。記録から渡すと、カード 1 枚の食い違いが後ろへ波及しない。ただし調停器の中の状態（直前の発火・上限の数）が一度ずれるとずれは続くので、枠ごとに最初に割れた時刻 `first_divergence_ms` を出す。純粋な処理はライブラリの新しいモジュールに置き、bin は行を読んで JSON を出すだけにする（`--invitation` と同じ分け方・`invitation_trigger.rs:138-226`・`replay.rs:1842-1951`）。

### 記録から戻すもの

- 枠: `probe_frame` 1 行ごとに `Arbiter::new`（seed・`anchor_ms`・設定 22 項目・`logger.rs:1783-1830`）。`arbiter_version` が違えば exit 1。日の問いの状態は `into_day_question` で次の枠へ引き継ぐ（`probe_arbiter.rs:945`・駆動役の `s1_driver.rs:232-256` と同じ）。
- 入力: `key` の押下の `t` と `focus_transition` の `t`（駆動役が受けるのと同じ集合・確かめ: `lib.rs:5313-5321`・`5883-5889`）。
- 一時停止: `recording_pause` の `paused` が `paused`・`resumed` になる。止めた行の時刻で `day_question_mut().on_pause`（`probe_arbiter.rs:828`・`s1_driver.rs:548-562`）。
- 開いているカード: プローブは発火の tick の次から、閉じる行（`realtime_label.ts`・`superseded` のラベル・一時停止で下ろしたなら `recording_pause`・終了なら最後の行）まで。日の問いは `day_question` の `shown_ts` から `t` まで。プローブがあれば日の問いより優先（`s1_driver.rs:272-285`）。確かめ用のカード（`debug: true`）も開いていた区間としては入れる（層化の `card_open` は日の問いのカードでも立つ・`probe_arbiter.rs:519`）。
- 外から来る契機: `trigger: "quit"` の行は `shown_ts` で `on_quit` を入れ、調停器が出すと言うかを確かめる（`probe_arbiter.rs:835`）。答えた・閉じた行では `on_closed`。

### 記録に無いが判定に要るもの

| 情報 | 扱い |
|---|---|
| tick の位相（1 秒の sleep でずれる・`lib.rs:2337`） | 位相を 0・250・500・750 ms の 4 通りで回し、結果が割れた項目を `boundary_tick` に分ける。候補の判定の away・gap・cap は候補の時刻だけで決まり（`probe_arbiter.rs:404-428`）位相に依らない。位相が効くのは再開の直後のウォームアップ・カードを閉じた直後・同じ tick の無作為と層化の重なり |
| 枠が動き出した時刻 | `probe_frame` の行の前後の行の時刻で挟む。3 秒以内にかかる不一致は `boundary_activation` |
| 時差（行に書かない・計画の判断 4） | `--utc-offset-secs` を `--probes` と `--day-questions` でも受ける（今は `--invitation` 専用・`replay.rs:1675`）。`--probes` で渡さなければ、日の問いの照合と no_ask を `unverified.offset_unknown` にする（no_ask は既定で無効・確かめ: `probe_arbiter.rs:59`・`probe_frame` の `no_ask_enabled` で分かる）。`--day-questions` では必須 |
| 前日までの日の状態（`s1_day_state.json`・NDJSON に入らない） | 空から始め、入力の範囲で積み上げる。入力の最初の日より前を対象にした拾い直しは `unverified.prior_day_state`。`--day-state <json>` を任意で受ける |
| スリープからの復帰（行が無い・確かめ: `lib.rs:727` は Atomic を増やすだけ） | 抑制の行の `t − candidate_ts` が 30 秒以上なら、その tick を復帰とみなす（`GAP_AS_POWER_RESUME_MS`・`s1_driver.rs:37`・`318-321`）。抑制の行の無いスリープは見えないので、記録が `warmup` で抑制し再生が判定した候補は `unverified.power_resume` に分ける |
| 起動か日付のローテートか（`app_started`） | 区別できない（確かめ: `session_start` の行は G1 のブロックの開始だけ・`lib.rs:4631`）。起動に依る日の問いの拾い直しの不一致は `unverified.app_start` |
| 同意の取り消し（行が無い・`s1_driver.rs:623`） | 同意し直すと枠が作り直される（`probe_frame` が出る）ので、枠の終わりから次の枠まで、または入力の終わりまでに「再生は行を出すのに記録に無い」ものを `unverified.tail` にする（それ以上の推定はしない） |

## 照合の鍵・分類・JSON

- 鍵: 無作為は `(枠, candidate_ts)`（候補の列は seed と起点だけで決まる・`probe_arbiter.rs:362-395`）。層化は `(枠, 層, 引き金の押下の時刻)`。差し替えは差し替えた層化のカードの `probe_id`。日の問いは `(target_day, trigger, delayed)` で、`shown_ts` は再生の now + 2000 との差が ±1000 ms 以内なら同じ。
- 1 件ごとの分類（重ならない・この順に当てる）:
  1. `debug_check`: 記録の `debug: true` の行（判断 3）。
  2. 境目: `boundary_pause`（鍵の時刻が [止めた行の時刻 − 2000, 止めた行の時刻]・判断 2）・`boundary_tick`・`boundary_activation`。
  3. `unverified`: `offset_unknown`・`prior_day_state`・`power_resume`・`app_start`・`tail`。
  4. 照合した残り: `match`・`differ`（両方あるが発火と抑制、または理由が違う）・`missing`（再生にあり記録に無い）・`extra`（記録にあり再生に無い）。
- 判断 2 の窓の補足: tick は最大 1 秒遅れるので、割れうる範囲は約 3 秒。判断 2 は変えず、窓の外の 2〜3 秒にかかる件数を `near_pause_outside_window` として別に出す。
- 出力: `{mode:"probes", replay_version, arbiter_version, utc_offset_secs|null, tick_phases_ms, inputs:[{file, session_start, frames:[{anchor_ms, activation_ms:{lo,hi}, end_ms, first_divergence_ms|null}]}], counts, by_kind:{random, low_operation_end, resumption, superseded, day_question}, items:[{kind, key_ms, class, recorded, replayed, phase_stable}], cards, lag_check}`。
  - `cards`（回答率・S1-A4・A7）: `total・answered・skipped_by_person{reason}・superseded・dropped_by_pause・dropped_at_quit・carried_across_rotation・open_at_input_end・orphan・debug・response_rate_excl_superseded`。
  - `lag_check`: `{s1_tick_lag_ms: 2000, lag_sensitive_items, lag_sensitive_matched}`。鍵の時刻の 2 秒前までに押下がある項目の一致の数（押下が届き切っていたかの必要条件）。
- 一時停止で下ろしたカード: `probe_assignment` あり・ラベルなし・次の段 1 の行が `recording_pause` の `paused: true`。ローテートをまたぐカードは入力全体を `probe_id` で索引して結ぶ。
- `--day-questions`: 答えた行（`debug` を除く）ごとに `{t, target_day, presses_until_cutoff, cutoff_ms, input_covers_cutoff, paused_ms_in_span}`。範囲は `t` から次の現地 4:00（`eh3::local_day` の切れ目）まで。

## 変更対象

### 新規作成するファイル
- `src-tauri/src/s1_replay.rs`（純粋）: 行の型・`probe_frame` から `ArbiterConfig` を戻す処理・照合・`day_questions`。

### 修正するファイル
- `src-tauri/src/bin/replay.rs`: `Args` に `probes`・`day_questions`（`1537`）・相互排他の列（`1775-1795`）・位置引数で複数のファイル（`1803`・`meta.session_start` の順・重なれば拒む）・`--utc-offset-secs` の許可（`1675`）・`--day-state`・1 行 1 MiB の上限（`1839` にならう）・振り分け（`2237` と同じ形・不正なら exit 1 で stdout を空に）。
- `src-tauri/src/s1_driver.rs`（判断 3）: `ProbeCard`・`Effect::Assigned`・`DayRowData` に `debug`。判定は変えない。
- `src-tauri/src/lib.rs`: `run_s1_effects` の Effect → LogEntry の写し（`2125-2173`）を純関数に切り出す（往復の検査と共用・挙動は変えない）。`s1_day_question_entry`（`2046`）とラベルを書くコマンドに `debug`。
- `src-tauri/src/logger.rs`: 書式関数（`710`・`729`・`782`・`1848`）に真のときだけ `,"debug":true`。
- `schema_dto.rs`・`schema/current.json`: 任意の `debug`。

## 既存パターンとの整合性

- ライブラリが純粋な再生を持ち bin は薄く（`invitation_trigger::replay_recorded`）・不正な入力は exit 1（fail-closed）。
- `--snapshot` は `ProbeAssignment` に `deny_unknown_fields` が無く（`replay.rs:1218-1225`）新しい行種は読み飛ばす（`1176-1183`）ので byte-equal を保てる見込み。
- 打鍵の本文は読まない（`key` 行は `t` と押下かだけ）。`analysis/` に IO を置かない。

## テスト戦略

- 往復の検査（主）: 合成の入力で純粋な `S1Driver` を回し、切り出した写しで LogEntry にし、本物の logger の書式で一時ファイルへ書き、`s1_replay` に掛けて `missing`・`extra`・`differ` が 0・`match` が 1 件以上。
- 2 秒の遅れの陽性対照（v1 から）: 往復の検査で押下が駆動役に届く時刻を 0〜1900 ms 遅らせても全件一致し、2100 ms 以上遅らせると割れうる（割れる合成の入力を 1 つ持つ）。
- 壊すと赤: `probe_assignment` を 1 行消すと `missing` が 1／抑制の行を 1 行足すと `extra` が 1／seed を書き換えると `match` がほぼ 0／止めた行の 1 秒前は `boundary_pause`・4 秒前なら `missing` のまま／`debug` の行が `extra` にならない。
- 個別: ローテートをまたぐ回答・一時停止で下ろしたカード・`superseded` を分母から外す・取り消しの後の `tail`・`--probes` と `--invitation` の排他・位相を 4 通りに振ったときの境目・`--day-questions` の 4:00（JST と UTC）。
- 直列化: 本物の行のバイト列が変わらない（既存の byte 固定）・既存のゴールデンの byte-equal・`emit_schema`。

## 既知の限界とリスク

- 記録に残らない取りこぼし（`S1_INPUT_DROPPED`・`lib.rs:688` は warn だけ／ログのチャネルが詰まって `key` 行だけ落ちる）は不一致として表に出るだけ。
- 区間の削除は NDJSON に印を残さない（確かめ: `redaction.rs`・台帳は別ファイル）。削除の範囲の再生は崩れる（`probe_frame` が消えれば枠ごと再現できない）。
- 一時停止の間に閉じた日の問いは行が無く（`lib.rs:2130`）、その後の開いているカードの状態が分からない。
- 分類は不一致が後ろへ波及した分まで数える。主に見るのは `first_divergence_ms`。
- PR 1 の時点の schema parity は確かめていない。
- 範囲外の気づき: `--calibration` は `probe_assignment` を層も `debug` も見ずに無作為のプローブとして数える（`replay.rs:3891`・未確かめ）。

## 実装中に変わった点と既知の限界（2026-11-07）

- 誤りは `Result<_, String>`（この repo は anyhow を依存に持たない・`redaction.rs:33-39`）。JSON として読めない行（落ちた走行の書きかけ・UTF-8 でない行）は数えて飛ばし（`skipped_lines`）、再生に使う行種の欄が壊れていれば行番号つきで止める。
- 開いているプローブの区間の始まりは、再生が発火させたならその tick、させていなければ「候補 + 3 秒」と割り当ての行の位置の遅い方（行の位置は発火の tick より前になりうる）。確かめ用のカードは行の位置から。
- 日の問いは位相をまたいで「対象の日・契機・拾い直しか」で結ぶ（判断 6 の HIGH）。
- `lib.rs` の写しのうち枠・抑制・割り当て・日の問いを `s1_effect_row` に切り出し、往復の検査と共用した。差し替えのラベルの 2 行は 6 択の門の中で組む（O1 の門の検査が組む場所を 3 関数に限っている）ので、検査の側で同じ組み立て関数を呼ぶ。
- 往復の検査は本物の `SessionLogger` で一時ファイルに書く（`meta` の時刻だけ合成の時刻に直す）。
- 時刻の検査: 行の時刻が `meta.session_start` から −60 秒〜+3 日の外なら拒む・全体は 40 日まで。
- 照合の基準: 一致の数が最も多い位相を基準にし、他の位相でだけ一致した項目は境目（判断 8）。照合の時刻の検査は、起きた時刻をファイルの始まりで、参照の時刻を絶対の範囲（2020〜2100 年）と全体の 40 日で縛る。
- 既知の限界: 溜まった候補の見分け（t − 候補 > 3 秒）は tick が 1 秒以上遅れる（App Nap など）と普通の行でも超える／取り消しの後に押下が無いと記録の後ろが落ちたのと見分けられない（`tail_no_activity`）／区間の削除をまたぐ記録は一致しない／一時停止の間に閉じた日の問いと同意の取り消しは行が無い（取り消しで下ろしたカードは `cards.open_at_input_end`）／1 秒の中で止めて再開してまた止めたときの `on_pause` の呼び方は駆動役と違う／ファイル全体と `--day-state` の大きさに上限は無い（研究者の手元の CLI）／出力に入力のファイル名が載る（gse-dataset へは共有しない）／no_ask を有効にした場合の時差なしの照合は検査していない（既定で無効）／`S1_TICK_LAG_MS` で押下が届き切るかは、実の記録の `lag_check` で必要条件しか分からない。

## 設計判断の履歴

- 実行回数: 1 回目
- 採用: ハイブリッド（v2 を土台に、v1 の 2 秒の遅れの陽性対照を足す）
- 根拠: 研究者が推奨どおり選んだ（2026-11-07）。v2 は開いているカードを記録から渡して不一致の連鎖を防ぎ、v1 が見落としたスリープの復帰（記録に行が無い）を拾う。v1 は `design-v1.md`、比べは `design-comparison.md`。

---

# PR 2: 段 1 の配布の門・launcher・組み立て・文書（2026-11-07）

/reimagine はかけない（requirement の運用メモ・O1 の門の型にならう）。研究者の決め（decisions 判断 9・10）: 本人用の印は `s1.mode` の中身に `audience=self` の 1 行で置く／組み立て `make-common-app-zip.sh` に `--mode s1`（本人用だけ）を足す。

## アプローチ

1. **組み立て `--mode s1`**（`experiments/20260801-controlled-friction-task/make-common-app-zip.sh`）
   - 持ち物は O1 と同じ（README・初回セットアップ・鍵・`g1-submit.json`）で、launcher だけ段 1 用の `launch-s1-windows.bat` を `GSE_起動.bat` の名で入れる。README は O1 のものを使う（本人用。参加者向けの README は R9 で同意文書と一緒に作る）。
   - 印: `o1.mode`（0 バイト）と `s1.mode`（中身 `audience=self` の 1 行）。`g1.mode`・`eh3.mode` は入れない。`s1.mode` の書き出しは `[ "$MODE" = s1 ] &&` で始まる 1 行に限る（O1 の門がこの形で O1 の配布物への混入と見分ける）。
   - `--config` の明示を O1 と同じく求める。タグに `o1.rs` と `s1.rs` があること、実体（`gse-next` の macOS と Windows）に `s1.mode`・`GSE_S1_MODE` の文字列があることを確かめる。
   - 展開後の検査（macOS）と Windows の zip の検査に、段 1 の印 2 つ・中身・`g1.mode`/`eh3.mode` の不在を足す。selftest にモード `s1` の持ち物・launcher のバイト形式・`GSE_DISABLE_PROBES` を付けないことを足す。
2. **launcher `launch-s1-windows.bat`**: O1 の launcher を元に、`set GSE_DISABLE_PROBES=1` を外し（計画の判断 6）、`s1.mode` の不足を知らせ、`eh3.mode` が同居していたら中断する（アプリは両方を落として素の O1 で動くので、黙らせない・計画の判断 7）。BOM・chcp を日本語より前・CRLF（memory participant-launcher-encoding）。
3. **門 `scripts/check-s1-release-readiness.sh`**
   - 引数: `--audience self|participants`（必須）・`--dist <フォルダか zip>`（1 つ以上・必須）・`--consent <段 1 の同意文書>`（participants のとき）・`--selftest`。知らない引数・欠けは exit 2。終了コードは O1 と同じ（0/1/2）。
   - [1] 組み立てと launcher（repo）: `s1.mode` を書き出す行が macOS と Windows の両方にあり、すべて `[ "$MODE" = s1 ] &&` の形／`eh3.mode` を書き出す行が無い／launcher が在り、BOM・CRLF・chcp が最初の非 ASCII の行より前・コメントでない行に `GSE_DISABLE_PROBES` が無い。
   - [2] リリースタグ: `s1.rs` と `s1_driver.rs` を含む最新のタグがあり、そのタグ以降に `src-tauri/src`・`src-tauri/Cargo.toml`・`src` が動いていない（O1 の門と同じ判定・比較先は origin/main か main）。
   - [3] 同意: self は「本人用（計画の判断 5）: 同意文書の承認は求めない」で緑。participants は `--consent` があり、行頭完全一致の `<!-- s1-esm-consent: approved -->` と、未記入の欄（`（実施前に記入）`）が無いこと。今は段 1 の同意文書（R4）が無いので participants は赤が正しい。
   - [4] 配布物（`--dist` ごと・zip は展開せず python の zipfile で読む）: `o1.mode` と `s1.mode` があり、`g1.mode` と `eh3.mode` が無い／`s1.mode` の中身が audience に一致（self は `audience=self`、participants は `audience=participants`。participants の門に `audience=self` を渡すと「本人用の配布物」で赤）／`.bat` のコメントでない行に `GSE_DISABLE_PROBES` が無い・Windows の配布物（`gse-next.exe` がある）に `.bat` がある／`gse-next` の実体に `s1.mode` と `GSE_S1_MODE` のバイト列がある。
   - selftest: 一時ディレクトリに門・組み立て・launcher を写し、`git init -b main` で合成の `s1.rs`・`s1_driver.rs` をコミットしてタグを打ち、合成の配布物（フォルダと zip）を作る。基準が緑、✅ を 1 つずつ壊すと赤、未達を満たすと緑。対照の文字列（`GSE_DISABLE_PROBES`・承認の印・`audience=self` など門の本文に出る語）は実行時に連結して作る。
4. **O1 の門の手直し**（`check-o1-release-readiness.sh`）: 「O1 の配布スクリプトが `s1.mode` を書き出さない」を、「`make-distribution.sh` には 1 行も無く、`make-common-app-zip.sh` の書き出しはすべて `[ "$MODE" = s1 ] &&` の形」に変える。selftest に陽性（段 1 の分岐の中の書き出しは緑）と陰性（`make-distribution.sh` に書き出し → 赤・分岐の外の書き出し → 赤のまま）を足す。
5. **文書**: `docs/architecture.md`（段 1 の行種と配布の門）・`docs/architecture/gse-design-map.md`（§1 のラベルの行・§4）・`docs/o1-distribution-tag.md` は触らない（段 1 の配布タグの文書は R9）。

## 変更対象ファイル

| ファイル | 変更 |
|---|---|
| `scripts/check-s1-release-readiness.sh` | 新規 |
| `experiments/20260801-controlled-friction-task/launch-s1-windows.bat` | 新規（BOM・CRLF） |
| `experiments/20260801-controlled-friction-task/make-common-app-zip.sh` | `--mode s1`・検査・selftest |
| `scripts/check-o1-release-readiness.sh` | `s1.mode` の書き出しの判定と selftest |
| `docs/architecture.md`・`docs/architecture/gse-design-map.md` | 段 1 の行種と門 |

`src/`・`src-tauri/` は変えない。

## テスト戦略

- `bash scripts/check-s1-release-readiness.sh --selftest`（陽性と陰性の対照）。
- `bash scripts/check-o1-release-readiness.sh --selftest` が今までの件数＋足した件数で緑。本体の実行は、変更の前後で s1.mode の行の判定だけが変わり、他の行は同じ（前後の出力の差分で確かめる）。
- `bash experiments/20260801-controlled-friction-task/make-common-app-zip.sh --selftest`。
- `scripts/check-shell-portability.sh`（bash 3.2）。
- 本体の `check-s1-release-readiness.sh --audience self --dist <無い>` が赤・exit 1 で、理由が出る。実の組み立て（dmg と gh が要る）は今は回さない（段 1 を含むタグがまだ無い）。

## 既知の限界

- 門は組み立ての本文を静的に読む。実体の検査は組み立ての展開後の検査と、門の [4] が担う。
- アプリは `s1.mode` の中身を読まないので、本人用の配布物を門を通さずに他の人へ渡すことは防げない（防ぐのは門を通す運用）。
- 参加者向けの組み立て（`audience=participants`）は作らない（R9）。

## PR 2 の実装中に変わった点（2026-11-07）

- 門が本物の launcher を赤にした（O1 の launcher から写した日本語のコメントが `chcp 65001` より前）。段 1 の launcher は chcp を 2 行目へ上げた。O1 の launcher も同じ並びだが配布中なので触らない。
- 点検（判断 11）で、配布物を読む python の例外で緑に倒れる穴を塞いだ（`DONE=1` を求める）。印の名前は大文字小文字・末尾の点と空白をならして比べ、全階層の印・`.bat`/`.cmd`・名前の異常・1 GiB を超えるメンバーを見る。
- 書き出しの検出は `${M}` と `tee`/`cp`/`touch`/`mv` も拾い、許す行は「`[ "$MODE" = s1 ] && printf '%s\n' 'audience=self' > "$M/s1.mode"`」と `$W` の 2 行の完全一致に限る（段 1 と O1 の両方の門）。組み立ての selftest 7c は探す行を実行時に組み立てる（門が 7c の行を書き出しと数えたため）。
- タグの新しさは `src-tauri` の全体・`src`・`package.json`・`package-lock.json` を見る。`git log` の失敗は赤。
- 同意の印はコードのフェンスの外にちょうど 1 回。版との結び付けは R4 で決める。
