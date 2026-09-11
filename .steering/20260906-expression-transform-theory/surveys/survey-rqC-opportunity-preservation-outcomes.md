# RQ C サーヴェイ: 「機会保存」型アウトカムの操作化に先行はあるか

## 1. 動機

GSE は行き詰まり時に「外部の答えをそのまま受け取って終える」のではなく「自力で解く機会が保存される」ことを狙う。これを行動指標
(`paste_after_stuck_rate` / `self_recovery_without_paste` / `manual_contribution_ratio`) として操作化しようとしているが、
この操作化そのものに先行研究があるか（借りられるか）を、隣接分野（overreliance 研究・ITS help-seeking・writing/coding assistance・
情報探索行動）を横断して確認した。effect size よりも **「変数をどう定義したか」** を主目的として記録している。

## 2. 検証状態

- 探索 angle: 5 系統（(a) overreliance/acceptance rate、(b) manual contribution ratio、(c) hint abuse/gaming the system、
  (d) copy-paste 検出、(e) 反証=適切な依存/under-reliance の害）× 各 3〜6 クエリ、計 約20 クエリ。
- 接触ソース: 約28 件（うち一次全文を pypdf で確認できたもの 6 件: Vasconcelos et al. 2023 全文、Swaroop et al. 2025 全文、
  Baker "Gaming the System: A Retrospective" 全文、NIRVANA 論文全文、Microsoft Aether overreliance レビュー全文、
  Olatunji et al. 2026 全文（WebFetch 経由要約））。残りは WebSearch のスニペット/要約止まり = **二次資料水準**。
- claim 抽出: 23 件。
- 敵対的 3 票検証: confirmed (3-0) 4 件 / confirmed (2-1, 留保付き) 8 件 / 否決 (1-2 以下) 7 件 / 検証対象外（背景情報のみ）4 件。
- ★ 重複潰し確認: `doi:10.1073/pnas.2422633122` (Bastani et al. 2025) と `arXiv:2604.04721` (Liu et al. 2026) は
  探索中に再度ヒットしたが、指示通り「発見」として扱っていない（本報告の登録候補一覧にも含めない）。

## 3. gate 判定（要点先出し）

