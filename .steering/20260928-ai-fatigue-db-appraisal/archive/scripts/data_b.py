# Claude 再評価データ（後半: AF013–AF034）
from data_a import R

NOGSE = dict(reg="未登録", use="—", check="—", impl="—")
TA_EXCL = "（題名・抄録段で除外）"

def bg(**kw):
    base = dict(use="背景保持", state="方法論評価済み（背景）", url2="", need="—", gse=NOGSE, dom=None,
                ta="除外", ft=TA_EXCL, final="除外", ftstat="対象外", qa="対象外", next="—")
    base.update(kw)
    return base

R["AF013"] = bg(tier="背景（E4）", scope="AI 疲労の概念を扱うナラティブレビュー（導入圧力・組織・言説への疲労を含む）",
    level="本文関連箇所確認", next="引用元の実証性を遡る。相互作用中の疲労と、AI 導入・言説への疲労を分けて抽出。",
    url="https://ijahss.net/assets/files/1755327497.pdf", loc="PDF（8 頁）Abstract, Methodology, Figure 1",
    basis="一次研究でない（E4）。", route="サブエージェントが PDF 全文から抽出",
    design="ナラティブレビュー＋テーマ統合", n="採択件数の記載なし（参考文献は約 30 件）",
    strengths="情報源（Google Scholar・Scopus・ResearchGate・PubMed・IEEE Xplore）と検索語を明記。限界で出版バイアスに言及。",
    concerns="検索式・検索日・採択件数・PRISMA 図・研究の質評価がない。学術文献と業界資料が混在。資金・COI・データの宣言がない。",
    cite="先行する概念整理として。頻度・効果の根拠にしない。", need="引用元の遡及。",
    url2="https://doi.org/10.56734/ijahss.v6n8a7", jbi="D: Y=1,4,8,11 / N=3,5,6,7 / U=2,9,10",
    diff="一致。宣言欄が無いことを追加。", reason="E4（既存レビュー・背景として保持）",
    memo="背景（既存レビュー）。GSE [P361]。",
    gse=dict(reg="[P361]（active）", use="生成的返権論 §6.3：AI 疲労を technostress・組織設計の問題として扱う視角。",
        check="GSE の注記（体系的レビューでも因果研究でもない）は一次（検索日・件数・質評価なし）と一致。", impl="—"))

R["AF014"] = bg(tier="背景（E4）", scope="AI 疲労と精神的健康の文献レビュー（職場中心）",
    level="本文関連箇所確認", next="採択件数（22 と 30）を著者に照会。引用する場合は参考文献の原著を個別に確認。",
    url="https://apcz.umk.pl/QS/article/download/70890/46360/235124",
    loc="出版社 PDF（20 頁）Abstract, Introduction, §3, §5, §8.2, Disclosure。Crossref と DOI システム",
    basis="一次研究でない（E4）。", route="メインが出版社 PDF で件数と DOI 表記を確認し、Crossref と DOI システムで登録を確認",
    design="文献レビュー（著者表記『Comprehensive Literature Review』）",
    n="★ 抄録『22 studies』・参考文献 22 件に対し、本文は 3 箇所で『30 studies』",
    strengths="問いを 3 つ明記。限界（縦断・介入・一般化・測定の標準化の欠如）を具体的に列挙。",
    concerns="検索の情報源・検索式・検索日の記載が一切ない。採択件数が 22 と 30 で食い違う。質評価なし。★ PDF に印字された DOI（10.12775/QS.2026.55.70890）は未登録で解決しない。登録 DOI は DB の 10.12775/QS.2026.54.70890（Crossref 上の巻は 55）。",
    cite="引用追跡の手がかりとしてのみ。内容を実証的な結論に転用しない。", need="件数の照会。",
    url2="https://doi.org/10.12775/QS.2026.54.70890", jbi="D: Y=1,11 / N=3,5,6,7,9 / U=2,4,8,10",
    diff="GPT の I10（参考文献の書誌の要照合）に加え、件数 22／30 と PDF の DOI 誤記（未登録）を新たに確認。DB の DOI（54）は登録済みで正しい。",
    reason="E4（既存レビュー・背景として保持）", memo="背景（既存レビュー）。引用追跡用。")

