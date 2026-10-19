# 設計（Claude の作業）

研究者の判断は decisions.md にある。ここには見本の作り方と、確かめの方法・結果を置く。

## 実物へ持ち込む前の確かめ

### 前提: 背景の窓はマウスを受けない

背景の層の試作（`spike/handmark-stage` の `src-tauri/src/handmark_stage_spike.rs` 冒頭）は、窓がマウスを受けない作りになっている（背後のデスクトップのクリックを奪わないため）。そのため、窓の中の WebView がマウスのイベントを受け取る形は取れない。実物では、Rust の側で入力を読み、表現の窓へ渡す形になる。

### 1. カーソルの位置（macOS）: 権限なしで読める（実測）

- 方法: 権限を持たない ad-hoc 署名の .app（`LSUIElement`・`open -n` で起動し、Claude Code の端末の権限を引き継がない）が、`NSEvent.mouseLocation` を 0.1 秒ごとに 12 秒読む。別のプロセスから `CGWarpMouseCursorPosition` でカーソルを 3 か所へ 2 秒ずつ置き、最後に元へ戻した。
- 権限の状態（.app の中で読んだもの）: `AXIsProcessTrusted()=false`、`CGPreflightListenEventAccess()=false`、`CGPreflightPostEventAccess()=false`。
- 結果: 値が置いた位置を追った（陽性対照）。(200, 200) → y=756、(600, 300) → y=656、(400, 500) → y=456。戻した後は元の位置。y は Cocoa の座標（下が 0）で、主画面の高さ 956 から引いた値になっている。
- 環境: macOS 27.0.1（26A434）、MacBook Air。
- 試しのプログラム: `/private/tmp/claude-501/-Users-johnd-GSE-prototype/8e502c18-7e5b-4d0e-a473-1fad576e459e/scratchpad/mouseprobe/src/probe.swift`（作業用。リポジトリには入れない）。
- 分かったこと: カーソルの位置には、イベントを取る仕組み（CGEventTap）も TCC の許可も要らない。描画のたびに一点を読むだけで、列を持たずに済む。

### 2. クリックとホイール（macOS）

- 方法: 1 と同じ形の権限を持たない .app（`probe2.swift`）が 20 秒動く。(a) `NSEvent.pressedMouseButtons` を 50ms ごとに読み、0 から 0 でない値へ変わった回数を数える。(b) 聞くだけの CGEventTap（`leftMouseDown`・`rightMouseDown`・`scrollWheel`）を作り、届いた数を数える。その間に研究者がデスクトップの空いたところを 3 回クリックした（研究者の実地の操作・2026-10-20）。スクロールは行っていない（研究者に確かめた）。
- 権限の状態: `AXIsProcessTrusted()=false`、`CGPreflightListenEventAccess()=false`。
- 結果:
  - (a) 3 回とも数えた（4.05 秒・10.65 秒・18.25 秒）。
  - (b) tap は作れたが、終わりの時点で無効（`tapIsEnabled=false`）。押下 0 件。押下が 3 回あったのに 0 件なので、権限がないと tap には押下が届かないと読める。ホイール 0 件はスクロールをしていないので陰性ではない。ホイールも届かないだろうとは言えるが、実測ではない（未確認）。
- 分かったこと:
  - クリックは、権限なしで、押されているボタンを繰り返し読む方法で取れる。いまの O1 の取り方（ADR-014 D4 の mac 側のマスク）を広げずに済む。
  - ホイールには繰り返し読む方法がない。macOS では tap が要り、押下と同じく権限なしでは届かない見込み（ホイールは未確認）。GSE の本体は打鍵の tap のために許可を持っているが、実物でホイールを使うと、表現の側にもイベントを取る仕組みが入る。
- 限界: 50ms ごとの読みは、50ms より短い押下を取りこぼしうる（トラックパッドのタップでのクリックは短い）。今回の 3 回は取れたが、取りこぼしの率は測っていない。描画の速さ（30〜60 回/秒）で読めば 17〜33ms になる。

### 2b. Windows

- 位置: `GetCursorPos`。クリック: `GetAsyncKeyState(VK_LBUTTON)` などを描画のたびに読む。どちらもフックを使わない。実測はしていない（Mac だけで完結するタスクのため）。
- ホイール: 繰り返し読む方法がない。Raw Input はすでに O1 の `observe_windows.rs` が使っており、Raw Input の受け先は 1 つのプロセスで装置の種類ごとに 1 つの窓なので、表現の側で別に登録すると O1 の受け先を奪う（Microsoft の一次資料の逐語「Only one window per raw input device class may be registered to receive raw input within a process」。`.steering/20260821-workspace-behavior-triage/survey-input-channels.md:342` に引用がある）。O1 の処理から分けて受け取るなら、記録の経路と表現の経路が同じ場所を通ることになり、条件 1 と最もぶつかる。
- まとめ: 位置とクリックは両 OS とも、権限もフックも要らない読み方がある。ホイールは両 OS とも、イベントを取る仕組みを表現の側にも持たせることになる。

### 3. 表現用の値をロガーへ渡さない形（条件 1）

壁紙の層の前例（`src-tauri/src/wallpaper.rs:1013` の `the_wallpaper_layer_cannot_write_records`・R-P9）に倣う。

- 表現の入力を読むコードを、記録の側と別のモジュールに置く（例: `handmark_input.rs` と OS ごとのファイル）。O1 の `input/observe*.rs` と `analysis/pointer_bin.rs` には手を入れない。
- テスト 1（構造）: そのモジュールのソース（テストの部分とコメントを除く）が `LogEntry`・`tracing::`・`log_tx`・`POINTER_TX` を含まない。対照として、記録する側のファイル（`lib.rs`）では見つかることも確かめる（R-P9 と同じ）。
- テスト 2（逆向き）: `logger.rs`・`schema_dto.rs`・`submission.rs` が表現の入力の型の名前を含まない。
- テスト 3（溜めない・条件 2）: そのモジュールは最後の一点だけを持ち、列を持たない（ソースに `Vec<`・`VecDeque` を含まない）。表現の窓の側は、受け取った値を保存しない（`localStorage`・`invoke` で返さない）ことを TS 側のソース検査で固定する。
- 型そのもので止められること: 表現の入力の型に `serde::Serialize` を付けるのは窓へ渡すために要るので、型だけでは記録への流れを止められない。止めるのはモジュールの境界とテストである。
- 陽性対照: テストはそれぞれ、検査する文字列を一時的に足した版で赤になることを確かめる（実行時に文字列を組み立てて、対照の文字列を検査対象のファイルに書かない。gate-green-but-artifact-broken の 4 型目）。

### 4. ADR で明示するか

ADR-014 D4 の「入れないもの」の表は、絶対座標を名指ししている（`docs/adr/ADR-014-continuous-natural-work-collection.md` の表）。D4 は O1 の収集の決まりで、表現の側のことは決めていないが、表現の側のコードが絶対座標を読むのを見た人には、D4 に反するように見える。実物へ持ち込む前に、「表現には使うが記録しない」とその境界（3 のテスト）を ADR で明示する方がよい、というのが Claude の見立て。起票はこのタスクの外（判断 5）。

## 見本

（見比べの結果の後に書く）
