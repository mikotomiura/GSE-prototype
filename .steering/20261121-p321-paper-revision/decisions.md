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
