# 次セッション用 開始プロンプト（被験者管理の自動化：F1→P-ID自動発番＋自動メール ＋ 管理シート拡充）

> このファイル本文を新しいセッションの最初に貼る。GSE-prototype 用。
> 主対象は `Form_Phase1/GSE_Phase1_Form_Builder.gs`（Google Apps Script）。アプリ本体(Rust/TS)は触らない想定。
> 実機操作（GAS 実行・トリガ設定・メール送信テスト）はユーザー（研究者）。エージェントは .gs 実装＋手順提示＋検証。

## 0. 一言ゴール
被験者番号(P-ID)付与と被験者管理を **手動運用から半自動/自動運用へ** 引き上げる。具体的には
(1) **F1 同意フォーム提出をトリガに P-ID を自動発番し、本人へ自動メール**、
(2) **管理スプレッドシートでの具体的な被験者管理**（フォーム回答の取り込み・進捗ダッシュボード・検証）。

## 1. ここまでの確定（マージ済み・触らない前提）
- `Form_Phase1/GSE_Phase1_Form_Builder.gs`（main・最新）に以下が実装済み:
  - フォーム生成: `buildForm`(F1 同意・固定ID) / `buildF2`(事前) / `buildF4`(セッション後) / `buildF5`(事後・固定ID)。
    `buildF3` は **廃止・フォールバック専用**（プローブ回答は in-app ProbeCard が正規ルート）。
  - `clearForm`: buildForm 再実行時の "Invalid data updating form"（分岐ナビ orphan）を解消済み。
  - 管理シート: `buildManagementSheet()`（タブ=リンク集/参加者ロスター/セッション提出トラッキング）、
    `setupPhase1Forms()`（一式一括）、`recordFormUrl`（各 build が URL を Script Properties に記録）。
  - **P-ID 連番採番（手動）**: `addParticipant()` が「参加者ロスター」に次の一意 `P###`（P001→P002…ゼロ埋め）を発行。
    `nextParticipantId_()` が既存最大+1 を計算。
  - Dropbox File Request URL 配線: `DROPBOX_FILE_REQUEST_URL`（/request/ 形式・提出専用）。公開鍵(pubkey.txt)セルも明確化済み。
- バージョンは 3 ファイル + lockfile を **0.1.21** に統一済み。
- 現状の P-ID 付与フロー = 「被験者 F1 提出 → 研究者が手動で `addParticipant()` → 本人へ手動メール」。

## 2. ★今回の実装（GAS）
### Task 1: F1 提出トリガで P-ID 自動発番＋自動メール
- **トリガ**: F1 フォーム（`FORM_ID`）に **installable な `onFormSubmit` トリガ**を設定する関数 `installF1Trigger()` を追加
  （`ScriptApp.newTrigger('onF1Submit').forForm(FORM_ID).onFormSubmit().create()`、二重作成防止に既存トリガ削除）。
- **ハンドラ `onF1Submit(e)`**:
  1. 回答から **適格性判定**（Q3 年齢=18歳以上 or 保護者同意提出済み / Q6 IME=はい / Q7 OS=Windows|macOS / Q1・Q2 同意チェック）。
     不適格・非同意なら **発番しない**（ログだけ残す）。※ F1 の分岐は SUBMIT 終了するが「提出イベント」は飛ぶので回答値で判定する。
  2. 適格なら `nextParticipantId_()` で **P-ID 発番** → 「参加者ロスター」に行追加（氏名/メール/OS/同意日/条件 を回答から転記）。
  3. **本人へ自動メール**（`MailApp.sendEmail` or `GmailApp`）: P-ID ＋ 次ステップ（アプリ入手・gse-package コマンド例
     `gse-package --participant P0XX --recipient pubkey.txt`・pubkey.txt 入手先・Dropbox File Request URL）。
     メール本文はテンプレ定数化。送信先は F1 Q8（メール）。
  4. **冪等性**: 同一メール/同一回答の二重発番を防ぐ（既ロスターに同メールがあればスキップ）。
- **判断ポイント（要ユーザー確認）**:
  - 完全自動メール送信 vs 「発番＋下書き作成（研究者が確認して送信）」。研究倫理的には後者が安全。既定提案=**下書き(createDraft)案**も用意。
  - 条件(condition=baseline/intervention)の割付ロジック（手動 / 交互 / ランダム）。Phase1 は単群なので既定 baseline で良いか確認。
- **GAS 権限**: Forms トリガ + Spreadsheet + Gmail/Mail 送信スコープ（初回承認）。

### Task 2: 管理スプレッドシートでの具体的な被験者管理
- **フォーム回答の取り込み**: F2/F4/F5 の回答（各フォームの response sheet）を **P-ID キーで参照**し、ロスターの
  「F2事前/F4回答(計)/F5事後/セッション数」を自動更新する関数 `refreshRosterStatus()`（手動実行 or 時間トリガ）。
  - 各フォームは「回答先スプレッドシート」を持たせる（`form.setDestination` or 既存リンク）。P-ID 列で COUNTIFS 集計 or GAS 集計。
- **進捗ダッシュボード**: 完了率・未提出者・**MNAR 観点の無回答フラグ**（プローブ/フォーム無回答率）をサマリタブに。
- **データ検証**: ロスターの condition/OS 列に**ドロップダウン**（DataValidation）、P-ID の形式・重複チェック。
- **撤回/除外**: 「撤回/除外」列を立てたら集計・配布対象から外す運用（フィルタ/条件付き書式）。
- **対応表の保護**: 実名↔P-ID 対応表（ロスター）は **研究者のみ**。共有設定の注意書きをシートに明記（data-privacy / pilot-runbook §0）。

## 3. 先に読む
- `Form_Phase1/GSE_Phase1_Form_Builder.gs`（実装本体・既存関数を再利用）
- `Form_Phase1/GSE_GoogleForm設問草案.md`（F1〜F5 の設問・適格性条件・P-ID 運用）
- `docs/pilot-runbook.md`（P-ID/対応表/Dropbox/.age/metrics の運用フロー・§0 プライバシー）
- メモリ MEMORY.md（管理シート/Dropbox/P-ID 連携の到達点）

## 4. 制約（厳守）
- **P-ID 形式**: 英数字16字以下・Windows 予約名不可（`logger.rs is_valid_participant_id` ＋ `package.rs` の両方を満たす）。
  `_`/`-` は gse-package で不可 → 使わない。連番 `P###` を維持。
- **data-privacy**: 実名/メール↔P-ID 対応表は repo 外・研究者のみ。フォーム/NDJSON/Dropbox/metrics は P-ID を単一キーに連携。
  メールは被験者本人にのみ送る。.gs に PII をハードコードしない（フォームID/Dropbox URL/公開鍵置き場の記入は可）。
- 自動メール送信は誤送信リスクがあるため、**既定は下書き作成 → 研究者が送信**を提案（完全自動はユーザー明示承認時のみ）。
- GAS のみ。アプリ本体(Rust/TS)・HMM・schema は不変。

## 5. 進め方
- `.gs` 実装は branch → PR（このリポの慣習）。`node --check` で構文確認（GAS グローバルは parse 通過）。
- 実機（GAS 実行・トリガ設定・メール下書き確認）はユーザー。エージェントは実装＋手順＋検証チェックリスト提示。
- 関連: 本タスク完了後、別途「本番ビルド実機スモーク検証」(`.steering/20260626-v2.22-smoke-verify/`) が残っている。
