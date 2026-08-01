# 次セッション開始プロンプト — Codex 連携ツールの移植性バグを bootstrap テンプレート側で根治する

このタスクは **実装作業 (`.steering/`)** なので、必ず `/start-task` を先に実行して作業記録を作ること。
下の「===」以下をそのままコピペして開始する。

---

Codex 連携ツールの macOS 移植性バグを、**bootstrap テンプレート側**で根治する。
2026-08-01 に GSE-prototype の**配備済みスクリプト**は修正済み (PR #78 / main `8ed6076`) だが、
**テンプレートは未修正**のため、新規プロジェクトを bootstrap すると同じバグを再生産する。

## まず読む (着手前・順守)

1. `.idea/issue-commands-setup-flock-portability.md` — **本件の詳細・影響範囲・修正方針の単一真実源**。
   まずこれを読む。
2. 修正済みの参照実装 (これに揃える):
   - `scripts/run-codex-review.sh` — 元から python 方式 (jq/flock 非依存)。**これが正解の形**。
   - `scripts/run-codex-consult.sh` — PR #78 で同方式へ統一した。差分が実例になる (`git show 8ed6076`)。
3. Skill: `git-workflow` (コミット規約) / `implementation-workflow` (共通骨格)。

## 背景 (なぜ直すか)

macOS には `flock` が無い。テンプレートが生成する予算更新コードは

```bash
(
  flock -x 9
  jq ... .codex/budget.json > .codex/budget.json.tmp && mv ...
) 9> .codex/budget.json.lock
```

という形で、macOS では `flock: command not found` になる。しかし生成されるスクリプトは
`set -uo pipefail` (= `set -e` なし) なので **処理が継続**し、さらに
`jq -r 'select(.type=="usage") | .usage.total_tokens // 0'` が 0 を返すため
`budget.json` に **`tokens_used=0` が記録**される。

結果として「Codex を呼んでも消費が積み上がらない」= **予算ガードが実質無効**な状態になる。
エラーで止まらないので**気づかない**のが最大の問題。実際 GSE-prototype では
`.codex/budget.json` の `tokens_used` が 116283 のまま 1 ヶ月以上放置されていた。

## ゴール

新規 bootstrap したプロジェクトが、**macOS でも Windows git-bash でも**予算ガードが正しく効く状態になる。
テンプレートと `verify-setup` の検証項目が整合する。

## 作業対象 (このリポジトリ内)

`.claude/commands/commands_setup/` 配下。**注意: このディレクトリは `.gitignore` の「個人用ファイル」に
入っており git 追跡されていない**。よって通常のコミットには乗らない。
→ 変更の記録は `.steering/` に残し、テンプレート本体の同期は `.idea/issue-...` の手順に従う。

| ファイル | 行 | 内容 |
|---|---|---|
| `setup-codex-bridge.md` | 560 / 950 / 1054 | `flock -x 9` を含む予算更新コードを生成 |
| `setup-hooks.md` | 659 | 同上 (token-report-stop.sh 生成部) |
| `verify-setup.md` | 342 | 「atomic budget update (**flock**) が実装されているか」を要求 |

## 修正方針

1. **4 箇所の `flock` + `jq` ブロックを python 方式へ差し替える**。
   `run-codex-review.sh` の実装をそのまま雛形にする (read-modify-write + `datetime.date.today()`)。
   トークン抽出は **`total_tokens` の再帰探索**にし、codex の出力形が変わっても黙って 0 にならないよう
   `WARN` を出す (PR #78 で追加した `find_tokens()` を流用)。
2. **生成されるスクリプト冒頭に `PYTHON=$(command -v python3 || command -v python || true)` の
   検出と不在時 fail を入れる** (run-codex-review.sh と同形)。
3. **`verify-setup.md:342` を改訂**。「flock が実装されているか」→
   「**予算更新が atomic かつ `flock`/`jq` 非依存 (python) で実装されているか**」。
   現状のままだと、正しく直したプロジェクトほど検証に落ちる。
4. **生成物に実行ビットを付ける手順を明記**。今回のバグ①は `secrets-filter.sh` が `100644` で
   `Permission denied` になり codex-consult が完全に動作不能だったもの。テンプレートに
   `chmod +x` を含めるか、`verify-setup` で実行ビットを検証する項目を足す。

## やらないこと (スコープ外)

- `sed -i` は**テンプレート側は既に正しい** (`setup-hooks.md:671` は `sed -i.bak`)。
  GSE-prototype の配備済みファイルがテンプレートから逸脱していた (ドリフト) だけなので、
  テンプレート修正は不要。**ドリフトが他にも無いか確認するだけ**でよい。
- 他プロジェクトへの横展開は `.idea/issue-...` の管轄。このセッションでは
  GSE-prototype 内のテンプレートを直し、**issue に「参照実装ができた」旨を追記**するところまで。

## 検証

`.claude/commands/commands_setup` は追跡外なので CI では守れない。手で確認する:

1. 生成されるはずのスクリプトを一時ディレクトリに書き出し、`bash -n` で構文検証。
2. `flock` / `jq` が**実コマンドとして**残っていないこと (コメント中の言及は可):
   `grep -nE '^\s*(flock|jq) |\| *jq' <生成物>`
3. 予算更新の read-modify-write が macOS で通ること (python 単体で確認)。
4. `verify-setup.md` の改訂項目が、修正後の GSE-prototype 実物に対して **pass** すること。

## 完了時

- `/finish-task` を実行 (`/cross-review` 含む)。
- `.idea/issue-commands-setup-flock-portability.md` の「進捗」欄を更新する。
- テンプレートは git 追跡外なので、**コミットされるのは `.steering/` の作業記録のみ**になる点を
  完了報告で明示する (「変更したのにコミットが無い」と後で混乱しないため)。
