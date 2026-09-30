# S-02 検索漏れ候補 11 件の抄録（＋ 標本の比較・N-06）—— 書誌と要点（事実）

> 取得日: 2026-09-29（日本時間。書誌と抄録 21:38＝JSON の executed。本文はその後）。手順は `design.md` §2（抄録を読む前に固定）。
> ★ このファイルは事実だけを書く（書誌・抄録や本文に書いてあること）。判定に関わる記述は別のファイル（`survey-S-02-ai-judgments.md`）にある。
> 書誌の生の結果: `evidence/S-02/s02_meta_2026-09-29.json`（書誌・訂正の関係・オープンアクセスの表示。抄録は repo に置かない）。スクリプト: `evidence/S-02/fetch_meta.py`。
> 本文を読んだ 4 件は、サブエージェント（Sonnet）が平文から項目を抜き出し、メインが該当箇所を開いて確かめた（対象・N・国・疲労の尺度・AI が項目に入るか・主な結果）。
> ★ 2026-09-30 追記: #3（出版社のページをブラウザで読んだ）と #8（Zenodo のファイル）の本文はメインが直接読み、§1・§2・§3・§6・§7 に足した。本文・資料の写しは repo に置かない。

## 1. 対象と入手の状況

| # | 書誌（Crossref・DataCite で確かめた） | 抄録の出どころ | 本文 |
|---|---|---|---|
| 1 | Asmi F, Wong A, Almugren I, Chotia V ほか 2026. Dark side of generative AI: a stressor–strain outcome and cognitive load theory explanation on decision fatigue and cognitive overload. *J Enterprise Information Management*. doi:10.1108/jeim-10-2025-1027（訂正: Corrigendum, doi:10.1108/jeim-08-2026-1628, 2026-09-07） | Crossref | 読めず（出版社が 403）。訂正の中身も読めず |
| 2 | Honggang W, Khoso AK, Althubyani AR 2026. Technostress, digital fatigue, and AI dependency as antecedents of burnout and SDG-4 achievement in EFL classrooms. *Scientific Reports* 16. doi:10.1038/s41598-026-45402-7 | Crossref | 読んだ（Europe PMC・CC BY） |
| 3 | Khoso AK, Honggang W ほか 2026. Technostress forecasting in EFL classrooms: How digital fatigue and perceived AI ethical concerns shape digital burnout and undermine SDG-4 achievement. *Acta Psychologica*. doi:10.1016/j.actpsy.2026.107396 | Europe PMC | 読んだ（2026-09-30・出版社のページをブラウザで・CC BY。2026-09-29 はスクリプトが弾かれて読めず） |
| 4 | Thorpe D, Bean C, Krieg J ほか 2025. Associations between generative artificial intelligence usage, Job Demands, Job Control and Burnout. *AI & Society*. doi:10.1007/s00146-025-02764-2 | 出版社の公開ページ（`dc.description`） | 読めず（購読制） |
| 5 | Kim B-J, Kim M-J 2026. Digital efficiency, human exhaustion: How human-centered AI buffers the impact of AI adoption on physical health via AI techarnostress（Crossref の題名の表記のまま）. *Technology in Society*. doi:10.1016/j.techsoc.2026.103553 | **取れなかった**（Crossref・Europe PMC・Semantic Scholar・OpenAlex に無く、出版社は 403） | 読めず（OpenAlex の表示は closed） |
| 6 | Chung J, Kwon H 2025. Privacy fatigue and its effects on ChatGPT acceptance among undergraduate students: is privacy dead? *Education and Information Technologies*. doi:10.1007/s10639-024-13198-6 | Semantic Scholar | 読んだ（出版社の公開 HTML・CC BY-NC-ND） |
| 7 | Kang I, Li D 2025. AI Anxiety to Fatigue and Its Consequences: The Moderating Role of AI Usage Motivation. *Journal of Business Convergence*. doi:10.31152/jb.2025.12.10.6.297 | 出版社の公開ページ（DBpia の `abstract` の meta） | 読めず（DBpia の会員制） |
| 8 | Nobles C 2026. AI Fatigue in Higher Education: A Systematic Review of Associated Conditions, Manifestations, and Lifelong Learning Implications. *Zenodo*. doi:10.5281/zenodo.22838191（版の DOI 10.5281/zenodo.22838190） | DataCite（1 文だけ） | 読んだ（2026-09-30・Zenodo のファイル〈原稿の写しと表〉。2026-09-29 は S-02 の作業中に取得が 403「unusual traffic」で、以後 API も JSON を返さず読めず） |
| 9 | Kim B-J, Lee J 2024. The mental health implications of artificial intelligence adoption: the crucial role of self-efficacy. *Humanities and Social Sciences Communications*. doi:10.1057/s41599-024-04018-w | Semantic Scholar | 読んだ（出版社の公開 HTML・CC BY-NC-ND） |
| 10 | Hur W-M, Shin Y 2024. Service employees' STARA awareness and proactive service performance. *J Services Marketing*. doi:10.1108/JSM-03-2023-0115 | Crossref | 読めず（購読制） |
| 11 | Jeong J, Kim B-J, Lee J 2024. Navigating AI transitions: how coaching leadership buffers against job stress and protects employee physical health. *Frontiers in Public Health*. doi:10.3389/fpubh.2024.1343932 | Crossref | 読んだ（Europe PMC・CC BY） |

