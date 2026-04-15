# Phase 1 Ground Truth 収集基盤 — design.md v1

> **注意**: 本 design は v1 たたき台。`requirement.md` の「運用メモ」に従い、この後 `/reimagine` で v2 を独立生成して v1 vs v2 比較 → 採用案決定を行う。**確定前に実装に入らない**。

## 実装アプローチ

### 設計原則
- **既存パターンに乗る**: `LogEntry` の手書きシリアライザ、手書き CLI パーサ、`#[tauri::command]` 登録など既存パターンをそのまま踏襲
- **analysis/ の純粋性維持**: engine への paused アクセスは既存の `Arc<AtomicBool>` 経由（Mutex 不要）
- **Phase 0 ゴールデン非破壊**: `tests/snapshots/minimal.json` の byte-equal を維持するため、既存 `LogEntry` バリアントの出力形式には手を入れない

### アーキテクチャ概略

```
Dashboard.tsx                     lib.rs (Main Thread)           Analysis Thread
 ┌──────────────┐                  ┌────────────────────┐         ┌───────────────────┐
 │ GT 3 択ボタン │                  │ record_user_label  │         │ loop_step::step() │
 │ 5 秒ホールド  │─ invoke ────────►│  → log_tx.send()   │         │  check paused     │
 │  (useRef +    │                  │                    │         │  pending_stuck_ts │
 │   setTimeout) │─ invoke ────────►│ set_engine_paused  │────────►│  (Atomic)         │
 │               │                  │  → engine          │         │                   │
 │  toast 表示   │◄─ emit ─────────│    .set_paused()    │         │  p_flow > 0.5 で  │
 └──────────────┘                  └────────────────────┘         │  recovered_at 補完 │
                                                                   └───────────────────┘
                                                                           │
                                                                   Logger Thread
                                                                   NDJSON: {"type":"user_label", ...}
```

## 変更対象

### 修正するファイル

- `src-tauri/src/logger.rs`
  - L11-48 `LogEntry` enum に `UserLabel { timestamp: u64, label: String, recovered_at: Option<u64> }` を `End` の直前に追加
  - L104-180 `match entry` ブロックに `writeln!` アーム追加（手書きシリアライザ）
  - 出力: `{"type":"user_label","t":<u64>,"label":"<flow|incubation|stuck>","recovered_at":<u64|null>}`
  - 末尾に `#[cfg(test)]` モジュール新設（T1-1）

- `src-tauri/src/analysis/loop_step.rs`
  - L205-218 `was_paused` フラグの同期強化: `step()` 冒頭で `engine.get_paused()` を毎回参照、Tauri コマンド経由の pause 解除後にも `extractor.reset()` が走るように修正
  - **HIGH リスク対策**（impact-analyzer 指摘）

- `src-tauri/src/lib.rs`
  - L694-709 `invoke_handler!` に `record_user_label` / `set_engine_paused` を登録
  - L495-575 分析スレッド本体: `pending_stuck_ts: Arc<AtomicU64>` を参照して `out.feat.p_flow > 0.5` 検出時に `LogEntry::UserLabel { ..., recovered_at: Some(now) }` を追送
  - `AppState` 相当の構造体に `pending_stuck_ts: Arc<AtomicU64>` を追加（0 = None, >0 = timestamp）

- `src-tauri/src/bin/replay.rs`
  - L51-94 `ReplayEvent` enum に `UserLabel` バリアント追加
  - L106-150 `Args` に `metrics: bool` 追加、手書きパーサに `--metrics` フラグ
  - L152-213 `main()` に metrics 分岐。`--metrics` と `--snapshot` は排他

- `src/components/Dashboard.tsx`
  - L130-139 を参考に Flow / Incubation / Stuck 3 ボタン追加
  - `useRef<number | null>` + `setTimeout(5000)` で 5 秒ホールド機構を新規実装
  - `onMouseDown` で `set_engine_paused(true)`、5 秒経過時のみ `record_user_label` + `set_engine_paused(false)`
  - `onMouseUp` / `onMouseLeave` で早期解除（clearTimeout + `set_engine_paused(false)`）
  - トースト表示（既存ライブラリ有無を実装時確認）

