# タスクリスト — Step 5: 層 0 とのバランスで「読める閾値」を探る

> 対応: `requirement.md` / `design.md` / `decisions.md`

---

## Step 5a — 層 0 の音量つまみ

- [x] `step4.config.json` に `layer0_gain` 軸（`l0_full` 1.0 / `l0_half` 0.5 / `l0_quarter` 0.25 / `l0_eighth` 0.125 / `l0_off` 0）を追加。既定 `l0_full`
- [x] `step4.html` に軸 UI（既存のラジオ群と同じ型）を追加
- [x] `applyLayer0Gain()` を新設（★ raised-cosine / `setValueCurveAtTime` / `cancelAndHoldAtTime`）
- [x] ⚠️ **`buildGraph` を含む LAYER0-CORE を 1 文字も触っていないこと**（S5-D4）
- [x] `__step4.state()` に **いま効いている `expr.gain`** を出す（★ 目標値ではない）
- [x] ★ 再生をまたいで選択が保たれる（`startAudio()` の末尾で適用）

## Step 5b — 測定の前提を壊さない（S5-D6）

- [x] ★ ①（比の実測）が **つまみのランプ到達を待つ**（`l0RampUntil`）。残り秒数を画面に出す
- [x] ★ 盲検の結果 JSON に **層 0 の倍率（候補 id ＋ 実数）** を記録する
- [x] ★ つまみを変えたら **比を測り直させる**（前の比を持ち越して盲検を始めさせない）
- [x] ★ 既存 4 点（均衡 / 対照の差 / 端点校正 / ピーク）が倍率を変えても効き続けることを確認

## 検査（★ すべて「壊して赤くなること」を実測する）

- [x] 候補に **1.0 と 0 の両方**が実在する
- [x] 既定が **1.0**（＝既定で音が変わらない）／ すべての `gain` が 0..1
- [x] ★ **`expr.gain` を書く実時間側の箇所が 1 つだけ**（S5-D5）
- [x] ★ つまみが **raised-cosine 曲線**で移る（段差でない）
- [x] ★ 校正が `l0RampUntil` を参照している
- [x] ★ 結果 JSON に層 0 の倍率が入る
- [x] ★ **LAYER0-CORE の一致検査（S4-D8）が緑のまま**
- [x] `bash run.sh check` が全緑（selftest / meta / 平滑器 / Step 3 / git 混入）

## ブラウザ実地（⚠️ BL-1 — 4 回詰まった形）

- [x] ★★★ **`{visibilityState, hasFocus, outerWidth}` を先に実測**。`hidden` / `0` のうちは一切測らない
- [x] 実クリックで倍率を変え、**着弾先の要素**を確認（`mousedown` capture プローブ）
- [x] ★ **AC-1**: 倍率を変えて **層 0 単体 rms が変わり / 層 2 単体 rms が変わらない**ことを実測
- [x] ★ **AC-2**: 切替中の rms 軌跡を実測し、**段差が無い**ことを示す
- [x] ★ **AC-3**: 逆検査が **FAIL のまま**であること（つまみを変えても検算の基準が動かない）
- [x] ★ **AC-4**: 各倍率で①を実測し、**予測表と実測を並べて記録**（★ 予測を実測欄に書かない）
- [x] ★ ピーク / クリップを実測（`__step4.peak()`）

## 研究者の耳（★ ここからは私は判定しない）

- [ ] ★ 倍率ごとに **①比 → ②盲検 8 回** を繰り返して閾値を探す
- [ ] ★ 閾値の倍率で **10 分聴いて B1（気にならないか）** を問う ← ★★★ **α の可否**
- [ ] 結果 JSON を `results/` に保存してもらう

## 記録

- [x] `experiments/20260812-expression-step4-grain/notes.md` に **【Step 5】/ S5-n として追記**（既存の節を書き換えない）
- [x] 研究者の言葉を **原文どおり**残す（「かも」を「である」に直さない）
- [x] ★ **無効と分かった測定は消さず、無効であると書いて残す**

## 完了処理

- [x] ★★ **S4-D1 で決めたまま未実施のレビューを消化**: `code-reviewer` + `security-checker` **並列**
- [x] ★ `/cross-review`（⚠️ **実データを diff に含めない** / ⚠️ 未追跡は `git add -N` / ⚠️ commit 前に回す）
- [ ] `/finish-task`
- [ ] ⚠️★★★ **`git push` は deny されている。研究者に `! git push` を依頼する**
