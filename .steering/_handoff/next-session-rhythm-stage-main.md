# 引き継ぎ: 背景のステージの机上の検査 —— 本番

作成 2026-10-13（Windows・G-GEAR）。返答・記録は日本語で。記号（★・⚠️）を多用しない（研究者の指摘）。

## 新しいセッションで最初に打ち込む文

```
.steering/_handoff/next-session-rhythm-stage-main.md を読んで、背景のステージの本番を回して notes を書いて。
```

## 1. ここまでの状態

- design は固定済み（`2b7db259`・world v4）。固定の後の逸脱は design §8（判断 18・19・下見 1 の値・細部の読み方・スモークの seed）。
- 計器は `experiments/20261012-rhythm-stage-desk-check/` に揃った（`stage.py`・`twins.py`・`checks.py`・`replay_all.py`・`selftest.py`・`run.sh --pilot | --smoke | --main`）。code-reviewer 1 巡と Codex 2 巡を通した（判断の記録は tasklist と各コミット）。
- 下見 1 は済み: `config.json` の `pc_stall.lam`（raw 0.05・smooth と rank 0.15・jitter の hold と decay 0.10・jitter の ground 0.15）。値は design §8。
- スモーク（`SEED + 2`・P 12）は `results/main-smoke/`（git の外）。結果はこの引き継ぎの §4 に書く。

## 2. 読む順（一次）

1. `design.md` の §3.1〜§3.6（判定と記述）・§3.3 の v4 の宣言・§8 の全行。`decisions.md` 判断 16〜20。
2. `scripts/checks.py` の `judge`・`main_run`・`describe` と、出力の `e13.json`・`describe.json`・`summary.json` の形。

## 3. このセッションでやること

1. CI が走っていないことを確かめる（`gh run list --limit 5`・G-GEAR は self-hosted の runner）。
2. `PYTHON=C:/wt/portrait-eh1-round3/experiments/20261010-portrait-eh1-round3/.venv/Scripts/python.exe GSE_REPLAY=C:/wt/_target-portrait-eh1/release/gse-replay.exe bash run.sh --main --jobs 16` を裏で回す（8〜15 時間の見込み。出力はファイルに保存）。生成・replay・双子・自己検査（P 240 での λ=1 の PC と seg の変異を含む）・判定・記述の順。
3. 終わったら `results/main/`（`e13.json`・`describe.json`・`summary.json`・`provenance.json`・`capabilities.json`）をコミットし、`notes.md` を書く: 項目 1 の判定（L300 が主・L60・L1800 は副）と検査器の理由、赤の内訳と重要度（§3.6）、項目 2〜4・6 の記述、A を基準にした値、design §3.3 の読み方の文（特に v4 の宣言）。
4. 判断 18（jitter の遅れは読まない）・判断 20（`res=sec` のテンポは速さをほぼ運ばない）を notes の読み方に入れる。
5. 結果は親タスクの判断 3・5 の見直しの材料として研究者に渡す（tasklist の最後の項）。

## 4. スモークの結果

2026-10-13・計器 `dab6dd66`・汚れなし・seed 20261011（`SEED + 2`）・P 12 と双子・`results/main-smoke/`（git の外）。自己検査は 0 件の失敗、生成から `summary.json` まで 768 s で通った（判定・記述 25 本・双子の AUC 24 本が出る）。P 12 の判定の数は配線の確認だけで、読まない（本番の列ではない）。

## 5. 守ること

- 合成の列だけを使う。キーストロークの内容・NDJSON の生ログ（合成も）を外部の LLM（Codex を含む）に送らない。
- 結果を見てから主のラベル・基準・world・λ・式を選び直さない（design §3.0・§3.3）。
- `src-tauri/`・EH3 のファイルに触れない（判断 1）。
- Codex の台帳（`.codex/budget.json`）は `git checkout --` で戻さない。
- `git add -A` を使わない（明示したパスだけ）。
