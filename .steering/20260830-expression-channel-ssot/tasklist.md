# タスクリスト

## 準備
- [x] `.idea/20260819-smartphone-computational-media-channel.md` を全文（347 行）読む
- [x] `docs/literature/_index.md` の 2026-08-30 の 4 行 / `research-positioning.md` §3 の追記 4 ブロックを読む
- [x] 既決を一次で確認（D8 / D9 / D10 / D11 / PM-D4 / PM-D11 / PS-Q1・Q3・Q5 / PM-Q7・Q8 / ADR-015）
- [x] 凍結の範囲を `docs/preregistration-v0.3.md` 全文で確認（PreReg-1〜8）
- [x] 引き継ぎ §5 の「事故になるもの」5 件を実測で確認（★ 実測は **8 件**に増えた）

## 裁定（論点 1〜6 ＋ 追加の問い）
- [x] 論点 1: 差分の所在を「媒体」から「結合 (B)」へ焦点化 → **閉じた**（EC-D1）
- [x] 論点 2: 音声の自動開始は Phase1 の範囲外 → **閉じた**（EC-D2 / ADR-017 D5）
- [x] 論点 3: 「打鍵は work だから測ってよい」に条件を付ける → **閉じた**。⚠️ **計器は Phase1 に入れない**（EC-D3）
- [x] 論点 4: 境界クラス = PC → スマホ一方向イベント → **閉じた**（EC-D4 / ADR-017 D2–D4）
- [x] 論点 5: 主張の書き方 5 件 → **4 件適用 / 1 件は案**（EC-D5）
- [x] 論点 6: 表現層第 1 版は Physical Anchor を出口に持つ → **閉じた**（EC-D6 / ADR-017 D7）
- [x] 追加の問い: 復帰後の差分を表現へ結合する形 → **裁定 ＋ 入力の割り方を固定**（EC-D7 / ADR-017 D8）

## SSOT 昇格
- [x] `docs/adr/ADR-017-expression-channel-boundary.md` を新設（D1–D9・Accepted）
- [x] `docs/adr/README.md` の一覧に追記
- [x] `docs/architecture/expression-channel.md` を新設（§0–§8）
- [x] `docs/agent-shared.md` のリンクハブに追加 ＋ 概要の介入列を是正
- [x] `docs/research-positioning.md` §1 / §4 / §7 / §8 / §9 を適用（研究者承認済み）
- [x] `docs/glossary.md` に 6 語追加 ＋ 削除語 4 件を廃止扱い ＋ 禁止用語を是正
- [x] `.idea/...` に 2026-08-30 追記（SSOT への昇格・無効になった記述・未決）

## 事故の是正
- [x] `.claude/skills/physical-anchor/SKILL.md` の D11 違反を是正（★ 全面改訂・研究者承認済み）
- [x] `docs/architecture.md` の ADR-015 未追随 12 箇所を是正
- [x] `docs/research-positioning.md` §9 の Lv2 Wall / Monk Mode を是正
- [x] `docs/glossary.md` の Wall / Zen Timer / Monk Mode / Early Unlock を廃止扱い（★ 追加で発見）
- [ ] ⚠️ `data-privacy` SKILL の位置情報の節 → **切り出し**（`_handoff/next-session-prompt-expression-channel-followups.md`）
- [ ] ⚠️ [P6] の書誌確定 / [P170] 図 1 の分類 → **切り出し**（サーヴェイ次ラウンド）
- [ ] ⚠️ `intervention-design` SKILL のルール 5（Monk Mode）の確認 → **切り出し**

## 検証
- [x] `PYTHONUTF8=1 python scripts/check_citations.py` が違反ゼロ
- [x] `git status --short src-tauri src` が空（★ 実装差分ゼロ）
- [x] `/cross-review`（★ パス限定で実行・exit 0）→ **指摘 4 件＋テスト観点を全件反映**（EC-D8）

## ドキュメント
- [x] `decisions.md` に論点 1〜6 ＋ EC-D7 と「断定していないこと」を記録
- [x] `positioning-section5-draft.md` に §5 改訂案（⚠️ **未適用**）
- [x] 次セッションの引き継ぎを `.steering/_handoff/` に作成

## 完了処理
- [x] `design.md` の最終化
- [x] git commit
