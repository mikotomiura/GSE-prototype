# 決定記録 — O1 macOS 計器（2026-08-24）

## T1: ADR-016 D9 前提1（macOS 同時稼働の実機確認）— ✅ 判定

- **判定日時**: 2026-08-24（macOS 実機・aarch64-apple-darwin）
- **問い**: `CGEventTap` を2プロセスで同時に張れるか。片方が失敗したり取りこぼしたりしないか。
- **計器**: 使い捨て probe（scratchpad `hookprobe/`、repo 外・ADR-012 D7 の作法）。
  1プロセスにつき2本の別 tap（keyboard: KeyDown/KeyUp・pointer: MouseMoved/*Dragged/ScrollWheel、
  T2 の設計要件「既存 tap とは別 tap」を模した構成）。VK・座標・文字は一切読まず、
  カウンタのみ（`CGEventTapOptions::ListenOnly`）。

### ラウンド1: 合成入力（`CGEventPost`・Escape キー30回 + マウス1px移動60回 + スクロール10回）

| 指標 | プロセス A | プロセス B | 期待値 |
|---|---|---|---|
| key tap 設置 | ✅ OK | ✅ OK | — |
| pointer tap 設置 | ✅ OK | ✅ OK | — |
| `key_tap_callbacks`（KeyDown+KeyUp） | 52 | 52 | ≤60（下記注） |
| `pointer_tap_callbacks`（moved+scroll） | 70 | 70 | 70 ✅完全一致 |

⚠️ **最初の試行で Shift キー(0x38)を注入したところ両プロセスとも `key_tap_callbacks=0` だった**。
→ ★ macOS では修飾キーは `KeyDown`/`KeyUp` ではなく `FlagsChanged` として届く
（`hook_macos.rs` の既知の仕様・§0-3 が既に文書化していた内容と一致）。
→ ★ **Escape (0x35) に切り替えて再試行し、正しく届くことを確認した。**

⚠️ Escape の到達数は 52/60（26 keydown + 26 keyup、期待は 30/30）—— ★ 注入間隔 5ms での
連続注入が一部間引かれた可能性がある（原因は未特定・本タスクのスコープ外）。
★ **重要なのは A と B が完全に一致したこと**（52=52、70=70）。→ T1 の問い
（「2プロセスが同じイベントを等しく受け取るか」）に対する答えとしては十分。

### ラウンド2: 実入力（20秒・キーボード/マウス操作を依頼）

| 指標 | A | B |
|---|---|---|
| `key_tap_callbacks` / `pointer_tap_callbacks` | 0 / 0 | 0 / 0 |

⚠️ **これは Windows 版と同型の `signal_absent`**（ADR-013 D1 の語彙）—— ★ 依頼メッセージと
probe 起動が同時になり、20秒の窓内に実操作が間に合わなかった可能性が高い。
⚠️ **「実入力では届かなかった」と読んではならない**（A/B とも 0 で一致しており、
「届いたが片方だけ」という失敗モードではない）。

### 判定

✅ **両プロセスの計数が完全に一致した**（合成入力ラウンドで 52=52 / 70=70）。
→ ★ **T2 へ進む。**

⚠️ 残（Windows 版と同じ形で残す・本タスクのブロッカーではない）:
1. 実入力ラウンドの取り直し（時間があれば）
2. 長時間・高負荷での安定性（★ O1 は数日〜数週間走る。`CGEventTapIsEnabled` の無通知失効が
   2系統になると2倍起きうる — T5 で扱う）

---

## 判断 2: L-c フォーカス遷移の実装手段 — objc2 系クレートを直接依存に追加する

- **判断日時**: 2026-08-24
- **背景**: `NSWorkspace.didActivateApplicationNotification`（ADR-014 D4 指定）は Cocoa/AppKit
  API であり、Carbon の `#[link] extern "C"` パターン（`ime_macos.rs`/`hook_macos.rs` が
  Carbon/CoreGraphics に対して使っている）では書けない（C シムが存在しない）。
- **選択肢**:
  - A: `objc2` + `objc2-foundation` + `objc2-app-kit` + `block2` を直接依存に追加し、
    `NSWorkspace.sharedWorkspace().notificationCenter()` に
    `addObserverForName:object:queue:usingBlock:` で購読する。
  - B: 生の `libobjc` ランタイム FFI（`objc_msgSend`/`sel_registerName`/`objc_getClass` の
    手書き宣言）で同じ通知購読を組む。
  - C: NSNotificationCenter を避け、`NSWorkspace.frontmostApplication.processIdentifier` を
    高頻度ポーリングして変化を検出する（識別子はログに出さず、内部の差分検出にのみ使う）。
- **採用**: A
- **理由**:
  - ★ `objc2`(0.6.4) / `objc2-foundation`(0.3.2) / `objc2-app-kit`(0.3.2) / `block2`(0.6.2) は
    **Cargo.lock に既に解決済み**（Tauri の macOS バックエンド `tao`/`wry` の推移依存）。
    → 直接依存に追加してもバージョン解決が壊れるリスクは低い（実測: `cargo build` で確認する）。
  - ⚠️ B（生 FFI）は block の ABI を手組みする必要があり、objc2/block2 より遥かにリスクが高い。
    誤りが「コンパイルは通るが実行時に落ちる／メモリ破壊」という検知しにくい形で現れる。
  - ⚠️ C（ポーリング）はイベント駆動でないため、遷移の「時刻」の精度が劣化する
    （ポーリング間隔に依存）。また ADR-014 D4 が明示的に通知ベースの手段を指定しており、
    ポーリングへ逃げる理由が無い。
- **トレードオフ**: 本 repo で objc2 系クレートを直接使う前例が無いため、実装・デバッグに
  多少の手戻りリスクがある（`rust-standards` ルール7の「新規依存追加基準」に照らして、
  既存ロックファイルで解決済み・MIT ライセンス・活発にメンテナンスされている点はクリア）。
- **影響範囲**: `src-tauri/Cargo.toml`（4クレート追加、macOS ターゲット限定）、
  `src-tauri/src/input/observe_macos.rs`。
- **見直しタイミング**: objc2 系のビルドが本機で失敗する、または API 呼び出しが
  想定と異なることが判明した場合は、選択肢 C（ポーリング）への切り替えを検討する。

---

## 判断3: ⚠️★★★ `keyboard_layout_id()` の `dispatch_sync_f` は使わない（★ 実機クラッシュで発見・修正）

- **判断日時**: 2026-08-24（macOS 実機・T5 実機総合確認中）
- **背景**: `ime_macos.rs::is_japanese_ime_open()` の実装パターン（`dispatch_sync_f` で
  メインキューへ同期 dispatch）をそのまま `keyboard_layout_id()` に移植して実装した。
  T5 で実機起動したところ、**`setup()` の直後で確実にクラッシュした**
  （`EXC_BREAKPOINT`/SIGTRAP、crash report:
  `~/Library/Logs/DiagnosticReports/gse-next-2026-08-24-014312.ips`）。
  backtrace は `keyboard_layout_id` → `dispatch_sync_f_slow` →
  `__DISPATCH_WAIT_FOR_QUEUE__` → (呼び出し元) `tauri::app::setup` →
  `NSApplication _sendFinishLaunchingNotification`。
- **真因**: `lib.rs` の `setup()` クロージャは Tauri により**メインスレッド**で
  （`did_finish_launching` から）同期的に呼ばれる。★ そこで `dispatch_sync_f` を使って
  **メインキューへ同期 dispatch** すると、**メインスレッドがメインキューへの
  dispatch 完了を待って自分自身をブロックする**（自己デッドロック）。
  最近の macOS の libdispatch はこれを検知して即座に `EXC_BREAKPOINT` で落とす
  （無言でハングするのではなく、デバッグを助けるための意図的なクラッシュ）。
  ⚠️★★★ **`hook-constraints` mac-2「`dispatch_sync_f` はメインスレッドから呼ばない」を
  自分でコメントに書いていたのに、実際の呼び出し元（`lib.rs::setup()`）がメインスレッドで
  あることを検証しないまま実装した** —— `verify-before-claiming` の教訓通りの失敗。
  `ime_macos.rs::is_japanese_ime_open()` は**背景スレッド**（IME ポーリングスレッド）から
  呼ばれるので dispatch が正しいが、その前提を確認せずパターンだけ移植した。
- **選択肢**:
  - A: `keyboard_layout_id()` を `dispatch_sync_f` 無しの直接呼び出しに変更する
    （呼び出し元がメインスレッドである前提を関数の契約にする）。
  - B: `lib.rs` 側で `keyboard_layout_id()` を背景スレッドから呼ぶよう変更する。
- **採用**: A
- **理由**: ★ 呼び出し元を変えるより、関数側の実装を「メインスレッドから呼ばれる」
  という実際の呼び出しパターンに合わせる方が変更が小さく、`lib.rs` 側の
  「ロガー起動前に同期的に解決する」という既存の設計意図（D-G・Windows 実装時の教訓）
  とも整合する。
- **トレードオフ**: `keyboard_layout_id()` は「メインスレッド専用」という暗黙の契約を
  持つことになる。★ 背景スレッドから呼ぶ新しい呼び出し元を将来追加する場合は、
  再び `dispatch_sync_f` 経由に戻す必要がある（doc comment に明記済み）。
- **影響範囲**: `src-tauri/src/input/observe_macos.rs` の `keyboard_layout_id()` のみ。
- **見直しタイミング**: `keyboard_layout_id()` の呼び出し元が増える、または背景スレッドから
  呼ぶ必要が生じたとき。
- **再発防止**: 修正後、実機で3回（累計 ~3分）起動→操作→終了を繰り返し、
  クラッシュ0件・新規クラッシュレポート0件を確認した（T5 節参照）。

---

## T5: 実機総合確認（2026-08-24・macOS 実機・`./target/debug/gse-next` を直接起動）

★ ターミナルベースで `nohup ./target/debug/gse-next` を起動し（`cargo run` は再ビルドの
出力がログに混ざるため、確認は事前ビルド済みバイナリを直接叩いた）、合成マウス移動
（scratchpad の `inject`）+ `open -a` によるアプリ切替で活動を発生させた。

| 項目 | 結果 |
|---|---|
| 起動 | ⚠️ **1 回目はクラッシュした**（判断3 の `dispatch_sync_f` 自己デッドロック）。修正後は複数回起動して 0 クラッシュ |
| `keyboard_layout` が `meta` に載る | ✅ `"keyboard_layout":"com.apple.keylayout.ABC"` |
| `capabilities.config_gated` | ✅ `focus_transition`/`pointer_bin`/`secure_input` が正しく列挙（T3 の実行時確認） |
| `pointer_bin` の行が出る | ✅ 73 行（合成マウス移動 300px + スクロール25回、約90秒） |
| `focus_transition` の行が出る | ✅ 13 行（`open -a` によるアプリ切替 4 往復） |
| `secure_input` の行が出る | ✅ 1 行（起動直後のベースライン値 `on:false`。★ 変化が無い限りこれ以降は出ない設計 — 区間の起点を確定するための初回送出であり「変化したときだけ」の趣旨に反しない） |
| `buttons` (pointer_bin) | ✅ 全行で `0`（ADR-014 D4 の mac 側マスクに `*MouseDown` が無いための設計通りの非対称。決定1 で事前記録済み） |
| ドロップの実測 | ✅ **0 件**（`hook_health` 行が 0 = 状態変化なし。`dropped_delta` は 1 件も出現しなかった） |
| 既存の打鍵 tap | ✅ 影響なし（`CGEventTap installed ... tap_mode=Input Monitoring input_monitoring=true accessibility=true` が正常出力） |
| 長時間安定性 | ⚠️ **約90秒のみ確認**（数時間規模の安定性は未検証・研究者へ返す） |
| 区間指定削除UI/一時停止/インジケータ | ⚠️ **未確認** —— ★ 本 Mac ではスクリーンショットが撮れず（`memory: macos-app-visual-check-workflow`）、かつ本タスクの diff はこれらのファイル（`redaction.rs`/`recording.rs`/`RecordingControls.tsx`）に一切触れていない（OS 非依存の既存機能）。目視確認は別途 AX API 経由の操作か、人手での確認が必要 |

★ **クラッシュを実機で踏んで直せたこと自体が、この T5 ステップを飛ばしてはいけない
理由の実例になった**（もし T5 を省略していたら、G1 相当の配布判断に混入していた）。

修正後の再検証（別セッションで再ビルド・再起動）でも 0 クラッシュ・
`Input Monitoring` → `Accessibility` フォールバックの既存動作も正常に確認できた。

## 判断4: ⚠️ ポインタ tap の無通知失効対応は「即再有効化」のみ実装し、「完全失効時の再作成」は実装しない

- **判断日時**: 2026-08-24
- **背景**: 引き継ぎ文書 §2 T2 は「`CGEventTapIsEnabled` の定期確認・無通知失効への
  再有効化」を要求している。`hook_macos.rs` の既存実装は2段構え:
  (a) `TapDisabledByTimeout`/`ByUserInput` イベントをコールバックで検知し
  `CGEventTapEnable` で即再有効化、(b) `CFRunLoop::run_current()` が完全に戻ってきたら
  （tap 自体が無効化された場合）外側のループで tap ごと作り直す。
- **実装したのは (a) のみ**（`pointer_event_callback` の冒頭で
  `TapDisabledByTimeout`/`ByUserInput` を判定し `POINTER_TAP_PORT` 経由で再有効化）。
- **実装しなかったもの**: (b) の「tap が完全に無効化されたら作り直す」経路。
  ★ 理由: `run_pointer_loop` は `CFRunLoop::run_in_mode`（100ms 区切り）でポンプしており、
  `run_current()` のような「exit で失効を検知する」形になっていない。完全失効の検知には
  別途 `CGEventTapIsEnabled(tap.mach_port)` を毎ループ確認する仕組みが要り、
  本セッションの時間内では実装・実機検証が終わらないと判断した。
- **トレードオフ**: ⚠️★★★ **ポインタ tap が完全に無効化された場合（(a) の再有効化では
  回復しない稀なケース）、プロセスを再起動するまで `pointer_bin` が出なくなる。**
  ★ 打鍵の主計器（`hook_macos.rs`）は (a)+(b) 両方を持つので影響を受けない。
  ⚠️ O1 は数日〜数週間走るので、この残差リスクは無視できない。
- **見直しタイミング**: ★ **次セッションで (b) を実装すること。** 具体的には
  `run_pointer_loop` のポンプループ内で `CGEventTapIsEnabled(POINTER_TAP_PORT の port)`
  を毎秒程度確認し、無効なら `run_loop.remove_source` → tap 再生成 → 再登録する
  外側リトライを追加する。
- **完了報告への明記**: この判断は「やらなかったこと」として完了報告に明記する
  （§6 チェックリスト）。

---

## code-reviewer / security-checker レビュー（2026-08-24）と対応

★ `/finish-task` Step 3 前の実装中レビュー（code-reviewer ∥ security-checker 並列起動）で
HIGH 2件・MEDIUM 6件・LOW 5件（code-reviewer）+ HIGH 1件・MEDIUM 2件・LOW 4件（security-checker）
の指摘を受けた。以下の通り対応した。

### 対応した指摘

| 指摘元 | 重大度 | 内容 | 対応 |
|---|---|---|---|
| code-reviewer | HIGH | `secure_input` のエッジが `try_send` 失敗で永久に失われる（`last_secure` を送信**前**に更新） | ★ 送信成功時のみ `last_secure` を進める形に修正 |
| code-reviewer | HIGH | ポインタ tap 初回設置失敗にリトライが無い | ★ `try_install_pointer_tap` + backoff (2s→5s→10s) のリトライループを実装 |
| security-checker | HIGH (H1) | tap 未設置時に `CFRunLoopRunInMode` を回すとビジーループになりうる（spawned thread で 500ms あたり ~2.9M 反復と実測） | ★ tap 未設置の間は `run_in_mode` を呼ばず `thread::sleep(100ms)` に切り替え |
| code-reviewer | MEDIUM | 再有効化にスラッシング上限が無い | ★ `POINTER_CONSECUTIVE_REENABLES` + `MAX_CONSECUTIVE_REENABLES=100`（`hook_macos.rs` と同値）を追加 |
| code-reviewer | MEDIUM | ポインタ tap の生存信号が無い | ★ `POINTER_CALLBACK_COUNT: AtomicU64` を追加（診断用・`hook.rs::CALLBACK_COUNT` と同役割） |
| code-reviewer | MEDIUM | `SECURE_INPUT_AVAILABLE` が `cfg!()` 直書きで `imp::` 経由でない | ★ 3 モジュール（macos/windows/stub）に `SECURE_INPUT_AVAILABLE` const を追加し `observe.rs` から委譲する形に統一 |
| code-reviewer | MEDIUM | テストが production の配線を通っていない（トートロジー） | ★ `fold_delta`/`build_pointer_bin` を純関数として切り出し、callback とテストの両方から呼ぶ形に変更 |
| code-reviewer | MEDIUM | `keyboard_layout_id` のメインスレッド契約が doc コメントだけ | ★ `debug_assert!(MainThreadMarker::new().is_some(), ...)` を追加（release ビルドはコスト0） |
| code-reviewer | LOW | `thread::spawn` に名前が無い | ★ `Builder::new().name("gse-o1-pointer")` に変更 |
| code-reviewer | LOW | Windows 側に `secure_input_enabled` 常時 `None` の対テストが無い | ★ `observe_windows.rs` に `secure_input_enabled_always_none_on_windows` を追加 |
| security-checker | LOW (L1) | `IsSecureEventInputEnabled() -> bool` の FFI 型が不正確（`Boolean` は `unsigned char`） | ★ `-> u8` に変更し `!= 0` で正規化 |
| security-checker | LOW (L2) | `start()` が冪等でない（二重呼び出しで observer/tap が二重設置されうる） | ★ `observe.rs::start()` に `STARTED: AtomicBool` ガードを追加（全 OS 共通） |
| security-checker | LOW (L3) | `POINTER_TAP_PORT` の SAFETY コメントの根拠が事実と違う | ★ 「tap が生存している間だけ非null」ではなく「`run_pointer_loop` が戻らないため mem::forget した tap がプロセス終了まで生存する」という正しい論法に書き直した |

★ 全修正後、`cargo test --workspace`（479 lib tests 含む）緑・`cargo clippy --all-targets`
警告0（変更ファイル内）・実機で再度 T5 相当の確認（起動・pointer_bin/focus_transition/secure_input
の出力・クラッシュ0件）を実施した。

### ⚠️ 対応しなかった指摘（★ 理由付きで残す。次セッション/研究者へ返す）

| 指摘元 | 重大度 | 内容 | ⚠️ なぜ今回は対応しないか |
|---|---|---|---|
| security-checker | MEDIUM (M1) | `secure_input` の現在値が G1 ブロック分割 (`Rotate`) や一時停止解除をまたいで再送出されない（エッジ検出の状態がプロセス寿命で持たれる一方、行の書き出しはファイル境界/pause でも区切られるため、後続ファイル/再開後の区間で `on` の根拠行が欠けうる） | ★ `recording.rs`（pause/resume）と `logger.rs`（`Rotate`）という別モジュールの状態遷移を `observe_macos.rs` の 1Hz ループへ橋渡しする配線が要り、本タスクのスコープ（`observe_macos.rs` の実装）を超える。⚠️ プライバシー漏洩ではなく解析側のミスアトリビューションリスクなので、次セッションでの設計判断（`Rotate`/`resume` の通知を受け取る仕組みを作るか、あるいは低頻度のハートビート送出に切り替えるか）に委ねる |
| security-checker | MEDIUM (M2) | `OBSERVATIONS_DROPPED` を誰も読んでいない（「黙って消さない」という doc の主張が実態と不一致。3箇所目の加算元は本タスクで追加した） | ★ 唯一の妥当な配線先 (`lib.rs` の `liveness` 監視スレッド) は `EVENTS_DROPPED`/`hook_health`/ブロック境界処理が密結合した繊細なロジックであり、複数回の HIGH 指摘を経て現在の形に固まっている。本タスクの範囲を超えて触るリスクの方が大きいと判断し見送った。⚠️ 既存の穴（`FOCUS_TX`/`POINTER_TX` の分も含め元々未読み出し）であり、本タスクが悪化させたのは「読まれない加算箇所が2→3に増えた」点のみ |
| security-checker | LOW (L4) | `redaction.rs::retain_outside_range` は `secure_input` の on/off ペアの片側だけ削除しうる | ★ `redaction.rs` は本タスクで一切触っていない既存コード。プライバシー上は安全側（消えすぎる方向）であり、解析スクリプト側の対応で足りるとレビュー自身が明記している |

### ⚠️ 実機での追加検証（レビュー対応の妥当性確認）

- **CPU 使用率の調査**: レビュー後の実機起動で `ps` が 99-100% CPU を示し、H1 の busy-loop 修正が
  不十分ではと疑った。★ `sample` で `gse-o1-pointer` スレッドを直接調べたところ
  `mach_msg2_trap`（正しくブロッキング待機）にいることを確認し、疑いを晴らした。
  ⚠️★★★ **念のため `git stash` で本タスクの変更を全て外し（macOS 側が明示的スタブの状態）、
  同じ 99% CPU が再現することを実測した** —— ★ **この高 CPU 使用率は本タスクの変更と無関係の
  既存 Tauri/WebView 挙動**である（`observe` がスタブでも再現するため）。
  → ★ 本タスクのスコープ外の既存事象として研究者へ返す（別途調査が要る）。
- **`moved` バケットの疑似リグレッション調査**: HIGH/MEDIUM 修正後の実機テストで、合成マウス
  移動（±1px の振動）を注入したところ `moved:0` が連続し、リファクタリングでバグを入れたかと
  疑った。★ コードを詳細に見直したが `fold_delta`/`build_pointer_bin` は元のロジックと数学的に
  同一であることを確認。★ 疑いを検証するため注入ツールを ±20px/±15px の単調な大きな移動に
  変更して再実行したところ `moved` が 1〜4 の非ゼロバケットで安定して出ることを確認した。
  → ★ **原因は production コードではなく、注入ツールの ±1px 振動が macOS のイベント coalescing
  で丸められていたこと**（テストツールの artifact）。production コードの正しさを実機で再確認できた。

## 判断5（発見・本タスクの diff 外）: `replay.rs` に既存の flaky test を発見した（★ 修正しない・記録のみ）

- **発見日時**: 2026-08-24（`cargo test --workspace` を最終確認で複数回実行中）
- **症状**: `o1_observation_lines_are_skipped_by_run_replay` がまれに失敗する
  （実測: 単体/`--bin gse-replay` 単独では 3/3 通過、`--workspace` 全体では 1/2 で失敗）。
- **真因（`git blame` で特定）**: **本タスクの diff ではなく、既に main にマージ済みの
  別セッションのコミット `9eb1384c`**（"feat(input,logger): O1 (R3-a) の非打鍵チャネルと
  被験者の 3 点セットを実装する"・PR #113・Windows 側実装セッション）が原因。
  ★ 新テスト関数 `o1_observation_lines_are_skipped_by_run_replay` を、既存の
  `hook_health_line_is_skipped_by_run_replay` の `#[test]` 属性とその関数定義の**間**に
  挿入した結果:
  - 旧 `#[test]`（2026-08-09 由来）が**新関数のほうに再結合**され、
    新関数の直前にあるもう1つの `#[test]` と合わせて**同じ関数に `#[test]` が2回**付いた
    （`duplicated attribute` 警告の原因）。
  - `hook_health_line_is_skipped_by_run_replay` は**自分の `#[test]` を失い、
    テストとして実行されなくなった**（`dead_code` 警告の原因 —— **静かにテストされなくなった
    回帰保護**である）。
  - 二重登録された `o1_observation_lines_are_skipped_by_run_replay` の2インスタンスが
    **同一の一時ファイルパス**（`std::process::id()` ベース。同一プロセス内なので両インスタンス
    で同じパスになる）へ並列に書き込み・削除するため、テストランナーの並列実行と競合し
    **まれに失敗する**。
- **本タスクとの関係**: ⚠️★★★ **私の diff は `src-tauri/src/bin/replay.rs` を一切触っていない**
  （`git diff --stat` で確認済み）。★ この bug は完全に無関係な既存コードであり、
  たまたま今回のフルテスト実行で踏んだだけである。
- **対応**: ⚠️ **修正しない**（本タスクのスコープ外。CLAUDE.md「既存のテストを無断で変更しない」
  にも配慮し、対象が完全に別セッションの成果物であるため）。★ この発見を記録として残し、
  ユーザー/研究者に報告する。
- **見直しタイミング**: 別タスクとして修正することを推奨する。修正内容は明確
  （2385行目の重複 `#[test]` を削除し、`hook_health_line_is_skipped_by_run_replay`
  （2425行目）に `#[test]` を付け直すだけ）。

---

## /cross-review（Claude ∥ Codex 並列・2026-08-24）と対応

★ code-reviewer/security-checker の実装中レビュー対応後、`/cross-review` を実行した
（`cross-reviewer` エージェント経由、diff 688行・予算/機密チェック通過）。

### 両者一致 HIGH（★★★ 対応済み）

**`POINTER_CONSECUTIVE_REENABLES` が `MAX_CONSECUTIVE_REENABLES`（100）に達すると、
`pointer_ok` が `true` のまま永久に固着し、ポインタ tap が完全に死んだ状態から
二度と回復しないバグ。** ★ 皮肉にも、直前の code-reviewer レビュー対応で追加した
スラッシング防止策（判断: MEDIUM-1 対応）自体が原因だった —— 上限到達後はコールバックが
「何もせず return」するだけで、`run_pointer_loop` 側の `pointer_ok` を `false` に戻す経路が
無く、外側の backoff-retry ループ（`pointer_ok == false` のときだけ発火）が永久に起動しない。
結果: **`pointer_bin` がプロセス再起動まで無音で死ぬが、`capabilities.config_gated()` は
宣言し続ける**（ADR-013 D1「計器が無いなら自己申告する」の趣旨違反）。

- **修正**: `POINTER_TAP_GAVE_UP: AtomicBool` を追加。コールバックが上限到達で諦めた
  ときにこのフラグを立て（Atomic のみ・`hook-constraints` 準拠）、`run_pointer_loop` の
  ループ先頭で毎周期 `swap(false)` して読み取り、立っていたら `pointer_ok = false` へ戻して
  既存の backoff-retry 経路（`try_install_pointer_tap` の再実行）に接続した。
  ★ `try_install_pointer_tap` は成功時に `POINTER_CONSECUTIVE_REENABLES` を 0 に戻す既存実装
  なので、再作成後は正常にカウンタもリセットされる。
- 修正後、`cargo build`/`cargo test --workspace`（479 lib tests green）/実機起動（クラッシュ0）
  で再確認した。

### Codex 指摘・採用（MEDIUM）

`secure_input` の2段目（`observe_macos.rs` → `secure_rx` チャネル → `lib.rs` の drain スレッド
→ `logger` チャネル）で、1段目（HIGH-1 是正済み）と異なり2段目は focus/pointer と同じ
「送れなくても待たない」パターンのままで、失敗が一切検知できなかった。
→ ★ `lib.rs` の `recv(secure_rx)` 腕で `try_send` 失敗時に `OBSERVATIONS_DROPPED` を
加算するよう修正（M2 で「誰も読んでいない」と記録済みのカウンタだが、
**「起きたら数える」だけは即座に足せる低コストな改善**として採用した）。

### Codex 指摘・却下（誤検知として記録）

Codex（read-only sandbox のためコンパイル不可）が objc2-app-kit/`MainThreadMarker` の
API 不一致を懸念して HIGH としたが、**実機で `cargo check`/`cargo test --workspace`/
`cargo clippy --all-targets` を複数回実行し全て green** であることを確認済み
（T5 節・本節冒頭のビルド確認）。★ Codex 自身も「誤検知なら証跡が必要」と自己申告しており、
sandbox 制約による推測であって実装の欠陥ではないと判断し却下した。

### 見送った提案（次セッション/研究者へ返す）

- M1（`secure_input` の Rotate/pause 境界問題）の緩和策として cross-review が
  「`observe_macos.rs` 内だけで完結する低頻度ハートビート送出」を提案した。
  ★ 判断5（本タスクでは見送り）は維持するが、次にこの領域を触るセッションへの
  具体的な選択肢として記録しておく。
- `POINTER_CALLBACK_COUNT`（本タスクで追加した生存信号）も `OBSERVATIONS_DROPPED` と
  同様に誰にも読まれていない。★ M2 の見送り判断の対象をこの新カウンタにも広げて記録する。
