# tasklist.md

## フェーズ 0: 本タスク(レビュー＋設計) — 完了
- [x] v0.2(.docx)精読・関連 docs/コード/Skill 把握
- [x] codex 独立レビュー併用(相互検証)
- [x] 厳密レビュー(Part A, High×6 + Med/Low)
- [x] 具体設計(Part B, スキーマ/解析/事前登録/kill 基準)
- [x] コーナー段階介入 UI 設計(Part C)
- [x] steering 記録(requirement/design/decisions/tasklist)

## フェーズ 1: 立て付け確定(ユーザー判断 → docs 反映)
- [x] **Lv2 = ソフトのみで確定**(2026-06-12 承認)。walk-hard は実装しない(D-5)
- [x] スモークの主張を「探索的＋測定法較正」に降格する方針の合意
- [x] codex 第2次独立評価で Part B を上書き(D-8〜D-13)
- [x] **改善版 v0.3 設計書を起草** → `.idea/GSE_事後ラベリングシステム設計書_v0.3.md`
- [x] **v0.3 をユーザーがレビュー → 納得**(2026-06-16「v0.3 でとりあえず OK」= 実装契約として確定)

## フェーズ 1.5: 実装前の凍結(現タスク内・Step 0)
- [x] PreReg-1..8(v0.3 §15)を `docs/preregistration-v0.3.md` に凍結
- [x] glossary 改訂(criterion label / random probe / time isolation / context_beacon / C-index / 2段ゲート / 前向き holdout 等を追加、GT 行に D-13 注記)
- [ ] `intervention-design` Skill のクリックブロック前提(ルール 1/7)を更新 ※介入 UI 着手時に実施(プラミング先のため後送り)
- [ ] glossary の Wall(Lv2) 定義を「ソフトコーナー companion」へ改訂 ※同上(D-5・介入 UI タスクで)

---

# 初回較正スモーク = 最小核・計測プラミング先(D-14 / 2026-06-16 確定)

> スコープ: IN=核データ収集+オフライン解析 / OUT=比較条件(beacon・波形cue)・統制課題・介入UI・Recall点推定
> 実装順: A(全ブロッカー)→ (B ∥ C)→ D → E

## Task A — schema 拡張(別タスク /start-task → /add-feature)【全ブロッカー】✅ 完了(2026-06-16)
> 新セッション用プロンプト: `next-session-prompt-taskA.md`(このフォルダ内)
> 実装記録: `.steering/20260616-probe-schema/`
- [x] `schema_dto.rs` + `LogEntry` に `session_meta` / `probe_assignment` / `realtime_label` / `vignette_response` を同期追加(§14)
- [x] producer 不変条件を強制(skip⇒q1/q2=null、source=self_marker⇒probe_id=null 等。ProbeRef で型保証 + clamp)
- [x] emit_schema 再生成 → `schema/current.json` 更新 → drift 緑(byte-equal)。lib test 97 緑・新規 clippy 警告ゼロ

## Task B — backend プローブ scheduler(A 後 / C と並行)
- [ ] rolling thinning(λ≈2回/30分・gap≥8分・cap≤2回/30分・離席は適格から除外)で一様ランダム時刻生成
- [ ] `probe_assignment` ログ(scheduled_ts / session_elapsed_ms)+ フロントへ emit
- [ ] 自己マーカー hotkey(source=self_marker・副データ)

## Task C — frontend 収集(A 後 / B と並行)
- [ ] `session_meta` 宣言 UI(task_kind 一打・セッション開始)
- [ ] プローブカード(Q1摩擦/Q2前進スライダー・skip理由・latency 計測)→ `realtime_label`
- [ ] 尺度ビネット 8 問の初回フロー → `vignette_response`

## Task D — オフライン解析 gse-replay 拡張(A + 実データ後)
- [ ] probe_id 起点の時間隔離窓抽出(t−31s..t−1s, X/Y 集約)
- [ ] 被験者内 方向付き C-index(§7)
- [ ] 2 段ゲート判定(測定法ゲート→モデルゲート, PreReg-2/4)
- [ ] MNAR 上下限(全高摩擦/全低摩擦, PreReg-7)
- [ ] ビネット採点(PreReg-1)→ `metrics.json`
- [ ] ※ 既存 `metrics.rs` の confusion/recall は流用せず C-index 系を別パスで追加(D-14)

## Task E — 通し検証
- [ ] 自己ドッグフードで end-to-end 1 本(合成 or 実セッション)
- [ ] 3–5 名スモーク → PreReg ゲート判定(Go / Kill / INCONCLUSIVE)

---

## 後続(プラミング後・別タスク)
- [ ] コーナー段階介入 UI(Phase4・design Part C)+ `intervention_dismiss` を同一コンポーネントで合流(D-5/D-6)
- [ ] 比較条件: `context_beacon` + 波形 cue ラベル(PreReg-3 再現性)
- [ ] 統制課題 `task_checkpoint`(機能ラベル / それまでは「未評価」と明記)
