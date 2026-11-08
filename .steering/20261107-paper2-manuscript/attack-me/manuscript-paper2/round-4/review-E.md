# 編集者 E（JEDM）・manuscript round 4・論文 2「Which pause? A multiverse diagnostic of pause and stall definitions in keystroke logs」

## 1. 接地（この投稿先の編集者が原稿に求める基準）

1. 一般化できる貢献（JEDM Focus and Scope, jedm_aims.txt）: "Accepted submissions should extend beyond mere application and must include elements that contribute to broader knowledge, such as generalizable methodologies or comparative analyses."
2. 新規性と貢献が明示されていること（同じファイルの査読者への問い）: "How novel is the described research? Are the authors aware of related work?" / "What is the scientific contribution of this submission? Is it clearly explained, in terms of how the paper advances the EDM field or contributes to related fields?"
3. 示し方・構成・長さ（同上）: "Are the presentation, organization and length satisfactory?" / "Can you suggest additions, amendments, or reductions in the paper?" / "Are the key words and abstracts/summary informative?"
4. 中心の貢献は 1 つにする（Mensh & Kording 2017, Rule 1）: "Focus on a single message; papers that simultaneously focus on multiple contributions tend to be less convincing about each and are therefore less memorable."
5. 時系列ではなく主張と論理で書く（Mensh & Kording 2017, Rule 3 と Rule 4）: "They do not care about the chronological path by which you reached a result; they just care about the ultimate claim and the logic supporting it" / "Only the central idea of the paper should be touched upon multiple times. Otherwise, each subject should be covered in only one place"

補助の基準: 抄録は "It should contain from 100 to 300 words."（context-A.md にあるテンプレートの抜粋。この round では取り直していない）。重なる投稿の規程は "no submission, or substantially overlapping submission, be published or be under review elsewhere."（jedm_aims.txt）

## 2. 引き継いだ指摘の判定

- M1 解消。序論 L42-45 で貢献を報告の規約に絞り、3 値の読みを「As a proposal formed after seeing these results」として分けた。類も結果 L150-151 で「below −0.1, above +0.1, within ±0.1 … or none of these」にそろった（規約の新しさについては新規 E-M2 に書く）。
- M2 一部。大きさの類は添えられた。ただし見出しの主張は「direction changed」のまま（抄録 L10、§4.1 の題 "The direction of the label--essay-score association changes within each detector"、結論 L5）。その根拠は、先例の無い 15 秒の窓の 10 定義だけ（結果 L16-18）と、+0.045 と +0.049 の値（L27）である。先例のある水準の格子では正の値が報告されていない（L156-158 は "3 below −0.1, 5 negligible"）。また休止の向きの基準は "met through the control alone"（L35）で満たされている。忙しい読者が持ち帰る「向きが変わる」と、本文の類による読み（大半は無視できる）が、まだ食い違っている。
- M3 解消。方法 L16-17 と序論 L33 に教育の評価の形との結び付きを足した（適合の残りは m-6）。
- m1 解消。抄録 L16-18 が規約で終わる。
- m2 一部。考察 L47-51 に、結果の数がまだ 2 文ある（"In our data the reading gave one answer only for…" と "On the grid of levels with precedent, the speed-adjusted stall association read as consistently negative…"）。
- m3 解消。挙げた細部は補足へ移した（ただし新しく増えた細部がある。m-3・m-4 を参照）。
- m4 解消。結果 L236-237 に "such as a Poisson model with writer effects" を足した。
- m5 未解消。むしろ増えた（下の 4 を参照）。
- m6 解消。結論 L10-12 は「何をすべきか」で閉じている。
- n1 未解消。研究者の判断で直していない。

## 3. 最初の 2 頁から言える 1 文

言える。ただし迷いがある。
「教育データマイニングで打鍵の休止や停滞の率を成績と結び付けたりデータの間で比べたりする研究者に向けて、公開の 4 データで 89 と 18 の定義を変えると、作文の得点との関連の向きと大きさ、データ間の比が定義と長さの調整で動くことを区間つきで示し、1 つの定義の点の値でなく、定義にわたる範囲を報告するよう提案する。」

