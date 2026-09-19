# 単位 b: 非再捕捉の射程を絞る新 ADR（ADR-033）

> 親タスク: `.steering/20260919-theory-ssot-promotion/`（段 3）。引き継ぎ §2 の単位 **b**。

## 背景

- 生成的返権論の草案は、必要条件候補に Non-recapture（返還後の行為を報酬・罰・ランキングへ再利用しない）を置く。
- SSOT には、返還後の応答を次の判断へ戻す設計が既にある（ADR-008 D1「介入の効用」の両方向の更新・`RECENT_DISMISS_MS`）。理論レビューの衝突 X-06。
- 研究者判断 1 #3（2026-09-18・J-4）: **抑制方向のみ許す**。拒否を尊重して控える利用は許し、応答を成功として学習・評価・報酬へ戻す利用は禁ずる。ADR-008 D1 の射程を絞る別 ADR が要る。
- 研究者判断 1 #11（J-15）: 受容率を成功指標にしない（choice symmetry）。

## ゴール

- 新 ADR（ADR-033）で、応答の定義・許す向き・禁ずる向き・抑制の解き方の根拠・研究の評価の条件・実装の受け入れ条件を決める。

## スコープ

### 含むもの
- `docs/adr/ADR-033-non-recapture-suppression-only.md`（新規）
- `docs/adr/README.md` の一覧に 1 行

### 含まないもの
- ⚠️ ADR-008 / ADR-018 の本文の書き換え
- ⚠️ PM-Q7（ADR-017 D8 の非対称を維持するか）
- ⚠️ RP §5 H-PA / §8 の改訂（単位 d-2）・glossary（単位 e）・CORE-CS 契約（単位 g）
- ⚠️ 実装（`OnlineUpdater` は未実装）

## 受け入れ条件

- [ ] 研究者判断 J-4 / J-15 の範囲を越えて決めていない
- [ ] `RECENT_DISMISS_MS` が許される側に入り、現行コードが本 ADR に従っていることを一次で確かめている
- [ ] ADR-023 D2（再開後の動態は入力にしない）を緩めていない
- [ ] 引用はすべて登録済み・「先行研究が存在しない」型の断定が無い
- [ ] `/cross-review` 2 巡

## 関連ドキュメント

- `.steering/20260918-theory-critical-review/decisions.md` 判断 1 #3 / #11・`ssot-collision-findings.md` X-06 / X-16・`review-D.md` §6
- `docs/literature/20260919-non-domination-and-autonomy-norms.md`（S2）
- `docs/adr/ADR-008-online-learning-boundary.md`・`ADR-017` D8・`ADR-018` D3 / D5・`ADR-023` D2・`ADR-027` D4

## 運用メモ

- /reimagine 適用: **No**
- 理由: 向きは研究者が裁定済み（J-4）。ADR はそれを既決と矛盾しない形で書き下ろす作業である
