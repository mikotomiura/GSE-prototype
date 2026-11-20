# 編集者の役 E（UMUAI の担当編集者）・round 10 の結果

対象: /Users/johnd/GSE-prototype-paper3/papers/per-person-learning/manuscript/main.tex（commit c87c7d63）。references.bib は注入の有無だけを grep で確かめた。

## 1. 接地（抜き出した基準）

- **E1（範囲）** UMUAI の Aims & Scope（context-A.md）: "novel and significant original research results about interactive computer systems that can adapt themselves to their users, and on the design, use, and evaluation of user models for adaptation"。分野の列挙に "methods for the design and evaluation of user models and adaptive systems" がある。→ 適応のためのユーザーモデルを評価する方法に、新しい貢献があることを求める。
- **E2（読者）** Aims & Scope: "The central audience of the journal are researchers, students and industrial practitioners from the following areas: Adaptive Systems, Human-Computer Interaction, ... the Instructional Sciences, ... Linguistics"。→ 系列モデルや平滑の訓練を前提にせず読めることを求める。
- **E3（1 つの貢献）** Mensh & Kording 2017 Rule 1: "Focus on a single message"。Table 1 には「違反の兆候」として "Readers cannot give 1-sentence summary." がある。
- **E4（図表の題が結論を運ぶ・結果の段の順）** Rule 7: "the title of the figure should communicate the conclusion of the analysis"。さらに "Each subsequent paragraph in the results section starts with a sentence or two that set up the question ... and the paragraph ends with a sentence that answers the question."
- **E5（語の定義と一貫）** Rule 2: "Define technical terms clearly ... Avoid abbreviations and acronyms"。Rule 4: "Only the central idea of the paper should be touched upon multiple times" と "Resist the temptation to use a different word to refer to the same concept"。

## 2. 要旨と序論だけから言える 1 文

言える。

「キーストロークの系列モデルでは、書き手ごとのモデルは同じ弱い構造の共有モデルにははっきり勝つ（最大 0.19 nats/記号）。しかしその構造は書き手自身の一次マルコフ連鎖に負ける。構造と、共有モデルへ引き寄せる強さを他の書き手で選ぶと、残りは 1/100 以下に縮み（事後に両側へ同じ平滑を当てた設計者向けの比べで 3.4〜5.2×10^-3）、個人差を示さない。だから、個人ごとに作るかを決める研究では、本人の連鎖と強い共有モデルの両方と比べ、選びは他人で行うべきだ。」

迷った箇所は 1 つ。序論（main.tex:49）は「2 つ目の値が決定に関わる」と宣言している。しかしその理由の句「the strongly shrunk per-person fit is effectively less smoothed than the shared model」は、prior mode（3.3 節で初めて出る）を知らない読者には追えない。どちらが答えかは「宣言としては」決まっているが、「理解としては」決まっていない。

## 3. 指摘

### round 9 の引き継ぎの判定

- **M1 答えが 2 つの値に割れる → 一部。** 序論 L49「the remainder does not show per-person differences」と要旨 L35「Neither value shows a per-person difference」で、主張は 1 つになった。ただし、決定に関わる値（対称の再当てはめ）は要旨の後半に回っている。要旨は先に固定の平滑の値とその合成の裏付けに約 60 語を使う。図表と節の題は、決定に関わらない方の値を結論として運んでいる（下の新規 N1）。
- **M2 4.4 の入れ替えの段 → 一部。** L284 は「Does the remainder need the writer's own sessions, or would any k sessions do?」と問いで始まり、改善した。しかし答えの「so the remainder does not come from refitting the prior on k sessions alone」は段の中ほどに埋まり、段の最後は但し書き「None of the values at α=0.03 was checked against synthetic writers.」で終わる（E4）。手順の文「the per-person fit is refitted with w's chosen τ, and a prior built the same way from a shared model without w and v, to v's k training sessions and scored on w's held-out sessions」は、入れ子が深く初見では読めない。規則「a margin of at least half the remainder」と、2 文後の「the margin is not a share of the remainder」は、続けて読むと矛盾して見える。
- **M3 平滑の効きの呼び名 → 解消。** L49 で smoothing effect を定義し、L145 で定め直している。
- **m1 但し書きの繰り返し → 一部。** 下の N4 に位置を全部挙げた。
- **m2 序論の未定義の語 → 解消。** fixed base smoothing と symmetric refit は L49 で定義されている。second null は序論に出ない。ただし L145 で、定義（L191）より前に second null が出る（nit）。
- **m3 要旨の照応 → 一部。** 「its source (the writer, closeness in time or the amount of data)」の its は第 2 の値を指すと読めるが、遠い。末文の「compare with both baselines」の both は、要旨の中で 2 つの基準として名指されていない（N3）。
- **m4 定義の無い語 → 一部。** 残っている語は N5 に挙げた。
- **m5 方法の細部を補足へ → 未解消。** 著者は採らないと判断した。N6 で長さとの関係でだけ触れる。
- **n1 4.4 を 2 小節に → 未解消。** 著者は採らないと判断した。N1 の解消の条件と重なる。

