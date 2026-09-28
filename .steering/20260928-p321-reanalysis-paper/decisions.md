# 重要な設計判断

★ 2026-09-28 の grill（研究者との対話）で確定した。前提は判断 16
（`.steering/20260927-ime-observation-paper-eval-design/decisions.md`）。

## 判断 1: 投稿先 = EASE 2027 Short Papers and Emerging Results

> ⚠️ **判断 8・9 で改めた**（EASE は取り下げ・現行は EMSE の研究論文）。

- **判断日時**: 2026-09-28
- **背景**: 判断 16 で暫定にしていた投稿先を研究者が確定する。
- **選択肢**:
  - A: EASE 2027 Short（6 頁・abstract 2027-02-22 / paper 2027-03-01 AoE・double-anonymous）
  - B: ICPC 2027 RENE（paper 2026-12-18・新データ必須・逐語 "lack of statistical power (small samples) is not a good submission"）
  - C: ICPC 2027 ERA（2026-11-26・4+1 頁）
- **採用**: A
- **理由**: 募集文が「指標の再評価」「新しい文脈での確認」を名指ししている（判断 16 の逐語）。
  BRM（12 月）・CHI 2027 Posters（2027-01-21）の後なので IME 論文と締切が衝突しない。
- **トレードオフ**: 6 頁に収める。B の「新データへの適用」という枠組みは使わない。
- **影響範囲**: 外枠（6 頁）、匿名化（GSE を引くときは三人称）、スケジュール。
- ⚠️ **締切の値は 2026-09-28 に判断 16 で一次確認したもの。投稿前に CFP を開き直す。**
- **見直しタイミング**: CFP が変わった場合、または解析の結果が 6 頁に収まらない場合（→ B へ）。

## 判断 2: 主系列 = 正式版 [P433] のコーディング、v1 は感度

> ⚠️ **判断 7 で前提が変わった**（2 つのパッケージは同じコーディング。主系列は公開されている唯一のコーディング）。

- **判断日時**: 2026-09-28
- **背景**: 正式版 [P433] は数え直している（参照 21% → 33%・活動 2137 → 2135）。どちらで数えるかで主張の値が動く。
- **選択肢**:
  - A: 正式版を主・v1 を感度
  - B: v1 を主・正式版を感度
  - C: 主従なしで並記
- **採用**: A
- **理由**: 査読者が引くのは正式版なので、旧版を主にすると理由を問われる。
- **条件分岐（先に固定する）**:
  - 正式版パッケージが**取得でき**、かつ [P433] の既報値で**検算が通る** → 正式版が主系列
  - 取得できない、または検算が通らない → **v1 を主系列**にし、その理由（経路ごとの失敗、または合わない項目）を論文に書く
- ★ **どちらの場合も、論文には数えた版を必ず書く**（handoff §2-2）。
- **影響範囲**: 実験の `config.yaml`（入力の版）、外枠の数値、`references.md` の引き方。
- **見直しタイミング**: 正式版パッケージが v1 と同じ生データ（数え直しが集計側だけ）と判明した場合は、差分を「集計手続きの違い」として書き直す。

## 判断 3: このタスクの完了範囲 = 解析 ＋ 外枠まで

- **判断日時**: 2026-09-28
- **選択肢**: A: 解析 ＋ 外枠（handoff §2 の 1–5） / B: 解析まで（1–3） / C: 原稿完成まで
- **採用**: A
- **理由**: 外枠（主張 ↔ 根拠の対応表）まで作れば、執筆を別タスクに分けても主張が揮発しない。
- **影響範囲**: `requirement.md` の受け入れ条件。原稿執筆は別の `.steering/` タスクで行う。

## 判断 4: arXiv プレプリントは、投稿先の匿名性規程を一次で確認してから決める

> ⚠️ **判断 10 で閉じた**（投稿と同時に出す）。下の追記の EASE の規程は、投稿先を EMSE に改めたので参考情報。

