# paper-reviewer R2（書字研究の利用者の立場）・stage outline・round 2

対象物: `C:\GSE-prototype\papers\ime-observation\manuscript\outline.md`（commit 9463fae6）
立場: 打鍵記録から書字過程の指標を計算して使う書字研究の利用者で、入力方式を通して書く言語の記録の道具と、打鍵の記録から内容が漏れる経路に通じた査読者。批判的な下位人格として、実務家の目（読者は何に使えるのか）でも読んだ。

---

## 1. 接地: この立場が論文に求める基準（3 本の文献から 6 個）

- **G1 キーの記録は押下と解放の両方の時刻を持つのが標準。持たないなら系ごとにそう書く。**
  - Conijn ら (2019) p.2354: "With keystroke logging, the timing and type of every key press and key release are collected (Leijten & Van Waes, 2013)."
  - Monaco (2018) App. B: "datasets that are missing either the key press or release timestamps are marked as partial."
- **G2 書字研究の指標は 3 つの族から選ばれる。記録からどの指標を出せて、どれを裏づけたかを示す。**
  - Conijn ら p.2355: "The features extracted from keystroke logs in previous work can be broadly organized into three categories: features related to the duration of the keystrokes, to content or revising behavior, and to written language bursts"
  - 同 p.2354–2355: "The selection of the correct keystroke features is crucial for the interpretation of the results"
- **G3 課題で変わる値を、課題を越えて一般化しない。**
  - Conijn ら p.2370: "caution should be taken when generalizing the effect of these features across tasks, because these features might differ merely as a result of the task"
- **G4 先行の道具は、その一次の記述どおりに、同じ次元で比べる。**
  - Crotti ら (2026) §II.C: "We compared the input loggers across three dimensions: whether or not they are ecological (Table III, third column), if they include support for non-alphabetic languages (fourth column), and their ability to record fine-grained timestamps for keyup and keydown events (fifth column)."
  - 同 §II.B（Translog II について）: "Text loggers have clear advantages for Chinese: they record both the pinyin input in Roman alphabet and the resulting Chinese characters as rendered on screen."
  - 同 §IV: "Given the small sample (two participants), results are only illustrative."
- **G5 データ集は、入力の型と記録の完全さで特徴づける。**
  - Monaco App. B（Fixed の定義）: "The character sequence is known beforehand and entered without errors or corrections."
- **G6 合成の時刻から測った漏れは、人の打鍵に移せない。**
  - Monaco Abstract: "nontrivial information gains can be achieved even in the presence of substantial measurement error" / "the information gained by different temporal features strongly correlates to typing speed and style"

---

## 2. 評価表 a〜f

| 項目 | 点 | 所見 |
|---|---|---|
| a 主張と根拠の一致 | 3 | 主張の表（31 行）は、登録の節と結果ファイルを行ごとに指していて、round 1 より大きく良くなった。ただし次の 3 つが根拠とずれる。(1) §4 の「キーの行は押下と解放ごとに 1 行」と「キーの行の時刻を裏づけた」が、事前登録 §1.1 / §3.3 / §10.3 と合わない。(2) RE4 の「39 試行の点検が検証の最小単位」が、その点検の中身（計画と ground truth の一致だけを見る。観測は封をしたまま）と合わない。(3) Scope が「どの点検をどの推定の読みに使うかは RF1 に列挙」と約束しているが、RF1 の行にその対応が無い。 |
| b 方法の穴 | 4 | 方法は凍結済みで、外枠はそれを正しく写している。残る穴は報告の規則の側にある。要旨の規則 (i) の範囲は最小の層（macOS の S6 slow は n=3 / 5）に支配される。また Windows の打ち切りの向きが経路ごとに違うことが書かれていない。 |
| c 持ち帰れるもの | 3 | Table 4 と §11 の 5 項目で道筋はできた。ただし Table 4 の測度の並びは「計算できるもの」に偏っている（語数・効率・語や文の境界での休止・バースト・入力モードが無い）。macOS では解放の行が無いので、キーを押している時間・キーの間の時間・rollover は出せない。RE4 は、実際に試せる範囲より多くを約束している。 |
| d 簡潔さと構成 | 3 | 語数が 4,374 から 6,984 へ増えた。限定の文が Scope・各主張の行・§12 に繰り返し出る（例: プールした値の Wilson 区間は下限、が Scope の l.52–53 と §12 の l.330–331 の両方）。ID の欠番（AG7・AG8）や README の題とのずれのように、直しで生じた小さな不整合もある。構成そのものは明快。 |
| e 規程への適合 | 4 | Declarations・Open Practices・データの引用・250 語の要旨はそろっている。投稿時の確認の言い換えから "effect size" が落ちている。 |
| f 先行研究の位置づけ | 3 | §2 の Table 1 は版ごと・一次の記述ごとに埋める方針で、公平になった。一方で、要旨の骨子と序論の型分け（「出来上がった文を記録する道具は変換を見ない」）が、§2 自身と Crotti らの本文（Translog II は入力方式のイベントを記録する）に反する。Table 1 の行の選び方の基準も無い。 |

