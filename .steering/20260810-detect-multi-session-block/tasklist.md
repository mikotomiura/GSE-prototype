# タスクリスト

## 準備

- [x] P010 の復号・検証（`notes.md §10`）
- [x] 原因側をコードで裏取り（`lib.rs:1973` / `:2019` / `App.tsx:478` / `tray.rs:65`）
- [x] スコープと規則の位置づけを確定（`decisions.md` D-1〜D-5）

## 実装

- [x] `validate_blocks.py`: `session_start` ≥ 2 → FAIL
- [x] `validate_blocks.py`: `alive=false` + key>0 の WARN 文面を、測った量を出す形に修正
- [x] `analyze.py`: `read_block` が `n_session_starts` を返す（★ ここでは止めない）
- [x] `analyze.py`: `read_block(..., from_last_session=True)` で最終セッションだけ読む
- [x] `analyze.py`: `load_subject_blocks` が既定で `SystemExit`
- [x] `analyze.py`: `--last-session-on-restart` + 結果への `restart_handling` 刻印
- [x] `analyze.py`: `--verify-blocks` は再開始を表示して **0 を返す**（契約を変えない）

## テスト

- [x] `validate_blocks.py --selftest` に 2 ケース（2 セッション赤 / ★ 1 セッション緑の対照）
- [x] `analyze.py --selftest` に 3 ケース（フラグ無し止まる / 有り通る / ★ 1 セッションは不変）
- [x] ★ P010 実データで `validate_blocks.py --dataset` が block07 を FAIL
- [x] ★ P010 実データで `analyze.py` がフラグ無しで止まり、有りで 1387 打鍵 / 4:44
- [x] ⚠️★ **壊して赤を見る**（新検査を無効化したら 3・4 が緑に戻ることを確認）

## レビュー

- [x] レビュー（★ セッション制約でサブエージェント単独起動は不可 → `/cross-review` の
      cross-reviewer が Claude 側の通読＋実測クロスチェックを兼ねた。自己レビューで 3 件修正）
- [x] ✅ `/cross-review` 実施（Codex 36,888 tokens）。★ Codex のみの MEDIUM 1 件が**本物の穴**
      （2 つの数え方のずれ）→ 自分で再現して修正。記録は `notes.md §10-9`

## ドキュメント

- [x] `preregistration.md` に規則を凍結（★ 改訂履歴に「結果を見る前に決めた」を残す）
- [x] `notes.md §10-4` の「提案」を「実装した」に更新
- [ ] ⚠️ `data.md` 冒頭「**本実験は未実施**」が P010 の実施で事実でなくなっている
      → ★ 確証ステータスの書き方は研究者判断なので、**別途確認してから**直す

## 完了処理

- [ ] `/finish-task`
- [ ] コミット（`test` or `fix` scope=analysis）

## ★ 積み残し（本タスクでは触らない）

- ⚠️ `lib.rs:1973` のローテート意味論（押し直し = 新ファイル）— D-1 で却下、後日枠
- ⚠️ `lib.rs:2001` `let _ = try_send(SessionStart)` の fail-loud — 引き継ぎ §7
- ⚠️★ `meta` 行にアプリ版を刻む — 「どの版で実施したか」が今回**答えられなかった**原因
- ⚠️ 記録用紙と `blocks/P010.json` の `file` 列の突き合わせ（`notes.md §10-5`）
- ⚠️ P010 block07 で参加者が画面に何を見たか（本人に確認）／`gse-app.log` の回収