R["AF015"] = bg(tier="背景（E4）", scope="AI テクノストレスと人材開発介入のシステマティックレビュー",
    level="抄録・公開要約確認", state="詳細評価保留", next="最終版の公開後に方法・採択研究を確認。",
    url="https://link.springer.com/article/10.1007/s44163-026-01855-3",
    loc="Springer ページの抄録（ブラウザ・2026-09-28・受理原稿の表示あり）",
    basis="一次研究でない（E4）。", route="メインがブラウザで抄録を確認（本文はログイン壁で取得不可）",
    design="SLR（Scopus 単独）＋ VOSviewer の共語分析", n="125→36（2020〜2025 年・英語・査読誌・2026 年 1 月検索）",
    strengths="検索日・期間・件数を抄録で明記。", concerns="単一データベース。介入の有効性の根拠の強さは本文未確認。受理原稿の段階。",
    cite="AI テクノストレスと職場介入の概観として。", need="本文。", jbi="D: 抄録のみ（全項目 Unclear）",
    diff="GPT の記載（2020–2025 年・36 文献・Scopus 125 件）を抄録で支持。検索は 2026 年 1 月と追加確認。",
    reason="E4（既存レビュー・背景として保持）", memo="背景（既存レビュー）。")

R["AF016"] = bg(tier="背景（E4）", scope="教育での生成 AI と認知負荷（疲労ではない）",
    level="本文関連箇所確認", next="引用する結果ごとに負荷の指標・比較群を確認。",
    url="https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2026.1921504/full",
    loc="Frontiers HTML Methods, Results, Limitations（全般的負荷の内訳は検証担当が逐語確認）",
    basis="一次研究でない（E4）。", route="サブエージェント（WebFetch の要約経由で、逐語は未照合）",
    design="SR（WoS SSCI の Education カテゴリ・2026 年 6 月検索）・記述的エビデンスマップ", n="139→39（DB 経由 37＋後方引用 2）",
    strengths="14 次元の二重コーディングと κ、PRISMA 図。メタ分析を避けた理由を明記。",
    concerns="単一 DB・英語のみ。研究単位のバイアス評価なし・出版バイアスの評価なし（著者が明記）。採択研究で疲労を測ったものは特定できず。",
    cite="認知負荷が下がる・変わらない条件の背景として。負荷の低下を疲労の低下と読み替えない。",
    jbi="D: Y=1,2,3,6,7,8,11 / N=5,9 / U=4,10",
    diff="一致（全般的負荷 22 研究：低下 11・差なし 5・増加 2・方向比較なし 3・質的報告 1）。検証担当が逐語で確認。",
    reason="E4（既存レビュー・背景として保持）", memo="背景（既存レビュー）。",
    gse=dict(reg="未登録", use="—", check="—",
        impl="GR-H11（負荷の最小化を普遍的な善にしない）と、『負荷の低下≠疲労の低下』の区別に使える背景。"))

R["AF017"] = bg(tier="背景（E4）", scope="AI ストレッサーの分類（疲労状態とは区別）",
    level="本文関連箇所確認", next="本文が燃え尽き・消耗との関連を記述する一次研究（AF019 を除く 4 件・各研究の測定は未確認）を引用追跡（検索漏れ候補に記載）。",
    url="https://ceur-ws.org/Vol-4134/paper2.pdf", loc="CEUR PDF（25 頁）Abstract, §2.1–2.5, Figure 1, Limitations",
    basis="一次研究でない（E4）。", route="サブエージェントが PDF 全文から抽出",
    design="SLR（Scopus 単独・2025-03-07 検索・PRISMA 2020）・ナラティブ統合", n="1333→66（量的 40・質的 9・混合 6・概念 11）",
    strengths="完全な検索式・検索日・組入れ基準・PRISMA 図を報告。限界を率直に記述。",
    concerns="単一 DB・参考文献の手作業探索なし。一次スクリーニングは第 1 著者（『by the first author』）、抽出は 1 名の著者（『one author performed the primary extraction』）。抄録は『正式なバイアス評価ツールは用いていない』、本文 2.5 節は証拠の強さを strong／moderate／weak で格付けしたと記す（非公式な評価）。",
    cite="ストレッサーの分類と引用追跡に。", url2="https://urn.fi/URN:NBN:fi:tuni-202601121319",
    jbi="D: Y=1,2,3,8,10,11 / N=4,5,6 / U=7,9",
    diff="一致。単一評価者であることと、本文が燃え尽き・消耗との関連を記述する一次研究 5 件（うち 1 件は AF019・各研究の測定は未確認）を追加。",
    reason="E4（既存レビュー・背景として保持）", memo="背景（既存レビュー）。DOI なし（URN）。",
    gse=dict(reg="未登録", use="—", check="—",
        impl="新しいストレッサー『自律性の喪失』は GSE の権限台帳と対応。Tarafdar et al. 2007（GSE [P367]）と同じ系譜。"))

