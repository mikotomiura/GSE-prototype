# 設計: idle オーバーレイの幾何的退避

## アプローチ
idle 遷移時に `ignoresMouseEvents=YES`（現状）に**加えて**、オーバーレイ窓を
**画面外へ退避（+ 1x1 縮小）**する。show 時（Probe/Nudge=box / Wall=全画面）は既存の
`setSize`/`setPosition` がそのまま復帰させるので、追加の復帰処理は不要。

理由（多層防御）:
1. 幾何退避は OS 退行（Tahoe 26.x）や ignoresMouseEvents の tri-state バグに対して**免疫**。
   画面に重なる領域が無ければ、どの経路でもクリックを奪えない。
2. ignoresMouseEvents=YES は二次ガードとして残す。
3. revert された card 窓方式が既に採っていた実績ある手法（-20000,-20000）。

## 変更対象（予定）
- `src/components/Overlay.tsx`
  - idle 分岐（現 167-174）で `setOverlayInteractive(false)` に加え、
    `win.setPosition(new PhysicalPosition(-20000, -20000))`（＋必要なら `setSize(1x1)`）を実行。
  - 退避は **show より前に上書きされない**よう、統合 effect の依存・cancelled ガードと整合させる
    （stale effect が退避を後から上書きしない / 退避が show を後から潰さない順序）。
  - `setOverlayInteractive` 失敗時でも退避は実行されるよう、退避を ignoresMouseEvents 設定と
    独立に（try/catch を分ける）行う。← これが「panel 変換失敗時の全画面ブロック」増幅条件を断つ。
- `src-tauri/src/overlay_panel.rs:55` … 「画面外退避するので常駐コストは無視できる」コメントを、
  実装に合わせて「idle 時に Overlay.tsx が画面外退避する」旨へ修正（嘘コメント解消）。
- （任意・推奨）`ignoresMouseEvents` 読み返しの番兵: Rust に NSWindow の
  `ignoresMouseEvents` 値を返す debug command を追加し、回帰検知に使う
  （`.steering/20260625-macos-overlay-clickthrough-fix/next-session-prompt.md:32` の積み残し）。

## 検討した代替案と却下理由
- `window.hide()` / `orderOut:` … D10 で却下済み（webview JS 休眠で probe_triggered 取りこぼし）。
  Web 調査でも occlusion/App Nap でタイマー throttle と確認。→ 採らない。
- CSS `pointer-events:none`（body）… DOM 内ヒットテストのみ変更。NSWindow/WKWebView の
  画面領域は残りクロスアプリ透過にならない（tauri#11461 で不十分と確認）。→ 単独では不可。
- ignoresMouseEvents 単独強化 … OS 退行/ tri-state バグに脆弱（本件の現状そのもの）。→ 不十分。

## テスト戦略
- ロジック: Overlay.tsx の idle 退避は実機依存（setPosition の効果）。`cargo test` 範囲外。
- 回帰: `analysis/` は無関係。`gse-replay --snapshot` / `emit_schema` は影響なし（UI のみ）。
- 実機 smoke（必須・runbook 化）:
  1. Probe 発火 → カードが見える・カード内クリック可・カード外は背後へ透過。
  2. Probe 応答 → idle → **画面全域**で背後アプリ（ブラウザ等）がクリックできる。← 本件の主眼。
  3. Wall 発動 → 全画面ブロック（QR/ボタンのみ可）。解除 → idle で背後クリック可へ復帰。
  4. 前面エディタのタイピングフォーカスが奪われない。
  5. Windows 非回帰（Probe/Wall/idle）。
- HMM 不変（HMM_VERSION 据え置き・golden 再生成不要）。

## リスク / 留意
- 退避と show の競合（race）: 統合 effect は `cancelled` フラグで stale を無効化済み。
  退避処理も同じ effect 内 or 同じ cancelled ガード下に置き、新 state（show）を潰さないこと。
- マルチモニタ: -20000,-20000 は全モニタ左上外。負方向に十分大きい値で全構成をカバー（card 窓方式と同値）。
- always_on_top + CanJoinAllSpaces のまま退避するので、Space 切替でも露出しない。

## 進め方（次セッション）
1. `/start-task`（または本ディレクトリを継続）→ `architecture-rules` / `intervention-design` /
   `typescript-standards` Skill 参照。
2. 実装 → `cargo build --target aarch64-apple-darwin` → 実機 smoke。
3. `/finish-task`（code-reviewer + security-checker + /cross-review 必須）。
4. 検証後に memory `macos-overlay-clickthrough-bug` を「idle 残存も解決」へ更新。
