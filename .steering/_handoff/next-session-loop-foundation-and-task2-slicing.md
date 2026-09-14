# 次セッション開始プロンプト — **2z（Loop 基盤整備）＋ タスク 2 の issue 分解**

> 作成: 2026-09-14 / ⚠️★★★ **このメモを一次資料にしない。**
> ★ 一次は `docs/loop-engineering.md`（**用語 / Done・Stop / budget / events 契約 / モデル割当の単一 SSOT**）／
> `.steering/_template/loop-config.README.md`（★ **落とし穴集。必ず読む**）／
> `docs/adr/ADR-030-stall-onset-and-decision-episode.md` **D10 / D11**（★ 作れる範囲の確定）／
> `docs/adr/ADR-032-instrument-change-arbitration.md` **D5 / §Migration M7**（★ `capability matrix`）／
> `.steering/_handoff/next-session-mhd-feature-redesign-ssot.md` **§8b / §8c**（★ 前提監査の実測と deny リストの実体）。

## §0 ⚠️★★★ まずこれを実行する

```bash
cd /c/GSE-prototype        # Windows は git-bash 必須
git switch docs/adr-030-stall-onset-definition && git log --oneline -3 | cat
cat .steering/_template/loop-config.README.md | head -60      # ★ 落とし穴集
cd src-tauri && cargo test --workspace 2>&1 | tail -3         # ★ ベースラインが緑か（⚠️ 予測しない）
```

⚠️★★★ **`git switch main` しないこと** —— ★ **ADR-030 / 031 / 032 はこのブランチにしか無い**
（★ **ADR-029 だけ 2026-09-14 に main へマージ・push 済み**・CI 緑）。

⚠️★★★ **モデル**: 2z は **Sonnet**／issue 分解は **Opus**（★ `docs/loop-engineering.md` のモデル割当）。
⚠️ **応答は日本語で。**

---

## §1 ★ なぜこの 2 つなのか（★ 研究者判断 2026-09-14）

★ **承認待ち（ADR の Accepted 化・同意 §3 の改訂）は研究者の判断**なので、
→ ★ **承認を待たずに走れるもののうち「今日の未決を最も多く閉じる経路」に入る。**

| ★ 閉じるもの | どこで |
|---|---|
| **④** IME の 9 候補の採否 | ★ `capability matrix`（ADR-032 **D5** が「先に測れ」と命じた） |
| **⑤** `esc_count` の要否 | ★ 同上 |
| **起票 21** 単独キー用の門 | ★ 同上（⚠️ `esc_count` の要否が決まらないと門の必要性も決まらない） |
| **起票 23** ① が `t0` の発火を動かすか | ★ `gse-replay` で比較（ADR-032 **M12**） |

⚠️★★★ **タスク 2 は `Loop Engineering モード C の初回`である**（★ 研究者判断 2026-09-13・判断 15）。
★ **Loop に載せるのはタスク 2 だけ**（⚠️ 裁定・契約文書は載せない）。

---

## §2 ★ 前半 = **2z（Loop 基盤整備）** —— ⚠️ **再導出しないこと**

★ **実体は `next-session-mhd-feature-redesign-ssot.md` §8c に完成形で置いてある**（★ JSON も理由も）。
⚠️ **ゼロから考え直さない。**

### ⚠️★★★ 何が欠けているか（★ 2026-09-13 実測）

| # | 事実 |
|---|---|
| 1 | ⚠️ 現行 `.claude/settings.json` の `permissions.deny` は **`chmod -R` / `sudo` の 2 件だけ** |
| 2 | ★ `loop-config.README.md` が必須とするのは **7 件**（★ 追加 5 件 = `git push` / `gh pr merge` / `git reset --hard` / `git rebase` / `rm -rf`） |
| 3 | ⚠️★★★ **deny を worktree へ入れる仕組みが無い**（★ `loop-spawn.sh` / `loop-run.sh` を grep して `settings` は **0 件**） |
| 4 | ★ 正しい置き場は **worktree の `.claude/settings.local.json`**（★ `.gitignore:46` で ignore 済み ＝ worktree ごとに別物にできる） |
| 5 | ⚠️★★★ **main checkout の `settings.json` に入れてはならない** —— ★ **対話セッションでも `git push` が塞がれる** |

### ★ やること

