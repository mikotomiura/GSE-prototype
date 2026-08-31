# サーヴェイ結果 — 「認知リソースの消耗」と「生成AIワークの負荷」

- **実施**: 2026-08-30（サブエージェント並列）
- **状態**: RQ-A（AI ワークの認知負荷・角度 2）と **RQ-D（ego depletion 再現性）は完走**。
  RQ-B（レビュー追従の破綻）/ RQ-C（スクリーン離脱の回復）は**セッションのレート制限で中断 → 再実施**。
- **扱い**: ★ 本ファイルはサーヴェイの生の持ち帰り。`docs/references.md` への登録は**別途メインが直列で**行う。

---

## 結論 1（最重要）: 「認知リソースを一方向に消耗させる」は **書けない**

研究者の当初案の文言 —— 「長時間の没入は認知リソースを**一方向に消耗**させる」——
は、**ego depletion の限定資源モデルそのもの**であり、**2026 年時点で擁護できない**。

### 一次証拠（すべて事前登録・大規模）

| 研究 | 設計 | 結果 |
|---|---|---|
| Hagger et al. (2016) *Perspect. Psychol. Sci.* 11(4):546–573, DOI 10.1177/1745691616652873 | **RRR・事前登録・k=23 lab・N=2,141**（★ プロトコルは **Baumeister 本人が事前に承認**） | **d = 0.04, 95% CI [−0.07, 0.15]** |
| Vohs et al. (2021) *Psychol. Sci.* 32(10):1566–1581, DOI 10.1177/0956797621989733 | **事前登録・k=36 lab・N=3,531** | **d = 0.06, 95% CI [−0.02, 0.14]**。ベイズは **帰無仮説を 4 倍支持** |
| Carter et al. (2015) *JEP: General* 144(4):796–815, DOI 10.1037/xge0000083 | 116 独立効果量・バイアス補正メタ分析 | naive g=0.43 → **PEESE b = 0.003, 95% CI [−0.14, 0.15]** |
| Hagger et al. (2010) *Psychol. Bull.* 136(4):495–525 | 危機前ベンチマーク・198 検定・**公刊のみ** | d = 0.62 [0.57, 0.67] |

**決定打（Vohs 2021）**: **操作は成功していた** —— 努力感の効果量 **d = 1.76, 95% CI [1.66, 1.86], I² = 0%**。
★ つまり「消耗させられなかった」のではなく、**「消耗 → 成績低下」の連結が無い**。

**生理的候補も消えた**:
- Vadillo, Gold & Osman (2016) *Psychol. Sci.* 27(9):1207–1214 — グルコースモデルの p-curve。逐語:
  *"researchers and policymakers should refrain from drawing any conclusions about the role of glucose in self-control."*
- Finley, Tang & **Schmeichel** (2019) *Social Psychology* 50(5–6):322–331 — 逐語:
  *"We found no evidence that blood glucose levels influence or are influenced by self-control."*
  （★ **Schmeichel は depletion の創始世代**。自陣営の生理的候補を自ら否定している）

**逆向きの所見**: Carter et al. (2015) —— **消耗タスクを多く行った方が後続成績が良い**（限定資源モデルの予測と逆）。

**中立の審判（これが引用すべき温度）**:
Friese, Loschelder, Gieseler, Frankenbach & Inzlicht (2019) *Pers. Soc. Psychol. Rev.* 23(2):107–131,
DOI 10.1177/1088868318762183 — 逐語:
> "We conclude that despite several hundred published studies, the available evidence is **inconclusive**."

⚠️★★★ **Hagger et al. (2010) の d = 0.62 を単独で引くと、この文献を知る査読者には無知か不誠実に映る。**

### 生き残っている効果（小さい・形が違う）

