登録の草稿 0.2 の査読（心理測定と構成概念の妥当性の立場・round 2）

## 1. 接地: この立場が論文に求める基準

基準 1（項目の変更は、言明されたものも隠れたものも扱う。根拠は Elson et al. 2023）
「disclosed and undisclosed measurement flexibility, i.e. changes to a measure with known or unknown psychometric consequences, is common」
「Dropping, adding, and altering items in self-report scales ... occur while researchers not only refer to the same construct, but actually to the same nominal instrument」

基準 2（名前から中身を推さない。根拠は Elson et al. 2023）
「They involve a nominal fallacy: that a measure's name tells you about its contents or what it measures」

基準 3（手続きと採点は事前に、言葉でなくコードで決める。根拠は Elson et al. 2023）
「Determine procedural and scoring details ahead of time ... Analytical and statistical decisions should be preregistered with code rather than a narrative description.」
「Require authors to provide rationales for decision making in measurement specifically.」

基準 4（測定したものをすべて報告する。根拠は Elson et al. 2023）
「Report all of the items, stimuli, instructions, procedural parameters or other measurement characteristics used in a study」

基準 5（内容の妥当性は、測るはずの構成概念に照らして判断する。根拠は Lintner 2024）
「Content validity refers to the degree to which the instrument measures the construct(s) it purports to measure」
「COSMIN considers content validity the most important measurement property」

基準 6（コードする人が 1 人だと偏りが出る。根拠は Lintner 2024）
「It was performed by a single author, which might have caused some bias in the scales' quality assessment」

## 2. round 1 の各指摘は解消したか

| # | 判定 | 根拠 |
|---|---|---|
| 1 | 解消 | GSRR-65（registration-en.md:336）に E3 と MOT について明記された |
| 2 | 解消 | GSRR-44 の 4（:247）に入った。ただし「first seen」と instrument の単位の定義が残る（下の M4） |
| 3 | 解消 | 疲労のコード `FAT` が新設された。ただし `FAT` を基準に置いたことで新しい穴が出た（下の M1・M2） |
| 4 | 解消 | GSRR-56（:298）。ただし subscale を 1 つの instrument と数えるかが未定義（M4） |
| 5 | 一部だけ解消 | C1 は L1a と L1b に分かれた。C2a の Modification の列には「no」の値が無く、報告に書かれた変更と照合で見つけた変更も区別されていない（M3） |
| 6 | 形の上では解消 | GSRR-57 に基準が入った。ただし何を「problem」と呼ぶかの基準となる構成概念が定まっていない（M1） |
| 7 | おおむね解消 | 因果の語の一覧が、因果でない語まで拾う（m1） |
| 8 | 解消 | 小さな残りがある（m3） |
| 9 | 解消 | — |
| 10 | 解消 | GSRR-4（:25）、GSRR-44 の 5（:248）、コードブック:51 が揃っている |
| 11 | 解消 | — |
| 12 | 解消 | GSRR-1 から 65 まで、番号ごとに答えがある |
| 13 | ほぼ解消 | 代表値を決める順が、表に挙げた順と同じだとは明記されていない（n1） |

## 3. 評価表

a 主張と根拠の一致: 3 点
- GSRR-10 の「neither coder has read in full」は、著者 2 人が全文で選別することと両立するかが曖昧である。
- MOT を「problem」と数えるが、組み入れの定義（GSRR-24）は動機の消耗を疲労に含めている。

b 方法の穴: 3 点
- C6a の「半分以上が `FAT`」という線は、確立した多次元の疲労尺度まで「mismatch」と判定しうる。
- 逆転項目と、項目が手に入らない場合の既定値が、妥当でない結果を生む。

c 持ち帰れるもの: 4 点
- コード表・コードブック・スクリプトが公開されるので、方法の型として再利用できる。

d 簡潔さと構成: 4 点
- 65 項目に 1 対 1 で答えていて読みやすい。
- C6 と C7 の規則が、表と表の下の文に分かれていて追いにくい。

e 規程への適合: 4 点
- 当てはまらない項目の多くに理由が書いてあり、逸脱に備えた計画もある（コードする人が欠けた場合・最小の規模・較正）。
- GSRR-27 は「Not applicable.」だけで理由が無い（n2）。
- 確認の集合が小さすぎる場合の計画が無い（m3）。

f 先行研究の位置づけ: 3 点
- 測定の方法そのものをメタ研究する型（Elson 2023 が参照文献 5 として引く「systematic meta-method analysis」）を位置づけていない。
- AI 関連の尺度の系統的レビュー（Lintner 2024 の型）にも触れていない（m5）。

