# RQ δ — 触覚を含む三感覚統合と媒体不変性（2026-09-06・第 3 ラウンド）

**問い**: 触覚を含めた三感覚（視覚 × 聴覚 × 触覚）の統合的な写像理論・媒体不変性の先行はあるか。
**用途**: 判断 (f)（媒体の能力プロファイル）と **A16（媒体不変性）** を受け入れ観点として書けるかの判定 gate。
**名前空間**: `P`（理論基盤）。★ 採番と `docs/references.md` / `docs/literature/_index.md` への append は**メインが直列で行う**。本ファイルは**登録候補の報告のみ**。

## 0. 進捗ログ（★ 1 ソースごとに追記）

| # | 取得物 | key | 状態 |
|---|---|---|---|
| 1 | Nesbitt, *MS-Taxonomy: a conceptual framework for designing multi-sensory displays*, IV 2004 | doi:10.1109/IV.2004.1320213 | 書誌 Crossref 確認済。★ 視/聴/触を**同じ語彙**で記述する分類学＝(b) の直接候補。⚠️ 本文未取得（§9） |
| 2 | Nesbitt, *Designing Multi-sensory Displays for Abstract Data*, PhD thesis, Univ. of Sydney 2003 | https://ses.library.usyd.edu.au/handle/2123/4135 | MS-Taxonomy の原典。⚠️ **PDF 403 で取得失敗**（§9） |
| 3 | ★★★ Xu, Williams & Wall, *Let's Get Vysical: Perceptual Accuracy in Visual and Tactile Encodings*, arXiv 2023 | arXiv:2308.04392 / doi:10.48550/arXiv.2308.04392 | **(c) 直接**。同一データを SVG(視覚) vs swell paper(触覚)。N=12。★ **符号の有効性順位はモダリティ間で転写されない** |
| 4 | ★★★ Khalaila, Harrison, Kim & Cashman, *"They Aren't Built For Me"*, arXiv 2024 | arXiv:2410.08438 / doi:10.48550/arXiv.2410.08438 | **(c) 直接**。Cleveland&McGill の触覚再現。N=11（視覚障害者）。★ **転写は概ね成立** —— ⚠️ #3 と結論が食い違う |
| 5 | Hogan & Hornecker, *Towards a Design Space for Multisensory Data Representation*, Interacting with Computers 29(2), 2016 | doi:10.1093/iwc/iww015 | (b) 候補。Crossref で著者・巻号確認済。⚠️ 抽象は publisher により elided・**本文未取得** |
| 6 | Brewster & Brown, *Tactons: Structured Tactile Messages for Non-Visual Information Display*, AUIC 2004 / CRPIT Vol.28, 15–23 | http://eprints.gla.ac.uk/3443/ | (a) 古典。⚠️ Crossref に AUIC 版 DOI 無し。CHI'04 EA 版は doi:10.1145/985921.985936 |
| 7 | ★★★ Spence, *Exploring Group Differences in the Crossmodal Correspondences*, Multisensory Research 35(6):495–536, 2022 | doi:10.1163/22134808-bja10079（CC BY・全文取得済） | **(d) 直接**。★ Parise(2016) N=62: 極性一致率が **偶然水準 ca.50% 〜 ほぼ完全一致**まで広く分散。Velasco+2016 は 44% 一致。⚠️ Nava+2016: pitch–height の **audiotactile 対応は幼児で弱い** |
| 8 | ★★★ Griffin, *Feeling It Out: The Use of Haptic Visualization for Exploratory Geographic Analysis*, Cartographic Perspectives No.39 (Spring 2001), 12–29 | https://cartographicperspectives.org/index.php/journal/article/view/cp39-griffin （OA・全文取得済） | **(a) 直接**。★ **Bertin の視覚変数構文の触覚版**（touch: vibration/flutter/pressure/temperature、kinesthetic: resistance/friction/kinesthetic location、visual-analog: size&elevation/shape/texture-grain/orientation × nominal/ordinal 適合表）。⚠️ **実証ではなく論理的分析のみ** |
| 9 | Vasconcellos 1991（Griffin 経由の二次言及） | — | ⚠️★★★ **反例の核**: Bertin をそのまま触覚へ翻訳した結果、**両感覚で知覚できる変数しか残らず**、触覚固有（温度/圧/kinesthetic）が落ちた → ★ 判断 (f) の直接の論拠 |
| 10 | Dullaert, Ranasinghe, Degbelo & Bouali, *Data Physicalization with Haptic Variables: Exploring Resistance and Friction*, CHI EA 2024 | doi:10.1145/3613905.3651011（green OA: research.utwente.nl/files/382269076/chi24-539.pdf） | (a) 実証側。★ resistance vs friction は効率・正確性とも**有意差なし**、選好は resistance。⚠️ 予備研究 |
| 11 | ★★★ Sun, Yao & Fu, *Crossmodal Correspondence Mediates Crossmodal Transfer from Visual to Auditory Stimuli in Category Learning*, J. Intelligence 12(9):80, 2024 | doi:10.3390/jintelligence12090080 | **(c)/(d) の機構**。4 実験・各 N≈47–48。★ pitch–elevation で転移あり（d=0.923）、⚠️ **pitch–size では転移なし（BF10=0.278＝帰無の証拠）** → ★ **意味の保存は「対応が頑健な軸に限る」条件付き** |
| 12 | Zong, Hajas et al., *Umwelt: Accessible Structured Editing of Multimodal Data Representations*, CHI 2024 | doi:10.1145/3613904.3641996 / arXiv:2403.00106 | ★ **共有の抽象データモデル → 視覚/聴覚/テキストを同格に生成**。⚠️ **触覚は無い**。GSE の IR→媒体と構造が同一 |
| 13 | Tak & Toet, *Towards Interactive Multisensory Data Representations*, IVAPP/GRAPP 2013, 558–561 | doi:10.5220/0004346405580561（全文取得済） | ★ **(b)/(e) のゼロ宣言**。逐語: 「there is currently a **lack of agreed guidelines** for their integrated design, as well as **little empirical research** in this area」 |
| 14 | Luzhnica & Veas, *Background perception and comprehension of symbols conveyed through vibrotactile wearable displays*, IUI 2019, 57–64 | doi:10.1145/3301275.3302282 | 角度 6。★ **背景（アンビエント）理解 97%**。⚠️ **多タクタ装着型 + 最適化レイアウト**＝location 変数を使用 → ★ ロック画面へ外挿不可 |
| 15 | Wang, Millet & Smith, *Designing wearable vibrotactile notifications for information communication*, IJHCS 89:24–34, 2016 | doi:10.1016/j.ijhcs.2016.01.004 | 角度 6。⚠️ 書誌のみ Crossref 検算・**本文未取得** |
| 16 | Yu & Brewster, *Evaluation of multimodal graphs for blind people*, Univ. Access Inf. Soc. 2:105–124, 2003 | doi:10.1007/s10209-002-0042-6 | (c) 周辺。★ 同一グラフを視/聴/触で提示する**系**の評価。⚠️ 比較対象は raised paper であり **「意味保存」の測定ではない** |
| 17 | Enge et al. 2023 統一用語論（★ **既登録 [P301]**） | — | ⚠️ 新規候補にしない。視+聴のみで**触覚を含まない**ことを §5 で使用 |
| 18 | Nees（★ **既登録 [P310]**）「理論はまだ無い」 | — | ⚠️ 新規候補にしない。#13 と対にする |

