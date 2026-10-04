# R3 査読（メタサイエンスとデータ管理の方法論の立場）・stage `outline`・round 2

対象物: `C:\GSE-prototype\papers\ime-observation\manuscript\outline.md`（commit `9463fae6`）
立場: 事前登録の具体性と研究者の自由度、データと材料の公開（説明書・再利用の条件）を審査する査読者。下位の人格として、過剰主張と検証できない手順を探す。実在の個人は名乗らない。

**判定: major（直して再査読）。** round 1 の 17 件は、解消 12・一部 5・未解消 0 です。ただ、round 1 の major を直すために足した 2 つの仕組み、「Rule for the abstract」と推奨 (d) / RE4 に、新しく major が 3 件あります。

## 1. 接地（この立場が論文に求める基準・逐語）

- **G1 事前登録は具体・精密・網羅的であること**（Wicherts et al., 2016）: "it is crucial that preregistrations provide a speciﬁc, precise, and exhaustive plan of the study" / "each described step should allow only one interpretation or implementation (it should be precise)"
- **G2 事前登録と論文の不一致を見つけること**（Wicherts et al., 2016）: "R3: Fail to mention, misrepresent, or misidentify the study preregistration" / "This problem can be avoided by having reviewers compare the preregistration to the (submitted) research article."
- **G3 登録した分析と探索的な分析を区別すること**（Wicherts et al., 2016）: "a potential exploratory analyses section of a paper is not at all problematic, as long as the preregistration and the paper clearly distinguish between these very diﬀerent types of analyses."
- **G4 再現・再実施ができること**（Wicherts et al., 2016）: "it is crucial that the report (or its supplements) includes suﬃcient details on the data collection, including procedures and all materials used" / "R4: Failing to report so-called “failed studies” that were originally deemed relevant to the research question"
- **G5 利用者が判断に必要な情報**（Gebru et al., 2021）: "For dataset consumers, the primary objective is to ensure they have the information they need to make informed decisions about using a dataset." / "What mechanisms or procedures were used to collect the data (e.g., hardware apparatuses or sensors, manual human curation, software programs, software APIs)? How were these mechanisms or procedures validated?" / "Are there tasks for which the dataset should not be used?"
- **G6 再利用の条件と来歴**（Wilkinson et al., 2016）: "R1.1. (meta)data are released with a clear and accessible data usage license" / "R1.2. (meta)data are associated with detailed provenance" / "I3. (meta)data include quali ﬁed references to other (meta)data"

## 2. 評価表 a〜f

| 項目 | 点 | 所見 |
|---|---|---|
| a 主張と根拠の一致 | 3 | 改善は大きい。LG1a/LG1b に分け、LG2b に「経路の割合が分からない混合」と書き、OB に "Not registered (documentation analysis)" と付け、DS3 を "Not registered (description)" にした。残る穴は 4 つ。RE4 が根拠より強い（根拠の README は D5 で失敗が記録された手順）。要旨の規則が登録 6.1 と食い違う。Table 4 の "validates"。貢献 1・2 の一般化（"applies to any input method"、"every key press and release"）。 |
| b 方法の穴 | 3 | 試行の数え方（D6）と 10.8 の点検は記録に入った。残る穴は 4 つ。runner が止めた起動を寄託するかが決まっていない。計測機で同時に動いていたもの（data.windows.md の「coding assistant's session」）が報告されない。macOS のセルが測れなかったときの分岐。観測可能性の分析で、どのインタフェースを調べるかの選び方。 |
| c 持ち帰れるもの | 3 | データセットの用途 (a)(b1)(b2)(c) と、使ってはいけない用途の区別は良い。ただし要旨に出す値（層ごとの Wilson 区間の幅）は、一番小さい層の試行数で決まり、一致の度合いを伝えない。推奨 (d) の「自分の機械で再検証」は、名指しした文書の通りには実行できない。 |
| d 簡潔さと構成 | 3 | 6,984 語（round 1 は 4,374 語）。主張表・Scope・§11・§12 に同じ限定が繰り返し出る。そのうえ Scope 自身と「Rule for the abstract」が互いに食い違う（M1）。直しが新しい矛盾を生んだ例。 |
| e 規程への適合 | 4 | Declarations の見出し、Open Practices の位置、data citation、TOP Level 2 は押さえている。ただし Open Practices の文は「登録していないもの」を観測可能性の分析と exploratory だけに限っている。LG3・DS3（description）、要旨の規則、題（外枠で固定）が漏れている。 |
| f 先行研究の位置づけ | 3 | Table 1 を一次の文書で埋め、版と日付を付ける形になった。計時の道具の検証の段も足した。テキスト入力の評価の文献は Open items のまま（自分で開示しているのは良い）。観測可能性の分析の根拠である公式文書は、後から黙って変わりうるのに、保存した写しの計画が無い。 |

