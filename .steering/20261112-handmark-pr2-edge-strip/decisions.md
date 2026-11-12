# 重要な設計判断

## 判断 1〜3: 始める前に研究者が選んだこと（2026-11-12・AskUserQuestion・3 問とも推奨どおり）

1. **帯の描画の元**: 帯は背景と同じ Rust の状態（`StageState`・250ms の固定の刻み・ADR-051 D5）を受けて描く。30／10 回の切り替えは、窓の側で状態から決める（状態は描画の回数に影響しない）。打鍵ごとのイベントは窓へ送らない。
   - 理由: PR 1 の判断 9・PR 3 の判断 1〜4（跡は Rust）とそろい、PR 4 の描き直しが背景と同じ関数で帯も作れる。
   - 採らなかった案: 試作のまま窓の側（打鍵ごとのイベントを帯へ送り、帯の中で動かす）。
2. **帯が映すポインタ**: 打鍵（風）を描き、カーソルが帯に近づくと薄くする（試作どおり）。近さは Rust のポインタのスレッドで 0〜1 の数 1 つにし、帯の窓へだけ送る。トレイで「カーソル」を切った日は薄くしない。
   - 限界: PR 4 の再生では位置が無いので、薄くなる分は再現できない（ADR-051 D3 の限界に足す）。
   - 採らなかった案: 打鍵だけ（カーソルの下で線が見えにくい）／跡の場も帯に映す（14pt で見分けられるか分からず、payload が帯にも行く）。
3. **見えていた時間**: 出ている間、帯の窓の `occlusionState` が見えている時間を足して `handmark_day.visible_ms` に書く。背景の窓は透明な部分が多く、覆われていても見えている扱いになりうるので数えない（文書に書く）。
   - 採らなかった案: 帯か背景のどちらか（ほぼ `shown_ms` と同じになりうる）／`null` のまま。

## 判断 4: ディスクの空きを戻す（2026-11-12・研究者・AskUserQuestion）

- 始めた時点で空きが 2.3 GiB（自前ランナーの下限 8 GiB を割る）。GSE の worktree の `target` はすでに掃除済みだった。
- 研究者が「Caches を私が消す」を選び、一覧（Google/Chrome の HTTP のキャッシュ 5.2G・VSCode の更新の残り 1.6G・Homebrew・notion-updater・node-gyp・pip）の全部を消すことを承認した。消した後の空きは 10 GiB。gse-next・Codex・claude-cli のキャッシュは残した。
- 開発版のビルドで再び 8 GiB を割るので、push の前にこの worktree の `target` を消す。

## 判断 5: 設計を承認・/reimagine は使わない（2026-11-12・研究者・AskUserQuestion・推奨どおり）

- design.md の案（帯は背景と同じ状態を受ける 2 枚目の窓・帯が作れなくても背景は閉じない・近さは帯へだけ・`visible_ms` は状態ファイルの日の累計で `shown_ms` と同じ条件かつ帯が見えている刻みだけ）を承認した。
- /reimagine は使わない（requirement.md の運用メモ）。

## 判断 6: 実装 A の実装役の報告を確かめる（2026-11-12）

- コミット 529e76b1（`visible_ms`）・49713109（近さ）。fmt・clippy（`-D warnings`）・`cargo test --workspace`（lib 1289 件）・emit_schema の byte-equal を自分で走らせ直して緑。
- コードで確かめたこと: `add_visible` は `add_shown` と同じ `if` の中だけ／窓を開く・閉じるときに `strip_visible` を偽に戻す／近さの `y_pt = (1 − p.y) × 主画面の高さ` は `to_point`（y は下向き）の逆で、左下が原点の点に戻る／近さは `TraceField` に触れない。
- 変異: 実装役の 2 つ（帯が見えないときも足す → 2 件赤／近さで場に触れる → 1 件赤）に加え、私が 1 つ（カーソルを切っても近さを 0 に戻さない → `near_is_sent_only_when_it_changes_and_zero_once_when_cut` が赤）。戻した後の作業ツリーは空。
- 実装役が決めた細部はそのまま採る: `tick` を包みにした `tick_with_strip`・`StripSpot`（帯の下端と主画面の高さ）・一点が読めない刻みは近さ 0。
- 行の `visible_ms` は、記録があれば出していない日（`assigned_off` など）でも `Some(0)` になる（既存テストの期待を `None` から `Some(0)` に変えた）。`shown_ms` が同じ日に 0 を出すのと同じ読みで、`null` は「記録が無い（計っていない）」に限る。design 4 節のとおりなので採る。
- 空き: ビルドで 7.6 GiB（下限 8 GiB を割った）。push の前に `target` を消す（判断 4）。