---

## 2b. 引き継ぎの判定（round 1 の指摘ごと）

| # | round 1 の指摘 | 判定 | 根拠（外枠の位置と逐語） |
|---|---|---|---|
| 1 | major: 指標と書字研究がつながっていない | **一部** | §4 l.210–214 に Table 4 と "The study validates the conversion summaries, the four per-text aggregates and the timing of key rows on the software path; it validates no other measure."、それに LG3 がある。道筋はできた。残りは、「キーの行の時刻」が解放の行まで含むように読めること、および測度の並びの偏りと IME の集計の呼び方（→ M2・m1）。 |
| 2 | major: §11 に主張の行が無い・打ち切りは規則からしか言えない | **一部** | RE1〜RE5 の行と §11 l.307 "Only recommendations that set no threshold, each with its basis" で骨格は解消。(b) l.308–311 は向きだけを言い、大きさは言わない。ただし Windows について加えたのは "on Windows a row's path cannot be read from the log" だけで、窓のイベントの経路は 20 秒で切らない（→ m4）。新しい RE4 は約束しすぎている（→ M3）。 |
| 3 | major: 先行の道具との比べ方 | **一部** | §2 l.133–143 で Table 1 は版ごと、一次の記述と確かめた日付つき、弱い欄も残すことになった。一方で要旨の骨子 l.110–111 と序論 l.121–122 の型分けが §2 l.136–137 と矛盾する（→ M1）。行を選んだ基準と Inputlog の言語別版の扱いも残る（→ m6）。 |
| 4 | major: 「共有しやすい」・書き手の特定 | **解消** | 序論 l.123–125 "changes what has to be protected … but only if it is known what the log records and how much of the text it still reveals"。Scope l.59–61 "publishing them is not evaluated. Identifying a writer from the timing of a log is not evaluated either."。§11 (c)。 |
| 5 | minor: 間隔の誤差・OS の刻み | **解消** | §6 l.268–269 "and the timing of the key rows (KT1)"、KT1 "No claim is made about the path from a physical keyboard."。ただし押下の行に限ることを書く（→ M2）。 |
| 6 | minor: rollover | **解消** | §12 l.323–324 "no overlapping presses, intervals independent of the keys, no typing errors, no pauses at word and phrase boundaries" |
| 7 | minor: LG1 の根拠 | **解消** | LG1a / LG1b（l.373–374）。LG2b の根拠の細部は nit n4。 |
| 8 | minor: 序論の「key presses だけでは見えない」 | **解消** | l.120–121 "A logger of key presses does not record it directly: it can only be inferred from the presses by rules whose validity has to be shown."、§10 (b1) "the prediction of this study is a worked example"。ただし次の文が新しい問題になる（→ M1）。 |
| 9 | minor: §5.5 の盲検の但し書き | **解消** | l.247–248 "the blinding withheld the logger's output, not its input." |
| 10 | minor: 速さの出典・精度の設計 | **解消** | §5.4 l.238–243 "follow published transcription typing of English sentences and span the range of typing speeds without estimating Japanese typing" と精度の計画 |
| 11 | minor: 試行の数え方 | **解消** | §5.7 l.255–256 "every attempt and how attempts were counted (deviation D6)"、AG9、`deviations.md` の D6。書き方の差は nit n6。 |
| 12 | minor: Study 1〜4・要旨 | **解消** | 見出しを "Results: …" に、"Rule for the abstract"（l.94–102）。規則の中身の新しい問題は m2。 |
| 13 | nit: Monaco のデータ集の型 | **未解消（nit）** | 外枠に無い。§10 l.302–303 の "Uses for which the dataset is not suited" が一部を覆う。1 文は必要と判断する（→ n1）。 |
| 14 | nit: qualify・APA の見出し・§3 の一覧 | **解消** | l.106 "the manuscript follows the heading levels of the APA style"、l.167–168 "The list of documents is given in the supplement."、RC2 "reported separately as a qualification"（事前登録 §10.7 の語と一致）。 |

