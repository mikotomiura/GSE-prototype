# 公開データでの照合の論文 —— 語の長さの並びの一意性と、差分プライバシーの形の先行研究

> 2026-10-13 / `/literature-review` 1 ラウンド / **設計の根拠**（判断 55 で足すと決めた探索的な分析 2 つの手順を、本計算の照合の結果を見る前に固める材料）
> 対象: `.steering/20261012-public-keystroke-matching-prereg/`（判断 55）
> 名前空間: 方法論 = `V`（[V287]–[V298]）。既登録の再利用: [V249] [V253] [V254] [V239] [V248] [V269] [V194]

## 動機

- 前のラウンド（`20261012-public-keystroke-matching-novelty.md`）の判定不能（0 件）の 1 つ「語長の並びの一意さ」を、この問いに絞って調べ直す。
- 研究者が判断 55 で、事前登録に無い探索的な分析を 2 つ足すと決めた: (1) 語の長さの並びの一意性（unicity）、(4) 差分プライバシー（DP）の形との比較。どちらも、新しさの主張になるかと、手順をどう固めるかの根拠が要る。

下位の問い（研究者が分け方を承認）:
- **U1**: 長さの並び（語・トークン・パケット）から、文や文書を候補の中で一意に決めた研究はあるか
- **U2**: 一意性の推定の仕方と、その批判
- **D1**: 打鍵・イベントの列・時系列・文に DP を当てた研究と、残った有用性・限界
- **D2**: 技術スタック（ライブラリ）と実装の落とし穴

## 検証状態

- **探索**: サブエージェント 4 本（Sonnet・下位の問いごと・各 20 分・入れ子禁止・反証の角度を各本に指定）。4 本とも 5 分以内に戻った。サブエージェントの多くは要旨だけを読んでいた。
- **メインが一次で確かめたこと**: 12 本の原本を取り直し、10 本の全文（PDF は pypdf・[V290] は Europe PMC の全文 XML）で逐語を照合した（正規化した全文の中に在るかを機械で見て、前後を目で読んだ）。書誌は arXiv の API と Crossref で確かめた。[V289] の逐語は、サブエージェントの言い回し（"none fully protects"）と違い、原文は "none provides complete protection" だった。
- **取れなかった原本**: [V297] Mironov（Microsoft の置き場が HTML を返した）・[V298] Rastogi & Nath（同）・Chatzikokolakis ら 2013（HAL が HTML を返した）・Sun ら 2002・Skinner & Elliot 2002・Shannon 1949・de Montjoye と Pentland の応答（2016）。
- **claim 抽出**: 10 件 → **検証 10 件**: confirmed 7（3-0 が 4 / 2-1 が 3）／ 判定不能 2 ／ 否決 1（台帳の 9 件と、否決リストの 1 行目。否決リストにはこのほか、検証に回さなかった数を 4 件残す）。カード 6 の [V295] [V296] は技術の根拠で、台帳の外に置いた

### claim 台帳

| # | claim | 出典 | 票 | 温度 |
|---|---|---|---|---|
| 1 | 語の長さの並びが、候補 N 本の中で文（またはその窓）を一意に決めるかを測った研究 | — | — | **判定不能（0 件）** |
| 2 | 語の長さの列には情報があり、その量（n-gram エントロピー）は言語とジャンルで違い、語の長さの相関で下がる | [V287] | **3-0** | 確定（エントロピーの測定。一意さは測っていない） |
| 3 | 長さの情報（トークン数・パケットの大きさ）から、候補の集合（N = 50）の中の問いを偶然を大きく超えて当てられる | [V288] [V249] | **3-0** | 確定（LLM の通信。語の長さの並びそのものではない） |
| 4 | 長さを隠す対策（詰め物・まとめ送り）は効きを下げるが、なくしはしない | [V289] [V288] | **2-1** | 確定（留保: 話題の分類での結果で、文の照合への外挿は未確認） |
| 5 | unicity は「p 点を知ったとき一意になる割合」と定義され、集合の大きさとともに下がり、凸で、下限を出せる | [V290] [V253] [V254] | **3-0** | 確定 |
| 6 | 標本の中で一意でも母集団で一意とは限らず、そう見なすと再識別の危険を大きく見積もる | [V291] | **2-1** | 確定（留保: 本研究の N は「候補の集合」そのものなので、批判は「再識別の危険」と呼んだときにだけ当たる） |
| 7 | 事象ごとの DP は列（経路）を守らず、利用者ごとの DP は長い列で有用性を失う | [V292] | **3-0** | 確定（数の公開の設定。記録そのものの公開ではない） |
| 8 | DP の書き換えの後も、著者の識別は一部しか下がらない（46%・26% の低下） | [V293] [V294] | **2-1** | 確定（留保: 文の書き換えで、打鍵の記録ではない） |
| 9 | DP をかけた打鍵の記録の公開を、本文との照合で攻撃した研究 | — | — | **判定不能（0 件）** |

