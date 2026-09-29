# 次セッション（G-GEAR）— IME 論文: Mac の 004 が base に入った後の 005 / 006 → 020 / 023 → 024

> 作成: 2026-09-29（W4 を終えたセッションの最後に・研究者の指示）。前の G-GEAR 用 handoff（`next-session-ime-paper-ggear-w4.md`）の後継。前のものは読まなくてよい。
> ⚠️ **このメモを一次資料にしない。** 一次は `.steering/20260927-ime-observation-paper-eval-design/` の `_issue-plan.md`（§2 波・§4 機械の割り当て・§5 マイルストーン）・`issues/NNN.md`・`decisions.md`（判断 1〜46）・`blockers.md`（B1〜B9）・`tasklist.md`。状態は着手時に測り直す。
> ⚠️ Mac 側（004 / 007 / 012）は別の handoff: `.steering/_handoff/next-session-ime-paper-mac.md`。★ 両方の機械が同じ base に push するので、push の前に `git pull --no-rebase` で取り込む（force しない）。

## §0 打ち込む用（G-GEAR で・`/clear` の直後に）

```
.steering/_handoff/next-session-ime-paper-ggear-w5.md を読んで、IME 論文の評価一式の続きを G-GEAR で進めてください。まず Mac の 004 が base（origin/feature/ime-eval-kit）に入っているかを測り、入っていなければ研究者に確認して止まる。入っていれば 005 / 006 をループで回して merge ゲートを通し、続けて 020 / 023、最後に 024 の段取りに進む前に研究者に確認する。
一次資料: .steering/20260927-ime-observation-paper-eval-design/ の _issue-plan.md・issues/005.md 006.md 020.md 023.md 024.md・decisions.md（判断 34〜46）・blockers.md。
⚠️ 実行の前に docs/loop-engineering.md を Read する。base は feature/ime-eval-kit（origin から pull してから回す）。
Skill: subagent-delegation・verify-before-claiming・git-workflow。応答は日本語。研究者の判断が要ることは AskUserQuestion で聞く。
コミットは git add パス指定（-A 禁止）。main への merge は W6 まで終わってから（研究者の判断）。
```

## §1a 追記（2026-09-29・Mac の W2 / W3 を取り込んだ後）

- ★ **Mac の 004 / 007 / 012 は base に入った**（Mac が merge・G-GEAR で取り込んで確認）。base = **`3e078338`**（push 済み）。
- G-GEAR で取り込んだとき、全 acceptance が `kit/check.sh` の 1 件で赤だった（004 の `emit.py` の selftest・B11）→ 判断 52 / 53 で `emit.py` を直した（oracle の時刻を高分解能の時計に・遅れの上限は `--selftest --full` へ）。直した後の base の clean な checkout で、G-GEAR で回る全 acceptance 17 本が失敗 0 件（macOS 専用の 004 / 007 / 012 は exit 2 ＝対象外）・ループの verify 3 本（`check.sh`・`check.sh --compile`・`check-shell-portability.sh`）が緑・`_style_check.py` 違反 0 件。
- ★ 判断 54: 005 / 006 の `## Dependencies` から 004 を外した（004 の `issue_done` は Mac の events にだけある）。→ **§2 の手順 1 の「004 の merge」は満たされている。手順 2（`--issues 005,006`）から始めてよい**。
- ★ 推奨の順番（2026-09-29 のセッションでメインが勧めた・研究者は未確定）: **Mac で `emit.py` の確認（`004-acceptance.sh` の回し直し）を先に済ませてから 005 / 006 を回す**。着手時に `git pull` して `tasklist.md` の「⚠️ Mac: `004-acceptance.sh` を回し直す」が済んでいるかを見る。済んでいなければ研究者に確認する。Mac で赤だったなら、005 / 006 の前にメインが `emit.py` を直す（`emit.py` は 005 / 006 の Allowed Files の外なので worker は直せない）。
- ⚠️ 同じ機械で別プロジェクト（`C:\ERRE-Sand_Box`）の重い計算が走っていると CPU を奪う（2026-09-29 に 82%）。既定の selftest は負荷に左右されないようにしたが、ループや acceptance の所要時間は延びる。

## §1 状態（2026-09-29 の終わり）

- base `feature/ime-eval-kit` = **`ff2a392c`**（push 済み）。merge 済み: 001 002 003 008 009 010 011 013 **014 018 019** 015 016 017 021 022 ＋ 整理（issue 028）。merge 後の base の clean な checkout で **全 acceptance 17 本が失敗 0 件**・`_style_check.py` 違反 0 件。
- ★ **W4 は完了**（014 / 018 / 019・判断 44〜46）。止めていた 014 の worktree は片付けてから回し直し、3 本とも attempt 1 で `issue_done`（1 run・13.0M トークン・$5.53）。
- 残りの issue と依存（`## Dependencies` の一次）:

