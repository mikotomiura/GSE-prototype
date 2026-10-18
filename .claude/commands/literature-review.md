---
description: >
  先行研究サーヴェイを 1 ラウンド分実行する。RQ を検証可能な下位問いに分解し、
  複数 angle で探索 → claim 抽出 → 敵対的 3 票検証 → 落合フォーマットのカード生成 →
  docs/references.md への append-only 登録 → docs/literature/_index.md 追記 →
  research-positioning.md §3/§4 への還元まで行う。「サーベイする」「先行研究を調べる」
  「この主張の証拠を確かめる」「Epic の go/no-go を文献で判定する」時に実行する。
allowed-tools: Read, Write, Edit, Grep, Glob, WebSearch, WebFetch, Task,
  Bash(date *), Bash(ls *), Bash(grep *), Bash(git *), Bash(python3 *)
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

### ★ 回し方（⚠️ メインで抱え込まない）

⚠️★★★ **angle ごとの探索をメインで直列に回さない。** ★ WebSearch の出力は長く、
メインの文脈を食い潰すわりに、**必要なのは抽出結果だけ**である。

- ★ **angle ごとに subagent へ分ける**（`model: sonnet`・`docs/loop-engineering.md:71` の
  「survey（探索・影響調査） = Sonnet」に従う）。★ 独立なので **1 メッセージで並列**に投げる。
- ⚠️ **渡し方の契約は `subagent-delegation` Skill**（★ 範囲・禁止事項・締切の 5 点を必ず書く）。
- ★ 各 subagent には **`citation-ssot` と `literature-card` を先に Read させる**。
  ★ 持ち帰らせるのは **逐語引用 ＋ 完全な書誌情報 ＋ 反証**（⚠️ 要約だけを受け取らない）。
- ⚠️ **subagent の中でさらに subagent を起動させない**（★ 汎用 agent に投げるので
  **必ず書く**側である —— `subagent-delegation` ルール 4 の相手別の表）。
  ⚠️★★★ 2026-09-19 の実測（`.steering/20260919-ssot-sr-systematic-review/deviations.md:13` 逐語）:
  「段 2 を全件に回したところ、**並列のサブエージェントが入れ子で 20 本以上に増え、
  月の利用上限に 2 回当たって全停止した**」。★ **並列数と総本数はメインが決める。**
- ⚠️★★★ **`references.md` への append は *メインが直列で* 行う。**
  ★ 理由: 採番 (`[Pn]` / `[Vn]`) は append-only の共有資源で、
  **並列に書くと採番が衝突する**（`citation-ssot`）。
- ⚠️ **一次資料の読解を subagent に代行させない**（★ 断定の根拠にするものはメインが開く。
  `verify-before-claiming` ルール 1 / 7）。

### ⚠️ PDF の読み方（★ WebFetch では読めない）

★ `WebFetch` は PDF を**読めない**が、**原本をローカルへ保存はする**。
→ ★ そのパスを **`pypdf`** で開けば一次全文が取れる。
⚠️ `Read` の PDF 経路は `pdftoppm` 不在のため**この環境では使えない**。

```python
from pypdf import PdfReader
print("\n".join(p.extract_text() or "" for p in PdfReader(path).pages))
```

⚠️ 要旨・二次記述だけで採番したなら、`references.md` の備考に
**「一次全文未取得」と明記する**（★ 黙って一次扱いにしない）。

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
- [ ] ⚠️ `python3 scripts/check_citations.py` が **`=== 違反なし ===`** で終わった（★ 下記 2）
- [ ] ⚠️ **このラウンドを単独でコミットした**（★ 下記 1）
- [ ] 文献 DB を作り直し、新しい書誌の要約を足して、シートと検索のページに反映した（下記 3）

## ★ ラウンドを閉じる（⚠️ 次ラウンドを始める前に）

> ★ 上の**完了条件の最後の 2 行の手順**である（⚠️ ここを読み飛ばすと完了条件が満たせない）。

### 1. ⚠️★★★ **毎ラウンド、その場でコミットする**

★ `references.md` / `_index.md` / `research-positioning.md` は**ラウンドをまたいで同じ行を触る**。
⚠️ 2 ラウンドぶんが未コミットで同居すると、**`git add -p` で分離できなくなる**
（★ 採番が連続しているので hunk が混ざる）。
→ ★ **1 ラウンド = 1 コミット**。次の angle を投げる前に閉じる。

### 2. ⚠️ `check_citations.py` は「違反なし」まで**繰り返す**

```bash
python3 scripts/check_citations.py
```

⚠️★★★ **1 回通っただけで「違反なし」と書かない。**
★ 是正すると**新たな違反が現れうる**（★ 追記・番号の付け替えで、欠番や重複の判定が変わるため）。
→ ★ **是正 → 再実行**を、**`=== 違反なし ===` が出るまで**繰り返す。

