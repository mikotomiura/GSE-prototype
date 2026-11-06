# 文献カード: 公開データの知見の論文 1 の関連研究 —— CS1 の struggle の検出・打鍵の休止の測定・検出器の評価の方法

- **トピック**: public-data-findings-related-work
- **日付**: 2026-11-06
- **作業記録**: `.steering/20261105-public-data-findings-paper/`（判断 26）
- **用途**: 論文 1（JEDM）の外枠の「関連研究」の節（柱 3 つ）と、評価の設計・考察・限界の節の接地。gate 判定ではない。

## 動機

外枠（`paper-write/outline.md`・判断 25）の関連研究の節は、柱 3 つ（CS1 の過程からの struggle の検出／打鍵の休止の測定／検出器の評価の方法論）で書く。前のラウンド（`20261105-public-data-findings-novelty.md`）は新規性（手前から当てた報告・代理のラベル・休止の形・単位の揺れ）を扱ったが、柱の系譜そのものと、評価の方法（同等の判定・事例対照の揃え方・時間のリーク）は扱っていない。attack-me（outline round 1）の接地に使った Pelánek 2015・Gardner 2018・Lakens 2017 も未登録だった。本ラウンドは、references.md にある文献を番号だけ挙げ、未登録の文献を探した。

## 検証状態

- 下位の問い 3 つ（Q1 CS1 の過程のデータからの struggle の検出の系譜／Q2 打鍵の休止の測定／Q3 検出器の評価の方法）を、Sonnet のサブエージェント 3 本で並列に探した。どれにも反証の角度（Q1: 別のデータで再現しない報告／Q2: 休止が困難を示さない報告／Q3: 同等の検定・ROPE・揃えすぎへの批判）を含めた。
- 候補 42 本のうち 38 本を登録した（[V427]〜[V464]）。登録しなかったもの: Alamargot et al. 2007（「休止の前後の並列処理」・抄録も本文も未読）・Obuchowski 1997（書誌だけ）・Thomas et al. 2005（DOI なし・[V439] が再現している）・Wong et al. 2021（使う主張が否決・下）。
- 既登録で番号だけ挙げたもの: Q1 [V413]・[V414]・[V426]・[V86]・[P33]・[P34]・[P357]・[P121]・[V424]・[V243]・[V244]・[V366]・[V418]・[V419]／Q2 [V416]・[V423]・[V425]・[V422]・[V421]・[V160]〜[V164]・[V158]・[V31]・[V192]・[P36]・[P38]・[P123]・[P270]・[P44]／Q3 [V102]・[V98]・[V63]・[V89]・[V94]。
- メインが逐語を照合したもの: 全文は Pelánek 2015・Gardner & Brooks 2018・Lakens 2017（attack-me の接地のテキスト）・Ahadi et al. 2015（著者稿の PDF）・Medimorec & Risko 2017（著者校正の PDF）・Chenu et al. 2014（OA の PDF）。抄録は、OpenAlex か Europe PMC で 32 本の逐語を照合し、すべて一致した（Medimorec・Olive・Mansournia は OpenAlex に抄録が無く、原本か Europe PMC で照合）。書誌は 38 本とも Crossref（Pelánek は Zenodo・Benavoli は JMLR のページ）で確かめた。Švábenský et al. 2024 の表の数値と限界の節は、サブエージェントが ar5iv の要約を経て読んだだけで、メインは照合していない（下では抄録の逐語だけを使う）。
- claim 20 件（下の表の行）を抽出し、3 票（内的妥当性・外への広げ・頑健さ）で判定した。確定 9・留保つき確定 7・判定不能 4。否決 4（下）。

## 要点を先に

