# 引き継ぎ — 肖像の EH2（壁紙 API の機械の検証）・macOS 機

> 作成: 2026-10-09（研究者の指示「引継ぎなどを書いてもらえれば win, mac ごと別の機器で実行できます」）。
> ⚠️ **このメモを一次資料にしない。** 中身は `.steering/20261009-portrait-eh1-eh2/design.md` §4 と `experiments/20261009-portrait-eh2/README.md`。
> Windows 版の引き継ぎは `next-session-portrait-eh2-windows.md`（別の機器で並行に回す）。

## §0 次のセッションの最初に貼るプロンプト

```
.steering/_handoff/next-session-portrait-eh2-macos.md を読んで、肖像の EH2 の macOS 版を回してください。
ブランチは docs/portrait-eh1-eh2 です。worktree を切って作業し、結果と notes-macos.md だけをコミットして push してください（PR は出さない）。
⚠️ macOS 版のスクリプトは一度も実行されていません。最初に --dry-run を回し、直す必要があれば直してから進めてください。
```

## §1 前提（この機械で回してよいか）

1. **計測の run がこの機械で走っていないこと**を研究者に確かめる（計測に使う Mac は CI の self-hosted runner `gse-mac` でもある）。走っていたら回さない。
2. **壁紙が普通の画像であること**。動く壁紙（Sonoma 以降の空撮など）は、この API では元に戻せない。スクリプトは画像が読めるファイルでないと断って止まる。⚠️ `--force` は使わない。一時的に普通の画像へ替えたなら、終わったあとに研究者が自分で元に戻す。
3. Xcode のコマンドラインツール（`swift --version` が通ること）。権限の付与は要らないはず（壁紙の設定に TCC は要らない）。もし許可を求められたら、何の許可かを研究者に伝えてから進める。
4. NSWorkspace が替えるのは**今の Space**の壁紙だけ。スクリプトは今の Space だけを替えて戻す。

## §2 手順

```
git fetch origin docs/portrait-eh1-eh2
git worktree add -b docs/portrait-eh2-mac-run ../wt-portrait-eh2-mac origin/docs/portrait-eh1-eh2
cd ../wt-portrait-eh2-mac
```

1. **壁紙を替えない確認**: `swift experiments/20261009-portrait-eh2/macos/eh2_wallpaper.swift --dry-run`
   - ⚠️ **このスクリプトは作成した機械（Windows）では一度もコンパイルも実行もされていない**。コンパイルの誤りが出たら直す（直したら、直した点を `notes-macos.md` に書き、スクリプトの修正も一緒にコミットしてよい）。
   - 結果の `screens`（画面の数と画素数）・`wallpaper_process`（`WallpaperAgent` か `Dock`）・`dryrun_cpu` の `cpu_s` が数値か null かを見る。
2. **短い試し**（約 1 分・壁紙が縞と点に数回変わって元に戻る）: `--quick`。最後に `Restored: [true, ...]` が出ることを確かめる。⚠️ 出なければ止めて、README の「戻らなかったとき」で戻し、研究者に報告する。
3. **本番**（約 12 分・その間は機械を触らない。CPU を測る）: 引数なし。
4. **任意の手の確認**（研究者がその場にいれば）: `--manual`。Spaces（Mission Control で Space を足す）と、画面共有か録画（QuickTime の画面収録・Zoom など）の中での見え方を y/n で答える。⚠️ Space を移る操作は研究者に頼む。
5. 結果は `experiments/20261009-portrait-eh2/results/eh2-macos-<日時>.json`。`restored` がすべて `true`、`per_screen.readback_ok` が `calls` と同じかを見る。

## §3 記録とコミット

- `experiments/20261009-portrait-eh2/notes-macos.md` を新しく作り、表に書く: 日時・機械の種類（例「MacBook Air M・macOS 15・内蔵 1 台」。機械の名前やユーザー名は書かない）・モード・`per_screen` の中央値と p95・CPU（idle と busy の自分と `WallpaperAgent`）・複数画面で別々の画像が読み戻せたか・手の確認の答え・気づいたこと（反映の遅れ・アニメーション・ちらつきなど）・スクリプトを直したならその内容。
- ⚠️ **Windows の機器も同じブランチへ並行に push する**。衝突を避けるため、**この機器が触るのは `results/eh2-macos-*.json`・`notes-macos.md`・（直したなら）`macos/eh2_wallpaper.swift` だけ**。`README.md`・`decisions.md`・`tasklist.md`・`design.md` は触らない。判断を書く必要があれば `notes-macos.md` の中に「判断 M1」として書く。
- コミット: ファイルを名指しして add（`git add -A` やディレクトリ単位の add は使わない）。
  ```
  git add experiments/20261009-portrait-eh2/results/eh2-macos-<日時>.json experiments/20261009-portrait-eh2/notes-macos.md
  git commit -m "docs(experiments): 肖像の EH2 を macOS で回した（<機械の種類>）" -m "Refs: .steering/20261009-portrait-eh1-eh2/"
  git push origin HEAD:docs/portrait-eh1-eh2
  ```
  push が拒まれたら `git pull --rebase origin docs/portrait-eh1-eh2` してからもう一度。
- ⚠️ **ブランチ名は `docs/` のまま**にする。`feature/*` に push すると CI が self-hosted で走る（2026-10-09 に一度起きた・本タスクの判断 4）。**PR は出さない**（計測の run の後）。

## §4 守ること（CLAUDE.md・memory から）

- 応答は日本語。研究者に聞くときは AskUserQuestion に推奨と理由を添える。
- 本体の checkout に別の作業が載っていることがあるので、worktree で作業する。
- 結果の JSON に機械の名前・ユーザー名・パスが入っていないことを、コミットの前に目で確かめる（`os_version` は入る）。
- 元の壁紙のパスは `$TMPDIR/gse-eh2-restore-<日時>.json` にだけ置かれる。リポジトリに入れない。
- 数字は「この機械で測った値」として書く。一般化しない（「GSE が示した」と書かない）。
