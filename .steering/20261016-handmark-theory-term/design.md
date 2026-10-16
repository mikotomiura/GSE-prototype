# 設計: handmark-theory-term

## アプローチ

文書の改訂だけ。研究者の裁定（判断 28・本タスク判断 1）の範囲だけを本文に当て、`/cross-review` で一次と照合する。

## 変更対象

- `docs/theory/measurement-terminating-practice-portraiture.md`: §1 見出し・§1.4 新設・§0/§5/§12 の注記・§5.3/§9/§10 の追記
- `docs/glossary.md`: 「手跡」1 行
- `docs/theory/README.md`: 索引の説明 1 行

## 書き方の規則

- 文献に依拠する記述は既存の [Pn] だけを使い、新しく採番しない。S-TN の台帳の留保（抄録のみ・12 人の帰無）を落とさない。
- 新しさを主張しない。候補を語として扱わない。Claude が足した論点は、そう明記する。

## テスト戦略

- 引いた [Pn] が `docs/references.md` に実在すること（grep）
- 誤記「タンジブリティ」が変更した docs に 0 件
- `/cross-review`（Claude と Codex）
