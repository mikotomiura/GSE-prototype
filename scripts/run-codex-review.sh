#!/usr/bin/env bash
# scripts/run-codex-review.sh
# cross-reviewer エージェント / codex-review Skill から呼ばれる wrapper。
# 任意の codex exec コマンド実行を防ぐため、パラメータを固定化する。
# jq 非依存 (python 使用) — jq 未導入環境向けに python 化 (2026-06-16)。
#
# 使い方:
#   scripts/run-codex-review.sh > /tmp/cross-review-codex.md            # 未ステージ変更
#   scripts/run-codex-review.sh <base>..<head> -- path1 path2 > out.md  # 対象を明示
#   scripts/run-codex-review.sh --ack-filtered <base>..<head> -- path1  # ★ 下記参照
#
# 引数を渡すとそのまま `git diff "$@"` に流す。★ 引数なしの既定挙動 (未ステージ変更) は不変。
# ⚠️ 引数が無いと **コミット済みの変更はレビューされない** (git diff は未ステージのみ)。
# タスク完了後の /cross-review は差分がコミット済みなので、範囲を明示して呼ぶこと。
# 内部で git diff | scripts/secrets-filter.sh を通し、固定 prompt で Codex を呼ぶ。
#
# ★ --ack-filtered (2026-08-07 追加)
#   secrets-filter が exit 2 を返しても中止せず、警告を出して続行する **明示的な** 逃がし口。
#   既定は fail-closed のまま。⚠️ 自動では絶対に付けない。人が差分の該当行を目で見て
#   「実体のある機密は無い」と確認し、その根拠を .steering に残した時だけ付ける。
#   背景: secrets-filter は行内に `secret =` 等の**語**が出ただけで 2 を返すため、
#   `let secret = v` のような識別子や「SHARED_SECRET を .gs に書くな」という注意書きでも
#   ブロックされる。この誤検知で cross-review が連続で skip される事故が実際に起きている。
#   ⚠️ フィルタは通る (置換・hunk 除去は適用済み)。飛ばすのは「中止の判断」だけである。
#
# exit code:
#   0: Codex レビュー完了 (stdout に結果) / 引数なしで未ステージ変更が無い (skip)
#   1: 予算超過 / Codex エラー / python 不在 / ★ 明示した範囲の差分が空
#   2: secrets-filter が機密を検出 (fail-closed。--ack-filtered 指定時は 2 を返さない)

set -uo pipefail

ACK_FILTERED=0
if [ "${1:-}" = "--ack-filtered" ]; then
  ACK_FILTERED=1
  shift
fi

# ⚠️★★ 残りの引数は `<range> [-- <paths>]` **だけ**に絞る (security-checker 指摘)。
#   ★ `--` 以外のオプションを通すと `git diff --no-index <repo 外のパス>` が書け、
#   ⚠️ **追跡外・repo 外のファイルを Codex に送れてしまう**。
#   実測: `g1-submit.json` (endpoint + SHARED_SECRET) は .gitignore で通常の git diff には
#   出ないが、`--no-index` は index も ignore も無視するので到達する。
#   ★ このラッパの存在理由は「パラメータを固定すること」なので、入力範囲も固定側に含める。
#   ⚠️ ★ コメントと実装を一致させる: `--` の前は **range を高々 1 個**しか許さない
#   (「`-` で始まらなければ何個でも通る」だと、書いてある形より広い・cross-review 指摘)。
seen_ddash=0
ranges=0
for a in "$@"; do
  if [ "$a" = "--" ]; then
    seen_ddash=1
    continue
  fi
  [ "$seen_ddash" -eq 1 ] && continue
  if [ "${a#-}" != "$a" ]; then
    echo "[run-codex-review] FAILED: オプションは受け付けません: $a" >&2
    echo "[run-codex-review] 受け付ける形: <base>..<head> [-- <path> ...]" >&2
    exit 1
  fi
  ranges=$((ranges + 1))
  if [ "$ranges" -gt 1 ]; then
    echo "[run-codex-review] FAILED: range は 1 個までです ('--' の前に $a)" >&2
    echo "[run-codex-review] 受け付ける形: <base>..<head> [-- <path> ...]" >&2
    exit 1
  fi
