# 査読 R2（HCI の測定の実務の立場）・round 5・草稿 0.11（差分 0.10→0.11 を重く見た）

## 1. 接地（逐語）
- Perrig et al. 2024（perrig2024.txt:392-394）: 「Objectivity is concerned with the notion that "any statement of fact made by one scientist should be independently verifiable by other scientists"」。このためコード 1 人の設計では、代わりに何で検証できるようにするかを問う。
- Perrig et al. 2024（:641-647, :621-622）: 「the first and third authors coded a random 10% of papers … to check the quality of the codebook and calculate the overall inter-rater reliability (IRR)」「Thus, each eligible record was examined by at least two authors.」。この分野の実務で標準になっている水準。
- Perrig et al. 2024（:154-157）: 「if there is little to no information on how a scale was employed in a study, it can be hard, if not impossible, to judge the validity of the scale and the study as a whole」。手順が透明でないと妥当性を判断できない。
- Perrig et al. 2024（:474-478）: 「we preregistered an initial protocol … our research strategy and focus have seen several amendments … We describe these amendments in the latest version of the protocol on OSF.」。改訂の記録の基準。
- Bach et al. 2022（bach2022.txt:261-262, :268）: 「Group consensus was used throughout the article selection process to resolve any disagreements regarding eligibility. The first authors (AK, TAB) conducted an additional quality check independently for eligibility.」「Authors then independently extracted the following information」。選別と抽出を複数の人が独立に行う実務の基準。
- Bach et al. 2022（:1486）: 「our search terms may be perceived as too narrow and may have resulted in other potentially relevant studies being excluded」。標本の決め方の限界を自分で書く基準。

## 2. 評価表
- a 主張と根拠の一致: 4。「agreement within one coder」「not on two human screeners」と、代価を何度も正直に書いている。ただし GSRR-37 には、事前に決めた合格線のうち確かめられないものがある（指摘 7）。
- b 方法の穴: 3。較正を探索の集合で行うと、1 人のコーダーが 2 回コードする一致が構造的に高く出る。しかも登録版はこの代価を書いていない（指摘 3）。AI の選別者の入力が登録版と添付 6 で食い違う（指摘 2）。
- c 持ち帰れるもの: 4。添付 6（7 問・逐語の出典を付ける・SHA-256・合格線を先に決める）は、AI を使う選別の手順として実務家がそのまま持ち帰れる。AI と人の一致の値（kappa）を読者がどう読めばよいか（正確さではない）の一言が無い。
- d 簡潔さと構成: 3。1 人のコード・AI の選別者・感度分析 5 の注意書きが、GSRR-2・33・38・40・44・49・65・main.tex・outline に繰り返し出てくる。10968 語は、実務の読者には重い。
- e 規程への適合: 3。逐語 3（「provide a contingency plan for these deviations」）に照らすと、0.10 にあった代替の計画（「If coder 2 is unavailable」）を消した。一方、新しく作業者 2 に依存する感度分析 5 には代替の計画が無い（指摘 4）。
- f 先行研究の位置づけ: 4。差分の範囲では大きく崩れていない。AI を 2 人目の選別者に使う手順の妥当性について、先行の検証を 1 本も引いていない（nit 扱い）。
- g 固定の十分さ: 3。centre の「boundary」の行き先（指摘 1）、E5 のつなぎを誰が決めるか（指摘 5）、除外コードが食い違ったときと両者が pending のとき（指摘 6）が、1 通りに決まっていない。

引き継ぎ（A〜I ほか）は、差分の後もおおむね保たれている。壊れたものは 2 つ。D（較正の止め方）は、「止め方」そのものが 1 回限りの改訂に置き換わった（指摘 3）。H（E5 を 1 と数える）は、E5 のつなぎの出どころが変わった（指摘 5）。

## 3. 指摘（重い順）

