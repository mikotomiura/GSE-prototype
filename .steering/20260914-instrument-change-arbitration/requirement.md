# 計器を変える一式を 1 本で裁く（ADR-032）

## 背景

★ `ADR-030 D11` は「**計器を変えない範囲**（`T0` / `T1a` / `T1b` / `T1d` / `Q`）だけを開け」、
⚠️ **変える範囲（`T1c` / `T2` / `T3`）の採否を本文で決めなかった** —— 逐語:

> ★ **計器変更 ＋ 再配布を伴う一式として、別タスクで一括して裁く**
> （★ `.steering/20260911-outcome-arbitration-and-o1-preflight/decisions.md` **判断 12** が置いた
> 研究者指示の順序「**idea 議論 → Mh-D 全体の修正 → 再配布**」に乗せ、**起票 11 の ESM と 1 本に束ねる**）。

→ ★ **その送り先が本タスクである。**

★ さらに **2026-09-14 の研究者判断**で、**ADR-031（6 択 ESM）の M5 / M2 に伴う再配布を本タスクの裁定と
同じリリースへ束ねた**。⚠️★★★ **その結果、本タスクが「唯一締切を持つもの（ESM）」の律速になった。**
★ 同意の再開封を **2 回から 1 回**に減らすのが束ねの目的である。

⚠️★★★ **これは *費用* の裁定ではない。*禁止* の再審である**（`ADR-030 D11` 逐語:
「上表を『計器変更 ＋ 再配布のコスト』として読むと、次タスクが**費用比較から始まり、境界が値切られる**」）。
→ ★ **「いくらかかるか」ではなく「禁止を解くか」から書く。**

## ゴール

★ **① 〜 ⑦ の 7 項目を 1 本の ADR（ADR-032）で裁く。** 各項目に

1. ★ **解く / 解かない**（⚠️ 費用からではなく禁止から書く）
2. ★ 解くなら **何の約束が破れるか**（⚠️ 逐語で特定する）
3. ⚠️ 解かないなら **何が測れなくなるか**（★ 「不要」で済ませない）

を書く。

| # | 裁定対象 |
|---|---|
| ① | `T1c` の `undo` / `redo` 往復 |
| ② | `T2` の「元の app へ戻った」 |
| ③ | `T3` domain-local events |
| ④ | `.idea/survey §6.3` の IME content-free 状態機械 |
| ⑤ | 起票 6（ライブ変換 ON で ESC 1 回が `abandon` を過大にする） |
| ⑥ | `.idea/survey §6.2` 第一仮説を accept するか |
| ⑦ | ADR-031 の配布を本タスクと同じリリースへ束ねる |

## スコープ

### 含むもの
- ★ `docs/adr/ADR-032-*.md`（新規・**Proposed**）
- ★ `docs/adr/ADR-031-*.md` §Migration への **1 行追補**（⑦）
- ★ `docs/adr/README.md` の索引行
- ★ `.steering/20260914-instrument-change-arbitration/`

### 含まないもの
- ⚠️★★★ **コード変更**（★ 裁定であって実装ではない。実装は Accepted 後）
- ⚠️★★★ **`ADR-030 D10 / D11` の蒸し返し**（★ Tier 枠・投資順序・仕切りは accept 済み）
- ⚠️★★★ **特徴リストの accept**（★ D10 逐語「特徴を増やせば精度が上がるとは仮定しない」）
- ⚠️★★★ **ADR 本文の *決定* の書き換え**（★ 改訂は番号の大きい ADR へ）
- ⚠️★★★ **`docs/preregistration-v0.3.md` の書き換え** / **`HMM_VERSION` の bump**
- ⚠️★★★ **`.idea/` 本文** / **`.steering/` の過去記録**の書き換え
- ⚠️★★★ **O1 の配布**（★ ADR-014 判断 4 の境界は「**配布**」）
- ⚠️ **起票 16 / 17 / 18 の裁定**（★ 入力として読むが本タスクでは裁かない）

## 受け入れ条件

- [ ] 1. 新 ADR（ADR-032）が ① 〜 ⑦ を裁いている
- [ ] 2. ⚠️ 各項目に「**解く / 解かない**」と「**破れる約束 / 測れなくなるもの**」が逐語で書いてある
- [ ] 3. **引用（`[Pn]` / `[Vn]`）が付いている**（`citation-ssot` ルール 1・⚠️ **ADR も対象**）
- [ ] 4. `docs/adr/README.md` に行が足してある
- [ ] 5. **ADR-031 に「配布は本タスクと同じリリース」の追補**が入っている
- [ ] 6. ⚠️ **コード変更ゼロ**（`git diff --stat` で `src-tauri/` が 0 行）
- [ ] 7. `check_citations.py` / `check_doc_lexicon.py` が緑（⚠️ 「違反なし」まで繰り返す）
- [ ] 8. `code-reviewer` ＋ `security-checker` を**並列**で通し HIGH を消化
- [ ] 9. `/cross-review` を**パス限定**で通している（⚠️ `docs/mitou_submission/**` を送らない）

## 関連ドキュメント

- `docs/adr/ADR-030-stall-onset-and-decision-episode.md` **D10 / D11**（★ 蒸し返さない枠）
- `docs/adr/ADR-031-self-reported-activity-audit-criterion.md`（★ ⑦ の追補先）
- `docs/adr/ADR-014-continuous-natural-work-collection.md` **判断 6 / D4 の禁止表**
- `docs/adr/ADR-009-recovery-risk-axis-and-latent-state.md` **D2**（★ 役割カテゴリの条件）
- `.claude/skills/data-privacy/SKILL.md` **ルール 7**
- `.idea/20260910-mhd-feature-work-behavior-literature-gap-survey.md`（★ **551 行・全文**）
- `.idea/20260910-mhd-criterion-practice-trace-and-g-o-validation.md`（★ **349 行・全文**）
- `.steering/20260911-outcome-arbitration-and-o1-preflight/` **判断 12 / 起票 6**
- `.steering/20260913-mhd-inference-ssot/blockers.md` **起票 16 / 17 / 18**

## 運用メモ

- **/reimagine 適用**: **No**
- **理由**: ⚠️★★★ **`/reimagine` は実装着手前専用**（CLAUDE.md）であり、本タスクは
  **コード変更ゼロの裁定**である。★ かつ代替案の比較は既に 2 段で済んでいる ——
  (a) 各項目の選択肢を一次資料から起こし、(b) **① / ② / ⑤ は 3 択で研究者が 2026-09-14 に採択**した
  （→ `decisions.md` 判断 1 / 2 / 3）。★ プラン段階の承認も取得済み。
