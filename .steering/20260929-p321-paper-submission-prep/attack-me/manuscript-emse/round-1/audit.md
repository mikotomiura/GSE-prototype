# 意図の監査（stage: manuscript・round 1）—— 監査役の報告

対象: `C:\wt\p321-attack-me\.steering\20260929-p321-paper-submission-prep\attack-me\manuscript-emse\round-1\tmp\target\self-resolution-measure\paper\main.resolved.tex`（位置は main.tex と同じ行番号 L）
意図の資料: context-B.md、outline.md（C1–C7・書いてはいけないこと・構成）、reading-guide.md（全体）。decisions.md（原稿執筆）は Grep で一部だけ見た。

最も重いのは **A（要旨で符号が逆）** です。逐語は投稿版でも同じでした（`emse-submitted-preview.txt` 72 行目）。B・C・G がこれに続きます。

---

## 1. 意図にあって対象物に無いもの（届いていない主張・持ち帰り）

**A. 持ち帰り 2 が要旨で逆向きに書かれている（重大）**
- 要旨 L44: "In the first dataset, restricting to resolved episodes changed the measure by only \ensuremath{-}3.5 points, because a positive numerator effect and a negative denominator-only effect largely cancelled."
- 表 2 L219・L221 では R0 = 78.7、R1 = 82.2 です。解決した単位に絞ると、指標は 3.5 ポイント**上がり**ます。−3.5 は R0 − R1（条件づけの効果）の値で、「絞ったときの変化」ではありません。
- §6.2 L256 は正しく書いています: "\Ro{} = 82.2\% is close to \Rz{} = 78.7\%: the conditioning effect \Rz{}~$-$~\Ro{} is \ensuremath{-}3.5\pp"。
- 要旨には "numerator effect"・"denominator-only effect" の定義がありません。この効果が直前の 11.2 と同じ量だということも、要旨だけでは読み取れません。
- make_results.py の claims() は、この要旨の文を検査していません。

**B. 持ち帰り 2 の中心の量が凍結の後に足されたことを、本文が「名前の変更」と書いている**
- L179: "Seven later changes (names of measures, a renamed data folder, ...) are logged in the replication package; none changed a reported value."
- NOTES.md の Deviation 1 によると、凍結した config は `"denominator_effect": "R0 - R1"` でした。"denominator_only_effect = R0′ − R1 was added" とあるとおり、分母だけの効果（区間つき）とその分解は、凍結後のレビューで**新しく足された量**です。
- この量は要旨・C3・貢献 (i) の柱です。それなのに本文の開示では「名前の変更」としか読めません。

**C. 区間の限界（context-B の既知の限界）が要旨と結論に無い。D1 では区間の広さの順序が本文の説明と食い違う**
- 要旨 L44 "(developer-level bootstrap 95\% interval 6.8 to 15.7)"・結論 L371 "(developer-level bootstrap interval [6.8, 15.7])" には「不確かさの下限として読む」の限定がありません（限定は §5.2 L185 にだけあります）。
- 表 2 L223–224 では、D1 のブートストラップ区間 [6.8, 15.7] が、クラスタを無視した Wilson 区間 [6.2, 19.5] より**狭い**です。一方 §8 L362 は "Wilson intervals, which ignore clustering, are narrower than they should be for clustered data" と書いています。この順序（クラスタを考えた区間のほうが狭いこと）を本文はどこでも説明していません。そのうえで要旨と結論は、狭いほうを中心に出しています。

**D. 持ち帰り 3 は §7.3 にしか全部そろっていない**
- 要旨 L44: "We recommend reporting both measures and the unresolved, unconsulted share separately." 測度は 3 つ定義されているので、"both" がどれを指すか曖昧です。「別の名前で」「参照と解決の操作的定義」「版と規則の明記」もありません。
- 結論 L371: "reanalyses should state which coding and which rule produced each figure they reuse" では、版と規則の明記が再解析だけに狭まっています。§7.3 L328 の提言 4 は元の研究にも求めていますが、結論からは操作的定義の明記も落ちています。

**E. outline C1 の「D2 の意味の違いを主張の文に入れる」が要旨では果たされていない**
- 要旨の D2 の文 L44 "In 17 tasks from 12 developers the difference was 11.8 points from the paper's tables and 5.9 points ..." には、「観察終了までに解決も参照も記録されなかった割合」という限定がありません（前の文の "in one of them also when observation ends" だけです）。
- 結論 L371 には入っています。要旨では D1 の 11.2 のすぐ後に 11.8 が並ぶので、書いてはいけないことの「同程度」と読まれる余地があります。