R["AF018"] = bg(tier="背景（E4）", scope="AI 対話システムへの過依存と認知能力（疲労は扱わない）",
    level="本文関連箇所確認", next="主張ごとに一次研究を遡る。",
    url="https://slejournal.springeropen.com/counter/pdf/10.1186/s40561-024-00316-7.pdf",
    loc="出版社 PDF（37 頁）Methods, Figure 1, Limitations, Declarations",
    basis="一次研究でない（E4）。", route="サブエージェントが PDF 全文から抽出",
    design="SLR（ProQuest・IEEE Xplore・ScienceDirect・WoS／2017〜2023 年）", n="70→研究 9 件＋関連報告 5 件（本文は『14』と表記）",
    strengths="組入れ・除外基準を表で明示、PRISMA 図。",
    concerns="限界の節は『14 databases』と書くが実際は 4 DB。COI 声明が二重否定（『no non-competing interests』）。倫理欄が未来形（『intends to submit』）。批判的吟味のツールなし。スクリーニングが単独か 2 名かは判別できない（『dual screening process』の記述と、共著者の貢献は校閲のみという記載が併存）。疲労への言及がない。",
    cite="過依存と疲労を区別する背景として。", jbi="D: Y=1,2,11 / N=5,7,9 / U=3,4,6,8,10",
    diff="DB の『14 文献』は研究 9＋報告 5。内部不整合 3 件を新たに確認。",
    reason="E4（既存レビュー・背景として保持）", memo="背景（既存レビュー）。")

R["AF019"] = dict(
    tier="中心-B", use="中心候補", scope="AI テクノストレスと仕事の情緒的消耗（MBI-GS）",
    level="本文関連箇所確認", state="領域別暫定評価",
    next="各時点の脱落と解析対象、AI テクノストレスの項目、Bayesian SEM の統制変数を確認。",
    url="https://www.sciencedirect.com/science/article/pii/S0268401225000192",
    loc="ScienceDirect 全文（ブラウザ・2026-09-28・OA）§3 方法（参加者・手続き・測定）, §6.3 限界",
    basis="情緒的消耗を T2 に MBI-GS の情緒的消耗 5 項目（『I feel burned out from work』）で測定し、T1 の AI テクノストレスが予測 → 疲労を測定し、AI 由来の要求と関係づける一次研究（中心-B）。",
    route="メインがブラウザで出版社ページの全文を部分的に読解",
    design="3 時点の時間差調査（1 週間を超える間隔・原文『intervals over a week』）・Bayesian SEM",
    n="600 有効回答（365 社・台湾の AI 導入上場企業・男女各 50%・平均 39.2 歳）。2023 年 10〜12 月・調査会社",
    strengths="要求（AI テクノストレス）と資源（AI 効力感・生成 AI）の両経路、時点の分離、倫理承認番号（REC 202310HS020）、回答率（26.8%）の開示。消耗は標準尺度（α=.93）。",
    concerns="時間差は 1 週間を超える程度で、交差遅延でも無作為化でもない自己報告。消耗は仕事一般の消耗で、AI との相互作用に帰属しない。生成 AI の変数は自由記述を独立評定者がコード化（§6.3）。",
    cite="AI 由来の要求と仕事の消耗の関連、資源経路との対比として。AI 疲労そのものの証拠とは区別する（中心-B）。",
    need="脱落・統制変数。", url2="https://scholar.lib.ntnu.edu.tw/en/publications/insights-from-the-job-demandsresources-model-ais-dual-impact-on-e/",
    jbi="A（時間差調査に準用）: Y=1,2,4,7 / U=3,5,6,8（部分読解）",
    diff="★ GPT は背景保持（境界例・要協議）。本評価はプロトコル §2 の規則で中心-B とした（疲労を標準尺度で測定し、AI 由来の要求と関係づけている）。台湾・調査会社・回答率・倫理番号を一次で追加。",
    ta="含める", ft="含める", final="含める", reason="", ftstat="進行中", qa="完了（AI予備・部分読解）",
    memo="中心-B（GPT と不一致）。AF017 の採択研究にも含まれる。",
    dom=dict(
        sel="一部懸念：調査会社のパネル、男女同数の割付、回答率 26.8%。",
        mea="一部懸念：消耗は MBI-GS で標準的だが、仕事一般の消耗で AI に帰属しない。",
        tim="一部懸念：1 週間を超える時間差で予測変数と結果を分離。交差遅延・無作為化ではない。",
        con="判定不能：統制変数の節を未読。", ana="判定不能：Bayesian SEM の詳細を未照合。",
        tra="低懸念：倫理承認番号・回答率・OA。",
        summ="選択△ 測定△ 時間△ 交絡? 解析? 透明○", cite="AI 由来の要求と仕事の消耗の関連として。"),
    gse=dict(reg="未登録", use="—", check="—",
        impl="生成 AI が技術ストレスの負の効果を和らげるという資源側の所見は、AI 疲労の一方向の説明に偏らない反例。二重台帳で『負担だけでなく資源も数える』論点に対応。"),
)

