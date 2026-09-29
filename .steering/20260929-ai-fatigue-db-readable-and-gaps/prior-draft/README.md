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
- ★ **判定者用ファイルは、サーヴェイとまとめができた後に仕上げる**（研究者の方針・`../decisions.md` 判断 11）。そのときの出発点がこの `judge_xlsx.py`。

## ★ 仕上げるときに直すこと（2026-09-29 のレビューで分かったこと）

1. ⚠️ **記入済みのファイルを上書きしない**（security-checker MEDIUM）: 出力先が既にあっても `os.replace` で置き換えるので、候補を足して作り直すと研究者の判定が黙って消える。→ 出力先があれば止める（`--force` のときだけ上書き）か、`../scripts/build_readable.py` と同じく記入欄を ID で引き継ぐ。試験に「既存の出力先で止まる」を足す。
2. **import 先**: `build_xlsx.py` の**未コミットの版**（`row_height` を持つ版）を import する。そのままでは写した場所で `ImportError` になる → パッチを当てるか、`row_height` を自前で持たせる（`../scripts/build_readable.py` が自前で持っている）。
3. **出力先**: 既定の出力先が写した場所では `.steering/20260929-…/judge/` になる（docstring は `archive/judge/`）→ 出力先を明示し、存在しないディレクトリは作らずに止める。
4. **DOI のリンク**: `https://doi.org/` に DOI を URL エンコードせずにつないでいる → `urllib.parse.quote` を通す。
5. ⚠️ **AI の判定・懸念の語が入っていないことを機械で確かめる**（`FORBIDDEN_LABELS` / `FORBIDDEN_IN_SHEET`）。変異で赤になることも確かめる。サーヴェイで足した候補を判定対象に入れるかは研究者が決める。
6. ⚠️ `data_d.py` の G03 は [P207]・[P208] を「自我消耗の再現性の問題」としているが誤り（`../decisions.md` 判断 6）。文面を使い回さない。
