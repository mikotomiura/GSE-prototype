---
description: >
  先行研究サーヴェイを 1 ラウンド分実行する。RQ を検証可能な下位問いに分解し、
  複数 angle で探索 → claim 抽出 → 敵対的 3 票検証 → 落合フォーマットのカード生成 →
  docs/references.md への append-only 登録 → docs/literature/_index.md 追記 →
  research-positioning.md §3/§4 への還元まで行う。「サーベイする」「先行研究を調べる」
  「この主張の証拠を確かめる」「Epic の go/no-go を文献で判定する」時に実行する。
allowed-tools: Read, Write, Edit, Grep, Glob, WebSearch, WebFetch, Bash(date *), Bash(ls *), Bash(grep *)
---

# /literature-review

`literature-card` / `citation-ssot` Skill の**実行コマンド**。両 Skill が「カード 1 枚の書式」と
「出典 1 件の登録」を定義するのに対し、本コマンドは **1 サーヴェイラウンド全体の手続き**を定義する。

> **前提 Skill (実行前に Read すること)**
> - `.claude/skills/literature-card/SKILL.md` — 落合 6 項目・カード契約
> - `.claude/skills/citation-ssot/SKILL.md` — `[Pn]`/`[Vn]` 名前空間・append-only・provisional
> - `docs/research-positioning.md` §8 — **エビデンス温度**（過大主張の禁止）

---

## Step 0: ラウンドの目的と予算を確定する

ユーザーに以下を確認する（未指定なら質問する。推測で始めない）:

1. **問い (RQ)**: 何を確かめるラウンドか
2. **用途**: 判定 gate（Epic の go/no-go）/ 設計根拠の補強 / ランドスケープ把握 のどれか
3. **名前空間**: 理論基盤なら `P`、検証方法論なら `V`
4. **予算**: 探索 angle 数（既定 3–5）・取得ソース数の目安（既定 15–25）

既存カードとの重複を先に潰す:

```bash
ls docs/literature/
grep -n "やり残し\|判定不能\|UNPROVEN\|証拠ゼロ" docs/literature/_index.md
```

> **既存カードが「やり残し」として名指しした穴を埋めるラウンド**は最優先。
> `_index.md` の該当行を引用して、本ラウンドの動機としてカード冒頭に書く。

---

## Step 1: RQ を検証可能な下位問いに分解する

RQ をそのまま検索しない。**(a) 現象は実在するか / (b) それを我々の手段で測れるか** のように、
**証拠の種類が変わる境界**で 2–4 問に割る。分解結果をユーザーに提示して合意を取る。

> なぜ割るか: GSE の過去ラウンドでは「(a) 過信は実在し害を生む＝確定」「(b) content-free 代理で
> 検出できる＝直接証拠ゼロ」と**下位問いごとに温度が真逆**になった。割らないと平均化されて
> gate 判定が誤る（`20260724-agentic-coding-overreliance-detection.md`）。

---

## Step 2: 多角探索（angle を変えて重複を減らす）

下位問いごとに **angle を変えた検索**を行う。同じ問いを言い換えるだけの検索は 1 angle と数える。
angle の例: 分野を変える（HCI / 教育心理 / SE） / 測定法を変える（RCT / 観察 / メタ分析） /
反証側から引く（null 結果・出版バイアス補正・失敗事例）。

**必ず反証 angle を 1 つ以上含める。** GSE に有利な証拠だけを集めると Step 3 の対称性が壊れる。

取得した各ソースについて記録する: 出典 key（DOI / arXiv / 正規化 URL）・N・設計・主要効果量。

> **禁止**: NDJSON セッションログ・キーストローク内容を検索クエリや外部送信に含めない
> (`data-privacy` Skill)。

---

## Step 3: claim 抽出

ソースから **「GSE の判断を動かしうる主張」だけ**を抜く（要約ではない）。1 claim = 1 行 +
根拠（数値・設計）+ 出典 key。この時点では真偽を決めない。

---

## Step 4: 敵対的検証（3 票パネル・対称フィルタ）

各 claim を **3 票**で判定する。票は **視点を変える**（例: 内的妥当性 / 外的妥当性・外挿 /
効果量の頑健性＝出版バイアス・補正後の値）。

| 票 | 意味 | 扱い |
|---|---|---|
| `3-0` | 全票が支持 | confirmed（本文で断定してよい） |
| `2-1` | 1 票が留保 | confirmed だが**留保内容をカード §5 に明記** |
| `1-2` / `0-3` | 否決 | **カード本体に書かない**。§否決リストに 1 行で残す |

**対称性の厳守**: GSE に有利な主張も不利な主張も同じフィルタにかける。有利な主張を甘く通した
時点でこのラウンドの出力は gate に使えなくなる。

**エビデンス温度**を claim ごとに 1 語で付す:

