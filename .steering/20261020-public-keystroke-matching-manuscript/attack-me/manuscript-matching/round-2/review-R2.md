# review R2（データを公開・管理する側の立場・round 2・変更箇所だけ）

## 1. 接地（逐語）
- G1 Borgman, borgman.txt 192–195「Good stewardship means releasing some kinds of data and preventing the release of other kinds of data. The same data may fall into either category, depending on the time, purpose, or entity requesting access.」
- G2 Borgman, borgman.txt 1591–1592「As records are mined and combined, tracking sources and policies associated with individual datasets becomes more difficult.」
- G3 Borgman, borgman.txt 1312–1315「information that can be used to distinguish or trace an individual's identity, either alone or when combined with other personal or identifying information that is linked or linkable to a specific individual.」
- G4 Hanisch et al., hanisch.txt 77–79「Context information and habits being represented as strong signals in the data further complicate effective anonymization.」
- G5 Hanisch et al., hanisch.txt 2420–2422「the attacker models should be made explicit and common」・2447–2448「most anonymization techniques are only evaluated rudimentarily with the assumption of a weak attacker」
- G6 Hanisch et al., hanisch.txt 512–514「it is not uncommon that behavioral data are sold to third parties or released unintentionally through a breach or hack」

## 2. 評価表
- a 3: 出どころは明記。条件が付くのは §3.3 だけで序論は条件なし。§3.3 前半の「We do not know who held the texts」「it does not estimate a harm that has occurred」が新しい文と食い違う。
- b 3: drawn from が全件か一部か不明（discussion.tex 21「logs that did not pass the selection of the KLiCKe release」）。重なりを確かめる方法は照合のほかにもある（尋ねる）。
- c 2: 「元の集まりを後で公開すると先の伏せ字の公開が無効になる」という教訓を書いていない。§6.3 にも無い。
- d 4: 挿入は短い。§3.3 末尾と表 1 の 1 行目でほぼ同じ文が 2 回。
- e 3: 倫理の論の前提が変わるのに義務と関係者の段落が追いついていない。
- f 3: 新しい引用なし。Borgman や Narayanan と結べる。

## 3. 指摘
1. [major] 義務からの論拠と関係者の区分が崩れている（ethics.tex 27–28・48–49・33–34）。同意は人と目的に付く。解消: 拒む根拠を「別の当事者が別の約束の下で出した公開で、その条件と主催者の意図を確かめていない」の形に。重なる書き手は二つの公開に同時に入りうると 1 文。自信 高。
2. [major] 名指すことの害の性質が変わったのに「report only」で済ませている（ethics.tex 41–44）。対応を最初に公にするのはこの論文。KLiCKe の著者の承諾・通知（28–30）に重なりの記載を含めるかが書かれていない。解消: only を外し、新しく知られうるもの・著者の同意・通知に含めて応答を報告することを書く。載せない選択肢と比べる 1 文。自信 高。
3. [major] §3.3 の前半（95・95–96）が古いまま残り、107–110 と食い違う。序論 19–20 は条件なしで、動機の例の公開がすでに無効になったように読める。解消: 95 行目を直し、96 行目の「起きた害」を書き分け、序論に if と「評価は処理について行う」の一句。自信 高。
4. [major] 個人的な連絡の範囲が不明なまま帰結に使っている。確かめない理由も弱い（threat-model.tex 104–107）。尋ねることは照合ではない。解消: 連絡が範囲について何を述べ何を述べなかったかを 1 文。尋ねたか・通知で尋ねるかを書く。ethical reasons は照合しない理由に限る。自信 中。
5. [minor] threat-model.tex 109–110「another log of the same writing」が不正確。matching が論文の攻撃か突き合わせか区別がない。解消: 書き分け、攻撃は要らないかもしれないと一句。自信 中。
6. [minor] threat-model.tex 148「We read the stated goal as keeping the text apart from the rest of the log, and this reading is ours.」に、連絡が影響する（伏せ字の目的はコンペの期間に限ったものだったかもしれない）ことを書いていない。解消: 1 文足す。自信 中。
7. [minor] 公開する側に持ち帰らせる教訓（出どころとその後の公開を追う）を §6.2 か §6.3 に書いていない。自信 中。
8. [nit] 序論の「The essays of the competition」と §3.3 の「the competition data」の言い方のずれ。自信 低。

## 4. 変更箇所についての推奨: minor
出どころを明記し §3.3 は条件文で抑えている。倫理の節が新しい前提に追いついていない（1・2）。数段落の書き直しで済むが、通知と同意の 2 点は事実を確かめる必要がある。

## 5. 読めなかった範囲・注入の疑い
- 読んでいない: main.tex・data.tex（grep 行を除く）・open-science.tex（grep 1 行を除く）・references.bib。接地 2 本は該当箇所の前後だけ。
- 注入の疑い: 無し。
