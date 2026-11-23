# 3〜5 名で計測と介入効果を言う設計 —— 単一事例・個人内の無作為化・推定器のタイミング・HCI の慣行

> 2026-10-31 / `/literature-review` 1 ラウンド / **設計の根拠**（案 A と案 B を選ぶ材料。gate の判定ではない）
> 対象: `.steering/20261031-gse-small-n-research-design/`（design.md の案 A・案 B）
> 名前空間: 方法論 = `V`（[V299]–[V311]）。既登録の再利用: [V28] [V4] [V58] [V123] [P258]

## 動機

- 研究者は、GSE の重い課題をユーザー検証の人数確保と見ている。2026-10-31 に研究の形から見直すと決め、軸を「計測」と「介入効果」の 2 本に置いた（同 decisions.md 判断 4）。採択後に見込む人数は研究者本人を含めて 3〜5 名。
- Codex の第二意見で、主要アウトカム `receipt_free_resumption` が自然作業ではまれで観測に穴がある（受領は clipboard の paste だけ・ADR-024 :232・:304）ことが分かり、統制課題で効果を測る案 B が立った。2 案の分かれ目を文献で接地する。

下位の問い（研究者が分け方を承認）:
- **S1**: 単一事例の設計で、3〜5 名・何回の反復があれば効果を主張できるとされるか（多重ベースライン・開始時点の無作為化）
- **S2**: MRT と N-of-1 は、人数が極めて少なく、アウトカムがまれで、持ち越しがあるときに成り立つか
- **S3**: 推定に基づくタイミングを、頻度を合わせた無作為のタイミング・固定スケジュール・単純なルールと直接比べた研究はあるか
- **S4**: HCI で少人数・長期・自己実験の研究はどう書かれ、事例の再現はどう一般化として受け取られるか

## 検証状態

- **探索**: サブエージェント 4 本（Sonnet・下位の問いごと・各 15 分・入れ子禁止・反証の角度を各本に指定）。2〜6 分で戻った。ACM DL と PMC は 403 や reCAPTCHA で取れないものが多く、要旨だけの文献が残った。
- **メインが一次で確かめたこと**: サブエージェントが保存した全文テキスト（WWC 2010・Liao 2016・Qian の MRT 解析・Boruvka 2018・Mishra 2021・Fischer 2011・Desjardins & Ball 2018・TummyTrials・Hornbæk 2014）の中で、カードに使う逐語が正規化した全文に在ることを機械で照合した（全件在った）。Mishra の p 値は前後の文と表の行も読んだ。Qian の版は arXiv の API で題を確かめた（[V4] = arXiv:2107.03544 "…: Experimental Design and Data Analysis Considerations"／今回読んだのは arXiv:2004.10241 "…: Data Analysis Methods"）。
- **要旨だけ**: [V300] [V301] [V302] [V307]。[V302] の数値はサブエージェントの要約経由で、一次で照合していない。
- **claim 抽出**: 13 件 → 検証 13 件: confirmed 9（3-0 が 5 / 2-1 が 4）／ 判定不能 2 ／ 否決 2

### claim 台帳