**F. 想定読者の前提（公開値を自力解決の参照点として引く人がいる）を裏づける実例が無い**
- 動機は仮定の形でしか書かれていません。L44 "is easily read as"、L55 "That reading is attractive whenever published observational data are reused as a reference point"。
- §2.5 L99 は検索の小問 (1) "studies that report a ``no consultation'' share without conditioning on outcome" を挙げていますが、その結果を書いていません。書かれているのは (2) と版の違いについての結果だけです。

## 2. 対象物にあって意図に無いもの（漂流・範囲を超えた言い方）

**G. 題と本文が食い違う**
- 題 L34: "outcome-agnostic self-resolution measures in two public debugging datasets"
- §2.1 L81: "Neither study presents the share of episodes or tasks without consultation as a measure of self-resolution."（L57 も同じ趣旨）
- 題は「データの中に自力解決の指標がある」と読めますが、本文はそれを否定しています。用語も揺れています（題は self-resolution、§3.4 L132 は unaided resolution）。

**H. 「4 定義で検討した」を超えて言い切っている（outline C5 の限定・非難の調子）**
- §7.4 L335: "so a reader who reuses a reported consultation rate cannot recompute it from the published material."
- 一方 L284 は "the same data may have been aggregated differently, which we cannot rule out" と書いています。L335 は、検討した 4 定義の外まで一般化した言い方です。
- 同じ段落で "Disputes over reanalyses ..." を引いているので、論争の枠に置いたように読まれる余地もあります。

**I. 「取りこぼしうる」（C6）が「取りこぼす」と断定になっている。§8 とも食い違う**
- §6.4 L307: "the body text describes consultations in two more. A reanalysis that extracts only the tables therefore undercounts consultation"
- §8 L346: "redirecting the issue to colleagues is closer to handing it over than to consulting"・"P1's review of reports of similar issues resembles the issue-tracker activity that D1's strict definition excludes"
- §8 は P1TA を参照と数えることに疑いを出しています。それなのに §6.4 は「あと 2 つの参照」と断定しています。

**J. 書いてはいけないこと「分母だけの効果のほうが大きい」に近い書き方（境界）**
- L256: "the numerator effect (5.9\pp) is much smaller in absolute value than the denominator-only effect (\ensuremath{-}14.5\pp)"
- 同じ L256: "whereas every denominator-only interval lay below 0"
- 後者の点推定は L120 の "it is never positive" で構造上きまっています。それを条件づけの効果と対比して並べると、独立の発見のように読めます。
- make_results.py L275 のコメントも "the denominator-only effect outweighs the numerator effect" です。

**K. 貢献の置き方が outline とずれている**
- L68 の貢献 (i) は "an exact decomposition that states what each of the three measures counts" です。
- §3.3 L128 は "Equation ... is an identity about the three measures, not an additional analysis" と書いています。
- outline の「関連研究の配置」は「本論文の貢献はその定量」としています。恒等式を第一の貢献に置くと、新しさの主張に読まれる余地があります。

**L. 「すべての数値」の言い過ぎ**
- L68 の (v): "reproduces every number in this paper with one command"
- README L52 の限定は "Every analysis number in the text is taken from results.tex" です。κ・7.8 時間・0.7%／1.3%・"about 30 sources ... 13"（L99）などは run.sh の出力ではありません。

## 3. 意図どうしの矛盾・対象物の中の矛盾（README 等を含む）

**M. D1 の「未解決」の意味を、context-B と原稿が違う形で扱っている**
- context-B は「D2 の「未解決」は観察期間の終わりを含み、D1 の中止とは意味が違う」と書いています。
- しかし原稿自身の集計では、D1 の未解決かつ参照なしの 10 件のうち 8 件が DF3 です。L204: "8 ended with the developer going to return later (DF3) ... its eventual outcome is unknown"。つまり主に「後で戻る」で、中止ではありません。
- 原稿の中でも食い違いがあります。
  - §6.1 L206 は D2 について "which is not the same event as in D1" と書いています。
  - §8 L350 は両方のデータをまとめて "Unresolved therefore means ``not resolved within the observed unit'', not ``given up''" としています。
- D1 と D2 で何が違うのか（セッション内で本人が述べた区切りか、研究期間という管理上の終わりか）を、一か所で言い直す必要があります。