| 研究 | 内容 |
|---|---|
| Dang et al. (2021) *Soc. Psychol. Personal. Sci.* 12(1):14–24, DOI 10.1177/1948550619887702 | **事前登録・12 lab・N=1,775**。逐語 *"a small and significant ego depletion effect, **d = 0.10**. After excluding participants who might have responded randomly… **d = 0.16**."* |
| **Lin, Saunders, Friese, Evans & Inzlicht (2020)** *Psychol. Sci.* 31(5):531–547, DOI 10.1177/0956797620904990 | ★★★ **事前登録 4 実験・N=686・拡散モデル**。逐語 *"the high-demand manipulation reduced **boundary** but not **drift rate**… effort exertion reduced **response caution** rather than inhibitory control, suggesting that after exerting effort, people **disengage and become uninterested in exerting further effort**."* |
| Wiehler et al. (2022) *Current Biology* 32(16):3564–3575.e5, DOI 10.1016/j.cub.2022.07.010 | ★ 唯一の資源“らしい”生存者。⚠️ ただし **燃料の枯渇ではなく副産物（グルタミン酸）の蓄積**。単一施設・未追試 |

### 理論の乗り換え先（一次逐語つき）

- **Kurzban, Duckworth, Kable & Myers (2013)** *BBS* 36(6):661–679, DOI 10.1017/S0140525X12003196 —
  逐語 *"the sensation of 'mental effort' is the output of mechanisms designed to measure the **opportunity costs** of engaging in the current mental task"*、
  および ★★★ **"finite but not destroyed with use"**（＝ 各瞬間には有限だが、使っても不可逆に減らない）
- **Agrawal, Mattar, Cohen & Daw (2022)** *Psychol. Rev.* 129(3):564–585, DOI 10.1037/rev0000309 — 逐語
  *"…the phenomenological counterparts of these opportunity cost measures, **instead of reflecting the depletion of resources as has often been assumed.**"*
- Matthews et al. (2023) *Cognition* 240:105603 — 逐語 *"fatigue **fluctuates** from trial-to-trial"*（★ 単調減衰ではない）

### ★★★ GSE にとっての含意（戦略的にも重要）

> **資源枠組みは GSE にとって *技術的にも* 不利である。**
> 限定資源モデルは**単調な減衰**を予測するが、それは観測されない。
> 生き残った説明が予測するのは **変動し・文脈依存で・可逆な「関与の低下」**であり、
> ★ **30 秒ローリングウィンドウで実作業を見る GSE が実際に検出できるのはまさにそれである。**

**採用すべき言い換え（証拠の強さ順）**:

- ★★★ **推奨（打鍵動態と直結する）**:
  「demanding な作業を続けたあとに確実に変わるのは**処理能力ではなく、投資を続ける意思**である。
  人は決定閾値を下げて**関与から降りる**一方、処理速度や抑制制御はおおむね保たれる」
  → Lin et al. (2020)。★ **`p_stuck` / バックスペース / 逡巡といった打鍵特徴量に直接写る。**
- 「持続的な努力は固定的なプールを消費するのではなく、**続けることの主観的な費用対効果を押し上げる**」
  → Kurzban et al. (2013) / Agrawal et al. (2022)

---

## 結論 2: 「生成AIワークは通常のスクリーンワークより消耗が激しい」も **そのままでは書けない**

★ 文献は 3 つの山に割れており、**混同されて引用されている**。

### 山 (a) AI を *使うこと* 由来の負荷 —— 薄い。しかも方向が逆のものがある

| 研究 | 設計 | 結果 |
|---|---|---|
| **Burelli et al. (2026)** arXiv:2606.20598（*EMSE* 投稿中） | ★ **N=60・被験者内クロスオーバー・事前登録・EEG/視線/EDA/HRV** | ⚠️★★★ **AI 支援下で EEG θ/α 比が *低下*（β = −1.11, p_BH = .01）**。逐語 *"consistent with **reduced cognitive engagement** when developers **offload generative effort** to the model."* ⚠️ 周辺 R² < 0.10 |
| **Lee et al. (2025)** CHI 2025, DOI 10.1145/3706598.3713778 | N=319 ナレッジワーカー・936 事例・横断自己申告 | ⚠️ タイトルからして **"Self-Reported ***Reductions*** in Cognitive Effort"**。逐語 *"GenAI **shifts the nature of critical thinking toward information verification, response integration, and task stewardship**."* |
| Feng, Afroz & Sarma (2026) arXiv:2510.07435（ICSE-SEIS '26 採択） | N=442 OSS 開発者・**横断**・PLS-SEM | 逐語 *"GenAI adoption heightens burnout by increasing job demands"*。⚠️★★★ **バーンアウト構成概念に「雇用不安」を指標として混ぜている**（＝山 (a) と (b) が潜在変数の中で混線）。著者自身 *"associations… rather than causal relationships"* |