★ **取得ソース 18 本 / angle 6**。予算（15〜20 本・4〜6 angle）内。

## 1. 動機（★ 判断 (f) と A16）

GSE は `p_stuck` を **中間表現 (IR) → 媒体固有の実装** の 2 段で表現する。ここに 2 つの判断がぶら下がる。

- **判断 (f)**: 表現側に「媒体の能力プロファイル」を置き、各媒体が何を表現できるかを自己記述させる。
- **A16（媒体不変性）**: 同じ IR から異なる媒体へ落としたとき **意味が保存されること**を受け入れ観点に足す。

前 2 ラウンドで **視覚**（[P295] Draco / [P300] Vega-Lite）と**聴覚**（[P301] Enge et al. 統一用語論 /
[P307] Walker 心理物理スケーリング / [P308] Dubus & Bresin / [P310] Nees「理論はまだ無い」）は
形式的な写像理論の有無まで詰めた。⚠️ **触覚は 2 ラウンドとも一度も見ていない。** 本ラウンドはその穴を埋める。
また [P306] CcNav が「表現の構成規則は別ドメインへ移植できる」という楽観への反証として登録済であり、
本 RQ はその線を **モダリティ間**へ延長する。

## 2. 検証状態

- 取得ソース **18 本**（全文取得 6 本 / 書誌のみ Crossref 検算 12 本）。
- 探索 angle **6**（触覚の符号化理論 / マルチモーダル記述枠組み / クロスモーダル対応の心理物理 /
  同一データのモダリティ間比較 / 反証 angle / 通知の抽象符号としての触覚）。
