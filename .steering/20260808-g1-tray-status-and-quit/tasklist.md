# タスクリスト

## 実装

- [x] `tauri` に `tray-icon` feature を足す
- [x] `src-tauri/src/tray.rs`（3 状態 + メニュー + 1Hz 更新スレッド）
- [x] 終了経路を `shutdown_and_exit()` に一本化（`SHUTTING_DOWN` で二重起動を防ぐ）
- [x] main 窓の `CloseRequested` を捌く（overlay の × は無視）
- [x] ⚠️ G1 では分析起動とフォルダ表示をやらない
- [x] スタート画面に「GSE を終了」

## 検証

### ★ 機械検査

- [x] `cargo test --workspace` 304 passed / 0 failed（トレイ 5 件を含む）
- [x] ゴールデン回帰 15 snapshots match / `emit_schema` byte-equal
- [x] `cargo fmt --check` / clippy 新規警告なし / `tsc --noEmit`

### ★★ 実機（dev ビルドを起動して確かめた）

| 何 | 結果 |
|---|---|
| トレイが出るか | ✅ `menu bar 2` に status item が 1 個。★ title = `○` = `measure_title(Stopped)` |
| トレイのスレッド | ✅ `sample` に `Thread: gse-tray` |
| 生成エラー | ✅ `Failed to build the tray icon` は 0 件 |
| メニューの中身 | ✅ `GSE — 停止中（記録していません）` / 区切り / `GSE を終了` |
| ★★ トレイの「終了」 | ✅ **2 秒でプロセス消滅**。ログに `tray: quit requested` → `shutdown requested` → `session closed` |
| ★★ × で閉じる | ✅ **2 秒でプロセス消滅**（★ 3 時間ゾンビの根本原因が塞がった） |
| ⚠️ 副産物 | ★ `gse-app.log`（本日追加）が**実バイナリで動いた**。1242 B / 10 行 / mode 0600 |

### ⚠️ ★ 確かめられなかったこと（正直に書く）

- ⚠️ **`計測中` / `計測できていません` への遷移は実機で見ていない。**
  ★ 理由: `開始する` は WKWebView の中にあり、**AX に露出しないので押せなかった**
  （`entire contents` に「開始」が 0 件。`screencapture` も Screen Recording 権限が無くて不可）。
  → 純関数の単体テストと 1Hz polling の配線でしか担保していない。
  ★ **確認方法**: セッションを 1 回開始して `gse-app.log` に
  `tray state -> Measuring` が出るのを見る（1 行で済む）。
- ⚠️ **dev ビルドでの確認であって、配布物（CI の本番バイナリ）ではない。**

## 仕上げ

- [x] 自己レビュー（★ 2 件の誤りを自分で見つけて直した）
- [x] `/cross-review`（Codex）— 5 指摘。★ うち 1 件は**私が作った経路**のバグ（未開始終了で
      空パス → 意図しないフォルダを開く）。4 件対応 / 1 件は実測で不成立と判定
- [x] 配布まで（v0.1.24 タグ → CI Release → zip → Drive 差し替え・byte 照合・共有設定確認）
- [x] 引き継ぎメモの更新

## ⚠️ 本タスクで**残った**もの（次セッションへ）

- [ ] ★★ **Windows 実機の結果確認**（2026-08-09 に研究者が実施済み・⚠️ **私は結果を見ていない**）
  - トレイが出たか（⚠️ オーバーフローに畳まれていないか）
  - ★ `gse-app.log` に `tray state -> Measuring` が出たか（**唯一どこでも未確認の遷移**）
  - × で `gse-next.exe` が消えたか
- [ ] 提出確認ダイアログの見た目（pending が無いと出ないので未確認）
- [ ] `refreshG1RunSheet` の所要（6.0 → 18.6 秒）が伸び続けないか
