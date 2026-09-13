# 停滞 onset の文献接地 と 日本語 IME 変換過程の公開データ

> 2026-09-13 / `/literature-review` 1 ラウンド / **検算ラウンド**（★ 探索ではなく、**既に本文で使っている主張の一次確認**）

## 動機（★ なぜこのラウンドを回したか）

★ 前セッションが **ADR-030**（`stall onset` / `Decision Episode` の操作的定義）を
**引用ゼロ件**で書き、⚠️ 研究者の指摘で後から接地し直した。
★ その是正で `Context-3b`（文献が既に否定していること）を足したが、
⚠️★★★ **`.idea/survey §13` の主要文献 33 件中 21 件が `docs/references.md` に未登録**であり、
★ **うち「強い反証」5 本のうち 3 本**が含まれていた（`.steering/20260913-mhd-inference-ssot/blockers.md` **起票 4**）。

★ 併せて **起票 5** —— `.idea §3.1`（「Translog-II は日本語ローマ字入力を `IME` として記録する」）と
`docs/references.md` **[P273]**（「IME の扱いは 1 語も書かれていない」＋ やり残し）が食い違っており、
⚠️ **どちらが一次確認済みかが確定できていなかった**。

## 検証状態

- **取得ソース**: 7 件（★ うち **全文到達 6 件** ／ **abstract のみ 1 件** ＝ [V148]）
  ＋ **公開生データ 1 件を実測**（[P360]・`P01_T1.xml` 10.2 MB を実際に grep）
- **claim 抽出**: **21 件** → **検証 21 件**
- **confirmed 13**（★ 3-0 が 8 / 2-1 が 5）／**否決 7**／**判定不能 1**
- **登録**: **[P357]–[P360]** / **[V146]–[V150]**（★ `provisional` 2 件 = **[V148]** / **[V150]**）

> ⚠️★★★ **初稿の集計（17 / 11 / 5 / 1）は合っていなかった**（★ `code-reviewer` MEDIUM 指摘・2026-09-13）。
> ★ **数値の忠実性を売りにしたラウンドで自分の集計が合わないのは効く**ので、**台帳を置いて数え直した**。

### ★ claim 台帳（★ 集計を検算できるようにする）

| # | claim | 出典 | 票 |
|---|---|---|---|
| 1 | 単一の沈黙閾値は**二群**（介入が要る／要らない）を分離できない（⚠️ **「計画中／詰まっている」は GSE 側の言い換え**・→ カード 1 の囲み） | [P357] | **2-1** |
| 2 | 54 特徴でも回帰は baseline を超えず、分類は最大 AUC=.57 | [P358] | **2-1** |
| 3 | 打鍵数ベースの分割が時間ベースより良い | [P358] | **2-1** |
| 4 | ラボで通った境界検出が実地で崩れる（★ **定性のみ**・→ 否決 3） | [V146] | **2-1** |
| 5 | 境界検出は「断片の検出」と「断片の結合」の 2 副問題に分かれる | [V146] | **2-1** |
| 6 | person-spell-period（★ spell ごとに period カウンタをリセット） | [V147] | **3-0** |
| 7 | 過去履歴は spell ダミー ＋ 直前 spell の持続時間（time-varying）で統制する | [V147] | **3-0** |
| 8 | spell **内**の期間従属も未解決である（★ 著者自身の言明） | [V147] | **3-0** |
| 9 | cause-specific hazard は当該 failure type の生存確率として直接解釈できない | [V148] | **3-0** |
| 10 | JITAI の構成要素は **4 つ**である | [V149] | **3-0** |
| 11 | JITAI は intervention-determined であり participant-determined ではない | [V149] | **3-0** |
| 12 | Translog-II は日本語 IME の変換過程を記録する（★ 論文 ＋ 生ログの二重確認） | [P359] [P360] | **3-0** |
| 13 | Translog-II は keydown のみ記録し keyup を記録しない（★ dwell time が取れない） | [P359] | **3-0** |
| 14–20 | ⚠️ **否決 7 件** → §否決リスト（1 / 2 / 3 / 4 / 5a / 5b / 6） | — | **1-2 が 1 / 0-3 が 6** |
| 21 | ⚠️ subdistribution hazard の**定義** | [V148] | **判定不能** |

## gate 判定（★ 下位問いごとに温度を分ける。⚠️ 平均化しない）