- 抄録を取れたもの 10 件（うち #8 は 1 文だけ）・取れなかったもの 1 件（#5）。本文を読んだもの 4 件（#2・#6・#9・#11）→ ★ 2026-09-30 に #3・#8 を足して 6 件（この 2 件はメインが直接読んだ。サブエージェントは使っていない）。

## 2. 1 件ごとの要点

### #1 Asmi ほか 2026（JEIM）—— 抄録

- 横断調査。知識労働者 460 名（国は抄録に無い）。共分散構造分析（CB-SEM）。
- 課題・技術（幻覚を含む）・組織（内容の統制を含む）の 3 水準のストレス要因 → 認知的過負荷と**意思決定疲労**（並列の 2 つのストレイン）→ 生成 AI の利用をやめる意図。
- 著者が報告した結果: 内容の統制を除くすべてのストレス要因が認知的過負荷・意思決定疲労と正に関連。両ストレインが中止の意図に寄与。
- 意思決定疲労の尺度の出典・項目数・項目が AI に触れるかは、抄録からは分からない。

### #2 Honggang ほか 2026（Scientific Reports）—— 本文

- 横断調査（PLS-SEM・多群分析）。中国の公立大学 4 校の英語学習者 **N=545**（中国の学生 412・留学生 133）。層化無作為抽出（熟達度・専攻・デジタルツールの使用頻度）。オンラインと紙の質問紙。収集の年月・大学名は本文に無い。倫理: 揚州大学の IRB（国際学院の学術委員会）の承認（番号の記載なし）。受理 2026-03-18・公開 2026-04-01。
- 疲労系の測定: **デジタル疲労** 6 項目（Sarangal & Nargotra 2022 から。本文の定義は「デジタルの学習基盤への長い関与による認知的・情動的な消耗」）・α=0.90／**デジタル燃え尽き** 24 項目（Erten & Özdemir 2020 のデジタル燃え尽き尺度: デジタル老化 12・デジタル剥奪 6・情動的消耗 6）・α=0.92。項目文は本文に無い。
- AI の変数: **AI 依存の知覚** 5 項目（Morales-García ほか 2019 から）・α=0.86。ほかにテクノストレス 13 項目。
- 著者が報告した結果: デジタル疲労 → 外国語不安 β=0.35（p<0.001）、AI 依存 → 外国語不安 β=0.15（p<0.05）、デジタル燃え尽き → SDG の達成 β=−0.32（p<0.001）。
- データ: 求めに応じて提供。

### #3 Khoso ほか 2026（Acta Psychologica）—— 本文（2026-09-30）

