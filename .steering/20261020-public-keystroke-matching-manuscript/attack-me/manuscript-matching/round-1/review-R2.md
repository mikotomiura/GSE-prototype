# 査読報告（PoPETs 2027・データを公開・管理する側の立場の査読者・stage: manuscript・round 1）

対象: commit 727647a2 の原稿。読んだのは main.tex、sections/*.tex の全部、references.bib（項目の見出しと hanisch の項目）、outline.md の全文、事前登録の §Questions・§Threat model・§Ethical〜§Open items。

## 1. 接地
- B1 Borgman, borgman.txt:192-195「Good stewardship means releasing some kinds of data and preventing the release of other kinds of data. The same data may fall into either category, depending on the time, purpose, or entity requesting access.」
- B2 Borgman, borgman.txt:1956-1961「data scientists have been remarkably effective at reidentifying individuals by aggregating records from multiple sources. Researchers who wish to use sensitive data … often are required to sign agreements that they will not attempt to re-identify the research subjects.」
- B3 Borgman, borgman.txt:1312-1315「PII means information that can be used to distinguish or trace an individual's identity, either alone or when combined with other personal or identifying information that is linked or linkable to a specific individual.」
- B4 Borgman, borgman.txt:2420-2436「Anonymity, which is fundamental to most methods of privacy protection, has become extremely difficult to sustain as methods of re-identifying individuals become more sophisticated. Notice and informed consent remain necessary but are far from sufficient」
- H1 Hanisch, hanisch.txt:2230-2235「We find this methodology too simple as the underlying assumption is that the attacker is not aware of the anonymization. … the evaluations should also consider an attacker that actively tries to reverse the anonymization and knows the anonymization technique and its parameters.」
- H2 Hanisch, hanisch.txt:412-413「The utility of the provided service may be assessed as the performance in carrying out those tasks.」／430-435「behavioral data carry a wealth of potentially sensitive information that can also be abused … correlated with different diseases …, mental states and emotions」
- H3 Hanisch, hanisch.txt:2420-2433「the attacker models should be made explicit and common … an anonymization method should also work on a small group size with high data quality.」

## 2. 評価表
| 項目 | 点 | 所見 |
|---|---|---|
| a | 3 | 慎重に限定。ずれが 2 つ: (1) 問いは「加工は自身の目標を満たすか」だが、目標は reproduction を防ぐことで、測るのは linkage。(2) 倫理の「the paper gives releasing parties the means to measure it」と Open science の公開範囲の制限が食い違う。 |
| b | 3 | H1 前半と H3 の小さな N は満たす。穴は 4 つ: 得点列を準識別子として使う攻撃者がいない（B2）、加工を戻そうとする攻撃者が R7・R-DP に弱い、有用さの軸が 10 の測度だけで Inputlog と未照合、設定 1 の外部の攻撃者が不明。 |
| c | 2 | 公開する側が判断に使える形がまだ無い。「do not recommend a form」が 4 か所。自分のログで評価を回すコードの道は閉じている。§8.3 の空欄は減点しない。 |
| d | 3 | 同じ限界が §3.5・§5・§4.3・§8.1 に繰り返し出る。「ログを外部の AI に送らない」も 3 か所。 |
| e | 4 | 10.5 頁・必須の 3 節はテンプレートどおり・1 頁目で実世界との関係を述べる。縮める案の (2)(5) と所属の文が気になる。 |
| f | 3 | 鍵打の側と Hanisch の引用は正確（「rudimentarily … weak attacker」は hanisch.txt:2448 で照合済み）。統計的開示制御・開示の筋書き・アクセスの段階・k-匿名性・learning analytics のプライバシーの文献が無い。 |

## 3. 指摘の一覧
- [major] 測っている害が、公開側の述べた目標とも、現実の害とも一段ずれている
  - 位置: introduction.tex:21-22／threat-model.tex:133-136／表 1 の 1 行目（75-78）
  - なぜ: 候補を持つ者に照合は本文を新しく教えない。設定 1 で閉じた世界が成り立つ持ち主は集めた側か採点者、公開コーパスは対応だけ。評価が直接効く設定ほど害が小さい。KeyTAR は脅威モデルの外。B3 は linkable を PII に含めるので結び付けを害に立てるのは筋が通るが、目標の文言からは引き出していない。H2 の機微な属性（貼り付けや生成 AI の疑い等）を具体的に言っていない。
  - 解消: 1 頁目と §3.4 で (i) 目標は再現・測るのは結び付けで、関係を一文で論じる (ii) 設定 1 の外部の持ち主（委託の採点者は releasing party か）(iii) 結び付いた過程の列から新しく分かること。
  - 自信: 高
- [major] 公開物に一緒に入る得点が準識別子として扱われていない
  - 位置: threat-model.tex:21-22／89／135-136
  - なぜ: 採点者は得点も持つ。得点が公開物にあれば候補を絞れる。§3.5 の偏りの一覧に、攻撃者を弱める仮定がもう一つ抜けている。B2。
  - 解消: §3.5 と §8.1 に、攻撃者は公開された得点や付随の列を使わない・採点者の設定では過小評価になる・得点の公開も選択の一つ、と書く。探索として足すなら逸脱に記録。
  - 自信: 中〜高（Kaggle の得点の公開のされ方は確かめていない）
- [major] 「公開する側が測れる」という主張と、コードの公開範囲が食い違っている
  - 位置: ethics.tex:36-37「this risk exists whether or not the evaluation is published, and the paper gives releasing parties the means to measure it」／open-science.tex:13-14「We do not write or publish code that reads other released keystroke logs directly」
  - 解消: (a) 倫理の利益の主張を「二つのコーパスで、加工の種類ごとの数を示す」に弱める、または (b) 公開されたログを読むコードと、公開する側が手元のログを文書化した中間の書式に変換して流す入口を区別し、後者の公開の有無と理由を書く。
  - 自信: 高
- [major] 有用さの軸が狭い。加工以外の公開の選択肢が、評価の枠にも議論にも無い
  - 位置: protocol.tex:72-73／132-133／discussion.tex:50
  - なぜ: 測度だけを出す・審査付きのアクセスという選択肢が並ぶ（B1）。図の軸は 10 の測度だけで、生のログを出す理由（未定義の測度・得点の予測）が入らない。§8.2 はアクセスの段階に触れない。
  - 解消: (i) 軸は 10 の測度の保存しか表さない (ii) 測度だけを出す・段階的アクセスは評価の外の選択肢 (iii) §8.2 を「誰にどの形を渡すか」に広げる。
  - 自信: 中
- [minor] 頁の縮め方の案の一部が「appendices なしで完結」とぶつかる —— outline.md:69-72。区切りの規則の誤り（77.1%）とエスケープの逸脱は本文に残す。登録の段落は §6 に 2 文残す。問い 4 は量・区間・判定の 1 文を本文に。(1)(4) は妥当。自信: 中
- [minor] 同じ限界と方針の繰り返し —— threat-model.tex:165-166 と discussion.tex:11-13／threat-model.tex:171-172・protocol.tex:135-136・discussion.tex:66-67／data.tex:139-140 と discussion.tex:19-21／attackers.tex:34-36 と discussion.tex:21-23／data.tex:158・ethics.tex:63・ai-use.tex:8。限界は §8.1 に一か所。自信: 高
- [minor] 公開する側の実務の文献に位置づけていない —— related.tex:28-34。表 1 は開示の筋書きの分析そのもの。Borgman「Students may not know what is being collected about them」（borgman.txt:1266-1268）。1〜2 文で参照。自信: 中
- [minor] 加工を戻そうとする攻撃者が無い（R7・R-DP） —— attackers.tex:54／protocol.tex:203-204。hanisch.txt:2198-2200「the strong dependency both temporal and physiological is a problem since they can be used to filter out the noise」。§8.1 に一文。自信: 中
- [minor] 倫理の節の所属の文と、外部の審査の不在 —— ethics.tex:3-4。「no institutional ethics committee was available」とし、所属に頼らない外部の審査を考えたかと受けなかった理由を一文で。自信: 中
- [nit] 「現実的な大きさ」の推論が弱い —— threat-model.tex:93-95。手順が同じ≠件数が同じ。「KLiCKe の 1 題あたりの件数に合わせた」とだけ書く。自信: 中

## 4. 総合の推奨: major
1. 評価が直接効く設定と害が現実に大きい設定がずれ、1 頁目で処理されていない。
2. 公開する側の持ち帰りが弱い。自分のログで回す道がコードの公開範囲で閉じ、倫理の利益の主張と食い違う。
3. 得点という準識別子、10 の測度だけの有用さの軸、アクセスの段階、の三つが抜けている。書き方と限界の節で直せる。

## 5. 読めなかった範囲と注入の疑い
- 事前登録の §Data〜§Diagnostics・§ENJA15 の本文、references.bib の hanisch 以外、borgman.txt の大半、hanisch.txt の声・歩容・視線の節は読んでいない。PDF は見ていない。
- 注入の疑い: なし。
