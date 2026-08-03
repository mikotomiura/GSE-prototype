# Loop Engineering 統合 検証レポート

検証日時: 2026-08-01 17:29
統合モード: full · 実行モード: A+B+C · Codex ゲート(L6): enabled
grilling(L2): self-provided · CLAUDE.md loop 節: appended

## 総合判定

✅ HEALTHY

## Step 1: ファイル存在 (README §2.1)
- 固定名成果物: 12/12 存在（doc 1・commands 3・agents 2・hook 1・scripts 2・steering テンプレ 3）
  - 実行モード A+B+C の想定どおり `loop-orchestrate.md` / `loop-worker.md` (B) と
    `loop-run.sh` (C) がすべて存在し、取り残しなし
- 追記契約 (CLAUDE.md / settings.json / progress / external-skills / agent-shared): ✅
- 条件付き: L6 skip の取り残しなし N/A (L6 は enabled) · L2 self-provided grilling ✅
  (`.claude/skills/grilling/SKILL.md` / `.claude/skills/issue-slicing/SKILL.md` とも
  model: Opus を明記)
- 実行モードの取り残し: なし (A/B/C いずれの成果物も想定どおり存在)
- CLAUDE.md loop 節: appended ✅ · 行数 19/20 (マーカ込み)・CLAUDE.md 全体 148/150 行
- docs で止まった実装なし: `docs/loop-engineering.md` に対応する実行体
  (loop-issue/loop-orchestrate/loop-run.sh) と loop-watchdog が揃っている ✅

## Step 2: wiring
- loop-guard.sh 実行権限 (-x): ✅
- loop-guard.sh が Stop hook 登録: ✅ (既存 stop-check.sh / token-report-stop.sh を破壊せず追記)
- loop-issue の workflow 参照 (full=参照): ✅ (`implementation-workflow` skill を参照)
- model 割当が docs の表と一致 (watchdog=haiku / loop-worker=sonnet / review=opus / slicing=opus): ✅
- loop-status の single-writer 明記: ✅
- [モードB] セッション境界ガード: ✅
- [モードB] 既定並列 1 + Allowed Files 非交差判定: ✅
- [モードB] loop-worker が /goal を使っていない: ✅ (「/goal は使えない」と明記のみ)
- [モードB] worker 自己申告を events で独立検証: ✅ (loop-watchdog 経由)
- [モードB] board の single-writer 例外運用: ✅ (「別端末の /loop-status を同時に走らせない」条件を明記)
- [モードC] bash -n 通過 + 実行権限: ✅
- [モードC] mode ガード (mode!="C" で停止): ✅
- [モードC] loop-spawn.sh --no-exec への委譲 + spawn 側の対応: ✅
- [モードC] permission_mode 安全既定 (acceptEdits / 全許可は明示合意): ✅
  (`LOOP_ALLOW_FULL_ACCESS=1` が無い限り拒否・"default" は無効値として明示的に弾く)
- [モードC] events の writer が script のみ + attempt/exit が数値: ✅ (`--argjson`)
- [モードC] --max-turns / token_ceiling / 停止イベント: ✅
- [モードC] トークン積算に cache_read/cache_creation を含む: ✅
- [モードC] error_max_turns を attempt 終了として扱う: ✅ (失敗扱いにしていない)
- [モードC] permission_denials を検査: ✅
- [モードC] permission_denials を**致命扱いしていない**: ✅ (「非致命・verify の exit code で判定する」と明記)
- [モードC] run_verify をコマンド置換で呼んでいない: ✅ (`if run_verify ...; then` の直接呼び出し。
  コメントに「$(run_verify ...) の形に戻すな」という注意書きのみで実装は正しい)
