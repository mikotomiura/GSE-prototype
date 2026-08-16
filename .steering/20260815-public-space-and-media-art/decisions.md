# 設計判断の記録 — 公共の場・音・メディアアート、そして over-fitting（PS）

> 2026-08-15 / ★ **本セッションは議論とサーヴェイのみ。実装に入っていない。**
> ⚠️★★★ **決定は 1 つも下していない。** 以下の PS-D1〜 は**一次資料で確かめた事実**であり、
> PS-Q1〜 は**研究者に返した判断**である。
> 文献: `docs/literature/20260815-design-parsimony-public-space-and-media-art.md`（[P108]–[P116] / [V81]–[V82]）
> 入口: `.steering/_handoff/next-session-prompt-public-space-and-media-art.md`

---

## ★ 研究者の指示（原文・書き換えない）

**① セッション開始時（引き継ぎ §0 に記録済み）**
> 「具体的な音自体の問題，　またはオブジェクトなどがカフェなどの公共な場所での場合での議論なども
> 行いたいですね．プライバシーだけではなく、ほかの人にとっての邪魔にならないかなどの議論やｓｕｒｖｅｙな、
> どメディアアートとしての表現方法など含めたものを次のセッションで行いたいね」

**② ★★★ セッション中に追加された上位の問い**
> 「Bはイヤホン自体もよいが, 音自体の問いに戻ったりなど, 現状の形でもよいと思うのだが,まずこの
> メディア表現＋音などの形を現在は取っており、このコンセプトやベクトルの方向はよいのだが、
> さらにもう少しシンプルな解き方もあるのではないかと感じた(over fitting).
> この疑問自体の内容も調査サーヴェイなどで測ってほしい」

★ **研究者が本セッションで下した手続き上の決定**（★ Step 0 / Step 1 の合意）:

| # | 決定 |
|---|---|
| 1 | ★ 範囲 = **A + C 主・B は 1 angle 追加**（★ B は「音自体の問い」に戻る余地も残す） |
| 2 | ★ 用途 = **A は設計根拠の補強 / C は gate / B は設計判断の材料** |
| 3 | ★ 予算 = **angle 6 → RQ-0 追加により 8**・ソース 25–30 |
| 4 | ★★★ 順序 = **RQ-0（over-fitting）を第 1 波として先に回し、結果を返してから第 2 波** |
| 5 | ★ 第 1 波の結果を見たうえで **第 2 波は予定どおり 5 angle** |

---

## ★ 一次資料で確かめた事実（★ これは決定ではない）

### PS-D1: ★★★ over-fitting の正体は「効かない」ではなく「検証できない」

⚠️★★★ **私は「文献はシンプル側を支持するだろう」と予想していた。外れた。**
★ **「文献はシンプルにせよと言っている」は 0-3 で否決した**（否決 T-1）。

| 出所 | 逐語 |
|---|---|
| ★★★ [P110] Cuijpers ら 2019（16 研究・22 比較・15 要素） | **"None of the other studies had enough power to detect an effect size smaller than g = 0.55."** ／ **"The currently available component studies do not have the statistical power nor the quality to draw any meaningful conclusion about key ingredients of psychotherapies for adult depression."** ／ **"Only one study had low risk of bias."** |
| ★★ [P108] Squires ら 2014（25 レビューの overview） | **"no compelling evidence that multifaceted interventions are more effective than single-component interventions"** ／ **"no statistical evidence of a relationship between the number of intervention components used in the study group and the effect size"** ／ ★★★ **"The median improvement for single vs. usual care ... was 5.7%, and for multifaceted vs. single interventions, it was only 1.9%."** |
| ⚠️★★★ [P109] Zhang ら 2024（**6,878 効果量・N=186,729**・**反証側**） | **"the linear form (B = 0.03, SE = 0.01, p < .001) but not the quadratic form (B = −2e−3, SE = 1e−3, p = .12) ... predicted effect sizes"** —— ⚠️ **ただし "approximately 87% of the samples included between 0 and 4 behavioral recommendations"** かつ数えているのは **"exhortations to perform specific health behaviors"（行動推奨であって表示要素ではない）** |

> ★★★ **帰結: 問いは「要素を減らすか」ではなく「最初の 1 要素を何にするか」である。**

### PS-D2: ★★★ GSE は同じ原理を既に 3 回適用しており、表現層にだけ適用していない

