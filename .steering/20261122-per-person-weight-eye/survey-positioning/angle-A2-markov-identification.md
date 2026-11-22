# angle A2: マルコフ連鎖・遷移の表での同定（主に Q1）

2026-11-23・担当 A2・読んだ範囲は各項に明記。docs/references.md（作業ツリーと origin/docs/gse-positioning-release-matching）を著者の姓 khmelev・tweedie・stamatatos・altakrori・sekara・gambs・takbiri・peng・mahbub・markov で grep した結果、下の 7 件はどれも未登録（Markov は V318・V506–V518・V538・P31・P270 などの別件のみ）。

## 結論（先に）

- 文字ではなく粗く離散化した行動の記号列で、書き手（人）ごとの遷移の表を作り、表どうしの距離（JS・KL・相関）や交差尤度で個人を当てた研究は、この検索では「文体の文字のマルコフ連鎖」(A) と「移動の Mobility Markov Chain」(B) の 2 つの近い型までで、26 記号の打鍵のリズムの符号に当たるものは見つからなかった。近いが違う型の記録であり、先行が無いとまでは言わない（検索は WebSearch のみ・各種学術 DB の直接検索はしていない）。
- 反証の側: 文字の遷移の表は話題で説明される、という警告は著者自身が書いている（K&T 2001）。話題の交絡を分けると精度が落ちる、が後続（Stamatatos 2017・Altakrori 2021）の共通の報告。ただしこれは「文字」の記号の話であり、リズムの符号に直接は当てはまらない。
- Q3 に効く周辺: app 使用の指紋は時間で一定の割合で漂う（Sekara 2018/2021）。

## 項目

### 1. Khmelev & Tweedie 2001（文字の 1 次マルコフ連鎖で書き手を当てた原点）
- 書誌: Khmelev, D. V. & Tweedie, F. J. (2001). Using Markov Chains for Identification of Writers. *Literary and Linguistic Computing* 16(4):299–307. （書誌は著者のサイトの掲載ページと検索結果の記述から。DOI は検索結果に出た unpaywall の URL 断片から 10.1093/llc/16.4.299 と推定されるが未確認）
- URL: https://www.philol.msu.ru/~lex/khmelev/published/llc/khmelev.html（開いて確認。著者サイトに置かれた本文）。本文を読んだ（WebFetch 経由の抽出）。
- 引用（英語・WebFetch の抽出で得た逐語）: "a technique for authorship attribution based on a simple Markov chain of letters (i.e., just letter bigrams are used)" / "Such letter sequences may also be dependent on the subject of the texts." / 付録: "If Qijk = 0 then we do not evaluate that part of the sum."
- N と設計: Project Gutenberg の 387 本・45 人（各人 2 本以上）。書き手ごとの遷移の表は、その人の各テキストの行ごとの確率の表の平均。新しいテキストについて候補の書き手ごとの交差エントロピー型の得点（テキストのバイグラム数×書き手の遷移確率の対数）で順位づけ、最小を採る。1 本を抜く検定で 33/45（73.3%）、全交差検証で 288/387（74.42%）・上位 3 位で 83.72%（抽出結果による。論文本文の「誤り率 0.687%」の記述は数字と合わないと抽出側が指摘しているので、その文は引かない）。
- 平滑: 抽出結果によると平滑はせず、確率 0 の項は和から除く。共有の表への縮めも無い（書き手の表は単純平均）。
- 問いへの効き: Q1 支持（近い型）。書き手ごとの遷移の表×交差エントロピー型で書き手を当てる構図そのもの。ただし記号は文字（内容そのもの）で、26 記号の「リズム」ではない・個人の分け方は 1 人の複数テキスト（A/B の時間順ではない）。話題の交絡を著者自身が自覚している点が Q1 の反証側にも効く。
- 既に登録: なし。