1. ★ `loop-run.sh`（または `loop-spawn.sh`）が **worktree 作成直後に `.claude/settings.local.json` を書く**工程を足す。
2. ⚠️ **既存の `settings.local.json` があれば上書きせず `deny` 配列へマージする**（★ 他のキーを消さない）。
3. ★ **検査を対で置く**（⚠️ `verify-before-claiming` ルール 6）——
   ⚠️★★★ **「正常なら緑」だけ試さない。★ 正常 / 不在 / 壊れている の 3 状態**を作って通す（ルール 5b）。

> ⚠️★★★ **なぜ安全装置が先なのか** —— ★ `loop-config.README.md` 逐語:
> 「実測 (claude 2.1.220) では最初の 2 回の無人実行が **コード 0 行のまま終了**した (約 $11 を消費)。
> 対話セッション (モードA/B) では人間が承認するので顕在化せず、**無人のモードC で初めて即死する**。」
> ★ 原因は `allowed_tools` を `null` にしたこと（⚠️ `acceptEdits` は **Edit/Write を通すだけで Bash を通さない**）。
> → ★ **テンプレートの既定リストは修正済み。⚠️ `null` に戻さない。**

---

## §3 ★ 後半 = **タスク 2 の issue 分解**（`grill` → `to-prd` → `to-issues`）

### ⚠️★★★ **縦切りの目安は 5 本ではなく 7 本である**（★ 2026-09-14 に是正）

⚠️ `next-session-mhd-feature-redesign-ssot.md` **§8b の表は 5 本（T0 / T1a / T1b / T1d / Q）**だが、
★ **これは `ADR-030 D11` の *初版* が `T1c` を丸ごと「要」に送っていた時点の記述である。**
→ ★ **その後 `code-reviewer` の指摘で「`T1c` のうち 5 項目は計器変更不要」に直っている**（D11 の表）。
⚠️ かつ **2026-09-14 に `capability matrix` が加わった**（ADR-032 M7）。

| issue 候補 | 中身 | ★ acceptance の考え方 |
|---|---|---|
| **T0** | keys / delete / paste / mean IKI / 単純 pause / net production | ★ 出力に当該フィールドが出ること ＋ 手計算との一致 |
| **T1a** | pause p50/p90/max・CV・個人相対 surprise | ★ 同上 ＋ 分布統計の境界値 |
| **T1b** | 直前/直後 `KeyCategory`・Space/Enter/文末句読点・IME 局面 | ★ `sentence_punctuation` が分離されていること（⚠️ **投資順序で最有力**） |
| ★ **T1c**（**2026-09-14 追加**） | delete run / rewrite / 再削除 / **loop depth** / 局所 recurrence | ⚠️★★★ **`undo`/`redo` 往復は入れない**（★ ADR-032 D1 が Accepted になるまで計器が無い） |
| **T1d** | pause 後の生成/削除/移動・再停止時間・安定生成時間 | ⚠️★★★ **タスク 1（`stall onset`）の定義に依存** → ★ `## Dependencies` で直列化 |
| **Q** | capability / missingness reason / logger・IME health / observability mask | ⚠️★★★ **状態特徴にしない**（`survey:194` 逐語「**欠測を 0 として入力せず、推論の抑制・abstention に使う**」） |
| ★ **capability matrix**（**2026-09-14 追加**） | ★ 現行 schema だけで **T0/T1 のどこまで offline replay できるか**の実測表（`.idea/survey §11-2`） | ⚠️★★★ **`OS × ライブ変換設定` で層別する**（★ ADR-032 D5・⚠️ 1 つの表に畳まない）／★ **IME の 9 候補**と **`navigation-to-edit lag`** の可否を出す |

### ⚠️ 分解の規律（★ `issue-slicing` skill の 7 基準）

- ⚠️★★★ **Tier ごとの横切りにしない**（★ 基準 1「**層別の横切り分割は禁止**」）。★ **特徴群ごとに縦に割る。**
- ★ **Allowed Files 非交差**（基準 3）／ **AC ↔ test 対応**（基準 4）／ **DAG**（基準 6）／ **単独 merge 可**（基準 7）。
- ⚠️★★★ **`cargo test` が無条件に緑になる issue では AC 未充足のまま `issue_done` になる**（★ `loop-run.sh` のコメント逐語）
  → ★ **`acceptance.sh` は「新特徴が実際に出力に出ていること」を検査する。**

