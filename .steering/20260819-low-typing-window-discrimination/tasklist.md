# タスクリスト

## Phase 0: grill と裁定（完了）

- [x] `_handoff` の全文読解（440 行）
- [x] §2 の必読資料を実測で裏取り（ADR-008 / cv-gate-null / research-positioning §8・§9 /
      personalization §5.2・§8.2・§10 / ADR-009 / 前セッション D-6・D-7）
- [x] ★ **handoff と SSOT の衝突を特定**（`personalization…:786` / `:1152` の G1 ゲート）
- [x] ★ **G1 の実施状況を確認**（`controlled-friction-task/data.md:4` = 1/3 名）
- [x] ★ **`starved_ms` の意味論をコードで確認**（`liveness.rs:86-103` の 3 分岐）
- [x] ★ **観測の間引きを確認**（`lib.rs:2923` = 状態変化時のみ／30 秒未満は残らない）
- [x] ★ **既存実測を発見**（`20260809-g1-hook-liveness-detection/measurements.md §3` = 13.3%）
- [x] ★ **38.09% が上限側であることを確認**（`expression-power/data.md:40-42`／論述限定は 29%）
- [x] ★ **`task_kind` が Phase1 で分散ゼロであることを確認**（`task-scope-detector/data.md:14`）
- [x] grill（8 分岐を確定）
- [x] `requirement.md` / `decisions.md`（D-1〜D-10）/ `design.md` を作成
- [x] `docs/glossary.md` に 6 語を追記
- [x] ★ **設計欠陥を着手前に潰した**（「T0 = 沈黙長のみ」の循環 → `§8` の T0 定義へ戻す）

## Phase 1: 設計の承認と破壊（実装着手前）

- [x] design.md をユーザーが承認
- [x] `/reimagine` を実行し、**v2 を採用**（`design-comparison.md` / `design.md` 末尾に履歴）
- [x] ★ v2 が v1 の欠陥を 2 件是正（`§8.1` 逐語への抵触 / `keys`・`bs_keys` が Phase1 ログに無い件）

## Phase 2: 事前登録（★ 実データを見る前に凍結する）

- [x] `experiments/20260819-silence-presence-decomposition/` を作成
- [x] `preregistration.md` を**実データ参照前に**凍結（第 1〜3 版・改訂履歴 append 済み）
- [x] `config.json`
- [x] `SEED` / `env.md` / `requirements.txt`
- [x] `README.md`

## Phase 3: 実装（解析スクリプト）

- [x] `scripts/extract.py` — NDJSON → 沈黙ギャップ表
      （`key` の press から gap、`hook_health` から `peak_starved_ms` / `suspect_by_L`）
- [x] `scripts/analyze.py` / `scripts/describe.py` — LOSO ablation・2 基線への勝ち幅・生存曲線
- [x] `scripts/selftest.py`（S1a/S1b/S1c/S2/S3/S4）
- [x] `scripts/leakcheck.py`
- [x] `run.sh`

## Phase 4: 検証（★ ここまで実データを見ない）

- [x] `selftest.py` **exit 0**（★ 実装バグ 2 件を実データ前に検出・修正）
- [x] `leakcheck.py` **exit 0**
- [x] 合成 NDJSON での再構成が手計算値と一致

## Phase 5: 実行

- [x] `run.sh` **exit 0**
- [x] manifest sha256 が上流と**一致**（AC-7）
- [x] 2 回実行で `results/*.json` が **byte-equal**
- [x] ギャップ 776 個（Stop 条件に非該当）
- [x] ⚠️★★★ **別の Stop が発火: 計器不在**（`hook_health` 行が 0）。事前登録どおり L3 を出さず記録

## Phase 6: 記述

- [x] `data.md`
- [x] `notes.md`（★ 否定的結果を第一級の結論として記述）

## Phase 7: SSOT への還元

- [x] `docs/adr/ADR-011-low-typing-window-track.md`（⚠️ ADR-010 は既存だったので 011）
- [x] `docs/adr/README.md` の索引に追加
- [x] `docs/research-positioning.md` §8 の表の**直後に追記**（表は不変）
      — 探索トラック / 38.09% と 29% の併記（AC-10）/ 個人差 vs 実タスク差
- [x] `docs/architecture/personalization-and-online-learning.md` §5.2 に追記

## Phase 8: 回帰とレビュー

- [x] `cargo test --workspace` **exit 0**
- [x] `emit_schema` の差分**ゼロ**を確認
- [x] `code-reviewer` + `security-checker` を**並列起動** → HIGH 7 / MEDIUM 8 / **CRITICAL 1** を全件消化
- [x] `/cross-review`（パス限定 1,728 行で実行）→ Codex 高 2 / 中 2 を全件採用
      - ⚠️ `secrets-filter` が一度 fail-closed。**誤検知ではなく**、`leakcheck.py` の陽性対照に
        実在形式のセッション名を書いていた。`--ack-filtered` で迂回せず**架空名の約束へ修正**して通過
      - ★ **両者一致**は 1 件（`duration == gap_min` の露出ゼロ）→ 明示計上で対応
- [x] schema parity check（`check_schema_parity.py --dataset C:/gse-dataset` = **OK・22552 bytes**）
- [x] `/finish-task`

## Phase 9: 本タスクで新たに判明し、次へ送るもの

- [ ] ⚠️ **G1 終了後に本パイプラインを G1 コホートで実走する**（★ 本タスクの実験の本来の目的）
- [ ] ⚠️ **打鍵のみでの分析に関するユーザーの疑問**（★ 内容未記録・次セッションで確定する）

## ⚠️ 本タスクでやらないこと（`requirement.md` スコープ外の再掲）

- `src-tauri/` のコード変更（`engine.rs` への Tier 0 配線・`hook_health` の出力条件変更）
- input 層の新規 OS フック（マウス / `EVENT_SYSTEM_FOREGROUND`）
- `§8` 段別表・`§9` A-Q3 の**書き換え**（追記のみ）
- 適格性ゲート `keydown ≥ 100` の変更
- Wall / PM-Q1〜Q7 / `App.tsx` の argumentative lock
