# 重要な設計判断

前のタスクの記録は `.steering/20260929-p321-paper-submission-prep/decisions.md`（判断 1〜24）。ここでは番号を 1 から振り直す。2026-11-21 の grill で、研究者が AskUserQuestion で選んだもの。「推奨」は私が出した推奨で、判断 10 のほかはすべて研究者が推奨を選んだ。

## 判断 1: 改訂の範囲 = verdict §5 の major 1〜10 と minor をすべて
- **決定**: major と minor をすべて直す。nit も一緒に拾う。
- **理由**: いま残せば次の査読でそのまま返ってきて、往復が 1 回増える。原稿はいま自由に変えられる。
- **却下案**: major だけ／外延の major（A・B・C・G）だけ（早く出せるが、残りが査読で返る）。

## 判断 2: 指摘 A = 主の定義はそのまま・打ち切りとしての感度分析と区間を足す
- **決定**: 凍結した主の定義は変えない。足すのは 2 つ。(1) 感度分析: DF3 を除く／DF3 と DF5 を除く／D2 の研究期間の終わりを除く。(2) 区間 [R0′, R0] の提示。11.2pp は「最終的な解決に対しては上限」と書き、要旨と結論の "over-states" の言い方を弱める。D1 の DF3 の位置と k = 7 も報告する。
- **理由**: 凍結からの逸脱を作らずに、査読者 3 人の指摘に答えられる。参考値（verdict §4）: DF3 を除くと 2.6pp、DF3 と DF5 を除くと 1.3pp。
- **却下案**: 見出しを 1.3〜11.2pp の区間に替える（凍結からの逸脱として開示が要る）。

## 判断 3: 指摘 B = 誤読の実例を探し、無ければ主張を絞る
- **決定**: 検索の手順（どこを・どの語で・どこまで）を先に decisions.md に決める。見つかれば引く。無ければ「予防的な報告の推奨」に絞り、検索の結果（0 件を含む）を本文に書く。本文が取れなければ Chrome で読む。有料のものは使わない。
- **理由**: 探さずに絞ると、実例を探したかを査読で問われうる。
- **却下案**: 探さずに絞る。

## 判断 4: 指摘 C = 題を変える・案は用語をそろえた後で
- **決定**: 先に本文の用語を、内容を表す名前にそろえる。そのあと題の案を 2〜3 本出し、研究者が選ぶ。前半の "When "no help" is not "solved"" は残す方向。
- **却下案**: 題はそのままにし、本文を題に合わせる。

## 判断 5: 指摘 G = 原著者に照会する・返事を待たずに出す
- **決定**: 文面は Claude が下書きし、研究者が送る（外に出る行為）。待つ期間は 2 週間を目安にする。返事が無ければ「照会したが未回答」と本文に書いて投稿する。
- **理由**: 査読者 2 人が照会を求めている。未回答でも「照会した」と書ける。
- **却下案**: 返事が来るまで投稿しない（時期が読めない）／照会しない。

## 判断 6: 出し先 = 候補を一次で比べてから研究者が選ぶ
- **決定**: 改訂の最初の段で、IST・JSS・IEEE TSE・Software Quality Journal などを比べる。見るのは費用（購読型で 0 か）・発表の義務・範囲・頁の上限・クラス・プレプリントの規程で、出版社の公式ページで確かめる（curl が 403 なら Chrome）。表にして研究者が選ぶ。
- **理由**: 書式（頁の上限・クラス）が改訂の仕方に効くので、改訂の前に決めたい。⚠️ EMSE は判断 24 の通知で「出し直してよい」とは書いていないので、候補に入れるなら受け入れの状況を確かめる。
- **却下案**: なし（研究者に決めた雑誌は無かった）。

## 判断 7: プレプリント = 改訂版を Zenodo に・arXiv は止める
- **決定**: 改訂版のプレプリントを Zenodo に置く。下書きまでは Claude、publish は研究者の確認の後。出し先の規程がプレプリントを許すかは一次で確かめる。arXiv の endorsement は止める（Shepperd には頼まない）。
- **理由**: endorsement が要らない。IME の論文で手順ができている。
- **却下案**: arXiv を続ける（endorsement が取れるまで出せない）／出さない。

## 判断 8: 指摘 K = D1 の派生表をアーカイブに入れる（ライセンスが許せば）
- **決定**: episode 単位の派生表（個人を特定しない形）を Zenodo の新しい版に入れる。元データのライセンスが再配布を許すかを先に一次で確かめ、許されなければ入れずに言い方だけ直す（"every number … one command"）。
- **却下案**: 言い方だけ直す。

