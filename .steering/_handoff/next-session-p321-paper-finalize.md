# 次セッション — 2 本目の論文（[P321]/[P433] ＋ [P434] の再解析）の原稿を投稿できる形に仕上げる

> 作成: 2026-09-28（`.steering/20260928-p321-paper-draft/` の完了時）。
> ⚠️ **このメモを一次資料にしない。** 判断は `.steering/20260928-p321-paper-draft/decisions.md`（判断 1–11）、原稿は論文用リポジトリ `C:/self-resolution-measure` の `paper/main.tex`（`be754be`）。

## §0 打ち込む用

```
.steering/_handoff/next-session-p321-paper-finalize.md を読んで、2 本目の論文の原稿を投稿できる形に仕上げてください。
まず /start-task で .steering/<日付>-p321-paper-finalize/ を作る（メインの checkout が他セッションで使用中なら git worktree で切る）。
一次資料: .steering/20260928-p321-paper-draft/decisions.md（判断 1–11）・論文用リポジトリ C:/self-resolution-measure の paper/main.tex・NOTES.md・results/report.md。
ビルド: bash paper/build.sh（Tectonic が要る。無ければ判断 2 の手順で scratch に置く＝研究者の承認を取ってから）。
Skill: verify-before-claiming・citation-ssot・subagent-delegation。応答は日本語。GSE 側は専用ブランチで git add はパス指定（-A 禁止）。
```

## §1 研究者の決定（★ 2026-09-28 にすべて決まった＝判断 12）

- 著者: Mikoto Miura・mmiura.network@gmail.com・Hiroshima, Japan（`4a81a43` で原稿に反映済み）
- Statements and Declarations: すべて該当なしで記入済み ／ LLM の開示: 今の文面で確定 ／ 題: 仮題で確定
- ⚠️ 原稿のライセンスは**投稿時に決める**（arXiv に出すときに出版社の規程を一次で確かめる）
- 論文用リポジトリのコミット著者: 過去は書き換えない・以後は Mikoto Miura（⚠️ 公開すると過去の John Do <johndo.mik.080@gmail.com> も出る）
- ⚠️ 研究者が原稿全体を通読して内容を確認するのはこれから（「The author is responsible for the content」の前提）

## §2 投稿前の残り作業

- pdfLaTeX（Overleaf か投稿システムのプレビュー）で一度組む（⚠️ Tectonic は XeTeX＝判断 2）。`\vbox` の 2pt のはみ出しが 1 件ある（頁送り）
- Zenodo の DOI を取って Data availability の仮置きを埋める（外部アカウントの操作＝研究者）
- 投稿の直前に EMSE の規程ページを開き直す（書式・査読方式・LLM 方針）
- arXiv へのプレプリントは投稿と同時（前タスク判断 10）

## §3 やらないこと

- ⚠️ 解析の定義・結果を変える（変えるなら `NOTES.md` の Deviations に記録する別作業）
- ⚠️ [P321]/[P434] の値を GSE の期待値として使う・原稿で GSE に言及する
- ⚠️ ADR-024 D7 の訂正（前タスク判断 14: 次の関連 ADR で行う）
