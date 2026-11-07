# 次のセッション —— 公開データの知見の論文 1: 投稿（研究者）と、その後

> 作成: 2026-11-07。worktree `/Users/johnd/GSE-prototype-public-findings`・枝 `docs/public-data-findings-paper`（push は研究者の手元・docs だけなので [skip ci]）。前の引き継ぎ 15 の §2 の 2 と 3 は済んだ。

## §1 状態

- 投稿先 JEDM。単盲（匿名版にしない・判断 42）。規程の照合と投稿の画面の項目は `.steering/20261105-public-data-findings-paper/paper-write/submission-prep.md`。
- 原稿: 草稿 v8（推定器の設計者が著者であることを `sections/data.tex` に 1 文）。code の DOI は公開 repo 0.2.2（10.5281/zenodo.24026278）。組むと誤り 0・overfull 1・32 頁・本文 7,463 語・要旨 295 語。組み方は `manuscript/BUILD.md`（テンプレートは JEDM の頁の zip）。
- カバーレター: `papers/public-data-findings/submission/cover-letter.md`（英語・pandoc で 1 頁）。利益相反（推定器の設計者・資金なし・編集者との関係なし）・プレプリントの DOI・生成 AI の宣言の場所・単盲の理由。
- 公開 repo: v0.2.2 = 3ea2591（`paper/` は v8 の写し・DOI は 0.2.1 のまま）・main 7e4d81d（DOI を README と CITATION に）。verify が 0。Zenodo の zip はタグと同じ。
- プレプリント: Zenodo 10.5281/zenodo.24026330（2026-11-07 公開・PDF は手元と SHA-256 一致）。
- CS1 の著者の返事: 待ち。

## §2 やること

1. 研究者が JEDM に登録（「Register as Author」に印）して投稿の画面を開く。私は画面の文を Chrome で読んで `submission-prep.md` の項目と照合し、要旨の素の文を渡す（Zenodo の記録 24026330 の description と同じ文）。入力と Submit は研究者。Submit の前に、システムが作った版の全頁を研究者が見る。
2. カバーレターの「編集者との関係なし」は研究者が確かめた（2026-11-07・関係なし）。
3. 投稿の後: 受付の番号を記録し、プレプリントに誌名を足すかを決める（Zenodo の記録の notes の更新は新しい版を作らずにできる）。
4. 著者の返事が来たら引き継ぎ 11 の §2 の 1。

## §3 気をつけること

- 公開 repo に `.steering/`・GSE の `docs/`・未踏の情報を入れない。公開 repo のコミットに `Claude-Session:` を書かない。
- Zenodo の下書きは API だけで作る（画面で作ると DOI が空で publish が 400）。token は `~/zenodo/zenodo_token.txt` をプロセスの中で読むだけ。
- OSF は触らない。`.codex/budget.json` は未ステージのまま。
- 返答とファイルは日本語、記号を控える。未決は AskUserQuestion で日本語で聞く。
