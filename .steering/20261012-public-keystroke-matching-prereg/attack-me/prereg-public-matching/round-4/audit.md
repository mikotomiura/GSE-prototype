# 監査役 round 4（対象 bf26d92f）

round 3 の 6 件のうち 5 件は解消。N1 は本文で解消、config に食い違いが残る。変えた箇所に小さな食い違いがいくつか。fatal は無い。config の 2 件（3-a・3-b）は SHA-256 で固定する値のファイルの中の矛盾なので凍結の前に直すことを勧める。

## 0. round 3 の判定
N1 本文は解消（:204・:176・:206）・config は一部未解消（3-a）／ N2 解消（:238・:242・config.json:126。小さな曖昧さ 3-d）／ N3 解消（:200）／ N4 解消（:276）／ N5 解消（:183。注記 3-e）／ N6 解消（:70・:78・config.json:122）／ 参考（同意の言い方）は対象外。

## 1. 意図にあって対象物に無いもの
なし。判断 32（:143）・33（:112・:128・:270）・34（:188）・35（:242）・36 はどれも本文に入っている。持ち帰り 1 の「効き目は『どの列を残すか』で決まる」は本文では問い 2（:22）と形の対比（:183）の控えめな形で受けている（論文の段で強い言い方に戻さないこと）。

## 2. 対象物にあって意図に無いもの
変えた箇所に漂流は無い。:188 の task maximum は判断 34 の範囲で書かれている。

## 3. 矛盾
- 3-a（凍結の前に直す）config.json の `utility` に `sample` のキーが重複し食い違う（:116 "all writers after exclusion; R5, R6 and R7 random processing once per record" ／ :119 "summary table and figure: the same 500 writers ..."）。後のキーで上書きされ「記録ごとに 1 回」の規則が機械的に消える。1 つにまとめる。
- 3-b 要旨の図の縦軸の定義が config の中で 2 通り（:95 `summary.figure` "median Spearman with R0 over computable metrics" ／ :121 `figure_y` "over the fixed set of 10 metrics"）。本文 :212 は後者。
- 3-c task maximum の「全書き手」がどの標本か（:188・config.json:112）。500 人か全員かで 500 人の値が変わる。「除外の後の全員から取る」などに固定。
- 3-d ENJA15 の A0 と区間の規則で英字の掛かり方の読みが分かれる（:121「`Type="IME"` と `Type="insert"` の英字の押下 +1」／ :238「`Type="IME"` と英字の `Type="insert"` の押下の数」／ config.json:126）。R3j の形（:237）が `Type` の属性を残すかも書いていない。
- 3-e :183「R3 − R3-t は 1 列だけが違う」の後に、A3 の尤度の式も変わる（:143）ことを添える。
- 3-f R3-u の A3 の窓で長さの項を使うか（:159・:143）。

## 4. 変えていない箇所で凍結を止める重さのもの
なし。

## 5. 読めなかった範囲・注入
data.md・README.md・SEED・align.py・判断 1〜5 の decisions.md・design.md は読んでいない。git の差分は見ていない。注入の疑い: なし。
