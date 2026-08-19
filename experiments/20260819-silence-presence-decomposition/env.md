# 実行環境の固定 — experiments/20260819-silence-presence-decomposition

`reproducibility-discipline` ルール 2。

| 項目 | 値 |
|---|---|
| OS | Windows 11 Home 10.0.26200 |
| Python | **3.11.9** |
| numpy | **2.4.6** |
| scipy | **1.17.1**（★ `requirements.txt` に固定。⚠️ **本実験の主経路は numpy のみで動く**——`scipy` は上流 `block_variance` の import 連鎖のために揃えてある） |
| seed | `SEED` ファイル（**20260819**）。⚠️★ **使用箇所は自己検査の合成データ生成のみ**。★ **本解析（抽出・記述・LOSO）は完全に決定的**で seed に依存しない |
| HMM_VERSION | **`0.4.0`**（`src-tauri/src/analysis/engine.rs:58`）。⚠️★ **本実験は HMM 出力を 1 バイトも使わない**（`key` / `hook_health` の生レコードのみ）ので結果に影響しない。★ 刻むのは来歴のためである |
| Rust | ★ 使わない（`Cargo.lock` は本実験の再現に無関係）。⚠️ ただし **`src-tauri/` のコードは仕様の参照元**なので、`liveness.rs` / `lib.rs` を変更したら本実験の前提を再確認すること |
| 上流スクリプト | `experiments/20260815-expression-power/scripts/block_variance.py` の `window_counts` / `_input_manifest` を **import して再利用**（★ 窓の切り方を再発明しない） |

## ⚠️ 依存している `src-tauri/` の実装（★ 変わったら本実験は無効になる）

| 参照先 | 依存している事実 |
|---|---|
| `src/input/liveness.rs:86-103` | `step()` の 3 分岐（打鍵でリセット / 入力皆無で凍結 / それ以外で加算） |
| `src/input/liveness.rs:63-66` | `log_after_ms: 30_000` / `down_after_ms: 120_000` |
| `src/lib.rs:2923` | `if health == prev_health && !rehook { continue; }`（状態変化時のみ出力） |
| `src/lib.rs:2951-2956` | 復帰行が `peak_starved_ms` を搬送する |
| `src/lib.rs:2914` | `Down` 到達で `request_reinstall()` を 1 エピソード 1 回だけ呼ぶ |
| `src/lib.rs:2832` | `TICK_MS = 1000` |
| `src/logger.rs:1310` | `key` 行の形（`t` / `vk` / `press`） |
| `src/logger.rs:1393` | `hook_health` 行の形（`t` / `alive` / `starved_ms` / `rehook` / `dropped`） |
| `src/bin/replay.rs:428` | `is_backspace(vk) = vk == 0x08 \|\| vk == 0x2E` |

⚠️★★ **これらは「記録の仕様」であって「実験のためのインタフェース」ではない。**
★ 将来 `hook_health` の出力条件やしきい値が変わったら、**本実験の結果は再計算が要る**
（旧ログと新ログを混ぜてはならない）。

## 再現

```bash
export GSE_PHASE1_NDJSON=<Phase1 生 NDJSON を置いたディレクトリ>   # ★ repo 外
bash run.sh
```

★ `run.sh` は次の順で走り、**どこかで落ちたら結果を書かない**:
自己検査 → 抽出 → 入力 manifest の照合 → L1/L2 記述 → L3 → 漏洩検査。
