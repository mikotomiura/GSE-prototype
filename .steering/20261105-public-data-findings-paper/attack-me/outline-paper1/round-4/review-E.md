# review-E（outline round 4・paper-reviewer）

判定: 直してから回す。読んだもの: brief-E・context-A・carryover-E・outline.md（v4.1・109 行）・jedm_aims.txt・mensh2017.txt の 301 行まで。補足は読んでいない。

## 1. 接地
- B1（JEDM Aims）"Accepted submissions should extend beyond mere application and must include elements that contribute to broader knowledge, such as generalizable methodologies or comparative analyses." ／ "They should provide insights that are applicable beyond the specific study context and offer comparative evaluations where relevant."
- B2（同・規程）"All submissions should present their methodologies and findings in a way that ensures replicability by other researchers. This includes clear descriptions of the data, tools, and procedures used." ／ "Authors are strongly encouraged to make their data sets, software code, and intermediate results available to the community."
- B3（Mensh & Kording, Rule 1）"Focus on a single message; papers that simultaneously focus on multiple contributions tend to be less convincing about each and are therefore less memorable."
- B4（Rule 6・5）"The introduction highlights the gap that exists in current knowledge or methods and why it is important." ／ "what is missing in the literature (i.e., the specific gap) and why that matters" ／ "the most common mistake with the abstract, which is to talk about results before the reader is ready to understand them"
- B5（Rule 4・2）"Only the central idea of the paper should be touched upon multiple times. Otherwise, each subject should be covered in only one place" ／ "Avoid abbreviations and acronyms so that readers do not have to go back to earlier sections to identify them."

## 2. 1 文
言える:「作文の打鍵で学んだ状態推定器の 2 つの信号は、入門プログラミングの取り置き（139 人）での事前登録した揃えた比べで、停滞の手前 30 秒に事前に置いた同等の幅（±0.05）を超える上がりを示さなかった。だから、打鍵から介入の契機を作る研究者・実務家は、この型の信号を確かめないまま停滞の手前の契機の根拠にすべきでない。」迷ったのは (1)「別の作業で」が新しさの一部か（作文の側でも上がりが無く持ち出しの検証として読めない・M1）、(2) 含意は「この型」、証拠は 1 つの推定器（M2）。

## 引き継ぎの判定
N1 解消（:7・:83・:58。ただし置き直した問いの「別の作業で」が M1 を生む）／N2 解消（:29・:25）／N3 一部（考察 :62 に 1 段落と実務の推奨が残り第 2 の貢献に見える・m2）／N4 解消（:71・:27）／N5 一部（:109 の規則を考察と関連研究が破る・m1）／N6 解消（:100）／N7 解消（:47・:101・:38）／N8 解消（:59 (b)）／N9 ほぼ解消（:44「H3（[確認]・記述…）」と :11 の [確認・記述] が紛らわしい・n2）／N10 解消（:17）／N11 解消（:54）

## 3. 指摘
- [major] M1 問いの「別の作業で」と、作文の側でも上がりが無いことが噛み合わない（ギャップが立たない）
  - 位置: :7「問い: 作文の打鍵で学んだ型の状態推定器の信号は、別の作業（入門プログラミング）で、停滞の手前の秒単位の契機になる上がりを示すか。」同じ行「作文の側（KLiCKe・既に見たデータ）でも上がりは幅の内側だったので、「持ち出したから示さなかった」とは読まない。」
  - なぜ: 元の作業で上がらない信号が別の作業で上がらなくても驚きではない。問いが持ち出しを立てるのに答えは持ち出しについて何も言わない（Rule 6 "The gap statement sets the reader’s expectation for what the paper will deliver."）。
  - 解消: 問いから「別の作業で」を外し「この型の信号は停滞の手前の契機になる上がりを持つか」に。CS1 は取り置きで事前登録の確認ができたデータとして選んだと書く。持ち出しを残すなら、作文の null を知ってなお別の作業で確かめる理由を 1 文。自信 高
