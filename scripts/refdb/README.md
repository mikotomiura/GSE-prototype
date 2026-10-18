# 文献 DB（scripts/refdb/）

各枝の `docs/references.md`（書誌の正本）をまとめて、Google スプレッドシート「GSE 文献DB」の「一覧」・検索のページ・書誌のファイル（BibLaTeX / BibTeX / CSL-JSON）を作り直す仕組み。決めたことは `.steering/20261018-literature-db/decisions.md`（判断 1〜8）。

- 書誌と接地の正本は `docs/references.md`。シートからは書き戻さない（判断 1）。
- シートで人が書く列（読んだ・メモ）だけはシートが正本。作り直しの前に必ず読み、key で結び直す。
- 要約と特徴は `docs/literature/refdb/summaries.json`。抄録は著作物なので repo に入れず、手元のキャッシュ `~/.cache/gse-refdb/` だけに置く。

| ファイル | 役割 |
|---|---|
| `build.py` | 作り直しのコマンド（下の §1） |
| `fetch.py` | 抄録と CSL の取得（`build.py --fetch` のときだけ・キャッシュにあるものは取り直さない） |
| `../requirements-dev.txt` | xlsx を書く openpyxl（`~/.venvs/gse-provision` に入れてある。無ければ `--no-xlsx`） |
| `config.json` | 読む枝・枝の短い名前・研究の筋（カードのファイル名に含まれる語 → 筋）・人が書く列 |
| `template.html` | 検索のページのひな形 |
| `summary_prompt.md` | 要約を書く依頼文（§3） |
| `merge_summaries.py` | 返ってきた要約を検査して `summaries.json` に足す（§3） |

## 外にあるもの

- **文献 DB の本体はスプレッドシート「GSE 文献DB」**: https://docs.google.com/spreadsheets/d/1v7frJm2a6BkXzepEpglB62AT_2c3t0NzJ2mNA8UfRFw/edit （シート: 検索・集計・一覧・凡例。「一覧」のシート ID は 2123943520）。CSV はこのシートへ値を流し込むための受け渡し用で、DB ではない（§2）
- 検索のページ: https://claude.ai/artifact/Js8ZBgzkWAZBHdgrzqjwSA （同じ URL に出し直す）
- Google Drive のフォルダ GSE の中の「文献DB」（手元では Drive for desktop の同期フォルダ。パスにメールアドレスが入るので、ここには書かない。2026-10-18 に研究者が決めた並べ方）:
  - `文献DB/`: 置くのは 3 つだけ（判断 17）。スプレッドシート「GSE 文献DB」（本体）、`GSE文献DB.xlsx`（一覧・書誌・説明を 1 つにした写し）、`GSE文献DB.bib`（BibTeX・論文の原稿が使う形）。xlsx と .bib は日付の無い名前で、作り直すたびに上書きする
  - `文献DB/作業/`: `build.py` の出力先（日付つきの CSV・`.html`・`.csl.json`・`.bib` 2 本・`.xlsx`・`manifest.json`・`missing_summaries.json`）
  - `文献DB/作業/手作り_2026-10-18/`: 2026-10-18 に手で作った版（`GSE文献DB_2026-10-18.csv`・`GSE文献DB_v2_2026-10-18.csv`・`.csl.json`・`.bib` 2 本）と、最初の差し替えの前の「一覧」の書き出し（`一覧_差し替え前_2026-10-18.csv`）。§6 の照合の正解はここにある

## 1. 作り直す

```bash
git fetch origin                                  # build.py は fetch しない
PY=~/.venvs/gse-provision/bin/python                       # openpyxl が入っている
$PY scripts/refdb/build.py --keep <シートの一覧の値> --out "<文献DB/作業>" --deliver "<文献DB>"
$PY scripts/refdb/build.py --verify "<文献DB/作業>"          # 「揃っている」を確かめる
```

