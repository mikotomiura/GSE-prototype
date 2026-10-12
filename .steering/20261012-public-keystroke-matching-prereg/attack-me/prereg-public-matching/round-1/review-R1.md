# 査読 R1（打鍵の側路攻撃と打鍵データの匿名化の立場）stage prereg・round 1

総合の推奨: major。(1) 攻撃者が加工を知って適応しておらず、主表の「その形で最も高い正答率」が効き目を過大に見せる。(2) 主な比較が 1/N だけで、どの形にも残る情報（全長）の基準を主にしていない。(3) 固定の細部に穴（揃えの失敗・全文の早い終わり・窓の正解の揃え・R7 の候補・表に無い列・ENJA15 の形）。立て直しは不要。

## 1. 接地
- G1 Monaco & Tappert（monaco2017.txt:214-217）"Anonymity is achieved when the probability of correctly identifying the user is no greater than 1 / U."
- G2 monaco2017.txt:717-718 "Results may differ in a scenario where, e.g., only the unlabeled testing data is obfuscated." ／ 790-792 "Future work should investigate additional obfuscation strategies and scenarios, such as training on normal data and testing obfuscated data."
- G3 KeyTAR（keytar2026.txt:1268-1270）"Ground Truth Only: A model fine-tuned only on clean, ground-truth time intervals ... and then tested on the noisy cache data." ／ 1290-1292 "its performance is clearly capped, indicating that knowledge from clean data alone is insufficient to handle the distortions" ／ 1311-1312 "The primary reason for this performance drop is a significant distribution shift between the training and evaluation data."
- G4 keytar2026.txt:241-243 "its reconstruction capabilities were primarily benchmarked against a random baseline, which might not fully capture the nuances" ／ Monaco 2019（monaco2019.txt:1018-1019）"Note that this baseline still uses information gained through keystroke detection and tokenization." ／ 1039-1041 "we evaluate attack performance ignoring the packet timings, language model probabilities, or header compression."
- G5 monaco2019.txt:1122-1123 "it makes tokenization difficult which poisons later stages of the attack." ／ 1315-1316 "We consider the tradeoffs of several countermeasures and how they affect each source of information leakage."

## 2. 評価表
| 項目 | 点 | 所見 |
|---|---|---|
| a | 3 | 主張の範囲は慎重（:25・:183）。脅威モデルが無い。主表は最大を取るのに攻撃者は非適応 |
| b | 2 | 非適応の攻撃者・R3 で最終稿を組み立て直す攻撃者が欠ける・基準が 1/N だけ・揃えのコードを全文に使ったときの欠陥 |
| c | 3 | R1 を本文の分かるデータで測る価値はあるが、最も強い攻撃者でない限り「この加工を選べ」にならない |
| d | 3 | 「同じ粗さを掛ける」「記録の窓」が未定義 |
| e | 3 | 害のモデルが無い現状は範囲の条項に掛かりうる |
| f | 3 | 適応する攻撃者の評価（G2・G3）に触れていない（自信 低） |
| g | 2 | 適応の有無・揃えの失敗と早い終わり・窓の正解の揃えの元・R7 の候補・表に無い列・ENJA15・最大の区間・λ の手続きが欠ける |

