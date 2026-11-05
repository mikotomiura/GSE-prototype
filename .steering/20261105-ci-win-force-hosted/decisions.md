# 判断

## 判断 1: 守り方は変数で hosted に固定する（研究者の決定・2026-11-05）

候補は (a) 変数で hosted に固定、(b) G-GEAR のランナーのサービスを止める、(c) 今は offline なので何もしない。研究者は (a) を採った。(b) は再起動などで黙って戻ると G-GEAR に載る。(c) は振り分けがジョブの始まりに決まるので、確かめた後に起き上がると防げない。

## 判断 2: 振る舞いの確かめで、最初の測定が偽陽性だった

最初のハーネスは zsh で `env -i ... $2 bash probe.sh` と書き、zsh が `$2` を空白で分けないため、強制の変数が token の変数の値の一部として 1 つの変数に渡っていた。結果、強制=1 が self-hosted と出た。取り出した script に分岐があることを確かめてから、引数を分けて渡し直し、期待どおりの 5 通りを得た（強制=1 は online でも token 無しでも hosted、未設定・`0`・空文字は online で self-hosted）。

## 判断 3: レビューの指摘の採否（2026-11-05）

code-reviewer（HIGH 無し）と /cross-review の Claude 側の指摘を受けた。

- 採る（MEDIUM・code-reviewer）: push で走る CI は push した枝の中の ci.yml を使う。この変更が枝に入っていなければ、変数を設定しても従来どおり probe する。→ 手順を「この変更を先に main へ入れる → R1 などの枝に main を取り込む → 枝の ci.yml に分岐があることを `git show <branch>:.github/workflows/ci.yml | grep -c GSE_WIN_FORCE_HOSTED` で確かめてから push」に改めた（tasklist）。main 向けの PR は merge ref の ci.yml で評価されるので、main に入った後は PR では自動で効く。
- 採る（LOW・code-reviewer）: 変数が空でも "1" でもないときに notice を 1 行出す（設定の誤りをログで見分けるため）。
- 採る（LOW・cross-review の Claude 側）: 判定役の `decide-win-runner` 自体は `gse-mac`（この MacBook）で走るので、強制中も Mac のスロットを使う。G-GEAR を守る目的には影響しない（design.md に注を足した）。
- 採らない（LOW）: fork の PR で `vars` が読めない可能性。fork の PR では self-hosted の判定ジョブ自体が if で走らない（既存の遮断）。

## 判断 4: Codex の機密フィルタの誤検知と `--ack-filtered`

1 回目の /cross-review で、`scripts/secrets-filter.sh` が行内マッチ 3 件で止めた（Codex は 0 回）。3 件は ci.yml の文脈の行 2 つ（シークレットの参照名 `secrets.RUNNER_STATUS_TOKEN` を env に渡す行と、token の変数が空かを見る行）と、この decisions.md の判断 2 の説明文。どれも値を含まないことを私が diff で確かめた。判断 2 の説明文は変数名の書き方を言い換えた。ci.yml の 2 行は変えられないので、2 回目は `--ack-filtered` で回す。
