# carryover-R3 — round 4 からの引き継ぎ（R3: 投稿先の方法論と再現性の番人の立場）

作成: 2026-10-02（メイン）。あなた（R3 の立場）の round 4 の新しい指摘 8 件（下で 新 1〜新 5・nit a〜c と呼ぶ。あなたの round 4 の応答の §4 の順）と、round 4 であなたが「部分的に解消」と判定した前の指摘 1 件について、メインの裏取り・研究者の採否・対応・未解決を書く。あわせて、round 4 の後に変わった、あなたの指摘に直接は対応しない大きな変更（§3.4 の焦点の規則など）を「C. 共通」に書く。
⚠️ **再掲を求めない**。各指摘が今の版で**解消したか**を 1 件ずつ判定してから（解消 / 部分的に解消 / 未解消・理由 1 行・今の版の位置）、**今回の直しが作った新しい穴**を探してほしい。round 4 で「解消」と判定した指摘は引き継がない（変わっていない節は round 4 までの判定のまま）。
「採らなかった」部分は研究者の選択（またはメインの選択）で、理由を添えた。その理由が成り立たないと考えるなら、新しい指摘として根拠つきで書いてよい。

## 版の変化（round 4 の版 `159a2ec8` → 今の版 `ba89bcbd`）

- 節番号は変わっていない。round 4 の行番号は使えない（本文は 12,143 語から 14,665 語に増えた）。変わった節とコードの関数は context-A の「round 4 から変わった箇所」。
- 読んでよいファイルの一覧は round 4 と同じ（増減なし）。
- round 4 で「約束の文だけ」だった §3.1 の 2 つの点検と `pilot-macos.md` の Raw logs は、凍結の前に測定機で行い、**中身がある**。⚠️ パイロットの生ログはこの機械にも一覧にも無い（§3.1 の数は、文書の中の整合とコードが数えるものとの対応で見てほしい）。

## A. round 4 の新しい指摘

裏取りの判定は、メインがコード・計画・事前登録で確かめた結果。

### 新 1 [minor] §3.4 の閉じた規則が、道具の引数・限界の単位・道具が入力を拒んだ場合で 1 通りに決まっていない
- 裏取り: **真**（(i) 窓の引数を名指さない・(ii) 「in each block」なのに道具は run の合計しか出さない・(iii) exit 2 の扱いが無い・(iv) `pipeline.py` は manifest の `aborted` しか見ない）。
- 研究者の採否: 規則をブロックごとの区間で閉じ、命令行・exit 2・検査の対象を §3.4 に書き、`pipeline.py` も同じ規則を当てて拒む。
- 対応: (i) §3.4 に命令行を逐語で（`python3 kit/analysis/delivery.py --plan <run>/plan.jsonl --oracle <run>/oracle.jsonl --obs <run>/obs.jsonl --gt <run>/gt.jsonl --pre-ms 20 --tail-ms 300 --out <report>`）。`data.md` 手順 1 も同じ。(ii) §3.4 の「**Presses from outside.**」の段落（区間は oracle の `block_begin` で切り、区間ごとに「送った打鍵で説明されない参照の key-down の数」が手順の作る打鍵〔最初の区間は k・最後の区間は印だけ・ほかは印＋k〕を超えたら中止。合計の読みは無くなった）。`delivery.py` の `_segments` が区間ごとの数を 2 版（`all_presses` / `excluding_mode_keys`）で出し、`data.md` の表の列は `max_beyond_markers_before_last_block` と `beyond_markers_last_block`（手で by_segment から拾わない）。(iii) §3.4（「A run for which `delivery.py` refuses its input (exit status 2) also counts as aborted. No other reason and no explanation is admitted.」）。(iv) `pipeline.py` の `reference_abort_reasons` を `analyse` が使い、当たる run は exit 2。`e1_delivery.json` に `abort_rule`（`{focus_margin_ms, obs_send_delay_ms, pre_ms, reference_receives_mode_keys, runner_kana_presses_per_block, tail_ms, unplanned_focus_loss_with_unexplained_presses_aborts}`）を記録する。§5 の最後（「and it refuses a run that the rules of section 3.4 catch」）。
- ⚠️ 計画の SHA-256 の照合は**コードには足していない**（登録の 2 つの値は §2.4 の文にしか無く、`config.json` に足すと凍結のハッシュの対象と形式が変わる。メインの選択）。`data.md` の Run checks の表に「SHA-256 of the plan」の列を足し、手順 1 で §2.4 と照合する。

