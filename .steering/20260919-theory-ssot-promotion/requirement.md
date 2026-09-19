# 理論レビューの SSOT 昇格（段 3）—— 親タスク

> 起点: `.steering/_handoff/next-session-theory-ssot-promotion.md`（⚠️ 一次資料ではない）。
> 判断の一次は前段 `.steering/20260918-theory-critical-review/decisions.md`（判断 1〜4）と、本タスクの `decisions.md`（判断 1 = 研究者判断バッチ 3）。
> ★ 本ディレクトリは**段 3 全体の親**である。作業単位 a〜i は 1 単位 = 1 タスク（`.steering/20260919-ssot-<単位>-…/`）として個別に `/start-task` し、ここには段全体の判断と進行だけを置く。

## 背景

- 前段（`20260918-theory-critical-review`）で、pre-SSOT の理論草案（`.idea/` の A / B / C）と評価契約群（D）の批判的レビュー（段 1）とサーヴェイ 5 ラウンド（段 2）が終わった。
- 研究者判断バッチ 1（18 問）・バッチ 2（8 問）で、SSOT（ADR・RP・glossary・評価契約）へ上げる中身が決まった。まだ `docs/` には 1 行も入っていない。
- 別トラックの規約（`20260916-gse-theory-operationalization-review/requirement.md`）は「Claude Code との批判的検討と人間による採否判断を経るまで SSOT へ上げない」と定める。→ ★ 本タスクはその「上げる」段である。

## ゴール

- 引き継ぎ §2 の作業単位 a〜i を §3 の順に、1 単位ずつ `/start-task` → 反映 → `/cross-review` 2 巡 → コミットで SSOT へ上げる。
- 体系的レビュー（前段 判断 2 #2）を、RP §4 に差分を書く前に行う（範囲・検索元・時期は本タスク 判断 1）。
- 研究者判断が要る箇所は推測で埋めず、AskUserQuestion でまとめて聞く。実装の設計（issue 004 の U1〜U4 / 006 の V1〜V5）は聞かずに実装フェーズへ回す（前段 判断 3）。

## スコープ

### 含むもの
- ADR-030 補訂 1（項目 6 を除く）・新 ADR（非再捕捉の射程 / G1・O1 の並行実施 / 招待の出し方の選択 ＝ 検討）
- `docs/research-positioning.md`・`docs/glossary.md` の改訂
- 評価契約群（`.steering/20260916-gse-theory-operationalization-review/`）の改訂
- 理論本体を `docs/theory/` へ移して版管理し、改訂する（本タスク 判断 1 #4）
- 体系的レビュー（RP §4 の差分候補だけ・本タスク 判断 1 #5〜#7）

### 含まないもの
- ⚠️ ADR-030 補訂の項目 6（E1）—— 実装フェーズで issue 006 の V1 を裁定した後に書き直す（前段 判断 3）
- ⚠️ 実装（Rust / TS）・issue 004 / 006 の実装・Loop 基盤の修正（タスク 2 の実装フェーズ）
- ⚠️ `docs/preregistration-v0.3.md` の書き換え（凍結済み）
- ⚠️ ADR 本文の書き換え（補訂節・新 ADR で上書きする）
- ⚠️ 被験者向け文書（`docs/participant-setup-guide.md`・同意文書）の変更 —— 必要が出たら研究者へ返す（被験者向け文書は契約）
- PM-Q7（復帰後の差分を表現へ結合するか）の裁定（前段 判断 1 #4）
- S3〜S6b のサーヴェイ（★ S3 は理論名の確定に要る → 別ラウンド。本タスク 判断 1 #3）

## 受け入れ条件

- [ ] 単位 a〜i がそれぞれ個別のタスクディレクトリを持ち、`/cross-review` 2 巡の記録とコミットがある（i は「起票しない」結論でもよい）
- [ ] 研究者判断を推測で埋めていない（本タスク `decisions.md`・各単位の `decisions.md`）
- [ ] 「先行研究が存在しない」と書いていない（書けるのは「今回の範囲で見つからなかった（ラウンド名・日付）」まで）
- [ ] ADR 本文・事前登録を書き換えていない
- [ ] `python scripts/check_citations.py` が「違反なし」まで回っている
- [ ] 禁止用語（`docs/glossary.md` の表・ADR-030 の却下リスト）を新しい文書にも当てている（`check_doc_lexicon.py` は固定の 7 本しか見ない）

## 関連ドキュメント

- `.steering/_handoff/next-session-theory-ssot-promotion.md`
- `.steering/20260918-theory-critical-review/`（`decisions.md`・`review-A〜D.md`・`adr-030-amendment-draft.md`・`positioning-reduction-draft.md`・`definitions-restop-t1d-t1c.md`・`ssot-collision-findings.md`）
- `docs/literature/20260919-*.md`・`docs/references.md`
- `docs/adr/README.md`（ADR の書き換え禁止規約）

## 運用メモ

- /reimagine 適用: **単位ごとに判断する**（前段 判断 1 #18「段 3 の昇格タスクで必要なら行う」）
- 理由: 単位 a〜h は研究者が既に裁定した中身を SSOT へ書き写す作業であり、複数案の比較が要らない。単位 i（起票するかどうかの検討）は各単位の `requirement.md` で改めて判断する
- モデル: 設計判断・ADR の起草は Opus（メイン）。機械的な置換は Sonnet のサブエージェント