| # | 下位問い | 温度 | 1 行結論 |
|---|---|---|---|
| **Q-a** | **長い沈黙の意味は一方向か** | ★★★ **確定（否）** | **単一の沈黙閾値は二群（介入が要る／要らない）を分離できない** —— ★ 検出器を作った当人が明言 [P357]。⚠️ **「計画中／詰まっている」は GSE 側の言い換え**（→ カード 1 の囲み）。⚠️ **根拠にされてきた `r=.507` は弱い**（→ 否決 1） |
| **Q-b** | **打鍵過程特徴の性能天井はどこか** | ★ **確定（低い）** | 54 特徴でも**回帰は平均予測を超えず、分類は最大 AUC=.57** [P358]。⚠️ **ただし予測対象は「作品の成績」**（→ 否決 2） |
| **Q-c** | **ラボの性能は実地に持ち越せるか** | ★ **確定（崩れる）** | ラボの手法が実地で**過剰分割**へ崩れ、チューニングすると今度は**半数で検出ゼロ** [V146]。⚠️ **「80% → 76% 誤差」は別指標の並置**（→ 否決 3） |
| **Q-d** | **反復エピソード / 競合リスクの作法は何か** | ⚠️ **部分確定＋穴** | person-spell-period と過去履歴の統制は確定 [V147]。⚠️★★★ **`cluster-robust SE` の出典に [V147] は使えない**（→ 否決 4）。⚠️★★★ **「反復エピソード × 競合リスク」の同時作法は [V147] にも [V148] にも無い**（→ 起票） |
| **Q-e** | **Translog-II / ENJA15 は IME をどう記録するか** | ★★★ **確定（記録する）** | **`Type="IME"` の Key 事象 ＋ 確定 insert の `IMEtext` 属性**として記録する。★ **論文 [P359] と公開生ログ [P360] の二重確認**。→ ⚠️★★★ **`research-positioning.md` ／ [P273] ／ 未踏提出 2 文書の主張を 1 段下げた**（→ 否決 **5a**） |

---

## カード 1: 単一の沈黙閾値は二群を分離できない **[検証済 2-1]** [P357]

> ⚠️★★★ **見出しの「二群」は著者の語である。**★ 逐語は *"cannot distinguish between **two populations**"* で、
> その二群は *"may benefit from intervention"* / *"may not need intervention"*。
> → ★ **「計画中／詰まっている」への割り当ては GSE 側の *言い換え* であって、著者が名付けたものではない**
> （★ `code-reviewer` MEDIUM 指摘・2026-09-13）。⚠️ **「著者が明言した」と書けるのは *二群に割れて分離できない* までである。**

**1. それはどんなもの?**
米国州立大学の非 CS 専攻向け CS 入門科目で、iSnap（Snap! ブロックプログラミング）の
**2 週間オープンエンド中間プロジェクト**のトレースログから「苦闘の瞬間」を検出する 7 種の検出器を作り、
授業後アンケート（感情価・出来事）および成績と突き合わせた **CSEDM ワークショップ論文**。

**2. 先行研究と比べてどこがすごい?**
★ 「詰まり検出器」を**作って終わらない**。⚠️ **自分の検出器が分離に失敗していることを明示的に報告している。**

**3. 技術や手法の肝はどこ?**
★ `Overly Idle` 検出器の定義が逐語で
*"This detector identifies **the number of times** when there is a gap of **more than five minutes** between students' actions in iSnap."*
→ ⚠️★★★ **測っているのは「idle の長さ」ではなく「5 分超ギャップの *発生回数*」である。**

**4. どうやって有効だと検証した?**
**N=19** のコーディングトレース（12,262 アクション）× **Spearman 順位相関**。
`Overly Idle` × プロジェクト総合成績 = **ρ 0.5066, p=0.0269**（★ **正**の相関）。
負の感情側は valence 3 項目（*looked up how to do something* −0.5595 ／
*spent a long time looking for a simple error* −0.6299 ／ *felt unsure about what to work on* −0.6753）。

**5. 議論はあるか?**
⚠️★★★ **著者自身の結論が本カードの本体である**:
> *"In sum, this detector divides students into **two distinct groups**. … one portion of the population
> recognized by this detector may benefit from intervention, and the other portion may not need intervention.
> **In its current shape, this detector cannot distinguish between two populations**."*

⚠️ **留保（1 票）**: **N=19・多重比較補正なし**（Table 4 だけで約 40 検定 ＝ **Bonferroni なら落ちる**）。
★ 著者も *"this could lead to the multiple comparison problem"* と自認。
⚠️ 観測空間は**ブロック操作イベント**でありキーストロークではない。授業内 **2 コマ約 2 時間のみ**・ペア作業込み。
⚠️ 「5 分」に**文献的根拠は無い**（★ 専門家 4 名の示唆に基づく設定値・感度分析なし）。

