# ADR-006: task_kind → β baseline 配線 or IME 状態を代理とするか

- **ステータス**: **Deferred**（研究者判断待ち・★Post-Phase1 の最優先論点）
- **日付**: 2026-07-24
- **対応**: Epic 2（Writing Adapter 抽出）の分岐点。roadmap ADR-006。
- **関連**: ADR-001（HMM 降格）/ ADR-002（domain-local inference）/ `docs/architecture/domain-adapter-boundary.md §Layer 3-4`

## Context

GSE の HMM は特徴量を潜在二軸へ写す際、**dual baseline β** を使う（`engine.rs:291` `calculate_latent_axes`）。
現行の β 選択は **`ime_open`（日本語 IME on/off）による**（実測・Epic 0 で確認）:

```rust
// src-tauri/src/analysis/engine.rs:311
let (beta_f1, beta_f3, beta_f4, beta_f5, beta_f6) = if ime_open {
    // β_writing: Japanese typing baseline
} else {
    // β_coding: Alphanumeric/coding baseline
};
```

さらに `ime_open` は β 選択だけでなく **backspace ペナルティも gate** する
（`engine.rs:367` `apply_backspace_penalty = pending && !ime_open`。IME 変換修正の BS 連打を誤ペナルティしないため）。

一方 **`task_kind`（`Argumentative/Correspondence/Creative/VibeCoding` の 4 変種）は `analysis/` に一切渡っていない**
（`grep task_kind src-tauri/src/analysis/` = 0 件・Epic 0 で確認）。`task_kind` は `logger`/`schema_dto` の enum と
`session_meta` の**記録専用メタ**であり、推論パイプラインでは **dead_code**。

つまり現状、「どのドメインの baseline で採点するか」は**宣言された task_kind でなく、その瞬間の IME 状態が代理**している。

### ⚠️ 誤解の防止（この ADR がしないこと）
本 ADR は **「日本語 IME をやめる」話ではない**。`ime_open` は「今この瞬間、日本語 IME が日本語入力モード
（あ/カ）か」を表す**実行時フラグ**であり、争点は「β baseline の**選び方**を実行時 IME 状態にするか task_kind に
するか」だけである。以下は **A/B/C のどの案でも変わらない・閉じない**:
- **日本語 IME キーストロークの捕捉・記録**（composition/confirmation イベント・VK コード）は `input/`・`logger` 層の
  責務で、β 選択ロジックとは**直交**する。ADR-006 では触れない。
- **gse-dataset での日本語 IME タイプデータ公開**（未踏アピール）は保全される。NDJSON schema の IME 関連フィールドは
  変更しない（凍結・ADR-005 も additive のみ）。
- 推奨 **C** はむしろ `ime_open` を Writing head 内の within-writing 信号として**明示的に維持**する
  （backspace ペナルティ gate 含む）。IME 検出・IME 特徴量を捨てる案は A/B/C のいずれにも含まれない。

### なぜ今 Phase2 マルチタスク化の分岐点か
- Phase1 は `argumentative`（日本語論述）に**固定**（`App.tsx` argumentative lock・凍結）。この間は
  ほぼ IME on = β_writing が使われ、task_kind は定数なので**配線しても Phase1 データは変わらない**。
- Phase2 でタスクを混在させると、IME 代理は破綻しうる: 英字引用を打つ writer（IME off → 誤って β_coding）・
  日本語コメントを書く coder（IME on → 誤って β_writing）。`research-positioning §8` は
  「task_kind→β 未配線 → タスク混在は単一 β での採点ミスマッチ（交絡）」と明記。

### 制約（この ADR を Phase1 中に実装できない理由）
- β 選択ロジックの変更は **HMM 挙動の変更** = `HMM_VERSION`(現 `0.3.0`) bump = ゴールデン（replay --snapshot）
  不一致 = **Phase1 の C-index 再現性を破壊**（migration-risk-register の凍結対象）。
- 従って**実装は Phase1 完了後の Epic 2 以降**。本 ADR は方向を決めるのみ。

## Decision

**二者択一（配線 vs 代理）を単純採決せず、「決定を Deferred のまま、v2 で採る枠組みを Alternative C（分離）に
寄せる」ことを推奨し、確定は研究者判断に委ねる。**

推奨の骨子（Alternative C・下記）:
1. **task_kind は「どの domain head/baseline set を使うか」を選ぶ上位信号**とする（ADR-002 の Adapter 境界と一体）。
2. **IME 状態は Writing head 内部の within-writing 信号**として維持する（β_writing 内の日本語 composition・
   BS ペナルティ gate は writing 固有の挙動であり、ドメイン選択の役割から切り離す）。
3. 実装は Phase1 完了後・`HMM_VERSION` bump とセット・**動作非変更を破る変更**なので Epic 2 の acceptance
   （replay/calibration parity）を満たす形で段階導入する。