| # | claim | 出典 | 票 | 温度 |
|---|---|---|---|---|
| 1 | 単一事例の効果の主張には、異なる 3 時点（または 3 回の相の反復）での実証が要る。多重ベースラインは 3 つ以上の基線、6 相以上・各相 5 点以上で「基準を満たす」、各相 3 点以上で「留保つき」 | [V299] [V28] | **2-1** | 確定（留保: 3 回は逐語で "professional convention" であって検出力から出た数ではない） |
| 2 | 開始時点を無作為化した検定は、即時・急な効果では固定開始点より検出力が高い | [V300] | **2-1** | 確定（留保: 要旨のみ） |
| 3 | 効果が遅れて出る・じわじわ出るとき、全手続きの検出力が大きく落ち、固定開始点の方が勝つ | [V301] | **2-1** | 確定（留保: 要旨のみ。Nudge の効果の型は未知なので事前に登録が要る） |
| 4 | MRT の必要人数は、平均標準化効果 0.10・利用可能率 0.7 で N=32、効果 0.05・利用可能率 0.4 で N=193 の規模 | [V303] | **3-0** | 確定 |
| 5 | 1〜13 名の単一事例の設計は、持ち越しが無く、効果が個人内のばらつきを圧倒するほど強いときに MRT の代わりになる | [V303] | **3-0** | 確定 |
| 6 | MRT の推定量の標的は集団の周辺効果で、個人の因果効果は「通常は達成できない」。n<50 では小標本補正を勧める | [V305] | **3-0** | 確定 |
| 7 | 持ち越し（遅延効果）は無視できる前提ではなく、ラグ k の効果として定義・推定する対象である | [V304] [V305] | **3-0** | 確定 |
| 8 | n=1〜5 の MRT を実施・報告した事例 | — | — | **判定不能（0 件）** |
| 9 | 推定器のタイミングと頻度を合わせた無作為のタイミングを直接比べた研究は厳密には 1 件で、静的な推定器は近位の受容性で無作為に勝ち（+38%）、個人ごとに更新する推定器は有意に勝たなかった | [V306] | **2-1** | 確定（留保: 指標は通知への応答＝近位の受容性で、行動や作業の成果ではない。HCI の作業中のヒントへの外挿は未確認） |
| 10 | センサー駆動の通知と、時間帯を決めた毎日の通知の間に意味のある差は無かった | [V307] | **1-2** | 否決（下の否決リスト） |
| 11 | 推定器と単純なルールを直接比べた研究 | — | — | **判定不能（0 件）** |
| 12 | 個人内の効果の検出力は人数ではなく観測の回数で決まり、効果が小さいと長い記録が要る。12 日の自己実験では多くが「証拠なし」に終わった | [V310] | **3-0** | 確定 |
| 13 | HCI の再現は 891 本中 3%。再現は結果が繰り返せるかを確かめ、成り立つ・成り立たない条件を記述する | [V311] | **3-0** | 確定 |

票の視点: ① 内的妥当性 ② GSE への外挿（打鍵の推定・控えめなヒント・3〜5 名）③ 頑健性（未読の範囲・反証）。
判定不能 = 「4 本の探索（各 15 分以内）とメインの照合で見つからなかった」であって「存在しない」ではない。

## gate 判定（要点先出し・本ラウンドは設計の根拠）

- **S1 単一事例の基準**: 3〜5 名は WWC の多重ベースラインの下限（3 基線）にちょうど当たる。ただし 3 は慣行で、無作為化検定の検出力は効果が即時で大きいときにしか出ない（確定・要旨水準を含む）。
- **S2 個人内の無作為化**: MRT は集団の効果を標的にし、必要人数は数十〜数百（確定）。3〜5 名の MRT は根拠が無い（判定不能・0 件）。個人ごとの推定にするなら、持ち越しと観測回数が成否を決める（確定）。
- **S3 推定器のタイミング**: 頻度を合わせた無作為との直接比較は厳密に 1 件で、結果は推定器の種類で割れる（確定・近位指標のみ）。推定器 vs 単純なルールは 0 件（判定不能）。→ 案 B の比べは、先例が薄いぶん貢献の余地があり、負ける可能性も実在する。
- **S4 HCI の慣行**: CHI の n の最頻値は 12 で、少 n は確認的検定を主結果にせず記述と区間に留め、再現を前提にする（[V123]）。再現は HCI でまれ（3%）で、事例をまたいだ再現は分野の欠落を埋める位置づけで書ける（確定）。

