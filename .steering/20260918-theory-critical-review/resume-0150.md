# 01:50 自動再開の手順（2026-09-19）

> 2026-09-18 23:58 作成。利用上限（94%）で中断する前提で、段 2 を 01:50 から始める。
> ⚠️ このメモは一次資料ではない。判断の一次は `decisions.md` 判断 1、定義の一次は ADR / コード。

## 現在地

- ✅ 段 1 完了: `review-A〜D.md`・`ssot-collision-findings.md`・`citations-audit.md`・`definitions-restop-t1d-t1c.md`・`adr-030-amendment-draft.md`・`survey-plan.md`
- ✅ 研究者判断バッチ 1（18 問）を `decisions.md` 判断 1 に記録
- ⏳ 段 2（サーヴェイ）: **S7 → S8 → S1 → S2**（研究者が 4 つとも選択）＋ **Digital Nature は必要なら補足**（研究者追記）
- ⚠️ 段 1 の成果物は**未コミット**（作業ディレクトリのみ）。段 2 の第 1 ラウンドのコミットの**前に**、段 1 の成果物を 1 コミットにまとめる（明示ファイル指定）

## 段 2 の進め方（1 ラウンド = 1 問い）

1. 各ラウンドは `/literature-review` の手順（RQ 分解 → 複数 angle 探索 → claim 抽出 → 敵対的 3 票検証 → カード → `docs/references.md` へ append → `docs/literature/_index.md` 追記）。
2. ★ **モデル**: WebSearch / 一次資料の読解を行う調査サブエージェントは**調査向けの Opus**（研究者指示）。⚠️ 429（月次上限）が出たら Sonnet へ落として続け、その旨を記録する。機械的照合は Sonnet。Loop での実装は Sonnet。
3. ★ サブエージェントは**並列**、`docs/references.md` への追記は**メインが直列**（memory「Survey via subagent」）。重複キーは DOI / 正規化 URL で検査（⚠️ Horvitz 1999 は既に [P42] が別キーで登録済み —— `citations-audit.md`）。
4. ★ **1 ラウンドごとに即コミット**（memory「Commit each survey round」）。`git add` は明示ファイル指定のみ。`python scripts/check_citations.py` を「違反なし」まで回す。
5. ⚠️ `research-positioning.md` §3 / §4 への**還元は段 3（昇格タスク）へ送る**（J-1 の反映と同時に行うため）。還元案は本ディレクトリに `survey-S*-positioning-draft.md` として置く。
6. ⚠️ `docs/`・ADR・事前登録・実装は、references.md / literature カード / `_index.md` 以外は**変更しない**。

## ラウンドごとの問いと、結果をどこへ返すか

| 順 | ID | 問い | 結果の返し先 |
|---|---|---|---|
| 1 | **S7** | content-free な修正（revision）指標の先行（削除の走り・書き直し・再削除・入れ子・局所反復・R-burst、Conijn et al. 2021 revision detection、Inputlog、S-notation） | `definitions-restop-t1d-t1c.md` §6 を確定案へ更新 → `decisions.md` に判断 2 として記録（⚠️ フィールド名の変更は issue 004 AC1 の改訂なので研究者判断を仰ぐ）→ `issues/004.md` の Background に算出式を転記 |
| 2 | **S8** | 中断後の再開・再停止・P-burst / R-burst の操作化、2 秒閾値以外の区切り | `definitions-restop-t1d-t1c.md` §3-§4 の外的接地を追記 → `issues/006.md` の Background に算出式を転記（J-10 / J-11 は決定済み） |
| 3 | **S1** | ironies of automation・moral crumple zone・take-over request・adjustable autonomy・responsibility gap と「返権の負荷逆説」「権限・負担の二重台帳」 | `review-B.md` B-23 / B-24 の判定を更新。吸収されるなら J-1 / J-2 を研究者に再度伺う |
| 4 | **S2** | 共和主義的非支配・関係的自律・nudge 倫理・contestability と「非支配的協調」 | `review-D.md` §5 の「依拠と差分」を更新 |
| 補 | **DN** | Digital Nature（落合 2018 書籍・関連一次）の射程 —— 局所的な非認定・終端を既に論じているか | ⚠️ **S1 / S2 の後、CORE-CS の比較節（J-6）を書くのに必要と判断した場合だけ**。不要と判断したら理由を `decisions.md` に 1 行 |

## 段 2 の後（このセッションでは着手しない）

- 段 3（SSOT 昇格）の単位を `next-steps` として書き出す: (a) ADR-030 補訂 1、(b) ADR-008 D1 の射程を絞る新 ADR（J-4）、(c) ADR-014 判断 4 を上書きする G1/O1 並行実施の新 ADR（J-5）、(d) RP §1 / §5 H-PA / §8 の改訂（J-1 / J-15）と stale 箇所の一次への是正、(e) glossary（返権・Semantic Stop・二重台帳・再開 / 再停止）、(f) EVAL-NCC 契約の既存トラックへの接続し直し（J-13）
- タスク 2 の再開順（判断 25）の先頭は「Loop 基盤の修正」。issue 004 / 006 は S7 / S8 の定義転記後。