### 新 2 [minor] 中止の規則の閾値を、パイロットの参照ログに当てていない
- 裏取り: **真**（当時、パイロットで数えたのは観測の側の到達だけ）。
- 研究者の採否: 凍結の前に測定機でパイロットの参照のログに当て、上限の設定をその結果で決めて §3.1 に書く。
- 対応（§3.1 の 2 つ目の項目）: `pilot2-on`・`pilot2-off`・`verify-off`（矢印の印・3 打鍵）に §3.4 の引数で `delivery.py` を当てた。かなキー 15 回のどれも参照に key-down を残さず（最初の区間は 0 行・各ブロックの区間の「説明されない数」は印の 3 打鍵ちょうど）→ **k = 0**。S14 のモードキーも 2 つとも届かない（試行の中で送った打鍵の到達は 4,072 / 4,090・3,972 / 3,990・1,174 / 1,180、届かなかった 18・18・6 は S14 の試行の数 × 2 とちょうど一致）→ モードキーは送った打鍵に数えない（版 `excluding_mode_keys`）。この設定で 3 run とも、印を引いた余りの最大は 0（規則は中止にしない）。区間の最後の行から次のブロックまでの最小は 1,582 ms。「Only counts and times are reported; no key code is read or written.」
- 対応（コード）: `pipeline.py` の定数 `RUNNER_KANA_PRESSES_PER_BLOCK = 0`・`REFERENCE_RECEIVES_MODE_KEYS = False`。印は run の計画が述べる長さ（本番 4・パイロット 3）を使う。
- あなたの 3 つ目の問い（遅れた行が 300 ms の尾を超えて「外」に数えられることがあるか）について、§3.1 が報告する数は上のとおり（3 run とも印を引いた余りの最大は 0）。遅れの分布そのものは §3.1 に書いていない。

### 新 3 [minor] 問 3 の主の範囲で、一致の限界と ICC が k の混合になり、速さのあいだで比べられない
- 裏取り: **真**（メインが計画と予測から計算: k の平均は ON で slow 4.60・mid 6.49・fast 7.17、OFF で 4.56・6.43・7.21。slow で k ≤ 3 が 30 / 126・27 / 117、k = 8 は 4・0、k = 0 は無い。`l2.py` はテキストを等しい重みで並べる）。
- 研究者の採否: **開示する**（あなたの解消の条件の (c)）。
- 対応: §6.7（「Under `under_limit` a text keeps only its trials in the scope, and in this design their number k differs between speeds: … A value computed over fewer trials varies more, so the limits of agreement and the ICC of the primary scope hold for this design's distribution of k and are not compared between speeds. The bias is the mean of the per-text differences with every text weighted equally, whatever its k. The smaller k is, the more texts have a measure that cannot be computed on one side (for example no session, so no mean conversion time) and are left out of that measure (section 6.11).」）と §7 の打ち切りの項。k の数は `spec_predict.py --from-plan` の `plan_figures` で再現できる（§3.1 の最後の段落）。
- 採らなかった: (a) 主の一致を k = 8（または下限以上）のテキストに限る（推定の対象が変わり、slow で多くのテキストを失う）・(b) k の層ごとにも報告する（slow の k = 8 は 4 / 0 テキストしか無い）。

