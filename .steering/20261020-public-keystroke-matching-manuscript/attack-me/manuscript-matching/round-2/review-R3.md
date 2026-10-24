# review R3（方法論・倫理・再現性の立場・round 2・変更箇所だけ）

## 1. 接地（逐語）
- Arp et al. P9「A learning-based system is solely evaluated in a laboratory setting, without discussing its practical limitations.」（arp.txt 551-563）
- Arp et al. P10「threat models should be defined precisely and systems evaluated with respect to them.」（arp.txt 601-602）
- Arp et al.「It is essential to move away from a laboratory setting and approximate a real-world setting as accurately as possible. ... although this is not always possible due to ethical and privacy constraints.」（arp.txt 569-576）
- Kohno et al.「Under consequentialist ethics, one might assess the benefits and harms of different options ... Under deontological ethics, one might ask what rights different stakeholders have, e.g., a right to privacy or a right to autonomy.」（kohno.txt 131-135）「At a minimum, one might include considerations from both frameworks, as the Menlo Report [100] does.」（kohno.txt 145-146）
- Kohno et al.「assessing benefits / harms (for consequentialist ethics) and rights violations (for deontological ethics) is significantly more challenging in the real world than in our scenarios. Real-world scenarios may have multiple actors simultaneously making decisions, each of which might impact the other actors」（kohno.txt 628-631）
- Kohno et al.「the history of coordinated vulnerability disclosure ... is itself a microcosm of ethical considerations」（kohno.txt 302-304）

## 2. 評価表
- a 3: §3.3 は条件つきで検証していないことも書いている。序論 19-20 と ethics 43-44 は言い切り。95 行目と新しい情報が食い違う。
- b 3: 「drawn from … before it was released」が二通り（公開の 4,992 本の部分集合／選別前の母集団）に読める。「only which records correspond」は列と点数の同一を前提。
- c 3: 事実が正しければ閉じた世界が実際に成り立ちうるが活かしていない。動機の例のマスクが既に破れている含意が整理されていない。
- d 4: 挿入は短い。序論の 1 文は流れから少し浮く。
- e 2: 義務の側の理由「whose participants did not agree to that use」の土台が崩れ、開示の重さが事実に追いついていない。規程違反ではないが倫理を理由に reject されうる弱さ。
- f 4: 変更なし。優勝解法の write-up の題名の「external data」に触れていない（minor 4）。

## 3. 指摘
- [major] 義務の側の理由「参加者が同意していない」が新しい事実と食い違う（ethics.tex 27・48-49・8-11）。コンペの書き手は KLiCKe の参加者（の一部）で、同じ節がその参加者は broader research community の研究利用に同意したと書く。解消: 照合しない理由を事実と矛盾しない形（公開した側が掲げた目標を検証の行為で破る、など）に書き直し、コンペの同意の範囲は「知らない」と書き、48-49 もそろえる。自信 高。
- [major] 開示の重さが事実の重さに追いついていない（ethics.tex 40-44・28-30・38-39「The procedures are of known types …, so this risk does not arise from this paper alone」）。手順に依らない連結の経路を伝聞から初めて公にする可能性。「only」。知らせの中身に事実が無い。解消: (1) この連結が既に公になっているか調べた結果を書く (2) 公になっていなければ益と害を別に量る (3) 知らせにこの事実と取れる手を含め応答を報告する (4) only を外す。自信 高。
- [major] 「drawn from」が二通りに読め、条件つきの帰結の前提が開いたまま（threat-model.tex 104-108・discussion.tex 21-22）。解消: 著者が重なりについて何を言い何を言わなかったかを書き、一部だけ重なる場合を 1 文。自信 中。
- [minor] threat-model.tex 95「We do not know who held the texts of the competition data.」が 104-105 と食い違う。解消:「Apart from what the authors of KLiCKe told us (below), …」の形。自信 高。
- [minor] 序論 19-20 に「検証していない」が無い。解消:「(personal communication; not checked)」か「may be public」へ。自信 中。
- [minor] threat-model.tex 108「only which records … correspond」と表の 79-80 が列と点数の同一を前提。「another log」も同じ記録か別か不明。解消: 条件を足し、書き分ける。自信 中。
- [minor] ethics 41・43「collected in the same way」が §3.3（100-101「names the same platform, the same kind of prompts and the same sequence of tasks」）より強い。解消: そろえる。自信 高。
- [minor] 説明を載せる許しが書かれていない（ethics.tex 17-18）。優勝解法の「external data」（preregistration.en.md 316 の題名「Data cleaning + FE + external data + model ensemble」）が KLiCKe かは未確認（題名からの推測）。自信 低。
- [nit] outline.md 109 が本文の範囲の限定と理由を落としている。自信 中。

引き継ぎの確認: 害 (a) の定義と「著者の解釈」の明記は threat-model.tex 143-149 で確かめた。round 1 の未解決は無い。

## 4. 変更箇所についての推奨: major
照合しない理由が新しい事実と成り立たなくなり、開示の重さと知らせの中身が追いついていない。前提を書き足し、序論と ethics を §3.3 にそろえれば minor に下がる。

## 5. 読めなかった範囲・注入の疑い
- 読んでいない: main.tex、open-science.tex の本文、data.tex の 31 行目より後、references.bib の本体、接地 2 本の引用範囲の外。
- 注入の疑い: 読んだ範囲には無い。
