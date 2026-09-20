# 次セッション — Loop 基盤の修正（★ タスク 2 の再開順 ②）

> 作成: 2026-09-20。⚠️★★★ **このメモを一次資料にしない。**
> ★ 一次は `.steering/20260914-mhd-feature-offline-tiers/decisions.md`（**判断 25 の再開順 / 判断 26**）／
> 同 `blockers.md`（**起票 3 / 10**）／ `scripts/loop-run.sh` / `scripts/loop-worktree-deny.sh` /
> `.claude/settings.json` / `docs/loop-engineering.md`。

## §0 打ち込む用（★ 新しいセッションにこのまま貼る）

```
.steering/_handoff/next-session-loop-foundation-fixes.md を読んで、Loop 基盤の穴（起票 3 / 10 ＋ issue_ids の Status 無視）を塞いでください。
まず /start-task を起動し、grill で「どこまでを境界として強制し、どこを多層防御に留めるか」を確定してから進めてください。
状態は一次（scripts/loop-run.sh・loop-worktree-deny.sh・.claude/settings.json の実物と、reflog / events の実測）で確かめ直すこと。台帳も引き継ぎも未検証メモとして扱う。
⚠️ 研究者判断 2026-09-18（判断 25 #4）の逐語は「次に Loop を回す前に直す」です。ここを飛ばして 004 / 006 に入らないでください。
設計判断は Opus。サブエージェントは既定 sonnet、レビューとセキュリティだけ opus（model を毎回明示・入れ子禁止）。
応答は日本語。git add -A / git add <dir> は使わない。.codex/budget.json を git checkout -- で戻さない。
```

## §1 ⚠️ なぜこれが次なのか（★ 一次で確かめた事実）

★ タスク 2（`20260914-mhd-feature-offline-tiers`）の**再開順は研究者が確定済み**（判断 25）:

```
① 理論レビュー  ✅ 完了（.steering/20260918-theory-critical-review/・判断 26 で 004 / 006 へ算出式を転記）
② Loop 基盤の修正（起票 3 / 10）   ← ★ ここ
③ 封筒 issue（起票 2 / 5）
④ 004（T1c）/ 006（T1d）
⑤ capability matrix（ADR-032 M7）
⑥ P1 前: 事前宣言文書 ＋ CLI 注入 ＋ 両極（ポインタ・修飾キー）
```

⚠️ 判断 25 #4 の逐語は **「次に Loop を回す前に直す」**。★ ④ は Loop で回す前提なので、②を飛ばせない。

## §2 ★ 対象（★ 3 件。すべて 2026-09-20 に一次で再確認した）

### (1) 起票 10 —— ⚠️★★★ **worker が worktree 隔離を自分で外せる**（実測済みの実害）

★ reflog の実測（2026-09-15・issue 004 の attempt）:

```text
92fd22f HEAD@{0}: checkout: moving from loop/004-issue to main
bd921b6 HEAD@{1}: commit: docs(engine): issue 004 … 実装せず停止し、定義未確定を起票する
```

→ ⚠️ `git worktree list` が `C:/wt/GSE-prototype-004-issue 92fd22f [main]` を示す状態になった。

**なぜ通ったか（★ 2026-09-20 に一次で再確認）**:

- ★ 注入される必須 deny は **7 件で実在する**（`scripts/loop-worktree-deny.sh:43`）:
  `Bash(git push:*)` / `Bash(gh pr merge:*)` / `Bash(git reset --hard:*)` / `Bash(git rebase:*)` /
  `Bash(sudo:*)` / `Bash(rm -rf:*)` / `Bash(chmod -R:*)`
- ⚠️ **`git checkout` / `git switch` は 0 件**（同ファイルを grep して確認）。
- ⚠️ 追跡済み `.claude/settings.json:114-115` の `allow` に **`Bash(git *)` と `Bash(gh *)`** が在る。
  → ★ **`git checkout` は明示的に許可されている。**

⚠️★★★ **引き継ぎメモの「必須 deny が 5 件欠けている」は陳腐化している**
（★ `20260914-loop-foundation-worktree-deny/` で注入自体は入った）。**欠けているのは件数ではなく `git checkout` の行**である。

**★ 判断 25 #4 が名指しした対策**: **ブランチ検査** ＋ **worktree 内の `git checkout` / `git switch` の遮断**。

### (2) 起票 3 —— ⚠️ `permission_denials` の内訳が説明できない

- ★ Loop モード C は `permission_denials=N` を **件数だけ** events に残す。
  issue 002 の 6 attempt で **1 / 2 / 5 / 10 件**が記録されたが、⚠️ **何が拒否されたか分からない**。
- ★ 次にやること: `scripts/loop-run.sh:342` 付近の `res` を `WORK_TMP` に保存する改修。
- ⚠️ worker の transcript は `~/.claude/projects/C--wt-GSE-prototype-<id>-issue/*.jsonl` に残る。
- ⚠️ それまでは「非致命」という扱いの**妥当性を確かめていないまま使っている**と承知する。