- [モードC] fingerprint が空のとき生出力へフォールバック: ✅ (`tail -40` フォールバックあり)
- [モードC] watchdog が plan mode でない + verdict は 1 行目 1 語判定: ✅
- [モードC] acceptance 段があり AC が gate に載っている: ✅ (`<id>-acceptance.sh` 規約あり)
- [モードC] DONE_IDS を events から seed: ✅
- [モードC] issue_deps が箇条書き限定 + 自己依存を preflight で検出: ✅
- [モードC] base_branch を config から解決: ✅ (`LOOP_BASE_BRANCH` → config → origin/HEAD → main → master)
- [共通]   allowed_tools が null でない: ✅ (echo/ls/cat/wc/test 等を含む明示リスト)
- [共通]   loop-issue に Bash(git \*) が無い: ✅ (個別 git サブコマンドのみ。復帰禁止コメントあり)
- [共通]   settings.json に permissions.deny がある: ✅ (git push/reset --hard/rebase/sudo/rm -rf/chmod -R/gh pr merge)
- [共通]   token_ceiling が実測に見合う (2M のままでない): ✅ (40,000,000 に設定済み)
- [モードC] CLI フラグ検証の記録 (progress): ✅ (claude 2.1.220 で `--help` 実測を記録)

## Step 3: schema / semantics
- /goal = セッションスコープ executor + done はトランスクリプト判定 → 客観 recheck 必須: ✅
- events 語彙 10 種 + fingerprint 定義: ✅
- board 状態機械: ✅
- _loop-config.json キーが README §2.3 と一致 (mode 含む): ✅
- モデル割当ポリシー (原則 1 行 + 表 + 根拠): ✅
- issue-slicing 7 基準: ✅
- 実行モード A/B/C 比較 + セッション境界の WHY + モードB/C 制約の明記: ✅
  (モードB: 同一チェックアウト共有・loop-guard.sh 素通り・既定直列・/goal 不可、
  モードC: `claude -p` が完全なセッションであり events が exit code から作られる、をいずれも明記)

## Step 4: coverage-map drift 監査
- procedural-docs-coverage: loop-engineering 登録済: ✅ (本検証で L1 の defer 分を新規登録)
- 未カバー (死蔵リスク) の節: なし
- drift (doc 新節がマップに無い): なし (初回は見出し語の表記揺れで 7 件の疑陽性が出たが、
  「節」列を doc の見出し全文に揃えて解消)
- 分類矛盾 (手続き→docs-only): なし

## Step 5: 相互参照
- Agent→Command (loop-watchdog→loop-issue): ⚠️ 部分的
  (loop-issue.md / loop-worker.md → loop-watchdog の**順方向**参照は明記されているが、
  loop-watchdog.md 自身は呼び出し元コマンド名を名指ししていない。契約は入力パラメータ
  [issue パス・events_path・test-runner 出力] で成立しており機能的な破綻はない → LOW)
- Hook→Stop (loop-guard 発火): ✅
- Command→Skill (loop-issue→workflow/grilling): ✅
- Command→Agent (loop-orchestrate→loop-worker/code-reviewer): ✅
- CLAUDE.md→docs (loop ポインタ節が実在 command のみ案内): ✅ (dangling 参照なし・19 行)
- skip 経路への dangling 参照: なし (L6 enabled のため対象外)

## 修正が必要な項目

### CRITICAL
なし

### HIGH
なし

### MEDIUM
なし

### LOW
- `loop-watchdog.md` の説明文に呼び出し元 (`loop-issue` / `loop-worker`) への明示的な言及がない。
  現状は入力契約 (issue パス・events_path 等) で機能しているため実害はないが、
  月次メンテ時に「誰が呼ぶエージェントか」を読み手が即座に把握できるよう、
  description か本文冒頭に 1 行「`loop-issue` (モードA/C) / `loop-worker` (モードB) から
  attempt 直後に呼ばれる」を足すと discoverability が上がる。

## 推奨される次のアクション
1. (任意・LOW) `loop-watchdog.md` に呼び出し元コマンド名を明記する 1 行を追記する。
2. 月次メンテナンスとして `/verify-loop-setup` を再実行し、coverage drift と
   skip 経路の取り残しを継続監視する。
3. 実運用に入ったら、最も安い issue 1 本を `parallel=1` で C モードから試し、
   docs に明記された「新しい実行モードを初めて使う時の基盤検証」を実施する。