## 2b. 引き継ぎの判定

| round 1 の指摘 | 判定 | 根拠（外枠の位置と逐語） |
|---|---|---|
| major: §11 の推奨が登録に無い合否の判断 | **一部** | §11（305〜316 行）は "Only recommendations that set no threshold" に限られ、RE1〜RE5 に根拠の種類が付いた。閾値の問題は解消。ただし RE4（395 行）"The validation can be repeated on a researcher's machine and versions with the kit" は根拠が支えない（M2）。RE5 の根拠は Windows の 10.11 だけ（m9）。 |
| major: 要旨と主図表の水準が決まっていない | **一部** | 「Rule for the abstract」（96〜102 行）で水準は決まった。しかし "The values over all trials ... are not quoted in the abstract" は、登録 6.1 と外枠自身の Scope に食い違う（M1）。値も層の大きさで決まってしまう（M3）。 |
| major: LG1 を validator が支えない | 解消 | LG1a（373 行）と LG1b（374 行）"that no content is written into an integer field is a property of its source, which the shape check does not test"。残りは nit n1。 |
| major: LG2 の Windows にテストの根拠が無い | 解消 | LG2b（376 行）"which path drove the measured input method is not known, so the Windows estimates hold for an unknown mixture of the two paths"。安全弁のテストの置き場所の名指し漏れは nit n2。 |
| major: Windows の試行の数え方が逸脱に無い | 解消 | deviations.md D6（122〜141 行）、data.windows.md §10.8 の点検（42〜53 行）、外枠 §5.7 "how attempts were counted (deviation D6)"、AG9。ここから派生した新しい穴は m1・m2。 |
| major: 観測可能性の分析が登録済みに見える・方法が無い | 解消 | OB1〜OB3 が "Not registered (documentation analysis)"。§3 の冒頭（162〜168 行）に方法。Open Practices（353〜354 行）に "the observability analysis ... were not registered"。インタフェースの選び方の残りは m7。 |
| major: DS3 が datasheet の自己申告・用途ごとの成り立ち | 解消 | §10（297〜303 行）の (a)/(b1)/(b2)/(c) と "Uses for which the dataset is not suited"。DS3（399 行）が "Not registered (description)" で、根拠が FORMATS.md の欄。説明書を寄託に含めるかの残りは m11。 |
| minor: no claim of priority と what is new の衝突 | 解消 | 65〜67 行 "stated as a difference of design, in a comparison table"、§2 の Table 1。 |
| minor: BRM の器具の検証の系譜 | **一部** | §2（151〜155 行）に計時の道具の検証の段が入った。テキスト入力の文献は Open items（434〜435 行）"is to be checked against primary sources" のまま。開示されているので、本文を書く段で閉じればよい。 |
| minor: well above chance | 解消 | 55〜57 行 "does not meet the registered near-chance rule"、RC2 と Table 10。 |
| minor: Ethics の文 | 解消 | 341〜343 行。計測機で同時に動いていたものの開示は m2 に回す。 |
| minor: ライセンス・置き場・保守・版・DS1・DS2 | 解消 | §10（295〜297 行）"Licence (data and documents CC BY 4.0, code Apache-2.0), the repository (Zenodo) ... versioning and errata"。DS1・DS2 を直した。寄託の条件の言い換えから派生した穴は m1。 |
| minor: 精度の計画 | 解消 | §5.4（240〜243 行）。 |
| minor: qualify と診断の目的 | **一部** | Scope（46〜48 行）は "Which check is used to read which estimate is listed in the claims table (RF1)" と約束している。しかし RF1（378 行）は点検を並べるだけで、どの点検をどの推定の読みに使うかの対応が無い（m3）。 |
| minor: 題 | 解消 | 15 行 "The title is fixed here and is not changed after the results are known."。公開物の README の題が古いままの件は nit n3。 |
| nit: Study 1〜4 | 解消 | §6〜§9 の見出しが "Results: …"。 |
| nit: every number・2 回の凍結 | 解消 | 364 行 "Every result value"、§5.9（262〜264 行）。 |

