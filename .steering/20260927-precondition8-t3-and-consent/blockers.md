# 詰まりと解決

## 1. `loop-run.sh` の progress フラグが、無関係な issue を巻き添えで `blocked` にする（2026-09-27・実測）

**症状**: issue 005（`## Dependencies: なし`・完全独立）が、依存関係の無い issue 003 の attempt が
失敗した同じバッチ実行の中で、2 回とも `blocked（依存 issue が未完のため未実行）`にされた。
loop/005-issue の worktree/branch は**一度も作られていなかった**（実測: `git worktree list` /
`git branch -vv` に該当なし）ため、これは「依存未了」ではなく「そもそも試みられなかった」ことが
確定している。

**原因（`scripts/loop-run.sh:1082-1104` の実装を読んで特定）**:

```bash
remaining="$ALL"; progressed=1
while [ -n "$remaining" ] && [ "$progressed" = "1" ]; do
  progressed=0; batch=""
  for id in $remaining; do
    deps_met "$id" || continue
    batch="$batch $id"
    [ "$(printf '%s' "$batch" | wc -w)" -ge "$PARALLEL" ] && break
  done
  [ -n "$batch" ] || break
  pids=""
  for id in $batch; do run_issue "$id" & pids="$pids $!"; done
  for p in $pids; do wait "$p" || true; done
  for id in $batch; do
    if jq -e -s --arg i "$id" 'any(.[]; .issue==$i and .event=="issue_done")' "$EVENTS" >/dev/null; then
      DONE_IDS+=("$id"); progressed=1
    fi
    remaining="$(printf '%s\n' $remaining | grep -vx "$id" || true)"
  done
done
```

`parallel=1`（本タスクの pin）のとき、外側の `while` 1 周につき `batch` は**先頭から見て
`deps_met` が真の最初の 1 件だけ**を掴む（`break` の位置）。`remaining` に `003 005` が残っている状態で
003 の `deps_met` が真（001/002/004 が `DONE_IDS` に入っている）だと、batch は `003` だけになり
`005` は**この周では一度も見られない**。003 が失敗すると（`issue_done` イベントが出ない）
`progressed` は 0 のまま、`remaining` からは 003 だけが（成否に関わらず）外れて `005` が残る。
→ `while` 条件 `progressed = 1` が偽になり**ループを抜ける**。
→ 末尾の「依存先が落ちて起動できなかった issue を明示的に blocked にする」ループが、
**実際には依存を満たしている 005 も**同じ文言で `blocked` にする。

**要点**: `remaining` からの除去（成否に関わらず batch 全員を外す）と、`progressed`（issue_done が
1 件でも出たか）が**別の変数**なのに、`while` の継続条件が後者だけを見ている。「このバッチは失敗した」
と「他に試せる issue が無い」を混同している。

**回避（本タスクで実施）**: 003 を base へマージ後に再実行して解消したのち、
`bash scripts/loop-run.sh <task-dir> --issues 005` で単独実行し `issue_done` を得た。

**恒久修正は本タスクの範囲外**（`scripts/loop-run.sh` は task 横断のインフラ）。
★ 次に `loop-run.sh` を触るセッションは、`deps_met` が真な `remaining` が 1 件でも残っているなら
`progressed` に関わらず `while` を続ける形（例: 「今回のバッチで新たに試せた issue が 0 件」を
別途判定する）に直すべき。起票のみ行い、本タスクでは修正しない
（`## Allowed Files` に `scripts/loop-run.sh` を含む issue が無いため・スコープ外の変更は
Stop Condition に該当）。

## 2. issue の DAG 依存と「base へのマージ」は別物（`loop-run.sh` が自動でマージしない）

**症状**: issue-plan は「003 は 001/002/004 が**この作業ブランチに入ってから**実行する」と明記していたが、
`loop-run.sh` の `deps_met()` は events.jsonl の `issue_done` だけを見ており、各 issue は
独立 worktree（base からの別ブランチ）で実行される。001/002/004 が `issue_done` になっても、
**base ブランチ自体には何もマージされない**。003 の worktree は base から切られるため、
001/002/004 の成果物（`participation_status` / `recruitment_closed` / T3 台帳）を**一切含まない**
状態で起動し、AC が必ず落ちる。

**発見経緯**: 003 は 1 回目の attempt で自ら一次資料を確認し（`git worktree list` /
`issues/00{1,2,4}.md` の `## Status` を確認）、正しく `blocked` と記録して停止した
（★ verify-before-claiming の規律どおり、実装せず事実確認だけで止まった好例）。

**対応**: オーケストレータ（本セッション）が `git merge --no-ff loop/00{1,2,4}-issue` を
base ブランチへ手動実施してから 003 を再実行した。

**恒久修正は本タスクの範囲外**: モード C の「ウェーブ間で base へマージする」手順は
`docs/loop-engineering.md` に明文化されていない（issue-plan には書いたが、実行者への
一般手順としては未整備）。次に `docs/loop-engineering.md` を改訂するセッションは、
「依存 issue の**成果物実体**を要する issue（ファイル交差は無いが参照を要する）は、
依存先を base へマージしてから spawn する」という手順を明文化することを検討する。