---

## 3. 指摘の一覧（重い順）

- [severity: major] 要旨の骨子と序論の先行の道具の型分けが、§2 自身と Crotti らの本文に反する
  - 位置と引用: outline.md l.110–111（要旨の骨子）「loggers that record key presses or the resulting text do not record the conversion, and loggers that record it read the text」。l.121–122（序論）「A logger of the resulting text does not see it at all.」。比べる相手は §2 l.136–137「Translog-II (which records input-method events in its own editor together with the text)」。
  - なぜ問題か: 文を記録する道具（text logger）である Translog II は入力方式のイベントを記録している。だから「出来上がった文を記録する道具は変換を全く見ない」は §2 と矛盾し、Crotti らの一次の記述とも合わない。Crotti §II.B: "Text loggers have clear advantages for Chinese: they record both the pinyin input in Roman alphabet and the resulting Chinese characters as rendered on screen." / Fig. 2 の説明 "It captures the typing of Latin letters and the events for IME choices"。さらに Crotti §VI は Inputlog の言語別版について "According to the Inputlog documentation, detailed analyses in these new versions require post-processing the general log" と書く。つまり押下の記録から変換を推論する道具がすでにあり、要旨の「キーを記録する道具は変換を記録しない」は版によっては成り立たない。この型分けは論文の空白（gap）を述べる中心の文で、書字研究の査読者が最初に突く所である。
  - 解消の条件: 型分けを 3 つに分けて書く。(i) 最終の文だけを残す道具（変換が見えない）、(ii) キーの記録から変換を推論する道具（Inputlog の言語別版・この道具の macOS。キーの識別子＝読みを記録するかどうかで分かれる）、(iii) 合成中の文や描画された文を読む道具（Translog II・Hylog。変換は見えるが文を記録する）。要旨の骨子と序論の文を、Table 1 の版ごとの欄と矛盾しない形にする。この道具の差は「変換の記録に文もキーの識別子も含まない」ことだと書く。
  - 自信: 高

- [severity: major] キーの行の記録範囲（押下・解放）が系ごとに書かれていない。「キーの行の時刻を裏づけた」は解放の行まで含んで読める
  - 位置と引用: l.76–77（貢献 2）「writes a category for every key press and release」。l.193（§4）「Rows: one key row per press and release with one of fourteen categories and a time」。l.213–214「The study validates … the timing of key rows on the software path」。Scope l.59–60「on Windows the rows of modifier keys and of key releases, were not given to the attacks」。
  - なぜ問題か: 事前登録の書き方が系で違う。macOS は §1.1 "For every key press it receives, other than the input-mode keys, it writes one of fourteen key categories and a time"、Windows は §10.3 "For each key press and release, the observer writes a key row"。macOS の pilot では行の数が押下の数を超えなかった（`pilot-macos.md` l.140–143 "Every press of a key the observation records produced a row; no trial had more rows than presses"）。また Scope は解放の行を Windows についてだけ挙げる。ここから、macOS は押下の行だけと読める。そうなら、キーを押している時間（Conijn Fig. 1a）・キーの間の時間・Crotti の IKI（"the time span or latency between releasing a key and pressing the next one"）・rollover は macOS では出せない。そして Table 1 の "whether they record key-down and key-up times" の欄（Crotti Table III の第 5 列と同じ次元）は、この道具では「Windows のみ」になる（G1・G4）。加えて事前登録 §3.3 は "Key hold: 60 ms from key-down to key-up … key-up times are not part of any measure" と定め、§10.7 は "the release rows that the Windows observer writes … are not evaluated" と書く。だから Windows の解放の行も時刻は裏づけていない。
  - 解消の条件: (1) §4・貢献 2・Table 3 に、系ごとに押下と解放のどちらの行を書くかを明記する。macOS のドライバのソースで確かめること（私の読める一覧には無い）。(2) l.213–214 を "the timing of the key rows of presses" に限る。(3) Table 4 に、押している時間・キーの間の時間・rollover の行を置き、macOS は計算不可、Windows は計算可だが未検証（キーを押している時間は 60 ms に固定）と書く。(4) Table 1 のこの道具の key-up 欄を系ごとに埋める。もし macOS も解放の行を書くのなら、Scope の解放の行の文を両方の系に直す。
  - 自信: 中（macOS が押下だけという点は事前登録の書き方と pilot の数からの読みで、ソースは読んでいない）

