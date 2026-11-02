# 要件 — MhD の単位を分ける ADR（効果の単位と、MhD の有効標本数の単位）

## 背景

- MhD（推定器の段を上げていく計画）の有効標本数の単位は、ADR-019 D4 で `Decision Episode` に固定され、ADR-030 D7 で「1 つの停滞の始まり（C0）= 1 つの Decision Episode の開始」に載せられた。理由は、30 秒窓を 1 Hz で出すので隣の窓が 29/30 重なり、窓を独立な標本に数えられないこと（[V100]）。
- ところが停滞の定義そのものが問い直されている（synthesis 判断 2）。C0 のほかに C1（活動の止まり）・C2（前進なき活動）・C6（打鍵の空回り）を作ると、C0 の停滞は C2 側と C1 側におよそ半分ずつ分かれた（`experiments/20261103-stall-candidates-c1c2c6/notes.md` §4）。定義を変えると、MhD の標本の数と境界も変わる。
- ADR-030 補訂 1 項目 6: onset とエピソードは 1 対 1 にならない（E1/E2 の束ね方が未決）。
- 次の検証の段 1（`.steering/20261103-gse-next-study-design/decisions.md`）では、詰まりの基準（C4）をアプリ内のプローブで取り、無作為の枠の申告を主にする。割付の単位は日。
- synthesis 判断 7・8: 効果を見る単位（日・作業のまとまり）と MhD の有効標本数の単位は別の量。O1 の 1 日 = ADR-019 のセッション 1 本。holdout は日で切る。日を独立に扱えるかは H4b で確かめる。

## ゴール

- 効果を見る単位と、MhD の有効標本数の単位を、別の量として定義する ADR を 1 本起票する（ADR-019 D4・ADR-030 D7 を上書きする範囲を明示する）。
- MhD の単位を、停滞の定義の見直し（C0・C1・C2・C6）と段 1 の C4 の取り方に合わせて開き直す。
- O1 の 1 日 = 1 セッションと、holdout を日で切ることを書く。

## スコープ

### 含むもの
- 単位の ADR の内容を研究者と決め、第二意見（/reimagine）を取り、起票し、レビューにかける。
- 引き継ぎ §2 の 3（MhD 固有の事前登録の条件の中身の形）を、時間が残れば詰める。

### 含まないもの
- コードの変更。
- 停滞の定義の選択（C4 が要る）。
- 次の検証の段 1 の ADR の起票（段 1 の判断 9・別タスク）・同意文書・research-positioning と WBS の改訂。
- 公開データでの MhD の配管の空回し（引き継ぎ §2 の 4・別タスク）。
- 保留 1（動機づけと同期・共生の感覚の問い方）。

## 受け入れ条件

- [ ] 単位の ADR が起票され、ADR-019 D4・ADR-030 D7 のどこを上書きするかが書かれている。ADR の本文の書き換えはしない。
- [ ] 判断と理由が decisions.md に残っている。
- [ ] code-reviewer と /cross-review を通し、指摘の扱いが記録されている。
- [ ] Codex に O1 の記録・中間・結果の本文を送っていない。

## 関連ドキュメント

- `docs/adr/ADR-019-model-maturity-and-promotion-gate.md` D3・D4
- `docs/adr/ADR-030-stall-onset-and-decision-episode.md` D7・補訂 1 項目 6
- `docs/architecture/personalization-and-online-learning.md` §3.1
- `.steering/20261102-gse-synthesis-redesign/`（synthesis.md・decisions.md）
- `.steering/20261103-gse-next-study-design/decisions.md`

## 運用メモ

- /reimagine 適用: Yes
- 理由: 研究者が判断 1〜5 の後に、起票前の第二意見として /reimagine を選んだ（引き継ぎ「起こす前に codex-consult か /reimagine」）。