- 読む枝は `config.json` の `branches`。作業中の枝を足すときは `config.json` に足すか、`--branches origin/main,origin/docs/x` で一時的に上書きする。枝が main に入ったら設定から外す（判断 5）。
- 出力先の既定は `~/.cache/gse-refdb/out/<日付>/`（判断 6）。試しに回すときは `--out` を付けない。
- 新しい書誌の抄録と CSL は `--fetch` で取る（判断 7）。タイムアウト・429 などの一過性の失敗はキャッシュに残さず、次の `--fetch` で取り直す（404 だけ「無い」と覚える）。付けないとキャッシュだけで作り、キャッシュに無い書誌は手元の題・出典・年から最小限に作る（件数を表示する）。
- `.bib` には pandoc が要る。無ければ `--no-bib`。`.xlsx` には openpyxl が要る。無ければ `--no-xlsx`。
- `--deliver <文献DB>` は、作り終えて出力先へ移した後に、`GSE文献DB.xlsx` と `GSE文献DB.bib` を日付の無い名前で上書きする。2 本を一時の名前で写し終えてから入れ替えるので、片方だけ新しくなることは無い。`--no-xlsx`・`--no-bib` とは一緒に使えない。
- xlsx のバイト列は、同じ入力でも回すたびに変わる（openpyxl が保存の時刻を書く）。同じ入力かどうかは CSV のハッシュで見る。xlsx のセルが 32,767 字を超えると止まり、xlsx に書けない制御文字は外して `manifest.json` の `xlsx_removed_control_chars` に数える。
- `--keep` のシートの値は、Sheets の `get_values` の返り値をそのまま渡してよい（拡張子が `.txt` でも中身が JSON なら読む）。
- ある時点の枝を読み直すときは `--pin 枝=commit`（2026-10-18 の照合は §6）。

出力は出力先の中の一時のフォルダ（`.refdb-*`）で全部作ってから、1 ファイルずつ出力先へ移す。作る段で止まった回（pandoc の失敗・読んだ・メモの検査など）は、出力先が前の回のまま残る。移す段で止まった（ディスクが一杯・Ctrl-C）ときは新旧が混ざりうる。`manifest.json` は最後に移し、ほかの成果物すべての SHA-256 を `sha256` に持つので、使う前に `python3 scripts/refdb/build.py --verify <出力先>` で確かめる（「揃っている」と出なければ回し直す）。電源断などで `.refdb-*` が残ったら消してよい。`manifest.json` の `formula_like_cells` が 1 以上なら、`= + - @` で始まるセルがあり、Google スプレッドシートで数式として読まれうるので、貼る前に確かめる。

出るもの（ファイル名に日付）: `GSE文献DB_<日付>.csv`（20 列・BOM 付き）・`.html`（検索のページ）・`.csl.json`・`_biblatex.bib`・`_bibtex.bib`・`missing_summaries.json`（カードから引かれているのに要約が無いもの）・`manifest.json`（読んだ枝の commit と件数）。

### 読んだ・メモを結び直す（判断 8）

1. 作り直す前に、シートの「一覧」の値を読む。Sheets の MCP で `get_values`（範囲 `一覧!A1:T`）を呼び、返った JSON をそのままファイルに書いて `--keep` に渡す（`{"values": [...]}` のままでよい）。シートから CSV を書き出して渡してもよい。
2. `読んだ` はチェックボックスで、付けていない行は `FALSE` で返る。それは書いた内容に数えない。
3. 読んだ・メモがある行の key が正本から消えていると、終了コード 3 で止まり、消えた key とメモを表示する。直った key が分かれば `--rekey 旧key=新key`（何度でも）、分からなければ `--keep-orphans` で表の末尾に状態「正本に無い」・ID「—」の行として残す。
4. ほかにも、読んだ・メモを黙って失いうる形では止まる。どれも出力先には何も書かない（前の回のまま）。
   - 終了コード 2: シートの見出しに `key`・読んだ・メモの列が無い（列の名前を変えた・消した）／JSON に `values` が無い／表が空
   - 終了コード 3: key が空の行に書いた内容がある／同じ key の行が 2 つあり内容が違う／`--rekey` で 2 つの key が同じ key に入る
   直す場所はシートか `--rekey` で、`references.md` の key をシートに合わせて変えない（書誌の正本は references.md）。

## 2. シートに反映する

906 行を Sheets の API で送ると量が大きすぎるので、CSV を Drive で変換して写す（memory `abstract-sources-and-drive-ids`）。