**N. §7.2 の一般の説明が D1 に当てはまらない**
- L318: "the conditioning effect is small whenever unresolved units are about as often unconsulted as resolved ones, however many unresolved units there are."
- D1 では q = 62.5% に対して R1 = 82.2% で（L256）、「ほぼ同じ」ではありません。D1 で効果が小さいのは、u = 16/89 が小さいからです（u × (q − R1) ≈ 0.18 × (−19.7) = −3.5）。
- 要旨と結論は、同じ現象を「打ち消し合い」で説明しています。L318 の一文を D1 の説明と読む読者には、2 つの説明が食い違って見えます。

**O. D2 の「未解決」の書き方が原典・outline・NOTES と少しずつずれている**
- L168: "In D2, ``unresolved'' therefore includes the end of observation, not only giving up." これは、4 件のどれかが「諦め」だと示唆します。
- 原典 li2026.txt 343–344 行目: "participants did not resolve the task within the study period (P4TA, S3TA, S4TB, S5TA)" とあり、4 件すべてです。outline も「4 task すべて打ち切りを含む」と書いています。
- NOTES.md L10 は "an unresolved *participant* task (P4TA) was one not resolved ``within the study period''" で、P4TA だけに限っています。原稿 L168（4 件すべて）と合いません。

**P. 転記者の書き方が README だけ違う（書いてはいけない「2 人が独立に」の境界）**
- README.md L51: "Two independent (LLM-assisted) transcriptions" は「人が LLM の助けを借りて転記した」とも読めます。
- data/li-coblenz-2026/README.md L12 は "produced with an LLM-based coding assistant ..., not by two people"、原稿 L172 も LLM による転記と書いています。

**Q. 凍結の開示に、RQ4 の扱いが書かれていない（確かめられない・問い）**
- L179 の (2) は "While identifying which rule might produce the journal version's figures for D1 (RQ4), we computed \Rz{} and \Rzp{} once ..." です。
- 表 5 の項目ごとの一致のパターンが凍結前に分かっていたかどうかは、"we disclose which" の一覧に書かれていません。渡された資料の範囲では確かめられません。

**R. 引用の照合の記述と、資料が食い違う可能性（確かめられない・問い）**
- L197: "The assistant checked every quotation in this paper against the text extracted from its source"
- 原稿は journal 版（alaboudi2023）を 5 か所で逐語引用しています（L53・L55・L77・L160 など）。context-A は、この版に無料で読める版が無いとしています。本文をどう入手したかは、この資料の範囲では確かめられません（誤りとはしません）。

**S. 小さなもの**
- README.md L3・NOTES.md L7 には、題から外した "drift" がまだ残っています。README の測度の表 L9–14 は、D2 も含めて "episodes" で定義しています。
- Data availability L391 は、D1 の figshare のリンクが非公開の共有リンクで、ブラウザでしか取れないこと（DATA.md L29・L33）に触れていません。

## 4. 読めなかった範囲・読み方の開示

- 全文を読んだもの: context-A.md、context-B.md、outline.md、reading-guide.md、main.resolved.tex、README.md、NOTES.md、DATA.md、ENV.md、config.json、results/report.md、data/li-coblenz-2026/README.md、text_external.csv。
- 一部だけ読んだもの: make_results.py（205–314 行目だけ）、analysis/*.py（import の行を Grep しただけ）、emse-submitted-preview.txt（Grep で数か所だけ）。原典 2 本は Grep で引いた箇所だけです。decisions.md（原稿執筆）は Grep の一致行だけです。
- 読んでいないもの: main.tex（resolved 版で代えた）、results.tex、refs.bib、metrics.json、provenance.txt、run.sh、build.sh、transcription_a.csv／transcription_b.csv、SEED。
- ⚠️ 一覧の外のファイルに触れました: `tmp\target` を範囲にした Grep が、一覧に無い `tmp\target\emse-upload-main.tex` に一致し、その 1 行（836 行目。main.tex の L168 と同じ文）が出力に出ました。それ以上は開いておらず、指摘の根拠にも使っていません。
- main.resolved.tex の L23–24（`\newcommand{(reproduced)}` など）は、マクロを置き換えた写しの副産物と判断し、指摘の対象にしていません。

## 5. 注入の疑い

ありません。main.resolved.tex L1 の "READ-ONLY COPY FOR REVIEW" や make_results.py のコメントは説明の文で、LLM に向けた指示ではありませんでした。