- **判断日時**: 2026-09-28
- **選択肢**: A: 規程を確認してから決める / B: 出さない / C: 投稿前に出す
- **採用**: A
- **理由**: EASE は double-anonymous。プレプリントの可否・宣伝の制限を未確認のまま決めない。
- **影響範囲**: 投稿スケジュール。⚠️ 確認は投稿先の規程ページ（一次）で行う。
- **見直しタイミング**: 規程を確認したら、この判断に結果を追記する。

## 判断 5: 解析手続きは、正式版の結果を見る前に `config.yaml` に凍結してコミットする

- **判断日時**: 2026-09-28
- **背景**: 本研究は探索的（事前登録なし）。ただし正式版の数え直しで値が動いたとき、定義を後から選び直す余地があると主張が弱くなる。
- **選択肢**:
  - A: 正式版パッケージを開いて**検算だけ**を通し、R₀ / R₁ / R₀′ を計算する**前に**定義（episode の畳み方・fix の定義・参照の定義・感度の軸・区間の手続き・seed）を `config.yaml` に書いてコミットする
  - B: 結果を見ながら定義を詰める
- **採用**: A
- **理由**: 「分子の効果が約 11pt」という主張が、定義の選び直しで作られたものではないことを git 履歴で示せる。
- ★ 実体は論文用リポジトリの `config.json`（本判断の文面の `config.yaml` は `config.json` と読む）。
- ★ **検算（既報値との突き合わせ）は凍結前に行ってよい**（入力の対応づけを確かめる手続きで、主張の値を見ない）。
- ⚠️ 凍結後に定義を変えた場合は、`notes.md` に逸脱として記録し、変更前の値も併記する。
- **影響範囲**: 実験のコミット順（config → 解析本体）。

## 判断 6: 論文用の別リポジトリ `mikotomiura/self-resolution-measure`（private）を作り、解析一式をそこに置く

- **判断日時**: 2026-09-28（研究者の提起「論文用の新しいリポジトリを作ったほうがよさげ？」を受けて）
- **選択肢**:
  - A: 今作る・private（解析コード・[P434] 転記 CSV・設定・結果・原稿・README）
  - B: 今は GSE の `experiments/` で進め、投稿前に切り出す
  - C: 作らない
- **採用**: A（名前は研究者が `self-resolution-measure` を選んだ）
- **理由**: (1) EASE は double-anonymous で、査読者に渡す再現一式を匿名にする必要がある。GSE リポジトリには著者と GSE の文脈が至る所にある。
  (2) この論文は GSE のコードもデータも使わない（handoff §4）ので依存が無い。(3) IME 論文の判断 5（評価一式を別リポジトリで公開）と同じ運用。(4) 後から切り出すと二重管理になる。
- **トレードオフ**: GSE の hooks・CI・Skill は新リポジトリでは自動で効かない。→ 規律（seed 固定・入力の SHA-256 照合・検算ゲートの自己検査）は `run.sh` の中に持たせる。
- **置き場所の分担**:
  - 新リポジトリ（`C:/self-resolution-measure`）: 解析コード・転記 CSV・設定・結果・原稿・README（データ取得手順と SHA-256）。⚠️ **生データは置かない**（`raw/` を `.gitignore`）。
  - GSE リポジトリ: 作業記録（本 `.steering/`）・`docs/references.md`・`docs/glossary.md`。
- **影響範囲**: `requirement.md` の実験の置き場所（`experiments/20260928-…` → 新リポジトリ）。⚠️ ライセンス（コード / データ）は未決 —— 公開前に決める（IME 論文の判断 15 = コード Apache-2.0 ／ データ・文書 CC BY 4.0 が先例）。
- **見直しタイミング**: 投稿時に匿名ミラー（例: anonymous.4open.science）の作り方を決めるとき。

## 判断 7: 正式版パッケージは v1 とバイト同一だった → 主系列は「公開されている唯一のコーディング」、正式版の報告値は項目ごとの再現表で扱う

> ⚠️ 下の「単一の規則では再現できない」は、末尾の「判断 7 の追記」で**検討した 4 定義の範囲に限定した**。

