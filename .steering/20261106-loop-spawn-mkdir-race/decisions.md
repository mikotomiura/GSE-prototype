# 判断

## 判断 1: main への別の PR で直す（研究者の決定・2026-11-06）

R1（PR #388）とは関係のない直しなので、main への別の PR にした。直した後に R1 へ main を取り込む。

## 判断 2: 印を noclobber の pid ファイルにする

候補は (a) noclobber の pid ファイル、(b) GNU の mkdir（`gnumkdir`）を探して使う、(c) python の os.mkdir。(b) は 26.04 にしか無い名前で、git-bash・macOS で分岐が要る。(c) は python を必須にする。(a) は bash だけで済み、git-bash（Windows のループの実行）でも同じに動く。既存の pid ファイルの名前と読み戻しの検査をそのまま使えるので、差分も小さい。

## 判断 3: 範囲に入れなかったもの

`scripts/run-features-all-poles.sh` も `mkdir "$LOCK_DIR"` の不可分を前提に二重起動を防いでいる。走らせるのは研究用の機械（macOS の BSD mkdir・G-GEAR の git-bash の GNU mkdir）で、今は影響しない。ubuntu 26.04 などの uutils の環境で走らせるようになったら、同じ形で直す。

## 判断 4: 1 巡目のレビューの指摘で放し方と戻り値 2 を作り直す（2026-11-06）

/cross-review（Claude・Codex が一致した HIGH 2 件・Codex の MEDIUM 1 件・Codex 22,705 トークン）と code-reviewer（HIGH 1・MEDIUM 3・取り合いの実測つき）を受けた。

- HIGH（両者一致・code-reviewer も）: 戻り値 2 を「pid が無い・ディレクトリが無い」にも返していたため、持ち主が放している途中（pid を消した後・ディレクトリを消す前）に当たると、他人のロックを残骸と取り違えて `rm -rf` した。code-reviewer の取り合いの実測（6 本・3000 回）で二重保持を 28〜56 件確認、同じ枝を何もしない対照で 0 件。→ 2 は「pid が在るのに普通のファイルでない」（14a の形）だけにし、曖昧なときは全部 1（待つ）にした。
- HIGH（両者一致）: 放すときの `rm -rf` は pid を消してからディレクトリを消すので、その間に元の場所で印が取られうる。→ `discard_dir`（別名へ mv＝rename で一度に外してから消す）にした。本体の解放・stale の除去・除去用ロックの解放・読み戻しの不一致の後始末の 4 か所。除去用ロックの解放は自分の印のときだけ。
- MEDIUM（Codex・code-reviewer）: 印の作成と pid の書き込みを一緒にしていたので、書き込みの失敗（ENOSPC 等）で空の印が残り、他人の印と取り違えて永久に待った。→ 作成（noclobber の `: >`）と書き込みを分け、作成できたら自分の印と確定する。書けたかは既存の読み戻しで見る（14a・14b はそのまま意味を保つ）。
- MEDIUM（code-reviewer）: 除去用ロックが中に pid を持つようになり、`rmdir` で消えなくなった。die の案内の `rmdir` を `rm -rf` に直した（本体のロックの案内も・LOW）。除去用ロックの stale 判定は足していない（rm も mv も失敗し続ける環境でだけ残る。判断 3 と同じく記録に留める）。
- テストの不足（Codex）: 11a2 は「両方 exit 0」しか見ない。→ 11a3 を足した（git を包み `git worktree add` の区間に noclobber の印・3 本 × 4 ラウンド）。変異で確かめた: 印の取り方を mkdir だけに戻すと 11a2・11a3 が赤（読み戻しの検査が止める）、読み戻しの検査も外すと 11a3 が「区間が 8 回重なった」。
- 11g の差し替えに `mv` の失敗を足した。消し方が mv を経由する形になったので、「消せない状態が続いてもスピンせず止まる」という検査の意図を保つため。

検証: `loop-spawn-cleanup-test.sh` 120 件・0 件、`loop-run-guard-test.sh`・`loop-worktree-deny-test.sh`・`check-shell-portability.sh` 通過。Windows の git-bash（MSYS）で noclobber が O_EXCL として働くことは確かめていない（code-reviewer も未確認と明記）。

## 判断 5: 2 巡目のレビューの指摘で戻り値 2 を「消さずに止まる」にする（2026-11-06）

/cross-review 2 巡目（Codex 27,876 トークン・HIGH 1 は Claude と一致・MEDIUM 2）と code-reviewer 2 巡目（取り合いの実測つき）を受けた。code-reviewer の実測で、放し方の rename は旧来の窓を閉じていた（旧の放し方の対照で二重保持 4 件、新しい放し方では窓に関わる分 0）。残った二重保持はすべて戻り値 2 の誤判定から連鎖していた。

- HIGH（両者一致・code-reviewer）: 戻り値 2 の判定 `{ [ -e ] || [ -L ]; } && [ ! -f ]` は stat が 2 回に分かれ、間で持ち主が外すと誤って立つ（実測で二重保持 1 件ずつ）。2 を共有の状態として 2 本が同時に見ることもある（Codex）。→ 判定を 1 回の stat で決まる `-d`・`-p`・`-S` だけにし（code-reviewer の実測で 0 件）、さらに 2 のときは何も消さずに案内を出して止まる（Codex の案）。誤って立っても余計な停止で済み、他人のロックを消さない。
- MEDIUM（Codex・実測）: pid が FIFO だと noclobber の open が読み手を待って詰まり、タイムアウトも効かない。→ noclobber で作る前に判定する。
- MEDIUM（Codex・code-reviewer）: 除去用ロックの pid の書き込みに失敗すると空の印が残り、EXIT trap の「自分の印のときだけ外す」に当たらず残骸になる。→ 取った直後に読み戻し、合わなければ自分の除去用ロックを外して諦める。
- MEDIUM（code-reviewer・Windows は確かめていない）: mv が一時的に失敗すると、正常系の解放の後に `exec claude` で同じ pid が生き続けるので、ロックが長く残る。→ mv を 3 回まで再試行し、外せなければ「手で rm -rf」と警告を出す（今までは無言）。
- LOW（両者）: 退避先の名前の衝突と `.gone.*` の残骸。→ 退避先を mktemp -d で一意にした。`.gone.*` の掃除は足していない（ロックそのものは外れているので害はない）。
- 採らない（Codex の LOW）: 放すときに mv が失敗したら元の場所で rm -rf する後備え。元の場所で消すと 1 巡目の窓が戻るので、警告に留めた。

検査の変更（意図は変えない・研究者に報告する）:
- 14a・14b の書き込みの失敗の作り方を「pid の場所にディレクトリを置く」から「`printf '%s' "$$"` だけを失敗させる」に替えた。前者は新しい claim_dir では残骸として「消さずに止まる」経路に入るため。14a（書けなければ自分のロックを残さずに止まる）と 14b（読み戻しの検査を外すとロックが残る）の意図は同じ。
- 14f を足した: 残骸（pid がディレクトリ）を、不可分な mkdir ではタイムアウトで、既にあっても 0 を返す mkdir では残骸の案内で、どちらも消さずに止まる。pid が FIFO でも詰まらずに止まる（15 秒の見張り付き）。変異（事前判定を外す）で 14f(uutils)・14f(fifo) が赤（fifo は 15 秒で打ち切り）になることを確かめた。

検証: `loop-spawn-cleanup-test.sh` 123 件・0 件、`loop-run-guard-test.sh` 98・`loop-worktree-deny-test.sh` 34・`check-shell-portability.sh` 12 通過。
