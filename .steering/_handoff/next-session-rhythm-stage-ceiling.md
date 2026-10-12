# 引き継ぎ: 背景のステージの机上の検査 —— 下見 0（基準のモデルの天井）の計器

作成 2026-10-12（Windows・G-GEAR）。返答・記録は日本語で。記号（★・⚠️）を多用しない（研究者の指摘）。

**着手の条件**: 研究者が `.steering/20261012-rhythm-stage-desk-check/design.md` §9（Claude が足した細部 14 項目）を確かめ終えていること。変えたい項目があれば、下見 0 の**前に** design を直してコミットする（下見 0 の後は §3.0 の末尾への値の追記しか許さない・design §3.0「順序」）。最初に研究者に「§9 は確かめ終えたか・変える項目はあるか」を聞く。

## 新しいセッションで最初に打ち込む文

```
.steering/_handoff/next-session-rhythm-stage-ceiling.md を読んで、背景のステージの下見 0 の計器を作って。
```

## 1. 読む順（一次）

1. `.steering/20261012-rhythm-stage-desk-check/requirement.md`・`decisions.md`（判断 1〜12）・`design.md`（全文。特に §1.5 の A_speed・§1.6 の world v3・§3.0 の下見 0・§3.2 の天井）。
2. EH1 第 5 回の計器: `experiments/20261010-portrait-eh1-round5/`（`scripts/gen_sessions.py`・`scripts/portrait.py` の `presence_features`・`presence_features_long`・`scripts/checks.py` の `oof_predict`・`e13_labels`・`config.json`・`run.sh`・`data.md`・`env.md`）。
3. 新規性の文献: `docs/literature/20261012-rhythm-stage-novelty.md`（S-RN・設計には影響しない）。

## 2. このセッションでやること（下見 0 だけ）

1. `experiments/<日付>-rhythm-stage-desk-check/` を作る（`reproducibility-discipline`・`docs/experiment-tracking.md`）。EH1 第 5 回から `gen_sessions.py`・`SEED`（20261009）・`requirements.txt`・`env.md`・`data.md` の型を写す。
2. `gen_sessions.py` に `--world v3` を足す（design §1.6: STRUGGLE の `flight_median_ms`・`flight_sigma` を FLOW と同じ 150・0.25、v1 の `p_pause_after_bs` 0.6・`pause_after_bs_min_ms` 2000・`pause_after_bs_extra_ms` 3000 を STRUGGLE に戻す）。v1・v2 の出力が EH1 第 5 回の生成器と SHA-256 で同じことを先に確かめる（design §3.7 の world）。
3. A（EH1 と同じ）と A_speed（design §1.5 の速さの 5 量・L60 は前 4 窓の量 1・2）を作る。
4. `run.sh --ceiling`: `SEED + 1`・P 40 で world v2 と v3 の合成の記録を作り、ラベルごと（L300・L60・L1800）・分類器ごと（hgb・lr）に AUC(A)・AUC(A_speed) を OOF で出す。`gse-replay` は使わない。描画の候補・PC は作らない・回さない。
5. design §3.0 の選び方（L300 の AUC(A_speed) の小さいほうの分類器 ≤ 0.85 の world を使える・v2 優先）で world を決め、値と選んだ world を §3.0 の末尾に追記してコミットする（これが「固定」）。v3 の AUC(A)・AUC(A_speed) − AUC(A) も記録する。どちらも使えなければ本番に進まず研究者に戻す。
6. 計器のコードは `/cross-review`（Codex の系統はパスを限ったラッパー `scripts/run-codex-review.sh <range> -- <paths>`）と code-reviewer に通す。

## 3. 守ること

- 合成の列だけを使う。実在の人の打鍵・gse-dataset のログは使わない。キーストロークの内容・NDJSON の生ログを外部の LLM（Codex を含む）に送らない（合成の NDJSON も Codex に渡さない）。
- 実装（`src-tauri/` の描画やデスクトップの層の窓）はしない。EH3 のファイル（`wallpaper.rs`・EH3 の事前登録）に触れない（判断 1）。
- この機械は G-GEAR（self-hosted の Windows CI の runner を兼ねる）。下見 0 は `gse-replay` を使わないので build は要らない。本番（後の段）では EH1 と同じビルド `C:/wt/_target-portrait-eh1/release/gse-replay.exe`（SHA-256 `71d09dab…986`）を使う。
- Codex の台帳（`.codex/budget.json`）は `git checkout --` で戻さない。回す前に origin/main の台帳も見る（ブランチごとに記帳が分かれる）。
- `git add -A` を使わない（明示したパスだけ）。

## 4. 下見 0 の後（別の段）

- 下見 1（PC-stall 24 本の λ・design §3.9）→ 計器の残り（`stage.py`・`twins.py`・`checks.py`・`selftest.py`）→ スモーク → 本番（73 本 × 3 ラベル）→ `notes.md`。
- 結果は親タスク `.steering/20261012-portrait-rhythm-motion/` の判断 3（新しい面の規則）・判断 5（背景での招待）の見直しの材料として研究者に渡す。