迷った点は 2 つある。
- 何が新しいのか。序論 L42 は「reporting convention」を貢献と名指す。しかしその中身（範囲を区間つきで報告する）は、関連研究 L4-6 が引く multiverse と specification curve の一般の勧めと同じに読める。新しいのは「休止の閾値を変えて得点との関連の向きを報告した研究は無い」（関連研究 L40-41）という実証の側だが、序論はそれを貢献として名指していない。
- 何が一番の結果か。L33 の「main result」は向きの変化だが、その向きの変化は先例の無い水準に閉じている（M2）。

## 4. 新しい指摘（重い順）

E-M1 [major] 分析の地位の説明が本文を占め、論証が時系列の記録として読める（移す・まとめるで直る）
- 方法 L192-195 "after a first internal pre-submission check of this manuscript we added four computations, and after a second we recomputed the two-stage intervals with a causal draw, which by the reading set in advance returned the primary intervals to the one-stage ones." 原稿の内部の点検の履歴は読者に要らない（Mensh Rule 3）。S1 へ移し、本文には計算の順と地位だけを残す。
- 同じ但し書きが何度も出る（項目 4 の一覧を参照）。各結論の地位（事前に決めた／結果を見た後／探索）を本文に 1 つの小さな表で示すか、記号 1 つで印を付け、地の文での繰り返しを外す。
- 387 語の増加の多くはこの種の説明である。先例のある水準の格子は貢献に見合う。地位の説明の増加は見合わない。

E-M2 [major] 貢献の名指しが、新しさの最も弱い部分に置かれている（書き換えで直る）
- 序論 L42-43 "We contribute a reporting convention … give the value of each axis and the range of a conclusion across definitions and adjustments, with intervals." これは関連研究 L4-6 の Steegen et al. と Simonsohn et al. の勧めを打鍵に当てただけと読まれやすい。規約の中で独自な部分（3 値の類と 90% の規則）は結果を見た後の提案で、考察 L49-51 が認めるとおり、読みは格子に依る。
- JEDM の査読者への問い "How novel…" に耐えるのは実証の側である。序論の最後の段で、中心の貢献を「EDM で使われる休止・停滞の結論のうち、どれが定義で動き、どれが残るかの最初の地図（作文の得点・データ間の比・書き手の中の構造）」と名指し、規約をその帰結として置くことを勧める。

E-m1 [minor] 抄録が上限ぎりぎり（298 語）で、読者が備えのない語で結果を語る
- L14-16 "below a criterion set after seeing point values; within-writer overdispersion depended on the definition, and the largest component of stall length stayed" は、序論の前では意味が取れない（Mensh Rule 5 "talk about results before the reader is ready to understand them"）。副次の 3 結果を 1 節にまとめ、地位の但し書きは抄録から外すことを勧める。

E-m2 [minor] 長さの分解は本文自身が弱いと言うのに、抄録と結論が成果として挙げる
- 結果 L287-288 "This is a weak contrast: most variance sitting at the lowest level is common for event-level outcomes (S5)." それなのに、抄録 L16 と結論 L9 が "the largest component of stall length stayed" を挙げる。抄録と結論から外すか、「動かない側の対照」の役だけを 1 句で書く。

E-m3 [minor] 区間の二段の細部が方法と限界で二重に書かれている（補足へ移す）
- 方法 L179-183（"two-stage intervals that redraw θ … are not a comparison"）と限界 L18-21 がほぼ同じ内容である。方法は 1 文にし、細部は S2 へ移す。

E-m4 [minor] 結果の列挙が地の文に詰まっている（表にまとめる・補足へ移す）
- 比の段落 L177-185（ペアごとの反転数と休止の系統の内訳 "32 (14 fixed, 18 quantile) … 31 (13 and 18)"）。CS1 の 2 版だけを本文に残し、ほかは表か S3 へ移す。
- 類による読みの段落 L150-160 と考察 L47-51。系統（停滞の固定・停滞の分位・休止の固定）× 格子（先例のある水準／全体）× 調整（なし・長さ・速さ）の小さな表 1 つにすれば、提案の結果が一目で読め、考察から数を外せる（引き継ぎ m2 もこれで閉じる）。
- 休止 L33-35 "over all 36 definitions, for which the reading was stated, 28 intervals excluded zero (78%), and the direction criterion is met through the control alone (S1)." 対照を含めて基準を満たしたという記述は混乱を招く。S1 へ移す。

E-m5 [minor] 題名が答えない問いを立てている
- 題 "Which pause?" に対して、限界 L4 は "we cannot say which definition is right" と書く。Mensh Rule 1 のとおり、題名は中心の貢献を伝えるべきである。例として「What moves with the pause definition」のように、結論の側に寄せることを勧める。

