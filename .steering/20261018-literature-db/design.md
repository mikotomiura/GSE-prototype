# 設計

## 実装アプローチ

2026-10-18 の下書き（`scripts/refdb/draft/` の 1〜8）を、1 本のコマンド `scripts/refdb/build.py` にまとめる。正しさの基準は、2026-10-18 に Drive へ置いた実物（`GSE文献DB_v2_2026-10-18.csv` ほか）で、同じ時点の枝の commit を読ませて件数と列の中身を突き合わせる（テストではなく、実データでの照合の手順として残す）。

```
python3 scripts/refdb/build.py [--config scripts/refdb/config.json] [--branches origin/main,origin/docs/x]
                               [--out DIR] [--keep SHEET.csv|SHEET.json] [--rekey OLD=NEW ...] [--keep-orphans]
                               [--fetch] [--cache ~/.cache/gse-refdb] [--no-bib]
```

- 読む枝・研究の筋の対応表・枝の短い名前・人が書く列（読んだ・メモ）は `scripts/refdb/config.json`（判断 5）。`--branches` で上書き。枝は `git show <枝>:<path>` で読むので、作業ツリーを切り替えない。`git fetch` はしない（README で先に打つ）。
- 出力先の既定は `~/.cache/gse-refdb/out/<YYYY-MM-DD>/`、`--out` で Drive の同期フォルダへ（判断 6）。
- ネットは `--fetch` のときだけ（判断 7）。キャッシュは `~/.cache/gse-refdb/{abstracts,csl_raw}.json`（2026-10-18 のものをそのまま使う）。
- 読んだ・メモは `--keep` で渡す。CSV（シートの「一覧」を書き出したもの）か、Sheets の `get_values` の返り値（2 次元の配列の JSON）。key の列で結び直す。正本に無い key にメモがあれば止める（終了コード 3）。`--rekey` か `--keep-orphans` で進める（判断 8）。

### 出力（すべて `--out` の下・ファイル名に日付）

| ファイル | 中身 |
|---|---|
| `GSE文献DB_<日付>.csv` | 20 列・UTF-8 の BOM 付き（シートの「一覧」へ貼るもの） |
| `GSE文献DB_<日付>.html` | 検索のページ（`template.html` の `__DATA__`・`__STRANDS__`・`__SUB__` を置き換え） |
| `GSE文献DB_<日付>.csl.json` | CSL-JSON |
| `GSE文献DB_<日付>_biblatex.bib`・`_bibtex.bib` | pandoc で CSL-JSON から変換 |
| `missing_summaries.json` | 要約が無い文献（カードから引かれているもの）。要約を書く依頼の入力（key・題・出典・接地・手元の抄録） |
| `manifest.json` | 読んだ枝と commit・件数（文献・要約・カードでの記述・番号の衝突・CSL をキャッシュから作った数 / 最小限で作った数）・結び直した読んだ・メモの数 |

### 処理の段（下書きとの対応）

1. `collect`（下書き 1）: 各枝の `docs/references.md` の行を読む。8 列と 7 列の行を扱う。key でまとめ、引用を拾ってカード / カード外に分ける。
2. `claims`（下書き 2）: カードの表の行と `### ` の見出しから記述と温度を拾う。
3. 要約の結合: `docs/literature/refdb/summaries.json` を key で引く。
4. `rows`（下書き 7）: 20 列の行。研究の筋はカードのファイル名 → 筋の対応表。URL が空なら DOI / arXiv から補う。年は出典の文字から。
5. `page`（下書き 6）・`csl`（下書き 8）・`bib`（pandoc）。
6. `fetch`（下書き 3・5・`--fetch` のときだけ）: `scripts/refdb/fetch.py`。メールアドレスは送らない。

## 変更対象

### 新規作成するファイル
- `scripts/refdb/build.py` — 上の 1〜5 と引数・出力
- `scripts/refdb/fetch.py` — 抄録と CSL の取得（キャッシュつき）
- `scripts/refdb/config.json` — 読む枝・枝の短い名前・研究の筋の対応表・人が書く列
- `scripts/refdb/template.html` — 下書きから移す（件数の文を `__SUB__` に）
- `scripts/refdb/summary_prompt.md` — 要約を書く依頼文
- `scripts/refdb/README.md` — 作り直しとシート・ページへの反映の手順
- `scripts/tests/test_refdb_build.py` — 下のテスト
- `scripts/refdb/merge_summaries.py` — 探索役が書いた要約を検査して `summaries.json` に足す（形・key・抄録との 15 語の重なり・材料に無い数値）

### 修正するファイル
- `.claude/commands/literature-review.md` — 最後に「DB を作り直す」段を足す
- `.github/workflows/ci.yml` — テストを配線する（`check-tests-are-wired.sh`）

### 削除するファイル
- `scripts/refdb/draft/` — 1 本にまとめた後に消す（手順の記録は git の履歴と README に残る）

## 影響範囲

repo のほかのコードからは呼ばれない。`docs/references.md` は読むだけで書かない（判断 1）。

## 既存パターンとの整合性

- `scripts/*.py` は標準ライブラリだけ・`python3 -m unittest scripts.tests.test_*` で CI に載せる形（`test_build_analysis_db.py` と同じ）。
- 枝の読み元は関数で差し替えられるようにし、テストは一時ディレクトリに枝の中身を作って `DirSource` で読む（git もネットも使わない）。fixture のファイルは置かない。

## テスト戦略

- 単体: 8 列 / 7 列の行・接地に ` | ` を含む行／CSL の題が配列・`issued` に null や文字・空になったら欄ごと外す／年が出典に無い／番号の衝突の印／名前空間 P・V・PV／URL の補い／研究の筋（カード外・未引用）
- 結び直し: 読んだ・メモが key で同じ行に戻る／消えた key で止まる（終了コード 3）／`--rekey`・`--keep-orphans`／CSV と get_values の JSON の両方
- 件数: 一時ディレクトリの枝で文献・要約・カードでの記述の数が manifest に正しく出る
- 実データ: 2026-10-18 の commit（main 5d7c53be・tangibility 8ae9c61d・c-outline 46910d1c・core1 3fa31e0b・core2 0914f063・motivation 32e76be2）で作り、906・675・576 と、2026-10-18 の CSV の列ごとの一致を見る

## ロールバック計画

新しいファイルだけなので、枝ごと捨てられる。シートは作り直しの前に「一覧」を書き出して残しておく（README の手順）。