## 判断 7: 実装 B の実装役の報告を確かめる（2026-11-12）

- コミット 5ec58aca（描画）・5fb7ab89（窓の層と配線）・a1b64b39（検査）。fmt・clippy・`cargo test --workspace`（lib 1300 件）・emit_schema・`tsc --noEmit`・`npm run test:handmark`（28 件）を自分で走らせ直して緑（tsc と node は、メインの `node_modules` を一時的にリンクして走らせ、すぐ消した）。
- コードで確かめたこと: `lib.rs` の帯の呼び出し 8 か所はすべて `cfg(target_os = "macos")` の下／帯の失敗で背景を閉じない／帯の窓は `phase`・`drift` を積まず届いた状態へ寄せるだけ／`nextFrameMs` は閉じた・見えていない → 止める、風か薄れの途中 → 33ms、他 → 100ms。
- 直したもの（私・本コミット）: `open` はメインスレッドで後から `SHOWN` を真にするので、開いた直後に `close` が来ると、隠れた帯で `SHOWN` が真のまま残り、見張りが回り続ける筋書きがあった。隠す処理の中でも `SHOWN`・`STRIP_VISIBLE` を偽にした。AppHandle を要るのでテストは無い（画面の確かめで、開け閉めを繰り返して見張りのスレッドが増えないかを見る）。
- 実装役が決めた細部はそのまま採る: 純粋な部分のファイル名 `handmarkStripFrame.ts`（大文字小文字だけ違う名前で tsc が落ちるため）・近さと状態の送りを `handmark_edge_strip.rs` に置く・検査の一覧 `STRIP_WINDOW` を背景の `WINDOW` と分ける・開くたびに見えているかの最初の読みを必ず送る。
- 帯に `set_content_protected`（画面共有に写さない）は付けていない（試作にも無い・設計のタスクの判断 5 で「選ばなかったもの」）。
- 確かめていないこと（画面で見る）: NSPanel の振る舞い・覆ったときの `occlusionState`・描画の停止と CPU・`background_throttling` の効き・見張りのスレッドの数・薄くなる見た目・`visible_ms` の値・`setFrame` の後の webview の幅・起動直後の `State` の順序。Windows のビルドは CI で見る。

## 判断 8: 区切りの点検（code-reviewer・security-checker）の指摘と、`visible_ms` の 5 分の行（2026-11-12）

- security-checker: CRITICAL・HIGH なし。MEDIUM 2・LOW 4。code-reviewer: HIGH なし。MEDIUM 2・LOW 4。筋書きをコードで確かめ、どれも事実だった（tauri 2.10.2 の `match_any_or_filter` は宛先を指定しない JS の listener を `emit_to` の宛先に関わらず通す・`ROW_MS` は 300,000）。
- **`visible_ms` の 5 分の行（研究者が選んだ・AskUserQuestion・推奨どおり）**: `shown_ms` と同じに扱う。5 分の行に日の累計を載せたままにする。隣り合う行の差から 5 分ごとに帯が見えていた量（全画面のアプリや下まで広げた窓を使っていた時間帯）が読めることと、削除した区間の前後の行の差から区間の中の量が読めることを、文書に書く。
  - 理由: 落ちたときもその日の量が残る（ADR-051 D4 の「一定の間隔で書き直す」）。中身やアプリ名は含まない。`shown_ms` は同じ性質を PR 1 で受け入れている。
  - 採らなかった案: 日の最後の行だけに載せる（終了の行が無い日に欠ける）／5 分の行では粗く丸める（読み方が複雑になる）。
