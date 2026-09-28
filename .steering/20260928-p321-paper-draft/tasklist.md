# タスクリスト — p321-paper-draft

## 0. 前提
- [x] PR #252（[P434] の照合記録）の CI 緑 → merge（`e379b81c`）・main の run（36375095068）success を確認
- [x] 引き継ぎ・前タスクの判断 1–17・`outline.md`・`results/report.md`・`NOTES.md`・カードを読む
- [x] grill 4 問（判断 1–4）・`/start-task`（worktree `docs/p321-paper-draft`・⚠️ メインの checkout は並行セッションの IME loop-run が使用中のため worktree で作業）

## 1. 準備
- [x] テンプレート 2 種をダウンロードして比較 → SN v3.1・`sn-basic`（判断 1）
- [x] Tectonic 0.17.0 を scratch に置き、サンプルを組む（EPS 不可・XeTeX＝判断 2）
- [x] [V178] の本文を取得（IEEE・CC BY 4.0・23 頁）し、7 つのガイドライン（G1・G2・G3.1–G3.3・G4・G5）と §2.3–2.4 を読む
- [x] 解析コード（`d1.py`・`d2.py`・`stats.py`・`analyze.py` の自己検査）・`config.json`・`DATA.md`・コードブックを読む
- [x] 原著 3 本と引用する文献（[P435] [P436] [V170] [V175] [V176] [V178]）の逐語を PDF で照合（pypdf・20 件一致）
- [x] 統計手法の出典を subagent で探索 → メインが一次で照合 → `docs/references.md` に [V179]–[V183] を登録（判断 8）

## 2. 足場
- [x] `paper/build.sh`・`paper/make_results.py`・`paper/results.tex`・`.gitignore`（判断 5・6）
- [x] `paper/main.tex`・`paper/refs.bib`（21 項目・design.md の対応表）

## 3. 執筆（判断 3 の順）
- [x] Results（表 2: 主定義、表 3: D1 の 8 通り、表 4: 起点、表 5: [P433] の再現）
- [x] Measures（表 1: 構成概念 = [V178] G1）/ Data / Method（LLM の使用を含む）
- [x] Introduction / Background and related work
- [x] Discussion / Threats to validity（[V178] の G1–G5 に沿う）
- [x] Conclusion / Statements and Declarations（仮置き）/ Data availability
- [x] Abstract（242 語）・キーワード（6）・題（仮題）

## 4. 検査
- [x] `bash paper/build.sh` exit 0（20 頁・Overfull 0・未定義の引用 / 参照なし）
- [x] 対照 4 本（未定義キー・`metrics.json` の改変・主張を偽にする値・無変更）
- [x] 書いてはいけないことの grep（PDF 全文・11 パターン → 該当は否定文・原著の逐語・replication package 等の正当な用法だけ）
- [x] 論文用リポジトリの `bash run.sh` exit 0（結果は同梱のものと同一）
- [x] 論文用リポジトリにコミット（`e9c8e2b`・push はレビュー後）

## 5. 完了
- [ ] `/cross-review` 2 巡 ＋ security-checker
- [ ] 研究者への確認（著者情報・Statements・題・LLM の開示の文言）
- [ ] 論文用リポジトリを push
- [ ] GSE 側: `/finish-task` の出荷フロー（PR → CI 緑なら merge）

## 残課題（本タスクの外）
- 投稿前に pdfLaTeX（Overleaf か投稿システム）で一度組む（判断 2）
- Zenodo の DOI（投稿時・Data availability の仮置きを埋める）
- 投稿前に EMSE の規程ページを開き直す（書式・査読方式）