- claim 抽出 **7 件** → 3 票検証で **confirmed 6 件**（3-0: 3 / 2-1: 3）、**否決 1 件**（+ 検索中に浮上した否決 4 件・§8）。
- ⚠️ 書誌はすべて **Crossref で検算**した。★ WebFetch の小モデルが Spence 2022 の**表題を誤読**した
  （「Crossmodal Correspondences: A Tutorial Review」と返した）が、Crossref で
  「Exploring Group Differences in the Crossmodal Correspondences」と訂正済。**伝聞を信じないこと。**

## 3. gate 判定（下位問い (a)〜(e) ごとに温度 1 行）

| 問い | 温度 | 1 行 |
|---|---|---|
| **(a) 触覚単独の形式的写像理論** | **確定（分類学は存在）／ 「形式言語」は不在** | ★ Griffin 2001 が **Bertin 視覚変数構文の触覚版**（3 系 10 変数 × データ型適合表）を提示し、Brewster & Brown の Tacton が符号パラメータ体系（frequency/amplitude/duration/rhythm/location/waveform）を持つ。⚠️ **Vega-Lite / Draco 相当の実行可能な仕様言語・制約解法は存在しない**。Griffin 自身が「**論理的分析であって実証ではない**」と明言 |
| **(b) 三感覚横断の統一写像理論** | **PLAUSIBLE BUT UNPROVEN** | ★ Nesbitt の **MS-Taxonomy** が「視覚化・ソニフィケーション・触覚表示を**同じ語彙**で記述する」分類学として実在し、Hogan & Hornecker 2016 が設計空間を継ぐ。⚠️ しかし**語彙はあっても規則が無い**: Tak & Toet 2013 が逐語で「lack of agreed guidelines … little empirical research」。★ 現代の実装系（Umwelt CHI 2024）は視+聴+**テキスト**で、**触覚を含まない** |
| **(c) ★★★ 意味保存の実測** | **確定（実測あり）／ 結論は「保存されない」側に傾く** | ★ **3 本の直接証拠がある**。Xu+2023 は同一データの視覚 vs 触覚で **符号の有効性順位が転写されない**と結論。Khalaila+2024 は逆に**概ね転写される**と報告（⚠️ 視覚障害者 N=11）。Sun+2024 が機構を与える: 転移は **crossmodal correspondence が頑健な軸でのみ**起きる（pitch–elevation d=0.923 / pitch–size は BF10=0.278＝**帰無の証拠**） |
| **(d) ⚠️ 反証: 個人差・文化差** | **確定** | ★ Spence 2022: Parise(2016) N=62 で **極性の一致率が偶然水準 ca.50% 〜 ほぼ完全一致まで分散**。Velasco+2016 は 44% 一致。構造的・一部の統計的対応（pitch–size）は普遍でありうるが、'Arbitrary and Artificial' な対応は普遍でない。文化差（UK vs Taiwan）は**極性ではなく切替点**に出る。⚠️ Nava+2016: pitch–height の **audiotactile 対応は幼児で弱い**＝触覚アームは視覚アームより弱い |
| **(e) 埋め方** | — | §5 参照。★ **条件を 2 つ落とせば埋まる**（三感覚→二感覚 / 統一理論→個別理論の寄せ集め）。⚠️ **アンビエント条件と GSE の媒体条件は落としても埋まらない＝ゼロ** |

## 4. claim と 3 票検証

票の視点: **① 内的妥当性** / **② GSE の「スマホ・ロック画面・アンビエント」設定への外挿** / **③ 効果量・再現性の頑健性**

| # | claim | 出典 | ① | ② | ③ | 判定 | 温度 |
|---|---|---|---|---|---|---|---|
| C1 | 触覚には Bertin 型の**変数分類学**が存在し、データ型（nominal / ordinal）への適合規則まで書かれている | Griffin 2001 | ○ | ✕ | △ | **2-1** | 確定 |
| C2 | 視/聴/触を**同じ語彙**で記述する分類学（MS-Taxonomy）は 2003 年から存在する | Nesbitt 2003/2004 | ○ | △ | ○ | **3-0** | 確定 |
| C3 | ★★★ 同一データを視覚→触覚へ落とすと、**符号の有効性順位は転写されない** | Xu, Williams & Wall 2023 | ○ | △ | △ | **2-1** | 確定 |
| C4 | ★★★ モダリティ間の意味の転移は、**基底の crossmodal correspondence が頑健な軸に限って**成立する | Sun, Yao & Fu 2024 | ○ | ○ | ○ | **3-0** | 確定 |
| C5 | ★★★ クロスモーダル対応の**極性の合意率は偶然水準まで落ちうる**（普遍性は対応の種類に依存する） | Spence 2022 | ○ | ○ | ○ | **3-0** | 確定 |
| C6 | 三感覚を統合した設計**規則**（guidelines）は存在せず、実証研究も乏しい | Tak & Toet 2013 | ○ | ○ | △ | **2-1** | 確定（ゼロ宣言） |
| C7 | アンビエント条件でも触覚は高精度（97%）で抽象記号を伝えられる | Luzhnica & Veas 2019 | ○ | ✕ | △ | **1-2 → 否決** | §8 |

