# GSE v2 アーキテクチャ概要 (SSOT)

> **ステータス**: Accepted（方向性）。本書は `GSE_Post_Phase1_Improvement_Design_v0.1.md`（提案・2026-07-23）を
> Epic 0 リポジトリ実態調査（`.steering/20260724-epic0-repo-reality-check/`）に接地して昇格した
> **アーキテクチャ SSOT** である。研究の主張・エビデンス温度の SSOT は `docs/research-positioning.md`、
> 現行コードの実態は Epic 0 成果物、凍結契約は `docs/preregistration-v0.3.md` を正とする。
> 個別の設計判断は `docs/adr/` の ADR を参照。
>
> **基準日**: 2026-07-24 ／ **接地元コミット**: origin/main `dd0e058`（Epic 0 マージ済み）

---

## 0. 本書の位置づけ

旧『GSE 技術設計書』の次の前提を**そのまま引き継がない**（旧技術設計書 `docs/[提案プロジェクト補足資料]GSE技術設計書.md` は
本 SSOT へ移行のうえ docs/ から撤去。過去版は git 履歴で参照可・設計書 §0）:

- キーストローク単独で PC 作業全般の認知状態を推定する
- `FLOW / INCUBATION / STUCK` を直接的な認知状態クラスとして扱う
- HMM の三状態出力を GSE の主役に置く
- `p_stuck` の閾値から段階的介入を直接発火する
- 論述・コーディング・創作を同一特徴空間で早期に一般化する

今後の技術設計は **GSE v2 を最優先の概念基準**とする。

### GSE v2 の核（設計書 §0）

1. 本文の意味ではなく、観測可能な**作業行動の形**を扱う
2. 内面を断定せず `stuck_likelihood` / `friction_score` / `engagement_score` 等の**連続 proxy** を扱う
3. **Need と Opportunity を分離**する
4. `breakpoint_score` / `receptivity` / `cooldown` / `daily_cap` / `recent_dismiss` / `task_kind` を介入判断に使う（⚠️ **2026-09-01: `Monk Mode` を削除** — ADR-015 D2）
5. `none` と `defer` を**正式な主要アクション**として扱う
6. HMM は補助モデルとし、主役を **Intervention Decision Engine** に移す
7. 本文・クリップボード本文・ウィンドウタイトルを保存しない

検証設計は「X1 推論妥当性 / X2 介入判断妥当性 / Y プロダクト価値」を分離した v0.4 方針を維持する
（`docs/research-positioning.md §0` の層構造）。

---

## 1. 改訂後のプロダクト定義（設計書 §2.1）

> GSE は、タスク固有の操作イベントから、作業上の摩擦・前進・探索・反復と介入可能性を推定し、
> **本人が自ら是認できる (self-endorsed) 範囲**で「何もしない／待つ／軽く気づかせる／一度離す」を選択する、
> プライバシー保護型の作業調整基盤である。

> ⚠️★★★ **2026-08-30 訂正（研究者承認）—— 旧文は「本人の *自律性を損なわない範囲で*」だった。**
> ★ **定義が空で、誤読の危険があった。**★ SDT の autonomy は原典逐語で **"regulation by the self"**、
> その反対 heteronomy は **"regulation that occurs without self-endorsement"** [P178]。
> ★★★ *"having many options is not a basic need"* / *"one could have only one option … and yet feel quite
> autonomous so long as one truly endorses that option"*。
> → ⚠️★★★ **「選べる／消せるから自律的」は SDT では成立しない。**
> ★ 正しい根拠は **「本人が事前に *是認 (self-endorse)* している」**ことである。
> ⚠️ **計器は未確定** —— 唯一の候補は **[V88] METUX の TENS-Interface**（★ Gate H の運用指標。
> ⚠️ 著者自身が初期版と留保しているので確証には使わない）。詳細は `research-positioning.md` §5 H-Y-b。

### 維持する独自性（§2.2）
生産的苦闘を即答で置換しない／本文を読まず作業構造を扱う／介入しないことを価値ある判断とする／
Need と Opportunity を分ける／拒否と「今はもがきたい」を学習信号にする／必要時のみ身体的回帰を提案する／
AI 利用を禁止せず主体性を失った利用パターンを対象にする。

