# 実行環境の固定 — experiments/20260815-expression-power

`reproducibility-discipline` ルール 2（環境を lockfile で固定）/ ルール 3（GSE 固有アンカー）。

## GSE 側のアンカー

| 項目 | 値 | 出所（一次資料） |
|---|---|---|
| `HMM_VERSION` | **0.3.0** | `src-tauri/src/analysis/engine.rs:45`（実測 grep） |
| `EXPR_VERSION` | **0.3.0-step4** | `.steering/20260811-expression-prototype-step0/scripts/expr_smooth.py:59`（実測 grep） |
| repo commit（実験時） | **`ad697f1`** | `git rev-parse --short HEAD` |
| ブランチ | `docs/media-sound-modality-survey` | 実測 |

⚠️★ **本実験は GSE のコードを 1 行も実行しない。** 検出力計算は設計の算術であり、
`gse-replay` も HMM も回さない。★ **それでも刻印を残すのは、後で
「どの版の設計を前提に計算したか」を復元できるようにするため**である
（★ `HMM_VERSION` が変わっても本計算の数字は変わらない —— ⚠️ **変わるのは前提の方**）。

## ツールチェイン

| ツール | 版 | 用途 |
|---|---|---|
| Python | **3.11.9** (tags/v3.11.9:de54cf5, Apr 2 2024) [MSC v.1938 64 bit (AMD64)] | 全計算 |
| OS | Windows 11 Home 10.0.26200 | — |
| シェル | git-bash（`run.sh`） | 1 コマンド再現 |

### ⚠️★★★ 依存の履歴（★ セッション中に変わったので両方を残す）

```text
2026-08-15 実験開始時（実測）:
  numpy MISSING / scipy MISSING / statsmodels MISSING / pandas MISSING
      ↓ ★ 研究者の指示「必要だと判断するライブラリは積極的に取り入れてよい」（2026-08-15）
2026-08-15 導入後（実測）:
  numpy 2.4.6 / scipy 1.17.1
```

★ **層を分けた**（★ 依存を足しても主結果の再現性を落とさないため）:

| 層 | ファイル | 依存 | 役割 |
|---|---|---|---|
| ★ **主結果（決定的）** | `power_calc.py` | ★ **標準ライブラリのみ** | 到達可能性 / Mann-Whitney 厳密帰無 / 解析式 |
| ★★★ **主結果（検出力）** | `power_mc.py` | **numpy** | ★ **並べ替え検定をそのまま模擬して δ80 を解く** |
| ★ 実測アンカー | `block_variance.py` | ★ **標準ライブラリのみ** | 集計値のみ出力 |
| ★ 自己検査 | `power_selftest.py` | ★ **標準ライブラリのみ** | 43 件 |
| ★★★ oracle 検査 | `oracle_check.py` | **numpy / scipy** | ★ **自前実装を参照実装で突き合わせる**（20 件） |

⚠️★★★ **numpy を入れたことで実際に誤りが 1 件見つかった**（★ 入れる価値がここにあった）——
★ `oracle_check.py` O5 の高精度モンテカルロが、**解析式（σ 既知の正規近似）が検出力を系統的に過大評価する**
ことを示した（★ n=3・B=8・δ=1.0 で **+0.061 = 8 SE**）。
★ 原因: **並べ替え帰無は観測データに条件付き**であり、H1 では処置が観測分散を膨らませて**帰無分布ごと広がる**
（膨張率 `sqrt(1 + Bδ²/(4(B−1)))` = 1.134）。→ ★ **δ80 の主経路をモンテカルロへ切り替えた。**

★ なお `power_calc.py` が自前実装しているもの（★ oracle で全て検証済み）:

| 要るもの | 通常の出所 | 本実験での実装 |
|---|---|---|
| 正規分布の CDF | `scipy.stats.norm.cdf` | `math.erf` |
| 正規分布の分位点 | `scipy.stats.norm.ppf` | 二分法（200 反復） |
| Mann-Whitney 厳密帰無 | `scipy.stats.mannwhitneyu` | 漸化式 `C(m,n,u) = C(m-1,n,u-n) + C(m,n-1,u)` の DP |
| 並べ替え検定 | `scipy.stats.permutation_test` | 全数列挙（`itertools.combinations`）＋ モンテカルロ |

⚠️★★★ **自前実装は「正しいと信じる」わけにいかない。** ★ 2 段で固定している:

1. `scripts/power_selftest.py`（**43 ok / 0 fail**・依存ゼロ）—— ★ **G1 の実測値（C(8,4)=70 / 実質 AUC≈1.0）の再現**、
   **帰無の第一種過誤が厳密値（3/70・12/252）に一致**、**seed 固定で byte-equal**。
2. `scripts/oracle_check.py`（**20 ok / 0 fail**・numpy / scipy）—— ★ **参照実装との突き合わせ**:
   `math.erf` ⇄ `scipy.stats.norm.cdf`（誤差 1.1e-16）／ 二分法 ⇄ `norm.ppf`（5.6e-12）／
   自前 DP ⇄ `scipy.stats.mannwhitneyu(method="exact")`（1.1e-16）／
   ★ **stdlib 実装 ⇄ numpy 実装の検出力が 3SE 以内**。

★ **`requirements.txt` は置いていない**が、⚠️ **numpy 2.4.6 / scipy 1.17.1 が要るのは
`power_mc.py` と `oracle_check.py` だけ**である（★ 版は本ファイルに実測で刻んだ）。
★ **numpy が無い環境でも `run.sh calc` / `anchor` / `selftest` は完走する**（★ `run.sh` が分岐する）。

## ⚠️ 環境固有の落とし穴（★ 実測で踏んだもの・踏まなかったもの）

1. ★★ **Windows コンソールは cp932** —— ★ `run.sh` が `PYTHONIOENCODING=utf-8 PYTHONUTF8=1` を立てる
   （★ layer0 実験で実測済みの既知の穴。本実験では**立てたので踏んでいない**）。
2. ⚠️★★ **`raw/` は gse-dataset の git 管理外**（★ `git status --porcelain raw/` が無出力 = 追跡されていない）。
   → ★ **commit hash では入力を固定できない。**`data.md` の manifest ダイジェストで固定する。
3. ★ **`Cargo.toml` は repo 直下に無い**（`src-tauri/`）—— ★ 本実験は cargo を使わないので無関係だが、
   ★ **引き継ぎ §5-9 の注意事項なのでここに残す。**

## 実行時間（実測）

| 工程 | 時間 |
|---|---|
| `run.sh calc` | 数十秒（★ モンテカルロ 4 セル ＋ 個人水準 20 セル） |
| `run.sh anchor` | 1 秒未満（13 セッション・1.8 MB） |
| `run.sh selftest` | 1–2 分（★ 検査 6/7 が `power_calc.py` を 2 回再実行するため） |