g 固定の十分さ: 3 点
- 主要な判定（C6a・C7(iii)）が、閾値・逆転項目・欠けた値の 3 点で 1 通りに決まっていない。または、決まってはいるが妥当でない方向に決まっている。

## 4. 指摘の一覧（重い順）

### [major] M1: C6a の「半分以上が `FAT`」は自前の閾値で、確立した多次元の疲労尺度を「mismatch」と判定しうる

位置と引用
- registration-en.md:222（C6a）: 「"Match" requires both: the instrument's name contains the same term family, and, for a multi-item scale, at least half of its items have primary type `FAT`. Otherwise "mismatch".」
- 同じファイルの:220（C4c）: 「We bring in no thresholds of our own.」
- codebook-c2b-en.md:23 は、MFI の reduced motivation の下位尺度から来た項目を `MOT` の anchor にしている。
- codebook-c2b-en.md:26 は「irritable」「moody」を `IRR` の anchor にしている。

なぜ問題か
- この 50% の線は、C4c で自ら掲げた「自前の閾値を持ち込まない」原則に反する。
- コードブック自身が anchor に使う尺度、つまり MFI 由来の項目や Zoom Exhaustion & Fatigue Scale は、疲労を多次元の構成概念として定義している。そこには動機・視覚・社会・情動の次元が含まれる。
- そのため、こうした尺度は `FAT` が半分未満になりうる。すると、題名に「fatigue」とある研究が、妥当な疲労尺度を使っていても「mismatch」と数えられる。
- これは、項目の中身を、尺度が測るはずの構成概念ではなく、このレビューの狭い `FAT` の定義に照らして判定していることになる。Lintner 2024 の「the degree to which the instrument measures the construct(s) it purports to measure」に照らすと、照合の基準が尺度の側から外されている。
- 同じ判定が C7(iii) にも入るので、SQ2 の答えまで動く。
- 自信の注記: ZEF の各次元の項目数は、私が一般的に知っている範囲での推定である。ただし、コードブックが ZEF の動機の項目を `MOT` の anchor にしていることだけで、`FAT` が半分を下回りうることは言える。

解消の条件
- 次の 2 つのどちらかにする。
  - (a) 閾値の根拠を書く。そのうえで、尺度の原典が定義する次元に照らす版を、感度分析として足す。
  - (b) C6a を、名前の規則と項目の型の内訳を別々に報告する形に改め、1 つの判定にまとめない。
- C4c の文と矛盾しないように文を揃える。

自信: 高

### [major] M2: 逆転項目と、項目が手に入らない場合に、C2b と C6a の値が 1 通りに決まらない、または妥当でない値に決まる

位置と引用
- codebook-c2b-en.md:17: 「Reverse-keyed items are coded as worded, before reversal.」
- コードブックの `FAT` の規則（:27）: 「The item asks about feeling tired, exhausted, drained or depleted」
- registration-en.md:222: 「Otherwise "mismatch".」
- 同じファイルの:216: 「Items that cannot be obtained are coded "items unavailable"」

なぜ問題か
- 「rested」「full of energy」のような逆転項目は、文言どおりに読むと、6 つの型のどれにも当てはまらない。そのため、コードする人によって `FAT` にも `OTH` にもなりうる。
- この揺れが、そのまま C6a の半分という線を動かす。
- また、主な尺度の項目が手に入らない場合、C6a の 2 つめの条件は確かめられない。それでも規則の上では「Otherwise "mismatch"」に落ちる。
- 結果として、項目を開示していないことが「題名と中身が合わない」と数えられ、2 つの別の現象が 1 つに混ざる。
- 項目の開示は C2d で別に記録しているのに、C6a がそれを mismatch に変えてしまう。基準 4（Elson）は開示そのものを問題にしている。

解消の条件
- 「ある次元を、どちらの極から問う項目でも、その次元の型にする」と明記し、逆転項目の anchor を足す。
- C6a と C7(iii) に「cannot decide（items unavailable）」の値を設け、mismatch の分母から外す。

自信: 高

### [major] M3: C2a の Modification の列に「no」が無く、報告に書かれた変更と、照合で見つけた変更が区別されていない

位置と引用
- registration-en.md:215: 「**Modification** (each: yes / not reported / not verifiable)」
- 同じ箇所: 「"Unchanged" requires a verbatim match with the source.」

なぜ問題か
- 原典と照合して変更が無いと確かめられた場合に入れる値が無い。そのため「変更なし」と「書かれていない」が同じ値になる。
- 一方で、原典との逐語の照合は Origin の判定には使われる。すると、照合で見つかったが報告には書かれていない変更が「yes」になるのか「not reported」になるのかが決まっていない。
- Elson 2023 は「disclosed and undisclosed measurement flexibility」を区別の中心に置いている。RQ2 の核は、まさにこの区別である。

