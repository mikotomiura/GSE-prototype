# 実行環境の固定 — experiments/20260812-expression-layer0-drone

`reproducibility-discipline` ルール 2（環境を lockfile で固定）/ ルール 3（GSE 固有アンカー）。

## GSE 側のアンカー

| 項目 | 値 | 出所（一次資料） |
|---|---|---|
| `HMM_VERSION` | **0.3.0** | `src-tauri/src/analysis/engine.rs:45` |
| `EXPR_VERSION` | **0.2.0-step3** | `.steering/20260811-expression-prototype-step0/scripts/expr_smooth.py:59` |
| repo commit（実験開始時） | `abe72dc` | `git rev-parse HEAD` |
| Rust 依存の固定 | `src-tauri/Cargo.lock`（165,794 B / sha256 先頭 `71c0eaf899ac6255`） | 実測 |

⚠️★ **2026-08-12 追記（Step 4 / S4-D3）**: 本実験の**実施時の版は `0.2.0-step3`** である。
Step 4 で `EXPR_VERSION` の SSOT（`expr_smooth.py:59`）が **`0.3.0-step4`** へ上がったため、
★ **`layer0.config.json` の刻印だけを追随させた**（S3-D15 が「凍結しない」と明言した artifact なので
追随は改竄ではない）。⚠️ **本ファイルの実測値は 1 文字も書き換えていない。**

★ `EXPR_VERSION` は **config にも書いてある**（`layer0.config.json`）。
**2 箇所の一致は `scripts/layer0_selftest.py` が検査する**（片方だけ上げると赤くなる）。

## ツールチェイン

| ツール | 版 | 用途 |
|---|---|---|
| rustc | 1.94.1 (e408947bf 2026-03-25) | `gse-replay`（release ビルド） |
| cargo | 1.94.1 (29ea6fb6a 2026-03-24) | 同上 |
| Python | 3.11.9 | ★ **標準ライブラリのみ**（numpy / scipy / soundfile を入れていない） |
| Google Chrome | **151**（Chromium 151） | Web Audio の実行・検算 |
| OS | Windows 11 Home 10.0.26200 | — |

★ **Python の依存追加はゼロなので `requirements.txt` を置いていない。**
（`reproducibility-discipline` ルール 2 は「ランダム要素があれば seed」「環境は lockfile」を求めるが、
★ **固定すべき外部依存が存在しない**。→ **無い理由をここに書く**のが本節の役目である。）

## Web Audio 側の実測値（★ 「たぶんこう」ではなく測った）

| 項目 | 実測 | 意味 |
|---|---|---|
| 既定の `AudioContext.sampleRate` | **48000 Hz** | 実時間再生のレート（デバイス依存） |
| 検算の `OfflineAudioContext` | **8000 Hz × 400 s** | `layer0.config.json` の `selftest` で固定 |
| 包絡の間引き後レート | **200 Hz**（8000 / 40） | Nyquist 100 Hz > 参考線の最大 70 Hz |
| 検算 1 回の所要 | **約 0.9–1.0 s** | 24 通りの掃引でも実用範囲 |

⚠️★ **実時間（48 kHz）と検算（8 kHz）はレートが違う。**
層 0 は 55–110 Hz + 8 次までなので最高 880 Hz、**どちらのレートでも折り返さない**
（`layer0_selftest.py` が「最高次倍音が Nyquist を大きく下回る」を検査している）。
★ ただし **「検算したレートと聴くレートは別である」ことは事実として書いておく。**

## ⚠️ 環境固有の落とし穴（実測で踏んだもの）

1. ★★ **Windows コンソールは cp932**——`—`(U+2014) や `⚠`(U+26A0) を符号化できず、
   Python が **本文 1 行目で `UnicodeEncodeError` を出して落ちた**（実測）。
   → `layer0_selftest.py` は `stdout/stderr` を `errors="backslashreplace"` に設定する。
   `run.sh` は `PYTHONIOENCODING=utf-8` を設定する。
2. ★★ **`file://` では設定ファイルを `fetch` できない**（同一オリジン制約）。
   → `run.sh serve` がローカル HTTP（127.0.0.1）で配る。
   ★ **player は fetch 失敗時に設定ファイルの手動選択へフォールバックする**ので `file://` でも使える。
   ⚠️ ただし **`file://` そのものでの動作は未確認**（本セッションは `http://127.0.0.1:8766` で検証した）。
3. ★★★ **合成クリックでは `AudioContext` が起動しない**（Chrome の autoplay policy）。
   実測: `element.click()` では `ctx.state` が `suspended` のままで、
   **素の `await ctx.resume()` は Promise が解決せず play() が無言で固まった。**
   → **1.2 s で打ち切って画面にエラーを出す形へ修正**し、修正を `layer0_selftest.py` の検査に固定した。
4. ⚠️ **ブラウザのタブが背面／ウィンドウが最小化されていると、実クリックもスクリーンショットも届かない**
   （実測: `visibilityState="hidden"` / `outerWidth=0` / `Page.captureScreenshot` が 30 s タイムアウト）。
   ★ **「クリックしても効かない」を要素の欠陥と誤読しない**（着弾プローブで区別した）。
