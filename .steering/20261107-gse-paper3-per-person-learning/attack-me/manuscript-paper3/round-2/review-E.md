# review-E（manuscript round 2・UMUAI 担当編集者）

判定: 直してから回す（軽い改訂。移すこととまとめることで足りる）。fatal なし。読んだもの: main.tex 全文・context-A・carryover-E・mensh.txt。references.bib は grep だけ。補足は読んでいない。

## 0. 引き継ぎの判定
| round 1 の指摘 | 判定 | 位置と逐語 |
|---|---|---|
| 要旨が規程の上限を超える | 解消 | 要旨 250 語。規程 "Please provide an abstract of 150 to 250 words."。この先 1 語でも足せば超える |
| 新規性を「既存の部品の当てはめ」と自己規定 | 解消 | main.tex:48「Our contribution is a finding about sequence models of keystroke behaviour」「we do not claim the parts as new」 |
| 合成検査の方法が本文に無く結果が埋もれる | 解消 | 3.5（143–144）・4.4（232–233）。見出しが結論の形 |
| 意義が nats/symbol の単位から出てこない | 一部 | 270「For a designer deciding whether to model each person, the first number argues for per-person models and the second gives little reason to」。0.19 nats がなぜ支持する大きさかは未説明。限界 289「downstream benefit and cost for adaptation were not measured」。著者の選択として受け入れる |
| 中心の記号列が本文だけでは分からない | 解消 | 3.2（97） |
| minor: 但し書きの繰り返しほか | 一部 | 3.4（141）で地位を 1 度定義・推奨 (4) 替わった（280）・宣言（306）。改訂で足した部分で但し書きの繰り返しが増えた |
| nit: 表と図・作業用の注記 | 一部 | Table 1 のキャプションは「Panels and evaluation symbols.」のまま。e 表記は残る（未決 7） |

## 1. 接地
1. Aims & Scope "provides an interdisciplinary forum for the dissemination of novel and significant original research results about interactive computer systems that can adapt themselves to their users, and on the design, use, and evaluation of user models for adaptation." / "methods for the design and evaluation of user models and adaptive systems"
2. 規程 "Please provide an abstract of 150 to 250 words." / "Please provide 4 to 6 keywords" / "All original research must include a data availability statement."
3. Mensh Rule 1 "Focus on a single message; papers that simultaneously focus on multiple contributions tend to be less convincing about each and are therefore less memorable." / Table 1 "Readers cannot give 1-sentence summary."
4. Mensh Rule 4 "Only the central idea of the paper should be touched upon multiple times. Otherwise, each subject should be covered in only one place in order to minimize the number of subject changes."
5. Mensh Rule 7 "The results section needs to convince the reader that the central claim is supported by data and logic." / "the paragraph ends with a sentence that answers the question." / Rule 8 "explains how the results have filled the gap ... provides caveats to the interpretation, and describes how the paper advances the field" / Rule 2 "Define technical terms clearly because readers can become frustrated when they encounter a word that they don't understand."

## 2. 1 文の要約
「打鍵の記号列の sequence model では、同じ構造の共有モデルと比べたときの per-person の利得（最大 0.19 nats/symbol）は、本人の 1 次 Markov 連鎖とも比べ、構造と縮小を他人で選ぶ強い比較にすると 2 桁以上小さくなる（約 5×10⁻⁴）。だから、人ごとにモデルを持つかを決める研究や設計者は、両方の基準と比べ、検出の下限を報告すべきだ。」迷った点: 題名（"what remains of the gain"）と要旨の後半は「残り」に重心を置くが、その残りは本文自身が「neither shows nor rules out」と書く量。中心が「利得が縮むこと」か「残りの大きさ」かで一瞬迷う。

## 3. 指摘
- [major] 改訂で足した「残り」の頑健性の材料が、検出の下限より 20 倍小さい量に本文の大きな部分を使い、中心の発見を薄めている
  - 位置: 233「the smallest level detected in at least eight of ten seeds is $10^{-2}$ at both $k$」・235 見出し「The remainder stays positive when choice and report use different writers and when both models are smoothed alike」・242「we do not read the values at the lighter smoothing as the size of a per-person gain」・244「we do not read a direction from it」・281「whether it measures the effect of smoothing was not evaluated, so we do not recommend it」・3.6（146–150）・Table 3（246–265）・Table 2 の prior-mode の 2 列・3.3「Prior mode (diagnostic)」（108）
  - なぜ: 4.4 で 1e-2 未満は確実には検出できないと示した直後に、4.5 と Table 3 で約 5e-4 の量の符号の頑健性を詳しく扱い、結論は「大きさは読まない」「向きは読まない」。4.5 の最後の段落は推奨しない診断に割かれる。「なぜこれを聞かされたか」が分からない。4.4 の「No negative-control median reached the real remainder, but ... the two are not compared」（233）は論理の要が 1 文に詰め込まれている。Mensh Rule 7・Rule 3 "This structure reduces the chance that the reader will wonder 'Why was I told that?'"
  - 解消: (a) prior mode の診断（3.3 の段落・Table 2 の 2 列・4.5 の最後の段落・限界の該当文）を補足へ。(b) 4.5 の冒頭か末尾に、この検査が中心の主張の何を守るのかを 1 文（例「縮みは選びの楽観や共有モデルの平滑の片寄りの産物ではない」）。(c) Table 3 を Fixed・Split・Both refitted の 3 列にし、Only shared refitted は 1 文で済ませて補足へ。(d) 題名・要旨で中心は「利得が 2 桁以上縮むこと」で、残りは決められない量だと先に書く。
  - 自信: 中
