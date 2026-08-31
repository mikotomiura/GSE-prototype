# Mac ランナーのディスク清掃プロンプト（2026-08-31）

> ★ 下の「--- ここから ---」〜「--- ここまで ---」を、**Mac 側の Claude Code セッションにそのまま貼る**。
> 作成元: Windows 側セッション（PR #135 の CI 失敗対応）

---

--- ここから ---

このマシンは GitHub Actions の self-hosted ランナー `gse-mac` です。**ディスクが枯渇して CI が落ちています。**再生成可能なビルド成果物だけを消して復旧してください。

## 背景（確認済みの事実）

リポジトリ `mikotomiura/GSE-prototype` の PR #135（**ドキュメントのみ・コード差分ゼロ**）で、
`check (gse-mac-selfhosted, aarch64-apple-darwin)` が失敗しました。ログの逐語:

```
error: failed to build archive at
  `/Users/johnd/actions-runner/_work/GSE-prototype/GSE-prototype/src-tauri/target/aarch64-apple-darwin/debug/deps/libgse_next_lib.a`:
  No space left on device (os error 28)
error: could not compile `gse-next` (lib) due to 1 previous error
```

同じコードは **Windows の self-hosted ランナーでは SUCCESS** しています。つまり原因は
変更内容ではなく、**この Mac の空き容量**です。

## やってほしいこと

### Step 1: 消す前に現状を記録する（必須）

```bash
date
df -h /
echo "--- 容量の内訳 ---"
du -sh ~/actions-runner/_work/GSE-prototype/GSE-prototype/src-tauri/target 2>/dev/null
du -sh ~/.cargo/registry ~/.cargo/git 2>/dev/null
du -sh ~/actions-runner/_work/_temp ~/actions-runner/_work/_tool 2>/dev/null
du -sh ~/Library/Caches 2>/dev/null
```

**この出力をそのまま報告してください。**どこが太っているかで次の判断が変わります。

### Step 2: ランナーがジョブ実行中でないことを確認する（必須）

```bash
pgrep -fl "Runner.Worker" || echo "ジョブ実行中ではない（安全）"
```

⚠️ **`Runner.Worker` が出たらジョブ実行中です。その場合は削除せず、終わるまで待ってください。**
消すと走行中のジョブが壊れます。

### Step 3: ビルド成果物を消す（最も効く・再生成可能）

```bash
rm -rf ~/actions-runner/_work/GSE-prototype/GSE-prototype/src-tauri/target
df -h /
```

`target/` は `cargo build` が作り直します。消して安全です。次回ビルドだけ遅くなります。

### Step 4: Step 3 で足りなければ、cargo キャッシュとランナーの一時領域

```bash
rm -rf ~/.cargo/registry/cache ~/.cargo/registry/src ~/.cargo/git/checkouts
rm -rf ~/actions-runner/_work/_temp/*
df -h /
```

### Step 5: 最終確認と報告

```bash
df -h /
pgrep -fl "Runner.Listener" || echo "警告: ランナーのリスナーが動いていない"
```

**報告してほしいこと**: 清掃前後の空き容量（`df -h /` の Avail）と、リスナーが生きているか。

## ⛔ 絶対に消してはいけないもの

| パス | 理由 |
|---|---|
| `~/actions-runner/.credentials*` / `.runner` / `.env` | **ランナーの登録情報。消すと再登録が要る** |
| `~/actions-runner/bin` / `externals` | ランナー本体 |
| `~/.cargo/bin` | rustup / cargo の実行ファイル本体（`registry` とは別物） |
| `~/.rustup` | ツールチェイン本体。消すと再ダウンロード（数 GB） |
| `~/actions-runner/_work/GSE-prototype/GSE-prototype/` 直下のソース | ⚠️ **`target/` だけを消す。リポジトリ本体は消さない** |
| `~/Library/Keychains` | 署名まわり |

⚠️ `rm -rf` の対象を打つ前に、**そのパスが上の表に無いことを必ず確認**してください。
⚠️ **`~/Library/Caches` の一括削除は避けてください**（他アプリを壊しうる）。どうしても要るなら
`~/Library/Caches/Homebrew` など**対象を限定**して報告した上で消してください。

## やらなくてよいこと

- ⚠️ **CI の再実行は不要です。**Windows 側のセッションが `gh run rerun 33349992247 --failed` で
  実行し、マージまで進めます。**空き容量を報告するところまでで止めてください。**
- リポジトリの `git pull` / ビルド / テストは不要です。

--- ここまで ---
