# S7 生報告の退避（S7-a / S7-b / S7-c）—— ⚠️ 未検証。3 票検証の入力

> 2026-09-19。サブエージェント（Opus）の報告。⚠️ S7-b は逐語引用を 1 か所に制限していたため、定義は「数値を残した言い換え」。
> ★ 取得済み本文（pypdf 抽出・`=====PAGE n=====` 区切り）: `C:\Users\johnd\AppData\Local\Temp\s7b\*.txt` —— **カード化の前にメインが逐語を照合する**。

## S7-b（教育測定・学習分析の打鍵特徴）

### 結論（サブエージェント）
- キー種別と時刻だけで計算できる修正特徴は 4 系統: (1) 削除キーの回数・連の長さ・直前ポーズ、(2) Insert/Delete の交替系列、(3) P-burst と「削除で終わる R-burst」の近似、(4) 修正間の時間。
- 位置か本文が要る: jump edit / I-burst / Cut・Paste / typo の除外、ETS のチャンク系特徴（Retyped / TypoCorrected / NewContent 等・式は非公開）、修正の連鎖（repetitive / embedded）。
- 不利な証拠: 位置なしの DIRatio は得点群で差なし（Zhu 2019）／編集回数と得点の関係は文書長で正規化すると大部分が消える（Almond 2012）／多重 backspace 特徴は課題をまたぐ相関 .09（Deane & Zhang 2015）／位置で J と E を分けた 4 状態モデルが 3 状態より有意に当てはまる（Guo 2020）。

### 文献表（DOI は Crossref 確認）
| 著者 年 | 題名 | DOI | 設計・N | 範囲 |
|---|---|---|---|---|
| Almond, Deane, Quinlan, Wagner & Sydorenko 2012 | A Preliminary Analysis of Keystroke Log Data From a Timed Writing Task（ETS RR-12-23） | 10.1002/j.2333-8504.2012.tb02305.x | CBAL・68 名 | 全文 |
| Deane 2014 | Using Writing Process and Product Features to Assess Writing Quality…（ETS RR-14-03） | 10.1002/ets2.12002 | N=1,569 / 1,284 | 全文 |
| Zhang & Deane 2015 | Process Features in Writing…（ETS RR-15-27） | 10.1002/ets2.12075 | 29 特徴・N=831 | 全文 |
| Deane & Zhang 2015 | Exploring the Feasibility of Using Writing Process Features…（ETS RR-15-26） | 10.1002/ets2.12071 | 6 課題・2,500 名超 | 全文 |
| Deane et al. 2018 | Retyping, drafting, and editing（ETS RM-18-06） | DOI 未確認 | N=463 | 定義と要約部 |
| Zhu, Zhang & Deane 2019 | Using Keystroke Sequences…（ETS RR-19-11） | 10.1002/ets2.12247 | N=761・系列マイニング | 全文 |
| Guo, Zhang, Deane & Bennett 2020 | Scenario-based assessment… writing processes（JEDM 12(1):19–45） | 10.5281/zenodo.3911797 | 4 状態セミマルコフ・N=1,082 | 全文 |
| Baaijen, Galbraith & de Glopper 2012 | Keystroke Analysis: Reflections on Procedures and Measures（Written Communication 29(3):246–277） | 10.1177/0741088312451108 | Inputlog・80 ログ | 全文 |
| Galbraith & Baaijen 2019 | Aligning keystrokes with cognitive processes in writing（*Observing Writing* pp.306–325） | 10.1163/9789004392526_015 | レビュー・PCA | 全文 |
| Conijn, Dux Speltz & Chukharev-Hudilainen 2024（online 2021-11-22） | Automated extraction of revision events from keystroke data（Reading and Writing 37:483–508・CC BY） | 10.1007/s11145-021-10222-w | 注釈 7,120 候補・N=65 | 全文 |
| Conijn et al. 2022（online 2021） | A product- and process-oriented tagset for revisions in writing（Written Communication 39(1):97–128） | 10.1177/07410883211052104 | N=65・7,120 修正 | 全文 |
| Conijn, Roeser & van Zaanen 2019 | [P36] 既登録 | 10.1007/s11145-019-09953-8 | — | — |
| Chenoweth & Hayes 2001 / Kaufer, Hayes & Flower 1986 | R-burst の原典 | 10.1177/0741088301018001004 / 10.58680/rte198615612 | — | **未取得**（二次引用 3 件は一致） |
| Guo et al. 2018 / Sinharay et al. 2019 | — | 10.1111/jedm.12172 / 10.1080/08957347.2019.1577245 | — | abstract のみ |

