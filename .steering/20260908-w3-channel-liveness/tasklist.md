# タスクリスト

## 準備
- [x] ★ mac 側 (origin/main 35 コミット) を取り込む（★ `1301a34`・⚠️ コンフリクトは `_handoff/README.md` 1 件）
- [x] ★ `/start-task` の grill でゴールと 4 分岐を確定（→ `decisions.md`）
- [x] ★ 一次資料をサブエージェント 2 本に並列で投げる（ADR-017 D2 / ADR-021 D9 ／ ADR-022 D5 / ADR-027 / PM-D4 / [P256]）
- [x] ★ `grilling` Skill を読む
- [x] ★ `citation-ssot` Skill を読む（★ ADR に出典を引くため）
- [x] ★ `verify-before-claiming` Skill を読む

## 実装（★ 文書）
- [x] `docs/adr/ADR-028-channel-liveness-and-expiry.md` を書く
- [x] `expression-channel.md` §2.1 項目 4 を改訂する
- [x] `expression-channel.md` §7.5 の `A3` / `A21` / `A22` を更新し、新観点を足す
- [x] `expression-channel.md` §8 の `W-3` を閉じ、`W-1` 行を更新する
- [x] `docs/glossary.md` に確定用語を足す
- [x] `docs/adr/README.md` に ADR-028 の行 ＋ 読む順の注記
- [x] `docs/agent-shared.md` のリンクハブ行

## テスト（★ 文書の機械検査）
- [x] `check_citations.py` を **exit 0**（⚠️ 「違反なし」まで是正 → 再実行）
- [x] `check_doc_lexicon.py` が緑
- [x] 変更ファイルの markdown 表の破損を機械走査（★ 0 件）
- [x] 旧文が SSOT に残っていないことを grep で確認

## レビュー
- [x] `code-reviewer` ＋ `security-checker` を並列起動
- [x] HIGH 指摘への対応（⚠️ backlog へ punt しない）
- [x] `/cross-review`（★ コミット後・パス限定・出力は scratchpad）

## ドキュメント
- [x] glossary への用語追加
- [x] 引き継ぎ `.steering/_handoff/` の更新（★ **`W-1` などの残タスク**・研究者の指示）

## 完了処理
- [x] design.md の最終化
- [x] decisions.md の作成
- [x] git commit
