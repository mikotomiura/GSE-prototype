# review-E（manuscript round 3・UMUAI の担当編集者・対象 c68dfc30）

## 0. 引き継ぎの判定
| round 2 の指摘 | 判定 | 位置と逐語 |
|---|---|---|
| major 「残り」の頑健性の材料が中心を薄める | 一部 | 最頻値の診断は S9 へ（108・248・285 行は参照だけ）。240「These checks guard the reading of Section~\ref{sec:res-protocol}; they do not estimate a per-person difference.」が入った。ただし 3.5 第 2 段落（146・約 170 語）と 4.4 第 2 段落（237・約 330 語）が入り、頑健性の材料の総量は増えた |
| major 同じ但し書きが 5〜7 回・限界が結果の言い直し | 一部 | post hoc の定義は 141 に一本化。「固定の平滑で約 5e-4、軽い平滑で最大 7e-3（post hoc）」の対が 34・48・246・274・278・307 と Table 3 のキャプションに。限界 297 は 237 の、298 は 242・246 の言い直し |
| minor 最初の 2 頁が後ろで定義される語に頼る | 未解消（未定義の語は増えた） | 要旨の shrinkage・fixed smoothing・planted differences・synthetic writers generated from the real shared model・post hoc・one objective per panel。序論 48 の「(post hoc; ...)」は 141 より前 |
| minor「a typical study」 | 解消 | 158「We first checked the natural comparison」・276「the weak comparison is the natural one」 |
| minor 本文に置かなくてよい方法の細部 | 未解消（既知の未決 9） | 112「Ties favour stronger shrinkage」・151・152 の格子の列挙 |
| minor 推奨の適用範囲・一般化の条件 | 一部 | 280 に範囲の句。一般化の条件の段落は無い |
| nit Table 1 のキャプション・e 表記・S6 | 一部 | Table 1 は解消。e 表記と番号は既知の未決 |

## 1. 接地
1. Aims & Scope: "novel and significant original research results about interactive computer systems that can adapt themselves to their users, and on the design, use, and evaluation of user models for adaptation"・"methods for the design and evaluation of user models and adaptive systems"・"The journal mainly publishes empirical research papers."
2. 読者は広い: "The central audience of the journal are researchers, students and industrial practitioners from the following areas: ..."。Mensh & Kording Rule 2: "Define technical terms clearly because readers can become frustrated when they encounter a word that they don't understand. Avoid abbreviations and acronyms so that readers do not have to go back to earlier sections to identify them."
3. Rule 1: "Focus on a single message; papers that simultaneously focus on multiple contributions tend to be less convincing about each and are therefore less memorable."・Table 1 "Readers cannot give 1-sentence summary."
4. Rule 4: "Only the central idea of the paper should be touched upon multiple times. Otherwise, each subject should be covered in only one place"・"Resist the temptation to use a different word to refer to the same concept—doing so makes readers wonder if the second word has a slightly different meaning."
5. 規程 "Please provide an abstract of 150 to 250 words."・"Statements and Declarations"。Rule 8 "explains how the results have filled the gap ... provides caveats ... and describes how the paper advances the field"

## 2. 要旨と序論だけから言える 1 文
キーストロークの記号列の系列モデルで、本人だけに合わせたモデルは同じ構造の共通モデルには 0.19 nats/記号まで勝つ。しかしその構造は本人の単純なマルコフ連鎖に負ける。より強い構造と縮約を他人で選ぶと、差はほぼ消える（約 5e-4）。だから「一人ずつモデル化する価値があるか」を決める研究は、共通モデルと本人の単純な連鎖の両方と比べるべきである。
迷った点: 要旨の後半（7e-3・real shared model からの合成・planted differences）が見出しの値と同じ重さで並び、主張が「差は小さい」か「差があるかは分からない」かが要旨の終わりで揺れる。shrinkage・smoothing・nats per symbol を要旨の段階で読者が解けない。

