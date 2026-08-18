# ADR-006: task_kind → β baseline 配線 or IME 状態を代理とするか

- **ステータス**: **Accepted（枠組み = Alternative C「分離」＋下位決定 #2/#3 も確定・研究者採択 2026-07-24）**。
  ★ **実装済み（2026-08-18・2a 抽出 / 2b 配線の 2 コミット）** — 下記「実施記録」参照。
- **日付**: 2026-07-24（提起 → 枠組み C 採択 → 下位決定 #2/#3 確定、すべて同日）
- **対応**: Epic 2（Writing Adapter 抽出）の分岐点。roadmap ADR-006。
- **関連**: ADR-001（HMM 降格）/ ADR-002（domain-local inference）/ `docs/architecture/domain-adapter-boundary.md §Layer 3-4`
- **拡張**: **ADR-010**（「どの head も当てはまらない」= head 相対 `scope_fit`）。
  本 ADR が決めた **head の選択**に、**選ばれた head が当てはまっていない場合の経路**を足す
  （`evidence_quality` を下げるだけで re-route しない）。**本 ADR の Decision は変更しない。**

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

**枠組みとして Alternative C「分離」を採択する（研究者判断・2026-07-24）。** 二者択一（配線 A / 代理 B）は採らない。

C の骨子:
1. **task_kind は「どの domain head を走らせるか」を選ぶ上位ルーティング信号**とする（ADR-002 の Adapter 境界と一体）。
   β は各 head の所有物に格上げし、「1 関数内の 2 択 if」から外す。
2. **IME 状態（`ime_open`）は Writing head 内部の within-writing 信号**として維持する（β_writing 内の日本語
   composition・BS ペナルティ gate は writing 固有の挙動であり、ドメイン選択の役割から切り離す）。
3. 実装は Phase1 完了後。**抽出（挙動不変・no bump）と配線（挙動変更・bump）を 2 サブフェーズに分ける**
   （Migration 参照）。

**採択根拠**: A/B は単一 HMM 内の β 切替の入力を変えるだけで、Phase2 のタスク混在時に交絡（§8）が戻る。
C は task_kind（宣言）と IME（観測）を**直交**させ、Phase1 挙動を包含したままドメイン追加に耐える。日本語 IME
信号を Writing head 内に温存するため IME データ収集・dataset 公開とも矛盾しない（→ Context「誤解の防止」）。

**なぜ「枠組み採択」に留め、実装は Deferred か**: (i) 凍結対象（engine.rs/HMM_VERSION）に触れ Phase1 完了が前提、
(ii) Phase1 は task_kind 定数のため**今この配線を検証するデータが無い**、(iii) 下位2点（下記）が未決。
→ Phase1 verdict 確定後、ADR-002 と同時に実装着手する。

### Alternative C の実装形（具体化）

```rust
// 現在: 1 つの HMM・β は 2 セット・切替 = 実行時 IME 状態
//   fn calculate_latent_axes(features, ime_open) { let β = if ime_open { β_writing } else { β_coding }; }

// C: task_kind が head を選ぶ。β は各 head のプロパティ。
match session.task_kind {
    Argumentative | Correspondence =>
        WritingHead.infer(features, ime_open),   // ime_open は head 内部で β_writing・日本語composition・BS gate を制御
    VibeCoding =>
        CodingHead.infer(features, /* focus / test / accept 等の coding 信号 */),  // 自前 baseline
    Creative =>
        CreativeHead::feasibility_only(),         // 打鍵希薄・Epic 6 feasibility のみ
}
```

- **現行 β_coding（IME off で選ばれる分）の行き先**は下位決定 #3 に依存する未決の移行論点（Coding head baseline へ
  移す／Writing head 内の「IME off 英字・数式」サブ baseline として残す）。
- Phase1 は Writing head のみ稼働 ＝ 現行挙動と一致するため、抽出フェーズ（2a）は **`HMM_VERSION` 不変**で通せる。

### 下位決定（確定・研究者採択 2026-07-24）

