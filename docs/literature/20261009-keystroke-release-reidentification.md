# 打鍵の記録を公開するとき、何が残るか —— 先例・攻撃・加工・制度

> 2026-10-09 / `/literature-review` 1 ラウンド / **設計根拠の補強**（★ ADR-039 の【決 5】【決 6】【決 6-a】と同意文 v2 の第 3 層を研究者が決める材料。本ラウンドは**決めない**）
> 対象: issue #333（公開する打鍵の記録から本文を照合・復元されにくくする方法）・ADR-039（Proposed）・`.steering/20261009-release-deidentification-survey/`
> 名前空間: 方法論 = `V`（[V243]–[V263]）。既登録の再利用: [P269] [P274] [P275]（先例）/ [V7]（否決リスト）/ [V194] / [V237]–[V240]（★ [V237] [V239] [V240] は本ラウンドで一次を照合して注記を更新した）

## 動機（★ なぜこのラウンドを回したか）

- issue #333 は、公開の段（段 0 集計値 / 段 1 分析に使った表現 / 段 2 加工した打鍵イベント / 段 3 生の記録）と加工・公開前の関門を挙げ、「現時点の推奨（未決）」を置いた議論のメモである。
- ⚠️ その要の主張に根拠が無かった: 「数十語分あれば候補の文章をほぼ一意に特定できる」は issue 自身が「概算・要実測」と書く。加工の効き目の根拠 [V239] は抄録だけ、[V240] は下位エージェントの報告だけだった（`references.md` の注記どおり）。
- repo に、打鍵データの公開・再識別・開示制御を扱ったラウンドが無かった（`_index.md` で 0 件）。
- 公開は撤回できない。→ 研究者と合意して（2026-10-09）、決める前に 1 ラウンド回した。

★ 下位問い（研究者と合意・2026-10-09）:
- **S1 先例** —— 自由記述・自然作業の打鍵データセットは、何の項目を、どう加工して、どの条件で公開したか
- **S2 攻撃** —— (a) 時刻・長さの並びからの本文推定と照合 / (b) 別の日のセッションの結び付け（再識別）/ (c) 健康状態の推定
- **S3 防御** —— 時刻の加工（[V239] [V240] の一次確認）・集約・小さな n での差分プライバシーと合成データ
- **S4 制度** —— BRM の type 4 の例外の逐語・管理型アクセス・code-to-data・個人情報保護法（個人識別符号・仮名加工・匿名加工）・GDPR

## 検証状態

- **探索**: サブエージェント 4 本（Sonnet・下位問いごと・各 20 分・入れ子禁止・反証 angle を各本に指定）。生の出力は scratchpad（`survey/s1–s4.md`）。4 本とも 5 分以内に戻った。
- **メインが原本を取り直して逐語を照合した**: 27 件（★ 下位エージェントの抽出テキストは使わず、curl で取り直して pypdf / HTML から読んだ）。
  - 全文: [V243] [V244] [V248] [V249] [V250] [V239] [V240] [V255] [V258] [V262]
  - 該当ページ・該当条の全文: [P274] [P269] [V245] [V247] [V237] [V256] [V257] [V259] [V260] [V261] [V263]
  - 要旨と該当節: [V246] [V251] [V253] [V254] [V7]
  - 要旨のみ: [V252]
- 書誌（巻号頁・DOI）は、[V244] [V246] [V247] [V250] [V251] を Crossref で、[V253] [V254] [V251] を PDF の柱で、[V252] を J-STAGE の書誌で確認した。[V243]（JEDM）は Crossref で DOI が見つからず、[V248]（USENIX Security 2001）は DOI を確かめていないので、どちらも URL を key にした。
- **claim 抽出**: 32 件 → **検証 32 件**
- **confirmed 23**（3-0 が 16 / 2-1 が 7）／ **PLAUSIBLE BUT UNPROVEN 1** ／ **判定不能 5**（該当ゼロ）／ **否決 3**
- ⚠️ **本ラウンドで訂正した前提（3 件）**:
  1. [V240] の旧注記「時刻の丸めは攻撃側の前処理で効き目を失いうる」は**誤読**だった。原文 §2.6 は「**攻撃側が**時刻を離散化しても EER の改善はわずか／無視できる」であり、§3.2 は防御側の離散化（delay）と乱数のフレーム遅延（rdelay）が**どちらも保護を与える**と書く（カード 6）。→ ADR-039 D6 と issue #333 の同じ記述が誤り。
  2. ADR-039 事実 1 の注「『編集者の裁量』という言葉は、私が確かめた逐語には無い」は**誤り**だった。BRM の投稿規定に逐語 *"The decision on whether to proceed to peer review in such cases is at the Editor's discretion."* がある（カード 8）。
  3. ADR-039 D5 の「（プライバシーを理由とする）例外の逐語は自分で確かめていない」を**確かめた**（カード 8）。
  - ⚠️ ADR の本文は書き換えない規約なので、3 件は ADR-039 に反映していない（研究者の判断・`.steering/20261009-release-deidentification-survey/decisions.md`）。

### claim 台帳