### 留保（2-1 の内容を明記）

- **C1 の ✕（票②）**: ⚠️★★★ **Griffin の syntax は GSE の媒体でほぼ消滅する。**
  3 系 10 変数のうち、kinesthetic（resistance / friction / kinesthetic location）は力覚デバイス前提で
  ロック画面に無く、visual-analog（size&elevation / shape / texture-grain / orientation）は**空間的に
  分解された触覚面**を前提とするので単一振動子に無い。touch 系も pressure / temperature は不可で、
  **実質 vibration（と flutter＝その下位）しか残らない**。→ ★ **10 変数 → 1 変数への縮退**。
  ⚠️ これは C1 を弱めると同時に、**判断 (f)「媒体の能力プロファイル」を強く支持する**。
- **C3 の △（票②③）**: N=12 の大学生・**swell paper の能動的探索**で、GSE のアンビエント条件と粒度が違う。
  かつ Khalaila+2024（N=11・視覚障害者）は**逆向きの結論**を出しており、★ 再現性は確立していない。
  ⚠️ ただし **2 本とも「触覚は視覚と同じ設計指針でよい」を支持していない**点では一致する
  （Khalaila の参加者自身が「視覚由来のガイドラインではなく視覚障害者向けに設計された符号がほしい」と述べた）。
- **C6 の △（票③）**: 2013 年の position paper であり、以後 [P301] Enge et al. 2023（視+聴）や
  Umwelt 2024 が部分的に進めている。★ **視+聴に限れば C6 はもはや成り立たない**。
  ⚠️ **触覚を含めた三者では今も成り立つ**（Umwelt は触覚を含まない）。

## 5. ⚠️ ゼロの検算表

| 落とした条件 | 埋まるか | 代表例 |
|---|---|---|
| 三感覚統合 → 二感覚（視覚＋聴覚）でも可 | ★ **埋まる** | [P301] Enge et al. 2023（substrate / mark / channel を聴覚へ移植）、Umwelt CHI 2024 doi:10.1145/3613904.3641996（**共有の抽象データモデル**から視覚・ソニフィケーション・テキストを**同格に**生成。⚠️ 触覚なし） |
| 統一理論 → モダリティごとの個別理論の寄せ集めでも可 | ★ **埋まる** | 視覚 = Bertin / [P300] Vega-Lite、聴覚 = [P307] Walker、触覚 = Griffin 2001 + Brewster & Brown 2004。⚠️ ただし**三者を貫く規則は無い**（Tak & Toet 2013 の逐語） |
| 意味保存の**実測** → 理論的主張だけでも可 | ★ **埋まる（が逆向き）** | ⚠️ **実測の方が先に存在する**（Xu+2023 / Khalaila+2024 / Sun+2024）。理論的主張（Nesbitt / Vasconcellos）は**実証されていない**。→ ★ 「理論だけで良い」に条件を落とすと**弱い方に落ちる** |
| アンビエント → 能動的探索でも可 | ★ **埋まる** | Xu+2023・Khalaila+2024（swell paper の能動探索）、Yu & Brewster 2003（力覚マウスで探索）。⚠️ **アンビエント条件のままだと該当ゼロ**（Luzhnica+2019 は背景条件だが多タクタ装着型） |
| 汎用データ → 特定用途（ナビ・医療）専用でも可 | ⚠️ **部分的にしか埋まらない** | Griffin 2001 は地理データ専用、Yu & Brewster 2003 はグラフ専用。★ **どれも「1 本の連続スカラの強度」という GSE の IR 形とは合わない**（GSE が落とすのは多次元データセットではなく `p_stuck` 1 軸） |
| **★ 上記を全部保ったまま** = 三感覚 × 統一理論 × 実測 × アンビエント × 汎用 | ⚠️★★★ **ゼロ** | **該当研究なし。ゼロはゼロと書く。** |

⚠️★★★ **もう 1 つのゼロ**: GSE の媒体条件（**スマホのロック画面・単一振動子・常在的/周辺的**）に
外挿できる触覚の先行は、取得した 18 本の中に **1 本も無い**。
（Griffin / Dullaert は力覚デバイス、Luzhnica は多タクタ装着型、Xu / Khalaila / Yu は能動探索。）

