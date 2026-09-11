# 一次取得と書誌確定（2026-09-06・第 3 ラウンド）

対象: メインから名指しされた 5 件。**探索はしない。取れたか取れなかったかを確定させる。**
⚠️ 本ファイルは報告専用。`docs/references.md` / `docs/literature/_index.md` は **一切編集していない**。

## 0. 進捗ログ

| 件 | 状態 |
|---|---|
| （最初） | 報告ファイルを空で作成（前ラウンドの全損対策） |
| 1 Tiefenbeck | Crossref で DOI 確定 → Unpaywall → **ETH Research Collection の DSpace REST API 経由で published version PDF 全文取得** ✅ |
| 2 Buçinca | Crossref で DOI 確定 → Unpaywall → **arXiv 2102.09692 で全文取得** ✅ |
| 3 [P307] Walker | Crossref / DataCite / OpenAlex / ICAD prefix facet の 4 系統で **DOI 不在を確定** ＋ ICAD 公式アーカイブで **一次全文も取得** ✅ ／ ⚠️ **登録 URL が別論文だった（要訂正）** |
| 4 [P310] Nees | **DOI = `10.21785/icad2019.048` 確定**（頁 176–183）✅ ／ ⚠️ **登録 URL が別論文だった（要訂正）** |
| 5 [P311] Thomson | **DOI = `10.1117/12.587254` 確定**（Proc. SPIE 5669, pp. 146–157）✅ ／ ⚠️ 本文は **OA に存在しない** |

### ★ 5 件の結論（1 行ずつ）

| # | 文献 | 取得 | 確定した DOI |
|---|---|---|---|
| 1 | Tiefenbeck et al., *Nature Energy* (2019) | **一次全文** | `10.1038/s41560-018-0282-1` |
| 2 | Buçinca, Malaya & Gajos, *PACM HCI* (2021) | **一次全文** | `10.1145/3449287` |
| 3 | [P307] Walker, Kramer & Lane, ICAD 2000 | **一次全文**（副産物） | ⚠️ **DOI なし（確定）** |
| 4 | [P310] Nees, ICAD 2019 | 書誌のみ | `10.21785/icad2019.048` |
| 5 | [P311] Thomson et al., SPIE 2005 | 書誌のみ（本文は closed） | `10.1117/12.587254` |

---

## 1. ★★★ Tiefenbeck et al. (2019) Nature Energy

### 温度: **一次全文を取得した**（published version PDF・10 頁・本文＋Methods 全部）

### 書誌（Crossref 逐語）

```
DOI: 10.1038/s41560-018-0282-1
title: Real-time feedback promotes energy conservation in the absence of
       volunteer selection bias and monetary incentives
container-title: Nature Energy
volume 4, issue 1, pages 35-41
issued (Crossref): 2018-11-19  ← online first
authors: Tiefenbeck Verena; Wörner Anselma; Schöb Samuel; Fleisch Elgar; Staake Thorsten
type: journal-article
```

⚠️ **年の扱い**: Crossref の `issued` は online-first の **2018-11-19**。
PDF 本文の欄外は逐語 `NATuRE ENERgy | VOL 4 | JANUARY 2019 | 35–41`、
ETH のメタデータも `Publication date: 2019-01`。
→ ★ **誌面 (issue) 年は 2019 が正しい。「(2019)」で引いてよい。**

⚠️ **Publisher Correction が 2 本ぶら下がっている**（本文の訂正ではなく publisher 側の訂正）:
`10.1038/s41560-019-0358-6` (Nature Energy 4(4):346, 2019-03-08) と
`10.1038/s41560-019-0484-1` (Nature Energy 4(10):891, 2019-09-20)。
★ 引用は本体 DOI でよいが、この事実は記録しておく。

### 取得経路（★ 成功経路。前ラウンドの 403 の正体も）

1. Crossref `query.bibliographic=<題名>` → DOI 確定。
2. Unpaywall `https://api.unpaywall.org/v2/10.1038/s41560-018-0282-1?email=...`
   → `is_oa: true`, `oa_status: "bronze"`, best = `https://www.nature.com/articles/s41560-018-0282-1.pdf`。
   ⚠️ **この nature.com の "PDF" URL は curl では HTML（記事ランディングページ）を返す**
   （HTTP 200 / 330 KB / `file` の判定は `HTML document`）。
   ★ ただし **その HTML に abstract 全文が入っている**ので、abstract だけならここで取れる。
3. ★★★ **本命は ETH Research Collection。ただし handle URL を直接叩いても中身は取れない**
   —— **DSpace 7 の Angular SPA なので HTML は 782 バイトの空シェル**。
   ⚠️ ★ **403 ではなかった**。ブラウザ UA を付けると `handle/20.500.11850/294409` は **200** を返す。
   （前ラウンドの「403」は UA 無しが原因である可能性が高い。★ いずれにせよ HTML 経路は無意味。）
   → ★ **REST API を使う**:
   - `https://www.research-collection.ethz.ch/server/api/pid/find?id=hdl:20.500.11850/294409`
     （⚠️ **302 を返すので `-L` 必須**） → item uuid `8edb6b25-7fbd-470e-b9ba-295bc22d8ac1`
   - `.../server/api/core/items/<uuid>/bundles` → `ORIGINAL` bundle uuid `af3e81c5-3e5c-4464-8356-7492ea7d1c5f`
   - `.../server/api/core/bundles/<uuid>/bitstreams` → `s41560-018-0282-1.pdf` (2,107,040 B)
   - `.../server/api/core/bitstreams/912fabd0-8ebe-4919-985a-2a78b80a879d/content` → **PDF 実体**
   - `pypdf` で 10 頁 / 54,187 文字を抽出。★ **published version**
     （ETH の rights 表示: `In Copyright - Non-Commercial Use Permitted`）。

