# 次セッション開始プロンプト — **タスク 2 の Loop 実行（モード C の初回）**

> 作成: 2026-09-14 / ⚠️★★★ **このメモを一次資料にしない。**
> ★ 一次は `.steering/20260914-mhd-feature-offline-tiers/_issue-plan.md`（**DAG / 交差表 / 実行前の前提**）／
> `issues/00X.md`（**AC と Stop Conditions の SSOT**）／ `docs/loop-engineering.md`（Loop の単一 SSOT）／
> `.steering/_template/loop-config.README.md`（★ **落とし穴集。必ず読む**）。

## §0 ⚠️★★★ まずこれを実行する

```bash
cd /c/GSE-prototype        # Windows は git-bash 必須
git switch docs/adr-030-stall-onset-definition && git log --oneline -3 | cat
cat .steering/20260914-mhd-feature-offline-tiers/_issue-plan.md | head -60
cat .steering/_template/loop-config.README.md | head -70       # ★ 落とし穴集
bash scripts/loop-run.sh .steering/20260914-mhd-feature-offline-tiers --dry-run
```

⚠️★★★ **`git switch main` しないこと** —— ★ **ADR-030 / 031 / 032 はこのブランチにしか無い**。
★ `_loop-config.json` の `base_branch` もこのブランチに pin してある（⚠️ main から切ると全 issue が即死する）。

⚠️★★★ **モデル**: 実行制御は **Sonnet**（★ `docs/loop-engineering.md` のモデル割当）。
⚠️ **応答は日本語で。**

---

## §1 ★ 前セッション（2026-09-14）で何が済んだか

| # | 済んだこと | 場所 |
|---|---|---|
| **1** | **2z（Loop 基盤整備）** —— worktree への必須 `permissions.deny` 7 件の注入 ＋ **毎 attempt の再保証** | `.steering/20260914-loop-foundation-worktree-deny/` |
| **2** | ⚠️★★★ **モード C が 1 issue 目で必ず死ぬ実バグを発見・修正した** | 下記 §2 |
| **3** | **タスク 2 の issue 分解**（縦切り 7 本 ＋ 各 `acceptance.sh` ＋ `_loop-config.json`） | `.steering/20260914-mhd-feature-offline-tiers/` |
| **4** | TASK-PRE（Codex の第二意見）を 1 回実行し、採否を記録した | `…/_codex-preplan.md` |

★ コミット 5 本（`56d4e58` / `a75bfda` / `29a19c1` / `e326c4f` / `365a8a6`）。⚠️ **push はしていない。**

---

## §2 ⚠️★★★ 実行前に知っておくこと（★ 前セッションで実測した罠）

1. ⚠️★★★ **`loop-run.sh` は `_loop-events.jsonl` を作ってから `loop-spawn.sh` を呼ぶ。**
   ★ そのため spawn 側の「作業ツリーに未コミット変更があります」判定に**自分で作ったファイルが当たり**、
   **1 issue 目から `worktree 生成に失敗` で全部死んでいた**（★ stub 実行で再現 → `.gitignore` に 3 件追加して解消）。
   → ⚠️ **`.steering/**/_loop-events.jsonl` 等を `.gitignore` から外さないこと。**
2. ⚠️★★★ **worktree の deny は attempt ごとに再検査される。**
   ★ 消されていたら events に `WARN: … permissions.deny が失われていた` が 1 行残り、再注入される。
   ⚠️ **再注入にも失敗したら `blocked` で止まる**（deny 無しでは起動しない）。
3. ⚠️★★★ **「注入されていること ≠ 発効していること」は未検証である。**
   ★ `claude -p` が worktree の deny を実際に読んで `git push` を拒むかは**まだ誰も確かめていない**。
   → ★ **001 を回したときに `permission_denials` と events を見て確かめる**（⚠️ 予測しない）。
4. ⚠️ `acceptance_template` は `loop-run.sh` に**読まれない**。★ 実体は
   `$TASK_DIR/issues/<id>-acceptance.sh` のハードコード（`loop-run.sh:235`）。
5. ⚠️ `--dry-run` で検証できるのは config / DAG まで。★ **権限・cwd 境界・hook 発火は観測できない**
   （★ SSOT 逐語・実測で 2 回空振り）。

---

## §3 ★ やること（★ この順で・⚠️ 飛ばさない）

### 3-1. ⚠️★★★ **まず 001 だけを単独で回す**

```bash
bash scripts/loop-run.sh .steering/20260914-mhd-feature-offline-tiers --issues 001
```

★ SSOT 逐語「**新しい実行モードを初めて使う時は、最も安い issue 1 本を `parallel=1` で回して基盤を検証する。**」

★ 001 が終わったら **events を人の目で読む**:

```bash
cat .steering/20260914-mhd-feature-offline-tiers/_loop-events.jsonl | jq -c .
```

⚠️ 見るべきもの:
- `permission_denials=` を含む行（★ **何が拒否されたか** ＝ `allowed_tools` の過不足）
- `WARN: … permissions.deny が失われていた`（★ worker が安全設定に触ったか）
- `issue_done` の前に `acceptance` 段が通っているか（⚠️ `verify` が緑でも AC 未充足なら止まる）

### 3-2. 残りを回す

