# 設計 (probe-card-ui)

## 実装アプローチ

**既存オーバーレイ窓を「ウィジェットモード」で右上小ボックスに縮小する** (新窓は作らない=Wall 窓へ
の回帰リスクを避ける)。プローブが単独表示のときだけ窓を小ボックス化し、カード以外を OS レベルで
クリック透過にする。Wall と Nudge は現状維持 (全画面)。

### オーバーレイ表示モード (Overlay.tsx の統合 effect)
```
if (isWallActive):            maximize() + setIgnoreCursorEvents(false)   // 全画面ブロック (現状維持)
else if (probe && !nudge):    box(右上) + setIgnoreCursorEvents(false)    // 非ブロック (本タスクの核)
else if (nudge || probe):     maximize() + setIgnoreCursorEvents(false)   // nudge or 同時表示 → 現状維持
else:                          hide()
```
- box 化: `unmaximize()` → `setSize(LogicalSize(W,H))` → `setPosition(LogicalPosition(右上))`。
  右上座標は `currentMonitor()` の size/scaleFactor から算出 (logical)。多モニタは monitor.position を加算。
- box から戻る (nudge 出現/wall): `maximize()` で全画面へ復帰。
- **全て try/catch。失敗時は maximize()+ignore(false) にフォールバック** (= 現状挙動。悪化させない)。
- nudge は `top:42%` 配置のため box 化すると位置が崩れる → **nudge では box 化しない** (scope 最小化)。

### カード演出 (ProbeCard.tsx + App.css)
- ProbeCard を **右上** に (`top` 配置へ。現状 `bottom`)。
- スライドイン animation (`probe-card-pop` クラス + keyframes)。gentle に「ぴょこっと」。

## 変更対象

### 修正するファイル
- `src/components/Overlay.tsx` — `probeActive`/`nudgeOpacity`/`isWallActive` から表示モードを決める
  統合 effect に置換。box 化 (resize+position+monitor) を追加。Wall/Nudge は現状維持。
- `src/components/ProbeCard.tsx` — 配置を bottom→top-right に。`probe-card-pop` クラス付与。
- `src/App.css` — `.probe-card-pop` + `@keyframes probe-pop-in` を追加。

### 新規作成 / 削除
- なし (新窓・新依存なし)。

## 影響範囲
- Wall: 全画面ブロック維持 (effect 最初の分岐で maximize)。回帰なし。
- Nudge: 現状維持 (box 化対象外)。位置・ブロック挙動とも不変。
- Probe 単独時のみ非ブロック化。probe+nudge 同時はまれで、安全側 (全画面) に倒す。

## 既存パターンとの整合性
- typescript-standards: `any` 不使用・IPC/window API は型付き・ビジネスロジックを足さない (UI のみ)・
  失敗時フォールバック (try/catch)。状態は useState/useRef のみ (外部ライブラリ追加なし)。
- intervention-design: Wall/Nudge トリガー・解除ロジックは不変 (UI 配置と窓サイズのみ)。

## テスト戦略
- `tsc` 型チェック + `vite build` 緑。`cargo build` 緑 (Rust 不変だが念のため)。`cargo test --workspace` 緑。
- **GUI 挙動 (右上スライドイン・クリック透過・Wall 全画面維持) は実機 (Win) で手元検証**
  (ヘッドレスでは window resize/cursor 挙動を検証不可)。フォールバックで最悪でも現状維持。

## ロールバック計画
- frontend のみの変更。問題時は branch 破棄で main へ戻る。box 化が不調なら effect の分岐を
  「常に maximize」にすれば即時現状復帰 (フォールバックと同じ)。
