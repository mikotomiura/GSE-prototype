# 沈黙の 2 成分分解 — 在席×非打鍵 / 入力皆無

**問い**: 打鍵が沈黙している区間は「**在席×非打鍵**」と「**入力皆無**」にどう分かれ、
その区別は**打鍵の再開**を予測するか。

⚠️★★★ **探索トラック**である（適格性ゲート `keydown ≥ 100` を適用しない）。
**本実験の結果は確証主張に一切使わない。**
→ 位置づけの正本は `preregistration.md §0` と
`.steering/20260819-low-typing-window-discrimination/decisions.md` **D-3 / D-4**。

## 何が新しいか

★ `src-tauri/src/input/liveness.rs` の `starved_ms` は、
**「沈黙のあいだ入力デバイスに触れていた累積時間」**そのものである
（`step()` は system 入力ありかつ打鍵なしでのみ進み、入力皆無では凍結する）。
→ ★★★ **既存の `hook_health` 行だけで、沈黙を 2 成分に分解できる。**
**新規 sensing ゼロ・privacy 境界の再検討ゼロ・`src-tauri/` のコード変更ゼロ。**

⚠️ これは `liveness.rs` が**誤検知として仕様固定した挙動**
（テスト名 `mouse_only_work_is_a_known_false_positive`）を、**信号として使い直す**ものである。
用途の転用であることを `preregistration.md §9-5` に明記している。

## 3 層

| 層 | 問い | モデル依存 |
|---|---|---|
| **L1** | 沈黙ギャップの成分分布（被験者別） | ★ 無し |
| **L2** | ⚠️★★★ **5 分窓の時間内訳。特に `keydown < 100` で除外される窓の中身** | ★ 無し |
| **L3** | presence は T0 に対して増分を持つか（2 基線への勝ち幅） | あり |

★ **`§0` の問い「打鍵が無い窓で何が起きているか」に答えるのは L2 であって L3 ではない。**
L3 が全滅しても L1 / L2 の結論は残る。

## 実行

```bash
export GSE_PHASE1_NDJSON=<Phase1 生 NDJSON を置いたディレクトリ>   # ★ repo 外
bash run.sh
```

⚠️ 入力パスは repo に書かない（OS ユーザー名を含むため）。
`run.sh` は入力の `manifest_sha256` を検査し、上流実験と別のデータなら **exit 3** で止まる。

## ファイル

| ファイル | 役割 |
|---|---|
| `preregistration.md` | ★ **実データを見る前に凍結**した仮説・判定基準・除外規則・Stop 条件 |
| `config.json` | 閾値（★ コードに埋めない） |
| `data.md` | 入力の来歴（manifest sha256）と限界 |
| `env.md` | 実行環境 |
| `scripts/extract.py` | NDJSON → ギャップ表 ＋ 窓の時間内訳 |
| `scripts/describe.py` | L1 / L2（model-free） |
| `scripts/analyze.py` | L3（離散時間ハザード・LOSO・上下界・120 秒副解析） |
| `scripts/selftest.py` | ★ **本解析より先に回す**自己検査 |
| `scripts/leakcheck.py` | 漏洩検査（OS ユーザー名 / 絶対パス / ファイル名形式） |
| `notes.md` | 結果と限界 |
