# Loop 基盤の穴を塞ぐ（起票 3 / 10 ＋ `issue_ids()` の Status 無視）

## 背景

★ タスク 2（`.steering/20260914-mhd-feature-offline-tiers/`）の**再開順は研究者が確定済み**
（同 `decisions.md` 判断 25）。その **② が本タスク**である。

⚠️ 判断 25 #4 の逐語は **「次に Loop を回す前に直す」**。
★ ④ の issue 004 / 006 は Loop で回す前提なので、②を飛ばせない。

本タスクが塞ぐのは 3 件（★ すべて 2026-09-20 に一次で再確認した）:

### (1) 起票 10 — ⚠️★★★ worker が worktree 隔離を自分で外せた（★ 実測済みの実害）

★ reflog の実測（2026-09-15・issue 004 の attempt）:

```text
92fd22f HEAD@{0}: checkout: moving from loop/004-issue to main
bd921b6 HEAD@{1}: commit: docs(engine): issue 004 … 実装せず停止し、定義未確定を起票する
```

→ ⚠️ `git worktree list` が `C:/wt/GSE-prototype-004-issue 92fd22f [main]` を示す状態になった。

**なぜ通ったか**（★ 一次で確認）:

- ★ 注入される必須 deny は **7 件で実在する**（`scripts/loop-worktree-deny.sh:43`）。
  ⚠️ ただし **`git checkout` / `git switch` は 0 件**。
- ⚠️ 追跡済み `.claude/settings.json:113-116` の `allow` に **`Bash(git *)`** が在る。
  → ★ **`git checkout` は明示的に許可されている。**

⚠️★★★ **今回の実害は「無い」が、それは偶然である**（起票 10 逐語）:
worker は commit **後**に checkout したので作業は残った。
⚠️ **未コミットのまま checkout していたら失われていた**（★ 001 / 002 / 003 の worker は
**いずれも未コミットのまま終わっている**）。

### (2) 起票 3 — ⚠️ `permission_denials` の内訳が説明できない

- ★ Loop モード C は `permission_denials=N` を **件数だけ** events に残す。
  issue 002 の 6 attempt で **1 / 2 / 5 / 10 件**が記録されたが、⚠️ **何が拒否されたか分からない**。
- ⚠️ それまでは「非致命」という扱いの**妥当性を確かめていないまま使っている**。

### (3) 申し送り — `issue_ids()` が `## Status` を読まない

★ `scripts/loop-run.sh:150-152`（2026-09-20 に逐語で再確認）:

```bash
issue_ids() {
  ls "$TASK_DIR"/issues/*.md 2>/dev/null | while read -r f; do basename "$f" .md; done | sort
}
```

→ ⚠️ `--issues` を付けずに回すと **`blocked` の 004 / 006 も走る**。
★ 実績: **004 は attempt 1〜3 を失った**（起票 9 と同型の空回り）。

## ゴール

⚠️★★★ **「deny を足した」で終わらせない。** 次の 3 つが**実測**で言えること:

1. ★ worktree の中で `git checkout main` が **拒否される**（★ 拒否されない側も 1 回撮って対照にする）。
2. ★ worktree の HEAD が `loop/<id>-` から外れた attempt が **`blocked` になる**（fail-closed）。
3. ★ `blocked` の issue が **既定の実行対象から外れる**（⚠️ `--issues` で明示すれば回せる）。

Done は `bash scripts/loop-run-guard-test.sh` と `bash scripts/loop-worktree-deny-test.sh` が
**ともに exit 0**、かつ実測ログが `measurements.md` に残っていること。

## スコープ

### 含むもの

