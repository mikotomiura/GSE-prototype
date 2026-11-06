# 次のセッション —— 公開データの知見の論文 1: 結果の登録・CoAuthor の探索・原稿

> 作成: 2026-11-06。worktree `/Users/johnd/GSE-prototype-public-findings`・枝 `docs/public-data-findings-paper`（push は研究者の手元）。前の引き継ぎ `next-session-gse-public-data-findings-paper-5.md` の §2 は全部済んだ。

## §1 状態

- 事前登録 v10 を OSF で凍結した（英語版を正）。プロジェクト `https://osf.io/cm4ru`（非公開）の登録は次の 4 つ（どれも公開・承認済み）:
  1. 事前登録 `https://osf.io/mrkxt`（2026-11-05T21:56Z・manifest 9a1a7f14…28da9b・凍結の commit 63885bad）
  2. 開始の記録 `https://osf.io/hfvy7`（この走りは変換の照合 145 / 146 で中断・判定の値は計算していない）
  3. 逸脱 1 `https://osf.io/fqgcp`（照合を check_holdout_writers.py に・manifest c821ae03…f6b0・commit abc1ed0e・研究者の判断）
  4. やり直しの開始の記録 `https://osf.io/ajg2x`（start.json 8aeb07fa…7f7013）
- 最初の完走: commit 4a30ce6e・confirm_holdout.json 3a73346f…d72018。H1 は支持（4 つの組がすべて分岐 1・0.487〜0.489）、床にない対の感度（始点）も分岐 1、H2 は 2 信号とも分岐 4、H3 は 2 学習器とも分岐 2（記述）。詳細は `experiments/20261105-findings-paper1-prefreeze/notes.md` の末尾。
- 探索（付録 F・判定に使わない）: CS1 2021 年版の見た 31 人と KLiCKe は H1 の型が分岐 1・H2 の型が分岐 4。引きの種の幅は 0.486〜0.494。`experiments/20261106-findings-paper1-exploration/notes.md`。
- 判断の記録は `decisions.md` の判断 20〜23。attack-me は round 8 で閉じた。

## §2 やること（この順）

1. **結果と来歴を OSF の 5 つ目の登録にする**（Chrome の拡張が切れて未了）。添えるもの: `results_holdout/confirm_holdout.json`・`provenance_holdout.json`・`holdout_writers_check.json` と、`git archive --format=zip 4a30ce6e experiments/20261105-findings-paper1-prefreeze/results_holdout` の zip。作り方は前の 4 つと同じ（OSF の API で Open-Ended の下書き・要約・ライセンス CC BY 4.0・分野 Educational Assessment, Evaluation, and Research → immediate → Gmail の承認のリンクを href で開く〔取り消しのリンクと座標が近いので押さない〕→ API で public と SHA-256 を照合）。notes に URL を書く。
2. **CoAuthor の探索**（付録 F の残り）: `~/gse-public-data/coauthor/work2_dwell100/` の書き手ごとにつないだ中間を、`confirm_p1.h1_writer`・`h2_writer`（`cs1=False`）に渡す橋渡しと、付録 A4 の AI の提案まわりの出来事の除外を、条件の文書に書いてコミットしてから実装する。取っておいた 18 人は開けない。
3. **原稿（JEDM）**: `paper-write/outline.md` の分岐の書き方（H1 支持 × H2 分岐 4 → 揃えた比べの同等だけを報告し、対比は主張しない）で外枠を確定し、草稿へ。主の 1 文は notes の末尾の文。
4. push と PR は研究者の手元（docs だけなので [skip ci]）。

## §3 気をつけること

- 取り置きの手順は完走の記録で止まる。再実行しない。凍結した文書と manifest のファイルを書き換えない（変えるなら逸脱）。
- `.codex/budget.json` は台帳で、未ステージのまま（巻き戻さない）。
- 書き手ごとの値を repo に出さない・外部の LLM に送らない。
