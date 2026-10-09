# 引き継ぎ — 肖像の EH2（壁紙 API の機械の検証）・Windows 機

> 作成: 2026-10-09（研究者の指示「引継ぎなどを書いてもらえれば win, mac ごと別の機器で実行できます」）。
> ⚠️ **このメモを一次資料にしない。** 中身は `.steering/20261009-portrait-eh1-eh2/design.md` §4 と `experiments/20261009-portrait-eh2/README.md`。
> macOS 版の引き継ぎは `next-session-portrait-eh2-macos.md`（別の機器で並行に回す）。

## §0 次のセッションの最初に貼るプロンプト

```
.steering/_handoff/next-session-portrait-eh2-windows.md を読んで、肖像の EH2 の Windows 版を回してください。
ブランチは docs/portrait-eh1-eh2 です。worktree を切って作業し、結果と notes-windows.md だけをコミットして push してください（PR は出さない）。
```

## §1 前提（この機械で回してよいか）

1. **計測の run がこの機械で走っていないこと**を研究者に確かめる（G-GEAR は CI の self-hosted runner でもある）。走っていたら回さない。
2. **背景が「画像」であること**（設定 → 個人用設定 → 背景 → 「画像」）。スライドショー・単色・Windows スポットライトだと、スクリプトは断って止まる（元に戻せないため）。⚠️ `-Force` は使わない。背景を一時的に「画像」へ替えたなら、終わったあとに研究者が自分で元に戻す（元の設定を書き留めてもらう）。
3. Windows PowerShell 5.1 で動く（PowerShell 7 でもよい）。管理者権限は要らない。

## §2 手順

```
git fetch origin docs/portrait-eh1-eh2
git worktree add -b docs/portrait-eh2-win-run C:/wt/portrait-eh2-win origin/docs/portrait-eh1-eh2
cd C:/wt/portrait-eh2-win
```

1. **壁紙を替えない確認**: `powershell -NoProfile -ExecutionPolicy Bypass -File experiments\20261009-portrait-eh2\windows\eh2_wallpaper.ps1 -DryRun`
2. **短い試し**（約 1 分・壁紙が縞と点に数回変わって元に戻る）: 同じコマンドに `-Quick`。最後に `Restored: True ... position ok: True` が出ることを確かめる。⚠️ 出なければ止めて、README の「戻らなかったとき」で戻し、研究者に報告する（**この経路は作成した機械では回せていない** —— 作成した機械の背景がスポットライトだったため）。
3. **本番**（約 12 分・その間は機械を触らない。CPU を測る）: 引数なし。
4. **任意の手の確認**（研究者がその場にいれば）: `-Manual` を付けて回す。仮想デスクトップ（Win+Ctrl+D で作る）と、画面共有か録画（Teams・Zoom・ゲームバー Win+Alt+R など）の中での見え方を y/n で答える。
5. 結果は `experiments/20261009-portrait-eh2/results/eh2-windows-<日時>.json`。中身を開いて、`restored` がすべて `true`、`per_monitor.readback_ok` が `calls` と同じかを見る。

## §3 記録とコミット

- `experiments/20261009-portrait-eh2/notes-windows.md` を新しく作り、表に書く: 日時・機械の種類（例「G-GEAR・Windows 11・モニタ 2 台」。機械の名前やユーザー名は書かない）・モード・`per_monitor` の中央値と p95・`all_monitors` の中央値・CPU（idle と busy の explorer と自分）・複数モニタで別々の画像が読み戻せたか・手の確認の答え・気づいたこと（ちらつき・反映の遅れなど）。
- ⚠️ **macOS の機器も同じブランチへ並行に push する**。衝突を避けるため、**この機器が触るのは `results/eh2-windows-*.json` と `notes-windows.md` だけ**。`README.md`・`decisions.md`・`tasklist.md`・`design.md` は触らない（まとめはこのタスクの本体のセッションが行う）。判断を書く必要があれば `notes-windows.md` の中に「判断 W1」として書く。
- コミット: ファイルを名指しして add（`git add -A` やディレクトリ単位の add は使わない）。
  ```
  git add experiments/20261009-portrait-eh2/results/eh2-windows-<日時>.json experiments/20261009-portrait-eh2/notes-windows.md
  git commit -m "docs(experiments): 肖像の EH2 を Windows で回した（<機械の種類>）" -m "Refs: .steering/20261009-portrait-eh1-eh2/"
  git push origin HEAD:docs/portrait-eh1-eh2
  ```
  push が拒まれたら `git pull --rebase origin docs/portrait-eh1-eh2` してからもう一度。
- ⚠️ **ブランチ名は `docs/` のまま**にする。`feature/*` に push すると CI が self-hosted（G-GEAR・計測の Mac）で走る（2026-10-09 に一度起きた・本タスクの判断 4）。**PR は出さない**（計測の run の後）。

## §4 守ること（CLAUDE.md・memory から）

- 応答は日本語。研究者に聞くときは AskUserQuestion に推奨と理由を添える。
- main checkout（`C:\GSE-prototype`）は別の作業が載っているので触らない。worktree で作業する。
- 結果の JSON に機械の名前・ユーザー名・パスが入っていないことを、コミットの前に目で確かめる（スクリプトは入れない作り）。
- 元の壁紙のパスは `%TEMP%\gse-eh2-restore-<日時>.json` にだけ置かれる。リポジトリに入れない。
- ⚠️ **標準出力を notes・コミットメッセージに貼らない**（一時フォルダのパスにユーザー名が出る）。コミットの前に次を回し、何も出ないことを確かめる:
  `grep -nE 'Users|/var/folders|DISPLAY#' experiments/20261009-portrait-eh2/results/eh2-windows-*.json experiments/20261009-portrait-eh2/notes-windows.md`
- 数字は「この機械で測った値」として書く。一般化しない（「GSE が示した」と書かない）。
