# タスクリスト

## 準備
- [x] ハンドオフ `.steering/_handoff/next-session-prompt-signal-diagnostics-unresolved.md` を読む
- [x] `docs/loop-engineering.md` を読む (CLAUDE.md の loop 節が要求)
- [x] `notes.md` / `decisions.md` (前タスク) / `diagnostics.py` / `.idea` §1 を読む
- [x] Skill `reproducibility-discipline` / `git-workflow` を参照
- [x] **§0 判断: Loop に載せない** → `decisions.md` D1 (ユーザー承認済み)

## 調査 (総当たり)
- [x] `probe_variants.py` を新設 (本体に混ぜない・`diagnostics.py` から import して定義の二重化を回避)
- [x] ① セル数の定義を総当たり (648 通り) → 単一候補まで復元 (D4)
- [x] ② 相関の取り方を総当たり (384 通り) → 条件を特定・自分の実装側の誤りだった (D3)
- [x] ③ ICC の式 × 前処理を総当たり (336 通り) → `.idea` は η² と判明 (D2)

## 本体への反映
- [x] `d4_icc` に `eta_squared` を併記 (ICC(1) 自体は変えない)
- [x] `d2_d3` に `term_correlations_with_recalc_x_beta_writing` を追加 (`.idea` の条件を再現可能に)
- [x] `render()` / `metrics.json` を更新
- [x] `notes.md` §1 突合表 3 行 / §2-A1 / §2-B / §2-C / §3 を更新
- [x] `.idea` §1 に結果を追記 (gitignore・コミットには乗らない)

## 検証
- [x] `check_notes.py` を新設 (notes.md / metrics.json ⇔ results/diagnostics.json)
- [x] `acceptance.sh` を新設 (7 項目)
- [x] `acceptance.sh` が全項目 PASS
- [x] `check_notes.py` が空振りしないことを負のテスト 6 本で確認 (値の変更 / 桁の追加 / 別行に同値 / probe の件数 / P1 の解釈 / P3 の式)
- [x] `cargo test --workspace` (Rust 無変更の確認 — 23 passed / 0 failed)

## レビュー
- [x] code-reviewer + security-checker (並列)
- [x] `/cross-review` (TASK-POST) — ICC(1) vs η² の判断を独立再検証・誤りなし
- [x] HIGH 指摘への対応 (check_notes.py の素通り経路 2 件 → decisions.md D7)

## 完了処理
- [x] design.md / decisions.md の最終化
- [ ] git commit (**パス指定のみ**。`git add -A` / `commit -a` は使わない)

## やらないこと (スコープ外・確認済み)
- ADR-008/009 の起票 → 本タスクの結論を入力に別タスク
- `engine.rs` / `features.rs` の変更 → 診断は Python 側で完結
- `notes.md` §4 の統計上の限界 3 件の解消 → 設計上の限界として明示済み
</content>
