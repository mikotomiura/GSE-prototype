# carryover-R1 — round 4 からの引き継ぎ（R1: 打鍵の時刻を測る道具の検証の立場）

作成: 2026-10-02（メイン）。あなた（R1 の立場）の round 4 の新しい指摘 8 件（下で 新-1〜新-8 と呼ぶ。あなたの round 4 の応答の §4 の順）と、round 4 であなたが「部分的に解消」と判定した前の指摘 2 件について、メインの裏取り・研究者の採否・対応・未解決を書く。あわせて、round 4 の後に変わった、あなたの指摘に直接は対応しない大きな変更（§3.4 の焦点の規則など）を「C. 共通」に書く。
⚠️ **再掲を求めない**。各指摘が今の版で**解消したか**を 1 件ずつ判定してから（解消 / 部分的に解消 / 未解消・理由 1 行・今の版の位置）、**今回の直しが作った新しい穴**を探してほしい。round 4 で「解消」と判定した指摘は引き継がない（変わっていない節は round 4 までの判定のまま）。
「採らなかった」部分は研究者の選択（またはメインの選択）で、理由を添えた。その理由が成り立たないと考えるなら、新しい指摘として根拠つきで書いてよい。

## 版の変化（round 4 の版 `159a2ec8` → 今の版 `ba89bcbd`）

- 節番号は変わっていない。round 4 の行番号は使えない（本文は 12,143 語から 14,665 語に増えた）。変わった節とコードの関数は context-A の「round 4 から変わった箇所」。
- 読んでよいファイルの一覧は round 4 と同じ（増減なし）。
- round 4 で「約束の文だけ」だった §3.1 の 2 つの点検と `pilot-macos.md` の Raw logs は、凍結の前に測定機で行い、**中身がある**。⚠️ パイロットの生ログはこの機械にも一覧にも無い（§3.1 の数は、文書の中の整合とコードが数えるものとの対応で見てほしい）。

## A. round 4 の新しい指摘

裏取りの判定は、メインがコード・計画・事前登録で確かめた結果。

### 新-1 [major] 閉じた中止の規則が、実行器自身のかなキーで発火しうる（規則の特異度をパイロットで確かめていない）
- 裏取り: **真**（仕組み）。`run_cell.py` は前のブロックの最後の `trial_end` の直後に次のブロックの `focus_cmd` へ進み、`emit.py` の `run_block` は待ちを置かない。窓は `trial_end` + 300 ms で `block_end` では切らない。参照は `keyDown(with:)` に来たすべてを `key_down` に残す。当時この機械で確かめられなかったのは「かなキーが参照の `keyDown(with:)` に届くか」と「`focus_cmd` の所要時間」。
- 研究者の採否: 規則をブロックごとの区間で閉じ、かなキーの落ちる窓の位置に依らない形にする。上限（かなキーを数えるか）は凍結の前に測定機でパイロットの参照のログに当てて決める（あなたの解消の条件 (a) の方向）。命令行を §3.4 に書く（(c)）。
- 対応（文）: §3.4 の「**Presses from outside.**」の段落（「The report divides the time of a run at the block starts that the oracle records into segments: the time before the first block, and each block from its start to the start of the next block (the last block to the end of the logs). For each segment it counts the key-downs of the reference that the sent presses do not explain … The run counts as aborted when the count of any segment exceeds the presses that the procedure makes in it: k for the segment before the first block, the marker presses of the block plus k for every other segment except the last, and the marker presses alone for the segment of the last block」）。命令行は §3.4 の字下げのコマンド（`--pre-ms 20 --tail-ms 300`）。
- 対応（パイロット・§3.1 の 2 つ目の項目）: `pilot2-on`・`pilot2-off`・`verify-off` に §3.4 の引数で `delivery.py` を当てた。かなキー 15 回のどれも参照に key-down を残さず（最初の区間は 0 行・各ブロックの区間の「説明されない数」は印の 3 打鍵ちょうど）→ **k = 0**。S14 のモードキーも 2 つとも届かない（試行の中で送った打鍵の到達は 4,072 / 4,090・3,972 / 3,990・1,174 / 1,180、届かなかった 18・18・6 は S14 の試行の数 × 2 とちょうど一致）→ モードキーは送った打鍵に数えない（版 `excluding_mode_keys`）。3 run とも、印を引いた余りの最大は 0（規則に当たらない）。区間の最後の行から次のブロックまでの最小は 1,582 ms。メインの記録では、同じ点検を当てた 6 run・27 回のかなキーでも同じだった。
- 対応（コード）: `delivery.py` の `_segments`（区間ごとの数・2 版）、`pipeline.py` の定数 `RUNNER_KANA_PRESSES_PER_BLOCK = 0`・`REFERENCE_RECEIVES_MODE_KEYS = False` と `reference_abort_segments`。区間は `block_begin` の壁時計で切る半開区間（`block_begin` ちょうどの行は新しいブロックの区間）。各試行の到達は min(送った数, その試行に割り当たった行のうち区間の中にあるもの)。
- §3.4 の帰結の文: 「A kana press that does leave a key-down in a run of the measurement makes the run count as aborted wherever it falls; it cannot let a press from outside pass.」（k = 0 なので、かなキーが残れば落ちた区間に依らず中止になる）。
- 採らなかった: (b) runner を変えて `focus_cmd` の前後を oracle に書き、窓をそこで切る（oracle の形式・検証器・予測器まで触る。区間で数えれば窓の位置に依らない）。

