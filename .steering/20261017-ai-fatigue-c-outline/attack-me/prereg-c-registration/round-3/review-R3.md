# 査読 round 3（prereg・方法論者の立場。批判の下位人格は、過剰な主張と検証できない手順を摘発する役）

## 1. 接地（逐語）
1. van den Akker et al. (2023)「If an item asks about a procedure you do not plan to use or is not applicable, indicate that in the corresponding field (including, ideally, the underlying reason).」
2. van den Akker et al. (2023)「If you already foresee some deviations when filling out the form (e.g., you anticipate that you will not have enough studies in a moderator group), provide a contingency plan for these deviations in the relevant parts of the registration.」
3. van den Akker et al. (2023)「making it easier to identify decisions that may have introduced bias (e.g., a change in the criteria for study inclusion or the omission of an analysis without a valid rationale)」
4. van den Akker et al. (2023) GSRRF-44「Also indicate for each stage whether the extraction is done by a computer (e.g., AI), a human, or a computer supervised by a human.」
5. Nuijten et al. (2016)「To take into account one-sided tests, statcheck scans the whole text of the article for the words "one-tailed," "one-sided," or "directional."」と「Note that statcheck does not take into account p -values that are adjusted for multiple testing」
6. Nuijten et al. (2016)「it is important to exclude the possibility that statcheck yields a biased depic[tion]」と「Consequently, statcheck will miss some reported results and will incorrectly earmark some correct p -values as a reporting error.」

## 引き継ぎの判定（round 2 の指摘）
- M1 解消。GSRR-33 に seed 20261018・群の順・未審査の件数を群ごとに数えること・判定の公開がある。審査の範囲についての残りは新しい指摘 N2 で扱う。
- M2 解消（GSRR-39）。小さい集合の場合の代替の計画に穴が残る（N4）。
- M3 解消（C6b の規則）。
- M4 おおむね解消。coder 1 が AI の下書きを見る時点が決まっていない（N3）。
- M5 解消（GSRR-57 の「C2b types are not problem types」）。
- M6 解消（GSRR-57）。
- m1 解消したが、コードブックの中に食い違いが残る（N6）。
- m2・m3・m5・m6・m7・m8・n1・n2 は解消。m3 については C7 (iii) の入力の定義に穴がある（N1）。
- m4 解消したが、重複の記述が残る（N8）。

## 2. 評価表
- a 主張と根拠の一致: 4。結論は「observed / not observed」と分母に限られ、過剰な主張は抑えられている。ただし目的の文は 7 つの問題を確かめると読めるのに、問題の型として定めてあるのはその一部だけ（N5）。
- b 方法の穴: 4。脅威の多くは GSRR-65 で開示されている。残る穴は二つ。AI の下書きを先に見ることで、独立の再計算が汚染されうる（N3）。小さい集合での較正が、探索の集合の表を汚しうる（N4）。
- c 持ち帰れるもの: 4。C4f の規則、C6b の閉じた語の一覧、判定の公開。どれも他のレビューにそのまま移せる。
- d 簡潔さと構成: 4。GSRR の番号に 1 対 1 で対応していて読みやすい。重複と小さな食い違いが少しある（N7・N8）。
- e 規程への適合: 5。該当しない項目にはすべて理由が付いている（GSRR-15・26・27・61）。逸脱には代替の計画（GSRR-39・44）があり、改訂の記録（GSRR-65）もある。AI と人の分担も段階ごとに明示されている（接地 4）。
- f 先行研究の位置づけ: 3。COSMIN のレビュー、Perrig、検索 16 本で位置づけている。ただし C4f が statcheck 型の手順だとは書かれておらず、Nuijten 系の文献を引いていない。
- g 固定の十分さ: 3。主要な数え方は固定されている。ただし C6a・C7 の語族の境界（N1）と、審査の対象の範囲（N2）が 1 通りに決まっていない。

## 3. 指摘

