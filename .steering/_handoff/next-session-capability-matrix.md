# 次セッション — 起票 18（Loop の `--cleanup`）→ `capability matrix`（ADR-032 M7）★ タスク 2 の再開順 ⑤

> 作成: 2026-09-21。⚠️★★★ **このメモを一次資料にしない。**
> ★ 一次は `docs/adr/ADR-032-instrument-change-arbitration.md`（**D5 / M7 / M11 / §Consequences**）／
> `.steering/20260914-mhd-feature-offline-tiers/decisions.md`（**判断 4 / 判断 5 / 判断 25 #16**）／
> `.steering/20260914-instrument-change-arbitration/blockers.md`（**起票 6 / 起票 21**）／
> `scripts/loop-spawn.sh`（起票 18 の対象）。

## §0 打ち込む用（★ 新しいセッションにこのまま貼る）

```
.steering/_handoff/next-session-capability-matrix.md を読んで、次の 2 本をこの順で実施してください。

【1 本目・小】起票 18: scripts/loop-spawn.sh の --cleanup が、逸脱した worktree を撤去できないのに
「完了」と報告する。★ worktree をブランチ名だけで引いているのが原因（loop-spawn.sh:57）。
パスでも引くようにし、撤去できたことを確かめてから完了と書くよう直す。
⚠️ 一次は .steering/20260914-mhd-feature-offline-tiers/blockers.md の「起票 18」。

【2 本目・本題】capability matrix（ADR-032 M7）: 現行 schema だけで T0/T1 のどこまで offline replay
できるかを OS × ライブ変換設定 で層別した表を docs/architecture/ に作る。
⚠️ Loop に載せない（判断 4）。⚠️ 実証範囲は「現行 schema の静的分析 ＋ 既存 fixture の実測 replay ＋
起票 6 の既測結果の引用」に限る（判断 5）。★ 合成 fixture 上の判定であることを表に明記し、
実データでの再判定が要る項目は「要再判定」と書く（⚠️「作れる」と断定しない）。
★ 表が閉じたら ADR-032 の未決 ④ / ⑤ と、M11（単独キー用の門）を裁定する。

状態は一次（ADR-032 本文・decisions.md・scripts/）で確かめ直すこと。台帳も引継ぎも未検証メモとして扱う。
設計判断は Opus。サブエージェントは既定 sonnet、レビューとセキュリティだけ opus（model を毎回明示・入れ子禁止）。
応答は日本語。git add -A / git add <dir> は使わない。.codex/budget.json を git checkout -- で戻さない。
```

## §1 ⚠️ なぜこれが次なのか（★ 2026-09-21 に一次で確かめた）

★ タスク 2 の**再開順は研究者が確定済み**（`.steering/20260914-mhd-feature-offline-tiers/decisions.md` 判断 25）:

```
① 理論レビュー        ✅ 完了（.steering/20260918-theory-critical-review/）
② Loop 基盤の修正     ✅ 完了（.steering/20260920-loop-foundation-fixes/）
③ 封筒 issue（起票 2 / 5）  ✅ 完了（.steering/20260920-envelope-issues/）
④ 004（T1c）/ 006（T1d）    ✅ **完了**（.steering/20260920-issues-004-006/・PR #215 は 2026-09-21 に merge 済み）
⑤ capability matrix（ADR-032 M7）  ← ★ ここ
⑥ P1 前: 事前宣言文書 ＋ CLI 注入 ＋ 両極（ポインタ・修飾キー）
```

★ ④ の結果（`4fa0d15` が main）:
`cargo test --workspace` **775 passed** ／ acceptance **001〜008 ＋ envelope すべて OK** ／
CI（win / mac の `check` ＋ `frontend-check`）**すべて pass**。

## §2 ★ 1 本目（小）—— 起票 18: `loop-spawn.sh --cleanup` の嘘の完了報告

⚠️ **なぜここで先に片付けるか**: `capability matrix` は **Loop に載せない**（判断 4）ので ⑤ には要らない。
★ しかし **⑥ を issue に切って Loop で回す回**には要る。判断 25 #4 の先例
（逐語「Loop 基盤の穴は**次に Loop を回す前に直す**」）と同型なので、⑥ の直前に回すより
**独立した小タスクとして先に潰しておくほうが安い**（★ ⑤ の文脈と混ざらない）。