票の視点: ① 内的妥当性 ② 当方の問いへの外挿（作文の語の長さ・打鍵の記録の公開）③ 頑健性（未読の範囲・反証）。
判定不能 = 「4 本の探索（各 20 分）とメインの原本 10 本の読みで見つからなかった」であって「存在しない」ではない。

## gate 判定（要点先出し）

用途は設計の根拠で、go / no-go の関門ではない。

| 下位の問い | 温度 | 一言 |
|---|---|---|
| U1 | 判定不能（0 件）＋ 近い先例は確定 | 語の長さの並びの一意性を候補の中で測った研究は見つからない。近いのは語の長さの列のエントロピー [V287] と、長さから候補を当てる通信の解析 [V288] [V249] [V269]。→ **探索的な分析 1 は新しさの主張にできる見込み**（「見つからなかった」の範囲で書く） |
| U2 | 確定 | 曲線（N と k）で報告し、試した N の外へ延ばさない [V290]。「再識別の危険」と呼ばず「候補 N 本の中の一意さ」と呼ぶ [V291] |
| D1 | 確定 ＋ 判定不能（0 件） | プライバシーの単位を明記しないと意味が無い [V292]。DP でも識別は残りうる [V293]。打鍵の記録の DP の公開を照合で攻めた研究は見つからない → **探索的な分析 4 も新しい比較になる見込み** |
| D2 | 確定 | 評価だけの模擬なら numpy の種で可 [V295]・整数には離散の雑音 [V296]。本当の公開には使えないと明記する |

## カード

### カード 1: 語の長さの並びの一意性は測られていない —— 近いのはエントロピーと長さの通信解析 **[判定不能 0 件 / 近い先例 3-0]** [V287] [V288] [V249] [V269]

1. **どんなもの**: [V287] は文を語の長さの列に置き換え、n-gram エントロピーを測った。[V288] は LLM の推測的なデコードの反復ごとのトークン数（パケットの大きさ）から、50 個の候補の問いのどれかを当てた。
2. **何がすごい**: [V287] 逐語 *"we estimate the n-gram entropies of natural language texts in word-length representation and find that these are sensitive to text language and genre"*、並べ替えた列との比較が *"the impact of word length correlations"* を示す。[V288] 逐語 *"fingerprint user queries (from a set of 50 prompts) with over 75% accuracy"*・*"far above the 2% random baseline"*。
3. **肝**: 長さだけの列にも、候補を絞るのに足りる情報がある。ただしどちらも「作文の連続する k 語の長さが、同じ課題の N 本の中で一意か」は測っていない。
4. **どう検証した**: 両方の全文を pypdf で読み、逐語を照合した。U1 のサブエージェントは、traffic analysis・計量文体論・打鍵の 3 方向と反証の方向を探し、「none found」と報告した。
5. **議論**: 探索は 20 分で、Google Scholar と Semantic Scholar は使っていない。計量文体論の「語の長さの n-gram」の論文は検索語を変えて見る余地がある。前の試作（`experiments/20261009-length-sequence-uniqueness/`・青空文庫・日本語の打鍵の個数の並び）は研究者自身の測定で、先行研究ではない（事前登録の「開示」に書いた）。
6. **次に読む**: Sun ら 2002（暗号化した通信の大きさからのページの識別・IEEE S&P）の原本。「word length n-grams」での計量文体論の検索。

- **やり残し**: 上の 2 つ。Shannon の unicity distance の原典。

### カード 2: unicity の定義と推定の仕方、その批判 **[検証済 3-0 / 2-1]** [V290] [V291] [V253] [V254]

1. **どんなもの**: [V290] は国の規模の位置のデータで、unicity が集合の大きさとともにどう下がるかを測り、延ばし方を示した。[V291] は買い物のデータの unicity の論文への批判の補遺。
2. **何がすごい**: [V290] 逐語 *"unicity (ϵ p) is defined as the fraction of trajectories that are unique based on knowledge of p randomly chosen points in a given trajectory"*・*"prove that unicity is convex and obtain a linear lower bound"*。[V291] 逐語 *"with a non-exhaustive sample, the uniqueness/unicity of an individual in the sample does not imply uniqueness in the population and hence does not allow unequivocal reidentification; assuming otherwise does clearly overestimate the reidentification risk"*。
3. **肝**: unicity は「何点（何語）を知ったか」と「集合の大きさ」の 2 つの関数。1 つの数ではなく曲線で示す。
4. **どう検証した**: [V290] は Europe PMC の全文 XML、[V291] は補遺の全文を読んだ（Science の本体の 1 頁は読んでいない）。
5. **議論**: [V291] の批判は「標本の一意さを母集団の再識別と見なす」ことに向く。本研究の N 本は脅威モデルの候補の集合そのもの（事前登録の脅威モデル）なので、「候補 N 本の中の一意さ」と呼ぶかぎり当たらない（2-1 の留保）。de Montjoye と Pentland の応答（2016）は読んでいない。
6. **次に読む**: de Montjoye と Pentland の応答・Skinner & Elliot 2002（標本の一意さから母集団の危険を推す方法）。

