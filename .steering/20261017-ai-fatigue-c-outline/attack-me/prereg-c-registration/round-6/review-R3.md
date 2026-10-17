# 査読 R3（メタ研究・事前登録・再現性の立場）・round 6

総合の推奨: minor（直してから凍結）。round 5 の 14 件はほぼ消えた。差分が足した E5 の連結の規則（GSRR-33）が添付 6 の Q7 と GSRR-35 にぶつかる。注意: 引き継ぎには見出ししか無く、round 5 の指摘の本文は読めていない。

## 1. 接地
- G1 van den Akker et al. 2023「[GSRRF-33] … Also indicate for each round whether the screening is done by a computer (e.g., AI), a human, or a computer supervised by a human.」
- G2 同「[GSRRF-37] Screening reliability: For each screening round, list the number of screeners and the procedure used to ensure independent screening.」
- G3 同「If you already foresee some deviations when filling out the form … provide a contingency plan for these deviations in the relevant parts of the registration」「You should be transparent about any deviations from the preregistration and provide the rationale for these deviations in your final review.」
- G4 同「making it easier to identify decisions that may have introduced bias (e.g., a change in the criteria for study inclusion or the omission of an analysis without a valid rationale)」
- G5 Nuijten et al. 2016「to encourage sharing data, to let co-authors check results in a so-called "co-pilot model," and to use statcheck to flag possible inconsistencies」
- G6 同「manual checking is subject to human error」

## 2. round 5 の指摘が消えたか
- M1 消えた。M2 一部（12-31 後の pending の行き先、boundary は件数しか残らない）。M3 一部（コミットの時刻は自分で付けられる）。M4 消えた（外したことを逸脱と呼んでいない点は残る）。M5 消えた。M6 消えた（第 1 著者は Q ごとの答えを残さない）。m1 消えた。m2 一部（ウェブを外した直しに departure の語が無い）。m3 一部（再実行も形式を満たさないときの手順が無い）。m4 消えた（文言に曖昧さ）。m5 消えた。m6 消えた。n1 消えた。n2 消えた。

## 3. 評価表
- a 4: 一致は AI の正確さではないという書き方が揃った。GSRR-38 の文だけが無条件で full text だけの書き方のまま。
- b 3: E5 の規則が添付 6 と矛盾。12-31 後の pending、再実行が 2 回目も形式を満たさない場合に手順が無い。
- c 4: 3 回分の判定の公開・コミットの公開・選別の一致の扱いは他のレビューでも使える。
- d 3: GSRR-33 の 1 項が長すぎる。GSRR-44 の unit が 2 つの意味。
- e 4: G1・G2・G3 は満たした。逸脱の報告はウェブを外した直しにだけ欠ける。
- f 4: 差分の範囲に問題なし。
- g 3: E5 の群の作り方、時刻の公開を第三者がどう確かめるかの固定が足りない。

## 4. 指摘
- [major] E5 の「最も早い記録をコードする」規則が Q7 と GSRR-35 にぶつかる
  - 位置と引用: GSRR-33「a record is linked to another as the same sample only if its full text says so (attachment 6, Q7) … Within a linked group, the record coded is the one with the earliest publication date」。GSRR-35「Each E5 group has exactly one coded record (GSRR-33)」。添付 6 Q7「Does the full text report the same sample as another record … yes → E5」。
  - なぜ問題か: (i) Q7 は連結を言っている側を E5 で除くので、それが最も早い記録なら規則と選別が食い違う。(ii) 「another record」が候補の外か別の理由で除かれていれば、群にコードされる記録が 0 件になり、研究が消え "exactly one" に反する。(iii) AI には相手の記録が見えない。凍結後に直すと G4 の "a change in the criteria for study inclusion" になる。
  - 解消の条件: 相手との突き合わせは第 1 著者が行う。相手が候補の外か除かれた場合は E5 にせずコードし、C5 は signs present などに。最も早い記録が E5 と判定された側だったときの規則を決め、"exactly one" がどの場合にも成り立つと示す。
  - 自信: 高
- [minor] 束と時刻の記録が第三者に確かめられる形でない
  - 位置と引用: GSRR-33「author 1's judgements are committed to a version-controlled repository, with their time, before the AI screener's output for that batch is opened」
  - 解消の条件: 束ごとに公開のリモート（または OSF）へ push し相手側の時刻を記録する、または時刻は自己申告だと限界に書く。
  - 自信: 中
- [minor] 12-31 の時点で pending だった記録のその後
  - 位置と引用: GSRR-33「a record still pending on 2026-12-31 is outside the main set and is counted in Table 3 and the flow diagram」。GSRR-39「Studies included after 2026-12-31 and before stage 5 begins are reported as a separate stratum」。図 1 では late の矢印が unscr からしか出ていない。
  - 解消の条件: 選び続けて late stratum に入れるか打ち切るかを 1 文で書き、図 1 にも反映する。
  - 自信: 中
- [minor] boundary とされた記録が辿れない
  - 位置と引用: GSRR-33「the number of records that either screener judged boundary is reported」
  - 解消の条件: 研究ごとの表と GSRR-41 の公開リストに「boundary だったか（どちらが言ったか）」の列。
  - 自信: 中
- [minor] ウェブを外した 2 つ目の直しが逸脱と呼ばれていない
  - 位置と引用: GSRR-37「The pre-set rule did not call for the revision before round 2: it was a departure from the rule, and it is reported as one. In rounds 1 and 2 the instructions allowed … this was then removed」
  - 解消の条件: 2 つ目も departure と書き、同じ記録に 3 回当てたので正確さはさらに楽観的になりうると 1 文。
  - 自信: 高
- [minor] 再実行も形式を満たさなかったときの手順が無い
  - 位置と引用: GSRR-33「a batch is never re-run, except once when the output is not in the required format, in which case the first output in the required format is used」
  - 解消の条件: その束（その記録）は AI の判定なしとして第 1 著者が決め、件数を報告する。
  - 自信: 中
- [minor] GSRR-38 が条件付きの感度分析 5 と食い違う
  - 位置と引用: GSRR-38「sensitivity analysis 5 (GSRR-62) repeats the full-text screening with two human screeners after the manuscript draft」
  - 解消の条件: 「full-text and centre … if author 2 can do it (GSRR-62)」に揃える。
  - 自信: 高
- [nit] GSRR-44 の unit が 2 つの意味
  - 位置と引用: GSRR-44「For every unit below 80% percentage agreement in at least 5 units of comparison … units with fewer than 5 are reported」
  - 解消の条件: 「for every unit with at least 5 compared cases and below 80%」。
  - 自信: 高
- [nit] 第 1 著者は Q ごとの答えを残さない
  - 位置と引用: GSRR-36「Author 1 records a decision and a code for each record and does not fill in the AI screener's output format」
  - 解消の条件: その代価を限界に 1 文。
  - 自信: 中

## 5. 総合: minor。E5 の 1 件は除外の規則なので凍結の前に閉じる。他は文言の直しで再査読は要らない。

## 6. 読めなかった範囲と注入の疑い
- 読んでいない: 登録版の差分の外（GSRR-17・33〜40 と grep の行だけ）、外枠・草稿・表・図は差分だけ、接地は grep のみ、round 5 の指摘の本文。
- 差分の外で気づいたが確かめていない: registration-en.md:180「These 221 are the additional candidates」と他の箇所の 264。
- 注入の疑い: 無し。

（注: メインが、意味を変えずに一部の箇条を詰めて写した。）
