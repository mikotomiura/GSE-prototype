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

（段 2 に入るときに書く）