**6. 次に読むべき論文は?**
★ Gorson & O'Rourke ／ Dong et al.（★ 「5 分」の由来として著者が挙げた 2 本）。

**★ やり残し**: ⚠️ **本論文は「二群に割れる」ことは示したが、二群を *分ける変数* を特定していない。**
★ ADR-030 が投資順序で `T1b`（境界）を先に置いた判断（[P121] 由来）は、
**この論文が空けた穴に対する仮説**であって、本論文が支持したものではない。

---

## カード 2: 打鍵過程特徴を 54 個積んでも、作品の質は平均予測を超えて当たらない **[検証済 2-1]** [P358]

**1. それはどんなもの?**
Inputlog で記録した **N=126** の 30 分学術サマリー課題から **54 個**の打鍵過程特徴
（pauses / revisions / typing bursts / verbosity / other）を作り、
**最終成績**を (a) 回帰、(b) 二値分類（合格ライン 5.5 未満 = "might need support"）で予測した **OA 論文**。

**2. 先行研究と比べてどこがすごい?**
★ **時点分割を 2 通り**（時間ベース 5 分刻み ／ **打鍵数ベース 1/6 刻み**）で回し、
⚠️ **どちらでも baseline を超えないことを正面から報告した**。

**3. 技術や手法の肝はどこ?**
★ baseline の置き方が明確 —— 回帰は**平均最終成績**、分類は**多数クラス**（52%）。
★ fold 内で feature reduction（nearZeroVar → findCorrelation(0.80) → RFE）を閉じている
（⚠️ **leakage を作っていない**）。

**4. どうやって有効だと検証した?**
> *"**None of the regression models outperformed the baseline**, and the classification models were only
> slightly better than the majority class baseline (**highest AUC = 0.57**)."*（Abstract）

★ AUC 0.57 は **打鍵数ベース分割 × SVM(radial)** の値。
> *"The support vector machine outperforms the baseline and all other models at every timepoint …
> However, **with an AUC of 0.57, these models still do not perform well**."*（p.853）

**5. 議論はあるか?**
⚠️★★★ **予測対象が「作品 (product) の成績」であってプロセス内状態ではない。**
→ ★ 「打鍵から最終成績を当てられない」は「**打鍵から停滞を検出できない**」を**含意しない**（→ 否決 2）。
⚠️ **留保（1 票）**: 被験者**間**の横断予測（1 人 1 セッション・個人内反復構造なし）／L2 学習者の統制課題／
特徴量は**先行研究からの借り物**で、著者自身「早期予測用に設計されていない」と limitation に書く。
→ ★ 引けるのは「**この特徴集合ではこの課題で拾えなかった**」まで。

**6. 次に読むべき論文は?**
★ Conijn et al. (2019) [既登録] ／ Conijn et al. (2021) revision detection（★ **未登録**）。

**★ やり残し** ⚠️★★★ **GSE の計器設計に直接効く所見が 1 つ出た**:
★ **打鍵数ベースの分割が時間ベースの分割より良かった**（★ 理由は「時間分割は最初/最後のセグメントに情報が乏しい」）。

⚠️★★★ **ただし GSE へはそのまま移らない（★ 一次＝コードで実測して初稿を訂正した）。**
★ `src-tauri/src/analysis/features.rs:102-104`:
```rust
let last_ts = self.buffer.back().unwrap().timestamp;
let cutoff = last_ts.saturating_sub(30_000);
```
★ 回帰テスト `tier0_key_counts_use_the_30s_window_ending_at_the_last_event`（`:670-681`）が逐語で固定:
「⚠️★★★ 窓の右端は **バッファ最後のイベント時刻**であって「今」ではない。
 cutoff = last_ts − 30_000 なので、**last_ts が古いままなら窓も古いまま動かない**。」

→ ★★★ **GSE の窓は「直近 30 秒」ではなく「*最後の活動から遡って* 30 秒」であり、
沈黙中は空にならず *凍結* する ＝ 時間ベースと打鍵数ベースの *中間* にある。**
⚠️ したがって **[P358] の機序（最初/最後のセグメントが薄い）は GSE では発生しない。**
★ **残る懸念は別のもの 2 つ**:
(a) **打鍵密度が違う区間で「30 秒」の意味が揃わない**、
(b) **凍結中は特徴ベクトルが古くなる**（★ ADR-030 **D3** が別途扱う）。
★ 単一研究の所見なので **ablation 対象**であって前提にしない（→ 起票 17）。

