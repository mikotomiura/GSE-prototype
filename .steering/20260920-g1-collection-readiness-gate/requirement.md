# 要件 — G1 収集開始の前提条件 1〜7 に「確かめ方」を与える

- **作成**: 2026-09-20
- **前段**: `.steering/20260920-g1-o1-inventory/`（棚卸し）/ `.steering/_handoff/next-session-g1-preconditions-verification.md`
- **ブランチ**: `feature/g1-collection-readiness-gate`

## 背景（★ すべて 2026-09-20 に一次で実測）

G1 の事前登録は逐語で **「⚠️ 1〜7 が終わるまで新コホートの収集を始めない。」** と宣言している
（`experiments/20260801-controlled-friction-task/preregistration.md:69`）。

⚠️ **ところが、この 7 つを確かめる機械検査はどこにも無い。**

| 場所 | 実測 |
|---|---|
| `experiments/.../run.sh`（432 行） | ★ 自分で「**技術的な準備が整っているかだけを見る**」と宣言（`:7-9`）。`run_cargo_filter` は **`probe_scheduler` と `log_channel` の 2 本だけ**（`:322` / `:352`）。`golden` / `gse-replay` / `parity` は **0 ヒット** |
| `.github/workflows/ci.yml` | ⚠️ **ゴールデンは 6 本あるのに `minimal.ndjson` 1 本しか再生していない**（`:581-582`）。`tests/snapshots/` = 6 ファイル |
| `preregistration.md:80` | ★ 第 19 版が「版が一致していることは前提条件 1〜7 が満たされたことを意味しない」と注記済み |

→ ⚠️ **「`run.sh` が緑だから収集してよい」と読める状態**が残っている。

### ★ 各前提条件の実測（★ 本タスク開始時点の状態。⚠️ 解消は本タスクの仕事ではない）

| # | 前提条件（逐語の所在） | 実体 |
|---|---|---|
| 1 | ADR-013 の実装（`:355`） | ★ **実装済み**。`logger.rs:4246 meta_line_is_byte_identical_when_not_g1` が `app_version`/`capabilities` を出力行ごと固定、`:4084` が `dropped_delta`。⚠️ **`run.sh` が呼んでいない** |
| 2 | G-1 の修正（`:356`） | ★ **実装済み**。`g1.rs` の `g1_restart_while_active_rotates_without_counting` / `restart_is_distinguished_from_meta_retry_by_the_handshake`。⚠️ **`run.sh` が呼んでいない** |
| 3 | 同意文書・guide への追記＋配布済みフォーム突合（`:357-358`） | ⚠️★★★ **未達**。`consent.md` / `participant-guide.md` に `starve_window` も `app_version` も **0 ヒット**（記録項目表は `consent.md §3:40` / `participant-guide.md §6`） |
| 4 | ゴールデン 6 本 byte-equal / schema parity / 両 OS の対（`:359`） | ⚠️ **6 本のうち 1 本しか回っていない**（CI）。手元にも一括で回すものが無い |
| 5 | 課題ページ再生成 ＋ **Drive 差し替え**（`:230-232`） | ⚠️ `build_task_pages.py --selftest` は内部ロジックのみ。生成物 `pages/` は **`.gitignore` 済み**（`.gitignore:151`）。Drive 側の検査資産は **存在しない**（`verify-drive-upload.py` は実在しない） |
| 6 | 記録用紙の「文字数」欄（`:233-234`） | ★ **実体あり**。`record-sheet-confirmatory.md:40` の表見出しに「文字数」。⚠️ 引き継ぎメモは「未確認」と書いていた |
| 7 | 途中でやめた人の数え方（`:47-61`） | ⚠️ **研究者判断待ち**（範囲だけ確定） |

## ゴール

**`scripts/check-g1-collection-readiness.sh` を新設し、前提条件 1〜7 の充足を機械が持つ。**

- Done: `bash scripts/check-g1-collection-readiness.sh --selftest` が **exit 0**（全変異ケースで赤を検出）。
- Done: `bash scripts/check-g1-collection-readiness.sh` が **exit 1**（★ 3 / 5 / 7 が未達なので **今は赤いのが正しい**）で、
  **どれが赤か・なぜ赤かが読める**。
- Stop: 前提条件そのものを満たしに行かない（★ 赤を緑にするのは別タスク・一部は研究者判断）。

## スコープ外（★ やらないこと）

- ⚠️ **事前登録 `§3` の書き換え**（凍結）／前提条件の**文面の変更**（★ 検査を足すだけ）
- ⚠️ **ADR 本文の書き換え**
- ⚠️ **被験者向け文書（`consent.md` / `participant-guide.md`）の変更** — ★ 契約なので研究者へ返す
  （→ 前提条件 3 は **赤のまま残す**）
- 前提条件 **7 の中身を決めること**（研究者判断・別トラック）
- Drive API を叩く検査スクリプトの新規作成（→ 記録票方式に落とす）
- `run.sh` の既存検査の意味の変更

## 運用メモ

- /reimagine 適用: **No**
- 理由: 置き場（A/B/C）と各前提条件の確かめ方は grill で研究者が確定済み（`decisions.md` 判断 1〜4）。
  ★ 残るのは実装設計であり、初回案を破棄して比較する段ではない。
