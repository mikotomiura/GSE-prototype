# 設計の倹約性・公共の場・メディアアートとしての表現方法 (2026-08-15)

> `/literature-review` 1 ラウンド（★ 2 波構成）。★ 研究者の指示（原文・書き換えない）:
> 「**具体的な音自体の問題，　またはオブジェクトなどがカフェなどの公共な場所での場合での議論なども
> 行いたいですね．プライバシーだけではなく、ほかの人にとっての邪魔にならないかなどの議論やｓｕｒｖｅｙな、
> どメディアアートとしての表現方法など含めたものを次のセッションで行いたいね**」
>
> ★★★ さらにセッション中に **上位の問いが追加された**（原文）:
> 「**Bはイヤホン自体もよいが, 音自体の問いに戻ったりなど, 現状の形でもよいと思うのだが,まずこの
> メディア表現＋音などの形を現在は取っており、このコンセプトやベクトルの方向はよいのだが、
> さらにもう少しシンプルな解き方もあるのではないかと感じた(over fitting).
> この疑問自体の内容も調査サーヴェイなどで測ってほしい**」

## 動機（★ なぜこのラウンドか）

★ **2 つの動機がある。**

1. ★ 前ラウンド（2026-08-15・`20260815-portable-ambient-object-and-activity-coupling.md`）で形が
   **「PC の隣に置く可搬な物理オブジェクト（常在・周辺）」**に収束したが、
   ⚠️ **公共の場（カフェ）に持ち出す前提が出て、他者への影響という一度も扱っていない問いが立った。**
2. ★★★ **セッション中に研究者が over-fitting を指摘した。** ⚠️ これは A/B/C の**上流にある問い**であり、
   ★ 先に回すことで A/C の探索深度が変わりうる（★ 研究者判断で第 1 波に置いた）。

## 検証状態

| 項目 | 数 |
|---|---|
| 探索 angle | **8**（★ 第 1 波 3 ＋ 第 2 波 5・**反証 angle 2 つ内蔵**） |
| 取得ソース | 第 1 波: 約 12（★ うち **一次全文 2 本**: Zhang 2024 PDF 全文 / Squires 2014 PMC 全文） |
| 新規登録 | **[P108]–** / **[V81]–** |
| 敵対的検証 | ★ **3 レンズ**（内的妥当性 / 外的妥当性・外挿 / 効果量の頑健性） |

---

# 第 1 波 — RQ-0: 「メディア表現 ＋ 音」の形は over-fitting か

## gate 判定（要点先出し）

| 下位問い | 温度 | 1 行 |
|---|---|---|
| **RQ-0a 要素を足すほど効くか** | ⚠️★★★ **分野で符号が逆**（★ 平均化してはならない） | ★ 医療者行動変容では **関係なし**[P108]／★ 健康行動の推奨数では **正の線形**[P109]。⚠️ **ただし [P109] の 87% は 0–4 要素の範囲**であり、GSE の要素数は**外挿の外側** |
| ★★★ **RQ-0b どの要素が効いているか識別できるか** | ★★★ **確定（そして答えは「できていない」）** | ⚠️★★★ **[P110] 逐語: "The currently available component studies do not have the statistical power nor the quality to draw any meaningful conclusion about key ingredients"** ——★ **16 研究・22 比較・15 要素を積み上げても識別できていない** |
| **RQ-0c（反証）単純化は失敗するか** | ⚠️ **反証側の証拠が実在する** | ★ [P109]（**N=186,729**）は **要素を足すほど効く（線形）**と報告し、⚠️ **二次関数項は有意でない**（p=.12）。★ **研究者の直感に不利な証拠であり、隠さず記録する** |

> ★★★ **第 1 波の芯**: ⚠️ **文献は「シンプルにせよ」とは言っていない。**
> ★★★ **文献が言っているのは「その要素数では、どれが効いたか識別できない」である。**
> → ★ **over-fitting の正体は「効かない」ではなく「検証できない」。**

---

## カード 1: ★★★ 構成要素を積んでも、どれが効いているかは識別できていない —— 検出力と質が足りないため **[検証済 3-0]** [P110]

> ★★★ **本ラウンド第 1 波で最も重い 1 件。★ 研究者の over-fitting 懸念に、文献側から最も正確に答える。**

**1. どんなもの**: Cuijpers, Cristea, Karyotaki, Reijnders & Hollon (2019) *Psychotherapy Research* 29(1):15–29。
★ 成人うつ病の心理療法について、**component study（dismantling ＝ 1 要素を抜く／additive ＝ 1 要素を足す）**を
網羅的に探索し、**16 研究・22 比較**をメタ分析した。

**2. 先行研究と比べてどこがすごい**: ★ 米国 IOM が「**心理社会的介入の中核要素を特定することが実装の鍵**」と
述べたのを受け、⚠️ **「では実際に特定できているのか」を正面から数えた。**
★ 先行レビューは異質な研究集合になり多くを取りこぼしていた、と著者が述べている。

**3. 技術・手法の肝**: ★ **要素を「抜く」「足す」という 2 種類の設計を分けて集計**し、
★ **各研究の検出力を個別に評価した**（★ ここが本論文の効き所）。

**4. どうやって有効だと検証した**（★ 一次 abstract 逐語）:
- **"The pooled difference between the full treatments and treatments with one component removed was
  g = 0.21 (95% CI: 0.03∼0.39)."**
