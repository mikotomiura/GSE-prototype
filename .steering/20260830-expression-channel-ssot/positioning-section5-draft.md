# `research-positioning.md` §5（仮説）改訂案 —— ★★★ **適用済み**（2026-08-30）

> ★★★ **2026-08-30・研究者が追加承認したため、改訂 1〜5 をすべて `docs/research-positioning.md` §5 へ適用した。**
> ★ 併せて **`docs/architecture/gse-v2-overview.md:44`（「本人の自律性を損なわない範囲で」）も適用**した
> （→ 「**本人が自ら是認できる (self-endorsed) 範囲**で」）。
> ⚠️ **本ファイルは以降「案の記録」であり、SSOT は `docs/research-positioning.md` §5 である。**
> ★ 当初（同日の 4 択時点）は「§1 / §4 / §7 は適用、§5 は案提示のみ」だった。
>
> ★ 根拠はすべて 2026-08-30 のサーヴェイ 4 ラウンド（[P133]–[P191] / [V87]–[V88]）。
> ⚠️ **確証の核（H-X1 / H-X1b）は 1 文字も触らない。**★ 触るのは **H-Y の測り方 / H-PA / 新設 H-EXPR** である。

---

## 改訂 1 ⚠️★★ **H-Y —— 「悪化させない」の測り方に、主観だけでは足りないことを書く**

### Before（現行・逐語）

> **かつ成果物品質（第三者ブラインド）と NASA-TLX [V11]・自己効力感（GSE scale [P15]・副指標）を悪化させない**。

### After（案）

> **かつ成果物品質（第三者ブラインド）と NASA-TLX [V11]・自己効力感（GSE scale [P15]・副指標）を悪化させない**。
> ⚠️★★★ **2026-08-30 追加 —— 主観指標だけで「悪化させていない」と判定しない。**
> ★ autoplay を無効化した RCT（**N=76**・10–17 日）で **1 日の視聴が −21.0 分（p=0.003）**動いたのに、
> ★★★ **事前に 95% が「自分は視聴時間を制御できている」に同意していた** [P135]。
> → ★ **「悪化させない」の判定には *行動側の客観指標*（作業ログ・完了率・放棄率・時間超過）を必ず併報する。**
> ⚠️ **[P135] はエンタメの継続消費であって介入ではないので、「autoplay が有害だから GSE も有害」は成立しない**
> —— ★ **移るのは測定側の含意のみ**である（★ [V35] [P71] [P73] と同じ「主観は動くが客観は動かない／その逆」の型の 4 本目）。

---

## 改訂 2 ⚠️★★★ **H-Y —— Gate H の `autonomy loss` に計器を置く**

### Before（現行）

★ §5 に `autonomy` の記述は無い（⚠️ **`wbs-verification-halfyear.md:293` Gate H が
`autonomy loss` を *拒否権付きの反証ゲート* のアウトカムに据えているのに、尺度も理論も未登録だった**）。

### After（案・**H-Y の直後に 1 項追加**）

