# carryover-R1 — round 3 からの引き継ぎ（R1: 打鍵の時刻を測る道具の検証の立場）

作成: 2026-10-02（メイン）。あなた（R1 の立場）の round 3 の新しい指摘 7 件（下で N-1〜N-7 と呼ぶ。あなたの round 3 の応答の §4 の順）と、round 3 であなたが「部分的に解消」と判定した前の指摘 6 件について、メインの裏取り・研究者の採否・対応・未解決を書く。
⚠️ **再掲を求めない**。各指摘が今の版で**解消したか**を 1 件ずつ判定してから（解消 / 部分的に解消 / 未解消・理由 1 行・今の版の位置）、**今回の直しが作った新しい穴**を探してほしい。round 3 で「解消」と判定した指摘は引き継がない（変わっていない節は round 3 の判定のまま）。
「採らなかった」部分は研究者の選択（またはメインの選択）で、理由を添えた。その理由が成り立たないと考えるなら、新しい指摘として根拠つきで書いてよい。

## 版の変化（round 3 の版 `abc5d7f9` → 今の版 `159a2ec8`）

- 節番号は変わっていない。round 3 の行番号は使えない（本文は 11,217 語から 12,143 語に増えた）。変わった節とコードの関数は context-A の「round 3 から変わった箇所」。
- 読んでよいファイルの一覧は round 3 と同じ（増減なし）。

## A. round 3 の新しい指摘

裏取りの判定は、メインがコード・計画・事前登録で確かめた結果。7 件すべて「真」。

### N-1 [major] 完了した run を、観測自身の余分な key 行で中止にでき、その判断に裁量が残る
- 裏取り: 真（§3.4 と `data.md` 旧手順 4 の逐語、`delivery.py` の selftest「observation: a duplicate row is counted as excess」）。
- 研究者の採否: 中止は**参照のログが実行器の外からの打鍵を示すときだけ**、閉じた規則で決め、「説明」の裁量を無くす。観測の余分な行は観測器の結果として解析し、§6.3 で報告する。検査は `delivery.py` 単体（key 行だけ）で、各 run の直後・§3.2 の次の項目の前に行い、判断と時刻を解析の前に記録する。
- 対応: §3.4（「A completed run counts as aborted when its plan has another SHA-256 than the plan of section 2.4, or when the reference log shows a key press from outside the executor: in the delivery report of `kit/analysis/delivery.py`, run on the run directory alone (it reads the key rows of the logs, not the session rows), the reference's `excess_rows` over all presses is greater than zero, or its `rows_outside_trials` exceeds the five presses made outside the trials in each block (four marker presses and one kana press). No other reason and no explanation is admitted. … Rows of the observation without a sent press are a result of the observer under test (section 6.3) and never make a run count as aborted. Aborted runs are reported with their reason and their delivery figures」）・§3.2 の最後の文・§6.3 の最後から 2 文目・`data.md`（「Run checks」の表を新設し、旧手順 4 の検査を「run の直後」の手順 1 に移した）。あなたの解消の条件の (2)(3)(5) と、(1) の「観測の余分な行は中止の理由にしない」を満たす形。
- メインの実装上の選択: 閉じた規則は `delivery.py` の**今ある**出力（参照の `excess_rows` と `rows_outside_trials`）で書いた。`delivery.py` は記述の道具のままで、判定の欄は足していない。外からの入力で中止にした run は預けない（参照のログは受けた key-down のキーコードを持つので、人の打鍵が入りうる）。
- 採らなかった: (1) の「送った打鍵から決めた許容幅」を数で決めること（観測の余分な行は、許容幅の内外を問わず中止の理由にしない、で包んだ）。(4)（説明を探すときに読んでよいもの）は、説明を認めないので要らなくなった。

