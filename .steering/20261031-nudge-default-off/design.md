# 設計

## アプローチ

1. `src-tauri/src/lib.rs:119-122`: 初期値を false にし、コメントに ADR-040 D1 を書く。O1 の明示的な false（`lib.rs:3995-4003`）は二重の守りとして残し、コメントの「既定値は true」を直す。
2. `src/App.tsx:114-132`: 第2週の `interventionEnabled` を false にし、`label` と `description` を事実に合わせる。`PhaseWeek` の値（`week2_intervention`）は内部の識別子なので変えない。
3. docs（decisions D2 の範囲）。

## 変更対象

- src-tauri/src/lib.rs
- src/App.tsx
- README.md / README.ja.md / docs/agent-shared.md / docs/architecture.md / docs/verification-runbook.md / docs/pilot-runbook.md / .claude/skills/architecture-rules/SKILL.md / .claude/skills/intervention-design/SKILL.md

## テスト戦略

- `cargo test --workspace`（ゴールデンのスナップショット回帰を含む）。
- `cargo run --bin emit_schema` の出力と `schema/current.json` の一致。
- `npx tsc --noEmit`。
- 初期値を確かめる単体テストを lib.rs に足すか検討する（既存のテストの形に合わせる）。
- 画面の確認: 開始画面の週セレクタの説明文（文字の変更のみ）。
