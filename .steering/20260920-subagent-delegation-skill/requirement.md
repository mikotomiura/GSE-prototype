# 要件 — サブエージェント委譲の規律を Skill 化し、サーヴェイ実行の運用を `/literature-review` へ落とす

- **作成**: 2026-09-20
- **ブランチ**: `docs/subagent-delegation-skill`（★ main から。G1 ゲートとは別トピック）

## 背景（★ すべて 2026-09-20 に一次で実測）

### ⚠️ 委譲の規律が repo に 1 行も無い

| 置き場 | `subagent` / 委譲 / 並列 |
|---|---|
| `.claude/skills/`（23 本） | ❌ **該当 Skill なし** |
| `docs/external-skills.md` | ❌ **0 件** |
| `.claude/commands/literature-review.md`（187 行） | ❌ **0 件** |

→ ⚠️ いま規律があるのは **`~/.claude/.../memory/` の 4 件だけ**である。
★ プロジェクト自身の格付け（`verify-before-claiming` ルール 1）で **memory は三次資料**であり、
**根拠にしてはならない**と定めている。加えて memory は **マシン単位**で、
**Codex CLI とは共有されず**、**版管理もされない**。

⚠️★★★ **本セッションで実際にこの穴を踏んだ**: 2026-09-13 付の引き継ぎメモ（三次資料）を根拠に
「次は `stall onset` の操作的定義」と報告したが、一次を見ると **`stall onset` は ADR-030 で定義され
実装も完了済み**だった。→ ★ **三次資料に規律を置くと、その規律自体が腐る。**

### ⚠️ サーヴェイ実行の運用も同じ状態

`/literature-review` は Step 0〜9 のパイプラインを持つが、実測で次が **0 件**:
`commit`（毎ラウンド即コミット）/ `check_citations`（再実行ループ）/ `pypdf`（PDF の読み方）/ `並列`。

### ★ 一次資料が既にあるもの（★ 重複して書かない）

- **モデル割当ポリシー**: `docs/loop-engineering.md:60-76`
  逐語「**やり直しが効かない判断は Opus / やり直しが効く作業は Sonnet / 判断を含まない実行は Haiku。**」
  ＋ 役割別の表（survey = Sonnet ／ 統合レビュー = Opus ／ verify 実行 = Haiku ／ 監視 = Haiku）。
  → ★ **Skill はこれを再定義せず、引いて subagent 固有の制約を足す。**

### ⚠️ ついでに見つかった矛盾（★ 起票する）

★ `Task`（subagent 起動）を持つ agent は **`loop-worker` の 1 本だけ**（12 本中）。
⚠️ ところが `.claude/commands/cross-review.md` Step 5 は逐語で
「`cross-reviewer` 内部で: 1. `code-reviewer` を **Task で並列起動**」と書いている。
★ 実体は `.claude/agents/cross-reviewer.md` の `tools: Read, Bash, Glob, Grep` で **`Task` を持たず**、
本文にも `Task` は **0 件**。→ ⚠️ **文書が約束している内部動作は実行不可能である。**

## ゴール

1. **`.claude/skills/subagent-delegation/SKILL.md` を新設**し、委譲の規律の SSOT にする。
2. **`/literature-review` に「回し方」の節を追記**する（fan-out / 直列にする所 / 毎ラウンド即コミット /
   `check_citations` の再実行ループ / PDF は `pypdf`）。
3. `CLAUDE.md` の Skill 表に 1 行足して入口を作る。
4. 対応する **memory 4 件をポインタに縮める**（★ 二重管理の drift を止める）。

- Done: `empirical-prompt-tuning` の **Lite**（1 シナリオ × 2 iter）を通し、
  **別エージェントが読んで詰まらない**ことを実測する。
- Stop: `docs/loop-engineering.md` のモデル割当ポリシーを**書き換えない**（★ 引くだけ）。

## スコープ外（★ やらないこと）

- ⚠️ `docs/loop-engineering.md` の改訂（★ Loop の SSOT。本タスクは引用するだけ）
- ⚠️ **`cross-reviewer` / `/cross-review` の修正**（→ ★ **起票して次タスクへ**。
  ★ 直すには「cross-reviewer に `Task` を与える」か「コマンドの記述を実体に合わせる」かの
  **裁定**が要り、本タスクの射程を超える）
- 公式 Skill（`docs/external-skills.md`）で足りる領域の自作
- `.claude/agents/*.md` の新規作成・改訂

## 運用メモ

- /reimagine 適用: **No**
- 理由: 置き場・memory の扱い・検証 tier は grill で研究者が確定済み（`decisions.md` 判断 1〜4）。
  ★ 残るのは執筆であり、初回案を破棄して比較する段ではない。
