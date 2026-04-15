# Completion Log — Windows Onboarding

> Windows 実機での検証完了時に本ファイルを記入する。

## 実行環境

- 実行日時 (Windows 側): 2026-04-15 23:00 〜 2026-04-16 00:40 (JST)
- 実行日時 (macOS 側集約確認): 未実施 (ユーザー側で後日 `git pull` + `aggregate_metrics.py`)
- Windows PC:
  - OS: Windows 11 Home (Build 10.0.26200)
  - Platform: win32
  - Shell: bash (Git Bash)
  - キーボード配列: 未確認 (ユーザー環境)
- gse-prototype commit: `9adf529` (pull 済み、pre-task)
- gse-dataset commit: `534893a` (Windows onboarding push 後、main)

## Stage A: 環境構築
- [x] A-1: Visual Studio 2022 Build Tools (C++ workload) — cargo build 成功から確認
- [x] A-2: Rust stable — 1.94.1
- [x] A-3: Node.js 22 LTS — v24.14.1 (想定より新しいが動作)
- [x] A-4: Git for Windows — 2.53.0
- [x] A-5: SSH 鍵セットアップ — **未実施** (HTTPS 認証で代替、gse-dataset clone 済み)
- [x] A-6: git 設定 — `core.autocrlf=input` 新規設定、user.name/email 既存
- [x] A-7: Python 3.10+ + jsonschema — 3.11.9 + jsonschema 4.26.0

所要時間: 既存環境活用のため実質 5 分 (autocrlf 設定のみ)

## Stage B: Clone
- [x] B-1〜B-4: gse-prototype は `C:\GSE-prototype` (既存)、gse-dataset は `C:\gse-dataset` (HTTPS clone、main @ 9d2c4ed 以降)

> **パス差分**: steering 想定 `%USERPROFILE%\repos\` に対し、本機は `C:\` 直下に配置。両レポジトリが隣り合う点は同じ。blockers.md の懸念事項として記録。

## Stage C: Build + Test
- [x] C-1 cargo build --target x86_64-pc-windows-msvc — 1m47s、warning 1 (`is_ime_active_check` dead_code、既存)
- [x] C-2 cargo test --workspace — **51 tests passed, 0 failed, 0 ignored**
- [x] C-3 snapshot regression — **15 snapshots match** tests/snapshots/minimal.json
- [x] C-4 schema drift check — emit_schema 出力と `schema/current.json` **diff 0** (LF / no-BOM)
- [x] C-5 tsc + vite build — エラー 0、vite ビルド 440ms

## Stage D: 実機スモークテスト
- [x] D-1 Tauri dev 起動 (ユーザー実機操作)
- [x] D-2 Counter 初期表示 (ユーザー報告: GT アクション説明記載済み)
- [x] D-3 Flow ラベル: 直後押下でデバウンス / 3 秒以上で反映 (ユーザー確認)
- [x] D-4 Inc / Stuck ラベル: 押下反映確認
- [x] D-5 セッション終了 (Dashboard ボタン)
- [x] D-6 NDJSON 生成確認 — **`C:\gse-dataset\raw\P000\gse_20260415_144120.ndjson`** (約 34KB)
  - **Note**: 保存先が steering 想定 `%USERPROFILE%\Documents\GSE-sessions\` ではなく `C:\gse-dataset\raw\P000\` に書かれた。`logger.rs` の挙動差は blockers.md に記録。
- [x] D-7 meta / user_label 内容確認: hmm_version 0.2.0、user_label 6件 (Flow 4 / Inc 1 / Stuck 1)、feat 96件、key 224件

セッションファイル: `gse_20260415_144120.ndjson`

(初回スモーク用の `gse_20260415_143258.ndjson` [7 labels / no typing] は metrics all-zero のため採用せず、タイピング混じりの第 2 セッションを本 onboarding の baseline とした。retrospective `実機データで算出系をすぐ回す` に沿った判断。)

## Stage E: Metrics + dataset commit
- [x] E-1 pretty-print 確認: SessionMetrics 出力正常、Detection lead median = **+26315 ms**
- [x] E-2 JSON 配置: `C:\gse-dataset\metrics\P000\windows\gse_20260415_144120.metrics.json` (1132 bytes, LF / utf8 no-BOM)
- [x] E-3 validate_schema.py NDJSON — OK (metrics JSON 自体は schema 対象外)
- [x] E-4 commit + push — **commit `534893a`** (dataset repo main) `data(P000-windows): first session 2026-04-15 (onboarding smoke)`

Metrics サマリ (pretty-print の抜粋):
```
SessionMetrics
  Total labels: 6 (Flow:0, Inc:0, Stuck:0)
  Macro F1: 0.000
  Micro F1: 0.000
  Per-class:
    Flow       P=0.000  R=0.000  F1=0.000  support=0
    Incubation P=0.000  R=0.000  F1=0.000  support=0
    Stuck      P=0.000  R=0.000  F1=0.000  support=0
  Detection lead median: +26315 ms  (positive = HMM leads user)
  Stuck recovery median: n/a
  Warnings: 6 (全 label が ±1000ms 内に FeatSnapshot 無しと判定)
