# 引き継ぎ: 相対のタイミングの計器（案 D）を試作で測り、レビューを通して固定する（G-GEAR）

作成 2026-11-22（Windows・G-GEAR）。前の引き継ぎ `next-session-rhythm-stage-relative-timing-instrument.md` の §3 の 1〜3 が終わった続き。返答・記録・AskUserQuestion の引数は日本語で書く。記号（★・⚠️）は多用しない。AskUserQuestion には推奨と理由を添える。

## 0. 新しいセッションで最初に打ち込む文

```
C:\wt\rhythm-stage-relative-timing\.steering\_handoff\next-session-rhythm-stage-relative-timing-freeze.md を読んで、§1 の条件を確かめてから、§3 の順で進めて。
```

- 作業の場所: worktree `C:\wt\rhythm-stage-relative-timing`・ブランチ `docs/rhythm-stage-relative-timing`。`C:\GSE-prototype` の作業ツリーには触れない。
- タスクの記録: `.steering/20261122-rhythm-stage-relative-timing/`（design は下書きのまま・判断 1〜11）。`/start-task` をやり直さない。
- 計器: `experiments/20261122-rhythm-stage-relative-timing/`（コミット `644967c9`・push はまだ）。

## 1. 始める前に一次で確かめる

1. 重い処理が無い（`ps -W | grep -i python`）。CI の `gh run list --status in_progress` と `--status queued` が空。
2. 道具: `C:/wt/_target-portrait-eh1/release/gse-replay.exe`（SHA-256 `71d09dab…986`）と仮想環境 `C:/wt/portrait-eh1-round3/experiments/20261010-portrait-eh1-round3/.venv/Scripts/python`（3.11.9・numpy 2.4.6・scipy 1.17.1・scikit-learn 1.9.1・threadpoolctl 3.7.0）。
3. `git status` が clean（この引き継ぎのコミットの後）で、`git log` に `644967c9` がある。

## 2. 読むもの（この順）

1. `decisions.md` の判断 10 と 11（11 に、計器で足した細部・自己検査の割合・変異の結果がある）。
2. `design.md`（下書き・SSOT）。
3. 計器の `scripts/stage.py`（案 D は `d_*` の関数）・`checks.py`（`e13_target(..., base=)`・`pilot_parts`・`main_specs`・`main_run`）・`selftest.py`（`--mutants`）・`run.sh`（`--selftest | --mutants | --ceiling | --pilot | --smoke | --main`）。

## 3. やること（順に）

1. **研究者に先に聞く**（判断 11 の 2 点・推奨を添える）:
   - N1 で除く秒が s = 2 で約 8 割（1000 ms を超える休止が 2 倍で 2000 ms の上限を越える）。判断 10 の見直しの条件に当たりうる。`N_WIN`・`MAX_AGE_S` を変えるか、このまま「除いた割合を記録する」で進めるか。
   - N2 で `D-all` が変わる秒が 0.137 だけ。design §3.3 (d) の見込み（`D-all` は倍率に左右されうる）と §3.7 の N2 の文をどう書くか。
2. **使い捨ての試作で 1 段の時間を測る**: 本番と違う seed（例 `SEED` 以外の値・P 40）。`run.sh` は `SEED` を読むので、入れ物を scratchpad に写して `SEED` を変え、自己検査（`test_config` が SEED = 20261122 を要求する）を飛ばして `gen_sessions.py` → `capabilities_gate` → `replay_all.py` → `twins.py` → `ceiling.py` → `checks.py --pilot` → `--apply-pilot` → `checks.py`（本番の形・P 40）を直接呼ぶ。試作の値は design の判断に使わない（時間と動くかだけを見る）。本番と同じ seed の列（20261122・20261123・20261124）は開かない。見積もりを design §4 に書き直す。
3. **書き戻し**: `env.md`・`data.md` を写し元のまま直していない。このタスクの内容（段 g050 / f200・SEED 20261122・L300 だけ・基準 2 つ・`--mutants`・split と compare が無い）に直す。design §1.2・§3.7・§9 に判断 11 の細部（窓の上限の端・0 ms・N1 の偶数の ms・N2 の 600 ms・バイト一致の比べ方・下見の S の早い打ち切り・PC-corr を残した）を書き、§3.7 の「300 秒ちょうど前は入らない」を §1.2 の半開区間に合わせて直す。
4. code-reviewer と security-checker を並列に起動する（`subagent-delegation` Skill の契約: model の明示・範囲（`experiments/20261122-rhythm-stage-relative-timing/` と design）・禁止事項（編集しない・前の回の入れ物を読むだけ）・締切）。
5. `/cross-review` を 2 巡（1 巡目 = 自文書・他文書の矛盾、2 巡目 = 足した規則の境界条件）。パス限定（`run-codex-review.sh -- <paths>`）・出力は scratchpad。予算は worktree と origin/main の `.codex/budget.json` を先に見る。指摘の対応を decisions.md に書く。
6. 直した後に `bash run.sh --selftest`（`GSE_REPLAY` 付き）と `bash run.sh --mutants` を回し直す。
7. design の状態を「固定」にし、計器と design を同じコミットで固定する。下見 0 も本番も回していないことを design の冒頭に書く。push する（計測の run の最中は PR を出さない）。
8. 止めて研究者に報告する（下見 0 から先は研究者の許可の後）。

## 4. 守ること

- 合成の列だけを使う。NDJSON（合成も）・キーストロークの内容を外部の LLM（Codex を含む）に送らない。Codex は repo を読めないので、資料はプロンプトに貼り「シェル禁止」を明記する。
- 前の 6 回とまとめの入れ物・判定・notes・design を書き換えない（自己検査は写し元を読むだけ。写し元の dir で python を動かすときは `PYTHONDONTWRITEBYTECODE=1`）。`src-tauri/`・`src/`・EH3・Mac のブランチ・照合の論文の worktree に触れない。
- `.codex/budget.json` を `git checkout --` で戻さない。`git add -A`・`git add <dir>` を使わない。
- heredoc でクォートや複雑な置換を書かない（今回、bash の heredoc で 2 回壊れた）。Python の置換は Write で `.py` を作るか Edit を使う。書き戻しは `newline="\n"`。
- バックグラウンドの「completed」の通知を信じず、結果のファイルとログを一次で確かめる。
- 実験の根元に `work-selftest.log`・`work-mutants.log` が残っているなら、コミットしない（消してよい）。