## 6. ★★★ A16（媒体不変性）への含意

### 結論: **条件付きで書ける**

★ **書けるのは「観点の形」であって「前提としての不変性」ではない。**

#### 書ける部分（根拠あり）

1. **測り方の先行がある。** Cleveland & McGill 型の符号復号課題を**別モダリティで再現する**という
   手続きは Xu+2023 と Khalaila+2024 が実際に回している。★ **「同じ IR を別媒体へ落として、
   復号された値／順位が一致するか」を受け入れ試験として書くことは、方法論的に先行に接地できる。**
2. **成立条件が特定されている。** Sun+2024 は、意味（学習したカテゴリ構造）の転移が
   **基底の crossmodal correspondence が頑健な軸に限って**起きることを 4 実験で示した
   （pitch–elevation で d=0.923、pitch–size では **BF10=0.278＝帰無の積極的証拠**）。
   → ★ **A16 は「軸ごとに」判定する観点として書ける。「表現全体が不変か」では書けない。**

#### 書けない部分（根拠が反対を向いている）

3. ⚠️ **「不変性が成り立つ」という前提は支持されていない。** Xu+2023 は
   「data physicalizations will require **different** design guidance than that developed for visual
   encodings」と結論し、符号の有効性順位の転写を否定した。★ A16 を
   「不変であるべし」という**要求**として書くと、先行に反する要求を書くことになる。
4. ⚠️ **極性すら合意されない。** Spence 2022 経由の Parise(2016)（N=62）で、極性の一致率は
   **偶然水準 ca.50% から near-perfect まで分散**する。→ ★ 「`p_stuck` が高い＝振動が強い／速い」の
   極性が全被験者で共有される保証は無い。**極性は測定対象であって仮定ではない。**
5. ⚠️★★★ **GSE の媒体条件への外挿元がゼロ。** Griffin の 10 変数はロック画面で **1 変数に縮退**し、
   Luzhnica+2019 の 97% は**多タクタ装着型**の成績で単一振動子に外挿できない。
   → ★ **触覚を A16 の対象媒体に含めるなら、自前で測る以外に根拠は無い。**

#### ★ 推奨する書き方（そのまま ADR に落とせる形）

> **A16（媒体不変性）**: 中間表現の**各軸について**、媒体 A と媒体 B に落とした結果が
> **同一の順序関係と同一の極性**で復号されることを確認する。⚠️ 不変性は**仮定せず**、
> 軸ごとに**測定して合否を出す**。★ 不変でない軸が見つかった場合は、**媒体の能力プロファイル
> （判断 (f)）に「この軸は当媒体では表現しない」と記録する**のが正しい帰結であり、
> 媒体側の実装を無理に合わせない。

★ この形なら C3・C4・C5 と矛盾せず、**判断 (f) と A16 が同じ機構の表裏になる**
（不変でない軸を検出する装置が A16、検出結果を保持する場所が (f)）。

#### ⚠️ 無条件に「書ける」にするために足りないもの

- ★ **ロック画面級の単一振動子 × アンビエント条件**で、IR の 1 軸（`p_stuck` の強度）が
  視覚と触覚で**同順に**復号されることの実測。→ **先行ゼロ。自前で取るしかない。**
- ★ GSE の被験者コホートでの **polarity survey**（Parise 型・N≥50）。
  「強い `p_stuck` ↔ 速い／強い振動」の極性合意率が偶然水準を有意に超えるか。
- ⚠️ 触覚を実装しない限り、A16 は当面 **視覚（PC オーバーレイ）× 視覚（スマホロック画面）**の
  **同一モダリティ間**の観点に留まる。★ **同一モダリティ間なら本 RQ の反証は効かない**
  （Xu+2023 も Sun+2024 も Spence 2022 も、**モダリティを跨いだとき**の話である）。
  → ★ **これが現実的な着地点。** 触覚は A16 の対象媒体に入れない。

## 7. ★ 登録候補（DOI/arXiv/URL・N・設計・効果量・接地案）

⚠️ 既登録 [P295] / [P300] / [P301] / [P306] / [P307] / [P308] / [P310] は**含めていない**。
★ メインは DOI / arXiv ID を key に照合すること。

