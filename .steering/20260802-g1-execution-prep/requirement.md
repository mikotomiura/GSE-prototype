# G1 実施直前準備（D-5 の決着・本番課題文・n と実施順序の凍結）

## 背景

G1 統制タスク実験の実施資材は前ラウンド（`.steering/20260802-g1-implementation/`・
`preregistration.md` 第 2 版）で揃い、`bash run.sh` は GREEN だった。
残っていたのは **研究者判断を要する 4 件** と **本番用課題文** である。

前ラウンドで **Phase1 の実データを使って検定の到達可能域を測った**結果、2 つの問題が露見した:

1. `§2.5` の「positive control ✗ → **G1 無効**」が**誤発動しうる**。
   計器が完全に健全（AUC=1.0）でも、到達可能な最小 p が 0.05 を超える被験者が実在する
   （Phase1 実データで **4 例中 1 例**）。**n=1 では Fisher 統合による救済も無い。**
2. 主判定の帰無分布 95 パーセンタイルが **AUC ≈ 0.94**。すなわち **実質 AUC ≈ 1.0 が要る**。
   補助基準の 0.70 は全く拘束的でない。⚠️ これは `§3.7` の
   「`✗` は打鍵という計測手段への否定的証拠」という強い解釈と衝突する
   ——**検出力不足で `✗` になったものを「世界の性質」と読むことになる**。

⚠️ **どちらも、確証データを 1 件でも取る前に決着させなければ事後改訂になる。**

## ゴール

**G1 を「凍結解除後すぐ回せる」状態にする。** 実験の実施そのものは行わない。

## スコープ

### 含むもの

- **T-1** D-5 の決着（研究者判断）→ 必要なら `preregistration.md` 第 3 版 ＋ `config.json` 同期
- **T-2** 主判定の検出力についての研究者確認（`§3.7` の `✗` の解釈）
- **T-3** 本番用の課題文 **8 題材 × 2 版**（`materials/`）
- **T-4** 確証標本の n の扱いと実施順序の確定・記録
- **T-5** `/cross-review`（Claude ＋ Codex の独立レビュー）

### 含まないもの

- ★ **実験の実施**（パイロット P-1 を含む）
- `preregistration.md §3.1 / §3.2 / §3.4 / §3.5 / §3.6` の変更（**凍結**）
- `docs/preregistration-v0.3.md` / `research-positioning.md §5` の変更
- `src-tauri/` / `src/` の変更（G1 はコード変更ゼロで実施できる）
- 新規文献の登録（本ラウンドは外部文献に新規に依拠していない）

## 受け入れ条件

- [x] D-5 の採用案が確定し、変更した場合は**判定を緩めていないことが論証されている**
- [x] `§3.7` の `✗` の解釈について研究者判断が得られ、記録されている
- [x] `python3 validate_materials.py --strict` が緑（8 題材 × 2 版）
- [x] n の扱い（凍結するか、いつ凍結するか）と実施順序が `notes.md` に記録されている
- [x] `bash run.sh` が GREEN のまま
- [x] `preregistration.md` と `config.json` が齟齬なく同期している
- [ ] `/cross-review` を実施した（または skip 理由を明記した）

## 関連ドキュメント

- `experiments/20260801-controlled-friction-task/preregistration.md`（第 3 版・**判定基準の唯一の真実源**）
- 同 `config.json` / `protocol.md` / `materials/README.md` / `notes.md`
- `.steering/20260802-g1-implementation/decisions.md`（**D-5 が本ラウンドの主題**）
- `docs/adr/`（ADR-009 D7）/ `docs/architecture/personalization-and-online-learning.md §8.2`
- `.steering/_handoff/next-session-prompt-g1-execution-prep.md`（本ラウンドの入口）
