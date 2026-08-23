# 設計

## 実装アプローチ

`.steering/_handoff/next-session-prompt-o1-macos-instrument.md` の §2 手順（T0〜T5）を
そのまま実行する。設計判断は ADR-014/ADR-016 で確定済みであり、新規の設計判断は
発生させない（発生しそうになったら decisions.md に理由付きで記録し、勝手に決めない）。

T1（同時稼働の実機確認）を実装より先に行う。T1 が失敗した場合、T2 以降には進まず
案α（同一被験者・別時点）へ降りることを ADR-016 と `.steering/` に記録して終了する。

## 変更対象

### 修正するファイル
- `src-tauri/src/input/observe_macos.rs` — スタブから実装へ
  （`keyboard_layout_id` / `secure_input_enabled` / `FOCUS_AVAILABLE` /
  `POINTER_AVAILABLE` の4関数・定数）
- `src-tauri/src/capabilities.rs` — `emitterless` から実装済み行種を除去、
  `config_gated()` に `secure_input` の条件付き push を追加
- `src-tauri/src/lib.rs` — `keyboard_layout` を `log_channel.start()` 直前に解決
  （必要な場合のみ）
- `src-tauri/src/input/hook_macos.rs` — 既存テスト4本を壊さない範囲でのみ触る
  （§0-3 の禁止事項に抵触する変更はしない）

### 新規作成するファイル
- scratchpad 上の使い捨て probe（repo には置かない、T1 専用）

### 削除するファイル
- なし

## 影響範囲

- `observe_macos.rs` の実装により macOS で O1 非打鍵チャネル（`secure_input` /
  `focus_transition` / `pointer_bin`）が初めて記録可能になる。ただし段3（推論への配線）
  は対象外であり、記録されるだけで HMM 側は読まない。
- `capabilities.rs` の宣言変更は既存の `cargo test` による宣言/実装一致検証に影響する。
- 既存の打鍵 tap（`hook_macos.rs`）には触れない（相乗り禁止、§0-3/§4-1,2 参照）。

## 既存パターンとの整合性

- Carbon FFI + `dispatch_sync_f` パターンは `ime_macos.rs:130-195` を踏襲する。
- ポインタの量子化は自前実装せず `analysis/pointer_bin.rs`
  （`PointerAccum::add_move` / `add_button_press` / `add_wheel` → `close(now_ms)`）を使う。
- Windows 側の `observe_windows.rs`（1本の専用スレッドで WinEvent + Raw Input + 1秒ビン）
  と対称な設計にする。

## テスト戦略

- 単体テスト: ポインタ変換が座標を持たないことを純関数レベルで固定。
  `secure_input` が状態遷移時にしか行を出さないことを固定。
- 統合テスト: `capabilities.rs` の宣言/実装一致を `cargo test` で機械検証（既存の仕組み）。
- 実機確認（E2E 相当）: T1（同時稼働）/ T5（ドロップ実測・行出力・meta 反映・UI 動作・
  長時間安定性）。実機でしか検証できない部分は Read/grep による事後確認で代替しない。
- ゴールデン回帰: `cd src-tauri && cargo run --bin gse-replay -- ...` を6本すべて実行し
  byte-equal を確認（`HMM_VERSION` / `is_feature_key` を変えていないため差分ゼロが期待値）。

## T2 実装の技術選定（★ 実施済み・最終形）

- **`keyboard_layout_id()`**: `TISCopyCurrentKeyboardLayoutInputSource`
  （ADR-014 D4 逐語で指定）+ `kTISPropertyInputSourceID`。
  ⚠️★★★ **当初 `dispatch_sync_f` 経由（`ime_macos.rs` パターンの流用）で実装したが、
  実機でメインスレッド自己デッドロック→ `EXC_BREAKPOINT` クラッシュを実測した**
  （唯一の呼び出し元 `lib.rs::setup()` が既にメインスレッドだったため）。
  → ★ **直接呼び出しに修正**（`decisions.md` 判断3）。この手戻りは「実機でしか踏めない
  クラスの不具合」の実例であり、T5（実機総合確認）を省略してはいけない理由の裏付けになった。
- **`secure_input_enabled()`**: `IsSecureEventInputEnabled()`（Carbon `#[link]` 1行、
  戻り値は `bool` ではなく `u8` で受けて `!= 0` 正規化 — security-checker L1 指摘対応）。
- **`POINTER_AVAILABLE` / L-b ポインタ**: 別 `CGEventTap`
  （`core-graphics` クレートは既存依存）+ `analysis/pointer_bin.rs` の再利用。
  ⚠️ レビュー対応で **初回設置失敗時のリトライ（backoff 2s→5s→10s）**・
  **無通知失効時の即再有効化＋スラッシング防止**・**tap 未設置中は `CFRunLoop::run_in_mode`
  を呼ばず `thread::sleep` で待つ**（security-checker H1: source 無しで run_in_mode を
  呼ぶとビジーループになりうると実測されたための対処）を追加した。
- **`FOCUS_AVAILABLE` / L-c フォーカス遷移**: `NSWorkspace.didActivateApplicationNotification`。
  Cocoa/AppKit API は Carbon FFI パターンでは書けないため、`objc2`(0.6.4)/
  `objc2-foundation`(0.3.2)/`objc2-app-kit`(0.3.2)/`block2`(0.6.2) を直接依存に追加した。
  ★ いずれも Cargo.lock に既に解決済み（Tauri の tao/wry の推移依存）だったため
  バージョン解決は壊れず、実機ビルド・実行で正常動作を確認した。

## レビュー対応で追加した設計要素（実装中の code-reviewer/security-checker レビューより）

- `POINTER_CALLBACK_COUNT` — tap の生存信号（ADR-013 の失敗類型「ゼロ行=無活動」と
  「ゼロ行=計器死亡」を区別できない、を防ぐための診断カウンタ）
- `secure_input` は edge-encoded な区間フラグであるため、**送信成功時のみ**状態を進める
  （失敗時に進めると以降ずっと符号が反転する重大バグだった）
- `observe.rs::start()` に二重起動ガード（`STARTED: AtomicBool`）を追加し、全 OS 共通で
  observer/tap の二重設置を防ぐ
- `fold_delta`/`build_pointer_bin` を純関数に切り出し、callback が実際に呼ぶロジックを
  直接テストできる形にした（以前はテストが production の配線を通っていなかった）

詳細な指摘一覧と対応・見送り判断は `.steering/20260824-o1-macos-instrument/decisions.md`
「code-reviewer / security-checker レビュー」節を参照。

## ロールバック計画

`observe_macos.rs` の変更が問題を起こした場合は当該コミットを revert すれば
スタブ状態に戻る（OS 非依存の器・段1・HMM 側は無変更のため副作用は macOS の
ロガー出力行のみに限定される）。