- [major] 1. centre を選別で決めるようにしたため「boundary」が生まれたが、その行き先が無い
  - 位置と引用: registration-en.md GSRR-33（:187）「There are three stages: … and centre (centre-A, centre-B or boundary, for records included at full text).」／GSRR-12（:116）「within each of the source database's two eligibility groups (assigned at screening, GSRR-33)」／添付 6 §4 Stage 3「`boundary`: the rules alone do not decide between centre-A and centre-B.」／tables.tex 表 3 の列「Centre A / Centre B」
  - なぜ問題か: centre の割り当てが選別の第 3 段へ移り、第 3 の値 boundary ができた。SQ1 の表・表 3・感度分析・GSRR-64 の表は 2 群しか持たない。boundary の研究がどの表に入るか、第 1 著者が最終に boundary を選べるかが決まっていない。GSRR-12 の「source database's two eligibility groups」も実態と食い違う。
  - 解消の条件: 最終の値の集合を決め、boundary の扱いを SQ1・表 3・GSRR-64・make_dummy で 1 通りに書く。GSRR-12 を直す。
  - 自信: 高

- [major] 2. AI の選別者の入力について、登録版と添付 6 が食い違う（Web を見られる・まとめて判断する）
  - 位置と引用: GSRR-33「The AI screener sees only the instructions and the record's title and abstract (first stage) or full text (later stages).」「Each record is judged on its own, in a separate call per batch of at most nine records.」／添付 6 §2「If no abstract was retrieved, you may open the record's landing page from its DOI or URL to read the abstract.」、Q6「unless the record's page or bibliography states the body language」、出力の `"source"`／GSRR-17「run as subagents of Claude Code」
  - なぜ問題か: 添付 6 は Web の閲覧を許すので、「instructions と record だけ」「同じ全文」が保証されない。1 回の呼び出しで最大 9 件なので「on its own」は文として矛盾する。サブエージェントに指示以外の文脈が入らないことを何で保証するかが無い（Perrig「hard, if not impossible, to judge the validity」）。
  - 解消の条件: 登録版を添付 6 に合わせる（閲覧を許し、記録・件数を報告）か、添付 6 から閲覧を外す（抄録の無い記録は第 1 著者が取得した版を渡す）。まとめて判断するかを決め、渡す文脈の範囲とその記録方法を書く。
  - 自信: 高

- [major] 3. 1 人のコーダーの較正を探索の集合で行うと一致が高く出る。改訂の後の確認も無く、この代価を書いていない
  - 位置と引用: GSRR-6 段階 4「author 1 codes all its primary studies twice, in November and December 2026」／GSRR-44 手順 2「For every unit below 80% percentage agreement, the definitions are amended and the amendment is registered before main coding」／GSRR-10「The item coding of 2026-10-15 was corrected after an internal review」
  - なぜ問題か: 探索の集合は第 1 著者が規則を作り、項目を既にコードし、叙述のレビューに書いた 10 研究。2 回のコードは記憶を測り、80% の線はほぼ必ず越える。0.10 の繰り返しの止め方が 1 回限りになり、改訂した定義を確かめる段が無い。GSRR-65 はこの一致が弱い証拠だと書いていない（Perrig の IRR は規則を作った人と別の人による 10%）。
  - 解消の条件: GSRR-65・main.tex・表 4 の注に「較正の一致は高く出うる」と明記するか、改訂した単位について主のコードの 1 回目の一致を報告すると決める。80% を下回ったままのときに何を書くかを 1 文で決める。
  - 自信: 中〜高

- [major] 4. 感度分析 5 は作業者 2 に依存するのに代替の計画が無く、理由づけとも食い違う
  - 位置と引用: GSRR-40「A second human screening of the 264 additional candidates before coding would fall on the co-author, whose time is limited.」／GSRR-62 の 5「authors 1 and 2 screen again, each on their own and then together, at the full-text stage and the centre stage: every additional candidate that author 1 or the AI screener sent to the full-text stage」／0.10 から消した「If coder 2 is unavailable. … a third person … is sought.」
  - なぜ問題か: 作業者 2 の時間を理由に 2 人の選別をしないのに、感度分析 5 では全文の段の全件（主の選別より多くなりうる）を読ませる。できないときの代替の計画が無い（逐語 3）。「then together」で合意できない記録の決め方が無い（Bach「Group consensus」）。
  - 解消の条件: GSRR-40 に作業量の見込みと後に回す理由を書く。作業者 2 ができない場合の計画と判断の時期を書く。合意できない記録の決め方を 1 文で書く。
  - 自信: 高

