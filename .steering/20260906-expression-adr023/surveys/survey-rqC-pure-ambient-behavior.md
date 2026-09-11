# RQ γ — 純アンビエント（非数値）× 行動指標（2026-09-06・第 3 ラウンド）

## 0. 進捗ログ（★ 1 ソースごとに追記）

- 2026-09-06 開始。報告ファイル初期化。
- 2026-09-06 Crossref 検算: **PUC 誌に Kluckner の論文は 0 件**（`filter=issn:1617-4909` + `query.author=Kluckner` → total-results 0）。伝聞書誌は誤り。2013 年の該当は LNCS 2 本。
- 2026-09-06 **Kluckner et al. 2013 (AmI, LNCS 8309) を GREEN OA で全文取得**（S2 経由 → jschrammel.files.wordpress.com）。→ §4 に顛末。
- 2026-09-06 **Dahlinger et al. CHI 2018（抽象 vs 具体 eco-driving RCT）を全文取得**（Unpaywall=closed だが St.Gallen Alexandria の bitstream が公開）。→ §7 候補 1。
- 2026-09-06 同一グループの **Dahlinger, Tiefenbeck, ... , Wortmann (2018) *Transp. Res. Part D* 65:375-386「numerical vs. symbolic」** を Crossref で確定（DOI 10.1016/j.trd.2018.09.013）。⚠️ Tiefenbeck が共著 ＝ [P314] と同一系列。
- 2026-09-06 **Maan, Merkus, Ham & Midden (2011) *Energy Efficiency* 4(2):175-183 を全文取得**（Unpaywall hybrid OA）。★ **数値を一切含まない照明色のみ vs 数値** の直接比較。→ §7 候補 3。
- 2026-09-06 Ham & Midden (2010) Persuasive LNCS 6137 (DOI 10.1007/978-3-642-13226-1_14) は **CLOSED**（Unpaywall/S2 とも）。→ §9。
- 2026-09-06 UbiFit「Flowers or a Robot Army?」(UbiComp 2008, DOI 10.1145/1409635.1409644) 全文取得（pensivepuffin 公開）。★ garden 表示は**数値ゼロ**、かつ 3 群設計で display のみを分離。→ §7 候補 4。
- 2026-09-06 ⚠️ **WebSearch の要約が誤りだった**: 「numeric > graphical」と書かれたが、原典 Sohn & Nam (2015) は逐語 **"the graphical representation ... was significantly more effective than the numeric representation"**。→ 一次で検算した。
- 2026-09-06 FAB study (Godino et al. 2013, PLoS ONE, DOI 10.1371/journal.pone.0075398) を Europe PMC で確認。N=466 RCT・客観 PA で **null**。→ §7 反証候補。
- 2026-09-06 Sohn & Nam 経由で **UpStream (Kuznetsov & Paulos, CHI 2010)** を発見。二色のみの抽象表示 vs 数値 × 客観水消費。→ 最重要の追加候補。
- 2026-09-06 反証 angle: Börner et al. (2015) / FAB (N=466) / ロック画面壁紙 RCT (N=60, 事前登録) の 3 件の null を確定。
- 2026-09-06 angle 4（アンビエント音）: **GSE 関連の実例ゼロ**。見つかるのは自転車・Parkinson 等の**リアルタイム運動学習ループ**で、行動変容の常在フィードバックではない。→ §6 に記載。
- 2026-09-06 探索終了。取得ソース 15 / angle 6。

---

## 1. 動機（★ [P314] のハイブリッド性への留保）

[P314] Tiefenbeck et al. (2018) の 22% 削減は「数値 ＋ アイコン」のハイブリッド表示で得られた。
GSE の層 A は**数値・文字を一切出さない抽象符号のみ**であり、[P313]/[P314]/[V136] のどれも
「純アンビエントで客観行動が動いた」ことを示していない。本ラウンドはその穴を埋めに行く。

## 2. 検証状態

| 項目 | 数 |
|---|---|
| 取得ソース | **15**（うち**全文 7**・abstract/書誌確定 5・取得不能 3） |
| 探索 angle | **6**（非数値抽象×客観行動 / 表示形式の直接比較 / UbiFit 系 / アンビエント音 / 反証 / 通知の抽象度） |
| 抽出 claim | 4 |
| 3 票検証 | confirmed 3（うち 3-0 が 2・2-1 が 1）/ 分割 1（下位問いで温度が真逆） |
| 否決 | 3 |

⚠️ **一次で検算して覆した二次情報 2 件**（§8 参照）。WebSearch 要約と孫引きの両方が誤っていた。

---

## 3. gate 判定（下位問いごとの温度）

