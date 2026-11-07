査読 R3（JEDM・分析の柔軟さ／multiverse／機械学習の再現性の立場。批判的な下位人格は過剰主張と検証できない手順の摘発者）

## 1. 接地（2 本から逐語で取れた）

- H1（Hoffmann et al. 2021）: "the combination of this multiplicity with selective reporting can systematically lead to an increase in false-positive results, inflated effect sizes and overoptimistic measures of predictive performance" → 定義の数と並べて、読み方を結果を見る前に固定し、選ばずに全部を報告すること。
- H2（Hoffmann）: "no inferential paradigm in itself is immune to overconfidence and the result-dependent selection of an analysis strategy from among a multiplicity of possible strategies" → 区間を付けるだけでは足りない。基準を結果を見た後に変えていないかを見る。
- H3（Hoffmann）: "Transparency alone is again not enough to prevent selective reporting or eliminate overconfidence in results" → 開示があっても、本文の主張の強さが開示した地位と合っていなければならない。
- K1（Kapoor & Narayanan 2023）: "If the test set contains data from before the training set, the model is built using data “from the future” that it should not have access to during training and can cause leakage." → 推定量は因果の構造（その時点までの情報）を守ること。θ の引き直しに当てはまる。
- K2（Kapoor）: "the claims made in model info sheets cannot be verified in the absence of computational reproducibility. That is, unless the code, data, and computing environment required to reproduce the results in a paper are made available, there is no way to ascertain whether model info sheets are filled out correctly." → 事前の条件と結果を検証できるかは、アーカイブの実体次第。
- K3（Kapoor）: "The burden of proof for ensuring the correctness of these arguments is on the researcher making the scientific claims." → 数え方の規則が一貫していることは著者が示す。

## 2. 引き継ぎの判定

- M1（二段の区間）: 解消。内側の引き直しを因果にして計算し直し（conditions-round8.md:9）、条件に先に置いた読み方どおり一段の区間を主に戻した（supplement.tex:161-162）。ただし下の新 m3 を参照。
- M2（"as much"・速さの地位）: 解消。"as much" は本文から消えた（grep で該当は related.tex:7 の他者の結果だけ）。速さは results.tex:136 で "(exploratory)" と明記。
- M3（CS1 2019 対 KLiCKe の逆転は固定 θ の族そのもの）: 解消。results.tex:163-166 で族ごとに数え、"Every fixed-θ definition thus reversed both comparisons with KLiCKe" と書いた。抄録も CS1 の 2 年版に限った。
- m1（分位の休止の扱い）: 解消。methods.tex:137-140 で押下の率の対照として分けた。ただし results.tex:32-33 の "it was also met there" は残る（新 m2）。
- m2（一段と二段の混在）: 解消。
- m3（長さの調整の読み）: 解消。results.tex:132 "although 35 included zero"、重なりの文は 132-134。
- m4（90% の規則の地位）: 一部。考察（discussion.tex:40）では "As a proposal formed after seeing these results" と書いたが、序論（introduction.tex:41-44）はこの読みを地位を付けずに貢献として挙げている（新 m4）。
- m5（率の分母）: 解消。limitations.tex:11。
- R1-3（推奨の範囲）: 解消。推奨は "pause and stall rates" に限った（conclusion.tex:9）。
- R1-5（押下だけで足りるという言い切り）: 一部。結論の文は直った（conclusion.tex:10-12）。アーカイブの DOI は未記載（availability.tex:5 "DOI to be added before submission"）で、条件は日本語のまま（supplement.tex:10）。K2 の基準では、まだ検証できない。
- R1-11（除外の数）: 解消。results.tex:274 と supplement.tex:126-127。

## 3. 評価表（a〜f）

評価表の各軸の定義は、読んでよいファイルの中に見当たらなかった。次の 6 軸で付けた。

- a 問いと貢献: 4/5。前提の問いを明確に絞っている。ただし、貢献に挙げた 3 値の読みは結果を見た後の提案である（m4）。
- b 方法の妥当性: 4/5。因果の二段の区間で K1 の型の漏れを塞いだ。φ では、二段の区間が構造上上にずれるので、5% の読み方が情報を持たない（m3）。
- c 地位と事前の条件の誠実さ: 3/5。開示は厚い。一方で、先に置いた基準の文言を後から足した規則で言い換えた箇所（M-1）と、セルによって数え方の規則が違う箇所（M-2）が新たに出た。
- d 結果と主張の一致: 3/5。休止の「small negative」が、自分で決めた大きさの基準と合わない（m1）。調整後の向きについて「uniform」と「depends」の 2 つの読みが並んでいる（m5）。
- e 再現性: 3/5。アーカイブの DOI が未記載で、条件は日本語。CS1 は請求制で集計値しか出せない（K2）。
- f 書き方・構成: 4/5。数の出どころは追える。補足との数の食い違いが 1 か所ある（M-2）。