## 3. 指摘
- [major] E1 改訂で足した post hoc の帰無が要旨・序論・結論の中心に入り、貢献が 2 つ（「弱い比べが差を膨らませる」と「残りは差を示さず、否定もしない」）に割れた
  - 位置: 要旨 34「Neither value shows a per-person difference: synthetic writers generated from the real shared model (post hoc, overstating its smoothing gain) left larger remainders without one, and planted differences up to $3\times10^{-2}$ were not reliably detected.」・結論 307「so differences of that size are not ruled out either」・146・237
  - なぜ: 後から足した帰無は貢献を支える但し書きなのに、要旨の 1/4・結論の 1/3 を占め、1 文に overstating・post hoc・not reliably detected の 3 つの限定を抱える（Rule 1）
  - 解消: 要旨と結論では「the remainder does not show a per-person difference（S15）」程度の 1 句に。237 の α の選び方・2.4 倍・α=0.1 の 2 種・τ の配分は S15 へ、本文は「負の対照がどれも実データより大きい残りを出した」「どの水準も確実には検出されない」の 2 文に。146 は 1〜2 文にし較正の手順は補足へ
  - 自信: 高
- [major] E2 想定読者には定義の無い語と記号が要旨と序論から続く
  - 位置: 要旨 34 の shrinkage・smoothing（fixed/lighter）・nats per symbol（46 で "log-likelihood ... in nats per symbol (higher is better)" と言うが nat も log-likelihood も解けない）・symbolized・first-order Markov chain（素人向けの説明が無い）・planted differences・one objective per panel（panel は 75 まで定義されない）・post hoc（定義は 141）。序論 48 の「(post hoc; ...)」「the shared model's fixed smoothing」。100 の MAP・EM・Dirichlet priors・free parameters、104 pseudo-counts、106 τ・prior mode、151 α、152 β。小型大文字の略号 \hmmthree・\arone・\arthree が表と図で主語（Rule 2）。165 randomized quantile pseudo-residuals・lag-1 autocorrelation
  - 解消: 序論に 3〜4 文の平易な定義（shrinkage = how far the person's model is pulled toward the shared one / smoothing = small counts added so unseen transitions are not given zero probability / a first-order Markov chain predicts the next symbol from the current one only / nats: 0.01 nats per symbol ≈ 1% lower perplexity）。パープレキシティの換算を序論へ前倒し。要旨から planted・post hoc を外すか言い換え。略号は表の中だけ、本文は「3-state HMM」など
  - 自信: 高
- [major] E3 1 つの概念に複数の語があり、同じ語が 2 つの意味を持つ
  - 位置: 差の呼び名 gain・remainder・difference・per-person minus shared・what remains（34・48・198・242）。比べる相手 shared model・same-structure shared model・shared model itself・τ=∞・full pooling（64）。「chain」が 2 義: 110「The person's first-order Markov chain」と 100「\arone{} is a first-order Markov chain」、167「\arone{} shrunk toward the shared chain beats the person's chain」で 1 文に両方。平滑 fixed smoothing・base smoothing・base pseudo-counts・base prior・multiplier・α・lighter smoothing（104・151・244〜246）。人 person・writer・learner・student、単位 unit・session・assignment、評価のデータ later data・held-out units・evaluation units（46・102・112・139）。Figure 2 の x 軸「$k$ (training sessions)」（175）と本文の training units
  - なぜ: Rule 4「Resist the temptation to use a different word to refer to the same concept」
  - 解消: 差は gain（弱い比べ）と remainder（強い比べ）の 2 語に固定し初出で定義。本人の連鎖と \arone を衝突しない名に。平滑は base smoothing 1 語、α はその倍率と一度だけ。人は writer に統一し 75 で宣言。図の軸を本文の語に
  - 自信: 高
