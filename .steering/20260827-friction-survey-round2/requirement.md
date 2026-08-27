# requirement — 摩擦操作サーヴェイ 第 2 ラウンド

## 背景

2026-08-27 に G1 の判定が `MANIPULATION_CHECK_FAILED` で止まり、第 1 ラウンドの文献サーヴェイが
**(a) 課題文を直す / (b) 操作を再設計 / (c) 測り方を変える** を判定して **de-risk 先行**とした
（`docs/literature/20260827-friction-manipulation-direction-and-manipulation-checks.md`）。

★ 本タスクはその第 1 ラウンドが残した**やり残し 7 件**を一次資料で潰すサーヴェイ 1 ラウンドである。
入口は `.steering/_handoff/next-session-prompt-friction-survey-round2.md`。

## ゴール

`/literature-review` の完了条件を満たすこと:

1. `docs/literature/<YYYYMMDD>-<slug>.md` を生成する
2. `docs/references.md` に **append-only** 登録する（採番は末尾の次番号 = P135 / V88 から）
3. `docs/literature/_index.md` に 1 行追記する
4. `docs/research-positioning.md` への還元（または「還元不要」）を明示する
5. **gate 用途なので go / no-go / de-risk 先行 を明言する**

## 受け入れ条件

- [x] 下位問い R1–R4 に分解し、**探索前に gate 基準を凍結**した（handoff §2 をそのまま使用）
- [x] 反証 angle を 1 つ以上含めた（★ 専任 subagent を 1 つ立てた）
- [x] 各 claim を **3 票の敵対的検証**にかけた（視点を変える・1 agent に 3 票を書かせない）
- [x] `判定不能` を「弱い支持」に丸めていない
- [x] 否決リストを残した
- [x] `python3 scripts/check_citations.py` が **違反なし**
- [x] 一次全文に到達したかどうかを**ソースごとに明記**した（★ 前ラウンドは 7 件中 1 件しか到達していなかった）

## ⚠️ 本タスクで扱わないもの（handoff §9）

- 課題文の書き直し / `preregistration.md` の改訂（★ 研究者の行為）
- O1 の実装（★ 別セッション・G-GEAR 側の担当）
- `replay.rs` の flaky test
- `validate_blocks.py` の既存 17 件 FAIL
- ⚠️★★★ `analyze.py --unseal`（★ 押すと `confirmatory_status_forfeited=true` が刻まれる）