- **判断日時**: 2026-09-28
- **一次で確かめたこと**:
  - 正式版 [P433] のパッケージ `Replication_Debugging.zip`（figshare file 30646101・218,759 B・SHA-256 `523705d8f02f59bfe952328598f03ee28f1d2c8f2a5e3a26caf2d251c8108fe4`・2021-09-04 更新・CC BY 4.0）の中身:
    `rowData.json`（SHA-256 `497df0b4…` ＝ **v1 と同一**）・`codingBook.pdf`（`0a1cc4cb…` ＝ **v1 の `codingBookFSE2021.pdf` と同一**）・`Observe-devOnlineDataSetLink.txt`（同一）・`interviews .pdf`（**新規**・Study 2 の面接）。
  - → ★ **正式版の数え直し（参照 21% → 33%・活動 2137 → 2135）のデータはパッケージに入っていない。**
  - ★ [P433] の Consult の定義は逐語 "Browse online documents, forms, issue tracker, and any type of resources outside the development environment"（Table 3）。コードブックの `Other` には **OT2: Issue tracker** がある。
  - ★ 公開データで [P433] の報告値を定義ごとに当てた（scratch の探索・`analyze_p321.py` の関数を流用）:

    | [P433] の報告値 | strict（`Seeking information`） | ＋U コード | ＋OT2（issue tracker） | ＋OT2＋U |
    |---|---|---|---|---|
    | 全体 "33%" | 19/89 = 21.3% | 20/89 = 22.5% | 27/89 = 30.3% | 28/89 = 31.5% |
    | committed "all" | 7/10 ✗ | 7/10 ✗ | **10/10 ✓** | **10/10 ✓** |
    | fresh "15%" | **12/79 = 15.2% ✓** | 13/79 = 16.5% | 17/79 = 21.5% ✗ | 18/79 = 22.8% ✗ |
    | 開発者 "91%" | **10/11 ✓** | **10/11 ✓** | 11/11 ✗ | 11/11 ✗ |
    | 短い episode "none" | 0/22 ✓ | 0/22 ✓ | 0/22 ✓ | 0/22 ✓ |
    | 長い episode "74%" | 11/23 = 47.8% | 12/23 = 52.2% | 15/23 = 65.2% | 16/23 = 69.6% |

    ★ 「23 episode で総時間の 79%」は公開データでも **79.5%** で一致（episode の畳み方は正式版とも整合）。
  - → ⚠️★★★ **[P433] の Consult の報告値は、公開データに対する単一の規則では再現できない**（「committed は全部」は issue tracker を含めないと出ず、「fresh 15%」「91%」は含めると出ない）。
- **採用**:
  1. **主系列 = 公開されている唯一のコーディング（両パッケージ共通の `rowData.json`）× strict の参照定義**。検算は v1 の既報値 12 項目（2026-09-06 に緑）。★ 判断 2 の分岐「検算が通らない → v1 を主系列にし、理由を書く」に当たる。
  2. **論文には「どちらのパッケージも同じデータ」「正式版の Consult の報告値は単一の規則で再現できない」を項目ごとの再現表で書く。**（⚠️ → 末尾の追記で「検討した 4 定義のいずれでも同時には再現できない」に限定した。論文にはそちらを書く） 引用は [P433]（正式版）、データはそのパッケージ（v1 と同一であることを明記）。
  3. ★ **参照の定義を感度の軸に加える**: strict ／ ＋U ／ ＋OT2 ／ ＋OT2＋U。探索では分子の効果が **+11.2pt（strict・＋U）〜 +9.0pt（＋OT2・＋OT2＋U）**。