- [major] 同じ但し書き・限定が 5〜7 回繰り返され、限界の節が結果の言い直しになっている
  - 位置: 「neither shows nor rules out」34・48・274・293・303 の 5 回。「planted differences below 1e-2 ... not reliably detected」34・48・232–233・270・274・293・303 の 7 か所。「its size depends on (that) smoothing」34・48・242・270・274・294・303。post hoc の経緯 141・149・242・248・292・294 の 6 回。「returns only part ... 3 to 40%」233・293。合成 CS1 の τ = 10^6 233・295。陰性対照の並び 233・295。k = 12・15 の二分の負 238・295。2 つの目的の τ 112・200・204。限界 724 語・10 項目で考察 713 語より長い。限界で初めて出る結果 291「a per-writer decomposition of the remainder did not separate a planted difference from none」・293「A difference planted in 5 of 17 synthetic writers was not detected in the panel median.」
  - なぜ: 4,451 語から 6,204 語へ増えた分の多くは但し書きの反復。Mensh Rule 4 "each subject should be covered in only one place"
  - 解消: 各但し書きを 1 か所に（検出の下限は 4.4 と考察、平滑の依存は 4.5、post hoc は 3.4 で定義して以後は目印）。要旨・序論・結論は 1 回の短い言及。限界は結果で言ったことを繰り返さず番号で指す形へ半分に。限界で初めて出る結果は結果の節か補足へ。
  - 自信: 高
- [minor] 最初の 2 頁が後ろの節で定義される語に頼っている
  - 位置: 要旨 34「the gain at a fixed smoothing of the shared model」「when both models are refitted with a lighter smoothing chosen on other people (a post hoc check)」・序論 48「when choice and report are split between writers and when both models are smoothed alike」。序論の最後の段落は約 300 語
  - なぜ: base smoothing とは何か、なぜ固定が問題かは 3.3・3.6 まで分からない。Mensh Rule 2・Rule 6 "The last paragraph of the introduction ... compactly summarizes the results"
  - 解消: 要旨と序論では平滑・分割の限定を 1 句（例 "robust to two checks of the choice and the smoothing"）に。序論の最後の段落は「発見 → 設計者への意味 → 限定 1 文」に。
  - 自信: 中
- [minor]「a typical study」の比較だという言い方に根拠が示されていない
  - 位置: 156「We first checked the comparison a typical study makes」・272「What is new here is that ... the weak comparison is one a typical study would choose」
  - 解消: その比較をした先行研究を引く。引けないなら「a natural comparison」などへ弱める。
  - 自信: 中
- [minor] 本文に置かなくてよい方法の細部
  - 位置: 112 の同点の扱い「Ties go to the earlier candidate in an order from the shared model itself through decreasing $\tau$ and ...」・150 の格子「$\{0.01, 0.03, 0.1, 0.3, 0.5, 1, 2\}$」・238「At $k=12$ and 15 the lower 2.5\% point of the split values is negative ... (not prespecified)」・167 の連鎖の平滑の再選択の段落。Mensh Rule 9 "the methods section is read least of all. Budget accordingly."
  - 解消: 補足へ移し、本文には結論の 1 文だけ。
  - 自信: 中
- [minor] 推奨の適用範囲が狭く、UMUAI の読者全体への意義が見えにくい
  - 位置: 276「for overlapping-window symbolizations like ours, we recommend what this study evaluated」・163「The finding of this section therefore holds for overlapping, smoothed symbols」
  - 解消: 考察の最後に、どの性質の記号列（連続する記号の依存が強いもの）なら本人の連鎖を基準に加えるべきかの一般化の条件を 1 段落。確かめた範囲と分ける。Mensh Rule 8
  - 自信: 中
- [nit] Table 1 のキャプションが結論の形でない・e 表記・S6 の欠番
  - 位置: 81「Panels and evaluation symbols.」・Table 2・3 の「$+4.8$e$-4$」・context-A「S6 は本文から参照されていない」
  - 解消: Table 1 の 1 文目を CS1 の休止の割合（0.72）を言う文に。e 表記を揃える。補足の番号を振り直す。
  - 自信: 高

## 4. 判定
直してから回す（軽い改訂）。1 中心の発見ははっきりし、最初の 2 頁から 1 文で言える。範囲と形式も満たす。2 ただし改訂で足した「残り」の頑健性の材料と prior mode の診断が、検出の下限より小さい量の記述に本文を使い、但し書きの反復（5〜7 回）と結果を言い直す限界（724 語）が中心を埋もれさせている。3 prior mode の診断・細部・限界の繰り返しを補足へ移し、各但し書きを 1 か所にまとめ、4.5 が中心の主張に何を足すかを 1 文で書けば、そのまま査読に回せる。

## 5. 読めなかった範囲と注入の疑い
references.bib は grep だけ。補足の印のファイルは読んでいない。投稿先の一次は context-A の抜粋だけ。注入の疑い: なし。
