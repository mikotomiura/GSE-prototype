# 文献カード: 実オフィスの打鍵動態と精神的疲労（de Jong et al. 2020）[P218]

- **トピック**: typing-dynamics-mental-fatigue
- **日付**: 2026-09-01
- **出典 [P218]**: `docs/references.md` の [P218]（key: `doi:10.1371/journal.pone.0239984`）
- **一次確認**: ★ **JATS XML 原本の全文**（119,812 chars）を取得し、逐語を機械照合した。
  取得経路は `https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0239984&type=manuscript`。
  ライセンス **CC BY 4.0**（<https://creativecommons.org/licenses/by/4.0/>）。
  ★ **改変の表示**: 逐語引用は英語原文のまま、**和訳・要約・再構成・表の抜粋は本カードによる改変**である
  （CC BY 4.0 §3(a)(1)(B)）。逐語の総量は原文 119,812 文字に対し約 2.8%。
- **なぜこのカードが要るか**: ★★★ **GSE のセンシング方式そのものの先行研究**である
  —— 実オフィスで 6 週間、**content-free の打鍵動態のみ**から作業者の状態変化を追った。
  ⚠️ かつ **著者自身が GSE の中核リスク（リアルタイム・フィードバックの偽陽性）を名指ししている。**

---

## ⚠️★★★ 最初に: 引き継ぎメモの前提を 1 件訂正した

`.steering/_handoff/next-session-research-positioning-fix.md` は本論文を
**「打鍵動態から精神的疲労を検出」**と要約していたが、★ **一次全文にあたったところ正確ではない。**

| | 引き継ぎメモの記述 | ★ 一次で確認した実体 |
|---|---|---|
| 疲労の測定 | 「打鍵動態から**精神的疲労を検出**」 | ⚠️★★★ **本研究は疲労そのものを測っていない。** 疲労尺度（CIS / NASA-TLX / KSS 等）の使用記述が本文に**一切ない**。測ったのは **time-on-task / time-of-day / day-of-week に対する打鍵指標の変化**であり、疲労との接続は**先行するラボ実験 [18]（同一研究室の 2018 年 EEG 実験・P3 との相関）からの外挿**である。★ **公平のため付記する**: 著者自身は abstract で *"markers derived from typewriting are **susceptible to changes in behavior related to mental fatigue**"* と枠づけており、⚠️ **「疲労と関連する行動変化」であって「疲労の測定」ではない**という言い方を保っている（★ 誇張しているのは要約側であって著者ではない） |
| 観察の純粋性 | （言及なし） | ⚠️★★★ **6 週間ずっと介入が入っていた** —— 逐語: *"**Each working day, participants received real-time feedback on their performance provided via text messages on their mobile phones and via email.** An overview was provided via email at the end of the day."* ★ **本論文を「純粋観察の先行例」として引くのは不正確である。** かつ著者はこれを限界として論じていない |
| 標本 | （言及なし） | ⚠️ **N = 22（45 名中）。残存率 49%** |

→ ★ **本カードは訂正後の実体に基づいて書く。**（`verify-before-claiming` ルール 1: 三次資料＝引き継ぎメモを根拠にしない）

---

## 1. それはどんなもの?

大学職員 22 名の**実際の執務環境**で 6 週間、ワークステーションに常駐した keylogger が
**キー間隔（interkey interval）とバックスペース比率の 2 指標だけ**を 1 分刻みで記録し、
**連続打鍵 45 分以上のブロック**を対象に、打鍵動態が
**time-on-task（連続作業時間）/ time-of-day（午前・午後）/ day-of-week（曜日）**でどう変わるかを
混合効果モデルで解析した縦断観察研究。

★ 主要な所見は **「連続作業とともにタイピングは遅く・不正確になるが、その形は時間帯と曜日で変わる」**であり、
⚠️ **「疲労を検出した」ではない。**

## 2. 先行研究と比べてどこがすごい?

- ★ **実験室から実オフィスへ出た点**。逐語: *"Previously, this type of research was mainly conducted in
  **simulated office environments** [37]"* ／ *"…or focused on **self-reported behavior of employees** [38],
  using measures that either **interrupted regular office work** or relied on **subjective measures influenced
  by the observer's personal judgment** [39]."*
  → ★★★ **GSE が掲げる「作業を中断せず・自己申告に頼らず・常時測る」という三点セットが、
  そのまま本論文の新規性の主張である。**
