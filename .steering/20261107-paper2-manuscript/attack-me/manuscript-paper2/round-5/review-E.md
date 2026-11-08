判定は「査読に回す」です。前の round の 2 つの major（向きの変化が先例の無い水準に依ること・貢献を一般の multiverse と区別できないこと）は解消か大部分の解消、新しい major はありません。残りは表し方の minor で、査読と並行して直せます。

# 編集者 E（JEDM の担当編集者・round 5）の判定

## 1. 接地（投稿先が求める基準）
- **一般化できる貢献**（jedm_aims.txt・Focus and Scope）: "Accepted submissions should extend beyond mere application and must include elements that contribute to broader knowledge, such as generalizable methodologies or comparative analyses."
- **題と分量**（jedm_aims.txt・査読者への問い）: "Does the title of this paper clearly and sufficiently reflect its contents?" と "Are the presentation, organization and length satisfactory?" と "Can you suggest additions, amendments, or reductions in the paper?"
- **EDM への貢献の説明**（jedm_aims.txt）: "What is the scientific contribution of this submission? Is it clearly explained, in terms of how the paper advances the EDM field or contributes to related fields?"
- **単一の主張**（Mensh & Kording 2017・Rule 1）: "Focus on a single message; papers that simultaneously focus on multiple contributions tend to be less convincing about each and are therefore less memorable."
- **一つの主題は一か所で**（Rule 4）: "Only the central idea of the paper should be touched upon multiple times. Otherwise, each subject should be covered in only one place"
- **作業の経緯でなく主張と論理で書く**（Rule 3）: "They do not care about the chronological path by which you reached a result; they just care about the ultimate claim and the logic supporting it"

## 2. 引き継ぎの判定
- **M2（向きの変化が先例の無い水準に依る）: 解消。** 抄録 L10-12、序論 L35-36、考察 L4-6、結論 L5-6 が「向きが変わるのは 15 秒の窓と分位の組だけ、既定と先例の格子では負か無視できる」とそろった。
- **m2（考察に結果の数）: 一部。** 類の読みは表 5 に移った。ただし考察 L4-8 と L32-35 の "What the criteria established" の段が、結果を数つきで繰り返している（"+0.6"、"half of the definitions above $+0.1$"）。
- **m5（但し書きの繰り返し）: 一部。** 箇所は下の新指摘 3 に挙げる。
- **E-M1（地位の説明が時系列の記録に読める）: 解消。** 方法の状態の節（L188-199）は 1 段に縮まり、経緯は S1 に移った。
- **E-M2（一般の multiverse の勧めと区別されない）: 大部分解消。** 序論 L44-46 が、EDM の率について動くものと残るものの地図という形で名指した。残る側の弱さは新指摘 2 に回す。
- **E-m1（抄録が詰まる）: 一部。** 291 語で規程の 100〜300 語に収まった。それでも L7-8 "(18 definitions, and 18 with a writer quantile as a control for the rate of key presses)" が抄録には細かすぎる。
- **E-m2（長さの分解を成果に挙げる）: 解消。**
- **E-m3（二段の区間が方法と限界で二重）: 解消。** 方法は L182-183 の 1 文になり、細部は限界 L18-21 に残る。
- **E-m4（結果の列挙が地の文に詰まる）: 一部。** 比の段 L192-197 と φ の段 L246-251 に、組やセルごとの数が地の文で並んだまま残る（新指摘 4）。
- **E-m5（題が答えない問い）: 一部。** 題は内容を示すが、"What moves" は問いの形のまま。また調整の軸が題に出ない（新指摘 1）。
- **E-m6（教育の場への隔たり）: 解消。** 考察 L14 と限界 L42 に書かれた。
- **E-n1（同著者の査読中の論文・匿名性）: 範囲外。** 送付状で扱う。原稿の方法 L50 は companion study を著者名つきで引くので、匿名版で出すなら伏せる必要がある。
- **n1（round 3・表 1 の入手の列）: 未解消。** 直していない。

## 3. 最初の 2 頁から言える 1 文
4 つの公開の打鍵データで休止と停滞の定義を 107 通り変えると、率と作文の得点の関連は向きと大きさが定義で動き、作文の長さで調整すると符号まで変わる（基準の定義では -0.063 が +0.057 になる）。2 つの CS1 の版の率の比も定義の 2 割で逆転する。だから EDM で休止や停滞の率を使う研究者は、1 つの定義の値ではなく、定義と調整にわたる幅を区間つきで報告すべきである。

