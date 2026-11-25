# 投稿先の適合（論文 3・書き直し v2 の後・paper-write Step 0）

- 調べた日: 2026-11-25。原文の取り方: A 群（TMLR・JEDM・JLA・JWA・JoWR）は `curl` で保存した原文、B 群（BRM・IJHCS・TiiS・Machine Learning・Reading and Writing）は Chrome で開いた原文の抜粋（curl は Springer の Client Challenge・Elsevier と ACM の Cloudflare で止まった）。下の逐語は、判定に使う 20 文をメインが保存した原文に grep で当てて在ることを確かめた（「照合済み」）。保存先は作業用の置き場（`/private/tmp/claude-501/-Users-johnd-GSE-prototype/e9778ff9-4639-4b34-989f-6871d30644b5/scratchpad/venue/`・消えうる）。取れなかったものは「未照合」。
- 調べは 2 本の調査役（general-purpose・sonnet）に渡し、報告をメインが一次で照らした。

## 目的と読ませたい相手（先に確かめる）

- 持ち帰り（outline.md の先頭）: 行動ログの系列モデルで、同じ構造の共有モデルとの比べが見せる本人ごとの得は、強い比べの前でほとんど消える。本人の 1 次マルコフ連鎖を並べるのが安い確かめになる。
- 届けたい相手: ログから本人ごとのモデル（個人化・ユーザーモデル）を作り、共有モデルと比べて「個人化は効く」と報告する研究者と、それを読む設計者・査読者。変えたいこと: 同じ構造の共有モデルに勝つことを、個人化の根拠として読まない／本人の連鎖を並べる。
- 研究の一言の分類（題と要旨の名詞から）: 「公開のキーストロークの記録 1 つ（＋境界の例 1 つ）で、本人ごとの HMM と共有モデルの比べ方を確かめた評価の研究。比べを強くすると得が消える、という否定寄りの知見」。
- 判断 2 の 1〜3（答えが「分からない」・実質 1 データ・事後の解析）は誌を替えても残る。だから、新しさや大きな効果より「主張と根拠の一致」「控えめな貢献」を受け入れると明言する誌が合う。

## 候補ごとの比べ

| 誌 | 費用 | AI の方針（門） | 範囲の一句（門 1） | 門 3 看板の語 | 優先の明言 | 判定 |
|---|---|---|---|---|---|---|
| TMLR | 無料（"TMLR imposes no fees or payments to authors"） | 通る（"LLMs may be used as general-purpose assistive tools" / ただし "If a paper fully is AI generated with little or no human involvement ... it is unlikely to meet this criterion"） | "experimental and/or theoretical studies yielding new insight into the design and behavior of learning in intelligent systems" ・ "accounts of applications of existing techniques that shed light on the strengths and weaknesses of the methods" → 言い直しても問いは変わらない（本人ごとの学習の得の評価）＝通る | machine learning・personalization は要旨に入っていない → 言い換えが要る（要旨に "machine learning" の語を問いを曲げずに入れられる） | "TMLR emphasizes technical correctness over subjective significance" ・ "novelty of the studied method is not a necessary criterion for acceptance" ・ "Papers should be accepted if they meet the criteria, even if the contribution or significance of the work is modest" | **第 1 候補** |
| Behavior Research Methods（Springer） | 購読の選択で無料（OA は £2690）。投稿料・頁料の無いことの明言は未照合 | 通る（Springer 共通の文。Methods に記す。ML 誌の頁で照合。BRM の頁では未照合） | "articles concerned with the methods, techniques, and instrumentation of research in experimental psychology" → 「行動の記録から本人ごとのモデルを評価する方法」と言えば入るが、序論の入り方を心理学の方法に変える必要＝言い換えが要る | experimental psychology・behavioural research の語は無い → 言い換えが要る | 明言なし（探した: 投稿規程の全文の語の検索） | 第 2 候補。IME の論文が同じ誌で審査中 |
| Machine Learning（Springer） | 購読の選択で無料（OA は £2490） | 通る（"Use of an LLM should be properly documented in the Methods section"） | "Research methodology papers improve how machine learning research is conducted" ・ "Papers making claims about ... methods ... provide solid support via empirical studies" → 評価の作法の論文として通る | machine learning の語が無い → 言い換えが要る | 明言なし | 第 3 候補。分量の上限は未照合 |
| JEDM | 無料（"no article processing charges"） | 通る（開示の節を参考文献の前に） | "computational approaches for analyzing electronic repositories of student data to answer educational questions" → 主データ CoAuthor は学生のデータでなく、問いも教育の問いでない＝通らない | — | "Accepted submissions should extend beyond mere application and must include elements that contribute to broader knowledge" | 外す（門 1）。論文 1・2 が審査中でもある |
| JLA | 無料 | 著者向けの文なし（6 頁を検索） | "research into the challenges of collecting, analysing and reporting data with the specific intent to improve learning" → 学習の改善の問いでない＝通らない | — | "All research papers must make explicit their significance for the wider field of learning analytics" | 外す（門 1） |
| Journal of Writing Analytics | OA（APC の無いことの明言は未照合） | 著者向けの文なし | "the study of writing processes and written texts through the use of a wide range of analytical tools" → 書く過程の研究としては入るが、本論文は書き手について何も言わない（どの比べ方で得が消えるか）＝言い換えが要る（疑わしい） | writing analytics の語は無い | 明言なし | 保留（読者の素養と量的な厚みが合わない恐れ） |
| JoWR | 無料 | 著者向けの文なし | "scientific research exploring the mental and social processes underlying written production" ＋ "findings fail to make a contribution to understanding that extends beyond the specific context" で desk reject → 書く過程を問わない＝通らない | — | 上の desk reject の文 | 外す（門 1）。打鍵版の論文 A も同じ誌 |
| IJHCS（Elsevier） | 購読の選択で無料（"No open access publication fee"） | 通る（投稿時に申告） | "research on the design and use of interactive computer technology" ＋ "expected to focus on concrete solutions for concrete user audiences" → 設計の提案が無い＝通らない | — | "we do not normally consider ... contributions ... which analyse an issue but do not comprise significant and robust design and evaluation elements" | 外す（門 1） |
| ACM TiiS | 有料（"All ACM publications ... are 100% Open Access"・機関が ACM Open に入っていなければ APC $1300〜1800。困窮の免除の頁は未照合） | 未照合 | 未照合 | — | — | 外す（費用） |
| Reading and Writing（Springer） | 購読の選択で無料 | 通る | "pertaining to the processes, acquisition, and loss of reading and writing skills" ＝通らない | — | — | 外す（門 1） |
| IEEE TLT・IJAIED | 未照合（bot 対策で原文が取れなかった） | 未照合 | 未照合 | — | — | 比べに入れない |