| # | 書誌 | key | N・設計・効果量 | GSE への接地案 |
|---|---|---|---|---|
| **D1** | Griffin, A. L. (2001). *Feeling It Out: The Use of Haptic Visualization for Exploratory Geographic Analysis*. **Cartographic Perspectives**, No. 39 (Spring 2001), 12–29. | https://cartographicperspectives.org/index.php/journal/article/view/cp39-griffin （OA・全文確認） | 実証なし。**論理的分析による設計提案**。touch(vibration/flutter/pressure/temperature) + kinesthetic(resistance/friction/kinesthetic location) + visual-analog(size&elevation/shape/texture-grain/orientation) × nominal/ordinal 適合表 | ★ **判断 (f) の直接の型**。「媒体の能力プロファイル」を **変数 × データ型の適合表**として書く先行。⚠️ かつ **GSE の媒体では 10→1 変数に縮退する**ことを示す材料 |
| **D2** | Nesbitt, K. V. (2004). *MS-Taxonomy: a conceptual framework for designing multi-sensory displays*. **Proc. 8th Int. Conf. Information Visualisation (IV 2004)**. | doi:10.1109/IV.2004.1320213 | 分類学（spatial / temporal / direct metaphor）。★ 視・聴・触を**同一語彙**で記述 | ★ (b) の唯一の三感覚統一枠。⚠️ **本文未取得**（§9）→ **provisional 登録を推奨** |
| **D3** | Nesbitt, K. V. (2003). *Designing Multi-sensory Displays for Abstract Data*. PhD thesis, School of IT, Univ. of Sydney. | https://ses.library.usyd.edu.au/handle/2123/4135 | MS-Taxonomy の原典 | 同上。⚠️ **PDF 403**（§9）→ **provisional** |
| **D4** | ★★★ Xu, Z., Williams, K., & Wall, E. (2023). *Let's Get Vysical: Perceptual Accuracy in Visual and Tactile Encodings*. arXiv. | arXiv:2308.04392 / doi:10.48550/arXiv.2308.04392 | **N=12**（大学生）。同一データを SVG(視覚) vs swell paper(触覚)。Cleveland&McGill 型復号課題。★ 視覚が精度・認知負荷・自己評価で優位。**触覚は視覚対応物と復号精度が異なる** | ★★★ **A16 の直接の反証側**。「順位は転写されない」＝ A16 を*要求*として書けない根拠 |
| **D5** | ★★★ Khalaila, A., Harrison, L., Kim, N. W., & Cashman, D. (2024). *"They Aren't Built For Me": A Replication Study of Visual Graphical Perception with Tactile Representations of Data for Visually Impaired Users*. arXiv. | arXiv:2410.08438 / doi:10.48550/arXiv.2410.08438 | **N=11**（視覚障害者）・4 チャート型・swell form 印刷。Cleveland&McGill の触覚再現。★ **より速く、同等〜優位の精度** | ★ **D4 と逆向きの結論**。⚠️ **対称性の担保として必ず併記する**。両者の一致点は「視覚由来ガイドラインをそのまま使うべきでない」 |
| **D6** | ★★★ Sun, Y., Yao, L., & Fu, Q. (2024). *Crossmodal Correspondence Mediates Crossmodal Transfer from Visual to Auditory Stimuli in Category Learning*. **Journal of Intelligence**, 12(9), 80. | doi:10.3390/jintelligence12090080 | **4 実験・各 N≈47–48**。視覚（elevation / size）でカテゴリ学習 → 聴覚（pitch）へ転移。★ pitch–elevation: 一致条件が有意に高精度 **t(46)=3.198, p=.013, d=0.923**。⚠️ pitch–size: 転移なし **BF10=0.278** | ★★★ **A16 の成立条件そのもの**。「意味の保存は対応が頑健な軸に限る」→ **A16 を軸ごとの観点として書く**根拠 |
| **D7** | ★★★ Spence, C. (2022). *Exploring Group Differences in the Crossmodal Correspondences*. **Multisensory Research**, 35(6), 495–536. | doi:10.1163/22134808-bja10079 （CC BY・全文確認） | レビュー。★ Parise(2016) **N=62** で極性一致率が **ca.50%（偶然水準）〜 near-perfect** に分散。Velasco+2016 は **44%** 一致。⚠️ Nava+2016: pitch–height の **audiotactile 対応は幼児で弱い** | ★★★ **(d) の主柱**。「極性は仮定でなく測定対象」の根拠。★ 4 分類（structural / statistical / semantic / hedonic）は、**どの軸なら不変性を期待してよいか**の判断枠になる |
| **D8** | Tak, S., & Toet, A. (2013). *Towards Interactive Multisensory Data Representations*. **Proc. IVAPP/GRAPP 2013**, 558–561. | doi:10.5220/0004346405580561 （全文確認） | position paper。逐語: 「there is currently a **lack of agreed guidelines** for their integrated design, as well as **little empirical research** in this area」 | ★ **(b) のゼロ宣言**。[P310] Nees（聴覚の「理論はまだ無い」）の**三感覚版**として対にできる |
| **D9** | Zong, J., Hajas, D., et al. (2024). *Umwelt: Accessible Structured Editing of Multimodal Data Representations*. **CHI 2024**. | doi:10.1145/3613904.3641996 / arXiv:2403.00106 | **N=5**（blind/low-vision エキスパート）。★ **共有の抽象データモデル**から視覚・ソニフィケーション・テキストを**同格に**生成、クエリ述語を全モダリティで reify | ★★★ **GSE の IR→媒体と構造が同一の実装先行**。⚠️ **触覚を含まない**＝「三感覚→二感覚に落とせば埋まる」の実例 |
| **D10** | Hogan, T., & Hornecker, E. (2016). *Towards a Design Space for Multisensory Data Representation*. **Interacting with Computers**, 29(2). | doi:10.1093/iwc/iww015 | ⚠️ 抽象は publisher により elided、**本文未取得** | (b) の補強。⚠️ **provisional 推奨** |
| **D11** | Brewster, S. A., & Brown, L. M. (2004). *Tactons: Structured Tactile Messages for Non-Visual Information Display*. **AUIC 2004**, CRPIT Vol. 28, 15–23. | http://eprints.gla.ac.uk/3443/ （AUIC 版に DOI なし。CHI'04 EA 版は doi:10.1145/985921.985936） | 設計提案。符号パラメータ: frequency / amplitude / duration / rhythm / location / waveform | ★ (a) の古典。**触覚側の「チャネル」列挙**として (f) の能力プロファイルの語彙に使える |
| **D12** | Luzhnica, G., & Veas, E. (2019). *Background perception and comprehension of symbols conveyed through vibrotactile wearable displays*. **IUI 2019**, 57–64. | doi:10.1145/3301275.3302282 | ★ 背景（並行課題下）で **97%** の文字・単語認識。二重課題で主課題性能も低下せず | ⚠️★★★ **外的妥当性の反例として登録すべき**。多タクタ装着型＋最適化レイアウト＝**location 変数を使用**。★ ロック画面の単一振動子には外挿不可、を示す証拠 |
| **D13** | Dullaert, S., Ranasinghe, C., Degbelo, A., & Bouali, N. (2024). *Data Physicalization with Haptic Variables: Exploring Resistance and Friction*. **CHI EA 2024**. | doi:10.1145/3613905.3651011 （green OA: research.utwente.nl/files/382269076/chi24-539.pdf） | 予備研究。resistance vs friction、minima/maxima/cluster 課題。★ **効率・正確性とも有意差なし**、選好は resistance | (a) の実証側。⚠️ **kinesthetic 変数＝ロック画面に無い**。★ Griffin の syntax が 20 年後も**部分的にしか実証されていない**ことの証拠 |
| **D14** | Yu, W., & Brewster, S. (2003). *Evaluation of multimodal graphs for blind people*. **Universal Access in the Information Society**, 2, 105–124. | doi:10.1007/s10209-002-0042-6 | 3 段階評価。同一グラフを視/聴/触で提示する系。★ 多モーダル線グラフは raised paper より有意に高精度、⚠️ **探索時間は有意に遅い** | (c) 周辺。⚠️ 比較対象が raised paper であり **「モダリティ間の意味保存」の測定ではない**。★ 参考止まり |
| **D15** | Wang, Y., Millet, B., & Smith, J. L. (2016). *Designing wearable vibrotactile notifications for information communication*. **IJHCS**, 89, 24–34. | doi:10.1016/j.ijhcs.2016.01.004 | ⚠️ **本文未取得**（書誌のみ Crossref 検算） | 角度 6 の補強。⚠️ **provisional 推奨、または見送り** |