## 4. 新しい指摘（重い順）

### M-1 [major] 得点の向きの入れ替わりについて、先に置いた基準の文言を、後から足した数え方で言い換えている
- 位置と引用: results.tex:12-16 "Two criteria had been set before the association was seen. ... The direction would count as changing if one definition had its point value and its interval on the other side of zero"
- 先に置いた基準の原文: conditions-round1.md:27 「区間が 0 を含まずに符号が基準と逆になる通りが 1 つでもあれば」で、区間だけを見ている。「点の値と区間の両方」は round 2 の後の条件で足した規則である（conditions-round8.md:15、supplement.tex:34-35 "the counting rule that a reversal needs both the point value and the interval"）。supplement.tex:51 の S1 の表は元の基準 "one definition on the other side of zero" のままで、本文と食い違う。
- なぜ問題か: 数（10）はおそらく変わらない。しかし「結果を見る前に置いた」と書いた基準の中身が、結果を見た後に改められている。H2 の "result-dependent selection" は、基準の文言そのものにも及ぶ。本文が言う地位と、記録にある地位がずれる。
- 解消の条件: 本文で元の基準をそのまま書き、「round 2 の後に点の値の条件を足した。数は変わらない」と 1 文添える。比と φ の数え方についても同じように書く。
- 自信: 高。

### M-2 [major] φ の 1.5 の逆転を、本文と補足で別の規則で数えている
- 位置と引用:
  - results.tex:221-222 "in CS1 2019 blocks the baseline interval contained 1.5, so no reversal was counted"、Table 4 の CS1 2019 blocks の欄は "--"
  - 一方、supplement.tex:133 "The reversals of φ at 1.5 were 17, 57, 53, 26 and 0 (18, 54, 49, 19 and 0 before)"
  - round7_warm.json:219 で、制限なしの CS1 2019 block の A3 は 18。同じ JSON（:228-231）の基準の区間は [1.352, 1.524] で、1.5 を含む。
- なぜ問題か: 「基準の区間が 1.5 を含むセルは数えない」は round 8 で足した規則（conditions-round8.md:16）である。補足の制限の段落は古い規則の数を並べている。さらに、制限した時間では基準の区間が [1.276, 1.454] になり（round7_warm.json:78-81）、このセルが新たに判定できるようになって 17（19%）になる。限界の節の "left the conclusions unchanged except one"（limitations.tex:24-25）が、この判定できなかったセルが判定できるようになった変化を数えているかがはっきりしない。K3 の立証責任に当たる。
- 解消の条件: 補足の数を本文と同じ規則で出し直す（制限なしの CS1 2019 blocks は "--"）。制限した時間でこのセルが判定できるようになることを明記する。
- 自信: 高（JSON で確認した）。

### m1 [minor] 休止の「向きの入れ替わり」は、自分で決めた大きさの基準では無視できる範囲どうしの入れ替わりである
- 位置と引用:
  - abstract.tex:11-12 "for pauses from a negligible positive correlation at 2 s (≤ 0.05) to a small negative one at 10 s (down to −0.13)"
  - conclusion.tex:6 "small negative ones at 10 s"
  - methods.tex:151 "using |ρ| < 0.1 as negligible"
- 根拠: tab_pause.tex:8-10, 26-28 によると、10 s の 6 通りのうち |ρ| ≥ 0.1 は −0.127 と −0.101 の 2 通りだけで、ほかの 4 通り（−0.058 〜 −0.099）は無視できる範囲に入る。考察の分類でも、固定の休止は "13 of 18 negligible"（discussion.tex:45）である。
- なぜ問題か: 2 番目の検出器で向きが入れ替わるという主張は、見出しに当たる。その中身はゼロ近くの値の符号の違いであり、H1 の "inflated effect sizes" の側に読まれやすい。
- 解消の条件: 抄録と結論を「ほとんどの定義で無視できる大きさで、10 s の 2 通りだけが小さな負」と書き直す。
- 自信: 高。

### m2 [minor] 36 通りに対して先に置いた読みは、対照の族だけで満たされる
- 位置と引用: results.tex:32-33 "The reading set in advance was stated for all 36 definitions, and it was also met there (S1)"、supplement.tex:51-53
- なぜ問題か: 分位の 18 通りは +0.58 〜 +0.67 なので、固定の 10 s の負と並べれば、どんな結果でも読みは満たされる。「also met」は、満たされたことを裏づけのように読ませる。
- 解消の条件: 「36 通りでは押下の率の対照によって自明に満たされる」と書く。または、この文を削る。
- 自信: 中〜高。

