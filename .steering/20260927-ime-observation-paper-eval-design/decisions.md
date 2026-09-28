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
