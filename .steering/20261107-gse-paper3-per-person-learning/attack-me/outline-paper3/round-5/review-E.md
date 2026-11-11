## 編集者の役 E（UMUAI）round 5 の判定（outline.md commit afc96bfa）

読んだ: brief-E.md・context-A.md・carryover-E.md・mensh.txt・outline.md。README（補足）は読んでいない。

### 1. 接地
- B1 Aims & Scope（context-A.md 19 行）"dissemination of novel and significant original research results about interactive computer systems that can adapt themselves to their users, and on the design, use, and evaluation of user models for adaptation."
- B2 同 "methods for the design and evaluation of user models and adaptive systems"
- B3 Mensh & Kording Rule 1・Table 1 "Focus on a single message; papers that simultaneously focus on multiple contributions tend to be less convincing about each"・"Readers cannot give 1-sentence summary."
- B4 Rule 4 "Only the central idea of the paper should be touched upon multiple times. Otherwise, each subject should be covered in only one place"
- B5 Rule 7 "convert this into a sequence of declarative statements that become the headers of subsections"・"The editors want to make sure that the paper is significant"
- B6 規程（context-A.md 21〜24 行）要旨 150〜250 語・キーワード 4〜6・"Statements and Declarations"・data availability statement。語数の上限は規定なし。

### 2. 1 文
言える（Take-home と C1 から）: 打鍵の記号列の人ごとの系列モデルは同じ構造の共有モデルという弱い相手には大きく勝つが、構造と縮小を他の人で選ぶと 15 セッションのパネルで残る差は手順の検出の下限より小さく、共有モデルの事前の最頻値にも勝たない。だからパネル全体で判断する研究は 3 つと比べるべきだ。迷った点: Take-home の 1 文目は約 70 語で、"the same weak structure" の weak が定義されていない（4.2 まで分からない）。

### 引き継ぎの判定
N1 一部（Take-home と 4.4 は限った。C1 の見出し 11 行 "the gain that a weak comparison shows disappears against a stronger one" が限らず言い切る）／N2 一部（4.4 の解釈の文が分解能より下の値から結論・新規 N1）／N3 解消／N4 解消（3,530 語）／N5 解消（3 行と 44 行）／N6 解消（27 行）／N7 未解消（既知の未決・数えない）／M2 解消（49 行・新しい緊張は新規 N1）／M4 一部（新規 N4）／m2 解消（49 行）。

### 3. 新規の指摘
- N1 [major] 4.4 の「This shows」が検出の下限より下の値と効かなかった分解から結論を出す
  - 位置と引用（48 行）"This shows that the shared model's smoothing, not the person's data, accounts for most of the remainder"・根拠 "Prior mode minus shared for ar3 is +7.4e-4"・"per-person minus mode is −3.5e-4 to −1.6e-4"。食い違い: 47 行 S15 "the decomposition of the remainder applied to synthetic writers (it did not separate a planted difference from none; in these writers the prior mode was worse than the shared model, unlike the real data)"・検出の下限 1e-2・3e-2（47・64 行）・49 行 "a likelihood ratio of about 4 to 13 over an hour"。
  - なぜ問題か: 残りは検出の下限より約 1 桁小さいと言いながら、同じ桁の差の大小から「大半」の出どころを言い切るのは分解能を超える。分解は合成で効かなかったと自分で書く。5 節の尤度比 4〜13 は「残りは小さくない」とも読ませ、見出しの「検出できない」との両立（パネルの中央値の検出の下限と 1 人の 1 時間の累積の違い）が書かれていない。
  - 解消の条件: 記述の文に下げる（例 "the remainder is of the same size as the prior mode's gain over the shared model; the protocol cannot apportion it"）。分解が合成で効かなかったことを同じ段落に 1 文。5 節に検出の下限と 1 人の累積の尤度比が別の量と 1 文。
  - 自信: 高
- N2 [moderate] C1 の見出しの "disappears" が 6 節の限定と矛盾（11 行・64 行 "A remainder below that limit, or a per-person model that does not beat the prior mode, does not show that per-person differences are absent."・13 行の 30 セッション k = 30）。解消: "shrinks below what the protocol can detect"（15 セッション）。自信: 高
- N3 [moderate] CS1 の役割が 1 文で書かれていない（14 行 "CS1 cannot show a per-person gain"・45 行 "CS1 shows no consistent gain"・60 行 "the CS1 measure is mostly the prediction of pause seconds"）。解消: 3.1 か序論で役割を 1 文（例: 手順が共有モデルそのものを選ぶ境界の事例）。役割の無い CS1 の数（48 行 "in CS1 the prior mode beats the shared model by +2.0e-4"）は S6 か S9 へ。自信: 中
- N4 [moderate] 但し書きの繰り返し（35 行 "Caveats are stated in full once, in Section 6" と食い違う）: 「不在を示さない」48・64 行／検出の下限の数 47・64 行（13 行にも言葉で）／「一部しか返さない」47・49・64 行／確率ゼロ 27・44・48・67 行／30 セッションが 9 人 13・65 行／ar3 が格子の最大 13・47・63 行（パネル全体の判断 7・49・66 行は中心の限定で繰り返してよい）。解消: 項目ごとに 1 か所で全文、他は参照。自信: 高
- N5 [minor] 本文に要らない細部（30 行の同点の規則 "ties go to the larger tau and then the structure with fewer free parameters"・44 行の後の確かめの列挙・48 行 "Placing the prior mode among the candidates changes little: the median objective picks it for at most one writer, whose held-out sequence has zero probability under it, and the mean objective never picks it in CoAuthor (S9)"・47 行の記号化の 2 文）。解消: 同点の規則は S3、列挙は "five later checks (S12)"、候補の結果は S9 へ移して 1 句。自信: 中
- N6 [minor] 3.2 の「状態推定器」が誰の何か無い（44 行 "these are the symbols a state estimator updating once per second over the last 30 s would read"）。適応への橋が宙に浮く。解消: どの種の適応系がこの形の記号を読むかを 1 文と出典。自信: 中
- N7 [minor] Take-home の "gains a lot" と "the same weak structure"（7 行）。解消: 量の言い方に、weak は本人の連鎖に負ける構造と句で。自信: 中
- 記録: 63 行の ar3 が格子の最大は 6 節にあるので数えない。

### 4. 判定: 直してから回す（文の単位で直る）
貢献は 1 文で言え、UMUAI の読者に届く方法論の貢献で、構成も読者の問いの順。4.4 の解釈の文が自分で示した分解能と合成で効かなかった分解の上に立ち（N1）、C1 の見出しが不在を言い切る（N2）。どちらも書き換えで直り、分量（3,530 語・予算 7,000 語）にも問題はない。

### 5. 読めなかった範囲・注入の疑い
README（補足）・S1〜S15・規程の原文は読んでいない。注入の疑い: なし。