| # | 出所（一次） | 逐語 / 要旨 |
|---|---|---|
| 1 | `docs/design-history.md:24` | HSMM 却下 —— **"requires massive data to estimate duration parameters (overfitting in n=1 environments)"** |
| 2 | `docs/architecture/personalization-and-online-learning.md:671` | ★ **「軽量性は制約ではなく帰結である」「軽さは目的ではなく、データ量が許す複雑さの上限がたまたま軽いところにある、というだけである」** |
| 3 | `.steering/20260801-architecture-consolidation/decisions.md:52-61` | ★ 状態数を**決めない**と決定。理由 1 逐語 **「情報を持たない観測の上に状態構造を載せても事後分布は情報を持たない」**／理由 3 Codex #7 **「D 以外のベースラインを先に置き、D の複雑さに対する勝ち幅を測れ」** |

⚠️★★★ **そして既決 7（`.steering/20260810-.../decisions.md:73`「de-risk pilot 第 1 版は視覚 1 モダリティのまま」・
理由は「交絡と検出力 n=3–10」）は既にこの方向を向いていたのに、その後の議論はその外側で膨らんだ。**

### PS-D3: ★ 要素を識別する方法論は存在するが、GSE の n では回らない

★ [V81]（Collins, Dziak & Li 2009）/ [V82]: **factorial では各主効果を標本全体で推定できる**。
⚠️★★★ **しかし「条件あたり少人数でよい」は「総標本が少なくてよい」ではない。**
★ `media-expression-spec.md` §8 が既に書いている —— **C(8,4)=70 の離散性で主判定が事実上 AUC≈1.0 を要求**。
→ ★ **第 1 版の要素数が 1 に近い所へ落ちるのは倹約の美学ではなく検出力の算術である。**

### PS-D4: ⚠️★★★ [P93] Warnock 2011 の一次を取得し、repo の記述を訂正した

★ **前ラウンド最優先のやり残しを閉じた。** ⚠️ **閉じた結果、旧記述が半分だけ正しかった。**

| | 旧記述（`_index.md` 2026-08-14 行 / `references.md` [P93]） | ★ 一次で確認した内容 |
|---|---|---|
| 誤り率 | 「主タスクの中断量はモダリティによらず同じ」 | ★ **正しい**。**F(4,101)=16.57, p<0.0001** だが post hoc の有意差は **control vs 実験条件のみ**。逐語 **"there is no connection between task disruption and the modality of the notification"** |
| ⚠️★★★ 活動率 | **記述が無い（見落とし）** | ⚠️★★★ **モダリティ差が有意。F(4,101)=8.76, p<0.0001。**逐語 **"visual and audio conditions appeared to prompt the player to speed up"** —— ★ **視覚と音は同じ群に入り、どちらも作業速度を上げた** |

→ ★ **「音だけが特別に破壊的」は不成立（★ 前ラウンドの結論は維持）。**
⚠️ **同時に「音は無害」でもない。**
⚠️★★★ **さらに「モダリティは等価」と書いてはならない**（★ 等価性検定も BF も無い・否決 T-4）。
★ `references.md` [P93] を **provisional → active** に更新し、訂正を本文に書いた。

### PS-D5: ⚠️★★★ 引き継ぎ §3 の前提（運動符号は他者にも等しく効く）は条件付きになった

★ [P114] Nair, Ma & Abrams 2026（各 N=24・3 実験・被験者内）:

| 観察者の探索モード | 逐語 |
|---|---|
| ★ **一意形状の探索** | **"(1,057 ms) was significantly longer than when the distractor was absent (998 ms), t(23) = 4.57, p < .001, d = 0.41"** |
| ★★★ **事前指定形状の探索** | **"(560 ms) was not significantly different from ... (557 ms), t(23) = .79, p = .436, d = .026"** |

→ ★★★ **捕捉されるかは刺激ではなく観察者の探索モードで決まる。**
⚠️ **ただしカフェの隣席の人がどちらのモードかは、この論文からは決められない。**
→ ★ **A の問いは消えていない。「自明に危険」から「条件が特定された未検証」へ移った。**

### PS-D6: ★★★ C の gate —— 「作品になるか」には分野側が既に答えている

★ [P112] Skog, Ljungblad & Holmquist 2003（★ 一次全文・実配備・潜在利用者 約 300 名）逐語:
> **"In information visualization, aesthetics can almost be considered an added bonus, or at least a
> bi-product when striving for readability and effectiveness. In ambient information visualization, on
> the other hand, aesthetics is considered a primary property, both in the design and during use.
> When designing ambient infovis, it may even be necessary to go against established infovis guidelines
> in order to adhere to an artistic template."**

→ ★★★ **`spec` §9-8（S3-D11）の先送りは閉じられる —— 「α は作品になるか」に対し、
ambient 領域では「作品性は副産物ではなく一次的性質である」と一次が書いている。**

