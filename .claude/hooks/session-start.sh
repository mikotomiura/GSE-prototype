#!/bin/bash
# Session start hook - プロジェクトの動的情報を表示

echo "════════════════════════════════════════"
echo "Branch : $(git branch --show-current 2>/dev/null || echo 'N/A')"
echo "Commit : $(git log -1 --oneline 2>/dev/null || echo 'N/A')"
echo "Changed: $(git status --short 2>/dev/null | wc -l | tr -d ' ') files"

# 進行中のタスク (.steering/ 直下の日付ディレクトリ)
current_tasks=$(ls -1 .steering/ 2>/dev/null | grep -E '^[0-9]{8}-' | tail -3)
if [ -n "$current_tasks" ]; then
    echo ""
    echo "Tasks in .steering/:"
    echo "$current_tasks" | sed 's/^/  - /'
fi

echo "════════════════════════════════════════"
