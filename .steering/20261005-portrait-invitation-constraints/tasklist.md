# タスクリスト

## 準備
- [x] grill（AskUserQuestion 2 回・研究者の追加「物体の必要性」）→ requirement.md
- [x] worktree とブランチ（`docs/portrait-invitation-constraints`・S-MR のブランチから）
- [x] コンテキストが長くなったので区切った。引き継ぎは `.steering/_handoff/next-session-portrait-invitation-constraints.md`（2026-10-05・研究者の指示）

## 1. 台帳
- [x] ADR 025 / 026 / 027 / 033 / 035 の決定の節を全部読む（021 は D3〜D6 と D9 の一般原則）
- [x] 既存の文献カードから、肖像・招待・物体にかかる行を抜く（S-MR・物体・自己状態の外在化・可読性。PC 招待面のカードは ADR-026 に取り込まれている分を使った）
- [x] `constraints-ledger.md` を書く（3 区分・出典・格・衝突 T1〜T8）→ コミット `e5ec1e4c`

## 2. 小さなサーヴェイ（S-PI）
- [x] subagent-delegation を確かめ、3 angle を Sonnet で並列に投げる（締切 20 分・入れ子禁止・有料禁止）→ 所要 4.0 / 2.9 / 2.7 分
- [x] 断定に使う一次をメインが開いて照合する（メインが原本を取り直し、逐語 24 か所すべてを確認。報告の誤り 3 つを訂正）
- [x] claim 抽出・3 票・温度・否決リスト（台帳 19 件・否決 N1〜N5）
- [x] カード・references（DOI で重複確認・採番を全ブランチで測り直し P454–P467）・_index
- [x] check_citations が違反なし
- [x] 単独でコミット・push → `583a5ca8`（PR なし）

## 3. 決定
- [x] 物体の必要性の論点を、既存の材料から立てる（台帳 T8・物1〜物12）
- [x] ラベル・無視の扱い・物体の必要性を、推奨と理由を添えて研究者に聞く（AskUserQuestion 1 回・4 問。肖像の「状態を表さない」の定義も 1 問として聞いた・4 問とも推奨どおり）
- [x] decisions.md に「決定 / 理由 / 却下案」で記録する（判断 4〜7）
- [x] EH1 の設計の制約と EH3 で測るものを導く（判断 8）
- [x] `.idea/` に還元する（`.idea/20261005-motivation-fatigue-reentry-surface.md` §8.2 に注記・§11 を追加・版管理外）
- [x] 用語が固まったら glossary に追記する（「予期しない・評価を含まない驚き」）

## 4. 閉じる
- [ ] コミット・push（PR は出さない）
- [ ] /cross-review 1 巡目・2 巡目と対応を decisions.md に
