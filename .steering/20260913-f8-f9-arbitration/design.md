# design — F-8 / F-9

## F-8: third-party action を commit SHA へ固定する

| action | 旧 | 新 | ⚠️ 注意 |
|---|---|---|---|
| `dtolnay/rust-toolchain` | `@stable` | `@6bed0761…` | ⚠️ **ブランチ参照**だった。★ 固定先が `stable` ブランチ上で、`action.yml` の `toolchain` 既定が **`stable` のまま**であることを確認 |
| `Swatinem/rust-cache` | `@v2` | `@6323deb1…` (v2.9.2) | ⚠️ `v2` は **annotated tag** —— ★ `git/ref/tags` が返す SHA は**タグオブジェクト**で、commit ではない。`git/tags/<sha>` で解決した |
| `softprops/action-gh-release` | `@v2` | `@3bb12739…` (v2.6.2) | ★ hosted だが `contents: write` を持ち**被験者配布物を差し替えうる**ので固定 |

★ `actions/*` は**タグのまま**。⚠️ 理由を `ci.yml` に書く（GitHub 自社所有 ／ dependabot 無しでは
固定＝完全手動更新になり、★ 古いまま放置されるリスクの方が大きい）。

⚠️★★★ **置換は `uses:` 行だけに限定する。** ★ 一度 `s.replace` で全文置換して、
**follow-up 注記と過去の CI ログ引用まで壊した**（実測・やり直した）。

## F-9: 汎用 linter を入れず、不変条件を検査する

`scripts/check_workflow_invariants.py`（★ `--self-test` ＋ `scripts/tests/` = repo の既存作法）。

| # | 不変条件 | 出自 |
|---|---|---|
| 1 | 全 job が**実効 `permissions`** を持つ（top-level 継承可） | F-5 |
| 2 | third-party action が **40 桁 commit SHA** で固定（`actions/*` と `./` は除外） | ★ **F-8 の決定そのものを守る** |
| 3 | `supply-chain.yml` が **self-hosted へ向いていない** | ⚠️ 実機に被験者の復号鍵がある |
| 4 | ⚠️ **走査 0 件は exit 2**（「違反なし」と読ませない） | ★ 既存ゲートの教訓 |

★ 配線先は **`frontend-check`**（⚠️ `supply-chain.yml` は `paths` 限定で、依存を触らない PR では走らない）。

## テスト戦略

| # | 検査 | 期待 |
|---|---|---|
| T1 | `--self-test` | exit 0（6 群） |
| T2 | `python -m unittest scripts.tests.test_check_workflow_invariants` | exit 0（22 件） |
| T3 | 実データ | exit 0・★ **26 step / 第三者 7 本を検査**と出力に出る |
| T4 | ⚠️ 変異 A: 第三者をタグへ戻す | **exit 1** |
| T5 | ⚠️ 変異 B: top-level permissions を消す | **exit 1** |
| T6 | ⚠️ 変異 C: supply-chain を self-hosted へ | **exit 1** |
| T7 | ⚠️ 変異 D: 新しい第三者を可動タグで足す | **exit 1** |
| T8 | ⚠️ 空振り: workflow 0 件 / ディレクトリ不在 | **exit 2 / 4** |
| T9 | `check-tests-are-wired.sh` | ★ **14/14** |
| T10 | CI 全緑 ＋ ⚠️ `workflow_dispatch`（ブランチ）で `build-windows` 実機確認 | 緑 |

## レビュー

`code-reviewer` + `security-checker` を**並列**／`/cross-review`（⚠️ パス限定・`--ack-filtered` は研究者確認のうえ）。