**#2 IME off の日本語論述（英字引用・数式・URL）の β 扱い → 「再スコープ（collapse しない）」を採択。**
- Writing head 内に **latin/英数サブ baseline** を持つ。値は**現 `β_coding`（F1=150 / F3=0.06 / F4=5.0 / F5=2.0 / F6=0.08）を
  そのまま `β_writing_latin` に改名**して流用し、`ime_open` で `β_writing`（IME on）と切り替える。
- **backspace ペナルティ（obs=25・streak≥14）は現行どおり `!ime_open` 紐付けを維持**。
- 根拠: β_writing（F1=100 / F4=2.5）は日本語 IME 変換のリズム。ラテン直接入力は速く・バーストが長く、現 β_coding プロファイルに
  近い。β_writing 固定に collapse するとラテン窓を誤採点する。**再スコープは現行挙動そのものの概念的分離**であり、
  **抽出フェーズ（2a）で byte-equal 維持＝`HMM_VERSION` bump 不要**（改名は数値変更を伴わない）。

**#3 VibeCoding / Creative の baseline → 「head 所有 ＋ Creative は打鍵 β 無し」を採択。**
- **VibeCoding**: Coding head が **現 `β_coding` を初期シードとして継承**し、以後は**自前で所有・再チューニング**する。
  ただし Coding head の**主信号は打鍵 β でなく coding イベント**（accept/reject/test/revert/diff-review・
  `domain-adapter-boundary.md §Adapter B`）。エージェントコーディングは AI 操作主体で連続打鍵が薄いため、打鍵 β は弱い補助。
- **Creative**: **打鍵 β を持たせない**。打鍵希薄で無音＝idle と区別できず打鍵 β は原理的に不適。feasibility のみ（Epic 6）、
  head を作るなら編集/タイムラインイベント基盤。**現 β_coding の流用はしない**。
- 帰結: 現 β_coding は v2 で **2 つの所有者に分岐**する — (i) Writing head の `β_writing_latin`（#2・値そのまま）、
  (ii) Coding head の初期 β（#3・以後独立に再チューニング）。両者は同じ数値から出発するが概念的・進化的に別物。

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

### C. 分離（★採択・2026-07-24）: task_kind → head/baseline-set 選択、IME → within-writing 信号
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

## 実施記録（2026-08-18・`.steering/20260818-adr006-head-extraction-wiring/`）

Phase1 が **収集打ち切りで終了**（verdict = `inconclusive` / GATE3 = `DataInsufficient`）し
凍結が解除されたため、Migration step 1 の条件が成立して着手した。**2 コミットに分けた**（逐語どおり）。

| サブフェーズ | コミット | `HMM_VERSION` | ゴールデン |
|---|---|---|---|
| **2a 抽出** | `refactor(engine): β を Writing head へ移送し β_coding を β_writing_latin に改名する` | `0.3.0` **不変** | 4 本 **byte-equal**（＋全 10 fixture が対 main で byte-equal） |
| **2b 配線** | `feat(engine): task_kind を head 選択へ配線し Coding head v0 を追加する` | `0.3.0` → **`0.4.0`** | 既存 4 本 **byte-equal のまま**・新規 `vibe_coding_ime_mixed` を追加して 5 本 |

### ★ 本 ADR に書かれていなかった点で、実装時に決めたこと

