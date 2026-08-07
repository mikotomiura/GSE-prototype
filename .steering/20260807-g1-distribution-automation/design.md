# design — G1 配布の自動化

決定は `decisions.md`（D-1〜D-5）。ここは「どう作るか」だけを書く。

## 1. 全体の流れ（★ 人が押す所を 2 か所に閉じる）

```
G1-C 提出 → onG1ConsentSubmit（自動: P-ID 採番 / 行追加 / 受付メール）
   ↓
[人] python3 assign.py --subject P0XX && python3 validate_blocks.py   ← ★ 割付は自動化しない (§3-1)
   ↓
[人] ./make-distribution.sh P0XX both                                  ← 既存・変更しない
   ↓
[機械] 課題ページを Drive へ置く（Claude + Drive MCP）
        make-upload-manifest.sh → create_file(base64) × N → verify-drive-upload.py
   ↓
[人] 出たフォルダ URL を「G1 実施トラッキング」の「配布フォルダURL」列に貼る  ← ★ 唯一の手入力
   ↓
[機械] 時間トリガー g1AutoSendPendingMaterials() が拾って事前資料メールを送る
```

⚠️ ★ 割付 (`assign.py`) は**意図的に**この鎖に入れない（`§3-1`）。
seed を使う科学的な行為であり、取り違えると「同じ人に 2 通りの割付」が黙って生まれる。

## 2. 変更対象

| ファイル | 変更 |
|---|---|
| `experiments/.../dist-readme-macos.txt` | 分割配布に合わせて書き直す。★ `§2.13`/`§2.14-2` の 3 指示は残す (D-4) |
| `experiments/.../make-upload-manifest.sh` | ★ 新規。課題ページの base64 と期待 byte 数を出す |
| `experiments/.../verify-drive-upload.py` | ★ 新規。Drive のメタデータ JSON と manifest を突き合わせる |
| `Form_G1/GSE_G1_Form_Builder.gs` | `RUN_HEADER` に列追加 + 移行関数 + 自動送信トリガー + ガード |
| `Form_G1/README.md` | 運用手順を追記 |

⚠️ ★ `make-distribution.sh` は触らない（`§7`）。

## 3. Drive 配置

親: `GSE_ユーザー検証_G1_アプリダウンロードリンク` = `1FDkU52n9EXO92TzCieivexg7WKsXHkFP`

- 共通 Windows `1MIbhx5sFSXz2CUCWU2MyY4S8bD-686Xi`（6 件。★ byte 照合済み 2026-08-07）
- 共通 macOS `1yY6ydzDFD8FANzF1aXbNMpG2MjzQvGhC`（4 件。dmg 10,220,785 B 一致。
  ⚠️ README は差し替えが要る = D-4）
- ★ 新規 `課題ページ_被験者別/<P-ID>/`

**アップロードの型**: `create_file` に `base64Content` + `disableConversionToGoogleType: true`。
⚠️ ★ `textContent` は使わない。中身次第でバイトが化ける既知問題があり
（`drive-mcp-upload-fidelity`: エスケープ列を含む HTML で 44B 欠損を実測）、
block ページは `writing-pad.html` 由来の JS を含む。
⚠️ ★ MCP に**更新・削除のツールが無い**ので、間違えると重複が残る。→ 上げる前に manifest を出し、
上げた後に `fileSize` を照合し、**1 件でも合わなければリンクを発行しない**（AC-2）。

**手動フォールバック**: Drive 画面へフォルダをドラッグしても等価である。
その場合も `verify-drive-upload.py` で照合してから URL を貼ること。

## 4. Apps Script

### 4-1. 列の追加（⚠️ `setupG1Forms()` は実行しない）

`RUN_HEADER` の「課題文リンク送信日」の**直前**に `配布フォルダURL` を挿す。

⚠️ ★ `runCol_` は**コード側の `RUN_HEADER` しか見ない**（`.gs` のコメントに実害の記録あり:
2026-08-03 に 16 列のシートへ 17 列の定義で回して「実施日」に「はい/いいえ」が付いた）。
→ コードだけ変えると実シートと 1 列ずれる。**移行関数 `migrateRunSheetAddUrlColumn()` を用意し、
実シートに列を挿してから**使う。`assertRunHeader_` が不一致で止まるので黙ってずれない。

### 4-2. 自動送信

```
g1AutoSendPendingMaterials()   ← 時間トリガーが呼ぶ（引数なし）
  for 各行 in G1 実施トラッキング:
    ✓ P-ID がある
    ✓ 配布フォルダURL が https://drive.google.com/ で始まる      … ガード 1
    ✓ 課題文リンク送信日 が空                                    … ガード 2（冪等）
    ✓ Phase1 ロスターからメールが引ける（引けなければ備考にフラグ）
    → sendTaskMaterialsEmail(pid, email, url) を呼ぶ（既存を再利用・本文は変えない）
  ★ 1 回の発火で送るのは最大 G1_AUTO_SEND_MAX_PER_RUN(=3) 人             … ガード 3
  ★ Script Properties G1_MATERIALS_AUTOSEND_OFF が真ならば即 return      … ガード 4
```

- `previewPendingTaskMaterials()`（送らずに対象だけログに出す）を必ず併設する
- `installMaterialsAutoSendTrigger()` / `removeMaterialsAutoSendTriggers()` を用意する
- ★ 本文 (`g1MaterialsBody_`) は**変えない**。`scripts/check_g1_emails.py` の基準を跨がない

## 4-3. ⚠️ 失敗の可視化

`onG1ConsentSubmit` と同じ流儀で、送信に失敗したら「備考」列にフラグを立てる。
黙って落とすと「URL は貼ったのに永久に届かない」状態が見えなくなる。

## 5. テスト戦略

★ Rust/TS を触らないので `cargo test` は無関係（回帰の対象外）。検証は次で行う:

| 何 | どう検証するか |
|---|---|
| GAS のガード | `Form_G1/guard_test.cjs` と同じ流儀で node 実行できる単体テストを足す |
| メール本文 | `python3 scripts/check_g1_emails.py`（題材名・提示順の混入検査） |
| アップロード | `verify-drive-upload.py` が Drive メタデータと manifest を byte 比較 |
| README | 復活させた 3 指示が入っていることを grep で機械検査 |
