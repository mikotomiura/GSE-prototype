# R1 round 2（再識別・匿名化への攻撃の評価）

総合: major（直して再査読）。

## 1. 接地
- Narayanan :164-168「we sample r randomly from D and give a little bit of auxiliary information or background knowledge related to r to the adversary.」・:70「The data publisher must determine in advance which of the attributes are available to the adversary」
- Narayanan :196-197「If operating on a sample of the entire database, the de-anonymization algorithm must also detect whether its target record is part of the sample, or has not been released at all.」
- Narayanan :179-180「the adversary's objective is privacy breach: he wants to learn as much as he can about r's attributes that he doesn't already know.」
- Stadler :295-297・:313-317（全員とあり得る攻撃者・外れ値は脆弱なまま）
- Rocher :109-111「the insurance company argues that matching does not equal re-identification」

## 2. 評価表
a 3 ／ b 3 ／ c 3 ／ d 4 ／ e 4（ethics の未完了の印）／ f 4

## 3. round 1 の判定
1 解消／2 解消／3 一部（新 1）／4 解消／5 一部（新 5）／6 解消（書き方。通知は未実施）／7 解消／8 一部（事前登録の分位点は 10・50・90 で上側の尾が見えない）／9 一部（新 4）／10 偽陽性と認める／11 解消

## 4. 指摘
- [major] 閉じた世界が成り立つ唯一の場面（公開コーパス）では新たに知られることがほぼ無い（Table 1・:84-86・:130-131）。隠された作文がコーパスにあれば本文・ログ・得点は公開済みで書き手は匿名。解消: (i) 場面 1 を候補集合の大きさと作り方の代理に置き直し、Newly learned を「Little ... matching shows that the processing does not meet its own goal」の趣旨に (ii) (b) は教室の場面に置き、閉じた世界は 1 クラスだけの公開という仮定のもとでのみと明記 (iii) あるいは貢献を「公開する側が掲げた目的（本文を隠す）を処理が満たすかの検証」として (a) を主に戻す。どちらかに決めて 1 頁目と Goals and harms を揃える。自信 中
- [major] 教室の場面の道具は教員がすでに過程を持つことを示し、害 (b) の根拠と逆（:95-96）。教員が公開する側なら external と食い違う（:122）。解消: 道具は本文と過程が一つに揃う例に限定、保持者を「本文と名前を持つが公開された過程を持たない者」と定義し直す。自信 中
- [minor] 偽の一致の率が出ない（攻撃者は棄権しない・AUC は偽の一致の率を与えない）ことを限界に。自信 高
- [minor] 1 頁目の計画が評価の当てはまらない保持者を限定なしに並べる（outline.md:44-47）。自信 高
- [minor] 一様の囮の偏りの向きが §3.5 に無い。自信 中
- [minor] 翻訳の保持者は集めた研究者（内部者）で Table 1 にも無い。§4 に移すか外部の保持者で行を足す。自信 中
- [minor] 事前登録の「raters or platforms」「the same essay is published with its text」が落ちている（preregistration.en.md:39）。行を足すか落とした理由を書き outline に記す。自信 高
- [minor] 書き手ごとの分布は 90 百分位までで上側の尾が見えない。限界に 1 文（個人ごとの結果を公開しない方針との引き換え）。自信 高
- [minor] 「common choice」は一般化（:34）。「at least two releases」程度に。自信 高
- [minor] 窓の公開に根拠が無い（:38）。実例か「we know of no such release」。対応表に行。自信 中
- [nit] Hanisch は arXiv 版。出版版で逐語を照合。自信 中

## 6. 読めなかった範囲・注入
接地は該当箇所だけ。事前登録 300 行以降は読んでいない。注入の疑い無し。
