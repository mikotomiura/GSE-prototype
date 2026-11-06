# 要件: loop-spawn のロックが ubuntu 26.04 の mkdir で二重に取れる（CI の 11a が赤）

## 背景

2026-11 から CI の frontend-check で `scripts/loop-spawn-cleanup-test.sh` の 11a（別 id の同時 spawn を 3 ラウンド）が毎回落ち、後ろの 23 段が skip されていた（PR #387・#388）。最後に通った main の run（2026-10-14）は ubuntu 24.04、今は `ubuntu-latest` = 26.04。

診断用の一時的な workflow（枝 `diag/loop-spawn-11a`・run 42174347593 ほか）で確かめたこと:

- 26.04 の coreutils は Rust 版（uutils 0.10.0）。`mkdir` は `/usr/lib/cargo/bin/coreutils/mkdir`。git は 2.56.0・bash 5.3.9・gawk 5.3.2。
- 失敗した側のログは毎回「loop-spawn.lock に pid を書き込めませんでした（読み戻し=[もう一方の pid]）」。2 本の `mkdir "${LOCK}"` が両方とも 0 を返し、両方がロックを取ったと思い込んでいた。
- 対照（2 プロセスで同じものを同時に作らせ、両方が成功した回数・各 300 回）: uutils の mkdir 258 回／python の os.mkdir 0 回／bash の noclobber 0 回／GNU の mkdir（26.04 の `/usr/bin/gnumkdir`）0 回。

git 2.56 は無関係（最初の見立ては外れ）。fail-closed の読み戻しの検査が二重取得を捕まえて止めていたので、壊れた状態で進んだことはない。

## ゴール

`mkdir` が不可分でない環境でも、ロックがちょうど 1 本だけ取れる。取れなかった側は止まらずに待つ。

## 受け入れ条件

- [x] 「既にあっても 0 を返す mkdir」に差し替えて同時 spawn を 3 ラウンドする検査 11a2 を足し、直す前に赤（3 ラウンドとも片方が落ちる）を見る
- [x] 直した後、`loop-spawn-cleanup-test.sh` 119 件すべて通る（11a2・14a/14b・11g/11h を含む）
- [x] `loop-run-guard-test.sh`・`loop-worktree-deny-test.sh`・`check-shell-portability.sh` が通る
- [ ] PR の CI の frontend-check が全段通る（ubuntu 26.04 で）
