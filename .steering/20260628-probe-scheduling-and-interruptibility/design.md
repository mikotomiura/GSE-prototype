# 設計

## 実装アプローチ

2 トラック並行: **(I) スケジューラ是正（コード）** と **(II) 落合サーベイ（研究）**。II の知見で I のパラメータ/方式を裏取りする。

### (I) スケジューラ是正

1. **再現と原因特定**（純ロジック優先）:
   - `probe_scheduler.rs` の現行パラメータ実値を lib.rs の駆動側から洗い出す（λ / gap_min_ms / cap_count / cap_window_ms / away_idle_ms / poll 間隔 / seed）。
   - 模擬セッション（純ロジックを長時間 now_ms で driver し、idle 一定）で「初期 3 連→枯渇」を再現する単体テストを書く。
   - 仮説の切り分け:
     - **cap**: `cap_window_ms` が長すぎ/セッション規模 → 早期 cap_count 到達で以降ずっと棄却。
     - **λ 過大**: 平均間隔が短く序盤に集中（Poisson の自然なクラスタ＋gap_min が弱い）。
     - **gap_min 過小**: クラスタを許す。
     - **idle→away**: 駆動中に `last_key_ms==0`/idle 増で away 抑止（PR#36 の macOS 失効と同系。実ログで確認）。
2. **是正方針（候補・サーベイで確定）**:
   - 目標レート（例 N 件/時 or /セッション）を満たしつつ **均す**: λ 調整 ＋ **gap_min（最小間隔）で密集抑止** ＋
     **cap は"レート制限"であって"総量打ち切り"でないこと**を保証（cap_window をローリングで正しく流す）。
   - 枯渇防止に **soft max-gap（一定無発火が続いたら次候補を優先発火）** の導入を検討（一様性を壊さない範囲で）。
   - 純ロジック維持（OS/RNG/時刻は引数注入）。seed 固定で replay 決定性を保つ。

### (II) 非侵襲提示

- **probe 版 Opportunity ゲート**: 能動タイプ中（直近打鍵 <2s）は発火を遅延、小休止（2–30s）に合わせる
  （介入 Opportunity と同思想。ただしプローブは一様性要件があるため「遅延」は記録し偏りを監査）。
- 穏やか onset（既存 `.probe-card-pop` スライドイン）・右上非ブロック小ボックス（既存 Overlay box 化）を踏襲。
- ⚠️ 一様ランダム性と「小休止合わせ」はトレードオフ。**どこまで条件付けるかはサーベイ＋研究判断**（measurement 独立性を壊さない範囲）。

### (II') 落合フォーマット文献サーベイ（`literature-card` skill）

- トピック: ESM/EMA サンプリングスケジュール（signal/interval/event-contingent）、opportune moment/受容性、
  割り込み可能性（breakpoint/負荷依存）、通知タイミング、最小侵襲介入。
- 起点（references.md 既出）: [V1] Pejovic ESM・[V2] Sahu 受容性・[V4] Qian MRT・[V14] Anderson interruptibility。
- 新規候補（WebSearch で実在確認のうえ V 名前空間へ append・捏造禁止・provisional 可）:
  ESM 方式論（Csikszentmihalyi/Larson の ESM 原典系）、interruptibility（Adamczyk & Bailey / Iqbal & Bailey の breakpoint）、
  notification timing（Mehrotra 等）。
- 各カードに 6 項目＋「やり残し」＋GSE §4 への含意。`_index.md` 追記、出典は `citation-ssot` 経由で append-only。

## 変更対象

- `src-tauri/src/analysis/probe_scheduler.rs` — スケジュール方式/パラメータ・テスト追加
- `src-tauri/src/lib.rs` — 駆動側のパラメータ供給・poll・（必要なら）probe Opportunity ゲート配線
- `src/components/ProbeCard.tsx` / `Overlay.tsx` / `App.css` — 非侵襲提示（必要なら）
- `docs/literature/<date>-probe-timing-interruptibility.md`（新規カード）・`docs/literature/_index.md`
- `docs/references.md`（V 名前空間 append）・`docs/research-positioning.md` §3/§4（還元）

## テスト戦略

- **純ロジック単体テスト**: 模擬 driver で (a) クラスタ→枯渇の再現、(b) 是正後の分散（gap 分布・件数・一様性監査）。
- **replay 回帰**: `gse-replay --snapshot` byte-equal（スケジューラは feat 出力に影響しないが確認）。seed 固定で決定性。
- `cargo test --workspace`。

## 既存パターンとの整合性

- `architecture-rules`: 純スケジューリングは `analysis/` に閉じ OS API を呼ばない（引数注入）。
- `reproducibility-discipline`: 模擬実験を `experiments/` に記録（任意）。
- `data-privacy`: プローブに本文・タイトルを載せない（ProbeId は seeded・型で混入排除）。

## ロールバック計画

スケジューラ変更はパラメータ＋純ロジックに限定し、replay 決定性で回帰検出。問題時はパラメータを現行へ戻す。
ブランチ `fix/probe-scheduling-spread` 等で隔離。
