# 参考文献 (References)

中央書誌 SSOT。設計書・実験ノート・研究ポジショニングの本文 `[Pn]`/`[Vn]` はここを参照する。

## 採番方式（重要）

GSE には**2 つの先行する局所書誌**が存在し、それぞれ独自の `[1..N]` 番号を既に使っている:

- **`P` 名前空間** = 提案プロジェクトの理論構築書誌（`docs/[提案プロジェクト補足資料]GSE_proposal_参考文献.md`、`[P1]..[P15]`）
- **`V` 名前空間** = ユーザー検証の方法論書誌（`Form_Phase1/ユーザー検証_codex-review_v0.4`、`[V1]..[V17]`）

両者を 1 本に renumber すると既存ドキュメントの inline 番号が全てずれるため、**名前空間を保持して統合**する
（citation-ssot の append-only・恒久 ID・renumber 禁止を、名前空間ごとに守る）。新規研究ドキュメント
（research-positioning.md 等）は `[Pn]`/`[Vn]` を直接引用する。重複文献は「重複」列で相互リンクする。
追加・撤回ルールは名前空間内で append-only / tombstone / 再利用禁止。重複防止キーは DOI / arXiv / 正規化 URL。

---

## P 名前空間 — 理論基盤（提案書誌）

| [n] | key | 著者・タイトル | 出典・年 | URL | GSE 設計での接地 | 重複 | 状態 |
|---|---|---|---|---|---|---|---|
| [P1] | doi:10.1016/j.neubiorev.2024.105572 | León Méndez, M. et al. — Effects of internet and smartphone addiction on cognitive control in adolescents and young adults: a systematic review of fMRI studies | Neurosci. Biobehav. Rev. 159:105572, 2024 | — | 動機: デジタル依存→認知制御の毀損 | — | active |
| [P2] | doi:10.1073/pnas.1510459112 | Bratman, G. N. et al. — Nature experience reduces rumination and subgenual prefrontal cortex activation | PNAS 112(28):8567, 2015 | <https://doi.org/10.1073/pnas.1510459112> | Physical Anchor（自然・反芻低下）の理論根拠 | =V9 | active |
| [P3] | url:weforum-fojr-2025 | World Economic Forum — Future of Jobs Report 2025 | WEF, 2025 | <https://www.weforum.org/publications/the-future-of-jobs-report-2025/> | 動機: 労働・スキルの文脈 | — | active |
| [P4] | url:gitclear-copilot-2024 | GitClear — Coding on Copilot: 2023 Data Suggests Downward Pressure on Code Quality | GitClear, 2024 | <https://www.gitclear.com/coding_on_copilot_data_shows_ais_downward_pressure_on_code_quality> | 動機: AI 依存の品質毀損（実証） | — | active |
| [P5] | url:harvard-ai-minds-2025 | Harvard Gazette — Is AI dulling our minds? | Harvard, 2025 | <https://news.harvard.edu/gazette/story/2025/01/is-ai-dulling-our-minds/> | 動機: 認知オフロードの一般的論点 | — | active |
| [P6] | proc:design-society-2019 | Kawakami, H. & Naito, K. — Benefit of Inconvenience (不便益) | Proc. Design Society, 2019 | — | コア思想: 不便益（利便性と便益の直交） | — | active |
| [P7] | doi:10.2196/59247 | Park, J. H. — Discriminant Power of Smartphone-Derived Keystroke Dynamics for MCI | J. Med. Internet Res. 26:e59247, 2024 | <https://doi.org/10.2196/59247> | キーストローク→認知プロキシの妥当性 | =V13 | active |
| [P8] | doi:10.1037/a0036577 | Oppezzo, M. & Schwartz, D. L. — Give your ideas some legs: the positive effect of walking on creative thinking | J. Exp. Psychol. LMC 40(4):1142, 2014 | <https://doi.org/10.1037/a0036577> | Physical Anchor（歩行→創造性）の理論根拠 | =V8 | active |
| [P9] | book:metacognition-1994 | Bjork, R. A. — Memory and Metamemory Considerations in the Training of Human Beings | in Metcalfe & Shimamura (Eds.), Metacognition, MIT Press, 1994 | — | 望ましい困難（desirable difficulties） | — | active |
| [P10] | doi:10.1016/0272-4944(95)90001-2 | Kaplan, S. — The restorative benefits of nature: toward an integrative framework | J. Environ. Psychol. 15(3):169, 1995 | <https://doi.org/10.1016/0272-4944(95)90001-2> | Physical Anchor（注意回復理論 ART） | =V12 | active |
| [P11] | arXiv:2511.12468 | Mehta, A. et al. — Detecting LLM-Assisted Academic Dishonesty using Keystroke Dynamics | arXiv:2511.12468, 2025 | <https://arxiv.org/abs/2511.12468> | AI 依存の content-free 検出（補助指標） | =V6 | active |
| [P12] | doi:10.1080/07370000802212669 | Kapur, M. — Productive Failure | Cognition and Instruction 26(3):379, 2008 | — | コア概念: 生産的苦闘（productive struggle/failure） | — | active |
| [P13] | isbn:978-0-14-311526-7 | Thaler, R. H. & Sunstein, C. R. — Nudge: Improving Decisions About Health, Wealth, and Happiness | Yale Univ. Press, 2008 | — | Lv1 Nudge 介入の理論根拠 | — | active |
| [P14] | doi:10.1146/annurev-neuro-071013-014030 | Raichle, M. E. — The Brain's Default Mode Network | Annu. Rev. Neurosci. 38:433, 2015 | — | Incubation 状態（DMN/マインドワンダリング） | — | active |
| [P15] | url:fu-berlin-gse-scale | Schwarzer, R. & Jerusalem, M. — Generalized Self-Efficacy Scale | in Measures in Health Psychology, NFER-NELSON, 1995 | <http://userpage.fu-berlin.de/~health/selfscal.htm> | 自己効力感の測定（一般性=副指標） | =V10 | active |
| [P16] | doi:10.58680/ccc198115885 | Flower, L. & Hayes, J. R. — A Cognitive Process Theory of Writing | College Composition and Communication 32(4):365, 1981 | <https://doi.org/10.58680/ccc198115885> | 執筆の認知プロセス（planning/translating/reviewing）＝停滞の工程構造（課題種別の停滞接地） | — | active |
| [P17] | isbn:978-0-521-33700-2 | Scardamalia, M. & Bereiter, C. — Knowledge Telling and Knowledge Transforming in Written Composition | in S. Rosenberg (Ed.), Advances in Applied Psycholinguistics Vol.2, pp.142–175, Cambridge Univ. Press, 1987 | — | 課題種別→停滞の質（論述=knowledge-transforming=高負荷 vs 物語/通信文=knowledge-telling=低負荷） | — | active |
| [P18] | doi:10.1037/0278-7393.14.3.355 | Kellogg, R. T. — Attentional Overload and Writing Performance: Effects of Rough Draft and Outline Strategies | J. Exp. Psychol. Learn. Mem. Cogn. 14(3):355, 1988 | — | 停滞=作業記憶過負荷（課題要求でその大きさが変動）の実証的接地 | — | provisional |
| [P19] | doi:10.1016/S0065-2601(06)38002-1 | Gollwitzer, P. M. & Sheeran, P. — Implementation Intentions and Goal Achievement: A Meta-Analysis of Effects and Processes | Adv. Exp. Soc. Psychol. 38:69–119, 2006 | <https://doi.org/10.1016/S0065-2601(06)38002-1> | 実行意図の古典的メタ分析。⚠️ **効果量 d=0.65 は [P21]（642テスト・2024/2025）に上書きされた**（本 d=.65 主張は 2026-07-23 の検証で 0-3 否決）。**効果量の引用は [P21] を使うこと**。本項は歴史的位置づけとして保持 | →P21 | superseded |
| [P20] | doi:10.1145/3698205.3729547 | Learning@Scale 2025 — メタ認知プロンプトの事前登録 RCT（N=1,005、null） | Proc. L@S '25, 2025 | <https://doi.org/10.1145/3698205.3729547> | プロンプト単体は不活性でありうる＝効果はユーザーの目標整合に依存（活性化が介入の前提条件） | — | provisional |
| [P21] | doi:10.1080/10463283.2024.2334563 | Sheeran, P., Listrom, O. & Gollwitzer, P. M. — The Effects of Implementation Intentions on Goal Attainment: A Meta-Analysis of 642 Tests | European Review of Social Psychology 36(1):162–194, 2024/2025 | <https://doi.org/10.1080/10463283.2024.2334563> | **実行意図の効果量 SSOT**。素の d=.36 [.33,.40] → 出版バイアス補正後 RoBMA d=.15 [.08,.22]（tau=0.27）。contingent d=.43 > schedule d=.29、記録すると d=.31 vs .44、詳細化で .46→.24、リハーサル有効 .45 vs .33＝活性化 UI の設計制約 | ←P19 | active |
| [P22] | doi:10.1037/a0015984 | Armitage, C. J. — Effectiveness of Experimenter-Provided and Self-Generated Implementation Intentions to Reduce Alcohol Consumption | Health Psychology 28(5):545–553, 2009 | <https://doi.org/10.1037/a0015984> | テンプレ選択式でも自由記述と有意差なし（p=.62）＝content-free 制約下の UI 選択の根拠。ただし等価性検定ではない（検証 2-1） | — | active |
| [P23] | doi:10.1111/dar.13553 | Cooke, R. et al. — Effectiveness of implementation intention interventions to reduce alcohol consumption: meta-analysis | Drug and Alcohol Review, 2023 (PMID 36173203) | <https://doi.org/10.1111/dar.13553> | オンライン配信サブグループ d+=-0.04 [-0.14,0.06]・大学生 d+=-0.04＝GSE が置かれる配信様式での null（境界条件） | — | active |
| [P24] | url:jmir-mhealth-2025-e65260 | Ahmadyar, S., Szypula, J., Bogosian, A. & Tapper, K. — 実行意図 vs 実務的 tips の要因実験（n=169、2週間日次アドヒアランス） | JMIR Mhealth Uhealth 13:e65260, 2025 (PMC12334108) | <https://mhealth.jmir.org/2025/1/e65260> | 能動統制に対し上乗せなし（71% vs 72%, P=.73）＝独立 null。⚠️ DOI 未確定のため URL キーで登録（provisional）。同論文のモデレーション主張（P=.04）は 0-3 否決につき引用禁止 | — | provisional |
| [P25] | doi:10.1177/0146167204271308 | Sheeran, P., Webb, T. L. & Gollwitzer, P. M. — The Interplay Between Goal Intentions and Implementation Intentions | Pers. Soc. Psychol. Bull. 31(1):87–98, 2005 (PMID 15574664) | <https://doi.org/10.1177/0146167204271308> | 効果は強く活性化した目標意図に条件づけられる＝**実行意図は動機を作らない**（活性化 UI の適用限界） | — | active |
| [P26] | doi:10.1037/0022-3514.83.1.231 | Koestner, R., Lekes, N., Powers, T. A. & Chicoine, E. — Attaining Personal Goals: Self-Concordance Plus Implementation Intentions | J. Pers. Soc. Psychol. 83(1):231–244, 2002 (PMID 12088128) | <https://doi.org/10.1037/0022-3514.83.1.231> | 個人プロジェクトでは実行意図の主効果ゼロ・self-concordance との交互作用のみ＝需要が薄い層では効かない | — | active |

