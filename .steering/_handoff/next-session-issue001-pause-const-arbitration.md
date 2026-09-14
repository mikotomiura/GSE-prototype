# 次セッション開始プロンプト — issue 001 の pause 閾値問題を裁定する（詳細版・Opus）

> ★ **本ファイルは詳細版。** セッション冒頭に**そのまま打ち込む短い本文**は
> `next-session-issue001-pause-const-arbitration-prompt.md` にある（2026-09-15 追加）。
> ★ 前段（issue 001 実行の記録）は `next-session-loop-run-task2.md` /
> `next-session-loop-run-task2-prompt.md`。★ **その実行は 2026-09-15 に完了し、以後は本メモが現行**
> （旧 2 本の冒頭に上書き表示を入れてある）。
>
> 作成: 2026-09-15 / ⚠️★★★ **このメモを一次資料にしない。**
> ★ 一次は `.steering/20260914-mhd-feature-offline-tiers/issues/001.md` の Execution Result
> （★ **worktree 側にのみ存在・未コミット・証拠として保持中**）／
> `_loop-events.jsonl` ／ `docs/adr/ADR-030-stall-onset-and-decision-episode.md`。

---

## §0 まず読む

1. `.steering/_handoff/next-session-issue001-pause-const-arbitration-prompt.md`（★ 貼り付け用）
2. worktree の Execution Result（★ 一次資料・証拠保持中）:
   `C:/wt/GSE-prototype-001-issue/.steering/20260914-mhd-feature-offline-tiers/issues/001.md`
   （⚠️ **main checkout 側の同名ファイルは `queued` のまま更新されていない**。worker の調査結果は
   worktree 側にしかない）
3. `.steering/20260914-mhd-feature-offline-tiers/_issue-plan.md`（DAG / 交差表）
4. `docs/adr/ADR-030-stall-onset-and-decision-episode.md` の **D1 / D3 / D10 / D11**
5. `docs/loop-engineering.md`（Stop Condition の扱い）

---

## §1 何が起きたか（★ 実測・2026-09-14〜15）

- issue 001（`gse-replay --features` ＋ `T0` activity）を Loop モード C で `--issues 001` 単独実行。
- **6 attempt すべて `acceptance_fail` → `abandoned`**（`_loop-run-report.md`:
  tokens 7,792,190 / cost **$3.528222**）。
- worktree (`C:/wt/GSE-prototype-001-issue`) に**実装コミットはゼロ**。`feat_offline/` ディレクトリ自体が
  存在しない。変わったのは `issues/001.md` の Execution Result 欄だけ（未コミット）。
- worker の調査結果（原文は上記 §0-2）:
  - `features.rs` の「単純 pause」閾値（F5/F6 共通・2 秒）は **named constant として存在しない**。
    生リテラル `2000` が 4 箇所に散在: `features.rs:133`（F1 Flight Time 上限キャップ）／
    `:218,221`（F5 ポーズ判定、`// TUNE: ポーズ判定閾値 2000 ms (F5, F6 共通)` コメント付き）／
    `:233`（F6 削除後停止判定）／ `:280-281`（`make_silence_observation` の F1 合成値）。
  - issue 001 **AC 6**「pause 閾値は `features.rs` の既存定数を参照する」を満たす参照先が無い。
  - `analysis/intervention.rs:7` の `SHORT_PAUSE_MIN_MS`（値は同じ `2_000`）を代用候補として検討したが、
    Nudge の一時停止バケット分類用の定数であり F5/F6 とは**意味論的に別物**と判断（値の一致は偶然の
    可能性）。AC 6 の文言どおり「`features.rs` の既存定数」ではないため採用を見送った。
  - `features.rs` は Allowed Files に無く、Scope の Out 節でも変更を明示禁止しているため、
    実装を進めず **issue 001 の Stop Conditions 3 番目**
    （「『単純 pause』の閾値に対応する既存定数が `features.rs` に見つからないとき」）に該当すると
    判断して停止した（issue.md `Status: blocked`）。

## §1b ⚠️★★★ 2z の実地検証（「注入 ≠ 発効」）は依然未決着（★ 訂正記録）

- 6 attempt で `permission_denials` が 1〜3 件出た（`_loop-events.jsonl` の `attempt_start` 行）。
- ⚠️ **これを「git push 拒否が発効した証拠」と断定してはならない**（★ 一度そう報告しかけて訂正した）。
  `claude -p` の生 JSON (`res`, `loop-run.sh:342`) は**変数のままでファイルに保存されておらず**、
  denial の中身（どのツール呼び出しが拒否されたか）を今から確認する手段が無い。
- `loop-run.sh:361-366` のコメントが逐語「**denial が 1 件でもあれば return 1 する実装は間違い**…
  events_path は main checkout の絶対パスであり worktree の cwd 境界の外にあるため、append しようと
  すると**必ず**拒否される。無関係なディレクトリを 1 度覗いただけでも同じ」と説明しており、
  今回の denials は **worktree 外への日常的アクセス試行**である可能性が高い（`git push` とは無関係）。
- → ★ **「注入されていること ≠ 発効していること」は今回も検証できなかった**。次に検証するなら、
  `loop-run.sh:342` の `res` を `WORK_TMP` 配下に保存するよう変更し、denial の中身（tool 名・コマンド）
  を events か別ログに残す仕組みを先に足す必要がある（★ これも今回の裁定範囲外・記録のみ）。

## §2 ⚠️★★★ モードC の運用上の発見（★ 教訓・裁定と別に記録）

- worker が issue.md の `Status` を `blocked` に書いても、**`loop-run.sh` の events.jsonl には伝わらない**
  （モードC の原則「events を書くのは script だけ」の帰結）。
