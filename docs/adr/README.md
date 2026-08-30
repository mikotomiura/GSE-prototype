# Architecture Decision Records (ADR)

GSE の重要なアーキテクチャ判断を記録する。各 ADR は **Context / Decision / Alternatives / Consequences /
Migration** を持つ。SSOT のアーキテクチャ概要は `docs/architecture/gse-v2-overview.md`、研究の主張・
エビデンス温度は `docs/research-positioning.md`、現行実態は `.steering/20260724-epic0-repo-reality-check/`。

## ステータス凡例
- **Accepted**: 決定済み。実装が従う。
- **Proposed**: 方向は合意。詳細/確定は実装時 or 後続 ADR。
- **Deferred**: 判断を保留（エビデンス待ち／Phase1 完了待ち／研究者判断待ち）。
- **Superseded by ADR-xxx**: 後続 ADR に置換。

> **前提**: すべて Phase1 完了 + 研究者承認が前提。Epic 1（本 ADR 群）は**コード変更ゼロ**。凍結対象
> （`schema_dto.rs`/`schema/current.json`・`engine.rs` HMM_VERSION・`intervention.rs` 閾値・`probe_scheduler.rs`・
> `App.tsx` argumentative lock・`preregistration-v0.3.md`）は Phase1 完了まで変更禁止。
>
> ★★★ **2026-08-18 更新: Phase1 は収集打ち切りで終了した**（verdict = `inconclusive` /
> GATE3 = `DataInsufficient`）。**凍結は解除**され、ADR-002 / ADR-006 の実装（`engine.rs` の
> `HMM_VERSION` は `0.4.0` へ bump）を実施した。
> ⚠️ ただし **`App.tsx` の argumentative lock は解除していない** —— 外すには Phase2 の
> 募集・教示・条件割付の運用設計が要るため、別タスクとして残っている。
> ⚠️ また **`intervention.rs` の閾値**も本タスクでは触っていない。

## 一覧

