# タスクリスト

## 準備
- [x] `.idea/issue-commands-setup-flock-portability.md` を読む (単一真実源)
- [x] 参照実装 `scripts/run-codex-review.sh` / `run-codex-consult.sh` を読む
- [x] テンプレート 4 箇所 + 散文 3 箇所を grep で特定
- [x] 配備済みファイルのドリフト確認 (hook の fail-open / 実行ビット)
- [x] テンプレートの変更前状態を退避 → 最終的に `template-changes.patch` として記録 (decisions.md D5)

## 実装 — テンプレート (git 追跡外)
- [x] `setup-codex-bridge.md` Step 5: codex-review SKILL.md 生成部の flock+jq → python
- [x] `setup-codex-bridge.md` 6.5a: `run-codex-review.sh` 生成部 → python (予算 read + update)
- [x] `setup-codex-bridge.md` 6.5b: `run-codex-consult.sh` 生成部 → python
- [x] `setup-codex-bridge.md`: 生成 Skill の allowed-tools から `Bash(jq *)` を除去
- [x] `setup-hooks.md` 7.5a: `codex-budget-guard.sh` → python + fail-closed
- [x] `setup-hooks.md` 7.5b: `secrets-pre-filter.sh` → python + fail-closed
- [x] `setup-hooks.md` 7.5c: `token-report-stop.sh` → python + flock 除去
- [x] `verify-setup.md`: 検証項目改訂 (flock 要求 → flock/jq 非依存) + 実行ビット検証追加
- [x] 散文修正: `setup-agents.md` / `setup-skills.md` / `setup-commands.md`

## 実装 — 配備済み (git 追跡内)
- [x] `.claude/hooks/codex-budget-guard.sh`: fail-open → fail-closed
- [x] `.claude/hooks/secrets-pre-filter.sh`: 同上
- [x] `.claude/hooks/token-report-stop.sh`: 残存 flock 除去
- [x] `scripts/run-codex-review.sh`: 実行ビット付与 + `find_tokens()` + WARN を consult と統一

## テスト (手動 — commands_setup は CI 対象外)
- [x] 生成物を scratchpad に書き出し `bash -n` 構文検証
- [x] `grep -nE '^\s*(flock|jq) |\| *jq'` が 0 件
- [x] 予算 read-modify-write を python 単体で実行 (budget.json コピーに対して増分確認)
- [x] `find_tokens()` を 3 入力 (usage 形 / ネスト形 / 欠損) で確認
- [x] `codex-budget-guard.sh` に JSON を流して PASS / BLOCKED / 早期 exit を確認
- [x] 改訂した verify-setup 項目を GSE-prototype 実物に当てて pass すること

## レビュー
- [x] code-reviewer によるレビュー (HIGH 2 / MEDIUM 8 / LOW 6)
- [x] security-checker (HIGH 3 / MEDIUM 5 / LOW 5)
- [x] 独立レビュー (Codex) — ラッパーが自己ブロックするため手動経路で実施
      (decisions.md D11 に経路と理由を記録。**縮退 = skip はしていない**)
- [x] HIGH 指摘への対応 (D6 算術 fail-open / D7 ゲート発火条件 / D8 セッションログ / D9 usage キー名)
- [x] 対応後の回帰テスト再実行 (配備済み + テンプレート生成物の両方)

## ドキュメント
- [x] `.idea/issue-commands-setup-flock-portability.md` の「進捗」欄を更新
- [x] issue に「参照実装ができた」旨を追記 (他 6 コピーへの配布用)

## 完了処理
- [x] design.md の最終化
- [x] decisions.md の作成 (D1-D11)
- [x] git commit (branch `fix/codex-tooling-portability`)
      — **テンプレートと `.idea/` は追跡外なのでコミットに乗らない**点を完了報告に明記済み

## 残作業 (別タスク)

- [ ] 他 6 コピーへの `template-changes.patch` 配布 (`.idea/issue-...` §7.1 の管轄)。
      **配備済みファイルにも同じ修正が要る**点に注意 (§7.3)
- [ ] `secrets-filter.sh` の自己ブロック解消 — 「ファイル名に secret を含む」「自身の
      検出パターン一覧が行内マッチする」の 2 段で、自分自身の diff をレビューできない
      (decisions.md D11)