---

## カード 3: ラボで通った境界検出は、実地では過剰分割と検出ゼロへ崩れる **[検証済 2-1]** [V146]

> ⚠️★★★ **どこまでが生き残るのかを先に書く**（★ `code-reviewer` MEDIUM 指摘・2026-09-13）。
> ★ **可**: 「*別研究の* ラボ結果に対して、実地では崩れた」という **定性の対比**。
> ⚠️ **不可**: **数値の対比**（→ 否決 3。★ 81% と 76% は分母も定義も違う）。
> ⚠️ **「両極に振れる」は GSE 側の要約語**であって著者の語ではない（★ 逐語は 112 vs 21 と
> *"no tasks are detected in half of the 12 programmer days"* の 2 点。★ 「70% 以上は本文に存在しない」と
> 同じ厳しさを**自分の語にも当てる**）。

**1. それはどんなもの?**
Coman & Sillitti の自動タスク境界検出アルゴリズム（IDE 操作履歴の TIIA → 平滑化 → ピーク）を、
上海のソフト企業のプロ開発者 **6 名・1 か月**の実データへ適用した産業事例研究（ICSM 2012）。

**2. 先行研究と比べてどこがすごい?**
★ **他人のアルゴリズムを実地で落としてみせ、落ちた理由を診断している**（★ 追試の稀な形）。

**3. 技術や手法の肝はどこ?**
★ 失敗の**質**を分けている —— ベースラインパラメータでは **112 検出 vs 21 申告**（過剰分割）。
⚠️ チューニングすると今度は *"**no tasks are detected in half of the 12 programmer days**"*。
→ ★ **失敗の向きが 2 つある**（★ 「精度が下がる」ではない）。⚠️ **「両極に振れる」は GSE 側の要約語**（上の囲み）。

**4. どうやって有効だと検証した?**
> ラボ: *"the algorithm was able to correctly identify **9 out of the 11 tasks** … achieving a success rate of **81%**"*
> 実地: *"the total difference of number of tasks identified is 16. The total number of self-reported tasks is 21,
> so the **overall error rate is about 16/21=76%**."*

⚠️★★★ **この 2 つは別指標である**（→ 否決 3）。

**5. 議論はあるか?**
⚠️ **GT が「1 日の終わりの自己申告メール」**。著者自身が threats に
*"This assumes that programmers know what a task is, they can recall what they did, and they are willing to report it"*
と書く。→ ★ **「検出 112 vs 申告 21」の乖離が、アルゴリズムの過剰なのか申告の粗さなのかを本研究は分離できていない。**
⚠️ 1 社・6 名・12 人日・回収率 12/18。⚠️ 観測チャネルは **Eclipse の artifact アクセス履歴**でありキーストロークではない。

**6. 次に読むべき論文は?**
★ Coman & Sillitti (ESEC/FSE 2007 / ICPC 2008) の原典（★ **未登録**・ラボ 81% の出所）。

**★ やり残し** ★★★ **最も移植価値が高いのは数値ではなく提言である**:
> *"the problem of identifying the task boundaries in fact consists of **two sub-problems**.
> a) detecting task sessions … and b) **linking related task sessions together**"*

→ ★ **GSE の `stall onset` も「断片の検出」と「断片を同一の停滞に束ねる」を分けないと、同じ過剰分割に落ちる。**
★ ADR-030 **D2 の不応期（refractory）** はこの 2 番目に対応する装置だが、
⚠️ **束ね方（linking）を「不応期の長さ」1 つで代表させてよいかは未検証。**

---

## カード 4: 反復エピソードの離散時間生存分析 —— ただし robust SE の出典にはならない **[検証済 3-0 / 一部 0-3]** [V147]

**1. それはどんなもの?**
同一個人に**複数回**起きるイベント（multiple spells）を離散時間生存分析で扱う方法論論文。
例データは特別支援教育教員 **N=3,941・12 年・1 人最大 4 spells**、Person-Spell-Period **38,672 行**。

**2. 先行研究と比べてどこがすごい?**
★ 単一 spell の枠組み（[V60] Singer & Willett 1993）を**反復へ拡張**し、
⚠️ **「普通のロジスティック回帰にかけるだけでよい」**ことを尤度の一致から示した。

**3. 技術や手法の肝はどこ?**
★ **(a) データ構造** —— 1 行 = (person, spell, period)。逐語
*"when the next spell begins (SP NUM = 2), **the time period counter restarts (PD NUM is reset to 1)**"*。
★ **(b) 過去履歴の統制** —— 逐語
*"**the inclusion of spell dummies as predictors is tantamount to controlling for the number of previous events,
and the duration of a prior spell can easily be included as an additional time-varying predictor**"*（★ Allison [V59] を引く）。

