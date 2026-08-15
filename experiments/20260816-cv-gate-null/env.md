# 実行環境の固定 — experiments/20260816-cv-gate-null

`reproducibility-discipline` ルール 2。

| 項目 | 値 |
|---|---|
| OS | Windows 11 Home 10.0.26200 |
| Python | **3.11.9** |
| numpy | **2.4.6** |
| scipy | **1.17.1** |
| seed | `SEED` ファイル（**20260816**）。★ 使用箇所はブートストラップ再抽出のみ（MLE は決定的） |
| HMM_VERSION | `0.3.0`（`src-tauri/src/analysis/engine.rs:45`）。⚠️ **本実験は HMM 出力を使わない**ので結果に影響しない |
| Rust | ★ 使わない（`Cargo.lock` は本実験の再現に無関係） |

## ⚠️ numpy / scipy を使う理由（★ 上流実験は標準ライブラリのみだった）

★ **左側打ち切り最尤法**（`scipy.optimize` / `scipy.stats.norm.sf`）が要る。
⚠️★★★ **自前の解析式で済ませない方針は 2026-08-15 の実測に基づく** ——
姉妹実験で **解析式による検出力が系統的に楽観側へ 8 SE 外れており、
numpy/scipy の参照実装と突き合わせて初めて判明した**
（`.steering/_handoff/next-session-prompt-mhd-improvement-and-scope.md` §9-1 の 2 番）。
→ ★ **ライブラリを入れてよい（研究者の許可・2026-08-15）。★ 独立実装で突き合わせる。**
★ 本実験でも **MLE と打ち切りモーメント法の 2 経路**で当てはめを検算している
（`gate_null.moment_check`・相対誤差 0.2–3.5%）。

## 再現

```bash
export GSE_PHASE1_NDJSON=<Phase1 生 NDJSON のディレクトリ>   # ★ repo 外
bash experiments/20260816-cv-gate-null/run.sh
```

⚠️★★ Windows コンソールは cp932 —— `run.sh` が `PYTHONIOENCODING` / `PYTHONUTF8` を立てる。

## 漏洩検査

```bash
python .steering/20260811-expression-prototype-step0/scripts/leakcheck.py experiments/20260816-cv-gate-null
# -> 絶対パスらしき出現: 0 / ユーザー名: 0（2026-08-16 実測）
```
