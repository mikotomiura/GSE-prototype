# blockers — Step 4（層 2 粒子 ＋ 混同テスト）

## BL-1 ✅ **解除済み**（2026-08-12）— B4（停止・音量が実際に効くこと）が 3 セッション連続で測れていなかった

> ★★★ **解除**: 研究者が Chrome ウィンドウを復元して前面に置いた直後、
> `visibilityState="visible"` / `hasFocus=true` / `outerWidth=1280` を実測し、
> **B4 の 4 条件すべてを実測で PASS**（`experiments/20260812-expression-step4-grain/notes.md` §3.9）。
>
> ⚠️ ★ **機械側では解除できなかった。** `resize_window` は `Successfully resized` を返すが
> `outerWidth=0` / `visibilityState="hidden"` のままで、タブグループを開き直しても
> **新しいウィンドウがまた最小化で開いた**（2 回とも）。**人の操作が要る。**
>
> ★ 以下は経緯として残す（同じ形で詰まらないため）。

### 現況

| 回 | いつ | 結果 |
|---|---|---|
| 1 | Step 3（2026-08-12 未明） | ⚠️ 未実測。Chrome ウィンドウが最小化 |
| 2 | Step 4 前半（同日・PC 断で中断） | ⚠️ 未実測。`visibilityState="hidden"` / `outerWidth=0` を実測（`notes.md` §5-1） |
| 3 | Step 4 後半（2026-08-12 昼） | ⚠️ 未実測。**同じ条件が再現**（下記） |

### ★ 3 回目の実測値（2026-08-12・Windows 11 / Chrome）

```json
{"visibilityState":"hidden","hasFocus":false,"outerWidth":0,"outerHeight":0,
 "innerWidth":1264,"innerHeight":910,"hasStep4":"object"}
```

- ★ `innerWidth/innerHeight` は正常値を返すのに `outerWidth/outerHeight` が **0**。
  → **ウィンドウは存在するが最小化されている**（Windows の最小化ウィンドウの挙動）。
- ★ `mcp__claude-in-chrome__resize_window` は **`Successfully resized` を返すが直らない**（実測）。
  `innerWidth` は 958 → 1264 に変わったが、`outerWidth` は 0 のまま・`visibilityState` も `hidden` のまま。
  → ⚠️ **このツールの成功応答を「ウィンドウが前面に出た」と読んではならない。**
- ★ タブグループを開き直しても**新しいウィンドウがまた最小化で開く**（2 回とも同じ）。

### なぜ飛ばせないか

`media-expression-spec.md` §5 要件 1（**交渉不可**）＝「ユーザーが止められる／音量を変えられること」。
根拠は [P71]（26 週フィールド）で、**制御できない連続音は主観的 well-being をむしろ低下させる**。
★ **常時鳴らす形（案 α）はこの要件の上にしか成立しない。**

⚠️ **合成クリック（`element.click()` / `dispatchEvent`）では代替にならない。**
autoplay policy 下では `AudioContext` が `suspended` のままになり、
「押しても鳴らない」が**仕様どおりの挙動として出てしまう**ため、
「本当にブロックされた」と「そもそも操作が届いていない」が区別できない
（`browser-verification` §2.0 の否定的テストの罠そのもの）。

### ★ 解除の条件（研究者の操作が要る）

1. タスクバーから **「GSE 表現層 Step 4 — 層 2（粒子）＋ 層 0 の自律変異」** の Chrome ウィンドウを復元する
2. ★ **他のウィンドウを前面に重ねない**（重ねると `visibilityState` が `hidden` に戻る）
3. → `visibilityState="visible"` / `outerWidth>0` を実測してから測定を始める

### ★ 測定の設計（ウィンドウさえ出れば自動で測れる。合格条件は先に確定済み）

| # | 合格条件 | 測り方 |
|---|---|---|
| B4-0 | 実クリックが着弾している | `window.__hits`（`mousedown` を capture で記録）が空でないこと。★ **空なら座標系の問題であって要素の問題ではない** |
| B4-1 | **対照**: 鳴ること | 「鳴らす」実クリック後に `__step4.rms() > 0`。★ **これが出ないと B4-2 は何も言えない** |
| B4-2 | ★ 止まること | 「止める」実クリック後、rms が減衰して ≈0 → `playing===false` → ctx closed |
| B4-3 | ★ 音量が変わること | スライダ実操作で `masterGain` **かつ実出力 rms** が同方向に動く（目標値だけを見ない） |
| B4-3b | ★ フェードイン窓でも効くこと | 再生開始 **4 秒以内**に動かして、数秒後に元へ戻らないこと |

⚠️ **停止は 0.4 s ランプ → +0.15 s で `ctx.close()` し、`analyser` が `null` になる**
（`step4.html` の `stop()`・`CFG.envelope.fade_out_s=0.4`）。
→ ★ **クリック前に 50 ms サンプラを仕込んで軌跡を取る。** 停止後に 1 回だけ読むと
`rms()` が `null` を返し、「止まったから 0」と**区別できない**。

### ★ 次に同じ形で詰まらないために

- ★ **ブラウザ検証を含む Step は、最初に `visibilityState` / `outerWidth` を実測してから始める**
  （`browser-verification` §2.0b の着弾プローブより手前の関門）。
- ★ **引き継ぎに「Chrome を前面・非最小化に」と書くだけでは 3 回とも効かなかった。**
  → 機械側で**先に実測して止まる**形にした（本セッション）。この形を次 Step でも維持する。
