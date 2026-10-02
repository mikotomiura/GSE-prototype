# carryover-audit — round 4 からの引き継ぎ（意図の監査役）

作成: 2026-10-02（メイン）。あなた（監査役）の round 4 の指摘 14 件（1-A〜1-D・2-A・2-B・3-A〜3-H）と、round 4 であなたが「部分的に解消／未解消」と判定した前の指摘 3 件（1-1・1-2・1-a）について、メインの裏取り・研究者の採否・対応・未解決を書く。あわせて、round 4 の後に変わった、あなたの指摘に直接は対応しない大きな変更（§3.4 の焦点の規則など）を「C. 共通」に書く。研究者の採否とメインの実装上の選択は、context-B の判断 116〜124 に記録してある。
⚠️ **再掲を求めない**。各指摘が今の版で**解消したか**を 1 件ずつ判定してから（解消 / 部分的に解消 / 未解消・理由 1 行・今の版の位置）、**今回の直しが作った食い違い**を探してほしい。round 4 で「解消」と判定した指摘は引き継がない（変わっていない節は round 4 までの判定のまま）。
「採らなかった」部分は研究者の選択（またはメインの選択）で、理由を添えた。その理由が成り立たないと考えるなら、新しい指摘として根拠つきで書いてよい。

## 版の変化（round 4 の版 `159a2ec8` → 今の版 `ba89bcbd`）

- 節番号は変わっていない。round 4 の行番号は使えない（本文は 12,143 語から 14,665 語に増えた）。変わった節とコードの関数は context-A の「round 4 から変わった箇所」。
- 読んでよいファイルの一覧は round 4 と同じ（増減なし）。
- round 4 で「約束の文だけ」だった §3.1 の 2 つの点検と `pilot-macos.md` の Raw logs は、凍結の前に測定機で行い、**中身がある**。⚠️ パイロットの生ログはこの機械にも一覧にも無い。
- ⚠️ round 4 の context-A の §6.7 の要約に「4 つの層のどれでもない試行の版は診断」とあったのは誤り（あなたの 3-B の指摘のとおり）。round 5 の context-A では直した。

## A. round 4 の指摘

裏取りの判定は、メインがコード・計画・事前登録で確かめた結果。

### 1-A（minor）判断 115 の 2「外からの入力で中止にした run は預けない」が事前登録に無い
- 裏取り: **真**。
- 対応: §3.4（「A completed run that counts as aborted for any of these reasons is not deposited, because its reference log records the key code of every key-down it received and its observation log records every key press on the machine, so either may hold a person's key presses.」）。「預けない」は、外からの入力の場合だけでなく、完了した run を中止に数えた場合すべて（計画の SHA-256 の違い・`delivery.py` の exit 2・焦点の規則）に広げた（判断 118 の 3・どれも解析しない run で、参照のログは key code を持つ）。中止の報告の場所は `data.md` の Run checks の表（§3.4 が名指す）。`pipeline.py` は規則に当たる run を拒む（`n_aborted` には入らず、解析が止まる）。

### 1-B（nit）§1.2 の問 4 に範囲が無い
- 対応: §1.2 の問 4 の終わりに「(Section 6.8 states what is not evaluated.)」。

### 1-C（minor）新しい中止の閾値が実際の参照のログで確かめられていない
- 研究者の採否: 規則をブロックごとの区間で数え、上限を凍結の前に測定機でパイロットの参照のログに当てて決める（判断 116・117 の Z3 (3)）。
- 対応: §3.1 の 2 つ目の項目。`pilot2-on`・`pilot2-off`・`verify-off` に §3.4 の引数で `delivery.py` を当てた。かなキー 15 回のどれも参照に key-down を残さず → **k = 0**。S14 のモードキーも 2 つとも届かない → モードキーは送った打鍵に数えない（版 `excluding_mode_keys`）。3 run とも、印を引いた余りの最大は 0。§3.4 の「Two settings of the rule were fixed before the freeze from the logs of the pilot (section 3.1): k = 0 … and the input-mode keys of S14 do not count among the presses sent」。

