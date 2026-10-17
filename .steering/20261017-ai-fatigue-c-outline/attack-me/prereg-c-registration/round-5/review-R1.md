# 査読 R1（心理測定と構成概念の妥当性の立場）・prereg round 5（草稿 0.10 → 0.11 の差分）

## 1. 接地（逐語）
- Elson et al. (2023): "the lack of transparency in reporting, and (c) the lack of common referents ... are an enormous threat to meaningful evidence cumulation and research synthesis." → 手順を透明に報告すること。
- Elson et al. (2023): "Document when deviations happened, and if possible assess the robustness of conclusions." → 逸脱を記録し、頑健さを確かめること。
- Elson et al. (2023): "a measure cannot be improved when changes to it are not communicated." → 手順の変更を伝えること。
- Elson et al. (2023): "Reject studies that use novel/ad-hoc measures without providing validity evidence from independent data." → 新しい道具には独立のデータで裏づけること。
- Lintner (2024): "It was performed by a single author, which might have caused some bias in the scales' quality assessment, despite the COSMIN quality criteria being straightforwardly and quantitatively stated" → 1 人で行うことを限界として明記すること。
- Lintner (2024): "I assessed each measurement property by a box containing several questions scored on the scale of very good, adequate, doubtful , and inadequate , according to the defined COSMIN criteria" → 判断を固定した問いと尺度に落とすこと。

## 2. 評価表
- a 3: 1 人で 2 回の代価は正直に書かれている（GSRR-44・49・65）。主の集合を「two independent screeners」が選んだという言い方は、食い違いを全部第 1 著者が決める手順より強い。外枠の「the scheme reused」には他の人が使える証拠が無い。
- b 2: 較正の材料がコーダー自身が規則を作りコードした記録（記憶で一致が膨らむ）。改めた定義を確かめずに主のコードへ進む。主の集合の E5 の連結を誰が決めるかが宙に浮いた。
- c 3: AI の選別者の事前の点検と公開の計画は持ち帰れる。コーダー間の再現性の証拠は無くなった。
- d 3: 差分は整っているが、添付 6 と本体で入力の定義がずれる。
- e 3: 感度分析 5 に実行できない場合の計画が無い（逐語 3）。AI の指示を規則の外で改めたことが逸脱として書かれていない（逐語 2）。
- f 3: 1 人の評価を限界とした先例（Lintner 型）に結びつけていない。差分の範囲では大きな問題ではない。
- g 2: 感度分析 5 の調整の規則・締切の日付・著者 2 が欠けたときの扱い、boundary の行き先、両者が pending のとき、AI の出力の取り直しの規則が 1 通りに決まっていない。

引き継ぎの直し（A・B・C・E・G・I・J・K・10 研究未満）は、差分が壊したものは見つからなかった。

## 3. 指摘（重い順）

- [major] 1. 主の集合の E5（同じ標本）の連結を誰が決めるかが、差分で宙に浮いた
  - 位置と引用: GSRR-35「Each E5 group has exactly one coded record, whose C5 value is "linked by the source database as the same sample"」。GSRR-43 C5「We do not decide sameness ourselves」。GSRR-33 の AI は「does not see the source database's classification」。添付 6 Q7 で AI が E5 を判定する。
  - なぜ問題か: 主の集合の E5 はこのレビューの選別者が決めるので、C5 の値の名前と「We do not decide sameness ourselves」が主の集合では偽になる。RQ4 の根拠がずれる（Elson「a measure cannot be improved when changes to it are not communicated」）。
  - 解消の条件: 主の集合の E5 の連結を誰がどう決めるかを書き、C5 の値の名前と GSRR-35・RQ4 の文を書き換え、1 群のうちどれをコードするかを書く。
  - 自信: 高

- [major] 2. 較正が、コーダーが規則を作りすでにコードした記録の上で行われ、改めた定義は確かめられないまま主のコードに入る
  - 位置と引用: GSRR-44 step 2「Author 1 codes all primary studies of the exploration set twice ... For every unit below 80% percentage agreement, the definitions are amended and the amendment is registered before main coding」。GSRR-10「Version 2 was therefore written after the exploration results were seen」。
  - なぜ問題か: 1 人の 2 回の一致は安定性で再現性ではない。既に読んだ 10 研究なので記憶で一致が上に偏る。0.10 の追加の回が無くなり、改めた定義が未検証のまま主の集合に当たる（Lintner「performed by a single author ...」、Elson「without providing validity evidence from independent data」）。
  - 解消の条件: (1) 較正の一致が記憶で膨らみうることを GSRR-65 と表 4 の注に書く。(2) 改めた単位の確かめ方を 1 通りに決める（主の集合の最初の n 件で 2 回の一致を見る等）。しないなら「改めた定義は較正で確かめていない」と限界に書く。
  - 自信: 高

- [major] 3. 添付 6 が、本体の言う AI の入力の範囲を越えている（ウェブを開くこと）
  - 位置と引用: instructions.md §2「If no abstract was retrieved, you may open the record's landing page from its DOI or URL to read the abstract.」、Q6「unless the record's page or bibliography states the body language」、"source"。GSRR-33「The AI screener sees only the instructions and the record's title and abstract (first stage) or full text (later stages).」。instructions.md 冒頭「It sees only this text and the record's inputs listed in section 2」。
  - なぜ問題か: 登録する 2 つの文書が食い違う。AI がウェブを開けるなら、同じ入力の前提と再現性が崩れる。
  - 解消の条件: 抄録の無い記録は DB が取った抄録を両者に渡し AI にウェブの道具を持たせない、またはウェブを許すこととその範囲・記録の仕方を本体に書く。
  - 自信: 高