| # | 論点 | 決定 | 記録 |
|---|---|---|---|
| **D-3** | ⚠️ 本 ADR は BS ペナルティ gate を「Writing 固有」と書いたが **Coding 側の扱いを書いていない** | Coding head v0 も **同じ `!ime_open` gate を持つ**。2b の目的は β の取り違えを直すことであって BS 挙動を変えることではない | `decisions.md` D-3 |
| **D-4** | ⚠️ `engine.rs` の SemVer 定義（MAJOR/MINOR/PATCH）は**すべて「既存ログ」基準**で、「まだ存在しない入力クラスにだけ挙動が出る」今回のケースを覆っていなかった | **`0.4.0`（MINOR）** とし、**SemVer 定義そのものに 1 行足して穴を埋めた** | `decisions.md` D-4 |
| **D-5** | ⚠️ 既存ゴールデン 4 本は全て argumentative 相当なので **2b でも byte-equal のまま**＝ Migration step 4 が要求する「差分」が存在しない | `vibe_coding_ime_mixed` を**新規追加**。既存 4 本の byte-equal は「無関係な副作用が無いこと」の証明に使い、新規 1 本が「意図した差分」を担う | `decisions.md` D-5 / `diff-intent-2b.md` |
| **D-6** | ⚠️ 下位決定 #3 は「Creative に打鍵 β を持たせない」と決めたが、**代替 head がまだ無い**ので字義どおり実装すると Creative で推論が出せない | Writing head へ流し、`head_id = writing_fallback` を刻んで**事後に分離できる**ようにした。**#3 からの意図的な逸脱**。数値挙動は Writing と完全に同一 | `decisions.md` D-6 |
| **D-8** | ADR-002 の trait 範囲 | `DomainInferenceHead` のみ実装。`DomainAdapter`（`ingest`/`privacy_audit`）は Epic 4/5 | `decisions.md` D-8 / ADR-002 |

### ★ 実装上の発見（次に触る人へ）

1. ⚠️ **engine はアプリ起動時に 1 個だけ作られ、`start_session` の `reset()` は head に触れない**（実測）。
   `task_kind` は `start_session` の**後**に `record_session_meta` で届くので、
   構築時に head を固定すると本番では永久に Writing head のままになる。
   → head を `Arc<Mutex<Arc<dyn DomainInferenceHead>>>` にして `set_domain()` で差し替える形にした。
   ⚠️ **`start_session` と `record_session_meta` の間の 1Hz tick は Writing head で走る**（窓は 1 秒未満）。
   塞ぐには `start_session` に `task_kind` を持たせる必要があり、フロントの IPC 契約変更を伴う（未実施）。
2. ⚠️ **`head_id` は `FeatSnapshot` ではなく `session_meta` に置く。** `FeatSnapshot` に足すと
   ゴールデン snapshot が全滅し、2b の acceptance（既存 4 本 byte-equal）が消滅する。
3. ⚠️ **`bin/replay.rs` は `session_meta` を読み飛ばしていた**（`timestamp() == None` でソート対象外）。
   `task_kind` を engine 生成前に抽出する配線を足さないと、**リプレイが本番の挙動を再現できない**。
4. ★ **`task_kind` → `TaskDomain` の変換は `logger.rs` に 1 本だけ置く**（`impl From<TaskKind>`）。
   本番（`lib.rs`）とリプレイ（`bin/replay.rs`）が同じ経路を通らないと、ゴールデンが守っている保証が嘘になる。

### ⚠️ まだ効いていないこと

★ `App.tsx` の **argumentative lock が残っている**ため、実運用では `vibe_coding` セッションが発生せず、
2b は「**lock を外した瞬間に効く**」状態で置いてある。lock 解除は Phase2 の募集・教示・条件割付の
運用設計とセットの別タスク（`decisions.md` D-9）。
★ また `research-positioning.md §9` A-Q3 の解除条件②は、**Coding head が自前 β を持って初めて実質的に満たされる**
——これは 2b で満たした。もう片方の条件①（B-a プール倍率の実数）は未了のままである。

## 研究者判断（すべて確定・2026-07-24）
- ~~Alternative A / B / C~~ → **C（分離）採択**。
- ~~#2 IME off 日本語論述の β 扱い~~ → **再スコープ（β_writing_latin サブ baseline・collapse しない）採択**（上記「下位決定」）。
- ~~#3 Creative/VibeCoding の baseline~~ → **head 所有（Coding は β_coding 継承→自前再チューニング）＋ Creative は打鍵 β 無し**採択。

> 確定した #2/#3 は **抽出（2a）では現行挙動と一致するため影響せず**、実際に効くのは配線（2b）＝Coding head 追加時（Phase2）。
> 実装は Phase1 完了・凍結解除後（Migration 参照）。