→ **2 案への含意（私の読み・研究者が選ぶ）**: 3〜5 名では、案 A の多重ベースラインも MRT も「集団の効果」を言う設計にはならない。言えるのは **個人ごとの効果と、その事例をまたいだ再現**である。そのとき成否を決めるのは人数ではなく **1 人あたりのアウトカムの件数**と **効果の型（即時か漸進か）**で、ここが案 B（統制課題で件数を起こし、受領を観測できるようにする）に有利に働く。一方、案 B の「推定器 vs 無作為」は先例が 1 件で、推定器が勝たない結果も報告されている。

---

### カード1: 単一事例の効果の主張は「3 回の実証」が基準だが、その 3 は慣行である **[検証済 2-1]** [V299] [V28]

1. **どんなもの？** WWC が単一事例の設計の評価基準を定めた技術文書（2010 年のパイロット版。[V28] は 2013 年の論文版）。
2. **先行研究と比べてどこがすごい？** 基準を数で書いた: 逐語 "The study must include at least three attempts to demonstrate an intervention effect at three different points in time or with three different phase repetitions." ／ "To Meet Standards a multiple baseline design must have a minimum of six phases with at least 5 data points per phase. To Meet Standards with Reservations a multiple baseline design must have a minimum of six phases with at least 3 data points per phase."
3. **技術や手法のキモはどこ？** 反復は人を足すのと同じ働きをする: 逐語 "The minimum number of phase repetitions needed to meet the standard … is three, but four or more is recognized as more desirable (and statistically advantageous in cases in which, for example, the researcher is applying a randomization statistical test)."
4. **どうやって有効だと検証した？** 検証ではなく専門家パネルの合意。脚注 9 逐語 "The three demonstrations criterion is based on professional convention"。無作為化は逐語 "these applications are still rare"（2010 年時点）。
5. **議論はある？** 一般化の束ねは別の閾値を置く（逐語 "at least three different research teams at three different geographical locations"、実験計 20 以上）。3〜5 名の一報はその水準に届かない。5 点の最小には異論の立場表明がある（CEC Division for Research・本文未読）。
6. **次に読むべき論文は？** WWC Handbook の現行版の単一事例の節（未読）。Kratochwill & Levin の無作為化の議論（未読）。

### カード2: 開始時点の無作為化の検定は、効果の型で検出力が逆転する **[検証済 2-1]** [V300] [V301]

1. **どんなもの？** 多重ベースラインの無作為化検定 5 手続きをシミュレーションで比べた 2 本（要旨のみ）。
2. **先行研究と比べてどこがすごい？** [V300] 要旨逐語 "All five procedures were found to maintain their Type I error probabilities at acceptable levels. In most of the conditions investigated here, two of the random start-point procedures (Koehler-Levin and restricted Marascuilo-Busk) were more powerful than the others with respect to detecting immediate abrupt intervention effects."
3. **技術や手法のキモはどこ？** 効果の型（即時・急 / 遅れ / 漸進）で手続きの優劣が変わる。
4. **どうやって有効だと検証した？** シミュレーション。[V301] 要旨逐語 "(1) the powers of all of the procedures were severely diminished; and (2) … the single fixed intervention start-point procedures generally outperformed those with randomized intervention start points."（遅れて出る急な効果・即時の漸進的な効果）
5. **議論はある？** 控えめなヒントの効果が即時に急に出るとは限らない。効果の型を事前に登録しないと、検定の選び方が結果を見てからになる。人数と検出力の数値は本文で確かめていない。
6. **次に読むべき論文は？** 両論文の本文。Bouwmeester & Jongerling 2020（否決リスト 2）。

### カード3: MRT は集団の効果の設計で、3〜5 名には根拠が無い **[検証済 3-0]** [V303] [V305] [V4] [V58]