- ★★★ **"One study had sufficient statistical power to detect a small effect size and found that adding
  emotion regulation skills increased the effects of CBT. None of the other studies had enough power to
  detect an effect size smaller than g = 0.55."**
- ★ 15 要素が検討され、**うち複数比較で検討されたのは 4 要素のみ**。
- ⚠️ **"Only one study had low risk of bias."**
- ★★★ **結論（逐語）: "The currently available component studies do not have the statistical power nor
  the quality to draw any meaningful conclusion about key ingredients of psychotherapies for adult depression."**

**5. 議論はあるか**:
- ⚠️ 対象は**心理療法**であって表現層ではない。★ **しかし主張の中身は「検出力の算術」**であり、
  **領域に依存しない**（★ 3 レンズすべてがここで支持に回った理由）。
- ⚠️ `g = 0.21` の CI 下限は **0.03** で、**ほぼ 0 に接している**。
- ★ 逆に言えば **「要素は効かない」とも言っていない** —— ★ **「分からない」と言っている。**
  ⚠️ **これを「単純にすべき」と読むのは過剰読解である。**

> ★★★ **GSE への含意（★ ここが本ラウンド第 1 波の中核）**:
> ★ **RCT を何十年も積んだ分野が、16 研究・22 比較を集めてなお「どの要素が効くか分からない」と結論した。**
> ⚠️★★★ **GSE の表現層は現在 12 件以上の設計要素を持ち、n = 3–10 である。**
> → ★ **「どれが効いたか」を識別する設計は、現在の形では原理的に組めない。**
> ★★ **これは GSE が既に 3 回下している判断と同じ形である**（下記 §「GSE 内部の先例」）。

## カード 2: ★★ 多要素の介入が単一要素より優れるという証拠は無い —— しかも要素数と効果量に関係が無い **[検証済 2-1]** [P108]

**1. どんなもの**: Squires, Sullivan, Eccles, Worswick & Grimshaw (2014) *Implementation Science* 9:152。
★ **系統的レビューの overview（＝三次資料）**。**25 レビュー**を対象に、
「多面的（multifaceted）介入は単一要素の介入より医療者の行動を変えるか」を集計した。

**2. 先行研究と比べてどこがすごい**: ★ **「多要素の方が効く」という広く共有された前提を、正面から検定した。**

**4. どうやって有効だと検証した**（★ PMC 全文からの逐語）:
- ★★★ **"This overview of systematic reviews offers no compelling evidence that multifaceted
  interventions are more effective than single-component interventions."**
- ★ **"The findings of this overview do not support the commonly held assumption that multifaceted
  interventions are more effective than single-component interventions at changing health-care
  professionals' behaviours."**
- ★★★ **"there was no statistical evidence of a relationship between the number of intervention
  components used in the study group and the effect size"**（★ Grimshaw ら・French ら の 2 レビューで同文）
- ★ **25 レビュー中、効果量 / 用量反応の統計解析を提供したのは 3 レビューのみ。**
- ★★★ **数字の芯（Shojania ら）**: **"The median improvement for single vs. usual care (with no
  co-interventions) was 5.7%, and for multifaceted vs. single interventions, it was only 1.9%."**

**5. 議論はあるか**:
- ⚠️★★ **overview of systematic reviews ＝ 三次資料**である。★ 個々のレビューの質に依存する。
- ⚠️★★★ **対象は「医療者の行動変容」**であって、**本人の作業中の自己状態表現ではない。**
  ★ **ドメインは GSE から遠い。**
- ⚠️ **5.7% / 1.9% は median improvement であって標準化効果量ではない** ——
  ★ **[V40] の d や [P101] の F 値と直接比較できない。**
- ★ **ただし主張の形は「優位の証拠が無い」という否定形**なので、留保があっても成立する。

> ★★ **GSE への含意**: ★★★ **`5.7% → 1.9%` は「1 つ目の要素の勝ち幅 ≫ 2 つ目以降の勝ち幅」を
> 数字で言った唯一の一次記述である。**
> → ★ **表現層でも「最初の 1 要素」と「それ以降」は別の期待値で扱うべきである。**

## カード 3: ⚠️★★★ 反証 —— 要素（推奨）を足すほど効果は上がる。しかも二次関数項は有意でない **[検証済 2-1]** [P109]

> ⚠️★★★ **研究者の over-fitting 直感に対する、最大規模の反証。★ 隠さず先に置く。**

**1. どんなもの**: Zhang, Liu, White, Liu, Durantini, Chan, Dai, Zhou, Leung, Ye, O'Keefe, Palmese &
Albarracín (2024) *Psychological Bulletin*。★ **6,878 効果量 / 803 独立標本 / 364 報告 / N = 186,729**。
**8 領域**（食事・喫煙・運動・HIV 予防 / 検査 / 治療・飲酒・薬物）にわたり、
★ **「行動推奨の数」と行動的・臨床的変化の関係**を推定した。

**2. 先行研究と比べてどこがすごい**: ★ 先行の統合は **1〜3 領域**に限られていた。
★ 本研究は **8 領域横断で、線形か曲線かという形そのものを検定した。**

**3. 技術・手法の肝**: ★ **CHE+ モデル（correlated hierarchical effects）＋ 傾向スコア**。
★ **線形項と二次項の両方をモデルに入れ**、共線性を避けるため線形項を中心化してから二乗した。