### 新-2 [minor] 閉じた規則は、凍結する解析のコードでは強制されない（手で埋める表だけ）
- 裏取り: **真**（`pipeline.py` は manifest の `aborted` だけを見た。`check_run` にも無かった）。
- 研究者の採否: `pipeline.py` も同じ規則を配送の報告から当て、当たる run を拒む。
- 対応: `pipeline.py` の `reference_abort_reasons`（理由の文字列だけを返し、ログの値は出さない）を `analyse` が使い、当たる run は `InputError`（exit 2）。`e1_delivery.json` に `abort_rule` を記録する。§5 の最後（「and it refuses a run that the rules of section 3.4 catch」）・§3.4（「`kit/analysis/pipeline.py` applies the same rules to the delivery report it computes and refuses to analyse a run that they catch.」）。「in each block」の読みは、区間ごとの判定にしたので合計の読みは無くなった。
- ⚠️ 計画の SHA-256 の照合は**コードには足していない**（登録の 2 つの値は §2.4 の文にしか無く、`config.json` に足すと凍結のハッシュの対象と形式が変わる。メインの選択）。`data.md` の Run checks の表に「SHA-256 of the plan」の列を足し、手順 1 で §2.4 と照合する。

### 新-3 [minor] §6.3 の最後から 2 文目が §3.4 より広い
- 裏取り: **真**。
- 対応: §6.3（「Rows of the observation without a sent press are a result of the observer and stay in the analysis; whether the rows of the reference make a run count as aborted is decided by the rules of section 3.4 alone.」）。

### 新-4 [minor] 「1 つの違いで失うのは 1 ブロック」が、矢印で終わる試行の後の欠けで破れる
- 裏取り: **真**（メインが `align_blocks` を論理で追った: 1 つの欠けで 2 ブロックを失う）。
- 研究者の採否: 直す（あなたの解消の条件の 1 つ目: 錨を右に揃える）。
- 対応（コード）: `closed_set.py` の `_is_anchor` を「印の区分の連なりの右の端」（直後が印の最後の区分でない）に、`_next_anchor`・`align_blocks` をそれに合わせた。selftest に「ブロック末の閉じる Return の欠け（矢印 1〜3 の後）で失うのはそのブロックだけ」と「印の直前に足された矢印でもブロックを失わない」の対照。左端の条件を前提にしていた既存の対照 3 つは新しい期待に直した。ブロックの最初の試行が矢印で始まる手順は両方の手順書に無い（実装の作業で確かめた）。
- 対応（文）: §6.8 の第 2 段落（「A marker is looked for at the right end of a run of arrow presses, so arrow presses just before it (for example those that end the last trial of a block whose closing Return is missing) do not hide it; … A difference therefore loses only the block that holds it, and a press added between two blocks loses none; this is checked by the selftest of the code on the cases it constructs, not proved in general.」）・`kit\e2\README.md` の Usage と selftest の項。
- 実ログでの確認（§3.1 の 1 つ目の項目）: 矢印の印を使ったパイロットの 3 run の観測の key 行に、`--markers-in-obs` とパイロットの 3 打鍵の印で割り当てだけを流した（攻撃はしない）。15 / 15 ブロック・282 試行を採点し、割り当てのない打鍵は 0。欠陥は無くコードは変えていない。⚠️ これらのログには欠けも足しも無いので、**再同期は実ログでは試されていない**（§3.1 にそう書いた）。