1. **どんなもの？** MRT の必要人数の算定（[V303]）と、MRT の解析の手引き（[V305]）。
2. **先行研究と比べてどこがすごい？** 人数を判断点の効果の大きさと利用可能率から出す。Table I（検出力 0.80・有意水準 0.05）: 平均標準化効果 0.10 で利用可能率 0.7 なら N=32、0.4 なら N=52。効果 0.05 なら N=112・193。
3. **技術や手法のキモはどこ？** 人数が小さく済むのは、効果の時間の形を先に仮定し、被験者内の対比も使うから（逐語 "both between-subject as well as within-subject contrasts in proximal responses are used"）。
4. **どうやって有効だと検証した？** シミュレーション。[V305] 逐語 "the ideal but usually unattainable goal is to determine the individual-level causal effect" ／ "When the sample size is small (e.g., n < 50), we recommend use of further small sample corrections for both the standard error and the degrees of freedom".
5. **議論はある？** [V303] は単一事例の設計を別物と位置づける: 逐語 "These trials usually only involve 1 to 13 participants" ／ "A critical assumption is that the effect of the treatment is only temporary (no carry-over effect) so that each participant can act as his own control." ／ "in settings in which treatments are expected to have sufficiently strong effects so as to overwhelm the within person variability in response … these designs provide an alternative to the micro-randomized trial design." 控えめな Nudge は「強い効果」に当たりにくい。まれな二値のアウトカムでの検出力は、読んだ範囲に無かった。
6. **次に読むべき論文は？** CENT 2015（N-of-1 の報告指針・未読）、AHRQ の N-of-1 の手引き（未読・washout の長さ）。

### カード4: 持ち越しは推定する対象である **[検証済 3-0]** [V304] [V305]

1. **どんなもの？** 時間とともに変わる因果効果の調整を扱う推定の枠組み（[V304]・応用は n=28 のパイロット）。
2. **先行研究と比べてどこがすごい？** 近位の効果とラグ k の効果を潜在結果で定義する。
3. **技術や手法のキモはどこ？** 逐語 "Many treatments may have delayed effects. … So in general both proximal and other lagged effects of treatments on the response variable may be of interest."
4. **どうやって有効だと検証した？** 漸近理論と n=T=30 規模のシミュレーション。n<30 の挙動は論文に無い。
5. **議論はある？** [V305] 逐語: 遅延効果の解釈は "averages over, in addition to the history information observed up to that decision point, future treatments and future covariates"。→ 観測窓と次の割付を重ねると、効果の意味が変わる（Codex の第二意見 2 と同じ向き）。
6. **次に読むべき論文は？** Piccininni ら（N-of-1 の因果推論・arXiv:2406.10360・要旨のみ・未登録）。

### カード5: 推定器のタイミング vs 頻度を合わせた無作為 —— 直接比較は 1 件で結果は割れる **[検証済 2-1]** [V306]

1. **どんなもの？** 歩数を促すチャットボットで、受容的な瞬間を推定して送る効果を測った 3 週間の現場実験（83 名、適応モデルは不具合で 61 名）。
2. **先行研究と比べてどこがすごい？** メッセージごとに {無作為 / 静的な推定器 / 個人ごとに更新する推定器} を等確率で割り付け、頻度をそろえた。推定器が 30 分以内に受容的な時点を見つけなければ 31 分目に送り、無作為として数える（逐語 "since 31 minutes later than a random time is still a random time"）。
3. **技術や手法のキモはどこ？** 発火の機会はサーバーが決め、推定器はその中で「いつ」だけを選ぶ。タイミングの付加価値だけを分けられる。
4. **どうやって有効だと検証した？** 逐語 "the static model showed a significant improvement of over 38% in just-in-time receptivity when compared to the control model (p < 0.001). The adaptive model had an improvement of more than 15% over the control model, but the improvement was not significant (p = 0.271)." ／ "the adaptive model did not perform significantly better than the control model if we considered the entire study duration".
5. **議論はある？** 指標は通知への応答（近位の受容性）で、行動の変化ではない。個人ごとに更新する推定器（GSE の個人化に近い）が勝たなかった。単純なルール（休止）と無作為の比べでは、通話・SMS の終わりに送ると応答が速かった（[V308]・逐語 "interruptions (notifications) are attended to and dealt with significantly more quickly after a user has finished an episode of mobile interaction compared to a random baseline condition"）が、これは推定器ではなく規則である。推定器 vs 単純なルールの直接比較は 0 件。
6. **次に読むべき論文は？** Künzler ら 2019（[V306] の静的モデルの学習元・未読）。Morrison ら 2017 の本文（否決リスト 1）。