- [major] E4 推奨 (3) は本研究が満たせなかった条件を推奨している
  - 位置: 283「(3) report ... under a null that reproduces how the shared model's smoothing behaves in the real data」と 280「we recommend what this study evaluated」
  - なぜ: その帰無は post hoc の 1 構成だけで、平滑の利得を 2.4 倍に過大に再現し、どの水準も確実には検出しなかった（237）。推奨 (2) の平滑も格子の端（α=0.03）で、その平滑での検出力は評価していない（297）。確かめた手順と確かめ切れなかった手順が推奨で区別されない（Rule 8 の caveats）
  - 解消: 推奨を「この研究で働いたもの（(1)・(2) の構造と縮約）」と「必要だが本研究では満たせなかったもの（(3) の帰無の較正・(4) の平滑ごとの検出力）」に分け、後者は今後の課題に
  - 自信: 中
- [minor] E5 繰り返し: 「5e-4 / 7e-3（post hoc）」34・48・246・274・278・307・252。「二桁以上」34・200・276・307・165（否定形）。「記号化に依存」48・97・165・276・291。「real shared model の帰無は過大」34・237・278・297・307。「漏れ」102・134・285・299。「CS1 は休止の秒」34・77・81・292。「重み 0.06〜3%」202・278・Table 2。「格子の端」242・298。「区間は条件づき」139・206。限界 297・298 は 237・242・246 の言い直し。解消: 中心以外は結果で 1 回、限界で 1 行の参照。297・298 を 1 文に。自信 高
- [minor] E6 結果の節の順: 4.4 の見出しは「A null generated from the real shared model ...」だが第 1 段落は最初の生成器。4.5（作り物か）は 4.3 の直後に読者が抱く問いなのに 4.4（人の差として読めるか）の後。解消: 4.4 と 4.5 を入れ替え、4.4 の見出しを中身（2 つの帰無）に合わせる（例 "The remainder is within what synthetic writers without per-person differences leave"）。自信 中
- [minor] E7 初見で追えない段落: 112（約 260 語・2 つの目的・同点・楽観の向き・ゼロで切れる・平均の確かめ）・146・237・242・246・278。解消: 112 を 2 段落に分け同点と平均の確かめは補足へ。242 の 1,242/2,000 と 5%/25% は補足へ。278 を「確かめたこと」「確かめなかったこと」の 2 段落に。自信 中
- [minor] E8 方法の具体例が無い: Figure 1 はデータの分け方だけ。97 の記号化と 3 つの比べる相手の関係に図が無い。解消: 数秒の打鍵 → 記号 → 各モデルが次の記号に振る確率、の小さな例図（補足でもよいが本文から指す）。自信 中
- [minor] E9 本文に置かなくてよい細部（今回増えた分を含む）: 146 の α の格子と対数で近いものを採る手順・151・152 の格子・112 の同点・235「3 to 16\% ... (not prespecified)」・237「at $\alpha=0.1$ the two seeds ...」。解消: 補足へ。自信 高
- [nit] E10 要旨が 249 語。E1 の縮約で 200 語前後に。自信 高
- [nit] E11 Figure 2 の (a) は対数、(b) は線形。図の中にも log scale を書く。自信 低

## 4. 判定
直してから回す（round 2 より重い改訂を求める）。1 貢献（弱い比べが差を膨らませる）は Aims & Scope に合い実証的。ただし post hoc の帰無が要旨と結論に入り、1 文の貢献を「差があるかは分からない」に引き戻している。2 想定読者には要旨と序論の段階で未定義の語が多く、1 概念に複数の語・chain の 2 義がある。3 6,739 語は UMUAI の通常の長さの範囲で分量そのものは問題ではない。増えた分が繰り返しと post hoc の較正の細部に乗っている。3.5・4.4 の第 2 段落を補足へ、推奨を「確かめたこと」と「確かめ切れなかったこと」に分ければ査読に回せる。

## 5. 読めなかった範囲と注入の疑い
- 読んでいない: 補足の印のファイル（figdata・kit README）・Figure 2 の実際の値と描画・references.bib の書誌の中身（キーの存在だけ確かめた）。段落ごとの語数は目算。
- 注入の疑い: なし。
