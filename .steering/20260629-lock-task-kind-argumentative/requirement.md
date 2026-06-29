# 要件: task_kind を論述 (argumentative) にロック (Phase1 ブロッカー #2)

## 背景
Phase1 較正は **論述限定**。しかし `src/App.tsx` の `TASK_KINDS` は 4 種（論述/通信文/創作/vibe coding）を
選択可能で、既定が論述なだけ。被験者が非論述を選ぶと **C-index がタスク種別で交絡**する
（2026-06-29 Phase1 実行可否レビューのブロッカー #2）。

## ゴール
スタート画面の作業種別セレクタを **論述のみ**に固定し、非論述を選べなくする。
backend / 型 `TaskKind`（4 種）・session_meta スキーマは不変（収集後に種別を広げられる）。

## 受け入れ条件
- [ ] スタート画面で task_kind が論述固定（他種別が選べない）。
- [ ] session_meta.task_kind は従来通り `argumentative` を記録（非回帰）。
- [ ] Phase1 完了後に種別を戻せるよう、復活手順が自明（コメントアウト保持）。
- [ ] `npx tsc --noEmit` 通過。介入/ゲート/プローブのロジックは触らない。

## 非対象
- backend の TaskKind enum 変更（4 種維持）。analysis ロジック。