### 段階的に捨てる主張（§2.3・技術設計/README/提案資料から降格）
- 「人間の認知状態をキーストロークだけで読む」
- 「Flow / Incubation / Stuck を正確に分類する」
- 「5 秒の沈黙から深い熟考か固着かを判定できる」
- 「PC 作業全般へそのまま汎用化できる」
- 「貼り付け回数が AI 依存度を示す」／「打鍵量が自力解決率を示す」

→ 実装上の残存箇所と降格方針は **ADR-001**（HMM を Writing baseline へ降格）を参照。

---

## 2. 7 層アーキテクチャ（設計書 §3.1）

```text
[0] Session Context      task_kind / work_intent / support_consent / intervention_profile
        ↓
[1] Domain Event Adapter Writing / Agentic Coding / Creative Editing
        ↓
[2] Privacy Boundary + Event Envelope   内容を除去し操作種別・量・時間・結果だけ保持
        ↓
[3] Domain-local Feature Extraction     タスク固有特徴量
        ↓
[4] GSE v2 Work-State Proxy   friction / stuck_likelihood / engagement / incubation_like_pause / flow_like_continuation
        ↓
[5] Opportunity & Receptivity   breakpoint / receptivity / cooldown / daily_cap / recent_dismiss
        ↓
[6] Intervention Decision Engine   none / defer / nudge   (⚠️ zen / wall は ADR-015 D1 で削除)
        ↓
[7] Outcome & Harm Evaluation   recovery / loop escape / helpfulness / annoyance / autonomy / reuse
```

**重要な制約**: 「共通イベント層」を作っても、異なるタスクの意味を早期に同一化しない。Writing の Backspace と
動画編集の Undo はどちらも revision 系だが、同一の重み・同一の `stuck_likelihood` へ直接入れてはならない。
> ⚠️★★★ **2026-09-02 追記（ADR-019 D2 / ADR-020 D1）**
>
> - ★ **本 7 層 `Layer 0`–`Layer 7` が処理の呼称の SSOT である。**
>   ⚠️ `.idea/20260901-…` §15 が提案した **`L1〜L4`（Mh-D 内部）は採らない** ——
>   repo には既に **L1/L2 を別の意味で使う体系が 3 系統**ある
>   （① 本 7 層 ② `glossary.md` の「MhD（L1）→ Need 層（L2）」 ③ 表現層の「層 0–3」）。
>   ★ 新設すると **4 系統目**になり、`L2` が 3 通りの意味を持つ。
> - ★ **モデルの成熟は `M1`〜`M4` と呼び、処理層とは別の軸として扱う**（ADR-019 D1）。
>   ⚠️ **「Stage」とは呼ばない。**
> - ⚠️★★★ **7 層の外に「長期プロファイル層」を足さない**（ADR-020 D1）。
>   ★ 長期の量は **ADR-018 D5 の行動指標の時系列**として扱い、**固有名を与えない**。

共通化するのは (1) ログのメタデータ構造 (2) Decision Engine へ渡す proxy のインターフェース の 2 点に限定し、
特徴抽出と較正は domain-local とする。詳細は `docs/architecture/domain-adapter-boundary.md`。

---

## 3. 現行実装 ↔ v2 層の対応（Epic 0 接地・真実源）

> 出典: `.steering/20260724-epic0-repo-reality-check/{repo-inventory,design-vs-code-gap}.md`。
> ◎=実装済 / ○=名前違い・分解形で実装 / △=部分 / 記録=schema のみ / ✗=未実装。

