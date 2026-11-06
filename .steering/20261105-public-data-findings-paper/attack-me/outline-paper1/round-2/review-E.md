# review-E（outline round 2・paper-reviewer）

読んだのは依頼文、context-A.md、外枠 outline.md（本文の印。101 行すべて）、carryover-E.md、接地の jedm_aims.txt と mensh2017.txt だけ。補足の印のファイルは読んでいない。

## 1. 接地
- G1（JEDM Focus and Scope）: "Accepted submissions should extend beyond mere application and must include elements that contribute to broader knowledge, such as generalizable methodologies or comparative analyses."
- G2（同）: "Submissions must emphasize the novelty and impact of the research. They should provide insights that are applicable beyond the specific study context and offer comparative evaluations where relevant."
- G3（同）: "Submissions should clearly explain the data mining, modeling, and analysis components, with an emphasis on methodological rigor. Where possible, studies should compare different methods or approaches to highlight their relative effectiveness and limitations."
- G4（Mensh & Kording 2017, Rule 1）: "Focus on a single message; papers that simultaneously focus on multiple contributions tend to be less convincing about each and are therefore less memorable." Table 1 "Readers cannot give 1-sentence summary."
- G5（同 Rule 4 / Rule 3）: "Only the central idea of the paper should be touched upon multiple times. Otherwise, each subject should be covered in only one place" ／ "They do not care about the chronological path by which you reached a result"
- G6（同 Rule 9）: "the methods section is read least of all. Budget accordingly."

## 2. 1 文
何とか言える:「事前登録した確認で、作文で係数を決めた打鍵の推定器の 2 つの信号は、入門プログラミングの停滞の手前 30 秒で、停滞にならなかった休止と揃えて比べると上がりを示さず、同等の幅に収まった。打鍵から秒単位の契機を作る研究者は、手前の上がりを報告する前に、揃えた対照で同等を確かめる手順を持ち帰れる。」
迷った 2 か所: 前半の主語は JEDM の読者が知らない自作の推定器で、なぜ確かめることが大事かが無い（major 1）。後半は C2 の手順が結論を変えることを示せていない（:46）ので推奨としてしか言えない。

## 3. 引き継ぎの判定（round 1 の 10 件）
| round 1 の指摘 | 判定 | 理由 |
|---|---|---|
| [major] 方法が要る理由が無い | 解消 | :7 で枠組みが反転。ただし C2 が G1 の適合を一身に背負う（major 2） |
| [major] 主語が広い | 解消 | :13 |
| [major] EDM の読者の検出器にどう効くか | 一部 | :54 で届く相手が打鍵ベースに狭まった。:75 の援助の要求・wheel spinning の検出器の多くは打鍵ベースでなく、推奨 2 つ（:58）が届く理由が無い |
| [major] 主張に細部と記号 | 解消 | :19 |
| [minor] C3 | 解消 | :57。ただし KLiCKe の数値が 6 つ（minor） |
| [minor] 結果の後半 | 解消 | :93 |
| [minor] 但し書きの繰り返し | 一部 | 4 系統で繰り返し（minor） |
| [minor] なぜ大事か | 一部 | :75 で比べの相手は示したが、H2 分岐 4 で「揃えないと間違う」帰結が無く、可能性の側（:55 (a)）にとどまる |
| [nit] 内部の記号 | 一部 | :101 は ADR・分岐・P0 だけ。`d_p_stuck`・`ewma_x`・H1〜H3・X8・K6 の呼び方が無い。「条件 A」（:38）が外枠の中で未定義 |
| [nit] 小見出し | 一部 | 5.5「登録の外の探索」だけ宣言の文でない |

## 4. 新しい指摘
- [major] 推定器がなぜ確かめる価値を持つのかが序論の設計に無い
  - 位置: :13「作文で係数を決めた打鍵の推定器の 2 つの信号は」／:89「問題 → 問い → いちばん強い主張 → 貢献 2 つ」／:75
  - なぜ: 推定器が発表済みか・使われているか・なぜ CS1 へ持ち出すかが無く、「自作の検出器が別の領域で効かなかった」としか読めない。G2・G1 "mere application"。Mensh Rule 2 "a naïve reader who must first be made to care about the problem"。
  - 解消: 序論の 2 段落目までに、推定器が代表する型（作文の打鍵から学習した状態推定器）と、その型を CS1 へ持ち出すことが読者の何を決めるかを 2〜3 文。言えないなら一般化の根拠が無いことを持ち帰りの側で引き受ける。
  - 自信: 高
