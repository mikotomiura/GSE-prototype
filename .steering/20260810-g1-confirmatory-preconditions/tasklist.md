# タスクリスト

## 準備

- [x] P010 が前提 3 点を満たしていないことを実測で確認
- [x] ★ `analyze.py` が `confirmatory` を一度も見ていない / glob が `PILOT-*` を拾うことを確認
- [x] grill で 4 分岐を確定（`decisions.md` D-1〜D-5）

## 実装

- [x] `config.json`: `sample_roster` 新設（confirmatory=[] / pilot / shakedown=["P010"]）
- [x] `config.json`: `design.n_subjects` を **3** で凍結
- [x] `config.json`: `status` を実態に合わせる / `revision` を 15 へ（`v15_changes` に非対称性）
- [x] `analyze.py`: roster を読み `confirmatory` だけを解析対象にする
- [x] `analyze.py`: ⚠️ 境界 5 種を fail-loud に（空 / 未登録 / 欠員 / キー無し / n 未達）
- [x] `analyze.py`: 結果に `sample_roster_applied` を刻む
- [x] `analyze.py`: `PREREG_REVISION` を 15 へ

## テスト

- [x] `analyze.py --selftest` に roster ケース（★ 対照で切り替わることを固定）
- [x] `analyze.py --selftest` に境界 5 種
- [x] `validate_blocks.py --selftest` が無変更のまま緑（回帰していない）
- [x] ★ 実データ: P010 が確証解析に入らない（⚠️ 判定は出さない）
- [x] ⚠️★ **壊して赤を見る**: roster の P010 を confirmatory に移すと入る
- [x] `bash run.sh` が GREEN

## レビュー

- [x] `/cross-review`（Claude ∥ Codex）
- [x] ★ 研究の妥当性を重点的に見てもらう（n=3 の根拠 / shakedown 条項 / 非対称性の書き方）

## ドキュメント

- [x] `preregistration.md` 第 15 版: `§2.8` shakedown 条項
- [x] `preregistration.md`: 実施条件に研究者承認での開始とリスクを追記（D-4）
- [x] `preregistration.md`: `§2.4` に n=3 凍結と `§2.4-4/5/6` の再宣言
- [x] ⚠️ 改訂履歴に「本改訂は **P010 取得後**・いかなる解析より前」を明記
- [x] `notes.md`: n 凍結の日付と**コミットハッシュ `d3caebd`**（§2.4-1 手続き 3・2 箇所）
- [x] `data.md` 冒頭の訂正（★ `results/` が空なのは今も真）

## 完了処理

- [x] `/finish-task`（schema parity は非 touch で skip）
- [ ] コミット → push → PR → merge

## ★ 本タスクの後にやること（別タスク）

- ⚠️ **P010 のフォーム回収**: `produced_chars` 10 件 / 操作チェック 7 件。
  ★ これが無いと P010 は shakedown としても中身を検証できない
- ⚠️ 記録用紙と `blocks/P010.json` の `file` 列の突き合わせ（`notes.md §10-5`）
- ⚠️ `gse-app.log` の回収（版の特定 / block07 で参加者が何を見たか）
- ★ `meta` 行にアプリ版を刻む（次に配布物を作るときに同梱）
- ⚠️ Phase1 GATE3 の決着（別トラック）
- **確証標本 3 名の募集と日程調整**（★ 配布物は現行のまま使える）