### (3) ★ 申し送り —— `issue_ids()` が `## Status` を読まない

★ `scripts/loop-run.sh:150-152`（2026-09-20 に逐語で再確認）:

```bash
issue_ids() {
  ls "$TASK_DIR"/issues/*.md 2>/dev/null | while read -r f; do basename "$f" .md; done | sort
}
```

→ ⚠️ `--issues` を付けずに回すと **`blocked` の 004 / 006 も走る**。
★ 実績: **004 は attempt 1〜3 を失った**（起票 9 と同型の空回り）。
→ ★ `blocked` を**既定の選択から外す**（⚠️ 明示指定すれば回せる、は残してよい）。

## §3 ★ 受け入れ条件（★ このプロジェクトで 4 回踏んだ型を避ける）

- [ ] **(1) は実測で示す**: ⚠️ 「deny を足した」で終わらせない。★ **worktree の中で実際に
      `git checkout main` を試し、拒否されること**を確かめる（★ 成功してしまう側も 1 回撮る）。
- [ ] **ブランチ検査**は「attempt の終了時に worktree の HEAD が `loop/<id>-issue` であること」を見る
      （⚠️ 外れていたら events に残して**失敗にする**）。
- [ ] **(3) は 3 状態で実測**: `blocked` を含む task で (a) 既定実行 / (b) `--issues` で明示 /
      (c) `Status` 行が無い issue、の挙動をそれぞれ確かめて書く。
- [ ] ⚠️ **検査が「見ていないもの」を検査自身のコメントに書く**（★ deny は**境界ではなく多層防御**で、
      綴り違いの迂回は残る —— `docs/loop-engineering.md` の逐語）。
- [ ] `decisions.md` に判断を残す。★ `blockers.md` の起票 3 / 10 を**閉じる**（⚠️ 消さない）。

## §4 ⚠️ 先に確かめること（★ 推測で始めない）

1. `scripts/loop-worktree-deny.sh` の `DENY_REQUIRED`（`:43`）と `ensure_deny`（`loop-run.sh:121`）の実体。
2. `.claude/settings.json` の `permissions.allow` / `deny`（⚠️ **allow の広さが deny を無効化する**）。
3. `_loop-config.json` の `allowed_tools`（★ ⚠️ `null` にすると worker が 0 行で死ぬ —— 実測 2 回・約 $11）。
4. `docs/loop-engineering.md` の「7 件は多層防御であって境界ではない」節（★ **本件はその逐語の実証**）。

## §5 ★ 並行して残っているもの（⚠️ 本タスクでは触らない）

| # | 何 | 状態 |
|---|---|---|
| A | **004（T1c）/ 006（T1d）** | 🔴 `blocked`。★ 算出式は判断 26 で確定・転記済み。⚠️ 残るのは**実装フェーズの設計議論**（004: U1〜U4 ／ 006: V1〜V5）。★ **「未裁定」の語が 1 つでも残っていれば着手しない**（`grep -c 未裁定`） |
| B | 封筒 issue（起票 2 / 5） | ★ 再開順 ③。出力を `{ provenance, config, rows }` に。⚠️ **全 acceptance の前提（配列）を 1 度だけ書き換える** |
| C | 起票 7（`T1a` の分位点が構造的に退化） | ⚠️ **開いたまま**。★ 判断 25 #11 で「事前宣言と一緒に決める」 |
| D | G1 収集開始ゲートの赤 6 件 | ⚠️ **研究者判断 5 件が律速**。→ `next-session-after-g1-collection-gate.md` |
| E | ブランチ `feature/g1-collection-readiness-gate`（8 コミット） | ⚠️ **未 push / 未 PR**。★ 研究者の指示で「**次セッション終了後に push → PR → CI 緑 → merge**」 |

## §6 ⚠️ 守ること

- ★ `/start-task` から。判断は `decisions.md`。`verify-before-claiming`（状態の断定は一次で）。
- ⚠️ ADR 本文・事前登録 `§3`・被験者向け文書は書き換えない。
- ★ 完了時に `code-reviewer` ＋ `security-checker`（並列・opus）と `/cross-review` **2 巡**（パス限定）。
  ⚠️ レビュー系 subagent には「コミット済みの範囲だけ・作業ツリーを触らない・隔離クローンを作らない・
  長い selftest は回さない・N 分で結論」を明記する。
- ⚠️ `git add -A` / `git add <dir>` 禁止。`.codex/budget.json` を `git checkout --` で戻さない。
- ⚠️★★ **python でスクリプトを書き戻さない**（★ Windows で **CRLF が混入**する。2026-09-20 に実測）。
  → `Write` / `Edit` を使い、`tr -cd '\r' | wc -c` が 0 であることを確認する。
- ★ コミット: `[type]([scope]): [説明]` ＋ 本文 ＋ `Refs:` ＋
  `Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>`。
