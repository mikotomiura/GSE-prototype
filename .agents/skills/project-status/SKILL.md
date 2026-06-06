---
name: project-status
description: >
  GSE プロジェクトの現在状態をリアルタイムで取得する動的 Skill。
  作業を始める前・コンテキストが分からなくなったとき・進捗を確認したいとき・
  最近の変更を把握したいとき・.steering/ の記録を確認したいときに使う。
  git 状態・最近コミット・未完了タスク・変更ファイル統計・steering 記録を一括取得。
context: fork
agent: Explore
allowed-tools: Bash(git *), Bash(grep *), Bash(find *), Bash(wc *), Read, Glob
---

# Project Status

このスキルは現在の GSE プロジェクト状態を動的に取得します。

## 現在の git 状態

```bash
git status --short
```

## 最近のコミット (10 件)

```bash
git log --oneline -10
```

## 現在のブランチ

```bash
git branch --show-current
```

## 進行中の .steering/ タスク（ディレクトリ一覧）

```bash
ls .steering/ | grep -v '^_' | grep -v '^README'
```

## 未完了チェックボックス（件数と内容）

```bash
grep -r "- \[ \]" .steering/ --include="tasklist.md" -l 2>/dev/null
```

```bash
grep -r "- \[ \]" .steering/ --include="tasklist.md" 2>/dev/null | head -10
```

## 変更ファイルの統計

```bash
git diff --stat HEAD 2>/dev/null | tail -1
```

## あなたのタスク

上記の動的データを分析し、以下を報告してください:

1. **現状サマリ** — 1-2 行で
2. **進行中の作業** — .steering/ と git status から
3. **注意すべき点** — 未コミット変更・未完了タスク・大量変更など
4. **推奨される次のアクション** — 何を優先すべきか

レポートは簡潔に。詳細は必要に応じてユーザーが追加で質問する。
