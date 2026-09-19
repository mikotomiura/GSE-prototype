# 体系的レビューのプロトコル（★ 検索を走らせる前に固定する）

> 固定日: 2026-09-19（★ このファイルを検索の実行より前にコミットする）。
> 根拠: 段 3 判断 1 #5〜#7（範囲 = RP §4 の差分候補だけ ／ 検索元 = OpenAlex ＋ Semantic Scholar API・ACM DL と PhilPapers は手動で補完 ／ 期間 = 制限なし〜2026-09 ／ 時期 = RP §4 を書く前）。
> ⚠️ 走らせた後に検索式・採否基準を変えたら、**変えたことと理由を `deviations.md` に書く**（黙って変えない）。

## 1. 問い

各差分候補について、**その候補を明示的に述べた・提案した・操作化した先行研究があるか**。

| ID | 由来 | 差分候補（★ 定義） |
|---|---|---|
| **C1** | S1 (a) | 適応系・自動化系が、**認識的権限**（意味の認定・評価・報酬化）を人へ返す（手放す）こと |
| **C2** | S1 (b) | 系とのやり取りが人に生む負担として、**解釈と説明要求**（出力の解釈・検証・説明を求められること）を記述・計上すること |
| **C3** | S1 (c) | 権限と責任が**そろったまま**人の側へ返っても、残務（解釈・検証・応答）が人へ移ること |
| **C4** | S1 (d) | 系が故障や限界ではなく、**価値判断によって任意に**権限を返す（手放す）局面 |
| **C5** | S2-1 | **見逃し可能性**: 介入・通知・招待に応答しないことを、選択・同意・不利益・評価低下の根拠として読まないこと |
| **C6** | S2-2 | **非再捕捉**: 利用者の応答（受諾・拒否・訂正）を、成功として学習・評価・報酬へ戻さないこと |
| **C7** | S2-3 | 系による**意味の認定と応答の要求を終了させること**を、設計の規範的な要件にすること |

## 2. 検索元と期間

- **OpenAlex**（`https://api.openalex.org/works`）: `filter=title_and_abstract.search:<式>`・`sort=relevance_score:desc`・`per-page=200`・**上位 200 件**まで。
- **Semantic Scholar**（`https://api.semanticscholar.org/graph/v1/paper/search`）: `query=<語>`・`limit=100`・`fields=title,abstract,year,externalIds,venue`・**上位 100 件**まで。⚠️ 鍵なしは 429 が返る → 5 秒以上あけて最大 6 回まで再試行し、取れなかった式は「取得失敗」と記録する（黙って落とさない）。
- **手動の補完**: ACM Digital Library と PhilPapers の検索画面で、各候補の Q_a の語を 1 回ずつ引き、上位 20 件の題名を見る（★ 再現性が低いので**補完**としてのみ扱う）。
- **期間**: 制限なし〜 2026-09-19。**言語**: 英語の検索式のみ（⚠️ 日本語の文献は対象外 → 限界に書く）。

## 3. 検索式（★ 固定）

> OpenAlex の式は論理演算（AND / OR / 引用符）を使う。Semantic Scholar は語の並び（論理演算なし）。