| 下位問い | 温度 | 1 行 |
|---|---|---|
| **(a)** 「数値を出さない抽象符号のみ」で**客観行動**を主要アウトカムに測った研究はあるか | ★ **分割する** | **ラボ/模擬環境なら `確定`**（Maan 2011: 照明色のみ・21% 削減・p=.01）。**実フィールド × 完全客観 × 数値ゼロ**は **`判定不能`（該当 0 件）** |
| **(b)** 効果量は。数値つき表示との**直接比較**はあるか | `確定`（2-1） | 直接比較は **5 本**存在し、方向は一貫して「抽象側が勝つ」。最良は Dahlinger TRD 2018（RCT・N=62・245,819 km・symbolic **−0.231 l/100km, p<.01** / numerical **−0.006, n.s.**）。⚠️ **ただしその symbolic 条件にも数値が残っている** |
| **(c)** 存在しないなら、どの条件を落とせば埋まるか | — | §6 の検算表。**「実フィールド」を落とす**か**「完全客観」を落とす**かのどちらか 1 つで埋まる。**2 つ同時に保つと 0 件**である |
| **(d)** 「抽象符号のみ」が効かなかった/劣ったという反証はあるか | `確定`（3-0） | ある。**逆効果**（UpStream 公共蛇口: 純 traffic light で使用時間 **+133.5%, p<0.001**）・**null 3 件**（Börner 2015 / FAB N=466 / ロック画面壁紙 RCT N=60 事前登録） |

★ **本 RQ の一行結論**: 「純アンビエントで行動が動いた」は **`PLAUSIBLE BUT UNPROVEN`**。
**動いた実例はあるが、いずれも (i) ラボ模擬か (ii) 自己申告混入か (iii) 有意に届かないかのどれかを含む。**
そして **[P314] のハイブリッド性への留保は、本ラウンドで *解消されず、むしろ補強された*。**

---

## 4. ★★★ Kluckner et al. (2013) の顛末

### 4.1 書誌の検算（★ 伝聞は誤りだった）

| 項目 | 伝聞 | Crossref による確定 |
|---|---|---|
| 誌名 | *Personal and Ubiquitous Computing* | ❌ **誤り**。`https://api.crossref.org/works?filter=issn:1617-4909&query.author=Kluckner` → **total-results = 0**（PUC に Kluckner の論文は存在しない） |
| 実体 | — | ✅ 2013 年の該当は **LNCS 収録の 2 本** |

確定した 2 本:

1. **Kluckner, P. M., Weiss, A., Schrammel, J., & Tscheligi, M. (2013). "Exploring Persuasion in the Home:
   Results of a Long-Term Study on Energy Consumption Behavior." In *Ambient Intelligence (AmI 2013)*,
   LNCS 8309, pp. 150–165.** DOI: `10.1007/978-3-319-03647-2_11`
   → ★ **全文取得成功**（Unpaywall は closed だが、Semantic Scholar が GREEN OA を保持:
   `https://jschrammel.files.wordpress.com/2010/10/ami13_kluckner-et-al-_cameraready.pdf` — 共著者 Schrammel の
   セルフアーカイブ。16 ページ camera-ready 全文）
2. Kluckner, P. M., Weiss, A., & Tscheligi, M. (2013). "Where to Place My Ambient Persuasive Display?
   Insights from a Six-Month Study." In *Persuasive Technology 2013*, LNCS 7822, pp. 110–115.
   DOI: `10.1007/978-3-642-37157-8_14` → ⚠️ **取得不能**（Unpaywall `is_oa:false / closed`、
   Semantic Scholar `openAccessPdf.status = CLOSED`、Springer ペイウォール）。§9 に記載。

### 4.2 ★ 指示された 3 点の逐語確認（本命 = AmI 2013）

**(1) 数値を伴わない表示か → ❌ NO。ハイブリッドである。**

装置は **FORE-Watch**（タブレット常設のキッチン時計型アンビエント表示）。逐語:

> "we decided to focus on the familiar and well-known system of the **traffic light system with red, yellow,
> green**, to adjust action. Due to the fact that this color code was recognized unconsciously and intuitively,
> there is little cognitive demand."

ここまでは純色符号だが、**同じ装置の feedback view が数値を出す**。逐語:

> "**Average Consumption.** The display shows the average electricity consumption (**in KW/h units**) over a
> week, the day before is labeled as 'yesterday'. The dot represents the average from baseline start."
> "**Consumption per Phase.** … It uses two modalities of feedback electricity consumption (1) **bar chart**,
> which is divided into a week … and (2) **reward icon** for honor that are three levels of performances
> (gray-shades for good, very good, excellent)."

さらに forecast view 自体が「**キッチン時計**」であり、逐語 "the device is based on a kitchen clock and
**shows additional information to the time of day**" — 時刻（数字）を常時出す。
→ ★ **色符号 ＋ kWh 数値 ＋ 棒グラフ ＋ 時刻。[P314] と同型のハイブリッドであり、GSE 層 A への外挿は不可。**

**(2) アウトカムは客観行動か → △ 客観データは取ったが、主要アウトカムは自己申告である。**

