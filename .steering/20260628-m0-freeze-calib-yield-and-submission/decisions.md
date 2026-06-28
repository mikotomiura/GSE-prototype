# 設計判断 (§2 確定・T0 を根拠に)

T0 落合サーベイ（[V24]-[V29]、`docs/literature/20260628-calibration-sampling-density.md`）の所見を
根拠に、実装前の §2 数値判断を確定する。裏取り不能な外挿は「概算」と明示。

## D1: 較正専用 ProbeConfig レート（T1・最重要）

**決定**: `ProbeConfig::calibration()` を新設し、較正セッション（condition=blind_calibration）でのみ使用。

| フィールド | default | **calibration** | 根拠 |
|---|---|---|---|
| `lambda_per_ms` | 2/30分 (≈1/15分) | **1/6分** | ESM 標準は 6/日だが「総回数は compliance に無相関・頻度↔期間トレードオフ」[V25][V26]＝構造化セッション内なら高密度可。default の ~2.5× |
| `gap_min_ms` | 6分 | **3分** | 31s 分析窓（t-31s..t-1s）と重ならない・隣接プローブの窓非重複を保証。away_idle と同値だが独立制約 |
| `cap_window_ms` | 20分 | 20分（据置） | rolling 測定窓は維持 |
| `cap_count` | 2 | **4** | 較正は収量優先。20分4回＝90分18上限で非律速（実効はλで~10-14に収まる） |
| `max_gap_ms` | 22分 | **10分** | 短いセッションでの drought 防止（P007 の21分 drought 再発回避）。soft censoring 維持 |
| `away_idle_ms` | 3分 | 3分（据置） | 離席除外は不変 |
| `min_session_elapsed_ms` | 31秒 | 31秒（据置） | warm-up＝窓が session_start を割らない保証（DB-8）を維持 |

**収量逆算（実測で確認）**: シミュレーション（seed 0..64・90分・active）で **提示 min=10 / max=15 /
mean≈12 件/セッション**（`calibration_yield_supports_gate2_in_a_few_sessions` テスト）。compliance ~80%[V25]
で有効 ~9.6/セッション → **2 セッションで有効 ≈ 19、2-3 セッション/人で有効 ≈ 20 件（GATE2）**。
measurement independence は stratified random のまま維持（[V18]-[V23]・小休止合わせは入れない＝L0 較正の独立性）。
**非侵襲レート（Phase2 配備）とは分離**: `ProbeConfig` は注入式なので default（配備・侵襲最小）と
calibration（較正・収量優先）を共存可能。

**裏取りの限界**: compliance ~80%・有効=提示×0.8 は GSE ドメイン未測定の概算。M0 P007 再走で実測し較正。

## D2: GATE2 ≥20 件/人の妥当性（T5・閾値は維持）

**決定**: 閾値 ≥20 は**変更しない**。ただし prereg/positioning に「**floor であって高精度推定の十分条件
ではない**」と明示する。
**根拠**: ≥20 は単一事例最小 ~15–18 点（phase ≥5–6 × ≥3 実証）[V28] を超え、within-person 信頼性の
理想 ~70–100 機会 [V27] には届かない、その**間の floor**。Stage-1 の C-index 方向検定（median ≥0.65・
全員 >0.55）には妥当な床。Stage-2 昇格時に機会数増を予告する。

## D3: 提出方式（T2）= A 自動検出ダブルクリック・ラッパー（推奨）

**決定**: A を採用。最新 `~/Documents/GSE-sessions/gse_*.ndjson`（or `$GSE_DATASET/raw/<pid>/`）を
自動検出 → 永続 `~/.gse/participant_id` ＋ 同梱 pubkey で `gse-package` ロジックを呼ぶダブルクリック実行物。
**理由**: (1) age 依存を blind アプリ本体に載せない（盲検・審査面で隔離）、(2) 参加者のパス手打ちミス排除、
(3) 提出摩擦の除去は compliance/retention に対する正しい投資（負担は密度より提出摩擦で効く [V25][V29]）。
B（アプリ内ページ）は age 依存をバイナリに載せる審査が要り盲検リスク → 不採用。

## D4: self-marker 導線（T4）= 教示追加（実装は既存活用）

**決定**: self-marker は**既に実装済**（Dashboard ボタン「🔴 今とても詰まっている」＋ D/M ホットキー、
`record_self_marker` IPC）。コードは流用し、**教示・UX を `participant-setup-guide.md` に追加**（現状欠落）。
**役割再定義**: 較正ラベルは **probe（signal-contingent）を主・self-marker（event-contingent）を従**。
event-contingent は率で測れず取りこぼしが主 [V24] のため、self-marker 単独に依存しない（実データ self-marker=0
は教示欠落が主因と判断）。必要なら控えめな UI ヒントを追加。

## D5: バージョンカット（T5）

**決定**: prereg に「**リリース版 0.3.0 release = shakedown / M0 凍結ビルド = confirmatory**」を**前向き宣言**
（forking paths 排除のため事後でなく事前にカットを明記）。P006=researcher test、P007=shakedown として
experiment-tracking に記録し、M0 凍結後に P007 を confirmatory 再走。

## D6: レビュー対応（code-reviewer + security-checker + Codex cross-review）

- **code-review HIGH（meta-ready ゲートのサイレント全滅）**: 対応。grace(5s) 超過で default 初期化＋warn。
- **Codex HIGH（meta フラグが世代未照合）**: 対応。`SESSION_META_READY: AtomicBool` →
  `SESSION_META_FOR_START_MS: AtomicU64` に変更し、session_start と**世代照合**してから calibration を採用。
  判定を純ロジック `decide_probe_init`（probe_scheduler.rs・OS 非依存）へ抽出し 5 単体テスト追加。
  これで「前セッションの古い meta が新セッションに適用される」事故と grace 境界の偽 warn を同時に解消。
- **Codex MEDIUM-3（`gse-submit --help` が exit 1）**: 修正。help は stdout＋exit 0。
- **Codex #6（gate/packaging テスト不足）**: 対応。decide_probe_init 5 本＋package_session 結合テスト
  （meta 欠落 reject・出力名・復号後 category/非 vk 確認）追加。
- **不採用＋理由**:
  - Codex MEDIUM-4（`--recipient` 任意ファイル読取）: `--recipient` は上級者向け override で既定経路ではない
    （既定＝同梱 pubkey.txt/env）。ローカルツールで外部送信なし。security-checker も LOW（鍵ピンニング）判定。
    runbook に pubkey fingerprint 目視確認を記す方針で十分（コード変更不要）。
  - Codex LOW-5（participant ID を `^P[0-9]{3}$` に厳格化）: 不可。logger は ID を `P`+12hex で自動生成しうる
    （`P###` 固定でない）。厳格化すると自動生成 ID を弾く。現行の英数字≤16（traversal 防止）が正。
  - code-review MEDIUM（packaging が logger パス規約を手写し）: logger の `resolve_participant_id` は ID 生成の
    副作用があり read-only 提出ツールから呼べない。意図的複製として doc 注記＋parity テスト
    （`session_dir_mirrors_logger_fallback`）で drift 監視。logger の temp フォールバック先未探索は既知の限界
    （一次パス書込失敗時のみ・稀）として runbook で対処。
- **security-checker**: CRITICAL/HIGH なし。匿名化必須・recipient 検証・traversal 防止の不変条件成立を確認。