done

PYTHON=$(command -v python3 || command -v python || true)
if [ -z "$PYTHON" ]; then
  echo "[run-codex-review] FAILED: python not found (予算管理/JSON パースに必須)" >&2
  exit 1
fi

# Windows git-bash の日本語ロケール (cp932) で Unicode エラーにならないよう UTF-8 を強制。
# ここで落ちると codex 課金後・budget 更新前に死に、消費が記録されない。
export PYTHONUTF8=1 PYTHONIOENCODING=utf-8

# budget.json は repo root 基準で参照する (cwd 依存だと予算チェックが不成立になる)
ROOT=$(git rev-parse --show-toplevel 2>/dev/null || echo .)
BUDGET_FILE="$ROOT/.codex/budget.json"
export BUDGET_FILE

TMPDIR_WORK=$(mktemp -d)
trap 'rm -rf "$TMPDIR_WORK"' EXIT

git diff "$@" > "$TMPDIR_WORK/raw.diff"
if [ ! -s "$TMPDIR_WORK/raw.diff" ]; then
  if [ "$#" -gt 0 ]; then
    # 範囲を明示して呼んだのに空 = 指定ミス。ここで exit 0 を返すと
    # 「rc=0 だから走った」と誤読される (silent failure)。明示的に落とす。
    echo "[run-codex-review] FAILED: 指定した差分が空です: git diff $*" >&2
    exit 1
  fi
  echo "[run-codex-review] no unstaged changes to review (skipped, no budget consumed)" >&2
  exit 0
fi

# 機密フィルタ (fail-closed)
# `if ! cmd; then rc=$?` は **常に 0** になる (`!` が反転した後のステータスを拾うため)。
# それだと secrets-filter の exit 2 (機密検出) と 1 (故障) を区別できず、
# 呼び出し側が「機密でブロック」と「codex 故障」を取り違える。
# cwd に依存すると `cd src-tauri` した状態から呼んだだけでフィルタが見つからず
# rc=127 (= "secrets-filter error") になる。repo root 基準で引く。
SECRETS_FILTER_REPORT="$TMPDIR_WORK/filter-report.txt" \
  "$ROOT/scripts/secrets-filter.sh" < "$TMPDIR_WORK/raw.diff" > "$TMPDIR_WORK/input.diff"
rc=$?
if [ "$rc" -ne 0 ]; then
  if [ "$rc" -eq 2 ]; then
    if [ "$ACK_FILTERED" -eq 1 ]; then
      echo "[run-codex-review] WARN: secrets-filter がヒットしたが --ack-filtered で続行する" >&2
      echo "[run-codex-review] WARN: 送信するのは**フィルタ後**の差分である" >&2
      # ⚠️★ **どの行がなぜマッチしたかを出す** (security-checker 指摘)。
      #   ★ 以前は「除去された hunk 行数」だけを出していたが、それは **安全な側**
      #   (中身が消えた部分) の件数であり、人が確かめるべき行内マッチが 1 件も見えなかった。
      #   ⚠️ 値そのものは出さない (端末とスクロールバックに秘密を残さない)。
      echo "[run-codex-review] WARN: 人が確認すべき箇所 (行番号と理由。値は出さない):" >&2
      sed 's/^/[run-codex-review]   raw.diff:/' "$TMPDIR_WORK/filter-report.txt" >&2
    else
      echo "[run-codex-review] BLOCKED: secrets-filter detected sensitive content" >&2
      echo "[run-codex-review] 誤検知だと人が確認できた場合のみ --ack-filtered を付けて再実行する" >&2
      exit 2
    fi
  else
    echo "[run-codex-review] FAILED: secrets-filter error rc=$rc" >&2
    exit 1
  fi