| # | claim | 出典 | 票 | 温度 |
|---|---|---|---|---|
| 1 | 自然作業中の打鍵（左右の手・Space の印・日付と時刻）を数週〜数か月にわたり記録し、**誰でも取れる形**（ODC-By）で公開した先例がある | [P274] | **3-0** | 確定（慣行の実在） |
| 2 | 打鍵（押したキー・保持時間・押下と解放の時刻）と病状の要約を、誰でも取れる形で公開した先例がある | [V245] | **3-0** | 確定 |
| 3 | 公開データセットの作成そのものを同意の対象として明記した例がある | [V247] | **3-0** | 確定 |
| 4 | 打鍵ログの脱識別には打鍵ログ特有の難しさがあり、制限付きアクセスに倒した例（Blackbox）がある。公開した側も「ラベル付きの別標本が無い限りで脱識別」と限界を書いた | [V243] | **3-0** | 確定 |
| 5 | 打鍵の遅延（ダイグラフの平均）だけで別の時期の標本と高い精度で結び付く（加工なしで約 98%・top-10）。個人のプロファイルの平均を 500 ms に丸めると約 7%（偶然は約 5%） | [V244] | **2-1** | 確定（留保: 丸めは**集計したプロファイル**に掛けたもので、イベントの時刻ではない・キー識別子つき） |
| 6 | 打鍵の時刻だけ（キー識別子なし）から、打った内容の情報が漏れる（打鍵対あたり約 1 bit） | [V248] | **2-1** | 確定（留保: touch typing の人・ランダムなパスワード） |
| 7 | 長さの並びだけから、言語モデルで文を復元できる（応答の 29%・話題は 55%） | [V249] | **2-1** | 確定（留保: 長さはトークンごとに正確・LLM の定型的な文体・既知平文で強くなる） |
| 8 | **当方の形式**（カテゴリ化・推敲あり・日本語 IME）の記録から、候補の文章と照合できる | （#6 #7 の継ぎ接ぎ） | — | **PLAUSIBLE BUT UNPROVEN**（直接の研究 0 件） |
| 9 | 自由記述の打鍵で大規模に個人を識別できる（背景 1,000 人で Rank-1 67.4%・国で事前に絞ると 84.0%） | [V250] | **2-1** | 確定（留保: キーコードを入力に含む・1 セッションは短い転写） |
| 10 | キー識別子を持たない（カテゴリ化した）記録で、日をまたいで個人を識別できる | — | — | **判定不能（0 件）** |
| 11 | 打鍵の保持時間だけから、早期の Parkinson 病を識別できる（AUC 0.81・n=42/43） | [V246] | **3-0** | 確定 |
| 12 | 打鍵による神経・精神疾患の検出は、自然な環境のデータでも AUC 0.82（臨床では 0.89）。エビデンスの質は中程度 | [V251] | **3-0** | 確定（群の識別として） |
| 13 | 乱数の遅延は識別を下げるが、半分にするには多くの場合 500 ms 要る | [V239] | **3-0** | 確定（⚠️ 抄録と結論の「約 20%」は表から再現できない。自由文は 0.71→0.62 ＝相対 13%） |
| 14 | 攻撃側が時刻を離散化しても EER の改善はわずか／無視できる。防御側の離散化と乱数のフレーム遅延はどちらも保護を与え、同じ遅延なら乱数が常に上 | [V240] | **3-0** | 確定（⚠️ 旧注記の訂正） |
| 15 | 粗くしても一意性はほとんど下がらない（位置の軌跡: 4 点で 95%・一意性は解像度の約 1/10 乗でしか減らない） | [V253] | **2-1** | 確定（留保: 位置データからの類比） |
| 16 | 標本が小さく不完全でも、再識別は高い確率で成功しうる（15 の属性で 99.98%） | [V254] | **2-1** | 確定（留保: 人口統計の属性） |
| 17 | 合成データは推論攻撃を防がないか、有用性を保てない。外れ値は守られない。DP つきの生成は改善するが、小さなデータでは保証か有用性を大きく失いうる | [V255] | **2-1** | 確定（留保: 表形式・n=1000） |
| 18 | 参加者 3〜5 人の差分プライバシーでは雑音が信号を上回る | — | — | **判定不能（一次 0 件）** |
| 19 | 30 秒窓の特徴量だけを出す加工の効き目を測った研究 | — | — | **判定不能（0 件）** |
| 20 | BRM の type 4 は「参加者の秘密を破らずに」生データを自由に入手できることを前提とし、プライバシーで公開できない場合は「アクセスの条件」を書けばよいと明記する。Open Practices Statement の文例にも「データは出せないがコードは公開し模擬データで示す」形がある | [V237] | **3-0** | 確定 |
| 21 | BRM: 開始前に承認の無い研究は事後の承認が通常得られず査読に回せないことがあるが、その判断は**編集者の裁量** | [V237] | **3-0** | 確定（⚠️ ADR-039 事実 1 の注の訂正） |
| 22 | Springer Nature は共有への同意（利用・収集への同意とは別）を収集前に取ることを求め、管理型アクセス（再識別しない合意）と TRE を手段に挙げる | [V256] [V257] | **3-0** | 確定 |
| 23 | 安全は状態でなく程度であり、データそのものに加え、プロジェクト・人・環境・出力の 5 つで管理する（Five Safes） | [V258] | **3-0** | 確定（枠組みとして） |
| 24 | 資格制の利用許諾の定型: 再識別の試みの禁止・再共有の禁止・目的の限定・コードの還元 | [V259] | **3-0** | 確定 |
| 25 | 日本の個人識別符号の「身体の特徴」の列挙に、打鍵の特徴は無い | [V260] | **3-0** | 確定（⚠️ 個人情報に当たるかは別。照合で特定の個人を識別できるかで決まる [V238]） |
| 26 | 匿名加工情報の基準は「特異な記述等の削除」と「データベースの性質を勘案した措置」を含み、特異かは個別の事例ごとに客観的に判断する | [V261] [V262] | **3-0** | 確定 |
| 27 | GDPR の biometric data は行動の特徴を含み、一意の識別を許す・確かめる処理の結果を指す。仮名化したデータは個人データとして扱う | [V263] | **3-0** | 確定 |
| 28 | BRM がプライバシーを理由に申請制を認めた・拒んだ具体例 | — | — | **判定不能（0 件）** |
| 29 | 打鍵の時刻を公開したデータから実際に個人が特定された事例・公開を撤回した事例 | — | — | **判定不能（0 件）** |
| 30–32 | ⚠️ 否決 3 件 → §否決リスト | — | **1-2 が 3** | — |

