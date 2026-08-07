# tasklist — G1 配布の自動化

## 1. macOS README の修復（D-4）
- [x] `dist-readme-macos.txt` を分割配布に合わせて書き直す
- [x] `§2.13`/`§2.14-2` の 3 指示が残っていることを grep で確認（欠落 0）
- [x] 再生成して byte 数を確認（3,470 → 4,251 B）
- [x] ★ Drive の旧 README を削除 → 新版を配置（4,251 B・ローカルと byte 一致を実測）

## 2. 課題ページの Drive 配置
- [x] `G1/G1_課題ページ_被験者別/` を作成（`1qhl28IDeh-19upuZf_YxPwwdq_d9xVcI`）
      ★ 親「アプリダウンロードリンク」の**外**に置いた（他被験者の割付が見えるため・§2.12）
- [x] `make-upload-manifest.sh`（base64 + 期待 byte 数 + Win/mac の同一性検査）
- [x] `verify-drive-upload.py`（照合・1 件でも不一致なら rc=1）
- [x] PILOT-win で実走（4 枚の manifest 生成 ✅）
- [x] ⚠️ 壊れた入力で rc=1 を実測（合成 5 パターン: ok=0 / -44B=1 / 欠落=1 / 変換=1 / 余分=1）
- [x] ★ 実 Drive で実測: 部分アップロード → rc=1 / 完全一致 → rc=0
- [x] ★ base64 経路のバイト忠実性: `fileSize` 9519 = ローカルと一致、`text/html` のまま
- [x] ⚠️ ★ 方針変更 (D-7): 親は**制限付き（非公開）**にした。owner のみであることを実測
- [ ] ★ 人: 被験者フォルダを作るたびに、そのフォルダだけ「リンクを知っている全員（閲覧者）」にする
- [x] ★ 疎通試験の残骸 `PILOT-win/` を削除（親フォルダが空であることを実測）

## 3. Apps Script（D-3）
- [x] `RUN_HEADER` に「配布フォルダURL」を追加（方針転換の理由をコメントに明記）
- [x] `migrateRunSheetAddUrlColumn()`（列を**挿す**・冪等・見知らぬ形なら止める）
- [x] `g1AutoSendPendingMaterials()` + ガード 4 本
- [x] `previewPendingTaskMaterials()`（送らない）
- [x] `installMaterialsAutoSendTrigger()` / `removeMaterialsAutoSendTriggers()`
- [x] ★ cross-review の指摘でガード 5（URL 重複）・6（LockService）を追加（D-6）
- [x] ★ 送信後に送信日を読み直す後始末を追加（「送れたのに記録が無い → 再送」を潰す・D-6）
- [x] node 単体テスト `materials_autosend_test.cjs` — 36 項目緑（★ 陽性対照込み）
- [x] `python3 scripts/check_g1_emails.py` 緑（列参照・開示範囲とも一致）
- [x] 既存テスト非回帰: `guard_test.cjs` 4/4 ・ `submit_guard_test.cjs` 33/33
- [x] ★ `GSE_Gate1` に最新 `.gs` を貼り直し、DriveApp スコープを再承認、
      `migrateRunSheetAddUrlColumn()` / `previewPendingTaskMaterials()` /
      `installMaterialsAutoSendTrigger()` を実行（2026-08-07・ユーザー報告）
      ★ 列が入っていることは管理シートを読んで独立に確認済み

## 4. 記録と引き継ぎ
- [x] `Form_G1/README.md` に運用手順を追記
- [x] `.idea/短縮版リンク集.md` に新フォルダを記録（⚠️ gitignore 済み）
- [x] `/cross-review`（Claude + Codex 並列・指摘 4 件すべて採用 → D-6）
- [x] `make-upload-manifest.sh` の nullglob（D-6 #4）
- [x] ★ D-7: 親を非公開に戻し、ガード 7（フォルダ実体の検査）を追加（commit ed383e8）
- [ ] ⚠️ `git push` は deny。ユーザーに `! git push` を打ってもらう

## ⚠️ 見つけたが直していないこと（別タスク）
- `GSE_G1_Form_Builder.gs` の「`scripts/check_g1_topic_titles.py` が検査する」というコメントは
  **そのファイルが存在しない**（実在するのは `check_g1_emails.py`。検査内容は同等）
- 同一端末を 2 人が使うと `~/.gse/g1_participant_id` が前の人の値のまま残る（`lib.rs:1113`）
- `g1-submit.json`（共有シークレット）が `anyone: reader` のフォルダにある（D-2 で現状維持と決定）