**4. どうやって有効だと検証した**（★ 一次 PDF 全文からの逐語・実数）:
- ★★★ **"indicating that the linear form (B = 0.03, SE = 0.01, p < .001) but not the quadratic form
  (B = −2e−3, SE = 1e−3, p = .12) of the number of behavioral recommendations predicted effect sizes
  after controlling for the confounds."**
- ★ 傾向スコアを共変量に入れない版では **B = 0.04, SE = 0.007, p < .001**（★ 傾向スコアが上方バイアスを減衰）。
- ★ **感度分析 3 本**（差分の差 / WEIRD 標本 / 研究品質 3 指標）**すべてで線形が有意・二次は非有意**
  （差分の差: 線形 B = 0.03, p = .001 / 二次 B = −0.002, p = .12）。
- ★ 先行の推定: **各推奨あたり約 d = 0.07 の改善**（Dai 2020 / Sunderrajan 2021）。

**5. 議論はあるか**（★ 3 レンズのうち 2 つが重い留保を付けた）:
- ⚠️★★★ **外挿の範囲が決定的に狭い**（★ 一次 abstract 逐語）:
  **"although approximately 87% of the samples included between 0 and 4 behavioral recommendations."**
  ★ 本文の実測でも **"The average number of recommendations across all groups was 2.50, and the average
  number of recommendations among multiple-behavior interventions was 3.37."**
  → ★★★ **「線形である」は 0–4 の範囲で推定された線形であり、GSE の要素数へ外挿できない。**
- ⚠️★★★ **単位が違う。** ★ ここで数えられているのは **"exhortations to perform specific health behaviors"
  ＝ 本人に行動を求める推奨**である。⚠️ **GSE の層 0/1/2/3 は推奨ではなく表示要素であり、同じ物を数えていない。**
- ⚠️ **著者自身が同じ論文内に反対側の先行を書いている**（逐語）: Wilson ら (2015) は
  **"studies with two to three recommendations outperformed those with only one (d = 0.33 vs. d = 0.17),
  but that there was no difference between single- and multiple-behavior programs once there were
  four or more recommendations (d = 0.33 vs. d = 0.19)."**
  → ★★ **4 要素以上で頭打ちという報告が、この論文の中に併記されている。**
  ⚠️ **ただし Wilson 2015 は一次未取得（Zhang 経由の二次引用）であり、根拠に使ってはならない。**
- ⚠️ 効果は小さい（**推奨 1 つあたり B = 0.03**）。

> ★★★ **GSE への含意**: ★ **「足すほど効く」側の証拠は実在し、しかも本ラウンドで最大規模である。**
> ⚠️ **しかしそれは (a) 0–4 の範囲で、(b) 行動推奨という別の単位について推定されたものである。**
> → ★ **「だから GSE も足してよい」とは書けない。**★ **同時に「足すのは無駄だ」とも書けない。**

## カード 4: ★ 要素を識別するには factorial 設計が要る —— ただし n=3–10 には届かない **[検証済 3-0（方法論）]** [V81] [V82]

**1. どんなもの**: Collins, Dziak & Li (2009) *Psychological Methods* 14(3):202–224 と、
Collins ら (2014) *American Journal of Preventive Medicine*（factorial experiments）。
★ **MOST（Multiphase Optimization Strategy）**の統計的中核。

**3. 技術・手法の肝**: ★ **factorial 設計では各参加者が各要素を「受ける / 受けない」ので、
各主効果が標本全体で推定できる**（★ 条件ごとの人数ではなく総標本で検出力が決まる）。
→ ★ 4 要素を個別 RCT で測ると **N=1,792（1 実験 448 名）**必要な所を、factorial なら大幅に減らせる。

**5. 議論はあるか**:
- ⚠️★★★ **「条件あたり少人数でよい」は「総標本が少なくてよい」ではない。**
  ★ 検出力を決めるのは**総標本**であり、⚠️ **GSE の n = 3–10 はどの factorial 設計の閾値にも届かない。**
- ★ ★ **GSE は既にこの壁を自分で書いている** —— `media-expression-spec.md` §8:
  **「G1 が自ら『最も重要な弱点』と書いた検定の到達可能性（C(8,4)=70 の離散性で主判定が事実上
  AUC≈1.0 を要求）」**。

> ★★ **GSE への含意**: ★ **「要素を足すなら factorial で足す」が正しい方法論であり、
> ⚠️ それが n=3–10 で組めない以上、第 1 版の要素数は 1 に近い所へ落ちる。**
> ★ **これは倹約の美学ではなく、検出力の算術である。**

## カード 5: ⚠️ アンビエントディスプレイ領域で「要素数 × 効果」を測った研究は見つからなかった **[判定不能]**

**1. どんなもの**: ★ RQ-0 を GSE 固有の領域（ambient / peripheral display）で問い直した。
「表示要素を増やすと効果が上がるか / glanceability が落ちるか」を測った研究を探した。

**2. 結果**: ⚠️ **該当ゼロ。** ★ 見つかったのは **設計指針・ヒューリスティック評価・glanceability の定義**
（Mankoff ら 2003 / Matthews ら の peripheral display 評価）であり、
⚠️ **要素数を独立変数にして効果を測った実証は無い。**

**5. 議論はあるか**: ⚠️★★★ **空白は有望を意味しない**（★ 本トラックで 3 度目の同じ警告）。
★ **しかも [P90]（無視されるよう設計されたものを深く評価することは原理的に難しい）が、
この空白の理由を既に説明している可能性がある。**