★ 集計の検算: 3-0 = #1 #2 #3 #4 #11 #12 #13 #14 #20 #21 #22 #23 #24 #25 #26 #27（16）／ 2-1 = #5 #6 #7 #9 #15 #16 #17（7）／ PLAUSIBLE = #8 ／ 判定不能 = #10 #18 #19 #28 #29（5）／ 否決 = #30 #31 #32（3）＝ 計 32 件。

⚠️ **判定不能 = 「4 本 × 20 分の探索と、その後のメインの確認で見つからなかった」**であって「存在しない」ではない。
⚠️ **票の視点**: ① 内的妥当性（その研究の中で主張が支えられているか）② 当方への外挿（キー識別子なしの約 15 カテゴリ・自然作業・n 3〜5・日本語 IME）③ 頑健性（反証・効果の大きさ・評価の過大さ）。★ GSE に**有利な**主張（加工すれば出せる・先例と同じ粒度なら出せる）も同じフィルタにかけた（→ 否決 #32）。

## gate 判定（要点先出し）

| 下位問い | 温度 | 一言 |
|---|---|---|
| **S1** 先例 | **確定（慣行の実在）／判定不能（安全の実績）** | 打鍵の時刻を誰でも取れる形で出した先例はある（[P274] は Space の印と日付まで出している）。⚠️ ただし公開文書に再識別の評価は無い。評価を伴うのは集計プロファイルを丸めた [V244] だけ。事故・撤回の事例は 0 件 |
| **S2-a** 本文の推定・照合 | **確定（一般命題）／PLAUSIBLE BUT UNPROVEN（当方の形式）** | 時刻から内容が漏れる [V248]、長さの並びから文を復元できる [V249]。⚠️ カテゴリ化・推敲・日本語 IME の記録での照合は直接の研究 0 件 → **自前で測るしかない** |
| **S2-b** 再識別 | **確定** | 時刻だけで別の時期の標本と結び付く [V244]、大規模に識別できる [V250]。⚠️ ただしどちらもキー識別子つき。カテゴリ化した記録の識別は 0 件 |
| **S2-c** 健康状態の推定 | **確定（群の識別）** | 保持時間だけで早期 PD [V246]。自然な環境でも AUC 0.82 [V251]。→ 加工しても消せない側 |
| **S3** 防御 | **確定（悲観側）** | 遅延は数百 ms 要る [V239]。丸めも効くが [V240]、集計値に掛けた効き目 [V244] をイベントの公開には持ち込めない。粗くする・標本が小さい・合成データは単独で安全とみなせない [V253] [V254] [V255]。⚠️ 小 n の DP は判定不能 |
| **S4** 制度 | **確定** | BRM はプライバシーを理由に「アクセスの条件」を書く道を規定に持つ [V237]。管理型アクセスの型 [V257] [V258] [V259]。日本の個人識別符号の列挙に打鍵は無いが、個人情報かは別 [V260] [V238] |

★ **判定: de-risk 先行。** issue #333 の第一候補（段 0 ＋ 段 1 を申請制で出す・段 2 は関門を通った場合だけ）を**否定する証拠は無く**、S4 は道があることを示した。⚠️ ただし (1) 照合（#8）と段 1 の効き目（#19）は文献で決まらず、**関門の実測が先**、(2) 健康状態の推定（#11 #12）は加工で消せないので**同意文で知らせる**側に回る。

---

### カード 1: 打鍵の時刻を誰でも取れる形で出した先例はある —— ただし安全の評価は伴っていない **[検証済 3-0]** [P274] [V245] [P269] [V247]

1. **どんなもの**: Parkinson 病の研究のデータ 2 件（Tappy [P274]・neuroQWERTY [V245]）は PhysioNet で、大規模な打鍵データ [P269] は研究室のページで、KeyRecs [V247] は Zenodo で公開されている。
2. **何がすごい**: [P274] は逐語 *"as they typed normally on their own computer (without any supervision) over a period of weeks or months"*、記録したのは *"email, word processing, web searches and the like"* の作業中。欄は *"Hand: L or R key pressed"*・*"Direction: Previous to current LL, LR, RL, RR (and S for a space key)"*・*"Date: YYMMDD"*・時刻（ミリ秒）。アクセスは逐語 *"Anyone can access the files, as long as they conform to the terms of the specified license."*（ODC-By）。[V245] は 4 列 *"The key pressed."*・保持時間・解放と押下の時刻を同じ条件で出す。[P269] の同意は逐語 *"consent that their anonymized data will be collected and used for research purposes"*、利用は *"free to use for research and non-commercial use"*。[V247] の同意は逐語 *"for the creation of this publicly available dataset"*。
3. **肝**: ★ 当方の段 2 に近い粒度、あるいはそれより細かい粒度（Space の印・日付・押したキー）が、誰でも取れる形で既に出ている。
4. **どう検証した**: 各データのページを取得して読んだ（2026-10-09）。
5. **議論**: ⚠️★★★ **先例があることは安全の証拠ではない。** どのページにも再識別・照合の評価は無い。[P274] は Space の印があるので語長の並びが取れる。→ 「先行例と同じ粒度だから出してよい」は根拠にしない（否決 #32 と同じ理由）。⚠️ [P269] は転写課題で本文が既知なので、本文の流出が問題にならない設計（自然作業の先例ではない）。
6. **次に読む**: Tappy の論文 Adams 2017（PLOS ONE・doi:10.1371/journal.pone.0188226）の倫理・同意の節。BiAffect（Space と BackSpace を記録しないとされる・一次未取得）。
- **やり残し**: BiAffect・Kaggle の Q-type（[P274] の注記）・Clarkson II・Buffalo の公開条件を一次で読んでいない。

