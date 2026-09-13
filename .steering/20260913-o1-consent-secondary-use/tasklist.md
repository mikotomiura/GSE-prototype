# タスクリスト

## 準備
- [x] ハンドオフを読む（⚠️ 一次資料にしない）
- [x] `scripts/check-o1-release-readiness.sh` でベースラインを取る（★ 通過 19 / 未達 1）
- [x] 一次を読む: `consent-draft-o1.md` / `GSE_O1_Form_Builder.gs` / `o1_form_builder_test.cjs` / `o1-deletion-ledger.md`
- [x] `data-privacy` Skill を参照
- [x] ⚠️ 同意有無の置き場を研究者に確認（→ `decisions.md` 判断 1）

## 実装
- [x] `consent-draft-o1.md` §3 末尾に任意項目を追加（★ dev メモ 12 も追記）
- [x] ビルダー: 定数 ＋ `o1ConsentOptionalItemTitles_()` ＋ build / migrate の配線
- [x] ビルダー: `o1ConsentAnswers_` の `secondaryUse` ＋ 登録ログ note への連結
- [x] ⚠️ ビルダー: **フォーム本文は触らない**と決めた（→ design.md・任意の内容は専用セクションに閉じる）

## テスト
- [x] `o1_form_builder_test.cjs`: 既存「すべて必須」を必須群/任意群に分割
- [x] `o1_form_builder_test.cjs`: 新規 §6b（任意性・順序・1 対 1・固有名不在・往復・冪等・note）＋ ケース下限を 215→236
- [x] `check-o1-release-readiness.sh`: 検査 2 本追加 ＋ selftest 8 件（在る 2 / 無い 3 / 壊れている 3）
- [x] `node Form_O1/o1_form_builder_test.cjs` が exit 0（★ 242 ケース）
- [x] `bash scripts/check-o1-release-readiness.sh` が **21 緑 / 1 未達**（★ 未達はリリースタグの陳腐化のみ・ベースラインと同じ）
- [x] `--selftest`: 追加 8 件は全緑。⚠️ 既存 2 件の失敗は **main でも同じ**（→ blockers 起票 15）
- [x] `PYTHONUTF8=1 python scripts/check_doc_lexicon.py` が exit 0

## レビュー
- [x] code-reviewer + security-checker を**並列**起動
- [x] HIGH 1 / MEDIUM 5 / LOW 8 に対応（→ review.md）＋ 検証中に自分で 1 件発見して修正
- [x] `/cross-review`（パス限定・ID 混入 0 件を実測）→ 5 件のうち 4 件に対応（→ review.md）

## ドキュメント
- [x] `docs/o1-deletion-ledger.md`: §2b（撤回経路）/ §5c（判定規則・fail-closed）/ A-13 追記
- [x] glossary に 2 語追加（「任意の二次利用同意」/「二次利用の印」）

## 完了処理
- [x] design.md の最終化
- [x] decisions.md の作成
- [x] git commit（2 本）
- [ ] ⚠️★★★ **文言を研究者の承認へ返す**（★ 被験者向け文書は契約）
