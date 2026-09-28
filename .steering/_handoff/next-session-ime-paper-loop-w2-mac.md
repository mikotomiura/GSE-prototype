# 次セッション（Mac）— IME 論文: W2 の Mac 分（issue 004 / 007）をループで実行する

> 作成: 2026-09-28（G-GEAR で W1 を merge し、W2 の G-GEAR 分を回し始めた時点）。
> ⚠️ **このメモを一次資料にしない。** 一次は `.steering/20260927-ime-observation-paper-eval-design/_issue-plan.md`（§2 波・§4 機械の割り当て・§7 config の注意）と `issues/004.md` / `issues/007.md`、詰まりは `blockers.md` B1〜B4、判断は `decisions.md` 判断 23〜26。状態は着手時に測り直す。

## §0 打ち込む用（Mac で・`/clear` の直後に）

```
.steering/_handoff/next-session-ime-paper-loop-w2-mac.md を読んで、IME 論文の評価一式の W2 の Mac 分（issue 004 / 007）をモード C で実行してください。
一次資料: .steering/20260927-ime-observation-paper-eval-design/_issue-plan.md（§4 機械の割り当て・§7 config の注意）・issues/004.md・issues/007.md・blockers.md。
⚠️ 実行の前に docs/loop-engineering.md を Read する。base は feature/ime-eval-kit（origin から pull してから回す）。
⚠️ _loop-config.json の events_path を Mac のパスへ書き換えてから回し、その変更はコミットしない。
緑なら merge ゲート（clean な checkout で 004 / 007 の acceptance・code-reviewer ∥ security-checker）→ base へ merge → push。
Skill: subagent-delegation・verify-before-claiming・git-workflow。応答は日本語。研究者の判断が要ることは AskUserQuestion で聞く。
コミットは git add パス指定（-A 禁止）。main への merge は W6 まで終わってから（研究者の判断）。
```

## §1 状態（2026-09-28・G-GEAR）

- ★ base `feature/ime-eval-kit` に W1（001）が merge 済み（`32b3fdc2`）。レビューを受けて契約を変えた（判断 23〜26）: `capabilities` は `{key, ime_shadow}` の列挙・`gt` / `obs` の行のバックスラッシュを拒否・`plan/1` / `oracle/1` / `corpus/1` の型を `FORMATS.md` に追加（判断 25）・`papers/.gitignore`。
- ★ **004 / 007 が従う契約は `papers/ime-observation/kit/formats/FORMATS.md` の最新版**。とくに 004 は「`oracle/1` の型」節（全行が 2 つの時刻を持つ・`trial_begin` は `gap_before_ms` の待ちの**後**・`marker` は押下ごとに 1 行・`reset` は `block_begin` の前）、007 は「エスケープを使わない」（⚠️ Swift の `JSONEncoder` は既定で `/` をエスケープする → `.withoutEscapingSlashes`）と「BOM を付けない」。
- G-GEAR では W2 の 7 本（002 003 010 016 → 008 011 015）を回している最中。Mac の 004 / 007 とは Allowed Files が交差しない（`_issue-plan.md` §3）。
- ★ **追記（同日・G-GEAR）**: 002 003 008 010 016 は base に merge 済み。判断 29 で `plan/1` のヘッダに `recipes_sha256` / `corpus_sha256` が増え、「試行は直前のブロック行を指す」になった（004 の実行器は計画を読むので、この形を受け入れること）。判断 34 で **004 / 007 は `verify_level: parse`** になった（watchdog は起動しない。合否はメインの clean な checkout の acceptance とレビューで決める）。
- ★ W2 の実測: 1 本あたり約 600 万トークン・$2.3〜2.7（1 attempt）。レビューで毎回 MEDIUM 以上が出て、直しにもう 1 回ずつ手がかかった。

## §2 手順

