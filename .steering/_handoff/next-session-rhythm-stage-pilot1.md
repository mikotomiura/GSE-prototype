# 引き継ぎ: 背景のステージの机上の検査 —— 下見 1 と計器の残り

作成 2026-10-13（Windows・G-GEAR）。返答・記録は日本語で。記号（★・⚠️）を多用しない（研究者の指摘）。

## 新しいセッションで最初に打ち込む文

```
.steering/_handoff/next-session-rhythm-stage-pilot1.md を読んで、背景のステージの下見 1 と計器の残りを作って。
```

## 1. ここまでの状態

- design は**固定済み**（`2b7db259`・`.steering/20261012-rhythm-stage-desk-check/design.md`）。本番の world は **v4**（停滞は訂正の率と区間の構造にだけ出る・研究者の判断 16）。固定の後に変えたものは §8 に書く。基準の値は動かさない。
- 下見 0 は 2 回回した: 1 回目 v2 0.997・v3 0.884（使えない・`results/ceiling-1/`）、2 回目 v4 0.705（使える・`results/ceiling/`）。値は design §3.0。
- 計器は `experiments/20261012-rhythm-stage-desk-check/`: `gen_sessions.py`（EH1 の写し + `--world v3`・`v4`）・`baseline.py`（モデル A と A_speed・`tables()`）・`ceiling.py`（統計の写し `auc_prep`・`auc_w`・`oof_predict`）・`selftest.py`（下見 0 のぶん）・`run.sh --selftest | --ceiling`。`/cross-review` は判断 15・17。
- Python は EH1 第 3 回の `.venv` を `PYTHON` で渡す（`env.md`）。

## 2. 読む順（一次）

1. `design.md` の全文（特に §1.2〜§1.5 の写像・PC・攻撃者、§3.1〜§3.3 の判定、§3.4 の記述、§3.7 の自己検査、§3.9 の下見 1、§8）と `decisions.md` 判断 1〜17。
2. EH1 第 5 回の計器: `experiments/20261010-portrait-eh1-round5/scripts/checks.py`（`judge`・`e13_target`・ブートストラップ・`stratified_permutation`・`lagged`・`select_lambda`・`isotonic_blocks`）・`replay_all.py`・`selftest.py`・`run.sh` の `prepare`。

## 3. このセッションでやること

1. 計器の残り: `replay_all.py`（EH1 の写し・`gse-replay` は EH1 と同じビルド `C:/wt/_target-portrait-eh1/release/gse-replay.exe`・SHA-256 `71d09dab…986` を `GSE_REPLAY` で渡す・新しく build しない）・`stage.py`（24 候補・PC1・PC-stall・PC0・PC-corr の 10 Hz の `a`・`r`、`ALLOWED_INPUT`）・`twins.py`・`checks.py`（§3.1〜§3.6）。`selftest.py` に §3.7 の残り（入力の閉じ・因果 2 つ・双子・止まり方・遅れの量・PC・変異）を足す。
2. `run.sh --pilot`（§3.9: `SEED + 1`・P 40・world v4・PC-stall 24 本の λ の格子・L300 で目標 0.05・上限 0.08）→ λ を `config.json` に書き、値を §8 に書く。下見 1 では候補 24 本を回さない。所要を見積もる（73 本 × 3 ラベル）。
3. `run.sh --smoke` → 計器の `/cross-review`（Codex はパスを限ったラッパー `scripts/run-codex-review.sh <range> -- <paths>`）と code-reviewer。本番は CI の走っていない時に回す。

## 4. 守ること

- 合成の列だけを使う。実在の人の打鍵・gse-dataset のログは使わない。キーストロークの内容・NDJSON の生ログ（合成も）を外部の LLM（Codex を含む）に送らない。
- 本番の前に候補の値を見ない（下見 1 は PC-stall だけ）。
- `src-tauri/`・EH3 のファイル（`wallpaper.rs`・EH3 の事前登録）に触れない（判断 1）。
- Codex の台帳（`.codex/budget.json`）は `git checkout --` で戻さない。回す前に origin/main の台帳も見る。
- `git add -A` を使わない（明示したパスだけ）。
- v4 の結果の読み方は design §3.3 の v4 の宣言に限る（緑は「打鍵の時刻に停滞が出るときにステージがそれを写さない」を言わない）。
