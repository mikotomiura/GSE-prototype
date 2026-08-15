# 入力データの固定 — experiments/20260816-cv-gate-null

`reproducibility-discipline` ルール 3（入力を hash で固定）/ `data-privacy` Skill。

## 入力

| 項目 | 値 |
|---|---|
| 出所 | Phase1 ユーザー検証の生 NDJSON（**5 名**・2026-06-29 〜 2026-07-30） |
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
⚠️ **セッション名・ファイル名・時刻・vk を 1 つも含まない。**
★ 参加者 ID は `P0xx` の形で残る（★ 上流実験の出力と同じ水準。⚠️ **本 notes.md の表では A–E に匿名化した**）。