| 柱 | 問い | 温度 | 一言 |
|---|---|---|---|
| 1 | 古典の過程の指標（EQ・Watwin・RED・NPSM）は何を当てたか | 確定 | 学期単位の成績。元の報告は成績の分散の約 4 割（[V428]・[V430]） |
| 1 | 別のデータ・別の学期に持ち出すと | 確定 | 弱くなる・文脈に依る（[V431] の別データで r < 0.3・[V433]・[V429]・[V432]）。最良の EQ でも宿題の点に負ける（[V434]） |
| 1 | 分野の研究の多くは単一の機関・授業か | 確定 | 2 つの WG の総説が、検証と再現の不足を言う（[V435]・[V436]） |
| 1 | 細かい粒度・演習の最中の検出 | 確定（留保つき） | 細かい粒度ほど難しい（[V437]）。演習の最中に打鍵から未完了を当てる先行がある（[V438]・[V414]） |
| 1 | CS1 で、秒単位の出来事の手前を揃えた対照と比べた研究 | **判定不能（0 件）** | 前のラウンドと同じ |
| 1・2 | 区切りでの休止は、流暢さを考えに入れても成績と関わるか | 確定（留保つき） | 区切りでの遅さは語の中の流暢さで説明され、止まる頻度だけが残る（[V439]・5 学期） |
| 2 | 休止の意味は位置と定義で変わるか | 確定 | 効果の大半は位置で変わり、定義で結果が揺れる（[V440]・[V446]・[V447]） |
| 2 | 休止の閾値は書き手で揃うか | 確定（留保つき） | 書字の速さで変わり、混合の成分の数も書き手で違う（[V441]・[V442]・[V444]） |
| 2 | 上位の処理は打鍵と並行して進むか | 確定（留保つき） | 熟達した書き手では並行する（[V445]・手書き）。[V416] の打鍵の並列の説と合う |
| 2 | 窓単位の HMM で状態を分けた打鍵の研究 | 確定（留保つき） | 1 秒の窓の 3 状態の HMM で、計画様の状態が語と文の境界の前に増える（[V448]・境界であって停滞ではない） |
| 2 | 長い休止が困難を示さないと直接示した実証／長い休止の直前を短い休止の直前と比べた研究 | **判定不能（0 件）** | 解釈が一意でないという記述（[V443]・[V441]）はあるが、直接の測定は無い |
| 3 | AUC だけで評価してよいか | 確定 | AUC は相対の評価で較正を見ない。指標の選び方が結論を動かす（[V449]） |
| 3 | 学習分析でのモデルの比べの処方 | 確定 | 2 つのモデルの AUC の差に、ベイズの階層モデルと ROPE（[V450]・[V455]）。比べる対象が本研究（1 つの AUC と 0.5）と違う |
| 3 | 頻度論の区間 ∩ 幅は同等の判定として立つか | 確定 | 区間が幅の内側なら TOST の同等（[V451]・[V452]）。幅の恣意性は ROPE に限らない（[V453]）。どちらも小標本では弁別が弱い（[V454]） |
| 3 | 揃えない対照は精度を大きく見せるか | 確定（留保つき） | 症例と別の対照群で評価した診断の研究は過大評価（[V458] RDOR 3.0）。入れ子の事例対照が標準（[V457]）。早期警告の評価の定義はばらばら（[V459]） |
| 3 | 揃えた設計の解析 | 確定 | 揃えた共変量で調整しない要約は偏る（[V456]） |
| 3 | 揃えすぎの批判 | 確定（留保つき） | 揃えは選択の偏りを生み、精度を下げうる（[V460]・病因の研究）。揃えたデータで学ぶと識別が消える（[V461]・査読前・訓練の側） |
| 3 | 群と時間の構造とリーク | 確定 | 構造を無視した交差検証は誤差を過小評価（[V462]・[V98]）。クラスタのブートストラップは一貫（[V464]）。リークの定義（[V463]・[V102]） |
| 3 | AUC を事前の幅と頻度論の区間で同等と判定した研究／秒単位の手前を揃えた対照で同等の幅で評価した研究 | **判定不能（0 件）** | 探した範囲では無い |
| 3 | 出来事に近い窓だけを使うと性能が大きく見えることを数値で示した研究 | **判定不能（0 件）** | 近いのは [V458]（診断の設計）・[V461]（揃えの影響で向きは逆）だけ |

