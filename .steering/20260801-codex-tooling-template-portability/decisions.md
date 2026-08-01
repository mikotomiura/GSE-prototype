# 設計判断

## D1: `flock` による排他制御を捨てる

**判断**: 予算更新から `flock` を完全に除去し、python の read-modify-write に統一する。

**根拠**:
- `flock` は Linux util-linux 由来で **macOS に無い**。Windows git-bash には有る。
- 生成スクリプトは `set -uo pipefail` (= `set -e` 無し) なので `flock: command not found` でも
  処理が継続する。「ロックを取ったつもりで取れていない」状態。
- 想定利用は単一ユーザー・単一マシン。`codex-review` / `codex-consult` の並列起動は稀。
- `run-codex-review.sh` は元から python 方式 (ロック無し) で運用実績がある。

**結論**: 「壊れたロック + 0 が記録される」より「ロック無し + 正しい値が記録される」方が明確に良い。
将来どうしても排他が要るなら `os.mkdir()` ベースの可搬ロック (POSIX/Windows 両対応) で代替する。

## D2: fail-closed と fail-open の線引き

同じ「python が無い / JSON が壊れている」でも、スクリプトの役割によって扱いを変える。

| スクリプト | 役割 | 判定不能時 |
|---|---|---|
| `codex-budget-guard.sh` | **ゲート** (PreToolUse) | `exit 2` で **BLOCK** |
| `secrets-pre-filter.sh` | **ゲート** (PreToolUse) | `exit 2` で **BLOCK** |
| `run-codex-*.sh` | 最終防衛 (呼び出し前に自分で止まる) | `exit 1` で中止 |
| `token-report-stop.sh` | **報告のみ** (Stop) | `WARN` + `exit 0` |

**根拠**: ガードは「検証できない = 通さない」が正しい。報告 hook を fail-closed にすると、
python が無いだけでセッション終了が妨げられ、実害の無い所で作業が止まる。

**修正した具体的な fail-open** (配備済み `codex-budget-guard.sh` に実在した):

```bash
BUDGET=$(... || echo "0")   # python 不在 → BUDGET=0
PER_INV=$(... || echo "0")  #              → PER_INV=0
USED=$(... || echo "0")     #              → USED=0
if [ $((BUDGET - USED)) -lt "$PER_INV" ]  # 0 -lt 0 は false → PASS
```

パーサが無いのにガードが「予算 OK」を返していた。

## D3: `2>/dev/null` をヒアドキュメント終端の**次の行**に置いてはいけない

作業中に自分で踏んで検知したので記録する。

```bash
if ! BUDGET_INFO=$("$PYTHON" - <<'PY'
...
PY
2>/dev/null); then     # ← これは別コマンド (null command) として実行され、
                       #    $( ) の終了ステータスがその 0 で上書きされる = fail-open
```

`$( )` の終了ステータスは**最後のコマンド**のもの。`PY` の後ろの `2>/dev/null` は
リダイレクトだけの空コマンドとして解釈され成功するため、python の失敗が握り潰される。
実際 budget.json 破損テストで `[guard] PASS: codex budget OK (0 tokens remaining)` / `rc=0` が
出てしまった (= 本件で直そうとしているバグと同じ形)。

**正**: リダイレクトはコマンド行に置く。

```bash
if ! BUDGET_INFO=$("$PYTHON" - 2>/dev/null <<'PY'
```

## D4: トークン抽出は `total_tokens` の再帰探索にする

`.type=="usage"` 決め打ちだと、codex の JSON 出力形が変わった瞬間に **黙って 0 を書き続ける**。
`find_tokens()` で再帰探索し、見つからなければ stderr に `WARN` を出す。
0 を記録するにしても「気づける」ことが本質。

検証: `type=="usage"` 形 → 1234 / ネストした `turn.stats.usage` 形 → 777 / 欠損 → 0 + WARN。
2 番目は旧実装なら 0 になっていたケース。

