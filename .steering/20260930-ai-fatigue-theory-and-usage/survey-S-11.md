# S-11 「AI 疲労」の語の使われ方 —— 事実

> 取得日: 2026-09-30（日本時間 18:13＝`evidence/S-11/records_2026-09-30.json` の executed）。手順は `design.md` §0・§1（取得の前の 18:05 に固定・コミット `9fc6a8bc`）。
> ★ このファイルは事実だけを書く（論文に書いてあること）。語の用法の区分と定義文の案は別のファイル（`survey-S-11-ai-judgments.md`）にある。
> 生の結果（書誌だけ）: `evidence/S-11/records_2026-09-30.json`（取得）・`terms_2026-09-30.json`（ふるい）・`prompt_fatigue_trace_2026-09-30.json` と `_retry.json`（プロンプト疲れの概念分析を辿った記録）。抄録・本文は repo の外にだけ置いた。
> 対象は、判定者用ファイルの archive の写し（SHA-256 `6984472e…`）の DB 34 件と追加候補 225 件の計 259 件。

## 1. 取得の記録

| 情報源 | 抄録が取れた件数（259 件中） |
|---|---|
| OpenAlex | 222 |
| Semantic Scholar | 212 |
| Crossref | 172 |
| Europe PMC | 147 |
| **どれかで取れた** | **246** |

- 取得の例外（接続の失敗・429 の再試行の尽きなど）は 0 件。★ 400・404・410 の応答は「その情報源に記録なし」として扱い、件数としては残していない（`evidence/fetch_abstracts.py` の `get()`）。
- **抄録が取れなかった 13 件**（題名だけをふるいに当てた）: AF002・AF003・AF017（DOI なし）・AF034（訂正通知）・S02-04・S02-05・S14-43・S13-20・S08-03・S12-18・S12-21・S12-22・S12-23（DOI なし）。★ AF002（*Int J Inf Manage* 2026）と AF003（*Comput Hum Behav* 2026）は、4 つの情報源のどれにも抄録が無かった。
- DOI の無い 4 件のうち、S04-30 と S12-24 は Europe PMC で題名（S12-24 は前刷りの識別子）が一致し、抄録を使った。AF017・S12-23 は一致しなかった。
- DOI で引いた 7 件（AF026・S04-21・S04-36・S04-76・S04-80・S14-21・S14-36）で、情報源の題名が判定者用ファイルの題名と一致しなかった。Crossref と OpenAlex の題名で 1 件ずつ見ると、7 件とも同じ文献で、違いは HTML の実体参照（`&amp;`・`<scp>`）・綴り（assited／assisted）・言語（S04-76 はスペイン語の題名）・版による題名の違い（S04-36）だった。情報源の間で抄録の長さはほぼ同じだった。

## 2. 語形の件数（題名＋抄録・`design.md` §1.2 の正規表現）

| 記号 | 何を拾うか | 当たった記録 | 当たった語の例 |
|---|---|---|---|
| N1 | AI の語 ＋ 疲労の名 | 15 | AI fatigue・AI-induced fatigue・AI-related burnout |
| N2 | 疲労の名 ＋ 前置詞 ＋ AI の語 | 2 | Fatigue with Artificial Intelligence（AF010 の題名）・burnout associated with AI（S14-31） |
| N3 | プロンプト疲れ（英語） | 0 | — |
| N4 | 日本語 | 0 | — |
| N5 | 近接の語（数えるだけ） | 20（うち N5 だけの記録 19） | AI anxiety・AI technostress・AI-induced technostress・AI-related stress・AI-Stressors |

- **語（N1〜N4）を使う記録は 259 件中 16 件**。内訳は DB 8 件（AF001・AF006・AF007・AF008・AF009・AF010・AF013・AF014）と追加候補 8 件（S02-07・S02-08・S04-37・S15-15・S14-25・S14-31・S08-02・S08-03）。
- 16 件のうち、題名に語があるのは 11 件（AF001・AF006・AF007・AF008・AF009・AF010・AF013・AF014・S02-08・S08-02・S08-03）。S04-37・S15-15・S14-25・S14-31 は抄録にだけある。S02-07 は抄録にあり、題名は「AI Anxiety to Fatigue」（N5 と疲労の語が別の位置にある）。
- DB の「直接研究」12 件（AF001〜AF012）のうち、抄録で語を使わないもの: AF004（認知的疲労）・AF005（認知的疲労）・AF011（決定疲れ）・AF012。AF002・AF003 は抄録が取れず、題名に語は無い。
- N5 だけの 19 件: AF005・AF011・AF015・AF017・AF019・AF025・S12-03・S14-02・S14-03・S14-08・S14-19・S14-20・S14-22・S14-24・S14-26・S14-33・S14-39・S14-51・S14-52。