### カード 2: 脱識別の難しさと、「ラベル付きの別標本が無い限り」という限界 **[検証済 3-0 / 2-1]** [V243] [V244] [P275]

1. **どんなもの**: [V243] は CS1 の打鍵データ 2 本を公開した論文（JEDM 2023）。[V244] はプログラミング授業の打鍵の遅延から学生を結び付け、加工の効き目を測った論文（L@S 2017）。[P275] は打鍵データの公開を断った例。
2. **何がすごい**: [V243] 要旨逐語 *"the challenges of deidentification that are peculiar to keystroke log data"*。§4 逐語 *"The creators and maintainers of the Blackbox dataset, in fact, have restricted access because of the technical challenges of deidentification"*。打鍵の時刻による識別を認めたうえで、逐語 *"However, all of these identification techniques require a labeled sample, which the regulatory definition of identifiability assumes is not available."* とし、結論で逐語 *"the data is deidentified only as long as there is no other labeled sample of a student's keystrokes."* と限界を書く。加工は逐語 *"mask the characters of identifying text with the @ character"*（時刻は加工していない）。利用者への注意は逐語 *"Ethical use of this dataset includes avoiding attempts at reconstructing identities."*。[V244] 要旨逐語 *"simply removing explicit identifiers such as names and student numbers is not sufficient to protect the privacy of the users"*。
3. **肝**: [V244] は、500 ms の丸めで逐語 *"Approximately 7% of the students are correctly identified with a threshold of k = 10. This accuracy is very low when compared to the non-anonymized accuracy of around 98.5%. Purely random guessing would yield an identification accuracy of around 5% with our data set, which means that even with the 7% accuracy it is possible that there may still be some information on identity in the data, which might not be acceptable in all scenarios."* と書く ＝ **偶然の水準と並べて基準を書いた先例**。
4. **どう検証した**: [V244] は 199 人 / 153 人。個人ごとにダイグラフの平均遅延のプロファイルを作り、top-k の最近傍で別の時期と照合した。
5. **議論**: ⚠️★★★ **[V244] の丸めは、個人のプロファイル（ダイグラフごとの平均）に掛けたもの**（逐語 *"rounding the average latencies in typing profiles"*）。イベントの時刻を公開すれば、攻撃者は自分で平均を取り直せるので、**段 2（イベント）には同じ効き目を期待できない**（★ 私の推論・未検証）。⚠️ 丸めは単調に効かない（Table 1・2014 年: 100 ms で 81.7%・200 ms で 6.5%・300 ms で 72.5%・400 ms で 77.1%・500 ms で 6.5%。著者も 200 ms の値を *"unexpected"* と書く）。一方、等幅の区間化は 300 ms で 6.5% / 7.2% まで単調に下がる。★ 有用性は残る: 500 ms の丸めでもプログラミング経験の分類は 73.9%（ZeroR 58.8%・Table 2）。⚠️ どちらもキー識別子つき。⚠️ [V243] の「ラベル付きの別標本は無い」という前提は、**当方では崩れる**（同じ参加者の別のセッション・G1 と O1 の両方に参加した人がいる）。
6. **次に読む**: Longi et al. 2015（Koli Calling・98.6% の原典）・Brown et al. 2018（Blackbox の制限の理由）。
- **やり残し**: [V244] は「ラベル付きの別標本」を攻撃者が持つ前提の照合だけを測った。当方で測るなら同じ前提（同じ参加者の別の日）で測る。

### カード 3: 時刻と長さの並びから内容が漏れる —— 一般命題は確定、当方の形式での照合は未検証 **[検証済 2-1]** [V248] [V249] [V194]

1. **どんなもの**: [V248] は SSH の打鍵の時刻からパスワードを推す攻撃（USENIX Security 2001）。[V249] は暗号化通信のトークン長の並びから、AI アシスタントの応答文を復元する攻撃（USENIX Security 2024）。[V194] は打鍵のサイドチャネルの SoK。
2. **何がすごい**: [V248] 逐語 *"the timing information leaks about 1 bit of information about the content per keystroke pair"*・*"Herbivore can reduce the cost of password cracking by a factor of 50"*。[V249] 逐語 *"we were able to accurately reconstruct 29% of an AI assistant's responses and successfully infer the topic from 55% of them"*。手法は (1) LLM で長さの並びを文に翻訳 (2) 文と文の文脈 (3) *"performing a known-plaintext attack by fine-tuning the model on the target model's writing style"*。
3. **肝**: ★ 当方の記録は Space・Enter・句読点の位置が分かるので、**長さの並び**（単語長・文長・段落長）が残る。[V249] はまさに長さの並びだけから文を当てる。
4. **どう検証した**: [V248] は HMM と n-Viterbi。[V249] は 57 万件の質問で学習し、検証 1 万・テスト 1 万。
5. **議論**: ⚠️ [V248] の前提は逐語 *"In this paper we only consider users who are familiar with keyboard typing and use touch typing."*。⚠️ [V249] の長さはトークンごとに**正確**で、標的は LLM の定型的な文体。人の文章・推敲（BackSpace・カーソル移動・貼り付け）・日本語 IME で崩れるかは**未検証**。⚠️ 逆に「書きぶりを学習すると強くなる」（既知平文）は、**本人の過去の文章を持つ攻撃者が強い**ことを示唆する。→ ★ **#8（当方の形式での照合）は PLAUSIBLE BUT UNPROVEN**。issue #333 の「照合は易しい」は**見込みのまま**で、関門で測る。
6. **次に読む**: Wright et al. "Spot me if you can"（IEEE S&P 2008・パケット長で候補の語句を照合・本文未取得）／ Idaho 大の修論 "Keystroke Timing Attacks in a Free-Text Environment"（書誌のみ）。
- **やり残し**: 語長の並びだけで文がどれだけ一意になるかの研究は見つからなかった（★ 自前で見積もる: 青空文庫など）。