R["AF020"] = bg(tier="背景（E2）", scope="AI 過信の抑制（cognitive forcing）と主観評価（疲労は未測定）",
    level="本文関連箇所確認", url="https://arxiv.org/pdf/2102.09692",
    loc="arXiv 著者版 PDF（21 頁）§3–§5, Table 3。GSE の全文精読記録 [P127]",
    basis="疲労・消耗を測定していない（単項目の『Mental demand』＝『I found this task difficult』のみ）→ E2。",
    route="サブエージェントが arXiv 全文から抽出し、GSE の既存の精読記録（[P127]）と照合",
    design="オンライン実験（MTurk・条件のランダム割付・混合計画）", n="260 募集→199 解析（除外 61）",
    strengths="客観的な過信指標、条件間の比較、混合効果モデル。",
    concerns="疲労の測定なし。主観指標は単項目。単一の低リスク課題・LLM 以前の模擬 AI。",
    cite="過信を減らす摩擦と、主観的な複雑さ・選好とのトレードオフの背景として。",
    url2="https://doi.org/10.1145/3449287", jbi="C（準用）: Y=1,7,8,9,10,12,13 / U=2,3,11 / NA=4,5,6",
    diff="DB の要約『インターフェースの主観評価は低くなる傾向』は、著者自身の限界の記述『at the cost of reducing the perceived usability』と一致する。★ ただし GSE の全文精読（[P127]）では、条件間で有意だったのは System Complexity のみ（2.64→2.95, p=.002）で、Mental demand は CFF 2.84 ≈ SXAI 2.86（no-AI 3.66 より低い）、Preference・Trust の群間差は非有意。精密化を提案する。",
    reason="E2（疲労を測定していない・背景として保持）", memo="背景（隣接研究）。",
    gse=dict(reg="[P127]（active）＝[V37]（[P338] は重複登録の tombstone）",
        use="摩擦で過信を減らす設計の正典。効果と嫌悪が同じダイヤル、Need for Cognition による受益の格差。",
        check="GSE の精読記録と抽出が一致（N=199、Mental demand の周辺平均）。",
        impl="GSE の文献カード（docs/literature/20260724-friction-retention-and-overreliance-evidence.md）は、2026 年の部分的な非再現の報告として Arun & Fischer 2026（doi:10.1145/3808045.3808049・書誌は Crossref で確認）を挙げる（選択的な摩擦は主観的負荷のみ増加）。★ 本文は未照合なので、DB には『関連報告（本文未照合）』として追記する候補。"))

R["AF021"] = bg(tier="背景（E2）", scope="ChatGPT 利用と認知負荷・診断技能の RCT（疲労は未測定）",
    level="抄録・公開要約確認", state="詳細評価保留", next="引用する場合は群別脱落・ITT・試験登録を全文で確認。",
    url="https://doi.org/10.1016/j.nepr.2026.104949", loc="Europe PMC の抄録・Crossref・Unpaywall",
    basis="疲労を測定していない（認知負荷のみ）→ E2。", route="サブエージェント（抄録）",
    design="3 群ランダム化比較試験（事前事後・並行群・3 週間）", n="108 無作為化→91 解析",
    strengths="ランダム化で、個人学習・個人＋ChatGPT・仲間＋ChatGPT を比較。",
    concerns="本文未取得（購読制）。群別脱落・ITT・登録は未確認。公開日の表記が索引間で不一致（Unpaywall 2026-08-20、Europe PMC 2026-08、Crossref 2026-10）。",
    cite="総認知負荷が全群で下がったことの背景として（群間の検定結果は抄録に無い。p=.936 は診断技能の交互作用。疲労の軽減とは書かない）。",
    url2="https://pubmed.ncbi.nlm.nih.gov/42636698/", jbi="C: 全項目 Unclear（抄録のみ）",
    diff="一致。公開日の不一致を追加。", reason="E2（疲労を測定していない・背景として保持）", memo="背景（隣接研究）。")

