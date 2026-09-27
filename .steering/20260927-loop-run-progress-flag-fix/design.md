# 設計 — loop-run-progress-flag-fix

## アプローチ

`scripts/loop-run.sh` の DAG 実行ループから `progressed` を消し、継続条件を `while [ -n "$remaining" ]` だけにする
（decisions.md 判断 1・案 A）。「試せる issue が無い」の判定は、既存の `[ -n "$batch" ] || break` がそのまま担う。

### 停止と非再試行の論証
- バッチに入った issue は、成否に関わらず `remaining` から外れる（この行は変えない）。
- ループはバッチが空でないときだけ続くので、1 周ごとに `remaining` は 1 件以上減る。
  → 周回数は多くても issue 数まで。同じ issue が同じ run で 2 回バッチに入ることはない。
- 失敗した issue に依存する issue は `deps_met` がずっと偽なので、バッチに入らず `remaining` に残る。
  バッチが空になった時点でループを抜け、末尾の既存ループで `blocked` になる（従来どおり）。

## 変更対象
- `scripts/loop-run.sh` — DAG 実行ループ（`progressed` を削除し、根拠をコメントに書く）
- `scripts/loop-run-guard-test.sh` — P 節（P1 / P2）と M-prog 変異テスト
- `docs/loop-engineering.md` — 2026-09-27 の是正節（不具合 1 の記録と、不具合 2 の運用手順）

## テスト戦略（判断 3）
- **P1**: 001 = 必ず失敗（stub が `loop/001*` ブランチではコミットしない → uncommitted → abandoned）／
  002 = 独立／003 = 001 に依存／004 = 002 に依存。期待する結果は次のとおり。
  - 002 と 004 が `issue_done`
  - 003 が「依存 issue が未完」の `blocked` で、`attempt_start` は 0 件
  - 001 の `attempt_start` が 1〜2 件（`max_attempts` を超えない）
  - 002 と 004 の `attempt_start` がちょうど 1 件（再試行しない）
- **P2 陰性対照**: 全部成功する stub なら 4 本とも `issue_done` になり、`blocked` は 0 件。
- **M-prog**: sed を 2 か所当てて旧実装そのものを戻すと、P1 の判定が赤になる。