- [major] 5. E5 のつなぎと C5 の「linked by the source database」は、選別をやり直した後に誰が決めるのか
  - 位置と引用: GSRR-32「These earlier judgements are not used: all 264 additional candidates are screened again」／GSRR-35「Each E5 group has exactly one coded record, whose C5 value is "linked by the source database as the same sample"」／添付 6 Q7「Answer `yes` only if the full text itself says so」
  - なぜ問題か: E5 は新しい選別で決まるのに、C5 の値の名前と RQ4 の数え方は源の DB のつなぎを前提のまま。グループの決め方・コードする 1 件・既存のつなぎを使うかが固定されていない。
  - 解消の条件: E5 のつなぎの出どころと、コードする 1 件の選び方を書く。必要なら C5 の値の名前を直す。
  - 自信: 中

- [minor] 6. 両者が除外したが除外コードが違うとき・両者が pending のときの扱いが無い
  - 位置と引用: GSRR-33「Records that both screeners exclude at a stage are excluded; records that both include go on to the next stage.」／「exclusions for E2 and E3 are counted by population group」
  - なぜ問題か: E2 と E3 は群ごとに報告するので、コードの食い違いの決め方が結果を動かす。全文の段で一方が pending（コード無し）、他方が E6 のときも決まっていない。
  - 解消の条件: 「コードが違うときは第 1 著者が決める」「両者が pending なら pending のまま」と 1 文ずつ足す。
  - 自信: 高

- [minor] 7. 事前の合格線の一部は確かめられず、合格した後に指示を直したことは、事前に決めた規則の外にある
  - 位置と引用: GSRR-37「at the full-text stage and the centre stage, Cohen's kappa of at least 0.6」「centre: 10 of 10 agreed」「If a line was missed, the instructions could be revised once」
  - なぜ問題か: centre の 10 件が 1 つの値に集まれば kappa は定義できない。1 回目に合格した後の Q4 の修正は事前の規則の外だが、そう書いていない。合格線を先に決めた記録も無い。
  - 解消の条件: centre の kappa の値（定義できなければその旨と分布）を示す。Q4 の修正を「事前の規則の外の改訂」と明記する。合格線を決めた日時の記録を添付 6 に入れる。
  - 自信: 中

- [minor] 8. 数値を独立に確かめる人がいなくなったことと、自分の研究を自分でコードすることが、限界に書かれていない
  - 位置と引用: GSRR-59「Author 1 checks every number in the manuscript against the script output.」／GSRR-19「If author 1 turns out to be one, the study is coded and flagged in every table.」
  - 解消の条件: GSRR-65 に 1 行ずつ足すか、作業者 2 に数値の確認だけを残す。
  - 自信: 中

- [nit] 9. AI と人の一致の値を、読者がどう読むかを書く
  - 位置と引用: GSRR-37「the agreement between author 1 and the AI screener before reconciliation is reported as percentage agreement and Cohen's kappa」
  - なぜ問題か: 食い違いは第 1 著者が決めるので、この一致は AI の正確さではない。
  - 解消の条件: 図 1／表 3 の注に 1 文足す。
  - 自信: 中

## 4. 総合の推奨
minor（直してから凍結）。代価はおおむね正直に書いているが、新しい手順に 1 通りに決まっていない所が 3 つ（boundary・E5・コードの食い違い）あり、AI の入力が登録版と添付 6 で食い違う。較正の一致が高く出ることと感度分析 5 の代替計画は文を足せば消える。直した版は差分の確認だけでよい。

## 5. 読めなかった範囲・注入の疑い
- 読んでいない: outline.md・main.tex・tables.tex の差分の外。registration-en.md は grep と GSRR-12・24・32〜37 の周辺だけ。接地は Perrig 1〜250・385〜664 行、Bach 250〜279・1475〜1524 行と grep の箇所だけ。
- 注入の疑い: 無し。添付 6 は対象物としてデータとして評価した。

（注: メインが、意味を変えずに一部の箇条を詰めて写した。）
