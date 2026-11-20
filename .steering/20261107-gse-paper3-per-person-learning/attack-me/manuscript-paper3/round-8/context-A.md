# context-A —— 査読者・編集者・監査役に渡すもの（round 8・stage manuscript）

## 対象物
論文 "Per-person sequence models of keystroke behaviour: what remains of the gain against stronger comparisons"（本文の改訂版）。投稿先は User Modeling and User-Adapted Interaction（UMUAI・Springer）の研究論文（original research）。対象物の版: commit 77d5f324（main.tex）。article クラス・natbib で組んでいる（投稿前に Springer Nature の様式へ移す）。補足資料（Online Resource S1〜S16）はまだ作っていない。

round 7 からの主な変更: 両側に同じ平滑を当てた比べ（post hoc）に、3 つ目の対照（同じ τ と同じ作りの事前で、書き手の k 単位を別の書き手の k 単位に置き換えた当てはめを書き手の評価の単位で採点）を足した。系列の先頭の記号を採点から除いた残り（固定の平滑と両側の版・k = 5・15）を 3.4 に 1 文で足した（どちらも結果を見た後に足した計算・条件を先に決めた）。要旨の桁・限定（構造の固定・CS1 の固定の平滑・k の範囲・not prespecified）、4.4 の見出し、結論の固定の平滑の限定、重みの断り、EM の初期化と収束の 1 文、用語（cell・gain）を直した。結果を見た後の変更は 6 つ、後の確かめは 12 と数え直した。本文を 7,502 語から削り（方法・結果・考察・結論の繰り返しと細部を補足へ）、作業用のマクロを消した。

## 想定読者の素養（paper-write Step 0 の規則で決めた・round 3 と同じ値）
適応する系とユーザーモデルの研究者・学生・実務家（HCI・教育工学・情報システム・言語学・情報科学を含む）。系列モデル（隠れマルコフモデル・マルコフ連鎖）とベイズの平滑・統計の専門の訓練を前提にしない。
- 根拠（Aims & Scope の逐語・下の一次の抜粋）: "The central audience of the journal are researchers, students and industrial practitioners from the following areas: Adaptive Systems, Human-Computer Interaction, Artificial Intelligence, the Instructional Sciences, Information Systems, Linguistics, and the Information Sciences." 名指された読者のうち素養の最も少ない層（HCI・教育工学・言語学の研究者や学生）を採った。

## 読んでよいファイルの一覧（これだけ）
| ファイル | 印 | 根拠 |
|---|---|---|
| /Users/johnd/GSE-prototype-paper3/papers/per-person-learning/manuscript/main.tex | 本文（要旨・序論〜結論）＋必須の節（末尾の "Statements and Declarations"） | 原稿そのもの。Statements は規程が "Statements and Declarations" の見出しで求める節 |
| /Users/johnd/GSE-prototype-paper3/papers/per-person-learning/manuscript/references.bib | 本文（参考文献の一覧） | main.tex が \bibliography で読む |
| /Users/johnd/GSE-prototype-paper3/papers/per-person-learning/manuscript/figdata/fig2_p15_hmm3.csv ・ fig2_p15_ar1.csv ・ fig2_p15_ar3.csv ・ fig2_p15_joint.csv ・ fig2_p15.csv（同じ dir） | 補足（Figure 2 の作図の値・書き手の中央値だけ） | main.tex の Figure 2 が読む集計値 |
| /Users/johnd/GSE-prototype-paper3/papers/per-person-learning/kit/symbols/README.md | 補足 | 公開予定の記号化のキットの説明。本文は Online Resource S2 と Code availability から指す |

- 編集者の役 E は「本文」と「必須の節」の印のもの（main.tex と references.bib）だけを読む。

## 測った値（メインが機械で測った・2026-11-20・commit 77d5f324）
- 本文（序論の最初から結論の最後まで・見出しと図表のキャプションを含む・表と図の中身と数式を除く）: 7,263 語（`texcount -inc -sub=section main.tex` の節ごとの text+headers+captions の和）。round 7 の版（ed297dd4）は同じ測り方で 7,502 語（−239）。
- 要旨: 248 語（`texcount -1` で要旨の環境だけを数えた。規程の上限 250）。
- キーワード: 6 個。
- 図表: 6（Figure 3・Table 3）。参考文献: 33 件。組版 18 頁（latexmk で組み直した）。

## 投稿先の一次の抜粋（round 8 で 2026-11-20 に Chrome で原文のページを開き直し、下の 13 文が本文に逐語で在ることを照合した〔ページの本文の文字列に含まれるかを機械で照らした〕。curl は拒否のページ〔3 KB〕を返したので使わなかった）
- Aims & Scope（https://link.springer.com/journal/11257/aims-and-scope）・照合済み:
  - "User Modeling and User-Adapted Interaction provides an interdisciplinary forum for the dissemination of novel and significant original research results about interactive computer systems that can adapt themselves to their users, and on the design, use, and evaluation of user models for adaptation."
  - 分野の列挙に "acquisition and formal representation of user models" と "methods for the design and evaluation of user models and adaptive systems" を含む。
  - "The journal mainly publishes empirical research papers."
  - "The central audience of the journal are researchers, students and industrial practitioners from the following areas: Adaptive Systems, Human-Computer Interaction, Artificial Intelligence, the Instructional Sciences, Information Systems, Linguistics, and the Information Sciences."
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
1. 補足資料 S1〜S16 は未作成（本文の参照先がまだ無い）。番号の欠け（S6・S10・S11）は振り直す。
2. Uto et al. 2020 の評価の設計は全文で未確認（本文は Uto の評価の設計に触れない）。
3. Liu & Meng は 2016 年の雑誌版を引き、文言は arXiv 版で確かめた（雑誌版の文言は未照合）。
4. 元の記号列の記録ごとのハッシュは未公開（限界に 1 文ある）。
5. Springer Nature の様式への移行。
6. Code availability のリポジトリの URL と DOI、事前の記録（条件）の公開の場所は未定（投稿前に埋める）。
7. 残差の点検の要約の図は入れていない（値は補足 S13 の予定）。Table 2 の e 表記は残している。
8. Data availability で書き手ごとの値を出さない理由（著者が確かめ中）。
9. 推奨の一般化の条件の段落・Table 3 を 3 列にすることは、まだ入れていない。
10. 閾が陰性対照 5 種の最大であることの不確かさは、本文に 1 句を入れた（3.6・限界）。それ以上の扱い（種を増やす等）はしない。
11. 重ならない窓の値は本文に出さず補足 S13 に置く（本文は向きと交絡の断りだけ）。両側の版の τ は値ごとの人数と重みまでを出し、書き手ごとの値は出さない。
12. 両側の版の値（残りと 3 つの対照）は合成の書き手で確かめていない（本文に断りがある）。合成の書き手で確かめる計算はしない。
13. 入れ替えの対照の書き手の k 単位は評価の単位の直前の回なので、書き手の間の差と時間の近さを分けない（本文に断りがある）。分ける計算はしない。
14. 本文の語数は自分で置いた目安（6,800 語）を超えている（投稿先に上限の規定は無い）。
