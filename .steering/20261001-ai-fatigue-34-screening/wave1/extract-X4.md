# 抽出 X4（AF013〜AF018・Nobles 2026）

作業日 2026-10-01。判定はしない。逐語は 1〜2 文まで。「未確認」=読めていない・確かめられない、「記載なし」=読んだ範囲に無い。
キーワード検索は各件の本文テキスト（下記パス）に対する大文字小文字無視の部分一致の行数（grep -ic）。AF015 は本文が取れず抄録ページのみ。

ローカルのテキストの作業コピー（参照用）: `...\scratchpad\wave1\t\` の AF013.txt / AF014.txt / AF015.txt（HTML から変換・抄録ページのみ）/ AF016.txt・AF016c.txt / AF017.txt / AF018.txt / NOBLES.txt

---

## AF013

1. **本文の入手**: 取得済み。`C:\Users\johnd\Downloads\ai-fatigue-fulltext\AF013\b997adee_af013.txt`（同 .pdf・出版社 PDF の全文。もう 1 組 `c7bca0ee_AF013.*` は 48 バイト差の別取得で未比較）。版: IJAHSS Vol.06 Issue 08, August 2025, DOI 10.56734/ijahss.v6n8a7, 頁 53 から。URL: https://ijahss.net/assets/files/1755327497.pdf
2. **種類**: 著者の自称は「narrative literature review with thematic synthesis」（Abstract・Methodology）。系統的レビューとは自称していない。「qualitative, secondary research design」とも書く（Methodology 冒頭）。
3. **対象・問い**: AI の仕事・教育・日常への浸透による「AI fatigue」。個別の RQ 文は無く、「AI fatigue を技術ストレスと認知負荷理論の交点で捉え、digital burnout との重なりと、認知・感情・組織の駆動因を示す」と述べる（Introduction 末尾）。
4. **方法**（p.54-55 Methodology）: 情報源は Google Scholar・Scopus・ResearchGate・PubMed・IEEE Xplore＋業界・組織系プラットフォーム。検索語は「AI fatigue」「artificial intelligence burnout」「technostress」「digital burnout」「generative AI stress」。期間 2017〜2025。検索式の全文: 記載なし。検索日: 記載なし。言語: 記載なし。選別の手順・独立 2 名: 記載なし。PRISMA 図: 記載なし（「prisma」0 件）。採択数: 記載なし。質の評価: 記載なし（限界として「出版バイアス」「概念的・小規模研究が多い」とだけ書く）。
   - 内部の食い違い（読んで気づいた点）: 対象の文が「…policy briefs from 2017 to 2025 … as well as studies focused solely on technical AI, technology, or digital performance without discussion of human impact」（p.55）と続き、後半は除外基準に読めるが包含の文に連なっている（除外の語が脱落している可能性。未確認）。
5. **採択内訳**: 記載なし（採択件数も表も無い）。引用の種類は査読論文・業界報告（EY 2024 の調査・Forbes Technology Council 等）・書籍が混在（参考文献一覧）。疲労を測った研究の数: 記載なし。
6. **主要な結論**: AI fatigue は技術ストレス・認知過負荷・情動的消耗の相互作用で生じ、AI の使用量だけでなく導入の速度・不透明性・不均一さに駆動される。個人の適応の問題ではなく、デジタル変革の実践がもたらす系統的な帰結と主張する。digital burnout の「サブ条件」と位置づけ（Figure 1・p.55-56）、人間中心設計・政策上の保護・組織のウェルビーイング介入を提案、実証・縦断・部門横断研究を求める（Conclusion）。
7. **限界・要確認点**: 著者の限界は Methodology 末尾（二次研究・質と範囲に依存・出版バイアス・概念的証拠が多い）。要確認: (a) 上記の包含／除外の文の乱れ。(b) 枠組みは「lived experiences and everyday observations within workplaces and social environments」に基づくと書く（p.55）が、その観察の出どころ（一次データか）は記載なし。(c) 「AI fatigue」の定義は「constant interaction with AI-driven tools and the relentless pressure to adapt」（Introduction）で、p.55 では「hearing about them」「left behind」まで含めて症状を述べており、定義の範囲が相互作用の疲労と言説・導入への疲労の両方に及ぶ（箇所を 2 つ: Introduction の定義 / p.55 の「tired of using AI tools, irritated by endless AI content, and frustrated by both the hype and the hesitance」）。
8. **データ・抽出表・コードブックの公開**: 記載なし（「data avail」「supplement」0 件）。
9. **(A)**
   - A1 AI への帰属 vs 一般の尺度: 節を立てる（「Understanding AI Fatigue: Intersections Between AI Fatigue and Digital Burnout」p.55-56・Figure 1）。ただし区別は概念図とナラティブで、「測定」の区別ではない。測定・尺度の語（measur, instrument, questionnaire）は本文中 0 件（参考文献に Digital Burnout Scale の韓国語版の妥当性論文がある）。
   - A2 単一項目・自己報告だけの批判: 記載なし。
   - A3 自由記述・質的コーディング: 記載なし。
   - A4 疲労の測り方の内訳の表・集計: 記載なし。
10. **(B)**: 受動的疲労・警報疲れ・覚醒度・自動化バイアス: 記載なし。「complacen」1 件（p.57 前後の Brunnlechner 2025 の段落。「over-trust and complacency」を AI fatigue の一因の可能性として述べる 1 文＋その研究紹介）。他の語（passive fatigue / automation bias / alarm fatigue / alert fatigue / vigilance / over-reliance / overreliance / Parasuraman / Hancock / Matthews / Desmond）は各 0 件。自動化の人間工学の文献の引用: 記載なし。
11. **組織の水準**: 扱う（節を立てる）。「Organisational Strategies for Mitigating AI Fatigue」（参加型導入・リーダーシップ・訓練・ウェルネス監査・Sanchez-Segura et al. 2023）と「organisational misalignment」を駆動因に挙げる（Abstract・Conclusion の前の節）。理論は技術ストレス理論（Tarafdar et al. 2007, Brod 1984）と認知負荷理論（Sweller 1988）。
12. **『AI適格性評価』の次の確認・作業**: 「引用元の種類と実証性を遡って確認」→ 確かめた（一部）: 引用は査読論文・EY 調査・業界団体の記事・書籍が混在し、実証研究か否かの区分は本文に無い。「相互作用時の疲労とAI導入・言説への疲労を分けて抽出」→ 否定された（一部）: 本文は両者を分けず「AI fatigue」に束ねる（上記 7(c)）。分けた抽出は本文からは取れず、引用先の一次に降りる必要がある。
13. **『確認事項』**: 「全文の方法・採択文献を確認してレビュー形式を確定する」→ 確かめた: 形式は自称で narrative review（上記 2）。採択文献の一覧: 無く、参考文献一覧（約 60 件）のみ。
14. **ほかに確かめること（レビュー形式の確定材料）**: 検索式 記載なし／検索日 記載なし／採択数 記載なし／PRISMA 記載なし。情報源と期間（2017〜2025）と検索語（5 語）だけ記載。

---

## AF014

1. **本文の入手**: 取得済み。`...\AF014\b997adee_af014_real.txt`（出版社 PDF の全文・20 頁）。ほか `b997adee_af014.html`（出版社の記事ページ）と、今回 2026-10-01 に取り直した `live_view_20261001.html`（記事ページ）。URL: https://apcz.umk.pl/QS/article/view/70890 ／ https://apcz.umk.pl/QS/article/download/70890/46360
2. **種類**: 著者の自称は「Comprehensive Literature Review」（題名）と「literature review」（本文）。系統的とは自称していない。
3. **対象・問い**: 医療・技術・製造・事務の労働者の AI 疲労とメンタルヘルス。3 つの問い（臨床医のバーンアウトへの影響／AI 利用とウェルビーイング・キャリアの機序／組織要因と設計介入）（§1）。
4. **方法**: 検索の情報源・検索式・検索日・言語・選別の手順・PRISMA 図・質の評価: すべて記載なし（「database」「search」「prisma」「screen」「inclusion」0 件）。「Methods and Approaches in the Literature」（§3）は採択研究の設計の紹介で、選別の方法ではない。期間は「March 2025 and March 2026」（Abstract・§1）。
   - 内部の食い違い（箇所を 2 つ）: Abstract「This review summarizes 22 studies published between March 2025 and March 2026」 vs §1「synthesizes findings from 30 studies」・§3「The 30 reviewed studies」・§5「A review of all 30 studies」。参考文献は番号 20 まで（p.19-20）で、30 件には届かない（参考文献が 20 件で終わる点は未精査・一覧の番号の最後を確認したのみ）。
5. **採択内訳**: 設計の記述は §3: スコーピングレビュー（[1, 11-12]）、横断調査が最多（n=200〜683）、SEM、SHAP を使う機械学習解析、医師への半構造化面接。疲労を測った研究の数: 記載なし。測定は「validated measurement tools, including burnout scales (e.g., Maslach Burnout Inventory components), technology stress perception scales, AI anxiety inventories, and patient safety attitude questionnaires」と一括記述（§3、p.5）。
6. **主要な結論**: AI の影響は実装の質・組織の支援・設計に依存し、AI は文書作業の削減で助けることもあるが、設計不良の AI は監視・確認という新たな作業で負荷を増やす。主因は「workload intensification」と述べる。「AI fatigue is a serious and measurable problem」（Abstract）で、予防の責任は個人ではなく企業と AI 設計者にあるとする。
7. **限界・要確認点**: 著者の限界は §8.2（横断設計が多い・介入の RCT 無し・地域偏り・機序が不明・肯定的な結果が少ない・個人差・「Measurement Standardization: The field lacks standardized, validated measures of AI-specific stressors and fatigue」）。選別方法の限界は書かれていない。要確認: (a) 22 件／30 件の食い違い（上記 4）。(b) 参考文献 [3] の著者欄が「DES -1221-Pdf-Dumps, et al.」・題名は JMIR のプレプリント（doi 10.2196/preprints.85247）として載る。25% のストレス低減（パイロット）を [3] に拠る（§8.2）。(c) [12] の掲載誌が「Deleted Journal」。(d) [4] は AF017（Sapkota ら）。(e) 生成 AI を文法補助に使った旨の宣言あり（p.18）。
8. **データ公開**: 「Data Availability Statement: Not Applicable.」（p.18）。抽出表・コードブック: 記載なし。
9. **(A)**
   - A1: 段落（§2「Recent research distinguishes between AI-stressors and traditional technology…」で AI 固有のストレッサーと従来の IT の区別を述べる。尺度の区別としては §8.2 の「AI fatigue scales」の開発が必要という 1 文）。一般尺度を AI の文脈で使うことの区別そのものの議論: 記載なし。
   - A2: 1 文（§8.2「Different studies used varied instruments, making cross-study comparison difficult」。自己報告だけの測定への批判としては、横断設計の限界として述べるのみ）。単一項目への批判: 記載なし。
   - A3: 記載なし。
   - A4: 記載なし（§3 に尺度の種類の列挙が 1 段落あるが、研究ごとの表・集計は無い）。
10. **(B)**: 受動的疲労・警報疲れ・覚醒度・自動化バイアス: 記載なし。「overreliance」2 件（§4.1 の [1] からの 1 文と §5 の 1 文。いずれも誤情報・誤用のリスクの文脈）。AI が「monitoring the system」の新しい作業を生むという記述あり（Abstract・§5）だが人間工学の文献の引用は無い。他の語はすべて 0 件。
11. **組織の水準**: 扱う（節を立てる）。§4.3「Organizational Stress and Workplace Impacts」、§6 保護要因、§7「HCI-Guided Interventions」、Abstract の結論が組織責任。
12. **次の確認・作業**: 「全文の検索・採択方法」→ 確かめられない（記載なし）。「参考文献3/12/20等を個別照合」→ 確かめた（本文の参照一覧から）: [3] は著者欄が上記の通り（プレプリント）、[12] は掲載誌が「Deleted Journal」（doi 10.55606/ijmh.v4i1.5557）、[20] は Chuang, Chiang & Lin (2025) International Journal of Information Management 83:102887 と記載。外部での実在確認は未実施。「DOI文字列と巻表示の差は、それだけで誤りとしない」→ 下記 14。
13. **確認事項（巻と DOI 文字列）**: 確かめた。2026-10-01 に取り直した記事ページ（live_view_20261001.html）のメタデータは `citation_volume=55`、`citation_doi=10.12775/QS.2026.54.70890`、ページ内のリンクも `doi.org/10.12775/QS.2026.54.70890`（2 か所）。一方、PDF の第 1 頁の引用表記は「Quality in Sport. 2026;55:70890 … https://doi.org/10.12775/QS.2026.55.70890」。つまり出版社の PDF は DOI に 55、記事ページは 54 を示す（現状は食い違ったまま）。DOI の解決先の確認は未実施。
14. **ほかに確かめること**: 上記 13（掲載の巻 55、記事ページの DOI 文字列は 54 を含む、PDF は 55）。受理 2026-05-04・公開 2026-05-06（PDF 第 1 頁）。

---

## AF015

1. **本文の入手**: 入手不可（抄録のみ）。保存済みの `...\AF015\c7bca0ee_AF015.html` と、2026-10-01 に取り直した `live_20261001.html` はいずれも Springer の記事ページで、抄録・書誌・ライセンスのみ（本文なし）。PDF の URL（link.springer.com/content/pdf/10.1007/s44163-026-01855-3.pdf）は 2 通りの取り方で HTTP 404。有料の壁・ログインは使っていない。版: 早期公開（「We're sharing this article early… subject to further edits and will be replaced automatically by the final Version of Record」）。
2. **種類**: 題名・本文（抄録）とも「systematic literature review (SLR)」、記事の種別 Review。PRISMA に従うと書く。
3. **対象・問い**: AI が誘発する技術ストレス（techno-complexity / overload / insecurity / uncertainty）と、訓練・コーチング等の HRD 介入による対処（抄録）。
4. **方法**（抄録のみ）: Scopus のみ、2026 年 1 月に検索、査読誌・英語・2020〜2025 年。PRISMA に従い 125 件を特定、36 件を採択、共起語分析にも 36 件。主題統合と VOSviewer による共起語分析。検索式・独立 2 名・質の評価: 未確認（本文なし）。
5. **採択内訳**: 36 件（デザイン・疲労を測った研究の数: 未確認）。
6. **主要な結論**（抄録）: AI の使用は技術ストレスの多面的な側面を生み、従業員の心理的健康・職務満足・ワークエンゲージメントに悪影響。訓練・コーチング・スキル向上・組織の支援が、デジタル能力を高め技術不安を和らげる。
7. **限界・要確認点**: 本文を読めていないため未確認。抄録上の確認点: 単一データベース（Scopus）。受理 2026-07-21・公開 2026-07-26・受領 2026-04-15。
8. **データ公開**: 抄録ページには記載なし（本文は未確認）。
9. **(A)** A1〜A4: 未確認（抄録に記載なし）。
10. **(B)**: 抄録に記載なし。キーワード検索は抄録ページ（約 8.6 千字）に対して全語 0 件（本文は未読のため本文の有無は未確認）。
11. **組織の水準**: 扱う（抄録の主題。「organizational interventions」「supportive organizational practices」「HRM and HRD literature」）。
12. **次の確認・作業**: 「採択研究のデザインと介入エビデンスを追跡」→ 確かめられない（本文なし。抄録は「training, coaching, upskilling … improve their digital competence」と述べるが、採択研究のデザインの記述は抄録に無い）。「受理原稿と最終掲載版の更新を確認」→ 現状: 取り直したページは早期公開のまま、巻・号・頁は空（`citation_firstpage` が空）。
13. **確認事項（早期公開版）**: 確かめた（現状）: 2026-10-01 に取得したページも early publication の表示で、「Published: 26 July 2026」、巻号頁の記載なし。最終版の著者・巻号頁・内容の変更の確認は、最終版が公開されていないため未了。
14. **ほかに確かめること（最終版の書誌と早期公開版の違い）**: 最終版の巻・号・頁: 未公開（記載なし）。早期公開版と最終版の違い: 分からない（最終版が未公開）。保存版（2026-10-01 14:05 前後）と取り直し版は大きさがほぼ同じ（238,932 / 238,896 バイト）で、抄録の語に差は見ていない（全文の差分比較は未実施）。

---

## AF016

1. **本文の入手**: 取得済み。`...\AF016\ffbe473e_af016.txt`（出版社の全文ページ。1 行に潰れており本文は整形して読んだ）、`c7bca0ee_AF016.txt`（別取得）、補足表 `c7bca0ee_AF016_supp1.xlsx`（S1〜S3。**内容は未精読**・ファイルの存在のみ確認）。版: Front. Psychol. 17 (2026), 公開 27 August 2026, DOI 10.3389/fpsyg.2026.1921504。
2. **種類**: 系統的レビュー（自称。PRISMA 2020、「systematic review of this defined WoS/SSCI corpus, not a claim of exhaustive coverage」）。事前登録: 「The review was not preregistered.」
3. **対象・問い**: 教育（主に学部生）での生成 AI と近接する教育用 AI が学習者の認知負荷に与える影響。認知負荷理論（内在・外在・学習関連）の三分類と認知的オフローディングで整理。RQ1 が負荷の測定（Results）。**疲労ではなく認知負荷が対象**（fatigue 0 件）。
4. **方法**: Web of Science Core Collection のみ。SSCI・Education and Educational Research カテゴリ・英語・Article。検索式は 3 つのトピック欄を AND（負荷語／AI 語／大学語）で全文掲載。検索日: 2026 年 6 月（年の制限なし）。補足に WoS の保存クエリのリンク。後方引用追跡を補助的に実施。選別の流れ: 139 件→カテゴリ外 53 件除外→86 件→題目抄録で 30 件除外→全文 56 件→19 件除外→37 件＋後方追跡 2 件＝**39 件**。PRISMA 2020 図あり（Figure 1）。コーディング: 14 次元、2 名が独立に全件コード、Cohen's kappa 報告（0.80 未満だった 3 次元は規則を改訂して再コード）。質の評価: 「No validated study-level risk-of-bias or methodological-quality appraisal was preserved」とし、MMAT・JBI 等で採点しない（限界として保持）。
5. **採択内訳**: 39 件。設計: 実験 28・調査相関 7・単群前後 2・質的 2。測定: 負荷・努力尺度（Hwang 系その他）各 9、単一項目の精神的努力（Paas）7、三因子尺度（Leppink 2013・Klepsch 2017）計 6、NASA-TLX 4、負荷を質的主題としてコード 3、著者作成項目 1（合計 39。本文の記述を足した）。疲労を測った研究: 0 の記載（疲労の語が本文に 0 件）。
6. **主要な結論**: 全体指標だけの報告が 22 件で、外在負荷の低下とは言えない。外在負荷を別に測ったのは 16 件で、低下 7・差なし 3・上昇 1・曲線 1・方向なし 4。学習関連負荷の下位尺度を含むのは 11 件・方向ありは 5 件。総括は条件付き 21・有益 16・混合 2。AI の効果は足場かけ・投与量・既有知識・課題設計に依存。
7. **限界・要確認点**: 著者の限界（Limitations 節）: WoS/SSCI 限定・英語、尺度と設計の不均質と独立の質評価の欠如、「most studies relied on self-report and many used overall or undifferentiated load measures」。要確認: Abstract は「four did not provide a directional comparison」を 2 回使う（外在 16 件と全体指標 22 件の内訳。数の合計は一致して見える: 外在 7+3+1+1+4=16、全体 11+5+2+4=22）。補足 S1〜S3 の確認は未実施。
8. **データ公開**: 補足表 S1（採択 39 件の完全な引用と DOI）・S2（全文除外 19 件と理由）・S3（設計・測定の一覧）・PRISMA 2020 チェックリストを補足に載せる（Method・Supplementary material 節）。独立の「Data availability」見出し: 記載なし。
9. **(A)**
   - A1 AI への帰属 vs 一般の尺度: 記載なし（疲労を対象にしないため）。近い論点として、「AI/GenAI の対比を透明に報告せよ」「全体の負荷指標を AI の効果として束ねてはならない」（Abstract・Discussion）がある。
   - A2: 段落で論じる（Discussion: 「Most studies … relied on self-reported load, and self-report is precisely the channel through which offloading is most likely to mislead」＋眼球運動との併用の例、Implications で「pair self-report with process or performance measures」）。単一項目（Paas・7 件）は集計に出るが、単一項目そのものの批判: 記載なし。Limitations に 1 文。
   - A3: 1 文の言及（負荷を質的主題としてコードした研究が 3 件と数えるのみ。「表現が無い」ことの解釈: 記載なし）。
   - A4: 節を立てる（Results「Measurement of cognitive load (RQ1)」・Figure 2・補足 S3）。
10. **(B)**: 受動的疲労・警報疲れ・覚醒度・自動化バイアス・過信: 記載なし（全語 0 件）。近接: 認知的オフローディングを分析軸にし、Rind et al. (2026) を引いて「calibrated trust」「verify AI output」に触れる（Implications・1 段落）。自動化の人間工学の文献: 記載なし。
11. **組織の水準**: 記載なし（教育現場の教師・授業設計への含意のみ）。
12. **次の確認・作業**: 「引用する結果ごとに負荷の定義・指標・比較群・測定時点を確認」→ 一部確かめられた: 指標の内訳と比較設計（実験 28 件＝AI 条件と比較群または対抗条件）は本文にある。研究ごとの定義・測定時点は S3（未精読）に依存する（本文には「timing」「measurement point」「post-test」の語 0 件）。
13. **確認事項**: 入力に無し。
14. **ほかに確かめること**: 入力に無し（束ごとの追加なし）。

---

## AF017

1. **本文の入手**: 取得済み。`...\AF017\b997adee_af017_fulltext.txt`（CEUR-WS Vol-4134 paper2 の PDF 全文）。ほか `b997adee_af017.txt`・`c7bca0ee_AF017.txt`（別取得）。版: STPIS'25（2025-09-17/18 Skopje）、CEUR 公開 2025-12-20（PDF 内の表示）。OpenAlex に無料版の記録は無いが、一次情報 URL（ceur-ws.org）で全文が取れた。
2. **種類**: 系統的文献レビュー（自称。Okoli の 8 段階＋PRISMA 2020、「pre-specified protocol」と書く）。「standalone systematic literature review」（§2.1）。
3. **対象・問い**: 職場で AI システムに関連づくストレッサー。RQ1: 新たな AI ストレッサーは何か。RQ2: 従来の技術ストレッサーとどう違うか。
4. **方法**: 情報源は Scopus のみ（「No other databases were searched … no manual search of references」）。検索式を全文掲載（stress / AI / work-organization・最終版・Article・英語）。検索日 2025-03-07。期間制限なし。1333 件→第 1 段階（タイトル・抄録）で 1210 件除外→123 件→全文で 57 件除外→**66 件**。PRISMA 2020 図あり（Figure 1）。選別: 第 1 著者が題名・抄録を選別・抽出も 1 名（「one author performed the primary extraction for all studies」）。質の評価: 形式的な RoB は無し。研究ごとに「strong / moderate / weak」を記述的に注記（標本規模・設計の厳密さ）。プロトコルの登録先: 記載なし（「register / PROSPERO / OSF」0 件）。
   - 内部の食い違い（箇所を 2 つ）: §2.3「At the first stage, titles and abstracts were reviewed … by the first author」・§2.4「one author performed the primary extraction for all studies」 vs §2.3 末尾「No disagreements arose in the screening process among the authors as the criteria were clear-cut」（独立の複数名の判定がなかった場合、不一致が生じない前提の文になる。複数名の判定の有無は本文に明示なし）。
5. **採択内訳**: 66 件（量的 40・質的 9・混合 6・概念 11）、部門別（横断・一般 31、ホスピタリティ 11、医療 11、製造 4、交通 3 …）、AI の種類別（顧客対応 13・アルゴリズム管理・監視 11・臨床 11・生成 AI 5 …）（§3.1）。**疲労を実測した一次研究の一覧**: 本文には無い（66 件の一覧は Data Availability の「can be accessed here」のリンク先で、テキストからは読めない）。本文中に消耗・バーンアウトを結果に含むと書かれた研究の引用番号: 疲れ・消耗・燃え尽きの結果は [3][44][48][50][62][68][70][72][82][86] などで言及されるが、各研究が疲労をどの尺度で実測したかは本文に記載なし。
6. **主要な結論**: AI は確立した 6 つの技術ストレッサー（overload・invasion・complexity・insecurity・uncertainty・unreliability）を増幅し、さらに 5 つの AI ストレッサー（techno-unpredictability・loss of autonomy・ethical and moral conflict・social erosion・career disruption）を持ち込む。従来のストレッサーは現代の AI の特徴を捉えるに不十分と主張。
7. **限界・要確認点**: 著者の限界（§4 の限界の段落）: 否定的側面に偏る（肯定・中立のみは除外）・横断設計が多く因果は言えない（縦断は [49,57,61,68,79,86] のみ）・東アジア偏重・質で重み付けしていない・Scopus のみ（「strain」「burnout」で書かれた研究を逃す可能性）・近年の生成 AI は予備的。新規 5 ストレッサーは「lack validated measurement scales」。要確認: 上記 4 の食い違い。「pre-specified protocol」の実体（登録・公開）は記載なし。
8. **データ公開**: 「Data Availability: The full list of the 66 included studies can be accessed here.」（リンク先は未確認）。抽出表・コードブック: 記載なし（「data extraction form (initialized in a spreadsheet)」と書くが公開の記載なし）。
9. **(A)**
   - A1: 節を立てる（分析の軸）。ただし対象は疲労ではなくストレッサー。「AI ストレッサー」と従来の技術ストレッサーの区別が RQ2 の中心（§1・§3.2-3.3）。一般の尺度を AI の文脈で使う際の区別: 記載なし。
   - A2: 1 文（§4 限界「most empirical evidence is cross-sectional … a reverse causality or common method issue」。単一項目の批判: 記載なし）。
   - A3: 記載なし（質的研究は 9 件と数えるのみ。著者自身の統合は帰納コーディング）。
   - A4: 記載なし（方法別の内訳は 66 件の設計のみ。測定法別の内訳は無し）。1 文の言及として、新規ストレッサーに「validated measurement scales」が無いと書く。
10. **(B)**: 受動的疲労・警報疲れ・自動化バイアス: 記載なし。「vigilance」1 件（§3.2.1 末尾の「heightened vigilance, trust erosion」＝AI の予測不能性に伴うストレスの特徴。覚醒度研究の引用は無し）。「over-reliance」1 件（§3.2.2: 検査室職員が分析機器への過信で批判的思考が鈍ると懸念する [25] Jafri et al. 2024）。近接する記述: 地下鉄・高速鉄道の運転士が「passive monitoring」に置かれ「skill fade」と緊急時の介入圧を述べる [22,41]（§3.2.2）、自律運航での引き継ぎ [23]、Chen et al. [22] の精神的作業負荷。いずれも自動化の人間工学の古典（Parasuraman・Hancock・Matthews・Desmond）の引用ではない（0 件）。
11. **組織の水準**: 扱う（一部）。職場・組織の文脈が対象（「workplace」）。アルゴリズム管理・監視（11 件）、ILO 報告、組織の支援・方針への含意（§1 末・§4）。組織論の理論の導入は記載なし。
12. **次の確認・作業**: 「本レビューとの包含範囲の違いを記録」→ 確かめた（本文から）: AF017 は職場、Scopus のみ（stress×AI×work）、66 件（概念 11 件を含む）、疲労語ではなくストレス語で検索（限界節に「strain」「burnout」の取りこぼしの可能性）。「疲労を実測した一次研究を切り分けて追跡」→ 確かめられない（本文に一覧が無く、リンク先の一覧が未確認）。
13. **確認事項**: 入力に無し。
14. **ほかに確かめること**: (a) 概念の系譜: 技術ストレスは Brod [9]（1982 の記載）、Tarafdar ら [10]（2007）と Ragu-Nathan ら [11]（2008）の 5 創出因子、Weinert ら [12]（2020）の techno-unreliability、Tarafdar・Cooper・Stich [7][13]（2019）、ストレスの定義は Lazarus & Folkman [6]（1984）、Salo ら [8]（2018）。ストレッサーとストレインの区別は IS 文献 [13]（§1）。燃え尽きの尺度の系譜（MBI 等）: 記載なし。(b) 疲労・消耗の実測一次研究の一覧: 上記 5 の通り本文には無い。

---

## AF018

1. **本文の入手**: 取得済み。`...\AF018\b997adee_af018_fulltext.txt`（Smart Learning Environments 11:28 (2024) の全文 37 頁）。DOI 10.1186/s40561-024-00316-7。
2. **種類**: 系統的レビュー（自称。PRISMA と Macdonald ら (2023) の 5 段階。冒頭の文脈整理で scoping review (Tricco 2018) にも言及）。
3. **対象・問い**: 学生の AI 対話システム（生成モジュール付き）への過信が、意思決定・批判的思考・分析的思考に与える影響と、AI の倫理的問題が過信に寄与する経路。**疲労は対象外**（fatigue 0 件）。
4. **方法**: ProQuest・IEEE Xplore・ScienceDirect・Web of Science の 4 データベース。検索語は 4 組（AI 対話システム／倫理的問題の語／認知能力の語）。期間 2017〜2023。査読論文＋会議論文、英語、レビュー・書籍・社説は除外。検索日: 記載なし。検索式の完全な形（Boolean 式）: 記載なし（語の列挙のみ）。選別の独立 2 名: 「dual screening process in accordance with the PRISMA guidelines」とあるが担当者の記述なし。PRISMA 図あり（Figure 1: 70 件→15 件除外→55→全文 40 件・35 件評価→除外 21→9 件＋「reports of included studies 5」＝14 件）。質の評価: 記載なし。
   - 内部の食い違い: 本文「removal of redundant entries, … reducing the initial collection of studies to 70」 vs Figure 1「Records identified … (n=70)」の後に重複 7 件を除去。Limitations「based on a review of literature from only 14 databases」 vs 方法の 4 データベース（14 は採択件数と同じ数）。「14 publications were identified, each featuring all the specified search terms」（Choosing the final samples）と、前段の 70→35→14 の絞り込みの記述の関係は本文だけでは整合を取れない。
5. **採択内訳**: 14 件。表 2（Findings of AI dialogue systems…）に研究ごとの目的・結果・認知能力・倫理問題を載せる。設計の混在（調査 245 名の事例研究 [Malik 2023]、教師への半構造化面接 [Marzuki 2023]、論考・レビュー型を含む）。デザインの分布の集計表: 記載なし。疲労を測った研究: 0（語なし）。
6. **主要な結論**: AI の倫理的問題（誤情報・アルゴリズムバイアス・盗用・プライバシー・透明性）が過信を助長し、意思決定・批判的思考・分析的思考を損ないうる。人は「fast and optimal solutions」を好み、ヒューリスティクスに頼ると説明する（Abstract・Conclusion）。
7. **限界・要確認点**: 著者の限界: 否定的影響に絞った狭い範囲、データベースの限定、高等教育に限定。要確認: 上記 4 の食い違い、一次研究のデザインと結果（Table 2 は研究の記述が中心で、効果の測定の記述は薄い）。「Ethics approval」欄が「The author intends to submit a comprehensive application for ethical clearance…」の文言（Declarations）。
8. **データ公開**: 「Availability of data and materials: Not applicable.」。表 2 は本文内にある。
9. **(A)** A1〜A4: 記載なし（疲労・疲労の測定を扱わない。過信の測定への批判: 記載なし）。
10. **(B)**: 「over-reliance」61 件・「overreliance」6 件（レビューの中心概念。定義は Abstract: 「users accept AI-generated recommendations without question…」→節を立てる）。「automation bias」2 件（本文 1 文: Gsenger & Strle 2021 を引く「…weakening of essential cognitive abilities (Grinschgl & Neubauer, 2022) and automation bias (Gsenger & Strle, 2021)」＋参考文献 1 件）。「complacen」4 件（Duhaylungsod & Chavez 2023 の「ease of access … can lead to complacency」ほか。結論部でも反復）。受動的疲労・警報疲れ・覚醒度: 記載なし。Parasuraman・Hancock・Matthews・Desmond: 0 件。自動化の人間工学の古典の引用: 記載なし（過信は教育・倫理の文献と認知バイアス・ヒューリスティクス〈Grinschgl & Neubauer 2022〉から導く）。
11. **組織の水準**: 記載なし（教育者・政策担当者への提言＝Recommendations の 1 段落のみ）。
12. **次の確認・作業**: 「主張に対応する一次研究のデザインとアウトカムを再抽出」→ 一部確かめられた（表 2 から研究ごとの記述は読めるが、デザインとアウトカムの統一的な再抽出は未実施。全 14 件の分類は未了）。
13. **確認事項**: 入力に無し。
14. **ほかに確かめること**: 入力に無し。

---

## NOBLES

1. **本文の入手**: 取得済み（手元の写し。Zenodo へは取りに行っていない）。`C:\Users\johnd\Downloads\ai-fatigue-fulltext\NOBLES\B9_manuscript.txt`（原稿）・`B9_xlsx.txt`（表 01〜04 の写し）・`AI_Fatigue_Reproducibility_Package\`（xlsx 4 本・docx・README・CITATION.cff・DEPOSIT_CHECKLIST.txt・repository_metadata.json・SHA256SUMS.txt）。版: 原稿は投稿前の状態で、「Received X of Month, 2026」「Cite as … Knowledge Economy and Lifelong Learning, X(X), XX-XX」のプレースホルダと「AUTHOR VERIFICATION REQUIRED」の注記が残る。Zenodo の記録（doi:10.5281/zenodo.22838191）と同一かは未確認。パッケージの metadata は version 1.0・publication_date 2026-09-18。非査読。
2. **種類**: 著者の自称は「systematic review」（題名・Abstract）。ただし統合は「two-cycle narrative and thematic synthesis」で、一次研究・二次レビュー・ガイダンス分析・隣接する組織の証拠を混ぜて数える（Table 4 の evidence-role）。
3. **対象・問い**: 高等教育の学生・教員・職員の AI 疲労。RQ1 関連条件（と文脈的増幅因子の区別）、RQ2 認知・感情・動機・行動・身体の現れ、RQ3 機序に合う予防策とその証拠。
4. **方法**: 9 情報源（Scopus・WoS・ERIC・Education Source・PsycINFO・PubMed・IEEE Xplore・ACM DL・Google Scholar）。検索日 2026-07-06〜07-10、更新 07-15。期間 2020〜2026 年 7 月・英語。検索式は Appendix B と `01_Search_Strategy.xlsx` に掲載（「replication-ready」）。ただし「The exact historical search exports were not included … the appendix strings must therefore be checked against saved platform histories」。件数: 304 件特定（Table 3 の合計 68+54+31+27+24+22+19+14+45=304 と一致）→重複 49 除去→255→題目抄録で 205 除外→50 件取得・うち 5 件は同定不能で未取得→45＋引用追跡 1＝46 全文→14 除外→**32 件**。PRISMA 図・チェックリストあり（Figure 1・Appendix A）。選別: **1 名のみ**（「No independent second-reviewer verification was documented」）。32 件中 7 件を 2 週間後に再コード（自己内の一貫性）。質の評価: MMAT 2018 に「informed」した設計別の判断（Table 6）。確信度は著者定義（GRADE-CERQual ではない）。プロトコルは事前登録していない（「not prospectively registered」）。Google Scholar は先頭 100 件を確認し 45 件を採用、残り 55 件の内訳は記録なし。灰色文献は系統的には探索せず。ソフトウェアまたは AI 対応ツールの名前・版は記録なし（要記入の注記）。
5. **採択内訳**（32 件。Table 6 と `03_..._Appraisal.xlsx`）: 直接の一次証拠（Table 4 の区分）に当たるのは、題名と設計から読める範囲で Miranda 2026（グラウンデッド・セオリー）・Soriano 2026（潜在プロフィール分析）・Parreño 2026（内容・KWIC 分析）・Wang 2026（横断の構造モデル・technostress / digital fatigue / AI dependency / burnout）・Alkhatib 2026（横断調査・「AI-induced cognitive overload and digital fatigue」）・Halupa & Bolliger 2020（教員調査・技術疲労・生成 AI 以前）。文脈的一次（採用・信頼・公平性の調査・質的）、二次（レビュー）、ガイダンス・政策、隣接する組織の証拠（銀行・医療・公共機関）を含む。**疲労を AI に帰属させて測った研究の数**: 表の記録からは数えられない。題名で AI 疲労・AI 誘発の疲労を掲げるのは 4 件（Miranda・Parreño・Soriano・Alkhatib）、Wang は技術ストレス・デジタル疲労・AI 依存の並列、Halupa は AI 以前の技術疲労（題名と Table 6 の判断文による。尺度・設問の中身は未確認）。測り方（尺度名・単一項目か否か）: Table 6 と `03`・`04` に**記録なし**（列は Source / Design or type / Context / Synthesis role / Appraisal judgment のみ）。「Alotaibi: fatigue was not measured」「Suwendi: fatigue is inferred from implementation burden rather than measured」のように、疲労を測っていない旨の判断文は個別にある。
6. **主要な結論**: 疲労と関連する条件として直接支えられるのは、認知過負荷と確認の負担・技術ストレスと常時接続・許容される使い方の曖昧さ・依存に伴う動機の枯渇。不透明性・信頼・公平性・不均等なアクセスは「contextual amplifiers」であり独立の原因とは言えない。現れは 5 領域で共起するが、反復する循環と「制度設計の信号」という枠組みは理論的統合で未検証。「AI fatigue」は妥当性が確かめられた別個の心理測定構成概念ではなく、技術ストレス・デジタル疲労・燃え尽きの交点の概念的提案とする。
7. **限界・要確認点**（著者の記述: Conclusion の限界の段落）: 未登録・単独選別・検索の履歴の未保存・同定不能 5 件・Google Scholar 55 件・英語のみ・統計統合不可・介入証拠が無い。要確認（読んで気づいた点）: (a) 原稿の記述する検索式・除外の一覧は「reconstructed from the final manuscript tables」（`01` Provenance Notes）で、原本のエクスポートではない（README・DEPOSIT_CHECKLIST も同旨）。(b) 14 件の全文除外と 5 件の未取得の書誌は存在しない（`02` Audit Limitations）。(c) 生成 AI（ChatGPT）を改稿・表の下書きに使用と開示（Statement on the Use of AI Tools）、「digital tool」の名前が未記録（上記 4）。
8. **データ公開**: 原稿の Data Availability Statement: 「The screening log, extraction codebook, appraisal matrix, and verified historical search exports **should be deposited** in a trusted open repository before publication. Persistent identifier: [TO BE INSERTED AFTER DEPOSIT].」＋「AUTHOR VERIFICATION REQUIRED: Deposit the reproducibility package…」。パッケージ側: `repository_metadata.json` の license は「TO_BE_SELECTED_BY_AUTHOR_AT_DEPOSIT」、related_identifier は「PENDING_PERMANENT_REPOSITORY_IDENTIFIER」。手元の原稿の状態は未寄託の記述（Zenodo の公開記録との関係は未確認）。パッケージには、検索（01）・件数と 32 件（02）・抽出と判断（03）・コードブックと再コード（04）がある。
9. **(A)**
   - A1: 節を立てる（Table 2「Conceptual Boundaries Between AI Fatigue and Adjacent Constructs」、定義の節。「not … a validated diagnostic or psychometric category」）。ただし AI に帰属させて測ることと一般の疲労尺度を AI の文脈で使うことの区別を、尺度の水準で論じる記述: 記載なし（Table 6 では Wang の技術ストレス・デジタル疲労と AI 疲労を別の列に置く程度）。
   - A2: 段落で論じる（Abstract「predominantly cross-sectional and self-reported evidence does not establish causation」・Table の Note・Conclusion「Heterogeneous measures … need for validated scales」、研究ごとの判断文）。単一項目の批判: 記載なし。
   - A3: 1 文の言及（Parreño の判断文「findings reflect expressed experience in one national context」）。「疲労の表現が無い」の解釈: 記載なし。
   - A4: 記載なし（Table 6 は設計別の記載で、測定法・尺度の集計は無い）。
10. **(B)**: 受動的疲労・自動化バイアス・警報疲れ・覚醒度・Parasuraman 等: 記載なし（0 件）。「overreliance」5 件（検索式 2 か所＋Klimova & Pikhart 2025 の「well-being, overreliance, and screen-exposure」の紹介 2 か所）。近接: 「passive reliance」「passive output acceptance」を依存の枯渇の説明（動機・行動の現れ）に使う（反復するループの記述と Codebook）。自動化の人間工学の文献の引用: 記載なし（理論は JD-R〈Demerouti 2001〉と資源保存理論）。
11. **組織の水準**: 扱う（節を立てる）。制度の導入・調達・ガバナンス・教員支援・公平性、「institutional monitoring」「fatigue as an institutional design signal」、隣接の組織の証拠（銀行・公共機関）。理論: JD-R・資源保存理論。
12. **次の確認・作業**: 入力に無し。
13. **確認事項**: 入力に無し。
14. **ほかに確かめること**: (a) 採択 32 件のうち疲労を AI に帰属させて測った研究: 上記 5（題名と設計から 4 件、数は記録されていない。尺度は未記録）。(b) 原稿のデータ公開の欄: 上記 8（「should be deposited」・識別子は TO BE INSERTED・未寄託の文面）。

---

## 7 件の対応表（行=件、列=(A1)(A2)(A3)(A4)(B)）

| 件 | A1 | A2 | A3 | A4 | B |
|---|---|---|---|---|---|
| AF013 | 節（概念図・尺度は対象外） | 記載なし | 記載なし | 記載なし | 1 文（complacency 1 件のみ・古典の引用なし） |
| AF014 | 段落（AI ストレッサーと従来の区別）＋1 文（尺度未整備） | 1 文 | 記載なし | 記載なし（尺度の列挙 1 段落のみ・表なし） | 1 文（overreliance 2 件・古典の引用なし） |
| AF015 | 未確認（本文なし） | 未確認 | 未確認 | 未確認 | 未確認（抄録は記載なし） |
| AF016 | 記載なし（疲労を扱わない） | 段落 | 1 文 | 節 | 記載なし（近接: オフローディング・較正された信頼の 1 段落） |
| AF017 | 節（対象はストレッサー・疲労ではない） | 1 文 | 記載なし | 記載なし | 1 文（vigilance 1・over-reliance 1・passive monitoring の記述。古典の引用なし） |
| AF018 | 記載なし | 記載なし | 記載なし | 記載なし | 節（過信が主題）＋1 文（automation bias）・古典の人間工学の引用なし |
| NOBLES | 節（概念境界の表）・尺度の水準の区別は記載なし | 段落 | 1 文 | 記載なし（設計別のみ・測定法の列なし） | 1 文（passive reliance の語のみ・古典の引用なし） |