→ 柱 1 は「古典の指標は学期単位で、持ち出すと弱くなる」系譜として書け、本研究の「同じ母集団の取り置きで、出来事の秒単位の手前を揃えて比べる」をその先に置ける。柱 2 は「休止は位置・速さ・個人で読む」が厚く、本研究の個人化した θ と揃えた対照の動機になる。ただし本研究は位置（語・文・トークンの境界）では揃えていない（カード 3 の 5）。柱 3 は「区間 ∩ 幅」を TOST の形として正当化でき、ROPE（[V450]）との違いは比べる対象の違いとして 1〜2 文で書ける。揃えすぎの批判（[V460]・[V461]）は限界か考察で受ける必要がある（カード 6 の 5）。

---

### カード 1: 古典の過程の指標は学期単位の成績を当て、別のデータに持ち出すと弱くなる **[検証済 3-0]** [V427] [V428] [V429] [V430] [V431] [V432] [V433] [V434]

1. **どんなもの？** CS1 の編集とコンパイルの記録から、苦戦する学生を数で表す指標の系譜。Error Quotient（[V427]・Jadud 2006）は、続くコンパイルで同じ誤りが繰り返されるかを数える。Watwin（[V428]）・Repeated Error Density（[V429]・RED）・Normalized Programming State Model（[V430]・NPSM）が続いた。
2. **先行研究と比べてどこがすごい？** 元の報告は大きい。Watwin は 45 人で "explaining 42.49% of the variance in coursework marks"（[V428] 抄録）、NPSM は "accounted for 41% of the variance in students' programming assignment grades"（[V430] 抄録）。
3. **技術や手法の肝はどこ？** 単位はコンパイルの出来事の連なりで、当てるものは学期の成績か試験。[V427] の抄録: "This edit-compile cycle often represents students' attempts to make their programs syntactically, as opposed to semantically, correct."
4. **どうやって有効だと検証した？** 持ち出すと弱くなる。Ahadi et al. 2015（[V431]・メインが著者稿の全文を照合）は、EQ と Watwin を別の大学の CS1 で記述どおりに実装し、試験・成績との相関が "all low (r < 0.3)" だった。§6: "the approaches had relatively poor performance on the data at our disposal"。学習した予測器も、同じ授業の別の学期では落ちた（"the within-dataset performance was higher than that of the cross-semester performance"・§5.6 "it should be adjusted if the context changes"）。指標の側の著者も文脈への依存を言う（[V429] RED は "less context dependent" を利点に挙げる・[V433] "these metrics tend to be context dependent and contain free parameters"・[V432] "they have largely been developed and validated in narrow contexts"）。Švábenský et al. 2024（[V434]・n = 280）は、3 つの指標のうち EQ が最良だったが "though still not explaining most of the observed variability"（抄録）。
5. **議論はあるか？** 本研究にとっての意味: この系譜の指標は学期単位の結末を当て、出来事の秒単位の手前ではない。比べの相手が違うので、本研究の同等の結果はこれらの値を覆さない（前のラウンドのカード 1 と同じ）。持ち出すと弱くなるという系譜は、本研究が「作文で係数を決めた推定器を CS1 に持ち出した」ことと同じ問題の側にあり、関連研究で 1 文つなげられる。[V434] の「宿題の点に負けた」という数値（表）はメインが照合していないので、本文では抄録の逐語だけを使う。[V432] は抄録の前半しか読めていない（結果は未確認）。
6. **次に読むべき論文は？** [V432] の全文（ACM・Koli Calling 2015）。

### カード 2: 分野の研究の多くは単一の機関で、細かい粒度の検出は難しい **[検証済 3-0（[V435]・[V436]）・2-1（[V437]・[V438]）]** [V435] [V436] [V437] [V438]

