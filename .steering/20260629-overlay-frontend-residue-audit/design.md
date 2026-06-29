# 設計

## 実装アプローチ

「推測で直さず計測で白黒つける」(requirement.md / hypotheses.md) を満たすため、**まず計装を入れ、
Windows 実機で状態行列を測る** ことに本セッションのスコープを限定する。真因が一次情報で確定する
までは恒久修正を入れない (測定をノイズで汚さない)。

計装は 2 層:
1. **Rust 読み取り専用 debug command** `debug_overlay_window_state(tag)` —
   overlay 窓の `outer_position` / `outer_size` / `is_visible`、Windows では `GWL_EXSTYLE` の
   `WS_EX_TRANSPARENT` / `WS_EX_LAYERED` を読み返し、tracing(`target=overlay_audit`) に出して
   `OverlayWindowState` を返す。窓を一切変更しない。`ensure_debug_enabled()` (GSE_DEBUG=1) ゲート下。
2. **Overlay.tsx 側の読み返しログ** — `VITE_GSE_DEBUG=1` のときだけ、統合 effect の各遷移直後
   (idle 退避後 / widget(box) show 後 / fullscreen(Wall) 後) に上記 command を `tag` 付きで invoke。
   idle は H2/H3 (後から box に戻る上書き) を捕まえるため **直後 + 遅延 (~1.5s)** の 2 回読む。

この計装で hypotheses.md の H1-H5 を確定/棄却し、真因に対する Windows で確実に効く修正を次段で行う。

## 変更対象

### 修正するファイル
- `src-tauri/src/lib.rs` — `OverlayWindowState` DTO + `debug_overlay_window_state` command を追加し、
  `generate_handler!` に登録。既存 `force_wall`/`debug_force_probe` と同じ `ensure_debug_enabled()` 様式。
- `src/components/Overlay.tsx` — `OVERLAY_DEBUG` ゲート + `auditWindowState(tag)` ヘルパを追加し、
  統合 effect の 3 分岐直後に呼ぶ (idle は遅延読みも)。介入の閾値/トリガー logic は一切変更しない。

### 新規作成するファイル
- `.steering/20260629-overlay-frontend-residue-audit/runbook.md` — Windows 実機の状態行列手順。

### 削除するファイル
- なし

## 影響範囲

- 本番 (被験者) ビルド: `VITE_GSE_DEBUG` off で `auditWindowState` は no-op、かつ `GSE_DEBUG` 未設定で
  command 自体が Err を返すため、**挙動・パフォーマンスに影響なし** (二重 gate)。
- 計装は読み取り専用。窓状態 (位置/サイズ/interactive) を変更しないので D7-D13 非回帰。

## 既存パターンとの整合性

- Rust: `ensure_debug_enabled()` + `Result<T, String>` + `tracing` (rust-standards)。unsafe Win32 は
  read-only で SAFETY コメント付き。`#[cfg(windows)]`/`#[cfg(not(windows))]` 分岐で macOS の unused_mut を回避。
- TS: `invoke<T>` 型付け・`any` 不使用・IPC 失敗は catch して握りつぶす (typescript-standards)。
- Tauri command は lib.rs に集約 (architecture-rules ルール1)。frontend は IPC + ログのみでロジックなし。

## テスト戦略

- 単体/回帰: `cargo test --workspace` (既存スナップショットに影響しないことの確認) +
  `cargo build --target aarch64-apple-darwin` (macOS path コンパイル)。Windows cfg path は
  macOS では型チェックされないため **Windows ビルド (CI) で別途コンパイル確認** が必須。
- 実機: Windows で `VITE_GSE_DEBUG=1` + `GSE_DEBUG=1`、runbook.md の状態行列を実行しログ収集。
- macOS: 非回帰スモーク (idle で背後クリック透過・カード/Wall 正常)。

## ロールバック計画

計装は独立した追加コードのみ。問題があれば command 登録行と Overlay.tsx の `auditWindowState`
呼び出しを削除すれば原状復帰 (機能ロジックは無変更なので副作用なし)。
