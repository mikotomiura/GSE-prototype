# タスクリスト — intervention-ux-clarity

## 準備
- [x] intervention.rs / lib.rs (INTERVENTION_ENABLED gate) / App / Dashboard 調査
- [x] gse-replay --intervention で dogfood セッション分析 (none1082/defer29, DC=1.0)
- [x] intervention-design Skill 参照 (Monk Mode=Wall のみ無効・ルール5)
- [x] 設計承認 (Step C・Monk Mode Option A)

## 実装
- [x] App.tsx: Dashboard へ interventionEnabled を渡す
- [x] Dashboard.tsx: interventionEnabled prop 追加・Monk Mode トグルを条件表示
- [x] docs/functional-design.md: 発火/非発火条件・away_idle 全停止訂正・interventionEnabled vs Monk Mode
- [x] docs/glossary.md: Monk Mode 補強 + away_idle 追加
- [x] decisions.md: opportunity ゲート調査結果と推奨 (n 増で再評価)

## 検証
- [x] npm run build (tsc+vite) 緑・any なし
- [~] intervention.rs 無変更 → cargo test/snapshot 不変 (省略)
- [ ] 手動: interventionEnabled OFF→Monk非表示 / ON→表示 (実機・残)

## レビュー
- [x] code-reviewer (HIGH/MEDIUM なし・LOW doc 2件対応) + security-checker (PASS・no-op)。Codex は jq 不在でスキップ。
- [x] HIGH 対応: なし

## 完了処理
- [x] /finish-task: schema parity skip (schema 無変更)
- [ ] commit / push / PR