### 山 (b) AI に *置き換えられる不安* —— 「AI で疲れる」引用の大半はこれ。**道具の使用を測っていない**

Brougham & Haar (2018) の "AI awareness" 尺度（項目は逐語「自分の仕事が AI に置き換わると思う」）。
⚠️ **これを「AI を使うと疲れる」の根拠に使うのはカテゴリーエラー。**

### 山 (c) ★★★ 因果的に最も強い証拠は「AI が消耗を *下げる*」側にある

| 研究 | 設計 | 結果 |
|---|---|---|
| **Afshar et al. (2025)** *NEJM AI* 2(12), DOI 10.1056/AIoa2500945, **NCT06517082** | ★★★ **24 週・stepped-wedge・個人無作為化・実用的 RCT・N=66・ITT** | **work exhaustion −0.44, 95% CI [−0.62, −0.25], P < 0.001** |
| **Lukac et al. (2025)** medRxiv 2025.07.10.25331333, **NCT06792890** | ★ **3 群 RCT・N=238・真の対照群あり** | PFI 疲弊 **−0.27 [−0.48, −0.07], p = .01**。⚠️ **主要評価項目（文書時間）はほぼ null** |
| Brynjolfsson, Li & Raymond (2025) *QJE* 140(2):889–942 | 段階的導入・N=5,179 | 生産性 +15%、**離職 ~10pp 減**。⚠️ **疲弊尺度は未測定**。エージェント感情は **null** |

⚠️★★★ **これらを省くと文献の状態を誤って伝えることになる。**

### ★★★ したがって書ける最強の形（＝ GSE の問題設定とむしろ一致する）

> 生成 AI は認知的な仕事を **重くする** のではなく、**生成の努力を肩代わりして関与を下げ**、
> 残った努力を **検証（verification）** の側へ移す。

- 「関与が下がる」= Burelli et al. の EEG θ/α **低下**（事前登録・クロスオーバー）
- 「検証へ移る」= Lee et al. CHI 2025 の逐語
- ★ **これは GSE が狙い撃つ「答えをそのまま受け取ってしまうこと」そのものである。**
  → ★ **「消耗が激しいから休ませる」ではなく「関与が下がるから、関与が起きる余地を守る」**という論建てに変わる。

---

## 未検証・引用してはいけないもの（サブエージェントの明示的な警告）

1. GitHub Copilot の「60–75% がフラストレーション減」「88% 生産性向上」→ **ベンダー自己申告。査読なし**
2. Guglielmi et al. arXiv:2504.06808 → **登録報告（プロトコル）であり結果が存在しない**。結果があるかのように誤引用されている
3. Lee et al. CHI 2025 の作業別パーセンテージ（72%/79%/76%/55%）→ **本文未読・未検証**
4. Chuang et al. / Hai et al.（IJIM 2025）→ **abstract のみ。効果量未検証**
5. Dell'Acqua et al. "Jagged Technological Frontier" → **wellbeing 系アウトカムの有無を確認できず**

---

## 再実施が要るサーヴェイ（レート制限で中断）

- **RQ-B**: 「AI の出力速度に人間のレビューが追いつかない」——
  ★ 有力候補は **METR (2025-07-10)**（16 名・246 タスク RCT・実測 19% 遅い / 主観 20% 速い。
  ⚠️ **METR 自身が結果を historical と位置づけている**留保つき）と
  **Fan, Liu, Pan & Zhang "When Help Hurts" CHI 2026, DOI 10.1145/3772318.3791176**（N=60・honorable mention。
  ⚠️ ACM DL は 403 なので著者版を探す。⚠️ **同論文は AI で RAW-TLX が −18.2 ポイント下がったとも報告**）
