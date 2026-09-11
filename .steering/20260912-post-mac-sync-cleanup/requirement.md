# mac 同期後の後片付け (clippy / ブランチ / dataset 未追跡)

## 背景

2026-09-12 に mac 側の成果 (PR #185 / #186 / #187) を Windows 機へ同期した
(`main`: `5e5eccc` → `0d4cafb`)。同期そのものは成功し、回帰は緑だった
(653 tests pass / ゴールデン 6 fixture 226 snapshot 一致 / schema byte-equal)。

一方で **同期の検証中に、mac 側変更とは無関係な既存の汚れが 3 種類** 見つかった。

1. ⚠️ `cargo clippy -- -D warnings` が **29 error** で落ちる。
   ★ 一次確認の結果 **mac 側変更が原因ではない**:
   - `git diff 5e5eccc..0d4cafb` に `is_ime_active_check` は一度も現れない
     (最後に触ったのは `5e3c85c`)。
   - mac が触った唯一のエラー箇所 `hook_windows.rs` の `classify_ime_nav_key` は
     同期前 `5e5eccc` と **1 文字も違わない** (遷移表削除で行番号が 188→146 にずれただけ)。
   - 残り 28 件は mac 差分が触っていないファイル。
   ★ 本機 toolchain は `rustc/clippy 1.94.1` で、`rust-toolchain.toml` による固定は無い。
   ⚠️ **CI は clippy を実行していない** (`ci.yml` に記述なし) ので、赤を出しているのは
   `.claude/hooks/stop-check.sh` だけ。→ `.rs` を触るたび `[stop] WARN` が出続ける。
2. ★ main にマージ済みのローカルブランチが **26 本** 残っている
   (うち `docs/post-merge-records` はリモートが削除済み)。
3. ★ `C:\gse-dataset` に未追跡の `metrics/P000/macos/*.metrics.json` が **13 本**
   (2026-04-15〜17)。⚠️ `hmm_version` / `app_version` を持たない**旧形式**で、
   追跡済みの同ディレクトリのファイルが持つ `.range_metrics.json` の対も無い。

## ゴール

上記 3 件を消し、`.rs` を触るたびに出ていた恒常的な警告を無くす。
⚠️ **振る舞いは 1 ビットも変えない** (lint 是正と死蔵コード削除のみ)。

## スコープ

### 含むもの
- `cargo clippy -- -D warnings` が **exit 0** になるまでの是正 (8 ファイル / 29 件)
- 死蔵関数 `is_ime_active_check` の削除
- main にマージ済みのローカルブランチ 26 本の削除 (★ **ローカルのみ**)
- `C:\gse-dataset` の未追跡 metrics 13 本の削除

### 含まないもの
- ⚠️ **リモートブランチの削除** (origin 側には一切触れない)
- ⚠️ **`rust-toolchain.toml` の新設** (両 OS / CI に波及する別判断)
- ⚠️ 未マージの 2 ブランチ
  (`docs/expression-transform-theory` / `feat/resumption-outcome-arbitration`) の処理
- ⚠️ mac 側で意図的に残した **起票 6** (ライブ変換 ON の `abandon` 過大) の修正
  — ★ 設計上の争点があり idea 議論の入力として残す判断 (判断 12)
- ⚠️ `--all-targets` (テスト・ベンチ) の clippy — ★ hook の gate は lib/bin のみ

## 受け入れ条件

- [ ] `cd src-tauri && cargo clippy --quiet -- -D warnings` が **exit 0**
- [ ] `cd src-tauri && cargo test --workspace` が **653 passed / 0 failed** を維持
- [ ] ゴールデン 6 fixture がすべて一致 (`gse-replay --snapshot`)
- [ ] `cargo run --bin emit_schema` が `schema/current.json` と byte-equal
- [ ] `git branch --merged main` の残りが `main` と未マージ 2 本のみ
- [ ] `cd /c/gse-dataset && git status --porcelain` が空

## 関連ドキュメント

- `docs/development-guidelines.md` §1 (規約) / §3 (テスト方針)
- `.claude/hooks/stop-check.sh` (clippy gate の実体)
- `docs/experiment-tracking.md` (metrics の版固定)
- `.steering/20260911-outcome-arbitration-and-o1-preflight/decisions.md` 判断 12

## 運用メモ
- /reimagine 適用: **No**
- 理由: 設計判断を伴わない。lint 是正・死蔵コード削除・ファイル削除のみで、
  実装案が複数あるわけではない。⚠️ 振る舞いを変えないことはゴールデン回帰が機械で守る。
