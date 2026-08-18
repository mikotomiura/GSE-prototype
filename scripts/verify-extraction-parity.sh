#!/usr/bin/env bash
# verify-extraction-parity.sh — 挙動不変リファクタの全 fixture 差分検証
#
# ADR-006 Phase 2a (Writing head 抽出) の acceptance を、ゴールデン 4 本より広い範囲で担保する。
# ゴールデン snapshot は 4 本しかないが fixtures は 10 本あるため、
# 「ゴールデンで覆われていない経路で挙動が変わっていないこと」をここで確かめる。
#
# 使い方:
#   bash scripts/verify-extraction-parity.sh [<base-ref>]
#     <base-ref> … 比較対象の git ref (既定: main)
#
# 仕組み:
#   1. <base-ref> の worktree を切って gse-replay をビルド (= 変更前)
#   2. 現在の作業ツリーで gse-replay をビルド (= 変更後)
#   3. 全 fixture を既定モード (snapshot 出力) で両方に流し、stdout を byte 比較
#   4. 1 バイトでも差があれば exit 1
#
# ⚠️ **このスクリプトは fail-closed である。**
#   「両方とも失敗したから一致とみなす」という扱いはしない。検証できなかった fixture が
#   1 本でもあれば FAIL にする。acceptance を証明するゲートが沈黙して通ると、
#   HMM 挙動の変化を見逃すため (security-checker H-1)。
#
# ⚠️ **2a 専用のツールである。**
#   2b (task_kind → head 配線) では `calib_subject_*` の 3 本が `task_kind=vibe_coding` を
#   持つため出力が変わるのが**正しい**。2b では使わない。
#
# ⚠️ `<base-ref>` に渡した ref は `cargo build` される = build.rs / proc-macro が実行される。
#   信頼できない ref (fork の PR ref 等) を渡さないこと。CI の untrusted job に配線しない。
#
# ⚠️ fixture は **current 側のもの**を base バイナリにも食わせる。
#   コード差分だけの parity を見る道具なので、同じ差分で fixture を追加・変更した場合は
#   base が知らない入力形式で落ちて偽 FAIL になる。その場合はスクリプトの結果でなく
#   ゴールデンと単体テストで判断すること (下でも検出して警告する)。
#
# 注意:
#   - Cargo.toml は repo 直下に無く src-tauri/ にある

# ⚠️ `docs/development-guidelines.md` §10 の規約どおり `set -euo pipefail` を使う。
#   exit code は同 guidelines が文書化している `|| rc=$?` イディオムで取るので、
#   `-e` を外す必要はない (`-e` を外すと mkdir / find の失敗まで素通りする)。
set -euo pipefail

BASE_REF="${1:-main}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# ⚠️ `-` 始まりの引数を git の parse-options に食わせない。
#   `git worktree add --detach <path> --force` は commit-ish 未指定 = HEAD で成功してしまい、
#   base と current が同一コミットになって byte-equal が自明に成立する (偽 PASS)。
if ! git -C "$REPO_ROOT" rev-parse --verify --quiet "${BASE_REF}^{commit}" >/dev/null; then
    echo "FAIL: not a commit: $BASE_REF" >&2
    exit 1
fi

# ⚠️ `set -u` は空文字を捕捉しないので、mktemp の失敗を明示的に検査する。
#   捕まえないと WORK_DIR="" になり、BASE_TREE が /base に化けて worktree を想定外の場所に作る。
WORK_DIR="$(mktemp -d)"
if [ -z "${WORK_DIR:-}" ] || [ ! -d "$WORK_DIR" ]; then
    echo "FAIL: mktemp -d failed" >&2
    exit 1
fi

BASE_TREE="$WORK_DIR/base"
OUT_DIR="$WORK_DIR/out"

cleanup() {
    git -C "$REPO_ROOT" worktree remove --force "$BASE_TREE" >/dev/null 2>&1 || true
    rm -rf "$WORK_DIR"
    # ⚠️ Windows では target/ のファイルロックで worktree remove が失敗しやすい。
    #   ディレクトリだけ消えると .git/worktrees/ に孤児メタデータが溜まり
    #   `git worktree list` が汚れ続けるので prune しておく。
    git -C "$REPO_ROOT" worktree prune >/dev/null 2>&1 || true
}
trap cleanup EXIT

mkdir -p "$OUT_DIR"

echo "== base ref: $BASE_REF =="
if ! git -C "$REPO_ROOT" worktree add --detach "$BASE_TREE" -- "$BASE_REF" >/dev/null; then
    echo "FAIL: could not create worktree for $BASE_REF" >&2
    exit 1
fi