### 特徴定義（抜粋・判定: 不要 = キー種別と時刻だけで可 ／ 近似 ／ 要 = 位置・本文が要る）
- number of backspaces or deletes（Conijn 2019 p.8; tagset Table 1 E2 p.103）: **不要**（ただし選択削除 1 回と BS 10 回で値が変わる）
- single / multiple-character backspacing（Deane 2014 p.10, Table 3 p.13; Almond p.15）: **不要**
- DIRatio = NumDelete ÷ NumInsert（Zhu p.5）: **近似**
- keystroke action subsequences（insert/delete の系列・内容と間隔を無視・長さ ≤10・support ≥0.1）（Zhu pp.4, 9–11）: Insert/Delete 部分は**近似**、cut/paste/replace は**要**
- Local Editing state E（Guo 2020 pp.21, 23–24: 長いポーズ = IKI > KBS×10、W=5 の窓で delete・replace が 2 を超えたら E）: **近似**（KBS は語の同定が要る）
- revision event の開始（Conijn 2024 pp.488–489, 493）: ① 文書長が減る削除が始まる → **近似**、② leading edge 以外での挿入 → **要**
- revision end の baseline: 削除後に打った文字数が削除文字数に並んだ打鍵を終端（Conijn 2024 p.494, Table 3）→ **不要**。★ 完全一致 36%（±1 打鍵で 57%）、文字列を使う RF は 71%
- P-burst / R-burst（Baaijen p.250; G&B pp.308, 311・二次引用）: P は**不要**、R は**近似**（BS 連で終わる塊）
- burst（ETS: Edit 以外の事象が 2/3 秒未満の間隔で続く系列、2/3 秒 ≒ 平均ポーズ＋2SD）（Almond p.15; Deane 2014 p.9）: **近似**
- Repetitive / embedded（repetitive = 直前の修正の開始位置から 2 字以内で始まる修正）（tagset p.111）: **要**
- Jump / J state / I-burst / Cut / Paste / typo の除外 / CorrectedTypo 等 / EventsAfterLastCharacter / efficiency: **要**
- pause before revision / time from previous revision（tagset Table 1 H2, I7）: **不要**
- 唯一の逐語: Conijn 2024 p.489 —— 公開コードの前提データは各押下の "key type, position in the document and current document length"

### claim（向き・言い換え）
- 不利: 位置なしの DIRatio は得点群間で有意差なし（Zhu Table 1 p.6、考察 p.12）
- 有利: 内容を無視した Insert/Delete 部分系列で得点群と性別を判別（p<.001）。最も判別的なのは語長を超える削除連（Zhu pp.11–12）
- 不利: 編集事象数を最終字数で正規化すると得点との関係が大部分消える（Almond p.39）
- 不利: 編集因子は総時間に .83／.88 で負荷（Deane 2014 Table 3 p.13）
- 不利: 編集因子は人手得点の有意な予測子にならず、交差検証でも再現。編集行動の基準率は極めて低い（Zhang & Deane p.7, Table 6 p.9）
- 不利: 総時間で正規化した多重 backspace 特徴の課題間相関は最低 .09（Deane & Zhang p.9）
- 有利（弱）: 編集因子はプロンプトをまたぐ予測で β=.14／.18（Deane 2014 p.17）
- 有利: 修正の 77.9% は leading edge 上、86.2% はカーソル位置、81% はカーソル移動なしで始まる（tagset Table 2 p.114; Conijn 2024 Table 7 p.505）
- 有利: 削除を 1 件でも含む候補は決定木ですべて真の修正（候補の 93% が真）（Conijn 2024 p.493）
- 不利: backspace だけの操作化は文脈挿入を漏らす。終端を最後の BS に置くのも誤り（Conijn 2024 p.485）
- 不利: 位置で J と E を分けた 4 状態モデルが 3 状態より有意（LRT p<.0001）（Guo 2020 pp.28, 37）
- 不利: 修正量の大域指標（text modification index）は有用性が限られる（G&B p.321）
- 中立: R-burst（PR 型平均 4.43 語）は P-burst（5.87 語）より短い（Baaijen p.259）

### 見つからなかったもの
- キー種別と時刻だけで修正特徴を作り、人手注釈の修正と照合して妥当性を示した研究: **0 件**
- 位置なし特徴と位置あり特徴の正面比較: **0 件**（Guo 2020 が間接）
- ETS の "in-word editing" という特徴名: **0 件**
- ETS のチャンク系特徴の計算式: **非公開**

## S7-a（書字過程研究の修正分類・反証側 S7-d）

> 取得済み本文: `C:\Users\johnd\AppData\Local\Temp\s7lit\*.txt`（`mahlow2023.txt` の中身は Buschenhenke 2024、`conijn2022_revext.txt` は Conijn 2024）。
> ★ 主要 claim はカード（`docs/literature/20260919-content-free-revision-measures.md`）に採った。ここには採らなかったものだけ残す。