- ⚠️ **開示（判断 5 との関係）**: ＋OT2 の R₀ / R₀′ は、[P433] の数え方を**特定する途中で見てしまった**（凍結前）。★ 主系列（strict）は 2026-09-06 に Table 4/5 の独立 3 統計で対応づけを固定済みで、**今回の値を見て選び直していない**。→ 凍結する `config` にこの経緯を書き、感度の軸は 4 定義すべてを報告する（都合の良いものだけを選ばない）。
- **影響範囲**: handoff §3 の「書いてよいこと」の 2 項目目（「コーディングの版で参照率が 21% → 33% と動く」）は**そのままでは書けない** →「同じ公開データに対し、正式版の報告値は単一の規則で再現できない。issue tracker を参照に含めるかで参照率は 21% → 30% 動き、分子の効果は 11.2pt → 9.0pt 動く」に改める。`docs/references.md` [P433] の gloss（「数え直されており値が違う」）に、パッケージが同一だったことを追記する。
- **見直しタイミング**: 著者から再コーディング版のデータが公開された場合（→ 主系列を差し替えるかを再判断）。

## 判断 4 の追記: 規程を一次で確認した（2026-09-28・ブラウザで取得）

- ★ **EASE 2027 Short Papers and Emerging Results**（`https://conf.researchr.org/track/ease-2027/ease-2027-short-papers-and-emerging-results` ）:
  - 逐語 "Submissions must not exceed 6 pages, including all figures, tables, references, and appendices." → ⚠️★★★ **参考文献・付録込みで 6 頁**（本文だけで 6 頁ではない）。
  - 逐語 "Authors must comply with the SIGSOFT Open Science Policy."
  - 逐語 "EASE 2027 will employ a double-anonymous review process. Authors should not include names or affiliations in their submissions, and references to their own prior work should be written in the third person. Online supplements, replication packages, and other materials referred to in the submission should also be anonymized."
  - 日程（AoE）: abstract **2027-02-22** ／ full paper **2027-03-01** ／ 通知 2027-04-05 ／ camera-ready 2027-04-19（判断 16 の値と一致）。
  - ⚠️ 逐語 "If a submission is accepted, at least one author of the paper is required to register for the conference and present the paper."（**2027-06-15〜18・Hanoi**）。⚠️ ACM ICPS の open access で、資格によって **APC** がかかりうる。→ ★ 研究者に要確認（参加と費用）。
  - ⚠️ **プレプリントについての記載はこのページに無い。**
- ★ **SIGSOFT Open Science Policy**（`https://github.com/acmsigsoft/open-science-policies/blob/master/sigsoft-open-science-policies.md` ・DOI 10.5281/zenodo.10532792）:
  - 逐語 "We encourage [VENUE_NAME] authors to self-archive their pre- and post-prints in open and preserved repositories."
  - 査読者向け逐語 "We ask you not to actively hunt the identity of authors, especially in case they self-archived a preprint of their submission."
  - → ★ **double-anonymous とプレプリントは両立する**（規程が自己アーカイブを推奨している）。
  - 逐語 "We ask authors to provide a supporting statement on the data availability (or lack thereof) in their submitted papers in a section named Data Availability after the Conclusion section." → ★ **結論の後に Data Availability 節が要る**（6 頁に含まれる）。
  - 逐語 "GitHub, GitLab, and similar services for version control systems do not offer properly archived and preserved data." → ⚠️ **再現一式は GitHub だけでは足りない**。Zenodo / figshare / OSF 等に保存する。査読中は匿名の閲覧リンク、採択後に公開（逐語で案内される手順: `https://github.com/dgraziotin/disclose-data-dbr-first-then-opendata` ）。
- **暫定の結論**: プレプリントは規程上可能。⚠️ **いつ出すか（投稿と同時 / 投稿後 / 採択後）は研究者が決める**（判断 4 の見直しとして次の確認で聞く）。
- **影響範囲**: 判断 6（再現一式の置き場所）—— 査読用には GitHub の private リポジトリとは別に、**匿名で閲覧できるアーカイブ**（例: figshare の private link・OSF の anonymous view-only link）を用意する。外枠の頁配分は参考文献込みの 6 頁で組む。

## 判断 8: 条件「登壇なし・費用ゼロ」→ 判断 1（EASE 2027 Short）を見直す（2026-09-28）

