# wall-refire-root-and-dashboard-ui

## 背景 (実機フィードバック)
1. **Wall を何度解除しても毎回再発火する**(#24 の cooldown 修正後も解消せず)。
   真因をコードから特定: `App.tsx` の Wall 起動は `if (action==="wall" && !isWallActive) setTrue` で
   **エッジ検出が無い**。解除 (sensor-accelerometer→setFalse) 後も判定が "wall" のまま続く
   (特に overlay ウィンドウは `last_decision` を読むため lingering し、しかも action!=wall で false に
   する else が無い) ため、次ポーリングで即再起動 → 毎回再発火。#24 の cooldown は `decide()` 内のみで
   この lingering last_decision 経路には効かない。
2. **スタート画面で「尺度理解テスト」ボタンが見えない**。`.start-screen` が `justify-content:center` +
   `min-height:100vh` で overflow 非スクロールのため、800x600 窓でコンテンツが下に見切れて
   尺度理解テストボタン/ヒントがクリップされていた。
3. **ダッシュボードに「戻る」が無い**。終了は quit_app (アプリ終了) のみで、スタート画面へ戻る導線が無い。

## ゴール
- Wall は 1 エピソードにつき 1 回だけ起動し、解除後に再発火しない。
- スタート画面の全項目 (尺度理解テスト含む) が見切れず到達できる。
- ダッシュボード/ビネットからアプリを終了せずスタート画面へ戻れる。

## スコープ
### 含むもの
- App.tsx: Wall 起動に `wallHandledRef` エッジ検出 (非 wall→wall の立ち上がりのみ起動・解除後の
  lingering wall で再起動しない・action が wall を離れたら次エピソード許可)。
- App.css: `.start-screen` を `flex-start + overflow-y:auto + max-height:100vh` でスクロール可能に。
- Dashboard: onBack で「← 戻る」(setIsStarted(false)・アプリ終了しない)。ナビ行 (戻る/終了)。
- VignetteTest: 質問画面に「← 戻る (中断)」(onComplete)。
### 含まないもの
- backend / 介入判定ロジック / HMM / schema 変更 (今回 frontend のみ)。
- Wall の見た目 (全画面段階減光は維持・承認済)。

## 受け入れ条件
- [ ] Wall 解除後に再発火しない (エッジ検出)・新エピソードでは起動する
- [ ] スタート画面の尺度理解テストボタンが見える (スクロール可)
- [ ] ダッシュボードの「戻る」でアプリ終了せずスタート画面へ
- [ ] tsc+vite build 緑・cargo test 緑 (Rust 不変)

## 運用メモ
- /reimagine: No。別 PR・main 基点。frontend のみ。
