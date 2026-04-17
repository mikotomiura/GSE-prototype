# 設計案比較

## v1 の要旨

- sync-all.ps1 と sync-all.sh の **それぞれに Step 0 を直接埋め込む**。
- 比較は **SHA-256 ハッシュ**で byte-equal を厳密に評価。
- PS 5.1 の BOM quirk 回避のため `Get-FileHash` を採用、bash 側は
  `sha256sum` / `shasum` をフォールバック。
- drift 時は diff 先頭 20 行 + 修復手順を表示し、新 exit code 5 で停止。
- テストは手動（dry-run でドリフト再現・不在ケース再現・通常ケース）。

## v2 の要旨

- schema 比較ロジックを **`scripts/check_schema_parity.py`** に集約。
  sync-all.ps1 / sync-all.sh は helper を 1 行で呼ぶだけ。
- 比較は **JSON 意味同値**（`json.load` + `sort_keys` 正規化）。CRLF/LF や
  末尾 newline の揺れは drift として扱わない。enum variant の diff 分析
  (missing / extra) を出力。
- ドキュメント規約は gse-dataset 側の `validate_schema.py` と揃える
  (shebang / argparse / pathlib)。
- Python helper に **unittest** を付け、shell 側は呼び出しの exit-chain
  だけなので手動回帰テストで済む。

## 主要な差異

| 観点 | v1 | v2 |
|---|---|---|
| アプローチ | shell 2 言語に別実装を埋め込む | Python 1 本に集約、shell は呼ぶだけ |
| 比較粒度 | byte-equal (SHA-256) | JSON 意味同値 |
| CRLF/BOM 耐性 | 厳格に不一致扱い → Windows 環境で誤 FAIL リスク | 揺れを吸収 (false positive 回避) |
| 変更規模 | shell 2 本 + docs | Python 1 本新規 + shell 2 本 1 行追加 + unittest + docs |
| テスト戦略 | 手動のみ | Python helper は自動 (unittest) + shell は手動 |
| ドリフト方向の診断 | diff 出力のみ | "missing variants" / "extra variants" で人間可読 |
| 依存追加 | なし | Python (ただし既に gse-dataset 側で常用) |
| 拡張性 | shell 2 本を毎回編集 | Python 側を変えれば自動で両 shell に反映 |
| 将来 tier-1 チェック追加 | ps1/sh に更に分岐を増やす必要 | helper 内にフラグ 1 つ増やすだけ |
| 実装行数 (見積) | shell +80 行 × 2 + docs | Python ~60 行 + shell +10 行 × 2 + unittest +80 行 + docs |
| 初期実装コスト | 低 (単純) | 中 (Python + test 併設) |
| メンテ負荷 | 高 (2 言語同期必須) | 低 (1 ヶ所集約) |
| リスク | Windows BOM/CRLF の誤検出で本番停止 | Python 未存在環境での動作 (実運用では validate_schema.py で既に要求されており同等) |

## 推奨案

**v2 を推奨**。根拠:

1. **将来の編集での drift リスクが最小**。ps1 と sh に同じアルゴリズムを
   書くのは、本タスクが防ごうとしている「2 ヶ所の同期を忘れる」問題と
   **全く同じ構造**を新たに生み出す皮肉がある。v2 はこの再帰を断つ。
2. **CRLF/BOM 誤検出リスクが排除される**。v1 のハッシュ厳格比較は、
   impact-analyzer が指摘した通り Windows 環境で high-risk。「drift
   じゃないのに drift と言う」pre-flight はすぐ無視されて形骸化する。
3. **回帰テストを自動化できる**。Python helper 単体ならテストを書く
   コストが低く、将来の編集で挙動が壊れにくい。
4. **拡張コストが線形**。将来 tier-1 チェックを足したい、variant 追加の
   向き (backward compat か否か) を判定したい、などの拡張が 1 ヶ所で完結。

v1 が勝る唯一の観点は「今この瞬間の実装コストが低い」だが、この検査は
CI 代替として **長期運用される想定**であり、初期実装よりメンテ負荷を
優先すべき。

---

**採用選択:**
1. v1 — shell 埋め込みで最速実装
2. v2 — Python helper に集約（推奨）
3. ハイブリッド — 具体的に指定してください
4. 再生成 (残り 2 回)
