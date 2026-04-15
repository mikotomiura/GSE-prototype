# Phase 1 Ground Truth 収集基盤 — design.md v2

> 本 design は `/reimagine` で requirement.md のみを参照して v1 を意図的に破棄し、ゼロから再生成した案。v1 の「5 秒ホールド + pause + AtomicU64 + Rust 内蔵 metrics」は一切前提にしない。

## 設計哲学

**最小汚染・オフライン計算・単一責務**: GT 付与行為そのものがキーストロークデータを汚染しないことを最優先する。HMM を一時停止して汚染を回避するのではなく、**汚染源を最初から発生させない**設計にする。副次的に HIGH リスク #2（pause 中バッファ滞留）は発生源から消滅する。

`recovered_at` のような派生情報はログ記録時点では計算せず、`gse-replay` の metrics 計算時に**純粋関数として後付けで算出**する。production path をシンプルに保ち、閾値変更時の再計算を自由にする。

## 実装アプローチ

### アーキテクチャ

```
[OS 全域ホットキー]
  Cmd+Shift+Option+F/I/S
        │
        ▼
 tauri-plugin-global-shortcut ─invoke─► record_user_label(label)
                                               │
                                               │ server-side timestamp
                                               │ label validation
                                               ▼
                                          log_tx ─► Logger
                                               │
                                               ▼
                                  NDJSON: {"type":"user_label","t":<u64>,"label":"<x>"}

                        ※ engine.pause() は呼ばない・追加しない
                        ※ 分析スレッドと Hook は完全に素通り
```

### GT 付与 UX: **OS グローバルホットキー**（マウス不要・pause 不要）

- デフォルト: `Cmd+Shift+Option+F` / `I` / `S`（3 モディファイアでユーザーの IDE ショートカットと衝突しにくい）
- 2 秒デバウンス（誤打鍵防止）
- Dashboard は**読み取り専用の counter widget** のみ表示: `Flow:3 / Inc:1 / Stuck:2 | shortcut: ⌘⇧⌥ F/I/S`
- 1 ラベル = 1 ホットキー押下（所要 ~1 秒、認知負荷最小）
- **マウスを動かさない** → プログラミング中のフロー・思考を分断しない

**なぜ 5 秒ホールドではないのか**: 5 秒ホールドは「ボタンを押し続ける」という明示的な意識的動作を要求し、Flow 状態のラベル付与そのものが Flow を壊す。また 5 秒間の pause が必要になり HIGH リスクを抱える。ホットキーは打鍵習慣の延長で発火でき、pause 不要で汚染源が生まれない。

### Stuck 回復時間: **オフライン純粋関数で後付け計算**

- `LogEntry::UserLabel` の `recovered_at` は常に `None` で記録
- `gse-replay --metrics` 実行時に以下を計算:
  - 各 Stuck ラベルに対し、そのタイムスタンプ以降の FeatSnapshot ストリームを走査
  - `p_flow > 0.5` を満たす最初のスナップショットの時刻を `recovered_at` として算出
  - 窓幅（例: 15 分）超過時は `None`（回復せず）
- メリット:
  - production path に `Arc<AtomicU64>` / 分析スレッド追加ロジック不要
  - pure function でユニットテストしやすい
  - 閾値（`p_flow > 0.5`）を変えて再計算できる（Phase 2a 以降のアルゴ改善で再利用）
  - 複数 Stuck 連続時のハンドリングが宣言的に書ける

### メトリクス surface: **Rust 内蔵 + JSON 出力 + オプショナル Python**

- `gse-replay --metrics <session.ndjson>` 人間可読の pretty-print（混同行列 + F1 + 中央値）
- `gse-replay --metrics --json <session.ndjson>` 構造化 JSON（スクリプト連携用）
- `ml/analyze.py`（新規、薄いラッパー）: JSON を stdin で受け取り、複数セッション集計・ROC 曲線・時系列可視化を matplotlib で出力
  - sklearn / pandas は使えるなら使う、無理なら標準ライブラリだけで動かす（チーム環境への影響を抑える）
- 利点: Rust 側は「素早い単一セッション検証」、Python 側は「深い探索的分析」の棲み分け

### IPC: **単一コマンド + サーバー側タイムスタンプ**

```rust
#[tauri::command]
fn record_user_label(
    label: String,  // "flow" | "incubation" | "stuck" のみ許可
    log: State<'_, Arc<Mutex<LogState>>>,
) -> Result<(), String> {
    let label_enum = UserLabelKind::parse(&label)?;
    let timestamp = now_ms();  // サーバー側で付与、クライアント時計drift排除
    log.lock().unwrap_or_else(|p| p.into_inner())
       .tx.try_send(LogEntry::UserLabel { timestamp, label: label_enum, recovered_at: None })
       .map_err(|e| e.to_string())
}
```