- 横断調査（PLS-SEM・調整つきの直列媒介）。中国の公立大学 4 校（北京・上海・広州・成都）の英語の単位科目を取る学部生 **N=545**（中国の学生 412・留学生 133〈17 か国〉）。層化無作為抽出（国籍・学年・語学学習でのデジタルツールの使用頻度）。適格の条件に「AI の学習基盤を週 2 回以上使う」を含む（選別に答えた 600 名のうち 545 名）。2025 年 3〜4 月に Qualtrics で収集（本文の §3.3 は 4 週間、§3.5 は 3 週間と書く）。倫理: 主たる大学の IRB（承認番号 202505・大学名の記載なし）。資金: 江蘇省社会科学基金（23YYB011）。
- 質問紙の言語: 本文の §3.3 は英語だけで実施し中国語訳は用意しなかったと書き、本文の §3.4 は簡体字中国語への翻訳と逆翻訳を行い中国の学生への補助として残したと書く。予備調査の人数も本文の §3.3 は 38 名、§3.4 は 35 名。
- 疲労系の測定: **デジタル疲労** 6 項目（Sarangal & Nargotra 2022 から。項目例は「オンラインの授業の後に消耗を感じる」）・α=0.89（本文の §3.4.2）、本文の表 4 では 0.871／**デジタル燃え尽き** 24 項目（Erten & Özdemir 2020: デジタル老化 12・デジタル剥奪 6・情動的消耗 6。英語の授業と学習基盤を指すよう書き換えた）・α=0.913（本文の表 4）。5 件法。本文に載る項目例（デジタル疲労 1・デジタル燃え尽き 3）は AI に触れない。全項目は補足資料 1 にあると書く（読んでいない）。
- AI の変数: **AI の倫理への心配（知覚）** 26 項目（Kim & Ko 2022: 透明性 8・公平 5・安全 5・責任 8）・α=0.94。テクノストレス（Wang ほか 2020 から・2 次元）は「AI の道具」などを含むよう項目を書き換えた。
- テクノストレス・**デジタル疲労**・AI の倫理への心配（知覚）→ 外国語学習不安 → **デジタル燃え尽き** → 学業成績 → SDG-4 の達成。テクノロジーの自己効力感が、燃え尽きと成績の負の関係を調整（留学生で大きい）。
- 著者が報告した値: テクノストレス β=0.41・デジタル疲労 β=0.33・AI の倫理への心配 β=0.22（外国語学習不安へ）。間接効果 0.10〜0.19。
- S-02 #2（Honggang ほか 2026, Scientific Reports）との関係: 本文は #2 を序論と文献の節で 3 回引く。同じ標本・同じデータという記述は無い（このファイルの §3 の比較表）。
- データ: 求めに応じて提供。

### #4 Thorpe ほか 2025（AI & Society）—— 抄録

- 調査。オーストラリアの労働者 **N=197**。過去 6 か月の生成 AI の利用・仕事の要求・仕事の裁量・**燃え尽き**を測定。
- 著者が報告した結果: 生成 AI の利用は仕事の裁量と正の関連。仕事の要求・燃え尽きとは有意な関連なし。
- 燃え尽きの尺度は抄録からは分からない。

### #5 Kim & Kim 2026（Technology in Society）—— 題名だけ

- 題名は、AI の導入が「AI テクノストレス」を介して身体の健康に及ぼす影響と、人間中心の AI による緩衝を扱うと述べる（題名に「human exhaustion」）。抄録・本文は読めていない。

### #6 Chung & Kwon 2025（Education and Information Technologies）—— 本文

- 横断調査（PLS-SEM）。韓国の学部生で ChatGPT を使ったことのある人 **N=695**（700 回収のうち 5 件を分析から外した）。本調査は 2023 年 11 月、調査会社（Macromill Embrain）のパネルでオンライン。予備調査は同月、高麗大学のオンラインの場で 107 名。倫理: 高麗大学 IRB（KUIRB-2023-0386-01）。
- 疲労系の測定: **プライバシー疲労**（抄録の定義: プライバシーに関する無力感と倦怠）。項目は Schaufeli ほか 1996（MBI-GS）から翻案。本文は、全尺度の項目に「undergraduate students」と「ChatGPT」を組み込んだと書く。5 件法。項目数と個別の信頼性の値は、本文の表が取り出せず確認できなかった（予備調査で 1 項目を外したことは本文にある）。
- 著者が報告した結果: プライバシー疲労 → 知覚リスク β=−0.359（p<0.001）、→ 利用意図 β=0.108（p<0.01）、→ 成果期待 β=0.126（p<0.001）。
- データ: 相当の理由があれば提供。