- **RQ-C**: 「回復には *スクリーンから離れること自体* が要るか」——
  ⚠️ **結論 1 により、この RQ は前提から書き直しが要る**（「消耗の回復」ではなく「関与の再開」）

---

## 結論 3（RQ-C・2026-08-31 完走）: 「画面の外へ出ること自体に固有の効果」も **書けない**

### 判定の根拠 3 本

1. 媒体を単独で分離した唯一の実験は、**紙休憩と PC 画面休憩を区別できなかった**
   （Kang & Kurtzberg 2019, *J. Behav. Addict.* 8(3):395–403, DOI 10.1556/2006.8.2019.21。
   **N=414・無作為・4 条件・休憩内容を統制**。紙 vs PC 画面は消耗も成績も ns。害があったのは*スマホ*だけ）。
2. **事前登録 N=308 では、*画面上の*自然映像が画面外の安静を上回った**
   （Grobelny et al. 2024, *Sci. Rep.* 14:21603, DOI 10.1038/s41598-024-72825-x。
   補充 d: 自然（画面上）= 0.91 / SNS = 0.46。**自然のみ完全回復**）。
3. RQ が要求する実験 —— **画面内 vs 画面外の休憩を同一デザインで振り、*関与の再開* を測る** —— は**存在しない**。

### 書ける最強の形

> demanding な作業を続けたあとに低下するのは処理能力ではなく、**投資を続ける意思**である（Lin et al. 2020）。
> この低下は可逆で、**報酬を上げるだけで行動・P3・瞳孔径が揃って戻る**（Hopstaken et al. 2015,
> *Psychophysiology* 52(3):305–315 —— 逐語 *"After increasing the rewards, all measures reverted to higher levels."*）。
> **しかし「画面の外へ出ること」がこの再開を引き起こすという統制証拠は無い。**

⚠️ **使ってはいけない語**: 「回復」「消耗」「リソースの補充」——**すべて限定資源モデルの語彙**である。

---

## ★★★ 結論 4（想定外・最重要）: **ART（注意回復理論）は限定資源モデルそのものである**

⚠️★★★ **ego depletion と同じ穴に落ちる。** Stevenson et al. (2018) の abstract 冒頭・逐語:

> *"Attention Restoration Theory (ART) predicts exposure to natural environments may lead to improved
> cognitive performance through **restoration of a limited cognitive resource**, directed attention."*

そして **Kaplan & Berman (2010)** *Perspect. Psychol. Sci.* 5(1):43–57, DOI 10.1177/1745691609356784 は、
ART を **Baumeister の ego depletion に明示的に溶接している**（逐語で「大根実験」と
**Gailliot et al. のグルコース仮説**を根拠に挙げる）。
→ ★★★ **前ラウンドで両方とも死亡が確認済みである。**

### 事前登録された ART の検定は全滅

| 研究 | 結果 |
|---|---|
| **Stevenson et al. (2021)** *JEP* 77:101679（★ ART II の筆頭著者自身・事前登録 RCT・**薬物という陽性対照つき**） | *"In contrast to Taylor and Kuo's (2009) findings, **no improvements were found after exposure to nature**."* |
| **Hartanto et al. (2023)** *Exp. Psychol.* 70(2):96–107 | *"**Bayesian analyses further showed substantial support for the null hypothesis**"* |
| **Augustinova et al. (2022)** *JEP* 84:101901 | *"despite being appropriately powered… **Bayesian evidence against this reduction**"* |
| **Neilson et al. (2021)** *Human Factors* 63(6) | *"**The results failed to replicate Berto (2005)**"* ＋ 逐語で**未公刊の再現失敗を自白** |
| **McDonnell & Strayer (2024)** *Sci. Rep.* 14:1845（N=92・40 分の自然歩行 RCT・最も厳密な支持研究） | 実行制御 RT は **χ²=0.358, p = 0.549**。陽性は ERP 1 成分のみ（p=.034・非事前登録・未補正） |