> - **H-Y-b (自律性の非毀損・運用指標)**: 介入あり(B) は介入なし(A) に比べ、**本人の自律性（autonomy）を損なわない**。
>   ⚠️★★★ **ここでいう autonomy は「選べること」ではない** —— SDT 原典逐語で **"regulation by the self"**、
>   反対の heteronomy は **"regulation that occurs without self-endorsement"** [P178]。
>   ★★★ *"having many options is not a basic need"* / *"one could have only one option … and yet feel quite
>   autonomous so long as one truly endorses that option"*。
>   → ⚠️★★★ **「opt-in と dismiss があるから自律性を脅かさない」という論法は使わない。**
>   ★ 正しい書き方は **「本人が事前に *是認 (self-endorse)* しているから」**である。
>   → **操作化**: **[V88] METUX の TENS-Interface の autonomy 下位尺度**を第一候補とする。
>   ⚠️ **著者自身が *"The measures presented are initial iterations that will require more thorough validation
>   and refinement"* と留保している**ので、★ **確証には使わず、`wbs-verification-halfyear.md` Gate H の
>   *運用指標* として使う。**
>   ⚠️ **併せて [P182] を併記する** —— k=99 研究・119 標本のメタ分析レビューが
>   *"contrary to SDT, the variance basic psychological needs account for in some of these outcomes is
>   **statistically significant but practically insignificant**"* と報告している
>   （★ [P99] に対する [P107] と同じ役割）。
>   ★ 一方 **[P182] の方法論的警告は GSE に有利**である: *"We therefore **discourage cross-sectional
>   self-report studies** dealing with basic psychological needs"* —— ★ **GSE の個人内・縦断・日次デザインは
>   SDT 文献が自ら求める方向にある。**
>   ⚠️★★★ **METUX は層をまたぐ矛盾も明記している**（逐語 *"a technology can support psychological needs at
>   one level while undermining them at another"*）→ ★ **GSE では「表現層で autonomy を支えつつ介入層で損なう」が
>   構造的にありうる**ので、**層ごとに測る**。

---

## 改訂 3 ★★★ **H-PA —— 完了条件・量・主張範囲の 3 つに制約を明記する**

### Before（現行・逐語）

> - **H-PA (Physical Anchor)**: 身体的アンカー（離席・歩行・自然）[P2][P8][P10] は、**受容（opt-in 率・拒否理由）と効果
>   （復帰後の手動入力・stuck 再発・主観的リセット感）を分けて**評価し、安全条件（夜間 Outdoor 無効）下で受容かつ有効である。

### After（案）

> - **H-PA (Physical Anchor)**: 身体的アンカー（離席・歩行）[P2][P8][P10] は、**受容（opt-in 率・拒否理由）と効果
>   （復帰後の手動入力・stuck 再発・主観的リセット感）を分けて**評価し、安全条件（夜間 Outdoor 無効）下で受容される。
>   ★ **2026-08-30 追加の制約 4 件**:
>   1. ⚠️★★★ **完了条件は「時間 ＋ 往復（復帰）」であって「歩数達成 / 距離達成」ではない**（既決 D11 条件 2）。
>      ★ 量で解放を決めると [P99] の performance-contingent（★ 目標に届かなかった群 `d = −0.88`）に入る。
>   2. ⚠️★★★ **量（歩数・距離・速度）を本人にも表現層にも渡さない**（既決 D11 条件 1）。
>      ★ [P77] 逐語 *"Even in the absence of explicit external incentives, measurement itself can thus have
>      similar effects."* ＝ **「報酬ではない」は防御にならない。**
>   3. ⚠️★★★ **「歩けば作業成績が上がる」は仮説に入れない** —— micro-break のメタ解析（**22 標本 / N = 2,335**）は
>      **活力 d = .36 / 疲労 d = .35** を支持する一方、**成績は全体で null（d = .16, 95% CI [−.04,.37], p = .116）**、
>      ⚠️ **認知的に負荷の高い課題では d = −.09** である [P162]。
>      ★ **GSE が「機会の保存」に主張を限定している設計は、この反証を最初から避けている。**
>      ⚠️ **逆に「歩けば作業が良くなる」を表現で暗示すると、文献に反する暗示を与えることになる。**
>   4. ⚠️ **Phase1 の実体は WoZ ＋ 自己申告**であり、⚠️ **本フェーズでは「有効である」を主張しない**
>      （★ 旧文の「受容かつ**有効**である」から「有効」を落とす）。
>   ★ 第 1 版の境界の形は **ADR-017 D3**（PC → スマホの一方向・inbound を作らない）。

---

## 改訂 4 ★★★ **H-EXPR（表現層・新設・探索的）**

### Before（現行）

