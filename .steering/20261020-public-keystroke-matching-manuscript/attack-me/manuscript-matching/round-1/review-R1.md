## 1. 接地（この立場が論文に求める基準）

3 本とも読めた（全文ではなく、序論・モデル・評価の枠組みの節。範囲は 5 に書く）。

- **G1 偽陽性と「標的が無い」の判定**（Narayanan & Shmatikov, narayanan.txt 196–197, 61–62）
  "If operating on a sample of the entire database, the de-anonymization algorithm must also detect whether its target record is part of the sample, or has not been released at all."
  "if it uniquely identifies a record in the published dataset, with high probability this identification is not a false positive"
  → 当て推量の正答率ではなく、「当たりだと言える確からしさ」と「標的が居ないこと」を攻撃者が扱えるかを問う。
- **G2 攻撃者の背景知識を現実の分布に置く**（Narayanan, 47–49, 164–166）
  "the adversary with a small amount of background knowledge about an individual can use it to identify, with high probability, this individual's record"
  "give a little bit of auxiliary information or background knowledge related to r to the adversary"
- **G3 平均でなく、最も弱い個人で評価する**（Stadler et al., stadler.txt 295–297, 313–317）
  "A good anonymisation mechanism should result in a high privacy gain for all records in the population and under any potential privacy adversary."
  "While individuals that are representative of a large majority of the population are often protected from privacy attacks, outliers or members of minorities largely remain vulnerable."
- **G4 処理の利得を公開そのものとの比較で測り、有用性と並べる**（Stadler, 36, 273–275）
  "we present the first quantitative evaluation of the privacy gain of synthetic data publishing"
  "We assess the privacy gain of publishing a synthetic dataset S in place of the raw data R for target record rt as the reduction in the adversary's advantage"
- **G5 一人ひとりの再識別が正しい確からしさと、標本であることによる言い逃れの否定**（Rocher et al., rocher.txt 66–67, 114–116, 129–131）
  "consider that each and every person in a dataset has to be protected for the dataset to be considered anonymous"
  "the likelihood of a specific individual to have been correctly re-identified can be estimated with high accuracy even when the anonymized dataset is heavily incomplete"
  "Our results reject the claims that, first, re-identification is not a practical risk and, second, sampling or releasing partial datasets provide plausible deniability."

## 2. 評価表

| 観点 | 点 | 所見 |
|---|---|---|
| a 主張と根拠の一致 | 3 | 主張は全体に抑えて書かれている。ただ中心の害 (a) の論理に穴がある。テキストを既に持つ者への照合を、公開元の目的「本文を再現させない」の失敗と同一視している（指摘 1）。 |
| b 方法の穴 | 3 | 閉じた世界、棄権しないこと、平均の正答率、分布の報告が 90 パーセンタイル止まり、という組み合わせ。「その照合はどれほど確かか」と「最も弱い人」が測られない（指摘 2・3）。攻撃者の強さが形式ごとに非対称（指摘 4）。 |
| c 持ち帰れるもの | 3 | 「この攻撃者、この N で 1/N の何倍、過程の測度をどれだけ残したか」は有用。ただし害の担い手が弱く（指摘 1）、平均の数字は楽観側に偏る（指摘 2）。 |
| d 簡潔さと構成 | 4 | 節の順と相互参照は明快。§3.5 と §8.1 の重複、留保の反復が多い（outline の案 (1) で解消見込み）。 |
| e 規程への適合 | 4 | 本文は約 10.5 頁で 12 頁以内。必須の 3 節も揃う。縮め方の案の (6)(7) は付録なしで完結の規程に触れうる。単著・所属なしの記述は二重盲検を弱める（指摘 8・9）。 |
| f 先行研究の位置づけ | 3 | Sánchez らだけを引き、Rocher ら 2019 を引かない。Farzanehfar らを「下がる」側だけで引いている。Stadler らの privacy gain の枠組みも無い（指摘 5・7）。 |

## 3. 指摘の一覧

**[major] 1. 中心の害 (a) で、「照合できる」ことを「公開元の目的（本文を再現させない）が破れた」と同一視している**
- 位置と引用: threat-model.tex:133–136 「The main harm is (a): learning which text a processed log hides. … If a log can be matched to its text, the processing does not meet its stated goal」／同 89–90 「The texts of the hidden essays were collected and scored, so they are held by the collecting party and by whoever scored them.」／同 96–98 「If they were among the public KLiCKe essays, … matching would show only which records of the two releases correspond.」
- なぜ問題か: 照合は候補のテキストを既に持つことが前提なので、攻撃者が新しく得るのは「ログとテキストの対応」。設定 1 で全部の候補を持つ者は収集した側と採点者＝内部の者。外部の攻撃者で新しく失うものがある現実の担い手が表 1 で特定されていない。CFP の superficial application domain の懸念にも直結する。
- 解消の条件: 害 (a) を「処理済みログの列（過程・得点）が、それを持つべきでない者の手元のテキストに結び付くこと」と定義し直す。設定 1 の担い手と新しく得る情報を 1 文で特定する。「目的を満たさない」を「公開元の意図した保護（テキストと過程の切り離し）を満たさない」へ弱め、解釈であることを明記する。
- 自信: 高