★ 旗艦の **Berman, Jonides & Kaplan (2008)** 実験 2 は **N=12** で、**仮説の検定である交互作用が落ちている**
（逐語 *"The location-by-time interaction was **not reliable, F(1, 10) = 0.486**"*）。

→ ⚠️★★★ **ART は「殺された」のではなく「まともに検定されたことが一度も無い」。**
★ **未踏 2 文書は ART に寄りかかっていないので無傷**（2026-08-31 実測: 提案書に Kaplan/ART の言及ゼロ）。

---

## ⚠️ リポジトリ側の不整合（本タスクのスコープ外・要別タスク）

| # | 問題 | 実測 |
|---|---|---|
| 1 | **[P8] Oppezzo & Schwartz が `active` のまま、`research-positioning.md` の 6 箇所で現役引用**（L111 / L209 / L211 / L657 / L667 / L749）。うち L211 は逐語「**歩けば認知が回復する**」の理論根拠として引いている | ★ 未踏文書では取り下げ済みだが、**SSOT では取り下げられていない** |
| 2 | **[P10] Kaplan ART が「Physical Anchor の理論基盤」として引かれている**（L209） | ★ 結論 4 により**危険**。査読者の第一撃に無防備 |
| 3 | ⚠️★★★ **`research-positioning.md` が Lv2 Wall を *現行機能* として書いている**（L228 逐語「GSE の現行レパートリーは Lv1 Nudge（柔らかい）と **Lv2 Wall（硬い）**の二極に張り付いており」／ L597 / L602） | ★ **ADR-015 で削除済み**。SSOT が古い |
| 4 | [P166] Stevenson 2018 の「実環境 > 仮想環境 ＝ GSE に有利」という読み（L456） | ★ **同じ著者の事前登録 RCT (2021) が null**。そのまま出すと自傷 |

---

## ★ 予定外の収穫: GSE のセンシング方式そのものの先行研究

**de Jong, M., Bonvanie, A. M., Jolij, J. & Lorist, M. M. (2020)** "Dynamics in typewriting performance
reflect mental fatigue during real-life office work." *PLOS ONE* 15(10):e0239984,
DOI 10.1371/journal.pone.0239984（OA）。**実オフィスで 6 週間、打鍵動態から精神的疲労を検出。**

- 逐語: *"although office workers are entitled to have breaks during a working day,
  **the scheduled breaks might not have been enough to fully recover**"*
- 逐語（⚠️ GSE の偽陽性リスクを著者自身が名指ししている）:
  *"personalized real-time feedback based on changes in typing behavior could be provided…
  **However, real-time feedback might be biased due to dynamics in typewriting performance
  that are not related to lapses in performance.**"*

→ ★★★ **`docs/literature/` のカード化を強く推奨**（本タスクのスコープ外）。

---

## 査読者が最初に突く点（RQ-C エージェントの警告）

1. ★★★ 「**ART に依拠している時点で限定資源モデルを再輸入している**」
2. ★★★ 「**行動指標では一度も出ていない**」（最良の RCT で p = 0.549、事前登録は 5 本全部 null）
3. ★★ 「**システムが押し付けた休憩は、文献が示した機序を壊す**」
   —— 効くのは **preferred** な活動（Hunter & Wu 2016）／自律性が低い昼休みは**疲労を増やす**（Trougakos et al. 2014）／
   micro-break が効くのは **general work engagement が低い人だけ**（Kim et al. 2018）。
   → ★★★ **ADR-018（完了条件を課さない・本人が決める）は偶然この批判に耐える設計になっている。明示的にそう書くべき。**
4. 「**用量が 1〜2 桁足りない**」—— 最適は約 30 分（Bell et al. 2025）。40 秒 micro-break は**原著チーム自身が再現失敗**（F=0.06, p=.946）

---

## 結論 5（RQ-B・2026-08-31 完走）: 「レビューが追いつかない」は **条件付きで書ける**