### ⚠️★★★ 論点 1: 表示は数値を含むか（★ 逐語）

⚠️ **含む。それどころか「数値 ＋ 順序尺度 ＋ 絵」のフル・ハイブリッドである。**

> "In the treatment condition (60% of rooms, randomly assigned), smart shower meters displayed
> real-time feedback on the resource consumption of the ongoing shower: **total water consumption
> in litres (one decimal), total energy use in (kilo)watt hours, a dynamic rating of the current
> energy-efficiency class (A–G) and a four-stage animation of a polar bear standing on a gradually
> melting ice floe** with stage transitions at predefined energy-use thresholds"
> — 本文 Results 冒頭（PDF p.36）

Methods はさらに、**そもそも単一の数値表示ではないことを設計思想として明言**している:

> "**Most feedback devices display a bundle of elements rather than a single numeric metric** to put
> the measurement data into context; frequently used elements include historic comparisons, peer
> comparisons, analogies and energy savings tips. Likewise, the smart shower meters in rooms
> assigned to the treatment condition displayed **water consumption in litres (one decimal), energy
> use in (kilo)watt hours, current water temperature, a dynamic rating of the current
> energy-efficiency class (A–G) and a four-stage animation of a polar bear** standing on a melting
> ice floe with stage transitions at predefined energy use thresholds."
> — Methods, "Display content in the treatment group"

★ **絵（polar bear）だけを分離した内的証拠もある**（★ ただし本論文の測定ではなく別研究 [ref 52] への参照）:

> "While the polar bear may be an eye-catching and memorable display element, **it does not seem to
> drive the savings effects**. A related study specifically examined the effect of variations of the
> design choices of the feedback elements; the results indicate that **if the polar bear animation
> makes any difference, it reduces rather than increases the effectiveness of the display**."
> — Methods, 同節

⚠️★★★ **これは GSE にとって不利な方向の一次証拠である。**
本論文の中で「抽象的な絵」に最も近い要素（polar bear）を、**著者自身が「効果を駆動していない、
むしろ効果を *下げる* 可能性がある」と書いている**。
★ 効いているのは **数値 (litres / kWh) と順序尺度 (A–G class)** の側だと読むのが自然である。

★ **統制群も「無表示」ではない**（★ Hawthorne 対策として温度だけ出す）:

> "while guests in the treatment rooms received real-time feedback on their resource use from the
> beginning of the shower (along with the current water temperature), **control-group devices
> displayed only water temperature**."

> "While the temperature reading does not convey information about the resource use and remains
> relatively static over the course of a shower, **it indicates that the device measures data**, thus
> reducing potential differences between the treatment and control group for Hawthorne effects to occur."

### 論点 2〜4: アウトカム / N / 効果量 / 持続（★ 逐語）

**アウトカムは完全に客観行動**（自己申告は一切なし。デバイス内蔵メモリの実測）:

> "For each water extraction, the smart shower meter recorded **energy and water consumption,
> average water temperature, interruptions and the duration**." （Methods, "Data"）

> "Using the data stored on the device..." ／ "...its internal memory, **which was read out at the end
> of the study**."

⚠️ ★ **被験者は研究の存在すら知らされていない**（非 opt-in が本論文の売り）:

> "real-time feedback on resource consumption during showering induces substantial energy
> conservation in an **uninformed sample** of guests at 6 hotels (**265 rooms, N = 19,596
> observations**)" （Abstract）

**N / 設計**:

> "In a randomized controlled trial, guests at six Swiss hotels (see Table 1) encountered a smart
> shower meter fitted to the shower in the bathroom of their hotel room. ... We equipped a total of
> **265 rooms** with these devices and collected a data set with **19,596 observations** (water
> extractions, after pre-processing) from **February to April 2016**."

> "**Approximately 40% of the rooms were assigned to the control group.** They serve as the reference
> group to calculate the treatment effect."

⚠️ **Table 1 の合計欄は "Total 269"** で本文・Abstract の 265 と食い違う（原文のまま）。
★ 引用時は本文の **265** を使い、この不一致を鵜呑みにしない。
★ 標準誤差は **room level でクラスタ調整**（Table 3/4 脚注: "adjusted for clustering at the room level"）。

**効果量**（★ 逐語）:

> "guests in the treatment group used on average **0.215 kWh less energy per shower** than the
> control-group mean of **1.883 kWh** (Table 2, column 1). This represents a **reduction of 11.4%
> (t(19,596) = −4.88, P < 0.001)**. Controlling for flow rate (column 2), the effect is still highly
> significant, with a reduction of **0.188 kWh (t(8,882) = 3.59, P < 0.001), or 10.0%**."

- log 変換モデル (Table 3): **−0.124\*\*\* (SE 0.024)**, N = 19,596, **R² = 0.008**
- ホテル固定効果 (Table 4): **−0.197\*\*\* (SE 0.041)**, N = 19,596, **R² = 0.021**

