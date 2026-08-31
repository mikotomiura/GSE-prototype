# CI ディスク枯渇の恒久対策 (self-hosted mac)

## 背景

2026-08-31、PR #135 (ドキュメントのみ・コード差分ゼロ) の
`check (gse-mac-selfhosted, aarch64-apple-darwin)` が失敗した。

```
error: failed to build archive at
  `.../src-tauri/target/aarch64-apple-darwin/debug/deps/libgse_next_lib.a`:
  No space left on device (os error 28)
error: could not compile `gse-next` (lib) due to 1 previous error
```

同じコードが Windows の self-hosted では SUCCESS しており、**原因は変更内容ではなく
ランナー実機の空き容量**だった。発生時の空きは **424MiB**。

⚠️ 根本原因は「self-hosted は workspace が永続する」こと。GitHub-hosted の使い捨て VM なら
ジョブ終了とともに消える `target/` が、実機では**誰かが手で消すまで永久に残り増え続ける**。

実測した内訳:

| パス | サイズ |
|---|---|
| runner の `src-tauri/target` | 2.7G |
| **ローカル開発クローン `~/GSE-prototype/src-tauri/target`** | **31G** |
| `~/.cargo/registry` | 572M |

ローカルクローン側 31G の内訳は `debug` 18G / `aarch64-apple-darwin` 9.1G /
`release` 3.2G / `x86_64-pc-windows-msvc` 546M。
`debug` と `aarch64-apple-darwin` は**実質同じマシン向けの同じコード**で、
`--target` を明示すると別ディレクトリにフルセットが作られるため二重に存在していた。

## ゴール

手作業の棚卸しに頼らず、ディスク枯渇で CI が落ちない状態を自動で維持する。

## スコープ

### 含むもの
- CI (`check` ジョブ・self-hosted mac) にビルド前のディスクガードを追加
- ローカル/ランナー双方の古い成果物を週次で自動掃除する仕組み (cargo-sweep + launchd)

### 含まないもの
- sccache の導入 (PR #135 の rerun 進行中に `~/.cargo/config.toml` を触ると
  mac ジョブを巻き込んで壊しうるため、マージ後に別タスクとする)
- `~/Library/Caches` (12G) の削減。他アプリを壊しうるため対象外
- `[profile.dev] debug = 0` の追加。**既に入っており対応済み**だった

## 受け入れ条件

- [x] `check` の self-hosted mac で、ビルド前に空き容量を判定し不足時のみ掃除が走る
- [x] 掃除は走行中のビルド/CI ジョブを壊さない (Runner.Worker / cargo / rustc を検査)
- [x] `actionlint` (shellcheck 込み) で新規指摘ゼロ
- [x] 週次の自動掃除がログを残して動作する

## 関連ドキュメント

- `.github/workflows/ci.yml` — `check` ジョブの Disk guard step
- `~/.local/bin/gse-cargo-sweep.sh` / `~/Library/LaunchAgents/local.gse.cargo-sweep.plist`