### 新規作成するファイル

- `src-tauri/src/analysis/metrics.rs`
  - 純粋計算モジュール（analysis/ の純粋性に適合）
  - 入力: `Vec<ReplayEvent>` + `Vec<FeatSnapshot>`
  - 出力: 混同行列 / precision / recall / F1 / リード/ラグ中央値 / Stuck 回復時間中央値
  - `#[cfg(test)]` で合成ケースをカバー（T1-5）

- `.steering/20260415-phase1-ground-truth/baseline_metrics.md`（雛形）
  - ベースライン precision/recall 記録用

### 削除するファイル

なし

## 影響範囲

| 影響先 | レベル | 根拠 | 対処 |
|---|---|---|---|
| `tests/snapshots/minimal.json` | LOW | 手書きシリアライザのため既存バリアント出力不変 | T1-4 で回帰確認 |
| 既存 `LogEntry` 使用箇所 | LOW | 新バリアント追加のみ。`match` 網羅のコンパイラチェックで漏れ検知 | — |
| `engine.rs` 9 本のスナップショットテスト | NONE | engine 自体に変更なし | — |
| Hook Thread バッファ滞留 | HIGH | pause 中に 512 件蓄積リスク | `was_paused` 同期で `extractor.reset()` を確実発火 |
| Phase 0 以前の NDJSON への `--metrics` 実行 | MEDIUM | UserLabel 欠落時のゼロ除算リスク | 警告 + 空集計、panic させない |

## 既存パターンとの整合性

- **LogEntry 追加**: `ImeState { timestamp, on, active }` バリアント（L39-43 / L155-165）が最も近い形式
- **Tauri コマンド追加**: `get_session_file(log: State<...>)` (L297) / `start_session` (L307) パターン
- **Dashboard invoke**: L130-139 の `invoke<string>("open_accessibility_settings")` パターン
- **CLI パーサ拡張**: L117-138 の `--snapshot` 手書きパーサ流用
- **`--snapshot` 排他**: Args 構造体に `metrics: bool` 追加 + `main()` 冒頭で排他チェック

## テスト戦略

| ID | 種別 | 内容 | 実装場所 |
|---|---|---|---|
| T1-1 | Unit | `LogEntry::UserLabel` serialize（flow/inc/stuck × recovered_at None/Some、計 6） | logger.rs `#[cfg(test)]` |
| T1-2 | Manual | 5 秒ホールド中 HMM pause の実機確認（NDJSON 目視） | 手順書 |
| T1-3 | Manual | Stuck ラベル → Flow 復帰で `recovered_at` が埋まる | 手順書 |
| T1-4 | Regression | `tests/snapshots/minimal.json` byte-equal 維持 | 既存 gse-replay 再実行 |
| T1-5 | Unit | `--metrics` の混同行列 / F1 / 中央値（合成 ReplayEvent 列） | analysis/metrics.rs `#[cfg(test)]` |
| T1-6 | Unit | Tauri pause 経由での `was_paused` 同期 + `extractor.reset()` | loop_step.rs `#[cfg(test)]` |

## ロールバック計画

- **logger.rs の新バリアント**: 削除してコンパイルが通る構造。ロールバック時は 1 commit revert で完結
- **Tauri コマンド 2 本**: `invoke_handler!` から外せば無効化可能
- **Dashboard UI**: 新規ボタンのため非表示にすれば既存機能への影響ゼロ
- **分析スレッド `pending_stuck_ts`**: `AtomicU64` 読み取りのみ追加。Atomic が 0 なら既存挙動を維持するガード設計
- **loop_step.rs の `was_paused` 強化**: 変更前は Tauri 経由 pause に対応していなかったので、ロールバックすると元の誤検知リスクが復活。完全ロールバックではなく改修版の退行テストを残すべき

