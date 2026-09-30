# 抽出結果 G1（AF001, AF002, AF003, AF004, AF034, AF005）

注記: 本レコードの多くは ScienceDirect（Incapsula/PerimeterX による bot 検知、HTTP 403・CAPTCHA）と
PubMed（reCAPTCHA）が自動アクセスをブロックしたため、**全文を直接閲覧できたのは AF005（Frontiers, OA）のみ**。
他は Crossref / OpenAlex / Unpaywall / Europe PMC / Semantic Scholar の書誌・抄録 API、および ResearchBox
（AF001 の補助資料ページ）からの抽出。全文未取得のレコードは「未確認」表記を用い、「記載なし」は使わない
（全文を読んで不在を確認したわけではないため）。

---

## AF001
- アクセス範囲: 抄録のみ（全文不可）。使用 URL:
  - https://doi.org/10.1016/j.chbr.2026.101186 → https://linkinghub.elsevier.com/retrieve/pii/S2451958826002605 → https://www.sciencedirect.com/science/article/pii/S2451958826002605 （HTTP 403、Incapsula/PerimeterX CAPTCHA ページ、本文取得不可。ページ本体は 1.2MB あるが中身はボット判定ページ）
  - https://ink.library.smu.edu.sg/soss_research/4462/ （SMU リポジトリ。Incapsula にブロックされ空応答、"Request unsuccessful. Incapsula incident ID: ..."）
  - https://researchbox.org/6748 （補助資料ページ。閲覧可）
  - https://api.openalex.org/works/doi:10.1016/j.chbr.2026.101186 （抄録を `abstract_inverted_index` から復元、閲覧可）
  - https://api.unpaywall.org/v2/10.1016/j.chbr.2026.101186 （gold OA・CC BY-NC-ND を確認、PDF 直リンクなし）
  - Semantic Scholar（DOI 解決）: 抄録 null
  - ResearchGate URL（input 記載分）は未着手（時間配分のため深追いせず）