## 判断 9: 指摘 H = クラスタが少ないときの区間を併記する・手法は文献で確かめてから
- **決定**: 主の区間は凍結のまま。補助の区間（wild cluster bootstrap などの候補）を、一次の文献（`citation-ssot`）で確かめてから 1 つ選んで足す。あわせて「0 を含まない」の言い方と推定の対象も直す。
- **却下案**: 併記しない（限界として書くだけ）。

## 判断 10: 投稿の前に attack-me round 2 を当てる ／ /reimagine を使う
- **決定**: 直した原稿に attack-me round 2 を当てる。査読者の席は出し先の分野に合わせる。/reimagine は design.md を書いた後、着手の前に使う（研究者の選択。私の推奨は「使わない」だった）。
- **理由**（round 2）: 直した箇所が新しい穴を生んでいないか、round 1 の指摘が本当に閉じたかを確かめる。

## 判断 12: S0 —— journal 版の本文は committed・fresh の件数を書き直していない ／ 照会の前提を一次で固めた（2026-11-21）
- **入手**: Springer のページは有料（"Buy article PDF ￥4,980"・Chrome で確認）。OpenAlex の無料の版は arXiv v1 だけ（別の版）。Google Scholar の「全 4 バージョン」に NSF Public Access Repository の PDF（`https://par.nsf.gov/servlets/purl/10490781`）があった。研究助成の成果の公開の置き場で、合法に無料で読める。2,295,565 B・SHA-256 `38fe70013497c01686dac59c6077cb1c350cc1942dbd49e1435ac9eccd24b94c`・34 頁・"Page 2 of 34 … (2023) 28:117 Empirical Software Engineering" の版面（scratchpad に置いた。repo には入れない）。⚠️ 2026-09-28 に [P433] の全文をどこから読んだかは記録が無い（同じ置き場の可能性があるが、確かめていない）。
- **逐語**（journal 版）: "Consulting resources was the least common activity, occurring in only 33% of debugging episodes. However, 91% of developers consulted external resources at least once." ／ "Consulting resources occurred in all committed debugging episodes, but only 15% of fresh debugging episodes." ／ "coding 89 debugging episodes and 2135 instances of activities" ／ "Half of the debugging episodes focused on committed defects and did not end with a successful fix, either because more information was needed to reproduce the defect or the developer deferred debugging until later."
- **件数**: journal 版の本文（抽出した文字）に、committed・fresh の件数は無かった（図 7 の時系列の図にだけある）。arXiv v1 の逐語は "Ten debugging episodes started because five developers (D1, D2, D3, D5, and D8) worked towards debugging reported defects" ・ "In the remaining 79 debugging episodes"。共有データからの再現も 10・79（`metrics.json` の `d1_gate_v1`）。→ verdict §4 の注意（「journal 版が committed 10・fresh 79 を報告しているか」）への答えは、「**報告していない。ただ『committed の半分が修正に至らなかった』は 10 件中 5 件と合う**」。原稿の 33% と 24.7% の不整合は「v1 の件数を仮定すると」という条件つきで書く（S5）。
- **照会の文面**: `inquiry-alaboudi-latoza-draft.md`（英語・4 問: consultation の定義／件数と起点の割り当て／コーディングの改訂／DF3 の episode のその後）。宛先は研究者が確かめる。

## 判断 11: 出し先 = Journal of Systems and Software（JSS・Elsevier）（2026-11-21・研究者の選択）
- **調べ方**: 出版社の系統ごとに Sonnet の汎用エージェント 3 本へ並列で渡した（判断 6）。3 本とも、誌ごとの投稿ガイドの本体を WebFetch で読めなかった（ScienceDirect・Wiley は 403、Springer は認証へのリダイレクト）。そこで判断に使う行は、私が Chrome の `javascript_tool` で公式のページから逐語で取った（下の「一次」）。「代行」はサブエージェントが取った逐語で、私は開いていない。
- **比較**（費用は購読型で出す場合）:

