# 次セッション（Mac）— IME 論文: G-GEAR で merge した W3 の残り・W5 と、直した `emit.py` を Mac で確かめる

> 作成: 2026-09-29。**2026-09-30 に §0 を書き換えた**: 前回の §0（`emit.py` の判断 52 / 53 の確認）は Mac で済んでいる（`36dd894e`）。今回やることは §1c の確認だけ（ループは回さない）。
> ⚠️ **このメモを一次資料にしない。** 一次は `.steering/20260927-ime-observation-paper-eval-design/` の `decisions.md`（判断 55〜65）・`blockers.md`（B10〜B12）・`tasklist.md`。状態は着手時に測り直す。
> ⚠️ G-GEAR 側は別の handoff: `.steering/_handoff/next-session-ime-paper-ggear-w6.md`（G-GEAR の次は W6 = 024）。★ 両方の機械が同じ base に push するので、push の前に `git pull --no-rebase` で取り込む（force しない）。

## §0 打ち込む用（Mac で・`/clear` の直後に）

```
.steering/_handoff/next-session-ime-paper-mac.md を読んで、§1c のとおり G-GEAR で merge した分（005 006 020 023 と、004 の emit.py の追補・判断 59）を Mac で確かめてください。ループは回さない。
手順: base（feature/ime-eval-kit）を origin から取り込む（main checkout を別セッションが使っていれば、B10 のとおり base 用の worktree で扱う・ブランチを切り替えない）。clean な checkout で、Mac で回せる merge 済みの全 acceptance（001 002 003 004 006 007 010 011 012 015 016 017 018 019 020 021 022 023 028・Windows 専用の 005 008 009 013 014 は exit 2 ＝対象外）を回す（出力はファイルへ・終了コードはパイプの後ろで取らない）。あわせて python3 papers/ime-observation/kit/emit/emit.py --selftest --full（機械が空いた状態で）と python3 papers/ime-observation/kit/analysis/pipeline.py --selftest --full。§1c の 3（E3 のプロセス名）も確かめる。
緑なら tasklist.md の「⚠️ Mac: …」の行に結果を書いてコミットし、git pull --no-rebase の後に push する。赤なら直さずに研究者に報告する（B11 の教訓: 片方の機械でしか回していない selftest が、もう片方で赤になりうる）。
一次資料: .steering/20260927-ime-observation-paper-eval-design/ の decisions.md（判断 55〜65）・blockers.md（B10〜B12）。Skill: verify-before-claiming・git-workflow。応答は日本語。
コミットは git add パス指定（-A 禁止）。main への merge はしない（W6 の後・研究者の判断）。
```

## §1c 確認すること（2026-09-30）

1. **`emit.py`（004 の追補・判断 59）**: 送出の基準を `trial_begin` の刻印（`t_mono_ns`）にした。selftest に「keys are scheduled from the recorded trial_begin timestamp」を足した。G-GEAR では既定の selftest が 200 回中 0 回赤（直す前は 2 回）。→ Mac で `004-acceptance.sh`・`emit.py --selftest --full`。macOS では `perf_counter_ns` / `perf_counter` はどちらも `mach_absolute_time()`。
2. **G-GEAR で merge した any の issue（006 / 020 / 023）と、それらの追補（006 のセルの `label`〔判断 62〕・FORMATS の reset 行の条件〔判断 56〕・`.gitattributes` の `experiment/` の `eol=lf`〔判断 63〕）**: Mac で一度も acceptance を回していない（B11 の教訓）。特に:
   - 006 `run_cell.py` の selftest は子プロセスの停止に POSIX の分岐（`start_new_session` と `os.killpg`・SIGTERM）を持ち、G-GEAR では「無視した子を kill する」ケースが info 行になって**走っていない**。→ Mac で `run_cell.py --selftest` の全ケースが ok か（info で飛ばしていないか）を確かめる。
   - 020 `pipeline.py` の selftest の `run.sh` の門（子プロセス）と、`--selftest --full`（全変種）。
   - 023 `summarize_e3.py --selftest`。
3. **E3 のプロセス名（判断 64・未確認の前提）**: Darwin の `p_comm` は 16 文字で切れ、`pgrep -x` は切れた名前と照合する見込みなので、`kit/e3/run_e3.sh` は macOS では既定の `E3_PROC` を先頭 16 文字（`ime-observation-`）にしている。→ 単体ロガーを release ビルドして短く起動し（例 `ime-observation-logger --out /tmp/e3-name-check.jsonl --duration-s 60`・入力監視の権限の確認が出たら断ってよい〔プロセス名だけを見る〕）、別の端末で `ps -c -o comm= -p <pid>` と `pgrep -x ime-observation-` と `pgrep -x ime-observation-logger` の結果を記録する。★ 前提が外れていたら（22 文字のまま一致する等）、`run_e3.sh` の既定を直す必要があるので研究者に報告する（直さない）。終わったら `/tmp/e3-name-check.jsonl` を消す。

## 以下 §1〜§3 は前回（2026-09-29 の昼）の手順。完了済み・参照用

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