- 直すもの（実装役へ）: code-reviewer M1（帯の寄せの起点が最後に描いた値で、描いた回数・覆われていた後に見た目が変わる → 今の時刻の寄せた値から寄せ、状態の遷移を純関数にして node で縛る）・M2（見張りの抜け際と開き直しの順序 → `SeqCst` か 1 つのロック）・L1（閉じる要求・出せなかったときも印を偽に）・L2（読みと書きの間の閉じ → 世代で捨てる）・L3（濃さの寄せを閉じた式に）・L4（`is_valid` に `visible_ms ≤ shown_ms`）。security-checker M2（帯の送りの検査の穴: `emit_to` の第 1 引数・`emit_filter`・`EventTarget`・`Emitter::emit`・TS の接頭辞）・L1（帯の層の `tracing` は `warn_once` の 1 か所だけ）・L2（`lib.rs` の `emit_near` は 1 回だけ）・L3（CSP に外の宛先が無いことの検査）。
- 直さず残すもの: security-checker L4（窓ごとにアプリのコマンドを絞っていない・既存の性質・他の副窓と同じ）。背景の窓の寄せも M1 と同じ型（毎フレーム描くので影響は小さい見込み・PR 2 の範囲外。引き継ぎに書く）。

## 判断 9: 区切りの直しの実装役の報告を確かめる（2026-11-12）

- コミット 1369279e（寄せの起点・濃さの閉じた式）・c626b24c（SeqCst・`hide_and_clear`）・3692b86c（`visible_ms ≤ shown_ms` を `is_valid` に）・856f8d03（検査の強化）。fmt・clippy・`cargo test --workspace`（lib 1306 件）・emit_schema・`tsc --noEmit`・`npm run test:handmark`（32 件）を自分で走らせ直して緑。
- コードで確かめたこと: `receiveStrip` は開いていない・種が替わったときだけ寄せずに置き、それ以外は `shownAt(st, now)`（今の時刻の寄せた値）から寄せる。
- 変異: 実装役の 4 つ（寄せの起点を最後に描いた値に戻す → node 2 件赤／`is_valid` の条件を外す → 赤／`emit_to` の宛先を別の窓に → 赤／帯の層に `tracing::debug!` → 赤）に加え、私が 1 つ（`tauri.conf.json` の `img-src` に `https://example.com` を足す → `the_csp_names_no_external_destination` が赤）。戻した後の作業ツリーは空。
- 状態ファイルで `visible_ms > shown_ms` のときは壊れた扱い（`DayLoad::Broken` → 記録なし → 窓は閉じたまま・fail-closed）になる。既存の壊れた状態ファイルの経路と同じ。
- 実装役が決めた細部はそのまま採る。L2 の世代の確かめは `SHOWN` を見てから `emit_to` までの短い隙間を塞がないが、次の周回で最初の読みを送り直して戻る。
- 確かめていないこと（画面で見る）: 見張りの本数・開け閉めの繰り返し・覆った後の戻り・薄くなる動き。

## 判断 10: 画面の確かめ（2026-11-12 13:51〜14:08 JST・研究者と）

> 前のセッション（3cd56812）で行い、記録する前にセッションが落ちた（画面のロックで VSCode のセッションを作り直すことになった）。次のセッションが、そのセッションの会話の記録・状態ファイル・NDJSON・applog から書き起こした。

- 段取り: gse-next は止まっていた。一時の HOME（前のセッションの scratchpad の hm2-home）で開発版を `GSE_DEBUG=1 GSE_O1_MODE=1 GSE_S1_MODE=1 GSE_HANDMARK_TABLE=<表>` で起動した。表は `--seed 20261112 --s1-start-day 20768 --early-min 1 --early-max 1 --late-days 6`（SHA-256 8060e816…・今日 20769 が後期の初日で出す日）。
- 見たこと（研究者の目）: ① 帯が Dock の上端に沿う ② 全画面のアプリの上で画面の下端に出る ③ 打鍵で線が揺れる ④ カーソルを近づけると薄くなる、の 4 項目とも可。
- CPU（`ps` の累積の秒の差・1 コア = 100%・本体＋WebKit の子 7 つ）:
  - 帯が出ていて見えている 30 秒: 計 15.4%（本体 4.7・GPU 5.5・WebContent 1.1／0.5／2.1／1.4・Networking 0.0）。
  - 画面のロック中（1 回目・14:00:55〜14:01:55・帯は出ている）: 計 18.9%（本体 5.3・GPU 7.3）。下がらなかった。
  - 2 回目（14:06:34〜14:07:35）: 計 13.7%。この間の 14:07:20 に「やめる」が押されているので、ロックの値としては読めない。
