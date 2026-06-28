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

→ 一意な文献数 = 15 + 17 − 6 = **26**。

## 追加・撤回ルール

1. 新規文献は該当名前空間の末尾に次番号で追加する（既存番号を振り直さない）。
2. 撤回時は行を残し「状態」を tombstone にする。番号は再利用しない。
3. 同一文献の二重登録は key 列（DOI / arXiv ID / 正規化 URL）で検出して防ぐ。
4. 両書誌に既出の文献は「重複」列で相互リンクし、片方を tombstone 化しない。

> 注: web 検索で暫定登録していた Csikszentmihalyi / Epp / Lau / 疲労バイオマーカー等は、
> **研究者本人の書誌に含まれないため除外**した（Flow 状態語彙は P14 Raichle 等で別途接地）。
> 必要なら citation-ssot 経由で P/V いずれかの名前空間に append する。