- `確定` — 直接証拠あり（設計・指標が問いに一致）
- `PLAUSIBLE BUT UNPROVEN` — 継ぎ接ぎでしか成立しない（**直接証拠なしに接する**）
- `判定不能` — コーパス中に該当研究ゼロ

> `判定不能` を「弱い支持」に丸めない。**ゼロはゼロと書く**のがこのラウンドの最大の価値。

---

## Step 5: カード生成

`docs/literature/<YYYYMMDD>-<topic-slug>.md` を作る。`card-template.md` の 6 項目を守り、
各カード見出しに **検証票と出典**を付ける:

```
### カードN: <主張を 1 行で> **[検証済 3-0 / 2-1]** [V45]
```

カード冒頭に必ず置く 3 ブロック:

1. **動機** — なぜこのラウンドを回したか（既存カードのどの「やり残し」か）
2. **検証状態** — 何ソース取得 / 何 claim 抽出 / 何件検証 / confirmed・refuted の内訳
3. **gate 判定（要点先出し）** — 下位問いごとに温度 1 行ずつ

末尾に **否決リスト**（Step 4 で 0-3 / 1-2 になった主張と否決理由）を必ず置く。

---

## Step 6: 出典を references.md に append-only 登録

`citation-ssot` Skill に従う。名前空間（`P` / `V`）の**末尾の次番号**から採番し、既存番号を
renumber しない。重複は DOI / arXiv / 正規化 URL の key で判定し、既出なら「重複」列で相互リンク。

- DOI / 版 / URL が未確認なら `provisional`（**捏造しない**）
- 既存 [n] を上書きする新証拠が出たら、旧行は `superseded` にして `→Pnn` を張る
  （例: [P19] d=0.65 → [P21] で上書き。番号は消さない）

---

## Step 7: _index.md に 1 行追記

`docs/literature/_index.md` の表に追記する（列: 日付 / トピック / ファイル / カード数 /
「やり残し」要約）。**「やり残し」要約が次ラウンドの入口**になるので、
次に誰かが何を埋めるべきかが読める粒度で書く。

---

## Step 8: research-positioning.md への還元

本ラウンドの結果が §3（ランドスケープ）/ §4（差分の主張）を **補強 / 反証 / 精緻化**の
どれをしたかを判定し、該当箇所を inline `[Pn]`/`[Vn]` 付きで更新する。

**反証だった場合は主張を下げる。** 過去ラウンドでは「摩擦が能力を育てる」→「自力解決の
機会を保存する」への**主張範囲の縮小**が正しい還元だった。

ADR / preregistration に影響する場合は、該当 ADR の「根拠」節にも [n] を張る（凍結済み
`docs/preregistration-v0.3.md` は**書き換えず**、影響を `.steering/` に記録して次改訂へ回す）。

---

## Step 9: Grill Me（自己点検）

- [ ] 反証 angle を含めたか（有利な証拠だけ集めていないか）
- [ ] 下位問いごとに温度が分かれていないか確認したか（平均化していないか）
- [ ] `判定不能` を「弱い支持」に丸めていないか
- [ ] 否決リストを残したか（否決の履歴が消えると同じ主張が再浮上する）
- [ ] 全カードの [n] が references.md に実在するか
- [ ] provisional と active を取り違えていないか（捏造 URL ゼロか）
- [ ] `_index.md` の「やり残し」が次ラウンドの入口になっているか

---

## 完了条件

- [ ] `docs/literature/<YYYYMMDD>-<topic-slug>.md` が生成された
- [ ] `docs/references.md` に append-only 登録された（renumber なし）
- [ ] `docs/literature/_index.md` に 1 行追記された
- [ ] `docs/research-positioning.md` への還元（または「還元不要」の判断）が明示された
- [ ] gate 用途なら **go / no-go / de-risk 先行**のいずれかを明言した

## アンチパターン

- ❌ RQ を分解せず 1 問のまま検索する（温度が平均化されて gate 判定を誤る）
- ❌ 反証 angle を省く / 有利な主張だけ甘く通す（対称性が壊れ、出力が gate に使えなくなる）
- ❌ 「該当研究ゼロ」を「弱い支持」と書く
- ❌ 否決した主張を記録せず捨てる（次ラウンドで同じ主張が無検証で再浮上する）
- ❌ 未確認の DOI / URL を書く（`provisional` で登録して確認に回す）
- ❌ 既存 [n] を renumber する / 削除する（inline 番号が全部ずれる）
- ❌ 凍結済み preregistration を本コマンドで書き換える

## 関連

- Skill: `literature-card`（カード契約）/ `citation-ssot`（出典登録）/
  `reproducibility-discipline`（実験側の対応物）
- Docs: `docs/literature/_index.md`（索引 SSOT）/ `docs/references.md`（書誌 SSOT）/
  `docs/research-positioning.md`（還元先）