R["AF022"] = bg(tier="背景（E2）", scope="ChatGPT 利用の先行要因と結果（疲労は未測定）",
    level="本文関連箇所確認", url="https://link.springer.com/article/10.1186/s41239-024-00444-7",
    loc="Springer 全文 Study 1／2 Methods, Measures, Ethics declarations",
    basis="fatigue・burnout・exhaustion の語が本文に無い → E2。", route="サブエージェントが全文から抽出",
    design="Study1 尺度開発（EFA）＋ Study2 3 波の時間差調査（1〜2 週間間隔）・PLS-SEM", n="Study1 165／Study2 約 900 接触→494 解析（合算しない）",
    strengths="利用尺度の内容妥当性（専門家 5 名）と EFA。Study2 は時点を分離。倫理承認の記載あり。",
    concerns="疲労を測らない。記憶喪失尺度（3 項目）の出典なし。成績は自己報告の GPA。統制変数なし。著者も逆因果を排除できないと明記。",
    cite="学業負担・時間圧力と ChatGPT 利用の関連の背景として。", jbi="A: Y=1,3,7,8 / N=5,6 / U=2,4（5・6 は判断 11 の規則）",
    diff="一致。", reason="E2（疲労を測定していない・背景として保持）", memo="背景（隣接研究）。")

R["AF023"] = bg(tier="背景（E2）", scope="生成 AI 利用時の批判的思考と主観的努力の再配分（疲労は未測定）",
    level="本文関連箇所確認", url="https://www.microsoft.com/en-us/research/wp-content/uploads/2025/01/lee_2025_ai_critical_thinking_survey.pdf",
    loc="著者公開 PDF（23 頁）§3.2–3.3, §4, §6.3",
    basis="疲労を測定していない（『fatigue』は質問順序の効果についての注記のみ）→ E2。",
    route="サブエージェントが全文から抽出し、GSE [P365] と照合",
    design="横断オンライン調査（Prolific）・事例を参加者に入れ子にしたランダム切片モデル＋自由記述の質的分析", n="333→319 人、957→936 事例",
    strengths="入れ子構造を考慮、98 仮説に Benjamini–Hochberg 補正、限界 5 点を明記、倫理審査の承認を記載。",
    concerns="主観的・回顧的な努力の自己報告。英語話者・若年・技術に通じた層への偏り。",
    cite="批判的思考が検証・統合・監督へ移るという記述の背景として。", url2="https://doi.org/10.1145/3706598.3713778",
    jbi="A: Y=1,2,3,5,6,8 / U=4,7", diff="一致（936 は事例数、参加者は 319）。",
    reason="E2（疲労を測定していない・背景として保持）", memo="背景（隣接研究）。",
    gse=dict(reg="[P365]（active）", use="生成的返権論 §6.3：批判的思考は消えるのでなく、検証・応答の統合・タスクの監督へ移る。",
        check="GSE の記述と一致（319 人・936 事例）。", impl="—"))

