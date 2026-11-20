# 引き継ぎ —— 論文 3（UMUAI）の返事を受ける

- 入口の文: worktree /Users/johnd/GSE-prototype-paper3（枝 docs/gse-paper3-per-person-learning）で、.steering/_handoff/20261121-paper3-umuai-response.md を読んで、UMUAI からの返事に対応してください。
- 投稿の記録: `.steering/20261120-gse-paper3-submission/submission-record.md`（Submission ID 1d92fbfb-becf-4ae5-9ab1-ec86a1fb26a4・2026-11-21 JST）。誌の原稿番号はメールで来たら記録と memory に書き足す。
- 最初の段は Technical Check。指摘のメールが来たら、直すのは原稿の写し（papers/per-person-learning/manuscript/）で、数値は変えない。直したら zip だけから組めること・校正刷りと手元の PDF が同じことを確かめ直す。
- 関連の原稿: JEDM 1484・1486（審査中）。返事の内容しだいで Dual publication の説明を見直す。
- 公開 repo（GitHub per-person-keystroke-models・Zenodo 10.5281/zenodo.24395569）に投稿先と状態を書かない。

## 査読結果が来たら
- 判定と査読者のコメントを全文で記録に写してから読む（`.steering/` に新しいタスクを `/start-task` で作る）。
- 指摘は一次（原稿・補足・解析の記録・公開 repo）で裏取りしてから、採る／採らないを研究者に AskUserQuestion で 1 件 1 問で聞く（概要と、どの問いで答えが変わるかを添える）。
- 数値を変える直しは、条件を先にコミットしてから計算し、照合をやり直す。値が変わったら公開 repo の版を上げるかを研究者に聞く（Zenodo は新しい版で出す）。
- 改訂稿を出す前に attack-me（Codex を加える）で確かめ、判定の推移が minor で続いたら閉じる。
- 返答の手紙（response letter）は指摘ごとに「どこをどう直したか」を頁と節で示す。共著者はいない。
- 改訂の投稿も SNAPP。同意の印は私が押し、規約と Submit は直前にチャットで確かめる。校正刷りは手元の PDF と照合する。