| id | 題 | runs_on | 依存 | 動ける条件 |
|---|---|---|---|---|
| 004 | 実行器の核と dry-run・macOS | macos | 001 | **Mac が回す**（最優先） |
| 007 / 012 | 参照入力欄 macOS / 単体ロガーの macOS ドライバ | macos | 001 / 011 | Mac が回す |
| 005 | 実行器の Windows（SendInput） | windows | 004 | ★ 004 が base に入った後（G-GEAR） |
| 006 | 1 セルの段取り | any | 003, 004 | ★ 004 が base に入った後（G-GEAR が既定） |
| 020 | 実験一式と 1 コマンドの再現（W5） | any | 006, 018, 019 | 006 が base に入った後 |
| 023 | E3 の器 | any | 006 | 006 が base に入った後 |
| 024 | 公開 repo への書き出し（W6） | any | 020 | 020 が base に入った後 |
| 025 / 026 / 027 | 任意（縮退順 ①④③） | — | — | `## Status: blocked`（既定で外れる） |

- Allowed Files は 005 / 006 / 020 / 023 のあいだで交差しない（`_issue-plan.md` §3）→ 同じ波の issue は 1 run にまとめてよい。
- 判断 44〜46（2026-09-29）の要点:
  - 44: 単体ロガーの候補窓の判定は**クラス名だけ**（UIA でフォーカス要素の名前を読まない）。写した元との違いは `kit/logger/PROVENANCE.internal.md` に記録。⚠️ **M5 で確かめる**: IMM 経路の端末で、名前でしか裏が取れない候補窓があると stale の判断が早まりうる。
  - 45: `dwell_ms == 0` の観測行（時計の巻き戻り）は l1 / l2 が件数を出す。⚠️ **照合での扱い（検出 / 偽検出 / 評価から外す）は M3 の凍結で決める（未決）**。l2 は平均変換時間と時間割合から外し、変換の数と放棄には今は数える。
  - 46: L2 は未実行・除外の試行を含むテキストを捨てて件数を出す。
- 判断 34: 未実行の issue はすべて `verify_level: parse`。合否は**メインが clean な checkout で回す acceptance** とレビューで決める。
- 公開物の書き方（判断 36 / 42 / 43）: `papers/ime-observation/` は学術的な英語・GSE への言及なし・内部の番号（decision / issue / judgment・M0〜M13）なし・写した元との関係の語（reference implementation / upstream / verbatim copy）なし・★ ⚠ なし。各 acceptance の最後の `style_ok` が見る。規則の全文は `papers/README.md`。

## §2 手順

1. **状態を測る**: `git fetch` → `git log --oneline feature/ime-eval-kit..origin/feature/ime-eval-kit`・`tail -5 .steering/20260927-ime-observation-paper-eval-design/_loop-events.jsonl`・`git worktree list`・`git branch --list 'loop/*'`。
   - **004 の merge が origin に無ければ**: W5 / W6 は始められない → 研究者に確認して止まる（★ Mac を待たずにできるのはループ外の M0〔コーパスの確定・作品の選定と取得は研究者の承認〕くらい）。
   - あれば `git pull --ff-only`（ローカルに未 push のコミットがあれば `--no-rebase`）。
