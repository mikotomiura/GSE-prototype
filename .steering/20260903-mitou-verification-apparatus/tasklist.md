# タスクリスト

## 準備
- [x] 引き継ぎプロンプトを読む (`.steering/20260903-mitou-doc-consistency-fixes/next-session-prompt.md`)
- [x] `docs/mitou_submission/README.md` (運用 SSOT) を読む
- [x] 詳細資料 §4 / §5、検証レポート全体、技術設計書 §7-§11 を読む
- [x] `G1` / `O1` / 語彙の出現数を実測で再検証
- [x] 機械検査 3 本のベースラインが緑であることを確認
- [x] ページ数を LibreOffice で実測 (→ README の表が古いことを発見)
- [x] 統制実験レジームの到達点をサブエージェントで棚卸し
- [x] 自然作業の長期記録レジームの到達点をサブエージェントで棚卸し

## 実装
- [x] 詳細資料 §4【検証ワークフロー】直後へ 250〜350 字を挿入
- [x] 検証レポートへ §7.5「検証を支える装置」を追加 (動いている / 未実装 / 未検証 を書き分け)
- [x] 裸の `G1` を処理 (技術設計書 L628 / 検証レポート L31・L62)
- [x] `docs/mitou_submission/README.md` のページ数表を実測値へ訂正
- [x] `.docx` を再生成 (詳細資料のみ `--compact`)

## 検証
- [x] `md2docx.py --selftest` 緑
- [x] `check_doc_lexicon.py` 緑 (`★` / `⚠️` ゼロ)
- [x] `check_citations.py` 緑
- [x] **一次資料との突き合わせを別エージェントへ委譲** (機械検査は事実誤りを見ない)
- [x] **Google Drive でページ数を実測** (提出経路。10 ページ以内)

## レビュー
- [x] code-reviewer / security-checker
- [x] `/cross-review` (省略しない。Codex 側は事実検証を問わない前提で投げる)
- [x] HIGH 指摘への対応

## 完了処理
- [x] design.md の最終化
- [x] decisions.md の作成
- [ ] git commit
- [ ] `/finish-task`
