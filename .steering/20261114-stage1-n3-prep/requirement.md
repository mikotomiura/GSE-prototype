# stage1-n3-prep —— 段 1 を採択前に n=3 で回すための ADR-052

## 背景

研究者は 2026-11-14 に、本人の段 1 を約 1 週間（手跡の後期まで）回した後、採択を待たずに本人以外の 3 名を回すと決めた。基準は「研究として強い方」（memory: project-stage1-n3-before-adoption）。ADR-043 D3 は確認を採択後の参加者で行うとし、D8 は ADR-031・ADR-032 の Accepted の条件を「段 1 の同意文書の承認」としている。採択前は審査を受ける道が無く、ADR-039 D1 の 2026-10-12 の注は「GSE で新しく集めるときは承認を受けてから」と広く言い換えている。このままでは n=3 の位置づけと根拠が ADR に無い。

入口: `.steering/_handoff/next-session-gse-stage1-n3-prep.md`。grill の決定は `decisions.md` 判断 1〜9。

## ゴール

ADR-052 を書き、ADR-043 D3・D8 と ADR-051 D1・ADR-039 D1 の範囲を、判断 1〜9 のとおりに読み替える。ADR の本文は書き換えず、README と関連文書に注記する。

## スコープ

### 含むもの
- `docs/adr/ADR-052-*.md`（判断 1〜9 を D に写す・citation-ssot で接地）
- `docs/adr/README.md` の一覧に ADR-052 を足し、ADR-031・ADR-032・ADR-039・ADR-043・ADR-051 の行に読み替えを注記
- `docs/preregistration-stage1.md` の S1-G1・S1-G2 と §0 に、ADR-052 への参照を足す（値は埋めない）
- `docs/glossary.md` の用語（済み）
- 次のタスクへの引き継ぎ（事前登録の値・同意文書と配布物・手跡の macOS と Windows）

### 含まないもの
- 事前登録の値の決定と凍結（本人の探索の後・別タスク）
- n=3 の同意文書・配布物・リリースタグ（別タスク）
- 手跡の PR #408 のマージ・Windows 版の実装（別タスク）
- 本人の段 1 の記録を開くこと・Codex に記録や集計を送ること
- コードの変更

## 受け入れ条件

- [x] ADR-052 が判断 1〜9 を D として持ち、各 D の根拠が一次資料（ADR 番号と節・ファイル:行・[Pn]/[Vn]）に降りている
- [x] ADR-014 判断 3 の 4 根拠を段 1 に一つずつ当て直し、崩れないかを書いている（問い・手跡・提出・募集）
- [x] ADR-039 D1 の範囲（2 本目の論文）を、本文の逐語で確かめたうえで書いている
- [x] README の一覧と読み替えの注記が入り、ADR 本文は書き換えていない（`git diff` で ADR-031/032/039/043/051 の本文が 0 行）
- [x] /cross-review（code-reviewer＋Codex）を通し、指摘の採否を decisions に記す
- [x] 研究者が ADR-052 の本文を読んで Accepted にするか決めた

## 関連ドキュメント

- docs/adr/ADR-043・ADR-047・ADR-051・ADR-014（判断 3）・ADR-039（D1）・ADR-050
- docs/preregistration-stage1.md
- .steering/_handoff/next-session-gse-stage1-n3-prep.md

## 運用メモ
- /reimagine 適用: No
- 理由: 判断 1〜9 は grill で 2〜3 の案を比べて研究者が選んだ。ADR はそれを根拠づけて写す作業で、穴は完了前の /cross-review（Codex を含む）で探す（研究者が 2026-11-14 に選んだ）。