### カード 4: 自由記述の打鍵による大規模な識別 —— ただしキーコードを使っている **[検証済 2-1]** [V250]

1. **どんなもの**: [V250] TypeNet。物理キーボード 16 万 8 千人・モバイル 6 万人の自由記述の打鍵で、LSTM による個人認証と識別を評価した（IEEE TBIOM 2022）。
2. **何がすごい**: 背景 1,000 人の識別で Rank-1 67.4%（デスクトップ・triplet loss・Table 5）、国で事前に絞ると 84.0%（Table 6・逐語 *"pre-screening by country"*）。
3. **肝**: 入力は逐語 *"a time series with three dimensions: the keycodes, press times, and release times of the keystroke sequence"* ＝ **キーコードを含む**。
4. **どう検証した**: Aalto の 2 データ（[P269] が物理キーボード側）。1 セッションは短い文の転写。
5. **議論**: ⚠️ キーコードを外した結果は報告されていない。★ 著者自身がテキストへの依存を調べ、デスクトップでは編集距離と得点の相関が無い（*"in desktop scenarios (Fig. 6 up) this correlation is not present"*）と書く ＝ 時刻の癖そのもので識別している側の証拠。⚠️ 当方は n=3〜5 の**閉じた集合**なので、識別の問題としては TypeNet より**易しい**向き（★ 推論・未検証）。
6. **次に読む**: キー識別子なし・カテゴリ化した打鍵での識別の研究（見つからなかった → #10）。
- **やり残し**: #10（カテゴリ化した記録での日をまたぐ識別）は 0 件 → ★ 関門 (ii) の実測で埋める。

### カード 5: 打鍵の時刻だけから健康状態が推定される —— 加工で消せない側 **[検証済 3-0]** [V246] [V251]

1. **どんなもの**: [V246] は日常のキーボード操作の保持時間から早期 Parkinson 病を検出した研究（Sci Rep 2016・neuroQWERTY）。[V251] は打鍵による神経・精神疾患の検出の系統的レビューとメタ分析（Sci Rep 2022・41 研究）。
2. **何がすごい**: [V246] 逐語 *"measures the key hold times (the time required to press and release a key) during the normal use of a computer"*・*"AUC = 0.81 (n = 42/43; …)"*。[V251] は PD の統合感度 0.86・特異度 0.83。自然な環境のデータでも AUC 0.82（95% CI 0.79–0.84）で、臨床（0.89）より有意に低いが高い。
3. **肝**: ★ 使う特徴は**保持時間**（押下と解放の差）であり、**キー識別子が無くても取れる**。当方の記録は押下と解放の時刻を持つ。
4. **どう検証した**: [V246] は 85 人。[V251] は QUADAS-2 で偏りのリスクを評価し、逐語 *"we rated the quality of evidence to be moderate"*。
5. **議論**: ⚠️ どれも**群の識別**（病気か対照か）で、ラベル付きの学習データを要する。個人の日ごとの気分・疲労の推定とは設問が違う。⚠️ 異質性が高い（I² 79–87%）。→ ★ それでも「公開した打鍵から健康状態が推定されうる」は根拠つきで言える。**加工（遅延・丸め）で保持時間を壊せば分析も壊れる**ので、関門ではなく**同意文 v2 の第 3 層で知らせる**側に回る（★ 推論）。
6. **次に読む**: Adams 2018 JMIR（自宅の自然入力での neuroQWERTY の検証）・うつ・MCI の研究（agent 報告の AUC 0.98 などは小さい n で、本文未読）。
- **やり残し**: 小 n の研究の過大評価の検討を読んでいない。

### カード 6: 時刻の加工の効き目 —— 遅延は数百 ms 要る・丸めも効く（[V240] の訂正） **[検証済 3-0]** [V239] [V240]

