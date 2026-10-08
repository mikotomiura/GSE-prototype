# 引き継ぎ: Windows で O1（v0.1.40）がスリープをまたいで記録を続けるかを確かめる

作成 2026-10-08（Mac）。Windows 機の Claude Code で、研究者と一緒にすぐ行う。
返答・記録では絵文字や記号（★・⚠️）を多用しない（研究者の指摘）。

## 1. なぜやるか

- O1 の参加者はノート PC を閉じて使う。スリープをまたいで記録が続き、復帰後に区切り（24 時間）と再送（6 時間ごと）が追いつくかは、送られる記録の量に直結する。
- macOS は 2026-09-10 に成立している（v0.1.34・蓋閉じ 5 分 12 秒・復帰後に key 179 件・dropped 0。`.steering/20260910-measurement-binary-rebuild/sleep-test-result.md`）。
- Windows は記録が無い。検証に使ってきた Windows 機（G-GEAR・Windows 実機）は電源設定でスリープが 0（無効）になっている（`.steering/20260927-ime-observation-paper-eval-design/pilot-windows-ggear-notes.md:14`・`pilot-windows-1-notes.md:16`）。
- 設計（コードで確認済み）: 区切り・48 時間の待ち・6 時間の再送はすべて OS の時計（エポック ms）の差で判定し、60 秒ごとに確かめる（`src-tauri/src/lib.rs` の O1 daily-rotate スレッド、`src-tauri/src/o1.rs` の `ROTATE_AFTER_MS` / `SUBMIT_GRACE_MS` / `PERIODIC_RECONCILE_MS`）。スリープ中の時間も経過に入り、復帰後 1 分以内に追いつくはず。これを実機で確かめる。

## 2. 始める前に確かめること（順に）

1. どの機で行うかを研究者に聞く。ノート型（蓋を閉じられる機）があればそれが本命。
2. G-GEAR で行う場合: G-GEAR は GitHub Actions の自前ランナー（`g-gear-win-x64`）でもある。寝かせると走っているジョブが落ちる。
   - `gh run list --status in_progress` と `gh run list --status queued` で、走っている・待っているジョブが無いことを確かめる。
   - 2026-10-08 時点で PR #327 / #329 の Windows のチェックが、G-GEAR の負荷で 30 分の時間切れになって止まっている（走らせ直し待ち）。試験の前後で研究者に確認する。