---

## ★★★ GSE 内部の先例 —— 研究者の over-fitting 指摘は、既に 3 回下されている判断と同型である

> ★ **一次で確認した**（★ 記憶や引き継ぎを根拠にしない）。

| # | 出所（一次） | 逐語 / 要旨 |
|---|---|---|
| 1 | `docs/design-history.md:24` | HSMM を却下 —— **"requires massive data to estimate duration parameters (overfitting in n=1 environments)"** |
| 2 | `docs/architecture/personalization-and-online-learning.md:671` | ★ **「軽量性は制約ではなく帰結である」「軽さは目的ではなく、データ量が許す複雑さの上限がたまたま軽いところにある、というだけである」** |
| 3 | `.steering/20260801-architecture-consolidation/decisions.md:52-61` | ★ 状態数を**決めない**と決定。理由 1 逐語: **「情報を持たない観測の上に状態構造を載せても事後分布は情報を持たない」**／理由 3: Codex #7 **「D 以外のベースラインを先に置き、D の複雑さに対する勝ち幅を測れ」** |

⚠️★★★ **そして表現層には、この原理が一度も適用されていない。**

```text
★ 実測されたつまみ = [P85] の運動符号 …… 1 つだけ
   （★ しかも本人側でしか測られておらず、物理オブジェクトへの転移は演繹）
      ↓
★ 現在の形 = 層 0 / 1 / 2 / 3（4 層）
            ＋ 物理オブジェクト（可搬・常在・周辺）
            ＋ 歩行連動（二値・スマホ計測）
            ＋ 具体案 A-1〜A-12
      ↓
n = 3–10
      ↓
⚠️★★★ [P110]: RCT を積んだ分野でも 16 研究 22 比較で識別できていない
      ↓
★★★ 「どれが効いたか」は、この形では原理的に出せない
```

★ **既決 7（第 1 版は視覚 1 モダリティ・理由は「交絡と検出力 n=3–10」）は、既にこの方向を向いていた。**
⚠️ **その後の議論が、その制約の外側で膨らんだ。**

## ⚠️ 第 1 波の否決リスト

| # | 否決した主張 | 票 | 否決理由 |
|---|---|---|---|
| **T-1** | ★ **「文献は『シンプルにせよ』と言っている」** | **0-3** | ⚠️ [P110] は **「分からない」**と言っており「効かない」とは言っていない。★ [P108] は**否定形の主張**（優位の証拠が無い）であって単純化の推奨ではない。★ [P109] は**逆向き**である。→ ★ **「単純にせよ」は文献から導けない** |
| **T-2** | ⚠️ **「[P109] があるので要素を足してよい」** | **0-3** | ⚠️ **87% が 0–4 要素の範囲**で推定された線形であり、GSE の要素数は外挿の外側。⚠️ しかも数えているのは **"exhortations to perform specific health behaviors"** ＝ 行動推奨であって表示要素ではない（**単位が違う**） |
| **T-3** | ⚠️ **「4 要素で頭打ちになる（Wilson 2015）」を根拠に使う** | **1-2** | ⚠️ **一次未取得**（★ [P109] 経由の二次引用）。★ 記録はするが**根拠に使ってはならない** |

## ⚠️ 第 1 波のやり残し

1. ★★ **[P111] Bell, Marcus & Goodlad (2013) *JCCP* 81(4):722–36 の abstract / 全文** ——
   ★ **additive study では効果が有意**（★ しかも追跡で大きくなる）と報告する側で、
   ⚠️ **[P110] と符号が違う可能性がある。** ★ APA 側が abstract を閉じており未取得。
2. ★★ **Wilson ら (2015) の一次** —— ★ **「4 要素以上で頭打ち」の唯一の出典**で、
   ⚠️ 現在 [P109] 経由の二次引用のまま。
3. ★ **Shojania ら の元レビュー** —— ★ `5.7% vs 1.9%` の元数字（★ [P108] 経由）。

---

# 第 2 波 — A: 公共の場 / B: 音の具体問題 / C: メディアアートとしての表現方法

## gate 判定（要点先出し）

| 下位問い | 温度 | 1 行 |
|---|---|---|
| **RQ-1 他者にとって負担になるか** | ⚠️ **部分的にしか埋まらなかった** | ★ 社会的受容性は**独立した研究系として実在する**（★ 使用者視点と観察者視点を明示的に分ける）[P116]。⚠️ **一次全文が取れず（403）二次水準**。★ 反証側には **display blindness**[P115] があるが ⚠️ **機序が「広告だと期待するから」**であり**机上の私物には移らない** |
| ★★★ **RQ-2 運動符号は他者側でも同じつまみか** | ★★★ **確定（★ そして引き継ぎの前提が条件付きになった）** | ⚠️★★★ **運動オンセットの不随意捕捉は「観察者が何を探しているか」で消える** —— ★ 一意形状探索では捕捉（**1,057 vs 998 ms, t(23)=4.57, p<.001, d=0.41**）、★ **事前指定形状の探索では消える（560 vs 557 ms, t(23)=.79, p=.436, d=.026）**[P114] |
| **RQ-3 カフェの規範** | ⚠️ **未探索のまま**（★ 予算を RQ-2 / RQ-5 に寄せた・**やり残しに明記**） | — |
| **RQ-4 音（イヤホン・モダリティ）** | ★ **確定（★ そして前ラウンドの記述に訂正が要る）** | ★★★ **[P93] の一次全文を取得**（★ 前ラウンド最優先のやり残し）。**誤り率ではモダリティ差なし**だが、⚠️★★★ **活動率では差があり、視覚と音は速度を上げ、触覚と嗅覚は遅くした（F(4,101)=8.76, p<0.0001）** |
| ★★★ **RQ-5 「作品になる」と言えるか（C の gate）** | ★★★ **語彙は確定 / 効果は判定不能 → `de-risk 先行`** | ★★★ **[P112] 逐語: "In ambient information visualization ... aesthetics is considered a primary property, both in the design and during use."** ——★ **ambient では作品性は副産物ではなく一次的性質**。⚠️ **しかし効果の出典は 1 本も無い**（[P103]/[P104]/[P106] すべて設計論・質的） |
| **RQ-6（反証）美的体裁は効果を下げたか** | ⚠️ **下げなかった、という報告が出た** | ★ [P112] **Lesson 3 逐語: "Basing a visualization on an artistic style need not hinder – and might even support – the readability and comprehension"**。⚠️ **ただし N=6 の質的観察** |

