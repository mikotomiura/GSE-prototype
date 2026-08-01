# 設計

## 実装アプローチ

**参照実装に揃える (発明しない)**。`scripts/run-codex-review.sh` は元から python 方式で本問題を
持たず、`scripts/run-codex-consult.sh` は PR #78 (`8ed6076`) で同方式へ統一済み。
テンプレートが生成するコードを **その形にコピーする**。

共通イディオム (4 箇所すべてで同一):

```bash
PYTHON=$(command -v python3 || command -v python || true)
if [ -z "$PYTHON" ]; then
  echo "[<name>] FAILED: python not found (予算管理/JSON パースに必須)" >&2
  exit 1
fi
```

```python
def find_tokens(o):
    """usage の載る位置は codex のバージョンで揺れるため total_tokens を再帰探索する。
    旧実装は .type=="usage" 決め打ちで、形が変わると黙って 0 を記録し予算ガードを無効化していた。"""
```

`tokens` が 0 のままなら **stderr に WARN**。黙って 0 を書かない (= 本件の核心)。
予算更新は python の read-modify-write (`flock` 不要)。

## 排他制御を捨てる判断

`flock` を外すとロックが無くなるが実害は無いと判断する (issue §5.3 と同じ結論):

- 想定利用は単一ユーザー・単一マシンで `codex-review` / `codex-consult` の並列起動は稀
- `run-codex-review.sh` は元から python 方式 (ロック無し) で運用実績がある
- **「壊れたロック + 0 が記録される」より「ロック無し + 正しい値が記録される」方が明確に良い**

必要になったら `os.mkdir()` ベースの可搬ロック (POSIX/Windows 両対応) で代替できる旨をテンプレートの
補足に残す。

## 変更対象

### 修正するファイル (テンプレート — git 追跡外)

- `.claude/commands/commands_setup/setup-codex-bridge.md`
  - Step 5 `codex-review` SKILL.md 生成部 (554-576) — `flock`+`jq` 予算更新 → python
  - Step 6.5a `scripts/run-codex-review.sh` 生成部 (914-959) — 予算チェック/更新 → python
  - Step 6.5b `scripts/run-codex-consult.sh` 生成部 (1011-1063) — 同上
  - 生成 Skill の `allowed-tools` から `Bash(jq *)` を落とす
- `.claude/commands/commands_setup/setup-hooks.md`
  - 7.5a `codex-budget-guard.sh` 生成部 (520-557) — `jq` → python、**fail-closed**
  - 7.5b `secrets-pre-filter.sh` 生成部 (574-577) — 同上
  - 7.5c `token-report-stop.sh` 生成部 (623-681) — `jq` → python、`flock` 除去
- `.claude/commands/commands_setup/verify-setup.md`
  - Step 4 の検証項目 (342) を改訂 + 実行ビット / flock・jq 非依存の検証項目を追加
- 散文の「atomic + flock」記述: `setup-agents.md:823` / `setup-skills.md:394` /
  `setup-commands.md:959`

### 修正するファイル (配備済み — git 追跡内)

ドリフト確認の結果、テンプレートと同じ欠陥が **配備済み側にも残っていた**ため併せて直す:

- `.claude/hooks/codex-budget-guard.sh` — `python3 ... || echo "0"` のフォールバックにより
  **python 不在時に BUDGET=0/USED=0/PER_INV=0 → `0 -lt 0` false → PASS**。
  ガードが fail-open している。fail-closed (exit 2) へ修正。
- `.claude/hooks/secrets-pre-filter.sh` — 同型のフォールバックがあれば同様に fail-closed へ。
- `.claude/hooks/token-report-stop.sh` — 残存する `flock` を除去 (`|| true` で無害だが
  `.lock` ゴミファイルを作る)。
- `scripts/run-codex-review.sh` — git mode が `100644` で **実行ビットが無い**。
  `codex-review` SKILL.md は `scripts/run-codex-review.sh` を**直接実行**する経路を持つため
  bug ① と同じ `Permission denied` を踏む (`cross-reviewer` は `bash ...` 経由なので無事)。
  `git update-index --chmod=+x` で修正。
  併せて `find_tokens()` + WARN を consult 側と揃える (現状は `.type=="usage"` 決め打ち)。

### 新規作成するファイル

- `.steering/20260801-codex-tooling-template-portability/decisions.md` — 排他制御の放棄と
  fail-closed/fail-open の線引きを記録

## 影響範囲

- **本体コード (Rust/TS) への影響はゼロ**。HMM / replay / schema には一切触れない。
- `commands_setup` は git 追跡外 → CI では守れない。検証は手動 (下記)。
- 配備済み hook の fail-closed 化により、**python 不在環境では codex 呼び出しが全てブロック**される。
  これは意図した挙動 (ガードが検証できないなら通さない)。python3 は macOS / git-bash の
  いずれにも標準で入るため実害は想定しない。

## 既存パターンとの整合性

- `scripts/run-codex-review.sh` / `run-codex-consult.sh` の python イディオムをそのまま踏襲。
- hook の `[guard] PASS` / `[guard] BLOCKED:` プレフィックス規約 (CLAUDE.md「Hook による自動強制」) を維持。
- `sed -i.bak` (GNU/BSD 両対応) はテンプレート側で既に正しいので触らない。

## テスト戦略

`cargo test` は無関係 (本体コード変更なし)。手動検証を tasklist に明記する:

1. **構文検証**: テンプレートが生成するはずのスクリプトを scratchpad に書き出し `bash -n`。
2. **依存残留チェック**: `grep -nE '^\s*(flock|jq) |\| *jq' <生成物>` が 0 件
   (コメント中の言及は可)。
3. **read-modify-write の実機確認**: 予算更新 python を macOS 単体で実行し、
   `budget.json` が正しく増分されることを一時コピーで確認。
4. **`find_tokens()` の単体確認**: `type=="usage"` 形 / ネストした別形 / 欠損 の 3 入力で
   それぞれ 正値 / 正値 / 0+WARN になること。
5. **verify-setup の改訂項目が実物に pass すること**: 修正後の GSE-prototype
   (`scripts/run-codex-*.sh`, `.claude/hooks/*.sh`) に対して手で当てる。
6. **hook の回帰**: `codex-budget-guard.sh` に codex を含む/含まない JSON を流し、
   PASS / BLOCKED / 早期 exit が期待通りか確認。

## ロールバック計画

- 配備済みファイル: `git revert` 一発 (単一コミット)。
- テンプレート: git 追跡外のため差分を `template-changes.patch` として残す
  (`patch -R -p1` で戻せる)。全文コピーは置かない — gitignore で「個人用」とした
  テンプレートを git に入れることになるため (decisions.md D5)。
  同じ patch が issue §5.2「他 6 コピーへ配る」の配布物にもなる。