スマートメータで 15 分粒度の kWh を 7 か月取得している（客観）。しかし論文の RQ は逐語
"Can an **attitudinal (behavior) change** be observed …" であり、結果節の大半 (§4.1) は
10 種の心理尺度（INTUI / PANAS / SIM / UTAUT / TAM2 / AttrakDiff2 / TRUST 等）である。
行動の節 (§4.2) は 1 段落しかない。

**(3) 効果量は → ✗ 報告されていない。数値の効果量はゼロ件。**

逐語:

> "The analysis of the KW/h-consumption of the two experimental groups resulted that **a low correlation**
> between consumption behavior and the dynamic group exists; **a weak trend** is presented for the static group."
> "there is **small significant correlation** by the dynamic group and the static group presents **a tendency**."

★ **係数も、削減率も、CI も、検定統計量も一切ない。** さらに著者自身が内的妥当性を否定する逐語:

> "the **absence of real-time consumption data**, the **non-presented data from the pre-phase of the study** …
> the evidence of effects for the static group is **particularly difficult**."

**統制群は存在しない**（2 群はどちらも FORE-Watch を見る「静的 forecast vs 動的 forecast」の比較であり、
表示なし群がない）。被験者 24 世帯は逐語 "24 **energy consultants** and four of their partners" =
**エネルギー会社の相談員本人**であり、外的妥当性は極めて限定的。

### 4.3 判定

**Kluckner et al. (2013) は RQ γ の「純アンビエント × 客観行動」の実例には *ならない*。**
理由は 3 つとも独立に致命的: (i) 表示がハイブリッド、(ii) 主要アウトカムが態度尺度、
(iii) 効果量・統制群なし。→ 登録候補としては**否決**（§8）。


---

## 5. claim と 3 票検証

票の視点: **① 内的妥当性 / ② GSE 層 A への外挿 / ③ 効果量の頑健性（出版バイアス・追試）**

### C1a. 「数値を一切含まない抽象符号のみ」の表示で、客観的に測られた行動が有意に動いた研究は存在する **[2-1]**

根拠: Maan et al. 2011 — 壁に投影する LED ランプの**色だけ**（緑↔赤）。数値表示は一切なし。
逐語 "participants who had received lighting feedback used a lower amount of energy on average on the tasks
(M=544 W, SD=208) than participants who received numerical feedback (M=692 W, SD=202), F(1, 53)=7.16, p=0.01"
→ **21% 低い**。従属変数は 6 室の熱損失から計算した消費電力（＝設定行動から機械的に決まる客観値）。

| 票 | 判定 | 理由 |
|---|---|---|
| ① 内的妥当性 | ○ | 2×2 被験者間・無作為割付。認知負荷の交互作用も予測どおり（数値のみ負荷で処理が遅延、照明は不変） |
| ② 層 A への外挿 | ✗ | ⚠️ **「仮想セントラルヒーティング画面」を 30 分操作するラボ課題**。実消費ではない。かつ色は**制御対象の量そのもの**を符号化し規範方向（緑=善）が自明。GSE 層 A の「行き詰まり」には規範的最適も直後の制御ループも無い |
| ③ 頑健性 | △ | N=57（各セル ≈14）で 21% は大きすぎる（winner's curse の疑い）。★ **独立追試を発見できなかった**。⚠️ **no-feedback 統制群が無い**ので「純アンビエントが *何もしないより* 効く」ことは示していない（示したのは「数値より効く」だけ） |

→ **2-1 confirmed。留保: ラボ模擬・統制群なし・追試なし。**

### C1b. 「実フィールド × 完全に客観的な行動 × 数値ゼロの表示」の実例は存在する **[0-3 → 否決 = ゼロ]**

★ **コーパス中に 0 件。** 最も近い 2 本がどちらも条件を 1 つ落としている:

- **UbiFit**（Consolvo et al. UbiComp 2008, DOI 10.1145/1409635.1409644）: 表示は**数値ゼロ**（花＝活動・蝶＝目標達成、逐語
  "the garden has no wilting flowers, weeds, or stormy sky" / 未達なら "the garden will simply not have a butterfly"）。
  フィールド 3 か月・N=28・3 群で **display のみを分離**（interactive application は全群にある）。
  結果は交互作用 **F(1,312)=6.51, p=.0112**（表示あり群は活動時間を維持、なし群は減少）。
  ⚠️ **落ちている条件 = 完全客観**: アウトカムの Activity Duration/Count は **MSP センサ推論と手入力ジャーナルの混合**であり、
  自己申告が混入する。⚠️ **Activity Count は p=.095 で有意に届かない。** N=28/3 群。
- **UpStream**（Kuznetsov & Paulos CHI 2010, DOI 10.1145/1753326.1753604）: ambient orb は**数値ゼロ**（traffic light のみ）、
  アウトカムはセンサ実測ガロン ＝ **完全客観**。⚠️ **落ちている条件 = 有意性**: N=4 世帯・各相 5–12 回で、
  逐語 "average usage decreased by more than 1.5 gallons for all participants, with two of the decreases being
  **marginally significant** (2.1 gallons, **p=0.09** and 1.7 gallons, **p=0.11**)" → **どの群も p>.05**。

