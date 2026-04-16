# 設計案比較

## v1 の要旨
既存 hook を個別に改修。各 hook に [PASS] 表示を追加し、UserPromptSubmit を動的スクリプトに差し替える。
SessionStart に hook 一覧、PostToolUse に fmt 結果報告を追加。
各 hook が独立して自分のステータスを報告する「分散型」アプローチ。

## v2 の要旨
UserPromptSubmit を「Preflight Dashboard」として中央ゲート化。毎ターン 1 つのスクリプトが
全チェック（.steering/ 状態、未コミット変更、reimagine 適用状態）を一括実行し、
コンパクトなダッシュボード形式で表示。PreToolUse は補助的な guard 層として PASS 表示を追加。
3 層構造（Preflight / Guard / Report）で責務を明確分離する「集約型」アプローチ。

## 主要な差異

| 観点 | v1 | v2 |
|---|---|---|
| アーキテクチャ | 分散型（各 hook が独立報告） | 集約型（preflight が中央ゲート） |
| 毎ターンの可視性 | UserPromptSubmit のみ動的化 | UserPromptSubmit がダッシュボード（全状態を一望） |
| Edit なしターンの可視性 | SessionStart 後は何も見えない | preflight が毎ターン表示 → 常に見える |
| 新規ファイル数 | 2 (user-prompt-check.sh, post-edit-fmt.sh) | 1 (preflight.sh) |
| 出力プレフィックス | [PASS] / [CHECK] / [BLOCKED] (3種) | [preflight] / [guard] / [fmt] (層別3種) |
| /reimagine 強制 | なし（チェック項目に含まれない） | preflight で design-v1.md 有無を検出・WARNING 表示 |
| SessionStart 変更 | hook 一覧を追加 | 変更なし（preflight が毎ターン補完するため不要） |
| UserPromptSubmit の BLOCK | 言及なし | 明示的に「BLOCK しない」判断（作業不能防止） |
| 設計の凝集度 | 低（5 hook を個別改修） | 高（preflight に集約、guard/report は補助） |
| 変更規模 | 修正 6 ファイル + 新規 2 | 修正 5 ファイル + 新規 1 |

## 推奨案
**v2（Preflight Dashboard 方式）** — 理由:

1. **本質的な問題解決**: 「Edit なしのターンで何も見えない」問題は v1 では解決しない。v2 の preflight は毎ターン発火するため完全に解決
2. **/reimagine 検出**: v2 は design-v1.md の有無で reimagine 適用状態を自動検出。v1 にはこの機能がない
3. **変更規模が小さい**: 新規ファイル 1 つ、層別の責務分離で保守性が高い
4. **情報の集約**: ユーザーは preflight の 2-3 行を見るだけで全状態を把握できる。v1 は各 hook の出力をバラバラに見る必要がある
