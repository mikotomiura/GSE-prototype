# main へのマージ計画（★ 計画のみ。⚠️ 本タスクでは実行しない）

> ★ 一次の実測は `evidence.md`「マージ / schema parity / 配布経路の材料」。
> ⚠️ 実行の可否・時期は**研究者判断**。★ 特に **G1 の実施中にタグを動かす**ことは
> ADR-034 D3 に触れるので、判断 2（「最初の配布」＝リブート後の次の配布）と一緒に読むこと。

## 1. いまの形（2026-09-20 実測）

| 項目 | 値 |
|---|---|
| `git rev-list --count main..HEAD` | **140** |
| `git rev-list --count HEAD..main` | **2**（`093ebf1` ＋ マージコミット `92fd22f`） |
| merge-base | `a41150e`（2026-09-13） |
| ブランチ側の差分 | **251 files / +32,624 / -227**（Add 201・Modify 50・**削除と改名は 0**） |
| ★ merge-base から見た main の**純増分** | **`.steering/_handoff/README.md` の 1 ファイルだけ** |
| 衝突予測 | ⚠️ **1 件のみ**: `.steering/_handoff/README.md`（`git merge-tree --write-tree main HEAD` = exit 1・CONFLICT 1 行） |

★ ADR-029 の本文は **分岐点より前に共有履歴へ入っている**ので、main 側の
`92fd22f`（ADR-029 のマージ）は**内容としては新規ではない**。

## 2. 衝突の中身と解き方（1 件）

- **ファイル**: `.steering/_handoff/README.md`（引き継ぎの一覧表）
- **両側**: 同じ表の同じ行を別の文字列に書き換えている。
  - main 側: 「O1 同意へ『二次利用（表現）』の任意項目を足す」を **未着手 → 完了**へ。
  - ブランチ側: 同じ行を別表現に変え、さらに行を多数追記。
- **解き方**: ★ **ブランチ側の表を土台にし、main 側が付けた「完了」の更新をその行へ移す**
  （⚠️ どちらかを丸ごと捨てない —— main 側の「完了」は**実際に完了した事実**の記録）。
- ⚠️ 解決したら **`.steering/_handoff/README.md` に本タスクの行も足す**（本タスクの引き継ぎ）。

## 3. 順序（★ この順でしか安全に進めない）

```
(1) マージ前の検証（手元・下記 §4）
      ↓
(2) main を取り込む → 衝突 1 件を解く → マージ後にもう一度 §4
      ↓
(3) schema の同期（⚠️ ここを飛ばすと gse-dataset 側が古いまま drift が残る）
      cd src-tauri && cargo run --bin emit_schema
      → src-tauri/schema/current.json と byte-equal を確認
      → gse-dataset へコピー → **両 repo を同期コミット**
      → python scripts/check_schema_parity.py --dataset C:/gse-dataset  # exit 0 を確認
      ↓
(4) 新しい `v*` タグを push（★ CI が Release 成果物を作る唯一の経路）
      ↓
(5) ★ そのタグを **G1 の「最初の配布」のタグ**として記録（ADR-034 Migration 3 / 判断 2）
      ↓
(6) 配布スクリプトは `--tag <そのタグ>` で回す
      ⚠️ 既定値は古い（make-distribution.sh = v0.1.23 / make-common-app-zip.sh = v0.1.24）
```

## 4. マージの前後で回す検証（★ `docs/verification-runbook.md` §1 のとおり・発明しない）

```bash
cd src-tauri
cargo test --workspace                                   # (a)
cargo run --bin gse-replay -- tests/fixtures/minimal.ndjson \
  --snapshot tests/snapshots/minimal.json                # (b) 背骨（byte-equal）
cargo run --bin emit_schema                              # (c) 出力を schema/current.json と byte-equal 比較
cd .. && npx tsc --noEmit                                # (d)
cd src-tauri && cargo fmt --check
cargo clippy --all-targets --features package -- -D warnings   # (e) CI は -D warnings の門を持つ
```

★ 加えて本タスクで触ったゲート 3 本:

```bash
bash scripts/check-shell-portability.sh                       # 期待 rc=0
bash scripts/check-o1-release-readiness.sh                    # ⚠️ 期待 rc=1（残り 2 件は正しい赤）
bash scripts/check-o1-release-readiness.sh --selftest         # 期待 rc=0（空回り検出）
cd experiments/20260801-controlled-friction-task && bash run.sh   # 期待 rc=0
```

⚠️★★ **手元の緑は CI の代替にならない**（macOS 側は `hook_windows.rs` を 1 行も
コンパイルしない・`--features package` の有無も残る）。★ マージ後に CI の
`check` (windows / macOS) と `frontend-check` が緑になることを**必ず確かめる**。

## 5. ⚠️ 注意（★ 踏みやすい順）

1. ⚠️★★★ **タグを動かすと G1 の配布の固定に触れる**（ADR-034 D3）。
   ★ 判断 2 で「最初の配布 = リブート後の次の配布」と決めたので、**まだ固定は始まっていない**。
   → ★ いま新しいタグを打つのは D3 違反ではない。⚠️ ただし **(5) で記録した後は固定が始まる**。
2. ⚠️ **schema drift はこのブランチが生んだもの**（main には `activity_label` が無い）。
   → マージすると gse-dataset 側との parity が「一致」から「drift」へ変わる。★ (3) を飛ばさない。
3. ⚠️ `.codex/budget.json` がブランチ側で変更されている。★ **`git checkout --` で戻さない**
   （記帳が消えると復元できない）。
4. ⚠️ `.worktrees/` と `tmp/` は未追跡のまま。★ `git add -A` / `git add <dir>` を使わない
   （作業ツリーに常に別ブランチの未コミット作業がある）。
5. ⚠️ ブランチ側の `.github/workflows/ci.yml` の差分は **+24/-0 の追記のみ**で
   `build-*` / `release` ジョブは無変更 —— ★ 衝突しないが、**CI の挙動は変わる**
   （`loop-worktree-deny-test.sh` が check / frontend-check で回る）。

## 6. ⚠️ 未確認（★ 実行前に確かめる）

- main 側 2 コミットが触った `.steering/20260911-outcome-arbitration-and-o1-preflight/` の
  **記述内容**が本ブランチの記述と矛盾しないか（★ ファイルパスの交差は 0 なので git は無衝突）。
- `scripts/check-o1-release-readiness.sh` / `loop-run.sh` / `loop-spawn.sh` が main 比で
  新規か変更か（★ 本計画の結論は変わらないが、レビュー時の読み方が変わる）。
