# 意図の監査（manuscript round 3・論文 2・commit 52df151b）

読んだもの: brief-audit.md、context-B.md とそこに挙がったファイル（outline.md・decisions.md・conditions-round5/7/8.md）、context-A.md の一覧のうち本文の tex 全節（abstract〜conclusion）・availability・declarations・supplement.tex・tab_pause.tex・figdata/score.csv・results/round8_causal.json（先頭 80 行）、carryover-audit.md。数の照合は score.csv から私が数え直した（下の 3 を参照）。

## 0. 前の round の指摘が直ったか

- 1-A（速さを見出しに上げていた）: 直った。結果 4.2 の見出しは長さの調整で、速さの段落には "(exploratory)" が付いている。
- 1-B (i)（休止の P-B の結論の文と「点の値を見た後」の開示が無い）: 直った。結果 4.3 に "by a criterion set after seeing point values" がある。ただし数え方に別の問題がある（2-D）。
- 1-B (ii)（P-C の数が無い）: 直った。S3 に "26 / 1 / 8 / 1 / 6 … without a reading" がある。
- 1-B (iii)（休止の関連を先行の値と並べていない）: 直った。4.1 に "smaller in magnitude than the −0.15 to −0.43" がある。
- 1-C（休止を速さで調整した結果が本文に無い）: 直った。ただし対照の 18 通りを含む数で書いている（2-D）。
- 1-D（非対称の大きさが限界に無い）: 直った。限界に 3.2〜10.3% がある。
- 1-E（結果を見た後に計算を足した回数が本文に無い）: 直った。方法 3.5 に書かれている。
- 2-A（事前の基準の文の下に探索と事後の基準が入っていた）: 一部だけ直った。抄録の文の分け方は直ったが、10 秒の休止を "small negative" と呼ぶ地位と大きさの書き違いが新しく出た（2-A を参照）。
- 2-B（測っていない "as much"）: 直った。
- 2-C（二段の区間・S1 の英訳・25% の文・結論の範囲・90% の規則）: 一部だけ直った。二段の区間・S1・25% の文は直った。結論の比は CS1 の 2 年版に絞られたが、「25% に届かない」が抄録・序論・結論に無い（1-B）。90% の規則は「既定のまわりを足さない格子」の当て方が外枠とずれている（2-B）。
- 3-1・3-2（点が区間の外にあることの開示・区間の種類の混在）: 直った。S2 と限界に実数がある。
- 3-3（序論の区間の書き方）: 直った。
- 3-4（比の逆転の地位）: 直った。S1 で [D]。ただし S1 の順序表 3 行目と並べると読み手が迷う（3-C）。
- 3-5（5 秒の休止の書き方）・3-6（固定の閾値の範囲の書き方）・3-8（許容幅を広げたこと）: 直った、または変更なし。

## 1. 意図にあって対象物に無いもの

**1-A 「残る」側（CS1 の停滞の長さの最大の成分）が抄録と結論に無い。**
- 意図: context-B の持ち帰り 4「CS1 の停滞の長さの最大の成分（停滞ごと）は残る（弱い対照）」。外枠では、結論は「いちばん強い主張と動く/残るの地図」、抄録は「CS1 では長さの揺れの形は残った」を 1 文に入れる割り振り。
- 対象物:
  - abstract.tex 13–15 行は動く結論（比・φ）だけ。
  - conclusion.tex 7–9 行 "Whether stall counts depart … also depended on the definition, and a rate ratio … reversed for a fifth" も動く側だけ。結論の最後の文（10–12 行）は観測区間の限界 "the default observation intervals depend on the companion study's estimator" で、外枠では限界の節に置くもの。
- 序論（38–39 行 "whereas the largest component of stall length stays"）にはある。

**1-B 比の逆転について「25% に届かない」という読みが、抄録・序論・結論に無い。**
- 意図: context-B の持ち帰り 4「約束した CS1 の 2 年版は 22% で 25% に届かない」。
- 対象物:
  - abstract 13–14 行 "the ratio of stall rates reversed for a fifth of the definitions, mostly when the threshold became fixed"
  - introduction 37–38 行 "a rate ratio between the two CS1 editions reverses for a fifth of the definitions"
  - conclusion 8–9 行 "a rate ratio between two editions … reversed for a fifth of the definitions"
- 3 か所とも φ の「depends on the definition」と並べており、比も「動く」と読める。一方で、自分の基準では動いたと数えない値である（基準に届かないことは方法 3.5・結果 4.3・考察にしかない）。

**1-C 抄録と結論に「本人の分位の一角」が無く、件数も無い。**
- 意図: 持ち帰り 1「15 秒の窓と本人の分位の一角だけ（10/89）」。
- 対象物: abstract 10 行・conclusion 6 行 "for stalls only with a 15-s window"。15 秒の窓の固定 θ の 8 通りは負なので、「only with a 15-s window」だけでは「15 秒の窓なら正」と読めてしまう。