### 2.1 固定したふるいの外で、目で見て足した 3 件（`decisions.md` 判断 4）

固定した正規表現の後に、AI の語と疲労の名が 3 語以内に並ぶ句を抄録で目で見た。疲労の名を、原因を表す動詞・前置詞（caused by・brought by・elicited by）で AI に結ぶ句のある 3 件を「語を使う記録（補い）」として §3 に足した。

| 鍵 | 句 | 正規表現が拾わなかった理由 |
|---|---|---|
| AF024 | 題名 “Learning Burnout Caused by Generative Artificial Intelligence Misuse” | AI の語の一覧に「generative artificial intelligence」が無い |
| S02-12 | 抄録 “digital fatigue brought by AI” | 前置詞の一覧に「brought by」が無い |
| S14-04 | 抄録 “emotional exhaustion elicited by AI-associated technostressors” | 前置詞の一覧に「elicited by」が無い |

- 足さなかった句の型: 文脈を示す句（S14-20 “burnout in AI-integrated educational contexts”・S13-06 “burnout in AI-integrated customer service roles”）、変数を並べる句（“AI awareness and job burnout” など）、題名の問い（S13-13 “Can AI Save Us from Burnout?”）、AI の利用時の状態の比較（S04-25 “less burnout when using the AI scribe”）。

## 3. 語を使う記録で、語に意味を与える文（`design.md` §1.3）

- 意味を与える文: 語（またはそれを指す語）を含み、(a) 定義、(b) 何であるか・何から生じるかの言い換え、(c) 構成要素・次元の列挙、のどれかを述べる文。「多次元である」のような性質だけを述べる文は数えない。
- 抄録に無く、OpenAlex で無料の版がある記録は本文で探した。後の文に明示の定義（defined as・conceptualise as など）があれば「明示の定義」の欄に書いた。