## 門 2（投稿先の論文と会話しているか）

- 原稿の参考文献に、上の候補の誌の論文は無い（TMLR・BRM・Machine Learning とも 0 本）。新しい領域の扱い（paper-write Step 0）: 門 1・3 が「通らない」でなければ外さず、送り状で読者にとっての新しさを 1 文で述べる。
- TMLR の最近の論文（OpenAlex で TMLR に紐づく 6 本を開いた・arXiv 版）: 評価の作法を問い直す論文が載っている（"Auditing GeoFM Evaluation for Field-Extent Segmentation: Label Proxies, Baselines, and When Frozen Features Matter" 2026・doi:10.48550/arxiv.2611.00054・約 7.3k 語、"A Note on Generalization in VAEs: How Effective Is Synthetic Data & Overparameterization?" 2025・doi:10.48550/arxiv.2310.19653）。本人ごとの得とベースラインの論文としては "Fusion of Global and Local Knowledge for Personalized Federated Learning" 2023・doi:10.48550/arxiv.2302.11051。キーストロークや本人ごとの HMM の論文は見つからなかった。引ける候補はこの 3 本（読むのは誌を決めた後）。
- 同じ種類の研究（1 つのデータで比べ方を確かめ、得が消える型）: TMLR で型の一部に当たる 1 本（上の評価の監査）。6 本を開いたが結果の節を精読していないので、本数は「未判定」。BRM・Machine Learning は 0 本を開いた → 「未判定」。

## 分量

- TMLR: "Submissions may be any length, but a paper's length should be justified by its content"。付録と補足は "at the discretion of the reviewers"。要旨の語数の規定は見当たらない。本文 6,215 語は最近の 6 本（約 6.4k〜9.1k 語・1 本 17.7k）の範囲。
- BRM: 要旨 250 語以内。本文の上限は見当たらない。
- Machine Learning: 未照合。

## TMLR を選ぶときの注意（研究者に伝える）

1. 査読が公開される: "TMLR uses an open-reviewing, double-blind process. An open reviewing model, where papers, reviews, and discussion are visible to the public"。投稿した原稿・査読・やり取りが OpenReview に公開で残る（不採録の扱いは未照合）。公開物に投稿先と状態を書かない方針とぶつかるかは研究者が決める。
2. 二重盲: 原稿を匿名にする（著者・所属・公開 repo の URL・Zenodo の DOI を伏せる）。プレプリントは "allowed to upload their submissions to arXiv or other preprint servers at any time" で、Zenodo の既存のプレプリントは残してよい。
3. 書式は TMLR の LaTeX（sn-jnl から移す）。
4. AI: 補助としての利用は可。人の関与が乏しい全面の生成は基準を満たしにくいと明言しているので、著者が全ての引用と数値を照らしたことを開示に残す（3.4 の文は既にそう書いている）。
5. 看板の語: 要旨と序論の第 1 段に machine learning・personalization の語を、問いを曲げずに入れる（門 3 の言い換え）。

## 結論（4 行）

- 範囲の門: TMLR は 門 1 通る・門 2 通らない（新しい領域・送り状で 1 文）・門 3 言い換えが要る。BRM は 1・3 とも言い換えが要る。Machine Learning は 1 通る・3 言い換えが要る。
- 種類の貢献: 評価の作法を問い直す知見（新しい手法なし）。TMLR の優先 "technical correctness over subjective significance"・"novelty ... is not a necessary criterion" に入る。読者は機械学習の研究者（個人化の評価をする人）で、系列モデルの推定の細部は前提にしない。
- 分量: TMLR は上限なし（内容で正当化）。本文 6,215 語で足りる。
- 一言の分類が優先に入るか: TMLR は入る（優先の文が控えめな貢献を明言）。BRM・Machine Learning は明言なしで、同じ種類の研究の本数は未判定。推奨は TMLR。決めるのは研究者（公開の査読の扱いを含む）。
