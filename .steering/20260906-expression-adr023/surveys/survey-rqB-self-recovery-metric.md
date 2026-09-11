# RQ β — self_recovery_without_paste の粒度に合う先行（2026-09-06・第 3 ラウンド）

## 0. 進捗ログ（★ 1 ソースごとに追記）

- 2026-09-06 T0: 報告ファイル作成。skill/command 読了。探索開始。
- T1 angle 1/2/3/4 の初回検索完了。候補 9 件を identify:
  - Impasse-Driven problem solving (Cognition 2024, S0010027724000325, N=856)
  - Pre-Filtering Code Suggestions using Developer Behavioral Telemetry (arXiv 2511.18849)
  - CodeWatcher: IDE Telemetry Data Extraction Tool (arXiv 2510.11536)
  - PasteTrace (arXiv 2506.17355)
  - How to Catch Novice Programmers' Struggles (EDM 2022, Zenodo 6983260)
  - Predicting Struggling Students in CS1 (arXiv 2608.25769)
  - Feature Modulation to Improve Struggle Detection in Web Search (arXiv 2112.04711)
  - When To Help? Non-Intrusive Struggle Detection, older adults (CHI 2026 EA, 10.1145/3772363.3798756)
  - Smart Paste (arXiv 2510.03843)

- T2 arXiv API で 6 件の abstract 取得。★ 重要所見:
  - arXiv 2604.04721 (Liu, Christian, Dumbalska, Bakker, Dubey) N=1,222 RCT。「AI 支援は persistence を下げ、
    unassisted performance を損なう」。約 10 分の接触で発現。→ GSE を **支持**する側（反証 angle の逆）。
  - arXiv 2510.03843 (Smart Paste, Google): 「code is pasted 4 times more often than it is manually typed」。
    ★ paste は病理ではなく**既定**。指標設計の base rate 警告。
  - arXiv 2511.18849: **content-free** telemetry のみで suggestion acceptance を事前予測（never inspects code or prompts）。
    → (b) と angle 6 の直撃。acceptance rate 18.4%→34.2%。
  - arXiv 2608.25769: Breakthrough(BT)=過去提出が全部 0% → 最終提出が満点 / Fully Stuck(FS)。
    ★ 「自力で抜けた」のイベント的操作化だが **正誤ラベル必須**。→ ゼロ検算表の該当行。
  - arXiv 2510.11536 (CodeWatcher): copy-paste / CGT insertion / focus shift を IDE telemetry で記録。★ ただし content 保持。
  - arXiv 2506.17355 (PasteTrace): IDE 内で copy/paste/cut/delete/typing を実時間記録（剽窃検出用途）。

- T3 全文取得と操作化の確認:
  - **Odijk, White, Hassan Awadallah & Dumais, CIKM 2015** (DOI 10.1145/2806416.2806488): Bing ログ数百万セッション
    (2014-06 の 7 日間)。`Task` = 10 分以内 & 語/結果を共有する topically coherent sub-session。
    ★ struggling は **自動・content-free 近似** (最初の 2 クエリで結果を精査しない = クリック無し or dwell<10s の quick-back)。
    ⚠️ **成否 (successful / unsuccessful struggling task) は crowd 判定**。pivotal query も第三者ラベル。
  - **Liu, Christian, Dumbalska, Bakker & Dubey, COLM 2026** (arXiv 2604.04721v4): N=1,222 / 3 実験。
    ★ persistence = **skip ボタン押下率**（問題単位 = イベント単位・セッション内 10〜15 分・自動観測）。
    solve rate 0.57 (AI) vs 0.73 (control), Cohen's d=-0.42 [-0.66,-0.19];
    skip rate 0.20 vs 0.11, d=0.25 [0.02,0.48]。⚠️ **離散問題 + 正誤 + 明示 skip UI が前提**。
  - **van Daelen (A.C.L.), JEBO 2026** (DOI 10.1016/j.jebo.2026.107675, vol 248, 107675, CC-BY/hybrid):
    ⚠️ ScienceDirect 403 で全文未取得（→ §9）。書誌のみ Crossref/Unpaywall で確定。
  - **Ross & Arfini, Cognition 2024** (DOI 10.1016/j.cognition.2024.105746, vol 246, 105746): 全文 PDF 取得済 (London Met)。

- T4 ★★★ **本ラウンド最重要の発見**: **Alaboudi & LaToza 2021 "An Exploratory Study of Debugging Episodes"**
  (arXiv 2105.02162 / ESEC-FSE 系 preprint・データ figshare 公開)。
  - `debugging episode` = 「開発者が defect に最初に遭遇した時点」〜「修正した or **やめると決めた**時点」。
    ★ **イベント単位・セッション内・自然な実作業（live-streamed の職業開発者 11 名 / 15 セッション / 30 時間 /
    2137 debugging activities）**。粒度は GSE とほぼ一致。
  - ★ 活動コードに **`Consulting External Resources`**（ブラウザ / ローカル文書を開いて情報を探す）が**独立して存在**。
    → **episode 時間の avg 3% (sd ±10%, range 0–59%)**、**出現頻度 avg 1 (±2)/episode, range 0–16**、
    1 回 35s (±42s)。資源内訳 Doc 83% / Q&A 19% / Code example 9%。原因 API 説明 92% / エラー説明 8%。
  - 「プログラミング中に生じた新規 defect の **14%** は successful fix に至らなかった」。
  - debugging は **プログラミング 8 分ごと**に発生。episode 時間の 80% が 25 episodes に集中。
  - ⚠️★★★ **つまり「外部資源を参照せずに解決した episode の割合」は彼らのデータから計算可能だが、
    論文はその数値を報告していない**。★ これが GSE の `self_recovery_without_paste` に最も近い先行で、
    **やり残しがちょうど本指標の位置にある**。
  - ⚠️ 制約: **人手のビデオコーディング**（content-free 自動観測ではない）。かつ **LLM 以前 (2021)**。