→ **ゼロはゼロと書く。**

### C2. 抽象/象徴表示は数値表示より客観行動を動かす（直接比較） **[2-1]**

直接比較 5 本、方向は**一貫して抽象側**:

| 出典 | 設計 | 結果 |
|---|---|---|
| Dahlinger et al. 2018 TRD | RCT・N=62・245,819 km・265,939 区間・10 週 | symbolic **β=−0.231 l/100km (SE .106), p<.01**（≈ **2–3%**）/ numerical **β=−0.006, n.s.** |
| Dahlinger et al. 2018 CHI | ★ **同一試験の別解析** | abstract **β=−.33 (SE .14), p<.05** / concrete **+.07, n.s.** |
| Maan et al. 2011 | ラボ RCT・N=57 | 照明のみが数値より **21%** 低消費, p=.01 |
| Sohn & Nam 2015 | ラボ・N=40・32 デザイン | 逐語 "the **graphical** representation … was significantly more effective than the **numeric**" |
| Kuznetsov & Paulos 2010 | フィールド・N=4 世帯 | ambient は全員減、numeric は 2/4 のみ。⚠️ **いずれも有意でない** |

| 票 | 判定 | 理由 |
|---|---|---|
| ① 内的妥当性 | ○ | TRD 版は無作為化のバランス確認済み（baseline 燃費 F=0.02, **p=0.98**）、個体固定効果＋道路属性統制。CHI 版は baseline が不均衡（abstract 群が有意に高燃費 p=.002）で、TRD 版がそれを是正している |
| ② 層 A への外挿 | ✗ | ⚠️ **5 本すべてが「消費量」ドメイン**（燃料・暖房・水）。符号が指す量が本人の直接制御下にあり、望ましい方向が一意。GSE 層 A（行き詰まり度）はどちらも満たさない |
| ③ 頑健性 | △ | ⚠️ **TRD と CHI は独立追試ではなく同一フィールド試験**。⚠️ **共変量なしの Model 1 では symbolic は −0.024 で非有意**であり、効果は `Day` 投入後にのみ出現する。⚠️ 著者自身が交絡を明記: 逐語 "the eco-tree also used a **moving average**, while the fuel gauge displayed **instantaneous** information" ＝ 抽象性の分離ができていない |

→ **2-1 confirmed。留保: 消費量ドメイン限定・同一試験・抽象性と時間集約の交絡。**

### C3. ⚠️★★★ [P314] の「ハイブリッド性」留保は、本ラウンドで **補強された** **[3-0]**

★ **RQ γ で見つかった最良の直接比較の「抽象」条件にも、例外なく数値が残っていた。**逐語:

- Dahlinger TRD 2018: "In order to increase comprehensibility of and receptiveness to this eco-feedback,
  **the underlying values of the three-minute floating average of fuel consumption, as well as the real-time
  consumption, are presented on the bottom right of the feedback screen.**"
- Dahlinger CHI 2018: "the high-construal stimulus depicted goal-related information based on a more abstract
  representation, i.e., **a tree and simple numbers**" / "**At the bottom left a display of the current fuel
  consumption was included** to increase comprehensibility of the EDFIS."
- Kluckner AmI 2013: "The display shows the average electricity consumption (**in KW/h units**) over a week"
- Sohn & Nam 2015: 最良デザインは "the ratio to average consumption … drawn in a **bar-graph**" ＝ 比率（数値）を保持

→ ★ **これら 5 本が支持しているのは「抽象層を *数値の上に足す* と効く」であって、「数値を *取り去っても* 効く」ではない。**
**数値を完全に取り去った条件で行動が有意に動いた実例は、フィールドでは 0 件、ラボで 1 件（Maan）のみ。**
3 票とも異論なし（① この読みは逐語に依拠 / ② 層 A は数値がゼロなので外挿ギャップは実在 / ③ 反例を探したが見つからない）。

### C4. 「純アンビエントが効かない/劣る/逆効果」の反証は存在する **[3-0]**

- ⚠️★★★ **逆効果**: UpStream 公共蛇口の純 traffic light 表示で使用時間が**増加**。逐語 "a marginally significant
  (p=0.14) **25.7% increase** in duration … for men, and a **significant (p<0.001) 133.5% increase** … for women"。
  著者の説明は novelty/探索行動（"it was not unusual to observe people use water simply to watch the system
  cycle through its states"）。→ ★ **抽象符号は「意味を探る」対象になり、行動を意図と逆に動かしうる。**
- **null**: Börner, Kalz & Specht (2015) *Environmental Education Research* 21(6):899-915 —
  逐語 "The results **do not provide clear evidence** that the design of the displays influences learning outcome
  or that the displays lead to pro-environmental behaviour change."（representational fidelity を変えても差が出ない）
