# gse-docs-clarity —— docs を今の設計（ADR-052 まで）に合わせて読める形にし、不要なものを外す

## 背景

- `docs/research-positioning.md` は 1721 行で、§1 に改訂ブロックが 3 層（2026-10-31・11-03・11-05）あり、旧文に「〜で改めた」の注が重なっている。外の読み手には読めず、内部でも古い契約を掴む危険がある。ADR-047 Migration 1 は「本文は書き直さず改訂ブロックと注で直す」と決めていたが、その結果がこの状態である。
- ADR-040〜052（2026-10-31〜11-14）で、位置づけ（「詰まる前に」を外す）・主の対象（停滞）・推定の役（契機を作らない）・段 1/段 2・手跡・人数（N-of-1）が組み替わった。agent-shared・glossary・functional-design・architecture・architecture/ 配下の Epic 期の設計文書は、Nudge 中心・3 状態中心の記述を多く残している。
- 2026 年度未踏の不採択コメント（`~/Downloads/未踏.webp`）への対応表は `.idea/20260911-...md` §13 にしかなく（版管理外・9 月時点で古い）、再応募の素材として使えない。
- 研究者の指示（2026-11-15）: WBS（`docs/wbs-verification-halfyear.md`）は不要なので消す。ほかにも不要な docs は消す。

## ゴール

1. `docs/research-positioning.md` を、ADR-052 までの現行の主張だけで書いた新しい本文（目安 300〜400 行）にする。旧全文は `docs/history/` へ逐語で移す。[Pn]/[Vn] の番号と参照は保つ。
2. 文書の「現行版と履歴を分ける」作法を ADR-053 で決める（ADR-047 Migration 1 を改める）。
3. agent-shared・glossary・architecture/gse-design-map・functional-design・architecture を現行に揃える。未踏の不採択コメントへの対応表を docs の内部の追跡表として置く。
4. 不要な docs を削除し、古い設計文書は履歴へ移す。旧パスから移し先・削除のコミットを `docs/history/README.md` の表で辿れるようにする。

## スコープ

### 含むもの

- PR1: research-positioning の新本文＋旧全文の履歴への移動＋ADR-053＋`docs/history/README.md`。
- PR2: agent-shared・glossary・architecture/gse-design-map・未踏の対応表（docs/mitou_submission/ 配下・内部の追跡表）。WBS などの削除と履歴への移動、参照元（ADR 以外）の付け替え。
- PR3: functional-design・architecture・（必要なら）repository-structure を現行に揃える。

### 含まないもの

- ADR の本文の書き換え（規約。ADR からの参照は履歴の表で辿る）。
- 凍結した事前登録（v0.3・p1-episode・stage1）・削除保証の台帳・被験者向け文書の中身の変更。
- 応募書類（mitou_submission の提出版）の改訂。
- theory/・literature/・references.md の中身の再編（references への append は可）。
- コードの変更。
- 研究の主張そのものの変更（ADR にない新しい決定を docs で下さない）。

## 受け入れ条件

- [ ] research-positioning の新本文に、ADR-052 までの位置づけ・headline・問い・主張と主張の上限・段 1/段 2・推定の役・手跡・人数・反証条件・スコープ・新規性として書ける範囲が入り、改訂ブロックの層が無い。各主張に根拠の ADR か実験のパスが付く。
- [ ] 旧全文が `docs/history/` に逐語で残る（`diff` で一致を確かめる）。
- [ ] ADR-053 が Accepted で、`docs/adr/README.md` の表に載る。
- [ ] 削除・移動した文書について、`docs/history/README.md` に旧パス → 移し先 / 削除のコミットの行がある。ADR 以外の参照元にリンク切れが無い（grep で 0 件）。
- [ ] 各 PR で `/cross-review` を通す（Codex を加える）。
- [ ] glossary の禁止用語を新しい本文が使っていない。

## 関連ドキュメント

- `docs/adr/ADR-040`〜`ADR-052`・`docs/adr/README.md`
- `docs/research-positioning.md` §1 の 2026-11-05 改訂ブロック
- `.idea/20260911-mhd-growth-personalization-and-gse-overview-roadmap.md` §13
- `.steering/20261105-gse-overview-and-concept/doc-drift.md`

## 運用メモ

- /reimagine 適用: No
- 理由: 研究の決定は ADR-040〜052 で済んでおり、このタスクは文書をそれに合わせる作業である。構成の選択（現行版と履歴を分ける・3 PR）は研究者が AskUserQuestion で決めた（decisions.md 判断 1〜6）。