- T4b その他: Alaboudi & LaToza の関連で **Theory of Troubleshooting** (arXiv 2602.10540, Starr & Storey, 27 名 GT 面接)、
  **programmer's block** (Schantong, Siegmund & Siegmund, EMSE 2024, DOI 10.1007/s10664-024-10542-9, vol 30)、
  **Echoes of AI** (arXiv 2507.00788, N=151, 2 相 RCT, Phase1 完了時間 -30.7% 中央値・Phase2 で保守性差なし)。
- T5 報告書を完成。取得ソース 20 / angle 6 / claim 8 / 否決 5 系統。

## 1. 動機

前ラウンドで機会保存の 3 指標のうち 2 本は先行に接地できた（`manual_contribution_ratio` = NIRVANA の
Human Contribution Ratio から借用、`paste_after_stuck_rate` = 構造のみ借用）。⚠️ **`self_recovery_without_paste`
だけが「時間粒度の合う先行が見つからず自前で定義するしかない」で止まっていた。**
加えて前ラウンドは **指標名そのものが危険**（[P126] の逐語判定により「助けの回避」を良い指標として扱うのは有害）
という判定を出しており、本ラウンドは **(1) 粒度の合う先行の有無** と **(2) 指標名・定義の是正先** の 2 つを同時に決める。

★ 本ラウンドが問う「粒度」は 4 条件の連言である:

| # | 条件 | 内容 |
|---|---|---|
| G1 | **時間** | セッション内（分〜十数分オーダー）。セッション末集計・週単位追跡は不可 |
| G2 | **単位** | 「行き詰まりイベント 1 件」に対する条件付き結果 |
| G3 | **測定** | content-free に自動観測できる行動。人手ラベル・事後自己申告に依存しない |
| G4 | **設定** | 開放的な実作業。正誤ラベル・問題境界・mastery 定義が存在しない |

---

## 2. 検証状態

- 探索 angle: **6**（① 認知科学の impasse ／ ② AI 支援の依存度の自動計測 ／ ③ copy-paste・provenance の自動検出 ／
  ④ debugging・struggle の行動ログ ／ ⑤ 反証（自力遂行を報酬にする害）／ ⑥ 方法論（イベント単位の条件付き率））
- 取得ソース: **20**（うち全文 PDF 取得 4 / abstract・書誌確定 14 / 書誌のみ 2）
- 抽出 claim: **8**
- 判定: `3-0` = 4 件 ／ `2-1` = 3 件（留保明記）／ 否決 = 1 件（+ 否決系統 4 件）
- ⚠️ Crossref / Unpaywall / Semantic Scholar で書誌を検算済み。捏造 DOI ゼロ。

---

## 3. gate 判定（下位問い (a)〜(d) ごとに温度 1 行）

| 問い | 温度 | 1 行判定 |
|---|---|---|
| **(a)** 「支援を受けずに自力で行き詰まりを抜けた」をイベント単位・セッション内で操作化した先行 | **PLAUSIBLE BUT UNPROVEN** | ★ **G1・G2・G4 を同時に満たす先行は 1 件だけ実在する**（Alaboudi & LaToza 2021 の debugging episode ＋ `Consulting External Resources` 活動コード）が、**G3 を満たさず（人手ビデオコーディング）、かつ肝心の「外部資源を参照せずに解決した episode の割合」を報告していない**。→ **借りられるのは枠だけ、数値は自前。** |
| **(b)** 「答えを写す／受領する」行動を content-free に検出・計数した先行 | **確定** | ★ 存在する。arXiv 2511.18849 は「**never inspects code or prompts**」と明記した pre-invocation telemetry のみで suggestion acceptance を予測し、Smart Paste / CodeWatcher / PasteTrace は paste・CGT 挿入イベントを IDE で実時間計数している。**条件付き受領率 (acceptance rate) は SE で標準的に報告される指標**（18.4→34.2% / 45% / 33–46%）。 |
| **(c)** 存在しないならどの条件を落とせば埋まるか | **確定** | ★ **落とすべき条件は G3（測定）1 つだけ**。G3 を人手ラベルに緩めた瞬間 (a) は埋まる。他の 3 条件はどれを落としても埋まるが、落とす必要がない。→ §5。 |
| **(d)** この型の指標に付随する既知の妥当性の脅威 | **確定 4 件 / 判定不能 2 件** | ★ 最大の脅威は「**解決**と**放棄**が content-free には同じに見える」。次に「paste は既定であって病理ではない（Google 社内で **手打ちの 4 倍** paste される）」と「impasse は解決率を 0.32→0.15 に落とす＝**低ベースレート**」。→ §4 C4/C7/C8。 |

> ★ **総合**: `self_recovery_without_paste` は **「借りる」と「自前」の中間**。
> **episode の定義**（開始 = 行き詰まり遭遇、終了 = 解決 **または** やめると決めた時点）と
> **受領イベントの content-free 検出**は先行から借りられる。
> **「自力で抜けた」という妥当化済みの二値指標は文献に存在しない（ゼロ）** ので、定義は自前。
> ⚠️ ただし自前で作るなら **「自力」を主語にしてはいけない**（§7）。

---

## 4. claim と 3 票検証

票の視点は **[内] 内的妥当性 / [外] GSE 設定への外挿 / [量] 効果量の頑健性**。

### C1 `2-1` — 行き詰まりイベント単位・セッション内・開放的実作業で「外部資源参照の有無」を episode ごとに記録した先行は実在する 【確定】
- 根拠: Alaboudi & LaToza 2021（arXiv 2105.02162）。`debugging episode` = 「defect に最初に遭遇した時点」〜
  「fix した **or やめると決めた**時点」。職業開発者 11 名 / 15 セッション / **30 時間** / **2137 debugging activities**
  / 1407 programming activities を 2 名がコードブック反復で体系的にコーディング。
  活動カテゴリに **`Consulting External Resources`**（ブラウザやローカル文書を開いて情報を探す）が独立して存在。
- [内] ○ — コードブックを反復合意で構築、2 名コーディング、除外規則（休憩・雑談）明示。
- [外] ○ — **職業開発者が実プロジェクト（Firefox / curl / Webpack / Alacritty 等）で行う開放的作業**。GSE の設定と一致。
- [量] △ — 開発者 11 名・単一研究・未追試。live-stream する開発者という**自己選択標本**。**2021 年＝ LLM 以前**。
- **判定 `2-1` 採用（留保: 標本の代表性と LLM 以前であること）**

