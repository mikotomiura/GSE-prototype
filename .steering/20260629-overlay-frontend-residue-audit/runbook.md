# Runbook: オーバーレイ残存バグの状態行列計測 (Windows 実機)

目的: 「どの状態遷移後の idle で透明 overlay 窓が画面に残り背後クリックを奪うか」を一次情報で確定し、
hypotheses.md の H1-H5 を確定/棄却する。**推測で直さない。まずこの行列を埋める。**

## 0. 前提・起動

- Windows 11 実機 (被験者環境)。`VITE_GSE_DEBUG=1` かつ `GSE_DEBUG=1` の二重 gate を両方設定。
  - dev: `set GSE_DEBUG=1` した上で `VITE_GSE_DEBUG=1 npm run tauri dev` (git-bash/PowerShell の流儀に合わせる)。
  - ビルド版で測るなら、起動シェルで `set GSE_DEBUG=1` してから exe を起動 (フロントは VITE_GSE_DEBUG=1 で焼いた版)。
- ログ: backend の tracing 出力 (`target=overlay_audit` の `overlay_window_state` 行) を収集。
  各行に `tag / x / y / w / h / visible / offscreen / ex_transparent / ex_layered` が出る。
- Dashboard の debug ボタン (`force_nudge` / `force_wall` / `debug_force_probe`) で各遷移を能動的に発火できる。

## 1. 読み方 (番兵)

- **idle が正常**: idle-immediate と idle-after-1500ms の両方で `offscreen=true` (x<=-10000)、w/h が小さい。
  → この状態の遷移後 idle は背後クリックを奪わない (退避が効いている)。
- **idle が残存 (バグ)**: idle-* で `offscreen=false` かつ w/h が box(≈390x430) 級 / 全画面級。
  → この窓が透明のまま画面に残りクリックを奪う。`ex_transparent` も併せて確認:
  - `ex_transparent=false` なら setIgnoreCursorEvents が実効していない (#11461 裏取り) →
    退避が唯一の頼みだったのに効いていない = H4/H5 濃厚。
  - `offscreen=true` なのに体感でクリックを奪う → 退避は効いているが別窓 (main 窓等) の問題を疑う。
- **後から戻る (上書き)**: idle-immediate=offscreen=true だが idle-after-1500ms=offscreen=false →
  別 effect が退避を上書き (H2/H3)。どの遷移の後で戻るかを記録。

## 2. 状態行列 (各行を 1 操作ずつ・他アプリ前面で背後クリック可否も体感記録)

| # | 遷移 | 操作手順 | 期待 (正常) | 記録: idle-immediate | 記録: idle-1500ms | 背後クリック可? |
|---|---|---|---|---|---|---|
| 1 | probe → 回答 → idle | debug_force_probe → カードで「回答する」 | offscreen=true | | | |
| 2 | probe → skip(思い出せない) → idle | debug_force_probe → 「思い出せない」 | offscreen=true | | | |
| 3 | probe → skip(✕) → idle | debug_force_probe → ✕ | offscreen=true | | | |
| 4 | nudge → dismiss → idle | force_nudge → いずれかの dismiss ボタン | offscreen=true | | | |
| 5 | nudge → silent(無操作60s) → idle | force_nudge → 60s 放置 | offscreen=true | | | |
| 6 | wall → 解除 → idle | force_wall → QR/Early Unlock で解除 | offscreen=true | | | |
| 7 | probe → nudge → idle | debug_force_probe→回答 → 直後 force_nudge→dismiss | offscreen=true | | | |
| 8 | 連続 probe → idle | debug_force_probe→回答 を素早く2回 → idle | offscreen=true | | | |
| 9 | 起動直後 idle (セッション開始前後) | start_session 直後、何も介入なし | offscreen=true | | | |

各行で widget-show / fullscreen-wall の行 (x/y/w/h) も控えると、box/全画面が正しく配置されたかが分かる。

## 3. 切り分けの早道 (hypotheses.md)

- **#6 (Wall 解除後) でも残存するか?**
  - する → 退避 API 系 (H4/H5) または全 effect 共通の race。probe 固有ではない。
  - しない (Wall は OK で probe だけ残る) → probe 固有 (H1: probeActive 未リセット / H2: 退避↔box 逆 race)。
- **idle-immediate=offscreen=true だが idle-1500ms=false** → H2/H3 (後から上書き)。
- **idle-immediate から offscreen=false** → H1 (idle 分岐未到達=probeActive 残存) か H4 (退避が物理的に無効)。
  - `visible` が true で w/h が box 級 → 統合 effect が idle 分岐に入っていない (probeActive=true のまま) 疑い → H1。
  - `visible` true で setPosition 後も x が ~0 → setPosition(-20000) が clamp/無効 → H4。

## 4. 確定後 (次段)

真因が確定したら Windows で確実に効く修正を入れ、本 command を回帰番兵として残す
(idle で `offscreen=true` を assert するスモーク)。修正確定で v0.1.21 を同 ver 再リリース。