## V 名前空間 — 検証方法論（ユーザー検証 v0.4 書誌）

| [n] | key | 著者・タイトル | 出典・年 | URL | GSE 検証での接地 | 重複 | 状態 |
|---|---|---|---|---|---|---|---|
| [V1] | arXiv:1508.03725 | Pejovic, V. et al. — Mobile-Based Experience Sampling for Behaviour Research | arXiv:1508.03725, 2015 | <https://arxiv.org/abs/1508.03725> | ESM/プローブ方法論・較正長期化リスク | — | active |
| [V2] | arXiv:2508.02817 | Sahu, N. K. et al. — Real-World Receptivity to Adaptive Mental Health Interventions: Findings from an In-the-Wild Study | arXiv:2508.02817, 2025 | <https://arxiv.org/abs/2508.02817> | Opportunity（受容性） | — | active |
| [V3] | arXiv:2506.03054 | Dziak, J. J. & Nahum-Shani, I. — Constructing Evidence-Based Tailoring Variables for Adaptive Interventions | arXiv:2506.03054, 2025 | <https://arxiv.org/abs/2506.03054> | X2 tailoring 変数の構築 | — | active |
| [V4] | arXiv:2107.03544 | Qian, T. et al. — The Micro-Randomized Trial for Developing Digital Interventions | arXiv:2107.03544, 2021 | <https://arxiv.org/abs/2107.03544> | Phase 3 MRT 設計（介入機会の因果評価） | — | active |
| [V5] | arXiv:2601.17753 | Crotti, R. et al. — Hylog: A Hybrid Approach to Logging Text Production in Non-alphabetic Scripts | arXiv:2601.17753, 2026 | <https://arxiv.org/abs/2601.17753> | 日本語 IME ログ健全性（本文非保存） | — | active |
| [V6] | arXiv:2511.12468 | Mehta, A. et al. — Detecting LLM-Assisted Academic Dishonesty using Keystroke Dynamics | arXiv:2511.12468, 2025 | <https://arxiv.org/abs/2511.12468> | AI 支援混入の補助指標 | =P11 | active |
| [V7] | arXiv:2603.00177 | Condrey, D. — Detecting Cognitive Signatures in Typing Behavior for Non-Intrusive Authorship Verification | arXiv:2603.00177, 2026 | <https://arxiv.org/abs/2603.00177> | キーストロークの個人識別性→プライバシー | — | active |
| [V8] | doi:10.1037/a0036577 | Oppezzo, M. & Schwartz, D. L. — Give your ideas some legs | J. Exp. Psychol. LMC 40(4):1142, 2014 | <https://doi.org/10.1037/a0036577> | Physical Anchor 効果の根拠 | =P8 | active |
| [V9] | doi:10.1073/pnas.1510459112 | Bratman, G. N. et al. — Nature experience reduces rumination... | PNAS 112(28):8567, 2015 | <https://doi.org/10.1073/pnas.1510459112> | Physical Anchor 効果の根拠 | =P2 | active |
| [V10] | url:fu-berlin-gse-scale | Schwarzer, R. & Jerusalem, M. — Generalized Self-Efficacy Scale | NFER-NELSON, 1995 | <http://userpage.fu-berlin.de/~health/selfscal.htm> | 自己効力感 副指標 | =P15 | active |
| [V11] | url:nasa-tlx | Hart, S. G. & Staveland, L. E. — Development of NASA-TLX | NASA Task Load Index, 1988 | <https://humansystems.arc.nasa.gov/groups/TLX/> | 作業負荷（NASA-TLX short・副指標） | — | active |
| [V12] | doi:10.1016/0272-4944(95)90001-2 | Kaplan, S. — The restorative benefits of nature | J. Environ. Psychol. 15(3):169, 1995 | <https://doi.org/10.1016/0272-4944(95)90001-2> | Physical Anchor（ART） | =P10 | active |
| [V13] | doi:10.2196/59247 | Park, J. H. — Discriminant Power of Smartphone-Derived Keystroke Dynamics for MCI | JMIR 26:e59247, 2024 | <https://doi.org/10.2196/59247> | キーストローク→認知プロキシ妥当性 | =P7 | active |
| [V14] | arXiv:1805.07793 | Anderson, C. et al. — Assessment of Social Roles for Interruption Management | arXiv:1805.07793, 2018 | <https://arxiv.org/abs/1805.07793> | 割り込み可能性（interruptibility）/ Opportunity | — | active |
| [V15] | url:google-workspace-security | Google Workspace Help — How Google protects your organization's security and privacy | Google | <https://support.google.com/a/answer/60762?hl=en> | Form↔ログのデータ分離・運用 | — | active |
| [V16] | url:dropbox-file-request | Dropbox Help — How to create and manage Dropbox file requests | Dropbox | <https://help.dropbox.com/share/create-file-request> | ログ提出（File Request）運用 | — | active |
| [V17] | url:dropbox-security | Dropbox Help — Dropbox account safety / how security works | Dropbox | <https://help.dropbox.com/security/how-security-works> | 暗号化・ゼロ知識保管の限界→ローカル暗号 | — | active |
| [V18] | lit:larson-csik-1983-esm | Larson, R. & Csikszentmihalyi, M. — The Experience Sampling Method | New Directions for Methodology of Social & Behavioral Science 15:41–56, 1983 (reprint: Springer 2014, doi:10.1007/978-94-017-9088-8_2) | <https://doi.org/10.1007/978-94-017-9088-8_2> | ESM 原典・signal/interval/event-contingent。L0 較正プローブの measurement independence 一次根拠 | — | active |
| [V19] | isbn:978-1-4129-2557-0 | Hektner, J. M., Schmidt, J. A. & Csikszentmihalyi, M. — Experience Sampling Method: Measuring the Quality of Everyday Life | Sage, 2007 | <https://methods.sagepub.com/book/mono/experience-sampling-method/toc> | ESM logistics・stratified/block 型信号がクラスタ回避の標準＝同次 Poisson 是正の裏付け | — | active |
| [V20] | doi:10.1145/985692.985727 | Adamczyk, P. D. & Bailey, B. P. — If not now, when? The effects of interruption at different moments within task execution | CHI '04, pp.271–278, 2004 | <https://doi.org/10.1145/985692.985727> | 割り込みタイミング・breakpoint＝L2' Opportunity（介入機会）合わせ | — | active |
| [V21] | doi:10.1145/1357054.1357070 | Iqbal, S. T. & Bailey, B. P. — Effects of intelligent notification management on users and their tasks | CHI '08, pp.93–102, 2008 | <https://doi.org/10.1145/1357054.1357070> | defer-to-breakpoint 通知＝L2' 介入最適化（無偏測定とは逆向き） | — | active |
| [V22] | doi:10.1145/3130956 | Pielot, M. et al. — Beyond Interruptibility: Predicting Opportune Moments to Engage Mobile Phone Users | Proc. ACM IMWUT 1(3):91, 2017 | <https://doi.org/10.1145/3130956> | opportune moment／engagement 予測＝L2' 受容性最大化（較正に流用すると独立性汚染） | — | active |
| [V23] | doi:10.1145/2858036.2858566 | Mehrotra, A. et al. — My Phone and Me: Understanding People's Receptivity to Mobile Notifications | CHI '16, pp.1021–1032, 2016 | <https://doi.org/10.1145/2858036.2858566> | 受容性・心理特性要因。重要な内容の通知すら disruption を生む＝介入侵襲のトレードオフ | — | active |
| [V24] | doi:10.1145/3123988 | van Berkel, N., Ferreira, D. & Kostakos, V. — The Experience Sampling Method on Mobile Devices | ACM Comput. Surv. 50(6):93, pp.1–40, 2017 | <https://doi.org/10.1145/3123988> | モバイル ESM の決定版サーベイ。signal/interval/event-contingent の設計トレードオフ＝較正サンプリング設計の一次根拠 | — | active |
| [V25] | doi:10.1177/10731911211067538 | Wrzus, C. & Neubauer, A. B. — Ecological Momentary Assessment: A Meta-Analysis on Designs, Samples, and Compliance Across Research Fields | Assessment 30(3):825–846, 2023 | <https://doi.org/10.1177/10731911211067538> | EMA メタ分析 k=477。標準=6/日×7日、compliance 平均79.2%、総回数は compliance/dropout と無相関＝較正密度設計の数値根拠 | — | active |
| [V26] | doi:10.1111/add.14503 | Jones, A. et al. — Compliance with ecological momentary assessment protocols in substance users: a meta-analysis | Addiction 114(4):609–619, 2019 | <https://doi.org/10.1111/add.14503> | EMA compliance メタ分析 ≈75.1%（80%閾値未達が常態）。頻度/期間と compliance 無相関＝[V25] 補強 | — | active |
| [V27] | doi:10.1007/s10869-022-09803-5 | Lafit, G. et al. — Optimizing Measurement Reliability in Within-Person Research: Guidelines for Research Design and R Shiny Web Application Tools | J. Bus. Psychol., 2022（online 2021） | <https://doi.org/10.1007/s10869-022-09803-5> | within-person 信頼性は測定機会数 T の関数。短尺は多数機会要＝GATE2 ≥20 の妥当性検証（信頼性理想は ~70–100） | — | active |
| [V28] | doi:10.1177/0741932512452794 | Kratochwill, T. R. et al. — Single-Case Intervention Research Design Standards | Remedial & Special Education 34(1):26–38, 2013 | <https://doi.org/10.1177/0741932512452794> | 単一事例/N-of-1 設計標準。効果実証に ≥3 回・各 phase ≥5–6 データ点＝個人内サンプルサイズ下限 | — | active |
| [V29] | doi:10.1145/2628363.2628364 | Pielot, M., Church, K. & de Oliveira, R. — An In-Situ Study of Mobile Phone Notifications | MobileHCI '14, pp.233–242, 2014 | <https://doi.org/10.1145/2628363.2628364> | 通知 63.5件/日・通知量↑→負の感情↑。通知/提出摩擦＝負担の実証（T2/T4 裏付け） | — | active |
| [V30] | url:cmu-ml-18-104 | CMU-ML-18-104 — Keystroke dynamics によるストレスの個人内分類（PhD thesis） | Carnegie Mellon Univ. Machine Learning Dept., 2018 | <https://reports-archive.adm.cs.cmu.edu/anon/ml2018/CMU-ML-18-104.pdf> | 個人内分類 89.5% vs 被験者横断 <60%・universal marker 不在（116名）＝within-person 較正必須の一次根拠。per-user 較正コスト＝採用摩擦の裏付け | — | provisional |
| [V31] | doi:10.1177/0741088313491692 | Leijten, M. & Van Waes, L. — Keystroke Logging in Writing Research: Using Inputlog to Analyze and Visualize Writing Processes | Written Communication 30(3):358–392, 2013 | <https://doi.org/10.1177/0741088313491692> | ポーズ長のテキスト単位階層（語内<語間<文間<段落間）＝ポーズ「位置」分類の方法論。本文非保存で移植可能 | — | provisional |
| [V32] | doi:10.1017/S0272263119000263 | Révész, A. et al. — Investigating the Relationship of Task Complexity, Cognitive Processes, and L2 Writing | Studies in Second Language Acquisition, 2019 | <https://doi.org/10.1017/S0272263119000263> | 論述課題での keystroke+視線+刺激再生の三角測量。文間ポーズ=planning / 語内ポーズ=transcription＝停滞の質の弁別根拠 | — | provisional |
| [V33] | doi:10.1073/pnas.2213114120 | Grüning, D. J. et al. — Directing smartphone use through the self-nudge app one sec | PNAS 120(8):e2213114120, 2023 | <https://doi.org/10.1073/pnas.2213114120> | 10秒 friction+意図表示で 36% 断念・試行自体 37% 減、habituation 耐性。self-nudge（自己導入）フレーミングの受容性根拠。⚠️ **2 ラウンド連続で検証を通過しておらず独立再現も未確認**＝GSE の差別化仮説の中核でありながら根拠は未固定 | — | provisional |
| [V34] | doi:10.1145/2858036.2858428 | Kim, Y.-H., Jeon, J. H., Choe, E. K., Lee, B., Kim, K. & Seo, J. — TimeAware: Leveraging Framing Effects to Enhance Personal Productivity | CHI '16, pp.272–283, 2016 | <https://doi.org/10.1145/2858036.2858428> | 自己追跡フィードバックはネガティブ枠のみ有効（0.634）・**撤去2週で効果消失**（IV→WD -0.473, p=.003）＝継続利用の主柱にできない根拠。N=24 で PF の null は検出力不足 | — | active |
| [V35] | doi:10.1145/3613904.3642469 | Hu, Y. & Lee, S. W. — （タイムラプス自己内省による生産性フィードバックの比較実験） | CHI '24, 2024 | <https://doi.org/10.1145/3613904.3642469> | 豊かな文脈的フィードバックでも**客観生産性は動かず**（62.6 vs 64.8, F(1,297)=1.58 n.s.）主観のみ上昇＝自己追跡の効果は知覚に偏る。N=15 で検出力不足 | — | active |
| [V36] | doi:10.1371/journal.pone.0245066 | Aeon, B., Faber, A. & Panaccio, A. — Does time management work? A meta-analysis | PLOS ONE 16(1):e0245066, 2021 | <https://doi.org/10.1371/journal.pone.0245066> | 158研究・490効果量。⚠️ **大半が横断研究**でフォローアップ・継続利用アウトカムを報告せず＝novelty effect 減衰と retention の判定材料にならない（スコープ否定）。r≈.25 上限主張とウェルビーイング優位主張は 0-3 否決につき引用禁止 | — | active |