R["AF024"] = bg(tier="境界（保留）", use="保留", state="範囲の判断待ち",
    scope="生成 AI の誤用と『学習バーンアウト』（代理項目は GenAI に帰属した過負荷と関心・意欲の低下。情緒的消耗の項目はない）",
    level="本文関連箇所確認", url="https://www.mdpi.com/2227-9709/12/2/51",
    loc="MDPI ページ（Wayback 保存）§1 定義, §2, Table 1（全 20 項目をメインが確認）, 宣言欄, Data Availability",
    basis="★ 境界例: 学習バーンアウトを『emotional exhaustion, loss of motivation, and diminished interest』と定義し、GenAI に帰属した過負荷（項目 2『overwhelmed by the amount of information provided by GenAI』・5『After using GenAI, I often feel mentally overloaded』）と関心・意欲の低下（19・20）を代理として測る。情緒的消耗を問う項目はない。プロトコル §1 の概念は動機面の消耗を含むため E2（疲労を測っていない）とは言い切れず、中心とも言い切れない → 範囲の判断を人間の判定者に委ねる。",
    route="サブエージェントが全文（Wayback）から抽出、メインが Table 1 の全 20 項目と定義を確認",
    design="事例研究：自作質問紙（横断）＋年度コホートの比較（非ランダム化）", n="質問紙 143。コホート比較の人数は記載なし",
    strengths="倫理承認番号（SK-2024-SH-058）、データを GitHub で公開、資金 4 件を開示。",
    concerns="情緒的消耗の項目がなく、20 項目の多くは利用行動・依存・教員の役割。自作尺度（出典なし・構造的妥当性の検証なし・下位尺度 α=.759〜.877）。推測統計がほぼない。コホートは年度が違う非ランダム化の比較。",
    cite="含める場合も、GenAI に帰属した過負荷・関心の低下の記述的な結果として。学習バーンアウトの妥当な測定としては引用しない。", url2="http://web.archive.org/web/2025/https://www.mdpi.com/2227-9709/12/2/51",
    jbi="A: N=2,4,5,6 / U=1,3,7,8",
    diff="★ GPT は背景保持（境界例・要協議）。本評価も境界例と判断し、プロトコルの語彙で『保留』（範囲の判断を人間に委ねる）とした。初稿は E2 としたが、code-reviewer の指摘（AF007 の Cognitive Overload・Motivational Disengagement を AI 疲労として数えていることとの一貫性）を受け、Table 1 を一次で読み直して改めた。",
    ta="含める", ft="保留", final="保留", ftstat="進行中", qa="完了（AI予備）",
    reason="境界例（範囲の判断待ち・E コードではない）", memo="境界（保留）。GPT と相違（背景保持→保留）。")

R["AF025"] = bg(tier="背景（E4）", scope="AI 不安尺度（疲労の比較概念）", level="抄録・公開要約確認", state="詳細評価保留",
    url="https://doi.org/10.1080/10494820.2019.1674887", loc="OpenAlex の抄録・Crossref",
    basis="尺度の原著（E4）。", route="サブエージェント（抄録）", design="尺度開発・妥当性検証", n="301（抄録）",
    strengths="AI 不安を独立の構成概念として定義。", concerns="本文未取得で項目数・因子数は未確認。オンライン公開 2019-10-14、巻号 2022（30 巻 4 号）。",
    cite="AI 不安と AI 疲労の弁別に使う比較尺度として。", url2="https://eric.ed.gov/?id=EJ1345149",
    jbi="E: 抄録のみ", diff="一致。N=301 を抄録で追加。", reason="E4（尺度の原著・背景として保持）", memo="背景（尺度・理論）。")

R["AF026"] = bg(tier="背景（E4）", scope="ビデオ会議疲労尺度（AI ではない）", level="本文関連箇所確認",
    url="https://vhil.stanford.edu/sites/g/files/sbiybj29011/files/media/file/fauville-zef-chbr_2021.pdf", loc="著者公開 PDF（10 頁）",
    basis="尺度の原著（E4）。", route="サブエージェントが PDF 全文から抽出", design="尺度開発（項目生成→EFA→CFA）", n="395（MTurk）／130／2724（合算しない）",
    strengths="15 項目・5 因子、下位 α=.83〜.89・総合 .95、二次因子 CFA（CFI .944、RMSEA .086）、多様な成人標本での再検証で RMSEA .065。",
    concerns="RMSEA .086 はやや高い。会議の文脈で、AI への名称置換では内容妥当性は移らない。",
    cite="多次元のデジタル疲労尺度の構成・手順の比較に。", url2="https://doi.org/10.1016/j.chbr.2021.100119",
    jbi="E: 構造的妥当性・内的一貫性=報告あり", diff="一致（N を段階別に追加）。", reason="E4（尺度の原著・背景として保持）", memo="背景（尺度・理論）。")