## Open 設計判断（/reimagine で再検討対象）

### ⚠️ 最重要: pause 中バッファ滞留問題（HIGH リスク #2）

**課題**: Tauri コマンド経由で `engine.set_paused(true)` を呼んでも、pause 判定が効くのは 1Hz gate の extract/update 段のみ。その手前の `extractor.push()` と crossbeam channel (`log_rx`) は動き続けるため、5 秒ホールド中のキーストロークが 30 秒ローリングウィンドウに残留する。解除直後の特徴量計算で **pause 中に溜まったイベントがバースト扱い** され、誤 Stuck 判定が出る可能性がある。既存の `was_paused` フラグは 1Hz gate skip 時にしか立たないため、Tauri 経由 pause では `extractor.reset()` が走らない。

**改善案 4 つ**:

| 案 | 内容 | 長所 | 短所 |
|---|---|---|---|
| A | Hook 側で `IS_PAUSED: AtomicBool` を見て送信スキップ | バッファ 0 | pause 中のキーストローク数自体が記録されない |
| B | Analysis Thread の recv 段で `try_recv` 全 drain + `was_paused = true` | バッファ清掃確実、既存機構活用 | channel 枠一時占有（5 秒 × 10 keys/s ≒ 50 件で実害なし） |
| C | `step()` 冒頭で `prev_paused` と比較、edge で `extractor.reset()` | 1 箇所完結、テスタブル | channel 滞留は残る（長時間 pause で危険） |
| D | `engine.push_event()` 経由に統一、内部で paused 時弾く | 根本的に綺麗 | 既存 API 変更大、analysis/ を跨ぐリファクタ |

**v1 推奨: B + C 併用**
- B で recv 段で drain（Hook からの流入を止める）
- C で `step()` 冒頭の edge 検出で `extractor.reset()`（1Hz gate 外からの pause にも対応）
- 3 段ガード（Hook → channel → recv drain → step() reset edge）で冗長性確保

**テスト強化（T1-6 拡張）**: Tauri pause 中に Hook 相当 InputEvent を 100 件送っても、解除後の最初の step() で extractor 内容がゼロかつ HMM 状態が前回値を引き継がないことを検証。

**/reimagine で問うこと**: v2 が別方式（例: Monk Mode 的な「論理 pause」と「物理 pause」の分離、engine の pause 責務を loop_step へ移譲、等）を提案するかどうか。4 案すべて未確定として v2 を走らせる。

---

### その他の Open 設計判断

1. **GT 付与 UX**: 5 秒ホールド vs トグルボタン vs キーボードショートカット vs 押下→確認ダイアログ
2. **IPC 分離/統合**: `record_user_label` + `set_engine_paused` 分離 vs 単一 `record_user_label_with_pause` 統合
3. **pending_stuck_ts 管理方式**: `Arc<AtomicU64>` グローバル vs 分析スレッドへチャネル転送 vs Replay 側後処理
4. **メトリクス算出場所**: Rust 内蔵 vs 外部 Python（sklearn）vs 両対応
5. **clap 導入**: 手書きパーサ継続 vs clap 導入
6. **metrics モジュール配置**: `src-tauri/src/analysis/metrics.rs` vs `src-tauri/src/bin/metrics.rs`
7. **トースト UI**: 既存ライブラリ利用 vs 自作（未調査）

## Phase 1 受け入れ条件との対応

- GT 付きセッション収集 → UI + ログ基盤を提供（収集自体は運用）
- `gse-replay --metrics` 出力 → §変更対象で実装
- baseline_metrics.md 記録 → 新規作成
- 5 秒ホールド HMM pause 実機確認 → T1-2
- Phase 0 ゴールデン byte-equal → T1-4
- `cargo test` 全 PASS → T1-1/T1-5/T1-6 追加後に確認
- code-reviewer / security-checker HIGH 対応 → レビュー後