- ★ **content-free 制約の水準が GSE より強い**。保存したのは **1 分ごとの「直前 15 分の平均キー間隔」と
  「直前 15 分のバックスペース比率」のみ**で、**生のキーコード列すら残していない**。
  逐語: *"To safeguard the confidentiality of the typed text during the study, **only the backspace key was
  given a unique marker**."*
  → ★ **プライバシー制約下でも 6 週間の実環境縦断が成立することの外部的裏付け**（GSE の設計姿勢に有利）。
- ★ **先行するラボ実験** [18]（de Jong et al. 2018, *Front. Psychol.* 9:1113）が
  **統制環境で EEG P3 と打鍵指標の相関**を示しており、本論文はその**現場移送**にあたる
  （⚠️ 「親論文」は引用関係上の正式な語ではないので「先行するラボ実験」と書く）。

## 3. 技術や手法の肝はどこ?

- **指標は 2 つだけ**: 平均キー間隔（★ **5 秒超の間隔は平均から除外**）と バックスペース比率。
  ⚠️★★★ **この 5 秒閾値は意図的に「注意の途切れ（mental block）」を捨てている** —— 逐語:
  *"**In the present study, we excluded lapses of attention by excluding interkey intervals that were longer
  than 5 seconds.**"*
  → ★ **GSE の F3/F6（サイレンス系）が拾おうとしているのは、本論文がまさに捨てた帯域である。**
- **窓の取り方**: 1 分ごとに直前 15 分を集約 → 45 分以上連続した系列のみ解析対象。
  ★ GSE の 30 秒ローリングウィンドウより **2 桁粗い**。
- **解析**: `lme4` の混合効果モデル（参加者ごとに varying intercept、AIC が改善すれば
  time-on-task / time-of-day の varying slope を追加）、自由度は Satterthwaite 近似、事後検定は Bonferroni、
  多項式対比（linear / quadratic）で 120 分の形を見る。

## 4. どうやって有効だと検証した?

**設計**: N = 22（12 女性・M = 48.1 歳・SD = 13.4）。45 名が同意し **23 名を除外**
（除外理由の逐語: 打鍵を伴わない業務（*"teaching and collecting research data"*、特に博士課程学生・
ポスドク）／**複数のワークステーションで働いていた**ため記録機の設置端末にデータが集まらなかった）。
0.8 FTE 以上・打鍵が業務に含まれることが参加条件。6 週連続、2 コホート（5 月開始 / 11 月開始）。

**主結果（実数・★ 原論文 Table 2 / Table 3 より）**:

| 効果 | キー間隔 | バックスペース比率 |
|---|---|---|
| Time-on-task² | F(2, 94707) = 17.75, p < .001 | F(2, 91637) = **284.28**, p < .001 |
| **Time-of-day** | ⚠️ **F(1, 94719) = 1.07, n.s.** | F(1, 91656) = 36.55, p < .001 |
| Day-of-week | F(4, 94707) = 74.15, p < .001 | F(4, 91637) = 53.37, p < .001 |
| Time-on-task² × time-of-day | F(2, 94703) = 6.90, p = .001 | F(2, 91634) = 12.93, p < .001 |
| 3 元交互作用 | F(8, 94701) = 72.08, p < .001 | F(8, 91633) = 9.54, p < .001 |

- **午前と午後で形が違う**: 逐語 *"**the interkey interval remained stable during continuous typewriting in
  the morning, but in general it increased with 11.6 ms during two hours of continuous task performance in
  the afternoon**."* ⚠️ **午前のキー間隔は linear（z = −1.92）・quadratic（z = 1.73）とも非有意**。
- **バックスペースは午前も午後も増える**（120 分で **約 1.6%**）。増え方の**形**だけが午後で二次関数寄り。
- ⚠️★★★ **曜日の仮説は棄却された**。逐語: *"First, we hypothesized that typing performance would decline
  over the workweek… **Contrary to our expectations**, we observed an increase in the interkey interval from
  295 ms on Monday to 301 ms on both Tuesday… after which the interkey interval decreased to 296 ms on
  Thursday and **291 ms on Friday**, during which employees' typewriting was fastest."*
  ★ **曜日差は最大 10 ms で、参加者間 SE（≈ 9.6 ms）と同程度**である。