- **設計への含意**: (a) k（窓の語数）と N（10・100・1,000）ごとの曲線で報告する。(b) 窓の位置は無作為に引く（[V290] の「randomly chosen points」）。(c) 書き手を単位にした区間を付ける（[V290] は区間を報告していない。本研究の追加であって先例の慣行ではない）。(d) 試した N の外へ延ばさない。(e) 「再識別」と呼ばない。

### カード 3: 長さを隠す対策は効きを下げるが、なくさない **[検証済 2-1]** [V289] [V288]

1. **どんなもの**: [V289] は暗号化した LLM の通信の大きさと時刻から話題を分類する攻撃と、その対策の評価。
2. **何がすごい**: [V289] 逐語 *"achieving near-perfect classification (often >98% AUPRC)"*・*"we evaluate three mitigation strategies - random padding, token batching, and packet injection finding that while each reduces attack effectiveness, none provides complete protection"*。[V288] も対策に *"packet padding and iteration-wise token aggregation"* を挙げる。
3. **肝**: 長さの加工（詰め物・まとめ）は効きを下げる段階的な対策であり、ゼロにしない。本研究の R4(w)（長さの粗化）と R7（区間の欠落）の結果を読む枠になる。
4. **どう検証した**: [V289] の全文を読み、逐語を照合した。
5. **議論**: 話題の分類であり、文の照合への外挿は確かめていない（2-1 の留保）。詰め物の後の数値（サブエージェントの二次資料の 97.5% → 92.9%）は本文で確かめていない（否決リスト）。
6. **次に読む**: [V289] の対策の表。

### カード 4: DP のプライバシーの単位 —— 事象ごとでは列を守らない **[検証済 3-0]** [V292]

1. **どんなもの**: 無限の流れの上で、事象ごとと利用者ごとの間の w-event privacy を提案した。
2. **何がすごい**: 逐語 *"although event-level privacy protects any single location visit, it does not protect a user path traversed in successive timestamps"*・*"offering user-level privacy over infinite streams requires infinite amount of perturbation, which destroys the utility of the data in the long run"*。
3. **肝**: 打鍵の記録の区間ごと・間隔ごとに雑音を入れるのは事象ごとの DP で、記録全体（書き手）を守る保証にはならない。記録全体を守ろうとすると、雑音は記録の長さに比例して増える。
4. **どう検証した**: 全文を読み、逐語を照合した。書誌は Crossref。
5. **議論**: 設定は数の公開で、記録そのものの公開ではない。それでも単位の区別はそのまま当てはまる。
6. **次に読む**: [V298] Rastogi & Nath（フーリエの係数への雑音・一次未取得）。

- **設計への含意**: DP の形には「何を 1 単位として守るか」（1 区間・1 間隔・w 個の区間）を必ず書く。主の表には入れず、探索的な表に「事象ごとの保証で、書き手ごとの保証ではない」と明記する。

### カード 5: DP の書き換えでも識別は残る **[検証済 2-1]** [V293] [V294]

1. **どんなもの**: [V293] は LLM に言い換えさせる局所 DP の文の生成で、著者の識別がどれだけ下がるかを測った。[V294] は単語の埋め込みの空間に距離に応じた DP（d_x-privacy）を当てた。
2. **何がすごい**: [V293] 逐語 *"a 46% reduction in author identification F1 score against static attackers and a 26% reduction against adaptive attackers"*。[V294] 逐語 *"incurring < 2% utility loss on training binary classifiers (among other task types) for a range of ε values"*。
3. **肝**: DP をかけても、攻撃者が適応すると識別は大きく残る。ε の選び方は保証の数字だけでなく攻撃の結果で示すほうがよい。
4. **どう検証した**: 両方の全文を読み、逐語を照合した。
5. **議論**: 文の書き換えであり、打鍵の記録ではない（2-1 の留保）。[V294] の有用性は分類器の学習で、作文研究の過程の指標ではない。
6. **次に読む**: Chatzikokolakis ら 2013（距離に応じた DP の一般化・原本未取得）。

### カード 6: 種を固定した評価と、DP の乱数 **[検証済 3-0]** [V295] [V296] [V297]