### 新しい指摘

- **[severity: major] N1 図・表・結果の節の題が、決定に関わらない方の値（<10^-3）を論文の答えとして運んでいる**
  - 位置と引用:
    - 4.3 の見出し L234「leaves a remainder below 10^{-3} at the fixed base smoothing」
    - Table 2 の題 L245「falls from a gain of about 0.2 to a remainder to below 10^{-3} nats per symbol」
    - Figure 2 の題 L230「with the 3-state AR-HMM the per-person model beats its shared model by less than 10^{-3}」
    - 決定に関わる値は、点検の節 4.4 の見出し L273「returns in a symmetric refit (post hoc)」の中、7 段のうち 3 段目（L280）にある。
  - なぜ問題か: 序論 L49 は「The second bears on a designer's decision」と言う。ところが、要旨から図表へ飛ぶ読者（E4: "figures are often viewed by readers who skip directly from the abstract"）が持ち帰るのは「10^-3 未満」で、決定に関わる 3.4〜5.2×10^-3 は「点検」の扱いで埋もれる。答えが 2 つに割れる問題（M1）が、図表の層で残っている。
  - 解消の条件: 次のどちらかがあれば消える。(a) Table 2・Figure 2・4.3 の題を「弱い比べの利得は強い比べで 1/100 以下に縮む」と、値の大小を限定しない結論にする。(b) 対称の再当てはめを自分の小節（または Figure 2 の点か Table 2 の行）にし、題に 3.4〜5.2×10^-3 を出す。題の書き換えだけなら新しい計算は要らない。
  - 自信: 高

- **[severity: major] N2 最初の 2 頁で、なぜ 2 つ目の値が答えなのかを想定読者が理解できない**
  - 位置と引用: L49「whereas at the fixed base smoothing the strongly shrunk per-person fit is effectively less smoothed than the shared model it is compared with」
  - なぜ問題か: この句の理解には 2 つの知識が要る。強く縮めた当てはめが、base smoothing を除いた \bar S の正規化（prior mode, L143）に近づくこと。その近づき方が平滑を外すのと同じ効きを持つこと。どちらも 3 節まで出てこない。HCI・教育工学の読者には、2 つ目の値を選ぶ根拠が宣言にしか見えない（E2、E5 "Define technical terms clearly"）。
  - 解消の条件: 序論で平易な 1 文を足す。例:「強く縮めると、個人のモデルは共有モデルから平滑を抜いた形に近づくので、固定の平滑のままでは片側だけ平滑が軽い比べになる。そこで、平滑も他人で選んで両側に同じものを当てた比べを、決定に使う」。あるいは Figure 1 の隣に、3 つの比べ（弱い・強い・両側同じ平滑）を並べた模式図を置く。
  - 自信: 中

- **[severity: minor] N3 要旨に定義の無い語と、読みにくい推奨の文**
  - 位置と引用:
    - L35「at the fixed base smoothing」（要旨の中で定義されない）
    - L35「under the post hoc null」（null の語が要旨で初出）
    - L35「planted differences」
    - L35「should compare with both baselines and choose structure, shrinkage and, applied to both models, smoothing on other people (post hoc, one structure)」
  - なぜ問題か: 要旨だけを読む読者（E3・Mensh Rule 5）には、fixed base smoothing と null が何か分からない。末文は挿入句で目的語が割れていて、1 回では読めない。248/250 語で余地も無い。
  - 解消の条件: 3 つの直しで消える。fixed base smoothing を「the small default smoothing」などの平易な語にする。null を「synthetic writers without per-person differences」に統一する。推奨を 2 文に割る（"Compare with the person's own Markov chain and a stronger shared model. Choose structure, shrinkage and smoothing on other people, applying the same smoothing to both models."）。語数は、固定の平滑の値に付いた合成の裏付けの句を序論へ移して作る。
  - 自信: 高

- **[severity: minor] N4 同じ但し書きの繰り返し**
  - 位置と引用:
    - 対称の再当てはめが合成で確かめられていないこと（7 回）: L35「or checked on synthetic writers」、L49「the second was not checked against synthetic writers」、L284「None of the values at α=0.03 was checked against synthetic writers」、L321「no synthetic check」、L332「(ours was evaluated only at the fixed base smoothing)」、L345「calibrates detection at the fixed base smoothing only」、L354「it was not checked against synthetic writers」
    - 書き手と時間の近さ・データの量を分けていないこと（5 回）: L35、L284、L321「though not necessarily because of stable differences between writers」、L333、L354
    - 倍率が格子の端にあること（5 回）: L280「α=0.03 is the lowest value of the grid」、L321「a multiplier at the edge of its grid」、L329、L346、L354
    - post hoc の印: 要旨だけで 4 回。本文では 20 回を超える（L49、L180、L185、L241、L273、L280、L282、L288、L314、L319、L321 は 3 回、L323、L329、L354 は 3 回 など）
    - 「overlapping, smoothed」の範囲の限定: L35、L51、L134、L204、L319、L327、L339、L354
  - なぜ問題か: E5 の "Only the central idea ... multiple times" に当たる。但し書きが主張と同じ回数だけ出て、どれが中心か読者が測れない。
  - 解消の条件: 対称の再当てはめの 3 つの限界（合成の点検なし・源を分けていない・格子の端）を限界の節の 1 項にまとめる。要旨・序論・結論はそれを 1 句で指し、4.4 と考察 L321 は参照だけにする。post hoc は 3.4 節 L180 の一覧で定義済みなので、表と節の見出しの印に限る。
  - 自信: 高