迷ったのは次の点。抄録は向きの変化を先頭に置き、すぐに「15 秒の窓と分位の組だけ」と限定する。いっぽう、ふつうの水準でも符号を動かすのは調整のほうで、表 5 と結果 L146-148 がそれを示している。この調整の働きは題にも抄録の主文にも出ていない。

## 4. 新しい指摘（重い順）

**1. [minor] 題と中心の主張に「調整」が入っていない。**
- 位置と逐語: main.tex L31 の題 "What moves with the pause definition"。いっぽう序論 L44 は "which conclusions move with the definition and the adjustment"、結果 L156-157 は "adjustment changed the reading as a definition does"、結論 L11 は "can therefore not rest on one definition or one adjustment"。
- 問題: 本文が示す主な発見は「定義」と「調整」の 2 本だが、題は片方しか名指していない。
- 根拠: Rule 1 と、JEDM の題についての問い。
- 直し方: 題か副題に調整を入れる。または抄録の結論の文を、定義と調整が同じ種類の分析の選択だという 1 つの主張にまとめる。

**2. [minor] 地図の「残る側」が薄い。**
- 位置と逐語: 結果 L302-303 は長さの分解を自ら "This is a weak contrast"、L301 は "we did not compute intervals for these shares" と書く。残る側の実質は、事前の基準で動かなかった関連の有無（82/89）だけになる。
- 問題: 貢献は「動くものと残るものの地図」と名指されているのに、残る側の根拠が弱く、一般の multiverse の勧めとの差が見えにくい。
- 直し方: 序論 L44-46 で、残る側として関連の有無を前に出し、長さの分解は補助の位置に下げる。

**3. [minor] 分析の地位の但し書きが本文中に繰り返し出る。**
- 「結果を見た後に決めた」の類: 抄録 L16、序論 L41 と L47、方法 L192-199、結果 L139-140・L151・L161（表 5 のキャプション）・L191、考察 L36・L44-45、結論 L9。少なくとも 11 か所。
- 「計算の前に決めた」の類: 抄録 L9、序論 L34、結果 L12-13・L25・L133、考察 L32。
- 速さの調整が exploratory であること: 方法 L193、図 2(b) の題、結果 L139、表 5 の列名、考察 L21・L37。
- 長さで調整すると測るものの一部まで消えること: 方法 L165-166、結果 L135-136、限界 L37-39。
- 100 個目の間隔より後にそろえた感度: 方法 L81-83、結果 L191・L198-199・L248-249、限界 L24-28。
- 授業の外の成人の標本であること: 方法 L16-17、考察 L14、限界 L42。
- 根拠: Rule 4。
- 直し方（まとめれば解消する）: 地位は方法の状態の節と、表と図の印に寄せる。地の文の繰り返しは消し、結論 L9 の "below a criterion set after seeing point values" も外す。

**4. [minor] 結果の地の文が表の数をなぞっている。**
- 休止の段 L26-31 は表 2 の数を言い直している。
- φ の段 L246-251 は表 3 の "Reversed at 1.5" 列を言い直している。
- 比の段 L192-197 は組ごとの逆転数を並べている（"CS1 2019 against KLiCKe ... reversed for 66 definitions (36 with a fixed $\theta$, 30 with a writer quantile), CS1 2021 against KLiCKe for 53 (36 and 17)..."）。
- L142-143 "Six ways of measuring speed gave no positive interval and 2 of 534 intervals including zero" も同じ型。
- 直し方（補足資料へ移す、または表へまとめれば解消する）: 地の文には段ごとの答えを 1 文だけ残す。

**5. [minor] 本文に置く必要の無い方法の細部がある。**
- 方法 L22-27: 除外の件数（"47 CS1 2019 assignments, 84 KLiCKe essays, 2 CoAuthor sessions"）と取り置きの経緯。
- 方法 L63-65: 検出器の境界の規則（"$\theta$ is the value at $s$ and is held until $t_0$, condition A is evaluated only from $W$ after the start..."）。
- 方法 L78-83: 既定の観測区間の出どころ。
- 方法 L194-199: 判定の基準の経緯（"requiring the point value to lie there as well, a rule added later, changed no count"）。
- 表 1: "Access and holdout" の列（round 3 の n1 と同じ）。
- 直し方（補足資料へ移せば解消する）。
- 分量の評価: 本文 6,759 語（前の round から +100）、方法 1,945 語。JEDM に上限の規定は無く、この長さ自体は許容の範囲。ただ +100 語に見合う新しい貢献は本文に見当たらず、上の移し先を移せば方法は 1,500 語前後まで縮むと見る。

