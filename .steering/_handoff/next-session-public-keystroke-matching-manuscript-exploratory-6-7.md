# 次のセッション（Mac）: 照合の論文 —— 探索的な分析 6・7 の結果を原稿に入れる

作成 2026-11-12（判断 90 の後・旧 `next-session-public-keystroke-matching-manuscript-exploratory-6-7-and-tian.md` から分けた）。この機械は Mac。G-GEAR の作業（分析 6・7 の計算）はこのセッションでしない。Dr. Tian の返事は別の引き継ぎ（`next-session-public-keystroke-matching-tian-reply.md`）。

## 新しいセッションで最初に打ち込む文

```
.steering/_handoff/next-session-public-keystroke-matching-manuscript-exploratory-6-7.md を読んで、照合の論文に探索的な分析 6・7 の結果を入れて。
```

## 始める条件（揃っていなければ書かずに止まる）

- G-GEAR の分析 6（λ の格子・`results/exploratory_lambda.json`）と 7（窓の走査・`results/exploratory_scan.json`）が終わり、枝 `docs/public-keystroke-matching-manuscript` に merge され、notes.md の「探索的な分析の手順 その 3」に終了時刻・SHA-256・陽性対照の結果がある。G-GEAR 側の引き継ぎは `next-session-public-keystroke-matching-exploratory-lambda-ggear.md`（見込み: 11-12 開始、6 が約 3.2 日・7 が約 2.3 日、11-18〜19 ごろ）。
- worktree `/Users/johnd/GSE-wt-matching-manuscript`。`git fetch` と `git merge --ff-only origin/docs/public-keystroke-matching-manuscript`。SHA-256 を notes.md の記録と照らす。

## やること

1. 読む物: 判断 85 の 2（粗い形は書き方で限った）・判断 86（結果を見た後の探索で、問い 1〜4 に使わない）・notes.md の手順 その 3・`paper-write` Skill（`git show origin/chore/paper-write-skill:.claude/skills/paper-write/SKILL.md`）と `verify-before-claiming`。
2. `make_tables.py` に分析 6・7 の表を足す（判断 80〜82・89 と同じ型）。陽性対照（λ = 8 の A2・A1′ が `main.json` と一致、λ = 4・16 の A2 が `A2-lam4`・`A2-lam16` と一致）を表の生成でも確かめ、合わなければ止まる。壊した写しで止まること・既存の生成ファイルが変わらないこと（`git status`）を確かめる。
3. 書く所: 付録 D（探索）に表と手順。本文は §7.2 と §8.1・§8.3 の粗い形の文（「全文の低い値は λ = 8 の端から端の整列を反映しうる」）を結果に合わせて 1〜2 文。結果を見た後に決めた探索であることを明記する。
4. 粗い形の値が上がれば C2 の記述（序論・抄録・§7.3・結論）に響く。直す範囲が抄録や主張に及ぶなら、書く前に研究者に AskUserQuestion で聞く。
5. 本文は 12 頁（Ethical Considerations が p12 右段）。足す前に頁を測る。足した数値は集計の JSON と機械で照らす。
6. ビルドは投稿版とプレプリントの版の両方（BUILD.md・`build-preprint.sh`）。文体の門・`length-log.md` に 1 行・decisions.md に判断・tasklist.md・commit・push・`/cross-review`（原稿の diff だけ）。
7. Dr. Tian に「補足の解析が入ったら新しい版を送る」と約束している（2026-11-12）。プレプリントの版の PDF を作り、短い送り状の下書き（何が足されたか・先方の話に関わる記述は変わっていないこと）を書く。送るのは研究者。Dr. Tian の返事の引き継ぎで原稿を直していれば、それも含めた版にする。

## 公開の計画（判断 88）

- 投稿と同時にプレプリント（arXiv cs.CR、だめなら OSF Preprints）・OSF の登録・論文用の repo と Zenodo を公開する。プレプリントの版（`preprint.tex`・判断 90 の追記）には投稿版のための角括弧（open science の匿名リンク・「withheld until acceptance」）が残っている。プレプリントの版でだけ OSF と repo のリンク・個人的な連絡の日付を埋める仕組みが要る。手が空けば着手してよい。arXiv の endorsement は研究者が確かめる。
- PoPETs 2027 の査読中のプレプリントの扱いを、petsymposium.org が読めれば読む（2026-10-29 は DNS が SERVFAIL）。

## 守ること

- 集計の JSON だけを読む。打鍵の記録・本文・キャッシュを開かない。それらを外部 LLM（Codex を含む）に送らない。原稿の diff は Codex に送ってよい（判断 83）。
- 引用は citation-ssot。公開する原稿に内部の番号・GSE・著者名を書かない。
- worktree で作業し、コミット前に `git branch --show-current`。`git add -A` を使わない。push だけで止める。
- 応答は日本語。決めてほしいことは推奨と理由を添えて AskUserQuestion で聞く。