- 修正は位置で分ける: L&S 2006b abstract *"Revisions are fundamentally divided according to their position in the text and according to their effect on the developing text."*（⚠️ 本文未取得・pre / contextual の定義は Haugaard & Jensen 2019 p.39 経由の二次）
- Faigley & Witte 1981 p.402（CCC 32(4):400–414・doi:10.58680/ccc198115887）: 分類軸は命題（本文）が要る
- Trace-it の「level」は言語単位（paragraph / sentence / phrase / word / character）であり入れ子の深さではない（KTH ページ）
- 入れ子は "hierarchy of revisions … revision tree"（Trace-it）／ embedded は位置の範囲の包含（tagset p.111）
- overrides は人手注釈で一致度 α = 0.55（tagset Table 3 p.116）
- Inputlog マニュアル p.89: substitution の同定には位置データが要る
- Leijten & Van Waes 2013 [V31] p.366: "recursivity" は S-notation の非線形性の写像
- 反証: How to Typo p.87 copy task では typo の 56% が即時訂正、25% が 1 打鍵遅れ … ／ p.90 自然課題では 10 文字以上遅れて直されることがある
- 反証: Haugaard & Jensen 2019 p.39 本文があっても pre-contextual は打鍵ログだけでは解釈困難
- 位置なしで借りられる指標（tagset E.2 / H.1 / H.2 / I.7・Conijn 2024 の件数終端・Baaijen の時間条件・Malekian の単発/連続 BS）—— ⚠️ 妥当性の検証は無い
- 見つからなかったもの: 位置なしの入れ子の深さの数値指標 0 件 ／ 「rewrite」「redelete」「loop depth」を修正の構成概念として定義した文献 0 件（ETS の "retyping" は copy typing の意味・RM-18-06 p.6）／ キー種別と時刻だけの typo 判別 0 件 ／ 日本語 IME 0 件

## S7-c（RQA・プログラミングの編集ログ・入れ子の深さ）

