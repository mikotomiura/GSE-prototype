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

## 判断 5: Codex の指摘の採否（2026-11-05・/cross-review 2 回目）

Codex は HIGH 無し。3 件とも採った。

- MEDIUM「notice だけでは実際の実行先を確かめていない」: 受け入れ条件と tasklist に、`check` の Windows のレグのログ冒頭の `Runner name:`・`Machine name:` を足した。
- MEDIUM「変数を設定する前に self-hosted と決まって待機しているジョブは守られない」: 変数を設定する直前に queued・in_progress の run が 0 件であることを確かめる段を tasklist に足した。2026-11-05 の時点では queued・in_progress・waiting はどれも 0 件。
- LOW「強制のときに probe しないことの検査が弱い」: 呼ばれた回数を記録する偽の `gh` で測った。強制=1 で 0 回（windows-latest）、`0` で 1 回（self-hosted）。

Codex の使用は 1 回。量はメインの台帳へ写した。

## 判断 6: PR の CI の 1 回目で見つかった、main の既存の違反を同じ PR で直す（2026-11-05）

PR #387 の 1 回目の run（41990943684）で、`decide-win-runner` は強制の notice を出して `["windows-latest"]` に決め、`check` の Windows のレグは `GitHub Actions 1000008126`（labels `windows-latest`）で走った（受け入れ条件の本番の確かめ）。

同じ run で frontend-check が赤だった。原因はこの変更ではなく、`experiments/20261102-stall-decomposition/extend/run.sh:43` の `$w（`（bash 3.2 で多バイト文字を変数名に食う・Shell portability gate）。6d468117 で main に入り、以後の main のコミットが skip の印付きだったため、CI で検出されていなかった。origin/main でも手元で同じく未達 1 件を再現した。直すのはエラーの文の 1 行だけで計算の出力は変わらないため、別のコミット（235a8082）で同じ PR に載せた。

## 判断 7: hosted の Windows のときだけ check の上限を 60 分にする（研究者の決定・2026-11-05）

PR #387 の 2 回目の run（41991152937）で、hosted の Windows の check は Rust の段（build 6 分・test 5 分・snapshot・schema・clippy 3 分）が全部通った後、Loop の git-bash のテストが遅く（run guard 13 分）、`timeout-minutes: 30` で job ごと cancel された。G-GEAR では 30 分に収まっていた。

候補は (a) hosted のときだけ上限を 60 分、(b) hosted では Loop の 3 段を飛ばす、(c) 取り消しを許して手で判断する。研究者は (a) を採った。検査の中身は変えない。条件は「matrix が Windows のレグで、`decide-win-runner` の出力が `["self-hosted","gse-win"]` でない」（強制・fallback・出力の欠落はどれも hosted に振られるため）。費用は 1 回につき Windows の約 45 分（分数では約 90 分）。

同じ run の frontend-check（ubuntu）は `loop-spawn-cleanup-test.sh` の 11a（別 id の同時 spawn の 3 ラウンド目で rcb=1）の 1 件で赤だった。手元では 3 回とも 118 件すべて通った。同時起動の競合を見るテストのため、たまに落ちる既存の検査と見て、この PR では直さない。次の run でも落ちたら別に調べる。