### #7 Kang & Li 2025（Journal of Business Convergence）—— 抄録

- 調査（SEM）。韓国の AI 利用者 **N=212**。
- AI による職の置き換えへの不安・AI の学習への不安・AI の成果の不確実さ → **AI 疲労** → 技術ストレスによる欲求不満・組織の凝集性の低下。AI の利用動機が調整（仕事の動機の利用者で影響が大きい）。
- 著者が報告した結果: 3 つの不安はいずれも AI 疲労に寄与し、職の置き換えへの不安の影響が最も大きい。
- AI 疲労の尺度の出典・項目数は抄録からは分からない。

### #8 Nobles 2026（Zenodo）—— 再現パッケージ（原稿の写しと表・2026-09-30）

- 公開 2026-09-19。資料の種別は「Other」。利用許諾は Zenodo の表示で CC BY 4.0（同梱のメタデータの JSON は「著者が選ぶ」のまま）。ファイルは `AI_Fatigue_Reproducibility_Package_v1.0.zip`（244,667 バイト・Zenodo の MD5 と一致）1 つ。中身は原稿の写し（docx）・表 4 本（検索・選別・抽出と評価・コード化）・README など。
- README は、表は原稿の記録から組み立て直したもので、データベースからの元の書き出しや当時の選別の記録ではないと書く。選別で外した記録の 1 件ごとの記録は無い。
- 原稿: 単著の系統的レビュー（米国の大学の所属）。受理・公開の日付の欄は「X of Month, 2026」、データの公開先の欄は識別子を「挿入する」という指示のまま（欄が埋まっていない）。PRISMA 2020 に沿うと書き、統合は物語的・主題的。対象は高等教育の学生と教員。
- 検索: 9 つの情報源（Scopus・Web of Science・ERIC・Education Source・PsycINFO・PubMed・IEEE Xplore・ACM DL・Google Scholar）・2026-07-06〜10・英語・2020 年〜2026 年 7 月。AI × 疲労系の語（technostress・burnout・dependency・well-being などを含む）× 高等教育。
- 選別の数: 304 → 重複 49 を除き 255 → 題名・抄録で 205 → 50 → 取得できず 5 → 45 ＋ 引用の追跡 1 ＝ 46 → 全文で 14 → **32 件**。32 件は一次の実証研究・レビュー・方針や指針の分析・隣の分野の組織の研究を含む。著者の表は 32 件それぞれに統合での役割と評価を付けている（評価はここに写さない）。
- 採択 32 件の DOI と DB・追加候補の突き合わせ（2026-09-30・DOI の一致）: DB にあるもの 3 件（AF006 Parreño ほか 2026・AF007 Miranda ほか 2026・AF008 Soriano ほか 2026）。S-02 #2 と同じ DOI が 1 件（原稿の文献一覧は著者を「Wang, H.」と書く・doi:10.1038/s41598-026-45402-7）。ほかの 28 件は、DB と追加候補の事実のファイルに DOI が無い（うち 2 件〈Um 2026・Klimova & Pikhart 2025〉は S-14・S-15 の抽出の表にレビューとして記録がある）。28 件のふるいは、このファイルの §7。
- 原稿は、改稿で ChatGPT（構成・言語・表の下書き）と Grammarly を使ったと書く。

### #9 Kim & Lee 2024（Humanities and Social Sciences Communications）—— 本文

