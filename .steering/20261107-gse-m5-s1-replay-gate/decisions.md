# 重要な設計判断

## 判断 0: 着手前の確かめ（引き継ぎ §2 の 1・2）

- 判断日時: 2026-11-07
- ディスク: 空き 6.7GiB。`feature/gse-m5-s1-core` が `origin/main` に入っていることを `git branch --merged` で確かめ、`/Users/johnd/GSE-prototype-m5-core/src-tauri/target`（5.1G）を消した。空き 12GiB。`GSE-prototype-m5-driver` には成果物が無かった。
- 2 本目で確かめ残した取り消しの経路（ロックの持ち方を変えた後の版・main 3a792fb9）を macOS の画面で確かめた。隔離した HOME・`GSE_O1_MODE=1 GSE_S1_MODE=1 GSE_DEBUG=1 VITE_GSE_DEBUG=1 npm run tauri dev`（cargo と rustup は本物の HOME を指す）。本番の GSE は動いていなかった（AX の取り違えの心配なし）。
  - 「問いに同意する」→ ローテートし、新しいファイルの先頭に `meta`・`probe_frame`。
  - 確かめ用の「段1 プローブ (random)」でカードを出し（overlay 379×417 に `直前の30秒について教えてください`）、開いたまま「問いへの同意を取り消す」→ overlay は 1×1 の画面外に戻り、`probe_assignment` は 3・ラベルの行は 2 のまま（取り消したカードの行なし）、`~/.gse/s1_probe_consent` が消えた。カードが下りたのは押下の約 5 秒後（画面の 5 秒の取り直しの範囲）。
  - 取り消しの後に確かめ用の口を 2 つ（プローブ・日の問い）押しても、カードは出ず、問いの行は 8 のまま。
  - 途中の 2 枚の `dismissed` は研究者が画面で閉じたもの（研究者に確かめた）。

## 判断 1: 範囲の切り方

- 判断日時: 2026-11-07
- 選択肢: A 1 タスク・2 PR（(a) 再生／(b)(c) 門・launcher・文書・schema）／B 1 タスク・1 PR／C (a) だけ
- 採用: A
- 理由: (a) は差分が大きく、/cross-review を小さく保てる。(b) は (a) を待たずに出せる。記録は 1 つにまとめる。
- 影響範囲: PR が 2 本になる。schema の変更（判断 3 の `debug`）は PR 1 に入り、gse-dataset の同期は PR 2 でまとめて行う（PR 1 の時点で parity が赤にならないかは design で確かめる）。

## 判断 2: 一時停止の境目の 2 秒

- 判断日時: 2026-11-07
- 背景: 駆動役は一時停止を壁時計で受けるが、調停器の時計は `S1_TICK_LAG_MS = 2000` だけ遅れている。tick は 1 秒ごとで、どの tick で止まったかは記録から正確には分からない。
- 選択肢: A 境目にかかる不一致を別に数える／B 再生でも `recording_pause` の時刻 − 2 秒で効かせて合わせる／C 両方
- 採用: A
- 理由: 記録から分からないものを分かったふりをしない。件数が見えるので、多ければ後で B を足せる。
- 見直しタイミング: 実の記録で境目の件数が多いとき。

## 判断 3: 確かめ用のカードの行の見分け方

- 判断日時: 2026-11-07
- 背景: `probe_assignment`・ラベル・`day_question` の行には `card_id` も印も無く（`lib.rs` の `s1_day_question_entry`）、再生で `card_id >= 1<<52` を除くことはできない。印が無いと、確かめのカードは「調停器が出していない余り」になり、本物の不具合と区別できない。
- 選択肢: A 確かめ用のカードの行だけに `debug: true`（偽のときは書かない）／B 印を付けず運用（隔離した HOME）で分ける／C 確かめ用のカードは行を書かない
- 採用: A
- 理由: 本物の行は 1 バイトも変わらず、本人の試しの記録に混ざっても後から分けられる。schema の変更は (c) の同期と一緒に済む。
- トレードオフ: schema にフィールドが 1 つ増える。

## 判断 4: 再生の設計（/reimagine）

- 判断日時: 2026-11-07
- 選択肢: v1 駆動役ごと回す／v2 調停器だけを回し開いているカードを記録から渡す／ハイブリッド
- 採用: ハイブリッド（v2 を土台に、v1 の 2 秒の遅れの陽性対照を足す）
- 理由: v2 は不一致の連鎖を防ぎ、v1 が見落としたスリープの復帰（記録に行が無い・`lib.rs:727`）を拾う。v2 の推測「起動とローテートを `session_start` で分けられる」は外れ（`session_start` は G1 のブロックだけ・`lib.rs:4631`）だったので `unverified.app_start` に直した。
- 作り方: v2 は v1 を読ませない Plan エージェント（Opus）に作らせ、メインが一次で確かめた。比べは `design-comparison.md`。

## 判断 5: gse-dataset の schema の同期を PR 1 に合わせる