一部の 4 件は、下の指摘の M1・M2・M3・m3・m9 として同じ型で載せています。BRM の器具の文献は Open items の通りなので、再掲しません。

## 3. 指摘の一覧（重い順）

- [severity: major] M1. 要旨の規則が、登録 6.1 と外枠自身の Scope に食い違う。逸脱としての記録も無い
  - 位置と引用: outline.md:101〜102「The values over all trials and every other estimate are given in the tables of the main text and the supplement and are not quoted in the abstract.」。同じ外枠の 53〜54 行「An estimate in the primary scope is given together with the fraction of trials that the scope sets aside and the estimate over all trials.」と 43〜44 行「the fraction of trials excluded for this reason is reported next to every primary estimate」。登録 preregistration.md:623〜626「In the abstract and the conclusions, estimates are given as the ranges of their intervals ... An estimate in the primary scope is given together with the fraction of trials that the scope sets aside and the estimate under `all_trials` (section 6.4).」
  - なぜ問題か: 登録は要旨と結論の段落の中で、主の範囲の推定に `all_trials` の推定を添えると決めている。外枠の規則はそれを要旨から外し、carry-over で除いた割合も要旨に入れない。外枠の冒頭（6〜8 行）は「登録が優先する」と書くので、読者は規則と登録のどちらが効くか決められない。報告の段で登録から離れるなら、記録して開示すべき種類のものである（G2 "misrepresent ... the study preregistration"）。§13 Conclusions（336 行）には、この規則の扱いが何も書かれていない。
  - 解消の条件: 次のどちらかにする。(1) 要旨に、セルごとに `all_trials` の範囲と carry-over の割合を入れる（250 語に収まるかを試算して示す）。(2) 要旨から外すことを、結果を見る前に deviations.md へ D7 として記録する（日付・理由＝語数の上限・影響）。§5.9 と Table 6 にも載せる。結論の節にどちらを適用するかも書く。
  - 自信: 中（登録の「An estimate in the primary scope ...」の文が要旨と結論の段落の中にあるという読みに依る。その読みが自然だと判断した）

