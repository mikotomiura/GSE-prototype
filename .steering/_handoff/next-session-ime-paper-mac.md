# 次セッション（Mac）— IME 論文: Mac の issue（004 / 007 / 012）をループで実行する

> 作成: 2026-09-29。★ 前の Mac 用 handoff（`next-session-ime-paper-loop-w2-mac.md`）の後継。前のものは読まなくてよい。
> ⚠️ **このメモを一次資料にしない。** 一次は `.steering/20260927-ime-observation-paper-eval-design/` の `_issue-plan.md`（§4 機械の割り当て・§7 config の注意）・`issues/004.md` `007.md` `012.md`・`decisions.md`（判断 1〜46）・`blockers.md`（B1〜B9）。状態は着手時に測り直す。
> ⚠️ G-GEAR 側は別の handoff: `.steering/_handoff/next-session-ime-paper-ggear-w5.md`（★ 2026-09-29 に W4〔014 / 018 / 019〕を merge し終え、base は `ff2a392c` 以降。判断 44〜46 が増えた。G-GEAR の 005 / 006 → 020 / 023 は **Mac の 004 が base に入るのを待っている**）。★ 両方の機械が同じ base に push するので、push の前に `git pull --no-rebase` で取り込む（force しない）。

## §0 打ち込む用（Mac で・`/clear` の直後に）

```
.steering/_handoff/next-session-ime-paper-mac.md を読んで、IME 論文の評価一式の Mac の issue（004 / 007、続けて 012）をモード C で実行し、merge ゲートを通して base に入れてください。
一次資料: .steering/20260927-ime-observation-paper-eval-design/ の _issue-plan.md（§4・§7）・issues/004.md 007.md 012.md・decisions.md（判断 34〜46）・blockers.md。
⚠️ 実行の前に docs/loop-engineering.md を Read する。base は feature/ime-eval-kit（origin から pull してから回す）。
⚠️ _loop-config.json の events_path を Mac のパスへ書き換えてから回し、その変更はコミットしない。
Skill: subagent-delegation・verify-before-claiming・git-workflow。応答は日本語。研究者の判断が要ることは AskUserQuestion で聞く。
コミットは git add パス指定（-A 禁止）。main への merge は W6 まで終わってから（研究者の判断）。
```

## §1 状態（2026-09-29）

- base `feature/ime-eval-kit` = `c1da5b8a` 以降（G-GEAR が W4 を進めているので、着手時に `git pull` で最新を取る）。G-GEAR 側で 13 本と整理（issue 028）が merge 済み。
- Mac の issue: **004**（実行器の核と dry-run・macOS の送出）・**007**（参照入力欄 macOS）は W2、**012**（単体ロガーの macOS ドライバ・依存 011 は base にある）は W3。★ 3 本とも `verify_level: parse`（判断 34・watchdog は起動しない）。任意の 026 は `blocked`。
- ★ 004 が base に入ると、G-GEAR の 005（Windows の送出）・006（1 セルの段取り）→ 023（E3）・020（W5）が動けるようになる。**004 を最優先**にする。
- 公開物の書き方（判断 36 / 42 / 43）: `papers/ime-observation/` は学術的な英語・GSE への言及なし・内部の番号（decision / issue / judgment・M0〜M13）なし・写した元との関係の語（reference implementation / upstream / verbatim copy）なし・★ ⚠ なし。各 acceptance の最後の `style_ok`（`issues/_style_check.py`）が、その issue が変えたファイルを検査する。規則の全文は `papers/README.md`。
- 契約: `papers/ime-observation/kit/formats/FORMATS.md`（英語。`plan/1` のヘッダの `recipes_sha256` / `corpus_sha256`・試行は直前のブロック行を指す・`oracle/1` の型〔全行が 2 つの時刻・`trial_begin` は試行間の待ちの後・`marker` は押下ごとに 1 行・`reset` は `block_begin` の前〕・エスケープと BOM の禁止）。
- 012 が使う照合の道具: 公開用 `kit/logger/check_manifest.py`（`--self`）／内部用 `kit/logger/check_manifest_upstream.internal.py`（`--against-upstream` / `--update --manifest manifest.macos.json --entries <spec>`）。★ 012 は macOS で初めて単体ロガーをコンパイルする（`Cargo.lock` は GSE と同じ版にそろえてある）。`main.rs` / `Cargo.toml` の直しが要れば Stop（011 の追補として研究者へ）。

