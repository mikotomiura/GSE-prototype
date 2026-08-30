# タスクリスト — 未踏 2027 提出文書の書き直し

## 準備
- [x] 引き継ぎ `.steering/_handoff/next-session-prompt-mitou-2027-rewrite.md` を読む
- [x] SSOT を読む（research-positioning / ADR-015 / ADR-017 / expression-channel /
      preregistration / WBS / glossary / EC-D1〜D10 / literature `_index`）
- [x] 実測材料を読む（Phase1 分析 notes / G1 README / features.rs の 5 特徴量）
- [x] 2026 版 2 文書を全文読む
- [x] ⚠️ **研究者へ確認**: 主役 / Phase1 の出し方 / git の扱い（→ `decisions.md` D1–D3）
- [x] `/start-task` で `.steering/20260830-mitou-2027-rewrite/` を作る
- [x] 2026 版をスクラッチパッドへ退避（★ repo 外・D3 を裏口から覆さないため）

## 実装
- [x] **提案書**を 2027 版へ全面改訂（⚠️ 見出し 1〜8 ＋ 参考文献の構造を保つ）
- [x] **技術設計書**を 2027 版へ全面改訂（★ 構造も再設計してよい）
- [x] 両文書の参考文献リストを再構成（★ 独自番号体系・`references.md` は動かさない）

## テスト（★ 文書の機械検査）
- [x] 提案書の見出し構造が 1〜8 ＋ 参考文献（`grep -c '^# '` = 9）
- [x] 削除済み機能が**現行機能として**登場しない（Wall / Monk Mode / Zen Timer / Early Unlock）
- [x] 降ろした主張が登場しない（6 特徴量 / 3 クラス分類 / 3 状態推定）
- [x] 身体活動センシングが**本体の完了条件として**登場しない（GPS / 歩数 / 加速度 / FFT）
- [x] `glossary.md` 禁止用語が登場しない（不便益 HCI である / 不便益を測定可能にした / 歩数達成 / 断定）
- [x] `DataInsufficient` と `表現チャネル` が両文書に入っている
- [x] 予算が 9ヶ月 / 2,646,000円 / 2,100円/時 × 約1,260時間 のまま
- [x] `PYTHONUTF8=1 python scripts/check_citations.py` が違反なし（★ `docs/` を汚していない検算）
- [x] `git status --porcelain src-tauri src` が空（★ コード差分ゼロ）

## レビュー
- [x] ⚠️ `code-reviewer` / `security-checker` は**対象外**（★ コード差分ゼロ）
- [x] `/cross-review`（Codex）を**パス限定**で回す
      （⚠️ memory: 無関係な未コミット変更で BLOCKED するため必ず `-- docs/mitou_docs`）
- [x] 指摘への対応（★ 5 件すべて採用・`decisions.md` D5）

## ドキュメント
- [x] ⚠️ `docs/` 側 SSOT は**変更しない**（★ 本タスクは参照する側）
- [x] `glossary.md` への用語追加は**不要**（★ 新概念を導入していない）

## 完了処理
- [x] `design.md` の最終化
- [x] `decisions.md`（D1–D5）
- [x] git commit（★ ブランチ `docs/mitou-2027-rewrite`・3 コミット: 全面改訂 / cross-review 反映 / budget）
- [ ] ⚠️ **研究者確認**: `decisions.md` D4（ロードマップが WBS §改訂予定＝**未承認**に依拠している）