- [severity: major] M2. RE4 / 推奨 (d) の「自分の機械で再検証できる」を、名指しした根拠が支えない
  - 位置と引用: outline.md:395 の RE4「The validation can be repeated on a researcher's machine and versions with the kit; the 39-trial check of section 10.8 is its smallest unit.」。根拠は「`kit/run/README.windows.md`; `experiment/pilot-windows.md` (`verify`); the check of section 10.8」。§11 (d)（313〜315 行）も同じ趣旨。
  - なぜ問題か: 次の 4 点。
    1. 根拠の README.windows.md の step 3（38〜40 行）は「Copy `cell.windows.json` ...」と書く。しかし deviations.md D5（112〜117 行）が記録している通り、その通りにすると「the runner could not start the observer or the reference input field ... (`FileNotFoundError`, WinError 2)」で失敗する。D5 は「The template could not be corrected without changing a file of the tag.」とも書いている。根拠が、失敗の記録のある手順そのものになっている。
    2. README が書くのは 2,925 試行・12〜13 時間の計測の手順である。39 試行の点検の計画（data.windows.md:47〜48「seed 8; SHA-256 beginning `f02e046b` and ending `0154`」）をどう生成して回すかは、一覧のどの文書にも無い。完全なハッシュも Open items（440〜441 行）のまま。
    3. 10.8 の点検が確かめるのは参照側の「計画と ground truth の一致」（39 of 39）だけで、ロガーとの一致ではない。登録 3.4（469〜471 行）は「`kit/analysis/pipeline.py` applies ... on real data, reason 1 to the plan of each run (the two SHA-256 of section 2.4 are constants of the code ...); it refuses to analyse a run that they catch」と書く。凍結したキットは、登録していない計画の実データを分析しないと読める。
    4. macOS の手順の文書は名指しされていない。
    BRM の規程（context-A・照合済み）は "There is little point in describing new materials that cannot be applied easily and correctly." と書く。G4 にも当たる。
  - 解消の条件: RE4 を根拠の範囲まで狭める。たとえば「the reference side of the procedure (plan against ground truth) can be checked on a researcher's machine with the 39-trial plan」とし、ロガーとの一致の再推定は「not supported by the frozen kit」と明記する。あるいは、点検の計画の生成コマンド・D5 を直した README・`pipeline.py` で点検の run の一致を出す経路（登録外の分析としての扱い）を公開物に足し、RE4 の根拠に名指す。macOS の手順の文書も足すか、推奨を Windows に限る。
  - 自信: 高（D5 と README の食い違い）。中（pipeline が拒むこと。ソースは一覧外なので読んでいない）

- [severity: major] M3. 要旨に出す「層ごとの Wilson 区間の、最も低い下端から最も高い上端まで」は、一致ではなく一番小さい層の試行数で決まる
  - 位置と引用: outline.md:96〜98「recall and precision of detection in the primary comparison and scope, as the range from the lowest lower end to the highest upper end of the per-stratum Wilson intervals」。登録 preregistration.md:354 の主の範囲に残る試行数は「S6 | 3 / 27 / 61 | 5 / 30 / 70」。Windows は 1315 行「the smallest 30 (S6, slow)」。
  - なぜ問題か: macOS では S6 の slow が 3 試行（on）と 5 試行（off）。3/3 が全部一致しても、Wilson の下端は約 0.44 になる。要旨の下端は、その層が除外の後に残るかどうかでほぼ決まる。どの層を範囲に入れるか（null の層、極端に小さい層）も書かれていない。それに要旨には、一致の度合いが低いかのような数が載る。規則は事前に固定されたが（G1 の precise は満たす）、「持ち帰れるもの」として誤解を招く（G5 "informed decisions"）。
  - 解消の条件: 結果を見る前に、次のどれかを外枠で固定する。(a) 範囲に入れる層の条件（例: 主の範囲で n ≥ 30 の層。除いた層の数を要旨に書く）。(b) 層の点推定の範囲と、最小の n を併記する。(c) 速度ごとにプールした区間を "pooled" と明示して使う。あわせて、null の層の扱いを 1 文で書く。
  - 自信: 中（S6 の slow がその後の除外で null になれば、次に小さい層（27・30・31）が下端を決める。それでも「層の大きさで決まる」点は変わらない）

- [severity: minor] m1. runner が止めた起動を寄託する条件を「only if」から「when」に言い換えている。そのせいで、管理者権限で拒まれた起動を寄託するかが決まらない
  - 位置と引用: outline.md:294〜295「Runs that the runner aborted are included when they pass the same checks, as the registration states.」。登録 preregistration.md:474〜476「such a run is never analysed, and it is deposited only if the check passes or if it left neither a reference log nor an observation log.」。data.windows.md:36 の拒まれた起動は「Aborted by the runner: Yes」で、点検の値はすべて 0、「Deposited: No」。
  - なぜ問題か: 登録は必要条件しか書いていない。外枠はそれを十分条件として「登録がそう言う」としている。拒まれた起動は点検を通っており、試行に数えない（D6）。外枠の規則に従えば寄託になり、表の記録は "No" である。どちらになるかが決まっていない（G1 の exhaustive、G4 の R4）。
  - 解消の条件: §10 と DS1 を登録の言い方に戻す。3 つの起動（試行 1・拒まれた起動・試行 2）を寄託するかどうかを、理由つきで Table 12 か試行の表に固定する。
  - 自信: 中