### ⚠️★★★ METR の 19% を現在の事実として引いてはいけない

**METR 自身が 2026-02-24 に無効化している。**ブログ冒頭バナー逐語:

> "These results are out of date… **We believe these historical results no longer reflect the current
> impact of AI models on open-source developer productivity.**"

継続研究の逐語: *"Our early 2025 study found the use of AI causes tasks to take 19% longer,
**with a confidence interval between +2% and +39%**."* ／
*"we believe it is likely that developers are **more sped up** from AI tools now — in early 2026"* ／
新データは *"**unreliable signal**"* と本人が明記（選択バイアス・報酬が $150/h → $50/h）。
⚠️ 論文 arXiv:2507.09089 は **preprint（査読なし）**。

★ **維持されている部分だけを引く**:
> *"developers are **broadly well-calibrated on the relative amount of time** that issues will take,
> but **their expectations regarding the usefulness of AI assistance are reversed**."*

### ⚠️ Fan et al. CHI 2026「When Help Hurts」もタイトルに騙されてはいけない

一次 PDF 全文取得済み（CC-BY）。**主結果は「AI で負荷が *下がった*」である**:
**−18.2 TLX points, 95% CI [−22.3, −14.0], p < 0.001** ／ 時間 **×0.78** ／ 正答 **OR = 1.71**。

★ **GSE が使えるのは 2 点だけ**:

1. **検証負荷が疲労上昇を部分媒介する** —— Condition×Index **p = 0.041**、
   KSS の間接効果 **ab = 0.15 [0.06, 0.27]**（総効果の約 26%）。
   逐語 *"implicating **rework and error-cascade costs** rather than a generic 'AI effect.'"*
   ⚠️ 著者の留保 *"the design does not establish causal identification."*
2. ★★★ **「ほぼ無検証の受容」は正答率を下げる**（＝「検証を飛ばす」の唯一の量的一次証拠）——
   受容率の二次項 **β₂ = −0.81, SE = 0.28, p = 0.005**、最適点 **0.48 [0.44, 0.53]**。
   逐語 *"**very high acceptance (near-blind acceptance) were both associated with lower correctness**"*
   ⚠️ 著者は *"exploratory rather than prescriptive"* と留保。

### ★★★ 著者自身が GSE のアーキテクチャを提言している（位置づけに直結）

> *"A practical implication is to **monitor these behavioral signals directly and intervene when they
> exceed lightweight thresholds** (e.g., rising compile/test failures or prolonged time-to-first-compile),
> rather than assuming that more model output or more explanation will help. Where feasible,
> **micro-restorative strategies (short micro-breaks…) can reduce fatigue without harming throughput**"*

→ ★★★ **GSE はこの提言の実装である**と §3 に書ける。

### 訓練では直らない（＝実行時介入が要る根拠）

- **Parasuraman & Manzey (2010)** *Human Factors* 52(3):381–410 逐語:
  *"Automation bias occurs in both naive and expert participants, **cannot be prevented by training or instructions**"*
  ／ *"**the failure to verify (not attending to the raw data) indicates a reallocation of attention**"*
- **Skitka, Mosier & Burdick (1999)** *IJHCS* 51(5):991–1006 —— **統制実験 N=80・自動化なし対照群あり**。
  見落とし **41% vs 3%**（F(1,62)=44.32）。逐語 *"**even when it contradicted their training and other
  100% valid and available indicators**"* ／ ★ **「疑っていても検証行動は変わらない」**:
  *"even though participants on the whole did not feel the AMA was very reliable? Put simply, **the answer is yes**."*

### ★★★ 主観が追えないことの一次証拠（GSE の存在理由そのもの）

