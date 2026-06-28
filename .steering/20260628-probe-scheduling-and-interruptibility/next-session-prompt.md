# 次セッション用 開始プロンプト（ランダムプローブの分散化・非侵襲化 ＋ 落合サーベイ）

> このファイル本文を新しいセッションの最初に貼る。GSE-prototype 用。
> コード（probe_scheduler / lib.rs / 一部 frontend）＋研究（落合サーベイ）の混合タスク。

## 0. 一言ゴール
ランダムプローブが **初期に 3 連発→以降枯渇**する挙動を是正し、**セッション全体に程よく分散**かつ
**非侵襲**に出す。あわせて **落合フォーマット文献サーベイ**（`literature-card` skill）で probe timing /
最小侵襲介入の知見を集め、設計と `research-positioning §3/§4`・`references(V)` に接地する。

## 1. 最初にやること
1. `.steering/20260628-probe-scheduling-and-interruptibility/` の requirement.md / design.md / tasklist.md を読む。
2. `src-tauri/src/analysis/probe_scheduler.rs`（純ロジック・同次 Poisson + thinning）と `lib.rs` の駆動側を読み、
   **現行パラメータ実値**（λ / gap_min_ms / cap_count / cap_window_ms / away_idle_ms / poll / seed）を洗い出す。
3. 純ロジックの**模擬 driver で「クラスタ→枯渇」を再現する単体テスト**を先に書く（TDD）。

## 2. 原因仮説（切り分ける）
- **cap 枯渇**: `cap_window_ms` が長すぎ/セッション規模 → 早期に cap_count 到達で以降ずっと棄却（最有力候補）。
- **λ 過大** / **gap_min 過小**: 序盤クラスタ。
- **idle→away 抑止**: `last_key_ms==0`/idle 増で away 判定（PR#36 macOS 失効と同系。実ログ確認）。

## 3. 是正方針（サーベイで裏取り）
- 目標レートを保ちつつ**均す**: λ＋gap_min（最小間隔）＋**cap はローリングのレート制限**（総量打ち切りにしない）。
- 枯渇防止に **soft max-gap** を検討（一様性を壊さない範囲）。純ロジック・seed 決定性・OS/RNG/時刻は引数注入を維持。
- 非侵襲: 能動タイプ中（直近打鍵 <2s）は遅延、小休止合わせ、穏やか onset、右上非ブロック小ボックス。
  ⚠️ 一様ランダム性 vs 小休止合わせのトレードオフは measurement 独立性を壊さない範囲で（研究判断）。

## 4. 落合サーベイ（literature-card skill）
- 起点（references.md 既出）: [V1] Pejovic ESM / [V2] Sahu 受容性 / [V4] Qian MRT / [V14] Anderson interruptibility。
- 新規は WebSearch で実在確認のうえ V 名前空間へ append（捏造禁止・provisional 可）。候補: ESM 原典系、
  interruptibility の breakpoint（Adamczyk & Bailey / Iqbal & Bailey）、notification timing。
- 落合カード ≥3 本→`docs/literature/<date>-probe-timing-interruptibility.md`、`_index.md` 追記、出典 append（citation-ssot）。
- 「やり残し」を `research-positioning §3/§4` に還元。

## 5. 制約・完了基準
- `architecture-rules`: 純スケジューリングは analysis/ に閉じ OS API を呼ばない。`data-privacy`: プローブに本文/タイトルを載せない。
- `cargo test --workspace` ＋ `gse-replay --snapshot`（byte-equal）が通る。
- code-reviewer + `/cross-review`（`bash scripts/run-codex-*.sh`）→ commit → `/finish-task`。

## 6. 順序メモ
- 落合サーベイは research-positioning §3/§4・references(V) に追記する。**R1 反映タスク
  （`.steering/20260628-r1-positioning-review-reflection/`）は完了済み（branch `docs/r1-review-reflection` / commit 36891a7・未 merge）**。衝突しないので本タスクを走らせてよい。
- ⚠️ R1 で research-positioning に**層モデル（§0 L0 軸 / L1 Stuck=p_stuck / L2 Need / L2' Opportunity）**が入った。
  本タスクの probe timing/interruptibility は **L2' Opportunity（小休止合わせ）と measurement 独立性（L0 較正の汚染回避）のトレードオフ**に直結する。
  サーベイの「やり残し」を §3/§4 に還元する際は**この層語彙に揃える**（probe timing は L0 較正データ源、Opportunity 合わせは L2' の介入機会判定、と取り違えない）。
- R1 docs が未 merge のため、編集着手前に `docs/research-positioning.md` の最新（branch 反映後）を確認すること。
