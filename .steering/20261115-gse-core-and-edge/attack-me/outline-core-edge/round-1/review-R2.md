# review-R2（注意に応じて介入の時機を決める系と 1 人ごとの推定の応用・実務家・paper-reviewer・opus）—— round 1

## 接地
- Horvitz, Jacobs & Hovel 1999: "Alerts provide potentially valuable information at a cost of interruption. The cost of an interruption depends on the nature of the interruption and on a user's current task and focus of attention."／"infer a probability distribution over a user's focus of attention and harnessing such inferences to infer the expected cost of transmitting alerts to users."／"Decisions about deferral must take into consideration the cost associated with the delayed review of the information."／"we seek to build or learn probabilistic models that can make inferences about a user's attention under uncertainty."
- Hart et al. 2022: "(2) Do between-person and personalized models perform differently when inferring such self-reports?"／"We trained personalized machine learning models on data from employees (N=158) who participated in a 3-week ecological momentary assessment study."／"The mean R 2 was approximately 0.31 (SD 0.29)…"／"without sacrificing predictive performance or potential treatment efficacy"

## 評価表
a 2／b 2（予測の検査は人をまたぐ holdout だけで 1 人ごとのモデルを試していない・帯は事後・0.54 の下端が帯の内・対応は 3 名）／c 2（何を作るかが無い・発火の条件が空）／d 3／e 2（開発の成果物が見えない）／f 1（介入の時機の系・受動センシングを申告で検証する研究が出てこない）

## 指摘
- [major] 系の発火の条件が今の地図の上では空（読める所は IME だけ、停滞の手前は読めない所）。解消: 招待を出す条件をどの面のどの観測で決めるかを 1 文（例: 手前は予測せず長い止まりの後に事後に出す）・「9 割以上が停滞に至らない発火」との扱い。自信 高。
- [major] 「読めない所」の言い方が根拠より強い（推定器 1 つ・事後の帯の帰無を「観測からは言えないこと」へ）。0.54〜0.57 の下端が帯の内で「信号が無いとは言わない」の根拠に弱い。解消: 「この推定器・この窓では読めなかった所」に限る・0.54〜0.57 のデータ・区間・帯との関係。自信 高。
- [major] 予測の検査は人をまたぐ評価だけで 1 人ごとのモデルを試していないのに、§4 は「新しい人への当てはまり」を主張しないとする。言えるのは「人をまたいでは読めない」まで。解消: 限定に「人をまたぐ評価だけ。1 人ごとのモデルは未検査」と書くか、1 人ごとの検査を段 1 に入れる。自信 高。
- [major] 定義の検査は予測の結論が定義で動くことを示していない（動いたのは作文の点との関連の向きとデータ間の比）。「動く」の大きさが無い。解消: 「結論そのもの」を「作文の点との関連」に限り、動いた程度を数値 1 つで。自信 中。
- [major] 何を作るのか・読者が何を持ち帰れるのかが書かれていない（地図は文書か道具か）。公募は開発の成果物を求める。解消: 期間内に作るものを 1〜2 行（例: 3 つの検査を他の観測の経路に当てる公開の道具・読める所で動く招待の系）と使う人。自信 高。
- [major] 先行研究の位置づけが無い（Horvitz 1999 は "the stream of user activity built from sequences of mouse and keyboard actions" を注意の推定に使う・Hart 2022）。解消: 介入の時機の系・1 人ごとの受動センシング・打鍵からの内容の漏れに先行を 1 本ずつ、差分を 1 文。自信 高。
- [minor] 誤った時機の費用と見送る費用が扱われていない。解消: 誤発火の費用をどう抑えるか（無視しても何も起きない等）を 1 文。自信 中。
- [minor] §1 の「漏れる所」の行に合成入力・既知の候補の限定が無い。自信 高。
- [minor] 3 名で「確認」とする根拠が無い。1 人ごとの判定の基準と言える範囲を 1 文。自信 中。
- [nit] 「30 秒の上がり」「事前登録した帯」「手跡」・数値が 2 つずつの理由。自信 高。

## 総合: major
地図の 2 面（読めない所・定義しだいの所）の言い方が根拠より強い。読める所に停滞の材料が無いので何を作りいつ動くかが決まらず、開発を求める公募と合わない。先行研究との対照と、人をまたぐ評価と 1 人ごとの評価の区別が無い。

## 読めなかった範囲
根拠のパス・記入要領は読んでいない。horvitz1999 は 1〜330 行あたりと grep、hart2022 は grep の断片。注入の疑いは無い。