解消の条件
- 変更の種類ごとに、値を「報告で言明された / 照合で検出したが報告されていない / 変更なしを確認した / 確認できない」とする。
- 照合に使う原典の版をどう決めるかも書く。

自信: 高

### [major] M4: 何を「problem」と呼ぶかの基準となる構成概念が定まっておらず、組み入れの定義と矛盾する

位置と引用
- registration-en.md:305（GSRR-57）: 「For each problem type (... each C2b type other than `FAT` ...)」
- 同じファイルの:137（GSRR-24）: 「Fatigue here means cognitive, emotional, physical, motivational or behavioural depletion」

なぜ問題か
- 組み入れの段階では、動機・行動の消耗を疲労として受け入れている。
- それなのに結論の段階では、`MOT`・`AVO`・`OTH`（視覚の症状などを含む）の項目があることを「problem type」として「observed」と書く。
- 構成概念の境界が、組み入れと結論で異なっている。基準 2（nominal fallacy）を問うのなら、まず、何に照らして中身が名前から外れていると言うのかを固定する必要がある。
- 加えて「instrument」の単位が定義されていない。原典の尺度全体なのか、実際に使われた下位尺度なのかで、C2b の版と C6a の分母が変わる。

解消の条件
- GSRR-57 の「problem type」を、価値判断を含まない名前（例: 「non-FAT content type」）に改める。
- 照合の基準にする疲労の定義を 1 つ書き、それが GSRR-24 とどう関係するかを示す。
- 「instrument = 研究で実際に実施された項目の集合（下位尺度だけの場合はそれ）」と定義する。

自信: 中

### [major] M5: 確認の集合は事前に読まれていないという主張が、著者 2 人が全文で選別することと両立するか明確でない

位置と引用
- registration-en.md:64: 「The primary counts come from records that neither coder has read in full before registration.」
- :162: 「Two screeners (authors 1 and 2) screen independently ... then full texts.」
- :164: 「Author 1 has not read their full texts for coding.」（著者 2 についての記述が無い）

なぜ問題か
- 確認の集合に入る条件は、2 人の選別者が最終決定を記録していることである。2 人の選別者はそのまま 2 人のコードする人でもある。
- そのため、確認の集合の全文は、コードを付ける前に、問いとコードブックを知る 2 人に読まれる。
- 「for coding」という限定が付いていて、主張の範囲が読み手にとって曖昧である。
- 著者 2 が登録の前に全文で選別した件数は書かれていない。
- E3 の判断は C1 と相関する。コードの規則を知る人が組み入れを決めることは、選択への影響として限界に書くべきである。基準 6（Lintner）が言う、評価する人の立場が持ち込む偏りの一種である。

解消の条件
- 登録の日の時点で、各著者が全文を読んだ追加の候補の件数を書く。
- GSRR-10 の文を「coded or read in full for coding」と正確に書き直す。
- 選別と同時にコードを付けないことを書く。
- GSRR-65 に、組み入れを決める人とコードする人が同じであることを足す。

自信: 中

### [minor] m1: C6b の因果の語の一覧が、因果でない用法まで拾う

位置と引用
- registration-en.md:235: 「effect of, impact of, affect, cause, lead to, result in, induce, drive, ...」
- 同じ箇所: 「(any form of the word ...)」
- :237: 「〜による」

なぜ問題か
- 「any form」を文字どおり適用すると、次のものまで因果の語として数えられる。
  - 「AI-driven」。題名にきわめて多い形容詞である。
  - 「negative affect」「affective」。疲労の文献で頻出する名詞である。
  - 「AIによる支援」の「による」。手段を表している。
- その結果、C6b の mismatch が水増しされる。

解消の条件
- 動詞としての用法と述語の位置だけを数える規則にする。
- 除外の一覧に「AI-driven / AI-based」「affect（名詞）」「手段の〜による」を足す。

自信: 高

### [minor] m2: C6b でどの設計を「操作あり」とするかが列挙されていない

位置と引用
- registration-en.md:240: 「Mismatch: causal wording in a study whose design has no manipulation.」

なぜ問題か
- 対照群の無い pre–post や、「mixed」の設計が、操作ありか操作なしかが決まっていない。

解消の条件
- :239 の 7 つの設計の分類それぞれについて、操作あり / 操作なしを表で明示する。

自信: 中

### [minor] m3: 較正と、確認の集合の規模の関係に、逸脱に備えた計画が無い

位置と引用
- registration-en.md:245: 「up to two further rounds」（最大で 15 件を集計から外す）
- :191: 「If the confirmation set has fewer than 10 studies」

