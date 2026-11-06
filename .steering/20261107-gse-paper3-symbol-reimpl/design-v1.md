# 設計（初案 v1）—— 記号化の書き直し

経路の洗い出し: `obs-pipeline-map.md`（サブエージェント・2026-11-07）。メインが一次で確かめた所: `obs` は 1 回目の replay の出力（`build_obs.py` の `feat_p`）から取る／平滑は `0.3·raw + 0.7·prev` のリテラル（`engine.rs:383-395`）／x・y は head の重みのあと [0, 1] に clamp（`heads/writing.rs:126-129`）／5×5 と罰の 25（`engine.rs:402-410`）。

## アプローチ

純 Python（標準ライブラリのみ・numpy なし）で、生データから `obs` までを 1 本の離散時間の模擬として書き直す。

1. 変換: CoAuthor の生の出来事（user 起源の 1 文字の挿入・削除・カーソル移動）と CS1 2021 の X-Keystroke / X-Action を `{t, category}` の押下の列にする（既存の変換の規則を仕様として写し、コードは新しく書く）。
2. 離しの合成: `rel = min(t + 100, max(t, 次の押下 − 1))`。
3. 模擬: t0 から 1,000 ms の格子の tick と出来事を、同時刻は tick を先に、安定な並びで処理する。容量 600 のバッファ、30 秒の窓の 5 特徴、経路（打鍵中・移り・沈黙）、φ と x・y、共有の平滑（初期値 (0.1, 0.8)・経路ごとの α）、5×5、罰（Backspace の連続 14 以上・保留して打鍵中の更新で消費）。
4. 出力: tick ごとの (t, x, y, obs, α)。

浮動小数は replay と同じ演算の順で書き、x・y の値の bit まで一致を目標にする（`obs` だけでなく `ewma_x`・`ewma_y` も照らす。bin の境界の 1 ULP のずれを見つけるため）。

## 変更対象

- 新規: `papers/per-person-learning/kit/symbols/`（`symbols.py`・`convert_coauthor.py`・`convert_cs1.py`・`selftest.py`・`README.md`）
- 新規（公開しない）: 照合のスクリプト `.steering/20261107-gse-paper3-symbol-reimpl/check_against_replay.py`（手元の中間 `~/gse-public-data/...` の `feat` の `obs`・`ewma_x`・`ewma_y` と比べ、一致・不一致の件数だけを出す）
- GSE 本体は変えない。

## テスト戦略

- 合成の selftest: 手で作った短い押下列で、経路の分かれ目（沈黙 2 秒・15 秒・25 秒）、罰の保留と消費、f1 == 0 で行が出ない場合、同時刻の tick と出来事の順、を期待値で確かめる。期待値は replay で同じ合成の入力を回して得る（GSE の側の出力を正にする）。
- 変異: α の閾値・罰の閾値・tick の順・離しの合成をそれぞれ 1 つずつ壊し、名指しの selftest が赤になるのを見る。
- 実データの照合: CoAuthor の全セッション・CS1 2021 の全課題で、feat 行の数・各行の t・obs・ewma_x・ewma_y の bit が一致すること。不一致は件数と種類だけを記録して止める。

## 却下候補（/reimagine で比べる）

- Rust の独立クレートに関数を写す（浮動小数の一致は確実だが、読者には重く、論文 1 の逐語コピーの形に近づく）。
- 変換は既存の GSE の NDJSON を入口にし、模擬だけを書き直す（変換を公開しないと生データから作り直せない）。
