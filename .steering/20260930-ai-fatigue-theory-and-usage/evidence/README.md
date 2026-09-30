# evidence（本タスク: S-11 語の用法・S-09 理論の節）

| ファイル | 何か |
|---|---|
| `screen.py`・`test_screen.py` | 語形（N1〜N5）・一般の構成概念の語・枠組み（F-*）の正規表現（design.md §1.2・§2.3 に固定）と、その陽性・陰性の検査（`python -m unittest test_screen`）。★ 判定ではない。当たった語の文字列だけを返す |
| `fetch_abstracts.py` | 抄録を DOI で取り直す（Europe PMC・Semantic Scholar・OpenAlex・Crossref。design.md §0.3）。`records` は判定者用ファイルの archive の写しの 259 件（SHA-256 を確かめる）、`theory` は S-09 の原典・原著の固定の一覧。書誌だけを repo に、抄録は repo の外に `common.write_pair` で対にして書く |
| `run_screen.py` | 取得した抄録にふるいを当て、書誌だけの結果を `S-11/`・`S-09/` に書く。メインが読む束（抄録の全文と印）は repo の外 |
| `S-11/records_2026-09-30.json` | 259 件の取得の記録（鍵・DOI・題名・抄録が取れた情報源・文字数・OpenAlex の本文の入手）。抄録は持たない |
| `S-11/terms_2026-09-30.json` | 語形・一般の構成概念の語のふるいの結果（当たった語の文字列だけ） |
| `S-11/trace_prompt_fatigue.py`・`S-11/prompt_fatigue_trace_2026-09-30.json` | プロンプト疲れの概念分析（検索漏れ候補 No.128・129）の本体を辿った記録（Zenodo の記録の関連の識別子・Crossref・Semantic Scholar の題名の検索） |
| `S-11/prompt_fatigue_trace_2026-09-30_retry.json` | 同じ手順の回し直し（Semantic Scholar が 1 回目に 429 だったため。2 回目も 429） |
| `S-11/find_in_fulltext.py` | repo の外に保存した無料の本文（PDF・HTML・XML・docx）から、語形を含む文と手がかりの有無を標準出力に出す（本文を repo に書かない・`decisions.md` 判断 6） |
| `S-09/theory_2026-09-30.json` | 原典・原著（design.md §2.2・§2.4 の DOI のあるもの）の取得の記録 |
| `S-09/theory2_2026-09-30.json` | 逸脱で足した 2 件（Hobfoll ほか 2018・Parasuraman & Manzey 2010・`decisions.md` 判断 3）の取得の記録 |
| `S-09/frameworks_2026-09-30.json` | 枠組みのふるいの結果（当たった語の文字列だけ） |

- ★ 前タスクの `../../20260929-ai-fatigue-surveys/evidence/common.py` と `../../20260930-ai-fatigue-judge-file/evidence/search_round.py` の `clean`（タグの名前を限って除く）を import して使う。
- 抄録・本文の置き場は本セッションの scratchpad（git の外）。連絡先（メールアドレス）は学術 API に送っていない。
- ⚠️ `fetch_abstracts.py` の `get()` は、259 件と原典の取得を回した後に、許す URL の一覧と opener を引数で受け取る形に直した（`trace_prompt_fatigue.py` が Zenodo の API の根を足すため・`decisions.md` 判断 9）。既定の引数での動きは、回した版と同じ。`theory2` の一覧も回した後に足した（判断 3）。
- ⚠️ `run_screen.py`・`fetch_abstracts.py` は出力先が既にあると止まる（上書きしない）。
- ⚠️ 流用するときの注意（2026-09-30 の完了時レビュー・code-reviewer と security-checker。実行した版の振る舞いは変えていない）:
  1. `get()` は 400・404・410 を黙って `None` にし、`errors` に残さない。「エラー 0 件」は「例外 0 件」の意味にしかならない（400 は Europe PMC の TITLE の式や S2 の DOI のパスが不正でも隠れる）。流用するときは、4xx を情報源・鍵ごとに数えて書誌の JSON に残す。
  2. `get()` の `allowed` と `opener` は対で渡す約束で、コードでは強制していない（別の一覧の opener を渡すとリダイレクトの柵が崩れる。`allowed=[]` は既定の 4 つに広がる）。流用するときは opener の引数をなくし、`allowed` から `guarded_opener` を中で作る。`Retry-After` が日付の形だと `int()` で落ちる。許可外へのリダイレクトも再試行する。
  3. `title_match` は、正規化で空になる題名で `None` を返し、`fetch()` は不一致として扱わない（DOI の無い題名の検索が確かめずに採られうる。今回の DOI の無い 4 件は英語・日本語の題名で、該当しない）。Europe PMC の `rs[0]` は DOI の一致を確かめていない。DOI で引いた記録は、題名が合わなくても抄録を統合する（今回は判断 7 で事後に確かめた）。
  4. `trace_prompt_fatigue.py` は Zenodo と Crossref の失敗を捕まえず（S2 の `HTTPError` だけ）、書誌の JSON の置き場も確かめない（抄録に当たる説明文は検査済みの `abs_dir` にだけ書く）。
  5. `run_screen.py` は 2 つの出力を順に排他的に開くので、2 つ目が既にあると片方だけが残る。`load_pair` は `mode` と `input_sha256` を確かめない。
  6. `common.ensure_outside_repo` は、いまの worktree の根しか比べない（別の worktree の中は「外」と判定される）。抄録・本文の置き場は scratchpad など git の外にする（前タスクの README の注意 (1) と同じ）。
  7. `load_records()` の `open(...).read()` はファイルを閉じていない。`fetch()` の `abs_dir` の引数は使っていない。
