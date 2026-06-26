# 設計判断

## D1: 通知メールは自動送信（AUTO_SEND=true）
- 当初決定 (2026-06-27 朝): `AUTO_SEND=false`（下書き作成・研究者が確認後送信）を既定とした。
- 変更 (2026-06-27): ユーザー明示指示により `AUTO_SEND=true`（MailApp.sendEmail で自動送信）へ切替。
  当初の設計が要求した「完全自動はユーザー明示承認時のみ」の承認条件を満たしての変更。
- 根拠: 研究者の手動送信ステップを省き、適格な F1 提出から通知までを完全自動化したいため。
- 影響/リスク低減: 適格な F1 提出の瞬間に本人宛メールが送られる（確認ステップ無し）。
  誤送信は (a) 適格判定（同意・年齢・IME・OS・メール@検証）、(b) 冪等性（同一メール二重送信防止）、
  (c) 送信先を F1 Q8 の本人メールのみに限定、で抑える。安全側へ戻す場合は `AUTO_SEND=false`。

## D2: condition は全員 baseline 固定
- 決定: `DEFAULT_CONDITION="baseline"` でロスター転記。
- 根拠: Phase1 は単群・対照なし（FD1）。動的割付は不要。将来 AB 設計時はロスターの
  ドロップダウン（baseline/intervention）で手動上書き可能にしてある。ユーザー確認 2026-06-27。

## D3: フォーム回答は destination sheet ではなく getResponses() で直接取得
- 決定: `recordFormUrl` に form id を保存し、`FormApp.openById(id).getResponses()` で集計。
- 根拠: destination sheet を各フォームに設定する運用ステップを増やさずに済む。P-ID 列を
  直接読めて突合がシンプル。id 追加は後方互換（既存呼び出し不変）。
- 注意: 既存 Script Properties は id 無し → build F2/F4/F5 を一度再実行するまで集計は空。

## D4: ロスター行1に機密バナー、ヘッダを行2へ。探索はヘッダ動的検出に統一
- 決定: `rosterHeaderRow_()` で「P-ID」ヘッダ行を動的に探し、全集計/採番がそれを起点にする。
- 根拠: 実名↔P-ID 対応表の機密性をシート上で明示（data-privacy / pilot-runbook §0）。
  行構成変更で既存 `nextParticipantId_` が破綻しないよう探索方式を新ヘルパと統一（review HIGH）。

## D5: 発番区間を LockService で直列化
- 決定: dedup→採番→appendRow→flush を ScriptLock で排他。
- 根拠: F1 同時提出時にトリガ並行実行で同一 P-ID を重複発番しうる（GAS トリガはシリアライズ
  非保証）。重複 P-ID は突合の根幹を壊すため必須（cross-review HIGH 一致指摘）。

## D6: 通知失敗は備考列に可視化して手動回復可能にする
- 決定: メール作成を try/catch し、失敗時はロスター備考列(13)に「⚠通知未作成-要手動送信」を記録。
- 根拠: ロスター行確定後に createDraft/sendEmail が例外を出すと、dedup により再提出が
  スキップされ被験者が永久に通知未達になりうる（cross-review HIGH-2）。Phase1 規模では
  再試行機能までは作らず、失敗を可視化して研究者が手動フォローする SOP とする。

## D7: PII 最小化（ログのメールマスク・ダッシュボードに実名を出さない）
- 決定: `Logger.log` のメールは `maskEmail_`（u***@example.com）。進捗ダッシュボードの
  要フォロー一覧は P-ID のみ（実名は出さない）。実名↔P-ID はロスタータブに閉じる。
- 根拠: Apps Script 実行ログはクラウドに残る。ダッシュボードはスクショされやすい。
  PII 露出面を対応表（機密バナー付きロスター）に限定する（security / cross-review 指摘）。

## 見送り（記録のみ）
- 設問タイトル部分一致照合の脆さ（"OS"/"メールアドレス" 重複）: ランタイム保護まではせず、
  `f1Answers_` に「F1 に同キーワードの別設問を足すな」制約コメントを明記して対処。
- `applyRosterValidation_` の条件付き書式全置換: Phase1 規模では手動書式追加は限定的なため許容。