**4. どうやって有効だと検証した?**
★ multiple-spell の deviance は spell 別単独解析の deviance の**単純和**で、推定値と SE は**同一**。
→ ★ **価値は推定値そのものではなく、(i) 同時解析の効率、(ii) spell 間で予測子効果が違うかの検定、
(iii) 前の spell の予測子が次の spell に及ぼす遅延効果の検定**にある。

**5. 議論はあるか?**
⚠️★★★ **本カード最大の発見はここである** —— **W&S は robust SE も frailty も採用していない**（→ 否決 4）:
> *"currently there are **no readily accessible replacements** for them that resolve the problem.
> The best approach, therefore, may be to **continue in the explicit knowledge that the problem exists**."*
> *"any analytic method … that ignores the presence of unobserved heterogeneity is likely to provide
> **inefficient parameter estimates with negatively biased standard errors** (Allison, 1982)."*

⚠️★★★ **GSE に最も効く弱点**（★ 著者が明記）:
> *"the same dependence also occurs **across consecutive time periods within a single spell**"*

→ ★ **GSE は 1Hz で期を刻むので、この「spell 内の期間従属」は年単位より遥かに強い。**
⚠️ かつ **行数を N として扱うと SE が壊滅的に楽観化する**（★ 有効標本は個人数／イベント数）。

**6. 次に読むべき論文は?**
★ **[V150]** Therneau (1993)（★ W&S が corrected variance の出典として挙げる。⚠️ **`provisional`・書誌未確認**）／
★ 現代的な recurrent-event 手法（Andersen–Gill / PWP / 離散時間混合効果）。

**★ やり残し**: ⚠️★★★ **「反復エピソード × 競合リスク」を *同時に* 扱う作法は本論文にも [V148] にも無い。**
★ GSE は 1 セッション内で停滞が繰り返し起き（multiple spells）、かつ終わり方が複数ある（competing risks）。
→ ★ **起票する。**

---

## カード 5: subdistribution hazard —— ⚠️ abstract しか読めていない **[検証済 3-0（限定）/ 判定不能 1]** [V148]

**1. それはどんなもの?**
競合リスク下で **cumulative incidence function (CIF)** への共変量効果を直接評価するための
semiparametric 比例ハザードモデル（JASA 1999）。

**2. 先行研究と比べてどこがすごい?**
> *"the cause-specific hazard function **does not have a direct interpretation in terms of survival
> probabilities for the particular failure type**"* ／ 既存手法は
> *"**do not allow the analyst to directly assess the effect of a covariate on the marginal probability function**"*

**3. 技術や手法の肝はどこ?**
> *"we propose **a novel semiparametric proportional hazards model for the subdistribution**"*

⚠️★★★ **subdistribution hazard の *定義* は確認できていない**（★ 本文未取得・closed access）。
⚠️ よく流布する「**競合イベントを起こした被験者を risk set に残し続ける**」という説明は **一次未確認**。
→ ★★★ **ADR 等で定義を逐語引用してはならない。**

**4. どうやって有効だと検証した?**
★ 乳がん臨床試験データで cause-specific 法と対比（★ abstract 記載のみ・数値未確認）。

**5. 議論はあるか?**
⚠️★★★ **接合部が危ない** —— ★ **Fine–Gray は連続時間モデル**であり、**GSE は 1Hz の離散時間**。
→ ★ **離散時間 × 競合リスクは [V62] Meir & Gorfine (2023) が既登録なので、そちらを主に引く**（→ 否決 5b）。

**6. 次に読むべき論文は?**
★ **[V61]** Austin, Lee & Fine (2016) の実務入門（★ 既登録）／
★ Putter et al. (2024) *incoherence of multiple Fine-Gray models*（★ **未登録**・複数モデル同時当てはめの破綻）。

**★ やり残し**: ★ **本文 PDF の入手**（⚠️ リポジトリ版が見つからなかった）。
★ それまでは `provisional` のまま、**定義を引かず「共変量効果を CIF に対して直接評価できる」までで使う**。

---

## カード 6: JITAI の構成要素は 4 つ。⚠️ かつ GSE は JITAI の定義軸から外れている **[検証済 3-0]** [V149]

**1. それはどんなもの?**
モバイルヘルスにおける **Just-in-Time Adaptive Intervention (JITAI)** の定義・構成要素・設計原理を
体系化した枠組み論文（Ann Behav Med 52(6)）。

