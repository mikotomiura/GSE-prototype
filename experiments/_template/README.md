# `experiments/_template/` — 解析テンプレート

★ 新しい実験を始めるときは、このディレクトリを
`experiments/<YYYYMMDD>-<exp-name>/` へコピーして書き換える。

規約の SSOT は `docs/experiment-tracking.md`、発火層は `reproducibility-discipline` skill。

## ⚠️★★★ `run.sh` の Step 0 を消さないこと (ADR-013 Migration 4)

`run.sh` の **Step 0 は `scripts/capabilities_gate.py`** である。
これは「収集済み信号を使う解析は、**最初に `capabilities` を機械判定する**」という
規約を、⚠️ **人の手順ではなくコード**にしたものである。

★ ADR-013 自身の診断は逐語で「**規約は書いてあったのに適用しなかった**」であり、
「計器がコホートを跨げなかった」失敗は既に **2 件**起きている:

1. `keys` / `bs_keys` の配線は 2026-08-16。⚠️ Phase1 ログはそれ以前なので**存在しない**。
2. `hook_health` / `starved_ms` は Phase1 コホート (63 ファイル) に **1 行も無い**
   (記録 2026-07-04〜07-24 に対し `liveness.rs` の追加は 2026-08-09 = **収集の 16 日後**)。

⚠️ **どちらも「0 行 = 信号が無かった」と読んでしまったことが原因**である。

## ★ 判定表 (3 群 ＋「表に無い」)

| 群 | 0 行の意味 |
|---|---|
| `unconditional` | ★ **信号が無かった** (測れて、無かった) |
| `threshold_gated` | ⚠️ **判定不能** (閾値未達と区別できない。例: `hook_health` / `starve_window`) |
| `config_gated` | ⚠️★★★ **判定不能** (設定で送出元ごと止まっていた。例: **G1 では probe 系が常に 0 行**) |
| どれにも無い | ⚠️ **計器が無かった** (★ 過去 2 件の失敗はここ) |

⚠️ **旧ログには `capabilities` キー自体が無い** → ★ 「**計器が無かった**」に倒す。
⚠️ 新旧が混ざったコホートは **`MIXED` で止める** (★ 平均を取る前に止める)。

## ファイル

| ファイル | 役割 |
|---|---|
| `run.sh` | 再現のエントリ。★ **Step 0 = capabilities gate** |
| `config.yaml` | 全ハイパーパラメータ (HMM 閾値・α・β・ゲート定数) |
| `SEED` | 乱数 seed (固定) |
| `data.md` | 入力 NDJSON の version/hash と被験者/OS (gse-dataset の commit hash) |
| `env.md` | 環境固定 (Cargo.lock / rustc version / OS / requirements.txt) |
| `results/` | 生成物 (`capabilities.json` / `metrics.json` / `calib.json` 等) |
| `notes.md` | 所感・逸脱 ＋ 仮説 (`research-positioning.md §5`) と PreReg 番号へのリンク |

## ⚠️ 使うときの注意 (★ 実測で踏んだもの)

1. ⚠️★★ **`Cargo.toml` は repo 直下に無い** (`src-tauri/`)。
   `cd src-tauri` するか `--manifest-path` を付ける。
2. ⚠️★★ **Windows コンソールは cp932** → Python は **`PYTHONUTF8=1`** を必ず付ける。
3. ⚠️★★ **`| tail` にパイプしない。** `$?` が tail のものになり**赤を見落とす**
   (`.steering/20260819-g1-reboot-and-instrument-fix/blockers.md` B-3)。
   → **リダイレクトしてから `echo $?`**。
4. ⚠️ **NDJSON 生ログ・キーストローク内容はコミットしない** (`data-privacy` SSOT)。
   共有は集計 JSON のみ。
5. ⚠️★★★ **`results/capabilities.json` にファイル名は入らない**
   (security-checker HIGH・2026-08-21)。★ 実データのファイル名は
   **擬似 ID ＋ セッション開始時刻そのもの** (`P010_gse_20260629_073659.ndjson`) であり、
   ⚠️ `.gitignore` は `results/*.json` を**塞いでいない** (「集計 JSON はコミット可」)。
   → ★ JSON には不可逆な `file_id` だけが入り、実名は**端末表示 (stderr) にだけ**出る。
   ⚠️ **その stderr をコミットする先へリダイレクトしないこと。**
