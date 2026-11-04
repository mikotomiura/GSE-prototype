# 引き継ぎ —— τ の格子を広げる試験のコードと合成の門（条件の後の段）

> 作成: 2026-11-04（Mac のセッション）。このメモを一次資料にしない。一次は `experiments/20261104-timeseries-tau-extend/conditions.md`（計算の前にコミット済み・`eb7a1884`）と `.steering/20261104-gse-timeseries-tau-extend/`（判断 1〜5・tasklist の「次のセッション」）。枝 `exp/gse-timeseries-tau-extend`・worktree `/Users/johnd/GSE-prototype-tau-extend`（前回の枝 `exp/gse-coauthor-ml-improve` の `b1771098` から）。

## 0 入口の文

```
/Users/johnd/GSE-prototype-tau-extend/.steering/_handoff/next-session-gse-timeseries-tau-extend-code.md を読み、条件どおりにコードを書いて、合成の selftest と変異の門を Mac で通してください。作業は worktree /Users/johnd/GSE-prototype-tau-extend で。
```

## 1 やること（順に）

1. 前回の `experiments/20261104-coauthor-ml-improve/` の `scripts/`・`run.sh`・`mutate.sh` を `experiments/20261104-timeseries-tau-extend/` へ写す（前回のディレクトリは変えない）。
2. 条件どおりに変える。要点:
   - `TAUS` に 3×10^4・10^5・3×10^5・10^6 と ∞ を足す。τ = ∞ は当てはめず、w を除く共通の母数を使う（評価の単位でも折り目でも）。
   - 構造は hmm3・ar1・ar2・ar3。全員の共通の乱数の通し番号は前回のまま（hmm3 = 0・ar1 = 3・ar2 = 4・ar3 = 5）。外した hmm6・hmm10 の番では `random_model` を引いて捨てる（書き手ごとの流れを前回とそろえる）。
   - 行: τ 固定 9 行・τ 他人（∞ を含む）・τ 本人 CV（∞ を含む）・2 段（他人: (構造, τ) を w を除く「本人 − r1」の中央値でまとめて選ぶ）・2 段（構造は他人・τ は本人 CV）・K 本人 CV（ar と both の族）。
   - 相手に書き手ごとの「共通 − r1」を足す。学習・評価の記号の数の中央値と四分位を出す。選ばれた τ を「格子の中・下の端・上の有限の端・∞」で数える。
   - ロジスティックの段（D4）を外す。
   - selftest: P-INF・P-TAU・P-JOINT・P-PR1・P-SUBSET を足し、P-LAM・P-LINF・P-C1・P-SIMP・P-PROBE・P-EMPTY を外す。変異 m11〜m15 を足し、m4・m5・m9・m10 を外す。
   - `repro_check.py`（P-REPRO）: 前回の `results/summary.json` と重なるセルを相対 1e-9 で照らす。HP Z2 で走らせる門（Mac では版が違うので照らさない）。
   - 書き手ごとの値の置き場所は `~/gse-public-data/landscape/timeseries_tau_extend_writer_values.*.json`。
3. 計算の前に code-reviewer。
4. Mac で合成の selftest と変異の門を通し、時間を測り直す（見積もりは HP Z2 で約 1 時間 40 分）。
5. 職場の PC 向けの引き継ぎを書く。手順は前回の `next-session-gse-coauthor-ml-run-on-hp-z2.md`（manifest の照合・`-X utf8`・JOBS = 16）を下敷きにし、P-REPRO を足す。

## 2 守ること

- 条件を直すのは実データを見る前だけで、直したら判断として `decisions.md` に書き、conditions の末尾に「条件の後の変更」として足す。
- 書き手ごとの値・holdout の一覧を人が開かない。repo には集計値だけ。Codex には条件・コード・集計値の文だけを渡す。
- EM の状態に名前を付けない。結果を段 1 の候補の採否の根拠にしない。
- push は研究者の手元で行い、PR は研究者が確かめてから出す（`[skip ci]`）。

## 3 道具

- 実験 → reproducibility-discipline。コード → 計算の前に code-reviewer、完了時に code-reviewer と /cross-review。決めることは AskUserQuestion で 1 問ずつ。
