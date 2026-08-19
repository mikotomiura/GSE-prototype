# タスクリスト

## 準備
- [x] handoff `_handoff/next-session-prompt-observation-space-for-nonkeystroke-tasks.md` を読む
- [x] §4 の必読 9 件を読む（domain-adapter-boundary / notes.md / research-positioning §8・§9 /
      ADR-011 / ADR-008 / ADR-010 / task-adaptation / decisions.md / env.md / data-privacy）
- [x] 収集仕様の 3 つの穴を `file:line` まで実測確認（`lib.rs:2924` / `hook.rs:140` / `liveness.rs:64`）
- [x] 引用 ID（[P117][P118][P119][P120][P121][V27][V28][V83][V84]）が `references.md` に登録済みか確認

## grill（`/start-task` Step 1 の置換）
- [x] §1 の切り分けを最初に固定（A-Q3 は発動しない / 文献の帯は別の土俵）
- [x] §3 の 12 点をすべて裁く（D-0〜D-12）
- [x] `decisions.md` に決定/理由/却下案を記録
- [x] `docs/glossary.md` に新規用語 4 件を追記

## 設計
- [x] `requirement.md` を記入
- [x] `design.md`（v1）を記入
- [x] `/reimagine` を実行 → `design-v1.md` 退避 / v2 生成 / `design-comparison.md`
- [x] 採用判断（**v2**）と根拠を `design.md` 末尾に追記

## 成果物（★ コード変更ゼロ）
- [x] `docs/adr/ADR-012-nonkeystroke-observation-formative-track.md`（Accepted）
- [x] `docs/adr/ADR-013-collection-self-description.md`（Accepted）
- [x] `experiments/20260819-nonkeystroke-silence-coverage/preregistration.md`（★ 実データ参照前に凍結）
- [x] `experiments/20260819-nonkeystroke-silence-coverage/README.md`
- [x] `docs/research-positioning.md` §8 **T3 行の降格先列のみ**改訂 ＋ §9 の矛盾記述を整合
- [x] `docs/adr/README.md` に ADR-012 / ADR-013 を索引追加
- [x] `docs/architecture/domain-adapter-boundary.md` §Adapter C に追記
- [x] `docs/architecture/personalization-and-online-learning.md` §5.2 に追記
- [x] `docs/adr/ADR-011-…md` Migration 3b に Stage 0 との関係を追記
- [x] `.steering/_handoff/next-session-prompt-g1-cohort-silence-decomposition.md`（★ Stage 0・収集完了次第）
- [x] `.steering/_handoff/next-session-prompt-nonkeystroke-instrument-build.md`（★ Stage 1 計測器）

## 検証（★ 「変えていないことの証明」）
- [x] `git diff --stat -- src-tauri` が **空**
- [x] `cd src-tauri && cargo test --workspace` が緑
- [x] `cargo run --bin gse-replay -- tests/fixtures/minimal.ndjson --snapshot tests/snapshots/minimal.json` が exit 0
- [x] `HMM_VERSION` が `0.4.0` のまま
- [x] `python scripts/check_schema_parity.py` が exit 0
- [x] `§8` の **T1/T2 行**に差分が無い
- [x] 禁止語（利得の主張）が ADR-012 / ADR-013 / prereg に無い

## 検証（追加・★ verify-before-claiming）
- [x] 引用した `file:line` を全件機械照合
      （★ 1 巡目で 3 件のずれを検出: `liveness.rs:63→64` / `lib.rs:2967→2965` / `notes.md:1807→1808`。
      ⚠️ **1 巡目の sed は `lib.rs:2967` を 2 ファイルで取りこぼしており、code-reviewer の指摘で 2 巡目に修正した**）
- [x] 2 巡目: `lib.rs:2883-2891` / `liveness.rs:86-104` も訂正

## レビュー
- [x] code-reviewer + security-checker（並列実行・★ 別々の穴を検出）
- [x] `/cross-review`（★ パス限定で実行・secrets-filter 通過・`--ack-filtered` 不使用）
- [x] HIGH / CRITICAL 指摘への対応（★ **全件消化**。CRITICAL 0 / code-reviewer HIGH 6 / security-checker HIGH 4 / Codex 重大 2・中 2・テスト 1 → D-13 に記録）

## 完了処理
- [x] `decisions.md` の作成
- [x] `design.md` の最終化（★ v2 採用・⚠️ §4.1/§7 の variant 由来 capabilities を訂正）
- [ ] git commit
