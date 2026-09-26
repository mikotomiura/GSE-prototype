# 設計 —— Loop 基盤の是正（P1-I / J / K / B / D ＋ 起票 A）

> 方針の裁定は decisions.md 判断 1〜7（grill・研究者）。ここはその落とし込み。
> 調査: file-finder（テスト土台）／ impact-analyzer（`uncommitted` の語彙の波及）／ P1-B はメインが `claude -p` で実測。

## 根本原因（一次で確認済み）

| 起票 | 原因（ファイル:行は 2026-09-26 時点） |
|---|---|
| P1-I | `loop-run.sh` `run_issue` は `run_verify` が緑なら `ensure_branch` だけ見て `issue_done` を出す。**作業ツリーの状態とコミット数を見ていない**。verify は worktree の作業ツリーを測るので、未コミットでも緑になる |
| P1-J | `loop-spawn.sh` は `git fetch origin "$base"` が成功すると**無条件に** `start="origin/$base"`。ローカル `$base` が先行していても見ない |
| P1-K | `git worktree add -b` は upstream 設定で `.git/config` を書く。2 本同時だとロックで片方が落ちる。`set -e` なので**ブランチだけ作られた状態で die** し、片づけない |
| P1-B | worker の `allowed_tools` に acceptance 実行が無い |
| P1-D | `issue_deps_raw` の正規表現 `^\s*[-*]\s*(#|issue\s*)?[0-9]{3}\b` は `- **001**` の `**` で一致しない。拾えなかったことを誰も言わない |
| 起票 A | spawn 経路（`id="${1:?…}"` / `short="${2:-issue}"`）に `--cleanup` 経路の `case` 検証が無い |

## アプローチ

### P1-I（`loop-run.sh`・判断 5）
- `run_verify` 緑 →（recheck なら watchdog）→ **新設 `check_committed <wt> <anchor> <out>`** → `ensure_branch` → `issue_done`。
- `check_committed` は次のどちらかで失敗（非 0）:
  - `git -C "$wt" status --porcelain` が空でない（dirty。⚠️ `.claude/settings.local.json` と `src-tauri/target/` は gitignore 済みなので対象外になる —— 一次確認済み）
  - `git -C "$wt" rev-list --count "$anchor..HEAD"` が 0（`$anchor` ＝ 既存の `wt_anchor` ＝ worktree 生成時の HEAD）
  - ⚠️ `anchor` が空・rev-list が失敗 → 数えられない ＝ **done にしない側**（fail-closed）
- 失敗時: `VERIFY_KIND=uncommitted`、出力ファイルに「dirty の porcelain 一覧 ＋ コミット数」を書き、**既存の失敗経路にそのまま合流**（`emit verify uncommitted` → `check_wt_became_blocked` → fingerprint による no-progress 判定 → 次 attempt）。
  ★ 同じ未コミット状態が続けば同じ fingerprint → `no_progress_stop` で止まる（無限に回らない）。
- 語彙の追随（impact-analyzer）: `docs/loop-engineering.md` 語彙表（10 → 11 種）と Stop Condition 節、`.claude/commands/loop-status.md`（board: `uncommitted` → 🔄 running）、`.claude/commands/loop-issue.md` の「commit は文章の契約で機械強制ではない」節（モード C では機械検査あり、と更新）、`.claude/agents/loop-worker.md` の失敗種別列挙に 1 行。
  ⚠️ `loop-watchdog.md` の既存の穴（他の失敗種別も `test_fail` と書く）は範囲外（記録のみ）。

### P1-J（`loop-spawn.sh`・判断 3）
- fetch 成功後、`refs/heads/$base` が在れば `origin/$base` と比べる:

| 状態 | 判定 | start |
|---|---|---|
| ローカル無し | — | `origin/$base`（現行） |
| 一致 | sha 等しい | `origin/$base` |
| ローカル先行 | `merge-base --is-ancestor origin/$base $base` | **`$base`（ローカル）** ＋ WARN「未 push の N コミットを含む」 |
| ローカル遅れ | `merge-base --is-ancestor $base origin/$base` | `origin/$base`（現行） ＋ 情報行 |
| 分岐 | どちらでもない | **die**（worktree も branch も作らない）|

- 選んだ理由を provenance ブロック（stderr）に `start-choice=<equal|local-ahead|local-behind|no-local|fetch-failed>` として 1 行出す。
- `loop-run.sh` は spawn の stderr を run ログへ流している（既存）。加えて `start-choice=local-ahead` を見たら、attempt 1 の `attempt_start` に `detail=WARN: …` を付けて **events にも残す**（既存の WARN 作法・語彙は増やさない）。