### 新-5 [nit] §6.7 の「none of the four layers」
- 対応: §6.7 の最後（「As a diagnostic, the differences are also reported over the trials of the layer none (section 6.4).」）。

### 新-6 [nit] §3.1 の 2 つの約束の書き方
- 対応: 1 つ目を 2 文に分けた（「The criteria that a run of the pilot has to meet for its raw logs to be deposited are written there before the freeze. The raw logs of the runs that meet them are deposited with the measurement data.」）。`pilot-macos.md` の Raw logs は「written before the freeze of the pre-registration」にそろえ、基準の中身を書いた。2 つ目は対象の run（`pilot2-on`・`pilot2-off`・`verify-off`）・`--markers-in-obs`・パイロットの 3 打鍵の印・使い道（「This is a diagnostic of the code: if it reveals a defect, the defect is corrected before the freeze, and the fractions before and after the correction are reported.」）と結果を書いた（上の新-4）。

### 新-7 [nit] 「D は … usually near 1」に根拠が無い。範囲の層に当てはまらない
- 裏取り: 「usually near 1」に根拠が無いのは**真**。⚠️ 「主の範囲の層では 3.4 を超えうる」は**偽**: メインが計画と予測から計算すると、主の範囲の層の Σm²/Σm の最大は ON 3.05（S14 mid）・OFF 3.22（S15 mid）で、計画の層の上限の内。
- 対応: §3.3（「Over the trials of the primary scope (section 6.4) it is at most 3.05 (on, S14 middle) and 3.22 (off, S15 middle), within the same bound (`plan_figures`, section 3.1). D is therefore at most about 3.4 within a stratum, and near 1 only when rho is small.」）。`spec_predict.py --from-plan` が層ごとの Σm²/Σm を `plan_figures` として出し、§3.3 の値を再現できる（§3.1 の最後の段落）。

### 新-8 [nit] §3.2 の「each run」の検査に問 5 の `idle` が入る
- 対応: §3.2（「The check of section 3.4 is made right after each run of the two cells and of the `working` condition (the `idle` condition sends no key and has no plan)」）と §3.4（「The rules apply to the runs of the two cells and of the `working` condition of question 5; the `idle` condition sends no key and has no plan.」）。

## B. round 4 で「部分的に解消」と判定した前の指摘

### m11（パイロットの生ログを預ける基準）
- 対応: `pilot-macos.md` の Raw logs に基準を書いた（runner の run が候補・runner が中止した run も本計測と同じ条件・§3.4 の規則がパイロットで決めた設定と run 自身の印〔3 打鍵〕で当たらない・`pipeline.py --check-deposit` が通る・喪失の外では観測の余分な行は止めない・封印したセッション行は凍結と本計測の後に預けるためにだけ開ける・凍結の前に 6 run と最初のパイロットの前の短い run に規則を当て、どれにも当たらなかった）。

### n3（解析コードの同一性）
- round 4 から変わらない（研究者の選択: コミットは `notes.md` に手で書く形・§9 の 40 桁の識別子）。

## C. 共通: round 4 の後に変わった、上の指摘に直接は対応しないもの

### C1. 預ける前の点検を runner が中止した run にも当てる（round 4 の直しの後に行ったコードの点検の指摘・研究者の採否）
- 点検の指摘（裏取りは真）: runner が中止した run（Ctrl+C・前面の確認の失敗など、人の介入と相関しうる）は、§3.4 の規則が解析の中にしか無いため、預ける前に規則が当たらなかった。
- 研究者の採否と対応: `pipeline.py --pack` と `--check-deposit` が、完了・中止を問わずすべての run に §3.4 の規則を当て、当たる run と点検できない run（`delivery.py` が拒む・参照のログの無い観測のログ）を梱包しない。§3.4（「The same check is made on a run that the runner aborted: such a run is never analysed, and it is deposited only if the check passes or if it left neither a reference log nor an observation log.」）・`data.md` 手順 1 と梱包の手順。中止に数えた run は理由を問わず預けない（計画の SHA-256 の違い・`delivery.py` の exit 2 を含む。メインの選択）。