| 誌 | 費用 | 査読 | preprint | 長さ・書式 | 範囲 |
|---|---|---|---|---|---|
| **JSS** | 一次 "No open access publication fee."（`sciencedirect.com/journal/journal-of-systems-and-software/publish/open-access-options`） | 一次 "This journal follows a single anonymized review process." | 一次 "Authors may share preprints in line with Elsevier's article sharing policy. Sharing preprints, such as on a preprint server, will not count as prior publication." | 一次 "It is encouraged that authors submit full-length papers of less than 36 pages single-column or 18 pages double-column." ／ 要旨は "does not exceed 250 words"（いまの要旨は超える） | 代行 "All articles should provide evidence to support their claims" ・ "The journal welcomes reports of practical experience for all of these topics, as well as replication studies."（`shop.elsevier.com/journals/journal-of-systems-and-software/0164-1212`）／ 代行 JSS Open Science Initiative（再現一式を Open Science Board が審査し、採否には影響しない） |
| IST | 一次 "No open access publication fee." | 一次 single anonymized | 一次（JSS と同じ文） | 一次 "A research paper's maximum length is 15,000 words … figures and tables count 200 words each." ／ 構造化した要旨が必須 | 一次 "Empirical studies of all aspects of engineering and managing software development" ／ データは一次 "Option C"（寄託が必須） |
| SQJ | 一次 "The journal does not charge a submission fee or publication fee." | 一次 "This journal follows a single-blind reviewing procedure." | Springer 全体（前タスク判断 23 の一次） | 一次 "The submission must be generated via LaTeX using the header \documentclass{sn-jnl}." | 一次 品質と品質管理が中心（"all aspects of software quality"） |
| JSEP | 一次 "There is no page charge to authors." | 確かめられなかった | 一次 "…allow authors to submit manuscripts that have already been made available on a non-commercial preprint server." | 確かめなかった | 代行（検索の要約）開発・テスト・保守・進化 |
| TSE | 代行（IEEE CS の MOPC の PDF）"Any pages or fraction thereof exceeding this limit are charged $200 per page." ・ "…12 formatted pages for Transactions…" → 外した | — | — | — | — |
| TOSEM | 代行（検索の要約）2026-01-01 から全面 OA・APC が要る → 外した（memory `feedback_venue_no_talk_zero_cost` と同じ） | — | — | — | — |

- **決定**: JSS（研究者の選択・私の推奨）。
- **理由**: 範囲に「主張に証拠を」と「replication studies の歓迎」があり、再解析の論文にいちばん合う。Open Science Initiative があり、公開済みの再現一式を生かせる。査読は single anonymized なので、Zenodo の preprint（判断 7）と両立する。
- **却下案**: IST（範囲は合う。構造化した要旨が要るだけで、条件は満たす。JSS が不採択なら次の候補）／SQJ（書式の手間は最小だが範囲が品質管理に寄る）／JSEP（査読の方式が未確認・範囲が保守と進化に寄る）／TSE（超過頁料）／TOSEM（APC）。
- **改訂への効き方**（design.md の前提）: 要旨を 250 語以内に削る ／ 書式は elsarticle を勧められている（"We encourage you use our LaTeX template"。初回の投稿で必須かは、JSS の LaTeX の節を design の段で確かめる）／ 編集できるソース一式を出す ／ Highlights が要るかを確かめる ／ Open Science Initiative に参加するか（研究者の判断・design の段で）。
- ⚠️ **未確認**: 代行の行（範囲・Open Science の文）は私が開いていない。design の段で JSS の投稿ガイドの Article structure・Highlights・LaTeX・Open Science の節を一次で読む。サブエージェントは「JSS が 2025 年に査読の依頼に 20 件の上限を設けた」と編集者の論考（arXiv 2601.19217・本文は読んでいない）の要約から報告した → 受け付けの状況に関わるので、design の段で確かめる。

## 判断 13: S0c —— 照会を送った（2026-11-21・研究者）
- 研究者が mmiura.network の Gmail から送った。宛先は `tlatoza@gmu.edu`・`aalaboud@gmu.edu`（journal 版の著者情報）。文面は `inquiry-alaboudi-latoza-draft.md` の改稿（丁寧に直した版。4 つの問いの中身は判断 12 の版と同じ）。
- 待つ目安は 2 週間 = **2026-12-05**。返事を待たずに S1〜S8 を進め、S9 で返事か「未回答」を RQ4 の節へ入れる。
- 同じ日に研究者が決めたこと: Open Science Initiative に参加する ／ 推薦の査読者の欄は投稿の直前（S9）に確かめる（候補の下書きは S2 の F と一緒に作る）／ 費用が無いなら JSS のまま（判断 11 の一次 "No open access publication fee." と購読型の出し方で無料）。

