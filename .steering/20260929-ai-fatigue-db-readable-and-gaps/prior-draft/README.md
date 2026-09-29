# 前回のセッションの未完成の下書き（参考・未レビュー・未実行）

⚠️ **ここにあるものは、前回のセッション（2026-09-29 00:47〜00:53）がコミットせずに止まっていた作業の写しである。** レビューも実行もしていない。
一次は worktree `C:\GSE-ai-fatigue-appraisal`（ブランチ `docs/ai-fatigue-db-appraisal`・PR #258 でマージ済み）の作業ツリーにあり、
その worktree が消されても失われないよう、2026-09-29 に写した（元のファイルは変更していない。写しの SHA-256 は元と一致）。

| ファイル | 何か | 元の場所 |
|---|---|---|
| `judge_xlsx.py` | ★ **判定者用ファイル**（AI の判定を 1 つも含まない・研究者が判定者 1 として独立判定するためのもの）を作るスクリプト。冒頭に研究者の発言「独立判定のうちの一つは私が行う感じになります」 | `archive/scripts/judge_xlsx.py`（未追跡） |
| `data_d.py` | 1 論文 1 行のまとめ（SUMMARY）・課題 T01〜T19・アイディア G01〜G09 | `archive/scripts/data_d.py`（未追跡） |
| `uncommitted-assemble-build_xlsx.patch` | `assemble.py`・`build_xlsx.py` へのコミットされていない変更（上の 3 つをシートにする準備・`row_height` など） | `git diff` |

- 課題・アイディアの中身は、今回の `../issues.md`（issue 34 件）に取り込み済み（対応表は `../decisions.md` 判断 2）。
- ★ **判定者用ファイルは、サーヴェイとアイディアのまとめができた後に仕上げる**（研究者の方針・`../decisions.md` 判断 11）。そのときの出発点がこの `judge_xlsx.py`。
  ⚠️ `judge_xlsx.py` は `build_xlsx.py` の**未コミットの版**（`row_height` を持つ版）を import する。そのまま動かすにはパッチを当てるか、`row_height` を自前で持たせる（今回の `../scripts/build_readable.py` が自前で持っている）。
  ⚠️ 判定者用ファイルに AI の判定・懸念の語が入っていないことを**機械で確かめる**（`judge_xlsx.py` の `FORBIDDEN_LABELS` / `FORBIDDEN_IN_SHEET`）。変異で赤になることも確かめる。
