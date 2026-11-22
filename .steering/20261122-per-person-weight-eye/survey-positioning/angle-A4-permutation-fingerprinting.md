# angle A4: 入れ替えの帰無と「指紋」の研究（主に Q3）

調査日: 2026-11-23。読んだ範囲は全件「抄録のみ」（Europe PMC REST の抄録を逐語で取得。PMC・bioRxiv の本文は reCAPTCHA と 429 で開けず、本文は未読）。DOI は Europe PMC の登録値で、doi.org を自分で開いては確かめていない（「Europe PMC で確認」と書く）。

## 照合の結果（docs/references.md）

main と origin/docs/gse-positioning-release-matching の両方で、Finn / Horien / Amico / Ojala / Gratton / Combrisson / Wang(Caffo) / connectome を grep して 0 件（Winkler は別人の P86 のみ）。以下 8 件はすべて未登録。

## 1. Wang ら 2021（入れ替えの帰無そのものの批判・最重要）

- 書誌: Wang Z, Sair H, Crainiceanu C, Lindquist M, Landman BA, Resnick S, Vogelstein JT, Caffo B. On statistical tests of functional connectome fingerprinting. Canadian Journal of Statistics, 2021（誌の年・DOI 10.1002/cjs.11591 は検索結果の Zendy・英国図書館の記載による。巻号頁は未確認）。プレプリント bioRxiv 2018, doi:10.1101/443556（Europe PMC で確認）。
- 読んだ範囲: 抄録のみ（本文は未読）。
- 引用:
  - "we investigate the statistical tests of matching based on exchangeability assumption in the fingerprinting analysis. We show that a nearly universal Poisson(1) approximation applies for different matching schemes."
  - "the test is overly sensitive to uninteresting directions in the alternative hypothesis, such as clustering due to familial status or demographics."
- N と設計: HCP（長い技術的反復スキャン・一卵性/二卵性双生児・きょうだい）と BLSA（通常長の縦断）の 2 つの安静時 fMRI。
- Q3 への効き: 近いが重要な反証側。「名札の入れ替え帰無は、交換可能性が崩れる対立仮説（家族・属性によるクラスタ）に過敏で、本人性以外の構造でも棄却される」。こちらの B の名札入れ替え帰無にそのまま当てはまる論点（書き手のクラスタ＝同じ課題・同じ集団・同じ機器・同じ文書の下位集団）。CoAuthor/CS1 の書き手が課題・トピック・セッション条件でクラスタするなら、入れ替えの棄却は「安定した本人差」の証拠にならない。
- 注意: Poisson(1) の結果は「1 対 1 の照合の正解数」の帰無で、こちらの AUC の平均とは量が違う。同じ形で当てはまるとは言えない。
- 登録: なし。

## 2. Horien ら 2018（データ量と動きが同定の率を決める・反証側）

- 書誌: Horien C, Noble S, Finn ES, Shen X, Scheinost D, Constable RT. Considering factors affecting the connectome-based identification process: Comment on Waller et al. NeuroImage, 2018, pp.172-175. doi:10.1016/j.neuroimage.2017.12.045（Europe PMC で確認）。
- 読んだ範囲: 抄録のみ。
- 引用:
  - "the amount of data collected per subject and in-scanner motion are the predominant factors influencing identification rates, not the spatiotemporal resolution of the acquisition."
  - "We show scan length and motion affect identification, whereas the imaging protocol does not affect these rates."
- N と設計: HCP を記録の長さと動きの関数で再解析し、CoRR データでマルチバンドと非マルチバンドを比較。
- Q3 への効き: 支持と反証の両面。同定の率や自己の近さはデータ量（こちらでは書き手ごとの A・B の記号数、遷移表の疎さ）に強く依存する。書き手ごとのデータ量の差が AUC の差になりうる。入れ替えの帰無は書き手を入れ替えるだけでデータ量を条件づけないので、データ量の違いは帰無で消えない。書き手ごとの記号数の下限そろえ（または打ち切りで揃える）を較正で入れる根拠になる。
- 登録: なし。

## 3. Horien ら 2019（間隔を変えた安定性・Q3 の「時間の漂い」側）

