# 次セッション — IME 論文: Windows の追補の OSF 登録と M7（Windows の本計測）

> ★ **2026-10-03 追記: 追補は OSF に登録済み — https://osf.io/4jwzn（DOI 10.17605/OSF.IO/4JWZN・2026-10-03T13:56 UTC・添えたファイルの SHA が一致・`notes.md` に記録）。§1 の未了 1 は済み。**
> 作成: 2026-10-03（Surface Pro 8・M5 と M6 を終えたセッションの最後）。
> ⚠️ **このメモを一次資料にしない。** 一次は `.steering/20260927-ime-observation-paper-eval-design/` の `decisions.md`（**判断 137〜142**）・`tasklist.md`・`pilot-windows-1-notes.md`・`attack-me/prereg-ime-windows/round-1・2/verdict.md` と、凍結した `papers/ime-observation/experiment/preregistration.md` の **§10**・`deviations.md`・`data.windows.md`・`kit/run/README.windows.md`。状態は着手時に `git fetch` で測り直す。

## §0 打ち込む用

```
git fetch → 状態を確かめる（PR の merge・タグ ime-observation-prereg-windows が origin にあるか）。
.steering/_handoff/next-session-ime-paper-m7-windows.md を読んで §2 から始めてください。
一次は decisions.md の判断 137〜142、事前登録 §10（とくに §10.6〜§10.9）、deviations.md、data.windows.md、kit/run/README.windows.md。
⚠️ 凍結のタグ ime-observation-prereg-windows のコードは変えない（変えるなら deviations.md に逸脱として先に記録し、研究者に戻す）。
⚠️ Windows の計測は、追補の OSF 登録の日付より後でなければならない（§10.1）。登録が済むまで計測しない。
⚠️ 合成キーを送る run は研究者の答えで「離席中に自動」（研究者は常に離席している扱い）。
Skill: verify-before-claiming・reproducibility-discipline・git-workflow・data-privacy。
応答は日本語。公開物（papers/）は学術的な英語・GSE への言及なし。コミットは git add パス指定（-A 禁止）。
```

## §1 状態（2026-10-03 の終わり）

- **M5（Windows の較正パイロット）と M6（Windows の追補）は済んだ**。Surface Pro 8 = 計測する機械で行った（判断 136）。
  - 凍結の commit `a57c4fd79134d68364c29b440637bfb717a881cb`・タグ `ime-observation-prereg-windows`（annotated）。`frozen_at: 2026-10-03`・`sha256` は macOS と同じ値（`64dfbb6e…`）。
  - 書き出しの一覧: 108 ファイル・SHA-256 `f61af353301e1370ac27c4a7425e8c2eb32991df9f7a2a765a26948da87787b7`（`.steering/…/freeze-export-list-windows.txt`）。凍結したファイルの SHA-256 `f86209631e495d2c7e80dab266a91814728aa55a18485da106df836c3cec2b1d`。`experiment/notes.md` に記録済み（OSF の URL はまだ）。
  - 逸脱 D1（Windows の S4 は Esc 3 回）・D2（Windows の計画と参照 `win_tsf` の照合）・D3（長い試行は oracle の送出の幅・正解の長さは感度）・D4（観測の key 行が送った押下で説明されなければ中止）。macOS の計画と結果が変わらないことは `3cc151c7` で確かめた（`deviations.md` 末尾）。
  - attack-me: round 1 major → round 2 minor → 直して凍結。完了時レビュー（code-reviewer ∥ security-checker）の指摘も直した。⚠️ `/cross-review` は省略（この Surface に Codex CLI が無い・`python3` が Store のスタブで Codex 系の hook が fail-closed になる）。
- **未了**:
  1. ★ **研究者の作業: OSF Registries に追補を登録する**（macOS の登録 `https://osf.io/9nh7r` の前例。添えるもの: 凍結したファイル〔`git show ime-observation-prereg-windows:papers/ime-observation/experiment/preregistration.md` を LF のまま〕・commit の 40 桁・一覧の SHA）。→ URL・DOI・登録の日付・添えたファイルの SHA-256 を `experiment/notes.md` に追記（macOS の段落と同じ形）。
  2. PR（枝 `feature/ime-m6-windows-addendum`）の merge。
- この機械の注意: 作業コピーは `core.autocrlf=true`（CRLF）→ 計画は**書き出し（LF）から**作る。`kit/check.sh` は LF の worktree（`git -c core.autocrlf=false worktree add …`）で回す。`python3` は `~/ime-pilot/bin` を PATH の先頭に置くと 3.11.9 になる。パイロットの生ログ・封印は `~/ime-pilot/runs/`（git に入れない）。