1. **どんなもの？** ITiCSE の 2 つの WG の総説（[V435] 2015・[V436] 2018）と、粒度の細かい検出の 2 本（[V437] Rodrigo & Baker 2009・[V438] Fwa 2019）。
2. **先行研究と比べてどこがすごい？** [V435] 抄録: "the majority of the studies focus on simplistic metric analysis and are conducted within a single institution and a single course" ／ "a critical need for validation and replication"。[V436] 抄録: "increase efforts to validate and replicate work"。
3. **技術や手法の肝はどこ？** [V437] は、平均の水準では当たっても、実験室ごとの揺れの検出は "were less successful"（抄録）。[V438] は Java の演習の最中の打鍵と操作から、未完了を "on a granular basis"（抄録）で当てる。
4. **どうやって有効だと検証した？** 総説は文献の分類。[V437]・[V438] は抄録だけで、数値は確かめていない。
5. **議論はあるか？** 留保（1 票・[V437]・[V438]）: 抄録だけ。[V437] の「細かい」は実験室の間の揺れで、秒単位ではない。[V438] が対照を揃えたかは分からない。総説の 2 本は、本研究の「事前登録・同じ母集団の取り置き」の位置づけ（検証と再現の不足に応える）に使える。
6. **次に読むべき論文は？** [V438] の全文（SMU の機関リポジトリに OA）。

### カード 3: 休止は位置・速さ・書き手で読む **[検証済 3-0（位置）・2-1（速さと書き手）]** [V440] [V441] [V442] [V443] [V444] [V446] [V447]

1. **どんなもの？** 打鍵（と手書き）の休止の長さが、何で変わるかの研究。
2. **先行研究と比べてどこがすごい？** Medimorec & Risko 2017（[V440]・101 人・メインが著者校正の全文を照合）: "the majority of pause effects in written composition are modulated by pause location"・"inconsistencies when using various definitions of pauses"。課題でも向きが変わる（[V446] 翻訳と作文: "the mean length of pause at textual category boundaries grew the higher the category was in the linguistic hierarchy"）。打鍵の間隔は語の間 < 読点 < 句点の順に長い（[V447]・14 人）。
3. **技術や手法の肝はどこ？** 書き手ごとの分布で読む。Chenu et al. 2014（[V441]・メインが全文を照合）: "the optimal number of components depends on the writer and text"・"A pause of 200 ms between words, then, would not indicate the same operation for a young and older writer"・休止の長さは "might well be a function of mean writing speed"。[V442]（ロシア語・50 人）: "avoiding the imposition of fixed thresholds in pause analysis that are universally applicable to all writers"（抄録）。[V444]（JEDM の読者に近い ETS の系統）: 書き手ごとの重い裾の分布の母数は "robust across prompts designed to assess student proficiency for the same writing purpose"（抄録）。
4. **どうやって有効だと検証した？** [V440] は 3 つの区間 × 3 つの位置 × ジャンル。[V441] はガウスの混合（2〜4 成分）を書き手と文章ごとに当てた。
5. **議論はあるか？** 留保（1 票・速さと書き手）: [V441] は手書きの子ども、[V442] は抄録だけ。「休止は困難を示さない」と直接測った実証は 0 件で、上は「解釈が一意でない」という記述にとどまる（[V443] 抄録: "challenges in researching writers' pausing behavior (e.g., defining pauses)"）。本研究にとっての意味: 個人化した θ と、停滞にならない休止を対照に揃えることの動機になる。一方、本研究は停滞と対照を位置（語・文・トークンの境界）では揃えていない。[V440] の結果からは、位置が停滞と対照で偏ると手前の量も偏りうる。これは限界の節に 1 文で書く候補（PLAUSIBLE BUT UNPROVEN・本研究のデータで確かめていない）。
6. **次に読むべき論文は？** Schilperoord 1996・Wengelin 2006（書誌だけ確認・未読）。

### カード 4: 区切りでの遅さは流暢さで説明され、上位の処理は打鍵と並行する **[検証済 2-1]** [V439] [V445] [V448] [V416]