- **背景**: 研究者の指示（逐語）「できれば登壇なし, お金かからず一切0で行きたい.」
- **EASE 2027 が条件に合わない理由**（判断 4 追記の一次）:
  - 逐語 "If a submission is accepted, at least one author of the paper is required to register for the conference and present the paper."（登壇が必須・参加登録費がかかる・会場は Hanoi）
  - 逐語 "Depending on the authors' institutional and geographic eligibility, publication may require payment of an ACM Article Processing Charge (APC)."（APC がかかりうる）
- **方針**: ★ **購読型（非 OA）で出せば APC が無料の学術誌**を候補にする（誌には登壇が無い）。プレプリント（arXiv）は無料なので併用してよい。
- ⚠️ **候補は各誌の規程を一次で確かめてから研究者に示す**（APC の有無・非 OA での掲載料／超過頁料・短い論文の区分・再解析 / 再現論文の受付・匿名査読の方式）。
- **影響範囲**: 判断 1（投稿先）・判断 4（プレプリント）・外枠（頁数・形式）・判断 6（再現一式の匿名化の要否）。
- ⚠️ **他タスクへの波及（本タスクでは変更しない）**: IME 論文の判断 8（CHI 2027 Posters を「余裕があれば」併願）は、通常は参加登録と会場での発表を前提とする → 同じ条件に当たりうる。`.steering/20260927-ime-observation-paper-eval-design/` に戻るときに見直す。

### 判断 8 の追記: 費用ゼロ・登壇なしの候補を一次で確認した（2026-09-28・実ブラウザ）

- 調査は subagent（Sonnet・15 分）が先に回したが、出版社のページは curl / WebFetch では 403 で、大半が検索スニペット頼みだった → ★ **上位候補だけメインが実ブラウザで一次確認した**。
- ★ **Empirical Software Engineering（Springer・Hybrid）**:
  - 逐語 "Article Charges: The journal does not charge a submission fee or publication fee. If your article is accepted for publication, it will be published without incurring any cost to the authors. However, authors are offered the option to publish your accepted article as Open Access. … Selecting the Open Access option will require an Article Processing Fee … Please note color art is free of charge for the online publication."（`https://link.springer.com/journal/10664/submission-guidelines` ）
  - 逐語 "Both original and replicated studies can be reported, varying from controlled experiments to field studies, from data intensive to qualitative. Preference is given to studies that can be replicated or expanded upon."（`https://link.springer.com/journal/10664/aims-and-scope` ）
  - 逐語 "In most cases, the decision is made in less than three months."
  - ★ [P433] 自体が EMSE の論文。⚠️ 短い論文の区分は見当たらない（通常の研究論文として出す）。⚠️ 査読方式（single / double）は未確認。
- ★ **Information and Software Technology（Elsevier）**:
  - 逐語 "Research Papers, Short Communications and Review Articles." ／ "A research paper's maximum length is 15,000 words … For short communication, the maximum length is 2,500 words. Please note that References and appendixes are part of the submission and count against the total number of words and that figures and tables count 200 words each."（guide for authors）
  - 逐語 "Short Communications is a new section dedicated to short papers addressing new ideas, controversial opinions, 'Negative' results and much more."（⚠️ 原文の二重引用符を一重に置き換えた）
  - open access options のページ: Subscription = 逐語 "No open access publication fee." ／ OA の APC = **USD 3820**
  - 逐語（投稿の宣言）"The work described has not been published previously except in the form of a preprint, an abstract, a published lecture, academic thesis or registered report." → ★ プレプリントは可
- **除外**（subagent の報告・未再確認）: ACM TOSEM（2026 年から全面 OA で購読経路が無い）・PeerJ Computer Science（APC 必須）。
- ⚠️ 未確認のまま: JSS・IEEE TSE（超過頁料）・JSEP。
- → ★ 候補を研究者に示して選んでもらう（本追記の直後）。

## 判断 9: 投稿先 = Empirical Software Engineering の研究論文（判断 1 を改める・2026-09-28）