| 下位問い | 温度 | 一言 |
|---|---|---|
| (a) 受容率そのものを outcome にした overreliance 研究 | **確定** | "overreliance rate" = 「AI が誤っている条件下で AI 提案に一致した割合」という条件付き率が確立した操作化として存在する（Vasconcelos 2023 / Swaroop 2025 / Buçinca 2021 ほか）。関連指標（switch fraction, WOA）も体系化されている（Passi & Vorvoreanu 2022 のレビュー）。ただし対象はほぼ全て「単発の判断課題」で GSE の「行き詰まり」文脈とは異なる。 |
| (b) 成果物の本人比率を outcome にした writing/coding 研究 | **確定（ただし writing 領域に限定）** | NIRVANA (Jelson et al. 2026) の Human Contribution Ratio (HCR) が `manual_contribution_ratio` とほぼ同型の定義をすでに持つ。コード領域は業界ブログ水準の推定値が乱立し（10%〜95%）、査読済み・厳密な controlled outcome としての「寄与比率」はまだ薄い。 |
| (c) 行き詰まりからの自力脱出 (hint abuse / gaming the system) | **確定（20年蓄積は実在）だが GSE の文脈への転用は PLAUSIBLE BUT UNPROVEN** | Baker et al. 2004 以降、gaming the system / help abuse の機械学習検出器と学習への負の相関は確立済み。しかし「行き詰まり→外部から答えを受領」ではなく「閉じたカリキュラム内でのヒント連打」が対象で、トリガーの定義が GSE と異なる。 |
| (d) コピペ/検索結果転記の行動ログ計測 | **判定不能（PLAUSIBLE BUT UNPROVEN、一部は否決）** | 存在はするが (i) 剽窃検出フレーミングに偏る（RQ の除外条件に抵触）、(ii) 小 N パイロット止まり (Olatunji et al. 2026, N=18)、(iii) 効果がほぼ null (物理宿題コピー検出, 26 問中 3 問のみ有意)。「学習過程の指標として」使った頑健な例は見つからなかった。 |
| (e) 反証: 受容率を下げること自体が良いとは限らない | **確定** | Dietvorst et al. 2015 (algorithm aversion)・Buçinca et al. 2021 (cognitive forcing の代償)・Ma et al. 2024 (Devil's Advocate が overreliance を下げるが under-reliance を上げる) が明確にこのトレードオフを実証している。GSE の指標設計に直撃する。 |

## 4. ★★★ 操作化の対応表（本ラウンド最重要）

| GSE 指標 | 借りられるか | 根拠 |
|---|---|---|
| `paste_after_stuck_rate` | **(ii) 部分的に借りられる** | 構造（「トリガー状態が成立した条件下での受容率」という条件付き率の型）は Vasconcelos et al. 2023 の逐語定義から直接借りられる: *"Overreliance: We define overreliance as the percentage of decisions when a human decision maker accepts an AI's incorrect prediction... if a decision-maker agreed with the AI's prediction 80% of the time when the AI was incorrect, then the overreliance is 80%."* (arXiv:2212.06823, §4.5)。Swaroop et al. 2025 (IUI, DOI:10.1145/3708359.3712128) も同型: *"Overreliance rate: the proportion of times participants gave the same answer as an AI recommendation, conditioned on the AI recommendation not being optimal."* ★ しかし **トリガー条件が違う**: 先行は「AI が客観的に誤っている」という第三者検証可能な条件、GSE は「本人が行き詰まっている」という内的状態（HMM 推定）が条件。この差は軽くない — GSE 版は「トリガー検出自体の妥当性」という先行にはない検証負荷を追加で負う。 |
| `self_recovery_without_paste` | **(iii) 自前で定義するしかない** | 直接の precedent は見つからなかった。最も近い代理指標は 2 つ: (1) 既登録の Liu et al. 2026 (arXiv:2604.04721) の `skip rate`（持続性の代理、d=0.25/0.10/0.42）——ただしセッション末の「投げ出したか」であり GSE が求める「行き詰まり直後に自力で再開したか」という**瞬間**の粒度ではない。(2) Danry et al. 2026 (CHI, 二次資料水準・MIT News 経由) の「4週間後の無支援成績が baseline 比 -15pt」——これは**スキル保持の長期減衰**であり、瞬間的な自力回復とは時間粒度が全く異なる。両者とも「型」は近いが「粒度」が違うため、GSE の変数をそのまま埋める先行は無い。 |
| `manual_contribution_ratio` | **(i) 先行から借りられる** | NIRVANA (Jelson et al. 2026, arXiv:2604.07344) が **ほぼ同一の変数を厳密に定義済み**: `HCR = (HA − HD) / ((HA − HD) + (GP − GD))` （HA=人間が追加した語数, HD=人間が削除した語数, GP=ChatGPT からペーストされた語数, GD=削除された ChatGPT 由来語数）。0〜1 で 1 が完全自筆。N=77 の大学生ライティング課題で実測され、4 つの writer profile（Lead Authors HCR=0.98 〜 Vibe Writers HCR≈0.01）に判別力があることも確認済み。★ ただし writing (ChatGPT + エッセイ) 領域限定で検証されており、GSE が想定するコーディング/汎用作業への転用は未検証。 |

**総合**: GSE の 3 指標は **1/3 が直接借用可能 (manual_contribution_ratio)、1/3 が構造だけ借用可能 (paste_after_stuck_rate)、1/3 は自前設計が必要 (self_recovery_without_paste)** という混合状態。「機会保存」を単一の借用可能なフレームワークとして丸ごと輸入できる先行は存在しない。

## 5. カード（落合フォーマット、[検証済 3-0/2-1] 表記）

### [検証済 3-0] Vasconcelos et al. 2023, "Explanations Can Reduce Overreliance on AI Systems During Decision-Making"
- **出典 key**: arXiv:2212.06823 / Proc. ACM Hum.-Comput. Interact. 7, CSCW1, Article 129 (2023)（一次全文確認済み）
- 1. どんなもの: AI 判断支援における overreliance（AI の誤った推奨をそのまま受け入れる率）を、説明 (explanation) の提示形式・課題難度・金銭的インセンティブで操作し、4 つの実験 (N=340/340/286/114) で計測。
- 2. 先行と比べて何がすごいか: overreliance を「認知の必然」ではなく「コスト・ベネフィットに応じた戦略的選択」として初めて実証的に位置づけた。
- 3. 技術・手法の肝: `overreliance = AI が誤っている場合に人間が AI 推奨に同意した割合` という条件付き率。ベイズ線形混合モデルで 95%信用区間が 0 を跨がないかで判定。
- 4. どう有効と検証したか: 難課題では説明が overreliance を有意に下げる (Hard: 推定差 1.74, 95%CI [0.89, 2.76])。中程度課題では効果なし（H1c 不支持）——効果は課題難度に条件付き。
- 5. 議論: 効果は難易度・インセンティブに強く依存し普遍的ではない。プロリフィックのクラウドワーカーによる合成論理パズル課題であり、GSE が想定する「進行中の創作/コーディング作業」とは生態学的妥当性が異なる。
- 6. 次に読むべき論文: Buçinca et al. 2021 (cognitive forcing functions)、Swaroop et al. 2025 (personalization)。
- **GSEへの含意**: `paste_after_stuck_rate` の分母定義（「介入が刺さる条件」を絞ってから率を取る）はこの論文の設計をそのまま輸入できる。ただし GSE の「トリガー」（行き詰まり検出）は AI 正誤のような外形的検証可能性を持たない点が構造的な弱点として残る。

### [検証済 3-0] Swaroop, Buçinca, Gajos, Doshi-Velez 2025, "Personalising AI Assistance Based on Overreliance Rate in AI-Assisted Decision Making"
- **出典 key**: DOI:10.1145/3708359.3712128 (IUI '25)（一次全文確認済み・Harvard 著者ページ PDF）
- 1. どんなもの: 個人ごとの overreliance rate（「AI が最適でない/誤っているときに AI 提案と同じ答えを出す割合」）を probe question で素早く推定し、AI アシスタンスの出し方（AI-before / AI-after）を個人化する。
- 2. すごいところ: overreliance を「安定した個人特性」ではなく「タスク内で学習される戦略」として扱い、probe question だけで overreliance quality を実験1の後半データより先に予測できることを示した。
- 3. 手法の肝: `overreliance rate = 条件（AIが最適でない/誤っている）下でAI推奨と一致した回答の割合`。実験1で全ポリシー共通 AI-suboptimal overreliance = 0.58±0.05、AI-wrong overreliance = 0.22±0.05。実験2の personalised policy では AI-wrong overreliance が 0.41±0.05 まで上昇するケースも観測（=個人化が裏目に出ると overreliance が悪化しうる）。
- 4. 検証: 2 つの実験、IRB 承認済み、ヒストグラムによる戦略クラスタ分析。
- 5. 議論: 「良い方向の個人化」が常に成功するとは限らない（実験2で overrelier でない群が maladaptive policy を学習してしまうケースを報告）——介入設計の副作用に自覚的。
- 6. 次に読むべき: Bhatt et al. (モデル選好の個人化)、Buçinca et al. 2024 (Accuracy-Time Tradeoffs)。
- **GSEへの含意**: 「率を 2 種類に分解する」設計（suboptimal 条件 vs wrong 条件）は、GSE が `paste_after_stuck_rate` を「軽い行き詰まり」と「深い行き詰まり」で分けて報告する際の直接のテンプレートになる。

### [検証済 3-0] Jelson et al. 2026, "NIRVANA: A Comprehensive Dataset for Reproducing How Students Use Generative AI for Essay Writing"
- **出典 key**: arXiv:2604.07344（一次全文確認済み・html版から本文抽出）
- 1. どんなもの: N=77 の大学生がエッセイ課題を ChatGPT 統合エディタで行い、キーストローク・会話履歴・コピペイベントを全記録したデータセット。
- 2. すごいところ: `manual_contribution_ratio` にほぼ相当する変数を初めて厳密に数式化し、4 つの writer profile に判別力があることを実測で示した。
- 3. 手法の肝: **HCR = (HA − HD) / ((HA − HD) + (GP − GD))**、**HER = (HA + HD + GD) / (HA + HD + GP + GD)**（HA=人間追加語数、HD=人間削除語数、GP=AIからペーストされた語数、GD=削除されたAI由来語数）。
- 4. 検証: Lead Authors (n=37, HCR=0.98) / Collaborators (n=15, HCR=0.53) / Drafters (n=11, HCR=0.09) / Vibe Writers (n=14, HCR≈0.01) の 4 群に分離、可読性・体感オーナーシップと相関。
- 5. 議論: 単一機関・単一課題（エッセイ）・ChatGPT 限定。コーディングや多様な業務への一般化は未検証。HCR は「量」（語数）だけを見ており「質」（アイデアの由来）は捉えない点は本論文内でも限界として言及されると推測されるが、この点は一次確認できていない（要フォロー）。
- 6. 次に読むべき: 「Modifying AI, Enhancing Essays」(arXiv:2412.07200, active engagement 指標), 「Assessing LLM Text Detection: Does Human Contribution Affect Detection?」(arXiv:2508.08096)。
- **GSEへの含意**: `manual_contribution_ratio` は **このまま輸入できる可能性が高い**唯一の GSE 指標。GSE のログ設計（誰が追加/削除したか、外部由来かどうかのタグ付け）が HCR と同じ粒度で取れているか確認する価値がある。

### [検証済 2-1] Dietvorst, Simmons, Massey 2015, "Algorithm Aversion: People Erroneously Avoid Algorithms After Seeing Them Err"
- **出典 key**: PubMed 25401381 / Journal of Experimental Psychology: General, 144(1), 114-126（二次資料水準：要約のみ確認、全文未読）
- 1. どんなもの: アルゴリズムが人間より正確に予測できる場面でも、人はアルゴリズムの誤りを一度見ただけで過度に信頼を失い、劣った人間の予測者を選んでしまう現象を 5 実験で実証。
- 2. すごいところ: 「受容率が低いこと＝良いこと」という直感を覆す、JDM 分野の基礎文献。
- 3. 手法の肝: 予測者（人間 vs アルゴリズム）の過去の成績を見せた後、将来の予測にインセンティブを結びつける対象をどちらか選ばせる、という選択率を outcome にしている。
- 4. 検証: 5 実験、アルゴリズムが人間に勝っている場面でも同じ小さな誤りに対しアルゴリズムの方に非寛容になることを一貫して示す。
- 5. 議論: 一貫して再現されてきた頑健な効果だが、あくまで「予測」課題であり、GSE の「行き詰まり中に貼り付けを受け取るか」という文脈とは距離がある。
- 6. 次に読むべき: Logg, Minson, Moore 2019 (algorithm appreciation, 逆方向の現象)。
- **GSEへの含意**: `paste_after_stuck_rate` が低いことを単純に「良い」と解釈してはいけない、という最重要の警句を与える一次文献（要全文確認）。

### [検証済 2-1] Ma et al. 2024, "Beyond Recommender: An Exploratory Study of the Effects of Different AI Roles in AI-Assisted Decision Making"
- **出典 key**: arXiv:2403.01791（二次資料水準：要約のみ）
- 1. どんなもの: AI の役割 (Recommender / Analyzer / Devil's Advocate) × AI 性能水準 (高/低) を操作し、overreliance と under-reliance を両方測定。
- 2. すごいところ: overreliance を下げる介入 (Devil's Advocate) が under-reliance を代償として増やすという **トレードオフを同一実験内で直接実証**した数少ない研究。
- 3. 手法の肝: overreliance と under-reliance を対にした 2 変数として並置測定（AI が正しい場合の不採用率 = under-reliance、誤っている場合の採用率 = overreliance）。
- 4. 検証: 高 AI 性能下で Devil's Advocate は Analyzer より overreliance が有意に低い (p<.01)。ただし高 AI 性能下では Recommender の方が under-reliance が Analyzer/Devil's Advocate より有意に低い (p<.01, p<.001)。
- 5. 議論: 「良い介入」の定義がロール依存で入れ替わる。単一指標 (overreliance だけ) で介入を評価すると見誤る。
- 6. 次に読むべき: Buçinca et al. 2021、cognitive forcing functions の一般化条件。
- **GSEへの含意**: `paste_after_stuck_rate` を下げる Nudge 設計は、同時に「本来受け取るべきだった有効な助けまで拒否させる」副作用（GSE 版 under-reliance）を生みうる。単指標での成功宣言をしない設計が必要。

### [検証済 2-1] Baker, Corbett, Koedinger, Wagner 2004, "Off-Task Behavior in the Cognitive Tutor Classroom: When Students 'Game the System'"
- **出典 key**: DOI:10.1145/985692.985741 (CHI 2004, pp.383-390)（二次資料水準＋関連の Baker 本人による回顧録全文 (learninganalytics.upenn.edu/ryanbaker/PSCS-gaming-v6.pdf) は一次確認済みだが、そちらは方法論的回顧でありオリジナルの数値は含まれていなかった）
- 1. どんなもの: 実教室での Cognitive Tutor 使用ログから「gaming the system」（正解を得るためにヒントやシステムの規則性を悪用する行動）を機械学習モデルで検出。
- 2. すごいところ: 「gaming the system」という構成概念を確立し、機械学習検出器の妥当性を実教室デプロイで検証した最初期の研究。
- 3. 手法の肝: アクションログの特徴量（ヒント連打の速さ、誤答パターン等）から gaming 確率を予測する潜在応答モデル。
- 4. 検証: 実教室規模のログでモデルの予測的妥当性を検証（詳細な N・効果量は二次資料からの引用に留まり要一次確認）。
- 5. 議論: 後続研究 (Baker et al. 2008, Shih et al. 2008/2010) は gaming に「有害」「非有害」の 2 種があるとして単純な負の効果を修正している——**「ヒント連打=悪」と単純化すると先行研究の分岐点を見落とす**。
- 6. 次に読むべき: Aleven & Koedinger 2000 (help abuse の原型)、Shih, Koedinger, Scheines 2008 (bottom-out hint と学習の正の関係)。
- **GSEへの含意**: 20年の蓄積がある「行き詰まり回避行動の検出」パラダイムそのものは GSE の `self_recovery_without_paste` 設計の先例になるが、ITS は「閉じたカリキュラム内のヒント」が対象で、GSE の「開かれた作業での外部貼り付け」とはトリガーの性質が違う——**転用は要検証**。

### [検証済 2-1] Vakkari, Völske, Potthast, Hagen, Stein 2019, "Modeling the Usefulness of Search Results as Measured by Information Use"
- **出典 key**: Information Processing & Management 56(3), 879-894（二次資料水準：要約のみ）
- 1. どんなもの: 長文エッセイを書く執筆者が検索結果からコピペ（+ 編集）した内容を追跡し、その量から検索結果の「有用性」を予測。
- 2. すごいところ: コピペという行動ログを「有用な情報を見つけた成功のシグナル」として肯定的に位置づけた点が GSE の前提と対称的。
- 3. 手法の肝: コピペイベント＋その後の編集の有無を情報利用の指標として符号化。
- 4. 検証: この指標で執筆者の情報探索の成功度を高精度に予測できたと報告（詳細な効果量は要一次確認）。
- 5. 議論: **本論文はコピペを「悪い受容」ではなく「成功した情報利用」として扱っており、GSE の価値づけと真っ向から対立する**——これは (e) の反証角度そのもの。
- 6. 次に読むべき: Vakkari 2021 (Predicting essay quality from search and writing behavior)。
- **GSEへの含意**: `paste_after_stuck_rate` の「貼り付け=機会喪失」という価値づけは、情報探索行動研究の標準的な価値づけ（貼り付け=有用な情報を見つけた証拠）と衝突する。GSE はこの対立を明示的に議論する必要がある（受け取った答えを「そのまま」使うか「足場」にするかの違いで整理するのが妥当）。

### [検証済 2-1] Passi & Vorvoreanu 2022 (Microsoft Aether), "Overreliance on AI: Literature Review"
- **出典 key**: Microsoft Research (Aether) レポート（一次全文確認済み・pypdf 抽出。ただしレポート自体が~60本の二次統合であることに留意）
- 1. どんなもの: overreliance に関する約60本の論文を統合したレビュー。
- 2. すごいところ: overreliance の測定方法を一覧化した唯一級のタクソノミー（本 RQ にとって一次資料級の価値）。
- 3. 手法の肝: 4 つの主要な測定法を整理: (i) **Agreement with incorrect recommendations**（Buçinca et al. 2021 の定義=誤った推奨のうち受け入れた割合）、(ii) **Switch fraction**（AI推奨に完全に答えを変えた頻度、Lu & Yin 2021; Kim et al. 2021）、(iii) **Modifying answers to align**（変更度合いの%、Kim et al. 2021）、(iv) **Weight of Advice (WOA)** = `(revised_prediction − initial_prediction) / (AI_recommendation − initial_prediction)`（Logg et al. 2019）。
- 4. 検証: レビュー論文のため一次検証はなし、統合のみ。
- 5. 議論: "Appropriate reliance is a moving target because it is hard to operationalize and depends on context and application domain." — 本 RQ の結論を裏書きする逐語。
- 6. 次に読むべき: レビューが引用する Bansal et al. 2019, Green & Chen 2019, Suresh et al. 2020。
- **GSEへの含意**: `paste_after_stuck_rate` を設計する際、単純な二値受容率だけでなく WOA のような「どれだけ答えに引き寄せられたか」の連続量も検討候補にできる（GSE では「貼り付け後にどれだけ編集せず使ったか」に対応）。

## 6. 登録候補一覧

| 仮 key | 出典 | N | 設計 | 効果量 | 操作化の定義 | 確認水準 |
|---|---|---|---|---|---|---|
| vasconcelos2023-overreliance | Vasconcelos, Jörke, Grunde-McLaughlin, Gerstenberg, Bernstein, Krishna. "Explanations Can Reduce Overreliance..." Proc.ACM HCI CSCW1 (2023). arXiv:2212.06823 | 340/340/286/114 (4研究) | オンライン実験・Bayesian混合モデル | Hard task: 1.74 [0.89,2.76] (説明効果) | overreliance=誤ったAI推奨を受容した割合 | 一次確認済み |
| swaroop2025-personalising | Swaroop, Buçinca, Gajos, Doshi-Velez. IUI'25. DOI:10.1145/3708359.3712128 | 未確認（実験1後半+実験2、Bachelor 232名等の記述あり） | オンライン実験・probe question | overreliance rate 0.22〜0.61 (条件により) | overreliance rate=AI最適でない/誤っている時にAI一致した割合 | 一次確認済み |
| bucinca2021-cognitive-forcing | Buçinca, Malaya, Gajos. "To Trust or to Think" Proc.ACM HCI CSCW1 (2021). arXiv:2102.09692 | 未確認 | オンライン実験 | 記載: forcing functionsがoverreliance有意減 | agreement with incorrect recommendations | 二次資料水準 |
| dietvorst2015-algorithm-aversion | Dietvorst, Simmons, Massey. J.Exp.Psych:General 144(1) (2015). PMID:25401381 | 5実験 (N未確認) | 実験室実験・予測課題 | アルゴリズムを見た群は選択率が有意に低下（一貫再現） | 予測主体(人/アルゴリズム)の選択率 | 二次資料水準 |
| logg2019-algorithm-appreciation | Logg, Minson, Moore. OBHDP 151 (2019) | 6実験 | 実験室実験 | WOAが人間助言よりアルゴリズム助言で高い | Weight of Advice (WOA) 連続量 | 二次資料水準 |
| ma2024-beyond-recommender | Ma et al. "Beyond Recommender..." arXiv:2403.01791 | 未確認 | 2(AI役割)×2(AI性能)実験 | Devil's Advocate: overreliance↓(p<.01) but under-reliance↑(p<.01/.001) | overreliance/under-reliance対 | 二次資料水準 |
| jelson2026-nirvana | Jelson et al. arXiv:2604.07344 (2026) | N=77 | ライティング課題・キーストローク+コピペログ | HCR 0.01〜0.98 (4 profile間) | HCR=(HA-HD)/((HA-HD)+(GP-GD)) | 一次確認済み |
| baker2004-gaming-system | Baker, Corbett, Koedinger, Wagner. CHI2004, DOI:10.1145/985692.985741 | 実教室規模 (N未確認) | 機械学習検出器+教室デプロイ | 学習量への負の相関（「2/3」の数値は未一次確認） | gaming確率=ML検出器の出力 | 二次資料水準 |
| aleven2000-help-abuse | Aleven & Koedinger. ITS 2000 (仮) | 未確認 | ITS ログ分析 | help abuseと学習の負の相関（詳細未確認） | help abuse (bottom-out hint連打) | 二次資料水準・書誌未確定 (provisional) |
| vakkari2019-search-usefulness | Vakkari, Völske, Potthast, Hagen, Stein. IPM 56(3) (2019) | 未確認 | ライティング+検索課題 | コピペ量で情報利用成功を高精度予測（詳細未確認） | コピペイベント+編集の有無 | 二次資料水準 |
| olatunji2026-do-not-copy-paste | Olatunji, Djire, Klein, Bissyandé. arXiv:2608.22638 (ASE'26) | N=18 (行動パイロット) | Unicode摂動 × 2群比較パイロット | 直接コピー 3.83 vs 5.00件（有意性未報告） | Copy-Paste Resistance (CPR) = 摂動後に構文エラー化した正解コード件数/正解コード総数 | 一次確認済み（WebFetch要約） |
| pastetrace2026 | (著者未確認、University of Hawai'i系, provisional) arXiv:2506.17355 | ツール論文 (評価N未確認) | IDE統合リアルタイムログ | 未実施（ツール提案のみ） | ペーストイベントのリアルタイム追跡 | 二次資料水準・書誌未確定 |
| physrevper2022-answer-copying | 著者未確認 (provisional). Phys.Rev.Phys.Educ.Res. 18, 010126 (2022) | 26問題, 自己申告42名 vs 残り | 試行時間分布の混合モデル | 26問中3問のみ有意差（ほぼnull） | 試行時間の短さ分布からのコピー検出 | 二次資料水準 |
| danry2026-dialogues-ai | Danry, Rani, Liang, Lippman, Maes. CHI2026 (仮、arXiv未確認) | N=67, 4週間 | 縦断・before/after | 無支援成績が baseline比 -15pt (4週後) | 「Dependency Developer」比率 (~20%)、無支援時パフォーマンス変化 | 二次資料水準（MIT News経由、原論文未読） |
| passi2022-aether-review | Passi & Vorvoreanu. Microsoft Research (2022) | ~60論文レビュー | 文献レビュー | N/A | overreliance測定法のタクソノミー(agreement rate/switch fraction/WOA等) | 一次確認済み |
| ziegler2024-copilot-productivity | Ziegler et al. Commun.ACM (2024年3月号)（書誌詳細未確認, provisional） | N=934,533 (テレメトリ) | 大規模観察研究 | acceptance rate(28.9%→32.1%)が生産性実感の最良予測子 | Copilot提案の受容率(テレメトリ) | 二次資料水準 |

## 7. 否決リスト

- ⚠️ 「AIコード生成の割合は業界で10%〜95%」系の主張（各種ブログ/ベンダー統計） — 査読なし・方法論バラバラ・自己申告混在で、頑健な操作化の先行例としては**否決**（0-3）。base rate の参考程度に留める。
- ⚠️ Olatunji et al. 2026 の行動パイロット (N=18) の「効果」（直接コピー減少）— サンプル過小・有意性未報告のため効果としては**否決**（1-2）。CPR という**指標定義自体**は登録候補として残す。
- ⚠️ Phys.Rev.PER 2022 の「宿題コピー検出」— 26問中23問で有意差なし、事実上の null 結果のため効果としては**否決**（0-3）。検出手法（試行時間分布のfinite-mixture modeling）は方法論として参考価値あり。
- ⚠️ "Detecting Verbatim LLM Copy-Paste in Homework" (arXiv:2605.16336) — RQ が明示的に除外した「剽窃検出」フレーミングそのものであり、「学習/問題解決過程の指標」としての用途ではないため**除外**（gate対象外・否決）。
- ⚠️ Baker et al. 2008 / Shih et al. 2008 の「gaming に非有害な下位種がある」主張 — Baker 2004 の主張と直接対立し、CTAT/Cognitive Tutor という単一エコシステム内の再分析に留まるため、「gaming=一様に有害」という単純化に対する反証としては**留保付き 1-2** （命題としては成立するが、GSE文脈への外挿は不可）。
- ⚠️ 医療 CDS のアラートオーバーライド率 (46%〜96%) を overreliance の系として使う案 — 一次研究間のばらつきが大きすぎ、方法論的異質性の疑いが強いため単一の効果としては**否決**（研究間異質性 0-3）。「率のレンジがそもそも巨大に振れる」という事実の参考程度。
- ⚠️ Vakkari 2019 の「コピペ=情報利用成功」という主張をそのまま「GSEの貼り付けも実は良い」と読み替えること — これは誤読であり**却下**。GSE 文脈は「行き詰まり後にそのまま受け取って終わる」ことを問題視しており、Vakkari の文脈（能動的な情報探索の結果としての編集込みコピペ）とはトリガー条件も後続行動も異なる。両者は**対称的だが同一視できない**（否決理由として明記）。

## 8. 結論

GSE の 3 指標は **混合状態**である: `manual_contribution_ratio` は **(i) 先行から借りられる**（NIRVANA の HCR がほぼ同型）。`paste_after_stuck_rate` は **(ii) 部分的に借りられる**（「条件付き受容率」という型は overreliance rate 研究群から輸入できるが、トリガー条件の性質—AI正誤の外形的検証可能性 vs 内的状態推定—が異なるため丸ごとの輸入はできない）。`self_recovery_without_paste` は **(iii) 自前で定義するしかない**（時間粒度の合う precedent が存在しない）。

★ (e) を踏まえた留保: **どの指標であれ、改善（例: `paste_after_stuck_rate` の低下）を単純に「良い」と解釈してはならない。** Dietvorst et al. 2015 は「受容率の低下が単なる不合理な回避（algorithm aversion）でありうる」ことを、Ma et al. 2024 は「overreliance を下げる介入が under-reliance という別の害を生む」ことを、Vakkari et al. 2019 は「同じ行動（コピペ）が別の文脈では成功の証拠にすらなる」ことを示している。GSE が指標の改善を主張する際は、必ず (1) 課題の最終品質、(2) 本人の以降の自力遂行能力、の少なくとも一方を対にして報告し、「率が下がった＝良い」という単指標の宣言をしないことを設計原則にすべきである。

## 9. やり残し

1. Buçinca et al. 2021 (arXiv:2102.09692) の全文を pypdf で一次確認し、cognitive forcing functions が課したユーザー体験上のコストの正確な効果量を取る。
2. Aleven & Koedinger 2000 の正式書誌（タイトル・掲載誌）を確定させる — 現状 provisional。
3. Danry et al. 2026 の原論文（CHI 2026 proceedings もしくは arXiv）を特定し、MIT News 経由の二次要約から一次確認へ格上げする。
4. NIRVANA 論文中で HCR の限界（「量は測れるが質は測れない」等）が明示的に論じられているかを本文精読で確認する。
5. コード領域（`manual_contribution_ratio` のコーディング版）について、査読済み controlled study（業界ブログではなく）が今後出るか継続監視する。現状は「業界推定値の乱立」止まりで学術的な precedent が薄い。
6. `self_recovery_without_paste` については、ITS の help-seeking 文献 (Roll, Baker, Aleven, McLaren, Koedinger 2005 の "Modeling Students' Metacognitive Errors") のような「ヒントなしで自力継続できたか」を瞬間粒度で測った研究がないか、次ラウンドで別 angle（"unassisted problem-solving resumption" 等）で深掘りする価値がある。
7. Ziegler et al. 2024 (CACM) の正式な巻号・DOI を確認する。