R["AF027"] = bg(tier="背景（E4）", scope="一般 ICT のテクノストレスの生成要因・抑制要因", level="抄録・公開要約確認", state="詳細評価保留",
    url="https://doi.org/10.1287/isre.1070.0165", loc="OpenAlex の抄録", basis="尺度・理論の原著（E4）。", route="サブエージェント（抄録）",
    design="構成概念開発・横断調査・SEM", n="608", strengths="テクノストレスの生成要因と抑制要因を分ける古典的な枠組み。",
    concerns="本文未取得。生成 AI 以前の ICT の文脈。", cite="要求・資源・結果の理論的整理に。", jbi="E: 抄録のみ",
    diff="一致。", reason="E4（尺度・理論の原著・背景として保持）", memo="背景（尺度・理論）。",
    gse=dict(reg="関連: [P367] Tarafdar et al. 2007（同じ研究群の先行研究）", use="生成的返権論 §6.3：overload・invasion・complexity・uncertainty を設計・組織の条件として扱う。",
        check="—", impl="DB の尺度・理論に [P367]（Tarafdar et al. 2007, JMIS）を並べる候補。"))

R["AF028"] = bg(tier="背景（E4）", scope="一般疲労尺度（AI への帰属を測らない）", level="抄録・公開要約確認", state="詳細評価保留",
    url="https://pubmed.ncbi.nlm.nih.gov/12670612/", loc="PubMed の抄録。AF001 §5.1.2",
    basis="尺度の原著（E4）。", route="サブエージェント（抄録）・メインが AF001 本文での使用を確認",
    design="心理測定学的検証", n="未確認（抄録に数値なし）", strengths="10 項目・一因子の簡便な一般疲労尺度。",
    concerns="本文未取得。AI への帰属を測らない。", cite="一般疲労の比較尺度として。AF001 が収束妥当性の検討に FAS を使っている（AF001 §5.1.2）。",
    url2="https://www.sciencedirect.com/science/article/abs/pii/S0022399902003926", jbi="E: 抄録のみ",
    diff="一致。AF001 での使用を追加。", reason="E4（尺度の原著・背景として保持）", memo="背景（尺度・理論）。")

R["AF029"] = bg(tier="背景（E4）", scope="認知負荷尺度（疲労状態とは区別）", level="本文関連箇所確認",
    url="https://link.springer.com/content/pdf/10.3758/s13428-013-0334-1.pdf", loc="Springer 著者版 PDF（15 頁）",
    basis="尺度の原著（E4）。", route="サブエージェントが PDF 全文から抽出", design="尺度開発（PCA→CFA）・ランダム化実験",
    n="56／171・136・148／58（合算しない）", strengths="10 項目・3 因子（IL／EL／GL）、α=.81／.75／.82、CFA と実験で検証。",
    concerns="負荷であって疲労ではない。", cite="AI 研究の認知負荷指標の由来として。", url2="https://pubmed.ncbi.nlm.nih.gov/23572251/",
    jbi="E: 構造的妥当性・内的一貫性=報告あり", diff="一致。", reason="E4（尺度の原著・背景として保持）", memo="背景（尺度・理論）。")

def meth(**kw):
    kw.setdefault("use", "方法論保持"); kw.setdefault("tier", "方法論（E4）"); kw.setdefault("state", "方法論の適用範囲確認")
    kw.setdefault("reason", "E4（方法論・報告指針）"); kw.setdefault("memo", "方法論保持。")
    return bg(**kw)

R["AF030"] = meth(scope="スコーピングレビューの報告指針", level="本文関連箇所確認",
    url="https://eprints.whiterose.ac.uk/id/eprint/136633/1/PRISMA_ScR_Manuscript_July6th_clean_1_.pdf", loc="著者受理版 PDF（29 頁）・PRISMA 公式・EQUATOR",
    basis="報告ガイドライン。", route="サブエージェントが受理版の全文と公式ページを確認", design="報告ガイドライン（Delphi）", n="非該当",
    strengths="必須 20＋任意 2 項目、Delphi（合意 85%）で作成。",
    concerns="報告指針であり研究の質の尺度ではない。2026-09-28 時点で正式な改訂版（PRISMA-ScR 2.0 等）は公式サイト・EQUATOR で見当たらない（サブエージェントの WebFetch 要約経由）。",
    cite="本レビューの報告項目の整備に。", url2="https://www.equator-network.org/reporting-guidelines/prisma-scr/", jbi="非該当", diff="一致。")

