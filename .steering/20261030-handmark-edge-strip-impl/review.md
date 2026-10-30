# レビュー（code-reviewer・security-checker・2026-10-30・対象 c31b2dfb^..b0ee84ae）

## 直したもの

| 出どころ | 指摘 | 直し |
|---|---|---|
| code-reviewer HIGH 1・security MEDIUM 2 | 隠している途中に終了すると戻らない | 隠す前に STATE に一覧を入れる。隠す前と、メインスレッドで隠す直前に `is_shutting_down()` を見てやめる |
| code-reviewer HIGH 2・security MEDIUM 1 | Cmd+Q の終了は `shutdown()` を通らず、隠したアプリが戻らない | `lib.rs` の `.run(ctx)` を `.build(ctx).run(...)` にし、`RunEvent::Exit` で `restore_on_exit` を呼ぶ（macOS だけ） |
| code-reviewer MEDIUM 3 | 帯を Dock の上に動かした後も、近さを画面の下端から測っていた（Dock の上で濃く薄くなる場所がずれる） | 帯の下端を `handmark_edge_strip::bottom_pt()` に覚え、`strip_near(cursor_on, y, bottom)` で帯からの距離で測る。帯より下（Dock の上）も距離で薄れる。テストを足した |
| code-reviewer MEDIUM 4 | 「背景を閉じる」で風が止まっても帯が最後の風で描き続ける | 背景の `close()` から帯の `close()` も呼ぶ |
| code-reviewer MEDIUM 5 | 窓の一覧の読みを 250ms ごとにメインスレッドで回していた | 帯の見張りのスレッドで読み、結果の真偽だけをメインスレッドへ渡す。画面の大きさは `CGDisplay::main().bounds()` |
| code-reviewer MEDIUM 7 | 見張りのスレッドが重なりうる | 世代の番号を足し、古い見張りは抜ける |
| code-reviewer LOW 9 | 終了間際にメインスレッドが回らないと黙って戻せない | 警告を出す |
| security LOW 3 | トレイのコメントの「記録しない」が実態（applog に 1 行ずつ残る）と合わない | コメントを実態に直した |
| security LOW 4 | 名前を読まないことが検査で守られていない | `handmark_stage_guard.rs` に、帯とどける操作と風のファイルが名前を読む API を含まない検査と、風のファイルが書き出さない検査を、陽性対照つきで足した。`localizedName` を足すと赤になることを確かめた |

## 直さなかったもの（試作の段の限り）

- code-reviewer MEDIUM 6: 全画面の誤判定（Dock を自動で隠す設定で手で最大化した窓・画面いっぱいのボーダーレスの窓）。判断 6 の限りのまま。移動のログは動いたときだけ出る。
- code-reviewer LOW 8: `NSApplication::activate()` は macOS 14 以降だけ。本線に移すときに分岐する。
- code-reviewer LOW 10・11: 風が 0 のままでも送る・listen の失敗を黙って捨てる（既存の背景と同じ書き方）。
- security LOW 5: 帯の窓の capability を listen と unlisten だけに絞る余地。背景と同じ `core:default` のまま。
- security LOW 6: pid の再利用で別のアプリを戻しうる（見込みは低い）。
- security LOW 7: 近さの数から縦の位置が約 8 点の刻みで分かる（判断 2 の範囲どおり）。

## 実機の確かめ（直しの後・run10・2026-10-30 15:09〜15:14 JST）

- 帯は起動直後に `bottom_lift_pt=48.0`（Dock の上）。
- (b) 研究者の目視:「薄くなります」（帯を Dock の上に置いたまま、カーソルを寄せると薄くなる）。
- (a) 15:13:37 に前面に出られ（85ms）`hidden=14`・`not_hidden=0`。15:13:39 に研究者が Cmd+Q を押し、`handmark reveal: restored on exit` が出て開発版が終わった。研究者の目視:「cmd + Q で戻りました」。終了後に見えているアプリは 14（System Events の visible）。
- 開発版の後片付け: 残りのプロセスなし・ポート 1420 は空き・一時フォルダを消した。O1 の収集アプリ（pid 99037）は動いたまま。