| ADR | 主題 | ステータス | 対応 Epic |
|---|---|---|---|
| [ADR-001](ADR-001-hmm-as-writing-baseline.md) | HMM を Writing baseline へ降格・三状態表示の降格 | Accepted（実装は後続） | Epic 1→2 |
| [ADR-002](ADR-002-domain-local-inference.md) | domain-local inference / DomainAdapter 境界 | **Accepted（2026-08-18・trait 範囲は `DomainInferenceHead` のみに限定）** | Epic 2 |
| [ADR-003](ADR-003-accountability-outside-core.md) | Accountability を core 外の opt-in extension に分離 | Proposed（採否は Deferred・第4ラウンド待ち） | Epic 3.5+ |
| [ADR-004](ADR-004-decision-engine-boundary.md) | Decision Engine 境界（pure function 化）+ Consent 軸 | Accepted（Consent 実装は Epic 3） | Epic 3 |
| [ADR-005](ADR-005-event-envelope-versioning.md) | Event Envelope schema versioning | Proposed | Epic 2/5 |
| [**ADR-006**](ADR-006-task-kind-beta-wiring.md) | **task_kind → β baseline 配線 or IME 代理を正とするか** | **Accepted（枠組み C 2026-07-24）・★ 実装済み 2026-08-18（`HMM_VERSION` 0.4.0）** | Epic 2 分岐点 |
| [ADR-007](ADR-007-receptivity-decomposed-vs-unified.md) | receptivity 統合スコア化 or 分解維持 | Accepted（分解維持を推奨） | Epic 3 |
| [ADR-008](ADR-008-online-learning-boundary.md) | オンライン学習の境界（PersonalizationStore / OnlineUpdater / ContextBuilder・PreReg-5 との両立基準） | Proposed | Epic 2+ / Phase1 後 |
| [ADR-009](ADR-009-recovery-risk-axis-and-latent-state.md) | X 軸を `self_directed_recovery_risk` へ再定義し、潜在状態の数を決めない | Proposed | Epic 2+ / Phase1 後 |
| [ADR-010](ADR-010-task-scope-gating.md) | 「どの head も当てはまらない」— head 相対 `scope_fit` / 宣言と観測の役割分離（**ADR-006 の拡張であって改訂ではない**） | Proposed | Epic 2+ / Phase1 後 |
| [**ADR-011**](ADR-011-low-typing-window-track.md) | **低打鍵窓の扱い**— 沈黙を「在席×非打鍵 / 入力皆無」に分解する**探索トラック**を `§8` 段別表の外に新設し、`paste`/`keys` を推論へ流す「**読む実装**」は G1 判定まで出さない（★ **コード変更ゼロ**） | **Accepted（2026-08-19）** | Epic 2+ / G1 前後 |
| [**ADR-012**](ADR-012-nonkeystroke-observation-formative-track.md) | **非打鍵タスクの観測空間を「実測で」決める** — ★ **ADR-008 D1 が空白にした「どう superset を決めるか」**を埋める形成的トラック。判定量は**沈黙被覆率**、閾値は**打鍵タスクの実測値から導く**（人が選ばない）。`§8` **T3 行の降格先列のみ**を改訂（★ **T1/T2 と A-Q3 は不変**・**コード変更ゼロ**） | **Accepted（2026-08-19）** | Epic 6 / G1 非依存 |
| [**ADR-013**](ADR-013-collection-self-description.md) | **収集仕様の自己記述性** — 「**信号が無い**」と「**計器が無い**」をログだけで機械判定できるようにする（`meta.capabilities` / `starve_window` / `dropped_delta`・すべて **additive**）。★ **実装済み（2026-08-19・G1 リブート前の停止期間）**。⚠️ 残ゲートは**同意文書の突合**（収集開始前） | **Accepted（2026-08-19）** | 実装済み |
| [ADR-014](ADR-014-continuous-natural-work-collection.md) | **自然作業の常時収集を「第 3 の収集レジーム (R3)」として定義**し、⚠️ **確証には使わない** — R1 統制ブロック（G1・確証）/ R2 宣言ブロック（ADR-012 Stage 1・形成的）/ **R3 自然作業の常時収集（形成的のみ）** に分ける。★ **非打鍵チャネルを集める**（⚠️ 打鍵のみでは `left_observation` が **実装ゼロ・観測不能**）。⚠️★★★ **ただし「全部」ではない**: **R3 自身の段 1 を実データ前に凍結**・**役割カテゴリは入れない**・★ **記録のみで推論に 1 バイトも流さない**（Tier 0 配線の先例）。★ 判定量は **G2 の上下界の幅**。⚠️ **ADR-013 D6 を R3 の範囲で条件付き解除**（★ ADR-012 D7 制約 4 は不変）。⚠️ **在席の連続タイムラインを作ることを隠さず同意と保管で受ける**（本 ADR は**コード変更ゼロ**） | ★★★ **Accepted**（2026-08-23・研究者判断 1〜6 を確定: 対象者=**形成的サブコホート 3〜5 名** / 倫理審査=**不要（理由を記録）** / 開始=**G1 の *収集完了* 直後（判定は待たない）** / lock=**R3 の範囲でのみ解除** / consent 粒度=**実装を文言に合わせる**） | Epic 2+ / **G1 の収集完了後**（⚠️ 判断 6 の実装は別タスク・`Punctuation` 追加の採否が先） |
| [ADR-015](ADR-015-wall-removal.md) | **Lv2 Wall と Monk Mode を全削除する** — ★ 全画面ブロック UI は **D-5 (2026-06-12・ユーザー承認) が「残さない」と決めていたのに未履行**だった。⚠️ Monk Mode は `intervention-design` ルール 5 逐語「**Wall を無効化するだけ**」で、Wall 削除により**定義上デッドになる**ため一緒に削除。★ **HIR は残す**(対象が `{nudge}` になっただけ)。⚠️★★★ **PM-D11 を覆す** —— Physical Anchor が再利用予定だった **Wall Server の 1 ビット経路が消え、境界クラスの再設計が要る**。⚠️ 凍結文書 (G1 事前登録) と履歴記録は**書き換えない**（ずれは記録として残す） | ★★★ **Accepted** (2026-08-23) | 完了 (⚠️ 運用文書と Physical Anchor 再設計は別タスク) |