1. **どんなもの？** Koutcheme, Hellas & Leinonen 2026（[V439]）は、CS1 の打鍵の区切りの遅延と成績の関係を、公開データの 5 つの学期で概念的に再現した。Olive & Kellogg 2002（[V445]）は二重課題で、上位の処理が運動の実行と並行するかを調べた。Garcés-Manzanera 2026（[V448]）は L2 の作文の Inputlog の記録を 1 秒の窓に分け、3 状態の HMM を当てた。
2. **先行研究と比べてどこがすごい？** [V439] 抄録: "slower fluent typing went with lower exam scores, but we found no further association at chunk boundaries once fluency inside words was taken into account"・止まる頻度は "consistent across cohorts"。[V445] 抄録: "high-level processes are activated concurrently with motor execution"、ただし "not for children and not for adults who used an unpracticed uppercase script"。[V448] 抄録: "without treating pauses or deletions as direct cognitive evidence"・"Planning-like occupancy and dwell increased before words and sentences"。
3. **技術や手法の肝はどこ？** [V439] は区切りの遅延を語の中の流暢さで調整する（休止を流暢な打鍵との比で読む形）。[V448] は窓の特徴（時間・文字の増え・カーソル・編集）から状態を推定し、言語の境界は後の分析のために別に持つ。
4. **どうやって有効だと検証した？** [V439] は 5 学期（数値は抄録に無い）。[V445] は聴覚の探りへの反応時間の干渉。[V448] は 100 セッション。
5. **議論はあるか？** 留保（1 票）: 3 本とも抄録だけ（[V448] は ScienceDirect が 403・[V439] は 2026 年の Koli Calling で全文未取得）。[V445] は手書き。本研究にとっての意味: [V439] は「休止は流暢な打鍵との比で読む」を CS1 で支える。[V439] の公開データが本研究の CS1 と同じ系統かは確かめていない。[V445]・[V416] の並列の説の下では、停滞の手前に兆候が集まる理由は弱い（外枠の考察の「休止の理論との関係」・事前登録 P2）。[V448] は本研究の推定器に最も近い形（窓単位の HMM を打鍵に当てる）で、境界の前に状態が変わることを示すが、停滞の手前ではなく、揃えた対照との比べもない。関連研究の柱 2 で 1〜2 文で触れる候補。
6. **次に読むべき論文は？** [V448] と [V439] の全文。Alamargot et al. 2007（"Parallel Processing Before and After Pauses"・doi:10.1163/9781849508223_003・未読・未登録）。

### カード 5: AUC だけでは較正を見ず、同等の判定は区間 ∩ 幅で立つ **[検証済 3-0（[V449]〜[V452]）・2-1（[V453]・[V454]）]** [V449] [V450] [V451] [V452] [V453] [V454] [V455]

