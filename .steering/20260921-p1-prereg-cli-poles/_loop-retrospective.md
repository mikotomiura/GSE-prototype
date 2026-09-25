# Loop 振り返り — P1 前: 事前宣言文書 ＋ CLI 注入 ＋ 両極（2026-09-25 実行セッション）

> ★ 一次は `decisions.md` 判断 17〜29 と起票 P1-A〜K、各 `issues/00X.md` の Status / Execution Result、`_loop-events.jsonl`（gitignore）。
> ⚠️ 本書は要約であり、一次の代わりにしない。

## 1. 結果

| issue | 中身 | Loop の終わり方 | 自力完走 | merge |
|---|---|---|---|---|
| 001 | 凍結値の CLI 注入 ＋ θ の標本数 | 1 回目: 分解漏れで 6 attempt 空回り → 2 回目: verify 緑・watchdog 空応答で blocked | ✗ | `f5163a6` |
| 002 | 削除の最小幅 | acceptance の `--exact` 欠陥で blocked（attempt 2） | ✗ | `01d90f2` |
| 003 | `T1a` 30 秒窓 | 同上（attempt 2） | ✗ | `dde07ee` |
| 004 | 極の器 | **attempt 1 で issue_done** | ✓ | `5c6cc4b` |
| 005 | 極 M+ | attempt 1 で issue_done（⚠️ max_turns・**未コミット**） | △ | `ac812fa` |
| 006 | 極 B | 1 回目: 古い origin から切られ blocked → 2 回目: attempt 4 で issue_done | △ | `f1305f0` |
| 007 | `ime_overlap` | acceptance の jq 欠陥で 5 attempt 赤 → blocked | ✗ | `822fd2a` |
| 008 | 計算量の門 ＋ 3 極スクリプト | 1 回目: 並列 spawn の config ロック競合 → 2 回目: issue_done（⚠️ 未コミット） | △ | `ddc3172` |
| 009 | ADR-030 補訂 2 | **attempt 1 で issue_done** | ✓ | `1739b5c9` |

★ 前半（001〜004）は PR #222 で main へ merge 済み（CI 緑）。

## 2. ⚠️ 自力で完走しなかった原因の内訳（★ 実装の失敗は 0 件）

| 原因の層 | 件数 | 例 |
|---|---|---|
| **分解（issue / acceptance の作り）** | 6 | `restart.rs` の Allowed Files 漏れ（001・判断 17）／ 依存の太字が黙って落ちる（P1-D）／ acceptance の `--exact`（002・003・005〜007）／ jq の配列欠陥（001・007）／ 他 issue の完全一致の門を壊す（001・004・005・判断 22）／ 変数展開の bash 3.2 誤読 |
| **Loop 基盤** | 5 | worker の blocked を見ず空回り（`cc4d4fe` で是正）／ watchdog の空応答（判断 21）／ コミット無しで issue_done（P1-I）／ 古い origin から worktree（P1-J）／ 並列 spawn のロック競合（P1-K） |
| **権限設定** | 常時 | worker が `bash <acceptance>` を実行できない（P1-B）→ acceptance の欠陥を worker が自己検証できず、Loop の verify でしか分からない |

★ **教訓**: ⚠️ 失敗のほとんどは **分解の側**にあった。★ acceptance は「実 fixture ＋ 実装で通しで回すまで未検証」（memory `feedback_acceptance_self_test`）—— 分解の時点では実装が無いので回せず、**Loop の最初の実行が acceptance の最初の実行になる**。→ ★ 次回の分解では、少なくとも **acceptance の「テスト名の照合」「jq の型」を 1 本の既存テスト / 既存出力で試してから**確定する。

## 3. ★ メインの独立検証が唯一の網だった

- ⚠️ Loop の verify は **issue 自身の acceptance しか回さない**。→ 他の門（`envelope-acceptance.sh` ほか旧タスクの完全一致）の破損は、**メインが新旧すべての acceptance を回した時にだけ**見つかった（001 / 004 / 005）。
- ⚠️ メインの検証スクリプト自体にも欠陥があった（`echo "$(…)=$?"` で終了コードが常に 0）。★ **わざと落ちるスクリプトで非 0 を拾う**ことを確かめてから使う形に直した（`decisions.md` ウェーブ 2 の記録）。

## 4. ★ レビューの効果

- **Claude 系統**（`code-reviewer` ＋ `security-checker`・issue ごと）: 研究上の主張に関わる HIGH を 3 件（M+ の自動リピート〔判断 23〕・極 B の向き〔判断 25〕・D4 #2 の上書きの誤記）。
- **Codex 系統**（`/cross-review`・gpt-6-astra）: ⚠️ Claude 系統が見落とした穴を拾った —— **判断 23 の look-ahead と孤立 release**（→ 判断 27 で B へ改めた）・M+ の上位集合（判断 28）・IME の「下限」の矛盾（判断 29）。
  ★ 判断 23 は**メインが推奨した案**であり、独立系統のレビューがそれを覆した。

## 5. 未是正の起票（★ 次のタスクへ）

P1-A（凍結既定で restart の非退化検査が走らない）／ P1-B（worker が bash を実行できない）／ P1-C（issue サイズ基準の超過）／ P1-D（依存パーサーが太字を落とす）／ P1-F（`--set q` が `warmup_count` を連動しない）／ P1-G（`--feature-config` の id / version 未検証）／ P1-H（Loop の verify に全 acceptance の回帰を入れる設計）／ P1-I（コミット無しの issue_done）／ P1-J（古い origin から worktree）／ P1-K（並列 spawn のロック競合）／ 凍結文書の出力表に `ime_overlap` が無い（新版を切るかは研究者判断）。