⚠️ ★ **R² は 0.008〜0.047 と極めて小さい**。★ 効果は「頑健だが、分散のごく一部しか説明しない」。

★ 自己選択サンプルとの比較（★ opt-in の方が効果が大きい）:

> "the effect size in the **opt-in household sample (0.592 kWh, or 22%) was larger than the effect we
> observe in the hotel setting (0.215 kWh, or 11.4%)**"

**持続 / 減衰: ⚠️ 測っていない。測れないと著者が明記している。**

> "Moreover, **due to the short duration of guests' hotel stays, we are not able to examine effects
> over time**. While several studies (lasting between 2 and 16 months) document the mid-term effect
> stability of activity-specific real-time feedback **with opt-in samples**, further research needs to
> investigate **whether the large savings effects also persist over time among non-self-selected
> participants**."

★ **つまりこの論文から「効果が持続する」は引けない。**

### ★ GSE への含意（1 行）

⚠️★★★ **[P314] の「ハイブリッド表示だから外挿できない」という留保は、本論文で *強まる*。**
表示は数値 (litres/kWh) ＋順序尺度 (A–G) ＋絵 (polar bear) のハイブリッドであり、かつ
**著者自身が「絵は効果を駆動しない、むしろ下げうる」と書いている**ため、本論文は
**「抽象符号のみで行動が変わる」証拠にならない**どころか **逆向きの示唆**を与える。
★ GSE の層 A（数値を出さない抽象符号）の根拠として本論文を引くのは **不可**。
★ 引けるのは「**リアルタイム・活動特異的フィードバックは非 opt-in の実環境でも客観行動を動かす**」
という一般命題までで、**符号の抽象度については GSE に不利な一次証拠**として扱うのが誠実である。

---

## 2. ★★ Buçinca, Malaya & Gajos (2021) — cognitive forcing のコスト

### 温度: **一次全文を取得した**（arXiv 著者版 PDF・21 頁・ACM 組版と同一）

### 書誌（Crossref 逐語 ＋ 本文の ACM Reference Format 逐語）

```
DOI: 10.1145/3449287
title (Crossref): "To Trust or to Think"   ← ⚠️ Crossref は副題を落としている
container-title: Proceedings of the ACM on Human-Computer Interaction
volume 5, issue CSCW1, pages 1-21
issued 2021-04-13 / published-online 2021-04-22
authors: Buçinca Zana; Malaya Maja Barbara; Gajos Krzysztof Z.
```

★ **正式な題名と article number は本文の ACM Reference Format から取る（逐語）**:

> "Zana Buçinca, Maja Barbara Malaya, and Krzysztof Z. Gajos. 2021. **To Trust or to Think: Cognitive
> Forcing Functions Can Reduce Overreliance on AI in AI-assisted Decision-making.** Proc. ACM
> Hum.-Comput. Interact. **5, CSCW1, Article 188** (April 2021), 21 pages. https://doi.org/10.1145/3449287"

⚠️ ★ **`page: 1-21` ではなく `Article 188` が正しい所在**。Crossref の `page` を鵜呑みにしない。
★ arXiv: **2102.09692**（DBLP key: `journals/pacmhci/BucincaMG21`）。

### 取得経路

- Crossref → DOI `10.1145/3449287`。
- Unpaywall → `oa_status: "green"`, best = `https://arxiv.org/pdf/2102.09692` (submittedVersion)。
- Semantic Scholar も同じ arXiv PDF を `"status": "GREEN"` で返す。
- ★ **ACM DL は一度も叩いていない**（Cloudflare を踏む必要がなかった）。
- `curl -L` で 1.9 MB / 21 頁 → `pypdf` で 80,138 文字抽出。

### ⚠️ 代償の数値と検定（★ 逐語）

**(a) trade-off の存在**

> "However, there was a trade-off: **people assigned the least favorable subjective ratings to the
> designs that reduced the overreliance the most.**" （Abstract）

> "As hypothesized, we also observed a trade-off between the acceptability of the designs and their
> effectiveness at reducing the overreliance on the AI. Specifically, **people over-relied less on the
> AI when exposed to the conditions that they found more difficult, preferred less, and trusted less.**"
> （Introduction）

**(b) 主観指標の数値と検定（Table 3・逐語の marginal means と standard errors）**

⚠️ ★ 条件は 3 カテゴリ: `no AI` / `SXAI` (simple explainable AI) / `CFF` (cognitive forcing functions)。

| 指標 | post-hoc | no AI | SXAI | CFF | 検定 |
|---|---|---|---|---|---|
| Trust | {CFF, SXAI} | — | **3.91 (0.09)** | **3.72 (0.08)** | *F*(1, 146.4) = 2.84, **n.s.** |
| Preference | {no AI} < {CFF, SXAI} | 3.13 (0.12) | **3.78 (0.09)** | **3.62 (0.09)** | *F*(2, 169.5) = 10.52, *p* ≪ .0001 |
| Mental Demand | {SXAI, CFF} < {no AI} | 3.66 (0.16) | **2.86 (0.12)** | **2.84 (0.11)** | *F*(2, 183.4) = 11.70, *p* ≪ .0001 |
| **System Complexity** | **{SXAI} < {CFF, no AI}** | 3.19 (0.14) | **2.64 (0.11)** | **2.95 (0.10)** | *F*(2, 172.2) = **6.19, *p* = .002** |