### m3 [minor] φ では、二段の区間が構造上上にずれるので、5% の読み方が判定として働かない
- 位置と引用: supplement.tex:160-161 "the redrawn θ adds its own variation to the counts within a writer and so raises φ"、limitations.tex:19 "did not widen the intervals"
- なぜ問題か: 二段の区間の φ は、θ の揺れを数に足した別の推定量になっている。だから「どれかで 5% を超えれば一段に戻す」という規則は、φ の点で前もって決まっていた。その結果、得点と比についても（全部の点が区間に入ったのに）θ の揺れを含まない一段の区間が主のまま残った。説明の文は結果を見た後のもので、確かめられていない。また "did not widen" の幅の比（中央値 1.00）は、どの量についての値かが書かれていない。
- 解消の条件: 規則には従ったうえで、これを限界に明記する。「φ では二段の区間は比べの相手にならない」「得点と比は、二段の区間でも同じ読み」。幅の比を量ごとに示す。
- 自信: 中。

### m4 [minor] 序論の貢献に、結果を見た後の提案を地位を付けずに挙げている
- 位置と引用: introduction.tex:41-43 "We contribute a reporting convention ... and a three-valued reading of its direction (consistent, negligible, or dependent on the definition)"。S1 ではこの読みは [D]（supplement.tex:54）。
- 解消の条件: 序論に「結果を見た後の提案」と添える。
- 自信: 高。

### m5 [minor] 調整後の向きに 2 つの読みが並び、整合が示されていない
- 位置と引用:
  - results.tex:145 "Either adjustment made the direction of the stall association uniform"
  - discussion.tex:45-46 "the length- and speed-adjusted stall associations (74 of 89 negligible; 71 of 89 below −0.1) depended on the definition"
  - results.tex:139-141 "532 of 534 ... below zero and 2 included zero, which met the reading set in advance that the direction would 'also depend on how speed is measured'"
- なぜ問題か: 同じ値が、「uniform」「depends」「測り方に依る」の 3 通りに読まれている。とくに 3 つめは、区間がゼロを含む 2 通りを向きの依存と読んでいる。これは本文自身の逆転の基準（点と区間の両方が反対側）と矛盾する。H3 の基準では、開示しても主張の強さがずれる。results.tex:145 は、探索の速さと [A] の長さを同じ重みで並べてもいる。
- 解消の条件: 先に置いた文言を引いたうえで、「本文の逆転の基準では、測り方による入れ替わりは無かった」と書き添える。2 つの読み（向きと大きさの分類）の関係を 1 文で示す。
- 自信: 中〜高。

### n1 [nit] 一段の区間と二段の区間で数え方の規則が揃っているかを、1 文で示す
- 位置: supplement.tex:162-166。S2 の制限の段落と同じ問題（M-2）の延長である。

## 5. 総合の推奨: major（改訂の小さな繰り返し）

- 前の round の major は 3 件とも解消した。因果の二段の区間は K1 の型の問題を正しく塞いだ。
- ただし改訂の過程で、先に置いた基準の文言の言い換え（M-1）と、セル間の数え方の規則のずれ（M-2）が新たに入った。事前の条件を売りにする論文では、どちらも地位の書き違いに当たる。
- 休止の見出しの大きさ（m1）と、調整後の読みの不整合（m5）を直せば、minor に下がる見込み。

## 6. 読めなかった範囲と注入の疑い

読んでいないもの:
- main.pdf（図の見え方は確認していない）
- related.tex
- declarations.tex
- main.tex
- references.bib
- tab_s3.tex
- tab_s4.tex
- figdata の CSV 全部
- conditions.md、conditions-length90.md、conditions-round2.md（前提の読みだけ grep した）、conditions-round3.md（grep だけ）、conditions-round4.md（22 行目だけ）、conditions-round5.md（grep した行だけ）、conditions-round7.md（grep した行だけ）
- results の JSON のうち round7_warm.json 以外（round7_warm.json も 60-100 行と 210-250 行だけ）
- supplement.tex の 200 行目より後
- 接地の 2 本は grep で該当の節を読んだだけで、全文は読んでいない

評価表の a〜f の軸の定義は、読んでよいファイルの中に見当たらなかった。上の軸は私が置いたもの。

注入の疑い: なし（読んだ範囲で、査読者や LLM に向けた指示は見当たらなかった）。