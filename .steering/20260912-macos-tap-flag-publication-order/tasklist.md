# tasklist — macOS 公開フラグの公開順修正

## 調査
- [x] 失敗テスト・アサーション・値を CI ログで特定 (`left: None` ×2 本)
- [x] PR #199 の mac job で同テストが **ok** だったことをログで確認 (= 間欠)
- [x] 手元で 6 回連続実行 → 6/6 成功
- [x] `None` を返す条件を `tap_is_enabled()` の実装で確定 (`TAP_ENABLED_SNAPSHOT == -1`)
- [x] `-1` を書く経路を**全部**列挙 (`:891` / `:1002` / 初期値)
- [x] 公開順が設置時・退出時の**両方**で逆になっていることを特定

## 実装
- [x] 設置時: `HOOK_ACTIVE.store(true)` を snapshot / `TAP_PORT` の**後**へ移す
- [x] 退出時: `HOOK_ACTIVE.store(false)` を payload クリアの**前**に保つ (★ 下ろすのは先)
- [ ] 退出時の `Ordering` を `Relaxed` → `Release` に揃える
- [x] テストに切り分け情報を足す (`HOOK_ACTIVE` 現在値 / `watchdog_recoveries()`)

## 検証
- [x] `cargo clippy --all-targets -- -D warnings` → exit 0
- [x] `cargo clippy --all-targets --features package -- -D warnings` → exit 0
- [x] `cargo test --features package --workspace` → 緑
- [x] ⚠️ `macos_hook_rehook` を**連続 10 回**回して緑 (★ 間欠なので 1 回では足りない)
- [x] ゴールデン byte-equal / schema byte-equal
- [x] ⚠️ `HMM_VERSION` を bump していない

## 記録
- [x] `decisions.md`
- [ ] コミット / PR
- [ ] ⚠️ main の CI が緑に戻ったことを確認 (★ 間欠なので複数 run を見る)

## レビュー反映 (2026-09-12・3 系統)

### 一致した指摘 (⚠️ 最優先)
- [x] **HIGH**: 下ろし側の不変条件は `Release` では保証されない (code-reviewer HIGH ＋ Codex HIGH ＋ security LOW-1)
      → コメントを「下ろす側は窓を**縮める**のみ」に訂正
- [x] **HIGH**: 「main の赤の原因」の断定が窓の幅と噛み合わない (code-reviewer HIGH ＋ 自分の検算)
      → 表題・steering を「(a) を塞いだ / (b) は未排除」に統一

### code-reviewer のみ (⚠️ 診断の存在意義を直撃)
- [x] **MEDIUM**: `tap_diag()` が assert 対象を読んだ**後**に読むので整合スナップショットでない
      → (b) で落ちたのに `HOOK_ACTIVE=true` を出して **(a) と誤読させる**
- [x] **MEDIUM**: 「下ろす 3 経路」は実際は **2 経路** (⚠️ 実誤り。grep で確認)
- [x] **MEDIUM**: payload の定義が未閉鎖 —— `USING_ACCESSIBILITY_FALLBACK` (`:999`) は
      `HOOK_ACTIVE` (`:974`) より**後**にあり、字義通りだと新不変条件に違反して見える
- [x] **LOW**: `hook.rs:244` の doc に「payload を後読みしない読み手は `Relaxed` でよい」を残す

### security-checker のみ
- [x] **MEDIUM**: コメント「観測側は `Acquire` で読む」が本番と食い違う
      (⚠️ 本番 4 箇所は `Relaxed` 単独読み。`Acquire`＋payload はテストのみ)

### Codex のみ
- [x] **HIGH**: 観測側の double-check が無く teardown 中の interleaving を検証できていない
      → ★ テストに **flag → payload → flag の二度読み**を入れて (a)/(b) を判定させる

### 却下 / 別 PR
- [x] `lib.rs` / `tray.rs` の `Relaxed` 読みを変えない判断 → **妥当** (code-reviewer LOW が追認)
- [ ] ⚠️ **別 PR**: `liveness.rs:604` と `hook_macos.rs` のテストがグローバル
      `TAP_ENABLED_SNAPSHOT` を取り合う (★ 本件とは別バイナリなので今回の赤とは無関係)
- [x] assert をデッドライン付きポーリングにする案 → **却下** ((a) を恒久的に隠すため)
