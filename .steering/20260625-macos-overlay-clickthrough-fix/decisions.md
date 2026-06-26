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

## D7. NSPanel への確定（2026-06-26・D6 の acceptFirstMouse / 不透明 card 窓案を上書き・ユーザー承認済み）
実機検証で **acceptFirstMouse も不透明 card 窓も不十分**と判明（HANDOFF §1-2）:
- 透明 overlay 窓は macOS でクリックを webview へ一切配送しない（DIAG: pointer/click=0）。
- 隠れ窓（hide/orderOut）は WKWebView の JS が休眠し Tauri イベント取りこぼし（probe_triggered 不達）。

Web 調査（tauri #11386 open / #6781・#14102 open / Apple WKWebView docs / Pluely・tauri-nspanel・
spotlight-example のソース）で **真因＝非 key/非アクティブ NSWindow がクリックを content view へ
ルーティングしない**ことを確定。`accept_first_mouse` + `focused(false)` 経路はこれら open issue が
「flaky・toggle 経路依存」と明記する不安定経路。**canonical fix = 窓を
`NSWindowStyleMaskNonActivatingPanel`(1<<7) + `canBecomeKeyWindow→YES` の NSPanel 化**
（Spotlight/Raycast クローンの定石。tauri 公式 discussion #9876 が tauri-nspanel を推奨）。

**採用（ユーザー承認 2026-06-26）= 既存 overlay 窓を tauri-nspanel で非アクティブ Panel 化。**
- `to_panel()` で既存 overlay 窓をそのまま変換 → Probe/Nudge/Wall は全て overlay に戻す
  （= WIP の card 窓分割・画面外 JS 起こしハックを **全 revert**）。
- 透明性は維持（macos-private-api 既存）。クリックは panel が webview へ配送、フォーカスは奪わない。
- overlay はセッション中ずっと show 済みのため JS 休眠問題は発生しない。
- **panel level は Floating 固定（昇格禁止）**: tauri-nspanel #104 で高 level が IME をブロック。
  GSE は日本語 IME 合成パイプラインがあるため必須制約。
- 既存の `setIgnoreCursorEvents` トグル / box リサイズ / Wall 全画面ブロックは現状維持で動くはず
  （NSWindow プロパティのため panel 化後も有効）。実機で Wall 非ブロック非回帰を検証。
- リスク: git-only 依存（tauri-nspanel、crates.io 非掲載）/ macOS 26 の wry #1576 WKWebView crash を
  実機検証 / 2.10 の JS/Rust 版整合。

**WIP（f770ae4）の card 窓系は全撤去**: `CardWindow.tsx` 削除、`card` 窓生成（lib.rs）撤去、
`card_dbg` コマンド撤去、start_session の card show 撤去、ProbeCard を overlay へ戻す、DIAG 計器全除去。

### D7 補足（code-reviewer / security-checker 反映・2026-06-26）
- **git 依存は rev 固定**: `tauri-nspanel` を `branch = "v2"` ではなく `rev = "18ffb9a2..."` で pin
  （Cargo.lock の SHA と一致）。`cargo update` で無レビューに HEAD へ滑るのを防ぐ（両レビュー MEDIUM）。
- **accept_first_mouse(true) は NSPanel の保険として併存**: 主の修正は NSPanel 化。Pluely の Tauri 2.x
  レシピも conf で acceptFirstMouse:true を併用しており踏襲。将来 panel 化を外すと無言で
  acceptFirstMouse 依存に戻る点はコメントで明示済み。
- **set_style_mask は絶対代入**: overlay は decorations(false)=borderless(0) 生成のため 1<<7 単独で
  既存ビットを失わない（OR 等価）。ただし panel 化後に JS の setSize/maximize（box⇄全画面）が効くかは
  実機検証項目（runbook D/結果の解釈）。効かない場合の fallback は窓制御を Rust command へ寄せる。
- **collection behavior = CanJoinAllSpaces | FullScreenAuxiliary**: Wall を Space 切替で回避されない
  ためにも妥当。カードは画面外退避で常駐コスト無視可。
- 関数戻り値は `tauri::Result`（このリポジトリは anyhow を依存に持たず `Result<_,String>`/`tauri::Result`
  を使う実態規約。bin/replay.rs に明記。reviewer の anyhow 指摘は docs 旧記述ベースで実態と逆だった）。
  to_panel 失敗は非致命で呼び出し側 setup が tracing::error のみ。
- security: `cargo audit` 未インストールのため transitive（objc/cocoa/block）の自動照合は未実施。
  既知 CVE は把握範囲に無いが、ローカルで一度 `cargo audit` 実行を推奨（follow-up）。