- 書誌: Horien C, Shen X, Scheinost D, Constable RT. The individual functional connectome is unique and stable over months to years. NeuroImage 189, 2019, pp.676-687. doi:10.1016/j.neuroimage.2019.02.002（Europe PMC で確認）。
- 読んだ範囲: 抄録のみ。
- 引用:
  - "individual differences of the functional connectome are stable across 3 months to 1-2 years (and even detectable at above-chance levels across 3 years)."
  - "We conduct analyses demonstrating that these results are not driven by head motion."
- N と設計: 年齢の幅が広い 4 つの安静時 fMRI データセット（N は未確認）。
- Q3 への効き: 近いが違う。間隔が数か月〜数年でも同定が成り立つことを示すが、間隔の関数として率を同一デザインで描いたものではない（検索でも「同一デザインで日・週・月を比べた研究は見つからなかった」）。つまり「A と B の間を空けたセルを作って漂いと安定を分ける」は、少なくとも見つけた範囲では先例が薄い。先例は「間隔を変えた別データセット」を並べる形まで。
- 登録: なし。

## 4. Gratton ら 2018（安定した個人差と日ごとの変動の分解・Q3 の分離の先例）

- 書誌: Gratton C, Laumann TO, Nielsen AN, Greene DJ, Gordon EM, Gilmore AW, Nelson SM, Coalson RS, Snyder AZ, Schlaggar BL, Dosenbach NUF, Petersen SE. Functional Brain Networks Are Dominated by Stable Group and Individual Factors, Not Cognitive or Daily Variation. Neuron 98(2), 2018, pp.439-452.e5. doi:10.1016/j.neuron.2018.03.035（Europe PMC で確認。巻号は未確認）。
- 読んだ範囲: 抄録のみ。
- 引用:
  - "functional networks are dominated by common organizational principles and stable individual features, with substantially more modest contributions from task-state and day-to-day variability."
- N と設計: 高密度に繰り返し測った 9 人（被験者・セッション・課題の間の変動の大きさと分布を分解）。
- Q3 への効き: 支持（形が近い）。共通の構造・安定した個人差・セッション/課題由来の変動を分けて見積もる枠組みで、「共有の表に向けて縮める → 本人の安定した成分」「A と B の間のセル → 日ごとの漂い」の分け方の概念的な先例になる。ただし N=9 で、分解は分散成分ではなく相関の構造の比較。
- 登録: なし。

## 5. Finn ら 2015（指紋の原型・入れ替え検定の由来）

- 書誌: Finn ES, Shen X, Scheinost D, Rosenberg MD, Huang J, Chun MM, Papademetris X, Constable RT. Functional connectome fingerprinting: identifying individuals using patterns of brain connectivity. Nature Neuroscience 18, 2015, pp.1664-1671. doi:10.1038/nn.4135（Europe PMC で確認）。
- 読んだ範囲: 抄録のみ。入れ替えの詳細（Wang 批判の二次情報では、126 回の同定の試行が独立でないため 1,000 回の入れ替えの検定）は検索要約による二次情報で、原文の手法は未確認。
- 引用: "functional connectivity profiles act as a 'fingerprint' that can accurately identify subjects from a large group. Identification was successful across scan sessions and even between task and rest conditions"
- N と設計: HCP の約 120 人規模（正確な数は未確認）。同定は「1 回目の記録の 1 人を、2 回目の全員の中から相関で最も近い人に当てる」型。
- Q3 への効き: 形が最も近い先例だが、量は「同定の率」で、こちらの「書き手ごとの AUC の平均」とは違う。AUC の側は量が連続で、1 位の当たり外れを使わない。この違いを位置づけに書ける。
- 登録: なし。

## 6. Amico & Goñi 2018（differential identifiability）

- 書誌: Amico E, Goñi J. The quest for identifiability in human functional connectomes. Scientific Reports 8, 8254, 2018. doi:10.1038/s41598-018-25089-1（Europe PMC で確認）。プレプリント arXiv:1707.02365。
- 読んだ範囲: 抄録のみ（検索要約では「run length」「motion」を検討とあるが、本文は未読）。
- 引用: "the individual fingerprint of a human functional connectome can be maximized from a reconstruction procedure based on group-wise decomposition in a finite number of brain connectivity modes."
- N と設計: HCP の約 100 人の無関係な被験者（検索要約より・未確認）。
- Q3 への効き: 近いが違う。identifiability 指標（自己の類似 − 他人の類似の差）の定義は、こちらの「本人の A は他人の A より本人の B に近いか」と同形だが、この論文の主眼は指標を最大化する再構成で、入れ替えの帰無の妥当性ではない。群の分解で個人差を残す点は「共有の表に向けて縮める」と方向が逆（共有成分の除去か、共有への縮みか）。注意して比べる価値あり。
- 登録: なし。

