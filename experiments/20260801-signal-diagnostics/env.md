# env — 実行環境の固定

## 実行

```bash
GSE_DATASET=/path/to/gse-dataset ./experiments/20260801-signal-diagnostics/run.sh
```

所要 約 25 秒 (Apple Silicon / n_perm=10000)。

## 環境

| 項目 | 値 |
|---|---|
| OS | macOS (Darwin 25.5.0) / Apple Silicon |
| Python | 3.14.4 |
| 依存パッケージ | **なし (標準ライブラリのみ)** |
| Cargo.lock sha256 (先頭16) | `f45b5eb438beacf3` (`src-tauri/Cargo.lock`) |

`numpy` / `scipy` は**使わない**。この環境に入っておらず、追加すると再現条件が増えるため。
そのぶん C-index の並べ替え検定は密ランクのバケット集計で高速化している
(`FastCIndex`。素朴な O(n^2) 実装との一致を毎回 `self_check()` で検証する)。

## 乱数

| 項目 | 値 |
|---|---|
| seed | `20260801` (`config.json`) |
| 反復数 | `10000` (`config.json`) |
| 乱数源 | `random.Random(seed)` — 単一インスタンスを全セルで共有 |

同一 seed で 2 回実行し `results/diagnostics.json` が **byte-equal** になることを確認済み。

## GSE 固有アンカー

| 項目 | 値 | 取得元 |
|---|---|---|
| HMM_VERSION | `0.3.0` | 入力 NDJSON の `meta.hmm_version` (全 40 件) |
| KAPPA | `2.0` | `features.rs` から抽出 |
| β_writing (F1/F3/F4/F5/F6) | 100.0 / 0.10 / 2.5 / 1.0 / 0.12 | `engine.rs` から抽出 |
| β_coding (F1/F3/F4/F5/F6) | 150.0 / 0.06 / 5.0 / 2.0 / 0.08 | `engine.rs` から抽出 |
| X 合成重み | φ3=0.30 / φ6=0.25 / φ1=0.25 / φ5=0.20 | `engine.rs` から抽出 |
| Y 合成重み | φ4=0.40 / (1−φ1)=0.35 / (1−φ5)=0.25 | `engine.rs` から抽出 |

**定数は Python にハードコードしない。** `extract_constants.py` が Rust ソースから正規表現で
抽出し `constants.json` に書き出す。抽出できなければ `run.sh` は非ゼロ終了する (fail-closed)。
φ の式そのもの (`((x-beta)/(KAPPA*beta)).clamp(0,1)`) が期待形かも検査する。

理由: Python 側に β を書き写すと `engine.rs` を変えたときに診断結果が**黙ってずれる**。
`constants.json` を追跡下に置いてあるので、Rust 側の変更は次回再現時に diff として見える。
