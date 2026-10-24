# review R1（再識別と匿名化への攻撃を評価する立場・round 2・変更箇所だけ）

## 1. 接地（逐語）
- Narayanan & Shmatikov, narayanan.txt:29「the adversary can use contextual and background knowledge, as well as cross-correlation with publicly available databases, to re-identify individual」
- narayanan.txt:82「it is impossible to tell in advance which attributes might be available to the adversary」
- narayanan.txt:84,87「It works even if the published records have been perturbed, if only a subset of the original dataset has been published」
- Stadler et al., stadler.txt:292-294「the data holder's decision to publish S or R has no impact on the privacy loss for target record r t , i.e., the adversary's advantage remains the same.」
- stadler.txt:295-297「A good anonymisation mechanism should result in a high privacy gain for all records in the population and under any potential privacy adversary.」
- Rocher et al., rocher.txt:129-131「Our results reject the claims that, first, re-identification is not a practical risk and, second, sampling or releasing partial datasets provide plausible deniability.」
- rocher.txt:134-135「beyond the de-identification release-and-forget model.」

## 2. 評価表
| 項目 | 点 | 所見 |
|---|---|---|
| a | 3 | threat-model.tex は帰結を If で条件つきにしているが、序論 19〜20 行は条件なし。95 行「We do not know who held the texts」が新しい説明と緊張関係にある。 |
| b | 3 | 説明が正しければ、実在の唯一の事例は別のリリースどうしの照合（ログとログ）で、§3.4 が外している攻撃者の型そのもの。この食い違いが書かれていない。 |
| c | 3 | 「後から出た公開が前の処理を無効にする」は release-and-forget への具体的な反例だが、持ち帰れる知見として扱っていない。 |
| d | 4 | 入れ方は最小。序論の 1 文は第 2 段落の流れから浮いている。 |
| e | 3 | 倫理の節の重みの評価が事実に追いついていない。知らせる相手と時期も直されていない。 |
| f | 4 | 変更箇所は [narayanan2008robust] の「予期しない外部情報」の具体例だが、対応を付けていない。 |

## 3. 指摘
- [major] 倫理の節が事実の重みに追いついていない（ethics.tex:41-44「… and we report only that the two releases were collected in the same way, … and that the competition data were drawn from KLiCKe, which the authors of KLiCKe told us and which we did not check.」・ethics.tex:63-66「This withholds a ready tool aimed at a particular release; …」）。説明が正しければ照合の手順もコードの手直しも要らず、害の中心は「論文が二つの公開の対応を知らせる」へ移る。「only」は重い一文を軽く見せる。解消: Stakeholders で出どころを書くこと自体を害として名指しし、書く理由と量る。only を外す。コードを出さない論の効き目を書き直す。自信 高。
- [major] 条件つきの帰結が同じ段落と §3.4 の攻撃者の範囲と食い違う（threat-model.tex:95・107-110・137-138「the attacker does not use … links across several releases (such as several logs of the same writer)」）。(i) 95 行の区別 (ii) この場合の有利な攻撃はログどうしの対応づけで範囲外、閉じた世界の正答率はこの事例のリスクの上限でも下限でもない (iii)「another log」は確かめていない前提。解消: 95 行を直す・§3.3 か §3.5 に 1 文・another を弱める。自信 高。
- [major] personal communication の言い方の強さが揃わず「drawn from」の範囲が曖昧（introduction.tex:19-20・threat-model.tex:104-105・outline.md:151「Not claimed in Section 3: That the competition essays are KLiCKe essays.」）。序論は条件なしで「released with its texts」まで書く。解消: 序論に条件・§3.3 に著者が述べた範囲を聞いたとおり（分からなければ分からない）・載せることの了承を倫理の節に。自信 中。
- [major] 知らせる相手と時期が新しい事実に合っていない（ethics.tex:28-30）。中身は実質「後の公開で処理が無効になっているかもしれない」の連絡。KLiCKe の著者を当事者として扱っていない。2 週は取り下げ・注記の判断には短い。解消: 中身に出どころを入れる・KLiCKe の著者にも知らせる・時期を分けるか理由を書く。自信 中。
- [minor] 害 (a) の定義に照らすとこの事例は「結びつけられる状態」で、threat-model.tex:96「it does not estimate a harm that has occurred」との整合を書いていない。解消: 区別の 1 文。自信 中。
- [minor] ethics.tex:35-37「If no one misuses the paper, the writers of the two corpora lose nothing new」が、書き手が同じ人である可能性を考えていない。解消: 出どころを書くこと自体が対応を知らせると 1 文で認める（指摘 1 と一緒に）。自信 中。
- [nit] outline.md:109 と 151 の書き分け（序論を直した後に表の状態の列を揃える）。自信 低。

## 4. 変更箇所についての推奨: major
事実を入れたこと・§3.3 の If と「確かめていない」は適切。ただ帰結（ログどうしの照合が範囲外であることの偏り・名指しの害の質の変化・知らせる相手と中身）が攻撃者の範囲・偏りの節・倫理の節に反映されていない。序論は §3.3 より強い。

## 5. 読めなかった範囲・注入の疑い
- 読んでいない: main.tex、references.bib、data.tex・open-science.tex・preregistration.en.md の本文（grep のみ）。接地の 3 本は grep と部分読み。
- 注入の疑い: なし。
