# context-A —— 査読者・編集者・監査役に渡すもの（revision-integrated round 1・stage revision）

## 対象物
論文 "Per-person sequence models of keystroke behaviour: most of the gain over a shared model vanishes against stronger comparisons"（改訂稿）。〔2026-11-27 訂正: 起動の時点ではここに古い題 "what remains of the gain against stronger comparisons" を書いていた。査読者 3 人と監査役が気づいた。main.tex 29 行の題が正〕前の投稿先（ユーザーモデルの誌）では査読に回されず、理由は "lack sufficient depth" の一句だけだった（個別のコメントは無い）。その後、数値を変えずに要旨・序論・考察・限界・結論を組み直し（書き直し v2）、さらに探索の分析 1 つを補足 S14 に足し、本文の限界の第 1 項の末尾に 1 文を足した。次の投稿先は Transactions on Machine Learning Research（TMLR）の予定。
- 対象物の版: commit fbef3f75（main.tex・supplement.tex）。
- まだ TMLR の LaTeX の様式に移しておらず、匿名化もしていない（著者が把握している未決 1）。形式と匿名の不備そのものは判定に数えない。

## 想定読者の素養（TMLR の Scope と Acceptance Criteria の逐語から）
機械学習の研究者で、個人化（per-person / personalized model）の評価をする人。予測モデル・尤度・交差検証・ベイズの平滑の基本は分かるが、キーストロークのログや書き手の研究、隠れマルコフモデルの推定の細部は前提にしない。
- 根拠: "TMLR’s objective is to publish original papers that contribute to the understanding of the computational and mathematical principles that enable intelligence through learning, be it in brains or in machines."（Editorial Policies）と "The writing and organization should make the paper's main contributions, findings, and takeaways understandable to TMLR's (human) audience."

## 読んでよいファイルの一覧（これだけ）
| ファイル | 印 | 根拠 |
|---|---|---|
| /Users/johnd/GSE-prototype-paper3/papers/per-person-learning/manuscript/main.tex | 本文（要旨・序論〜結論）＋必須の節（末尾の Declarations） | 原稿そのもの。TMLR は倫理の指針しだいで Broader Impact の節を求める（下の抜粋） |
| /Users/johnd/GSE-prototype-paper3/papers/per-person-learning/manuscript/references.bib | 本文（参考文献の一覧） | main.tex が読む |
| /Users/johnd/GSE-prototype-paper3/papers/per-person-learning/manuscript/supplement.tex | 補足（Online Resource 1・S1〜S14。S14 が今回足した探索の節・570 行から） | 本文が \Sref で指す。TMLR は "Looking at the Appendix is at the discretion of the reviewers."（Author Guidelines） |
| /Users/johnd/GSE-prototype-paper3/papers/per-person-learning/manuscript/figdata/fig2_p15.csv ・ fig2_p15_ar1.csv ・ fig2_p15_ar3.csv ・ fig2_p15_hmm3.csv ・ fig2_p15_joint.csv（同じ dir） | 補足（図の作図の値・書き手の中央値だけ） | main.tex の図が読む集計値 |
| /Users/johnd/GSE-prototype-paper3/papers/per-person-learning/kit/symbols/README.md | 補足 | 記号化のキットの説明。本文が補足と Code availability から指す |

- 編集者の役 E は「本文」と「必須の節」の印のもの（main.tex と references.bib）だけを読む。

## 測った値（メインが機械で測った・2026-11-27・commit fbef3f75）
- 本文（序論の最初から結論の最後まで・見出しと図表のキャプションを含む・表と図の中身と数式を除く・結論の末尾の補足資料の案内の段 64 語を除く）: 6,272 語（`texcount -inc -sub=section main.tex` の節ごとの text+headers+captions の和）。内訳: 序論 793・関連 456・方法 2,009・結果 1,563・考察 669・限界 653・結論 135。
- 前の版との比べ（同じコマンド）: 書き直し v2（3e49aad7）6,215 語（+57。限界 +49・結論 +8）。前の投稿先に出した版（0ee3cd5f）6,984 語。
- 要旨: 245 語。図表: 6。組版の本文 PDF 20 頁、補足 PDF 18 頁。補足の S14 は約 1,600 語。

