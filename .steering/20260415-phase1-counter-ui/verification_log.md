# Phase 1 実機手動検証ログ

> **用語**: これは `docs/development-guidelines.md` §3 の **実機手動検証** です。Playwright 等の自動 E2E は含みません。
> 
> **目的**: Task 1 (backend ログ+ホットキー) + Task 2 (metrics CLI) + Task 3 (Dashboard counter) の 3 層が結合して動くことを実機で目視確認する。

## 実行環境

- 日時: _YYYY-MM-DD HH:MM_ (実施時に記入)
- ホスト: _macOS <version> / <chip>_
- ブランチ: main
- Task 1 commit: `461e920`
- Task 2 commit: `71674f2`
- Task 3 commit: _<本ログ記録後に付与>_

## 事前チェック

- [ ] `git log --oneline -3` で Task 1/2 の commit が存在
- [ ] `cd src-tauri && cargo test --workspace` 全 PASS
- [ ] `cd src-tauri && cargo build --target aarch64-apple-darwin` warning 0
- [ ] `npx tsc --noEmit` エラー 0

## 検証手順

### Step 1: 起動 + 権限確認
- [ ] `~/.cargo/bin/cargo tauri dev` で起動
- [ ] (初回のみ) macOS Input Monitoring 権限を付与
- [ ] Dashboard が表示される

実測メモ:
- 起動時間: _< s>_
- Input Monitoring: _granted / pending_
- Accessibility fallback: _true / false_

### Step 2: Counter 初期表示
- [ ] Counter widget が `GT: Flow 0 / Inc 0 / Stuck 0` を示す
- [ ] ショートカット hint (`⌘⇧⌥ F/I/S`) が表示されている

### Step 3: Flow ラベル 1 回目
- [ ] `⌘⇧⌥F` 押下 → Counter `Flow 1`
- [ ] `tracing` ログに `user_label recorded: flow @ <ts>` が出る

### Step 4: デバウンス確認
- [ ] Step 3 直後 (2 秒以内) に再度 `⌘⇧⌥F` → Counter は **1 のまま**
- [ ] tracing に `shortcut label recording failed: debounced (<2s since last label)` が出る

### Step 5: 2 秒以上待って再押下
- [ ] 3 秒待機後 `⌘⇧⌥F` → Counter `Flow 2`

### Step 6: Incubation / Stuck
- [ ] `⌘⇧⌥I` × 1 → Counter `Inc 1`
- [ ] `⌘⇧⌥S` × 1 → Counter `Stuck 1`

### Step 7: セッション終了 + NDJSON 検査
- [ ] 「セッション終了」ボタンで正常終了
- [ ] `~/Documents/GSE-sessions/gse_YYYYMMDD_HHMMSS.ndjson` を特定
- [ ] meta 行に `"hmm_version":"0.2.0"` が含まれる（**Phase 0 条件 5 消化**）
- [ ] `{"type":"user_label","t":...,"label":"flow",...}` が 2 件
- [ ] `{"type":"user_label","t":...,"label":"incubation",...}` が 1 件
- [ ] `{"type":"user_label","t":...,"label":"stuck",...}` が 1 件

確認コマンド:
```bash
grep '"hmm_version"' ~/Documents/GSE-sessions/gse_*.ndjson | tail -1
grep '"type":"user_label"' ~/Documents/GSE-sessions/gse_*.ndjson | tail -10
```

### Step 8: `--metrics` pretty-print
- [ ] `cd src-tauri && cargo run --bin gse-replay -- <session> --metrics`
- [ ] SessionMetrics 出力が `Total labels: 4 (Flow:2, Inc:1, Stuck:1)` を示す
- [ ] warning が出ていても許容（実セッションの F/I/S は HMM と一致しない可能性が高い）

### Step 9: `--metrics --json`
- [ ] 同コマンド + `--json` で構造化 JSON が stdout に出る
- [ ] `jq '.total_labels'` 等が動く

### Step 10: 回帰確認
- [ ] `cargo run --bin gse-replay -- tests/fixtures/minimal.ndjson --snapshot tests/snapshots/minimal.json` で `OK: 15 snapshots match`

## 結果サマリ

- 全ステップ PASS: _Y / N_
- ブロッカー: _none / <内容>_
- 所要時間: _<分>_
- セッションファイル: _<path>_（Phase 2a 集計用に `.steering/20260415-phase1-ground-truth/baseline_metrics.md` に記入）

## 追加観察

> 想定外の挙動・改善アイデアはここに記録する。