**2. 先行研究と比べてどこがすごい?**
★ 「適応的介入」を **decision point 単位の決定規則**へ落とし、**近位／遠位転帰**を分離した。

**3. 技術や手法の肝はどこ?**
> *"**(1) decision points, (2) intervention options, (3) tailoring variables, and (4) decision rules**"*

⚠️★★★ **構成要素は 4 つである。**★ **proximal / distal outcome は "components" ではなく "design principles" 側**。
（⚠️ 内部メモが「6 構成要素」と書いていたら原文と食い違う。→ 否決 6）
> *"**A decision point is a time at which an intervention decision is made**."*
> *"**Proximal outcomes are the short-term goals the intervention options are intended to achieve** …
> Proximal outcomes are often **mediators**"*

**4. どうやって有効だと検証した?**
★ 枠組み論文であり実証研究ではない（★ 事例として HeartSteps 等を引く）。

**5. 議論はあるか?**
⚠️★★★ **GSE の位置づけに直接効く区別がある**:
> *"the adaptation in a JITAI is **employed by the intervention itself rather than by the target individual**."*
> ⇄ *"**participant-determined approaches** that make an array of supportive resources available for the
> target individual to decide when and what type of support to initiate."*

→ ★★★ **ADR-018 D1 で Physical Anchor が完了条件を持たなくなり、ADR-026 が「招待」を差し出す面として
設計された GSE は、この軸では *participant-determined* 側に寄っている。**
⚠️ **したがって「GSE は JITAI である」と自称しない。**★ 引けるのは **decision point / proximal outcome の語彙**と、
★ **「凍結した検出器を用いた介入の因果効果を測る方法」としての MRT**（`.idea/survey §7.5`）まで。

**6. 次に読むべき論文は?**
★ **[V4]** Qian et al. MRT（既登録）／ Klasnja et al. (2015) micro-randomized trials（★ **既登録** = 別 ID）。

**★ やり残し**: ⚠️ **`intervention_eval.rs` の HIR / Precision が JITAI の proximal outcome に対応するかは未照合。**

---

## カード 7: Translog-II は日本語 IME の変換過程を記録している —— 論文と生ログの二重確認 **[検証済 3-0]** [P359] [P360]

**1. それはどんなもの?**
[P359] = Translog-II（翻訳過程研究の標準キーロガー）の方法論論文（*Data* 2026・Gold OA・24 頁）。
[P360] = その公開生データ **ENJA15** の Translog-II XML（★ SVN・`.xml` 226 本）。

**2. 先行研究と比べてどこがすごい?**
⚠️★★★ **著者自身が「Translog-II の logging 能力は文献でしばしば誤って記述されてきた」と名指しで訂正している**
（★ 対象は Muñoz Martín ら ＝ **[V5] Hylog の共著者**）。

**3. 技術や手法の肝はどこ?**
> *"in order to produce the Japanese Kanji "年" … four characters were typed, "NENN", plus the space bar …
> **Translog-II records these five keystrokes as "Type=IME" events and the actual text modification as insertion**."*
> *"The attribute "**IMEtext**" records the sequence of keystrokes that were typed to produce a sequence of
> characters which eventually appear on the screen."*

★ 変換候補選択の時間を**認知的に意味のある段階**と明記:
> *"potentially also the time the typist spends evaluating and selecting among the candidate characters
> presented by the IME—**a cognitively meaningful step**"*

**4. どうやって有効だと検証した?**
⚠️★★★ **本ラウンドは論文を信じず、公開生ログを直接取得して検算した** [P360]。
★ `P01_T1.xml`（10.2 MB・⚠️ **`P01` は *ENJA15 の被験者 ID* であって GSE の被験者ではない**）の実測: `Type="IME"` **1,355** ／ `IMEtext=` **192** ／ `insert` 183 ／ `delete` 92。
★ `Type="IME"` の `Value` は 36 種で全てローマ字キー相当 ＋
⚠️★★★ **`[Back]` 87（変換中の打ち直し）・`[ProcessKey]` 22（候補選択）・`[D0]/[D2]/[D4]`（候補番号）**。
★ 逐語サンプル:
`<Key Time="333156" Cursor="57" IMEtext="D2D0D0D2NNEBackBackNENSpace" Type="insert" Value="２００２年" />`
★★★ **[P359] §2.3 が「終身刑」の例に引く `SHBackBackD4BAISpaceBackBackSHUUSINKEISpace` が生ログと完全一致**
（＝ 論文と公開データが同一起源であることを確認）。

