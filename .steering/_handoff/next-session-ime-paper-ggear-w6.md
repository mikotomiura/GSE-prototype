# 次セッション（G-GEAR）— IME 論文: W6（024 公開 repo への書き出し）

> ✅ **2026-09-30: 完了**（024 を `c6305340` で base へ merge・判断 67〜71）。次は `next-session-ime-paper-after-w6.md`（Mac の確認と main への merge の判断）。

> 作成: 2026-09-30（W3 の残り 005 / 006 と W5 の 020 / 023 を merge したセッションの最後に・研究者の指示「コンテキスト的に次セッションで回す」）。前の G-GEAR 用 handoff（`next-session-ime-paper-ggear-w5.md`）の後継。前のものは読まなくてよい。
> ⚠️ **このメモを一次資料にしない。** 一次は `.steering/20260927-ime-observation-paper-eval-design/` の `_issue-plan.md`（§2 波・§5 マイルストーン）・`issues/024.md`・`decisions.md`（判断 1〜65）・`blockers.md`（B1〜B12）・`tasklist.md`。状態は着手時に測り直す。
> ★ **2026-09-30 03:4x 更新**: Mac の確認（`next-session-ime-paper-mac.md` の §0）は済んだ（Mac の push `e1744b98`〜`2c3a2781` を G-GEAR で取り込み・§1b）。**Mac 側に残りの作業は無い**。W6 は G-GEAR で回す。
> ★ 両方の機械が同じ base に push するので、push の前に `git fetch` で相手の push を読み、`git pull --no-rebase` で取り込む（force しない）。

## §0 打ち込む用（G-GEAR で・`/clear` の直後に）

```
.steering/_handoff/next-session-ime-paper-ggear-w6.md を読んで、IME 論文の評価一式の W6（issue 024 公開 repo への書き出し）を G-GEAR で進めてください。
まず §1 の状態を測り直し（base feature/ime-eval-kit を origin から pull して 2c3a2781 以降であること・Mac から新しい push があれば先に読む）、§2 の未決（024 の秘匿の検査と、merge 済みの公開物の架空のパスの衝突）を AskUserQuestion で研究者に聞いてから、024 の issue を直してループを回し、merge ゲートを通す。
一次資料: .steering/20260927-ime-observation-paper-eval-design/ の _issue-plan.md・issues/024.md・decisions.md（判断 36 / 42 / 43 / 55〜66）・blockers.md（B1〜B12）。
⚠️ 実行の前に docs/loop-engineering.md を Read する。Skill: subagent-delegation・verify-before-claiming・git-workflow。応答は日本語。研究者の判断が要ることは AskUserQuestion で聞く。
コミットは git add パス指定（-A 禁止）。main への merge はしない（W6 の後・研究者の判断）。新しい公開 repo を作らない・push しない・DOI を取らない（M12 は研究者）。
```

## §1 状態（2026-09-30 の終わり）

- base `feature/ime-eval-kit`: 005（`9098e1ee`）・006（`5668dccd`）・023（`038645a8`）・020（`82a74e22`）を merge 済み。追補: FORMATS の reset 行の条件（001・`08541088`）・`emit.py` の送出の基準（004・判断 59・`96a19df6`）・セルの `label`（006・判断 62・`1c4b025e`）・`.gitattributes` の `experiment/` の `eol=lf`（判断 63）。
  - ✅ **merge 後の base（`82a74e22`）の clean な checkout で全 acceptance 24 本を回した**（2026-09-30）: G-GEAR で回る 21 本がすべて失敗 0 件（macOS 専用の 004 / 007 / 012 は exit 2 ＝対象外）・`_style_check.py papers/ime-observation` 違反 0 件 → push 済み。