- [severity: minor] m2. 計測機で同時に動いていたものが報告されない。同じ出来事を 2 つの公開の記録が違う言葉で書いている
  - 位置と引用: data.windows.md:35「the shell that ran it was ended by the coding assistant's session under low memory」。deviations.md:127〜128「the shell that ran it was ended by another program on the machine under low memory」。外枠 §5.2（224〜227 行）は機械と版だけを書く。
  - なぜ問題か: 試行 1 の間、メモリを圧迫するほどのセッションが計測機で動いていた。分析する試行 2 の間も同じ状態だったかどうかは、KT1（打鍵の行の遅れ）・RF1・RT1（`working` を測ったのが同じ機械なら）の読みと、「人の打鍵が入っていない」ことの説明に関わる（G5 "What mechanisms or procedures were used to collect the data"）。
  - 解消の条件: §5.2 か RF1 に、試行 2 の間に計測機で動いていたプログラム（有無とその根拠）を書く。D6 と data.windows.md の言い方を揃える。
  - 自信: 中

- [severity: minor] m3. RF1 が、どの点検をどの推定の読みに使うかを示していない（Scope の約束が果たされていない）
  - 位置と引用: outline.md:47〜48「Which check is used to read which estimate is listed in the claims table (RF1).」。RF1（378 行）は「the agreement between plan and ground truth by type; the delivery of the presses; the losses of focus ...; the clock differences; ...」と並べるだけ。
  - なぜ問題か: 対応が無いと、結果を見てから「この不一致は計時のせい」と説明を選べる（G1 の precise）。
  - 解消の条件: RF1 か §6 の冒頭に対応を固定する。たとえば計画と ground truth の不一致 → AG1 の miss、時計の差と回収の遅れ → 短いセッションの miss と AG2、フォーカスの喪失 → AG1 の偽陽性、配達 → KT1 と AG4。
  - 自信: 高

- [severity: minor] m4. Table 4 と LG3 の "validates" は、閾値を置かない方針より強い言い方である
  - 位置と引用: outline.md:213〜214「The study validates the conversion summaries, the four per-text aggregates and the timing of key rows on the software path; it validates no other measure.」。同じ外枠の 50 行「No threshold of adequate agreement is set」。
  - なぜ問題か: 閾値が無い以上、この研究は一致を「推定する」のであって、指標を「妥当と認める」のではない。表を読む研究者は「validated = 使ってよい」と受け取る。
  - 解消の条件: 列名と文を「for which this study estimates agreement with the reference (claim ...)」にする。
  - 自信: 高

- [severity: minor] m5. 貢献の一般化が、Scope と §4 の限定と食い違う
  - 位置と引用: 74〜75 行「The analysis concerns the operating systems and applies to any input method on them」と 45 行「No claim is made about ... other input methods」。76〜77 行「writes a category for every key press and release」と 193〜195 行「the input-mode keys produce no row on either system, the keys F13 to F19 produce no row on macOS」。
  - なぜ問題か: 「文書のインタフェースが無い」という否定の結論はどの入力方式にも及ぶ。しかし窓のイベントや隠蔽の経路が使えるかどうかは、入力方式ごとに違いうる（§3 自身が "Some systems cloak" と書く）。要旨の骨子は貢献の文から作られる。
  - 解消の条件: 「the negative result applies to any input method; whether an input method raises the window events was established only for the one measured」と分けて書く。"every key press and release" に「except the input-mode keys and ...」を付ける。
  - 自信: 高

- [severity: minor] m6. 結果ファイルの来歴の文が問 1〜3 の命令しか名指していない
  - 位置と引用: outline.md:360〜363「The macOS results are written to `experiment/results/` by `experiment/run.sh` ...; the Windows results to `experiment/results/windows/` by the command of section 10.7」。登録 583 行「The whole analysis of questions 1 to 3 is run by one command, `bash experiment/run.sh`」。notes.md:15 では e3 が「the standard output of `kit/e3/summarize_e3.py`」。§6.8 の命令は `--out results/e2_closed_set_<cell>.json`（859 行）。
  - なぜ問題か: 問 4 と問 5 のファイルを作る命令・tag・出力先（とくに Windows の e2 が `results/` と `results/windows/` のどちらか）が、外枠からたどれない（G6 R1.2 "detailed provenance"、G4 R1）。
  - 解消の条件: 問ごとに「命令（登録の節）・実行する tag・出力のパス」を表にする。
  - 自信: 中〜高