**5. 議論はあるか?**
⚠️★★★ **GSE に効く制約が 2 つある**:
1. **keydown のみ記録し keyup を記録しない** —— *"dwell time … cannot be directly derived from Translog-II logs"*。
2. **IME 単位 ↔ トークン境界の不一致の定量は *中国語 (RUC17) のみ***（69.1% が Type 1）。**日本語は future work**。

⚠️ **content-full である** —— `Value` に確定文字列、`IMEtext` にローマ字打鍵列が残る
（★ ただし**候補の *内容* と順位は記録されない**。残るのは候補 *番号* と `[ProcessKey]` だけ）。
⚠️ **確認は `P01_T1` の 1 セッションのみ**（226 本全数ではない）。

**6. 次に読むべき論文は?**
★ **RUC17 生データ**（★ 中国語・`Type="IME"` 834 を実測済み）／ Lu (2020) [P272]（既登録）。

**★ やり残し** ⚠️★★★ **[V5] との緊張を本ラウンドでは裁かなかった。**
★ [V5] Hylog は一次で *"none supports non-alphabetic writing, as they cannot identify logograms and symbols
introduced by IMEs"* と述べ、**Translog-II もその「既存ロガー」に含まれる**とされてきた。
⚠️ しかし [P360] の生ログでは **確定 insert の `Value` に logogram（`年` / `２００２年`）が入っている**。
→ ⚠️★★★ **文としては両立しない。**★ ただし **[V5] の全文を本ラウンドで再読していない**ので、
★ [V5] が指すのが「**未確定表示状態の再構成**」という別の能力である可能性を排除できない。
→ ★★★ **裁定せず起票する**（⚠️ 一節だけを見て裁かない —— `verify-before-claiming` ルール 7）。

---

## ⚠️★★★ 否決リスト（★ 記録を残さないと同じ主張が無検証で再浮上する）

| # | 否決した主張 | 票 | ⚠️ 否決理由 |
|---|---|---|---|
| **1** | 「**5 分超 idle は成績と正相関する（`r=.507`）**」を効果量として引く | **1-2** | ★ 内的には実測だが、⚠️ **N=19・Spearman・多重比較補正なし**（Table 4 だけで約 40 検定 ＝ Bonferroni で落ちる）。★ かつ相関相手は **idle の長さではなく「5 分超ギャップの *回数*」**。→ ★ **引くなら著者の *定性的結論*（二群に割れて分離できない）を引く** |
| **2** | 「**打鍵過程特徴では停滞を検出できない**」（[P358] を根拠に） | **0-3** | ⚠️★★★ **[P358] の予測対象は「作品の成績」であってプロセス内状態ではない。**★ 被験者間の横断予測で、個人内反復構造が無い。→ ★ 言えるのは「**この特徴集合ではこの課題で拾えなかった**」まで |
| **3** | 「**ラボ 80% が実地で 30% 相当に落ちた**」型の対比 | **0-3** | ⚠️★★★ **分母も定義も違う。**★ 81% = 正しく同定できたタスク数の割合（9/11）／ 76% = **Σ\|検出数 − 申告数\| ÷ 申告総数**（16/21・**定義上 100% を超えうる**）。★ 本文に「70% 以上」という表現は**存在しない** |
| **4** | 「**Willett & Singer (1995) が cluster-robust SE / frailty を推奨している**」 | **0-3** | ⚠️★★★ **W&S 自身は採用していない。**★ 逐語 *"there are no readily accessible replacements … continue in the explicit knowledge that the problem exists"*。★ robust SE を採るなら出典は **[V150]**（Therneau 1993・`provisional`）。⚠️★★★ **[V59]** Allison は *問題の所在* の出典であって手当てではない |
| **5a** | 「**日本語 IME の *変換過程* を含む公開データセットは確認できない**」 | **0-3** | ⚠️★★★ **[P360] の生ログに変換過程が残っている**（ローマ字打鍵・変換中の `[Back]`・候補選択 `[ProcessKey]`・候補番号）。→ ★ **`research-positioning.md` の主張を 1 段下げる**（→ §還元） |
| **5b** | 「**Fine & Gray (1999) を GSE の離散時間設計にそのまま使える**」 | **0-3** | ⚠️ **連続時間モデルである。**★ 離散時間 × 競合リスクは **[V62]** Meir & Gorfine (2023) を主に引く |
| **6** | 「**JITAI の構成要素は 6 つ（proximal / distal outcome を含む）**」 | **0-3** | ★ 原文は **4 components**。proximal / distal outcome は **design principles 側**の概念 |