## §1b 追記（2026-09-29・G-GEAR で Mac の W2 / W3 を取り込んだ後）

- ★ Mac の 004 / 007 / 012 は G-GEAR で取り込み済み（base `3e078338` 以降）。G-GEAR で `main.rs`（判断 51）の Windows のビルド・テストは緑。
- ⚠️ **G-GEAR で 004 の `emit/emit.py` を直した**（判断 52 / 53・B11）: oracle の時刻を高分解能の時計から取る・時計が 1 ms より粗ければ止まる・遅れの 95 パーセンタイルの上限は `--selftest --full` へ。→ ★ **次の Mac のセッションでは、まず `004-acceptance.sh` を clean な checkout で回し直す**（macOS では `time.time_ns()` と `perf_counter_ns()` を使う）。赤なら研究者に報告する。
- ★ 教訓（B11）: 片方の OS でしか acceptance が回らない issue でも、`check.sh` が拾う selftest は両方の OS で走る。merge したら、もう片方の機械で全 acceptance を回すまで完了としない。

## §2 手順

1. `git fetch` → `git switch feature/ime-eval-kit`（無ければ `git switch -c feature/ime-eval-kit origin/feature/ime-eval-kit`）→ `git pull --ff-only`。
2. `_loop-config.json` の `events_path` を `/Users/johnd/GSE-prototype/.steering/20260927-ime-observation-paper-eval-design/_loop-events.jsonl` に書き換える（⚠️ コミットしない。最後に `git diff` から消えていることを確かめる）。
3. `bash scripts/loop-run.sh .steering/20260927-ime-observation-paper-eval-design --issues 004,007`（main checkout に未コミット・未追跡の物があれば、他トラックの物には触らずに `LOOP_FORCE=1`）。続けて `--issues 012`。
4. merge ゲート（issue ごと）:
   - worktree の `git status` が空・`git log feature/ime-eval-kit..loop/<id>-issue` にコミットがある。
   - `loop/<id>-issue` を detached で短いパスの clean な worktree に出し、そこを cwd にして `bash .steering/20260927-ime-observation-paper-eval-design/issues/<id>-acceptance.sh > out 2>&1; echo $?`（⚠️ 終了コードはパイプの後ろで取らない）。
   - `code-reviewer` と `security-checker` を 1 メッセージで並列に（範囲 = `feature/ime-eval-kit...loop/<id>-issue`・read-only・clone しない・重い検査を名指しで禁止・締切 15 分・「公開物の書き方は style_ok が見ている」）。
   - 契約を変える指摘は AskUserQuestion で研究者に聞く。仕様の範囲の直しは作業用エージェント（`general-purpose`・`model: sonnet`）に worktree で直させる（★ 指示に「main checkout を触らない・`git checkout --` で戻さない・入れ子にしない・判断 36 の書き方・締切」を書く）。戻ってきたらメインが clean な checkout で確かめる。
5. `git merge --no-ff loop/<id>-issue` → merge 済みの全 acceptance を clean な checkout で回す（⚠️ `require_os` が Windows の issue〔005 008 009 013 014〕は Mac では exit 2 ＝「この機械で回すな」で、失敗ではない）→ `git pull --no-rebase`（G-GEAR が先に push していれば）→ `git push origin feature/ime-eval-kit` → `bash scripts/loop-spawn.sh --cleanup <id>`。
6. `tasklist.md` の W2 / W3 の Mac の行を更新してコミット・push。

## §3 気をつけること

- ⚠️ **worker に合成キーを送らせない**。004 の実バックエンドは `--i-understand-this-sends-keys` が無ければ送らない（AC）。acceptance も送らない。実際に送るのはパイロット（M1）で、人とメインが行う。
- ⚠️ `check.sh` は Windows の機械でも回る → macOS 専用の部品に selftest の目印を付けるなら、macOS 以外では「対象外」で exit 0 にする（004 の Scope）。
- ⚠️ Swift の `JSONEncoder` は既定で `/` をエスケープする → `.withoutEscapingSlashes`（007）。BOM を付けない。
- ⚠️ 文書にユニコードエスケープの例（バックスラッシュ u と 16 進 4 桁）を書かない（ツールの入力で化ける）。
- ⚠️ GSE 本体（`src-tauri/` ほか）を変えない。人の打鍵データを使わない。プロトコル凍結（M3）の前に ImeShadow と正解を突き合わせない。新しい公開 repo を作らない。main へ merge しない（W6 の後）。
