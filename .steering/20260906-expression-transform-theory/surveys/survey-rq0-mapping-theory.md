# サーヴェイ: RQ0 — データ→表現写像の形式理論は存在するか

> 2026-09-06 実行。用途: `.idea/20260905-data-to-social-media-expression-theory.md` の
> go/no-go 判定（最優先ラウンド）。名前空間候補: `P`（理論基盤）。
> **本ファイルは登録候補の下書きであり、`docs/references.md` / `docs/literature/_index.md` は未編集**
> （citation-ssot / literature-review の規約により、採番・append はメインが直列で行う）。

## 動機

`.idea` メモが提案する「観測値・潜在的関係・時間変化・不確実性・媒体制約を複数段階で変換し、
意味構造と媒体実装を分離する中間表現層」が、既存の可視化/音楽インタフェース/ソニフィケーション/
データ物理化の各分野で **形式的（代数・文法・設計空間）にすでに定式化されていないか**を確認する。
repo は既に [P113] Informative Art の逐語
*"a mapping between design structure and information structure rather than a effective presentation
of information content"* を持っており、これが `.idea` の中核原理と同一命題に見えることが動機。

## 検証状態

- 探索 angle: 6（可視化系統3・NIME系統2・ソニフィケーション系統4・データ物理化系統2・
  横断統一理論系統3・反証系統込み。重複除去後は概ね RQ の (a)〜(e) を横断）
- 取得ソース: 17 件（新規候補。既出 [P48][P49][P113] は重複潰し済みで対象外）
- claim 抽出: 4 件（下記）。うち 3 件 confirmed（1 件は 3-0、2 件は 2-1 で留保付き）、
  1 件は否決対象を含む（Caiola et al. 2022 の位置づけ）
- 否決: 1 件（下記否決リスト）

## Gate 判定（要点先出し・下位問い別エビデンス温度）

- **(a) 可視化分野の写像代数**: **確定**。GoG (Wilkinson) / Vega-Lite (Satyanarayan et al. 2017) /
  AVD (Kindlmann & Scheidegger 2014) は実在し、実装（ggplot2, Tableau, Vega-Lite）を伴う
  15–25 年の成熟した形式理論。ただし Munzner (2009) は「マッピングの代数」ではなく
  「設計・検証の階層プロセスモデル」であり、この 4 者を同列の「写像代数」として扱うと過大。
- **(b) NIME マッピング層**: **確定**（ただし内部で温度差あり）。Hunt & Wanderley (2002) は
  taxonomic（one-to-one/many-to-many 等の分類）であり数学的に厳密ではない。
  Van Nort, Wanderley & Depalle (2014) が初めて「関数・位相空間」として数学的定式化。
  = **NIME の「マッピング層」概念自体は 2000 年代初頭からあるが、形式化の完成は 2014 年**。
- **(c) ソニフィケーションの parameter mapping 理論**: **混合（確定するのは「未成熟」の方）**。
  Hermann (2008) / Grond & Berger (Sonification Handbook Ch.15) は記法・taxonomy レベルの
  formalization に留まる。★★ **分野の内部者自身が「理論はまだ未成熟」と明言**
  (Nees 2019 → Enge et al. 2023 が追認)。Dubus & Bresin (2013) の系統レビュー（179 論文・
  495 マッピング事例）も「マッピング効果の適切な評価は少数の論文でしか行われていない」と報告。
  → 可視化分野と違い、**ソニフィケーションは「理論はあるが未成熟であることが分野内で合意されている」**。
- **(d) [P49] データ物理化設計空間**: 本文取得は本ラウンドでも失敗
  （arXiv abs ページ 403 / PDF はサイズ超過で WebFetch 不可）。★ 新規に見つけた **Jansen et al. (2015)**
  が [P49] の先行（同じく 47 事例の設計空間・context/structure/interaction の 3 軸）であり、
  **7 年隔てて独立に「分野横断の統合は欠けている」と自認**している点が [P49] の主張を補強する
  二次的裏付けになる。★ [P49] 自体の温度は repo 記載のまま「判定不能に近い（本文未確認）」を維持。
