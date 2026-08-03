# タスクリスト — G1 パイロット P-1 の前日準備

## 準備（完了）
- [x] `protocol.md` / `preregistration.md §2.8 §2.10 §2.11` / `Form_G1/README.md` / `materials/README.md` を読む
- [x] `bash run.sh` を実行して変更前が GREEN であることを確認（V-7）
- [x] `gh release view v0.1.22` でアセットの実体を確認（V-1・**5 件**）
- [x] `v0.1.21..v0.1.22` のアプリコード差分を確認（V-2・kill switch のみ）
- [x] macOS の `open` が環境変数を渡すかテスト用 .app で実測（V-4・**渡る**）
- [x] `productName` を確認（V-5・`gse-next`）
- [x] `validate_materials.py` が `## 資料 N` だけを数えることを確認（教示への追記は ±5% に影響しない）

## 実装（スクリプト）
- [x] `assign.py` に `--pilot-topic N` を追加（既定 1・範囲 1..8・`--pilot` 併用必須）
- [x] `assign.py --selftest` に検査を追加（範囲外 / 非併用 / topic=1 の後方互換）
- [x] `launch-g1-macos.command`（quit → `GSE_DISABLE_PROBES=1 open -a gse-next`・`chmod +x` 済み）
- [x] `launch-g1-windows.bat`（BOM + CRLF + `chcp 65001` を日本語より前・実測で BOM あり / 裸 LF 0）
- [x] `record-sheet-pilot.md`（4 ブロック版・強制比較欄なし）
- [x] `make-handouts.sh` に記録用紙・デブリーフ資料の .docx 生成を足す

## 実装（G-5 手引きの冊子化 / G-6 架空明示とデブリーフ）
- [x] ★ 課題文 16 本の**教示末尾に一律 1 行**「この資料は本実験のために作成した架空のものです」を追加
      （★ `## 資料 N` に入れない = ±5% 制約に影響させない。全題材共通なので条件差を作らない）
- [x] ~~`copy.md` にも同趣旨の 1 行~~ → ★ **対象外にした**（架空の統計を含まない中立文であり、
      「架空」と書くとかえって不正確になる。判断は `materials/README.md §5b` に記録）
- [x] `debrief.md` を新規作成（★ **G1-S の後に渡す**。実在の論点と出典を開示。`sources.md` の被験者向け版）
- [x] `participant-guide.md` を冊子化（表紙・目次・問い合わせ先。⚠️ 冒頭の実験者向け注記は切り取り運用のまま）
- [x] `materials/README.md` に「架空明示を入れた」ことを記録（E-3 の記録義務）

## 文書のズレ是正（★ 判定基準には触れない）
- [x] **Z-2** `protocol.md §6` を P-1 用と確証用に分け、「P-1 では強制比較を取らない」を明記
- [x] **Z-4** `protocol.md §1.1` のアプリ名を `gse-next` に直し、`open -a` の既存インスタンス問題を書く
- [x] `protocol.md §5` に 2 端末 × 2 題材（G-1/G-4）を追記
- [x] `protocol.md` に G-5（1 枚ずつ維持・手引き冊子化）と G-6（架空明示・デブリーフ）を反映
- [x] **Z-1** 引き継ぎ `T-1` を 5 アセット・portable exe に直す／`T-2` のアプリ名を直す
- [x] 引き継ぎ `§2` に「P-1 では G1-M を取らない」を追記
- [x] `env.md` に P-1 の記入枠を 2 回分（OS / 題材 / 実施順 / HMM_VERSION / ビルドタグ）
- [x] `notes.md` に P-1 の節（G-1〜G-6・Z-1〜Z-4）

## 検証
- [x] `python3 validate_materials.py --strict` が緑（★ 架空明示の追加後も ±5% を満たす）
- [x] `python3 assign.py --pilot --pilot-topic 2` が topic02 を出す
- [x] `python3 assign.py --pilot` の出力が**変更前と一致**（後方互換）
- [x] `python3 assign.py --selftest` 緑
- [x] `blocks/PILOT-win.json` / `PILOT-mac.json` を生成し `python3 validate_blocks.py` 緑
- [x] `bash make-handouts.sh` が緑（★ 条件の露出チェックを含む）
- [x] `bash run.sh` が **GREEN のまま**
- [x] ★ `git status` に `blocks/*.json` / NDJSON / CSV / `handouts/` が出ていない

## レビュー
- [x] ★ **自己レビュー**（差分の読み直し）で欠陥 1 件を発見・修正:
      `check_files` の格下げにより `--dataset` でも「実施後の file 転記漏れ」が緑を通る穴が
      生まれていた → `check_dataset` に fail を追加し、★ **その検査が空回りしていないことも実測**
- [ ] code-reviewer / `/cross-review`（★ サブエージェント起動は**研究者の指示待ち**。
      渡すのは git diff のみ・NDJSON 生ログと被験者データを渡さない）
- [ ] HIGH 指摘への対応

## 完了処理
- [x] `decisions.md`（G-1〜G-6・Z-1〜Z-4・凍結に触れないことの論証）
- [x] `design.md` の最終化
- [ ] git commit（★ `blocks/*.json` を含めない）

## ★ 研究者の手作業（本セッションでは代行できない）
- [ ] Apps Script で `setupG1Forms()` を実行 → `listG1FormUrls()` → 実施端末にブックマーク
- [ ] 各フォームの「回答」タブでスプレッドシートへのリンクを作る
- [ ] 管理シート「リンク集」の手動セル（記入パッドの置き場・送付先）を埋める
- [ ] 課題文・手引き冊子・記録用紙・デブリーフ資料を印刷し、課題文は**封筒**に入れる（条件を書かない）
- [ ] 実施端末に `v0.1.22` の本番バイナリを入れる（Win: `gse-next.exe` / mac: `.dmg`）
- [ ] 記入パッドを**拡張機能なしのプロファイル**で開けることを確認する
- [ ] ★ 実施は **08-04 以降**（`protocol.md §5-1`: 課題文作成日と 1 日空ける。課題文は 08-03 生成）