| ID | OpenAlex（`title_and_abstract.search`） | Semantic Scholar（`query`） |
|---|---|---|
| C1-a | `("epistemic authority" OR "interpretive authority") AND (algorithm OR "artificial intelligence" OR "intelligent system" OR "adaptive system" OR "user interface")` | `epistemic authority algorithmic system user` |
| C1-b | `("algorithmic restraint" OR "computational restraint" OR "designed restraint" OR "technological restraint")` | `algorithmic restraint design withholding inference` |
| C1-c | `("relinquish" OR "relinquishing" OR "relinquishment") AND (algorithm OR "artificial intelligence" OR automation) AND (interpretation OR meaning OR judgment OR evaluation)` | `system relinquishes interpretation judgment to user` |
| C2-a | `("interpretation burden" OR "interpretive burden" OR "interpretive labor" OR "interpretive labour" OR "interpretive work") AND (algorithm OR "artificial intelligence" OR automation OR "intelligent system")` | `interpretive labor algorithmic system users` |
| C2-b | `("verification burden" OR "burden of verification" OR "explanation burden" OR "burden of explanation") AND (user OR human)` | `verification burden AI users explanation` |
| C2-c | `("burden shifting" OR "burden-shifting" OR "shifts the burden" OR "shift the burden") AND (explanation OR explainability OR interpretation OR contestation) AND (AI OR algorithm OR automation)` | `explainability shifts burden to users` |
| C3-a | `(authority AND responsibility AND (mismatch OR consistency OR alignment OR "double bind")) AND (automation OR "human-machine" OR "human-automation" OR "human-robot")` | `authority responsibility consistency human automation` |
| C3-b | `("residual tasks" OR "leftover tasks" OR "left-over tasks" OR "residual work") AND (automation OR "artificial intelligence") AND responsibility` | `residual tasks automation operator responsibility` |
| C3-c | `("responsibility gap" OR "moral crumple zone" OR "liability sponge") AND (burden OR workload OR residual)` | `responsibility gap burden shifted to users` |
| C4-a | `("transfer of control" OR handover OR "hand-over" OR takeover) AND (voluntary OR deliberate OR "by design" OR "system-initiated") AND (value OR ethics OR ethical OR autonomy)` | `system-initiated handover of control by design ethics` |
| C4-b | `("adjustable autonomy" OR "sliding autonomy" OR "mixed-initiative") AND (ethics OR ethical OR "human agency" OR "value")` | `adjustable autonomy ethics human agency` |
| C4-c | `("self-limiting" OR "designing for disengagement" OR "designing for withdrawal" OR "restraint by design") AND (technology OR system OR design)` | `self-limiting technology designing for disengagement` |
| C5-a | `(ignorable OR ignorability OR "safe to ignore" OR "right to ignore") AND (notification OR nudge OR prompt OR intervention OR reminder)` | `ignorable notifications nudge design` |
| C5-b | `("non-response" OR nonresponse OR "no response" OR unanswered) AND (nudge OR "just-in-time" OR notification OR prompt) AND (penalty OR consequence OR interpretation OR choice)` | `non-response just-in-time intervention interpretation` |
| C5-c | `("silence as consent" OR "inaction as consent" OR "default as choice" OR "omission as choice") AND (design OR nudge OR technology)` | `inaction as consent nudge default` |
| C6-a | `("user feedback" OR "implicit feedback" OR "user response" OR "user correction") AND ("not used for training" OR "excluded from training" OR "without learning" OR "refrain from learning" OR "not learn")` | `user feedback excluded from learning adaptive system` |
| C6-b | `(refusal OR dismissal OR decline) AND (recommender OR "adaptive system" OR "just-in-time" OR notification) AND (respect OR honor OR backoff OR suppress OR suppression)` | `respecting user refusal adaptive system suppression` |
| C6-c | `("anti-extractive" OR "non-extractive" OR extractive) AND design AND (feedback OR engagement OR data) AND (user OR interaction)` | `non-extractive design user feedback engagement` |
| C7-a | `("response obligation" OR "obligation to respond" OR "response pressure" OR "responsiveness expectation" OR "availability expectation") AND (technology OR notification OR messaging OR system)` | `obligation to respond technology users pressure` |
| C7-b | `("designing endings" OR "designing for endings" OR "end of interaction" OR "ending interactions") AND (design OR HCI OR technology)` | `designing endings interaction HCI` |
| C7-c | `(("stop inferring" OR "cease inference" OR "semantic withdrawal" OR "withdraw interpretation") OR ("non-inference" AND design))` | `system stops interpreting user meaning design` |

## 4. 採否基準

### 段 1（題名と抄録）
- **採る**: (i) 対象が対話的・適応的・自動化・アルゴリズムの系（HCI・HRI・自動化・推薦・通知・介入）であり、**かつ** (ii) その候補（§1 の定義）を**明示的に**述べる・提案する・操作化する・実測する。
- **採らない**: 語が出てくるだけ／法的・組織上の権限で系と関係しない／候補と逆向きの主張しかない（★ ただし「逆向きの主流」の例として別に記録してよい）。
- 迷ったら**採る**（段 2 で落とす）。

### 段 2（本文）
- 公開本文（OA・著者版・arXiv）で候補の定義に当たる**逐語**を探す。本文が取れないときは抄録で判定し、「抄録のみ」と記録する。
- 判定: **該当**（定義に当たる逐語あり）／**部分**（一部の要素だけ）／**非該当**。

### 結論の書き方
- 該当が 1 件以上 → その候補は**既出**。RP §4 では差分として書かず、先行として引く。
- 部分だけ → **部分的に既出**。何が残るかを書く。
- 0 件 → 「**本プロトコル（検索式・検索元・期間・採否基準）の範囲で該当 0 件**」と書く。⚠️ 「先行研究が存在しない」とは書かない。

## 5. 手順と記録

1. 検索を走らせ、式ごとに**実行日時・件数（総数・取得数）・取得失敗**を `search-log.md` に書く。
2. 重複を DOI（無ければ正規化した題名）で除く。
3. 段 1 → 段 2。候補ごとに `screening-C<n>.md` に、段 1 で採った全件（題名・年・DOI・理由）と、段 2 の判定（逐語つき）を書く。
4. **検算**: メインが、段 2 で「該当 / 部分」とした全件の逐語を本文で照合する。段 1 で落とした件から候補ごとに無作為に 10 件を選び、落とした判断を見直す。
5. PRISMA 型の件数表（検索 → 重複除去 → 段 1 → 段 2 → 該当）を `results.md` にまとめる。
6. 該当・部分の文献は `docs/references.md` に append-only で登録する（`citation-ssot`）。

## 6. 既知の限界（★ 先に書く）

- ⚠️ Scopus / Web of Science を使わない（段 3 判断 1 #6）。OpenAlex と Semantic Scholar の索引の漏れはそのまま残る。
- ⚠️ 英語の検索式のみ。日本語の文献は対象外。
- ⚠️ 関連度順の上位で打ち切る（OpenAlex 200・Semantic Scholar 100）。下位の該当は拾えない。
- ⚠️ 段 1 / 段 2 のふるい分けは言語モデルのサブエージェントが行い、二重のふるい分けはしない。→ 手順 4 の検算で補う。
- ⚠️ 候補の定義が新しい言い方なので、同じ中身を別の語で書いた文献は検索式に掛からないことがある（★ 手動の補完と、既知の文献（S1 / S2 のカード）の引用・被引用で補う余地がある。今回は行わない）。