---

## カード 6: ★★★ 通知の破壊性はモダリティによらない —— ⚠️ ただし「誤り率」についてだけである **[検証済 2-1]** [P93]（★ 一次全文取得・**前ラウンドの記述を訂正**）

> ★★★ **前ラウンド（2026-08-14）の最優先やり残し #1 を閉じた。**
> ⚠️★★★ **そして閉じた結果、前ラウンドの記述が半分だけ正しかったことが判明した。**

**1. どんなもの**: Warnock, McGee-Lennon & Brewster (2011) *INTERACT 2011*, LNCS 6947, pp.572–588。
★ **視覚・聴覚・触覚・嗅覚**の通知を**同一被験者内**で比較し、
**主タスクの破壊性**と**通知の有効性**を分けて測った。**N=27**（男 14 / 女 13）。

**3. 技術・手法の肝**: ★ **破壊性を 2 つの指標に割った** —— **誤り率（superfluous views per turn）**と
**活動率（turns per second）**。★ **通知なしの control 条件を置いた。**

**4. どうやって有効だと検証した**（★ 一次 PDF 全文・逐語）:
- **H1（誤り率）**: **F(4, 101) = 16.57, p < 0.0001**。★ しかし post hoc Tukey の逐語:
  > **"the significant differences were between the control and the experimental conditions; there were
  > no significant differences in error rate between any of the conditions with notifications. The data
  > did not support the hypothesis, suggesting that there is no connection between task disruption and
  > the modality of the notification."**
- ⚠️★★★ **H2（活動率）—— ここが前ラウンドで見落とされていた**: **F(4, 101) = 8.76, p < 0.0001**。逐語:
  > **"Post hoc Tukey tests identified two groups: one containing the visual and audio conditions and
  > the other containing tactile and olfactory. These two groups were significantly different from each
  > other. Olfactory and tactile notifications introduced a temporal disruption, slowing the players,
  > while visual and audio conditions appeared to prompt the player to speed up resulting in a higher
  > rate of activity."**
- **H3（正答率）**: 視覚 **96%** / 音 **90%** / 触覚 **76%** / 嗅覚 **70%**（χ²(3)=41.2, p<0.0001）。
- 考察の逐語: **"there were no significant differences between the modalities, implying that the
  notifications were all equally disruptive."**

**5. 議論はあるか**:
- ⚠️★★★ **これは「通知」の実験である。** ★ GSE の表現層は**常在で通知ではない**。
  ★ しかも control vs 実験条件では**有意に壊れている** —— **「通知を入れること自体」は壊す。**
- ⚠️★★ **「差が検出されなかった」は「等価である」ではない。** ★ 等価性検定も Bayes factor も無い
  （★ [P79] のカード 2 と**同じ問題**）。
- ⚠️ 主タスクは**ゲーム様の課題**であり、論述執筆ではない。
- ★ 著者自身が**馴化・親しみによる説明**を挙げ、**測っていない**と明記している。

> ★★★ **GSE への含意（★ 訂正を含む）**:
> ★ **`_index.md` 2026-08-14 行の「主タスクの中断量はモダリティによらず同じ」は、誤り率については正しい。**
> ⚠️★★★ **しかし活動率ではモダリティ差があり、しかも視覚と音は同じ群に入った。**
> → ★ **「音だけが特別に破壊的」という主張は、この一次でも支持されない**（★ 前ラウンドの結論は維持）。
> ⚠️ **同時に「音は無害」でもない** —— ★ **視覚と音はどちらも作業速度を上げる方向に押した。**

## カード 7: ⚠️★★★ 運動符号の不随意捕捉は、観察者が「何を探しているか」で消える **[検証済 2-1]** [P114]

> ★★★ **引き継ぎ §3 が A の新しさの根拠として置いた前提**——
> 「**周辺視で無視しにくい性質は隣の席の人にも等しく働く**」——**を直接検定した唯一の系。**

**1. どんなもの**: Nair, J., Ma, X. & Abrams, R. A. (2026)
*Attention, Perception & Psychophysics* 88(2):65。★ **運動オンセット（motion onset）の妨害刺激**が
注意を捕捉するかを、**探索課題の種類を変えて** 3 実験（**各 N=24・被験者内**）で測った。