## §2 やること（M7: Windows の本計測・登録の後）

1. 登録の日付を `notes.md` で確かめる（今日より前・計測より前）。
2. タグ `ime-observation-prereg-windows` から書き出す（`export.internal.py --allow-missing-license`）→ 一覧の SHA が `f61af353…` と一致することを確かめる → 書き出した側でロガーと `refinput-windows` をビルド（`--locked`）。
3. `kit/run/README.windows.md` の手順: 計画を作り SHA が `b7bdf8fc…36b0` と一致すること・セルのファイル（`cell.windows.json` を写して `ime` に版、`clock_sync_disabled` / `auto_update_disabled` を true に）・Windows 11 Home の更新の一時停止（12〜13 時間を覆う）と「時刻を自動的に設定」を切る・電源。
4. ★ §10.8: **IME の版（`IMJPTIP.DLL`）がパイロット（10.0.26100.8875）と違えば**、先に 39 試行の点検（`plan-verify` と同じ形）を回し、39 / 39 でなければ測らずに研究者に戻す。
5. 本計測（Windows のセル）→ 直後に `delivery.py` の点検（§3.4 と §10.8: k = 0・`excluding_mode_keys`・`src` が `win_tsf`・D4 の観測の区間）→ `data.windows.md` の Run checks に 1 行 → **すぐ commit して push**（§10.8）。中止なら同じ計画で最大 3 回。
6. 問 5 の Windows（`idle` → `working`・別の夜・`kit/e3`）。`working` も §10.8 の規則と点検の行。`cpu_all_zero` は `working` だけ不十分（§10.9）。
7. 解析は §10.7 の命令（`pipeline.py --runs-from experiment/data.windows.md … --out experiment/results/windows`）で、Windows のタグから。macOS のセルは Windows のタグから解析しない。

## §2.5 進み具合（2026-10-03 23:50〜 JST のセッション）

- PR #302 は merge 済み（`6c6aefe0`）・タグは origin にある。登録日 2026-10-03 → **計測は 2026-10-04 0:00 JST 以降に始める**（§10.1「登録日が計測より前」）。
- ✅ §2-2: LF の worktree `~/ime-m7/wt`（タグ `a57c4fd7`）から書き出し `~/ime-m7/export` → 108 ファイル・一覧 `~/ime-m7/export-list.txt` の SHA-256 `f61af353…87b7`（コミット済みの一覧とバイト一致）。ロガーと `refinput-windows` を `--locked` でビルド済み。
- ✅ §2-3 の計画: `~/ime-m7/plan/plan-windows.jsonl` の SHA-256 `b7bdf8fc…36b0`（§10.6 と一致）。
- ⚠️ **版が変わった**: `IMJPTIP.DLL` **10.0.26100.8972**（パイロット 8875）・OS build **26200.9168**（パイロット 8875）→ §10.8 の 39 試行の点検が要る（計画は `~/ime-pilot/plan-verify.jsonl`・SHA `f02e046b…0154`・パイロットと同じ。セルは本計測のセルのファイル。合否は `gt_sessions.py --rules experiment/gt_rules.json`〔`win_tsf`〕の `oracle_agreement` で 39 / 39）。
- ⚠️ **再起動待ちの更新** KB5129195（2026-10-03 22:02 に「reboot is necessary」・`RebootPending` あり）→ 計測中の自動再起動を避けるため、**再起動して更新を終えてから**版を読み直し、その版でセルのファイルを作り、点検 → 本計測。
- 未了の手作業（研究者）: AC 電源（23:55 時点で放電中 52%）・更新の一時停止・「時刻を自動的に設定」を切る（今は `Type NTP`）。スリープ / 画面オフ 0・スクリーンセーバーなしは確認済み。self-hosted runner のサービスは無い（確認済み）。

## §3 気をつけること

- ⚠️ 凍結のコードを変えない。欠陥が見つかれば直さずに止めて研究者に戻す（逸脱の記録は研究者が決める）。
- ⚠️ 観測の ImeShadow（セッションの行）は、計測の解析まで読まない（パイロットの封印は寄託のためにだけ開ける・§10.10）。
- ⚠️ 生ログを git に入れない・外部の LLM に渡さない。参照のログのキーコードを転記しない。
- ⚠️ 合成キーは前面の窓に入る。run の間は誰も PC に触れない（タブレットなのでタッチ・ペンも）。
- ⚠️ G-GEAR は Windows の CI の self-hosted runner。この Surface はそうではない（確かめてから）。

## §2.6 進み具合（2026-10-04 0:20〜1:50 JST のセッション・枝 `docs/ime-m7-windows-d5`・PR #303）