R["AF031"] = meth(scope="スコーピングレビューの実施方法論（JBI）", level="抄録・公開要約確認",
    url="https://doi.org/10.11124/JBIES-20-00167", loc="Europe PMC の抄録・Crossref（全著者）",
    basis="方法論文献。", route="サブエージェント（抄録）・メインが Crossref で全著者を確認", design="方法論ガイダンス", n="非該当",
    strengths="JBI の手引きの 2020 年更新（国際科学委員会が承認）。", concerns="本文未取得。AF033 の本文によれば JBI の手引きも改訂中。",
    cite="計画・選定・抽出の手順に。", jbi="非該当",
    diff="★ 全著者 9 名を Crossref で確認: Micah D.J. Peters; Casey Marnie; Andrea C. Tricco; Danielle Pollock; Zachary Munn; Lyndsay Alexander; Patricia McInerney; Christina M. Godfrey; Hanan Khalil（DB は先頭 4 名のみ）。")

R["AF032"] = meth(scope="尺度の測定特性を評価するレビューの方法論（COSMIN）", level="本文関連箇所確認",
    url="https://link.springer.com/article/10.1007/s11136-018-1798-3", loc="Springer OA PDF（11 頁）",
    basis="方法論文献。", route="サブエージェントが PDF 全文から抽出", design="方法論ガイドライン", n="非該当",
    strengths="10 段階の手順で、測定特性を個別に評価して統合。", concerns="患者報告尺度の枠組みで、一般の AI 利用者の尺度には調整が要る。",
    cite="尺度の測定特性の整理に。", jbi="非該当", diff="一致。")

R["AF033"] = meth(scope="PRISMA-ScR の改訂に向けた方法論のスコーピングレビュー", level="本文関連箇所確認",
    url="https://pure.amsterdamumc.nl/ws/files/217632679/Updating-the-prisma-reporting-guideline-for-scoping-reviews.pdf", loc="機関リポジトリ PDF（15 頁）構造化抄録・Plain language summary・Introduction",
    basis="方法論文献。", route="サブエージェントが PDF 全文から抽出", design="スコーピングレビュー（報告指針の更新の準備）", n="8265 件をスクリーニング",
    strengths="37 の追加候補項目を抽出し、後続の Delphi を予定。",
    concerns="★ 構造化抄録『43 unique documents (13 overviews of ScRs and 30 guidance documents)』と平易な要約『47 research papers』で件数が食い違う（本文で確認）。完成した新版ではない。",
    cite="改訂の準備研究として。既存の PRISMA-ScR を置き換えた新版とは書かない。", url2="https://pubmed.ncbi.nlm.nih.gov/42107664/",
    jbi="非該当", diff="GPT の要照合点（43 と 47）を本文で確認。")

R["AF034"] = bg(tier="訂正（E4）", use="訂正連結", state="訂正内容確認済み",
    scope="AF004 への訂正通知（参考文献 2 件と、関連する背景引用 3 箇所）", level="本文関連箇所確認",
    url="https://www.sciencedirect.com/science/article/pii/S0001691826009807", loc="ScienceDirect の訂正通知本文（ブラウザ・2026-09-28・OA）",
    basis="訂正通知（E4・原著 AF004 に連結）。", route="メインがブラウザで訂正本文を確認", design="訂正通知", n="非該当",
    strengths="訂正の対象（Mun 2023・Paul et al. 2023 の DOI 照合の誤り）と修正後の文を明示。",
    concerns="著者は『研究デザイン・データ・解析・結果・解釈・結論には影響しない』と明記。★ ただし AF004 の交互作用の向きの矛盾（照合事項 C02）は訂正の対象外で、未解決。",
    cite="AF004 を引用するときは訂正後の版を参照する。独立研究として数えない。", url2="https://pubmed.ncbi.nlm.nih.gov/42225464/",
    jbi="非該当", diff="★ GPT は『参考文献のみの訂正と断定しない』として保留していた。本文で参考文献のみ（2 件・3 箇所）と確認し、保留を解消。",
    reason="E4（訂正通知・AF004 に連結）", memo="訂正連結。")


# design §4 の規則: 全文で JBI／COSMIN を埋めた件=完了（AI予備）、抄録のみ=進行中、方法論・訂正=対象外（判断 11）
for _k, _x in R.items():
    if _x["use"] == "背景保持":
        full = _x["level"] == "本文関連箇所確認"
        _x["qa"] = "完了（AI予備）" if full else "進行中"
        _x["ftstat"] = "進行中" if full else "入手不可"
