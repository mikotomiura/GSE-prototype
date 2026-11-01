# 引き継ぎ — CS1 打鍵データの著者から返事が来たとき

> 作成: 2026-11-02（研究者の依頼）。研究者は 2026-11-02 に著者（john.edwards@usu.edu）へメールを送った。
> このメモを一次資料にしない。事実は一次（メールの本文・Dataverse の API）で確かめ直す。

## 0 何を頼んだか

- 送った文面: `.steering/20261102-gse-public-data-landscape/cs1-contact-draft.md`（件名 "Request for access to the CS1 keystroke datasets (doi:10.7910/DVN/6BPCXN and doi:10.7910/DVN/BVOF7S)"）。
- 頼んだ範囲（判断 3）: 2019 年版（doi:10.7910/DVN/6BPCXN・505 名・ブラウザの IDE）と 2021 年版（doi:10.7910/DVN/BVOF7S・44 名・8 課題・PyCharm）の `keystrokes.csv` だけ。
- 約束したこと（返事の後も守る）:
  - 使うのは時刻と出来事の種類だけ。挿入・削除の文字は保存せずに捨てる。
  - 記述の集計だけ。個人を特定しようとしない。他のデータと結び付けない。
  - 課題文・課題の雛形と動画・調査票（`keystrokes-survey.csv`）・`students.csv`・`keystrokes-raw.csv`・実行の記録（`runs1.csv`・`runs2.csv`）は取らない・使わない。
  - 生のファイルは研究者の計算機にだけ置き、再配布しない。公開するのは集計値だけで、データと論文（[V243]）を引く。

## 1 返事の種類ごとの扱い

| 返事 | すること |
|---|---|
| 承諾（条件なし） | §2 へ。承諾のメールの日付と要点（逐語の 1〜2 文）を `.steering/<日付>-cs1-landscape/decisions.md` に写す（メールの全文や相手のアドレス以外の個人情報は repo に入れない） |
| 条件つきの承諾（同意書・用途の制限・引用の形など） | 条件を研究者と一つずつ確かめ、守れるかを AskUserQuestion で聞く。署名や同意が要るものは研究者が行う。守れない条件があれば取らない |
| 断り | CS1 を俯瞰から外したことを、俯瞰の notes（`experiments/20261102-public-data-landscape/notes.md` の「言える範囲」）ではなく新しいタスクの記録に書く。代わりのデータを探すかは研究者に聞く |
| 返事が無い | 研究者が催促するかを決める。こちらから取りに行かない（ファイルは技術的には落とせるが、termsOfAccess に従うと決めた・判断 1） |

## 2 承諾の後の作業（新しいタスク・worktree を分ける）

1. `git fetch` の後に origin/main から worktree を切る（例 `/Users/johnd/GSE-prototype-cs1`・ブランチ `docs/gse-cs1-landscape`）。`.steering/<日付>-cs1-landscape/` を作る。
2. ディスク: 2 つの `keystrokes.csv` で約 650 MB（2019 年版 455,078,162 バイト・2021 年版 193,521,644 バイト・2026-11-02 の API の値）。`df -h ~` で 3 GB を切っていたら始めない。他のトラックの中間（`~/gse-public-data/` の下）は消さない。
3. 取得: Dataverse の API でファイルの一覧を取り、`keystrokes.csv` だけを落とす（`https://dataverse.harvard.edu/api/datasets/:persistentId/?persistentId=doi:10.7910/DVN/<ID>` の `files[].dataFile.id` → `https://dataverse.harvard.edu/api/access/datafile/<id>`）。置き場は `~/gse-public-data/cs1/raw/2019/`・`.../2021/`。SHA-256 と大きさと取得の時刻を `data.md` に書く。`readme.txt` は列の定義を確かめるために読んでよい（小さい・中身は説明）。
4. 列の確かめ: 列の名前と `EventType` の種類と件数だけを数える（中身の文字は出力しない）。2019 年版と 2021 年版で列が違う（[V243] の調べでは 2019 は `X-Keystroke`、2021 は `X-Action`・`X-Metadata`・`.steering/20261031-gse-public-data-fit-ai-request/survey-datasets.md`）。人の単位（学生の ID の列）と課題の単位を確かめる。ID は repo に出さない。
5. 条件を計算の前にコミットする: 俯瞰の `conditions.md` の L1〜L6 を同じ定義で当てる。変換（出来事 → GSE の key 行）の対応表は件数を見る前に固定する。書き手の 3 割を種で取っておく。
   - 2021 年版は 1 人に複数の課題があるので、L5（人の中の揺れ）を課題を単位にして出す。1 単位が長いので、CoAuthor（約 11 分）で数え上げの揺れに埋もれた点を確かめられるかが見どころ。
   - PyCharm の補完などで入る複数の文字の挿入は、打鍵の列に入れず、別に数える（受領の数え方を濁すため）。
   - AI の提案は無い（AI 以前）。受領にあたる出来事も無い見込み。L4 は「受領の経路が無い作業」の例として扱う。
6. 変換と replay: KLiCKe（`experiments/20261101-klicke-early-stall-trigger/scripts/build_work.py`）と CoAuthor（`experiments/20261102-public-data-landscape/scripts/build_coauthor.py`）の形に倣う。replay のバイナリは `~/gse-public-data/klicke/bin/gse-replay`（SHA-256 は俯瞰の `run.sh` が照合している値）。中間は 1 本ずつ消す。
7. 結果は `experiments/<日付>-cs1-landscape/notes.md` に、言える範囲を限って書く（プログラミングの課題・米国の大学の CS1・AI 以前・ブラウザの IDE と PyCharm）。
8. 完了時に code-reviewer と /cross-review を並列で回す。docs と experiments だけなら PR なし・`[skip ci]` の `--no-ff` マージで main へ入れてよい（差分にコードと CI の設定が無いことを確かめる・直前に fetch）。

## 3 守ること

- 打鍵の本文・生のファイルを外部の LLM（Codex を含む）に送らない。メインの出力にも本文を出さない（件数と列名だけ）。
- 「Ethical use of this dataset includes avoiding attempts at reconstructing identities.」（[V243]）を守る。
- `docs/references.md` の [Vn] は append-only。CS1 は [V243] を引く（データの DOI は書誌の欄にある）。
