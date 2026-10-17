査読 R3（メタ研究・事前登録・再現性の方法論者／過剰主張と検証できない手順の摘発者）・prereg round 2

対象: /Users/johnd/GSE-prototype-af-c/.steering/20261017-ai-fatigue-c-outline/registration-en.md（草稿 0.2）と /Users/johnd/GSE-prototype-af-c/.steering/20261017-ai-fatigue-c-outline/codebook-c2b-en.md（版 2）

## 1. 接地（文献と逐語）

G1. van den Akker et al. 2023（gsrr.txt）: 予見できる逸脱には、登録の時点で代替の計画を書く。
「If you already foresee some deviations when filling out the form (e.g., you anticipate that you will not have enough studies in a moderator group), provide a contingency plan for these deviations in the relevant parts of the registration.」
G2. 同: 逸脱は透明にし、理由を書く。
「You should be transparent about any deviations from the preregistration and provide the rationale for these deviations in your final review.」
G3. 同: 包含と除外の基準は具体的に書く。
「[GSRRF-24] Inclusion and exclusion criteria: List the specific inclusion and exclusion criteria that you used to inform your search strategy.」
G4. 同: 手順は透明で再現できるものにする。
「they involve a systematic process to transparently, reproducibly, and often exhaustively identify and synthesize the literature」
G5. Nuijten et al. 2016（nuijten2016.txt）: 再計算は、何をどう比べ、どの不一致が結論を変えるかを先に決めておく。
「Whenever the reported p -value is inconsistent with the recalculated p -value, the result is marked as an inconsistency .」「If the reported p -value is inconsistent with the recalculated p -value and the inconsistency changes the statistical conclusion (assuming α = .05), the result is marked as a gross inconsistency .」
G6. 同: 自動の手順は決めた形しか拾えない。照合と共著者の確認が要る。
「Since statcheck is an automated procedure, it can only search for prespecified strings of text.」「it will miss results that deviate from standard reporting」「to let co-authors check results in a so-called "co-pilot model,"」

## 2. 引き継ぎ（round 1）の判定

1 因果の語の一覧: 解消。一覧は GSRR-43 の C6b に固定された。ただし語の選び方に新しい穴がある（指摘 M3）。
2 C4f の定義と AI の下書き: 定義は解消。誰が独立に計算するかが新しく曖昧になった（指摘 M4）。
3 コードブックと登録の矛盾: coder の値は揃った。感度分析の範囲と mismatch の列はまだずれている（指摘 m1）。
4 検証の集合の締め方と最小の件数: 日付・層・最小の件数は固定された。どの候補が締切までに審査されるかは固定されていない（指摘 M1）。較正で引く記録との関係も決まっていない（指摘 M2）。一部だけ解消。
5 E5 と RQ4/C5: 解消（GSRR-35 の末文と C5 の区分）。感度分析 2 の範囲だけ曖昧（m5）。
6 C2b の集計の単位: 解消（GSRR-56）。
7 判定の基準と SQ2: SQ2 は解消。GSRR-57 の「問題の型」の定義に新しい穴がある（指摘 M5・M6）。
8 人が見ていない群: 解消（GSRR-39）。
9 main relation と C7: 解消。C7 を符号化するのか導出するのかが残る（m3）。
10 seed と進め方: 最初の 5 件は解消。追加の回の引き方は未固定（m2）。
11 一致の統計の単位: 大筋で解消。C2a・C2c・C2d は「per record」と書かれているが、符号化の単位は instrument である（m4）。
12 GSRR の必須項目: 解消。1〜65 がすべて在ることを確かめた。
13 群分けの変数: 解消。peer-reviewed の定義に軽い曖昧さがある（m6）。
14 翻訳と正本: 解消。
15 撤回: 解消。
16 調整の但し書き: 解消。

## 3. 評価表