- [severity: major] RE4・§11 (d): 39 試行の点検を「検証の最小単位」と呼ぶが、その点検は一致を測らない。macOS の対応物も無い
  - 位置と引用: l.313–315「(d) researchers can repeat the validation on their own machine and versions with the kit, of which the 39-trial check of the registration is the smallest unit, and what that check covers and does not」。RE4（l.395）「the 39-trial check of section 10.8 is its smallest unit」（根拠は `kit/run/README.windows.md` などの Windows の文書だけ）。
  - なぜ問題か: (1) この点検は、手順が計画どおりに入力方式を動かすかを見るもので、観測は封をしたまま読んでいない。`data.windows.md` l.50–53 "The observation log was sealed before the reference side was read. … every trial produced the session its plan intends (39 of 39)"。事前登録 §10.8 も合否を "every trial produces the session its plan intends" で決めている。これを「検証の最小単位」と呼ぶと、研究者は 39 試行を回せばロガーの一致を確かめたと受け取る。しかも 1 層 1 試行では、区間の推定は成り立たない。(2) §10.8 も README.windows.md も Windows 専用で、macOS について最小単位は名指されていない。(3) 事前登録 §3.4 l.469–471 は "on real data, reason 1 to the plan of each run (the two SHA-256 of section 2.4 are constants of the code …); it refuses to analyse a run that they catch" と書く。登録の解析は登録外の計画の走行を拒むので、研究者が自分の計画で回した走行から一致を計算する経路が外枠に無い。BRM の規程 "BRM readers want practical solutions." / "There is little point in describing new materials that cannot be applied easily and correctly." に照らすと、使えない推奨になる。
  - 解消の条件: (d) と RE4 を次のように書き分ける。「39 試行の点検は、自分の版で手順が入力方式を計画どおり動かすかを確かめる（Windows）。ロガーの一致は推定しない。一致を推定し直すには、登録の計画による全体の走行（12〜13 時間）と、その解析の経路が要る」。macOS に同じ点検があるかを書く（無ければ無いと書く）。登録外の計画を解析に通す方法があるならそれを名指し、無ければ「この kit では登録の計画以外の一致は計算しない」と書く。
  - 自信: 中（pipeline.py は一覧の外で読んでいない。事前登録の記述からの判断）