> ⚠️ **機構の断定を書かない**（2026-09-20 に一度書いて誤りだった）。
> ★ 実装（`scripts/check_citations.py:148-152`）は違反を `violations` に集約し、
> **`=== VIOLATION N 件 ===` として全件出力する**（★ 早期 `break` / `return` は無い）。
> → ★ 繰り返すのは **「打ち切られるから」ではなく「是正が新しい違反を生むから」**である。

### 3. 文献 DB を作り直す（1 と 2 の後に）

`references.md` に足した書誌を、スプレッドシート「GSE 文献DB」・検索のページ・`.bib` に反映する。手順の詳細は `scripts/refdb/README.md`（以下はその順番だけ）。

1. 読む枝を決める。`build.py` は `git show <枝>:docs/references.md` で読むので、作業ツリーの未コミットの変更は読まない（1 のコミットが先）。
   - この枝を push 済みなら `git fetch origin` し、`scripts/refdb/config.json` の `branches` に `origin/<この枝>` があるか見る。無ければ足す（main に入ったら外す）。
   - push 前なら、`--branches` に config の枝の一覧を渡し、その中の `origin/<この枝>` をローカルの枝名 `<この枝>` に置き換える。`--branches` は config の `branches` を丸ごと置き換えるので、ほかの枝も全部書く。
2. シートの「一覧」の値を読む（Sheets の `get_values`・範囲 `一覧!A1:T`）。返った JSON をファイルに書く。読んだ・メモを消さないため、これを飛ばさない。
3. 試しに回す: `python3 scripts/refdb/build.py --fetch --keep <2 のファイル>`（`--out` を付けないので出力は `~/.cache/gse-refdb/out/<日付>/`）。回すのは、この試しと 5 の本番の 2 回で、引数は `--out` のほかは同じにする。`pandoc` が無いと `.bib` で止まるので、そのときは `brew install pandoc` を研究者に頼むか、試しだけ `--no-bib` を付ける。
   - 終了コードを見るので、出力を `| tail` などのパイプに通さない。
   - 終了コード 3 で止まったら、表示された key のメモを `--rekey 旧=新` か `--keep-orphans` で扱う。どちらにするかは研究者に聞き、答えを足して試しを回し直す。key を直す場所は `references.md` だけで、シートの key を手で直さない。止まった回は `manifest.json` が出ないので、報告には止まった理由と聞いた問いを書く。
4. `missing_summaries.json` が空でなければ、`scripts/refdb/summary_prompt.md` の依頼文で要約を書かせ、`merge_summaries.py` で検査して `--write` で足す。「数値を目で確かめる」に出たものは目で見る。`summaries.json` の変更はこのラウンドの後に別のコミットにする。
5. `--out` に Drive の `文献DB/作業` を渡して作り直し、`--verify` で揃っていることを確かめてから、成果物（`.html`・`.csl.json`・`.bib` 2 本）を `文献DB` へ写す（README §1）。README §2 の手順でシートの「一覧」を差し替え、§4 で検索のページを同じ URL に出し直す。文献 DB の本体はスプレッドシートで、CSV はそこへ流し込むための受け渡し用。
6. 報告に `manifest.json` の件数（文献・要約・カードでの記述・要約が無いもの・CSL を最小限で作った数・結び直した読んだ・メモ）を書く。

## アンチパターン

- ❌ RQ を分解せず 1 問のまま検索する（温度が平均化されて gate 判定を誤る）
- ❌ **探索をメインで直列に回す**（文脈を食い潰す。angle ごとに subagent へ並列）
- ❌ **`references.md` への append を subagent にさせる**（採番が衝突する）
- ❌ **ラウンドを複数ためてからコミットする**（`git add -p` で分離できなくなる）
- ❌ **`check_citations.py` を 1 回だけ回して「違反なし」と書く**
- ❌ 反証 angle を省く / 有利な主張だけ甘く通す（対称性が壊れ、出力が gate に使えなくなる）
- ❌ 「該当研究ゼロ」を「弱い支持」と書く
- ❌ 否決した主張を記録せず捨てる（次ラウンドで同じ主張が無検証で再浮上する）
- ❌ 未確認の DOI / URL を書く（`provisional` で登録して確認に回す）
- ❌ 既存 [n] を renumber する / 削除する（inline 番号が全部ずれる）
- ❌ 凍結済み preregistration を本コマンドで書き換える
- ❌ シートの「一覧」を読まずに文献 DB を作り直して貼る（読んだ・メモが消える）
- ❌ シートの値を `references.md` へ書き戻す（書誌の正本は `references.md`）

## 関連

- Skill: `literature-card`（カード契約）/ `citation-ssot`（出典登録）/
  `reproducibility-discipline`（実験側の対応物）
- Docs: `docs/literature/_index.md`（索引 SSOT）/ `docs/references.md`（書誌 SSOT）/
  `docs/research-positioning.md`（還元先）
