# 設計 — Task B backend プローブ scheduler

## 実装アプローチ

### レイヤー分離(architecture-rules 厳守)
- **純粋ロジック** → `src-tauri/src/analysis/probe_scheduler.rs`(新規)。OS API / Tauri / 時刻取得 /
  グローバル RNG を一切呼ばない。`now_ms` / `idle_ms` は引数で受け、RNG は seed 注入(`StdRng`)。
  指数間隔サンプリング・gap/cap/away thinning・時間隔離窓計算・不透明 `ProbeId` 生成を担う。
- **OS/Tauri 配線** → `lib.rs`。専用ポーリングスレッド起動・`probe_triggered` emit・
  `ProbeAssignment` 送信・自己マーカー hotkey・`session_start_ms` 共有を担う。

### スケジューラ駆動 = 専用ポーリングスレッド(技術的確定事項)
1Hz Analysis Thread はレイテンシ要件があり **`AppHandle` を持たない**(emit 不可)。
プローブ駆動は emit と logger 送信の両方が要るため、IME Polling
(`input/ime_windows.rs:205 spawn_ime_open_polling_thread`)と同型の専用スレッドを
`setup()` で spawn する。`crossbeam_channel::Receiver<()>` を wake/shutdown 兼用にし、
`recv_timeout(1000ms)` でポーリング。sender drop で `Disconnected` → 自然終了。
→ 1Hz 推論ループには触れない(分離維持)。

### probe_id = 内部生成 newtype(security-checker 申し送り厳守)
`ProbeId(String)` newtype を probe_scheduler 内に閉じ、**唯一のコンストラクタは
seeded RNG から `[A-Za-z0-9_-]` 16文字を生成**する `ProbeId::generate(&mut rng)`。
外部 `String` を受け取る経路を作らない → 本文/タイトル由来 ID の混入を型で排除。
`uuid` crate は追加しない(seeded RNG で決定論テスト可能にするため・base64url 風アルファベット)。

---

## 設計判断 A(/reimagine 相当の2案比較)— スケジューリング方式

### 案 A1(推奨): 同次 Poisson(指数間隔)+ rolling thinning
- セッション開始時 `next = now + Exp(λ)`。poll で `now ≥ next` の候補到来時に制約判定:
  away(idle≥180s)/ gap(<8分)/ cap(直近30分で2件)のいずれか違反 → **棄却(thin)**して
  `next = now + Exp(λ)` を再抽選。全制約 OK → 発火・記録・再抽選。
- 指数間隔: 逆変換 `interval = -ln(1-u)/λ`(u=`rng.gen::<f64>()`, u→0 ガード)。rand_distr 不要。
- **長所**: 同次 Poisson は「count 条件付きで時刻が一様」= **一様ランダムの教科書的生成法**。
  `probe_assignment.scheduled_ts` の実現分布で一様性を**監査証明しやすい**(D-14 の核心要件)。
  オンライン/無限長セッション対応。idle 除外が「離席中は候補を棄却し再抽選」で自然に表現できる。
- **短所**: thinning が制約境界付近で厳密 Poisson をわずかに歪める(監査は scheduled ログで追える)。

### 案 A2: 30分窓ごとに一様2点を事前抽選し gap で棄却
- **長所**: 「窓内に一様2点」と述べやすく cap=2 が厳密。
- **短所**: (a) 固定窓境界で comb 構造(一様性が窓内ローカル止まり、全体では非一様)。
  (b) 窓跨ぎの gap 違反処理が要る。(c) idle 除外を**絶対時刻の事前抽選**へ組込むのが困難
  (離席で再抽選するとモデル非依存性の監査が濁る)。

### 採用案: **A1**(handoff の "rolling thinning / Poisson 指数間隔" 明示とも一致)
監査可能性(一様性の証明しやすさ)と idle 除外の自然さで A1 が優位。

---

## 設計判断 B — B↔C イベント契約

**B が分析窓を確定し emit に含める / C は受領して `realtime_label` へ転記**(handoff base 採用)。
v0.3 §14 の `realtime_label` は `analysis_window_start_ms/end_ms` を持ち、Task A の
`realtime_label_answered` も窓を引数に取る。よって窓確定を B に集約するのが schema と整合。

