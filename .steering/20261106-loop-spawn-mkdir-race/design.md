# 設計

- `claim_dir <dir>` を足す。`mkdir` の後、`<dir>/pid` を bash の noclobber（`set -C` のリダイレクト＝bash が O_EXCL で開く・coreutils に依らない）で作れたときだけ取得とする。戻り値は 0（取れた）／1（取れなかった: 他の印がある・持ち主が放した直後。待って取り直す）／2（書けない: pid が普通のファイルでない等）。
- 本体のロック `${LOCK}`: `while ! mkdir` を `claim_dir` に置き換え、1 のときだけ待つ。0 と 2 はループを出て、既存の読み戻しの検査（`written_pid != $$` なら rm -rf して die）に任せる（2 は 14a の「pid を書けない」の経路にそのまま乗る）。ループの後の `printf > pid`（上書き）は消す（上書きは他のプロセスの印を消しうる）。
- stale 除去用のロック `${LOCK}.reap` も同じ前提だったので `claim_dir` にする。中に pid ができるので、放すときは `rm -f pid` の後に `rmdir`。2 のときは自分が作った除去用ロックを消す。
- `set -e` の下で `rm` の失敗で黙って抜けないよう `|| true` を付ける（11g は rm を必ず失敗させる。最初の版はこれで黙って rc=1 で抜けた）。
- 取れなかった側はディレクトリを消さない（持ち主のもの）。

## テスト戦略

- 11a2（新規）: `mkdir() { command mkdir -p "$@"; }` を export して同時 spawn。macOS でも ubuntu 26.04 と同じ状況を再現できる。
- 既存の 11a〜11h・13・14 で、stale 除去・タイムアウト・pid を書けない場合の fail-closed が変わらないことを見る。
- PR の CI（ubuntu 26.04）で 11a が通り、frontend-check の後ろの段も走ることを見る。