- `scripts/loop-run.sh` — ブランチ検査 / `permission_denials` の内訳保存 / Status フィルタ
- `scripts/loop-worktree-deny.sh` — `DENY_REQUIRED` に `Bash(git checkout:*)` / `Bash(git switch:*)` を追加（7 → 9 件）
- `.steering/_template/loop-config.README.md` — ⚠️ **契約の二重定義**なので同時に更新する
- `scripts/loop-worktree-deny-test.sh` — 件数の期待値（7 → 9）
- `scripts/loop-run-guard-test.sh` — ★ **新規**。ブランチ検査と Status フィルタの 3 状態検査
- `.claude/commands/loop-issue.md` — ★「worker は commit してから終わる」を契約に明記（⚠️ 文章のみ・機械強制しない）
- `docs/loop-engineering.md` — ★「7 件は多層防御であって境界ではない」節を**実測結果**で更新し、
  ★ **ブランチ検査が境界である**ことを書く
- `.gitignore` — `_loop-artifacts/`
- ★ 実測ログ（`measurements.md`）

### 含まないもの

- ⚠️ 追跡済み `.claude/settings.json` の `permissions.allow` は**触らない**（★ 判断 1 で却下）
- ⚠️ 起票 4（`preflight_dag` の文言・merge 済み依存）— ★ 再開順に入っていない
- ⚠️ 封筒 issue（起票 2 / 5）— ★ 再開順 ③（次タスク）
- ⚠️ issue 004 / 006 の実装 — ★ 再開順 ④
- ⚠️ ADR 本文・事前登録 `§3`・被験者向け文書の書き換え
- ⚠️ 「未コミットで終わった」ことを**失敗にする**検査（★ 判断 5 で却下）
- ⚠️ `_loop-config.json` の `allowed_tools` の変更（★ `git checkout` は元から入っていない）

## 受け入れ条件

- [ ] **(1) は実測で示す** — ⚠️ 「deny を足した」で終わらせない。
      ★ worktree の中で実際に `git checkout main` を試し、**拒否されること**を確かめる
      （★ **成功してしまう側も 1 回撮る**）。
- [ ] **ブランチ検査**は「worktree の HEAD が `loop/<id>-` であること」を見る
      （⚠️ 外れていたら events に残して**失敗にする**）。
- [ ] **(3) は 3 状態で実測** — `blocked` を含む task で
      (a) 既定実行 / (b) `--issues` で明示 / (c) `## Status` 行が無い issue、の挙動をそれぞれ確かめて書く。
- [ ] ⚠️ **検査が「見ていないもの」を検査自身のコメントに書く**
      （★ deny は**境界ではなく多層防御**で、綴り違いの迂回は残る —— `docs/loop-engineering.md` の逐語）。
- [ ] `decisions.md` に判断を残す。
      ★ `.steering/20260914-mhd-feature-offline-tiers/blockers.md` の起票 3 / 10 を**閉じる**（⚠️ 消さない）。
- [ ] `bash scripts/loop-worktree-deny-test.sh` が exit 0（★ 9 件へ更新後）
- [ ] `bash scripts/loop-run-guard-test.sh` が exit 0（★ 新規）
- [ ] ⚠️ `tr -cd '\r' | wc -c` が **0**（★ CRLF 混入なし）

## 関連ドキュメント

- `docs/loop-engineering.md` — ★ 用語 / Done・Stop / budget / モデル割当の SSOT
- `.steering/_template/loop-config.README.md` — ★ 必須 deny の逐語リスト（**契約の二重定義**）
- `.steering/20260914-mhd-feature-offline-tiers/blockers.md` — 起票 3 / 10
- `.steering/20260914-mhd-feature-offline-tiers/decisions.md` — 判断 25（再開順）/ 判断 26（申し送り）
- `.steering/20260914-loop-foundation-worktree-deny/` — ★ 注入の仕組みを入れた前タスク

## 運用メモ

- **/reimagine 適用: No**
- **理由**: ★ 対策の形は grill で確定済み（判断 1〜5）であり、複数案の比較は済んでいる。
  ⚠️ アーキテクチャの再発明ではなく、**既存スクリプトへの検査の追加**である。
