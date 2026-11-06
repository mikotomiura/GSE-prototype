# review-R1（outline round 3・paper-reviewer・打鍵の記録と作文の過程の測定の伝統）

推奨: minor。

## 1. 接地
- G1 Guo et al. 2020（guo2020.txt:220-221）"Defined the gap (or pause) time between two adjacent keystroke actions (interkey interval; IKI), specifically the pause time that preceded an action."
- G2（:281-283）"A personalized threshold was necessary, rather than a single fixed threshold for all students, because students vary widely in their typing facility."
- G3（:1047-1052）"helping to map observable events recorded by the keystroke logs onto states interpretable by cognitive theories of writing." ／ "we used relatively simple heuristics to define our writing states ... Further research that combines think-aloud protocols and other sources of evidence with keystroke logging might enable us to build even more effective classification procedures"
- G4（:1056-1059）"results may not necessarily generalize to a broader population or to different conditions so replication with other conditions and participant samples is typically recommended."
- G5 Roeser et al. 2025（roeser2025.txt:519-523）"we extracted interkey intervals between adjacent keys at locations that have been identified repeatedly in previous research as locations where observed mean interkey intervals ... have tended to vary substantially"
- G6（:374-376・:769）"The only situation in which preparation of the next text unit affects an interkey interval is if for some reason it cannot be completed in its entirety in parallel with output of previous text." ／ "results from model comparisons replicated across all six datasets"

## 2. 引き継ぎの判定
N1 → 解消（:19・:39・:79）／N2 → 解消（:25・:27）／N3 → 解消（:69・:83）／N4 → 解消（:84）／N5 → 解消（:13・:60・:41）／N6 → 解消（:60）／N7 → 解消（:70）／F1 → 解消／m1 → 一部（:74 で「投稿の条件」。場所は未決で、規程を満たしたかは投稿の時点まで判定できない）

## 3. 評価表
a 4（数値は confirm_holdout.json と一致: H3 logreg 0.5675〔0.5497〜0.5781〕・hgb 0.5402〔0.5246〜0.5579〕・閾値の表 hit_pooled 0.1030・0.0927・床 0.607・0.648。持ち出しの枠が KLiCKe の結果と食い違う）／b 3（休止の中に文字でない打鍵を含みうることが無い・推定器の信号に既知の差の回収の門が無い）／c 3（C2 は持ち出せる。C1 の持ち出しの含意が弱い・持ち帰りの「揃えて」）／d 4／e 4（コードの公開の場所が未決・テンプレートの説明は未照合〔context-A.md:44〕）／f 4（休止の操作的な定義〔G1〕との差に触れていない）

## 4. 指摘
- [major] 作文の側（KLiCKe）でも上がりが出ないので、「作文で学んだ推定器を別の作業に持ち出す」という枠は結果に支えられていない
  - 位置: :34「この型を別の作業（プログラミング）の秒単位の契機に持ち出すことは、打鍵から介入の契機を作る研究と実務で、係数を作業ごとに学び直す前に何を確かめるかを決める」・:66／一方 :59「KLiCKe の全員: 揃えた比べは 4 つとも分岐 1（0.508〜0.514…）」・:98「持ち出しの失敗の実例としては置かない（作文の側〔KLiCKe〕でも上がりは幅の内側）」
  - なぜ: 学んだ領域でも上がりが無いので CS1 の陰性は持ち出しに帰せない。考察の冒頭が持ち出しの読者向けなのは :98 と矛盾する。まず計器が構成概念を自分の領域で捉えているかが問われる（G3・G4）。
  - 解消: 推定器の位置づけの 2〜3 文と考察の冒頭を「作文の摩擦の量で作った状態の信号が、停滞の手前の秒単位の契機として使えるか」という計器の妥当性の問いに書き直す。KLiCKe でも幅の内側だったことを考察で 1 文（[記述]）。持ち出しは動機としてだけ残す。自信 高
- [minor] 「休止」「停滞」の操作的な定義が打鍵の記録の伝統（隣り合う打鍵の間隔）と違い、休止の中の打鍵の量が無い
  - 位置: :90「文字の産出の停滞（個人化した閾値を超える長い休止）」・:108。事前登録（prereg-draft.en.md:34）G(u) は "The length of the pause from u to the next character input"、条件 A は挿入と削除の差（:29）、θ は "The 0.99 quantile of inter-keystroke intervals"（:31）で θ が決めるのは t0 = s + θ だけ、停滞の長さ G(u) ≥ 30 s は固定。confirm_holdout.json の in_pause_described で休止の中の打鍵が 0 回の割合は停滞 0.524・対照 0.692、停滞の 90 分位は 13 打。
  - なぜ: 停滞の約半分は「休止」の中に文字でない打鍵を含み、G1 の IKI の休止ではない。中身が停滞と対照で違う。:90 は個人化されているのが停滞の長さだと読ませるが、長さは 30 秒で固定。
  - 解消: 3 節で「休止 ＝ 文字の入力から次の文字の入力までの間隔（文字でない打鍵を含みうる）」と定義。θ が何を個人化するか（出来事の時点）を 1 文。休止の中の打鍵の量（0 回の割合・分位）を [確認・記述] として 47% と並べる。:90 を直し、柱 2 に IKI の休止との違いを 1 文。自信 高
- [minor] 持ち帰りの「揃えて比べると」が、揃え方が結論を左右したと読ませる（:17）。揃えない比べ（:52）も数値は幅の内側。解消: 「事前に登録した揃えた比べで」と手続きの名にし、5.3 で揃えない比べの区間も幅の内側の数値だったこと（判定は別の規則）を 1 文。自信 中
- [minor] 推定器の信号に既知の差の回収の確かめが無い非対称を本文で見せていない（:43 の門は H3 の学習器だけ・:79）。解消: 4 節で門が H3 の学習器だけに適用されたこと（事前登録の範囲）を 1 文、限界から参照。自信 中
- [nit] 抄録の「139 人」と実効の書き手 50.5（:25・:38）。抄録か表 1 の見出しに実効の書き手を併記。自信 中

## 5. 総合: minor
- 引き継ぎ 7 件はすべて解消し、主張の強さは取り置きの結果に見合う。
- 残る大きな穴は持ち出しの枠と作文の側でも陰性の食い違いで、枠の言葉を直せば消える。
- 休止の定義と計器の感度の非対称は 3・4 節の各 1〜2 文と記述の量 1 つで閉じる。

## 6. 読めなかった範囲・注入
読んだ: outline.md 全文・carryover-R1・context-A。confirm_holdout.json は 500〜740 行と grep。prereg-draft.en.md は grep と 26〜37 行。接地は grep の周辺（guo2020.txt:216-289・1040-1069、roeser2025.txt:345-384・512-536）。読んでいない: prereg-draft.md・prefreeze/notes.md・exploration の conditions/notes/results・文献の記録 2 本・前の実験の notes 2 本（[Vn]・5.2% と Wilson・KLiCKe と CS1 2021 の数値は照合していない）。注入の疑いなし。