★ **優先度**:
- **必須** = **D4 / D5 / D6 / D7**（A16 の直接証拠・反証・成立条件）
- **次点** = **D1 / D8 / D9**（判断 (f) の型と (b) のゼロ）
- **外的妥当性の反例として** = **D12**
- **provisional / 見送り** = D2 / D3 / D10 / D14 / D15（本文未取得）

## 8. ⚠️ 否決リスト

| 主張 | 票 | 否決理由 |
|---|---|---|
| 「クロスモーダル対応は普遍だから、同じ IR を任意の媒体へ落としても意味は保たれる」 | **0-3** | ⚠️ 3 方向から反証される。Spence 2022（極性一致率が **偶然水準 ca.50%** まで落ちる）／ Sun+2024（pitch–size では転移せず **BF10=0.278＝帰無の証拠**）／ Xu+2023（符号の有効性順位が転写されない）。★ **A16 を無条件の前提として書くことはできない** |
| 「触覚は視覚の代替として同等に使える（だから視覚の設計指針を流用してよい）」 | **1-2** | ⚠️ Xu+2023 で触覚は精度・認知負荷とも劣位。Khalaila+2024 は同等〜優位だが **視覚障害者コホート**であり、健常者のアンビエント条件へ外挿できない。★ 両論文とも「視覚由来ガイドラインの流用」を明示的に否定している |
| C7「アンビエント条件でも触覚は高精度（97%）で抽象記号を伝えられる」 | **1-2** | ⚠️ Luzhnica+2019 の 97% は **多タクタ装着型ディスプレイ + 最適化レイアウト**の成績で、**location（空間）変数を使用**している。★ GSE のロック画面（単一振動子・location 変数なし）へ外挿できない。内的妥当性は高い（票①○）が外挿が壊れる |
| 「Vasconcellos 1991 のように Bertin の視覚変数をそのまま触覚へ翻訳すればよい」 | **0-3** | ⚠️★★★ **Griffin 2001 が明示的に反証している**: 翻訳の結果 **両感覚で知覚できる変数しか残らず**、触覚固有（temperature / pressure / kinesthetic）が丸ごと落ちた。★ **これは判断 (f) の必要性の直接の論拠**であり、単純な媒体不変性の追求が**媒体固有の表現力を捨てる**ことを示す |
| 「三感覚を統合した設計規則は既に整備されている」 | **0-3** | ⚠️ Tak & Toet 2013 が逐語で否定（「lack of agreed guidelines … little empirical research」）。★ 2024 年の最先端（Umwelt）でも**触覚は含まれない** |

