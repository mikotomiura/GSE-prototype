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

## 判断 12: 直した版の画面の確かめ（2026-11-12 15:28〜15:32 JST・研究者と）

- 段取り: 判断 10 と同じ表（SHA-256 8060e816…）・新しい一時の HOME で、判断 11 の直しを入れた開発版（bb599f29）を起動した。gse-next は止まっていた。
- 見たこと（研究者の目）: 帯と背景が出ていて、打鍵で線が揺れる。
- ロックしていない状態で `visible_ms` = `shown_ms`（93,495／93,495・その後 108,198／108,198）。実機のセッションの読みで `strip_seen` が真になる（`on_console` の読みが効いている）。
- 開け閉めの繰り返し: 研究者がトレイの「やめる」「描く」を 5 往復（2 秒おき）。`toggles` に 10 件・`stage_starts` に 5 件（起動の 1 件と合わせて 6 件・最後の 1 件は次の書き出しで入った）。スレッドの本数は押す前 38・押した後 38（見張りのスレッドが増えない）。
- applog: 帯と手跡の警告は無し。`keyboard hook may be dead ... starved_ms=30102` の ERROR が 1 行あった（起動から約 100 秒）。起動直後の既知の偽陽性（memory: claude-code-caffeinate-blocks-sleep-tests の「起動 65 秒後に starved_ms=30074」）と同じ型で、PR 2 の変更の外。
- 終わった後、開発版を止めた。

## 判断 13: 完了時のレビュー（code-reviewer・security-checker）と、ロックの量が 5 分の行から読めること（2026-11-12）

- security-checker: CRITICAL・HIGH なし。MEDIUM 1・LOW 2。code-reviewer: CRITICAL・HIGH なし。MEDIUM 1・LOW 5。
- **security-checker M1（研究者が選んだ・AskUserQuestion・推奨どおり）**: 判断 11 の後、`shown_ms − visible_ms` の大半は画面のロック・ユーザーの切り替え・主画面のスリープの時間になり、5 分の行どうしの差から 5 分ごとのその量が、削除した区間の前後の行の差から区間の中の量が読める。受け入れて、schema の説明に書き、gse-dataset もそろえる。
  - 理由: 入力が無かった時間は、既存の `key` の行（時刻つき）・毎秒の `feat`・ポインタの 1 秒ビンが秒の単位ですでに示しており、新しく分かるのは「ロックしていた」という区別だけ。削除区間の中の量は `shown_ms` が既に同じ性質を持つ（判断 8）。
  - 採らなかった案: ロックの判定を描画の停止だけに使い、足す量から外す（`visible_ms` がほぼ `shown_ms` に戻る）／日の終わりの行だけに載せる（落ちた日に欠ける）。
- 裏取り: 指摘の筋書きをコードで確かめ、どれも事実だった（`kick` は予約を 0ms に置き直す・近さは値が変わるたびに 16ms の刻みで届きうる／`open` は `STRIP_VISIBLE` を偽に戻していなかった／`read_session` が None でも何も残らない）。
- 直したもの:
  - code-reviewer M（描画の回数）: `kickDelayMs`（純関数）で、最後に描いてから `ACTIVE_FRAME_MS` は空け、今の予約が十分早ければ動かさない。node で縛った（16ms ごとに近さが届いても 1 秒の描画が 31 回以下）。変異（常に 0 を返す）で 3 件赤。
  - code-reviewer L（古い見えているの持ち越し）: `open` の成功の経路で `STRIP_VISIBLE` を偽にしてから世代を進める。
  - code-reviewer L（読めないことが残らない）: `read_session` が None のとき、別の印で 1 回だけ警告を残す。`warn_once` は印を引数に取る形にし、tracing の出口は 1 か所のまま。
  - code-reviewer L（検査の壊れやすさ）: 見張りの検査を `probe_loop` の本体に限り、`STRIP_VISIBLE.store(visible, …)` と `emit_to(…, visible)` を求める形にした。
  - security-checker L1: `read_session` が読む鍵は 2 つだけ・辞書を回さない・Debug で出さない・tracing しないことを本文検査で縛った（陽性対照の語は実行時に組み立てる）。security-checker L2: 2 つ目の `unsafe` に SAFETY の注記。
  - security-checker M1: schema の `handmark_day` の説明に、5 分の行と削除区間の前後の行の差から読める量を書いた（判断 8 の「文書に書く」もここで満たす）。gse-dataset の同期の枝に写して parity が通る。
  - 変異: 鍵を 1 つ足す・送りに `occlusion_visible` を使う・印に `occlusion_visible` を使う → 3 回とも赤。fmt・clippy・`cargo test --workspace`（lib 1309 件）・emit_schema・`tsc --noEmit`・`npm run test:handmark`（36 件）が緑。