1. **どんなもの**: [V239] は打鍵の時刻に乱数の遅延・間隔の混合を入れ、識別と属性の推定がどれだけ下がるかを測った（arXiv 2017）。[V240] はブラウザ上の打鍵の時刻への攻撃と、遅延による防御を評価した（SECRYPT 2019）。
2. **何がすごい**: [V239] 結論逐語 *"With a 25 ms delay, identification accuracy is reduced by approximately 20% on average, and in most cases a 500 ms delay is needed to halve the identification accuracy."*。Table 4（delay mix・識別精度）: 長い自由文で Δ=0 → 0.71、平均の遅れ 26 ms → 0.62、126 ms → 0.36、394 ms → 0.30。[V240] §2.6 逐語 *"Timestamps values have been discretized using 1,001 different resolutions (from 0 to 1 by step of 1/1,000). As shown in Figure 3, attacker might expect slight (J≃ 0.02 for GREYC W1) or negligible (J < 0.005) EER improvement by doing so."*。§3.2 逐語 *"As shown in Figure 5, both provide significant protection compared to the costless KDAS. However, for the same latency, rdelay seems always better than delay."*・*"any pre-processing done with public information cannot decrease the privacy"*。
3. **肝**: ★ 遅延は効くが、識別を半分にするには数百 ms 要る。丸め（離散化）も防御として効くが、同じ遅れなら乱数の方が強い。
4. **どう検証した**: [V239] は 110 / 101 / 127 人・RandomForest・層化 10 分割。[V240] は固定文の 4 データ（46〜104 人）・EER。
5. **議論**: ⚠️★★★ **[V240] の旧注記（「丸めは攻撃側の前処理で効き目を失いうる」）は誤読**。原文の「攻撃側の前処理」の節は、**攻撃側が**離散化して EER を良くできるかの話であり、改善はわずか。「公開情報だけでできる前処理はプライバシーを下げない」は、**丸めで EER が下がる（攻撃が良くなる）場合**についての注である。⚠️ [V239] の「約 20%」は表から再現できない（短い固定文 25%・長い固定文 8%・自由文 13%）→ 引くときは表の値を併記する。⚠️ 属性（性別など）の推定は、逐語 *"Soft biometric trait classification accuracies, which are initially near chance accuracy, are relativity unaffected"* ＝ **もともと偶然の水準に近い**ので、加工の効果は測れていない。⚠️ どちらも**リアルタイムの経路**の加工で、公開後の記録の加工とは設計が違う。⚠️ 数百 ms の遅延は、段 2 の時刻を使う分析（保持時間・間隔）と**正面から衝突する**。
6. **次に読む**: KeyDrown（NDSS 2018・本文未取得）。
- **やり残し**: 公開後の記録に加工を掛けた評価（オフラインの加工）は見つからなかった。

### カード 7: 粗くしても・小さくしても・合成しても、単独では安全にならない **[検証済 2-1]** [V253] [V254] [V255]

1. **どんなもの**: [V253] は 150 万人・15 か月の携帯電話の位置の軌跡の一意性（Sci Rep 2013）。[V254] は不完全な標本からの再識別の成功率の推定（Nat Commun 2019）。[V255] は合成データの公開のプライバシーの定量評価（USENIX Security 2022）。
2. **何がすごい**: [V253] 逐語 *"four spatio-temporal points are enough to uniquely identify 95% of the individuals"*・*"the uniqueness of mobility traces decays approximately as the 1/10 power of their resolution. Hence, even coarse datasets provide little anonymity."*。[V254] 逐語 *"99.98% of Americans would be correctly re-identified in any dataset using 15 demographic attributes"*・*"even heavily sampled anonymized datasets are unlikely to satisfy the modern standards for anonymization set forth by GDPR"*。[V255] 逐語 *"synthetic data either does not prevent inference attacks or does not retain data utility"*・*"Synthetic data drawn from generative models without explicit privacy protection does not protect outlier records from linkage attacks."*・*"Synthetic data sharing is often motivated by the unique value of sensitive dataset that are limited in size. This implies that, in practice, data holders might struggle to achieve the desired strict privacy guarantees, or face a large utility loss"*。
3. **肝**: ★ 「粗くすれば」「標本が小さいから」「合成データにすれば」は、どれも単独では安全の根拠にならない。
4. **どう検証した**: [V253] は解像度を変えて一意性を測った。[V254] は 210 の母集団で一意性を予測（AUC 0.84〜0.97・agent 報告・私は図表を照合していない）。[V255] は Adult と Texas（n=1000）で shadow model による連結攻撃。
5. **議論**: ⚠️ どれも打鍵ではない（位置・人口統計・表形式）→ **類比**として引く。★ 反証側: [V255] 逐語 *"Differentially private generative models can provide a significantly higher privacy gain with respect to linkage attacks than traditional data synthesis algorithms."* ＝ DP つきなら改善する。⚠️ ただし同じ論文が、小さなデータでは保証か有用性を大きく失いうると書く。⚠️ **参加者 3〜5 人の DP の限界を明示した一次は 0 件**（#18）→ issue #333 の「n が 3〜5 人だと雑音が結果を上回る」は**推論のまま**。
6. **次に読む**: de Montjoye 2015（Science・クレジットカード）とそのコメント・応答（反証側の候補・未読）。
- **やり残し**: 打鍵データに DP を適用した評価（ε と識別率）を探していない。

### カード 8: BRM と Springer Nature —— プライバシーを理由に「アクセスの条件」を書く道がある **[検証済 3-0]** [V237] [V256] [V257]

1. **どんなもの**: BRM の投稿規定 [V237]、Springer Nature の研究データ方針 [V256] と機微なデータの手引き [V257]。2026-10-09 に curl で取得し、HTML から読んだ。
2. **何がすごい**: [V237] 逐語 *"This journal operates a type 4 research data policy. A submission to the journal implies that materials described in the manuscript, including all relevant raw data, will be freely available to any researcher wishing to use them for non-commercial purposes, without breaching participant confidentiality."*。同じ見出しの下に逐語 *"When it is not possible to share research data publicly, for instance when individual privacy could be compromised, data availability should still be stated in the manuscript along with any conditions for access."*。Open Practices Statement の文例に逐語 *"Due to data protection rules, the data cannot be made available, but documented code for the analyses in this article is available at (url for the site where the code is located) and is illustrated with simulated data."*。倫理の見出し "Retrospective ethics approval" に逐語 *"The decision on whether to proceed to peer review in such cases is at the Editor's discretion."*。[V257] 逐語 *"Participant consent to share the data (in addition to use or collection of data) should also be obtained and documented prior to data collection."*・*"Use of a controlled access repository to manage who can access data and under what terms … apply additional restrictions such as an agreement not to reidentify participants."*。
3. **肝**: ★ ADR-039 D5 の案 A（申請制）も案 C（集計値とコードだけ）も、**規定の文言の中に置き場所がある**。案 C は Open Practices の文例そのもの。
4. **どう検証した**: 規程の逐語の照合（運用の実例ではない）。
5. **議論**: ⚠️ 本則の「freely available」と申請制の緊張は残る。文例 3 は *"available from the corresponding author on reasonable request"* で、審査や利用許諾を伴う管理型は文例に無い。⚠️ **BRM が実際に申請制を認めた・拒んだ例は 0 件**（#28）→ 投稿前に編集部へ尋ねる（ADR-039 の問い合わせ A に足す候補）。⚠️ 規程は改訂されうるので、投稿時に読み直す。
6. **次に読む**: Springer Nature の data availability statement の文例集（"restricted access datasets" の例）。
- **やり残し**: 「on request」の実効性への批判（Gabelica ら 2022 など・agent 報告で所在のみ）を読んでいない。

