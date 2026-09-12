#!/bin/bash
# Stop hook (Report 層) - セッション終了時の静的解析
# 問題があった時のみ [stop] WARN を 1 行出す。詳細はユーザーが手動で実行する前提。

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
MANIFEST="${REPO_ROOT}/src-tauri/Cargo.toml"

# 変更ファイルが無ければスキップ
CHANGED=$(git diff --name-only HEAD 2>/dev/null | wc -l | tr -d ' ')
if [ "$CHANGED" -eq 0 ]; then
    exit 0
fi

# Rust: cargo clippy (変更された .rs ファイルがある場合のみ)
#
# ⚠️★★★ --all-targets を付けること (2026-09-12)。
#   ★ 既定のターゲット (lib + bin) だけだと **#[cfg(test)] のコードが一切解析されない**。
#   ⚠️ しかも clippy は lib が落ちた時点で止まるので、lib を緑にするまで bin の指摘も見えない。
#     → 実際にこの穴で 1.94 の lint が 33 + 12 件たまり、片付けるまで存在に気づけなかった。
#
# ⚠️★★★ --features package を付けること (F-3・2026-09-12)。
#   ★ CI の clippy は `ci.yml` の **1 箇所だけ**で、`--all-targets --features package` である。
#   ⚠️ default features だけで回すと **CI の真部分集合**しか見ないので、
#     `packaging.rs` / `reconcile.rs` / `gse-package` / `gse-unpack` / `gse-submit`
#     (= 提出経路) が **ローカルで 1 度も lint されない**。
#   ★ `cfg(not(feature = "package"))` は repo 全体で 0 件 (PR #199 で実測) なので、
#     default ⊂ package。→ ⚠️ **2 本走らせる必要は無く、置き換えで両方を覆う。**
#   ★ 実測コスト (mac・1 ファイル編集後): 4–5 秒 → 6 秒 = **+1〜2 秒**。
#
# ⚠️★★★ 出力を捨てない (F-3 の本丸)。
#   ★ 旧版は `>/dev/null 2>&1` で中身を捨て「issues があります」とだけ言っていた。
#   ⚠️ それでは **何が悪いか分からず、WARN が読み飛ばされる**。
#     → ★ 先頭の指摘と件数を出し、**そのまま打てる再現コマンド**を添える
#       (⚠️ 旧文言は `--features package` が抜けており、打っても同じ結果にならなかった)。
if git diff --name-only HEAD 2>/dev/null | grep -q '\.rs$'; then
    if [ -f "$MANIFEST" ]; then
        CLIPPY_LOG=$(mktemp -t gse-stop-clippy)
        if ! cargo clippy --manifest-path "$MANIFEST" --quiet --all-targets \
            --features package -- -D warnings >"$CLIPPY_LOG" 2>&1; then
            # ★ clippy は指摘 1 件につき `error: ...` 行を 1 本出す。
            # ⚠️ ただし末尾の `error: could not compile ...` は**集計行**なので数えない
            #   (★ 数えると 1 件の指摘が 2 件に見える。実際に陽性対照で 1 件が 4 と出た)。
            # ⚠️ なお `--all-targets` では lib と lib-test が別ユニットなので、
            #   ★ **同じ指摘が複数回出ることがある** (= 件数は「指摘の延べ数」である)。
            COUNT=$(grep -c '^error: ' "$CLIPPY_LOG" 2>/dev/null || echo 0)
            AGG=$(grep -c '^error: could not compile' "$CLIPPY_LOG" 2>/dev/null || echo 0)
            COUNT=$((COUNT - AGG))
            echo "[stop] WARN: cargo clippy reported ${COUNT} 件 (延べ) の指摘 (--all-targets --features package):"
            # ⚠️ 出しすぎない (★ Stop hook の出力なので先頭だけ)。
            sed -n '1,15p' "$CLIPPY_LOG" | sed 's/^/[stop]   /'
            if [ "$COUNT" -gt 1 ]; then
                echo "[stop]   ... (先頭のみ表示)"
            fi
            echo "[stop]   再現: cd src-tauri && cargo clippy --all-targets --features package -- -D warnings"
        fi
        rm -f "$CLIPPY_LOG"
    fi
fi

# TypeScript: tsc --noEmit (変更された .ts/.tsx ファイルがある場合のみ)
if git diff --name-only HEAD 2>/dev/null | grep -qE '\.(ts|tsx)$'; then
    if [ -f "${REPO_ROOT}/tsconfig.json" ] && command -v npx >/dev/null 2>&1; then
        if ! (cd "$REPO_ROOT" && npx --no-install tsc --noEmit >/dev/null 2>&1); then
            echo "[stop] WARN: tsc reported type errors. Run 'npx tsc --noEmit' to inspect."
        fi
    fi
fi

exit 0