- **null**: Godino et al. (2013) *PLoS ONE*「FAB study」— **N=466 RCT**、Actiheart による客観 PA。
  逐語 "The intervention had **no effect on objectively measured physical activity** (PAEE: β=−0.92, 95% CI −3.50 to 1.66,
  p=0.48 …)" / "**Results did not differ according to the type of feedback**"（simple / visual / contextualised）。
  ★ ただし awareness は上がった（OR=1.74）＝ **「気づきは動くが行動は動かない」**。
- **null**: Majeed et al. (2026) *Behavioral Sciences* 16(5):623 — ★ **ロック画面** 壁紙の事前登録 within-subject RCT、
  N=60・各条件 3 週。逐語 "we did **not find any differences** between conditions across the pre-registered
  confirmatory outcomes"（productivity・procrastination を含む）。⚠️ 壁紙は**何も符号化していない**ので
  「フィードバックでない常在画像は効かない」までしか言えないが、**GSE 層 A と媒体・曝露形態が最も近い null** である。

→ **3-0 確定。** ★ **有利側 (C2) を 2-1 で通したのと同じ厳しさで、この反証も通っている（対称）。**

---

## 6. ⚠️ ゼロの検算表

**厳格条件**（＝ GSE 層 A と同型）: 「数値・文字を一切出さない」×「客観行動が主要アウトカム」×「アンビエント（周辺的・常在）」×「統制群あり」×「視覚」×「実フィールド」
→ ★ **この全部を満たす研究は、本ラウンドのコーパスに 0 件。**

| 落とした条件 | 埋まるか | 代表例 |
|---|---|---|
| **「数値を一切出さない」→ 小さく従属的な数値なら可** | ✅ **埋まる** | **Dahlinger et al. 2018 TRD** (10.1016/j.trd.2018.09.013): RCT・N=62・245,819 km、symbolic **−0.231 l/100km, p<.01 (≈2–3%)**。⚠️ ただし symbolic 側にも数値がある |
| **「客観行動」→ センサ＋自己申告の混合なら可** | ✅ **埋まる** | **UbiFit** (10.1145/1409635.1409644): 数値ゼロ表示・フィールド 3 か月・N=28、display×week 交互作用 **F(1,312)=6.51, p=.0112** |
| **「実フィールド」→ ラボの模擬課題なら可** | ✅ **埋まる** | **Maan et al. 2011** (10.1007/s12053-010-9102-6): 照明色のみ・数値ゼロ、模擬暖房消費 **−21%, F(1,53)=7.16, p=.01** |
| **「統制群あり」→ 数値表示との比較のみで可** | ✅ **埋まる**（が意味が変わる） | Maan / Dahlinger はどちらも **no-feedback 群を持たない or 抽象 vs 数値の対比**。→ ★ 示せるのは「数値より効く」で、「何もしないより効く」ではない |
| **「有意」→ 方向の一貫性で可** | ✅ **埋まる** | **UpStream** (10.1145/1753326.1753604): 完全客観・フィールド・数値ゼロだが **p=.09 / .11**、N=4 世帯 |
| **「視覚」→ 聴覚・触覚でも可** | ❌ **埋まらない** | ★ **該当ゼロ。** 見つかる sonification は自転車ペダリング・Parkinson 歩行等の**リアルタイム運動学習ループ**で、行動変容の常在フィードバックではない。唯一の客観行動×聴覚は Sohn & Nam の「beep の頻度」だが、これは**視覚表示に付随するアラート**であって単独の非数値チャネルではない |
| **「アンビエント（周辺的）」→ 能動的に見に行く表示でも可** | ✅ **埋まる** | [P313] Karlin et al. (2015) k=42 の大半がこの型。★ ただし効果量は r=.04–.08 と小さい |

★ ★ ★ **読み方**: 埋めるには **必ず 1 つ以上を落とさねばならない。**
**「数値ゼロ」と「実フィールドの完全客観アウトカム」を同時に保った研究は、本ラウンドでは発見できなかった。**

---

## 7. ★ 登録候補

⚠️ **メインへ**: 既存 [P1]–[P316] / [V1]–[V136] は未確認。**key（DOI）で必ず照合すること。**
★ 特に **UbiFit 2 本は既登録の可能性が高い**（[P100]/[P101] 候補）。Karlin / Tiefenbeck / Kelly&Knottenbelt は本ラウンドでは新規提案しない。

