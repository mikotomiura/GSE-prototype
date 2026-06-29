# 次セッション開始プロンプト (オーバーレイ残存バグの厳密監査・Windows)

このタスクは **新しいセッションで実行**する。コピペで開始できるよう以下を渡す。

---

GSE の macOS/Windows 共通オーバーレイ窓 (`src/components/Overlay.tsx`) に残る「透明窓が画面に
残存し背後アプリのクリックを奪う」フロントエンドバグを **厳密に判定・修正**する。

## 最重要前提 (これを誤解しないこと)
- 先行タスク `20260629-macos-overlay-idle-clickthrough` の **幾何退避修正 (画面外 setPosition +
  setSize)** は **v0.1.21 にリリース済だが Windows で不十分**。実機で**ランダムプローブ後の idle
  残存がまだ発症**している。「修正済」前提で進めない。
- 観測 OS は **Windows 11** (被験者環境)。Windows は透明 WebView2 窓で `setIgnoreCursorEvents`
  が効かない (Tauri #11461) ため、幾何退避が唯一の堅牢策のはず — それが効いていない原因が焦点。
- **セッション記録は健全** (feat 1Hz 連続・probe 3/3 ラベル一致・session_end 正常)。本件は記録で
  なく **窓状態制御**の問題。

## やること (推測で直さず、計測で白黒つける)
1. `.steering/20260629-overlay-frontend-residue-audit/` の `requirement.md` と **`hypotheses.md`**
   (H1-H5・切り分け早道) を読む。先行 `20260629-macos-overlay-idle-clickthrough/` と memory
   `macos-overlay-clickthrough-bug` も読む。
2. Skill: `architecture-rules` / `intervention-design` / `typescript-standards` /
   `rust-standards` / `hook-constraints` を参照。
3. **計装を先に入れる**: Rust に窓状態読み返し debug command (`outerPosition`/`outerSize`/
   Windows の WS_EX_TRANSPARENT・macOS の ignoresMouseEvents) を `ensure_debug_enabled()` ゲート下で
   追加。Overlay.tsx の各遷移直後に読み返して tracing へ出す (D13 で実績の fe_dbg 様式)。
4. **状態行列で網羅判定** (Windows 実機・VITE_GSE_DEBUG=1 + GSE_DEBUG=1):
   {probe回答 / probeスキップ / nudge dismiss / nudge silent / wall解除 / probe→nudge / 連続probe}
   × 各遷移後 idle の **実窓位置/サイズ/クリック透過**。残存する状態を特定し H1-H5 を確定/棄却。
5. 真因に対し Windows で確実に効く修正 → 同 debug command で回帰番兵化 → Windows/macOS 両実機 smoke。
6. `cargo build` (両ターゲット) → `/finish-task` (code-reviewer + security-checker + /cross-review)。
7. 検証後 memory `macos-overlay-clickthrough-bug` を更新。修正が確定したら v0.1.21 を同 ver 再リリース
   (旧版削除・前セッションの手順: push→PR→merge→tag 再付与で CI ビルド)。

## 死守する非回帰 (D7-D13)
- Probe カード=カード内クリック可/カード外透過、Wall=全画面ブロック、フォーカス非奪取 (D12)、
  hide/orderOut 不使用 (D10)、maximize/setStyleMask 再適用なし (D8)、macOS 非回帰。

## 切り分けの早道 (hypotheses.md より)
- Wall 解除後も残存する? → 退避 API 系 (H4/H5)。しない → probe 固有 (H1/H2: probeActive 未リセット
  or 退避と box 配置の逆 race)。
- idle 確定の数秒後に再度窓位置を読む: 後で box に戻る → 上書き (H2/H3)。最初から box → idle 分岐
  未到達 (H1) か退避無効 (H4)。

## 注意 (前セッションからの引き継ぎ)
- ローカル main が origin より古い場合あり (未コミットの無関係作業と衝突)。`git stash -u && git pull
  --ff-only && git stash pop` で整える。修正は origin/main に入っている。
- 作業ツリーに無関係な未ステージ変更が多数。commit は対象ファイルを明示 pathspec で限定する。