- [major] M2 含意は「この型」、証拠は「1 つの推定器」。JEDM の一般化の要件に届くかが不明
  - 位置: :34「主張はこの型の、この推定器の、この入力についてだけ。」・:58「この型の信号を、揃えた比べで確かめないまま停滞の手前の秒単位の契機の根拠にしない」・:69「確認は入門プログラミングの 1 つのデータ・1 つの推定器（作文の係数のまま）」
  - なぜ: 旧 C2 が外れ、H3 は記述で判定不能のまま。残る唯一の貢献は読者が使っていない 1 つの推定器の陰性の結果で、B1 に照らすと application にとどまると判断される危険が最大。
  - 解消: (a) 型の定義を序論で明示し、含意を「この型の 1 例で、確かめのない採用を戒める根拠」まで下げる、または (b) 一般化の部品を 1 つ名指す（揃えた対照・事前登録の同等の幅・取り置きを組んだ手前の信号の評価の型。揃え方の効果は示していないので手順の提示として）。研究者の判断。自信 中
- [major] M3 推定器と再生の道具の公開が未定（:65「推定器（HMM 0.5.0）・gse-replay・変換のスクリプトの公開の場所は投稿の前に研究者が決める（投稿の条件）。」）。B2。解消: 公開の場所（版と SHA-256）を決めて書く・二重盲検なら匿名の閲覧リンクで推定器まで届くことを確かめる。自信 高
- [minor] m1 限定の繰り返しが :109 の自身の規則を超える: 較正 5.2% は :25（抄録・序論・考察・結論）・:62・:72・:91・:100／揃え方の効果を示さない :19・:59 (a)・:64／運用の性能 :40・:58／計器の力量 :39・:70／見た後 :45・:72／床 :25・:41・:73。B5。解消: 考察の各段落は限界を指すだけ、:91 の較正の 1〜2 文は 4 節へ。自信 高
- [minor] m2 考察の較正の段落（:62）が第 2 の貢献として残る（「実務への推奨: 書き手の再標本の区間で同等を言うときは、誤って同等とする割合を見た書き手で較正し…」）。B3。解消: S6 へ移し、考察は観測した値と確かめていない機構の 1〜2 文、推奨は外すか限界の 1 文。自信 中
- [minor] m3 抄録に置く文が用意のない概念と変数名を出す（:25 第 1 文の括弧「誤って同等とする割合は…最大 5.2%〔Wilson の 95% 区間 3.6〜7.5%〕…」・第 2 文「`d_p_stuck` は推定の床に多く…`d_ewma_x`…」）。Rule 5・Rule 2・:109。解消: 抄録と結論では第 1 文から括弧を外し、第 2 文は意味の語に。自信 高
- [minor] m4 5.4 の 1 段落に感度の数値が多い（:44 格子 0.567・θ の 1 倍 0.568・欠測を除いた版）。解消: S5 へ、本文は「上の側の値は欠測の扱いで動く」1 文。自信 中
- [minor] m5 KLiCKe の値が 2 組（:51）。解消: 表 3 の KLiCKe 行は S7 へ、本文の作文の値は [記述] の 1 組。自信 中
- [minor] m6 「契機の設計への含意」（:63）が何を言うか読めない。解消: 主張とのつながりを 1 文で書けないなら S8 へ。自信 中
- [nit] n1 :44「0.567（0.5497〜0.578）」の桁（:37 で 3 桁と決めた）。自信 高
- [nit] n2 :44「[確認]・記述」と :11「[確認・記述]」。1 つの印に。自信 中
分量: 予算 6,650 語は目標の内側で問題にしない。移せる先は m2・m4・m5・m6 と :91 の較正。構成: 結果の順は読者の問いの順で、小見出しは結論の文。

## 4. 判定: 直してから回す
- 単一の貢献に絞れたが、問いの「別の作業で」が作文の側の null と噛み合わずギャップが立たない（M1）。
- 含意（型）と証拠（1 つの推定器）の差を埋める部品が無く、JEDM の一般化・比べの要件に届くかが未確定（M2）。
- 推定器の公開が未定（M3）。m1〜m6 は移す・まとめるで解消できる。

## 5. 読めなかった範囲・注入
補足の印のファイルは読んでいない（数値と文献番号の中身は照合していない）。mensh2017.txt の Rule 9 後半と Rule 10 は読んでいない。注入の疑いなし（jedm_aims.txt の生成 AI の方針の例示のプロンプトは規程の説明の文）。