| # | 書誌 | key | N / 設計 | 効果量 | 表示に数値は | 接地案 |
|---|---|---|---|---|---|---|
| **1** | Dahlinger, A., Tiefenbeck, V., Ryder, B., Gahr, B., Fleisch, E., & Wortmann, F. (2018). The impact of numerical vs. symbolic eco-driving feedback on fuel consumption – A randomized control field trial. *Transportation Research Part D* 65, 375–386. | `10.1016/j.trd.2018.09.013` | 62 名・10 週・22,538 trip・265,939 区間・245,819 km・**RCT（統制群あり）**、個体固定効果 | symbolic **β=−0.231 l/100km (SE .106), p<.01**（≈2–3%）/ numerical **β=−0.006, n.s.** | ⚠️ **ある**（3 分移動平均＋実時間消費を画面右下に併記） | ★ **本 RQ の最重要候補。** 「表示形式そのものが客観行動を左右する」の直接証拠。同時に **[P314] の留保を保存する根拠**（symbolic 側にも数値がある） |
| **2** | Dahlinger, A., Wortmann, F., Ryder, B., & Gahr, B. (2018). The Impact of Abstract vs. Concrete Feedback Design on Behavior – Insights from a Large Eco-Driving Field Experiment. *CHI '18*, 1–11. | `10.1145/3173574.3173953` | 56 名・21,608 trip・297,000 km。⚠️ **#1 と同一フィールド試験の別解析**（独立追試ではない） | abstract **β=−.33 (SE .14), p<.05** / concrete **+.07, n.s.** | ⚠️ **ある**（"a tree **and simple numbers**"） | ★ 構成レベル理論 (construal level theory) による**機序の説明**が要る時に引く。⚠️ **#1 と併記して「1 試験」と明示すること**（baseline 不均衡 p=.002 も #1 が是正済み） |
| **3** | Maan, S., Merkus, B., Ham, J., & Midden, C. (2011). Making it not too obvious: the effect of ambient light feedback on space heating energy consumption. *Energy Efficiency* 4(2), 175–183. | `10.1007/s12053-010-9102-6` （OA: hybrid） | 57 名・2×2 被験者間ラボ実験（表示形式 × 認知負荷）、**模擬**セントラルヒーティング | 照明のみ **544 W** vs 数値 **692 W** ＝ **−21%**, F(1,53)=7.16, **p=.01**。処理時間も照明が速い (36s vs 45s, p=.001)、認知負荷交互作用 F(1,49)=4.50, p=.039 | ✅ **ゼロ**（壁に投影する色だけ） | ★ **「数値を完全に取り去っても客観指標が動いた」唯一の有意例**（ただしラボ・模擬）。GSE 層 A の「低認知負荷で常在的に読ませる」設計論拠に最も近い |
| **4** | Consolvo, S., Klasnja, P., McDonald, D. W., Avrahami, D., Froehlich, J., LeGrand, L., Libby, R., Mosher, K., & Landay, J. A. (2008). Flowers or a Robot Army? Encouraging Awareness & Activity with Personal, Mobile Displays. *UbiComp '08*, 54–63. | `10.1145/1409635.1409644` | 28 名・3 群・**3 か月フィールド**（冬季休暇期）。★ display のみを分離（interactive app は全群共通） | display×week 交互作用 **F(1,312)=6.51, p=.0112**（維持 vs 減少）。休暇週の交互作用 F(1,311)=4.11, p<.05。⚠️ Activity Count は **p=.095** で不成立 | ✅ **ゼロ**（花・蝶のみ。⚠️ ただし全群が数値つき app を併用） | ★ **携帯の常在表示 × 数値ゼロ × 長期フィールド**という点で**層 A に媒体が最も近い**。⚠️ **既登録の可能性が高い — DOI で照合** |
| **5** | Kuznetsov, S., & Paulos, E. (2010). UpStream: motivating water conservation with low-cost water flow sensing and persuasive displays. *CHI '10*, 1851–1860. | `10.1145/1753326.1753604` | 本編: 4 世帯・3 週・センサ実測。パイロット: 公共蛇口 2 室 | ⚠️ **本編は全群 p>.05**（ambient: −2.1 gal **p=.09** / −1.7 gal **p=.11**、numeric: −2.7 gal p=.08）。パイロットは **逆効果**（女性 **+133.5%, p<0.001**） | ✅ **ゼロ**（orb の色のみ） | ★ **二重に価値がある**: (i) 純アンビエント × 完全客観の**唯一のフィールド例だが有意でない**、(ii) **novelty による逆効果の実測**＝層 A の HIR 設計に直結する反証 |
| **6** | Sohn, M., & Nam, T.-J. (2015). The Effects of Eco-Feedback Design on Users' Immediate Reactions to Water Conservation. *Archives of Design Research* 28(4), 77–93. | `10.15187/adr.2015.11.28.4.77` （OA CC BY-NC） | 40 名・ラボ・32 デザイン・実測水量 | graphical > numeric（水節約で有意）。全体平均 −29.22%（SD 23.48）。⚠️ 「解釈の型」（事実/金銭/環境価値）は**行動に差なし**（主観評価のみ有意） | ⚠️ **ある**（棒グラフ＋平均比の %） | ★ 「主観評価（有用性・満足度）が動いても行動は動かない」ことを**同一実験内で示している**。⚠️ 層 A の受容性評価を行動の代理にしない根拠 |
| **7** | Godino, J. G., Watkinson, C., Corder, K., Sutton, S., Griffin, S. J., & van Sluijs, E. M. F. (2013). Impact of personalised feedback about physical activity on change in objectively measured physical activity (the FAB study): a randomised controlled trial. *PLoS ONE* 8(9), e75398. | `10.1371/journal.pone.0075398` | **466 名 RCT**、Actiheart（心拍＋加速度）による客観 PA、8 週 | ★ **null**: PAEE β=−0.92 (95% CI −3.50–1.66, **p=0.48**)、ACC β=0.01 (p=0.21)。⚠️ **awareness だけ上昇 OR=1.74 (1.05–2.89)** | 3 型（simple / visual / contextualised）を比較し **型による差なし** | ★ **反証の主柱**。「気づきは上がるが客観行動は動かない」という**分離の直接証拠**。★ GSE が「本人の気づき」を成功指標に置き換える誘惑への歯止め |
| **8** | Börner, D., Kalz, M., & Specht, M. (2015). It doesn't matter, but: examining the impact of ambient learning displays on energy consumption and conservation at the workplace. *Environmental Education Research* 21(6), 899–915. | `10.1080/13504622.2014.921804` （OA: green / research.ou.nl） | 準実験・大学キャンパス職員。**representational fidelity（抽象度）と notification level を 2 次元で操作** | ★ **null**: 逐語 "do not provide clear evidence that the design of the displays influences learning outcome or that the displays lead to pro-environmental behaviour change" | 抽象度を操作変数にしている | ★ **抽象度を直接いじって「差が出なかった」唯一の実験**。C2（抽象＞数値）の**対称的な反例**として必ず併記する |
| **9** | Majeed, N. M., Chen, N. R. Y., Goh, A. Y. H., Hu, M., Koh, K. J. J., Ang, Y. H. G., & Hartanto, A. (2026). Examining the Effects of Viewing Nature and Animal Smartphone Wallpapers on Affect, Behaviour, and Cognition: A Randomised Cross-Over Trial. *Behavioral Sciences* 16(5), 623. | `10.3390/bs16050623` （OA） | **60 名・事前登録・within-subject・各条件 3 週** | ★ **null**（confirmatory 全滅: life satisfaction / affect / stress / **productivity / procrastination**）。探索的には animal 壁紙が **distractibility を増やす** | ✅ 数値ゼロだが**何も符号化していない** | ★ **媒体（スマホロック画面）と曝露形態が層 A に最も近い null**。★ 「ロック画面に画像を置けば何か動く」という**弱い前提の反証**。⚠️ フィードバックでない点を必ず明記 |
| **10** | Aldenaini, N., Alqahtani, F., Orji, R., & Sampalli, S. (2020). Trends in Persuasive Technologies for Physical Activity and Sedentary Behavior: A Systematic Review. *Frontiers in Artificial Intelligence* 3, 7. | `10.3389/frai.2020.00007` （OA） | 170 論文の系統的レビュー（2003–2019） | アンビエント/公共ディスプレイ 16 件中 **fully successful 9 (56%) / partially 4 / unsuccessful 2 / 未評価 1** | — | ★ ランドスケープ用。⚠️ **「成功」の判定は各原論文の自己申告に依存**するので効果量の根拠には使わない |