- 3 時点の時間差調査（5〜6 週間おき・AMOS）。韓国の企業の勤務者 **N=416**（第 1 波 803 → 第 2 波 571 → 第 3 波 418 → 完全回答 416）。調査会社のパネル（約 545 万人）から層化無作為抽出。倫理: 延世大学 IRB（202208-HR-2975-01・承認日 2022-08-15）。本文は、同意を 2022 年 3〜4 月に調査会社のサイトで得たと書く。
- 疲労系の測定: **燃え尽き** 6 項目（Maslach ほか 1997・2001 の MBI から。項目は仕事による情動的・心身の消耗を問い、AI に触れない）・α=0.891（第 3 波）。
- AI の変数: **組織の AI 導入** 5 項目（「組織が人事管理に AI 技術を使っている」などの記述・第 1 波）α=0.949／AI の学習の自己効力感 4 項目 α=0.936。
- 著者が報告した結果: AI 導入 → 仕事のストレス β=0.286（p<0.001）、仕事のストレス → 燃え尽き β=0.568（p<0.001）、AI 導入 → 燃え尽きの直接の効果は無く、間接効果の 95%CI [0.102, 0.230]。AI の学習の自己効力感が AI 導入と仕事のストレスの関係を調整（β=−0.279）。
- データ: 相当の理由があれば提供。

### #10 Hur & Shin 2024（J Services Marketing）—— 抄録

- 2 時点のオンライン調査。韓国の接客・サービスの従業員 **N=301**（小売・飲食・宿泊観光・銀行）。第 1 波: 職が STARA（スマート技術・AI・ロボット・アルゴリズム）に置き換えられうるという認識・自己効力感・レジリエンス・仕事の自律性。第 2 波: 積極的なサービス行動。
- 著者が報告した結果: STARA の認識は仕事の自律性の低下を介して、後の積極的なサービス行動と負に関連。
- 抄録に、疲労・燃え尽き・消耗の測定は挙がっていない。

### #11 Jeong, Kim & Lee 2024（Frontiers in Public Health）—— 本文

- 3 時点の時間差調査（5〜6 週間おき・AMOS）。韓国の企業の勤務者 **N=375**（第 1 波 718 → 第 2 波 507 → 第 3 波 378 → 完全回答 375）。調査会社のパネル（約 439 万人）から層化無作為抽出。収集の年月は本文に無い（投稿 2023-11-24・受理 2024-03-14）。倫理: 延世大学 IRB（番号の記載なし）。
- 測定: 組織の AI 導入 5 項目（#9 とほぼ同じ文言・第 1 波）α=0.92／仕事のストレス（本文は「4 項目」と書き、それより多い項目文を並べる）α=0.90／**身体の健康** 8 項目（全体的な健康・同年代との比較・血圧・血糖・心疾患・脳血管疾患・関節炎など）α=0.87（第 3 波）。
- 疲労・燃え尽き・消耗の尺度は無い（「fatigue」の語は、技術ストレスの身体症状を述べる先行研究の紹介にだけ出る）。
- 著者が報告した結果: AI 導入 → 仕事のストレス β=0.311（p<0.001）、仕事のストレス → 身体の健康 β=−0.276（p<0.01）。

## 3. #2 と #3 の比較（標本）

