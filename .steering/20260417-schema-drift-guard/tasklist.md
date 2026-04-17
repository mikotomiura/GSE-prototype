# タスクリスト

## 準備
- [x] requirement.md / design.md 記入 + /reimagine 実施
- [x] file-finder / impact-analyzer 並列調査
- [x] v2 採用判断 (design-comparison.md 参照)

## 回帰テスト (TDD: 先に追加する)
- [x] `scripts/tests/` ディレクトリ用意 (`__init__.py` 込み)
- [x] `scripts/tests/test_check_schema_parity.py` を追加
      ケース: match / CRLF / キー順 / variant 追加 / variant 除去 / proto 不在 / dataset 不在
- [x] TDD 赤: helper 未実装で 7/7 FAIL を確認

## 実装: Python helper (単一の真実の源)
- [x] `scripts/check_schema_parity.py` 実装
- [x] TDD 緑: 7/7 PASS を確認

## 実装: Shell ラッパー側 (helper 呼出しのみ)
- [x] `scripts/sync-all.ps1` に pre-flight 呼び出し追加 ($LASTEXITCODE cache 対応)
- [x] `scripts/sync-all.sh` に同等の pre-flight 呼び出し追加 (python3/python fallback)

## ドキュメント更新
- [x] `docs/development-guidelines.md` §10.2 に pre-flight が走る旨を追記
- [x] `docs/development-guidelines.md` §10.3.1 (新設) に helper の契約・使用法を追記

## 動作確認 (手動回帰)
- [x] PS normal: Step 0 OK + 以降の Step も通過
- [x] PS drift: ime_shadow 削除 → Step 0 FAIL inferred exit 1 (variant 差分表示 + 修復手順)
- [x] PS missing: dataset schema rename → Step 0 FAIL inferred exit 3 (コピー手順表示)
- [x] bash normal: Step 0 OK 確認
- [x] bash drift: shell exit=1 (set -e quirk 修正後)
- [x] bash missing: shell exit=3

## レビュー (並列実行)
- [x] code-reviewer 起動: HIGH 2件 + MEDIUM 5件 + LOW 5件
- [x] security-checker 起動: ブロッカーなし (MEDIUM 2件)
- [x] HIGH #1 対応: regex-based exit inference → --machine-readable センチネル駆動に置換
- [x] HIGH #2 対応: sync-all.sh Step 2 に set -e / rc 取得パターンコメント追記
- [x] MEDIUM (code-reviewer) 対応: _collect_type_enums イテレート化・const 対応、JSON parse error の個別エラーメッセージ、unittest に invalid JSON / BOM / const / sentinel 4 ケース追加
- [x] MEDIUM (security-checker) 対応: 再帰→スタックイテレートに変更 (RecursionError 回避)、センチネル導入で文字列 inference の脆さを除去
- [x] LOW 対応: tier-1/tier-2 cross-ref (§10.3), diff posix path 変換, "fingerprint" コメント整理
- [ ] LOW 未対応: em-dash ↔ ASCII 統一 (コスメティック、スコープ外と判断)

## 完了処理
- [x] design.md 末尾に実装時判明事項を追記 (PS quirk / bash quirk / reviewer 反映 / 動作確認サマリ)
- [x] /finish-task Step 1-2 完了
- [ ] /finish-task Step 3-5 (最終レビュー + テスト + commit)