- `visible_ms`: 5 分の行は 13:56:31 に 299,574／299,574、14:01:31 に 599,689／599,689（1 回目のロックの 1 分を含む区間で `visible_ms` = `shown_ms`）。終わりの状態ファイルは `shown_ms` 704,551・`visible_ms` 703,279（差 1.3 秒）。**画面のロックは、帯が見えていない扱いにならなかった**（`occlusionState` が変わらなかった見込み・未確認）。描画も止まらなかった（CPU が下がらない）。
- トレイの入れ切り: `toggles` に 4 回（14:02:12 切る・14:06:16 入れる・14:07:20 切る・14:08:03 入れる）。切っていた間は `shown_ms` に入っていない。applog に WARN・ERROR・panic なし（起動時の O1・段 1・プローブの既定の WARN だけ）。
- 確かめていないこと: 窓で帯を覆ったとき（ロックではなく）の `occlusionState` と描画の停止・見張りのスレッドの本数・開け閉めの繰り返し。
- ⚠️ 段取りの誤り: 「見えない状態」を作るのに画面のロックを研究者に頼み、VSCode のセッションごと作り直すことになった。以後、画面のロックは頼まない。

## 判断 11: 見えているかに、画面のロックと主画面のスリープを足す（2026-11-12・研究者・AskUserQuestion・推奨どおり）

- 根拠: 帯は浮く層の窓で、`occlusionState` が見えていないになったことは試作から一度も無い（試作の results.md: Dock に隠れても・全画面でも true）。判断 10 で画面のロック中も見えている扱いで、CPU も下がらなかった。このままでは `visible_ms` ≈ `shown_ms` で、覆われたら止めるも効かない。
- 決めたこと: 見えている = `occlusionState` が Visible かつ画面がロックされていない（`CGSessionCopyCurrentDictionary` の `CGSSessionScreenIsLocked` が真でない）かつ主画面が眠っていない（`CGDisplayIsAsleep` が偽）。見張りのスレッドで 250ms ごとに読む。
- 限界（文書に書く）: ロックの鍵は Apple の公開ヘッダに名前が無い（広く使われているが文書が薄い）。ロックしないスクリーンセーバーと、Dock に隠れた分は拾えない。
- 確かめ方: 純関数のテストと変異。ロック中の実機の確かめは、Claude のセッションを走らせていない時間に研究者だけで行う（判断 10 の誤り）。ロックしていない状態で鍵が無く `CGDisplayIsAsleep` = 0 であることは確かめた（swift の小さな読み）。
- 採らなかった案: 今のまま意味を限って書く（ロック中も描き続け、`visible_ms` が `shown_ms` とほぼ同じ）／`visible_ms` をやめる。
- 実装（判断 11 の続き）: `strip_seen`（純関数）と `SessionView`、`read_session`（`CGSessionCopyCurrentDictionary` の `#[link]` 宣言・create の規則で包む・読むのは 2 つの鍵だけ）を `handmark_edge_strip.rs` に足し、見張りの読みを通した。ユーザーの切り替え（`kCGSSessionOnConsoleKey` が偽）も同じ辞書から読めるので見えていない側に足した。セッションが読めないときも見えていない側。fmt・clippy・`cargo test --workspace`（lib 1308 件）・emit_schema の byte-equal が緑。変異: 3 つの条件をそれぞれ外す → 3 回とも赤／見張りで `strip_seen` を通さない → 本文検査 `the_strip_probe_judges_visibility_through_strip_seen` が赤。schema の `visible_ms` の説明の文を改めた（gse-dataset の同期が要る）。