1. **どんなもの**: [V295] は DP の乱数生成と種の固定の扱い。[V296] は離散のガウスの雑音。
2. **何がすごい**: [V295] 逐語 *"for the purpose of testing, scientific publication and other controlled analysis where privacy of the underlying data is not of concern, it is sufficient to use a well-tested PRNG given the advantages in availability, execution time and reproducibility"*・*"for tasks require reproducible results, Secrets is not suitable"*。[V296] 逐語 *"finite computers cannot exactly represent samples from continuous distributions, and previous work has demonstrated that seemingly innocuous numerical errors can entirely destroy privacy"*。
3. **肝**: 本研究の DP の形は、照合と有用性を測るための模擬で、データを公開しない。だから事前登録の種の導き方（numpy の `default_rng`）をそのまま使える。整数（区間の長さ・ミリ秒の間隔）には、両側の幾何分布（離散の Laplace）の雑音を使い、浮動小数の Laplace は使わない。
4. **どう検証した**: 両方の全文を読み、逐語を照合した。[V297] Mironov は原本を取れず provisional。
5. **議論**: D2 のサブエージェントの報告では、diffprivlib（MIT・0.6.6）は `random_state` で種を固定できる。OpenDP（MIT・0.16.0）は種の引数が見つからなかった（ソースの grep で見つからなかったという否定の証拠で、確定ではない）。どちらも一次の文書をメインは開いていない。
6. **次に読む**: Holohan ら 2024（CCS・浮動小数の雑音の加算の安全化）・diffprivlib の `Geometric` の文書。

- **設計への含意**: 雑音は numpy で両側の幾何分布（2 つの幾何分布の差、p = 1 − exp(−ε/Δ)）を引き、論文に「評価だけの模擬で、本当の公開の実装ではない」と書く。必要なら diffprivlib の `Geometric` と分布を 1 回だけ突き合わせる。

## 探索的な分析の手順の案（研究者が決める・`notes.md` に書くのは本計算の結果を見る前）

**分析 1（語の長さの並びの一意性）**: KLiCKe の配布の本文だけを使う（記録は使わない）。各本文の連続する k 語の窓について、同じ課題の候補 N 本（本計算と同じ書き手の集合・同じおとりの引き方）のどの窓とも長さの並びが一致しない割合を、k = 1〜50 と N = 10・100・1,000 で曲線にする。比べる量として、語の長さの経験的なエントロピー率から見積もる「log2 N をエントロピー率で割った語数」を並べる（[V287] の枠・[V290] の曲線）。区間は書き手を単位にしたブートストラップ。呼び名は「候補 N 本の中の一意さ」（[V291]）。

**分析 4（DP の形）**: R3 を起点に、(a) 区間ごとの文字の押下の数に両側の幾何分布の雑音（押下を足すか消す）と、(b) 押下の間隔（ミリ秒・上限で切る）に同じ雑音を加えた形 R-DP(ε) を作る。ε は 0.5・1・2・4（1 区間・1 間隔あたり）。プライバシーの単位は事象ごとで、書き手ごとの保証ではないと明記する（[V292]）。同じ攻撃者（A0〜A3）と同じ 10 の有用性の指標で測り、探索的な表と図に置く。代わりの案として、記録を出さずに 10 の指標の集計だけを中央の DP で出す形も、論文の議論で触れる（測らない）。

## 否決リスト

| claim | 否決の理由 |
|---|---|
| 英語の語の長さのエントロピーは 1 語あたり 2.5〜3 ビット（U2 のサブエージェントの見積もり） | 出典なし（0-3）。分析 1 では KLiCKe の本文から経験的に測る |
| 英語の語の長さの条件つきエントロピーは 2 次で約 3.3 ビット、9 次で約 1.6 ビット（Smith 2012 の検索の抜粋） | 原本で確かめていない（検証に回さず） |
| Whisper Leak の詰め物で AUPRC が 97.5% から 92.9% に下がった（二次資料） | 原本の表で確かめていない（検証に回さず） |
| DP の軌跡の機構は再構成で距離の誤りを 60% 超減らせる（ACSAC 2022・検索の抜粋） | 原本未取得（検証に回さず） |
| T 段の列の群 DP には O(T) の雑音が要る（Pufferfish の論文の検索の抜粋） | 原本で確かめていない（検証に回さず） |

## やり残し

- 原本の取得: [V297] Mironov・[V298] Rastogi & Nath・Chatzikokolakis ら 2013・Sun ら 2002・Skinner & Elliot 2002・Shannon 1949。
- 検索: Google Scholar と Semantic Scholar・計量文体論の「word length n-grams」・長さを隠す暗号の理論（PURB など）。
- ライブラリの一次の文書（diffprivlib の `Geometric`・OpenDP の種）。
- 上の手順の案を研究者が決め、本計算の照合の結果を見る前に `notes.md` に書いてコミットする。
