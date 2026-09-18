# タスクリスト

## 分解（★ 本セッション・2026-09-14・Opus）
- [x] `docs/adr/ADR-030` D2 / D3 / D4 / D5 / D6 / D10 / D11 を一次で読む
- [x] `docs/adr/ADR-032` D5 / §Migration M7 を一次で読む
- [x] `.idea/…-survey` §6.1 / §6.3 / §11 を一次で読む
- [x] grill（★ 判断分岐 6 件を閉じた → `decisions.md`）
- [x] ベースライン実測（test / check / clippy / golden / schema parity すべて exit 0）
- [x] `issues/001`〜`007` ＋ 各 `acceptance.sh`
- [x] `_loop-config.json`（★ `base_branch` を作業ブランチに pin・`parallel: 1`）
- [x] `_issue-plan.md`（★ DAG / 交差表 / 自己検査）
- [x] `docs/glossary.md` に確定用語 3 件
- [x] `--dry-run` で config / DAG / acceptance の検出を確認（★ 7 本とも `acceptance=yes`）

## ⚠️ 分解セッションはここで終わる
- [x] `/clear` する
- [x] **新セッション**で `bash scripts/loop-run.sh .steering/20260914-mhd-feature-offline-tiers --issues 001`
      （★ 最も安い 1 本で基盤を検証する）
- [x] 001 が緑なら残りを回す（★ 001 は Loop 外で仕上げた・判断 8）

## 実行（★ 別セッション）
- [x] 001 `--features` ＋ `T0`（★ commit `061e6fb`）
- [x] 002 `T1b`（境界）（★ commit `284c754` → merge `a4400b9` ＋ レビュー修正。⚠️ Loop は `abandoned`・原因は検査バグ＝判断 13）
- [x] 003 `T1a`（分布）（★ commit `1440524` → merge `46f98ff` ＋ レビュー修正。⚠️ 起票 7 が開いたまま＝分位点が構造的に退化）
- [!] 004 `T1c`（revision topology）★ **保留** —— ⚠️ rewrite / redelete / loop_depth / local_recurrence の**演算的定義が存在しない**（★ .idea/survey も候補名の一覧だけ）。→ 起票 9 / 判断 17。★ 研究者の定義確定待ち
- [x] 005 `stall onset`（★ 判断 11 で `parse` へ）（★ commit `134c9e2` → merge `da1b8b2`。⚠️ **レビューを通さずに merge されていた** → 2026-09-18 に客観検証 ＋ レビュー 2 本 → ⚠️★★★ **削除区間に onset が立つ**（HIGH・実測）ほか → 判断 18）
- [x] ★ 008 `stall onset` の是正（観測区間 = D8 (b-2)・末尾の沈黙・`task_kind`・O(N log N)・検出力）（★ Loop attempt 4 → レビュー 2 本 → 是正 `9e5d0fa` → merge `2b417c1`。判断 18 / 22）
- [!] 006 `T1d`（restart）★ **保留**（2026-09-18）—— ⚠️ 算出式が一次資料に無く、「再停止」は ADR-031 の転帰側の語。→ 起票 17 / 判断 20。★ 研究者の定義確定待ち
- [x] ★ Loop 基盤: worker へのプロンプト `/loop-issue` が MSYS のパス変換で壊れていた（★ 003〜008 の全 attempt）→ commit `446fa3b` で修正（判断 19）
- [ ] 007 `Q`（evidence quality・★ 判断 11 で `parse` へ）

## Loop 外（★ 対話で行う・研究者判断 2026-09-14）
- [ ] `capability matrix`（ADR-032 **M7**）—— ⚠️ `OS × ライブ変換設定` で層別。
      ★ 範囲は `decisions.md` 判断 5（schema 静的分析 ＋ 既存 fixture ＋ 起票 6 の既測結果）
- [ ] ⚠️ matrix の結果で **ADR-032 の未決 ④ / ⑤ と起票 21（単独キー用の門）** を閉じる

## 完了処理
- [ ] 全緑後: `code-reviewer` + `security-checker` 並列 ＋ `/cross-review`（2 巡）
- [ ] `_loop-retrospective.md`
- [ ] main へのマージは研究者判断
