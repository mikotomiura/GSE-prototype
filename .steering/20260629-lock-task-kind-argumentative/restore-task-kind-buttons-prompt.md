# 次セッション開始プロンプト（task_kind 選択ボタンの復元 / Phase1 完了後）

このタスクは **Phase1 較正が完全に終わり、論述以外のタスク種別へ研究を広げると決めた後**に実行する。
それまでは論述ロックを維持すること（非論述混入で C-index が交絡するため）。下の「===」以下をコピペして開始する。
実装タスクなので `/start-task` を先に実行し `.steering/` に記録する。

---

GSE のダッシュボードの **task_kind 選択ボタンを 4 種（論述/通信文/創作/vibe coding）に復元**する。
Phase1 較正中は論述 (argumentative) にロックしていた（`.steering/20260629-lock-task-kind-argumentative`・
ブロッカー#2 対応）。Phase1 が完了し他種別へ広げるフェーズに入ったので、ロックを解除する。
**実装タスク**なので必ず `/start-task` を先に実行し記録する。

## まず読む
1. Skill: `implementation-workflow`（共通骨格）/ `typescript-standards`（`src/` の React・any 禁止・IPC）/
   `architecture-rules`（フロントにロジックを置かない）/ `git-workflow`（コミット/ブランチ/リリース）。
2. ロックの経緯: `.steering/20260629-lock-task-kind-argumentative/`（decisions D8 付近・design.md）。

## やること（最小修正）
- `src/App.tsx` の `TASK_KINDS`（先頭付近・「Phase1 ロック」コメントの直下）でコメントアウトしている 3 種
  （`correspondence`/`creative`/`vibe_coding`）の `//` を外して復活させる。
- 同セレクタの見出し「今回の作業種別（Phase1 は論述に固定）:」を中立に戻す（例:「今回の作業種別:」）。
- 「Phase1 ロック」説明コメントは、復元した旨に更新（または除去）。
- 型 `TaskKind`（probeTypes・4 種）・backend・session_meta スキーマは**元から不変**なので変更不要。
  既定 `taskKind` は用途に応じて見直す（現状 argumentative）。

## 検証
- `npx tsc --noEmit` ＋ `npm run build`。
- 手動: スタート画面に 4 種が表示され、選択が session_meta.task_kind に反映される。
- 介入/ゲート/プローブのロジックは触らない（非回帰）。

## 仕上げ
- `/finish-task`（code-reviewer + `/cross-review`）。
- リリースする場合: **version を適切に bump**（task_kind 拡張は新フェーズ機能なので v0.1.21 同 ver 再リリースではなく
  新バージョン推奨）→ タグ push で CI ビルド。**repo を一時 PUBLIC**にしないと Actions が即 fail する点に注意
  （ビルド完了後 PRIVATE へ戻す。詳細はメモリ `build-ci-and-pilot-distribution`）。
- メモリ `pilot-calibration-label-yield-gap` / `build-ci-and-pilot-distribution` の task_kind ロック記述を「解除済み」に更新。