- 結果、**同じ理由（実装ゼロ）で 6 回リトライ**され、`max_attempts` 到達まで待たされた
  （$3.53 消費）。fingerprint は 6 回とも異なっていた（`b55e78d0…` / `beaa63fb…` / `856c561d…` /
  `4bceb8eb…` / `10ddd771…` / `a093398b…`）ため `no_progress_stop`（同一 fingerprint 連続）は発火せず、
  `max_attempts` 到達の `abandoned` まで回り切った。
- ⚠️ **これは今回の裁定の範囲外**だが、次回 issue-slicing / `loop-config.README.md` への追記候補として
  記録しておく：Stop Conditions に該当する前提の有無（今回なら「pause 閾値の named constant が存在
  するか」）を **acceptance.sh 側で事前に機械検査**しておけば、1 attempt 目で `acceptance_fail` の
  中身から気づけた可能性がある。

---

## §3 3案（★ この場での推奨 = 案1）

### ★ 案1（推奨）: `features.rs` の閾値を `pub const` に一本化する先行 issue を切る

- ADR-030 **D3**「新しい定数を作らず、既存パラメータを対称に再利用する」に最も沿う。
- `features.rs:133,218,221,233,280-281` の生リテラル `2000` を、値を変えずに `pub const` へ
  **命名するだけ**の最小リファクタ（新しい判断量は増やさない）。
- Allowed Files に `features.rs` を加えた issue を 001 の前に挿入し、DAG を
  `000(新規) → 001 → 002 → … → 007` に更新する。
- ⚠️ **要確認**: ADR-030 **D1**「検出器はオフライン側に置く（`features.rs` / `engine.rs` を触らない）」が
  この種の**命名だけの最小リファクタ**（検出ロジックの追加ではない）まで禁じているか、ADR-030 本文
  （D1 の逐語と射程）を次セッションで実際に読んで裁定すること（★ 推測しない）。

### 案2: `intervention.rs::SHORT_PAUSE_MIN_MS` の転用を ADR-030 に一文追記して許可する

- 利点: `features.rs` に触れず issue 001 をそのまま実行できる。
- 欠点: worker 自身が「値の一致は偶然の可能性があり意味論的に別物」と指摘済み。ADR-030 D3 の
  「既存パラメータを**対称に**再利用する」の精神に本当に沿うか要検討（Nudge のバケット定数を
  検出器の閾値に流用してよいかは設計判断）。

### 案3: pause 閾値を `--features` モードでは扱わず AC 6 を撤回・改訂する

- 利点: 工数最小。
- 欠点: `T0` の `activity` から `pauses` フィールドが抜ける（または未定義のまま）。
  「新しい定数を作らない」規律を検証する AC が消えることになり、issue-plan.md の設計意図
  （§6「全部 parse にしていない」根拠の一部）を弱める。

---

## §4 裁定後にやること

1. 上記いずれかを裁定する（★ Opus・設計判断。Sonnet 実行セッションでは決めない）。
2. `.steering/20260914-mhd-feature-offline-tiers/decisions.md` に裁定を追記する（判断番号を振る）。
3. **案1**: 先行 issue（例: `issues/000.md`）を追加 → `_issue-plan.md` の DAG・交差表・Allowed Files 表を
   更新 → issue 001 の Background / Scope / AC 6 に定数名を明記。
   **案2**: ADR-030 に一文追記 → issue 001 の AC 6 の文言を `SHORT_PAUSE_MIN_MS` 参照に調整。
   **案3**: issue 001 の Scope / AC から pause 関連を撤回 → `_issue-plan.md` を更新。
4. worktree (`C:/wt/GSE-prototype-001-issue`) を cleanup する:
   `bash scripts/loop-spawn.sh --cleanup 001-issue`
   （★ 調査結果の原文を読み終え、必要な引用は本メモ・decisions.md に転記済みなら撤去してよい）。
5. issue を改訂した上で `bash scripts/loop-run.sh .steering/20260914-mhd-feature-offline-tiers --issues 001`
   （案1 なら先に `--issues 000`）で単独再実行する。

---

## §5 実行条件（★ 継続・変更なし）

- ブランチ: `docs/adr-030-stall-onset-definition`（⚠️ main へ switch しない — ADR-030/031/032 はここにしか無い）。
- `git add -A` / `git add <dir>` を使わない（明示ファイル指定）。
- `_loop-config.json` の `allowed_tools` を `null` にしない。
- `.gitignore` の `_loop-events.jsonl` / `_loop-board.md` / `_loop-run-report.md` を外さない。
- `HMM_VERSION` を bump しない／ゴールデン snapshot を再生成しない。
- `schema_dto.rs` / `logger.rs` / `capabilities.rs` を触らない。
- `features.rs` / `engine.rs` / `loop_step.rs` の変更は原則禁止（★ 案1 を採る場合の例外可否は §3 の
  「要確認」どおり ADR-030 D1 本文で裁定すること）。

---

## §6 一次資料（パス）

- worktree Execution Result: `C:/wt/GSE-prototype-001-issue/.steering/20260914-mhd-feature-offline-tiers/issues/001.md`
- `.steering/20260914-mhd-feature-offline-tiers/_loop-events.jsonl`（6 attempt 全記録）
- `.steering/20260914-mhd-feature-offline-tiers/_loop-run-report.md`（cost $3.53 / 7.79M tokens）
- `src-tauri/src/analysis/features.rs:133,218,221,233,280-281`
- `src-tauri/src/analysis/intervention.rs:7`（`SHORT_PAUSE_MIN_MS`）
- `docs/adr/ADR-030-stall-onset-and-decision-episode.md`（D1 / D3 / D10 / D11）
