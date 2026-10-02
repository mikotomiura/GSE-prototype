# carryover-R2 — round 4 からの引き継ぎ（R2: 打鍵記録を使う書字研究の利用者・行動ログの公開の安全の立場）

作成: 2026-10-02（メイン）。あなた（R2 の立場）の round 4 の新しい指摘 8 件（major 1・minor 4・nit 3。下では応答の §4 の順に「新 major」「新 minor-k」などと呼ぶ）と、round 4 であなたが「部分的に解消／未解消」と判定した前の指摘について、メインの裏取り・研究者の採否・対応・未解決を書く。あわせて、round 4 の後に変わった、あなたの指摘に直接は対応しない大きな変更（§3.4 の焦点の規則など）を「C. 共通」に書く。
⚠️ **再掲を求めない**。各指摘が今の版で**解消したか**を 1 件ずつ判定してから（解消 / 部分的に解消 / 未解消・理由 1 行・今の版の位置）、**今回の直しが作った新しい穴**を探してほしい。round 4 で「解消」と判定した指摘は引き継がない（変わっていない節は round 4 までの判定のまま）。
「採らなかった」部分は研究者の選択（またはメインの選択）で、理由を添えた。その理由が成り立たないと考えるなら、新しい指摘として根拠つきで書いてよい。

## 版の変化（round 4 の版 `159a2ec8` → 今の版 `ba89bcbd`）

- 節番号は変わっていない。round 4 の行番号は使えない（本文は 12,143 語から 14,665 語に増えた。+21%）。変わった節とコードの関数は context-A の「round 4 から変わった箇所」。
- 読んでよいファイルの一覧は round 4 と同じ（増減なし）。
- round 4 で「約束の文だけ」だった §3.1 の 2 つの点検と `pilot-macos.md` の Raw logs は、凍結の前に測定機で行い、**中身がある**。⚠️ パイロットの生ログはこの機械にも一覧にも無い（§3.1 の数は、文書の中の整合とコードが数えるものとの対応で見てほしい）。

## A. round 4 の新しい指摘

裏取りの判定は、メインがコード・計画・事前登録で確かめた結果。

### 新 major: §3.4 の閾値「1 ブロックに 5（印 4・かな 1）」が確かめていない前提に立ち、検査の数は取りこぼしと外からの打鍵が相殺する
- 裏取り: **真**（仕組み）。かなキーは oracle に行が無く、参照が受けたかを確かめた記録が当時の一覧に無かった。`delivery.py` は run の合計しか出さず、`excess_rows` は試行の中で差し引く。預ける基準の下書き（`pilot-macos.md`）は観測と参照のすべての行が送った打鍵と対応することを求め、§3.4 と前提がぶつかりえた。
- 研究者の採否: 規則をブロックごとの区間で数え（合計の読みを無くす）、上限（かなキーを数えるか）を凍結の前に測定機でパイロットの参照のログに当てて決める。相殺は限界として書く。預ける基準を本計測と揃える。
- 対応（文）: §3.4 の「**Presses from outside.**」の段落（区間は oracle の `block_begin` で切り、区間ごとに「送った打鍵で説明されない参照の key-down の数」が手順の作る打鍵〔最初の区間は k・最後の区間は印だけ・ほかは印＋k〕を超えたら中止）。相殺は §3.4 の後半（「The rule on presses counts the key-downs that remain beyond the presses that reached the reference, so a lost press and a press from outside cancel out: a marker press that does not reach the reference against a press from outside anywhere in the same segment, and a press of a trial that does not reach it against a press from outside in the interval of the same trial. Such a replacement is not detected (section 7).」）と §7 の新しい項「The stopping rule counts presses, not keys」。
- 対応（パイロット・§3.1 の 2 つ目の項目）: `pilot2-on`・`pilot2-off`・`verify-off` に §3.4 の引数で `delivery.py` を当てた。かなキー 15 回のどれも参照に key-down を残さず（最初の区間は 0 行・各ブロックの区間の「説明されない数」は印の 3 打鍵ちょうど）→ **k = 0**。S14 のモードキーも 2 つとも届かない（試行の中で送った打鍵の到達は 4,072 / 4,090・3,972 / 3,990・1,174 / 1,180、届かなかった 18・18・6 は S14 の試行の数 × 2 とちょうど一致）→ モードキーは送った打鍵に数えない（版 `excluding_mode_keys`。数えると S14 の各試行に外からの打鍵の入る余地ができる）。3 run とも、印を引いた余りの最大は 0。
- 対応（預ける基準）: `pilot-macos.md` の Raw logs を本計測の §3.4 と揃えた（喪失の外では観測の余分な行は預けることを止めない）。
- 対応（コード）: `delivery.py` の `_segments`、`pipeline.py` の `reference_abort_segments`（定数 `RUNNER_KANA_PRESSES_PER_BLOCK = 0`・`REFERENCE_RECEIVES_MODE_KEYS = False`）。

