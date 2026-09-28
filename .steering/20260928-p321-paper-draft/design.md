# 設計 — p321-paper-draft

## アプローチ

- 原稿は論文用リポジトリ `C:/self-resolution-measure`（private・GitHub `mikotomiura/self-resolution-measure`）の `paper/` に置く（前タスク判断 6）。
  ⚠️ EMSE の規程「LaTeX はサブフォルダを使わない」→ `paper/` の中はフラット（図・`.bib` も同じ階層）。
- ★ **原稿の数値は手で写さない。** `paper/make_results.py` が `results/metrics.json` から `paper/results.tex`（マクロ定義）を生成し、
  本文は `\R{d1/strict/DF1/ne}` の形で引く。未定義のキーは `\errmessage` でビルドを止める（黙って空欄にしない）。
  `paper/build.sh` は `results.tex` を生成し直して、コミット済みのものと `cmp` で比べる（結果と原稿の食い違いを機械で検出する）。
- ★ 本文だけにある導出値（例: 未解決の episode のうち参照なしの割合 Q）も `make_results.py` が counts から計算する（手計算を本文に入れない）。
- テンプレートのクラス・bst は `paper/build.sh` が公式 zip から SHA-256 照合で取り込む（判断 5）。
- 書き順は判断 3（Results から）。主張は前タスク `outline.md` の C1–C7 に 1 対 1 で対応させる。

## 変更対象

| リポジトリ | ファイル | 内容 |
|---|---|---|
| self-resolution-measure | `paper/main.tex` | 原稿（`sn-jnl`・`sn-basic`） |
| self-resolution-measure | `paper/refs.bib` | 参考文献（下の対応表） |
| self-resolution-measure | `paper/make_results.py` | `results/metrics.json` → `paper/results.tex`（標準ライブラリのみ） |
| self-resolution-measure | `paper/results.tex` | 生成物（コミットする。`build.sh` が再生成と `cmp`） |
| self-resolution-measure | `paper/build.sh` | テンプレートの取り込み・`results.tex` の照合・Tectonic でのビルド |
| self-resolution-measure | `.gitignore` | `paper/sn-jnl.cls`・`paper/sn-basic.bst`・ビルドの中間物・PDF |
| self-resolution-measure | `README.md` | Layout に `paper/` を追記 |
| GSE-prototype | `.steering/20260928-p321-paper-draft/` | 本記録 |
| GSE-prototype | `docs/references.md` | 新たに引く文献の追記（append-only） |

## 参考文献の対応表（`refs.bib` のキー ↔ `docs/references.md`）

| bib キー | references.md | 備考 |
|---|---|---|
| `alaboudi2021` | [P321] | arXiv v1（DataCite） |
| `alaboudi2023` | [P433] | EMSE 28(5):117 |
| `li2026` | [P434] | PACMSE 3(FSE) FSE049 |
| `hellas2023` | [P435] | |
| `karabenick2011` | [P436] | |
| `almeda2017` | [P126] | |
| `ich2020e9r1` | [V170] | 著者欄は `{ICH}`（本文では ICH (2020)） |
| `gooley1999` | [V171] | |
| `ferreiragonzalez2007` | [V172] | |
| `austin2016` | [V61] | |
| `shepperd2014` | [V173] | |
| `tantithamthavorn2016` | [V174] | ⚠️ 本文未読 → 内容は [V175] の要旨が伝える範囲だけで書いた |
| `shepperd2018reply` | [V175] | |
| `shepperd2018replication` | [V176] | |
| `ralph2018` | [V177] | ⚠️ 要旨のみ |
| `sjoberg2023` | [V178] | ★ 本文を読んだ（2026-09-28） |
| `wilson1927` | [V179] | 新規登録。⚠️ 本文未読（書誌で引くだけ） |
| `brown2001` | [V180] | 新規登録。要旨で照合 |
| `cameron2008` | [V181] | 新規登録。⚠️ 回帰の文脈 → 類比 |
| `cameron2015` | [V182] | 新規登録。⚠️ 回帰の文脈 → 類比 |
| `hesterberg2015` | [V183] | 新規登録 |

★ 21 項目 = `refs.bib` の 21 項目 = PDF の文献リストの 21 件（2026-09-28 に照合）。書誌は doi.org の BibTeX（Crossref / DataCite）から取り、キー・エスケープ・頁範囲だけ整えた。

## 検査（受け入れ条件との対応）

| 何を | どうやって |
|---|---|
| 原稿の数値 = 解析結果 | `build.sh` が `results.tex` を再生成して `cmp`。未定義キーはビルドが止まる |
| PDF が組める | `bash paper/build.sh` exit 0（Tectonic・⚠️ XeTeX。pdfLaTeX での確認は投稿前の残課題＝判断 2） |
| 書いてはいけないこと | `outline.md` の各項目を英語の禁止句に直して `grep`（検査の句と結果は tasklist に記録） |
| 要旨の語数・キーワード数 | 要旨を抜き出して数える |
| 引用 = `.bib` = references.md | ビルドのログに未定義の引用が無い ＋ 上の対応表 |

## テスト戦略

- 対照（実施した手順・論文用リポジトリの複製で）: ① `main.tex` の `\R{...}` を 1 か所だけ存在しないキーに書き換える → LaTeX が `unknown key` で exit 1（Step 2 の `cmp` は `results.tex` を変えていないので通る＝`\errmessage` を切り分けて確かめた）／ ② `metrics.json` の値を 1 つ変える → Step 2 の `cmp` が赤 ／ ③ 主張を偽にする値 → `claims()` が止める ／ ④ 無変更 → exit 0 ／ ⑤（1 巡目の後）ログを出さない偽の Tectonic → 古いログを消したうえで「main.log was not produced」で exit 1。
- ★ 1 巡目の後、③ の型を `python paper/make_results.py --selftest` に移した（10 通りの改変がすべて止まり、無変更は通る）。`build.sh` Step 2 が毎回これを回す。
- レビュー: `/cross-review` 2 巡（Codex ＋ code-reviewer）＋ security-checker（`finish-task` Step 3）。

## ロールバック計画

- 論文用リポジトリの `paper/` は新規ディレクトリで、解析（`analysis/`・`results/`・`config.json`）には触らない → `paper/` を消せば元に戻る。