## 判断 14: S1 —— 枠を elsarticle に移した（論文用リポジトリ `revision-jss` の `061938a`・未 push）
- **分け方**: `main.tex` を `abstract.tex`（要旨の 1 段落）・`body.tex`（§1〜結論）・`declarations.tex`（声明。`\bmhead` を枠が定める `\declhead` に替えただけ）と、枠 `main-jss.tex` に分けた。旧 `main.tex` は `git rm`（タグ `submission-2026-09-29` に残る）。
- **本文の差分 0 の確かめ方**: 使い捨てのスクリプトで、3 つのファイルを旧 `main.tex`（main の版）の該当行と文字単位で比べた → 一致。題・キーワードも一致。
- **枠**: `elsarticle` の `preprint,12pt,authoryear`・`elsarticle-harv`・`hyperref`（本文の節題が `\texorpdfstring` を使う。sn-jnl は hyperref を読んでいた）・`geometry` で A4・余白 25mm。理由: 既定の余白だと表 3 つが本文幅を 30〜59pt はみ出した。本文（表）を変えずに収めるため、枠の側で幅を広げた。10pt なら 14 頁、12pt で 18 頁（はみ出しは 2〜3pt が 2 件で、旧版にも 1 件あった程度）→ 査読で読みやすい 12pt を採った。36 頁未満の規程に十分。
- **`build.sh`**: Springer の zip の取得とハッシュの検査を消した。代わりに、Tectonic の bundle から取る `elsarticle.cls`（"elsarticle 2020/11/20, 3.3"）と `elsarticle-harv.bst` の版の行を照合し、頁数が 35 を超えたら止める。変異で 3 つとも止まることを確かめた（頁の上限 10・クラスの版 3.4・bst を num）。`bash paper/build.sh` exit 0（18 頁）・`bash run.sh` exit 0（`results/` は変わらない）。
- **README**: 組版の段落・配置の表・ライセンスの表（Springer の行を消した）を直した。
- Tectonic 0.17.0 は scratchpad に取り直した（`tectonic-0.17.0-x86_64-pc-windows-msvc.zip`・SHA-256 `f61ce51f…`）。
- **未確認**: 投稿画面に推薦の査読者の欄があるか（S9 で研究者が確かめる・判断 13）。

## 判断 15: S2-B —— 誤読の実例の検索の手順（検索の前に決めた・判断 3）
- **何を「実例」と数えるか**: 公刊物（論文・プレプリント・学位論文・技術報告）の本文で、(a) 参照・助けの求めが記録されなかった単位（episode・task・session）を、解決した・自力で解いた・助けが要らなかった、と読む文、または (b) 参照の頻度の低さから助けの必要の低さ・自力での解決を推す文。分類は「実例」「近い（参照が少ないことを述べるだけで、解決や必要には触れない）」「該当なし」。
- **どこを**: (1) 前向きの引用: Alaboudi & LaToza の arXiv 2021（2105.02162）と EMSE 2023（10.1007/s10664-023-10352-5）、Li & Coblenz 2026 を引く文献を、OpenAlex（`cites:`）と Semantic Scholar の citations で全部挙げ、各文献で引用している箇所の前後を読む。(2) 語の検索: Google Scholar と OpenAlex で、下の語を 2021〜2026 年の範囲で検索し、各問いの上位 30 件の題と抄録を見る。
- **語**: "debugging" と組み合わせて "without consulting" / "without seeking help" / "rarely consult" / "without external help" / "resolved on their own" / "self-resolved" / "unaided"。および "help seeking" "programming" "did not ask for help" "did not need help"。
- **どこまで**: 有料の本文は使わない（無料の版を OpenAlex と Google Scholar の「すべての版」で探す）。無料の本文が無ければ抄録だけを読んだと記録する。締切 25 分。
- **記録**: 候補ごとに、書誌・DOI か URL・読んだ版（本文か抄録か）・該当する文の逐語（25 語以内）・分類。0 件も結果として本文に書く（判断 3）。
- **裏取り**: 「実例」「近い」に分類された候補は、メインが本文を開いて逐語を確かめてから使う。