### 新 minor-k: 問 3 のテキストに残る範囲の試行の数が速さで系統的に違うのに、主の限界と ICC はテキストを等しく並べる
- 裏取り: **真**（メインが計画と予測から計算: テキストあたりの範囲の試行の数 k の平均は ON で slow 4.60・mid 6.49・fast 7.17、OFF で 4.56・6.43・7.21。slow で k ≤ 3 が 30 / 126・27 / 117、k = 8 は 4・0、k = 0 は無い。`l2.py` はテキストを等しい重みで並べる）。⚠️ あなたの「slow の一致の限界はテキストの大きさだけで約 1.25 倍」は、メインは計算していない（確かめられない）。
- 研究者の採否: **開示する**（あなたの解消の条件の (c) と「偏りがテキストの平均か試行の平均か」）。
- 対応: §6.7（「Under `under_limit` a text keeps only its trials in the scope, and in this design their number k differs between speeds: … A value computed over fewer trials varies more, so the limits of agreement and the ICC of the primary scope hold for this design's distribution of k and are not compared between speeds. The bias is the mean of the per-text differences with every text weighted equally, whatever its k. The smaller k is, the more texts have a measure that cannot be computed on one side … and are left out of that measure (section 6.11).」）と §7 の打ち切りの項。k の数は `spec_predict.py --from-plan` の `plan_figures` で再現できる（§3.1 の最後の段落）。
- 採らなかった: (a) 主の一致を k ≥ m のテキストに限る（推定の対象が変わり、slow で多くのテキストを失う）・(b) 限界と ICC を k の階級ごとにも報告する（slow の k = 8 は 4 / 0 テキストしか無い）。

### 新 minor-S6: 再重み付けの版で S6 がほぼ空になり、コードは空の層を null にせず落とす
- 裏取り: **真**、しかもあなたの「ほぼ空」より強い: 持ち越しの無い版（carried out でも received carry でもない・範囲の中）の S6 は、メインの計算で**両セル・全速さで 0 試行**。S13 は主の範囲に 1 つも残らない。
- 研究者の採否: 直す（あなたの解消の条件のとおり）。
- 対応（文）: §6.7（「In the measurement plans the view without carried-over sessions holds no trial of S6, in either cell at any speed, and S13 has no trial in the primary scope (section 3.3): these scenarios cannot be reweighted, their strata are reported as null with the reason (section 6.11), and the view contains no disagreement that a session carried from one trial into another causes.」）。
- 対応（コード）: `l2.py` の `per_trial` は、計画にある層で試行の無いものも行として出し、すべての行に `status`（`ok` / `no_trial`）と層ごとの `trials_not_used` を持たせる。

