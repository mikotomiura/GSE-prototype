# 判断

## 判断 1: main への別の PR で直す（研究者の決定・2026-11-06）

R1（PR #388）とは関係のない直しなので、main への別の PR にした。直した後に R1 へ main を取り込む。

## 判断 2: 印を noclobber の pid ファイルにする

候補は (a) noclobber の pid ファイル、(b) GNU の mkdir（`gnumkdir`）を探して使う、(c) python の os.mkdir。(b) は 26.04 にしか無い名前で、git-bash・macOS で分岐が要る。(c) は python を必須にする。(a) は bash だけで済み、git-bash（Windows のループの実行）でも同じに動く。既存の pid ファイルの名前と読み戻しの検査をそのまま使えるので、差分も小さい。

## 判断 3: 範囲に入れなかったもの

`scripts/run-features-all-poles.sh` も `mkdir "$LOCK_DIR"` の不可分を前提に二重起動を防いでいる。走らせるのは研究用の機械（macOS の BSD mkdir・G-GEAR の git-bash の GNU mkdir）で、今は影響しない。ubuntu 26.04 などの uutils の環境で走らせるようになったら、同じ形で直す。
