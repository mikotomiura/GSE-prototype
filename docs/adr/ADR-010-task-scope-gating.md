# ADR-010: 「どの head も当てはまらない」の扱い — head 相対 `scope_fit` と宣言/観測の役割分離

- **ステータス**: **Proposed**（設計のみ・コード変更ゼロ）。実装は Phase1 完了・凍結解除後。
- **日付**: 2026-08-02
- **対応**: Epic 2（Writing head 抽出）以降。検証は Phase2 の構造化較正。
- **関連**: **ADR-006**（`task_kind` → head ルーティング・**本 ADR は改訂しない**）/
  ADR-002（domain-local inference）/ ADR-005（additive schema）/ ADR-008・ADR-009 /
  `docs/architecture/task-adaptation-and-scope-gating.md`（設計本体）

## Context

ADR-006 は `task_kind` が **どの head を走らせるか**を決めた。しかし
**「どの head も当てはまらない」状態を定義していない**（`personalization-and-online-learning.md §11-11` の起票）。
現行コードの切替は `ime_open` の 2 値のみであり、対象外の作業は**誤った head で黙って処理される**。
`progress_proxy` は対象外作業（写経・タイピング練習）で**最大化する**ため、
Need が高いのではなく **Need の計算そのものが無意味**な区間を、システムが正常値として扱う。

2 回の実験がこの穴の埋め方を制約した:

- `experiments/20260802-task-scope-detector/`: 行動署名は**解像度を持つ**（p=0.00010）。
  判別特徴の第一候補は `bs_rate`（当初仮説の長ポーズではない）。
- `experiments/20260802-within-person-scope-detector/`: ★ **individual 基準単独の検出器は動かない**。
  マスキング（逸脱が常態化した人はフラグ不能）・尺度過敏（z=+25.8）・
  **観測全体が偏っている人にはレバレッジが無い**（唯一の外的 true positive を当てたのは母集団基準）。

外的正解ラベルは**コホート全体で 1 件**しかなく、**感度も偽陽性率も推定できない**。

## Decision

### D1. out-of-scope は **head の 1 つにしない**。head 相対の `scope_fit` フラグとする

`NullHead` / `UnknownHead` を作らない。走っている head が `scope_fit` を計算し、
`WorkStateEstimate` の `evidence_quality` を単調に減衰させ `uncertainty` を上げる。

これにより既存原則——`evidence_quality` 低下 → `none`/`defer`（`intervention-decision-engine.md`）、
**未較正 head では強介入を禁止**（`domain-adapter-boundary.md §原則`）——が**そのまま発火する**。
★ **新しいゲート機構を作らないことが本決定の要件である。**

### D2. `scope_fit` は **head 相対**であり、絶対的な「対象外作業」を定義しない

「走っている head が較正された分布と、いま観測している証拠が整合するか」と定義する。
副産物として、**ルーティングが誤っていた場合の fallback がルーティングを直さずに成立する**。
判定機構は共有し、**特徴集合と定数は head が所有する**（ADR-006 の「β は head 所有」と同じ所有規則）。

### D3. 宣言（`task_kind`）と観測（署名）が食い違っても **re-route しない**

- 宣言は **routing のみ**、観測は **`scope_fit` のみ**に使う。融合して「真の task_kind」を作らない。
- 衝突時は宣言された head を走らせ続け、`evidence_quality` を下げる。
- 根拠: (i) 宣言は Phase1 で分散ゼロ・自己申告は不一致が実測済みで、**観測は routing を検証できない**、
  (ii) 観測で re-route すると **head の baseline が次の判定の入力になる閉ループ**になる、
  (iii) 失敗コストが非対称（割引の最悪＝介入が減る／re-route の最悪＝**別 baseline で自信を持って誤採点**）。
- 自動 re-route は昇格ゲート（設計本体 §3.3）を満たすまで実装しない。

### D4. 解像度 — 推定は streaming 窓、読み出しは **Decision Episode**、セッション単位は研究解析のみ

読み出し窓長 ≤ 最短検証 block 長 を制約とし、境界をまたぐ窓は検証集合から除外する。

### D5. 検出器の**構造**を凍結し、**定数は凍結しない**

`flag := (個人内逸脱 OR コホート逸脱) AND 絶対水準ゲート`、尺度 floor、中心のコホート縮約、
★ **到達不能性（`unreachable`）を出力に含める**（「検出できなかった」と「そもそも検出できない」を区別する）。
定数は **Phase2 の構造化 block データの in-scope 側だけ**から決める
（正例を使わない＝**感度を推定量として残す**）。詳細と禁止事項は設計本体 §4.5。

