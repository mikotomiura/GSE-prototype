# 引き継ぎ — 公開データの当てはめ 項目 2（KLiCKe・Kaggle）: 作文中の値の分布と誤発火の基準

> 作成: 2026-11-01（項目 1 と案 A の後・研究者の指示で新しいセッションから始める）。
> このメモを一次資料にしない。事実は一次（`experiments/*/notes.md`・`decisions.md`・データのページ・コード）で確かめ直す。
> 元の計画は `next-session-gse-public-data-fit.md`（項目 1〜7 の表）。

## 0 ここまでの結果（一次は各 notes.md）

1. 項目 1（`experiments/20261031-coauthor-pre-request-signal/`・`.steering/20261031-gse-public-data-fit-ai-request/`）
   - CoAuthor [V348]（英語の共同執筆・MTurk・Tab で AI の提案を要求）。本文を捨てて GSE の NDJSON にし、`gse-replay` を通した。
   - 1 回目: AI の要求の手前の `p_stuck`・`ewma_x` は対照より詰まり側でなかった（AUC 0.42・0.45・逆向き）。要求の多くは語・文の区切りの直後で、直前の休止は中央値 0.65 秒（探索）。
   - 2 回目（本人の揺れ＋層別）: 休止 2 秒以上の要求でも、30 秒の上がりは見えない（0.517・0.502・書き手 38）。
2. 案 A（`experiments/20261101-coauthor-pre-stall-signal/`・`.steering/20261101-gse-pre-stall-signal/`）
   - 本人の分布で立てた停滞の始まり（ADR-030）を正解の時刻にし、停滞の前の最後の文字の入力で比べた。30 秒の上がりは見えない（0.503・0.493・書き手 28）。推定を通さない打鍵の量でも 0.5 の周り（探索）。
   - 研究者が判断する材料: 打鍵のリズムの上がりで「詰まる前」を先回りする前提は、このデータでは支持されない。打鍵で確実に見えるのは止まりそのもの。招待の契機を「止まりの初期」（本人の θ に届く前）に置く・打鍵の外のチャネル（フォーカスの遷移）を足す、が候補（判断 13 の未決）。
3. 副産物（項目 4 の材料）: 61 人の本人の θ は 1.3〜23.8 秒（中央値 3.9 秒）・停滞の始まりは 1 人あたり中央値 18 件・`p_stuck ≥ 0.6` の秒は 4.7%（`experiments/20261031-coauthor-pre-request-signal/results/round2_dwell100/`）。

## 1 始め方

1. 返答・記録・AskUserQuestion は日本語で。記号を多用しない。決めることは推奨と理由を添えて AskUserQuestion で聞く。
2. `/start-task` の作法で `.steering/<日付>-gse-public-data-fit-item2/` を作る（新しい worktree・origin/main から）。
3. 最初に研究者に聞くこと（下の §3）を、§2 の確かめの後に AskUserQuestion で聞く。条件は計算の前にコミットする。
4. 長い計算は G-GEAR かを先に考える（memory `feedback-ggear-tasks-stay-on-ggear`）。G-GEAR で重い計算中は PR を出さない。main へのマージは研究者の指示で PR なし・`[skip ci]`（2026-11-01 の項目 1 と同じ）。
5. 完了時は code-reviewer と /cross-review を並列で回す。

## 2 先に確かめること（一次）

- データの置き場: 照合論文のトラック（`/Users/johnd/GSE-wt-matching-manuscript/experiments/20261012-public-keystroke-matching/data.md`・ブランチ `docs/public-keystroke-matching-manuscript`）は KLiCKe の `WritingTask.zip`（SHA-256 `ffa4d753…555d`・記録の CSV 4,992 本）を取得済みだが、置き場の `raw/` は 2026-11-01 時点でこの Mac の worktree に無かった（G-GEAR の可能性）。そのトラックの成果物は書き換えない・読むだけ（判断 18）。Mac に無ければ、同じ data.md の手順（Drive のファイル ID・SHA-256 で照合）で `~/gse-public-data/klicke/` に取り直す。人口統計のファイルは取らない（MTurk の worker ID を尋ねる調査票）。
- KLiCKe の利用条件: [V273] 逐語 "These files can be downloaded and used freely. However, if you wish to use them in your research project, please reference this repository as an original"。著者からの 2026-10-24 の返事は利用への懸念を書いていない（`/Users/johnd/GSE-wt-matching-manuscript/.steering/_handoff/next-session-public-keystroke-matching-manuscript-kaggle-source.md:17`）。研究者は公開の条件で使うと決めた（§3）。
- Kaggle [V265]: コンペのデータは KLiCKe を公開する前に KLiCKe のコーパスから取ったもの（同じ返事）。独立のデータではないので使わない（§3）。
- KLiCKe の記録は押下と離しの時刻（`DownTime`・`UpTime`）を持つ。CoAuthor と違って離しの合成が要らない。列と書式の癖（バックスラッシュつきの 2 字・cp1252 の 21 本）は照合論文の data.md の検査 1・2 と notes.md の逸脱 D1。

## 3 研究者が決めたこと（2026-11-01・`.steering/20261101-gse-pre-stall-signal/decisions.md` 判断 4）

1. データ: KLiCKe だけ（Kaggle は KLiCKe 由来で独立でない・使わない）。
2. 出す分布: 両方。主は止まりの初期の値（休止が本人の θ の 0.5・0.75 倍に届いた時点で、作文中の発火の頻度（1 時間あたり）と、そのうち本人の停滞に至る割合）。副は KLiCKe での案 A の追試（離しの時刻があるので、合成の離しの影響を外した形）。
3. KLiCKe の利用: 公開の利用条件の範囲で使い、出すのは集計値だけ。人口統計のファイルは取らない。
4. 残っているのは解析の条件（何を数えるか・何なら成り立つと読むか）。新しいセッションで推奨を添えて AskUserQuestion で聞き、計算の前にコミットする。
5. 2026-11-01 の追記（研究者の回答）: 項目 2 は AI に依らない問いとして今の条件のまま進める。KLiCKe は AI なしの作文なので、案 A の追試は「ふつうのデスクワークで詰まる前が見えるか」の確かめになる（CoAuthor は AI つきの共同執筆）。主要アウトカムの見直しは合流で行う（`next-session-gse-three-parallel-tracks.md` §4 の 4）。

## 4 使えるもの

- 変換と replay の道具: `experiments/20261031-coauthor-pre-request-signal/scripts/`（`convert.py` は CoAuthor 専用。KLiCKe 用の変換は新しく書く。`add_feat.py`・`concat_writer.py`・`analyze2.py`・`slim.py` は使い回せる）。
- 作法の注意（項目 1 で踏んだこと）:
  - `gse-replay --features` は入力に `feat` 行が要る（無いと観測区間が 0 本で停滞の始まりが 1 件も立たない）。replay の既定の出力を `add_feat.py` で足す。
  - 書き手ごとにつなぐときは時刻を詰める（`--features` のティックの上限は約 11.5 日）。
  - 中間は大きい（CoAuthor で 1 回 2 GB 前後）。ディスクの空きが少ない（2026-11-01 で約 4 GB）ので、`slim.py` の形で読む項目だけを残す。
  - 書き手の ID（MTurk の ID）を結果のファイルに出さない。
  - 特徴量を書き手の中の分位に直しても、書き手ごとの AUC は変わらない（順位を保つ変換）。