- ★ **§1b Mac の確認（2026-09-30・Mac が実施して push）**:
  - Mac（macOS 27.0・Python 3.14.4）で base `44241f49` の clean な worktree から、Mac で回せる merge 済みの全 acceptance 19 本（001 002 003 004 006 007 010 011 012 015〜023 028）が失敗 0 件。`emit.py --selftest --full`（判断 59 の直しを含む・49 件 ok）・`run_cell.py --selftest`（G-GEAR では飛んでいた POSIX 専用の「a child that ignores the termination request is killed」も Mac で ok）・`pipeline.py --selftest --full`（Mac では 4 秒）・`summarize_e3.py --selftest` も緑。→ ★ **005 / 006 / 020 / 023 と判断 59 の `emit.py` は両 OS で緑**。
  - ⚠️ **判断 64 の前提（macOS のプロセス名は 16 文字で切れる）が外れた** → **判断 66**: Mac の実測で `pgrep -x` は 22 文字の完全な名前 `ime-observation-logger` で一致し、`ime-observation-`（16 文字）では一致しない（16 文字に切れるのは `top` の COMMAND 列だけ）。`kit/e3/run_e3.sh` の既定を両 OS とも完全な名前にし、切り詰めを外した（`e1744b98`）。Mac で `/cross-review` を回して指摘を反映（`4b63384b`）・Codex の予算を記帳（`2c3a2781`）。
  - G-GEAR で取り込んだ後（`2c3a2781`）、clean な checkout で `023-acceptance.sh` が失敗 0 件（Windows・2026-09-30）。`run_e3.sh` の変更は macOS の分岐を外しただけで、Windows の既定は変わらない。
- 残りの issue: **024**（W6・依存 020 は merge 済み・`issue_done` は G-GEAR の events にある）。任意の 025 / 026 / 027 は `## Status: blocked`。
- ★ ループ外の段取り（研究者と人の仕事・`_issue-plan.md` §5）: M0（コーパス）→ M1（macOS の較正パイロット）→ M2 → M3（事前登録の凍結）… 。W6 の後に main への merge を研究者が判断する。
- 公開物の書き方（判断 36 / 42 / 43）: `papers/ime-observation/` は学術的な英語・GSE への言及なし・内部の番号（decision / issue / judgment・M0〜M13）なし・写した元との関係の語なし・★ ⚠ なし。各 acceptance の最後の `style_ok` が見る。出どころは `*.internal.md` と manifest の `upstream_*` の欄だけ（024 が落とす）。
- このセッションの裁定の要点（判断 55〜65。詳細は decisions.md）:
  - 55 実キーの前面の確認は runner（`run_cell.py`）がバックエンドの `focus_back` で・Windows のバックエンドは押下ごとに照合 ／ 56 IME のリセットは送出のフラグがあるときだけ ／ 57 run の manifest のホームと repo のルートを `~` / `<repo>` に置換＋寄託前の検査（020 の `--check-deposit` / `--pack`）／ 58 子の停止の記録を実態に ／ 59 `emit.py` の送出の基準を `trial_begin` の刻印に ／ 60 / 61 E3 の写しは実行行を保ち注釈だけ英訳・出典は `PROVENANCE.internal.md` ／ 62 セルの `label`（解析で必須）／ 63 凍結の門（印の書式・`sha256` = config.json / SEED / 正解の規則の SHA-256 の並びの SHA-256・実データは `--prereg` 必須）／ 64 E3 は 1 条件 8 時間 ／ 65 020 の selftest を既定 17 秒と `--full` に分けた ／ ★ 66（Mac）E3 のプロセス名は macOS でも完全な名前で照合する（64 の前提の訂正）。
  - ⚠️ 未決として残したもの: 照合器の `clock_offsets_ms`（run ごとの時計の差）の出どころ（M1 / M3 で決める・今は 0）／`dwell_ms == 0` の扱い（判断 45・M3）。

## §2 未決 —— 024 を回す前に研究者に聞く（2026-09-30 に聞こうとして、セッションを区切ったため未回答）