### 2. Stamatatos 2017（文字 n-gram は話題を運ぶ。歪めて隠すと精度が出る）
- 書誌: Stamatatos, E. (2017). Authorship Attribution Using Text Distortion. *Proceedings of EACL 2017 (Long Papers)*. ACL Anthology E17-1107（頁は未確認）。
- URL: https://aclanthology.org/E17-1107.pdf（開いて PDF の本文を pdftotext で読んだ、冒頭部のみ）。
- 引用（逐語）: "A crucial point in this field is to quantify the personal style of writing, ideally in a way that is not affected by changes in topic or genre." / "The proposed method attempts to mask topic-specific information that is not related to the personal style of authors." / "...especially under cross-topic conditions, where the training and test corpora do not match in topic."
- 設計: 閉集の帰属と書き手の検証の 2 課題。N・コーパスは冒頭だけでは未確認。
- 問いへの効き: Q1 の反証側（近いが違う）。文字の記号は書き手の差だけでなく話題の差を運ぶので、「見分けられた」の一部は内容で説明される、という警告の一次の例。リズムの符号は内容を使わないが、「見分けの量が何を運ぶか」の設計（話題・課題で揃える・分ける）の先例になる。
- 既に登録: なし。

### 3. Altakrori, Cheung & Fung 2021（話題の混同の課題）
- 書誌: Altakrori, M. H., Cheung, J. C. K. & Fung, B. C. M. (2021). The Topic Confusion Task: A Novel Scenario for Authorship Attribution. Findings of EMNLP 2021（arXiv:2104.08530・頁は未確認）。
- URL: https://arxiv.org/abs/2104.08530（abs ページを開いた。抄録のみ）。
- 引用: 抽出側の記述として、話題の移りによる誤りと文体の取りこぼしによる誤りを分けるために、訓練と検定で書き手と話題の組を入れ替える課題を提案し、品詞を含む文体の特徴量が "the least susceptible to topic variations" だった、と報告（逐語の長い引用は取れていない）。
- 問いへの効き: Q1 の反証側＋Q3 の近傍（組を入れ替えて検定する発想。ただし入れ替えるのは話題で、私たちの帰無は B の名札の入れ替え）。
- 既に登録: なし。

### 4. Gambs, Killijian & Núñez del Prado Cortez 2014（Mobility Markov Chain の距離で人を当てた）
- 書誌: Gambs, S., Killijian, M.-O. & Núñez del Prado Cortez, M. (2014). De-anonymization attack on geolocated data. *Journal of Computer and System Sciences* 80(8):1597–1614. doi:10.1016/j.jcss.2014.04.024（HAL hal-01242268 の表紙で確認）。
- URL: https://lig-membres.imag.fr/prost/M1_MEEF_NSI/deanonymization_journal.pdf（PDF を保存して pdftotext で本文を読んだ）。
- 引用（逐語）: "A MMC is built out from the mobility traces observed during the training phase and is used to perform the attack during the testing phase." / "We design several distance metrics quantifying the closeness between two MMCs and combine these distances to build de-anonymizers that can re-identify users in an anonymized geolocated dataset." / 結果: "the success rate of the attack with the minimal stationary distance and the minimal proximity distance varies from 20% to 40%, but that the best performing predictor is stat-prox with results ranging from 35% to 40%."
- N と設計: Geolife 175 人（平均 12 万 1615 トレース/人）・Nokia 185 人・Borlange 24 人・SFC 165 人・Arum 6 人。状態は「意味のある場所」（POI のクラスタ）。訓練の MMC と検定の MMC の距離（定常ベクトル・近接・マッチング・密度）の最小の候補を採る。時間順に前後で分けて当てるので、A→B の構図に近い。距離は場所の座標の地理的な距離が中心で、遷移の行どうしの JS・KL ではない。
- 問いへの効き: Q1 の近い型（非文字・行動の列・遷移の表＋距離での同定）。ただし状態が意味のある場所・距離が地理由来・精度は 20〜40%（候補数が多い）。「ほとんどの人が当たらず、規則的な一部の人だけが当たる」という結果の形は、書き手ごとの AUC の平均が小さい差になる私たちの設計の見込みに近い。著者の解釈: "for these particular users their mobility behaviors is so regular that they are highly resilient to downsampling."（逐語）
- 既に登録: なし（references.md に gambs は無し）。