fi

# 予算チェック (python; jq 不要)
# budget.json が壊れていると BUDGET_INFO が空になり、`$((BUDGET - USED))` が
# 「算術エラー -> if 偽 -> そのまま codex を呼ぶ」で **fail-open** する。明示的に止める。
if ! BUDGET_INFO=$("$PYTHON" - "$BUDGET_FILE" 2>/dev/null <<'PY'
import json, sys, datetime


def need_int(v):
    """非整数 / bool / 負値 / 桁あふれを弾く。ここを緩めると値が bash の算術に渡り、
    `$((BUDGET - USED))` が構文エラー → set -e 無しで続行 → **素通り** になる。"""
    if isinstance(v, bool) or not isinstance(v, int) or v < 0 or v > 10**12:
        raise ValueError(f'invalid budget value: {v!r}')
    return v


d = json.load(open(sys.argv[1], encoding='utf-8'))
today = datetime.date.today().isoformat()
used = d['today']['tokens_used'] if d['today'].get('date') == today else 0
print(need_int(d['daily_token_budget']), need_int(d['per_invocation_max']), need_int(used))
PY
); then
  echo "[run-codex-review] FAILED: .codex/budget.json を読めない / 値が不正" >&2
  exit 1
fi
BUDGET=$(echo "$BUDGET_INFO" | cut -d' ' -f1)
PER_INV=$(echo "$BUDGET_INFO" | cut -d' ' -f2)
USED=$(echo "$BUDGET_INFO" | cut -d' ' -f3)
for v in "$BUDGET" "$PER_INV" "$USED"; do
  case "$v" in
    ''|*[!0-9]*) echo "[run-codex-review] FAILED: 予算値が整数として読めない" >&2; exit 1 ;;
  esac
done
if [ $((BUDGET - USED)) -lt "$PER_INV" ]; then
  echo "[run-codex-review] BLOCKED: budget exceeded ($USED/$BUDGET used today)" >&2
  exit 1
fi

PROMPT="独立した第二意見として以下の git diff をレビューしてください。
焦点 (優先度順):
1. 明らかなバグ / 論理ミス
2. セキュリティ上の懸念 (input validation, auth, injection)
3. テストカバレッジの不足
4. Claude が見逃しがちな盲点 (静的解析が拾わない設計の歪み)

400 語以内、優先度順に。日本語可。誤検知の可能性がある場合は明示。

---
$(cat "$TMPDIR_WORK/input.diff")"

# 固定パラメータで Codex を呼ぶ
# ★ -C で作業ルートを一時ディレクトリに閉じる (2026-08-04)。
#   ⚠️ これが無いと codex は **repo ルートで動き、diff とは無関係にリポジトリを読み返す**。
#   2026-08-03 に 1 回で 458,940 トークン (日次予算 200,000 の 2 倍超) を消費した原因がこれである。
#   レビュー対象の diff は PROMPT に入っているので、repo への読み取りは不要。
#   ★ `-C` / `--cd` は `codex exec --help` で実在を確認済み (codex-cli 0.142.5)。
#   ⚠️ 予算ガードは「呼ぶ前」しか見られず、1 回の呼び出しが予算を食い尽くすのを止められない。
#   入力側を絞るこの措置が、現状ゆいいつの実効的な歯止めである。
if ! codex exec --json --sandbox read-only --skip-git-repo-check \
  -C "$TMPDIR_WORK" \
  -m gpt-5.5 -c model_reasoning_effort=medium \
  - <<< "$PROMPT" > "$TMPDIR_WORK/result.jsonl"; then
  echo "[run-codex-review] FAILED: codex exec error" >&2
  exit 1
fi