1. **どんなもの？** 学習分析の評価の指標（[V449] Pelánek 2015）、モデルの比べの統計（[V450] Gardner & Brooks 2018・[V455] Benavoli et al. 2017）、同等の検定（[V451] Lakens 2017・[V452] Lakens et al. 2018）と、その批判（[V453] Kruschke 2018・[V454] Linde et al. 2023）。
2. **先行研究と比べてどこがすごい？** [V449]（メインが全文を照合）: "the AUC metric considers predictions only in relative way – if all predictions are divided by 2, the AUC metric stays the same. For this reason the AUC metric should not be used (as the only metric) in cases where we need absolute values of predictions to be well calibrated"・"the choice of a metric can influence results more than the choice of a parameter fitting procedure"。[V450]（全文を照合）: "We recommend Bayesian hierarchical methods for model evaluation"・"By using a region of practical equivalence (ROPE), the Bayesian method separately estimates the magnitude and variability of each estimated effect (here, differences in AUC between a pair of models)"。
3. **技術や手法の肝はどこ？** [V451]（全文を照合）: "If the 90% CI falls within the equivalence bounds, the observed meta-analytic effect is statistically equivalent"（TOST の α = .05 に対応）。幅の根拠が無いときは "the maximum sample size you are willing to collect implicitly determines your SESOI"。[V452] は SESOI の決め方を並べる。
4. **どうやって有効だと検証した？** [V450] は MOOC の 96 モデルで 3 つの方法を比べた。[V454] はシミュレーション: "these two methods generally require over 250 cases within each condition when rather large equivalence margins of approximately .2 or .3 are used"（抄録）。
5. **議論はあるか？** 本研究にとっての意味: (1) 本研究の判定（書き手の再標本の 95% 区間が [0.45, 0.55] の内側）は、片側 2.5% の TOST の形にあたる。[V451] の 90% 区間（片側 5%）より厳しい側である。評価の設計の節で 1 文書く。(2) ROPE（[V450]・[V455]）は 2 つのモデルの AUC の差を比べる処方で、本研究は 1 つの推定器の AUC と 0.5 を比べる。違いは「比べる対象が違い、区間の被覆を再標本で較正できる頻度論の形を採った」と書ける。ただしこの「較正できる」は本研究の手順の主張で、文献の主張ではない。(3) [V453] 抄録: "analogous considerations apply to setting the decision thresholds for p values and Bayes factors"。幅の恣意性は ROPE でも同じで、どちらを採っても幅の根拠は問われる（外枠の限界「幅は実用の境界として正当化されていない」と合う）。(4) 留保（1 票・[V453]・[V454]）: 抄録だけで、[V454] の 250 件は効果量の尺度の数で AUC には移せない。本研究の実効の書き手 50.5 人は少ない側にあり、誤って同等とする割合を較正した（最大 5.2%）ことの動機として引ける。[V449] は、閾値の表を AUC と並べる理由（較正を見ない AUC の限り）に使える。
6. **次に読むべき論文は？** [V452]・[V454] の全文。AUC に TOST を当てた例（探していない）。

### カード 6: 揃えない対照は精度を大きく見せ、揃えすぎにも批判がある **[検証済 2-1（[V456]〜[V459]）・2-1（[V460]）・1 票は強い留保（[V461]）]** [V456] [V457] [V458] [V459] [V460] [V461]

1. **どんなもの？** 臨床の診断と早期警告の評価の、事例と対照の揃え方の研究。
2. **先行研究と比べてどこがすごい？** Lijmer et al. 1999（[V458]・184 研究のメタ疫学）抄録: "Studies evaluating tests in a diseased population and a separate control group overestimated the diagnostic performance compared with studies that used a clinical population (RDOR, 3.0; 95% confidence interval [CI], 2.0-4.5)"。Pepe et al. 2008（[V457]・PRoBE）は、出来事の前に集めた試料で評価する "nested case-control study design" を標準に置く。Fang et al. 2020（[V459]・48 研究）は早期警告の評価が "heterogeneous hence making it difficult to interpret and compare"。
3. **技術や手法の肝はどこ？** Janes & Pepe 2008（[V456]）抄録: "adjustment for the matching covariates is essential, as unadjusted summaries of classification accuracy can be biased"・"matching greatly complicates estimation of the incremental value of the marker"。
4. **どうやって有効だと検証した？** [V458] は相対の診断オッズ比のメタ回帰。[V456] は統計の理論と例。
5. **議論はあるか？** 留保（1 票・外への広げ）: どれも臨床の診断・予測で、行動の信号の秒単位の手前ではない。本研究にとっての意味: 揃えない対照が精度を大きく見せうること（[V458]）と、出来事の前の信号を出来事の後に事例と対照を選んで評価する形（[V457]）は、本研究の揃えた比べを関連研究の柱 3 に置く足場になる。ただし本研究のデータでは揃えない比べにも上がりが出なかった（H2 は分岐 4）ので、「揃えないと上がりが大きく見える」は本研究では言えない（外枠の「可能性にとどまる問題」(a)）。[V456] は、揃えた共変量（書き手・区切り・層）の内側の AUC を出すことと、揃えた設計の要約の偏りの関係を、評価の設計の節で 1 文確かめる材料になる。反証: Mansournia et al. 2018（[V460]）抄録: "matching, even for non-confounders, can create selection bias"・"matching may harm precision and power"・"limit case-control matching to a few strong well-measured confounders"（病因の研究のオッズ比の議論で、分類の精度ではない）。Ehlers et al. 2025（[V461]・medRxiv・査読前）: 発症の時刻で揃えたデータで学んだモデルは "AUROC values below 0.50"、"overly strict matching criteria may significantly impair predictive performance"（訓練の側の揃えで、評価の側ではない）。本研究への批判として立つのは「揃えすぎて手前の違いを消したのではないか」で、温度は PLAUSIBLE BUT UNPROVEN（本研究は揃えた比べで学習していない・揃えない比べにも上がりが無かった）。限界か考察で 1 文受ける。
6. **次に読むべき論文は？** Rothman・Wacholder et al. 1992 の overmatching（一次未確認）。Wong et al. 2021（外部検証の AUC 0.63・開発側の値は抄録に無い）。

