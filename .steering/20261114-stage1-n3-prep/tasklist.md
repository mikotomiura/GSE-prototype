# タスクリスト

## 場面ごとに使うもの（完了前に照合する）
- ADR の根拠の確かめ → verify-before-claiming（ルール 7・8: 長い一次資料を 1 節で代表させない・「閉じた」と書く前に全文 grep）
- 文献の引用 → citation-ssot（ADR も対象・[Pn]/[Vn] は既存を使い、足すなら append-only）
- 完了時のレビュー → /cross-review（code-reviewer＋Codex・O1 と段 1 の記録の本文は送らない）
- 決めることは AskUserQuestion で 1 問ずつ・日本語

## 準備
- [x] 引き継ぎ・ADR-043・ADR-014 判断 3・ADR-039 D1 を読む
- [x] grill（判断 1〜9）
- [x] worktree（`/Users/johnd/GSE-prototype-stage1-n3`・枝 `docs/gse-stage1-n3-prep`）
- [ ] ADR-039 D1・ADR-047・ADR-050・ADR-051 を全文で読む（ルール 7）
- [ ] ADR-014 判断 3 の 4 根拠を段 1 の構成（問い・手跡・提出・募集）に当てる材料を集める

## 実装（文書）
- [ ] ADR-052 の草案（Context・D1〜D9・上書きの範囲・Alternatives・Consequences・Migration・参照した書誌）
- [ ] README の一覧と読み替えの注記
- [ ] preregistration-stage1.md に ADR-052 への参照
- [x] glossary の用語

## レビュー
- [ ] /cross-review
- [ ] 指摘の採否を decisions に記す

## 完了処理
- [ ] 研究者が ADR-052 を読み、ステータスを決める
- [ ] 引き継ぎ（事前登録の値・同意文書と配布物・手跡の macOS と Windows）
- [ ] design.md の最終化
- [ ] git commit（push と PR は研究者に確かめる）
