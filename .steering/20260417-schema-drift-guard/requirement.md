# schema-drift-guard

## 背景

`docs/development-guidelines.md` §10.3 に定められた「schema_dto.rs 更新 →
`src-tauri/schema/current.json` 書き出し → **gse-dataset/schema/current.json に
コピー**」フローのうち、**第 3 ステップが手動運用で強制力がない**。

2026-04-17 に以下の事象が発生した:

1. 2026-04-16 の Phase 2b IME Shadow 機能実装で `schema_dto.rs` に
   `ImeShadow` バリアントを追加。`src-tauri/schema/current.json` は更新済み。
2. gse-dataset 側 `schema/current.json` へのコピーが `/finish-task` 時に
   抜け落ち、Phase 2b task は「完了」としてクローズされた。
3. 2026-04-17 のバッチ同期で `sync-session.ps1` → `validate_schema.py` が
   `ime_shadow` / `review_marker` を未知の形状として reject。5 ファイル全てで
   `schema validation failed` となり、同期停止。
4. 手動で schema をコピーしてから再走させるまで 10 分程度の手戻り発生。

CI drift check は repo 内 (schema_dto.rs vs `src-tauri/schema/current.json`) の
1 段のみカバーしており、cross-repo のドリフトは検知範囲外。加えて memory
「CI exhausted」のとおり GitHub Actions は 3000h 超過で事実上停止しており、
CI による事前検知は当面期待できない。

## ゴール

バッチ同期 (`scripts/sync-all.*`) 実行時に **最初のステップ**として
schema parity を機械的に検証し、ドリフト検出時は **データコピー前に停止**
する。停止時のエラーメッセージで修復手順を明示し、ユーザーが迷わず
次アクションを取れる状態にする。

## スコープ

### 含むもの
- `scripts/sync-all.ps1` (Windows) への pre-flight schema parity check 追加
- `scripts/sync-all.sh` (macOS/Linux) への同等チェック追加
- ドリフト検出時の修復手順メッセージ整備
  (`cargo run --bin emit_schema > schema/current.json` とコピーの 2 段)
- `docs/development-guidelines.md` §10.3 の運用記述を pre-flight 前提に更新
- `.steering/20260417-schema-drift-guard/` の記録

### 含まないもの
- CI による drift 検知の復活（CI exhausted、対象外）
- `schema_dto.rs → src-tauri/schema/current.json` 側の drift 検知強化
  (本来 repo 内 CI の責務・本タスクでは扱わない)
- auto-copy による自動同期
  (自動データ書き換えは破壊的変更になりうるため避ける・明示的停止を優先)
- `scripts/sync-session.*` (単一ファイル版) への check 導入
  (バッチ側で事前停止できれば十分・単一呼び出しは validate_schema.py が
   既存チェック層として機能している)
- macOS/Linux 側の本番バッチ運用前提の深いチューニング
  (まず .ps1 + .sh 両方に最小 check、以降の調整は後続タスクで)

## 受け入れ条件

- [ ] sync-all.ps1 実行時、schema がドリフトしていると Step 1 より前に停止
- [ ] sync-all.sh 実行時、同等の停止動作
- [ ] 停止時のメッセージに (1) 検出した差分概要 (2) 修復コマンド例が含まれる
- [ ] schema が一致している通常ケースでは影響なく従来動作を維持
- [ ] dry-run (`-NoCommit` / `--no-commit`) でも check が走る
- [ ] docs §10.3 に pre-flight の説明が追記される
- [ ] 既存の 5 ファイル同期フローが regression なく完走する

## 関連ドキュメント

- `docs/development-guidelines.md` §10.2 (バッチ同期ワークフロー)
- `docs/development-guidelines.md` §10.3 (Schema 機械生成)
- `scripts/sync-all.ps1` / `scripts/sync-all.sh` (拡張対象)
- `scripts/sync-session.ps1` / `scripts/sync-session.sh` (対象外・参考)
- `.steering/20260416-sync-batch-sessions/` (前タスク: バッチラッパー作成)

## 運用メモ
- /reimagine 適用: Yes
- 理由: 実装案が複数考えられ (停止方針 / 自動修復 / 警告のみ / どのスクリプトに入れるか)、
  最良案が自明ではないため、破壊と構築で v2 案を検討する