- 書誌（一次で見えた値）: 著者（全員, Crossref 準拠）= Gabriel R. Lau / K.T.A. Sandeeshwara Kasturiratna / Adalia Y.H. Goh / Eddie M.W. Tong / Andree Hartanto。誌名 = Computers in Human Behavior Reports。巻 23、論文番号 101186（first/last page とも 101186）。年 2026、オンライン公開 2026-06-26（license の vor start 日）、印刷/正式公開 2026-08。DOI 表記: 10.1016/j.chbr.2026.101186（Crossref・OpenAlex 一致）
- 訂正・撤回・懸念表明: Crossref `update-to` = null、`relation` = {} （空）。訂正・撤回・懸念表明は確認できず
- 研究デザイン: 尺度開発・検証研究（"scale development and validation"）。4 つの下位研究から成る（抄録に "Across four studies with 717 participants"）
- 対象・国・募集方法・収集時期: 未確認（抄録に国・募集方法・収集時期の記載なし。全文未取得）
- N（募集・除外・解析の各段）: 抄録レベルで「4 studies with 717 participants」（単位=人、4 研究合計）。各研究別の N は未確認（ResearchBox に Study 2/3/4 のデータ CSV が存在するが、ファイル中身は未開封）
- AI の種類・利用文脈: 未確認（抄録は "human–AI interaction" 全般を対象とし、特定の AI ツール名の記載は抄録中に無し）
- 疲労（または中心構成概念）の操作化: 構成概念名 = AI Fatigue（AI 疲労）。尺度 = 15-item AI Fatigue Scale（新規開発、著者ら）。因子構造 = 4 因子（cognitive, emotional, physical, behavioural）の高次モデル（"a four-factor (cognitive, emotional, physical, behavioural) higher-order model"）。項目文の逐語例: 未確認（抄録に個別項目の例文なし。ResearchBox のプレビューにも項目文は表示されず）。★ 疲労が「AI の利用」に帰属して測られているか: 尺度名・構成概念名自体が "AI Fatigue" であり、抄録は "user fatigue arising from prolonged human–AI interaction" と明記 — AI 利用に明示的に帰属させた操作化と読める（逐語: "user fatigue arising from prolonged human–AI interaction has become an increasing concern"）
- その他の主要変数: general/clinical/digital fatigue、AI-specific technostress、AI dependency、AI attachment、critical thinking in AI use、negative affect、attitudes toward AI、neuroticism、conscientiousness、extraversion、self-reported current AI use、intention to reduce AI use（すべて抄録に名称のみ記載、尺度出典は未確認）
- 解析手法: 抄録の記述から EFA/CFA を含むと推定されるが、手法名の明示は未確認（"identified and confirmed" という語のみ、具体的解析名は不明）
- 主要結果（報告された数値を逐語で）: "The scale demonstrated strong internal consistency (α = .92), robust factor loadings, two-week test-retest reliability (ICC(2,1) = .65), and measurement invariance across sex."（出所: OpenAlex 抄録）。相関係数などの具体値は抄録になく未確認
- 著者自身が述べる限界: 未確認（全文未取得）
- 倫理承認・同意: 未確認（全文未取得。抄録に記載なし）
- 事前登録・データ/材料公開・資金・利益相反: 事前登録 = ResearchBox 6748 に Study 2 "AsPredicted #249,222"（PDF, 2025-09-27 付）、Study 3 "AsPredicted #249,751"（PDF, 2025-10-01 付）、Study 4 "AsPredicted #253,505"（PDF, 2025-10-23 付）の 3 件が確認できる（Study 1 の事前登録は ResearchBox 上に見当たらず）。データ = ResearchBox に "AI_Fatigue_Study2.csv" / "AI_Fatigue_Study3.csv" / "AI_Fatigue_Study4.csv"（いずれも更新日 2026-06-28）。資金 = Crossref funder: Singapore Management University、Government of Singapore Ministry of Education（award 25-SOSS-SMU-006）。利益相反: 未確認
- 設計別チェック（E: COSMIN 測定特性。全文未取得のため各項目「報告あり（数値, 抄録由来）」または「未確認（全文未取得）」で区別）:
  - 内容的妥当性（項目生成の手順・対象者/専門家の関与）: 未確認（全文未取得。抄録には "generated and content-validated an item pool" とあるが手順の詳細なし）
  - 構造的妥当性（EFA・CFA・標本の分離・適合度）: 未確認（"identified and confirmed a four-factor ... higher-order model" のみで適合度指標は抄録になし）
  - 内的一貫性: 報告あり（数値） — α = .92（全体、下位尺度ごとの値は未確認）
  - 信頼性（再検査・期間・ICC）: 報告あり（数値） — two-week test-retest, ICC(2,1) = .65
  - 測定誤差: 未確認
  - 仮説検証（収束・弁別・増分）: 報告あり（方向性のみ、数値は未確認） — "Convergent validity evidence was supported through associations with general, clinical, and digital fatigue... discriminant validity evidence was observed against... AI dependency, AI attachment, and critical thinking"（具体的 r 値は抄録になし）
  - 異文化妥当性: 報告あり（一部） — 性別間の測定不変性のみ（"measurement invariance across sex"）。文化間の異文化妥当性の記載は未確認
  - 反応性: 未確認
- 気づいた内部不整合: 特になし（抄録・Crossref・OpenAlex 間で書誌の不一致は見当たらず）。ただし ResearchBox に Study 1 の事前登録が見当たらない点は、4 研究のうち事前登録対象が 3 研究のみである可能性を示唆（未確認、深追いできず）

---

## AF002
- アクセス範囲: 書誌のみ（抄録も取得不可）。使用 URL:
  - https://www.sciencedirect.com/science/article/pii/S0268401225001422 （HTTP 403）
  - https://doi.org/10.1016/j.ijinfomgt.2025.103010 （Crossref 解決のみ、抄録フィールドなし）
  - Europe PMC REST search（DOI 指定）→ hitCount 0（未索引）
  - OpenAlex works（DOI 指定）→ open_access.is_oa = false、abstract_inverted_index なし
  - Unpaywall → is_oa: false, best_oa_location: null
  - Semantic Scholar → abstract: null（openAccessPdf.url も空文字）