### C2 `3-0` — その先行は「外部資源を参照せずに解決した episode の割合」を報告していない 【確定】
- 根拠: 本文・Table 4・Table 5 を全文取得して確認。報告されているのは
  `Consulting External Resources` の **episode 時間比 avg 3%（sd ±10%, range 0–59%）**、
  **頻度 avg 1（±2）/episode, range 0–16**、1 回 **35s（±42s）**、資源内訳 Doc 83% / Q&A 19% / Code example 9%、
  原因 API 説明 92% / エラー説明 8% ——「0 回の episode の割合」は**どこにも無い**。
- ★ 頻度が avg 1（±2）で range が 0 から始まる以上、**0 回の episode は相当数ある**が、その率は未公表。
- ★★★ **やり残しがちょうど GSE の指標の位置にある。**しかも **データセットは figshare で公開**されている。
- **判定 `3-0` 採用**

### C3 `3-0` — 「答えの受領」は content-free に自動検出・計数でき、条件付き受領率は SE の標準指標である 【確定】
- 根拠 1: arXiv 2511.18849 — 逐語 *"The filter operates solely on pre-invocation editor telemetry and
  **never inspects code or prompts**."* typing speed / file navigation / editing activity のみで acceptance を予測。
  production VS Code plugin・4 か月の naturalistic use で acceptance **18.4% → 34.2%**、低価値 LLM 呼び出しの **35%** を抑制。
- 根拠 2: Smart Paste（arXiv 2510.03843, Google）— paste は IDE イベントとして直接観測可能。deploy 後 acceptance **45%**。
- 根拠 3: CodeWatcher（arXiv 2510.11536）— *"insertions made by CGTs, deletions, copy-paste actions, and focus shifts"* を記録。
- 根拠 4: PasteTrace（arXiv 2506.17355）— IDE 内で copy / paste / cut / delete / typing を実時間記録。
- [内] ○ [外] ○（SE 実務・実 IDE）[量] ○（複数独立実装で一貫）
- **判定 `3-0` 採用** ★ **(b) は「構造だけ借りる」ではなく「そのまま借りられる」。**

### C4 `2-1` — paste は開発作業の**既定**であって病理ではない 【確定（方向）/ PLAUSIBLE（倍率）】
- 根拠: Smart Paste 逐語 *"we observe that **code is pasted 4 times more often than it is manually typed**"*（Google 社内）。
- [内] ○ — 社内テレメトリの実測。[外] △ — Google の巨大モノレポ特有の可能性。[量] ○ — 4× は方向が反転する余地が小さい。
- **判定 `2-1` 採用（留保: 単一企業のテレメトリ）**
- ★ 含意: **「paste が無かったこと」を美徳として数える指標は、正常な作業の大半を異常と呼ぶ。**
  → §7 で「受領なし」を *絶対率* ではなく **トリガー条件付きの相対率 / 生存時間**で書く根拠。

### C5 `2-1` — AI 支援は persistence を下げ、支援なし成績を落とす。10 分で発現する 【確定（現象）/ PLAUSIBLE（GSE 設定）】
- 根拠: Liu, Christian, Dumbalska, Bakker & Dubey（COLM 2026 / arXiv 2604.04721v4）。**N = 1,222**・RCT 3 本
  （算数 2・読解 1）。★ persistence = **"skip" ボタン押下率**（問題単位・自動観測・セッション内 10–15 分）。
  solve rate **0.57（AI）vs 0.73（control）**, t(305) = −3.64, P < 0.001, **Cohen's d = −0.42 [−0.66, −0.19]**;
  skip rate **0.20 vs 0.11**, t(305) = 2.16, P = 0.031, **d = 0.25 [0.02, 0.48]**。
  逐語: *"choosing to skip reflects a deliberate decision not to engage, making it a clear measure of
  motivation and persistence, **independent of ability**"*。
- [内] ○ — RCT・複数ドメインで追試・注意チェックによる除外。[外] △ — **離散問題・正誤あり・明示 skip UI** が前提で、
  GSE の開放的作業にはどれも無い。[量] ○ — d = 0.25〜0.42、CI が 0 を跨がない。
- **判定 `2-1` 採用（留保: 課題構造が GSE と異なる）**
- ★ 含意: GSE の問題意識（受領が自力遂行の機会を潰す）に**因果証拠**がついた。ただし **skip ボタンという affordance が
  無い開放的作業では、同じ構成概念を測る術がない**——これがまさに本 RQ の穴。

### C6 `3-0` — 「struggle → 成否」をセッション内・タスク単位で自動抽出した先行はあるが、**成否は人手ラベル**である 【確定】
- 根拠: Odijk, White, Hassan Awadallah & Dumais, CIKM 2015（DOI 10.1145/2806416.2806488）。
  Bing の実ログ数百万セッション（2014-06 の 7 日間）。`Session` = 30 分無操作で区切る。
  `Task` = 10 分以内かつ非ストップワード語 or 上位結果を共有する topically coherent sub-session。
  struggling の検出は **自動かつほぼ content-free**（最初の 2 クエリで結果を精査しない＝クリック無し、
  または **dwell < 10 秒**の quick-back クリック）。
  ⚠️ **successful / unsuccessful struggling task の区別も pivotal query も crowd worker の第三者判定**。
- [内] ○ [外] ○（web 検索は開放的で正誤ラベルが無い）[量] ○（数百万セッション）
- **判定 `3-0` 採用**
- ★ 含意 1: **G1・G2・G4 を満たし G3 を「トリガー検出だけ」満たす**先例。GSE の `p_stuck` 側の妥当性は補強される。
- ⚠️ 含意 2: **「抜けられたか」の側は自動化できず人手に落ちた**。★ これが (a) が埋まらない構造的理由。
- ⚠️ 含意 3: 検索では **「答えの受領」＝検索そのもの**なので、`without_paste` に相当する成分が原理的に存在しない。