- 再起動後の版: OS build 26200.9457・`IMJPTIP.DLL` 10.0.26100.9278（パイロット 8875）。AC・NoSync・更新の一時停止（10-29 まで）は確認済み。
- ★ **逸脱 D5**（判断 143）: 凍結の `cell.windows.json` の相対パス（`kit/logger/...`）では Windows で子が起動しない → セルのコピー `~/ime-m7/cell-windows.json`（SHA-256 `0e4c17ed…4fb6`）で 2 つの exe を `kit\...` に。計測の前に push 済み（`563c08a4`）。
- ✅ §10.8 の 39 試行の点検: **39 / 39**（`~/ime-m7/runs/verify-m7`・観測は封印済み）。
- ❌ **試み 1**（`~/ime-m7/runs/aborted/cell-1`）: 00:38 起動 → 00:59 に Claude Code がメモリ不足でバックグラウンドの shell を止めた。`run.json` なし。`data.windows.md` に行を記録・push 済み（`2cab630c`）。残りは最大 2 回。
- 片付け: npm / pip のキャッシュ・`src-tauri/target`・パイロットの `target`・前セッションの worktree 2 つを消した（C: の空き 4.8 → 8.8 GB）。
- **試み 2**: 研究者が VS Code を閉じ、単独の PowerShell から `start_windows.py … --run-dir C:/Users/johnd/ime-m7/runs/cell-2` を起動する（Claude Code の外）。
- **次のセッション**: `cell-2` の `run.json` の有無を確かめる → `delivery.py`（`data.md` の Deposit procedure 1・`--pre-ms 20 --tail-ms 300`）→ `data.windows.md` の Run checks に試み 2 の行（manifest の SHA-256・D4 は `observation.segments.excluding_mode_keys.max_unexplained_beyond_markers`）→ すぐ commit・push → PR #303 を CI 緑で merge。⚠️ git の identity が無い機械なので `git -c user.name="Mikoto Miura" -c user.email="164107357+mikotomiura@users.noreply.github.com"`。

## §2.7 次のセッションの起動と打ち込む用（試み 2・2026-10-04 1:50 JST）

研究者の手順: Slack・Edge を通知領域から終了 → VS Code を閉じる → Win+R「powershell」（管理者でない）→

```
$env:CLAUDE_CODE_DISABLE_BG_SHELL_PRESSURE_REAP = "1"
cd C:\GSE-prototype
claude
```

打ち込む用:

```
.steering/_handoff/next-session-ime-paper-m7-windows.md の §2.6・§2.7 を読んで、M7 の試み 2 を起動してください。
1. 状態を測る: git fetch・枝 docs/ime-m7-windows-d5（PR #303）・版（IMJPTIP.DLL 10.0.26100.9278・build 26200.9457 から変わっていないか）・AC・NoSync・RebootRequired なし・空きメモリ。変わっていたら起動せずに戻す。
2. 計画 ~/ime-m7/plan/plan-windows.jsonl の SHA-256 が b7bdf8fc…36b0、セル ~/ime-m7/cell-windows.json が 0e4c17ed…4fb6 であることを確かめる。
3. run は Claude Code のバックグラウンドのタスクにしない。PowerShell の Start-Process で独立したプロセスとして起動する（作業ディレクトリ ~/ime-m7/export・python kit/run/start_windows.py --cell C:/Users/johnd/ime-m7/cell-windows.json --plan C:/Users/johnd/ime-m7/plan/plan-windows.jsonl --run-dir C:/Users/johnd/ime-m7/runs/cell-2 --i-understand-this-sends-keys・標準出力と標準エラーは ~/ime-m7/runs/cell-2.out / cell-2.err へ）。起動後 1 分で前面の確認（cell-2.out の "brought to the front: yes"）と子の生存を確かめる。
4. 終了の見張りは run.json の出現 または start_windows.py のプロセスの消失を until ループで（両方の終わり方を拾う）。
5. 終わったら §2.6 の「次のセッション」の点検 → data.windows.md に試み 2 の行 → すぐ commit・push（§10.8）。
⚠️ 凍結のタグのコードは変えない。観測のセッション行は読まない。生ログを git に入れない。run 中は誰も PC に触れない。git は -c user.name/-c user.email（§2.6）。
Skill: verify-before-claiming・reproducibility-discipline・git-workflow・data-privacy。応答は日本語。
```

## §2.8 進み具合（2026-10-04 1:55〜13:05 JST のセッション）

