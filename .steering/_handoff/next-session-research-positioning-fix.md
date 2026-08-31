# 次セッション用プロンプト — research-positioning.md の是正と de Jong カード化

> 作成: 2026-08-31 / 前タスク: `.steering/20260830-mitou-2027-proposal-slimming/`
> ★ このファイルを **新セッションで丸ごと読ませてから** 作業を始める。

---

## 前提（CLAUDE.md の制約・省略不可）

1. **`/start-task` を先に起動する。**該当コマンドを使わずに作業を始めない。
2. **docs/ の先読み**: `@docs/agent-shared.md` のリンクハブから該当 docs を先に読む。
3. **必須 Skill を Read してから手を動かす**: 本タスクでは
   `citation-ssot`（append-only 採番・tombstone 規約）/ `literature-card`（落合フォーマット）/
   `verify-before-claiming`（断定の前に一次資料へ降りる）。
4. **サーヴェイ・WebSearch はサブエージェントへ委譲する**（メインで抱えない）。
   `docs/references.md` への append は**メインが直列で**行う（並列 append は採番が壊れる）。
5. **完了時に `/cross-review` を必ず実行**（`-- <paths>` でパス限定。無関係な未コミット変更で BLOCKED するため）。
6. `.steering/` への記録を省略しない。

---

## 背景

2026-08-30〜31 の未踏 2027 提案書の書き直しで、サーヴェイ 4 本を回した。その副産物として
**`docs/research-positioning.md` に 4 件の不整合**が見つかったが、**当該タスクのスコープ外として残してある**。

サーヴェイの一次証拠と逐語は **`.steering/20260830-mitou-2027-proposal-slimming/survey-notes.md`（331 行）**
に全部ある。**まずこれを読むこと。** 再サーヴェイは不要。

---

## やること 1: `docs/research-positioning.md` の是正（4 件）

### (1) 最重要 —— ART（注意回復理論）が限定資源モデルであることへの対処

**判明した事実**（`survey-notes.md` 結論 4）:

- Stevenson et al. (2018) の abstract 冒頭・逐語:
  *"Attention Restoration Theory (ART) predicts exposure to natural environments may lead to improved
  cognitive performance through **restoration of a limited cognitive resource**, directed attention."*
- **Kaplan & Berman (2010)** *Perspect. Psychol. Sci.* 5(1):43–57, DOI 10.1177/1745691609356784 が、
  ART を **Baumeister の ego depletion とグルコース仮説に明示的に接続している**。
- **両方とも死亡が確認済み**（Hagger 2016 k=23/N=2,141 で d=0.04 ／ Vohs 2021 k=36/N=3,531 で d=0.06 ／
  Carter 2015 の PEESE b=0.003 ／ グルコースは Vadillo 2016・Finley/Schmeichel 2019 が否定）。
- **事前登録された ART の検定は 5 本すべて null**（ART II の筆頭著者自身の RCT を含む）。

**現状の問題箇所**: `docs/research-positioning.md` **L209** が
[P10] Kaplan ART を「**Physical Anchor の理論基盤**」として引いている。

→ **やること**: ART を「理論基盤」から外し、`survey-notes.md` の「書ける最強の形」に置き換える。
★ 使う語彙は「**関与の再開**」であって「回復」「消耗」ではない
（**Lin et al. 2020** 事前登録 4 実験・N=686 ／ **Hopstaken et al. 2015** —— 逐語
*"After increasing the rewards, all measures reverted to higher levels."*）。

### (2) [P8] Oppezzo & Schwartz (2014) が `active` のまま現役引用されている

⚠️ **未踏文書では取り下げ済みだが、SSOT では取り下げられていない。**
`docs/references.md:41` が `active`、`research-positioning.md` の **L111 / L209 / L211 / L657 / L667 / L749**
で引用されている。⚠️ 特に **L211 は逐語「歩けば認知が回復する」の理論根拠として引いている。**

