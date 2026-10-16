# 設計

## 段 1: 右下の小面を少し主張させる

- 候補は見本台（https://claude.ai/artifact/5uejeC8kJ9PF2sFTyUquzc）の甲-2 の式のまま、大きさ・色・線だけを変えた 5 つを、候補台（https://claude.ai/artifact/6MgWQuDKsintuj2DCZhJpS）に実寸で並べた。下地は明るい壁紙・暗い壁紙・色の濃い壁紙・白い文書・暗いエディタの 5 種類。どの枠も同じ合成の打鍵列で動く。
- 採った乙（判断 1）の描き方: 地の点（半径 0.32 r・墨）の外に 1.5 px の白い縁。輪は白（線 3＋1.5×2 px）を描いてから墨（線 3 px）を重ねる。透明度は輪の両方に `1 - e` を掛ける。
- 窓の一辺 52 px（輪の最大の半径 1.06 r＝21.2 px＋線の半分 1.5 px＋白い縁 1.5 px ＝ 24.2 px が収まる）。`MARGIN` 10（円の縁が作業領域の端から約 16 px）。

### 変更するファイル
- `src/components/HandmarkSurface.tsx` — `BOX_PX`・`SIZE_PX`・色と線。配色の明暗での切り替えをやめる。
- `src-tauri/src/handmark_spike.rs` — `SIDE`・`MARGIN`。

### 確かめ方
- tsc・cargo check。見え方は研究者の目（この Mac では Claude が画面を撮れない）。

## 段 2: 背景の層の実現性

### 窓（`src-tauri/src/handmark_stage_spike.rs`・新規・macOS だけ）

- `GSE_HANDMARK_STAGE_SPIKE=1` のときだけ作る。label `handmark-stage`。小面（`GSE_HANDMARK_SPIKE`）とは独立に出し入れできる。
- 主画面の全体（メニューバーの下も含む frame）の大きさ・透明・枠なし・影なし・フォーカスを取らない・タスクバーに出さない。
- 作った後に NSWindow を直接設定する: `setLevel(CGWindowLevelForKey(kCGDesktopWindowLevelKey))`（アイコンの層 `kCGDesktopIconWindowLevelKey` より下）、`setCollectionBehavior(CanJoinAllSpaces | Stationary | IgnoresCycle)`、`setIgnoresMouseEvents(true)`、`orderFrontRegardless`（key にしない）。NSPanel にはしない。
- 共有の種別は既定のまま（写るかを測る）。`GSE_HANDMARK_STAGE_SPIKE_PROTECT=1` のときだけ `sharingType = .none` にして読み返す（読み返せなければ出さない・小面と同じ fail-closed）。両方の条件で取り込みを比べる。
- 打鍵は小面と同じ所（`lib.rs` の `notify_key`）から、時刻だけを送る。推定を受け取る口を作らない。
- 計測（`GSE_HANDMARK_SPIKE_MEASURE=1` のときだけ）: 1 秒ごとに Rust 側で `occlusionState` の可視ビットを読み、窓から返る 1 秒ごとの記録と一緒に CSV に書く。

### 描画（`src/components/HandmarkStage.tsx`・新規）

- 写し方は仮で、見本台の等高線の波（9 本の正弦の線）をそのまま使う。材料は直近 30 秒の打鍵の時刻だけ。1 秒ごとに目標（振れ幅＝30 秒の打鍵の数・位相の進み＝直近 1 秒の打鍵の数）を決め、その 1 秒のあいだに滑らかに近づく（表現の議論の判断 3・`res=sec`）。2 秒止まったら振れ幅を少しずつ下げる。
- 線は半透明で、壁紙が透けて見える。
- 計測のとき、1 秒ごとに「その 1 秒で描いたフレームの数・`document.visibilityState`・1 秒の刻みが何 ms 遅れたか」を返す。

### 確かめ方

| 項目 | 方法 | 誰が |
|---|---|---|
| 層の上下 | `CGWindowListCopyWindowInfo` で、この窓とデスクトップのアイコンの窓（Finder）の `kCGWindowLayer` と並びを読む | Claude |
| Spaces | Ctrl+→ で隣のデスクトップへ移り、窓が画面上（`kCGWindowIsOnscreen`）にあるか | Claude |
| 全画面 | テキストエディットを全画面にして、窓が画面上にあるか | Claude |
| 複数ディスプレイ | いまは 1 枚だけ。研究者が外部のディスプレイを持っていれば段 3 で | 未確認になりうる |
| 覆われたときの継続 | 他のアプリをすべて隠したとき（陽性対照）と、全面の窓で覆ったときの 1 秒ごとの記録（フレームの数・刻みの遅れ・`occlusionState`） | Claude（合成の打鍵） |
| 取り込み | 前の試作と同じ Chrome の `getDisplayMedia`（自動選択）で画面全体を撮り、背景の線が写るか。保護あり／なしの両方。Zoom の自動も同じく | Claude |
| 標準のスクリーンショット | Cmd+Shift+3 | 研究者（この Mac では Claude が撮れない） |
| 負荷 | 背景あり／なしで、gse-next と WebContent のプロセスの CPU の累積時間の差分（セッション中・覆われているとき・電池のとき） | Claude |

### 変更するファイル
- 新規: `src-tauri/src/handmark_stage_spike.rs`・`src/components/HandmarkStage.tsx`・`src-tauri/capabilities/handmark-stage.json`
- 修正: `src-tauri/src/lib.rs`（mod・setup・notify_key・コマンド）・`src/main.tsx`（label の分岐）・`src-tauri/src/tray.rs`（「背景を閉じる」）

### 守ること
- `analysis/portrait/`・`wallpaper*.rs`・`eh3.rs`・`experiments/` に触れない。壁紙の画像を読まない・書かない。
- 打鍵の内容を材料にしない。計測は合成の打鍵で。