- 直さず残すもの:
  - code-reviewer L（閉じたら tsx の `visible` を真に戻す）: 偽にすると、窓の listen より先に見張りの最初の読みが届いたとき、見えているのに描かないままになる。開き直しから最初の読みまで（250ms 程度）ロック中でも描くのは害が小さい。意図をコメントに書いた。
  - code-reviewer L（`DayRecord` の `deny_unknown_fields` と `STATE_VERSION` 1 のまま）: 前の版へ戻すと、新しい状態ファイルは壊れた扱い（fail-closed）になり、手跡は閉じたままになる。手跡のコミットはまだどのタグにも入っていないので、影響は開発版の行き来だけ。配る前にこの性質を覚えておく。

## 判断 14: /cross-review（Codex を加える）と直し（2026-11-12）

- Codex: 本線のチェックアウトから wrapper を 2 回（`handmark_edge_strip.rs`・`handmark_guard.rs` ／ 残りの 13 ファイル）。2 回とも exit 0・secrets-filter のブロックなし。2 回で計約 8.2 万トークン（今日の累計 154,086・上限 2,400,000）。wrapper の指示文は固定なので、既知の未決は添えられず、私の側で振り分けた。手動承認の閾値（2,000 行）を超えるので、研究者に確かめてから送った（AskUserQuestion・2 回に分けて送る）。
- Claude 側: 全体は判断 13 の code-reviewer、直しのコミット bd04b04b は別の code-reviewer が見た（HIGH・MEDIUM なし・LOW 4）。
- **両者一致**（code-reviewer の判断 13 の LOW と Codex の 1 回目の 1）: 見張りが「閉じていない・世代が同じ」を確かめてから書くまでの間に閉じて開き直されると、古い「見えている」が新しい開きへ書かれる。判断 13 の直し（`open` で偽に戻す）だけでは「確かめ → 閉じる → 開く → 古い真を書く」の順が残っていた。**直した**: 世代と見えているかを 1 つの `AtomicU64`（`STRIP_SEEN`・`pack_seen`）に詰め、見張りは `set_seen_for`（世代が同じときだけ CAS で書く）で書く。`open` は世代を進めて見えているを偽にする。`OPEN_GEN` と `STRIP_VISIBLE` は無くした。純関数 `write_if_gen`・`next_open` をテストで縛った（変異: 世代を見ずに書く → 赤）。
- **Codex のみ・採用**:
  - 読めなかった刻み（メインスレッドへ投げられない・返事が来ない）で前の「見えている」が残る → 見えていない側に倒す（`set_seen_for(gen, false)`・窓への送りは変えない）。本文検査で縛った（変異: タイムアウトで倒さない → 赤）。
  - CSP の検査がスキームを省いたホスト名（`connect-src example.invalid`）を通す → 許す source expression の一覧（`'self'`・`data:`・`'none'`）に改め、陽性対照を足した（変異: `img-src` にスキームなしのホストを足す → 赤）。今の CSP に穴は無い。
- **Codex のみ・誤検知**: 2 回目の 1（`handmark_edge_strip.rs` が差分に無い）は、1 回目に送ったため。
- **Codex のみ・直さず残す**:
  - 1 回目の 4（全画面の判定が幅と下端だけ）: 幅いっぱいで下端まで伸ばした普通の窓があると、帯を画面の下端へ移して Dock の後ろに隠れうる。試作からの判定で、Dock に隠れる分は判断 11 の限界と同じ扱い。実機で起きたら見直す。
  - 2 回目の 2（近さ・見えているかの最初の送りを窓が受け取る前に送ると取りこぼす）: 見えているかは、窓の側が閉じたら真に戻すので描画が止まったままにはならない（判断 13）。近さは、カーソルが動けば次の値が届く。
  - 2 回目の 3（`visible_ms` を持たない古い状態ファイルを 0 で読む）: 手跡のコミットはまだどのタグにも入っていない。同じ日に古い版から上げた日だけ、その日の `visible_ms` が少なく出る（研究者本人の開発版の行き来に限られる）。
  - 2 回目の 4（削除区間の前後の行の差から量が読める）: 判断 13 で研究者が受け入れ、schema の説明に書いた。
- 直しのコミットのレビューの LOW: JSDoc の付け先を `nextFrameMs` へ戻した／`read_session` の検査で辞書に触れる箇所を `dict.` の数で縛り、`GetValue` を禁止語に足し、陽性対照で鍵の一覧が変わることを確かめた／design.md の警告の文言を新しい形（`handmark: edge strip: unavailable: …`）に合わせた／`strip_seen` の本体の検査は足さない（純関数のテストが 4 方向を縛る）。
- 確かめ: fmt・clippy・`cargo test --workspace`（lib 1310 件）・emit_schema・`tsc --noEmit`・`npm run test:handmark`（36 件）が緑。