- **背景**: 判断 8（登壇なし・費用ゼロ）。候補は判断 8 追記で一次確認した。
- **選択肢**: A: EMSE 研究論文 ／ B: IST Short Communications（参考文献込み 2,500 語） ／ C: IST 研究論文
- **採用**: A（研究者が選んだ）
- **理由**: 逐語で費用ゼロ（"does not charge a submission fee or publication fee"）・登壇なし・"Both original and replicated studies can be reported"。★ [P433] 自体が EMSE の論文なので、その報告値の再現性を扱う場として自然。短報の語数制限（IST の 2,500 語）に縛られないので、感度分析（参照の定義 4 通り・本文ベースの追加）と EMSE の再現表を全部載せられる。
- **トレードオフ**: ⚠️ 短い論文の区分が無い → 通常の研究論文として「分量が足りない」と見られるリスク。★ 見直し: desk reject されたら B（IST 短報に圧縮）へ。
- **影響範囲**: `outline.md`（6 頁の配分 → EMSE の研究論文の構成へ）、判断 6（査読方式が double-anonymous かは未確認 → 匿名化の要否は投稿前に確認）。⚠️ **判断 1 の EASE は取り下げ**（締切 2027-03-01 の制約も消える）。

## 判断 10: arXiv へのプレプリントは投稿と同時に出す（判断 4 を閉じる・2026-09-28）

- **採用**: 投稿と同時（研究者が選んだ）。
- **根拠**: Springer Nature の方針（逐語 "Posting of preprints is not considered prior publication and will not jeopardize consideration at Springer Nature journals." —— `.steering/20260927-ime-observation-paper-eval-design/decisions.md` 判断 13 で一次確認済み）。
- ⚠️ EMSE の査読方式が double-anonymous なら、その規程とプレプリントの扱いを投稿前に一次で確認する。

## 判断 11: 論文用リポジトリのライセンス = コード Apache-2.0 ／ データ・文書 CC BY 4.0（2026-09-28）

- **採用**: IME 論文の判断 15 と同じ（研究者が選んだ）。
- **理由**: 元データ（[P321] / [P433] のパッケージ・[P434] の論文）がどちらも CC BY 4.0 なので、転記データを CC BY 4.0 で出すと整合する。⚠️ CC BY は**出典の表示と変更の明示**を求める → 転記 CSV に出典と「値は変えずに転記した」ことを書く。
- **影響範囲**: `self-resolution-measure` に `LICENSE`（Apache-2.0 の原文）と `LICENSE-DATA`（CC BY 4.0 の legalcode）を置き、README に対象範囲を書く。公開は投稿時（今は private のまま）。

### 判断 7 の追記（2026-09-28・/cross-review 後）: 主張の範囲を検証した範囲に限る

- ⚠️ Codex の指摘: 「単一の規則では再現できない」「数え直しのデータはパッケージに無い」は、**検証した範囲を超える**。
- ★ 改めた言い方: **「検討した 4 つの参照の定義のいずれでも、[P433] の Consult 関連の報告値を同時には再現できなかった。2 つのパッケージには同じコーディングしか入っておらず、[P433] の報告値の導き方は特定できなかった（同じデータを別の集計で数えた可能性は排除できない）」**。
- 反映先: `docs/references.md` [P433]・`outline.md` C5・論文用リポジトリ `DATA.md`・カード。

## 判断 12: /cross-review（1 巡目）の裁定（2026-09-28）

