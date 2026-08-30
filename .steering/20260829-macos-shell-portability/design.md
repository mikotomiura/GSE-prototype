# 設計

## 実装アプローチ

★ **3 件とも「意味を変えずに書き方だけ直す」**。⚠️ ロジック・exit code の契約・
検査の厳しさは 1 ミリも変えない（★ 変えると「直したから緑になった」のか
「緩めたから緑になった」のか区別できなくなる）。

### (1)(2) `$var` ＋ 多バイト文字 → `${var}`

```diff
- echo "… 同期しません（$why）" >&2
+ echo "… 同期しません（${why}）" >&2
```

★ **なぜ `${}` で直るのか**: bash は `${` を見た時点で閉じ `}` まで変数名として読むので、
⚠️ **後続バイトの解釈に依存しない**。★ bash 3.2 / 5.x / git-bash / zsh すべてで同じ結果になる。

⚠️★ **代替案（採らない）**: 全角を半角に置換する / `set -u` を外す。
★ 前者は**被験者と研究者が読むメッセージの文面を変える**（日本語の体裁が崩れる）、
後者は**未定義変数を黙って空にする**（★ 本プロジェクトが最も避けている silent failure）。

★ 対象は **リポジトリ全体で 17 箇所**（走査結果は `decisions.md` に貼る）。
⚠️ コメント行の 1 箇所も直す（★ そこだけ生の `$DRIVE（` が残ると、
「直っていない実例」と「直った規約」が同じファイルに同居して読み手が誤る）。

### (3) `bom_crlf_ok` の BOM 検査

```diff
- head -c 3 "$1" 2>/dev/null | od -An -tx1 | grep -q 'ef bb bf' || return 1
+ [ "$(head -c 3 "$1" 2>/dev/null | LC_ALL=C od -An -tx1 | LC_ALL=C tr -d '[:space:]')" = "efbbbf" ] || return 1
```

★ **空白を全部落としてから 1 つの文字列と比べる**ので、⚠️ **区切り幅の違い（BSD=2 / GNU=1）に
依存しない**。★ `grep -q` の部分一致もやめて **完全一致**にする
（⚠️ 部分一致だと「先頭 3 バイト以外に ef bb bf が現れた」ときに誤って通る余地が残る）。

⚠️ CR/LF の計数（`tr -cd '\r'`）は**触らない**。★ macOS で実測して既に正しく動いている
（`cr=109 lf=109` / `cr=62 lf=62`）。

### (4) ★ 再発を止める検査（新規）

⚠️★ **1 箇所ずつ直すだけでは同じ罠をまた踏む**（★ 実際 `prepare-subjects.sh:234` に
実測コメントが残っていたのに 17 箇所生きていた）。→ **リポジトリ全体を走査する検査**を置く。

`scripts/check-shell-portability.sh`:

| 検査 | 何を見るか |
|---|---|
| A | `git ls-files` のシェルスクリプト全部で `$name` の直後が非 ASCII の箇所が **0 件** |
| B | ⚠️★ **陽性対照**: わざと `$v）` を書いた一時ファイルを走査対象に混ぜて **必ず捕まる** |
| C | ⚠️★ **陰性対照**: `${v}）` と書いた一時ファイルは **捕まらない**（★ 直し方が有効である証拠） |

★ B/C が無いと「該当 0 件」が **走査そのものが空振りしている**のと区別できない
（memory `silent-failure-in-guard-scripts` / `measurement-instrument-false-positives`）。

★ 対象ファイルの拾い方は **拡張子だけに頼らない**（⚠️ `.command` や shebang のみのファイルを
取りこぼす）。→ `.sh` / `.bash` / `.command` ＋ **shebang に bash/sh を持つ追跡ファイル**。

## 変更対象

### 修正するファイル
- `scripts/sync-session.sh` — ★ **161 行の `$why）` → `${why}`（本番コードの欠陥）**
- `scripts/sync_session_o1_guard_test.sh` — 6 箇所の `$rc）` → `${rc}`
- `scripts/check-o1-release-readiness.sh` — 2 箇所 ＋ 新検査の呼び出しを追加
- `experiments/20260801-controlled-friction-task/make-common-app-zip.sh` — 4 箇所 ＋ BOM 検査
- `experiments/20260801-controlled-friction-task/prepare-subjects.sh` — 2 箇所（1 つはコメント）
- `experiments/20260801-controlled-friction-task/run.sh` — 1 箇所

### 新規作成するファイル
- `scripts/check-shell-portability.sh` — ★ 走査 ＋ 陽性/陰性対照

### 削除するファイル
- なし

## 影響範囲

| 何 | 影響 | ★ 対処 |
|---|---|---|
| `sync-session.sh` の exit code | ⚠️ **1 → 4 に変わる**（★ これが本来の契約） | ★ 呼び出し側 `sync-all.sh` / `.ps1` が 4 をどう扱うか確認する |
| `sync-session.ps1`（Windows） | ★ **触らない**（⚠️ PowerShell に同じ罠は無い） | ★ 2 実装の規則が揃っているかは既存テストが見る |
| G1 の配布経路 | ⚠️ `make-common-app-zip.sh` を触る | ★ **既定 `--mode g1` の挙動を変えない**。BOM 検査は G1 launcher にも同じく効く |
| Windows / git-bash | ★ `${}` はどの bash でも同じ | ⚠️ **CI（Windows）で赤が出ないこと**を確認する |

## 既存パターンとの整合性

- ★ ゲートは「**通過 N 件 / 未達 M 件**」を出して非 0 で落ちる形（`check-o1-release-readiness.sh`）
- ★ 検査には**必ず陽性対照を添える**（`make-common-app-zip.sh` 8d の既存パターンに倣う）
- ★ `set -euo pipefail` を維持する

## テスト戦略

- ⚠️★ **単体テスト（Rust）は 1 行も関係しない**（★ 変更はすべてシェル）
- ★ 実測で確かめる:
  1. `bash scripts/sync_session_o1_guard_test.sh` が**最後まで走る** → 6 ケース緑
  2. `bash scripts/sync-session.sh <o1 な NDJSON> --no-commit; echo $?` → **4**
  3. ★ **通常セッション**では 4 以外（⚠️ 「全部弾く実装」になっていないことの陽性対照）
  4. `make-common-app-zip.sh --selftest` → 17/17
  5. `check-shell-portability.sh` → 0 件、⚠️ **壊した複製では赤**
  6. `check-o1-release-readiness.sh` → 未達は「送信 timeout 未実測」1 件だけ
- ★ ⚠️ **`$?` の取り方に注意**（memory: `script | tail -2; echo $?` は tail の rc を見る）

## ロールバック計画

★ 変更は 1 ブランチ `fix/macos-shell-portability` に閉じており、
⚠️ 生成物（zip / dist）は**コミットしない**。→ `git checkout main` で完全に戻る。
★ 検算ランの成果物は `dist/_common/O1_実施用_*` と `/tmp/o1-dryrun-submit.json` で、
**両方セッション終了時に消す**。
