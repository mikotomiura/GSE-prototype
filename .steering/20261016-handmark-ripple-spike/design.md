# 設計

## アプローチ

前の試作（`.steering/20261016-handmark-a-surface-spike/design.md`）の窓・配線・取り込みの除外・fail-closed はそのまま使い、変えるのは描画と窓の大きさと計測だけ。

### 描画（判断 5・見本 https://claude.ai/artifact/5uejeC8kJ9PF2sFTyUquzc の甲-2 と同じ式）

- `HandmarkSurface.tsx` を canvas に替える。大きさ `size = 28`（半径 `r = 14`）。
- 地: 中心に灰の点（半径 `0.32 r`）を常に描く。
- 波紋: 打鍵を受けたら、その時刻を起点に 250 ms で、半径 `r × (0.36 + 0.7 × ease(t))`・不透明度 `1 − ease(t)`・線幅 `max(1.2, 0.12 r)` の輪を描く（`ease(t) = 1 − (1 − t)^2`）。続けて打ったら、前の波紋を捨てて新しい起点から描き直す（波紋は常に 1 つ）。
- 色: 灰（見本の `--s-gray-base` / `--s-gray-hi`。明るい外観で #9aa3ab / #ffffff、暗い外観で #5e676f / #f2f4f6）。外観は `prefers-color-scheme` で切り替える。
- 描画のループは波紋があるあいだだけ回し、消えたら地を描いて止める（止まった後に動き続けないことの確かめにも使う）。
- 窓: 輪の最大の半径は `1.06 r ≈ 14.8 px` に線幅の半分を足して約 15.7 px なので、窓を 32×32 にする（`SIDE = 32`）。端からの余白は 28 px の円の縁が端から約 16 px になるよう `MARGIN = 14`。

### 計測（`GSE_HANDMARK_SPIKE_MEASURE=1` のときだけ）

1. 遅れ: 前の試作と同じ（描画の後の 2 つ目の `requestAnimationFrame` で `Date.now() − 打鍵の時刻`・`latency-<起動>.csv`）。
2. 波紋の一生: 波紋が終わる（打ち切られる・250 ms を描き終える）たびに 1 行を返す。中身は `seq`・`start_ms`（最初に描いたフレームの `performance.now()`）・`end_ms`（最後に描いたフレームの `performance.now()`）・`max_t`（描いた進み `t` の最大）・`truncated`（打ち切りか）。`ripple-<起動>.csv` に書く。時刻は `performance.now()`（窓を開いてからのミリ秒）で、壁時計は持たない。
3. 止まった後に消えるか: 描き終えた波紋の `cleared_ms − start_ms`（地だけを描いて描画のループを止めたフレームまで）が 250 ms ＋ 1〜2 フレームを超えないこと。当初は `idle` の行を別に書く案だったが、描き終えた行の `cleared_ms` で代える（実装に合わせた・判断 5）。
4. 記録の限り: `start_ms` は打鍵を受けた時刻ではなく最初に描いたフレームの時刻。1 フレームも描く前に打ち切られた波紋は行を残さない（遅れの CSV には seq がある）。窓を閉じる直前の波紋も残らない。

集計（scratchpad の Python）:
- 動いていた割合: 区間 `[start_ms, end_ms]` の和を 10 秒の窓で数える。列ごとに、列の中に収まる 10 秒の窓を 1 秒ずつずらした値の中央値と範囲を出す（見本の量と同じ定義）。
- 一打ごとの見分け: 打ち切られた波紋の `max_t` から、輪の半径（`0.36 + 0.7 ease`）と不透明度（`1 − ease`）を出し、列ごとの分布を表にする。

### 合成の打鍵の列

- 一定の間隔: 0.06 / 0.10 / 0.15 / 0.25 / 0.40 秒（それぞれ約 15 秒ぶん）。0.25 秒は 250 ms とちょうど同じで、境目を見る。
- バースト: 0.12 秒間隔で 12 打 → 2 秒止まる、を 5 回。
- `synthetic-keys.applescript`（前の試作）を流用し、バーストは新しい `synthetic-burst.applescript`。AppleScript の `delay` は正確でないので、間隔は CSV の `start_ms` の差から実測で書く。
- 遅れの取り直しは前と同じ列（0.15 秒 × 200・0.06 秒 × 100）。

## 変更対象

### 修正するファイル
- `src/components/HandmarkSurface.tsx` — 描画を canvas の波紋に、計測に波紋の一生を足す
- `src-tauri/src/handmark_spike.rs` — `SIDE`・`MARGIN`、`handmark_spike_ripple` コマンドと 2 つ目の CSV
- `src-tauri/src/lib.rs` — コマンドの登録 1 行

### 新規作成するファイル
- `.steering/20261016-handmark-ripple-spike/synthetic-burst.applescript`

## 影響範囲

試作の窓は `GSE_HANDMARK_SPIKE=1` のときだけ作られる。環境変数が無ければ前と同じく何もしない。取り込みの除外・fail-closed・推定に依らない配線は変えない。

## 既存パターンとの整合性

前の試作の計測の方式（環境変数で有効・CSV は一時ディレクトリ・一時停止中は書かない・窓の label を確かめる）に揃える。

## テスト戦略

- 単体: 新しい CSV の 1 行の書式と、受け付ける値の範囲（`max_t` は 0〜1・時刻は有限）を純粋な関数でテストする。
- `cargo test`・`cargo clippy`・`npx tsc --noEmit`。
- 実機（Mac）: 上の列を流して CSV を集計する。研究者が自分の画面で見る（`manual-check.md`）。

## ロールバック計画

試作の枝の中だけの変更で本線に入れない。戻すなら該当コミットを revert する。