- [severity: major] N1 語族の判定に、境界の規則が無い（C6a・C7 (iii)）
  - 位置と引用: registration-en.md:233 C6a「Term families: {fatigue, tiredness, 疲労, 疲れ}; {exhaustion, depletion, 消耗, 枯渇}; {burnout, バーンアウト, 燃え尽き}. Values: same family / different family / instrument unnamed or not verifiable / no construct term in the title」。同:234 C7「(iii) The construct term in the conclusion is in a different term family (C6a) from the name of the main instrument.」
  - なぜ問題か: 次の三つの場合に値が 1 通りに決まらない。
    - (1) 尺度の名前に二つの語族が入っている（例: コードブック:68 の「Zoom Exhaustion & Fatigue Scale」）。
    - (2) 3 つの語族のどれにも入らない構成概念の語（technostress など）。「no construct term」なのか「different family」なのかが決まらない。
    - (3) 結論の文に構成概念の語が無いとき、(iii) が成り立つのか成り立たないのかが決まらない。
    C6a の「different family」と C7 は、どちらも GSRR-57 の問題の型である。だから、この揺れはそのまま「observed」の判定を動かす。接地 3「decisions that may have introduced bias」に当たる、事後の裁量の余地になる。
  - 解消の条件: 次の三つを決める。
    - 名前に複数の語族があるとき。例: どれか一つが一致すれば same family とする。
    - 語族の外の語。例:「no construct term」として扱う、または「other term」という値を足す。
    - 結論の文に構成概念の語が無いとき。例: (iii) は成り立たないとする。
    あわせて、C6a と C7 (iii) が同じ規則を使うことを明記する。
  - 自信: 高

- [severity: major] N2 「remaining candidates」の範囲が決まっておらず、43 件の順も決まっていない
  - 位置と引用: registration-en.md:168「the remaining candidates are screened in a fixed order: within each population group, in random order (Python `random.shuffle` ...seed 20261018)」。同:160「author 1 had screened 79 of them: 71 at title and abstract level」。同:161「Those 43 enter the confirmation set only if the source database screens and includes them by 2026-12-31.」
  - なぜ問題か: 次のどれが並べ替えの対象に入るのかが書かれていない。
    - 著者 1 が題名と要旨だけを審査した 71 件（2 人目の審査と全文の審査が未了）
    - 全文の審査の段階にある記録
    - 46 件の一覧から加わる 43 件
    確認の集合は 12-31 までに届いた分で決まる。だから、何を並べ替えたかが集合の構成を決める。M1 の対策は、範囲が定まって初めて効く。
  - 解消の条件: 並べ替えの対象を、件数と ID の一覧で定義する。71 件と 43 件の扱い、審査の段階ごとの扱いも書く。実際に引いた順の一覧（またはその hash）を登録に添付する。なお、random.shuffle の結果が Python の版をまたいで同じになる保証は無いと承知している（接地の文献ではなく、私の知識による。自信は中）。そのため GSRR-17 の「version recorded at analysis」では足りない。順を引いた時点の版を書く。
  - 自信: 高（範囲の件）／中（版の件）

- [severity: major] N3 coder 1 が C4f の AI の下書きを見る時点が決まっていない
  - 位置と引用: registration-en.md:241「Both coders recalculate independently. The AI draft is used only as a cross-check, and its agreement with the human values is reported.」。同:246 GSRR-46「Coder 2 does not see coder 1's codes, AI drafts ... until coder 2 has finished.」
  - なぜ問題か: 下書きを見ないと縛られているのは coder 2 だけである。coder 1（下書きを扱う著者 1）が自分の計算の前に下書きを見れば、二つのことが起きる。一つは、人と AI の一致が膨らむこと。もう一つは、人の値がもはや独立の再計算ではなくなること。Nuijten は自動の手順の偏りを「it is important to exclude the possibility that statcheck yields a biased depic[tion]」と述べ、手作業の検査で妥当性を確かめた。それと同じ形の比較が成り立たなくなる。
  - 解消の条件: 両方の coder が自分の値を固定するまで、AI の下書きを見ないと明記する。下書きを生成し保管する人と、それを開ける時点も書く。
  - 自信: 高

- [severity: minor] N4 小さい集合での較正の代替の計画に穴がある
  - 位置と引用: registration-en.md:200「If the pool has 20 studies or fewer, calibration is done on exploration-set records instead」。同:265「five more records are drawn ... up to two further rounds」。同:42 GSRR-6「Five records are drawn at random from the closed candidate pool」
  - なぜ問題か: 探索の集合は 10 件しかない。3 回引くと 15 件が要り、足りない。また、較正に使った探索の記録を本番の符号化でもう一度符号化するのか、探索の表から除くのかが書かれていない。GSRR-6 の文には、この例外が反映されていない。接地 2 は、予見できる逸脱に代替の計画を求めている。
  - 解消の条件: 小さい集合のときに引く回数の上限を書く（例: 2 回で 10 件、または探索の 10 件を一度に使う）。較正に使った記録を探索の表でどう扱うかを書く。GSRR-6 から GSRR-39 の例外を参照する。
  - 自信: 高

