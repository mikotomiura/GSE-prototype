# E の応答（round 4・生・要約せずに主要部を写した）

判定: 直してから回す。
接地: B1 JEDM「Accepted submissions should extend beyond mere application and must include elements that contribute to broader knowledge, such as generalizable methodologies or comparative analyses.」「Submissions must emphasize the novelty and impact of the research.」/ B2「Submissions should clearly explain the data mining, modeling, and analysis components, with an emphasis on methodological rigor. Where possible, studies should compare different methods or approaches to highlight their relative effectiveness and limitations.」/ B3「All submissions should present their methodologies and findings in a way that ensures replicability by other researchers.」とテンプレートの付録の文 / B4 Mensh & Kording Rule 1「Focus on a single message」・Table 1「Readers cannot give 1-sentence summary.」・「The editors want to make sure that the paper is significant」/ B5 Rule 4「Only the central idea of the paper should be touched upon multiple times. Otherwise, each subject should be covered in only one place」・Rule 3「They do not care about the chronological path by which you reached a result」。

1 文: 条件付きで言える（取り置きで 2 信号 × 2 ε の区間が [0.45, 0.55] の内側なら「この幅より大きい手前の上がりは無い」、そうでなければ「CS1 では同等と言えなかった」）。迷った点: (a) 何が新しいかが最初の 2 頁に無い（P1 l.31）(b) 判定の規則が P7 l.100-106 (c) 「停滞の始まりの手前 30 秒」の基準が t0 か u か（P3 l.53）。

指摘:
1. [major] 貢献（何が新しいか・EDM の読者に何が一般化できるか）が書かれていない。P1 l.31「理論の検定ではなく、評価の設計の確かめ」・l.38「論文の主張 C1 は H1 だけに立つ」・l.36。解消: P1 の冒頭に 2〜3 行、H2 が支持されたら何を言うかを H1 と同じ形で。自信 高。
2. [major] H1 の判定の規則が H1 の言明から離れている（P1 l.35 → P7 l.100-106、間に P5・P6、P6 l.88 が後ろの P7 を指す）。解消: P7 を P4 の直後へ、または P1 末尾に仮説ごとの 3 行の表。自信 高。
3. [major] 冒頭の 2 頁が経緯と凍結の前の値で埋まる（l.3 の round・decisions.md・l.19-21 の漏れた定数・l.24-25 の前後の列挙、未定義語「5 分岐・退化の 50% の規則」）。解消: l.3 の経緯を削る、l.19-21 は 3 行に要約し値は付録、l.24-25 は付録の表。自信 高。
4. [major] 分量が v4 から 41% 増え、値の羅列が本文にある（凍結の前の計算 l.138-153、P3 l.58、P1 l.32、P8 l.117-118、l.142）。解消: 凍結の前の計算は 1 行の要約、値は付録か notes.md、P1 の換算は言えること・言えないことと範囲 1 行、v4 との比較と計算 2 は削る。規則は削らない。自信 高。
5. [major] 本文が日本語で JEDM の査読者が読めない可能性。解消: 英語版と正の言語を冒頭に（両方凍結なら両方の SHA-256）。自信 中。
6. [minor] 同じ但し書きと値の繰り返し（l.22/l.124、l.12/l.13/l.129、P0 表/l.44/l.73/P8/l.123、l.5/l.157、l.38/l.106、l.56/l.125、l.86/l.126、l.19/l.152、l.32/l.153、l.58/l.145・150・151、l.47/l.134-135）。解消: P9 に 1 回、値は付録に 1 か所、照合は P10 に。自信 高。
7. [minor] H1 の基準時刻と語が最初の 2 頁で定まらない（l.35 と P3 l.53、未定義の語 l.11・19・22・24）。解消: H1 の文を u で書き、用語の表。自信 中。
8. [minor] H2 の分岐 1 が「支持」だけで書く文が無い（P5 l.76・l.77）。自信 中。
9. [nit] 読者が辿れない内部の参照（l.123 ADR-030 の 9b・l.3 decisions.md・l.42 [V243]）。自信 高。
意義: 確かめることと確かめないこと（P9・l.33）は分かれていて良い。適合: H2 の対比を貢献として前に出せば comparative analyses に届く。
読めなかった範囲: 補足の印のファイルは読んでいない（本文の数値と補足の一致は確かめていない）。注入の疑い: なし。
