# Phase 2b: IME Shadow Features (Windows)

## 背景

IME 変換中の行動パターン（変換滞在時間、候補ナビゲーション回数、変換放棄率）は
認知摩擦の潜在的指標だが、現状 GSE のログに記録されていない。
Phase 3 (LR 判断ゲート) でこれらの特徴量が有用かデータで判断するため、
まず Windows 環境でログ収集基盤を整備する。

## ゴール

Windows 環境で IME 変換セッションごとに以下を NDJSON ログに記録する:
1. **Composition Dwell Time** — IME 変換ウィンドウの表示〜非表示の時間 (ms)
2. **Candidate Navigation Count** — 変換中の矢印キー押下回数
3. **Abandon Rate** — ESC による変換放棄の有無

HMM の放出行列・遷移行列には統合しない（ログ蓄積のみ）。

## スコープ

### 含むもの
- hook.rs への Atomic カウンター追加
- hook_windows.rs の WinEvent / LowLevelKeyboardProc コールバック拡張
- LogEntry::ImeShadow バリアント追加 + NDJSON 出力
- `#[cfg(target_os = "windows")]` による OS 分離
- 既存テスト・ゴールデンスナップショットの回帰確認

### 含まないもの
- HMM の X/Y 軸・放出行列への統合
- macOS 対応（TCC・dispatch_sync 制約により保留）
- LR 判断ゲート (Phase 3)
- gse-replay での ImeShadow 再生対応

## 受け入れ条件

- [ ] Windows ビルドで ImeShadow ログエントリが NDJSON に出力される
- [ ] HMM の既存出力に差分がない（ゴールデンスナップショット一致）
- [ ] macOS ビルドが壊れていない
- [ ] cargo test 全通過
- [ ] cargo clippy 警告なし

## 関連ドキュメント

- `.steering/20260414-improvement-roadmap/design.md` §Phase 2b (L354-407)
- `docs/architecture.md` §4 (スレッドモデル・データフロー)

## 運用メモ
- /reimagine 適用: No
- 理由: ロードマップで設計が詳細に定義済み。Atomic + WinEvent + NDJSON 出力の実装パスが一意で、複数案の比較は不要。
