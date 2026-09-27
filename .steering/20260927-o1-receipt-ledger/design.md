# 設計 — O1 受領台帳＋途絶検知

> 判断の一次は `decisions.md`（判断 1〜7）。ここは構造の要約。

## 実装アプローチ

- **新規 1 ファイル `Form_O1/GSE_O1_Ledger.gs`**（第 3 の Apps Script プロジェクトに貼る）。`doPost`・ビルダーは**触らない**。
- 純関数（名前の解析・判定・通知の差分・登録ログの読み取り・設定の検査）と、GAS 側（走査・書き込み・通知・トリガー）を分け、
  **純関数は Node の vm で同じソースを読んで固定**する（既存の `o1_submit_guard_test.cjs` と同じ流儀）。
- 走査は全走査＋既知 ID の除外＋時間予算 240 秒（判断 5）。台帳は追記のみ・途絶タブは毎回上書き（派生表）。

## 変更対象

### 新規
- `Form_O1/GSE_O1_Ledger.gs` — 台帳本体。関数: `o1LedgerRun`（トリガーの実体）／`installO1LedgerTrigger`／`o1LedgerCheck`（読み取りのみ・配備時の実測用）＋純関数群。
- `Form_O1/o1_ledger_test.cjs` — 116 ケース（名前・判定・通知・登録ログ・設定・通し・ソースの性質）。
- `Form_O1/o1_ledger_mutation_test.sh` — 42 変異（1 箇所ずつ）。
- `.steering/20260927-o1-receipt-ledger/{requirement,design,decisions,tasklist,t3-person-ledger-design}.md`

### 修正
- `scripts/check-o1-release-readiness.sh` — 台帳のテスト実行・直書き走査への追加・selftest の fixture へ写す。
- `.gitignore` — `Form_O1/*` のホワイトリストへ新 3 ファイルを明示（⚠️ 足さないと `git add -A` が黙って飛ばす）。
- `docs/glossary.md` — 受領台帳・途絶・欠番・未受領。

### 変えない
- `Form_O1/GSE_O1_Submit.gs`・`Form_O1/GSE_O1_Form_Builder.gs`（`git diff --stat` で 0 を確認する）。

## 影響範囲
- 稼働中のものへの影響は**ゼロ**（配備は別承認・別プロジェクト）。リリースゲートに 1 件（台帳のテスト）が増える。

## 既存パターンとの整合性
- 登録ログ・管理シートの流儀（バナー行 1・見出し行 2・データ行 3〜／`参加者ロスター` を持つ表には書かない）。
- `MailApp` のみ（`GmailApp` 不使用）・宛先はスクリプト プロパティ・fail-closed。
- ゲートの ID 形検査（25 文字以上の英数字の引用）・bash 3.2 の `${name}` 括りに従う。

## テスト戦略
- 単体（純関数）: 境界（4 日 23 時間/5 日・6/7 日・欠番の猶予）・順序前後・重複・登録ログの Date/文字列。
- 通し（偽 Drive/Sheets）: 冪等・通知は変化時に 1 回・宛先未設定/送信失敗で通知済みにしない・ロック・ロスター表拒否・時間予算・範囲外書き込み・数式注入。
- ソースの性質: `GmailApp` 不在・Drive 書き込み不在・直書き不在・受け口の `sanitizeName_` との一致（実関数を突合）。
- 変異: 上記のガードを 1 箇所ずつ壊して赤（`VERBOSE=1` でどの検査で赤かを確認）。
- ⚠️ 限界: 偽の Drive/Sheets は実物の制約を知らない → **実フォルダでの通し確認は配備時**（`o1LedgerCheck` で 未確認 2 点と所要時間を実測）。

## ロールバック計画
- 配備前は `git revert`。配備後はトリガーを外し（`installO1LedgerTrigger` の逆操作＝Apps Script の画面で削除）、追加した 2 タブは残しても無害（他のタブに触れていない）。