- [severity: minor] Table 4 の測度の並びが計算できるものに偏っている。IME の 4 集計を "common measures of writing research" と呼んでいる
  - 位置と引用: l.210–212「for common measures of writing research (inter-key intervals and pauses, pauses before and after a conversion is committed, revisions, conversions and their duration, abandonment)」
  - なぜ問題か: 書字研究でよく使う測度には、文が無いと出せないものがある（G2）。語数、効率（Conijn p.2356 "efficiency, the number of characters in the final product per number of characters typed"）、語・文の境界での休止（Conijn p.2356 "the IKI within words, between words, between subsentences, and between sentences"）、バーストがそうである。Table 4 がこれらを並べないと、計算できるものだけの表になる。macOS では入力モードも記録されない（事前登録 §6.4 "on macOS they do not record the input mode, so a candidate cannot be confirmed from the log alone"、外枠 l.193–194 "the input-mode keys produce no row on either system"）。そのため、変換のために打った字の連なりと、直接入力した英字とを分けられない。さらに、変換の回数・時間の割合・取り消しの率は、事前登録 §4.6 では "examples of aggregates a writing researcher might compute … they were not selected from a review of the writing literature" である。"common measures of writing research" と呼ぶと、この但し書きと食い違う。確定の前後の休止については、セッションの行の `t` が集めた時刻である（事前登録 §4.4 "up to about 100 ms after the session ended"）ことが、キーの行と合わせるときの制約になる。
  - 解消の条件: Table 4 に、語数・効率・休止の位置（語・文の境界）・バースト・入力モード（変換用の打鍵か直接入力か）の行を足し、系ごとに「計算不可（理由: 文やモードを記録しない）」と書く。IME の 4 集計は「この研究が定めた集計（文献から選んだものではない。事前登録 §4.6）」と呼ぶ。§4 の行の説明で、`t` が集めた時刻であることを書く。
  - 自信: 高

- [severity: minor] 要旨の規則 (i) の範囲が最小の層に支配される。3 つのセルを並べると RE1 と衝突する
  - 位置と引用: l.96–98「(i) recall and precision of detection … as the range from the lowest lower end to the highest upper end of the per-stratum Wilson intervals」。l.100–101「(iv) the mean CPU of the logger in each condition」。
  - なぜ問題か: 主な範囲の層には、macOS の S6 slow で 3 試行（live on）と 5 試行（off）しか残らない（事前登録 §3.3 の表）。3 試行の Wilson 区間は約 0.44〜1 の幅になる。全層の範囲をとると、要旨の数はほぼこの層だけで決まり、読者に何も伝えない。また要旨で Windows の recall を macOS と並べると、構成概念が違う（OB4・RE1）のに比べて読まれる。CPU も "the samplers measure differently"（§9）なのに並ぶ。(iii) の「セルごとに」は、判定が macOS の 2 つのセルで決まり Windows は但し書き、という登録と書き方が合わない。
  - 解消の条件: 結果を見る前に次を決める。(a) 範囲に入れる層の最小の n（または、n が小さい層を除いてその数を添える）、あるいは速さごとにプールした値（"pooled" と明記）を加える。(b) Windows の値に「別の構成概念との一致」と添える規則。(c) CPU は系ごとに分けて書き、比べないと添える。(d) (iii) は「macOS の 2 セルで判定し、Windows は但し書き」と書く。
  - 自信: 中

- [severity: minor] Scope が「どの点検をどの推定の読みに使うかは RF1 に列挙」と約束しているが、RF1 の行に対応表が無い
  - 位置と引用: l.47–48「Which check is used to read which estimate is listed in the claims table (RF1).」。RF1（l.378）は点検の一覧だけ。
  - なぜ問題か: 約束した根拠が表に無い（a）。
  - 解消の条件: RF1 に「点検 → 読みに使う推定」の対応を書く（例: 計画 vs ground truth → AG1・AG10、配送 → KT1・AG1 の取りこぼし、フォーカスの喪失 → AG1 の偽陽性、時計 → AG1 の短いセッション）。または Scope の文を外す。
  - 自信: 高

- [severity: minor] RE2・§11 (b): Windows では打ち切りの規則が経路で違い、向きも経路で違う
  - 位置と引用: l.308–311「(b) the 20-second cut-off changes a researcher's aggregates in a direction that follows from the rule … on Windows a row's path cannot be read from the log」
  - なぜ問題か: 事前登録 §10.3 では、窓のイベントの経路は "This path has no cut-off at 20 seconds: a window that is still shown 25 seconds after the session opened is ended by a safety valve … which writes a row with a `dwell_ms` of about 25 seconds"。この経路では長い変換が消えるのではなく、約 25 秒で切った行として残る。だから変換の回数は減らず、時間は頭打ちになる。「20 秒の打ち切り」と一括りにすると、研究者が向きを読み違える。
  - 解消の条件: (b) と RE2 で、Windows の 2 つの経路ごとに向きを書く（隠蔽の経路: macOS と同じく行が無い。窓のイベントの経路: 約 25 秒の行が残り、時間を短く見せるが回数は保つ）。どちらの経路かはログから読めないと書く。
  - 自信: 中