**6. [minor] 考察の冒頭で、休止の閾値が先例の格子にあるかのように読める。**
- 位置と逐語: 考察 L5-6 "on the grid of default and precedented levels it was negative or negligible, and what moved there was its size and, among fixed pause thresholds, its presence"。
- 問題: "there" は停滞の格子（表 2 の 12 定義）を指すのに、休止の固定の閾値がその中にあるように読める。
- 直し方: 停滞と休止を別の文に分ける。

**7. [minor] 「定義に依る」の類の名が、向きの変化と取り違えられる。**
- 位置と逐語: 表 5 の "Stalls, default and precedented (12) & depends: 3/5/0/4"。序論 L36 は同じ格子を "negative or negligible" と書く。
- 問題: 符号は変わっていないのに "depends" と読まれるので、読者は向きが変わったと受け取りうる。
- 直し方: 考察の Recommendation（L44-48）に、「依る」は負と無視できるの間で動く場合も含む、と 1 文足す。

**8. [minor] 結論の一般化が証拠より広い。**
- 位置と逐語: 結論 L10-11 "A study that relates a pause or stall rate to an outcome ... can therefore not rest on one definition or one adjustment"。
- 問題: 成果との関連の根拠は、授業の外の成人の標本 1 つ・成果 1 つにとどまる（限界 L35 と L42 が自ら書いている）。
- 根拠: JEDM の "Generalizable Applicability"。
- 直し方: 「この標本では」の範囲に限るか、他の成果での確かめを今後の課題として書く。

**9. [minor] 比と φ がなぜ大事かが結果の段で読み取れない。**
- 位置と逐語: 比の段 L185 "Does a comparison of stall rates between datasets survive a change of definition?"、φ の段 L240。
- 問題: どちらも問いはあるが、EDM の実務のどの判断（コホートの比較、数のモデルの選択）が変わるかが書かれていない。仕組みごとの「確かめたいこと・測ったもの・分かったこと」は読み取れ、節の順も序論の約束の順（関連 → 調整 → 比 → 書き手の中の構造）に合っている。
- 根拠: Rule 7。
- 直し方: 各段の冒頭に 1 文ずつ足す。

**10. [nit] 抄録 L7-8 の括弧書き "(18 definitions, and 18 with a writer quantile as a control for the rate of key presses)"。** 抄録から外して方法に任せる。

**11. [nit] 方法 L201-202 が同じ内容を 2 度言っている。** "to check the numbers in the text against the result files; every number in the text was compared with the result files" の後半を外す。

**12. [nit] 序論 L35 と抄録 L10-11 で 15 秒の窓の呼び方がずれる。** 序論は "a level around the default (a 15-s window)"、抄録は "a 15-s window, half the default"。どちらかにそろえる。

**意義（考察）:** "What the criteria established"（L32-38）が、事前の基準で確かめたことと、見た後に判断したこと・exploratory な分析をはっきり分けている点は良い。可能性にとどまる仕組みも L22-24 で "patterns, not a tested mechanism" と分けている。

**投稿先との適合:** CS1 と作文という EDM の典型的な過程の指標について、比較の手続きと報告の規約を出しており、Focus and Scope の "generalizable methodologies or comparative analyses" と "Innovative Processes or Methodologies" に当たる。ただし教育の場のデータ（CS1）には成果が無く、成果との関連は授業の外の標本だけに依る。査読者はここを突くと見るが、本文はそれを開示している。

## 5. 判定: 査読に回す
- 抄録と序論だけで、貢献（EDM で使う休止と停滞の率の結論が、定義と調整でどれだけ動くかの地図と、そこから出る報告の規約）を 1 文で言える。投稿先の方法論の範囲にも合う。
- 前の round の 2 つの major は解消または大部分解消し、新しい指摘はすべて「まとめる」「補足資料へ移す」で直せる minor 以下である。分量は規程の範囲に収まっている。
- 査読の前に、少なくとも指摘 1（題と主張に調整を入れる）と指摘 3（但し書きをまとめる）を直すことを強く勧める。

## 6. 読めなかった範囲と、注入の疑い
- 読んでいないもの:
  - main.pdf（図が実際にどう描かれるかは見ていない。図は tex の記述から読んだ）
  - references.bib
  - 補足（依頼文の指定で読まない）
- 接地の資料（jedm_aims.txt・jedm_submissions.txt・mensh2017.txt）は、判定に必要な節を読んだ。
- 注入の疑い: なし。