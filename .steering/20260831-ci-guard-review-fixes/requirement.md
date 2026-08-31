# CI ディスクガードのレビュー指摘是正 ＋ self-hosted の fork 遮断

## 背景

`.steering/20260831-ci-disk-hygiene/` で入れた CI ディスクガードは、
⚠️★★★ **無レビューで `main` に入った**。PR #136 (削除のパーミッション修正) のブランチを
`chore/ci-disk-hygiene` の**上で切ってしまった**ため、`e641874` が PR #136 に相乗りして
そのままマージされた。

その後 code-reviewer が **4 件**、security-checker が **HIGH 1 件**を指摘したが、
⚠️ **1 件も直っていない**状態で `main` に残っていた。

★ 現状の実害は限定的だった (ガードは `check` でのみ動き `|| true` で CI を落とさず、
削除範囲は workspace 配下に閉じる) が、★ **指摘は指摘として残っている**。

## ゴール

指摘 5 件 (code-reviewer 4 ＋ security-checker 1) を、**実測で裏を取りながら**塞ぐ。

## スコープ

### 含むもの

| # | 指摘 | 重さ | 出所 |
|---|---|---|---|
| 1 | ガードが `check` にしか掛かっていない (`build-macos` が無防備) | HIGH | code-reviewer |
| 2 | `rm -rf target` の直後に `rust-cache` が復元し「フルビルドに倒す」が成立しない | HIGH | code-reviewer |
| 3 | `requirement.md` の `[x]` が実体と違う ／ 実体が repo 外・未追跡 | HIGH | code-reviewer |
| 4 | `avail_gb` の無言 fail-open ／ `cargo-sweep` 不在時 echo のみ ／ 掃除後の再判定なし | MEDIUM | code-reviewer |
| 5 | 外部 fork の PR が self-hosted 実機 (＝復号鍵と同一 home) で任意コードを走らせうる | HIGH | security-checker |

### 含まないもの

- ⚠️ §2 の候補 **c** (`~/.gse/age-identity.txt` をランナーと別マシン/別アカウントへ退避)。
  ★ **本質的な対策はこちら**だが運用変更を伴い、鍵の移動は研究者の手作業である。
  → 本 PR の候補 **b** は「public 化した瞬間に成立する」経路を塞ぐだけ。**c を代替しない**。
- ⚠️ 実機の `rustup` 復旧 (下記「作業中に判明した別問題」)。研究者の判断待ち。
- sccache 導入 (`.steering/20260831-ci-disk-hygiene/requirement.md` で既に対象外)

## 受け入れ条件

- [x] ガードの実体が 1 か所 (`.github/actions/disk-guard`) にあり、`check` と `build-macos` の
      **両方**から使われている
- [x] floor 発火時にキャッシュ復元が飛ぶ (`steps.disk_guard.outputs.wiped`)
- [x] 空き容量を測れないとき **fail-closed** で落ちる (⚠️ 陽性対照で旧コードの fail-open を再現して確認)
- [x] `cargo-sweep` 不在が `::warning::` として run に出る
- [x] 掃除後に**測り直して** floor を判定する
- [x] 掃除まわりの実体 (`gse-cargo-sweep.sh` / インストーラ) が repo に追跡されている
- [x] `.steering/20260831-ci-disk-hygiene/requirement.md` の誤った `[x]` が実体に戻っている
- [x] 外部 fork の PR で self-hosted ジョブが走らない
- [x] `actionlint` が **main と同じ指摘 3 件のまま** (新規ゼロ・★ 予測でなく差分比較で確認)
- [x] 新規シェルが `shellcheck` / `scripts/check-shell-portability.sh` を通る

## ⚠️ 作業中に判明した別問題 (★ 本 PR の対象外・研究者へ報告済み)

1. **`cargo-sweep` が実機から失われていた。** 2026-08-31 11:54 に 1 度成功した記録があるが、
   その後どこにも無い。→ 週次ジョブは毎回 `exit 1`、CI ガードは「未導入」で素通りしていた。
   ★ **指摘 #4 が机上の懸念でなく、実際に起きていた**ことの証拠である。
2. ⚠️★★★ **`rustup` 本体が消えている。** `~/.cargo/bin/` の 13 個は全部 `rustup` への symlink で、
   `file` が `broken symbolic link` と言う。★ toolchain 実体
   (`~/.rustup/toolchains/stable-aarch64-apple-darwin/bin/cargo` = cargo 1.98.0) は無事。
   ⚠️ **原因は不明**。私が走らせた `cargo install cargo-sweep` は cargo を起動できずに終わっており、
   これで説明できない。★ 推測で断定しない。
   → ⚠️ **この状態では `cargo test` / `cargo build` がローカルで走らない。**

## 関連ドキュメント

- `.steering/20260831-ci-disk-hygiene/` — 初版タスク (受け入れ条件を本 PR で訂正)
- `.steering/_handoff/next-session-prompt-o1-v0-1-31-and-open-fronts.md` §2 / §3
- `scripts/maintenance/README.md`