## 判断 16: S2・S3 —— 調べもの 3 本の結果と、補助解析を追加だけで足した（2026-11-21）
- **S2**: 3 本の戻りは `survey-s2.md`（要約。使う前にメインが一次で確かめる）。B は実例 0・近い 0（浅い検索・本文は 3 本だけ）。H は「k と分布を主、補助は CR2 と Bell–McCaffrey の t 区間」を推奨。F は 5 系統の候補と査読者の候補 8 人（抄録のみ）。
- **H の採否**: CR2-BM を補助の区間として採った。理由: 閉じた式で決定的、クラスタの大きさが不揃いなら df が自動的に下がる、Imbens & Kolesár の 10 クラスタの不揃いな設計で被覆が最良（エージェントの引用・メインは未確認）。WCR（restricted wild cluster bootstrap）は回帰の制約つき検定を反転する必要があり、比率の平均だけの今回には重い。「役に立たない」は選ばない。D1 の区間は [5.9, 16.6]（df 6.84）で、パーセンタイル区間 [6.8, 15.7] より広い。D2 は df 9.0 で下限が 0 未満（-7.4）＝情報が乏しい。本文には「0 を含まない」を検定として書かない。
- **K**: figshare の 2 つの項目を Chrome で一次で読んだ。どちらも "CC BY 4.0"（creativecommons.org/licenses/by/4.0 へのリンク）で、どちらも "This item is shared privately"。→ 帰属を示せば派生表を再配布できる。私的なリンクは消えうるので、派生表をアーカイブに入れる理由が強まった。派生表の実装は S9 の前（Zenodo の版を作るとき）に。
- **S3**（論文用リポジトリ `revision-jss` の `c3e1133`・未 push）:
  - `config.json` に `post_review_additions` を、`analysis/post_review.py` を新しく足した。結果は `results` の `post_review` の下にだけ出る。
  - 凍結の守り: `analyze.py` が、凍結した config の部分（`_comment` と新しい節を除く）と、提出版の `metrics.json`（タグ `submission-2026-09-29`・`f13cd9e4…`）の SHA-256 を定数で持つ。`post_review` 以外が 1 つでも違えば結果を書かない。self-test は陰性対照つき（凍結の項目を変えると検出・違う metrics は拒否・新しい節と `_comment` は対象外）。
  - コードの外からも確かめた: 新しい `metrics.json` から `post_review` を除くと、タグの版と完全に一致。`report.md` は追記だけ（削除 0 行）。
  - `bash run.sh` は先に拒否され（期待どおり）、`ALLOW_RESULT_CHANGE=1` で 1 回だけ通した。`paper/build.sh` exit 0。
  - self-test で 1 件落ちた: 時間重みの検査の前提（合成の episode が全部同じ長さ）が誤り。合成データの最初の episode は中断をはさんで 60 秒。期待値を (59×30+60)/(99×30+60) に直した（コードは正しかった）。
  - NOTES.md に Deviation 8 を書いた。
- **主な値**（strict|DF1）:
  - DF3 を除くと 2.6pp [0.0, 7.3]、DF3 と DF5 を除くと 1.3pp [0.0, 5.0]。round 1 の参考値と一致。
  - DF3 を解決に数え直すと、数え直した後の R0′ が 76.4%・numerator effect 2.2pp。
  - k = 7/11（1 人に集中する最大の割合 0.2）。
  - DF3 は 12 件・うち 4 件がセッションの最後の episode。参照なしの DF3 は 8 件・うち 2 件が最後（5 人・6 セッション）。
  - 時間で重みをつけると numerator effect 19.1pp。未解決で参照なしの episode の中央値は 290.5 秒、解決で参照なしは 108 秒。
  - D2 で研究期間の終わり（P4TA）を除くと table5 は 6.2pp・k=2、table+text は 0.0pp・k=1。P1TA を除いた table+text は 5.9pp。
- **研究者に聞くこと**（S4 の前に）: B の 2 回目（やり残しの本文を開く・Google Scholar と教育系）を回すか。

## 判断 17: S4 —— 名前は「内容名＋新しい記号」・概念の語は unaided resolution（2026-11-21・研究者の選択・私の推奨）
- **決定**: unconsulted share U = (a+b)/N ／ unaided-resolution share A = a/N ／ unaided-resolution rate among resolved units A|R = a/S。差は unresolved-unconsulted share（U − A ＝ b/N）・conditioning difference（U − A|R）・denominator difference（A − A|R。分解にだけ使う）。"effect" は使わない。概念は "unaided resolution" に統一する（self-resolution・resolved without help の揺れを消す）。`metrics.json` のキー（R0・R0_prime・R1・numerator_effect など）は外部の契約なので変えない。
- **理由**: R2 の指摘 3 点（4 つのセルに 6 つの名前・R0′ のプライムが R0 の変種に見える・effect が因果を連想させる）をすべて解く。記号が中身を表す（U = unconsulted、A = unaided）。
- **却下案**: 内容名＋記号は今のまま（プライムの誤解が残る）／記号を主にして effect だけ替える。
- **実施**（`revision-jss` の 2 つ目のコミット・未 push）: マクロ `\Rz`・`\Rzp`・`\Ro` の出力を U・A・A_{|R} に替えた。本文の語を使い捨てのスクリプトで一括で置き換え、残った 5 か所は手で直した。表の列見出しは記号の差にして、表の幅を保った。
- **置き換えの途中で起きたこと**:
  - "self-resolution" の一括置き換えで、Data availability の GitHub の URL（`self-resolution-measure`）まで書き換わった → 戻した。
  - sed で表の見出しを直そうとしてバックスラッシュが落ち、`Rz{}` が文字のまま組まれた。ビルドは通ってしまう → Edit で直し、`[^\]R[zo]p?{}` を grep して 0 件を確かめた。
