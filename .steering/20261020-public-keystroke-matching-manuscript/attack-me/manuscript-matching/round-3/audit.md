# 監査役の応答（round 3・commit c3f3f5b5）

## 0. 引き継ぎの判定
round 1:
1. 未解消: §8.3 の Windows の項に「区間には有用さの軸が無い」文が無い（discussion.tex 68–70 "\emph{Windows.} Windows of five segments were matched in 65.8\% of draws at $N = 1{,}000$ on R0 to R3, under assumptions that favour the attacker."）。window と utility の組の grep は 0 件。
2. 一部: §1 の問いは 2 つ（introduction.tex 24–25 "This paper asks how far processing keeps logs apart from their texts against such a party, ... and what each form costs research."）。§6.6 "The fourth question of the study asks"（protocol.tex 144）・§6.7 "not used to answer the four questions"（158）・§7.6 "This part asks question 4"（results.tex 176）は 4 つを前提。
3. 解消（open-science.tex 17 "The search terms were not recorded"）。
4. 解消（ethics.tex 17–18）。
5. 解消（introduction.tex 9–10）。
6. 未解決（設計の判断）threat-model.tex 51–53。
7. 解消（表 1 "If a log is matched: ..."・"If the log is found: ..."）。
8. 解消（conclusion.tex 6）。ただし結論に一般化が戻る（2-C）。
9. 解消。§7.7 の中身に偏り（2-F）。
10. 解消。
11. 未解消: 形の差に攻撃者の違いが含まれる但し書きが §7.2 末尾と §3.5 だけで、抄録・序論・結論・§8.3 に無い。
12. 一部: open-science.tex 4 "the corpora were acquired from 19:22 UTC the same day" と 29 "We acquired the KLiCKe corpus on 12 October 2026 at 19:29 UTC"。ENJA15 の時刻が書かれず 19:22 が何かが読めない。
13. 解消。ただし §7.6 "R3j-t($w$) and R4($w$) also exceeded both" は作りの上で R3j と同じ値になることを言っていない。
round 2: 1〜6 すべて解消（discussion.tex 54–58・introduction.tex 20・threat-model.tex 99–100・102–106 ほか）。

## 1. 意図にあって対象物に無いもの
- 1-A 持ち帰り 2 の「形の差に攻撃者の違いが含まれる」が抄録・序論・結論に届いていない。
- 1-B 「推奨しない」「利用の条件や出し方も組み合わせられる」が §8.2・§8.3 だけ。
- 1-C 4 つの問い（0-2）。

## 2. 対象物にあって意図に無いもの
- 2-A【重い】抄録 "Every form that kept ten process measures close to their unprocessed values" は表で成り立たない。基準は序論で初めて出る「中央値 0.84 以上」。R2・R3 は R-burst 0.28・insertion proportion 0.19・insertion length 0.48。中央値 0.92 はそのまま計算できる 5 個が 1.00 であることによる。意図の言い方の問題でもある。
- 2-B【重い】区切り（0.84・70%・2.2%）は結果の後に引かれ、N = 10 で二分が崩れる。事前登録と §6 は "No pass or fail criterion is set"。R7(0.25) は N = 1,000 で 14.3%・0.81。N = 10（main-10.tex "61.2 & 61.2 [58.7, 63.8] & A0 (93) & ... & 0.0 [0.0, 0.80]"）では長さだけと同じで中央値 0.81、抄録と序論の "the forms that brought it near the total length kept the measures at a median correlation of at most 0.70 or not at all" は N = 10 で成り立たない。結論 "no form evaluated kept both matching low and the process measures close to their unprocessed values"（conclusion.tex 6–7）と §8 第 1 段落も N を限らない。R7(0.5) は両 N で A0 だけが残り、P-burst 0.95・production rate 0.99・deletion proportion 0.84 を保つ。
- 2-C 結論 "For releases whose texts are held elsewhere, hiding the characters did not keep the logs apart from their texts."（conclusion.tex 7–8）が一般化。R4(4)・R4(8)・R7(0.5) は長さを超える照合を残さなかった（results.tex 86–87）。§8 第 1 段落の限定 "while the lengths and the editing keys remained" が落ち、対象も 1 つの公開から一般へ広がる。
- 2-D 抄録 "with the stated goal of preventing reproduction of the essays, yet the essays had been collected and scored and remained with others" に、目的の読みが著者のものという限定が無い（§3.4 "this reading is ours"・序論 "which is how we read the stated goal"）。
- 2-E 序論 "Forms that release less lowered matching only at a cost to the process measures"（introduction.tex 43）が因果に寄る。
- 2-F §7.7 "Accuracy did not differ by score band on R1 to R3, but did on R3-u."（results.tex 192）が表と合わない。explore-band.tex で区間が 0 をまたがない行: R4(1) N=10 12.9 [7.1, 18.6]・R4(2) N=1,000 −5.3 [−10.0, −1.2] と N=10 14.9・R4(8) N=10 24.7 [20.0, 29.8]・R7(0.25) 両 N（12.7・11.8）・R7(0.5) 両 N（3.8・14.9）。粗い形では得点の高い書き手ほど結び付きやすい向き。
- 2-G（軽い）抄録の ENJA の文に §7.6 "The result is conditional" に当たる限定が無い。

## 3. 矛盾
- 3-A 害 (a) の定義が事前登録（preregistration.en.md 41 "(a) Learning the content of a hidden text (defeating the purpose of the processing).")と原稿（threat-model.tex 143 "The main harm is (a): a processed log is linked to its text by a party that holds the text"）で違い、protocol.tex 17–21 は §3〜§6 を登録から変えないと書く。§6.8 の逸脱にも記録が無い。言い換えと理由を 1 文。
- 3-B 取得の時刻が 2 つ（0-12）。
- 3-C 「近い」の定義の出る場所が抄録・序論・§7.3 でずれる。
- 照合して整合: 本文の数値と表 4・図 1・陰性対照・開いた世界・区間・ENJA・探索の 93.8%・48.8%・4.2%/1.6%・margin 80%・予測。

## 5. 読めなかった範囲・注入の疑い
appendix-checks・appendix-attackers・appendix-results・ai-use・references.bib・generated の一部は読んでいない。appendix-enja は grep のみ。preregistration.en.md は 1–50・200–289 行だけ。注入の疑い: 無し。