### カード 9: 管理型アクセスの型 —— Five Safes と利用許諾の定型 **[検証済 3-0]** [V258] [V259]

1. **どんなもの**: [V258] は研究データへのアクセスを設計する枠組み Five Safes（UWE の working paper 2016）。[V259] は PhysioNet の資格制データの利用許諾 1.5.0。
2. **何がすごい**: [V258] は 5 つの次元を *"Safe projects / Safe people / Safe data / Safe settings / Safe outputs"* と置き、逐語 *"These dimensions embody a range of values: 'safety' is a measure, not a state."*。[V259] 逐語 *"The LICENSEE will not attempt to identify any individual or institution referenced in PhysioNet restricted data."*・*"The LICENSEE will not share access to PhysioNet restricted data with anyone else."*・*"The LICENSEE will use the data for the sole purpose of lawful use in scientific research and no other."*・*"The LICENSEE agrees to contribute code associated with publications arising from this data to a repository that is open to the research community."*。
3. **肝**: ★ issue #333 の案 C（申請制と利用規約・コードをデータ側へ送る方式）は、Five Safes の「人」「出力」で管理する形に当たる。[V259] は利用規約の文案の雛形になる。
4. **どう検証した**: 枠組みと規約の文書（効き目の評価ではない）。
5. **議論**: ⚠️ [V258] 自身が逐語 *"Up to now this model has largely been described indirectly in other papers"* と書く。批判的な検討（J. Privacy and Confidentiality）は未読。⚠️ 参加者 3〜5 人の個人研究者が、申請の審査やコードの代行実行を回せるかは別の問題（未検討）。
6. **次に読む**: DataSHIELD（Gaye et al. 2014・doi:10.1093/ije/dyu188）・Guinney & Saez-Rodriguez 2018（model-to-data）・OpenSAFELY（いずれも書誌のみ）。
- **やり残し**: code-to-data の先例を一次で読んでいない。UK Data Service / ICPSR のアクセスの段も未読。

### カード 10: 法令 —— 個人識別符号の列挙に打鍵は無いが、それで個人情報でないとは言えない **[検証済 3-0]** [V260] [V261] [V262] [V263] [V238]

1. **どんなもの**: 個人情報保護法施行令 [V260]・施行規則 [V261]・個人情報保護委員会のガイドライン（仮名加工情報・匿名加工情報編）[V262]・GDPR [V263]。
2. **何がすごい**: [V260] 第 1 条第 1 号は身体の特徴を イ DNA ／ ロ 顔 ／ ハ 虹彩 ／ ニ「発声の際の声帯の振動、声門の開閉並びに声道の形状及びその変化」／ ホ「歩行の際の姿勢及び両腕の動作、歩幅その他の歩行の態様」／ ヘ 静脈 ／ ト「指紋又は掌紋」と列挙する（打鍵は無い）。[V261] 第 34 条（匿名加工情報の作成の基準）は 第 3 号 連結する符号の削除・第 4 号「特異な記述等を削除すること」・第 5 号「当該個人情報データベース等の性質を勘案し、その結果を踏まえて適切な措置を講ずること」。[V262] 逐語「実際にどのような記述等が特異であるかどうかは、情報の性質等を勘案して、個別の事例ごとに客観的に判断する必要がある。」。[V263] Art. 4(14) 逐語 *"'biometric data' means personal data resulting from specific technical processing relating to the physical, physiological or behavioural characteristics of a natural person, which allow or confirm the unique identification of that natural person"*、Recital 26 逐語 *"Personal data which have undergone pseudonymisation, which could be attributed to a natural person by the use of additional information should be considered to be information on an identifiable natural person."*。
3. **肝**: ★ 打鍵の癖は日本法の個人識別符号の列挙に無いが、個人情報かどうかは照合で特定の個人を識別できるかで別に決まる [V238]。GDPR では「行動の特徴」が biometric data の文言に入る。
4. **どう検証した**: e-Gov 法令 API v1（施行令・施行規則・2026-10-09 取得）、ガイドラインは令和 6 年 12 月一部改正の PDF、GDPR は EUR-Lex の全文。
5. **議論**: ⚠️ **法的判断はしていない。** ⚠️ 参加者 3〜5 人では、ほぼ全員の記録が「特異な記述等」になりうる（★ 私の推論）。⚠️ GDPR Art. 9(1) の禁止は逐語 *"biometric data for the purpose of uniquely identifying a natural person"* に掛かる ＝ 識別を目的にしないことが論点になりうる（★ 私の読み・法的判断ではない）。→ ★ ADR-039 D7（例外に頼らず同意で受ける）を変える材料は無い。
6. **次に読む**: 施行令第 1 条第 1 号の「個人情報保護委員会規則で定める基準」の規則の条文・法第 57 条（適用除外）。
- **やり残し**: 「学術研究機関等」の定義と、個人研究者・学生の扱いの解説を読んでいない（ADR-039 D7 の未確認と同じ）。