### ★ 判定不能（⚠️ 「弱い支持」に丸めない）

| 主張 | ⚠️ なぜ判定不能か |
|---|---|
| **subdistribution hazard の定義** | ★ [V148] は **closed access で本文未取得**。⚠️ **二次情報の説明を一次として書かない** |

---

## ⚠️★★★ 書誌の誤りを 2 件見つけた（★ どちらも `.idea` 側・repo の `docs/` には未混入）

| # | 誤り | ★ 実測 |
|---|---|---|
| **1** | `.idea/survey §13` の **`10.18653/v1/L16-1635` は実在しない DOI** | ★ `doi.org` / Crossref / OpenAlex とも **404**。実在するのは **`10.63317/596uwk22ufyn`**（ELRA）。⚠️ ★ **repo の `docs/` には混入していない**（grep 実測） |
| **2** | ★ その DOI が指すのは **[P273] とは別の論文**である | ★ `L16-1635` = *"English-to-Japanese Translation vs. Dictation vs. Post-editing"*, **LREC 2016, pp.4024–4031**。⚠️ **[P273] は APTIF 2016 の *"ENJA15: A Free Corpus of English–Japanese Translation Process"***。→ ★ `.idea/survey §13` が「Carl et al. (2016), ENJA15」として挙げているのは**コーパス論文ではない方**である |

> ⚠️★★★ **したがって [P273] 本文の読み（「IME の扱いは 1 語も書かれていない」）は本ラウンドで検証されていない。**
> ★ 本ラウンドが読んだのは **LREC 論文**のほうで、そちらでは `IME` が**脚注に 2 回**出る
> （*"problems of gaze-to-word when using IME input"* / *"problems for computing PWR based on the IME input"*）——
> ★ **いずれも記録方式の記述ではない。**
> → ★ **閉じたのは [P273] の *やり残し*（生ログで IME 事象の記録有無を直接確認する）だけである。**

## ★ 名前空間の判定則（⚠️ 本ラウンドまで明文化されていなかった）

⚠️★★★ **規則が無いと次ラウンドが再現できない**（★ `code-reviewer` MEDIUM 指摘）。★ 以後はこれで割る:

> ★ **主張の使途が「GSE の *設計仮説* を動かすもの」なら `P`／「*評価手続きの制約* を課すもの」なら `V`。**

★ 本ラウンドの適用: **P** = [P357]（沈黙の意味）/ [P358]（特徴量の天井）/ [P359] [P360]（IME の記録可能性）。
**V** = [V146]（外的妥当性の崩れ方）/ [V147] [V148] [V150]（生存解析の作法）/ [V149]（JITAI の評価枠）。
⚠️ **renumber 禁止なので過去分は遡及修正しない。**★ 既存の揺れ（[V83] Poreba ⇄ [P358] Conijn）はそのまま残る。

## ★ research-positioning.md への還元

⚠️★★★ **反証だったので主張を下げる**（→ 否決 5a）。詳細は `docs/research-positioning.md` の該当箇所を参照。
★ 残る差分は `.idea/survey §3.1` が既に述べていたとおり
**「content-free・一般アプリ横断・自然作業・未来回復との接続」**であり、**IME 記録そのものではない**。

## ★ 次ラウンドの入口（やり残し）

1. ⚠️★★★ **[V5] と [P359]/[P360] の緊張を裁く**（★ [V5] 全文を再読してから。**本ラウンドでは裁定しなかった**）
2. ⚠️★★★ **「反復エピソード × 競合リスク」を同時に扱う作法**（★ [V147] にも [V148] にも無い）
3. ★ **[V148] Fine & Gray の本文 PDF**（★ 定義を引けるようにする）
4. ★ `.idea/survey §13` の**残り 14 件**（★ 33 中 19 登録済み・**2026-09-13 に機械で数え直した**。⚠️★★★ 初稿の「17 件」は自分で検算しておらず誤りだった。★ かつ `Carl et al. (2016), ENJA15` の 1 行は **2 論文を取り違えている**ため数え方が一意でない ——**LREC 論文として数えれば 15 件**）——
   特に **Putter et al. (2024)**（複数 Fine-Gray モデルの非整合）／**Coman & Sillitti 原典**（ラボ 81% の出所）／
   **Conijn et al. (2021)** revision detection ／ **[V150] Therneau (1993) の書誌特定**
5. ★ **ENJA15 の残り 225 セッション**で `Type="IME"` の有無を確認（★ 本ラウンドは `P01_T1` のみ）