★ §5 に表現層の仮説は無い（⚠️ **設計は `.steering/` と追跡外の `.idea/` にしか無かった**）。

### After（案・**H-PA の直後に 1 項追加**）

> - **H-EXPR (表現チャネル・探索的・⚠️ 効果を主張しない)**: 推定された内的状態を**常在面に非断定的に写す**表現層は、
>   **介入発火数・有害介入率（HIR）を悪化させず**、かつ**本人にとって読める**。
>   ★ **判定は `de-risk 先行`** —— ★ **作品として設計してよいが、効果は主張しない。**
>   ⚠️★★★ **これは逃げではなく、この系譜の標準的な作法である** —— Informative Art の創始者自身が自作物を
>   *"its usefulness as an awareness support is rather limited"* と書いており [P113]、
>   Slow Technology 系で最長の実配備すら **N=3 世帯・14 か月の質的研究** [P186] である。
>   → **操作化（3 点）**:
>   1. ★ **ON/OFF の無作為化 ＋ 作業ログの客観指標**で測る（⚠️ **主観だけでは害を検出できない** [P135]）。
>   2. ⚠️★★★ **「表現層のみ」を headline アームにしない** —— 既決 **D8**。
>      ★ 表現層が structure 系に留まれるのは「出口を開く」からで、**出口の行き先が Physical Anchor である**
>      （外すと [V40] の information 系 `d=0.00 / BF01=33.84` へ落ちる）。
>      ⚠️ **不便益の認定条件 1（労力）を満たすのは Physical Anchor だけである** [P170]。
>   3. ⚠️★★★ **displacement を避ける** —— [P187] 逐語 *"risks a **displacement**, wherein reflection is linked
>      with some desired outcome … and **assessment of that outcome is taken as evidence that reflection
>      occurred**"*。→ ★ **行動指標の改善を「反省が起きた証拠」にしない。**
>      ⚠️ 将来「表現層が反省を促した」と言うなら、正しい計器は [V77] TSRI / [V78] RRT / [P191] の水準 R0–R4 である。
>   → **設計 SSOT**: `docs/adr/ADR-017-expression-channel-boundary.md` / `docs/architecture/expression-channel.md`。

---

## 改訂 5 ★ **依存関係 —— 新設仮説の位置づけ**

### Before（現行・逐語）

> - **依存関係**: **確証ゲートは H-X1 / H-X1b（ともに L0 軸）のみ**。H-X1 が not-kill → H-Y / H-X2 / H-PA へ進む…

### After（案）

> - **依存関係**: **確証ゲートは H-X1 / H-X1b（ともに L0 軸）のみ**。H-X1 が not-kill → H-Y / H-Y-b / H-X2 / H-PA / H-EXPR へ進む…
>   ★ **H-Y-b（自律性）は Gate H の運用指標であって確証ゲートではない**（⚠️ **[V88] は著者自身が初期版と留保**）。
>   ★ **H-EXPR は探索的で、効果を主張しない**（`de-risk 先行`）。

---

## ⚠️ 本案が **触れていない**もの

- ★ **H-X1 / H-X1b / H-X1c / H-X2** —— ⚠️ **1 文字も触らない**（★ 確証の核 ＋ 凍結済みの操作化）。
- ★ **PreReg-1〜8** —— ⚠️ **触らない**（★ `preregistration-v0.3.md` は凍結・ADR-015 D5）。
- ★ **`gse-v2-overview.md:44` の「本人の自律性を損なわない範囲で」** —— ⚠️ **別途の研究者確認**
  （★ 案は「本人が **自ら是認できる (self-endorsed)** 範囲で」＋ [P178] を引く）。
- ★ **[P77] 実験 4 の 1 項目（work↔fun）の Phase1 投入** —— ⚠️ **入れない**（EC-D3・**PreReg-2 の凍結に荷重する**）。
  ★ 送り先は **Phase 1.5 / Gate H の運用指標**。