- **残り**（S5）: "the effect"・"two effects" などの一般語の effect（約 10 か所）と、文の流れの手直し。題は S6。

## 判断 18: S5 の前半 —— 内側の節を書き直した（2026-11-21）
- **B の扱い**: 2 回の検索（`survey-s2.md`）で、実例は 0 件。判断 3 のとおり「予防的な報告の推奨」に絞り、検索の範囲と 0 件を本文（§2.5）に書く（S5 の後半）。Marwan et al. 2020 の逐語は、§2.2 の「頼まないことは要らないことではない」の支えに使える（使う前に PDF で確かめる）。
- **論文用リポジトリ**（`revision-jss`・未 push）:
  - `b80b2d8`: P1TA を未解決に数え直す解析を足した（D2 の table のみの値が 11.8 → 17.6、table+text は 5.9 のまま）。§5 に「最初の版の後に足した解析」の節（打ち切り・区間 [A, U]・k と CR2・時間・P1TA）を置いた。§4 に配信者の選択的なコーディングと P1TA の逐語を入れた（どちらも arXiv v3 の PDF から一次で取った）。κ を 0.75・0.84 にした。引用を 3 件足した（Imbens & Kolesár 2016・MacKinnon, Nielsen & Webb 2023・Manski 2003。書誌は OpenAlex、前の 2 件は本文の該当文を PDF で確かめた）。
  - `19400ba`: RQ2 に時間で重みをつけた版を足し、差を指す "effect" を消した。
  - `c84c86b`: 提言を受け手別（設計する人／再利用する人／道具を評価する人）にし、最小の報告として 2×2 表（表 6）を置いた。§7.1 と結論を「区間 [A, U] の幅」の読みに直した。§7.2 の一般論に「未解決が少ない場合」を足した。§7.4 の言い切りを 4 定義の範囲に絞った。RQ4 の D2 の "undercounts" と §8 の食い違いを解いた。§8 に打ち切りの仮定・k・CR2・二次データの倫理の節を足した。段落の題の末尾の「..」（elsarticle が自分でピリオドを打つ）を 24 か所直した。
  - 新しい質的な文はすべて `make_results.py` の検査にし、変異で止まることを確かめた（6 本）。既存の変異 2 本が新しい検査で先に止まった → `post_results` を `claims` の後に回し、重複する検査を 1 つ消した。
  - 22 頁（36 頁未満）。
- ⚠️ **約束を書いたが、まだ実装していないもの**: §8 の倫理の節に「再現一式の派生表は URL・名前を含まない」と書いた → K の派生表（`results/d1_episodes.csv`）を S9 の前に必ず実装する。実装しないなら、この文を消す。