### C7 `2-1` — impasse は解決率を大きく下げる（0.32 → 0.15）。よって「自力で抜けた」は**低ベースレート**事象である 【確定（現象）/ 留保（外挿）】
- 根拠: Ross & Arfini, Cognition 246:105746 (2024)。**4 本の事前登録実験・総 N = 856**（Exp1 は N = 125、
  OSF 事前登録 URL 本文中に明記）。Exp1 では 125 名中 **86 名 (0.69)** が stuck を報告。
  正答割合は **impasse 非経験 0.32 / impasse 経験 0.15**。正答までの latency は 57.1s vs 51.9s。
  impasse は **resolved / unresolved の二状態を取る**（★ ただし判定は**自己申告**）。
- [内] ○ — 事前登録・大 N・混合効果モデル。[外] △ — **1 分スケールの stumper 課題**で、正解が定義されている。
  [量] ○ — 0.32 vs 0.15 は大きく、4 実験で一貫。
- **判定 `2-1` 採用（留保: 課題スケールが GSE の分〜十数分と異なる）**
- ★ 含意: `self_recovery_without_paste` を**二値の率**で書くと、**分母が小さく分子がさらに小さい**。
  → 検出力が出ない。§7 案 B（生存時間）を推す最大の理由。

### C8 `3-0` — 「解決」と「放棄」は content-free 自動観測では区別できない 【確定（脅威として）】
- 根拠: Alaboudi & LaToza の episode 終端定義が逐語で *"A debugging episode ends when the developer
  **fixes the defect or decides to stop**"*。さらに *"For new defects created while programming, **14%** did not
  conclude with a successful fix, either because the developer had higher priority tasks ... or deferred the work until later"*。
- ★ **人手でビデオを見て発話を聞いても「やめると決めた」を終端に含めざるを得なかった**。
  打鍵ログだけを見る GSE には、この 14% を分離する情報が**原理的に無い**。
- **判定 `3-0` 採用** ★ **これが本指標の最大の妥当性の脅威。**

---

## 5. ⚠️ ゼロの検算表

**4 条件（G1 時間 / G2 単位 / G3 測定 / G4 設定）を同時に満たす先行は ★ ゼロ。**

| 落とした条件 | 埋まるか | 代表例 |
|---|---|---|
| **何も落とさない（G1+G2+G3+G4）** | ✗ **ゼロ** | 該当なし。★ ゼロはゼロ。 |
| **G3 のみ**: content-free 自動観測 → 人手ラベル可 | ○ **埋まる（あと一歩）** | **Alaboudi & LaToza 2021**（arXiv 2105.02162）: episode 単位・セッション内・開放的な職業実作業・`Consulting External Resources` を episode ごとに計数。⚠️ **ただし該当率そのものは未報告**（→ C2）。★ **落とす必要があるのはこの 1 条件だけ。** |
| **G4 のみ**: 開放的作業 → 正誤定義がある課題も可 | ○ 埋まる | **Liu et al. COLM 2026**（arXiv 2604.04721）: skip rate（問題単位・自動・10–15 分）。**arXiv 2608.25769**: Breakthrough（過去提出が全部 0% → 最終提出が満点）/ Fully Stuck の二分。 |
| **G3 の一部 ＋ G2 の粒度**: 成否だけ人手、単位はタスク（sub-session） | ○ 埋まる | **Odijk et al. CIKM 2015**（DOI 10.1145/2806416.2806488）: struggling task の successful / unsuccessful。トリガー検出は自動、成否は crowd。 |
| **G1 のみ**: セッション内 → セッション末集計でも可 | ○ 埋まる | **Bassner et al., CE:AI 2026**（DOI 10.1016/j.caeai.2025.100537, N = 275）: 試験得点。**Peng et al. 2023**（arXiv 2302.06590）: タスク完了時間 −55.8%。**Borg et al.**（arXiv 2507.00788, N = 151）: Phase1 完了時間 中央値 −30.7%。 |
| **G3 全部**: 自動観測 → 自己申告可 | ○ 埋まる | **Ross & Arfini, Cognition 2024**（DOI 10.1016/j.cognition.2024.105746）: impasse の resolved / unresolved を自己申告で二分。**Starr & Storey**（arXiv 2602.10540, 27 名面接）。 |
| **「答えの受領」→「助けの要求」でも可** | ○ 埋まる ⚠️ | **ITS help-seeking 系**（Hint Factory / HelpNeed Predictor arXiv 2010.04124、Student Productivity Model arXiv 2207.03025、Avoiding Help Avoidance arXiv 2009.13371、AI-Assisted Help-Seeking Trajectories arXiv 2606.22809）。⚠️★★★ **[P122] で否決済み**（正誤ラベル / 問題境界 / mastery の 3 つが GSE に無い）**かつ [P126] で「助けの回避を良い指標とすること自体が有害」と判定済み**。→ **新規候補として扱わない。**(d) の脅威としてのみ言及。 |
| **「自力で抜けた」→「受領行動そのものの計数」だけでよい** | ○ **埋まる（確定）** | **arXiv 2511.18849**（content-free acceptance 予測）/ **2510.03843** Smart Paste / **2510.11536** CodeWatcher / **2506.17355** PasteTrace。★ (b) 側は完全に借りられる。 |

**★ 検算の結論**: 穴は **G3（測定）に集中している**。
GSE が新規に作る必要があるのは「**行き詰まりイベント後に、答えの受領を挟まずに進行が再開したか**を
**人手ラベルなしで**判定する規則」ただ 1 つであり、
イベントの切り方（Alaboudi & LaToza）も受領の検出（arXiv 2511.18849 / Smart Paste）も先行から取れる。

---

## 6. ★ 登録候補（メインが `docs/references.md` へ採番・append する候補。★ 本 subagent は登録していない）

> ⚠️ 各候補に DOI / arXiv ID / 正規化 URL を付す。重複判定はメインが key で行うこと。

