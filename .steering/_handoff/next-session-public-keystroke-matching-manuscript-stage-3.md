# 次のセッション（Mac）: 照合の論文 —— 段 3: 全員の付録と、R-DP の R0 に比べる有用性を入れる

作成 2026-10-29（判断 81 の後）。この機械は Mac。G-GEAR の作業はこのセッションでしない。

| 段 | 届くもの | 書く所 |
|---|---|---|
| 済み | `main.json`・`enja15_main.json`・探索 3〜5 | §7・序論・考察・結論・抄録（判断 79） |
| 済み | `main_a4.json`・`main_a4_without_cpu_writer.json` | 表 2 の A4 の行・§7.4・§7.5・付録 E の KeyTAR（判断 80） |
| 済み | `exploratory_unicity.json`・`exploratory_dp.json` | §7.7 の 1 文・付録 D の表 6〜8（判断 81） |
| 済み | `exploratory_dp_utility_r0.json`（R-DP の R0 に比べる有用性） | 付録 D の表 8 と「Tables」の段落の角括弧（判断 82・2026-10-29） |
| **3（このセッション）** | `main_all.json`（全員の付録） | 付録 E の Results on all writers |
| 完成 | ― | 草稿の完成（判断 76）→ attack-me round 3 |

## 新しいセッションで最初に打ち込む文

```
.steering/_handoff/next-session-public-keystroke-matching-manuscript-stage-3.md を読んで、照合の論文に段 3 の結果を入れて。
```

## 始める条件（揃っていなければ、揃った方だけ書くか、書かずに止まる）

- `results/main_all.json`: G-GEAR の `all` の段（2026-10-28 18:12 UTC 開始・約 10〜12 日・11 月中旬の見込み）が終了コード 0 で終わり、原稿の枝に merge され、notes.md に終了時刻と SHA-256 の記録がある。
- `results/exploratory_dp_utility_r0.json`: G-GEAR の引き継ぎ `next-session-public-keystroke-matching-dp-utility-r0-ggear.md` が済み、notes.md の D5 に陽性対照の結果がある。
- 2 つは独立。片方だけ届いていれば、その方だけ書き、もう片方の角括弧は残す。
- worktree は `/Users/johnd/GSE-wt-matching-manuscript`（枝 `docs/public-keystroke-matching-manuscript`）。始める前に `git fetch` と `git merge --ff-only origin/docs/public-keystroke-matching-manuscript`。

## やること

1. `main_all.json`: 開く前に、`main.json` と重なる葉（標本の 500 人の件をキャッシュから使い回した部分ではなく、集計が別になる）の関係を notes.md D4 で確かめる。全員の付録は A0〜A3 の全文（`appendix-results.tex` の 201 行目の角括弧）。`make_tables.py` に関数を足し、既存の生成ファイルが変わらないことを `git status` で確かめ、止まる条件は壊した写しで確かめる（判断 80・81 と同じ）。
2. （済み・判断 82）`exploratory_dp_utility_r0.json`: 表 8（`explore-dp-score.tex`）に R0 との相関（平均）を足すか、R0 との比の中央値の表を足す。`utility-r0.tex`・付録 E の有用性の表と同じ量と書き方にそろえる。R3 の値が `main.json` と違えば止まる条件を入れる。付録 D の「Tables」の段落の角括弧と、その上の LaTeX のコメント（D5）を直す。§7.7 の文は変えない（本文の余白は 0）。
3. 数値と量の語を集計の JSON と機械で照らす（`verify-before-claiming`）。
4. 頁を測る（`paper-write/length-log.md` の数え方）。付録だけなので本文は動かない見込みだが、測る。⚠️ 余白は 0。
5. ビルド（エラー 0・未定義 0・overfull は今 2）・PDF を画像で見る（表の幅。判断 80・81 で `\multicolumn` の行が表を広げた）・文体の門（違反 0）・`length-log.md` に 1 行・`../20261012-public-keystroke-matching-prereg/decisions.md` に判断 83・tasklist.md・commit・push。
6. 草稿の完成（判断 76）の残り: 倫理の公開元への連絡の角括弧（下の「別の手続き」）・open science の匿名リンク。揃ったら attack-me round 3 の引き継ぎを書く。

## 道具

- テンプレート: `submission-template-2027.zip`（SHA-256 `b1abbcc0…`）。前のセッションの scratchpad（`/private/tmp/claude-501/-Users-johnd-GSE-prototype/c7596314-4e54-4c40-9a09-b78b8bb51140/scratchpad/tpl/`）に写しがある（消えていれば BUILD.md の手順で取り直す）。`bash build.sh <PoPETS-2027-latex-template> <出力先>`。
- 文体の門: repo の根から `python3 .steering/20260927-ime-observation-paper-eval-design/issues/_style_check.py --root . papers/keystroke-log-release-matching`。
- 頁: `pdftohtml -xml` で "Ethical Considerations" の見出しの位置。

## 読む物

- `paper-write`（`/Users/johnd/GSE-wt-paper-write-skill/.claude/skills/paper-write/SKILL.md`）と `verify-before-claiming`。書く前に読む。
- 判断 79〜81（`../20261012-public-keystroke-matching-prereg/decisions.md`）・notes.md の D4・D5。
- 詰まった所は `/Users/johnd/GSE-wt-paper-write-skill/.steering/20261024-paper-write-skill/field-trial.md` の続きに書く（候補 16・17 が判断 81 で足された）。Skill はまだ直さない。

## 守ること

- 脅威モデル・攻撃者・手順は凍結した事前登録から変えない。変えるときは notes.md の「逸脱」に書く。
- 集計の JSON だけを読む。打鍵の記録・本文・キャッシュを開かない。外部 LLM（Codex を含む）に送らない。
- 引用は citation-ssot。公開する原稿に内部の番号・GSE を書かない。
- 応答は日本語。決めてほしいことは推奨と理由を添えて AskUserQuestion で聞く。
- worktree で作業し、コミット前に `git branch --show-current`。`git add -A` を使わない。push だけで止める。G-GEAR で計算している間は PR を出さない。

## 別の手続き（研究者）

- The Learning Agency Lab への通知（`reply-drafts-20261013.md` の下書き 5）は、500 人の結果が出た時点で送る条件が揃っている。送ったら日付と応答を ethics.tex の角括弧に入れる（段とは別に）。
- PoPETs の program chairs の返事（2026-10-29 に研究者が共有・判断 81）: 出席は掲載の条件でなく、遠隔の発表は無い。研究者は出席せずに PoPETs を続けると決めた（判断 81 の追記）。採録されたら、出席できないことを chairs に伝える連絡の下書きを書く。