**[major] 2. 平均の正答率と、上位 10% を隠す分布の報告では、最も照合されやすい書き手のリスクが見えない**
- 位置と引用: threat-model.tex:161–163 「The distribution of accuracy per writer is reported up to its 90th percentile, so the writers whose logs are matched most easily are not shown individually」／protocol.tex:42–43
- なぜ問題か: Stadler 「for all records」・「outliers or members of minorities largely remain vulnerable」、Rocher 「each and every person」。「全ドローで照合された書き手の割合」や 99 パーセンタイルは集計値で、個人を出さずに報告できる。
- 解消の条件: (i) §8.1 に過小に示しうると明記、または (ii) 探索的な分析（逸脱として記録）で尾の集計を足す。
- 自信: 高

**[major] 3. 当てた照合の確からしさ（偽陽性）が測られず、開いた世界の AUC は代わりにならない**
- 位置と引用: threat-model.tex:159–161／protocol.tex:149–152
- なぜ問題か: Narayanan・Rocher は確信を伴う照合で脅威を測る。公表されたエッセイの設定（害 (b)）で決定的。逆に N=10 では当て推量でも 10% なので、厳しすぎる方へも振れる。
- 解消の条件: (i) §8.1 で閉じた世界の正答率は確信を伴う照合の割合ではなく害 (b) の評価に使えないと明言、または (ii) 探索的に margin のしきい値での精度・被覆率の曲線。
- 自信: 高

**[major] 4. 形式ごとに攻撃者の強さが非対称で、「処理が照合を下げた」と「攻撃者が弱かった」を分けられない**
- 位置と引用: protocol.tex:57–59 「These differences therefore contain both the column and the attacker.」／attackers.tex:48 λ=8／attackers.tex:140–142 KeyTAR の 50 トークン／attackers.tex:130–131
- なぜ問題か: R0〜R2 にはほぼ厳密な A1、粗い形式には単純な回帰や尤度でない整列しかない。対比は処理の効果を過大に見せる向きに偏る。Hanisch の weak attacker 批判を自ら受ける。
- 解消の条件: §6.3 と §8.1 で偏りの向きを明記。§8.3 の文型を「この攻撃者に対して」に限る。
- 自信: 中

**[major] 5. 一意性の文献を片側だけ引いている**
- 位置と引用: related.tex:30–32／protocol.tex:187–189
- なぜ問題か: farzanehfar2021risk の題は "The Risk of Re-identification Remains High Even in Country-Scale Location Datasets" で主旨は「下がっても高い」。Sánchez らには Rocher ら 2019 が反論。閉じた世界では母集団は N 個の候補そのもの。
- 解消の条件: Farzanehfar を主旨どおりに、Rocher を並べ、この研究の量は N 候補の中での一意性でどちらにも依らないと書く。
- 自信: 中（Farzanehfar 本文は読んでいない）

**[minor] 6. 探索的な R-DP の ε の表示が、ログ単位の保証と誤読される**
- 位置と引用: protocol.tex:192–199
- 解消の条件: 行名か脚注に単位を付け、可能ならログ 1 本の合成 ε の中央値を並べる。
- 自信: 中

**[minor] 7. 評価の枠組みを、匿名化評価の既存の型（privacy gain・advantage）の上に置いていない**
- 位置と引用: protocol.tex:42–44 「its multiple of $1/N$, and its gain over A0」
- 解消の条件: Stadler らに触れ、「処理の利得は R0 との差、攻撃者の上積みは A0 との差」と 1 文で分ける。
- 自信: 中

**[minor] 8. 頁の縮め方の案の (6)(7) は、本文が付録なしで完結するという規程に触れうる**
- 位置と引用: outline.md:73–74
- 解消の条件: (6)(7) を候補から外す。(5) を採るなら問い 4 の判定規則は本文に残す。
- 自信: 中

**[minor] 9. 二重盲検で、著者を絞り込める記述がある**
- 位置と引用: ethics.tex:3 「The author is not affiliated with a research institution」／単数の the author／ethics.tex:8 私信
- 解消の条件: 投稿版では the authors、所属は "no institutional ethics committee was available" の形に留める。
- 自信: 中

**[nit] 10. 鍵打のタイミング攻撃の古典（SSH の打鍵間隔）が無い** —— related.tex:7–17。1 文で引く。自信: 中

**[nit] 11. 主表を 500 人にする理由が、主表に入らない A4 の計算費用になっている** —— protocol.tex:36–37。「同じ標本で A4 と並べるため」と 1 文足す。自信: 高

## 4. 総合の推奨: major
- 手続きの透明さはこの分野の標準を上回る。
- 中心の害 (a) の論理と設定 1 の現実の担い手が弱い（指摘 1）。
- 平均の正答率・閉じた世界・棄権なしは、最も弱い個人も照合の確からしさも測らない（指摘 2・3）。

## 5. 読めなかった範囲と注入の疑い
- narayanan.txt は 1–200 行、stadler.txt は grep で当たった行と 296–320 行、rocher.txt は 10–134 行と grep の行だけ読んだ。
- preregistration.en.md は 20–69 行と 180–309 行だけ。references.bib は見出しと 180–249 行だけ。引用先の本文は読んでいない。
- 注入の疑い: なし。