| 出典 | 数値 |
|---|---|
| **Parry et al. (2021)** *Nat. Hum. Behav.* 5(11):1535–1547（★ **事前登録メタ分析・106 効果量・N=52,007**） | 自己申告と実測ログの相関 **r = 0.38 [0.33, 0.42]**。ログ平均 ±5% に入った自己申告は **49 件中 3 件（6.12%）**。⚠️ **向きは決まらない** |
| **Murphy-Hill et al. (2021)** *IEEE TSE* 47(3):582–594（Google 内 **n = 3,344**） | 主観生産性 vs 客観出力の **R² < 3%** |
| **Deslauriers et al. (2019)** *PNAS* 116(39)（**無作為クロスオーバー RCT・N=149**） | 実感 **−0.56 SD** / 実測 **+0.46 SD**（p < 0.001）。★「流暢さが理解の実感を作る」最良の RCT |

### ⚠️ 反証側（省略不可）

- **Khojah et al. (2026)** ASE '26, arXiv:2606.26505 —— **N=32 実務者・視線計測・ベイズ**。
  逐語 *"**while the thoroughness of code review did not change** for participants, they **spent more time**
  fixating on LLM-labelled code"*。→ ★ **「乖離」は支持するが「精査の低下」は否定する。**
- **METR 2025 の定性データ** —— *"**75% report that they read every line of AI generated code**"*。
- **Sandoval et al. (2023)** USENIX Sec —— *"AI-assisted users produce critical security bugs at a rate
  **no greater than 10% more than the control**"*（⚠️ 非劣性検定の一方が p = 0.06）。
- **Melumad & Yun (2025)** *PNAS Nexus* 4(10):pgaf316（**n = 10,462・複数事前登録**）——
  ⚠️ **「本人が自覚していない」を否定**: *"participants **reported developing shallower knowledge**"*。
- **Peng et al. (2023)** arXiv:2302.06590 —— **乖離の向きが逆**（主観 35% / 実測 55.8% ＝ 過小評価）。

### ★★★ 書ける最強の形（提案書に貼れる）

> 自動化された出力を検証せずに受け入れる傾向は、専門家でも生じ、**訓練や明示的な検証指示では防げない**
> [Parasuraman & Manzey 2010; Skitka et al. 1999]。生成 AI 環境ではこの負荷が「生成」から「検証」へ移り
> [Lee et al. 2025]、**AI 提案をほぼ無検証で受け入れる帯域では正答率が実際に下がる**
> [Fan et al. 2026: β₂ = −0.81, p = 0.005]。ところが**当人の主観はこの過程を追えない**——
> 自己申告と実測ログの相関はメタ分析で **r = 0.38** [Parry et al. 2021, N=52,007]、
> 開発者の生産性実感と客観出力の共有分散は **3% 未満** [Murphy-Hill et al. 2021, n=3,344]。
> **したがって、AI 支援下で「検証が抜けていく過程」は自己申告では捉えられず、
> 作業中の行動そのものを常時計測する経路が要る。**

★★★ **最後の一文が GSE の存在理由そのものである。**

## ⛔ 引用禁止（RQ-B エージェントの名指し・追加分）

1. **METR arXiv:2507.09089 の 19% を現在の事実として** —— 著者自身が historical と宣言
2. **Kosmyna et al. "Your Brain on ChatGPT"** —— 本文冒頭に *"Preprint, under review"*
3. **Yu et al. arXiv:2606.22721** —— journal_ref なし・著者 5/7 が Independent Researcher・因果同定なし
4. ⛔⛔ **Alter et al. (2007) の disfluent font 効果** —— **死んでいる**。Meyer et al. (2015) *JEP:General*
   144(2) が **17 実験・N=7,367** で *"**no evidence of a disfluent font benefit under any conditions**"*。
   ★ **「摩擦が熟慮を起こす」を Alter で正当化してはいけない**
5. **Porter et al. (1998) を「検査速度が効く」証拠として** —— 逐語で
   *"did **not** significantly influence the defect detection rate"*（前提が逆）
6. **SmartBear/Cisco の「200 LOC/hour」** —— 出典なしの伝聞。自社データでは
   *"We found no metric that correlated significantly with inspection rate"*
7. **Fisher et al. (2015) を「主観と実測の乖離」の証拠として** —— **客観指標が 1 つも無い**