> "They perceived the system as **significantly less complex in simple explainable AI conditions
> compared to either cognitive forcing functions or no AI**. ... **Conditions within categories did not
> differ significantly on any of the subjective ratings.**" （§4.2）

⚠️★★★ **代償の中身を誤読しないこと（★ ここが本件の要点）**:

- ★ **有意に払った代償は「System Complexity」だけ**（SXAI 2.64 → CFF 2.95, *p* = .002）。
- ⚠️ **Trust は下がったが有意ではない**（3.91 → 3.72, n.s.）。
- ⚠️ **Preference も CFF (3.62) < SXAI (3.78) だが、この 2 つは同じ括弧に入っており有意差なし**
  （有意なのは `no AI` (3.13) がその両方より低いという向き）。
- ⚠️★★★ **Mental Demand は CFF で *上がっていない*。** CFF 2.84 ≈ SXAI 2.86 で、
  むしろ **`no AI` (3.66) の方が有意に高い**。
  → ★ **「摩擦を足したら主観的認知負荷が上がった」は、この論文からは言えない。**

**(c) 主観と客観の相関（★ trade-off の実体）**

> "**Trust and preference were significantly negatively correlated with both overall performance and
> carb source detection performance for incorrect model predictions.** ... **Mental demand and system
> complexity were significantly negatively correlated with overall and carb source detection
> performance for correct model predictions.** However, **mental demand was significantly positively
> correlated with carb source detection performance for incorrect model predictions.**" （§4.3）

> "When the AI model was making incorrect predictions, **people performed best in conditions that they
> preferred and trusted the least, and that they rated as the most difficult.**" （§6 Discussion）

**(d) 所要時間**: ⚠️ **本論文は task time を従属変数として報告していない。**
測られているのは正答/過信の分布と主観 4 指標。時間に関する記述は **設計上の強制待機**と**全体所要**のみ:

> "...the message '**AI is processing the image**' for **30 seconds** before the suggestion and
> explanation were presented..." （CFF 条件の 1 つ）
> "**The study took 15 minutes on average.**" （Participants）

→ ★ **「所要時間が増えた」という主張の一次にはできない**（★ 30 秒の待機は *操作* であって *結果* ではない）。

### ★★★ (e) 代償が「誰に」大きかったか（★ NFC との交互作用・逐語）

> "We found that **cognitive forcing functions benefited the more advantaged group—people with high
> NFC—the most.**" （Introduction）

★ 主観の NFC 分割（§5・Table 6）:

> "**Low NFC participants generally found the task significantly more mentally demanding (M = 3.10)
> than high NFC participants (M = 2.62), (F(1,165) = 7.07, p = .009).** Similarly, they found the
> **system to be significantly more complex (M = 3.04) than high NFC participants (M = 2.65),
> (F(1,162.4) = 5.86, p = .02).** Low NFC participants reported on average **higher trust (M = 3.92)
> than high NFC participants (M = 3.70), albeit not significantly so (F(1,172.1) = 2.89, n.s.).**
> They also **preferred the systems on average more (M = 3.80) than high NFC participants (M = 3.56),
> but this difference was also not statistically significant (F(1,170) = 2.63, n.s.).**"

> "**High NFC participants reported significantly higher trust for simple explainable AI conditions
> compared to cognitive forcing functions. They also preferred simple explainable AI conditions more
> than cognitive forcing functions and perceived them to be significantly less complex. There were no
> significant differences for subjective ratings across categories for low NFC participants.**"

★ Table 6 の System Complexity 行（PDF から抽出した値）:

- `High NFC`: **{SXAI} < {CFF}** — SXAI **2.64 (0.15)** vs CFF **2.95 (0.13)**, *F*(1, 57.53) = **6.26, *p* = .01**
- `Low NFC` : **{SXAI, CFF}** — SXAI **2.96 (0.16)** vs CFF **3.11 (0.15)**, *F*(1, 71.73) = 0.47, **n.s.**

★ 性能側の交互作用:

> "High-NFC participants demonstrated significantly higher overall performance (M = 0.44) than low-NFC
> participants ... (M = 0.67) significantly better (F(1,172.2) = 32.11, p ≪ .0001) than low-NFC
> participants (M = 0.44)."

> "...**high-NFC participants benefited from cognitive forcing functions as they significantly improved
> both their overall and carb source detection performance.** Whereas, while cognitive forcing
> functions improved low NFC participants' carb source detection performance significantly on
> incorrect model predictions, **they did not significantly improve their overall performance.**"

⚠️★★★ **交互作用の向きを取り違えない**:

- **効果（overreliance 低減）は高 NFC に偏って出た。**
- **主観コスト（complexity の有意な悪化）も高 NFC 群でのみ有意に検出された。**
  低 NFC 群は CFF/SXAI 間で主観差が出ない —— ★ 低 NFC は**条件をまたいで元から重い**
  （mental demand も complexity も有意に高い）ため、差が見えないという読み方になる。
- ★ 著者の枠組みは **intervention-generated inequalities (IGI)**:
  > "we showed that our approach, while effective on average, appears to **benefit individuals with
  > high NFC more than those with low NFC**" ／ "the user interface innovations that ... require
  > increasing amounts of cognitive effort to operate, **systematically benefit high-NFC individuals
  > more than those with lower levels of cognitive motivation.**"

