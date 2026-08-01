# 設計 — タスク適応と scope ゲーティング

## アプローチ

設計本体を 1 本の新規文書に集約し、決定だけを ADR として切り出す。
既存文書は**ポインタだけ**を足し、実測の記録（§11-11）は起票の記録として残す。

| 成果物 | 役割 |
|---|---|
| `docs/architecture/task-adaptation-and-scope-gating.md` | **設計本体**（T-C 較正プロトコル → T-A 統合設計 → T-B 検出器の構造） |
| `docs/adr/ADR-010-task-scope-gating.md` | **決定**（D1〜D6 ＋ Alternatives ＋ Migration） |
| `docs/adr/README.md` / `ADR-006` | 一覧に ADR-010 を追加。ADR-006 に「拡張であって改訂ではない」注記 |
| `personalization-and-online-learning.md` §11-11 / §11-1 | 設計の移送先ポインタ。`phase` の暫定案 |
| `domain-adapter-boundary.md` Layer 3-4 | scope 経路の注記（原則がそのまま発火することを明示） |

## 主要な設計判断（詳細と根拠は `decisions.md`）

1. **out-of-scope は head ではなくフラグ**（`scope_fit`）。`NullHead` を作らない。
2. **scope は head 相対**。絶対的な「対象外作業」を定義しない。
3. **宣言は routing のみ・観測は割引のみ**。食い違っても **re-route しない**。
4. **推定は streaming 窓・読み出しは Decision Episode**。セッション単位は研究解析のみ。
5. **検出器は 3 項構造**（個人 OR コホート）AND 絶対ゲート ＋ 尺度 floor ＋ 縮約 ＋ **到達不能性の出力**。
6. **定数は書かない**。**正例を使わずに（in-scope 側だけで）決める**手続きだけを凍結する。
7. **Phase2 で較正するのは Writing head のみ**。Coding は未較正のまま運用、Creative は baseline を作らない。
8. **`phase` は Phase2 では意味づけしない**（暫定・研究者判断待ち）。

## 変更対象

- 新規: `docs/architecture/task-adaptation-and-scope-gating.md` / `docs/adr/ADR-010-task-scope-gating.md`
- 追記のみ: `docs/adr/README.md` / `docs/adr/ADR-006-task-kind-beta-wiring.md`（関連欄）/
  `docs/architecture/personalization-and-online-learning.md`（§11-11・§11-1）/
  `docs/architecture/domain-adapter-boundary.md`（Layer 3-4 の注記）
- **コードは 1 バイトも変更しない。**

## 検証戦略

コード変更が無いため `cargo test` / replay は対象外（回帰リスクゼロ）。代わりに文書側の整合を確認する:

- [x] 凍結対象ファイルに触れていない（`git status` で確認）
- [x] ADR-006 の Decision 本文が無改変（追記は「関連/拡張」欄のみ）
- [x] `research-positioning.md §5` を変更していない
- [x] `docs/references.md` に追記していない（新規の文献主張をしていない）
- [x] 相互参照が双方向に張られている（設計本体 ↔ ADR-010 ↔ ADR-006 ↔ §11-11 ↔ adapter-boundary）
- [x] PII・セッション日時・raw NDJSON を出力していない

## リスクと緩和

| リスク | 緩和 |
|---|---|
| 「構造を凍結した」が定数の決め方まで縛れておらず、Phase2 で結局データを見て決めてしまう | §4.5 に**禁止事項**を明記（38 セッションで定数を決めない・結果を見てから主指標を選び直さない） |
| `scope_fit` が新しいゲート機構に育つ | §3.5 を **allow-list ＋ 禁止リスト**で書いた（Layer 5-7 は `evidence_quality` しか読まない） |
| 3 項構造（B-2 のコホート項）が `§11-11` の記録（連言のみ）を越えている | 越えたことと理由を**明示**し、「仮説であって実測ではない」「Phase2 で有無を比較する」と書いた |
| 既知 4 例の当てはめが性能の証拠と誤読される | §4.2 に「**導出集合 = 検定集合**・循環している・支持するのは必要性だけ」と明記 |
