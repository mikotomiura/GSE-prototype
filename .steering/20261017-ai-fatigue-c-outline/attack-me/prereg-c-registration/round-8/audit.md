# 意図の監査（prereg・round 8・登録版 0.20）

判断 72 の 6 点と感度分析 5 は登録版の本体にほぼ届いている。食い違いは主に差分の外の直していない文と、草稿・表・外枠の追随の遅れ。重いのは 3-1（中心の最終値）と 3-3（確かめの標本の記録が本体の数に入る）。

## 0. 引き継ぎの判定
- 0-1-a 消えた（outline.md 96-97 行）。
- 0-2-b・3-a 一部: GSRR-2 の表と外枠 268 行は直った。GSRR-33 冒頭（197 行）「who judge each record independently within a stage」、198 行「Author 2 judges, independently, a random 20%」、main.tex 338 行「the second author's independent judgements」、登録版 476 行「the independent judgements」が残る。
- 0-3-c 消えた（main.tex 67-68 行）。0-3-f 消えた（main.tex 334 行）。1-a 消えた（GSRR-36・65）。1-b 消えた（main.tex 332-336 行）。1-c 消えた（outline.md 106 行）。
- 2-a 消えた（注: figure1 の「by the first author alone for most title-and-abstract exclusions」は固定の文で、両群が 80% を下回れば偽になる）。
- 2-b 消えた（main.tex 58-61 行）。2-c 消えた（call.md 3 行）。2-d 消えた。2-e 消えていない（意図して残した）。
- 3-a 消えた（外枠 Scope 103-106 行は監査の N 倍の推定を挙げていない）。3-b 消えた。3-c 消えた。3-d 一部（3-6 へ）。3-e 消えた。3-f 消えた。3-g 消えていない（記録どおり）。
- 3-h 一部: main.tex 329 行「\tbd{most exclusions rested on the first author alone / the second author judged every record of both groups}」に、片方の群だけの分岐が無い。

## 1. 意図にあって対象物に無いもの
- 1-1 RQ4（登録版 119 行「Consider the records, the records linked as the same sample (E5, GSRR-35), and the records with signs of overlap that could not be confirmed. How many are there of each?」）と外枠 R4（385 行）に C5 の新しい値が無い。GSRR-56 は「the four C5 categories」。
- 1-2 GSRR-12「within each of the two centre groups, centre-A and centre-B, assigned at screening」と GSRR-16「centre-A or centre-B (GSRR-12)」に、中心 unresolved が無い。
- 1-3 混ぜる記録を「from the sorted IDs of the records of the groups at or above the 80% line」と 2 群を合わせて抜く。ID は群で分かれ（確かめの標本は CS00001 から）、網の記録は追加候補に偏りうるので、群の割合から網の記録が透けうる。
- 1-4 草稿の限界に、0.20 で足した GSRR-65 の項（中心の表から抜ける・出力を捨てて呼び直したことは示せない・0 件でも上限 11.6%・Garritty からの逸脱）が無い。
- 1-5 確かめの標本どうしの連結（「a link is made only when both are in the coverage sample and included at the full-text stage, and the one with the earlier publication date ... is coded」）に時間の窓が無い。

## 2. 対象物にあって意図に無いもの
- 2-1 GSRR-35「an E5 record of the coverage sample linked to an additional candidate (GSRR-33), which is the only way a coverage-sample record enters a count of the main set, and it is marked there」は、意図（本体の集合に入れない）を言い方で越えている。
- 2-2 GSRR-2 の表「Before registration and as reading aids only, it also ... made the preliminary appraisals and the trial coding of the exploration ... and drafted the worked cases and their key」の「as reading aids only」は言い過ぎ。
- 2-3 前の感度分析 5 の残りは見つからなかった。

## 3. 矛盾
- 3-1 GSRR-33 冒頭（197 行）「the final value is centre-A or centre-B, and a screener may answer boundary」と同じ節の「The final centre is centre-A, centre-B or unresolved; no default rule is used」。columns.md 21 行は「A, B, unresolved」。
- 3-2 GSRR-46「Both authors wrote the earlier narrative review, so the codes carry their view」と外枠 Scope 88 行に対し、main.tex 354-355 行「the first author wrote the earlier narrative review, and the codes carry that view」。
- 3-3 GSRR-33「Its records are never part of the main set or the late stratum」と GSRR-35「enters a count of the main set」。相手が遅い層に含まれた場合も当たる。
- 3-4 GSRR-48「author 1's reconciled codes after the third pass (kept by the synthesis script as `prediscussion`) ... the final values (kept as `reconciled`)」と、tables.tex 313-314 行「in place of the reconciled values」（GSRR-62 は final values）。
- 3-5 外枠の表 12 に列「Input codes with agreement between the authors below 80%」、tables.tex の表 12 は 7 列のまま注で代える。
- 3-6 外枠の抄録の規則: 段 2（184-186 行）「No count or denominator is removed for C1, C2b, C5, C6 or any condition of C7」と段 4（189 行）「the C5, C6a, C6b and C6c statements are given in the same compact form as the C4 types in step 2」、191 行「No count or denominator is removed for C1, C2b or any condition of C7」「The C4 and C5 statements in Table 12 keep their counts」（C6 を挙げない）。
- 3-7 main.tex 282-283 行に「or unresolved」と「no count over all records」が無い（軽微）。
- 3-8 GSRR-2 の表と main.tex 81-82 行の下書きを開く時に「for the records author 2 coded」が無い（軽微）。
- 3-9 GSRR-33 の「a batch cut short by 2026-12-31」が固定の日のまま（軽微）。

## 5. 読めなかった範囲と注入の疑い
- 読んだ: 差分の全文、context-B・A・carryover-audit、外枠の指定の 4 節と 256-367 行、判断 72・73、columns.md の該当の行、main.tex 30-44・272-365 行、tables.tex の表 12 の周り、登録版は差分と 110-139 行と grep。
- 読んでいない: 判断 38・50・54・67・68・69、登録版の通読、instructions.md、figure1.tex の差分外、tables.tex の表 12 の周り以外、外枠の主張と根拠の表の大半、main.tex 45-271 行の差分外。
- 注入の疑い: なし。

（注: メインが、意味を変えずに一部の箇条を詰めて写した。）