⚠️★★★ **しかし「作品性が効果を生む」の出典はゼロ**（否決 T-6）——
[P103] は評価を将来に置き、[P104] は設計論、**[P106] は Research through Design の質的研究**
（★ 本ラウンドで abstract 逐語確認・著者は Siying Hu, Zhenhao Zhang）。

### PS-D7: ★★★ 同じ「読めなさ」が、本人には欠陥・他者には保護として働く

★ [P112] の実配備の実数（★ 説明板 ＋ 配布資料 30 部 ＋ HP 記事を置いてなお）:

```text
6 名にインタビュー
  → 1 名は "did not know that some data was visualized"（★ 装飾だと思った）
  → 2 名は WHAT は分かるが HOW が読めない
  → 3 名が HOW まで到達
  → 実際に使ったのは 2 名（3 回 / 1 回）
```

⚠️★★★ **そして段を分けたのは「バス路線 16 を使うかどうか」＝ 文脈を共有しているかどうかだった。**
→ ★★★ **GSE では「自分の状態を知っている本人」と「知らない他者」がまさにその関係にある。**
→ ★ **A-7（他人に意味が読めない符号にする）は「暗号にする」必要がない ——
「文脈を持つ人だけが HOW に達する符号」で足りる。**★ **一次の裏付けが初めて付いた。**

### PS-D8: ★ 表現方法（技法）として一次から拾えたもの

| # | 技法 | 出所 |
|---|---|---|
| 1 | ★★★ **THAT / WHAT / HOW の 3 段で「どこまで読ませるか」を設計変数にする** | [P112] 逐語 |
| 2 | ★ **空間配置を記憶術にする**（★ 恣意的対応は覚えられず、**実在ランドマーク基準**が最良だった） | [P112] Lesson 4 |
| 3 | ★★★ **`壊れている` を様式の破れとして出す**（★ 黒い四角＝サーバ停止） | [P112] 逐語 |
| 4 | ★ **aesthetic ambiguity / slow revelation** | [P106]（★ **効果の出典ではない**） |

★ **反証 angle は逆を出した**: [P112] Lesson 3 逐語
**"Basing a visualization on an artistic style need not hinder – and might even support – the readability
and comprehension"** —— ⚠️ **ただし N=6 の質的観察なので、否定側（美にすると読めなくなる）も断定できない**（T-7）。

---

## ⚠️ 研究者に返す判断（★ 私は 1 つも決めていない）

| # | 判断 | 選択肢 | 私の見立て（★ 未承認） |
|---|---|---|---|
| ★★★ **PS-Q1** | ⚠️★★★ **表現層の第 1 版を「1 要素」に絞るか** | (a) 絞る（★ 既決 7 の理由をそのまま延長）／(b) 絞らず現在の形で進む（★ [P109] の線形を根拠に）／(c) 中間 | ★ **(a)**。★ 理由は [P110] の検出力・[V81] の算術・PS-D2 の内部先例 3 件。⚠️ **[P109] は反証だが 0–4 の範囲・単位違いで届かない** |
| ★★★ **PS-Q2** | ★ **その 1 要素を何にするか** | (a) 画面周辺の運動符号（C）／(b) 層 0（音）／(c) 物理オブジェクト | ★ **(a)**。★ **実測されたつまみを持つのはこれだけ** [P85]。⚠️ **(b) は [P93] 一次でも優位が出ず、活動率では視覚と同群** |
| ⚠️ **PS-Q3** | ★ **層 0 をどう扱うか**（★ 旧 PM-Q2 の (i)/(ii)/(iii)） | (i) 共変量 ／ (ii) アームに戻す ／ (iii) **第 1 版から外す** | ⚠️ **(iii) が第 1 波の算術から導かれる。★ しかしこれは研究者の音の構想を第 1 版から落とすことを意味する** → ★ **研究者判断** |
| **PS-Q4** | ★★★ **C の gate 判定を受け入れるか** | (a) `de-risk 先行`（★ 作品として設計してよい / 効果は主張しない）／(b) 別の判定 | ★ **(a)**。★ **S3-D11 の先送りはこれで閉じられる** |
| **PS-Q5** | ★ **本人と他者を、それぞれ THAT / WHAT / HOW のどの段で止めるか** | ★ 例: 本人=HOW / 他者=THAT ／ 本人=WHAT / 他者=THAT など | ★ **本人=WHAT、他者=THAT** を推す。⚠️ **理由: 表現層は効果を担わない（既に合意）ので、本人が HOW まで読める必要が無い** |
| ⚠️ **PS-Q6** | ⚠️ **RQ-3（カフェ / third place の規範）を次ラウンドで埋めるか** | (a) 埋める ／ (b) 設計で先に決めて後回し | ★ **(a)**。★ **本ラウンドで唯一探索できなかった angle** |

---

