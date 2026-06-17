# Task — calibration-blind-dashboard (v0.3 較正セッションの blind/minimal メイン画面)

## 背景

v0.3 較正スモークの核は「**モデル出力非依存**のランダム時点プローブ + 申告前 30 秒の時間隔離 +
criterion label + C-index + 2段ゲート」。しかし現行 `Dashboard.tsx` は Current State /
Flow / Incubation / Stuck の確率を表示しており、v0.3 設計原則「**モデルを被験者に一切見せない**」と
衝突する。較正セッション中に X/Y/p_stuck/推定状態を見せると、主観回答がアンカリングされ
**測定独立性が壊れる** (criterion label が汚染される)。

## ゴール

v0.3 較正セッション中の**既定メイン画面を blind/minimal dashboard に変更**し、モデル出力を
被験者に見せない状態で `ProbeCard` / `VignetteTest` / `session_meta` / `interventionEnabled` の
既存フローを維持する。`calibrationMode` など**明示的な状態**で分岐し、暗黙条件にしすぎない。

## スコープ

### 含むもの
- v0.3 較正セッション用の blind/minimal Dashboard 実装 (較正中はモデル出力を非表示)。
- `calibrationMode` 等の明示状態による画面分岐 (通常/デバッグ Dashboard は残してよい)。
- Start 画面を研究設計に合わせる (較正中は介入既定オフ維持・尺度理解テスト導線維持)。

### 含まないもの
- PreReg-1..8 の閾値や判定契約の変更。
- HMM / `calibration_eval` / cohort 判定ロジックの変更。
- Nudge/Wall の効果検証、MRT、介入ポリシー再設計。
- NDJSON 生ログ・キーストローク内容・本文・ウィンドウタイトルの取り扱い。
- 大規模なデザイン刷新。

## 受け入れ条件

- [ ] v0.3 較正セッション開始後、メイン画面に Flow / Incubation / Stuck / Current State /
      確率バー (および GT カウンタ・状態説明文) が**表示されない**。
- [ ] 較正中に表示してよいもの: セッション経過時間 / Keyboard・Hook 状態 / Monk Mode (介入有効状態) /
      セッション終了ボタン / 必要最小限の権限警告。
- [ ] `ProbeCard` は従来どおり Overlay に表示され Q1/Q2 回答ができる (「送信成功後にのみ閉じる」を壊さない)。
- [ ] `VignetteTest` は従来どおり動く。
- [ ] `interventionEnabled=false` の較正セッションでは Nudge/Wall が表示されない。
- [ ] ランダムプローブの選定ロジック・モデル状態・X/Y・p_stuck は較正画面に表示しない。
- [ ] TypeScript で `any` を増やさない。
- [ ] 可能な範囲で `npm` / `cargo` の既存検証を実行。実行不可なら理由を design.md / 完了報告に明記。

## 関連ドキュメント / 参照
- `.idea/GSE_事後ラベリングシステム設計書_v0.3.md`
- `docs/preregistration-v0.3.md` / `docs/functional-design.md` / `docs/glossary.md`
- `src/App.tsx` / `src/components/Dashboard.tsx` / `src/components/ProbeCard.tsx` /
  `src/components/VignetteTest.tsx` / `src/components/Overlay.tsx` / `src/App.css`
- 必須 Skill: `typescript-standards` / `data-privacy` (必要に応じ `intervention-design`)

## 運用メモ
- /reimagine 適用: **No**
- 理由: アーキテクチャ・公開 API の再設計ではなく、v0.3 較正時の UI 表示を測定独立性に合わせて
  制限する明確な実装タスク。`calibrationMode` 等の状態分岐設計は要るが、既存 App/Dashboard/ProbeCard の
  流れに沿った小さめの feature。
- ブランチ: `feature/calibration-blind-dashboard` (起点 = main 295a481 = A+B+C+D+E 統合済 tip)。
- 作業ツリーに既存の未コミット infra(Codex bridge)+docs が残存 (E と同様、本タスクと分離・選択 add)。
