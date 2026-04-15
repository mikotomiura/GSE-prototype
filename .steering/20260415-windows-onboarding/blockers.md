# Blockers — Windows Onboarding

Windows 実機での検証中に発見したブロッカー・回避策を記録する。初期は空。

## テンプレ

```
### [YYYY-MM-DD] <タイトル>

- **症状**: 何が起きたか
- **再現手順**: 再現性の有無と再現コマンド
- **根本原因**: 判明していれば記載、不明なら「未解明」
- **暫定回避策**: タスクを進めるための迂回手段
- **影響範囲**: Windows 固有 / 両 OS / 特定ハードウェアのみ 等
- **恒久対応**: 後続タスクで対応する場合、担当タスクへのリンク
```

---

## 既知の懸念事項 (実機検証前の予測、実測で確認する項目)

### 懸念1: SmartScreen アラート

- **予測症状**: `cargo tauri dev` で起動する未署名バイナリに Windows Defender SmartScreen が反応する可能性
- **暫定回避策**: SmartScreen ダイアログで「詳細情報 → 実行」を選択
- **恒久対応**: タグ push 時の `build-windows` ジョブで NSIS installer が生成されるが、これも未署名。Phase 2+ で署名証明書導入を検討

### 懸念2: グローバルホットキー衝突

- **予測症状**: `Ctrl+Shift+Alt+F/I/S` が IME 切替・他アプリのショートカットと衝突
- **暫定回避策**: 別キーに変更 (例: F9/F10/F11) する場合は `lib.rs` の `Modifiers` + `Code` を修正し、両 OS で合意
- **恒久対応**: 企業 PC や日本語 IME 利用時の推奨キーマップを blockers.md で収集、必要なら設定可能化

### 懸念3: Webview2 Runtime 未導入

- **予測症状**: Dashboard 起動直後にクラッシュ (`WebView2Loader.dll` not found 等)
- **暫定回避策**: Microsoft Edge WebView2 Runtime を別途インストール
- **恒久対応**: `tauri.conf.json` の `bundle.windows.webviewInstallMode` で自動導入設定 (既に `downloadBootstrapper` がデフォルト)

### 懸念4: グループポリシー制約

- **予測症状**: 企業管理下の Windows で `RegisterHotKey` が失敗、または Hook 登録が拒否される
- **暫定回避策**: 個人 PC での検証を優先
- **恒久対応**: エンタープライズ展開時に検討

### 懸念5: JIS キーボードでの修飾子衝突

- **予測症状**: JIS 配列で `Ctrl+Shift+Alt+F` が特殊文字入力と衝突
- **暫定回避策**: US 配列で検証、JIS 固有の issue は個別記録
- **恒久対応**: キー配列に応じた動的修飾子切替 (Phase 2+)

---

## 実機で発見したブロッカー

### BL-1 [2026-04-16] セッション NDJSON の保存先が Documents ではなく gse-dataset/raw 配下

- **症状**: Windows 実機で Dashboard のセッション終了後、steering 想定の `%USERPROFILE%\Documents\GSE-sessions\gse_*.ndjson` ではなく **`C:\gse-dataset\raw\P000\gse_*.ndjson`** に書き出された
- **再現手順**: 毎回再現。`npm run tauri dev` → ラベリング → セッション終了 → dir Documents → 空、dir gse-dataset/raw/P000 → 新ファイル
- **根本原因**: 未解明。`logger.rs` が何らかの方法で gse-dataset の raw パスに書いている (ハードコード / 環境変数 / dirs crate の Windows 挙動差？)。Mac 側挙動との差分未調査
- **暫定回避策**: Stage E は該当パスから直接読む (steering 手順の `$SESSION` 変数定義を調整)。完了ログに明記
- **影響範囲**: Windows 固有 (macOS では Documents に書かれている実績あり)
- **恒久対応**:
  - Option A: Windows でも Documents に戻すよう `logger.rs` の path 解決を修正
  - Option B: 現状の `gse-dataset/raw/` 保存を「開発者マシン限定の仕様」として docs に明文化 (gitignore で raw/ は保護済み)
  - 判断は Windows 側で継続的に GT 収集する運用次第。Phase 2a 着手前に別タスクで決定

### BL-2 [2026-04-16] gse-replay --metrics が label 近接の feat を全取りこぼしする

- **症状**: `gse_20260415_144120.ndjson` は user_label 6件 (Flow 4 / Inc 1 / Stuck 1)、元 NDJSON の feat 96件を保持。python で時刻差分を計測すると全ラベルが ±500ms 以内に feat を持つ。にもかかわらず `gse-replay --metrics` は 6 件全てを `no FeatSnapshot within ±1000ms` 警告で脱落させ、confusion matrix 全 0・per-class support=0 を返す
- **再現手順**:
  1. `C:\gse-dataset\raw\P000\gse_20260415_144120.ndjson` を入力として
  2. `cargo run --bin gse-replay --target x86_64-pc-windows-msvc -- <session> --metrics`
  3. warnings が 6 件出る
- **根本原因**: 調査中。疑い2つ:
  1. `gse-replay` は元 NDJSON の feat を**破棄して step() 再実行で自前生成する**設計 (replay.rs:4)。再生成 feat 列が label 時刻とアライメントしていない可能性
  2. または Mac/Windows で step() 再実行結果が異なる (タイムスタンプ精度 / イベント順序)
- **補足**: `detection_lead_ms_median` は +26315ms で計算される → 再生成 feat 列自体は存在し argmax も効いている。LABEL_MATCH_WINDOW_MS=1000 の近接判定のみが全滅している点が奇妙
- **暫定回避策**: 当セッションの metrics JSON は all-zero のまま commit (dataset repo `534893a`)、aggregate で all-zero session として扱う
- **影響範囲**: 現時点では Windows onboarding セッションで確認。Mac 側 baseline (`gse_20260415_080921.metrics.json`) は Stuck support=2 で正常動作しており、両 OS 差分の可能性あり
- **恒久対応**: 別タスク `20260416-metrics-label-alignment-bug/` 等で調査。Phase 2a Go/No-Go 判定前に fix 必須 (retrospective の MEDIUM M2 と別物だが優先度 HIGH に昇格)

### BL-3 [2026-04-16] SSH 認証未セットアップ — gse-dataset は HTTPS でクローン

- **症状**: `ssh -T git@github.com` が `Permission denied (publickey)`
- **暫定回避策**: `git clone https://...` で HTTPS 経由クローン。push も HTTPS で動作確認済み
- **影響範囲**: 本機のみ (ユーザー環境依存)
- **恒久対応**: ユーザー判断。Windows 実機で継続運用するなら SSH 鍵を `ssh-keygen` で生成し GitHub に追加推奨
