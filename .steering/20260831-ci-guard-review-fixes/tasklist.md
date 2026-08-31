# タスクリスト

## 調査 (実測)

- [x] PR #134/#136/#137/#138 の状態を確認 (→ #136/#137/#138 MERGED・#134 CLOSED)
- [x] `chore/ci-disk-hygiene` の実在を確認 (→ **削除済み**。中身は `main` にある)
- [x] `bash scripts/check-o1-release-readiness.sh` (→ 通過 18 / 未達 1)
- [x] ⚠️ 指摘 #3 の前提を検証 (→ **launchd 登録は済んでいた**。レビューの前半は誤り)
- [x] ⚠️ `cargo-sweep` の実在を検証 (→ **不在**。指摘 #4 が実際に起きていた)

## 実装

- [x] `.github/actions/disk-guard/action.yml` を新設 (実体を 1 か所に)
- [x] `check` を composite action 呼び出しに置換 ＋ `wiped` でキャッシュ復元を条件化
- [x] `build-macos` に同じガードとキャッシュ条件を追加 (指摘 #1)
- [x] fail-closed / `df -Pk` / warning 格上げ / 掃除後の再判定 (指摘 #4)
- [x] ⚠️ 自分が作り込んだサブシェル欠陥を修正 (`::error::` が変数に飲まれていた)
- [x] `scripts/maintenance/` に正本 ＋ インストーラ ＋ README (指摘 #3)
- [x] `.steering/20260831-ci-disk-hygiene/requirement.md` の誤 `[x]` を訂正 (指摘 #3)
- [x] fork 遮断を 3 ジョブに追加 (指摘 #5 / §2 候補 b)

## 検証

- [x] ガード本体を 4 状態で実走 (ok / nodf / low / sweepless) — 全て期待どおり
- [x] ★ **陽性対照**: 旧コードを注入して fail-open を再現 (exit 0 で素通りすることを確認)
- [x] `actionlint` を main と差分比較 (新規指摘ゼロ)
- [x] `shellcheck` 新規シェル 2 本 ＋ composite action 本体 (rc=0)
- [x] `scripts/check-shell-portability.sh` (通過 7 / 未達 0)
- [x] `install-cargo-sweep-launchd.sh --verify` を現状に対して実行 (❌ 2 件を正しく検出)
- [ ] ⚠️ `code-reviewer` ＋ `security-checker` の並列レビュー
- [ ] ⚠️ `/cross-review` (Codex)
- [ ] ⚠️ **CI が実際に緑になること** (★ push するまで分からない。予測しない)

## ⚠️ やっていないこと (★ 明示する)

- [ ] ⚠️ `cargo test` — **走らせていない**。Rust に 1 行も触っておらず、かつ実機の `rustup` が
      壊れてローカルで cargo が起動しない
- [ ] ⚠️ 実機でディスクを枯渇させた本番検証 — **できない** (合成ハーネスで代替した)
- [ ] ⚠️ `install-cargo-sweep-launchd.sh` の**実行** — `cargo` が壊れているため未実行。
      ★ `rustup` 復旧後に研究者が実行する
- [ ] ⚠️ §2 候補 c (鍵の退避) — 研究者の運用判断