→ **やること**: `citation-ssot` の tombstone 規約に従って [P8] を処理し、本文 6 箇所の引用を外す。
⚠️ **番号は再利用しない。**

### (3) ★★★ Lv2 Wall が「現行機能」として書かれている

⚠️ **ADR-015（2026-08-23）で削除済みなのに、SSOT が古いまま。**
**L228** 逐語: 「GSE の現行レパートリーは Lv1 Nudge（柔らかい）と **Lv2 Wall（硬い）**の二極に張り付いており」
／ **L597** / **L602**（「Wall は画面全体を塞ぎ、解除はスマートフォンからの `POST /unlock` のみ」）。

→ **やること**: 現行機能の記述から Wall を外す。
★ 併せて **ADR-018 D7 で段階呼称 Lv1〜Lv4 は廃止方向**になっているので、実体名（Nudge / Physical Anchor）へ。
⚠️ ただし **docs/ 全体の一括改名は別途判断が要る**（過去 ADR の本文改変は履歴を損なう）。

### (4) [P166] Stevenson 2018 の読み方が危険

**L456** が「実環境 > 仮想環境 ＝ GSE に有利」と読んでいるが、
⚠️ **同じ著者の事前登録 RCT（Stevenson et al. 2021, *JEP* 77:101679）は null**であり、
著者自身も *"this may also be due to differences in the typical lengths of exposure"* と留保している。
→ そのまま出すと自傷になる。

### ★ 併せて解ける未解決事項

**L457** の「[P162] vs [P166] の未解決の矛盾」は **用量**でほぼ説明できる ——
Albulescu [P162] は **≤10 分**の micro-break、**Bell et al. (2025)** *J. Environ. Psychol.* 104:102632 の
最適は **約 30 分**で、*"Nature benefits were generally larger for participants who underwent cognitive fatigue"*。
⚠️ ただし **Bell の本文は未取得**（abstract / highlights のみ）。断定する前に一次を取ること。

---

## やること 2: de Jong et al. (2020) のカード化

**de Jong, M., Bonvanie, A. M., Jolij, J. & Lorist, M. M. (2020)**
"Dynamics in typewriting performance reflect mental fatigue during real-life office work."
*PLOS ONE* 15(10):e0239984, DOI 10.1371/journal.pone.0239984（**OA**）

★★★ **GSE のセンシング方式そのものの先行研究である。**実オフィスで 6 週間、打鍵動態から精神的疲労を検出。

**取得済みの逐語 2 本**:
> *"although office workers are entitled to have breaks during a working day,
> **the scheduled breaks might not have been enough to fully recover**"*

> *"personalized real-time feedback based on changes in typing behavior could be provided…
> **However, real-time feedback might be biased due to dynamics in typewriting performance
> that are not related to lapses in performance.**"*

⚠️ **後者は GSE の偽陽性リスクを著者自身が名指ししている。**カードの「議論」欄に必ず入れること。

→ `literature-card` Skill の落合フォーマットで `docs/literature/<日付>-typing-dynamics-mental-fatigue.md` を作り、
`docs/literature/_index.md` に追記し、`docs/references.md` に append する。

---

## 未登録の一次資料（`docs/references.md` へ append する候補）

★ **次番号は `[P192]` / `[V89]`**（2026-08-31 時点）。
⚠️ **Perry et al. は既に `[V45]`/`[V51]`、Buçinca et al. は `[P127]`/`[V37]` として登録済み** —— 重複注意。

`survey-notes.md` に逐語つきで揃っている未登録分:

| 群 | 文献 |
|---|---|
| ego depletion の再現性 | Hagger 2016 / Vohs 2021 / Carter 2015 / Friese 2019 / **Lin 2020** / Dang 2021 / Kurzban 2013 / Agrawal 2022 / Vadillo 2016 / Finley 2019 |
| 生成AI下の認知的関与 | **Burelli 2026** / Lee 2025 (CHI) / Afshar 2025 (NEJM AI) / Lukac 2025 |
| 検証を飛ばす・主観の乖離 | **Skitka 1999** / **Parasuraman & Manzey 2010** / **Fan 2026 (CHI)** / **Parry 2021** / Murphy-Hill 2021 / Deslauriers 2019 / **Khojah 2026（反証側）** |
| 休憩の媒体 | **Kang & Kurtzberg 2019** / **Grobelny 2024** / Arnberger 2026 / Fan & Baharum 2024 / Sianoja 2018 / Hunter & Wu 2016 / Kim 2018 |
| ART の反証 | **Stevenson 2021 RCT** / Hartanto 2023 / Augustinova 2022 / Neilson 2021 / McDonnell & Strayer 2024 / Joye & Dewitte 2018 / **Kaplan & Berman 2010** |
| センシングの先行 | **de Jong 2020** |
| 計測反応性 | König 2022（★ 技術設計書には [54] として既出） |

---

## ⛔ 引用してはいけないもの（サーヴェイが名指しした分・必ず守る）

1. **METR arXiv:2507.09089 の 19% を現在の事実として** —— 著者自身が
   *"no longer reflect the current impact"* と宣言済み。乖離の実証としてのみ、historical と明記して引く。
2. ⛔⛔ **Alter et al. (2007) の disfluent font 効果** —— **死んでいる**。
   Meyer et al. (2015) *JEP:General* 144(2):e16–e30 が **17 実験・N=7,367** で
   *"no evidence of a disfluent font benefit under any conditions"*。
   ★ **「摩擦が熟慮を起こす」を Alter で正当化してはいけない**（Buçinca 2021 か Deslauriers 2019 を使う）。
3. **Kosmyna et al. "Your Brain on ChatGPT"** —— 本文冒頭に *"Preprint, under review"*。
4. **Yu et al. arXiv:2606.22721** —— journal_ref なし・因果同定なし。
5. **Fisher et al. (2015) を「主観と実測の乖離」の証拠として** —— **客観指標が 1 つも無い**。
   必ず **Eliseev & Marsh (2023)** と対で。
6. **Porter et al. (1998) を「検査速度が効く」証拠として** —— 逐語で
   *"did **not** significantly influence the defect detection rate"*（前提が逆）。
7. **SmartBear/Cisco の「200 LOC/hour」** —— 出典なしの伝聞。ベンダー資料。
8. **Parasuraman & Riley (1997) を complacency の定義として** —— **この論文は定義していない**。
9. **Kruger & Dunning (1999) を「人は自己評価できない」証拠として** ——
   Nuhfer et al. (2017, N=1,154) が **r=.60** を報告。

---

## 触ってはいけないもの

- ⚠️ **`docs/preregistration-v0.3.md`** —— **凍結文書**。ずれは記録として残す。
- ⚠️ **過去 ADR の本文**（ADR-001〜017）—— 改訂は**新規 ADR の追補**で行う（ADR-012 / ADR-018 の先例）。
- ⚠️ **`docs/mitou_docs/`** —— 2026-08-31 に確定済み。本タスクでは触らない。
- ⚠️ **`src-tauri/` / `src/`** —— コード変更ゼロ。

---

## 完了条件

- [ ] `research-positioning.md` の 4 件が是正され、ART が「理論基盤」から外れている
- [ ] [P8] が tombstone 化され、本文 6 箇所の引用が外れている
- [ ] Wall が現行機能として登場しない
- [ ] `docs/literature/` に de Jong カードがあり、`_index.md` に載っている
- [ ] `docs/references.md` に未登録の一次資料が append されている（採番は append-only）
- [ ] `PYTHONUTF8=1 python scripts/check_citations.py` が違反なし
- [ ] `git status --porcelain src-tauri src` が空
- [ ] `/cross-review` をパス限定で実行済み
