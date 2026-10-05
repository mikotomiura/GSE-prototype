# 重要な設計判断

★ 2026-09-27 の grill（研究者との対話）で確定した。前提の調査は同日セッションの論文化可能性調査。

## 判断 1: 第一投稿先 = Behavior Research Methods (BRM)

- **背景**: 国内学会は研究者判断で見送り。国際で「IME 観測ツール ＋ 精度評価」を受ける場が要る。
- **選択肢**: A: BRM（手法・ツール誌・随時投稿） / B: Journal of Writing Research（打鍵ログ研究の中心誌） / C: CHI 2027 Posters/LBW
- **採用**: A
- **理由**: 締切がなく分量の制約も緩いので、両 OS・再構成攻撃・実行コストを 1 本に収められる。打鍵ログツール論文の前例がある系統。
- **トレードオフ**: 査読に数か月かかる。精度評価と再現性を厳しく問われる。
- **影響範囲**: 評価の厳密さ（事前凍結・信頼区間）、コードとデータの公開声明、倫理声明（人を対象としないので「該当なし」）。
- **見直しタイミング**: desk reject された場合は B へ。

## 判断 2: 正解 (ground truth) = 自作の参照入力欄が自分のプロセス内で観測する IME イベント

- **背景**: macOS 側は打鍵推論なので、スクリプトの送信ログを正解にすると**同じ打鍵から作った正解で打鍵推論を評価する循環**になる。
- **選択肢**: A: 自作の参照入力欄（macOS = `NSTextInputClient` の `setMarkedText`/`insertText`/`unmarkText`、Windows = 自窓の `WM_IME_*` / IMN 通知または in-proc TSF） / B: スクリプトの送信ログ / C: 画面録画に人が注釈
- **採用**: A
- **理由**: 正解が IME 自身の状態から来るので循環しない。⚠️ **自分のプロセス内の観測**なので `docs/agent-shared.md` 制約 7（他プロセスの TSF 観測不可・グローバルフックでの `WM_IME_*` 傍受禁止）に触れない。
- **トレードオフ**: 参照入力欄の実装が両 OS で要る。⚠️ 参照入力欄は **1 つのアプリ**なので、他アプリでの挙動への一般化は限界として書く。C は、この Mac が画面を撮れない（TCC）ので不可。
- **見直しタイミング**: 参照入力欄が特定の IME で composition イベントを受けられないと判明したとき。

## 判断 3: 入力 = 合成入力のみ（人の打鍵は著者本人も含めない）

- **背景**: 倫理審査を経ていない（`.steering/20260804-g1-pilot-execution/decisions.md` D-3）。
- **選択肢**: A: 合成のみ / B: 合成 ＋ 著者本人 / C: 合成 ＋ 新規参加者（要倫理審査）
- **採用**: A
- **理由**: 倫理声明を「該当なし」にできる。端のケースはシナリオとして網羅的に作れる。
- **トレードオフ**: 自然な打鍵での精度は主張できない → **限界として明記**する。
- **見直しタイミング**: 査読で自然打鍵を要求され、かつ倫理審査の道が開いたとき。

## 判断 4: 範囲 = 両 OS・主要 IME

- **採用**: macOS 標準の日本語入力（ライブ変換 ON / OFF）と Windows の MS-IME は必須。Google 日本語入力は両 OS で任意（時間が許せば）。ATOK など有償 IME は対象外。
- **理由**: 論文の中心は **OS の非対称をどう扱うか**なので、片方だけでは主張が成立しない。
- **トレードオフ**: Windows の実測は Windows 機での作業が要る（memory `windows-agent-collection-only`：収集だけを依頼する運用）。

## 判断 5: コード公開 = 評価一式だけを別 repo で先に公開する

- **背景**: BRM は code / data availability の声明を求める。研究者の方針は「GSE 本体の OSS 公開と JOSS は未踏採択後」。
- **選択肢**: A: 評価一式だけを先に公開 / B: 査読者にだけ非公開で渡す / C: 投稿を OSS 公開後へ回す
- **採用**: A
- **範囲**: IME 観測部分（`ime_compose.rs` / `ime_cloak.rs` と OS ごとの薄いドライバ）、参照入力欄、シナリオ実行器、解析スクリプト、評価データ。⚠️ GSE 本体（HMM・介入・logger 全体）は含めない。
- **見直しタイミング**: 切り出しが本体と深く絡んで分離できないと判明したとき。

## 判断 6: 論文の貢献範囲

- **採用**: (1) 精度評価（主）、(2) 本文を再構成できないことの定量分析、(3) TSF では観測できないことの論証、(4) 実行コストの実測
- **却下**: [P321] 再解析の同梱（論点が離れる）
- **トレードオフ**: (2) は独立した課題で工数が増える。⚠️ 結果が「一部は漏れる」になっても**そのまま報告する**（content-free を過大に主張しない）。

## 判断 7: 目標時期 = 2026 年内に BRM へ投稿

- **理由**: 研究者の指定。
- **影響範囲**: 約 3 か月で、参照入力欄の実装・両 OS での実測・再構成分析・執筆を終える必要がある。律速は Windows 側の実測。

## 判断 8: CHI 2027 Posters は「余裕があれば」並行で出す

- **背景**: 研究者から「余裕があれば CHI にも」。
- **確認した事実**（2026-09-27）:
  - CHI 2027 Papers の締切は **2026-09-10 で既に過ぎた**（https://chi2027.acm.org/authors/papers/ ）
  - CHI 2027 **Posters** は **2027-01-21 締切・4 ページ（参考文献除く）・非アーカイブ**。逐語「All Poster submissions are non-archival. Authors may re-use and re-submit the content to other peer-reviewed and archival venues.」（https://chi2027.acm.org/authors/posters/ ）
  - ⚠️ LBW という区分が CHI 2027 にあるかは未確認（Papers ページの一覧は Papers / Panels / Workshops / Meet-Ups / Posters / Interactive Demos / SRC）
- **採用**: BRM 投稿後に、同じ結果の要約を CHI 2027 Posters に出す（任意）。
- **理由**: 非アーカイブなので二重出版にならない。締切の順序（BRM 12 月 → CHI 1 月）とも整合する。
- **⚠️ 未確認**: BRM が「査読中の論文と同じ内容の非アーカイブ発表」をどう扱うか（Springer の規程ページは取得できなかった）。→ 投稿前に BRM の規程を確認し、カバーレターで開示する。
- **見直しタイミング**: BRM の規程が非アーカイブ発表も制限していた場合は CHI を見送る。
- ⚠️ **追記（2026-10-03）**: 2026-09-28 に **取り下げ済み**（`.steering/20260928-p321-reanalysis-paper/decisions.md` の判断 15・研究者の選択）→ IME 論文は **BRM だけ**。

## 判断 9: 2 本目は「今は書かない」（2026-09-27）

- **背景**: 研究者の基準は「accept されやすい」かつ「機が熟している（すぐ書ける）」の両方を満たすなら 2 本目を書く。
- **検討**:
  - [P321] 再解析は**機は熟している**（解析・検算済み・`experiments/20260906-p321-resumption-baseline/`）。
    ⚠️ しかし受け皿として最有力だった RENE トラックが**両方とも新しいデータを要求**している:
    - SANER 2027 RENE（abstract 2026-10-19 / paper 10-23・10+2 頁・double-anonymous）逐語「Such submissions should at least apply the approach to new data sets (open-source or proprietary).」（https://conf.researchr.org/track/saner-2027/saner-2027-reproducibility-studies-and-negative-results-rene-track ）
    - ICPC 2027 RENE（abstract 2026-12-11 / paper 12-18。https://conf.researchr.org/home/icpc-2027 ）。ICPC 2026 RENE の規程は同じ文言（2027 年版の規程本文は未確認）
    → ★ 本解析は**原著者の公開データの再解析**なので、この条件を満たさない。「小標本による否定的結果は良い投稿ではない」とも明記されている（ICPC 2026）。
  - AI エージェント開発の経験報告は、失敗の体系的な分類が無く**機が熟していない**。
  - Phase1 の否定的結果は倫理審査の問題で**出せない**。
- **採用**: 2 本目は書かない。IME 論文（BRM）＋ CHI 2027 Posters（同じ結果の短縮・非アーカイブ）に集中する。
- **見直しタイミング**: [P321] と同じ定義を適用できる**別の公開データ**（debugging episode 等の人手コーディング済みデータ）が見つかった場合 → 新データへの適用として ICPC 2027 RENE（12-18 締切）を再検討する。

---

★ 以下 2026-09-28（次セッション: `.steering/_handoff/next-session-ime-paper-discussion.md`）。
前提の一次確認: CPU 値の出所（`experiments/20260903-o1-runtime-cost/notes.md`）／MS の TSF・IMM 文書／
Apple の `NSTextInputClient` 文書（JSON 経由で取得）／BRM の投稿規程と Springer 共通方針（ブラウザで取得）。

## 判断 10: design.md 初版を、一次確認による訂正 4 点を入れて承認する（2026-09-28）

- **背景**: 初版は一次文書を見ずに書いた箇所があった。
- **訂正**:
  1. ⚠️ `unmarkText` は**取消ではなく確定側**。Apple 逐語 "The text view should accept the marked text as if it had been inserted normally."（`https://developer.apple.com/documentation/appkit/nstextinputclient/unmarktext()` ）。★ 呼び出し順は Apple の文書に**書かれていない**。
  2. Windows の正解は **(a) IMM 互換メッセージ / (b) TSF 直受け（`ITfContextOwnerCompositionSink`）の 2 経路**を試して選ぶ。MS 逐語 "all non-TSF-enabled applications, except 16-bit and console window applications, are empowered by the TSF-based text services through a compatibility layer"（`https://learn.microsoft.com/en-us/previous-versions/windows/desktop/dnacc/input-method-editor-and-text-services-framework-accessibility` ）—— ⚠️ **どのメッセージが届くかは書かれていない**。
  3. `nav` の正解 = 正解側のセッション区間 × シナリオ実行器が送った矢印キー（区間を IME 自身から取るので循環しない）。
  4. ⚠️ CPU 平均 0.98% は**無効な値**（旧計器 `top -l 2` の過小報告。`notes.md:616-653`）。
- **採用**: 訂正を入れた初版を承認し、`/reimagine` へ進む。
- **影響範囲**: design.md §0 / §1.1 / §1.3 / §3 / §4 / §5 / §6、requirement.md の背景。

## 判断 11: 凍結前に「参照入力欄の較正パイロット」を行う（2026-09-28）

- **背景**: 判断 10 の 1・2 のとおり、正解の定義（確定・取消・候補窓）の根拠が**一次文書に無い**。
- **選択肢**: A: 参照入力欄だけを動かして呼び出し列を記録し、正解の定義を決めてから凍結 / B: 文書だけで凍結し、食い違いは逸脱として記録
- **採用**: A
- **理由**: 正解の定義を推測で凍結すると、凍結後に逸脱が出るのがほぼ確実。
- ⚠️ **境界**: GSE の IME 観測部を**走らせない**・ImeShadow と**突き合わせない**。→ ★ 精度の実測ではないので、handoff §4「プロトコル凍結前に実測を始めない」に当たらない。パイロットの範囲は preregistration に明記し、生ログも公開物に含める。
- **影響範囲**: design.md §1.1a・§6。

## 判断 12: E3 は「公開する IME 観測部だけ」を両 OS で測り直す。バッテリーは外す（2026-09-28）

- **背景**: 既存の値（macOS 2.19% / 1.62%・Windows 2.06%）は **GSE アプリ全体**の値で、論文で公開する観測部だけの値ではない（`notes.md:868-1000`）。
- **選択肢**: A: 観測部だけを測り直す（GSE 全体の値は参考として併記） / B: GSE 全体の既存値を引いて限界に書く / C: A ＋ macOS だけバッテリー
- **採用**: A
- **理由**: 読者が使うのは公開された観測部なので、その値を示すべき。活動量で値が動く（`notes.md:1000`）ので作業中 / 無操作の 2 条件で測る。
- **却下（バッテリー）**: 指標として 2026-09-04 に取り下げ済み・Windows 機に物理的にバッテリーが無い・macOS のエネルギー影響は無次元（`notes.md:176-193, 446`）。→ 限界に書く。
- **影響範囲**: design.md §3、paper-suggest.md C5。

## 判断 13: CHI 2027 Posters への併願は、BRM 投稿時のカバーレターで開示する（2026-09-28）

- **背景**: 判断 8 の未確認事項。★ BRM の投稿規程（`https://link.springer.com/journal/13428/submission-guidelines` ・2026-09-28 にブラウザで取得）にも、Springer 共通の方針（`https://link.springer.com/brands/springer/journal-policies` ）にも、**非アーカイブのポスター発表の扱いは書かれていない**。
  - Springer 共通の方針（逐語）: "The manuscript should not be submitted to more than one publication for simultaneous consideration. The submitted work should be original and should not have been published elsewhere in any form or language (partially or in full), unless the new work concerns an expansion of previous work."
  - プレプリントについては逐語 "Posting of preprints is not considered prior publication and will not jeopardize consideration at Springer Nature journals."
  - CHI 2027 Posters 側は逐語 "All Poster submissions are non-archival. Authors may re-use and re-submit the content to other peer-reviewed and archival venues."（判断 8）
- **選択肢**: A: 投稿時のカバーレターで開示 / B: 編集者に事前に問い合わせる / C: CHI は出さない
- **採用**: A
- **理由**: 規程に禁止の記述が無く、非アーカイブ発表なので、開示して判断を編集者に委ねるのが透明。
- **見直しタイミング**: BRM の編集者から指摘があった場合は CHI への投稿を取り下げる（CHI の締切 2027-01-21 は BRM 投稿より後）。
- ⚠️ **追記（2026-10-03）**: CHI 2027 Posters への併願そのものを 2026-09-28 に取り下げた（p321 のタスクの判断 15）→ カバーレターでの開示は**不要**。

## 判断 14: /reimagine の結果、ハイブリッド（v1 ＋ v2 の 8 点）を採用する（2026-09-28）

- **背景**: `/reimagine` 1 回目で `requirement.md` だけから v2 を再生成し、`design-comparison.md` で比べた。
- **選択肢**: A: ハイブリッド / B: v2 を全部 / C: v1（訂正版）/ D: もう一度 /reimagine
- **採用**: A
- **理由**: v1 は判断 1–13 と整合するが、⚠️ **凍結後には直せない妥当性の穴が 2 つ**ある:
  (1) **L2（書字研究者が計算する集計量の一致）が無い** —— BRM の読者が使うのは集計量。
  (2) **IME の学習で試行が独立でなくなる**のを扱っていない。
  → v2 から取り込む 8 点: L2 を主評価に／IME の学習・予測・辞書のリセットと固定／打鍵の速さ 3 水準の要因／oracle による正解の検証と content-free な正解ログ／パラメータ回復テストと陰性対照／E2 のシミュレーション攻撃と特徴の除去実験／逐語コピーの manifest／論文の「Validation framework」「Recommendations for researchers」節。
- **却下（必須化しない）**: 実アプリへの転移確認・現代文コーパス → **任意**（縮退順の先頭）。理由: 判断 7（2026 年内の投稿）に対して工数が重い。
- **トレードオフ**: 初版より工数は増える（L2 解析・IME のリセットの自動化・除去実験）。
- **影響範囲**: design.md 全体（v2 由来の箇所に〔v2〕印）。★ 縮退順 = 転移確認 → Google 日本語入力 → 現代文コーパス → S9 → E2 の開集合。★ プロトコルは OS ごとに段階凍結する（Windows 版は Windows 本計測前の追補）。
- **見直しタイミング**: 較正パイロットで 1 試行の実時間が 8 s を大きく超えた場合は、標本数（n = 75 / セル × シナリオ × 速さ）を凍結前に見直す。

## 判断 15: 題は T1、ライセンスはコード Apache-2.0 ／ データ・文書 CC BY 4.0（2026-09-28）

- **題**: *Observing Japanese IME conversion without recording text: Observability limits, a cross-platform logger, and a synthetic-input validation*（paper-suggest.md T1）。★ E2 の結果が強ければ T4 へ変えてよい（研究者了承済み）。
- **ライセンス**: コード = **Apache-2.0**（特許条項あり）、データ・シナリオ・文書 = **CC BY 4.0**。
- **理由**: BRM の Type 4 方針（非商用の自由利用を最低限とする）を満たし、特許条項で利用者を守れる。
- ⚠️ **未確認**: 現代文コーパス（任意）を使う場合は、その元ライセンスが CC BY 4.0 での再配布と両立するかを選定時に確かめる（例: CC BY-SA は継承が要る）。

## 判断 16: [P321] 再解析を 2 本目として並行で進める（判断 9 を改める・2026-09-28）

- **背景**: handoff §3 のサーヴェイを subagent 4 本（観察データ / 計装ログ / 投稿先 / 新規性）で回し、判断を動かす点はメインが一次で裏取りした。研究者の指示: 「機関に関係なく使えるもの（論文などで公開されたもの）で、機が熟しているなら並行して進める」。
- **一次で確かめたこと**:
  1. ★ **新しいデータがある**: [P434] Li & Coblenz（FSE 2026・doi:10.1145/3797077）の論文は逐語 "licensed under a Creative Commons Attribution 4.0 International License"。★ Table 4（task ごとの `Resolved` Y 13 / N 4）と Table 5（手法 × task・外部資源 6 task）だけで [P321] の定義を当てはめられる。配信者の episode の終端も逐語 "either the streamer's announcement that they gave up or had to continue another time, or the issue … fixed" で**同じ束ね方**。→ ★ R₀ = 11/17・R₀′ = 9/17・**分子の効果 +11.8pt**（[P321] は +11.2pt）。⚠️ n = 17・単位は task。⚠️ GitHub の補足データは LICENSE 無し → 論文の表だけを使う。
  2. ★ [P321] のデータも **CC BY 4.0**（`experiments/20260906-p321-resumption-baseline/data.md:13`）。→ ★ **両方とも機関に属さずに使える**。
  3. ⚠️ **R₀ は原著が補集合で報告済み**（arXiv v1 "occurring in only 21% of debugging episodes"、正式版 [P433] は "33%"）。→ repo の「論文は未報告」は誤りだった（`references.md` [P321] と `notes.md` §9.1 で訂正）。
  4. ⚠️ **「未 fix ほど参照が多い」は defect の起点で交絡**（層別で向きが揃わない。`notes.md` §9.2）。
  5. ★ **再解析・指標の再評価を受ける場がある**: EASE 2027 Short Papers and Emerging Results（逐語 "Re-evaluations, critiques, or empirical assessments of established theories, methods, measures, benchmarks, datasets, and research practices" ／ "Replication, reproduction, and confirmation studies, including studies that confirm previously established findings in new populations, technologies, organizations, or contexts"・**6 頁・abstract 2027-02-22 / paper 2027-03-01 AoE**・double-anonymous。https://conf.researchr.org/track/ease-2027/ease-2027-short-papers-and-emerging-results ）。ICPC 2027 ERA（逐語 "research in progress and do not require a solid evaluation"・4+1 頁・2026-11-26。https://conf.researchr.org/track/icpc-2027/icpc-2027-early-research-achievements--era- ）。
- **採用**: **2 本目を並行で進める**。主張の芯は R₀ ではなく、⚠️ **「解決と中止を同じ終端に束ねた episode 定義のもとで、成果を要求しない自己解決指標がどれだけずれるか」**（分子の効果 ＝ 未解決かつ参照なしで終わった割合）を **2 つの独立な公開データ**で示すこと、および交絡（起点）と版によるコーディングの揺れ（21% → 33%）の指摘。
- **暫定の投稿先**: ★ **EASE 2027 Short Papers（2027-03-01）**。理由: 募集文が「指標の再評価」「新しい文脈での確認」を名指ししている／BRM 投稿（12 月）と CHI Posters（2027-01-21）の**後**なので IME 論文と締切が衝突しない。⚠️ ICPC 2027 RENE（12-18・新データ必須）も [P434] で条件を満たしうるが、BRM と同月で、逐語 "lack of statistical power (small samples) is not a good submission" に n = 17 が当たりうるので次点。★ 投稿先の最終確定は研究者（次セッションで確認）。
- **却下**: 判断 9 の「今は書かない」—— 見直し条件（別の公開データが見つかる）が満たされたため。
- **トレードオフ**: ⚠️ 新規性は薄い（R₀ 自体は既報）。★ 主張を「指標の形の問題」と「交絡・版の揺れ」に絞る。⚠️ 正式版 [P433] の replication package が未入手（bot 対策）→ ブラウザで取得して v1 との差を突き合わせるのが次の最初の作業。
- **影響範囲**: `paper-suggest.md` の候補表と投稿計画、`docs/references.md`（[P321] 訂正・[P433]・[P434] 追加）、`experiments/20260906-p321-resumption-baseline/notes.md` §9、handoff `next-session-p321-reanalysis-paper.md`（新規）。
- ⚠️ **やらないこと**: [P321] / [P434] の値を GSE の期待値として使う（`notes.md` §4）。IME 論文と同じ論文に混ぜる（判断 6）。

---

★ 以下 2026-09-28（issue 分解セッション: `.steering/_handoff/next-session-ime-paper-issues.md`）。
⚠️ 分解の前に研究者へ 4 問を尋ね、次の 4 つの判断を確定した。

## 判断 17: E1 で評価する「観測」は、公開する単体ロガーにする（2026-09-28）

- **背景**: design.md §1.1 の図は「GSE の IME 観測部 → ImeShadow 行」と書くが、**何を動かして評価するか**（GSE アプリか、公開する単体ロガーか）は決まっていなかった。preregistration が「何を評価したか」を書く以上、凍結前に決める必要がある。
- **選択肢**: A: 単体ロガー（公開物） / B: GSE アプリ（配布ビルド）＋ 単体ロガーとは manifest で核の同一性だけを保証 / C: 両方を同時に走らせる
- **採用**: A
- **理由**: 題（判断 15）が *a cross-platform logger* であり、読者が使うのは公開物である。E3（判断 12）も同じ単体ロガーを測るので、E1 と E3 の対象が一致する。
- **トレードオフ**: ⚠️ 単体ロガーの OS ドライバが**本計測の前提**になり、クリティカルパスが 1 段伸びる。⚠️ ドライバは GSE の `hook_*.rs` の逐語コピーではない（新規の最小コード）ので、「GSE の値」ではなく「**公開ロガーの値**」として書く。
- **影響範囲**: issue 分解（ロガーのドライバ issue が本計測のマイルストーンの依存に入る）。★ 較正パイロットの手順 3（合成入力がフックに届くか）も単体ロガーの **`key` 行だけ**で見る（判断 11 の境界）。

## 判断 18: Windows 専用の issue は、この Windows 機（G-GEAR）でループを回す（2026-09-28）

- **背景**: 判断 4 と handoff は「Windows 側は研究者の Windows 機で収集だけを依頼する」運用を引いていたが、⚠️ その根拠の memory（`windows-agent-collection-only`）は G-GEAR の memory には**無い**。★ 一方、G-GEAR ではモード C のループを**過去 3 タスク**で回している（`.steering/20260914-mhd-feature-offline-tiers/` / `20260921-p1-prereg-cli-poles/` / `20260926-p1-main-prep/` の `_loop-config.json` の `events_path` が `/c/GSE-prototype/...`）。
- **選択肢**: A: G-GEAR でループを回す / B: Mac で実装し、Windows は `cargo check --target` と CI、収集だけを G-GEAR で行う
- **採用**: A
- **理由**: B では Windows のアプリが実機で初めて動くのが 11 月の Windows パイロットになり、不具合の発見が遅れる。律速は Windows（判断 7）。
- **影響範囲**: 各 issue に **`runs_on`**（`macos` / `windows` / `any`）を付け、`_issue-plan.md` に機械ごとの `--issues` を書く。★ 判断 4 のトレードオフの記述（「収集だけを依頼する」）は、**実測（本計測）の運用**としては残す。

## 判断 19: 読みの付与は SudachiPy を前処理だけに pin する（2026-09-28）

- **背景**: design.md §1.5 は「青空文庫の文から句を抽出する」とだけ書くが、⚠️ 漢字かな交じり文をローマ字で打つには**読み**が要る。一次の設計に手段が無かった。
- **選択肢**: A: `sudachipy` ＋ `sudachidict_core`（どちらも Apache-2.0）を前処理だけに pin / B: かな書きの句だけを抽出 / C: 少数の句に人手で読みを付ける
- **採用**: A
- **理由**: ライセンスがコード Apache-2.0（判断 15）と両立する。前処理を 1 回走らせて「句 ＋ 読み」のデータを確定し、その SHA-256 を `data.md` に記録すれば、以降の実行は辞書に依存しない。B は句が機能語に偏り、E2 の言語モデルとも文体がずれる。C は E2 の閉集合（K = 1000）に足りない。
- **トレードオフ**: ⚠️ 形態素解析の読みは誤りうる（例: 固有名詞）。★ ただし E1 は変換事象を測るので、読みが原文と違っても**打鍵列として妥当なかな**であれば足りる。E2 の正解は**打った読み**（原文ではない）と定義する。
- **影響範囲**: コーパス準備の issue（新規依存 2 件を Scope In に明記し、ループの停止条件「新規依存の追加」に当たらないようにする）。

## 判断 20: 評価一式は GSE で開発し、公開時に新しい repo へ書き出す（2026-09-28）

- **背景**: 研究者から「論文用に新しいリポジトリを作ったほうがよいか」と問われた。判断 5 は「評価一式だけを別 repo で先に公開する」とだけ書いており、**開発の場所**は決まっていなかった。
- **選択肢**: A: GSE の `experiments/20260928-ime-observation-accuracy/kit/` で開発し、公開時に新 repo へ書き出す / B: 今すぐ新 repo を作り、そこで開発する / C: 開発は GSE・private の空 repo だけ先に作る
- **採用**: A
- **理由**:
  1. ⚠️ **GSE の履歴は公開できない**（`.github/workflows/ci.yml:169` 逐語「public 化は**履歴全体を公開**するため experiments/ の被験者水準データが露出する」）→ 公開 repo は**どのみち新しい履歴**で始まる。
  2. ★ **ループ基盤が GSE の worktree 前提**（`loop-run.sh` / `loop-spawn.sh`・hook・CLAUDE.md の制約）。B では使えない。
  3. ★ **逐語コピーの manifest 照合は、コピー元が見える側でしか意味を持たない**。GSE は private なので、公開 repo の CI にできるのは「manifest と自分自身の一致」までである。GSE とのずれの検出は GSE 側に置く。
  4. Zenodo の DOI（design.md §4）は公開時点の repo のリリースに付ければ足りる。
- **トレードオフ**: 公開 repo の履歴は書き出し時点から始まる（★ BRM が求めるのは信頼できるリポジトリへの寄託であり、開発履歴ではない）。⚠️ GSE の `.gitignore` は `experiments/**/*.jsonl` / `*.ndjson` を無視する → ★ 評価の生ログは git に入れず、**Zenodo に寄託**して SHA-256 を `data.md` に記録する（既存の規約と同じ形）。テストの fixture はテストの中で生成する。
- **影響範囲**: すべての issue の Allowed Files（`experiments/20260928-ime-observation-accuracy/kit/` 配下）、書き出しの issue、公開のマイルストーン。★ 新 repo の作成は**外部への操作**なので、公開のマイルストーンで研究者が行う（または承認を得て行う）。

## 判断 21: 論文用の作成物は `papers/ime-observation/` に全部まとめる（2026-09-28）

- **背景**: 研究者から「論文用のコードや作成物は別ディレクトリを作ってその直下に置くか。GSE に影響が無いように（例: GSE-papers）」と問われた。
- **選択肢**: A: `papers/ime-observation/` にコード・原稿・事前登録・結果をすべて置く / B: コードと原稿は `papers/`、事前登録と結果は既存規約どおり `experiments/20260928-ime-observation-accuracy/`
- **採用**: A（研究者が選択）
- **構成**:
  ```
  papers/
  ├── README.md            ← 境界の規則（GSE 本体から参照しない等）
  └── ime-observation/     ← 書き出しの単位 ＝ 公開 repo の中身
      ├── kit/             ← 参照入力欄・実行器・単体ロガー・解析
      ├── experiment/      ← preregistration.md / SEED / config.json / data.md / env.md / run.sh / notes.md / results/
      ├── manuscript/      ← BRM 原稿・図
      └── LICENSE-CODE / LICENSE-DATA / CITATION.cff
  ```
- **理由**: 公開は 1 ディレクトリの書き出しで済む。★ GSE 本体（`src-tauri/`・`src/`）からは参照させず、GSE のビルドと CI の対象にも入れない。⚠️ ただし repo 全体を見る門（`scripts/check-shell-portability.sh` 等）には引き続きかかる。
- **トレードオフ**: ⚠️ `docs/experiment-tracking.md` の「実験は `experiments/<date>-<name>/`」から外れる → ★ 規約（SEED / env.md / data.md / run.sh / notes.md）は `experiment/` の中で守り、その旨を同文書に 1 行足す（issue 001）。⚠️ `.gitignore` の `experiments/**/*.jsonl` / `*.ndjson` は `papers/` に効かない → ★ `papers/ime-observation/.gitignore` で生ログを無視する（issue 001）。
- **影響範囲**: design.md / requirement.md が書く `experiments/<date>-ime-observation-accuracy/preregistration.md` は **`papers/ime-observation/experiment/preregistration.md`** に読み替える（★ 両文書の冒頭に追記した。本文は書き換えない）。

## 判断 22: issue 分解で決めた実装の型（2026-09-28・slicer の裁定・研究者が覆せる）

★ ループの issue は Allowed Files・verify・新規依存を**分解の時点で**固定しないと成立しない（`docs/loop-engineering.md` の停止条件「新規依存の追加が必要」）。以下はそのための裁定である。

| 部品 | 言語・手段 | 理由 |
|---|---|---|
| 生成器・実行器・段取り・解析・パイロットの道具・E2・E3・書き出し | **Python 3 の標準ライブラリだけ** | 依存ゼロで再現しやすい。既存の `experiments/*/analyze.py` と同じ型。⚠️ コーパス前処理だけ SudachiPy（判断 19） |
| 実行器の OS 送出 | Python `ctypes`（macOS = CoreGraphics の `CGEventPost`、Windows = `user32!SendInput` の scan code） | 計画 → 送出 → oracle を 1 言語で閉じる。⚠️ `docs/agent-shared.md` 制約 1（`windows` crate のみ）は **GSE の Rust** の規約であり、GSE の外にある評価一式には掛からない —— ★ ただし「送出は明示フラグが無ければ行わない（既定 dry-run）」を AC にする |
| 参照入力欄 macOS | Swift 1 ファイル（`swiftc`・パッケージ依存なし） | `NSTextInputClient` は AppKit のプロトコルで、Rust から実装するより素直 |
| 参照入力欄 Windows | Rust（`windows = "0.58"`・src-tauri と同じ版） | GSE の規約と揃う。⚠️ TSF はこのアプリ**自身のスレッド**に対してだけ使う（判断 2・`architecture-rules` ルール 5 が禁じるのは他プロセスの観測） |
| 単体ロガー | Rust（依存は src-tauri と**同じ crate・同じ版**に限る: `windows 0.58` / `core-graphics 0.24` / `core-foundation 0.10` / `serde` / `serde_json` / `crossbeam-channel`） | 逐語コピーした `ime_compose.rs` / `ime_cloak.rs` / `ime_mode.rs` がそのままコンパイルでき、**それらの単体テストも単体ロガーの中で走る** |

- **逐語コピーの範囲**（2026-09-28 に一次で確認）:
  - ★ **ファイルごと**: `ime_compose.rs`（外部参照は `super::hook::VK_KANJI` ＋ Atomic 8 個 ＋ `super::ime_cloak::MAX_SESSION_MS`・`ime_compose.rs:71,90,360-363`）／`ime_cloak.rs`（外部参照ゼロ・`use std::collections::BTreeSet;` のみ・`:34`）／`ime_mode.rs`（`super::hook::{VK_DBE_* 5 個, VK_KANJI}` の定数だけ・`:31-34`）。→ ★ `hook` は**定数と Atomic だけのシム**で足りる。
  - ★ **抜粋（アンカーで範囲を決める）**: `anonymize.rs` の `/// VK コードをプライバシーセーフなキー種別カテゴリに変換する` 〜 `/// NDJSON 1 行を匿名化する。` の直前（`KeyCategory` の doc・derive・enum・impl・`anonymize.rs:12-127`。⚠️ ファイルごとはテストが `crate::schema_dto::LogEntryDto` に依存するので不可・`anonymize.rs:325`）／`hook_macos.rs` の **`is_observed_key`（`:248`）と `macos_vk_to_vk`（`:279`）の 2 関数**を doc comment ごと、関数ごとの抜粋として（⚠️ `macos_vk_to_vk` と `handle_event`（`:480`）の間には別の関数があるので「〜 `handle_event` の直前」では取らない）。
  - ⚠️ **新規に書く**: OS ドライバ（CGEventTap / 低水準キーボードフック / WinEvent・DWM cloak）と行の書き出し。★ `hook_macos.rs`（1529 行）・`ime_windows.rs`（673 行）・`lib.rs` の IME Monitor（`:3552-3664`）は `logger::LogEntry` や G1 の分岐に絡むため（impact-analyzer 報告を一次で裏取り）。
  - ★ manifest は「ファイル / 抜粋 / 新規」の 3 種を区別して持つ → 論文で「GSE と共有するのはどこまでか」を正確に書ける。
- **ImeShadow の `t`**: `lib.rs:3216-3243` のとおり **drain した時刻**（IME Monitor のポーリング）であって変換の終端ではない。→ ★ 観測区間は `[t − dwell_ms, t]` を既定とし、⚠️ 終端の遅れ（0〜100 ms）を注入してもパラメータを回復できることを照合器の AC にする（issue 017）。
- **生ログの置き場**: git に入れない（Zenodo に寄託・SHA-256 を `data.md`）。テストの fixture はテストの中で生成する。

## 判断 23〜26: issue 001 の merge ゲートのレビューを受けた契約の変更（2026-09-28・研究者の回答）

★ W1（issue 001）の merge 前に code-reviewer と security-checker を並列で回した（どちらも CRITICAL / HIGH なし）。
契約（`FORMATS.md` / `validate_logs.py` の規則）を変える指摘だけを研究者に問い、4 問とも推奨案で確定した。

| # | 論点（出どころ） | 採用 | 理由 |
|---|---|---|---|
| 23 | `obs/1` の `capabilities` に、名前の正規表現に合うローマ字の単語列を何個でも入れられる（security-checker MEDIUM） | ★ **capabilities だけ閉じる**: 名前は `{key, ime_shadow}` の列挙・3 つの配列を通して重複を拒否（＝合計 2 個まで）。整数の欄・版の文字列・`manifest_sha256` は絞らず、README と FORMATS に「**値の意味は保証の範囲外**」と明記する | 単体ロガーで現れる名前は 2 つだけと契約自身が書いている。整数・版の範囲を絞ると後続の worker が詰まりうる。content-free は生産側の設計（長さ・種別・時刻しか書かない）で担保し、検査器はその**構造**を機械で確かめる、と書き分ける |
| 24 | JSON のエスケープ（`"gt\/1"` や、`\u` ＋ 16 進 4 桁で 1 文字を綴った `ev`）がデコード後の列挙に合って通る（code-reviewer MEDIUM・再現済み） | ★ **`gt` / `obs` の行に `\` があれば拒否**。FORMATS に「エスケープしない（Swift は `.withoutEscapingSlashes`）」と書く | 許される文字列値はどれも `\` を含まないので、正しい出力は必ず通る。後続の検査が生の文字列で行を探す前提（空白の禁止と同じ型）を守る |
| 25 | `plan/1` / `oracle/1` の型（`intent` の各キーの型・ヘッダの `os`・時刻のキー名・`trial_id` / `phrase_id` の書式）が未確定（code-reviewer MEDIUM） | ★ **W2 の前にメインが FORMATS.md に型を 1 行ずつ足す**（ID は `P`＋3 桁に当たらない書式）。差分を研究者に見せてから base に入れる | W2 で生産側（003 / 004）と消費側が並列に動くので、食い違いを統合（020）まで持ち越さない |
| 26 | 圧縮した生ログ（`*.jsonl.gz` / `*.zip` / `*.tar.gz`）と `papers/` の他の場所の `*.jsonl` が追跡されうる（security-checker LOW） | ★ **圧縮物を足し、`papers/.gitignore` にも `*.jsonl` / `*.ndjson` を置く**。例外 `!kit/corpus/data/*.jsonl` は残す | 027（現代文コーパス）も `kit/corpus/data/` に置くので例外は狭めない |

- ★ 仕様の範囲内の直し（研究者に問わずメインが直した）: M1 FORMATS の「整数か真偽値」の文言を issue に戻す ／ M2 ライセンスを種類で書く（コード Apache-2.0 / データ・文書 CC BY 4.0）／ 違反と開けないファイルが重なったら exit 1 を優先 ／ 違反メッセージに出すキー名は既知のものだけ ／ `check.sh` の目印は行全体の一致だけ拾う（⚠️ 行末の空白・CR は許す —— `grep -x` だけだと CRLF のファイルで目印が黙って外れ selftest が回らなくなる）・`--root` の存在確認・`.venv` / `venv` を探索から外す ／ UTF-8 の BOM が拒否されることを FORMATS に明記（既存の挙動の記述） ／ selftest の CLI の件数を実数に。
- ★ **判断 25 の中身**（2026-09-28・メインが下書き → 研究者が差分を承認 → base へ）: `FORMATS.md` の `plan/1` / `oracle/1` / `corpus/1` に「の型」節を足した。判断が入った点: `trial_id` = `^t[0-9]{5,}$`（全体の連番）・`block_id` = 0 始まりの連番 ／ `intent` は 8 キー必須・`cand_index` は 0 始まりの整数か `null` ／ `*_sha256` はファイルのバイト列の SHA-256（小文字）／ oracle の時刻は「`sent` / `marker` = 送出の直前・**`trial_begin` = `gap_before_ms` の待ちの後**（試行の区間に試行間の待ちを含めない —— 010 の重なりと 019 の分母に効く）・`reset` は `block_begin` の前」／ `marker` は押下ごとに 1 行 ／ `work_id` / `phrase_id` は小文字始まり（024 の被験者 ID の検査 = 大文字の `P` ＋ 3 桁に当たらない）。
- ★ 研究者に問わず記録だけしたもの（LOW・後続の issue やマイルストーンで扱う）: ヘッダが壊れていると 2 行目以降を検査しない ／ `manifest_sha256` の大文字 ／ `gt` の `vk` は合成入力でのみ生成する旨 ／ `NSNotFound` の扱い（007）／ `check.sh` の除外パターンが ROOT を含む絶対パスに効く（checkout が `target/` 等の下にあると 0 本の赤になる・赤に倒れる向き）。

## 判断 27〜30: W2a（002 / 003 / 010 / 016）の merge ゲートのレビューを受けた裁定（2026-09-28・研究者の回答）

★ code-reviewer 2 本（002+003 / 010+016）と security-checker（002+010）を並列で回した。CRITICAL なし、HIGH は 010 の 2 件だけ。
契約・設計に関わる 4 点を研究者に問い、4 問とも推奨案で確定した。

| # | 論点（出どころ） | 採用 | 理由 |
|---|---|---|---|
| 27 | 010 H1: Windows の `nav` の正解の区間。確定版 design.md:100 は「Windows は候補窓が開いていた区間」、issue 010:14 はこの括弧を落としていた（分解の取りこぼし） | ★ **design に合わせる**: 規則に候補窓の閉じ（`candidate_end`）を足し、Windows 用に「候補窓が開いていた区間の矢印数」を別の欄 `nav_true_cand` で出す（`mac_nstic` は `null`）。数える矢印は**そのセッションが帰属した試行の `sent` に限る**（確定が遅れて次の試行の矢印を拾うのを防ぐ）。018 の `nav` の正解は `nav_true_cand` が `null` でなければそれ、`null` なら `nav_true` | GSE の Windows の `nav` は窓イベント由来。セッション全体で数えると、候補窓を開く前の文節移動が正解にだけ入り、一致率が系統的に下がる |
| 28 | 010 H2: `excluded` が区間の列だけで、セッションに印が無い。時計の跳びの区間は跳んだ当の壁時計で書かれ、gt と oracle は単調時計の基準が違う | ★ **試行単位で印を付ける**: セッションに `excluded_by`（理由の配列・空なら対象外）、`excluded` の各要素に影響する `trial_ids`。017 は印と `trial_id` で外す（区間では外さない）。診断用にセッションへ `n_start_while_open`（開いている間に来た start の数）も出す | 017〜020 が突き合わせ方をそれぞれ決めると、除外件数と `dwell_ms` がずれる。除外は「全部報告」する規則（design §1.3） |
| 29 | 003: 計画にどの版の recipes / コーパスで作ったかが残らない。S10（読みの前半だけ打つ）と S12（合成かな列）の「打った読み」が計画から一意に取れない | ★ **`plan/1` のヘッダに `recipes_sha256` と `corpus_sha256` を足す**（FORMATS の改訂）。試行は**直前のブロック行**を指す、と契約を狭める。打った読みを返す `typed_reading(...)` を 003 から公開する | パイロットの後に recipes を直す前提なので、計画ごとに版を束ねないと後から辿れない。E2（019 / 021）が打った読みを各自で作り直さずに済む |
| 30 | 002 / 003: 読みに「ゐ ゑ ゕ ゖ」を含む句。romaji の表は `wi` / `we` / `xka` / `xke` と打つが、IME は一般に `wi` を「うぃ」、`xka` を「ヵ」と解釈しうる（実機では未確認） | ★ **002 で句ごと捨てる** | 打った読みと正解の読みが食い違う曖昧さを刺激の側で消す |

## 判断 31〜34: W2b（008 / 011 / 015）の merge ゲートのレビューと watchdog の扱い（2026-09-28・研究者の回答）

★ code-reviewer 2 本（008+011 / 015）と security-checker（008+011+015）を並列で回した。CRITICAL なし。HIGH は 011 の 1 件（Windows の候補窓の観測の差し込み口が無い）と 015 の 2 件（封印の大きさから ImeShadow の行数が推せる・`reach.py` がブロックの境目で取りこぼしを隠す）。
008 は LOW だけで merge した（002 / 003 / 010 / 016 と同時・`c968670b`。merge 後の base で 6 本の acceptance が緑）。

| # | 論点（出どころ） | 採用 | 理由 |
|---|---|---|---|
| 31 | 015 `seal_obs.py`: 標準出力・`seal.json` のバイト数と封印先の大きさから、ImeShadow の行数（＝検出したセッション数）が ±5% で推せる（レビュー 2 本が実測）。issue 015 は `seal.json` にバイト数を記録せよと書いていた | ★ **バイト数を標準出力と `seal.json` から外し、封印先を 1 MiB 単位に詰める**（元の長さは詰め物の後ろに置き、凍結後の開封で取り除く）。完全性は SHA-256 だけで確かめる。docstring / README の「行数は分からない」を直す | 凍結の前に再現率が読めると判断 11（パイロットは ImeShadow を見ない・数えない）が崩れる。標準ライブラリだけで閉じられる |
| 32 | 011: `manifest_sha256` の元の `manifest.json` が autocrlf で CRLF になると OS ごとに値が変わる。ドライバの manifest はハッシュに入らない | ★ **`.gitattributes` に `papers/ime-observation/kit/logger/manifest*.json text eol=lf` を足すだけ**（メインが base に入れた）。ハッシュの対象は `manifest.json` のまま | ドライバの版は各 manifest と照合器で辿れる。012〜014 が後から manifest を足してもコンパイルが壊れない |
| 33 | 011: manifest の `new`（GSE と同じ判断を同じ順で新しく書いたコード）は、GSE 側が後で直されても照合器が緑のまま | ★ **検出できるようにする**: `new` のエントリに写した元の GSE の範囲（アンカー）とその SHA-256 を持たせ、`--against-gse` で照合する（012〜014 も同じ形を使う） | 論文は「ロガー = GSE の判断」と主張する。要の部分だけずれを検出できない状態を避ける |
| 34 | watchdog: W2 の `recheck` 5 本のうち 3 本（010 / 008 / 011）が空応答で `blocked`。watchdog はこのタスクでは bash / python を実行できず読むだけ（B3）。`blocked` だと `issue_done` が出ず後続が起動しない | ★ **まだ回していない `recheck` の 14 本（004 005 007 009 012 013 014 017 018 019 020 021 024 026）を `parse` に落とす**。合否はこれまでどおりメインが clean な checkout の acceptance とレビューで決める。`blocked` のまま base に merge した issue は、後続の `## Dependencies` から外す（`issue_done` は手で書かない）: 009 から 008・020 から 010（2026-09-28）。011 は merge の後に 012 / 013 / 023 / 024 から外す | 独立の再検証になっていない watchdog が、止めるだけで判定の材料を増やさない。依存の DAG は実行の順序だけを決め、成果物は base にある（`docs/loop-engineering.md` 2026-09-27） |

## 判断 35: 013 の Stop（`is_observed_key` の抜粋が `crate::analysis::key_gate` を呼ぶ）を 011 の追補で解く（2026-09-28・研究者の回答）

- 事象: W3 の 013（単体ロガーの Windows ドライバ (1)）の worker が attempt 1 で Stop した。GSE の `is_observed_key`（`hook_windows.rs:118-133`）は本体の先頭（`:120`）で `crate::analysis::key_gate::is_feature_key` を呼ぶが、単体ロガーのクレートに `analysis` が無く（`main.rs:10-17`）、`mod analysis;` を足せるのは 013 の Allowed Files の外の `main.rs` だけ。→ AC3 / AC4（逐語の抜粋）を Allowed Files の中で満たせない。★ `_issue-plan.md` §7b の「残るリスク」がそのまま起きた形。
- 一次で確認: `key_gate.rs` の外部参照は doc コメントのリンク 1 件（`:46`）とテストの `use super::*`（`:65`）だけ → ファイルごとの逐語コピーにできる。
- 選択肢: A = 011 の追補で `key_gate.rs` を逐語コピー（逐語の主張を保つ）／ E = AC4 を緩めて「移植＋変化検出」（主張が弱まる）
- **採用: A**。メインが base に入れた: `src/analysis/key_gate.rs`（`cmp` で GSE と一致）・`src/analysis/mod.rs`・`main.rs` の `#[allow(dead_code)] mod analysis;`・`manifest.json` の `key_gate`（file）と `analysis_mod`（new）・`main.rs` の SHA-256 を持つ 3 エントリの更新（`check_manifest.py --update`・`--self` と `--against-gse` は一致）。README の共有範囲の表と 013 / 014 の Background に追記。
- 影響: `meta` の `manifest_sha256` の値が変わる（まだ何も凍結していない）。013 は範囲を変えずに回し直す。

## 判断 36: 公開物の書き方 —— 学術的な英語・GSE への言及なし（2026-09-28・研究者の指示と回答）

- 研究者の指示（逐語の要旨）: 「コメントの箇所などで GSE と関連するような記述は、公開する際には一切ないようにする。コメントの口調や表現もアカデミックに」。
- 研究者の回答（4 問とも推奨案）:

| 論点 | 採用 |
|---|---|
| 言語 | ★ **公開物（`papers/ime-observation/` のコメント・docstring・README・FORMATS・selftest の説明）は学術的な英語**。内部の記録（`.steering/`・`papers/README.md`）は日本語のまま |
| 逐語コピー（GSE から 1 バイトも変えずに写したファイル・抜粋）のコメント | ★ **リポジトリの中では逐語のまま**（GSE との照合は公開しない側で続ける）。**公開の書き出し（024）でコメントを機械的に除き**、各ファイルの冒頭に学術的な英語の説明を 1 つ付ける。公開側の manifest は書き出した後のファイルのハッシュを持つ |
| 直す時期 | ★ ① 今から書くもの: まだ回していない issue と作業用エージェントへの指示に規則を入れる ② 024 の書き出しの検査に `GSE` / `src-tauri` / `★` / `⚠` などを足して機械で止める ③ 既に merge したもの（W1〜W3）は **W3 の後に整理の issue を 1 本切って**書き直す |
| 出どころの記録 | ★ **公開しない欄・ファイルに寄せる**: manifest の `gse_*` の欄と、書き出しの対象外の `*.internal.md` だけに書く。公開するコメント・README には書かない。書き出し（024）がそれらを落とす |

- ⚠️ 整理の issue で一緒に直すこと: acceptance が日本語の文字列（selftest のケース名など）を名指している箇所（例 `010-acceptance.sh` の「5 型」）は、コードを英語にすると赤になる → acceptance の側も同時に直す。GSE を指す識別子（例 `check_manifest.py --against-gse`）も中立の語に改める。
- ⚠️ 今走っている W3 の 017 / 021 / 022 は旧い書き方のまま出てくる → 整理の issue の対象に入れる。

## 判断 37〜41: W3（009 / 013 / 017 / 021 / 022）の merge ゲートのレビューを受けた裁定（2026-09-28・研究者の回答）

★ W3 の 5 本はループで `issue_done`（013 は判断 35 の追補の後に回し直し）・clean な checkout で acceptance 失敗 0 件。
レビュー: code-reviewer 3 本（009+017 / 021+022 / 013）・security-checker 2 本（009+021+022 / 013）。CRITICAL なし。
HIGH は 009・017・021（2 件）・022・013（引き継ぎの穴）。security は LOW だけ。5 問とも推奨案で確定した。

| # | 論点（出どころ） | 採用 | 理由 |
|---|---|---|---|
| 37 | 009 HIGH: 変換の途中でフォーカスが移ると、`OnSetFocus` → `detach` → `reset` で開いていた変換を `tsf_end` なしで捨てる。010 は開いている間の `tsf_start` を数えるだけなので、次の試行の変換と 1 つの正解セッションに併合される（S15） | ★ **変換が終わるまで古いコンテキストの監視を外さない**（IME 自身の終わり方を正解として記録する）。M5 のパイロットで、フォーカスを移したときに終わりの通知が本当に届くかを確かめ、届かなければ「フォーカスが外れたら閉じる」規則を 010 に足す | 正解ログは IME 自身の状態を写すのが目的。参照入力欄の都合で区切ると正解の側に人工的な併合・取消ができる |
| 38 | 017 HIGH: IoU ≥ 0.5 の 1 対 1 を先に確定するので、2 断片の分割が「対＋偽検出」、偏った併合が「対＋取り逃し」になる。design §1.2 の「分割・併合を別に数える」意図が実データで見えない | ★ **1 対 1 の後で数え直す**: 主の対応づけは変えず、対になった正解の区間に大半が入る未使用の観測を「分割」、対になった観測の区間に大半が入る未使用の正解を「併合」に数え直す。注入の検査に現実的な割れ方（切り目が乱数の 2 断片・偏った併合・短いセッション）を足し、定義による偏りを数値で報告する | 主の指標（適合率・再現率）の定義を変えずに、design が見込む macOS の併合（S8 / S9）を併合率として見えるようにする |
| 39 | 021 HIGH ×2: 除去実験で情報の多い特徴集合ほど正解率が低い逆転（例 1 秒ビンの件数 0.38 < 件数だけ 0.84）。S12 の囮に打てない句が混ざり偶然水準が 1/K でなくなる | ★ **攻撃者は情報を捨てられる前提で、各特徴集合は「それ自身と、そこから作れる粗い集合の正解率の最大」を報告し、公開の粒度の推奨はこの値で決める**。距離も直す（予想ログの位相を揃える・区切りの間の件数で比べる・ビン境界を「間」にしない）。囮はそのシナリオで計画が選べる句に絞る。シナリオ別の内訳を出す。S10 の正誤は打った読み（`typed_reading`）で判定する | 漏洩を過小評価する向きの推奨を出さない。偶然水準を 1/K に保つ |
| 40 | 022 HIGH: 句単位の分割で、評価句と同じ作品の約 8 割が学習側に入る（design の K1 より強い攻撃者） | ★ **作品（`work_id`）単位で分ける**（K1 = コーパスは知っているがその作品は知らない）。句単位の結果も「より強い攻撃者（K1+）」として併記する。入れ替えとの差の `gain_vs_shuffled` を出す | 攻撃者モデルの名前と中身を一致させる |
| 41 | 013 のレビュー: 候補窓の観測関数（GSE の `is_candidate_window_open` 相当）を核に渡しておらず、013 の引き継ぎにも 014 の仕様にも書かれていない。014 は IME の開閉を追う仕様だが、開閉の書き手は GSE ではキーボードフックの中にあり、014 は 013 の `keyboard.rs` を変えられない | ★ **IME の開閉の追跡を 014 から外す**（公開するログ `obs/1` は開閉を書かない）。014 は**候補窓の観測関数**（DWM cloak・EnumWindows・UIA・stale のリセット）を `candidate_window_observer` として核に渡すことを仕様と AC に明記する。論文では「単体ロガーは IME の開閉を記録しない」と書く | 使わない経路を作らない。候補窓の判定は `dwell_ms` / `nav` に直接効くので、GSE と同じ判断を担う場所をはっきりさせる |

- ★ 仕様の範囲の直し（研究者に問わずメインが段取りする）: 013 のフックからの送信を上限つきのチャネルの `try_send` にし、取りこぼしを数える（hook-constraints）／009 の `Msftedit.dll` をシステムフォルダからだけ読み込む（DLL の植え付け）・始点の位置で「確定 → 次の開始」を分ける・M5 の確認項目を README に足す／017 の F1 の区間をクラスタ・ブートストラップに・`t_raw` を常に付ける・`n_start_while_open` を出力に出す／021・022 の深い入れ子・重複キーの拒否・出力を上書きしない・obs のヘッダの検査・マーカーと IME の切替が行になるかの前提を 2 本で揃える（既定は「行が出ない」＝ Windows の `is_observed_key` の外）。

## 判断 42: 判断 36 の実装 —— 機械の門・識別子の改名・内部の番号・整理の進め方（2026-09-28・メインの実装上の選択）

- **機械の門**: `issues/_style_check.py`（内部の道具・公開しない）。禁止語（語としての GSE・`src-tauri`・`.steering`・★・⚠・内部の番号〔decision / issue の番号・M0〜M13〕）と、地の文（コメント・docstring・Markdown の地の文・manifest の `reason`・規則の `_note`）の日本語を拾う。逐語コピー（manifest の `file` / `excerpt` の範囲）・`kit/corpus/data/`・`*.internal.md`・生成物は除く。バッククォートの中の日本語（読みの例など）は許す。2026-09-28 の base で違反 2,404 件。
- **acceptance の関数 `style_ok`**（`_acceptance-lib.sh`）: その issue が変えた `papers/ime-observation` の中のファイルだけを検査する。まだ回していない 14 本の acceptance に入れ、日本語のケース名（006 / 018 / 019 / 023 / 024 / 025）を英語にした。024 の acceptance に判断 36 の検査（書き出した全体の検査・出どころの欄が無い・`*.internal.md` が無い）を足した。
- **識別子の改名**: `check_manifest.py --against-gse` → `--against-upstream`、manifest の `gse_*` の欄 → `upstream_*`。判断 36 の「出どころは manifest の `gse_*` の欄」は、改名後の `upstream_*` の欄を指す。公開の書き出し（024）は `upstream_*` と `start_anchor` / `end_anchor` / `check_decls` を落とす。
- **整理の進め方**: issue 028。ループではなく、メインが 6 つの束（形式と入口／刺激／解析／パイロットと E2／ロガー／参照入力欄）に分けて作業用エージェントに並列で渡し、統合して `028-acceptance.sh` と merge 済みの全 acceptance で確かめる。merge 済みの issue の acceptance が名指す日本語のケース名は、028.md の表の英語の名前に同時に直す。

## 判断 43: 公開物から「参照実装・写した元」との関係の説明も除く（2026-09-28・研究者の回答）

- 論点: issue 028 の整理の後も、公開物（主にロガー）に「reference implementation（参照実装）」「upstream（写した元）」「verbatim copy」の言い回しが残っていた（GSE と名指さないが、別の実装を写した関係を説明している。公開 repo では写した元が見えず、写した元との照合も使えない）。論文ディレクトリの README にも、公開しない境界の規則（`../README.md`）へのリンクがあった（メインが `53fa7b87` で除いた）。
- 採用: ★ **公開物からも除く**。
  - 公開する説明文には関係を書かず、中身だけを書く（例「the monitoring loop polls every 100 ms」）。
  - 写した元との照合（`--against-upstream`）と manifest の書き直し（`--update`）は、書き出さない内部の道具 `kit/logger/check_manifest_upstream.internal.py` に移す。公開する `check_manifest.py` は自己照合（`--self`）と selftest だけにする。
  - 書き出し（024）は `*.internal.*` をすべて書き出さない。検査器は `*.internal.*` を対象外にし、公開物の中の「reference implementation / reference source / upstream / verbatim copy」を拾う（2026-09-28 の base で 110 件・すべてロガー）。

## 判断 44〜46: W4（014 / 018 / 019）の merge ゲートのレビューを受けた裁定（2026-09-29・研究者の回答）

★ W4 の 3 本はループで attempt 1 の `issue_done`（計 13.0M トークン・$5.53）。clean な checkout で acceptance 失敗 0 件（014 ✅ 17 / 018 ✅ 12 / 019 ✅ 11）。
レビュー: code-reviewer 3 本（014 / 018 / 019）・security-checker 2 本（014 / 018+019）。CRITICAL なし。HIGH は 018 の 1 件・019 の 2 件（security は MEDIUM 1 件〔014〕・他は LOW）。
直しは作業用エージェント（Sonnet）が各 worktree で行い、メインが clean な checkout で acceptance を回し直し（014 ✅ 17 / 018 ✅ 12 / 019 ✅ 11・いずれも失敗 0 件）、HIGH の直しが効くことを写しへの変異で確かめた（018: 偽検出の中の `dwell_ms == 0` を数えない → selftest 赤／019: 観測側から偽検出を落とす → selftest 赤。直す前の 019 は同じ変異で 7 ケースとも緑だった）。

| # | 論点（出どころ） | 採用 | 理由 |
|---|---|---|---|
| 44 | 014 security MEDIUM: 候補窓の観測関数が、写した元と同じく UI Automation でフォーカス要素の名前（accessible name）を 100 ms ごとに読み、「候補」の部分一致で判定していた。保存・ログはしないが、他アプリの任意の文字列（タブ名・本文など）をプロセスのメモリに読み込み、一致すると `ime_shadow` 行の出力時刻が遅れる（1 ビット程度の副チャネル）。公開する README は「content-free by construction」と主張している | ★ **名前の分岐を外し、クラス名（"Candidate"）だけで判定する**。写した元との違いは `kit/logger/PROVENANCE.internal.md` に記録する（公開物には書かない・判断 43） | 公開する観測器が構造的に内容を読まないことを保つ。写した元の実測（`ime_windows.rs:186-193`）で、cloak 経路の端末ではこの UIA の裏取りは 0 件なので、主な環境では差が出ない見込み。⚠️ IMM 経路の端末で名前でしか裏が取れない候補窓があると stale の判断が早まりうる → **M5 のパイロットで確かめる** |
| 45 | 018 code-reviewer HIGH: 時計の巻き戻りで出る `dwell_ms == 0` の観測行は、照合器（017 の `match.py`）で長さ 0 の区間になり、長さ正の正解と重ならないので必ず偽検出に落ちる。l1 の `n_zero_excluded` は実データでは常に 0 になり、適合率はその行の分だけ下がる | ★ **l1 がすべてのバケット（対・分割・併合・偽検出）の `dwell_ms == 0` の行を数えて出す**。照合でこの行を検出とみなすか・偽検出か・評価から外すかは、パイロットで巻き戻りが実際に起きるかを見てから **M3（事前登録の凍結）で決める**（⚠️ 未決）。★ 019（l2）も同じ方針: 平均変換時間と時間割合からは外し、変換の数と放棄には今は数え、件数（`n_dwell_zero`）を出す | 規則を決める材料（巻き戻りの頻度）がまだ無い。凍結の前に決めればよく、それまで件数が見えることが要る |
| 46 | 019 code-reviewer MEDIUM ×2: ① 計画にあって oracle に無い試行（途中で止まった実行）が 1 件でもあると L2 全体が exit 2 になる ② 除外された試行（`clock_jump` / `log_truncated`）を含むテキストが欠けのないテキストとして扱われ、テキストの時間は落ちた試行の分を含んだまま変換の数だけ減る（テキスト間のばらつきが人工的に増え ICC を押し上げうる・件数も出ない） | ★ **どちらかを 1 件でも含むテキストは捨て、理由別（未実行 / 除外）・ブロック別・速さ別の件数を出す**。速さが混ざるテキストはエラーのまま | 既存の「端数は捨てて件数を出す」と同じ規則で、テキストは常に欠けのない `text_size_trials` 件になる。途中で止まった実行でも L2 が出る |

- ★ 仕様の範囲の直し（研究者に問わずメインが段取りした）:
  - 014: `resolve_events` の 1 周分を差し替え可能な `step` に切り出してテスト（旧来の経路が駆動中は Atomic に触れない・再表明・`on_tick`）／クラスの判定を DWM への問い合わせより先にする（写した元の順）／`WM_QUIT` で hook スレッドが終わる（共有の `stop` は立てない → 核が「driver's thread has ended unexpectedly」で検知する）／pump が止まったらフックを外してから join する／SAFETY・既知の限界（UIA の同期呼び出しが監視ループを遅らせうる）・doc の記録のずれ。
  - 018: 打ち切りの境界は観測器に合わせて `>= 20000` ms（design.md §1.3 の「20 秒超」の字面ではなく、観測器が打ち切る条件に揃える）／`truncation` の `n_long` は照合に入った正解だけを数え、除外されたものは別に数える／`truncation` と `oracle` を層ごとにも出す（issue 018 の Scope）／selftest の穴（`mae_ci`・表の向き・`nav_true_cand == 0`・対照の seed・不一致の試行が評価に残ること）／入力の不整合を exit 2 に／`B` の上限（100000）／出力に写る入力の欄（oracle の件数・種類・`cell`）を検証する。
  - 019: テキストごとの変換の数を固定値で検査（観測側は対・分割・併合・偽検出の全行、正解側は取り逃しを含む）／Bland–Altman と ICC を速さの層ごとにも出す（design.md §1.5「主推定値は層別」。CLI の要約は層別を主に表示）／`outside_texts` を理由別に／ICC の区間は未定義の再標本があれば出さず理由を残す／回復の許容幅を詰める／壊れた match.json・重みのオーバーフロー・`B` の上限・`definition` の照合を exit 2 に。
  - security LOW L-5（`--out` が既存ファイルを黙って上書きする）は直さない: `kit/analysis/` の 4 本（match / gt_sessions / l1 / l2）に共通の既存の方針で、出力は入力から再生成できる。

## 判断 47: Mac の W2（004 / 007）を回す前の段取り 2 点（2026-09-29・メインの実装上の選択・研究者が覆せる）

| 論点 | 採用 | 理由 |
|---|---|---|
| 004 / 007 の `## Dependencies` の `001` | ★ **外す**（判断 34 と同じ形・`issue_done` は手で書かない） | 001 の `issue_done` は G-GEAR の events にだけある。Mac の events は空なので、`deps_met` が永久に偽で一度も起動しない（`loop-run.sh:1072`）。成果物は base にある |
| Mac の base で verify（`kit/check.sh`）が赤: `analysis/gt_sessions.py` の selftest「input hardening」の深い入れ子（3000 段）が Python 3.14.4 では `RecursionError` にならず受理される | ★ **selftest の深さを 1,000,000 段に上げる**（`gt_sessions.py` の 1 行）。拒否の実装（`RecursionError` を捕まえる）は変えない | 実測: Python 3.14.4 は 3000 / 10000 / 100000 段を解析し、1,000,000 段で `RecursionError`。3.9.6 も 1,000,000 段で `RecursionError`。G-GEAR の版でも同じ向き（深いほど必ず落ちる）。ベースラインの verify が赤だと Mac の全 attempt が verify で落ちる。★ 他の部品（`open_set` / `closed_set` / `build_corpus` / `seal_obs`）の同種の検査は、別の理由（型の検査など）でも拒否されるので 3.14 でも緑だった |

- 確認: 直した後の base で `kit/check.sh` が 20 本すべて緑、`010-acceptance.sh` 失敗 0 件（Mac・Python 3.14.4）。

## 判断 48〜49: Mac の W2 の 004 の merge ゲートのレビューを受けた裁定（2026-09-29・研究者の回答）

★ 004 はループで attempt 1 の `issue_done`。clean な checkout（`loop/004-issue` を detached）で `004-acceptance.sh` 失敗 0 件（✅ 28）。
レビュー: code-reviewer 1 本・security-checker 1 本（並列）。CRITICAL なし。HIGH は 2 件（どちらも一次で確認）。

| # | 論点（出どころ） | 採用 | 理由 |
|---|---|---|---|
| 48 | security HIGH: 送出の確認（`--i-understand-this-sends-keys`）と `SUPPORTED_KEYS` の事前検査が CLI の `run()` にしか無い。006 が `Emitter` / `Backend` を直接使うと素通りし、フラグなしで実キーが出る | ★ **門を `Emitter` に置く**（`allow_send=False` が既定・dryrun 以外は明示が要る・送る前に `SUPPORTED_KEYS` を検査）。**Backend の境界は変えない**（005 / 026 の差し込みの形を保つ） | 006 が使う層で止める。境界を変えると 005 にも波及する |
| 49 | security MEDIUM: `focus_away` の既定の退避先が Finder で、前面化の成功を確かめていない。前面化に失敗すると次の `enter` が Finder に入り、選択中のファイルの改名が始まりうる | ★ **既定をなくし（`away_app` を必須）、activate の後に前面アプリのバンドル ID を読み戻して一致しなければ送出を止める**。退避先は M1 で「キー入力で状態が変わらないアプリ」を選ぶ | 実機でファイルを壊しうる経路を送る前に閉じる |

- ★ 仕様の範囲の直し（メインが段取り）: selftest の否定対照が本物の `main()` で `--backend macos` を起動していた（code-reviewer HIGH・フラグ検査が壊れた瞬間に実際に送る）→ 検査の間だけ `load_backend` を番兵に差し替える／close のキーごとの try・down は送る前に `_held` へ／SIGTERM で close を通す／送る前の計画の検査（down/up の対・必須の欄・重複 ID・`at_ms` の上限・入れ子・サイズ）／`SubprocessError` の終了コード／CLI で `reset_ime` を黙って無視しない／`--validate` の型（bool の `step` / `seq`・keyname の列挙・`reset` の位置）／`marker_gap_ms` の検査／`fullmatch`・`/usr/bin/osascript`／README（擬似キーの時間・ヘッダだけの oracle の後始末・`CGEventSetFlags` の既定フラグの上書きを M1 で確かめる）。

## 判断 50: Mac の W2 の 007 の merge ゲートのレビューを受けた裁定（2026-09-29・研究者の回答）

★ 007 はループで attempt 1 の `issue_done`。clean な checkout（`loop/007-issue` を detached）で `007-acceptance.sh` 失敗 0 件（✅ 14）。
レビュー: code-reviewer 1 本・security-checker 1 本（並列）。CRITICAL なし。security は内容の漏れの経路なし（MEDIUM 2・LOW）。code-reviewer の HIGH 2 件のうち「マウスが IME に届かない」は、S9 のクリック先が IME の候補窓（別プロセス）なので実質は下がる（issue 026 で確認）→ 仕様の範囲で入れる。

| # | 論点（出どころ） | 採用 | 理由 |
|---|---|---|---|
| 50 | code-reviewer MEDIUM: 参照入力欄は確定した文字をメモリ上の本文にため続け（`doCommand` は記録だけ）、IME は `attributedSubstring` 経由で前の試行の文字を左の文脈として読める。変換の結果が試行の順に依存しうる（design.md の「IME は学習する」と同じ型の独立性の崩れ） | ★ **確定のたびに本文を空にする**（未確定が無くなった時点で本文と選択を空に戻す）。README に「通常のテキスト欄と違い左の文脈を与えない」と書く。削除・移動のコマンドは最小限実装する | 試行の独立を保つ。本文がメモリに残る時間も最小になる |

- ★ 仕様の範囲の直し（メインが段取り）: マウスイベントを入力コンテキストへ／`characterIndex(for:)` は `NSNotFound`・`firstRect` の `actualRange` をクランプ／`setMarkedText` の範囲の加算のオーバーフロー／selftest の `--out` が既存のパス（ディレクトリごと）を消す → 既存は拒否し `O_EXCL|O_NOFOLLOW`・0600 で作る（security MEDIUM）／書き込み失敗で exit 1／ログへ書く経路を `record` とヘッダに絞る／focus_in の二重記録／`validAttributesForMarkedText`／selftest で IME への答え（範囲・長さ）を検査／README の主張を「文字列を書かない」に絞り、`vk` の列から打鍵が復元できる旨を書く（security MEDIUM）。

## 判断 51: 012 の merge ゲートの HIGH（main queue が回らない）を 011 の追補で解く（2026-09-29・研究者の回答）

- 事象: 012 の code-reviewer HIGH。macOS のドライバは入力ソースの問い合わせを main queue に積むが、単体ロガーの `main()` はメインスレッドで監視ループを回し main queue を処理しない → 問い合わせが一度も完了せず、JIS のモードキー以外の切替・起動時点の日本語入力が黙って欠測になる（写した元は main queue が回る前提で同期に聞く）。一次で確認し、小さな再現プログラムで陰性対照（回さない → 0 / 10 件）も実測した。
- 選択肢: A = 011 の追補で `main.rs` を直す（写した元と同じ判断に戻す）／ B = 仕様の範囲（警告・Known limits・M1 の手順で各ブロックの先頭に かな）
- **採用: A**。メインが base に入れた: `main.rs` に `run_with_main_queue`（macOS だけ: 記録を別スレッドへ、メインスレッドは main run loop を最大 100 ms ずつ回す。他の OS は従来どおり）・`manifest.json` の `main.rs` を指す 3 エントリの `sha256` の更新（`--update`・`--self` / `--against-upstream` は一致）・`PROVENANCE.internal.md` に記録。
- 確認（Mac）: release ビルド・clippy・`cargo test` 75 件が緑。再現プログラムで回す形が 10 / 10 件を実行（CPU 時間ほぼ 0）。
- ⚠️ 残り: Windows 側は `cfg` で従来の経路のままだが、コンパイルは G-GEAR でしか確かめられない → 次の G-GEAR のセッションで 011 / 013 / 014 の acceptance を回す。012 はこの base を取り込んでから、残りの指摘（警告と件数・タップの復帰の件数と上限・競合・テスト・ドキュメント）を直す。
- ★ 012 の仕様の範囲の直し（メインが段取り・作業用エージェントが `loop/012-issue` で `9bd278d8`）: 入力ソースの doc を実態に合わせ、問い合わせが 2 秒完了しなければ警告を 1 回・完了件数を停止時に出す／`IME_OPEN` への書き込みを `compare_exchange` に（モードキーの書き込みを上書きしない）／タップの再有効化を 2 系統で数えて停止時に出す・連続上限を写した元の 100 に・作り直しは入れず Known limits に／`handle_key` の判断を純粋関数に切り出してテスト（auto-repeat の除外を殺す変異で赤をメインが確認）／タイムアウト後に遅れてできたタップは installed を出さずに畳む／権限のダイアログと Secure Event Input を doc に。security は LOW 3 件だけ（上の doc の 2 件と、作り直しの層が無いこと）。clean な checkout で `012-acceptance.sh` 失敗 0 件（✅ 16）。

## 判断 52〜54: Mac の W2 / W3 を G-GEAR で取り込んだときの直し（2026-09-29・52 / 53 は研究者の回答・54 はメインの実装上の選択）

★ G-GEAR で base（`91289c09`）を取り込み、clean な checkout で merge 済みの全 acceptance 20 本を回した。判断 51 で変えた `main.rs` は Windows でもビルド・テストが通った（011 / 013 / 014 の cargo の項目がすべて緑）。一方で、**全 acceptance が共通の 1 件（`kit/check.sh`）で赤**になった。原因は 004 の `emit/emit.py` の selftest の時間の 3 ケース（Mac でしか検査されていなかった）。

| # | 論点（出どころ） | 採用 | 理由 |
|---|---|---|---|
| 52 | `emit.py` は oracle の時刻を `time.monotonic_ns()` / `time.time_ns()` で取る。G-GEAR の Python 3.11.9 では `monotonic` が `GetTickCount64()`（実測 16 ms 刻み）、`time` が `GetSystemTimeAsFileTime()`（宣言上 15.6 ms。他のプロセスがタイマーを細かくしていると 1 ms）。selftest の試行間の待ち・マーカーの間隔・遅れが 16 ms 刻みで測られて赤。**実データでも Windows の試行の窓と矢印キーの時刻（`nav` の正解）が 16 ms 刻みになる** | ★ **`emit.py` を Python の版によらず高分解能の時計にする**: `t_mono_ns` は待ちと同じ `time.perf_counter_ns()`、Windows の `t_wall_ms` は `GetSystemTimePreciseAsFileTime`（ctypes・標準ライブラリ）。時計の宣言上の分解能が 1 ms より粗ければ `Emitter` が出力を作る前に止まる（`ClockTooCoarse`・exit 2）。004 の追補としてメインが base に入れた | 環境の要件を増やさずに（Python 3.13 以上を必須にせずに）oracle の時刻を 1 ms 以下にする。門は `Emitter` にあるので、006 が `Emitter` を直接使っても効く |
| 53 | 時計を直すと、送出の遅れの 95 パーセンタイル（< 20 ms）が G-GEAR で 23〜56 ms の赤になった。原因は同じ機械で別プロジェクト（`C:\ERRE-Sand_Box`）の重い計算が CPU を 82% 使っていたこと。高い優先度で回すと 0.01〜0.04 ms | ★ **遅れの上限だけを `--selftest --full` に移す**。既定の selftest には負荷に左右されない検査（計画より早く送らない・待ちの下限・時計の分解能と出どころ・粗い時計で止まること）を残し、95 パーセンタイルは値を表示するだけにする。パイロット（M1 / M5）では空いた機械で `--full` を回す | 既定の selftest は全 acceptance とループの verify が毎回回す（入口の規則「重い・環境に左右される検査は既定で回さない」）。機械が忙しいと理由なく赤になり、ループが空回りする |
| 54 | 005 / 006 の `## Dependencies` の `004`: 004 の `issue_done` は Mac の events にだけあり、G-GEAR の events（機械ごと・git 管理外）には無い → `deps_met` が永久に偽で起動しない | ★ **外す**（判断 34 / 47 と同じ形・`issue_done` は手で書かない）。006 の依存は 003 だけになる | 004 の成果物は base にある |

- 確認（G-GEAR・Python 3.11.9）: 既定の selftest 47 件がすべて緑（負荷がある状態で）・`--full` は高い優先度で緑（95 パーセンタイル 0.04 ms）。写しへの変異 4 本がすべて赤: 時計を両方元に戻す／門を外す／行の壁時計だけ `time.time_ns()` に戻す（⚠️ 実測の刻みの検査だけでは、他のプロセスがタイマーを細かくしていると捕まらなかった → `_stamp()` が高分解能の 2 つの関数から時刻を取ることを関数の差し替えで確かめる検査を足した）／単調時計だけ元に戻す。
- ⚠️ Mac: 次の Mac のセッションで `004-acceptance.sh` を回し直す（`emit.py` を変えたため。macOS では `time.time_ns()` と `perf_counter_ns()` を使う）。

## 判断 55〜58: W3 の残り（005 / 006）の merge ゲートのレビューを受けた裁定（2026-09-29・55〜57 は研究者の回答・58 はメインの実装上の選択）

★ 005 / 006 はループで attempt 1 の `issue_done`（1 run・parallel=1・5.36M トークン・$2.60）。clean な checkout で acceptance 失敗 0 件（005 ✅ 19 / 006 ✅ 14）。
レビュー: code-reviewer 2 本（005 / 006）・security-checker 1 本（005+006）。CRITICAL なし。HIGH は 006 の 2 件（code-reviewer）と security の 1 件で、うち 3 件は同じ論点（下の 55）。一次で確かめた: `run_cell.py:370-377` は `focus_cmd` が空なら前面化も確認もせず、終了コード 0 だけを見て最初のマーカーを待ちなしで送る／両バックエンドの `focus_back`（`backend_macos.py:141-162`・`backend_windows.py:181-196`）は「前に出す → 読み戻す → 違えば止める」を持つが runner は使っていない／`reset_cmd` は dryrun・フラグなしでも走る（`:366-369`）／`run.json` はセルのコマンド配列と例外の文字列をそのまま書く（`:314-335`）／`FORMATS.md:174` は「`reset_ime` が真なら `reset` 行」。

| # | 論点（出どころ） | 採用 | 理由 |
|---|---|---|---|
| 55 | 006 code-reviewer HIGH・security HIGH・005 code-reviewer M4 / security M-a: 実キーを送るときに参照入力欄が前面にあることを誰も確かめていない。起動直後は runner を打った端末が前面なので、1 ブロック分の打鍵（`tab`・`enter` を含む）が端末の入力バッファに溜まり、runner の終了後にシェルが実行しうる。送出の途中で前面を奪われても検知しない | ★ **runner がバックエンドで確かめる**: `run_cell.py` は各ブロックの前（最初を含む）に、開いたバックエンドの `focus_back`（前に出す → 読み戻す → 違えば止める）を通す。実バックエンドではセルの `backend_opts` に `focus_back` が要るオプション（`KEY_OPTIONS["focus_back"]`: macOS = `focus_app` / Windows = `focus_window`）を必須にし、無ければ子プロセスを起こす前に exit 2。`focus_cmd` は任意の前処理として残す（非 0 なら従来どおり中止）。★ Windows のバックエンドは `focus_window` を必須にし、`open()` で前面に出して読み戻し（違えば止める）、**押下の直前に毎回** `GetForegroundWindow()` を照合する（呼び出し 1 回。macOS は照合に `osascript` が要り遅いのでブロックの先頭だけ）。★ 004 の Backend の境界（`SUPPORTED_KEYS` / `Backend(opts)` / `open` / `send` / `close`）は変えない（判断 48） | 誤った窓への打鍵はシェルでのコマンドの実行・ファイルの改名になりうる。両バックエンドに読み戻しは既にあり、境界を変えずに runner から使える。Windows は照合が安いので、前面を移すこと自体が安全な停止の手段になる |
| 56 | 006 security M-c: IME のリセット（ユーザー辞書・学習の消去＝取り返せない・学習履歴はその人の語彙）が dryrun・フラグなしのリハーサルでも走る。006 code-reviewer M6: `reset_ime` が真で `reset_cmd` が空のとき何も残らない（FORMATS と食い違う） | ★ **`reset_cmd` は送出のフラグ（`--i-understand-this-sends-keys`）があるときだけ実行する**（dryrun でも同じ）。無ければ実行せず、manifest の `resets` に `skipped` と理由を残す。`reset_ime` が真で `reset_cmd` が空のときも `skipped`。★ `FORMATS.md` の oracle の行の順を「`reset` は `reset_ime` が真で、かつリセットを実行したとき」に直し、実行しなかったリセットは manifest に残すと書いた（メインが 001 の追補として base に入れた。読む側の `pilot/call_types.py`・`pilot/reach.py` は reset 行を任意の区切りとして扱っていて、必須としている部品は無い） | 取り返せない操作は、送出と同じく明示の同意の下でだけ行う。フラグを 1 つに保つ |
| 57 | 006 security M-d: run ディレクトリは Zenodo に寄託する計画だが、`run.json`（セルのコマンド配列・例外の文字列）と子の stderr にユーザー名を含む絶対パスや checkout のパスが入りうる（判断 36 にも反する） | ★ **書くときに置換 ＋ 寄託前の検査**: `run_cell.py` は manifest に書くとき、ホームディレクトリと repo のルートの絶対パスを `~` / `<repo>` に置き換える。子の stderr は寄託しないと README に書く。★ 020 に `pipeline.py --check-deposit <run-dir>...`（寄託する 5 ファイルにホームの絶対パス・ユーザー名・repo のルートがあれば exit 1）と `data.md` の寄託の手順を足した（メインが 020 の回す前に issue を直した） | 置換は取りこぼしうる（子の出力・例外）ので、寄託の直前に機械で止める。再現に要るのは相対の位置だけ |
| 58 | 006 code-reviewer HIGH 1: Windows の `Popen.terminate()` は `TerminateProcess`（強制終了）なのに manifest に `terminated`（穏当に止めた）と書く。ロガーの出力の末尾が失われうる | ★ **子の側は直さない・記録を正確にする**（メインの判断）: 一次で確かめた —— ロガーは「1 行ごとに write と flush」（`kit/logger/src/main.rs:90-93`）、参照入力欄（Windows）も「1 行ごとに OS へ書く」（`kit/refinput-windows/README.md`）。強制終了で書いた行は失われない。→ manifest の記録を実態に合わせ（Windows は強制終了と書く）、README に「子は各記録を生じた時点で OS へ書くこと」を契約として書く。止める順は起動の逆（参照入力欄 → ロガー）、最後のブロックの後の待ち `settle_ms` の既定を正の値にする。子の子（ラッパー経由の起動）は POSIX ではプロセスグループごと、Windows ではプロセスの木ごと止める | 停止の依頼の仕組み（stdin の EOF など）を足すと、merge 済みの 011〜014 と参照入力欄の契約を変えることになる。その必要が一次で無いと確かめられた |

- ★ 仕様の範囲の直し（研究者に問わずメインが段取り）:
  - 005: 差し替えた api を捨てない（`close` の後の `open` で本物を作らない・二重の `open` は拒む）・selftest の冒頭で本物の `_Api` を番兵に替える（code-reviewer M1・security 補足）／keymap の網羅を核の `KEYNAMES` と比べる（常に真だった・M2）／窓は可視・完全一致のタイトルでちょうど 1 つ（`EnumWindows`）・最小化なら元に戻す（M3・L4）／管理者として動いていたら `open()` で止める（security L-e）／戻り値 0 の説明から UIPI の推測を外し `get_last_error()` を載せる・UIPI の取りこぼしは戻り値で見分けられないこと・前景ロック・Windows 11 のタイマー分解能・仮想キーの `wScan` が 0 であること（観測器は仮想キーで判定する）を docstring に（L1〜L3・L7）／selftest の穴（押下だけで前面化・`KEYUP`・keymap の値の型）。
  - 006: 想定外の例外を握りつぶさない（トレースバックを run ディレクトリと stderr に）／OS の版と Python の版を manifest に／`allow_send` がフラグから渡ることを selftest で確かめる／押下の直前に子の生死を同期で確かめる／`{out}` を絶対パスに／時計の分解能の検査を子を起こす前に／計画を 1 回だけ読む／commit を開始時に取り作業ツリーの変更の有無も残す／reset / focus の stderr と失敗の種類を残す／停止の間の SIGTERM・2 回目の Ctrl-C でも全員を止めて manifest を書く／stderr のファイルも排他で作る／Windows で `.bat` / `.cmd` を拒む／例のセルのリセットを失敗する仮コマンドに／README（スリープ・画面ロックを止める・F13〜F19 が他のアプリのホットキーを発火しうる・セルのファイルは実行されるコード・ラッパー経由で起動しない）。
  - 直さない: 006 L19（`emit.py` の私的な関数への依存と事前検査の重複）は核の issue を開き直すことになるので、次に核を触るときに回す。

## 判断 59: `emit.py` の送出の基準を `trial_begin` の刻印そのものにする（2026-09-29・研究者の回答・004 の追補）

- 事象と原因は `blockers.md` B12（既定の selftest が約 1% で「計画より早く送った」になる。基準の `perf_counter()` を刻印より先に取っていた）。
- 選択肢: A = 基準を刻印に揃える／ B = selftest の許容を広げる（oracle のずれは残る）／ C = 記録だけして後で
- **採用: A**。メインが base に入れた: `Emitter._emit` が書いた行を返し、`run_trial` は `start = <trial_begin の t_mono_ns> / 1e9` とする（刻印の単調時計 `perf_counter_ns` と待ちの `perf_counter` は同じ時計）。selftest に「keys are scheduled from the recorded trial_begin timestamp」（`trial_begin` の刻印だけを 5 ms 遅らせる `Emitter` の派生で 2 試行を送り、最小の遅れが -1 ms 以上）を足した。
- 確認（G-GEAR・Python 3.11.9）: 既定の selftest 48 件が緑・style 違反 0 件。写しで基準を元の形に戻す変異で新しいケースが 3 回とも赤。
- ⚠️ Mac: 次の Mac のセッションで `004-acceptance.sh` を回し直す（macOS では `perf_counter_ns` / `perf_counter` はどちらも `mach_absolute_time()`）。

## 判断 60〜61: 023 の worker の Stop（写しと公開物の書き方が両立しない）を仕様の側で解く（2026-09-30・研究者の回答）

- 事象: W5 の 023 の worker が attempt 1 で Status を `blocked` にして止まった（`blocked（受け入れ条件どうしの矛盾）`）。AC2「写しと元の差はプロセス名の行だけ」と判断 36 の書き方（`style_ok`）が両立しない（違反 166 件・すべて 3 本の写しの中）。一次で確かめた: 計測器 2 本（`sample-macos.sh` / `sample-windows.sh`）は注釈の行だけが違反（行末の注釈は無い）、`calibrate-cpu.sh` は画面に出す文言（`echo` / heredoc の本文）も日本語と ★。元の `summarize.py` は校正の値を掛け合わせておらず、`calibrate-cpu.sh` は測定器の陽性対照（手作業の確認）。
- もう 1 点: issue 023 は「写しの表（元のパス・SHA-256・変えた行）を README に書く」としていて、worker の公開 README に GSE のパス（`experiments/20260903-o1-runtime-cost/...`）と「以前の計測から写した」が載った。判断 36 / 43 より前に書いた仕様（機械の門の禁止語には当たらないので `style_ok` は緑だった）。

| # | 論点 | 採用 | 理由 |
|---|---|---|---|
| 60 | 写しと書き方 | ★ **計測器 2 本は実行される行を元と同じに保ち、注釈だけを学術的な英語に訳す**。AC2 を「注釈（`#` の行・`#!` を除く）と空行を除くと、元との差はプロセス名の行だけ」に改め、陽性対照（実行される行を 1 行足すと検出する）を acceptance に足した。★ **`calibrate-cpu.sh` は写さず、同じ測り方を英語で書き直す**（集計には使わない手作業の確認） | 計器の同一性（測るコード）を保ったまま公開物の書き方を守る。校正の文言は出力そのものなので、訳すと「写し」の検査が機械で書けない |
| 61 | 出典の表の置き場 | ★ **`kit/e3/PROVENANCE.internal.md` に移す**（Allowed Files に足した・024 は書き出さない・`_style_check.py` の対象外）。公開の README は計器の中身だけを書き、元のパスと写した関係を書かない。acceptance: README と 4 本に `experiments/20260903` が 0 件・README に `copied` が 0 件・`PROVENANCE.internal.md` に 2 本の元のパスと元の SHA-256 | ロガーと同じ形（判断 43） |

- 段取り: 023 の worktree（worker の `d70e30f4` / `30e321ec`）は片付け、直した issue と acceptance で `--issues 023` を回し直す。

## 判断 62〜63: W5 の 020 の merge ゲートのレビューを受けた裁定（2026-09-30・研究者の回答）

★ 020 はループで attempt 1 の `issue_done`。clean な checkout で `020-acceptance.sh` 失敗 0 件（✅ 28）。寄託前の検査 `--check-deposit`（判断 57）も入っていた。
レビュー: code-reviewer 1 本（HIGH 4・MEDIUM 5・LOW 9）・security-checker 1 本（CRITICAL / HIGH なし・MEDIUM 5・LOW 8）。一次で確かめた: `run.sh:77` は行頭の `frozen_at:` / `sha256:` だけを見る／`pipeline.py:124-126` の `repo_root()` は 2 段しか上がらず `<repo>/papers` を返す／`run_cell.py:141-165` はセルの `label` を未知のキーとして拒み、pipeline はラベルを `cell.label`（無ければ `os`）から取るので同じ OS の 2 セルが必ず重なる／ロガーは `ime_shadow` を `config_gated` に置く（`kit/logger/src/main.rs:71-73`・0 行は判定不能）が Step 0 はそれも「宣言あり」と数える／design.md §1.2 は両 OS 共通の定義 `all` の値も求める／`match.py` の `theta` / `drop_start_while_open` を設定で渡せない。

| # | 論点（出どころ） | 採用 | 理由 |
|---|---|---|---|
| 62 | code-reviewer H3・M3: セルのラベルの出どころ | ★ **セルのファイルに任意のキー `label` を足す**（006 の追補としてメインが base に入れた: `OPTIONAL_KEYS` に `label`・書式は `^[A-Za-z0-9_.+-]{1,64}$`〔照合器の `CELL_RE` と同じ〕・selftest に陽性と陰性・README と例のセル）。★ pipeline は `cell.label` を**必須**にし、`os` への黙った代替をやめる。同じ label の run は**中止していないものが 1 つだけ**（撮り直しの中止分は件数に数える） | ラベルはセルの性質で、出どころの記録（`run.json`）に残るべき。run_cell では任意のまま（dryrun の検査のセルに要らない）にし、解析で必須にする |
| 63 | code-reviewer H1・M1・M2: 凍結の門 | ★ **書式 ＋ 迂回の封じ ＋ 設定の照合**: 印は `frozen_at: YYYY-MM-DD…` と `sha256: <64 桁の 16 進>` をちょうど 1 行ずつ（プレースホルダ・空・コメントやフェンスの中は数えない）。`sha256` は「`config.json`・`SEED`・正解の規則ファイルの順に、各ファイルの SHA-256（16 進）に改行を付けて連ねたもの」の SHA-256 と定義し、`pipeline.py --freeze-hash` で出す。`run.sh` と `pipeline.py`（実データの解析では `--prereg PATH` を必須にする・合成の run だけ免除）の両方で再計算して一致を求める。解析コードの固定は凍結のコミットのタグで行う（M3）。★ `.gitattributes` に `experiment/*.json`・`SEED`・`*.sh`・`gt_rules*.json` の `eol=lf` を足した（機械ごとにハッシュが食い違わないように） | 凍結の後に解析の設定を変えられない・直接呼び出しでも迂回できないことを機械で保証する |

- ★ 仕様の範囲の直し（研究者に問わずメインが段取り）:
  - code-reviewer: H2 `repo_root()` を run_cell と同じ定義（`git rev-parse --show-toplevel`・無ければ 3 段上）に／H4 Step 0 は `ime_shadow` が gated で、正解のセッションが 1 件以上あるのに `ime_shadow` の行が 0 件なら「判定不能」の違反にする（合成のヘッダも実物と同じ `config_gated` に）／M4 各セルで OS の定義と共通の定義 `all` の両方を出す（design §1.2）／M5 `theta` と `drop_start_while_open` を設定で渡す（`clock_offsets_ms` の出どころは M1 / M3 で決める・⚠️ 未決・今は 0）／L4 seed の導き方を書き、合成の生成と注入の乱数を分ける／L6 `--synthetic` の出力先が本番の `results/` なら止め、結果に合成の印／L7 `SEED` の厳密な検査／L8 `CDPATH`／L9 想定外の例外は型名だけで exit 2・失敗したら古い結果を残さない。
  - security: M-A `--pack OUT.zip`（寄託する 5 ファイルだけを決定的に束ね、その束を検査し SHA-256 を出す・`data.md` の手順を「束ねる → 検査 → 寄託 → SHA-256 を記録」に）／M-B 機械に依存しない規則（5 ファイルの中の絶対パスの形〔ドライブ文字・UNC・`/Users/`・`/home/`・`/Volumes/`・MSYS の `/c/`〕をすべて拒み、`~` と `<repo>` で始まるものと相対パスだけを許す）と `--also-user` / `--also-home`（検査した機械を `data.md` に記録）／M-C 中断 run の null のログは無くてよい・`run.json` は必ず見る／M-D 寄託の門でも content-free の検査とハッシュの照合を通す／M-E `data.md` の行に `run.json` の SHA-256 を持たせて照合し、結果の `runs.list` に `manifest_sha256`／L-a `outputs.*.sha256` の書式／L-b `RecursionError`・想定外の例外／L-c 照合済みのバイト列を検査する／L-d 通常ファイルだけ・リンクを拒む・大きさの上限／L-e `--runs-from` はコメントとフェンスの中を読まない・使ったラベルを出す／L-f `--synthetic` は既存を上書きしない／L-h `mktemp` の失敗。

## 判断 64: W5 の 023（回し直し）の merge ゲートのレビューを受けた裁定（2026-09-30・研究者の回答）

★ 023 は判断 60 / 61 で仕様と acceptance を直してから回し直し、attempt 1 で `issue_done`。clean な checkout で `023-acceptance.sh` 失敗 0 件（✅ 27）。
レビュー: code-reviewer 1 本（HIGH 3・MEDIUM 5・LOW 8）・security-checker 1 本（CRITICAL / HIGH なし・MEDIUM 2・LOW 7）。一次で確かめた: 元の `summarize.py` の床は 480 行で、元の計測は 8 時間で 731 行・周期の中央値 39 秒（`notes.md:883-885`）→ worker の README の「4 時間・30 秒間隔で 480 行」は届かず必ず `insufficient`／Windows のサンプラ（写しの実行行）は `Get-Counter` が読めないと CPU に 0 を書き、集計は RSS > 0 の行を在席として数える／観測器の bin 名は 22 文字（`kit/logger/Cargo.toml:18`）。

| # | 論点 | 採用 | 理由 |
|---|---|---|---|
| 64 | E3 の 1 条件あたりの計測時間 | ★ **元の計器と同じ 8 時間・30 秒間隔**（1 晩 1 条件・2 条件 × 2 OS で計 4 晩・M10）。集計の床は**行数 480 と窓の長さ 4 時間以上の両方** | 元の計器の基準（8 時間で 731 行）に揃える。短い窓でレートを代表させない（`notes.md:906-907`） |

- ★ 仕様の範囲の直し（メインが段取り・作業用エージェント）: macOS のプロセス名の切り詰め（Darwin の `p_comm` は 16 文字・`pgrep -x` は切れた名前と照合する見込み → `run_e3.sh` が Darwin では既定を先頭 16 文字に。⚠️ **Mac の実機でまだ確かめていない** → 次の Mac のセッションで `ps -c -o comm=` を見る）／`working` での観測器の入れ替わり（再起動を数え、RSS の傾きを区間ごとに or n/a）／窓の長さの床／OS ごとの量の違いの注記／`conditions.txt` にコア数・OS の版・実行ファイルの SHA-256／Windows のカウンタの事前確認と全部 0 の警告／同名のプロセスの数の事前確認（`idle` はちょうど 1・`working` は 0）／`E3_PROC` の検証・PowerShell へは環境変数で／出力はラベルと basename だけ／値の検査／`calibrate-cpu.sh` の trap と期限／出力先の作成の原子性／selftest の歪んだ列 ほか。★ 写しの実行行は変えない（判断 60）。

## 判断 65: 020 の selftest を既定と `--full` に分け、selftest の間だけ読み込みをキャッシュする（2026-09-30・メインの実装上の選択・研究者が覆せる）

- 事象: 020 の直しの後、`pipeline.py --selftest` が G-GEAR で約 56 秒（入口 `kit/check.sh` の目安 30 秒を超える）。ケースごとに測ると特定の 1 本ではなく分散していて（凍結の門 13.9 秒ほか）、書いた直後のファイルの読み込みが 1 回 60〜80 ms かかることが主因（Windows）。全 acceptance とループの verify が毎回回す。
- 採用: 既定の `--selftest` は各門の代表の変種（陽性 1 つと主な陰性）だけにし（約 17 秒）、全変種は `--selftest --full`（約 29 秒）に回す（入口の規則「重い検査は `--full` へ」）。★ 既定で落とす前の変異 4 本（印の可視行の判定を素通し・`sha256` の照合を外す・gated の 0 行の判定を外す・JSON の復号を外す）がすべて**既定の selftest で赤**になることを確かめた（作業用エージェントとメインの両方）。selftest の間だけ、変わっていないファイルの読み込みを 1 回にするキャッシュ（鍵はパス・更新時刻・大きさ・inode、書いてから 0.3 秒未満のファイルは使わない、`lstat` の検査は毎回）を入れた。本番の解析では無効（`selftest()` が設定し `finally` で戻す）。
- ⚠️ merge ゲートでは `--selftest --full` も回す（2026-09-30 は緑・30 秒）。

## 判断 66: macOS の E3 のプロセス名は切り詰めず完全な名前で照合する（判断 64 の前提の訂正・2026-09-30・研究者の回答）

- 事象: 判断 64 の直しは「Darwin の `p_comm` は 16 文字・`pgrep -x` は切れた名前と照合する見込み」を未確認の前提として、`run_e3.sh` の macOS の既定を `ime-observation-` にし、長い `E3_PROC` を 16 文字に切っていた。
- 実測（Mac・macOS 27.0・単体ロガーの release ビルドを起動）: `ps -c -o comm= -p <pid>` = `ime-observation-logger`（22 文字）／`pgrep -x ime-observation-logger` は一致／`pgrep -x ime-observation-`（`-u <uid>` の有無とも）は一致なし／16 文字に切れるのは `top -l 1 -pid` の COMMAND 列だけ。→ ★ 前提が外れており、直す前の `run_e3.sh idle` は「found 0」で止まる（直す前の版で実測・対照）。
- 採用: `run_e3.sh` の既定を両 OS とも `ime-observation-logger` にし、16 文字への切り詰めを外した。README の該当節と `PROVENANCE.internal.md` の「Not verified here」を実測に合わせた。`pgrep -f` を採らない理由（判断 64 のとき）は変わらない。
- 確認: ロガーを動かした状態で直した `run_e3.sh idle 8 2 <dir>` が exit 0・「processes named ime-observation-logger before the run: 1」・`samples.tsv` に実際の値（CPU 0.17%・RSS 4897 KB）。直す前の版は同条件で exit 3。

## 判断 67〜69: W6（024 公開 repo への書き出し）を回す前に issue を直した（2026-09-30・G-GEAR・研究者の回答）

★ 024 は判断 36 / 42 / 43 より前に書いた部分があり、そのまま回すと worker が Stop 条件で止まる箇所が 3 つあった（2 つ目以降は、メインが使い捨ての試作の書き出しで acceptance を先に通して見つけた）。3 問とも推奨案で確定した。

| # | 論点（出どころ） | 採用 | 理由 |
|---|---|---|---|
| 67 | 024 の秘匿の検査は「書き出す全文で `C:\Users\` / `/Users/` の絶対パスを拒む」だったが、merge 済みの公開物に正当な理由で当たる（一次: 寄託の検査・置換の selftest の架空のパス `kit/analysis/pipeline.py:1446-1474, 1495, 1572`・`kit/run/run_cell.py:1151-1153`、規則の説明文 `pipeline.py:79, 690`・`experiment/data.md:33`）。⚠️ handoff の選択肢 C の「020 の `--check-deposit` と同じ規則（実在の値だけ）」は一次と違った —— 020 は寄託する run のファイル用に絶対パスの形をすべて拒むので、ソースに当てると 020 自身の selftest に当たる | ★ **A: 実在の値＋ユーザー名を伴う形を拒み、明示の架空の名前の一覧だけ通す**。拒む: 書き出す機械のホームディレクトリ（綴りの変種）・repo のルート・ログイン名（3 文字以上・語として）・`--also-user` / `--also-home`、と `<ドライブ>:\Users\<名>`・MSYS の `/<ドライブ>/Users/<名>`・`/Users/<名>`・`/home/<名>`（直前が英数字・`.`・`~`・`/`・`\` などの相対パスは当てない）。通す: 一覧 `alice`・`alice2`・`bob`・`carol`・`dave`・`erin`・`gina`・`harry`・`YAMADA~1`・`name`（定数・実行時に広げない）と名前を伴わない `/Users/`。merge 済みのファイルは変えない | 架空のパスは検査器自身の陰性対照として正当で、読みやすさを保てる。実在の漏れは「実在の値」と「一覧に無い名前」の両方で捕まり、一覧は監査できる。★ 試作で確かめた: この規則は公開物の中で一覧の名前だけに当たる |
| 68 | 単体ロガーは `manifest.json` を埋め込み、その SHA-256 をログのヘッダ `manifest_sha256` に書く（`kit/logger/src/main.rs:56-73`）。書き出しは manifest を書き直すので、repo からビルドしたロガーのログの値は公開 repo のどこにも現れず、「公開したロガーで測った」ことを読者が照合できない（今はどの部品も値の中身を照合していない —— 形だけ） | ★ **パイロットと本計測（M1 / M4 / M5 / M7 / M10）のロガーは書き出した側からビルドする**。024 に「同じ commit からの書き出しは機械によらず同じバイト列（LF に揃える）」と README の手順を足した。acceptance は書き出しの一覧の SHA-256 を表示する（別の機械の acceptance と比べる）。ライセンスの全文はロガーのバイト列に影響しないので、測定用のビルドは `--allow-missing-license` の書き出しから行ってよい | 評価したロガー ＝ 公開したロガー（判断 17）を機械で示せる。写した元との照合（内部の道具）は repo の側で続ける |
| 69 | 逐語コピーの 4 本（`file`: `key_gate.rs` / `ime_compose.rs` / `ime_cloak.rs` / `ime_mode.rs`）は**文字列リテラル**にも日本語を持つ（73 個・異なるもの 72 個。テストの `assert!` / `assert_eq!` / `expect` の失敗メッセージと、`ime_cloak.rs` のコンパイル時の `assert!` 1 個〔写した元のファイル名 `lib.rs` を含む〕。うち 15 行に ★ / ⚠。`excerpt` の範囲には無い）。コメントを除くだけでは書き出し側に残り、検査で必ず止まる | ★ **書き出しが、内部の対訳表 `kit/export/translations.internal.json`（書き出さない）で学術的な英語に置き換える**。ソースの綴りの完全一致で引く・対訳の無いものと使われない項目は exit 1・`to` は ASCII だけで同じ種類のリテラル・書式のプレースホルダの並びを保つ。訳（72 項目）は worker が作り、メインが merge ゲートで確かめる | 振る舞いは変わらず、公開側のテストは英語の説明を保つ。repo の逐語コピーと写した元との照合は変わらない。元が変われば対訳表の食い違いで気づく |

- ★ 仕様の範囲の直し（メインが同時に入れた）:
  - 024 の記述を現行に合わせた: `--against-gse` → 内部の道具 `check_manifest_upstream.internal.py --against-upstream`（判断 42 / 43）・`gse_path` の許可リストと逐語コピーの `.steering/` の許可リストを削除（コメントを除いた後は不要）・除外を `papers/ime-observation/.gitignore` の全部＋`*.internal.*`・`.DS_Store` に・`experiment/results/` の集計 JSON は含める（⚠️ handoff の「`experiment/results/` を書き出さない」は一次〔`experiment/notes.md` の表・M8〕と違った）・書き出す前に元の側で `--self` 相当・`--out` は存在しないパスだけ・リンクとテキストでないファイルは exit 2・出力のファイルは相対パス・当たった値を出さない・公開側の manifest のすべてのエントリの `sha256` を計算し直す（`excerpt` と `new` が同じファイルに載る）。
  - ⚠️ selftest のケース名 2 つを改名した: `comments are stripped from verbatim copies` → `comments are stripped from manifest-listed sources`、`upstream fields are dropped from the public manifest` → `internal fields are dropped from the public manifest`（旧名は判断 43 の関係の語に当たり、acceptance の AC9〔書き出した全体の `_style_check.py`〕と両立しなかった —— 判断 42 で名付けたあと判断 43 で検査器に語が足された）。
  - acceptance に足した: 書き出した側の `cargo test --locked`（ロガー）・`kit/check.sh`・全 `*.rs` の `rustfmt --edition 2021` 構文解析（★ 別の OS の専用ファイルは G-GEAR ではコンパイルされないので、構文だけは両 OS で確かめる）・CR が無い・一覧の SHA-256 の表示・公開側の manifest の欄の集合・逐語コピーの範囲が ASCII だけ・既存の書き出し先を消さない・★ 実物の写しに 6 種類（被験者 ID・ホーム・一覧に無い名前・`.steering/`・`GSE`・対訳の無い日本語のリテラル〔写しの manifest を直して元の側の照合は緑にしておく〕）を混ぜる陰性対照と、混ぜない写しの陽性対照。
  - `_style_check.py` を直した: 明示したファイル（`style_ok` は `git diff` の名前を直接渡す）でも `*.internal.*` を対象外にする（判断 43 の「対象外」と食い違っていた・selftest に 2 ケース・直す前の形の変異で赤）。→ 対訳表（日本語の元の綴りを持つ）が `style_ok` で止まらない。
- ★ acceptance の検証（メインが使い捨ての試作 `export.py` と仮の対訳表で・scratch の worktree）: 正しい試作で失敗 0 件（約 2 分 20 秒・91 ファイル）。試作への変異がそれぞれ狙った検査で赤: コメントを残す（＋試作自身の禁止語の検査を外す）→ AC9 の違反 1258 件・AC8b ／ 出どころの欄を残す → AC4 の欄の集合・出どころの欄の grep ／ 被験者 ID・禁止語・名前つきの形・実在の値の検査をそれぞれ外す → AC8 の該当する陰性対照だけが赤。export.py の無い base では 51 件の赤（異常終了なし）。
  - ⚠️ 検証で直した acceptance の穴: (1) 実在の値の陰性対照は、ホームが名前つきの形の規則にも当たるので実在の値の規則を切り分けられていなかった（その規則を外した変異でも緑）→ `--also-home` / `--also-user` に形の規則に当たらない値を渡す対照と、渡さなければ通る陽性対照を足した。(2) その値を `/opt/...` にすると Windows の git-bash が引数を `C:/Program Files/Git/opt/...` に書き換えて一致しなくなった → ドライブ文字の形 `Z:\lab\zed-home` にした。

## 判断 70〜71: 024 の merge ゲートのレビューを受けた裁定（2026-09-30・研究者の回答）

★ 024 はループで attempt 1 の `issue_done`（約 17 分・`a193c751`）。clean な checkout（`C:/wt/clean-024`）で `024-acceptance.sh` 失敗 0 件（✅ 58・一覧の SHA-256 `31c8e324…`・91 ファイル）。対訳表 72 項目はメインが全件読んだ（意味を保つ・プレースホルダが一致・`lib.rs` は訳から消えている）。
レビュー: code-reviewer（HIGH 1・MEDIUM 4・LOW 7）・security-checker（HIGH 2・MEDIUM 4・LOW 5）。どちらも CRITICAL なし。一次で確かめた: 被験者 ID の規則 `(?<![A-Za-z0-9_])P\d{3}(?![A-Za-z0-9_])`（`export.py:75`）は `P017_macos.json`・`run_P017` を通す（両レビューが一致）／判断 67 (b) の規則（`export.py:82-90`）は `C:\Users\山田\x`・`/Users/山田/x`・`file:///Users/zed/x`・`\\?\C:\Users\zed`・`/mnt/c/Users/zed/x` に当たらず、`/Users/alice+zed/x`・`/Users/alice@corp/x`・`/home/bob%20x` は名前が途中で切れて一覧の名前として通る（関数を import して実測）／`collect()`（`export.py:308-339`）は作業ツリーを歩き、除外は論文の `.gitignore` の型の直書きだけ。

| # | 論点（出どころ） | 採用 | 理由 |
|---|---|---|---|
| 70 | security HIGH・code MEDIUM: 作業ツリーをそのまま読むので、repo 直下の `.gitignore` だけが無視する秘密（`.env`・`*.pem`・`*age-identity*`・`*token*.json`・`credentials.json`・`g1-submit*.json`・`*.log` など）や、未追跡のメモ・未コミットの変更が、テキストなら公開の書き出しに入る（秘匿の検査は鍵やトークンの中身を探さない）。判断 68 の「同じ commit からは同じバイト列」も成り立たない | ★ **git の作業ツリーの中なら、書き出すファイルはすべて追跡済みで HEAD と一致していること**（違えば exit 2）。**秘密の名前の型**は git の有無によらず exit 2。README に「リリースする commit の新しい clone から書き出す」。git の無い一時的な写しは今のまま | 判断 68 を機械で保証し、未追跡の秘密が構造的に入らない |
| 71 | 両レビュー MEDIUM: 判断 67 (b) の抜け（上の実測） | ★ **絶対パスの字句で判定する**: 絶対パスの字句（`/`・`\`・ドライブ文字・`file:` で始まる）の成分に `Users` / `home` があれば、次の成分全体（途中で切らない・ASCII 以外を含む）を名前として一覧と完全一致で照合する。相対パスは字句が絶対パスでないので当てない。エスケープを戻した行にも当てる | 判断 67 の左の境界の意図（相対パスを外す）をそのまま書き直し、絶対パスの抜けを閉じる |

- ★ 仕様の範囲の直し（研究者に問わずメインが段取り）: (a) の実在の値から左の境界を外す（worker が付けていた・仕様と `pipeline.py` の先例より弱い）／被験者 ID の境界に `_` を含めない／ファイルの相対パスも検査する／Windows のジャンクションを止める（Python 3.11 の `os.path.islink` は偽）／除外の比較を大文字小文字を問わずに・`.gitignore` と除外の定数の一致を確かめる／書き出した逐語コピーの範囲が ASCII だけであることを `export.py` 自身も確かめる／コメントを除いた行の `rstrip` を除いたコメントの直前の空白だけに／目印の制御文字が元にあれば止める／excerpt の範囲の重なり／対訳の `to` の閉じ引用符・制御文字・重複／`--also-user` が 3 文字未満なら exit 2／後始末（親を作らない・消し損ねの警告・想定外の例外は exit 2）／冒頭の説明の文言。selftest に 6 ケース、acceptance に陰性対照 10 本（`P017_windows`・`file:///Users/`・`\\?\C:\Users\`・ASCII でない名前・名前に被験者 ID を持つファイル・`.env`・`--also-user` 2 文字・一時的な git repo の陽性 1 本と陰性 2 本）を足した。
- 直さない: 成功の行と `check_manifest.py` の出力の末尾に絶対パスが出うる（手元のコンソールだけ）／小文字の `p017`（被験者 ID は大文字の `P` の約束・判断 25）。
- ★ 直しと確認（2026-09-30）: 作業用エージェント（Sonnet）が `loop/024-issue` で直した（`24264d40` 本体・`d8e3f1d9` 書き出しが自分の selftest の語と README の例に当たるのを連結と言い換えで直す・`9cf4eac9` selftest に被験者 ID の `_` 接続の形）。メインが確かめた: 直す前の版（`a193c751`）では新しい検査 15 項目がすべて赤／直した版の clean な checkout で最新の acceptance（`5540df1e`）失敗 0 件（✅ 74・一覧の SHA-256 `9e586e52…`・91 ファイル）／写しへの変異 7 本（`_` の境界を戻す・git の規則を外す・秘密の名前を外す・絶対パスの字句の判定を外す・エスケープを戻さない・ファイル名を見ない・reparse point を見ない）がすべて selftest で赤（⚠️ `_` の境界の変異は最初 selftest が緑で acceptance の実物の写しだけが捕まえた → selftest に入力を足させた）。→ `c6305340` で base へ merge。
- ⚠️ 残る LOW（記録だけ）: JSON の中でさらにエスケープした綴り（区切りのバックスラッシュが 4 つ続く形）は 1 回だけ戻すので名前つきの形を見逃しうる（起こりにくい）。

## 判断 72〜73: W6 の後 —— main への merge と、凍結を公開で示す方法（2026-09-30・G-GEAR・研究者の回答）

★ 着手時に測り直した事実（一次）: base は origin と一致（`ed9c0ac7`）・origin/main より 107 コミット後ろ / 171 コミット先。main との差は `papers/`（97 ファイル・36,231 行）と `.steering/` のほかに 4 ファイル（`.gitattributes`・`docs/experiment-tracking.md`・`docs/repository-structure.md`・`.codex/budget.json`）。`git merge-tree` で試すと衝突は 2 件（`.codex/budget.json`・`.steering/_handoff/next-session-ime-paper-mac.md` の add/add）。このブランチの CI（push で走る）は `8bcf2a81`・`b2e284e2` で緑。⚠️ Codex の台帳は main と合算すると 2026-09-30 がすでに 546,201（main 471,884 / 8 回 ＋ このブランチ 74,317 / 1 回）で、1 日の上限 300,000 を超えている（このブランチの台帳だけを見るとガードは通る —— 台帳がブランチごとに分かれる既知の穴）。
★ BRM の規程（2026-09-30 に一次で確認・submission guidelines の Open Practices）: 事前登録は必須でない。Open Practices Statement の例文は逐語 "Materials and analysis code are available at (url for the site hosting the data and materials). None of the reported studies were preregistered." と "Stimuli, validation data and analysis code are available at (url for the site hosting the data and materials). Validation study 1 was preregistered (url for the preregistration)." → 事前登録したと書くなら、事前登録の URL を載せる形。

| # | 論点 | 採用 | 理由 |
|---|---|---|---|
| 72 | `feature/ime-eval-kit` を main へ merge するか（W6 の後・研究者の判断と決めてあった） | ★ **今日（2026-09-30）merge する。Codex の 1 日の上限を一時的に引き上げて /cross-review を回す**（研究者の選択。メインの推奨は「Codex は予算の戻る 10-01」だった）。手順: origin/main を base に取り込む（台帳は合算・Mac の handoff は base の新しい方）→ push → /cross-review 2 巡 ∥ security-checker → 上限を 300,000 に戻す → PR → CI 緑なら merge（git-workflow ルール 6）。★ Codex に渡す範囲は **GSE 本体に入る 3 ファイル（`.gitattributes`・`docs/experiment-tracking.md`・`docs/repository-structure.md`）と公開の境界（`kit/export/export.py`・`kit/export/translations.internal.json`・`issues/024-acceptance.sh`）の 6 ファイル・1,774 行**（手動承認の閾値 2,000 未満）。上限は 300,000 → **750,000**（2 巡ぶんの余裕 約 200,000）。`today.tokens_used` は改竄しない | W1〜W6 はすべて issue ごとの merge ゲート（code-reviewer ＋ security-checker・両 OS の acceptance）を通っている。main との乖離は日ごとに広がる。papers/ の全体（36,231 行）は Codex に渡せないので、main に新しく入る部分と公開の境界に絞る |
| 73 | 事前登録の凍結（M3 = macOS 版／M6 = Windows 版の追補）を公開で示す方法（2026-09-30 に G-GEAR のセッションで研究者に指摘した・未決だった） | ★ **凍結した `experiment/preregistration.md` を OSF Registries に登録する**（研究者の選択・メインの推奨と同じ）。登録には凍結の印（`frozen_at:` / `sha256:`）と、凍結の commit の書き出しの一覧の SHA-256（024・判断 68）を載せる → 後で作る公開 repo のコードと照合できる。★ 登録は**外部への操作なので研究者が行う**（または承認を得て行う）。★ 登録の日時は、その OS の最初の本計測の run（M4 / M7）より前でなければならない | OSF の一次（help.osf.io「Welcome to Registrations & Preregistrations」）: 逐語 "Once you submit a registration, you will not be able to edit or make changes to it or any associated files." ／ "You can embargo it for up to four years." ／ 取り下げても "basic metadata (e.g. title, contributors, DOI, etc.)" と取り下げの理由は残る。費用: 逐語 "The OSF is a free open-source software project"（help.osf.io の FAQ。⚠️ cos.io の $5,000 は機関が自前の登録所を持つ場合の料金で、個人の登録ではない）。BRM の例文の "url for the preregistration" にそのまま使え、読者（心理学）に通りがよい。git の commit の日時は書き手が書けるので第三者の証拠として弱い（案 c を採らない理由） |

- ★ 未決（M3 / M6 で研究者が決める）: (1) エンバーゴ（本計測の間は中身を伏せる・最長 4 年）を使うか、すぐ公開するか。(2) M6 の追補を別の登録にするか、OSF の登録の更新の仕組みを使うか（⚠️ 更新の仕組みは一次で確かめていない → M6 の前に確かめる）。(3) 登録する文書は公開物と同じ規約（学術的な英語・GSE への言及なし）で書く —— `preregistration.md` は `papers/` の中にあるので `_style_check.py` と書き出しの検査を通る。
- `_issue-plan.md` §5 の M3 / M6 の Done に「OSF の登録の URL と登録の日時を `experiment/notes.md` に記録し、登録の日時が最初の本計測の run より前」を足した。

## 判断 74〜76: main への merge の前の /cross-review 1 巡目を受けた裁定（2026-09-30・研究者の回答）

★ レビュー（範囲は判断 72 の 6 ファイル・`c11b8b80..3ba24091`）: code-reviewer（CRITICAL / HIGH 0・MEDIUM 2・LOW 8）・security-checker（CRITICAL / HIGH 0・MEDIUM 4・LOW 6）・Codex（P1 2・P2 1・`--ack-filtered`〔B14〕・50,317 トークン）。
一次で確かめた: `git_top`（`export.py:436-437`）は git が見つからないと `None` を返し、判断 70 の `check_committed` を飛ばす（両 Claude が一致）／`WORD_RULES`（`:83-95`）は `_style_check.py` の `FORBIDDEN`（`:31-45`）の internal-ref・relation と地の文の日本語を持たない（両 Claude が一致）／対訳表は `excluded()` の `.internal.` に当たるので `check_committed` の対象外で、`load_table`（`:474-`）はリンクを確かめない（Codex）／`collect()`（`:382-`）の `os.walk` に `onerror` が無い（Codex）／`names_a_user`（`:634-`）は空の成分を名前にしない（`/Users//zed`・Codex と security が一致）・`_TOKEN_START`（`:99`）の後読みが `:` と `/` を除くので `root:/Users/zed`・`https://host/C:/Users/zed` が字句にならない（両 Claude）／`BRACKETED_REF`（`:96`）で `[P017]` が通る（両 Claude）／`SECRET_NAMES`（`:70-71`）に `*token*.txt`・`id_rsa*` などが無く、中身の署名も見ない（両 Claude）／`#!` で始まる `.rs`（`#![…]`）も 0755（`:767`）／`--out` は元の dir の外なら repo の中でも通る（`:725`）／acceptance の写した元のファイル名の grep が部分一致（`024-acceptance.sh:91-95`・`run_logger.rs` で誤って赤）。

| # | 論点 | 採用 | 理由 |
|---|---|---|---|
| 74 | security M4: 公開する `export.py` 自身が、禁止語を連結で作る形（`"G"+"SE"`・`"src"+"-tauri"`・`"."+"steering"`・データ用 repo の名前・`g1-submit` / `o1_submit`・`upstream` の欄名）で内部の名前を運び、読者は非公開の元から写したことも読める（判断 36 / 43 と衝突・連結の形は 024.md の仕様どおり） | ★ **書き出し器を公開しない**: `kit/export/` の 3 ファイルを `*.internal.*` に改名する（`export.py` → `export.internal.py`・`README.md` → `README.internal.md`・対訳表はそのまま）。公開の `README.md` の表から `kit/export/` の行を消す | 読者は非公開の元を持たないので書き出し器を動かせず、公開しても役に立たない一方で、写した元との関係だけを明かす。★ 書き出し器の中には内部の語をそのまま書いてよくなる |
| 75 | code M2・security M3: 公開の最後の門（書き出し）は `_style_check.py` の規則の一部しか見ない。M1〜M11 で直接コミットした文書が acceptance を通らずに M12 の公開まで届く | ★ **書き出しが全規則を回す**: 書き出しの最後に、出力の dir に `_style_check.py --root <出力> .` を回し、違反が 1 件でもあれば出力を消して exit 1（ファイルと行と種類だけを出し、当たった値は出さない）。道具の場所は `--style-check PATH`、省けば元を含む git の作業ツリーの頂点からの `.steering/20260927-ime-observation-paper-eval-design/issues/_style_check.py`（`papers/README.md` が機械の門として名指す場所）。見つからない・道具が exit 2・異常終了のときは出力を消して exit 2（★ 黙って飛ばさない） | 公開は研究者が手で行うので、手順の段ではなく機械の門にする。★ 規則を書き出し器に写さない（写すと 2 つが食い違う） |
| 76 | 両 Claude の LOW: 被験者 ID の検査は角括弧の `[P…]` を文献番号として先に消すので、`[P017]`・`[P017, P021]` が通る | ★ **例外をやめる**: `BRACKETED_REF` による消去をやめ、角括弧の中の被験者 ID の形も止める。`papers/README.md` の「文献番号のように角括弧で囲んだ `[P…]` は別」を直し、公開物では非公開の書誌の番号 `[Pn]` を使わない（普通の学術的な引用を使う）と書く | `[Pn]` は非公開の書誌の番号で、公開物の読者に意味が無い。一次で数えると、公開物の中の `[Pn]` は逐語コピーのコメント（書き出しで消える）と selftest だけで、地の文には 0 件 |

- ★ 仕様の範囲の直し（研究者に問わずメインが段取り・024.md の追補に書いた）:
  - (a) git が見つからない（`FileNotFoundError`）ときは、元の dir から上へ `.git`（dir でも file でも）を探し、あれば exit 2（git の作業ツリーの中では git が要る）。`_git_env` は `GIT_CEILING_DIRECTORIES`・`GIT_DISCOVERY_ACROSS_FILESYSTEM` も消す。git の無い一時的な写しは今のまま。
  - (b) 対訳表は書き出さないが出力を変える入力なので、git の作業ツリーの中なら追跡済みで HEAD と一致を求める。リンクなら exit 2。
  - (c) `os.walk` の `onerror` で exit 2（読めない dir）。git の作業ツリーの中なら、追跡済みで除外に当たらないファイルがすべて集められたことを確かめる（欠けたら exit 2）。
  - (d) index の `assume-unchanged` / `skip-worktree` の印（`git ls-files -v` の小文字・`S`）が書き出すファイルか対訳表にあれば exit 2。
  - (e) 秘密の名前の型を足す（大文字小文字を問わない）: `*token*.txt`・`*.token`・`*.env`・`key.txt`・`id_rsa*`・`id_ed25519*`・`id_ecdsa*`・`id_dsa*`・`.netrc`・`_netrc`・`.npmrc`・`.pypirc`・`.git-credentials`・`credentials`・`*.ppk`・`*.asc`・`*secret*`。中身の署名（age の秘密鍵の頭・PEM の秘密鍵の BEGIN 行・GitHub / GitLab のトークンの頭・AWS のアクセスキーの形・Slack のトークンの頭）に当たれば exit 2（値は出さない）。止めるときの文言に「名前が偶然当たったなら改名する」。★ 署名は連結などで組み立て、差分に秘密に見える綴りをそのまま書かない（Codex の前の機密フィルタが止める・B14）。
  - (f) 絶対パスの字句: 連続する区切り（`/Users//zed`）は空の成分を飛ばして次の成分を名前にする。`:` の直後の絶対パス（`zed@labhost:/home/zed`・`root:/Users/zed`・`path:C:\Users\zed`）と URL の path（`https://host/C:/Users/zed`・`sftp://host/Users/zed`・`vscode://file/C:/Users/zed`）も字句として拾う。相対パス（直前が英数字・`.`・`~`）は今のまま当てない。
  - (g) 書き出す機械のホスト名（`socket.gethostname()` と環境変数 `COMPUTERNAME` / `HOSTNAME`・3 文字以上・語として・大文字小文字を問わない）を実在の値の規則に足す。README.internal の手順に「両方の開発機の `--also-user` / `--also-home` を渡す」。
  - (h) 語の検査を外すのは `kit/corpus/data/` の `*.jsonl`（`_CORPUS_JSONL` に一致するファイル）だけにする。
  - (i) `.internal.` の形でないのに名前に `internal` を語として含むファイル（`(^|[._-])internal([._-]|$)`・大文字小文字を問わない）は exit 2（黙って書き出さず、黙って除かず、改名を求める）。
  - (j) 実行権限は 1 行目が `#!/` で始まるファイルだけ（`#![` を除く）。
  - (k) `--out` が元を含む git の作業ツリーの中なら exit 2。
  - (l) acceptance（メインが書く）: 写した元のファイル名の grep を語として行い、書き出しに実在するファイル名は除く。
  - (m) 文書（メインが直す）: `docs/repository-structure.md` の「置くべきでないもの: 生ログ」に corpus の例外。`papers/README.md` の逐語コピーの例外の文（判断 69 の後）・`[P…]` の例外（判断 76）・書き出し器（判断 74）。
- 直さない（記録だけ）: `.csv` / `.tsv` / `.json` / `.txt` の生データがコミットされていれば書き出される（拡張子で判定し、`papers/README.md` の約束に頼る。content-free の集計 JSON を公開するため）／Windows で書き出すと実行権限が付かない（README.internal に「公開 repo は macOS か Linux で作る、または `git update-index --chmod=+x`」と書く）。

## 判断 77: (f) の「連続する区切り」は同じ区切り文字の連なりだけにする（2026-09-30・メインの実装上の選択・研究者が覆せる）

- 背景: 作業用エージェント（Sonnet・`loop/024-fix2`）が (f) を字義どおり「空の成分をすべて飛ばす」で実装すると、実物の公開物 `kit/analysis/pipeline.py:1481` に当たって書き出しが止まった（Stop 条件・acceptance 29 件の赤はすべてこの波及）。当たったのは 020 の寄託の検査の selftest の綴り `b"\\/home\\/x"`（Python のバイト列のリテラルで、中身は JSON の中でさらにエスケープした `/home/x`・名前 `x` は架空）。
- 採用: 空の成分を飛ばすのは、`Users` / `home` の後が**同じ区切り文字の連なり**（`//`・`\\`・`///`）のときだけ。`/` と `\` が混ざった連なり（`\/`・`\\/`）は飛ばさない（エージェントの読み・`e6932553`。メインが docstring と README.internal を実装に合わせた・`d8db7a80`）。
- 理由: 指摘の形（Codex・security: `/Users//zed`・`/home//zed`）はすべて同じ文字の連なり。混ぜた連なりは JSON の二重エスケープの綴りで、判断 70〜71 で「直さない LOW」と記録した形と同じ範囲（一重のエスケープ `\/home\/zed` はアンエスケープした行で捕まる）。★ merge 済みのファイルを変えない（判断 67）。架空の名前の一覧を広げない。

## 判断 78: /cross-review 2 巡目を受けた裁定 —— 混ざった区切りも飛ばし、テストの架空の名前を一覧の名前にする（2026-09-30・研究者の回答）

★ レビュー（範囲は `3ba24091..41516d71` の直し・6 ファイル）: Codex（P1 2・P2 1・43,075 トークン・機密フィルタは当たりなし）・code-reviewer（CRITICAL / HIGH 0・MEDIUM 4・LOW 8）・security-checker（CRITICAL / HIGH 0・MEDIUM 1・LOW 5）。
一次で確かめた（関数を読み込んで実測）: `names_a_user` は `C:/Users/\zed/x`・`/Users/./zed` を通す／`https://stackoverflow.com/users/12345/name`・`https://github.com/users/octocat/projects/1`・`https://example.org/home/docs` を利用者のパスとして止める（★ 追補 2 の (f) で `:` の直後を字句にした副作用の誤検知）／PGP の秘密鍵の BEGIN 行（`… KEY BLOCK-----`）に当たらない／`check_secret_content` は対訳の置き換えの前だけ（`export.internal.py:889` → 変換は `:893`）／`resolve_style_tool` はファイルの有無しか見ない／`git_top` の「not a git repository」の枝は `.git` を探さずに `None`（`:487-488`）。

| # | 論点 | 採用 | 理由 |
|---|---|---|---|
| 78 | Codex P1: `/` と `\` が混ざった区切り（`C:/Users/\zed/x`）の後の名前を見逃す（判断 77 で狭めたため） | ★ **テストの名前を変えて塞ぐ**: `kit/analysis/pipeline.py:1481` の selftest の架空の名前 `x`（`b"\\u002fhome\\u002fx"`・`b"\\/home\\/x"`）を一覧の名前 `alice` に変え、書き出しの (f) は**区切りの連なりを混ざっていても飛ばし、`.` だけの成分も飛ばして**次の成分を名前にする。判断 77 を置き換える | pipeline.py の寄託の検査は名前によらず絶対パスの形をすべて拒むので、名前を変えても selftest の意味は変わらない。混ざった区切りと、判断 70〜71 で記録した LOW（JSON の二重エスケープ）の両方が閉じる。変えるのはテストの文字列 2 つだけ（★ 判断 67 の「merge 済みのファイルは変えない」の例外として研究者が認めた） |

- ⚠️ 追記（メインの実測・acceptance を直す前の版で回して判明）: Codex の例 `C:/Users/\zed/x` は、直す前の版でもエスケープを戻した行（`\z` の `\` が落ちる）で捕まっていた。捕まらないのは戻した後も混ざったままの綴り（`/\\zed`）で、acceptance の陰性対照はこちらに直した（直す前の版で赤・既存の検査 118 件は緑・新しい検査 21 件が赤）。

- ⚠️ 訂正（2026-09-30・作業用エージェントの実測）: 名前は `alice` ではなく **`harry`**（同じ架空の名前の一覧）にした。pipeline.py の selftest（`_case_deposit_paths`）はログイン名を `alice` にしているので、パスの名前が `alice` だと「ログイン名」の規則にも当たり、期待（絶対パスだけ）と食い違って selftest が赤になった（`85d0219d` の時点で 9 件中 1 件）。上の表の「名前を変えても selftest の意味は変わらない」は、名前がログイン名と重ならない限りで正しい。研究者の選んだ「一覧の架空の名前に変える」の範囲内の選択（`f2d14f79`）。
- ★ 仕様の範囲の直し（研究者に問わずメインが段取り・024.md の追補 3 に書いた）:
  - (a) 中身の署名を足す: PGP の秘密鍵の BEGIN 行（`PRIVATE KEY BLOCK-----` も）・Anthropic（`sk-ant-`）・OpenAI（`sk-proj-`）・Google（`AIza`）・GitHub の refresh token（`ghr_`）・AWS の一時キー（`ASIA`）。★ 署名の検査を**対訳の置き換えの後の出力**にも、**エスケープを戻した行**にもかける（exit 2・値は出さない）。
  - (b) `git_top` の「not a git repository」の枝でも上へ `.git` を探し、あれば exit 2（prune された worktree・壊れた `.git`・ファイルシステムの境界）。
  - (c) 検査の道具を commit に固定する: 元が git の作業ツリーの中なら、道具（既定の場所でも `--style-check` でも）は**道具を含む git の作業ツリーで追跡済み・HEAD と一致・index の印なし**でなければ exit 2。元が git の外（一時的な写し）なら今のまま。
  - (d) 検査の道具が読まない種類のファイルを書き出さない: 書き出すファイルは、拡張子が `.py`・`.rs`・`.sh`・`.md`・`.json`・`.toml`・`.swift`・`.txt`・`.cff` か、名前が `.gitignore`・`SEED`・`Cargo.lock`・`LICENSE-CODE`・`LICENSE-DATA` のどれか（違えば exit 2・「道具に種類を足すか、ファイルを除く」）。`kit/corpus/data/` の下は直下の `*.jsonl` だけ（それ以外は exit 2）。
  - (e) URL の誤検知: `http://`・`https://` の URL の path では、ドライブ文字の形（`/C:/Users/<名>`）だけを利用者のパスとして扱う（web の `/users/<id>`・`/home/<x>` は通す）。他の scheme（`file`・`sftp`・`scp`・`ssh`・`smb`・`vscode` など）は今の規則のまま。
  - (f) 出力を一時的な兄弟の dir に書き、manifest の照合と書き方の検査を通ってから `--out` へ改名する（途中で止められても「完成品に見える」出力を残さない）。
  - (g) コンパイラのフラグの形（空白・行頭・引用符の直後の `-I` / `-L` / `-F` に続く絶対パス・`-L/Users/zed/lib`）も字句にする。
  - (h) `internal` を含む名前を広げる: 英字に挟まれていない `internal`（大文字小文字を問わない・`internal2.md`・`internal notes.md`・`notes(internal).md`）と、英小文字の直後の `Internal`（`notesInternal.md`）。`internals`・`international` は通す。
  - (i) 秘密の名前の型を dir 名にも当てる。足す: `.ssh`・`.gnupg`・`.aws`・`.docker`・`.kube`・`.pgpass`。
  - (j) ホスト名の規則は `localhost` を探さない。README.internal の手順に「もう片方の開発機のホスト名も `--also-user` で渡す」。
  - (k) 実行権限は 1 行目が `#!` ＋ 任意の空白 ＋ `/` のファイル（`#! /bin/sh` も）。`#![` は除く。
  - (l) 対訳表が追跡済みなら、作業ツリーに無くても commit の検査の対象にする（消した表が検査から漏れない）。
  - (m) README.internal: 名前の型の誤検知の例（`tokenizer_notes.txt`・`secret-sharing.md`・`*.asc` の公開署名）と、直さない形を書く。
  - (n) acceptance（メインが書く）: `kit/export` の grep を書き出しの全体に・追補 3 の陰性対照（混ざった区切り・`/./`・`-L/Users/<名>`・PGP と `sk-ant-` の中身・秘密の dir 名・読まない種類 `.tex`・corpus の `.jsonl` でないファイル〔追補 2 の (h) の期待を exit 2 に改める〕・git の元で追跡されていない検査の道具）と、URL の陽性対照 3 本。
- 直さない（記録だけ）: 空白を含むパス（`C:\Documents and Settings\<名>`・字句は空白で切れる）／`_style_check.py` が JSON の日本語を `reason` / `_note` だけで見て、`.txt` / `.cff` の日本語を見ないこと（シナリオの JSON は日本語のデータを正当に持つ・道具の設計）／`localhost` 以外のよくある語のホスト名（止める側に倒れる）。

## 判断 79: M0 のコーパスは新字新仮名の 12 作品・`--per-work 150`・`--seed 1`（2026-09-30・研究者の承認・Mac）

- **背景**: M0（`_issue-plan.md` §5）で作品を選び、青空文庫から取得する（研究者の承認が要る）。一次で確かめた下限: E2 の閉集合は K = 1000（design.md §2）→ 1,000 句以上／022 の作品単位の分割は `_MIN_WORKS_FOR_SPLIT` = 5 作品以上／1 シナリオ = 75 × 3 速さ = 225 試行（design.md §1.5）／歴史的仮名づかいの読みの句は捨てられ、旧仮名の作品の読みは実辞書で確かめていない（`kit/corpus/README.md` Known limitations）。
- **選択肢**: A: 新字新仮名の 12 作品（小説・随筆・評論を混ぜる）・`--per-work 150`（最大 1,800 句）/ B: 小説 6 作品・`--per-work 200`（最大 1,200 句）/ C: 研究者が指定
- **採用**: A（研究者が AskUserQuestion で推奨を選択）
- **中身**: 漱石『坊っちゃん』『こころ』・芥川『河童』・太宰『人間失格』『斜陽』・賢治『銀河鉄道の夜』（000456）・寺田寅彦『柿の種』・坂口安吾『堕落論』（042620）・織田作之助『夫婦善哉』・林芙美子『放浪記（初出）』・中谷宇吉郎『雪』（052468）・岡本綺堂『半七捕物帳 01 お文の魂』（001293）。作品 ID・URL・文字遣い・著作権フラグは青空文庫の公式の一覧 CSV（`list_person_all_extended_utf8.zip`）で確かめた（12 作品すべて新字新仮名・作品著作権フラグ「なし」）。
- **理由**: A は K = 1000 と作品単位の分割の両方に余裕があり、作品単位で分けたときの学習側の作品数が多い。文体を小説に偏らせない（E2 の攻撃者の言語モデルとの文体のずれを少しでも減らす・design.md §2）。
- **結果**: 1,800 句（各作品 150・候補は最少の『堕落論』で 241）・読みの長さ 6〜30（中央値 16）・SHA-256 `c8f890cb4d0848bf04e6d7d95efe4e4d3dfd02a23eb1c7f103344f14d13e4620`・`SudachiPy==0.7.0`・`sudachidict-core==20260723.1`。2 回の書き出しでバイト一致・`--validate` exit 0・`kit/check.sh` 緑・`_style_check.py` 違反 0 件・書き出し器が通る（91 ファイル）。仮の config（selftest の値・n = 75）で両 OS の計画を作ると、どのシナリオでも 225 試行がすべて別の句（`--validate` exit 0）。
- **トレードオフ**: ⚠️ 読みの誤りが残る（無作為 40 句の目視で `絞罪→しぼりざい`・`この室→むろ`・`女学校→おんながっこう`）。E1 は打鍵列として妥当なかなで足り、E2 の正解は打った読み（判断 19）なので直さない。同じ読みの句が 9 組（README の既知の限界）。
- **影響範囲**: `kit/corpus/data/phrases.jsonl`・`kit/corpus/requirements.txt`・`experiment/data.md`（「Phrase corpus」節に 6 項目と出典の作品表）。生の `.txt` / zip は repo に入れない（archive の SHA-256 だけを記録）。

## 判断 80: M1 の所見を受けた macOS の手順とマーカーの直し（2026-10-01・研究者の選択と実測）

- **背景**: M1 の 1 回目（`pilot-macos-1-notes.md`）で、変換後の Enter が確定せず試行が持ち越される・マーカー F13 / F14 が観測側に届かない、が見つかった。
- **採用**: (1) macOS の recipes をライブ変換 ON の IME の実際の挙動に合わせる（候補の窓の Enter は選ぶだけ → Enter 2 回・数字の後に Enter・Esc 4 回）。★ 研究者の手打ちでも同じ挙動を確認したので、合成キーの人工物ではない。(2) マーカーは**矢印キー（← → ←）**（研究者が AskUserQuestion で推奨を選択。他の案: F13 のまま時計を試行の打鍵で合わせる / F1〜F12 を語彙に足す）。
- **理由**: (1) README（`kit/gen/README.md`）の想定どおり、パイロットの後に直すのは recipes のデータ。(2) 矢印キーは既に語彙にあり観測され、変換中でなければ IME の状態も文字も変えない。E2 は既存の `--markers-in-obs` で扱える（コードの変更なし）。
- **トレードオフ**: ⚠️ ライブ変換 OFF では余分な Enter が改行になりうる → OFF のセルは別の recipes ファイル（パイロットしてから）。⚠️ E2 を本番のログに回すときは `--markers-in-obs` を付ける。
- **影響範囲**: `kit/gen/recipes.json`（macOS のみ）・`generate_plan.py` / `simulate_obs.py` の selftest・`refinput-macos/build.sh`・pilot / run / e2 / gen / refinput-macos の README・`run/cell.example.json`。

## 判断 81: M1 の枝の PR の前の整え —— 生成器の版を上げ、OFF 用の手順書も selftest で照合する（2026-10-01・G-GEAR・メインの実装上の選択・研究者が覆せる）

- **背景**: 引き継ぎ（`next-session-ime-paper-m2.md` §2）の 1〜4。M1 で macOS の手順を変え、OFF 用の手順書 `recipes.macos-live-off.json` を足したが、生成器の版は `1.1.0` のままで、OFF 用の手順書は selftest の外にあった。
- **採用**:
  1. `GENERATOR_VERSION` を `1.1.0` → `1.2.0`。`kit/gen/README.md` の規則（「recipes の手順の意味が変わったら上げる」）に当たる。`plan/1` の書式は変わらないので minor。この値を固定している検査は無い（`grep -rn "GENERATOR_VERSION\|generator_version\|1\.1\.0"`。selftest の架空の計画は `"0"` / `"0.1"` を使う）。
  2. OFF 用の手順書も selftest で照合する。`_scenario_checks` の終わりのキーを、手順の型ごとの表 `_PROFILES`（`windows` / `macos-live-on` / `macos-live-off`）から引く形にした。足した検査: OFF の 13 シナリオの照合・S11 が既定で外れる・Windows の節と `kana_layout` が `recipes.json` と同一・2 つの macOS の型が互いの計画を拒む（陰性対照）・`--validate`・`typed_reading`。README の「selftest は `recipes.json` だけを見る」を直し、ファイルの表と `scenarios` の行に OFF 用の手順書を足した。
  3. `_scenario_checks(..., os_name="macos")` の既定を無くし、型を必須の引数にした（呼び出しは selftest の 5 か所だけ・どれも型を渡す）。
  4. `run/cell.example.json` の `layout` を `US keyboard` → `JIS keyboard` に直した。`focus_cmd` の key code 104 は JIS のかなキー、S12 の `kana_layout` は JIS のかな配列、両パイロットとも JIS で、例のほうが食い違っていた。⚠️ `learning`（「毎ブロックでリセット」）は直さない。例は設計（design.md「ブロックの先頭で辞書・学習状態をリセット」）を示していて、`reset_cmd` は仮（`run/README.md` の前提 6「`cell.example.json` gives placeholders only」）。パイロットでリセットしなかったことは、M2 で `pilot-macos.md` の条件に書く（引き継ぎ §3.5）。本番でリセットするかどうかは M3 の事前登録で決める。
- **確認（G-GEAR・Windows 11・Python 3.11.9）**: `generate_plan.py --selftest` 103 件が緑（直す前は 96 件）。OFF 用の手順書に変異を 7 本入れると、7 本とも selftest が赤になった（S1 の Enter を 2 回・S5 の Esc を 2 回・S2 の Enter を 1 回・S8 の数字の後の Enter を削る・S11 を既定で有効・Windows の節を変える・`kana_layout` を変える）。`kit/check.sh` の 27 本と `--compile` が緑、`_style_check.py papers/ime-observation` の違反は 0 件。
- **経緯**: 1〜3 の差分は、worktree `C:/wt/ime-m1-pilot` に未コミットで残っていた（`generate_plan.py` の mtime は 2026-10-01 04:11 で、引き継ぎの commit `0da36bcc` の 6 分後。書いた記録は無く、前のセッションの書きかけと見られる）。メインが全行を読んで採用し、README を合わせ、4 を足した。

## 判断 82: M1 の枝の完了時レビュー 1 巡目（Claude の 2 系統）の指摘への対応（2026-10-01・G-GEAR・メインの実装上の選択・研究者が覆せる）

- **背景**: `97381a7b..5a9cc805`（この枝だけの差分・17 ファイル）に code-reviewer ∥ security-checker を回した。どちらも CRITICAL / HIGH は 0。指摘はすべて一次（コード・`pilot-macos-1-notes.md`・`clock_sync.py`・`run_cell.py`）で裏を取った。
- **直したもの**（papers/ の 7 ファイル）:
  1. 〔MEDIUM・コード〕矢印だけのマーカーが観測側で一意でない: 観測は種類しか持たないので、← → ← は `navigation` × 3 として探される。S7 は → を `nav_count` 回続けて押すので、`nav_count_max` ≥ 3 なら試行の中にも同じ並びが現れる。本物のマーカーが欠けたブロックでは、それが割り当てられて `missing` に出ない（`clock_sync.py` の README の約束に反する）。→ `normalize_config` が「矢印だけのマーカーは `nav_count_max` より長い」を検査して、破る config を拒む（exit 2）。gen / pilot の README に規則を書いた。⚠️ パイロットの config（← → ←）は `nav_count_max` によっては拒まれる → M2 で研究者が「4 打鍵のマーカー（← → ← →）」か「`nav_count_max` ≤ 2」かを決める（引き継ぎ §3）。
  2. 〔MEDIUM・文書〕ライブ変換 ON で残った食い違いが gen/README に無かった → 「126 試行のうち、かな入力の 9 試行中 2 件は 1 回目の Return で確定・数字選択と予測候補の各 1 件が持ち越し」を Limitations に足した。OFF の確認には n = 39 を添えた。
  3. 〔MEDIUM・文書〕e2/README が証拠より強かった（送ったのは F13 / F14 だけ・4,000 は試行の中の押下だけ）→ 書き分けた。
  4. 〔MEDIUM・文書〕OFF のセルの計画を ON 用の手順書で攻撃しても `closed_set.py` は止まらない → e2/README の Usage に「`--recipes` は計画を作ったファイル（OFF なら `recipes.macos-live-off.json`）」と、照合がまだ無いこと・出力の `recipes_sha256` で後から比べられることを書いた。⚠️ コードの照合は今回入れない: selftest の計画は `recipes_sha256` が `"0" * 64` で、照合を入れると closed_set / open_set の selftest と 021 / 022 の fixture を直す範囲になる → E2 を本番のログに回す前の項目として引き継ぎ §5 に書いた。`open_set.py` は手順書から `kana_layout` と `typed_reading` しか使わず、2 つのファイルで同一なので実害は無い。
  5. 〔LOW〕gen/README: 手順の終わりのキーを変えたら `_PROFILES` も直す・S11 の行の条件を前に出す・「仮説」は Windows の手順だけ（macOS は 1 台・1 版の実測）。`generate_plan.py`: 型の表のコメントの不正確さ（Windows の数字選択は 0 キー・Space の無い確定は全型で Return 1 回）・失敗の文言に型の名前・Windows の照合でも全シナリオが現れたかを確かめる。
  6. 〔LOW〕run/README: `4a.` は CommonMark でリストの印にならない → 4 の 2 段落目にした（番号 5〜8 は変えない）。前提 6 の「placeholders only」を、仮の値（`reset_cmd`・`ime_settings.learning`・`ime` の版）の名指しに直した。`focus_cmd` は送出フラグの有無によらず、前面の確認より前に実行される（`run_cell.py:579-587` で確認）ことを表に書いた。前提 4 に System Events の Automation の許可と、計測の後に外せることを書いた。
  7. 〔LOW〕pilot/README: 「空の欄のキャレットを動かす」は不正確（確定のたびに欄は空になり、矢印は命令として届く）・「変換の外で押す」は持ち越しのブロックでは成り立たない → 事実として書き直した。`open_set.py` の docstring の「function keys」を直した。
  8. 〔LOW・security〕`build.sh` の bundle id の検査を送出側（`backend_macos.py:39` の `[A-Za-z0-9][A-Za-z0-9.-]{0,127}`）と同じ形にし、`LC_ALL=C` で範囲を ASCII に固定した。検査の部分だけを git-bash 5.2 で 11 通り試した（128 文字は通し 129 文字・先頭の `.` / `-`・空・空白・`"`・`<`・非 ASCII は拒む）。⚠️ macOS の bash 3.2 と `build.sh` 全体（`swiftc`）は Mac で確かめる。
- **直さないもの（理由）**:
  - 〔MEDIUM・security〕パイロットの生ログを公開物に含めるときの除外の基準が無い → M2 の §3-4 の作業そのもの。基準（計画どおりで aborted でない run だけ・oracle に対応しない観測の key 行が 0 件・手打ちの探査と手打ちの対照は除く）を引き継ぎに書いた。
  - 〔LOW・security〕`focus_cmd` のかなキーが前面の確認より前に押される → 例の osascript に前面の bundle id の確認を足すのは、Windows では試せない。引き継ぎの Mac の項目にした。`run_cell.py` で `focus_cmd` を送出フラグの対象にする案は、既存の acceptance の挙動を変えるので採らず、README に書くだけにした。
  - 〔範囲外〕`cell.example.json` の `predictive_candidates: "off"` と、既定で有効な S10（予測候補）の食い違い → パイロットの実際の設定を `pilot-macos.md` の条件に書くときに確かめる（引き継ぎ）。
- **確認**: `generate_plan.py --selftest` 108 件が緑。新しい検査への変異 4 本（検査を外す・`<=` を `<` にする・Windows の照合に OFF の型を渡す・Windows の計画から S2 を抜く）がすべて赤。`kit/check.sh` の 27 本・`--compile` が緑、`_style_check.py` の違反 0 件。

## 判断 83: M1 の枝の完了時レビュー（Codex）—— 上限の一時的な引き上げと、指摘 4 件への対応（2026-10-01・G-GEAR・上限は研究者の選択・対応はメインの実装上の選択で研究者が覆せる）

- **予算**: 同日の Codex の実消費は、並行セッション（`docs/ai-fatigue-protocol-cont`）の台帳で 291,174 / 7 回だった。こちらで 1 回回すと上限 300,000 を超える。予算ガードの hook は `C:\GSE-prototype` の台帳（66,418）を読むので止まらない。研究者に AskUserQuestion で 3 案を出した（推奨は「今日は PR まで・Codex は 10-02」、ほかに「今日だけ 350,000 に上げる」「Codex を省く」）。研究者は「今日だけ上限を 350,000 に上げる」を選んだ。台帳に `_comment_2026_10_01_m1_pr_raise` を足した。並行セッションには、今日はこれ以上回さないよう SendMessage で知らせた。
- **実行**: `scripts/run-codex-review.sh 97381a7b..6fa44a6a -- papers/ime-observation`（12 ファイル・772 行）。機密フィルタは素通りした。消費は 33,557（本ブランチの台帳 199,404 → 232,961・5 → 6 回）。同日の合計の見込みは 291,174 + 33,557 = 324,731。
- **指摘と対応**（4 件とも一次で確かめた）:
  1. 〔P1〕`closed_set.py` が計画と違う手順書を黙って使う。code-reviewer の MEDIUM と一致したので、判断 82 の「README だけ」を改め、コードで止める。`run()` で、各計画のヘッダーの `recipes_sha256` と `--recipes` のファイルの SHA-256 を比べ、違えば exit 2 にした。selftest の計画は `recipes.json` の実際の SHA-256 で作るように直し、OFF 用の手順書を渡すと exit 2 になるケースを足した（83 件緑・照合を外す変異で赤）。021 の acceptance は selftest とケース名の grep だけなので、影響しない。`open_set.py` は、2 つのファイルで同一の `kana_layout` / `typed_reading` しか使わないので照合しない（README に書いた）。
  2. 〔P1〕例の `focus_cmd` が、前面の確認の前にキーを送る。`dryrun` では同意なしで送る。security-checker の LOW と同じ。
     - (i) 同意: `run_cell.py` で、`focus_cmd` を `reset_cmd` と同じく送出フラグの対象にした。フラグが無ければ実行せず、manifest に skipped と理由を書く。README の「フラグは機械の状態を変える操作すべてへの同意」に合わせた。既存の「focus の失敗で abort」のケースはフラグありに直した。フラグなしでは走らない・フラグありでは走る、の 2 ケースを足した（53 件緑・ゲートを外す変異で赤）。manifest の `focus` を読む処理は `run_cell.py` の外に無い（grep）。
     - (ii) 順序: 例の osascript に、かなキーを押す前の前面の確認を 1 行足した。式は送出側 `backend_macos.py` の `FRONT_QUERY`（`id of application (path to frontmost application as text)`）で、パイロットの実機で動いたもの。違えば `error` で非 0 になり、`run_cell.py` がブロックの前に abort する。⚠️ この 1 行は実機で試していない → Mac で確かめる（引き継ぎ）。README の前提 6 に「パイロットの後に足した 1 行」と書いた。
  3. 〔P2〕持ち越しは、キー列の照合（`_scenario_checks`）では見つからない。`gt_sessions.py` の `oracle_agreement` は不一致を型ごとに数えるが、除外はしない。→ 持ち越した試行（と次の試行）をどう扱うかは、正解の定義と事前登録で決める（M2 / M3・引き継ぎ §3）。今回はコードを変えない。
  4. 〔P2〕OFF 用の手順書でも、S11 を `scenarios` で名指しすれば生成できる。→ OFF 用の手順書の S11 を S9 と同じ形（`steps` が空・既定で無効）にし、名指しすると生成が止まるようにした。selftest に 1 ケース足した（109 件緑・直す前の手順書で赤）。⚠️ これで OFF 用の手順書の SHA-256 が変わる。パイロットの `verify-off` の計画は、`19c537c0` の版を指す（生ログを預けるときは、その版を添える）。
- **2 巡目**: Codex の 2 巡目は回さない。同日の合計の見込み（324,731）に 1 回（3〜4 万）を足すと、研究者が選んだ 350,000 を超えるため。2 巡目の観点（今回足した規則の境界条件）は、Claude の code-reviewer で見る。

## 判断 84: M1 の枝の完了時レビュー 2 巡目（code-reviewer・足した規則の境界条件）への対応（2026-10-01・G-GEAR・メインの実装上の選択・研究者が覆せる）

- **背景**: 判断 82・83 で足した 5 つの規則（マーカーの長さ・E2 の手順書の照合・`focus_cmd` の同意・前面の確認・OFF の S11）の境界条件を、`5a9cc805..8ae9ccd1` で code-reviewer に攻めさせた。CRITICAL 0・HIGH 1・MEDIUM 5・LOW 5。すべて一次で確かめた。
- **直したもの**:
  1. 〔HIGH〕E2 の照合はファイルのバイト列で SHA-256 を比べる。ところが `recipes*.json` に `eol` の指定が無く、`core.autocrlf=true`（Git for Windows の既定）で clone すると CRLF になる。そうなると、正しい手順書を渡しても止まる。⚠️ この機械（`autocrlf=input`）では LF だった。od と Python でバイトを数えて確かめた（`git ls-files --eol` も `i/lf w/lf`）。なお、`grep -c $'\r'` は行数を返していて、測定器のほうが誤っていた。→ 先例（判断 32・63）に倣い、repo 直下の `.gitattributes` に `kit/gen/recipes*.json` と `kit/corpus/data/*.jsonl` の `eol=lf` を足した。コーパスの SHA-256 は `experiment/data.md` にも書いてある。index はもとから LF なので、中身は変わらない。⚠️ 書き出し器は公開 repo 用の `.gitattributes` を作らない（既存の先例のファイルも同じ）→ M12 の項目として引き継ぎに書いた。
  2. 〔MEDIUM〕マーカーの検査は、書かれたマーカーを見ていて、観測に残る並びを見ていなかった（`["left","f13","right","left"]` が通る）。また、上限は config の `nav_count_max` ではなく手順書の `params` で決まる（整数も書ける）。さらに、検査が `normalize_config` の中にあったため、E2 もこれを呼んでいた。E2 はマーカーを個数で読み飛ばすだけなので、パイロットの config で E2 が誤って止まる。→ 検査を `plan_rows`（生成のときだけ）に移した。観測されないキーの集合 `UNOBSERVED_KEYS`（e2/README のキーの表と同じ前提）を除いたマーカーが矢印だけなら、作った計画の試行の中の矢印の最長の連続（観測されないキーは飛ばして数える）より長いことを求める。S7 の無い計画では検査しない。selftest: 前提（nav 3 で連続 3 が実際にある）・拒否 3 通り（`["left","f13"]` を拒否側へ移した）・受理 6 通り・手順書で上限 5 にした S7・`normalize_config` が判定しないこと。
  3. 〔MEDIUM〕E2 は `config_sha256` を照合していなかった。K2（`ASSUMPTIONS`）は config も攻撃者の知識に挙げている → 手順書と同じく照合する。selftest は、計画を作った config を実際にファイルに書き、それを `--config` に渡す形に直した（もとは「計画は部分集合の config・`--config` は別のファイル」だった）。⚠️ コーパスは照合しない。設計（design.md §2）に「E2 だけ現代文のコーパスを足す」という任意の案があり、計画と違うコーパスを渡す正当な使い方がありうる。README に書いた。
  4. 〔MEDIUM〕例の前面の確認が 1 回だけで、送出側（0.2 秒おきに 5 回）より誤って中断しやすい → `repeat 5 times … exit repeat … delay 0.2 … end repeat` の後で確かめる形にした。⚠️ 実機では試していない（引き継ぎ）。
  5. 〔LOW〕run/README: manifest の `focus` に `skipped` を書いた（`focus_cmd` が空でなく、フラグが無いとき）。フラグの節の「skipped と記録」を、「計画が求めた reset と、空でない `focus_cmd`」に正した。前提 4 に「手順書はライブ変換の設定に合わせる・runner は確かめられない」を足した。前提 6 に「bundle id は例の 3 か所」を足した。
  6. 〔LOW〕e2 / pilot の README: ← → ← は、どの試行も矢印を 3 回続けて押さない間だけ使える、と注記した。本番のマーカーは事前登録で決める。
  7. 〔LOW〕`open_set.py` は、手順のうち「どのシナリオがかなで打つか」も読む → 2 つの手順書でこれが一致することを selftest で確かめる。
- **確認**: `generate_plan.py --selftest` 113 件・`closed_set.py --selftest` 84 件が緑。変異 5 本がすべて赤: 検査の呼び出しを外す・射影をやめる・上限を 3 に固定する・OFF の S12 のかな入力を外す・照合から config を外す。S12 の変異は、最初の文字列の置き換えが Windows の節にも当たって不発だったので、JSON として macOS の S12 だけを変えてやり直した。`kit/check.sh` の 27 本と `--compile` が緑、`_style_check.py` の違反 0 件。
- **直さないもの**: なし（引き継ぎに回したのは、M12 の公開 repo の `.gitattributes` と、実機での前面の確認の 2 つ）。

## 判断 85: 本番の n・think の上限・マーカーの長さ（2026-10-01・Mac・研究者の選択）

- **材料**（一次で取り直した）: 再パイロットの ON は 126 試行で 23.2 分（1 試行 11.05 秒・待ちとマーカー込み）。`generate_plan.py --estimate` は 1 試行 11.19 秒と見積もり、実測とほぼ一致した。think（対数一様 0.2〜20 秒）の寄与は、126 試行のうち think を使う 54 試行で計 202 秒（全体の約 15%・平均 1 試行 1.6 秒）。
  - 1 セル（14 シナリオ × 3 速さ × n）の見積もり（macOS・ON / OFF）: n = 75 で 9.79 h / 9.25 h、n = 60 で 7.86 h / 7.40 h、n = 50 で 6.63 h / 6.15 h。
  - think の上限を下げた場合（n = 75・ON）: 10 秒で 9.15 h、5 秒で 8.79 h。下げても 1 時間ほどしか縮まず、20 秒打ち切りの境界を見るという think の目的（design.md §1.5）を失う。
  - 再現率 0.95 付近の Wilson 95% 半幅: n = 75 で ±5.3pt、n = 60 で ±6.0pt、n = 50 で ±6.6pt。
- **研究者の選択**（AskUserQuestion・推奨どおり）: **n = 75・think 0.2〜20 秒**（1 セル約 10 時間を受け入れる）。**マーカーは 4 打鍵 ← → ← →**（`nav_count_max` = 3 を残す）。
  - ← → ← → で `nav_count_max` = 3 なら、生成器が計画を作ることを ON / OFF の両方の手順書で確かめた（exit 0）。← → ← のままでは exit 2 になる（判断 84 の検査）。
- **反映**: `kit/pilot/README.md` の `clock_sync.py` の例の JSON を 4 打鍵にし、`kit/e2/README.md` の記述も合わせた。`segment_by_plan`（`pos += len(r["marker"])`）と `clock_sync.py`（`len(spec["oracle_keys"])`）は、マーカーの長さによらないことをコードで確かめた。本番の生成の config は、M3 の事前登録で凍結する（今回はファイルを作らない）。

## 判断 86: macOS の正解の定義 —— 打鍵の途中の自動確定を 1 つのセッションに含める（2026-10-01・Mac・メインの実装上の選択・研究者が覆せる）

- **所見**: `gt_rules.example.json` のままでは、ライブ変換 ON の再パイロット（`pilot2-on`）で 126 試行中 40 試行が `multiple_sessions` になった（oracle 一致率 85 / 126）。ライブ変換は、読みを打っている途中で先頭を確定し、残りを marked にする（`insert_text` → `set_marked`）。既定の規則は、この確定ごとにセッションを閉じる。
- **測定**（参照側の gt ログ・oracle・plan だけ。ImeShadow の封印は開けていない）:
  - 試行の中で `insert_text` の後に `set_marked`（len > 0）が続いた 85 件の間隔は、0.50〜7.85 ms（中央値 1.0 ms）。どの 1 件も、間に `key_down` が無かった。つまり同じ 1 打鍵への IME の応答がひと続きに出ている。
  - 試行の最後の確定から次の `set_marked` までは、最小 958 ms（試行の間の待ち 1,000 ms による）。ライブ変換 OFF（`pilot2-off`・`verify-off`）では、試行の中の続きは 0 件。
  - 旧手順の `verify-1`（`b38b9904`）でも、続きは 29 件・最大 4.5 ms だった。
- **決定**: `experiment/gt_rules.json` を新しく作り、`experiment/config.json` の `gt_rules` をこれに向けた。`mac_nstic` の commit は「`insert_text`（len > 0）または `unmark` で、その後 50 ms 以内に `set_marked`（len > 0）が来ないもの」とする。Windows の 2 つの規則は example のまま（M5 で直す）。example は selftest と pipeline が参照する仮説として残す。
  - 50 ms は、既存の cancel の `within_ms` と同じ値。観測された最大の 7.85 ms と最小の 958 ms のあいだにある。
  - 10・20・50・200・500・900 ms のどれでも、3 つの run（`pilot2-on`・`pilot2-off`・`verify-off`）のセッションと除外がバイト単位で同じだった。1 ms では 95 / 126、5 ms では 122 / 126、1,500 ms では 17 / 126 に崩れる。
  - 1 試行が意図する変換は 1 つ（oracle の照合が 1 試行 1 セッションを期待する）。試行の間は 1,000 ms 空く。このため 50 ms の窓が、意図の違う 2 つの変換をつなぐことは、計画の作りの上で起きない。
  - `unmark` はパイロットで一度も観測されていない。整合のために同じ条件を付けた。
- **結果**: oracle 一致率は ON 124 / 126（残る 2 件は持ち越し）、OFF 117 / 117、`verify-off` 39 / 39。
- **確認**: `gt_sessions.py` の selftest に `_case_experiment_rules` を足した。`experiment/gt_rules.json` を読み、自動確定を 1 セッションに含め、続きの無い確定では閉じること、また example では同じ入力が 2 つに割れること（対照）を確かめる。変異: 規則から続きの条件を外す・ファイルを消す → どちらもこのケースだけが赤。

## 判断 87: 持ち越しは、持ち越した試行と受けた試行の両方を除外し、件数は別に報告する（2026-10-01・Mac・研究者の選択）

- **所見**: ON の再パイロットでは 2 件（t00098 S10 → t00099、t00119 S8 → t00120）。セッションが前の試行の中で始まり、次の試行の区間まで続く。重なりの大きい次の試行に割り当てられるので、前の試行は `no_session`、次の試行は前の文字列を含んだセッションになる。
- **研究者の選択**（AskUserQuestion・推奨どおり）: 2 試行とも除外し、持ち越しの件数は記述の量として別に報告する。
- **実装**: `gt_sessions.py` で、セッションの区間（閉じていなければログの最後の事象まで）が 2 つ以上の試行の trial_begin..trial_end と重なるとき（両端を含む）、`excluded` に `{"type": "carry_over", "log": "gt", "trial_ids": [重なった試行すべて]}` を足す。下流の `match.py` は除外を試行の単位で扱うので（`trial_ids` に入った試行の観測も落とす）、変更は要らない。`l2.py` は型によらず除外を数える。
  - `oracle_agreement` は変えない（持ち越した試行は `no_session` の不一致として残る）。一致率は「手順が意図どおりに IME を動かしたか」の量で、持ち越しはその失敗だから。
  - 判定は壁時計で行う。試行の割り当て（`_assign_trial`）と同じ時計に揃えた。gt 側の壁時計の飛びがセッションの中にあると、区間が伸びて carry_over にも当たる。どちらにしても除外なので、結果は変わらない。既存の陰性対照（clock_jump_ms を変えると excluded が変わる）は、clock_jump の項目だけを比べる形に直した。
- **確認**: 実データで、2 組（`t00098`/`t00099`・`t00119`/`t00120`）だけが carry_over になった。OFF の 2 run は 0 件。selftest に `_case_carry_over` を足した。持ち越しの検出、試行の後・次の試行の前に落ちる確定は対象外（陰性対照）、一致率は変わらない、閉じないセッションは log_truncated と carry_over の両方、を確かめる。変異 3 本（追加を外す・2 を 3 にする・重なりの判定を包含に変える）はどれもこのケースだけが赤。⚠️ 〔判断 88 で訂正〕この 3 本では、3 試行にまたがる場合と端ちょうどの場合が試されていなかった（code-reviewer が、両端だけを見る変異と端を含まない変異が通ることを示した）。`gt_sessions.py --selftest` 14 件・`kit/check.sh` 27 本・`run.sh --synthetic` が緑。

## 判断 88: M2 の完了時レビュー（Claude の 2 系統）への対応（2026-10-01・Mac・メインの実装上の選択・研究者が覆せる）

- **結果**: security-checker は CRITICAL / HIGH 0・MEDIUM 1・LOW 2。code-reviewer は CRITICAL / HIGH 0・MEDIUM 2・LOW 4。すべて一次で確かめた。
- **直したもの**:
  1. 〔MEDIUM・security〕`pilot-macos.md` の生ログの預け方の基準が、観測側の key 行しか押さえていなかった。参照入力欄も `keyDown` ごとに物理キーの `vk` を記録する（`RefInput.swift:176`、ソースの冒頭に「人が打ったログは打鍵内容として扱う」とある）。→ 基準に次の 3 点を足した。観測の key 行と gt の `key_down` の両方が、送出の記録に対応すること。今の `reach.py` は逆向きしか数えないこと。手打ちの対照と Enter・Esc の探査は runner の run ではなく、預けないこと。手打ちの記録（`manual-*.jsonl`・`enter-probe*`・`esc-probe*`）が `~/ime-pilot/runs/` の外にあることも確かめた。
  2. 〔MEDIUM・code〕`_case_carry_over` が、両端だけを見る変異と端を含まない変異を見逃した（元の場所で再現した）。→ 3 試行にまたがるケース（真ん中の試行に事象が無い）と、終端が次の trial_begin とちょうど同じ ms のケースを足した。2 本の変異はどちらも赤になった。
  3. 〔MEDIUM・code〕ライブ変換 ON では、先頭が自動確定した後に残りを取り消しても、セッションの outcome は `cancel` になる。数えると、`pilot2-on` の取り消しの 27 試行のうち 11 試行（S4: 3・S5: 3・S6: 5）がこれに当たった。→ `gt_rules.json` の `_note` と `pilot-macos.md` に、「outcome は最後に閉じた理由で、途中の自動確定は数えない」と件数を書いた。観測側の放棄とどう照合するか（診断用のフィールドを足すかを含む）は、M3 の事前登録で決める（引き継ぎ）。
  4. 〔LOW〕50 ms の窓の端ちょうどのケースを足した（50 ms は続き、51 ms は別のセッション）。`> limit` を `>= limit` にする変異で赤になる。
  5. 〔LOW〕docstring に 2 点書いた。壁時計の飛びで、次のブロックの最初の試行まで carry_over になりうること（除外が増える向き）。窓の中でログが終わると、log_truncated ではなく確定として閉じること。
  6. 〔LOW〕`_note` の最大値を 7.85 ms に揃えた。README の「frozen with the protocol」を「will be / to be frozen」にした（生成の config はまだ無い・判断 85）。
- **直さないもの**: 〔LOW・security〕carry_over の判定は、試行数とセッション数の総当たりになっている。1 セル約 3,150 試行では実害が無いので、そのままにする。
- **確認**: `gt_sessions.py --selftest` 14 件・`kit/check.sh` 27 本・`run.sh --synthetic`・`_style_check.py` 違反 0 件。実データの組み立ては変わらなかった（ON 124 セッション・除外 2、OFF 117・0、`verify-off` 39・0）。
- **Codex**: 今日（10-01）の実消費は 324,731 で、上限 300,000 を超えている → 研究者に確かめる。

## 判断 89: M2 の完了時レビュー（Codex）—— 上限の一時的な引き上げと、指摘 3 件への対応（2026-10-01・Mac・上限は研究者の選択・対応はメインの実装上の選択で研究者が覆せる）

- **予算**: 回す時点で、当日の実消費は 324,731 / 8 回（上限 300,000 を超えていた）。研究者に AskUserQuestion で 3 案を出した（推奨は「明日回してから PR」）。研究者は「今日だけ上限を上げて回す」を選んだ。台帳の上限を 360,000 にし（`_comment_2026_10_01_m2_raise`）、`scripts/run-codex-review.sh eb8409b3..HEAD -- papers/ime-observation` を 1 回回した（29,449・→ 354,180 / 9 回）。回した後、上限を 300,000 に戻した。
- **指摘と対応**（3 件とも一次で確かめた）:
  1. 〔P2〕50 ms 以内に始まった独立の入力も、続きとしてつないでしまう。→ 両方の手順書の全シナリオ（macOS・Windows）を走査した。確定・取り消しのキー（enter・esc・digit）の後に打鍵（`type_reading` を含む手順）が続くものは 0 件。手順の書き方 8 種をすべて数えて、走査の漏れが無いことも確かめた。試行の間は 1,000 ms 空く。よって計画の作りの上では起きない。`pilot-macos.md` にこの前提を書いた。コードは変えない。
  2. 〔P2〕ログが窓の中で終わると、確定を未確認のまま採用する。→ 3 つの run とも、gt ログは最後の確定の 0〜23 ms 後で終わっていた。ただし runner は、最後のブロックの後 `settle_ms`（既定 1,000 ms）待ってから参照入力欄を止める（`run_cell.py:596`）。実測では、最後の確定から run の終わりまで約 1,065〜1,084 ms あった。窓のあいだ参照入力欄は動いていて、何も来なかったことになる。`pilot-macos.md` に「`settle_ms` を窓より短くしない」と書いた。事前登録（M3）で `settle_ms` を固定する（引き継ぎ）。
  3. 〔P3〕取り消しの経路のテストが足りない。→ `_case_experiment_rules` に 2 つ足した。自動確定の後に残りを取り消すと 1 つの cancel になること。`unmark` も続きの有無で開く・閉じること。`unmark` の窓を外す変異で赤になる。
- **確認**: `gt_sessions.py --selftest` 14 件・`kit/check.sh`・`_style_check.py` 違反 0 件。

---

★ 以下 2026-10-01（G-GEAR・M3 の事前登録の下書きに入る前）。研究者に AskUserQuestion で 8 問を問い、8 問とも推奨どおりに決まった。
材料はこのセッションで一次から取った: `pipeline.py:320-352`（解析の設定・凍結のハッシュ）・`l1.py:44-51`・`l2.py:30-35`（`dwell_ms == 0` は「凍結で決める」）・`match.py:28-42`（ずれと IoU の性質）・`gt_rules.json` の `_note`・`e2/README.md:88-98, 229-241`・`ime_compose.rs` の冒頭（観測側の放棄の定義）・Dhakal ら（2018）の本文（Aalto の PDF を pypdf で全文抽出）・OSF ヘルプ。解析コードと E2 / E3・生成器・実行器の目録は Sonnet の作業用エージェント 2 本に作らせ、ここに書いた事実はメインが一次で開き直した。

## 判断 90: 本番の打鍵の速さは 480 / 240 / 120 ms（2026-10-01・G-GEAR・研究者の選択）

- **一次**: Dhakal ら（2018・CHI・doi:10.1145/3173574.3174220・`[P269]`）の Table 1 と本文。参加者ごとの平均 IKI は、全体 238.66 ms（SD 111.60）・速い群（速さが 90% の参加者を上回る・約 78 WPM 超）121.70 ms（SD 11.96）・遅い群（遅い 10%・約 26 WPM 未満）481.03 ms（SD 123.36）。押下の長さは 116.25 ms（SD 23.88）。IKI の計算では前の打鍵から 5,000 ms を超えた打鍵を除いている。
- **選択肢と見積もり**（n = 75・`generate_plan.py --estimate`・コーパス `c8f890cb…`・ライブ変換 ON / OFF の 1 セル）: A = 480 / 240 / 120 → 11.9 h / 11.2 h ／ B = 300 / 200 / 120（パイロット）→ 9.8 h / 9.3 h ／ C = 400 / 240 / 120 → 11.1 h / 10.5 h。
- **研究者の選択**: **A**（推奨）。3 水準が一次の値（遅い群・全体・速い群の平均）にそのまま対応し、根拠を 1 文で書ける。1 セルは約 2 時間長くなる。
- ⚠️ **書き方の注意**（事前登録で明記する）: 生成器の `iki_median_ms` は対数正規分布の**中央値**で、一次の値は**参加者ごとの平均 IKI の平均**。σ = 0.3 では分布の平均は中央値の約 1.046 倍（502 / 251 / 126 ms）。一次は英語の書き写し（物理キーボード・オンラインの課題）で、日本語のローマ字入力ではない → 「打鍵の速さの範囲を一般の打鍵研究の値で張る設計上の要因」と書き、日本語の打鍵の推定値とは書かない。
- **メインの実装上の選択**（研究者が覆せる・事前登録に書く）: `iki_sigma` = 0.3（間隔にばらつきを持たせる設計上の値で、データから推定したものではない）／ `key_hold_ms` = 60（生成器は押下を重ねない〔`at_ms` は押下と離しを順に置き、間隔の下限は `key_hold_ms + 1`〕。一次の 116 ms を使うと、速い水準〔中央値 120 ms〕の間隔の多くが下限に張り付く。IME は押下で動くので、離しの時刻は観測の対象に入らない）／ `inter_trial_ms` = 1,000 ／ `marker_gap_ms` = 150 ／ `cand_index_max` = 4 ／ `block_size` = 25 ／ `kana_len` 4〜8。n = 75・think 0.2〜20 s・マーカー ← → ← →・`nav_count_max` = 3 は判断 85。⚠️ パイロットの config の全体は Mac にだけあり、repo の記録は速さ・think・n・マーカーだけ（`pilot-macos-1-notes.md:10`）→ Mac で `cand_index_max` などの値を確かめる（引き継ぎ）。

## 判断 91: IME の学習はリセットしない。条件と限界に書く（2026-10-01・G-GEAR・研究者の選択）

- **背景**: design.md §1.1b は「ブロックの先頭で辞書・学習状態をリセット」と書くが、パイロットはリセットしておらず、macOS の標準 IME でリセットする手段も見つかっていない（`pilot-macos.md` の Setup・`run/README.md` の前提 6）。
- **選択肢**: A = リセットしない・条件と限界に書く ／ B = 凍結の前に手段を探して入れる（10 月中旬の凍結が遅れうる・パイロットの一部のやり直し）。
- **研究者の選択**: **A**（推奨）。`reset_ime_every_block` = false。学習の影響は候補の並びや自動確定の位置に出うる。区間はブロック単位のクラスタ・ブートストラップで出すが、ブロックをまたぐ依存は扱えない → 限界に書く。
- **影響**: design.md §1.1b からの逸脱として事前登録に書く（設計の段階の意図 → 実際の条件）。`cell.example.json` の `learning` の記述をパイロットと本番の実際に合わせる（引き継ぎ §M3 (4)）。

## 判断 92: 段階凍結は、Windows の追補で凍結の印を更新する（2026-10-01・G-GEAR・研究者の選択）

- **背景**: 凍結の印 `sha256` は `config.json`・`SEED`・`gt_rules.json`（全体）を束ねる（`pipeline.py:343-352`）。`gt_rules.json` は Windows の 2 つの規則も持ち、それは Windows の較正パイロットの後に直す予定（`gt_rules.json` の `_note`）。macOS 版を凍結した後に Windows の規則を直すと、印が合わなくなる。
- **選択肢**: A = 追補の凍結で `preregistration.md` の `frozen_at` と `sha256` を書き換え、macOS の節・`config.json`・`SEED`・`mac_nstic` の規則は変えない ／ B = 規則ファイルと凍結のハッシュを OS ごとに分ける（凍結の門・selftest・acceptance の改修）。
- **研究者の選択**: **A**（推奨）。コードの変更なし。OSF には macOS 版の登録がそのまま残る。⚠️ 追補では、変えてよいのは `gt_rules.json` の `win_imm` / `win_tsf` と、追補の節の本文だけ。変えていないことは 2 つの凍結のタグの差分で示し、追補にも書く（事前登録の本文に、この手順を先に書いておく）。

## 判断 93: OSF Registries の登録はすぐ公開する（2026-10-01・G-GEAR・研究者の選択・判断 73 の未決 (1)）

- **一次**（OSF ヘルプ「Addressing Fear of Scooping on OSF Preregistrations」）: エンバーゴは逐語 "you can hide the details of your study from public view for a certain period" ／ "An embargo on the OSF can last for up to four years from the first submission" ／ 外部からは "it will appear as a 'page not found' notification"。⚠️ エンバーゴ中の view-only link は検索結果の要約にあるだけで、逐語では確かめていない。
- **研究者の選択**: **すぐ公開**（推奨）。中身は手順と解析計画だけで機微な情報が無い。BRM の Open Practices Statement に URL を載せ、凍結の日時を誰でも確かめられる。登録は研究者が行う（判断 73）。

## 判断 94: 時計のずれは補正しない。マーカーで測ったずれは診断として報告する（2026-10-01・G-GEAR・研究者の選択）

- **背景**: 解析は `clock_offsets_ms` を照合器に渡していない（`pipeline.py:325-328`・`notes.md` の Unresolved）。一方 `pilot-macos.md` の Clocks は「Analyses that align the observation with the reference use the per-block offsets.」と書いていて、食い違っている。
- **一次**: パイロットの観測 − 参照は、ブロック 1〜5 で −5〜−1 ms、ブロック 0 で −10 / −22 ms（`pilot-macos.md`）。`dwell_ms` の誤差は長さの差なので、ずれに依らない。照合（IoU ≥ 0.5）は、長さ L のセッションならずれが L/3 以下で対になる（`match.py:38-41`）。
- **研究者の選択**: **補正しない**（推奨）。コードは変えない。`pilot-macos.md` の一文を直す。本番でも各 run で `clock_sync.py` を回し、ブロックごとのずれを結果と一緒に報告する（事前登録に書く）。

## 判断 95: `dwell_ms == 0` の観測の行は今の扱いのまま、件数を出す（2026-10-01・G-GEAR・研究者の選択・判断 45 の未決）

- **今の扱い**（一次）: 照合では長さ 0 の区間で、正の長さのセッションと重ならないので必ず偽検出に入る（`l1.py:44-51`）。L1 の dwell の誤差からは外して `n_zero_excluded` に数え、`zero_dwell_rows` をすべてのバケットで数える。L2 では変換の数と放棄率に数え、平均変換時間と時間の割合からは外し、`n_dwell_zero` を出す（`l2.py:30-35`）。
- **研究者の選択**: **今のまま**（推奨）。コードの変更なし。適合率を下げる側（観測に不利な側）に倒れる。時刻の同期を止めるので稀なはず。⚠️ コードの docstring 4 か所（`l1.py:50-51, 456-457`・`l2.py:34-35, 547-548`）の「事前登録で決める」は、事前登録の後に「事前登録で決めた」に直す（凍結の前に）。

## 判断 96: 自動確定の後の取り消しは、照合はそのままにして、層別の診断を足す（2026-10-01・G-GEAR・研究者の選択・判断 88 の引き継ぎ）

- **一次**: 正解側のセッションの outcome は最後に閉じた理由で、途中の自動確定は数えない（`gt_rules.json` の `_note`・`pilot-macos.md`）。`pilot2-on` の取り消し 27 試行中 11（S4: 3・S5: 3・S6: 5）が「先頭が自動確定した後に残りを取り消した」形。観測側（macOS）は、未確定の文字列を捨てる Esc で放棄の印を立てる（`kit/logger/src/input/ime_compose.rs` 冒頭の表「`abandon` に入るもの」）→ 向きはそろうはず。
- **研究者の選択**: **照合はそのまま・層別の診断を足す**（推奨）。主の指標は変えない。正解のセッションに「途中で自動確定があった」印（数）を付け、放棄の一致をその層でも報告する。
- **実装**（メインが段取り・凍結の前）: `gt_sessions.py` のセッションに、続きのあった確定の数を出す欄を足す。`l1.py` の `abandon` に、その欄で分けた表を足す。selftest と変異で確かめる。

## 判断 97: E2 の「偶然に近い」は、各 K で正解率の 95% 区間の上端が 2/K 以下（2026-10-01・G-GEAR・研究者の選択）

- **背景**: `e2/README.md:229-241` は、公開の粒度の推奨を「許容幅に入る特徴集合」で決め、幅は解析計画が凍結の前に決めるとする（キットは決めない）。⚠️ 同じ節の「The recommended granularity is the **coarsest** feature set whose `acc` is still within the margin」は誤り: `acc` は粗い集合へ向かって増えない（自分とそこから作れる粗い集合の最大）ので、幅に入る集合は粗い側へ閉じており、「最も粗い」は常に `counts_only` になる。意図は「幅に入る**最も細かい**（順序で極大の）集合」。
- **選択肢**: A = 上端 ≤ 2/K ／ B = 上端 ≤ 1/K + 5 ポイント（K = 1000 では偶然の 51 倍まで許す）／ C = 幅を決めず記述だけ。
- **研究者の選択**: **A**（推奨）。K によらない尺度で、K = 1000 でも意味を持つ。Wilson 区間はブロック内の相関を無視する（`e2/README.md:93-98`）→ 上端で判定することで一部を吸収し、残りは限界に書く。
- **影響**: 事前登録に定義を書く。`e2/README.md` の「coarsest」を直す（凍結の前）。

## 判断 98: 事前登録の下書きでのメインの実装上の選択（2026-10-01・G-GEAR・メインの選択・研究者が覆せる）

★ 判断 90〜97 を実体にするときに、研究者に問わずに決めたもの。すべて `experiment/preregistration.md`（下書き）に書いた。凍結の前なら変えられる。

1. **本番の生成の config のファイル** = `experiment/plan_config.macos.json`（macOS の 2 セルで共用。ON は `recipes.json`、OFF は `recipes.macos-live-off.json`）。値は判断 85・90。凍結のハッシュ（`config.json`・`SEED`・`gt_rules.json`）には入れず、凍結のタグで固定する（計画のヘッダーが SHA-256 を持つ）。G-GEAR で両セルの計画を生成して `--validate` が exit 0（ON 3,150 試行・126 ブロック・推定 42,846 s ＝ 11.9 h／OFF 2,925 試行・117 ブロック・40,224 s ＝ 11.2 h）。G-GEAR（Python 3.11.9）の計画の SHA-256: ON `c7a5469de0febbbc2e90259e477900ab0eb68c74b86f420b1e9491799a1210ba`・OFF `3759ebf7832ba561820abab504929dbadd7e775a33e22ba0e89b92e4800009a2`。⚠️ 生成器の README は「バイト一致は同じ機械・同じ Python の版でだけ保証」と書く → 本番の計画は Mac で生成し、run の manifest の `plan_sha256` で辿る（Mac で同じ値になるかは引き継ぎで確かめる）。
2. **seed** = すべて `experiment/SEED` の値（20260929）: 計画の生成・E2 の closed set の `--seed`・open set の `--split-seed` と `--seed`・解析のブートストラップ。別々の値にする理由が無い（用途どうしで乱数を共有しない）。
3. **E2 の固定値**: closed set は K = 10 / 100 / 1000・6 つの特徴集合・`--markers-in-obs`（矢印のマーカーは観測に残る）・`--ime-toggle-in-obs` は付けない（パイロットで、macOS の入力モードのキーは観測に行が出なかった）・セルごとに別々に回す（手順書の照合）。open set は `--split both`（K1 と K1+）・n = 3・Witten–Bell・beam 8・`--length-info both`・`--eval-fraction 0.2`（作品単位では 12 作品中 3 作品が評価側になる。`split_phrases` を読んで確かめた）・bootstrap 1000。出力の名前は `results/e2_closed_set_<cell>.json` / `results/e2_open_set_<cell>.json`。
4. **E3 の `working`** は、ライブ変換 ON のセルの計画（約 11.9 時間）を流す。サンプラーは 8 時間で止める。E1 の夜とは分ける（サンプラーの負荷を E1 に混ぜない）。
5. **止める規則**: 各セルは 1 回の run で完了させる。中止された run は同じ計画で新しい run ディレクトリから最大 3 回まで。中止の run は理由とともに報告し、解析しない。3 回で完了しなければ「測れなかった」と報告する（`pipeline.py` は中止の run を数え、同じラベルの中止していない run は 1 つだけを求める・判断 62）。
6. **登録の範囲**: この登録は macOS の 2 セル。Windows のセル・Google 日本語入力・参照入力欄以外のアプリでの転移確認は含めず、行うなら測る前に追補で登録する（設計の縮退順〔判断 14〕で任意のものは、手順を較正していないので凍結に入れられない）。
7. **書誌**: 公開物は著者と年で引き（判断 76）、内部の書誌は `docs/references.md` に `[V184]` Bland & Altman（1986）・`[V185]` Cohen（1960）・`[V186]` Shrout & Fleiss（1979）・`[V187]` McGraw & Wong（1996）・`[V188]` Efron（1979）・`[V189]` Witten & Bell（1991）を足した。既存の `[P269]` Dhakal ら（2018）・`[V179]` Wilson（1927）・`[V181]` Cameron ら（2008）に使用箇所を書き足した。書誌は Crossref で、Efron の頁は Project Euclid の引用の行で確かめた（本文は Dhakal ら以外は読んでいない・手法の出所として書誌で引くだけ）。
8. **公開物の直し**（凍結の前）: `notes.md` の主張の表は、内部の設計文書の番号（C3〜C5）を指していて、しかも design.md §0 と食い違っていた（設計では C3 ＝ E1・C4 ＝ E2・C5 ＝ E3、表では C3 ＝ 検出・C4 ＝ L1・C5 ＝ L2）→ 問いと結果のファイルの表に書き直した。借りた手法の表に出典を入れ、「出典は `[Pn]` で足す」を消した（判断 76）。Wilson の使用箇所（「3 つの結果すべて」は L2 に当たらない）と、時計のずれを補正しないこと（判断 94）も直した。

---

★ 以下 2026-10-01（G-GEAR・M3 の attack-me round 1 の後）。記録は `attack-me/prereg-ime-macos/round-1/`（`verdict.md` が裏取りと判定）。査読者役 3 人（R1 計測の道具の検証・R2 書字研究の利用者と公開の安全・R3 統計と事前登録）はいずれも major・fatal 0。研究者に AskUserQuestion で 8 問（4 問 × 2 回）を問い、8 問とも推奨どおりに決まった。⚠️ 査読の結果は研究の証拠ではない（採否の材料）。下の数値は、メインが一次（コード・計画）で取り直したもの。

## 判断 99: 20 秒の打ち切りは、推定の対象を分ける（2026-10-01・G-GEAR・研究者の選択・attack-me round 1 の X1）

- **所見**（3 人一致・裏取りは真）: 観測器は 20 秒以上のセッションに行を出さない（仕様）。`match.py`・`l2.py` はこれを除かないので、recall の分母と L2 の正解側に入る。
- **一次**（メインが計画から数えた・観測の値は使っていない）: 両セルの計画を G-GEAR で再生成（SHA-256 は判断 98 の値と一致）し、観測器の定義（最初の英数字キー〜最初の終端キー）の期間を送出の時刻で数えた。20 秒以上は slow 31.7%（ON 333 / 1,050）・31.9%（OFF 311 / 975）、mid 約 11%、fast 約 9%。S13 を除くと slow 約 26%。思考を挟む S1・S2・S4・S7・S8 の slow は 44〜55%。間の無い S3 でも slow は 16 / 75（打つだけで中央値 14.7 s・90 パーセンタイル 23.6 s）。⚠️ 判断 90（480 ms）の時点では、この割合を見ていなかった。
- **付随**（コードで確認）: 打ち切りは「20 秒を過ぎた後の次の打鍵」で判定し、その打鍵をまっさらな状態に当て直す（`ime_compose.rs:219-235`）。英数字なら新しいセッションが始まり、断片の行（偽検出）になる。
- **研究者の選択**: **対象を分ける**（推奨）。送出の記録から観測器の定義で期間を決定的に計算し、20 秒未満の試行を Q1・Q2 の主の分母にする。20 秒以上は打ち切りの確認で別に数え、打ち切りの後の断片の行も数える。L2 は全試行（研究者が実際に受ける偏り）を主とし、20 秒以上を除いた版を副に出す。判断 90 の速さと計画は変えない。
- **実装**: 判断 100 の予測器が、試行ごとの「仕様の期間」と打ち切りの印を出す（同じ部品で X1 と X2 を満たす）。

## 判断 100: 観測器の規則から予想できる食い違いは、仕様の予測を参照として登録し、2 段で報告する（2026-10-01・G-GEAR・研究者の選択・X2・引き継ぎ §2 の 4 を閉じる）

- **所見**（R1 M4・監査役 1-2・コードで確認）: Backspace は観測のセッションを閉じない → S6 は試行の中で閉じず次の試行へ続く。Tab（`kVK_Tab → VK_TAB`）と `minus`・`comma`・`period`（`→ VK_OEM_*`）は「その他」で閉じる → S10 は Tab で閉じ、読みに「ー」「、」「。」を含む試行は途中で閉じる（計画で ON 113・OFF 99 試行。うち S12 のかな配列が ON 76・OFF 64）。ON の S1・S2・S7・S12・S15 は 1 回目の Return、S4・S5 は 1 回目の Escape で閉じ、正解は 2 回目以降で閉じる。⚠️ 観測の値は見ていない。
- **研究者の選択**: **仕様の予測を登録**（推奨）。送出の記録に観測器の状態機械（Rust の `step` と同じ表）を当てた「予測の行」を作り、(i) 正解 対 予測（推論規則の妥当性）と (ii) 予測 対 観測（実装と計時の忠実度）の 2 段で報告する。終端のキーを含む読みでも層を分ける。引き継ぎ §2 の 4（予想を書くか）は、数の予想ではなく「決定的な予測の行」を参照として登録する形で閉じる（検定の形にならない）。
- **費用**: Python の予測器と selftest・変異の追加。凍結が数日遅れうることを研究者は受け入れた。

## 判断 101: E2 の near chance は K = 1000 を判定から外し、規則の性質を載せ、2 セルの両方を求める（2026-10-01・G-GEAR・研究者の選択・X3・判断 97 の改訂）

- **所見**（3 人一致・裏取りは真）: 「Wilson の上端 ≤ 2/K」は、予定の n（S12 を除き ON 2,925・OFF 2,700）では、K = 1000 で偶然の水準の攻撃が通る確率が 0.210（ON）・0.067（OFF）しかない（メインが二項分布で再計算）。K = 10 は偶然の 1.85 倍、K = 100 は 1.47 倍まで通る。⚠️ 判断 97 の「K = 1000 でも意味を持つ」は、この n では成り立たなかった。
- **研究者の選択**: **K = 1000 を外す**（推奨）。K = 10・100 は 2/K のまま判定し、真の正解率が 1/K〜3/K のときの「通る確率」の表を事前登録に載せる。K = 1000 は記述にとどめる。推奨は 2 セルの両方で near chance の集合に限る。
- **実装**: 推奨はコードではなく報告された値から読む（`closed_set.py` は判定しない）→ 事前登録の文と、凍結の前に計算する表で直す。

## 判断 102: E2 の推奨は ms の時刻を持つ集合を対象外にする（2026-10-01・G-GEAR・研究者の選択・X4）

- **所見**（R1 M1・R2 major-1・major-3・裏取りは真）: 合成の打鍵間隔はキーと独立に引かれる（`generate_plan.py` の `_draw_iki`・`e2/README.md:123-124`）。人の記録で内容が漏れる 2 字の組ごとの間隔を、この設計は測れない。攻撃はセッションの行を読むが使わない（`e2/README.md:224-226`）のに、§6.7 は攻撃者が「the session rows」を見ると書く。
- **研究者の選択**: **ms の時刻は対象外**（推奨）。`all`・`no_runs` は「この設計では評価できない」と事前に書き、推定だけを報告する。1 秒のビン（`bin1s`・`bin1s_count`）と時刻なしの集合（`no_time`・`counts_only`）だけを判定する。セッションの行は推奨の対象外と明記する。人の休止の型を模していないことは限界に書く。理由: 2 字の組の間隔（数十 ms）は 1 秒のビンで消える。

## 判断 103: n の根拠は精度の目標に書き直し、推定値を形容しない（2026-10-01・G-GEAR・研究者の選択・X6）

- **所見**（R3 M3・監査役 1-4・2-2・R1 m7）: n の根拠が「1 晩に収まる」と、割合 0.95 付近の半幅の 1 例だけ。連続量には精度の目標が無く、Q3 は「agree するか」と問うのに基準が無い。`notes.md` は「informative の精度は事前登録に書いた」と言う。
- **研究者の選択**: **幅の表＋形容しない**（推奨）。主な推定量ごとに、予定の n での区間の幅の表を載せる（割合は p = 0.5・0.8・0.95 の各幅、連続量は SD の関数として）。各量に「その幅で言えること」を 1 文。Q3 は how closely に改める。要旨と結論では区間の範囲だけを書き、「よく一致した」などの形容をしないと約束する。n の根拠は「精度を目標に選び、1 晩に収まることを確かめた」に書き直す（design §1.5・判断 85 の実際の順序に合わせる）。

## 判断 104: L2 に試行ごとの差をシナリオ × 速さ別に足す（2026-10-01・G-GEAR・研究者の選択・X7）

- **所見**（R2 major-5・R3 M3 の 4・監査役 1-6）: L2 の文はシナリオを均等に混ぜた 8 試行で、偏りと ICC はどのシナリオが入るかで決まる。design §1.3a は速さとシナリオの両方の混合を意図していたが、今は速さだけ。
- **研究者の選択**: **試行ごとの差を足す**（推奨）。4 量の試行版（変換の数の差・変換時間の和の差・取り消しの数の差）をシナリオ × 速さ別に報告し、読者が自分の混合で重み付けし直せる形にする。文ごとの値と ICC は「この設計の均等な混合の下での値」と明記する。
- **実装**: `l2.py` に試行単位の表（selftest・変異つき）。

## 判断 105: 妥当性への脅威と限界の節を足す。畳まない規則での感度の解析は足さない。直す一覧（minor 19・nit 9）を承認（2026-10-01・G-GEAR・研究者の選択・X5 と一覧）

- **X5**（R1 M5）: **節だけ足す**（推奨）。目的の文を「参照入力欄が受けた呼び出しから §4.3 の規則で組み立てたセッションとの一致」に改める。脅威と限界（参照入力欄・規則・合成入力・学習を戻さない〔判断 91 の「限界に書く」〕・1 台・ソフトの時計・S9・物理キーの経路）を手当てか限界として書く。畳まない規則（example の `mac_nstic`）での再解析は足さない。理由: 畳まない規則は窓の幅の違いではなく「1 つの変換」の定義を変える。窓の幅はパイロットで 10〜900 ms のどれでも同じセッション（§4.3・判断 86）。畳んだ結果の影響は判断 96 の `n_continued_commits` の層で見える。
- **直す一覧**: `verdict.md` §3 の minor 19 件と nit 9 件を**承認**（推奨）。pooled の重みは、本文をコードに合わせて「件数の和」と書く（各シナリオの試行数は等しいので、除外と分割を除けば均等に近い。コードは変えない）。凍結のハッシュに入る `gt_rules.json`・`config.json` の `_note` も凍結の前に直す（監査役 3-3）。
- **次**: 直した版で attack-me round 2（同じ立場・同じ接地の文献・引き継ぎ `carryover-*.md` を渡し、再掲を求めない）。

## 判断 106: 他の IME と参照入力欄以外のアプリでの転移は、この研究の外（別の研究）にする。追補は Windows だけ（2026-10-01・G-GEAR・研究者の選択・判断 98 の 6 の改訂）

- **きっかけ**: 研究者の問い「感度の解析とは？ 具体的な IME の話なら、別の研究として実行するのが筋では」。→ メインの説明: 判断 105 の「感度の解析」は他の IME ではなく、同じデータで正解の組み立て方（自動確定を畳むか）を変える再解析のこと（足さないと決定済み）。他の IME を別の研究にする筋については、(1) 手順書と正解の規則は IME ごとに較正パイロットが要り、実質は別の計測になる、(2) この論文の問いは「この観測器と方法が標準 IME でどこまで一致するか」で、IME をまたぐ一般化は別の問い（転移）、(3) 追補の範囲を Windows に絞ると監査役 3-2 も解ける、を挙げた。Windows（Microsoft IME）は主張 C2（両 OS）の中核なので、この論文の追補に残す。
- **研究者の選択**: **別の研究にする**（推奨）。事前登録 §1.3 は、追補で登録するのを Windows のセル（と E3 の Windows・監査役 1-9）だけにし、他の IME と他のアプリでの転移は「この研究の外」と書いて、限界と今後の課題に回す。
- **影響**: 判断 98 の 6 の「Google 日本語入力と参照入力欄以外のアプリでの転移確認は、行うなら測る前に追補で登録」を改める。design §1.6（転移確認）・判断 14 の縮退順の任意の項目は、この論文の範囲から外れる。§7 は Windows の追補の範囲（新しいファイルの追加を含む）を書き直す。

---

★ 以下 2026-10-01（G-GEAR・attack-me round 1 の直しの実装）。判断 99〜106 を実体にするときに、研究者に問わずに決めたもの（引き継ぎ §0「実装の細部はメインの実装上の選択」）。凍結の前なら変えられる。

## 判断 107: round 1 の直しの実装上の選択（2026-10-01・G-GEAR・メインの選択・研究者が覆せる）

1. **照合の組み込みの形**（判断 99・100）: `match.evaluate` に `prediction_bytes` と `scope`（`all_trials` / `under_limit` / `over_limit`）を足した（CLI は `--prediction` / `--scope`）。`long` の試行は除外と同じく**試行の単位**で分ける（その試行の正解のセッションと、重なりで割り当たる観測の行をまとめて）。どの試行にも属さない行は `under_limit` 側。比較は 3 つ: `gt_obs`（主）・`gt_pred`（段 (i)・観測を読まない）・`pred_obs`（段 (ii)）。`pred_obs` は予測の行を正解の形（`spec_predict.as_sessions_bytes`）にして基準に置き、**正解の除外をそのまま引き継ぐ**（3 つの比較が同じ試行を覆う）。予測のセッションの試行は「始まった試行」ではなく、正解と同じ**重なり最大**で割り当てる。
   - L1 は 3 つの比較 × `under_limit`（主）・`all_trials`。L2 は `gt_obs` だけ × `all_trials`（主）・`under_limit`（副）。L2 を段 (i)(ii) に回さない理由: 2 段は 1 セッションの振る舞い（規則とその実行）を分けるためで、L2 はその関数（集計）なので、研究者が受ける偏りとして `gt_obs` だけを出す。
   - L2 の `under_limit` は**文を残し**、`long` の試行のセッションと行を両側から抜く（文を丸ごと捨てると slow の文はほぼ全部消える: 0.68^8 ≈ 5%）。`dwell_fraction` の分母（文の時間）は変えない。試行ごとの表（判断 104）は範囲の外の試行を除く。
2. **診断の層**: `carried_out`・`received_carry`（`n_started == 0`）・`closing_key_in_reading`（`minus` / `comma` / `period` を送る試行。かな配列でも、読みの中で観測器が閉じるキーはこの 3 つだけと一次で確かめた・selftest でも確認）・`none`。層ごとの照合のやり直しはせず、同じ照合を層で数える。出力は pooled と速さ別（シナリオ × 速さは主の表にあり、層 × 層別にすると結果のファイルが合成 64 試行で 2.2 MB になった）。
3. **結果のファイルの形**: `cells[label][definition][comparison][scope]`。各ファイルの頭に `primary`（比較と範囲）と `keymap_sha256`。`e1_detection.json` に `predictions`（予測の要約・層別の `long` の数）と `same_sessions_as_all`（2 つの定義が同じセッションか・群 I）。Windows の計画（予測なし）は `gt_obs` × `all_trials` だけ。
4. **合成の run**: oracle に打鍵（文字・Return・Escape・矢印）を載せ、計画の steps を oracle の打鍵と一致させた（配送の報告が計画と oracle を突き合わせるため）。16 試行ごとに、長音記号を含む試行・21 s の試行（20 s の後に数字）・Backspace で取り消す試行を置く。合成の観測は `inject.py` が **20 s 未満の正解のセッションだけ**から作る（観測器は 20 s 以上に行を出さない。予測器とは独立）。
5. **L1 の追加**（minor 7）: 一致の限界（LoA）の上下それぞれにブロックのブートストラップの区間・kappa にブロックのブートストラップの区間（未定義のときは理由つきで出さない: `no_kappa` / `fewer_than_two_blocks` / `undefined_resample`）・速さ別の層（`by_speed`。kappa は層の中では片方の結果しかないことが多いので、速さ別で読むと事前登録に書いた）。
6. **配送の報告** `kit/analysis/delivery.py`（minor 5・16・4）: Sonnet の作業用エージェントに仕様を渡して書かせ、メインがコードを読み、selftest を回し、フォーカスの喪失（参照入力欄の `focus_out` を試行ごと・層ごとに数える）を足した。送出の遅れ（計画の予定に対して・単調時計）・両方向の到達（観測の key 行・参照の `key_down`、入力モードのキーを含む / 除く）・行の遅れと間隔の誤差（数が一致した試行だけ）。パイプラインの 4 つ目の結果 `e1_delivery.json`。`data.md` の預け方に「試行の中で送出の無い行が 0、試行の外の行がマーカーとかなの押下（1 ブロック 5）を超えない」を足した。
7. **事前登録の中の選択**: 実行の順は ON → OFF → E3 `idle` → E3 `working`（E3 の再生が E1 の前に学習を足さない）／E3 の条件が不足（480 標本未満・4 時間未満）なら §3.4 と同じく最大 3 回／closed set が exit 2 で止まったらそのセルは「計算できなかった」で、推奨はしない／ブロックの途中の焦点の喪失は除外せず数える／OS・IME の版が変わったら逸脱として報告し、記録どおり解析／open set のブートストラップを 1,000 → **2,000**（解析と揃えた・判断 98 の 3 を改める。理由を書くより揃えるほうが単純）／`all` の定義は一致の確認だけ（`same_sessions_as_all`）／解析は凍結のタグのクリーンな取り出しから回し、コミットを `notes.md` に書く（R1 n3）／§9 に `plan_config.macos.json`・2 つの手順書・コーパス・キーマップの SHA-256（計画のヘッダーの値と一致を確かめた）／精度の表は `stats.wilson` で x = round(p·n) の半幅（引き継ぎの値と一致）／E2 の近いの規則は時刻なし・1 秒ビンの 4 集合に、K = 10・100 の両方、2 セルの両方で当てる／予測の値の開示は、計画の時刻で組んだ擬似 oracle（送出の遅れなし・ブロックの間 2 s）から出した値（引き継ぎ・tasklist の値と全部一致）。
8. **足さなかったもの**: 先行研究の位置づけ（群 M）は、基準をソフトの層に置く理由と外部の時計を使わない限界を §7 に書くにとどめ、文献を引く段落は原稿（`manuscript/`）に回す（事前登録に文献の総説は要らない・引くなら citation-ssot で本文を読んでから）。4 つの集計量は「例示であり文献の総説から選んだものではない」と書いた（R2 minor-2 の後者）。
9. **確認**: selftest 全部（`kit/check.sh` 29 本・`delivery.py` を含む）・`run.sh --synthetic` 2 回で 4 ファイルともバイト一致・`_style_check.py` 違反 0 件・`check_citations.py` 違反なし・`--check-prereg` は exit 3（未凍結を正しく判定）。変異はメインが 4 回に分けて 31 本（ほかに作業用エージェントが `delivery.py` に手で 12 本・すべて赤）: 生き残りは 5 本で、うち 4 本はテストを足して赤にした（Tab を閉じるキーに数える・`pred_obs` に正解を渡す〔合成では数が偶然一致した〕・長いセッションを inject に渡す・合成の計画と oracle の時刻のずれ）。1 本（LoA の区間で 2 対未満を除く条件）は等価（1 対なら 1 ブロックで、ブートストラップがもともと区間を出さない）なので、条件のほうを消した。

---

★ 以下 2026-10-01（G-GEAR・M3 の attack-me round 2 の後）。記録は `attack-me/prereg-ime-macos/round-2/`（`verdict.md` が裏取りと判定）。同じ立場・同じ接地の文献で、役ごとの引き継ぎ（`carryover-*.md`）を渡して回した。推奨は R1 minor・R2 major・R3 minor（R3 は新しい major 2 件を凍結の前に直す条件つき）・fatal 0・接地の引用の捏造 0 → 判定 major revision。round 1 の引き継ぎ 47 件は、査読者の判定で解消 25・部分的に解消 19・未解消 3。新しい穴の多くは、round 1 の直しで**新しく足した部分**（§3.3 の精度の文・§6.4 の範囲と比較と層・§6.8 の依存の理由づけ）にあった。研究者に AskUserQuestion で 10 問（4・4・2）を問い、10 問とも推奨どおりに決まった。⚠️ 査読の結果は研究の証拠ではない（採否の材料）。下の数値は、メインが一次（コード・計画・`stats.wilson`）で取り直したもの。

## 判断 108: 問 3 の主を `under_limit` に、`long` を打鍵が入った試行すべてに広げ、問 3 に区間を足す（2026-10-01・G-GEAR・研究者の選択・round 2 の X1・X2・X5・判断 99 と 107 の 1 の改訂）

- **X1 問 3 の主**（R2 N3・R3 N1 がともに major・裏取りは真）: 判断 99 は問 3 の主を全試行（研究者が実際に受ける偏り）にしたが、§7 は「打ち切りの割合はこの設計の性質で、自然な打鍵の性質ではない」と書く。slow の long は ON 423 / 1,050 で、主の値は思考時間の分布（0.2〜20 s の対数一様）で決まる。→ **研究者の選択: `under_limit` を主に**（推奨）。問 1・2 と揃う。打ち切りは「20 秒以上のセッションは行を持たず、その後の英数字は断片の行になる」という決定的な規則として示し、読者が自分のセッションの長さの分布に当てられるようにする。`all_trials` は「この設計の打ち切り率の下での値」として副に出す。判断 99 の L2 の部分と、判断 107 の 1 の「L2 は `all_trials`（主）」を改める。
- **X2 `long` の定義**（R1 N3・R3 N4・監査役 2-a・3-i・裏取りは真）: `long` は打ち切られたセッションが**始まった試行**に付く（`spec_predict.py`）。S6 から持ち越したセッションが後の試行で打ち切られると、その後の試行の断片の行や失われたセッションが `under_limit` に残る。`received_carry` も `n_started == 0` だけで決めるので（`match.py:739`）、打ち切りの後に断片を始めた受け手を拾わない（§3.1 の数から ON で最大 75 試行）。→ **研究者の選択: 打鍵が入った試行すべてに広げる**（推奨）。`long` を「打ち切られたセッションに打鍵が 1 つでも入った試行」、持ち越しを受けた層を「前の試行で始まったセッションに打鍵が入った試行」に定義し直す（予測から決定的）。§3.1・§3.3 の数は計算し直す。
- **X5 問 3 の区間**（R3 N3 (i)・メインが `l2.py:310-319` で確認: `_agree` は Bland-Altman の点だけを返し、区間は ICC だけ。`mixture_bias` も点だけ）: §6.1 は「the limits of agreement … carry 95% percentile bootstrap intervals」と書く。→ **研究者の選択: `l2.py` に区間を足す**（推奨）。偏り・一致の限界の上下・混合の偏りに、ブロックのブートストラップの区間（selftest・変異）。理由: 主の推定に変動の尺度が無いのは規程 J5 に反し、凍結の後に足すと作り方を結果の後に選ぶことになる。

## 判断 109: E2 は 1 秒のビンを推奨から外し、打鍵の欠けはブロックで合わせ直す（2026-10-01・G-GEAR・研究者の選択・round 2 の X3・X4・判断 102 の改訂）

- **X3 1 秒のビン**（R1 M1 の残り・R2 N1 major）: ms の集合を外した理由（合成の間隔はキーによらず、この設計は人の時間の構造を作らない）は、1 秒のビンにも当たる。人の記録で 1 秒のビンに残るのは語・句の境の休止とビンごとの英字の数で、§6.8 自身が「Pauses between words and phrases … are not modelled either」と書く。→ **研究者の選択: 1 秒のビンを推奨から外す**（推奨）。推奨は `no_time`・`counts_only` だけ。`bin1s`・`bin1s_count` は ms の集合と同じく推定だけを報告する。⚠️ 代償: 推奨する粒度では時刻の指標が残らない（R2 minor-5 の中間の粒度は round 1 から未採用のまま）。判断 102 の「1 秒のビンと時刻なしの集合だけを判定する」を改める。
- **X4 打鍵の欠け**（R1 N5・R2 N2 major・裏取りは真: `closed_set.py` の selftest「one missing press stops the run instead of shifting later trials (exit 2)」・`open_set.py:70-71`・`data.md` 手順 4 は余分な行だけを検査）: 1 セル約 10 万打鍵で、パイロットの 0 / 約 8,080 では欠けの率の上限を小さく言えない。→ **研究者の選択: ブロックで合わせ直す**（推奨）。ブロックの印で合わせ直し、打鍵が計画と合わないブロックの試行は「採点しない」として数え、残りで判定する。closed set と open set の両方。§6.2 の「止まったら計算できなかった」を改め、§6.8 の n は採点した試行の数と書く。

## 判断 110: パイロットの生ログを預ける約束を戻し、追補は既存のファイルの Windows の部分も変えてよいとし、直す一覧を全部承認して round 3 を回す（2026-10-01・G-GEAR・研究者の選択・round 2 の X6・X7 ほか）

- **X6 パイロットの生ログ**（R1 m11・R2 minor-7・監査役 1-a・裏取りは真）: `29372289` で §3.1 の「its raw logs will be deposited with the measurement data after the check that report describes」が落ちた（判断 99〜107 にこれを消す判断は無く、design §1.1a の意図は「生ログも公開物に含める」。⚠️ メインの書き直しの漏れ）。封印したパイロットの観測ファイルを凍結の後にどうするかも登録に無い。→ **研究者の選択: 約束を戻し、封印は預けるときだけ開ける**（推奨）。基準を満たすパイロットの run の生ログを本計測のデータと預ける。封印したセッション行は、凍結と本計測の後に預けるためにだけ開け、解析しない（探索にも使わない）と登録する。基準そのものは Mac の残りの作業（`pilot-macos.md` の "Raw logs"）。
- **X7 Windows の追補**（監査役 3-d・裏取りは真: Windows の手順は既存の `kit/gen/recipes.json` と `recipes.macos-live-off.json` の `os.windows`、Return と Escape の回数は `generate_plan.py` の `_PROFILES["windows"]` にあり、`kit/gen/README.md` はそこを直せと書く。§8 は「既存のファイルは変えない」）。→ **研究者の選択: 既存のファイルの Windows の部分も許す**（推奨）。追補は 2 つの手順書の `os.windows` と `_PROFILES["windows"]` も変えてよい。macOS の部分が変わらないことは 2 つの凍結のタグの差で示し、macOS の解析は macOS のタグから回す。
- **監査役の応答の保存**: 応答に一覧の外のパス（`kit/refinput-windows/README.md:135`・Grep の出力に 1 行出ただけで指摘に使っていない、と本人）が 1 件あり、Skill の規則で写さずに問うた → **写す**（推奨）。逸脱として `verdict.md` §5 に記録。
- **直す一覧**: `verdict.md` §3 の X8（n の根拠の書き直し・n は変えない）・minor 26 件・nit 12 件を**全部承認**（推奨・コードを伴う minor 3・4・10・13・15 も）。
- **round 3**: **回す**（推奨）。同じ立場・同じ接地で、今回変わった節とコードに絞る。理由: round 2 では、round 1 の直しで新しく足した部分に新しい穴が入った。凍結は取り消せない。

---

★ 以下 2026-10-01（G-GEAR・attack-me round 2 の直しの実装）。判断 108〜110 を実体にするときに、研究者に問わずに決めたもの。凍結の前なら変えられる。

## 判断 111: round 2 の直しの実装上の選択（2026-10-01・G-GEAR・メインの選択・研究者が覆せる）

1. **`long` の広げ方**（判断 108 の X2）: 予測の各セッションに「打鍵が入った試行」の集合（`trials`）を持たせる。開いているセッションに当たった打鍵（閉じる打鍵を含む）はその試行を足す。⚠️ **打ち切る打鍵は、打ち切られたセッションに入らない**（打ち切りが遷移より先に来るため）。→ 打ち切りの後の最初の打鍵が次の試行の先頭なら、その試行は `long` にも `received_carry` にもならない（selftest で守る）。`long` = 打ち切られたセッションに打鍵が入った試行、`received_carry` = 前の試行で始まったセッションに打鍵が入った試行。出力の形式を `spec_predict/2` に上げ、`match.py` は `received_carry` の真偽値を必須にした（古い出力は拒む）。`match.py` の出力の `scope` に `layer_none_trials` を足した（L2 の試行ごとの表の層 none のため）。
2. **数の再現の手順**（R3 の「表の値を再現できる手順」）: `spec_predict.py --from-plan` を足した。計画の時刻から送出の記録を組む（`oracle_from_plan`: 印は `marker_gap_ms` 間隔・試行は `gap_before_ms` の後・打鍵は `at_ms`・ブロックの間 2 s）。⚠️ 前の版の使い捨てのスクリプトの値（ON の行 2,638・打ち切り 719・旧定義の long 677・持ち越し 188・始めない 113・分割 314・終端キー 113、OFF も同様）を**すべて再現した**ことを確かめてから、新しい定義の値を事前登録 §3.1・§3.3 に書いた: long は ON 755（slow 447・mid 198・fast 110）・OFF 713（422・192・99）、`received_carry` は両セル 184、S13 は全試行が打ち切り（前の版の 1 / 4 / 6・0 / 2 / 2 は、始まった試行だけを数えた結果）。§3.3 の最小の層は 31（ON の S1 slow・OFF の S8 slow）。精度の表は x = round(n·p) と明記した。
3. **問 3 の主**（X1）: `pipeline.py` の `PRIMARY["l2"]` を `under_limit` に・`L2_SCOPES` を主から並べた。`PRIMARY_NOTE` に「`all_trials` の値はこの設計の long の割合に依存」と足した。
4. **問 3 の区間**（X5・Sonnet の作業用エージェントが実装・メインが差分を読み、selftest を回し、抜き取りの変異 2 本で確かめた）: `_agree` に偏り・一致の限界の上下のブロックのブートストラップの区間（状態は偏りと限界で別。偏りは 1 テキストでも定義されるため）。`mixture_bias` は**層化した**ブロックのブートストラップ（速さごとに独立に再標本、同じ複製から各混合を組む。重み 1 を 1 つの速さに置いた混合はその速さの区間と一致）。`per_trial` に `only_trials` を足し、`per_trial_layer_none` を出す（`layer_none_trials` が無い古い match の出力では null）。
5. **E2 の合わせ直し**（判断 109 の X4・Sonnet の作業用エージェントが実装・メインが `align_blocks` を読み、selftest を回し、抜き取りの変異 2 本で確かめた）: `closed_set.align_blocks` / `align_plan` を `open_set` からも使う（open set の照合を「数と英字の数」から**区分の並びの全体**に強めた）。錨は「印と同じ区分の並びが、ちょうどその長さの連なりで現れる位置」（4 つ続く navigation は印だけに出る）。合わないブロックは自分の印で一度探し直し、だめなら次のブロックの印へ。印が壊れたときは、見つけた錨で次のブロックが丸ごと合えばそこから再開する（損失は原則 1 ブロック）。`n_presses_unassigned` は「採点したブロックが覆わない押下」（採点しないブロックの押下を含む）。`--markers-in-obs` が無いときは今までどおり止まる（錨が無い）。closed set に `--bootstrap`（既定 2,000）・正解率のブロックの区間（記述・最大は再標本ごとに取り直す）・`by_speed`。事前登録 §6.8 のコマンドに `--bootstrap 2000` を足した。
6. **焦点の喪失**（minor 10）: `delivery.py` が `trials_with_focus_out` を出し、pipeline が S15 以外のその試行に割り当たる行と偽検出を、すべての検出の結果（`focus_loss`）に数える。配送の報告は先に計算する（観測のセッション行は pipeline が読む。配送の報告は今までどおり key 行だけ）。
7. **組成**（minor 4）: `predictions.composition` に、層 × 範囲ごとの英字のキー数と思考時間（`think_ms` > 0 の試行）の分布を計画から出す。
8. **足さなかったもの**: minor 13（`carry_over` で除いた試行の観測の行）は `match.py` がすでに `excluded.obs.by_reason` で数えているので、文だけ。R2 nit 3（打ち切り・配送・合成の間隔の説明の重複を 1 か所に寄せる）は任意で、今回はしていない（本文は 9,326 語から 11,217 語に増えた・同じ測り方）。R2 minor-5（中間の粒度）は round 1 から未採用のまま、§7 に「時刻を持つより細かい粒度は評価していない」と書いた。
9. **確認**: `kit/check.sh` 29 本緑・`run.sh --synthetic` 2 回で 4 ファイルともバイト一致・`_style_check.py` 違反 0 件・`check_citations.py` 違反なし・`--check-prereg` exit 3（未凍結）・§9 の SHA-256 の表の 5 ファイルは今の値と一致・本文の「section N」はすべて実在の節。変異はメインのコードに 13 本（予測器 7・照合 2・pipeline 3・配送 1）ですべて赤、作業用エージェントのコードに抜き取りで 4 本（`l2.py` 2・`closed_set.py` 2）ですべて赤（作業用エージェントの自己申告はそれぞれ 18 本・17 本）。⚠️ `gt_rules.json` の `_note` を直したので、凍結のハッシュの値は変わる（凍結の前なので問題ない）。

---

★ 以下 2026-10-02（G-GEAR・attack-me round 3 の後）。round 3 の記録は `attack-me/prereg-ime-macos/round-3/`（判定は major revision・R1 minor・R2 major・R3 major・fatal 0・捏造 0）。

## 判断 112: 問 3 の 2 つの量を範囲の上で定義し直し、run の中止は参照の外からの入力だけで閉じた規則で決める（2026-10-02・G-GEAR・研究者の選択・round 3 の Y1・Y2・判断 107 の 1 と判断 110 の minor 17 の改訂）

- **Y1 問 3 の主のテキストの量**（R2 A・R3 1 がともに major・裏取りは真: `l2.py` の `n_conversions` は範囲に残った試行のセッションの和、`dwell_fraction` の分母はテキスト全体の時間のまま〔判断 107 の 1 のメインの選択〕）: テキストを残して長い試行だけを抜くので、2 つの量がテキストごとに残る試行の数（＝この設計の打ち切り率）に比例し、ICC を押し上げ、速さのあいだと混合の偏りを比べられなくする。判断 108 で主を移した理由が、主の範囲にも形を変えて当たる。→ **研究者の選択: 範囲の上で定義し直す**（推奨）。`n_conversions` は範囲に残った試行 1 つあたり、`dwell_fraction` の分母は範囲に残った試行の時間の和。範囲に残る試行の無いテキストは null（§6.11）。`mean_dwell_ms`・`abandon_rate` はもともと比なので変えない。採らなかった: 長い試行の無いテキストに限る（slow ではほとんど残らない）・定義はそのまま限界に書く。
- **Y2 §3.4 の run 単位の中止**（R1 N-1 major・R2 5・R3 3・監査役 2-1・裏取りは真）: round 2 の直し（判断 110 が承認した verdict minor 17）で、観測器自身の重複行でも run を中止にでき、「説明できる」に基準が無く、検査の元に解析全体の出力（`results/e1_delivery.json`）を許し、時機が「預ける前」で §3.2 の「次の実行の前」と両立しなかった。→ **研究者の選択: 参照の外からの入力だけで中止**（推奨）。中止は参照のログの余分な key-down（実行器が送っていない打鍵）と試行の外の行の上限超えだけで、閉じた規則で決め、「説明」の裁量を無くす。観測の余分な行は観測器の結果として解析し、§6.3 で報告する。検査は `delivery.py` 単体（key 行だけ）で、各 run の直後・§3.2 の次の項目の前に行い、判断と時刻を解析の前に記録する。理由: 試験の対象の誤りで run を捨てる道を断ち、預ける前のプライバシーの検査（人の打鍵の混入）は残す。採らなかった: 認める説明の閉じた一覧・関門を無くす。

## 判断 113: E2 の推奨は句 1 つの識別の範囲として書き、パイロットの預ける基準と合わせ直しの実ログでの確認は凍結の前に Mac で行う（2026-10-02・G-GEAR・研究者の選択・round 3 の Y3・Y4）

- **Y3 推奨の単位**（R2 B major・裏取りは真: §6.8 の closed set は試行ごとに K 句から 1 つを当てる。`kit/e2/README.md` の Scope of the claim は「combine several trials of the same typist」を含まないと書くが、事前登録の推奨の文に無い）→ **研究者の選択: 範囲を書く**（推奨）。§6.8・§1.2 の問 4・§7 に、規則は句 1 つの識別を判定し、同じ書き手の複数の句の組み合わせ・既知の最終テキストとの突き合わせは評価せず、推奨はログ全体の安全を述べない、と書く。採らなかった: テキスト（8 試行）単位の記述の解析を足す（新しい推定の対象とコード。今後の課題）。
- **Y4 パイロットの Mac での作業**（R1 m11・R2 minor-7・監査役 1-a・R2 6・裏取りは真: `pilot-macos.md` の Raw logs は「will be written here」のまま。合わせ直しは selftest の合成データでしか試していない）→ **研究者の選択: 両方を凍結の前に Mac で**（推奨）。(1) 預ける基準と「封印したセッション行は預けるときだけ開け、解析しない」を `pilot-macos.md` の Raw logs に書く。(2) パイロットの観測の key 行に `align_plan` だけを流し（攻撃はしない・セッション行に触れない）、採点されたブロックの割合を §3.1 に報告する。理由: 合わせ直しに欠陥が 1 つ見つかったばかりで（verdict minor 1）、実ログでの確認が安く効く。⚠️ パイロットのログは G-GEAR に無い。

## 判断 114: round 3 の直す一覧を全部承認し、round 4 を直した箇所に絞って回す（2026-10-02・G-GEAR・研究者の選択）

- **直す一覧**: round 3 の `verdict.md` §3 の minor 16 件・nit 10 件を**全部承認**（推奨）。コードを伴う minor 1（`align_blocks` の再開: 試行の中の「矢印 4 つちょうど」の偽の錨に移ると、以後のブロックが全部採点されない。メインが合成の列で動かして確かめた）・2（焦点の喪失を `focus_out` から次の `focus_in` までの区間で数える）・4（速さごとの偏りの区間を 1 つに）・6（重み付けし直しの版を汚染の層だけを除いたものに）を含む。minor 15 は「区間を付けないものの一覧に足す」側。冗長さの nit は重複の多い 3 点（設計効果・打ち切りの規則・`all_trials` の依存）を 1 か所に寄せる。
- **round 4**: **回す**（推奨）。同じ立場・同じ接地で、round 3 の直しで変わった箇所（問 3 の量の定義・§3.4 の中止の規則・合わせ直し・焦点の喪失・推奨の単位など）だけを見る。理由: round 2・3 とも、前の直しで足した部分に新しい穴が入った。凍結は取り消せない。

---

★ 以下 2026-10-02（G-GEAR・round 3 の直しの実装）。判断 112〜114 を実体にするときに、研究者に問わずに決めたもの。凍結の前なら変えられる。

## 判断 115: round 3 の直しの実装上の選択（2026-10-02・G-GEAR・メインの選択・研究者が覆せる）

1. **問 3 の量**（判断 112 の Y1・Sonnet の作業用エージェントが `l2.py` を実装・メインが差分を読んだ）: 定義は**すべての範囲で同じ**にした（範囲が変えるのは、どの試行を数えるかだけ）。名前を `n_conversions` から `conversions_per_trial` に変えた（数ではなく率なので）。`dwell_fraction` の分母は「範囲の中の試行の窓（oracle の begin〜end）の和」で、`all_trials` でも試行の間の待ちを含まない（テキストの端から端までの時間より短い）。範囲の中に試行が 1 つも無いテキストは 4 つの量とも null で、速さごとに数える。テキストごとの「範囲の中の試行の数」の分布を速さごとに出す（`texts.trials_in_scope_by_speed`）。試行ごとの量（`per_trial` の `n_conversions` ほか）は名前も定義も変えない。
2. **run の中止**（判断 112 の Y2）: 閉じた規則は `delivery.py` の**今ある**出力（参照の `excess_rows`〔すべての押下〕と `rows_outside_trials`〔1 ブロック 5 まで〕）で書いた。`delivery.py` は記述だけの道具のまま（判定の欄は足さない）。外からの入力で中止にした run は**預けない**（参照のログは受けた key-down のキーコードを持つので、人の打鍵が入りうる）。`data.md` に「Run checks」の表を足し、手順 4 だった検査を実行の直後に行う手順 1 に移した。
3. **焦点の喪失**（判断 114 の minor 2・Sonnet の作業用エージェントが実装・メインが差分を読んだ）: 喪失の区間は `focus_out` から次の `focus_in` まで（無ければログの終わりまで）。続く `focus_out` は 1 つの区間にまとめる。S15 の試行は、重なる喪失の区間がすべてその試行の中で始まって終わるときだけ数えない（計画した切り替え）。出力の名前を `reference_focus_out` から `reference_focus_loss` に変え、pipeline 側の S15 の除外は消した（`delivery.py` が持つ）。`focus_loss` に速さごとの数（`by_speed`）。⚠️ pipeline に S15 の除外を書き戻す変異は pipeline の selftest では赤にならない（合成の run は焦点を失わない）。S15 の扱いは `delivery.py` の selftest が守る。
4. **区間の二重**（minor 4）: `mixture_bias.by_stratum` から区間を外した（登録の区間は `agreement_by_stratum` の 1 つ）。混合の区間は変えない。
5. **重み付けし直しの版**（minor 6）: `match.py` の出力の `scope` に `uncontaminated_trials`（carried out と received carry のどちらでもない試行）を足し、`l2.py` が `per_trial_uncontaminated` を出す。`per_trial_layer_none` は診断として残した（pipeline の selftest が名指しするため）。
6a. **合わせ直し**（判断 114 の minor 1・Sonnet の作業用エージェントが `closed_set.py` を実装・メインが読んで抜き取りの変異で確かめた）: ブロックが今の位置で合わなければ、そのブロックの印か次のブロックの印が「ちょうどその長さ」で立つ位置を順に見て、そのブロックが丸ごと合えば置き、次のブロックが丸ごと合えばそのブロックだけを採点せずにそこへ進み、どちらも合わない位置（試行の中の矢印 4 つなど）は飛ばす。どこにも無ければ、そのブロックだけを採点せず、位置は動かさない（次のブロックが同じ所から探す）。印はブロックごとに違ってよい。⚠️ ブロックの直後に足された矢印が次の印とつながって 5 つになると、失うのは次のブロック（1 つだけ）。§6.8 はそう書いた。メインの抜き取りの変異で、`delivery.py` の S15 の判定を「すべての区間が中」から「どれかの区間が中」にする変異が生き残ったので、selftest を 1 件足した（S15 の切り替えが戻った後に、もう一度失って戻らない場合）。
6. **文**: §3.1 に「預ける基準は凍結の前に `pilot-macos.md` に書く」「合わせ直しだけをパイロットの key 行に流し、採点したブロックの割合をここに書く」を約束として書いた（中身は Mac の作業・判断 113）。設計効果は §3.3 に 1 か所（2 つの計画から計算した値）、§6.1 は参照に。打ち切りの規則は §1.1 に 1 か所、§6.4 は参照に（冗長さの nit）。`all_trials` の依存は §6.4・§7・`notes.md`・`PRIMARY_NOTE` に残した（読む場所が違うため）。設計効果の式の出典は足していない（新しい書誌の確認が要る）。題の nit（任意）は変えていない。

---

★ 以下 2026-10-02（G-GEAR・attack-me round 4 の後）。round 4 の記録は `attack-me/prereg-ime-macos/round-4/`（判定は major revision・R1 major・R2 major・R3 minor・fatal 0・捏造 0）。

## 判断 116: run の中止はブロックごとの区間で数え、上限は凍結の前にパイロットの参照のログで決める。問 3 のテキストの大きさは開示する（2026-10-02・G-GEAR・研究者の選択・round 4 の Z1・Z2・判断 112 の Y2 の改訂）

- **Z1 §3.4 の中止の規則**（R1 新-1 major・R2 major・R3 新 1・新 2・監査役 1-C・3-A・裏取りは真〔仕組み〕）: 判断 112 の閉じた規則は、閾値（参照の `excess_rows` > 0・`rows_outside_trials` がブロックあたり 5）が確かめていない前提に立つ。runner のかなキーは oracle に行が無く、`run_cell.py` は前のブロックの最後の `trial_end` の直後（`emit.py` の `run_block` は待ちを置かない）に次のブロックの `focus_cmd` を走らせるので、参照がかなキーを `key_down` に残し、それが `delivery.py` の窓（`trial_end` + 300 ms・`block_end` では切らない）に入れば、外からの入力の無い run が `excess_rows` で中止になる。残らなければ 1 ブロック 1 打鍵の見逃しの余裕になる。加えて「in each block」なのに道具は run の合計しか出さず、窓の引数・道具が入力を拒んだ場合・問 5 の `idle` が決まっておらず、`pipeline.py` は manifest の `aborted` しか見ない。⚠️ かなキー（104）が参照の `keyDown(with:)` に届くかは、パイロットのログが無い G-GEAR では確かめられない。→ **研究者の選択: ブロックごとの区間で数え、Mac で確かめる**（推奨）。`delivery.py` にブロックごとの区間（`block_begin` から次の `block_begin` まで・最初のブロックの前を 1 区間）で「参照の `key_down` のうち送った打鍵で説明されない数」を出させ、§3.4 の規則を「どれかの区間でこの数が印の打鍵＋かなキーの数を超える」にする（かなキーがどの窓に落ちても同じ数になる）。命令行（窓の値）・`delivery.py` が入力を拒んだ run は中止に数えること・検査の対象を §3.4 に書き、§6.3 は §3.4 を参照するだけにする。`pipeline.py` も同じ規則を配送の報告から当て、当たる run を拒む。上限の数（かなキーを数えるか）は、凍結の前に Mac でパイロットの参照のログに当てた結果で決め、§3.1 に書く（判断 117）。理由: runner を変えずに窓の位置の問題が消え、前提は実ログで確かめられる。採らなかった: runner を変えてかなキーを構造的に窓の外へ出す（oracle の形式・検証器・予測器まで触る）・今の規則のまま。
- **Z2 問 3 のテキストの大きさ**（R2 新 minor・R3 新 3・裏取りは真: メインが計画と予測から計算すると、テキストあたりの範囲の試行の数 k の平均は ON で slow 4.60・mid 6.49・fast 7.17、OFF で 4.56・6.43・7.21。slow で k ≤ 3 が 30 / 126・27 / 117、k = 8 は 4・0。k = 0 は無い）: 判断 112 で量を範囲の試行の上の率にしたので long の割合で値は動かなくなったが、一致の限界と ICC が k の混合になり、速さのあいだで比べにくい。→ **研究者の選択: 開示する**（推奨）。§6.7 と §7 に「主の範囲の一致の限界と ICC は、この設計のテキストあたりの範囲の試行の数の分布の上の値で、速さのあいだで比べない」「偏りはテキストに等しい重みの平均」「k が小さいほど、片側で値が計算できずに落ちるテキストが増える」と書く。採らなかった: k の階級ごとにも報告する（slow の k = 8 は 4 / 0 テキスト）・主を k ≥ m のテキストに限る（推定の対象が変わる）。

## 判断 117: 凍結の前の Mac の作業を広げ、その後に絞った round 5 を回す。round 4 の直す一覧を全部承認し、R3 の応答を写す（2026-10-02・G-GEAR・研究者の選択・判断 113 の Y4 の拡張）

- **Z3 Mac の作業**（判断 113 の Y4 に足す・R1 新-1 (a)・新-6・R2 新 major・新 minor・R3 新 2・nit・監査役 1-C・3-D・3-E・3-F）→ **研究者の選択: 広げて round 5**（推奨）。凍結の前に測定機で: (1) 預ける基準と「封印したセッション行は預けるときだけ開け、解析しない」を `pilot-macos.md` の Raw logs に書く。時点は「凍結の前」に揃え、観測の余分な行の扱いを本計測（判断 112: 観測の余分な行は観測器の結果で、中止・保留の理由にしない）と揃える（監査役 3-E）。(2) 合わせ直し（`align_plan`）だけを、矢印の印を使ったパイロットの run（`pilot2-on`・`pilot2-off`・`verify-off`）の観測の key 行に、`--markers-in-obs` とパイロットの 3 打鍵の印で流し（攻撃はしない・セッション行に触れない）、採点されたブロックの割合を診断として §3.1 に書く（最初のパイロットの F13・F14 の印は観測に行が無いので対象外）。コードの欠陥が見つかれば凍結の前に直し、前後の割合を書く。(3) 同じ run の参照のログに `delivery.py` を当て、かなキーと S14 のモードキーが参照の `key_down` に残るか・ブロックごとの区間の「説明されない数」を §3.1 に書き、Z1 の上限の数を決める（パイロットの印は 3 打鍵）。その後 G-GEAR に戻り、§3.4・§3.1・§6.7・`delivery.py`・`closed_set.py` に絞った round 5 を回してから、完了時レビュー → PR。理由: round 2〜4 とも直しで足した所に新しい穴が入った。Z1 の上限は Mac の結果で決まるので、その文は査読を通してから凍結したい（接地の本文は G-GEAR にだけある）。採らなかった: round 5 を回さない・判断 113 のまま（Z1 の前提を確かめない）。
- **直す一覧**: round 4 の `verdict.md` §3 の minor 8 件・nit 8 件を**全部承認**（推奨）。コードを伴う minor 1（合わせ直しの錨を右に揃える: ブロック末の S7 の Enter が欠けると末尾の矢印が次の印とつながり 2 ブロックを失う。メインが `align_blocks` を論理で追って確かめた）・2（`per_trial` が計画にある層で試行の無いものを null と理由で出す: 汚染の無い版では S6 が両セル・全速さで 0 試行）・5（`spec_predict.py --from-plan` に層ごとの Σm²/Σm を出させ、§3.3 の設計効果の値を再現できるようにする）を含む。
- **R3 の応答の保存**（機械の検査で一覧の外のパスが 1 件〔Grep の対象の親ディレクトリ・偽陽性の型〕・本人の申告で一覧の外の `kit/emit/emit.py` の 355〜379 行を Read〔指摘には使っていない〕）→ **写す**（推奨・判断 110 の先例と同じ）。有効な査読は 3。

---

★ 以下 2026-10-02（G-GEAR・round 4 の直しの実装・`4bd6cacd`）。判断 116・117 を実体にするときに、研究者に問わずに決めたもの。凍結の前なら変えられる。

## 判断 118: round 4 の直しの実装上の選択（2026-10-02・G-GEAR・メインの選択・研究者が覆せる）

1. **区間の数え方**（判断 116 の Z1・Sonnet の作業用エージェント A が `delivery.py`・`pipeline.py` を実装・メインが差分を読み、抜き取りの変異 2 本で確かめた）: 区間は oracle の `block_begin` の壁時計で切る半開区間（`block_begin` の時刻ちょうどの行は新しいブロックの区間）。`n_reached` は「区間に `trial_begin` がある試行」の min(sent, その試行に割り当たった行のうち区間の中にあるもの) の和にした（窓の始まりが前の区間にはみ出す端の場合でも `n_unexplained` が負にならない）。sent はモードキーを含む（S14 のモードキーが参照に届かなければ取りこぼしとして数えられ、余りの数を増やさない）。印の打鍵の数は計画の block 行の `marker` の長さ（oracle の `marker` 行ではない）。`delivery.py` は区間の数と `n_unexplained_beyond_markers`（印を引いた余り・0 未満は 0）を両側で出すだけで、上限と判定は持たない（判断 115 の 2 を守る）。観測の側の区間の数は記述。
2. **上限と判定の置き場所**: `pipeline.py` の `RUNNER_KANA_PRESSES_PER_BLOCK`（**暫定 1**・凍結の前に Mac のパイロットで 0 か 1 に決める・判断 117 の Z3 (3)）。最初の区間は k、最後の区間は印の数だけ（その後に `focus_cmd` が走らない）、ほかは印＋k。当たる run は `InputError`（exit 2）で、メッセージは cell の label と区間の block_id だけ。`e1_delivery.json` に `abort_rule`（k・pre_ms 20・tail_ms 300）を記録。事前登録の文は k を記号のまま置き、「0 か 1・凍結の前にパイロットで決める」と書いた。⚠️ `focus_cmd`（`cell.example.json`）は前面化の後に 0.7 s 待ってからかなキーを押すので、かなキーは最後の試行の窓（+300 ms）の外に落ちる見込みが高いが、区間で数えるので窓の位置には依らない。
3. **預けない範囲**: §3.4 の「預けない」を、外からの入力の場合だけでなく、計画の SHA-256 の違い・`delivery.py` の exit 2 を含む「完了した run を中止に数えた場合すべて」に広げた（どれも解析しない run で、参照のログは key code を持つ）。`data.md` 手順 1 も同じ。
4. **計画の SHA-256 の照合**（A3）: コードには足していない（登録の 2 つの値は事前登録 §2.4 の文にしか無く、`config.json` に足すと凍結のハッシュの対象と形式が変わる）。`data.md` の Run checks の表の欄で手で照合する。
5. **錨**（minor 1・作業用エージェント B）: 右に揃えた結果、ブロックのあいだに足された打鍵（印の直前の矢印を含む）でもブロックを失わなくなった（新しい性質・selftest で守る）。既存の対照 3 つ（5 つ続く nav は錨でない・印の直前に足した矢印でそのブロックを失う、など）は左端の条件を前提にしていたので、新しい期待に直した。保証の文は「selftest の場合で確かめた・一般には証明していない」と書いた（§6.8・README・docstring）。ブロックの最初の試行が矢印で始まる手順は無い（作業用エージェントが両方の手順書で確かめた）。
6. **空の層**（minor 2・作業用エージェント C）: `per_trial` のすべての行に `status`（`ok` / `no_trial`）と層ごとの `trials_not_used` を持たせた。
7. **`plan_figures`**（minor 5・Z2・作業用エージェント C）: `--from-plan` の出力だけに足した（`spec_predict/2` の形式の文字列は変えない。`match.parse_prediction` は未知の欄を読まない）。テキストの区切りは `l2.text_layout` と同じ規則を自前で書き、selftest で l2 と照合。本番の 2 計画（SHA-256 一致）で、§3.3 の 2.4〜3.1 / 2.5〜3.4・33〜39 / 30〜37 ブロック・主の範囲の最大 3.05（S14 mid）/ 3.22（S15 mid）と、§6.7 の k の平均・slow の k ≤ 3（30 / 126・27 / 117）・k = 8（4・0）・k = 0 なし、がすべて出力から再現された。k の数は凍結の前に計算した値なので §6.7 に開示し、§3.1 に再現の手段（`plan_figures`）を書いた。
8. **文の選択**: §6.6 の仕様との一致は `pred_obs` の `over_limit` の層ごとの検出の数（予測の行・観測の行・対・取りこぼし・偽検出）で読む、と書いた（新しい統計は足さない）。§6.4 の打ち切りの向きは「平均の変換時間と時間の割合は下がる・件数は打ち切りの後の英字・数字が新しいセッションを開くのでどちらにも・放棄の率は打ち切られたセッションが確定でも放棄でもありうるのでどちらにも」。§7 に「中止の規則は打鍵の数を数え、キーを比べない（置き換わった打鍵は検出しない）」の項を足し、「judges one phrase at a time」の項を §6.8 の参照に縮めた。§5 に「pipeline は §3.4 の規則に当たる run を拒む」を足した。§3.1 の OFF の carried out は「186（すべて S6・185 が後の試行へ続き、残る 1 つは試行の外の打鍵で打ち切られる）」とメインが予測の出力で数えた。`pilot-macos.md` は時点を「before the freeze」にしただけ（基準の中身と、観測の余分な行の扱いを本計測と揃えること〔監査役 3-E〕は Mac の作業）。
9. **確認**: `kit/check.sh` 29 本緑・`run.sh --synthetic` 2 回で 4 ファイルともバイト一致・`_style_check.py` 違反 0 件・`check_citations.py` 違反なし・`--check-prereg` exit 3・§9 の SHA-256 の表の 5 ファイルは今の値と一致・本文の「section N」はすべて実在・本文 13,422 語（round 4 の測り方）。変異: 作業用エージェントの自己申告は A 6 本・B 3 本・C 7 本ですべて赤。メインの抜き取り 3 本（`closed_set` の左端の条件を戻す → 14 件赤・`delivery` の印の数を無視 → 5 件赤・`pipeline` の最初の区間の余裕を 0 → 1 case 赤）もすべて赤。⚠️ A の変異 (iii)（区間の境界を逆にする）は pipeline の selftest では赤にならない（合成の run に `block_begin` ちょうどの行が無い）。`delivery.py` の selftest が守る。

---

★ 以下 2026-10-02（G-GEAR・round 4 の直しの後の作業中の点検〔code-reviewer ∥ security-checker・`b1c3f213..4bd6cacd`〕を受けて）。

## 判断 119: runner が中止した run にも §3.4 の点検を当てて `--pack` で強制し、S15 以外の焦点の喪失を中止に足す（2026-10-02・G-GEAR・研究者の選択・security-checker の HIGH と MEDIUM 2 件・round 4 の監査役 3-E）

- **中止した run の預け方**（security HIGH・MEDIUM 1・裏取りは真: `data.md` 手順 2「A log that an aborted run recorded with a null hash need not exist」は runner が中止した run を預ける前提。`pipeline.py` の `deposit_check_files` は中止した run では content-free の検査も飛ばし、§3.4 の規則は `analyse` の中にしか無い〔`data.md` は預けて取り出した後に run の一覧を足す＝規則が働くのは預けた後〕。参照のログは受けた key-down のキーコードを持ち、runner の中止〔Ctrl+C・前面の確認の失敗〕は人の介入と相関する）→ **研究者の選択: `--pack` で全 run に強制**（推奨）。`--pack` / `--check-deposit` が、完了・中止を問わず §3.4 の規則を当て、当たる run と点検できない run（delivery が拒む・計画や oracle が無い・参照のログの無い観測のログ）を梱包しない。§3.4 と `data.md` も「runner が中止した run にも当てる」に。採らなかった: 文だけ直す・中止した run は一切預けない。
- **観測のログの人の打鍵**（security MEDIUM 2・監査役 3-E と同じ根・裏取りは真: 観測器は機械のすべての打鍵の区分と時刻を記録し、預ける。人が参照以外のアプリに打つと参照の点検には掛からない。事前登録 §2.1 は「no person's typing is part of the data」）→ **研究者の選択: 焦点の喪失を中止に足す**（推奨）。参照が S15 の計画した切り替え（S15 の試行の窓の中で始まって戻る喪失）以外で焦点を失った run を §3.4 で中止に数え、預けない。参照以外へ打つには参照の焦点が外れるので、その道を閉じる。代償: 通知などで焦点を失っても約 12 時間のやり直し。§6.2 の「焦点の喪失は除外しない」を改めた。⚠️ Mac のパイロットで S15 以外の喪失が 0 回だったかを確かめ、0 でなければ研究者に戻す（§3.1 に書いた）。採らなかった: 残るリスクとして開示するだけ・Mac のパイロットの数を見てから決める。

## 判断 120: 作業中の点検の指摘への直しの実装上の選択（2026-10-02・G-GEAR・メインの選択・研究者が覆せる）

点検の指摘はメインが一次で裏取りした（security: HIGH 1・MEDIUM 2・LOW 3 はすべて真。code-reviewer: MEDIUM 4・LOW 8 は真。ただし M2 の「最後でない区間なら印＋k が吸収する」は**偽**〔かなキーが次の区間に滑ると、その区間は自分のかなキーと次のブロックのかなキーの 2 つを持ち、上限を 1 超える〕。範囲外の気づき「§3.2 は前面の確認の後にかなを押すと書くが runner は逆」も**偽**〔`focus_cmd` 自身が前面を確かめてからかなを押す: `cell.example.json` の osascript〕）。Sonnet の作業用エージェント D が `delivery.py`・`pipeline.py` を実装し、メインが差分を読んで 1 点直した。

1. **モードキーの版**（code-reviewer M1・真: `ime_on` はかなキーと同じキーコード 104〔`backend_macos.py:231`〕。k = 0 ならモードキーも参照に届かない見込みが高く、`all_presses` の数え方では S14 の各試行に 1〜2 打鍵の余裕ができ、外からの打鍵が隠れる）: `delivery.py` の区間を `all_presses` と `excluding_mode_keys` の 2 版にし、`pipeline.py` の暫定の定数 `REFERENCE_RECEIVES_MODE_KEYS = True` が版を選ぶ。凍結の前に Mac のパイロットの S14 の reach で決める（§3.1・§3.4 に書いた）。
2. **かなキーの滑り**（M2）: 起きても中止になる安全側なので規則は変えず、`delivery.py` に区間ごとの `ms_from_last_row_to_next_block` を記述として出し、パイロットの最小値を §3.1 に報告する（§3.4 に前提と、滑っても外からの打鍵は通らないことを書いた）。runner を変えて `focus_cmd` の前に oracle の行を書く案は採らない（判断 116 で runner を変えない選択）。
3. **block_id は整数だけ**（security LOW・L3）: 計画の検証器（`emit.py`・`generate_plan.py`）と揃えた。
4. **表に写す値**（L7）: 各版に `max_beyond_markers_before_last_block` と `beyond_markers_last_block` を出し、`data.md` の表の列をそれに合わせた（手で by_segment から拾わない）。
5. **block_begin の無い oracle**（L1）: 1 区間を「最初のブロックの前」として余裕 k（最後のブロックの区間だけが余裕 0）。
6. **selftest**（M3・M4・L4・L5）: k = 0 と 1 の両方で回す・手で作った delivery の報告で上限ちょうど／+1 を直接確かめる・`inside` の絞り込みを守る対照・古いコメントを直した。
7. **焦点の規則と預ける前の強制**（判断 119）: `reference_abort_reasons` が 2 つの規則の理由をまとめ（値を出さない）、`analyse` と `deposit_check_files`（`--check-deposit`・`--pack`）が使う。`delivery.py` は `n_loss_intervals_planned`（S15 の試行の窓の中で始まって戻る喪失）と `n_loss_intervals_unplanned` を出す。⚠️ メインの直し: 作業用エージェントの実装は「参照のログが無ければ点検の対象なし」だったが、観測のログだけがある run は焦点の喪失を確かめられないので「点検できない」に変え、selftest を 1 件足した（変異で赤を確かめた）。参照も観測も無い中止の run だけが点検なしで通る（§3.4・`data.md` も同じ）。
8. **文**: §3.4 を「計画の SHA-256／外からの打鍵／焦点の喪失」の 3 つの理由で組み直し、盲点を「手順の打鍵（印・かな）が届かないと同じ区間の外からの打鍵が隠れる」まで広げた（security LOW 1）。§2.1 に「§3.4 の規則が人の打鍵のしるしのある run を外す（捕まえないものは §7）」。§6.2 の焦点の喪失の項を「中止に数える・解析する run には無い」に。§7 の盲点の項に、焦点を動かさずにシステムが消費するショートカットはどちらの規則にも掛からない、を足した。§3.4 の文の「試行に割り当てた key-down」を「そのうち区間の中にあるもの」に（L6）。
9. **採らなかったもの**: security LOW 3（定数と §3.1 の k の食い違いの自動検査）は足さない。Mac の作業で定数と文を同じコミットで決める（引き継ぎに書く）。L2（`trial_end` の無い試行の打鍵が「説明されない」に数えられる）はメッセージの言い方を「測った試行と手順で説明されない」に直すだけにした（runner が中止した run では安全側に働く）。L8（`max_layer` の同値）は層の順で最初のものに。
10. **確認**: `kit/check.sh` 29 本緑・`run.sh --synthetic` 2 回で 4 ファイルともバイト一致・`_style_check.py` 違反 0 件・`check_citations.py` 違反なし・`--check-prereg` exit 3・節の参照はすべて実在・本文 13,902 語。変異: 作業用エージェント D の自己申告 6 本すべて赤・メインの抜き取り 1 本（観測だけの run の分岐を外す）赤。

---

★ 以下 2026-10-02（Mac・凍結の前の測定機での作業・判断 113 の Y4 ＋ 判断 117 の Z3 ＋ 判断 119）。パイロットの観測は `keys-out`（`obs.keys.jsonl`・key 行だけ）だけを使い、封印は開けていない。参照のログは `delivery.py` が key_down・focus の時刻だけを読み、キーコードは表示も転記もしていない。

## 判断 121: 焦点の規則は「計画外の喪失の中に観測の打鍵があるとき」だけ中止にする（2026-10-02・Mac・研究者の選択・判断 119 の焦点の規則の改訂）

- **所見**（パイロットの数）: `pilot2-off` で、参照が S15 以外で焦点を 1 回失った。試行 t00090（S1・fast・ブロック 4）の考える時間の中、Space を送ってから 2.7 秒後に **31 ms**。前後 1 秒以上キーの送出は無く、喪失の間とその前後 3 秒に観測の key 行は 0・参照の key_down も 0。他の 2 本と、同じ点検を当てた `pilot-1`・`verify-1`・`verify-s5` では 0 回（6 本で約 87 分）。この頻度だと 1 セル約 12 時間で平均約 8 回になり、判断 119 の規則（S15 以外の喪失はすべて中止）ではほぼ全セルが中止 → 3 回で「測定できず」になりうる（観測は 1 回なので頻度の幅は大きい）。
- **研究者の選択: 喪失中の打鍵で中止**（推奨）。S15 以外の喪失の区間（前後に余裕）に観測の key 行が 1 つでもあれば中止。理由: 判断 119 の根拠（人が他のアプリに打つには参照の焦点が外れ、観測は機械のすべての打鍵を記録する）を、人の打鍵がログに入る場合だけに絞る。打鍵の無い喪失はどちらのログにも人の打鍵を入れない。焦点を移すショートカットも余裕で拾う。採らなかった: 短い喪失を閾値で許す（値の根拠が弱い）・今の規則のまま（多くのセルが中止）・規則を外して §7 に開示（判断 119 で採らなかった案）。

## 判断 122: Mac の作業の実装上の選択と、決めた定数（2026-10-02・Mac・メインの選択・研究者が覆せる）

1. **k = 0**（`RUNNER_KANA_PRESSES_PER_BLOCK`）: 3 本・15 回のかなキーがすべて参照に key_down を残さない（最初の区間は 0 行・各ブロックの区間の「説明されない数」は印の 3 ちょうど・両版）。同じ点検を当てた 6 本・27 回でも同じ。
2. **`REFERENCE_RECEIVES_MODE_KEYS = False`**（版は `excluding_mode_keys`）: 参照の到達は `all_presses` が 4,072 / 4,090・3,972 / 3,990・1,174 / 1,180、`excluding_mode_keys` は 3 本とも 100%。差の 18・18・6 は S14 の試行の数 × 2 とちょうど一致 → 2 つのキーとも届かない（片方だけ届く場合ではないので研究者に問わない・引き継ぎ §2 (b) のとおり）。
3. **滑り**: 区間の最後の行から次のブロックまでの最小は 1,582 ms（`pilot2-on`）。k = 0 なので、かなキーが key_down を残せば落ちた区間によらず中止になる（§3.4 の前提の文を簡単にした）。
4. **区間の規則**: k = 0・`excluding_mode_keys`・印 3 打鍵で、3 本とも印を引いた余りの最大は 0（当たらない）。
5. **合わせ直しの診断**: scratchpad の使い捨てのスクリプト（repo に入れない）で `read_obs(keys-out)`・`read_plan`・`align_plan(..., markers_in_obs=True)` だけを呼んだ。3 本とも全ブロック採点（15 / 15 ブロック・282 試行・割り当てのない打鍵 0）。`keys-out` の ime_shadow 行は 0（読み取り側で確認）。欠陥は無くコードは変えていない。⚠️ ログに欠けも足しも無いので、再同期は試していない（§3.1 にそう書いた）。
6. **焦点の規則の実装**（判断 121）: `delivery.py` に定数 `FOCUS_MARGIN_MS = 500` と、計画外の喪失の区間（focus_out の 500 ms 前から focus_in の 500 ms 後まで・戻らない喪失はログの終わりまで）に入る観測の key 行の数 `n_presses_in_unplanned_losses`（2 つの区間に入る打鍵は 1 回）と、打鍵を含む喪失の数 `n_loss_intervals_unplanned_with_presses` を出させ、`params.focus_margin_ms` に記録。`pipeline.py` の `reference_abort_reasons` は後者 > 0 で中止。`abort_rule` の `unplanned_focus_loss_aborts` を `unplanned_focus_loss_with_presses_aborts` と `focus_margin_ms` に置き換えた。余裕の 500 ms はメインの選択（時計の差 22 ms・観測の行の収集遅れ約 100 ms より十分大きく、パイロットの喪失〔直前の行から 2.67 秒〕は通る）。観測のログが無い run は打鍵 0 として扱う（既存の「観測のログが無ければ空」と同じ・参照のログが無く観測のログだけある run は今までどおり点検できない）。命令行（§3.4）は変えていない（余裕は引数にせず定数）。
7. **selftest と変異**: `delivery.py` に 7 件（余裕のちょうど端・端 +1・戻らない喪失・S15 の切り替えの打鍵は数えない・2 つの余裕に入る打鍵・params）、`pipeline.py` の `_case_section34_enforcement` に「打鍵の無い計画外の喪失は分析も預ける前の点検も通る」。変異 4 本（余裕を外す・計画した喪失も数える・戻らない喪失を focus_out で切る・pipeline を旧規則に戻す）すべて赤。
8. **文**: §3.1 の 2 つの項目に結果（合わせ直しの割合・(a)〜(e) の数・焦点の所見と規則を変えた理由）。§3.4 の 3 つ目の理由・k と版の文（決めた値）・焦点の段落（余裕と、打鍵の無い喪失は中止にしないこと）・記録する数・盲点の「かなキー」を外した（k = 0 では隠せない）。§6.2 の焦点の項（解析する run は打鍵の無い喪失だけを持ちうる・除外しない）。§7 に「キーを押さずに焦点を移して戻る人は捕まらないが、ログに打鍵を入れない」。`data.md` の Run checks の前置き（k = 0・`excluding_mode_keys`・上限は両方 0）・表の列・手順 1。`pilot-macos.md` の Raw logs を本計測と揃えた基準に置き換えた（監査役 3-E の「every key row … matched」を削除・観測の余分な行は止めない・封印したセッション行は凍結と本計測の後に預けるためにだけ開ける・`--check-deposit` は開けた後に・パイロットの 7 本は §3.4 の規則に当たらない）。§3.4 の 2 つの段落は折り返し直した（中身の変更は上のとおり）。
9. **確認**（Mac・Python 3.14.4）: `kit/check.sh` 29 本緑・`run.sh --synthetic` 2 回で 4 ファイルともバイト一致（`abort_rule` に k = 0・False・500 が記録される）・`_style_check.py` 違反 0 件・`check_citations.py` 違反なし・`--check-prereg` exit 3・事前登録・`pilot-macos.md`・`data.md` の節の参照はすべて実在。§9 の SHA-256 の表の 5 ファイルは変えていない。⚠️ 本文の語数は `round-4/tmp/measure.py` が Mac の Python で SyntaxError（Windows 向けの書き方と思われる）で測れていない（G-GEAR で測る）。定数と文の照合は目で（`pipeline.py` の 0 / False ↔ §3.1・§3.4・`data.md`、`FOCUS_MARGIN_MS` 500 ↔ §3.4）。

---

★ 以下 2026-10-02（G-GEAR・Mac の作業を取り込んで確かめたとき）。G-GEAR（Python 3.11.9）でも `kit/check.sh` 29 本緑・`run.sh --synthetic` 2 回でバイト一致（`abort_rule` は k = 0・False・500）・文の検査 0 件・引用の違反なし・`--check-prereg` exit 3。本文 14,369 語（`round-4/tmp/measure.py`・Mac の作業の後）。定数（`pipeline.py` の 0・False、`delivery.py` の 500）と §3.1・§3.4・`data.md`・`pilot-macos.md` の文は一致。§3.1 の数は内部で整合（15 ブロック＝6＋6＋3・282 試行・S14 の未到達 18・18・6 は S14 の試行の数 × 2）。

## 判断 123: 焦点の規則は、喪失の区間の観測の key 行が実行器の送った打鍵を超えたときだけ中止にする（2026-10-02・G-GEAR・研究者の選択・判断 121 の改訂）

- **所見**（メインが計画から計算）: 判断 121 の規則（計画外の喪失の前後 500 ms に観測の key 行が 1 つでもあれば中止）は、実行器が送った打鍵の行も数える。喪失の間も実行器は打鍵を送り、観測は機械のすべての打鍵を記録するので、打っている最中に喪失が起きると人がいなくても中止になる。本番の 2 計画を `spec_predict.oracle_from_plan` の時刻で数えると、run の時間の **ON 78.1%・OFF 77.0%** が「送った打鍵〔試行の押下・印〕から 500 ms 以内（31 ms の喪失として）」に当たる（余裕 100 ms でも 45.9%・45.0%）。パイロットの率（1 回／約 87 分・ポアソンの 95% で 12 時間あたり約 0.2〜46 回と幅は大きい）で 1 セル約 8 回なら、喪失の時刻が打鍵と無関係であるかぎり、ほぼすべての run が中止になる。パイロットの 1 回は考える時間の中にあった。
- **研究者の選択: 送った打鍵を差し引く**（推奨）。計画外の喪失の区間（前後 500 ms・重なる区間はまとめる）ごとに、観測の key 行の数が、実行器が送って観測が記録する打鍵（試行の押下〔擬似キーとモードキーを除く〕と印の打鍵）の数を超えたら中止。送った打鍵は区間の 100 ms 前から数える（区間の直前に送られて行が区間に落ちる打鍵を差し引くため）。理由: 判断 121 の狙い（人の打鍵が入りうる run だけを外す）に合う。人の打鍵は送った打鍵を超える行として現れる。代償: 打っている最中の喪失を含む run も解析に残り、喪失中に送った打鍵は参照に届かず、その試行は食い違いとして数えられる（delivery と検出の結果の focus_loss が数えて報告する。§6.2）。観測が区間で 1 打鍵を取りこぼすと人の打鍵が 1 つ隠れ、観測器自身の重複行が区間に落ちると人がいなくても中止になる（§7）。採らなかった: 今の規則のまま（多くの run が中止になりうる）・Mac で喪失の率を測り直してから決める。
- 凍結の前に計算した 78% は §3.1 に開示した（最初の版を改めた理由として）。

## 判断 124: 判断 123 の実装上の選択（2026-10-02・G-GEAR・メインの選択・研究者が覆せる）

1. **数え方**（Sonnet の作業用エージェント E が `delivery.py`・`pipeline.py` を実装・メインが差分を読み、抜き取りの変異 1 本〔pipeline の `> 0` を `> 1`〕で赤を確かめた）: 計画外の喪失の区間を前後 `FOCUS_MARGIN_MS`（500）広げ、重なる・接する区間を 1 つにまとめる（`n_unplanned_loss_spans`）。まとめた区間 [a, b] ごとに、観測の key 行（press = true）の数と、観測が記録すると見込む送った打鍵（`sent` の down で擬似キーでもモードキーでもない押下〔measured / incomplete を問わず〕＋ oracle の `marker` 行）のうち送出の壁時計が [a − `OBS_SEND_DELAY_MS`, b] にあるものの数を比べ、超えた分を `n_unexplained` とする。区間の数（`n_unplanned_loss_spans_with_unexplained_presses`）と和（`n_presses_unexplained_in_unplanned_losses`）を出し、pipeline は前者 > 0 で中止。判断 121 の 2 つの数（`n_loss_intervals_unplanned_with_presses`・`n_presses_in_unplanned_losses`）は記述として残した（送った打鍵を含むことを docstring に書いた）。
2. **`OBS_SEND_DELAY_MS = 100`**: 送出から観測の行までの遅れの見込み（区間の直前に送られて行が区間に落ちる打鍵を差し引くため）。メインの選択。代償は、区間の終わりの直前 100 ms に送られて行が区間の外に落ちる打鍵の分だけ人の打鍵が隠れうること（§7）。パイロットの観測の遅れの実測は G-GEAR に無い（Mac の delivery の報告の `observation.timing.delay_ms` で確かめられる・round 5 で問われたら Mac の作業）。
3. **印を送った打鍵に数える**: 本番の印は矢印で観測が記録する。F13〜F19 の印（`pilot-1`）は観測に行が無いので、その場合は送った打鍵を多めに数える（人の打鍵が隠れる側）。本番には当たらない。
4. **名前**: `abort_rule` の `unplanned_focus_loss_with_presses_aborts` を `unplanned_focus_loss_with_unexplained_presses_aborts` に、`obs_send_delay_ms` を足した。`data.md` の表の列は `n_unplanned_loss_spans_with_unexplained_presses`。
5. **文**: §3.4 の 3 つ目の理由と焦点の段落（区間・まとめ方・送った打鍵の数え方・100 ms・打っている最中の喪失も打鍵の無い喪失もそれだけでは中止にしない）・記録する数・「観測の余分な行は中止の理由にしない」を「喪失の外では」に。§3.1 に最初の版を改めた理由（78%）。§6.2 の焦点の項（解析する run に打っている最中の喪失がありうる・その試行は食い違いとして数え、focus_loss で報告し、除外しない）。§7 の盲点（取りこぼし・終わりの直前 100 ms・観測器の重複行）。`data.md`（表の列・手順 1・喪失の外では観測の余分な行は止めない）。`pilot-macos.md`（預ける基準の文）。パイロットの 7 本は新しい規則でも当たらない（唯一の計画外の喪失の前後 3 秒に観測の key 行が 0）。
6. **確認**（G-GEAR）: `kit/check.sh` 29 本緑・`run.sh --synthetic` 2 回で 4 ファイルともバイト一致・`_style_check.py` 0 件・`check_citations.py` 違反なし・`--check-prereg` exit 3・節の参照はすべて実在・本文 14,665 語。変異: 作業用エージェント E の自己申告 6 本すべて赤・メインの抜き取り 1 本赤。

---

★ 以下 2026-10-02（G-GEAR・attack-me round 5 の後）。round 5 の記録は `attack-me/prereg-ime-macos/round-5/`（判定は minor revision・R1 minor・R2 minor・R3 minor・fatal 0・major 0・捏造 0・注入 0）。

## 判断 125: 焦点の規則は観測の行と送った打鍵を 1 つずつ対応させ、S15 の計画した切り替えにも当てる。計画の SHA-256 は解析でコードが照合する。感度は §7 に開示する。直す一覧を全部承認し、round 6 は回さない（2026-10-02・G-GEAR・研究者の選択・round 5 の Y1〜Y3・判断 119〜124 の焦点の規則と判断 118 の 4 の改訂）

- **Y1 焦点の規則の穴**（R1 M-1・m-2・R2 1・2・3・R3 3・nit・監査役 1-α・3-δ・裏取りは真）: (i) S15 の計画した切り替えの喪失を区間から丸ごと外す（`delivery.py` の `spans` は計画外の喪失だけ・selftest がそれを期待値に固定）ので、その間の人の打鍵はどちらの規則にも掛からない。(ii) 送った打鍵を区間の 100 ms 前から数え、行は区間の中だけ数えるので、区間の頭の 100 ms に送られて行が区間より前に落ちた打鍵の数だけ人の打鍵が隠れる（§7 は終わりの側だけ書いていた）。(iii) 100 ms はメインの選択で実測ではなく、パイロットの時計の表ではブロック 0 の「観測 − 実行器」が 95 ms・86 ms（ブロック 1〜5 は 0〜3 ms）。S15 の切り替えは `osascript` の activate でキーを送らない（`backend_macos.py`）ので、数える規則を計画した喪失に当てても人がいなければ当たらない。→ **研究者の選択: コードで閉じる**（推奨）。数える規則をすべての喪失（S15 の計画した切り替えを含む）に当て、観測の行と送った打鍵を時刻の順に 1 つずつ対応させ、対応の無い行を区間の中で数える。対応の幅は余裕を取る（86〜95 ms を十分に超える値）。理由: 頭と終わりの両方の穴が消え、実測していない 100 ms への依存も小さくなる。採らなかった: S15 だけコードで閉じて 100 ms は開示・両方とも文で開示するだけ。
- **Y2 計画の SHA-256**（R1 新-2・R2 nit 9・R3 4・裏取りは真。R3 の「判断 118 の 4 の理由は `pipeline.py` の定数に置く道を塞がない」も真）→ **研究者の選択: 解析ではコードで照合**（推奨）。登録の 2 つの値を `pipeline.py` の定数に置き、凍結した事前登録で解析を回すときに、計画の SHA-256 がどちらでもない run を拒む。預ける側はパイロットの run（別の計画）も通るので手の照合のままとし、§3.4 の文をそれに合わせて狭める。採らなかった: 文を狭めるだけ。判断 118 の 4 を改める。
- **Y3 規則の感度**（R1 m-3・裏取りは真: 規則が人の打鍵を捕まえることは selftest の合成の場合でしか確かめていない）→ **研究者の選択: §7 に開示する**（推奨）。参照から key window を奪わずに文字を受ける入力欄への打鍵は捕まらないかもしれない、と書く。理由: 本計測は無人の夜間で規則は安全網。Mac への往復と、意図して人の打鍵を含むログを作ることを避ける。採らなかった: 凍結の前に Mac で短い run を行い意図して打つ。
- **直す一覧**: round 5 の `verdict.md` §3 の minor 7 件・nit 14 件を**全部承認**（推奨）。コードを伴うのは minor 1（content-free の検査を中止した run にも当てる）・minor 5（78% を `plan_figures` で再現）と、Y1・Y2。
- **round 6**: **回さない**（推奨）。3 人とも minor で「再査読は要らない」とした。直しは確認の後、完了時レビュー（code-reviewer ∥ security-checker ∥ Codex 2 巡）で点検してから PR へ。

---

★ 以下 2026-10-02（G-GEAR・round 5 の直しの実装）。判断 125 を実体にするときに、研究者に問わずに決めたもの。凍結の前なら変えられる。

## 判断 126: round 5 の直しの実装上の選択（2026-10-02・G-GEAR・メインの選択・研究者が覆せる）

1. **焦点の規則の対応づけ**（判断 125 の Y1・Sonnet の作業用エージェント A が `delivery.py` を実装・メインが差分を読み、抜き取りの変異 1 本〔期限切れの送出を捨てる処理を外す → 13 件赤〕で確かめた）: ログ全体で 1 回、行を時刻の順に見て、送出が行の 300 ms 前から 20 ms 後までにある、まだ使われていない最も早い送出を 1 つ取る（同じ幅の窓では貪欲が最適で、対応の無い行を必要より多く残さない）。区間（すべての喪失を前後 500 ms 広げ、重なる・接する区間はまとめる）に入る対応の無い行が 1 つでもあれば中止。定数は `OBS_MATCH_BEFORE_MS = 20`（時計の許容・既定の pre_ms と同じ）と `OBS_MATCH_AFTER_MS = 300`（パイロットのブロック 0 の 86〜95 ms を十分に超える・既定の tail_ms と同じ）。`OBS_SEND_DELAY_MS` は消した。出力の名前は `n_loss_spans`・`n_loss_spans_with_unexplained_presses`・`n_presses_unexplained_in_losses`（`unplanned` を外した）。判断 121 の記述の数（`n_loss_intervals_unplanned_with_presses`・`n_presses_in_unplanned_losses`）と、試行の一覧から S15 の計画した切り替えを外す扱いは残した。盲点は §7 と docstring に 3 つ（取りこぼした行の送出が人の打鍵を 1 つ取りうる・窓の外の遅れ・観測器の重複行）。
2. **計画の SHA-256**（判断 125 の Y2・作業用エージェント B が `pipeline.py` を実装・メインが差分を読み、抜き取りの変異 1 本〔照合に oracle のハッシュを使う → 2 / 12 赤〕で確かめた）: `REGISTERED_PLAN_SHA256` を定数にし、実データ（合成でない）の解析で、中止でない run の計画のログの SHA-256（manifest と照合済みの値）が 2 つのどちらでもなければ exit 2。合成の run・`--pack`・`--check-deposit` には当てない（パイロットの run は別の計画で預ける）。`abort_rule` に `registered_plan_sha256` を足し、鍵の名前を `focus_loss_with_unexplained_presses_aborts`・`obs_match_before_ms`・`obs_match_after_ms` にした。selftest は `_set_constant` で定数を合成の計画に向け、`_case_run_sh` は一時の木に写した `pipeline.py` の定数の行を書き換える。
3. **中止した run の content-free の検査**（minor 1）: `deposit_check_files` が中止した run にも当てる。ハッシュが null で無いログは通し、最後の行が切れて検証できないログは拒む（預けない・安全側）。試行の途中で中止した run が打鍵の規則で必ず拒まれることは、コードは変えず §3.4 と `data.md` に書いた（判断 120 の 9 の L2 のまま）。
4. **78% の再現**（minor 5・作業用エージェント C が `spec_predict.py` を実装）: `plan_figures` に `focus_rule_first_version`（31 ms の喪失を前後 100 / 500 ms 広げた区間に送出〔擬似キー以外の押下・モードキーを含む〕か印の打鍵が入る時間の割合・oracle の最初の行から最後の行まで）。本番の 2 計画で 0.781061 / 0.769857（500 ms）・0.458774 / 0.450085（100 ms）＝開示した 78.1・77.0・45.9・45.0 と一致。既存の出力はバイト一致。メインが scratchpad の試作で定義を先に決めた（モードキーを含め印を足すと一致する）。
5. **文**: §3.4 を 4 つの理由を 1 か所に並べて書き直した（焦点の規則・余裕と窓は設計の選択・`idle` の観測のログは預けない・預けない理由を理由ごとに・試行の途中で中止した run・`--pack` は計画を照合しない）。§3.1 の喪失の数を記録から導ける形（余裕 500 ms で広げた区間に key 行 0・直前の行は最後に送った打鍵・その後 1 秒以上送出なし）に直し、頻度の幅・最終形の規則はパイロットのログに当てていないこと（預けるときに `--check-deposit` が当てる）・合わせ直しの診断のコードの版・`plan_figures` の 78% を足した。§6.7 の記号 k を r に。§7 の停止の規則の項を書き直し、感度は selftest でしか確かめていないこと（判断 125 の Y3）と「参照が自分で焦点を失う」項を足した。`data.md`・`pilot-macos.md` は規則を言い直さず §3.4・§7 を参照する形に（`pilot-macos.md` の「short run」は `short-1` と名指し、中断した試走は「ほかの runner の run」として預けるときの基準に）。`kit/run/README.md` に `--pack`、`kit/e3/README.md` に `idle` の観測のログを預けないこと。本文は 15,265 語（直しの前 14,665 語・+4%。R2 の分量の指摘には、言い直しを参照に替えたぶんだけ応えた）。
6. **確認**（G-GEAR・Python 3.11.9）: `kit/check.sh` 29 本緑・`run.sh --synthetic` 2 回で 4 ファイルともバイト一致（`abort_rule` は 500・20・300・k = 0・False・登録の 2 計画）・`run.sh`（実データ・未凍結）exit 3・`_style_check.py` 0 件・`check_citations.py` 違反なし・節の参照はすべて実在・§9 の 5 ファイルは変わらない。変異: 作業用エージェントの自己申告 A 8 本・B 7 本・C 7 本すべて赤、メインの抜き取り 2 本赤。定数と文の照合は目で（`delivery.py` の 500・20・300 ↔ §3.4・§7、`pipeline.py` の 0・False・20・300・2 計画 ↔ §3.4・§2.4、`plan_figures` ↔ §3.1）。

---

★ 以下 2026-10-02（G-GEAR・完了時レビューの後）。code-reviewer（CRITICAL・HIGH 0・MEDIUM 1・LOW 6）∥ security-checker（CRITICAL・HIGH 0・MEDIUM 1・LOW 4・範囲外 1）は `965486554..f02cb49a` の公開物 24 ファイル、Codex 1 巡目（P1 1・P2 2）は研究者の選択で `b1c3f213..HEAD` の `kit/` だけ（差分 8,773 行・約 635 KB で 2 巡は 1 日の予算を超えるため）。指摘はメインが一次で裏取りした（すべて真。Codex P1 は security LOW と同じ根）。

## 判断 127: 参照が焦点を得る前と止めた後も喪失として扱い、ずれの連鎖を数える終わりを延ばし、計画をセルと対応させ、残りの 12 件を直す（2026-10-02・G-GEAR・研究者の選択・完了時レビュー）

- **起動の前と止めた後**（security MEDIUM・裏取りは真: 観測器は参照より先に起動し〔`run_cell.py:556-557`〕、止めるときは参照が先〔`_stop_children`〕。焦点の行が無いと喪失は 0 件〔`_loss_intervals([], [3000]) == []`〕。参照が最初に焦点を得る前と止めた後の観測の打鍵は、どの規則にも掛からず預けられる。参照が一度も焦点を得ずに中止した run も通る）→ **研究者の選択: 喪失として扱う**（推奨）。ログの始まりから最初の focus_in まで（焦点の行が無ければログ全体）と、参照のログの最後の行より後を、焦点の規則の区間に加える。実行器はブロックの前に観測されるキーを送らない（かなキーは観測しない）ので、人がいなければ当たらない。採らなかった: §7 に開示するだけ。
- **ずれの連鎖**（security LOW・Codex P1・仕組みは真: 対応はログ全体で時刻の順なので、送出とその行の間に人の打鍵が入ると、対応の無い行が後ろの実行器の行へずれ、送出が詰まっていると区間の外へ運ばれる。遅れが大きいとき〔パイロットでは run の最初のブロックの 86〜95 ms〕だけ起きる。security の模擬: fast・遅れ 90 ms で約 0.1%・150 ms で約 49%）→ **研究者の選択: 数える終わりを延ばす**（推奨）。区間ごとに、対応の無い行を数える終わりを、送出の間隔が 320 ms（窓の幅）以下で続く並びの先 ＋ 300 ms まで延ばす（ずれはその隙間を越えられない）。採らなかった: §7 に開示するだけ。代償: 延ばした所に観測器の重複行が落ちると誤って中止（パイロットで重複は 0）。
- **計画とセル**（code-reviewer LOW・真: 解析の照合は「2 つのどちらか」だけで、ON のセルが OFF の計画でも、2 つのセルが同じ計画でも通る）→ **研究者の選択: セルと対応させる**（推奨）。`run.json` の `cell.ime_settings.live_conversion`（on / off）と計画の SHA-256 を対応させ、合わない run を実データの解析で拒む。判断 126 の 2 を改める。
- **残りの 12 件**（研究者の選択: 全部直す・推奨）: ① 同じミリ秒に focus_in → focus_out が並ぶと戻らない喪失が消える（code-reviewer MEDIUM・メインが `_loss_intervals([100, 200], [200]) == [(100, 200)]` で再現）→ ログの順を保つ ② oracle の marker 行を計画（ブロック・seq・印の長さ）と照合する（Codex P2）③ `pipeline.py` の説明文の窓の向きが逆・「すべての行が対応すれば人の打鍵は無い」は言い過ぎ（Codex P2）④ `data.md` の「Machine that ran the deposit check」の表が、公開の文書にログイン名と home のパスを書かせる（security 範囲外）→「渡したか」だけ ⑤ `delivery.py` が深い入れ子の JSON で RecursionError の traceback と exit 1（理由 2 の exit 2 にならない）⑥ `file:///Users/...` が絶対パスの検査を通る ⑦ `spec_predict.py` のエラーに絶対パス ⑧ `open_set.py` が観測のヘッダーでなく計画の os を渡し、OS の照合が働かない ⑨ `l2.py` の混合の区間の `thin` が値の無いブロックも数え、状態の名前が `_ba_interval` と揃わない・`per_trial` の `diff_ci` に状態が無い ⑩ `plan_figures` が `speed` の無いブロックを黙って落とす ⑪ `match.py:1631` の空白 ⑫ selftest の穴（戻らない喪失の併合・同じ時刻）。
- **Codex P1 の端**（区間の終わりで人の打鍵が本物の行を区間の外へ押し出す）は、区間の終わりが焦点の戻りの 500 ms 後なので、人がそこで打てば参照に key-down が残り打鍵の規則が捕まえる。数える終わりを延ばす直しでも閉じる。

## 判断 128: 判断 127 の実装上の選択（2026-10-02・G-GEAR・メインの選択・研究者が覆せる）

1. **`delivery.py`**（Sonnet の作業用エージェント D・メインが差分を読んだ）: 焦点の行を 1 回だけ読んで（時刻・行番号）の順に並べる（`read_gt_focus`）。起動の前の区間は、ログの順で最初の焦点の行が focus_in なら「始まり（None）〜その時刻」、焦点の行が無ければログ全体。止めた後の区間は、参照のログの key_down・focus の行の最大の時刻から終わりまで（この区間にも余裕 500 ms を付ける）。これらは中止の規則の区間にだけ入り、試行の一覧と記述の数は実際の焦点の行だけから数える。延長は `_extended_end`（e = b + 320、last = b + 20 から、送出の間隔が 320 ms 以下で続くあいだ last を進め e = max(e, last + 300)）。`n_presses_unexplained_in_losses` は窓のどれかに入る対応の無い行の異なる数。marker 行は block_id（整数・計画にある）・seq（整数・計画の印の長さの内）・（block_id, seq）の重複を拒む。`main` は RecursionError と Exception も exit 2（型の名前だけ）。selftest 144 件・変異 17 本のうち 16 本赤（残る 1 本は後ろの `except Exception` と同じ出力になる等価な変異）。
2. **`pipeline.py`**（作業用エージェント E）: `REGISTERED_PLAN_SHA256` を `{"on": …, "off": …}` にし、実データでは manifest の `cell.ime_settings.live_conversion`（文字列の "on" / "off" だけ）と計画の SHA-256 を対応させる（`_plan_matches_cell`）。`abort_rule.registered_plan_sha256` は dict。`file:` に続く `/`（JSON の綴りを含む）を絶対パスとして拒む。説明文の窓の向きを直し、言い過ぎを消した。合成の run を現実に寄せた: 参照のログの頭に focus_in、送ったすべてのキーに参照の key_down（+3 ms・セッションの組み立ての後に足すので正解のセッションに入らない）と観測の key 行（+5 ms）。期待を変えた selftest は 3 件（配送の報告の到達・重複していた key_down の削除・中止した run の内容の行の時刻）で、検査は弱めていない。selftest 12 ケース・変異 8 本すべて赤。
3. **ほかのファイル**（作業用エージェント F）: `spec_predict.py` のエラーは basename と型の名前だけ・`--out` の書き込みの OSError も exit 2・`plan_figures` は `speed` の無い / 不正なブロックを拒む。`open_set.py` は観測のヘッダーの os を渡す。`l2.py` の混合の区間は値のあるブロックだけを数え、`per_trial` に `diff_ci_status`（`ok` / `fewer_than_two_blocks`）。`match.py` の空白を行の継続に。selftest はすべて緑・変異 4 本赤。
4. **文**: §3.4 の理由 1 を「セルに §2.4 が与える計画でない」に、焦点の段落に起動の前と止めた後・ログの順・延長の数え方を足し、人がいなければ当たらない場合に「run の始まりと終わり」を足した。§7 の停止の規則の項に延長の後ろの重複行を足した。`data.md` の預けた機械の表を「渡したか（数）」だけに、手順 1 を「セルの計画」に。長くなった段落を 119 字で折り返した（§6.8 の 1 段落は中身を変えずに折り返しだけ）。本文 15,469 語。
5. **確認**（G-GEAR・最終の状態で）: `kit/check.sh` 29 本緑・`run.sh --synthetic` 2 回で 4 ファイルともバイト一致・未凍結の実データは exit 3・`_style_check.py` 0 件・`check_citations.py` 違反なし・節の参照はすべて実在。⚠️ 作業用エージェント E は報告の後もバックグラウンドの変異を走らせていたので、メインは E の完了を確かめてから確認をやり直した（`pipeline.py` の SHA-256 は報告の後で変わっていない）。

## 判断 129: 完了時レビューの Codex 2 巡目の扱い（2026-10-02・G-GEAR・メインの選択・研究者が覆せる）

Codex 2 巡目は今日足した規則の境界（`ba89bcbd..HEAD` の `delivery.py`・`pipeline.py`）を見た（P1 1・P2 2）。メインが一次で裏取りした。

1. **P1 延長した数える範囲が、喪失の外の入力を中止の理由にする**（真・文の食い違い）: 延長の範囲では、観測の余分な行（観測器の重複など）が連鎖を通じて中止の理由になりうるのに、§3.4・§6.3・`pilot-macos.md`・`pipeline.py` の説明は「喪失の外の余分な行は中止にしない」と書いていた。人の打鍵なら、焦点が戻った後なので参照に key-down が残り、理由 3 で中止になるのは同じ。→ 規則は保守側のまま変えず、4 か所を「広げた区間と、その後に数える範囲の外では」に揃え、§3.4 に「その中では原因を問わず数える（§7）」を足した。§7 は判断 128 で既に書いた。
2. **P2 `FORMAT`（`delivery/1`）を上げていない**（真）: 凍結の前で外部の利用者はおらず、利用側（`pipeline.py`・`data.md`）は同時に直した。形式は凍結のタグで固定される。→ 上げない。
3. **P2 本番の `REGISTERED_PLAN_SHA256` を登録の計画と照合するテストが無い**（真）: メインが今日、`generate_plan.py` で 2 計画を生成し直して SHA-256 の一致（ON `c7a5469d…`・OFF `3759ebf7…`）と on / off の対応（§2.4）を確かめた。定数と文の機械照合は判断 120 の 9 で採らないと決めている。→ テストは足さない。

---

★ 以下 2026-10-02（G-GEAR・M3 の凍結のセッション・引き継ぎ `next-session-ime-paper-m3-freeze.md`）。

## 判断 130: 凍結の前の試しの書き出しが拒否した selftest の 2 行を直す（2026-10-02・G-GEAR・メインの選択・研究者が覆せる）

- **発見**: 凍結の前に、main（`1086e3be`）の作業ツリーから `export.internal.py --allow-missing-license` を試しに回したら **exit 1**（`kit/analysis/pipeline.py:1996`・`:1997` が `user-path`）。判断 128 で足した deposit の selftest の 2 ケース（`file:///Users/x/y`・`FILE:/home/x`）が、書き出しの許可リスト（`alice`・`bob`・…・`name` の架空の名前だけ）に無い名前 `x` を使っていた。⚠️ 判断 128 の確認は `kit/check.sh` と `run.sh` だけで、書き出し（024）を回していなかった → **このまま凍結していたら、凍結の commit から書き出せず、M4 のロガーもビルドできなかった**。
- **直し**（`eaaeea74`・凍結の前）: 名前を `gina`・`harry` に替えた。検査の意味（`file:` に続く `/` は名前によらず絶対パス・期待は `absolute path` だけ）は変わらない。`pipeline.py --selftest` 12 ケース緑。
- **確認**（G-GEAR・Python 3.11.9・`eaaeea74`）: 試しの書き出し exit 0（98 ファイル）。一覧の SHA-256 を 024 の `LIST_PY` と、§9 の定義から書いた別の実装（scratchpad の `listsha.py`）の両方で計算して一致（`1ed564ec933f3950c01364363610cede01e7563765f562a71baec18034d64e05`・98 ファイル）。`kit/check.sh` 29 本緑。§9 の 5 ファイルの SHA-256 は表と一致。§2.4 のコマンドで 2 計画を生成し直して ON `c7a5469d…`・OFF `3759ebf7…`（§2.4・`REGISTERED_PLAN_SHA256` と一致）。凍結のハッシュ `64dfbb6e5f08222ade1fb96a8171d97c0fa1bc9ca9adb5cc987fc27bd9a8af2a`（作業ツリーと HEAD の blob で同じ・3 ファイルとも CR 0）。024-acceptance.sh は ✅ 137・❌ 2（SCOPE と GUARD だけ・B15）——書き出した側の `cargo test --locked`（ロガー）・全 `*.rs` の rustfmt 構文解析・陰性対照を含めて緑。
- ★ 教訓: 公開物のコードを変えたら、凍結や merge の前に **024（書き出し）も回す**。

## 判断 131: 凍結する・タグは `ime-observation-prereg-macos`・一覧を計算し直す道は M12 で公開 repo の最初の commit にする（2026-10-02・G-GEAR・研究者の選択）

研究者に AskUserQuestion で 3 問（すべて推奨どおり）。
- **凍結するか**: 既知の限界 3 つ（① 焦点の規則の最終形〔判断 125・127〕はパイロットの生ログにまだ当てていない — 預けるときに `--check-deposit` が当てる・§3.1 ② 規則の感度は selftest の合成の場合でしか確かめていない・§7 ③ 窓 300 ms・余裕 500 ms は設計の選択・§3.4）と判断 130 の直しを示して → **凍結する**（推奨）。採らなかった: 先に Mac で ① を当てる・保留。Status の文は問いのプレビューのとおり（凍結の日付・印は §9・印の 2 つ目が設定・seed・規則のファイルと合うときだけ実データを解析する・Windows は追補）。
- **タグの名前**: 既存のタグは `v0.1.0`〜`v0.1.38` だけで、`ci.yml` は `v*` のタグの push でリリースのビルドを走らせる（`on.push.tags: ["v*"]`）ので `v` で始まる名前は使えない → **`ime-observation-prereg-macos`**（推奨・annotated・Windows の追補は `ime-observation-prereg-windows` と対）。作業ブランチと一緒に origin へ push する。採らなかった: 日付入り・スラッシュの名前空間。
- **一覧を計算し直す道**（§9 の「公開物から計算し直せる」）: 凍結の commit にはライセンス全文が無いので、凍結の書き出しは `--allow-missing-license` の形（98 ファイル・`LICENSE-*` なし・`CITATION.cff` と `.zenodo.json` に TODO）→ **M12 で公開 repo（新しい履歴）の最初の commit を凍結の書き出しそのものにしてタグを付け、ライセンスと M12 の書き出しはその上に積む**（推奨）。今は何も公開しない。採らなかった: OSF の登録に zip を添付（登録と同時にロガーのコードが公開になる）・凍結の前にライセンスを置く。

実体（G-GEAR・Python 3.11.9）:
- 凍結の commit **`ff122e3246346da7869c4e990e4978acb1f191c6`**（`preregistration.md` の Status と 2 つの印だけ・8 行足して 3 行消した）。印は `frozen_at: 2026-10-02`・`sha256: 64dfbb6e5f08222ade1fb96a8171d97c0fa1bc9ca9adb5cc987fc27bd9a8af2a`。凍結したファイルの SHA-256 は `fa6fd586d580c47f13506cd36a87a94c08d6b9ab55b16a7b6df0b67670f87773`（タグの blob と書き出しの中で同じ）。
- `--check-prereg` exit 0。陰性対照: `sha256` を 1 桁変えた写し・`frozen_at` の行を消した写しは exit 3。`run.sh`（実データ）は凍結の門を通り、`data.md` に run が無いので `no run directory was given` で exit 2（計測の前なので想定どおり・結果は書かない）。⚠️ 020-acceptance の AC3 は凍結の前の約束（「`preregistration.md` が無い」は下書きを置いた時点から赤・「本番は exit 3」は上の実測の exit 2 で満たさない）。020 は凍結の後には回さない（凍結の門そのものは `pipeline.py` の selftest が一時の木で確かめている）。020 自体は回していない。
- タグ `ime-observation-prereg-macos`（annotated・メッセージに 2 つの印）→ `ff122e32`。
- **書き出しの一覧の SHA-256 = `29b183ba245939ad82d9fa2d7db26e1a18520e2966f4aa9ec74478a4e51e6c49`（98 ファイル）**: タグのクリーンな worktree（`C:/wt/ime-m3-freeze-export`・detached）から `export.internal.py --out <scratchpad> --allow-missing-license` を 2 回（どちらも exit 0・同じ一覧）。§9 の定義（相対パスと SHA-256 を空白で・パスのバイト順・各行 LF）から書いた実装と 024 の `LIST_PY` で同じ値。凍結の前の試し（`eaaeea74`）との差は `experiment/preregistration.md` の 1 行だけ。一覧そのものは `freeze-export-list-macos.txt`（このディレクトリ・M12 で公開 repo の最初の commit と照合する）。
- タグのクリーンな worktree で `kit/check.sh` 29 本緑・`run.sh --synthetic` 2 回で 4 ファイルともバイト一致。`_style_check.py papers/ime-observation` 0 件。
- 凍結の後の commit（記録）: `experiment/notes.md` に凍結の commit・タグ・`sha256`・一覧の SHA-256 を書いた（登録の URL と日付は登録の後）。`notes.md` は凍結のハッシュの対象でも解析のコードでもなく、§9 が記録の場所に名指す。

## 判断 132: 完了時レビューの扱いと Codex の上限（2026-10-02・G-GEAR・メインの選択・研究者が覆せる）

範囲は `1086e3be..ce205e83`（9 ファイル）。code-reviewer（CRITICAL・HIGH 0・MEDIUM 2・LOW 3）∥ security-checker（CRITICAL・HIGH・MEDIUM 0・LOW 1）∥ Codex 1 巡（`run-codex-review.sh` を公開物の 3 ファイルに絞って・確定的な指摘 0・確認事項 3・20,874 tokens）。指摘はメインが一次で確かめた。凍結したファイル（`preregistration.md`）と解析のコードには触れず、記録と申し送りで応えた。
- **Codex の上限**: 着手時に origin/main を取り込むと当日の台帳は 371,742 / 8 回（AI 疲労の #291 を合わせた和）で上限 300,000 を超えていた → 研究者の既定の指示（2026-10-01「codex は必要に応じて予算引き上げしていいよ」）で `daily_token_budget` だけを 420,000 に上げて 1 巡回した（392,616 / 9 回）。`tokens_used` は触っていない。回し終えて 300,000 に戻した（`_comment_budget_2026_10_02_ime_m3_freeze`）。
- **Codex 2 巡目は回さない**: 2 巡目は「自分が足した規則の境界条件」を見るためのもの（memory の運用）だが、この範囲は規則を足していない（コードの変更は selftest の文字列 2 つだけ）。1 巡目の後の変更は `.steering/` の記録だけ。
- **code-reviewer M1（公開の読者は private の commit とタグに辿り着けない・M12 の後の公開物からは別の一覧になる）**: 真（`gh repo view` で PRIVATE・`LICENSE-*` は一覧に 0 行）。→ OSF の登録の説明に添える案を引き継ぎ §2 に（研究者が決める）、M12 で `notes.md` に公開側のどの commit・タグが凍結の書き出しかを足すことを `_issue-plan.md` の M12・`tasklist.md` に。
- **code-reviewer M2（引き継ぎの「§2 の 6 は済み」が事実と違う・タグの push が要る）**: 真（その時点で `ls-remote` は空）。→ 引き継ぎの文を直し、タグは `git push origin refs/tags/ime-observation-prereg-macos` で明示して送り、`ls-remote` で確かめる。PR は merge commit（`ff122e32` を main から辿れる）。
- **code-reviewer L1（`run.sh` だけ `experiment/` からの相対）・L2（追補で印は差し替わるが Status の日付は §8 で書き換えられない）**: 真。凍結したので直さない → M6 の申し送り（追補の節に 1 文・`experiment/run.sh` と書く）。L3 は対応不要（検査の意味は変わらない）。
- **security LOW（40 桁とタグ名を公開物に書くこと）**: 公開してよい（40 桁は §9 で OSF の登録に載る・SHA-1 から中身は逆算できない）。残るリスク = private repo が公開物と同じネットワークに入るか公開に切り替わると、その commit のツリーが取り出せる → M12 は `git init` の新しい履歴で作り、fork・公開への切り替え・private の履歴の push を使わない（判断 20 の「新しい履歴」に理由を足した）。⚠️ 報告の「前例: 公開物の `kit/logger/manifest.json` に private repo の 40 桁がある」は**書き出しの前の開発側のファイルについてで、公開の形には当たらない**（書き出した側の manifest に `upstream` の欄は 0 件・メインが確かめた）。結論は変わらない。
- **Codex の確認事項**: (1) 値の整合 → 判断 131 で照合済み（`pipeline.py` の直し `eaaeea74` は凍結の commit の前にあり、タグに含まれる）。(2) 凍結の門の異常系 → `pipeline.py` の selftest（印なし・プレースホルダ・空・コメントやフェンスの中・2 行・ハッシュ違い・設定の 1 バイトの変更）と、メインの陰性対照 2 本。時系列の主張は OSF の登録が第三者の時刻を与える（判断 73）。(3) 1 文字の名前の境界 → 当たらない（`ABSOLUTE_PATH_RES` は名前によらず `file:` ＋ `/`・`/Users/`・`/home/` の根で当たる・`pipeline.py:967-975`）。

## 判断 133: M5（Windows の較正パイロット）は G-GEAR ではなく別の Windows 実機で行う・IME の学習はリセットしない・電源の設定はメインが一時的に切って戻す（2026-10-03・G-GEAR・研究者の選択）

- **背景**: OSF の登録（`https://osf.io/9nh7r`）が公開になり、Mac の M4 は Mac の夜を待つ。M5 は M4 にも OSF にも依存しない（`_issue-plan.md` §5 の前提は issue 群と M0 だけ）ので先に進める。`_issue-plan.md` は M5〜M7 の場所を G-GEAR としていた。
- **研究者の選択**: M5 は**別の Windows 実機**で行う（G-GEAR でビルドを始める前に研究者が指示）。G-GEAR では何も送っていない（書き出し・ビルド・run は 0 回）。
- **研究者に 3 問**（AskUserQuestion・推奨と理由つき）:
  - IME の学習 → **リセットしない**（推奨）。Mac（M1・事前登録 §3.2・§7）と同じ扱い。MS-IME の入力履歴の消去は設定画面の操作でコマンドが無く、`reset_cmd` にできない。追補で開示する。
  - 電源の設定 → **メインが一時的に切って戻す**（推奨）。`powercfg` で AC のスリープと画面オフを 0 にし、元の値を先に記録して run の後に戻す。スクリーンセーバーとロックも読んで、要れば同様に。
  - 実行の時間（離席中に自動 ／ その場で 1 本ずつ ／ 準備だけ）→ **答えの前に中断**（別の実機にすると決まったため）。→ 別の実機のセッションの最初に聞く。
- **未決（M6 の前に研究者が決める）**: M6（追補の凍結）と M7（Windows の本計測）をどの機械で行うか。⚠️ パイロットは計測する機械と IME の版で挙動を較正するものなので、**M7 は M5 と同じ機械**を推奨する。決まったら `_issue-plan.md` の M5〜M7 の「どこで」を直す。
- **影響範囲**: 引き継ぎ `next-session-ime-paper-m5-windows.md`（新規）・`tasklist.md`（M5 の行）。

## 判断 134: 判断 133 を改める —— 数時間以上の run だけを別の Windows 実機で行い、それ以外（M5 を含む）は G-GEAR で行う（2026-10-03・G-GEAR・研究者の選択）

- **研究者の指示**（判断 133 の引き継ぎを書いた後）: 「数時間以上の run 以外まではこの G-GEAR で行う」。
- **分け方**（メインが一次で当てはめた）:
  - **別の Windows 実機**: 数時間以上の run だけ。M7 の本計測のセル（Mac の見積もりで 1 セル約 9.5〜10 時間・`pilot-macos-1-notes.md`）と、Windows の E3 の 2 条件（`idle` / `working` は各 8 時間・事前登録 §6.10 の macOS の形を Windows の追補でも採るなら）。
  - **G-GEAR**: それ以外。M5 の較正パイロット（短い試しと本体・本体は Mac の M1 で 126 試行約 23 分）・書き出しとビルド・セルのファイル・M6 の追補の凍結・M8 の解析など。
- **判断 133 から引き継ぐもの**: IME の学習はリセットしない・電源の設定はメインが一時的に切って戻す（どちらも研究者の答え）。実行の時間（離席中に自動か）は未決のまま。
- ⚠️ **未決（M6 の前に研究者が決める）—— 較正した機械と計測する機械が違う**: パイロットは MS-IME の呼び出し列を**その機械と IME の版で**較正する。M5（G-GEAR）と M7（別の実機）で OS や MS-IME の版が違うと、パイロットで決めた正解の定義や手順書が計測する機械で同じに動く保証が無い。→ 推奨: (1) 追補に計測する機械の OS と MS-IME の版を書く、(2) M7 の前に計測する機械で**短い確認の run**（Mac の `verify-1` と同じ形・全シナリオ × 3 速さ × 1 で数分〜10 分程度）を回し、呼び出し列の型がパイロットと同じことを確かめる（違えば追補の凍結の前に戻る）。この確認は短い run だが計測する機械でしか意味が無いので、「短い run は G-GEAR」の例外になる。
- ⚠️ G-GEAR は Windows の CI の self-hosted runner（memory）。パイロットの run の間に CI の job が走ると負荷で送出の時刻が遅れる（`emit/README.md`）→ run の間は push しない（または runner を止める・止めると hosted へ回る）。
- **影響範囲**: `_issue-plan.md` の M7・M10 の「どこで」・引き継ぎ `next-session-ime-paper-m5-windows.md`（G-GEAR 用に書き直す）・`tasklist.md` の M5 の行。

## 判断 135: 引き継ぎを開いた機械は G-GEAR ではなく、判断 134 の「別の Windows 実機」（Surface Pro 8）だった —— M5 は G-GEAR に残し、ここでは機械の前提だけを記録する（2026-10-03・Surface・研究者の選択）

- **所見**（メインが着手時に測った）: `hostname` は `TABLET-J870RJQA`、`Win32_ComputerSystem` は Microsoft Corporation・**Surface Pro 8**。引き継ぎ §1 の参考値（G-GEAR: 26H2・build 26300）と OS が違う。Rust（`cargo` / `rustup`）は入っておらず、`python` は Microsoft Store の入口だけ（`AppData/Local/Programs/Python/Python311・312・314` の中に `python.exe` は無い）。
- **研究者に 1 問**（AskUserQuestion）: G-GEAR で行う（ここでは止める）／この Surface で行う（判断 134 を改める）／**この機械が「別の Windows 実機」** → **研究者の答え: この機械が判断 134 の「別の Windows 実機」**。→ M5 は判断 134 のとおり G-GEAR に残す。この機械では何もビルド・送出していない（ブランチを切っただけ）。
- **計測する機械の前提**（判断 134 の未決 2 で「M5 の記録と比べる相手」になる・2026-10-03 に読んだ値）:
  - OS: Windows 11 Home（`EditionID` Core）・`DisplayVersion` **25H2**・`CurrentBuild` **26200**・UBR 8875（⚠️ G-GEAR の 26H2 / 26300 と違う）。
  - MS-IME: 入力方式は `0411:{03B5835F-F03C-411B-9CE2-AA23E1171E36}{A76C93D9-5523-4E90-AAFA-4DB112F9AC76}`（Microsoft IME）だけ。DLL の版は `IMJPTIP.DLL`・`IMJPAPI.DLL`・`IMJPPRED.DLL` が **10.0.26100.8875**、`IMJPCD` など辞書・変換の DLL が 10.0.26100.8737 / 8328。`HKCU\Software\Microsoft\IME\15.0\IMEJP\MSIME`: `romastyle` MS-IME・`PredictionUseInputHistory` 1・`UseCloudSuggestion` 0（既定から変えていない・読んだだけ）。ローマ字／かな入力の別はまだ読んでいない。
  - キーボード: 配列 `00000411`（日本語）・`OverrideKeyboardIdentifier` PCAT_106KEY・`OverrideKeyboardType` 7（JIS）。
  - 画面と電源: `ScreenSaveActive` 1（`ScreenSaveTimeOut` 空）・`ForegroundLockTimeout` 200000・電源の計画は「バランス」。⚠️ 8 時間の run の前に、判断 133 のとおり元の値を記録してから一時的に切る。
  - 道具: git 2.55.0.windows.3・bash 5.3.15・`gh` 認証済み。**Rust と Python が無い** → M7 / M10 の前に入れる（M5 と同じ版を推奨）。
- **影響範囲**: `tasklist.md` の M5 の行・引き継ぎ `next-session-ime-paper-m5-windows.md` §1（計測する機械の値を足す）。

## 判断 136: 判断 135 を改める —— M5 をこの Surface Pro 8（計測する機械）で行う（2026-10-03・Surface・研究者の選択）

- **研究者の指示**（判断 135 の記録の後）: 「rust を CLI で入れてから実施するのは？ 特にハードウェアでの強い制約などがなければ同じ Windows だし実行していいんじゃ」。
- **メインの判断**: 賛成。この Surface は M7 の本計測の機械（判断 134・135）なので、**較正と計測の機械が揃い、判断 134 の未決 2（較正と計測の機械が違う）が消える**。ハードウェアの制約は見当たらない（i5-1135G7・8 GB・JIS・AC 電源）。G-GEAR の値（26H2 / 26300）は比べる相手として残す。
- **入れた道具**（2026-10-03・winget）: Python **3.11.9**（user・判断 52 の G-GEAR と同じ版）・rustup 1.29.1 → `rust-toolchain.toml` の **1.98.1**（既定にも 1.98.1 を指定）・Visual Studio 2022 Build Tools（VCTools・MSVC 14.44.35207）。`git` の作者名はこの機械に無い → 研究者の答えでコミットごとに `-c` で Mikoto Miura（設定は変えていない）。
- **電源**: 読んだ値は AC・DC とも スリープ 0・画面オフ 0・スクリーンセーバーなし（`SCRNSAVE.EXE` 空）→ **変える必要がなかった**（判断 133 の「切って戻す」は不要・値は `~/ime-pilot/power-before.txt`）。着手時はバッテリーで、研究者が AC につないだ（`BatteryStatus.PowerOnline` を読み戻し）。
- **影響範囲**: `tasklist.md` の M5・`pilot-windows-1-notes.md`（新規）・`_issue-plan.md` の M5 の「どこで」は M5 を閉じるときに直す。

## 判断 137: S4 は逸脱 D1 として Windows だけ Esc 3 回にし、S8 は数字の後に Enter を足す —— 直した手順で確認の run まで回す（2026-10-03・Surface・研究者の選択）

- **問い**（`pilot-windows-1-notes.md` の所見 1・2）: S4（Space → Esc 2 回）は MS-IME で複数文節に変換した後は取り消しにならない（3 回目で取り消し）。凍結の生成器の `_scenario_checks` と事前登録 §2.3 の表が S4 を OS を問わず Esc 2 回に固定しており、§8 の追補の範囲で直せない。S8 は数字の後に Enter が要る（§8 の範囲）。
- **研究者の答え**（AskUserQuestion）: S4 は「逸脱として Win だけ Esc 3 回（推奨）」、S8 は「直して確認の run まで回す（推奨）」。
- **変えたもの**: `kit/gen/generate_plan.py` の `_PROFILES` に `cancel_converted` を足し（windows は Esc 3 回・macOS の 2 つは Esc 2 回で値は変わらない）、S4 の照合をそれで読む。windows の `after_digit` を `["enter"]`。2 つの手順書の `os.windows` の S4 に Esc を 1 つ、S8 に Enter を 1 つ足した（2 つの手順書の `os.windows` は selftest が一致を求める → 同じに直した）。逸脱の記録は新しい `experiment/deviations.md` の D1（英語・日付・理由・影響）。
- ★ **macOS への影響が無いことを確かめた**: 本番の `plan_config.macos.json`・seed 11 で、タグの書き出しと直した作業ツリーから 2 つの手順書それぞれで macOS の計画を作り、記録される手順書の SHA-256 を伏せると**バイト一致**した（3,150 / 2,925 試行）。⚠️ 手順書の SHA-256 は変わるので、計画そのものはバイト一致しない（§8 のとおり macOS の計画はタグから作る）→ D1 にはこの形で書いた。
- **selftest**: 生成器 113 件緑。`kit/check.sh` は作業ツリー（`core.autocrlf=true` で CRLF）では 3 本が赤だが、**変更を stash した状態でも同じく赤**（`.rs` を `"\n"` で照合する selftest が CRLF で外れる・変更と無関係）→ LF のクリーンな worktree で全体を確かめる。
- **影響範囲**: M6 の追補（§8）では D1 を「逸脱」として追補の本文から参照する。正解の経路の選択・起動の手順（`run_fg.py` など）・`gt_rules` の Windows のブロックは M6 で決める。
- **完了時レビュー**（2026-10-03・`5c37c8ed..HEAD`）: `security-checker` は指摘なし（生ログ・キーコード・読みの転記なし・`papers/` に機械の情報なし・照合は緩んでいない）。`code-reviewer` は中 2・低 3 → 中 2（D1 がマーカーの欠けを S4 だけのせいにしていた・タグの差分に macOS のプロファイルの行が出ることを書いていなかった）と低 2（コメントに 1 文節の場合・3 回目の Esc の記述を "expected to" に）を直した。低 1（Windows の負の対照の selftest）は、凍結に関わる変更を広げないため見送った。
- ⚠️ **`/cross-review` は省いた（安全ゲート: codex 不在）**: この Surface には Codex CLI が入っていない（npm のグローバルは `claude` だけ）。加えて、この機械の `python3` は Microsoft Store のスタブなので、`secrets-pre-filter.sh`・`codex-budget-guard.sh` が「hook 入力 JSON を parse できない」で fail-closed になり、「codex」の語を含む Bash 呼び出しはすべて止まる（hook は `python3` を `python` より先に選ぶ）→ この機械で Codex を使うなら、導入と、Store のエイリアスを切るか hook の側の対応が要る。

## 判断 138: M6（Windows の追補）の中身 —— TSF の 1 セル・`gt_rules` は変えない・起動の道具を `kit/run/` に足す・n = 75（2026-10-03・Surface・研究者の選択）

- **材料**（2026-10-03・gt と oracle と plan だけを読み、obs は読んでいない）: タグのままの `gt_rules.json` でパイロットの gt を `gt_sessions.py` に通した。計画との一致は、直した手順の確認の run で **IMM 39 / 39・TSF 39 / 39**（確定 30・取消 9）。直す前の run の不一致（short: 33 / 39・30 / 39、本体: 102 / 117・93 / 117）は、すべて S4 と S8 の持ち越しとその次の試行による。S15（前面を外れた時点の確定）と TSF の S7（→ が文節の数を超えたときのその場の確定）も、今の規則で確定として数えられる。
- **研究者の答え**（AskUserQuestion・4 問とも推奨どおり）:
  1. 正解の経路は **TSF の 1 セル**（`refinput_tsf`・規則の `win_tsf`）。理由: MS-IME は TSF の入力方式（TIP）で、TSF の入力欄は composition を直接受け取る（IMM の窓は互換の層を通す）。いまのアプリの多くは TSF。IMM はパイロットの比較の相手として記録に残す。
  2. `gt_rules.json` の Windows のブロックは**変えない** → 凍結の `sha256:` は macOS と同じ値のまま、`frozen_at:` だけが追補の日付になる。根拠はパイロットの一致率として追補に書く。
  3. `focus_front.py`・`away_window.py`・`run_fg.py` を **Windows のセルだけが使う新しいファイルとして `kit/run/` に足す**（§8 の範囲・凍結の既存コードは変えない・selftest を付ける）。
  4. 試行数は **macOS と同じ 75**（13 シナリオ × 3 速さ × 75 = 2,925 試行・Surface の実測で約 11.5 時間）。
- **影響範囲**: `experiment/plan_config.windows.json`（新規）・`kit/run/` の 3 ファイル（新規）・Windows のセルのファイル（新規）・`preregistration.md` の追補の節と凍結の印・`experiment/pilot-windows.md`（M5 を閉じる）・`experiment/notes.md`（OSF の登録・M6 の最後に研究者が行う）。

## 判断 139: 凍結の解析コードは Windows の run を拒み、Windows の主要な範囲も作れない —— 逸脱 D2（計画の照合を広げる）と D3（Windows の範囲を正解の長さで定める）（2026-10-03・Surface・研究者の選択）

- **見つけたこと**（impact-analyzer の調査をメインが一次で確かめた）:
  1. `kit/analysis/pipeline.py:253` の `REGISTERED_PLAN_SHA256` と `:873` の `_plan_matches_cell` は、セルの `ime_settings.live_conversion` が "on" / "off" で、計画の SHA-256 が macOS の 2 つの計画と一致する run だけを解析する → Windows の run は必ず拒まれる。§8 の追補の範囲では直せない。
  2. `pipeline.py:787` は `plan["os"] == "macos"` のときだけ予測（`spec_predict`）を作り、無ければ範囲は `all_trials` だけ（`_prediction_summary` の理由は「the prediction models the macOS observer only」）。→ Windows では問い 1〜3 の主要な範囲 `under_limit` が無い。Windows のロガーは IME の WinEvent で観測するので（`driver_windows/ime_winevent.rs`）、キーからの予測はそもそも当てはまらない。20 秒の打ち切りは OS 共通（`kit/logger/src/input/ime_cloak.rs:167` `MAX_SESSION_MS: u64 = 20_000`）。
  3. TSF の参照入力欄は IME が消費したキーを受け取らない（`delivery.py` で参照への到達 6 / 1,470・パイロット本体 16 / 3,900）→ 中断の理由 3（外からの押下）は 0 で通るが、人の打鍵を見つける力は弱い（理由 4 は観測ログで働く）。IMM の参照なら各ブロックの前の `VK_IME_ON` がキーの行を 1 つ残し、凍結の k = 0 で毎回中断扱いになっていた（`verify-imm` の区間 0 に 1 行）→ TSF を選んだこと（判断 138）と整合。追補の限界に書く。
- **研究者の答え**（AskUserQuestion・2 問とも推奨どおり）: (1) **逸脱 D2**: `pipeline.py` の計画の照合に Windows のセルの計画を足す（セルの os が windows なら Windows の計画と照らす・macOS の照合は不変）。(2) **逸脱 D3**: Windows だけ、正解のセッションが 20 秒以上続いた試行を「長い」として `under_limit` / `over_limit` を作る（§4.3 の印を使う）。
- **進め方**: macOS の解析は macOS のタグから走る（§8）ので、D2・D3 は macOS の結果を変えない。それでも変更後のコードで macOS の入力の結果が変わらないことを selftest と合成データで確かめる。D2・D3 は `experiment/deviations.md` に記録し、追補の節から参照する。
- **実装と確かめたこと**（2026-10-03・判断 139 の続き）: D2 は `REGISTERED_PLAN_SHA256_WINDOWS`（Windows の計測の計画 `b7bdf8fc…36b0`）を足し、セルの os が windows なら照らす。D3 は新しい `kit/analysis/gt_scope.py`（正解のセッションが `limit_ms` 以上の試行を「長い」とし、予測と同じ形式で `match.py` に渡す）。Windows のセルを解析したときだけ `note_windows`・`registered_plan_sha256_windows`・`long_trials_from` を結果に記録する。selftest に Windows の合成 run の場合を足し、D2 の前の照合・D3 を外した状態の 2 つの対照で赤になることを確かめた。**macOS の合成 run の結果 4 ファイルは、タグのコードと変更後のコード（LF の worktree）でバイト一致**。LF の worktree で `kit/check.sh` 33 本緑。
- **計測の計画**: `plan_config.windows.json`（n = 75・macOS と同じ値）・`recipes.json`・seed 20260929 → 2,925 試行・117 ブロック・SHA-256 `b7bdf8fc…36b0`。Python 3.11.9 と 3.13.15（`uv`）でバイト一致。⚠️ この機械は `core.autocrlf=true` → 作業コピーから作ると設定ファイルの SHA-256 が変わり計画も変わる → 書き出し（LF）から作る（`README.windows.md` に書いた）。
- **D3 の見積もり**: 計画の打鍵の時刻の幅が 20 秒以上の試行 = 617 / 2,925（slow 401・mid 123・fast 93）。直した手順の確認の run 2 本では、この見積もりと正解の「長い試行」が 10 / 10 で一致。S13 は全試行が長い。S13 以外の層の最小は S6 slow の 30。
- **パイロットの診断**（§3.1 に相当・追補 §10.9）: E2 の割り当て（攻撃なし・`--markers-in-obs`）は 7 本・27 ブロック・429 試行すべてを採点し、割り当てられない押下 0。`delivery.py`（登録の形）は TSF の run を捕まえない（k = 0・計画外のフォーカス喪失 0）。IMM の run は k = 1・モードのキーを数える版で捕まえない。
- **書いたもの**: `experiment/deviations.md` の D2・D3、`experiment/pilot-windows.md`（公開・英語）、`kit/run/README.windows.md`、`preregistration.md` の §10（Windows の追補）。文体の検査は違反 0。⚠️ 凍結の印はまだ替えていない。

## 判断 140: Windows の追補は、凍結の前に attack-me を 1 回回す（2026-10-03・Surface・研究者の選択）

- **問い**: §10・D1〜D3・`pilot-windows.md` を書き終えた。macOS の登録は凍結の前に attack-me を 5 回回した。追補をどうするか。
- **研究者の答え**（AskUserQuestion）: 「attack-me を 1 回回してから凍結（推奨）」。理由（メインの推奨）: D2・D3 は解析のコードに触れるので、第三者の目で攻める価値が高い。
- **やり方**: `attack-me/prereg-ime-windows/round-1/`。macOS と同じ立場・同じ接地の文献（研究者の指示）。macOS の `tmp\` は G-GEAR にあるので、この機械で取り直した（8 本のうち 7 本は round 1 の原本と SHA-256 が一致・Koo の HTML は動的なページで違う〔題・著者は一致〕）。投稿規程も取り直し、J1〜J10 は逐語で在る。見る範囲はタグ `ime-observation-prereg-macos` から変わった箇所（§10 と、持ち込んだ公開物・コード）に絞り、§1〜§9 は文脈として渡した。
- ⚠️ この機械の `~/ime-pilot/runs/` に封印物と生ログがある（査読者役は Read しか持たないが、読むことは構造で縛れない）→ 起動の前に研究者に知らせ、応答の保存の検査（一覧の外の絶対パス）で確かめる。

## 判断 141: attack-me round 1（Windows の追補）の採否 —— 長い試行は oracle の送出の幅・D4 で人の打鍵を中止に・問 4 は macOS で決める・Windows の解析は別の一覧・直す一覧を全部承認（2026-10-03・Surface・研究者の選択）

- **round 1 の判定**: major revision（R1・R2・R3 とも major・fatal 0・接地の引用 12 / 12 在る・注入 0）。記録は `attack-me/prereg-ime-windows/round-1/verdict.md`。3 人が一致した最重要: Windows のロガーの規則が §10 に無く、メインが書いた「composition events を読む」は実装（IME の窓の表示・非表示・cloak）と違う。20 秒の打ち切りは cloak の経路にしか無く（窓の表示から）、WinEvent の経路には無い（25 秒の安全弁だけ）→ D3 の「両 OS で同じ」は成り立たない。⚠️ メインが一次を確かめずに書いた誤り（「composition events」と `cell.windows.json` のパス）。
- **研究者の答え**（AskUserQuestion・4 問とも推奨どおり＋直す一覧を全部承認・round 2 まで）:
  1. 長い試行の主の定義は **oracle の送出の幅**（試行の最初と最後の送った押下が 20 秒以上）。正解の長さの版は感度（`under_limit_gt_duration`）、19〜21 秒の境界の帯と、2 つの定義で分類の違う試行を層ごとに数える。
  2. **逸脱 D4**: Windows の run は、観測の key 行のうち送った押下で説明されないものが区間の印を超えたら中止（解析も寄託もしない）。パイロット 7 本は全区間で印ちょうど。
  3. 問 4 の推奨は **macOS の 2 セルで決める**（凍結のまま）。Windows のセルは同じ判定を別に報告し、成り立たなければ Windows のログへの但し書きとして報告する（推奨は変えない）。
  4. Windows の run は **`experiment/data.windows.md`**（新規）に並べ、`pipeline.py --runs-from experiment/data.windows.md --out experiment/results/windows` を §10.7 に逐語で。Windows のタグで出た macOS の結果は報告しない。IMM のパイロットの run は寄託しない（`--check-deposit` が k = 0 で拒む）。
- **実装**（`9fb61af2`・`b41c00b3`）: `kit/analysis/scope_windows.py`（`gt_scope.py` を置き換え）・`pipeline.py`（D4 の `observation_abort_segments`・`reference_abort_reasons(dlv, os_name)`・Windows の run の gt の `src` が `win_tsf` でなければ拒む〔D2 に含めた〕・感度の範囲・診断〔result_len の無い `tsf_end`・S4 の何回目の Esc〕・`note_windows` の書き直し・説明文）・selftest（D4 を外す・経路の検査を外す の 2 つの対照で赤）。§10 を書き直した（10.1〜10.11・Windows のロガーの小節・層ごとの表・Windows のタグの SHA の表・問 4・解析の入口・問 5 の量と `cpu_all_zero`）。`deviations.md` を D1〜D4 と「macOS は変わらない」の節（命令とハッシュ: macOS の計画はタグから登録の SHA と一致し、変更後は手順書の SHA を伏せてバイト一致／合成の macOS の run の結果 4 ファイルがバイト一致〔bootstrap 2000〕）で書き直した。`pilot-windows.md`・`README.windows.md` を直した。LF の worktree で `kit/check.sh` 33 本緑・書き出し 108 ファイル・文体の検査 0。
- **次**: round 2（同じ立場・同じ文献・役ごとの引き継ぎを渡し、再掲を求めない）。⚠️ round 2 の直しでコードを変えたら、`deviations.md` の「macOS は変わらない」の比較を取り直す。

## 判断 142: attack-me round 2（Windows の追補）の採否 —— minor・直して凍結へ（2026-10-03・Surface・研究者の選択）

- **round 2 の判定**: minor revision（R1・R2・R3 とも minor・fatal 0・接地の引用 6 / 6 在る・注入 0）。記録は `attack-me/prereg-ime-windows/round-2/verdict.md`。一致した指摘: §10.3 がロガーの実装と食い違う（WinEvent の経路の 25 秒の安全弁は dwell ≈ 25 秒の行を書く・経路は時点ごと〔WinEvent が一度も来ていなければ cloak〕・行に経路が残らない・セッション中の SHOW はやり直し・回収前の要約の喪失）。`cpu_all_zero` の食い違い。節番号の直し漏れ（メインの誤り）。
- **研究者の答え**（AskUserQuestion・4 問とも推奨どおり）: (1) `cpu_all_zero` は `working` だけ不十分として測り直し、`idle` は印つきで報告（§10.9 が README に優先）。(2) 経路は判定せず、20〜25 秒と 25 秒以上の観測の行を数えて記述で報告（混在は限界）。(3) 計測の守りを両方足す: IME の版がパイロットと違えば 39 試行の点検で 39 / 39 のときだけ測る／各 run の直後に点検の行（manifest の SHA）を commit して push。(4) 残りの直しを全部行って凍結まで。
- **実装**（`d40e090a`）: §10.1（OSF に登録するもの・push の時刻）・§10.3 の書き直し・§10.6（凍結の前に変われば表を直す・比の分母 13.3 / 13.0）・§10.7（D3 の読み方・S15・経路の記述・Σm²/Σm 1.56〜3.19・`scope_windows.py --from-plan`・診断・問 4 は修飾キーと離鍵の行を評価しない）・§10.8（`working` にも・D4 の盲点と報告・版の規則・push）・§10.9・§10.11（持ち出し・観測区間の時刻・参照の時刻・選別）。`scope_windows.py`（`--from-plan`・観測の行の診断）・`pipeline.py`（寄託でも参照の経路を検査・節番号）。selftest に寄託の経路の場合。`data.windows.md`・`pilot-windows.md`（IMM の k = 1 は登録の設定ではない・`windows_def` の数・比の分母）・`README.windows.md`（Windows 11 Home の更新の一時停止と時刻・LF の取り出し・版の確認）・`deviations.md`（D4 の盲点・「10 trials of one plan, run twice」・証拠の commit を `d40e090a` に）。
- **確かめたこと**: `d40e090a` の LF の worktree で `kit/check.sh` 33 本緑。macOS の計画（両手順書）と合成の run の結果 4 ファイルは、`9fb61af2` のときと同じハッシュでタグとバイト一致。文体の検査 0。
- **補足**: 道具の名前は判断 138 の作業名（`focus_front.py`・`away_window.py`・`run_fg.py`）から、公開物では `focus_windows.py`・`away_windows.py`・`start_windows.py` にした（OS ごとの命名にそろえた・メインの選択）。
- **次**: 完了時レビュー（code-reviewer ∥ security-checker・Codex は不在）→ 凍結の印を替える → タグ `ime-observation-prereg-windows` → 書き出しの一覧の SHA → OSF への登録（研究者）→ `notes.md`。

## 判断 143: 凍結のセルのテンプレートの相対パスが Windows で起動できない —— 逸脱 D5 を計測の前に記録する（2026-10-04・Surface・研究者の選択）

- **起きたこと**: 再起動の後の版は OS build 26200.9457・`IMJPTIP.DLL` 10.0.26100.9278（パイロット 8875）→ §10.8 の 39 試行の点検が要る。`cell.windows.json` を写して `ime` と 2 つの旗だけ埋めたセルで、書き出しの最上位から `start_windows.py` を起動 → runner が `FileNotFoundError`（WinError 2）で中止（00:24 JST・キーは 1 つも送っていない・`~/ime-m7/runs/verify-m7`）。
- **原因（実測）**: `subprocess` が `kit/logger/target/release/...`（スラッシュ・`./` なしの相対）を見つけられない。同じ cwd で `kit\...`・`.\kit\...`・`./kit/...` は起動する。`python`（`focus_cmd`）は起動する。パイロットのセル（`~/ime-pilot/make_cells.py`）は絶対パスだったので見つからなかった。
- **研究者の答え**（AskUserQuestion）: 「逸脱 D5 を先に記録（推奨）」。セルのコピーで 2 つの exe のパスを `kit\...`（最上位からの相対のまま）にし、`deviations.md` に D5 を書いて commit → push してから、点検 → 本計測。テンプレート・runner・タグのファイルは変えない。
- **点検の結果（§10.8・2026-10-04 00:27〜00:37 JST）**: D5 のセル（SHA-256 `0e4c17ed…4fb6`）・計画 `plan-verify`（`f02e046b…0154`）で `start_windows.py` → 中止なし・前面の確認 3 / 3。観測は `seal_obs.py` で封印（`cd4a5fcc…`・key 行 2,952 を残した）。`gt_sessions.py --rules experiment/gt_rules.json`（`b9a48375…`）→ `src` `win_tsf`・39 セッション（確定 30・取消 9）・**`oracle_agreement` 39 / 39** → 本計測へ。生ログは `~/ime-m7/runs/verify-m7`（中止の 1 回目は `~/ime-m7/runs/aborted/verify-m7-1`）。
- **本計測の 1 回目**: 2026-10-04 00:38 JST に起動（`~/ime-m7/runs/cell-1`・計画 `b7bdf8fc…36b0`）。
- ⚠️ **本計測の 1 回目は中止**: 2026-10-04 00:59 JST ごろ、Claude Code が「メモリ不足・セッションが idle」を理由にバックグラウンドの shell（`start_windows.py`）を止めた（run の失敗ではない）。runner・観測器・参照入力欄とも終了・`run.json` なし・oracle 6,133 行。空きメモリ 1.4 / 8 GB（VS Code・Chrome・Defender・メモリ圧縮）。`delivery.py` exit 0・参照側 0 / 0 / 0・観測の D4 の数 14（最後の区間・途中で切れた）→ 中止の試み 1 として `data.windows.md` に 1 行を書き、すぐ push（§10.8）。再起動は研究者の指示を待つ。

## 判断 144: G-GEAR の Windows パイロットの最初の試しを記録として残す（2026-10-04・G-GEAR・メインの選択・研究者が覆せる）

- **経緯**: 2026-10-03 未明、判断 134（M5 は G-GEAR）に従って G-GEAR で Windows の較正パイロットを回した（MS-IME `IMJPTIP.DLL` 10.0.26100.9278・Windows 11 26H2 / build 26300）。記録は枝 `docs/ime-m5-pilot-ggear`（`433d13ff`）に push したが、**main には入れていない**。その間に Surface のセッションが判断 135〜143 で M5（Surface）→ M6（追補の凍結・`https://osf.io/4jwzn`）→ M7 の Windows のセルまで進めた。⚠️ その枝の「判断 135」は main の判断 135 と**別の中身**（番号が衝突した）。
- **採用**: 枝の `pilot-windows-1-notes.md` を **`pilot-windows-ggear-notes.md`** に名前を変えて main に残す（冒頭に「M5 の記録ではない」と出どころを追記）。枝の判断 135・`pilot-windows-tools/`・書き直した引き継ぎは main に入れない（Surface の M5 と M6 が置き換えた）。
- **残す理由**: 別の版の MS-IME でも S4（変換の後の Esc 2 回で取り消されない）と S8（数字の後に Enter が要る）が同じに出た（Surface の判断 137 と一致）。ほかに、開始の前面化が `SetForegroundWindow` に拒まれうること（研究者の入力の直後に起動した run だけが通った）、`refinput_imm` の窓に文字が出ないこと（研究者が誤動作と受け取った）が記録にある。生ログは G-GEAR の `C:/ime-pilot-win/runs/` にある（コミットしない・預けない）。
- **後始末**: 枝 `docs/ime-m5-pilot-ggear` は不要になった → 2026-10-04 に研究者の了承で origin とローカルから消した（`433d13ff`・PR なし・worktree なし）。中身の記録はこの判断と `pilot-windows-ggear-notes.md`。⚠️ `pilot-windows-tools/` と書き直した引き継ぎは残していない（Surface の `kit/run/` と M5 の記録が置き換えた）。

## 判断 145: 投稿計画を前倒しする —— BRM に 10 月末に投稿・原稿は今から並行で書く（2026-10-04・G-GEAR・研究者の選択）

- **背景**: M4（Mac）は最後の run が 2026-10-05 10 時ごろに終わる（研究者）。M7 は Windows のセルが 10-04 13:03 に完了（2925 / 2925）、残りは Windows の E3（`idle` → `working`）で、明日・明後日に終わる見込み（研究者）。→ 結果は 10-05〜06 にそろう。Windows の追補は 10-03 に凍結済みなので、macOS の解析を Windows の結果より先に始めても追補に影響しない。
- **研究者の選択**: 投稿の目標は **2026 年 10 月末**（推奨どおり）。原稿は**今から並行で**書く（推奨どおり）。コンテキストの都合で、執筆は**次のセッション**から始める。
- **日程**（遅れても 11 月上旬に収める）:

  | 時期 | 内容 |
  |---|---|
  | 〜10-05 | 原稿の外枠（節構成・主張 ↔ 根拠の対応表・判断 21 の `manuscript/outline.md`）・手法の節（凍結した事前登録と追補 §10 から書ける・結果を待たない） |
  | 10-05〜07 | M4 の §3.4 の点検 → macOS の解析（macOS のタグから）。Windows の E3 の後に Windows の解析（Windows のタグから）・E3 のまとめ（M8・M10） |
  | 10-08〜17 | 結果・考察・序論・要旨 → 原稿の全体 |
  | 10-18〜22 | attack-me（原稿のプレ査読）1〜2 巡 → 直す |
  | 10-23〜27 | M12: 公開 repo・リリース・Zenodo の DOI・Open Practices Statement（OSF の 2 つの登録と DOI）・カバーレター |
  | 10-28〜31 | BRM に投稿 |

- **投稿先は BRM のまま**（判断 1）。★ **費用 0 を一次で確かめた**（2026-10-04・Chrome で `https://link.springer.com/journal/13428/how-to-publish-with-us`）: 逐語 "Authors can also choose to publish under the subscription publishing model (no APC charges apply); both options will be offered after the paper has been accepted."（OA を選ぶと APC は $4,090）。投稿規程（`/submission-guidelines`）の本文に投稿料・掲載料・カラー図の費用の語は無かった。雑誌なので登壇も無い → 研究者の条件（memory「登壇なし・費用ゼロ」・2026-09-28）を満たす。⚠️ 採択後に購読モデルを選ぶこと（OA を選ばない）。
- **CHI 2027 Posters**: 2026-09-28 に取り下げ済み（p321 のタスクの判断 15・判断 13 の追記）。→ 判断 8・9 の CHI の記述は無効。`design.md` §6・`requirement.md`・`paper-suggest.md` の残りを直した。
- ⚠️ **M12 の申し送り**: 凍結のタグが 2 つ（`ime-observation-prereg-macos` の一覧 `29b183ba…`・98 ファイル／`ime-observation-prereg-windows` の一覧 `f61af353…`・108 ファイル）。判断 131 は「公開 repo の最初の commit を macOS の凍結の書き出しにする」だけを決めている → **Windows の凍結の書き出しの一覧も公開物から計算し直せる形**（2 つ目の commit にするなど）を M12 の前に決める。
- **arXiv**: 任意。endorsement が要る（memory）ので、投稿をそれ待ちにしない。
- **影響範囲**: `design.md` §6・`paper-suggest.md` §6・`requirement.md` のゴール・`_issue-plan.md` の M13・`tasklist.md`・引き継ぎ `next-session-ime-paper-writing.md`（新規）。

## 判断 146: 合成入力の記録一式を「データセット」として論文の貢献の 1 つに加える（2026-10-04・G-GEAR・研究者の選択）

- **背景**: 研究者の問い「人のタイプではない機械型の IME データセットも公開するのか」。→ 公開することは既に決まっていた（`data.md` の寄託の手順・`design.md` §4・BRM の Level 2 TOP）が、論文では「再現性のための材料」の扱いだった（判断 6 の 4 つの貢献に入っていない）。メインが「content-free な IME 観測器を検証するためのデータセット（正解の参照ログ付き）として貢献に数えることもできる」と示した。
- **研究者の選択**: 「データセットとして出すのも今回の論文での貢献のプラスになりそう」→ **貢献に加える**。
- **範囲（メインの案・外枠で研究者が確定する）**:
  - ★ **主張の芯は判断 6 のまま**（精度評価が主）。データセットは 5 つ目の貢献として足す。⚠️ 「人の書字のデータ」「自然な入力のベンチマーク」とは書かない（合成入力・参照入力欄は 1 つ・IME の版は記録した版だけ）。
  - 中身: run ごとの `plan`・`oracle`・`gt`（参照入力欄が受けた IME のイベント＝正解）・`obs`（観測器の出力）・`run.json`、E3 の標本、語句のコーパス（青空文庫のパブリックドメイン）、計画の設定と seed。macOS 2 セル（ライブ変換 ON / OFF）＋ Windows 1 セル（MS-IME・TSF の参照）。
  - 使い道として書けるもの（過大にしない）: (a) IME が入力欄へ送る呼び出し列の、OS と設定ごとの実測（正解の定義の根拠の再検討）、(b) 自分の観測器の定義を同じ計画で再実行して比べる（計画・実行器・参照入力欄は公開物にある）、(c) 本文を伏せた打鍵ログから本文をどこまで復元できるかの研究（E2 と同じ形・送った語句が既知なので答え合わせができる）。
- **増える仕事**（判断 145 の日程の 10-23〜27 の M12 の枠に入れる・⚠️ 足りなければ 11 月上旬へ）:
  1. データの説明書（Datasheets for Datasets の形〔Gebru ら・引用は citation-ssot で登録〕: 動機・構成・収集の過程・前処理・用途・配布・保守）を公開物に置く。`kit/formats/FORMATS.md` を形式の仕様として参照する。
  2. Zenodo の記録を**データセットとして** DOI 付きで作る（ソフトウェアの記録と分けるか 1 つにするかは M12 で決める）。⚠️ memory: Springer の Editorial Manager は Zenodo のリンクを Invalid にした（EMSE の実測）→ 原稿の本文と参考文献に DOI を書き、投稿の欄は GitHub にする。
  3. 原稿にデータセットの節（または Availability の節を厚く）と、貢献の箇条に 1 行。限界（合成・1 つの参照入力欄・IME の版・中止した run の扱い）を明記する。
  4. 較正パイロットの生ログを含めるか（M2 の残り「生ログの置き場」）をこの機会に決める。
- **変えないもの**: 凍結した事前登録・解析のコード・寄託の手順（`data.md`）。データセットとしての打ち出しは論文の書き方の変更で、解析を足さない。
- **影響範囲**: 引き継ぎ `next-session-ime-paper-writing.md`（外枠に貢献 5 を入れる・増える仕事）・`tasklist.md`。

## 判断 147: 原稿の外枠 —— データセットは専用の短い節・パイロットの生ログは別の区分で数える・原稿は LaTeX（Springer の雛形）（2026-10-04・G-GEAR・研究者の選択）

- **背景**: 引き継ぎ `next-session-ime-paper-writing.md` §2 の 1（外枠）と 4（形式）。判断 146 は「範囲はメインの案・外枠で研究者が確定する」としていた。外枠は `papers/ime-observation/manuscript/outline.md`（公開物・英語）、内部の対応は `manuscript-map.md`。
- **研究者の選択（3 問とも推奨どおり）**:
  1. **データセットは専用の短い節**（§10 The dataset）にする。内容の表・用途 (a)〜(c)・限界を書き、説明書（Datasheets for Datasets の形）は公開物に別に置く。Availability の節を厚くする案は採らない。
  2. **較正パイロットの生ログ（基準を満たす run）をデータセットの一部として数える。ただし別の区分**（計画が本計測と違う較正の run）にする。★ 預けること自体は凍結した事前登録 §3.1 が既に約束している（判断 110）ので、判断 146 の増える仕事 4 の「含めるか」は、**データセットとして数えるか**だけが残っていた。
  3. **原稿は LaTeX（Springer Nature の雛形）**。表は結果の JSON から生成して本文に埋め込む。EMSE の実測（memory）どおり、提出する `.tex` は 1 本にまとめ、タイトル頁は別添にする。
- **メインの選択（研究者が覆せる）**: 貢献は判断 6 の 4 つ ＋ 判断 146 の 1 つの 5 つにし、ロガーは独立の貢献にせず貢献 2「ロガーとその検証（主）」にまとめた（design.md §0 の C2 は貢献 2 の前半に入る）。
- ⚠️ **未決（後で決める）**: (a) この G-GEAR には LaTeX も pandoc も無い（`command -v` で確認）→ コンパイルは LaTeX のある機械か Overleaf。(b) Springer の雛形のファイル（`sn-jnl.cls` など）は雛形側のライセンスなので、CC BY 4.0 の公開物に入れるかは雛形を取得するときに確かめる（入れないなら取得の手順を書く）。(c) BRM の投稿規程は WebFetch では Springer の認証に転送されて読めなかった → 投稿の前に Chrome で読み直す。
- **影響範囲**: `papers/ime-observation/manuscript/outline.md`（§10・DS1・Table 10）・`manuscript-map.md`・`tasklist.md`。
- ⚠️★ **追記（同日・attack-me の準備で BRM の投稿規程を一次で照合した結果・メインの記録）**: `curl -sL`（cookie つき）で `https://link.springer.com/journal/13428/submission-guidelines` の原文を取得し（2026-10-04 23:39 JST・HTTP 200）、文を逐語で確かめた。(1) ★ **投稿は ScholarOne**（逐語 "Manuscripts are to be submitted electronically via ScholarOne" ・`http://mc.manuscriptcentral.com/brmic`）であって Editorial Manager ではない → 上の 3 の「EMSE の実測どおり `.tex` は 1 本・タイトル頁は別添」の **`.tex` 1 本の根拠は BRM には当たらない可能性がある**（EMSE は Editorial Manager の実測）。タイトル頁は規程に逐語 "The title page must include the authors' names and affiliations and the corresponding author's address, telephone number, and e-mail address" があるが、別添かどうかは書かれていない。→ ScholarOne の挙動は投稿の段で確かめる。LaTeX の選択そのものは変えない。(2) ★ **外枠の誤りを直した**: Open Practices Statement は逐語 "immediately prior to the References section" なので、Declarations（逐語 "placed in a 'Declarations' section before the reference list"）→ Open Practices Statement → References の順にした（外枠の初稿は Open Practices を Declarations の前に置いていた）。Declarations の見出しは原文の一覧どおり（"Conflicts of interest/Competing interests"・"Authors' contributions (optional …)" を足した）。(3) 本文の分量・LaTeX の雛形の語は取得した範囲の原文に無い（規定なし）。

## 判断 148: 原稿を LaTeX で書くので公開物の文体検査を `.tex` / `.bib` に広げ、手法の節の草稿を書く（2026-10-04〜05・G-GEAR・メインの選択・研究者が覆せる）

1. **文体検査の穴**: `issues/_style_check.py` はディレクトリを歩くとき `TEXT_SUFFIX` にある拡張子だけを見ていて、`.tex` と `.bib` を飛ばしていた（明示したファイルなら禁止語だけは見る・日本語の地の文は見ない）。→ 公開の書き出し（`kit/export/export.internal.py` がこの道具を全体に回す）を原稿が素通りする。★ `TEXT_SUFFIX` に `.tex`・`.bib` を足し、2 つは**コメントも含めて全行**の日本語を赤にした（公開する全文なので）。selftest に 6 件（tex の本文・コメント・英語だけ・GSE・bib・走査で `.tex` を拾う）。変異 2 本（拡張子を戻す・分岐を外す）でどちらも selftest が赤。`papers/ime-observation` の全体で違反 0。
2. **手法の節** `papers/ime-observation/manuscript/sections/method.tex`（英語・LaTeX・約 5,200 語）: 凍結した事前登録（§2〜§6・§10）・`deviations.md`・`pilot-*.md` から書いた。数（パイロットの run 数 6 と 7・試行 468 と 429・一致 124/126・117/117・39/39・層の最小 31 と 32・S6 の 3 と 30・コーパス 1,800 句・読み 6〜30・SudachiPy 0.7.0）はすべて一次の記録から写した。測った後に分かる値（macOS の版）は `\tbd{}`。表は Table 3（シナリオ）・逸脱・2 回の凍結。
3. **書誌**: `manuscript/references.bib`（公開物・著者と年で引く・判断 76）。登録済みの [P269]・[V179]・[V181]・[V184]〜[V189] は事前登録の参考文献の行のとおり（名はイニシャル。⚠️ 最初に記憶で名を展開して書き、一次で確かめていないので戻した）。★ 新しく `docs/references.md` に **[V190] Takaoka ら（2018）Sudachi**（ACL Anthology の bib で確認）と **[V191] 青空文庫**（サイトが 200 を返すことを確認）を append した。OSF の 2 つの登録は API で題と登録日を確かめて `@misc` に（著者は TODO）。
4. `manuscript/main.tex` は Springer の雛形（`sn-jnl`・`sn-apa`）の骨組みだけ。雛形のファイルは置かない（判断 147 の未決 (b)）。⚠️ この機械には LaTeX が無く、**コンパイルしていない**（後の節のラベル〔`sec:logger`・`sec:dataset` など〕はまだ無い）。

## 判断 149: 外枠の attack-me round 1（major）の採否 —— 直す一覧を全部承認・§11 は閾値の無い 5 種・D6 と §10.8 を公開の記録に・題は Logging に固定・要旨の規則・利用者の道具は足さない・キー行の時刻は登録済みの値だけ（2026-10-05・G-GEAR・研究者の選択）

- **round 1**: `attack-me/outline-ime-manuscript/round-1/`。有効な査読 3 / 3（R1 計時の道具の検証・R2 書字研究の利用者・R3 メタサイエンスとデータ管理・いずれも Opus の `paper-reviewer`）＋ 監査役。3 人とも **major**。接地の引用 34 件を本文で照合して捏造 0、注入 0、偽陽性 0、確かめられない 1（テキスト入力研究の文献）。★ LG2 は「Windows の経路の単体テスト〔41 本〕は在るが外枠が名指ししていない」形の真。★ §10.8 の点検（39 / 39）は内部の記録にだけあり公開物に無かった（真）。
- **研究者の選択（7 問とも推奨どおり）**:
  1. 直す一覧（verdict.md の ★ 以外）を**全部承認**。
  2. **§11 の推奨は閾値の無い 5 種に限る**: (a) 定義が OS で違う測度は OS 間で比べない (b) 20 秒の打ち切りは規則から向きだけ (c) 漏洩は登録の判定の言い方（プライバシーの基準ではない）(d) 自分の機械で 39 試行の点検から再検証する手順 (e) 自分のアプリでの一致はこの一式では測れない。推奨ごとに根拠（結果・規則・構成概念）の行 RE1〜RE5。
  3. **D6 として記録し §10.8 の点検も公開**: `deviations.md` に D6（外から止められた試行は中止に数え、管理者権限で拒まれた開始は数えない）・`data.windows.md` に「Check of section 10.8」の節（build 26200.9457・IME 10.0.26100.9278・39 / 39・30 確定 9 取消）。⚠️ 点検の計画の SHA-256 の全桁はこの機械に無い（Surface の点検の run の manifest にある）→ 公開物には先頭 8 桁と末尾 4 桁だけを書き、全桁を写すことを外枠の Open items に置いた。
  4. **題は "Logging Japanese IME conversion without recording text: Observability limits, a cross-platform logger, and a synthetic-input validation" に今固定**し、結果の後に変えない（判断 15 の「E2 が強ければ T4」は取り下げ）。⚠️ `README.md`・`CITATION.cff`・`.zenodo.json`・`kit/` の題の文字列は T1 のまま → 公開の書き出しの前（M12）に揃える。
  5. **要旨の規則**: セルごとに (i) 検出の recall と precision の層ごとの Wilson 区間の最小の下端〜最大の上端 ＋ 主の範囲が外した割合 (ii) `dwell_ms` の偏りの速さごとの区間の範囲 (iii) 漏洩の判定と推奨（または推奨なし）(iv) 実行コストの条件ごとの CPU の平均（区間なし）。`all_trials` は本文の表だけ。
  6. **利用者向けのスクリプトは足さない**。代わりに Table 4（書字研究の測度 × OS: obs から計算できるか・この検証が裏づけたか）と LG3。
  7. **キー行の時刻は登録済みの値（§6.3 の行の遅れ・連続する行の間隔の誤差）を本文に上げるだけ**（KT1）。OS の刻みの分解能の探索は足さない。
- **実装（メイン）**: 外枠を全面的に書き直した（6,984 語・主張 31 行: OB 4・LG 5・RF 1・AG 8・KT 1・RC 3・RT 1・RE 5・DS 3。AG7・AG8 は RF1・KT1 に寄せた）。手法の節に D6・§10.8・精度の計画・基準をソフトウェアの層に置く理由・診断は読むためだけ・carry-over の割合・2 回の凍結の表。`_style_check.py` 違反 0。
- ★ **メインの反省**: context-B の「持ち帰ってほしいこと」に「入力方式自身のセッション」「どの測度を信頼してよいか」「結果に基づいて」と書いたのはメインで、事前登録と食い違っていた（監査役 3-A-1・3-A-2）。round 2 の context-B は事前登録の言い方にする。
- **次**: round 2（同じ立場・同じ接地・引き継ぎを渡し再掲を求めない）は次のセッション（コンテキストが半分を超えたため・memory「半分で区切る」）。

## 判断 150: 外枠の attack-me round 2（major）の採否 —— 直す一覧を全部承認・要旨は登録 §6.1 に従い層を絞る・推奨 (d) は 2 段に狭める・round 3 は原稿の attack-me で確かめる・macOS のセルが欠けたら推奨しない（2026-10-05・G-GEAR・研究者の選択）

- **round 2**: `attack-me/outline-ime-manuscript/round-2/`。有効な査読 3 / 3（R1 major・R2 minor・R3 major）＋ 監査役。接地の引用 57 件を本文で照合して捏造 0、注入 0、偽陽性 0（R2 の「macOS は押下だけ」の前提は偽で、指摘の残りは真）。round 1 の指摘の大半は解消。新しい穴は round 1 の直しで足した仕組みにあった（verdict.md の Y1〜Y44）。
- ★ **メインの見落とし（2 件）**:
  1. 判断 149-5 の要旨の規則を推奨したとき、凍結した事前登録 §6.1（623〜626 行 "In the abstract and the conclusions … An estimate in the primary scope is given together with the fraction of trials that the scope sets aside and the estimate under `all_trials`"）と照合していなかった。→ 規則が登録に反していた（Y1）。
  2. round 2 の context-B にも、事前登録と食い違う文が 2 つあった。「打ち切りが集計を動かす向きは規則から言える」は 4 つの集計のうち 2 つだけに当たり、Windows の窓の経路には 20 秒の打ち切りが無い。「時刻つきの記録は評価しない」は誤りで、時刻を持つ特徴の集合は攻撃に渡して推定だけを報告した。
- ★ **ソースで確かめたこと**: macOS のロガーも押下と解放の両方でキー行を書く（`kit/logger/src/driver_macos.rs` の `handle_key` と `queue_row`）。届き方（`delivery.py`）と攻撃（`closed_set.py` の `read_obs`）が使うのは押下の行だけ。事前登録 §1.1 は macOS を押下だけで書いている → 原稿では両 OS とも解放の行を書くと書き、登録の書き方との違いを注にする。KT1 の定義は凍結の `delivery.py`（62〜76 行）に在る。安全弁の実装とテストは `kit/logger/src/main.rs`（273 行・777 行）。
- **研究者の選択（6 問とも推奨どおり。1 問は事実の確認）**:
  1. 直す一覧（Y1〜Y44 の ★ 以外）を**全部承認**。既定は 3 つ: KT1 で最初のブロックを分けない（凍結の出力に無い）。文書の写しはアーカイブの URL で残す。`FORMATS.md` をデータの寄託に含める。
  2. **要旨は登録 §6.1 に従う**。セルごとに、主の範囲の値に、範囲が外した割合と carry-over の割合、`all_trials` の値を添える（逸脱 D7 は作らない）。範囲に入れるのは、主の範囲で **30 試行以上の層だけ**にし、外した層の数を添える（null の層は入れない）。Windows は「別の構成概念との一致」と添える。CPU は系ごとに書いて比べない。推奨は 1 つで、Windows は但し書きにする。§13 の結論にも同じ規則をかける。
  3. **推奨 (d) / RE4 は 2 段に狭める**（新しいコードは足さない）。(i) 39 試行の点検で確かめられるのは、自分の機械と版で手順が入力方式を計画どおり動かすか（基準の側・Windows・D5 の手当てつき）。(ii) ロガーの一致を推定し直すには、登録の計画の全体と凍結の解析が要る。この一式は登録外の計画では一致を計算しない。macOS には登録の短い点検が無い。
  4. **外枠の round 3 は回さない**。直した外枠は、原稿の attack-me（stage `manuscript`・判断 145 の 10-18〜22）に round 1・2 の引き継ぎを渡して確かめる。
  5. **macOS のセルが 1 つでも測れなければ、粒度は推奨しない**と報告する（登録の条件「両セル」を確かめられないため）。
  6. 試行 2 の間に Surface で何が動いていたか（Y12）は**分からない → Surface のセッションで調べる**。それまで外枠には報告の項目だけを置き、Open items に載せる。
- **実装（メイン）**: 外枠を直す（Y1〜Y44）。`method.tex` の基準を置く理由（Y7）を狭める。`deviations.md` D6 と `data.windows.md` の試行 1 の言い方を揃える（Y12）。⚠️ `README.md` の題（Y25）は引き継ぎ §2 の 4 で書き出しの前に直す。
- **影響範囲**: `papers/ime-observation/manuscript/outline.md`・`sections/method.tex`・`experiment/deviations.md`・`experiment/data.windows.md`・`manuscript-map.md`・引き継ぎ。

## 判断 151: macOS の Accessibility にも変換の範囲の属性と開始・終了の通知がある —— §3 と貢献 1 は「アプリが用意する経路は両 OS にある・ロガーはアプリを問わない経路だけを使う」の対称の形に書き直す・GSE 本体の文書は別のタスクで直す（2026-10-05・G-GEAR・研究者の選択）

- **背景**: 結果を待たない節（§3）を書くために Apple の一次文書を取得したところ（2026-10-05・`https://developer.apple.com/tutorials/data/documentation/…json` を `curl` で取得）、AppKit の `NSAccessibility.Attribute` に **`textInputMarkedRangeAttribute`**、`NSAccessibility.Notification` に **`NSAccessibilityTextInputMarkingSessionBegan` / `…Ended`** が載っていた（3 つとも macOS 10.6 から・説明の文は無い）。★ **WebKit のソースで実際に使われていることを確かめた**: `Source/WebCore/accessibility/mac/AXObjectCacheMac.mm` 361〜366 行（`AXNotification::TextCompositionBegan` / `…Ended` を 2 つの通知に写す）・`WebAccessibilityObjectWrapperMac.mm` 2290〜2295 行（変換中の範囲を `NSRange`＝位置と長さで返す）・コミット `1a5a134d14845e9bf54a67049a36a2585e62897c`（2026-10-05 00:59 UTC の main）。Chromium の `ax_platform_node_cocoa.mm` には同じ語が無かった（それ以上は調べていない）。
- ★ **数え直し**: 内部の調査メモ（`.steering/20260821-workspace-behavior-triage/survey-input-channels.md` §7.5）の「135 個を全数確認してゼロ」は **Carbon（C）の定数**（属性 101・通知 25・パラメータ付き 9）だけだった（今回も同じ数・該当なし）。AppKit の定数（属性 132・通知 43・パラメータ付き 19）を見ていなかった。→ ⚠️ 外枠の OB3「Accessibility の属性・通知に変換中の文字列を報告するものは無い」と、凍結した事前登録 §1.1「macOS には他のアプリの変換状態を報告する公開のインタフェースが無い」は**言い過ぎ**。
- **研究者の選択（2 問とも推奨どおり）**:
  1. **§3 と貢献 1 は対称の形で書き直す**: 両 OS とも、アプリのアクセシビリティの実装が用意すれば文字列なしで変換を知らせる経路がある（Windows は UI Automation の TextEdit パターンの変換対象の変化〔0x8030〕、macOS は変換中の範囲の属性と開始・終了の通知）。これはアプリしだいなので、アプリを問わない記録には頼れず、ロガーは使わず評価もしていない。アプリを問わない経路は Windows では入力方式の窓のイベント（と cloak）、macOS では調べた範囲に無い → 打鍵から推す。事前登録 §1.1 の文は文書が支えるより広いと注に書く。新しい計測は足さない。
  2. **GSE 本体の文書**（`docs/agent-shared.md` の技術的制約 7 の「macOS 側（公開 API が存在しない）」と調査メモ §7.5）は、この枝に混ぜず、**別の小さなタスクで一次（WebKit のソースと Apple の定数の一覧）に戻して直す**。
- **メインの見つけたこと（ソースで確かめた・研究者が覆せる）**: macOS のロガーが行を書くキーは、事前登録 §1.1 の書き方（「入力モードのキーのほか F13〜F19 と修飾キーが行を書かない」）より狭い。`kit/logger/src/driver_macos/keymap.rs` の `is_observed_key` は、英字・数字・主キー群の記号・Return・Tab・Space・Backspace・Forward Delete・Escape・矢印・F1〜F12 だけを通し、テンキー・Page Up / Down・Home / End・JIS の ¥ と _ のキー・ISO の § キーも行を書かない。→ 原稿の Table 3 はソースどおりの集合を書き、登録の書き方との違いを注にする（解放の行と同じ扱い・判断 150）。計測の計画が送るキー（`FORMATS.md` の `keyname`）は英字・数字・記号 3 つ・Space・Return・Escape・Backspace・Tab・矢印・入力モード・F13〜F19・Shift だけなので、計測の行には影響しない。
- **メインの見つけたこと（2）**: ログのヘッダの `manifest_sha256` はロガーの**共通部分の manifest**（`kit/logger/manifest.json`・状態機械・キーの分類・`main.rs`）だけを覆い、各 OS のドライバは別の manifest（`manifest.macos.json`・`manifest.windows.json`）にある（`main.rs` 56 行の doc 逐語 "Covers only the core manifest, not a driver's own manifest."）。→ 原稿の §4 と LG1b は「ヘッダの SHA-256 は共通部分を識別し、ドライバを含む全体は凍結のタグが固定する」と書く。
- **影響範囲**: `papers/ime-observation/manuscript/outline.md`（貢献 1・OB3・§3・§4・Open items）・新しい節 `sections/observability.tex`・`sections/logger.tex`・`manuscript-map.md`・`docs/references.md`（Apple / Microsoft / WebKit の文書）・引き継ぎ（GSE 本体の文書を直す別タスク）。

## 判断 152: main に入った Mac の記録（PR #297）と Windows の解析（PR #304）をこの枝に取り込む —— 逸脱の番号は main の D6（macOS の晩）を保ち、この枝の Windows の試行の数え方を D7 に付け直す（2026-10-05・G-GEAR・研究者の選択）

- **背景**: 研究者の知らせ「Mac の計測結果が git に merge された」「PR304 も merge された」。`git fetch` で確かめた: PR #297（`9cedba6c`・M4 の記録）は `data.md` の点検の表（ON・OFF・E3 working とも打ち切りに数えない）・`env.md`（macOS 27.0.1 26A434・JapaneseIM-RomajiTyping 6.3・rustc 1.99.0・Swift 6.4・背景の CI の負荷）・**逸脱 D6「macOS の run が別々の晩ではなかった」**。PR #304（`cf320319`）は Windows のセルの解析の結果（`experiment/results/windows/e1_*.json`・`e2_open_set_windows-msime-tsf.json`）と `data.windows.md`（run の行・書庫の SHA・問 5 の working の点検の行）。⚠️ macOS の解析（問 1〜4）はまだ回っていない。⚠️ Windows の問 4 の閉じた集合は凍結のコードの欠陥で止まっている（`next-session-ime-paper-m7-windows.md` §2.11・研究者が逸脱として決める待ち。macOS も S12 の候補が 72 で同じ欠陥に当たるおそれ）。
- ⚠️ **衝突**: この枝は判断 149 で D6 を「Windows の試行の数え方」に使っていた（未 merge）。main は D6 を macOS の晩に使った（先に merge）。
- **研究者の選択（推奨どおり）**: main の D6 を保ち、この枝の項を **D7** に付け直す。`deviations.md`（冒頭の文に D7 を足し、D6 の後に D7）・`data.windows.md`（「deviation D7」）・`method.tex`（本文・逸脱の表に D6 を足し D7 に・「七つの逸脱」）・`outline.md`（§5.7・§5.9・AG7）を直した。Windows の次の逸脱は **D8 から**（引き継ぎに書く）。
- **あわせて直したこと（メイン）**: `method.tex` の「各機械で別々の晩に測った」は macOS で D6 により事実と違う → 「決まった順で測った・登録は別々の晩を求める・macOS は D6」に直し、Windows の晩の扱いは \tbd（Windows 側で研究者の判断待ち）。
- **台帳**: `.codex/budget.json` は自動で混ざったが、この枝は台帳を触っておらず、取り込んだ結果は main と同じ（差分 0）。二重計上なし。

## 判断 153: 結果を待たない 4 節の事実の照合（指摘 17 件はすべて真）を反映し、macOS の版を記録から埋め、書誌 44 件を登録する（2026-10-05・G-GEAR・メインの選択・研究者が覆せる）

- **照合**: `ee54bcbe` の 4 節（`related.tex`・`observability.tex`・`logger.tex`・`dataset.tex`）を、独立のサブエージェント（Opus・読み取りだけ・取得した一次の文書のテキスト・ロガーのソース・凍結物だけを読む）に照合させた（約 9 分）。指摘 17 件を一次で裏取りし、**すべて真**（偽陽性 0）。主なもの: (1) AppKit の定数の数は各一覧の `init(rawValue:)` を除くと **属性 131・パラメータ付き 18・通知 42**（判断 151 の 132 / 19 / 43 は誤り・C の 101 / 9 / 25 は正しい）。(2) 押下の記録（oracle）はキー名でありキーコードではない。(3) 「計測では観測するキーの外のキーを送っていない」は誤り（ランナーがブロックの前に押すかなキーと S14 の入力モードのキーがある）・事前登録 §1.1 は解放に触れていないのであって「押下だけ」と書いてはいない。(4) Accessible Event Watcher の勧めはイベント定数の頁の全イベントに掛かる → アプリしだいの根拠は TextEdit パターンの頁だけにした。(5) TSF の頁は「in-proc server」としか言わない → 「入力方式を置き換える」を削った。(6)〜(17) IMM の「自分の窓」・XP 時代の MSAA の記述・コールバックの引数（フックの handle）・ウィンドウ一覧の情報・Table 2 の 2 行・宇都ら（2020）の執筆言語は明記なし・Monaco の主張の範囲（英単語）・CyWrite の「タグ付きのリリースなし」・ScriptLog の頁は 2003 年更新で現行版は開発者から入手（Wengelin & Johansson 2023）・Table 3 の閉じの条件・Tappy の空白キーの印・梱包が拒むリポジトリのパス。→ すべて直した（25 か所）。
- **照合で読んでいない範囲**（報告どおり）: 不在の主張（「文書に無い」）は全文の一覧が無いので確かめられない → 原稿は「調べた文書には無い」と書いた。Whiskerd らは注釈まで。`carl2012.txt` は読まれていない。
- **macOS の版**: main に入った `env.md`（PR #297）の記録から、`method.tex` と `observability.tex` の \tbd を「macOS 27.0.1（build 26A434）・ローマ字入力の版 6.3」で埋めた。外枠の Open items の SDK の確認も「27.0.1」と名指した。
- **書誌**: `docs/references.md` に **[V192]〜[V235]**（文献 8・道具の頁 6・WebKit のソース 1・Microsoft の文書 16・Apple の文書 12・SDK のヘッダ 1）を append。`references.bib` に 30 件（文書 29 ＋ WebKit）を足した（文献と道具は `ee54bcbe` で 25 件）。各文書は Wayback の写し（2026-10-05 01:22〜02:01 UTC）・最終更新日・取得日を注に持つ。生成は scratchpad の台帳から（手で写していない）。`check_citations.py` 違反なし・原稿の引用キー 67 / 67 が書誌にある。
- **影響範囲**: 4 節・`method.tex`・`outline.md`・`manuscript-map.md`・`docs/references.md`・`references.bib`。

## 判断 154: GSE 本体の訂正は別の枝で出し（PR #305）、LaTeX を入れて原稿と補遺を組めるようにする —— 雛形は公開物に入れず取得の手順と組む道具を置く（2026-10-05・G-GEAR・メインの選択・研究者が覆せる）

- **GSE 本体の訂正（引き継ぎ §2 の 0・判断 151-2）**: `main` から枝 `docs/macos-ax-marked-text-correction`（worktree `C:/wt/macos-ax-correction`）を切り、`.steering/20261005-macos-ax-marked-text-correction/` に記録した。`docs/agent-shared.md` 制約 7・`docs/architecture.md`・`docs/architecture/workspace-behavior-observation.md`・調査メモ §3.2・§7.5・§7.6 を「アプリを問わずに変換を知らせる公開の通知は見つかっていない・アプリが用意する経路はある」に直した（PR #305）。完了時レビュー（code-reviewer ∥ security-checker ＋ Codex 2 巡）の指摘はすべて一次で裏取りして直した。★ この論文に効く見つけたこと 2 つ:
  1. ⚠️ **`kit/logger/src/input/ime_compose.rs` は GSE の `src-tauri/src/input/ime_compose.rs` の逐語コピー**（`PROVENANCE.internal.md`「1 バイトも変えない」・`manifest.json` の SHA-256・`check_manifest_upstream.internal.py --against-upstream` が作業ツリーの上流と照合）。上流のコメント（16 行「公開 API が無い」）を直すと照合が赤になるので、**上流は直さなかった**。照合を凍結の commit に固定すれば上流を直せる（Codex の指摘）→ 研究者の判断待ち。kit の写しのコメントは公開物に残る（凍結物なので変えない）。
  2. WebKit は同じ commit で `AXObjectCache.cpp` 3692〜3719 行（`onTextCompositionChange`・`HAVE(INLINE_PREDICTIONS)` の条件つきで、`PlatformHave.h` 1326〜1331 行が Mac で 1）から 2 つの通知を投げ、`AXObjectCacheMac.mm` 375 行が userInfo `nil` で出す。→ 原稿の §3 の「WebKit が出す」は、発火の経路までソースで言える（実機で別のプロセスが受け取れるかは確かめていない）。§3 の文と [V206] の注に足すかは原稿の段で決める。
- **LaTeX の導入（引き継ぎ §2 の 1・研究者の許可 2026-10-05）**: `winget` で MiKTeX 25.12 をユーザーの領域に入れ（管理者権限なし）、パッケージの自動取得を有効にした。Springer Nature の雛形は 2024 年 12 月版の ZIP（901,814 バイト・SHA-256 `812e76dc…ecae`）を `https://cms-resources.apps.public.k8s.springernature.io/springer-cms/rest/v1/content/18782940/data/v12`（LaTeX author support の頁のリンク）から取得し、**公開物の外**（`C:\Users\johnd\tools\sn-template\`）に置いた。
  - ★ **判断 147 (b) の答え**: `sn-jnl.cls` の頭は LPPL 1.3c と「This file may only be distributed together with a copy of the LaTeX base system」（LaTeX の基本の `classes.dtx` から生成した旨）を書く → CC BY 4.0 の公開物には**入れない**。取得の手順を `manuscript/BUILD.md` に、組む道具を `manuscript/build.sh`（雛形の場所と出力の場所を引数に取り、ソースの横に何も書かない）に置いた。
  - **直したこと**: (1) `main.tex` に `amsmath`（クラスが文書の始めで `\allowdisplaybreaks` を呼ぶ・雛形の見本も読む）・`graphicx`・`array`・`[T1]{fontenc}`・`lmodern`。(2) 雛形の APA の書式は `url` の欄を素の文字で出すので、URL の下線でコンパイルが止まった → `APACrefURL` の環境を `\url` に渡すよう定義し直した（試しの文書で確かめた）。(3) 表の列を「列の間の余白を含む比率」の列型 `L{}` にし、各表の比率の和を 1 以下にした（はみ出し 4 件 → 0）。Table 1・2 は高さがページを 516 pt・354 pt 超えていた → 雛形の勧めどおり `sidewaystable`。他の `table*` は 1 段組なので `table`（雛形の表の字の大きさになる）。(4) 書誌: APA の文の頭だけ大文字にする規則で固有名詞が小文字になっていた（"Aozora bunko"・"2018 ieee symposium on security and privacy (sp)" など 10 か所）→ 括弧で守った。会議録の論文に雛形の書式は DOI を出さない（`fin.entry` の DOI がコメントアウトされている）→ 2 件は DOI を note にも書いた。Dhakal らの "p. Paper 646" を note の "Paper 646" にした。(5) 栞は小節までにした（段落の見出しで出ていた警告 6 件）。(6) 補遺の文書一覧を組む `supplement/supplement.tex` を足し、一覧の冒頭の閉じ引用符の欠けを直した。
  - **結果**: `main.pdf` 38 頁・エラー 0・未定義の参照は引き継ぎの 4 つ（`fig:components`・`sec:availability`・`sec:limitations`・`sec:results-attempts`）だけ・横のはみ出し 0・縦のはみ出し 2（9・10 頁・4 pt・脚注の頁）。`supplement.pdf` 5 頁・エラー 0（URL の列に数 pt のはみ出し）。表 1・参考文献の頁は画像にして目で確かめた。`_style_check.py` 違反 0。
  - ⚠️ **残したこと**: 雛形の APA の書式は 3 人以上の著者で最後の著者の前に "&" を出さない・会議録の DOI を出さない（出版社の書式なので `.bst` は変えない）。OSF の 2 つの登録の著者は `TODO` のまま（研究者の名の書き方を確かめてから）。BRM の投稿は ScholarOne なので、`.tex` を 1 本にまとめるか・雛形のファイルを上げるかは投稿の段で確かめる（判断 147 の追記）。
- **影響範囲**: `manuscript/main.tex`・`sections/related.tex`・`observability.tex`・`logger.tex`・`method.tex`・`dataset.tex`・`references.bib`・`supplement/observability-documents.tex`・新規 `supplement/supplement.tex`・`BUILD.md`・`build.sh`。

## 判断 155: 問 4 の閉じた集合は S12 の試行をすべて外す（逸脱 D8）・Windows の run の日時を逸脱 D9 にする・この枝の PR は結果の節の後に出す（2026-10-05・G-GEAR・研究者の選択）

- **背景**: 引き継ぎ §2 の 3（研究者の判断待ち）。Windows の閉じた集合は凍結のコードで止まっていた（`next-session-ime-paper-m7-windows.md` §2.11）。
- ★ **メインが一次で確かめたこと**: (1) 事前登録 §6.8（864〜868 行）は「S12 の試行は数えない・ライブ変換 ON 2,925・OFF 2,700」、§10.7（1326〜1331 行）は「S12 を除いて 2,700」。凍結の `closed_set.py` の `evaluate()` は「コーパスに無い句」の試行だけを外す（`used = [t for t in trials if t["phrase_id"] in by_id]`）。(2) 計画の生成器はかなのシナリオに、かなで打てるコーパスの句を先に使い切ってから生成したかな文字列を当てる（`generate_plan.py` 580〜592 行）。(3) ★ **3 つの計画を凍結のタグから再生成**（`git archive` → `generate_plan.py --seed 20260929`）し、登録の SHA-256（`c7a5469d…`・`3759ebf7…`・`b7bdf8fc…`）と一致した。どの計画も S12 は 225 試行で、そのうち 74 がコーパスの句（74 句すべて別）→ **macOS の 2 セルも同じ欠陥で止まる**。登録の数（3,150 − 225 = 2,925・2,925 − 225 = 2,700）は S12 をすべて外した数。(4) 開いた集合はシナリオで S12 を外していて（`open_set.py` 82 行）欠陥は無い。(5) Windows の E3 は `idle` が 10-04 13:16〜21:16（本計測の終わった日の昼）、`working` が 21:29〜10-05 08:35。登録 §10.8（1376〜1377 行）は「別々の夜に、この順で」。(6) 01:51 の拒否された開始は D7 が既に扱っている（照合済み・引き継ぎ §2 の 3）。
- **研究者の選択（3 問とも推奨どおり）**:
  1. **閉じた集合は S12 の試行をすべて外す**（逸脱 **D8**・3 セルとも）。
  2. **Windows の run の日時を逸脱として記録**（**D9**・macOS の D6 と同じ形）。
  3. **この枝の PR は結果の節の後に出す**（いまは push だけ・完了時レビューは結果の節と D8・D9 を足してから 1 回）。
- **実装（メインの選択・研究者が覆せる）**:
  - `kit/e2/closed_set.py` に **`--skip-scenario S`**（繰り返し可・既定なし）を足した。試行を計画に合わせた**後**で外すので、`alignment` と `n_trials` は計画の全体のまま、出力に `skipped_scenarios`（シナリオごとの数）を足す。⚠️ 既定（スイッチなし）の出力は凍結のコードと同じ（出力の辞書に鍵を足すのはスイッチがあるときだけ・候補は試行ごとの種から引くので他の試行の引きは変わらない〔`_sub_seed(tseed, "cand")`〕）。`evaluate()` は変えていない（selftest の S12 を含む検査がそのまま通る）。名前の検査（`S[1-9][0-9]*`・二重の指定を拒む）。selftest に 6 件（スイッチなしで鍵が無い・S2 を外す・計画に無い S12 は 0・名前の拒否・二重の拒否）→ **157 / 157**。★ 変異 3 本（外さない・鍵を常に書く・名前の検査を外す）はどれも selftest を赤にし、無変異の写しは緑（対照）。`kit/e2/README.md` に使い方。
  - `experiment/deviations.md` に **D8**（理由・3 計画の再生成と 74 / 225・効果）と **D9**（時刻・順と重なりなし）。冒頭の文に D8・D9。
  - `manuscript/sections/method.tex`: Windows の日時の `\tbd` を D9 の文で埋め、逸脱の表に D8・D9、「Nine deviations」。`outline.md` の §5.9 を「D1 to D9」に。
- ⚠️ **残り（次の作業）**: 閉じた集合を回すのは計測の機械（Windows = Surface の `experiment/runs/windows-msime-tsf-2`・macOS = Mac）。命令は §6.8・§10.7 のものに `--skip-scenario S12` を足し、`kit/e2/closed_set.py` だけこの commit のもの、他は各 OS の凍結のタグの書き出し。macOS の問 1〜4 もまだ回っていない。
- **影響範囲**: `kit/e2/closed_set.py`・`kit/e2/README.md`・`experiment/deviations.md`・`manuscript/sections/method.tex`・`manuscript/outline.md`。

## 判断 156: 結果の表と本文の値は `manuscript/tools/results_tables.py` が結果の JSON から生成し、原稿は `\rv{<key>}` で読む（2026-10-05・G-GEAR・メインの選択・研究者が覆せる）

- **背景**: 引き継ぎ §2 の 2（「結果の値は結果の JSON からスクリプトで写す・手で写さない」・要旨は外枠の「Rule for the abstract」）。まず Windows の結果で作る。
- **道具**: `manuscript/tools/results_tables.py`（標準ライブラリだけ）。`experiment/results/`（macOS の 2 セル・まだ無い）と `results/windows/` の `e1_detection.json`・`e1_l1.json`・`e1_l2.json` を読み、`manuscript/generated/` に 5 つを書く: `values.json`（全桁の値と出どころ〔ファイルと JSON の中の道筋〕）・`values.tex`（整形した値・原稿は `\rv{<key>}` で読み、無い鍵は `\tbd` で出る）・`table-detection.tex`（表 8: セル × 速さ、30 試行以上の層の Wilson 区間の最小の下端〜最大の上端、主の範囲と全試行）・`table-session.tex`（表 9: セル × 速さの滞在の偏り〔区間〕・一致の限界・中央値の絶対差・`abandon` の一致と κ・`nav` の完全一致・横向き）・`detection-strata.tex`（補遺: 層ごとの検出・範囲ごとに横向きの長い表・測っていないセルを名指す）。`--check` は書かずに比べて違えば exit 1（`build.sh` が最初に回す）。
- ★ **要旨の規則の写し方**: (i) 主の範囲の層ごとの「残った試行」は `e1_l2.json` の `per_trial.by_stratum[].n_trials`（検出の JSON は層の試行数を持たない）。層の数は計画の層（13 シナリオ × 3 速さ = 39）。範囲は 30 試行以上かつ再現率・適合率の区間がある層だけ。外した割合は `trials_not_used.out_of_scope` と検出の `excluded.trials.by_type.carry_over` を総試行（層の試行・除外・未実施・範囲外の和）で割る。(ii) `dwell_ms` の偏りは `e1_l1.json` の `metrics.by_speed[].dwell.bias_ci` の範囲。(iii) 推奨と (iv) CPU は閉じた集合と E3 の結果ファイルが来てから足す。
- **書式**: 割合は小数 3 桁・ms は整数（Python の丸め）・`values.json` は丸めない値を持つ。⚠️ 引き継ぎの「丸めない」は「手で丸めない」と読んだ（本文に 16 桁を出さない）—— 研究者が覆せる。
- **Windows の値（生成物から・主 = `windows_def`・`gt_obs`・`under_limit`）**: 再現率の範囲 0.412–1.000・適合率 0.321–1.000（36 層・外した層 3 = S13 の 3 速さ〔主の範囲で試行 0〕）、範囲が外した試行 617 / 2,925（21.1%）・carry-over 2 / 2,925（0.1%）、全試行では 39 層で再現率・適合率とも 0.000–1.000、滞在の偏りの区間の範囲 −1,121〜−456 ms（全試行 −1,916〜−535 ms）。⚠️ 解釈はまだ書かない（結果の節の段・macOS の後）。
- **検証**: selftest 18 件（合成の結果ファイル: 30 試行ちょうどの層は入り 29 は外れる・範囲・割合・ms の符号・出どころ・層の表の「試行なし」・決定的・`--check` の陽性と陰性 2 つ・主の範囲が違うと止まる・結果ファイルが無いとき）。★ 変異 5 本（`>=` を `>` に・範囲を区間でなく値から・`--check` が常に通る・主の検査を外す・総試行から範囲外を落とす）はどれも狙った検査で赤、無変異の写しは緑。生成した表を雛形で組んで画像で確かめた（`build.sh` で `main.pdf`・`supplement.pdf` ともエラー 0）。
- **配線**: `main.tex` に `\rv` と `\input{generated/values}`、補遺に `pdflscape` と層ごとの表。`BUILD.md` に生成と `--check` の手順。
- **影響範囲**: 新規 `manuscript/tools/results_tables.py`・`manuscript/generated/`（5 ファイル）・`main.tex`・`supplement/supplement.tex`・`build.sh`・`BUILD.md`。

## 判断 157: macOS の問 1〜3 が凍結のコードの欠陥で止まった —— 逸脱 D10 で「登録の解析（分子 > 分母は値なし）」と「直した解析（数え直した併合を対の観測の層に）」の両方を回す（2026-10-05・Mac・研究者の選択）

- **起きたこと**: 引き継ぎ `next-session-ime-paper-mac-analysis.md` §2 の 4 の命令（macOS のタグの書き出し `~/ime-m4/export-ff122e32`）が **exit 2**（`pipeline: x and n must be integers with 0 <= x <= n`）・結果のファイルは 1 つも書かれていない。原因を 1 回だけ見た（凍結のコードは変えずに `stats` の関数を外から包んでスタックを出した）: `match.evaluate` → `_layer_metrics`（`diagnostics.prediction_layers`・予測の層 × 速さ）→ `_metrics_row` の `merge_rate` = `_prop(merge_obs + merge_obs_recount, n_obs)` で **27 / 18**。
- **原因（コードで確かめた・`match.py` の `detection_metrics`）**: θ の数え直しの併合（`rc["merge"]` の `{"gt": 取り残された正解, "obs": 既に対になっている観測}`）を `st = gl(e["gt"])`（**取り残された正解の層**）に数えるが、分母 `n_obs` は観測を**その対の正解の層**で数える（`pairs` は `gl(p["gt"])`）。層が違うと分子だけが別の層に入る。分割の数え直しは対の正解の層（`gl(e["gt"])` の `e["gt"]` は対の正解）で分母と同じ側 → 非対称。予測の層は層の外の観測を `None` に落とすので分母が小さく、超えた。Windows は予測の層を計算しない（D3）ので止まらなかった。主の層（シナリオ × 速さ）でも試行をまたぐ併合があれば分子がずれうる（止まらないだけ）。
- **研究者の選択（2 問）**: (1) 欠陥の扱い → **ここで D10 の方針を立てる**（推奨）。採らなかった: G-GEAR に戻す・すべて止める。(2) 直し方 → **両方回す**（推奨）: ① 分子 > 分母の割合は値と区間なし＋注、それ以外は凍結のコードと同じ → **登録の解析**として報告 ② `IME_MATCH_MERGE_RECOUNT=obs` で数え直した併合を対の観測の層に数える → **直した解析**として横に並べる（§8）。Windows のセルも ② で回し直す（Surface / G-GEAR）。採らなかった: ① だけ・② だけ。⚠️ 選んだ時点で問 1〜3 の結果は誰も見ていない。⚠️ ただし直す途中で、問 4 の開いた集合のログの末尾（CER の数値の数行）がメインの画面に出た —— D10 の選択（問 1〜3 の数え方）より後で、選択には関わらない。
- **実装（commit `115cd5ff`・`kit/analysis/match.py` だけ・pipeline・設定・規則のファイルは変えない）**: `_prop` の防御・`merge_recount_mode()`（環境変数・`gt` / `obs`・ほかは InputError）・`obs` のとき `paired_gt[id(e["obs"])]` の層へ（`n_miss_as_merge` は正解の層のまま）・`evaluate` の `config` に `merge_recount` を `obs` のときだけ足す（凍結の形を保つ）。⚠️ スイッチを環境変数にしたのは、pipeline が match に渡す設定のキーが固定（`config.json` は凍結のハッシュの対象）で、pipeline を変えると macOS のタグと今の枝で中身が違う（D2〜D4）から。`match.py` はタグと枝でバイト一致。
- **検証**: match の selftest 18 件（新しい `_case_d10`: 層をまたぐ併合で ① は 1 / 0 を値なし＋注・② は対の層に 1 / 1・単一の層は両方で同じ・不正な値は拒否・`_prop(1, 2)` は区間を保つ）。★ 変異 3 本（防御を外す・`obs` の分岐を外す・防御を `<=` に）→ すべて赤。pipeline の selftest 13 件。★ **合成の run**（`--synthetic --seed 4`・`--seed 7`・`bootstrap_B` 2000・`gt_rules.example.json`）で **スイッチなしの 4 ファイルがタグとバイト一致**・スイッチありは delivery 以外の 3 ファイルが変わり `merge_recount` 36 か所。
- **影響範囲**: `kit/analysis/match.py`・`experiment/deviations.md`（D10）・結果は `experiment/results/`（登録）と `experiment/results/d10/macos/`（直した）。⚠️ Windows の ② は未実施（Surface / G-GEAR へ）。`results_tables.py` が `results/d10/` を読むかは G-GEAR が決める。

## 判断 158: macOS 27 の SDK のヘッダを数え直した —— AppKit は文書と一致、C の Accessibility は文書より多いが marked text の定数は無い、入力ソースのヘッダは入力ソースと入力モードだけ（2026-10-05・Mac・メインの確認）

- **SDK**: `xcrun --show-sdk-path` = Command Line Tools の `MacOSX.sdk`・`--show-sdk-version` **27.0**・build **26A425**（`CLTools_Executables` 27.0.0.0.1788430756）。⚠️ 機械の OS は 27.0.1（26A434）で、SDK の版とは別。
- **(a) AppKit `NSAccessibilityConstants.h`**（SHA-256 先頭 `bef307f721603f6b`）: 1 行 1 宣言を確かめたうえで `grep -c "NSAccessibilityAttributeName const"` **131**・`"NSAccessibilityParameterizedAttributeName const"` **18**・`"NSAccessibilityNotificationName const"` **42** → **判断 153 の数（文書の一覧から `init(rawValue:)` を除いた数）と一致**。`NSAccessibilityTextInputMarkedRangeAttribute`（96 行・macos(10.6)）・`NSAccessibilityTextInputMarkingSessionBeganNotification` / `…EndedNotification`（466・467 行・macos(10.6)）が**ある**。
- **(b) C `AXAttributeConstants.h`（`5734d01bc751983b`）・`AXNotificationConstants.h`（`204847bb5e78d75a`）**（HIServices）: python で `#define kAX…` を名前の末尾で分類 → `…Attribute` **138**（値の文字列で 137 種）・`…ParameterizedAttribute` **14**・`…Notification` **37**（ほか 1 と 4）。⚠️ **判断 153 の 101 / 9 / 25 と一致しない**（文書の一覧はヘッダの部分集合で、数え方の差は未調査）。marked text・text input・composition を表す定数は**無い**（`marked` に当たるのはコメントの "marked as focused" の 1 か所だけ・名前に text / input / select / range を含む定数は選択・可視範囲・行・セルの類）。→ 原稿の「C の定数に marked text は無い」は数の差に関わらず保たれる。数を書くなら「SDK 27.0 のヘッダで 138 / 14 / 37」と出どころを添える。
- **(c) `TextInputSources.h`（HIToolbox・`e3c1a70e0cb8e214`・© 2006-2008）**: ⚠️ **ISO-8859 で書かれていて grep が黙って空を返した**（memory「ugrep は非 UTF-8 で黙って空」と同じ型）→ latin-1 で読み直した。関数 16（`TISCopyCurrentKeyboardInputSource` ほか・入力ソースの選択・有効化・プロパティ）・定数 27（`kTISProperty…` 15・`kTISNotify…` 2・`kTISCategory…` 3・`kTISType…` 7）。`marked` / `composition` / `convers` / `candidate` / `inline` は 0 件 → **入力ソースと入力モードだけで、11.3 の写しで読んだことと変わらない**。
- **影響範囲**: 原稿の文（`observability.tex`）は G-GEAR が直す。この判断は数と数え方の記録だけ。

## 判断 159: macOS の 2 セルを書庫にして解析した（問 1〜5）—— 結果の表の道具は分母 0 の層で落ちたので直さず G-GEAR に戻す（2026-10-05・Mac・メインの実行・研究者が覆せる）

- **書庫**（`data.md` の手順 4〜5・書き出し `~/ime-m4/export-ff122e32`・一覧 `29b183ba…6c49` を再確認）: `pipeline.py --pack` を ON / OFF に（`--also-user` / `--also-home` を 1 つずつ・値は書かない）→ ON `77bd8a8e…49b8`（74,044,861 B）・OFF `e1cdf2e8…3d10`（66,091,676 B）。⚠️ zsh で `PIPESTATUS` が空だったので、同じ命令を一時の場所へもう一度 → **どちらも exit 0・バイト一致**。書庫は `~/ime-m4/deposit/`（git に入れない・OSF への寄託は研究者）。`e3-working-run` は書庫にしない（外枠の Open items）。
- **展開**: `experiment/runs/macos-standard-live-{on,off}-1`（gitignore）・`run.json` の SHA-256 が元の run と一致 → `data.md` に `run_dir` の 2 行・Deposits・Machine の表。
- **問 1〜3**: 判断 157（D10）のとおり 2 本 → どちらも exit 0・「2 run(s), 0 aborted, 2 analysed」。登録の側で D10 の注（値なし）は **32 か所・すべて `diagnostics.prediction_layers` の `received_carry` 層の速さごとの merge_rate**（主の `by_stratum` には 0）。直した側は注 0・`merge_recount: obs` 36 か所。`e1_delivery.json` は両方で同じバイト。
- **問 4**: 開いた集合 ON / OFF exit 0。閉じた集合（D8・`export-d8`・`14c85e6e` の `closed_set.py`・selftest 157 OK）ON / OFF exit 0・`skipped_scenarios` `{"S12": 225}`・`n_trials` ON 3,150 / OFF 2,925・各 K と特徴量の `n` ON 2,925 / OFF 2,700・`n_skipped` 0・採点されないブロック 0。推奨（§6.8 の判定）は読んでいない・書かない。
- **問 5**: `samples.tsv` の SHA が M4 の記録と一致 → `results/e3_macos.txt`（両方 `measured`・パスなし）。
- **出力の SHA-256 と命令**は `data.md` の新しい節「Analysis of the macOS cells」。結果のファイルにホームのパスが無いことを確かめた。
- ⚠️ **結果の表（§2 の 9）は生成できなかった**: `manuscript/tools/results_tables.py` が `fmt_p(None)` で `TypeError`（`table_strata`・主の層の表の split / merge rate）。該当は**分母が 0 の層**（OFF の `all_trials` の S13 の fast / slow は観測の行 0 → `merge_rate` と `precision` の値が None。どちらのセルも `(None, None)` の層は `recall` / `split_rate` が n = 0）—— 凍結のコードの元からの振る舞いで **D10 とは無関係**。表の道具は G-GEAR の持ち物（判断 156）で空欄の書き方は原稿の選択なので**直していない**。`manuscript/generated/` は書き換わっていない。⚠️ 予測の層の表を道具が読むなら、D10 の注（値なし）も同じく None で来る。
- ⚠️ 表示した値: 問 4 の開いた集合のログの末尾（数行の CER）が一度画面に出た（判断 157）。問 1〜3 の率・問 4 の推奨は見ていない。
- **出荷の記録（前のセッションの残り）**: PR #297（M4 の記録・D6）→ merge `9cedba6c` → main の CI は #304 の merge に取り消され、`cf320319` の main の CI（run 37253171494）が success。

## 判断 161: Windows の閉じた集合（D8 のスイッチ付き）と E3 の要約を Surface で回し、結果の JSON と記録を枝 `docs/ime-m8-windows-closed-set` に置く（2026-10-05・Surface・メインの選択・研究者が覆せる）

- **背景**: `next-session-ime-paper-surface-d8.md` §2。新しい計測はしない・凍結のコードと事前登録は変えない（D8 の `closed_set.py` だけ commit `14c85e6e` のものに差し替え）。
- **実行**: 入力の SHA-256 は計画・観測とも引き継ぎの値と一致。`export-d8`（書き出しの写し）で selftest OK（157 checks）・LF のまま。閉じた集合は `Start-Process` の独立プロセスで約 2 時間 40 分・exit 0・標準エラー空。`skipped_scenarios` `{"S12": 225}`・`n_trials` 2,925・全 K・全特徴量で `n` 2,700・`n_skipped` 0。出力 SHA-256 `93b5eb2b…38b7`。E3 は両方 measured・working の `cpu_all_zero` false。
- **前の引き継ぎの残り**: (a) 試み 2 の間の計測機の記録を `data.windows.md` に 1 段落（Defender の定義更新 1 件・電源サービスのイベント 11 件・再起動なし。タスクスケジューラのログは無効で、Claude Code のセッションは読んでいない → 「何も動かなかった」とは言わない）。(b) §10.8 の点検の計画の SHA-256 を全桁に（点検の run の manifest の `plan_sha256`）。
- **結果は読んでいない**: チャンスとの比較（§6.8）は結果の節で G-GEAR が書く。
- ⚠️ **手順の注意**: Windows の PowerShell に渡す `-File` のパスは `cygpath -w`。`git -C` に MSYS パス（`/c/...`）は渡せない（`C:/...`）。`grep -c $'\r'` はこのシェルで当てにならず、Python で数えた（CR 0）。
- **影響範囲**: `results/windows/e2_closed_set_windows-msime-tsf.json`・`results/windows/e3_windows.txt`・`data.windows.md`・本ファイル。

## 判断 165: Mac と Surface の解析を論文の枝に取り込み、結果の表の道具を値なしと測度ごとの層に対応させ、§3 に SDK 27.0 のヘッダの数を書き、`build.sh` の書誌の欠陥を直す（2026-10-05・G-GEAR・メインの選択・研究者が覆せる）

- **取り込み**: `origin/docs/ime-m8-macos-analysis`（判断 157〜159・逸脱 D10・`match.py`・macOS の問 1〜5 の結果）と `origin/docs/ime-m8-windows-closed-set`（判断 161・Windows の閉じた集合・E3 の要約）を merge（`a56b17e1`・`d889f45f`）。衝突は `decisions.md` の末尾の追記だけ（157〜159 の後に 161 を並べた）。番号の割り当て（Mac 157〜160・Surface 161〜164・G-GEAR 165〜）のとおりで、160・162〜164 は欠番。
- ★ **D10 の Windows の直した解析はまだ**（判断 157 の (2)・`deviations.md` D10 は「macOS と Windows の両方で横に並べる」）。Windows の run のデータは Surface にしか無い。`match.py` は 2 つのタグでバイト一致（`git diff ime-observation-prereg-macos ime-observation-prereg-windows -- …/match.py` が空）で、`115cd5ff` が変えたのは `match.py` だけ → Surface で Windows のタグの書き出しの写しに差し替えて回せる（引き継ぎ `next-session-ime-paper-surface-d10.md`）。
- **結果の表の道具**（判断 156 の直し・Mac の判断 159 で落ちた）: (1) 値の無い割合（分母 0・D10 の値なし）を `--` で出す（`fmt_p`・`est_ci`）。(2) ★ **要旨の規則の層は測度ごとに数える**: 規則の文「strata with fewer trials or no value」は測度ごとに読むのが文どおり。以前は再現率と適合率の両方に値がある層だけを入れていたので、観測の行が 0 で適合率が値なしの層（macOS OFF の全試行の S13）が、再現率 0 でも再現率の範囲から落ちていた。→ `strata_in_range(kept, strata, keys, measure)`・鍵は `<cell>.<scope>.<measure>.strata.used|left`・表 8 は測度ごとに「範囲（層の数/全層）」。⚠️ この直しは Mac の報告（値なしの層の形）を読んで決め、結果の値を出す前に入れた（値を見てから規則を変えていない）。selftest 19 件・★ 変異 7 本（`>` に・測度をまとめる・値なしで落ちる・値から範囲・`--check` が常に通る・主の検査を外す・総試行から範囲外を落とす）はどれも赤、無変異は緑。
- **3 セルの生成**: `values.json` の `cells` は 3 つ（`macos-standard-live-on`・`-off`・`windows-msime-tsf`）。⚠️ 生成のときに要旨の (i)(ii) の値が画面に出た（区間の範囲・外した割合）。結果の解釈は書いていない。macOS ON の層は 14 シナリオ × 3 速さ。
- **§3 と SDK**（判断 158）: `observability.tex` に「C の定数は文書の一覧で 101・9・25、macOS 27.0 の SDK のヘッダでは名前の末尾で数えて 138・14・37、どちらも marked text の定数なし」「AppKit は文書とヘッダで同じ 131・18・42」「入力ソースのヘッダは 27.0 でも composition を表すものなし」を足した。出典は新しく **[V236]**（`docs/references.md`・`references.bib` の `apple-sdk-27`・公開の URL は無い・ヘッダの SHA-256 の先頭を記録）。補遺の文書一覧の前書きと外枠の Open items（済み）も直した。`check_citations.py` 違反なし。
- ★ **`build.sh` の欠陥（判断 154 の記録の訂正）**: Windows の git-bash では `BIBINPUTS` に MSYS 形式のパス（`/c/…`）が入り、BibTeX が原稿の `references.bib` を見つけられず（別の同名のファイルを読み）、引用がすべて未定義になっていた。完了表示は `LaTeX Warning: Reference` だけを数えていて、natbib の「Citation … undefined」を数えていなかった → 見逃した。⚠️ 判断 154 の「未定義の参照は 4 つだけ」は手で組んだ版（`pwd -W` を使った）の事実で、`build.sh` の版には当たらなかった。→ Windows では `pwd -W` で渡し、完了表示に「undefined citations」を足した。直した後: 書誌 68 件・引用の未定義 0・参照の未定義は 4 つのラベルだけ。
- **公開物の文体**: Surface が `data.windows.md` に書いた内部の番号（「the record of M7」）を `_style_check.py` が赤にした → 「as when the runs ended」に直した（違反 0）。
- **影響範囲**: `manuscript/tools/results_tables.py`・`manuscript/generated/`・`build.sh`・`sections/observability.tex`・`references.bib`・`supplement/observability-documents.tex`・`outline.md`・`experiment/data.windows.md`・`docs/references.md`。

## 判断 166: Windows のセルの直した解析（逸脱 D10）を G-GEAR で回した —— 登録の解析は 2 台目の機械でもバイト一致、直した解析は併合の率とその分子だけが変わる（2026-10-05・G-GEAR・メインの実行・研究者が覆せる）

- **背景**: 判断 157 の (2)（Windows のセルも ② で回し直す）と判断 165 の残り。研究者の提案で Surface の代わりに G-GEAR で回した（引き継ぎ `next-session-ime-paper-ggear-d10.md`）。新しい計測はしない・凍結のタグのコードと事前登録は変えない・封印は開けない。
- **入力**（このセッションで測り直した）: 書庫 `Downloads\windows-msime-tsf-2.zip` `f2287a74…cd06`（`data.windows.md` の Deposits と一致）。展開済みの `experiment/runs/windows-msime-tsf-2`（gitignore を `check-ignore` で確認）の `run.json` `5c74a1fa…3d82`・`plan.jsonl` `b7bdf8fc…36b0`・`obs.jsonl` `58f0bda6…2562` が記録と一致。G-GEAR は Python 3.11.9（Ryzen 7 9700X・Windows 11 Home 26300）。
- **手順 1（書き出し）**: `git -c core.autocrlf=false worktree add --detach <scratch>/wt-win ime-observation-prereg-windows`（`a57c4fd7`）→ `export.internal.py --out <scratch>/export-win --allow-missing-license` exit 0・108 ファイル。一覧（§9 の形を Python で作り直した）の SHA-256 `f61af353…87b7` で、`freeze-export-list-windows.txt` と**バイト一致**。
- **手順 2（D10 の `match.py`）**: `export-d10` に写して `115cd5ff` の `match.py`（`6f817228…`・CR 0）に差し替え。タグとの差は D10 の 3 点（`_prop` の防御・`merge_recount_mode()` と `obs` の分岐・`config` の `merge_recount`・selftest `_case_d10`）だけを diff で確認。⚠️ `115cd5ff` は `deviations.md` も変えている（文書・コードは `match.py` だけ）。書き出しは `match.py` を変えない（書き出しの `match.py` がタグの git のバイトと同じ `66881f86…`）ので、差し替えは「`115cd5ff` の書き出し」と同じ。selftest は match 18 件・pipeline 13 件 OK。
- **手順 3（登録の解析の再現）**: 環境変数なし・`--out <scratch>/check-registered` → exit 0（約 2 分）・「1 run(s), 0 aborted, 1 analysed」・標準エラー空・**4 ファイルとも `results/windows/e1_*.json` とバイト一致**（Surface と G-GEAR・同じ Python 3.11.9）。→ D10 の変更 1 は Windows の登録の結果を変えない。`data.windows.md` に節を足した後にもう一度回して、4 ファイルがバイト一致（追記が `--runs-from` の読みを変えないこと）。
- **手順 4（直した解析）**: `IME_MATCH_MERGE_RECOUNT=obs`・`--out experiment/results/d10/windows`（無い場所・スクリプトで存在を確かめてから）→ exit 0・1 run・中止 0・標準エラー空。SHA-256: delivery `1c4e5cf2…f321`（登録と同じ）・detection `1ae79137…13ab`・l1 `ea8d22ea…878e`・l2 `b29a159e…a261`。
- **手順 5（突き合わせ・値は出さずに形と数だけ）**: delivery はバイト一致。detection は全範囲で層の数と並び・合算（pooled）が同じ。層ごとの precision・recall・F1・split_rate・miss_rate・false_pos_rate と `n_merge_obs_recount` 以外の数はすべて同じ。違うのは `merge_rate` と `n_merge_obs_recount` だけで、`windows_def` の `all_trials`・`under_limit`（主の範囲・37 層のうち 2 層）・`under_limit_gt_duration` で各 2 層、`all` で各 8 層、`over_limit` で 0 層。直した側は全層で分子 ≤ 分母。登録の側に D10 の注（値なし）は 0。`config.merge_recount: obs` が 8 か所（評価 8 本）。l1・l2 は `inputs_sha256.match` だけが違う。→ macOS の `results/d10/macos/` と**同じ形**（macOS は予測の層もあるので、加えて `prediction_layers` の併合の率と登録の側の注 32 か所）。出力にパス・ホスト名・ログイン名なし・CR 0。
- **記録**: `data.windows.md` に「Analysis under deviation D10」の節（機械は製品名でなく仕様で・内部の番号なし・`_style_check.py` 違反 0）。
- **読んでいないもの**: 率の値は出していない（変わった層の数だけ）。併合の率を登録と直した解析で並べる表は `results_tables.py` の仕事（引き継ぎ `next-session-ime-paper-results-2.md` §2 の 2）。
- **影響範囲**: `experiment/results/d10/windows/e1_*.json`（新規 4）・`experiment/data.windows.md`・本ファイル・引き継ぎ 2 本（surface-d10 の冒頭・results-2 の §5）。書庫 `Downloads\windows-msime-tsf-2.zip` は消さずに置いた（寄託は研究者）。

## 判断 167: データの寄託先は Zenodo（データセットの記録・データ単独の DOI）、コードと材料は GitHub の公開 repo にする（2026-10-05・G-GEAR・研究者の選択）

- **背景**: 研究者の問い「OSF へ up はいつ頃する？」。記録の食い違いを見つけた: 判断 146 は「Zenodo の記録をデータセットとして DOI 付きで作る（ソフトウェアの記録と分けるかは M12 で決める）」、判断 159 と引き継ぎ `next-session-ime-paper-results-2.md` は「OSF への寄託は研究者」。`data.md`・`data.windows.md` の Deposits はどれも「not yet deposited」で、日付は決まっていない。OSF Registries の 2 つの登録（`9nh7r`・`4jwzn`）は済んでいる（別物）。
- **メインの推奨**: Zenodo にデータセット用の記録として作る（判断 146 の形・外枠の Open Practices「the data with their own DOI」・下書きと DOI の予約は Claude が進められ、公開は都度確かめる〔memory「Zenodo token」〕・予約した DOI を先に原稿に書ける・Editorial Manager の欄は GitHub〔memory「Springer Editorial Manager」〕）。採らなかった: OSF のプロジェクトに上げて OSF で DOI を作る。
- **研究者の答え（逐語）**: 「ok. zenodo, githubにしよう」→ **データ = Zenodo（データセットの記録・データ単独の DOI）／コードと材料 = GitHub の公開 repo（M12 の計画どおり・リリースは Zenodo で DOI）**。投稿の欄のリンクは GitHub。
- **日程**: M12 の枠（判断 145 の 10-23〜27・足りなければ 11 月上旬）。投稿（10-28〜31）の前に DOI が要る（Data availability・Open Practices Statement）。DOI の予約は先にしてよい。
- **まだ決まっていないこと**（M12 で研究者に聞く）: E3 の標本（`samples.tsv`）の置き方・`working` の観測ログを含めるか（外枠の Open items）・較正パイロットの生ログを含めるか（判断 146 の 4）・ソフトウェアの記録は GitHub のリリースを Zenodo に連携させるか。
- **書庫の場所**（git の外）: macOS ON / OFF は Mac の `~/ime-m4/deposit/`、Windows は Surface の `~/ime-m7/deposit/`（G-GEAR の `Downloads` に同じ SHA の写し）。
- **影響範囲**: 判断 159 と引き継ぎの「OSF への寄託」はこの判断で読み替える（本文は書き換えない）。`next-session-ime-paper-results-2.md` §5 に書いた。

## 判断 168: 結果の表の道具に問 4（表 11・推奨）・問 5（表 12）・D10 の直した併合の率を足す（2026-10-05・G-GEAR・メインの選択・研究者が覆せる）

- **背景**: 引き継ぎ `next-session-ime-paper-results-2.md` §2 の 2（道具を広げる）の前半。3 セルの問 1〜5 と D10 の直した解析がそろった（判断 166）。
- **問 4 の規則（§6.8・§10.7 をコードに写した）**: 集合が K で near chance ＝ 報告の正解率（自身と粗い集合の最大＝`acc`）の Wilson 区間の上端（`acc_ci[1]`）≤ 2/K。規則の near chance ＝ K = 10 と K = 100 の両方。推奨 ＝ `no_time`・`counts_only` の順に、**macOS の 2 セルの両方**で near chance の最も細かい集合、無ければ none。macOS のセルが欠けたら not decided（外枠 §8）。Windows の同じ判定は但し書きで、推奨を変えない。K = 1,000 は規則に入れない。値の無い（採点された試行 0）集合は near chance としない。⚠️ `acc` と `acc_ci` の意味は `kit/e2/closed_set.py` の docstring（371〜381 行）で確かめた。閉じた集合のファイルは D8（S12 を外した）であることを検査する（`skipped_scenarios`）。
- **問 5（§6.10・§10.9）**: `summarize_e3.py` の出力を読み、`measured` の条件だけを引く（`insufficient` は値なし）。Windows の `working` で CPU が全部 0 は insufficient（§10.9）、`idle` は印つきで報告。要旨の (iv) は系ごと・条件ごとの CPU の平均（区間なし）。
- **D10**: 補遺の層の表に「Corrected」（直した解析の併合の率）の列を登録の列の隣に足した。登録の側が `merge_recount` を持っていたら止まる・直した側が `obs` でなければ止まる。値 `<cell>.d10.<primary|all>.merge.differ`（併合の率が変わった層の数）。
- **表の形（メインの選択）**: 表 11 は 2 つの規則の集合 × K = 10・100 をセルごとに（正解率〔Wilson〕・ブロックの区間・2/K・near chance）＋推奨の行。全集合・全 K と速さ・シナリオごとの素の正解率は補遺 `closed-set-all.tex`（`supplement.tex` に読み込んだ）。表 11・12 は表 8 と同じ `sidewaystable`。⚠️ 外枠の表 11 の「規則の性質」（§6.8 の確率の表）は登録の値で結果ではないので生成しない（結果の節で §6.8 を引く）。
- **検証**: selftest 19 → 40 件。★ 変異 16 本（`<=` を `<` に・素の区間を読む・K = 1,000 を規則に・片方の macOS で足りる・粗い集合を先に・Windows も決める・欠けたセルの検査を外す・欠けたら none・値なしを near chance に・Windows の全 0 を引く・insufficient を引く・直した列に登録の値・D8 の検査を外す・D10 の印を要求しない・登録の印を拒まない・変わった層を全部数える）→ すべて赤（欠けたセルの変異は例外でなく狙った確認で赤になるよう selftest を直した）。実物で生成 → `--check` 一致・文体違反 0。`build.sh`: main はエラー 0・未定義の参照は判断 165 と同じ 4 ラベル・overfull 1（HEAD と同じ）。補遺は overfull が 29 → 35（増えた 6 件は既存の層の表と同じ「横向きのページの出力時」の型）。表 11・12 は一時の写しの main に入れて組み、overfull が増えないことを確かめた（結果の節は §2 の 3）。
- ⚠️ **表示した値**: 規則のコードと selftest・変異を済ませてから実物で生成した。生成の後、表の幅の確認で LaTeX のログの overfull の行に表 12 の数が 4 つ出た（以降は数字を伏せた）。推奨と問 4 の値は見ていない。規則は生成の後に変えていない（変えたのは表の列の幅だけ）。
- **まだ**: 表 7（届き方・RF1・KT1）・表 10（L2）・開いた集合・表 8 の macOS の 3 つの比較と予測の層。
- **影響範囲**: `manuscript/tools/results_tables.py`・`manuscript/generated/`（新規 3 ファイル）・`manuscript/supplement/supplement.tex`・本ファイル。

## 判断 169: 結果の表の道具に問 3（表 10・文ごとの一致）と補遺の試行の差を足す（2026-10-05・G-GEAR・メインの選択・研究者が覆せる）

- **規則（§4.6・§6.7）**: 4 つの測度を §4.6 の順（変換の数・平均変換時間・取り消し率・変換に費やした時間の割合）。主は速さごと（`agreement_by_stratum`）。速さをまとめた値（`agreement`）と 3 つの混合（`mixture_bias`）は補遺で「比べるため」と明記。混合の重みは §6.7 の 0.6/0.3/0.1・等しい・0.1/0.3/0.6 と**照合して違えば止まる**。試行の差は主の範囲で 3 つの見方（全試行・運ばれた層を除く・層 none〔診断〕）。後の 2 つは予測の層が要るので Windows では「計算しない」と書く（§10.7）。
- **表の形（メインの選択）**: 表 10 はセル × 測度 × 速さで、文の数・偏り・下限・上限・ICC(A,1)（それぞれ区間つき）。区間が出せない推定は推定だけを出し、表の注で「理由は結果のファイル」。ミリ秒は整数、割合は小数 3 桁、負の符号は `$-$`。補遺 `text-agreement.tex`（`supplement.tex` に読み込んだ）は合算と混合・全試行の速さごと・試行の差（観測と参照の平均つき）。
- **検証**: selftest 40 → 49 件（作り物の全試行の値を主の範囲と変えて、範囲の取り違えが見えるようにした）。★ 変異 10 本を足して計 26 本（下限に上限の区間・ミリ秒でない・混合の重みを照合しない・文の無い行を落とす・区間なしを値なしに・層の無い見方を書かない・観測と参照の平均を入れ替え・表 10 と値が全試行を読む ほか）→ すべて赤。実物で生成 → `--check` 一致・文体違反 0・CR 0。一時の写しの main に表 10 を入れて組み、main の overfull は HEAD と同じ。補遺で増えたのは横向きのページの出力時の型だけ。
- **表示した値**: なし（ログの overfull は数字を伏せて見た）。
- **まだ**: 表 7（届き方・RF1・KT1）・開いた集合・表 8 の macOS の 3 つの比較と予測の層。
- **影響範囲**: `manuscript/tools/results_tables.py`・`manuscript/generated/`（新規 2 ファイル）・`manuscript/supplement/supplement.tex`・本ファイル。

## 判断 170: 結果の表の道具に開いた集合（RC3）の表を足す（2026-10-05・G-GEAR・メインの選択・研究者が覆せる）

- **規則（§6.8）とコードの確認**: `kit/e2/open_set.py` の docstring（14〜64 行）で、K1 = 作品ごとに分ける（`--split work`・既定）、K1+ = 文ごとに分ける（`--split phrase`）、`gain` = 基準線の CER − 攻撃の CER、`gain_vs_shuffled` = 他の試行の復号の CER − 攻撃の CER を確かめた。
- **表の形（メインの選択）**: `table-open-set.tex`（`sidewaystable`）。セル × 攻撃者（K0・K1・K1+・文ごとに分けた K0）× 長さの知識（区切りの数・本当の長さ）で、試行の数・攻撃の CER・基準線の CER・gain・shuffled との差（それぞれ区間つき）・復号できない試行の数。外枠の表の一覧には開いた集合の番号が無い（RC3 は §8 の本文）ので、本文に置くか補遺に回すかは §2 の 3 で決める。値 `<cell>.q4.open.<K0|K1|K1plus|K0.phrase>.<count|true>.<cer|gain|gainvsshuffled>`。2 つの分け方 × 2 つの長さ × K0・K1 がそろわなければ止まる。
- **検証**: selftest 49 → 52 件（攻撃者ごとに値を変えた作り物で、K1+ の取り違えと gain の取り違えが見える）。★ 変異 3 本を足して計 29 本 → すべて赤。実物で生成 → `--check` 一致・文体違反 0・CR 0。一時の写しの main に入れて組み、overfull は HEAD と同じ（見出しの「Undecodable」は分綴の位置を指定）。
- **表示した値**: なし。
- **影響範囲**: `manuscript/tools/results_tables.py`・`manuscript/generated/`（新規 1 ファイル）・本ファイル。

## 判断 171: 印の時刻（§6.9）を Windows のセルで計算し、結果の表の道具に表 7（RF1）・KT1・表 8 の macOS の 3 つの比較・予測の層（D10 の直した併合の率つき）を足す（2026-10-05・G-GEAR・研究者の選択〔印の時刻〕とメインの選択〔表の形〕・研究者が覆せる）

- **見つけたこと（一次で確かめた）**: §6.9 の印の時刻（`kit/pilot/clock_sync.py` の出力）は、本計測のどの run でも計算されていなかった。`e1_detection.json` の `config.clock_offsets_ms` は空（`notes.md` の「clock_offsets_ms is not passed to the matcher」＝補正しない設定）で、`uncorrected_blocks` は補正しなかったブロックの一覧にすぎず、印の時刻ではない。外枠の Claims and evidence は「its output is kept with the result files of the system」と書くが、`results/` にも `data.md`・`data.windows.md` にも無い。
- **研究者の選択（推奨どおり）**: **Windows を今回回す**（G-GEAR に run がある）。macOS は Mac への引き継ぎ。表 7 は、ファイルのあるセルは読み、無いセルは「not computed」と出す。採らなかった: 今回は回さない・逸脱にして報告しない。
- **Windows の印の時刻（実行）**: Windows のタグの `kit/pilot/clock_sync.py`・`seal_obs.py`（`git archive`・LF・HEAD と差なし）・selftest 緑。入力 3 ファイルは run の manifest の SHA-256 と一致。`obs.jsonl` の**写し**（repo の外）を `seal_obs.py` でキーの行だけに（`6b866cf5…`・run のディレクトリは触っていない）。印の仕様は登録に無いので、Windows のパイロットと同じ形（README の例の `gt_vks` を Windows の仮想キーに〔37・39〕・`obs_categories` は `navigation`・`max_gap_ms` 300・窓は既定 3,000 ms）を**出力を読む前に**決めた（`8e382eed…`）。exit 0・2 回目とバイト一致・`results/windows/clock_sync_windows-msime-tsf.json`（`5341c3d6…`・パスなし・CR 0）。117 ブロックすべてで実行器・参照・観測の印が見つかった（欠け 0）。記録は `data.windows.md` の新しい節。
- **道具（`results_tables.py`・メインの選択）**:
  - 読み込み: `Cell` が `e1_delivery.json` と全比較を読む。系ごとの比較の組（macOS は 3 つ・Windows は `gt_obs` だけ）と違えば止まる。計画と正解の一致（`e1_l1.json` の `oracle`）は l1.py の docstring のとおり全試行・全定義で同じものなので、2 つのスコープで違えば止まる（実物で、正解を使う 8 つの塊は同一・`pred_obs` は `plan_available: false` を確かめた）。検出の `focus_loss.n_trials` が届き方の `n_trials_with_focus_loss` と違えば止まる。`clock_sync_<cell>.json` があれば読み、4 つの差がそろわなければ止まる。
  - **表 7** `table-reference.tex`（`sidewaystable`・セルが列）: 計画と正解（試行・食い違いの数と率〔Wilson〕・§6.3 の順の 7 つの型・どの試行にも入らないセッション）／届き方（測った試行・送ったキー・予定に対する送出の遅れの中央値・95 %・最大・観測と参照の到達・少ない試行・多い行・試行の外の行を「全キー / 入力モードのキーを除く」の 2 版で）／フォーカスの喪失（計画どおりの S15 とその他・観測にキーの行のある喪失・重なる試行・その試行のセッションの行と偽陽性を主の範囲と全試行で）／印の時刻（見つかったブロック・4 つの差の中央値〔範囲〕と 1 時間あたりのずれ）。群ごとに「何を読むのに使うか」（RF1 の Reported in）を見出しの行に書いた。
  - **KT1** `table-key-timing.tex`（本文・観測のキーの行）と補遺の参照のキーダウン: 系 × 速さ（＋全速さ）× 遅れ・間隔の誤差の n・平均・最小・5 %・中央・95 %・最大。対にできた試行・できなかった試行は結果のファイルに**全体の数しか無い**ので、セルごとに全体で出す（KT1 の「per system and speed」の速さごとの対にできなかった数は出せない —— 結果の節で書く）。最小・最大は整数（時刻が整数の ms）、ほかは小数 1 桁（メインの選択）。⚠️ 外枠の表の一覧に KT1 の表は無い（Section 6 の本文）→ 表を足したのはメインの選択。
  - **表 8** `table-detection.tex` を `sidewaystable` にして比較の列を足した（macOS は `gt_obs`・`gt_pred`・`pred_obs`、Windows は `gt_obs`）。シナリオごとの試行数は主の比較のものを使う（§6.4「all three comparisons cover the same trials」）。値 `<cell>.<gtpred|predobs>.<primary|all>.<recall|precision>.range|strata.left`。
  - **予測の層**（補遺 `detection-layers.tex`）: macOS のセル × 3 比較 × 3 スコープ（`over_limit` も・§6.4「each comparison and scope」）× 4 層（§6.4 の順）× 速さと併合。併合の率の隣に D10 の直した値。D10 の値なし（分子 > 分母）は `--`。値 `<cell>.d10.layers.novalue`（`macos_def` の層の併合の率で値なしの数）。
  - 補遺 `reference-strata.tex`: 層ごとの計画と正解（型ごとの数・フォーカスの喪失のある試行）・ブロックごとの印の時刻（Windows）・参照の KT1。`supplement.tex` に読み込んだ。
- **検証**: selftest 52 → 78 件（Windows 形の合成に届き方・計画と正解・フォーカス・印の時刻、別の一時ディレクトリに macOS 形の合成〔3 比較・層・D10〕）。`_expect_stop` は他の例外を「狙った確認の赤」として数えるようにした。★ 変異 29 本（scratchpad の使い捨て）→ **すべて狙った確認で赤**（例外で落ちたものなし）・無変異は緑。実物で生成 → `--check` 一致・15 ファイル・CR 0・既存の `detection-strata.tex` はバイトが変わらない・文体違反 0。一時の写しの main に結果の表 8 つを入れて組み、**main の overfull は HEAD と同じ 1 件**・補遺は 55 → 81（増えた 26 件はすべて「横向きのページの出力時」の型）・未定義の参照は HEAD と同じ 4 ラベル。列の幅は 2 回直した（KT1 の見出し・桁区切りの数・層の表の見出し）。
- **表示した値**: 規則のコードと selftest・変異を済ませてから実物で生成した。生成のとき値は画面に出していない（overfull は数字を伏せた）。ただし形を確かめる途中で、macOS OFF のセルにフォーカスの喪失が `mid` の速さにある（速さの名前だけ）ことと、印が 117 ブロックすべてで見つかったことは見た。
- **まだ**: macOS の 2 セルの印の時刻（Mac で・同じ手順で `obs_categories` は `navigation`・`gt_vks` は macOS のキーコード 123・124）。表 11 の「規則の性質」・結果の節。
- **影響範囲**: `experiment/results/windows/clock_sync_windows-msime-tsf.json`（新規）・`experiment/data.windows.md`・`manuscript/tools/results_tables.py`・`manuscript/generated/`（新規 4・変更 3）・`manuscript/supplement/supplement.tex`・`manuscript/outline.md`（Open items）・本ファイル・`tasklist.md`。

## 判断 172: 登録が報告を求めていて結果の表に無かったもの（層ごとの 1 対 1 の一致・`over_limit` と感度分析の層ごとの検出・スコープの構成・除外の理由・打ち切りなど）を道具に足し、表 9 の一致の限界と中央値の絶対差に区間を付ける（2026-10-05・G-GEAR・メインの選択・研究者が覆せる）

- **見つけたこと（登録と外枠を一次で読み直した）**: 結果の節を書く前に、§6.1〜6.7・§10.7 が「報告する」と書くものを道具の出力と突き合わせた。足りなかったもの: (1) 問 2 は「per stratum, per speed and per cell」で 3 つの比較（§6.4・§6.6）→ 表 9 は主の比較・速さごとだけだった。(2) 問 1 は 3 つのスコープ（§6.4「computed under all three scopes」）と Windows の感度分析（§10.7 `under_limit_gt_duration`）→ 補遺の層の表は主の比較の 2 スコープだけだった。(3) §6.1「The number of letter keys and the think time of the trials in each scope are reported per stratum, from the plan」→ 無かった。(4) §6.2 の除外の理由・`start_while_open`・長さ 0 の行、§6.6 の打ち切りの数と「continued commit」で分けた `abandon`、§10.7 の診断（20〜25 秒・25 秒以上の行・S4 の Esc・長さの無い終わり・長い試行の 2 つの出どころ）、2 つの定義が同じセッションを持つか → 値に無かった。(5) ★ **表 9 の一致の限界と中央値の絶対差に区間が無かった**（判断 156 の表）—— §6.1「the bias and the limits of agreement ... carry 95% percentile bootstrap intervals」・結果のファイルに `loa_lo_ci`・`loa_hi_ci`・`mae_ci` がある → 外枠の「Estimates are reported with their intervals where the registration gives them」に照らして欠け。
- **道具（メインの選択）**:
  - 表 9: 偏り・下限・上限・中央値の絶対差それぞれに区間（列を 10 に・`footnotesize`）。行の部品 `session_cells` を補遺と共有。
  - 補遺 `session-strata.tex`（新規）: 比較 × 2 スコープ（問 2 のスコープ）× 層ごと・速さごと・併合。
  - 補遺 `detection-strata.tex`: 比較 × 検出のすべてのスコープ（`over_limit`・Windows の `under_limit_gt_duration` も）。試行の数は問 3 の試行の記録がある 2 スコープだけ（ほかは `--` と表の注）。各セルの頭にスコープの構成の表（macOS・予測の要約 `composition` から・中央値〔最小〜最大〕）。Windows は「予測を計算しないので無い」と書く（★ 凍結のコードが Windows では作らない —— 登録 §6.1 の欠け・結果の節で書く）。ラベルを `tab:strata-<cell>-<comp>-<scope>` に変えた（本文からの参照は無い）。
  - 値 `diagnostic_values`: 除外（理由ごと・`<cell>.excluded.<trials|gt|obs>.<reason|n>`）・`samesessions`・`startwhileopen`・`zerodwell`・`cutoff`（`n_long` ほか 5 つ）・`abandon.continued`・比較 × スコープの併合の検出の値（`pooled.<comp>.<scope>.<measure>`・F1 も）・予測の要約（macOS）・Windows の診断（`win.*`）。
  - ★ 除外の確認: 実物で「`pred_obs` の `gt` の側の除外が違う」で止まった —— `pred_obs` の最初の側は予測なので当然違う（値を見る前の形の確認で分かった・規則の直しは道具の検査の範囲）。→ 各比較の中でスコープ間は同じ・試行の除外は全比較で同じ・正解の側は `gt_obs` と `gt_pred`、観測の側は `gt_obs` と `pred_obs` で同じ、に直した。
- **検証**: selftest 78 → 91 件（合成に除外の理由・長さ 0・打ち切り・併合の値・層ごとの問 2・予測の要約・Windows の診断を足し、比較・スコープごとに値を変えた）。`l1` の比較の組が検出と違えば止まる確認を足したら、既存の「系の比較の組」の否定の確認が先に l1 の確認に捕まって変異で緑になった → 否定の確認を両方のファイルから外す形に直した。★ 変異は 2 回目 20 本（scratchpad の使い捨て）がすべて狙った確認で赤、判断 171 の 29 本も回し直して 28 本が赤（1 本は書き直した関数の型で、2 回目の変異が同じ規則を確かめる）。実物で生成 → 16 ファイル・`--check` 一致・CR 0・文体違反 0。一時の写しの main に結果の表 8 つを入れて組み、**main の overfull は HEAD と同じ 1 件**・補遺は 160（HEAD の 55 のうち出力時以外の 17 件は同じ、増えたのはすべて横向きのページの出力時の型）。
- **表示した値**: なし（形の確認で、除外がある／ないセル〔macOS OFF は除外 0〕と、Windows では 2 つの定義が別のセッションを持つことを見た —— どちらも登録が予想していた形）。
- **影響範囲**: `manuscript/tools/results_tables.py`・`manuscript/generated/`（新規 1・変更 4）・`manuscript/supplement/supplement.tex`・本ファイル。

## 判断 173: Windows の開いた集合の結果が macOS OFF とバイト一致する —— 取り違えではなく、2 つのセルの計画が句・文字キー・時刻を共有するため（G-GEAR で回し直して確かめた）（2026-10-05・G-GEAR・メインの確認）

- **見つけたこと**: 結果の表を読むと、Windows の閉じた集合（`no_time`・`counts_only`）と開いた集合の値が macOS OFF とすべての桁（区間まで）で一致していた。ファイルを比べると、開いた集合は**バイトが同一**（`77bba3a3…`・Windows は Surface が 10-05 10:30 に `44fbda3b` で入れた、macOS OFF は後で Mac が作った）。閉じた集合は別のファイル（`config_sha256`・`recipes_sha256`・`n_ime_shadow_rows_unused`・`all` などの 52 か所が違う）で、規則の 2 つの集合だけが同じ。
- **確かめたこと**: (1) G-GEAR の Windows の run から Windows のタグ（`git archive`・LF・selftest 134 件 OK）の `open_set.py` を §6.8・§10.7 の命令で回し直した → exit 0・約 80 秒・**`77bba3a3…` とバイト一致**（Windows の run がこのファイルを出す＝写し間違いではない）。(2) macOS OFF の計画を macOS のタグから §2.4 の命令で再生成 → 登録の `3759ebf7…` と一致。Windows の計画（`b7bdf8fc…`）と試行ごとに比べると、2,925 試行の block・シナリオ・速さ・gap・考える時間・句・読みの長さ・意図が**すべて同じ**。キーが違うのは S2（macOS が Return を 1 つ多く押す）と S4（Windows が Esc を 1 つ多く押す・D1）の各 225 試行だけ（後ろの時刻もそれに応じて違う）で、文字・数字・記号のキーは全試行で同じ・総数も同じ（93,861）。→ 開いた集合が読む文字キーと記号は 2 つのセルで同じで、両方とも入力モードのキー以外はすべて届いた → 同じファイルになる。
- **記録**: `data.windows.md` に節「The open set of question 4, repeated」（命令・SHA・計画の比較）。⚠️ それまで `data.windows.md` には Windows の開いた集合の命令と SHA が無かった（Surface のコミットの記録だけ）—— この節で埋めた。
- **原稿への影響**: 問 4 の結果の節で、Windows の判定が macOS OFF と同じ値になる理由（計画が句・文字キー・時刻を共有）を書く。問 1〜3 の Windows と macOS を並べないという規則は変えない。
- **影響範囲**: `experiment/data.windows.md`・本ファイル。

## 判断 174: 結果の節の草稿（§6・§7・問 4・問 5）を書き、表 11 の「規則の性質」は手法の節の既存の静的な表のままにする（2026-10-05・G-GEAR・メインの選択・研究者が覆せる）

- **規則（道具）を先にコミットしてから値を読んだ**: 表の道具は `ffd61b1a`（判断 171）・`7c599224`（判断 172）で固めた後、このセッションで初めて結果の値を読んだ。値を読んだ後に道具の規則は変えていない（判断 173 は記録の追加だけ）。
- **ファイル**: 新規 `sections/results-agreement.tex`（§6: 試行と attempts の表〔`sec:results-attempts`・記録 `data.md`・`data.windows.md` から写した〕・参照が確かめること〔表 7・KT1 の表〕・検出〔除外とスコープ・主の比較・予測との比較・2 つの定義・D10・打ち切り・診断・表 8〕・1 対 1 の一致〔表 9〕）・新規 `sections/results-text.tex`（§7・表 10）・`recoverability.tex` の結果（閉じた集合・推奨・Windows の但し書き・開いた集合・表 11 と開いた集合の表）・`cost.tex` の結果（表 12）。`main.tex` に 2 つを読み込んだ。
- **値の書き方**: 結果の値はすべて `\rv{}` か生成した表（本文の `\rv` は 175 個・生成した値に無いのは macOS の印の時刻の 4 つだけ＝未計算で太字の [鍵] が出る・意図どおり）。⚠️ 値でない**定性的な記述**（「OFF は除外なし」「ON の『セッションなし』は S10 の遅い・中の速さに多い」「文ごとの abandonment rate と fraction of time converting の偏りは全セルの全速さで負〔区間が 0 未満〕」「conversions per trial の偏りは macOS で速さにより符号が違い、Windows は全速さで正」「行の 20 秒以上は無い」）は生成した表を読んで書いた —— 結果のファイルが変われば手で直す必要がある（`--check` は捕まえない）。
- **一次で確かめてから書いたこと**: (1) D10 の直した解析が macOS でも変えたのは `merge_rate` と `n_merge_obs_recount`（と設定・注）だけ（登録と直したファイルを葉まで比べた・1,904 と 476 か所）。(2) macOS の `start_while_open` は正解の規則の開始の事象が `set_marked`（文字のたびに呼ばれる）なので、OFF は全セッション・ON はほぼ全セッション（`gt_rules.json`・`gt_sessions.py` の docstring）。(3) 試行の外の行の数が印のキーの数（4 × ブロック数）と一致。(4) 評価の語の grep（`only` は限定の用法だけ）・文体違反 0。
- **表 11 の「規則の性質」（引き継ぎ §2 の 3）**: `recoverability.tex` に登録 §6.8 の確率の表 `tab:nearchance`（静的・登録の値）が既にあった → そのまま置き、注の「判定は結果のファイルから足す」を「判定は表 `tab:closed-set`」に直した。外枠の表の一覧に KT1 の表を足した。
- **結果の要点（研究者への報告用）**: 問 4 は macOS の 2 セルとも `no_time`・`counts_only` が K = 10・100 で near chance にならず、**推奨は none**。Windows も同じ判定（値は macOS OFF と同じ —— 判断 173）。macOS ON は計画と正解の食い違いが他より多く、ほとんどが「セッションなし」（S10 の遅い・中）。Windows の参照は IME が消費しないキーしか受け取らない（設計どおり）ので、参照の側の KT1 は Windows で対にできない。
- **組版**: `build.sh` で main エラー 0・未定義の参照は 3 ラベル（`fig:components`・`sec:availability`・`sec:limitations`・`sec:results-attempts` は埋まった）・overfull は HEAD と同じ 1 件（試行の表の見出しの幅を 1 回直した）。
- **まだ**: 図 2〜5（外枠の Figures・道具は標準ライブラリだけなので作図は別に決める）・macOS の印の時刻（Mac）・要旨と結論（外枠の Rule for the abstract）・§1・§11〜13・完了時レビュー・attack-me。
- **影響範囲**: `manuscript/sections/results-agreement.tex`・`results-text.tex`（新規）・`recoverability.tex`・`cost.tex`・`main.tex`・`outline.md`（表の一覧）・本ファイル・`tasklist.md`。

## 判断 175: この枝の完了時レビュー（code-reviewer ∥ security-checker ＋ Codex 1 巡目）の指摘を一次で確かめて直す・「全試行の範囲」の読みを記録する（2026-10-05・G-GEAR・メインの選択・研究者が覆せる）

- **範囲**: `origin/main...HEAD`（`cf320319..4e0c36dd`・111 ファイル）。コードは 5 ファイル（`results_tables.py`・`match.py`〔D10〕・`closed_set.py`〔D8〕・`build.sh`・`_style_check.py`）。Codex は研究者の承認（手動承認の閾値 2,000 行を超えた・推奨どおり 5 ファイル）でパス限定（`run-codex-review.sh cf320319..4e0c36dd -- <5 paths>`）・1 回 77,499 トークン（この枝の台帳で今日 98,711・origin/main の 132,139 と合わせて約 23 万 / 30 万）。
- **結果**: code-reviewer = HIGH 0・MEDIUM 5・LOW 7（約 4 分）。security-checker = CRITICAL・HIGH・MEDIUM 0・LOW 4（約 6 分・生ログ・打鍵の中身・個人情報は公開物に無い）。Codex 1 巡目 = P1 1・P2 4。重なり: `build.sh` の相対パス（3 者）・D10 の入力の照合（code-reviewer と Codex）・D8 の検査の緩さ（同）・セル名と TeX のエスケープ（security と Codex）。
- **直したもの（`results_tables.py`・`build.sh`・`main.tex`・`BUILD.md`）**:
  1. `build.sh`: 雛形と出力先を最初に絶対パスに（Windows は `pwd -W`・TEXINPUTS も同じ形）・出力先が原稿のディレクトリの中なら拒否（自分で作ったディレクトリは消す）・`-no-shell-escape`・BibTeX の警告（exit 1）で止まらない・pdflatex が落ちたらログの場所を出す・「生成されていない結果の値」と BibTeX の警告の数を表示。⚠️ このセッションで雛形を `/c/...` の形で渡して `sn-jnl.cls` が見つからなかったのも同じ根（TEXINPUTS は MSYS が変換しない）。相対パスでの組版（scratchpad から雛形と出力先を相対で）と拒否を実際に回して確かめた。
  2. `main.tex` の `\rv`: 鍵が無いとき `\PackageWarningNoLine{results}{Result value <key> not generated}` を出し、`build.sh` が数える（今は macOS の印の時刻の 4 つ）。
  3. 範囲の鍵（要旨の規則・予測との比較）は層が 1 つも入らなくても `--` の値として出す。偏りの範囲に使った速さと除いた速さの数 `<cell>.<primary|all>.dwellbias.speeds.used|left`。
  4. D10: 登録の側に「分子 > 分母で値なし」が併合の率以外にあれば止める（Codex 5 への対応 —— `match.py` の `_prop` の防御はすべての割合に効くが、実データで値が消えたのは 32 か所すべて併合の率と確かめた・`match.py` は解析を回し終えた凍結の直しなので変えない）。直した側は、`merge_rate`・`n_merge_obs_recount`・`merge_recount` を除いて登録と完全に同じでなければ止める（入力の SHA・設定・ほかの率すべて）。
  5. D8: `skipped_scenarios` が `{"S12": >0}` だけ・どの結果の `by_scenario` にも S12 が無い・未採点のブロックと試行の数がある、を確かめる。
  6. 除外の試行の型は §6.2 の 3 つだけ・各型の数は総数以下・総数 0 は型が無いときだけ（⚠️ 1 つの試行が 2 つの型で数えられうるので「和 = 総数」は使わない —— `match.py` の `_count_types` を一次で確かめた）。
  7. セル名を `match.py` と同じ `CELL_RE` で検証・`tex_escape` を TeX の特殊文字すべてに。
  8. E3 の measured の条件に `cpu_all_zero` の行が無ければ止める。`--check` は、もう生成しないファイルが出力先に残っていれば赤。
- **直さなかったもの（理由）**:
  - ★ **code-reviewer MEDIUM「全試行の範囲」に入る層の選び方**: 外枠の「the same range over all trials」は (A) 主の範囲で選んだ層の全試行の区間、(B) 全試行の側で同じ作り方（30 試行以上の層）をやり直す、の 2 通りに読める。道具は (B)（判断 156 で、値を見る前に実装・ただし読みは記録していなかった）。(B) を保つ理由: 登録 §6.1 は「the estimate under `all_trials`」と書き、全試行の推定は主の範囲で 0 試行の層（S13）も含むべきで、(A) では全試行の値にならない。⚠️ 値を見た後でこの読みを変えると規則の後付けになるので変えない。研究者が (A) を選ぶなら、道具の 1 か所（`abstract_values` の `kept`）の直しで済む。
  - code-reviewer LOW「macOS のセルの集合に値が無いと none ではなく not decided に」: 値の無い集合を near chance としない扱いは判断 168 で値を見る前に selftest で固めた。実データは全集合に値がある → 変えない。
  - Codex 5 の `match.py` 自体の直し: 上の 4 のとおり（凍結の解析を回し直すことになる・新しい逸脱になる）。
  - security LOW「`.steering/` にユーザー名を含む絶対パス」: repo は private・`.steering/` は公開物の外・merge-base で既に 150 か所。新しい引き継ぎは `~` で書く。security LOW「ビルドの生成物を `.gitignore` に」: 出力先を原稿の外に限る拒否で代えた。
- **検証**: selftest 91 → 105 件。★ 変異 3 回目 14 本（scratchpad）→ すべて狙った確認で赤（除外の型の確認が、別の確認〔スコープ間の除外の一致〕に先に捕まって緑になったので、全スコープを変える形に直した）。1 回目の「D10 の数え方」の変異は、新しい共有の確認に例外で捕まるようになったので、数える箇所だけを変える変異に差し替えた。1・2 回目も回し直して計 62 本が狙った確認で赤。実物で生成 → 16 ファイル・`--check` 一致（値は鍵が増えただけ）・文体違反 0・CR 0。`build.sh` で main エラー 0・overfull は HEAD と同じ 1 件・生成されていない値 4（macOS の印の時刻）・BibTeX の警告 0。
- **影響範囲**: `manuscript/tools/results_tables.py`・`manuscript/build.sh`・`manuscript/BUILD.md`・`manuscript/main.tex`・`manuscript/generated/values.*`・`.codex/budget.json`（台帳）・本ファイル。

## 判断 176: Codex 2 巡目（判断 175 の直しの境界）の指摘 4 件を直す（2026-10-05・G-GEAR・メインの選択・研究者が覆せる）

- **範囲**: `run-codex-review.sh 4e0c36dd..9f730d2e -- results_tables.py build.sh main.tex`（約 235 行）・28,412 トークン（この枝の台帳で今日 127,123・origin/main の 132,139 と合わせて約 26 万 / 30 万）。3 巡目は回さない（記録どおり 2 巡・予算）。
- **指摘と直し（4 件とも一次で確かめて妥当）**: (1) 出力先の判定をシンボリックリンクで回避できる → `pwd -P`（物理パス）で比べ、Windows は `cygpath -m` で C:/ の形・大文字小文字を無視して比べる（大文字に変えた原稿のパスが拒否され、作ったディレクトリが残らないことを回して確かめた・リンクそのものの試しは Windows で作れないので未実施）。(2) 除外の数の整合 → 非負の整数・型ごとの最大 ≤ 総数 ≤ 型ごとの和（`match.py` は除外した試行にすべて型を付ける）。(3) `CELL_RE.match` は末尾の改行を許す（Python の `$`）→ `fullmatch`（⚠️ 上流の `match.py` も同じ `$` だが凍結のコードなので変えない）。(4) 未採点の数の確認が真偽値と負数を通す → `is_count`（`type(v) is int and v >= 0`）。
- **検証**: selftest 105 → 109 件。変異 3 回目に 4 本を足して 18 本・2 回目 20 本・1 回目 28 本の計 66 本が狙った確認で赤（末尾の改行の確認が、前の確認で書き換えたファイルを戻す前に読んでいて緑になったので、元のデータから作る形に直した）。実物の `--check` 一致（値の変化なし）・`build.sh` を相対パスで回して main エラー 0・overfull 1（HEAD と同じ）・生成されていない値 4。
- **影響範囲**: `manuscript/tools/results_tables.py`・`manuscript/build.sh`・`.codex/budget.json`（台帳）・本ファイル。

## 判断 177: macOS の 2 セルの印の時刻（§6.9）を判断 171 の手順で計算し、`data.md` に記録する（2026-10-05・Mac・判断 171 の研究者の選択の続き・研究者が覆せる）

- **入力（一次で確かめた）**: `experiment/runs/macos-standard-live-{on,off}-1/run.json` の SHA-256 が `data.md` の `run_dir` の行（on `0257755c…`・off `4ac581cb…`）と一致。`oracle.jsonl`・`gt.jsonl`・`obs.jsonl` の SHA-256 は 6 件とも manifest の `outputs.<name>.sha256` と一致。
- **道具**: タグ `ime-observation-prereg-macos`（`ff122e32`）から `git -c core.autocrlf=false archive` で取り出した `kit/pilot/clock_sync.py`・`seal_obs.py`（CR 0・`git diff <tag> HEAD` で差なし）。⚠️ 引き継ぎの命令どおり `kit/pilot` だけを取り出すと **`seal_obs.py --selftest` が 1 件赤**（「keys-out passes the obs/1 validator (exit 2)」）—— selftest が `../formats/validate_logs.py` を呼ぶのに、取り出していなかったため（不在 → exit 2）。同じタグの `kit/formats` も取り出して両方の selftest が緑。道具の欠陥ではなく取り出し範囲の問題なので、逸脱にはしない（`data.md` に「`kit/formats` もいっしょに取り出した」と書いた）。
- **キーの行だけの写し**: 各セルの `obs.jsonl` を scratchpad（repo の外）へ写し、`seal_obs.py --obs <写し>/obs.jsonl --keys-out <写し>/obs.keys.jsonl --sealed-dir <写し>/sealed`（exit 0）。`obs.keys.jsonl` は on `a3d7685c…`・off `8b8889b6…`。run のディレクトリの `obs.jsonl` の SHA-256 は実行後も manifest と同じ（触っていない）。
- **印の仕様**（出力を読む前に固定・Windows と同じ形）: `{"oracle_keys": ["left", "right", "left", "right"], "gt_vks": [123, 124, 123, 124], "obs_categories": ["navigation", "navigation", "navigation", "navigation"], "max_gap_ms": 300}`（`cd87248d…`）。根拠は `plan_config.macos.json` の `marker`（left, right, left, right・`marker_gap_ms` 150）と `kit/pilot/README.md` の例（同じ 1 行）。窓は既定 3,000 ms。
- **実行**: 2 セルとも exit 0・2 回目とバイト一致。`results/clock_sync_macos-standard-live-on.json`（`8daab9da…`）・`-off.json`（`e289c583…`）。CR 0・LF で終わる・パス・ホスト名・ログイン名なし。形: on は 126 ブロック・off は 117 ブロックすべてで実行器・参照・観測の印が見つかった（`missing` はどれも 0・ON の持ち越しで参照の印が欠けることはなかった）。
- **生成**: `results_tables.py --selftest`（109 件）→ 生成（16 ファイル・`reference-strata.tex`・`table-reference.tex`・`values.json`・`values.tex` が変わった）→ `--check` 一致。本文の `\rv{}` 174 キーのうち生成されていないものは 0（macOS の印のキー 26）。表 7 から「not computed」が消えた。文体の検査 `_style_check.py papers/ime-observation` 違反 0。⚠️ LaTeX が Mac に無い（`pdflatex`・`latexmk` なし）ので組版は G-GEAR の次のセッションに任せる。
- **表示した値**: ⚠️ 生成の後に `values.tex` の印のキーを確かめる `grep` で、macOS OFF の印の時刻の値（`markers.*` の 10 行）を画面に出してしまった。仕様・道具・生成はすべてその前に終わっていて、値を見た後で変えたものは無い。
- **記録**: `experiment/data.md` に節「Marker times of section 6.9」（Windows の節の形）。`manuscript/outline.md` の Open items の該当行を「Done on 5 October 2026」に直した。
- **引き継ぎへの注**: 引き継ぎ（`next-session-ime-paper-mac-markers.md` §2 の 2）の取り出しの命令は `kit/formats` を足すのが正しい（同じ手順を別の機械で回すときのため）。
- **完了時レビュー**: code-reviewer（HIGH 0・MEDIUM 0・LOW 3）∥ security-checker（指摘 0・パス / ホスト名 / 秘密 / 打鍵の中身 / 生ログの混入なし）。LOW の (1)「this manifest」があいまい →「the run manifest (`run.json`)」、(2) `<cell>` が未定義 → 節の冒頭で定義、を直した（文体違反 0）。(3) 表 7 の caption に、使うセルの無い凡例「not computed: …」が残る —— 生成物は手で直さず、道具で使われない凡例を出さないかは G-GEAR の次のセッションで決める（値と規則には関わらない）。`/cross-review` は送るコードが無い（記録・結果の JSON・生成物だけ）ので省略。
- **影響範囲**: `experiment/results/clock_sync_macos-standard-live-{on,off}.json`（新規）・`experiment/data.md`・`manuscript/generated/`（変更 4）・`manuscript/outline.md`・本ファイル・`tasklist.md`。

## 判断 180: Mac の印の時刻（判断 177）を G-GEAR で確かめ、PR #307 が main でなく枝に入ったので main への PR を出し直す・表 7 の使われない凡例を出さない（2026-10-05・G-GEAR・メインの確認と選択・研究者が覆せる）

- **見つけたこと**: PR #307 は 07:54Z に作られ、base が `docs/ime-manuscript-outline`（そのとき PR #306 は merge 前）だった。08:04Z の merge は**その枝に入っただけ**で、main（`8848eabe`・PR #306 の merge）には Mac の 2 commit が入っていない（`gh api .../branches/main`・`git branch -r --contains 45adce11` で確かめた）。→ この枝から main への PR を出し直す。
- **G-GEAR で独立に確かめたこと**: (1) `clock_sync_macos-standard-live-{on,off}.json` の SHA-256（`8daab9da…`・`e289c583…`）・印の仕様の SHA-256（`cd87248d…`）が `data.md` と一致・CR 0・LF・パスなし。形は ON 126・OFF 117 ブロックすべてで実行器・参照・観測の印が見つかり、`missing` はどれも 0（判断 177 と同じ）。(2) `results_tables.py --selftest`（109 件）・`--check` 一致（Mac の生成物が G-GEAR でもバイト一致）。(3) `build.sh`: main・補遺ともエラー 0・**生成されていない結果の値 0**・main の overfull 1（以前と同じ）・BibTeX の警告 0。(4) 文体の検査は repo 直下から `papers/ime-observation` で違反 0（⚠️ papers の中から `.` で回すと、ロガーの写し `kit/logger/src` に別の規則が当たって 1,274 件と出る —— 検査の呼び方の問題で、公開物の違反ではない）。
- **表 7 の凡例（判断 177 の LOW (3)）**: 「not computed: …」の凡例は、印の時刻の無いセルがあるときだけ出す（`table_reference`）。selftest 110 件（全セルに印の時刻があるとき凡例が無いこと）・変異 1 本（常に出す）が狙った確認で赤。値と規則には関わらない。
- **Codex**（`run-codex-review.sh 45adce11..0f1b0246 -- results_tables.py`・20,775 トークン・台帳は今日 258,825 / 6 回）: 不具合・セキュリティの懸念なし。確認事項 2 つ —— (1) 凡例を残す側の確認 → 既存の「rf1: a cell without marker times says so」が見ている（印の時刻の無いセルがあると「not computed」が出る）、(2) 凡例と表の本体の判定の一致 → 本体も同じ `clocks.get(label)` の `None`（`reference_rows` の `cs is None`）で一致。直さない。
- **影響範囲**: `manuscript/tools/results_tables.py`・`manuscript/generated/table-reference.tex`・本ファイル。

## 判断 181: 図 1〜5 を pgfplots（TeX）で描き、図 2〜5 の座標は結果の表の道具が生成する（2026-10-05・G-GEAR・メインの選択・研究者が覆せる）

- **背景**: 引き継ぎ `next-session-ime-paper-manuscript-1.md` §2 の 2（「道具は標準ライブラリだけ。作図を別のスクリプト〔matplotlib など〕にするか、TeX で描くかを決める」）。G-GEAR の Python に matplotlib は無い。MiKTeX には pgfplots 1.18.1 がある。
- **選んだもの**: pgfplots。`results_tables.py`（標準ライブラリのまま）が図 2〜5 を `generated/fig-*.tex`（pgfplots のコードと座標をその場に書いたもの）として生成し、スタイル（速さ・特徴の集合の色と印・区間・白抜き・パネル）は `main.tex` の前文に置く。図 1（構成）は結果の値を持たないので手書きの TikZ（`figures/components.tex`）。理由: (1) Python に新しい依存を足さない（再現の記録が増えない）、(2) 図の座標も `--check` に入り、結果のファイルとずれない、(3) 字体が本文と同じ。採らなかった: matplotlib の別スクリプト（依存と版の固定が増え、PNG/PDF が結果のファイルとずれても `--check` が捕まえない）。
- **図の規則（値を見る前に決めた・既存の表の規則は変えていない）**: 区間は結果のファイルの両端をそのまま縦の線で描く（推定が百分位の区間の外にあってもそのまま）。主の範囲で 30 試行未満の層は白抜き（要旨と本文の範囲から外れる層）。値の無い層は描かず、題で言う。図 2 = セル × 再現率・適合率（層ごと・主の比較と範囲）、図 3 = セルごとの `dwell_ms` の差（偏りと一致の限界の上下、それぞれの区間）、図 4 = 4 つの文ごとの測度（偏りと一致の限界・セル × 速さ）、図 5 = 閉じた集合の正答率と K（両対数・6 つの集合・1/K と 2/K の線・`acc`〔集合とそこから導ける集合の最大〕を描き `acc_raw` は描かない）。色は dataviz の categorical の 1〜6 番（`validate_palette.js` で CVD の分離は PASS・面との対比は WARN → どの系列にも固有の印があり、値は表にもある）。
- ⚠️ **組版で見つけたこと**: sn-jnl の `\scriptsize` は 9pt で `\footnotesize`（7pt）より大きい（`\f@size` で確かめた）。図の小さい字はすべて `\footnotesize` にした。本文の幅は 372pt（13.1 cm）・高さ 552.7pt（19.4 cm）→ 図 2（6 パネル）は `sidewaysfigure`、ほかは軸の寸法を cm で固定（`scale only axis`）。
- **検証**: selftest 110 → 125 件（`_selftest_figures`: 30 試行ちょうどは塗り・29 は白抜き・速さのずらし・区間の両端・区間の外の推定・一致の限界がそれぞれ自分の区間・文ごとは主の範囲・速さに値の無い測度は描かない・閉じた集合は `acc` と集合のずらし・1/K と 2/K・セルが無いと何も描かない）。★ 変異 12 本（scratchpad の使い捨て `mutate_figs.py`）はすべて狙った確認で赤、無変異は緑。実物で生成（20 ファイル）→ `--check` 一致。`build.sh` で main エラー 0・生成されていない値 0・BibTeX の警告 0。図の頁を画像にして目で確かめた（重なりを 2 回直した）。文体の検査 違反 0。
- **組版の数の変化**: main の overfull は一度 2 になった（図 1 の TikZ が 10.6pt はみ出した）→ 箱の幅と間を詰めて 1（以前と同じ vbox）に戻した。未定義の参照は `sec:limitations`・`sec:availability`（§12 と Data availability を書けば消える）。
- **影響範囲**: `manuscript/tools/results_tables.py`・`manuscript/generated/fig-*.tex`（新規 4）・`manuscript/figures/components.tex`（新規）・`manuscript/main.tex`（前文）・`sections/method.tex`・`results-agreement.tex`・`results-text.tex`・`recoverability.tex`・`manuscript/BUILD.md`・本ファイル・`tasklist.md`。

## 判断 182: 要旨・序論・推奨・限界・結論・Declarations・Open Practices Statement を書き、手法の節に逸脱 D10 を足す（2026-10-05・G-GEAR・メインの選択・研究者が覆せる）

- **要旨（外枠の Rule for the abstract・登録 §6.1）**: (i)〜(iv) を全部入れると 280 語 → 規則どおり (iv) CPU、次に (ii) `dwell_ms` の偏りを本文（`sec:cost`・`sec:results-session`）に回した。残りは (i) セルごとの再現率・適合率の範囲（30 試行以上の層・外した層の数を再現率と適合率で別に・範囲が外した割合・carry-over の割合・全試行の範囲）と (iii) 推奨（Windows は但し書き）。**248 語**（scratchpad の使い捨て `count_abstract.py` が `\rv` を生成値で展開して空白で数える・"0.280–1.000" は 1 語）。Windows は「別の構成概念」と書いて macOS とは別の文にした。値はすべて `\rv`。
- **道具の追加（書式だけ）**: 要旨の語数のため、範囲が外した割合と carry-over の割合を百分率だけで出す鍵 `<cell>.scope.setaside.pct`・`<cell>.carryover.pct`（値と出どころは既存の鍵と同じ）。規則は変えていない。selftest 125 → 126 件。変異 2 本（別の分母・もう一方の割合から）が狙った確認で赤（1 本目の作りは鍵を消して例外で落ちていた → 確認を `get` にして、変異を作り直した）。
- **新しい節**: `sections/introduction.tex`（§1: 外枠の Section plan と貢献 5 つ・優先権の主張なし）・`recommendations.tex`（§11: (a)〜(e)＝RE1〜RE5・閾値なし・根拠を名指す）・`limitations.tex`（§12: 外枠 §12 と登録 §7・§10.11。理想化した入力は影響する測度と向きを書き、向きは期待として書く・向きの言えないものは「分からない」と書いた）・`conclusions.tex`（§13: 要旨の規則で (i)〜(iv) をすべて・残る問い）・`declarations.tex`（`\backmatter`・雑誌の見出し・Ethics は Not applicable〔外枠どおり〕・Open Practices Statement）。`main.tex` の並びに入れた。
- **手法の節の D10**: 「Nine deviations」→「Ten」・表 `tab:deviations` に D10 の行・「macOS の解析は macOS のタグから D10 の 1 つ目の変更〔値なし〕と D8 のスイッチで回した・1 つ目の変更は合成の run で凍結のコードとバイト一致・2 つ目の直した解析は全セルで登録の解析の隣に報告」（`deviations.md` D10 で確かめた）。`\tbd{Deviations recorded after this draft}` を消した。外枠 §5.9 の「D1 to D9」を「D1 to D10」に。
- **参照**: `method.tex` の `sec:availability`（番号の無い Declarations の中を節番号で指していた）→「(Declarations, Code availability)」の文に。未定義の参照 0。
- ⚠️ **値から書いた定性的な語**（結果のファイルが変われば手で直す・`--check` は捕まえない）: 要旨の「neither … nor … none is recommended」、§11 (c) と §13 の「neither granularity … in either macOS cell」。推奨そのものは `\rv{q4.recommendation}`、Windows の判定は `\rv{q4.windows.qualification}`。
- ⚠️ **研究者が書くもの（`\tbd` のまま）**: 著者と所属（表紙）・Funding・Conflicts of interest・Authors' contributions。M12 で埋まるもの: データの DOI・コードの repo の URL とリリースの DOI・外枠を固定した公開 commit・表 1 の「This logger」の版・`dataset.tex` の working の観測ログ。⚠️ BRM はデータの引用を書誌に求める（外枠の Journal requirements）→ DOI を予約したら `references.bib` にデータセットの項目を足して Data availability から引く。
- **検証**: `build.sh` main エラー 0・未定義の参照 0・生成されていない値 0・overfull 1（以前と同じ vbox）・BibTeX の警告 0（65 頁）。評価の語の grep（`only` は限定、`closely`・`accurately` は問いの言い回し）。文体の検査 違反 0。新しい節の行は 120 字以内。
- **影響範囲**: `manuscript/main.tex`・`sections/{introduction,recommendations,limitations,conclusions,declarations}.tex`（新規）・`sections/method.tex`・`manuscript/outline.md`・`manuscript/tools/results_tables.py`・`manuscript/generated/values.*`・本ファイル・`tasklist.md`。

## 判断 183: 完了時レビュー（code-reviewer ∥ security-checker ＋ Codex 1 巡目）の指摘を一次で確かめて直す・M12 の寄託の 4 点を研究者が決めた（2026-10-05・G-GEAR・メインの選択〔直し〕と研究者の選択〔M12〕・研究者が覆せる）

- **範囲**: `94a1ddb3..2b13cbf2`（判断 181・182 の 2 commit・22 ファイル）。Codex はコードだけ（`run-codex-review.sh 94a1ddb3..2b13cbf2 -- manuscript/tools/results_tables.py`・差分 416 行・27,948 トークン・台帳は今日 286,773 / 7 回）。散文の LaTeX は Claude 側で見た。
- **結果**: security-checker = LOW 1（約 3.5 分）。code-reviewer = HIGH 0・MEDIUM 3・LOW 4（約 4 分）。Codex = P2 3・P3 1。重なり: 対数軸の 0（code-reviewer LOW 6 と Codex P2-1）。
- **直したもの**:
  1. （security LOW）結果の JSON のシナリオ名と速さが TeX にそのまま入る経路 → `load()` で全文書を歩き、層の `scenario` が `^S[0-9]{1,2}$`、`speed` が `SPEEDS`、`by_scenario`・`tsf_end_without_result_len` の鍵がシナリオ名でなければ止める（`CELL_RE` と同じ作法・範囲外の既存の表の経路もまとめて塞がる）。実データは通る（`--check` 一致）。
  2. （Codex P2-1・code-reviewer LOW 6）図 5 の対数軸で正答率 0 や区間の下端 0 が黙って消える → 軸の下端 `FIG_LOG_FLOOR`（0.0005）で描き、そうした値があるときだけ題に断りを足す。実データの最小は 0.064 で生成物は変わらない。
  3. （Codex P2-2）層が空のとき `fig_scenario_axis` が `IndexError` → 目盛りの無い軸にする（空のオプションは落とす）。
  4. （code-reviewer MEDIUM 2）図 4 は 1 枚の軸に Windows と macOS を並べる → 題に「Windows のセルの値は別の構成概念との一致で、macOS とは比べない」を足した。
  5. （code-reviewer MEDIUM 1）全試行の範囲に外した層の数が無い → 結論（語数の制限なし）と結果の節に足した。⚠️ 要旨は 249 語で入らないので足さない。読み: 規則 (i) の「with the number of strata left out」は主の範囲に付き、「the same range over all trials」は同じ作り方の範囲を指す（判断 175 の読み (B)）。全試行の外した数は本文と結論にある。研究者が要旨にも要ると決めれば、ほかを削って足す。
  6. （code-reviewer MEDIUM 3）限界の節に「止める規則が Windows では run を選びうる」（外枠 §12・登録 §10.11）の帰結が欠けていた → 「分析した run はそうした誤りの無い run に選ばれうる・全試行が止まればセルは測られなかった」を足した。
  7. （code-reviewer LOW 4）selftest の `"70.0\%"` は不正なエスケープ → バックスラッシュを 2 つにした（`-W error::SyntaxWarning` で構文を確かめた）。
  8. （code-reviewer LOW 5）限界の印（`mark=-`）に白抜きが効かない → `fig open` を `mark options={fill=white, line width=0.4pt}` にして細い線で区別し、図 3 の題を「Open marks and thin dashes」に。
  9. （code-reviewer LOW 7）要旨の「carry-over between trials 0.0% and 5.8%」の動詞の省略 → 「excluded」を足した（249 語）。
- **直さなかったもの（理由）**: Codex P2-3（`nan` の区切りに `unbounded coords=jump` が要る）→ `main.tex` の `fig interval` に指定済みで、組んだ図で区間が分かれていることを目で確かめた（Codex は `main.tex` を見ていない）。Codex P3（描画のテストが無い）→ 道具は標準ライブラリだけにする方針（判断 181）。組版は `build.sh` と目視で確かめる。code-reviewer の「打ち消し合う」の出典が見つからない → 登録 §7（1021 行）に逐語であった（偽陽性）。
- **検証**: selftest 126 → 133 件。★ 変異（scratchpad の `mutate_figs.py`）22 本すべて狙った確認で赤（2 本は作り直した: 前の直しで行が変わって当たらなかった 1 本、確認が例外で落ちて FAIL に数えられていなかった 1 本 → 確認を例外で落ちない形にした）。実物で生成 → 図 3・4 の題だけ変化・`--check` 一致。`build.sh`: main エラー 0・未定義の参照 0・生成されていない値 0・overfull 1（以前と同じ）・BibTeX の警告 0。文体の検査 違反 0。
- **M12 の研究者の答え（4 問とも推奨どおり）**: (1) E3 の標本 `samples.tsv` は Zenodo のデータに入れる（GitHub には入れない）。(2) E3 の working 条件の観測ログも寄託する（計測の run と同じ停止規則で点検済み・寄託の前に `--pack` と `--check-deposit`）→ `dataset.tex` の `\tbd{confirmed at deposit}` は寄託のときに外す。(3) 較正パイロットの生ログを別の区分として含める（外枠 DS1 どおり・封印したセッション行は寄託のためだけに開け、解析しない）。(4) コードのリリースの DOI は GitHub と Zenodo の連携で取る（研究者の GitHub アカウントでの操作）。
- **影響範囲**: `manuscript/tools/results_tables.py`・`manuscript/main.tex`・`sections/{conclusions,limitations,results-agreement}.tex`・`manuscript/generated/fig-{dwell,text-agreement}.tex`・`.codex/budget.json`（台帳）・本ファイル。

## 判断 184: Codex 2 巡目（判断 183 の直しの境界）の指摘 2 件を直す（2026-10-05・G-GEAR・メインの選択・研究者が覆せる）

- **範囲**: `run-codex-review.sh 2b13cbf2..a315a3ea -- manuscript/tools/results_tables.py`（差分 228 行）・24,183 トークン。⚠️ 台帳の残り 13,227 が 1 回の上限 30,000 を下回りガードで止まるので、研究者の 2026-10-01 の指示（上限は必要に応じて上げてよい・`tokens_used` は触らず理由をコメントに）により `daily_token_budget` を一時的に 330,000 にし、回した後に 300,000 に戻した（`_comment_2026_10_05_raise`）。今日の記帳は 310,956 / 8 回。3 巡目は回さない（記録どおり 2 巡）。
- **指摘と直し（2 件とも一次で確かめて妥当）**: (1) 図 5 で区間の上端も軸の下端より下だと、下端だけを切り上げて上下が逆転する（上端 0 は対数軸に描けない）→ 両端とも下端で描く・断りの判定に上端も入れる。(2) `SCENARIO_RE`（`^S[0-9]{1,2}$`）がコメントの「S1〜S15」より広く、S0・S01・S16〜S99 を通す → `^S(?:[1-9]|1[0-5])$`。実データ（S1〜S15）は通る（`--check` 一致）。
- **検証**: selftest 133 → 135 件（区間全体が下端より下・S1〜S15 だけを通し S0／S01／S16／小文字／末尾の空白を止める）。変異 2 本を足して 24 本すべて狙った確認で赤、無変異は緑。生成物は変わらない。
- **影響範囲**: `manuscript/tools/results_tables.py`・`.codex/budget.json`（台帳）・本ファイル。

## 判断 185: 研究者が答えられる `\tbd`（表紙・Funding・利益相反・貢献）を埋め、Springer Nature の規程に従って AI Declaration と図の題の断りを入れる・投稿の前に研究者が結果と考察を読んで直す段を置く（2026-10-05・G-GEAR・研究者の選択）

- **研究者の指示（逐語）**: 「TDDのかしょはasskusequestionで聞いて.名前: Mikoto Miura; mail: mmiura.network@gmail.com; orcid: https://orcid.org/0009-0000-4196-0508」「Hiroshima, Japanにして」。
- **AskUserQuestion の答え（すべて推奨どおり、または研究者の記入）**: 所属 = Independent researcher（Hiroshima, Japan）／単著（貢献は CRediT の役割をすべて Mikoto Miura）／Funding なし／利益相反なし／表紙の住所と電話は書かず、投稿システム（ScholarOne）にだけ入れる（原稿は公開の repo とプレプリントにも載るため）。
- **表紙**: sn-jnl の `\author*`・`\affil*`・`\email`。⚠️ 雛形の `\orcid` は `Orcidlogo.eps` を読むが、雛形にその画像は無く、`-no-shell-escape` では eps を変換できない → `\orcidlogo` を文字（「(ORCID 0009-…)」・リンク）に置き換えた。上付きにすると所属の印「1*」とくっつくので、名前の後ろに括弧で出した。
- **見つけた欠け（`\tbd` ではない）**: Springer Nature の「AI use in manuscript preparation」（2026-10-05 に curl で原文を取得）。逐語: Green と Amber の Declaration の欄は「Clearly describe use and confirm author accountability」、Amber の例に「drafting sections based on author input」、Red（不可）に「Writing results or discussion independently; generating scientific claims or interpretations」、図は「information about the AI system used, the purpose of its use, and the extent of its contribution should be provided in an AI Declaration in your manuscript. Specific disclosure should be provided within the caption or legend of the visual content.」。
- **研究者の選択**: (1) AI Declaration は使った範囲をすべて書く（推奨どおり）。(2) 投稿の前に、結果・推奨・限界・結論を研究者が読み、主張と解釈を自分のものとして直す段を置く（推奨どおり・規程の「the argument, interpretation, and conclusions must be author-led」）。読みやすいように、節ごとに主張と根拠の対応を日本語で添える。
- **書いたもの**: `declarations.tex` に見出し「AI declaration」（Claude〔Opus・Sonnet・Haiku・Claude Code〕と Codex〔コードのレビュー〕の使い道、研究の問い・設計・登録・計測・解釈は著者、AI はデータを作っていない、著者が確かめて責任を負う）。⚠️ モデルは一次で確かめた: ループの設定 `_loop-config.json` の `headless.model` が sonnet・`watchdog_model` が haiku、`.claude/agents/loop-worker.md` が sonnet。図 1〜5 の題に「code written with the assistance of an AI tool and reviewed by the author (AI declaration)」—— 図 2〜5 は道具の `FIG_AI_NOTE`（selftest 136 件・変異 1 本を足して 25 本すべて赤）、図 1 は手で。
- ⚠️ **宣言の「The author reviewed … and is accountable」は、投稿の前に研究者が読んで直す段（上の (2)）を済ませて初めて事実になる**。引き継ぎの段に入れた。
- **検証**: `build.sh` main エラー 0・未定義の参照 0・生成されていない値 0・overfull 0・BibTeX の警告 0。表紙を画像で確かめた。文体の検査 違反 0。残る `\tbd` は M12 のもの（データと release の DOI・repo の URL・外枠の公開 commit・表 1 の版・寄託の欄）だけ。
- **影響範囲**: `manuscript/main.tex`（表紙）・`sections/declarations.tex`・`figures/components.tex`・`manuscript/tools/results_tables.py`・`manuscript/generated/fig-*.tex`・本ファイル・引き継ぎ `next-session-ime-paper-manuscript-2.md`。

## 判断 186: AI Declaration を記録どおりの文に直す —— コードの確認は道具とテスト、設計と設定は提案と承認で書く（2026-10-05・G-GEAR・研究者の選択〔2 問〕とメインの選択〔残り〕・研究者が覆せる）

- **背景**: 判断 185 の追加分を code-reviewer に見せた（`1133af38..95351748`・10 ファイル・約 4 分・HIGH 2・MEDIUM 3・LOW 4）。Codex は今日の台帳が上限を超えている（310,956 / 300,000）ので回さず、Claude 単独に縮退した。
- **一次で確かめたこと**: (1) 研究者がコードを読んだ記録は無い（コードの確認は selftest・変異・code-reviewer・security-checker・Codex だけ）。(2) 判断 98 は「研究者に問わずに決めたもの」（seed・止める規則など）、判断 86 は「メインの実装上の選択」（macOS の正解の定義）。(3) Co-Authored-By はロガーの履歴（`src-tauri/src`・`kit/`・最初の commit 2026-02-19）で Opus 4.6・4.8・5・5.5、Sonnet 4.6・5・5.5。ループの設定は worker = sonnet・watchdog = haiku。(4) 本文の「2.7 s」は `data.md` の記録から写した値（外枠の「the figures of the records … from data.md」）。
- **研究者の選択（2 問とも推奨どおり）**: (H1) 「reviewed by the author」は記録どおりの文に直す → 宣言は「The code was checked by its tests and by the reviews named above」、図の題は「code written and reviewed with an AI tool (Claude) and checked by its tests; see the AI declaration」（図 1 は「code written with an AI tool (Claude)」）。(H2) 「decided by the author」は提案と承認で書く → 「The research questions are the author's. Parts of the design, of the analysis settings and of the text were proposed by Claude; the author chose among the options presented, checked and approved them, and froze the registrations.」。
- **メインが直したもの（研究者の「すべて書く」の選択に沿う）**: 使い道に、2 つの登録・逸脱の記録・手順・外枠と節の下書き、登録と外枠の模擬査読、run の点検・寄託の梱包・解析の実行（著者の指示の下）を足した。値の出どころを「解析のコード（登録の解析・表の逸脱・exploratory と書いた解析）から生成され、記録の数（run の点検など）は run の記録から写した」に正した。外枠は「著者の外枠」ではなく Claude の下書きに含めた。kit の部品は「all the code」に。モデルの版と期間（Opus 4.6〜5.5・Sonnet 4.6〜5.5・Haiku 4.5・2026 年 2 月〜10 月）。CRediT に Validation・Resources・Project administration を足した。selftest に描いた図 5 の題の確認を足した（137 件・変異 25 本すべて赤）。⚠️ datasheet はまだ書いていないので宣言から外した —— 書いたら足す。
- ⚠️ **後で事実になる文**: 「The interpretation of the results is the author's, and the author is accountable」は、投稿の前に研究者が結果・推奨・限界・結論を読んで直す段（判断 185 の (2)）を済ませて初めて事実になる。引き継ぎに書いた。
- **検証**: `build.sh` main エラー 0・未定義の参照 0・生成されていない値 0・overfull 0・BibTeX の警告 0。文体の検査 違反 0。
- **影響範囲**: `sections/declarations.tex`・`figures/components.tex`・`tools/results_tables.py`・`generated/fig-*.tex`・本ファイル・引き継ぎ `next-session-ime-paper-manuscript-2.md`。

## 判断 187: 研究者の指示で判断 185・186 の追加分を Codex に見せ、「No AI tool produced data」を意図どおりに狭める（2026-10-05 夜・G-GEAR・研究者の指示とメインの選択・研究者が覆せる）

- **背景**: 研究者「codexは制限が解除されたはず」。止めていたのは OpenAI 側ではなく repo の台帳の 1 日の上限（今日 310,956 / 300,000）。2026-10-01 の指示（上限は必要に応じて上げてよい）により一時的に 350,000 にし、`run-codex-review.sh 1133af38..f9d7fc5b -- declarations.tex main.tex components.tex results_tables.py`（差分 119 行）を回した（22,716 トークン）。回した後に 300,000 に戻した（`_comment_2026_10_05_raise_2`・今日の記帳は 333,672 / 9 回）。判断 186 で「Claude 単独に縮退」と書いた分は、これで 2 系統になった。
- **指摘と扱い**: (1) P2「`\orcidlogo` の置き換えが組めるか」→ `build.sh` でエラー 0・表紙を画像で確かめ済み（誤検知）。(2) P2「selftest は文言の挿入しか見ない」→ 組版は `build.sh` が原稿全体を組み（図を含めてエラー 0）、図は目で確かめている。道具は標準ライブラリだけの方針（判断 181）なので LaTeX の組版の試験は道具に入れない。(3) P3「No AI tool produced data が広く読める」→ 妥当（合成入力の計画は Claude が書いた生成器が作る）。「No language model produced or altered any value of the data: the plans were generated by the plan generator from the seed, the logs were written by the programs during the runs, …」に直した。
- **検証**: `build.sh` main エラー 0・overfull 0・未定義の参照 0。文体の検査 違反 0。
- **Mac の runner**: 12:18 の run は空きがちょうど下限 8 GiB で通ったが、12:41 の run（`f9d7fc5b`）の「Disk guard」がまた落ちた → 研究者に伝えた（解消していない）。
- **影響範囲**: `sections/declarations.tex`・`.codex/budget.json`（台帳）・本ファイル。

## 判断 188: 原稿の attack-me round 1（major）の採否 —— 直す一覧を全部承認・要旨は登録 §6.1 の規則を保ち端を決めたものを添える・ICC の恒等的な 0 は値なし（逸脱 D11）・dwell の分位点の限界を探索的に足す・問 4 の大きさを結論と §8 に・Discussion は研究者の解釈を元に・公開しないタイトル頁と投稿用の組版（2026-10-05 夜〜10-06・G-GEAR・研究者の選択）

- **round 1**: `attack-me/manuscript-ime-observation/round-1/`。立場は外枠と同じ 3 つ（R1 計時の道具の検証と方法の比較・R2 書字研究の利用者・R3 メタサイエンスとデータ管理）。接地は外枠の 7 本を残し、2 本を統計の方法論（Giavarina 2015・Koo & Li 2016）に替えた。有効な査読 3 / 3、3 人とも **major**。監査役 1 本。捏造 0・注入 0・偽陽性 0・確かめられない 1（[V31] を読んだか）。外枠からの引き継ぎは R1 16 中 10・R2 17 中 13・R3 19 中 13 が解消。
- **一次で確かめた重い指摘**（`verdict.md` §2.2）:
  - (Z1) 全試行の範囲は 3 セルとも 0.000–1.000 で、S13（打ち切りを越えるよう作った場面・ロガーは仕様どおり行を書かない）が決める。主の下端は S6・S10（登録 §6.4 が規則の予測する不一致に挙げた場面）が決める。
  - (Z2) 文ごとの ICC は、参照の「1 試行あたりの変換の数」がすべての文で 1.0（分散 0）の層で恒等的に 0。`stats.py` は分母 0 のときだけ None を返す。登録 §6.11 は zero variance を「値なし（理由つき）」とする。
  - (Z4) `method.tex` の「自動更新を切った」が `data.windows.md` の記録（Defender の更新・Claude Code のセッション）と食い違う。
  - (Z5) 再現の文（凍結タグから 1 命令）が同じ節の D8・D10 と矛盾する。
  - 規程: タイトル頁の住所と電話・二重行送り・データの引用。文献 2 件の著者が TODO。
- **研究者の選択（8 問とも推奨どおり・1 問は事実の確認）**:
  1. 直す一覧（Z1〜Z49 の ★ 以外）を**全部承認**。人で使う前の情報（Z39）も事実だけの短い段落として足す。
  2. **要旨と結論は登録 §6.1 の規則を保ち**、全試行の下端が設計の場面で決まることと、主の下端が規則の予測した不一致の場面で決まることを短く添える（語数は他を削る）。プールした値（pooled と明記）は結論と §6 に書き、要旨には入れない。
  3. **ICC の恒等的な 0 は値なし＋理由**（参照の値がすべての文で同じ）にし、参照の文間の SD を表に添える。結果を見た後の報告の変更なので**逸脱 D11** に記録する。
  4. 探索的な補足は **dwell の分位点の限界（2.5・97.5 %）と ±100 ms・±1 s に入る割合**だけ足す（新しい計測なし・探索的と標識）。Windows の 1 合成あたりの行の数と、囮の長さをそろえた攻撃は足さない。
     - ⚠️ **メインの誤り（問いの前提）**: 問いに「既存の対の値から計算できる」と書いたが、確かめると結果のファイル（`e1_l1.json`）は層ごとの要約（偏り・一致の限界・中央絶対差）だけで、対ごとの差を持たない。→ 研究者に問い直した（2026-10-06）。**研究者の選択（推奨どおり）**: 凍結の照合のコードを呼ぶ探索的なスクリプトを書き、Windows はこの機械（G-GEAR の `Downloads` の書庫）で、macOS は M12 で Mac を使うときに回す。結果は探索的と標識して結果のファイルに置き、表の道具が読む。⚠️ macOS の書庫は G-GEAR に無い（引き継ぎの「G-GEAR の Downloads に同じ SHA の写し」は Windows の 1 本だけだった）。
  5. **キーワード "privacy-preserving logging" を外し**、結論と §8 に問 4 の大きさ（K=10・100 の正答率と 2/K）、値が種類ごとの数の攻撃から来たこと、「記録しないことは明かさないことではない」を書く。要旨は語数が空いた分だけ。
  6. **Discussion を置く**。⚠️ Springer Nature の方針（"Writing results or discussion independently" は AI に不可・"drafting sections based on author input" は可）に従い、研究者が結果と考察を読んで直す段で、不一致の出どころの事実を日本語で渡し、研究者の解釈を元に英語にする。
  7. **計測の run はすべて Claude Code が起動した（研究者の指示で）**（事実の確認）→ AI 宣言に「計測の run を著者の指示で起動し監視した・Windows の試行 1 を低メモリで止めた」を書く。
  8. **公開しない別のタイトル頁**（住所・電話・メール）と**投稿用の組版**（sn-jnl の `referee` の二重行送り・右上の頁番号）を作る。公開の版は今の組版のまま。判断 185 の「住所と電話は投稿システムだけ」は、規程の照合（"The title page must include …"）により、投稿用のタイトル頁にも入れる形に改める。
- ★ **メインの誤り（記録する）**:
  - context-B の持ち帰り 1 は Windows の経路を窓のイベントだけにした（判断 151 は隠蔽も含む）。既知の限界の「macOS の問 1〜3 は 2 つの解析」は全セルの誤り。
  - 外枠の Open item「試行 2 の間に Surface で何が動いていたか」は `data.windows.md` の「What else ran on the measuring machine during attempt 2」に既に書かれていたのに、引き継ぎで未解決として渡した（Surface のセッションが書いた節を、外枠と引き継ぎに反映していなかった）。
- **次**: 直す（表の道具〔Z2・Z6・Z38〕は selftest と変異で確かめる）→ 研究者が結果と考察を読んで直す段（Discussion を含む）→ round 2 を回すかは直した後に問う。
- **影響範囲**: `papers/ime-observation/manuscript/`（節・表の道具・生成物・`references.bib`・`main.tex`）・`experiment/deviations.md`（D11）・投稿用のタイトル頁と組版（公開物の外）・本ファイル・`attack-me/manuscript-ime-observation/round-1/verdict.md` §7。
- **実装（2026-10-06・G-GEAR・`08865d82`・`7629be4d`）**: 直した中身は `verdict.md` §8。表の道具（selftest 154 件・使い捨ての変異 13 本すべて赤）・探索的なスクリプト（Windows を G-GEAR で回した）・本文・D11・補遺の来歴の表・投稿用の組版とタイトル頁のひな形。

## 判断 189: 判断 188 の直しの作業中の点検（code-reviewer ∥ security-checker）の指摘を一次で確かめて直す（2026-10-06・G-GEAR・メインの選択・研究者が覆せる）

- **対象**: `f30a6e6c..7629be4d` の `papers/`。code-reviewer: HIGH 3・MEDIUM 4・LOW 9。security-checker: CRITICAL / HIGH / MEDIUM 0・LOW 4。
- **一次で確かめて真だったもの（直した）**:
  - H1: 「macOS の中央絶対差は数十 ms」は live off だけ（live on は 384・171・97 ms）→「どのセルと速さでも中央絶対差は一致の限界の幅の 1/10 未満」に（表 8 で確かめた）。
  - H2: 「macOS のロガーと Windows の隠蔽の経路は S13 に行を書かない」は誤り（Windows の S13 には 58・80・77 本の行があり、対にならないだけ）→「どの行も S13 の会話と対にならなかった（macOS は打ち切りで行を書かない・Windows は 20 秒以上の行が無い）」に。§6 の打ち切りの段落も「20 秒以上の行を書かない」に。
  - H3: D11 の影響の範囲の書き漏れ（補遺でさらに 8 つ）→ `deviations.md` に列挙。
  - M1: live on の mid・fast は参照が 1 文だけ 1 と違い、ICC がほぼ 0（`e1_l2.json` で数えた）→ 基準は広げず §7 と D11 に開示。
  - M2: 探索的な値の文に「主の範囲」を足した。macOS の値は Mac で回すまで `\tbd`（8 個）。
  - M3: Windows の下端は recall と precision で場面が違う → 分けて書いた。
  - M4・L5・security 1・2: 探索的なスクリプトに `--registered`（コミット済みの `e1_l1.json` と速さごとの dwell の n・n_zero_excluded・mae・bland_altman が一致することを要求）・書き出しの解析モジュールの SHA-256 の記録・`--out` と `--scratch`（このディレクトリの外・空）の確認を解析の前に・`open(..., "x")`・登録側の値が無いときに落ちない形。Windows を回し直した（値は同じ・記録の欄だけ増えた）。selftest 24 件。
  - L1: 「ICC は 0」→「0（ロガーも一定なら定義されない）」。L2: 丸めて 0 の値に負号を付けない。L3: 補遺の速さをまとめた表にも注。L4: 範囲が 1 値でも単位。L6: 投稿用の bibtex の警告も数える。L7: 節の番号のコメント。L8: 「no_time 単独の攻撃と少なくとも同じだけ」。L9: §5 に表の比較の名前の対応。
  - security 3: `build.sh` の出力先の検査を `papers/ime-observation` 全体に広げ、`.gitignore` に LaTeX の副産物。security 4: タイトル頁のひな形の空欄の印が消えたら `build.sh` が止まる。
- **検証**: 表の道具の selftest 156 件・変異 13 本すべて赤。探索的なスクリプトの selftest 24 件。`build.sh --submission`: main・main-submission・補遺ともエラー 0・未定義の参照 0・生成されていない値は macOS の探索的な 8 個だけ・bibtex の警告 0・overfull は main 1（§4 の頁の 2.1 pt）。`build.sh` は `papers/ime-observation/experiment/` を出力先にすると拒む（試した）。文体の検査 違反 0・要旨 248 語。
- ⚠️ **開示**: code-reviewer は「6 to 30 kana」の出典を探す grep で、`experiment/runs/windows-msime-tsf-2/plan.jsonl`（合成入力の計画・git の外）の数行を目にした（根拠には使っていない）。生ログ・封印物は開いていない。
- **影響範囲**: `kit/analysis/explore_dwell_quantiles.py`・`experiment/results/exploratory/`・`manuscript/tools/results_tables.py`・`manuscript/generated/`・`manuscript/build.sh`・`papers/ime-observation/.gitignore`・`manuscript/sections/`（§5〜§8・§10〜§14 のコメント）・`experiment/deviations.md`・`verdict.md`。
