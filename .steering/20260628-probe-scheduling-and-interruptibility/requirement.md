# ランダムプローブの分散タイミング化・非侵襲化 ＋ 落合流 文献サーベイ

## 背景

実機（v2 アプリ）で **ランダムプローブが初期に立て続けに 3 回ほど高頻度で出た後、以降ほぼ出なくなる**
挙動を観測（研究者報告）。プローブ駆動の criterion label（Q1 摩擦 / Q2 前進）は **X1 較正の主データ**で、
時点が**セッション全体に程よく散らばる**ことが妥当性の前提（一様ランダム性）。初期クラスタ＋以降枯渇は
較正データを偏らせ、X1（GATE3 C-index）を毀損する。

現実装は `src-tauri/src/analysis/probe_scheduler.rs`：**同次 Poisson + rolling thinning**（純ロジック・seed 注入）。
指数間隔 `-ln(1-u)/λ` で候補抽選し、候補到来時に制約で間引く:
- **away**: `idle_ms ≥ away_idle_ms` → 棄却
- **gap**: 直近発火から `gap_min_ms` 未満 → 棄却
- **cap**: `cap_window_ms` 内に `cap_count` 件発火済み → 棄却

「初期クラスタ→以降枯渇」は **cap 枯渇（cap_window が長すぎ／セッション規模で 3 件到達後ずっと抑止）**、
**λ 過大**、**gap_min と相互作用**、または **idle→away 抑止（LAST_KEY_MS=0）** の疑い（要・実値確認）。

加えて研究者の要望: プローブは **連続的タイミングで多く出すのでなく程よく散らばせ**、かつ
**極力ユーザーを邪魔しない形**で出す。これに関し、**落合フォーマットの文献サーベイ**（`literature-card` skill）で
ESM/プローブ提示タイミングと「最小侵襲な介入/割り込み可能性」の知見を収集し、設計判断に接地したい。

## ゴール

1. プローブが **セッション全体に均す形で分散**して出る（初期クラスタ＋枯渇を解消）。一様性を監査で確認。
2. プローブ提示が **非侵襲**（能動タイプ中は出さない/小休止に合わせる、穏やかな onset、非ブロック小ボックス）。
3. **落合サーベイ**で (a) ESM/プローブのサンプリングスケジュール、(b) 割り込み可能性/最小侵襲介入 の知見を
   `docs/literature/` にカード化し、`references.md`（V 名前空間）に追加、`research-positioning.md` §3/§4 へ還元。

## スコープ

### 含むもの
- `probe_scheduler.rs` のパラメータ（λ / gap_min / cap_count / cap_window / away_idle）と駆動（lib.rs）の調査・是正
- 「初期クラスタ→枯渇」の**再現と原因特定**（実値・実ログ・純ロジックテスト）
- 非侵襲提示（能動タイプ中の抑止＝probe 版 Opportunity ゲート、onset、配置）の設計
- 落合フォーマット文献サーベイ（`literature-card` skill、V1/V2/V4/V14 ＋新規ソース）

### 含まないもの
- HMM/特徴量・介入ポリシー本体の変更（必要なら別タスク）
- F/I/S 分類の実装（非スコープ・研究方針どおり）

## 受け入れ条件

- [ ] 「初期クラスタ→枯渇」の原因を特定し、`probe_scheduler.rs` の純ロジックで再現テスト化
- [ ] パラメータ調整後、模擬セッションで**プローブ時点がセッション全体に分散**（一様性監査・gap 分布を確認）
- [ ] 非侵襲化（能動タイプ中抑止・小休止合わせ・穏やか onset）を実装 or 設計確定
- [ ] 落合カード ≥3 本を `docs/literature/<date>-probe-timing-interruptibility.md` に作成、`_index.md` 追記、出典を `references.md`(V) に append
- [ ] `research-positioning.md` §3/§4 に「やり残し」を還元（probe timing/interruptibility の差分）
- [ ] `cargo test`（probe_scheduler 純ロジック）/ replay 回帰が通る
- [ ] code-reviewer + `/cross-review`、`/finish-task`

## 関連

- `src-tauri/src/analysis/probe_scheduler.rs`（純ロジック・DB-1 同次 Poisson + thinning）
- `src-tauri/src/lib.rs`（プローブ駆動スレッド・実時刻・emit・パラメータ供給）
- `docs/functional-design.md` §2.x（v0.3 較正・一様ランダム要件 §4.1/§4.3）
- 既存参考: [V1] Pejovic ESM / [V2] Sahu 受容性 / [V4] Qian MRT / [V14] Anderson interruptibility（references.md）
- skill: `literature-card`（落合フォーマット）・`reproducibility-discipline`（実験記録）
