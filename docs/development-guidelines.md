# 開発ガイドライン

## 1. コーディング規約

### Rust

- **エラーハンドリング**: アプリケーションレベルでは `anyhow::Result` を使用。ライブラリ的なモジュールでは `thiserror` を検討。
- **ログ**: `tracing` クレートを使用（`tracing::info!`, `tracing::warn!`, `tracing::error!`）。`println!` や `eprintln!` は使わない。
- **unsafe ブロック**: Win32 API 呼び出しに限定し、ラッパー構造体内に隔離する。unsafe の理由をコメントで明記する。
- **Windows API**: `windows` crate (v0.58+) のみ使用。`winapi` crate は禁止。
- **命名**: Rust 標準の snake_case。型は PascalCase。定数は SCREAMING_SNAKE_CASE。
- **フォーマット**: `cargo fmt` に従う。

### TypeScript / React

- **命名**: コンポーネントは PascalCase、変数・関数は camelCase。
- **依存最小化**: 新しいライブラリ追加前に、既存依存で代替可能か確認。
- **型安全**: `any` の使用を避ける。Tauri IPC のレスポンスにも型を付ける。
- **状態管理**: React 組み込みの useState / useRef で十分な場合は外部ライブラリを使わない。

### コメント

- **書くべき場面**: HMM パラメータの根拠（論文参照）、unsafe の安全性説明、非自明なアルゴリズム選択の理由
- **書くべきでない場面**: コードから明らかな処理内容、TODO を放置（修正するか Issue にする）
- **フォーマット**: `//` で単行。ブロックコメントは `///` (doc comment) のみ。

## 2. Git ワークフロー

### ブランチ戦略

- **メインブランチ**: `main` — 常にビルド可能な状態を維持
- **作業ブランチの命名**: `[type]/[task-name]`
  - type: `feature`, `fix`, `refactor`, `docs`, `chore`
  - 例: `feature/onnx-inference`, `fix/ime-polling-crash`

### コミットメッセージ

```
[type]([scope]): [短い説明]

- 変更内容 1
- 変更内容 2

Refs: .steering/[YYYYMMDD]-[task-name]/
```

- **type**: feat, fix, refactor, docs, chore, test
- **scope**: engine, hook, ime, wall, frontend, logger 等
- **例**: `feat(engine): add ONNX Runtime inference path`

### バージョニング

- README の changelog でバージョンを管理（v2.0〜v2.21+）
- コミットメッセージ末尾に `(vX.XX)` を付与（重要な機能変更時）

## 3. テスト方針

### 現状

現時点では自動テストは未整備。HMM パラメータは手動チューニングとセッションログによる事後検証で品質を担保している。

### 目標

| 種類 | 範囲 | 優先度 | 備考 |
|---|---|---|---|
| 単体テスト | analysis::features, analysis::engine | 高 | 純粋な計算ロジック。OS 依存なし |
| 統合テスト | lib.rs のスレッド連携 | 中 | crossbeam channel のモック可能 |
| E2E テスト | Tauri アプリ全体 | 低 | OS フックの自動テストは困難 |

### テストの方針

- `analysis/` モジュールは OS 非依存なので、通常の `#[cfg(test)]` + `cargo test` で検証可能
- `input/` モジュールは OS フックに依存するため、統合テストは実機で手動確認
- セッションログ (NDJSON) の事後分析スクリプトが実質的な回帰テストとして機能

## 4. レビュー基準

### 必須チェック

- [ ] `cargo build` が成功する
- [ ] `cargo clippy` の警告がない（または理由付きで `#[allow]`）
- [ ] フックコールバック内にブロッキング処理がない
- [ ] unsafe ブロックに安全性コメントがある
- [ ] windows crate のみ使用（winapi 不使用）

### 推奨チェック

- [ ] HMM パラメータ変更時はセッションログで事後検証済み
- [ ] 新機能にはユースケースの記述がある
- [ ] エラー条件が tracing で適切にログ出力されている
- [ ] Tauri IPC 失敗時に安全なデフォルト値にフォールバックしている

## 5. パフォーマンス指針

### 厳守事項

- **フックコールバック**: Atomic 操作 + channel send のみ。Mutex ロック、I/O、メモリアロケーション禁止。
- **1Hz ゲート**: Analysis スレッドの recv_timeout で実現。累積ドリフトを防止するため絶対時刻ベースで管理。
- **EWMA 計算**: f64 演算のみ。ヒープアロケーションなし。

### 監視ポイント

- crossbeam channel の try_send 失敗率（warn ログで追跡）
- Logger の 5 秒フラッシュ間隔が I/O 負荷を許容範囲に保っているか
- Wall Server の HTTP レスポンス時間（スマートフォン UX に影響）

## 6. 依存ライブラリの追加基準

新しい crate / npm パッケージを追加する前に確認:

- [ ] 既存の依存で代替できないか？
- [ ] メンテナンスが活発か？（最終リリースが 1 年以内）
- [ ] ライセンスは MIT / Apache-2.0 互換か？
- [ ] コンパイル時間への影響は許容範囲か？（Rust の場合特に重要）
- [ ] `windows` crate の feature flags は必要最小限か？

## 7. セキュリティ指針

- **キーストロークデータ**: VK コードのみ記録。文字内容（Unicode テキスト）は一切記録しない。
- **セッションログ（リアルタイム運用）**: ローカルファイルシステムに保存。リアルタイム推定中の外部送信は行わない。
- **セッションログ（学習データ収集）**: ML モデル学習のためにセッションログを外部に送信する場合は、以下を必須とする:
  - ユーザーの明示的同意（オプトイン）
  - VK コードの匿名化（キー種別カテゴリへの変換等）
  - 送信先・保存期間の明示
  - 送信タイミングはセッション終了後のバッチ処理（リアルタイム送信禁止）
- **Wall Server**: ランダムトークンによるアクセス制御。ローカルネットワークのみ。ファイアウォールルールでポートを動的管理。
- **Tauri CSP**: `default-src 'self'; style-src 'self' 'unsafe-inline'` — 外部リソースの読み込みを禁止。

## 8. 禁止事項

- ❌ `winapi` crate の使用（`windows` crate v0.58+ のみ）
- ❌ フックコールバック内でのブロッキング操作
- ❌ グローバル TSF フック（ITfThreadMgr）の使用（UIPI でブロック）
- ❌ キーストロークの文字内容（Unicode テキスト）の記録
- ❌ リアルタイム推定中のセッションデータ外部送信（学習データ収集はセッション終了後にオプトインで許可）
- ❌ `println!` / `eprintln!` の使用（`tracing` を使う）
- ❌ `any` 型の多用（TypeScript）
