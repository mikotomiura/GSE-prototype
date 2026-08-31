# 設計: CI ディスク枯渇の恒久対策

## アプローチ

2 層で守る。「CI が落ちる直前に自動回復する層」と「そもそも溜めない層」。

### 層 1: CI のディスクガード (`.github/workflows/ci.yml`)

`check` ジョブに `if: matrix.runner == 'gse-mac-selfhosted'` の step を 1 つ追加。

- 空き **15GiB 未満** → `cargo sweep --time 7 --recursive src-tauri`
  (7 日以上触られていない成果物だけ削除。活きたキャッシュは残るのでフルビルドにならない)
- それでも **8GiB 未満** → `rm -rf src-tauri/target` でフルビルドに倒す

⚠️ **step の位置が重要**: `dtolnay/rust-toolchain` の**後**、`Swatinem/rust-cache` の**前**。

- cargo-sweep の呼び出しに cargo が要るので toolchain より後
- rust-cache の復元自体がディスクを食うので、その前に空けておく必要がある

### 層 2: 週次の自動掃除 (launchd)

- `~/.local/bin/gse-cargo-sweep.sh` — ローカルクローンとランナー workspace の両方を
  `--time 14` で掃除し、`~/Library/Logs/gse-cargo-sweep.log` に記録
- `~/Library/LaunchAgents/local.gse.cargo-sweep.plist` — 毎週日曜 03:00、`LowPriorityIO` + `Nice 10`

## 変更対象

| ファイル | 変更 |
|---|---|
| `.github/workflows/ci.yml` | `check` に Disk guard step を追加 (+34 行) |
| `~/.local/bin/gse-cargo-sweep.sh` | 新規 (リポジトリ外) |
| `~/Library/LaunchAgents/local.gse.cargo-sweep.plist` | 新規 (リポジトリ外) |

## 安全性の設計 (最重要)

⚠️ **走行中のビルドの成果物を消すとジョブが壊れる**。掃除の前に必ず検査する。

- スクリプト側: `pgrep -f Runner.Worker` で CI ジョブを、`pgrep -x cargo|rustc` で
  ローカルビルドを検査し、いずれかが動いていれば**何もせず exit 0**
- CI 側: ジョブ自身の step なので他ジョブとの競合は `concurrency` 設定が防ぐ

保護対象 (絶対に消さない): `~/actions-runner/{.credentials,.runner,.env,bin,externals}` /
`~/.cargo/bin` / `~/.rustup` / リポジトリのソース。掃除対象は `target/` 配下のみ。

## テスト戦略

- `actionlint` (shellcheck 込み) を変更前後で実行し、指摘が同一であることを確認
- ガードのシェルロジックを実機で実行し、空き 32GiB のとき「何もしない分岐」に入ることを確認
- `cargo sweep --dry-run` で破壊しないことを確認
- スクリプトを手動実行し、exit 0 とログ出力を確認

## 却下した案

- **sccache**: 効果は大きいが `~/.cargo/config.toml` は**ランナーと共有**のため、
  PR #135 の rerun 進行中に入れると mac ジョブを巻き込んで壊しうる。マージ後に回す。
  また sccache は incremental compilation と併用できず、ローカルの編集→再ビルドが
  遅くなる副作用がある。CI 限定で入れるのが妥当。
- **`[profile.dev] debug = 0` の追加**: 既に入っていた。18G の主因はシンボルではなく
  依存クレートの旧バージョンの `.rlib` 累積だった。
- **rust-cache の削除**: self-hosted では効果が薄いが、Windows 側と設定を分岐させると
  matrix が読みにくくなる。今回は触らない。
