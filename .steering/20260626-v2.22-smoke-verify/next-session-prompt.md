# 次セッション用 開始プロンプト（v2.22 本番ビルド実機スモーク検証 + Google Form 実動作確認）

> このファイル本文を新しいセッションの最初に貼る。GSE-prototype 用。
> 実装ではなく**検証フェーズ**。`.steering/` に検証記録を残す。OS 固有の実機確認が主。

## 0. 一言ゴール
**v2.22（macOS 介入オーバーレイのクリック受理修正 + プローブ窓クランプ修正）と Google Form ビルダー
修正は main にマージ済み。残りは「本番ビルドでの実機スモーク検証」と「Google Form の実動作確認」。**
コード修正は不要（バグが出たら別途対応）。検証して合否を `.steering/` に記録し、必要なら follow-up を切る。

## 1. ここまでの確定事実（マージ済み・触らない）
- main HEAD = `01139a1`（PR #37/#38/#39 すべてマージ済み・open PR なし）。app version 0.1.12。
- **クリック無反応バグ解決**: overlay を非アクティブ NSPanel 化（`src-tauri/src/overlay_panel.rs`）+
  capability に `allow-set-size`/`allow-set-position` 追加（★主因 D11）+ Rust 権威
  `set_ignore_mouse_events`（D9）+ `resign_key_window` でフォーカス非奪取（D12）+ idle hide 廃止（D10）+
  maximize 撤去（D8）。
- **「記録に失敗」解決**: 真因は log channel ではなく `self_marker_window_clamped`（probe_scheduler.rs）の
  **窓終端未クランプ**。起動 5s 以内のプローブ/マーカーで `window_end_ms < window_start_ms` に反転し
  `record_realtime_*` の検証で弾かれていた。`we = we.max(ws)` で修正・回帰テスト追加。
- **Google Form 修正**: `buildForm` 再実行時の `Invalid data updating form` を `clearForm`
  （削除前に分岐ナビゲーション解除）で解消。`Form_Phase1/GSE_Phase1_Form_Builder.gs`。
- 機械的検証は全 green 済み: `cargo test --lib` 228 passed / `gse-replay --snapshot` 一致（HMM 不変）/
  `tsc --noEmit` 0。dev 実機で部分確認済み: クリック効く・記録着地（起動 3.0s でゼロ幅窓 OK）・
  フォーカス非奪取（isKeyWindow=false）。

## 2. ★今回やること（検証のみ）
**検証の単一起点 = `docs/verification-runbook.md`。これを上から実行する。**

### A. macOS 本番ビルド実機スモーク（§2 + §1 自動回帰の再確認）
- 本番ビルドで起動（dev で確認済みでも本番で最終確認）:
  ```bash
  VITE_GSE_DEBUG=1 npm run tauri build
  GSE_DEBUG=1 "src-tauri/target/release/bundle/macos/<App>.app/Contents/MacOS/<bin>"
  #   ※ `open` は env を渡さないのでバイナリを直接起動する
  ```
- 未確認の重点項目（dev では軽くしか見ていない）:
  - **§2.3 Wall 全画面ブロック非回帰**: Wall 発火→全画面ブロック→QR→Zen Timer→unlock の full flow。
    NSPanel 化窓で `maximize()` 禁止（D8・NSRangeException）なので明示 setSize/setPosition で全画面に
    なっているか、クラッシュしないか。
  - **§2.4 日本語 IME 合成非回帰**: ローマ字→変換→確定。panel level=Floating が IME をブロックしないこと。
  - **§2.2 記録着地の再確認**: 起動 5s 以内/以降の両方でプローブ→回答→`realtime_label` が
    `~/Documents/GSE-sessions/gse_*.ndjson` に着地（5s 以内はゼロ幅窓 start==end）。
  - macOS 26（Tahoe）で wry #1576 系クラッシュが無いこと。

### B. Windows 実機スモーク（§3・差分のみ）
- overlay の NSPanel 化は **macOS gate**。Windows は従来 `set_ignore_cursor_events` 経路。
- プローブ/Nudge クリック・起動直後の記録着地（窓 clamp は OS 非依存）・Wall・IME(IMM) の非回帰。

### C. Google Form 実動作確認（§4）
- 更新後の `Form_Phase1/GSE_Phase1_Form_Builder.gs` を Apps Script エディタに**貼り直す**。
- `buildForm` を**2 回連続実行**して `Invalid data updating form` が出ないこと（clearForm の効果）。
- `buildF5` を**単独実行**して事後アンケートが生成されること（一括 `buildAllSupportForms` は
  実行時間/クォータに当たりやすいので単独推奨）。
- F2-B/F5 の GSE-10 と F2-C/F5 の `TSE_ITEMS` が pre/post で完全一致（matched 再測定の前提）。

## 3. 参照ドキュメント（先に読む）
- `docs/verification-runbook.md` — ★検証の単一起点（§1 自動 / §2 macOS / §3 Windows / §4 Form / §5 trouble）。
- `.steering/20260625-macos-overlay-clickthrough-fix/runbook.md` — overlay クリック修正の実機手順。
- `.steering/20260625-macos-overlay-clickthrough-fix/investigation-record-failure.md` — 記録失敗の真因詳細。
- `.steering/20260625-macos-overlay-clickthrough-fix/decisions.md` — D7〜D13 の設計判断。
- メモリ `macos-overlay-clickthrough-bug.md` — 解決済み（capability+NSPanel / D13 窓反転）の単一真実源。

## 4. 制約（厳守）
- 非ブロック維持（カード外は背後へ透過）+ フォーカス非奪取（D12）。Wall 全画面ブロック非回帰。
- panel level は **Floating 固定**（高 level は日本語 IME をブロックする・nspanel #104）。
- NSPanel 化窓で **maximize/unmaximize/fullscreen トグル禁止**（D8）。全画面は setSize/setPosition。
- Windows 非回帰（nspanel は macOS gate）。HMM / `schema_dto.rs` 不変。
- `winapi`/`println!`/`eprintln!`/`any` 禁止。既存テスト無断削除しない。
- diff に無関係な未ステージ変更を混ぜない（コミットは対象ファイル列挙・`-A` 禁止）。

## 5. 未処理の保留（把握しておく）
- **`git stash@{0}`** に無関係な既存変更が保全されている（`budget.json`/`advice.md`/
  `scripts/run-codex-consult.sh`/`scripts/secrets-filter.sh`/設計 docs 2件の削除（計 962 行）/`MEMO`/各種 .lock）。
  → **設計 docs 2件の削除が意図的か未確認**。不要なら `git stash drop`、必要なら選別して別 PR。
- 本番ビルド smoke で不具合が出たら、それが次の実装タスク（このセッションは検証が主）。

## 6. 起動時の行動（CLAUDE.md 準拠）
1. このプロンプト + `docs/verification-runbook.md` を読む。
2. 検証なので `.steering/20260626-v2.22-smoke-verify/`（本ファイルの dir）に検証結果を記録する
   （requirement/tasklist は軽量で可。合否と発見した不具合を残す）。
3. 実機操作はユーザー（研究者）が行う。エージェントは手順提示・ログ解析・不具合の切り分け・
   修正提案を担う。NDJSON 解析は `log-analyzer` サブエージェントが速い。
