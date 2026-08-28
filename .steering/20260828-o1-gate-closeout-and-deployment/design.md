# 設計

## A-1: O1 の liveness —— ★ **トレイだけ切り離す**

### ⚠️ 一次資料で確かめたこと（`src-tauri/src/lib.rs:4081-4090`）

★ トレイ表示と再設置は **同じ `HookHealth::Down` から発火している**:

```rust
crate::input::hook::HOOK_STARVED.store(health == HookHealth::Down, Ordering::Relaxed);
if health == HookHealth::Down && !rehook_done_this_episode { rehook = request_reinstall(); }
```

→ ⚠️ **`down_after_ms` を伸ばすと、本当にフックが死んだときの再設置も同じだけ遅れる。**

### 採用（研究者判断 2026-08-28）

| 経路 | 通常 / G1 | **O1** |
|---|---|---|
| ログ `ERROR`（研究者が後から読む） | 30 秒 | **30 秒（据え置き）** |
| 再設置 `request_reinstall()` ＋ `alive:false` の記録 | 120 秒 | **120 秒（据え置き）** |
| ★ トレイ「⚠ 計測できていません」（**被験者の目に入る**） | 120 秒 | **1800 秒（30 分）** |

★ 根拠: 被験者の目に入る誤警告がいちばん害が大きい一方、
⚠️ **復旧力（再設置）と証跡（NDJSON）は 1 つも失わない**のがこの分け方だけである。

### 実装

- `input/liveness.rs` に **純関数** `tray_starved(s, th, o1_tray_after_ms: Option<u64>)` を足す
  （★ 判断は OS 非依存側に置く、という既存の設計方針に従う）。
- `lib.rs` に `const O1_LIVENESS_TRAY_AFTER_MS: u64 = 1_800_000;` を置き、
  `HOOK_STARVED.store(...)` を `tray_starved(...)` 経由にする。
- ⚠️ `Thresholds` に欄を足さない（★ 49 か所で使われており、境界テストを壊す）。

## A-2: 送信 timeout —— ★ **値を触らず、ゲートの検査を強くする**

⚠️★★★ 現在の検査は `grep from_secs(180)` なので、**数字を書き換えるだけで緑になる**。
★ 実測（`.gs` 手順 8・1 日ぶんの実サイズ）は **B-1 のデプロイに依存**していて、いま実施できない。

→ ★ **検査を「実測の記録があるか ＋ コードが直っているか」の 2 本立てにする**:

1. `experiments/20260801-controlled-friction-task/o1-upload-timeout-measurement.md` を新設し、
   ★ 空欄の記録票（`状態: 未実施`）として置く。
2. ゲートは (a) 記録が `実測済み` で必須欄が埋まっている **かつ** (b) `from_secs(180)` が消えている、
   の**両方**でだけ緑にする。
3. selftest 3 に「**片方だけでは緑にしない**」を 2 件足す。

⚠️ これで A-2 は**赤のまま**だが、★ 「見えないまま緑」への抜け道が塞がる。

## E-1: 削除後の案内が O1 で逆を指している

★ `src/components/RecordingControls.tsx` の `outcome.files_skipped > 0` のブロックにだけ
`o1Mode` の分岐が無い。→ O1 では「**記録を再開する**」を案内する。
⚠️ 通常運用 / G1 の文言は **1 文字も変えない**。

## F-12 / E-4 / E-5

- **F-12**: `.github/workflows/ci.yml` の `cargo test --workspace` に `--features package` を足す
  （⚠️ 付けないと `reconcile` の 34 テストが走らない。★ `ci.yml:204` で実測）。
- **E-4**: `launch-o1-windows.bat` に UTF-8 BOM を付ける（★ G1 の launcher は `efbbbf` で始まる。実測）。
  ⚠️ 改行は `.gitattributes` の `*.bat text eol=crlf` が既に担保している（★ 判断 4 で訂正）。
- **E-5**: `make-common-app-zip.sh --selftest-dump` の持ち物一覧の二重管理を単一化する。

## テスト戦略

- `liveness.rs` に境界テスト（1799 秒 / 1800 秒 / 通常運用は不変 / O1 でも再設置は 120 秒）。
- ゲートの `--selftest` を **22 → 26 件**に増やす（★ 陽性対照と「片方だけ」を含む）。
- ⚠️ **フロントエンドにテストランナーが無い**（`package.json` に vitest 等が無い。実測）。
  → E-1 の機械検査は `tsc` のみ。★ **実機クリック（B-4）は研究者に残る**。