| # | 書誌 | key | N / 設計 | 主要な数値 | GSE への接地案 |
|---|---|---|---|---|---|
| B1 ★★★ | Alaboudi, A. & LaToza, T. D. (2021) *An Exploratory Study of Debugging Episodes.* | **arXiv:2105.02162**（DOI なし。データ: figshare `s/6c4026a941db49ea3de3`） | 職業開発者 11 名 / 15 セッション / 30 時間 / 2137 debugging activities（live-stream 観察・2 名の体系的コーディング） | debugging は **8 分ごと**に発生。`Consulting External Resources` = episode 時間の **avg 3%（±10%, 0–59%）**・**avg 1（±2）回/episode（0–16）**・1 回 **35s（±42s）**。新規 defect の **14%** は fix に至らず。episode 時間の 80% が 25 episodes に集中 | ★ **`self_recovery_without_paste` の episode 定義をここから借りる**（開始 = 行き詰まり遭遇 / 終了 = 解決 **または** 中止）。★ **やり残し = 「External Resources 0 回で終わった episode の割合」が未報告**。GSE がこれを content-free に自動で出せば**明確な差分**になる |
| B2 ★★★ | Al Awad, M. N., Ivanov, S. & Tikhonova, O. (2025) *Pre-Filtering Code Suggestions using Developer Behavioral Telemetry to Optimize LLM-Assisted Programming.* | **arXiv:2511.18849** | production VS Code plugin / 4 か月の naturalistic use | acceptance **18.4% → 34.2%**、低価値 LLM 呼び出しの **35%** を抑制 | ★ 逐語 *"operates solely on pre-invocation editor telemetry and **never inspects code or prompts**"* ——**content-free で受領を扱う先例**。GSE の `paste_after_stuck_rate`（トリガー条件付き受領率）の**方法論的親**として引く |
| B3 ★★ | Liu, G., Christian, B., Dumbalska, T., Bakker, M. A. & Dubey, R. (2026) *AI Assistance Reduces Persistence and Hurts Independent Performance.* COLM 2026 | **arXiv:2604.04721** (v4) | **N = 1,222**、RCT 3 本（算数 2 / 読解 1）、10–15 分セッション | solve rate 0.57 vs 0.73（**d = −0.42** [−0.66,−0.19]）／ skip rate 0.20 vs 0.11（**d = 0.25** [0.02,0.48]） | ★ GSE の前提（受領が自力遂行の機会を潰す）に**因果証拠**。★ 同時に「**skip ボタンという affordance があって初めて persistence が測れた**」ことが、開放的作業で同じものを測れない理由を示す |
| B4 ★★ | Odijk, D., White, R. W., Hassan Awadallah, A. & Dumais, S. T. (2015) *Struggling and Success in Web Search.* CIKM '15 | **DOI 10.1145/2806416.2806488** | Bing 実ログ数百万セッション（2014-06 の 7 日間）＋ crowd ラベル | struggling 判定 = 最初の 2 クエリでクリック無し or **dwell < 10 秒**の quick-back。task = 10 分以内 & 語/結果共有 | ★ **トリガー（行き詰まり）は自動で content-free に取れるが、成否は人手に落ちる**という構造の先例。GSE の `p_stuck` 側の妥当性補強＋ (a) が埋まらない理由の出典 |
| B5 ★★ | Ross, W. & Arfini, S. (2024) *Impasse-Driven problem solving: The multidimensional nature of feeling stuck.* Cognition 246:105746 | **DOI 10.1016/j.cognition.2024.105746** | **4 本の事前登録実験・総 N = 856**（Exp1 N = 125） | 0.69 が stuck を報告。正答割合 **0.32（impasse なし）vs 0.15（impasse あり）**。latency 57.1s vs 51.9s | ★ **impasse は resolved / unresolved の二状態を取る**という構成概念の一次出典。⚠️ **自力解決は低ベースレート**であることの根拠 → 二値率ではなく生存時間で書く理由（§7 案 B） |
| B6 ★★ | Nguyen, V. ほか (2025) *Smart Paste: Automatically Fixing Copy/Paste for Google Developers.* | **arXiv:2510.03843** | Google 社内テレメトリ・実配備 | ★ *"code is pasted **4 times more often** than it is manually typed"*。配備後 acceptance **45%**、社内全コードの 1% 超 | ★ **paste は既定であって病理ではない**——`manual_contribution_ratio` と `*_without_paste` の base rate 警告の出典 |
| B7 ★ | Basha, M., Ribeiro, A. M., Javahar, J., de Souza, C. R. B. & Rodríguez-Pérez, G. (2025) *CodeWatcher: IDE Telemetry Data Extraction Tool for Understanding Coding Interactions with LLMs.* | **arXiv:2510.11536**（OSF `j2kru`） | ツール論文（VS Code plugin + REST API + MongoDB） | *"insertions made by CGTs, deletions, copy-paste actions, and focus shifts"* を記録 | ★ 受領イベントの**計装の先例**。⚠️ ただし **content フィールドを保持する**ので GSE はそのまま採らない（`clipboard.rs` の文字数のみ設計との差分を書ける） |
| B8 ★ | McDonald, J., Robertson, S. & Peruma, A. (2025) *PasteTrace: A Single Source Plagiarism Detection Tool For Introductory Programming Courses.* | **arXiv:2506.17355**（データ DOI 10.6084/m9.figshare.27115852） | 導入プログラミング 2 コースで評価 | IDE 内で copy / paste / cut / delete / typing を実時間記録 | ★ 技術参照のみ。⚠️ **剽窃検出という設定**（不正の枠組み）は GSE と異なるので**指標の借用元にはしない** |
| B9 ★ | Kofune, Y., Shimari, K. & Matsumoto, K. (2026) *Predicting Struggling Students in CS1 Programming Using Keystroke-Level Editing Features.* | **arXiv:2608.25769** | CodeBench 2019-1・**507 名** | **Breakthrough** = 過去提出が全部 0% → 最終提出が満点 / **Fully Stuck** = 全部 0%。最早段階で AUROC 0.674（Combined）vs 0.575（ExecOnly） | ★ **「自力で抜けた」のイベント的操作化の唯一の明示例**。⚠️ ただし **正誤ラベル必須** → ゼロ検算表の G4 行の代表例 |
| B10 ★ | Tabarsi, B. T., Limke, A., Reichert, H., Qualls, R., Price, T., Martens, C. & Barnes, T. (2022) *How to Catch Novice Programmers' Struggles: Detecting Moments of Struggle in Open-Ended Block-Based Programming Projects using Trace Log Data.* CSEDM Workshop @ EDM'22 | **DOI 10.5281/zenodo.6983260** | 授業内 2 セッション（★ N 未確認 → §9） | trace log から struggle moment を自動検出する detector を作り、**学生アンケートで妥当性検証** | ★ **開放的（no fixed solution）な設定で moment 単位の struggle を自動検出**した先例。⚠️ **解決 / 未解決の区別も受領成分も無い** → (a) は埋めない |
| B11 ★ | Borg, M. ほか (2025) *Echoes of AI: Investigating the Downstream Effects of AI Assistants on Software Maintainability.* | **arXiv:2507.00788** (v3) | **N = 151**（95% が職業開発者）・2 相の統制実験（Phase2 は RCT） | Phase1: AI 使用で完了時間 **中央値 −30.7%**、常用者は **−55.9%**。Phase2: 保守性に**有意差なし**（Bayes 解析で効果は「あっても小さく非常に不確か」） | ⚠️ **反証側**: 「AI 由来コードは下流で害になる」は**支持されなかった**。→ GSE は「成果物の質が落ちる」とは主張できない。**機会保存**の主張に留める根拠 |
| B12 ★ | Bassner, P., Lenk-Ostendorf, B., Beinstingel, R., Wasner, T. & Krusche, S. (2026) *Less stress, better scores, same learning: The dissociation of performance and learning in AI-supported programming education.* Computers and Education: AI 10:100537 | **DOI 10.1016/j.caeai.2025.100537** | **N = 275**・入門プログラミング授業 | AI 群は演習得点が有意に高いが、**概念理解・コード読解には差なし**。無制限 AI は "comfort trap" | ⚠️ **短期パフォーマンス指標は学習を代理しない**。GSE がアウトカムに成績を置いてはいけない根拠（機会保存指標を選んだ判断の補強） |
| B13 ★ | Starr, A. & Storey, M.-A. (2026) *Theory of Troubleshooting: The Developer's Cognitive Experience of Overcoming Confusion.* | **arXiv:2602.10540** (v2) | 職業開発者 **27 名**・Constructivist Grounded Theory 面接 | troubleshooting は注意・作業記憶・メンタルモデルに持続的負荷をかけ、**認知的疲労**に至る | ★ 「行き詰まりからの回復」を**認知的コスト**として理論化。GSE の介入が「休ませる」方向である理由づけ |
| B14 ★ | Schantong, B., Siegmund, N. & Siegmund, J. (2024) *Toward a theory on programmer's block inspired by writer's block.* Empirical Software Engineering 30 | **DOI 10.1007/s10664-024-10542-9** | 理論構築（writer's block からの類推） | — （★ 詳細未取得 → §9） | ★ **「プログラマのブロック」を執筆研究から借りる**という GSE と同型の移送。writing head / coding head の共通構成概念の出典候補 |
| B15 ★ | Leijten, M. & Van Waes, L. (2013) *Keystroke Logging in Writing Research: Using Inputlog to Analyze and Visualize Writing Processes.* Written Communication 30(3):358–392 | **DOI 10.1177/0741088313491692** | 方法論論文 | **P-burst** = 2 秒以上の pause で切れる連続産出、**R-burst** = 推敲で切れるバースト。pause 閾値 200ms / 2s | ★ **「進行が再開した」を content-free に定義する既製の道具**。§7 の「再開」判定を **P-burst の再開**として書ける |
| B16 ★ | Parnin, C. & DeLine, R. (2010) *Evaluating cues for resuming interrupted programming tasks.* CHI '10, 93–102 | **DOI 10.1145/1753326.1753342** | 統制実験 | 中断後の再開手がかりの効果 | ★ **resumption を局所（イベント直後）で測る**方法論。§7 案 B の直系 |
| B17 ★ | Altmann, E. M. & Trafton, J. G. (2004) *Task Interruption: Resumption Lag and the Role of Cues.* Proc. CogSci 2004 | **DOI なし** / `https://www.interruptions.net/literature/Altmann-CogSci04.pdf` | 統制実験 | **resumption lag** = 「タスク画面が戻ってから最初のクリック / キー押下まで」。★ 逐語的に *local measure, taken immediately after every interruption*（対して time-on-task は global measure） | ★★★ **「イベント直後の局所測度」対「セッション集計の大域測度」という区別の一次出典**。GSE がセッション末集計を拒む根拠として引ける |
| B18 ★ | van Daelen, A. C. L. (2026) *Running against windmills: Costly perseverance in long- and short-term goal pursuit.* J. Econ. Behavior & Organization 248:107675 | **DOI 10.1016/j.jebo.2026.107675**（CC-BY / hybrid OA） | ⚠️ **全文未取得（ScienceDirect 403）→ §9** | ⚠️ 未確認 | ⚠️ **反証 angle の本命候補だが未検証**。「perseverance は exploration 課題でこそ高くつく」という方向は二次情報のみ。★ **メインは全文を取るまで登録を保留すべき** |
| B19 ○ | Peng, S., Kalliamvakou, E., Cihon, P. & Demirer, M. (2023) *The Impact of AI on Developer Productivity: Evidence from GitHub Copilot.* | **arXiv:2302.06590** | 職業開発者 95 名 RCT | 完了時間 **−55.8%** | ○ 文脈（受領の便益側）。★ 対称性のために置く |
| B20 ○ | Hassan Awadallah, A., White, R. W., Dumais, S. T. & Wang, Y.-M. (2014) *Struggling or Exploring? Disambiguating Long Search Sessions.* WSDM '14 | **DOI 10.1145/2556195.2556221**（★ 未検算 → §9） | Bing ログ | 長いセッションの「行き詰まり」と「探索」の弁別 | ⚠️ **「長い ≠ 行き詰まり」**——GSE の `p_stuck` が沈黙・長時間を stuck と読む場合の直接的な脅威 |

