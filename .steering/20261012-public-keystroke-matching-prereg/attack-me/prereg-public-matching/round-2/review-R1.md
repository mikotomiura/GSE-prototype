# R1 査読 round 2（打鍵の側路攻撃と打鍵データの匿名化の立場）

## 1. 接地
- G1 monaco2017.txt:213-217 "the user wishes to remain anonymous within a pool of U users. Anonymity is achieved when the probability of correctly identifying the user is no greater than 1/U."
- G2 monaco2017.txt:717-718 "Results may differ in a scenario where, e.g., only the unlabeled testing data is obfuscated." ／ :790-792 "Future work should investigate additional obfuscation strategies and scenarios, such as training on normal data and testing obfuscated data."
- G3 monaco2019.txt:993-995, 1017-1019 "compare this to a baseline attack in which the timing and language model probabilities are ignored" ／ "Note that this baseline still uses information gained through keystroke detection and tokenization."
- G4 monaco2019.txt:1315-1316 "We consider the tradeoffs of several countermeasures and how they affect each source of information leakage." ／ :1323-1324 "padding may not be effective to mitigate keystroke detection and does not provide any protection against a timing attack."
- G5 keytar2026.txt:241-244 "its reconstruction capabilities were primarily benchmarked against a random baseline, which might not fully capture the nuances of more sophisticated reconstruction challenges."
- G6 keytar2026.txt:1370-1376 "input reconstruction is extremely sensitive to the accuracy of retrieved inter-keystroke timings. Making matters worse, detection errors propagate to consecutive detections ... future defenses could use our findings and datasets to determine the appropriate amount of noise to inject in a principled manner."

## 引き継ぎの判定（14 件）
解消 9（#2・#3・#4・#9・#10・#11・#12・#13・#14）。一部 5: #1（R3-u で A3 が使われない・R7 の適応は (1 − p) 倍だけで揃えの構造が抑制に耐えない）・#5（align.py は窓の終点のまま・全文の版の実装が別に要ることを書いていない）・#6（正解だけが ∞ の場合を分けて数えない・R7 では構造上ほぼ全候補が ∞）・#7（R3-u・R7・R4 で「k 区間」をどの区間の列で数えるかが未定）・#8（区切りが落ちて区間が併合されることを扱っていない）。

## 2. 評価表
a 4（R7 の予測が揃えの構造が生む見かけの値で当たるおそれ）／ b 3 ／ c 4 ／ d 3（README.md:6 の判断の範囲が古い）／ e 4 ／ f 4 ／ g 4（R7 の群の上限・窓の区間の数え方・A4 に渡すイベント・A4 が縮んだときの主の表の n が未固定）

## 3. 指摘
- [major] R7 では区切りの押下の抑制で揃えが構造上ほぼ必ず切れる（prereg:118 の 5 通り・:120 の全文の終点の固定・:131・:132・:197）。区切りが 3 つ続けて落ちると記録の 1 区間が本文の 4 区間以上に当たり (1,3) が上限の群では通れない。語数 400 の概算で期待個数は p = 0.5 で約 25、p = 0.25 で約 5、p = 0.1 で約 0.4。全候補が ∞ → 1/N の同点。R7 の最も強い攻撃者は事実上 A0 になり、:197 の予測は揃えの実装の制約で当たる。解消: (i) R7 では群の上限を p に応じて広げる（式を書く）(ii) 抑制を明示した確率モデルの DP (iii) R7 だけ終点を自由に。あわせて「全候補 ∞」「正解だけ ∞」を分けて報告・合成の記録で R7 の正解の道が切れる割合を本計算の前に確かめる。自信 高。
- [major] R3-u で A3 が外れている（:134・:133・:196）。A2-b は区切りを局所の分類器で決め打ちするので誤りが波及する（G6）。R3 − R3-u の片側の攻撃者が弱いと「区切りを消すと効く」が過大になる。解消: A3 を R3-u に広げる（「字」の並びを候補の文字の並びと 1 対 1 に揃え、文字の組の間隔の対数尤度を足す）か、当てない理由を書き予測と対比に添える。自信 中。
- [minor] 窓の「k 区間」をどの区間の列で数えるかが形ごとに未定（:148・:151）。解消: 窓は R0 の区間で定め、その窓に含まれる押下だけを各形で取り出す（形の間で同じ始まり）。自信 中。
- [minor] おとりが学習用の書き手の本文を含み脅威モデルと食い違う（:145・:30）。解消: おとりを評価用に限るか、除外する版を副次に。自信 中。
- [minor] 型の align.py は全文の終点の固定を実装していない（align.py:2-5・41-44・prereg:120）。正解だけが ∞ の数が紛れる。解消: 全文では end_j = T に固定した版と書く・「正解が ∞・おとりに有限がある」場合の数を別に報告。自信 高。
- [minor] A4 に渡すイベントの種類と、A4 が縮んだときの主の表の n が未固定（:135・:137・:250）。KeyTAR は "standard English input" を前提（keytar2026.txt:1378-1379）。解消: A4 に渡すのは英字・数字・Space の押下の間隔だけ・A4 を減らしても主の表は 500 人のまま（または逆）。自信 中。
- [nit] R3-t は A0・A1'・A2 では構造上 R3 と同じ値（:90・:161）。注に書き、時刻の対比は A3 の差でも出す。自信 高。
- [nit] README.md:6「判断 6〜15」が古い。

## 4. 総合の推奨: major
14 件のうち 9 件解消・5 件一部。R7 の群の上限は最も強い攻撃者を構造上偶然の水準へ落とし予測を見かけ上当てる。直し方は設計の選択なので直した後に再査読したい。R3-u の A3 も対比の片側を弱くする。2 件を直し minor を 1 文ずつ固定すれば凍結してよい。

## 5. 読めなかった範囲・注入
接地の 3 本は grep で拾った箇所と前後だけ。書誌の本体・romaji_table.py・decisions.md・context-B.md・他の査読者の記録は読んでいない。注入の疑い: なし。