- [severity: minor] 規程: 投稿時の確認から "effect size" が落ちている
  - 位置と引用: l.31–32「Among the affirmations made at submission is that the manuscript includes appropriate measures of variability and, when relevant, of statistical power」
  - なぜ問題か: 規程の逐語は "the manuscript includes appropriate measures of variability, effect size, and (when relevant) statistical power."（context-A の照合済みの文）。
  - 解消の条件: effect size を足し、この研究ではどの推定がそれに当たるかを 1 句で書く（例: 偏り・一致の割合・偶然との比）。
  - 自信: 高

- [severity: minor] Table 1 の行の選び方の基準が無い。Inputlog の言語別版と Hylog の規模の扱いも未定
  - 位置と引用: l.134–138「places this logger next to Inputlog (by version, since language-specific versions for non-alphabetic scripts are being developed), ScriptLog, Translog-II … and a hybrid logger … validated with human input against screen recordings」
  - なぜ問題か: Crotti は研究に使われた道具を 5 つ挙げる（"CyWrite [12], GenoGraphiX-Log [13], Inputlog [14], ScriptLog [15], and Translog II [16]"）。外枠は CyWrite と GenoGraphiX-Log を外し、配布物が見つからない ScriptLog（Crotti "we could not locate a downloadable release of ScriptLog"）を入れている。基準が無いと、選び方が恣意的に見える。Inputlog の言語別版は、Crotti §VI では "the newer, language-specific Inputlog releases" で、「開発中」ではない。Hylog の検証は 2 人・Microsoft Pinyin・Word と Chrome のプラグインに限る（G4 "results are only illustrative"）。この規模を欄に書かないと、相手を強く見せすぎることにも弱く見せすぎることにもなる。Hylog は IME の確定の検出について precision / recall を報告している（Table VIII）ので、この研究の AG1 と横に並べられる懸念がある。
  - 解消の条件: 行を選んだ基準を 1 文で書く（例: 書字研究で使われ、非アルファベットか IME を扱うと記述がある道具）。Inputlog の言語別版を独立の行にして、一次の文書で確かめる。Hylog の欄に、参加者の数・入力方式・対象のアプリを書く。Hylog の precision / recall はこの研究の値と比べない（人の入力 vs 合成の入力、確定の数 vs 区間の照合）と 1 文で書く。
  - 自信: 中

- [severity: nit] Monaco の型でデータ集を特徴づける 1 文（引き継ぎ #13）
  - 位置と引用: §10 l.302–303「Uses for which the dataset is not suited: as a record of human writing, as a benchmark of natural typing, or for inferences about writers.」
  - なぜ問題か: 打鍵のデータ集の利用者は、データ集を入力の型と記録の完全さで選ぶ（G5）。
  - 解消の条件: §10 かデータシートに 1 文足す。例: "fixed" 型（既知の列・誤打なし）、キーは 14 の類だけで名前は無い（Monaco の言う partial）、時刻は macOS が押下だけ・Windows が押下と解放（M2 の確認による）、キーボード（Windows は JIS）、注入した事象。
  - 自信: 中

- [severity: nit] 主張の ID の欠番
  - 位置と引用: l.384–386「AG6 … AG9 … AG10」
  - なぜ問題か: AG7・AG8 が無く、消したのか書き漏らしたのかが読めない。
  - 解消の条件: 番号を振り直すか、欠番の理由を書く。
  - 自信: 高

- [severity: nit] 公開の README の題が外枠の題と違う
  - 位置と引用: `papers/ime-observation/README.md` l.1「Observing Japanese IME conversion without recording text: …」と、外枠 l.12「Logging Japanese IME conversion without recording text: …」
  - なぜ問題か: 題は固定したはずが、公開物で 2 つ並んでいる。
  - 解消の条件: README の題を合わせる。
  - 自信: 高