★ 設計と規模:

> "We conducted an experiment with **199 participants on Amazon Mechanical Turk**, in which we compared
> **three cognitive forcing designs to two simple explainable AI approaches, and to a no-AI baseline**."
> "Our data was analyzed using **mixed-effects models**."
> "...these human+AI teams performed worse than the AI model alone (**its accuracy was set to 75%**)."

★ 効果の上限についての留保も逐語で残す:

> "cognitive forcing functions **did not completely eliminate overreliance** on the AI"
> "even with the cognitive forcing functions, the human+AI teams in our study **continued to perform
> worse than the AI model alone**: the cognitive forcing functions **reduced, but not yet eliminated,
> overreliance** on the AI."
> "**Our results did not provide support for the hypothesis (H1b) that cognitive forcing functions will
> improve the performance of human+AI teams. There was no significant difference in performance
> between simple explainable AI approaches and cognitive forcing functions.**"

### ★ GSE への含意（1 行）

★ 「摩擦を足す介入は行動指標を改善しても主観コストを払う」という留保の一次として **使える**が、
⚠️ **払われたコストは「主観的な複雑さ」であって「認知負荷」でも「時間」でもない**（mental demand は上がっていない）ため、
★ GSE の留保は「**摩擦は *好まれなさ・複雑さ* を代償に過信を減らし、その利得も代償も元から余裕のある人（高 NFC）に偏る**」
という **IGI（介入起因の不平等）の形**で書くのが逐語に忠実であり、
⚠️ **「摩擦が全体性能を上げる」とは書けない**（H1b は明示的に棄却されている）。

---

# ⚠️★★★ 3〜5 の前に: **登録 URL が 2 件とも別論文を指していた**

★ DOI を探す過程で、**[P307] と [P310] に登録されている handle が、まったく別の論文のもの**であることが判明した。
★ さらに **ホスト `smartech.gatech.edu` 自体が死んでいる**（curl が `code=000` = 接続不能。DNS/サービス終了）。
Georgia Tech は DSpace 7 の `repository.gatech.edu` に移行しており、**`hdl.handle.net` 経由なら 200 で解決する**。

| # | 現在の登録 URL | ⚠️ そこにあるのは何か | ★ 正しい handle |
|---|---|---|---|
| 3 [P307] | `https://smartech.gatech.edu/handle/1853/50642` | **Walker, Nance & Lindsay, "Spearcons: speech-based earcons improve navigation performance in auditory menus", ICAD 2006** | **`1853/50679`** |
| 4 [P310] | `https://smartech.gatech.edu/handle/1853/61510` | **Ismailogullari & Ziemer, "Soundscape clock: Soundscape compositions that display the time of day", ICAD 2019 (DOI 10.21785/icad2019.034)** | **`1853/61522`** |

⚠️★★★ **これは DOI 確定より重い訂正である。** メインエージェントは `docs/references.md` の
**URL キーそのものを差し替える**必要がある（★ `url:` キーは重複防止キーなので、誤 URL のまま DOI キーに
移行すると、別論文が [P307]/[P310] として残る）。

★ 取得経路（★ 再発明しないための手順）:
`http://hdl.handle.net/1853/<n>` は 200 を返すが **DSpace 7 の Angular SPA なので HTML は 862 バイトの空シェル**。
→ `https://repository.gatech.edu/server/api/pid/find?id=hdl:1853/<n>`（★ `-L` 必須）で **完全な Dublin Core が JSON で返る**。

---

## 3. [P307] Walker, Kramer & Lane — DOI 確定

### 結論: ⚠️★★★ **DOI は存在しない（確定）。**

### 温度: **一次全文を取得した**（ICAD 公式アーカイブの PDF・6 頁）

### 検算に使った API レスポンスの要点（★ 4 系統すべてで否定を確認）

1. **Crossref**: `query.bibliographic=Psychophysical Scaling of Sonification Mappings Walker Kramer Lane`
   → 上位 6 件に**当該論文なし**（返るのは Walker 2005 の TAP 論文、JAES 2018、辞典章など）。
2. **DataCite**: `query=titles.title:"Psychophysical Scaling of Sonification Mappings"`
   → 逐語 `{"data":[],"meta":{"total":0,...}}` = **0 件**。
3. **OpenAlex**: `W1556530441` = `"Psychophysical scaling of sonification mappings"`, 2000, conference-paper,
   authors `['Bruce N. Walker', 'Gregory Kramer', 'David M. Lane']`
   → **`doi: None`**、`ids` は `{"openalex": ..., "mag": "1556530441"}` のみで **DOI キーが無い**。
4. **ICAD の DOI 名前空間の年次カバレッジ**: Crossref `prefixes/10.21785/works` は **総計 272 件**、
   published facet は逐語 `{"2019":52,"2021":36,"2017":34,"2016":34,"2018":30,"2025":25,"2023":24,"2024":22,"2022":15}`
   → ★ **ICAD が DOI を振り始めたのは 2016 年から。2000 年の予稿に DOI は存在しない。**
5. **リポジトリ側の裏づけ**: GaTech の item `1853/50679` の Dublin Core に **`dc.identifier.doi` フィールドが無い**
   （★ 対照として ICAD 2019 の item `1853/61522` には `dc.identifier.doi = https://doi.org/10.21785/icad2019.048` が有る）。