## 否決リスト（★ カード本体に書かない）

| # | 主張 | 出典候補 | 票 | 否決理由 |
|---|---|---|---|---|
| 30 | 打鍵の時刻を 5 ms に量子化しても、内容の複雑さとの相関が残る（作文で ρ 0.35–0.55） | [V7]（arXiv:2603.00177v3） | **1-2** | 査読の有無が未確認のプレプリントで、著者は事業者（利益相反の可能性）。要旨と表の該当行は読んだが本文の手法を精読していない |
| 31 | 日本語の自由文入力でも、打鍵で個人を高い精度で識別できる | [V252]（佐村・西村 2009） | **1-2** | 要旨のみ（本文の PDF は文字化け）。識別率の数値・入力方式・キー識別子の扱いが未確認。2009 年・LAN 上の課題 |
| 32 | 適切に加工すれば、打鍵の時刻は公開データに含めてよい（★ GSE に有利な主張） | [V244] 結論逐語 *"keystroke timings can be included in open data sets as long as proper anonymization procedures are followed"* | **1-2** | ① 内的: 丸めは集計したプロファイルに掛けたもので、イベントの公開を評価していない ② 外挿: キー識別子つき・識別だけを評価（照合・健康推定は対象外）③ 頑健性: 7% は偶然 5% を上回り、著者自身が「情報が残るかも」と書く。→ 当方の段 2 への一般化は否決 |

## GSE への還元

### issue #333 / ADR-039 の決めごとへの含意（★ 決めるのは研究者）

1. **【決 5】公開の形式**: BRM の規定に、プライバシーを理由に「アクセスの条件」を書く道が逐語である（カード 8）。案 C（集計値＋コード＋模擬データ）は Open Practices の文例そのもの。⚠️ 申請制の運用の先例は 0 件なので、**問い合わせ A に「申請制（利用許諾つき）で Open Practices Statement を書いてよいか」を足す**のが安い確認。
2. **【決 6】公開前の関門**: 攻撃を 3 つに分け、それぞれ文献に型がある。
   - 結び付け: [V244] の型（別の日のプロファイルを top-k で照合）を実データで。★ 基準は偶然の水準と並べて書く（[V244] の書き方が先例）。
   - 照合: [V249] の型（長さの並び → 候補の文章）を正解のある入力で。★ 当方の形式での直接の研究は 0 件（#8）→ **自前の実測が要る**。
   - 健康状態の推定: 保持時間が主役で、加工で消すと分析も壊れる（カード 5）→ **関門ではなく同意文で知らせる側**。
3. **加工の選び方**: 遅延は数百 ms 要り（カード 6）、段 2 の時刻の有用性と衝突する。丸めは効くが、[V244] の効き目は**集計値**に掛けたもので、イベントを出す段 2 には持ち込めない（★ 推論）。粗くする・標本が小さい・合成データは単独では安全とみなせない（カード 7）。
4. **段 1 も関門にかける**: 30 秒窓の特徴量だけを出す効き目を測った研究は 0 件（#19）。issue #333 の議論（`keys` の差から 1 秒ごとの打鍵数を逆算できる見込み）と合わせ、段 1 を無条件に安全とみなさない。
5. **同意文 v2 の第 3 層**: 共有への同意を収集前に取る（[V257]）。[V243] の注意書き（脱識別したが見落としの可能性がある・再識別を試みないこと）は第 3 層と利用規約の文案の素材。健康状態の推定のおそれ（カード 5）と、別のセッションと結び付けられるおそれ（カード 2・4）は根拠つきで書ける。
6. **先例を根拠にしない**: [P274] は Space の印と日付まで誰でも取れる形で出しているが、再識別の評価は無い（カード 1）。「先行例と同じ粒度」は公開の根拠にしない。
7. **ADR-039 の訂正候補 3 件**（★ ADR は書き換えない規約なので研究者の判断）: 事実 1 の注（編集者の裁量は逐語にある）／ D5 の「例外の逐語は未確認」（確認した）／ D6 の「時刻の丸めは攻撃側の前処理で効き目を失いうる [V240]」（誤読）。issue #333 の同じ記述も同様。

### `docs/research-positioning.md` への還元

- **精緻化**: §4 の「本文非保存だから公開しやすい＝GSE の差分 = 否決 1-2」に、本ラウンドの結果を 1 行足した（本文非保存でも結び付け・健康状態の推定は残り、照合も否定できない ＝「公開しやすい」そのものが条件つき）。研究の主張範囲（§1〜§3）は動かない。

## やり残し

- **S2-a の実測**: 語や文節の長さの並びがどれだけ一意か（青空文庫などで見積もる）と、正解のある入力での照合攻撃の試作（issue #333「次の一歩」）。★ 本ラウンドの結論は「文献では決まらない」。
- **S2-b**: キー識別子なし（約 15 カテゴリ）の記録での日をまたぐ識別（#10・0 件）。関門 (ii) の実測で埋める。
- **S1**: BiAffect・Kaggle の Q-type・Clarkson II・Buffalo の公開条件を一次で読んでいない。Tappy の論文（Adams 2017）の倫理と同意の節。
- **S3**: 打鍵データへの DP の評価（ε と識別率）・小 n の DP の限界の一次（#18・0 件）。KeyDrown の本文。
- **S4**: BRM の申請制の運用（#28・0 件）→ 編集部への問い合わせ。code-to-data（DataSHIELD・OpenSAFELY・model-to-data）と UK Data Service / ICPSR の一次。「学術研究機関等」の定義の解説。
- **反証側**: 「on request」の実効性への批判・Five Safes への批判・de Montjoye 2015 へのコメントと応答を読んでいない。