- **一次**: `.steering/20260914-mhd-feature-offline-tiers/blockers.md` の「起票 18」（★ 実測ログ付き）
- **対象**: `scripts/loop-spawn.sh`（★ `:57` の worktree 引き／ `--cleanup` の完了報告）
- **直し方（起票 18 が書いている 2 点）**:
  1. ★ worktree を **パス（`../wt/<repo>-<id>-<short>`）でも引く**。⚠️ ブランチ名だけに依存させない。
  2. ★ **撤去できたことを確かめてから「完了」と書く**
     （★ 同ファイルの `abort_worktree` は既にこの作法を持っている。⚠️ `--cleanup` 側だけが外れている）
- ⚠️ **再現手順は起票 18 に逐語で載っている**（`--cleanup zzz` → `git worktree list` に残る）。
  ★ **直す前に再現させること**（⚠️ 再現しないまま直して「直った」と書かない）。
- ★ 検証には `bash scripts/check-shell-portability.sh` も回す（⚠️ `$name` の直後に多バイト文字を置かない）。

## §3 ★ 2 本目（本題）—— `capability matrix`（ADR-032 M7）

### 何を作るか

★ `ADR-032 D5` 逐語の要求: 「**GSE の現行 schema だけで T0/T1 のどこまで offline replay できるか
capability matrix を作る**」。⚠️ **`OS × ライブ変換設定` で層別する**（★ 1 つの表に畳まない）。

- **置き場**: `docs/architecture/`（★ 判断 4 の「影響範囲」）
- **判定は 3 値**: 「作れる / 作れない / 粒度が足りない」（`ADR-032 D5`）

### ⚠️ 実証範囲は決まっている（判断 5・採用は **A**）

```
A: 現行 schema の静的分析 ＋ 既存 fixture での実測 replay ＋ 起票 6 の既測結果の引用
```

- ⚠️ **O1 は未配布で実データが 1 本も無い**（★ 手元の fixture は**すべて合成**）。
  ⚠️ 判断 5 の本文は「合成 13 本」と書いているが、★ **2026-09-21 の実測では 15 本**
  （`ls src-tauri/tests/fixtures/*.ndjson | wc -l`）—— issue 008 以降に
  `stall_onset_observed.ndjson` / `instrument_rich.ndjson` が増えている。★ 着手時に数え直すこと。
- ★ macOS ライブ変換の歪みは **2026-09-12 に実測済み**
  （`.steering/20260914-instrument-change-arbitration/blockers.md` の「起票 6」）。★ 引用できる。
- ⚠️★★★ **合成 fixture 上の判定であることを表に明記する。**
  ★ 実データでの再判定が要る項目は「**要再判定**」と書く（⚠️ 「作れる」と断定しない）。
- ★ **見直しタイミング**: O1 の実データが届いたとき（判断 5）。

### ★ 表が閉じたら裁定するもの

| 何 | 一次 |
|---|---|
| ADR-032 **未決 ④**（IME content-free 状態機械） | `docs/adr/ADR-032-instrument-change-arbitration.md` **D5** |
| ADR-032 **未決 ⑤**（`esc_count`） | 同 **D5 の理由 2**（★ 「matrix の前にフィールドを打たない」） |
| **M11 = 単独キー用の門** | `.steering/20260914-instrument-change-arbitration/blockers.md` の「**起票 21**」 |
| `navigation-to-edit lag` の可否 | 同 ADR `:316`（★ 「④ と同じ `capability matrix` 待ち」） |

> ⚠️★★★ **「起票 21」は 2 つある。**
> ★ ここで言う起票 21 は **`.steering/20260914-instrument-change-arbitration/blockers.md`** の
> 「単独キー用の門」である。
> ⚠️ **`.steering/20260914-mhd-feature-offline-tiers/blockers.md` の起票 21 は別物**
> （2026-09-21 に採番した「AC18 の穴」）。★ 同ファイル冒頭に注記を置いてある。

## §4 ⚠️ 残っている起票のタイミング（★ 2026-09-21 に整理した）

