# 設計 v2 — ブロック遷移を「1 本の直列化点」にする

> ★ `requirement.md` だけに立脚して再生成した案。v1 との比較は `design-comparison.md`。

## ★ まず不変条件を言葉にする (★ ここを飛ばすと手段の議論になる)

守りたいのは値ではなく**順序**である:

> ⚠️★★★ **`BlockEnd` は、次のブロックの `Rotate` より前にログ channel へ入る。**
> ★ そして「終わったブロック」と「始まったブロック」は**必ず別のファイル**になる。

★ この不変条件が破れると `protocol.md §1`「1 ブロック = 1 ファイル」が壊れる ——
⚠️ **G1 リブートの原因そのもの (P010 block07) と同じ失敗クラス**である。

⚠️ ここから 2 つのことが従う:

1. ★ **原子変数の比較だけでは足りない。** 「A が B より前」は 2 操作間の順序であり、
   1 語の CAS では表現できない。⚠️ しかも `start_session` は
   `Rotate` を**ログのロックの中**で送り、`SESSION_START_MS` を**ロックを抜けた後**で
   書く (`lib.rs:2193`) ので、★ **「`Rotate` は送られたが `SESSION_START_MS` はまだ 0」
   という窓が実在する**。
2. ★ **どちらが勝ったかを、勝った側が判定できる必要がある。** 排他だけでは
   「先に入った自動終了が、既に交代済みのブロックを閉じる」を防げない。

→ ★ **排他 (順序を作る) ＋ エポック照合 (勝敗を判定する) の 2 つが要る。**

## 実装アプローチ

### ① ブロック遷移の直列化点 — `BLOCK_TRANSITION` (`lib.rs`)

```rust
/// ⚠️★★★ **ブロック遷移の直列化点**。「開始する」の押下と自動終了は
/// この 1 本を通る。★ 守るのは値ではなく**順序**である。
static BLOCK_TRANSITION: Mutex<()> = Mutex::new(());
```

- **`start_session`**: 関数の入口で取り、`SESSION_START_MS.store(now)` の**直後に離す**。
  ★ `Rotate` / `SessionStart` の送信と `SESSION_START_MS` の更新が**ひと続き**になる
  ＝ v1 が閉じられなかった窓が消える。
  ⚠️ オーバーレイの `win.show()` は**外に出す** (ウィンドウ操作をロック中に行わない
  —— `latest_feat` のロックで既に同じ判断をしている・follow-up F-2)。
- **自動終了スレッド**: 1)〜4) (`session_active=false` → `SESSION_START_MS=0` →
  アイドル待ち → `BlockEnd` 送信) を**まるごと**この中で行う。
  ⚠️ `emit` / `spawn_reconcile` は**外に出す** (ブロックとブロックの間の処理であり、
  排他は要らない)。

#### ⚠️★★ ロック順序 (★ 反転させない)

```
BLOCK_TRANSITION  →  latest_feat  →  intervention  →  log
```

★ `BLOCK_TRANSITION` を**最も外側**に置く。⚠️ 自動終了スレッドは `log` の
`Mutex` を**取らない** (自分の `Sender` clone を持っている) ので、
★ **循環はそもそも作れない**。

⚠️ 待ちは最大 1500 ms (アイドル待ち) だが、これは**ブロックの境界**でしか起きない。
★ しかもその 1500 ms は「押下を待たせている」のではなく
「**押下が壊れないように待たせている**」時間である。

### ② 勝敗の判定を純関数へ — `g1::decide_block_end`

`decide_start_action` と同じ流儀 (判定は `g1.rs`、効果は `lib.rs`):

```rust
pub enum BlockEndAction {
    NotStarted,   // SESSION_START_MS == 0
    KeepRunning,  // まだ 5 分に達していない
    EndBlock,     // 閉じてよい
    Superseded,   // ⚠️★★★ 観測した時点と別のブロックになった → 中止
}

pub fn decide_block_end(
    observed_start_ms: u64,  // ポーリング時に観測した開始時刻
    current_start_ms: u64,   // ★ **排他を取った後**の開始時刻
    now_ms: u64,
    limit_ms: u64,
) -> BlockEndAction
```