### 1-D（要確認・nit）context-B の「中間の粒度は評価しない」がどの範囲を指すか
- 裏取り: **偽陽性**。context-B の「中間の粒度」は ms と 1 秒のビンのあいだを指し（判断 111 の 8）、§7 の今の文と同じ。round 5 の context-B はそう書いた。

### 2-A（nit）§3.4 は判断 112 の「だけ」に計画の SHA-256 を足すが、`data.md` の表に欄が無い
- 対応: `data.md` の Run checks の表に「SHA-256 of the plan」の列を足し、手順 1 に「check the plan's SHA-256 against section 2.4 of the pre-registration」を足した。⚠️ 照合はコードには足していない（登録の 2 つの値は §2.4 の文にしか無く、`config.json` に足すと凍結のハッシュの対象と形式が変わる。判断 118 の 4）。

### 2-B（minor）§6.4 の新しい文が §2.5 と §4.5 と食い違う
- 裏取り: **部分的に真**。key 行から打ち切りの候補は分かるが、macOS では入力モードが key 行に残らないので確定できない。「別の情報源でしか分からない」は言い過ぎで、「key 行だけでは確定できない」が正確。
- 対応: §6.4（「A session that is cut off has no row; the key rows of a log show candidates for one (a run of letter keys that no session row covers), but on macOS they do not record the input mode, so a candidate cannot be confirmed from the log alone.」）。打ち切りが 4 つの量を動かす向きを 1 文ずつ足した。§7 の打ち切りの項にも参照を足した。

### 3-A（minor）中止の上限が「ブロックごと」か「合計」か決まっていない
- 対応: §3.4 の「**Presses from outside.**」の段落（区間は oracle の `block_begin` で切り、区間ごとに「送った打鍵で説明されない参照の key-down の数」が手順の作る打鍵〔最初の区間は k・最後の区間は印だけ・ほかは印＋k〕を超えたら中止）。`delivery.py` の `_segments` が区間ごとの数を出し、`pipeline.py` の `reference_abort_segments` が当てる。

### 3-B（nit）§6.7 の「none of the four layers」
- 対応: §6.7 の最後（「the trials of the layer none (section 6.4)」）。

### 3-C（nit）§3.1 の 188 の言い方が §4.5 の広げた定義と合わない
- 裏取り: **部分的に真**。メインが予測から数えると、ON の carried out 188 はすべて後の試行で終わる（文は正しい）が、OFF の 186 のうち 1 つは後の試行で終わらない。
- 対応: §3.1（「186 (all S6; 185 of them run on into a later trial, and the session of the other is cut off by a press outside the trials)」）。

### 3-D（nit）・3-F（minor）§3.1 の約束の書き方と「何を」
- 対応: 1 つ目を 2 文に分けた（「The criteria that a run of the pilot has to meet for its raw logs to be deposited are written there before the freeze. The raw logs of the runs that meet them are deposited with the measurement data.」）。`pilot-macos.md` の Raw logs は「written before the freeze of the pre-registration」。2 つ目（合わせ直し）は、対象の run（`pilot2-on`・`pilot2-off`・`verify-off`。最初のパイロットの F13・F14 は観測に行が無いので外す）・`--markers-in-obs`・パイロットの 3 打鍵の印・使い道（コードの診断。欠陥が見つかれば凍結の前に直し、前後の割合を書く）を書いた。結果は 15 / 15 ブロック・282 試行・割り当てのない打鍵 0（欠陥は無くコードは変えていない）。⚠️ これらのログには欠けも足しも無いので、再同期は実ログでは試されていない（§3.1 にそう書いた）。