**3. 技術・手法の肝**: ★★★ **同じ運動刺激に対し、観察者側の探索モードだけを変えた。**

**4. どうやって有効だと検証した**（★ 一次逐語・実数）:

| 条件 | 逐語 |
|---|---|
| ★ **実験 1（一意形状の探索）** | **"the mean reaction time when a motion-onset distractor was present (1,057 ms) was significantly longer than when the distractor was absent (998 ms), t(23) = 4.57, p < .001, d = 0.41"** |
| ★★★ **実験 2・3（事前指定形状を異種形状の中から探す）** | **"the mean reaction time on distractor-present trials with a motion-onset distractor (560 ms) was not significantly different from the mean reaction time on distractor-absent trials (557 ms), t(23) = .79, p = .436, d = .026"** |

**5. 議論はあるか**:
- ⚠️★★★ **課題は視覚探索であって、執筆でも「隣席で作業する」でもない。** ★ 外挿である。
- ⚠️★★ **帰無側（実験 2・3）に等価性検定が無い。** ★ `d = .026` は小さいが**「捕捉が無い」の証明ではない。**
- ★ 著者自身が**馴化の寄与を測っていない**と明記（逐語: **"the extent to which habituation contributed
  to the attenuation is unknown"**）。

> ★★★ **GSE への含意（★ 引き継ぎ §3 の前提を条件付きにする）**:
> ⚠️ **「運動は誰の周辺視でも等しく捕捉する」は、そのままでは成り立たない。**
> ★ **捕捉されるかは、観察者が置いている探索モードに依存する**（★ `d = 0.41` ⇄ `d = 0.026`）。
> ⚠️★★★ **しかしカフェの隣席の人がどちらのモードかは、この論文からは決められない。**
> → ★ **A の問いは消えていない。★ 「自明に危険」から「条件が特定された未検証」へ移った。**

## カード 8: ★★★ 美的様式は可読性を妨げなかった —— ⚠️ しかし実配備で読めたのは 6 人中 3 人、使ったのは 2 人 **[効果は 1-2 否決 → 設計語彙として 3-0 保持]** [P112]

> ★★★ **C（メディアアートとしての表現方法）に対する、本ラウンド唯一の一次実地証拠。**

**1. どんなもの**: Skog, T., Ljungblad, S. & Holmquist, L. E. (2003)
*Between Aesthetics and Utility: Designing Ambient Information Visualizations*, **IEEE InfoVis 2003**。
★ **モンドリアン様式のバス発車時刻の可視化**を大学の公共空間に実配備し（★ 潜在利用者 約 300 名）、
★ **強制されない自然な利用**の下でインタビュー調査を行った。

**2. 先行研究と比べてどこがすごい**: ★★★ **「informative art は作品として成立するのか / 読めるのか」を、
実配備で正面から測った数少ない例。** ★ しかも著者らは**当該学科の所属ではなく**、
**利用に影響を与えない位置**にいることを明記している。

**3. 技術・手法の肝（★ GSE がそのまま使える語彙）** —— ★ **3 段の理解尺度**（★ 各段は次段の前提）:

| 段 | 逐語 |
|---|---|
| **THAT** | **"That something is visualized – does the subject know that the display is an information visualization and not simply decoration?"** |
| **WHAT** | **"What is visualized – can the subject tell us what data the visualization reflects?"** |
| **HOW** | **"How the data is visualized – can the subject read and interpret the visualization correctly?"** |

★ 逐語: **"Only when reaching the third step does a person have enough understanding to actually use an
ambient information visualization."**

**4. どうやって有効だと検証した**（★ 一次逐語・実数）:
- ★ 説明は**十分に用意された** —— 画面横の説明板・**約 30 部の配布資料**・大学ホームページの記事。
- ★ **6 名にインタビュー**（★ 常時その area にいる人に限定）。
- ⚠️★★★ **"Out of the six persons who were interviewed, one person did not know that some data was
  visualized on the display."**（★ **装飾だと思っていた**）
- **"Two people knew what was visualized, but did not know how to read it."**
- **"Out of the five, three people knew how to read the visualization."**
- ★ **使用**: **"Two of the three persons that knew how read the visualization, had also used it to catch
  the bus. One of them had used it three times and the other once."**

> ★★★ **つまり: 6 人中 → 5 人が「何か」を知り → 3 人が読めて → 2 人が実際に使い、
> うち 1 人は 3 回・もう 1 人は 1 回である。**

**5. 議論はあるか**:
- ⚠️★★★ **N=6 のインタビュー・統制なし・質的**。★ **効果の主張には使えない（1-2 否決）。**
- ⚠️ **効果量が無い。** 2003 年・大型プラズマ画面・公共空間。
- ★ **それでも重い理由**: ★ **強制されない実配備で、説明を十分に置いてなお、この歩留まりだった。**
  ⚠️ **[P90]（無視されるよう設計されたものは深く評価しにくい）の中で、これは数少ない実地の数字である。**

> ★★★ **GSE への含意（★ 2 つあり、片方は問い A に接続する）**:
> ★ **(1) C の gate へ**: ★ **作品として成立させることと、読まれることは別である。**
> ★ **THAT / WHAT / HOW は、GSE がどの段で止めるかを選べる尺度である。**
> ★★★ **(2) 問い A へ（★ 本ラウンドで最も設計に効く発見）**:
> ⚠️ **「1 人はデータが表示されていることすら知らず、装飾だと思った」——
> ★ これは本人にとっては欠陥だが、他者にとっては利点そのものである。**
> → ★★★ **A-7（他人に意味が読めない符号にする）に、初めて一次の裏付けが付いた。**
> ★ **同じ性質が、本人には失敗として、他者には保護として働く。**

