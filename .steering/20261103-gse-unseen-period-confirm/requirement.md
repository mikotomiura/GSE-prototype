# O1 の見ていない期間で H4a・H5 を確かめ、C1・C2・C6 の読みを並べる条件（計算の前のコミット）

## 背景

- `.steering/_handoff/next-session-gse-after-stage1-adr-prereg.md` §3 の候補 1。研究者が選んだ（2026-11-03）。
- synthesis（`.steering/20261102-gse-synthesis-redesign/synthesis.md` §5）で、今の計器で確かめられる仮説は H4a（日の揺れ）と H5（作業の後ろほど停滞が多い）だけ。O1 の 11-01 08:30 開始の本以降は、停滞の分解と C1・C2・C6 の記述で開けずに取ってある（`experiments/20261103-stall-candidates-c1c2c6/data.md`）。
- 2026-11-03 の時点で O1 はまだ記録中（11-02 08:30 開始の本が更新中・アプリが稼働中）。閉じているのは 11-01 08:30 の 1 本だけ。

## ゴール

確かめの条件（使うファイルの範囲・H4a と H5 の支持／反証／決まらないの式・C1・C2・C6 で並べる量）とコードを、見ていない記録を開く前にコミットする。実データの計算は O1 の終了後に 1 回だけ行う（このタスクでは行わない）。

## スコープ

### 含むもの
- `experiments/20261103-o1-unseen-confirm/` の条件・データ・環境の文、`confirm.py`（陽性対照と変異の確かめつき）、`run.sh`（O1 の稼働中は止まる）。
- 判断の記録（`decisions.md`）。

### 含まないもの
- 見ていない記録（11-01 08:30 開始の本以降）とその中間を開くこと。
- R1〜R5 の O1 側の確かめ（判断 1）。
- C4・H1〜H3・H4b。公開データの書き手（`holdout.json`）。
- ADR・事前登録（`docs/preregistration-stage1.md`）の変更。

## 受け入れ条件

- [ ] `python3 -I confirm.py --selftest` が緑で、判定の要の行を壊した変異で赤になる。
- [ ] `run.sh` が O1 の稼働中に止まる（今の状態で実際に止まることを確かめる）。
- [ ] 条件とコードが、見ていない記録を開く前にコミットされている。
- [ ] code-reviewer と /cross-review をかけ、指摘を直すか理由を書く。

## 関連ドキュメント

- `.steering/20261102-gse-synthesis-redesign/synthesis.md` §5（H4a・H5）・§2（R5）
- `experiments/20261103-stall-candidates-c1c2c6/`（C0〜C6 の検出器と 14 日の記述）
- `experiments/20261102-stall-decomposition/`（中間の作り方・まとまり・`unit_sd`）
- `experiments/20261103-mhd-dryrun-v2/notes.md`（区間の作り方の空回し）

## 運用メモ
- /reimagine 適用: No
- 理由: 実装の形は既存の検出器の再利用で決まり、判定の式は研究者が 1 問ずつ選んだ（判断 1〜4）。
