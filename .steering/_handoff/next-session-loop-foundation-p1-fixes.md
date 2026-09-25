# 次セッション — A. Loop 基盤の是正（P1 前タスクで踏んだ起票 P1-B / D / H / I / J / K ＋ 起票 A）

> 作成: 2026-09-26。⚠️★★★ **このメモを一次資料にしない。**
> ★ 一次は `.steering/20260921-p1-prereg-cli-poles/decisions.md`（**起票 P1-B / D / H / I / J / K**・判断 18 / 21 / 22）／
> 同 `_loop-retrospective.md`（§2 原因の内訳）／ `.steering/20260921-loop-spawn-resolve-base/blockers.md`（**起票 A**）／
> `docs/loop-engineering.md`（Loop の SSOT）。

## §0 打ち込む用（★ 新しいセッションにこのまま貼る）

```
.steering/_handoff/next-session-loop-foundation-p1-fixes.md を読んで、A（Loop 基盤の是正）を実施してください。

対象の起票（一次は .steering/20260921-p1-prereg-cli-poles/decisions.md と _loop-retrospective.md）:
  P1-I  issue_done がコミット 0 件でも出る（worker が max_turns で未コミットのまま終わる）
  P1-J  loop-spawn が upstream のある作業ブランチでは origin/<branch> から切る（ローカルが先行していても）
  P1-K  --parallel 2 の同時 spawn が .git/config のロックで片方落ちる
  P1-B  worker が bash <acceptance> / python を実行できない（allowed_tools）→ acceptance を自己検証できない
  P1-D  issue_deps_raw が「- **001**」の太字を黙って落とす（警告も出ない）
  P1-H  verify が issue 自身の acceptance しか回さない（他の門の破損が見えない）
  起票 A（.steering/20260921-loop-spawn-resolve-base/blockers.md）spawn 経路の id / short が無検査

⚠️ 実装タスクなので /start-task が先（.steering/ に requirement / design / tasklist）。
★ 設計判断は Opus、実装は Sonnet。サブエージェントは model を毎回明示・入れ子禁止・範囲と禁止事項・締切。
⚠️ git add -A / git add <dir> は使わない。main から作業ブランチを切る（例: fix/loop-foundation-p1）。
⚠️ .codex/budget.json を git checkout -- で戻さない（台帳）。/cross-review は Codex gpt-6-astra。
応答は日本語。状態は一次で確かめ直すこと。
```

## §1 前タスクの状態（★ 2026-09-26 実測）

- ★ P1 前タスク（issue 001〜009）は **main へ merge 済み**（PR #222 `d529a72` ／ PR #223 `b7030d13`・CI 全緑）。
- ★ 作業ツリーには**別トラックの未追跡ディレクトリ** `.steering/20260921-media-expression-theory-audit/`（C の材料）がある。⚠️ 消さない・コミットしない（`loop-spawn` の dirty 判定に当たるので、Loop を回すなら `git stash push -u -- <dir>` で退避し、終わったら戻す）。

## §2 ★ 各起票の要点と、是正案の出発点（⚠️ 設計は /start-task で決め直す）

| 起票 | 何が起きたか（実測） | 是正案の出発点 |
|---|---|---|
| **P1-I** | 005 / 008 で worker が max_turns 到達・**実装が未コミット**のまま verify 緑 → `issue_done`。そのまま merge すると空の merge | `issue_done` の直前に「`base..HEAD` のコミット ≥ 1 かつ 作業ツリーがクリーン」を検査。満たさなければ `blocked`（理由つき） |
| **P1-J** | PR のために push した後、ローカルで 005 を merge したが push しておらず、006 の worktree が **005 を含まない `origin`** から切られた（provenance は「1 コミット後ろ」と警告していたが無人で読まれず） | ローカルが upstream より**先行**していたらローカルを採る、または **fail-closed**。乖離の警告を events にも出す |
| **P1-K** | 007 ‖ 008 の同時 spawn で `error: could not lock config file .git/config`。008 はブランチだけ作られ worktree 無し | spawn を直列化（ロック）するか、短い間隔でリトライ。⚠️ 失敗時に残ったブランチを片づける |
| **P1-B** | worker は `bash <acceptance>` が承認待ちで拒否され、acceptance の欠陥（`--exact`・jq）を自分で見つけられず、Loop の verify で初めて赤になった | `_loop-config.json` の `allowed_tools` に acceptance 実行の許可を足す案。⚠️ 任意の bash を許すことになるので、**パスを限定した形**を検討（`Bash(bash .steering/*/issues/*-acceptance.sh:*)` 等が効くか実測） |
| **P1-D** | `- **001**（…）` の太字で依存が**黙って全部落ちた**（dry-run で全 issue `deps=[]`） | 太字・装飾を剥がしてから拾う。⚠️ 拾えない 3 桁数字が Dependencies 節にあれば**警告**（黙らない） |
| **P1-H** | Loop の verify は issue 自身の acceptance しか回さず、`envelope-acceptance.sh` ほか旧タスクの完全一致の門の破損が見えなかった（001 / 004 / 005） | verify に「回帰 acceptance の一覧」（config で指定）を足す案。⚠️ worker が他の門を直せないと blocked になるので、**分解で Allowed Files に入れる運用（判断 22）と組**で |
| **起票 A** | spawn 経路の `id` / `short` が無検査（`--cleanup` 側だけ検証） | spawn 側にも同じ検証を入れる |

## §3 ⚠️ 既知の検査手段（★ 流用する）

- `scripts/loop-run-guard-test.sh`（stub の `claude` で loop-run を実際に回す。W1〜W4 が 2026-09-25 の blocked 検知）／ `scripts/loop-spawn-cleanup-test.sh` ／ `scripts/check-shell-portability.sh`（bash 3.2）。
- ⚠️★★★ **検査を書いたら、判定を潰す変異で赤になることを確かめる**（memory `feedback_acceptance_self_test`）。
- ⚠️ 終了コードは**実行直後に `rc=$?`** で退避する（`echo "$(…)=$?"` は `$?` が壊れる —— 2026-09-25 実測）。

## §4 ★ A の後の予定（★ 研究者と合意 2026-09-26・未踏の提出は 2027 年 3 月頃）

1. **A**（本メモ）—— ⚠️ **範囲を絞る**: 優先は P1-I / J / K / B / D。P1-H（verify の回帰範囲）は設計が重いので後回し可。
   ★ **並行して S0**（研究案の文献台帳・`/literature-review`・コードに触らない）を回してよい。
2. **B → D**: ⚠️ **B が先**（事前宣言の新版 v1.1 = 出力表に `ime_overlap` を足して再凍結するか。★ 実データを見る前に凍結し終える）→ D（P1 本体の準備: 凍結値で実データを 3 極で回して解析する段取り）。
3. O1 / G1 の収集中に **「C ＋ 研究案」を 1 トラックで**:
   `.steering/20260921-media-expression-theory-audit/`（C）と `.idea/20260925-stall-choice-media-intervention-study-draft.md`（研究案・EH0）は重なる（研究案 S2 ≒ C の形成的比較）。
   ★ 工程: §6 の決めたい 5 点の議論（S0 の後）→ S1（日誌・面接の設計・別同意）→ S2（合成 trace での試作・壁紙 / 可視端）。S3（介入効果の事前登録）はずっと後。
   ★ 未踏の提出（2027 年 3 月頃）には S2 まで間に合えばよい見込み（S2 を D より前に繰り上げる必要はない）。
