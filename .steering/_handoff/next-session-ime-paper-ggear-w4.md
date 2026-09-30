# 次セッション（G-GEAR）— IME 論文: W4（014 / 018 / 019）の merge ゲートから、W5 / W6 へ

> ✅ **完了（2026-09-29）**: W4 の 3 本を merge した（base `ff2a392c`・判断 44〜46）。★ 後継は `.steering/_handoff/next-session-ime-paper-ggear-w5.md`。このメモは読まなくてよい。

> 作成: 2026-09-29（前セッションの context が 90% に達したため切り替え）。
> ⚠️ **このメモを一次資料にしない。** 一次は `.steering/20260927-ime-observation-paper-eval-design/` の `_issue-plan.md`（§2 波・§4 機械の割り当て・§5 マイルストーン）・`issues/NNN.md`・`decisions.md`（判断 1〜43）・`blockers.md`（B1〜B9）・`tasklist.md`。状態は着手時に測り直す。
> ⚠️ Mac 側（004 / 007 / 012）は別の handoff: `.steering/_handoff/next-session-ime-paper-mac.md`。

## §0 打ち込む用（G-GEAR で・`/clear` の直後に）

```
.steering/_handoff/next-session-ime-paper-ggear-w4.md を読んで、IME 論文の評価一式の W4（issue 014 / 018 / 019）の状態を測り直し、merge ゲートを通して base に入れてください。終わったら W5（020）・W6（024）の段取りに進む前に研究者に確認してください。
一次資料: .steering/20260927-ime-observation-paper-eval-design/ の _issue-plan.md・issues/014.md 018.md 019.md・decisions.md（判断 36〜43）・blockers.md。
⚠️ 実行の前に docs/loop-engineering.md を Read する。base は feature/ime-eval-kit。
Skill: subagent-delegation・verify-before-claiming・git-workflow。応答は日本語。研究者の判断が要ることは AskUserQuestion で聞く。
コミットは git add パス指定（-A 禁止）。main への merge は W6 まで終わってから（研究者の判断）。
```

## §1 状態（2026-09-29 の切り替え時点）

- base `feature/ime-eval-kit` = **`c1da5b8a`**（push 済み）。merge 済み: 001 002 003 008 009 010 011 013 015 016 017 021 022 ＋ 整理（issue 028）。merge 後の base で 13 本の acceptance・028・`_style_check.py`（違反 0 件）がすべて緑。
- ★ **W4 は研究者の指示で止めた**（2026-09-29）。`loop-run.sh --issues 014,018,019` を起動した後、014 の attempt 1 の途中で loop-run と worker（`claude -p "/loop-issue 014"`）を止めた。残ったプロセスは無い。
  - 014 の worktree `C:/wt/GSE-prototype-014-issue`（ブランチ `loop/014-issue`）は残っているが、**変更もコミットも無い**。events の最後は 014 の `attempt_start`（`issue_done` も `blocked` も無い）。
  - 018 / 019 は始まっていない。
  - → ★ 次のセッションでは、まず `bash scripts/loop-spawn.sh --cleanup 014` で worktree とブランチを片付けてから、W4 を最初から回す: `LOOP_FORCE=1 bash scripts/loop-run.sh .steering/20260927-ime-observation-paper-eval-design --issues 014,018,019`（バックグラウンド）。
- 判断の要点（詳細は decisions.md）:
  - 判断 34: 未実行の issue はすべて `verify_level: parse`（watchdog は bash / python を実行できず空応答で止まるため）。合否は**メインが clean な checkout で回す acceptance** とレビューで決める。
  - 判断 36 / 42 / 43: **公開物の書き方** —— `papers/ime-observation/` は学術的な英語・GSE への言及なし・内部の番号（decision / issue / judgment・M0〜M13）なし・写した元との関係の語（reference implementation / upstream / verbatim copy）なし・★ ⚠ なし。出どころは `*.internal.*` と manifest の `upstream_*` の欄だけ。機械の門は `issues/_style_check.py`、各 acceptance の最後の `style_ok`。規則の全文は `papers/README.md`。
  - 判断 41: 014 は IME の開閉を追わない。**候補窓の観測関数**（`candidate.rs`・cloak / EnumWindows / UIA の OR と stale のリセット）を `DriverHandle.candidate_window_observer` で核に渡す（014 の AC8）。
  - 照合の道具: 公開用 `kit/logger/check_manifest.py`（`--self` だけ）／内部用 `kit/logger/check_manifest_upstream.internal.py`（`--against-upstream` / `--update`）。

