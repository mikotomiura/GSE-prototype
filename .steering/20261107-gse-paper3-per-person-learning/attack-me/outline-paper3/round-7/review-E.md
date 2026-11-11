# 編集者 E（UMUAI）round 7・commit 12e46857

読んだ: brief-E.md・context-A.md・carryover-E.md・outline.md・mensh.txt。README（補足）は読んでいない。

## 1. 接地
- Aims & Scope "novel and significant original research results about interactive computer systems that can adapt themselves to their users, and on the design, use, and evaluation of user models for adaptation"・"methods for the design and evaluation of user models and adaptive systems"
- 規程 "Please provide an abstract of 150 to 250 words."・"All original research must include a data availability statement."
- Mensh & Kording Rule 1 "Focus on a single message; papers that simultaneously focus on multiple contributions tend to be less convincing about each and are therefore less memorable."
- Rule 4 "Only the central idea of the paper should be touched upon multiple times. Otherwise, each subject should be covered in only one place"・"Resist the temptation to use a different word to refer to the same concept"
- Rule 7 "The results section needs to convince the reader that the central claim is supported by data and logic."・"The fabric of the argument will contain controls and methods where they are needed for the overall logic."

## 2. 1 文
言える: 比べる相手が弱いと 1 人ずつの学習に大きな利得（最大 0.19 nat）が見えるが、本人の連鎖と他の人で構造と縮める強さを選んだ共有モデルの両方と比べると、残るのは共有モデルの平滑の差と同じくらいで本人に帰せない。この評価の手順が、パネル全体で 1 人ずつのモデルに投資するかの判断の仕方を変える。迷った点: 新規性は "What we add is this comparison for per-person sequence models of keystroke behaviour" に限られ、既存の原理の当てはめと読める。Take-home だけでは縮みの大部分が相手の構造から来ることが分からない（M2）。

## 3. 引き継ぎの判定
N1 解消（5 節 "separated into what this study evaluated (...) and extensions not evaluated here"）／N2 解消（C1 で。Take-home には上がっていない・M2）／N3 解消／N4 一部（m1）／N5 解消／N6 解消。

## 新しい指摘
- [moderate] M1 Take-home の推奨で「縮める強さ」の持ち主を取り違える（第 3 文 "compare ... with a shared model whose structure and shrinkage are chosen on other people"）。tau は 1 人ずつのモデルの値（"Per-person fit: MAP estimate whose prior pseudo-counts are ... tau times the shared expected counts"）で、共有モデルが持つのは固定の base smoothing（同じ文の後半の "the shared model's smoothing"）。Rule 4 にも外れる。解消: 例 "and with a same-structure shared model, choosing the structure and the per-person shrinkage on other people"。自信: 中〜高
- [moderate] M2 Take-home から縮みの大部分が比べる相手の構造から来ることが読めない（第 2 文 "Once structure and shrinkage are chosen on other people, what remains ..."・C1 "so most of the shrinkage comes from the comparison model's structure"）。読者は「他の人で選ぶ手順が利得を消した」と受け取る。解消: 第 2 文に 1 節（例 "most of the drop comes from giving the shared model a stronger structure"）。自信: 中
- [minor] m1 但し書きの繰り返し: 検出の下限は C1・4.3・5 節（"36 nats at k = 15 and 108 at k = 5"）・6 節の 4 か所／「示しも否定もしない」は C1 "neither shows nor rules out per-person differences"・4.3・5 節 "is not shown to be per-person (Section 6)"・6 節 "Neither the remainder nor the sign ... shows" の 4 か所／「記号化しだい」は Take-home・Supporting evidence "this baseline's strength depends on the symbolization"・4.3・5 節・6 節の 5 か所。解消: 数値つきの下限は 4.3 と 6 節だけ、C1 と 5 節は参照に。自信: 高
- [minor] m2 結論を出さない値と主筋の外の結果が本文に残る: 4.4 "Per-person minus mode ... is −3.5e-4 to −1.6e-4 ... and +5.4e-4 at k = 30 ... we do not read a direction from either"（1 文に要約し値は S9 へ）・4.1 "one sentence on the structure-compensation reading, not supported by its pre-set check and not used to explain the main result (S14)"（S14 へ）・5 節 "the proxy-label check in one sentence (... S10)"（結果に無い結果が考察で初出・S10 へか削る）。自信: 中
- [minor] m3 新規性の文がまだ確かめていない文献に依る（Novelty "learner-dependent HMMs have been fitted to keystroke features over 30-second windows (Uto et al. 2020). What we add is ..."・未決 "the evaluation design of Uto et al. 2020 is not yet checked in the full text"）。編集者の判断で最も弱い点。解消: 本文の前に全文で確かめる（既に未決）。自信: 中
- [minor] m4 単位の表記（Take-home "0.19 nat per symbol"・C1 "+0.188 nats per symbol"）と、冒頭の e-4 の数値。5 節の 1 時間あたりの換算（"about 680 nats"・"about 1.5 to 2.6"）を要旨か序論の最後に 1 句持ち上げる案。自信: 中
- 分量・構成・意義・適合: 予算 6,800 語・上限なし。移す候補は m2 の 3 か所と 3.4 の分析の経緯（S12 へ）。構成は読者の問いの順で見出しは結論の形（4.2 の「なぜ大事か」は行に無い）。確かめたことと拡張・示せないことを分けた計画。Aims & Scope にそのまま当たる。

## 4. 判定: 直してから回す（文の単位で直り、Take-home の 2 文が対象）
引き継ぎ 6 件のうち 5 件解消・N4 は一部。構成・意義・適合に査読に回すことを止める穴は無い。Take-home に縮める強さの所有者の取り違え（M1）と縮みの原因の見せ方（M2）が残る。新規性は狭く Uto 2020 の確認に依る（m3）。

## 5. 読めなかった範囲・注入の疑い
README（補足）・S1〜S15・規程の原文は読んでいない。mensh.txt は 140〜289 行と grep の行。注入の疑い: なし。