| v2 層 | 現行実装 | 状態 |
|---|---|---|
| [0] Session Context | task_kind を `session_meta` に記録するのみ。WorkIntent/SupportConsent は **0 ファイル** | 記録/✗ |
| [1] Domain Event Adapter | **なし**（`input/` が直接 `analysis/` へ）。Writing/Coding/Creative 分離なし | ✗ |
| [2] Event Envelope / Privacy | 本文非保存は徹底（VK コードのみ・data-privacy）。共通 `EventEnvelope`/`EventFamily` 外枠は未実装 | ○/✗ |
| [3-4] Work-State Proxy | `features.rs`(F1/F3/F4/F5/F6) → `engine.rs`(HMM・β dual baseline) → `loop_step.rs` | ◎（Writing 前提） |
| [5] Opportunity & Receptivity | `intervention.rs` の opportunity_score + cooldown/daily_cap/recent_dismiss + idle gate | ◎（receptivity は**分解形**・統合スコアは未実装） |
| [6] Decision Engine | `intervention.rs` `InterventionAction{None,Nudge,Defer}`（⚠️ **`Wall` は ADR-015 D1 で削除**・`intervention.rs:16-20`）・`new_with_thresholds` で閾値注入可 | ◎（Need/Opportunity 分離済・Consent 軸は未実装） |
| [7] Outcome & Harm | `metrics.rs` + `intervention_eval.rs` | △（harm は HIR のみ） |

### 特筆すべき実態（設計判断の前提）
- **Need / Opportunity 分離・`none`/`defer` 第一級・cooldown/daily_cap/recent_dismiss は既に実装済み**。
  設計書の中核は「新規実装」でなく「整理」が主。
- ⚠️★★★ **2026-09-01 訂正 —— Monk Mode は 2026-08-23 に削除された**（ADR-015 D2）。
  ★ かつ旧文の「**Monk Mode = 介入拒否**」という Epic 0 の理解自体が **ADR-015 Context-3 で否定されている** ——
  実装上の作用は **Wall 抑制のみで Nudge は抑制していなかった**。
  ⚠️ 旧文が名指しした `apply_wall_suppressions` は存在せず、現存は `apply_nudge_suppressions`（`intervention.rs:334`）である。
  設計書 §12-1 の揺れは Epic 0 で解決済み。
- ⚠️★★★ **2026-09-01 訂正 —— 旧文「`task_kind` は HMM β に未配線」は誤りである。**
  ★ **2026-08-18 に配線済み**（ADR-006 Phase 2b・`HMM_VERSION` を `0.4.0` へ bump）。宣言された `task_kind` が
  `record_session_meta` 経由で `CognitiveStateEngine::set_domain()` を呼び **domain head を選ぶ**
  （`analysis/heads/mod.rs` / `analysis/engine.rs:286`）。`ime_open` は **Writing head 内部の
  within-writing 信号**に降格した（`analysis/heads/writing.rs`）。
  ⚠️ **旧文は同じファイルの §「2026-08-18 の更新」と自己矛盾していた。**
  ★ **残る穴は `task_kind` 未宣言のセッション** —— 既定の Writing head で採点される（`engine.rs:133`）。
  ⚠️ かつ宣言は**自己申告**であり、宣言と実作業が食い違っても系は検証できない。→ **ADR-006 / ADR-010**。
- 旧 **Flow/Incubation/Stuck 三状態表示**が `src/App.tsx` / `src/components/Dashboard.tsx` に残存。ただし
  calibration blind（week1）では非表示に gate 済み。v2 では連続 proxy 表示へ置換 or 歴史的説明へ降格（**ADR-001**）。

---

## 4. HMM の位置づけ（設計書 §3.5・§7.2）

現行 HMM は**廃棄しない**。ontology の主役から Writing Head の baseline へ降格する。

```text
旧:  HMM → 三状態 → 介入
新:  Writing events → Writing features → HMM / rule baseline → v2 proxy + uncertainty → Opportunity → Decision Engine
```

HMM は Writing Head の**一候補**であり GSE 全体の ontology ではない。詳細は **ADR-001**。

### 旧技術設計から置換する章（設計書 §7.2）

> 旧技術設計書は本 SSOT へ移行して撤去済み。以下は「旧章の主張 → 本 SSOT が引き継ぐ新しい扱い」の対応表
> （旧版の文面は git 履歴で参照可）。

