# 設計 — 未踏提出文書の整合性修正と提案書の整理

## アプローチ

**A（整合性修正）と B（提案書の整理）を分ける。** A は SSOT と提出物のズレを閉じる回帰修正、
B は 1 ファイルの内容改訂であり、revert の単位が違う（decisions.md D3）。

## 変更対象

| ファイル | 何を |
|---|---|
| `docs/mitou_submission/README.md` | 再生成コマンドに `--compact`。実測ページ数の注記 |
| `docs/mitou_submission/mitou_docs/[提案プロジェクト補足資料]GSE技術設計書.docx.md` | §3.2 を現行実装へ／§8 の IME 主張を弱める／§4.4 に損失関数の受け皿 |
| `docs/mitou_submission/mitou_docs/[提案プロジェクト詳細資料]GSE_proposal.docx.md` | B-1〜B-10 |
| `docs/references.md` | Dhakal et al. (2018) を append-only 登録 |
| `CLAUDE.md` / `docs/agent-shared.md` | ADR 範囲を 022 まで |
| `docs/mitou_submission/figures/gse-model-promotion.svg` (+ .png) | 4 段へ差し替え |

## ページ予算

⚠️ **レンダラ依存であり、単一の正解が無い**（2026-09-03 実測）:

| 経路 | ページ数 |
|---|---|
| `md2docx.py --compact` → LibreOffice | **10.0**（10 ページ目は 646 字 / 17 行） |
| `md2docx.py`（`--compact` 無し）→ LibreOffice | **15** |
| Google Drive 表示（研究者確認） | **7** |

→ ★ **提出に使う経路で最後に 1 回実測する。** 本タスクでは Drive の 7 ページを基準に
**+4,000 字**を実効枠とする（3 ページ ≒ +4,900 字から安全余裕 0.5 ページを引いた値）。

⚠️ **未確認**: Drive 版で図 1〜3 が描画されているか。落ちていれば 7 ページの前提が変わる。

## テスト戦略

- `PYTHONUTF8=1 python scripts/check_doc_lexicon.py` = 違反なし（★ 禁止用語・装飾記号・撤回済み主張）
- README 手順で `.docx` 4 本を再生成し、`word/document.xml` のテキストが一致すること
- 提案書に `Markdown エディタ` / `国際的に存在しない` が残っていないこと（grep）
- ⚠️ **コード変更が無いので `cargo test` は本タスクの検証にならない。**
  技術設計書 §3.2 の修正が正しいことは `analysis/loop_step.rs:314` の逐語との突合で示す。
