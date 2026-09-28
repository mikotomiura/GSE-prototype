# [P434] 転記の人による照合表（判断 16）

> 目的: 転記 A と B はどちらも LLM（同じモデルの独立な 2 インスタンス）によるもので、バイト単位で一致した。
> ⚠️ 同じモデル同士の一致は「共通の読み違い」を防げないので、研究者が PDF と目で照合する。
> 所要: 約 10 分。終わったら末尾の「結果」に日付と結果を書く（→ 論文用リポジトリの `data/li-coblenz-2026/README.md` に反映する）。

## 開くもの

- PDF: `C:/self-resolution-measure/raw/li-coblenz-fse2026-arxiv2602.11435v3.pdf`
  （arXiv:2602.11435v3・SHA-256 `4b3ba562…`。同じものは https://arxiv.org/pdf/2602.11435v3 ）
- 頁は論文の頁番号（各頁の上端の `FSE049:N`）: **Table 4 = FSE049:7** ／ **Table 5 = FSE049:16** ／ 本文の引用 = FSE049:8・14・15

## 1. Table 4（FSE049:7）—— Task・Time・Resolved

| ✓ | Task | Time（論文の表記） | 転記の分 | Resolved |
|---|---|---|---|---|
| [ ] | P1TA | 2 h 25 min | 145 | Y |
| [ ] | P2TA | 18 min | 18 | Y |
| [ ] | P2TB | 12 min | 12 | Y |
| [ ] | P3TA | 36 min | 36 | Y |
| [ ] | P4TA | 32 min | 32 | **N** |
| [ ] | P5TA | 10 min | 10 | Y |
| [ ] | P5TB | 25 min | 25 | Y |
| [ ] | P5TC | 25 min | 25 | Y |
| [ ] | P6TA | 45 min | 45 | Y |
| [ ] | P6TB | 40 min | 40 | Y |
| [ ] | P7TA | 1 h 20 min | 80 | Y |
| [ ] | S1TA | 11 min | 11 | Y |
| [ ] | S2TA | 50 min | 50 | Y |
| [ ] | S3TA | 26 min | 26 | **N** |
| [ ] | S4TA | 10 min | 10 | Y |
| [ ] | S4TB | 27 min | 27 | **N** |
| [ ] | S5TA | 1 h 54 min | 114 | **N** |

★ 検算（機械で確認済み）: Y = 13・N = 4。N の 4 つは本文 FSE049:8 の "(P4TA, S3TA, S4TB, S5TA)" と一致。参加者 11 task の合計 468 分 = 本文の "7.8 hours" と一致。
⚠️ 配信者 6 task の合計 238 分は本文の "3.1 hours" と合わない（論文側の食い違いとして記録済み・転記の誤りではない）。

## 2. Table 5（FSE049:16）—— 外部資源の 3 行の "Application in Task"

| ✓ | 行（Name） | 論文の列の表記どおりに転記した task |
|---|---|---|
| [ ] | documentation | S1TA, S2TA, S4TB |
| [ ] | social-technical sources | S2TA, S3TA |
| [ ] | web sources | P2TB, P7TA, S1TA |

★ この 3 行に挙がっていない task は、転記ではすべて 0（参照なし）。和集合は 6 task（P2TB・P7TA・S1TA・S2TA・S3TA・S4TB）。

## 3. 本文の引用（感度分析 `table5_plus_text` で追加した 2 task）

| ✓ | task | 頁 | 逐語（`text_external.csv`） |
|---|---|---|---|
| [ ] | S5TA | FSE049:14（§4.2.3） | "some streamers engaged directly with chat participants to brainstorm solutions with viewers in real time (S3, S5)" |
| [ ] | P1TA | FSE049:14（§4.2.3） | "P1 similarly identified colleagues with relevant expertise and redirected the issue to those best equipped to resolve it" |
| [ ] | P1TA | FSE049:15（§4.3.1） | "P1 spent time reviewing reports of similar issues to learn how they had been handled" |

★ 判断してほしいこと（任意）: この 3 文を「その task の観察中に外部の人・資料を参照した」と読んでよいか。S3 は Table 5 に既出なので追加していない。「S4」の文書への言及は task を特定できないので追加していない。

## 結果（研究者が記入）

- 照合日:
- 一致しなかった行（あれば task と内容）:
- 本文の 3 文の読み（同意 / 異議）:
