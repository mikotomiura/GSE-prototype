# outcome-arbitration-and-o1-preflight

> ★ 親タスク: `.steering/20260911-intake-arbitration-branch/`（ブランチ取り込み）
> ⚠️ 本タスクは **T1（取り込み）の完了後**に着手する。ADR-024 が main に無いと裁定が書けない。

## 背景

### 1. ⚠️★★★ 転帰（未来アウトカム）の定義が 3 つ並立し、1 と 3 で主従が反転している

| # | 出典 | 時間原点 | 主イベント | 競合イベント | 構造 | 状態 |
|---|---|---|---|---|---|---|
| 1 | **ADR-009**（main） | stall onset | `recovery`（自力前進の回復） | `externalized`（paste） | 4 択・離散時間 hazard | **Proposed・凍結中・着手ゼロ** |
| 2 | **`metrics.rs`**（main・実装済み） | stuck エピソード（`p_stuck>=0.60` の連続区間） | `p_flow > 0.5` 到達 | — | 固定窓の二値判定 | 稼働中（2026-06-23 作・**ADR-009 より前**） |
| 3 | **ADR-024**（T1 で取り込み） | 離席候補ギャップ（≥180s）明けの初打鍵 | **`receipt`（external paste）の発生** | 受領を見ないまま次の離席候補ギャップが始まったこと | Aalen–Johansen 競合リスク CIF | **Accepted** |

★ **ADR-009 では paste は回復を妨げる競合イベント。ADR-024 では paste 自体が主イベント。**
⚠️ **両者の関係（上書きか別トラックか）はどの文書にも書かれていない。**
⚠️ `.idea/20260910` と `20260911`（ADR-024 の Accepted 日より後）はなお ADR-009 の 4 択語彙のまま。

### 2. ⚠️★★★ O1 はまだ開始していない（2026-09-11 に研究者が明言）

→ ★ **ラベル定義が未確定のまま収集を始めると事後選択になる。**
→ ★ **「配布後では原理的に復元できない観測」を確定する最後の機会。**

調査で見つかった配布前ギャップ（P1〜P4）:

| 優先 | 項目 | なぜ後から復元できないか |
|---|---|---|
| **P1** | macOS の IME 確定 / 放棄判別 | `ime_shadow`（`dwell_ms` / `nav` / `abandon`）は **Windows にしか無い**。macOS は `ime_state` の on/active 2 値のみ |
| **P3** | 修飾キー同時押下フラグ | 各キーが独立イベントで「同時押下」フラグが無く、通常打鍵と `Ctrl+Z` を区別できない |
| P2 | 配布する版をどのコミットにするか | → T1 の完了で解消する |
| P4 | macOS `secure_input` の実送出状況 | doc は「送出元なし」・コードは `SECURE_INPUT_AVAILABLE=true` → `blockers.md` 起票 1 |

⚠️ 当初 `KeyCategory` の `Punctuation` 追加を配布前ギャップと想定したが、
**これは既に main にマージ済み**（`feat/r3-accept-and-punctuation` = `e14b6bd` PR #113）で解消済み。
`punctuation` と `sentence_punctuation` は分離済みで、`boundary-conditioned pause` は現行記録から計算できる。

## ゴール

1. **O1 の主解析が予測する「未来転帰」の定義を 1 つに確定する**（issue 007）
2. **O1 配布前でなければ手遅れになる観測を実装する**（issue 008 / 009）

## スコープ

### 含むもの
- 転帰定義の一本化 ADR（ADR-009 と ADR-024 の関係を明文化）
- macOS の IME 確定 / 放棄判別（`ime_shadow` 相当）
- 修飾キー同時押下フラグ

### 含まないもの
- ⚠️ **ADR-009 を Accepted にすること** → ADR-009 自身が「最大の未決は G1 が `n = 0/3`」と書いており、
  G1（統制タスク実験）は自然データで代替できない（ADR-009 D7）
- ⚠️ **O1 回収後に凍結すべき項目**（期の幅 Δ / split 定義 / 勝ち幅の数値 / G-next・O-holdout）
  → 出典自身が Phase A（O1 discovery）→ Phase B（freeze・**O1 後**）→ Phase C と分けている
- ⚠️ **ADR 本文の書き換え** → ADR 本文は書き換えない規約。関係は新 ADR 側に書く
- ⚠️ **`receipt` の定義拡張**（AI 提案の accept 等）→ ADR-024 が明示的に「別 ADR の主題」として残した
- ⚠️ **セッション横断 CIF プールの実装** → ADR-024 が `N6: 未実装` と自認。本タスクでは起票のみ
- Mh-D の推論アーキ全般（→ T3 `20260911-mhd-inference-ssot`）
- メディア表現 / Practice Portrait（→ T4 `20260911-practice-portrait-ssot`）

## 受け入れ条件

- [ ] 転帰定義の一本化 ADR が書かれ、**ADR-009 と ADR-024 の関係**が理由付きで本文に明記されている
- [ ] O1 の主解析が使う **時間原点 / 主イベント / 競合イベント / 打ち切り** の 4 つが確定している
- [ ] 却下した方の定義が **Alternatives 節**に理由付きで残っている
- [ ] macOS 実機で IME の確定 / 放棄が NDJSON から判別できる（または「判別しない」と**明示的に記録**）
- [ ] `Ctrl+Z` が通常打鍵と区別できる（または 007 の裁定で不要と判断され、**その旨を記録**）
- [ ] `cargo test --workspace` / `gse-replay --snapshot` / `emit_schema` parity がすべて exit 0
- [ ] `/cross-review` を通している（skip した場合は理由を明記）

## 関連ドキュメント

- `docs/adr/ADR-009-recovery-risk-axis-and-latent-state.md`
- `docs/adr/ADR-024-resumption-outcome-without-estimator.md`（★ **T1 で取り込み後に main に出現**）
- `docs/architecture/personalization-and-online-learning.md` — `self_directed_recovery_risk` の定義
- `src-tauri/src/analysis/metrics.rs` — 現行の二値判定の実装
- `.claude/skills/hook-constraints/SKILL.md` — issue 008 / 009 で必読
- `.claude/skills/data-privacy/SKILL.md` — issue 009 で必読

## 運用メモ

- **/reimagine 適用: Yes**
- 理由: issue 007（転帰定義の一本化）は **O1 のラベル定義に直結し、やり直しが効かない**。
  設計段階で `/reimagine` を起動し、初回案を破棄して再生成した案と比較する。
  issue 008 / 009 には不要（実装作業のため）。
