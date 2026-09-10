# 次セッション: Phase1 完了前にできる「凍結非接触」の前倒し準備を並行実行

Post-Phase1 の Epic 1（GSE v2 SSOT 昇格 + ADR-001〜007）は **PR #71/#72/#73 で main 済み**
（main tip = `713c395`）。ADR-006 は **Alternative C「分離」+ 下位決定 #2/#3 まで確定**。
**Epic 2 以降のコード実装は Phase1 完了 + 凍結解除が前提**で今はできない。

このセッションでは、**Phase1 完了前でも凍結対象に一切触れずに価値を出せる 3 本を、並行サブエージェントで実行**する。
（前セッションで「集計は待つのでなく今のうちに盤石化する」方針を確認済み。GAS リマインド実装は完了済みで対象外。）

## 最優先: 全エージェント共通のガードレール（厳守）

- **凍結対象に一切触れない・変更しない**: `src-tauri/src/schema_dto.rs` / `src-tauri/schema/current.json` /
  `src-tauri/src/analysis/engine.rs`（特に `HMM_VERSION`）/ `src-tauri/src/analysis/intervention.rs` の閾値定数 /
  `src-tauri/src/analysis/probe_scheduler.rs` / `src/App.tsx` の argumentative lock / `docs/preregistration-v0.3.md`。
- **この前倒しパスは「調査 + 実行(read/run) + 報告 + 具体的な実行計画の提示」に限定**。コード改変はしない
  （新規 fixture/スナップショット/ハーネスの *追加提案* は出すが、実際の追加・コミットはメインで承認後に行う）。
- 実装系タスクではないが、着手時は該当 Skill（`reproducibility-discipline` / `architecture-rules` /
  `project-status`）を先に参照する。

## セットアップ（まず実施）

- `git fetch` して origin/main が `713c395` 以降か確認。
- **main ベースの clean な worktree を作る**（現在地 `feature/phase1-reminder-and-dashboard` は GAS 作業ツリーで
  未コミットあり・main より遅れ。cwd は毎回リセットされるので `git -C <worktree>` 運用）:
  `git worktree add -b chore/phase1-verdict-and-epic2-prep <path> origin/main`
- 各サブエージェントはこの worktree で作業させる（read/run のみなら共有可・cargo は target ロックで直列化）。

## 並行実行する 3 本（サブエージェントに委譲）

### ① 集計パイプラインを「ボタン一発 + 再現可能」状態に前倒し（最優先・凍結非接触）
- 既存 fixture で集計 CLI を通し dry-run 検証: `calibration_eval`(GATE2/GATE3・C-index) / `cohort`(verdict) /
  `intervention_eval`(HIR/Precision) / `gse-replay --metrics`(Y 指標)。
- 再現ハーネスを reproducibility-discipline 準拠に（seed 固定・HMM_VERSION 刻印・入力 NDJSON hash 固定）。
- **偵察済みの事実**: `scripts/run-calibration-cohort.sh` は在るが **`scripts/repro.sh` は見当たらない**（要確認・提案）。
  `src-tauri/tests/fixtures/` に calib_subject_s1/s2/s3_eval・cohort/・outcome_metrics・phase1_* 等あり。
  **`src-tauri/bin/` は存在せず**（repo-inventory の記載と不一致）→ 実バイナリ位置を要特定
  （`src-tauri/src/bin/` か Cargo workspace member か。`Cargo.toml` の `[[bin]]` / `bin` を確認）。
- 成果: データが揃った瞬間に verdict(Go/Kill/Inconclusive/DataInsufficient)を 1 コマンドで出せる手順 + 穴リスト。

### ② Epic 2 の安全網＝現行挙動ゴールデンの網羅監査（凍結非接触・read/run のみ）
- Epic 2 の受け入れ条件は「**replay --snapshot が byte-equal**」。その基準となる現行ゴールデンのカバレッジを監査。
- **偵察済みの事実**: `src-tauri/tests/snapshots/` に **`minimal.json` の 1 本しか無い**。Epic 2 が触る
  `engine.rs`/`features.rs`/`loop_step.rs` の挙動を byte-equal で守るには **golden カバレッジが薄い**。
- 各 fixture（特に `phase1_ime_heavy`・`calib_subject_*`・`category_coverage`）で現行 replay/calibration 出力を
  確認し、**Epic 2 前に固めるべき golden 一覧（どの fixture × どのモード）を提案**する。実際の snapshot 追加は
  メインで承認後（凍結挙動の *記録* なので安全だが、追加コミットは Phase1 中でも可否を明示確認する）。

### ③ deep-research 第4ラウンド（RQ-2 / RQ-3）※重い・要 opt-in の明示
- Epic 4(Agentic Coding)は「証拠ゼロ」で着手前のエビデンス確認が必須。**RQ-2 = エージェントコーディングの
  過信/盲目的 accept を content-free な行動イベント（accept/reject/test/revert/review-duration）だけで検出できるか**、
  **RQ-3 = accountability(他者存在・約束)の作業開始/継続への効果とツール効果からの分離可能性**。
- Phase1 と独立に今できるが**重い**。`deep-research` skill を使う。**1 回で 1 問に絞る**のが質的に有利
  （まず RQ-2＝Epic 4 gate を推奨、RQ-3 は follow-up）。研究ポジショニングのエビデンス温度
  （`docs/research-positioning.md §8`・[V43]自己申告逆風・[P27][P28]）を必ず踏まえ、過大主張しない。
- 産物は `docs/literature/` の落合フォーマットカード + `docs/references.md` への append-only 登録
  （`literature-card` / `citation-ssot` skill 準拠）。これは additive・凍結非接触。

## 参照する真実源（先読み）

- `.steering/20260724-epic0-repo-reality-check/`（repo-inventory / design-vs-code-gap / migration-risk-register /
  adr-and-issue-roadmap）— 現行実態と Epic ロードマップ。
- `docs/architecture/`（gse-v2-overview / domain-adapter-boundary / intervention-decision-engine）+ `docs/adr/`
  （ADR-001〜007。特に **ADR-006 = C 採択済み**）— Epic 1 の SSOT。
- `docs/research-positioning.md §1/§8/§9` — 理論接地(機会保存)・エビデンス温度・スコープ。
- `docs/development-guidelines.md §3`（Replay-as-Truth テスト方針）・`reproducibility-discipline` skill。

## 進め方

- ①② は read/run/report の調査サブエージェントとして**並行起動**（凍結非接触・ファイル改変なし）。各々が
  「現状 + 穴 + 具体的実行計画」を返す。メインが統合して、実際の準備作業（repro.sh 作成・golden 追加等）は
  ユーザー承認のうえ別ブランチ→PR で実施。
- ③ は `deep-research` skill を RQ-2 に絞って起動（重いので明示 opt-in・スコープ提示してから）。
- **凍結対象への変更、Epic 2 以降のコード実装には踏み込まない**。迷ったら推測で動かずユーザーに確認。
