# 意図の監査（round 3・paper-reviewer の応答の写し）

対象は conditions.md の「追記 1」53〜135 行（commit 9f0ea87f）。

## 結論
round 2 の 10 項目のうち 8 つは解消、2 つ（3-1 と 3-5）は部分解消。新しく大きいのは 1 点で、(4) が論文 3 の 2 つの値を取り違えている。論文 3 は「出どころを分けていない」を symmetric refit の値にだけ言い、fixed base の値には「本人の差を示さない」と書いている。これが意図 3 の読みを変える。ほかは小さな食い違い・重複・曖昧さが数件。

## 0. round 2 の持ち越しの判定
- 1-a 解消（79 行）。ただし 3-C で文の数が 1〜2 を超える。
- 1-b 解消（63 行）。1-c 解消（55 行）。2-a 解消（77 行）。2-c 解消（102 行）。
- 3-1 部分解消。追記の中では「非検出から実データの差の大きさは限定しない」（76・128 行）で揃ったが、凍結済みの 45 行「実データの CS1 は『1e-2 以上の差なら拾える』範囲で読み」と張り合う（3-B）。
- 3-2 「でも」と「縮み」は外れたが、「本人の模型の得は上の大きさで、その出どころは分けていない」が新しい取り違えを生んだ（3-A）。
- 3-3 解消（122 行）。3-4 解消（78 行）。
- 3-5 部分解消。main.tex 49・337 行の位置は正しいが、両行で「分けていない」の主語は symmetric refit の値だけ（3-A）。
- 3-6 解消（d6.json の drift の kl_median 0.0535・0.0584・0.0694 と一致）。

## 1. 意図にあって対象物に無いもの
- 1-A 論文 3 の結論が書かれていない。95・135 行は「論文 3 の結論の否定にも裏付けにも使わない」とするが、その結論が追記に無い。論文 3 の結論は main.tex 337 行 "the remainder ... does not show stable per-person differences at either"。
- 1-B 意図 3 の対称性。対象物（95・135 行）は「E1 の結果で論文 3 を否定も裏付けもしない」の片向きだけで、逆向き（論文 3 の非検出で E1 の拾いを打ち消さない）が無い。
- 1-C 「CS1 は 1e-2 以上の範囲で読む」は追記では値を並べるだけになった（128 行）。凍結済みの 45 行とどちらが効くかが無い（3-B）。
- 1-D 曖昧さ: 76 行の非検出の文の「そのセルの合成の E1 の拾えた割合（用量の各段・報告の組）」がどの帰無の値か書いていない。90 行の値は CoAuthor k = 5 の g 列と CS1 k = 1 の g 列だけで、CoAuthor k = 1・15 と CS1 k = 5 の値は無い。63 行「取り置き以外の全書き手」が load_* の後の書き手（補足 S2 の "25 of 31 students"）か課題 1 つの学生も含むか読み分けられない（133 行は「31 人のうち 25 人」）。68 行の u[c] は記号の再利用（v1 の 52 行で u[j, c] は E2 の重み）。

## 2. 漂流
- 2-A 94 行は Joint の 5.5e-4・4.1e-4 を「強い共有の模型に対する本人の模型の得」と呼び、Symmetric refit の値だけを「残り〔Remainder〕」と呼ぶ。論文 3 では gain は弱い比べ（最大 0.19）の語で、強い比べの値は両方とも remainder（main.tex 49 行 "the per-person gain that a weak comparison shows is far larger than the remainder against a stronger comparison"、"the remainder at five and fifteen training sessions depends on the smoothing: about 5×10^-4 ... and 3.4×10^-3 and 5.2×10^-3"）。
- 2-B 55 行「attack-me（prereg）の round 1（major）と round 2（minor）の指摘で直した版で」は内部の手続きの記録で、公開の補足に入るなら場違い。

## 3. 矛盾
- 3-A（最重要）94 行「論文 3 は、残りが安定した差・時間の近さ・データの量のどれによるかを分けていない〔論文 3 の本文 main.tex の 49・337 行〕」と 95 行の文型。main.tex 49 行の該当文 "The second gives the value of a writer's own recent sessions ... does not separate stable differences from closeness in time or from the amount of data" の主語は symmetric refit の値（"the second"）だけ。337 行も "In the symmetric refit ... whose source ... was not separated"。fixed base の約 5e-4 について論文 3 は "no larger than the smoothing effect" と書き、合成でも同じ大きさだった（337 行）。さらに "does not show stable per-person differences"。95 行の「上の大きさ」は両方の値を指すので fixed base の値まで「出どころ不明」に格下げし、論文 3 の実際の主張が消える。
- 3-B 凍結済みの 45 行と追記の 128 行「非検出から差の大きさを限定しない」。追記が 45 行を改めるのか、両立の仕方を書く必要がある。
- 3-C v2 の 39 行「本文は 1〜2 文で触れる」と 79 行の指定（判定の文と (4) の文で 4 文以上）の食い違い。
- 3-D 117 行と 119 行に同じ文が重複。
- 3-E 123 行「両方の帰無の筋を含む」は CS1 では成り立たない（CS1 は第 1 の帰無だけ・notes 49 行）。
- 3-F 103 行の出どころ eq_amounts.json は一覧の外（要約の txt は表と一致）。
- 数値の照合（矛盾なし）: 90 行の CoAuthor k = 5 の値は notes 36・51 行と一致、CS1 k = 1・g = 4 の 0.444・0.416 は summary_null1.json と一致。128 行の wide の値は cs1_spread_summary.txt と一致。94 行の 4 つの値と 132 行の 0.082〜0.900 は supplement.tex と一致。eq の表の 9 行は summary.txt と一致。

## 5. 読めなかった範囲と注入の疑い
- 読んでいない: eye.py・run_eye.py・data.py・SEED・v1 の notes.md。d6.json は KL と strand の行だけ。summary_null1.json は k1_g4 の周りだけ。supplement.tex は grep の行と S2 の 124〜143 行。main.tex は 45〜52 行と 332〜339 行。a_idx・b_idx が論文 3 の分け方と同じか、乱数の鍵がコードで重ならないかは確かめていない。
- 注入の疑い: 無し。