| 項目 | #2 Scientific Reports | #3 Acta Psychologica |
|---|---|---|
| 著者 | Honggang W・Khoso AK・Althubyani AR | Khoso AK・Honggang W ほか |
| N | 545（中国の学生 412・留学生 133） | 545（中国の学生 412・留学生 133）（2026-09-30 に本文で確かめた） |
| 場所 | 中国の公立大学 4 校 | 中国の公立大学 4 校（北京・上海・広州・成都） |
| 層化の基準 | 熟達度・専攻・デジタルツールの使用頻度 | 国籍・学年・デジタルツールの使用頻度 |
| 質問紙の方式 | オンラインと紙 | オンライン（Qualtrics） |
| 収集の時期 | 本文に無い | 2025 年 3〜4 月 |
| 倫理の記載 | 揚州大学の IRB（番号の記載なし） | 主たる大学の IRB（承認番号 202505・大学名の記載なし） |
| デザイン・解析 | 横断・PLS-SEM・多群分析 | 横断・PLS-SEM（調整つきの直列媒介） |
| 疲労系の変数 | デジタル疲労（Sarangal & Nargotra 2022 の 6 項目・α=0.90）・デジタル燃え尽き（Erten & Özdemir 2020 の 24 項目・α=0.92） | デジタル疲労（同じ出典の 6 項目・α=0.89、表 4 では 0.871）・デジタル燃え尽き（同じ出典の 24 項目・α=0.913） |
| AI の変数 | AI 依存の知覚 | AI の倫理への心配（知覚） |
| そのほか共通の変数 | テクノストレス・外国語不安・テクノロジーの自己効力感（調整）・SDG の達成 | テクノストレス・外国語学習不安・テクノロジーの自己効力感（調整）・学業成績・SDG-4 の達成 |
| デジタル疲労 → 不安 | β=0.35 | β=0.33 |
| 同じデータへの言及 | 本文に無い（サブエージェントとメインの検索で見つからなかった） | 本文に無い。#2 を序論と文献の節で 3 回引く（2026-09-30・「same sample」「dataset」などの語でも本文を探した） |
| 公開 | 2026-04-01 | 2026 年 9 月号（Crossref） |

## 4. 同じ著者が複数ある候補

- Kim Byung-Jik: #5・#9・#11 の著者。#9 と #11 は、同じ系統の 3 時点の調査（延世大学 IRB・調査会社のパネル・5〜6 週間おき）で、組織の AI 導入の 5 項目の文言がほぼ同じ。各波の人数は異なる（#9: 803/571/418/416、#11: 718/507/378/375）。
- Honggang W・Khoso AK: #2・#3（§3）。

## 5. N-06 IEEE DataPort のデータセット 2 件

| 項目 | doi:10.21227/rz27-ze05 | doi:10.21227/94rd-ny74 |
|---|---|---|
| 題名 | AI-Fatigue-Learning-6000: Measuring Artificial Intelligence Fatigue in AI-Assisted Learning Environments | AI-Fatigue-SEM-PLS-15000: A Large-Scale Dataset for Modeling Artificial Intelligence Fatigue in AI-Assisted Learning Environment |
| 作成者 | Wael Badawy（1 名） | Wael Badawy（1 名） |
| 公開 | 2026-06-16（DataPort の引用表記） | 2026（DataCite の登録 2026-06-16） |
| 件数 | 6,000 件の学習者の記録（CSV 96.36 KB） | 15,000 件の学習者のプロファイル・37 の Likert 指標・8 構成概念（CSV 3.13 MB） |
| 変数 | 属性・1 日の AI 利用時間・認知負荷・AI 依存・検証の負担・動機の低下・創造性の抑制・AI 疲労指数・疲労の水準 | AI 利用の強さ・認知負荷・AI 依存・検証の負担・動機の低下・創造性の抑制・学習の効果・AI 疲労（7 指標）・派生の得点・AI 疲労指数 |
| 収集の手続き・対象の国・時期・倫理の記載 | **ページに無い**（説明は「研究を支えるために設計された記録」） | **ページに無い**（説明は「学習の環境を代表するプロファイル」） |
| ファイル | 購読者のみ（取得していない） | 購読者のみ（取得していない） |

- DataCite によると、同じ作成者の IEEE DataPort の登録は 51 件（2025 年 10・2026 年 41）。2026-06-16 の 1 日に、上の 2 件を含む 9 件が登録されている（「AIBT-50K」「AI-Programming-Education-12000」「CPF-2500」など、件数を題名に含む教育データセット）。

## 6. 数のまとめ