### カード 7: 群と時間の構造を無視すると誤差を過小評価する **[検証済 3-0]** [V462] [V463] [V464] [V98] [V102]

1. **どんなもの？** 交差検証と再標本で、群（人）と時間の構造を扱う研究。
2. **先行研究と比べてどこがすごい？** Roberts et al. 2017（[V462]）抄録: "these structures are regularly ignored, resulting in serious underestimation of predictive error"。Field & Welsh 2007（[V464]）抄録: "the cluster bootstrap gives consistent estimates under both the transformation and the random-effect model"。
3. **技術や手法の肝はどこ？** Kaufman et al. 2012（[V463]）はリークを定義し、[V102] がそれを科学の再現の問題に広げた。[V98] は記録単位の交差検証が人単位より精度を大きく見せることを示した（既登録）。
4. **どうやって有効だと検証した？** [V462] は総説とシミュレーション、[V464] は理論。
5. **議論はあるか？** 本研究にとっての意味: 書き手の再標本（クラスタのブートストラップ）と、同じ母集団の書き手の取り置きの根拠。抄録だけだが、主張は各論文の要旨そのもので、本研究の使い方（書き手を単位にする理由）と合う。時間のリーク（推定器の係数を作文で決め、CS1 の取り置きで学習しない）は手順の側で避けている。
6. **次に読むべき論文は？** Obuchowski 1997（クラスタのある ROC の分散・doi:10.2307/2533958・書誌だけ）。

---

## 否決リスト

- **「出来事に近い窓だけを使うと性能が大きく見える」を数値で示した先行がある** → 0-3。探した範囲で 0 件。[V458] は診断の研究の対照群の取り方、[V461] は訓練の揃えで向きも逆。外枠の考察で「先行が示した」と書かない。
- **[V461] は、揃えた評価の同等が揃えすぎの産物だと示す** → 0-3。[V461] は揃えたデータで学習したモデルを元のデータで評価した研究で、評価の揃え方の研究ではない。査読前でもある。批判の可能性（カード 6 の 5）としてだけ受ける。
- **Watwin の 42% は別のデータに持ち出しても保たれる** → 0-3。[V431] の別のデータで r < 0.3。
- **Wong et al. 2021 は開発側の報告との差で、評価の時点の偏りを示す** → 1-2。開発側の AUC は抄録に無く、全文を読んでいない。登録しなかった。

## 本ラウンドのやり残し

- 全文を読んでいない近い文献: [V448]（窓単位の HMM・ScienceDirect が 403）・[V439]（Koli Calling 2026）・[V432]（EQ を複数の文脈で）・[V438]（演習中の未完了・SMU に OA）。草稿で 1 文を超えて使うなら全文を読む。
- Alamargot et al. 2007（休止の前後の並列処理・未読・未登録）。柱 2 の並列の説を厚くするなら読む。
- 位置（語・文・トークンの境界）で停滞と対照が偏っていないか（カード 3 の 5）は、本研究のデータで確かめていない。限界に書くか、記述の計算をするかは研究者が決める。
- AUC に TOST を当てた例・クラスタのある AUC の区間の最近の方法・overmatching の一次（Rothman・Wacholder 1992）は探していない。
- [V434] の表の数値（宿題の点の R² が誤りの指標より高い）はメインが照合していない。