## 9. ⚠️ 取得できなかったもの

| 対象 | 症状 | 対処 |
|---|---|---|
| Nesbitt (2004) *MS-Taxonomy*, IV 2004 本文 | **IEEE Xplore ペイウォール**。著者版・arXiv・HAL いずれも見つからず。Semantic Scholar の abstract は `none` | ⚠️ **内容は二次記述に依存**。★ 「spatial / temporal / direct metaphor の 3 分類」「全感覚に共通の語彙」までは複数出典で一致するが、**逐語確認はできていない**。→ **provisional 登録を推奨** |
| Nesbitt (2003) PhD thesis PDF | ses.library.usyd.edu.au の handle ページが **403**、PDF 直リンクは **HTML を返した**（239 bytes） | 同上。⚠️ **MS-Taxonomy が実証的に検証されたかは未確認のまま** |
| Hogan & Hornecker (2016) 本文 | OUP ペイウォール。★ Semantic Scholar の abstract は **publisher により elided** | 書誌のみ Crossref 検算済（Interacting with Computers 29(2), 2016）。**本文の主張は未確認** |
| Dullaert+ (2024) 本文 | ACM DL が **403**（Cloudflare） | ★ Semantic Scholar 経由で **green OA PDF の所在**と **abstract 全文**を取得。要旨レベルでは確認済 |
| Wang, Millet & Smith (2016) 本文 | Elsevier ペイウォール（Unpaywall 未試行） | 書誌のみ。⚠️ **登録するなら provisional** |
| Vasconcellos (1991) 原典 | ★ **Griffin 2001 経由の二次言及のみ**。ICA 会議録で入手困難 | ⚠️ **単独では登録しない**。Griffin の記述として引用するのが安全 |

### ★ 次ラウンドへの「やり残し」

1. ⚠️★★★ **ロック画面級の単一振動子 × アンビエント条件での意味保存の実測は先行ゼロ。**
   → 文献では埋まらない。**自前で測る**か、**A16 の対象媒体から触覚を外す**かの二択。
2. ★ **同一モダリティ間（PC 視覚 → スマホ視覚）の媒体不変性**は本 RQ の反証（すべてモダリティ跨ぎ）に
   当たらない。→ ★ **そこに限定した先行（レスポンシブ可視化・小画面での符号劣化・responsive vis）**を
   次ラウンドで引くべき。**これが GSE にとって最も実効的な次の一手。**
3. ★ Nesbitt MS-Taxonomy の**逐語確認と実証の有無**。IEEE 経由が要る。
4. ★ Spence 2022 の 4 分類（structural / statistical / semantic / hedonic）を GSE の IR の軸に当てて、
   **どの軸なら不変性を期待してよいか**を先に机上で仕分ける（実測の前の設計作業）。