- 書誌: 著者（全員, Crossref）= Hui Yang / Yu Zeng / Huizi Xing / Peng Hu。誌名 = International Journal of Information Management。巻 87、論文番号 103010。年 2026、公開 2026-04。DOI 表記: 10.1016/j.ijinfomgt.2025.103010（Crossref DOI 表記の年 "2025" と巻号の公開年 "2026" が異なる点は DOI 命名規則上の通例で不整合ではない）
- 訂正・撤回・懸念表明: Crossref `update-to` = null、`relation` = {}。訂正・撤回の表示は確認できず
- 研究デザイン〜内部不整合まで: すべて未確認（抄録・全文とも取得不可のため）
- 設計別チェック（A: 横断研究、全文未取得のため全項目 Unclear・「全文未取得」）: 1〜8 すべて Unclear（全文未取得）

---

## AF003
- アクセス範囲: 書誌のみ（抄録も取得不可）。使用 URL:
  - https://www.sciencedirect.com/science/article/pii/S0747563226001949 （HTTP 403）
  - https://dl.acm.org/doi/10.1016/j.chb.2026.109097 （HTTP 403）
  - https://doi.org/10.1016/j.chb.2026.109097 （Crossref 解決のみ）
  - Europe PMC REST search（DOI 指定）→ hitCount 0
  - OpenAlex works（DOI 指定）→ is_oa: false、抄録なし
  - Unpaywall → is_oa: false
  - Semantic Scholar → abstract: null
- 書誌: 著者（全員, Crossref）= Hui Yang / Jinqiang Wang / Peng Hu（Semantic Scholar 表記は "Jin-Qiang Wang" とハイフン付き — 表記ゆれ、実質的な著者不一致ではない）。誌名 = Computers in Human Behavior。巻 185、論文番号 109097。年 2026、公開 2026-12。DOI 表記: 10.1016/j.chb.2026.109097
- 訂正・撤回・懸念表明: Crossref `update-to` = null、`relation` = {}
- 研究デザイン〜内部不整合まで: すべて未確認
- 設計別チェック（A: 横断研究、全文未取得のため全項目 Unclear・「全文未取得」）: 1〜8 すべて Unclear（全文未取得）
- 備考: AF002・AF003 は著者 2 名（Hui Yang, Peng Hu）が共通し、同一テーマ（生成 AI 利用と疲労）を近接時期に別誌へ発表している（AF002: IJIM 2026-04、AF003: CHB 2026-12）。関連研究群として GSE 側の評価で重複度を確認する価値があると思われるが、これは判定であり本抽出の範囲外のため指摘のみ

---

## AF004
- アクセス範囲: 抄録のみ（全文不可）。使用 URL:
  - https://pubmed.ncbi.nlm.nih.gov/41076923/ （reCAPTCHA ブロックで本文取得不可）
  - https://www.sciencedirect.com/science/article/pii/S0001691825010388 （未着手・時間配分のため試行せず。ScienceDirect は他レコードで一貫して 403 のため同様と推定されるが未検証）
  - https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI:10.1016/j.actpsy.2025.105725&format=json&resultType=core （hitCount 1、抄録全文を取得。`isOpenAccess: "N"`, `inEPMC: "N"`, fullTextUrlList は "Subscription required" のみ）
  - Crossref（DOI 解決）: 抄録フィールドなし、書誌のみ