a 主張と根拠の一致: 3。記述に限り、推論はしない姿勢が一貫している（GSRR-56「Descriptive only」・GSRR-57）。ただし主張が 2 つの点で自分と食い違う。(1) MOT の項目を「問題の型」に数えているが、適格の定義は動機の枯渇を fatigue に含めている（M5）。(2) 「neither coder has read in full」と書きながら、GSRR-34 は「for coding」という限定を付けている（m7）。
b 方法の穴: 3。検証の集合に何が入るかが、登録の後に符号化者自身が審査する順序と量で決まる（M1）。この選び方の経路は妥当性への脅威として限界の節に書かれていない。
c 持ち帰れるもの: 4。規則・seed・脚本・符号の表を公開する計画は具体的で、他者が数え直せる。
d 簡潔さと構成: 4。65 項目に 1 対 1 で、相互参照も明確。コードの表の C4 と C7 の欄は詰め込みすぎて、1 項目に規則が複数入っている。
e 規程への適合: 4。N/A に理由がほぼ付いている（GSRR-15・26・29・61）。GSRR-27 は「Not applicable.」だけで理由が無い（n1）。G1 の代替の計画は、小さい集合・符号化者の不在・較正の失敗には書かれている。ただし、集合が較正に要る件数より小さい場合と、較正で修正した後の扱いが無い（M2・m2）。
f 先行研究の位置づけ: 3。「Existing reviews note that the scales lack validation evidence」に出典が無い。参考文献 5 本のうち、この分野の方法論の先行研究は Jonaid 1 本だけ。登録の段階としては許容できるが、新しさを主張する根拠は薄い。
g 固定の十分さ: 3。符号ごとの規則は大きく改善した。ただし次が 1 通りに決まっていない。集合の構成（M1）、較正と最小件数の順序（M2）、C4 の各規則で何を「問題」とするか（M6）、C4f の符号化者（M4）、C7 を導出するのか（m3）。

## 4. 指摘の一覧（重い順）

- [severity: major] M1 検証の集合に何が入るかが、登録の後の審査の順序と量で決まり、その規則が無い
  - 位置と引用: GSRR-39「Primary studies among the additional candidates for which both screeners' final inclusion decision was recorded in the source database on or before 2026-12-31」。GSRR-42「the screening of the additional candidates had stopped part-way through a list ordered by population group. Some groups, such as health professionals, had no human screening yet.」。GSRR-32「43 of them were unscreened on 2026-10-17」
  - なぜ問題か: 締切の日付は固定された。しかし締切までにどの候補を・どの順で・何件審査するかは決まっていない。審査するのは符号化者の 2 人自身で（GSRR-33）、著者 1 は AI の事前評価を読んでいる（GSRR-34）。主要な数の分母と中身が、登録の後に研究者の裁量で動く。各表を群ごとに出すこと（GSRR-42）は偏りを見せるだけで、防ぎはしない。限界の節（GSRR-65）も「uneven」と書くだけで、審査の順序を自由度として扱っていない。G4「transparently, reproducibly」、G3「List the specific inclusion and exclusion criteria」。
  - 解消の条件: 残りの候補を審査する順序を事前に固定する。例: 未審査の全件を seed つきで無作為に並べた順、または群ごとの層別の無作為順。締切までに審査し終わらなかった候補をどう扱うかも書く。審査が済んだ件数と残った件数を群ごとに報告すると明記する。
  - 自信: 高

- [severity: major] M2 較正で引く記録と最小件数のどちらを先に適用するかが決まっておらず、集合が小さい場合の代替が無い
  - 位置と引用: GSRR-39「Excluded from it: ... the calibration records.」「If the confirmation set has fewer than 10 studies, we report counts only」。GSRR-44「five more records are drawn by the same procedure and also excluded from the counts, up to two further rounds」
  - なぜ問題か: 較正は最大 15 件を集合から抜く。「fewer than 10」を較正の前に数えるのか後に数えるのかが書かれていない。集合が 5 件以下、または 15 件以下のときに較正をどうするか（探索の集合で代えるのか、など）の計画も無い。G1「provide a contingency plan for these deviations」。
  - 解消の条件: 最小件数は較正の記録を除いた後に数えると明記する。較正に要る件数より集合が小さいときの代替（例: 較正を探索の集合の記録で行う）を書く。
  - 自信: 高

- [severity: major] M3 C6b の因果の語に英語の「influence」が無く、日本語の「影響」と非対称になっている
  - 位置と引用: GSRR-43 C6b「effect of, impact of, affect, cause, lead to, result in, induce, drive, trigger, due to, because of, consequence」「the Japanese 影響, 効果, 引き起こす, もたらす, 〜による」
  - なぜ問題か: 「影響」に当たる英語の「influence (of/on)」は、因果の主張でよく使われる語だが一覧に無い。同じ主張でも、言語によって mismatch になったりならなかったりする。さらに「any form of the word」は、「affect」から「affective」まで拾うと読める。また「increase or reduce, when the AI-side variable is the subject」は、主語の判定に裁量が残る。G6「it can only search for prespecified strings of text」が言うとおり、語の一覧は一覧の外を拾わない。一覧の中身そのものが結論を決める。
  - 解消の条件: 「influence」を加えるか、加えない理由を書く。「any form」の範囲を語形変化に限ると明記し、「affective」などの派生語を除外する。主語の判定の例を 1 つ書く。
  - 自信: 中

