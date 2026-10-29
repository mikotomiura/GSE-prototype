# 次のセッション（Mac）: 照合の論文 —— 探索的な分析 6・7 を原稿に入れ、Dr. Tian への草稿を仕上げる

作成 2026-10-29（判断 87 の後）。この機械は Mac。G-GEAR の作業（分析 6・7 の計算、全員の付録の計算）はこのセッションでしない。

段の順: **このファイル（6・7 と Dr. Tian）** → `next-session-public-keystroke-matching-manuscript-stage-3.md`（全員の付録・11 月中旬）。

## 新しいセッションで最初に打ち込む文

```
.steering/_handoff/next-session-public-keystroke-matching-manuscript-exploratory-6-7-and-tian.md を読んで、照合の論文に探索的な分析 6・7 の結果を入れて、Dr. Tian への草稿を仕上げて。
```

## 始める条件（揃っていなければ書かずに止まる）

- G-GEAR の分析 6（λ の格子）と 7（窓の走査）が終わり、結果の JSON が枝 `docs/public-keystroke-matching-manuscript` に merge され、notes.md の「探索的な分析の手順 その 3」に終了時刻・SHA-256・陽性対照の結果がある（G-GEAR 側の引き継ぎ `next-session-public-keystroke-matching-exploratory-lambda-ggear.md`）。
- worktree は `/Users/johnd/GSE-wt-matching-manuscript`。`git fetch` と `git merge --ff-only origin/docs/public-keystroke-matching-manuscript`。SHA-256 を notes.md の記録と照らす。

## 1. 6・7 を原稿に入れる

- 読む物: 判断 85 の 2（粗い形は書き方で限った）・判断 86（結果を見た後の探索で、問い 1〜4 に使わない）・notes.md の手順 その 3。
- 書く所: 付録 D（探索）に表と手順、本文は §7.2 と §8.1・§8.3 の粗い形の文（「全文の低い値は λ = 8 の端から端の整列を反映しうる」）を結果に合わせて 1〜2 文。結果を見た後に決めた探索であることを明記する。
- 粗い形の値が上がれば C2 の記述（序論・抄録・§7.3・結論）に響く。直す範囲が抄録や主張に及ぶなら、書く前に研究者に AskUserQuestion で聞く。
- 本文は 12 頁（p12 で終わる）。足す前に頁を測る。足した数値は集計の JSON と機械で照らす。
- その後: ビルド・文体の門・/cross-review（原稿の diff は Codex に送ってよい・判断 83）。

## 2. Dr. Tian への草稿（判断 73・84・87）

- 下書き 4（`.steering/20261012-public-keystroke-matching-prereg/reply-drafts-20261013.md`）の `[ ]` を埋める: 主な結果の 1〜2 文（集計だけ）・投稿の日付。節の番号（出どころは §3.3）をビルドで確かめる。
- PDF は著者名入りの版: `bash build.sh <テンプレート> <出力先> /Users/johnd/paper-authors/keystroke-log-release-matching.tex` → `main-authors.pdf`（BUILD.md）。テンプレートは PoPETs の submission-template-2027.zip（BUILD.md に SHA-256）。
- 決まっていること（判断 87）: 6・7 入りの版を送る／Crossley に見せてよいかは尋ねない／The Learning Agency Lab へ知らせるべきかは尋ねる／載せることへの了承を明示に尋ねる／共著の提案は入れない（判断 84）。送るのは研究者。
- 日程: 下書き 5（The Learning Agency Lab への知らせ）の猶予（投稿の約 2 週前）と、判断 73 の「約 1 週返事が無ければ下書き 5 を送る」を保つには、Dr. Tian へ 11/9 ごろまでに送る必要がある。遅れていたら、研究者に AskUserQuestion で聞く（判断 87 の 2）。

## 3. 終わったら

- 判断（88 から）を `.steering/20261012-public-keystroke-matching-prereg/decisions.md` に書く。commit・push だけ（PR は出さない）。
- 送った日付が分かったら decisions.md に書く。返事で中身に踏み込んできたら、判断 84 の共著の提案の下書きを書く。
- 研究者のメモ（2026-10-29・会話）: 共著になれば、PoPETs で Dr. Tian が発表してくれる可能性がある（研究者は登壇しない・判断 81）。ただし発表を共著の誘いの理由にしない（贈る著者に見えるため・判断 84）。共著が決まった後に、本人の意向と参加費・渡航の負担を含めて頼む。

## 公開の計画（判断 88）

- 投稿と同時にプレプリント（arXiv cs.CR、だめなら OSF Preprints）・OSF の登録・論文用の repo と Zenodo を公開する。このセッションで手が空けば、準備（TeX のコメントを消した元・プレプリントの版の切り替え）に着手してよい。arXiv の endorsement は研究者が確かめる。
- PoPETs 2027 の査読中のプレプリントの扱いを、petsymposium.org が戻っていれば読む（2026-10-29 は DNS が SERVFAIL）。

## 守ること

- 集計の JSON だけを読む。打鍵の記録・本文・キャッシュを開かない。それらを外部 LLM に送らない。
- 引用は citation-ssot。公開する原稿に内部の番号・GSE・著者名を書かない（著者名は repo の外のファイルだけ）。
- worktree で作業し、コミット前に `git branch --show-current`。`git add -A` を使わない。
- 応答は日本語。決めてほしいことは推奨と理由を添えて AskUserQuestion（日本語）で聞く。
