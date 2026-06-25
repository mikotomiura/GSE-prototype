# 次セッション用 開始プロンプト（macOS でオーバーレイのカード/Nudge がクリックスルーして反応しない問題の修正）

> このファイル本文を新しいセッションの最初に貼る。GSE-prototype 用。
> 本タスクは調査・codex 相談まで完了済み。steering は
> `.steering/20260625-macos-overlay-clickthrough-fix/`（requirement.md / design.md / decisions.md）に作成済み。
> これを**引き継いで実装**する。実装系なので `/start-task` は dir 作成済みのためスキップ可、`/fix-bug` で進める。

---

## 依頼
macOS で、被験者向け非ブロック介入 UI のプローブ回答カード（`ProbeCard.tsx`）と Nudge カード
（`Overlay.tsx`）が**表示はされるがボタンを押しても反応しない**（クリックが overlay 窓を素通りして
背後アプリが反応する）バグを修正する。**カード領域のクリックはボタンに届き、カード外は背後へ透過する
非ブロック設計（フォーカス非奪取）を維持**したまま直す。`*.rs`/`*.tsx` 変更につき
`architecture-rules`/`rust-standards`/`typescript-standards`/`intervention-design`/`hook-constraints`
（macOS NSWindow 操作のメインスレッド/GCD 制約）を必須参照。

## 確定済みの事実（前セッションで特定）
- overlay は独立窓 label="overlay"（`src-tauri/src/lib.rs:1681`）: `transparent(true) decorations(false)
  always_on_top(true) skip_taskbar(true) visible(false)`、非フォーカス。Tauri v2 + `macos-private-api`。
- カード表示時、`Overlay.tsx` 統合 effect（`:130-211`）が窓を右上 box（`PROBE_BOX_W=390 ×
  PROBE_BOX_H=430`）へ縮小し `win.setIgnoreCursorEvents(false)`（`:191`）を await。例外なく box 化は
  成功（カードは見える）が、クリックは透過し続ける（実機 macOS / tauri dev で確認）。
- CSS は無実: `.overlay-root` は `pointer-events:auto`、カードも auto（Nudge は明示 auto・`:344`）。
- `ignoresMouseEvents=NO` なら 390×430 box 全体がクリックを取るはずだが透過する → **set 呼出が
  実効化していない or 透過窓 hit-test/first-mouse 問題**。Probe / Nudge 両方で発症。
- `#1`（logger disconnected でカード無反応）とも F4（macOS tap idle/away）とも**別の根本原因**。
  クリックがそもそも webview に届かないため `record_realtime_*` / `record_intervention_dismiss` まで到達しない。

## 進め方（root-cause-first・design.md / decisions.md に詳細）
### Step 0【真因の切り分け（最優先・憶測で固定しない）】
- Rust 側で overlay の NSWindow `ignoresMouseEvents` を**読み返す**デバッグ手段を入れ、JS が
  `setIgnoreCursorEvents(false)` した後の実値を確認する（macos cfg・メインスレッドで実行）。
  - (i) 値が YES のまま → set 呼出が no-op。→ Rust 側で直接設定 / 窓再生成 / 専用窓へ。
  - (ii) 値は NO だが透過 → 透過窓 per-pixel hit-test + `acceptsFirstMouse:`/`canBecomeKeyWindow`
    問題。→ NSPanel 化 / acceptsFirstMouse 許可 / 専用窓へ。

### Step 1【修正（診断結果で確定。候補の優先順位）】
1. **専用カード窓の分離**（第一候補・codex ⑤）: 全画面透明 overlay と clickable card を別窓にする。
   カードは小さな・適切に key を受けられる（ただし非アクティベートな）窓に載せ、透過 overlay の
   hit-test 問題を回避。Wall（全画面ブロック）経路は現状維持。
2. **Rust 側 overlay interaction state machine**（codex ④）: NSWindow 状態（ignore/size/pos）を Rust に
   集約し、JS は intent（show card / hide）だけ送る。JS・Tauri API・Rust 多経路の競合を断つ。
