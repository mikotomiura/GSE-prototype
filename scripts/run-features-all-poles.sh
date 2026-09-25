#!/usr/bin/env bash
# ★ `gse-replay --features` を **3 極すべて**で回し、極ごとに 1 ファイルを出す（issue 008・判断 3 のトレードオフ）。
#
# ⚠️★★★ なぜ要るか:
#   判断 3 は極を「別モード（`--pole`・1 実行 1 極）」で出すと裁定した
#   （★ 出力の形が不変・極が enum なので Cartesian を構造的に作れない）。
#   ⚠️ その代償が「**3 極のどれかを回し忘れる**」ことである。→ 本スクリプトが 3 極を**必ず**回す。
#
# ★ 出す組は 3 つだけ:
#     baseline        = 極 A・M−（現行の計算そのもの）
#     pointer_b       = 極 B・M−（ポインタ活動区間を抑制）
#     modifier_m_plus = 極 A・M+（修飾キー押下区間の文字キーを産出に数えない）
#   ⚠️ **極を Cartesian に組まない**（ADR-030 D3 の囲み「他の極と Cartesian に組まない。独立に報告する」）。
#   ★ 3 ファイルは互いに**独立の報告**であり、突き合わせるのは読む側である
#     （⚠️ 極 B が baseline の部分集合になるとは限らない・判断 25。G2 の上下界は極ごとの min / max で取る）。
#
# ⚠️ fail-closed:
#   - 1 極でも失敗（gse-replay が非 0 / 出力が JSON でない / `config.pole` がファイル名と食い違う）したら
#     **全体が非 0 で止まり、outdir には 1 ファイルも置かない**（★ 3 ファイルが揃わない outdir を作らない）。
#   - ⚠️★★★ `pole_applicable == false` は**失敗ではない**（★ 「その極は判定できない」という正しい報告。
#     ポインタ宣言の無い入力の pointer_b、修飾キー行の無い入力の modifier_m_plus）。
#     exit 0 のまま 3 ファイルを出す（★ 適用外を失敗に読むと、修飾キーの無いセッションが全部落ちる）。
#   - ⚠️★★★ **outdir の使い回しでは fail-closed が破れる**（code-reviewer MEDIUM・2026-09-25）:
#     前回の 3 ファイルが残る outdir で今回が失敗すると古い 3 ファイルが残り「3 極そろった」と誤読される。
#     成功時も黙って上書きされる。→ **`baseline.json` / `pointer_b.json` / `modifier_m_plus.json` の
#     いずれかが既にあれば exit 2 で拒否する**（上書きしたければ空の outdir を指定する）。
#   - ⚠️★★★ **outdir が git 管理下でも拒否する**（security LOW・2026-09-25）: 共有禁止の特徴行
#     （封筒 `sharing: prohibited`）を repo 内に書くと誤って stage されうる。GSE repo の中・
#     gse-dataset のクローンの中の両方を弾く（`git -C <outdir> rev-parse --is-inside-work-tree`）。
#
# Usage:
#   bash scripts/run-features-all-poles.sh <session.ndjson> <outdir>
#   GSE_REPLAY_BIN=src-tauri/target/release/gse-replay bash scripts/run-features-all-poles.sh <in> <outdir>
#     ★ `GSE_REPLAY_BIN` を与えると `cargo run`（debug）の代わりにそのバイナリを使う（長いセッションを release で回す用）。
#     ⚠️ 相対パスは**呼び出し元の cwd** から解決する。
#
# Exit: 0 = 3 ファイルとも出した / 1 = ⚠️ 失敗（★ 何も出していない） /
#       2 = 引数が違う、または outdir がガード条件に違反
#         （★ baseline.json / pointer_b.json / modifier_m_plus.json のいずれかが既にある ＝ 使い回し拒否・
#            outdir が git 管理下 ＝ 共有禁止の特徴行を誤って stage するのを防ぐため拒否）
#
# ⚠️ 出力（特徴行・封筒）は**中間成果物**であり `gse-dataset` へ共有しない
#   （★ `scripts/check_no_feature_output.sh`・`docs/glossary.md`「特徴行」）。outdir は repo の外に置く。
#
# 関連: docs/verification-runbook.md ／ .steering/20260921-p1-prereg-cli-poles/decisions.md 判断 3
set -uo pipefail

POLES=(baseline pointer_b modifier_m_plus)

die() { echo "[all-poles] NG: $*" >&2; exit 1; }
# ★ 引数不正 / outdir ガード違反は exit 1 (die) ではなく exit 2 で区別する（ヘッダの Exit 契約参照）。
reject() { echo "[all-poles] NG: $*" >&2; exit 2; }

if [ "$#" -ne 2 ]; then
  echo "usage: bash scripts/run-features-all-poles.sh <session.ndjson> <outdir>" >&2
  exit 2
fi
IN="$1"
OUT="$2"
[ -n "$IN" ] || { echo "[all-poles] ⚠️ 入力が空文字（★ 変数が未設定のまま展開されていないか）" >&2; exit 2; }
[ -n "$OUT" ] || { echo "[all-poles] ⚠️ outdir が空文字（★ 変数が未設定のまま展開されていないか）" >&2; exit 2; }

