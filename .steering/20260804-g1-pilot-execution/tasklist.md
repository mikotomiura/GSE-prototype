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

## ★★ 実動作検証（2026-08-03・ブラウザ自動化で実施）

### T-1 Apps Script（★ 全部 **実際に動かした**）
- [x] Apps Script プロジェクト `GSE_Gate1` に現行 `.gs` を貼り、保存
- [x] 権限承認（Forms / Spreadsheet / Gmail）が通る
- [x] `setupG1Forms()` 完了。★ **3 フォームの公開 URL は変わらない**（固定 ID 方式の実証）
- [x] `previewRegisterAckEmail()` で本文確認 → ★ **バグ 1 件を発見して修正**（下記 J-1）
- [x] `installG1ConsentTrigger()` 完了（`G1_AUTO_SEND=true`）
- [x] ★ **G1-C に実提出 → `onG1ConsentSubmit` がトリガー経由で完走**（6.1 秒）
      - `♻️ 既存の参加者として扱います: P006（m***@gmail.com）` = **冪等が実地で効いた**
      - `📧 受付メールを送信しました` / `🔁 再提出（発番なし）: P006`
      - ★ `maskEmail` が実ログで効いている（クラウドに実アドレスが残らない）
- [x] ★ **G1 実施トラッキングの列ズレを発見**（下記 J-2）→ 修正 → 実物が正しくなったことを確認
- [x] ⚠️ テスト行（P006）を削除して後片付け

⚠️ ★ **やっていないこと（正直に残す）**:
- [ ] **新規採番経路（P015 の発番）は未検証**。研究者判断で既存アドレスのみ使ったため、
      `g1NextParticipantId_` → `roster.appendRow` の枝は**一度も通っていない**
- [ ] **受付メールの「着信」は未確認**。MailApp が例外なく返ったことしか分からない
      （連携中の Gmail は別アカウントで、送信先 `mmiura.network@gmail.com` を読めない）
- [ ] G1-C の**テスト回答 1 件がフォームに残っている**（★ データ削除はしていない。研究者が判断する）
- [ ] STEP 8（各フォームの回答をスプレッドシートに繋ぐ）は未実施。★ **G1-M は必須**

### T-2 ブロックページ（★ 全項目クリア）
- [x] 課題文が読める・記入欄に打てる（`block02.html` を実ブラウザで表示）
- [x] ★ 文字数カウントが `count_chars` と一致（`"あいう えお\nかき　く🙂ab"` → **JS 11 / Python 11**）
- [x] ★ 課題文をコピーできない（トリプルクリック **選択 0 文字** / ★ **Cmd+A でも課題文が入らない**）
- [x] ブロック番号が埋まっていて編集できない（`readOnly`・`9` を打っても `2` のまま）
- [x] タブのタイトルが「G1 ブロック 2」（題材名なし）。★ ソース全文に `_hi`/`_lo`/`topic0` なし
- [x] 「消去して次のブロックへ」で本文が消え、カウンタが 0 に戻り、フォーカスが記入欄へ
- [x] 課題文パネルがスクロールして資料 3 の末尾まで到達する（313px 枠 / 内容 710px）
- [x] 外部リソース 0 件（`script[src]`/`link`/`img`/`iframe` = 0）
- [ ] ⚠️ ★ **`file://` そのものでは未確認**。拡張機能が `file://` を触れないため `http://127.0.0.1` で検証した
      （このページは fetch / storage / 外部リソースを一切持たないので差は出ないはずだが、**確かめてはいない**）
- [ ] ⚠️ **拡張機能なしのプロファイルでは未確認**（検証には拡張機能が要るため）

### T-3 Windows launcher
- [ ] ⚠️ ★ **1 つも実施していない**（Windows 実機が要る）。`.bat` の文字化け・`gse-next.exe` の起動・
      `taskkill` 検証ロジックは**すべて未検証のまま**

## ★ 研究者の手作業（本セッションでは代行できない）
- [ ] ★★ **T-3（Windows launcher）を実機で試す**
- [ ] 各フォームの「回答」タブでスプレッドシートへのリンクを作る（★ **G1-M は必須**）
- [ ] 管理シート「リンク集」の手動セル（ブロックページの置き場・送付先）を埋める
- [ ] 手引き冊子・記録用紙・デブリーフ資料を印刷する（⚠️ **課題文は印刷しない**・画面提示）
- [ ] 実施端末に `v0.1.22` の本番バイナリを入れる（Win: `gse-next.exe` / mac: `.dmg`）
- [ ] ブロックページを**拡張機能なしのプロファイル**で開けることを確認する
- [ ] `consent.md §8` の**倫理審査 承認番号**を埋める（★ 確証実施の前に。D-1 は媒体の決定であって審査完了ではない）
- [x] ★ 実施日を **08-04** に決定（D-2・`protocol.md §5-1` の「1 日空ける」を満たす）
