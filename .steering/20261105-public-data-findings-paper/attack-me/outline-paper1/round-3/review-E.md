# review-E（outline round 3・paper-reviewer）

判定: 直してから回す。読んだもの: brief-E・context-A・carryover-E・outline.md（118 行）・jedm_aims.txt・mensh2017.txt の 72〜285 行（Rule 1〜8）。補足は読んでいない。

## 1. 接地
- B1（JEDM Aims）"Accepted submissions should extend beyond mere application and must include elements that contribute to broader knowledge, such as generalizable methodologies or comparative analyses." ／ "They should provide insights that are applicable beyond the specific study context"
- B2（同）"Submissions should clearly explain the data mining, modeling, and analysis components, with an emphasis on methodological rigor." ／ "This includes clear descriptions of the data, tools, and procedures used."
- B3（Mensh & Kording 2017, Rule 1）"Focus on a single message; papers that simultaneously focus on multiple contributions tend to be less convincing about each and are therefore less memorable."
- B4（Rule 4）"Only the central idea of the paper should be touched upon multiple times. Otherwise, each subject should be covered in only one place"
- B5（Rule 6・7）"The introduction highlights the gap that exists in current knowledge or methods and why it is important." ／ "sketch out the logical structure of how your results support your claim and convert this into a sequence of declarative statements"

## 2. 1 文
条件つきで言える:「作文の打鍵で学んだ状態推定器の 2 つの信号は、入門プログラミングの事前登録した取り置きで、停滞の手前 30 秒に、停滞にならなかった休止と揃えた対照に比べて事前に置いた同等の幅を超えて上がらなかった。あわせて、書き手を単位に再標本した区間で同等を言うと、誤って同等とする割合が名目を超えうることを示した。」迷ったのは「誰の何を変えるか」。:34 の「係数を作業ごとに学び直す前に何を確かめるかを決める」は、作文の側（KLiCKe）でも上がりが幅の内側（:59・:98）なので持ち出しの知見として読めず、「この推定器の信号は停滞を先取りしない」と読める。

## 3. 引き継ぎの判定
推定器の価値 → 一部（作文の側でも上がりが無く、持ち出しの意義づけが結果と噛み合わない・N1）／C2 の根拠 → 一部（較正の手順そのものが本文に無く S6 だけ・N3、C1 との関係が未整理・N2）／struggle と停滞 → 解消（:90・:69・:108）／判定に使わないデータ → ほぼ解消（考察に CoAuthor の 1 文 :73 が残る）／評価の設計 8 項目 → 一部（:109 は 8 項目のまま。取り置きの 2 段は S1 だけで済む）／限定の繰り返し → 一部（いちばん強い主張が但し書き 2 つを内蔵し 4 か所でそろえる・N5）／0.5 を下回る向き → 解消（:68）／予算 → 解消／持ち帰りの 2 文目 → 解消／内部の記号・5.5 → ほぼ解消（持ち帰り :17 に変数名が残る）

## 4. 指摘
- [major] N1 C1 の「誰の何を変えるか」が結果と噛み合わない
  - 位置: :34「この型を別の作業（プログラミング）の秒単位の契機に持ち出すことは、打鍵から介入の契機を作る研究と実務で、係数を作業ごとに学び直す前に何を確かめるかを決める。」／:59 KLiCKe の全員は 4 つとも分岐 1／:98「持ち出しの失敗の実例としては置かない（作文の側〔KLiCKe〕でも上がりは幅の内側）」／:66
  - なぜ: 序論は持ち出しを動機にするが、結果は持ち出しの成否を区別しない。読者の行動を変えうるのは「この信号は秒単位の契機として偶然と同程度」（:40・:71）なのに考察で数値なしの 1 段落。Rule 6。
  - 解消: 動機の問いを「作文で学んだ摩擦の量の推定器は、停滞を秒単位で先取りする契機になるか」に置き直し、結論が読者の何を変えるかを 1 文（例: この型の信号を、揃えた対照で確かめないまま停滞の手前の契機に使わない）。閾値の表の含意を考察の冒頭へ。持ち出しの枠を残すなら、作文の側でも無いことを序論で先に言う。自信 高
