# 次セッション — 2 本目の論文（EMSE-D-26-01273）の arXiv（endorsement の後）と、査読への対応

> 作成: 2026-09-29（EMSE への投稿の後）。改訂: 2026-09-30（arXiv の endorsement の返事待ちで区切った）。
> ⚠️ **このメモを一次資料にしない。** 状態は着手時に測り直す（arXiv の下書き・endorsement・EMSE の状態・Zenodo・GitHub）。
> 一次の記録: `.steering/20260929-p321-paper-submission-prep/decisions.md`（判断 1–20。★ arXiv は **判断 18（規程）・19（ソースと研究者の選択）・20（投稿画面の実物）**）・`tasklist.md` §6。

## §0 打ち込む用（★ endorsement が取れたら）

```
git fetch origin してから MSYS_NO_PATHCONV=1 git show origin/main:.steering/_handoff/next-session-p321-arxiv-and-review.md を読んで、§2 A を A-2（研究者のログイン）→ A-3a から進めてください（arXiv の endorsement が取れた後）。研究者の指示（2026-09-29）: 「Draft までは Claude が進め、後半の publish から研究者にお願いする」。
着手時にまず確かめる: (1) endorsement が取れたか（研究者に聞く） (2) 下書き submit/8151855 がアカウントの画面に残っているか（期限 2026-10-13） (3) SHA-256: C:/wt/arxiv-upload/arxiv-source.zip = b8bf5062185f81c34df58e703d2848409067d73a3a619edf7dddcb3badeffaa6 ／ C:/wt/emse-upload-form-text.txt（要旨）= 9744c7ceb517c155ecbb1d4b61a046ba354b5ecfa21ec99436e5d0db4d527cb4 ／ C:/wt/arxiv-upload/Miura-no-help-is-not-solved.pdf（Preview と比べる基準）= eb4a5436efaa29ce7b4ede822c548bb0490f0265a64151e11793f8148b5580d7。違えば止めて研究者に。
⚠️ main checkout（C:/GSE-prototype）は別ターミナルのセッションが使っているかもしれない。git status を見て、GSE 側の記録は git worktree で切る。
Skill: git-workflow・verify-before-claiming・subagent-delegation・browser-verification（Chrome を使う最初に必ず）・citation-ssot（原稿を直すとき）。
応答は日本語。研究者の判断が要ることは AskUserQuestion で聞く。フォームへの入力・ファイルの上げ込みは、その都度研究者に確かめてから行う。ライセンス・規約への同意・最後の Submit は研究者。
```

⚠️ Windows の git-bash では `MSYS_NO_PATHCONV=1` を付けないと `origin/main:<path>` が化けて `git show` が失敗する（2026-09-30 実測）。

## §1 状態（2026-09-30 03:40 JST ごろに測った値）

- **arXiv**（判断 20）:
  - アカウント `mmiura`（研究者がログインする・Groups: cs・既定のカテゴリ cs.HC）。
  - ★ **下書き `submit/8151855`**（incomplete・**期限 2026-10-13**・編集すると延びる・期限を過ぎると消える）。Start の段で研究者が CC BY 4.0・規約への同意・著者・cs / cs.SE を入れて Continue → 逐語 "You are not endorsed for this archive. See endorsement help or request endorsement" で止まった。⚠️ **endorsement が無いと Add Files より先（上げ込み・組版・Preview・メタデータ）へ進めない。**
  - ★ **endorsement の依頼のメール**: 2026-09-30 03:21 JST に help@arxiv.org から研究者の gmail へ（cs.SE・endorse 用の URL と 6 文字のコード）。依頼文は `C:/wt/arxiv-upload/endorsement-request-filled.txt`（コードと URL を埋めた版・相手の名前・挨拶・署名の氏名は研究者が埋める）。⚠️ **コードはこの repo に書かない。** ⚠️ 知り合いの CS の研究者 1 人に送るのは研究者（この引き継ぎを書いた時点で、送ったかは未確認）。endorse できる人の条件（cs の論文が 3 か月〜5 年前に一定数・著者として登録）と探し方（abstract ページの "Which authors of this paper are endorsers?"）は `endorsement-request-draft.md` の冒頭。⚠️ メールが何を起点に届いたか（Continue か、request endorsement のリンクか）は確定していない（判断 20）。
