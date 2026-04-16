# setup-hooks.md 修正案プロンプト

> **対象**: `.claude/commands/commands_setup/setup-hooks.md`
> **目的**: 2層構成 → 3層構成 (Preflight / Guard / Report) への移行
> **背景**: 旧設計ではリマインダ層が固定文言 echo で、hook が動いているかユーザーに不透明だった。
> 新設計では UserPromptSubmit を動的プリフライトチェックに変更し、全層で結果を明示する。

---

## 変更 1: 設計原則 (§ 設計原則: 2 層構成 → 3 層構成)

**旧**:
- 第1層: 強制ブロック層 (PreToolUse)
- 第2層: リマインダ層 (UserPromptSubmit)

**新**:
- **Preflight 層** (UserPromptSubmit): `preflight.sh` が毎ターン .steering/ 状態・git 状態・reimagine 適用状態を動的チェックし、2-3 行のダッシュボードを表示。BLOCK しない（WARNING のみ）
- **Guard 層** (PreToolUse): 従来の強制ブロックを維持。パス時に `[guard] PASS` を明示出力
- **Report 層** (PostToolUse / Stop): fmt 実行結果の報告 + clippy/tsc チェック

**理由**: PreToolUse は Edit/Write 時にしか発火しないため、調査・質問のみのターンでは何も見えない。Preflight 層は毎ターン発火し、どんなターンでもプロジェクト状態が可視化される。

---

## 変更 2: Step 4 (UserPromptSubmit) の差し替え

**旧**: 固定文言の echo / prompt
```json
"command": "echo '[REMINDER] (1) CLAUDE.md を精読... (2) /reimagine を...'"
```

**新**: 動的チェックスクリプト
```json
"command": "bash .claude/hooks/preflight.sh"
```

`preflight.sh` のテンプレート:
```bash
#!/bin/bash
# Preflight dashboard — 毎ターン実行、プロジェクト状態を可視化
# 常に exit 0 (BLOCK しない)

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)

# Task check: 直近7日内の .steering/YYYYMMDD-*/ を更新日時順で検索
TASK_DIR=""
TASK_NAME=""
for i in 0 1 2 3 4 5 6 7; do
    DATE=$(date -v-${i}d +%Y%m%d 2>/dev/null || date -d "$i days ago" +%Y%m%d 2>/dev/null)
    [ -z "$DATE" ] && continue
    FOUND=$(ls -1td "${REPO_ROOT}/.steering/${DATE}-"* 2>/dev/null | head -1)
    if [ -n "$FOUND" ]; then
        TASK_DIR="$FOUND"
        TASK_NAME=$(basename "$FOUND")
        break
    fi
done

if [ -z "$TASK_DIR" ]; then
    echo "[preflight] task: NONE -- /start-task required before implementation"
    UNCOMMITTED=$(git status --short 2>/dev/null | wc -l | tr -d ' ')
    echo "[preflight] git: ${UNCOMMITTED} uncommitted"
    exit 0
fi

# Required files count
FILE_COUNT=0
MISSING=""
for f in requirement.md design.md tasklist.md; do
    if [ -f "$TASK_DIR/$f" ]; then
        FILE_COUNT=$((FILE_COUNT + 1))
    else
        MISSING="$MISSING $f"
    fi
done

# design.md template detection
DESIGN_NOTE=""
if [ -f "$TASK_DIR/design.md" ]; then
    # ヒアリング Q: design.md テンプレートの判定文字列をプロジェクトに合わせて調整
    if grep -q "採用する方針と、その理由。" "$TASK_DIR/design.md" 2>/dev/null; then
        DESIGN_NOTE=" | design: TEMPLATE"
    fi
fi

MISSING_NOTE=""
if [ -n "$MISSING" ]; then
    MISSING_NOTE=" | WARN: missing$MISSING"
fi

echo "[preflight] task: $TASK_NAME ($FILE_COUNT/3)${DESIGN_NOTE}${MISSING_NOTE}"

# Git + reimagine check
UNCOMMITTED=$(git status --short 2>/dev/null | wc -l | tr -d ' ')
REIMAGINE=""
if [ -f "$TASK_DIR/design-v1.md" ] || [ -f "$TASK_DIR/design-comparison.md" ]; then
    REIMAGINE=" | reimagine: applied"
elif grep -q "/reimagine 適用: Yes" "$TASK_DIR/requirement.md" 2>/dev/null; then
    REIMAGINE=" | reimagine: PENDING"
fi

echo "[preflight] git: ${UNCOMMITTED} uncommitted${REIMAGINE}"
exit 0
```