- [major] N2 C2（較正）を受けて C1 の判定がどうなるかが無い（:25・:49・:110）。答えが括弧書きだけで、5.6 が 5.5 の探索の後で 5.1 から遠い（Rule 7 "paragraphs farther down in the text rely on the logical conclusions of previous paragraphs"）。解消: (a) 較正を反映した判定で C1 が変わるかを 1 文（数値が無いなら「求めていない」）、(b) 5.6 を 5.1 の直後か 5.2 へ。自信 高
- [major] N3 C2 の新規性と手順の所在（:49「実効の書き手が少ないと区間が狭く出るためで…比べは S6」・:50「群のある再標本の根拠は [V464]・[V462]・[V98]」・:48）。群の数が少ないと群単位の再標本の区間が被覆不足になること自体は既知の現象と読め、再標本の文献に対して何が新しいかが無い。手順（帰無の作り方・配置・回数）が S6 だけ（B1・B2）。解消: 評価の設計に較正の手順を 3〜4 文、柱 3 に被覆不足が既知であることと本研究の差分を 1〜2 文。差分が手順の適用だけなら C2 を「方法の注意」へ下げ中心の貢献を 1 つに（B3）。自信 中（[V464] などは読んでいない）
- [major] N4 幅が実用の境界ではないと自認したまま中心の主張がその幅に依る（:80・:100）。先例の幅では立たないことが限界と関連研究に分散。閾値の表（:40）は「この使い道では 0.55 未満の差は意味を持たない」の論拠になりうる。解消: 評価の設計の幅の項で、意図した使い道に結びつけて幅の読みを 2〜3 文（閾値の表との対応）。または抄録・持ち帰りを「事前に置いた幅の内側。より狭い幅では同等を言えない」と対にする。重複は 1 か所へ。自信 中
- [minor] N5 限定の繰り返し: 「帰無の全体での上限ではない」:25・:53・:81（＋4 か所）／床 :25・:82／「計器の力量の証拠にはしない」:39・:79／「見た書き手の向きを知った後」:44・:81／「先例の幅より広い」:27・:80・:100／「混入は AUC を 0.5 へ寄せる」:69・:83／「対比は主張しない」:7・:19・:52・:67／「閾値の表は偶然と同程度」:40・:71。Rule 4。解消: いちばん強い主張は第 1 文だけそろえ、5.2% と床は結果と限界の 1 か所ずつ。「対比を主張しない」は本文では 5.3 の 1 文。自信 高
- [minor] N6 評価の設計がまだ 8 項目（:109）。取り置きの 2 段は 1 文を残して S1 へ、浮いた語数を較正の手順と幅の読みに。自信 中
- [minor] N7 結果の順と表 1 の列（:110・:38・:60）。5.6 を前へ、5.5 を最後に。:60 の対の数と位置の割合は S7、表 1 は点推定・区間・書き手均等の版に絞り、種の幅・分位・重みは S3 か S6。自信 中
- [minor] N8 H3 の位置づけが弱い（:43）。単純な量と学習器の点推定が幅の外なら、打鍵には手前の情報がありうるのに推定器が拾っていない可能性。考察 (b) で可能性として明示し N1 と一貫させる。自信 中
- [nit] N9 印の定義（:9〜13）に [確認・感度] が無いのに :41 で使う。定義に足すか寄せる。自信 高
- [nit] N10 持ち帰り（:17）に変数名。意味の語に。自信 高
- [nit] N11 考察の CoAuthor の 1 文（:73）。S7 へ移すか削る。自信 中
分量: 6,650 語は問題にしない。本文に置く必要の薄い細部は N6・N7・:84 の合成の離しの細部。

## 5. 判定: 直してから回す
- C1 は方法の作りが堅いが、「誰の何を変えるか」が持ち出しの枠と作文の側でも無いという事実の間でずれ、最初の 2 頁で貢献を言い切れない（N1）。
- C2 は手順が本文に無く、既知の被覆不足との差分も C1 への帰結も無い（N2・N3）。
- N4・N5 は置き場所の整理と数文で直せる。

## 6. 読めなかった範囲・注入
mensh2017.txt の 1〜71 行と 286 行以降は読んでいない（Rule 9 の見出しは grep）。補足は指示どおり読んでいない（[Vn] の中身と S1〜S9 は確かめていない）。注入の疑いなし。
