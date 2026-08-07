# requirement — G1 配布の自動化（Drive 配置 + メール送信）

引き継ぎ元: `.steering/_handoff/next-session-prompt-g1-distribution-automation.md`

## 背景

G1-C 提出 → `onG1ConsentSubmit`（P-ID 採番・トラッキング行追加・受付メール）までは自動。
梱包 `make-distribution.sh` も 2026-08-07 に完成済み。残る研究者の手作業は 2 か所:

- 【手作業 3】Drive へ上げて共有リンクを作る
- 【手作業 4】`sendTaskMaterialsEmail(pid, email, url)` を Apps Script で実行

⚠️ Apps Script の関数セレクタは**引数を渡せない**ので、今の 3 引数関数は
研究者がラッパーを手書きしないと実行できない。これが手作業 4 の実体である。

## ゴール

1. 被験者 1 人分の**課題ページ**を Drive に置き、共有リンクを得るまでを機械化する
2. 事前資料メールを**引数手打ちなし**で送れるようにする
3. 上記を `.steering` と Form_G1/README.md に手順として残す

## 受け入れ条件

- [ ] AC-1: 被験者 1 人分の課題ページ Drive 配置が、**全ファイルの byte サイズ照合**付きで通る
- [ ] AC-2: 照合に失敗したら**リンクを発行しない**（fail-closed）
- [ ] AC-3: 事前資料メールが引数手打ちなしで送れる。未送信の行だけに送る（冪等）
- [ ] AC-4: 送信を 1 か所で止められる（キルスイッチ）
- [ ] AC-5: `scripts/check_g1_emails.py` が緑（題材名・提示順がメール本文に無い）
- [ ] AC-6: macOS README に `§2.13` / `§2.14-2` 由来の 3 指示が残っている

## スコープ外（★ やらないこと）

- `make-distribution.sh` の作り直し（fail-closed ガード 4 本は実測済み）
- 割付 (`assign.py`) を梱包・アップロードに巻き込むこと（`§3-1`）
- `preregistration.md §3.1/§3.2/§3.4/§3.5/§3.6` の変更
- `schema_dto.rs` の変更
- 受付メールへの題材名・提示順の書き戻し（`§2.12`）
- ⚠️ **同一端末を 2 人が使うと `~/.gse/g1_participant_id` が前の人の値のまま残る**問題
  （`lib.rs:1113` は保存値をそのまま返す）。実在するが在宅 1 端末 1 人では出ない。別タスク。
- `launch-g1-windows.bat` の文言整理（`echo` 行 67「送信するを押す」・69「第1週」は
  自動送信 / Phase1 用語の名残に見えるが、確認していないので触らない）

## 運用メモ

- /reimagine 適用: No
- 理由: 設計の分岐（配布の形・共有範囲・送信起動）は着手前にユーザー判断で確定済み
  （`decisions.md` D-1〜D-3）。残りは実装のみで、複数案が競合していない。