## §2 手順

1. **状態を測る**: `tail -5 .steering/20260927-ime-observation-paper-eval-design/_loop-events.jsonl`・`git worktree list`・`ps` 相当で loop-run が生きているか。
   - まだ走っていれば完了を待つ（Monitor で events を見る）。
   - 止まっていて `issue_done` の無い issue が残っていれば: その worktree の `git status` と `git log feature/ime-eval-kit..loop/<id>-issue` を見る（コミットがあれば残す判断を研究者に聞く・無ければ `bash scripts/loop-spawn.sh --cleanup <id>`）→ `LOOP_FORCE=1 bash scripts/loop-run.sh .steering/20260927-ime-observation-paper-eval-design --issues <残りの id>` をバックグラウンドで回す。
   - ⚠️ main checkout に別トラックの未追跡ディレクトリがあるので `LOOP_FORCE=1` が要る（B1）。★ それらには触らない。
2. **merge ゲート（issue ごと）**:
   - worktree の `git status` が空・コミットがあること。
   - clean な checkout を**短いパス**に出す（`git worktree add --detach /c/wt/clean-<id> loop/<id>-issue`。⚠️ scratchpad の長いパスだと Rust の `target/` が消せない・B7）。そこを cwd にして `bash .steering/20260927-ime-observation-paper-eval-design/issues/<id>-acceptance.sh > out 2>&1; echo $?`（⚠️ 終了コードはパイプの後ろで取らない）。
   - レビュー: `code-reviewer` と `security-checker` を 1 メッセージで並列に。★ 範囲（三点リーダ `feature/ime-eval-kit...loop/<id>-issue`）・read-only・clone しない・`cargo` を回さない・締切 15 分・「公開物の書き方は style_ok が見ている」を書く。014 は `hook-constraints` / `rust-standards` を参照させる。
   - 契約・設計に関わる指摘は AskUserQuestion で研究者に聞く。仕様の範囲の直しは作業用エージェント（`general-purpose`・`model: sonnet`）に worktree で直させる（★ 指示に「main checkout を触らない・`git checkout --` で戻さない・入れ子にしない・判断 36 の書き方・締切」を必ず書く・B6）。戻ってきたらメインが clean な checkout で acceptance を回して確かめる。
   - `git merge --no-ff loop/<id>-issue` → 3 本そろったら clean な checkout で **merge 済みの全 acceptance**（001 002 003 008 009 010 011 013 014 015 016 017 018 019 021 022 028）と `_style_check.py` を回す → push → `loop-spawn.sh --cleanup <id>`。
3. `tasklist.md` の W4 を更新してコミット・push。
4. **W5 / W6 の前に研究者に確認**: W5 = 020（実験一式と 1 コマンドの再現・依存 006 は Mac の 004 の後）、W6 = 024（公開 repo への書き出し）。023（E3）も 006 待ち。★ Mac 側の 004 → 006 が先に要る。

## §3 気をつけること

- ⚠️ 作業用エージェントが報告の後もバックグラウンドの処理を残すことがある（B9）。merge の直前に worktree の `git status` と HEAD を確かめる。
- ⚠️ `closed_set.py` の selftest が 22 秒（入口の警告の目安 30 秒に近い・B8）。遅くなったら重い検査を `--selftest --full` に分ける。
- ⚠️ 文書にユニコードエスケープの例（バックスラッシュ u と 16 進 4 桁）を書かない（ツールの入力で化ける・memory `feedback-backslash-via-bash-heredoc`）。CR の確認は `tr -cd '\r' < f | wc -c`。
- ⚠️ GSE 本体（`src-tauri/` ほか）を変えない。人の打鍵データを使わない。プロトコル凍結（M3 / M6）の前に ImeShadow と正解を突き合わせない。新しい公開 repo を作らない（M12・研究者）。main へ merge しない（W6 の後）。
