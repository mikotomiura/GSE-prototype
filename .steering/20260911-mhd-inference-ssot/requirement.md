# mhd-inference-ssot

> ⚠️ **本タスクは issue 未分解。** `_survey-inference-architecture.md` を読んでから
> `issue-slicing` skill で分解すること。
> ⚠️ **T1（`20260911-intake-arbitration-branch`）の完了後**に着手する。

## 背景

`.idea/` の 9/10〜9/11 の 3 本（`20260910-mhd-criterion-*` / `20260910-mhd-feature-*` /
`20260911-mhd-growth-*`）が、MhD の推論アーキテクチャについて体系的な改善案を提示している。
調査結果は **`_survey-inference-architecture.md`** に保存済み（★ **これが本タスクの一次資料**）。

到達点の骨格: MhD は「打鍵から 3 状態を当てる分類器」から離れ、
**content-free な作業行動から、近い将来の 3 つの競合転帰を、打ち切りを含む離散時間の生存解析枠組みで
推定する**という提案に収斂している。推定は複雑さで昇格せず、calibration・上下界の安定・
future-session 改善という**測れる量**でゲートされる。

### ⚠️★★★ 判明した最重要の問題

1. **ADR-008 D8 と WP5 I2 が正面衝突する**
   - ADR-008 D8: 「③どの信号が効くかの癖には**専用の特徴選択機構を作らない**
     （1 人あたりラベル 20〜100 件では確実に過学習するため、②の係数の大きさとして吸収させる）」
   - WP5 I2: 「十分な過去 episode を持つ人だけ、限定候補から**個人別 feature subset** を選ぶ」
   - → ★ **I0/I1 は D8 と両立するが、I2 は正面から衝突する。**
     新規 ADR で D8 を明示的に部分改訂しない限り SSOT 化できない。

2. **hyperparameter registry の語彙が非整合**
   - `roadmap §5` の 11 項目 vs ADR-008 D5 の pinning リスト
     （`model_version` / `profile_version` / `initial_profile_state` / `update_rule_version` / `random_seed`）
   - 目的は近い（replay 再現性）が語彙が違う。`seed` ↔ `random_seed`、
     `profile_version` 系は roadmap 側に無く、`dataset_version` / `split_manifest` は ADR-008 側に無い

3. **Tier の名前が同じで軸が違う**
   - 既存 `personalization-and-online-learning.md §5.2` の Tier 0/1/2 は「**収集済みか否か**」の軸
   - `.idea` の T0/T1a-d/T2/Q は「**認知的作業の型（認知の跡がどこにあるか）**」の軸
   - → 同名衝突。昇格時に名前を変えるか軸を明記する必要がある

4. ⚠️★★★ **`Layer 4`（推定層）を専用に扱う設計文書が存在しない**
   - 出力スキーマ（`WorkStateEstimate`）は `domain-adapter-boundary.md` の末尾節に間借り
   - 現行 HMM の設計根拠は ADR-001 と Skill と `engine.rs` のコードコメントに**分散**
   - ★ **受け皿の推奨は新規ファイルではなく `personalization-and-online-learning.md`（1401 行・Proposed・
     「Layer 3-4 拡張」）への追記・統合**。新規ファイルを作ると重複してどちらが正か曖昧になる

5. **`M1〜M4` は ADR-021 D11 が撤回済み**（26 週 WBS の `M0〜M5` と記号が衝突したため）。
   ⚠️ `.idea/20260911` は**全編で `M1〜M4` を使っている**ので、昇格時に実体名へ置換が必須。
   `Mh-D` の正式表記も **`MhD`**（ハイフン無し）。

## ゴール

`.idea` の推論アーキ改善案のうち **A 区分（議論だけで閉じる）**を SSOT へ昇格し、
**B 区分（衝突・統合が要る）**については裁定の ADR を書く。

## スコープ

### 含むもの（A 区分・`_survey` の §11 判定より）
- 段別モデル候補の具体名と昇格判定表 → `gse-v2-overview.md` または ADR-019 への補遺
- **三つの時間**（O1 discovery / training-adaptation / evaluation）と
  **三つの出力を混ぜない**（MhD estimate / Decision / Practice Trace）
- **hyperparameter tuning 対象 / 禁止リスト 5 項目**
- auto-tuning の offline global tuning（grouped nested CV）
- WP5 **I0**（共有特徴 + 個人別縮約係数）
- **feature importance の四層**（population / conditional / personal / decision）
- **用語整理**: `Mh-D` → `MhD`、`M1〜M4` → 実体名

### 含むもの（B 区分・裁定が要る）
- ⚠️ **ADR-008 D8 と WP5 I2 の衝突の裁定**（新規 ADR）
- ⚠️ **registry 11 項目と ADR-008 D5 pinning リストの統合**
- ⚠️ **Tier 名の衝突解消**（既存 Tier 0/1/2 と `.idea` の T0/T1a-d/T2/Q）

### 含まないもの
- ⚠️ **特徴量 Tier の中身の確定**（T1c revision topology / T1b boundary pause / T1d restart shape /
  IME state machine）→ **C 区分**。O1 の実データで coverage・欠測率・feasibility が出るまで確定できない
- ⚠️ **G-next / O-holdout の正式名称・split・事前登録** → `roadmap §11` 自身が「ADR 化前の未決」と明記。
  **O1 完了後**に ADR 化
- ⚠️ **ADR-009 を Accepted にすること**（G1 が `n = 0/3`）
- ⚠️ **転帰定義の一本化** → T2（`20260911-outcome-arbitration-and-o1-preflight`）の issue 007
- ⚠️ **IME content-free state machine の実装** → D 区分（feasibility 試験が先）
- 学習コードの実装（現在 0 行。ADR-008 の枠組みの裁定が先）

## 受け入れ条件

- [ ] A 区分の各項目が `personalization-and-online-learning.md` ほかへ追記され、
      `check_doc_lexicon.py` / `check_citations.py` が exit 0
- [ ] ⚠️ **ADR-008 D8 と I2 の関係が新規 ADR で明文化されている**（改訂するのか、I2 を採らないのか）
- [ ] registry の語彙が一本化されている
- [ ] Tier 名の衝突が解消されている（改名するか軸を明記するか）
- [ ] 昇格した文書に `M1〜M4` と `Mh-D` が残っていない
- [ ] `/cross-review` を通している

## 関連ドキュメント

- ★ **`_survey-inference-architecture.md`（本ディレクトリ・一次資料）**
- `docs/architecture/personalization-and-online-learning.md`（1401 行・**受け皿の第一候補**）
- `docs/adr/ADR-008-online-learning-boundary.md`（★ **D5 / D8 が争点**）
- `docs/adr/ADR-019-model-maturity-and-promotion-gate.md`（昇格ゲート）
- `docs/adr/ADR-021-expression-channel-open-items.md` D11（`M1〜M4` の撤回）
- `docs/glossary.md`（`MhD` の正式表記・層呼称の 4 系統）

## 運用メモ

- **/reimagine 適用: Yes**
- 理由: ADR-008 D8 の部分改訂は**オンライン学習の境界そのものを動かす**判断であり、
  やり直しが効かない。設計段階で `/reimagine` を起動する。