→ ★ **「DOI なし（ICAD 2000 は DOI 未付与）」と確定してよい。**

### ★ 安定した所在（★ 2 つとも実測で生存確認済み）

- **一次全文 PDF（ICAD 公式アーカイブ）**: `https://icad.org/Proceedings/2000/WalkerKramer2000.pdf`
  （HTTP 200 / `application/pdf` / 34,625 B / 6 頁。★ `pypdf` で全文抽出済み）
- **リポジトリ handle**: `http://hdl.handle.net/1853/50679`
  → `https://repository.gatech.edu/handle/1853/50679`（HTTP 200）
  ⚠️ ★ **`smartech.gatech.edu` は使わない**（接続不能）。

### 訂正が要る書誌項目（★ GaTech の Dublin Core 逐語 ＋ PDF 一次）

```
dc.title            = Psychophysical scaling of sonification mappings
                      （★ PDF の表題は Title Case: "Psychophysical Scaling of Sonification Mappings"）
dc.contributor.author = Walker, Bruce N. / Kramer, Gregory / Lane, David M
dc.date.issued      = 2000-04
dc.identifier.uri   = http://hdl.handle.net/1853/50679
dc.identifier.citation = Proceedings of the 6th International Conference on Auditory Display (ICAD2000),
                         Atlanta, GA, April 2-5, 2000. Ed: P.R. Cook.
                         International Community for Auditory Display, 2000.
dc.publisher.original = International Community for Auditory Display (ICAD)
```

★ PDF 一次から確認できた著者所属（⚠️ **Georgia Tech ではない**）:
> "Bruce N. Walker — Psychology Dept., **Rice University**, 6100 Main St., Houston, TX 77005 USA
> Gregory Kramer — **Clarity**, 310 NW Brynwood Lane, Portland, OR 97229
> David M. Lane — Psychology Dept., **Rice University**"

★ 会議の正式名は **6th ICAD (ICAD2000), Atlanta, GA, April 2-5, 2000, Ed: P. R. Cook**。
⚠️ ★ 現在の登録が "Proc. ICAD 2000" 止まりなら、**編者と開催地を補える**。

⚠️ **頁は未確定**（正直に閉じる）:
ICAD 公式アーカイブは著者名ベースの平坦な Apache index で、**TOC も frontmatter も置かれていない**
（`/Proceedings/2000/` の 43 リンクはすべて `*.pdf` と親ディレクトリのみ）。
PDF 本体にも **柱・ノンブルが刷られていない**（camera-ready 版、6 頁）。DBLP は ICAD を索引していない
（`Psychophysical scaling of sonification mappings` で hits = 0）。
→ ★ **頁を書くなら別途一次で裏を取る必要がある。現時点では書かない。**

⚠️★★★ **同名論文との混同に注意**: OpenAlex `W2153314286` =
**"PSYCHOPHYSICAL SCALING OF SONIFICATION MAPPINGS: A COMPARISON OF VISUALLY IMPAIRED AND SIGHTED LISTENERS"
(Walker & Lane, ICAD **2001**)** が別に存在する（★ こちらも DOI なし。
`http://legacy.spa.aalto.fi/icad2001/proceedings/papers/walker_b.pdf`）。★ **著者数も年も違う別論文。**

---

## 4. [P310] Nees — DOI 確定

### 結論: ★★★ **DOI は存在する。`10.21785/icad2019.048`**

### 温度: **書誌のみ**（★ 本文再取得は不要という指示に従い、全文は取っていない）

### 検算に使った API レスポンスの要点

Crossref `works/10.21785/icad2019.048` の逐語:

```
DOI             = "10.21785/icad2019.048"
title           = ["Eight Components of a Design Theory of Sonification"]
container-title = ["Proceedings of the 25th International Conference on Auditory Display (ICAD 2019)"]
page            = "176-183"
issued          = {"date-parts": [[2019, 6]]}
publisher       = "Department of Computer and Information Sciences, Northumbria University"
event           = {"name": "ICAD 2019: The 25th International Conference on Auditory Display",
                   "theme": "Sonification for Everyday Life",
                   "location": "Newcastle upon Tyne", "acronym": "ICAD 2019", "number": "25",
                   "sponsor": ["Northumbria University"],
                   "start": [2019,6,23], "end": [2019,6,27]}
type            = "proceedings-article"
resource.primary.URL = "http://hdl.handle.net/1853/61522"      ← ★ 正しい handle はここ
authors         = Nees, Michael A.
```

★ DOI 解決の実測: `https://doi.org/10.21785/icad2019.048`
→ 最終 URL `https://repository.gatech.edu/entities/publication/c42a67e7-801b-4ae0-8ef9-f779c57abc6d`（200）。

★ リポジトリ側 (`hdl:1853/61522`) の Dublin Core 逐語（★ 独立に一致を確認）:

```
dc.title             = Eight components of a design theory of sonification
dc.contributor.author = Nees, Michael A.
dc.date.issued       = 2019-06
dc.identifier.doi    = https://doi.org/10.21785/icad2019.048
dc.identifier.uri    = http://hdl.handle.net/1853/61522
dc.publisher.original = International Community for Auditory Display (ICAD)
```

### 訂正が要る書誌項目