---

## 8. ⚠️ 否決リスト

| 否決した主張 / 候補 | 票 | 否決理由 |
|---|---|---|
| **Kluckner et al. (2013) AmI**（`10.1007/978-3-319-03647-2_11`）は純アンビエント × 客観行動の実例である | 0-3 | ★ 3 つとも独立に致命的: (i) 表示が **色 ＋ kWh 数値 ＋ 棒グラフ ＋ 時刻**のハイブリッド、(ii) 主要アウトカムは 10 種の**心理尺度**（RQ 自体が "attitudinal (behavior) change"）、(iii) **効果量・係数・CI が一切なく**（"a low correlation" / "a weak trend" のみ）、**統制群も無く**、著者自身が "the evidence of effects … is particularly difficult" と認めている。被験者 24 世帯は**エネルギー会社の相談員**。→ §4 |
| ⚠️★★★ **「UpStream は二色の抽象表示が数値より効果的だと結論した」**（Sohn & Nam 2015 の孫引き） | 0-3 | ★ **一次で検算して否決。** 原典 (CHI 2010) の本編は **ambient も numeric も全群 p>.05**（p=.09 / .11 / .08）、N=4 世帯・各相 5–12 事象。「効果的」と呼べる有意差は無い。⚠️ **孫引きが一次を有意方向に誇張していた。** → 候補 5 は「有意でない」ことを含めて登録する |
| ⚠️★★★ **「numeric expression was more effective for saving water than graphical expression」**（WebSearch 要約） | 0-3 | ★ **一次で検算して否決。** Sohn & Nam (2015) の逐語は**正反対**: "the **graphical** representation of water consumption was significantly more effective than the **numeric** representation"。**WebSearch の要約は誤り。** |
| Dahlinger CHI 2018 と TRD 2018 は 2 件の独立した証拠である | 0-3 | ★ **同一フィールド試験**（同じ 62/56 名の道路支援ドライバ、同じ 10 週）。効果量を 2 回数えてはならない。⚠️ CHI 版は baseline 不均衡（abstract 群が有意に高燃費 **p=.002**）を抱えており、TRD 版（baseline 燃費 F=0.02, p=0.98）が是正版である |
| **Kluckner et al. (2013) Persuasive**（`10.1007/978-3-642-37157-8_14`）を書誌のみで登録する | 1-2 | 本文未取得（CLOSED）。**6 ページの短報**で被引用 3。内容を確認せず登録しない。→ §9 |
| **Schrammel et al. (2011) FORE-Watch**（`10.1007/978-3-642-25167-2_19`）| 1-2 | 本文未取得（CLOSED）。かつ**同じ FORE-Watch の先行報告**で、上位版（AmI 2013）を §4 で否決済み |
| 「アンビエント音（sonification）で数値なしに行動が動いた」 | 判定不能 | ★ **該当ゼロ。** 見つかるのは運動学習ループ（自転車ペダリング / Parkinson 歩行）で、**行動変容の常在フィードバックではない**。→ §6 |