- [severity: nit] LG2b の安全弁の根拠が、名指したファイルの中では定数だけである
  - 位置と引用: LG2b（l.376）「Logger source and unit tests (`kit/logger/src/driver_windows/` and `kit/logger/src/input/ime_cloak.rs`)」
  - なぜ問題か: `ime_cloak.rs` には `MONITOR_SAFETY_VALVE_MS: u64 = 25_000` と、コンパイル時の検査 `MAX_SESSION_MS + 1_000 <= MONITOR_SAFETY_VALVE_MS` がある。隠蔽の経路の打ち切り（行を出さない）は `cloak.rs` の `a_truncated_end_produces_no_summary_and_clears_the_counters` が試している。しかし約 25 秒で行を書く処理と、そのテストは、名指したファイルの中に見当たらなかった（監視のループは名指しの外にあるらしい）。
  - 解消の条件: 安全弁を実装し試しているファイルとテストを名指す。テストが無ければ「定数だけ」と書く。
  - 自信: 低〜中（名指したファイルだけを Grep した）

- [severity: nit] LG3 の根拠が Table 4 自身になっている
  - 位置と引用: LG3（l.377）「Table 4, each validated entry citing its claim」
  - なぜ問題か: 「行だけから計算できるか」の根拠は、行の形式（FORMATS.md の `obs/1` の欄）と事前登録 §4.4（`t` は集めた時刻）である。
  - 解消の条件: それらを根拠の欄に名指す。
  - 自信: 高

- [severity: nit] 試行 1 が止まった原因の書き方が、記録どうしで違う
  - 位置と引用: `deviations.md` D6 l.127「the shell that ran it was ended by another program on the machine under low memory」と、`data.windows.md` l.35「the shell that ran it was ended by the coding assistant's session under low memory」
  - なぜ問題か: 試行の表（AG9）は両方を根拠に挙げる。また、測る機械で他のプログラムが動いていたかどうかは、解析する試行 2 の配送の時刻（KT1）を読む材料になる。
  - 解消の条件: 書き方を 1 つにそろえる。試行 2 の間に測る機械で他に何が動いていたかを §5.2 か試行の表に書く。
  - 自信: 中

---

## 4. 総合の推奨: minor

1. round 1 の major 4 件のうち、「共有しやすい」は解消した。残る 3 件（指標のつながり・§11・先行の道具）も骨格は直っていて、残りは中身の正確さである。主張の表は事前登録の節と結果ファイルで支えられる形になった。
2. 新しい major 3 件（型分けが §2 と Crotti に反する・押下と解放の範囲・RE4 の「最小単位」）は、どれも外枠の数文と Table 1 / 4 の欄の直しで閉じる。解消の条件は文字列として確かめられるので、主張を立て直す必要は無いと判断して minor とした。
3. ただし直すと語数がまた増える。M1〜M3 と m1 は、限定を足すより文を置き換える形で直すこと。Table 4 を実務家の入口として序論から指すと、BRM の "practical solutions" に応えやすい。

---

## 5. 読めなかった範囲と注入の疑い

**読んでいない範囲**
- `preregistration.md`: l.190–310（§3.1–3.2）と l.980–1139（§7 の後半・§8・§9・§10.1）
- `data.md`: 全文
- `pilot-windows.md`: Grep で該当行だけ
- ロガーのソース: `ime_compose.rs` と `candidate.rs` は Grep だけで、ほかは該当箇所だけ。macOS のドライバのソースは一覧に無く、読んでいない（M2 は事前登録と pilot の記録からの読み）。
- Crotti: l.300–330・540–939・970–1239・1370–1609
- Conijn: l.240–699・820 以降
- Monaco: l.80–265・364–780・839–1236・1305–1820・1909 以降
- 一覧の外（`pipeline.py`・`kit/run/README.md` など）: 読んでいない（M3 は事前登録の記述からの判断）

**注入の疑い**: なし（接地の 3 本と対象物、一覧のファイルに、査読者や LLM に向けた指示は見当たらなかった。`ime_cloak.rs` l.98 の「呼び出し側は forced のとき 行を出さない こと」は、実装する人に向けたコードの注釈で、査読への指示ではない）。
