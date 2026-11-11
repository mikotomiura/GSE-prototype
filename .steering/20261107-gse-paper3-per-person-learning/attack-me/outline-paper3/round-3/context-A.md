# context-A —— 査読者・編集者・監査役に渡すもの（round 3・stage outline）

## 対象物
論文（仮題: per-person learning in sequence models of keystroke logs）の原稿の外枠。投稿先は User Modeling and User-Adapted Interaction（UMUAI・Springer）の研究論文。本文はまだ書かれていない（外枠の段）。対象物の版: commit ede70d54（round 2 は 143fd602・round 1 は e84f4909）。

## 読んでよいファイルの一覧（これだけ）
| ファイル | 印 | 根拠 |
|---|---|---|
| /Users/johnd/GSE-prototype-paper3/papers/per-person-learning/manuscript/outline.md | 本文（外枠） | 原稿の主張・貢献・節の構成と予算を書いた唯一のファイル |
| /Users/johnd/GSE-prototype-paper3/papers/per-person-learning/kit/symbols/README.md | 補足 | 公開予定のコードの説明（記号化）。本文から補足資料・データとコードの声明で参照する予定 |

## 測った値（メインが機械で測った・2026-11-11）
- 外枠のファイル: 3732 語（wc -w・英語）・74 行（round 2 は 2808 語・70 行、round 1 は 2088 語・70 行）。
- 本文: なし（外枠の段）。外枠の節ごとの語数の予算の合計は 7,000 語（序論から結論まで・図表 4・要旨と宣言は予算の外）。round 1・2 も 7,000 語。
- 要旨・参考文献: まだ無い。

## 投稿先の一次の抜粋
2026-11-07 に Chrome で原文を開いて逐語を照合したもの。Springer は curl を拒否のページで返すため、round 2・3 では再照合していない（下の文は 2026-11-07 の照合のまま）。
- Aims & Scope（https://link.springer.com/journal/11257/aims-and-scope）: "User Modeling and User-Adapted Interaction provides an interdisciplinary forum for the dissemination of novel and significant original research results about interactive computer systems that can adapt themselves to their users, and on the design, use, and evaluation of user models for adaptation." 分野の列挙に "acquisition and formal representation of user models"、"personalization in areas such as affective computing ubiquitous and mobile computing"、"methods for the design and evaluation of user models and adaptive systems" を含む。
- 投稿規程（https://link.springer.com/journal/11257/submission-guidelines）:
  - "Please provide an abstract of 150 to 250 words."
  - "Please provide 4 to 6 keywords which can be used for indexing purposes."
  - "The following statements should be included under the heading \"Statements and Declarations\" for inclusion in the published paper. Please note that submissions that do not include relevant declarations will be returned as incomplete."
  - "All original research must include a data availability statement. This statement should explain how to access data supporting the results and analysis in the article, including links/citations to publicly archived datasets analysed"
  - "Supplementary Information (SI) will be published as received from the author without any conversion, editing, or reformatting."
- 規定なし（取得した範囲の原文に該当の文が無い）: 本文の語数・頁の上限、図表の数の上限。
- 未照合: プレプリントの方針、査読の形式。
- 参考（照合していない）: 最近の UMUAI の研究論文 3 本の本文は約 9,800〜13,300 語。