- **[severity: minor] N5 定義なしに出る語と、1 つの概念に 2 つの語**
  - 位置と引用:
    - 定義なしに出る語: L67「random effects」「boundary estimate of a variance component」、L70「deviance information criterion (DIC)」（略号だけ）、L71「Markov-switching models」、L137「Dirichlet priors」「MAP objective」、L178「percentile bootstrap intervals」、L51・L64「interpolation weights」、L333・L347「nested design」、L346「local optimum」、L348「conformance test」「per-record hashes」
    - 1 つの概念に 2 つの語: 共有モデルを L189 で「the common one」と呼んでいる。units / sessions / assignments / work blocks が混在する（L284 の入れ替えは「sessions」、L178 は「units」）。「per-person minus shared」と gain / remainder も混在する。
  - なぜ問題か: E2・E5 に当たる。特に「the common one」は、別の比べの相手かと読者に思わせる。
  - 解消の条件: 関連研究の語は 1 句の言い換えを添えるか削る。L189 は「the shared one」にする。入れ替えの段は units に揃える。
  - 自信: 中

- **[severity: minor] N6 長さ（7,745 語）は貢献を埋めてはいないが、4.4 節が貢献の値を埋めている**
  - 位置と引用:
    - 4.4 節（L273〜288）は 7 段に、writer split、shared-only、symmetric、2 つの prior-mode の対照、入れ替え、smoothing effect、先頭の記号を除いた採点が並ぶ。
    - 本文に置く必要の薄い細部: L137 の EM の開始点と停止の規則、L180 の事後の変更 6 件を 1 文で並べた箇所（約 150 語）、L288 の先頭の記号を除いた採点の段、L282 の 2 つの prior-mode の対照、L186 の own chain の平滑の選び、L346 の EM の局所解の 2 文
  - なぜ問題か: 投稿先に上限は無く、近年の UMUAI の論文（約 9,800〜13,300 語）より短いので、総量そのものは問題ではない。しかし round 9 からの +251 語の多くは 4.4 と限界に入り、決定に関わる値の段をさらに後ろへ押している（E4 "a sequence of statements"）。
  - 解消の条件: L288・L282・L186 を補足（S16）へ移し、本文には各 1 句の結果を残す。L180 の 6 件の一覧は表か補足 S12 へ移す。N1 の (b) を採るなら、4.4 を「平滑への依存」と「選びの点検」の 2 つに分ける（n1 と同じ）。
  - 自信: 中

- **[severity: nit] N7 小さな文の乱れ**
  - 位置と引用:
    - Table 2 の題 L245「falls from a gain of about 0.2 to a remainder to below 10^{-3}」（to が重なる）
    - L145「to calibrate the second null」（定義 L191 より前に出る）
  - 解消の条件: 「to a remainder below」にする。L145 は「a synthetic check (Section 3.6)」にする。
  - 自信: 高

### 意義と適合についての所見（指摘ではない）

- 考察 L323 の「Not established:」は、確かめた事と可能性にとどまる事を分けていて、よい（E8 相当）。
- 適合: 「ユーザーモデルの評価の方法」（E1 の列挙）に当たり、範囲内である。下流の適応の利得を測っていないことは L341 と L321 で断ってある。

## 4. 判定: 査読に回す

1. 1 つの主張（弱い比べの利得は強い比べで消え、残りは個人差を示さない）は、要旨と序論から 1 文で言える。範囲（ユーザーモデルの評価の方法）にも合う。
2. 残る major 2 件（N1 の図表と節の題、N2 の序論での理由の 1 文）は、題と 1〜2 文の書き換えで直せ、新しい計算は要らない。送る前に直すのが安いが、査読を止めるほどではない。
3. 繰り返しと 4.4 の密度（N4・N6）は、査読者にも同じ負担をかけるが、内容の判断は妨げない。

## 5. 読めなかった範囲と、注入の疑い

- 読めなかった範囲: なし。main.tex は全文を読んだ。references.bib は注入の語（ignore / reviewer / accept / instruction / LLM）を grep しただけで、書誌の中身は照合していない。補足の印のファイル（figdata・kit の README）は依頼どおり読んでいない。
- 注入の疑い: なし。