- 書誌: 著者（全員, Crossref・Europe PMC 一致）= Jinrui Tian / Ronghua Zhang（Europe PMC: Tian J, Zhang R. 所属: Institute of Developmental and Educational Psychology, School of Marxism, Wuhan University, 430072, Wuhan, China）。誌名 = Acta Psychologica。巻 260、論文番号 105725。年 2025、公開 2025-10（Crossref: published-online なし、published-print 2025-10-01。license vor start 2025-10-06、CC BY-NC、delay-in-days 5）。DOI 表記: 10.1016/j.actpsy.2025.105725。PMID = 41076923
- 訂正・撤回・懸念表明: **あり（Corrigendum, AF034）**。Crossref 側（AF004 自身のレコード）には `update-to` も `relation` も付いておらず（ともに空）、Corrigendum への参照は AF004 の Crossref メタデータからは検出できない。一方 Europe PMC の AF034（PMID 42225464）レコードの `commentCorrectionList` には `{"source":"MED","id":"41076923","reference":"Acta Psychol (Amst). 2025 Oct;260:105725. doi: 10.1016/j.actpsy.2025.105725.","type":"Erratum for"}` とあり、AF034 → AF004 方向の Erratum リンクは Europe PMC 側にのみ存在する（AF004 自身のレコードにはこの逆参照が現れない、非対称）
- 研究デザイン: 横断的質問紙調査＋モデレート媒介モデル（PROCESS Model 8）
- 対象・国・募集方法・収集時期: 対象 = 中国の大学生（"580 Chinese university students"）。募集方法・収集時期は未確認（抄録に記載なし）
- N: 580 人（"Data were collected from 580 Chinese university students"）。募集時・除外後の内訳は未確認
- AI の種類・利用文脈: 教育文脈での AI 利用一般（"the growing integration of artificial intelligence (AI) in education"）。特定ツール名は未確認
- 疲労（または中心構成概念）の操作化: 構成概念名 = cognitive fatigue（認知疲労）。媒介変数として位置づけ（"cognitive fatigue as a mediating mechanism"）。尺度名・項目数・出典・項目例はすべて未確認（抄録に記載なし）。★ 疲労が AI 利用に帰属して測られているかは未確認（抄録の文だけでは AI 依存→認知疲労という因果順の媒介モデルであることは分かるが、尺度項目文が AI 利用に明示的に言及しているかは全文が無いと判定不能）
- その他の主要変数: AI dependence（独立変数）、critical thinking（従属変数）、information literacy（調整変数、モデレータ）
- 解析手法: moderated mediation model, PROCESS Model 8（Hayes の PROCESS マクロと推定されるが明示引用は未確認）
- 主要結果（報告された数値を逐語で）: 具体的な係数・p 値・CI は抄録になし。定性的記述のみ: "greater AI dependence was associated with lower levels of critical thinking, with cognitive fatigue partially mediating this relationship. Information literacy buffered the negative impact of AI dependence on critical thinking but also amplified cognitive fatigue when AI reliance was high."
- 著者自身が述べる限界: 未確認
- 倫理承認・同意: 未確認
- 事前登録・データ/材料公開・資金・利益相反: 未確認（Crossref に funder 情報なし = "funder": None）
- 設計別チェック（A: 横断研究、全文未取得のため全項目 Unclear・「全文未取得」）: 1〜8 すべて Unclear（全文未取得。抄録レベルでは 3 対象者記述 = 「580 Chinese university students」のみ判明するが、全文未確認のためチェック表記は Unclear のまま）
- 気づいた内部不整合: **タイトルと抄録で調整変数の名称が食い違う**。Crossref のタイトルは "...the social buffering role of **AI literacy**"（AI リテラシー）だが、Europe PMC の抄録本文は一貫して "**information literacy** as a moderating factor" / "Information literacy buffered..." と記述しており、"AI literacy" という語は抄録中に一度も出てこない（出所: Crossref `title` フィールド vs Europe PMC `abstractText`、両方とも同一 DOI 10.1016/j.actpsy.2025.105725 のレコードから取得）。また、input-G1.md の AF004 節には PubMed URL が 2 件（41076923 と 42225464）列挙されているが、Europe PMC で確認したところ 42225464 は AF004 ではなく Corrigendum（AF034）の PMID であり、AF004 自身の PMID は 41076923 のみ（出所: fetch/af004_epmc.json の `pmid` フィールドと fetch/af034_epmc.json の `pmid` フィールド）

---