- **(e) 反証 angle**: ★★★ **確認された「ゼロ」**。視覚・聴覚・物理を横断し、かつ不確実性・
  時間変化する潜在状態を統一的に扱う形式理論は、17 件の探索コーパス中に **存在しなかった**。
  最も接近した試み (Enge et al. 2023) でも、対象は視覚+聴覚の 2 モダリティのみ・物理化は含まない・
  不確実性の言及ゼロ・時間は「常に線形」と明記された静的モデル・経験的検証なし（6–9 事例の
  事後分析のみ）。→ **「弱い支持」に丸めない。ゼロはゼロ**。

---

## 登録候補の出典一覧（citation-ssot 形式の下書き。番号は仮）

> N・設計・効果量列は「理論・設計空間論文」には該当しないものが多い（RQ の性質上、
> 効果検証ではなく理論の存在自体を問うているため）。該当する場合のみ記入。

| 仮 key | 出典 | N/設計 | 効果量/主要所見 | 1 行の意味 |
|---|---|---|---|---|
| cand:wilkinson-gog | Wilkinson, L. — *The Grammar of Graphics* (2nd ed.), Springer, 2005 (初版 1999) | — (理論書) | 7 直交要素 (Variables/Algebra/Scales/Statistics/Geometry/Coordinates/Aesthetics) でデータ→視覚属性の写像を規定 | 可視化分野の写像文法の起点。ggplot2/Tableau/Vega-Lite の直接の祖 |
| cand:satyanarayan-vegalite-2017 | Satyanarayan, Moritz, Wongsuphasawat, Heer — Vega-Lite: A Grammar of Interactive Graphics, IEEE TVCG 23(1):341-350, 2017. DOI 10.1109/TVCG.2016.2599030 | — | 視覚エンコーディング規則 + レイヤー/マルチビュー合成のための **composition algebra** を定義 | GoG に「合成代数」を実装レベルで追加した後継。現行 Vega-Lite の理論的核 |
| cand:kindlmann-scheidegger-2014 | Kindlmann & Scheidegger — An Algebraic Process for Visualization Design, IEEE TVCG 20(12):2181-2190, 2014 (VIS'14 Honorable Mention). DOI 10.1109/TVCG.2014.2346325 | — | データの数学的構造・計算機内表現・知覚の数学的記述の3層を **対称性 (symmetry) の保存/破壊**として定式化する Algebraic Visualization Design (AVD) | 可視化分野で最も厳密に「代数」を名乗る写像理論。データ変化↔画像変化の対応を群構造で扱う |
| cand:munzner-2009 | Munzner — A Nested Model for Visualization Design and Validation, IEEE TVCG 15(6):921-928, 2009. DOI 10.1109/TVCG.2009.111 (PMID 19834155) | — | 問題領域の特定→データ/タスク抽象化→視覚エンコーディング設計→アルゴリズム実装の4層ネスト構造。上流の誤りは下流に伝播する | ★ 留保: これは「写像の代数」ではなく「設計・検証プロセスの階層モデル」。同列に「写像理論」と呼ぶと過大 |
| cand:bertin-semiology | Bertin, J. — *Sémiologie Graphique* (1967) / *Semiology of Graphics* (英訳 1983, Univ. of Wisconsin Press) | — | retinal variables (position/size/color等) の分類とマーク概念を最初に体系化 | 現代の全ての可視化写像理論(GoG/Munzner/AVD)が明示的に依拠する祖形。★ 前計算機時代の分類体系であり、合成演算子を持つ現代的な意味の「代数」ではない |
| cand:hunt-wanderley-2002 | Hunt & Wanderley — Mapping Performer Parameters to Synthesis Engines, Organised Sound 7(2):97-108, 2002. DOI 10.1017/S1355771802002030 | — | one-to-one/one-to-many/many-to-one/many-to-many の写像分類 + explicit two-layer mapping (演奏パラメータ→中間パラメータ→合成パラメータ) | NIME の「マッピング層」概念の起点。★ **taxonomic であり数学的に厳密ではない**（本ラウンドで一次 PDF 確認済み） |
| cand:vannort-wanderley-depalle-2014 | Van Nort, Wanderley & Depalle — Mapping Control Structures for Sound Synthesis: Functional and Topological Perspectives, Computer Music Journal 38(3):6-22, 2014. DOI 10.1162/COMJ_a_00253 | — | 写像を **controller パラメータ空間→sound パラメータ空間の関数**として位相幾何学的に定式化 | NIME で唯一、写像を数学的関数として明示的に定式化した文献。「classical view of mapping as parameter association を拡張する」と自ら位置づける |
| cand:hermann-2008-taxonomy | Hermann — Taxonomy and Definitions for Sonification and Auditory Display, Proc. ICAD 2008, Paris | — | ソニフィケーション手法の分類・定義を整理 | ソニフィケーション分野の用語論的基盤。★ 分類であり写像を関数として定式化してはいない |
| cand:grond-berger-2011-ch15 | Grond & Berger — Parameter Mapping Sonification, Ch.15 in *The Sonification Handbook* (Hermann, Hunt, Neuhoff eds.), 2011 | — | データチャネル→音響合成パラメータの形式化された記法 (salience 順の写像表記法) を提示 | Parameter Mapping Sonification (PMSon) の標準的設計指針。★ 記法レベルの formalization であり公理系・合成演算子は持たない |
| cand:dubus-bresin-2013 | Dubus & Bresin — A Systematic Review of Mapping Strategies for the Sonification of Physical Quantities, PLoS ONE 8(12):e82491, 2013. DOI 10.1371/journal.pone.0082491 | **N=179 論文をレビュー、495 マッピング事例を抽出**（系統的レビュー） | pitch が最頻用の聴覚次元。★★ **「マッピングの妥当性を適切に評価した論文はごく一部に留まる」**と報告 | ★ 反証寄り: 形式理論の存在が実務上の系統的評価を保証しない。理論と実践の乖離を定量的に示す唯一の系統レビュー |
| cand:nees-2019-eight-components | Nees — Eight Components of a Design Theory of Sonification, Proc. ICAD 2019 | — | Gregor & Jones の設計理論8要素枠組みでソニフィケーション理論を検討 | ★★★ 逐語 **"sonification theory remains so underdeveloped that even the path to advance theory-building for sonification remains unclear"**。分野の内部者による「理論はまだ無い」宣言 |
| cand:enge-rind-2023-unified-terminology | Enge, Rind, Iber, Höldrich, Aigner — Towards a unified terminology for sonification and visualization, Personal and Ubiquitous Computing, 2023. DOI 10.1007/s00779-023-01720-5 (PMC10589160) | 6–9 件の既存デザインの事後分析のみ。ユーザースタディなし | 可視化理論 (substrate/mark/channel) をソニフィケーションへ移植し、1D 音響マークを `t˚=f(k)`, `c˚(t˚)=g(x)` として数式定義。★★★ 著者自身が Gregor&Jones の8要素のうち**「constructs のみ」を扱うと明言**し、Nees (2019) を引いて理論の未成熟を追認 | ★★★ 本ラウンド最重要所見: 「視覚+聴覚の統一理論」への**最も近い試み**だが、物理化は含まず・不確実性は皆無・時間は「常に線形」と明記された静的モデル・経験的検証なし |
| cand:caiola-lenzi-ricco-2022 | Caiola, Lenzi, Riccò — Audiovisual sonifications: A design map for multisensory integration in data representation, DRS2022 Bilbao | **N=80 件の audiovisual sonification 作品**を現象学的分析 | 「クロス感覢デザインマップ」（感覚間対応のパターン集）を生成。検証可能な仮説を提案する段階 | ★ 質的パターン集であり代数的定式化ではない（否決リスト参照） |
| cand:jansen-dragicevic-2015 | Jansen, Dragicevic, Isenberg, Alexander, Karnik, Kildal, Subramanian, Hornbæk — Opportunities and Challenges for Data Physicalization, CHI 2015. DOI 10.1145/2702123.2702180 | **N=47 件のデータ物理化事例**を系統的レビュー | context/structure/interaction の3軸設計空間を提示。逐語 **"research currently lacks a synthesis across the different communities"** | [P49] (Bae et al. 2022) の先行にあたる同型の設計空間論文。★★ **7 年隔てて独立に同じ「統合の欠如」を自認**しており、[P49] の主張の頑健性を補強する |
| cand:thomson-maceachren-2005 | Thomson, Hetzler, MacEachren, Gahegan, Pavel — A Typology for Visualizing Uncertainty, Proc. SPIE Visualization and Data Analysis, 2005 | — | accuracy/precision/completeness/consistency/lineage/currency/credibility/subjectivity/interrelatedness の不確実性次元を整理し、位置・属性・時間の軸に対応させる typology | 不確実性の可視化理論は**独立した別サイロ**として存在し、GoG/Vega-Lite/AVD の写像代数とは統合されていない（=不確実性を統一的に扱う写像理論は不在という反証角の補強） |

---

## 否決リスト

- **否決 (1-2)**: 「Caiola, Lenzi & Riccò (2022) の cross-sensory design map は、視覚↔聴覚間の
  写像を代数的に定式化した」— **否決**。80 件の現象学的（質的）分析によるパターン集であり、
  著者ら自身が「研究領域向けに検証可能な仮説を提案する」段階と位置づけている。合成演算子・公理・
  関数定義を持たない。→ カード本体には「代数的定式化の実例」として書かない。「設計語彙・
  パターン集」の温度でのみ引用可（[P45][P54][P67][P103] と同じ扱い）。

---

## Gate 判定（結論）

1. **各モダリティ単独では、形式的な写像理論は既に存在する**（可視化=確定・成熟 / NIME=確定だが
   数学的定式化の完成は 2014 年 / ソニフィケーション=記法レベルで存在するが分野内で「未成熟」と
   自認されている）。→ `.idea` が「データを色・音・形へ変換する理論」を**単一モダリティ内で**
   ゼロから作る、という前提では書けない。
2. **`.idea` の中核原理「意味構造と媒体実装の分離」自体は新規ではない**。[P113] Redström et al.
   (2000, Informative Art) が単一モダリティ(視覚)で逐語 *"a mapping between design structure and
   information structure rather than a effective presentation of information content"* として
   既に表明済み（repo 既登録・active）。→ **再発明**。この一節を「新規理論」として書いてはならない。
3. ★★★ **しかし、視覚・聴覚・物理を横断し、かつ不確実性・時間変化する潜在状態を統一的に扱う
   形式理論は、本ラウンドの探索コーパス（17 件）中に存在しなかった（確認されたゼロ）**。
   最も近い試み (Enge et al. 2023) は 2 モダリティ限定・物理化なし・不確実性ゼロ・時間は静的・
   検証なしで、`.idea` が要求する範囲（観測値・潜在的関係・時間変化・不確実性・媒体制約の
   複数段階変換 + 3 媒体以上）を満たさない。

**→ go/no-go: 条件付き go（ただし再発明箇所の切除が必須）**

- ★ 出発点は [P113]（構造の写像という原理）であり、「初めて分離した」と書かない。
- ★ 各モダリティの既存形式理論 (GoG/Vega-Lite/AVD, Hunt&Wanderley/Van Nort, Hermann/Grond&Berger)
  を先行として明示的に引用し、**理論を車輪の再発明せず借用**する（`.idea` §1.1 の「仮の名称」段階は
  この借用を経ていない状態で書かれている）。
- ★ ソニフィケーション分野が自ら「理論は未成熟」(Nees 2019) と認めている以上、GSE が音チャネルの
  写像理論を持ち出す際は**その分野の理論的地盤自体が弱い**ことを前提にする（過大な成熟度を
  主張しない）。
- ★ `.idea` の主張できる新規性は「①複数モダリティ（視覚+聴覚+物理）を②不確実性・時間変化する
  潜在状態込みで③統一的に扱う中間表現」の部分**のみ**であり、これが本ラウンドで唯一「ゼロ」と
  確認された空白。Enge et al. (2023) を**「最も近い競合」として直接引用**し、そこからの差分
  （物理媒体を含む・不確実性を扱う・時間変化する潜在状態を扱う）を明記して主張範囲を絞ること。
- ★ [P49]/[P113] と同じ温度（設計語彙・概念枠組みまで）で扱うべき文献が多く、「効果が実証されている
  理論」であるかのように書いてはならない（可視化系統の GoG/Vega-Lite/AVD だけは実装普及という
  異なる種類の裏付けを持つ）。

## 未取得・次ラウンドへの持ち越し

- [P49] (Bae et al. 2022) 本文: 依然未取得（arXiv abs ページ 403、PDF は WebFetch サイズ上限超過）。
  次回は `pypdf` でローカル保存済み PDF を読む手順（`reference_pdf_via_pypdf` メモ）を使うこと。
- Roddy & Bridges (2020) の逐語（Springer ペイウォールで本文未確認、要旨レベルの二次情報のみ）。
- haptic/tactile モダリティを含めた三感覚統合の探索は未実施（予算内で視覚+聴覚+物理化に絞ったため）。

---

## 追記: 追検証ラウンド（2026-09-06・coordinator 指示）

> 目的: (1) 既存写像代数が「許容条件 (admissibility constraints)」を既に持つか
> (GSE の「直交する」という位置づけの成否) (2) 「ゼロ」の主張（5条件連言）を条件を1つずつ
> 落として検算する。**既存探索結果の再利用を優先し、新規取得は最小限**（合計 10 件弱の
> 追加 WebSearch/WebFetch のみ）。

### 追検証1: 既存の写像理論は「合成規則」だけか、「許容条件」も持つか

#### (1-a) Kindlmann & Scheidegger (2014) AVD の原理 — ★ 核心

一次（論文本文の要約が WebSearch 経由で複数ソースから相互確認できた。PDF 自体は直接読解
不可＝バイナリ抽出失敗だったため、**この節は一次全文ではなく高再現性の二次引用**である点に注意）。

★★★ **原理は実在する。3 つ**:

1. **Representation Invariance（表現不変性）**: 逐語（二次引用）
   *"data, not spurious details of its representation, should determine the impression of the
   visualization"*。違反の失敗モードは **Hallucinator**（`H(v) = {h | r2 = h∘r1 and v∘h ≠ v}` と
   定式化される — 同じデータなのに表現の選択（座標変換等）だけで印象が変わってしまう現象）。
2. **Unambiguous Data Depiction（非曖昧性）**: 逐語（二次引用）
   *"all data features shall be distinctly visible in the visual design and map to individual
   visual features"*。違反の失敗モードは **Confuser**（異なるデータ特徴が視覚的に区別不能になる。
   例: テンソル可視化の bas-relief ambiguity で異なるテンソルが似た楕円体グリフになる）。
3. **Visual-Data Correspondence**: 逐語（二次引用）*"meaningful changes in data should produce
   analogously meaningful changes in impressions"*。上記 2 つの帰結として位置づけられる。

**(iii) 判定 — これは「知覚的・数学的忠実性」の条件か、「社会的・倫理的・注意資源上の許容性」まで
含むか**:

★★★ **前者のみ。後者は含まない。** 3 原理はいずれも「データの構造と、その視覚的印象の間の
写像が、対称性・区別可能性の点で忠実か」を問う**知覚的・数学的な graphical integrity 型の条件**
である（Tufte の Lie Factor と同じ問題設定＝データの外形をどれだけ正確に伝えるか）。
GSE が挙げる許容条件——**断定しない**（解釈の余地を残すか）／**状態依存で抽象度を切り替えない**
（一貫した表現ポリシー）／**未達を罰として描かない**（感情的フレーミング）／**2 秒で読める**
（注意資源コスト）／**色を主符号にしない**（チャネル選択の安全側設計）／**「変化なし」を空白で
表さない**（沈黙の意味論）——はいずれも「**推定対象（本人の内的状態）に対して、表現がどう
働きかけるか**」という**規範的・語用論的**な条件であり、AVD の 3 原理が問う「**データに対して
表現が忠実か**」という**記述的・意味論的**な条件とは**問いの種類が違う**。
→ ★★★ **AVD は GSE の許容条件を含まない。GSE の制約集合は AVD の再発明ではない**
（コア追検証の結論）。

#### (1-b) GoG / Vega-Lite / Van Nort / Grond&Berger / Munzner の規範的条件

- **GoG (Wilkinson)**: 探索した範囲で明示的な「してはならない」型の規範は確認できず
  （Aesthetics 要素は Bertin/Tufte 系の慣習に触れるが、規範を公理として持つ記述は見当たらない）。
  ⚠️ 未発見＝不在の確定ではなく本ラウンドの探索限界。
- **Vega-Lite (Satyanarayan et al. 2017)**: 技術仕様（合成代数）であり倫理的規範は無し（確認）。
- **Munzner (2009) Nested Model**: 「してはならない」型の規範は本ラウンドでは発見できず。
  ★ ただし性質が違う可能性がある候補として、著書 *Visualization Analysis and Design* の
  channel effectiveness ranking（どのチャネルが知覚的にどれだけ効果的か、という**ランキング**）
  があるが、これも「知覚的有効性」の話であり GSE 型の社会的許容性ではない。⚠️ 本文未確認。
- **Van Nort, Wanderley & Depalle (2014)**: 「一対一の直接的マッピングは表現力に乏しい／
  many-to-many の結合した写像が楽器的な身体性を生む」という**規範的だが美学的**な議論が
  NIME 分野に伏流している（Hunt&Wanderley 系譜、Rovan et al. の expressivity 論と地続き）。
  ⚠️ 本ラウンドでは Van Nort 2014 本文中の逐語は確認できず（二次的な分野知識としての言及に留まる）。
  これも「演奏者の表現力」を問う規範であり、GSE の「受け手（本人）への社会的・心理的作用」への
  規範とは対象が異なる。
- **Grond & Berger (Parameter Mapping Sonification, Sonification Handbook Ch.15)**:
  「外れ値の影響を抑えるため極値でなく分位点を写像の基準にすべき」という**頑健性・技術的な
  「べき」規範**を持つ（既出の要約より）。これも graphical-integrity 型（データに対する忠実性・
  頑健性）であり、GSE の社会的許容性とは別種。

→ **(1-b) の結論**: 探索した全ての写像理論（可視化・NIME・ソニフィケーション）が持つ規範は、
**「データに対する忠実性・頑健性・知覚的効果」の型**に留まり、**「受け手への社会的・心理的
作用（断定・処罰的フレーミング・注意資源・沈黙の意味論）」の型は 1 件も発見されなかった**。

#### (1-c) 反対側: 可視化・ソニフィケーションの倫理／規範文献（新規 angle）

- **Tufte — Graphical Integrity / Lie Factor**（*The Visual Display of Quantitative Information*,
  1983）: 6 原則の核心は逐語（要約引用）*"the representation of numbers, as physically measured
  on the surface of the graphic itself, should be directly proportional to the quantities
  represented"*。→ ★ これは AVD の Representation Invariance / Unambiguity の**前身**であり、
  同じく「データに対する忠実性」問題。GSE の許容条件とは別種であることを確認（AVD と同型の判定）。
- **Correll — "Ethical Dimensions of Visualization Research"** (CHI 2019, DOI
  10.1145/3290605.3300418): 可視化研究者・実務者の「科学者・エンジニアとしての義務を超えた
  道徳的責務」を提起する論文。本文全体の逐語照合は本ラウンドでは未達成（WebFetch がタイムアウト/
  403 で失敗）が、二次情報から確認できる射程は**欺瞞・プライバシー・恣意的な誤解を招く設計**の
  一般倫理であり、扱う主題は主として「**視聴者に対する外部データの誠実な提示**」（Cairo の
  *How Charts Lie* も同型: 切り捨てた軸・文脈を欠いたデータ・不確実性の隠蔽など）。
  ⚠️ **GSE の許容条件（本人の内的推定状態への言及の慎重さ）とは対象が違う**——Correll/Cairo は
  「**外部の・客観的に検証可能なデータ**を viewer に対して誠実に示すか」を問い、GSE は
  「**本人についての、モデルが推定した・不確実な内的状態**を、その**本人自身**にどう返すか」を
  問う。前者は data-to-viewer の誠実性、後者は inference-to-subject の節度——**問題の当事者
  構造そのものが異なる**（GSE には「第三者としての viewer」がおらず、推定対象＝受け手が同一人物）。
- **Barrass & Vickers — "Sonification Design and Aesthetics"** (Sonification Handbook Ch.7):
  「intrusiveness / distraction / listener fatigue / annoyance」という**注意資源・不快度**の
  懸念を扱う（本文完全な逐語照合は未達成、二次要約に留まる）。GSE の「2 秒で読める」「色を主符号に
  しない」に**質としては最も近い**（注意資源コストという軸を共有）。ただし「断定しない」「未達を
  罰として描かない」「変化なしを空白で表さない」という**解釈論的・意味論的**な条件は扱っていない
  （少なくとも二次情報の範囲では確認できず）。

→ **(1-c) の結論**: 可視化/ソニフィケーションの倫理文献は存在し、**「してはならない」型の規範を
持つ点では GSE と同じ構造を持つ**が、対象が (i) 外部データの誠実性（Tufte/Correll/Cairo）または
(ii) 聴覚的不快度（Barrass&Vickers）であり、**GSE の核心（本人の内的状態の推定を本人へ返す際の
節度）とは占有する場所が違う**。★ ただし Barrass&Vickers の「注意資源」軸は部分的に重なるため、
**GSE の許容条件を「完全に無主（unclaimed territory）」と書くのは過大**——「注意資源」の部分は
Barrass&Vickers を先行として引用すべきで、「断定しない／罰しない／沈黙の意味論」の部分のみが
真に無主。⚠️ また repo 既存の [P45] Gaver（曖昧さを設計資源とする）・[P75] Bodner&Prelec
（自己シグナリング・moral placebo effect）は、まさに「断定しない」「自己像への影響」という
GSE の核心条件そのものの先行に**repo 内に既に存在する**（本ラウンドで新規発見したものではないが、
1-c の文脈で再想起すべき）。→ ★★★ **GSE の許容条件の「内容」は無主ではない**（[P45][P75] が
部分的に先行）。無主なのは**「これを写像代数に対する直交レイヤーとして明示的に接続する」という
構造上の操作**の方である。

---

### 追検証2: 「ゼロ」の主張を割り引く（条件を1つずつ落とす）

| 落とす条件 | 残る問い | 先行はあるか | 温度 |
|---|---|---|---|
| 物理化を外す | 視覚+聴覚 ＋ 不確実性 ＋ 時間変化 | **部分的にあり、統合はされていない**。real-time sonification の設計原則（interpretability/linearity/continuity/resolution/orthogonality — ICAD "Monitoring Real-Time Data" 系譜）は時間変化に対応済み。"Sounding Uncertainty" 等、不確実性のソニフィケーション個別事例も散発的に存在。しかし Enge et al. (2023) の vis+audio 統一理論は不確実性ゼロ・時間は静的、のまま。→ **断片は存在するが統合した1本の理論は未発見** | PLAUSIBLE BUT UNPROVEN |
| 不確実性を外す | 視覚+聴覚+物理 ＋ 時間変化 | **各ペアは成熟、三元の統合は未発見**。dynamic/actuated data physicalization（shape-changing, 時間変化対応）は成熟した分野。real-time sonification も成熟。だが「視覚+聴覚+物理」を**三元同時に**統合する設計空間論文は本ラウンドで発見できず（SonART, Caiola et al. はいずれも二元＝vis+audio止まり） | 判定不能 |
| 時間変化を外す | 視覚+聴覚+物理 ＋ 不確実性（静的） | **未発見**。MacEachren/Thomson の不確実性 typology は視覚単独。物理化を含めた不確実性の統一枠組みは本ラウンドで確認できず | 判定不能 |
| 「潜在状態」を「観測量」に緩める | 視覚+聴覚+物理 ＋ 時間変化（観測量） | ★★★ **確定・大量に存在する**。Dubus&Bresin (2013, 物理量のソニフィケーション)・Jansen et al. (2015)・[P49] Bae et al. (2022)・[P76] Activity Sculptures・[P102] WhoIsZuki は**いずれも「観測された（測定済みの）量」を対象**にした設計空間/実装であり、本条件を緩めた途端に**この RQ で既に集めた候補の大半がそのまま「先行」になる**。→ ★★★ **この条件が本 RQ の空白を作っている最大の要因**の1つ | **確定**（埋まる） |
| モダリティを1つに絞る | 単一媒体 ＋ 不確実性 ＋ 時間変化（潜在状態のまま） | **一定量あり、ただし検証は本ラウンドでは浅い**。BCI/affective computing の「推定された精神状態のリアルタイム可視化」（例: EEG からの mental state space の可視化、biofeedback ダッシュボード）や Lan, Wu & Cao (2023, *Affective Visualization Design*, TVCG, 109 論文レビュー) が近傍に存在。ただし「不確実性を明示的に扱っているか」「断定しないという節度を持つか」は一次未確認 | PLAUSIBLE BUT UNPROVEN |

**★ どの条件が効いているか**: 表から、**「潜在状態→観測量」を落とす行だけが明確に「確定・大量に埋まる」**。
他の4行（物理化を外す／不確実性を外す／時間変化を外す／モダリティを1つに絞る）は
**「判定不能」または「断片はあるが統合未発見（PLAUSIBLE BUT UNPROVEN）」**に留まり、単独では
空白を埋めない。→ ★★★ **本 RQ の「ゼロ」の実体を作っているのは、突き詰めると
「(i) 3 モダリティ（視覚+聴覚+物理）を同時に統合する」ことと「(ii) 対象が観測量でなくモデル推定の
潜在状態である」ことの 2 条件であり、「不確実性」と「時間変化」は単独では空白の主因ではない**
（他分野で個別には十分に扱われているため）。

### ゼロ主張の温度の再判定

⚠️★★★ **前回ラウンドの結論3「視覚+聴覚+物理を横断し、かつ不確実性・時間変化する潜在状態を
統一的に扱う形式理論はゼロ」を文字通り「確定」と書くのは過大主張と判定する。**

理由:
1. 5 条件の連言は条件を増やすほど自動的に空になりやすい形をしており、実際に条件を1つ落とすと
   （「潜在状態→観測量」）**即座に大量の先行で埋まった**。これは coordinator の懸念（「日本語 IME
   打鍵データセットは存在しない」と同型の否決パターン）が**まさに的中した**ことを意味する。
2. 「三元モダリティの統合」自体は、二元（vis+audio: Enge et al. 2023, Caiola et al. 2022）までは
   到達しており、「モダリティを1つ足すと崩れる」壁に近い場所にいる——完全な空白というより
   **「二元までは統合の努力があるが、三元は未着手」という発展途上の空白**に近い。
3. 探索予算（17 件、6 angle）は「三元統合」「潜在状態＋不確実性＋時間変化の四重統合」という
   ニッチな交差点を**網羅的に**検証するには不足している。「見つからなかった」は
   「存在しない」ことの証明ではない。

→ **再判定: `判定不能`**（`確定` から格下げ）。ただし **「(i) 3 モダリティの同時統合」と
「(ii) 潜在推定状態（観測量でなく）」の 2 条件が空白の実体である**、という**より狭い主張**は
**PLAUSIBLE BUT UNPROVEN**として残せる（探索の一貫した傾向から支持されるが、悉皆的な反証を
経ていない）。

### GSE の「許容条件は直交する」という位置づけの生死判定

★★★ **部分的に生存。ただし2点の修正が必須。**

1. **「既存の写像代数（AVD/GoG/Vega-Lite/Van Nort/Grond&Berger）の内部に、GSE 型の許容条件は
   無い」は 1-a/1-b で確認され、生存する。** AVD は形式的な「許容条件」を持つが、その対象は
   graphical integrity（データへの忠実性）であり、GSE が問う「本人の内的推定状態への言及の節度」
   とは問いの種類が違う。→ **GSE の制約集合は AVD の再発明ではない**という核心の結論は保持できる。
2. **しかし「許容条件の内容が無主である」という含意は生存しない。** [P45] Gaver（曖昧さを資源とする）
   と [P75] Bodner&Prelec（自己シグナリング／moral placebo effect）が repo に既に登録されており、
   GSE の「断定しない」「本人の自己像への影響を配慮する」という条件の**内容**は、**写像代数の外側
   （デザイン理論・行動経済学）に既に先行がある**。またソニフィケーションの Barrass&Vickers が
   「注意資源」の軸で部分的に重なる。→ `.idea` は「許容条件を発明する」のではなく
   **「[P45]/[P75]/Barrass&Vickers 由来の許容条件を、既存の写像代数（GoG/AVD/Van Nort/
   Grond&Berger）に対する明示的な直交レイヤーとして初めて構造的に接続する」**という、
   **より狭いが依然として空白である**新規性として書き直す必要がある。
3. ★ **「直交レイヤーとして接続する」という構造上の操作自体の先行研究**（=「写像代数＋許容条件層」
   という二層アーキテクチャを明示的に論じた文献があるか）は、本追検証ラウンドでは探索していない。
   次ラウンドの持ち越し候補とする。

**総合結論**: GSE の位置づけ「両者は競合ではなく直交し、GSE の制約集合は既存代数の上に載る」は
**大枠として生存**するが、(a) 制約の**内容**は [P45]/[P75]/Barrass&Vickers を出典として引用し
「発明」ではなく「輸入」と書く、(b) 「ゼロ」の主張は `判定不能` に格下げし条件を絞る、
(c) 「二層アーキテクチャとしての接続」自体の新規性は未検証、の3点を `.idea` の次版に反映すること。
