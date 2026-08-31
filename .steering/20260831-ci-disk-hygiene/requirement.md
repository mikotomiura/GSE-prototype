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

> ⚠️★★★ **2026-08-31 訂正**: 下 2 件は初版で `[x]` にしていたが、**やっていないことを
> `[x]` にしていた** (code-reviewer 指摘 #3)。★ `verify-before-claiming` 違反そのものなので
> 実体に合わせて戻す。⚠️ 何を実測して戻したかは `.steering/20260831-ci-guard-review-fixes/` に書く。

- [x] `check` の self-hosted mac で、ビルド前に空き容量を判定し不足時のみ掃除が走る
- [x] 掃除は走行中のビルド/CI ジョブを壊さない (Runner.Worker / cargo / rustc を検査)
- [x] `actionlint` (shellcheck 込み) で新規指摘ゼロ
- [ ] ⚠️ **週次の自動掃除がログを残して動作する** —— ★ **成立していない**。
      launchd への登録自体は済んでいた (`launchctl list local.gse.cargo-sweep` が返る・
      plist とスクリプトも実在・2026-08-31 11:54 の実行ログもある) が、
      ⚠️ **`cargo-sweep` が実機から失われており**、以後この週次ジョブは毎回 `exit 1` する。
      ★ しかも旧スクリプトはログに ERROR を書くだけで、誰も見に行かなければ気づけなかった。
- [x] ⚠️ **ガードが `build-macos` にも掛かっている** (指摘 #1。初版は `check` のみ)
- [x] ⚠️ **floor 発火時にキャッシュ復元を飛ばす** (指摘 #2。初版は捨てた直後に復元していた)
- [x] ⚠️ **空き容量を測れないときに fail-closed** (指摘 #4。初版は黙って掃除を飛ばしていた)
- [x] ⚠️ **掃除まわりの実体が repo に追跡されている** (指摘 #3。初版は repo 外・未追跡)

★ 上 4 件は `.steering/20260831-ci-guard-review-fixes/` で **完了した**
(PR: `fix/ci-disk-guard-review-and-fork-gate`)。
⚠️ ただし 1 件目「週次の自動掃除」は **`[ ]` のまま**である ——
★ コードは直したが、⚠️ **実機に `cargo-sweep` が無く `rustup` も壊れているため未実行**。
→ `bash scripts/maintenance/install-cargo-sweep-launchd.sh` を実機で通すまで閉じない。

## 関連ドキュメント

- `.github/actions/disk-guard/action.yml` — ★ ガードの**実体はここ 1 か所**
  (⚠️ 初版は `ci.yml` の `check` ジョブに直書きだった)
- `.github/workflows/ci.yml` — `check` / `build-macos` の Disk guard step
- `scripts/maintenance/gse-cargo-sweep.sh` — ★ 週次掃除スクリプトの**正本**
- `scripts/maintenance/install-cargo-sweep-launchd.sh` — 導入 / 再導入 / `--verify` 検査
- ⚠️ `~/.local/bin/gse-cargo-sweep.sh` / `~/Library/LaunchAgents/local.gse.cargo-sweep.plist`
  は上記インストーラが配置する**複製**である (直すなら repo 側)
