# 次のセッション（Mac）: 照合の論文 —— 段 2: 探索的な分析 1・2（一意さ・R-DP）を入れる

> 使用済み（2026-10-29）: 段 2 を入れた（判断 81）。R-DP の R0 に比べる有用性は空で届いたので、G-GEAR の `next-session-public-keystroke-matching-dp-utility-r0-ggear.md` で集計し直し、段 3（`next-session-public-keystroke-matching-manuscript-stage-3.md`）で入れる。

作成 2026-10-27（判断 80 の後）。この機械は Mac。G-GEAR の作業はこのセッションでしない。

執筆は届いた結果ごとに段で進める（研究者 2026-10-24）。このセッションは **段 2 だけ**を行う。

| 段 | 届くもの | 書く所 |
|---|---|---|
| 済み | `main.json`・`enja15_main.json`・探索 3〜5 | §7・序論・考察・結論・抄録（判断 79） |
| 済み | `main_a4.json`・`main_a4_without_cpu_writer.json` | 表 2 の A4 の行・§7.4・§7.5・付録 E の KeyTAR・倫理の 1 つの例外（判断 80） |
| **2（このセッション）** | `exploratory_unicity.json`・`exploratory_dp.json` | §7.7 の角括弧・付録 D の角括弧と表 |
| 3 | `main_all.json`（全員の付録） | 付録 E の Results on all writers |
| 完成 | ― | 「草稿の完成」の 6 項目 → attack-me round 3 |

## 新しいセッションで最初に打ち込む文

```
.steering/_handoff/next-session-public-keystroke-matching-manuscript-exploratory-1-2.md を読んで、照合の論文に探索的な分析 1・2 の結果を入れて。
```

## 始める条件（揃っていなければ書かずに止まる）

- `results/exploratory_unicity.json` は 2026-10-27 に届いて原稿の枝に merge 済み（SHA-256 `78873a55…`・notes.md の「unicity の段」）。値はまだ誰も開いていない。
- `results/exploratory_dp.json`（R-DP）が G-GEAR の `dp` の段（2026-10-27 11:14 UTC 開始）で終了コード 0 で終わり、原稿の枝に merge され、notes.md に終了時刻と SHA-256 の記録がある。無ければ書かずに止まる。merge の手順は段 1 と同じ（freeze の枝に results の commit → 原稿の枝へ merge）。
- worktree は `/Users/johnd/GSE-wt-matching-manuscript`（枝 `docs/public-keystroke-matching-manuscript`）。始める前に `git fetch` と `git merge --ff-only origin/docs/public-keystroke-matching-manuscript`。

## やること

1. 2 つの JSON の構造を見る（`exploratory_unicity.json` の上の段の鍵は `N`・`all`・`entropy_bits_per_word`・`excluded`・`k_star`・`kmax`・`main500`・`mutate`・`source`・`starts_per_writer`・`writers_after_exclusion`）。手順は notes.md の「探索的な分析の手順（判断 55・56）」の分析 1・2 と、原稿の §6.7（`sec:protocol:exploratory`）と付録 D。
2. R-DP は `run_main.py --forms dp` の出力なので、形の鍵が主の計算と同じ形かを見る。`main.json` と重なるセルがあれば一致を確かめる。
3. `make_tables.py` に 2 つの表の関数を足す（付録 D）。値は手で写さない。既存の生成ファイルが変わらないことを `git status` で確かめる。止まる条件を足したら、壊した写しで止まることを確かめる（判断 80 と同じ）。
4. 角括弧を埋める: `results.tex` の §7.7 の終わり（`[Uniqueness of word-length sequences and R-DP, ...]`）と `appendix-exploratory.tex` の 63 行目。分析の地位（探索的）は §6 で 1 度だけ定義済み。§7.7 で繰り返さない。考察の「The exploratory analyses」の段落（一意さは母集団の再識別の危険ではない・R-DP の保証の単位）は限界の文としてすでにある。値で変えたくなったら研究者に聞く。
5. 書いた数値と、量の語（value / accuracy / interval など）がどの量を指すかを、集計の JSON と機械で照らす（`verify-before-claiming` を読んでから。判断 80 で「no value」が区間の端まで含むと読める誤りを見つけた）。
6. 頁を測る（`paper-write/length-log.md` の数え方）。⚠️ **余白は 0**（判断 80 の後、本文の最終行が p12 右段の最終行）。§7.7 の角括弧（約 2 行）を数値の文に置き換えて伸びれば、12 頁を超える。まず足した文から表と付録にある値を外す（判断 79・80 と同じ）。それでも超えたら、判断 79 で選ばなかった候補（§8.2 合意の段落を縮める）を推奨と理由を添えて AskUserQuestion で聞く。
7. ビルド（エラー 0・未定義 0）・PDF を画像で見る（表の幅・判断 80 で `overfull` に出ない広がりを見つけた）・文体の門（違反 0）・`length-log.md` に 1 行・`../20261012-public-keystroke-matching-prereg/decisions.md` に判断 81・tasklist.md・commit・push。
8. 段 3 の引き継ぎを書く（`main_all.json` が届いたら・11 月中旬の見込み）。

## 道具

- テンプレート: `submission-template-2027.zip`（SHA-256 `b1abbcc0…`）。前のセッションの scratchpad にある写しを自分の scratchpad に写して展開し、`bash build.sh <PoPETS-2027-latex-template> <出力先>`。
- 文体の門: repo の根から `python3 .steering/20260927-ime-observation-paper-eval-design/issues/_style_check.py --root . papers/keystroke-log-release-matching`。
- 頁: `pdftohtml -xml` で "Ethical Considerations" の見出しの位置（判断 80 の測り方は length-log.md の「数え方」）。

## 読む物

- `paper-write`（`/Users/johnd/GSE-wt-paper-write-skill/.claude/skills/paper-write/SKILL.md`）と `verify-before-claiming`。書く前に読む。
- 判断 79・80（`../20261012-public-keystroke-matching-prereg/decisions.md`）・notes.md の分析 1・2 の手順と「unicity の段」。
- 詰まった所は `/Users/johnd/GSE-wt-paper-write-skill/.steering/20261024-paper-write-skill/field-trial.md` の続きに書く（候補 13〜15 が判断 80 で足された）。Skill はまだ直さない。

## 守ること

- 脅威モデル・攻撃者・手順は凍結した事前登録から変えない。変えるときは notes.md の「逸脱」に書く。
- 集計の JSON だけを読む。打鍵の記録・本文・キャッシュを開かない。外部 LLM（Codex を含む）に送らない。
- 引用は citation-ssot（[V299]–[V325] は別の枝。今は [V329] まで）。公開する原稿に内部の番号・GSE を書かない。
- 応答は日本語。決めてほしいことは推奨と理由を添えて AskUserQuestion で聞く。
- worktree で作業し、コミット前に `git branch --show-current`。`git add -A` を使わない。push だけで止める。G-GEAR で計算している間は PR を出さない。

## 別の手続き（研究者）

The Learning Agency Lab への通知（`reply-drafts-20261013.md` の下書き 5）は、500 人の結果が出た時点で送る条件が揃っている。送ったら日付と応答を ethics.tex の角括弧に入れる（段とは別に）。
