# タスクリスト

## 段 1: 批判的レビュー
- [x] 引き継ぎメモ・判断 25・起票 9/11/12/15/17・issue 004/006 を読む
- [x] 文書 A（891 行）を全文読み `review-A.md`
- [x] 文書 B（658 行）を全文読み `review-B.md`
- [x] 文書 C（472 行）を全文読み `review-C.md`
- [x] 評価契約群 D（14 ファイル）を全文読み `review-D.md`（別トラックの未チェック受け入れ条件の判定を含む）
- [x] SSOT 照合（サブエージェント 4 本）→ 一次で検算 → `ssot-collision-findings.md` / `citations-audit.md`
- [x] 禁止用語の実検査（`check_doc_lexicon.py` の空回りを発見し、同じ規則を草案へ当てた）
- [x] 「再停止」／`T1d`／`T1c` の定義案（`definitions-restop-t1d-t1c.md`）
- [x] ADR-030 補訂案（`adr-030-amendment-draft.md`）
- [x] 研究者判断バッチ 1（18 問）→ `decisions.md` 判断 1
- [x] 段 1 の成果物をコミット

## 段 2: サーヴェイ（1 ラウンドごとにコミット）
- [x] S7 content-free な修正指標 → カード・[V151]–[V160]・定義案 §6.2b（`4403763`）。⚠️ issue 004 への転記は判断 2（改名）の後
- [x] S8 再開・再停止・burst → カード・[V161]–[V169]・定義案 §3.4・補訂案 項目 6（`7860ccb`）。⚠️ issue 006 への転記は判断 2 の後
- [x] S1 返権の負荷逆説 vs ironies of automation 等 → カード・[P368]–[P379]・`review-B.md` §5（`95abd10`）
- [x] S2 非支配的協調 vs 非支配・関係的自律・nudge 倫理 → カード・[P380]–[P391]・`review-D.md` §6（`99c0d60`）
- [x] （補足）Digital Nature の一次 —— ★ J-6（CORE-CS の比較節へ統合）を段 3 で正確に書くため必要と判断し、1 ラウンドに絞って実行（カード・[P392]–[P395]）
- [x] `check_citations.py` 違反なし（各ラウンド）

## 完了処理
- [x] 段 3（SSOT 昇格）の作業単位を書き出す → `.steering/_handoff/next-session-theory-ssot-promotion.md`（単位 a〜i）・RP 還元案 `positioning-reduction-draft.md`
- [x] 研究者判断が新たに要る箇所をまとめて聞く → バッチ 2（8 問・判断 2）。★ バッチ 3（実装の細部 4 問）は研究者が差し戻した → 実装フェーズへ回す（判断 3）
- [x] 判断 2 の `T1c` / `T1d` を issue 004 / 006・受け入れスクリプトへ転記（判断 4・タスク 2 判断 26）。⚠️ スクリプトは `bash -n` とダミー行での jq 検算のみ
- [x] ADR-030 補訂案 項目 6 に「V1 の裁定まで反映しない」を注記
- [x] `design.md` の最終化