- **速度‑正確性トレードオフではない**: 午後は両指標の個人別傾きが正相関（**r = 0.622, p < .001**）。
  ⚠️ **午前は無相関（r = −0.04, n.s.）**。

⚠️★★★ **効果量（d / η² / R² / ICC）と信頼区間は、本論文に 1 つも報告されていない**
（★ 「未取得」ではなく **原論文に存在しない**）。図の帯は CI ではなく SEM。
→ ★ **本論文から効果量を引くことはできない。**

## 5. 議論はあるか?

★ **専用の Limitations 節は無い**（節構成は Introduction / Present study / Methods / Results / Discussion /
Conclusions のみ）。以下はすべて Discussion 本文からの逐語。

1. ⚠️★★★ **著者自身が GSE 型のリアルタイム介入の偽陽性リスクを名指ししている**（★ 本カードの最重要点）:
   > *"First, **personalized real-time feedback based on changes in typing behavior could be provided** to the
   > users in order to help them detect when lapses in performance occur and a short break might be beneficial.
   > **However, real-time feedback might be biased due to dynamics in typewriting performance that are not
   > related to lapses in performance.** One of the characteristics of our working environment is the large
   > variability in working conditions, due to changes in work-related tasks, noise in the working environment,
   > and changes in general persons state, among others."*
2. **バックスペースは多義的**: > *"…**an increase in backspace use could originate from different types of
   behavior**. That is, in our study, participants could have corrected more (in)correctly typed letters
   and/or **detected their errors later**, which, as a result, required more consecutive backspaces to correct
   one incorrect keystroke."*
   → ★ GSE の `bs_rate` にそのまま当てはまる警告である。
3. **content-free の代償を著者が明記**: > *"**In order to safeguard the privacy of the employees, however, we
   did not monitor the identity of the keys apart from the backspace keys. For this reason, we were not able
   to identify and analyze the mistakes that were not corrected during typewriting.**"*
4. **統制不能な交絡**: > *"…**many uncontrollable factors may have influenced performance efficiency due to
   the dynamic nature of the actual office environment** [40, 41]."*（中断・電話・オンライン活動が需要を上げ、
   一方で作業動機と**スケジュール自律性**が需要を下げる、と両方向を挙げる）
5. ⚠️ **休憩に関する記述は控えめ**: > *"These findings imply that, **although office workers are entitled to
   have breaks during a working day, the scheduled breaks might not have been enough to fully recover from
   the demands they encountered during the day** [46]."*
   ⚠️★★★ **これは示唆であって検定ではない** —— ★ **本研究は休憩を操作していない。**
   （★ 引き継ぎメモの逐語は *"…fully recover"* で切れていたが、原文は *"from the demands they encountered
   during the day [46]"* まで続く。★ 引くときは全文で引くこと）
6. ★ **本カードが独自に見つけた問題（著者は論じていない）**:
   ⚠️★★★ **測定期間中ずっと日次フィードバックが与えられていた**にもかかわらず、
   これが打鍵動態そのものを変えた可能性（計測反応性 [P163]）は Discussion で一切扱われていない。
7. ★ **原論文内の数値の不整合を発見**: 本文はバックスペースの 2 元交互作用を
   *"F(2, 93467) = 9.54, p < .001"* と書き *"see Table 2"* を参照するが、
   **Table 3 の 2 元交互作用は F(2, 91634) = 12.93** で、**9.54 は 3 元交互作用の値**、
   かつ **Table 2 はキー間隔の表**である。→ ⚠️ **引用時は本文ではなく Table の値を採ること。**

## 6. 次に読むべき論文は?

