# ビルダーの配備設定を **スクリプト プロパティ**へ移す

## 背景

★ 受け口とビルダーで**設定の持ち方が食い違っていた**（一次資料で確認）:

| ファイル | 設定 |
|---|---|
| `Form_O1/GSE_O1_Submit.gs` | ✅ `PropertiesService`（`FOLDER_ID` / `SHARED_SECRET`） |
| `Form_O1/GSE_O1_Form_Builder.gs` | ❌ **`.gs` 内の `var` 直書き**（研究者がファイルを編集して埋める） |

⚠️ 直書きが危ないのは 3 つ:

1. **配備のたびに `.gs` を書き換える** → ★ **repo のコードと Apps Script 上のコードが必ず食い違う**
   （★ この repo が繰り返し踏んでいる「直したはずが配備物に届いていない」の形）
2. `O1_APP_DOWNLOAD_URL` は **T-15 と同じ形** —— ★ 配布フォルダは「リンクを知る全員=閲覧者」で、
   ⚠️ その中に提出設定（共有シークレット）が入りうる
3. `PHASE1_MGMT_SHEET_ID` は **参加者 PII への直接ポインタ**

## ゴール

★ 「環境ごとに変わる / 秘密・PII を指す」値だけをスクリプト プロパティへ移し、
⚠️ **安全装置と機械検査はソースに残す**。★ 戻ってこないようにゲートで機械的に止める。

## スコープ

### 含むもの（★ 研究者判断 2026-08-29）
- プロパティへ: `FORM_ID_O1_CONSENT` / `FORM_ID_O1_SURVEY` / `O1_APP_DOWNLOAD_URL` / `PHASE1_MGMT_SHEET_ID`
- ソースに残す: `G1_FORM_IDS_DO_NOT_TOUCH`（**安全装置**）/ `O1_CONTACT_*`・保管上限・設問文
  （**同意文書との一致を機械検査**）/ `O1_AUTO_SEND`・`O1_ALLOW_REBUILD_WITH_RESPONSES`（fail-closed 既定）
- 98 ケース検査 / 変異テスト / ゲート / 配備手順書の追随

### 含まないもの
- ⚠️ **`Form_G1/GSE_G1_Form_Builder.gs` は 1 バイトも触らない**（★ 研究者判断: G1 実施中）

## ⚠️ 移してはいけないもの（★ 判断の核）

**`G1_FORM_IDS_DO_NOT_TOUCH` をプロパティにすると、⚠️ 未設定＝拒否リストが空＝防波堤が黙って無効になる。**
★ これは 2026-08-07 に G1-C の全設問が消えた事故の再発防止そのものなので、
**コードと一緒に運ばれなければならない**。

## 受け入れ条件

- [x] `.gs` に配備固有の値が 1 つも残っていない（★ 実 ロスター ID も削除）
- [x] `node Form_O1/o1_form_builder_test.cjs` が緑（96 → **98 ケース**）
- [x] `bash Form_O1/o1_form_builder_mutation_test.sh` が **全変異赤**（25 → **26**）
- [x] `bash scripts/check-o1-release-readiness.sh` が **通過 16 / 未達 1**（15 → 16）
- [x] `--selftest` が全件通過（31 → **33**）
- [x] ⚠️ ゲートが「ビルダーへの直書き」を**実際に赤にする**ことを実測で確認
- [x] 配備手順書（runbook §2 / §3）が新しい形になっている
