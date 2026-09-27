# 次セッション — loop-run.sh の progress フラグ不具合を修正する

> 作成: 2026-09-27（`.steering/20260927-precondition8-t3-and-consent/` の実行中に発見・main=`02272e0`）。
> ⚠️ **このメモを一次資料にしない。** `scripts/loop-run.sh` は改訂され続けているので、行番号は着手時に測り直す。
> ★ **`.steering/_handoff/next-session-o1-release-tag-recut.md` と並行実行可能**
>   （触るファイルが完全に別: 本タスクは `scripts/loop-run.sh` のみ・リリース系には触れない）。

## §0 打ち込む用

```
.steering/_handoff/next-session-loop-run-progress-flag-bug.md を読んで、次を進めてください。
scripts/loop-run.sh の progress フラグの不具合（無関係な issue を巻き添えで blocked にする）
を修正してください。
⚠️ まず git pull --ff-only。/start-task（task 名: loop-run-progress-flag-fix）を実行し、
   grilling skill で修正方針（下記 §2 の 2 案のどちらか）を確定する。
★ 本番の Loop Engineering インフラを触るので、修正後は必ず「最も安い issue 1 本」で
   実地検証してから終える（docs/loop-engineering.md 逐語「新しい実行モードを初めて使う時は
   最も安い issue 1 本を parallel=1 で回して基盤を検証する」と同じ精神）。
Skill: verify-before-claiming・rust-standards は不要（bash script）。git-workflow。
応答は日本語。
```

## §1 現在の状態（2026-09-27・測り直し済み）

| 何 | 値 |
|---|---|
| main | `02272e0`（PR #237 merge 直後） |
| 不具合の実測記録 | `.steering/20260927-precondition8-t3-and-consent/blockers.md`（§1・§2の2件） |
| 影響 | `scripts/loop-run.sh` はタスク横断のインフラ。他の Loop タスクでも同型の空振りが起きうる |

## §2 不具合の詳細（一次: `scripts/loop-run.sh:1082-1104` 付近・行番号は着手時に測り直す）

### 不具合 1: progress フラグが無関係な issue を巻き添えで blocked にする

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

**実測した症状**（2026-09-27・`.steering/20260927-precondition8-t3-and-consent/`）:
issue 005（`## Dependencies: なし`・完全独立）が、無関係な issue 003 の attempt が失敗した
同じバッチ実行の中で、2 回とも `blocked（依存 issue が未完のため未実行）` にされた。
`loop/005-issue` の worktree/branch は**一度も作られていなかった**
（`git worktree list` / `git branch -vv` で確認）ため、これは「依存未了」ではなく
「そもそも試みられなかった」ことが確定している。

**原因**: `parallel=1` のとき、外側の `while` 1 周につき `batch` は**先頭から見て
`deps_met` が真の最初の 1 件だけ**を掴む（`break` の位置）。003 の `deps_met` が真だと
batch は `003` だけになり `005` はこの周では一度も見られない。003 が失敗すると
（`issue_done` イベントが出ない）`progressed` は 0 のまま。`remaining` からは 003 だけが
（成否に関わらず）外れて `005` が残る。→ `while` 条件 `progressed = 1` が偽になり
ループを抜ける。→ 末尾の「依存先が落ちて起動できなかった issue を明示的に blocked にする」
ループが、実際には依存を満たしている 005 も同じ文言で `blocked` にする。

**要点**: `remaining` からの除去（成否に関わらず batch 全員を外す）と、`progressed`
（issue_done が 1 件でも出たか）が**別の変数**なのに、`while` の継続条件が後者だけを見ている。
「このバッチは失敗した」と「他に試せる issue が無い」を混同している。

### 不具合 2（参考・修正は不要かもしれない）: issue の DAG 依存と「base へのマージ」は別物

`deps_met()` は events.jsonl の `issue_done` だけを見ており、各 issue は独立 worktree
（base からの別ブランチ）で実行される。依存先 issue が `issue_done` になっても、
**base ブランチ自体には何もマージされない**ので、依存先の**成果物の実体**を要する issue
（ファイル交差は無いが参照を要する）は、依存先を base へマージしてから spawn しないと
必ず落ちる。★ **これは仕様上の限界として許容されている可能性がある**（issue-plan 側が
「依存先が base に入ってから実行する」と明記すればよい話でもあるため）。
grill でこちらも直すかどうかを判断すること。直さないなら
`docs/loop-engineering.md` に「依存先の成果物実体を要する issue は base マージ後に spawn する」
という運用手順を明文化するだけでもよい（コード修正なしで済む）。

## §3 決めること（grill）

1. **不具合 1 の直し方**（2 案。どちらが良いか一次のコードを読んで判断する）:
   - 案 A: `progressed` を「issue_done が出たか」ではなく「`remaining` に対して deps_met が
     真になる issue が 1 件でも新たに見つかったか」で判定するよう作り直す。
   - 案 B: 失敗した issue を `remaining` から即座に除去せず、成功した issue だけ除去する形に変え、
     `deps_met` が真な issue が `remaining` に 1 件でも残っている限り `while` を継続する
     （無限ループを避けるため、同一 issue の再試行を防ぐガードが要る）。
   - ★ どちらでも良いが、**修正が「同一 issue を無限に再試行しない」ことを保証できるか**を
     テストで固定すること。
2. **不具合 2 を直すか**（コード修正 or ドキュメント明文化のみで済ませるか）。
3. 修正後、`docs/loop-engineering.md` の「モデル割当ポリシー」表・「実行モードとセッション境界」節
   との整合を確認する（★ L7 相当の drift 検出は無いので手で確認）。

## §4 検証方針

- ⚠️★★★ **本物の Loop 実行で再現・検証する**（bash script の単体テストが無いため、
  fixture task を作って実地で回すのが最も確実）。ダミーの 3〜4 issue（1 つはわざと
  失敗するように仕込む・1 つは無関係で独立）を用意し、旧実装で再現 → 新実装で解消、
  を両方実地で確認すること。
- `docs/loop-engineering.md` の既存の実測記録（`.steering/20260920-loop-foundation-fixes/`
  等）にある実測パターンを参考にする。

## §5 やらないこと

- `scripts/loop-spawn.sh` / `scripts/loop-worktree-deny.sh` 等、他の Loop 基盤ファイルの変更
  （不具合が無いか確認したら十分。今回の対象は `loop-run.sh` の progress フラグのみ）。
- worktree ブランチ検査（`ensure_branch`）や `permission_denials` の記録形式など、
  無関係な既存機構への変更。

## §6 一次資料（読む順）

1. `.steering/20260927-precondition8-t3-and-consent/blockers.md`（実測記録・本メモの出所）
2. `scripts/loop-run.sh`（着手時に最新版を読む。行番号は変わっている前提）
3. `docs/loop-engineering.md`（Loop Engineering の SSOT・実行モード表・Events 語彙）
4. `.steering/20260920-loop-foundation-fixes/`（過去の同種の実地検証パターン）
