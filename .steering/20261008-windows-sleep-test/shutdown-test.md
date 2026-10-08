# シャットダウン → 電源オン → サインインで O1（v0.1.40）が自動で立ち上がり、記録するか

研究者の求め（2026-10-08 深夜「じゃあ一応試験として行おうか」）。サインアウト → サインインの自動起動は v0.1.38 で確かめ済み（`.steering/20260928-o1-resilience-g1-g2-g5/g1-windows-autostart-experiment.md`）だが、電源を切って入れ直す流れと v0.1.40 は未実施だった。

## 試験前の状態（2026-10-09 00:01・後片付けの基準）

- `%USERPROFILE%\.gse`: `g1_participant_id`・`participant_id` の 2 つだけ（O1 のファイルは無い）。
- `HKCU\...\Run` と `StartupApproved\Run`: どちらも Edge の 1 件だけ。
- 配布フォルダ `OneDrive\デスクトップ\O1_実施用_Windows`: zip の 7 ファイルだけ（`o1.autostart` は無い）。
- `Documents\GSE-sessions`: O1 のファイルは無い。`gse-app.log` は 487 行。
- `GSE-submissions` に `P998_` は 0 件。
- 高速スタートアップ: **有効**（`HKLM\...\Session Manager\Power\HiberbootEnabled = 1`）。参加者の PC の既定に近い。
- 前回の起動: `LastBootUpTime` 2026-10-04 00:10:57・explorer 2026-10-04 00:18:56。

## 基線（2026-10-09 00:04・電源を切る前）

- 研究者が `gse-next.exe` をダブルクリックで起動した（PID 25596・00:03:41）。P998 で「確認しました」を押した（00:04:03）。
- applog: `O1 autostart: registered the login entry (HKCU\...\Run\GSE-O1)`（15:04:03Z）。
- `Run\GSE-O1` = `"C:\Users\johnd\OneDrive\デスクトップ\O1_実施用_Windows\gse-next.exe"`（引用符つき）。`StartupApproved\Run\GSE-O1` は無い。
- 配布フォルダに `o1.autostart`（中身は同じ exe のパス）。`.gse` に `o1_autostart_registered`・`o1_consent_ack`・`o1_participant_id`（00:04:03）・`o1_install_id` = `990828be74d2993d`（00:03:41）。
- 記録: `gse_o1_20261008_150341.ndjson`（meta: 0.1.40・`o1_mode=marker`・`o1_install_id` は上と同じ）。00:05 の時点で `key` 158・`feat` 114。`session_end` の行は無い。
- 親プロセス: ダブルクリックで開いても親は `explorer.exe` だった。→ **親だけでは自動起動と手で開いた場合を区別できない。** サインインした後に研究者が手で開かないことを条件にする。

## 手順

1. 研究者が、スタートメニューの「電源」→「**シャットダウン**」を選ぶ（「更新してシャットダウン」が出ていても、普通の「シャットダウン」を選ぶ）。アプリはトレイから終了しない（参加者がそのまま電源を切る形を再現する）。
2. 電源が切れたのを確かめてから、電源ボタンで入れる。サインインする。
3. **アプリを手で開かない。** 3 分以上待つ（10/01 の観察では、explorer から自動起動まで 2 分 06 秒）。
4. メモ帳などで 50 文字ほど打ち、2 分待つ。
5. 新しい Claude Code のセッションで `.steering/_handoff/next-session-windows-shutdown-test.md` を読ませて点検する。

## 合否（1 つでも欠けたら「成立した」と書かない）

| # | 項目 | 合格の形 |
|---|---|---|
| 1 | 本当に電源を入れ直した | `LastBootUpTime` が 2026-10-04 から変わった。Kernel-General 13（止まった）→ 12（始まった）がある。Kernel-Boot 27 で起動の種類（高速スタートアップか通常か）を記録する |
| 2 | 自動で立ち上がった | 研究者が手で開いていないのに `gse-next.exe` が動いている。PID が 25596 と違う。起動時刻が explorer の起動の数分後。CommandLine が配布フォルダの exe |
| 3 | O1 として記録している | 新しい `gse_o1_*.ndjson` ができ、meta が 0.1.40・`o1_mode=marker`・`o1_install_id` が `990828be74d2993d` のまま |
| 4 | 打鍵が入っている | 新しいファイルで、サインイン後の打鍵の分だけ `key` が増えている。`hook_health` の `dropped` が 0 |
| 5 | 前の記録が閉じられた | 基線のファイル `gse_o1_20261008_150341.ndjson` に `session_end` の行が付いている（シャットダウンのときに付いたか、次の起動の掃除 `O1 orphan sweep: closed` で付いたかを applog で見分ける） |
| 6 | 登録が保たれている | `Run\GSE-O1` が同じ exe のまま。`StartupApproved\Run\GSE-O1` が現れたら値を記録する（10/01 は初回の自動起動で `02…` が現れた） |

報告は「6 項目中 M 項目を実測で確認、判定しなかった K 項目」と数で書く。

## 後片付け（研究者に一覧を見せて了承を取ってから）

1. アプリを終わらせる（`taskkill /PID <pid>`。`/F` を付けない）。
2. `Run\GSE-O1` と `StartupApproved\Run\GSE-O1`（あれば）を消す。どちらも試験前は無かった。
3. `.gse` の `o1_autostart_registered`・`o1_consent_ack`・`o1_participant_id`・`o1_install_id` を消す（P998 であることを確かめてから）。`g1_participant_id`・`participant_id` は触らない。
4. 配布フォルダの `o1.autostart` を消す（**2026-10-08 に一度消し忘れた**）。
5. `Documents\GSE-sessions` の `gse_o1_*.ndjson`（試験で作ったもの）と `.o1_clock_hwm` を `Documents\GSE-sleeptest-20261008\shutdown\` へ移す。`gse-app.log` は残す。
6. `GSE-submissions` に `P998_` が無いことを確かめる（48 時間の待ちがあるので、10/11 00:00 より前に片付ければ送られない）。
7. 上の「試験前の状態」と同じになったことを確かめて、ここに書く。

## 結果

（電源を入れ直した後の新しいセッションで書く）
