---
description: >
  Loop の events を折り畳んで _loop-board.md を再描画するダッシュボード。
  人間の「見る画面」。繰り返し実行可能で /loop 30s /loop-status に載る。
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(git worktree list), Bash(gh pr list *), Bash(date *), Bash(cat *), Bash(ls *)
---

# /loop-status — Loop Board 再描画 (ダッシュボード)

これは **あなた (人間) の監視画面**。一目で状況が分かること (glanceable) を最優先し、
状態は emoji で表す。events (真実源) を折り畳んで board を丸ごと再生成する。
**単一書き手**: このコマンドだけが `_loop-board.md` を書く。worker は書かない。

## フロー

### 1. アクティブなタスク dir を特定
```bash
# .steering/ 直下で最新の [YYYYMMDD]-[task]/ を探す
ls -dt .steering/[0-9]*-*/ 2>/dev/null | head -1
```
複数候補があれば `_loop-events.jsonl` が最も新しく更新されたものを採用。
見つからなければ「アクティブなタスクがありません」と表示して終了。

### 2. config と events を読む
```bash
cat .steering/<task>/_loop-config.json    # task 名 / budget / events_path
cat .steering/<task>/_loop-events.jsonl   # append-only ログ (全行)
```
`_loop-events.jsonl` が空/不在なら board は全 issue を `⏳ queued` として描く。

### 3. worktree と PR の実状を取る
```bash
git worktree list
gh pr list --state all 2>/dev/null || echo "GH_ABSENT"   # gh が無ければ PR 列は –
```

### 4. events を issue ごとの最新状態に折り畳む
- issue 番号でグルーピングし、`ts` 昇順で最後の event を「現在状態」とする。
- event → 状態 emoji の対応:
  - `attempt_start` → 🔄 running (phase=execute)
  - `test_pass` → verifying/✅ 方向、`issue_done` → ✅ done (PR 反映)
  - `test_fail / typecheck_fail / lint_fail / acceptance_fail / uncommitted` → 🔄 running (verify で ✗、失敗回数を括弧表示。`uncommitted` = 緑だが未コミット／コミット 0 件)
  - `no_progress_stop / blocked / scope_violation` → ⛔ blocked (note に理由)
  - `abandoned` → abandoned
  - event 無し → ⏳ queued
- `try` = その issue の `attempt` 最大値。`verify` 列は test✓/✗・tc・lint を要約。
- **fingerprint は数えない** (loop-guard.sh の責務)。失敗回数の括弧表示のみ。

### 5. 進捗サマリ行と heartbeat を計算
```bash
date -u +%H:%M      # 現在時刻 (UTC)。events の ts も UTC(...Z) なので必ず -u で揃える
date -u +%s         # 差分計算用の epoch 秒 (UTC)
```
- 進捗行: `進捗 X/N done · 🔄R running · ⛔B blocked · tokens ?/ceiling`。
- heartbeat: 最新 event の `ts`(UTC) を epoch 秒に直し、`date -u +%s` との差から `(N分前)` を出す。
  表示時刻も `updated HH:MM` は **UTC** で出す (events が UTC のためローカル時刻と混ぜない)。
  events が古いほど「動いていない」ことが一目で分かる。
  > 時刻は UTC/ローカルを混在させないこと。混ぜると N分前 がタイムゾーン分ズレる。

### 6. _loop-board.md を丸ごと再描画 (Write で上書き)
README §2.5 のテンプレに従う:
```markdown
# Loop Board — <task>   ⏱ updated HH:MM (N分前)
進捗 X/N done · 🔄R running · ⛔B blocked · tokens ?/ceiling

| # | issue | 状態 | phase | try | verify | branch | note | PR |
|---|-------|------|-------|-----|--------|--------|------|----|
| ... 各 issue 1 行 ... |
```
状態機械: `queued(⏳) → running(🔄) → verifying → review → done(✅)` / `blocked(⛔)` / `abandoned`。

### 7. board を stdout にも出す
ファイル更新後、同じ内容を**画面にも表示**する (端末で即座に見えるように)。

## 運用メモ
- **繰り返し実行前提**。`/loop 30s /loop-status` で 30 秒ごとに自動再描画すると監視画面になる。
- board は派生ビュー。壊れても events から**毎回再生成**されるので安全。
- 単一書き手を破らない: worker からこのコマンドを呼ばない。
