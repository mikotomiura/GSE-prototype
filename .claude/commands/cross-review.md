---
description: >
  Claude と Codex で同じ変更を独立にレビューさせ、両者の結果を比較した統合レポートを返す。
  リリース直前 / セキュリティ関連 / 重要 PR で第二意見が欲しい時に使う。
  予算ガード (codex-budget-guard hook) と機密フィルタ (secrets-pre-filter hook、
  scripts/secrets-filter.sh) は呼び出し前に効いている前提。proprietary plugin 出力 /
  機密情報を含む diff には適用しない。
allowed-tools: Bash(git *), Bash(python *), Bash(python3 *), Read, Task
---

# /cross-review — Claude + Codex 並列レビュー

## このコマンドの目的

Claude の自己バイアスを Codex の独立視点で補正する。重要 PR で「両方が一致して指摘した問題」を最優先で対処することで、レビュー品質を担保する。

## 起動条件

- 重要 PR（リリース直前、セキュリティ関連）のレビュー
- ユーザーが「両方の視点で見て」と明示
- `code-reviewer` 単独レビューに不安がある時

## 適用しないケース

- diff が proprietary plugin 出力（`*.pdf` / `*.docx` / `*.xlsx` / `*.pptx`）を含む
- diff が機密情報（`.env`, `*.pem`, `*.key`, `*credentials*`）を含む
- `docs/external-skills.md` で「外部 LLM 送信禁止」となっているファイルを含む

## 実行フロー

### Step 1: 対象 diff の確定とサイズ判定

```bash
git diff --stat
git diff --name-only
```

変更がない場合は中断:
> 「変更がありません。レビュー対象がないため終了します。」

### Step 2: Proprietary / 機密混入チェック (fail-closed)

```bash
if git diff --name-only | grep -E '\.(pdf|docx|xlsx|pptx|env|pem|key)$|credentials|secret'; then
  echo "[/cross-review] BLOCKED: diff contains proprietary or sensitive files"
  echo "code-reviewer 単独に切り替えてください"
  exit 1
fi
```

### Step 3: 行数閾値による分岐

`.codex/budget.json` から閾値を読み込む (jq 非依存・python 使用):

```bash
THRESHOLD=$(python -c "import json;print(json.load(open('.codex/budget.json'))['diff_size_threshold_lines'])")
MANUAL_APPROVAL=$(python -c "import json;print(json.load(open('.codex/budget.json'))['manual_approval_threshold_lines'])")
LINES=$(git diff --stat | tail -1 | grep -o '[0-9]* insertion' | grep -o '[0-9]*' || echo 0)
```

- `LINES > MANUAL_APPROVAL` (デフォルト 2000): ユーザーに確認を求める。「n」なら `code-reviewer` 単独でフォールバック
- `LINES > THRESHOLD` (デフォルト 500): 警告だけ表示して進む
- それ以下: 自動進行

### Step 4: 予算チェック

```bash
# jq 非依存・python 使用
BUDGET=$(python -c "import json;print(json.load(open('.codex/budget.json'))['daily_token_budget'])")
PER_INV=$(python -c "import json;print(json.load(open('.codex/budget.json'))['per_invocation_max'])")
USED=$(python -c "import json,datetime;d=json.load(open('.codex/budget.json'));t=datetime.date.today().isoformat();print(d['today']['tokens_used'] if d['today'].get('date')==t else 0)")

if [ $((BUDGET - USED)) -lt "$PER_INV" ]; then
  echo "[/cross-review] BLOCKED: daily budget would be exceeded"
  echo "code-reviewer 単独に切り替えてください"
  exit 1
fi
```

### Step 5: cross-reviewer エージェントの起動

```
Task (cross-reviewer): 「git diff の現在の変更を Claude と Codex で並列にレビューし、
統合レポートを返してください。両者の指摘の一致 / 乖離を分類した上で優先度判定を付ける。」
```

`cross-reviewer` 内部で:
1. `code-reviewer` を Task で並列起動（Claude のレビュー）
2. `codex-review` Skill を Bash で並列起動（Codex のレビュー）
3. 両結果を比較・分類して統合レポート生成

### Step 6: 結果の表示と次アクション

統合レポートをユーザーに提示:

```markdown
## /cross-review 統合レポート

### 両者一致 (HIGH priority — 即対応推奨)
...

### Claude のみ指摘
採用 / 却下 / 要確認:
...

### Codex のみ指摘
採用 / 却下 / 要確認:
...

### 推奨アクション（優先度順）
1. ...
```

ユーザーが対処を進める（修正 → `/cross-review` 再実行）、または採用 / 却下を確定して終了。

## 関連

- `cross-reviewer` エージェント (`.claude/agents/cross-reviewer.md`)
- `codex-review` Skill (`.claude/skills/codex-review/SKILL.md`)
- `code-reviewer` エージェント (`.claude/agents/code-reviewer.md`)
- `.codex/budget.json` — 予算管理

## アンチパターン

- ❌ proprietary / 機密混入チェックを skip
- ❌ 予算チェックを skip
- ❌ 結果を盲信する（両者一致 HIGH でも false positive の可能性あり）
- ❌ 自動 commit する（人間の判断を必ず挟む）