## D5: テンプレートのバックアップは全文でなく patch で残す

`.claude/commands/commands_setup/` は `.gitignore` の「個人用ファイル」で git 追跡外。
全文コピーを `.steering/` に置くと、意図的に追跡外にしたものを git に入れることになる。
`template-changes.patch` (unified diff) のみ残す。

副次的な利点: issue §5.2 の「他 6 コピーへ配る」作業でそのまま `patch -p1` で適用できる。
`patch -p1 --dry-run` → 適用 → 現テンプレートと byte-equal を確認済み。

---

# レビュー (code-reviewer / security-checker / Codex) で判明した追加の判断

## D6: fail-open は parse ではなく**算術評価**へ移動していただけだった

code-reviewer と security-checker が独立に同じ HIGH を指摘した。
`|| echo "0"` を消しても、**値が整数でなければ bash の算術がエラーになり、
`set -e` が無いので次へ進む**。実測 (bash 3.2 / macOS 既定):

| budget.json の値 | 修正前の実測 |
|---|---|
| `null` | `None: unbound variable` → **rc=0 = PASS** |
| `200000.0` (float) | `invalid arithmetic operator` → 素通り |
| `"200000 999"` (空白入り) | `cut` がずれて `PER_INV=999` → **PASS** |
| `2**64 + 10` | 64bit ラップで残量が正に戻り **PASS** |

**対処**: python 側 `need_int()` で bool / 非 int / 負値 / `> 10**12` を例外にし、
既存の fail-closed 経路へ落とす。加えて shell 側でも `case "$v" in ''|*[!0-9]*)` で二重に検証する。
「python が通っても受け渡しが崩れれば同じ穴」なので両方要る。

## D7: ゲートの**発火条件そのもの**が緩かった

fail-open を塞いでも、ゲートが発火しなければ意味がない。security-checker の H2/H3。

1. `grep -qE 'codex[[:space:]]+exec'` 決め打ち → `codex e` (alias) /
   `codex review` / `codex --cd . exec` / 行継続 がすべて素通り。
   → サブコマンドを限定せず「codex が単独トークンとして出るか」で判定する。
   対話 REPL も予算チェック対象に含めて構わない (安全側)。
2. 禁止パターンの終端が「空白または引用符」だけ → **最も自然な書き方**
   (コマンド置換でファイルを埋め込む形) が終端 `)` のため素通り。
   → `([^A-Za-z0-9_]|$)` に緩める。direnv の設定ファイルも追加。
3. `grep` 自体への依存も fail-open — `grep` 不在 / regex エラーだと
   `if ! ... ; then exit 0` が「codex ではない」と解釈して通す。
   → 判定を python へ移し、判定不能なら `exit 2`。

### D7 の揺り戻し: 広げすぎて誤爆した → **コマンド位置**に限定した

1 の対処で「codex という語が単独トークンで出るか」にしたところ、
**ヒアドキュメント内の散文で codex に言及しただけの Bash 呼び出しまでブロック**
するようになった (作業中に 2 回踏んだ。作業記録を書く `python3 - <<EOF` が止まった)。

ゲートの目的は「codex を**起動する**呼び出し」を捕まえることなので、
行頭 / パイプ / `;` / `&&` / `||` / `(` の直後 = コマンド位置に限定した。

検証 (18 ケース):

| 発火する | 発火しない |
|---|---|
| `codex exec` / `codex e` / `codex review` | 散文中の言及 (heredoc 内) |
| `codex --cd . exec` (オプション先行) | `grep -n "codex" README.md` |
| `cd /tmp && codex exec` / `cat x \| codex exec -` | `ls codex-tools/` (ハイフン継続) |
| `OUT=$(codex exec foo)` (コマンド置換) | `cat .codex/budget.json` (パスの一部) |
| `/usr/local/bin/codex exec` (絶対パス) | 無関係なコマンド |
| 改行後の行頭 | |