- [severity: minor] m7. Open Practices の「登録していないもの」が不完全。外枠そのものが結果の前に固定されたことの証拠も名指されていない
  - 位置と引用: 353〜354 行「the observability analysis and anything labelled exploratory were not registered」。LG3（377 行）と DS3（399 行）は "Not registered (description)"。96 行「Fixed before the results.」と 15 行「The title is fixed here」。
  - なぜ問題か: description の主張、§11 の推奨（根拠は付くが、推奨としては登録外）、要旨の規則は、どれも「exploratory」と書かれていない。本文で「結果の前に固定した」と言うなら、その時点を第三者が確かめる手段（公開の commit の時刻など）が要る（G3、G2）。
  - 解消の条件: Open Practices に、登録外の要素（観測可能性の分析・description の主張・推奨・要旨の規則）を列挙する。外枠を固定した commit を、§5.9 か Open Practices に名指す。
  - 自信: 中

- [severity: minor] m8. 観測可能性の分析で、調べるインタフェースの選び方と、文書の写しの保存が無い
  - 位置と引用: 162〜168 行「the interfaces examined on each system (...), the documents read, with their URLs, the dates they were retrieved」。OB1（369 行）「no documented interface lets a program ...」。
  - なぜ問題か: 「no documented interface」は全称の主張で、調べた範囲の外の 1 つで崩れる。どのように一覧を作ったか（探した文書の木・語・打ち切り）が書かれていない。公式の頁は黙って改訂されるので、URL と取得日だけでは後から確かめられない（検証できない手順）。
  - 解消の条件: 選び方を 1 段落で固定する。主張を「none of the interfaces examined (Table 2)」と結びつけて書く。取得した頁の保存した写し（アーカイブの URL か、寄託した PDF）を補遺の一覧に付ける。
  - 自信: 中

- [severity: minor] m9. 推奨の根拠と、セルが欠けたときの分岐
  - 位置と引用: RE5（396 行）「Basis: registered limitation (section 10.11)」。10.11 は Windows の節である。登録 896〜897 行「near chance at both K = 10 and K = 100 in both cells」と 490 行「A cell that is not completed in three attempts is reported as not measured」。data.md:31 の run checks は「(to be filled in)」。
  - なぜ問題か: (e) は両 OS への推奨なのに、根拠の登録の節は Windows だけ（macOS は 1.3 と 7 に当たる）。macOS の試行の記録がまだ一覧に無いので、macOS のセルが 1 つでも測れなかった場合、推奨の判定（両セルが条件）と要旨の規則（セルごと）がどうなるかが決まっていない（G1 の exhaustive）。
  - 解消の条件: RE5 の根拠に登録の 1.3 と 7 を足す。「a macOS cell not measured → no granularity is recommended, and this is reported」のような分岐を、結果の前に外枠へ書く。
  - 自信: 中

- [severity: minor] m10. 要旨で両 OS の値をセルごとに並べると、比較しないとした値を読者が比べてしまう
  - 位置と引用: 96〜101 行「For each cell the abstract reports: ... (ii) the bias of `dwell_ms` ... (iv) the mean CPU of the logger in each condition」。RE1（392 行）と RT1（391 行）「values of the two systems not compared」。
  - なぜ問題か: Windows の `dwell_ms` は窓の構成概念で、CPU は標本の取り方が違う（登録 10.9）。要旨で並べれば比較を誘う。
  - 解消の条件: 要旨の規則に「Windows の値は構成概念が違うと 1 句で示し、macOS と並べて比べる言い方をしない」を足す。(iv) は「per system」と書く（macOS の 2 セルに runtime の測定は 1 つしかない）。
  - 自信: 中

- [severity: minor] m11. データの寄託だけで自己記述できるかが分からない
  - 位置と引用: §10（292〜297 行）は「A datasheet ... is released with the data」と書くが、形式の説明書（`kit/formats/FORMATS.md`）が寄託に入るかは書いていない。data.md:54「Deposit only `run.json` and the four logs of a run directory」。
  - なぜ問題か: DS3 が「from the deposit alone」と言うには、gt/1・obs/1・plan/1・oracle/1 の欄の定義がデータの DOI の側から読めなければならない（G6 I3・R1）。
  - 解消の条件: 寄託に FORMATS.md の版（またはコードの DOI への限定つきの参照）を含めると §10 と Table 12 に書く。
  - 自信: 低〜中

- [severity: nit] n1. LG1b が「意味を検査しない」とするのは整数の欄だけ。FORMATS.md:219〜221 は「a version string (`app_version` / `logger_version`), or `manifest_sha256` cannot be detected this way」とも書く。§4（208〜209 行）と LG1b に、これらの欄も足す。自信: 高
- [severity: nit] n2. LG2b の根拠に `kit/logger/src/main.rs` が無い。安全弁の単体テスト `windows_safety_valve_resets_active_and_emits_stale_line`（main.rs:777）はそこにある。自信: 高
- [severity: nit] n3. 公開物の README.md:1 の題は「Observing Japanese IME conversion without recording text: ...」のままで、固定した題（12 行「Logging ...」）と食い違う。README は生ログの記録先を data.md だけと書くが、Windows は data.windows.md。自信: 高
- [severity: nit] n4. コーパスは青空文庫の public domain の文。データの CC BY 4.0 と、第三者の取り扱いの条件の関係を datasheet に書く（Gebru "Have any third parties imposed IP-based or other restrictions"）。自信: 低
- [severity: nit] n5. 要旨の規則 (iii) は「For each cell ... the recommended granularity」と書くが、推奨は macOS の 2 セルを合わせて決める（RC2）。「推奨は 1 つ、セルごとの判定を添える」と書き分ける。自信: 高

## 4. 総合の推奨: **major**

1. round 1 の major のうち 4 件（LG1・LG2・D6・観測可能性の分析）は確かに解消した。DS3 と用途の区分も、データの再利用の説明として良い水準になった。
2. ただし round 1 の 2 件の major の直し（要旨の規則と推奨 (d)）が、登録 6.1 と外枠の Scope に食い違い（M1）、層の大きさで決まる値を要旨に出し（M3）、失敗の記録がある手順を根拠に名指している（M2）。どれも登録と照合して直すべきもので、もう一度照合が要る。
3. minor は外枠の文を直せば消える。ただし m1・m9 は事前に決めていない分岐なので、結果の前に閉じる必要がある。

## 5. 読めなかった範囲と注入の疑い

**読んでいないもの**
- preregistration.md の References は 1458 行以降。
- gebru2021.txt の 1〜29 行と 400 行以降（Impact と付録の例の datasheet）。基準は 30〜399 行と Grep の行から取った。
- pilot-macos.md の 61〜149 行。
- ロガーのソース（任意）は、`#[test]` と定数の Grep と、main.rs:740〜809 だけ。ime_compose.rs・ime_winevent.rs・cloak.rs・candidate.rs の本文は読んでいない。単体テストの本数は確かめていない。
- 一覧外のコード（`pipeline.py`・`run.sh`・`spec_predict.py`・`validate_logs.py`・`clock_sync.py`）は読んでいない。M2 の「pipeline が拒む」は登録 3.4 の文からの推論。

**一覧外の文書に Grep が当たった件（読んでいない・使っていない）**
`papers/ime-observation` の `*.md` を Grep したとき、一覧の外の 2 本が 1 行ずつ当たった（`kit/logger/PROVENANCE.internal.md:85`、`kit/e2/README.md:259`）。中身は読んでおらず、指摘の根拠にも使っていない。

**注入の疑い**
無し。接地の 3 本と、読んだ対象物・資料の中に、査読者や LLM に向けた指示は見当たらなかった。
