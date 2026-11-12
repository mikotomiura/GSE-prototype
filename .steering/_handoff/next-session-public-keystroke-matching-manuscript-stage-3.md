# 次のセッション（Mac）: 照合の論文 —— 段 3: 全員の付録（`main_all.json`）を入れる

**済み（2026-11-12・判断 89）。** 残りの分析 6・7 と Dr. Tian の返事は `next-session-public-keystroke-matching-manuscript-exploratory-6-7.md` と `next-session-public-keystroke-matching-tian-reply.md`。

作成 2026-10-29（判断 81 の後）。2026-10-29 に判断 82 の後で書き直した（R-DP の R0 に比べる有用性は済み、残りは `main_all.json` だけ）。この機械は Mac。G-GEAR の作業はこのセッションでしない。

| 段 | 届くもの | 書く所 |
|---|---|---|
| 済み | `main.json`・`enja15_main.json`・探索 3〜5 | §7・序論・考察・結論・抄録（判断 79） |
| 済み | `main_a4.json`・`main_a4_without_cpu_writer.json` | 表 2 の A4 の行・§7.4・§7.5・付録 E の KeyTAR（判断 80） |
| 済み | `exploratory_unicity.json`・`exploratory_dp.json` | §7.7 の 1 文・付録 D の表 6〜8（判断 81） |
| 済み | `exploratory_dp_utility_r0.json` | 付録 D の表 8 の R0 との相関（判断 82） |
| **3（このセッション）** | `main_all.json`（全員の付録） | 付録 E の「Results on all writers」（`appendix-results.tex` 201 行目の角括弧） |
| 完成 | ― | 草稿の完成（判断 76）→ attack-me round 3 |

## 新しいセッションで最初に打ち込む文

```
.steering/_handoff/next-session-public-keystroke-matching-manuscript-stage-3.md を読んで、照合の論文に全員の付録（main_all.json）の結果を入れて。
```

## 始める条件（揃っていなければ書かずに止まる）

- G-GEAR の `all` の段（2026-10-28 18:12 UTC 開始・12 並列で約 10〜12 日・11 月中旬の見込み）が終了コード 0 で終わり、`results/main_all.json` が原稿の枝に merge され、notes.md に終了時刻と SHA-256 の記録がある。
- worktree は `/Users/johnd/GSE-wt-matching-manuscript`（枝 `docs/public-keystroke-matching-manuscript`）。始める前に `git fetch` と `git merge --ff-only origin/docs/public-keystroke-matching-manuscript`。
- SHA-256 を notes.md の記録と照らす。

## `main_all.json` の形（コードから・値は未見）

- `run_main.py --all`（`run.sh` 46 行目）の出力。A4 は無い（A0〜A3）。形は main の 15 形（`--forms main`）。
- 上の段に `main500` と `all` の 2 つの標本がある（`run_main.py` 402〜416 行）。`main500` は標本の 500 人で、キャッシュ（指紋 `33fa95833296d7a5`）を使い回すので、**`main.json` の `main500` と同じになるはず**（`seconds` を除く）。これを陽性対照にする。違えば値を書かずに止まり、notes.md に逸脱として書いて研究者に聞く。
- `all` は除外の後の全員（一意さの `all` は 4,992 人だった。照合の除外は同じか `sample_sizes` で確かめる）。`all` に負の対照と探索 3〜5 は無い（`main500` だけ）。区間は `aggregate.resamples(seed, …, "all")` の抽出。

## やること

1. 陽性対照: `main_all["main500"]` と `main.json["main500"]` を `seconds` 以外で全部の葉で比べる。上の段（`seed_file_sha256`・`config_sha256`・除外）も比べる。
2. `make_tables.py` に `all_writers_table`（仮）を足す。量は付録 E の表と同じ書き方: 全文の最も強い攻撃者の正答率と区間（N = 10・100・1,000）、主な形。500 人の値と並べるかは表の幅を見て決める（判断 80・81 で `\multicolumn` の行が表を広げた）。止まる条件: 陽性対照が合わない、最も強い攻撃者が本文の注と違う、人数が `sample_sizes` と違う。壊した写しで止まること、既存の生成ファイルが変わらないこと（`git status`）を確かめる（判断 80〜82 と同じ）。
3. 201 行目の角括弧を、表への参照と 1〜2 文に替える。500 人と全員で結論が変わるか（強さの順・R3 の値）だけを書く。本文（§7）は変えない（余白 0）。全員の結果が 500 人と食い違うなら本文の主張に響くので、書かずに研究者に聞く。
4. 数値と量の語を集計の JSON と機械で照らす（`verify-before-claiming`）。
5. 頁を測る（`paper-write/length-log.md` の数え方・本文の終わりが p12 右段の最終行のままか）。
6. ビルド（エラー 0・未定義 0・overfull は今 2）・PDF を画像で見る・文体の門（違反 0）・`length-log.md` に 1 行・`../20261012-public-keystroke-matching-prereg/decisions.md` に判断 83・tasklist.md の段 3・commit・push。
7. `/cross-review`（研究者が 2026-10-29 に、集計の値を含む原稿の diff を Codex に送ってよいと認めた。`raw/` と results の JSON は送らない）。
8. 草稿の完成（判断 76）の残り: 倫理の公開元への連絡の角括弧（`ethics.tex` 30 行目・下の「別の手続き」）・open science の匿名リンク（`open-science.tex` 9 行目）。揃ったら attack-me round 3（まだなら）。

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
- 集計の JSON だけを読む。打鍵の記録・本文・キャッシュを開かない。それらを外部 LLM（Codex を含む）に送らない。原稿の diff は Codex に送ってよい（2026-10-29 研究者）。
- 引用は citation-ssot。公開する原稿に内部の番号・GSE を書かない。
- 応答は日本語。決めてほしいことは推奨と理由を添えて AskUserQuestion で聞く。
- worktree で作業し、コミット前に `git branch --show-current`。`git add -A` を使わない。push だけで止める。G-GEAR で計算している間は PR を出さない。

## 別の手続き（研究者）

- The Learning Agency Lab への通知（`reply-drafts-20261013.md` の下書き 5）は、判断 73 で Dr. Tian への草稿（下書き 4）の後に回した。下書き 4 の返事を約 1 週待ち、来なければ研究者が送る。送ったら日付と応答を ethics.tex の角括弧に入れる（段とは別に）。
- 2026-10-29 判断 88: 投稿と同時にプレプリント（arXiv、だめなら OSF Preprints）・OSF の登録・論文用の repo と Zenodo を公開する。準備の一覧（endorsement・TeX のコメントを消す・プレプリントの版・repo の点検）は判断 88。PoPETs 2027 の査読中のプレプリントの扱いはサイトが戻ってから確かめる。
- 2026-10-29 追記: この段の前に、探索的な分析 6・7 を原稿に入れて Dr. Tian へ草稿を送る段がある（`next-session-public-keystroke-matching-manuscript-exploratory-6-7-and-tian.md`）。
- PoPETs の program chairs の返事（2026-10-29 に研究者が共有・判断 81）: 出席は掲載の条件でなく、遠隔の発表は無い。研究者は出席せずに PoPETs を続けると決めた（判断 81 の追記）。採録されたら、出席できないことを chairs に伝える連絡の下書きを書く。
- Dr. Tian への共著の提案（判断 84）: 下書き 4 で草稿への意見を求め、返事で中身に踏み込んできたら、役割と承認の期限を添えて提案する（下書きは Claude・送るのは研究者）。共著になったら利害の表明などを直す（判断 84 の一覧）。