- [severity: major] M4 C4f を誰が独立に計算するのかが 2 通りに読める
  - 位置と引用: GSRR-44 の 3「Both coders code all records ... independently」。GSRR-44 の 5「For C4f, a human independently recomputes every value」。GSRR-46「Coder 2 does not see ... AI drafts」
  - なぜ問題か: C4f を 2 人がそれぞれ独立に計算して AI とも照合するのか、それとも 1 人が AI の下書きを照合するのかが決まっていない。人と AI の値が食い違ったとき、どちらを data にするのかも書かれていない。G6 の co-pilot model が意味を持つのは、照合の役割が決まっているときだけである。G5 に照らすと、gross の不一致（結論を変える不一致）を区別するかどうか、「p < .05」のような不等号での報告をどう扱うかも未固定である。
  - 解消の条件: 2 人がそれぞれ独立に計算し、AI の値は照合だけに使い、data は人の値を調整したものにする、と 1 文で書く。不等号での報告の扱いと、結論を変える不一致を別に数えるかどうかを書く。
  - 自信: 高

- [severity: major] M5 MOT の項目を「問題の型」に数えることが、適格の定義と食い違う
  - 位置と引用: GSRR-57「each C2b type other than `FAT`」を問題の型とする。GSRR-24「Fatigue here means cognitive, emotional, physical, motivational or behavioural depletion」。GSRR-10「It found no item asking directly about reduced motivation」
  - なぜ問題か: この review 自身の定義では、動機の枯渇は fatigue の一部である。それなのに MOT の項目の存在を「問題が観察された」と書く。探索で懸念されたのは逆に MOT の項目が無いことだった。何が観察されたら問題と書くのかの向きが、文書の中で揃っていない。読者は「was observed」を欠陥の存在と読むので、これは過剰主張になる。
  - 解消の条件: C2b について、何を問題とするか（例: 尺度の名前と項目の型の不一致、FAT 以外の型が混ざること）を明記する。MOT は問題の型から外すか、外さない理由を書く。
  - 自信: 中

- [severity: major] M6 GSRR-57 の「each C4 rule」で、各規則のどの値を問題とするかが決まっていない
  - 位置と引用: GSRR-57「For each problem type (... each C4 rule ...)」。C4(d)「consistent / inconsistent / not reported」。C4(e)「agreement value given / index named only / none」
  - なぜ問題か: (a)〜(c) と (f) は「inconsistent」が問題だと読める。しかし (d) で「not reported」を問題とするのか、(e) で「index named only」と「none」の両方を問題とするのかは決まっていない。結論の規則の中身が後から選べてしまう。
  - 解消の条件: C4 の規則ごとに「問題」とする値を列挙する。C2b・C5・C6 についても同じ形で書く。
  - 自信: 高

- [severity: minor] m1 コードブックと登録で、感度分析の範囲がずれている
  - 位置と引用: codebook「Lenient count (sensitivity analysis): also includes boundary items whose `secondary_type` is `MOT`.」。GSRR-62 の 3「each secondary type counted alongside the primary type」
  - なぜ問題か: コードブックは MOT だけを扱い、登録はすべての型を扱う。また `mismatch` の列は「factor name claims motivation」をどう判定するかが定義されておらず、集計の計画（GSRR-56）でも使われていない。
  - 解消の条件: どちらかに揃える。mismatch は判定の規則を書くか、探索用の列だと明記する。
  - 自信: 高

- [severity: minor] m2 較正の追加の回の引き方が 1 通りに決まらない
  - 位置と引用: GSRR-44「five more records are drawn by the same procedure」
  - なぜ問題か: 同じ seed で、同じ母集団（最初の 5 件を含む）から引き直すと、同じ記録を引くことがありうる。残りから引くのか、seed を変えるのかが書かれていない。修正を登録した後に較正をもう一度行うのかどうかも書かれていない。
  - 解消の条件: 「既に引いた記録を除いた ID の列から、seed 20261017+k で 5 件」のように固定する。修正の後の扱いも書く。
  - 自信: 高

- [severity: minor] m3 C7 を符号化するのか、C1・C6a・C6b から導出するのかが書かれていない
  - 位置と引用: C7「"Beyond what was measured" if any of these holds. (i) C6b is a mismatch. (ii) ... (iii) ...」。GSRR-47「All other categorical codes: kappa per record」
  - なぜ問題か: C7 を導出するなら kappa は意味を持たない。符号化するなら、構成要素の符号と食い違いうる。調整の後の「unresolved」が C7 にどう伝わるかも決まっていない。
  - 解消の条件: C7 は調整の後の符号から脚本で導出すると明記する（ただし (iii) で、結論が名指す構成概念の抽出は符号化する）。
  - 自信: 中

