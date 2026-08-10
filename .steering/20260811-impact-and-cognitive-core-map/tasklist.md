# タスクリスト

## 1. 既存 SSOT の突き合わせ（読む）

- [x] `docs/research-positioning.md`（56 KB・**未読だった**）— §7 が 3 行しかないことを確認
- [x] `docs/architecture/personalization-and-online-learning.md`（104 KB・**リポジトリ最大・未読だった**）
- [x] `docs/architecture/gse-v2-overview.md` — 7 層アーキと「段階的に捨てる主張」5 件
- [x] `.idea/20260801-behavioral-context-online-latent-ml-design.md`
      （★ **`ls` に出ていたのに一度も開いていなかった**。冒頭に「昇格済み・歴史資料」「4 状態案は不採択」）
- [x] `docs/adr/README.md`（ADR-001〜010 の一覧・ステータス）
- [x] `docs/adr/ADR-006`（task_kind → β 配線・**Accepted・枠組み C**）
- [x] `docs/wbs-verification-halfyear.md`（grep）— ★ **Gate D / S / H。Gate H は拒否権を持つ**

## 2. 一次資料での確認（コード。docs を根拠にしない）

- [x] ★★ **推論が読んでいる入力を確定**（`features.rs:82` `calculate_features`）
      → **`timestamp` / `is_press` / `is_repeat` / `is_backspace` の 4 つだけ**
- [x] ★★ **`vk_code` は特徴量に入らない**（`loop_step.rs:197-206` の `pressed_keys` 重複排除のみ）
- [x] ★★★ **`is_paste` は `analysis/` 内でどこからも読まれていない**
      （`grep is_paste src-tauri/src/analysis/` = `features.rs` のテスト初期化のみ）
- [x] X/Y 合成式の重みと行番号（`engine.rs:336`・`0.30φ3+0.25φ6+0.25φ1+0.20φ5`）
- [x] HMM パラメータ数（`transitions: [f64; 9]` ＋ `emissions: [f64; 78]` = **87・全て手書き定数**）
- [x] obs 量子化（`obs = x_bin*5 + y_bin` 0..24 ＋ `obs=25` BS penalty = **26**）
- [x] β 定数と選択（`BETA_WRITING_*` / `BETA_CODING_*`・`engine.rs:311` の `if ime_open`）
- [x] `ime_open` の役割 2 つ（β 選択 ＋ `apply_backspace_penalty` の gate・`engine.rs:367`）
- [x] φ の定義（`features.rs:48` `clamp((x−β)/(κβ),0,1)`・**κ=2.0 固定**）
- [x] G1 のブロック構成（`experiments/20260801-controlled-friction-task/protocol.md`
      — 10 ブロック×5 分・[1]/[10] が copy positive control・[2]–[9] が HI4/LO4・強制比較 7 回）

## 3. 成果物

- [x] `impact-and-core-map.md` — A: 社会的インパクト／意義（層別・証拠の温度つき・**負の側面を独立節に**）
      ／ B: 認知の核（振り分け表・癖の 3 分類・Tier 0/1/2・反証ゲート G1–G4・PreReg-5 両立基準）
- [x] `requirement.md`（本タスクの受け入れ条件）
- [x] `design.md` — ★ **入力層 → 推定 → オンライン学習 → メディア表現の接続設計**
      （§4 の中核 = **表現層を `p_stuck` の下流に置かず、系統 A/B の 2 本に分ける**）
- [x] `tasklist.md`（本ファイル）

## 4. 受け入れ条件の確認

- [x] インパクトが層ごとに分解され、各主張に証拠の温度と一次根拠が付いている
- [x] 負の側面（計測の害 [P77] / moral placebo [P75] / 反芻 / 監視感 / チャネル停止 [P55]）が独立節にある
- [x] オンライン学習の振り分け表と癖の 3 分類が SSOT から正しく写されている
- [x] 入力層の実体が**実コード**で確認されている（§2 のとおり）
- [x] β の議論が **ADR-006 の Decision** と **φ が単調変換である実測**の両方に接地している
- [x] `docs/` と凍結対象に**変更なし**（`git status` で検証）
- [x] `research-positioning.md §7` に**直接書き込んでいない**

## 5. 残（優先度順）

- [ ] ★★★ **G1 の残り 2 名 → 判定**——§3.1 の 3 分岐が決まらないと Stage 1 以降の投資先が決まらない
      ⚠️★★ **2026-08-11 訂正**: 「G1 未実施」は誤り。**n=3 で凍結済み**（`d3caebd`）・**P010 が確証標本 1 人目として実施済み**・
      pilot（PILOT-mac / PILOT-win）済み。**`analyze.py` は一度も判定を出していない**ので結果はまだ無い
- [ ] ⚠️ **`experiments/20260801-controlled-friction-task/README.md §0` が古い**——
      「データ 1 件も無い」「n 未凍結」のままで `notes.md` と食い違う。**README §0 だけ読むと現状を誤る**
- [ ] ★★ **`impact-and-core-map.md` を `research-positioning.md §7` へ landing させるか**（研究者判断・§7 は確認要）
- [ ] ★ **Gate D/S/H を `research-positioning.md` へ写すか**（現在は WBS にしかなく、§8 の限界と分離している）
- [ ] ★ **表現層の試作（Stage 0'）は G1 を待たずに始められる**——ただし `toeexpand` 往復検証が未実施
- [ ] **期の幅 Δ の事前宣言**（ADR-009 が「P1 開始前に宣言する」と明記）＋ **logit か cloglog か未決**
- [ ] **`PersonalizationStore` の同意・削除 UI**（`data-privacy` の拡張・実装前に必須）
- [ ] **尺度 floor を Phase A の robust quantile 実装に入れる**（scope 検出器専用にしない）