3. **小箱 C**（補助）: box を card サイズに最小化＋`NSScreen.visibleFrame` 基準で再配置。multi-display/
   Stage Manager/フルスクリーン Space で崩れる弱点と、透明余白がクリックを奪う安全性問題を許容できる
   場合のみ。
4. **D（カーソル追従）は不採用**（信頼性・プライバシーコスト）。

### Step 2【codex の盲点を必ず検証項目に入れる】
- **初回クリック**: 背後アプリが active のまま、カードへの**初回クリックでボタン action が発火**するか
  （`acceptsFirstMouse:` 相当）。
- **multi-display / Retina scale / フルスクリーン Space / Stage Manager / Mission Control 後**の座標・
  クリック領域。`visibleFrame` 基準の再配置と display change / scale 変更時の再計算。
- **透明余白の安全性**: カード外周でクリックを奪う領域を最小化（背後の重要 UI を潰さない）。
- **真値ログを残す**: `ignoresMouseEvents` 読み返しを回帰検知用に残す（Tauri/WRY 更新での再発防止）。

### Step 3【テスト】
- 窓ジオメトリ計算（visibleFrame クランプ等）は純関数化して `cargo test`。
- macOS `tauri dev` 実機: Probe（回答する/思い出せない/✕）・Nudge（詰まってない/今はもがきたい/閉じる）が
  押せて `record_realtime_*` / `record_intervention_dismiss` が走る。背後 active のまま初回クリック発火。
  カード外は背後へ透過。
- Windows 非回帰（少なくともロジック非破壊・できれば実機）。HMM/schema 不変（触らない）。

### Step 4【完了処理】
- code-reviewer ＋ security-checker（NSWindow/objc unsafe・プライバシー）→ `/finish-task` で `/cross-review`。
  ※ /cross-review 前に**無関係な未ステージ変更（budget.json/scripts/docs削除/MEMO/advice.md）を一時 stash**
  してから走らせる（混ぜない・Codex 自己ブロック回避。前タスクで実証済み）。
- ブランチ: 新規 `fix/macos-overlay-clickthrough`（独立 PR）。

## 真実源（先に読む）
- 本 dir の `requirement.md` / `design.md`（codex 指摘全文）/ `decisions.md`。
- `src/components/Overlay.tsx`（`:46-211` 統合 effect・setIgnoreCursorEvents、`:333-386` render・Nudge）。
- `src/components/ProbeCard.tsx`（listen・submitAnswer/Skip・カード DOM）。
- `src/App.css`（`.overlay-root` `:451`、`.nudge-card` `:480`、`.probe-card` 系・pointer-events）。
- `src-tauri/src/lib.rs`（`:1681` overlay WebviewWindowBuilder、`:1014` show、`:276` overlay 分岐）。
- 介入 UI を導入した commit `414ef1d`（この box+透過化で macOS が破綻した起点）。

## 制約
- 非ブロック維持（カード外は背後へ透過）＋**フォーカスを奪わない**。Wall 全画面ブロックは現状維持。
- macOS NSWindow/objc 操作は unsafe をラッパに隔離・**メインスレッド/GCD 制約厳守**（hook-constraints mac-2/5）。
  `winapi`/`println!`/`eprintln!`/`any` 禁止、Rust は `tracing`・`anyhow`。
- Windows を回帰させない（現状クリックは効いている前提）。HMM/`schema_dto.rs` 不変。
- グローバル入力監視（案 D）はプライバシー設計（キーストローク非記録・data-privacy）と衝突するため避ける。
- diff に未関係な未ステージ変更を混ぜない。既存テストを無断削除しない。

## 補足（前セッションの状態）
- F4（macOS tap idle/away）は PR #36 でマージ済み・別問題。本バグはそれとは独立。
- codex-consult は**実施済み**（結果は design.md 反映）。再相談は必要時のみ。