## カード 9: ★ 反証 angle の結果 —— 美的様式は可読性を下げなかった（むしろ支えうる） **[検証済 2-1]** [P112]

**1. どんなもの**: ★ RQ-6（**美的体裁は効果を上げなかった / aesthetics より情報量が効いた側**）を探した。

**2. 結果**: ⚠️ **予想と逆の報告が出た。** ★ [P112] の **Lesson 3（逐語）**:
> **"Basing a visualization on an artistic style need not hinder – and might even support – the
> readability and comprehension of an ambient infovis installation."**

★ 併せて **Lesson 4（逐語）**:
> **"Letting features of the information source affect the visual encoding, thus providing a mnemonic to
> remember the mapping, is a good way to support the comprehension of the display."**
★ 根拠は実測ベース —— **恣意的な空間対応（メール・地域天気）は覚えにくく、地理的メタファ（世界天気・
川をランドマークにしたバス停）は覚えやすかった。**

★ さらに **結論節の逐語（★ C の gate に直撃）**:
> **"In information visualization, aesthetics can almost be considered an added bonus, or at least a
> bi-product when striving for readability and effectiveness. In ambient information visualization, on
> the other hand, aesthetics is considered a primary property, both in the design and during use.
> When designing ambient infovis, it may even be necessary to go against established infovis guidelines
> in order to adhere to an artistic template."**

★ **そして「壊れている」の出し方**（逐語）:
> **"In our bus example we let black squares indicate that the server was down ... this consisted a
> noticeable break with the artistic template, something that should make it easier for users to
> conclude that something is wrong with the application."**

**5. 議論はあるか**: ⚠️★★ **同じ N=6 の質的観察に基づく "lessons learned" である。**
⚠️ **統制された aesthetics × readability の比較ではない。** ★ **著者の設計上の総括である。**

> ★★ **GSE への含意**: ★ **「美しくすると読めなくなる」という懸念は、この一次では支持されなかった。**
> ⚠️ **ただし [P48]（free-form が時間と usability で劣位）は生きている** ——
> ★ **[P112] のモンドリアンは free-form ではなく、強い構造を持つ様式である**（★ 矛盾しない）。
> ★★★ **`graceful degradation を様式の破れとして出す` は、GSE がそのまま使える技法である。**

## カード 10: ⚠️ 反証 angle（他者側）—— 「誰も見ない」側の証拠は実在するが、機序が移らない **[1-2 → 根拠に使わない]** [P115]

**1. どんなもの**: ★ **display blindness**（Müller ら, *Pervasive 2009*）。
**11 か所の公共ディスプレイで 91 名にインタビュー**し、passers-by が公共ディスプレイに
**ほとんど注意を払わない**ことを報告した。

**2. 結果**: ★ 機序は **「退屈な広告だと期待するから見ない」**。
★ **有用な情報を出すディスプレイ（学生向け iDisplay）は、店のクーポンより見られた。**

**5. 議論はあるか**:
- ⚠️★★★ **一次全文を取得できていない**（★ Springer が認証を要求・**二次水準**）。
- ⚠️★★★ **機序が GSE に移らない。** ★ display blindness は**「広告」というカテゴリ判断**に依存する。
  ⚠️ **カフェのテーブルに置かれた私物はそのカテゴリに入らない**
  —— ★ 実際 **[P98] では、同僚も車内の見知らぬ人も「見て・尋ねた」。**

> ★★ **GSE への含意**: ★ **「他者は見ない」を根拠にしてはならない。**
> ★ **[P98] の一次証拠（他者が実際に尋ねた）の方が、GSE の形に近い。**

## カード 11: ⚠️ イヤホン常時装着は「音の場所問題」を解くが、別のコストを持ち込む **[判定不能に近い・二次水準]**

**1. どんなもの**: ★ RQ-4 の B 側 —— **公共の場でスピーカーが消えたあとに残る唯一の経路**を調べた。

**2. 結果**:
- ★ **既存 [P73] が既に決着の一部を持っている**: **ANC は系列再生に null・改善するのは知覚プライバシーのみ。**
- ⚠️ **職場での対人知覚のコスト**（「常時装着者は近づきにくい・親しみにくいと見られる」）は
  **複数の二次記述で一貫している**が、⚠️ **一次を取得できなかった。**
- ⚠️ **装着そのものの負担**（occlusion effect・圧迫・熱）は工学文献と実務記事に散在し、
  ⚠️ **作業パフォーマンスとの co-measure は見つからなかった。**

**5. 議論はあるか**: ⚠️★★★ **本項は二次水準であり、断定に使ってはならない。**
★ **やり残しとして次ラウンドへ渡す。**

---

## ⚠️ 第 2 波の否決リスト