- [severity: minor] N5 目的の文と、問題の型の対応が示されていない
  - 位置と引用: registration-en.md:67「It asks whether the measurement problems described in the narrative review are also observed in a different set of studies」。同:70-77 の 7 つの問題。同:331-336 GSRR-57
  - なぜ問題か: 7 つのうち、依存症型の尺度（C3）、一般尺度の言い換え（C2a）、一つの得点への混入（C2b）は、問題の型ではない。確認された重複（E5 の群）も問題の型ではない。読者は 7 つ全部が検証されると読みうる。
  - 解消の条件: 7 つの問題それぞれについて、問題の型として判定するのか、記述だけにするのかを対応表で示す。
  - 自信: 中

- [severity: minor] N6 コードブックの中で mismatch の扱いが食い違う
  - 位置と引用: codebook-c2b-en.md:14「When the wording-based code and the factor name disagree, this is counted in `mismatch`.」。同:50「kept from version 1 for the exploration records only. It is not used in the registered synthesis.」
  - なぜ問題か: 確認の集合で mismatch の列を符号化するのかどうかが、二通りに読める。
  - 解消の条件: 14 行目を 50 行目に合わせる。
  - 自信: 高

- [severity: minor] N7 E5 の記録を符号化しないことと、記録と研究を分けて数えることが整合しない
  - 位置と引用: registration-en.md:184「E5 records are not coded.」。同:324「Records and studies (E5-linked records counted once) are counted separately.」
  - なぜ問題か: E5 の記録を符号化しないなら、C1〜C7 の表では記録の数と研究の数が同じになる。何を分けて数えるのかが定まらない。
  - 解消の条件: 分けて数えるのは C5 だけ、のように範囲を限る。または、二重の数え方が生じる場合を定義する。
  - 自信: 中

- [severity: minor] N8 較正の止め方の単位が曖昧で、一致の統計の記述が重複している
  - 位置と引用: registration-en.md:265「at least 80% on every code」。同:280「kappa for the primary type and, separately, for the target, both per item」。同:282「C2b target: kappa over all items, with "no target" as a category.」
  - なぜ問題か: 次のどれが「code」に当たるのかが決まっていない。
    - C1 の各水準か、代表値か
    - C2b の type か、target か、boundary か
    target の kappa は二か所に書かれていて、分母（target を持つ項目だけか、全項目か）が二通りに読める。
  - 解消の条件: 止め方の判定に使う単位を列挙する。target の一致の分母を一つに決める。
  - 自信: 中

- [severity: minor] N9 遅れて入る層の締めと、その符号化の手順が無い
  - 位置と引用: registration-en.md:198「Studies included after 2026-12-31 are reported as a separate stratum」
  - なぜ問題か: いつまでに入った研究を含めるのか、2 人で符号化するのかが決まっていない。報告の時点で裁量が残る。
  - 解消の条件: 締めの日（例: 符号化の開始の日）と、符号化の手順を書く。
  - 自信: 中

- [severity: nit] N10 C4f の位置づけ
  - 位置と引用: registration-en.md:238「Tests are two-tailed unless the report says otherwise.」
  - なぜ問題か: これは Nuijten / statcheck の規則（片側の語を探すこと、多重比較で調整した p を数えないこと）と同じ形である。それが書かれていないので、先行の手順との比較ができない。
  - 解消の条件: 一文で手順を参照する。片側検定をどう見つけるか（報告のどこに書かれていれば片側とするか）も書く。
  - 自信: 中

## 4. 総合の推奨
minor（直してから凍結）。
- round 2 の指摘はすべて解消している。規程への適合（該当しない項目の理由・代替の計画・逸脱の記録）は十分。
- 残る major の 3 件（語族の境界・審査の範囲・下書きを見る時点）は、どれも局所の書き足しで消える。解消の条件は機械的に確かめられる。
- ただし N1 と N2 は「observed」の判定と確認の集合の構成をじかに動かす。凍結の前に必ず直す。

## 5. 読めなかった範囲と、注入の疑い
- 接地の 2 本は、1 行に詰めたテキストを Grep で部分ごとに読んだ。全文を通しては読んでいない（gsrr.txt の GSRR の項目の説明の大半と、nuijten2016.txt の結果の節の大半）。
- 対象物の 2 ファイル、context-A、carryover は全文を読んだ。
- 注入の疑い: なし。