## 判断 19: S5 の後半 —— 序論・§2・§5.5・RQ4・要旨・声明・K を直した（2026-11-21）
- **研究者に聞いたこと**（AskUserQuestion）: 照会の返事はまだ無い ／ 解析のコードは研究者は読んでいない（出力だけを見た）→ §5.5 にそのとおり書いた ／ モデルの版を記録から抜き出してよい。
- **モデルの版の出どころ**: 論文用リポジトリと GSE の commit の Co-Authored-By の行（一次）。2026-09-06 の探索 = Claude Opus 5、09-28・29 と 11 月 = Opus 5.5、11 月の調べものの委譲 = Sonnet 5.5（この機械のセッション記録の `model` で確かめた）。9 月の委譲の Sonnet の版は記録が無い → 本文に「記録していない」と書いた。各インスタンスへの指示文は一式として保存していない → そう書き、渡したものを文で説明した。
- **一次で確かめた文献**（PDF を pypdf・書誌は Crossref）: Marwan, Dombe & Price 2020（著者の PDF・抄録の逐語）・Ko, DeLine & Venolia 2007（著者の PDF・抄録の逐語）・Parnin & Rugaber 2011（SQJ 版・著者のページ・抄録の逐語）。`docs/references.md` に [P635]〜[P640]（前半で足した Imbens & Kolesár・MacKinnon ほか・Manski も含める）を登録。`check_citations.py` は違反なし。
- **journal 版の 8 つの報告値**: NSF PAR の PDF（SHA-256 `38fe7001…`・判断 12 と同じ）から抽出した本文で、`config.json` の逐語 7 本と活動数 2135 がすべて見つかった（"Consulting resources occurred in all committed…" は抽出で語がつながっていたが同じ文）。long = "23 episodes" は本文にある・short は "bottom quartile" とだけあり件数が無い → 22 は 89 の 4 分の 1 の切り捨てと本文に書いた。⚠️ 研究者はまだ PDF と照合していない（本文にそう書いた。S7 で照合すれば書き換える）。
- **論文用リポジトリ**（`revision-jss`・未 push）:
  - `8109d1f`: 序論（予防の主張に絞る・貢献の並べ替え・分解は恒等式）、§2（中断と後回し・Marwan・部分識別・2 回目の検索の範囲と 0 件）、§5.5（版・日付・渡したもの・再現率は不明・コードは読んでいない）、RQ4（22 の根拠・報告値どうしの算術 22/89 = 24.7%・照会）、RQ2 の範囲を D1 と D2 で分けた、合わせ込みの的と検査の区別、要旨（249 語・符号を「上がる」に）、Highlights、声明を Elsevier の形に（生成 AI の申告を最後に）。`check_frontmatter.py`（要旨の語数・キーワード・Highlights の字数・申告の位置・禁止する文言・変異 8 本）を `build.sh` の Step 2 にした。`make_results.py` に算術の検査と変異 2 本。
  - `5372cdb`: K を実装した。`analysis/derived.py` → `results/d1_episodes.csv`（匿名の開発者とセッションの番号・符号・長さ。名前・URL・元のセッション ID・時刻なし）。`analyze.py` は 8 つのセルと活動数を表から戻せないと書かない。自己検査に破損 2 本と漏れの検査。metrics.json と report.md はバイト同一（`run.sh` を `ALLOW_RESULT_CHANGE=1` で 1 回・CSV が無かったため。その後の素の `run.sh` は identical）。awk で CSV から別に数えても 70/89・60/73・60/89・DF3 12（最後 4）。NOTES の Deviation 9・DATA.md の帰属。再現一式の文言（config の `_comment`・docstring・"drift"・"other project"・L10・κ）。
  - `8129e92`: 入れ子の定義の注・小数 2 桁の脚注。
- **生成 AI の申告**: 「使った後に著者が読み、必要に応じて直した」の文は、S7 の通読の後にだけ足す（いまは書いていない）。

## 判断 20: S6 —— 題は案 A（2026-11-21・研究者の選択・私の推奨）
- "When “no help” is not “solved”: unconsulted shares and unaided resolution in two public debugging datasets"（`6d0d3b4`）。本文の 2 つの名前がそのまま入り、self-resolution の語が消える。README の見出しも替えた。README の引用の bibtex は旧い版（タグ）の題のまま → S9 で新しい版の DOI と一緒に替える。
- Highlights 5 本（`paper/highlights.tex`・各 85 字以内）とキーワード 6 つ（変えていない）は S7 で研究者が見る。

## 判断 21: S7 —— 研究者の通読と修正案をすべて採る（2026-11-21）
- **研究者の通読**: 済み。全体の修正案（`JSS_draft_comprehensive_revision_plan_20261121.md`・研究者のローカル・外の査読ではない）を受けた。主旨は、測定の妥当性・観測終了・再現性の研究として立て直すこと。半分ほどは原稿に既にある。
- **研究者の決定**（AskUserQuestion・私の推奨は (1)+(2)+数え直しだった）: 全部を採る。
  - (1) 誤りに近い所: RQ1 の "does not establish the sign" を直す（U−A は定義から 0 以上。区間が 0 を下回るのは近似の性質）／ DF3 の寄与を同じ分母の 8/89 で示し、2/77 は対象の集合が変わった値と書く ／ §3.4 の冒頭に「unaided resolution は観測した単位の中で、記録された相談なしに解決したことの略記」。
  - (2) 小さい追加: b/(a+b)（既存の数からの割り算・NOTES に記録）／ RQ4 の表を「構造の確かめ」と「相談の統計の再現」に分ける ／ 2×2 表を §6.1 に移す ／ LODO（D1・post_review・Deviation 10）。
  - (3) 別の実装で 2×2 表を数え直す（`analysis/` を見せない別インスタンス・本文の記述と codebook だけから）／ 文献探索をやり直し、1 件ごとの判定の表を付録にする（いまは件数しか残っていない）。
  - 要旨: D1 の bootstrap 区間を外し、読み手（設計する人・再利用する人・道具を評価する人）を足す。
  - 一般化: §7 に段落を足す（U−A = u·q。移るのは仕組みで、大きさではない）。他の分野の例の文献もサブエージェントで探す。
- **採らないもの**: 題と RQ の全面的な書き換え（題は判断 20 で決めた。RQ は文言を observed 寄りに直すだけ）。
- **生成 AI の申告**: 通読が済んだので「読んで直した」の文を足してよいかは、改訂の後に改めて研究者に聞く（まだ聞いていない）。

