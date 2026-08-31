# タスクリスト

## 調査 (一次資料)

- [x] O1 の修正済み実装を読む (`Form_O1/GSE_O1_Form_Builder.gs:940-1071, 1531`)
- [x] G1 の未修正箇所を特定 (`:1775` / `:1789-1807` / `:1858` / `:3393`)
- [x] ⚠️ `LockService` がスクリプトプロジェクト単位である事実を確認 (→ T-27 は防げない)
- [x] テスト基盤の型を確認 (`Form_G1/guard_test.cjs` / `Form_O1/o1_form_builder_test.cjs`)
- [x] `run.sh` の配線方法と `guard_count` の書式を確認

## 実装

- [x] `g1NextParticipantId_`: `last > 1` → `last >= 1` (起票 E-3)
- [x] `g1FindInPhase1Roster_`: メール優先 ＋ `conflict` 返却 (起票 E-2)
- [x] `g1IsValidPid_` を新設
- [x] `g1WithRosterLock_` を新設し、`assignG1ParticipantId` を包む
- [x] `onG1ConsentSubmit` の手書きロックを `g1WithRosterLock_` に寄せる
- [x] `conflict` 分岐: **発番も受付メールも行わない**
- [x] `g1RecordRosterConflict_`: `⚠要確認` 行に出す (★ 他人の行を汚さない)
- [x] `g1CountPidRows_`: 採番直後の重複検知 (起票 T-27 の緩和)

## 検証 (すべて実走)

- [x] `Form_G1/g1_roster_test.cjs` を新設 — **29 ケース / 失敗 0**
- [x] ★ **変異注入 5 件すべてを捕捉** (M1〜M5)。無変異は緑
- [x] ★ **`run.sh` の配線の陽性対照** — 変異を入れると `rc=1` / `[FAIL]`
- [x] ⚠️ 完了行の書式を直して「件数不明」→ **29 ケース**と出るようにした
- [x] 空回りの番兵 (`pass < 25` で赤) を入れた
- [x] `run.sh` 全体 — **[GREEN] 全項目通過**
- [x] 既存 G1 テスト 4 本すべて rc=0 (退行なし)
- [x] ⚠️ **O1 側にも退行が無い**ことを確認 (`o1_form_builder_test` / `o1_submit_guard_test` rc=0)
- [x] ⚠️ 秘密・実 ID を新たに増やしていない (差分は 2 ファイル ＋ 新規テスト)
- [ ] ⚠️ `code-reviewer` ＋ `security-checker` の並列レビュー
- [ ] ⚠️ `/cross-review` (Codex)
- [ ] ⚠️ CI が緑になること (★ push するまで分からない)

## ⚠️ やっていないこと (★ 明示する)

- [ ] ⚠️★★★ **実 Google フォーム / 実 Apps Script への配備** —— ブラウザ作業で研究者の手番。
      ★ **配備しない限り実フォームの挙動は 1 ミリも変わらない。**
      ⚠️ `.steering/20260819-g1-reboot-and-instrument-fix/blockers.md:25` の **D-5 と同じ型**
      (repo は直したが実物に反映していない) なので、⚠️ **同じ轍を踏まないこと**。
- [ ] ⚠️ 実シート・実メールでの動作確認 — スタブのみ。★ 触っていない
- [ ] ⚠️ **T-27 の排他そのもの** — 別タスク (`/reimagine` を掛けるべき規模)
- [ ] ⚠️ T-21 (実ロスター ID の直書き) / T-15・T-16 (実 Drive ID) — 別トラック
- [ ] ⚠️ G1 の Windows launcher (T-3) / フック liveness の実機検証 — この Mac では不可