- **EMSE**: 原稿番号 **EMSE-D-26-01273**・2026-09-29 投稿・状態 Submitted（2026-09-29 の値。着手時に EM で確かめる）。カバーレターは「査読中に arXiv（CC BY 4.0）に出して ID を知らせる」と書いた。
- **論文用リポジトリ** `C:/self-resolution-measure`（public）: main = `728e81c`・投稿した版のタグ `submission-2026-09-29` = `75ce1ff`。
- **Zenodo**: 記録 23029603・DOI 10.5281/zenodo.23029603（findable）。token は `C:/zenodo/zenodo_token.txt`（memory `reference_zenodo_token`・公開は都度確認）。
- **手元の置き場**（repo の外・⚠️ 査読の対応が済むまで消さない）:
  - ★ `C:/wt/arxiv-upload/`: `arxiv-source.zip`（arXiv に上げる 6 ファイル・判断 19）・`Miura-no-help-is-not-solved.pdf`（同じソースを手元の pdfLaTeX（TeX Live 2026）で組んだ 21 頁・Preview と比べる基準・依頼の添付）・`endorsement-request-filled.txt`
  - `C:/wt/emse-upload-form-text.txt`（題と要旨の平文・★ arXiv の要旨の欄にそのまま使う・ASCII のみ 1,582 字）・`C:/wt/emse-upload/`・`C:/wt/emse-cover-letter.txt`・`C:/wt/emse-preview-2026-09-29.pdf`
  - ⚠️ zip を作り直すときの TinyTeX は前々セッションの scratch（`C:/Users/johnd/AppData/Local/Temp/claude/C--GSE-prototype/d77d0f35-0e5a-425a-9431-c4f9ff643515/scratchpad/tools/TinyTeX`）にあるが、消えうる（判断 2 の追記で入手元と SHA-256 を記録済み）。zip は作ってあるので、原稿を変えない限り要らない。

## §2 やること

### A. arXiv（★ 次のセッションの主題・endorsement が取れた後）

済んだもの: A-0 規程（判断 18）／A-1 ソース一式（判断 19）／A-2 ログイン（判断 20）／Start の段（研究者）→ endorsement で停止（判断 20）。

| 段 | 誰 | 何 |
|---|---|---|
| A-2 | ⚠️ 研究者 | arXiv にログインする（⚠️ パスワードの入力は私が行えない）。★ Chrome を**ターミナルと左右に並べる**（タブが `hidden` だとクリックが黙って落ちる・`browser-verification` §2.0a）。⚠️ タブグループの最後のタブを閉じるとグループごと消える → 消えても `tabs_context_mcp(createIfEmpty)` で作り直せば、ログインの状態はそのまま使える（判断 20 で実測） |
| A-3a | ⚠️ 研究者 | アカウントの画面から `submit/8151855` を resume → **Start の段**（連絡先の確認・Submittal Agreement への同意・"I am submitting as an author"・**ライセンス CC BY 4.0**・Computer Science / cs.SE）→ Continue。⚠️ 前回の入力が残っているかは未確認（残っていても研究者が確かめてから押す）。⚠️ ライセンスは help の逐語 "The license chosen is irrevocable and cannot be changed."（Submit 前の incomplete のうちに Start の段で変えられるかは未確認）|
| A-3b | 私（研究者の承認の後） | **Add Files**: `C:/wt/arxiv-upload/arxiv-source.zip` を上げる。⚠️ `file_upload` ツールは「セッションに共有されたファイル」しか上げられない（ツールの説明）→ 拒否されたら研究者がファイル選択の画面で選ぶ（⚠️ ファイル入力をクリックすると私には見えないネイティブの画面が開くので、私はクリックしない）。**Check Files**: 最上位のファイル = `main.tex`（`results.tex` は `\documentclass` が無いので候補に出ないはず・判断 18）・コンパイラ = pdflatex・TeX Live 2025（既定）。削除の推奨が出たら中身を読んで研究者に確かめる（⚠️ `refs.bib` は `.bbl` があるので未使用とされうる。判断 5 で CC BY の対象に入れたので、残すかは研究者） |
| A-3c | 私 | **組版のログと Preview**: エラー・未定義の参照と引用・Overfull を読む。PDF は頁数（手元は 21 頁・TeX Live 2025 で頁割りが少しずれることはありうる）・表 5 つ・タイトル頁の ORCID の行・参考文献・Data availability の DOI を、`C:/wt/arxiv-upload/Miura-no-help-is-not-solved.pdf` と比べる。⚠️ 差があれば止めて研究者に |
| A-3d | 私（研究者の承認の後） | **メタデータ**（下の表）と **cs.HC のクロスリスト**。⚠️ cs.HC のクロスリストに別の endorsement が要るかは未確認（help に記述なし・判断 18）→ 画面で拒まれたら研究者に（主カテゴリ cs.SE だけで出すか）。⚠️ ACM-class を空で通せるかも画面で確かめる（help は "cs archives only" とだけ書く） |
| A-4 | ⚠️ 研究者 | ★ **cls と bst の同梱を再確認する**（cls の冒頭の一文 "This file may only be distributed together with a copy of the LaTeX base system." の解釈は未解決のまま研究者が受け入れたリスク・判断 19・21）→ 最後の Preview を見て **Submit**（公開の手続きに入る。⚠️ Processing の間は "you may not edit the submission"。Submitted の状態なら Unsubmit で incomplete に戻せるが、公開の予定は再送信の時刻から組み直しになる・判断 18） |