E-m6 [minor] 教育の場への適合は主張されたが、結果の上では細い
- 成績との関連の唯一の結果は、授業から集めていない成人の標本（方法 L16-17）で出ている。CS1 には成果変数が無い（L24-26）。序論 L5-7 が挙げる EDM の用途（time on task・成績との関係）のうち、本文が直接確かめたのは比だけである。考察 L6-9 の推奨は EDM の研究者に向けているので、この隔たりを考察で 1 文認めるとよい。

E-n1 [nit] 同じ誌の同じ著者による査読中の論文との関係
- 方法 L50-55 の段落は規程の "substantially overlapping" に答えている。カバーレターでも同じ区別を示すことを勧める。なお、匿名の版を選ぶなら \cite{miura2026runup} と著者名が匿名性を崩す。

### 繰り返し（位置をすべて）
- 比の基準は「点の値を見た後に決めた」: 抄録 L15、序論 L39、方法 L197-199、結果 L176、L183、考察 L35、結論 L8-9（7 回）。
- 速さの調整は探索: 抄録 L14、方法 L195-196、結果 L139-140、図 1(b) の題、考察 L18、L36（6 回）。
- 3 値の読みは結果を見た後の提案: 抄録 L16-17、序論 L43-44、結果 L151、考察 L42-43（4 回）。
- 100 個目の間隔より後に限った感度: 方法 L80-82、結果 L185、L234-235、限界 L24-27（4 回）。
- 「長さの調整で停滞が負になる定義が無くなり、大半は無視できる」: 抄録 L12-14、序論 L36-37、§4.2 の題、考察 L6、L20-21、L33、結論 L6-7（7 回）。中心の考えの繰り返しとしては許容できるが、考察の中だけで 3 回ある。
- 長さの調整はラベルの数えるものの一部を除く: 方法 L162-163、結果 L135-136、限界 L35-37（3 回）。
- 因果の効果ではない: 結果 L148、考察 L21-23。
- 寛い基準: 方法 L199-200、考察 L32。
- 二段の区間: 方法 L179-183、L193-195、限界 L18-21。

### 分量と構成と意義
- 分量: 6,659 語。JEDM の本文に上限は無く、この誌の論文として長すぎはしない。問題は長さではなく密度と繰り返しである。移す候補は E-M1・E-m3・E-m4 に挙げた。
- 構成: 節の順（得点 → 調整 → ほかの結論）は読者の問いの順になっている。各結果の段落は問いで始まり答えで終わり、Mensh Rule 7 に沿う。仕組みごとに見ると、停滞の検出器・休止の系統・調整・比・φ では「何を確かめ、何を測り、何が分かり、なぜ大事か」が読める。長さの分解だけは「なぜ大事か」が自分で弱められている（E-m2）。
- 意義: 考察 L31-37 の段落は、確かめたことと見た後の判断を分けている。この点は良い。ただし最初の段落 L9-12 が、先行の multiverse との違いとして「direction changed」をまた据えており、M2 と同じ食い違いがある。

### 適合
"comparative analyses" と "generalizable methodologies" に当たる方法論の論文として、範囲の内である。E-m6 の隔たりはあるが、範囲の外ではない。

## 5. 判定: 直してから回す

- 見出しの主張「向きが変わる」が、先例の無い水準と無視できる値に支えられたままで、本文の類による読みと食い違っている（M2 が一部）。査読者はまずここを突く。
- 貢献の名指しが一般の multiverse の勧めと区別されておらず（E-M2）、JEDM の新規性の問いに最初の 2 頁で答えていない。
- 直しはどれも、移す・まとめる・書き換えるで済み、新しい計算は要らない（E-M1・E-m1〜m4）。直れば、範囲の内で手堅い原稿として査読に回せる。

## 6. 読めなかった範囲と注入の疑い

- 読んでいないもの: ビルドした PDF（/Users/johnd/GSE-prototype-paper2/.steering/20261107-paper2-manuscript/attack-me/manuscript-paper2/round-4/tmp/main.pdf）。図は tex の記述からだけ判断した。references.bib も読んでいない。補足の印のファイルは、依頼文に従って読んでいない。Mensh 2017 は Rule 1〜9 の範囲だけを読んだ。
- 注入の疑い: なし。