**なぜ確定でなく Deferred か**: (i) 凍結対象（engine.rs/HMM_VERSION）に触れ Phase1 完了が前提、
(ii) Phase1 は task_kind 定数のため**今この配線を検証するデータが無い**、(iii) 選択は「β を 2 本維持するか
head-local baseline にするか」という ADR-002/Epic 2 の抽象化と不可分。→ Phase1 verdict 確定後に ADR-002 と
同時確定するのが安全。

## Alternatives

### A. task_kind → β を直接配線（IME 代理を廃止）
`SessionContext.task_kind` を engine に渡し `task_kind ∈ {writing系} → β_writing / {coding系} → β_coding`。
- ✅ 宣言と baseline が一致・研究上の交絡（§8）が明快に消える。
- ❌ IME が担っていた **within-writing の意味**（日本語 composition の BS ペナルティ gate）を失う/再設計要。
  IME off の英字引用も一律 β_writing になり、writing 内の latin バーストで採点がずれうる。
- ❌ `Creative`/`VibeCoding` を「coding β」に丸めるのは粗い（Creative は打鍵が薄く β 自体が不適・adapter-boundary §Adapter C）。

### B. 現状維持（IME 状態を β 選択の正とし、task_kind は記録専用のまま）
- ✅ ゼロ変更・Phase1 と完全整合・IME の within-writing 意味を保つ。
- ❌ Phase2 のタスク混在で交絡が残る（§8）。task_kind が永続的に dead_code。
- ❌ v2 の「task_kind ごとに baseline と閾値を分ける」原則（設計書 §3.5）を満たさない。

### C. 分離（推奨の枠組み）: task_kind → head/baseline-set 選択、IME → within-writing 信号
- task_kind が **domain head を選び**（Writing/Coding/Creative・ADR-002）、β は各 head のプロパティにする。
  Writing head の中では IME 状態が composition/BS gate の within-writing 信号として残る。
- ✅ 宣言（task_kind）と観測（IME）の**役割を直交**させる。v2 の domain-local baseline 原則と整合。
  Creative の「β 不適」問題も head 差替で自然に扱える。
- ✅ Phase1 は Writing head のみ = 現行挙動を包含（動作非変更で抽出可能・Epic 2 acceptance と両立しやすい）。
- ❌ Adapter 抽象化（ADR-002）と同時実装が必要で重い。head 未較正時の強介入禁止（adapter-boundary §原則）を要配線。

## Consequences

- **採用（C 推奨）した場合**: ADR-002 と一体で Epic 2 を進める。engine の β は Writing head 内へ移送し、
  IME gate は writing 固有として保持。`HMM_VERSION` bump + replay/calibration parity を acceptance に。
  task_kind が初めて推論に効くのは Coding head 追加時（Phase2）。
- **A を採る場合**: 実装は軽いが within-writing の意味喪失を別途補償する設計が要る。Phase1 の β_writing 挙動を
  厳密再現できるか（IME off 論述の扱い）を replay で必ず検証。
- **B を採る場合**: task_kind は当面 dead_code のまま。Phase2 前に本 ADR を再訪する必要が残る。
- いずれも **Phase1 中は実装しない**（凍結）。Phase1 が Kill でも Writing Head 差替の価値は残る
  （migration-risk-register・GSE 全体 Kill としない）。

## Migration

> **★2 段階に分ける（ADR-002 との acceptance の食い違いを避ける）**: Epic 2 は「抽出」と「配線」の 2 サブフェーズに
> 分離する。抽出は**動作非変更＝HMM_VERSION 不変**（ADR-002 の acceptance）、配線は**挙動変更＝HMM_VERSION bump**。
> 両者を混ぜて 1 コミットにしない。

1. Phase1 完了 + verdict 確定を待つ（凍結解除）。
2. ADR-002（Adapter 境界）と本 ADR を**同時に**確定する（研究者承認）。
3. **Phase 2a（抽出・動作非変更）**: engine/features/β を Writing head へ**挙動を一切変えず**移送し、`ime_open` gate を
   writing 固有として保持する。acceptance = **replay --snapshot byte-equal / calibration parity / `HMM_VERSION` 不変**
   （ADR-002 と一致）。β 選択ロジックはこの段では**変えない**。
4. **Phase 2b（配線・挙動変更）**: task_kind を head/baseline 選択へ効かせる（Alt C なら Writing head 内は現行、
   Coding head 追加で task_kind が baseline に効く）。**この段で初めて `HMM_VERSION` を bump** → ゴールデン再生成 →
   差分が意図通りか `.steering/` に記録（`git-workflow`/`ml-workflow`）。
5. `schema_dto.rs` は additive のみ（task_kind enum は 4 変種維持・`emit_schema` diff を確認）。
6. Coding head 追加（Phase2）で初めて task_kind が baseline 選択に効く。cross-domain contamination guard は Epic 5。

## 研究者への判断依頼（この ADR で確定できない点）
- **Alternative A / B / C のどれを正とするか**（推奨は C・分離）。
- IME off の日本語論述（英字引用・数式）を Writing head 内でどう扱うか（β_writing 固定 or 細分）。
- `Creative`/`VibeCoding` の baseline を coding β 流用にするか head 固有にするか（Creative は打鍵希薄で要検討）。
