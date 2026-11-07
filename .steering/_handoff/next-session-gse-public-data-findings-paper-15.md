# 次のセッション —— 公開データの知見の論文 1: attack-me を閉じた後（投稿の準備・著者の返事）

> 作成: 2026-11-07。worktree `/Users/johnd/GSE-prototype-public-findings`・枝 `docs/public-data-findings-paper`（push は研究者の手元・docs だけなので [skip ci]）。前の引き継ぎ `next-session-gse-public-data-findings-paper-14.md` の §2 の 2 と 3 は済んだ。

## §1 状態

- attack-me manuscript: round 4〜6 を回して閉じた（推移 major ×5 → round 6 minor。E が初めて「査読に回す」）。判断 39〜41・各 round の verdict.md。
- 原稿: 草稿 v7（6c5495ff）。本文 7,456 語・要旨 295 語・組むと誤り 0・overfull 1。要旨と Data and code availability の code は公開 repo 0.2.1 の版の DOI（10.5281/zenodo.24025995）。
- 探索（登録の外・条件を先にコミット）: X18（30 秒の差の両端の行・`experiments/20261107-findings-paper1-round4-checks/`）・X19（比べを s − u = 30 秒に限る・θ の非対称・閾値の表の区間・`...-round5-checks/`）。
- 公開 repo: <https://github.com/mikotomiura/stall-runup-equivalence>（v0.2.1 = 3e58363・main 49348db）。Zenodo: 全版 24014042・0.2.1 は 24025995・0.2.0 は 24025183・0.1.0 は 24014043。`paper/` は v6 の写し。
- 著者への問い合わせ（取り置きの一覧・推定の行）: 返事待ち。

## §2 やること（研究者に順を確かめてから）

1. 著者の返事が来たら、その扱いを先にする（`next-session-gse-public-data-findings-paper-11.md` の §2 の 1）。
2. 投稿の準備: カバーレター・匿名版にするか（規程は任意）・投稿の画面の項目。投稿の Submit の前に校正刷りを研究者に見てもらう（memory）。
3. 投稿する版を決めたら、公開 repo を写し直して版を上げる（`assemble.sh` → copy → `tools/verify.sh ~/gse-public-data` → push・release は研究者に確かめる）。そのとき README（英・日）と `tools/readme_media.py` の「Table 6 / 表 6」を「表 5」に（探索の表を補足へ移して番号が変わった）。原稿の DOI をその版に差し替えると、その版の写しは前の版の DOI のままになる（版の DOI は版の中に書けない）。

## §3 気をつけること

- 公開 repo に `.steering/`・GSE の `docs/`・未踏の情報を入れない。コミットに `Claude-Session:` の行を書かない。
- OSF は触らない（mrkxt の `frozen-files-63885bad.zip` の扱いは研究者が決める）。
- 空きは約 6.7 GiB。取り置きの再計算などの大きな計算は、作業 dir を repo の外に置き、使い終えたら消す。
- `.codex/budget.json` は台帳で未ステージのまま。
- 返答とファイルは日本語、記号を控える。未決は AskUserQuestion で日本語で聞く。