---

## 9. ⚠️ 取得できなかったもの

| 文献 | 経路と結果 |
|---|---|
| **Kluckner, Weiss & Tscheligi (2013) "Where to Place My Ambient Persuasive Display?" Persuasive 2013, LNCS 7822, 110–115** (`10.1007/978-3-642-37157-8_14`) | Unpaywall `is_oa:false / oa_status:closed` → Semantic Scholar `openAccessPdf.status = **CLOSED**` → Springer ペイウォール。**セルフアーカイブも見つからず。取得不能で閉じる。** |
| **Ham & Midden (2010) "Ambient Persuasive Technology Needs Little Cognitive Effort" Persuasive 2010, LNCS 6137, 132–142** (`10.1007/978-3-642-13226-1_14`) | Unpaywall `closed` / S2 `CLOSED` / Springer ペイウォール。★ 候補 3 (Maan et al.) の姉妹研究（模擬洗濯機課題）なので、**Maan で代替可能**と判断して深追いしない |
| **Schrammel et al. (2011) FORE-Watch** (`10.1007/978-3-642-25167-2_19`) | Unpaywall `closed` / Springer ペイウォール。AmI 2013 版で内容は代替済み |
| **Kluckner et al. の PUC 誌論文** | ★ **存在しない。** Crossref `filter=issn:1617-4909` + `query.author=Kluckner` → **total-results 0**。伝聞書誌の誤り（§4.1） |

---

## 10. ★ GSE 層 A への含意（メインへの申し送り）

1. ⚠️★★★ **[P314] の留保は外せない。むしろ強くなった。** 本 RQ で見つかった最良の直接比較 5 本のうち
   **4 本の「抽象」条件に数値が残っている**（逐語確認済み）。支持されているのは
   「**抽象層を数値の上に足すと効く**」であって「**数値を取り去っても効く**」ではない。
2. ★ **数値を完全に取り去った有意例は Maan et al. 2011 の 1 本のみで、ラボの模擬課題**である。
   フィールドでは UbiFit（アウトカムに自己申告混入）と UpStream（有意に届かない）しかない。
   → **層 A の「数値を一切出さない」設計は、外部証拠で正当化されていない。** 設計判断としては保持してよいが、
   **「先行研究が支持している」と書いてはならない。**
3. ★ **反証側が具体的**: UpStream の公共蛇口では純アンビエントが**逆効果**（+133.5%, p<0.001）で、
   機序は「符号の意味を探る探索行動」。→ ★ **層 A の HIR（有害介入率）設計では「符号を解読しようとして作業から離れる」を
   明示的な害として数えるべき**。⚠️ UpStream 本編でも参加者の多くが色の意味（平均との比較）を**正しく読めていない**
   （逐語 "**Most participants, however, did not identify the color sequence as a comparison** between their current
   and average water usage"）。
4. ★ **FAB study (N=466) の分離が最も効く**: 「awareness は上がる (OR=1.74) が客観行動は動かない (p=0.48)」。
   → **層 A の評価で「本人が気づいた」を成功指標に置き換えない。** Sohn & Nam も同一実験内で
   「主観評価は有意差、行動は差なし」を示している。
5. ★ **媒体が最も近い null**: ロック画面壁紙の事前登録 RCT (N=60, 各 3 週) が productivity / procrastination で
   完全な null。⚠️ 壁紙は何も符号化していないので直接の反証ではないが、
   **「ロック画面に何か置けば行動が変わる」という素朴な前提は支持されていない**ことは言える。

---

*生成: 2026-09-06 / RQ γ サーヴェイ subagent / 取得 15 ソース・6 angle*