**カスタマイズポイント** (ヒアリングで調整):
- `design.md` テンプレート判定の grep パターン
- reimagine チェックの有無（/reimagine を使わないプロジェクトでは削除）

---

## 変更 3: Step 5 (PreToolUse) に PASS 出力追加

Guard スクリプトの最終 `exit 0` の直前に PASS 表示を追加するテンプレート:

**steering チェック**: 末尾に追加
```bash
TASK_NAME=$(basename "$TASK_DIR")
echo "[guard] PASS: steering ($TASK_NAME, 3/3 files) -> $REL"
exit 0
```

**banned パターンチェック**: 末尾に追加
```bash
echo "[guard] PASS: banned patterns ($REL)"
exit 0
```

---

## 変更 4: Step 7 (PostToolUse) をスクリプト化

**旧**: インライン lint コマンド
```json
"command": "cargo fmt --quiet 2>/dev/null || true"
```

**新**: 外部スクリプト + 変更報告
```json
"command": "bash .claude/hooks/post-fmt.sh"
```

`post-fmt.sh` テンプレート:
```bash
#!/bin/bash
# PostToolUse hook - format + 変更報告
REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
MANIFEST="${REPO_ROOT}/src-tauri/Cargo.toml"  # プロジェクトに合わせて調整

if [ ! -f "$MANIFEST" ]; then
    exit 0
fi

if cargo fmt --manifest-path "$MANIFEST" -- --check >/dev/null 2>&1; then
    exit 0
fi

cargo fmt --manifest-path "$MANIFEST" --quiet 2>/dev/null || true
echo "[fmt] cargo fmt applied"
exit 0
```

---

## 変更 5: Step 9 (settings.json 統合) のテンプレート更新

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          { "type": "command", "command": "bash .claude/hooks/session-start.sh" }
        ]
      }
    ],
    "UserPromptSubmit": [
      {
        "hooks": [
          { "type": "command", "command": "bash .claude/hooks/preflight.sh" }
        ]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "Edit|Write|MultiEdit",
        "hooks": [
          { "type": "command", "command": "bash .claude/hooks/pre-edit-steering.sh" },
          { "type": "command", "command": "bash .claude/hooks/pre-edit-banned.sh" }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          { "type": "command", "command": "bash .claude/hooks/stop-check.sh" }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Edit",
        "hooks": [
          { "type": "command", "command": "bash .claude/hooks/post-fmt.sh" }
        ]
      },
      {
        "matcher": "Write",
        "hooks": [
          { "type": "command", "command": "bash .claude/hooks/post-fmt.sh" }
        ]
      }
    ]
  }
}
```

---

## 変更 6: 完了通知の更新

```
Phase 6 完了です。

設定した Hook: 5 種（3 層構成）

【Preflight 層】
1. UserPromptSubmit → preflight.sh
   → 毎ターン .steering/ 状態・git 状態・reimagine 適用状態を動的チェック

【Guard 層】
2. PreToolUse → pre-edit-steering.sh + pre-edit-banned.sh
   → 実装ファイル編集時に [guard] PASS or BLOCKED を明示

【Report 層】
3. PostToolUse → post-fmt.sh
   → Edit/Write 後に format 実行、変更時のみ報告
4. Stop → stop-check.sh
   → セッション終了時に clippy/tsc チェック

【情報表示】
5. SessionStart → session-start.sh
   → セッション開始時にプロジェクト情報を表示
```

---

## 変更 7: 完了条件 + アンチパターンの更新

**完了条件に追加**:
- [ ] `preflight.sh` が毎ターン動的にプロジェクト状態を表示する
- [ ] PreToolUse がパス時に `[guard] PASS` を出力する
- [ ] 全 hook の出力が `[preflight]` / `[guard]` / `[fmt]` プレフィックスで統一されている

**アンチパターンに追加**:
- ❌ UserPromptSubmit に固定文言の echo を使う（動的チェックの preflight.sh を使うこと）
- ❌ PreToolUse のパス時に無言で通過する（`[guard] PASS` を出力すること）
- ❌ PostToolUse で format 変更の有無を報告しない