1. `git fetch` → `git switch feature/ime-eval-kit`（無ければ `git switch -c feature/ime-eval-kit origin/feature/ime-eval-kit`）→ `git pull --ff-only`。
2. `_loop-config.json` の `events_path` を `/Users/johnd/GSE-prototype/.steering/20260927-ime-observation-paper-eval-design/_loop-events.jsonl` に書き換える（⚠️ コミットしない。`git diff` に残ったら最後に戻す）。
3. `bash scripts/loop-run.sh .steering/20260927-ime-observation-paper-eval-design --issues 004,007`
   - ⚠️ main checkout に未コミット・未追跡の変更があると spawn が止まる（B1）。★ 他トラックの未追跡物なら触らずに `LOOP_FORCE=1` を付ける（dirty 検査だけを外す）。
4. merge ゲート（issue ごと）:
   - ⚠️ `issue_done` は verify（`kit/check.sh` 3 本）と acceptance の緑で出る（`parse`・watchdog なし）。★ 最終の合否はメインの clean な checkout の acceptance。
   - worktree の `git status` が空・`git log feature/ime-eval-kit..loop/<id>-issue` にコミットがあることを見る。
   - `loop/<id>-issue` を detached で clean な worktree に出し、そこを cwd にして main checkout 側の `issues/<id>-acceptance.sh` を回す（★ 終了コードはパイプの後ろで取らない）。変異を 1 本入れて赤になることも見る。
   - `code-reviewer` と `security-checker` を 1 メッセージで並列に（範囲 = `feature/ime-eval-kit..loop/<id>-issue`・read-only・締切 12 分・実行してよいコマンドを名指し）。
   - 契約を変える指摘は研究者に AskUserQuestion で聞く。仕様の範囲内の直しはメインが issue ブランチに足す。
5. `git merge --no-ff loop/<id>-issue` → `git push origin feature/ime-eval-kit`。⚠️ G-GEAR 側が先に push していて拒否されたら `git pull --no-rebase` で取り込んでから push（force しない）。
6. `bash scripts/loop-spawn.sh --cleanup <id>`。`tasklist.md` の W2 の行を更新してコミット・push。

## §3 気をつけること

- ★★★ **2026-09-29 追記（整理の後）**: base の `papers/ime-observation/` は学術的な英語になった（issue 028・`FORMATS.md` も英語。規則の意味は同じ）。各 acceptance の最後に `style_ok`（`_style_check.py`）があり、**その issue が変えたファイルに GSE・`src-tauri`・`.steering`・★ ⚠・内部の番号（decision / issue / judgment の番号・M0〜M13）・写した元との関係の語（reference implementation / upstream / verbatim copy）・地の文の日本語があると赤**になる。写した元との照合と manifest の書き直しは `kit/logger/check_manifest_upstream.internal.py`（`--against-upstream` / `--update`）、公開用の `check_manifest.py` は `--self` だけ。012 はこれを使う。
- ★★★ **公開物の書き方（判断 36・2026-09-28）**: `papers/ime-observation/` に書くコメント・docstring・README・CLI のヘルプは**学術的な英語**、GSE への言及（名前・パス・用語・「GSE と同じ」）と ★ ⚠️ などの記号は書かない。出どころは manifest の `gse_*` の欄と `*.internal.md` だけ。規則の全文は `papers/README.md`。レビューでもこれを見る。

- ⚠️ **worker に合成キーを送らせない**。004 の実バックエンドは `--i-understand-this-sends-keys` が無ければ送らない（AC）。acceptance も送らない。
- ⚠️ `check.sh` は G-GEAR（Windows）でも回る → `backend_macos.py` などに selftest の目印を付けるなら、macOS 以外では「対象外」で exit 0（004 の Scope）。
- ⚠️ `papers/` の文書に `.steering/` のパス・被験者 ID・`gse-dataset`・絶対パスを書かない。GSE 本体（`src-tauri/` ほか）を変えない。
- ⚠️ 文書にユニコードエスケープの例（バックスラッシュ u と 16 進 4 桁）を書かない —— ツールの入力で化ける（memory `feedback-backslash-via-bash-heredoc`）。

## §4 やらないこと

- 人の打鍵データを使う／Phase1 / G1 / O1 のデータを混ぜる
- プロトコル凍結（M3）の前に ImeShadow と正解を突き合わせる
- 新しい公開 repo を作る・push する（M12・研究者の判断）
- main へ merge する（W6 の後）
