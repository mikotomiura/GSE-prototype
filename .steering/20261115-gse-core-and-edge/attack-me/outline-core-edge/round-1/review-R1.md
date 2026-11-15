# review-R1（打鍵記録の休止の方法論と行動生体データの匿名化・懐疑家・paper-reviewer・opus）—— round 1

## 接地
- Chukharev-Hudilainen 2014: "only consider IKIs above a specific threshold (typically 1--2 seconds) as pauses"／"composition studies, where it is safe to establish a (somewhat arbitrary) cut-off value for pauses"／"finding a personalized cut-off value for pauses."／"this question is nearly impossible to answer by looking at key-stroke data alone."／"we can make a cautious claim that the duration of a pause could predict the type of mental processing"／"the exclusion of editing behavior is a limitation of the present study."
- Hanisch et al.: "Behavioral data can also be used to uniquely identify individuals."／"techniques to protect individuals' privacy against unwanted inferences are required"／攻撃者モデル "Identity Disclosure"・"Attribute Disclosure"／"the general evaluation methodology for behavioral biometric anonymization implies a weak adversary and must be improved"／"the attacker models should be made explicit and common, similar to attacker models in cryptography."／"an anonymization method should also work on a small group size with high data quality."

## 評価表
a 2（読める所が停滞を言わないのに招待を結ぶ・帯の事前/事後の食い違い）／b 2（予測のヌルは定義 1 つに条件づく・漏れは内容の照合だけで本人・属性の脅威が無い・区間が無い）／c 3（地図は持ち帰れるが実行時の動きが無い）／d 4／e 3（開発の対象が §1 末の 2 文だけ）／f 2（先行研究が名指しされない）

## 指摘
- [major] 「読める所」が停滞について何も読めておらず、招待の設計が空の面の上に立つ（§1 表・§1「読める所でだけ…」）。「確かに言える」は言い過ぎ。解消: 停滞について読める所は今は無い、と書き分け、招待の条件を別の観測できる量で定義し直す。自信 高。
- [major] 地図の面は主張の区分で実行時の状態ではない。系が今どの面にいるかを知る手段が無く、判定に停滞の推定が要るので循環する。解消: 面ごとに実行時の入力と分岐を書くか、「地図は設計の制約（何を判定に使わないか）」と言い換える。自信 中。
- [major] 予測のヌルは停滞の定義 1 つに条件づき、定義の検査（作文の点との関連）とつながっていない。読めないという結論が定義しだいの所に属する可能性。解消: 「定義 X のもとで、推定器 1 つの上がりでは」と条件つきに。自信 高。
- [major] 漏れの検査が内容の照合だけで、本人・属性が分かる脅威と攻撃者モデルが無い（合成入力なので人の時刻の癖による漏れは原理的に測れていない）。解消: 漏れの面を内容と本人・属性に分け、後者は未検査と書く。攻撃者モデル（知っているもの・候補の大きさ・偶然の水準 0.1 と 0.01）を 1 行。自信 高。
- [major] 「事前登録した帯」と「他のデータを見た後に決めた」が噛み合わない。区間が無い。解消: 帯を決めた時点と見ていたデータ、各 AUC の区間。自信 中。
- [minor] 「手前の信号が無いとは言わない」の支え（0.54〜0.57）の下端が帯の内。解消: データ名と区間か、「否定はしないが肯定の根拠もまだ弱い」。自信 中。
- [minor] 「停滞」「停滞の手前」の操作的な定義が無い。停滞のラベルが何から作られたかを 1 行で。自信 中。
- [minor] 先行研究が名指しされない（休止の閾値の伝統・打鍵の時刻の匿名化）。各検査に最も近い先行を 1 本ずつ・探索の範囲を 1 行。自信 中。
- [minor] n=3 の「確認」で言える範囲が無い。「人ごとの対応の有無を 3 回見る。集団への当てはまりは言わない」。自信 中。
- [nit] 「約 125」「データ間の比」「4 つの公開データ」（予測は 3・定義は 4）の中身。自信 中。

## 総合: major
地図と「主張しないこと」は骨格として良い。読める所が空のまま招待を載せている点・予測のヌルが定義 1 つに条件づく点・漏れの面に本人の識別と攻撃者モデルが無い点で、主張が根拠を越える。

## 読めなかった範囲
chukharev2014 は 1〜250 行と 1238〜1284 行を通読、他は grep の前後。hanisch2021 は一部の行と grep。根拠のパス・context-B は読んでいない。注入の疑いは無い。