---

## 7. ★★★ 指標名と定義の提案

### 7.0 現行名 `self_recovery_without_paste` の 3 つの欠陥

| # | 欠陥 | 根拠 |
|---|---|---|
| N1 | **`self_` が「助けの回避」を美徳として名指ししている** | ⚠️ [P126] 逐語: *"students who need help will be best served by **immediately seeking help**, rather than attempting to solve the problem on their own first"*。→ 名前が repo の既決判定と正面衝突する |
| N2 | **`recovery` が「解決」を含意するが、content-free には放棄と区別できない** | C8。Alaboudi & LaToza の episode 終端は逐語で *"fixes the defect **or decides to stop**"*、新規 defect の **14%** は fix に至らない（優先度・先送り）。★ 人手でビデオと発話を見てもこの 2 つは分離しきれなかった |
| N3 | **`without_paste` が「不在」を主語にしており、base rate を誤る** | C4。Google 社内では **paste は手打ちの 4 倍**。「paste しなかった」を数えると正常な作業の大半が異常になる |

### 7.1 案 A（副・報告用の二値）— `stuck_exit_without_receipt`

> **定義**: 行き詰まりトリガー `t0`（`p_stuck` が閾値を上抜けた時刻）から窓 `W`（既定 10 分）以内に、
> **受領イベントを 1 件も挟まずに**「実質的な産出の再開」が観測された行き詰まりイベントの割合。