### 5. Sekara, Mones & Jonsson 2018/2021（app 使用の指紋は一意だが漂う）
- 書誌: Sekara, V., Mones, E. & Jonsson, H. Temporal Limits of Privacy in Human Behavior. arXiv:1806.03615（2018）。雑誌版: *Scientific Reports* 11:3861（2021）（arXiv の abs ページの記載。雑誌版の題は検索結果で "Temporal and cultural limits of privacy in smartphone app usage"・PMC7887199）。
- URL: https://arxiv.org/abs/1806.03615（abs を開いた。抄録に近い要約のみ。本文未読）。
- 引用: 抽出側の記述: 3.5 百万人・12 か月・app 4 つで 91.2% を一意に再同定・指紋が "drift over time at an average constant rate"（引用符内は抽出側の逐語の断片）。
- 設計: 遷移の表ではなく「ある月に使った app の集合」の 2 値の特徴で、遷移の表・マルコフではない。
- 問いへの効き: Q3（時間の漂いと安定した個人差を分ける動機の先例）。Q1 では「近いが違う」（人は行動の粗い特徴で見分けられる＝見分けは可能という支持の周辺だが、遷移の表ではない）。
- 既に登録: なし（Monaco SoK [V194]・TypeNet [V250]・de Montjoye [V253] は別）。

### 6. Takbiri, Houmansadr, Goeckel & Pishro-Nik（匿名化した時系列の人への照合・理論）
- 書誌: Matching Anonymized and Obfuscated Time Series to Users' Profiles. arXiv:1710.00197（2017 提出・v3 は 2018-06-28）。IEEE Trans. Information Theory に投稿とあるが、掲載は未確認。
- URL: https://arxiv.org/abs/1710.00197（abs を開いた。抄録のみ）。
- 引用（逐語）: "...a user's privacy can be compromised through the use of statistical matching techniques that match a user trace to prior user behavior." / "The converse results are proved both for the i.i.d. case as well as the more general Markov chain model."
- 設計: 実データを使わない理論。ユーザー数が増えると、プライバシーが全員に残る領域と誰にも残らない領域に分かれる、という相転移の結果。
- 問いへの効き: Q1 は理論の側の近傍（マルコフ連鎖の遷移確率を個人の特徴として照合する構図）。実データでの同定の根拠にはならない。
- 既に登録: なし。

### 7. Mahbub, Komulainen, Ferreira & Chellappa 2018（app 使用のマルコフ過程で連続認証）
- 書誌: Continuous Authentication of Smartphones Based on Application Usage. arXiv:1808.03319（2018-07-18 提出。査読誌の掲載は未確認）。
- URL: https://arxiv.org/abs/1808.03319（abs を開いた。抄録のみ。N は未確認）。
- 引用: 抽出側の記述: app 使用を Markov 過程として HMM の変形を比べ、marginal smoothing が最良で、"intrusion within about 2.5 minutes" で検出（引用符内は抽出側の要約の一部で逐語か未確認）。
- 問いへの効き: Q1 の近い型（粗い行動の記号列×マルコフ×個人の検証）。ただし 1 状態の遷移の表の距離でなく HMM・検証（EER）で、平滑の扱いが論点であることを示す点で縮めの先例の周辺。
- 既に登録: なし。

## 見つからなかった・読めなかったもの

