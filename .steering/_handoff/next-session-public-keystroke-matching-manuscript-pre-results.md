# 次のセッション: 公開データでの照合の論文 —— 結果を待たずに書ける節を Mac で書く

作成 2026-10-20（判断 57〜59 の後）。この機械は Mac。本計算（A4 の KeyTAR・CPU の本計算）は G-GEAR で進めていて、このセッションでは触らない（G-GEAR の作業は G-GEAR に任せる）。
投稿の目標は PoPETs 2027 Issue 3（締切 **2026-11-30 AoE**）。間に合わなければ Issue 4（2027-02-28）。

## 新しいセッションで最初に打ち込む文

```
.steering/_handoff/next-session-public-keystroke-matching-manuscript-pre-results.md を読んで、照合の論文の結果に依存しない節（脅威モデルの動機から）を Mac で書き始めて。
```

## 今の状態（2026-10-20 時点）

- 事前登録は凍結済み（OSF 10.17605/OSF.IO/Y5R7N・2026-10-13）。英語の正の版は `experiments/20261012-public-keystroke-matching/preregistration.en.md`。以後の変更は `notes.md` の「逸脱」。
- 本計算は G-GEAR で実行中（11/9 ごろの見込み・判断 51）。結果はこのセッションでは見ない・使わない。
- 投稿先の順（判断 57・58）: **PoPETs → JPC か TDP → JEDM**（JWR は外した）。
- 段取り（判断 59）: 〜11/9 に結果に依存しない節を Mac で書く → 11/10〜11/25 に結果と考察・attack-me・`/cross-review` → 11/27 ごろ出すか Issue 4 に回すかを研究者が決める。
- PoPETs の PC chairs への問い合わせ（録画・オンライン発表の要否・10/13 送付）は返事なし。催促の下書きは `reply-drafts-20261013.md` の 3（10/27 ごろ・送るのは研究者）。段取りの条件にはしない。
- 判断の記録: `.steering/20261012-public-keystroke-matching-prereg/decisions.md`（判断 6〜59）。判断 57〜59 はブランチ `docs/public-keystroke-matching-venue-plan`（worktree `/Users/johnd/GSE-wt-matching-venue`）にあり、main にはまだ入っていない。

## やること

1. **最初に確かめる**: ブランチ `docs/public-keystroke-matching-venue-plan` の判断 57〜59 を読む。催促を送ったか・PC chairs の返事が来たかを研究者に尋ねる（来ていれば日付と要旨を `decisions.md` に書く）。
2. **原稿の置き場を決める**（研究者に AskUserQuestion）。案: IME 論文 1 と同じ形の `papers/<name>/manuscript/`（`papers/README.md` の公開物の規則に従う）か、論文用リポジトリ `mikotomiura/keystroke-log-release-matching`（private・G-GEAR の `C:\keystroke-log-release-matching` にある。Mac には clone が無い）。草稿は MacTeX。PoPETs の 2027 のテンプレートを一次で取得する。
3. **脅威モデルの動機の節**（最初に書く）: 現実に誰が、どの公開物と、どの候補の本文で照合できるか。公開の現場の例（KLiCKe・Kaggle の作文記録の加工 [V265]・`@` のマスク [V243]）を一次の出典で示す。攻撃者の知識・候補・攻撃者の一覧は凍結済みなので**変えない**（事前登録の Threat model・Attackers の節をそのまま使う）。書けたら attack-me（stage は原稿の外枠）にかけ、指摘は動機の書き方と限界の節に返す。
4. **序論・関連研究**: 新しさの根拠は `docs/literature/20261012-public-keystroke-matching-novelty.md`（claim #10 #11 #14）・`20261012-public-keystroke-matching-prereg-search.md`・`20261013-length-unicity-and-dp-release.md`。
5. **方法**: 事前登録の英語の版から書く（手順の言い換えで意味を変えない）。探索的な分析 2 つ（判断 55・56）は「事前登録に無い探索的な分析」と明記する。
6. **必須の 3 節**（PoPETs 2027 のテンプレート: ethical considerations・open science・AI use）。倫理の節の材料は `reply-drafts-20261013.md` の最後と判断 54（MIT License・Georgia State University の IRB・著者の確認・集計だけを報告）。所属が無く審査を受けられる委員会が無いことも書く（判断 7）。
   - これらの節は JPC・TDP・JEDM へ移るときもほぼそのまま使える（倫理・データとコードの公開・AI の利用の申告は多くの誌が求める）。移るときに直すのは書式・分量・匿名化（PoPETs は二重盲検、JPC・TDP は single-blind）。
7. **二重盲検の扱い**: OSF の登録はエンバーゴなしで公開中。論文から登録とコードをどう示すか（匿名のリンクなど）を PoPETs の著者向けの案内で一次で確かめ、研究者に問う。

## 守ること

- 応答は日本語（AskUserQuestion の問い・選択肢も日本語）。絵文字・★・⚠️ を多用しない。決めてほしいことは推奨と理由を添えて AskUserQuestion で聞く。
- 結果（G-GEAR の本計算の出力）を見ない・書かない。脅威モデルと方法は凍結した事前登録から変えない。
- 引用は `citation-ssot`（[Pn]/[Vn]・append-only）。公開する原稿には内部の番号・GSE への言及を書かない（`papers/README.md`）。
- 打鍵の記録・本文を外部 LLM（Codex を含む）に送らない。
- 並行セッションがあるので worktree で作業し、コミット前に `git branch --show-current` を確かめる。`.steering` だけの変更は push だけ（PR は研究者に確かめてから）。`git add -A` を使わない。