```

**所見**: 元 NDJSON には 96 件の feat があり、python で時刻差分を取ると全ラベルが ±500ms 内に feat を持つ。にもかかわらず metrics CLI は「no FeatSnapshot within ±1000ms」を全件に報告。`gse-replay` が `step()` で feat 列を **再生成** する設計 (replay.rs:4) のため、再生成 feat 列と label 時刻のアライメントが崩れる可能性がある。Mac 側の baseline (`gse_20260415_080921`) では support>0 が出ていたため Windows 固有か入力パターン固有かは別途調査要。blockers.md に詳細記録。

## Stage F: macOS 側集約確認
- [ ] F-1 git pull (macOS 側で後日実施)
- [ ] F-2 aggregate_metrics.py — session_count 期待: 既存 2 → 3 (Windows 分 +1)
- [ ] F-3 `--os windows` / `--os macos` フィルタ動作

## 発見したブロッカー

2件 (詳細は `blockers.md` 参照):
1. Windows セッションログ保存先 `C:\gse-dataset\raw\P000\` (想定: Documents/GSE-sessions)
2. `gse-replay --metrics` が NDJSON 内に feat が近接しているのに「no FeatSnapshot within ±1000ms」で全ラベルを落とす (再生成 feat とのアライメント問題疑い)

## 所要時間 (全体)

- 環境構築 (既存活用): 5 分
- Stage C (build + test、subagent 並列): 3 分
- Stage D (実機スモーク、2 セッション): ユーザー操作含め 15 分
- Stage E (metrics + push): 3 分
- ドキュメント (本ファイル + blockers): 7 分
- **合計**: 約 30 分 (ユーザー操作待ち除く)

## 次アクション
- [x] BL-2 (feat アライメント) を別タスクで調査 + fix 完了: `.steering/20260416-replay-feat-alignment-bug/` (2026-04-16)
  - warnings 6→0、Macro F1 0.000→0.722、Stuck F1 0→1.0
  - dataset の Windows metrics JSON も fix 後値で上書き push 済み
- [ ] macOS 側で `git pull` + `aggregate_metrics.py` で Windows 分集約確認 (Stage F)
- [ ] Mac baseline (`gse_20260415_080921.ndjson`) を fix 後 CLI で再計算して dataset metrics を更新 (Mac 端末でしか実行不能)
- [x] BL-1 (ログ保存先) **Closed 2026-04-16**: logger.rs の自動 sibling 探索を撤廃、env `GSE_DATASET` + fallback の 2 段に簡素化、tracing::info で可観測化。詳細は `.steering/20260415-windows-onboarding/blockers.md` BL-1 Closed エントリ参照
- [ ] Windows 側で継続的に GT ラベル付きセッションを収集 (n>=5 目標)
- [ ] Stage H (sync-session.ps1 雛形) は Phase 2a 着手前に別タスクで検討
- [ ] MEDIUM 分離タスク候補: `20260416-replay-input-validation/` (NaN/Inf float バリデーション) と `20260416-replay-single-pass-collector/` (NDJSON 1 パス化)
