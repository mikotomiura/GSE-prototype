# 引き継ぎ: 相対のタイミングの写像（案 D）の計器を作り、固定まで進める（G-GEAR）

作成 2026-11-22（Windows・G-GEAR）。返答・記録・AskUserQuestion の引数は日本語で書く。記号（★・⚠️）は多用しない。AskUserQuestion には推奨と理由を添える。

## 0. 新しいセッションで最初に打ち込む文

```
C:\wt\rhythm-stage-relative-timing\.steering\_handoff\next-session-rhythm-stage-relative-timing-instrument.md を読んで、§1 の条件を確かめてから、§3 の順で計器を作って。
```

- 作業の場所: worktree `C:\wt\rhythm-stage-relative-timing`・ブランチ `docs/rhythm-stage-relative-timing`（`origin/docs/rhythm-stage-summary` の `1cf9fcb9` から切った。上流は外して、自分の名前のリモートのブランチへ push している）。`C:\GSE-prototype` の作業ツリー（別ブランチ・未コミットの変更あり）には触れない。
- タスクの記録: `.steering/20261122-rhythm-stage-relative-timing/`（requirement・design・decisions 判断 1〜10・tasklist・design-v1/v2・design-comparison）。
- タスクは立て済み（`/start-task`・grill・`/reimagine` まで）。`/start-task` をやり直さない。実装は Sonnet が既定（CLAUDE.md のモデル選択）。設計の変更が要る論点が出たら、研究者に聞く。

## 1. 始める前に一次で確かめる

1. 重い処理が無い: 照合の論文（`C:\GSE-wt-matching-prereg`）やほかの計算の python が走っていない。`Get-CimInstance Win32_Process` は自動モードで拒まれたことがあるので、`ps -W | grep -i python` で代えてよい（2026-11-22 に実施）。
2. CI: `gh run list --status in_progress` と `--status queued` が空（G-GEAR は self-hosted の Windows の runner を兼ねる）。
3. 道具が残っている: `C:/wt/_target-portrait-eh1/release/gse-replay.exe`（揺れの形の計器が SHA-256 を照合する）と、前の回の仮想環境（Python 3.11.9・numpy 2.4.6・scipy 1.17.1・scikit-learn 1.9.1・threadpoolctl 3.7.0。場所は `experiments/20261015-rhythm-stage-speed-shape-world/env.md`）。無ければ作り直す前に研究者に伝える。
4. `git -C C:\wt\rhythm-stage-relative-timing status` が clean で、`git log -1` が `c8eaa9b1` 以降。

## 2. 読むもの（この順）

1. `.steering/20261122-rhythm-stage-relative-timing/design.md`（ハイブリッド・これが SSOT）と `decisions.md` 判断 1〜10。`design-v1.md`・`design-v2.md` は経緯で、仕様の根拠に使わない。
2. 写し元の計器 `experiments/20261015-rhythm-stage-speed-shape-world/`（`scripts/stage.py`・`checks.py` の `e13_target`・`judge`・`pilot*`・`baseline.py`・`gen_sessions.py`・`run.sh`・`config.json`・`selftest.py`）と、その design `.steering/20261015-rhythm-stage-speed-shape-world/design.md`（参照する前の回の節を含む）。
3. まとめ `.steering/20261017-rhythm-stage-summary/summary.md`（6 回の結果と計器の限り）。

## 3. やること（順に）

1. `experiments/20261122-rhythm-stage-relative-timing/` を作り、写し元の `.gitignore`・`config.json`・`run.sh`・`requirements.txt`・`env.md`・`data.md`・`scripts/` を写す（`notes.md`・`results/` は写さない）。前の dir を import しない。写し元のファイルは書き換えない。
2. design のとおりに直す（主な箇所）:
   - `stage.py`: 案 D の 2 本 `D-run-hold-sec`・`D-all-hold-sec`（§1.2: 数の窓 40 個・300 秒の上限・`run` は窓の中央値の 3 倍未満・`a` = `log(p90/p10)/log 10`・`r` = 隣の比の対数の絶対値の中央値・据え置き 8 個・5 対・1 秒ごとの更新・hold）。案 D の PC-stall は量を作った直後に入れ、据え置きと hold を通す（§1.5）。候補の一覧を 6 本（案 D 2 ＋ 錨 4）にする。
   - `checks.py`: 判定を基準（`A`・`S`）を引数に取る形にし、L300 だけで両方を作る（§1.4）。PC-stall の λ を基準ごとに選ぶ（§1.5）。下見 0 で AUC(A) が天井の段を止める（§3.0）。記述 (d0)・(d1)・(d2)（滑らかさの量だけの R² を含む）と、量を落とす変種（§1.6）を出す。L60・L1800・PCr・切り分けの読み・並べる表は外す。
   - `config.json`・`run.sh`: 段 `g050`（`--world graded --t 0.5`）・`f200`（`--world factor --c 2`）・`SEED` 20261122・ラベル L300。
   - `selftest.py`: design §3.7 の検査（N1・N2・作り物の列の不変・数の窓の境目・基準の取り違え・写し元との A_speed の判定のバイト一致・止める条件）と変異の一覧。変異は入れて落ちることを確かめ、結果を decisions.md に書く。
