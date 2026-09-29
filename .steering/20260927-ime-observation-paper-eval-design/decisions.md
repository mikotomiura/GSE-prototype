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