- [major] 4. 感度分析 5 の手順が 1 通りに決まっていない。著者 2 が欠けたときの計画も無い
  - 位置と引用: GSRR-62 の 5「authors 1 and 2 screen again, each on their own and then together」。GSRR-40「would fall on the co-author, whose time is limited」。
  - なぜ問題か: (1) together での決め方、(2) 締切の日付（late stratum を含めるか）、(3) 公開した判断を見ずに選ぶのか、(4) 実行できないときの扱いが無い（逐語 3、Elson「Document when deviations happened ...」）。
  - 解消の条件: (1)〜(4) を 1 文ずつ書く。第 1 著者は前の判断を覚えているので、増える独立性は主に著者 2 の分だと書く。
  - 自信: 高

- [minor] 5. 「two independent screeners」は、決定の構造より強い言い方
  - 位置と引用: outline.md「included by 31 December 2026 by two independent screeners, the first author and an AI screener」。GSRR-38「Author 1 decides every record on which author 1 and the AI screener differ」。
  - なぜ問題か: 最終の集合は AI を読んだ後の 1 人の判断。AI の指示は第 1 著者が同じ 34 件で磨いた基準から書いた。判断の独立であって視点の独立ではない。
  - 解消の条件: 段ごとに、食い違いを第 1 著者がどちらへ決めたかの件数を GSRR-37 と表 3 に足す。外枠と抄録は「screened independently by the first author and an AI screener; the first author decided differences」程度に留める。
  - 自信: 中

- [minor] 6. centre の「boundary」に、行き先の表が無い
  - 位置と引用: GSRR-33「centre (centre-A, centre-B or boundary ...)」。GSRR-12 SQ1 は 2 群。表 3 の列「Centre A / Centre B」。
  - 解消の条件: 「最終の centre は A か B。boundary は第 1 著者が決める」か「boundary は第 3 の列」のどちらかを書く。
  - 自信: 高

- [minor] 7. AI の指示を、事前に決めた改訂の規則の外で改めたことが、逸脱として書かれていない
  - 位置と引用: GSRR-37「If a line was missed, the instructions could be revised once ... Round 1 met all three lines ... One question ... was then clarified」。main.tex は round 2 の値だけ。
  - 解消の条件: GSRR-37 に「the rule did not call for a revision; the revision was a departure from it」。原稿の方法にも 1 文。
  - 自信: 中

- [minor] 8. 2 回目のコードを「1 回目を見ずに」行う仕組みが無い
  - 位置と引用: GSRR-44「the second pass is made without looking at the first」。
  - 解消の条件: 1 回目のコードの表を SHA-256 つきで保存して閉じ、2 回目は新しい書式で記録の順を並べ替えて行うと書く。
  - 自信: 中

- [minor] 9. AI の呼び出しの手順に、取り直しと一括処理の規則が無い
  - 位置と引用: GSRR-33「Each record is judged on its own, in a separate call per batch of at most nine records」「Its output is stored with its SHA-256 before author 1 opens it」。
  - 解消の条件: 取り直しの条件（書式の誤りのときだけ・最初の正しい出力を使う・回数を報告）。一括処理の影響を限界に 1 文。
  - 自信: 中

- [minor] 10. 両者が pending（コード無し）にしたときの扱いが無い
  - 位置と引用: instructions.md「`pending` (without a code) if the full text was read but the rules do not settle the record」。
  - 解消の条件: 第 1 著者が決めるか、主の集合の外に置いて数えるかを書く。
  - 自信: 中

- [minor] 11. 第 1 著者の基準と AI の基準が「same criteria」と言えるかが検証できない
  - 位置と引用: GSRR-36「attachment 6 gives the same criteria as questions」。添付 6 の尺度開発の論文の E4 の規則や範囲の決定 (b) は GSRR-24・35 に無い。
  - 解消の条件: 第 1 著者も添付 6 の問いと規則で判断すると書くか、それらを GSRR-24 に登録する。
  - 自信: 中

- [nit] 12. 数字の照合から独立の確かめ手が消えた（GSRR-59）
  - 解消の条件: 限界に 1 語足すか、著者 2 に数字の照合だけを残す。
  - 自信: 中

- [nit] 13. 外枠の「the scheme reused」（outline.md 133–134 行）
  - 解消の条件: 他の人が同じように使えるかは試していないと添える。
  - 自信: 中

## 4. 総合の推奨
major（直して再査読）。E5 の連結の主体が変わったのに C5・RQ4 の文が元のまま。較正は記憶で膨らみうるのに改めた定義を確かめる回が無い。添付 6 のウェブの利用と感度分析 5 の欠けがある。どれも文の直しで済む。

## 5. 読めなかった範囲と注入の疑い
- 読んだもの: 差分の全文（1–629 行）、添付 6 の全文、context-A.md、carryover-R1.md。
- 登録版は Grep の所と 84–99 行だけ（GSRR-24・35・43 の C5 と GSRR-33 は確認）。外枠は 116–137 行と差分。main.tex と tables.tex は差分だけ。接地の 2 本は Grep の断片だけ。
- 注入の疑い: なし。

（注: メインが、意味を変えずに一部の箇条を詰めて写した。）