## ★★★ 研究者の回答（2026-08-15・セッション末）

> ★ **PS-Q1 / PS-Q3 / PS-Q5 の 3 件すべてに「まだ決めない」。**

⚠️★★★ **これは保留であって否決ではない。** ★ 3 件とも**未決のまま次に渡す。**
★ **私の見立て（(a) 絞る / (iii) 外す / 本人=WHAT・他者=THAT）は採用されていない。**
⚠️ **採用されなかった事実をここに記録する**（★ CLAUDE.md「自分の推奨が否決されたら、その事実を記録する」）。

### PS-D9: ⚠️★★★ 3 件とも「文献をもう 1 ラウンド回しても決まらない」可能性が高い

★ **保留を受けて、各判断を実際に動かすものが何かを洗い直した**（★ 提案であって決定ではない）:

| 判断 | ⚠️ **文献で埋まるか** | ★ **実際に動かすもの** |
|---|---|---|
| **PS-Q1**（1 要素に絞るか） | ⚠️ **部分的**（★ [P111] Bell 2013 / Wilson 2015 一次が符号を変えうる） | ★★★ **GSE 自身の検出力計算** —— **「1 要素なら何が検出でき、4 要素なら何が検出できないか」を n=3–10 で実際に数字にする**。★ `spec` §8 は既に **C(8,4)=70 の離散性で主判定が事実上 AUC≈1.0 を要求**と書いており、**同じ逆算を要素数について回せば答えが出る**（★ 文献ではなく計算） |
| **PS-Q3**（層 0） | ⚠️★★★ **埋まらない** | ★★★ **B1（層 0 = 1.0 で 10 分・「気になるか」）の実施** —— ★ `spec` §9-4 が **「α の可否はここでしか決まらない」**と明記している。★ 併せて §9-9（層 0 が壊していないことは未測定） |
| **PS-Q5**（THAT/WHAT/HOW） | ⚠️★★★ **埋まらない**（★ [P112] は 3 段の**尺度**を与えるが、どこで止めるかは設計判断） | ★★★ **試作を見て決める** —— ★ `experiments/20260812-expression-step4-grain/player/step4.html` は既にある。★ **研究者自身が被験者なので、どの段が要るかは聴取/試視で分かる** |

> ★★★ **帰結（★ 提案・未承認）**: ⚠️ **次の 1 手はサーヴェイではない可能性が高い。**
> ★ **PS-Q1 は計算 / PS-Q3 は B1 の実施 / PS-Q5 は試作の試視**で、それぞれ独立に動かせる。
> ⚠️ **ただしこれは私の見立てであり、研究者が「先に RQ-3 を埋める」と判断するなら、それが優先される。**

---

## ⚠️★★★ over-fitting を理由に減らして「よくない」もの（★ 既決との衝突を先に潰す）

⚠️★★★ **既決 D8（`.steering/20260810-.../decisions.md:149-150`・逐語）は交渉不可の半分を持つ**:
> **「Lv2 Wall を主軸から外すのは可。しかし表現層だけにして Physical Anchor を外すのは不可とする」**

→ ★★★ **over-fitting を理由に減らしてよいのは「表現層の内部要素」であって、D8 の構造ではない。**
★ 理由 3 本は生きている（[V40] structure 系に留まるには出口の行き先が要る／[P54] の
`change blind`・`make aware` だけでは情報提示に留まる／不便益 [P6] を担うのは離席・歩行）。

⚠️ **同様に減らしてはならないもの**:
- ★ `spec` §5 の**必須要件 4 件**（交渉不可）
- ★ **既決 D9（報酬版を採らない）／D10・D11（歩行は二値のみ）** —— ★ **PM-Q7 は依然未決**

---

## ⚠️ 断定していないこと（★ 記録が消えると無検証で再浮上する）

- ★ **表現層を 1 要素に絞るべきか** —— ⚠️ **決めていない**（★ PS-Q1）。
- ★ **音を第 1 版から落とすべきか** —— ⚠️ **決めていない**（★ PS-Q3）。★ **落とす根拠は強くなったが、決定は研究者のもの。**
- ★ **[P114] がカフェの隣席に外挿できるか** —— ⚠️ **できない**（★ 視覚探索課題である）。
- ★ **[P112] の歩留まり（6→3→2）が GSE に転移するか** —— ⚠️ **未検証**（★ N=6・2003 年・公共の大型画面）。
- ★ **「作品性が効果を生む」か** —— ⚠️ **出典ゼロ**（★ 否決 T-6）。
- ★ **RQ-3（カフェの規範）** —— ⚠️ **探索していない。**
- ★ **[P111] Bell 2013 が [P110] と符号が違うか** —— ⚠️ **abstract が取得できず未確認。**