- [major] 投稿先との適合は C2 に懸かるが、C2 の根拠が手順の価値を示していない
  - 位置: :44 の (2)「変換の照合の不一致を計算の前に捕まえ」・(3)「H2 が分岐 4 でも書き方が 1 通りに決まった」／:46「揃え方が結論を変えることは示していない」
  - なぜ: 手順の効きを示すのは (1) の較正だけ。(2) は経緯（Rule 3）、(3) は定義から言えるだけ。対比を主張しないので手順の比較評価（G3）も無い。
  - 解消: (a) 根拠を (1) の較正に絞り、名目 2.5% と最大 5.2% の差が書き手の再標本で同等を言う他の研究に何を意味するかを結論の文に。(2)(3) は S1 へ。または (b) C2 を評価の設計の説明に下げ 1 貢献の論文にし、JEDM との適合を何で示すかを研究者が決める。
  - 自信: 中
- [major] 動機の「詰まり」とラベルの「停滞」がずれる
  - 位置: :75「援助の要求の検出・wheel spinning の早期検出・先回りのヒントは EDM の主題」／:68「ラベルは停滞（文字の産出の止まり）で詰まりの判定ではない。CS1 の停滞は実行の待ちを多く含む」／:34「停滞の 47% は休止の中に実行・貼り付け・切り替えを含む（対照は 6%）」
  - なぜ: 序論は struggle 検出で読者を呼ぶが、限界でラベルは詰まりでなく半数近くが実行の待ちと書く。Mensh Table 1 "Readers ask why something matters or what it means"。
  - 解消: 序論で最初から「文字の産出の停滞」を問いの対象と定め、struggle 検出との関係（上位の問いか代理か）を 1〜2 文。47% はデータの節に置き、考察で同等の読みに何を意味するかを 1 文。
  - 自信: 高
- [minor] 判定に使わないデータが本文の 3 つの節にまたがる（:36・:59・:91 の CoAuthor／:35 の K6 の値／:57 の契機の数え上げ）。解消: CoAuthor は S7 とデータの節の 1 文、K6 の値は S3、数え上げの数値は S8 か S7、考察は数値なし 1〜2 文。自信 高
- [minor] 評価の設計 1,200 語が 8 項目を抱える（:92）。H3 と揃えない比べの設計は本文に各 1〜2 文、細部は S4・S5。浮いた語数を序論の手当てへ。自信 中
- [minor] 同じ限定の繰り返し: 「揃え方が結論を変えることは示していない」系 :15・:46・:55・:70／「水準は 0.5 から離れた」系 :13・:30・:64／「最大 5.2%」:19・:44・:58・:66／「1 データ・1 推定器・見た後」系 :25・:38・:64・:66／ROPE :43・:83。解消: :38・:46 の「強さ」は限界への参照、ROPE は関連研究（:83）だけ、:70 の揃えすぎは考察 (a) へ。自信 高
- [minor] 0.5 を下回る向きを解釈しないままにすると問いが残る（:29）。考察で 1〜2 文（幅の内側・向きを問わない登録・KLiCKe は逆向き）。自信 中
- [nit] 予算の数字の食い違い: :52「考察に置くもの（7・700 語）」と :94「6 考察 | 900」、:85「7,000 語」と合計 6,650、節番号 :52「7」・:62「限界（8」と表（考察 6・限界 7）。自信 高
- [nit] 持ち帰りの 2 文目（:13）と限界（:64）の緊張。2 文目を 5.1 に置くか、力量は確かめていないことを添える。自信 低

## 5. 判定: 直してから回す
1. round 1 の major 4 件のうち 3 件は解消。総量も問題ない。
2. 主の主張は読者が知らない自作の推定器の陰性の結果で、序論の struggle とラベルの停滞がずれる（major 1・3）。
3. C2 の根拠のうち手順の効きを示すのは較正だけ（major 2）。序論 2 段落と C2 の絞り込みで査読に回せる水準になる。

## 6. 読めなかった範囲・注入の疑い
読めなかった範囲は無し。補足の印のファイルは指示どおり読んでいない（外枠の数値が出どころと一致するかは確かめていない）。テンプレートの説明の原文は見ていない。注入の疑いは無し。