| [ADR-016](ADR-016-nonkeystroke-interval-handling-in-o1.md) | **O1 における「在席×非打鍵」区間の受け方** — ⚠️★★★ **非打鍵区間は既定で `still_stalled` に算入され、`recovery` のハザードを下方へずらす**（★ `progress_proxy` が打鍵ベースであることの帰結）。★ 受け方は **`left_observation` と同じ両極端の仮定で挟む上下界**。⚠️ **第 5 のカテゴリを作らない / `evidence_quality` を O1 で動かさない / 判定量を新設しない**（★ 既存の幅を打鍵密度で層別して読むだけ）。⚠️ **段 1・4 択・役割カテゴリの順序を 1 文字も変えない**（★ **コード変更ゼロ**）。★ **D7**: 3D / 動画編集への *適応* はしない（**head を足さず宣言経路だけ確保**）。★ **D8**: 計測器の**ゲートを 2 本に割り**、操作語彙を**記録だけに流す**（`HMM_VERSION` 不変・schema 変更ゼロ）。★ **D9**: ADR-012 Stage 1 と**同一区間を 2 計器で観測**（⚠️ D7 制約 4 は不変） | ★★★ **Accepted**（★ **判断 1/2/3/5 = 2026-08-23**: 上下界 = `still_stalled`↔`recovery` / **コホートを重ねる** / **反転率 ≤ 0.10（恣意的と明示）** / **ゲート分割**。★ **判断 4 = 2026-08-25**: **宣言に含める。語は「デザイン・映像・制作作業」**。★ **判断 4b = 2026-08-25**: 運用形態 **(B) 常時収集** / 頻度 **起動時 1 回 ＋ 任意変更（変更 = ローテート + reset）** / 粒度 **既存 4 値** / 未宣言 **`session_meta` 行の不在で表す**） | Epic 2+ / **G1 の収集完了後** |
| [**ADR-017**](ADR-017-expression-channel-boundary.md) | **表現チャネルと媒体を分離し、PC ↔ スマホの境界を「一方向の抽象状態イベント」にする** — ★ **ADR-015 D4 が開けた「Physical Anchor の運搬路の再設計」を、第 1 版については「inbound の経路を作らない」で閉じる**。⚠️★★★ `.idea` メモは **§5（常時ストリーム）と §7（イベント駆動）で内部矛盾**しており、**§7 を正**とした（PM-D4「常時流し続けるのは一段大きい」＋ [P153] ロック画面の曝露は**中央値 3.4 秒**＝ **常時流しても受け手がいない**）。★ **D3**: 完了条件が「時間・往復」（PM-D11 条件 2）で、PC が既に**離席候補区間＋復帰**を content-free に観測しているため、**第 1 版でセンサを足す理由が無い**（⚠️ PM-D11 は覆さない）。⚠️ 帰結として持てるビットは「歩いた」ではなく**「離席候補区間があり、復帰した」** → ★ **表現層は断定しない**（[P183] Reflective Design 原則 4）。★ **D5**: **音声の自動開始は Phase1 の範囲外**（★ 「有害だから」ではなく **装着を閉じる手段も害を測る手段も無いから** —— [P137] 特異度 0.00/0.08 ／ [P146] ／ [P135] は −21.0 分が出たのに **95% が「制御できている」と回答**）。★ **D8**: 復帰後の差分を結合するとき **入力 1 =「時計の事実」／入力 2 = `p_stuck`** に割る（⚠️ 同じ打鍵から 2 入力を作ると ADR-009 D2 の自己言及が戻る）。★ **D7**: 既決 D8 を再確認（**不便益の認定条件 1 を満たすのは Physical Anchor だけ** [P170]）。★ **コード変更ゼロ** | ★★★ **Accepted**（2026-08-30） | Epic 3+ / 表現層トラック |

> ADR-008 / ADR-009 は一体で読む。背景・段階計画・評価指標・反証ゲートは
> `docs/architecture/personalization-and-online-learning.md`（統合設計文書）を参照。
> ADR-010 は ADR-006 と一体で読む。較正プロトコル・検出器の構造・定数の推定手続きは
> `docs/architecture/task-adaptation-and-scope-gating.md`（設計本体）を参照。
>
> ⚠️★★★ **ADR-012 と ADR-013 は一体で読む。** ADR-012（何を載せるか）は
> ADR-013（それを載せる仕様）が無いまま次コホートを収集すると、
> **「計器がコホートを跨げない」失敗を 3 件目として再生産する**（既に 2 件発生している）。
> ★ 事前登録と実験の骨格は `experiments/20260819-nonkeystroke-silence-coverage/` を参照。
>
> ★ **ADR-014 は ADR-012 / ADR-013 / ADR-009 D2・D7 と一体で読む。** ⚠️ 「常時収集」は
> **ADR-012 D7 制約 4（別計測器を常駐させない）** と **ADR-013 D6（在席の連続タイムラインを作らない）** が
> 別々の理由で塞いでいた領域である。
> ★ ADR-014 は **D7 制約 4 を 1 文字も変えず**（R3 は別計測器ではない）、
> **ADR-013 D6 の非打鍵行だけを R3 の範囲で条件付きに解除**する（★ 段 1 の事前凍結 / 記録のみ / 禁止表の遵守）。
> ⚠️★★★ **「記録する」と「superset を確定する」を混同しないこと** ——
> 確定するのは **ADR-012 D2 の段 3（推論への配線）**であり、★ **人が G1 判定後に決める**（**ADR-011 D4 は不変**）。
> ★ 突き合わせの全体像と実測の根拠は `.steering/20260821-workspace-behavior-triage/triage.md` / `decisions.md` D-15。
>
> ★ **ADR-016 は ADR-009 D2 と ADR-014 D4c と一体で読む。** ⚠️ ADR-016 は
> **新しいチャネルも新しいカテゴリも新しい判定量も作らない** —— ★ **既に段 1 で取れるものの *読み方*** だけを決める。
> ★ 観測設計側の記述は `docs/architecture/workspace-behavior-observation.md §9.4`〜`§9.6`。