### D6. Phase2 で較正する head は **Writing のみ**

Coding head の主信号（accept/reject/test/revert）は Adapter B 未実装で観測できないため
**未較正のまま運用**する（強介入禁止が自動で効く）。Creative は ADR-006 #3 により打鍵 β を持たず、
**baseline を獲得しない**（feasibility のみ）。→ 観測手段の無い head を打鍵だけで「較正済み」にしない。

## Alternatives

### A. `NullHead` / `UnknownHead` を head の 1 つとして追加する
- ✅ ルーティングの枠組みに素直に収まる。
- ❌ **切替判断に確信を要求する**。検出器は本質的に低確信（外的正解ラベル 1 件）で、確信を要求する場所に置けない。
- ❌ hard switch は走っていた head の推定を捨てる。連続的な縮退ができない。
- ❌ 新しい routing 分岐・復帰条件・UI 状態が要る＝**新機構を作らない**という §11-11 の長所を失う。

### B. 観測署名で `task_kind` を推定し **re-route する**
- ✅ 誤った宣言を実際に是正できる。
- ❌ 閉ループ（D3 の根拠 ii）。外的正解ラベルなしに本番へ載せられない。
- ❌ 失敗コストが非対称（D3 の根拠 iii）。

### C. 現状維持（out-of-scope を定義しない）
- ✅ ゼロ変更。
- ❌ 対象外作業で `progress_proxy` が最大化し、**Need の計算が無意味な区間を正常値として扱う**構造的欠陥が残る。
  ⚠️ この欠陥は「全被験者が対象作業のみを行っていた」場合でも成立する（**システムがそれを検証できない**）。

### D. individual 基準単独の検出器（前ラウンドの処方箋）
- ❌ **実測で棄却済み**。導出元の被験者でフラグ 0 件、外的根拠のある 2 件を両方取り逃し、
  代わりに実質的に平凡な 2 件をフラグした（順位の逆転）。

## Consequences

- `WorkStateEstimate` / `ContextSnapshot` に `scope_fit` と `unreachable` を **additive** に足す（ADR-005）。
  `evidence_quality` / `uncertainty` の**欄は増やさない**。
- `§4.4 Phase A` の robust quantile 実装に **尺度 floor を入れる**。
  ★ この floor は scope 検出器専用ではなく、`reference_deviation` を含む**全ての within-person z** に適用する。
- 較正プロトコル（設計本体 §2）が**検証の律速**になる。ラベルが無い限り本 ADR は PLAUSIBLE から動かない。
- R 層（自己申告の区間マーカー）は**既存 `self_marker` を再利用しない**——現行実装は
  Stuck 象限に固定されており（`lib.rs`）、相乗りさせると Phase1 のラベル意味が汚染される。
- **ADR-006 は変更しない。** 本 ADR は routing の決定に触れず、その上に scope 経路を足すだけである
  （`personalization-and-online-learning.md §9` の「拡張であって改訂ではない」と同じ関係）。

## Migration

1. Phase1 完了・verdict 確定を待つ（凍結解除）。**本 ADR の実装は Phase1 中に行わない。**
2. 較正プロトコル（設計本体 §2）を**別文書として凍結**する（`preregistration-v0.3.md` は変更しない）。
   凍結項目: block 構成 / counterbalance / 正例の種類 / 除外基準 / 定数推定手続き / 報告要件。
3. `App.tsx` の argumentative ロックを解除し、**宣言を定数から観測に戻す**（凍結対象・Phase1 後）。
4. 構造化較正で S 層データを取得 → §4.5 の手続きで定数を推定 → **事前登録して**検証。
5. 実装は **Epic 2 の抽出（2a・挙動不変）とは別コミット**にする。`scope_fit` の配線は
   `evidence_quality` を変えるため**挙動変更**であり、`HMM_VERSION` の扱いは ADR-006 Migration の
   2b（配線）と同じ規律に従う。

## 研究者判断（未確定）

- G1（統制タスク実験）へ scope block を相乗りさせるか（設計本体 §2.8・被験者負荷とのトレードオフ）。
- `phase` を Phase2 で意味づけしないという提案の可否（設計本体 §3.6）。
- 正例の 2 種類目（設計本体 §2.4）。
