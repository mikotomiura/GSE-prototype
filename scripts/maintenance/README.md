# scripts/maintenance — 実機 (self-hosted ランナー) の保守

⚠️★★★ **ここに置くのは「研究者の Mac そのもの」を触るものだけ**である。
被験者に配るもの・CI の中だけで完結するものは置かない。

## なぜ repo に置くか

2026-08-31 のディスク枯渇対策で、掃除の実体を `~/.local/bin/` と `~/Library/LaunchAgents/`
にだけ置いた。⚠️ 結果として **repo の外・未追跡**になり、

- レビューできない (diff に出ない)
- 再現できない (別マシンで同じ状態を作れない)
- **壊れても誰も気づかない** ← ★ 実際に壊れた

という状態になった (code-reviewer 指摘 #3)。★ 正本を repo に置き、
インストーラ経由でのみ実機へ配置する。

## 中身

| ファイル | 何 |
|---|---|
| `gse-cargo-sweep.sh` | ★ 定期掃除 (毎日・3 日より古い成果物) の**正本**。`~/.local/bin/` の同名ファイルはここからの複製 |
| `install-cargo-sweep-launchd.sh` | 導入 / 再導入 / `--verify` 検査。★ **冪等** |

## 使い方

```bash
# 現状を検査するだけ (書き込まない)
bash scripts/maintenance/install-cargo-sweep-launchd.sh --verify

# 導入 / 直したあとの再配置
bash scripts/maintenance/install-cargo-sweep-launchd.sh
```

⚠️ `--verify` が見るのは **5 つ**で、どれか 1 つが緑でも安心しないこと:

1. `cargo-sweep` が実在するか
2. 複製が実行可能か
3. ★ **複製が正本とずれていないか** (`cmp`)
4. plist があるか / **launchd に積まれているか** (⚠️ この 2 つは別物)
5. plist の指すプログラムが**実在するか** (壊れた symlink を黙って積まない)

## ⚠️ 2026-08-31 に実際に踏んだ壊れ方 (★ 同じ轍を踏まないために残す)

| 何が起きたか | どう見えたか |
|---|---|
| `cargo-sweep` が実機から失われた | 定期ジョブは毎回 `exit 1`。★ ログを開くまで無症状。⚠️ CI 側のガードも「未導入のためスキップ」と echo して**素通り**していた |
| `~/.cargo/bin/*` の 13 個が全部 `rustup` への symlink で、**`rustup` 本体だけが消えた** | `ls ~/.cargo/bin/` には `cargo` が**見える**のに、実行すると `no such file or directory`。★ `file ~/.cargo/bin/cargo` が `broken symbolic link` と言って初めて分かる。⚠️ toolchain 実体 (`~/.rustup/toolchains/*/bin/cargo`) は無事だった |

★ 教訓: **「ファイルがある」と「動く」は別**。検査は必ず*実行できるか*まで見る。

## CI 側との役割分担

| | いつ | 範囲 | 目的 |
|---|---|---|---|
| `scripts/maintenance/` (launchd) | 毎日 | 実機全体 (ローカルクローン ＋ 全ワークツリー ＋ ランナー workspace) | **予防** |
| `.github/actions/disk-guard` | ジョブごと | その run の workspace のみ | **直前の救命** |

⚠️ 片方だけでは足りない。定期掃除は「CI が動いていない時間」にしか走れず、
ジョブ内ガードは「他のディレクトリ」を掃除できない。
