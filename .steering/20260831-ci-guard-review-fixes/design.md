# 設計 — CI ディスクガードの是正 ＋ fork 遮断

## アプローチ

### 指摘 #1: ガードを `build-macos` にも掛ける

⚠️ 直書きを 2 か所に複製すると **必ず片方だけ直る事故**になる (今回まさにそれが起きた)。
→ ★ **composite action** `.github/actions/disk-guard/action.yml` に実体を 1 つ置き、
`check` と `build-macos` の両方が `uses: ./.github/actions/disk-guard` で呼ぶ。

⚠️ `build-macos` を優先する理由: 同じ `gse-mac` 実機で release ＋ dmg を 40 分掛けて作るため
`check` よりディスクを食い、落ちると**配布物が 1 つも作れない**。

### 指摘 #2: floor 発火時にキャッシュ復元を飛ばす

action が `wiped` (true/false) を出力し、呼び出し側の `Swatinem/rust-cache@v2` に
`if: ${{ steps.disk_guard.outputs.wiped != 'true' }}` を付ける。

⚠️ **`!= 'true'` にした理由**: Windows レグでは `disk_guard` step 自体が `if` で skip され、
`outputs.wiped` は**空文字**になる。`== 'false'` だと Windows でキャッシュが効かなくなる。
★ `!= 'true'` なら空文字は真 = 従来どおり復元される (Windows の挙動は不変)。

### 指摘 #3: 実体を repo に追跡する

| 置き場所 | 何 |
|---|---|
| `scripts/maintenance/gse-cargo-sweep.sh` | ★ 週次掃除の**正本** |
| `scripts/maintenance/install-cargo-sweep-launchd.sh` | 配置 ＋ launchd 登録 ＋ `--verify` |
| `scripts/maintenance/README.md` | 役割分担と、実際に踏んだ壊れ方 |

⚠️ **plist は追跡しない。** `/Users/johnd/...` を直書きした plist を repo に置くと
別マシンで壊れる。→ インストーラが `$HOME` から**生成**する。

★ `--verify` は 5 点を見る。⚠️ 特に「**plist がある**」と「**launchd に積まれている**」を
別々に見る (レビューは前者だけ見て「未完」と判断していたが、実際には後者も済んでいた)。

### 指摘 #4: fail-closed 化

```
旧: avail_gb() { df -k . | awk ... }        # df 失敗 -> 空文字
    if [ "$(avail_gb)" -lt 15 ]; then       # [ "" -lt 15 ] は非 0 -> if が偽 -> 黙って通過
新: 数値でなければ return 1 -> ::error:: -> exit 1
```

★ あわせて 3 点:
- `df -Pk` (POSIX 出力を強制。⚠️ `-P` 無しは長いデバイス名で**行が折り返る**)
- `cargo-sweep` 不在を `::warning::` に格上げ (⚠️ **実際に常時この分岐だった**)
- 掃除後に**測り直して** floor 判定 → さらに掃除後も floor 未満なら `::error::` ＋ exit 1
  (⚠️ 放置すると 20-40 分後に `os error 28` で落ちる。同じ失敗なら早くて読める方がよい)

#### ⚠️ 実装中に自分で作り込んだ欠陥 (★ 記録する)

初版では `before="$(measure before)"` と**コマンド置換で**呼んでいた。
⚠️ `$( )` はサブシェルなので、(a) 中の `exit 1` はサブシェルを抜けるだけ、
(b) **`::error::` の出力が呼び出し側の変数に飲まれて run ログに出ない**。
→ ★ 大域変数 `GB` に置いて現在のシェルで実行する形に直した。

### 指摘 #5 (security-checker HIGH): 外部 fork の遮断

```
github.event_name != 'pull_request'
  || github.event.pull_request.head.repo.full_name == github.repository
```

を `decide-win-runner` / `check` / `build-macos` の job-level `if` に足す。

⚠️ **`build-macos` では冗長**である (`pull_request` の `github.ref` は `refs/pull/N/merge` で
`refs/tags/v*` にならないので元々到達しない)。★ トリガーが増えたときに**黙って無防備に戻らない**
ための明示であり、いま何かを塞いでいるのではない —— と注記に書く。

⚠️ **副作用**: 外部 fork の PR では `check` / `build-macos` が skip され、
hosted の `frontend-check` だけが走る。→ ★ 外部 fork をフル検証したいなら
repo 内のブランチへ取り込んでから PR を出し直す (注記に書く)。

## テスト戦略

⚠️★★★ **CI を実際に落として確かめることはできない** (ディスクを枯渇させられない)。
→ ★ ガード本体を**抜き出して 4 状態で実走**させる。

| ケース | 期待 | 実測 |
|---|---|---|
| `ok` (空き 200GiB) | wiped=false / exit 0 / target 残存 | ✅ 一致 |
| `nodf` (df が壊れる) | ⚠️ `::error::` が**画面に出て** exit 1 | ✅ 一致 |
| `low` (空き 3GiB) | warning ＋ `rm -rf` 発火 ＋ wiped=true ＋ exit 1 | ✅ 一致 (CANARY 消滅を確認) |
| `sweepless` (空き 10GiB) | warning が出る / wiped=false / exit 0 | ✅ 一致 |

★ **陽性対照**: 旧コードを同じハーネスに注入して `nodf` を走らせ、
`free before:  GiB` (空欄) ＋ `[: : integer expression expected` ＋ **exit 0 で通過**を再現した。
→ ⚠️ 指摘 #4 は机上の懸念ではなく、**検査が捕まえる実在の欠陥**である。

### 静的検査

- `actionlint` — ⚠️ 予測せず、**main の出力と差分比較**する (main = 3 件 / 本 PR = 同じ 3 件)
- `shellcheck` — 新規シェル 2 本 ＋ composite action の本体 (抽出して) すべて rc=0
- `scripts/check-shell-portability.sh` — 通過 7 / 未達 0

⚠️ **`cargo test` は走らせていない。** ★ 本 PR は Rust に 1 行も触っていないことに加え、
実機の `rustup` が壊れており**ローカルで cargo が起動しない** (requirement.md 参照)。
→ Rust 側の検証は CI に委ねる。**「走らせた」とは書かない。**