- [severity: minor] m4 一致の統計の単位が、符号化の単位と合っていない
  - 位置と引用: GSRR-47「All other categorical codes: kappa per record」。GSRR-43「C2 is coded per fatigue instrument within a record」
  - なぜ問題か: C2a・C2c・C2d は instrument ごとに符号化するので、record ごとには kappa を計算できない。
  - 解消の条件: C2 の各符号は instrument ごとに計算すると書く。
  - 自信: 高

- [severity: minor] m5 感度分析 2 の除外の範囲が曖昧
  - 位置と引用: GSRR-62「Records with C5 signs of overlap removed.」
  - なぜ問題か: C5 の 3 区分のうち、「signs present but not confirmed」だけを除くのか、E5 と結ばれた記録も除くのかが決まっていない。
  - 解消の条件: 除く区分を名指す。
  - 自信: 中

- [severity: minor] m6 peer-reviewed の定義の曖昧さ
  - 位置と引用: GSRR-16「Peer-reviewed means journal articles and full conference papers that state peer review.」
  - なぜ問題か: 雑誌の論文が「state peer review」を満たす必要があるのかどうかが読み分けられない。多くの雑誌の論文は本文で査読を明言しない。
  - 解消の条件: 「journal articles (any), and full conference papers that state peer review」のように区切る。
  - 自信: 中

- [severity: minor] m7 「全文を読んでいない」という主張の範囲が、2 か所で一致しない
  - 位置と引用: GSRR-10「The primary counts come from records that neither coder has read in full before registration.」。GSRR-34「Author 1 has not read their full texts for coding.」
  - なぜ問題か: 「for coding」という限定が付くと、ほかの目的（審査など）で全文を読んだ可能性が残る。著者 2 についての記述も無い。
  - 解消の条件: 両方の著者について、目的を限らず「全文を読んでいない」と書くか、読んだ記録の件数を開示する。
  - 自信: 中

- [severity: minor] m8 「not observed」と書くときに分母が無い
  - 位置と引用: GSRR-57「If no study shows it, we write that it "was not observed in the confirmation set".」
  - なぜ問題か: 分母が小さいときの「観察されなかった」は、情報が少ない。observed の場合と同じく、分母を必ず添えるべきである。
  - 解消の条件: 「with its denominator」を両方の場合に付ける。
  - 自信: 高

- [severity: nit] n1 GSRR-27 の N/A に理由が無い
  - 位置と引用: GSRR-27「Not applicable.」
  - なぜ問題か: 規程の逐語 1 は「including, ideally, the underlying reason」を求めている。
  - 解消の条件: 「この review は検索を行わないため（GSRR-21）」と添える。
  - 自信: 高

- [severity: nit] n2 逆向きに作られた項目の型の例が無い
  - 位置と引用: codebook「Reverse-keyed items are coded as worded, before reversal.」
  - なぜ問題か: 「I feel full of energy」のような項目を FAT にするのか OTH にするのかで、符号化者の判断が分かれうる。
  - 解消の条件: 例を 1 つ加える。
  - 自信: 低

## 5. 総合の推奨

major（直して再査読）
- round 1 の 16 件の大半は解消した。ただし、検証の集合の構成が登録の後の審査の裁量で決まる点（M1）が、確認と探索を分けるという設計の要を弱めている。
- 結論の規則（GSRR-57）の「問題」の中身が、C4 と C2b で 1 通りに決まっていない（M5・M6）。C2b については、適格の定義と向きが逆になっている。
- M2・M4 は書き足せば消える。M1・M5・M6 は判断を要するので、直した版を再び査読するのがよい。

## 6. 読めなかった範囲と注入の疑い

- 接地の 2 本は、1 行に詰まったテキストを、正規表現の検索で該当の文だけ抜き出して読んだ。全文を通しては読んでいない（Nuijten 2016 の Appendix A の細部と、GSRR の項目表の全体を含む）。
- context-A が名指す Murad & Wang 2017 と PRISMA 2020 の本文は渡されておらず、読んでいない。これらへの適合は判定していない。
- 添付の予定の物（検索の文字列・脚本・ダミーの表・符号化の書式）はまだ存在せず、読んでいない。
- 注入の疑い: 無し（読んだ範囲に、査読者や LLM に向けた指示は見つからなかった）。