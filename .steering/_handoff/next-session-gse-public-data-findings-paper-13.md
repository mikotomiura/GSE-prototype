# 次のセッション —— 公開データの知見の論文 1: 公開 repo と DOI の後（attack-me round 3 の要否・著者の返事）

> 使用済み（2026-11-07・§2 の 2 と 3 は済んだ。続きは `next-session-gse-public-data-findings-paper-14.md`）。
> 作成: 2026-11-07。worktree `/Users/johnd/GSE-prototype-public-findings`・枝 `docs/public-data-findings-paper`（push は研究者の手元・docs だけなので [skip ci]）。前の引き継ぎ `next-session-gse-public-data-findings-paper-12.md` の §2 の 1 は済んだ。

## §1 状態

- 公開 repo: <https://github.com/mikotomiura/stall-runup-equivalence>（公開・v0.1.0 = b3bdc9a・main はその後に DOI を足した 3991670）。手元は `/Users/johnd/stall-runup-equivalence`。
- Zenodo: 全版 10.5281/zenodo.24014042・0.1.0 は 10.5281/zenodo.24014043。zip はタグと同じ中身を確かめた。
- 記録: `.steering/20261106-public-repo-assembly/`（判断 1〜4）。組み立ては `assemble.sh`（追跡済みのファイルだけを写す一覧）。
- 中身: 推定器の crate・論文の 3 つの実験（スクリプト・条件・notes・集計の結果）・依存先 4 つの実験のスクリプトと条件・原稿の tex（`paper/`）・README（英・日・図 2 つ）・`tools/`（`verify.sh`・`check_release.py`＋陽性対照 27 件・`check_manifest.py`・`readme_media.py`）。
- 入れていない（研究者の指示）: GSE の `docs/`・`.steering/`・`src-tauri/`・未踏の情報。manifest の 6 件は「公開しない」と示す（事前登録の草案 3 本は OSF の mrkxt に別名である）。書き手ごとの値・推定の行・取り置きの一覧・データ。
- 原稿: 要旨の置き字を DOI に・Materials・限界・補足の係数の節を公開に合わせた（7fc19bc6）。公開 repo の `paper/` は直す前の版のまま。
- 著者への問い合わせ（取り置きの一覧の公開）: 返事待ち。

## §2 やること（研究者に順を確かめてから）

1. 著者の返事が来たら、その扱いを先にする。手順は `next-session-gse-public-data-findings-paper-11.md` の §2 の 1（返事で推定の行・id の一覧の扱いを決め、考察の Materials と限界を直す）。加えて公開 repo について（一覧を足すなら公開 repo に足して版を上げる・`check_release.py` の取り置きの検査は一覧そのものを見つけたとして赤になるので、足す場所を許可する形に直す）。
2. attack-me round 3 を回すか。止める理由だった「推定器と replay が未公開」は閉じた。回すなら同じ panel・Codex あり・既知の未決は round 2 の `tmp/codex-input.md` の 18 件を組み直し、推定器の公開で閉じた件を外す。公開 repo の README と DOI を査読者に渡す。
3. 原稿を直したら `assemble.sh` で写し直し、`tools/verify.sh ~/gse-public-data` を通して v0.1.1 などを出す（Zenodo は `.zenodo.json` の版と日付も直す）。

## §3 気をつけること

- OSF の登録 mrkxt には `frozen-files-63885bad.zip`（manifest の全ファイル＝ADR-030 と .steering の草案を含む）が公開で添えてある（`experiments/20261105-findings-paper1-prefreeze/notes.md` 126 行）。研究者に伝えた。扱いは研究者が決める（私は OSF を触らない）。
- 公開 repo のコミットには `Claude-Session:` の行を書かない（研究者の選択）。committer は repo の設定で Mikoto Miura とメール。
- Zenodo の GitHub 連携は CITATION.cff を読めずに失敗した（原因は不明）。`.zenodo.json` が優先されるので、版を上げるときは `.zenodo.json` を直す。
- `.codex/budget.json` は台帳で未ステージのまま（巻き戻さない）。2026-11-07 は cross-review で約 3.5 万トークン。
- 返答とファイルは日本語、記号を控える。未決は AskUserQuestion で日本語で聞く。