## 7. Ojala & Garriga 2010（分類器の性能の入れ替え検定）

- 書誌: Ojala M, Garriga GC. Permutation Tests for Studying Classifier Performance. Journal of Machine Learning Research 11(62), 2010, pp.1833-1863. https://www.jmlr.org/papers/v11/ojala10a.html（WebFetch で開いて確認）。
- 読んだ範囲: JMLR のページの抄録（本文は未読）。
- 引用: "We explore the framework of permutation-based p-values for assessing the performance of classifiers."（抄録の第 1 文。WebFetch の要約が示した逐語）
- N と設計: 実データと合成データでの比較。2 つの検定: 名札の入れ替え（クラス構造を見つけたか）と、クラス内の特徴の入れ替え（特徴間の依存を使っているか）。
- Q3 への効き: 支持（方法論の原典）。B の名札の入れ替えは第 1 の検定にあたる。第 2 の型（クラス内で特徴を入れ替える）は、こちらでは「遷移の表の行や記号の順序を入れ替えて、順序の情報を使っているか」の帰無の候補になりうる（頻度だけで同定できるかを分ける。記号の出現率だけで AUC が説明される反証を切る）。ただし抄録のみのため、「入れ替えが崩れる条件」の議論は未確認。
- 登録: なし。

## 8. Combrisson & Jerbi 2015（理論上の偶然水準・小標本）

- 書誌: Combrisson E, Jerbi K. Exceeding chance level by chance: The caveat of theoretical chance levels in brain signal classification and statistical assessment of decoding accuracy. Journal of Neuroscience Methods 250, 2015, pp.126-136. doi:10.1016/j.jneumeth.2015.01.010（Europe PMC で確認。巻は未確認）。
- 読んだ範囲: 抄録のみ。
- 引用: "we demonstrate how applying signal classification to Gaussian random signals can yield decoding accuracies of up to 70% or higher in two-class decoding with small sample sets."
- N と設計: ガウス乱数でのシミュレーション（標本数・クラス数・交差検証・分類器を操作）。
- Q3 への効き: 近いが違う。理論上の偶然水準（AUC=0.5）を使わず入れ替えで経験的に帰無を作る根拠になる。こちらは入れ替えの帰無を使うので、むしろ支持。ただし時系列の自己相関（隣り合う窓が 29/30 秒を共有）で入れ替えの帰無自体が崩れるかは、この論文では扱っていない。

## 見つからなかったもの（0 件の検索）

- 同定の率を、同じ日・日をまたぐ・月をまたぐの間隔で同一デザイン内に並べて測った指紋の研究: Europe PMC の抄録検索と WebSearch（"test-retest interval identification accuracy days weeks months" 系）で 0 件。見つかったのは別データセットを並べたもの（Horien 2019）、乳児の within-session と between-session の比較（検索要約のみ。論文の同定は未確認）、短い間隔と 1 か月の比較（2025 年の Hangzhou 研究・要約のみ・未確認）。
- 「入れ替えの帰無の下で、書き手ごとのデータ量・クラスタを条件づけて検定した」指紋の研究: Wang ら以外は 0 件（未読の本文に推奨があるかもしれない）。
- 打鍵・書字の指紋の領域は担当外のため調べていない。

## 位置づけへの含意（要約・断定はしない）

1. 入れ替えの帰無は指紋の領域の標準だが、Wang ら（抄録）は「交換可能性が弱い帰無であり、家族・属性のクラスタに過敏」と指摘している。これは A4 の核心で、こちらの帰無にも同じ穴があるかを較正（クラスタを持つ合成の生成）で見る価値がある。
2. 同定の量は記録の長さと外乱に強く依存する（Horien 2018）。書き手ごとのデータ量をそろえるか、データ量を入れ替えの層にする設計が要る。
3. 間隔を空けたセルで「漂い」と「安定」を分けること自体は、概念として Gratton 2018 に近いが、打鍵のリズムの表で同じ分け方をした先例は、この angle の検索では見つからなかった。「見つからなかった」であって「無い」ではない。
4. 本文を読めていないため、1 と 2 の細部（Wang の推奨・Horien の打ち切りの設計）は、メインが一次で確かめてから登録する必要がある。
