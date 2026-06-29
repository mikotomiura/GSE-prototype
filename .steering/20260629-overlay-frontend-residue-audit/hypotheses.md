# 仮説: なぜ幾何退避が Windows で効かなかったか (要・実機計測で検証)

対象コード: `src/components/Overlay.tsx` の統合 effect (origin/main = リリース版)。
idle 分岐は概ね L184-205、show(widgetOnly) 分岐は L207-235、applyFullscreenBlock は L154-172。
**いずれも推測。次セッションは計測 (窓位置/サイズ/ignoresMouseEvents の読み返し) で白黒つけること。**

## H1: probeActive が idle へ戻っていない (effect が再実行されず box のまま残存)
- ProbeCard 回答/スキップ後に `onActiveChange(false)` が呼ばれず `probeActive` が true のままだと、
  `visible` が true のまま → 窓は右上 box (390x430)・interactive=true で残存し、box 領域が
  クリックを奪う。Windows はクリック透過が効かないので box 残存＝即クリック奪取。
- 検証: ProbeCard.tsx の dismiss/answer 経路が必ず `onActiveChange(false)` を発火するか。
  回答後に `probeActive` state がログ上 false になるか。
- 該当: `src/components/ProbeCard.tsx`、Overlay.tsx L71 `probeActive` / L353 `onActiveChange`。

## H2: 退避と show の逆 race (in-flight な box 配置が退避を後から上書き)
- probe→idle 遷移で旧 show effect が cancelled になるが、**既に発行済み**の
  `setPosition(右上)` / `setSize(box)` が、新 idle effect の `setPosition(-20000)` より後に
  OS へ着地すると、窓は box (オンスクリーン) に戻る。cancelled ガードは「次の発行」しか止めない。
- D7 (FIFO 依存) の現実化。Windows の IPC タイミングで起きやすい可能性。
- 検証: 退避の setPosition 発行後に**読み返し**て -20000 か box かを確認。box なら本仮説濃厚。

## H3: 退避後に別 effect が再 show / 再配置
- 連続するランダムプローブ、nudge effect (L297-)、または初回マウント effect (L135-137,
  `setOverlayInteractive(false)` のみだが) や `currentWindow` 依存の再実行で、退避直後に
  窓がオンスクリーンへ戻る。
- 検証: idle 確定後、次に窓位置を変える呼び出しがどの effect から来るかをログで追跡。

## H4: Windows で setPosition(-20000,-20000) が実際には退避していない
- always_on_top + skip_taskbar の borderless 窓で、Windows が負座標を clamp する / WebView2 子
  HWND が親と一緒に動かない、等。capability (`allow-set-position`/`allow-set-size`) は両 OS 付与済
  なので permission 落ちではないはず。
- 検証: 退避直後に `outerPosition()`/`outerSize()` を読み返し、実値が (-20000,-20000)/(1,1) か。
  clamp されていれば本仮説。

## H5: setSize(1,1) が Windows 最小サイズに clamp され、かつ setPosition も無効で box 残存
- Windows は WM_GETMINMAXINFO で最小窓サイズを強制しうる。1x1 が例えば数十px に clamp されても、
  位置が画面外なら無害。だが H4 と複合で「位置も効かず・サイズも残る」なら box 級の残存になる。

## 最有力の見立て (要検証)
**H1 か H2** が濃厚。理由: 症状が「**ランダムプローブによる**」idle 残存と特定されている =
probe→idle 遷移固有。記録は健全 (probe 3/3 ラベル) なので probe の表示/回答までは正常、
**回答後に idle へ畳む段**で box が残っている疑い。H4/H5 は「退避 API 自体が効かない」系で、
もしそうなら Wall 解除後も同様に残るはず → Wall 後の挙動を比較すると H1/H2 と切り分けできる。

## 厳密判定のための計装 (次セッションで実装)
1. **Rust に窓状態読み返し debug command を追加** (先行タスクで defer した番兵を、今度は *位置/サイズ*
   で実装): `outerPosition`/`outerSize`/`ignoresMouseEvents`(macOS)/WS_EX_TRANSPARENT(Windows) を返す。
   `ensure_debug_enabled()` ゲート下 (lib.rs L201)。
2. **Overlay.tsx の各遷移直後に上記を読み返してログ** (VITE_GSE_DEBUG 下、fe_dbg→tracing 様式。
   D13 で実績ある計装手法)。idle 確定後の実位置を一次情報で確認。
3. 状態行列で網羅: {probe-answer, probe-skip, nudge-dismiss, nudge-silent, wall-unlock,
   probe→nudge, 連続probe} × 各遷移後 idle の実窓位置。
4. 真因確定後に修正 → 同 debug command で回帰番兵化。

## 切り分けの早道
- Wall 解除後 idle で残存するか? する → 退避 API 系 (H4/H5) か全 effect 共通の race。
  しない → probe 固有 (H1/H2)。
- idle 確定の数秒後にもう一度窓位置を読む: 直後は -20000 だが後で box に戻る → H2/H3 (上書き)。
  最初から box → H1 (idle 分岐未到達) か H4 (退避無効)。