```bash
bash scripts/loop-run.sh .steering/20260914-mhd-feature-offline-tiers
```

⚠️ **`--parallel` を上げない。**★ 交差表（`_issue-plan.md` §3）のとおり**並列可能な組は 1 つも無い**。

### 3-3. 監視

`/loop-status` が board の単一書き手。⚠️ **`issue_done` を自己申告で信じない** ——
★ `recheck` の 3 本（001 / 005 / 007）は watchdog の客観再検証を通る。

### 3-4. 全緑後

★ `code-reviewer` + `security-checker` を**並列**起動 → `/cross-review`（**2 巡**）→ retrospective。
⚠️ main へのマージは**研究者判断**。

---

## §4 ⚠️ 止まったときの読み方

| events の最終行 | 意味 | ★ 次の手 |
|---|---|---|
| `blocked` ＋ `worktree 生成に失敗` | ⚠️ dirty tree か同名 worktree | ★ `git status` を見る ／ `bash scripts/loop-spawn.sh --cleanup <id>` |
| `blocked` ＋ `permissions.deny を保証できない` | ⚠️ worker が settings を壊した | ★ `bash scripts/loop-worktree-deny.sh --verify <worktree>` で確認 |
| `no_progress_stop` | ★ 同一 fingerprint × 4 | ⚠️ **issue の切り方か AC が悪い。**★ 人が読む |
| `abandoned` ＋ `max_attempts 到達` | ★ 6 回で緑にならなかった | ⚠️ 粒度が大きすぎた ＝ **分解の失敗**。★ 分割を検討 |
| `blocked` ＋ `AC 未充足` | ★ watchdog が NG と判定 | ★ `acceptance.sh` の出力を読む |

⚠️★★★ **issue の `## Stop Conditions` に当たったら worker は止まる。**
★ そのときは**設計判断が要る**ということなので、⚠️ **Sonnet の実行セッションで決めない。**
→ ★ `/clear` して **Opus で裁定する**（★ 特に 004 の `undo`/`redo` と 005 の ADR 曖昧さ）。

---

## §5 ⚠️★★★ 絶対にやらないこと

1. ⚠️★★★ **`main` から worktree を切らない**（★ ADR がこのブランチにしか無い）。
2. ⚠️★★★ **`features.rs` / `engine.rs` / `loop_step.rs` を変更しない**（★ ADR-030 **D1**）。
3. ⚠️★★★ **`HMM_VERSION` を bump しない** / ゴールデン snapshot を再生成しない。
4. ⚠️★★★ **`undo` / `redo` / `key.mod` を実装しない** —— ★ **ADR-032 が Accepted になり、
   同意 §3 の改訂（M4）が通ってから**（⚠️ 研究者承認待ち）。
5. ⚠️★★★ **`schema_dto.rs` / `logger.rs` / `capabilities.rs` を触らない**（＝ 計器変更）。
6. ⚠️★★★ **`allowed_tools` を `null` にしない**（★ 無人実行がコード 0 行で即死する。実測 2 回・約 $11）。
7. ⚠️★★★ **`.gitignore` から Loop の実行時生成物を外さない**（★ §2-1）。
8. ⚠️ **`git add -A` / `git add <dir>` を使わない**（★ 作業ツリーに別ブランチの未コミット作業がある）。
9. ⚠️ **`--parallel` を上げない**（★ 交差表のとおり並列可能な組が無い）。

---

## §6 ⚠️ 触らない（★ 研究者の承認待ち）

| # | 何 | ★ 状態 |
|---|---|---|
| **A** | **ADR-030 / 031 / 032 を Accepted にするか** | ⚠️ 全部 Proposed |
| **B** | **O1 同意 §3 の改訂 3 点**（ADR-032 **M4**） | ⚠️ 承認待ち。★ 文案は M4 の囲みに置いてある |

---

## §7 ★ Loop の外に残っている宿題（⚠️ 本セッションでは裁かない）

- ⚠️★★★ **`capability matrix`**（ADR-032 **M7**）—— ★ **Loop に載せないと決めた**（研究者判断 2026-09-14）。
  ★ 範囲は `.steering/20260914-mhd-feature-offline-tiers/decisions.md` **判断 5**
  （schema 静的分析 ＋ 既存 fixture 13 本での実測 replay ＋ 起票 6 の既測結果の引用／⚠️ `OS × ライブ変換設定` で層別）。
  ⚠️ **これが閉じるまで ADR-032 の未決 ④ / ⑤ と起票 21（単独キー用の門）が開いたまま**残る。
- **起票 16 / 17 / 18 / 19 / 20 / 21 / 22 / 23**（→ `.steering/20260914-instrument-change-arbitration/blockers.md`）
- **起票 11**（ESM 監査 criterion。⚠️ ⓪〜④ が丸ごと未着手・④ から始めてはならない）
- **タスク 3**（leakage 防止・split 規律の SSOT 化）
- ⚠️ 未踏 詳細資料の 10 ページ規約を実測 ／ `gse-dataset` の schema 同期
- ⚠️ `docs/loop-engineering.md` の「注入 ≠ 発効」— ★ **`permission_mode` を `auto` /
  `bypassPermissions` へ昇格させたときに deny がどう評価されるかは未検証**（→ §2-3 で確かめる機会）
