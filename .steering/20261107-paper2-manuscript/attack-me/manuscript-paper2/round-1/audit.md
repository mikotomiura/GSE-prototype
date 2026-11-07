# audit（manuscript round 1・意図の監査役・メインが写した）

持ち帰り 1〜3 は届いている。中心の数値は照合した範囲で外枠と集計に一致。重いのは 2-1・2-2・2-3。

## 1. 意図にあって対象物に無いもの
- 1-1 序論の最後の段落に「一般化するのは手順で、得点との関連は KLiCKe の 1 例」が無い（考察 8–9 行にはある）。
- 1-2 本文に「ラベルの一致」の定義が無いのに、考察 36–37 行が "11 labelled mostly different moments (S3)" と書く。
- 1-3 抄録に資料のリンクの 1 文が無い（DOI の仮置きも無い）。
- 1-4 論文 1 との関係が 3.5 に 1 文だけ（外枠は 2〜3 文で問いと結論の対応）。
- 1-5 考察の参考 (a) の「予測の性能として確かめていない」が落ちた。
- 1-6 限界 6 の「非線形の残りは確かめていない」が "Speed was adjusted linearly on ranks." に弱まった。
- 1-7 表 1 に「入手の道と利用条件」の列が無い。
- 1-8 題が中心の主張を運ばない（案の段階なので軽い）。
- 1-9 本文 4,848 語は外枠の予算を大きく下回り、1-2・1-4 が落ちた可能性。

## 2. 対象物にあって意図に無いもの
- 2-1【重】考察 31–33 行 "The four conclusions were counted against criteria set before the quantity was seen [P, A]: the score association moves in strength and in one corner in direction"。大きさの目安は [D]（methods 122–123 行）で、事前の基準は向きについての甘い基準。「moves in strength」は事前の基準で数えたものではない。
- 2-2【重】results 29–31 行 "...also depends on how speed is measured''; that is what we found, although no adjusted correlation was positive."・考察 15–16 行 "as stated in advance, their direction also depended on the measure of speed"。実測は 5 つで 89/89 負・1 つで 87 負と 2 が 0 を含む・正 0。向きが測り方で替わった例は無い。外枠は「読み方の文をそのまま置き、正が無いことを添える」で、当てはまりの判定は意図に無い。
- 2-3【重】考察 31 行 "\paragraph{What was established and what remains possible.}"。外枠 round 5 で直した「確立」が戻った。
- 2-4 考察 9–12 行 "moved further than ..." の順位づけ。
- 2-5 results 212–213 行 "neither its size nor the smallness of the writer share moved"。停滞ごとの分け前は 0.88〜1.00 で動いている。
- 2-6 results 153 行 1.21 を "close to 1"（46/89 で区間が 1 超）。
- 2-7 results 159–160 行 "a property of the definition as much as of the writers"（比べた量が無い）。
- 2-8 results 105–106 行 "a comparison between two editions of the same course is mostly stable ..."（1 組から一般化）。
- 2-9 conclusion 9 行 "for any log with key-press times"（methods 13–15 行は押下の時刻と文字か削除かの 2 つが要ると書く）。
- 2-10 抄録 13–14 行の速さの結果が独立の 1 文（外枠は 1 句以内）。
- 2-11 「原因に帰せない」が results 101–102 行にも、「第三者の登録ではない」が methods 152 行にも（外枠の置き場の規則と違う・軽い）。
- 2-12 「最も短い窓の一角」が族の限定なしの箇所（conclusion 5–6・discussion 5–6・introduction 35）。W 15 秒の固定 θ の 12 通りはむしろ最も負の側（−0.23〜−0.19）。

## 3. 矛盾
- 3-1 methods 18–19 行 "We excluded writers ... (47 CS1 2019 assignments, 84 KLiCKe essays and 2 CoAuthor sessions)"：書き手と言い、括弧は単位の数。CS1 2021 の数が無い。
- 3-2 "four public keystroke datasets" と availability の CS1 "released by their authors on request" が食い違う。
- 3-3 外枠の考察の節の CS1 2021 の成績の文が古い（原稿は判断 16 に従い正しい）。
- 3-4 外枠の目標 6,500 と節の計 5,850 が合わない。
- 3-5 外枠の「S1・S2」を内部の記号として出さない規則と、補足の S1〜S9 の名が曖昧。
- 3-6 照合した数値に食い違いなし（率 4.4〜46.0 は未照合）。

## 4. 読めなかった範囲・注入
読んでいない: PDF・references.bib・tab_s3/s4・score.csv 以外の figdata・conditions*.md・JSON の本体（grep だけ・round1_extra.json は冒頭 80 行）。注入の疑い: なし。