### 3-E（minor）人の打鍵の扱いが、パイロットと本計測で違う
- 研究者の採否: 預ける基準を本計測と揃える（判断 117 の Z3 (1)）。あわせて、観測のログに人の打鍵が入る経路を焦点の規則で閉じた（下の C2）。
- 対応: `pilot-macos.md` の Raw logs を置き換えた（「the observation records every key press on the machine」の前提はそのまま、「every key row … matched」を削除。§3.4 の規則がパイロットで決めた設定と run 自身の印〔3 打鍵〕で当たらないこと・`pipeline.py --check-deposit` が通ること・喪失の外では観測の余分な行は止めない〔本計測と同じ〕・封印したセッション行は凍結と本計測の後に預けるためにだけ開け、`--check-deposit` はその後に回す）。

### 3-G（nit）README と §6.8 でブロックを失う場合の言い方が違う
- 対応: 合わせ直しの錨を印の区分の連なりの**右の端**にした（コードの直し）。その結果、印の直前に足された矢印でもブロックを失わなくなり、ブロック末の閉じる Return が欠けて末尾の矢印が次の印とつながっても失うのはそのブロックだけになった。§6.8（「A difference therefore loses only the block that holds it, and a press added between two blocks loses none; this is checked by the selftest of the code on the cases it constructs, not proved in general.」）と `kit\e2\README.md` の Usage を同じ言い方にした。

### 3-H（要確認）§6.6 の「試行ごとの行の数」を出す箇所がコードに無い
- 裏取り: **真**。
- 対応: §6.6 の Cut-off（「Agreement with the specified rows is read from the detection counts of `pred_obs` under `over_limit` per stratum (the numbers of predicted and of observed rows, and the pairs, misses and false positives between them, section 6.5); no other statistic is computed for it.」）。新しい統計は足さない。

## B. round 4 で「部分的に解消／未解消」と判定した前の指摘

### 1-1 の残り（§6.2 の古い言い方）
- 対応: §6.2 の Not excluded（「the trials whose presses went into a session that the observer's rules cut off」）。

### 1-2（題が範囲を言っていない・nit）
- 採らなかった（round 3 から変わらない・任意の nit・メインの選択）。範囲は §1.3 にある。

### 1-a（パイロットの生ログを預ける基準）
- 対応: 上の 3-D・3-E。基準の中身が `pilot-macos.md` の Raw logs にある。

## C. 共通: round 4 の後に変わった、上の指摘に直接は対応しないもの

### C1. 預ける前の点検を runner が中止した run にも当てる（round 4 の直しの後に行ったコードの点検の指摘・研究者の採否・判断 119）
- 点検の指摘（裏取りは真）: runner が中止した run（Ctrl+C・前面の確認の失敗など、人の介入と相関しうる）は、§3.4 の規則が解析の中にしか無いため、預ける前に規則が当たらなかった。
- 研究者の採否と対応: `pipeline.py --pack` と `--check-deposit` が、完了・中止を問わずすべての run に §3.4 の規則を当て、当たる run と点検できない run（`delivery.py` が拒む・参照のログの無い観測のログ）を梱包しない。§3.4（「The same check is made on a run that the runner aborted: such a run is never analysed, and it is deposited only if the check passes or if it left neither a reference log nor an observation log.」）・`data.md` 手順 1 と梱包の手順。