| 旧章・主張 | 新しい扱い |
|---|---|
| Keystroke-First Design | Privacy-preserving Behavior-First。Writing は Keystroke-first adapter |
| FLOW/INCUBATION/STUCK 3 状態 | v2 の連続 proxy。三状態は補助的説明・旧 baseline |
| HMM Core | Writing Head の baseline |
| Sensing→Inference→Intervention→Physical Anchor | Context→Adapter→Domain features→v2 proxy→Opportunity→Decision→Outcome |
| `p_stuck` 閾値発火 | Need × Opportunity × Receptivity × Consent |
| 段階介入 | `none / defer / nudge`。強度と種類を分離（⚠️ `zen` / `wall` は ADR-015 D1 で削除。★ **段階呼称 Lv1〜Lv4 は ADR-018 D7 で廃止方向**。★ 復活には新規 ADR が要る）|
| PC 作業全般へ汎用 | domain-local 検証後に限定的転移を評価 |
| AI 依存 = 貼付 | domain-specific agency / review / recovery 指標 |
| Physical Anchor を最終段階の必須要素 | ★ **表現層の出口として構造的に必須**（既決 D8 / ADR-017 D7 —— ⚠️ 単独アームで headline 評価しない）。初期は opt-in。★ **完了条件を持たない「身体的回帰への方向づけ」**（ADR-018 D1）。評価量は**招待の受容 ＋ 機会保存の行動指標**（ADR-018 D5・**実行率 / 完了率ではない**）|

---

## 5. エビデンスの温度（過大主張の禁止・最重要）

> SSOT: `docs/research-positioning.md §1/§8`。本節は設計判断に効く要点の写しであり、効果量の一次根拠は
> research-positioning と `docs/references.md`（`[Pn]`/`[Vn]`）を参照する。**新設計を「効くはず」で実装しない**。

### 実証で支持されている（採用してよい）
- **`none`/`defer` の第一級化**: 受動観測の行動指標が受容性を予測し、自己申告指標は予測しなかった [V43]。
  「介入しない／待つ」を主要アクションに据える方向はエビデンスと整合する。
- **Motivation Generator を標準実装しない**: 実行意図の効果は出版バイアス補正で素 d=.36 → 補正後 **d≈.15** [P21]、
  ナッジ assistance 系は d=.22 → **≈.01** [V40]。if-then 計画・目標宣言・常時表示・カウントダウン・連続記録を
  標準機能にしない（設計書 §1.4/§3.2）。
- **Gate D（Demand）の桁の prior 化**: in-the-wild 30 日継続率 中央値 ~3.3% [V41]、登録経路が継続を支配 [V42]。
  実証で支持されているのは**外部ベンチの継続率の桁**であって **GSE 自身の需要が実証済みという意味ではない**。
  需要ゲートの閾値は「効くはず」でなく、この外部実測の桁を **prior として参照**するに留める（GSE の Demand は Gate D で今後測る）。

### 未検証（効果を主張しない・思想/設計として扱う）
- **Session Context（WorkIntent / SupportConsent）**: 3 ラウンドのサーヴェイで一度も直接検証されていない。
  むしろ [V43] は自己申告が受容性を予測しない**逆風**。→ receptivity の**主軸は行動指標**（cooldown/idle/recent_dismiss・
  既実装）に置き、Session Context は従。採用の正当化は次の 2 つ**のみ**で、効果は主張しない:
  1. **交絡の切り分け（解析 covariate）**: `WorkIntent=LowIntent` を記録し「need 高は詰まりでなく低意欲」を
     事後区別する（H-Y 解釈の共変量。効果の主張ではない）。
  2. **倫理・自律性ゲート**: `SupportConsent==ObserveOnly → 介入 none`（研究倫理・opt-in の原則）。
  → 詳細は **ADR-002 / ADR-003** と `intervention-decision-engine.md`。
- **Accountability Extension**（義務感・他者存在）: n=1 逸話水準。GSE Core と交絡するため **core 外の opt-in
  extension** に分離（**ADR-003**）。効果は第4ラウンド（RQ-3）確認後に判断。
- **Agentic Coding の過信 proxy**（`agency_balance` 等）: 第4ラウンド（RQ-2）で証拠ゼロ。observe-only の
  feasibility に留め、`agency_balance` は善悪スコアにしない（構成の記述 proxy）。→ Epic 4。

### 理論接地 = 機会保存（learning ではない）
GSE が主張するのは「摩擦が能力・学習を**育てる**」ではなく「**反射的な外部依存（即座の AI/検索オフロード）を
減らし、自力で解こうとする試行が発生する機会を保存する**」こと。**行動指標**（`external_paste_after_stuck` /
`self_recovery_without_paste` / `manual_contribution_ratio`）で測る。[P12] Kapur・[P9] Bjork は
「**守るべき困難が存在することの根拠**」に用い、「摩擦が学習を生む」の効果的接地には使わない
（PS-I メタ分析は摩擦単独の学習効果を支持しない [P27][P28]）。学習効果は将来の探索トラック
（research-positioning §8）。

