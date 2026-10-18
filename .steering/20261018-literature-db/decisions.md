# 重要な設計判断

## 判断 1〜4（2026-10-18・研究者・AskUserQuestion・4 問とも推奨どおり）

- **判断 1 正本**: 書誌と接地は `docs/references.md` が正本のまま（採番・append-only の規約と `check_citations.py` がそのまま効く）。シートはその写しに、読んだ・メモ・自分のタグなど人が書く欄を重ね、その欄だけはシートが正本。ページと .bib はシートと同じデータから作る。
- **判断 2 更新の流れ**: `/literature-review` の最後の段に「新しい書誌の要約を書き、DB を作り直してシートとページに反映する」を足す。全件の作り直しは 1 つのコマンドでもできる。
- **判断 3 枝**: 枝 `chore/literature-db`・タスク名 `literature-db` を origin/main から別の worktree（`/Users/johnd/GSE-prototype-literature-db`）で切った。作業中の枝の書誌も読めるよう、読む枝は設定で列挙する。
- **判断 4 要約**: 2026-10-18 に書いた 675 件の要約・特徴を `docs/literature/refdb/summaries.json` で持つ。抄録は repo に入れず、手元のキャッシュ（`~/.cache/gse-refdb/`）だけにする。

## 前提（研究者の言葉）

- 「スプレッドシート基本の上で一つに繋げておくとより楽かも。今後の研究を行う上でもこの仕組みを入れると楽かもね」（2026-10-18）