- 事象: 024 の秘匿の検査は「書き出す全文で `C:\Users\` / `/Users/` の絶対パスを拒む」（`issues/024.md` Background 18 行）。ところが merge 済みの公開物に、次が**正当な理由で**ある（2026-09-30 に grep で確認）:
  - 寄託の検査・置換の selftest の**架空のパス**: `kit/analysis/pipeline.py:1460-1474, 1489, 1572`（`C:/Users/alice/work`・`/c/Users/YAMADA~1/x`・`/Users/carol/x`・`/home/dave/x` など）、`kit/run/run_cell.py:1151-1153`（`/home/alice`）
  - 規則の**説明文**: `experiment/data.md:33`・`kit/analysis/pipeline.py:79, 690`（`/Users/`・`/home/`・`/c/Users/name`）
  - （`kit/logger/src/key_category.rs:31` の `[P121]` は文献番号で、逐語コピーの注釈なので書き出しで落ちる → 問題なし）
- 024 の Stop 条件は「検査を緩めず、当たったファイルを報告する」なので、このまま回すと worker が止まる（023 と同じ型）。
- 聞く選択肢（メインの推奨は A）:
  - **A**: 024 の検査は、書き出す機械の**実在の値**（ホーム・ログイン名・repo のルート）と、ユーザー名を伴う `C:\Users\<名>` / `/Users/<名>` / `/home/<名>` を拒む。ただし selftest の**架空の名前の明示の許可リスト**（alice / bob / carol / dave / erin / harry / YAMADA~1 など・`pipeline.py` と `run_cell.py` を grep して確定する）と、名前を伴わない説明の語（`/Users/` だけ）は通す。→ メインが `issues/024.md` と `024-acceptance.sh` を直してから回す。
  - B: 024 の検査は厳しいまま、006 / 020 の selftest の架空のパスを実行時の連結で作り、説明文から `/Users/` を除く（merge 済みの 2 ファイルと `data.md` の追補）。
  - C: 024 の検査を 020 の `--check-deposit` と同じ規則（実在の値だけ）にする。
- あわせて確かめること（仕様の範囲・メインが issue に書き足す）: 024 は判断 43 より前に書いた部分がある（`--against-gse` の語など）→ 028 で直した acceptance と整合しているかを読む。`experiment/results/`・`runs/`・`*.zip`（020 の `--pack` の出力）・`sealed/` を書き出さないこと。`kit/e3/PROVENANCE.internal.md`・`kit/logger/PROVENANCE.internal.md`・`check_manifest_upstream.internal.py` を書き出さないこと（`*.internal.*`）。

## §3 手順

1. **状態を測る**: `git fetch` → `git log --oneline feature/ime-eval-kit..origin/feature/ime-eval-kit`（Mac の push を先に読む）→ `git pull --no-rebase`。`git worktree list`・`git branch --list 'loop/*'`（残っていたら §4 のとおり片付ける）。`tail -5 .steering/20260927-ime-observation-paper-eval-design/_loop-events.jsonl`。
2. **全 acceptance**: W5 の後の全 acceptance は両 OS で済んでいる（§1・§1b）。`2c3a2781` より後に `papers/` が変わっていれば（Mac の push など）、その分の acceptance を clean な checkout（短いパス・B7）で回し直す。
3. **§2 を研究者に聞く** → 答えに合わせて `issues/024.md` と `024-acceptance.sh` を直し（acceptance は旧い成果物・架空の成果物で陰性対照を確かめる）、判断 67 以降として `decisions.md` に記録（★ 判断 66 は Mac が使った） → コミット・push。
4. **ループ**: `LOOP_FORCE=1 bash scripts/loop-run.sh .steering/20260927-ime-observation-paper-eval-design --issues 024`（バックグラウンド・events を Monitor で見る）。⚠️ main checkout に別トラックの未追跡ディレクトリ（`.steering/20260921-media-expression-theory-audit/`）があるので `LOOP_FORCE=1` が要る（B1）。★ それには触らない。
5. **merge ゲート**（これまでと同じ）:
   - worktree の `git status --porcelain --untracked-files=all` が空・コミットがある。
   - clean な checkout を短いパスに（`git worktree add --detach /c/wt/clean-024 loop/024-issue`）→ `bash .steering/.../issues/024-acceptance.sh > /c/wt/acc-024.out 2>&1; echo $?`。
   - レビュー: `code-reviewer` と `security-checker` を並列に。★ 範囲はコミットのハッシュか clean な checkout のパスで指す・read-only・clone しない・`kit/check.sh` と acceptance を回さない（`e2/closed_set.py` の selftest が約 22 秒・`pipeline.py` の selftest が約 17 秒）・締切 15 分・「公開物の書き方は style_ok が見ている」・仕様（issue の md の行番号）と入力の部品のパスを名指す。024 は ★ **書き出した後の中身に内部の情報（GSE・`.steering`・被験者 ID・メール・ホームのパス・`upstream_*` の欄・`*.internal.*`）が残らないこと**と、逐語コピーの注釈の除去が文字列リテラルを壊さないこと（書き出した側で `cargo test` と `kit/check.sh` が通る）を必ず見させる。
   - 指摘は一次で裏取り → 契約・設計に関わるものは AskUserQuestion → 仕様の範囲は作業用エージェント（`general-purpose`・`model: sonnet`）に worktree で直させる（★ 指示に「main checkout を触らない・`git checkout --` で戻さない・入れ子にしない・判断 36 の書き方・Allowed Files・acceptance が名指すケース名を変えない・締切」を書く・B6）。
   - ★ HIGH の直しは、写しへの変異で効くことをメインが確かめる（clean な checkout を汚さない）。
   - `git merge --no-ff loop/024-issue`（本文に merge ゲートの結果・`Refs:`・`Co-Authored-By`）。⚠️ `git merge -F -` は使えない（標準入力を読まない）→ メッセージはファイルに書いて `-F <file>`。
6. merge 後に全 acceptance（24 本＋024）→ `git pull --no-rebase` → push → 片付け（§4）。
7. `tasklist.md` と `decisions.md` を更新してコミット・push。W6 が終わったら、main への merge を研究者に確認する（⚠️ 勝手に merge しない）。

## §4 このセッションの後始末の状態

- ★ このセッションの最後に行ったこと（着手時に `git worktree list` / `git branch --list 'loop/*'` / `git status` で確かめ直す）: tasklist・decisions（判断 65）と handoff のコミット、全 acceptance が緑を確かめて push、`loop/005`・`006`・`020`・`023` の worktree と枝、検証用の `C:/wt/clean-*` の片付け。
- 止まった 023 の記録はローカルの枝 `archive/ime-023-attempt1-stop`（push していない）。
- 片付けの手順: `bash scripts/loop-spawn.sh --cleanup <id>`（未 merge のコミットを持つ枝は消さない → 内容を確かめてから `git branch -D`）。

## §5 気をつけること

- ⚠️ **Bash のバックグラウンド実行では `cd` が効かないことがあった**（2026-09-30: 200 回の繰り返しが全部「ファイルが無い」で空振りした）。バックグラウンドのコマンドは絶対パスで書く。
- ⚠️ ループの `loop-run.sh` の終わりの `spawn_err: unbound variable` は既知の雑音（B2）。
- ⚠️ 同じ機械で別プロジェクト（`C:\ERRE-Sand_Box`）の重い計算が走っていると CPU を奪う（2026-09-29〜30 に 74〜82%）。そのプロセスには触れない。
- ⚠️ `emit.py` の既定の selftest は判断 59 で決定的になった（200 回中 0 回赤）。⚠️ 別の selftest が間欠的に赤になったら、B12 のように**繰り返して捕まえてから**原因を読む（1 回の赤を「負荷のせい」で片付けない）。
- ⚠️ 文書にユニコードエスケープの例（バックスラッシュ u と 16 進 4 桁）を書かない。heredoc の中のバックスラッシュは化けうる（2026-09-30 に `printf '%s\n'` が改行に化けた）→ Edit で直す。CR の確認は `tr -cd '\r' < f | wc -c`。
- ⚠️ worker に合成キーを送らせない。GSE 本体（`src-tauri/` ほか）を変えない。人の打鍵データを使わない。凍結（M3 / M6）の前に ImeShadow と正解を突き合わせない。新しい公開 repo を作らない（M12・研究者）。main へ merge しない（W6 の後・研究者の判断）。