[ -f "$IN" ] || die "入力が無い: $IN"
command -v jq >/dev/null 2>&1 || die "jq が無い（★ config.pole の照合に使う）"
command -v git >/dev/null 2>&1 || die "git が無い（★ outdir が git 管理下かの判定に使う）"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
# ★ `cargo run` は src-tauri へ cd して回すので、入力は絶対パスにしておく。
IN_ABS="$(cd "$(dirname "$IN")" && pwd)/$(basename "$IN")"

# ⚠️★★★ 出力先の使い回し拒否: 3 ファイルのいずれかが既にあれば、mkdir/staging に進む前に止める
#   （★ mkdir -p はまだしていないので、outdir がそもそも無ければこの検査は素通りする）。
for pole in "${POLES[@]}"; do
  [ -e "$OUT/$pole.json" ] \
    && reject "$OUT/$pole.json が既に存在する（★ 上書き/使い回しを避けるため、3 ファイルとも無い outdir を指定すること）"
done

OUT_PRE_EXISTED=1
[ -d "$OUT" ] || OUT_PRE_EXISTED=0
mkdir -p "$OUT" || die "outdir を作れない: $OUT"

# ⚠️★★★ outdir が git 管理下なら拒否する（★ 共有禁止の特徴行を repo 内に書いて誤って stage するのを防ぐ）。
#   ⚠️ 判定は outdir を作った**後**。拒否するときは自分が作った空ディレクトリだけ消す（既存ディレクトリは消さない）。
if git -C "$OUT" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  [ "$OUT_PRE_EXISTED" -eq 0 ] && rmdir "$OUT" 2>/dev/null
  reject "outdir が git 管理下: ${OUT}（★ 特徴行は共有禁止 (sharing: prohibited)。outdir は repo の外に置く）"
fi

# ⚠️ 3 極が全部成功するまで outdir に 1 ファイルも置かない（staging）。
#   ★ 途中で止まったとき、1〜2 ファイルだけが残ると「3 極を回した」と読まれうる。
STAGE="$(mktemp -d "$OUT/.all-poles.XXXXXX")" || die "staging ディレクトリを作れない: $OUT"
trap 'rm -rf "$STAGE"' EXIT

run_replay() { # run_replay <極> <出力ファイル>
  if [ -n "${GSE_REPLAY_BIN:-}" ]; then
    "$GSE_REPLAY_BIN" "$IN" --features --pole "$1" > "$2"
  else
    ( cd "$REPO_ROOT/src-tauri" && cargo run --quiet --bin gse-replay -- "$IN_ABS" --features --pole "$1" ) > "$2"
  fi
}

for pole in "${POLES[@]}"; do
  f="$STAGE/$pole.json"
  run_replay "$pole" "$f" \
    || die "極 $pole の gse-replay --features が非 0 で終了した（★ 3 極のどれかを欠いたまま先へ進めない）"
  # ⚠️ 出力が JSON として読めない・極が食い違うものは出さない（★ ファイル名と中身の極が違うと読み手が誤る）。
  #   ★ 文字列一致だけでなく `jq -e` の終了コードも見る（先頭だけ正しい JSON で後ろが壊れた出力を
  #     素通りさせない。jq はストリームとして読むので、末尾に trailing garbage があれば非 0 で終わる）。
  if ! got="$(jq -e -r '.config.pole' "$f" 2>/dev/null)"; then
    die "極 $pole の出力から config.pole を取り出せない（jq -e が非 0。★ 出力が JSON でない、または途中から壊れている）"
  fi
  [ "$got" = "$pole" ] \
    || die "極 $pole の出力の config.pole が '${got:-<読めない>}'（★ ファイル名と極が食い違う出力は出さない）"
  applicable="$(jq -r '.config.pole_applicable' "$f" 2>/dev/null)"
  if [ "$applicable" = "false" ]; then
    reason="$(jq -r '.config.pole_not_applicable_reason // "?"' "$f" 2>/dev/null)"
    echo "[all-poles] note: 極 ${pole} は pole_applicable=false（理由: ${reason}）。★ 失敗ではなく正しい報告" >&2
  fi
done

# ★ ここまで来たら 3 極とも揃っている。まとめて outdir へ移す。
# ⚠️ 部分的な mv の失敗（LOW）: 2 本目以降が失敗したら、既に移した分を rm -f してから die する
#   （all-or-nothing。★ 1〜2 ファイルだけが outdir に残って「3 極そろった」と誤読されるのを防ぐ）。
MOVED=()
for pole in "${POLES[@]}"; do
  if ! mv -f "$STAGE/$pole.json" "$OUT/$pole.json"; then
    for done_pole in "${MOVED[@]}"; do
      rm -f "$OUT/$done_pole.json"
    done
    die "極 $pole の出力を outdir へ移せない（⚠️ 3 ファイルが揃っていない可能性）: $OUT"
  fi
  MOVED+=("$pole")
done

echo "[all-poles] OK: ${POLES[*]} → $OUT"