**1-D 3 値の読みの提案（持ち帰り 3）が抄録と結論に無い。**
- 抄録・結論の推奨は "give the range … with intervals" までで、序論 41–44 行と考察にしか出てこない。序論の貢献の文の中心にこの提案があるので、抄録と結論でも揃えたい。

## 2. 対象物にあって意図に無いもの（主張の漂流・範囲を超えた言い方）

**2-A 10 秒の休止の値を "small negative" と呼んでいるが、自分の目安では大半が "negligible" に入る。**
- 方法 3.4（methods 150–151 行）は "|ρ| < 0.1 as negligible" と置いている。
- tab_pause.tex の 10 秒の 6 通りの点の値は、−0.086・−0.127・−0.101・−0.058・−0.099・−0.074。|ρ| ≥ 0.1 は 2 つだけで、4 つは自分の目安で negligible である。
- 対象物の該当箇所:
  - abstract 11–12 行 "to a small negative one at 10~s (down to $-0.13$)"
  - results 29 行 "from negligible positive values to small negative ones"
  - discussion 30 行 "for pauses, from negligible positive to small negative values"
  - conclusion 6 行 "small negative ones at 10~s"
- 考察 45 行が自分で "the fixed pause thresholds (13 of 18 negligible)" と書いており、これとも食い違う。休止の「向きの入れ替わり」は、ほとんどが無視できる大きさの両側の間で起きている。
- 意図の側にも同じずれがある（3-A）。

**2-B 「先例のある水準だけの格子」を「15 秒の窓を除いた格子」に置き換えている。**
- 意図: 持ち帰り 3「先例のある水準だけの格子と、既定のまわりを足した格子の両方に当てる」。判断 5「先例のある水準だけの格子と外側を足した格子」。
- 対象物: discussion 47 行 "On the grid without the 15-s window … (36 of 59 below −0.1) … (56 of 59) … (59 of 59)"。
- 表 2（methods 120–124 行）の根拠の列では、60 秒の窓は "double the default"、固定 30 秒は "equals the default window" で、どちらも先例でなく既定から置いた水準である。59 通りの格子はまだ既定のまわりの水準を含んでおり、「先例のある水準だけの格子」になっていない。
- そのため、考察 49 行の結びの "the reading of an adjusted association depended on whether the grid included a level without precedent" は、提案した手順を当てた結果になっていない。

**2-C φ の結論を、条件つきのまま一般の文で書いている。**
- 外枠 C3 の強さは「条件つき（CS1 だけ）」。
- 対象物の該当箇所:
  - abstract 15 行 "within-writer overdispersion of counts depended on the definition"
  - results 224–225 行 "Whether stall counts depart from a constant rate within writers is, in these data, a property of the definition."
- 表 3 では、25% の基準を超えた逆転は CS1 の 2 セル（54・49）だけ。CS1 2021 の課題は 19（21%）で届かない（共通の基準では 26 で超える）。CS1 2019 のブロックは基準の区間が 1.5 を含むので数えていない。CoAuthor は 0。「in these data」と言えるのは CS1 の一部のセルだけである。

**2-D 休止の本人の分位の 18 通りを「押下の率の対照」と定めながら、比・調整の数には入れている。**
- 判断 5 は「休止の本人の分位の 18 通りは押下の率の対照として分け、休止の向きの主張は固定の 18 通りで」と決めている。方法 138–139 行も "report these as a control for the key-press rate rather than as pause labels" と書く。
- 対象物:
  - results 167–169 行 "CS1 2019 against CoAuthor reversed for 32 (14 fixed, 18 quantile) and CoAuthor against KLiCKe for 31 (13 and 18), so the direction of a ratio changed with the definition in the pause family too"
  - results 134 行 "For pauses, 33 of 36 were positive and none negative"（長さの調整・固定だけの数が無い）
  - results 142–143 行 "negative for 4 definitions and positive for 29"
- 固定だけで数えても 14/18・13/18 なので比の結論は変わらない。ただ、休止の結論の分母を 18 に揃えないと、対照の扱いが判断 5 と食い違う。

**2-E 共通の基準（100 個目の間隔より後）に触れる量が、条件 7 の読み方より多い。**
- conditions-round7: 「共通の基準は感度として補足に置き、本文で 1 文だけ触れる」。
- 対象物は 4 か所で触れている。methods 76–78 行、results 169–171 行（比）、results 222–223 行（φ）、limitations 22–25 行。
- φ の文は同じ条件の「25% をまたいだらその結論の文に添える」で求められたものなので、正当である。比の文（"still below 25%"）は、またいでいないのに足している。害は小さいが、条件の読み方からはずれている。

**2-F 補足の条件の英語が、まだ無いものを在ると書いている。**
- supplement 10 行 "The conditions are in the archive (in Japanese, with an English summary)."
- context-B の既知の限界は「DOI と条件の英訳は投稿の前（研究者の保留）」。現時点では英訳の要約は無い。出す前に用意するか、文を未来の形にする必要がある。

