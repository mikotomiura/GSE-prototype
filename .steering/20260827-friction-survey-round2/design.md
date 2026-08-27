# design — 摩擦操作サーヴェイ 第 2 ラウンド

## アプローチ

`/literature-review` の Step 0–9 をそのまま実行する。★ 下位問いと gate 基準は
`.steering/_handoff/next-session-prompt-friction-survey-round2.md` §1 / §2 が既に凍結しているので、
Step 0–1 は**議論し直さずそのまま採る**（★ 見る前に宣言済みという性質を壊さないため）。

## 下位問いと gate 基準（★ 探索前に凍結・handoff からの引き写し）

| | 下位問い | 名前空間 | gate 基準 |
|---|---|---|---|
| **R1** | 多文書統合は *主観的に* 重いのか | `P` | [P133] 本文で「文書数」が主観的難易度を上げるが**総テキスト長を統制した上で**成り立てば → (a) が生きる |
| **R2** | 時間圧・短時間課題で、要求と主観的難易度の関係は保たれるか | `P` | 崩れる／反転する報告があれば → (b) の最小改修に go。**該当研究ゼロなら `判定不能` と書く** |
| **R3** | 課題文の難易度を事前に揃える標準手続きと必要 N | `V` | 手続きと慣例 N が特定できれば (a) は実行可能。**2 ラウンド連続で `判定不能` なら文献では決まらないと結論** |
| **R4** | 方向性のある操作チェックの設計 | `V` | 事前登録例が 1 件でもあれば (c) はその形を採る。**ゼロなら自前で設計し「先行例なし」と明記** |

## 変更対象

| ファイル | 何を |
|---|---|
| `docs/literature/20260827-manipulation-check-attainability-and-task-complexity.md` | **新規**（10 カード） |
| `docs/references.md` | **append-only** で `[P135]`–`[P143]` / `[V88]`–`[V105]` を登録（★ `[P142]` は tombstone）＋ `[P36]` へ追記 |
| `docs/literature/_index.md` | 1 行追記 |
| `docs/research-positioning.md` | `§8` 方法論的限界へ**プローブ反応性の精緻化**を追記 |
| `experiments/20260801-controlled-friction-task/notes.md` | `§15` を追記（★ 実験側に効く結論と第 18 版の議題） |
| `.steering/20260827-friction-survey-round2/` | 作業記録 |

⚠️ **触らないもの**: `preregistration.md`（第 17 版・凍結）／`analyze.py`／`config.json`／
`results/metrics.json`（★ `verdict_sealed: true` を保つ）／`materials/`／O1 側の成果物

## 検証戦略

1. ★ **機械検算**: `python3 scripts/check_citations.py` が **違反なし**になること
   （未登録参照 / 同一名前空間内の key 重複 / tombstone の引用 / 欠番）
2. ★ **一次照合**: 判定を左右する逐語・数値は **メインが自分で原文にあたる**（D-3）
3. ★ **自前計算の再現性**: `Φ(d)` 写像・二項検定・検出力・CI・共線性は Python で計算し、
   **仮定を本文に明記する**（★ 文献の引用ではないことが読者に分かる形で）
4. ★ **敵対的検証**: 1 claim につき 3 subagent・視点を変える・1 agent に 3 票を書かせない

## ⚠️ リスクと対処

| リスク | 対処 |
|---|---|
| 検索エンジンの合成要約を証拠にしてしまう | ★ ソースを 1 件ずつ特定し、**到達水準を必ず明記**させる |
| PDF が binary で返って読めない | ★ **ローカルに保存されている**ので `Read` の `pages` / `pdftotext` で読む |
| 出版社が 403 | ★ green OA / 著者所属リポジトリ / `r.jina.ai` / core reader を当たる。**取れなければ `provisional`** |
| `references.md` の採番が O1 トラックと競合 | ★ **採る前に末尾を読み直す**（今回は `git fetch` 後に origin/main が `docs/references.md` を 1 行も触っていないことを確認済み） |
| 有利な証拠だけを集めて対称性が壊れる | ★ **反証専任の subagent を 1 つ立てる**＋ 敵対的検証で同じフィルタを両側にかける |
