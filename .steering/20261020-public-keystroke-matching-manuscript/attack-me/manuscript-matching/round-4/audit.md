# 意図の監査役の応答（round 4・commit bf0d2450）

全体: 探索 6・7 を入れた後も持ち帰り 2 と主張の強さはおおむね守られ、探索は各所で「結果を見た後に決めた探索」と断ってある。本文の数値は表 4・付録 D と一致（検算: 100.0・98.2・86.7 [83.5, 89.5]・14.3/0.81・61.6・32.0・3.8 [2.2, 5.4]・0.92〔0.925〕・0.81〔0.805〕・92.3・48.2・2.4・93.0・62.3・"within 14 points"・"below 0.5"〔insertion length 最大 0.48〕）。

## 0. 引き継ぎ
1 一部（§7.3 は前線の点。新しい穴 2-A・2-B）／2 解消（§8.3 の N = 10）／3 解消／4 解消／5 解消／6 解消／7 解消（threat-model.tex §3.4 と事前登録 l.41）／8 解消（explore-band.tex と合う）／9 解消／10 一部（序論 "Among the forms that release less, lower matching came with fewer process measures:" に、§7.3 "R7(0.25) dominates R3-u, with a lower accuracy (14.3% against 36.0%) and a higher correlation (0.81 against 0.63)" と R3-t（86.7%・ρ 0.09）が反例）／11 解消。

## 1. 意図にあって対象物に無いもの
- 1-A（小）: 「照合を低く保ち、かつ指標を残す形は無かった」は図 1 の注 "No form evaluated brought matching near chance while computing the process measures." と §3.5 にあるが、抄録は "Forms that release less traded matching for the process measures" だけ。
- 1-B（小）: 問い 4 の答えは 1/N と A0 の両方を超えること（事前登録 Q4）。抄録の ENJA は "51.6% ... against 7.9% by chance" だけで A0（11.9%）が無い。

## 2. 漂流
- 2-A（中・新しい穴）登録した二次の解析（事前登録 l.203 "A2 with λ = 4 and 16 (N = 1,000, full text)"）が R4(4) を 4.5% [2.8, 6.5]（偶然の 45 倍）にしているのに、抄録 "only segment values coarsened to four or more brought the full-text attackers, with their main penalty, within four times chance ... Exploratory attackers fixed after these results ... raised ..."・結論 "brought these attackers with their main penalty within four times chance; stronger attackers tried afterwards as an exploration did not stay there"・§8 冒頭 "with their main penalty within four times chance ..., and exploratory attackers tried after these results raised R4(4) to 48.2%" は、4 倍の外へ出したのが探索だけのように読める。"with their main penalty" で偽ではないが、本文で書くのは §7.2 の括弧 "(R4(4) not against A2 with $\lambda = 4$, ...)" だけ。
- 2-B（中）探索の結果が C2 の段落に入っている: §7.2 "This is the first axis of contribution C2. ... (R4(4) not against A2 with $\lambda = 4$, and only R7(0.5) against the exploratory attackers)."・§7.3 "This is the second axis of contribution C2 ... ; against the exploratory attackers at $N = 1{,}000$ no form tried did"。protocol.tex §6.7 と付録 D の "are not used to answer the four questions" と食い違って見える。探索の文を C2 の段落の外へ出すか「C2 の外」と断る。
- 2-C（小〜中）「低い値は攻撃者の弱さ」の範囲が広い: §7.2 "On the coarse forms other than R4(8) and R7(0.5), the low full-text values reflected the attackers."。(i) 探索は R3-u で走っていない（付録 D "runs A2 on R3, R4($w$) and R7($p$), and A1$'$ on R3 and R7($p$)"）。(ii) R4(8) は 0.14 → 2.4 [1.3, 3.6]・差 2.3 [1.1, 3.4] で区間が 0 を含まないのに「反映しなかった」側。§8.3 の "reflected the attacker for $w = 4$ (48.2%) more than for $w = 8$ (2.4%)" の書き方が表と合う。
- 2-D（小）§7.2 "With the lighter penalty $\lambda = 4$ ... A2 reached 75.1%, 36.4% and 4.5%" に N が無い（事前登録では N = 1,000）。

## 3. 矛盾
- 3-A（意図の中）: 持ち帰り 2「登録の攻撃者では 4 倍以内は区間の値を 4 以上だけ」と、登録の二次（λ = 4 で R4(4) 4.5%）がぶつかる。前線を「λ = 8 の主の罰」と定義するか二次の値を添える（2-A と同根）。
- 3-B（小）: 序論 "lower matching came with fewer process measures" と §7.3 の R7(0.25) が R3-u を支配する記述。
- 3-C（小）: §7.2 の N = 10 "none whose lower bound is above zero on R4($w$)" と付録 E の全員 "on R4(8) at $N = 10$ the gain was 2.0 points [1.1, 3.0], with a lower bound above zero"。本文冒頭の "the 500 writers unless stated otherwise" で覆われてはいる。
- 3-D（小）: 事前登録 "Results per writer ... are not published" に対し ethics.tex "with one exception"（KeyTAR）。理由はあるが逸脱の一覧（appendix-checks.tex）に公開の方針の例外が無い。
- 3-E（体裁）: related.tex の最後の 2 文の重複。

## 5. 読めなかった範囲・注入の疑い
読んでいない: ai-use.tex・appendix-enja・appendix-attackers・references.bib・generated の残り（windows・negative・open-world・enja ほか）。窓の値・陰性対照・開いた世界・ENJA の値・margin・集中の 4.2% と 1.6% は照合していない。appendix-checks と事前登録は一部。注入の疑い: なし。