### C2. 焦点の喪失を中止の理由に足し、その規則を凍結の前に 2 度改めた
- 点検の指摘（裏取りは真）: 観測器は機械のすべての打鍵の区分と時刻を記録し、預ける。人が参照以外のアプリに打つと、参照の点検には掛からない。§2.1 は「no person's typing is part of the data」。
- **最初の規則**（研究者の選択）: 参照が S15 の計画した切り替え（S15 の試行の窓の中で始まって戻る喪失）以外で焦点を失った run は中止。
- **1 度目の改訂**（研究者の選択）: 測定機でパイロットに当てると、`pilot2-off` に S15 以外の喪失が 1 回あった（31 ms・S1 の試行の考える時間の中・最後に送った打鍵から 2.7 秒後・前後 3 秒に観測の key 行も参照の key-down も 0）。他の 5 run では 0 回（6 run で約 87 分）。この頻度だと約 12 時間のセルで平均約 8 回になり、喪失ごとに中止にする規則ではほとんどの run が中止になりうる（観測は 1 回なので頻度の幅は大きい）→ 「喪失の区間（前後に余裕 500 ms）に観測の key 行が 1 つでもあれば中止」に改めた。採らなかった: 短い喪失を閾値で許す（値の根拠が弱い）・最初の規則のまま・規則を外して §7 に開示するだけ。
- **2 度目の改訂**（研究者の選択）: 1 度目の規則は、実行器が送った打鍵の行も数える。実行器は喪失の間も打鍵を送り、観測は機械のすべての打鍵を記録するので、打っている最中に喪失が起きると人がいなくても中止になる。本番の 2 計画を予測器の oracle の時刻で数えると、run の時間の **ON 78.1%・OFF 77.0%** が送った打鍵（試行の押下・印）から 500 ms 以内に当たる（31 ms の喪失として）→ 「計画外の喪失の区間（前後 500 ms・重なる区間はまとめる）ごとに、観測の key 行の数が、実行器が送って観測が記録する打鍵（試行の押下〔擬似キーとモードキーを除く〕と印の打鍵・区間の 100 ms 前から区間の終わりまでに送ったもの）の数を超えたら中止」に改めた。78% は §3.1 に開示した（最初の版を改めた理由として）。採らなかった: 1 度目の規則のまま・測定機で喪失の率を測り直してから決める。
- 今の文: §3.4 の「**Loss of focus.**」の段落・§3.1 の 2 つ目の項目の後半・§6.2 の最初の Other contingency（解析する run にも打っている最中の喪失がありうる・喪失中に送った打鍵は参照に届かず、その試行は計画と正解の食い違いとして現れ、除外しない）・§7 の新しい項「The stopping rule counts presses, not keys」（喪失の区間の中で観測が取りこぼした行と、区間の終わりの直前 100 ms に送られて行が区間の外に落ちる打鍵は、人の打鍵を 1 つ隠す／観測器の重複行は人がいなくても中止にする）・§2.1。
- コード: `delivery.py` の定数 `FOCUS_MARGIN_MS = 500`・`OBS_SEND_DELAY_MS = 100` と `_focus_losses`（規則が使うのは `n_unplanned_loss_spans_with_unexplained_presses`。1 度目の改訂の数 `n_loss_intervals_unplanned_with_presses`・`n_presses_in_unplanned_losses` は記述として残した）。`pipeline.py` の `reference_abort_reasons` は前者 > 0 で中止。
- メインの選択（研究者が覆せる）: 余裕 500 ms（2 つのログの時計の差・観測の行の収集の遅れ・焦点を移すキーを覆う）・送出の遅れ 100 ms（区間の直前に送られて行が区間に落ちる打鍵を差し引くため）。⚠️ **100 ms はパイロットの実測で決めていない**（観測の遅れの実測は測定機の配送の報告にあり、この機械に無い）。パイロットの 7 run は新しい規則でも当たらない（唯一の計画外の喪失の前後 3 秒に観測の key 行が 0）。

### C3. 採らなかったもの（このほか）
- 定数（`pipeline.py` の k と版、`delivery.py` の 500 と 100）と事前登録の文の一致を機械で検査すること（文と定数は同じコミットで決め、目で照合した）。
- 設計効果の式の出典を足すこと（新しい書誌の確認が要る）。
