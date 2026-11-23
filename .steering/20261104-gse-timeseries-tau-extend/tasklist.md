# タスクリスト

## 道具の対応（完了前に照合）

- 実験の条件・コード → reproducibility-discipline（条件を計算の前にコミット・SEED・provenance）
- コード → 計算の前に code-reviewer、完了時に code-reviewer と /cross-review（Codex には条件・コード・集計値の文だけ）
- 決めること → AskUserQuestion で 1 問ずつ（日本語）

## このセッション（条件）

- [x] 引き継ぎ・前回の conditions D3・notes 結果 1 を読む
- [x] 引き継ぎ 1 が済んでいることを確かめる（`exp/gse-stage1-penalty-synthetic` の `db45ccd2`・push だけ残る）
- [x] worktree `/Users/johnd/GSE-prototype-tau-extend`（枝 `exp/gse-timeseries-tau-extend`・前回の枝の `b1771098` から）
- [x] grill（範囲・τ の格子・構造・集計の行・計算の場所）→ 判断 1〜5
- [x] `conditions.md`・`SEED`
- [x] 条件をコミット（計算の前・eb7a1884）

## 次のセッション（コード・合成）

- [x] 前回の scripts・run.sh・mutate.sh を写し、条件どおりに変える（logit.py は写さない・subset_old.py と repro_check.py を足した）
- [x] 合成の selftest（1 回目）: P-JOINT（対照の候補の並べの書き間違い・hmm3 の自由な母数は ar1 より少ない）と P-TAU（判断 6）が赤 → 直した
- [x] code-reviewer（計算の前）: HIGH 1 件（m11 で `full=None` を引いて落ち、変異の門が「当たらない」で止まる）→ 直した。MEDIUM 2・LOW 3 のうち K 本人 CV の None を直した。残り（P-PR1 の pflag がすべて True・「構造は他人・τ は本人 CV」の行に名指しの対照がない（select_other は P-OTH が守る）・学習の記号の四分位は書き手の値そのもの（前回と同じ方針））は直していない
- [x] 合成の selftest・変異の門を Mac で通す（2026-11-05・Python 3.14.4・numpy 2.5.2）: 17 対照すべて緑（678 秒）、変異 11 個すべて名指しの対照が赤・終了コード 3（1,055 秒）
- [x] 時間を測り直す（timing.py・results/timing.json・合成・Mac）: 前回の HP Z2 の実測に「今回 / 前回」の比を掛けて本計算 約 1.0 時間（共通 約 2,390 秒・書き手 約 1,180 秒・書き手は前回のロジスティックを含むので上側）。合成の絶対の見積もり（16 プロセス）は 約 1.4 時間。条件の見積もり（約 1 時間 40 分）以内。大きい τ は反復が 7〜11 回で収まる
- [x] 職場の PC 向けの引き継ぎ（`.steering/_handoff/next-session-gse-timeseries-tau-extend-run-on-hp-z2.md`・manifest・`-X utf8`・JOBS = 16・P-REPRO）

## 本計算の後

- [x] P-REPRO の結果を確かめる（cells 4,224・mismatched 0・max_rel_diff 0.0。門・来歴もすべて通った・2026-11-06）
- [x] notes（言えること・言えないこと）。骨組み（値なし・読みの形を結果の前に決めた）は 2026-11-05 に書いた。値と読みは 2026-11-06。tables.md を report.py で生成
- [x] code-reviewer と /cross-review（HIGH 1 件は両者一致: 但し書きの範囲 → 判断 7 で直した。MEDIUM・LOW の転記・範囲の誤りも直した）
- [ ] push（研究者の手元で）・PR は研究者に確かめてから・`[skip ci]`