1. `--out` で `文献DB/作業` に CSV を書く（§1）。
2. Chrome で Drive のその CSV を開き、「Google スプレッドシートで開く」を押す。同じフォルダに一時のシートができる。
3. 一時のシートの最初のシートを、`copy_sheet_to_another_spreadsheet` で「GSE 文献DB」へ写す。
4. 「一覧」の `A2:T` を消してから（行が減ったとき古い行が残らないように）、写したシートの値を `copyPaste`（`PASTE_VALUES`）で「一覧」の `A1` へ貼る。
5. 「一覧」のフィルタの範囲（`basicFilter`）を新しい行数に合わせる。
6. 写したシートを「GSE 文献DB」から消し、一時のシートをゴミ箱へ。
7. 確かめる: 「集計」の「全体（重複なし）」が `manifest.json` の `works` と同じ・「検索」の B1 で筋を 1 つ選んで行が出る・読んだ・メモが入っている行を 2〜3 件、作り直す前の値と見比べる。

「検索」と「集計」の式は `'一覧'!A2:A` のような終わりのない範囲なので、行数が変わっても直さなくてよい（2026-10-18 に確認）。

## 3. 要約が無い文献に要約を書く

1. `missing_summaries.json` を 100 件ほどの束に分ける。
2. 束ごとに `summary_prompt.md` の依頼文を Sonnet の探索役に渡す（並列でよい）。
3. 返ってきた JSON を検査する: `python3 scripts/refdb/merge_summaries.py <返った.json> --input <束の入力.json>`。
   - 誤り（形・key の過不足・抄録との連続 15 語以上の重なり）があれば書かずに止まる。直させてから回し直す。
   - 写しの検査は英語の語で数えるので、抄録を日本語に訳して写したものは見つけられない。依頼文の「自分の言葉で書く」と、抜き取りで目で読むことに頼る。
   - 「数値を目で確かめる」は止めない。入力に無い数値の一覧なので、言い換え（「二つ」→「2」など）か、推し量った数値かを目で見分け、推し量ったものは直す。
4. 通ったら `--write` を付けて `summaries.json` に足し、§1 を回し直す。
5. OpenAlex の抄録は、`p < 0.025` のような不等号の前後の文が欠けることがある（memory `abstract-sources-and-drive-ids`）。数値の要約で抄録が不自然に切れていたら、Europe PMC の版と比べる。

## 4. 検索のページを出し直す

`GSE文献DB_<日付>.html` を、Artifact の `https://claude.ai/artifact/Js8ZBgzkWAZBHdgrzqjwSA` に出し直す（同じ URL に。新しい URL にしない）。出し直す前に Artifact の read で今の版を読む決まりがある。

この HTML は文字コードの宣言を持たない（Artifact が出すときに付ける）。手元のファイルをそのままブラウザで開くと文字化けして動かないので、手元で見るときは先頭に `<!doctype html><meta charset="utf-8">` を足した写しを開く（2026-10-18 に、そうした写しで 906 件・筋の件数・検索を確かめた）。

## 5. 書誌のファイル

`.bib` 2 本と `.csl.json` は §1 で `文献DB/作業` に出る。`--deliver` で `文献DB` に写るのは BibTeX の 1 本（`GSE文献DB.bib`）だけ（論文の原稿 2 本がどちらも BibTeX を使うため・判断 17）。xlsx の「書誌」のシートにも、1 行 1 件で同じ BibTeX の項目が入る。引用キーは最初の番号（例 `P534`）。番号の衝突で重なるときは key の末尾 8 字を足す（例 `P485_okp7zsv1`）。`keyword` に研究の筋、`note` に「GSE <ID> ｜ <要約>」。

## 6. 2026-10-18 の版との照合

2026-10-18 に手で作った版（`文献DB/作業/手作り_2026-10-18/` の `GSE文献DB_v2_2026-10-18.csv` ほか）と同じ時点を読むには:

```bash
python3 scripts/refdb/build.py --date 2026-10-18 \
  --pin origin/main=5d7c53be --pin origin/docs/tangibility-design=8ae9c61d \
  --pin origin/docs/ai-fatigue-c-outline=46910d1c --pin origin/docs/ai-fatigue-core1-item-analysis=3fa31e0b \
  --pin origin/docs/ai-fatigue-core2-discriminant=0914f063 --pin origin/docs/ai-fatigue-motivation-claims=32e76be2
```

件数は 906 件・要約 675・カードでの記述 576 件（1,571 行）・番号の衝突 48 で一致する。列の中身の違いは、手で作った版の誤りを直したもの（`.steering/20261018-literature-db/decisions.md` の判断 9）。

## テスト

```bash
python3 -m unittest scripts.tests.test_refdb_build -v
```

git もネットも使わない（一時ディレクトリに枝の中身を作って読む）。CI の `Literature DB build test` で走る。