### 新 4 [minor] §6.6 の「仕様の行との一致は試行ごとの行の数で読む」に、統計も計算するコードも無い
- 裏取り: **真**。
- 研究者の採否: 文を、コードが既に出す数で読む形に直す（新しい統計を足さない。あなたの解消の条件の後半）。
- 対応: §6.6 の Cut-off（「Agreement with the specified rows is read from the detection counts of `pred_obs` under `over_limit` per stratum (the numbers of predicted and of observed rows, and the pairs, misses and false positives between them, section 6.5); no other statistic is computed for it.」）。

### 新 5 [minor] §3.3 の設計効果の段落
- 裏取り: 「usually near 1」に根拠が無いのは**真**。計算を再現するコードが無いのは**真**（round 3 の値は使い捨てのスクリプト）。最小の主の層で半幅が約 0.35 SD になるのは**真**。⚠️ 「主の範囲の層では上限 3.4 が成り立つか確かめていない」は、確かめた結果**成り立つ**（メインの計算で主の範囲の層の Σm²/Σm の最大は ON 3.05〔S14 mid〕・OFF 3.22〔S15 mid〕）。
- 対応: §3.3（「Over the trials of the primary scope (section 6.4) it is at most 3.05 (on, S14 middle) and 3.22 (off, S15 middle), within the same bound (`plan_figures`, section 3.1). D is therefore at most about 3.4 within a stratum, and near 1 only when rho is small. With D = 1 the half-width is about 0.23 x SD with 75 pairs … and about 0.35 x SD with 31, the smallest stratum of the primary scope other than those of S6 and S13; with D = 3.4 it is about 1.8 times as wide.」）。`spec_predict.py --from-plan` が `plan_figures`（層ごとの試行・ブロック・Σm²/Σm を、計画の試行と long でない試行について。速さごとのテキストあたりの long でない試行の数の分布）を出し、§3.3 と §6.7 の値を再現できる（§3.1 の最後の段落）。本番の 2 計画（SHA-256 一致）で §3.3 と §6.7 の値がすべて出力から再現されることを、メインが確かめた。
- 採らなかった: 設計効果の式の出典を足すこと（新しい書誌の確認が要る）。

### nit a: §6.3 の文が §3.4 の許容と食い違う
- 対応: §6.3（「Rows of the observation without a sent press are a result of the observer and stay in the analysis; whether the rows of the reference make a run count as aborted is decided by the rules of section 3.4 alone.」）。

### nit b: §3.1 の 2 つの約束の書き方
- 対応: 1 つ目を 2 文に分けた（基準は凍結の前に `pilot-macos.md` に書く／満たす run の生ログを預ける）。`pilot-macos.md` の Raw logs は「written before the freeze of the pre-registration」にそろえ、基準の中身を書いた。2 つ目（合わせ直し）は、対象の run（`pilot2-on`・`pilot2-off`・`verify-off`）・`--markers-in-obs`・パイロットの 3 打鍵の印・使い道（「This is a diagnostic of the code: if it reveals a defect, the defect is corrected before the freeze, and the fractions before and after the correction are reported.」）を書いた。結果は 15 / 15 ブロック・282 試行・割り当てのない打鍵 0（欠陥は無くコードは変えていない）。⚠️ これらのログには欠けも足しも無いので、再同期は実ログでは試されていない（§3.1 にそう書いた）。

### nit c: 中止の規則は「外からの打鍵」の十分条件でしかない（相殺される）
- 対応: §3.4 の後半（「The rule on presses counts the key-downs that remain beyond the presses that reached the reference, so a lost press and a press from outside cancel out: … Such a replacement is not detected (section 7).」）と §7 の新しい項「The stopping rule counts presses, not keys」。

## B. round 4 で「部分的に解消」と判定した前の指摘

### 1（問 3 の量に抜いた試行の数が混ざる）→ 上の新 3 で開示した。

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
- runner を変えて、かなキーを構造的に試行の窓の外へ出すこと（区間で数えれば窓の位置に依らない）。