- **何を観測すれば計算できるか**
  1. **トリガー** `t0`: 既存の `p_stuck`（`analysis/engine.rs`）。★ B4 の先例に倣い、トリガー検出は自動・content-free でよい。
  2. **受領イベント** `receipt`: 「閾値超の挿入」。GSE で content-free に取れるのは
     `clipboard.rs`（文字数のみ）と `key_gate.rs` の打鍵カウンタ。
     → **1 イベントで `K` 文字以上（既定 `K = 40`）が挿入され、その挿入が打鍵由来でない**ものを `receipt` と定義する。
     ★ B2 の逐語 *"never inspects code or prompts"* と同じ立場（中身を見ない）。
  3. **再開**: **P-burst の再開**（B15）。`t0` 以降で、**2 秒以上の pause で区切られた連続打鍵バースト**が
     `L` 文字（既定 `L = 60`）以上続いた最初の時点。
- **壊れる条件**
  - ⚠️ **放棄と再開の混同**（N2 / C8）: 別ファイル・別タスクへ移って打鍵しても「再開」に見える。
    → `observe.rs` のフォーカス遷移で「同一アプリ・同一文書に留まっているか」を副条件に置くしかないが、**完全には解けない**。
  - ⚠️ **迂回**: スマホで答えを見て手で打ち直すと `receipt` が立たず「自力」に見える。★ 学術的な一次証拠は見つからず（→ §8）。
  - ⚠️ **低ベースレート**（C7）: impasse 経験時の正答率は 0.15。分子が小さく、被験者あたりのイベント数が要る。
  - ⚠️ `K` / `L` / `W` の 3 閾値がすべて**恣意的**。★ 感度分析を PreReg に書かないと p-hacking になる。

### 7.2 案 B（★ 推奨・主指標）— `receipt_free_resumption`（生存時間 / 競合リスク）

> **定義**: 行き詰まりトリガー `t0` からの経過時間を時間軸に取り、
> **競合する 2 つの終端イベント**——(i) **受領なしの産出再開**（案 A の「再開」）、(ii) **受領イベント**——の
> どちらが先に起きるかを **competing risks の生存時間解析**で推定する。
> 報告値は「`t0` から 5 分 / 10 分時点における **受領なし再開の累積発生関数 (CIF)**」。

- **なぜこちらを主にするか**
  1. ★ **C7（低ベースレート）を回避する。** 二値の率は分子が小さく検出力が出ないが、
     生存時間は「いつ起きたか」の情報も使うので、同じイベント数で検出力が高い。
  2. ★ **N2（解決 vs 放棄）を「打ち切り (censoring)」として明示的に扱える。**
     窓内にどちらも起きなかった episode は「打ち切り」であって「失敗」ではない。
     → **「やめた」を「自力で抜けられなかった」に**押し込まずに済む。★ ここが案 A との決定的な差。
  3. ★ **B17（resumption lag）の直系**。逐語で *local measure, taken immediately after every interruption* と
     位置づけられた測度型であり、GSE がセッション末集計を拒む理由がそのまま出典になる。
  4. ★ 介入効果は **CIF の差**または **cause-specific hazard ratio** で書ける。
     介入群で「受領の hazard が下がる」ことと「再開の hazard が上がる」ことを**別々に**言える。
- **壊れる条件**
  - ⚠️ **打ち切りが多すぎると推定が不安定**。離席・セッション終了・アプリ切り替えがすべて打ち切りになる。
    → `liveness.rs` / `observe.rs` の離席判定が effectively 打ち切り規則になるので、**その規則が指標の定義の一部**になる。
  - ⚠️ **競合リスクの独立性仮定**が怪しい（受領しやすい人ほど再開もしやすい可能性）。→ 感度分析が要る。
  - ⚠️ 事前登録で **「5 分 / 10 分」の 2 点だけを主要評価**に固定しないと、時点選択の自由度が残る。

### 7.3 案 C（保守案・新構成概念を作らない）— `receipt_after_stuck_rate` の**補集合として言及するだけ**

> **定義**: 独立指標を新設せず、既存 `paste_after_stuck_rate` を
> **`receipt_after_stuck_rate`（受領率）へ改名**し、`self_recovery_*` は **廃止**する。
> 「自力で抜けた」は主張せず、「受領しなかった」だけを報告する。

- **利点**: ★ [P126] の罠を**完全に**回避する（「助けの回避」も「自力解決」も一切主張しない）。
  ★ 新しい構成概念を発明しないので、妥当化の負債がゼロ。★ (b) は先行から丸ごと借りられる（C3）ので **温度が `確定` のまま**。
- **欠点**: ⚠️ 「進行できたか」を一切測れない。受領せずに**止まった**ケースと受領せずに**進んだ**ケースが同じ値になる。
  → **機会保存の主張（作業が進んだ）ができなくなり、機会の *不使用* しか言えない**。

### 7.4 ★ 推奨