### C2. 焦点の喪失を中止の理由に足し、その規則を凍結の前に 2 度改めた（判断 119・121・123）
- 点検の指摘（裏取りは真）: 観測器は機械のすべての打鍵の区分と時刻を記録し、預ける。人が参照以外のアプリに打つと、参照の点検には掛からない。§2.1 は「no person's typing is part of the data」。
- **最初の規則**（判断 119）: 参照が S15 の計画した切り替え（S15 の試行の窓の中で始まって戻る喪失）以外で焦点を失った run は中止。
- **1 度目の改訂**（判断 121）: 測定機でパイロットに当てると、`pilot2-off` に S15 以外の喪失が 1 回あった（31 ms・S1 の試行の考える時間の中・最後に送った打鍵から 2.7 秒後・前後 3 秒に観測の key 行も参照の key-down も 0）。他の 5 run では 0 回（6 run で約 87 分）。この頻度だと約 12 時間のセルで平均約 8 回になり、喪失ごとに中止にする規則ではほとんどの run が中止になりうる（観測は 1 回なので頻度の幅は大きい）→ 「喪失の区間（前後に余裕 500 ms）に観測の key 行が 1 つでもあれば中止」に改めた。採らなかった: 短い喪失を閾値で許す（値の根拠が弱い）・最初の規則のまま・規則を外して §7 に開示するだけ。
- **2 度目の改訂**（判断 123）: 1 度目の規則は、実行器が送った打鍵の行も数える。実行器は喪失の間も打鍵を送り、観測は機械のすべての打鍵を記録するので、打っている最中に喪失が起きると人がいなくても中止になる。本番の 2 計画を予測器の oracle の時刻で数えると、run の時間の **ON 78.1%・OFF 77.0%** が送った打鍵（試行の押下・印）から 500 ms 以内に当たる（31 ms の喪失として）→ 「計画外の喪失の区間（前後 500 ms・重なる区間はまとめる）ごとに、観測の key 行の数が、実行器が送って観測が記録する打鍵（試行の押下〔擬似キーとモードキーを除く〕と印の打鍵・区間の 100 ms 前から区間の終わりまでに送ったもの）の数を超えたら中止」に改めた。78% は §3.1 に開示した（最初の版を改めた理由として）。採らなかった: 1 度目の規則のまま・測定機で喪失の率を測り直してから決める。
- 今の文: §3.4 の「**Loss of focus.**」の段落・§3.1 の 2 つ目の項目の後半・§6.2 の最初の Other contingency（解析する run にも打っている最中の喪失がありうる・喪失中に送った打鍵は参照に届かず、その試行は計画と正解の食い違いとして現れ、除外しない）・§7 の新しい項「The stopping rule counts presses, not keys」・§2.1・`data.md`・`pilot-macos.md`。
- コード: `delivery.py` の定数 `FOCUS_MARGIN_MS = 500`・`OBS_SEND_DELAY_MS = 100` と `_focus_losses`（規則が使うのは `n_unplanned_loss_spans_with_unexplained_presses`。1 度目の改訂の数 `n_loss_intervals_unplanned_with_presses`・`n_presses_in_unplanned_losses` は記述として残した）。`pipeline.py` の `reference_abort_reasons` は前者 > 0 で中止。`e1_delivery.json` の `abort_rule` は `{focus_margin_ms, obs_send_delay_ms, pre_ms, reference_receives_mode_keys, runner_kana_presses_per_block, tail_ms, unplanned_focus_loss_with_unexplained_presses_aborts}`。
- メインの選択（研究者が覆せる）: 余裕 500 ms・送出の遅れ 100 ms（判断 122 の 6・判断 124 の 2）。⚠️ **100 ms はパイロットの実測で決めていない**（観測の遅れの実測は測定機の配送の報告にあり、この機械に無い）。

### C3. 採らなかったもの（このほか）
- 定数（`pipeline.py` の k と版、`delivery.py` の 500 と 100）と事前登録の文の一致を機械で検査すること（文と定数は同じコミットで決め、目で照合した・判断 120 の 9）。
- runner を変えて、かなキーを構造的に試行の窓の外へ出すこと（判断 116）。
- 問 3 の限界と ICC を k の階級ごとにも報告する・主を k ≥ m のテキストに限る（判断 116 の Z2）。
- 設計効果の式の出典を足すこと（判断 115 の 6）。

### ★ 名前の変化（古い言い方が残っていないかを見るときに）
- 判断 116〜124 で消えた・変わった名前: §3.4 の旧規則の「`excess_rows` over all presses is greater than zero」「`rows_outside_trials` exceeds the five presses … (four marker presses and one kana press)」・`data.md` の旧列「Reference `excess_rows` (all presses)」「Reference `rows_outside_trials` / limit」・`abort_rule` の `unplanned_focus_loss_aborts`（判断 119）→ `unplanned_focus_loss_with_presses_aborts`（判断 122）→ `unplanned_focus_loss_with_unexplained_presses_aborts`（判断 124）・「Presses outside every block are counted」・「usually near 1」・「none of the four layers」。