### カード6: HCI の少人数研究は、観測の回数・再現・開示で強くなる **[検証済 3-0 / 2-1]** [V310] [V311] [V309] [V123]

1. **どんなもの？** 自己実験の N-of-1（[V310]・IBS の 15 名・12 日・完全無作為の交互処遇）、HCI の再現の量（[V311]）、自伝的デザインの緊張（[V309]）、CHI の n の分布（[V123]）。
2. **先行研究と比べてどこがすごい？** [V310] 逐語 "the individual serves as their own control, testing the individual's specific response to an intervention rather than a group's average" ／ "The statistical power of this type of design relies on the number of observations collected for that specific case or individual."
3. **技術や手法のキモはどこ？** [V310] 逐語 "A food trigger that has a small effect on IBS symptoms will require an ATD with a larger number of days to be detected." 12 日では多くが「証拠なし」だった（3-0）。
4. **どうやって有効だと検証した？** [V311] 逐語 "we examined four publication outlets (891 papers) and found 3% attempting replication of an earlier result" ／ "Replications thereby help establish whether a finding can be repeated – increasing confidence in its validity – and describe the conditions under which it holds or fails."（3-0）。[V123] は CHI の n の最頻値 12 を示し、少 n の研究は確認的検定を主結果にせず再現を前提にするよう読める（既登録の逐語）。
5. **議論はある？** [V309] 逐語 "While self-usage has long been regarded as a questionable approach in human-computer interaction (HCI) research, recent projects have shown the successful use of autobiographical design as a method to investigate long-term and intimate relations between people and technologies in everyday life." ／ "researchers rarely share the details about how they conducted their autobiographical design"。研究者本人を事例に含めるなら、その事例を他と分けて示し、緊張を開示する必要がある（2-1・留保: 効果の主張に使う場面は論文の対象外）。novelty と参加そのものの効果は、長期の記録でも交絡として残る（Klasnja ら 2011・本文未読・未登録）。
6. **次に読むべき論文は？** Klasnja, Consolvo & Pratt 2011（CHI・本文未取得）、Neustaedter & Sengers 2012（自伝的デザインの原典・未読）、Kaptein & Robertson 2012（未読）。

---

## 否決リスト

| # | 主張 | 票 | 否決の理由 |
|---|---|---|---|
| 1 | 推定器のタイミングは固定スケジュールと差が無い（Morrison ら 2017 [V307]） | 1-2 | 要旨だけで本文を読んでいない。比べた相手は無作為ではなく時間帯を決めた毎日の通知で、頻度の一致も厳密でない。カード本体の根拠にしない |
| 2 | 多重ベースライン AB の無作為化検定は、大きな効果（d=1）で 6 名、中程度（d=0.6）で 8〜10 名あれば検出力 .8（Bouwmeester & Jongerling 2020 [V302]） | 1-2 | 数値はサブエージェントの要約経由で、本文内に不一致（8 名と 10 名）がある。一次で照合するまで設計の数値に使わない |

## やり残し（次のラウンドの入口）

- [V302] の本文で、人数・測定回数・効果量ごとの検出力の表を照合する（案 A を採るなら必須）。
- まれな二値のアウトカムでの個人内の無作為化の検出力（0 件のまま）。
- N-of-1 の持ち越しと washout の長さの一次（CENT 2015・AHRQ の手引き）。
- 推定器 vs 単純なルール（休止の検出）の直接比較（0 件）。
- Klasnja ら 2011・Caine 2016 の本文の残り・Neustaedter & Sengers 2012。
