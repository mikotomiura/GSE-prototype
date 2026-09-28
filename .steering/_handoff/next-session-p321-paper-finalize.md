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

## §1 研究者の入力が要るもの（★ 推測で埋めない）

1. 著者名・連絡先メール・所属（無ければ居住する都市と国）→ `main.tex` の `\author` / `\affil`
2. Statements and Declarations: Funding・Competing interests・Ethics（「公開データの二次分析・人を対象とする新しいデータ収集なし」の文面でよいか）・Author contributions
3. LLM の使用の開示（`main.tex` Sect. 5.5）の文面でよいか（⚠️ 「The author is responsible for the content」は、研究者が原稿全体を読んだ後に確定する）
4. 題（仮題: *When "no help" is not "solved": outcome-agnostic self-resolution measures in two public debugging datasets*）
5. 原稿（`main.tex` / `refs.bib`）のライセンス（README は「未定」と書いてある。arXiv に出すときに決める＝前タスク判断 10）
6. ⚠️ 論文用リポジトリを公開すると、コミットの著者メール（`git log` の author）も公開される。そのまま公開するか、noreply に書き換えて書き換えた事実を NOTES に残すかを決める（⚠️ 書き換えるとハッシュが変わり、Method の「コミットの順序が凍結を示す」の根拠が弱まる）

## §2 投稿前の残り作業

- pdfLaTeX（Overleaf か投稿システムのプレビュー）で一度組む（⚠️ Tectonic は XeTeX＝判断 2）。`\vbox` の 2pt のはみ出しが 1 件ある（頁送り）
- Zenodo の DOI を取って Data availability の仮置きを埋める（外部アカウントの操作＝研究者）
- 投稿の直前に EMSE の規程ページを開き直す（書式・査読方式・LLM 方針）
- arXiv へのプレプリントは投稿と同時（前タスク判断 10）

## §3 やらないこと

- ⚠️ 解析の定義・結果を変える（変えるなら `NOTES.md` の Deviations に記録する別作業）
- ⚠️ [P321]/[P434] の値を GSE の期待値として使う・原稿で GSE に言及する
- ⚠️ ADR-024 D7 の訂正（前タスク判断 14: 次の関連 ADR で行う）