## D8. NSPanel + maximize() クラッシュと撤廃（2026-06-26・実機 dev で確認）
NSPanel 化後の初回実機起動で `start_session` の `overlay.maximize()` が**クラッシュ**:
```
NSRangeException: Cannot remove an observer <WKWindowVisibilityObserver> for the key path
"contentLayoutRect" from <RawNSPanel> because it is not registered as an observer.
  -[NSWindow setStyleMask:] ← tao set_maximized ← start_session maximize()
```
**真因**: `maximize()`/`unmaximize()` は tao 内部で `setStyleMask:` をトグルする。NSPanel 化した窓に
載る WKWebView は `contentLayoutRect` の KVO オブザーバ登録状態が NSPanel と不整合になり、style mask 変更時の
view 付け替えでオブザーバ解除に失敗して例外で落ちる。透明窓のままなら maximize は動いていた=NSPanel 固有。

**対応**: overlay に対する `maximize()`/`unmaximize()` を**全廃**し、全画面化は明示 `setPosition`+`setSize`
（モニタ全域 physical 座標）で行う。setStyleMask を触らない操作（setSize/setPosition/show/hide/
setIgnoreCursorEvents）のみで表示制御を完結させる。
- 撤廃箇所: `lib.rs start_session`（maximize 除去・show のみ）/ `Overlay.tsx applyFullscreenBlock`
  （maximize 除去）/ `Overlay.tsx widgetOnly`（unmaximize 除去）。
- 副次的利点: 明示サイズはタスクバーごと全被覆=Wall の全ブロック意図に合致（maximize は work area 止まり）。
- Windows 非回帰: Windows は NSPanel 化しないが、明示 setSize/setPosition で従来同等の全画面被覆になる
  （maximize は元々フォールバック扱いで、主経路は明示サイズだった）。
- 教訓: **tauri-nspanel 化した窓では maximize/unmaximize/fullscreen トグル禁止**（setStyleMask 経由で
  WKWebView をクラッシュさせる）。サイズは setFrame 系（setSize/setPosition）で制御する。

## D9. クリック透過の真因＝ゲート1（ignoresMouseEvents）を Rust 権威化（2026-06-26・実機で確認）
クラッシュ解消後の実機テストで **カードは表示されるがクリックは依然背後アプリへ素通り**（ユーザー報告）。
macOS のクリック到達には 2 ゲートがある:
- **ゲート1**: `ignoresMouseEvents == NO`（窓が hit-test に参加）。
- **ゲート2**: クリックを content view(WKWebView) へ配送（非アクティブ panel + `accept_first_mouse`）。

D7 でゲート2 は対処したが、**JS の `setIgnoreCursorEvents(false)` が NSPanel 化窓で `ignoresMouseEvents` に
実効していなかった**（ゲート1 が開かず素通り。研究 Agent2 の懸念が的中）。

**対応**: Tauri コマンド `set_overlay_interactive(interactive)` を追加し、macOS は
`RawNSPanel::set_ignore_mouse_events(!interactive)` を **Rust 権威**で直接叩く。非 macOS は従来の
`set_ignore_cursor_events` に委譲（Windows 非回帰）。Overlay.tsx の `setIgnoreCursorEvents` 4 箇所
（mount/全画面/box/hide 失敗時）をすべてこのコマンド経由に置換。
- **key 化はしない**（`make_key_window` を呼ばない）: ゲート2 は `accept_first_mouse(true)` + 非アクティブ
  panel が担うため。前面アプリのタイピングフォーカスを奪わない（GSE はグローバル CGEventTap で打鍵捕捉
  するため、panel に key を渡すと前面アプリの入力先が外れ被験者の作業を阻害する）。
- 実機 smoke 待ち: これで初回クリックが効くか。効かない場合の次手は `make_first_responder(content_view)`
  （key 化せず webview を first responder 化）→ それでも駄目なら `make_key_window`（フォーカス影響を許容）。

## D10. 真因＝idle 時 hide による webview JS 休眠（2026-06-26・診断ログで確定）
D9 の Rust 権威 ignore_mouse_events を入れても素通り継続。**診断ログ**（set_overlay_interactive に
tracing + ignoresMouseEvents 読み戻し）を仕込んで実機計測した結果:
- 起動時に `interactive=false` が 2 回（mount effect）→ `ignoresMouseEvents=true`
- **`debug_force_probe emitted` 後に `interactive=true` が一度も出ない**

= カード表示時の `setOverlayInteractive(true)` に到達していない = 統合 effect から見て `probeActive` が
true になっていない = **`ProbeCard` の `probe_triggered` リスナーが発火していない**。emit は出ているのに
受け取らない理由は **idle 時の `win.hide()` で macOS の NSPanel/webview JS が休眠**しイベントを
取りこぼすため（研究で警告された隠れ窓 JS 休眠が現実化。カードが出たり出なかったりした非決定性の正体）。

