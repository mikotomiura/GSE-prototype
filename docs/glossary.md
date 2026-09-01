# ユビキタス言語定義

このプロジェクトで使用する用語を統一する。同じ概念を異なる言葉で呼ばないこと。
新しい概念を導入する際は必ずここに追加する。

## ドメイン用語

| 用語 (日本語) | 用語 (英語) | 定義 | 使用例 |
|---|---|---|---|
| 作業状態 | Work State | PC 操作に現れる行動的シグナルから推定する作業上の状態。脳内状態の直接分類ではなく、介入判断に必要な状態表現 | 「作業状態スコアを 1Hz で更新する」 |
| 認知状態 | Cognitive State | ユーザーの知的作業における内的状態。GSE では直接読める対象として扱わず、UserLabel や説明概念として限定的に使う | 「認知状態を直接読むとは主張しない」 |
| フロー | Flow | 滑らかにアウトプットが出ている行動パターンの説明語。現行 HMM の `p_flow` は flow-like continuation の参考スコア | 「p_flow は Flow 断定ではなく参考スコア」 |
| インキュベーション | Incubation | 生産的な沈黙・熟考に近い行動パターンの説明語。現行 HMM の `p_incubation` は incubation-like pause の参考スコア | 「長い休止は Incubation と断定せず介入を defer する」 |
| スタック | Stuck | 作業停滞・摩擦が強い可能性を表す説明語。`p_stuck` は **MhD（L1）が計算する** Stuck likelihood であり、**Need 層（L2）が `stuck_likelihood` として閾値消費する**（別層・別計算。[[MhD]] 参照） | 「p_stuck が高くても Opportunity が低ければ介入しない」 |
| 生産的苦闘 | Productive Struggle | 困難に取り組むプロセス自体に学習・成長の価値がある状態。GSE が保護する対象 | 「生産的苦闘を阻害しない介入設計」 |
| 不便益 | Benefit of Inconvenience | ★ **「不便であること」＝「労力（物理的／心理的）がかかること」から得られる益** [P170]。認定には 3 条件（1 益は不便だからこそ / 2 不便を被るのは受益者本人 / 3 副次的）が要る。⚠️★★★ **GSE の現行実装では条件 1 が満たされない**（Nudge は労力を課さない。不便を担う Physical Anchor は未実装）→ ★ **「不便益を *設計思想として引く*」と書き、「不便益 HCI *である*」とは書かない** | 「不便を担うのは Physical Anchor であって Nudge ではない」 |
| ナッジ | Nudge | `InterventionDecision.action == "nudge"` で発動する軽度介入。右端から小さく現れるサイドカードとして表示 | 「Nudge が表示されたがユーザーは作業を継続した」 |
| ~~ウォール~~ | ~~Wall (Lv2)~~ | ⚠️★★★ **2026-08-23 に削除**（**ADR-015 D1**）。★ 旧義: 全画面ロック + スマートフォンアンロックの強制介入。**現行に画面を塞ぐ介入は存在しない** | ⚠️ **新規に使わない**（★ 履歴記述でのみ可） |
| ~~ゼンタイマー~~ | ~~Zen Timer~~ | ⚠️★★★ **2026-08-23 に削除**（ADR-015 D1・Wall 専用だった） | ⚠️ **新規に使わない** |
| ~~モンクモード~~ | ~~Monk Mode~~ | ⚠️★★★ **2026-08-23 に削除**（**ADR-015 D2**）。★ 作用は Wall 抑制だけだったため、Wall 削除で**何もしないトグル**になった | ⚠️ **新規に使わない** |
| ~~早期解除~~ | ~~Early Unlock~~ | ⚠️★★★ **2026-08-23 に削除**（ADR-015 D1・`wall_server.rs` ごと） | ⚠️ **新規に使わない** |
| フィジカルアンカー | Physical Anchor | **画面から離れることへの方向づけ**（★ 未実装。⚠️ 旧称 Lv3/Lv4 —— **段階呼称は 2026-08-30 に廃止**・ADR-018 D7）。⚠️ **離席・歩行という [[身体的回帰]] へ誘う**が、★★★ **系は開始も完了も判定しない**（**ADR-018 D1**。⚠️ 既決 D11 条件 2「完了条件は時間・往復」は**取り下げ済み**）。⚠️★★★ **時間長・往復回数の閾値を系が置かない**（D2）。★ タイマー / カウントダウン / 残り時間表示を**実装しない** | 「Physical Anchor は表現層の *出口* であり、外すと表現層が装飾に落ちる（既決 D8）」 |
| グラウンドトゥルース | Ground Truth (GT) | ユーザー自身が主観的に付与する認知状態ラベル。**v0.3 (D-13) 以降、較正スモーク段ではこの語を使わず criterion label と呼ぶ** (測定法が較正で成立して初めて妥当性を語れるため)。GT は核検証フェーズ通過後にのみ正当化される | 「この段階のラベルは GT ではなく criterion label」 |
| 主観参照ラベル | criterion label | 較正スモークで収集する主観ラベル。GT を名乗らず「妥当性検証の参照基準候補」と位置づける。実体は Q1 摩擦 / Q2 前進の 2 軸 (各 1–5) | 「criterion label を順序 C-index で X/Y と照合」 |
| ユーザーラベル | UserLabel | 主観ラベルの総称。**2 経路が併存する**: (1) v0.3 較正の主データはプローブ回答で、NDJSON `realtime_label` (Q1/Q2 各 1–5) として記録 (= criterion label の実体)。(2) ホットキー自己申告は今も `logger::UserLabelKind` の 3 値 enum (`{Flow, Incubation, Stuck}`) のまま `user_label` 行に記録され、補助データとして残る | 「ランダムプローブ回答が realtime_label として記録される」 |
| ランダムプローブ | random probe | モデル出力と無関係にセッションごと ≤2回/30分、一様ランダムな時点で表示する Q1/Q2 の問い。較正スモークの**主データ源**。backend が時刻を生成し `probe_assignment` で監査記録 (v0.3 §4) | 「ランダムプローブの直前 30 秒を分析窓にする」 |
| 時間隔離 | time isolation | 申告は未来の打鍵を汚染するが過去は汚染しないという性質を使い、分析窓を申告**前** (プローブ t に対し t−31s〜t−1s) に限定して P1 汚染を構造的に解く設計 (v0.3 §4.2) | 「時間隔離窓 t−31s〜t−1s の特徴量だけ使う」 |
| 自己マーカー | self marker | 被験者が「今 Stuck だ」と思った瞬間に押す任意ホットキー。希少な深い Stuck を拾う**副データ** (Precision・事例用)。Recall 分母には混ぜない (v0.3 §4.1) | 「self_marker は分母に入れず事例探索に使う」 |
| プローブ源 | ProbeSource | `realtime_label` の発生源を区別する enum (`logger::ProbeSource`)。`random_probe` (一様ランダム、主データ) / `self_marker` (自己申告、副データ) | 「ProbeSource で Recall 分母対象かを判定」 |
| プローブ参照 | ProbeRef | `random_probe` には `probe_id` が必ず付き、`self_marker` には付かないという不変条件を型で表す (`logger::ProbeRef`) | 「ProbeRef により probe_id の有無を型で保証」 |
| skip 理由 | SkipReason | プローブ回答の skip 種別 enum (`logger::SkipReason`)。`none` (回答済) / `dont_remember` / `dismissed`。MNAR 対策 (PreReg-2/7) の分析軸 | 「dont_remember と dismissed を分けて skip bias を見る」 |
| トラック | Track | 較正スモークのセッション種別 enum (`logger::Track`)。`main` (本作業) / `exploratory` (探索)。`session_meta` に記録 | 「session_meta の track を main に設定」 |
| 課題種別 | TaskKind | 較正スモークの作業内容分類 enum (`logger::TaskKind`)。`argumentative` / `correspondence` / `creative` / `vibe_coding`。`session_meta` に記録 | 「TaskKind=vibe_coding で β を coding 寄りに」 |
| 想定象限 | ExpectedQuadrant | 尺度理解テスト (ビネット) の正解ラベル enum (`logger::ExpectedQuadrant`)。`flow` / `stuck` / `incubation` / `idle` の 4 値。Q1/Q2 の 2 軸とは別物 (教示の正解) | 「ビネット回答を ExpectedQuadrant と照合し理解度を測る」 |
| 介入応答 | InterventionResponse | 介入提示に対するユーザー側の応答を残す NDJSON 行 (`intervention_response`)。判定側 `intervention_decision` とは別の「ユーザー応答側」ログ。固定カテゴリ + 時刻のみ (WBS 0.8 / v0.4 §9) | 「Nudge dismiss を intervention_response として記録」 |
| dismiss 理由 | DismissReason | 介入を閉じた理由の固定カテゴリ enum (`logger::DismissReason`)。`not_stuck` (詰まってない=Need 誤り) / `want_to_struggle` (今はもがきたい=Opportunity 誤り) / `just_close` / `silent` (理由未選択)。Need 誤りと Opportunity 誤りを分離する (WBS 0.8 / v0.4 §9) | 「dismiss_reason=not_stuck は Need 過検出の証拠」 |
| 実験条件 | Condition | セッションの実験条件 enum (`logger::Condition`、`session_meta.condition`)。`blind_calibration` (Phase 1b) / `a` / `b` (Phase 2 AB/BA) / `nudge` / `defer` (Phase 3 MRT) / `baseline` | 「condition=blind_calibration の較正セッション」 |
| ラベルプール | LabelPool | ラベルの収集環境を区別する enum (`logger::LabelPool`、`session_meta.label_pool`)。`calibration_blind` (blind 較正・X1 判定に使用) / `post_intervention` (介入可視・合算しない) | 「X1 判定は calibration_blind プールのみ」 |
| ペースト文字数 | external_paste_chars | ペースト時のクリップボード**文字数 (整数) のみ**を記録する `paste` 行のフィールド。中身は数えた直後に破棄し保存・送信しない。(b) 自力解決率 `manual_contribution_ratio` の分母 (v0.4 §4.2 / CD1) | 「external_paste_chars で外部貼り付け量を測る」 |
| Stuck エピソード | StuckEpisode | アウトカム指標の基盤抽象。`p_stuck >= 0.60` (既定トリガ) の feat が `merge_gap` (30s) 以内の中断を挟んで連続する区間。エピソード後 5分内の回復/paste/net_diff を判定する単位。トリガは `StuckTrigger` enum で**将来** UserLabel / InterventionFired へ拡張予定だが**現状 PStuckThreshold のみ実装** (WBS 0.10 / outcome-metrics CD-OM1) | 「Stuck エピソードごとに自力回復したか判定する」 |
| 手入力寄与率 | manual_contribution_ratio | (b) 自力解決率の主指標。`manual_insert_chars / (manual_insert_chars + external_paste_chars)`。手入力 (文字生成キー−backspace, content-free) と AI ペースト量の比 (v0.4 §4.2) | 「manual_contribution_ratio が低い=AI コピペ依存」 |
| 自力回復率 | productive_manual_recovery_rate | Stuck エピソード後 5分内に **external paste なし**かつ **net_diff 正進行** (手入力純増≥1) で回復したエピソードの割合 (分母=回復したエピソード)。(b) のもう一つの主指標 (v0.4 §4.2) | 「自力回復率が高い=もがいて自力で抜けた」 |
| アウトカム指標 | OutcomeMetrics | `gse-replay --metrics` が捕捉済み NDJSON から算出する (a)AI依存度 / (b)自力解決率の集合。`SessionMetrics.outcome` に additive 付与。すべて数値のみ (本文非混入)。`external_paste_count` / `large_paste_rate` / `paste_after_stuck_rate` / `self_recovery_without_paste` 等を含む (WBS 0.10 / v0.4 §4.1・§4.2) | 「アウトカム指標は捕捉後に再計算できる」 |
| コンテキストビーコン | context_beacon | 内容非由来の cue (5分ごとランダムな色・図形、ログは ID のみ)。エピソード的目印になるが状態のヒントを漏らさない。波形 cue の confound を断つための比較条件 (v0.3 §5) | 「context_beacon は意味を持たない記号」 |
| 較正スモーク | calibration smoke | n=3〜5 で測定法 (ラベル方式) が成立するかを先に検証する研究フェーズ。効果量推定・破綻検出に限定し、確証主張はしない (v0.3 §3, §11) | 「較正スモークで測定法ゲートを通してから核検証へ」 |
| 較正モード (blind dashboard) | calibration mode | 較正セッション中、被験者にモデル出力 (推定状態/Flow・Incubation・Stuck 確率/p_stuck/GT counter/状態色) を**一切見せない**メイン画面表示モード (`App.calibrationMode`、既定 ON)。主観回答のアンカリング汚染を防ぎ測定独立性を守る。frontend 表示分岐のみ (backend/schema 不変) | 「較正モードでは推定状態を出さない」 |
| 尺度理解テスト | scale comprehension test | 本番前に 8 ビネット (2×2 象限×2) で Q1/Q2 が独立 2 軸として理解されているか検査する事前ゲート (PreReg-1) | 「尺度理解テストに合格してから本番データを取る」 |
| 2段ゲート | two-stage gate | 「測定法の失敗」と「モデルの失敗」を別々の Go/No-Go で事前宣言する反証可能化の仕組み。測定法ゲート → モデルゲートの順 (v0.3 §7) | 「測定法ゲートを通過しない限りモデル評価に進まない」 |
| ゲート対応 (GATE↔PreReg) | GATE–PreReg mapping | WBS の **GATE1–3** と preregistration の **PreReg-1..8** の対応。**GATE1 尺度理解 ↔ PreReg-1**（**現行スモークでは延期**・比較条件段で発効）/ **GATE2 測定法 ↔ PreReg-2・-3**（回答率 ≥80% / latency 中央値 ≤10s / 有効 ≥20 件/人）/ **GATE3 モデル（順序 C-index 中央値 ≥0.65 & 全員 >0.55）↔ PreReg-4**。0.65/0.55 は PreReg-4 で凍結した事前登録値。SSOT は `docs/preregistration-v0.3.md` | 「GATE3 は PreReg-4 のモデルゲート。現行スモークは GATE1 を延期し GATE2 起点」 |
| 順序一致度 | C-index (concordance index) | 「X が大きい区間ほど主観 Q1 も大きい」という順位の一致割合。0.5 が偶然・1.0 が完全一致・0.5 未満は逆方向。順序尺度と相性が良く方向を保つ。`\|r\|≥0.30` の代替 (v0.3 §7) | 「被験者内 C-index 中央値 ≥0.65 で Go 候補」 |
| 前向き固定 holdout | prospective fixed holdout | 各人の最初の 2 セッションで β を較正・凍結し、残りで完全固定評価する設計。「今日較正→明日使用」の実運用に一致。LOSO/LOUO の時間リークを避ける (v0.3 §8) | 「前向き固定 holdout で forking paths を排除」 |
| 時間隔離窓 | temporal isolation window | プローブ時刻 t に対し分析対象を **t−31s..t−1s** (プローブ前) に限定し、申告後 (t..t+60s) を破棄することで「申告が打鍵を汚染する」P1 を時間順序で構造的に隔離する仕組み (`realtime_label.analysis_window_*`、v0.3 §4.2 / D-8) | 「時間隔離窓内の feat だけで X を集約する」 |
| MNAR 範囲報告 | MNAR range reporting | 未回答プローブを「全て高摩擦」「全て低摩擦」と置いた上下限を併報する欠測の感度分析。被験者除外はせず (高欠測者を落とすと MNAR を強化)、無回答率 >20% 注意・>30% 主分析不成立 (v0.3 §10 / PreReg-7) | 「C-index を MNAR 上下限つきで報告する」 |
| コホート判定 | cohort verdict | 被験者別 calibration レポートを横断集約し、2段ゲートでコホート全体の Go/Kill/INCONCLUSIVE/DataInsufficient を出す判定 (`gse-cohort` / `analysis::cohort`)。ゲート駆動は各人の C-index 中央値 (PreReg-4)。`model_gate`/`measurement_gate` を再利用 (v0.3 Task E) | 「gse-cohort でコホート判定を出す」 |
| データ不足判定 | DataInsufficient | コホート判定の値の 1 つ。主指標被験者0名・提示プローブ0件・PreReg-5 最低要件 (eval≥6/probe≥16) 充足者なしのとき、無理に Go/Kill とせず「データ拡充が必要」と正直に報告する状態 (v0.3 §11 主張限界) | 「PreReg-5 未達なので DataInsufficient」 |
| Need | Need | 介入が必要そうかを表す層。MVP では主に `p_stuck` を `stuck_likelihood` として利用する | 「Need は高いが Opportunity が低い」 |
| Opportunity | Opportunity | 今介入してよいかを表す層。idle、post-burst pause、cooldown、daily cap、recent dismiss で判定する（⚠️ **2026-09-01 訂正: 「Monk Mode」を削除** — ADR-015 D2 で機能ごと削除済み） | 「Opportunity が低いため defer する」 |
| 受容性 | Receptivity | 今このユーザーが介入を受け取れる状態かを表す層。**Layer 5（Opportunity 側）に属する**。現行実装は cooldown + daily_cap + recent_dismiss + idle gate の**分解形**で、統合スコアは持たない（**ADR-007**）。⚠️ **潜在状態（Layer 4）に置かない**——入力がシステム状態と履歴であり潜在状態からの放出ではないため（**ADR-009**） | 「Receptivity は Layer 5。Layer 4 の潜在状態に混ぜない」 |
| 自力回復リスク | self_directed_recovery_risk | このユーザーが、この task 文脈で、**近い時間範囲（horizon H）内に自力による前進を回復できない確率**。Layer 4 の出力として `WorkStateEstimate` に additive 追加する提案（**ADR-009**・Proposed）。旧 X 軸（Cognitive Friction）の後継候補で、criterion が主観プローブでなく**行動**である点が決定的に異なる | 「recovery risk 単独では強介入を出さない」 |
| 前進 proxy | progress_proxy | 個人×task_kind×phase 基準で正規化した**純産出の持続**（窓内の 挿入−削除 打鍵数を個人基準で正規化し、T 秒以内に取り消されないこと）。content-free（打鍵数と時刻のみ）。`self_directed_recovery` ラベルの構成要素 | 「progress_proxy が個人基準を超えたら回復とみなす」 |
| 判断エピソード | Decision Episode | ML の収集単位。全打鍵でなく session start / phase change / pause onset・recovery / externalization / revision loop / intervention decision・outcome / session end を境界とする短い区間。種別・時間・回数・遷移のみを保存する | 「raw event でなく Decision Episode 単位で ContextSnapshot を作る」 |
| 個人プロファイル保管 | PersonalizationStore | `user × task_kind × phase` の個人プロファイル（基準値・写像係数・介入効用）を**ローカル保持**する部品。外部送信しない。更新するのは `OnlineUpdater` で、**潜在状態の構造は更新しない**（**ADR-008**） | 「PersonalizationStore の永続化には同意と削除 UI が要る」 |
| 打ち切り | censoring（recovery ラベル） | ⚠️★★★ **2026-08-01 に扱いが変わった（2026-08-21 に本欄を追随させた）**。content-free 制約下では検索・別デバイス・口頭相談などの外部化が観測できないのは**不変**だが、観測できない離脱を**まとめて「打ち切り」と呼ばない**。★ 3 つに分ける: `externalized`(paste) = **競合イベント** / `left_observation`(focus 喪失・アプリ切替、**回数のみ**) = ⚠️ **競合と真の打ち切りの混合（潰さない）** / セッション終了 = **管理的打ち切り**（independent）。⚠️ 生存解析の独立打ち切り仮定は「事象を起こしやすいかどうかで選択的に離脱していない」ことを要求するが [V59]、GSE の focus 喪失は「詰まったから離脱した」形で起こりうるため**破れている疑いが強い** | 「`left_observation` は**混合物**なので、独立打ち切りと決めつけずに上下界で挟む」 |
| 競合イベント | competing risk | ★ その発生が目的事象（`recovery`）の発生を**排除する**事象 [V61]。GSE では `externalized`(paste) —— 外部化して解決したなら**自力回復ではない**。⚠️ **競合イベントを単純に打ち切り扱いすると発生率が上方にバイアスする**（競合事象が互いに独立でも生じる） | 「paste は打ち切りではなく競合イベントである」 |
| 上下界（recovery） | recovery risk bounds | ★ `left_observation` の内訳は**データから同定できない**ため、両極端の仮定で `self_directed_recovery_risk` を挟んだ区間。**下界** = 全て独立打ち切り（risk 最小）/ **上界** = 全て競合イベント（risk 最大）。⚠️★★ **推定器は 1 本**で、読み出し段階だけを切り替える（2 本学習すると係数まで変わり「仮定だけを変えた比較」でなくなる）。⚠️ **反証ゲート G2（現行）はこの幅が介入判断を反転させないか**であり、★ **旧 G2「打ち切り率が閾値超なら失格」は 2026-08-01 に意味を失って置き換えられた** | 「上下界の幅が介入判断を反転させるなら `self_directed_recovery` は目的変数として使えない（G2）」 |
| 沈黙ギャップ | silence gap | 連続する 2 つの打鍵のあいだの無打鍵区間。⚠️ 既存 NDJSON から成分分解できるのは **30 秒以上**のものだけである（`lib.rs` の間引き（`if health == prev_health && !rehook { continue; }`） が `hook_health` 行を状態変化時のみ出力し、`liveness.rs` の `log_after_ms` が 30 秒であるため） | 「micro 帯（2–15 秒）の沈黙ギャップは既存ログでは分解できない」 |
| 在席×非打鍵 | present_not_typing | 沈黙ギャップのうち、**OS が入力を観測しているのに自前の打鍵フックが呼ばれていない**時間。`liveness.rs::step` が `starved_ms` を進める区間そのもので、マウス・トラックパッド等の非キーボード入力を含む。⚠️ **「作業している」ことの証明ではない**（入力デバイスに触れたことしか言えない） | 「この沈黙は在席×非打鍵が 80% を占める」 |
| 入力皆無 | no_input | 沈黙ギャップのうち、**OS の最終入力時刻が動かない**時間。`liveness.rs::step` が `starved_ms` を凍結する区間。⚠️ **離席・静止した読書・思考を区別しない** | 「入力皆無が長い沈黙は離席とは限らない」 |
| 在席割合 | presence_ratio | 沈黙ギャップにおける `peak_starved_ms / gap_duration_ms`。0 に近いほど入力皆無、1 に近いほど在席×非打鍵。⚠️ 30 秒未満の starvation は記録されないため**下側が切れている** | 「presence_ratio を T0（沈黙長のみ）に足して勝ち幅を測る」 |
| 打鍵再開 | typing_resumption | 沈黙ギャップが打鍵によって終わること。⚠️★ **回復（recovery）ではない**——別作業を始めただけの可能性を排除できないため、`self_directed_recovery` と同一視しない | 「typing_resumption は recovery proxy であって recovery ではない」 |
| 関与の再開 | re-engagement | ★★★ **demanding な作業のあとに戻るのは「処理能力」ではなく「投資を続ける意思」である**という枠組み（[P203] Lin et al. 2020・事前登録 4 実験・N=686・拡散モデル: 努力の行使が下げるのは `response caution` であって抑制制御ではない）。★ この低下は**可逆**で、**報酬を上げるだけで行動・P3・瞳孔径が揃って戻る**（[P209] Hopstaken et al. 2015 逐語 *"After increasing the rewards, all measures reverted to higher levels."*）。⚠️★★★ **「回復 / 消耗 / リソースの補充」で言い換えてはならない** —— それらは**限定資源モデル（ego depletion）の語彙**であり、**事前登録・大規模の検定で否定されている**（⚠️ **「死んだ」とは断定しない** —— [P202] は *"the available evidence is **inconclusive**"*、[P204] は **d = 0.10** の小効果を報告している。→ `research-positioning.md` §3 (b) に両方併記）（[P199] d=0.04 / [P200] d=0.06 / [P201] PEESE b=0.003）。★ **注意回復理論（ART）も同じ穴に落ちる**ため理論基盤に使わない（[P10] / [P192]・→ `research-positioning.md` §3）。★ **GSE にとっては技術的にも有利**: 限定資源モデルは単調減衰を予測するが観測されず、生き残った説明が予測する**変動し・文脈依存で・可逆な関与の低下**こそ、30 秒ローリングウィンドウが実際に検出できるものである | 「Physical Anchor が接地するのは*関与の再開*であって回復ではない」 |
| 探索トラック | exploratory track | 事前登録の適格性ゲート（`keydown ≥ 100`）を適用しない解析系統。⚠️ **確証主張には使わない**。確証トラック（ゲート適用済み）と結果を混ぜない | 「本実験は探索トラックなので確証主張に使わない」 |
| 形成的研究 | formative research / measurement development | ★ **何を測るべきかを決めるための研究**。⚠️ **効果や利得を推定しない**ため `§9` A-Q3 の解除条件は発動しないが、**利得を一言でも主張した瞬間に発動する**（**ADR-012**） | 「これは形成的研究なので利得を主張しない」 |
| 沈黙被覆率 | silence coverage | ★ **≥30 秒の沈黙ギャップの総時間のうち、あるチャネル集合のイベントが覆った割合**（各イベント時刻 `t` が `[t−w, t+w]` を覆うとし、重なりは和集合で 1 度だけ数える）。⚠️ **分母から打鍵の時間を定義上除いている**ため、「頻度が高い操作＝打鍵」が再び選ばれる退行が起きない。⚠️ **「入力があった」ことしか言わず「作業していた」ことの証明ではない**（**ADR-012 D1**） | 「この層の沈黙被覆率は全員で θ を超えた」 |
| 限界寄与 | marginal contribution | ★ **あるチャネルを候補集合から抜いたときの沈黙被覆率の低下**。superset への採否をこれで決める（**ADR-012 D8**）。⚠️ 学習器を当てるのではなく記述統計である | 「限界寄与が δ 未満なので superset に入れない」 |
| 計器の自己記述 | instrument self-description | ★ **そのログを出したビルドが「何を記録できたか」をログ自身に刻むこと**（`meta.capabilities` ＋ `app_version`）。これにより解析側が「**信号が無い**（宣言あり・行 0）」と「**計器が無い**（宣言なし）」を機械判定できる。⚠️ **`hmm_version` では代用できない**（HMM の版であって記録能力ではない）。⚠️ **送出元ベースで決め `#[cfg]` を反映する**（**ADR-013 D1/D2**） | 「capabilities に無いので、これは信号が無いのではなく計器が無い」 |
| 閾値ゲート付き行種 | threshold_gated line type | ★ **出力に閾値条件が掛かっている行種**（`hook_health` / `starve_window`）。⚠️★★★ **0 行は「信号が無かった」を意味しない**（閾値未達と区別できない）ため、解析側は**判定不能**として扱う。⚠️ `unconditional` と同じ集合に混ぜると、`capabilities` 自身が「計器が無い」と「信号が無い」の取り違えを再導入する（**ADR-013 D1**） | 「`starve_window` は threshold_gated なので 0 行から沈黙が無かったとは言えない」 |
| micro 沈黙窓集計 | starve_window | ★ **30 秒未満の在席×非打鍵（micro 帯）を 60 秒窓で数え上げた行**（`n_lt30` / `sum_lt30_ms`）。⚠️★ **`n_lt30 == 0` の窓は出力しない** —— 毎分必ず 1 行出すと「分単位の在席/中断の連続タイムライン」になり労務監視的な二次利用に転用されうるため。⚠️ **失うのは micro 沈黙の *位置***（本数と合計は残る）。★ `hook_health` の意味論は 1 文字も変えないので**旧ログと新ログを混ぜて比較できる**（**ADR-013 D4**） | 「starve_window があるので micro 帯の量が測れる」 |
| 落下差分 | dropped_delta | ★ **前の `hook_health` 行からの `dropped` の増分**。⚠️ `dropped` は**累積カウンタ**なのに解析側が「この区間で落ちた」と読む誤りが実際に起きた（前タスクの除外規則・code-reviewer HIGH）。★ 累積の `dropped` は非破壊で残し、差分を**併記**して誤読を消す（改名 `dropped_total` は breaking なので採らない・**ADR-013 D4**） | 「dropped ではなく dropped_delta を見る」 |
| G1 リブート | G1 reboot | ★ **G1 を計器と運用だけ直して測り直すこと**（2026-08-19 研究者決定）。⚠️★★★ **設計の問い（何を測るか・条件・ブロック構成・分析計画）は 1 文字も変えない**。P010 は**確証標本から外しパイロットとして保存**し（削除しない）、新たに 3 名を取り直す。★ 「1 名分の損失」ではなく「**計器を直してから測り直す機会**」であり、G1 の停止期間がそのまま ADR-013 の実装窓になる | 「G1 リブートの範囲は計器＋運用に限る」 |
| 収集レジーム | collection regime | ★ **「どういう条件下で集めたか」の区分**。⚠️ **1 つの語（「収集」）で別物を指すと主張の格が混ざる**ため、名前を付けて分ける（**ADR-014 D1**）: **R1 統制ブロック**（G1・5 分 × 10 ブロック・★ **確証**＝反証ゲート）/ **R2 宣言ブロック**（ADR-012 Stage 1・別計測器・★ **形成的**）/ **R3 自然作業の常時収集**（GSE 本体・⚠️ **形成的のみ**）。⚠️★★★ **R3 のデータで確証仮説を判定しない**（ADR-014 D2） | 「これは R3 のデータなので確証には使わない」 |
| 常時収集 | continuous natural-work collection (R3) | ★ **統制も宣言ブロックも置かず、通常の作業を長期連続で記録すること**。★ **非打鍵チャネル（フォーカス遷移の時刻 / 離脱の滞在時間 / ポインタの量子化スカラ）を集める** —— ⚠️ 打鍵のみでは **`left_observation` を 1 件も観測できず**（実装ゼロ・フォーカス未購読・`starved_ms` はマウス込み）、自然作業時間の **84.3%** を「何も起きていない」と記録し続ける。⚠️★★★ **ただし「全部」ではない**: **R3 自身の段 1 を実データ前に凍結**し、**役割カテゴリは入れない**（[P117] の穴）。★ **記録のみで推論に 1 バイトも流さない**（Tier 0 配線の先例・superset を確定するのは段 3）（**ADR-014 D4 / D4b**）。⚠️ R3 は定義上「**在席の連続タイムライン**」を作る（ADR-013 D6 が避けたもの）ので、**同意と保管の要求が R1 / R2 より重い**（ADR-014 D5/D7/D8） | 「R3 は非打鍵を集めるが、記録のみで段 3 には触れない」 |
| R3 の段 1 | R3 candidate freeze | ★ **R3 が集めるチャネルを、実データを見る前に人が凍結すること**（ADR-012 D2 段 1 の手続きを R3 に適用）。⚠️★★★ **ADR-012 D4 の層順序（L-a で足りたら L-b を集めない）は R3 に適用しない** —— ★ **判定量が違う**（ADR-012 = 沈黙被覆率 / R3 = **G2 の上下界の幅**）。⚠️ **L-a は「何らかの入力があった」の 2 値なので、離脱と在席×非打鍵を定義上区別できず、「L-a で足りる」分岐が存在しない**（**ADR-014 D4**） | 「R3 の段 1 は凍結済みなので、後から候補を足すなら別 ADR」 |
| **O1** | O1 (observation study 1) | ★★★ **自然作業の長期記録研究**（2026-08-23 命名）。⚠️ **G1 と対をなす *研究* の呼称**であり、★ **ゲートではない**（G1 は研究名とゲート名を兼ねるが、O1 は研究名のみ。⚠️ O1 が入力を作るゲートは **G2**）。★ 位置づけ: **収集レジーム = R3** ／ **実験 dir = `left-observation-decomposition`** ／ **主張の格 = 形成的のみ**（ADR-014 D2）。⚠️★★★ **`L1` にしなかった理由**: `L0`/`L1`/`L2` は**推論の層**（L0 = X/Y 二軸プロキシ＝確証の核 / L1 = Stuck / L2 = Need 判断性能）で埋まっており、★ **確証の核と衝突する**。`L-A`〜`L-C`（ラベルチャネル）・`L-a`〜`L-d`（取得コスト層）も L を使っている | 「O1 は形成的なので確証には使わない」 |
| O1 の実験名 | left-observation-decomposition | ★ **O1 の事前登録と結果を置くディレクトリの slug**（`experiments/<YYYYMMDD>-left-observation-decomposition/`・2026-08-23 確定）。★ 既存の流儀どおり**方法ではなく問いを名指す** —— O1 が答えるのは **`left_observation` の内訳が割れるか**（ADR-009 D2）。⚠️ **ADR-012 Stage 1 の `nonkeystroke-silence-coverage` とは判定量が違う**（あちらは沈黙被覆率・こちらは **G2 の上下界の幅**）。⚠️ 日付は**作る日**＝ G1 の収集完了後 | 「O1 の事前登録は left-observation-decomposition に置く」 |
| O1 の被験者向け呼称 | "long-term recording of everyday work" | ★ **「O1 普段の作業の長期記録」**（2026-08-23 確定）。consent 文書のタイトルに使う。⚠️ G1 の「**G1 統制タスク実験**」と対をなし、★ **統制タスクではないこと**が被験者にも分かる形にする。⚠️ 「常時収集」という語は**被験者向け文書では使わない**（★ ADR / 内部文書では R3 の定義語として使い続ける） | 「同意文書のタイトルは『説明・同意文書（O1 普段の作業の長期記録）』」 |
| 参照チャネル | reference channel | ⚠️★★★ **ADR-012 D12 の「参照」は *画面録画* を指す**（検証用サブサンプルのみ・研究者 PC の暗号化領域・**コード化直後に破棄**）。★ `.idea/20260819-…` メモが「**参照計測器**」と呼んでいる*行動*計測器（ADR-012 D7 の別計測器）と**別物である**。⚠️ **同じ「参照」の語で混同しない** | 「参照チャネル（録画）と別計測器（行動）を混同しない」 |
| 試行の連番 | attempt sequence number | ★ **提出物 `.age` に付くブロック番号が、プロトコルのブロック番号ではなく *起動した試行* の連番であること**。`reconcile.rs::next_block_number` が `.age` 名と `manifest.jsonl` の**最大値 + 1**（ディスク突き合わせ）で決めるため、中断した試行も番号を 1 つ消費する。⚠️ **対応付けは `manifest.jsonl` と NDJSON の中身で復元する** | 「block08 は 8 ブロック目ではなく 8 回目の試行である」 |
| アウェイアイドル | away_idle | `idle_ms ≥ 180秒` で**介入を全停止**するサプレッション (席を離れたら黙る=不便益)。一次抑制は idle 閾値そのもの。加えて放置で p_stuck も低下するため二重に介入は出ない (idle≠Stuck) | 「10分放置で介入が出ないのは away_idle で正常」 |
| 介入判断 | InterventionDecision | `analysis::intervention` が返す介入ポリシー出力。`none` / `nudge` / `defer`（⚠️ **2026-09-01 訂正: `wall` を削除** — ADR-015 D1。実測 `intervention.rs:16-20`） と説明スコアを含む | 「InterventionDecision を NDJSON に記録する」 |
| defer | defer | Need はあるが、今は介入機会ではないため先送りする判断 | 「active typing 中なので defer」 |
| daily cap | daily cap | 1日あたりの介入回数上限。通知疲れと過介入を防ぐ | 「Nudge daily cap（6 回/日）に達したので defer」（⚠️ **2026-09-01 訂正 —— 旧例は「Wall daily cap により defer」。Wall は ADR-015 D1 で削除済み**） |
| cooldown | cooldown | 介入後の再介入禁止時間。**Nudge は 10 分**（実測: `src-tauri/src/analysis/intervention.rs:5` `NUDGE_COOLDOWN_MS = 10 * 60 * 1000`）。⚠️ **2026-09-01 訂正 —— 旧文の「Wall は 60 分」は失効**（ADR-015 D1 で Wall ごと削除。★ 現行に Wall 系の定数は 1 つも無い） | 「cooldown 中なので Nudge を抑制」 |
| recent dismiss | recent dismiss | 直近で介入が拒否された事実。MVP 初期値では 20 分間、同種介入を抑制する | 「recent dismiss により defer」 |