- **レビュー**: Codex（ラッパー経由・範囲とパスを限定）／ Claude の code-reviewer 2 本（GSE の文書・論文用リポジトリのコード）／ security-checker。⚠️ cross-reviewer エージェントは内部で code-reviewer を起動する＝入れ子になるので使わず、メインから 4 本を並列に起動した。CRITICAL なし。
- ★ **採用した主な指摘**:
  1. ⚠️★★★ **R₀ − R₁ を「分母の効果」と呼ぶのは誤り**（Codex [P1]）。R₁ = 解決かつ参照なし ／ 解決 なので、分子も分母も変わる。★ 分解 R₀ − R₁ = (R₀ − R₀′) ＋ (R₀′ − R₁) を採り、R₀′ − R₁ を「分母だけの効果」、R₀ − R₁ を「条件づけの効果」と呼ぶ。★ D1（strict / DF1）: **+11.24pt ＋ (−14.78pt) = −3.54pt** ＝ 2 つは打ち消し合っていた（⚠️ 1 桁に丸めると足し算が合わない）。
     - ⚠️ **波及**: 2026-09-06 の旧実験（`notes.md` §1・§3）と判断 4、`docs/references.md` [P321]、⚠️ **ADR-024 の Context §3 と D7 の根拠文**（「分母より分子のほうが 3 倍効く」）。→ ★ 旧実験ノート・旧判断・[P321] には訂正を追記した。⚠️ **ADR-024 本文は書き換えない規約なので触らない** —— ★ D7 の決定（分子が成果を要求するかも書く）は有効のまま。**根拠の数字（3 倍）だけが誤り**で、次の ADR 改訂で訂正する（研究者に報告する）。
  2. 主張を検証範囲に限る（Codex [P1]・判断 7 の追記）。
  3. D2 の中心の値を表だけの +11.8pt に寄せない（Codex [P2]）→ outline C1 は「表だけ +11.8pt ／ 本文の参照を含め +5.9pt」を並べる。
  4. ⚠️★★ **転記は 2 人の人ではなく、LLM（メインと独立 subagent）が行った**（security-checker HIGH）→ 論文用リポジトリの記述を事実どおりに直し、同じモデル同士の一致は誤読の共有を防げないことを限界として書いた。★ 原稿でも AI の利用を開示する（投稿規程の AI 方針は次タスクで一次確認）。
  5. 検査の空回り（code-reviewer MEDIUM）: absent 項目・Others 分岐・ブートストラップの構造・config とコードの結び付け・コミット済み結果との照合 → すべて直した（論文用リポジトリ `ae39be6`・NOTES の Deviations 1–5）。
  6. 文書の食い違い（code-reviewer HIGH 2・MEDIUM・LOW）: カードの「コーディングの版」、[V175] の要旨の向き、EASE 時代の記述、「参加者側」の限定、「新しさ」の禁止用語ほか → 直した。
- ★ 論文用リポジトリ: `ae39be6` で `bash run.sh`（許可フラグなし）exit 0・自己検査 20 項目緑（⚠️ 当初「24 項目」と書いたのは数え違い＝2 巡目の指摘）・既存の値は 1 桁も変わらず列が増えただけ。
- **却下・保留**: 方法（percentile のクラスタ・ブートストラップ）は凍結済みなので変えない → 被覆率の限界を NOTES と report に書いた。

## 判断 13: /cross-review（2 巡目）の裁定（2026-09-28）

- **範囲**: 1 巡目の修正（GSE `5f781f66`・論文用リポジトリ `ae39be6`）の境界条件。Codex（範囲限定）と Claude の code-reviewer。CRITICAL なし。
- ★ **採用（HIGH）**:
  1. 凍結した config の R₁ の文言が曖昧（「参照なしで終わった episode ／ 解決」）→ 文言を「解決かつ参照なし ／ 解決」に直し、NOTES の Deviations 6 に変更前の逐語を残した（コードは `834f16a` 以来 a/S を計算・値は不変）。
  2. `run.sh` の Step 4 が git の無い配布物（Zenodo・ZIP）で照合せずに通り、Step 2 が同梱の結果を先に上書きしていた → 新しい実行を `results/.new` に書き、同梱の `results/` と `cmp` で比べてから置き換える形に改めた。★ **git を外したコピーで変異テスト**: 同梱の結果が手つかず → exit 0 ／ 1 バイト変える → exit 1（同梱の結果は上書きされない）。
