# round 2 — 監査役

引き継ぎ: 1-1 部分的に解消（`pilot-windows.md` の Results の IMM の文が k = 1 を名指さない）・1-2・1-3 解消・1-4 意図どおりの保留・2-1 解消（数の食い違い 1 つ）・2-2 部分的に解消（1.14）・2-3 解消（判断に読んだ記録が無い）・2-4〜3-2 解消・3-3 部分的に解消（節番号）・3-4 解消・3-5 解消（data.windows.md の冒頭と小見出しの食い違い）・3-6 部分的に解消（節番号）・3-7 解消。

意図にあって対象物に無いもの: (1-a) WinEvent の経路の弁が行を書くことが §10.3 に無い（main.rs 281–283・189–194・selftest l.519）。(1-b) 証拠の commit が凍結の版を覆うか要確認。(1-c) 持ち帰り 1 の「参照の側だけ」は「参照の側と観測の key 行」が正確。
対象物にあって意図に無いもの: (2-a) 道具の改名が判断に無い（`focus_front.py` → `focus_windows.py` など）。(2-b) `deviations.md` は Windows だけのファイルではない。(2-c) 預ける基準の `src` の規則が機械で検査されない（`--check-deposit` は `src` を見ない）。
矛盾: (1) 持ち帰り 1 の「だけ」は D4・構成概念・問 4・問 5・解析の入口を含まない。(2) §10.9 と `kit/e3/README.md` の `cpu_all_zero`。(3) 節番号のずれ（pipeline.py 988–989・262・scope_windows.py 22・105・data.windows.md 23・26）。(4) `windows_def` の数（§10.7「all but one in each check run」と pilot-windows.md「Every session of the corrected TSF runs but one」）。(5) 所要時間の比（15.2/13.3 = 1.14・11.2 × 1.06 = 11.9 h は 12〜13 h の下）。(6) `data.windows.md` の範囲（冒頭は問 5 の run も・小見出しは Windows のセルだけ）。(7) context-A の測った値が古い。
注入の疑い: なし。
