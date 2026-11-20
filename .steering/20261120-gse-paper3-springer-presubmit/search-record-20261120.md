# 文献検索の記録（1 回・2026-11-20）

問い: 打鍵の行動に本人ごとの系列モデルを当て、本人の後のデータで (a) 本人の単純な基準 または (b) 他人で選んだ/他人に当てた共通モデル と比べた研究はあるか。

置き場: /private/tmp/claude-501/-Users-johnd-GSE-prototype/e24df34b-7e90-4c6a-8581-d4682cf95a56/scratchpad/litsearch/
- oa/*.json と oa/urls.tsv（OpenAlex の応答と URL 逐語）
- arxiv/*.xml と arxiv/urls.tsv
- acl/anthology+abstracts.bib.gz（SHA-256 0b757e888d7d9145477a50cc78fd4b8dcc303af4147191ebb432d35b5be976a9・ファイル内の最終更新 2026-11-19）・acl/hits.json
- edmsite/p2019..p2026.html（EDM 公式の proceedings ページ）・edmsite/z_*.json（Zenodo の EDM community）
- ft/uto2020.txt・ft/pohmm.txt（全文を読んだ 2 本）
- scripts/（oa.sh, ax.sh, acl.py, show.py, abs.py）

## 1. 表

| 所 | 日 | 検索語（逐語） | 件数 | 選別（題名/抄録） | 全文 | 当たる |
|---|---|---|---|---|---|---|
| OpenAlex | 2026-11-20 | filter=title_and_abstract.search:keystroke AND ("hidden Markov" OR "Markov chain" OR "Markov model") | 46 | 46 / 8 | 2 | 0 |
| OpenAlex | 2026-11-20 | filter=title_and_abstract.search:(keystroke OR typing) AND (personalized OR individualized OR "person-specific" OR "user-specific" OR "learner-dependent") AND ("hidden Markov" OR "Markov chain" OR "sequence model" OR "sequential model") | 162 | 上位 50 / 1 | (上と重複) | 0 |
| OpenAlex | 2026-11-20 | filter=title_and_abstract.search:"writing process" AND (keystroke OR "keystroke logging") AND ("hidden Markov" OR "Markov chain" OR "Markov model") | 3 | 3 / 3 | (重複) | 0 |
| OpenAlex | 2026-11-20 | filter=title_and_abstract.search:(programming OR coding) AND keystroke AND ("hidden Markov" OR "Markov" OR "sequence model") | 10 | 10 / 1 | 0 | 0 |
| OpenAlex | 2026-11-20 | filter=title_and_abstract.search:keystroke AND (personalized OR individualized OR "person-specific" OR "user-specific" OR "individual-level") AND (Markov OR "sequence model" OR "sequential model" OR "state-space") | 2 | 2 / 2 | 0 | 0 |
| OpenAlex | 2026-11-20 | filter=title_and_abstract.search:"keystroke logging" AND (Markov OR "sequential pattern" OR "latent state" OR "hidden state") | 6 | 6 / 4 | (重複) | 0 |
| OpenAlex | 2026-11-20 | filter=title_and_abstract.search:"personalized language model" AND (typing OR keyboard OR "text entry" OR "text input") | 4 | 4 / 1 | 0 | 0 |
| OpenAlex | 2026-11-20 | search=keystroke hidden Markov model individual user sessions（自由語・関連度順） | 489 | 上位 50 / 3 | (重複) | 0 |
| arXiv API | 2026-11-20 | abs:keystroke AND abs:"hidden Markov" | 2 | 2 / 1 | 1（1607.03854） | 0 |
| arXiv API | 2026-11-20 | abs:keystroke AND (abs:personalized OR abs:individualized OR abs:"user-specific" OR abs:"person-specific") AND (abs:Markov OR abs:sequence) | 7 | 7 / 1 | 0 | 0 |
| arXiv API | 2026-11-20 | abs:"writing process" AND (abs:keystroke OR abs:typing) AND (abs:Markov OR abs:"latent state") | 0（応答は正常・totalResults=0） | 0 | 0 | 0 |
| arXiv API | 2026-11-20 | abs:typing AND abs:personalized AND (abs:"language model" OR abs:Markov) AND (abs:keyboard OR abs:"text entry") | 2 | 2 / 1 | 0 | 0 |
| arXiv API | 2026-11-20 | abs:keystroke AND abs:writing AND (abs:sequence OR abs:sequential OR abs:Markov OR abs:temporal) | 7 | 7 / 1 | 0 | 0 |
| ACL Anthology（bib 一括・139,573 件・抄録あり 90,112 件） | 2026-11-20 | 題名＋抄録に `(?i)(keystroke\|key-?stroke\|typing behaviou?r\|keystroke log)` | 50 | 50 / 4 | 0 | 0 |
| 同 | 2026-11-20 | `(?i)(keystroke\|typing behaviou?r).*?(hidden markov\|markov chain\|\bHMMs?\b)\|(hidden markov\|markov chain\|\bHMMs?\b).*?(keystroke\|typing behaviou?r)` | 1 | 1 / 1 | 0 | 0 |
| 同 | 2026-11-20 | `(?i)(keystroke\|typing\|text entry\|keyboard).*?(personali[sz]ed\|individuali[sz]ed\|user-specific\|person-specific)\|(personali[sz]ed\|individuali[sz]ed\|user-specific\|person-specific).*?(keystroke\|typing\|text entry\|keyboard)` | 7 | 7 / 3 | 0 | 0 |
| 同 | 2026-11-20 | `(?i)writing process.*?(keystroke\|keylog)\|(keystroke\|keylog).*?writing process` | 7 | 7 / 1 | 0 | 0 |
| EDM/JEDM（OpenAlex の source: S4306418235 "Educational Data Mining" 1007 件＋S7407065558 JEDM 197 件） | 2026-11-20 | filter=primary_location.source.id:S4306418235\|S7407065558,title_and_abstract.search:keystroke OR keystrokes OR "keystroke log" | 3 | 3 / 2 | 0 | 0 |
| 同 | 2026-11-20 | 同 source,title_and_abstract.search:(keystroke OR "writing process" OR typing) AND (Markov OR HMM OR sequence) | 8 | 8 / 1 | 0 | 0 |
| 同 | 2026-11-20 | 同 source,title_and_abstract.search:"hidden Markov" AND (individual OR individualized OR personalized OR "student-specific" OR "learner-specific") | 1 | 1 / 0 | 0 | 0 |
| EDM 公式 proceedings ページ（educationaldatamining.org/edm{2019..2026}/proceedings/・題名のみ） | 2026-11-20 | 題名に `(?i)keystroke\|key-stroke\|typing\|writing process\|keylog` と `(?i)markov\|\bHMM` | 打鍵系 9・Markov 系 7（8 年分） | 16 / 1 | 0 | 0 |
| Zenodo の EDM community（edm2026・edm2025・edm-2022） | 2026-11-20 | /api/communities/{c}/records?q=keystroke | 4 / 1 / 0 | 5 / 1 | 0 | 0 |

全文を読んだのは 2 本: Uto et al. 2020（UEC 機関リポジトリの版）と Monaco & Tappert（arXiv 1607.03854v7）。

## 2. 問いに当たる研究

見つからなかった（0 本）。

## 3. 近いが当たらない研究（上位 10）

1. Uto et al. 2020, IJAIED, doi:10.1007/s40593-019-00189-9 — [P270]。全文。学習者ごと・時間ごとの状態出現分布を持つ HMM を共有の GHMM と比べるが、比べは同じデータでの対数周辺尤度（log-ML）で、本人の後のデータでの比べではない（72 名が各 1 本の課題）。逐語: "For comparison, we also calculated the log-ML for each state number with GHMM."
2. Monaco & Tappert 2018, Pattern Recognition, doi:10.1016/j.patcog.2017.11.021（arXiv 1607.03854）— [V506]。全文。本人ごとの POHMM を後のセッションで評価する（"samples from the 4th session ... are used for training and sessions 5-8 ... for testing"）が、比べの相手は本人ごとの標準 HMM と他の異常検知器で、課題は本人の識別・照合。本人の単純基準や共通モデルとの比べではない。
3. Bahmani & Vertanen 2026, WiNLP, doi:10.18653/2026.winlp-main.11 — 未登録。本人の前のメッセージで適応し次のメッセージを予測する時間順の評価で、個人化 LLM を非個人化の基準・n-gram＋本人の PPM モデルと比べる（"using each user's earlier messages for adaptation as we try to predict their next message"）。最も形が近いが、対象は打った文字列（言語）で、打鍵の行動（時間・編集の系列）ではない。
4. King & Cook 2020, LREC, aclanthology.org/2020.lrec-1.299 — [V527]。本人の文章で LM を個人化し背景モデル・属性適応と比べる。対象は文章で打鍵の行動ではない。
5. Garcés-Manzanera 2026, RMAL, doi:10.1016/j.rmal.2026.100381 — [V534]。窓単位の HMM で L2 の書く過程を分ける。共通の 3 状態モデルで、本人ごとのモデルや後のデータでの比べはない。
6. Guo, Zhang, Deane & Bennett 2019, JEBS 44(5):571–596, doi:10.3102/1076998619856590 — 未登録。セミマルコフ過程で下位群の遷移を比べる。群の比べで本人ごとの予測評価はない。
7. Guo et al. 2020, JEDM, doi:10.5281/zenodo.3911796 — [V157]（登録は版違いの DOI zenodo.3911797）。セミマルコフで条件間を比べる。本人ごとの比べはない。
8. Babalola, Buddarapu, Mitros, Deane & Lynch 2026, EDM, doi:10.5281/zenodo.21039819 — 未登録。1 年分の縦断の打鍵特徴の本人内の安定性（ICC）を見る。系列モデルの本人ごとの当てはめと後のデータでの予測の比べはない（ただし「本人内のばらつきが大きい」は問いの背景に関わる）。
9. Abdelkader et al. 2026, IJACSA, doi:10.14569/ijacsa.2026.0170884 — [V318]。プログラミングの打鍵に Markov 連鎖・HMM・BiGRU で詰まりを検出。共通モデルで、本人ごとの比べはない。
10. Huh et al. 2023, IMWUT 7(2), doi:10.1145/3596236 — 未登録。スマホの打鍵の継続認証を 2 か月追い、定期的な再学習で FRR を保つ。本人ごとのモデルの経時劣化を見るが、系列モデルでなく、共通モデルや本人の単純基準との比べでもない。

## 4. 見つからなかった範囲

OpenAlex は title_and_abstract の 7 本（件数 46・162・3・10・2・6・4）と自由語 1 本（489 件）で、各々の関連度順の上位 50 件まで（50 件未満は全件）を題名で選び、近い 17 本前後の抄録を読んだ。arXiv は抄録の検索 5 本（2・7・0・2・7 件）を全件。ACL Anthology は全 139,573 件（抄録あり 90,112 件）に正規表現 4 本をかけた 65 件（重なりあり）を全件。EDM/JEDM は OpenAlex の 2 つの source（計 1,204 件）に 3 本（3・8・1 件）、公式 proceedings ページ 2019–2026 の題名、Zenodo の EDM community 3 つ。この範囲で、本人ごとの打鍵の系列モデルを本人の後のデータで本人の単純基準または共通モデルと比べた研究は見つからなかった。最も近いのは、同データの尤度で共有 HMM と比べた Uto et al. 2020 と、後のセッションで本人ごとの HMM 系を評価した Monaco & Tappert（相手は本人ごとの別モデル・課題は識別）、時間順で個人化 LM を非個人化と比べた Bahmani & Vertanen 2026（対象は文字列）である。

## 5. 取れなかった所・失敗したこと

- arXiv: 最初に http:// で叩き 301 の空応答を受けた。0 件と読まず https:// で再取得した（表の数は https の値）。
- OpenAlex の検索 2 本目（162 件）は、上位 50 件のほとんどが打鍵と無関係（推薦・医療）で、括弧の OR が意図どおりに効いていない、または "typing" の語幹の広がりの疑い。当たり外れの判定には上位 50 件のみ使った。
- OpenAlex の EDM source の総件数（filter のみ）は sort=relevance_score を付けたため取得に失敗した（エラー応答）。総件数は sources API の works_count（1007・197）で代えた。OpenAlex の EDM 会議の収録は欠けが大きく、抄録のない記録もある（例: EDM 2019 "Characterising Students' Writing Processes Using Temporal Keystroke Analysis" は抄録なし・題名のみで判定）。
- EDM 公式の proceedings ページは題名だけで、抄録は読んでいない（Zenodo に抄録のある 2025・2026 の打鍵の 5 本を除く）。EDM 2023・2024 の Zenodo community は試していない。
- Uto et al. 2020 の Springer の PDF は直接取れず（記事ページの HTML が返る）、UEC 機関リポジトリの版を読んだ。ブラウザを名乗る User-Agent での再取得は許可されず、行っていない。
- Garcés-Manzanera 2026・Guo 2019・Bahmani & Vertanen 2026・Babalola 2026 は抄録まで（全文は読んでいない）。
- Google Scholar・Web of Science・Scopus・ACM DL・IEEE Xplore は範囲外で、検索していない。