## AF034（Corrigendum — AF004 への訂正通知）
- アクセス範囲: 書誌のみ（訂正の本文は取得不可）。使用 URL:
  - https://pubmed.ncbi.nlm.nih.gov/42225464/ （reCAPTCHA ブロック）
  - https://doi.org/10.1016/j.actpsy.2026.107179 → https://linkinghub.elsevier.com/retrieve/pii/S0001691826009807 → ScienceDirect PII S0001691826009807（HTTP 403、Incapsula/CAPTCHA、本文取得不可）
  - Europe PMC REST（DOI 指定）→ hitCount 1、メタデータのみ取得（`fullTextUrlList` は "Subscription required" のみで抄録テキスト自体が Europe PMC レコードに含まれていない）
  - Crossref（DOI 解決）→ 書誌・`update-to` 取得
- **書誌（一次で見えた値）**: 著者（全員, Crossref・Europe PMC 一致）= Jinrui Tian / Ronghua Zhang（同一著者・所属は AF004 と同じ）。誌名 = Acta Psychologica。巻 267、論文番号 107179。年 2026、公開 2026-07（Crossref published-print 2026-07-01）。DOI 表記: 10.1016/j.actpsy.2026.107179。PMID = 42225464。タイトル逐語: "Corrigendum to “Learners' AI dependence and critical thinking: The psychological mechanism of fatigue and the social buffering role of AI literacy” [Acta Psychologica 260 (2025) 105725]"
- **訂正・撤回・懸念表明の確認結果**:
  - Crossref の AF034 レコードは `update-to` フィールドに `{"DOI":"10.1016/j.actpsy.2025.105725","type":"erratum","label":"Erratum","source":"publisher","updated":{"date-parts":[[2026,7,1]]...}}` を持つ — AF004（105725）に対する publisher 発行の erratum であることを Crossref が確認
  - Europe PMC の AF034 レコードは `pubTypeList.pubType = ["Published Erratum"]`、`commentCorrectionList` に `{"type":"Erratum for","id":"41076923"(=AF004のPMID),"reference":"Acta Psychol (Amst). 2025 Oct;260:105725. doi: 10.1016/j.actpsy.2025.105725."}` を持ち、AF004 との紐付けは Europe PMC 経由でも独立に確認できる
  - **訂正の具体的内容（何が訂正されたか＝参考文献／数値／表／著者情報のいずれか）は、今回アクセスできた範囲（Crossref メタデータ・Europe PMC メタデータ）には一切含まれていない。** ScienceDirect の実ページ（訂正本文が書かれているはずの場所）は Incapsula の CAPTCHA に阻まれ、PubMed のアブストラクトページも reCAPTCHA に阻まれたため、**訂正本文そのものは読んでいない**。したがって「何が」訂正されたかは特定できなかった
- 対象・国・募集方法・収集時期／N／AI の種類・利用文脈／疲労の操作化／その他の主要変数／解析手法／主要結果／著者自身が述べる限界／倫理承認・同意／事前登録等: **すべて未確認**（訂正通知は通常これらを含まないと想定されるが、本文を読んでいないため断定はできない）
- 設計別チェック: F（方法論文献・報告ガイドライン・訂正通知）に該当するため設計別チェックは不要（brief の規定通り）。件数などの主要数値: 該当なし（訂正通知の性質上、標本数等は本体論文 AF004 側に帰属すると推定されるが未確認）
- 気づいた内部不整合: AF034 → AF004 の紐付けは Crossref (`update-to`) と Europe PMC (`commentCorrectionList`) の双方で確認できる一方、**AF004 自身の Crossref レコードには逆方向の `relation`/`update-to` が一切現れない**（AF004 節を参照）。Corrigendum 側からは訂正対象が明確でも、原論文側のメタデータからは訂正の存在が読み取れない非対称性がある（出所: fetch/af004_crossref.json の `relation: {}` と fetch/af034_crossref.json の `update-to`）

---

## AF005
- アクセス範囲: **全文**（Frontiers, オープンアクセス）。使用 URL:
  - https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2026.1879080/full （閲覧可、CC BY 4.0）
  - Crossref（DOI 解決）で書誌確認
  - ★ 全文はツール経由（WebFetch、HTML→要約変換）で抽出した内容であり、逐語引用の正確性は一次 HTML を自分の目で全行確認したわけではない点に留保あり（時間制約のため生 HTML の再取得はしていない）