| # | 否決した主張 | 票 | 否決理由 |
|---|---|---|---|
| **T-4** | ⚠️ **「[P93] はモダリティが等価であることを示した」** | **0-3** | ★ **等価性検定も Bayes factor も無い**（★ [P79]/R-2 と同型）。⚠️ しかも**活動率ではモダリティ差が有意**（F(4,101)=8.76）。→ ★ **書いてよいのは「誤り率でモダリティ差は検出されなかった」まで** |
| **T-5** | ⚠️ **「他者は気にしない（display blindness）」** | **1-2** | ⚠️ **一次未取得**、かつ**機序が「広告だと期待するから」**で**机上の私物に移らない**。★ [P98] の一次が反対方向 |
| **T-6** | ⚠️ **「informative art は作品として成立し、しかも効く」** | **0-3** | ★ **成立する**側は [P112] 逐語で言える。⚠️ **効くという出典が 1 本も無い** —— [P103] は評価を将来に置き、[P104] は設計論、**[P106] は Research through Design の質的研究で行動変化を測っていない**（★ 本ラウンドで abstract 逐語確認） |
| **T-7** | ⚠️ **「美的様式にすると読めなくなる」** | **1-2** | ★ [P112] Lesson 3 が**逆を報告**。⚠️ ただし **N=6 の質的観察**なので**否定側も断定できない** |

## ⚠️ 第 2 波のやり残し

1. ⚠️★★★ **RQ-3（カフェ / third place の規範）は探索できなかった** —— ★ 予算を RQ-2 と RQ-5 に寄せた。
   ★ **次ラウンドの入口はここ。**
2. ★★ **[P116] Koelle ら CHI 2020「Social Acceptability in HCI」の一次全文**（★ 403）——
   ★ **観察者視点を扱った研究が何 % かという数字**が、問い A の空白の大きさを決める。
3. ★★ **[P115] Müller ら 2009 の一次全文**（★ Springer 認証）。
4. ★★ **イヤホン常時装着の対人知覚コストの一次**（★ 二次記述は一貫しているが出典に届いていない）。
5. ★ **[P113] Redström, Skog & Hallnäs (2000) の一次**（★ informative art の定義の大元）。
6. ⚠️ **[P106] の全文**（★ abstract は逐語確認済み。★ 参加者数・期間は未確認だが、
   **効果の出典でないことは abstract で確定した**）。

---

# ★★★ 3 つの問いへの答え（★ 全波を通した統合）

## ⚠️★★★ RQ-0（over-fitting）が A・B・C の答えを書き換えた

```text
第 1 波: 文献は「シンプルにせよ」とは言わない（T-1 を 0-3 で否決）
       言うのは「その要素数では、どれが効いたか識別できない」[P110]
      ↓
★ したがって問いは「減らすか」ではなく「最初の 1 要素を何にするか」になる
      ↓
★ A / B / C の結果は、その 1 要素を選ぶための材料として読む
```

| 問い | ★ 答え | 温度 |
|---|---|---|
| **A** | ⚠️ **「他者にも等しく効く」は条件付きになった**（[P114]: 捕捉は観察者の探索モード依存 `d=0.41 ⇄ d=0.026`）。★★★ **そして設計解に一次の裏付けが付いた** —— [P112] で **6 人中 1 人は「装飾だと思った」**＝ **A-7（他人に読めない符号）は実在する現象である** | ★ **RQ-2 確定 / RQ-1 二次水準 / RQ-3 未探索** |
| **B** | ★ **音を「最初の 1 要素」にする根拠は無い。** [P93] 一次で**モダリティ間の破壊性差は検出されず**（＝音が優れる証拠も無い）、⚠️ **活動率では視覚と音がともに速度を上げた**。★ 実測されたつまみを持つのは**視覚（運動符号）だけ**[P85] | ★ **確定（3 ラウンド連続で同じ向き）** |
| **C** | ★★★ **「α は作品になるのか」（S3-D11）への答え: 分野の側では既に「なる」と言える** —— [P112] 逐語 **"aesthetics is considered a primary property, both in the design and during use"**。⚠️ **しかし「作品性が効果を生む」は出典ゼロ** → **gate = `de-risk 先行`** | ★ **語彙は確定 / 効果は判定不能** |

## ★ C の gate 判定（★ 用途が gate なので明言する）

> ★★★ **判定 = `de-risk 先行`。**
> ★ **go と書ける部分**: 「表現層を作品として設計してよい」——★ ambient 領域では**美的性質は一次的**であり、
> ⚠️ **infovis の標準指針に反してでも様式を守ってよい**と一次が明記している [P112]。
> ⚠️ **no-go と書くべき部分**: 「作品性が効果を生む」——★ **[P103]/[P104]/[P106] は 1 本も効果の出典ではない。**
> ★ **de-risk の中身**: ★ **THAT / WHAT / HOW のどの段で止めるかを、先に決めて凍結する**（[P112]）。

## ★★★ 表現方法（技法）として実際に拾えたもの

| # | 技法 | 出所（★ 一次逐語） |
|---|---|---|
| **1** | ★★★ **THAT / WHAT / HOW の 3 段で「どこまで読ませるか」を設計変数にする** | [P112] |
| **2** | ★ **空間配置を記憶術にする** —— 恣意的な対応は覚えられず、**実在のランドマークを基準にした対応**が最良だった | [P112] Lesson 4 |
| **3** | ★★★ **`壊れている` は様式の破れとして出す**（★ 黒い四角＝サーバ停止）——★ **graceful degradation を美的テンプレートの中に設計する** | [P112] 逐語 |
| **4** | ★ **aesthetic ambiguity / slow revelation** | [P106]（★ abstract 逐語・**効果の出典ではない**） |
| **5** | ★ **「単に知らせる」から「データとともに / を通して生きる」へ** | [P106] 逐語 |

