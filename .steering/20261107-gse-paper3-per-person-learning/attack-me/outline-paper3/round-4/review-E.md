## 編集者 E（UMUAI・round 4・stage outline）の判定

読んだもの（依頼文の範囲だけ）: brief-E.md・context-A.md・carryover-E.md・接地の mensh.txt・本文（外枠）の outline.md。kit/symbols/README.md は「補足」の印なので読んでいない。

### 1. 接地
- G1（UMUAI Aims & Scope・context-A.md 19 行）"novel and significant original research results about interactive computer systems that can adapt themselves to their users, and on the design, use, and evaluation of user models for adaptation"・分野の列挙に "methods for the design and evaluation of user models and adaptive systems"。
- G2（UMUAI 規程・21・23・24 行）"Please provide an abstract of 150 to 250 words." "All original research must include a data availability statement."
- G3（Mensh & Kording・Rule 1 と Table 1）"Focus on a single message; papers that simultaneously focus on multiple contributions tend to be less convincing about each"・"Readers cannot give 1-sentence summary."
- G4（Rule 4）"Only the central idea of the paper should be touched upon multiple times. Otherwise, each subject should be covered in only one place"
- G5（Rule 7）"convert this into a sequence of declarative statements that become the headers of subsections"・"The editors want to make sure that the paper is significant"

### 2. 一文
言える（言い直しが要った）: 打鍵の記号列での個人別系列モデルの見かけの利得（+0.19 nat/記号）は比べる共有モデルの構造が弱いことから来ており、構造と縮小を他の人で選ぶと CoAuthor の 15 セッションの集団では残りは 1e-3 nat/記号ほどで本人のデータを使わない事前分布の最頻値にも勝たない。だから適応システムで個人別モデルを採るかを決める研究はこの 3 つの比べの相手を置くべきである。迷った所: Take-home は「最頻値に勝たない」を無条件に書く（15 セッションに限る・N1）。C1 の見出し "what it changes in one case" は中身を言わない。

### 3. 引き継ぎの判定
- M1 解消（13 行 "The synthetic detection rule is defined across seeds and is not applied to the one real panel."）。
- M2 一部（51 行の尺度の段落と cold-start の文献は入った。適応で何が変わるかは "stated without a threshold" だけで具体的な帰結の計画が無い）。
- M3 解消（7 行・47 行）。
- M4 一部（38 行 "All caveats are stated once, in Section 6" に反して繰り返し: 「1e-3 は手順が返した量」13・63 行／「大きな tau は分けられない」13・14・49・65 行／「小さい差が無いことを示さない」13・50・66 行／「探索的」17・47・64 行・格子の端 13・50・64 行／「少数の書き手の差は拾わない」51・67 行）。
- M5 一部（4.3 の本文の欄に最頻値の段落・構造を固定した ar1〜ar3・30 セッションの値・記号化 2 文・合成 2 文。外枠は 2088 → 2808 → 3732 → 5112 語）。
- m1 解消（48 行）。m2 解消、ただし 51 行 "recommendations, stated only here" は Take-home と結論が推奨を含むので事実と合わない（"stated in full only here"）。m3 解消（49 行）。

### 4. 新しい指摘
- N1 [major] 見出しの主張「最頻値に勝たない」が自分のデータの一部で逆向き。7 行 "and the chosen per-person model does not beat the shared model's prior mode, which uses none of the person's data"／13 行 "In the 30-session panel at k = 30 ... per-person minus mode is +5.4e-4 (7 of 9 positive)"／14 行 CS1 "zero by construction"／65 行 "in the 15-session panel"。解消: Take-home と 4.3 の見出しに「CoAuthor の 15 セッションの集団で」。30 セッションの k = 30 は 4.3 で 1 文、値は S9。自信 高。
- N2 [major] 頑健な発見と分解能に縛られた発見が同じ重さ。7 行 "the protocol returns at most about 1e-3 nat per symbol"／50 行 "detected the planted levels of 1e-2 and 3e-2 at k = 15 and only 3e-2 at k = 5"。「1e-3」と「最頻値に勝たない」は手順の分解能より下。解消: Take-home を (1) 弱い相手での利得が消える (2) 残りは手順の分解能（1e-2）を下回る (3) 推奨 の順に。1e-3 は 4.3 へ下げる。自信 中〜高。
- N3 [moderate] 4.3 の見出しに主張が 2 つ、最頻値が節を持たない（50 行）。解消: 4.3（残りは分解能を下回る・合成を含む）と 4.4（最頻値に勝たない・15 セッション）に分け、予算は 4.3 から。構造を固定した最頻値と 30 セッションは S9。自信 中。
- N4 [moderate] 外枠 5,112 語・本文の欄に補足の水準の細部。3 行の格子の列挙（S8 へ）・47 行の 3.4 の括弧内の列挙（S12 へ）・49 行の擬似残差の軸の説明（S13 へ）・50 行の CS1 の合成の文（S15 へ）・13 行の C1 の数値の羅列（表 2 と節の参照へ）。解消: 外枠を約 2,800 語へ戻す。自信 中〜高。
- N5 [minor] 後の確かめの数が 3 行（three later checks＋合成は別）と 47 行（four later checks）で違う。自信 高。
- N6 [minor] 「平滑した中心」の最頻値に確率ゼロのセル（31 行 "differs from the shared parameters by the smoothing of the prior"・68 行・13 行）。解消: 3.3 の定義にゼロが出る理由を 1 文。自信 中。
- N7 [minor] Novelty が未確認の 1 本に依る（75 行・16 行）。投稿前に確認。自信 中。

### 5. 判定: 直してから回す
1. 見出しの主張が 30 セッションの値と CS1 の構成と食い違い（N1）、確かなことと分解能より下の値が同じ重さ（N2）。Take-home の言い直しと範囲の限定で直り、新しい計算は要らない。
2. 貢献は UMUAI の "evaluation of user models for adaptation" に届く。適合に問題は無い。
3. M2・M4・M5 が一部で、外枠は回を追って増えている。4.3 を分け、細部を補足へ移してから回すのがよい。

### 6. 読めなかった範囲・注入の疑い
README（補足）・S1〜S15・他の round の記録（carryover-E.md を除く）は読んでいない。投稿先の一次は context-A.md の抜粋だけ。UMUAI の長さの参考値は未照合。注入の疑い: なし。