| # | 中身 | ★ いつやるか | ⚠️ 理由（★ 一次） |
|---|---|---|---|
| **18** | `loop-spawn.sh --cleanup` の嘘の完了報告 | ★ **本セッションの 1 本目**（§2） | ⑥ を Loop で回す前に要る。⚠️ ⑤ は Loop に載せない（判断 4）ので ⑤ 自体には不要 |
| **19** | `RUSTSEC-2026-0285`（rustls 0.23.43） | ★ **依存を触る回**（⚠️ 研究者裁定で「別タスク」）。★ `cargo tree -i rustls` で**誰が上限を締めているか**から | `supply-chain.yml` は **branch protection が無いので門ではなく信号**（`docs/agent-shared.md` 逐語）。★ 赤でも merge は止まらない |
| **20 (a)** | 打ち切りの追跡時間 | ✅ **完了**（`provenance.observed_intervals`・PR #215） | — |
| **20 (b)** | E2 の過剰分割 | ★ **E1 を入れる回**（＝ `recovery` / `progress_proxy` を実装する回） | V1 の裁定（`.steering/20260920-issues-004-006/decisions.md` 判断 2）が「E1 は `recovery` と同時に別層で」と決めている |
| **21**（mhd 側） | 配線を通した計算量の門が無い | ★ **同上（E1 を入れる回）** | ⚠️ E1 は **onset ごとの仕事を増やす**ので、二乗の危険が戻るのはまさにその回である。★ 計時では分離できない実測表が起票 21 に載っている（⚠️ 同じ検証を繰り返さないこと） |
| **22** | 台帳の切り捨て | ✅ **完了**（`run-codex-review.sh` の `[-30:]` を外し、消えた 1 件を復元・注記に訂正を追記） | — |

★ **`recovery` / `progress_proxy` はいつか**: ⚠️ `ADR-009` は **Proposed** で `ContextBuilder` は未実装。
★ 2026-09-21 に `grep -rn progress_proxy src-tauri/src/` で再確認した実測ヒットは
`analysis/features.rs` のコメントと `bin/replay.rs` の警告文だけである（★ 実装は無い）。
→ ⚠️ **20 (b) と 21 は G1 / O1 のデータが動くまで開いたままでよい。**★ 先取りして E1 を入れない。

## §5 ⚠️ 先に確かめること（★ 推測で始めない・相対パスを明示）

1. `docs/adr/ADR-032-instrument-change-arbitration.md` の **D5 / M7 / M11 / §Consequences**（★ 全文通読）
2. `.steering/20260914-mhd-feature-offline-tiers/decisions.md` の **判断 4 / 判断 5 / 判断 25 #16**
3. `.steering/20260914-instrument-change-arbitration/blockers.md` の **起票 6**（macOS ライブ変換の実測）と **起票 21**
4. `src-tauri/src/schema_dto.rs` ＋ `src-tauri/schema/current.json`（★ 「現行 schema」の実体）
5. `src-tauri/tests/fixtures/`（★ **2026-09-21 実測 15 本**・すべて合成。⚠️ 着手時に数え直すこと）
6. `src-tauri/src/analysis/feat_offline/`（★ いま何が作れているか ＝ `activity` / `boundary` /
   `dispersion` / `stall_onset` / `quality` / `revision` / `restart` の 7 モジュール）
7. `scripts/loop-spawn.sh`（起票 18 の対象。★ `:57` 付近）

## §6 ⚠️ 守ること

- ★ `/start-task` から。判断は各タスクの `decisions.md`。`verify-before-claiming`（状態の断定は一次で）。
- ⚠️ **ADR 本文・事前登録 `§3`・被験者向け文書は書き換えない**（★ matrix は `docs/architecture/` の新規文書）。
- ★ 完了時に `code-reviewer` ＋ `security-checker`（並列・opus）と `/cross-review` **2 巡**（パス限定）。
  ⚠️ レビュー系 subagent には **範囲 / 作業ツリー不可 / クローン不可 / 長い検査を回さない / N 分で結論**
  を明記する（★ 契約は `.claude/skills/subagent-delegation/SKILL.md`）。
  ⚠️ **範囲に入れないファイルがあるなら、その旨をプロンプトに書く**（★ 2026-09-20 に Codex が
  `Cargo.toml` を範囲外にしただけで「コンパイル不能」と誤検知した）。
- ★ `/cross-review` は `bash scripts/run-codex-review.sh <base>..<head> -- <paths>` の形で**パス限定**で回す。
  ⚠️ 出力先は scratchpad（★ repo に置かない）。
  ★ **予算は日付が変わると当日使用量が 0 で判定される**
  （`scripts/run-codex-review.sh:146` / `.claude/hooks/codex-budget-guard.sh:80` 実測）——
  ⚠️ **日付だけ見て「超過している」と早合点しない**。
- ⚠️★★ **python でスクリプトを書き戻さない**（★ Windows で CRLF が混入する）。
  → `Write` / `Edit` を使い、`tr -cd '\r' | wc -c` が 0 であることを確認する。
  ★ どうしても python を使うなら `newline='\n'` を明示する。
- ⚠️ `git add -A` / `git add <dir>` 禁止。`.codex/budget.json` を `git checkout --` で戻さない。
- ★ コミット: `[type]([scope]): [説明]` ＋ 本文 ＋ `Refs:` ＋
  `Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>`。
