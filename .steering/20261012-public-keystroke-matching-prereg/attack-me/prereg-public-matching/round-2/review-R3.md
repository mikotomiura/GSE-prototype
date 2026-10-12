# R3 査読 round 2（プライバシーの評価の指標の方法論と、事前登録・再現性の立場）

## 1. 接地
- G1（wagner2015.txt:196-200, 206-207）"evaluating a PET with a weak adversary model can lead to an overestimation of privacy." / "metrics can only be used to compare two different PETs if they use the same adversary model." / "studies should always include a detailed description of the used adversary model."
- G2（:225-226）"Prior information can considerably strengthen the adversary, and thus it is important that privacy metrics can account for it."
- G3（:127-128）"privacy metrics should be monotone with increasing adversary strength"
- G4（nosek2018.txt:96, 99）"the analytic pipeline is specified before observing the data." / "selection of tests is not influenced by the observed data, and all conducted tests are knowable."
- G5（:111）"The decision tree defines the sequence of tests and decision rules at each stage of the sequence." / "it is possible to preregister biases into decision trees."
- G6（:115）"transparently reporting what was and was not known in advance about the dataset."

## 2. 引き継ぎの判定（round 1 の 12 件）
| # | 判定 | 理由 |
|---|---|---|
| 1 組の集合 | 解消 | prereg:118 と config・align.py:8 が一致。同点の規則も align.py:37-38・42-44 と合う |
| 2 末尾と経路 | 一部 | 文は直ったが align.py は窓の終点しか持たず ValueError を投げる。包みは新しいコード（m3） |
| 3 窓の正解 | 一部 | 循環は切れた。最終稿と配布の本文が一致しない書き手で語への写し方が無い（M4） |
| 4 敵の模型 | 解消（一点を除く） | 学習用の組をおとりの集め方が打ち消す（M2） |
| 5 n | 一部 | 分岐は入った。500 人・抽選回数・窓の始まりの精度の根拠と ENJA15 の推定の単位が無い（M5） |
| 6 出力 | 解消 | :162 |
| 7 最大の偏り | 解消 | :160。点推定の上振れは安全側で :235 により許容 |
| 8 第三者の登録 | 一部 | 英語の版と日本語の版のどちらが正かが無い（m4） |
| 9 乱数と版 | 一部 | Python・numpy・ロジスティック回帰の版と正則化・KeyTAR の推論の既定値・writer の文字列の形が無い（m5） |
| 10 除外 | 一部 | ENJA15 の除外規則が無い（m6） |
| 11 A0 | 一部 | R4 の尺度が合わない（M3）・窓の A0 が無い（M1） |
| 12 λ | 解消 | :16・:118・:162 |

## 3. 評価表
a 4（問い 4 の「上回るか」に判定規則が無い・M6）／ b 3（陰性対照の設計・おとりと模型・R4 の A0）／ c 4 ／ d 3（攻撃者 × 窓の手順が追えない・README:6 の判断の番号）／ e 4（AI 使用の節の材料が無い・予測が「Claude の予測」・m7）／ f 3 ／ g 3（窓での手順・問い 4・ENJA15 の単位）

## 4. 指摘
- [major] M1 窓の範囲で A0・A1・A1'・A3 が何をするかが未定（:159・:130・:135）。解消: 攻撃者 × 範囲の表に窓での入力を 1 行ずつ・行わない攻撃者を明記。自信 高。
- [major] M1' 陰性対照（:204）は、入れ替えた記録の書き手 B の本文がおとりに入りうる（:145 は A だけを除く）ので 1/N より下に出る。解消: B の本文もおとりから除く、または B が入った割合と B の正答率を別に出す。自信 高。
- [major] M2 模型が認める学習用の組（:30）を、おとりの集め方（:145 学習用と評価用の両方）が打ち消す。模型どおりの攻撃者は学習用の本文を候補から消せる。解消: (i) おとりを評価用だけから (ii) 学習用と評価用を別の課題に (iii) 制限と理由を模型に書く。自信 中。
- [major] M3 R4(w) の A0（:129）で記録は Σ floor(v/w)、候補は英数字の数で尺度が合わない。解消: 候補の区間にも floor(値/w) を掛けて和を取る。自信 高。
- [major] M6 問い 4（:23）は二値なのに判定の規則が無い（:212）。解消: 差と 95% 区間の報告に書き換える、または書き方の規則を 1 つに固定。自信 高。
- [major] M5 ENJA15 の推定の単位（:154 は課題で層別）と `enja_decoys` の使い所が無い。500 人・抽選の回数に精度の根拠が無い。解消: 訳者を単位・原文で層別・N = 10 の抽選で使う・精度の根拠を 1 行。自信 中。
- [major] M4 配布の本文と最終稿が一致しない書き手で窓の正解が定まらない（:149・:45）。解消: 文字の揃えで写す規則、または窓の範囲から除く。自信 中。
- [minor] m3 型の align.py と prereg の終点と ∞ の扱いが違う（README.md:10・align.py:41-46・prereg:120）。解消: 包みを足すと書く。自信 高。
- [minor] m4 英語の版と日本語の版のどちらが正か（:3）。解消: 英語の版が正・config と SHA-256 を含める。自信 中。
- [minor] m5 道具の版と A2-b の設定（:133・:135・:155）。解消: config に版・特徴・正則化・writer は ID 列の文字列そのまま・KeyTAR の既定値は取得の後に data.md へ。自信 中。
- [minor] m6 ENJA15 の除外の規則が無い（:207-213）。自信 中。
- [minor] m7 予測の主体が「Claude」（:190）。研究者が採った予測と書くか、AI 使用の節の材料に。自信 中。
- [minor] m8 合成の記録の検査が凍結の前か後かが曖昧（:103・:105）。解消: 凍結の前に行い下書き 3 に入れる、または「凍結の後・取得の前」と明記。自信 中。
- [nit] README.md:6「判断 6〜15」が prereg:4「判断 6〜24」と食い違う。

## 5. 総合の推奨: minor（直してから凍結）
12 件のうち 5 件解消・7 件一部。M1・M1'・M3 は主な量か診断を設計の段で壊し、M6 は言い方の自由を残す。いずれも数行で消えるが、M1 は新しい手順なのでメインが一次で確かめること。

## 6. 読めなかった範囲・注入
wagner2015.txt は 1〜250 行だけ。nosek2018.txt は 95〜119 行と grep。書誌の本体・decisions.md・notes.md は読んでいない。注入の疑い: 無し。