### P1-K（`loop-spawn.sh`・判断 6）
- `LOCK="$(git rev-parse --git-common-dir)/loop-spawn.lock"` を `mkdir` で取る（stale 検出〜`worktree add` を囲む）。中に `pid` を書く。
  - 取れなければ 0.5 秒間隔で最大 120 秒待つ。待ち切れたら die。
  - 既存ロックの pid が生きていない（`kill -0` 失敗）なら stale として 1 回だけ除去して取り直す。⚠️ pid ファイルが無い／読めない（作成直後の競合）ときは stale と見なさない（待つ）。
  - 解放は `worktree add` の直後（成功・失敗とも）。`trap … EXIT` で異常終了時も解放する。⚠️ `exec claude` の前には必ず解放済み。
- `git worktree add` を `set -e` で落とさず `if ! …; then` で受け、**作られたブランチの tip が `start_sha` と同じ（＝ 何も積まれていない）ときだけ** `branch -D` して die（`abort_worktree` と同じ規則）。

### P1-B（`allowed_tools`・判断 4）—— ⚠️ 実測で前提が変わった（承認時に裁定を仰ぐ）
`claude 2.1.282`・`claude -p --permission-mode acceptEdits --allowedTools …`・haiku で実測（scratchpad、2026-09-26）:

| 規則 | 対象 | 結果 |
|---|---|---|
| `Bash(bash .steering/*/issues/*-acceptance.sh:*)` | acceptance | ❌ 拒否 |
| `Bash(bash .steering/*/issues/*-acceptance.sh *)` | acceptance | ❌ 拒否 |
| `Bash(bash .steering/:*)` | acceptance | ❌ 拒否 |
| `Bash(bash <完全なパス>)` | acceptance | ✅ |
| `Bash(bash:*)` | acceptance | ✅ |
| **`Bash(bash .steering/**/*-acceptance.sh)`** | acceptance（実タスク名のパスでも） | ✅ |
| 同上 | `bash other.sh` ／ `bash .steering/…/helper.sh` ／ 引数付き `… --x` ／ `A && bash other.sh` の後半 | ❌ 拒否（期待どおり） |
| 同上 | ⚠️ `bash .steering/../esc-acceptance.sh`（repo 直下の任意の `*-acceptance.sh`） | ✅ **通る（抜け道）** |

⚠️ 結論: **`**` 形式で機能としては効く**。ただし**境界にはならない** —— worker は `Write` を持つので `.steering/任意/…-acceptance.sh` を自分で作って実行でき、`..` でも外へ出られる。つまり権限上は `Bash(bash:*)` と同等（★ ただし `cargo run` / `cargo test` が build.rs 経由で既に任意コードを実行できる状況は変わらない）。
→ **選択肢（要裁定）**: A: `**` 規則を入れる（利便のための許可であって境界ではない、と明記）／ B: 入れずに記録（判断 4 の字義どおり）。