1. ⚠️★★★ **URL を差し替える**: `smartech.gatech.edu/handle/1853/61510`（**別論文**）→
   **`https://doi.org/10.21785/icad2019.048`**（正規 DOI URL）。
   ★ handle を併記するなら `http://hdl.handle.net/1853/61522`。
2. ★ **頁を追加**: **176–183**。
3. ★ **会議名を正式表記に**: `Proceedings of the 25th International Conference on Auditory Display (ICAD 2019)`,
   Newcastle upon Tyne, 23–27 June 2019。
4. ⚠️ 題名の大小が Crossref (Title Case) と GaTech (sentence case) で割れている。
   ★ **Crossref 側（"Eight Components of a Design Theory of Sonification"）を正**とするのが妥当。
5. ★ 発行者は Northumbria University の Department of Computer and Information Sciences（Crossref）／
   ICAD（リポジトリ）。★ **予稿集の発行者としては ICAD を書くのが慣行**だが、Crossref の値も併記できる。

---

## 5. [P311] Thomson et al. — DOI 確定

### 結論: ★★★ **DOI は存在する。`10.1117/12.587254`**

### 温度: **書誌のみ**（⚠️ 本文は **OA に存在しない** ——下記 §6）

### 検算に使った API レスポンスの要点

Crossref `works/10.1117/12.587254` の逐語:

```
DOI             = "10.1117/12.587254"
title           = ["A typology for visualizing uncertainty"]
container-title = ["SPIE Proceedings", "Visualization and Data Analysis 2005"]
volume          = "5669"
page            = "146"                    ← ★ Crossref は開始頁のみ
issued          = {"date-parts": [[2005, 3, 11]]}
published-print = {"date-parts": [[2005, 3, 11]]}
publisher       = "SPIE"
event           = {"name": "Electronic Imaging 2005", "location": "San Jose, CA"}
editor          = Erbacher, Robert F. / Roberts, Jonathan C. / Grohn, Matti T. / Borner, Katy
type            = "proceedings-article"
authors         = Thomson, Judi / Hetzler, Elizabeth / MacEachren, Alan / Gahegan, Mark / Pavel, Misha
```

★ **頁の範囲は DBLP で確定した**（★ Crossref も OpenAlex も開始頁しか持たない）:

```
dblp.org/search/publ/api?q=A+typology+for+visualizing+uncertainty&format=json
→ "A typology for visualizing uncertainty." | Visualization and Data Analysis | 2005
  | pages: 146-157 | doi: 10.1117/12.587254 | url: https://dblp.org/rec/conf/vda/ThomsonHMGP05
```

★ OpenAlex（DOI 引き）: `biblio = {'volume': '5669', 'issue': None, 'first_page': '146', 'last_page': '146'}`
（★ **last_page が first_page と同値 ＝ 範囲を持っていないだけ**。DBLP の 146–157 と矛盾しない）。
★ Semantic Scholar: `externalIds` に `DBLP: conf/vda/ThomsonHMGP05`, `MAG: 2106317998`,
`DOI: 10.1117/12.587254`、`journal.volume = "5669"`。

### 訂正が要る書誌項目

1. ⚠️★★★ **URL を差し替える**: 現在の `https://www.spiedigitallibrary.org/conference-proceedings-of-spie/5669/`
   は **巻トップであって論文単位ではない** → **`https://doi.org/10.1117/12.587254`**。
2. ★ **巻・頁を追加**: **Proc. SPIE Vol. 5669, pp. 146–157**。
3. ★ **会議名を正確に**: `Visualization and Data Analysis 2005`（親イベントは **Electronic Imaging 2005**, San Jose, CA）、
   発行 **2005-03-11**、発行者 **SPIE**。
4. ★ 編者を書くなら: R. F. Erbacher, J. C. Roberts, M. T. Grohn, K. Börner。
   ⚠️ Crossref の綴りは ASCII 化されている（`Grohn` / `Borner`）。★ 正しくは **Gröhn / Börner**。
5. ⚠️ 題名の大小: Crossref は sentence case `A typology for visualizing uncertainty`。
   ★ 現在の登録 `A Typology for Visualizing Uncertainty`（Title Case）は慣行として許容範囲だが、
   **SSOT を Crossref に合わせるなら sentence case**。
6. ★ 著者名の正式形: `Thomson, Judi` / `Hetzler, Elizabeth` / `MacEachren, Alan` / `Gahegan, Mark` / `Pavel, Misha`
   （⚠️ 現在の登録 `Hetzler, E.` は Crossref も `Elizabeth`。★ ただし同グループの 2005 CaGIS 論文では
   `Hetzler, Elisabeth` と **s / z 表記が割れている**ので、本件は **Elizabeth** を採る）。

---

## 6. ⚠️ 取得できなかったもの（★ 「探せば取れる」か「OA に存在しない」かの区別）