- emit payload:
  ```jsonc
  app.emit("probe_triggered", {
    "probe_id": "<opaque>" | null,        // self_marker は null
    "source": "random_probe" | "self_marker",
    "analysis_window_start_ms": <u64>,    // random: t−31000 / self: t−35000
    "analysis_window_end_ms":   <u64>     // random: t−1000  / self: t−5000
  })
  ```
- 窓計算(probe_scheduler の純関数):
  - random_probe: `[t−31_000, t−1_000]`(v0.3 §4.2)
  - self_marker:  `[t−35_000, t−5_000]`(v0.3 §4.2)

---

## 変更対象

### 新規作成
- `src-tauri/src/analysis/probe_scheduler.rs` — 純粋スケジューラ(RNG seed 注入)・窓計算・`ProbeId`。

### 修正
- `src-tauri/src/analysis/mod.rs` — `pub mod probe_scheduler;` 追加(metrics の後)。
- `src-tauri/Cargo.toml` — `rand = "0.8"` 追加(lock に 0.8.5 既存・新規 DL なし)。
- `src-tauri/src/lib.rs`:
  - `static SESSION_START_MS: AtomicU64`(or Arc<AtomicU64>)追加 + `start_session` で store。
  - `setup()`: 専用プローブスレッド spawn(AppHandle clone + logger tx + shutdown rx)。
  - スレッド本体: `recv_timeout(1000ms)` ループ → `scheduler.poll(now_ms, idle_ms)` →
    Some 時 `LogEntry::ProbeAssignment` 送信 + `probe_triggered` emit。
  - 自己マーカー hotkey: `Code::KeyM`(Ctrl+Shift+Alt+M)を shortcuts 配列へ追加 +
    handler に分岐(`LAST_MARKER_MS` と同型の debounce 用 static)→ self_marker emit。

### 削除
- なし。

## 影響範囲
- 既存 1Hz Analysis / Logger / IME スレッドには非干渉(新スレッド追加のみ)。
- logger は Task A で `ProbeAssignment` を既にハンドル済(`logger.rs:780`)→ schema 変更なし。
  → **`schema_dto.rs` / `current.json` は touch しない**(finish-task の parity guard に当たらない想定)。
- global-shortcut 配列に 1 キー追加 → 既存 F/I/S/R ハンドラへの影響なし(分岐追加のみ)。

## 既存パターンとの整合性
- スレッド: `input/ime_windows.rs:205` の `recv_timeout` + shutdown パターンに準拠。
- hotkey debounce: `lib.rs:25-33` の `LAST_MARKER_MS` / `MARKER_DEBOUNCE_MS` パターンに準拠。
- emit: `lib.rs:462` の `app.emit(name, serde_json::json!({...}))` パターンに準拠。
- idle: `input::hook::last_key_ms()` + `AWAY_IDLE_MS`(180_000)を再利用(新規 idle 検出を作らない)。
  ※ `AWAY_IDLE_MS` は intervention.rs private const → probe_scheduler は閾値を引数/定数で受け、
    駆動側が idle_ms を渡す(モジュール越え private 参照を避ける)。

## テスト戦略
- **単体(probe_scheduler, seeded・決定論)**:
  - gap: 連続発火間隔が常に ≥8分。
  - cap: 任意の 30 分窓で発火 ≤2 件。
  - away: idle≥180s の候補は棄却され発火しない。
  - 窓計算: random=[t−31000,t−1000] / self=[t−35000,t−5000]。
  - `ProbeId::generate` 出力が `[A-Za-z0-9_-]` のみ・長さ固定・同一 seed で再現。
- **統合**: スレッド駆動は薄い配線のため、scheduler 純ロジックの単体で主要保証。
  emit/送信は手動スモーク(自己ドッグフード=Task E)で確認。
- 既存テスト不変。`cargo test` / `clippy`(新規警告ゼロ)/ `npm run build` 緑。

## ロールバック計画
- 新スレッド spawn の1行と hotkey 1分岐、`pub mod` 1行、Cargo.toml 1行を revert すれば
  既存挙動へ完全復帰(新規ファイル削除のみで副作用なし)。