### 表現層 (メディア表現 / 音)

> 由来: `.steering/20260811-impact-and-cognitive-core-map/media-expression-spec.md` §1–§5、
> 既決 D13–D21 / S0-D1–S0-D14 / S3-D1–S3-D16 / S4-D1–S4-D7。⚠️ **介入 (Nudge / Physical Anchor) とは別系統**であり、
> 表現層は**介入判断を行わない**（状態を音に写すだけ）。

| 用語 | 英語表記 | 定義 | 関連用語 |
|---|---|---|---|
| 表現層 | expression layer | MhD の出力 (`ewma_x` / `ewma_y` / `p_flow`・`p_inc`・`p_stuck`) を**常時リアルタイムで音・映像に写す**層。★ **推定も介入判断もしない**（出力を入力として使うだけ）。版は `EXPR_VERSION` で刻む | `EXPR_VERSION`, 層 0–3 |
| 層 0 / 基層 | layer 0 / bed | 55–110 Hz 帯の持続音 ＋ **整数次倍音のみ**（非調和成分ゼロ・sharpness 低）。★ **状態に応答しない**——[P48] が要求する「自分の通常」の参照点。⚠️ **2026-08-12 改訂 (S3-D12)**: 「不動である」ことは役目ではない。**状態と無関係な自律変異は許される**（並置を成り立たせているのは「状態に応答しないこと」であって「変化しないこと」ではない） | 層 1–3, ドローン, 層 0 の自律変異 |
| 層 1 / うねり | layer 1 / swell | 摩擦 (`ewma_x`) を帯域幅・スペクトル重心に写す層。全遷移は時定数 ≥60 秒 | 層 0 |
| 層 2 / 粒子 | layer 2 / grain | 前進 (`ewma_y`) をグラニュラー密度に写す層。★ **粒子率の下限 100 grains/s**（下回ると粒が個別に聞こえ、リズムとして分節する＝ISE 側） | 分節, 層 0 |
| 層 3 / 空間 | layer 3 / space | 残響時間・初期反射・定位の広がりで状態の遠近を写す層。★ **音色を変えない** | 層 0 |
| ドローン | drone | 層 0 が鳴らす持続音そのもの。★ **オンセット・拍・音高のステップ・実物音の引用を持たない**（`spec` §2 の禁止事項） | 層 0, 分節 |
| 分節 | segmentation | ★ **ISE を引き起こす条件**。音響的な「変化」ではなく、聴覚ストリームが**別々の対象に切り分けられる**こと [P64]。分節を生むのはオンセット・拍・音高のステップ・和声の切り替え。⚠️ **「変化するから破壊的」は誤り**（文献カード本編の訂正済み記述） | ISE, 層 0 |
| ISE | Irrelevant Sound Effect | 無関係な音が系列再生課題を阻害する現象。★ 条件は**変化ではなく分節** [P64] | 分節 |
| 禁止帯 | forbidden modulation band | 変調周波数のうち避ける帯域。★ **4 Hz 付近が最悪**（fluctuation strength のピーク・ISE を 70 例中 63 例予測した予測子）[P69][P65]、**15–70 Hz** は roughness。★ 書き方は「緩慢だから安全」ではなく**「禁止帯から離れているから安全」** | 状態の波, 表現層の平滑化 |
| 状態の波 | state wave band | 状態由来の変動を置く帯域 **0.001–0.02 Hz**（分〜十分オーダー）。禁止帯の 2–3 桁下 | 禁止帯 |
| 表現層の平滑化 | expression smoothing | 1Hz の離散サンプルを**そのまま音に当てない**ための追加の一次遅れ。★ **時定数 ≥60 秒**、`alpha = 1 - exp(-dt/tau)` で **dt を毎サンプル見る**。★ **1Hz 側ではなくレンダレート側で回す**（S0-D7） | 禁止帯, `EXPR_VERSION` |
| 離席ギャップ | away gap (expression) | 表現層でフレーム生成を打ち切る間隔。★ **既定 180 秒**は production の `intervention.rs` `AWAY_IDLE_MS` に接地。跨いで平滑化すると**本人が居ない間のフレームを捏造する**（P010 で 71%）（S0-D11） | アウェイアイドル |
| `EXPR_VERSION` | EXPR_VERSION | 表現層の版。SSOT は `expr_smooth.py` の定数で、`layer0.config.json` にも同じ値を書き **selftest が一致を検査する**。★ **pilot 実施中は動かさない**（`spec` §5 要件 4） | 表現層 |
| オフスイッチ要件 | off-switch requirement | ★★★ **ユーザーが止められる／音量を変えられること**。`spec` §5 要件 1 = **交渉不可**。制御できない連続音は主観的 well-being をむしろ低下させる [P71] | 表現層, 層 0 |
| 案 α / 案 β | plan alpha / plan beta | α = **常時・作業中・リアルタイム**に鳴らす形（D21 で採用）。β = セッション終了後に「今日の音の地形」を出す形（比較条件として残す） | 表現層 |
| 層 0 の自律変異 | layer 0 autonomous drift | 層 0 が**状態と無関係に**行う超低速の変異（S3-D12 で許可）。⚠️ **状態信号になってはならない**——なった時点で層 0 は基層でなくなる | 層 0, 表現層の偽陽性 |
| 表現層の偽陽性 | expression-layer false positive | ★★★ **層 0 の自律変異を「自分の状態が変わった」と読んでしまうこと**。「何も起きていないのに状態が変わったと読ませる」ため、HIR（有害介入率）を最重要安全指標に置く GSE では軽く見ない（S3-D13） | 層 0 の自律変異, 混同テスト |
| 混同テスト | confusion test | 層 0 の自律変異と層 2 の状態応答を同時に鳴らし、★ **「いま変わったのは基層か自分か」を盲検・強制選択で当てさせる**工程。**印象ではなく正答率で案を落とす**（S4-D4） | 表現層の偽陽性, catch トライアル |
| catch トライアル | catch trial | 混同テストで★ **何も動かさないトライアル**。「いつも何か変わったと答える」応答バイアスを検出する。★ **採点には入れない**（S4-D4） | 混同テスト |
| A 案 / B 案 / C 案 | separation plans A/B/C | 表現層の偽陽性を避ける 3 案（S3-D13）。**A = 周波数で分ける**（自律変異を状態帯より 1 桁以上遅く ≤0.0005 Hz）/ **B = 次元で分ける**（層 0 は音色・減衰、状態は密度・帯域・空間）/ **C = 両方**。★ **推測で選ばず耳で決める** | 混同テスト, 状態の波 |
| 表現チャネル | Expression Channel | ★ **状態 → 表現の対応と、境界の契約を持つ抽象**。媒体（PC 画面内 / スマホ常在面 / 将来の専用オブジェクト）から独立している。⚠️★★★ **媒体は交換可能な実装詳細であり、研究の主張の所在に置かない**（★ スマホ常在面は [P101] [P102] に先行がある）。SSOT は **ADR-017** / `docs/architecture/expression-channel.md` | 常在面, 抽象状態イベント |
| 常在面 | ambient surface | ★ ロック画面・ホーム画面・壁紙のように、**開きに行かなくても目に入る表示面**。⚠️★★★ **「常在面に置くこと自体」に効能は無い** —— 事前登録 cross-over（N=60）で確証 6 アウトカム全 null・BF₁₀ 0.066–0.433 [P147] | 表現チャネル, 曝露予算 |
| 抽象状態イベント | abstract state event | ★ **境界を渡る唯一のペイロード**。`level`（`stable` / `friction_rising` / `stuck` / `intervention_active` の 4 値）/ `seq` / `emitted_at`（秒粒度）**のみ**。★ **`level` が変わったときだけ発火**する。⚠️ **1Hz を流さない**（PM-D4「常時流し続けるのは一段大きい」）。⚠️ `p_stuck` などの連続値を載せない | 表現チャネル |
| 曝露予算 | exposure budget | ★ **表現が実際に読まれる時間の実測制約**。ロック画面の準備時間は **中央値 3.4 秒・大半は 4 秒未満**（N=134・1 か月の端末ログ）[P153]。→ ★ **層 A（強制曝露・≤4 秒で読み取れる）と 層 B（任意閲覧・数十秒）に割る**。⚠️ 同じ表現を両方に流用しない | 常在面 |
| 離席候補区間 | away-candidate interval | ★ 沈黙区間を **「歩行」と断定せず**、離席・外部資源利用・熟考などを含む候補として扱う区間。⚠️★★★ **表現層は「あなたは歩いた」と断定してはならない**（[P183] Reflective Design 原則 4） | 身体的回帰, 離席ギャップ |
| 身体的回帰 | embodied return | ★ 離席・歩行によってデスクへ戻ること。**Physical Anchor が促す対象**。⚠️★★★ **系は完了を判定しない**（**ADR-018 D1/D2**）—— ★ 「離席候補区間があり、復帰した」は **観測**であって完了判定ではない（D3）。⚠️ **歩数・距離でも時間でも判定しない**（★ 単位を量から時間へ替えても [P99] の performance-contingent が作る「届かなかったセル」（`d = −0.88`）は消えないため）。⚠️★★★ **身体活動のセンシング自体を GSE 本体から恒久的に外した**（**ADR-017 D10**。★ 例外は形成的トラックのみ）。⚠️ **「歩いたから作業が良くなった」を暗示しない**（[P162]: 成績は全体で null d=.16, p=.116） | 離席候補区間, Physical Anchor |
| 系統 A / 系統 B | pathway A / pathway B | 音に写す入力の 2 経路（`spec` §3）。**A = 推定経由**（`ewma_x`/`ewma_y`/`p_*`。意味は豊かだが外れうる）/ **B = 観測直結**（`f1`/`f3`/`f4`/`f5`/`f6`。★ **HMM の前段なので GATE3 と無関係・MhD が Kill でも生き残る**）。⚠️ `paste` は `FeatSnapshot` に無いため系統 B から落としてある（S4-D6） | 表現層, `FeatSnapshot` |
| 粒子率 | grain rate | 層 2 が 1 秒あたりに発する粒の数。★ **下限 100 grains/s**。⚠️ **文献の数値ではなく [P64] の分節原理からの演繹**なので、★ **下限を割った状態も鳴らして耳で確かめる**（`spec` §9-6） | 層 2 / 粒子, 分節 |