## 投稿先の一次の抜粋（2026-11-27 に curl で原文の HTML を取り、下の文が原文に逐語で在ることを機械で照らした＝照合済み。引用符・空白の違いは原文の通りでない場合がある）
- Editorial Policies（https://jmlr.org/tmlr/editorial-policies.html）:
  - "TMLR’s objective is to publish original papers that contribute to the understanding of the computational and mathematical principles that enable intelligence through learning, be it in brains or in machines."
  - "To this end, TMLR invites authors to submit papers that contain new algorithms with sound empirical validation, optionally with justification of theoretical, psychological, or biological nature; experimental and/or theoretical studies yielding new insight into the design and behavior of learning in intelligent systems; accounts of applications of existing techniques that shed light on the strengths and weaknesses of the methods; ..."
  - "Review process TMLR uses an open-reviewing, double-blind process."
  - "They will evaluate the submission, and may reject it immediately for reasons including (but not limited to): being out of scope, TMLR having insufficient reviewer expertise to adequately handle, being poor quality or unlikely to meet TMLR's acceptance criteria, or having format violations (contingent on Editor-in-Chief approval)."
  - 評価の問い: "Are the claims made in the submission supported by accurate, convincing and clear evidence? Would at least some individuals in TMLR's audience be interested in knowing the findings of this paper? Papers should be accepted if they meet the criteria, even if the contribution or significance of the work is modest."
- トップページ（https://jmlr.org/tmlr/）:
  - "TMLR emphasizes technical correctness over subjective significance, to ensure that we facilitate scientific discourse on topics that may not yet be accepted in mainstream venues but may be important in the future."
- Acceptance Criteria（https://jmlr.org/tmlr/acceptance-criteria.html）:
  - "Nor should it form the basis for rejecting work on a method considered not “novel enough”, as novelty of the studied method is not a necessary criterion for acceptance in TMLR."
  - "Additionally, a submission should clearly communicate what it has found, why those findings may be of interest to some researchers in the area, and what readers can learn from the work."
  - "The writing and organization should make the paper's main contributions, findings, and takeaways understandable to TMLR's (human) audience."
  - "A machine learning class report that re-runs the experiments of a published paper has educational value to the students involved. But if it doesn't surface generalizable insights, it is unlikely to be of interest to (even a subset of) the TMLR audience, and so could be rejected based on this criterion."
  - "On the other hand, a proper reproducibility report that systematically studies the robustness or generalizability of a published method and lays out actionable lessons for its audience could satisfy this criterion."
- Author Guidelines（https://jmlr.org/tmlr/author-guide.html）:
  - "TMLR uses a double blind review process and submissions must be anonymized."
  - "Submissions may be any length, but a paper’s length should be justified by its content and papers that are unusually long (not counting any Appendices) are likely to result in reviewing delays."
  - "Looking at the Appendix is at the discretion of the reviewers." / "Like submissions, supplementary material must be anonymized."
- Submissions（https://jmlr.org/tmlr/submissions.html）: 倫理の指針が "may require a broader impact statement" と書く（文の一部）。
- 規定なし（取得した範囲の原文に該当の文が無い）: 要旨の語数・本文の語数の上限（"any length" のみ）。

## 著者が把握している未決（判定に数えず、主張に響く場合だけ指摘してよい）
1. TMLR の様式への移しと匿名化は未着手（著者名・所属・リポジトリの URL・DOI が残っている）。
2. 公開リポジトリに S14 の分析のコードと集計の値を入れるかは未決。
3. S14 は探索の分析で、その読みの文（"Readings" の段）と数は、データを読む前に凍結した型で書いたもの。数と読みの文は変えられない（変えるなら新しい版として凍結し直す）。直せるのは本文の限界の文と、S14 を本文・補足のどこに置くか。