**教訓**: ゲートは「広げれば安全」ではない。誤爆が多いと運用が回らず、
結局オフにされて穴になる。**発火条件は正確に**。

## D8: `secrets-filter.sh` が NDJSON hunk を落としていなかった (プライバシー規約違反経路)

hook 側の禁止パターンは NDJSON を持つのに、diff 本文を見る
`secrets-filter.sh` の `skip_hunk` には無い、という非対称があった。
追跡下の `src-tauri/tests/fixtures/` 配下のセッションログ fixture は vk コード列を含み
`git diff` に乗るため、fixture を編集して `/cross-review` を回すとそのまま外部 LLM へ渡る。
`docs/agent-shared.md` の「キーストローク内容・生ログは外部 LLM に送信しない」に抵触する。

→ `skip_hunk` に同じ拡張子条件を追加。検証: vk を含む hunk が落ち、
無関係な hunk は通り、exit 2 になることを確認した。
**本タスクの当初スコープ外だが、同じファイル族の既知のプライバシー違反経路のため塞いだ。**

## D9: codex-cli 0.142.5 には `total_tokens` が無い (WARN が実地で仕事をした)

本タスクの独立レビューを実際に走らせたところ `find_tokens()` が 0 を返し、
新設した WARN が発火した。実出力を確認すると `turn.completed.usage` は
`input_tokens` / `cached_input_tokens` / `output_tokens` / `reasoning_output_tokens` の 4 つで、
**`total_tokens` が存在しない**。

つまり「再帰探索にする」だけでは不足で、決め打ちを直した後も 0 を記録し続けるところだった。
WARN が無ければ **また 1 ヶ月気づかなかった**はずで、D4 の判断 (気づけることが本質) が
実地で裏付けられた形になる。

→ `find_tokens()` に「`total_tokens` が無ければ入力 + 出力の和」を追加。
cached / reasoning はそれぞれ入力 / 出力の内数なので足さない。
実出力に対して 28034 を抽出することを確認し、その値を予算に反映した。

## D10: 指摘のうち採らなかったもの

- **「`run-codex-review.sh` が codex exec の失敗を捕捉していない」= 誤検知**。
  Codex には diff しか渡していないため、既存の失敗捕捉が見えていない。実物を確認して却下。
- **「ロック廃止で lost update が起こる」= 既知・受容** (D1)。並列起動は稀で、
  「壊れたロック + 0 記録」より明確に良い。`os.replace` で破損だけは防いだ。
- **「`ROOT` が git 不在時に `.` へ落ちる」= 仕様**。budget.json が無ければ
  「Phase 5 未完了」として guard 不適用にする既存の設計に合わせている。

## D11: 独立レビュー (`/cross-review`) は縮退させず手動経路で実施した

ラッパー経路は自己ブロックする: 本タスクの diff は `secrets-filter.sh` /
`secrets-pre-filter.sh` を含み、**ファイル名の "secret"** が `secrets-filter.sh` 自身の
hunk skip 条件に当たって exit 2 になる (既知の catch-22)。
さらに `secrets-filter.sh` の全文を添付すると、今度は**自身の検出パターン一覧**
(`ANTHROPIC_API_KEY` 等) が行内マッチして exit 2 になる。

→ 縮退 (Claude 単独) にはせず、記録済みの手動経路で実施した:
1. `secret` を名前に含む 2 ファイルを除いた diff を作る
2. `secrets-pre-filter.sh` は全文添付、`secrets-filter.sh` は変更内容を散文で説明
3. `secrets-filter.sh` を通して exit 0 を確認してから codex へ送信
4. トークンを手動で予算へ反映

**恒久対処は別タスク**: 自ファイル名・自パターン一覧による自己ブロックの回避
(例: skip 判定を「ファイル名に secret を含む」から「実際に秘密値の形をしている」へ寄せる)。