- 01:51 の `cell-2`（`runs/aborted/cell-2`）は管理者権限でランナーが最初の試行の前に拒否・鍵は送っていない → `delivery.py` は exit 0・数はすべて 0（`runs/aborted/cell-2-admin.delivery.json`）。研究者の判断で**行は残し、最大 3 回には数えない**（`618892d1`）。⚠️ この判断を `decisions.md` に逸脱として書くかは研究者が決める。
- ✅ **試み 2**（`~/ime-m7/runs/cell-2`）: 01:57:31 に `Start-Process` で起動 → 13:03 に完了。2925 / 2925 試行・中止なし・manifest SHA-256 `5c74a1fa…3d82`。`delivery.py` exit 0・`src` `win_tsf`・4 つの数と D4 はすべて 0・計画外のフォーカスの喪失 0。行を記録して push 済み（`1c4a60b0`）。ロガーの stderr に `candidate window stale — auto-resetting` の WARN が 2 回（18:12Z・23:50Z）。
- 次: PR #303 を CI 緑で merge → §2 の 6（問 5 の Windows: `idle` → `working`・別の夜）→ §2 の 7（解析）。

## §2.9 進み具合（2026-10-04 13:10〜21:25 JST）

- ✅ PR #303 を CI 緑で merge（`93b4cdbd`）。
- ✅ **問 5 の `idle`**（`~/ime-m7/runs/e3-idle`）: 研究者の指示で 13:16 JST に開始（昼・本計測の終わった日の続き）→ 21:16 に完了。ロガーは単独で `Start-Process`（観測ログ `runs/e3-idle-obs.jsonl` は寄託しない・§3.4）、サンプラーは Git の bash で `run_e3.sh idle 28800 30`（PATH の `bash` は WSL なので使わない）。`summarize_e3.py`: 879 行・status `measured`・`cpu_all_zero: false`・CPU 平均 5.56 %・中央値 4.68・p95 10.82・最大 20.21・ワーキングセット最終 15.1 MB・傾き 0.01 MB/h・7.99 h・間隔の中央値 33 s。`samples.tsv` SHA-256 `43ab3b39…5f59`・`conditions.txt` `13bf360f…8122`・ロガーの SHA-256 `5f8a0567…06bd`。終了後にロガーを止めた。
- ⚠️ 研究者が決めること: (1) `idle` を昼に、本計測と同じ日に行ったことを「一夜ずつ・別の夜」（§6.10・§10.8）からの逸脱として記録するか。(2) 01:51 の拒否された開始を数えない判断の記録（§2.8）。
- `data.md` の手順 1 のとおり `idle` は Run checks に行を持たない。`data.windows.md` に問 5 の表は無い（寄託の時に追記する）。
- 次: 問 5 の `working`（`idle` と別の夜・`run_e3.sh working 28800 30 …` を先に起動 → 別のプロセスで本計測と同じセルと計画の `start_windows.py`・12〜13 時間・直後に `delivery.py` の点検と Run checks の行・`cpu_all_zero` なら不十分）→ §2 の 7（解析）。⚠️ 見張りの shell はメモリ不足で Claude Code に止められることがある（run 本体は外のプロセスなので無事）。

## §2.10 進み具合（2026-10-04 21:25〜2026-10-05 10:10 JST）

- ✅ **問 5 の `working` 試み 1**: 研究者の指示で `idle` の終了直後に開始（⚠️ `idle` と同じ夜にかかる・「別の夜」からの逸脱として記録するかは研究者が決める）。21:29:23 にサンプラー `run_e3.sh working 28800 30 runs/e3-working`（Git の bash・`E3_EXE` にロガー）→ 21:29:36 に `start_windows.py`（本計測と同じセル・計画・`runs/q5-working-1`）。ランナーは 08:35 に完了: 2925 / 2925・中止なし・manifest SHA-256 `1e5f40ac…217a`。`delivery.py` exit 0・`src` `win_tsf`・4 つの数と D4 はすべて 0。Run checks に行（`3007fb2d`）。
- `summarize_e3.py`（idle と working を並べて）: working は 880 行（不在 1 行 = 起動直後）・status `measured`・`cpu_all_zero: false`・CPU 平均 5.37 %・中央値 4.66・p95 10.84・最大 15.51・ワーキングセット最終 16.3 MB・傾き 0.09 MB/h・7.99 h。`samples.tsv` SHA-256 `638da0ea…f88f`・`conditions.txt` `9b6ae939…8345`。
- ロガーの stderr に `candidate window stale — auto-resetting` が本計測と working で各 2 回。
- 次: 問 5 の寄託（`samples.tsv`・`conditions.txt` の両条件）・本計測の寄託・§2 の 7（解析: §10.7 の命令を Windows のタグから）。研究者の判断待ち: `idle` / `working` の日時の逸脱の扱い・01:51 の開始の扱い。