---

## 重複文献（名前空間横断）

同一文献が両書誌に現れるもの（恒久 ID は両方維持、内容は同一）:

| 文献 | P | V |
|---|---|---|
| Oppezzo & Schwartz 2014 | [P8] | [V8] |
| Bratman et al. 2015 | [P2] | [V9] |
| Kaplan 1995 | [P10] | [V12] |
| Schwarzer & Jerusalem 1995 | [P15] | [V10] |
| Mehta et al. 2025 | [P11] | [V6] |
| Park 2024 | [P7] | [V13] |

→ 一意な文献数 = 26 + 36 − 6 = **56**（V18–V23 を 2026-06-28 の probe-timing/interruptibility サーベイで、V24–V29 を同日の calibration sampling density/yield サーベイで追加、
P19–P20 / V30–V33 を 2026-07-23 に介入コンテンツ×文脈シグナル×ML サーヴェイ
`docs/literature/20260703-intervention-content-and-ml-grounding.md` から追加。P との重複なし）。

> ⚠️ **P21–P26 / V34–V36 は 2026-07-23 の deep-research サーヴェイ第1ラウンド
> （`docs/literature/20260723-activation-layer-and-self-tracking-evidence.md`）で追加**。
> いずれも 3 票の敵対的検証を通過した主張に基づき、一次ソース本文で数値を逐語照合済みのため `active`
> （[P24] のみ DOI 未確定で `provisional`）。
>
> ⚠️ **[P19] は `superseded`**: d=0.65 という効果量主張が同ラウンドで 0-3 否決された。
> **実行意図の効果量を引くときは必ず [P21]（d=.36 素・補正後 d=.15）を使うこと**。
> 番号は citation-ssot 規約により再利用せず、行も残す。
>
> ⚠️ **P19–P20 / V30–V33 は `provisional`**: 出典は上記サーヴェイカード経由であり、**原論文の直接確認前**である
> （サーヴェイ自体が adversarial verify 通過を Card1/Card2 の 5 主張のみと明示している）。
> 効果量を設計判断の一次根拠に使う前に原論文を確認し、`active` へ昇格させること。
> 同サーヴェイの残り 17 件は**登録候補のまま**（研究者確認待ち。カード末尾の候補表を参照）。

## 追加・撤回ルール

1. 新規文献は該当名前空間の末尾に次番号で追加する（既存番号を振り直さない）。
2. 撤回時は行を残し「状態」を tombstone にする。番号は再利用しない。
3. 同一文献の二重登録は key 列（DOI / arXiv ID / 正規化 URL）で検出して防ぐ。
4. 両書誌に既出の文献は「重複」列で相互リンクし、片方を tombstone 化しない。

> 注: web 検索で暫定登録していた Csikszentmihalyi / Epp / Lau / 疲労バイオマーカー等は、
> **研究者本人の書誌に含まれないため除外**した（Flow 状態語彙は P14 Raichle 等で別途接地）。
> 必要なら citation-ssot 経由で P/V いずれかの名前空間に append する。
