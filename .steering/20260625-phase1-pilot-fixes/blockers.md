# ブロッカー

## B1: #1 層2 backend 根本修正は実機 repro のエラー文字列待ち（未解決）
- **内容**: プローブ/Nudge カード無反応の backend 根本原因（log channel `try_send` の Full か Disconnected か）は、
  実機 repro 時の devtools `console.error` 生文字列でしか確定できない。Claude 側ではアプリ起動
  （実キーボードフック＋OS 権限＋実セッション）を再現できないため確定不可。
- **静的調査で確定済み**: 3 コマンド共通の唯一の失敗点 = `tx.try_send`（`logger.rs:789` bounded(512)）。
  parse 系は全 round-trip 整合で deterministic 失敗を否定。consumer は常時 drain のため、毎回失敗なら
  (a) consumer 死亡 → Disconnected か (b) 真の backlog → Full のいずれか。
- **最有力仮説（2026-06-25 追加調査）= (a) consumer 死亡 → Disconnected → 静かな全データ消失**:
  - ログパス = `default_log_path()`: `$GSE_DATASET/raw/<pid>/gse_*.ndjson` or fallback `~/Documents/GSE-sessions/...`。
  - consumer は `File::create(path)`。失敗（GSE_DATASET の誤指定/未マウント、**macOS の Documents アクセス未許可**
    = `tauri build` の .app で TCC 未付与等）で `logger.rs:799-804` が tracing::error のみ残して early return → スレッド死亡。
  - 以後 channel は **Disconnected**。キーストロークログは `let _ = try_send`（`lib.rs:1144` 等）でエラー無視 →
    **NDJSON が一切書かれず静かに消失**。一方 probe/nudge の record コマンドは Err を返す → カードが閉じない。
  - normal load で 512 が埋まるのは打鍵速度的に非現実的（consumer は即時 drain）→ Full より Disconnected が濃厚。
  - 間欠性の説明: Documents 権限付与の有無 / GSE_DATASET 設定の有無で発生が変わる。
  - **深刻度**: 単なる UI バグでなく、該当セッションの**較正データ全損 + 無通知**。fail-loud 化が必須。
- **解除条件**: ユーザーが新ビルドで repro し、カードのインラインエラー発生時の `console.error` 文字列
  （特に "...full channel" / "...disconnected channel"）を共有 → 層2 を実装。
- **緩和済み**: 層1（フロント）で無限再表示ループと死んだボタン化は既に解消。失敗してもカード保持＋
  インラインエラー＋リトライになるため、データ収集ブロックの被害は層1 で大幅に軽減済み。

## フォローアップ（本タスク範囲外・別タスク候補）
- code-reviewer LOW: GSE-10 `gsesItems` は F2-B/F5 で配列リテラルが二重手書き（GAS:309-320 と 542-553）。
  TSE と違い byte 一致が目視依存。公式尺度（無改変・変更不可）のため本タスクでは触らず、将来
  TSE と同様に単一定数抽出する改善を別タスクで検討。