# ⚠️ base とは **別の target dir** を明示する。
#   CARGO_TARGET_DIR が環境に設定されていると base と current が同じ出力先を奪い合い、
#   後から建てた方のバイナリを 2 回比較して byte-equal が自明に成立する (偽 PASS)。
#   current 側は既存のキャッシュを使いたいので、環境設定があればそれを尊重する。
BASE_TARGET_DIR="$WORK_DIR/target-base"
CURR_TARGET_DIR="${CARGO_TARGET_DIR:-$REPO_ROOT/src-tauri/target}"

if [ "$BASE_TARGET_DIR" = "$CURR_TARGET_DIR" ]; then
    echo "FAIL: base と current の target dir が同一 ($BASE_TARGET_DIR)" >&2
    exit 1
fi

echo "== building base gse-replay =="
if ! (cd "$BASE_TREE/src-tauri" && CARGO_TARGET_DIR="$BASE_TARGET_DIR" cargo build --quiet --bin gse-replay); then
    echo "FAIL: base build failed" >&2
    exit 1
fi

echo "== building current gse-replay =="
if ! (cd "$REPO_ROOT/src-tauri" && CARGO_TARGET_DIR="$CURR_TARGET_DIR" cargo build --quiet --bin gse-replay); then
    echo "FAIL: current build failed" >&2
    exit 1
fi

# バイナリの解決。⚠️ 見つからないまま実行すると rc=127 が両側に出るので、ここで落とす。
resolve_bin() {
    local base="$1"
    if [ -x "$base" ]; then
        printf '%s' "$base"
    elif [ -x "${base}.exe" ]; then
        printf '%s' "${base}.exe"
    else
        printf ''
    fi
}

BASE_BIN="$(resolve_bin "$BASE_TARGET_DIR/debug/gse-replay")"
CURR_BIN="$(resolve_bin "$CURR_TARGET_DIR/debug/gse-replay")"

if [ -z "$BASE_BIN" ]; then
    echo "FAIL: base binary not found under $BASE_TARGET_DIR/debug/" >&2
    exit 1
fi
if [ -z "$CURR_BIN" ]; then
    echo "FAIL: current binary not found under $CURR_TARGET_DIR/debug/" >&2
    exit 1
fi
if [ "$BASE_BIN" = "$CURR_BIN" ]; then
    echo "FAIL: base と current が同一バイナリを指している ($BASE_BIN)" >&2
    exit 1
fi

# ⚠️ fixture が差分に含まれていると base バイナリに未知の入力を食わせることになる。
if ! git -C "$REPO_ROOT" diff --quiet "$BASE_REF" -- "src-tauri/tests/fixtures"; then
    echo "WARN: $BASE_REF との差分に tests/fixtures が含まれる。" >&2
    echo "      base バイナリが知らない入力形式で偽 FAIL になり得るので結果を鵜呑みにしないこと。" >&2
fi

total=0
mismatch=0

# ⚠️ 未クォート展開 (`for fx in $fixtures`) は word splitting と glob 展開の両方を受け、
#   スペースを含むパス (例 C:\Users\John Do\...) に clone された環境で壊れる。
#   -print0 / read -d '' で分割を殺す。
while IFS= read -r -d '' fx; do
    name="$(basename "$fx" .ndjson)"
    total=$((total + 1))

    base_rc=0
    "$BASE_BIN" "$fx" >"$OUT_DIR/$name.base" 2>"$OUT_DIR/$name.base.err" || base_rc=$?
    curr_rc=0
    "$CURR_BIN" "$fx" >"$OUT_DIR/$name.curr" 2>"$OUT_DIR/$name.curr.err" || curr_rc=$?

    if [ "$base_rc" -ne 0 ] || [ "$curr_rc" -ne 0 ]; then
        echo "FAIL  $name — replay exited non-zero (base=$base_rc / current=$curr_rc)"
        head -5 "$OUT_DIR/$name.curr.err" >&2
        mismatch=$((mismatch + 1))
        continue
    fi

    if cmp -s "$OUT_DIR/$name.base" "$OUT_DIR/$name.curr"; then
        echo "OK    $name"
    else
        echo "FAIL  $name — snapshot output differs"
        diff "$OUT_DIR/$name.base" "$OUT_DIR/$name.curr" | head -20
        mismatch=$((mismatch + 1))
    fi
done < <(find "$REPO_ROOT/src-tauri/tests/fixtures" -maxdepth 1 -name '*.ndjson' -print0 | sort -z)

echo
echo "== fixtures: $total / mismatch: $mismatch =="

# ⚠️ fail-closed: 検証本数がゼロなら「差分が無かった」ではなく「検証していない」。
if [ "$total" -eq 0 ]; then
    echo "FAIL: no fixtures found under src-tauri/tests/fixtures/ — 何も検証していない" >&2
    exit 1
fi

if [ "$mismatch" -ne 0 ]; then
    echo "PARITY FAILED — 挙動不変リファクタの前提が壊れている" >&2
    exit 1
fi

echo "PARITY OK — 全 $total fixture で出力が byte-equal"
