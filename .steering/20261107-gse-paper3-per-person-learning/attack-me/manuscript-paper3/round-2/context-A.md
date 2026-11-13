# context-A —— 査読者・編集者・監査役に渡すもの（round 2・stage manuscript）

## 対象物
論文 "Per-person sequence models of keystroke behaviour: what remains of the gain against stronger comparisons"（本文の改訂版）。投稿先は User Modeling and User-Adapted Interaction（UMUAI・Springer）の研究論文（original research）。対象物の版: commit 9a4c1d34（main.tex）。article クラス・natbib で組んでいる（投稿前に Springer Nature の様式へ移す）。補足資料（Online Resource S1〜S16）はまだ作っていない。

round 1 からの主な変更: 書き手を二分して選びと報告を分ける確かめ、共通のモデルの基の平滑と本人の連鎖の平滑を他人で選ぶ確かめ（共通だけ当て直す版と、本人の当てはめも当て直す版）、合成の感度の検査の種を 10 に増やして検出率と誤警報率を出したこと、を本文に入れ、要旨・序論・考察・結論の「残り」の読みを書き直した。

## 読んでよいファイルの一覧（これだけ）
| ファイル | 印 | 根拠 |
|---|---|---|
| /Users/johnd/GSE-prototype-paper3/papers/per-person-learning/manuscript/main.tex | 本文（要旨・序論〜結論）＋必須の節（末尾の "Statements and Declarations"） | 原稿そのもの。Statements は規程が "Statements and Declarations" の見出しで求める節 |
| /Users/johnd/GSE-prototype-paper3/papers/per-person-learning/manuscript/references.bib | 本文（参考文献の一覧） | main.tex が \bibliography で読む |
| /Users/johnd/GSE-prototype-paper3/papers/per-person-learning/manuscript/figdata/fig2_p15_hmm3.csv ・ fig2_p15_ar1.csv ・ fig2_p15_ar3.csv ・ fig2_p15_joint.csv ・ fig2_p15.csv（同じ dir） | 補足（Figure 2 の作図の値・書き手の中央値だけ） | main.tex の Figure 2 が読む集計値 |
| /Users/johnd/GSE-prototype-paper3/papers/per-person-learning/kit/symbols/README.md | 補足 | 公開予定の記号化のキットの説明。本文は Online Resource S2 と Code availability から指す |

- 編集者の役 E は「本文」と「必須の節」の印のもの（main.tex と references.bib）だけを読む。

## 測った値（メインが機械で測った・2026-11-13・commit 9a4c1d34）
- 本文（序論の最初から結論の最後まで・見出しと図表のキャプションを含む・表と図の中身と数式を除く）: 6,204 語（`texcount -inc -sub=section main.tex` の節ごとの text+headers+captions の和: 序論 588・関連研究 481・方法 1,804・結果 1,728・考察 713・限界 724・結論 166）。round 1 の版（eff4bc93）は同じ測り方で 4,451 語。
- 要旨: 250 語（`texcount -1` で要旨の環境だけを数えた）。
- キーワード: 6 個。
- 図表: 5（Table 1・Figure 1・Figure 2・Table 2・Table 3）。参考文献: 33 件（本文で引いた鍵も 33）。
- 補足資料の参照: S1〜S5・S7〜S16（S6 は本文から参照されていない）。

## 投稿先の一次の抜粋（2026-11-13 に Chrome で原文のページを開き、下の文が本文に逐語で在ることを照合した。curl は 3,038 バイトの拒否のページを返す）
- Aims & Scope（https://link.springer.com/journal/11257/aims-and-scope）・照合済み:
  - "User Modeling and User-Adapted Interaction provides an interdisciplinary forum for the dissemination of novel and significant original research results about interactive computer systems that can adapt themselves to their users, and on the design, use, and evaluation of user models for adaptation."
  - 分野の列挙に "acquisition and formal representation of user models" と "methods for the design and evaluation of user models and adaptive systems" を含む。
- 投稿規程（https://link.springer.com/journal/11257/submission-guidelines）・照合済み:
  - "Please provide an abstract of 150 to 250 words."
  - "Please provide 4 to 6 keywords which can be used for indexing purposes."
  - "The following statements should be included under the heading \"Statements and Declarations\" for inclusion in the published paper."
  - "Other declarations include Ethics approval, Consent, Data, Material and/or Code availability"（の文の冒頭）
  - "All original research must include a data availability statement."
  - "Supplementary Information (SI) will be published as received from the author without any conversion, editing, or reformatting."
  - "For LaTeX submissions we encourage authors to use the Springer Nature LaTeX template"
  - "This journal follows a single-blind reviewing procedure."
- 規定なし（取得した範囲の原文に該当の文が無い）: 本文の語数・頁の上限、図表の数の上限、プレプリントの方針（"preprint" の語がページに無い）。
- 参考（照合していない）: 最近の UMUAI の研究論文 3 本の本文は約 9,800〜13,300 語。

## 著者が把握している未決（投稿前に対応する。判定に数えず、主張に響く場合だけ指摘してよい）
1. 補足資料 S1〜S16 は未作成（本文の参照先がまだ無い）。
2. Uto et al. 2020 の評価の設計は全文で未確認（本文は Uto の評価の設計に触れない）。
3. Liu & Meng は 2016 年の雑誌版を引き、文言は arXiv 版で確かめた（雑誌版の文言は未照合）。
4. 元の記号列の記録ごとのハッシュは未公開（限界に 1 文ある）。
5. Springer Nature の様式への移行・補足の番号の振り直し。
6. Code availability のリポジトリの URL と DOI、事前の記録（条件）の公開の場所は未定（投稿前に埋める）。
7. 残差の点検の要約の図は入れていない（値は補足 S13 の予定）。Table 2 の e 表記は残している。
