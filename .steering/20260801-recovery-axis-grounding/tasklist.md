# タスクリスト — recovery risk 軸の理論裏付けと具体化

## T0: 準備
- [x] 前セッションの未コミット 43 ファイルを 2 系統に分けてコミット（混ぜない）
- [x] 主要文献を読む（統合設計文書 / ADR-008 / ADR-009 / 文献カード / decisions.md）
- [x] grill で **RQ-1 の判定基準**を結果を見る前に固定する（4 問・ユーザー裁定）
- [x] `.steering/20260801-recovery-axis-grounding/` を作成
- [x] 必須 Skill を読む（`citation-ssot` / `literature-card` / `reproducibility-discipline`）

## T1: 文献ラウンド（`/literature-review` 1 ラウンド）

### RQ-1（★最重要・厳格水準）
- [x] 1-a 打ち切りのある離散時間 time-to-event の標準形（person-period ロジスティック）→ **確定** [V59][V60]
- [x] 1-b 二値化 + 固定 horizon の害 → **確定**（[V59] pp.64–65 逐語）
- [x] 1-c focus 喪失は独立打ち切りか競合イベントか → **PLAUSIBLE BUT UNPROVEN**（混合・同定不能）
- [x] 1-d オンライン・低ラベル制約下での成立性（反証 angle 込み）→ **確定（条件付き）** [V63]
- [x] 3 票の敵対的検証（視点を変える）→ confirmed 7 / 2-1 が 1 / **否決 4 件**
- [x] **判定基準 (a)(b) への照合と判定** → **両方満たす → 書き換える**

### RQ-1 の判定が「書き換える」場合の改訂
- [x] `§3.3` ラベル定義（二値 → イベント時刻 ＋ 種別/打ち切り指示子）
- [x] `§3.4` 打ち切りの型を分ける（競合 / 混合 / 管理的打ち切り）
- [x] `§4.4 Phase C` 推定器（person-period 多項ロジスティック ＋ CIF による読み出し）
- [x] `§8.1` Recovery 層の評価指標（離散時間・競合事象向けへ）
- [x] `§8.2 G2` 反証ゲートの再定義（★上下界が介入判断を反転させるか）
- [x] `§11` Deferred の更新（7: Δ の任意性 / 8: 上下界は自前 / 9: 離脱の分離手段なし）
- [x] `ADR-009 D2` / `D5`（H-X1d 文言）/ `Migration` / `Consequences` / D1 本文
- [x] `decisions.md` に判断として記録（判断 1〜6・前セッション判断 8 の改訂）

### RQ-2 / RQ-3（標準水準）
- [x] RQ-2 先行研究の探索 → ★ **空白ではなかった** [P33][P34][P35]
- [x] RQ-2 の結果を `§2.6` に反映（**新規性の主張を縮小**）
- [x] RQ-3 online 学習 × 事前登録（prequential [V64] / 適応的デザイン [V65]）
- [x] RQ-3 の結果を `ADR-008 D4` / `§7.2` に反映（維持するが位置づけを変更）

### 成果物
- [x] 文献カード生成（`20260801-recovery-labeling-and-online-prereg.md`・RQ ごとの検証水準を冒頭に明記）
- [x] `docs/references.md` に append-only 登録（`[P33]`–`[P35]` / `[V59]`–`[V65]`・renumber 0 件・捏造ゼロ）
- [x] `docs/literature/_index.md` に 1 行追記（＋件数を 94 へ更新）
- [x] `docs/research-positioning.md` §3 への還元（★§5 は不変更）

## T2: 具体化
- [x] T2-a `experiments/20260801-controlled-friction-task/`（G1 実験設計・**実施しない**）
  - [x] 高摩擦を誘発する統制タスクの具体（統合の必要性で操作・語彙制約は交絡として棄却）
  - [x] 同一人物内の低/高摩擦条件の割付（8 ブロック・ABBA 釣り合わせ ＋ seed 無作為化）
  - [x] **分離できたと言える基準の事前宣言**（AUC 中央値 ≥0.70 / 4-5 名で >0.60 / 並べ替え p<0.05）
  - [x] `reproducibility-discipline` 規約（SEED / env.md / data.md / config.json / run.sh stub / notes.md）
- [x] T2-b Tier 0 配線の additive schema 設計メモ（`tier0-wiring-design.md`・コードは書かない）
  - [x] `feat` 行への additive 追加案（★ 実質 `keys` 1〜2 フィールドで足りることを発見）
  - [x] `emit_schema` diff の想定（additive-only）
  - [x] gse-dataset 側 schema parity への影響と作業順序

## T3: 完了処理
- [x] 改訂漏れチェック（旧定義「H 分以内」の残存 2 箇所を検出し修正）
- [x] citation 整合チェック（新規 10 件すべて references.md に実在・本文で使用・renumber 0 件）
- [x] 凍結対象への非接触チェック（`git status` で確認・変更なし）
- [x] コード変更ゼロの確認（`.rs` / `.tsx` / `.ts` の変更なし）
- [x] `cargo test --workspace` 緑（**246 + 23 passed / 0 failed**）
- [ ] `/finish-task`（`/cross-review` の可否は `.codex/budget.json` を確認してから判断）

## 判定サマリ

| RQ | 判定 | 帰結 |
|---|---|---|
| **RQ-1** | ★ **定式化は誤りだった → 書き換えた** | 二値ロジスティック → 離散時間競合リスク・ハザード。ADR-009 D2 改訂 |
| **RQ-2** | ★ **新規性主張が過大だった → 縮小した** | 「行動由来ラベル＝新規」は不成立。残るのは制約の組合せのみ |
| **RQ-3** | **D4 は維持・位置づけを変更** | 「自前の唯一解」→「一般原則の保守的な特殊ケース」 |