### N-2 [minor] 合わせ直しが、試行の中の「矢印 4 つちょうど」で以後のブロックをすべて失う
- 裏取り: 真（メインが `align_blocks` を合成の列で動かした: 8 ブロックのうちブロック 1 の S7 の矢印の行を 1 つ重複させると、結果は `[0, None, None, None, None, None, None, None]`＝以後が全部採点されない）。
- 研究者の採否: 直す（凍結の前に必ず）。
- 対応（コード）: `closed_set.py` の `align_blocks` の再開を変えた。ブロックが今の位置で合わなければ、そのブロックの印か次のブロックの印が「ちょうどその長さ」で立つ位置を順に見て、そのブロックが丸ごと合えば置き、次のブロックが丸ごと合えばそのブロックだけを採点せずにそこへ進み、どちらも合わない位置（試行の中の矢印 4 つなど）は飛ばす。どこにも無ければ、そのブロックだけを採点せず、位置は動かさない（次のブロックが同じ所から探す）。selftest に「S7 の矢印に重複が 1 つ」の対照を足した（失うのはそのブロックだけ）。`open_set.py` も同じ `align_plan` を使う。
- 対応（文）: §6.8 の第 2 段落（「A block is placed where its block-start marker (four arrow presses) and all its trials match the observed presses. … a run of four arrow presses inside a trial (for example a duplicated row in a trial that sends three) is not taken for a marker unless the next block matches there, so a difference loses one block only (the block that holds it, or the next block when an added arrow press joins that block's marker).」）・§6.2 の該当の項・`kit\e2\README.md` の Usage。
- ⚠️ 残る場合（メインが §6.8 に書いた）: ブロックの直後に足された矢印が次のブロックの印とつながって 5 つになると、失うのは次のブロック（1 つだけ）。
- 関連: §3.1 に「凍結の前に、問 4 の割り当てだけをパイロットの観測の key 行に流し（攻撃はしない）、採点したブロックの割合をここに書く」を足した。⚠️ **約束の文だけで、中身はまだ無い**（パイロットのログは測定機にあり、この機械に無い。round 4 の後に行う）。

### N-3 [minor] 焦点の喪失は focus_out の行がある試行だけを数え、喪失が続いた試行と S15 で戻らなかった場合を拾わない
- 裏取り: 真（`delivery.py` は `focus_out` だけを読み、`focus_in` を読まなかった。`_focus_loss` はセル × 比較 × 範囲の合計だけ）。
- 研究者の採否: 直す。
- 対応（コード）: `delivery.py` に `_loss_intervals` を足した。喪失の区間は `focus_out` から次の `focus_in` まで（無ければログの終わりまで）で、続く `focus_out` は 1 つの区間にまとめる。区間と重なる試行をすべて数える。S15 の試行は、重なる喪失の区間がすべてその試行の中で始まって終わるときだけ数えない（計画した切り替え）。どの試行とも重ならない区間（試行の間の待ちだけのもの）は `n_loss_intervals_outside_trials` に数える。出力の名前を `reference_focus_out` から `reference_focus_loss`（`trials_with_focus_loss`）に変え、S15 の扱いは `pipeline.py` から `delivery.py` に移した。`pipeline.py` の `_focus_loss` は行と偽陽性を合計と速さごと（`by_speed`）に出す。
- 対応（文）: §6.2 の焦点の喪失の項（「A loss lasts from a focus-out of the reference to its next focus-in (to the end of the log when none follows), so it can cover several trials, because the runner confirms the focus only before each block; an S15 trial counts when its switch does not return inside the trial. The trials that overlap a loss are counted per stratum in the delivery report, and the observation rows assigned to them, and how many of these are false positives, are reported with the detection results, in total and per speed」）。
- 採らなかった: 行と偽陽性を層（シナリオ × 速さ）ごとに出すこと（速さごとまで。試行の数は配送の報告に層ごとにある）。

### N-4 [minor] 層ごとの設計効果の上限が、ブロックごとの層の試行数のばらつきを入れていない
- 裏取り: 真（メインが 2 つの計画〔SHA-256 は登録の値と一致〕から計算: 1 つの層の Σm²/Σm は ON 2.36〜3.13・OFF 2.47〜3.43、層の 75 試行が入るブロックは ON 33〜39・OFF 30〜37、区間の幅の倍率は最大 1.77 倍・1.85 倍）。
- 対応: §3.3 の「Precision of continuous measures and the design effect」に式（D = 1 + (Σm_j²/Σm_j − 1) × rho）と、計画から計算した値（33〜39 / 30〜37 ブロック・2.4〜3.1 / 2.5〜3.4・D は最大約 3.4・区間で最大約 1.8 倍）を 1 か所に置き、§6.1 は §3.3 を参照する形にした。
- 採らなかった: 式の出典を足すこと（新しい書誌の確認が要る。メインの選択）。

### N-5 [nit] 速さごとの「1.4〜1.8 点」は独立を仮定したときの値
- 対応: §3.3（「which locate a recall near 0.95 to within 1.4 to 1.8 points if the trials are treated as independent; a speed level is made of whole blocks, so its design effect can reach 25 (below)」）。recall の分母がセッションであることは「(about one session each)」と書いた。

### N-6 [nit] §6.6 の「specified: the same rows」と §6.9 の断片の対の外れが互いを参照しない
- 対応: §6.6 の Cut-off の最後（「Agreement with the specified rows is read from the numbers of rows per trial; a pair of a short row can fail for timing alone (section 6.9).」）。

### N-7 [nit] `carried_out` が「後の試行で終わる」以外でも立つ
- 対応: 文を実装に合わせた。§4.5（「**carried out**: a session that the trial started does not end in the trial (it ends in a later trial, is cut off by a press outside the trials, such as a marker press, or is still open at the end of the log)」）。コードは変えていない。

## B. round 3 で「部分的に解消」と判定した前の指摘

### N2 の条件 3（要旨の規則）
- 対応: §6.1 の最後（「An estimate in the primary scope is given together with the fraction of trials that the scope sets aside and the estimate under `all_trials` (section 6.4).」）。

### N8 の `log_truncated`（どちらのログか）
- 対応: §6.2（「`log_truncated`: a session of the ground truth (assembled from the reference log) still open when that log ends.」）。

### m1（設計効果の量）→ 上の N-4 で対応。

### m5（焦点を失った試行の観測の行）→ 上の N-3 で対応。

### m11（パイロットの生ログを預ける基準）
- 研究者の採否（round 3 の後）: 預ける基準と「封印したセッション行は預けるときだけ開け、解析しない」を、凍結の前に測定機で `pilot-macos.md` の Raw logs に書く。
- 対応: §3.1 に「which are written before the freeze」を足した（「The raw logs of its runs that meet the criteria set out there, which are written before the freeze, are deposited with the measurement data.」）。
- ⚠️ **未解決（既知）**: 基準そのものは、まだ `pilot-macos.md` の Raw logs に無い（"will be written here" のまま）。round 4 の後に測定機で書く。この版で判定するのは、約束の文の書き方だけでよい。

### n3（解析コードの同一性）
- round 3 から変わらない（研究者の選択: コミットは `notes.md` に手で書く形・§9 の 40 桁の識別子）。