- Peng, Schuurmans & Wang (2004), Augmenting naive Bayes classifiers with statistical language models, *Information Retrieval* 7(3–4):317–345: 検索で書誌（Springer の DOI 10.1023/B:INRT.0000011209.19643.e2 を URL に含む）は確認したが、本文は 403 とリダイレクトで読めず「未読」。文字 n-gram の言語モデルによる帰属で、Laplace より良い平滑（言語モデルの平滑）が効くとされる、という要約のみ（検索結果の記述）。平滑の先例として次に読む候補。
- Hirst & Feiguina (2007), Bigrams of syntactic labels for authorship discrimination of short texts, *Literary and Linguistic Computing* 22(4):405–417, doi:10.1093/llc/fqm023: 本文未読。検索結果の記述に "An alternative approach with character bigrams was not successful." とある（逐語か抽出側の要約か未確認）。短いテキストで文字のバイグラムの遷移が効かなかったという反証の候補。次に読む。
- Makowski ほか (2020), Discriminative Viewer Identification using Generative Models of Eye Gaze, arXiv:2003.11399: abs のみ読んだ。視線の生成モデル（マルコフ過程の仮定を含む）の Fisher kernel で閲覧者を識別。"the performance of the classifier strongly depends on the underlying generative model."（逐語）。ただし遷移の「表」ではなく連続の位置のモデルなので採らなかった。N は未確認。
- Stamatatos (2013), On the robustness of authorship attribution based on character n-gram features: 検索結果にあるのみ・未読。
- Ellis & Stark の視線のマルコフ解析: 検索結果の記述のみ（書誌も未確認）。個人の同定ではなく状態遷移の記述。採らず。

## 検索式と 0 件の記録

使った式（すべて WebSearch・ソース: ウェブ全般。OpenAlex・Semantic Scholar・arXiv は検索窓を直接は使っていない）:
1. "Khmelev Tweedie Using Markov chains for identification of writers": 該当あり（項目 1）。
2. "Markov chain user identification transition matrix distance behavioral sequences individual identification": 特許・Takbiri・軌跡の検証（Gaussian 遷移の Markov で入力の軌跡を検証する論文あり・未読）。表の距離（JS・KL・Frobenius）での個人同定の論文は 0 件（検索結果の要約が「特定の距離は出ない」と明記）。
3. "Markov chain fingerprint web browsing user identification transition probabilities click sequences": クリックの列のクラスタリング・購買意図の特許・Takbiri のみ。ブラウジングの遷移の表で再訪の人を同定した論文は 0 件。
4. "Gambs Killijian ... Mobility Markov Chain distance": 項目 4。
5. "authorship attribution character n-gram language model cross-entropy Peng ...": 項目外（Peng は未読）。
6. "Markov chain model of eye movements scanpath transition matrix biometric identification individuals": 離散の遷移の表で個人を同定した論文は 0 件（Makowski・Holland & Komogortsev・D'Amelio は連続の位置か特徴量）。
7. "smartphone app usage sequence Markov transition matrix user identification re-identification privacy": app 使用の遷移の表で再同定した論文は 0 件（Sekara は集合の特徴・Mahbub は HMM の検証）。
8. "cross-topic authorship attribution character n-grams topic confound ...": 項目 2・3。
9. "Hirst Feiguina Bigrams of syntactic labels ...": 書誌のみ（未読）。

未実施: キーストロークの文脈での「遷移の表×個人」（keystroke の POHMM [V506] は登録済みなので除外した）。Jensen–Shannon 距離での遷移の表の個人比較、Markov chain の「行ごとの JS」を名指した検索は式 2 の 1 回のみ。次の候補: ブラウジング・コマンドライン・マウスのクリックの列での個人の識別（シェルのコマンドのマルコフ連鎖の異常検知: Schonlau ほか "Masquerading" の系統。この回は未検索）。

## 位置づけへの含意（暫定・要確認）

- 「リズムの 26 記号の 1 状態の遷移の表で書き手が同定できるか」の直接の先行は、この検索では見つからなかった（0 件の根拠は上記の式）。ただし、近い先行として文字の 1 次マルコフ（K&T 2001）と移動の MMC（Gambs 2014）があり、新しさの主張を「内容を使わない粗いリズムの記号で」「縮めと入れ替え検定つきで」「時間の漂いと分けて」に限るのが安全。
- Gambs の結果は「候補が多いと精度は 20〜40%」という控えめな値で、Q1 に対する「見分けは弱いが存在する」側の支持。