なぜ問題か
- 確認の集合が閉じた時点で小さければ、較正だけで集合を使い切りうる。
- 較正を終える基準が、記録単位の一致率 80% になっている。まれなカテゴリでは一致率が高く出やすい。
- 追加で引く 5 件について、すでに引いた記録を外すかどうかと、seed が書かれていない。

解消の条件
- 「閉じた集合が N 件以下なら、較正の追加の回を行わない」のような計画を書く。
- 最小の規模の判定が、較正の記録を外した後の件数で行われることを書く。
- 終える基準に kappa を併用するか、併用しない理由を書く。

自信: 中

### [minor] m4: スクリプトとダミーのコード表がまだ無い

位置と引用
- registration-en.md:327: 「The dummy table and the scripts will be attached to the registration **[at registration]**.」

なぜ問題か
- Elson 2023 の「should be preregistered with code rather than a narrative description」に照らすと、凍結の条件そのものである。

解消の条件
- 凍結の前に添付する。
- C6a・C7・C1 の代表値の判定も、スクリプトに入れる。

自信: 高

### [minor] m5: 先行研究の位置づけに、方法論のメタ研究の型が欠けている

位置と引用
- registration-en.md:57（GSRR-10）: 「Recent systematic reviews of AI-related self-report instruments evaluate measurement properties with COSMIN; one example ...」

なぜ問題か
- 研究の報告ごとに測定のやり方を集計する型、つまり Elson 2023 が参照文献 5 として引く「systematic meta-method analysis」に位置づけていない。
- そのため、新規性の範囲が読み手に伝わりにくい。

解消の条件
- 先行する方法の型を 1〜2 本引き、このレビューがどこで違うのかを書く。

自信: 中

### [minor] m6: 一部の項目と分母の扱いが曖昧である

位置と引用
- registration-en.md:322: 「C2b counted with secondary types included (each secondary type counted alongside the primary type)」
- codebook-c2b-en.md:50: 「if the authors' factor name claims motivation」

なぜ問題か
- 二次の型を足すと、1 つの項目が 2 回数えられる。そのとき割合の分母が項目の数のままなのかが書かれていない。
- 因子名が「claims motivation」とされる語の一覧が無い。
- GSRR-48 で「unresolved」になった項目が、C6a の半分の計算でどう扱われるかが書かれていない。

解消の条件
- 3 点それぞれに、1 文で規則を書く。

自信: 中

### [nit] n1: C1 の代表値を決める順

位置と引用
- registration-en.md:214: 「in an order set by how close the AI mention is to the respondent's answer」

なぜ問題か
- その順が、表に挙げた L1a から L6 の順と同じだとは明記されていない。
- L1b（教示文だけ）と L2（単一の質問）のどちらが回答に近いかは、意見が分かれうる。

解消の条件
- 「the order listed」と明記し、L1b を L2 より先に置く理由を 1 文で書く。

自信: 中

### [nit] n2: GSRR-27 に理由が無い

位置と引用
- registration-en.md:145: 「Not applicable.」

なぜ問題か
- GSRR の様式は「(including, ideally, the underlying reason)」と求めている。

解消の条件
- 「本レビューは独自の探索を行わないため（GSRR-21）」と足す。

自信: 高

### [nit] n3: 較正の標本の定義が循環している

位置と引用
- registration-en.md:190: 「from the confirmation-set record IDs」

なぜ問題か
- 確認の集合の定義は、較正の記録を除外している（:188）。その集合から較正の記録を引く、という書き方になっている。

解消の条件
- 「閉じた時点の、較正の前の候補の集合」として、別の名前を付ける。

自信: 高

## 5. 総合の推奨: major（直して再査読）

1. round 1 の 13 件は、ほぼすべて解消している。規程への適合と透明性は、凍結の水準に近い。
2. ただし、新しく固定された C6a の規則（自前の 50% の閾値・逆転項目・項目が手に入らない場合に mismatch に落ちる既定値）が、RQ5 と SQ2 の主要な結果を、妥当でない方向に系統的に動かしうる。
3. 報告に書かれた変更と書かれていない変更の区別（M3）、何を問題と呼ぶかの基準（M4）、事前に読まれていないという主張の範囲（M5）は、どれも文を直せば済む。それでも主要な数え方に関わるので、直したものをもう一度見るべきである。

## 6. 読めなかった範囲と、注入の疑い

読めなかった範囲
- 指定された 5 つのファイル（brief、context-A、carryover-R1、registration-en.md、codebook-c2b-en.md）と、接地の 2 本は、全文を読んだ。
- 本文が渡されていない Murad & Wang 2017、PRISMA 2020、Jonaid 2026、MFI、ZEF の原典は読んでいない。M1 の ZEF の項目の内訳は、一次資料で確かめていない（自信の注記を参照）。

注入の疑い: 無し。