---

## 6. 移行戦略と Epic ロードマップ（現在地）

> 詳細: `.steering/20260724-epic0-repo-reality-check/{migration-risk-register,adr-and-issue-roadmap}.md`。
> **すべて Phase1 完了 + 研究者承認が前提**。凍結対象（下記）は Phase1 完了まで変更禁止。

**Step 0 凍結対象**: NDJSON schema(`schema_dto.rs`/`schema/current.json`) / HMM 挙動(`engine.rs` HMM_VERSION・
`loop_step.rs`) / 介入閾値(`intervention.rs` 定数) / プローブ機構(`probe_scheduler.rs`) / argumentative lock
(`App.tsx`) / PreReg 契約(`preregistration-v0.3.md`)。

> ★★★ **2026-08-18: Phase1 は収集打ち切りで終了し、凍結は解除された**（verdict = `inconclusive` /
> GATE3 = `DataInsufficient`）。ADR-002 / ADR-006 を実装し、`HMM_VERSION` は **`0.4.0`** へ bump、
> NDJSON schema には `session_meta.head_id` を **additive** に追加した
> （`.steering/20260818-adr006-head-extraction-wiring/`）。
> ⚠️ **`intervention.rs` 閾値 / `probe_scheduler.rs` / `App.tsx` argumentative lock /
> `preregistration-v0.3.md` は今も未変更**である（解除されたが、まだ触っていない）。

| Epic | 内容 | 状態 |
|---|---|---|
| Epic 0 | Repository Reality Check（コード変更なし） | ✅ 完了（PR #70） |
| **Epic 1** | **Architecture ADR + docs SSOT 昇格（コード変更なし）** | ◀ **本書・進行中** |
| Epic 2 | Writing Adapter 抽出（動作非変更・replay parity が acceptance） | Phase1 完了後 |
| Epic 3 | Intervention Decision Refactor（Consent 軸新設・reason code ログ化） | Epic 2 後 |
| Epic 3.5 | Session Context 層（効果未検証・covariate/倫理ゲートに限定） | Epic 3 同時/直後 |
| Epic 4 | Agentic Coding Discovery（observe-only・第4ラウンド確認後に feasibility から） | エビデンス待ち |
| Epic 5 | Evaluation Pipeline v2（Gate D/S/X1/X2/Y/H schema 化） | 後続 |
| Epic 6 | Creative Editing Feasibility（Go/Defer/Kill 判定のみ） | 優先度最低 |

### Phase1 verdict による分岐（設計書 §5・migration-risk-register）
Go → Writing Adapter の X1 証拠として保存。Inconclusive/DataInsufficient → Writing 探索継続（全体再設計とは分離）。
**Kill → Writing Head/HMM の破綻。GSE 全体の Kill とはしない**（Adapter 抽象化はむしろ Writing Head 差替を可能にし有効）。

---

## 関連文書
- 詳細層設計: `docs/architecture/domain-adapter-boundary.md`（Layer 0-3）／`docs/architecture/intervention-decision-engine.md`（Layer 5-7）
- **個人適応・オンライン学習（Layer 3-4 拡張・Proposed）**: `docs/architecture/personalization-and-online-learning.md`
  — Phase1 較正の実測を受けた X 軸の再定義（`self_directed_recovery_risk`）、オンライン更新の層別境界、
  潜在状態の扱い、反証ゲート。**本書の 7 層（§2）と Epic ロードマップ（§6）は変更しない**（Layer 4 出力への
  additive 追加の提案に留まる）。決定は ADR-008 / ADR-009
- 設計判断: `docs/adr/README.md`（**ADR-001〜018**）
- 研究の主張・エビデンス: `docs/research-positioning.md`
- 現行実態: `.steering/20260724-epic0-repo-reality-check/`
- 昇格元（歴史資料）: `~/Downloads/GSE_Post_Phase1_Improvement_Design_v0.1.md`
