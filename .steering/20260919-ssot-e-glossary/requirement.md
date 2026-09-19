# 単位 e: glossary に理論レビューの語を足す

> 親タスク: `.steering/20260919-theory-ssot-promotion/`（段 3）。引き継ぎ §2 の単位 **e**。

## 背景

- 理論レビュー（前段）と段 3 冒頭の研究者判断で、理論の語の扱いが決まった: 「返権」は確定・理論名は S3 の後（段 3 判断 1 #3）／「非支配的協調」→「関係的自律を支える協調」（同 #1）／草案の「計測なき身体回帰」は「自ら選んだ間と再開の機会」へ統合（同 #2・J-14）／負担台帳は系が生む負担に限る（J-17）／受容率を成功指標にしない（J-15）／再開・再停止は条件 A の辺（J-10・ADR-030 補訂 1 項目 7）。
- 単位 a / b で ADR-030 補訂 1 と ADR-033（非再捕捉）が入った。

## ゴール

- `docs/glossary.md` に、返権・返権の負荷逆説・権限・負担の二重台帳・Semantic Stop・非再捕捉・選択の対称性・関係的自律を支える協調・産出の再開 / 再停止・計測なき身体回帰（SSOT の用法の固定）を足す。
- 既存の「自ら選んだ間と再開の機会」「打鍵再開」に注記を足す。禁止用語に 3 行（旧名・新規性の断定・`T1c` を修正と呼ぶこと）を足す。

## スコープ

### 含むもの
- `docs/glossary.md`

### 含まないもの
- ⚠️ 理論名「生成的返権論」の確定（S3 の後）
- ⚠️ RP・理論草案への反映（単位 d-2 / h）

## 受け入れ条件

- [ ] 禁止用語の表と衝突しない（新しい語が既存の禁止語を使っていない）
- [ ] 「先行が無い」型の断定をしていない
- [ ] 同名異義（計測なき身体回帰・再開）を分けている
- [ ] `check_citations.py` / `check_doc_lexicon.py` 違反なし
- [ ] `/cross-review` 2 巡

## 関連ドキュメント

- `.steering/20260918-theory-critical-review/decisions.md`（判断 1 / 2）・`review-B.md` §5・`review-D.md` §6
- `.idea/20260915-generative-relinquishment-theory.md` §3.1 / §4 / §6.3 / §9.1 / §11
- `docs/literature/20260919-authority-return-burden-precedents.md`（S1）・`docs/literature/20260919-non-domination-and-autonomy-norms.md`（S2）
- `docs/adr/ADR-030` 補訂 1・`ADR-033`

## 運用メモ

- /reimagine 適用: **No**
- 理由: 語と定義は研究者判断と草案で決まっている
