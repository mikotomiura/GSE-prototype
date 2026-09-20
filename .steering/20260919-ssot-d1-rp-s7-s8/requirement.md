# 単位 d-1: research-positioning への S7 / S8 の還元

> 親タスク: `.steering/20260919-theory-ssot-promotion/`（段 3）。引き継ぎ §2 の単位 **d** のうち、J-1 に依存しない S7 / S8 の部分（引き継ぎ §3-1・還元案 §3 の 2）。

## 背景

- 段 2 のサーヴェイ S7（content-free な修正の指標）と S8（再開・再停止・burst の区切り方）の結果を、`docs/research-positioning.md`（RP）へ還元する案が `.steering/20260918-theory-critical-review/positioning-reduction-draft.md` にある。
- S7 / S8 は理論（J-1）に依存しないので、J-1 と別のコミットで先に入れてよい（還元案 §3 の 2）。

## ゴール

- RP §3 の 2 段落（判別子に「修正（revisions）」を挙げる段落・沈黙の中身の段落）と §8 の段別表 T1 行に、還元案どおりの注記を足す。
- 反証は主張を下げる方向で還元する（`/literature-review` Step 8）。主張を上げる還元はしない。

## スコープ

### 含むもの
- `docs/research-positioning.md` の §3 の 2 段落と §8 の段別表の直後への追記

### 含まないもの
- ⚠️ 段別表の行そのものの書き換え（2026-08-16 の研究者決定）
- ⚠️ S1 / S2 / DN の還元・§1 / §4 の改訂（単位 d-2 / d-3）
- ⚠️ 事前登録（凍結済み）

## 受け入れ条件

- [ ] 還元案の S7 行・S8 行 2 つの要点がすべて入っている
- [ ] 「先行研究が存在しない」型の断定が無い（「今回の範囲（S7 / S8・2026-09-19）で 0 件」まで）
- [ ] 2-1 の claim・メイン未照合の claim に留保が付いている
- [ ] `check_citations.py` 違反なし
- [ ] `/cross-review` 2 巡

## 関連ドキュメント

- `.steering/20260918-theory-critical-review/positioning-reduction-draft.md` §1（S7 / S8 行）・§2
- `docs/literature/20260919-content-free-revision-measures.md`・`docs/literature/20260919-resumption-restop-and-bout-segmentation.md`
- `docs/adr/ADR-030-stall-onset-and-decision-episode.md` 補訂 1（単位 a）

## 運用メモ

- /reimagine 適用: **No**
- 理由: 還元の中身はサーヴェイのカードと還元案で決まっている。書き写す作業である
