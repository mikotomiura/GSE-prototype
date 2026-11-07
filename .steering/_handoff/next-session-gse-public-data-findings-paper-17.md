# 次のセッション —— 公開データの知見の論文 1: 投稿の後

> 作成: 2026-11-07。worktree `/Users/johnd/GSE-prototype-public-findings`・枝 `docs/public-data-findings-paper`（push は研究者の手元・docs だけなので [skip ci]）。引き継ぎ 16 の §2 の 1 と 2 は済んだ。

## §1 状態

- JEDM に投稿した（2026-11-07・投稿番号 1484・節 Articles・単盲）。記録は `.steering/20261105-public-data-findings-paper/paper-write/submission-prep.md` の「投稿」の節。状態は Queued（編集者の割り当て待ち）。
- 投稿した版: 草稿 v8。本文の PDF の SHA-256 は 5eab8d6f…（組み直すと時刻で変わるので、照合は投稿の画面から取り直したもので）。
- プレプリント: Zenodo 10.5281/zenodo.24026330（誌名は未記載）。
- 公開 repo: v0.2.2（10.5281/zenodo.24026278）。
- CS1 の著者の返事: 待ち。

## §2 やること

1. 編集者からの連絡（メール・JEDM のダッシュボード）が来たら読み、対応を研究者に聞く。査読の結果が来たら改訂の段へ（attack-me は改訂の後）。
2. プレプリントの記録に投稿先は書かない（研究者の判断・2026-11-07）。受理・公開の後に誌の DOI を足すだけにする。
3. 著者の返事が来たら引き継ぎ 11 の §2 の 1。
4. 受理・公開の後は、プレプリントと公開 repo に誌の DOI を足す（JEDM の Copyright Notice が求める）。

## §3 気をつけること

- 投稿中は原稿の内容を変えない（変えるのは査読への対応として）。他誌に出さない。
- 公開 repo に `.steering/`・GSE の `docs/`・未踏の情報を入れない。公開 repo のコミットに `Claude-Session:` を書かない。
- Zenodo は API だけ。token は `~/zenodo/zenodo_token.txt` をプロセスの中で読むだけ。
- OSF は触らない。`.codex/budget.json` は未ステージのまま。
- 返答とファイルは日本語、記号を控える。未決は AskUserQuestion で日本語で聞く。