### P1-D（`loop-run.sh`・判断 7）
- `issue_deps_raw`: 行ごとに `*` `_` `` ` `` を剥がしてから既存の正規表現で拾う。
- 新設 `issue_deps_unparsed <id>`: Dependencies 節（装飾を剥がした後）の `\b[0-9]{3}\b` 全体 − 拾った依存。空でなければ `preflight_dag` が `log "WARN: issue X の Dependencies に依存として拾わなかった 3 桁数字: …（箇条書き行の先頭にない）"`。die しない。`--dry-run` でも出る（preflight は dry-run より前に走る —— file-finder 確認）。

### 起票 A（`loop-spawn.sh`）
- `--cleanup` 経路の `case` を関数 `validate_name <label> <value>` に括り出し、cleanup の `id`、spawn の `id` と `short` の 3 か所で呼ぶ（振る舞いは cleanup 側不変）。

## 変更対象ファイル
- `scripts/loop-run.sh` — P1-I（`check_committed`・失敗経路合流）／ P1-J の events WARN ／ P1-D
- `scripts/loop-spawn.sh` — P1-J ／ P1-K ／ 起票 A
- `scripts/loop-run-guard-test.sh` — P1-I・P1-D・P1-J の events WARN の回帰
- `scripts/loop-spawn-cleanup-test.sh` — P1-J（bare origin で 4 状態＋fetch 失敗）・P1-K（同時 2 本・add 失敗で残骸なし）・起票 A の回帰
- `docs/loop-engineering.md` ／ `.claude/commands/loop-status.md` ／ `.claude/commands/loop-issue.md` ／ `.claude/agents/loop-worker.md` — `uncommitted` の語彙と P1-J / K / D の運用記述
- （P1-B が A なら）`.steering/_template/loop-config.json` と `loop-config.README.md`

## 既存パターンとの整合
- テスト: 両テストの `ok`/`ng`・`FINISHED` trap・一時 repo（`GIT_CONFIG_GLOBAL=/dev/null`）・陰性対照＋変異の作法に乗る。
  - P1-I: `loop-run-guard-test.sh` の `setup_repo`（stub claude がファイルを書くだけ）＋ `run_loop`。
  - P1-D: 同 `dry_run` ＋ `S` 系。
  - P1-J / K / A: `loop-spawn-cleanup-test.sh` の `setup_fake_repo` を `git init --bare` の origin 付きに拡張、`do_spawn` / `do_spawn_x`。
- 失敗の記録は既存の `emit`・WARN の `detail` 作法。events 語彙は `uncommitted` の 1 語だけ増やす。

## テスト戦略
- **TDD 順**: 各起票の回帰テストを先に足し、現行実装で**赤**になることを確かめてから直す。
- 各新テストについて**判定を潰す変異**（例: `check_committed` を常に 0、`is-ancestor` 分岐を削る、ロックを外す、装飾剥がしを外す、`validate_name` を外す）で赤になることを確かめる（既存テストの変異節と同じ作法）。
- 全体: `loop-run-guard-test.sh` / `loop-spawn-cleanup-test.sh` / `loop-worktree-deny-test.sh` / `check-shell-portability.sh`（bash 3.2）/ `check-tests-are-wired.sh` を緑。終了コードは実行直後に `rc=$?`。
- Rust / gse-replay は触らないので対象外。
- 手動: 実 Loop 実行（モード C）は本タスクでは行わない（判断 1）。

## 実装中に変わった点・判明した事実（/finish-task Step 2）

- **P1-I の位置**: 当初は「verify 緑の**後**に `check_committed`」だったが、レビュー C-M3 / C-M4 で **verify の前**へ移した（`check_committed && run_verify`）。
  → `uncommitted` の意味は「verify 前の時点で未コミット／コミット 0 件（verify も watchdog も回さない）」。判断 9。
- **P1-D**: 装飾剥がし `s/[*_`]//g` だけでは `* 001` の箇条書きが拾えなくなる回帰をメインのレビューで発見 → 箇条書きの `*` を先に `-` へ正規化（`deps_section_plain`・テスト P1-D-c）。
- **P1-K**: 同時実行の競合はこの環境で 12 並列まで再現しなかった → ロックは「先に置いたロック」で決定論的に検査（11d〜11f）。stale 除去は別ロック `.reap` で直列化（C-M2）・除去を試みた周も待ち回数を進める（C-M1）。
- **P1-J**: local-ahead の `start` を無修飾の `$base` にすると同名 tag で `worktree add` が曖昧で落ちる → `refs/heads/$base` で修飾（12g）。merge-base の rc 128 と origin_sha 空は「分岐」と別メッセージで止まる（テストでは再現できず・コードのみ）。
- **P1-B**: 実測で効いた綴りは `Bash(bash .steering/**/*-acceptance.sh)` だけ。境界ではない（判断 8）。文書の「main 側の acceptance を回すので合否は動かない」は誤りとして訂正（S-M1）。
- **指示文**: empirical-prompt-tuning（`prompt-tuning.md`）で loop-issue / loop-worker の未コミット時の手順を「まず自分で commit」に直した。
- **最終テスト**: guard / spawn-cleanup 100 / worktree-deny / portability / wired すべて rc=0。
- **/cross-review の後（判断 10・11）**: 未コミット判定は「verify（と watchdog）が新しく作った未追跡だけを生成集合で除外」「`--untracked-files=all`」「skip-worktree / assume-unchanged の印を verify の前後で検出」「verify 後に HEAD と追跡ファイルの不変を確認」。
  spawn は「後始末が終わるまでロック保持」「pid を読み戻して確かめる」「自分の pid のときだけ解放」「reap の残骸を EXIT で片づける」「全経路の start を修飾し、ローカルに無い base は die」。
  ⚠️ `start="$(local_ref_or_raw …)"` の die は `set -e` によって全体を止める（コマンド置換の中の die はサブシェルしか抜けない）—— `set -e` を外すと fail-open になる点に注意。
- **最終テスト**: guard 88（3 回連続で緑）/ spawn-cleanup 118 / worktree-deny 34 / portability / wired すべて rc=0。
