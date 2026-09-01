# タスクリスト

## 準備
- [x] 陳腐化の範囲を実測（`grep -c` でファイル別内訳）
- [x] ★ **コードの ground truth を 1 回だけ確定**（`InterventionAction{None,Nudge,Defer}` / Tauri コマンド 38 個 / デバッグボタン 2 個）
- [x] メインが独立に横断チェック（architecture.md の是正済み確認 / docs→コード参照 / invoke 参照）
- [x] `.steering/20260901-docs-stale-sweep/` を作成

## 監査（サブエージェント 4 本並列・★ 編集させず報告のみ）
- [x] `functional-design.md`（**45 件**）
- [x] `architecture/*` 3 本（**34 件**）
- [x] `development-guidelines` / `repository-structure` / `wbs`（**38 件**）
- [x] ★ **ADR-017 / ADR-018 / O1 の浸透**（**21 件**・研究者の指摘で追加した逆向きの軸）

## 是正（★ メインが直列・並列編集はしない）
- [x] `docs/agent-shared.md` — ★ **全エージェントの起点**（Lv 呼称 / 段階的介入 / ADR 範囲 / 主要ディレクトリ / ハブ表 11 本追加）
- [x] `docs/glossary.md` — 自己矛盾 3 行（cooldown / daily cap / InterventionPolicyState）＋ Opportunity ＋ aggregate_metrics
- [x] `docs/development-guidelines.md` — ★ **必ず失敗するテストコマンド**（`cd src-tauri` 欠落）/ CI runner / 排他フラグ / Wall Server / TSF 理由 / changelog / sensors
- [x] `docs/functional-design.md` — Wall 節ごと削除 / 禁止用語 2 件 / macOS 10→3 回 / key vk→category / 存在しないスクリプト 2 本 / セキュリティ節
- [x] `docs/architecture.md` — 完了条件 2 箇所（ADR-018 D1/D2/D4）/ `epoch` 欠落 / 見出しの Lv
- [x] `docs/architecture/gse-v2-overview.md` — ★ **自己矛盾していた「task_kind 未配線」** / InterventionAction / Monk Mode / 7 層 / ADR 範囲
- [x] `docs/architecture/intervention-decision-engine.md` — 現行型 / 現行閾値 / 最低ルール / 凍結解除
- [x] `docs/architecture/expression-channel.md` — ★ **ADR-018 D1/D3/D4/D5 の未反映**（§5.2 / §6 / §7.5 A7 / §8 E-5）
- [x] `docs/architecture/personalization-and-online-learning.md` — Lv2 Wall / structure 系 / X 合成式の位置
- [x] `docs/repository-structure.md` — ★ **実在モジュール 25 本を追記**（`o1.rs` / `observe_*` / `heads/` / `pointer_bin` 等）
- [x] `docs/wbs-verification-halfyear.md` — 存在しない Wall 定数 / HMM_VERSION 0.4.0→0.5.0 / 評価量 / dangling パス
- [x] `docs/experiment-tracking.md` — 例示の Wall

## テスト（★ 予測しない。走らせる）
- [x] `PYTHONUTF8=1 python scripts/check_citations.py` → **違反なし**
- [x] `git status --porcelain src-tauri src` → **空**
- [x] 現行仕様としての Wall / Monk Mode / Zen Timer / `wall_server` → **ゼロ**（残存は全て訂正注記・履歴・著者名の偽陽性）
- [x] docs→コードのファイル参照 → 存在しない 2 件はいずれも「存在しない」と書いている注記の中
- [x] `docs/agent-shared.md` のハブ表 → 自分自身を除き **全 26 本を網羅**
- [x] `repository-structure.md` → 実在ファイル **未記載ゼロ**

## レビュー
- [ ] `code-reviewer` + `security-checker` を並列起動
- [ ] `/cross-review`（★ 起動形は `HEAD -- <paths>`）
- [ ] HIGH 指摘への対応

## 完了処理
- [ ] `decisions.md` / `blockers.md` の最終化
- [ ] git commit