**対応**: 統合 effect の idle ブランチで **`hide()` を廃止**。代わりに「画面に出したまま透明 +
クリック透過 (`setOverlayInteractive(false)` = ignoresMouseEvents=YES)」にして JS を生かす。overlay の
中身は idle 時すべて非表示（`.overlay-root`/body とも `background: transparent`・ProbeCard=null・
Nudge=opacity0・Wall 非描画）なので、透明窓として不可視・無害。クリックは背後アプリへ透過する。
- これで probe_triggered リスナーが常時生き、カードが確実に表示され、box 化 + interactive(true) が走る。
- 教訓: **macOS overlay でイベント駆動 UI を載せる窓は hide(orderOut) しない**。透明 + クリック透過で
  出したまま JS を生かす（または Rust を真実源に fetch-on-show）。隠れ窓の JS 休眠は非決定的で厄介。
- 診断ログ（[PANEL] tracing + ignoresMouseEvents 読み戻し）は確認後に除去する。

## D11. ★真の根本原因＝Tauri capability に allow-set-size 不足（2026-06-26・診断ログで確定）
フロント診断（fe_dbg でチェーン各段をログ）で**破断点を特定**:
```
[FE] ProbeCard probe_triggered received      ← イベント到達 OK
[FE] ProbeCard onActiveChange(true)          ← probe state 伝播 OK
[FE] overlay effect: visible=true widgetOnly=true probeActive=true  ← effect 起動 OK
[FE] overlay effect: after show              ← show OK
[FE] overlay effect CATCH: window.set_size not allowed.
     Permissions associated with this command: core:window:allow-set-size   ← ★ここで例外
```
**真因**: `capabilities/default.json` が overlay 窓に `core:window:allow-set-size` /
`allow-set-position` を**与えていなかった**。box 化の順序が `setSize → setPosition →
setOverlayInteractive(true)` のため、`setSize` が permission エラーで例外を投げ、**interactive 化
（ignoresMouseEvents=NO）に到達せず**クリックが素通りしていた。

**これが当初からの本当の根本原因**。カードは `position:fixed` で描画されるので「表示はされるが
クリック不可（背後が反応）」という症状に完全一致。D5〜D10 で追っていた transparent/非 key/JS 休眠は
（gate2/堅牢性としては正しい改善だが）この **gate1 を開く手前の例外**が主因を覆い隠していた。

**対応**: `default.json` に `core:window:allow-set-size` + `core:window:allow-set-position` を追加。
不要になった `allow-maximize`（D8 で禁止）は除去。
- 教訓: **Tauri 2 で JS から `setSize`/`setPosition`/`setIgnoreCursorEvents` 等の窓コマンドを呼ぶ前に
  capabilities の permission を必ず確認**。permission エラーは例外で、await 連鎖の途中で投げると
  以降（クリック透過解除など）が黙って実行されない。症状が遠くに出るので原因特定が難しい。
- nspanel（D7・gate2/非フォーカス）と Rust 権威 ignore_mouse_events（D9）と hide 廃止（D10）は
  堅牢性のため維持。capability 修正（D11）が gate1 の即時ブロッカー解除。

## D12. becomesKeyOnlyIfNeeded でフォーカス非奪取（2026-06-26・D11 実機成功後の仕上げ）
D11 で**クリック解決を実機確認**（Probe/Nudge のボタンでカードが閉じる）。ただし readback で
`isKeyWindow=true`（`win.show()` が `makeKeyAndOrderFront` で panel を key 化していた）。GSE は被験者が
**書き続ける**研究ツールで、カード表示が前面アプリのタイピングフォーカスを奪うと執筆タスク＝データが
壊れる。カードは**マウス操作のみ**（テキスト入力なし）で key 不要。

**対応**: `convert_overlay_to_panel` に `panel.set_becomes_key_only_if_needed(true)` を追加。
テキスト編集等が必要な時だけ key 化する＝カードでは key を取らず前面アプリのフォーカスを維持。
クリックは `accept_first_mouse(true)` + `ignoresMouseEvents=false` で非 key のまま届く。
- 実機確認項目: ボタンが効く（非回帰）＋ カード表示中/後も別アプリでタイピング継続可（isKeyWindow=false）。
- **実機確認済（2026-06-26）**: `interactive=true -> ignoresMouseEvents=false isKeyWindow=false isVisible=true`。
  ボタン押下可（クリック到達）＝**macOS クリック無反応バグは解決**。

## D13. クリック修正で露出した「記録に失敗」＝次タスク（2026-06-26）
クリックが効くようになった結果、`ProbeCard` のボタン押下で `record_realtime_answer`/`record_realtime_skip`
が **失敗し「記録に失敗しました」**を表示（カード保持）。`lib.rs record_realtime_answer` は log channel
への `try_send` 失敗（`map_err(log_send_error)`）で Err。**本タスクの overlay 変更とは無関係**（logger/record
未変更）で、クリック不能のため従来到達できず**隠れていた既存バグ**。別タスク
`.steering/20260626-phase1-card-repro-backend-fix/`（#1 backend log channel）と同根の可能性。
次セッションで `logger.rs` の channel（full/disconnect 切り分け）を調査。引き継ぎ:
`HANDOFF-nspanel-DONE-and-record-failure.md`。