**`set_engine_paused` は追加しない**。pause 機能が将来必要になった時に別タスクで正面から設計する（Monk Mode 等）。本タスクは GT 収集に必要な最小限に絞る。

### pause 不在で大丈夫か（HIGH リスク #2 の解消根拠）

- ホットキー発火は 1-3 キーイベント（修飾キー + 本キー）程度
- 30 秒ローリングウィンドウには通常 200-300 キーイベントが入っている
- 追加 3 イベントの影響は F1 count / F3 median / F4 burst などのどの特徴量でも統計誤差レベル
- 2 秒デバウンスでラベル多重発火を防止 → バースト汚染も発生しない
- **結論: pause 機構そのものを導入しないことが最善の HIGH リスク対策**

## 変更対象

### 修正するファイル

- `src-tauri/src/logger.rs`
  - `LogEntry` enum に `UserLabel { timestamp: u64, label: UserLabelKind, recovered_at: Option<u64> }` を追加
  - `UserLabelKind` enum（`Flow` / `Incubation` / `Stuck`）を同ファイルに定義
  - NDJSON 手書きシリアライザに `UserLabel` アーム追加（出力: `{"type":"user_label","t":...,"label":"flow","recovered_at":null}`）
  - `#[cfg(test)]` で UserLabel serialize テスト追加

- `src-tauri/src/lib.rs`
  - Tauri コマンド `record_user_label` を 1 本追加（上記コード）
  - `invoke_handler!` に登録
  - `tauri-plugin-global-shortcut` を初期化、`Cmd+Shift+Option+F/I/S` に `record_user_label` を bind
  - デバウンス（2 秒）は lib.rs 内の `AtomicU64 LAST_LABEL_MS` で実装、shortcut ハンドラ冒頭で判定

- `src-tauri/Cargo.toml`
  - `tauri-plugin-global-shortcut = "2"` 追加

- `src-tauri/tauri.conf.json` / capabilities
  - global-shortcut のパーミッション許可

- `src-tauri/src/bin/replay.rs`
  - `--metrics` フラグと `--json` フラグを手書きパーサに追加（`--snapshot` と排他、両指定は Usage エラー）
  - `ReplayEvent::UserLabel` バリアント追加（既存手書きパーサに分岐追加）
  - `--metrics` 実行時は `analysis::metrics::compute_session_metrics()` を呼ぶ

- `src/components/Dashboard.tsx`
  - ラベル counter widget（読み取り専用 3 数値 + ショートカット hint）を追加
  - counter は `listen("user_label_recorded", ...)` で `record_user_label` の発火を購読してローカル state 更新
  - **ボタンは追加しない**。5 秒ホールド機構も不要

### 新規作成するファイル

- `src-tauri/src/analysis/metrics.rs`
  - 純粋関数 `compute_session_metrics(events: &[ReplayEvent], feats: &[FeatSnapshot]) -> SessionMetrics`
  - 内部で `compute_recovered_at` を呼び Stuck ラベルの後追い補完
  - 混同行列 / precision / recall / F1 / 検出リード・ラグ中央値 / Stuck 回復時間中央値
  - `SessionMetrics` 構造体に `serde::Serialize` 付与（JSON 出力用）
  - ユニットテスト豊富（合成 ReplayEvent 列で境界値カバー）

- `src-tauri/src/analysis/user_label.rs`（任意、logger.rs に同居でも可）
  - `UserLabelKind` enum 定義

- `ml/analyze.py`（オプショナル）
  - stdin から `--metrics --json` の出力を受け取り、複数セッション集計レポートを出す
  - `requirements.txt` は tiny（matplotlib or 標準ライブラリのみ）

- `.steering/20260415-phase1-ground-truth/baseline_metrics.md`（雛形）

### 削除するファイル

なし

## 既存パターンとの整合性

- **LogEntry 追加**: 既存の `ImeState` バリアントと同じ「手書きシリアライザに writeln! アーム追加」パターン
- **Tauri コマンド**: `get_session_file(log: State<...>)` と同じ `State<'_, Arc<Mutex<LogState>>>` 注入パターン
- **手書き CLI パーサ**: 既存 `--snapshot` パターン踏襲。ただし排他フラグが増えるため**この機会に `clap` 導入を検討**（別判断）
- **プラグイン導入**: Tauri 2.0 の capabilities システムに従う（v1 allowlist は使わない）

## 影響範囲

