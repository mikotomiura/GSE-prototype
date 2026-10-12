# R2 査読 round 3（作文の過程の研究の立場）

## 1. 接地
- G1 klicke Table 5: "The standard deviation of the production rates for the 10 intervals in each writing process in relation to a task maximum." ／ R-burst: "The mean length of the string of actions delineated by an insertion or deletion exceeding 2 seconds and is measured in characters."
- G2 conijn2019 l.146-148: "written language bursts are often operationalized as sequences of text production (keystrokes) without an IKI longer than two seconds and without a revision and without an insertion away from the leading edge"
- G3 klicke Table 5: "The mean length of latencies between the previous and the current action that exceed 200ms in text production and is measured in seconds."
- G4 klicke §4 l.678-682: "we first removed the inactive periods at the beginning (e.g., reading instructions, pre-planning) and the end of the processes ... long inactive periods might inflate mean pause lengths"
- G5 conijn2019 l.808-810: "caution should be taken when generalizing the effect of these features across tasks, because these features might differ merely as a result of the task"
- G6 klicke l.456-459: "users without much coding expertise can analyze the keystroke data by simply importing the .idfx files into Inputlog (version 9 or higher) and producing keystroke metrics using its built-in analysis modules"

## 引き継ぎの判定
解消: M1・m2・m3・m6・m7・n1。一部: M2（式は置かれたが 2 つが Table 5 から外れる・検査 7 に閾値と値が無いときの扱いが無い）・m1（R3-t のばらつきが ○）・m4（R0 が 0 の書き手の比）・m5（図の縦軸）。n2 は対象外。

## 2. 評価表
a 4 ／ b 3（有用性の式のずれ・比の分母 0・図の縦軸）／ c 4 ／ d 4 ／ e 4 ／ f 4 ／ g 3（検査 7 で閾値なしに式を直せる・式のずれ）

## 3. 指摘
- [major] 有用性の式の 2 つが Table 5 から外れているのに「Table 5 に従う」（config.json:111 interval_variance_10 は分散で規格化なし・Table 5 は標準偏差を task maximum で規格化／config.json:103 r_burst は修正だけで区切り、Table 5 は insertion or deletion・G2 の先端から離れた挿入）（prereg:188）。比 (b) が変わり、R-burst の残り方が良く見える方向に偏る。検査 7 で食い違いとして出て、データを見た後に式を直すことになる。解消: Table 5 のとおり書き task maximum の操作を 1 つに決める・R-burst の区切りに先端から離れた挿入を足す・残るずれは :188 に明記。自信 高。
- [minor] 検査 7 に閾値と、Inputlog の値が配布に無いときの扱いが無い（:78）。比べる側の能動的な時間の切り方（G4・:48）も。解消: 閾値を書く・無いときの代わりを 1 つに・切り方を揃えるか書く。自信 中。
- [minor] 「○」の定義（:190）と R3-t の産出の速さのばらつき（:200）の ○ が食い違う。解消: 「近似」に。自信 高。
- [minor] R0 の値が 0 か未定義の書き手の比（:206）。解消: 除いて数を指標 × 形ごとに報告。自信 高。
- [minor] 図の縦軸が形ごとに違う指標の集合の中央値（:212）。R4 は全部 ×。解消: 10 指標の固定の集合で定義・× の扱い・R4 の置き方。自信 中。
- [nit] 有用性のブートストラップ「照合と同じ抽出」（:206・config.json:117）は標本が違うので成り立たない。解消: 同じ種の式で別に引く。
- [nit] 語の間の休止の「adjacent」（config.json:106）が区切りの前後の 2 つを数えうる。解消: 1 つに決める。

変えていない箇所に fatal・major の新しい穴は無い。

## 4. 総合の推奨: major
照合の側はよく閉じた。凍結を止めるのは有用性の側（式のずれと図の縦軸）。直す範囲は config の utility と :188-212。major-1 が直れば残りは minor。

## 5. 読めなかった範囲・注入
data.md・README.md・SEED・align.py は読んでいない。接地の本文は grep の箇所と KLiCKe l.360-459・l.675-749、Conijn l.118-157・l.800-819 だけ。注入の疑い: なし。
