# コードブック: 尺度の項目が「何を」「何への」問うか

固定: 2026-10-15。`items.csv` のコード化より先に書いた。区分はユーザーが決めた（decisions.md 判断 2）。変えるときは版を上げ、変えた理由と影響した行を decisions.md に書く。

## 判定の原則

- 判定は**項目の文言だけ**で行う。尺度の著者が付けた因子名は `author_factor` 列に写すだけで、判定には使わない。文言による判定と因子名が食い違う場合は、`mismatch` 列で数える。
- 前置き（教示文・"After video conferencing ..." など）は `context` 列に写す。その項目が何の場面のことかを示すために使う。前置きの内容は第 1 段の型の判定には使わない。
- 1 項目に主の型を 1 つ付ける。2 つの型の間で迷う項目は、`boundary` = 1 にし、もう一方を `secondary_type` に書く。判定の根拠を `rationale` に 1 文で書く。
- 逆転項目は、逆転させる前の文言のまま判定する。

## 第 1 段: 内容の型（`type`）

提案書 v2 §6.1 の M4（回避・苛立ち・無力感・関与の低下が同じ「疲労」の得点に入る）の 4 型に、「その他」を足した。

| コード | 名前 | 判定の基準 | アンカー（例） | 境界の例 |
|---|---|---|---|---|
| `MOT` | 動機・関心・意欲の低下 | 何かをする気・関心・積極性が無い、または減ったことを、そのまま問う | MFI の reduced motivation に由来する ZEF の motivational の項目 "I don't feel like doing anything"・"I dread having to do things"（Fauville et al. 2021 Table 2・S-MR で redmot_2・redmot_4 と照合）。"I've lost interest in ..."・"I have become less proactive in ..." | 疲れを理由にしている（"too tired to do other things"）→ 第 1 候補は `OTH`（疲労）、第 2 候補は `MOT`、`boundary` = 1 |
| `AVO` | 回避・制限・離脱の行動 | 対象を避ける・使う量を減らす・無視する・別の手段を選ぶ、という行動や、行動の傾向を問う | "I avoid using AI even when it could help me."・"I avoid social situations" | 一人でいたい欲求（"want to be alone"）→ `AVO` とし、`boundary` = 1、`secondary_type` = `MOT` |
| `FUT` | 無益感・無力感 | 自分の努力や関心に意味・効果が無い、と感じるかを問う | "... is pointless"・"I doubt whether my efforts ... have any real impact" | — |
| `IRR` | 苛立ち・否定的な感情 | 苛立ち・不満・気分の落ち込みなど、消耗以外の否定的な感情を問う | "frustrated"・"irritated"・"irritable"・"moody" | "discouraged"（落胆）→ `IRR` とし、`boundary` = 1、`secondary_type` = `MOT` |
| `OTH` | その他 | 疲れ・消耗・認知の負荷・理解の困難・身体と感覚の症状・睡眠 | "I feel exhausted"・"My eyes can feel strained ..." | "tired of constantly evaluating ..."（うんざり）→ `OTH` とし、`boundary` = 1、`secondary_type` = `MOT` |

注: 「感情的な消耗」（"emotionally drained"）は消耗なので `OTH` に入れる。`IRR` には入れない。

## 第 2 段: 対象（`target`）

`type` が `MOT`・`AVO`・`FUT` の項目、または `secondary_type` がこの 3 つのどれかである項目に付ける。それ以外は空欄にする。

| コード | 名前 | 例 |
|---|---|---|
| `TASK` | 作業・活動の全般（対象を言わない） | "doing anything"・"having to do things"・"other things" |
| `AI_USE` | AI の利用 | "using AI"・"new AI features" |
| `AI_VERIFY` | AI の情報の真偽の判断 | "assessing the reliability of AI-generated content" |
| `AI_PRIV` | AI のプライバシーの管理 | "protecting personal data"・"privacy settings in AI tools" |
| `SOCIAL` | 人との関わり | "social situations"・"be alone" |

## 列の定義（`items.csv`）

`scale_id, item_no, item_text, context, author_factor, type, secondary_type, boundary, target, mismatch, rationale, source_page, coder`

- `item_text`: 逐語。最終版の質問紙の形で写す（ZEF は Table 3 の質問の形。Table 2 の短い形は `rationale` に添える）。
- `mismatch`: 著者の因子名が動機を名乗っているのに `type` が `MOT` でない場合、または因子名が動機を名乗っていないのに `type` が `MOT` の場合は 1 にする。それ以外は 0。
- `coder`: `claude-prelim`（Claude の予備判定）。ユーザーが AskUserQuestion で境界の項目を決めた行は `claude-prelim+user`。決めた内容は decisions.md に書く。

## 限界（集計にも書く）

- 項目の文言は、得点の成分を示さない。文言が動機を直接問わなくても、得点が動機の低下を映すことはありうる。それを確かめるには、相関や因子のデータが要る。
- 判定者は Claude の予備判定とユーザーの確認だけで、独立した 2 人目はいない。一致は測っていない（2 人目と一致の測り方は研究者の決定待ち）。