- 判断日時: 2026-11-07
- 背景: main 3a792fb9 の `schema/current.json` と `~/gse-dataset`（main aba6d7a）を `scripts/check_schema_parity.py` で比べると、既に `day_question`・`eh3_day`・`invitation_condition`・`invitation_present`・`probe_frame`・`probe_suppressed` が gse-dataset に欠けていて赤（rc=1）。`/finish-task` は赤だと止まる。
- 選択肢: A PR 1 に合わせて同期／B 実装の前に今の main で同期し PR 1 でもう一度／C PR 2 のまま
- 採用: A
- 影響範囲: gse-dataset の PR を PR 1 と対にする（push は研究者に確かめてから）。PR 2 の (c) は文書だけになる。
- 訂正（2026-11-07・実装の後）: 背景の「6 行種が欠けている」は、origin より 3 コミット遅れたローカルの `~/gse-dataset` の main と比べた結果だった。origin/main（bd1d471）と比べると、EH3 の `eh3_day`・`invitation_present` は同期済みで、欠けていたのは `day_question`・`invitation_condition`・`probe_frame`・`probe_suppressed` の 4 行種（と今回の `debug`・`superseded`）。同期が要ることは変わらない。
- 実施: `~/gse-dataset` に origin/main から `chore/schema-s1-replay` を切り、`schema/current.json` を写した（3b6539e・push はまだ）。`check_schema_parity.py` は OK。gse-dataset の `validate_schema.py` で、確かめ用の印つきの記録（判断 0 と同じ手順の隔離した HOME・新しい版）が新しい schema で OK、origin/main の schema では段 1 の行種で FAIL（陽性対照）。

## 判断 6: 点検（V1・code-reviewer ∥ security-checker）への対応

- 判断日時: 2026-11-07
- 範囲: `origin/main..b7c2b53e -- src-tauri`。HIGH は規約どおり直し、MEDIUM 6 件は研究者に聞いて全部直した（推奨どおり）。安い LOW も直した。直したものは、元に戻すと対応する検査が赤になることを確かめた（5 つの変異）。

| 出所 | 重さ | 指摘 | 対応 |
|---|---|---|---|
| code-reviewer | HIGH | 再生にだけ出た日の問いの鍵が tick の壁時計で、位相ごとに違うので必ず `boundary_tick` になり、`day_question` の行の欠けが赤にならない | 位相をまたいで結ぶ名（`stab`・判定は鍵の時刻、日の問いは対象の日と契機）を別に持つ。検査 `deleting_a_day_question_is_missing`。直すと、取り消しの後に再生だけが出す日の問いが `tail` でなく `missing` に出たので、日の問いも `tail` の対象にした |
| security-checker | MEDIUM | 時刻の幅に上限が無く、壊れた時刻 1 行で再生が止まらない・桁あふれ | 行の時刻が `meta.session_start` から −60 秒〜+3 日の外なら拒む・入力の全体の幅は 40 日まで・足し算は `saturating_add`・調停器の無い間は次の枠まで飛ばす・開いているカードの区間は索引で引く（毎 tick に全部をなめない）。検査 `broken_times_and_too_long_inputs_are_refused` |
| code-reviewer | MEDIUM | 枠を作った tick で起点より前の押下が調停器に渡る・調停器の無い間も待ち行列が残る | 駆動役と同じく、入力を受けた後に枠を作って起点より前を捨て、調停器の無い tick では待ち行列を捨てる。検査 `presses_before_the_anchor_are_not_fed` |
| code-reviewer | MEDIUM | 記録が `warmup` の不一致がすべて `unverified.power_resume` | 行が 30 秒以上途切れた直後か推定した復帰の直後（ウォームアップの幅）に限る。検査 `a_warmup_mismatch_is_unverified_only_after_a_gap` |
| code-reviewer | MEDIUM | 判定の行が 1 行も無い枠は全部 `tail` | 判定の行がある枠だけ `tail`。検査 `a_frame_without_any_decision_row_is_missing` |
| code-reviewer | MEDIUM | 同じ鍵の行が 2 行あると 1 件に潰れる | 2 行目以降を別の項目にして `extra`。検査 `a_duplicated_row_is_extra` |
| code-reviewer | MEDIUM | 時差なしで no_ask が有効なら全部が `offset_unknown` | no_ask の判定が絡む項目（記録か再生が `no_ask`）だけにする。検査なし（no_ask は既定で無効・`probe_arbiter.rs:59`） |
| code-reviewer | LOW | 確かめ用のカードの区間が候補 + 3 秒より後から・確かめ用の層化のカードに再生だけが差し替えを出す | 確かめ用のカードは割り当ての行の位置から開く・差し替えを出さない |
| security-checker | LOW | UTF-8 でない行を置き換えて受理する・`skip_reason` を検証せず出力のキーにする | UTF-8 でない行は読めない行として数える・`skip_reason` は既知の 4 値だけ |
| code-reviewer | LOW | `cards` の使わない引数 | 外した |
| 見送り | LOW | 1 秒の中で止めて再開してまた止めたときの `on_pause` の呼び方の差・ファイル全体の大きさの上限・`--day-state` の大きさ・出力にファイル名が載る（研究者の手元の CLI・gse-dataset へは metrics だけを共有する運用） | design の既知の限界に書く |
