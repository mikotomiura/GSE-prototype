# タスクリスト — g1-o1-release-and-o1-resilience

## T1 v0.1.36 の配布
- [x] 状態を測り直す（PR #232 merged / main CI success / ゲート 2 本 / ディスク 21 GiB）
- [x] バージョン整合（4 ファイルとも 0.1.36）
- [x] タグ push（研究者承認: v0.1.36 → 24c5e3e）・CI 全 job success（build-macos / build-windows / release）
- [x] Release 成果物の実体検証（`LC_ALL=C grep -a`・対照あり・限界は distribution-tag.md）
- [x] G1 用 zip（`--mode g1 --tag v0.1.36`・独立に署名/版/実行ビット再検算）
- [x] 使ったタグの記録（`experiments/20260801-controlled-friction-task/distribution-tag.md`）
- [ ] Drive 差し替え・被験者送付・記録票 C（**研究者**）
- [ ] 実機通し確認（初回起動 → 計測 → アプリ内提出 → 復号側受領。研究者同席）

## T2 O1 耐障害性
- [x] subagent 調査 4 本（A1〜A4）・断定に使う箇所は一次で裏取り（decisions.md）
- [ ] 実装する修正の選択（研究者）: G-2 定期 reconcile / ロック stale の heartbeat / G-5 送信前サイズ検査 / G-1 自動起動
- [ ] 実装（O1 用の別タグ）・`/finish-task`（code-reviewer + security-checker + /cross-review）

## T3 GAS の PJ 管理
- [ ] 提案 1〜5 の採否（研究者）→ 設計
