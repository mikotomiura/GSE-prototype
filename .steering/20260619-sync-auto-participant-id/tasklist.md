# タスクリスト

## 準備
- [x] 関連 docs (§10.2/§10.2.1) + logger is_valid_participant_id 仕様 + 4 スクリプト読了
- [x] 影響範囲調査 (唯一のプログラム的呼出元は sync-all→sync-session、他は docs 参照のみ)
- [x] design.md / decisions.md 記入・設計承認 (パス導出最優先で承認済)

## 実装
- [x] sync-session.sh: allowlist 関数 + パス導出 + ローカル PID 解決 + PID 解決順差し替え
- [x] sync-session.ps1: 同上 (PS 5.1, -ParticipantId 既定変更, [regex]::IsMatch で \A..\z)
- [x] sync-all.sh: per-participant 反復 (Step1 ローカル PID コピー / Step2 raw/*/ 反復 / Step3 一括 add)
- [x] sync-all.ps1: 同上 (子 PS 起動の -ParticipantId 渡し削除, psExe 解決をループ外へ)
- [x] docs/development-guidelines.md §10.2: 「sync 未追従」→「追従済み」+ per-participant 反復に更新
- [x] .ps1 に UTF-8 BOM 付与 (D5: PS 5.1 CP932 誤読対策) + §10.2.1 に footgun 追記

## テスト
- [x] bash -n 構文チェック (sync-session.sh / sync-all.sh) 緑
- [x] allowlist 単体スモーク (logger テストと同ケース群 35/35 一致)
- [x] パス導出単体 (6/6) + dry-run E2E (metrics/Pderive9abc/ 生成、GSE_PID=P003 でも path 勝利)
- [x] sync-all E2E (per-participant Paaa111/Pbbb222 振り分け、CON 不正名スキップ、fallback→raw/P000)
- [x] PowerShell ParseFile 確認 (BOM 付与後 sync-session.ps1 / sync-all.ps1 とも errors 0)
- [~] sync-all Step 0 schema parity: 機構は正常動作 (drift 検出 exit 1) だが、実 gse-dataset の
      schema が**既存ドリフト** (Part 3 無関係。Step 0 は未変更)。temp で schema 一致時は緑を確認済

## レビュー
- [x] code-reviewer + security-checker 並列 (焦点=パス導出インジェクション/allowlist 全経路)
- [x] CRITICAL/HIGH 指摘への対応:
  - HIGH-1 (予約名リスト 5 箇所重複・パリティ test 不在) → scripts/tests/test_participant_id_parity.sh
    新規作成 (logger.rs を read-only 参照し予約名集合 + is_valid_pid 挙動を機械検証)。緑。
  - HIGH-2 (sync-all.ps1 が $LASTEXITCODE で子の成否判定 = §10.2.1 で不安定) → 出力 metrics
    ファイルの実在 + 非空で判定する方式に変更 (sync-session.ps1 の方針に統一)。
  - SEC-MEDIUM (--output-dir/--fallback 値なしで set -u クラッシュ) → 値存在ガード追加。
  - CR-M3 (sync-all.ps1 .NOTES exit code 不足) → 0-4 に補正。
  - CR-M5 (bash が先頭行のみ読み logger より緩い) → 全文読み+trim で logger 一致に修正。
  - CR-M6 (git add raw/ metrics/ が skip 済み不正 dir も commit) → 触れた PID のみ
    `git add -- raw/<pid>/ metrics/<pid>/` に変更 (先頭ハイフン PID も `--` で防御)。実 commit test で
    CON が commit されないことを確認。
  - 見送り (理由明記): CR-M4 (exit 1 が arg/cargo 兼用) = pre-existing・exit code 契約変更は
    Part 3 範囲外。CR-L7/L8/L9/L10・SEC-LOW(先頭ハイフン) = cosmetic/pre-existing、SEC-LOW は
    M6 の `--` で実害経路を遮断済み。
- [ ] /cross-review (jq 不在なら Claude 単独へ縮退・skip 理由明記) → /finish-task Step 3

## ドキュメント
- [x] docs/development-guidelines.md §10.2 更新 (実装タスクに含む)

## 完了処理
- [ ] design.md の最終化
- [x] decisions.md の作成 (D1-D4)
- [ ] git commit (Refs: .steering/20260619-sync-auto-participant-id/)