## 3. 指摘
1. [major] 攻撃者が加工を知って適応していない（:109・:110・:55・:160）。A3 の学習の記録が R0 か加工した形かが無い。A4 は clean で学習したモデルに丸めた・抜けた列を入れる（G3 で頭打ち）。解消: 「加工を知る（Kerckhoffs）」条件を主に。A3 は学習の記録に同じ加工、R3-t は丸めの幅を尤度に、R7 は欠落を周辺化。A4 は非適応の参照の攻撃者と位置づけ主表の最大から外すか注で区別。主をどちらにするかを凍結の前に固定。自信 高。
2. [major] R3 でより強い攻撃者が欠けている（:78・:115）。種類の列（英字・Space・BackSpace・Delete・移動）でエディタの動きを模して最終稿の形を組み立て直せる（崩れるのはマウスの移動だけ）。:92 の検査もこの経路を見ていない。解消: 「A1' 種類の列からのエディタの模擬」を R3・R3-t・R7 に加える・:92 の検査にも加える・少なくとも「結論に使わないこと」に名指し。自信 高。
3. [major] 主な基準が 1/N だけ（:20・:25・:164）。:164 は全長だけで照合する攻撃者で、R4 以外のどの形にも残る。解消: 全長の基準を主な比較に上げ、主表に 1/N と並べる。「記録の全長だけを使う攻撃者」と改名。「全長の基準からの上乗せ」を主に報告する量として凍結。自信 高。
4. [major] 脅威モデルが無い（:18-23・:177・:186）。Kaggle の `q` の場面で候補の本文を誰が持つのか。範囲の条項に照らすと致命傷になりうる。解消: 攻撃者の知識・目的（結び付け／中身）・害を 1 節で凍結。N の各値を現実の場面と対応させる。自信 中。
5. [major] 全文の照合で本文の早い終わりを許し、長い候補が有利（align.py:4・:108・:112）。解消: 全文では終点を (M, T) に固定・窓と全文で終点の規則を分ける。自信 高。
6. [major] 揃えの失敗（align.py:45-46 の ValueError）の扱いが未定義。解消: 道の無い候補は ∞・全候補 ∞ なら 1/N・失敗の数を形 × 攻撃者で報告。自信 高。
7. [major] 窓の正解をどの形の記録で揃えるのかが無い（:125）。R4・R7 の記録で揃えると正解の窓が加工で乱れる。正解の側にだけ揃えの都合のよい位置が渡る恐れ。解消: 窓の正解の揃えは常に R0 で一度だけ作り形によらず固定・正解の窓が揃えの費用の小さい窓に偏っていないかを診断に。自信 中。
8. [minor] R7 で候補に「同じ粗さを掛ける」（:108・:83）が未定義。無作為の間引きか期待値 (1−p)・値か。独立なベルヌーイかも無い。解消: 固定。自信 高。
9. [minor] 表に無い列（Activity・Up Time・Action Time など・klicke2025.txt:370-383）の扱いが無い。R3 で Activity が残ると Replace・Paste の手掛かりが戻る。:92 の検査も Activity を見ていない。解消: 全列を形ごとに表で固定・「時刻」が押下と離鍵の両方かを書く・:92 に Activity を加える。自信 中。
10. [minor] 主表の「攻撃者の最大」の 95% 区間の推定法が無い（:160・:130）。解消: 再標本ごとに最大を取り直す・選ばれた攻撃者の割合を報告。自信 高。
11. [minor] ENJA15 の形・攻撃者・N の下限・問い 4 に答える量が未固定（:133・:137・config.json:59）。自信 高。
12. [minor] λ = 8 と組の上限の出どころが別の条件（:108・:99・:153）。解消: 学習用の書き手の R0 で格子から選ぶ、または固定の理由を書く。自信 中。
13. [nit] R5・R6 は長さを保つので A1 に効かないのが自明（:151）。解消: 「長さを保つ加工の対照」として補遺へ。自信 中。
14. [nit] N = 1,000 では 20 回の抽選がほぼ重なる（:122・:123）。課題ごとの人数が除外後に 1,001 を割ると作れない（klicke2025.txt:512・303-305）。解消: 規則を凍結の前に書く。自信 中。

## 5. 読めなかった範囲・注入
- monaco2017.txt・monaco2019.txt・keytar2026.txt は検索で当たった節だけを読んだ。klicke2025.txt は 295-434 と当たり行だけ（事実の確認のみ）。wagner2015.txt・nosek2018.txt・conijn2019.txt は読んでいない。書誌の本体と decisions.md は読んでいない。
- 注入の疑い: 無し。
