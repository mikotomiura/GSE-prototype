# 実行環境の固定 — experiments/20260902-expression-layerA-visual

`reproducibility-discipline` ルール 2（環境を lockfile で固定）/ ルール 3（GSE 固有アンカー）。

## GSE 側のアンカー

| 項目 | 値 | 出所（一次資料） |
|---|---|---|
| `HMM_VERSION` | **0.5.0** | `src-tauri/src/analysis/engine.rs:58`（実測 2026-09-02） |
| `EXPR_VISUAL_VERSION` | ★ **0.1.0-layerA** | `layerA.config.json` `expr_visual_version`（★ 本実験で新設） |
| repo commit（実験開始時） | `735e8df` | `git rev-parse --short HEAD` |

⚠️★★★ **`EXPR_VERSION`（音側・`0.3.0-step4`）とは別系統である。**
★ 音側は `experiments/20260812-expression-*` が持つ。★ **混ぜない。**
★ ADR-021 は「`EXPR_VERSION` は動かない」と決めたので、**視覚側は別の版キーを立てた。**

## ツールチェイン

| ツール | 版 | 用途 |
|---|---|---|
| Python | **3.11.9** | `scripts/selftest.py` / `python -m http.server`（★ **標準ライブラリのみ**） |
| Google Chrome | **151.0.7922.175** | Canvas 2D の実行・画素の検算 |
| OS | Windows 11 Home 10.0.26200 | — |
| rustc / cargo | 1.94.1 | ★ **本実験では使わない**（Rust コードに触れない） |

★ **Python の依存追加はゼロなので `requirements.txt` を置いていない。**
★ 使っているのは `json` / `re` / `sys` / `pathlib` / `tempfile` / `copy` / `io` / `contextlib` のみ。

⚠️★★★ **Windows の既定 stdout は cp932 で、`–`（U+2013）等が `UnicodeEncodeError` で落ちる。**
★ 2026-09-02 に実測して踏んだ。→ `selftest.py` 冒頭で `sys.stdout.reconfigure(encoding="utf-8")` する。
★ **検査が「赤」ではなく「例外」で死ぬのが最悪なので、先に潰してある。**

## ⚠️ 環境が結果に効く箇所（★ 隠さない）

| # | 何 | なぜ効くか |
|---|---|---|
| **1** | ⚠️★★★ **物理較正**（px/mm・視距離） | ★ **「視角 1°」は較正なしに意味を持たない。** ★ ハーネスは較正を通すまで試行を開かない |
| **2** | ⚠️ **ディスプレイの画素密度** | ★ 1° が何 px になるかが変わる。★ 本機では **1° = 39.52 px**（カード合わせ 323 px / 視距離 600 mm・実測） |
| **3** | ⚠️ **`devicePixelRatio`** | ★ 書き出し JSON に記録する。★ 本機の実測値は結果ファイル側にある |
| **4** | ⚠️ **ディスプレイのガンマ・輝度** | ★ 明度が唯一の符号なので効く。⚠️ **統制していない。限界として記録する** |
| **5** | ⚠️★★★ **ブラウザは実機のロック画面ではない** | ★ 下記参照 |
| **6** | ⚠️★★★ **窓の幅**（★ 2026-09-08 追加） | ★ **周辺視ブロック（§7）が開くかどうかが変わる。**★ 片側に `偏心 px + 刺激の半幅 + 8 px` が要る。★ 実測: **幅 958 px / 視距離 600 mm では不可**（必要 583 px > 利用可能 479 px）／ **視距離 400 mm なら可**（451 px ≤ 479 px）。→ ★ **全画面に近い窓で回すこと** |
| **7** | ⚠️★★★ **フレームレート**（★ 2026-09-08 追加） | ★ **周辺視の提示は 150 ms（60 Hz で 9 フレーム）**しかないので、**フレーム落ち 1 回で提示が 1 割変わる**。⚠️ **他タブ・他アプリを止めて回すこと**。⚠️★★★ **タブが背面にあると `requestAnimationFrame` は完全に止まる**（★ 2026-09-08 実測: 1.5 秒で 0 フレーム）—— ★ **必ず前面で回す** |

## ⚠️★★★ 実機との差（★ 最大の限界）

★ **本ハーネスは PC のブラウザ上の 360×360 の正方領域で提示する。実機のロック画面ではない。**
★ 2026-09-02 の一次調査（`.steering/20260902-expression-layer-os-constraints/survey-os-constraints.md`）で、
**実機はハーネスより符号が痩せる**ことが分かっている:

| # | 実機で起きること | 一次 |
|---|---|---|
| **1** | ⚠️★★★ **iOS はロック画面ウィジェットを強制的に monochrome にする** | 逐語 *"The system **desaturates** the widget, making a **monochrome** version"* |
| **2** | ⚠️★★★ **AOD ではアニメーションが実行されない** | 逐語 *"**On devices that include an Always-On display, the system doesn't perform animations**"* |
| **3** | ⚠️★★★ **ウィジェットは連続更新を支持しない** | 逐語 *"**Widgets don't show real-time information.**"* ／ *"timeline entries that are **at least about 5 minutes apart**"* |
| **4** | ⚠️★★★ **円形ウィジェットは 2.26° 幅しかない** | ★ 公式寸法 76×76 pt ＋ 視距離 300 mm・163 pt/inch の仮定（⚠️ **後 2 者は一次で確認していない仮定**）→ ★ **1° の全振幅はその 44% を動かす** |

→ ★★★ **本ハーネスで A-7 が読めても、それは「実機で読める」ことを意味しない。**
★ 逆に **本ハーネスで読めなければ、実機ではより読めない**（★ こちら向きの推論だけが安全である）。