## 技術用語

| 用語 | 英語表記 | 定義 | 関連用語 |
|---|---|---|---|
| HMM | Hidden Markov Model | 3 隠れ状態 × 26 観測ビンの確率モデル。Forward Algorithm で状態確率を逐次更新 | Emission Matrix, Transition Matrix |
| 遷移行列 | Transition Matrix | 3×3 の状態遷移確率行列。現在の認知状態から次の状態への遷移確率を定義 | HMM |
| 発射行列 | Emission Matrix | 3×26 の観測確率行列。各認知状態から各観測ビンが生成される確率を定義 | HMM, 観測ビン |
| 観測ビン | Observation Bin | 潜在軸 (X, Y) を 5×5 グリッド + 1 ペナルティビンに量子化した 26 離散値 (obs=0..25) | HMM |
| EWMA | Exponentially Weighted Moving Average | 指数加重移動平均。潜在軸の平滑化に使用。α が大きいほど最新値への追従が速い | 潜在軸 |
| ヒステリシス EMA | Hysteresis EMA | display_probs に適用する追加の平滑化層。状態確率の急激な変動を抑制 | EWMA |
| 潜在軸 | Latent Axes | 5 特徴量から算出する 2 次元空間。X 軸 = Cognitive Friction、Y 軸 = Engagement | 特徴量, 観測ビン |
| 認知的摩擦 | Cognitive Friction (X 軸) | 修正率・削除後休止・打鍵間隔・休止回数の加重合成。高いほど「つまずき」を示す | 潜在軸 |
| エンゲージメント | Engagement (Y 軸) | バースト長・打鍵速度・休止少なさの加重合成。高いほど「滑らかな出力」を示す | 潜在軸 |
| F1: 打鍵間隔 | Flight Time | 連続するキー押下間の中央値時間 (ms) | 特徴量 |
| F3: 修正率 | Correction Rate | (Backspace + Delete 回数) / 総キー数 | 特徴量 |
| F4: バースト長 | Burst Length | 打鍵間隔 < 200ms の連続入力の平均文字数 | 特徴量 |
| F5: 休止回数 | Pause Count | 2 秒以上の沈黙の回数 (30 秒ウィンドウ内) | 特徴量 |
| F6: 削除後休止率 | Pause-After-Delete Rate | (削除の後に 2 秒以上の沈黙) / 総削除数 | 特徴量 |
| ベースライン (β) | Baseline | 特徴量の正規化基準値。**各 domain head が所有する** (ADR-006 Alternative C)。Writing head は `β_writing` (IME on) と `β_writing_latin` (IME off) を持ち `ime_open` で切り替える | 正規化関数 φ, Writing head |
| ドメイン推論ヘッド | DomainInferenceHead | `analysis::heads` の trait。特徴量から潜在二軸 (X=Friction / Y=Engagement) を算出する。head の選択は `task_kind` (宣言) が決め、`ime_open` (観測) は head 内部の信号として使う | ADR-002, ADR-006 |
| Coding head v0 | Coding head v0 | エージェントコーディングドメインの推論ヘッド (`analysis::heads::coding`)。現 `β_coding` を**初期シードとして所有**し、`ime_open` に関わらず適用する。⚠️ 主信号である coding イベント (accept/reject/test/revert) は Epic 4 で、v0 は打鍵 β のみ | DomainInferenceHead, ADR-006 #3 |
| 課題ドメイン | TaskDomain | `task_kind` (宣言) から決まる head のルーティング信号 (`Writing` / `WritingFallback` / `Coding`)。変換は `logger.rs` の `From<TaskKind>` に 1 本だけ置く | TaskKind, DomainInferenceHead |
| head 識別子 | head_id | どの head がそのセッションを採点したかの識別子 (`writing` / `writing_fallback` / `coding_v0`)。`session_meta` NDJSON に記録。⚠️ `FeatSnapshot` には入れない (ゴールデン snapshot が壊れる) | TaskDomain, schema |
| Writing head | Writing head | 論述・文章作成ドメインの推論ヘッド (`analysis::heads::writing`)。Phase1 (task_kind=argumentative 固定) で走っていた挙動そのもの | DomainInferenceHead, β_writing_latin |
| `β_writing_latin` | writing latin baseline | Writing head 内の **IME off (ラテン直接入力: 英字引用・数式・URL) 用サブ baseline**。値は旧 `β_coding` をそのまま改名 (F1=150 / F3=0.06 / F4=5.0 / F5=2.0 / F6=0.08)。⚠️ **Coding の baseline ではない** — 「IME off の日本語論述」を Writing head 内に再スコープしたもの (ADR-006 下位決定 #2) | ベースライン (β), Writing head |
| 正規化関数 φ | Normalization Function φ | φ(x, β) = clamp((x − β) / (κ · β), 0, 1)。κ=2.0 | ベースライン |
| バックスペースペナルティ | Backspace Penalty | 連続 14 回以上のバックスペースで obs=25（ペナルティビン）を強制発火。IME 変換中は抑制 | HMM, 観測ビン |
| 摩擦フロア | Friction Floor | サイレンス時に合成される最小摩擦値。Stuck 状態の侵食を防止 | サイレンス検出 |
| サイレンス検出 | Silence Detection | 2 秒以上のキー入力なし状態。段階的 α 調整 (0.15 → 0.18 → 0.25) で遷移 | EWMA |
| 1Hz ゲート | 1Hz Gate | Analysis スレッドが 1 秒ごとに HMM 推論を実行する時間制御機構 | Analysis Thread |
| 分析ループ状態 | AnalysisState | `step()` をまたいで保持される分析ループのローカル状態構造 (`analysis::loop_step::AnalysisState`)。production では分析スレッドが 1 個所有、gse-replay も同型を使う | 1Hz ゲート, FeatSnapshot |
| 打鍵パス | TypingPath | 1Hz ゲートの 3 分岐の 1 つ。バッファ実データあり (f1>0) かつ `silence<2s`。`update()` を呼び、`pre_silence_features` をキャプチャ | 沈黙 3 状態機構, 摩擦フロア |
| 遷移パス | TransitionPath | 1Hz ゲートの 3 分岐の 1 つ。実データあり かつ `silence≥2s`。`update_silence()`、摩擦フロアは線形 (onset 8s)。「打鍵直後の沈黙」を扱う | 沈黙 3 状態機構, 摩擦フロア |
| 沈黙パス | SilencePath | 1Hz ゲートの 3 分岐の 1 つ。バッファ空 (f1=0) かつ `silence≥2s`。`update_silence()`、摩擦フロアは非線形増幅 (onset 2s)。「純粋な無入力」を扱う | 沈黙 3 状態機構, 摩擦フロア |
| IME_OPEN | — | 日本語 IME の ON/OFF 状態を示すアトミックフラグ。ON = 日本語入力モード | IME, ベースライン |
| IME_ACTIVE | — | IME 変換候補ウィンドウの表示状態を示すアトミックフラグ | IME |
| CGEventTap | — | macOS のキーボードイベント傍受機構。ListenOnly (Input Monitoring) と Default (Accessibility) の 2 モード | WH_KEYBOARD_LL (Windows 対応物) |
| Input Monitoring | — | macOS TCC 権限カテゴリ。kCGEventTapOptionListenOnly でキーイベントを受動的に傍受するために必要 | TCC, CGEventTap |
| Accessibility 権限 | Accessibility Permission | macOS TCC 権限カテゴリ。kCGEventTapOptionDefault でタップを作成するために必要。Input Monitoring のフォールバック先 | TCC, CGEventTap |
| CGKeyCode | — | macOS 固有の仮想キーコード (HIToolbox/Events.h)。hook_macos.rs 内で Windows VK コードにマッピング | VK |
| TIS | Text Input Source | macOS の入力ソース API。TISCopyCurrentKeyboardInputSource() で日本語 IME の ON/OFF を検出。GCD メインキュー経由で呼び出し必須 | IME_OPEN |
| dispatch_sync_f | — | GCD のメインキュー同期ディスパッチ関数。TIS クエリと AXIsProcessTrustedWithOptions に使用。フックスレッドから呼ぶ（メインスレッドからはデッドロック） | GCD |
| IME_COMPOSING | — | macOS 固有のアトミックフラグ。ローマ字→かな変換中（インライン下線テキスト）を示す。CGEventTap 内の状態機械で更新 | IME_ACTIVE |
| JIS_KEYBOARD_SEEN | — | macOS 固有のアトミックフラグ。JIS 物理 IME キーが検出された時点で true になり、TIS ポーリングを無効化する | TIS |
| USING_ACCESSIBILITY_FALLBACK | — | macOS 固有のアトミックフラグ。Input Monitoring から Accessibility へフォールバックしたことを示す | CGEventTap, TCC |
| FeatSnapshot | — | 1Hz ゲートで生成される特徴量 + HMM 状態確率のスナップショット (`analysis::loop_step::FeatSnapshot`)。NDJSON `feat` レコード + gse-replay 回帰比較の基本単位 | 1Hz ゲート, snapshot |
| LatestFeatState | — | 直近の FeatSnapshot を Tauri state として保持する構造。`get_intervention_decision` が F3/F4/F6 を読む | InterventionDecision |
| InterventionPolicyState | — | cooldown / daily cap / recent dismiss / last decision を保持する（⚠️ **2026-09-01 訂正 —— 旧文の「Wall 累積時間」は失効**。ADR-015 D1 で `wall_accum_ms` ごと削除） Rust 側ポリシー状態 | InterventionDecision |
| 混同行列 | Confusion Matrix | `[正解×推定]` の 3×3 行列 (`analysis::metrics::ConfusionMatrix`)。正解ラベルクラス × HMM argmax クラスの件数を格納 | UserLabel, F1 |
| Macro F1 | — | 各クラスの F1 を単純平均した値。固定分母 3 (scikit-learn 互換)。クラス不均衡に強くない代わりに minority class を重視 | 混同行列 |
| Micro F1 | — | 総 TP / 総 labels。多クラスでは accuracy と一致。GSE では分母は matched labels のみ (警告行きは除外) | 混同行列 |
| detection_lead_ms | — | UserLabel 時刻 - 最近傍同クラス argmax feat の時刻。正 = HMM 先行、負 = 遅延 (±60 秒窓内の最近傍を採用) | UserLabel, FeatSnapshot |
| recovered_at | — | Stuck ラベル後に p_flow > 0.5 に達する最初の FeatSnapshot 時刻。ログ記録時は null、`gse-replay --metrics` 実行時にオフラインで純粋関数算出 | compute_recovered_at |
| 範囲ラベル | RangeLabel | 時間区間 (`{start_ms, end_ms, label}`) 形式の GT ラベル (`analysis::metrics::RangeLabel`)。点ラベルを forward-fill で区間化したもの。1 ラベルから N 個の feat-label ペアを生成し検出力を高める | point label, forward-fill |
| 点ラベル / forward-fill | point label / forward-fill | point label = 単一時刻の GT ラベル。forward-fill = 次のラベルまで前のラベルを引き延ばし区間 (RangeLabel) 化する手法 (`intervention_eval`) | RangeLabel, PROTECT/STALL |
| PROTECT / STALL | — | 介入評価の GT 二値化。PROTECT = 旧 Flow/Incubation（守るべき状態）、STALL = 旧 Stuck（介入候補）。`gse-replay --intervention` で point label を forward-fill 区間化して使う | HIR, intervention_eval |
| ACT / HOLD | — | 介入評価の decision 二値化。ACT = {nudge}（介入する。⚠️ **2026-09-01 訂正: 旧文の `wall` を削除** — 実測 `intervention_eval.rs:54` 逐語「ACT={nudge}」）、HOLD = {none, defer}（控える） | HIR, InterventionDecision |
| HIR | Harmful Intervention Rate | 有害介入率 = ACT∩PROTECT / labeled-ACT。PROTECT 区間に介入してしまった割合。v2 介入評価の最重要・安全性指標 (`analysis::intervention_eval`) | PROTECT/STALL, intervention_eval |
| DC | Defer Correctness | defer 正答率 = W 秒以内に p_flow>0.5 へ回復した defer 区間 / 全 defer 区間。見送り判断が自己回復で支持された割合 | recovered_at, ACT/HOLD |
| Burden | — | 介入評価の過介入代理 = ACT 回数 / セッション分 | HIR |
| intervention_eval | — | v2 介入ポリシーのオフライン反実仮想評価モジュール (`analysis::intervention_eval`)。`gse-replay --intervention` から呼ばれ HIR/Precision/DC/Burden を算出。screening 用途 | HIR, DC, intervention_decision |
| hmm_version | — | `analysis::engine::HMM_VERSION` の SemVer 値 (現行 `0.4.0`)。meta NDJSON エントリに埋まる、gse-replay が版不一致を WARN | HMM, schema |
| schema_dto | — | `logger::LogEntry` の `schemars::JsonSchema` 派生専用ミラー型 (`schema_dto::LogEntryDto`)。production path に影響させず JSON Schema を機械生成するための DTO | emit_schema, current.json |
| intervention_decision | — | MVP Opportunity の NDJSON ログ種別。action, need_score, opportunity_score, p_stuck, idle_ms, wall_accum_ms, reason, suppressed_by を含む | InterventionDecision, schema |
| metrics.json | — | `gse-replay --metrics --json` の出力 (1 KB/session)。gse-dataset repo の `metrics/P*/<os>/` に配置する共有アーティファクト | aggregate_metrics, UC-GT3 |
| gse-dataset | — | セッションメトリクスの集約データ repo (`mikotomiura/gse-dataset`, private)。生 NDJSON は絶対に置かず、`metrics/` と機械生成 schema のみ tracked | metrics.json, schema sync |
| 被験者 ID | Participant ID | データ repo での匿名化識別子。`P000` (開発者自身) / `P001-P005` (Phase 2+ 外部被験者) | IRB, consent |
| Phase 2a Go/No-Go | — | ⚠️ **2026-09-01 訂正: `aggregate_metrics.py` は存在しない**（実体は `gse-cohort` / `scripts/run-calibration-cohort.sh`）が出力する判定。Stuck precision 平均 ≥ 0.6 かつ n ≥ 5 で GO、未満は INCONCLUSIVE | metrics.json, baseline_metrics.md |
| 収束器 | reconciler | 「あるべき状態 (desired state)」を宣言し、現状をそこへ寄せる周回処理。冪等が構造で保証される。`src-tauri/src/reconcile.rs` (`.age` の再送・取りこぼし回収) と配布自動化 Stage 2 が同じ形。**⚠️ 表現できない状態は管理してはならない**（「止めたい」を宣言できないなら共有を収束器の管轄に入れない） | desired state, D-7 |
| desired state | — | 収束器の入力となる宣言。配布自動化では P-ID ごとの「配る / 止める」の 2 値。⚠️「配る」しか表現できない収束器は同意撤回を潰す | 収束器 |
| spike | — | **実装前に、未検証の前提を実測で潰す使い捨ての検証**。結果は「可 / 否 + 実測値 + 実測日」で書き、⚠️「たぶん」「はず」を残さない。外れたときの行き先を先に決めてから実行する | verify-before-claiming |
| 捨てフォルダ | throwaway folder | spike 専用に作り、終わったら消す Drive フォルダ。⚠️ **本番の親フォルダで spike しない**ための隔離先。中身は実被験者の割付を含めない | spike, PILOT-spike |
| PILOT-spike | — | `assign.py --pilot --pilot-label spike` が生む spike 専用 subject。★ 本物の生成器を通した実形式の課題ページを、実被験者の割付を晒さずに得るための手段 | 捨てフォルダ, PILOT-mac/win |
| 陽性対照 | positive control | 「検査が壊れていれば赤になるはず」の入力を**わざと**通し、実際に赤になることを確かめる検査。⚠️ これが無いと「常に緑を返すガード」を緑と読み違える | 陰性対照, silent-failure |
| 陰性対照 | negative control | 「通ってはいけないもの」を通し、止まることを確かめる検査。例: 課題ページ以外 (`g1-submit.json` / `pubkey.txt`) を置いたら赤 | 陽性対照, 許可リスト |
| 許可リスト | — | 「これだけを通す」形の判定。⚠️ 拒否リスト（これを止める）と対で、**漏れが fail-open にならない側**を選ぶ。配布では `^block\d{2}\.html$` に一致する物だけを上げる | 陰性対照, fail-closed |
| drive.file スコープ | — | Google Drive API の**非機微**スコープ。「このアプリが作った・開いたファイルだけ」に限られる。⚠️ 資格情報が漏れても研究者の Drive 全体は読まれない。`drive` フルスコープ（機微）と混同しない | OAuth, spike-1 |
| allowFileDiscovery | — | Drive の共有設定。`false` = リンクを知っている全員、`true` = **検索可能＝一般公開**。⚠️ API の暗黙既定に任せず**明示指定して読み返す**（fail-open 側の性質を既定に依存させない） | permissions.create, D-7 |

## 略語

| 略語 | 正式名称 | 意味 |
|---|---|---|
| GSE | Generative Struggle Engine | 本プロダクトの名称 |
| MhD | Mind-house Detector（認知状態検出モデルの総称） | キーストローク行動から作業状態を推定する**検出モデルの総称**。内部で X(Cognitive Friction)/Y(Productive Engagement) 二軸と `p_stuck` を出す。**Stage 1 = 現行のルールベース HMM**（現在地・`engine.rs`）、**Stage 2 = ロジスティック回帰**（昇格は約 50 セッション＋3% 改善の Go/No-Go、未達なら Stage 1 を正＝オッカムの剃刀）。MhD の出力 `p_stuck`（L1 Stuck 計算）を Need 層（L2・`intervention.rs`）が閾値で消費する点に注意（別層・別計算） |
| HMM | Hidden Markov Model | 隠れマルコフモデル |
| EWMA | Exponentially Weighted Moving Average | 指数加重移動平均 |
| IME | Input Method Editor | 日本語入力メソッドエディタ |
| IPC | Inter-Process Communication | プロセス間通信（Tauri のフロントエンド↔バックエンド通信） |
| NDJSON | Newline Delimited JSON | 改行区切り JSON（セッションログ形式） |
| VK | Virtual Key | 仮想キーコード（Windows API 由来。macOS では CGKeyCode からマッピング） |
| TCC | Transparency, Consent, and Control | macOS のプライバシー権限管理フレームワーク。Input Monitoring, Accessibility 等のカテゴリを管理 |
| GCD | Grand Central Dispatch | macOS のスレッドディスパッチ機構。dispatch_sync_f でメインキュー実行に使用 |
| CDHash | Code Directory Hash | macOS コード署名のハッシュ値。TCC データベースでアプリを識別。ad-hoc 署名では不安定 |
| CSP | Content Security Policy | コンテンツセキュリティポリシー |
| UIPI | User Interface Privilege Isolation | UI 特権分離（Windows セキュリティ機構） |
| TSF | Text Services Framework | テキストサービスフレームワーク（Windows IME 基盤） |

## 禁止用語

| 禁止 | 代替 | 理由 |
|---|---|---|
| winapi | windows crate | winapi crate はメンテナンス停止。公式の windows crate (v0.58+) を使用 |
| allowlist（★ Tauri の権限の文脈でのみ禁止） | capabilities | Tauri 2.0 では v1 の allowlist を廃止し capabilities に移行。⚠️ **Tauri 以外の文脈**（配布で上げてよいファイルを絞る等）で「これだけを通す」判定を指すときは日本語の「許可リスト」を使う（技術用語表を参照）。★ 2026-08-16 に適用範囲を明記 |
| 集中度 / 集中状態 | Flow | 「集中」は曖昧。Csikszentmihalyi の Flow 概念を正確に使用する |
| 行き詰まり度 | p_stuck / Stuck 確率 | 「度」は曖昧。確率値で語る |
| ~~タイマー → Zen Timer~~ | — | ⚠️★★★ **2026-08-23 に失効**（ADR-015 D1 で Zen Timer ごと削除）。★ 現行に Zen Timer は無い |
| ~~ロック / ブロック → Wall (Lv2)~~ | — | ⚠️★★★ **2026-08-23 に失効**（ADR-015 D1）。★ **現行に画面を塞ぐ介入は存在しない** |
| 歩数達成 / 距離達成 / 時間達成 / 完了 / クリア（Physical Anchor の判定語） | **完了条件を課さない**（身体的回帰への**方向づけ**に留める） | ⚠️★★★ **ADR-018 D1**（★ 既決 D11 条件 2 を取り下げた）。★ 単位を量から時間へ替えても**達成判定の構造は残る** —— [P99] の performance-contingent は「届かなかった群」で `d = −0.88`、かつ逐語 *"anticipated evaluation … d = −0.40"* は**肯定的フィードバックでも評価の予期が毀損する**と述べる。★ 完了の宣告は [P183] 原則 4（*"avoid making the technology, rather than the user, the final authority on what the user is doing"*）に直撃し、★ [P163] の反応性機序 3（*"resolving discrepancies between actual and desired behaviour"*）を系の側が作る |
| 「あなたは歩いた」等の断定（表現層・UI） | 「摩擦の信号が下がった」等の非断定 | ⚠️★★★ 系が持てるビットは **「離席候補区間があり、復帰した」**までである（ADR-017 D3）。[P183] *"avoid making the technology, rather than the user, the final authority on what the user is doing"* |
| 不便益 HCI **である** | 不便益を**設計思想として引く** HCI | ⚠️★★★ 認定条件 1（益は不便だからこそ＝労力）が現行実装で満たされない [P170]。不便を担う Physical Anchor は未実装 |
| 不便益を**測定可能にした** | 不便益を思想として掲げた介入を**行動指標で前向きに検証した** | ⚠️★★★ **不便益に合意された測定尺度は存在しない**。GSE が測るのは行動指標であって不便益ではない |
| 認知リソースの**消耗** / **回復** / リソースの**補充**（★ Physical Anchor・休憩・自然曝露の文脈でのみ禁止） | **関与の低下** / **関与の再開**（→ 用語表） | ⚠️★★★ **限定資源モデル（ego depletion）の語彙であり、その枠組みは死亡が確認済み**（[P199] RRR k=23・N=2,141 で **d=0.04** / [P200] 事前登録 k=36・N=3,531 で **d=0.06** / [P201] PEESE **b=0.003**）。★ **[P200] は操作が成功していたことも示している**（努力感は大きく動いていた。⚠️ **効果量は「二プロトコル平均の切片 d=1.76」としてのみ引ける** —— プロトコル別では d=3.09 / d=0.46 と割れるため、裸の数値は誤導的。→ [P200] 行）＝ **「消耗 → 成績低下」の連結が無い**。⚠️ **注意回復理論（ART）は限定資源モデルそのもの**であり（[P166] 逐語 *"restoration of a limited cognitive resource"* / [P192] が ego depletion へ明示接続）、**事前登録された ART の検定は 5 本すべて null**（[P193]–[P197]）。→ ★ **この語彙で書くと、既に否定された枠組みを再輸入したことになる**。⚠️ **例外**: 既存の指標名 `自力回復率 / productive_manual_recovery_rate`・`打鍵再開` は**「停滞エピソードからの自力での前進」の意味**であって資源の補充ではない（★ 改名しない） |
| kCGEventTapOptionListenOnly | Input Monitoring tap / ListenOnly tap | API 定数名をそのまま使わず、権限名で説明する |
| kCGEventTapOptionDefault | Accessibility tap / Default tap | 同上 |

## 用語の追加・変更ルール

1. 新しい概念を導入する際は、まずここに追加してから実装する
2. 既存用語の意味を変える場合は、変更履歴を残す
3. ドメイン用語は日本語・英語の両方を定義する
4. 学術的な裏付けがある場合は参考文献を括弧内に記載する
