# タスクリスト

## 準備
- [x] `.steering/_handoff/next-session-after-adr026.md` を読む（★ 三次資料。当たりを付けるだけ）
- [x] 一次確認: `ADR-017` D2 / `ADR-021` D4・D5・D9・D10 / `ADR-022` D1 / `ADR-026` / `expression-channel.md` §2.1・§3.5.2b・§3.5.4・§3.6・§6.3・§7.5・§8
- [x] 実測: `invitation` は `src-tauri/src/` 0 件 / `src/` 0 件
- [x] 実測: `NUDGE_DAILY_CAP = 6`（`intervention.rs:19`）／`record_dismiss`（`:237`）
- [x] 実測: `liveness` は表現文脈の docs に 5 箇所のみ・**更新機構の定義は 0 件**
- [x] `verify-before-claiming` / `git-workflow` Skill を読む

## 実装（ドキュメント）
- [x] `docs/adr/ADR-027-invitation-delivery-semantics.md` を書く
- [x] `expression-channel.md` §2.1 を改訂（発火条件 / 再接続 項目 3 / 解除と断）
- [x] `expression-channel.md` §7.5 `A1` を書き直し、`A21` を新設（★ 併せて `A3` / `A5` / `A14` も改訂）
- [x] `expression-channel.md` §8 で `W-2` を閉じ、`W-1` に前提を追記し、`W-3` を新設（★ `PS-Q10` ③ の stale ポインタも更新）
- [x] `docs/glossary.md`（抽象状態イベント / 招待の解除 / 新規行「意味フィールド / 制御フィールド」）
- [x] `docs/adr/README.md` に ADR-027 の行 ＋ ADR-017 / ADR-021 の注記 ＋ 読む順の注記
- [x] `docs/agent-shared.md` のリンクハブ行
- [x] ⚠️ **表の破損修正 2 件**（★ `expression-channel.md` §3.6.2 の `PC-11`/`PC-12` 間 ／ `docs/adr/README.md` の ADR-015/016 間）

## テスト
- [x] `PYTHONUTF8=1 python scripts/check_citations.py` を「違反なし」まで（★ exit 0）
- [x] 旧文「`level` が変わったときだけ」が SSOT に残っていないことを grep で確認
- [x] 受け入れ観点の採番が `A1`–`A21` 連番（`A16` は予約済み欠番）／未決は `W-1`–`W-3`
- [x] 変更 5 ファイルの markdown 表の破損を機械走査（★ 0 件）

## レビュー
- [x] `code-reviewer` ＋ `security-checker` を並列起動
- [x] HIGH 指摘への対応（⚠️ backlog へ punt しない）—— ★ **HIGH 4 件すべて本タスクで消化**
- [ ] `/cross-review`（★ コミット後・パス限定・出力は scratchpad の絶対パス）

## ドキュメント
- [x] glossary への用語追加
- [ ] 引き継ぎ `.steering/_handoff/` の更新

## 完了処理
- [x] design.md の最終化
- [x] decisions.md の作成
- [ ] git commit