> 取得済み本文: `C:\Users\johnd\AppData\Local\Temp\s7c\`。逐語つき。

### 要点
- 打鍵に RQA をかけた研究の入力は **打鍵間隔（IKI / KPI）だけ**。**キー種別の系列に RQA / CRQA をかけた研究: 0 件**（語・文字の系列は本文が要る）。
- **名前の衝突 2 件**: (a) Allen et al. 2016 の "Average Recurrence" は RQA ではなく「打鍵がある時間窓どうしの距離」＝ポーズの指標、(b) Haake et al. 2022 は RQA を「local ではなく **global** な打鍵パターン」と位置づける → `local_recurrence` は両方と衝突。
- 位置なしの D/I 系列分析は **Zhu et al. 2019 の 1 件**。結論は GSE に不利: 得点群を分けたのは **D/I の交替ではなく、語長を超える D の連続または I の連続**。
- **位置を使わずに修正の入れ子の深さを定義した例: 0 件**。`loop depth` の用例 0 件。S-notation の入れ子は本文中の空間位置の括弧階層。
- 反証: IKI の RQA は打鍵速度と r = −0.55〜−0.72、RQA 指標どうしは r = 0.73〜0.98 で 1 因子に潰れる。

### 文献表（全件 references.md 未登録）
| 著者 年 | 題名 | DOI | 設計・N | 範囲 |
|---|---|---|---|---|
| Haake, Wallot, Tschense & Grabowski 2022 | Global temporal typing patterns in foreign language writing: exploring language- and task-specific… with RQA（Reading and Writing 37:385–417） | 10.1007/s11145-022-10331-0 | 被験者内 L1/EFL・N=40 | 全文 |
| Wallot & Grabowski 2013 | Typewriting dynamics: What distinguishes simple from complex writing tasks?（Ecological Psychology 25(3):267–280） | 10.1080/10407413.2013.810512 | 3 課題・N=64 | 受理稿全文 |
| Wallot & Grabowski 2019 | RQA tutorial for keystroke logging（*Observing Writing* pp.163–189） | 10.1163/9789004392526_009 | — | 未取得 |
| Allen, Jacovina, Dascalu, Roscoe, Kent, Likens & McNamara 2016 | {ENTER}ing the Time Series {SPACE}（EDM 2016 pp.22–29） | DOI 未確認（ERIC ED592674） | N=126 | 全文 |
| Allen, Likens & McNamara 2017 | RQA… dynamical analysis of student writing（FLAIRS-30 pp.240–245） | DOI 未確認（ERIC ED585783） | N=131 | 全文 |
| Marwan, Romano, Thiel & Kurths 2007 | Recurrence plots for the analysis of complex systems（Physics Reports 438:237–329） | 10.1016/j.physrep.2006.11.001 | 総説 | arXiv 版 §3.5 |
| Jadud 2006 | Novice compilation behaviour in BlueJ（PhD, Kent） | 10.22024/UniKent/01.02.86458（doi.org 解決・Crossref 無し） | 観察 | §4.3 |
| Švábenský et al. 2024 | Three programming error measures（ITiCSE pp.87–93） | 10.1145/3649217.3653563 | N=280 | arXiv 全文 |
| Kofune, Shimari & Matsumoto 2026 | Struggling students… keystroke editing（arXiv:2608.25769・SNPD 2026） | arXiv（DOI なし） | N=507 | **査読前** |
| Buschenhenke, Conijn & Van Waes 2023 | Measuring non-linearity（Reading and Writing 37:511–537） | 10.1007/s11145-023-10449-9 | 単一作家・約 400 セッション | 主要節 |
| （Zhu 2019 / Deane & Zhang 2015 / Conijn 2021 は S7-b と共通） | | | | |

### 逐語（抜粋）
- Marwan 2007 Eq.41: *"RR(ε) = 1/N² Σ R_i,j(ε) … a measure of the density of recurrence points in the RP"* ／ Eq.46 determinism: *"the ratio of recurrence points that form diagonal structures (of at least length lmin) to all recurrence points"*。⚠️ **`local recurrence` という語は Marwan 2007 に 0 件**
- Haake 2022 p.402: *"The pause time between each keystroke served as the target event for RQA"*／ pp.397–398（カテゴリ系列の設定）*"we can set the delay parameter as well as the embedding parameters to 1, and the threshold parameter (close) to 0"*
- Haake 2022 p.406: *"shorter IKIs (thus faster typing) also corresponded to higher values of RQA"*（Table 6: 中央値 IKI と RR −0.62・DET −0.72）／ p.409: *"these measures correlate very highly—… between r = 0.73 and 0.98"*／ p.407-408: 打鍵能力で RQA 成分の分散 30.07%、言語熟達度を足して 38.19%
- Wallot & Grabowski 2013（受理稿 p.12）: *"Factor 2 captures variance from overall length of key-press intervals and … (%Recurrence and %Laminarity). This factor is unrelated to the difference between typing tasks"*
- Allen et al. 2016 p.25（Average Recurrence）: *"expressed as the distances between time windows that contain at least one keystroke event. This measure is useful for identifying writing pauses"*／ p.26: Verbosity（打鍵数）が r = .819
- Allen et al. 2017 p.242: *"the words were converted into series of categorical numeric codes, wherein the codes represented the individual word types"*（本文が要る）
- Zhu 2019 p.5: *"the ratio of NumDelete over NumInsert, which approximately captures the extent of editing and revision of any kind"*／ p.4: *"we purposely ignored the linguistic content"*／ p.9: *"we only consider the actions, while ignoring the lengths of the pauses"*／ p.6: *"The difference on DIRatio was not significant"*／ **p.11: *"longer sequences … of delete or insert actions rather than local editing featuring alternating deletes and inserts"***／ p.12: *"not minor edits, which tend to be quick fixes to one or two characters"*（著者の解釈・検定なし）
- Deane & Zhang 2015 p.13: *"(pauses between sentences, cut/paste/jump events, and backspaces) show the least consistency across tasks"*／ p.5: *"the features remain, essentially, measures of fluency"*
- Jadud 2006 pp.115–117（EQ）: 位置（*"+/−1 difference in line number"*）と本文（STRING-EDIT 距離）が要る。⚠️ 本文「9 で割る」と図の説明「最大 8」が食い違う
- Conijn 2021 p.487（S-notation）: *"{…} indicates an insertion, […] a deletion, and | a break, or the spatial location in the writing process where the insertion or deletion … started"*／ 入れ子: *"revisions embedded within revisions, embedded within revisions, etc."*
- Buschenhenke 2023 p.519（jump）: *"all changes in cursor position (except from 1 character forward … and 1 character backwards …) are identified as a 'jump'"*
- Kofune 2026 §V-C（査読前）: *"may partly capture early disengagement rather than struggle alone, especially because editing duration was the most important feature"*

### 見つからなかったもの
- キー種別系列の RQA / CRQA: 0 件 ／ 位置なしの D/I 往復回数・交替の「深さ」: 0 件 ／ 位置なしの入れ子の深さ: 0 件（`loop depth` 0 件）／ D/I 指標が誤打率の代理にすぎないことの直接検定: 0 件 ／ IME（未確定文字列の Backspace）を扱った文献: 0 件 ／ Watwin 原典: 未読

### サブエージェントの示唆（推論・文献の主張ではない）
1. `local_recurrence` は改名するか、「r = 0、m と窓長を明記したカテゴリ RQA」と定義し、打鍵数と中央値 IKI を共変量に入れる
2. `loop_depth_max` の「depth」は避ける。位置なしで言えるのは連続長と交替回数まで。Zhu 2019 は連続の方が効いたので、交替回数と最大連続長の両方を ablation へ
