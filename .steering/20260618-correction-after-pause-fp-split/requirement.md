# correction_after_pause の FP/TP 分離診断 → Nudge HIR 改善

## 背景

Phase 0 (`20260618-intervention-eval-reason-sweep`) で判明:
- P000 13 session の有害 nudge (HIR=0.647, FP=22 / TP=12) は **100% が `correction_after_pause`**。
- post_burst_pause 由来は 0 件。
- `nudge_need` を上げる sweep は FP も TP も同時に削る（0.80 で HIR 半減するが recall も低下）。

カメラ提案 (`.idea/camera-gaze-need-opportunity-proposal.md`) の検討で、提案の抑制ルール
(`reading_like` = 低 correction / `off_screen` / `face_absent`) は、実測 FP 母集団
(correction_after_pause = **高** correction・on-screen) と**不一致**であることが判明。
→ カメラより先に keystroke 側で correction_after_pause の FP/TP を分離できないか検証する
(ユーザー選択: 「keystroke 側を先に詰める」)。

## ゴール

`correction_after_pause` の 22 FP (GT=PROTECT) と 12 TP (GT=STALL) を、決定時の特徴量
(p_stuck / f3 / f4 / f6 / idle_ms) で分離できるかを **production を変えずに診断**し、
分離可能なら Nudge HIR を下げる production tweak 候補を **3 案以内**、counterfactual で
HIR/recall を試算して提示する。

## スコープ

### 含むもの (まず Step 1 = 診断のみ)
1. ACT decision を (reason × GT) で層別し、各群の特徴量サマリ統計
   (count / p_stuck / f3 / f4 / f6 / idle_ms の min・median・max) を pooled で出す診断機能。
2. `gse-replay` に診断出力モードを追加（既存モードと相互排他）。
3. P000 13 session で実行し、correction_after_pause の FP 群 vs TP 群が特徴量で分離可能かを判定。

### Step 2 (Step 1 の結果次第・ユーザー承認後)
4. 分離する特徴があれば production tweak 候補 (≤3) を設計し、counterfactual で HIR/recall を試算。
5. 採用判断 → production 変更 (要れば policy version / golden 再生成)。

### 含まないもの
- カメラ/vision の実装 (doc 保存のみ、後続フェーズ)。
- Step 1 時点での production ロジック変更 (診断は完全に production 不変)。
- Phase 1 Need 校正・micro-randomization。

## 受け入れ条件 (Step 1)
- [ ] 診断機能が production 挙動を変えない (snapshot byte-equal / schema drift なし / 既存テスト緑)。
- [ ] correction_after_pause の FP 群と TP 群の特徴量分布を pooled で提示。
- [ ] 「分離可能か / どの特徴で / どのカットか」を結論づけ、Step 2 の tweak 候補方針を出す。

## 制約 (Phase 0 と同じ)
- analysis/ 純粋性、tracing のみ、anyhow、any/winapi なし。
- 診断出力は集計数値のみ (content・URL・window title を含まない)。
- 既存 golden snapshot byte-equal / schema drift なし。

## 関連
- `.steering/20260618-intervention-eval-reason-sweep/results.md` (FP=correction_after_pause の出所)
- `src-tauri/src/analysis/intervention.rs` calculate_opportunity (correction_after_pause: +0.15)
- `.idea/need-opportunity-improvement-plan.md` §5 (Nudge opportunity を reason 別に閾値分け)

## 運用メモ
- /reimagine 適用: No（Step 1 は診断で方針確定済み。Step 2 の tweak 設計時に複数案を比較する場合は再検討）。