3. `powercfg /a` で、その機が使えるスリープの種類を記録する（S3 か、モダンスタンバイ S0 Low Power Idle か）。モダンスタンバイでは、スリープ中もアプリが少し動くことがある。結果の読み方が変わるので、必ず記録に残す。
4. 電源設定を変える場合は、変える前の値を記録してから変える（`powercfg /q` の該当部分・設定画面のスクリーンショットは研究者）。今回は**スタートメニューの「電源」→「スリープ」で手で寝かせる**ので、タイムアウトの設定は変えなくてよい。
5. O1 の状態を見る（読むだけ）:
   - O1 v0.1.40 が動いているか。Drive の `O1_実施用_Windows.zip`（5,987,315 B・SHA-256 は `docs/o1-distribution-tag.md` の v0.1.40 節）を展開して起動したものか。
   - `%USERPROFILE%\.gse\` に `o1_participant_id` / `o1_consent_ack` / `o1_autostart_registered` があるか。**既にあれば退避してから進め、最後に戻す**（2026-09-28 の自動起動の実験と同じ作法・`.steering/20260928-o1-resilience-g1-g2-g5/g1-windows-autostart-experiment.md`）。
   - 無ければ、アプリの「研究者へ送る前に、1 回だけ確認させてください」で実験用の参加者 ID `P998` を入れて「確認しました」を押す（押さないと送信の経路が開かず、6 時間ごとの再送のログが出ない）。
   - 送信について: 記録は閉じてから 48 時間たたないと送られない。試験が 3 日以内に終われば、P998 の記録が研究者の Drive に届くことは無い。長く置く場合は、終わったあと Drive の O1 受け取りフォルダに `P998_` が無いことを確かめる。
6. 記録のフォルダ（`%USERPROFILE%\Documents\GSE-sessions\`）を見る。Documents が OneDrive に移されている機では `OneDrive\Documents\GSE-sessions\` になる。スクリプトは両方を探す。

## 3. 手順

スクリプトは `.steering/20261008-windows-sleep-test/win_sleep_check.py`。git-bash でも PowerShell でも動く（`python` か `py -3`）。読むのは NDJSON の行の種類と時刻、アプリのログの新しい行、イベントログ、プロセスの有無だけで、記録の中身は読まない。

1. **基線**: O1 を起動して 2 分以上たってから
   `python .steering/20261008-windows-sleep-test/win_sleep_check.py snapshot`
   - gse-next.exe が動いていない・o1_mode が無い、と出たら止まって直す。
2. **短い試験（必須）**: スタートメニューの「電源」→「スリープ」。5〜10 分置く。電源ボタンかキーで起こす。
3. 復帰したら、メモ帳などで 50 文字ほど打つ（中身は何でもよい。記録されるのはキーの種類だけ）。2 分待つ。
4. **点検**: `python .steering/20261008-windows-sleep-test/win_sleep_check.py check`
5. **長い試験（できれば）**: 基線を採り直し、6 時間以上寝かせる（夜通しなど）。復帰後の点検で、アプリのログに `O1 auto-submit (periodic (O1))` が**復帰から 1 分以内に**出ていれば、6 時間の再送が復帰で追いついたことになる。24 時間以上寝かせられれば、日ごとの区切り（新しい `gse_o1_*.ndjson` が開く）も見られる。

## 4. 合否（1 つでも欠けたら「成立した」と書かない）

| # | 項目 | 合格の形 |
|---|---|---|
| 1 | プロセスの生存 | 復帰後も gse-next.exe が同じく動いている |
| 2 | 本当に寝たか | イベントログに Kernel-Power 42（スリープに入った）と 107 または Power-Troubleshooter 1（復帰）がある。モダンスタンバイなら 506 / 507 |
| 3 | NDJSON の穴 | 寝ていた時間とほぼ同じ長さの穴が 1 つある。穴が無ければ「寝ていない」か「モダンスタンバイで記録が続いた」のどちらか（2 で見分ける） |
| 4 | 復帰後の打鍵 | 復帰後に `key` と `feat` が増えている（3 の手順で打った分） |
| 5 | 時計の巻き戻り | `.o1_clock_hwm` が減っていない |
| 6 | 復帰後のログ | 新しい行に、落ちた・送れないなどのエラーが続いていない。`keyboard hook may be dead`（starved_ms≈30 秒）は通常稼働でも出る既知の誤検知なので、それだけでは不合格にしない（`.steering/20260828-o1-infra-and-key-verification/decisions.md` 判断 A-2）。見るべきは `dropped` と `key` |

報告は「6 項目中 M 項目を実測で確認、判定しなかった K 項目」と数で書く。

## 5. 後片付け

- 電源設定を変えたなら戻す（変えた前後の値を記録に残す）。
- `.gse` を退避していたなら戻し、P998 の `o1_participant_id` / `o1_consent_ack` / 自動起動の登録（レジストリ `HKCU\...\Run\GSE-O1` と `StartupApproved\Run\GSE-O1`）を、実験で作ったものに限って消す。消す前に研究者に一覧を見せて了承を取る。
- `pre-sleep-snapshot.json` はコミットしない（ホームのパスが入る）。

## 6. 記録

- 結果を `.steering/20261008-windows-sleep-test/result.md` に書く（機の名前・Windows の版・`powercfg /a` の結果・各項目の実測値・判定しなかった項目）。
- 成立した場合も不成立だった場合も、`.steering/20260926-g1-o1-mac-collection-prep/o1-resilience-findings.md` の訂正の行（2026-10-08）に Windows の結果を 1 行足す。
- コミットは作業用のブランチで行い、push して PR にする。始める前に `git fetch` し、最新の main から切る（または PR #329 のブランチ `docs/sync-local-o1-steering-20261008` がまだ開いていればそこに足す）。

## 7. してはいけないこと

- NDJSON の生ログや打鍵の内容を外部の LLM（Codex を含む）に送らない。行の種類と件数・時刻だけを扱う。
- 研究者の了承なしに、電源設定・レジストリ・`.gse` を変えない。
- 判定できなかった項目を「問題なし」と書かない。