★ **入れる値**（判断 19 で研究者が選んだ・arXiv の欄は ASCII のみ）:

| 欄 | 値 |
|---|---|
| Title | `When "no help" is not "solved": outcome-agnostic self-resolution measures in two public debugging datasets` |
| Authors | `Mikoto Miura`（所属も都市も書かない） |
| Abstract | `C:/wt/emse-upload-form-text.txt` の **4 行目の本文だけ**（3 行目の見出し `Abstract:` は入れない・help "Do not include the word "Abstract""。R マクロを数値にした平文・PDF と照合済み） |
| Comments | `21 pages, 5 tables. Replication package: https://doi.org/10.5281/zenodo.23029603`（投稿先は書かない。⚠️ 頁数は arXiv の Preview の頁数に合わせる） |
| カテゴリ | 主 cs.SE ＋ クロスリスト cs.HC |
| ACM-class / Report-no / Journal-ref / DOI | 空（ACM-class は A-3d の注記） |

★ **載ったら**（A-5）: EMSE の編集部に arXiv の ID とライセンスを知らせる（Springer の規程 "Authors should disclose details of preprint posting, including DOI and licensing terms"・EM の "View Submission Correspondence" か編集部への連絡の手段を一次で確かめる・⚠️ 送る前に研究者に確かめる）／ Zenodo の記録の related_identifiers に arXiv を足す（メタデータは公開後も直せる・公開の操作は都度確認）／ README にプレプリントを書く（公開物の規律・GSE に言及しない）／ `decisions.md` に arXiv の ID を記録する。

⚠️ **endorsement が取れないまま 2026-10-13 を過ぎると下書きは消える** → 取れた後に新しく投稿を始めればよい（Start の段からやり直し）。取れる見込みが無ければ、代わりに Research Square にプレプリントを載せる道がある（判断 16・endorsement 不要）→ 研究者が決め、載せたら編集部に知らせる。

### B. 査読の結果が来たら
- 判定と査読コメントを読み、対応の方針を研究者と決める（grill）。原稿を直すなら、数値は `results/metrics.json` から生成し直書きしない（前タスク判断 6）・`bash run.sh` と `bash paper/build.sh` exit 0・`/cross-review`。
- 改訂版を出すときも EM の落とし穴（別添のタイトル頁・`.tex` は 1 つ・キーワードはセミコロン・Zenodo のリンクは無効扱い）に注意（memory `reference_springer_editorial_manager`）。
- 再現一式を変えたら、Zenodo は**新しい版**として出す（公開済みのファイルは差し替えられない）。⚠️ 波及: (a) 新しい版には新しい DOI が付く → 原稿の Data availability・README のバッジと BibTeX・カバーレターが名指ししている 23029603 を、新しい版の DOI か concept DOI（全版をまとめる DOI・記録のページで一次で確かめる）に改める ／ (b) 解析を変えたら `NOTES.md` の Deviations に追記し、原稿 §5.1 の "Seven later changes … none changed a reported value" の件数と文を更新する（凍結の主張を守る要）／ (c) 改訂版にも新しいタグを付け、arXiv にも新しい版を出す（ライセンスは版ごと）／ (d) 査読への返答書（point-by-point）と EM の改訂期限を記録する。

## §3 気をつけること

- ⚠️ Codex の台帳: 2026-09-30 の origin/main の `today` は 198,482 / 4 回（本セッションの完了時のレビューの前に見た値）。⚠️ ブランチごとに記帳されるので、回す前に origin/main と並行セッションの台帳を見る（memory `project_codex_ledger_branch_split`）。⚠️ PR #257 の 1 巡目 +81,661 / +1 回（2026-09-29・G-GEAR）は**どのブランチにも記帳されていない**（2026-09-29 の `_comment_merge_2026_09_29`）→ どちらか一方で 1 回だけ足す（二重に足さない）。merge で `today` が衝突したら和を採る（memory `feedback_codex_budget_is_a_ledger`）。
- ⚠️ 公開物（README・Zenodo の説明・arXiv の要旨とコメント・編集部への連絡）は学術的な英語・GSE に言及しない（memory `feedback_public_artifacts_academic_no_gse`）。
- ⚠️ arXiv の画面を `javascript_tool` で読むとき、リンクの `href` を丸ごと返すと、クエリ文字列を理由に出力が遮られる（2026-09-30 実測）→ `host + pathname` と引数の名前だけを返す。