- ★ **採用（MEDIUM / LOW・Codex P2 を含む）**: 丸めた値の足し算（2 桁で書く）／ D2 の区間の説明を行ごとの ((K−k)/K)^K に（table5 11.2%・本文込み 35.2%）／ 自己検査の数え違い（24 → 実数 20、2 巡目の修正後は 23）／ `check_config` をコードの定数と結び付けた／ [P321] の「新しいのは…」・[P433] の「数え直されており」・[P434] の +11.8pt だけの記述に追記／ D2 の「未解決」は観察期間内の打ち切りを含む → 主張の文に入れる／ 用語集に N > 0・S > 0 の条件と分解の順序。
- ★ 論文用リポジトリ `098b01a`: `bash run.sh`（許可フラグなし）exit 0・自己検査 23 項目緑・既存の値は不変。
- **3 巡目は回さない**: 2 巡目の指摘は 1 巡目の修正の境界に限られ、HIGH 2 件は変異テストで効きを確かめた。

## 判断 14: ADR-024 D7 の根拠文の誤りは「次の関連 ADR で訂正」する（2026-09-28・研究者の選択）

- **背景**: 判断 12。ADR-024 の Context §3 と D7 の根拠文「分母より分子のほうが 3 倍効く」は誤り（R₀ − R₁ は分子と分母を同時に変える差。分子の効果 +11.24pt ＋ 分母だけの効果 −14.78pt ＝ −3.54pt）。D7 の決定（分子が成果を要求しているかも書く）は有効。
- **選択肢**: A: 次の関連 ADR で訂正 ／ B: 今すぐ小さな ADR（ADR-037）を起こす ／ C: ADR 一覧に注記だけ
- **採用**: A
- **理由**: ADR 本文は書き換えない規約。決定そのものは変わらないので、受領なし再開の指標を次に扱う ADR で根拠を分解の形に差し替えれば足りる。それまでは `docs/references.md` [P321]・`experiments/20260906-p321-resumption-baseline/notes.md` §9.4・本判断 12 の訂正で参照できる。
- **見直しタイミング**: 受領なし再開（`receipt_free_resumption` / `pflow_exit_without_receipt`）の指標を扱う次の ADR を書くとき。⚠️ そこで D7 の根拠を引き直すこと。

## 判断 15: IME 論文の CHI 2027 Posters への併願は取り下げる（2026-09-28・研究者の選択）

- **背景**: 判断 8（登壇なし・費用ゼロ）。IME 論文の判断 8（`.steering/20260927-ime-observation-paper-eval-design/decisions.md`）は、BRM 投稿後に「余裕があれば」CHI 2027 Posters にも出すとしていた。ポスターは通常、参加登録費と会場での発表が要る。
- **選択肢**: A: 取り下げる ／ B: 規程を一次で確かめてから ／ C: 例外として残す
- **採用**: A（IME 論文は BRM だけにする）
- **影響範囲**: ⚠️ IME 論文の判断 8・13（カバーレターでの併願の開示）は不要になる。★ **IME 論文のタスクの decisions.md は本タスクでは書き換えない**（並行セッションが作業中）→ IME 論文のタスクに戻ったときに、判断 8・13 に「判断 15（p321 タスク）で取り下げ」と追記する。

## 判断 16: [P434] の転記は研究者が PDF と目で照合する（2026-09-28・研究者の選択）

- **背景**: 転記 A・B はどちらも LLM（同じモデルの独立な 2 インスタンス）で、一致しても共通の読み違いは防げない（判断 12-4）。
- **採用**: 研究者が照合する。照合表 = `p434-human-check.md`（17 行・Table 5 の 3 行・本文の 3 文）。
- **終わったら**: 照合の日付と結果を `p434-human-check.md` の末尾に書き、論文用リポジトリの `data/li-coblenz-2026/README.md`（How the transcriptions were made）に「著者が PDF と照合した」と追記する。⚠️ 一致しない行があれば転記 A・B を直し、`run.sh` を回し直す（`ALLOW_RESULT_CHANGE=1` は結果が変わる場合だけ）。
