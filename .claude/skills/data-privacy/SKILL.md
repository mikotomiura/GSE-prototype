---
name: data-privacy
description: >
  GSE のキーストロークデータ・セッションログのプライバシー規約。logger.rs / hook.rs /
  wall_server.rs を書く・修正するとき、セッションログの外部送信・ML データ収集機能を
  実装するときに必須参照。以下の状況で必須参照:
  - InputEvent に新しいフィールドを追加するとき（文字内容の記録禁止確認）
  - セッションログ (NDJSON) のフォーマットを変更するとき
  - 外部エンドポイントへのデータ送信機能を実装するとき
  - Wall Server に新しいエンドポイントを追加するとき
  - ML 学習データ収集パスを設計・実装するとき
  - Tauri CSP を変更するとき
allowed-tools: Read, Grep, Glob
---

# データプライバシー規約

## このスキルの目的

GSE はキーボード入力を常時監視するアプリケーションであるため、
ユーザーのプライバシー保護を最優先とする。
何を記録してよいか・してはならないか・外部送信の条件を明確にする。

## 適用範囲

### 適用するもの
- `hook.rs` の InputEvent 生成・記録
- `logger.rs` の NDJSON ログ設計
- 将来の ML データ収集パス
- Wall Server の通信設計

### 適用しないもの
- ローカルの UI 表示（ユーザー自身に見えるデータ）

---

## 主要なルール

### ルール 1: VK コードのみ記録。Unicode 文字内容は一切記録しない

キーの「種類」は記録してよい。キーの「意味（実際に入力された文字）」は記録禁止。

```rust
// ✅ 良い例（InputEvent）
pub struct InputEvent {
    pub vk_code: u32,        // 仮想キーコード: OK
    pub timestamp_ms: u64,   // タイムスタンプ: OK
    pub is_press: bool,      // 押下/離上: OK
    pub is_repeat: bool,     // オートリピート: OK
    pub is_backspace: bool,  // バックスペース判定: OK
}

// ❌ 禁止（InputEvent に追加してはならないフィールド）
pub scan_code: u32,          // スキャンコード → 物理位置特定に使える
pub unicode_char: char,      // 入力文字: 絶対禁止
pub window_title: String,    // 作業内容の推定に使える: 禁止
```

---

### ルール 2: セッションログ (NDJSON) のリアルタイム外部送信禁止

運用中（セッション中）のログは、ローカルファイルシステムのみに保存する。
`~/Documents/GSE-sessions/gse_YYYYMMDD_HHMMSS.ndjson`

```rust
// ❌ 禁止（セッション中にリアルタイムで外部送信）
async fn log_event(entry: LogEntry) {
    send_to_server(&entry).await;  // 禁止
}

// ✅ 正しい設計: ローカルファイルのみ
fn log_event(entry: LogEntry) {
    let _ = self.tx.try_send(entry);  // バックグラウンドスレッドがローカルに書く
}
```

---

### ルール 3: ML データ収集は 3 条件を必須とする

セッション終了後にオプトインでログを外部送信する場合の必須要件:

1. **ユーザーの明示的同意**（オプトイン UI、デフォルト OFF）
2. **匿名化処理**（VK コード → キー種別カテゴリへの変換等）
3. **バッチ送信のみ**（セッション終了後。リアルタイム送信禁止）

```rust
// ML データ収集パスの設計（将来実装時に参照）
// 1. セッション終了後に anonymize_log() を呼ぶ
// 2. ユーザーが同意している場合のみ upload_batch() を呼ぶ
// 3. 送信失敗時はローカルに保持し、次回リトライ
```

---

### ルール 4: Wall Server はローカルネットワーク限定

Wall Server はランダムトークンによるアクセス制御を必須とする。
外部インターネットからアクセスできてはならない。

```rust
// ✅ 正しい設計
// - ランダムトークンを生成して URL に埋め込む
// - Windows Defender ファイアウォールルールでポートをローカル LAN に制限
// - セッション終了時にファイアウォールルールを削除

// ❌ 禁止
// - 固定トークン（"unlock123" 等）
// - 0.0.0.0 へのバインドでファイアウォール設定なし
```

---

### ルール 5: Tauri CSP は外部リソースを禁止

`tauri.conf.json` の CSP:
```
default-src 'self'; style-src 'self' 'unsafe-inline'
```

外部 CDN・フォント・スクリプトの読み込みは禁止。

---

## チェックリスト

- [ ] InputEvent に Unicode 文字・ウィンドウタイトルが含まれていないか
- [ ] セッション中にリアルタイム外部送信がないか
- [ ] ML 収集パスにオプトイン同意・匿名化・バッチ送信の 3 条件があるか
- [ ] Wall Server にランダムトークン認証があるか
- [ ] Tauri CSP が外部リソースを禁止しているか

---

## 補足資料

- `anonymization.md` — 匿名化変換パターン（将来の ML 収集実装時に参照）

## 関連する他の Skill

- `ml-workflow` — ML データ収集・ONNX 移行の設計規則
- `rust-standards` — anyhow エラーハンドリング