| 鍵 | 記録 | 語形 | 意味を与える最初の文（逐語） | 種類 | 出どころ | 明示の定義・構成要素（後の文） |
|---|---|---|---|---|---|---|
| AF001 | Lau ほか 2026（*Comput Hum Behav Rep*, doi:10.1016/j.chbr.2026.101186） | AI fatigue | “to conceptualise AI fatigue as a multidimensional psychophysiological state that arises from sustained interaction with and exposure to AI technologies” | (a) | 本文 §2（抄録には無い） | 次の段落: “AI fatigue can be characterised by cognitive overload, emotional strain, and physical or sensory exhaustion, ultimately culminating in behavioural avoidance and disengagement.” |
| AF006 | Parreño ほか 2026（*IJLTER*, doi:10.26803/ijlter.25.3.29） | AI fatigue | “Although AI fatigue overlaps with digital fatigue, cognitive load, and academic burnout, it is positioned in this study as a context-specific experience associated with academic AI use.” | (a) | 本文 §1（抄録は “AI fatigue is multidimensional and unevenly experienced” だけ） | 続く文: “this study examines AI fatigue as students’ explicitly articulated experiences of cognitive, emotional, and motivational strain related specifically to AI-supported academic work” |
| AF007 | Miranda ほか 2026（*IJLTER*, doi:10.26803/ijlter.25.5.5） | AI fatigue | “identifies the dimensions that define AI fatigue as a form of strain arising from sustained academic use of AI tools” | (a) | 抄録 | 抄録: 5 つの次元 Cognitive Overload・Motivational Disengagement・Moral Unease・Physical Strain・Attentional Drift |
| AF008 | Soriano ほか 2026（*IAES Int J Artif Intell*, doi:10.11591/ijai.v15.i2.pp1963-1971） | AI-induced fatigue | “intensive AI use introduces a student-centered outcome that remains underexamined in empirical research, which few scholars describe it as AI-induced fatigue” | (b) | 本文 §1（抄録は語が出るだけ） | — |
| AF009 | SCOReD 2025（doi:10.1109/SCOReD68498.2025.11399092） | AI-induced fatigue | “AI-induced fatigue is multidimensional which involves emotional, technical, and behavioral components.” | (c) | 抄録 | 抄録: 3 因子 Cognitive-Emotional Fatigue・Tech-Clarity Fatigue・Passive Fatigue。抄録の最初の文は、学業で AI の道具を使うときの疲労を問いとする |
| AF010 | Triki & Turki 2025（*IJRISS*, doi:10.47772/IJRISS.2025.910000615） | AI fatigue・Fatigue with Artificial Intelligence | “AI fatigue unfolds along cognitive, emotional, relational, and ethical dimensions, leading in particular to information overload, feelings of dehumanization, and changes in strategies for interacting with technologies.” | (c) | 抄録 | 抄録の最初の文: AI の集中的な使用が、認知・情動・関係の疲労を生みうる（消費者とブランドのやり取り） |
| AF013 | Ragolane & Patel 2025（*IJAHSS*, doi:10.56734/ijahss.v6n8a7） | AI fatigue | “This paper conceptualises AI fatigue as a multidimensional condition arising from the interplay of technostress, cognitive overload, and emotional exhaustion, driven not only by constant AI use but also by the relentless pace, opacity, and unevenness of AI integration.” | (a) | 抄録 | — |
| AF014 | Sosiński & Piasecka 2026（*Quality in Sport*, doi:10.12775/QS.2026.54.70890） | AI fatigue | “This means workers feel stressed by the technology, overwhelmed by too much information, anxious about AI capabilities, and tired from constantly having to adapt to new systems.” | (b) | 抄録（前の文が「AI fatigue」と呼ばれるものを導入） | 抄録: “The biggest reason for AI fatigue is that it increases the workload, creating new tasks like monitoring the system instead of removing work.” |
| S02-07 | Kang & Li 2025（*J Bus Converg*, doi:10.31152/jb.2025.12.10.6.297） | AI fatigue | 抄録に意味を与える文なし（語は、3 つの前件〈AI による職の置き換えへの不安・AI の学習への不安・AI の成果の不確実さ〉と帰結をつなぐ媒介として出る） | — | 抄録 | 本文は無料の版なし（OpenAlex） |
| S02-08 | Nobles 2026（Zenodo, doi:10.5281/zenodo.22838191） | AI fatigue・artificial intelligence fatigue | “positioning artificial intelligence fatigue as an emerging multidimensional conceptual proposition at the intersection of technostress, digital fatigue, and burnout” | (b) | 本文（Zenodo の再現パッケージの原稿の写しの要旨。記録の説明文は論文の種別だけ） | 原稿 §AI Fatigue as an Emerging Construct: “AI fatigue is defined provisionally as cumulative cognitive, emotional, motivational, behavioral, and physical depletion associated with sustained interaction with AI-enabled systems and with the verification, disclosure, and self-regulation demands that those systems impose.” |
| S04-37 | *Front Psychol* 2026（doi:10.3389/fpsyg.2026.1859401） | AI fatigue | “AI Fatigue stems from cognitive overload sustained over time.” | (b) | 本文 §1（PMC の全文 XML。抄録は媒介変数として出るだけ） | 本文 §2.2.6: “AI fatigue can be related to the emotional and cognitive exhaustion experienced by users due to sustained interaction with AI-powered or digital technologies.” |
| S15-15 | Quan 2026（*Rev Artif Intell Educ*, doi:10.37497/rev.artif.intell.educ.v7ii.1413・ベトナムの大学生 30 名の面接） | AI fatigue | 抄録に意味を与える文なし（結論で、TAM が説明しないものの 1 つとして出る） | — | 抄録 | 本文は無料の版なし（OpenAlex） |
| S14-25 | *SAGE Open* 2025（doi:10.1177/21582440251400532） | AI-related burnout | 抄録に意味を与える文なし（最後の文に語が出るだけ） | — | 抄録 | 抄録の 2 文目: 大学教員が AI を職の役割への脅威と受け止めうることが燃え尽きを高めうる。本文は取れなかった（出版社のサイトが 403） |
| S14-31 | Sifat ほか 2026（*New Solutions*, doi:10.1177/10482911261474923） | burnout associated with AI | “5 domains of burnout: workload intensification through invisible labor, technostress driven by rapid technological change, an investigative burden that moves the faculty role from pedagogy toward surveillance, ethical strain within a policy vacuum, and disruption of professional identity” | (c) | 抄録（燃え尽きは「AI の導入と学術の公正の取り締まり」に伴うものとして書かれる） | — |
| S08-02 | RecalibrateGPT（arXiv 2026, doi:10.48550/arxiv.2609.00506） | AI fatigue | “their interfaces often devolve into a type → read → retype loop, creating conversational AI fatigue, cognitive load, and eventual task abandonment” | (b) | 抄録 | 抄録: 疲労の 4 類型（retyping・scanning・decision paralysis・context drift）。最後の文: “AI fatigue is not just a model-quality issue but an interaction-flow cost that interfaces can remove” |
| S08-03 | Anti-Design Approach in Countering AI Fatigue（*Int Des J* 2026, doi:10.21608/idj.2026.525979.1661） | AI fatigue（題名） | 抄録が無い（4 つの情報源のどれにも無い） | — | 題名 | 本文は無料の版なし（OpenAlex） |
| AF024（補い） | *Informatics* 2025（doi:10.3390/informatics12020051） | Learning Burnout Caused by Generative Artificial Intelligence Misuse | “This study explores the phenomenon of learning burnout among university students resulting from the misuse of GenAI in this context.” | (b) | 抄録 | 抄録: 質問紙の 5 つの次元（information overload and cognitive load・overdependence on technology・limitations of personalized learning・shifts in the role of educators・declining motivation） |
| S02-12（補い） | Alkhatib ほか 2026（doi:10.70670/sra.v4i1.1983） | digital fatigue brought by AI | “cognitive overload and digital fatigue brought by AI were observed to have adverse effects on student coping with academic problems” | (b) | 抄録 | — |
| S14-04（補い） | *Front Public Health* 2026（doi:10.3389/fpubh.2026.1695066） | emotional exhaustion elicited by AI-associated technostressors | “predict work disengagement behavior via the emotional exhaustion elicited by AI-associated technostressors” | (b) | 抄録（金融の専門職 285 名・4 時点の縦断） | — |

