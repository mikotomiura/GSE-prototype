# 次のセッション —— 公開データの知見の論文 1: round 3 の直しと公開 repo 0.2.0 の後（round 4 の要否・著者の返事）

> 使用済み（2026-11-07・続きは next-session-gse-public-data-findings-paper-15.md）。
> 作成: 2026-11-07。worktree `/Users/johnd/GSE-prototype-public-findings`・枝 `docs/public-data-findings-paper`（push は研究者の手元・docs だけなので [skip ci]）。前の引き継ぎ `next-session-gse-public-data-findings-paper-13.md` の §2 の 2 と 3 は済んだ。

## §1 状態

- attack-me manuscript round 3: major（R1・R2・R3 minor・E「直してから回す」・Codex major）。直し方は判断 38、対応は `.steering/20261105-public-data-findings-paper/attack-me/manuscript-paper1/round-3/verdict.md` §8。
- 原稿: 草稿 v4（b42c4b05）＋ Materials の再計算の句と DOI 0.2.0。題は "The 30-second signal changes of a hand-set keystroke state estimator before code-writing stalls stayed inside a preregistered equivalence band against short pauses"。要旨 292 語・本文 7,681 語・誤り 0・overfull 1。
- 探索 X16・X17: `experiments/20261107-findings-paper1-round3-checks/`（条件 d617b426・結果 2710ea5e）。
- 公開 repo: <https://github.com/mikotomiura/stall-runup-equivalence>（v0.2.0 = e9a595a・main 29464a6）。Zenodo: 全版 10.5281/zenodo.24014042・0.2.0 は 10.5281/zenodo.24025183・0.1.0 は 10.5281/zenodo.24014043。記録は `.steering/20261106-public-repo-assembly/` の判断 5。
- 取り置きの再計算: 公開した推定器で `tools/rerun-holdout.sh` を回し、`confirm_holdout.json` がバイト単位で同じ（3a73346f…72018）。
- 著者への問い合わせ（取り置きの一覧・推定の行の公開）: 返事待ち。

## §2 やること（研究者に順を確かめてから）

1. 著者の返事が来たら、その扱いを先にする（手順は `next-session-gse-public-data-findings-paper-11.md` の §2 の 1。公開 repo に一覧を足すなら `check_release.py` の取り置きの検査を、足す場所を許可する形に直して版を上げる）。
2. attack-me round 4 を回すか（Step 5）。推移は major 3 回、査読者 3 人は round 3 で minor、止め手は E。直しは題と貢献の形に触れたので、回すのが規則どおり（費用は Opus 5 本＋Codex）。回すなら同じ panel・同じ接地・役ごとの引き継ぎ（round 3 の指摘と対応・他の役は名指さない）・Codex には既知の未決の一覧（round 3 で研究者が保留したものを組み直す）。公開 repo 0.2.0 の README と DOI を一覧に入れる。
3. 次に原稿を直したら `assemble.sh` で写し直し、`tools/verify.sh ~/gse-public-data` を通して版を上げる（`.zenodo.json` と CITATION.cff の版・日付・題）。公開 repo の `paper/` の DOI は 0.1.0 のまま（その版の DOI は版の中に書けない）なので、写し直すと 0.2.0 の DOI になる。

## §3 気をつけること

- 公開 repo に `.steering/`・GSE の `docs/`・未踏の情報を入れない。コミットに `Claude-Session:` の行を書かない。
- OSF の登録 mrkxt の `frozen-files-63885bad.zip`（ADR-030 と .steering の草案を含む）は研究者に伝えた。扱いは研究者が決める（私は OSF を触らない）。
- `tools/rerun-holdout.sh` は作業 dir に書き手ごとの中間を書く（約 720 MB）。repo の外に置き、使い終えたら消す。
- `.codex/budget.json` は台帳で未ステージのまま（巻き戻さない）。
- 返答とファイルは日本語、記号を控える。未決は AskUserQuestion で日本語で聞く。