### 新 minor-§6.4: 読者向けの文が、打ち切りが 4 つの量を動かす向きも、key 行で分かることも書かない
- 裏取り: **部分的に真**。key 行から打ち切りの候補（どのセッション行も覆わない英字の連なり）は分かるが、macOS では入力モードが key 行に残らないので確定できない。「別の情報源でしか分からない」は言い過ぎで、「key 行だけでは確定できない」が正確。§7 の入れ漏れは真。
- 対応: §6.4（「A session that is cut off has no row; the key rows of a log show candidates for one (a run of letter keys that no session row covers), but on macOS they do not record the input mode, so a candidate cannot be confirmed from the log alone. Leaving out these longest conversions lowers the mean conversion time and the fraction of time spent converting. The conversions per trial can move either way, because a letter or digit typed after the cut-off opens a session of its own (section 1.1). The abandonment rate can move either way too, because a session that is cut off may have been committed or abandoned.」）と §7 の打ち切りの項の最後（「In a researcher's own log the sessions that are cut off cannot be confirmed from the key rows alone (section 6.4).」）。

### 新 minor-§3.1: 合わせ直しの約束が、どの run を・どの印で回し・結果を何に使うかを書いていない
- 対応: §3.1 の 1 つ目の項目に、対象の run（`pilot2-on`・`pilot2-off`・`verify-off`。最初のパイロットの F13・F14 は観測に行が無いので外す）・`--markers-in-obs` とパイロットの 3 打鍵の印・使い道（「This is a diagnostic of the code: if it reveals a defect, the defect is corrected before the freeze, and the fractions before and after the correction are reported.」）を書いた。
- 結果: 15 / 15 ブロック・282 試行を採点し、割り当てのない打鍵は 0。欠陥は無くコードは変えていない。⚠️ これらのログには欠けも足しも無いので、**再同期は実ログでは試されていない**（§3.1 に「it does not exercise the resynchronisation, which only the selftest's cases do」）。
- 関連（コード）: 合わせ直しの錨を印の区分の連なりの**右の端**にした（ブロック末の閉じる Return が欠けて末尾の矢印が次の印とつながっても、失うのはそのブロックだけ。ブロックのあいだに足された打鍵は何も失わない）。§6.8・`kit\e2\README.md`。保証は「selftest の場合で確かめた・一般には証明していない」と書いた。

### nit（3 件）
- §6.7 の「none of the four layers」→「the trials of the layer none (section 6.4)」。
- §6.8 の「Presses outside every block are counted」→「Presses that no scored block covers (including those of unscored blocks) are counted.」。
- §3.3 の「usually near 1」→「near 1 only when rho is small」。

## B. round 4 で「部分的に解消／未解消」と判定した前の指摘

### A（問 3 の主が long の割合に依存）・新 3 → 上の新 minor-k で開示した（偏りの側は round 4 で解消と判定済み）。

### minor 3（打ち切りの規則を読者のデータに当てる）→ 上の新 minor-§6.4 で対応。

### minor 6（合わせ直しを実ログで未試行）・minor-7（パイロットの生ログを預ける基準）
- 対応: 上の新 minor-§3.1 と、`pilot-macos.md` の Raw logs（runner の run が候補・runner が中止した run も本計測と同じ条件・§3.4 の規則がパイロットで決めた設定と run 自身の印〔3 打鍵〕で当たらない・`pipeline.py --check-deposit` が通る・喪失の外では観測の余分な行は止めない・封印したセッション行は凍結と本計測の後に預けるためにだけ開ける・凍結の前に 6 run と最初のパイロットの前の短い run に規則を当て、どれにも当たらなかった）。

### nit 3（冗長さ）
- 対応: §7 の「The text-recoverability study judges one phrase at a time」の項を §6.8 の参照 1 行に縮めた。
- ⚠️ 本文は 14,665 語（round 4 の版から +21%）。増えた分の大半は §3.1（パイロットの結果）と §3.4（区間の規則・焦点の規則・預ける前の点検）。

### major-3（セッション行の公開の形）・major-4・minor-5（中間の粒度）
- round 4 から変わらない（採らなかった・round 1 から）。

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
