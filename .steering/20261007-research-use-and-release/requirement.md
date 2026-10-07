# 打鍵の記録の研究利用と公開 — 同意・倫理の整理

## 背景

研究者は 2026-10-07 に、G1 / O1 で集めた人の打鍵の記録を論文（2 本目・BRM を想定）として公開したい、という方針を示した。
個人が分からないよう加工し、集計値も出しうる。所属大学（ZEN大学）は倫理審査を扱っていない可能性がある。
O1 は 2026-10-08 に v0.1.40 で始まる。現行の同意文書は O1 には公開の記述が無く、G1 は「生ログは公開しない」と約束している。
引き継ぎ: `.steering/_handoff/next-session-research-use-and-release.md`。

## ゴール

- 公開と 2 本目の論文の方針を ADR-039（Proposed）として記録する。
- 今日の O1 の同意改訂に入れる一文の案を、置き場所と同意項目まで具体にする。
- 同意文 v2（公表・公開の層）の草案、問い合わせ文 3 通の草案を作る。
- O1 事前登録草案の §0・§4・§12 を v0.1.40・`o1_install_id`・公開の扱いに合わせる。

## スコープ

### 含むもの
- ADR-039・`docs/adr/README.md` の索引・`docs/agent-shared.md` の番号範囲・`docs/references.md` への [V237]〜[V242] の登録
- `.steering/20261007-research-use-and-release/` の草案 3 本（今日の一文・同意文 v2・問い合わせ文）
- `.steering/20261007-o1-preregistration-draft/preregistration-draft.md` の修正（⚠️ main チェックアウトの未追跡ファイル。本ブランチには入らない）

### 含まないもの
- フォーム（`Form_O1/*.gs`・`Form_G1/*.gs`）と `consent-draft-o1.md` の書き換え（反映は研究者）
- 問い合わせの送信（研究者）
- 事前登録の凍結・`experiments/` の作成
- 法的判断（個人情報保護法の適用の可否を断定しない）

## 受け入れ条件

- [x] ADR-039 が BRM の規定（逐語を自分で確かめたもの）に接地し、研究者の判断（D1・D2・D8・判断 1）を記録している
- [x] 確かめていない事実を「未確認」と書き分けている（下位エージェントの報告のみのものは provisional・注記）
- [x] `check_citations.py` が違反なし
- [x] 草案がフォームを書き換えていない

## 関連ドキュメント

- `docs/adr/ADR-014`（判断 3 / D7 / D8）・`ADR-038`
- `Form_O1/GSE_O1_Form_Builder.gs`（`o1ConsentFormDescription_`・`o1ConsentItemTitles_`・`migrateO1ConsentForm`）
- `Form_G1/GSE_G1_Form_Builder.gs`・`experiments/20260801-controlled-friction-task/consent.md`

## 運用メモ
- /reimagine 適用: No
- 理由: 実装ではなく方針の記録と草案。主要な分岐（O1 の開始・G1 の扱い・今日の一文）は研究者が決めた。
