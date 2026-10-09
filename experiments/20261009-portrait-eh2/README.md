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

- **元の設定に必ず戻す**（Windows は `finally`、macOS は 1 か所の後始末。Ctrl+C でも戻す）。⚠️ ただし手の確認で 2 枚目のデスクトップ / Space にいる可能性がある間（最初のプロンプトから、読み戻しと操作者の「はい」で 1 枚目に戻ったと確かめるまで）は、自動では戻さず、restore ファイルと仮の画像を残して手で戻す案内を出す（2 枚目に元の画像を設定して、1 枚目に仮の画像が残るのを避けるため）。戻したあと読み戻して一致を確かめ、`restored` に真偽で記録する。
- **戻せない背景では動かない**: Windows はスライドショー・単色・Windows スポットライト（`BackgroundType` が 0 以外）・元の画像のファイルが無いとき・元の画像が Windows の Themes フォルダの写し（壁紙を替えた瞬間に上書きされる）のとき、macOS は画像が読めるファイルでないとき（動く壁紙など）。⚠️ macOS の壁紙の自動切り替え（時間ごとに替える設定）は読めるファイルの URL を返すので門を通るが、戻すと静止画になる。先に切り替えを止めてから回す。戻したあとは、読み戻したパスに加えて**元のファイルの SHA-256 が変わっていないこと**も確かめる。`-Force` / `--force` で押し切れるが、**元の背景は戻らない**ので使わない。先に背景を普通の画像にしてから回し、終わったら自分で元に戻す。
- 元のパスは結果に書かず、一時フォルダの `gse-eh2-restore-<日時>.json` にだけ置く。戻ったことを確かめたら消す。戻らなかったときは残る。
- **計測の run を回している機械では回さない**（CPU の数字が互いに乱れる）。
- 結果（`results/eh2-<os>-<日時>.json`）に、機械の名前・ユーザー名・パスは入らない。⚠️ **標準出力には一時フォルダのパス（ユーザー名を含む）が出る**ので、notes やコミットメッセージに貼らない。

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
| 2026-10-09 13:14 | Windows 11（1920×1080・1 台・背景はスポットライト） | `-DryRun` | `results/eh2-windows-20261009-131410-dryrun.json`。壁紙を替えない部分は動いた。背景が画像でないので、替えて戻す部分はこの機械では回していない（`-Quick` は設計どおり断って止まった）。12:14〜13:05 の記録は、レビューの指摘を直すたびに回し直して置き換えた |
| 2026-10-09 13:28〜13:49 | MacBook Air（M4・macOS 27.0.1・内蔵 1 台） | `--dry-run`・`--quick`・既定 | `results/eh2-macos-*.json`・`notes-macos.md`。最初の quick は読み戻しが早すぎて `restored: [false]` と記録された（設定は効いていた）。getter が約 0.2 s 遅れて追いつくので、読み戻しを待つようにスクリプトを直し（判断 M1）、quick と本番で `restored: [true]`・`restore_settled: [true]`。手の確認は未実施 |
| 2026-10-09 13:58〜14:17 | Surface Pro 8（Windows 11・内蔵 1 台） | `-DryRun`・`-Quick`・既定 | `results/eh2-windows-20261009-135800-dryrun.json`・`…-140639.json`・`…-140710.json`・`notes-windows.md`。**替えて戻す経路が初めて実機で回った**。直後の読み戻しで 30 / 30 一致・`restored` true。手の確認は未実施。⚠️ PowerShell 5.1 が書いた JSON は先頭に BOM が付く（Python では `utf-8-sig` で読む） |
