# EH2 — 壁紙 API の機械の検証（肖像・再着手の面）

> 親: `.steering/20261009-portrait-eh1-eh2/`（design §4）・`.idea/20261005-motivation-fatigue-reentry-surface.md` §8.5 の EH2。
> 仮の画像（縞と点の 2 枚）で回す。合否は置かず、記録するだけ。肖像の生成器（EH1）は使わない。

## 何を測るか

| 項目 | Windows（`windows/eh2_wallpaper.ps1`・`IDesktopWallpaper`） | macOS（`macos/eh2_wallpaper.swift`・`NSWorkspace`） |
|---|---|---|
| 設定と読み戻し | モニタごと・全モニタ一括。1 回ごとの所要時間 | 画面ごと。1 回ごとの所要時間 |
| 複数モニタ | 1 台ずつ別の画像を設定して読み戻す | 同じ |
| CPU とメモリ | 自分・`explorer`・`dwm`（`dwm` は権限が無いと null） | 自分・`WallpaperAgent`（無ければ `Dock`） |
| 仮想デスクトップ / Spaces（手・`-Manual` / `--manual`） | デスクトップ 1 で設定 → 2 へ切り替えて読み戻しと目視 | Space 1 で設定 → 2 へ切り替えて読み戻しと目視 |
| 画面共有（手・同上） | 共有か録画の中で 3 回更新 → 映り方とちらつき | 同じ |

時間: `-Quick` / `--quick` は約 1 分（3 回・何もしない 10 s・更新 10 s）。既定は約 12 分（30 回・何もしない 300 s・10 s ごとの更新 300 s）。

## 安全

- **元の設定に必ず戻す**（Windows は `finally`、macOS は最後に `restore()`）。戻したあと読み戻して一致を確かめ、`restored` に真偽で記録する。
- **戻せない背景では動かない**: Windows はスライドショー・単色・Windows スポットライト（`BackgroundType` が 0 以外）、macOS は画像が読めるファイルでないとき（動く壁紙など）。`-Force` / `--force` で押し切れるが、**元の背景は戻らない**ので使わない。先に背景を普通の画像にしてから回し、終わったら自分で元に戻す。
- 元のパスは結果に書かず、一時フォルダの `gse-eh2-restore-<日時>.json` にだけ置く。戻ったことを確かめたら消す。戻らなかったときは残る。
- **計測の run を回している機械では回さない**（CPU の数字が互いに乱れる）。
- 結果（`results/eh2-<os>-<日時>.json`）に、機械の名前・ユーザー名・パスは入らない。

## 回し方

```
# Windows（PowerShell）
powershell -NoProfile -ExecutionPolicy Bypass -File experiments\20261009-portrait-eh2\windows\eh2_wallpaper.ps1 -DryRun
powershell -NoProfile -ExecutionPolicy Bypass -File experiments\20261009-portrait-eh2\windows\eh2_wallpaper.ps1 -Quick
powershell -NoProfile -ExecutionPolicy Bypass -File experiments\20261009-portrait-eh2\windows\eh2_wallpaper.ps1 [-Manual]

# macOS（Xcode のコマンドラインツールが要る）
swift experiments/20261009-portrait-eh2/macos/eh2_wallpaper.swift --dry-run
swift experiments/20261009-portrait-eh2/macos/eh2_wallpaper.swift --quick
swift experiments/20261009-portrait-eh2/macos/eh2_wallpaper.swift [--manual]
```

`-DryRun` / `--dry-run` は壁紙を替えない（列挙・画像の生成・読み取り・CPU を数秒・結果の書き出しだけ）。

## 戻らなかったとき

- Windows: `%TEMP%\gse-eh2-restore-<日時>.json` の `monitors[].wallpaper` が元の画像。設定 → 個人用設定 → 背景で、その画像を選び直す（配置は `position`: 0 中央・1 並べて表示・2 拡大して表示・3 ページ幅に合わせる・4 ページ全体に合わせる・5 スパン）。
- macOS: `$TMPDIR/gse-eh2-restore-<日時>.json` の `url` が元の画像。システム設定 → 壁紙で選び直す。

## これまでの実行

| 日時 | 機械 | モード | 結果 |
|---|---|---|---|
| 2026-10-09 12:14 | Windows 11（1920×1080・1 台・背景はスポットライト） | `-DryRun` | `results/eh2-windows-20261009-121407-dryrun.json`。壁紙を替えない部分は動いた。背景が画像でないので、替えて戻す部分はこの機械では回していない |