2. **W3 の残り（005 / 006）**: `LOOP_FORCE=1 bash scripts/loop-run.sh .steering/20260927-ime-observation-paper-eval-design --issues 005,006`（バックグラウンド・events を Monitor で見る）。⚠️ main checkout に別トラックの未追跡ディレクトリ（`.steering/20260921-media-expression-theory-audit/` ほか）があるので `LOOP_FORCE=1` が要る（B1）。★ それらには触らない。
3. **merge ゲート（issue ごと）**:
   - worktree の `git status --porcelain --untracked-files=all` が空・`git log feature/ime-eval-kit..loop/<id>-issue` にコミットがある。
   - clean な checkout を**短いパス**に出す（`git worktree add --detach /c/wt/clean-<id> loop/<id>-issue`。⚠️ scratchpad の長いパスだと Rust の `target/` が消せない・B7）。そこを cwd にして `bash .steering/20260927-ime-observation-paper-eval-design/issues/<id>-acceptance.sh > /c/wt/acc-<id>.out 2>&1; echo $?`（⚠️ 終了コードはパイプの後ろで取らない）。
   - レビュー: `code-reviewer` と `security-checker` を並列に（2 本の issue をまとめて 1 本の security-checker にしてよい）。★ 範囲（三点リーダ `feature/ime-eval-kit...loop/<id>-issue`、別の作業がブランチにコミットを足す間は**コミットのハッシュか clean な checkout のパス**で指す）・read-only・clone しない・`kit/check.sh` と acceptance を回さない（`e2/closed_set.py` の selftest が約 22 秒）・締切 15 分・「公開物の書き方は style_ok が見ている」・仕様（issue の md と design.md の節の行番号）と入力の部品のパスを名指す。005 は `hook-constraints` ではなく実行器の境界（004 の `SUPPORTED_KEYS` / `Backend(opts)` / `open` / `send` / `close`・`--backend-opt`）を見させる。⚠️ 合成キーを送る経路（`--i-understand-this-sends-keys`）が既定で閉じているかを必ず見させる。
   - 指摘は**一次で裏取り**してから扱う。契約・設計に関わるもの（issue の定義を変える・別 issue の merge 済みファイルにまたがる）は AskUserQuestion で研究者に聞く。仕様の範囲の直しは作業用エージェント（`general-purpose`・`model: sonnet`）に worktree で直させる（★ 指示に「main checkout を触らない・`git checkout --` で戻さない・入れ子にしない・判断 36 の書き方・Allowed Files・acceptance が名指すケース名を変えない・締切」を必ず書く・B6）。
   - ★ **HIGH の直しは、メインが写しへの変異で効くことを確かめる**（`T=$(mktemp -d); cp -r <clean checkout>/papers/.../analysis "$T/"` で写し、その中だけを書き換えて selftest が赤になることを見る。clean な checkout を汚さない）。2026-09-29 は 019 の組み立てを壊す変異で、直す前の selftest が 7 ケースとも**緑のまま**だった。
   - 戻ってきたら clean な checkout を `git checkout --detach loop/<id>-issue` で進めて acceptance を回し直す。
   - `git merge --no-ff loop/<id>-issue`（本文に merge ゲートの結果と反映した指摘・`Refs:`・`Co-Authored-By`）。
4. **W5 / W4b（020 / 023）**: 006 を merge して push した**後**に、別プロセスで `--issues 020,023`（★ 依存先の成果物は後続の worktree に入らない → 006 を base に入れてから回す・`docs/loop-engineering.md` 2026-09-27）。merge ゲートは 3. と同じ。⚠️ 020 の `run.sh` は凍結（M3）の前は本番を止める作りで、実データは使わない。
5. **W6（024）の前に研究者に確認**（公開 repo への書き出しの検査・判断 36 / 43 の書き出し規則。⚠️ 新しい公開 repo は作らない・M12 は研究者）。
6. 波ごとに: merge 済みの**全 acceptance** を clean な checkout で回す（⚠️ Windows 専用〔005 008 009 013 014〕も G-GEAR では回る。macOS 専用〔004 007 012〕は G-GEAR では exit 2 ＝「この機械で回すな」で失敗ではない）＋ `python .steering/.../issues/_style_check.py papers/ime-observation`（違反 0 件）→ `git pull --no-rebase` → push → `bash scripts/loop-spawn.sh --cleanup <id>` → clean な checkout を `git worktree remove --force`（失敗したら `rm -rf` → `git worktree prune`・B7）。
7. `tasklist.md` と `decisions.md` を更新してコミット・push。

## §3 気をつけること

- ⚠️ 作業用エージェントに追加の直しを渡すとき、**走っている最中に `SendMessage` で送ったものは届かないまま終わった**（2026-09-29・018）。報告が返って止まった後に送り直したら再開して反映した。→ 追加は報告の後に送り、戻ってきたコミットに入っているかを `git log` と grep で確かめる。
- ⚠️ 作業用エージェントが報告の後もバックグラウンドの処理を残すことがある（B9）。merge の直前に worktree の `git status` と HEAD を確かめる。
- ⚠️ `closed_set.py` の selftest が約 22 秒（入口の警告の目安 30 秒・B8）。2026-09-29 の全 acceptance では警告は出なかった。
- ⚠️ `loop-run.sh` の終わりに `spawn_err: unbound variable` が出るのは既知の雑音（B2・判定に影響しない）。
- ⚠️ 文書にユニコードエスケープの例（バックスラッシュ u と 16 進 4 桁）を書かない（ツールの入力で化ける）。CR の確認は `tr -cd '\r' < f | wc -c`。
- ⚠️ **worker に合成キーを送らせない**（005 の実バックエンドも既定で送らない）。実際に送るのはパイロット（M1 / M5）で、人とメインが行う。
- ⚠️ GSE 本体（`src-tauri/` ほか）を変えない。人の打鍵データを使わない。プロトコル凍結（M3 / M6）の前に ImeShadow と正解を突き合わせない。新しい公開 repo を作らない（M12・研究者）。main へ merge しない（W6 の後）。
