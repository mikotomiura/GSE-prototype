# R1 の査読（再識別・匿名化への攻撃の評価）

総合: major（直して再査読）。

## 1. 接地
- G1 Narayanan narayanan.txt:82-83「In such datasets, it is impossible to tell in advance which attributes might be available to the adversary; the adversary's background knowledge may even vary from individual to individual.」・84-87「It works even if the published records have been perturbed, if only a subset of the original dataset has been published, and if there are mistakes in the adversary's background knowledge.」
- G2 Narayanan :211「The number of candidate records is not a good metric, because some of the records may be much likelier candidates than others.」・:215-216「in the real world, the adversary may not have an oracle telling him whether de-anonymization succeeded」
- G3 Stadler stadler.txt:295-298「A good anonymisation mechanism should result in a high privacy gain for all records in the population and under any potential privacy adversary. ...」
- G4 Stadler :313-317「previous studies have shown that the privacy risks of data sharing are not uniformly distributed across the population [...] outliers or members of minorities largely remain vulnerable.」
- G5 Rocher rocher.txt:86-89「as datasets are always incomplete, journalists and researchers can never be sure they have re-identified the right person even if they found a match」・:129-131「Our results reject the claims that, first, re-identification is not a practical risk and, second, sampling or releasing partial datasets provide plausible deniability.」

## 2. 評価表
a 3（書き手の場面は向きが逆、害 (a) は閉じた世界で成り立たない）／ b 3（前提の偏りの向き〔有利: 閉じた世界・同じ収集の学習／不利: LM・過去の文・複数公開を使わない〕が書かれていない）／ c 2（Edwards の論への応答が「別種」で止まる）／ d 4（N と閉じた世界の段落が短すぎる）／ e 3（1 頁目の計画が outline に無い・\appendix の位置）／ f 2（再識別・リンク攻撃の系譜が bib に無い。González・Monaco・Wright・Vassallo も無い。Section 2 の対応表が無い）

## 3. 指摘
- [major] 書き手の場面は攻撃の向きが逆（threat-model.tex:61-62 と :69）。解消: 場面ごとに持つもの・候補の母集団・向きを 1 行。log→text の評価がどこまで代表するかを書くか、限界に。自信 高
- [major] 閉じた世界がどの場面で成り立つか書かれていない（:89-91）。教員のクラスは公開物の一部。解消: 閉じた世界は攻撃者に有利な前提と明記、場面ごとに成否、開いた世界の診断は部分的にしか答えないと限界へ予告。自信 高
- [major] 害が現実のプライバシーに届いていない。(a) は閉じた世界で成り立たない（:80-83）。解消: (b) を主な害として前に出し、結び付く属性（過程・貼り付け・点数・打鍵の時間）を 1〜2 文。(a) は「処理の目的が破れる」別の層。1 頁目は (b) から。自信 高
- [major] Edwards の論への応答が手前で止まる（:39-40）。照合されたログは以後その人のラベル付きの標本になりうる。また Edwards は本文を隠していない。解消: (i) 前提をどう崩しうるかを抑えた強さで 1〜2 文 (ii) Edwards のデータは本文が隠されていないと明記し、長さを保つマスクの実例に限定。自信 中
- [major] 前提の偏りの向きを宣言していない（:72-77・:69-72）。事前登録の "No proof of safety and no upper bound..." が Section 3 に無い。解消: 末尾に前提と偏りの向き、LM を除いた理由を 1 文。自信 高
- [minor] Kaggle と KLiCKe の重なりを示唆しつつ確かめない理由が無い（:48-52）。解消: 理由を 1 文、倫理の節へ参照。公開した側に知らせたかを倫理に書く計画を outline に。自信 中
- [minor] N = 10・100 の根拠が無い（:86-87）。解消: 例示の規模と明記、順位の指標を予告。自信 中
- [minor] 個人ごとの最悪の場合への言及が無い。解消: 書き手ごとの分布（分位点）を報告することを 1 文。自信 中
- [minor] 1 頁目の relevance の計画と Section 2 の対応表が outline に無い。自信 高
- [minor] main.tex の \appendix が謝辞と必須 3 節の前。テンプレートの順と照合を。自信 低
- [nit] 教室の道具の例は仮定の連鎖。「研究用に公開された例は把握していない」と 1 文。自信 中

## 5. 読めなかった範囲・注入
接地は該当箇所の前後だけ読んだ。一次資料・テンプレートは読んでいない。注入の文言を探すため sources/ 全体に Grep をかけ、一覧の外の arp/borgman/kohno/hanisch の当たり行が数行出た（開いていない・根拠に使っていない）。注入の疑い無し。