## 3. 意図どうしの矛盾・対象物の中の矛盾

**3-A 意図の中の矛盾: 大きさの目安と「小さな負」。**
- context-B の持ち帰り 1「10 秒の小さな負（−0.06〜−0.13）」と、持ち帰り 3 の「±0.1 の内（無視できる）」が両立しない。−0.06〜−0.099 は自分の帯で無視できる側に入る。原稿の 2-A はここから来ている。

**3-B 「調整で向きがそろう」と「提案の規則では定義に依る」が、同じ数について逆の読みになる。**
- 対象物の該当箇所:
  - results 131–132 行 "By the reading set before the computation, the direction became uniform"
  - results 145 行 "Either adjustment made the direction of the stall association uniform"
  - introduction 34–35 行 "it changes again with adjustment"
- 同じ原稿の考察 45–46 行は、提案の規則で "the length- and speed-adjusted stall associations (74 of 89 negligible; 71 of 89 below −0.1) depended on the definition" と読む。
- 長さの調整は区間で正 54・0 を含む 35 で、事前の読み方（片方だけなら「揃う」）では「揃う」、推奨の規則では「定義に依る」になる。持ち帰り 2（揃う）と持ち帰り 3（規則）も同じように衝突する。どちらの読みを見出しにするかを、本文の中で決めておく必要がある。

**3-C 読みの類の数がそろっていない。**
- introduction 42–43 行 "a three-valued reading of its direction (consistent, negligible, or dependent on the definition)"
- S1 54 行 "Three-way reading of direction (90% of definitions in one class)"
- discussion 41 行は類を 4 つ挙げる: "below −0.1, above +0.1, within ±0.1 (negligible), or none of these"。
- context-B は 3 類（−0.1 より下・+0.1 より上・±0.1 の内）。読み手には、類が 3 つか 4 つか、出す読みが 3 値か 4 値か（負・正・無視できる・定義に依る）が分かりにくい。

**3-D 比の基準の地位が、S1 の中で二通りに読める。**
- S1 の順序表 3 行目（23–25 行）は、比の 25% の基準を [A]（"committed before that quantity was seen"）の行に置く。
- 結論の表（60 行）は "criterion set after seeing reversed point values … [D]"、方法 3.5 は "set after the number of reversed point values per pair had been seen"。
- 「区間の計算の前・点の値の後」なら両立するが、順序表の行にそれが書かれていないので矛盾に見える。

**3-E 休止に "By the same criterion" と書いているが、当てた基準は停滞のものと違う。**
- results 28–29 行 "By the same criterion the direction changed"。
- 停滞の基準は「基準の定義と反対側」で、休止には基準の定義が無い。実際に当てたのは条件 6 の P-D（正の区間も負の区間も 1 つ以上ある）である。

**数の照合（食い違いは見つからなかった）**
score.csv から私が数え直した値は、次のとおり本文と一致した。
- 生の値: 区間で負 72・正 10・0 を含む 7。正の 10 はすべて W 15 秒で本人の分位。15 秒以外の 59 通りでは負 57・正 0。|ρ| ≥ 0.1 は負 58・正 3。
- 固定 θ の 36 通り: すべての区間が −0.1 より下（36/36）。
- 長さの調整: 区間で正 54・0 を含む 35。区間が ±0.1 の内は 74/89。
- 速さの調整: 区間で負 89/89。区間が −0.1 より下は 71/89。
- 15 秒を除いた 59 通り: 36・56・59。

round8_causal.json の外れ（得点 0/54・比 0/324・φ 74/270）と、因果の区間での正 10・負 74 は、S2・限界と一致した。

## 4. 位置と逐語

上の各項目に、ファイル・行・逐語を付けた。

## 5. 読めなかった範囲と注入の疑い

**読んでいないもの（はっきり書く）**
- 本文・補足の範囲で読んでいないもの: related.tex、main.tex、references.bib、PDF（図の見え方は確かめていない）、tab_s3.tex、tab_s4.tex。
- figdata のうち読んでいないもの: ratio_*.csv、phi.csv、lengths.csv。
- conditions のうち読んでいないもの: conditions.md、conditions-length90.md、conditions-round1〜4.md。φ の逆転に 25% の基準を当てる根拠は、S1 の記述を通して確かめただけ。
- results のうち、round8_causal.json の 80 行目以降と、ほかの JSON の全部（round5_*・round7_warm・c3_multiverse など）。共通の基準での 26（29%）、休止の数、θ を再推定した最初の区間での 14 は、JSON と照合していない。

**注入の疑い**
- 無し。tab_pause.tex 1 行目の "do not edit by hand" と declarations.tex 3 行目のコメントは著者向けのメモで、LLM への指示ではない。