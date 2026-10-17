# 査読 R2（HCI の測定の実務の立場）・round 6

総合: minor（直してから凍結）。

## 1. 接地
- Perrig 2024:236-240「researchers should share the exact wording of the items they used in their research ... Sharing the items used allows readers to judge which version of a scale was employed, if or how items were adapted」
- Perrig 2024:155-158「if there is little to no information on how a scale was employed in a study, it can be hard, if not impossible, to judge the validity of the scale and the study as a whole. Thus, the absence of transparency hinders the identification and the prevention of QMPs」
- Perrig 2024:192-195「we can provide clear recommendations addressing the identified issues, helping future research use survey scales with even more potential」
- Perrig 2024:74-77「papers rarely contained complete rationales for scale selection (20.00%) ... only one-third of papers reported any scale quality investigation (36.67%)」
- Bach 2022:260-262「Group consensus was used throughout the article selection process to resolve any disagreements regarding eligibility. …」
- Bach 2022:1025-1027「Of the 16 studies, 12 (75%) developed their own questionnaires」

## 2. 評価表と引き継ぎ
a 4 / b 3（E5 の衝突・書式の確かめと盲検の順序）/ c 4 / d 3（GSRR-33 の詰め込み）/ e 4（2 度目の改訂）/ f 4 / g 3（境界の決め方・取り直し 2 回失敗・後継のモデルが線を割ったとき・束の包みのプロンプトと設定）。
引き継ぎ: 1 boundary 一部／2 AI の入力・束・文脈 一部／3 較正 消えた／4 感度分析 5 消えた／5 E5 一部／6 符号と pending 一部／7 合格の線と Q4 一部／8 数値 消えた／9 一致の読み方 消えた。

## 3. 指摘
- [major] E5 の「最も早い記録を符号化する」と Q7 の「そう書いている記録を E5 で除く」が衝突し、"exactly one coded record" が崩れうる（GSRR-33・Q7・GSRR-35）。解消: Q7 が yes なら群の早い記録を残し遅い記録を E5（Q7 は連結の判定）、相手が候補の外・除外・保留なら符号化し C5 を signs present などに、集合をまたぐときの扱い。自信 中。
- [major] 束の書式の確かめと盲検の順序、取り直しの規則の自己矛盾。GSRR-33「author 1's judgements are committed ... before the AI screener's output for that batch is opened」「except once … the first output in the required format is used and the number of re-runs is reported」。解消: 書式の確かめはスクリプトの JSON 検証だけで中身を表示しない、AI の実行はコミットの前か後か、取り直しは最大 1 回で合わなければ第 1 著者だけで判定し件数を報告。自信 中。
- [minor] 2 度目の改訂（ウェブを外した）も逸脱と書く（GSRR-37・main.tex:184-185）。自信 高。
- [minor] 境界を A か B に決める規則が無い（GSRR-33・添付 6）。解消: 既定の規則を登録、または境界の記録の ID と振った先を公開（GSRR-41・64）。自信 中。
- [minor] 束の包みの文とモデルの設定が固定されていない。instructions.md:3「This text is given, unchanged, to the AI screener for every record」。解消: 包みの文の雛形と SHA-256・呼び出しの設定を [at registration] として添付 6 に、冒頭を for every batch に。自信 中。
- [minor] 全文の段の保留が E6 と遅い層とぶつかる。GSRR-33「decided by author 1 as include, exclude or pending; a record still pending on 2026-12-31 is outside the main set」、GSRR-65「Records without one stay pending (E6) and are not coded」。図 1 の遅い層への矢印は unscr からだけ。解消: 無料の全文の無い記録は E6 の保留のままと明記、12-31 の後に解けて include になれば遅い層、図 1 に矢印。自信 中。
- [minor] 表 1 の C5 の値が古い。tables.tex:26「Same sample by the source database (E5 group)」。自信 高。
- [nit] 後継のモデルが線を割ったときは advisory only を当てる。
- [nit] 「著者 2 が行えない」を決める時期。
- [nit] GSRR-44 の参照先を GSRR-47 に。

## 4. 総合: minor。重いのは E5 の衝突と書式の確かめと盲検の順序。どちらも文で固定できる。

## 5. 読めなかった範囲・注入の疑い
- 読んでいない: 登録版の GSRR-33〜39・62〜65 と grep の行以外、草稿・表・図・外枠の差分の外、接地の大半。
- 注入の疑い: なし。

（注: メインが、意味を変えずに一部の箇条を詰めて写した。）