| 文献 | なぜ | 登録 |
|---|---|---|
| **de Jong, M., Jolij, J., Pimenta, A. & Lorist, M. M. (2018)** — "Age Modulates the Effects of Mental Fatigue on Typewriting" *Frontiers in Psychology* **9:1113**, `doi:10.3389/fpsyg.2018.01113`（**CC-BY 4.0 / OA**） | ★★★ **本論文が疲労との接続に使っている唯一の根拠**。統制環境（120 分の打鍵課題 ＋ EEG）で **P3** と打鍵指標の相関を示した**先行するラボ実験**。★ Young N=24（18–30）/ middle-aged N=24（50–67）で、逐語 *"typing accuracy decreased with ToT **in the young group, however, not in the middle-aged group**"* ＝ ⚠️ **年齢がモデレートする**（GSE の被験者構成に直結）。⚠️★★★ **ここを読まない限り「打鍵 → 疲労」の接地は本論文からは取れない** | ★ **未登録・最優先**（★ 書誌と DOI は 2026-09-01 に Crossref で検算済みなので、次タスクはそのまま append できる） |
| **Pimenta, Carneiro, Novais & Neves (2014)** *Hybrid Artif. Intell. Syst.* 389–401 | 打鍵からの非侵襲的な精神的疲労計測の先行。逐語 *"They found that several markers of typing performance were susceptible to the effects of time-of-day."* | 未登録 |
| **Steinborn & Huestegge (2016)** *Appl. Cogn. Psychol.* 30(5):795–805 — "A Walk Down the Lane Gives Wings to Your Brain" | ★ 本論文が *"time-on-task effects can be reversed by taking a short (coffee) break [25]"* の根拠に引く。⚠️★★★ **Physical Anchor に直結するが、[P162]（歩行特化の推定値は存在しない）と突き合わせが要る** | 未登録・要精読 |
| **Bills (1931)** *Am. J. Psychol.* 43:230–245 — "Blocking: a new principle of mental fatigue" | mental block（phasic lapse）の原典。★ **本論文が 5 秒閾値で捨てた帯域の理論**であり、**GSE のサイレンス特徴量が拾う帯域**そのもの | 未登録・要精読 |
| **Hockey & Earle (2006)** *J. Exp. Psychol. Appl.* 12(1):50–65 | ★ **作業スケジュールの自律性が疲労と成績への負荷の影響を減らす**。ADR-018（本人が決める）の傍証になりうる | 未登録 |

---

## → GSE への含意

- **やり残し（1 行）**:
  ⚠️★★★ **打鍵動態の変化を「疲労」や「停滞」として *読み出す* 段が、実環境では誰も検証していない** ——
  本論文は変化があることを示したが、疲労を測っておらず、効果量も報告せず、
  ★ **著者自身が「リアルタイム・フィードバックは、成績低下と無関係な打鍵動態の変動でバイアスされうる」と
  明記して読み出しの妥当性を未解決のまま残している。**

- **§4 差分との関係**: ★ **補強と精緻化の両方**である。
  1. ★ **補強**: 「本文非保存の行動プロキシで、作業を中断せず、自己申告に頼らず、実環境で常時測る」という
     GSE の測定姿勢は、**本論文が自らの新規性として掲げたもの**と一致する。
     ★ **6 週間の実オフィス縦断が content-free で成立した実例**があることは、GSE の feasibility を上げる。
  2. ⚠️★★★ **精緻化（差分の位置が動く）**: **GSE の空白は「打鍵から状態を測ること」ではない。そこは既にある。**
     ★ 空白は **(a) その読み出しに基づいて *介入する* こと**と、**(b) 介入が読み出しの妥当性を壊さないこと**である。
     ⚠️ **本論文はまさに (a) を future work として提案し、同じ文で (b) を危険と名指しした状態で終わっている。**
     → ★ **GSE の差分は「著者が危険と書いた一歩を、危険を測りながら踏む」ことに定式化できる**
     （★ HIR（有害介入率）と dismiss 率を第一級のアウトカムに置く GSE の設計は、この定式化と整合する）。
  3. ⚠️★★★ **反証側として効く点を隠さない**:
     - **本論文の観測窓は 15 分平均**であり、**GSE の 30 秒ウィンドウで同じ信号が立つ保証は無い。**
     - **5 秒超の間隔を捨てて**なお効果が出ている。★ **GSE はその捨てた帯域（サイレンス）を主戦場にしている**ため、
       **本論文は GSE の F3/F6 を支持しない**（否定もしない —— **測っていない**）。
     - ⚠️ **曜日の仮説は棄却された。**「週の後半ほど疲れる」型の設計仮説を GSE が置くなら、
       **本論文は反証側の一次証拠**である。
     - ⚠️ **N=22 / 残存率 49%**、脱落理由は「打鍵量不足」と「複数端末での勤務」。
       → ★ **GSE の被験者募集と単一機縛りに直接効く運用上の教訓**である。