### ⚠️★★★ 分解が終わったら **`/clear` して別セッションで実行する**

★ CLAUDE.md 逐語「**issue 分解と loop 実行は別セッション**」「*issue ファイルだけを読んで実行が成立しないなら、分解が失敗している*」。

---

## §4 ⚠️★★★ 絶対にやらないこと

1. ⚠️★★★ **`main checkout` の `.claude/settings.json` に `git push` の deny を入れない**（★ 対話セッションが壊れる）。
2. ⚠️★★★ **`allowed_tools` を `null` にしない**（★ 無人実行が**コード 0 行で即死**する。実測 2 回・約 $11）。
3. ⚠️★★★ **`undo`/`redo` / `key.mod` を実装しない** —— ★ **ADR-032 が Accepted になってから**（M5）。
4. ⚠️★★★ **`HMM_VERSION` を bump しない** / **`docs/preregistration-v0.3.md` を書き換えない**。
5. ⚠️★★★ **ADR-030 D10 / D11 を蒸し返さない**（★ Tier 枠・投資順序・仕切りは accept 済み）。
6. ⚠️★★★ **O1 を配り始めない。**★ 境界は「**配布**」（ADR-014 判断 4）。
7. ⚠️★★★ **`git add -A` / `git add <dir>` を使わない**（★ 作業ツリーに別ブランチの未コミット作業がある）。
8. ⚠️ **`--dry-run` で基盤を検証したことにしない** —— ★ SSOT 逐語「**権限・cwd 境界・hook 発火・契約の二重定義が観測できない**」。

---

## §5 ⚠️ 触らない（★ 研究者の承認待ち）

| # | 何 | ★ 状態 |
|---|---|---|
| **A** | **ADR-030 / 031 / 032 を Accepted にするか** | ⚠️ 全部 Proposed（★ 032 は **D1 / D9 の 2 本の解禁**を持つ） |
| **B** | **O1 同意 §3 の改訂 3 点**（ADR-032 **M4**） | ⚠️ 承認待ち。★ 文案は M4 の囲みに置いてある |

⚠️★★★ **B が通るまで実装（M5）も配布も動かない。** ★ ただし **ADR-031 M5 / M6 の配線の実装は進めてよい**
（★ 束ねたのは **配布と同意改訂**であって実装ではない —— ADR-032 D8）。

---

## §6 ⚠️ 実行時に効く前提

- ⚠️★★★ **`Cargo.toml` は repo 直下に無い（`src-tauri/` にある）。**
  ★ repo 直下から叩くなら `--manifest-path src-tauri/Cargo.toml`。
- ⚠️ Hook はすべて bash 前提。Windows では **git-bash 必須**。
- ★ `verify` は **固定 3 種**（`test` → `typecheck` → `lint` の順に `loop-run.sh:220` が読む）。
  ⚠️★★★ **テンプレの `pytest -q` をそのまま使わない**（★ GSE の実体へ pin する）。
- ★ `events_path` は **main checkout の絶対パス**。★ `mode: "C"` ／ ⚠️ **`budget.parallel: 1`（初回）**。
- ⚠️ ゴールデン replay は `session hmm_version = 0.2.0, current engine = 0.5.0` の**警告が出るが exit 0 / 15 一致**が
  **既存のベースライン**である。⚠️ **「無視してよい」と断定しない。**
- ⚠️ `/cross-review` は **2 巡**（★ 2 巡目 = **自分が足した規則の境界条件**。★ 2026-09-14 はそちらが重かった）。
  ★ 予算は `.codex/budget.json`（日次 300k）。
- コミット: `[type]([scope]): [説明]` ＋ 本文 ＋ `Refs: .steering/[YYYYMMDD]-[task-name]/`

## §7 ★ 併走している未了（⚠️ 本セッションでは裁かない）

- **起票 16 / 17 / 18**（`t0` の束ね方 ／ 30 秒窓の分割方式 ／ 反復 × 競合の同時作法）
- **起票 19 / 20 / 21 / 22 / 23**（★ 2026-09-14 起票。→ `.steering/20260914-instrument-change-arbitration/blockers.md`）
- ⚠️ 未踏 詳細資料の 10 ページ規約を Google ドキュメントで実測 ／ `gse-dataset` の schema 同期
- ⚠️ **タスク 3**（leakage 防止・split 規律の SSOT 化）—— ★ **本セッションと並行可**だが、**同時にやらない**
