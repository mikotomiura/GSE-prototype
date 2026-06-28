# 設計

## 実装アプローチ

実データで判明した (ii)〜(v) を 1 本のクリーンビルド（M0 凍結）に束ねる。実施順は **T0 サーベイ → §2 数値確定 → T1〜T5 → M0 凍結**。T0/§2 を飛ばして実装に入らない。

## 先読みで判明した事実（実装の前提）

### T1 較正 ProbeConfig（probe_scheduler.rs / lib.rs）
- `ProbeConfig` struct: `probe_scheduler.rs:135-174`。フィールド: `lambda_per_ms / gap_min_ms / cap_window_ms / cap_count / max_gap_ms / away_idle_ms / min_session_elapsed_ms`。
- default: λ=2/30分・gap_min=6分・cap=2/20分・max_gap=22分・away=3分・warmup=31s。
- **現状ハードコード**: `lib.rs:1640-1644` が `ProbeConfig::default()` を無条件使用。away_idle も `lib.rs:1655` でハードコード。
- seed: `lib.rs:1634` `rand::random()`、audit ログ済（D-14）。スケジューラスレッドは `SESSION_START_MS` 変化で再初期化（`lib.rs:1627`）。
- **セッション種別**: UI ドロップダウン（App.tsx）→ `condition`（`blind_calibration` / `baseline`）を session_meta に送信。`Condition::BlindCalibration` は logger.rs に存在。
- → **方針**: `ProbeConfig::calibration()` を追加し、`start_session` で受けた condition に応じて scheduler スレッドへプロファイルを供給（channel 注入 or Atomic フラグ）。seed 決定性・引数注入・純ロジック維持。31s 窓と重ならない gap_min を厳守。数値は §2 で T0 を根拠に確定。
- 既存テスト 24 本（droughts/spread/determinism/cap/gap/window clamp）。calibration プロファイル用に収量/分散テストを追加。golden 無し（シミュレーションで期待値生成）。

### T2 提出ラッパー（package.rs 再利用）
- `gse-package`: `--input --participant --recipient [--out]`。recipient は age1 文字列 or pubkey ファイルパス。出力 `{participant}_{stem}.age`。
- 匿名化: `anonymize.rs` VK→KeyCategory（11 種）・絶対時刻→相対・本文/タイトル非保存。`gse-unpack` 側で FORBIDDEN_RAW_FIELDS 検証。
- セッション NDJSON: `$GSE_DATASET/raw/<pid>/gse_*.ndjson`（env 設定時）or fallback `~/Documents/GSE-sessions/gse_<YYYYMMDD_HHMMSS>.ndjson`。
- participant_id: `~/.gse/participant_id` に永続（アプリと共有）。
- pubkey: ハードコード無し（研究者が out-of-band 配布）。`age` crate feature-gate（`package`）。
- → **方針（T2）**: 最新 `gse_*.ndjson` を自動検出 → 永続 participant_id ＋同梱 pubkey で gse-package ロジックを呼ぶダブルクリック実行物。**§2 で A/B 決定**（A=ラッパー推奨：age 依存を blind アプリ本体に載せない）。

### T3 ファイル名 実名漏れ
- Dropbox File Request が投稿者名を付与 → `P006_..._mikoto miura.age`（中身は匿名化済）。
- → docs 対策: 提出時に名前を出さない設定 ＋ 受領側で P### リネーム手順。`participant-setup-guide.md` §4 / `pilot-runbook.md` §4.1 に明記、data-privacy SSOT 化。

### T4 self-marker 導線（既に実装済・教示が欠落）
- 実装済: Dashboard 「🔴 今とても詰まっている」ボタン（`record_self_marker` IPC, lib.rs:943）＋ D ホットキー（Ctrl+Shift+Alt+D, lib.rs:1703）＋ M ホットキー（カード式, lib.rs:1702）。debounce 2s。
- 教示は **participant-setup-guide に存在しない** → §3 付近に self-marker 説明追加。必要なら frontend ヒント。

### T5 docs バージョンカット
- `preregistration-v0.3.md:1-6`（凍結ヘッダ）・PreReg-2（GATE2: 回答率≥80% / latency≤10s / 有効≥20件/人, line 30-32）。
- `research-positioning.md` §5（H-X1 鎖, 144-176）・§6 WBS M0（178-186）・§8 成功基準（195-210, Kill vs DataInsufficient）。
- `experiment-tracking.md`（実験ディレクトリ規約・label_pool 分離・participant↔ID）。
- `references.md`: V 名前空間 append-only、現在 **V23** が最新（probe-timing で V18-V23 追加済）→ T0 は V24 から。
- `literature/_index.md`: 最新 2026-06-28 probe-timing（5 カード）。

## 変更対象

### 修正するファイル
- `src-tauri/src/analysis/probe_scheduler.rs` — `ProbeConfig::calibration()` 追加・収量/分散テスト
- `src-tauri/src/lib.rs` — condition に応じた ProbeConfig 選択を scheduler スレッドへ供給
- `docs/participant-setup-guide.md` — self-marker 教示（T4）・提出ラッパー手順（T2）・実名漏れ注意（T3）
- `docs/pilot-runbook.md` — 受領側 P### リネーム手順（T3）・ラッパー受領フロー（T2）
- `docs/preregistration-v0.3.md` — バージョンカット前向き宣言（T5）
- `docs/research-positioning.md` §6/§8 — M0 ラベル収量前提更新（T5）
- `docs/experiment-tracking.md` — P006=researcher test / P007=shakedown 記録（T5）
- `docs/references.md`（V24+ append）・`docs/literature/_index.md`（T0）

### 新規作成するファイル
- `docs/literature/<date>-calibration-sampling-density.md` ほか落合カード ≥2 本（T0）
- 提出ラッパー実行物（T2・形態は §2 で確定: shell/AppleScript+PowerShell or 新 bin）
- `.steering/.../decisions.md`（設計判断）

## 影響範囲
- probe_scheduler の純ロジック/seed 決定性を壊さない（gse-replay byte-equal）。default プロファイルは不変＝既存スナップショット影響なし。calibration は新規分岐。
- 提出ラッパーは blind アプリ本体に age 依存を載せない（盲検維持）。CI 本番バイナリ＝配布の単一真実源を維持。

## 既存パターンとの整合性
- `analysis/` は OS API 非依存・純ロジック・seed 注入式（既存 ProbeConfig 注入設計に沿う）。
- データ匿名化保証（VK→KeyCategory・本文非保存）不変。
- citation-ssot append-only・名前空間保持。

## テスト戦略
- 単体: calibration プロファイルの収量（20件を目標時間で達成）・分散（drought 無し）・seed 決定性・gap_min ≥ 31s 窓。
- 回帰: `cargo test --workspace` ＋ `gse-replay --snapshot`（byte-equal、default 不変確認）。
- 提出ラッパー: 最新検出ロジック・匿名化保証（FORBIDDEN_RAW_FIELDS）を模擬入力で確認。

## ロールバック計画
- 各トラックは独立。T1 は calibration 分岐のみなので default に戻せば既存挙動。docs は git revert。M0 凍結タグは宣言のみ（コード不変）。
