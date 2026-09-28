# p321-paper-draft — 2 本目の論文の原稿（[P321]/[P433] ＋ [P434] の再解析・EMSE 研究論文）

## 背景

- 前タスク `.steering/20260928-p321-reanalysis-paper/` で解析と外枠が揃った（判断 1–17・`outline.md`・論文用リポジトリ `C:/self-resolution-measure` の `results/report.md`）。
  前タスクの判断 3 で「原稿の執筆は別タスク」としていた。
- 投稿先は *Empirical Software Engineering* の研究論文（前タスク判断 9）。書式・査読方式は前タスク判断 17 で一次確認済み
  （single-blind・要旨 150–250 語・キーワード 4–6・著者名と年の引用・Statements and Declarations と Data availability が必須・LLM の使用は Methods に書く）。
- 引き継ぎ: `.steering/_handoff/next-session-p321-paper-writing.md`（⚠️ 一次資料ではない）。

## ゴール

EMSE の研究論文として**全節の初稿**を論文用リポジトリに置き、手元で PDF まで組める状態にする（研究者の選択・判断 3）。

## スコープ

### 含むもの

- テンプレートの選択とダウンロード（研究者の承認済み・判断 1）と、手元のビルド手段（Tectonic・判断 2）
- [V178] の本文を読み、妥当性の節をその 7 つのガイドラインに沿って書く
- 原稿の全節: Results → Measures / Data / Method → Introduction / Related work → Discussion / Threats → Conclusion・Data availability → Abstract
- 参考文献（`.bib`）: `docs/references.md` の登録済みの文献から作る。新しく引く文献は `docs/references.md` に append-only で登録してから使う
- `/cross-review` 2 巡（Codex ＋ Claude の code-reviewer）と security-checker
- 著者情報・Statements and Declarations は仮置き（研究者に最後にまとめて確認する）

### 含まないもの

- 投稿そのもの・arXiv への投稿（判断 10: 投稿と同時）・Zenodo の DOI 取得（外部アカウントの操作）
- 解析の定義・結果の変更（凍結済み。変えるなら NOTES の Deviations に記録する別作業）
- ADR-024 D7 の訂正（前タスク判断 14: 次の関連 ADR で行う）
- IME 論文のタスクのファイル（並行セッションが作業中）
- [P434] の GitHub 補足データ（LICENSE 無し）
- [P321]/[P434] の値を GSE の期待値として使うこと

## 受け入れ条件

- [ ] 論文用リポジトリに原稿（`paper/`・サブフォルダなし）があり、`bash paper/build.sh` が exit 0 で PDF を出す
- [ ] 原稿の数値はすべて `results/report.md`（または `results/metrics.json`）と一致する（検算スクリプトで確かめる）
- [ ] 前タスク `outline.md`「書いてはいけないこと」の各項目に原稿が触れていない（grep で確かめる）
- [ ] 要旨 150–250 語・キーワード 4–6・Statements and Declarations・Data availability・Methods に LLM の使用の記述がある
- [ ] 本文の引用はすべて `.bib` にあり、`.bib` の各項目は `docs/references.md` の `[Pn]`/`[Vn]` に対応づけてある（design.md の対応表）
- [ ] `/cross-review` 2 巡と security-checker の CRITICAL / HIGH がすべて対応済み

## 関連ドキュメント

- `.steering/20260928-p321-reanalysis-paper/decisions.md`（判断 1–17）・`outline.md`
- 論文用リポジトリ `results/report.md`・`NOTES.md`・`DATA.md`・`config.json`
- `docs/literature/20260928-self-resolution-measure-positioning.md`
- `docs/references.md`

## 運用メモ

- /reimagine 適用: No
- 理由: 原稿の執筆で、主張と根拠の対応・書いてはいけないことは `outline.md` と前タスクの判断 1–17 で確定しており、設計の分岐が無い（研究者の選択・2026-09-28）。