- 本文の出どころ: AF001 は研究者の Downloads にある出版社版 PDF（SHA-256 `c023b466…`・A 群の S-08 と同じ写し。出版社のサイトは 403、NTU・SMU の機関リポジトリの版は取れなかった）。AF006・AF008 は出版社の PDF。S02-08 は Zenodo の再現パッケージの原稿の写し（docx）。S04-37 は Europe PMC の全文 XML（PMC13290586）。
- AF001 の本文は、上の定義に続けて、AI 疲労に固有の負担を “the ongoing verification and calibration work required when collaborating with a system whose outputs are variable, revisable, and not fully predictable” にあると書く（§2 の隣の構成概念との区別の段落）。
- 本文を取れなかった・無料の版が無いもの（4 件）: S02-07・S15-15・S14-25・S08-03。

## 4. 一般の構成概念の語（題名＋抄録・`design.md` §1.2）

| 語の区分 | 語を使う記録（16 件）のうち ＋ 補い（3 件）のうち | それ以外（240 件）のうち |
|---|---|---|
| 燃え尽き（burnout） | 4 ＋ 1（AF024） | 108 |
| 情動的消耗 | 1 ＋ 1（S14-04） | 30 |
| 消耗（exhaustion） | 2 ＋ 1（S14-04） | 49 |
| 疲労（fatigue・語を使う記録では語そのものを含む） | 14 ＋ 1（S02-12） | 59 |
| 精神的・認知的疲労 | 1 ＋ 0 | 9 |
| 決定疲れ | 0 ＋ 0 | 5 |
| テクノストレス | 5 ＋ 1（S14-04） | 23 |
| 認知負荷 | 6 ＋ 2（AF024・S02-12） | 25 |
| 情報過多 | 2 ＋ 1（AF024） | 3 |
| 負担（strain） | 6 ＋ 0 | 13 |
| 作業負荷（workload・NASA-TLX） | 3 ＋ 1（S02-12） | 40 |
| 疲れ（tired） | 2 ＋ 0 | 1 |

