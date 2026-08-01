# 設計

## 実装アプローチ

**コード変更ゼロの文書タスク**。Epic 1（ADR 群）と同じ形。

着手順序は「2 本を統合する」より先に **「昇格の前提を満たす」**（引き継ぎ §進め方）。
doc#2 をそのまま昇格させると (B-1) の `[V40]` 衝突と (A) の 4 状態の破綻が **SSOT の中に入り込む**ため。

1. 入力の読み込み（v2 SSOT 3 本 / ADR-001〜007 / research-positioning / PreReg-5 / references.md / `.idea` 2 本）
2. 外部 9 本の**書誌を一次ページで確認**（捏造禁止・citation-ssot ルール 5）
3. `/reimagine`（#6 潜在状態）— 初回案を破棄して再生成し比較 → `decisions.md` 判断 1
4. 裁定が必要な 4 点をユーザーへ提示（#6 / B-1 / ステータス / (D)）
5. 統合設計文書 → ADR-008 → ADR-009 の順で執筆（上位から下位へ）
6. 引用は**書きながら**採番（citation-ssot。書き終えてからだと主張と噛み合わない）
7. 周辺 SSOT の整合（glossary / references 件数 / ADR README / リンク行 / `.idea` ヘッダ）

### 3 層の成果物構造（なぜ 1 本にしないか）

| 層 | ファイル | 役割 |
|---|---|---|
| 文脈と計画 | `docs/architecture/personalization-and-online-learning.md` | 実測・段階計画・評価指標・反証ゲート・ContextSnapshot の具体形。ADR に入りきらない |
| 決定（機構） | `docs/adr/ADR-008-online-learning-boundary.md` | 何をオンライン更新し何を凍結するか / 3 部品 / PreReg-5 両立基準 / replay pinning |
| 決定（対象） | `docs/adr/ADR-009-recovery-risk-axis-and-latent-state.md` | X 軸の再定義 / 潜在状態の扱い / 旧仮説の非流用 |

## 変更対象

### 新規作成
- `docs/architecture/personalization-and-online-learning.md` — 統合設計文書（Proposed）
- `docs/adr/ADR-008-online-learning-boundary.md` — オンライン学習の境界（Proposed）
- `docs/adr/ADR-009-recovery-risk-axis-and-latent-state.md` — 新軸と潜在状態（Proposed）
- `docs/literature/20260801-behavioral-economics-and-online-personalization.md` — 落合カード 9 枚

### 修正
- `docs/references.md` — `[P29]`–`[P32]` / `[V54]`–`[V58]` を append。一意件数 66 → 84。登録ラウンドの注記
- `docs/adr/README.md` — 一覧に ADR-008/009 を追加
- `docs/glossary.md` — Receptivity（層の明示）/ `self_directed_recovery_risk` / `progress_proxy` /
  Decision Episode / PersonalizationStore / 打ち切り を追加
- `docs/literature/_index.md` — 本ラウンド行を追加。冒頭の件数記述を更新
- `docs/architecture/gse-v2-overview.md` — **§関連文書にリンク行のみ**（7 層・Epic 本文は不変）
- `docs/architecture/domain-adapter-boundary.md` — Layer 3-4 に additive 拡張候補のポインタ
- `docs/architecture/intervention-decision-engine.md` — Receptivity が Layer 5 である旨の 2 行
- `.idea/*.md` 2 本 — 「→ 昇格済み」ヘッダと是正点

### 触らない（凍結・厳守）
`src-tauri/**` / `src/**` / `schema_dto.rs` / `schema/current.json` / `engine.rs` / `loop_step.rs` /
`intervention.rs` / `probe_scheduler.rs` / `App.tsx` / `docs/preregistration-v0.3.md` /
`docs/research-positioning.md` / `docs/adr/ADR-001`〜`ADR-007`

## 影響範囲

- **SSOT の一貫性**: 新軸は `gse-v2-overview.md` の 7 層を**置き換えない**。Layer 4 出力への additive 追加に留める。
  ステータスを Proposed にすることで「方向は合意したがデータは無い」温度を保つ。
- **ADR-007 の保全**: doc#2 の 4 状態をそのまま入れると Layer 4 と Layer 5 に Receptivity が並立し
  ADR-007 が静かに無効化される。→ ADR-009 D3 と glossary・`intervention-decision-engine.md` の 3 箇所で
  「Receptivity は Layer 5」を明示して再発を防ぐ。
- **ADR-006 の保全**: 拡張は新 ADR が担い、ADR-006 のファイルは 1 バイトも変えない（判断 5）。
- **research-positioning の保全**: §5 は研究者確認必須節。H-X1d は**提案のみ**。

## 既存パターンとの整合性

- ADR は既存 7 本と同じ **Context / Decision / Alternatives / Consequences / Migration** 構成。
- ステータス凡例（Accepted / Proposed / Deferred / Superseded）は `docs/adr/README.md` に従う。
- 引用は `citation-ssot`（append-only・名前空間別・恒久 ID・重複キー = DOI/arXiv/正規化 URL・
  未確定は provisional）。
- 文献カードは `literature-card`（落合フォーマット 6 項目・`_index.md` へ追記・出典は references.md へ）。
- エビデンスの温度は `gse-v2-overview.md §5`（「効くはず」で実装しない・過大主張の禁止）。

## テスト戦略

コードが無いため自動テストは無い。代わりに**機械的に検証できる不変条件**を確認する:

- `git diff --stat` に `src-tauri/` `src/` が現れないこと（コード変更ゼロ）
- 凍結対象ファイルが変更ファイル一覧に無いこと
- 本文の全 `[Pn]`/`[Vn]` が `references.md` に実在すること（citation-ssot ルール 6）
- `references.md` の新規行の番号が末尾連番であること（renumber していない）
- `.idea` の ICC 4 値（0.060 / 0.055 / 0.159 / 0.156）が新規文書に出現しないこと
- 新規文書に「KTO 的」が出現しないこと（判断 7）

## ロールバック計画

新規ファイルの削除と、修正 7 ファイルの `git checkout` で完全に戻せる（コード非依存）。
`.idea` は追跡外なのでヘッダ追記は git 管理外（手動で戻す）。
