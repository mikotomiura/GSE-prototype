# 実行環境の固定 — experiments/20260812-expression-step4-grain

`reproducibility-discipline` ルール 2（環境を lockfile で固定）/ ルール 3（GSE 固有アンカー）。

## GSE 側のアンカー

| 項目 | 値 | 出所（一次資料） |
|---|---|---|
| `HMM_VERSION` | **0.3.0** | `src-tauri/src/analysis/engine.rs:45` |
| `EXPR_VERSION` | ★ **0.3.0-step4** | `.steering/20260811-expression-prototype-step0/scripts/expr_smooth.py:59` |
| repo commit（実験開始時） | `abe72dc` | `git rev-parse HEAD` |
| Rust 依存の固定 | `src-tauri/Cargo.lock` | 実測 |

★ **`EXPR_VERSION` は 3 箇所にある**（`expr_smooth.py` の定数 = SSOT / `step4.config.json` /
Step 3 の `layer0.config.json`）。★ **3 箇所の一致は `scripts/step4_selftest.py` が検査する。**
⚠️ **S4-D3 により Step 3 の config も `0.3.0-step4` へ追随させた**——
★ **Step 3 の実験実施時は `0.2.0-step3` である**（`notes.md` の実測値は書き換えていない）。

## ツールチェイン

| ツール | 版 | 用途 |
|---|---|---|
| rustc / cargo | 1.94.1 | `gse-replay`（release ビルド） |
| Python | 3.11.9 | ★ **標準ライブラリのみ**（numpy / scipy / soundfile を入れていない = S4-D7） |
| Google Chrome | **151**（Chromium 151） | Web Audio / AudioWorklet の実行・検算 |
| OS | Windows 11 Home 10.0.26200 | — |

★ **Python の依存追加はゼロなので `requirements.txt` を置いていない。**
S4-D7 に「何が依存を要求しうるか」を洗った表がある。★ **固定すべき外部依存が存在しない。**

## Web Audio 側（★ Step 3 から変えた点を明示する）

| 項目 | Step 3 | ★ Step 4 | なぜ変えたか |
|---|---|---|---|
| 実時間 `sampleRate` | 48000 Hz | 48000 Hz（デバイス依存） | — |
| 検算 `OfflineAudioContext` | 8000 Hz × 400 s | 同じ | — |
| **包絡の間引き** | 40（包絡 **200 Hz**） | ★ **10（包絡 800 Hz）** | ⚠️★ **粒子率 100 grains/s の変調は 100 Hz にあり、Step 3 の設定では包絡 Nyquist ちょうどで測定不能になる。**★ Step 3 が踏んだ「間引きの零点で `+31.7 dB` という嘘の値」を繰り返さないための変更 |
| **層 2** | 無し | ★ **AudioWorklet**（`grain-processor.js`） | 100 grains/s × 600 s = 6 万粒。★ ノード生成ゼロ・メモリ一定にするため（S3-D3 要件 a） |

## ⚠️ 環境固有の落とし穴（Step 3 の実測を継承 ＋ 本 Step で追加）

1. ★★ **Windows コンソールは cp932** —— `—`(U+2014) / `⚠`(U+26A0) で Python が落ちる。
   → `step4_selftest.py` が `stdout/stderr` を `errors="backslashreplace"` に設定。
   `run.sh` が `PYTHONIOENCODING=utf-8` を設定。
2. ★★★ **`file://` では動かない（Step 3 より厳しい）** ——
   Step 3 は設定 `fetch` だけが落ちてフォールバックがあったが、
   ★ **本 Step は `audioWorklet.addModule()` も同一オリジン制約に当たる**ので、
   **`file://` では層 2 が鳴らない。** → ★ **必ず `bash run.sh serve` で開く。**
   ★ player は読み込み失敗を**画面に出す**（無言で固まらない）。
3. ★★★ **合成クリックでは `AudioContext` が起動しない**（Chrome の autoplay policy）。
   ★ **実クリックが要る。**
4. ⚠️ **ブラウザのタブが背面／ウィンドウが最小化されていると、実クリックもスクショも届かない**
   （`visibilityState="hidden"` / `outerWidth=0`）。
   ★★ **Step 3 の B4（停止・音量が実際に効くか）が未実測のまま残ったのは、これが原因である。**
5. ⚠️ **`await ctx.resume()` を素で待たない**（無言で固まる）。1.2 s で打ち切って画面に出す。

## ★ 本 Step で使ったポート

- **8732**（`run.sh serve` の既定）。★ **ローカルのみ**（`--bind 127.0.0.1`）。
- ⚠️ **Step 3 のサーバ（8766）が前セッションから生きたままである**（本セッション開始時に実測 200）。
  ★ **私が立てたものではないので止めない。** 止めるなら `pkill -f "http.server 8766"`。