| 位置づけ | 採るもの | 理由 |
|---|---|---|
| **主要評価** | **案 B `receipt_free_resumption`**（5 分 / 10 分 CIF） | 低ベースレート（C7）と 解決/放棄の分離不能（C8）の両方に、**打ち切りという既製の統計装置**で応える唯一の案 |
| **副次・可読性** | **案 A `stuck_exit_without_receipt`**（二値率） | 論文・報告で読みやすい。★ ただし**主要評価にはしない** |
| **フォールバック** | **案 C** | ⚠️ 較正で案 B の打ち切り率が過大（例: 60% 超）だった場合、**案 B を降ろして案 C に退避**する |

★ **命名の原則（3 つとも `self` を含まない）**:
1. ⚠️ **`self_` を落とす** — [P126]。「自力」を美徳として名指ししない。
2. ⚠️ **`paste` ではなく `receipt`** — 実装手段（クリップボード）ではなく**構成概念（答えの受領）**を名前にする。
   ★ CGT 挿入 / suggestion accept / paste はすべて `receipt` の実装。B7 の CodeWatcher が
   *"insertions made by CGTs, deletions, **copy-paste actions**"* を並べて記録しているのと同じ抽象度。
3. ⚠️ **`recovery` ではなく `resumption`** — 「治った」ではなく「**再開した**」。
   ★ B17 の resumption lag と語彙を揃えることで、「解決したか」を主張しない立場が名前に埋め込まれる。

---

## 8. ⚠️ 否決リスト

| 主張 / 候補 | 票 | 否決理由 |
|---|---|---|
| **ITS の help-seeking 研究を `self_recovery_without_paste` の接地先にする**（Hint Factory / HelpNeed Predictor arXiv 2010.04124、Student Productivity Model arXiv 2207.03025、Avoiding Help Avoidance arXiv 2009.13371、AI-Assisted Help-Seeking Trajectories arXiv 2606.22809、wheel-spinning） | `0-3` | ⚠️★★★ **[P122] で否決済み**（ITS には正誤ラベル / 問題境界 / mastery があり、GSE には 3 つとも無い）。**かつ [P126] で「助けの回避を良い指標として扱うこと自体が有害」と判定済み**。★ 本ラウンドの検索でも 4 件ヒットしたが **全件、新規候補としては否決**。§5 と (d) の脅威としてのみ言及する |
| **剽窃検出の枠組み（PasteTrace の用途 / Crossley et al. EDM 2024 の keystroke plagiarism detection）を指標の借用元にする** | `1-2` | ⚠️ 技術（paste の実時間検出）は借りられるが、**「不正」という規範枠**が GSE の設定（正誤も不正も定義されない自然作業）と両立しない。★ 被験者に対する意味づけが変わる（`data-privacy` 上も危険）。→ **技術参照のみ**（B8） |
| **web search の struggle 予測モデル（Feature Modulation, arXiv 2112.04711）を候補にする** | `1-2` | ⚠️ **予測タスクであって指標の操作的定義ではない**。GSE が借りたいのは「何を数えるか」であって「どう当てるか」ではない。★ B4（CIKM 2015）が同じ系統の**定義側**を押さえているので冗長 |
| **Goodhart / metric gaming（指標を報酬にすると迂回される）を確定した脅威として書く** | 判定不能 | ⚠️ **学術的な一次資料が見つからなかった**（ヒットは全てブログ・wiki 等の grey literature）。★ 脅威としては現実的だが、**証拠ゼロなので「証拠なし」と書く**（§7.1 / §9） |
| **van Daelen (JEBO 2026) を反証証拠として採用する** | 判定不能 | ⚠️ **全文が取れていない**（ScienceDirect 403。CC-BY なのに）。二次情報の「exploration 課題では perseverance が高くつく」という方向だけでは 3 票にかけられない。★ **メインは全文入手まで登録を保留すべき**（B18） |

---

## 9. ⚠️ 取得できなかったもの

| 対象 | 症状 | 試した経路 | 状態 |
|---|---|---|---|
| van Daelen, JEBO 248:107675 (2026) 全文 | ScienceDirect **403**（`/pdfft` も HTML を返す） | WebFetch → 403 / curl+UA → 403 / **Unpaywall** → OA location が publisher DOI のみ / **Semantic Scholar** → `abstract: null` | ⚠️ **未取得**。書誌のみ確定（Crossref + Unpaywall で CC-BY hybrid と確認）。★ **反証 angle の本命が空いたまま** |
| Bassner et al., CE:AI 10:100537 (2026) 全文 | ScienceDirect ペイウォール | Crossref で書誌確定 / 検索結果の要約のみ | 部分取得（N = 275・主要結論のみ） |
| Tabarsi et al., CSEDM 2022 の **N** と「struggle が解決したか」の扱い | Zenodo ページの WebFetch 要約のみ。PDF 本体は未取得 | WebFetch（Zenodo record） | 部分取得。★ **N 未確認**のまま登録候補に入れている（B10）——メインは登録時に PDF を当たること |
| Hassan Awadallah et al., WSDM 2014 の DOI | Crossref 未検算（時間予算） | — | ⚠️ **B20 の DOI は未検算**。メインは登録前に Crossref で確認すること |
| Altmann & Trafton, CogSci 2004 の DOI | CogSci proceedings は DOI を持たない | Crossref → 別論文がヒット | **DOI なし**と確定。URL で登録するしかない（B17） |
| Alaboudi & LaToza のデータから「External Resources 0 回の episode 率」を実際に計算すること | figshare データセットは公開されている（`s/6c4026a941db49ea3de3`）が、本ラウンドの予算外 | — | ⚠️ **未実施**。★ **次ラウンド最優先の「やり残し」**——この 1 数値が取れれば、GSE の主要指標に **文献由来のベースラインが付く** |

---

## ★ 次ラウンドへの「やり残し」（`_index.md` 用の 1 行素材）

> `self_recovery_without_paste` は **枠（episode 定義・受領検出）は借りられるが、二値指標そのものは文献にゼロ**。
> ★ 埋めるべき穴は **G3（content-free 自動観測）1 つだけ**。
> ★ 最優先は **Alaboudi & LaToza の公開データ（figshare）から「External Resources 0 回で終わった debugging episode の割合」を
> 実際に計算する**こと（論文は未報告）。次点は **van Daelen (JEBO 2026) の全文入手**（反証 angle が空いている）。
