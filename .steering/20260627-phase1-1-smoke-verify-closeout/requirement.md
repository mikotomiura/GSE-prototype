# 要件: #1 backend 層2 修正の スモーク検証 ＆ クローズアウト

## 背景
前タスク `20260626-phase1-card-repro-backend-fix`（#1 カード無反応の backend 層2 根本修正
＝consumer 耐障害化＋fail-loud＋デバッグ強制トリガ＋誤誘導ラベル是正）は
`feature/phase1-pilot-fixes` で実装済み、**PR #31 / #32 で `main` にマージ済み**。

残るのは前タスク tasklist の最終2項目:
- [ ] 実機 repro / 本番ビルドスモーク（研究者作業）
- [ ] パイロット被験者の起動方法の確定

本タスクはこの「検証＆クローズアウト」と、`advice.md` の個人 issue 3 件への回答を担う。

## ゴール（受け入れ条件）
1. マージ済み `main` のコードがビルド・テスト健全であることを機械的に確認する
   （Claude が実行可能な範囲）。
2. 実機スモークテスト（TCC 権限を伴うため**研究者の手作業**）の手順書を用意する。
3. `advice.md` の 3 issue に回答 / 解決状態を提示する:
   - issue 1: dev 用と被験者用で初期 Dashboard が変化しないが問題ないか
   - issue 2: 被験者にどう GSE を起動させるか（セキュリティ/権限コスト）
   - issue 3: 事後アンケートの GAS コード作成

## スコープ外（憶測修正しない）
- 原因（Full/Disconnected）未確定のままの backend 追加修正（前タスク制約を継承）。
- codex が提案した堅牢化（first-run self-check / fsync / heartbeat 等）の**実装**は
  follow-up タスク候補として記録のみ。本タスクでは着手しない。
