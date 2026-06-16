# 設計 — calibration-blind-dashboard

## 実装アプローチ

v0.3 較正セッションの**測定独立性**を守るため、メイン画面 (`Dashboard`) からモデル出力
(Current State / Flow・Incubation・Stuck 確率バー / GT カウンタ / 状態説明 info-box) を
**較正中は非表示**にする。`App` に **明示的な `calibrationMode` 状態** (既定 ON = v0.3 既定) を持たせ、
Start 画面のトグルで切替可能にする。`calibrationMode=true` のとき `Dashboard` は blind/minimal 表示。

**フロントエンドのみで完結** (backend / schema / record_session_meta は変更しない)。
理由: blind 化は純粋に「被験者に何を見せるか」という UI 表示の制約であり、track="main" /
interventionEnabled は既に session_meta に記録済み。calibrationMode を NDJSON に永続化する必要はなく、
A schema 凍結・スコープ「schema 変更しない」を守れる。

新規コンポーネントは作らず **`Dashboard` に `calibrationMode` prop を足して既存セクションを条件表示**する。
理由: blind 表示も「セッションバー + 権限バナー + Monk Mode + 終了ボタン」という Dashboard の
既存要素をそのまま使う。権限バナー (macOS/Windows の権限フロー約 180 行) を別コンポーネントへ
複製すると二重保守になるため、単一コンポーネントの条件表示が最小差分・最低リスク。

### 較正中に「隠す」もの (モデル出力 = アンカリング源)
- `Current State` カード (dominant 状態名)
- `metrics-container` (Flow / Incubation / Stuck の確率バー + %)
- `gt-counter` (Flow/Inc/Stuck の自己ラベル累積 — 自分の状態傾向が見えると主観回答を汚染)
- `info-box` (Incubation/Stuck の意味を説明する文)
- コンテナの `state-${dominant}` クラス (背景色で状態を暗示しないよう中立クラスに置換)

### 較正中も「見せてよい」もの (要件どおり)
- `session-bar` (経過時間 + Keyboard / Hook 状態)
- 権限バナー (hookActive=false 時の必要最小限の警告)
- Monk Mode トグル (= 介入有効状態の表示・操作)
- セッション終了ボタン
- 較正モードであることの中立的な注記 (新規・モデル状態は含めない)

## 変更対象

### 修正するファイル
- `src/App.tsx` —
  - `const [calibrationMode, setCalibrationMode] = useState(true);` 追加。
  - Start 画面に「較正モード (モデル出力を非表示)」チェックボックス (既定 ON) を追加 (interventionEnabled の近く)。
  - `<Dashboard ... calibrationMode={calibrationMode} />` を渡す。
- `src/components/Dashboard.tsx` —
  - `DashboardProps` に `calibrationMode?: boolean` 追加 (destructure 既定 false)。
  - 上記「隠すもの」を `{!calibrationMode && (...)}` で条件表示。コンテナ class を較正時は中立 (`state-calibration`)。
  - 較正時に中立注記 (例: 「較正モード — 主観回答の独立性を保つため推定状態は表示していません」) を表示。
- `src/App.css` — `.state-calibration` (中立背景) と `.calibration-notice` の最小スタイル追加。

### 新規作成するファイル
- なし (新規コンポーネントは作らない)。

### 削除するファイル
- なし。

## 影響範囲
- `Overlay` / `ProbeCard` / `VignetteTest` は**無変更**。ProbeCard は overlay ウィンドウで従来どおり表示
  (`!isWallActive && <ProbeCard/>`)・「送信成功後にのみ閉じる」挙動は ProbeCard 内部のため不変。
- `interventionEnabled=false` → backend が action="none" を返す → Overlay の nudge/wall 非表示 (既存保証・不変)。
- backend / Tauri コマンド / schema / NDJSON は無変更。Overlay は p_stuck を表示に使っていない (nudge 透明度計算のみ) ため model 漏れなし。
- cognitiveState ポーリング (500ms) は継続するが**表示しないだけ** (アーキテクチャ不変・keyboardIdle 等に必要)。

## 既存パターンとの整合性
- 状態管理は組み込み `useState` のみ (typescript-standards ルール3)。`any` を増やさない (ルール1)。
- ビジネスロジックは frontend に持ち込まない (ルール2) — 表示有無の分岐のみで閾値判定は追加しない。
- prop 追加は既存の `isMonkMode` / `hookActive` を Dashboard に渡すパターンと同型。
- CSS クラスは kebab-case (ルール4)。

## テスト戦略
- `npm run build` (tsc 型チェック + vite ビルド) で型エラー・`any` 混入なしを確認。可能なら `npm run lint`。
- 手動 (実機・headless 不可): 較正セッション開始 → メイン画面に Flow/Inc/Stuck/Current State/確率バー/GT が
  出ないこと、ProbeCard が overlay に出て Q1/Q2 回答できること、VignetteTest が動くこと、
  interventionEnabled=false で nudge/wall が出ないこと。実行不可分は完了報告に明記。
- cargo 検証は不要 (Rust 無変更) だが、念のため `cargo build` 緑を確認 (回帰なし)。

## ロールバック計画
- フロントエンド 3 ファイルの追加分のみ。calibrationMode 既定を false に戻すか当該コミット revert で
  従来 Dashboard に即復帰。backend 不変のため副作用なし。
