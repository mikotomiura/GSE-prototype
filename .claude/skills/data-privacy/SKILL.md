---
name: data-privacy
description: >
  GSE のキーストロークデータ・セッションログのプライバシー規約。logger.rs / hook.rs /
  redaction.rs / recording.rs を書く・修正するとき、セッションログの外部送信・
  非打鍵チャネル・ML データ収集機能を実装するときに必須参照。以下の状況で必須参照:
  - InputEvent に新しいフィールドを追加するとき（文字内容の記録禁止確認）
  - セッションログ (NDJSON) のフォーマットを変更するとき
  - 外部エンドポイントへのデータ送信機能を実装するとき
  - ML 学習データ収集パスを設計・実装するとき
  - Tauri CSP を変更するとき
  - ★ **区間指定削除 / 一時停止**（redaction.rs / recording.rs / RecordingControls.tsx）を触るとき
  - ★ **非打鍵チャネル**（ポインタ / フォーカス遷移 / secure_input / レイアウト識別子）を実装するとき
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
- ★ **`redaction.rs` / `recording.rs`**（被験者の削除・停止経路・ルール 6）
- ★ **非打鍵チャネル**（`pointer_bin` / `focus_transition` / `secure_input`・ルール 7）

> ⚠️★★★ **Wall Server は 2026-08-23 に削除された**（ADR-015）。★ 下の**ルール 4 は歴史的記述**であり、
> 現行 repo に `wall_server.rs` は無い（実測。⚠️ 復活させるならルール 4 を先に読むこと）。

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

運用中（セッション中）のログは、ローカルファイルシステムのみに保存する。保存先は
`logger::default_log_path()` が環境変数 `GSE_DATASET` の有無で 2 段決定する:

1. `GSE_DATASET` 設定時: `$GSE_DATASET/raw/P000/gse_YYYYMMDD_HHMMSS.ndjson`
2. 未設定時 (fallback): `~/Documents/GSE-sessions/gse_YYYYMMDD_HHMMSS.ndjson`

どちらの経路でも**ローカル FS のみ**であり、リアルタイム外部送信は禁止。どのパスに
解決されたかは起動時の `tracing::info!` (`resolved_log_dir`, `source`) で常時可視化される。

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

### ルール 6: ★★★ 被験者は **止められる・消せる** —— この 3 つを壊さない (O1 / ADR-014 D7)

⚠️★★★ **ADR-014 判断 3（倫理審査は不要）の根拠 3 がこの 3 つで立っている。**
逐語の崩れる条件 ——「⚠️ **削除 UI が実装されないまま収集を始めた時点で崩れる**」。

| # | 要件 | 実装 | ⚠️ 壊す変更の例 |
|---|---|---|---|
| i | **稼働中インジケータ** | `RecordingControls.tsx`（★ 常時表示） | ⚠️ 「止まっている」を黙って「記録中」に見せる fallback |
| ii | **即時の一時停止** | `recording.rs` + `logger.rs` の書き出しゲート | ⚠️ 新しい行種を `is_writable_while_paused` に足す |
| iii | **事後の区間指定削除** | `redaction.rs` + `delete_time_range` | ⚠️ 削除の引数に**理由**を足す |

```rust
// ❌ 禁止: 削除に理由を求める
fn delete_time_range(from_ms: u64, to_ms: u64, reason: String)  // ⚠️ 同意文書 §4 違反

// ✅ 正しい: 理由を取らない (UI にも入力欄を置かない)
fn delete_time_range(from_ms: u64, to_ms: u64)
```

**削除の台帳 (`redaction_ledger.jsonl`) に書いてよいのは 5 つの数だけ**:
`requested_at` / `from` / `to` / `files_touched` / `lines_removed`。

```rust
// ❌ 禁止: 何を消したかを台帳に残す (削除の意味が消える)
{"from":.., "to":.., "removed_categories":["alphabetic","backspace"], "app":"..."}

// ✅ 正しい: 「消した」という事実だけ
{"requested_at":..,"from":..,"to":..,"files_touched":2,"lines_removed":37}
```

⚠️ **台帳を `gse_*.ndjson` にしない** —— `reconcile.rs` が提出候補として拾い、
★ **削除を要求した事実そのものが研究者へ渡る**。

⚠️ **新しい行種を足したら `LogEntry::line_type()` に足す。**
★ 足し忘れると一時停止ゲートを素通りし、**止めたはずの記録が黙って残る**。

#### ⚠️★★★ 2026-08-25 追記 — **iii（区間指定削除）は「送信前」にしか効かない**

