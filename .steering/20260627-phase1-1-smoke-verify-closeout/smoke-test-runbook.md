# 実機スモークテスト 手順書（研究者作業）

> Claude は実キーボードフック＋OS 権限（TCC）を伴う実行ができないため、本手順は
> **研究者が手元の Mac / Windows で実施**する。#1 最有力原因（macOS Documents/TCC で
> `File::create` 失敗）は **本番ビルドの .app/.dmg でこそ顕在化**するため、必ず本番ビルドで行う。

## 0. 機械的検証（Claude 実施済み・2026-06-25 / main）
- `cargo test --lib` … ✅ pass
- `cargo run --bin gse-replay -- … --snapshot tests/snapshots/minimal.json` … ✅ pass（HMM 不変）
- `tsc --noEmit` … ✅ pass
→ マージ済みコードはビルド・型・回帰健全。残りは TCC を伴う実機確認のみ。

## 1. デバッグビルドの起動（二重 gate を両方 ON）
デバッグトリガ（force_probe / force_nudge / force_wall）は **2 つの env** が必要:
- `VITE_GSE_DEBUG=1` … ビルド時（フロントにボタン描画）
- `GSE_DEBUG=1` … 実行時（backend が `ensure_debug_enabled()` で許可）

### macOS
```bash
# 本番ビルド（VITE フラグはビルド時に焼き込む）
VITE_GSE_DEBUG=1 ~/.cargo/bin/cargo tauri build --bundles dmg   # または CI の macos-dmg 成果物
# ⚠ `open App.app` は env を渡さない → 実体を直接起動して GSE_DEBUG を渡す
GSE_DEBUG=1 /Applications/GSE.app/Contents/MacOS/<bin名>
#   または: launchctl setenv GSE_DEBUG 1 してから通常起動
```
### Windows
```powershell
$env:VITE_GSE_DEBUG=1; npx tauri build --bundles nsis   # または CI の windows-nsis
$env:GSE_DEBUG=1; .\GSE.exe
```

## 2. 権限付与（macOS のみ・初回）
- 起動後「Input Monitoring 権限を付与してください」バナー → System Settings で許可 → **アプリ再起動**。
- ad-hoc 署名のため自動付与が効かない場合は Accessibility フォールバックの手動追加手順に従う。

## 3. #1 経路の能動テスト（デバッグボタン）
セッション開始後、Dashboard 下部のデバッグボタンで:
1. **「プローブ強制」** → ProbeCard 表示 → 回答ボタン → **カードが閉じる**ことを確認。
   - 閉じない場合、DevTools(Cmd+Opt+I)の `record_realtime_answer` エラー行を確認:
     **"...full channel" か "...disconnected channel" か** を記録（= 層2 の Full/Disconnected 確定情報）。
   - Skip ボタンでも同様（`record_realtime_skip`）。
2. **「Nudge 強制」** → Overlay の Nudge → dismiss → `record_intervention_dismiss` でカードが閉じる。
3. **「Wall 強制」**（`force_wall`） → Lv2 Wall 表示 → unlock 動作確認。

## 4. ログ健全性（fail-loud）の確認
- 正常時: `~/Documents/GSE-sessions/...`（または `$GSE_DATASET/raw/<pid>/`）に NDJSON が生成され、
  上記操作の `record_*` 行が追記されること。
- **fail-loud 検証**: わざと書込不可状況を作る（例: `GSE_DATASET=/nonexistent/path` で起動、
  または macOS Documents アクセス未許可のまま本番 .app 起動）→ Dashboard 上部に
  **⚠ バナー（「ログを一時フォルダに保存しています」/「ログを保存できません」＋保存先パス）** が出ること。
  → 静かな全損が撲滅されている証拠。バナーが出ずカードも閉じないなら層2 が未到達＝要追加調査。

## 5. 盲検（第2週ブラインド）の確認
- 週セレクタで第2週（`calibrationMode=false`）を選択し、**VITE_GSE_DEBUG を OFF**（被験者相当）で起動 →
  推定状態/確率/GT/状態説明が **一切表示されない**こと（`showModelOutput=false`）。
- VITE_GSE_DEBUG=1 のときのみモデル出力が出る（研究者デバッグ）。

## 6. 結果の記録
- 各ボタンの開閉可否、`record_*` の NDJSON 残存、fail-loud バナーの有無、
  （失敗時）DevTools エラー文字列（Full/Disconnected）を `.steering/` か本タスクに追記。
- "disconnected" だった場合 → 層2 修正が直撃で当たる想定。"full" だった場合 → 真の backlog 対策
  （容量/drain 律速）を別 follow-up で検討（前タスク decisions 判断1 の見直し条件）。
