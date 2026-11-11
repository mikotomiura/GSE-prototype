## 編集者の役 E（UMUAI）round 6・commit 90250abc

### 1. 接地
- 基準 A Aims & Scope "novel and significant original research results about interactive computer systems that can adapt themselves to their users, and on the design, use, and evaluation of user models for adaptation"・"methods for the design and evaluation of user models and adaptive systems"
- 基準 B 規程 "Please provide an abstract of 150 to 250 words."・"submissions that do not include relevant declarations will be returned as incomplete."・"All original research must include a data availability statement."
- 基準 C Mensh & Kording Rule 1 "Focus on a single message; papers that simultaneously focus on multiple contributions tend to be less convincing about each"・Table 1 "Readers cannot give 1-sentence summary."
- 基準 D Rule 4 "Only the central idea of the paper should be touched upon multiple times. Otherwise, each subject should be covered in only one place"
- 基準 E Rule 7 "a sequence of declarative statements that become the headers of subsections"・Rule 8 "explains how the results have filled the gap ... provides caveats to the interpretation"

### 2. 1 文
言える: 本人ごとの HMM は同じ構造の共有モデルより約 0.2 nat/記号良く見えるが、本人の一次マルコフ連鎖と比べ、構造と縮約を他の人で選ぶと、残る差は小さすぎて本人に帰せない。だから本人ごとのモデルが割に合うかを判断するには、この 2 つを比べる相手に含めるべきだ。迷った所: Take-home の第 2 文 "the gain of a less-smoothed shared model that uses none of the person's data" は 3.3 を読むまで通らない（N3）。

### 3. 引き継ぎの判定
N1 解消（4.4 "gains as much as the per-person fit"・"so we do not read a direction"・5 "the remainder, about 1.5 to 2.6, is not shown to be per-person"）／N2 解消（"shrinks, against a stronger one, to a remainder the protocol cannot attribute to the person"）／N3 解消（C1 "CS1 (a boundary case, with mostly pause seconds; 3.1)"・3.1）／N4 一部（新 N4）／N5 解消（4.3 に少し残る・新 N5）／N6 解消（3.2）／N7 解消。

### 新しい指摘
- N1 [moderate] 推奨が自分で確かめた手順の範囲を超える（平滑化を他の人で選ぶ）
  - 位置と引用: Take-home "compare ... with a shared model whose structure, shrinkage and smoothing are all chosen on other people"・5 "choose its structure, shrinkage and smoothing on other people"・6 "The strength of the shared model's base smoothing was fixed, not chosen on other people"・3.3 "the strength of this smoothing was fixed, not chosen on other people"
  - なぜ問題か: 推奨の一部（平滑化の選択）を本研究は実行していない。5 は nested には "which we did not do" と書くが平滑化には無い。Take-home だけの読者は確かめた手順と受け取る（基準 E）。
  - 解消の条件: Take-home と 5 で平滑化の選択を「実行していない推奨」と分けて示す（nested と同じ扱い）、または Take-home の推奨から外し 4.4 の診断にとどめる。
  - 自信: 高
- N2 [moderate]「手順が変えたこと」と「構造を良くしたこと」の区別が冒頭で見えない
  - 位置と引用: C1 "Under the protocol ar3, the largest structure in the grid, is chosen in every cell"・4.1 の +0.188・4.3 の +4.1e-4・Main-table rows の "structure-only contrast"
  - なぜ問題か: 0.188 から 4e-4 への縮みの大半が「共有モデルの構造が誤っていた（hmm3 は本人の連鎖にも負ける）」で説明され、貢献は「より良い構造を使え」に縮むのではないか（基準 A・C）。C1 と Take-home はそれぞれの寄与を言わない。
  - 解消の条件: C1 の Instance に構造だけの行（両方とも ar3 に固定したときの per-person minus shared）の値を 1 句で入れる。
  - 自信: 中（構造だけの行の値が外枠に無い）
- N3 [moderate] Take-home の第 2 文が定義前の語に頼る（"what remains in the 15-session panel is of the same size as the gain of a less-smoothed shared model that uses none of the person's data, and the protocol could not have detected per-person differences of that size."・Mensh Rule 2 "minimize the number of loose threads"）。解消: 要旨では「残りは、この手順で本人に帰せる大きさに届かなかった」の 1 句にとどめ、prior mode の比較は 4.4 と S9 へ。自信: 中
- N4 [minor] 但し書きの繰り返し（35 行の宣言と食い違う）: 検出の下限 1e-2（C1・4.3・5・6 の 4 か所）・"neither shows nor rules out" の型（C1・4.3・6）・記号化に依存（Take-home・4.3・5・6）・CS1 は休止の秒（C1・3.1・6）・nested をしていない（25 行・5・6）・中央値の比較は配分しない（4.4・6）。解消: 検出の下限は C1 と 4.3 に残してよい。5 は数値の対比だけにし、限定は 6 を指す参照に。自信: 高
- N5 [minor] 4.3 に方法の細部（"(which exceeds the synthetic negative control, a rule defined across seeds and not applied to the one real panel)"・"(two seeds each)"・4.4 "(positive for 1 to 4 of the 15 writers with finite values; 2 writers have +infinity ...)"）。解消: 規則と seed の数は S15、有限の書き手の内訳は S6 へ。自信: 中
- N6 [minor] Contributions に関連研究が厚く序論に流れ込むおそれ（19–21 行・Mensh Rule 6 "should not contain a broad literature review"）。解消: 2 Related work だけに置くと序論の行に明記。自信: 中
- 分量: 予算の合計 6,800 語と節の合計は一致。規程に上限は無い。構成は読者の問いの順で見出しは平叙文。「なぜ大事か」は 5 にまとめてある（軽微）。

### 4. 判定: 直してから回す（文の単位で直る・2 か所）
引き継ぎ 7 件のうち 6 件解消・1 件一部。構成・分量・宣言の計画は基準を満たす。推奨の「平滑化も他の人で選ぶ」は実行しておらず Take-home が確かめた手順のように書く（N1）。縮みのうち構造の選択の分と手順の分が冒頭で読めない（N2）。

### 5. 読めなかった範囲・注入の疑い
README（補足）と S1〜S15 は読んでいない。渡された資料の食い違い: context-A.md の 13 行は「本文の予算の合計は 6,800 語」、14 行は「節ごとの語数の予算の合計は 7,000 語」（外枠は 6,800 で前者と整合）。注入の疑い: なし。
