# 設計 —— P1 事前宣言 v1.1

## アプローチ

`docs/preregistration-p1-episode.md` の冒頭（ステータス行と「承認済み」行の直後）に、独立した引用ブロック
「**v1.1 改訂宣言（2026-09-26・再凍結 / 値は不変）**」を**挿入するだけ**にする。本文 §0〜§5 と既存の冒頭行は 1 文字も変えない（判断 2）。

ブロックは次を持つ:
1. 版の同定（v1.0 = 2026-09-25・`f5163a6`／v1.1 = 本宣言）と「実データを見る前に決めた」の明記
2. 上書き・追補 5 点（判断 4 の 1+2 / 3 / 4 / 6）。それぞれ「本文のどこを」「一次のどれで」を名指しする
3. 凍結 JSON を `1.0.0` に据え置く理由（判断 3）
4. 入れなかったもの（P1-A・PG-1・D9・E1）

## 変更対象

- `docs/preregistration-p1-episode.md`（追加のみ）
- `.steering/20260926-prereg-p1-episode-v1-1/*`

## 変更しないもの

- `src-tauri/prereg/p1-episode.json`・`src-tauri/**`・`scripts/check_prereg_parity.py`
- ADR-030（判断 5）・glossary（新しい用語を足さない。「事前宣言文書」「凍結 JSON」の定義は v1.1 でも真のまま）

## テスト戦略（検証）

| 何を | どう | 期待 |
|---|---|---|
| 値の一致 | `python scripts/check_prereg_parity.py` | exit 0 |
| 検査器が赤になれること | `python scripts/check_prereg_parity.py --self-test` | exit 0 |
| JSON・コード不変 | `git diff main --stat -- src-tauri/` | 空 |
| 本文を書き換えていない | `git diff main --numstat -- docs/preregistration-p1-episode.md` | 削除行 0 |
| 独立レビュー | `/cross-review`（パス限定） | 指摘を是正 or 記録 |