| 対象 | 状態 | 経路と失敗理由 | ★ 区別 |
|---|---|---|---|
| **[P311] Thomson et al. の本文** | **取得不能** | Unpaywall: `is_oa: false`, `oa_status: "closed"`, `best_oa_location: None`, `oa_locations: []`。Semantic Scholar: `openAccessPdf.status = "CLOSED"`。SPIE Digital Library の論文ページは **Imperva/Incapsula の bot wall**（返るのは `_Incapsula_Resource` の 1,156 B シェル、`ROBOTS: NOINDEX,NOFOLLOW`）。OpenAlex が挙げる University of Auckland ResearchSpace `http://hdl.handle.net/2292/7272` は 200 だが **DSpace SPA で HTML から本文・PDF に到達できず、Unpaywall も OA と認めていない**。 | ⚠️ **OA に存在しない**（探しても取れない）。★ ただし **書誌は完全に確定済み**なので、指示どおり「DOI 確定だけ」の目的は達成。 |
| **[P307] の頁番号** | **未確定** | ICAD 公式アーカイブは TOC 無しの Apache index、PDF に柱・ノンブル無し、DBLP は ICAD 非索引、OpenAlex の `biblio` は全 `None`。 | ⚠️ **一次に情報が無い**。★ 捏造せず空欄で閉じる。 |
| **Tiefenbeck の nature.com 直 PDF** | **迂回して成功** | `https://www.nature.com/articles/s41560-018-0282-1.pdf` は HTTP 200 だが **HTML を返す**（bronze OA のリダイレクト）。→ ★ **ETH の DSpace REST API で published version PDF を取得できたので実害なし**。 | ★ 取れた |
| **Semantic Scholar の連続叩き** | **一時失敗** | 短時間に 2 回叩いて `429 Too Many Requests`。数秒 sleep で復旧。 | ★ 取れた |

---

## 7. ★ 経路の教訓（★ 次ラウンドで再発明しないための追記）

1. ★★★ **DSpace 7 のリポジトリは HTML を読んでも無駄。REST API を叩く。**
   ETH Research Collection も Georgia Tech repository も **Angular SPA** で、handle URL の HTML は
   **800 バイト前後の空シェル**（`<ds-app></ds-app>` だけ）。⚠️ **これを「403 / ペイウォール」と誤診しない。**
   ```
   # 1) handle → uuid（★ 302 を返すので -L 必須）
   curl -sL -H 'Accept: application/json' '<host>/server/api/pid/find?id=hdl:<prefix>/<id>'
   # 2) uuid → bundles → ORIGINAL の uuid
   curl -sL -H 'Accept: application/json' '<host>/server/api/core/items/<uuid>/bundles'
   # 3) bundle → bitstreams → PDF の bitstream uuid
   curl -sL -H 'Accept: application/json' '<host>/server/api/core/bundles/<uuid>/bitstreams'
   # 4) 実体
   curl -sL '<host>/server/api/core/bitstreams/<uuid>/content' -o x.pdf
   ```
   ★ `pid/find` のレスポンスには **Dublin Core が丸ごと入る**ので、書誌確定だけならステップ 1 で足りる。
2. ★★★ **`smartech.gatech.edu` は死んでいる**（curl `code=000`）。★ **`hdl.handle.net/1853/<n>` を使う**
   （`repository.gatech.edu` に 200 でリダイレクトされる）。
   ⚠️ **`docs/references.md` に他にも smartech URL があれば全部同じ症状のはず。**
3. ★★★ **登録 URL は「生きているか」だけでなく「中身が同じ論文か」を検算する。**
   今回 2 件とも **生きている handle が別論文を指していた**。★ `pid/find` の `dc.title` と照合すれば 1 コマンドで判る。
4. ★★ **`curl` に必ずブラウザ UA を付ける。** ETH の handle は UA 無しで落ち、付けると 200 になった
   （★ 前ラウンドの「403」の正体はこれの可能性が高い）。
5. ★★ **DOI の「不在」を確定させるには 4 系統を揃える**:
   Crossref（題名検索）／ DataCite（`titles.title:"..."`）／ OpenAlex（`ids` に `doi` キーが無いこと）／
   ★ **発行元 prefix の年次 facet**（`api.crossref.org/prefixes/<prefix>/works?rows=0&facet=published:20`）。
   ★ 最後の 1 つが決定打になる —— **「その年にはそもそも DOI を振っていない」を示せる。**
6. ★★ **頁の範囲は DBLP が持っていることがある。** Crossref も OpenAlex も SPIE 系は開始頁しか持たないが、
   `https://dblp.org/search/publ/api?q=<title>&format=json&h=5` が `pages: 146-157` を返した。
   ⚠️ **DBLP の XML エンドポイント (`/rec/<key>.xml`) は 503 を返すことがある。★ search API の方が安定。**
   ⚠️ **DBLP は ICAD を索引していない**（sonification 系は空振りする）。
7. ★ **nature.com の bronze OA は `.pdf` URL でも HTML を返す。** ★ ただし **その HTML に abstract 全文が入る**ので、
   abstract で足りるなら `<meta name="dc.description">` か `id="Abs1-content"` を抜けばよい。
8. ★ **PowerShell 環境では Python の stdout が cp932。** `export PYTHONIOENCODING=utf-8` を毎回付けないと
   `UnicodeEncodeError: 'cp932' codec can't encode character` で**取得自体は成功しているのに落ちる**。
9. ⚠️ **Bash の quoted heredoc (`<< 'EOF'`) が本環境で失敗した**（`unexpected EOF while looking for matching '`）。
   ★ 長い日本語 markdown は **Write ツールで書く**方が確実。
10. ★ **Semantic Scholar は数秒あけて叩く**（連続で `429`）。★ ACM DL に触らずに済むなら触らない
    （Buçinca は Unpaywall → arXiv で完結した）。

