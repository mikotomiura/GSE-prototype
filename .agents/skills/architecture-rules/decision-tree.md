# architecture-rules: 「このコードはどこに置くべきか」判断フロー

```
新しいコードを書く
        │
        ▼
  OS API を呼ぶか？
  (windows crate, winapi 系)
        │
      YES ──► input/ に置く
        │       └── キーボード操作 → hook.rs
        │           IME 操作 → ime.rs
        NO
        │
        ▼
  UI を描画・イベントを受け取るか？
  (React コンポーネント, Tauri イベント listen)
        │
      YES ──► src/ (Frontend) に置く
        │       ただし: 状態推定ロジックは書かない
        NO
        │
        ▼
  純粋な計算か？
  (特徴量計算, HMM 推論, 数値変換)
        │
      YES ──► analysis/ に置く
        │       └── 特徴量 → features.rs
        │           推論 → engine.rs
        NO
        │
        ▼
  セッション永続化か？
  (NDJSON 書き込み, ログバッファ)
        │
      YES ──► logger.rs
        NO
        │
        ▼
  HTTP サーバー / QR / Zen Timer か？
        │
      YES ──► wall_server.rs
        NO
        │
        ▼
  スレッド起動 / Tauri コマンド定義 / モジュール統合か？
        │
      YES ──► lib.rs
        NO
        │
        ▼
  判断できない → docs/architecture.md を読んで確認、
  またはチームに相談してから実装
```

## よくある迷いどころ

| 迷いどころ | 答え | 理由 |
|---|---|---|
| Stuck 閾値の判定 (p > 0.70) | Rust 側 (analysis/engine.rs) | ビジネスロジックは Backend |
| Wall 起動タイミングの累積計測 | Frontend (useRef で計測) | UI 状態の追跡は Frontend の責務 |
| IME ON/OFF の Atomic フラグ更新 | input/ime.rs | OS API 依存 |
| β ベースライン切替ロジック | analysis/engine.rs | 純粋な計算 |
| NDJSON レコードのフォーマット | logger.rs | 永続化層 |