3. 写し元とのバイト一致の検査（生成器・錨・PC1・PC-stall・PC0）が通ることを確かめる。
4. 使い捨ての試作で 1 段の時間を測る: 本番と**違う seed**・P 40。本番と同じ seed の列は、固定の前に開かない（揺れの形の判断 9 の開示の型を避ける）。試作の結果の値は design の判断に使わない（時間と動くかだけを見る）。見積もりを design §4 に書き直す。
5. code-reviewer と security-checker を並列に起動する（`subagent-delegation` Skill の契約: model の明示・範囲と禁止事項・締切）。
6. `/cross-review` を 2 巡（1 巡目 = 自文書・他文書の矛盾、2 巡目 = 足した規則の境界条件）。パス限定で回す（`run-codex-review.sh -- <paths>`）。出力は scratchpad。指摘の対応を decisions.md に記録する。
7. design の状態を「固定」にし、計器と design を同じコミットで固定する。固定の時点で、下見 0 も本番も回していないことを design の冒頭に書く。
8. ここまでで止めて研究者に報告する（下見 0 から先は、研究者が回してよいと言ってから）。

## 4. 守ること（CLAUDE.md とこのタスクの制約）

- 合成の列だけを使う。NDJSON の生ログ（合成も）・キーストロークの内容を外部の LLM（Codex を含む）に送らない。Codex は repo を読めないので、資料はプロンプトに貼り「シェル禁止」を明記する（`docs/external-skills.md` の送信「禁止」の出力も入れない）。
- 背景のステージの 6 回とまとめの入れ物・判定・notes・design を書き換えない。`src-tauri/`・`src/`・EH3 のファイルに触れない。Mac のブランチ（`docs/tangibility-design` ほか）を書き換えない。照合の論文の worktree とその計算に触れない。
- `.codex/budget.json` を `git checkout --` で戻さない。回す前に worktree の台帳と origin/main の台帳を見る（予算ガードの hook は `C:\GSE-prototype` の台帳を読む）。上限は必要なら理由をコメントに書いて上げてよい。
- `git add -A`・`git add <dir>` を使わない（ファイルを名指しで足す）。計測の run の最中は PR を出さない（push だけ）。`.steering` だけの変更は push だけ。
- 設計は、どの結果（下見を含む）よりも前に固定する。固定の後に変えたものは design §8 の逸脱の表に、時刻と理由を添えて書く。段は下見 0 を見て足したり動かしたりしない。
- バックグラウンドの実行の「completed」の通知は終わりより早く届くことがある。結果のファイルとログを一次で確かめてから報告する。状態を変える呼び出し（push など）の出力はファイルに保存し、見落としを見るために再実行しない。
- バックスラッシュを含む置換は heredoc で書かず、Edit か Write の .py で行う。python の書き戻しは `newline="\n"` で CRLF を混ぜない。
- 検査のスクリプトは、実の入力で通しで回すまで未検証と扱う。通っても、判定式が常に真になっていないかを変異で潰す。
- Rust・TypeScript は書かないが、Python も `print` の代わりに既存の書き方（`dump` など）に合わせる。

## 5. このタスクの後（研究者の決定・判断 5）

- 人ごとのリズムの型を持つ world で、個人の再識別と個人ごとの読み手を測る段を、このタスクが終わった後に行う。このタスクの終わりに、その段への引き継ぎを `.steering/_handoff/` に書く（tasklist の最後から 2 番目）。
