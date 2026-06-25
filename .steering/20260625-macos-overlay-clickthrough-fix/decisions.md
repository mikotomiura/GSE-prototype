# 設計判断

## D1. 実装前に codex-consult を実施（2026-06-25）
macOS 固有の透過 overlay クリックスルーは盲点が多いため、実装前に codex-consult で第二意見を取得。
結果は design.md「codex-consult の指摘」に反映。要点: ①非フォーカスとクリック受理は別問題
（acceptsFirstMouse/canBecomeKey）、②小箱は multi-display/Spaces で崩れる、③透明余白の
クリック奪取は安全性問題、④NSWindow 状態を JS/Rust 多経路で触ると競合 → state machine を Rust に寄せる、
⑤NSPanel 化 or 専用カード窓の分離が有力、⑥カーソル追従は最終手段、⑦真因（実 ignoresMouseEvents）を
読み返して確認してから固定。

## D2. root-cause-first で進める
真因（`setIgnoreCursorEvents(false)` が実効化しているか）が未確定。先に Rust で実 `ignoresMouseEvents`
を読み返して (i)YESのまま/(ii)NOだが透過 を切り分けてから fix 系統を選ぶ。憶測で固定すると
Tauri/WRY 更新で再発する（codex ⑦）。

## D3. 採用候補の優先順位（診断後に確定）
1. 専用カード窓の分離（全画面透明 overlay と clickable card を別窓に）— codex ⑤
2. Rust 側 overlay interaction state machine（JS は intent のみ）— codex ④
3. 小箱 C（card サイズに最小化＋visibleFrame 再配置）— 補助。multi-display/安全性の弱点を許容できる場合のみ
4. D（カーソル追従）— 不採用（信頼性/プライバシーコスト）

## D5. 診断結果と採用方針の確定（2026-06-25・実装セッション）
症状の再精査で真因を確定: 「クリックが overlay を素通りして**背後アプリが反応する**」は
`ignoresMouseEvents = YES` のまま（= JS `setIgnoreCursorEvents(false)` が no-op）を意味する。
acceptsFirstMouse の取りこぼし（仮説 ii）なら初回クリックは GSE 起動に消費されるだけで背後アプリは
反応しない。よって **仮説 (i)** を主因と判断。

採用: **Rust 側 click-through 権威化（codex ④）**。
- `overlay_macos.rs`: `[NSWindow setIgnoresMouseEvents:]` をメインスレッドで直接呼び、設定後の
  実値を `[NSWindow ignoresMouseEvents]` で読み返す（objc 最小 FFI、新規 crate 追加なし）。
- `lib.rs`: `set_overlay_interactive(interactive)` コマンド。macOS は run_on_main_thread→読み返し、
  非 macOS は従来の `set_ignore_cursor_events` に委譲（Windows 非回帰）。
- `Overlay.tsx`: 4 箇所の `setIgnoreCursorEvents` を `setOverlayInteractive()` 経由へ集約し、
  読み返し値と要求値の mismatch を console.warn（回帰検知）。失敗時は JS API へフォールバック。

専用カード窓（codex ⑤）は採用見送り: 主因が (i) なら不要で、窓追加は表示制御・Wall 経路の
複雑性とリスクが大きい。実機で (i) 修正後も透過するなら（= 仮説 ii / acceptsFirstMouse）、
WKWebView の acceptsFirstMouse スウィズリング or 専用窓を follow-up とする（runbook 参照）。

box ジオメトリ（小箱 C の multi-display/visibleFrame 課題）は今回触らない: 主因と独立で、
現状でカードは正しく表示されている（縮小は成功）ため。実機で座標崩れが出たら別タスク。

## D6. 真因の訂正と最小修正への差し替え（2026-06-26・D5 を上書き）
**D5 の仮説 (i)（ignoresMouseEvents が no-op）は誤り**だった。実機で Rust 直接 setIgnoresMouseEvents:NO
を入れても解決せず、ソースレベル調査（WRY/tao/Tauri issue + Apple docs）で真因を確定:

**真因 = 非 key 窓 + WKWebView の `acceptsFirstMouse` 既定 false。**
- overlay はフォーカスを奪わない設計のため **常に非 key 窓**。
- macOS では非 key 窓のビューへのクリックは、そのビューの `acceptsFirstMouse:` が YES のときだけ
  配送される（Apple「Handling Mouse Events」）。
- WRY の `WryWebView`（React ボタンが載る実体）は `acceptsFirstMouse` を attribute 値で返し、
  既定 **false**（WRY `wry_web_view.rs:59-61` / `lib.rs:874`）。tao のホスト NSView は YES を返すが、
  クリックを受けるのは内側の WryWebView。
- よって **全クリック**（初回だけでなく毎回。窓が key にならないため毎回が「first mouse」）が
  window 活性化扱いで握りつぶされ、ボタンに届かない。`ignoresMouseEvents` とは独立した別ゲートで、
  そこをいくら直しても解決しないのは当然だった。
- 出典: Tauri #4316 / WRY #637 / Apple Handling Mouse Events / WRY・tao ソース。

**採用修正（最小）**: overlay 窓生成時に `WebviewWindowBuilder::accept_first_mouse(true)` を付与
（Tauri 2.10 doc:「clicking an inactive window also clicks through to the webview」）。
これで非アクティブ窓のクリックが webview へ届く。key 化しない＝フォーカス非奪取は維持。
`setIgnoreCursorEvents` の toggle（hide 時 true / カード表示時 false）は従来どおり必要なので
JS 経路のまま維持（このゲートは正しく動いていた）。

**D5 の Rust objc 機構（overlay_macos.rs / set_overlay_interactive コマンド / Overlay.tsx の
コマンド集約）は誤診に基づくため全撤去**。unsafe FFI を残さず、修正は builder 1 行に集約。
専用窓（codex ⑤）/ NSPanel は acceptFirstMouse で不足する場合の follow-up（runbook 参照）。