# 結果を python で parse: 最終 agent_message を stdout、token を budget.json へ反映 (jq/flock 不要)。
"$PYTHON" - "$TMPDIR_WORK/result.jsonl" <<'PY'
import json, os, sys, datetime


def find_tokens(o):
    """usage の載る位置も**キー名**も codex のバージョンで揺れるため再帰探索する。
    旧実装は `.type=="usage"` の `total_tokens` 決め打ちで、形が変わると
    **黙って 0 を記録**し予算ガードを無効化していた。

    実測 (codex-cli 0.142.5): `turn.completed.usage` に `total_tokens` は無く
    `{input_tokens, cached_input_tokens, output_tokens, reasoning_output_tokens}` が入る。
    cached_input_tokens は input_tokens の内数、reasoning_output_tokens は
    output_tokens の内数なので、合計は input + output で採る。"""
    if isinstance(o, dict):
        v = o.get('total_tokens')
        if isinstance(v, int):
            return v
        i, out = o.get('input_tokens'), o.get('output_tokens')
        if isinstance(i, int) or isinstance(out, int):
            return (i if isinstance(i, int) else 0) + (out if isinstance(out, int) else 0)
        for x in o.values():
            r = find_tokens(x)
            if r:
                return r
    elif isinstance(o, list):
        for x in o:
            r = find_tokens(x)
            if r:
                return r
    return 0


texts, tokens = [], 0
for line in open(sys.argv[1], encoding='utf-8'):
    line = line.strip()
    if not line:
        continue
    try:
        o = json.loads(line)
    except Exception:
        continue
    if o.get('type') == 'item.completed' and o.get('item', {}).get('type') == 'agent_message':
        texts.append(o['item'].get('text', ''))
    # codex は usage を**累積**で出すため最大値を採る。行ごとの加算にすると
    # 累積形式で二重計上になる。非累積形式なら過小計上だが、予算を緩める方向の
    # 誤りは WARN で気づけるようにしてある。
    tokens = max(tokens, find_tokens(o))
# 最終 agent_message を出力 (stdout = レビュー本文)
print('\n'.join(texts))
if not tokens:
    print('[run-codex-review] WARN: token usage not found in codex output; '
          'budget records invocation only', file=sys.stderr)
# トークン使用量を予算に反映 (read-modify-write)
p = os.environ.get('BUDGET_FILE') or '.codex/budget.json'
d = json.load(open(p, encoding='utf-8'))
today = datetime.date.today().isoformat()
if d['today'].get('date') == today:
    d['today']['tokens_used'] += tokens
    d['today']['invocations'] += 1
else:
    d.setdefault('history', []).append(d['today'])
    # ⚠️★★★ history は **append-only**（消さない）。
    #   ★ 旧版は `[-30:]` で切り捨てていた。⚠️ これは budget.json 自身の注記
    #     `_comment_history_2026_09_11`（逐語「★ 実測: history を回転させるコードは
    #     repo 内に存在しない (手作業の削除だった)」「→ ★ history は append-only とし、消さない」）
    #     と**真っ向から矛盾する** —— ★ 回転させるコードは**ここに在った**。
    #   ★ 2026-09-21 に実測: 日付が変わった 1 回目の記帳で **2026-08-12 の 1 件（25290 / 1 回）が
    #     実際に消えた**（`.steering/20260920-issues-004-006/decisions.md` 判断 8・`blockers.md` 起票 22）。
    d['history'] = sorted(d['history'], key=lambda x: x.get('date', ''))
    d['today'] = {'date': today, 'tokens_used': tokens, 'invocations': 1}
# 同ディレクトリの一時ファイル + os.replace で atomic に差し替える。
# `open(p, 'w')` は開いた瞬間に truncate するため、中断で budget.json が壊れる。
tmp = p + '.tmp'
with open(tmp, 'w', encoding='utf-8') as f:
    json.dump(d, f, ensure_ascii=False, indent=2)
os.replace(tmp, p)
PY