- 11 件: 抄録 10（1 件は 1 文だけ）・抄録なし 1・本文 4（★ 2026-09-30 に #3・#8 を足して 6）。
- 疲労系の構成概念を測ったと抄録・本文に書いてあるもの: #1（意思決定疲労）・#2（デジタル疲労・デジタル燃え尽き）・#3（同）・#4（燃え尽き）・#6（プライバシー疲労）・#7（AI 疲労）・#9（燃え尽き）の 7 件。#5 は題名だけ（「exhaustion」を含む）。#10・#11 は疲労系の測定が挙がっていない。#8 はレビュー。
- 項目文・教示に AI が入ると本文で確かめられたもの: #6（ChatGPT を項目に組み込んだと本文が書く）。AI が入らないと本文で確かめられたもの: #9（燃え尽き）。本文を読めず分からないもの: #1・#4・#5・#7。#2 はデジタル疲労の定義がデジタルの学習基盤に向き、項目文は本文に無い。#3 は本文に載る項目例（デジタル疲労 1・デジタル燃え尽き 3）が AI に触れず、全項目は補足資料にある（読んでいない・2026-09-30）。

## 7. #8 の採択研究のうち、DB と追加候補に無かった 28 件（2026-09-30 の突き合わせの時点）

- 手順: 28 件の題名と抄録（OpenAlex・28 件すべて抄録あり）に、S-15 の 0 段目の 3 群（依存・疲労・AI）のうち **AI と疲労の 2 群**（疲労の群は fatigue・depletion・exhaust・burnout・sleep・tired・drowsi）を当てた。依存の群は外した（問いは「AI × 疲労」で、依存は S-15 だけの条件のため）。★ 0 段目の定義（問いごとの 3 群がすべて当たる）どおりではない（2026-09-30 のレビューで書き方を直した）。書誌の記録は次のタスク（20260930-ai-fatigue-judge-file）の `evidence/B9/b9_screen_2026-09-30.json`、スクリプトは同じ場所の `screen_b9.py`（抄録は repo に置かない）。⚠️ 検索の前に固定した手順ではない（#8 の突き合わせの結果を見てから、既存の語群をそのまま当てた・同タスクの `decisions.md` 判断 15）。
- 2 群に当たったもの 4 件。うち一次研究の 2 件を下の表に載せ、追加候補に足した。残る 2 件はレビュー（Um 2026 *Psychiatry Investigation* は S-14 の抽出の表の S-14-009 と S-15 の S-15-179、Klimova & Pikhart 2025 *Frontiers in Psychology* は S-15 の S-15-030 に、抽出の表の `kind` がレビューとして記録がある。OpenAlex の `type` は Um 2026 が article）。
- 疲労の群を S-13・S-14 の群（burnout・exhaust・strain・fatigue）に替えても、増えるのは 1 件（銀行の AI の不正検知の研究・doi:10.3390/jrfm18040217）で、当たった語は `constrain`（「制約する」）の一部の `strain` だった。
- 当たらなかったもの 24 件: AI の語だけ 22 件（AI の導入・方針・指針・レビューなど）、疲労の語だけ 1 件（Halupa & Bolliger 2020: 米国の私立大学 3 校の教員 171 名の技術疲労〈テクノストレスと変化の疲れ〉。抄録に AI の語は無い）、どちらも無し 1 件（Bozkurt ほか 2020: COVID-19 による教育の中断）。

| 研究 | 抄録にあること |
|---|---|
| Alkhatib ほか 2026（Social science review archives.〈OpenAlex の表記〉, doi:10.70670/sra.v4i1.1983） | 横断調査。大学の学部生と大学院生 120 名（18〜30 歳・目的に沿った層化無作為抽出。国は抄録に無い）。尺度: デジタルリテラシー・学業のレジリエンス・認知的過負荷・**デジタル疲労**（出典は抄録に無い）。相関・回帰・媒介の分析。著者は、AI による認知的過負荷とデジタル疲労が学業の困難への対処に負の影響を持ち、デジタルリテラシーとレジリエンスの関係を部分的に媒介したと書く |
| Liu 2026（*Frontiers in Psychology*, doi:10.3389/fpsyg.2026.1795301） | 調査（EFA・SEM）。大学院生 392 名。AI の支援のある英語の学習で、AI リテラシー → 学習への関与・課題の価値 → 外国語の退屈（学業の圧力も）。疲労の尺度は抄録に無い（「emotional fatigue」の語は、課題の価値と退屈の関係を解釈する文にだけ出る） |