## 判断 22: 判断 21 の実施（2026-11-21）
- **論文用リポジトリ** `a55b9bb`（未 push）:
  - §3.1: r_i・c_i が何を記録しているかを書いた（観測した単位の中での解決・記録された相談）。b/(a+b) も定義した。§3.4 の冒頭に unaided resolution の但し書き。
  - RQ1:
    - b/(a+b) = 14.3%（D2 は 18.2・11.1）。
    - DF3 の寄与 9.0pp（8/89）。DF3 を除いた 2.6 は「残った 77 件の集合の値」と書いた。
    - LODO: D1 は 10.3〜12.5pp で、8 定義すべて正のまま。D2 table+text は 0.0〜7.1 で、一人を除くと消える。
    - D2 の CR2 が 0 を下回るのは近似の性質と書き直した。
  - 2×2 表を RQ1 に移した。§7.3 に単位ごとの表の列を書いた。
  - RQ4 の表を構造（1/2）と相談（strict 3/6・他 2/6）に分けた。+OT2 系は「最も近いが一致の保証はない」と書いた。
  - §7 に「Beyond these two datasets」を足した（u·q・Hellas 2023 の 1.3%・Shihab 2025 の 30 分の制限）。§8 と結論にも反映。
  - 要旨は 249 語。区間を外し、読み手を足した。
  - 検査: make_results に検査 4 本（LODO 2・活動数が 1 違う・b の範囲）と変異 3 本。analyze.py の自己検査に LODO 2 本。NOTES の Deviations 10・11。`run.sh` は `ALLOW_RESULT_CHANGE=1` で 1 回（lodo の追加だけ。ほかの欄と CSV は不変を確かめた）→ 素の run は identical。26 頁。
- **別の実装での数え直し**（Sonnet 5.5・`analysis/` を見せず、本文 §4.1・codebook・rowData だけ）:
  - 一致: 8 つの 2×2・終了コード・開発者ごとの内訳・由来・長さの中央値（ブロックの和）・活動数 2136。
  - 食い違い: 「DF3 がセッションの最後」の件数（3/1 対 4/2）だけ。数え直しはファイルの順で並べていた。Video8 はファイルの順が時刻順でない → いまの解析（時刻の順）が本文の定義どおり。
  - `audit/independent-recount/` に台本・出力・比較を入れた。§5.5 と §8 には「同じ種類の道具による 2 つ目の実装であり、人による数え直しではない」と書いた。
- **一般化の文献**（Sonnet・本文の逐語はメインが抽出テキストで確かめた）: Hellas 2023 は既に引いている [P435]。Shihab ほか 2025 ICER を [P641] として登録した（書誌は Crossref。arXiv 版と題が 1 語違う）。IDE のテレメトリの例は確かめられず、使わなかった。
- **残り**: 文献検索のやり直し（付録）はサブエージェントの戻り待ち。生成 AI の申告の「読んで直した」は改訂の後に研究者に聞く。

## 判断 23: 文献検索の記録付きのやり直し —— 前半だけ済んだ（2026-11-21）
- Sonnet 5.5 の汎用エージェント・約 13 分。記録は scratchpad の `search-log/` にある（`citing-works.tsv`・`keyword-queries.tsv`・README・本文の txt）。scratchpad は消えうる → 次のセッションの最初に論文用リポジトリへ移す。
- **A（前向きの引用）**: 一意の 70 件（生の記録 121 件・D1 を引くもの 64・D2 を引くもの 6。D2 そのものを含む）。本文を読めたのが 43 件（NONE 41・NEAR 2・INSTANCE 0）、読めなかったのが 27 件（引用文脈だけで判定。該当なし）。
  - 1 回目の 58 件との差は説明できていない（S2 だけ 12・OpenAlex だけ 16・両方 42）。
  - NEAR 2 件は、メインが抽出テキストで逐語を確かめた:
    - C04 "Time spent checking external resources was limited (<5%)…"（arXiv 2512.22418）
    - C29 "consult (2.3% of total time) were not major bottlenecks…"（arXiv 2510.08834）
    - どちらも時間の配分の話で、助けが要らなかったとは推していない → 実例ではない。
- **B（キーワード）**: 未了。OpenAlex の 1 日の上限（429・UTC 0 時に戻る）。代わりの S2 の語句検索は 7 問・2 件で、どちらも無関係。→ 日本時間 9 時以降に OpenAlex でやり直す。
- §2.5 と付録はまだ書き換えていない。B が済んでから、二つの回の数（58/36 と 70/43）を両方書き、記録した回を付録にする。