呼び出しは 2 回:

| いつ | 引数 | 何を判定するか |
|---|---|---|
| ポーリング (排他の外) | `(start, start, now, LIMIT)` | 未開始 / 未到達 / 到達 |
| ⚠️★ **排他を取った直後** | `(start, SESSION_START_MS.load(), now, LIMIT)` | ★ **交代されていないか** |

→ ★ **「押下が先」は `Superseded` として中止**され、始まったばかりのブロックは無傷。
→ ★ **「押下が後」は排他で `BlockEnd` の後ろに回る**ので、`Rotate` は必ず後。

### ③ 事後レビュー所見 C — 純関数 2 つ (`liveness.rs`)

> ⚠️★★★ **初版は効いていなかった**（code-reviewer HIGH）。経緯は `decisions.md` R-3。

```rust
/// ① そのティックのエピソード判定を抑止する。
pub fn starved_ms_carried_into_new_window(new_block_epoch: bool, prev_starved_ms: u64) -> u64;

/// ② ⚠️★★★ **累積そのものを 0 に戻す。** これが無いと 1 tick ずれて同じ誤帰属が起きる
///    —— `RotateForRestart` は**マウス押下**なので、エポックの tick では
///    `starved_ms` は 0 ではなく増え続けているためである。
pub fn reset_starvation_at_new_block(new_block_epoch: bool, starv: Starvation) -> Starvation;
```

★ ② は**通常のブロック境界で `session_active = false` により起きていることと同じ**であり、
⚠️ 再押下経路だけがその例外だったのを揃えるだけである。

⚠️★★★ **`peak_starved_ms` は戻さない。** 戻すと復帰行の `starved_ms` が 0 になり、
★ 「**何秒落ちていたか**」という測った量が消える（⚠️ 誤帰属ではなく**嘘**になる）。

⚠️★ **`MicroStarveWindow::tick` の引数は増やさない。** 増やすと既存テスト 10 本以上の
呼び出しを書き換えることになり、★ 研究者決定「**1 行で終わる範囲に限る**」を超える。

## 変更対象

### 修正するファイル
- `src-tauri/src/g1.rs` — `BlockEndAction` / `decide_block_end` を追加 (＋テスト)
- `src-tauri/src/lib.rs` — `BLOCK_TRANSITION` の導入、`start_session` と
  自動終了スレッドの臨界区間化、所見 C の 1 行差し替え
- `src-tauri/src/input/liveness.rs` — `starved_ms_carried_into_new_window` (＋テスト)

### 新規作成するファイル
- なし (★ モジュールを増やさない)

## 影響範囲

| 触るもの | 影響 | 対処 |
|---|---|---|
| `start_session` (通常運用でも通る) | ⚠️ ロックを 1 つ増やす | ★ **非 G1 では他に取る者がいない** (自動終了スレッドは `if g1_mode().is_some()` の中でしか spawn されない) → **無競合**。観測可能な挙動は変わらない |
| `SESSION_START_MS` の書き込み順 | ★ 変えない (`session_active=false` → 0 化 の順は従来どおり) | ★ 「`session_end` の後ろに feat/key を出さない」要件は従来どおり満たす |
| 記録仕様 (行の形) | ★ **変えない** | → `emit_schema` の diff は空。schema parity は据え置きで通る |
| `HMM_VERSION` | ★ **変えない** (0.4.0 据え置き) | → ゴールデン 6 本 byte-equal |
| ⚠️★ **通常運用の `starve_window`** | ⚠️ **1 か所だけ変わる** (下記) | ★ 明示して受け入れる |

### ⚠️★★★ 正直に書く — 「通常運用を 1 バイトも変えない」の**唯一の例外**

★ 所見 C の修正 (`starved_ms_carried_into_new_window`) は **モードで分岐しない**。
→ ⚠️ **通常運用でも**「セッション実行中に『開始する』を押した」tick で、
`starve_window` のエピソードが **1 本数えられなくなる**。

⚠️ **なぜモードで分岐させないか**:

1. ★ 誤帰属は**通常運用でも同じく誤り**である。片方だけ直すと
   ⚠️ **同じ行が読み手のモード知識に依存して意味を変える** ——
   ADR-013 が潰そうとした取り違えの新種を作る。
2. ⚠️ `liveness.rs` に G1 の知識を持ち込むことになる
   (`architecture-rules`: 判定はモード非依存の純関数に閉じる)。

★ **影響の大きさ**: 変わるのは `starve_window` の `n_lt30` が**最大 1 本**。
⚠️ 当該行は `threshold_gated` で、支えているのは ADR-012 Stage 0 の**形成的な投資判断**
であって確証の判定基準ではない。★ しかも Phase1 コホート (63 ファイル) には
**`starve_window` 行が 1 行も無い** (計器の追加は収集の 16 日後) ので、
⚠️ **既存データの解釈は 1 文字も変わらない**。

### ⚠️★ 待ち時間とデッドロックの検算

★ 自動終了が `BLOCK_TRANSITION` を持つ最長時間 = **アイドル待ち ≤ 1500 ms** ＋
`try_recv` のドレイン ＋ `try_send` 1 回。⚠️ `emit` / `recv_timeout(5s)` /
自動提出は**すべてロックの外**に出してある。

→ ★ 「開始する」の押下が待たされるのは **≤ 約 1.5 秒**、しかも**ブロック境界だけ**。

⚠️ **デッドロックしない検算**: 排他を持っている間に自動終了スレッドが行うのは
**アトミック操作と channel 操作だけ**で、★ `log` の `Mutex` も**メインスレッドも要求しない**。
→ `start_session` (同期コマンド) がメインスレッドで待っても、
⚠️ **待ち先が進むのに押下側を必要としない** ＝ 循環が無い。

## 既存パターンとの整合性

- ★ `g1.rs` = 判定 (純関数) / `lib.rs` = 効果、という既存の分担にそのまま乗る
  (`decide_start_action` が先例)。
- ★ `Mutex` の poison は `unwrap_or_else(|p| p.into_inner())` で扱う (repo 全体の流儀)。
- ★ `liveness.rs` は「OS 差を持ち込まない純関数」の方針を維持する。

## テスト戦略

### 単体 (両 OS 共通・`#[cfg(test)] mod tests`)

⚠️★★ **OS ゲート付きモジュールの中に書かない** (B-1 で実際に踏んだ)。
★ 実行後に**テスト総数が増えたことを必ず確認する**。

| テスト | 何を固定するか |
|---|---|
| `block_end_is_aborted_when_a_new_block_started` | ⚠️ **押下が先**: `observed != current` → `Superseded` |
| `block_end_proceeds_for_the_same_block` | ★ 同じブロックなら `EndBlock` |
| `block_end_waits_until_the_limit` | 5 分未満は `KeepRunning` |
| `block_end_ignores_an_unstarted_block` | `0` は `NotStarted` |
| `restart_epoch_does_not_carry_starvation_into_the_new_window` | ★ 所見 C: 再押下の tick でエピソードを数えない |
| `a_normal_tick_still_counts_its_episode` | ⚠️ **対照**: 通常の tick では従来どおり数える |
| `normal_block_boundary_is_unaffected_by_the_fix` | ⚠️ **対照**: 通常のブロック境界 (`session_active=false`) の挙動は不変 |
| `block_transition_lock_is_taken_before_the_log_lock` | ★ ソース走査でロック順序を固定 (⚠️ バイト数スライスしない) |

### 回帰

- `cargo test --workspace` (★ `cd src-tauri` してから)
- ゴールデン 6 本 byte-equal (`gse-replay --snapshot`)
- `emit_schema` の diff が空 → schema parity 据え置き

### ⚠️ E2E

★ **不要**。交錯はスレッドのタイミング依存で E2E では再現性が無い。
→ ⚠️ **だからこそ純関数へ切り出して決定的にテストする**のが本設計の主眼である。

## ロールバック計画

`git revert` 1 コミット。★ 状態も記録仕様も持たない変更なので、
戻しても既存ログの解釈は一切変わらない。