- 書誌（一次で見えた値）: 著者（全員）= Wenwen Zhao / Jiawen Liu（所属: School of Literature and Journalism, Guangdong Ocean University, Zhanjiang, China）。誌名 = Frontiers in Psychology。巻 17、論文番号 1879080（号・頁番号はなし、article number のみ）。年 2026、オンライン公開 2026-08-10（Crossref published-online 一致）。DOI 表記: 10.3389/fpsyg.2026.1879080。ライセンス CC BY 4.0
- 訂正・撤回・懸念表明: Crossref `update-to` = null、`relation` = {}。訂正・撤回の表示なし
- 研究デザイン: 横断的オンライン質問紙調査（"Cross-sectional online questionnaire survey using Wenjuanxing platform, disseminated via social media"）。C-A-B（cognitive-affective-behavioral）フレームワークに基づく
- 対象・国・募集方法・収集時期: 募集方法 = Wenjuanxing（問巻星、中国のオンライン調査プラットフォーム）経由・SNS 拡散。国は本文に明示されているか未確認（今回の抽出結果には「Not explicitly stated in content provided」とあり、著者所属が中国・調査プラットフォームが中国系である状況証拠はあるが、本文中の明示的な国名記載は確認できていない＝読んでいない）。収集時期は未確認
- N（募集・除外・解析の各段）: 募集 500 件（回答）、有効回答（解析対象）426 件（"426 valid questionnaires"、単位=回答）。除外基準の詳細は未確認
- AI の種類・利用文脈: generative AI（生成 AI）全般。特定ツール名の記載は今回の抽出結果になし（未確認）
- 疲労（または中心構成概念）の操作化: 構成概念名 = cognitive fatigue（認知疲労、上位概念）。下位に misinformation fatigue（8 項目、Choi et al. 2018 を改変）と privacy fatigue（8 項目、Choi et al. 2018 を改変）の 2 尺度。項目例（逐語）: misinformation fatigue = "Repeated verification of AI authenticity has left me affectively exhausted"；privacy fatigue = "Managing privacy settings for AI has left me utterly exhausted"。いずれも 7 件法（1=strongly disagree, 7=strongly agree）。★ 疲労が「AI の利用・監督」に帰属して測られているか: 項目文が明示的に "AI authenticity" "AI" への言及を含み、AI 利用に直接帰属する形で操作化されている（上記項目例で確認）
- その他の主要変数: AI misinformation risk perception（9 項目, Roozenbeek et al. 2022 改変, 例: "I often worry that AI-generated content requires further verification"）、AI privacy risk perception（4 項目, Featherman & Pavlou 2003 改変, 例: "Using AI tools may result in me losing control over my personal information"）、AI anxiety（8 項目, Wang & Wang 2022 改変, 例: "I'm concerned that AI technologies might lose control and malfunction"）、AI discontinuance intention（5 項目, Maier et al. 2015 / Bhattacherjee 2001 改変, 例: "I plan to stop using AI tools in the near future"）、AI dependence（4 項目, Huang et al. 2024 改変, 例: "When I cannot use AI, I feel anxious and uneasy"、モデレータ）
- 解析手法: SmartPLS 4.0 による構造方程式モデリング（PLS-SEM）、5,000 ブートストラップサンプルの並行媒介分析、モデレーション検定
- 主要結果（報告された数値を逐語で）: H1（誤情報リスク→AI 不安）β=0.153, p=0.004；H2（プライバシーリスク→AI 不安）β=0.316, p<0.001；H3（誤情報リスク→誤情報疲労）β=0.469, p<0.001；H4（プライバシーリスク→プライバシー疲労）β=0.420, p<0.001；H5（誤情報疲労→AI 不安）β=0.196, p=0.003；H6（プライバシー疲労→AI 不安）β=0.213, p<0.001；H9（AI 不安→利用中止意図）β=0.195, p<0.001；H10（AI 依存のモデレーション）β=−0.107, 95%CI[−0.190, −0.016], p=0.015。媒介効果: 誤情報疲労経由 indirect β=0.092, 95%CI[0.033, 0.160], p=0.004, VAF=37.6%；プライバシー疲労経由 indirect β=0.089, 95%CI[0.042, 0.140], p<0.001, VAF=22.0%。適合度: SRMR=0.075（<0.08 の閾値以下）。R²: 誤情報疲労 0.220、AI 不安 0.471、利用中止意図 0.223。信頼性: Cronbach's α はすべての変数で 0.8 超、AVE はすべて 0.5 超、CR はすべて 0.7 超、HTMT はすべて 0.90 未満
- 著者自身が述べる限界（逐語、40 語以内に短縮引用）: "The empirical analysis relies on cross-sectional survey data, which is susceptible to biases...and cannot definitively infer causality"／"This study focuses exclusively on generative AI scenarios, which constrains the generalizability"／"The sample consists primarily of young, highly educated users; caution is therefore warranted when generalizing...to populations with lower AI literacy"
- 倫理承認・同意（本文の方法節と宣言欄、逐語）: 倫理 = "Ethical review and approval was not required for the study on human participants in accordance with the local legislation and institutional requirements."；同意 = "The participants provided their written informed consent to participate in this study."（方法節と宣言欄が別々かどうかは今回の抽出では区別できておらず、同一文として提示された可能性がある＝未確認）
- 事前登録・データ/材料公開・資金・利益相反: データ公開 = "The datasets presented in this study can be found in online repositories. The names of the repository/repositories and accession number(s) can be found in the article/supplementary material."（リポジトリ名自体は未確認）。資金 = "This research was funded by the Scientific Research Startup Project of Guangdong Ocean University (grant no. 060302142609)."。利益相反 = "The author(s) declared that this work was conducted in the absence of any commercial or financial relationships that could be construed as a potential conflict of interest."。事前登録: 本文中に言及なし（Not mentioned in provided content — 未確認）
- 設計別チェック（A: 横断研究、全文取得済みのため個別判定）:
  1. 標本の組入れ基準が明確か: Unclear — 抽出結果に明示の組入れ/除外基準の記述なし（500件→426件の「有効」判定基準の詳細が今回の抽出に出てこず、原文該当箇所は読んでいない）
  2. 対象者と場が詳しく記述されているか: Yes（一部） — 性別比・年齢層・学歴は判明（女性65.3%/n=278, 男性34.7%/n=148；81.7%が25歳以下；72.1%が学部卒）。ただし国・地域・調査期間の明記は未確認
  3. 曝露（説明変数）が妥当・信頼できる方法で測られているか: Yes — 既存尺度（Roozenbeek et al. 2022; Featherman & Pavlou 2003 等）を改変使用と明記
  4. 状態の測定に客観的・標準的な基準が使われているか: Unclear — 自己報告尺度のみで客観的基準の言及なし
  5. 交絡因子が特定されているか: Unclear — 抽出結果に交絡因子の明示的検討の記載なし
  6. 交絡への対処が述べられているか: Unclear — 同上
  7. アウトカムが妥当・信頼できる方法で測られているか: Yes — AVE>0.5, CR>0.7, HTMT<0.90 などの測定特性が報告されている
  8. 統計解析は適切か: Yes（横断データからの因果主張には著者自身が限界として言及） — PLS-SEM・ブートストラップ・適合度指標（SRMR）が報告されている
- 気づいた内部不整合: 特になし（抄録の N=426、抽出本文の N=426 が一致）

---

## 全体メモ（アクセス手段別の到達状況）
- ScienceDirect（Elsevier, AF001/AF002/AF003/AF004/AF034）: すべて自動アクセスで 403／Incapsula・PerimeterX の CAPTCHA。ライセンスが gold OA（AF001, AF034）であっても bot 検知の壁は同じで、内容には到達できなかった
- PubMed（AF004, AF034）: reCAPTCHA チャレンジページのみでアブストラクトも読めず。ただし Europe PMC REST API 経由でメタデータ（AF004 は抄録全文含む）は取得できた
- ACM DL（AF003）: 403
- SMU institutional repository（AF001）: Incapsula にブロックされ空応答
- Frontiers（AF005）: 正常にアクセス可能・全文取得
- ResearchBox（AF001）: 正常にアクセス可能（事前登録・データファイルの一覧のみ、項目文自体は非表示）