- ★ 上の表の「それ以外」の列は、`evidence/S-11/terms_2026-09-30.json` の `count_general_not_uses_term`（補いを分ける前の 243 件で数えた値）から、補いの 3 件の分を引いた値（`decisions.md` 判断 4）。
- 抄録があり、上の語がどれも出ない記録は 25 件（方法論の 4 件・記録の負担や時間だけを測る記録 など）。「負担（burden）」の語は区分に入れていない。
- 「疲れ（tired）」の正規表現は左の境界を持たない（retired なども当たりうる）。当たった 3 件の抄録の文字列は、AF006「mental tiredness」・AF014「tired from」・S15-07「Psychosomatic tiredness」で、retired などは無かった（抄録で確かめた）。

## 5. サーヴェイで記録した用法の例（259 件の外を含む）

| 記録 | 語 | 何を指すか（出どころに書いてあること） | 出どころ |
|---|---|---|---|
| Synthetonia: Tonal Strain as a Candidate Facet of AI Fatigue（Zenodo 2026, doi:10.5281/zenodo.22566309） | AI fatigue・Synthetonia | 立場表明の論文。既存の尺度は “interaction cost: volume of generated output, the burden of verification, and prompt iteration” を測るとし、会話 AI の単調な文体に長くさらされることによる飽き（Synthetonia）を別の源として提案する | Zenodo の記録の説明文（2026-09-30 に読み直した）・A 群の `survey-S-08.md` §6 |
| A Control-Theoretic Approach to GenAI Fatigue（Zenodo 2025, doi:10.5281/zenodo.17772700） | GenAI Fatigue | 説明文は GenAI Fatigue を “the measurable degradation in recall and contextual fidelity within long, multi-turn histories” と書き、LLM の応用の側の問題として扱う | 同上 |
| 医学教育 2026（doi:10.11307/mededjapan.57.3_195・候補 S12-21） | 評価疲れ | 医学教育の分野別評価で、評価を担う側の組織・人が疲れること。LLM による判定を人の判定と比べた | A 群の `survey-S-12.md`（J-STAGE の抄録。4 つの情報源には抄録が無かった） |
| 人工知能学会 全国大会 2025（doi:10.11517/pjsai.JSAI2025.0_2P1OS2605） | 精査疲れ | 偽情報・誤情報の広がる情報環境で、情報を精査し続けることへの疲れ（理論的な発表） | 同上 |
| 公研 2026（雑誌のインタビュー記事） | 「それっぽい嘘」に疲弊 | 生成 AI のもっともらしい嘘への対応で、研究者の側が疲弊する（題名） | 同上（題名だけ） |

## 6. プロンプト疲れの概念分析（検索漏れ候補 No.128・129）

- Zenodo の記録 2 件（`21384564`・`21384565`）は同じ概念 DOI（`10.5281/zenodo.21384564`）の版で、題名は “Supplementary Materials for: A Concept Analysis of Prompt Fatigue in Generative-AI-Supported Learning”・公開 2026-07-15・資料の種別は publication。**関連の識別子（本体の論文への参照）は無く、説明文は空**だった。
- Crossref の題名の検索（`Concept Analysis of Prompt Fatigue`・上位 5 件）は、看護の疲労の概念分析 4 件とパンデミック疲れの概念分析 1 件で、本体は無かった。
- Semantic Scholar の題名の検索は、2 回（18:28・18:35）とも 429 で使えなかった。
- ⇒ **本体の論文は辿れなかった**（259 件にも無い）。

## 7. 限界（事実として）

- ふるいは題名と抄録に当てた。本文でだけ語を使う記録は数えていない（例: S04-37 は抄録では媒介変数の名として出るだけで、意味を与える文は本文にある）。
- 抄録が取れなかった 13 件は題名だけを見た。DB の AF002・AF003 はここに入る。
- 語形の正規表現は取得の前に固定した。固定の外の語形は §2.1 の目で見た確認（AI の語と疲労の名が 3 語以内に並ぶ句）だけで、それより離れた書き方は見ていない。
- 日本語の記録の多く（S12 の日本語の論文）は 4 つの情報源に抄録が無く、N4 は 0 件だった。日本語の用法は §5 の A 群の記録による。
