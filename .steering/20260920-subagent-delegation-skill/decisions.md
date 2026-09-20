# 設計判断 — サブエージェント委譲の Skill 化

## 判断 1: 委譲の規律は **新 Skill `subagent-delegation`** に置く

- **判断日時**: 2026-09-20（grill・研究者が選択）
- **選択肢**: A: 新 Skill ／ B: `CLAUDE.md §4` を厚くする ／ C: `implementation-workflow` に節を足す
- **採用**: **A**
- **理由**: ★ 内容が契約的で長い（model 割当 / 範囲と禁止事項 / 並列 / 入れ子 / 締切 / レビュー系の範囲）。
  ⚠️ B は `CLAUDE.md` 自身が冒頭で「**探索を始める起点を示すことであり、全情報を含むことではない**」と
  宣言しており、厚くすると**その宣言が嘘になる**（★ `run.sh` の宣言と同じ論法）。加えて
  **毎セッションの固定コスト**が増える。⚠️ C は委譲がレビュー・サーヴェイ・調査にもかかるので射程が狭い。
- **★ 先例**: `verify-before-claiming` と同じ型（★ 規律を Skill に置き、`CLAUDE.md` の表から指す）。

## 判断 2: サーヴェイ実行の運用は **`/literature-review` に追記**する

- **判断日時**: 2026-09-20（grill・研究者が選択）
- **選択肢**: A: `/literature-review` に追記 ／ B: 独立 Skill `survey-execution` ／ C: `citation-ssot` に追記
- **採用**: **A**
- **理由**: ★ 既に Step 0〜9 のパイプラインを持つコマンドが自然な持ち主で、**回すときに必ず読まれる**。
  ⚠️ B は `citation-ssot` / `literature-card` / `/literature-review` と **4 つ目**になり、
  「どれを見るか」が曖昧になる。⚠️ C は採番・append-only の持ち主であり、
  fan-out や `pypdf` を入れると**責務が混ざる**。

## 判断 3: 対応する memory 4 件は **ポインタに縮める**

- **判断日時**: 2026-09-20（grill・研究者が選択）
- **対象**: `feedback_use_subagents` / `feedback_subagent_model_split` /
  `feedback_review_subagent_scope` / `feedback_survey_via_subagent`
- **選択肢**: A: ポインタに縮める ／ B: そのまま残す ／ C: 削除
- **採用**: **A**
- **理由**: ⚠️ B は同じ規律が 2 か所に並立し、**片方だけ更新されて食い違う**。
  ★ 本セッションで実際にその型を踏んだ（2026-09-13 付の三次資料を根拠に誤報した）。
  ⚠️ C は **別 repo で作業するときに規律が 1 つも残らない**（★ memory はマシン単位、Skill は repo 単位）。
  → ★ **中身は Skill、memory は「どこを見るか」の 1 行**にする。

## 判断 4: 検証は `empirical-prompt-tuning` の **Lite**

- **判断日時**: 2026-09-20（grill・研究者が選択）
- **採用**: **Lite**（1 シナリオ × 2 iter・タグ監査なし・Hold-out なし）
- **理由**: ★ 同 Skill の選択マトリクス「**重要度 HIGH × 変更頻度 HIGH → Lite を頻繁に**」に当たる
  （★ 新規 Skill の初版は変更頻度が高い）。⚠️ Full は subagent が一気に増え、初版には重い。
  ⚠️ Structural-only は「**別のエージェントが読んで詰まらないか**」を実測しないので、
  ★ この Skill の目的自体が未検証になる。

---

## 判断 5: 規律ごとに **出所の格を明記する**（★ 本 Skill 固有の書式）

- **理由**: ⚠️★★★ 本 Skill が集める規律は **出所の格が揃っていない**。
  混ぜて書くと、⚠️ **memory 由来の規律まで一次資料のように読まれる**。
  → ★ 各規律に次のどれかを付ける:

| 印 | 意味 | 例 |
|---|---|---|
| **一次** | コード / 設定ファイル / 実測 | `Task` を持つ agent は `loop-worker` だけ（`.claude/agents/*.md` の `tools:` を実測） |
| **SSOT** | repo の確定文書 | モデル割当（`docs/loop-engineering.md:60-76`） |
| **実地** | `.steering/` に残る当時の記録 | 25 分ハング（`_handoff/next-session-g1-preconditions-verification.md:85`） |
| ⚠️ **未記録** | ★ **本 Skill で初めて repo に入る**（従来は memory のみ） | 締切の明記・レビュー系の範囲指定 |

- ⚠️ **「未記録」は、次に同じ場面が来たら *一次で確かめ直す* 対象**である（★ 格上げしない）。

## 判断 6: `cross-reviewer` の矛盾は **起票して直さない**

- **見つけたもの**（★ 2026-09-20 に一次で確認）: `.claude/commands/cross-review.md` Step 5 は逐語で
  「`cross-reviewer` 内部で **`code-reviewer` を Task で並列起動**」と書くが、
  ⚠️ `.claude/agents/cross-reviewer.md` の `tools:` は **`Read, Bash, Glob, Grep`** で **`Task` が無く**、
  本文にも `Task` は **0 件**。→ **文書が約束する内部動作は実行不可能**。
- **判断**: ★ **本タスクでは直さない。起票する。**
- **理由**: ⚠️ 直し方が **2 通りあり、裁定が要る**:
  - (a) `cross-reviewer` に `Task` を与える → ⚠️ **入れ子起動を 2 本目の agent に許す**ことになる
  - (b) コマンドの記述を実体（★ メインが code-reviewer と Codex を別々に起動する）へ合わせる
  ★ 本タスクのゴールは「規律を SSOT 化する」ことであり、⚠️ 裁定を混ぜるとスコープが崩れる。
- ★ **ただし Skill には「実体はこうである」と書く**（⚠️ 誤った内部動作を前提に委譲させない）。
