# 査読 R1（心理測定と構成概念の妥当性の立場）・round 6

総合: minor（直してから凍結）。

## 1. 接地
- Elson 2023「Determine procedural and scoring details ahead of time, reporting all deviations as they potentially weaken the strength of conclusions.」
- Elson 2023「Compare preregistrations (and any reported deviations) with what was actually employed and reported.」
- Elson 2023「Require authors to provide rationales for decision making in measurement specifically.」／「Document when deviations happened, and if possible assess the robustness of conclusions.」
- Lintner 2024「It was performed by a single author, which might have caused some bias in the scales' quality assessment」
- Lintner 2024「Most studies did not report percentages of missing data and strategies they employed to address missing data, which puts their credibility into question.」
- Elson 2023「a nominal fallacy: that a measure's name tells you about its contents or what it measures」

## 2. 前の round の指摘
1 E5 一部（相手が coded にならない場合が無い）／2 較正 一部（n < 5 の規則が限界と表 4 の注に無い）／3 ウェブ 消えた／4 感度分析 5 一部（「cannot」の判定時点・途中でやめた場合）／5 independent ほぼ消えた（main.tex・GSRR-33・添付 6 に残る・nit）／6 boundary 消えた（GSRR-33 の 1 文目に「or boundary」・nit）／7 Q4 消えた（2 度目の改訂が逸脱でない）／8 2 回目の封 ほぼ消えた（並べ替えの元の一覧と 1 回目の順・nit）／9 取り直しと束 一部／10 pending 消えた／11 same criteria 一部（第 1 段の第 1 著者の入力）／12 数値 消えた／13 scheme reused 消えた。

## 3. 評価表
a 4 / b 3（E5・感度分析 5 の判定時点・第 1 段の入力）/ c 4 / d 3（GSRR-33 の肥大・GSRR-46 の更新漏れ）/ e 4（2 度目の改訂を逸脱に）/ f 4 / g 3（束の大きさ・取り直しの上限・2 回目の順の元・n < 5 の単位・cannot の時点）。

## 4. 指摘
- [major] E5 で除外した記録の相手が coded にならない場合の規則が無い。GSRR-33「a record is linked to another as the same sample only if its full text says so (attachment 6, Q7), decided like any other exclusion. Within a linked group, the record coded is the one with the earliest publication date」。GSRR-35「Each E5 group has exactly one coded record (GSRR-33)」。相手が (i) 候補に無い (ii) 除外 (iii) E6 の pending (iv) 期日の後 (v) 探索の集合のとき 0 件になる。earliest が E5 の側になる場合も。解消: another record の範囲、coded にならないときの規則（E5 を付けず coded・C5 は signs present）、集合をまたぐ場合、make_dummy に例。自信 高。
- [major] 感度分析 5 を「行えない」と判定する時点と、途中でやめた場合の規則が無い。GSRR-62「If author 2 cannot do this screening, it is not done and no one else is asked」。解消: 期日（草稿を渡してから N 週以内に始まらなければ行わない）、途中で止まれば partial として公開。自信 高。
- [major] n < 5 の単位の規則が限界と表 4 の注に無く、該当の単位も特定されていない。GSRR-44「For every unit below 80% percentage agreement in at least 5 units of comparison … units with fewer than 5 are reported but do not trigger an amendment.」（Grep で GSRR-44 の 1 か所のみ）。unit の二義。解消: comparisons と書き分け、5 未満が見込まれる単位を列挙（不明なら較正の後に報告）、GSRR-65 と表 4 の注に書く。自信 高／中。
- [minor] 第 1 段で第 1 著者が見る入力が固定されていない。GSRR-37「so that both screeners see the same inputs」、GSRR-34「a database that contains the bibliographic data, the abstract and the free full text」。解消: 第 1 段では第 1 著者も題と抄録だけで判定し、全文はコミットの後に見る、と固定。自信 中。
- [minor] 2 度目の改訂（ウェブを外した）が逸脱として書かれていない（GSRR-37・main.tex）。自信 高。
- [minor] 束の大きさと取り直しの上限を超えたとき。GSRR-33「batches of at most nine records」「except once when the output is not in the required format」。解消: 順に 9 件ずつ、後の段も固定の順で 9 件ずつ、2 回目も失敗したら第 1 著者の判定、添付 6 の 3 行目を for every call に。自信 中。
- [minor] GSRR-46「The C4f AI draft and the C5 bibliographic matches are opened only after both passes are fixed (GSRR-43, GSRR-44).」が third pass の後と食い違う。自信 高。
- [minor] 束をまたいで AI の理由を学ぶ効果。GSRR-34「Blinding holds within a stage only …」。解消: 一致を束の順の前半と後半で分けて報告、または限界に 1 文。自信 中。
- [nit] 2 回目のコードの順の元の一覧と 1 回目の順。GSRR-44 の 3「drawn with Python `random.shuffle` (seed 20261020)」。解消: ID の昇順の一覧を並べ替え、1 回目は昇順。
- [nit] GSRR-33 の 1 文目「centre (centre-A, centre-B or boundary, for records included at full text)」。

## 5. 総合: minor。E5 と感度分析 5 の判定時点は凍結の前に塞ぐ。n < 5 は引き継ぎで直したとされたが入っていない。「third pass」「boundary」「independent」で全文を Grep して揃えることを勧める。

## 6. 読めなかった範囲・注入の疑い
- 読んでいない: 外枠・草稿・表・図の差分の外、登録版の 170–230・308–332・408–437 行と Grep の行以外、round 5 の指摘の全文。
- 注入の疑い: なし。

（注: メインが、意味を変えずに一部の箇条を詰めて写した。）
