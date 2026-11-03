# 引き継ぎ —— O1 の終了後に、見ていない期間で H4a・H5 を確かめる計算を回す

> 作成: 2026-11-03（`.steering/20261103-gse-unseen-period-confirm/` の後）。
> このメモを一次資料にしない。条件は `experiments/20261103-o1-unseen-confirm/conditions.md`、判断は同じ steering の `decisions.md` 判断 0〜8。

## 0 入口の文

「`.steering/_handoff/next-session-gse-unseen-period-run.md` を実施。O1 が終わったので、見ていない期間の確かめを 1 回だけ回して notes を書く」

## 1 状態

- 条件とコードはコミット済み（8b0e7c9b・a184f4d8・branch docs/gse-unseen-period-confirm）。見ていない記録（`20261101_083030` 以上）はまだ誰も開いていない。
- 2026-11-03 の時点で O1 は記録中。run.sh は O1 の稼働中・10 分以内の更新・2 回目・入力の違い・未コミットで止まる（すべて実際に止まることを確かめた）。

## 2 手順

1. 研究者が O1 を終える（アプリを終了する）。終えたことを研究者に確かめる。
2. 研究者の Mac で、branch を main に入れた後（または worktree `/Users/johnd/GSE-prototype-unseen-confirm` で）`bash experiments/20261103-o1-unseen-confirm/run.sh`。陽性対照と変異 40 種（数分）の後に中間を作り、`results/confirm.json`・`started.json`・`provenance.json` を書く。
3. 判定に使うのは最初の 1 回だけ。途中で環境の理由で落ちたら、同じ入力のときだけ再実行できる（判断 8）。日を足して回し直さない。
4. `notes.md` を書く: H4a（C0 の判定・主と副の読み・温まりを含めた値・C1・C2 の記述）、H5（C0 の判定・3 等分・C1・C2）、U4 の a〜f。U6 の言える範囲を守る。結果の集計値だけを repo に入れる（時刻・ファイル名・日付を出さない）。
5. code-reviewer と /cross-review（Codex に送るのは notes・コードだけ。結果の JSON も送らない方が安全）。

## 3 注意

- 結果を見た後に条件を変えない。変えたくなったら逸脱として notes に書き、判定は条件のまま出す。
- 「作業上の認知状態」「停滞」と書く。詰まりを検出したとは書かない。
- H4a の支持は H4b（日を効果の単位にできるか）の判定ではない。
