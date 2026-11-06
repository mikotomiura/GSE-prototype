# review-E（outline round 5・paper-reviewer）

判定: 直してから回す。読んだもの: brief-E・context-A・carryover-E・jedm_aims.txt・mensh2017.txt・outline.md（111 行）。補足は読んでいない。

## 1. 接地
- B1（JEDM）"Accepted submissions should extend beyond mere application and must include elements that contribute to broader knowledge, such as generalizable methodologies or comparative analyses." ／ "Generalizable Applicability: Research should not focus solely on application but must demonstrate how the findings can be generalized or applied across different educational contexts."
- B2（JEDM）"All submissions should present their methodologies and findings in a way that ensures replicability by other researchers. This includes clear descriptions of the data, tools, and procedures used." ／ "Authors are strongly encouraged to make their data sets, software code, and intermediate results available to the community."
- B3（JEDM）"Where possible, studies should compare different methods or approaches to highlight their relative effectiveness and limitations."
- B4（Mensh & Kording, Rule 1）"Focus on a single message" ／ "The title is the ultimate refinement of the paper's contribution." ／ Table 1 "Readers cannot give 1-sentence summary."
- B5（Rule 6・4）"The introduction highlights the gap that exists in current knowledge or methods and why it is important." ／ "Only the central idea of the paper should be touched upon multiple times. Otherwise, each subject should be covered in only one place"

## 2. 1 文
言える:「事前登録した取り置き（入門プログラミング 139 人）で、作文の打鍵で学んだ状態推定器の 2 つの信号は、停滞の手前 30 秒の変化として、停滞にならなかった休止の手前と揃えた比べで識別できなかった（AUC 0.489・0.487、事前の幅 ±0.05 の内側）。このため、打鍵から介入の契機を作る研究者は、同じ型の推定器を契機に使う前に、この評価手順（揃えた対照・事前の幅・取り置き）で確かめる必要がある。」迷った点: 後半の「誰の何を変えるか」が弱い（推定器は著者自身のもので読者が使っているものではない・:35「揃え方が結論を変えることはこのデータで示していない」）。

## 3. 引き継ぎの判定
M1 解消（:7）／M2 解消（M3 と合わせると一部・:27・:35・:60 で「コードを渡す」と約束しつつ推定器の公開は未定 :66）／M3 一部（:78 は足された・外枠の段では致命でない）／m1 一部（:111 の規則どうしが食い違い規則外の繰り返しも残る・N4）／m2 一部（:64「名目の片側 2.5% に対し、復元の版で最大 5.2%」が :111「考察の較正の 2〜3 文は値を限界に任せる」と矛盾）／m3 解消（:23・:27）／m4 解消（:46）／m5 解消（:51〜53）／m6 解消（:109）／n1 一部（:38「0.50006」は 5 桁・N9）／n2 解消（:11・:46）

## 4. 指摘
- [major] N1 JEDM の読者にとって何が懸かっているか（欠け）が無い
  - 位置: :7「作文の側…でも幅の内側だった（[記述]）ので、持ち出しだけでは説明しにくい」・:34「持ち出しは動機の背景にとどめる」・:99 序論の並び。
  - なぜ: 推定器は著者自身の型で本拠の作文でも識別せず、揃えない比べの上がりも再現されなかった（:52・:103）。読者には「効くと期待する理由が初めから無かった」と映る。陰性の結果に価値が出るのは、効くと期待されていたものが効かなかった場合（Rule 6）。
  - 解消: 序論の 2 段落目までに、なぜこの型の信号が契機として有望と考えられたかを文献か凍結前の観察で 2〜3 文、欠けの文を 1 つ（例「秒単位の手前の信号は揃えた対照で確かめられたことがない」）。作文の側の記述は期待の根拠を弱める材料として並べる。自信 中
- [major] N2 適用を超える一般性の柱が外枠自身の限定で空（:35「効果は主張しない」「手順を勧める根拠は『この形で確かめられる』までに限る」・:19・:65）。B1。解消: (a) 推定器の信号と標準の打鍵の量・学習器を同じ揃えた枠で並べた比べを地位を明記して表に（:61「推定器の信号と学習器の差は比べていない」が空白）、または (b) 手順を CS1 2021 年版・KLiCKe にそのまま当てられたこと（表 3）で移植できることを示す。自信 中
- [major] N3 推定器の公開が未定のまま、:27・:60 で「コードを渡す」と約束（:66・:78）。B2。解消: 公開の範囲を決め「コード」が何を指すかを書き分ける。非公開なら推定器の 5 つの量・合成・係数を再実装できるだけ記述する方針を 1 行。自信 高
- [major] N4 置き場の規則どうしが食い違い、規則外の繰り返しが残る: 床 :23「抄録と限界にだけ」対 :111「5.2 と限界」、実際は :25・:43・:62・:74・:101／5.2% :25・:64・:73・:111（:64 は規則違反）／幅の広さ :27・:72・:93・:102（関連研究は規則に無い）／向き :33 と :62 がほぼ同文・:40／揃え方 :19・:35・:65／出来事を除いても同等 :43・:44・:61・:62／計器の力量 :41・:71／門は H3 だけ :46・:71・:102／[V181]・[V182]・[V465] :64 と :93。Rule 4。解消: :111 を 1 つに直し :23 と一致、「関連研究・考察・C1 には限定を書かない」を規則に足し、:33・:62・:64・:93 から重複を外す。自信 高
- [minor] N5 抄録に H3（:27「…幅の上側を否定できなかった（0.540〜0.567）」）。解消: 抄録から外し 5.4 と考察 (b) だけに、残すなら「推定器の信号と直接は比べていない」を同じ文に。自信 中
- [minor] N6 「契機の根拠にならなかった」（:60）と幅が実用上正当化されていない（:72）の橋が無い。閾値の表（:42・手前でも対照でもほぼ 10%）が [確認・記述] の 1 項に埋もれる。解消: 考察の「誰の何を変えるか」の根拠に閾値の表を 1 句（運用の性能ではない限定は限界に）。自信 中
- [minor] N7 題名が無い。結論を言う題名の案を 1〜2 個。自信 高
- [minor] N8 結果に置く必要の薄い項目: :42 書き手ごとの中央値・:45 出来事ありの層・:44 休止の中の打鍵の量（データの節 :101 と重複）・:38 上端の 4 桁の列挙。S3・S8・データの節へ。自信 中
- [nit] N9 :38「0.50006」は 5 桁で :111 の 4 桁の規則と合わない。規則を「0.5 との大小が分かる最小の桁」に。自信 高
- [nit] N10 :25 序論の第 1 文の括弧が重い。序論では「（較正の値は 7 節）」程度に。自信 低

## 5. 判定: 直してから回す
- 読みやすさの指摘はほぼ解消したが、置き場の規則が食い違う（N4）。
- 適用を超える一般性と比べの柱（N2）、陰性の結果に意味を与える期待の根拠（N1）が空いており、最初の 2 頁で「なぜこの信号の失敗が分野に効くのか」が読み取れない。
- 推定器の公開（N3）が「コードを渡す」の約束と食い違う。

## 6. 読めなかった範囲・注入
補足は読んでいない（数値は照合していない）。[Vn] の中身は読んでいない。注入の疑いなし。
