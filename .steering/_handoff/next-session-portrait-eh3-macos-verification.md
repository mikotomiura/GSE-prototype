# 引き継ぎ — EH3 の macOS の実機の確認（Mac 用）

> 作成: 2026-10-11（EH3 の実装のタスク・G-GEAR）。このメモは一次資料にしない。
> 一次は `.steering/20261011-portrait-eh3-impl/`（requirement・design・decisions 判断 1〜7・tasklist）と、
> 要件 `.steering/20261011-portrait-eh3-prereg/implementation-requirements.md`。

## §0 次のセッションの最初に貼るプロンプト

```
.steering/_handoff/next-session-portrait-eh3-macos-verification.md を読んで、EH3 の macOS の実機の確認を始めてください。
PR #351（招待）と PR3（肖像と壁紙）が main に merge 済みであることを先に確かめてください。
```

## §1 いまの状態

- EH3 の実装は 4 本の PR に分けた: PR1 記録とモード（#350・merge 済み）／PR2 招待（#351）／PR3 肖像と壁紙／PR4 配布と文書。
- macOS のコードはこの機械（Windows）ではコンパイルされていない。CI の macOS の `check` が通っていることだけが確かめられている。
- macOS 固有のコード:
  - `src-tauri/src/wallpaper_macos.rs`: `NSWorkspace` の `setDesktopImageURL:forScreen:options:error:` / `desktopImageURLForScreen:`。画面の識別子は `deviceDescription["NSScreenNumber"]`。AppKit の呼び出しは `AppHandle::run_on_main_thread` でメインスレッドへ依頼し、5 秒まで待つ。
  - `src-tauri/src/input/power_macos.rs`: `NSWorkspaceWillSleepNotification` / `NSWorkspaceDidWakeNotification`。
  - `src-tauri/src/input/observe_macos.rs`: フォーカス遷移に「GSE 自身か」の 1 bit（`NSRunningApplication::currentApplication().isActive()`）。EH3 では GSE の窓への遷移と、そこから戻る遷移を記録しない。

## §2 確かめること（実機・手で）

研究者の Mac で、`~/.gse` を退避して（または別のユーザーで）行う。壁紙を書き換えるので、先に研究者の了承を取る。

1. `GSE_O1_MODE=1 GSE_EH3_MODE='order=A,E,D;a_first=seed;grammar=lattice;drift=none'` で開発ビルドを起動し、applog に `EH3 MODE ENABLED` と `EH3 portrait layer: enabled` が出る。
2. 打鍵すると `eh3_day`（day 1・`a_seed`）が NDJSON に出て、壁紙が地（無地に近い色）になる。5 分ごとの予定で形が育つ（60 秒以上の不在の中では育たない）。
3. スリープ → 復帰で、スリープの直前に seed の印が書かれ、復帰後に地から始まる。
4. 終了（トレイの「GSE を終了」）で seed の印が書かれる（メインスレッドを塞がないことの確認・判断 7 Q4）。
5. トレイの「壁紙を元に戻す」で元の壁紙に戻り、以後書き換えない。applog と NDJSON に何も出ない。
6. 期間の後と、`eh3.mode` を外した後の起動で、元の壁紙へ戻り、`~/.gse/eh3_wallpaper_original.json` と `~/.gse/eh3/` が消える。
7. 復元の確認: 読み戻したパスと元のファイルの SHA-256 が一致する（`eh3_wallpaper_original.json` を見て手で確かめる）。
8. 複数の画面（あれば）・画面の抜き差しで、別の画面の元の壁紙を戻さない。
9. 動く壁紙・時間で切り替わる壁紙では動かない（applog に `not used (NotAPicture)` か `enabled (checked later)`）。
10. 招待: `p_stuck` が上がる打ち方（訂正を繰り返す）で、30 秒後に右上に図像が 60 秒出る。押すと説明と設定の窓が開き、`focus_transition` 行が増えない。画面共有（QuickTime の画面収録など）に図像が映らない（`sharingType`）。

## §3 守ること

- 応答は日本語にする。★・⚠️ は多用しない。
- `git add` はファイルを名指しする。main checkout の git には触らない（worktree を切る）。
- 生のログ・NDJSON を外部の LLM に送らない。
- 研究者の決定（判断 1・2・3・6）の中身を変えない。
- 見つかった不具合は `fix/portrait-eh3-macos` のブランチで直し、`decisions.md` に判断を足す。