| 影響先 | レベル | 根拠 | 対処 |
|---|---|---|---|
| `tests/snapshots/minimal.json` | NONE | 手書きシリアライザで既存バリアント出力不変 | T1-4 で回帰確認 |
| 既存 `LogEntry` match 箇所 | LOW | 新バリアント追加のみ、コンパイラが網羅チェック | — |
| engine.rs / loop_step.rs | NONE | 一切触らない | — |
| Hook Thread バッファ | NONE | pause 機構を入れないので滞留なし | — |
| グローバルホットキーの他アプリ衝突 | MEDIUM | `Cmd+Shift+Option+F/I/S` はレアな 3 モディファイア組合せだが、可変にすべき | Dashboard から key combo を変更できる capability 扱いは将来対応。初期はハードコード |
| `tauri-plugin-global-shortcut` 導入 | LOW | 公式プラグイン v2 対応 | Cargo.toml と capabilities に 1 行ずつ追加 |

## テスト戦略

| ID | 種別 | 内容 | 実装場所 |
|---|---|---|---|
| T1-1 | Unit | `LogEntry::UserLabel` serialize（3 label × recovered_at None/Some、計 6） | logger.rs `#[cfg(test)]` |
| T1-2 | Unit | `compute_recovered_at` pure function（Stuck → Flow 遷移検出 / 15 分超過 / 連続 Stuck） | metrics.rs `#[cfg(test)]` |
| T1-3 | Unit | `compute_session_metrics` 混同行列 / F1 / 中央値（合成 ReplayEvent 列） | metrics.rs `#[cfg(test)]` |
| T1-4 | Regression | `tests/snapshots/minimal.json` byte-equal | 既存 gse-replay 再実行 |
| T1-5 | Unit | `record_user_label` コマンド（ラベルバリデーション / timestamp 付与 / デバウンス） | lib.rs `#[cfg(test)]` |
| T1-6 | Manual | ホットキー 5 発で 5 件のラベルが NDJSON に記録、中間の keystroke に差分なし | 手順書 |
| T1-7 | Manual | `--metrics` / `--metrics --json` 実行で期待出力 | 手順書 |

## ロールバック計画

- LogEntry バリアント: 1 commit revert で完結（手書きシリアライザのため副作用ゼロ）
- `record_user_label` コマンド: `invoke_handler!` から外せば無効化
- グローバルホットキー: plugin 初期化を削除すれば OS 登録も解除
- Dashboard counter widget: コメントアウトで無効化
- metrics.rs: 新規ファイルなので削除のみ

## Phase 1 受け入れ条件との対応

- ✅ GT 付きセッション ≥ 10 件: UI + ログ基盤を提供（収集は運用）
- ✅ `gse-replay --metrics`: §metrics.rs 新規で実装
- ✅ baseline_metrics.md 雛形: 新規作成
- ✅ 5 秒ホールド中の HMM pause 実機確認 → **要件解釈の変更**: 「ラベル発火中に HMM 状態が汚染されない」ことを代替検証（T1-6 の差分確認）
- ✅ Phase 0 ゴールデン byte-equal: T1-4
- ✅ `cargo test` 全 PASS: T1-1/T1-2/T1-3/T1-5 追加
- ✅ HIGH 指摘対応: pause 機構そのものを持たないので HIGH リスク #2 は発生しない

**⚠️ 注意**: requirement.md L39 の受け入れ条件「5 秒ホールド中の HMM pause が実機で目視確認済み」は v2 では該当する機構がない。採用時は requirement.md の更新（受け入れ条件を「ラベル記録中に HMM 入力汚染が生じないこと」に書き換え）が必要。

## v2 の主張

1. **5 秒ホールドは Flow を壊す**: マウス移動 + 5 秒間の意識的な「押し続け」はラベル付与行為が認知状態そのものを変える
2. **pause 機構は導入コストが高く HIGH リスクを生む**: Tauri 経由 pause と was_paused 連動、Hook 滞留、edge 検出、3 段ガード …… これら全てがホットキー設計では不要
3. **recovered_at は派生値であり記録時に確定させる理由がない**: 閾値変更時に再計算できないロックインになる
4. **メトリクスは Rust 単体では完結しにくい**: 複数セッション集計や ROC 曲線は Python の方が圧倒的に速い。単一セッションは Rust で即時、深掘りは Python の 2 層

## 設計判断の履歴

- 実行回数: 1 回目
- 採用: **v2（再生成案）**
- 根拠:
  1. 5 秒ホールドはラベル付与自体が Flow を壊す（測定器が対象を変質させる問題）
  2. HIGH リスク #2 を「軽減」ではなく「発生源ごと消滅」させる設計品質の高さ
  3. production path（loop_step.rs / engine.rs）を変更せず Phase 0 パイプラインを保全
  4. recovered_at をオフライン純粋関数にすることで Phase 2a 以降の閾値変更への柔軟性を確保
  5. 受け入れ条件（requirement.md L18, L39）の軽微な書き換えでゴール達成可能
