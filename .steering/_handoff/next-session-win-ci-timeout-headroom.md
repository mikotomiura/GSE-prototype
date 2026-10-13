# 起票 — Windows の CI（check ジョブ）が 30 分の上限まで余裕 8 分しかない

> 作成: 2026-09-28（`.steering/20260928-p321-paper-draft/` の出荷中に観測・研究者の指示で起票だけする）。
> ⚠️ **このメモを一次資料にしない。** 値は GitHub Actions の run と `.github/workflows/ci.yml` を開き直す。

## §1 観測したこと（一次: GitHub Actions の job の steps の時刻）

- main の run `36420188706`（PR #255 の merge `42441001`）の `check (gse-win-selfhosted, x86_64-pc-windows-msvc)`（job `108920821231`）が、逐語 "The job has exceeded the maximum execution time of 30m0s" で **cancelled**。検査のステップ（build・test・snapshot・schema・clippy・Loop worktree deny gate・Loop run guard gate）は**すべて緑**で、最後の `Loop spawn cleanup gate` の途中で打ち切られた。
- 上限は `ci.yml:333` の `timeout-minutes: 30`。
- 同じ内容の PR #255 の run（job `108912907815`・緑・全体 22 分）とのステップ別の比較:

  | ステップ | 緑の run | 打ち切られた run |
  |---|---|---|
  | Cargo build | 2 分 34 秒 | 3 分 14 秒 |
  | Cargo test | 2 分 27 秒 | 2 分 56 秒 |
  | Loop run guard gate | **10 分 22 秒** | **15 分 21 秒**（再実行 job `108944417216`: **15 分 45 秒**） |
  | Loop spawn cleanup gate | **4 分 31 秒** | **5 分 48 秒で打ち切り**（再実行: **6 分 00 秒で打ち切り**） |

- ★ 研究者の指示で Windows のジョブだけを 1 回再実行した（attempt 2）が、**同じ形で再び cancelled**（build 2 分 58 秒・test 2 分 48 秒・clippy 1 分 18 秒と、Loop のゲート以外は緑の run とほぼ同じ）。→ ★ 遅いのは **Loop のゲート 2 本だけ**で、その 2 本が PC の負荷に特に弱い。git-workflow ルール 6 に従い、それ以上は回していない。

- ★ Windows の runner（`gse-win`）は**研究者の作業用 PC（`mikoto-g-gear`）そのもの**で、打ち切られた時刻には並行する Claude のセッションの bash（IME 論文の loop-run・ディスク全体を走査する `find / -maxdepth 6 -iname *.cargo` など）が同じ PC で動いていた。→ ★ 遅くなった原因の見立て = **同じ PC での並行作業と CPU・ディスクを取り合った**（⚠️ 見立てであって計測ではない）。
- ★ 追記（2026-09-29・同日に訂正）: 本 PR の run `36431219194` の Windows ジョブは、attempt 1（2026-09-28 13:53〜14:24）が 30 分で cancelled。**attempt 2**（job `109011037190`・2026-09-29 01:43〜01:56 UTC）は**緑・全体 13 分 37 秒**（build 1 分 49 秒・test 2 分 06 秒・**Loop run guard gate 5 分 37 秒**・**Loop spawn cleanup gate 2 分 28 秒**）。続く本 PR の run `36510396762`（02:10〜02:23）と merge 後の main の run `36512457012`（02:24〜02:37）も緑で、Windows ジョブは 12 分台。
  - ⚠️ **3 本とも並行作業と重なっていた**: 同じ PC で IME 論文の W4 の loop-run（`_loop-events.jsonl` で 014 の worker が 01:51 から、018 / 019 が 02:13 まで）と、その merge ゲートの直し（`loop/014-issue`・`loop/018-issue`・`loop/019-issue` のコミットが 01:56〜02:40）が動いていた。⚠️ 本追記の最初の版は attempt 2 を「研究者が並行作業の無いことを確かめた後」「見立てと矛盾しない」と書いたが、**誤り**（events を見ずに書いた）。
  - → ★ 「同じ PC で並行作業があると遅くなる」は、**この 3 本では成り立たない**（Claude の worker と merge ゲートが動いていても 12〜13 分）。2026-09-28 に遅かった run との違い（ディスク全体の走査・並行する cargo のビルドなど）は測っていない → §2 の 2（何に時間を使っているかを先に計測する）の理由が強まった。
- 同じく 2026-09-28 の main の run `36446484801`（PR #258 の merge）の Windows ジョブは、Loop run guard gate の途中で逐語 "The self-hosted runner lost communication with the server" により failure（検査ステップの失敗ではない）。
- ★ 同じ Loop のゲート 3 本は ubuntu の `frontend-check`（`timeout-minutes: 15`）でも回っており、そちらはジョブ全体で約 2 分 → 時間を食っているのは **Windows の git-bash 上での実行**。
- 同日の別の run（`36394632998`）では macOS の self-hosted runner が「Complete job」で通信を失って failure（検査はすべて緑）→ 1 回の再実行で success。

- 追記（2026-10-13・PR #365 の出荷中）: PR #365 の run `38343081748`（attempt 1 と 2）と `38349281801` の Windows ジョブが 3 回続けて 30 分で cancelled（どれも Loop run guard gate の途中）。手順ごとの時間（秒）を直近の緑の run と比べると、遅いのはゲートだけではなかった:

  | 手順 | 10-12 の緑の run（約 20 本） | 10-13 の打ち切り（2 本） |
  |---|---|---|
  | Cargo build | 102〜131 | 495・498 |
  | Cargo test | 95〜114 | 460・389 |
  | Loop run guard gate | 304〜438 | 347・501（打ち切り） |

  打ち切りの間ずっと、同じ PC で別のセッションの計算（`C:\wt\eh3-windows-device-rest` の rhythm-stage-desk-check の `checks.py`・日本時間 10:35 開始・multiprocessing で 16 並列）が動いていた。日本時間 14:5x に 10 秒測ると python 18 プロセスが CPU を約 14.4 コア分使い、全体の負荷は 100%。attempt 1（日本時間 12:43〜）は、このセッションの 16 並列の自己検査（`selftest_main.py`）とも重なっていた。→ CPU を使い切る並列の計算があると、build と test まで 4〜5 倍に遅くなり、ゲートの前に時間を使い切る。§2 の 1〜3（上限・ゲートの時間）より、4（runner と作業の PC の共有・重い計算の並列数）が効く見込み。

## §2 決めること（別タスクで）

1. `check` の Windows ジョブの `timeout-minutes` を上げるか（⚠️ 上げても並行作業で遅くなる根本は残る）
2. Loop のゲート（`scripts/loop-run-guard-test.sh`・`loop-spawn-cleanup-test.sh`）の Windows での所要時間を短くするか（何に時間を使っているかを先に計測する）
3. Loop のゲートは ubuntu でも回っているので、Windows で回す理由（`ci.yml:630` 周辺のコメント＝git-bash の jq が CRLF を出す等）と照らして、Windows では一部だけにできるか
4. runner を研究者の作業用 PC と共有していることの扱い（重い作業中は CI が遅くなる前提で運用するか）

## §3 やらないこと

- ⚠️ 上限を上げるだけで閉じない（原因の計測を先にする）
- ⚠️ 再実行で緑になるまで回す運用にしない（git-workflow ルール 6）
