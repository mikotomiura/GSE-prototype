# 入力データの固定 — experiments/20260816-cv-gate-null

`reproducibility-discipline` ルール 3（入力を hash で固定）/ `data-privacy` Skill。

## 入力

| 項目 | 値 |
|---|---|
| 出所 | Phase1 ユーザー検証の生 NDJSON（**5 名**）。⚠️ **収集期間は書かない** —— 初版は日付範囲を書いていたが、これは生ログの時刻由来の新規開示であり、入力集合は下の `manifest_sha256` で既に固定できている（security-checker LOW） |
| 置き場所 | ⚠️★★★ **repo の外**。★ 実行時に環境変数 **`GSE_PHASE1_NDJSON`** で渡す（⚠️ **絶対パスをリポジトリに書かない** —— OS ユーザー名を含み `leakcheck.py` の漏洩パターンに当たる・security-checker M1） |
| ファイル数 | **63** |
| 合計バイト数 | **61,949,775** |
| ★ manifest sha256 | **`120e1a5e16447449c52c1313a2fa058b99949cc055d42354a3760b26ae50fa3b`** |

★ manifest は `block_variance._input_manifest` が生成する
（**ファイル名を含めず**、`(size, sha256)` を整列して連結したダイジェスト・S5C-D10）。
→ ★ **上流実験 `20260815-expression-power` と同一の入力集合であることが hash で確認できる。**

## 読む項目（★ これしか読まない）

- `type == "meta"` の `session_start`
- `type == "key"` かつ `press == true` の **件数のみ**（★ `vk` の値は 1 度も読まない）
- `t`（相対時刻の窓割り当てにのみ使用）

⚠️ **キーストロークの内容は元データに存在しない**（VK コードのみ）。

## 出力

`results/gate_null.json` —— ★ **集計統計量のみ**。
⚠️ **セッション名・時刻・vk を 1 つも含まない。**

★ **参加者 ID は `P0xx` の形で残る**（★ 上流実験 `20260815-expression-power` の出力と同じ水準）。

- ⚠️★★★ **`notes.md` の表の A–E は「読みやすさのための別名」であって匿名化ではない** ——
  ★ `results/gate_null.json` と値を照合すれば 1:1 で復元できる（security-checker LOW）。
- ⚠️★★★ **公開時は再採番が必須** —— ★ n=5 ＋ 参加者別プロファイルは、
  **ID→被験者の対応表を持つ者にとっては再識別可能**である。
  → ★ **`experiments/` や `docs/` を公開する（論文付録 / repo を public にする）時点で PID を差し替える。**
  ★ 現在 repo は **private**、対応表は研究者が別途管理（`docs/development-guidelines.md §10.2`）。
- ★ **参加者ラベルはコードで検証される** —— ファイル名の先頭断片が `P` + 英数 3–13 桁に
  一致しない場合は `UNK-n` の位置ラベルへ落とす（`gate_null.py`）。
  ⚠️ **初版はファイル名の先頭断片をそのまま書き出しており、実名や端末名を含むファイルが
  1 つ混じれば逐語でコミットされる状態だった**（security-checker MEDIUM）。
  ★ `selftest.py` 検査 6 が負検査として固定している。