★ **O1 は日次ローテートで閉じ、閉じたファイルを 48 時間おいてから自動提出する**
（★ 研究者判断・ADR-014 **D8 の上書き**・`.steering/20260825-o1-researcher-decisions/decisions.md` 判断 O1-2）。

⚠️ `delete_time_range` → `redact_dir` は **ローカルの `gse_*.ndjson` だけ**を書き換え、
**`.age`（提出物）は対象外**である（`redaction.rs:174-181`）。→ ★ **送信済みは呼び戻せない。**

| いつ | ★ 何が効くか |
|---|---|
| **提出前**（★ 48 時間の猶予） | ✅ **端末上で消える**（★ 根拠 3 はここで立っている） |
| ⚠️ **提出後** | ⚠️ **研究者側の削除手続き**（★ **台帳に載せること**・ADR-014 D8 制約 3） |

⚠️★★★ **したがって「48 時間の猶予」は UX の都合ではなく *根拠 3 を守る機構* である。**
★ **猶予を縮める / 外す変更は、ADR-014 判断 3 の再検討を伴う。**

---

### ルール 7: ★★★ 非打鍵チャネルは **段 1 の凍結表の中だけ** (O1 / ADR-014 D4)

★ 記録してよいのは以下**だけ**である（⚠️ **1 本も足さない**。足すなら別 ADR）:

| チャネル | ★ 記録してよい | ⚠️★★★ 記録してはならない |
|---|---|---|
| **フォーカス遷移** | ★ **遷移が起きた時刻のみ** | ⚠️ HWND / PID / アプリ識別子 / ウィンドウタイトル / **ウィンドウ通し番号**（★ 擬似識別子） |
| **ポインタ** | ★ **1 秒固定ビンの量子化スカラ**（移動量 / ボタン / ホイール）・⚠️ **ゼロ抑制** | ⚠️★★★ **絶対座標・軌跡・符号付き dx/dy・解像度・マルチモニタ配置**（★ 累積で軌跡が復元でき画面内容の代理になる）／⚠️ **イベント単位の移動量＋時刻の列**（★ mouse dynamics は**個人識別可能な生体特徴**） |
| **`secure_input`**（mac） | ★ **区間フラグ**（on/off の時刻） | ⚠️ 中身は一切取得しない |
| **レイアウト識別子** | ★ セッション開始時に **1 回だけ・識別子のみ** | ⚠️★★★ **`ToUnicodeEx` / `UCKeyTranslate` を呼ばない**（★ 呼んだ瞬間に**入力文字そのものがプロセス内に出現する**） |

```rust
// ❌ 禁止: HWND をコールバックの外へ出す / 座標を持つ
struct FocusEvent { t: u64, hwnd: isize }          // ⚠️ 擬似識別子
struct PointerEvent { t: u64, x: i32, y: i32 }     // ⚠️ 軌跡が復元できる

// ✅ 正しい: 時刻だけ / 1 秒ビンの量子化スカラだけ
struct FocusTransition { t: u64 }
struct PointerBin { t: u64, moved: u8, buttons: u8, wheel: u8 }
```

⚠️★★★ **役割カテゴリ（`editor` / `terminal` / `browser`）を入れない** ——
★ 入れた瞬間に **判断 3 の根拠 1（content-free）が崩れる**（ADR-009 D2 の順序は「G2 が落ちてから」）。

⚠️ **`WH_MOUSE_LL` を使わない**（★ システム全体のマウス入力を直列化し、
`LowLevelHooksTimeout` で**通知なく外される**）。→ ★ Windows は **Raw Input**、mac は**別 tap**。

---

## チェックリスト

- [ ] InputEvent に Unicode 文字・ウィンドウタイトルが含まれていないか
- [ ] セッション中にリアルタイム外部送信がないか
- [ ] ML 収集パスにオプトイン同意・匿名化・バッチ送信の 3 条件があるか
- [ ] Tauri CSP が外部リソースを禁止しているか
- [ ] ★ 削除経路が**理由を取っていない**か / 台帳が **5 つの数だけ**か (ルール 6)
- [ ] ★ 新しい行種を `LogEntry::line_type()` に足したか (ルール 6・一時停止ゲート)
- [ ] ★ 非打鍵チャネルが**段 1 の凍結表の中だけ**か / 座標・識別子が漏れていないか (ルール 7)

---

## 補足資料

- `anonymization.md` — 匿名化変換パターン（将来の ML 収集実装時に参照）

## 関連する他の Skill

- `ml-workflow` — ML データ収集・ONNX 移行の設計規則
- `rust-standards` — エラーハンドリング (⚠️ 本 repo は `anyhow` を依存に持たず `Result<_, String>` を使う)
