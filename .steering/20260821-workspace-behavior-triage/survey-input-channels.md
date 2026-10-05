# Rust から取れる入力・作業動作信号のサーヴェイ — R3 の段 1 を凍結するための一次調査

> 2026-08-22 / `.steering/20260821-workspace-behavior-triage/`
> ⚠️ **コード変更ゼロ。** 本文書は **ADR-014 D4（R3 の段 1）を凍結するための材料**であり、決定ではない。

## §0 なぜ調べるか（★ 目的を先に固定する）

**ADR-014 D4** は R3 の候補チャネルを **「実データを見る前に人が凍結する」**と決めた
（ADR-012 D2 段 1 の手続き）。⚠️ **凍結するには「そもそも何が取れるか」を厳密に知っている必要がある。**

★ 本サーヴェイが答えるべき問いは **3 つだけ**である:

| # | 問い | ⚠️ なぜ要るか |
|---|---|---|
| 1 | ★★★ **識別子を一切保存せずに「遷移が起きた時刻」だけ取れるか** | ADR-012 D4 **L-c 仕様**が要求。⚠️ **成立しないなら L-c は R3 の段 1 に入れられない** |
| 2 | ★★★ **座標を保存せずに「ポインタの量」だけ取れるか** | ADR-012 D4 **L-b 仕様**が要求（★ 累積で軌跡が復元できると**画面内容の代理**になる） |
| 3 | ★★★ **アイドル時間をキーボードとマウスで分離できるか** | ⚠️ `liveness.rs:543` が「**マウスのみの作業は Down に化ける**」を**既知の限界として仕様固定**している。★ 分離できれば L-a の左打ち切り問題が変わる |

⚠️★★★ **副次的な問い（★ 決定に直結する）**: **常時（数日〜数週間）稼働に耐えるか。**
★ G1 は 5 分ブロックなので、**フックが OS に外される / event tap が無効化される**問題に当たらなかった。
⚠️ R3 は当たる。

---

## §1 ★ repo 側で確定している事実（★ 本セッションで直接確認・推測なし）

### 1.1 現行の計器が **既に取っているもの**

| 信号 | NDJSON 行 | 出所（`file:line`） |
|---|---|---|
| **全打鍵の VK コード ＋ press/release** | `{"type":"key","t":…,"vk":…,"press":…}` | `src-tauri/src/logger.rs:1382-1392` |
| 対象キー | 英字 `0x41-0x5A` / 数字 `0x30-0x39` / テンキー `0x60-0x6F` / 記号 OEM `0xBA-0xC0`,`0xDB-0xDF` / BS `0x08` / Enter `0x0D` / Space `0x20` / Tab `0x09` / Delete `0x2E` | `src-tauri/src/input/hook_windows.rs:76-90`（`is_typing_key`） |
| ⚠️ **修飾キー（Shift/Ctrl/Alt）は記録されない** | — | 同上（`is_typing_key` が除外） |
| 貼り付け（**Ctrl+V の VK 組合せで検知**・中身は取得しない） | `{"type":"paste",…}` | `hook_windows.rs:530-535` / `schema_dto.rs:86-97` |
| IME 状態 | `{"type":"ime_state",…}` | `schema_dto.rs:136` |
| **入力の有無（マウス込み）** | `hook_health` / `starve_window` の `starved_ms` | `src-tauri/src/input/liveness.rs`（`GetLastInputInfo`） |

### 1.2 現行の計器が **取っていないもの**（★ R3 が足す候補）

| 信号 | 状態 | 出所 |
|---|---|---|
| **フォーカス / ウィンドウ遷移** | ⚠️ **未取得。** WinEventHook は **IME 専用**（`EVENT_OBJECT_IME_CHANGE`〜`EVENT_OBJECT_IME_HIDE`） | `hook_windows.rs:315-322` |
| **ポインタ（移動量 / クリック / ホイール）** | ⚠️ **未取得。** マウスフックは存在しない | `grep "WH_MOUSE_LL" src-tauri/` → 0 件 |
| **`left_observation`**（ADR-009 D2 の目的変数の 1 カテゴリ） | ⚠️★★★ **実装ゼロ** | `grep -rn "left_observation" src-tauri/src/` → **0 件** |
| スクロール / 選択範囲 / キャレット / undo・redo | ⚠️ 未取得 | — |

### 1.3 ★ **feature フラグの現状**（★ 追加コストの見積もりに直結する）

`src-tauri/Cargo.toml:130-141` で有効な `windows` crate feature:

```
Win32_Foundation / Win32_UI_WindowsAndMessaging / Win32_UI_Input_KeyboardAndMouse /
Win32_UI_Input_Ime / Win32_System_Threading / Win32_System_LibraryLoader /
Win32_UI_Accessibility / Win32_System_Com / Win32_System_Variant
```

解決済みの版（`Cargo.lock`）: **`windows` 0.58.0**（★ 宣言どおり。⚠️ 依存ツリーには `0.61.3` も居る）/
`core-graphics` 0.24.0・0.25.0 / `core-foundation` 0.9.4・0.10.1 / `objc2` 0.6.4。

★ **feature 追加の要否**（⚠️★ **初版の見積もりを 1 件訂正した**。★ サーヴェイ 2 本と私自身の
`windows-0.58.0/Cargo.toml` 直読で確認済み）:

| チャネル | ★ 新しい feature | 根拠 |
|---|---|---|
| **L-c（フォーカス遷移 `SetWinEventHook`）** | ★ **不要** | `Win32_UI_Accessibility`（有効）＋ 定数は `Win32_UI_WindowsAndMessaging`（有効） |
| **L-b（ポインタ・`WH_MOUSE_LL`）** | ★ **不要** | `Win32_UI_WindowsAndMessaging`（有効） |
| ⚠️ **L-b（Raw Input）** | ★ **不要** ——⚠️ **初版の「要る見込み」は誤りだった** | ★ `windows-0.58.0/Cargo.toml:716,719` を直読: **`Win32_UI_Input_KeyboardAndMouse = ["Win32_UI_Input"]`** → repo が宣言済みの `Win32_UI_Input_KeyboardAndMouse` から **`Win32_UI_Input` が推移的に有効** |
| クリップボード（`GetClipboardSequenceNumber` / `AddClipboardFormatListener`） | ⚠️ **`Win32_System_DataExchange`** | 未宣言（存在は確認済み） |
| セッションロック（`WTSRegisterSessionNotification`） | ⚠️ **`Win32_System_RemoteDesktop`** | 未宣言（存在は確認済み）。★ 定数 `WM_WTSSESSION_CHANGE`/`WTS_SESSION_LOCK` は既に有効な側 |
| 電源 / 在席 / ディスプレイ電源 | ⚠️★ **`Win32_System_Power` ＋ `Win32_System_SystemServices` の 2 つ** | ⚠️ **関数と GUID が別 feature に分かれている**（関数=`System/Power`、`GUID_SESSION_DISPLAY_STATUS` 等=`System/SystemServices`） |
| クリップボードのサイズ取得（★ 採らない） | `Win32_System_Memory` | ⚠️ **採らない**（§2.6） |
| 仮想デスクトップ（★ 採らない） | `Win32_UI_Shell` | ⚠️ **識別子ゼロと両立しない**（§2.2） |

---

## §2 ★★★ 3 つの問いへの答え（★ 両 OS 横断・これが本サーヴェイの核心）

### 問い 1 — **識別子なしで「遷移が起きた時刻」だけ取れるか** → ✅ **両 OS で成立する**

| | Windows | macOS |
|---|---|---|
| 手段 | `SetWinEventHook(EVENT_SYSTEM_FOREGROUND /*0x0003*/, ...)` ＋ `WINEVENT_OUTOFCONTEXT｜SKIPOWNPROCESS` | `NSWorkspace.notificationCenter` の `didActivateApplicationNotification` |
| ★ 識別子を捨てられるか | ✅ **`hwnd`/`idObject`/`idChild`/`idEventThread` を全て `_` で捨てられる**。★ **repo に既存の前例がある**（`win_event_callback` は既に 4 つとも `_` で受けている） | ✅ **`userInfo` を読まなければよい**。★ さらに `activeSpaceDidChangeNotification` は **`userInfo` 辞書自体が存在しない**（API 契約として保証） |
| 権限 | ★ 不要 | ★ **TCC 不要**（⚠️ AX 経路とは別） |
| feature / crate | ★ **追加不要**（`Win32_UI_Accessibility` は有効） | ⚠️ `objc2-app-kit` の追加 or `#[link(name="AppKit")]` 自前 FFI。★ **`Cargo.lock` に `objc2-app-kit 0.3.2` が既に推移依存で存在** |
| ⚠️ 実装上の要点 | ⚠️ **別フックを 1 本立てる**（`eventMin`/`eventMax` は**単一の連続範囲**しか取れず、IME 群 `0x8027..0x8029` と `0x0003` を 1 本にすると**デスクトップ全イベント**を購読することになる） | ⚠️ **run loop 必須**。★ CGEventTap 用スレッドに相乗りさせない |

⚠️★★★ **両 OS 共通の限界（★ 対称なので比較可能性は保たれる）**:
**「同一アプリ内のウィンドウ切替」と「別アプリへの切替」を識別子なしに区別できない。**

- Windows: 一次資料逐語「The system sends this event **even if the foreground window has changed to another window in the same thread**」
- macOS: `NSWorkspace` は**アプリ単位**。同一アプリ内の窓切替は**そもそも発火しない**。AX 経路は `AXObserverCreate(pid_t, ...)` で **PID が必須引数**

→ ★★★ **R3 で残せるのは「遷移の頻度分布」であって「注意の逸脱の頻度」ではない。** ⚠️ この制約を明記する。

### 問い 2 — **座標なしで「ポインタの量」だけ取れるか** → ✅ **両 OS で成立する（★ 質が違う）**

| | Windows（**Raw Input** 推奨） | macOS（**既存 CGEventTap に追加**） |
|---|---|---|
| 手段 | `RegisterRawInputDevices` + `RIDEV_INPUTSINK` + message-only window + **`GetRawInputBuffer` バッチ排出** | `CGEventType::MouseMoved` / `*Dragged` / `ScrollWheel` を購読し **`kCGMouseEventDeltaX/Y`(4/5) だけ**読む |
| ★ 座標を残さない保証 | ★★★ **構造的**。`MOUSE_MOVE_RELATIVE` 時、`RAWMOUSE` に**絶対座標フィールドがそもそも存在しない** ＝ **捨て忘れが起こりえない** | ⚠️ **方針的**。`CGEventGetLocation` を**呼ばなければ**座標は入らない（★ 呼べば入る） |
| feature / crate | ★ **追加不要**（`Win32_UI_Input` は `Win32_UI_Input_KeyboardAndMouse` から推移的に有効） | ★ `core-graphics 0.24` の既存 API で足りる |
| ⚠️ 罠 | ⚠️★★★ **`MOUSE_MOVE_RELATIVE` は `0x00`＝ビットではない。** `flags & MOUSE_MOVE_RELATIVE` は常に false → **絶対座標が「量」として保存される**。★ `MOUSE_MOVE_ABSOLUTE` の**不在**で判定する | ⚠️ delta は**ポインタ加速適用後**。⚠️★ **合成イベント（リモート操作・自動化）では delta が 0 のまま** |
| ⚠️ 代償 | ⚠️★★★ **注入判別ができない**（`RAWMOUSE` に注入フラグが無い）。★ `WH_MOUSE_LL` なら `LLMHF_INJECTED` で判るが、**システム全体のマウス入力を直列化**する | ★ `kCGEventSourceStateID`(45)`== 1`（HIDSystemState）で**物理入力に絞れる** |
| ⚠️ 常時稼働 | ★ **`GetRawInputBuffer` でバッチ排出でき、1000Hz マウスでも起床回数が抑えられる**。★ **OS に黙って剥がされる仕組みが無い**（`WH_MOUSE_LL` は `LowLevelHooksTimeout` で**通知なく外される**） | ⚠️★★ **既存のキーボード tap に相乗りさせない**（`MouseMoved` の高頻度が timeout 失効を誘発し、**打鍵観測を巻き込む**）→ **別 tap・別スレッド** |

⚠️★ **非対称**: Windows Raw Input は**デバイス単位のカウント**（被験者のマウス設定に依存しない）、
macOS は**加速適用後の delta**（設定依存）。→ ★ **被験者内 z 標準化が必須**。生の値を OS 間で比較しない。

### 問い 3 — ⚠️★★★ **アイドル時間をキーボードとマウスで分離できるか** → **OS で答えが違う**

| | Windows | macOS |
|---|---|---|
| 現行 | `GetLastInputInfo` | `CGEventSourceSecondsSinceLastEventType(0, kCGAnyInputEventType)`（`liveness.rs:207-232`） |
| ★ 分離 | ❌ **不可能。** `LASTINPUTINFO` は `cbSize` と **`dwTime` の 2 フィールドだけ**でデバイス種別を持たない | ✅ **可能。** ★ **関数が `CGEventType` を引数に取る** —— `kCGEventKeyDown`(10)/`KeyUp`(11)/**`FlagsChanged`(12)** と `MouseMoved`(5)/`ScrollWheel`(22)/各 Down を個別に問い合わせられる |
| 代替 | ⚠️ (a) 既存の `system_input_seen && !hook_event_seen`（★ **追加コストゼロ**。⚠️ **フック死と原理的に区別不能**）/ (b) `WH_MOUSE_LL` を 1 本足して `LAST_MOUSE_MS` を Atomic store | — |

★★★ **これは ADR 級の非対称である。** 「キーボードは 5 分静止だがマウスは動いている」＝**画面を読んでいる**（Incubation 候補）と、
「両方静止」＝**離席**を、⚠️ **macOS では分離でき、Windows ではできない。**

→ ★ **設計判断が要る**: (a) Windows に合わせて統合アイドルに落として揃える / (b) OS 別の特徴量として明示的に扱う。
⚠️ **(b) を採るなら `HMM_VERSION` の扱いを決める必要がある。**

⚠️★ macOS では **`stateID` の選択**も要る: `CombinedSessionState`(0) は**他アプリの合成イベントを含む**、
`HIDSystemState`(1) は**物理入力のみ**。★ 「人が物理的に居るか」には **(1) が意味論的に正しい**
（⚠️ 現行 `liveness.rs:209` は (0)。★ ただし現行の目的＝「人は居るのにフックだけ黙っている」の検出では
fail-safe 側に倒れるので**壊れてはいない**）。

---

## §3 ⚠️★★★ サーヴェイで判明した **R3 の設計に効く追加事実**

### 3.1 ⚠️★★★ macOS の **Secure Input** — R3 の成否に直結する（★ 最重要の新発見）

★ `EnableSecureEventInput()` は **システム全体のシングルトンかつ参照カウント式**。有効な間、
Apple TN2150 逐語「**Event taps (CoreGraphics/CGEvent.h)**」がブロックされ、
「keyboard events are not passed to any intercept processes, **regardless of foreground/background status**」。

| ⚠️ 何が起きるか | ★ 対処 |
|---|---|
| ⚠️★★★ **tap は「有効」のまま、`TapDisabled*` も来ず、単に KeyDown が届かない**（**無音のデータ欠損**） | ★ **`IsSecureEventInputEnabled()` で検知できる**（Carbon・`#[link]` 1 行） |
| ⚠️ パスワードマネージャ等が `Disable` を呼び忘れると、**そのアプリを終了するか画面ロックするまで全 tap が打鍵を受け取れない**（1Password / KeePassXC / Cursor で実例報告） | ★ 1Hz ゲートで確認し **`secure_input` フラグを NDJSON に記録**、その区間を**欠損扱い**にする |
| ⚠️★★★ **現状は「打鍵ゼロ」と「打鍵が見えない」を混同する** → **パスワード入力の直後に必ず Stuck/Incubation へ倒れる系統的バイアス** | ★ **マウスは secure input の影響を受けない** → ⚠️ **「打鍵 0 かつマウス活動あり」が検出シグナルになる**（★ **L-b を足す追加の正当化理由**） |

### 3.2 ⚠️★★★ IME 変換中の状態は **macOS ではグローバルに取れない**

| | Windows | macOS |
|---|---|---|
| 変換中か | ★ **観測できる**（WinEvent ＋ `ImmGetOpenStatus` ＋ UIA の 3 段） | ⚠️★★★ **アプリを問わずに変換を知らせる公開の通知は見つかっていない。** composition は対象アプリの `NSTextInputClient` 上で処理され、外へ知らせるかはアプリの Accessibility の実装しだい（WebKit のソースは出す・§7.5）。⚠️ 2026-10-05 訂正: 旧文は「公開 API が存在しない。composition は `NSTextInputClient` 上に閉じている」 |
| 現行実装 | `ime_windows.rs` | ⚠️ `hook_macos.rs::update_compose_state` ＝ **keycode 列からのヒューリスティック推定** |

→ ⚠️★★★ **同じ `IME_ACTIVE` フィールドでも Win=観測値 / mac=推定値であり、両 OS のデータを混ぜて学習・評価してはならない。**
⚠️ さらに **macOS 純正の「ライブ変換」は Space を押さずに変換が進む**ので、推定が特に外れる。

⚠️★★★ **かつ Windows 側の「観測」も現在は壊れている**（→ `findings-instrument-defects.md` 欠陥 1）。
★ **両 OS とも `IME_ACTIVE` の妥当性が未確立**である。

### 3.3 ⚠️ **文境界（boundary keys）の信頼性が OS で違う**

| | Windows | macOS |
|---|---|---|
| keycode の意味 | ★ **論理キー**。`VK_OEM_PERIOD`(0xBE) / `VK_OEM_COMMA`(0xBC) は一次資料が **"For any country/region"** と明記 | ⚠️★★★ **物理キー位置**。Apple ヘッダ逐語「**They identify physical keys on a keyboard**」 |
| ★ 文境界（`.`） | ✅ **レイアウト非依存で取れる** | ⚠️ **Dvorak では `.` が US の `E` 位置**、AZERTY / QWERTZ でも位置が違う → **取り違える** |
| ★ 語・段落境界 | ✅ `VK_SPACE`/`VK_TAB`/`VK_RETURN` は非依存 | ✅ `kVK_Space`(0x31)/`kVK_Tab`(0x30)/`kVK_Return`(0x24) は **"ANSI" 接頭辞を持たない機能キー**＝非依存 |

→ ★ **対処（`UCKeyTranslate` を導入せずに済ませる）**: セッション開始時に **レイアウト識別子だけ**を 1 回記録する
（Win=`GetKeyboardLayoutNameW` / mac=`TISCopyCurrentKeyboardLayoutInputSource`）。
⚠️ **US/JIS 以外のレイアウトでは文境界特徴を無効化する**（★ 除外判定であって文字復元ではない）。

⚠️★★★ **`ToUnicodeEx` / `UCKeyTranslate` を呼ばない。** ★ 呼んだ瞬間に**入力文字そのものがプロセス内に出現する**。

### 3.4 ★ 貼り付け検知 — **「コピー」と「貼り付け」は別物**（★ 両 OS で対称）

| | ★ 取れる | ⚠️ 取れない |
|---|---|---|
| Windows | **コピー/カットの累積回数** = `GetClipboardSequenceNumber()`（★ **ウィンドウ不要・`OpenClipboard` 不要・他アプリを妨害しない・識別子ゼロ**）／時刻精度が要るなら `AddClipboardFormatListener`（★ `wParam`/`lParam` が**仕様上 0 固定**＝識別子が構造的に存在しない） | ⚠️★★★ **「貼り付けが実行された」は OS レベルで原理的に取れない** |
| macOS | `NSPasteboard.changeCount`（★ ownership 変化＝コピー） | 同上（★ ESF の paste イベントは private） |

★ **現行の Ctrl/Cmd+V 検知は「貼り付けの *試行*」であり、両 OS で同じ取りこぼし特性を持つ**
（右クリック貼り付け / メニュー貼り付け / D&D / Shift+Insert / エディタ独自バインド）。
→ ⚠️ **系統誤差が OS 間で揃うので比較可能性は保たれる。** ★ ただし**開発者被験者では取りこぼしが大きい**（Vim `p` / Emacs `C-y`）。

⚠️★★ **macOS 15.4+ の Pasteboard Privacy** は非対称を生む: `NSPasteboard` の programmatic 読み出しで
**許可アラートが出る**（`AccessBehavior` の既定が `.ask`）。⚠️ **`external_paste_chars`（＝ `(b)` 自力解決率の構成要素）が
macOS 側だけ欠測しうる** → ★ **PreReg / GATE の合否契約に影響する**。
⚠️ 「中身を読まずにサイズだけ」は**公開 API では不可能**（`detectedMetadata` は型のみ）。

### 3.5 ⚠️★★ 配布 — **macOS で App Sandbox を有効にしてはならない**

★ Apple DTS（Quinn）逐語:
「**The APIs gated by the Accessibility privilege are not compatible with the App Sandbox**,
but the APIs gated by the PostEvent and ListenEvent privileges are compatible with the App Sandbox.」

→ ⚠️★★★ **Sandbox を有効にすると「Input Monitoring → Accessibility フォールバック」（プロジェクト制約 4）が片肺になる。**
★ **Developer ID 署名 + 公証（notarized DMG）での直接配布を選ぶ**。⚠️ MAS 配布は制約 4 と両立しない。

★ 併せて: **ad-hoc 署名は CDHash がビルドごとに変わり TCC 許可が毎回失われる**。
⚠️ ★ **これは `hook_macos.rs:582` が既に把握している症状の根本原因**であり、
**Developer ID 署名を入れればフォールバックへの依存自体が減る**。

### 3.6 ⚠️★★ Windows: **昇格プロセスの打鍵が届かない可能性**（★ `liveness` の第 2 の偽陽性源）

★ UAC 公式文書は「UIAccess **があれば** low-level hooks / raw input / GetKeyState で
**全整合性レベルの入力を読める**」と逐語で書く。→ ⚠️ **UIAccess が無ければ読めない**と強く読める（⚠️ 明記ではない）。

⚠️ 実運用上の含意: **管理者権限のエディタ / ターミナルへの打鍵が `key` 行に載っていない可能性がある。**
★ しかも `GetLastInputInfo` は入力を検知するので、⚠️ **`starved_ms` が進み「フックが死んだ」と誤判定する**。
→ ★ `liveness.rs:543` の `mouse_only_work_is_a_known_false_positive` と**同型の第 2 の偽陽性源**であり、**未文書化**。

---

## §4 ⚠️★★★ 両 OS の差 — **対のテストが要る箇所**

> ★ `docs/agent-shared.md` 逐語:「⚠️★★ **手元の検証は CI の代替にならない。** macOS では `hook_windows.rs` が
> 1 行もコンパイルされず、逆に `#[cfg]` を付けないテストは**相手側の OS でも走る**」
> → ★ **OS ごとに規則が違うロジックは両 OS に対のテストを置く。**

| # | 差 | ⚠️ 何が壊れるか | ★ 置くべき対のテスト |
|---|---|---|---|
| 1 | ⚠️★★★ **アイドルの種別分離**（mac=可 / Win=不可） | ★ 特徴量が OS 間で同一でなくなる | ⚠️ **仕様として固定する**: Win 側は「分離できない」を明示的にテストで固定（`liveness.rs:543` と同じ作法）、mac 側は分離値のテスト |
| 2 | ⚠️★★★ **`IME_ACTIVE`**（Win=観測 / mac=推定） | ★ **混ぜて学習・評価すると意味が違うものを同一視する** | ⚠️ 両 OS で `IME_ACTIVE` の**出所を記録**し、解析側で分岐する |
| 3 | ⚠️ **keycode の意味**（Win=論理 / mac=物理） | ★ 文境界が非 US 配列で崩れる | ★ **レイアウト識別子を記録**し、両 OS で「US/JIS 以外は文境界を無効化」を対でテスト |
| 4 | ⚠️ **ポインタ量の単位**（Win Raw Input=デバイスカウント / mac=加速後 delta） | ★ 生値の OS 間比較が無意味 | ★ 被験者内 z 標準化を**両 OS 共通の前段**に置く |
| 5 | ⚠️ **スクロールの単位**（Win=`WHEEL_DELTA`120 / mac=`IsContinuous` でライン↔ピクセルが動的に切替） | ★ 正規化式が OS で違う | ★ 正規化を OS 別に実装し、**同じ入力で同じ特徴値になる**ことを対でテスト |
| 6 | ⚠️★★ **Secure Input**（mac のみ・検知可） | ★ 打鍵欠損を離席と誤判定 | ★ mac に `secure_input` フラグのテスト。⚠️ Win 側は「該当機構なし」を明示 |
| 7 | ⚠️ **貼り付け文字数**（mac 15.4+ で許可アラート） | ★ **`(b)` 自力解決率が macOS だけ欠測** | ⚠️ **`capabilities`（ADR-013 D1）に載せて機械判定できるようにする** |
| 8 | ⚠️ **昇格プロセスの打鍵**（Win のみ） | ★ `starved_ms` の偽陽性 | ★ Win に実機確認事項として記録（⚠️ 自動テスト不可） |

---

## §5 ★ R3 の段 1 への反映 — **ADR-014 D4 の候補表を確定する**

### 5.1 ★ 成立が確認できたもの（★ **段 1 に入れる**）

| チャネル | Windows | macOS | ★ 識別子ゼロ |
|---|---|---|---|
| **フォーカス遷移の時刻**（L-c） | `SetWinEventHook(EVENT_SYSTEM_FOREGROUND)`・★ **feature 追加不要**・**別フック 1 本** | `NSWorkspace.didActivateApplicationNotification`・★ **TCC 不要** | ✅ **両 OS で成立** |
| **ポインタ量**（L-b） | ★ **Raw Input**（`RIDEV_INPUTSINK` + `GetRawInputBuffer`）・feature 追加不要 | 既存 tap に `MouseMoved`/`*Dragged` 追加・★ **別 tap に分ける** | ✅ **成立**（⚠️ Win は構造的 / mac は方針的） |
| **クリック / ホイール** | 同上（`usButtonFlags` / `usButtonData as i16`） | `ScrollWheel` ＋ `IsContinuous`(88) 分岐 ＋ **`MomentumPhase`(123)==0 のみ採用** | ✅ 成立 |
| **打鍵のキー種別**（D4e） | 既存（★ `LLKHF_INJECTED` を足すべき） | 既存 | ✅ 成立 |

### 5.2 ⚠️ **段 1 に入れないと確定したもの**（★ ADR-013 D6 の作法で明示 record）

| 入れないもの | ⚠️ 理由（★ サーヴェイで確定） |
|---|---|
| ⚠️★★★ **役割カテゴリ**（`editor`/`terminal`/`browser`） | ★ **ADR-009 D2 が「収集開始前に計器へ入れない」と条件を付けている**。⚠️ さらに**技術的にも識別子必須**（Win=HWND→PID / mac=`AXObserverCreate(pid_t,...)`）→ **識別子ゼロと両立しない** |
| ⚠️ **同一アプリ内のウィンドウ切替** | ★ **両 OS で識別子なしには不可能**（§2 問い 1） |
| ⚠️ **仮想デスクトップ切替 / フルスクリーン化** | Win: ★ **専用通知が存在しない**（MS 公式明言）。`IVirtualDesktopManager` は HWND + GUID 必須 |
| ⚠️★★★ **アプリ内の操作種別**（保存/実行/テスト/diff 承認/undo の**完了**） | ★★★ **原理的に不可能。** 意味への唯一の公開経路（Win=MSAA/UIA、mac=AX）が**構造上 HWND / PID を要求する**。★ **`AXObserverCreate` は `pid_t` を第 1 引数に取る**＝ API の型シグネチャに焼き込まれている |
| ⚠️ **選択範囲の文字数** | Win=UIA / mac=AX が必要。⚠️ **同じハンドルから本文が読める**ため境界が「能力」でなく「方針」にしかならず、**静的に監査できない** |
| ⚠️ **クリップボードのサイズ**（新規に増やすこと） | ⚠️ **サイズ自体が内容情報**（パスワード長・URL 長）。★ mac 15.4+ では**許可アラート**も出る |
| ⚠️ **絶対座標 / 解像度 / `dwExtraInfo` / `hDevice` / `kCGEventTargetUnixProcessID`** | ADR-012 D4 L-b の禁止表そのもの |

### 5.3 ★ **段 1 に足すべきと分かった 3 件**（⚠️ 初版の候補表に無かった）

| # | チャネル | ★ なぜ要るか |
|---|---|---|
| 1 | ⚠️★★★ **`secure_input` フラグ**（macOS・`IsSecureEventInputEnabled()`） | ★ **無いと打鍵欠損を離席と誤判定する**。⚠️ **`left_observation` の内訳を割るという R3 の目的そのものを壊す** |
| 2 | ★ **計器の健全性**（mac=`CGEventTapIsEnabled` / Win=`LLKHF_INJECTED` ＋ フォーカスフックの生存） | ⚠️ **R3 は数日〜数週間走る**。★ G1（5 分）では当たらなかった失効パターンに当たる |
| 3 | ★ **キーボードレイアウト識別子**（セッション開始時に 1 回） | ⚠️ **文境界の妥当性が配列に依存する**（§3.3）。★ **記録しないと事後に無効化判定ができない** |

⚠️★★★ **凍結したら候補を足さない**（足すなら別 ADR・ADR-014 Migration 3）。

### 5.4 ⚠️ **実機での確認が要る事項**（★ サーヴェイでは埋まらなかった）

| # | 未確認 | ★ 確認方法 |
|---|---|---|
| 1 | ⚠️ Surface Pro 8 の Type Cover タッチパッドが `MOUSE_MOVE_RELATIVE` か `ABSOLUTE` か | ★ `usFlags` のヒストグラムをログ出力（★ **座標を保存しない**） |
| 2 | ⚠️ 昇格プロセス前面時に `EVENT_SYSTEM_FOREGROUND` / `WH_KEYBOARD_LL` が届くか | ★ 管理者権限のターミナルで打鍵し `key` 行の有無を見る |
| 3 | ⚠️ macOS: マウスのみの tap が Input Monitoring を要求するか | ★ 要求しないなら **権限ダイアログ 0 でポインタ特徴だけ集められる** |
| 4 | ⚠️ macOS 26 で Pasteboard Privacy が既定有効か | ★ `(b)` 自力解決率の可否に直結 |
| 5 | ⚠️ `LowLevelHooksTimeout` の既定値 | ★ MS が既定値を文書化していない（上限 1000ms のみ確定） |

---

## §6 ★★★ アイドルの種別分離を **Windows でも実現する具体案**（研究者指示 2026-08-22）

> ⚠️ **設計のみ。本セッションでは実装しない**（★ 記録仕様の変更＝ ADR-013 D1 の `capabilities` に載る）。

### 6.1 ⚠️ 問題の正確な形

★ `GetLastInputInfo` が返す `LASTINPUTINFO` は **`cbSize` と `dwTime` の 2 フィールドだけ**で、
**デバイス種別を持たない**（★ 一次資料で確認）。→ ⚠️ **API を変えても分離はできない。**

★ **したがって「別のデバイス種別つきの入力源を足す」以外に道が無い。**

### 6.2 ★★★ 案 — **Raw Input を *マウスだけ* 登録する**

★ **実体ソースで確認済み**（`windows-0.58.0/src/Windows/Win32/UI/Input/mod.rs`）:

| 確認事項 | 実体 |
|---|---|
| **デバイス種別が届く** | `RAWINPUTHEADER.dwType`（`mod.rs:323-328`）。`RIM_TYPEMOUSE`=**0** / `RIM_TYPEKEYBOARD`=**1** / `RIM_TYPEHID`=**2**（`mod.rs:104-106`） |
| **非フォアグラウンドでも届く** | `RIDEV_INPUTSINK` = 256（`mod.rs:94`） |
| **feature 追加** | ★ **不要**（`Win32_UI_Input` は `Win32_UI_Input_KeyboardAndMouse` から推移的に有効） |

★★★ **キーボードは登録しない。** ⚠️ 理由 2 つ:
1. ★ **`LAST_KEY_MS` は既存の `WH_KEYBOARD_LL` で既に取れている**（重複は不要）
2. ⚠️★★★ **Raw Input のキーボードは `RAWKEYBOARD.VKey` を運ぶ** —— ★ **要らないものを受け取らない**のが
   `data-privacy` の作法（⚠️ 「受け取って捨てる」より「受け取らない」）

### 6.3 ★ 何が分離できるようになるか（★ ここが本題）

★ **3 つの時刻を並べると、いまは 1 つに潰れている 4 状態が分かれる**:

| 状態 | `LAST_KEY_MS`（既存フック） | **`LAST_POINTER_MS`（新・Raw Input）** | `GetLastInputInfo`（既存） |
|---|---|---|---|
| 打鍵中 | ★ 新 | — | 新 |
| ★ **マウスのみ作業**（＝画面を読んでいる・資料を見ている） | 古 | ★ **新** | 新 |
| **離席** | 古 | 古 | ★ **古** |
| ⚠️★★★ **フックが死んでいる** | 古 | 古 | ⚠️ **新** |

⚠️★★★ **現在この表の下 2 行が区別できていない。**
★ `liveness.rs:537-554` の `mouse_only_work_is_a_known_false_positive` が
**「マウスだけ動かしている人も Down になる」を *仕様* として固定している**のは、まさにこの潰れである。

→ ★★★ **Raw Input マウスを足すと、「マウスのみ作業」と「フック死」が完全に分離する。**
⚠️ さらに **Raw Input には LL フックのような「OS が黙って外す」機構が無い**ので、
★ **Raw Input の方が生存の *証人* として信頼できる**（⚠️ LL フックは `LowLevelHooksTimeout` で通知なく外れる）。

### 6.4 ⚠️ macOS との関係 — **同じ意味の量が両 OS で揃う**

| | Windows（★ 本案） | macOS |
|---|---|---|
| キーボードのアイドル | `LAST_KEY_MS`（`WH_KEYBOARD_LL`） | `CGEventSourceSecondsSinceLastEventType(1, KeyDown/KeyUp/**FlagsChanged**)` |
| ポインタのアイドル | **`LAST_POINTER_MS`（Raw Input `RIM_TYPEMOUSE`）** | 同 `(1, MouseMoved/Down/ScrollWheel/...)` |
| 全入力のアイドル | `GetLastInputInfo`（既存） | 同 `(0, kCGAnyInputEventType)`（既存） |

⚠️★ **mac 側で 2 点直すべきことが分かっている**:
1. ★ **`kCGEventFlagsChanged`(12) を落とさない** —— ⚠️ **Shift を押しっぱなしで思考中**が誤って idle になる
2. ★ 分離アイドルには **`stateID = kCGEventSourceStateHIDSystemState`(1)** を使う（**物理入力のみ**）。
   ⚠️ 現行 `liveness.rs:209` の `CombinedSessionState`(0) は**他アプリの合成イベントを含む**
   （★ ただし現行の目的＝「人は居るのにフックだけ黙っている」では fail-safe 側に倒れるので**壊れてはいない**）

→ ★★★ **非対称は解消できる。** ⚠️ **ただし「Windows が macOS に追いつく」形であり、
`GetLastInputInfo` を賢くするのではなく *別の入力源を足す* ことでしか達成できない。**

### 6.5 ⚠️ 実装前に潰すべきリスク（★ 3 件）

| # | リスク | ★ 確認方法 |
|---|---|---|
| 1 | ⚠️★★★ **一次資料逐語「Only one window per raw input device class may be registered to receive raw input within a process」** —— ★ **Tauri / WebView2 が既にマウスを登録していると奪い合う** | ★ **実機で `RegisterRawInputDevices` の戻り値を見る**。⚠️ 失敗したら本案は成立しない（→ 代替は `WH_MOUSE_LL`。⚠️ ただしシステム全体のマウス入力を直列化する） |
| 2 | ⚠️ **message-only window が要る**（`RIDEV_INPUTSINK` は `hwndTarget` 必須）。★ `WM_INPUT` はブロードキャストではないので message-only で届く**はず** | ★ 実機確認 |
| 3 | ⚠️★★★ **`RIDEV_NOLEGACY`(48) を絶対に指定しない** —— ★ 指定すると**自アプリの通常のマウス処理が死ぬ** | ★ コードレビュー ＋ テストで固定 |

### 6.6 ★ いつ実装するか — ⚠️ **いまではない**

| ★ 理由 | 詳細 |
|---|---|
| ⚠️ **記録仕様の変更である** | ★ 新しい信号を足す ＝ **ADR-013 D1 の `capabilities` に載る**。⚠️ IME 定数の修正は「意図した挙動の**回復**」だが、こちらは「**新しい能力の追加**」であり質が違う |
| ⚠️ **ADR-013 D6 / ADR-014 D4b の順序に反する** | ★ 非打鍵チャネルは **ADR-012 の段 2（実測）待ち**。★ R3（**G1 判定後**）で **記録のみ**として入れる |
| ★ **急がない根拠** | ⚠️ 「マウスのみ作業が Down に化ける」は **hook health の観点では偽陽性だが、ADR-011/012 が `starved_ms` を *L-a（在席×非打鍵）* と再解釈した以降は *それ自体が信号* である**。→ ★ **Stage 0 / `C_write` は汚染されない** |

→ ★★★ **本案は ADR-014 D4 の L-b と同一の登録で実現できる。** ⚠️ **L-b を実装するとき同時に入れる**のが正しい。
★ `survey-input-channels.md §5.1` の候補表に**既に含まれている**（★ 新しい候補を増やさない）。

---

## §7 ★★★ TSF で IME composition の観測問題は解決できるか（研究者指示 2026-08-22）

> **研究者指示（逐語）**: 「それか TSF だとその macOS, windows の問題は解決できるかな？
> まだ期間はあるし TSF と格闘してみるのもいいのかもしれない.」

### 7.1 ★★★ 答え — **No。⚠️ 時間をかけても変わらない**

⚠️ **これは難易度の問題ではなく、API 表面に入口が存在しないという問題である。**

| # | 一次資料の逐語 | ★ 何を意味するか |
|---|---|---|
| 1 | `ITfThreadMgr::Activate` —「**Activates TSF for the calling thread.**」 | ★ **スレッドに閉じている** |
| 2 | `ITfSource::AdviseSink(riid, punk, pdwCookie)` — source は「obtained from an **`ITfThreadMgr`** object」か「from an **`ITfContext`** object」 | ⚠️★★★ **リモート対象を指定する引数が構文上存在しない** |
| 3 | ⚠️★★★ **決定打** —— MSDN *IME and TSF Accessibility in Windows XP*（★ **支援技術＝我々と同じ立場の読者向け**）:「**To access the composition string managed in TSF, the assistive technology products must create the `ITfThreadMgr` in the process of creating the target TSF-enabled applications.**」「**Initialization is a per application-thread event.**」 | ★ **Microsoft 自身が「対象プロセスの中に入れ」と書いている** |
| 4 | `GUID_COMPARTMENT_KEYBOARD_OPENCLOSE` —「**This compartment is specific to a thread manager object.**」 | ⚠️ **IME の on/off ですらグローバルコンパートメントから取れない** |

★ **補足（背景の一部訂正）**: `ITfThreadMgr::GetGlobalCompartment` の "global" は**本当にプロセス跨ぎ**である
（逐語「**enables clients to share data across processes**」）。⚠️ **しかしグローバルなのは音声入力の 2 つだけ**
（`GUID_COMPARTMENT_SPEECH_UI_STATUS` / `_SPEECH_OPENCLOSE`）で、**GSE に無意味な割り当て**になっている。

### 7.2 ⚠️★★★ **既存制約の理由付けが誤っていた**（★ 本調査の副産物）

★ 旧文（`docs/agent-shared.md` 技術的制約 #7）: 「**グローバル TSF フック禁止**: **UIPI でブロックされる**」

⚠️ **UIPI の禁止リストは逐語で 5 項目**（*Windows Integrity Mechanism Design*）——
window handle validation / `SendMessage`・`PostMessage` / **thread hooks** / **journal hooks** / **DLL injection**。
→ ★★★ **TSF も COM も WinEvent out-of-context も含まれていない。**
⚠️ さらに UIPI は「**at the same privilege (or integrity) level では一切干渉しない**」ので、
**同一整合性レベルの通常環境では発動すらしない。**

★ **ただし旧文が「`WH_GETMESSAGE` / `WH_CALLWNDPROC` のグローバルフックで `WM_IME_*` を拾う」の意味なら
部分的に正しい** —— ★ そちらは **DLL 注入を要し**（`SetWindowsHookEx` 逐語「**can be used to inject a DLL
into another process**」）、**UIPI 第 5 項に直撃**する。⚠️ **旧文は 2 つの別問題を混同していた。**

→ ★ **`docs/agent-shared.md` #7 を書き換えた**（⚠️ **禁止の結論は変えていない。理由だけを正しくした**）。

### 7.3 ⚠️ 唯一の Yes ルート（自前 TIP）のコスト — ★ **見合わない**

| 項目 | ⚠️ コスト |
|---|---|
| 実装 | in-proc COM DLL ＋ ⚠️★★★ **仮名漢字変換エンジンそのもの**（★ ユーザーの IME を*置き換える*ため） |
| 配布 | ⚠️ **32bit / 64bit の 2 本**を同一 CLSID で side-by-side 登録。逐語「**if a 64-bit application attempts to load a 32-bit text service, the load fails silently**」「**No warning dialog or message displays**」→ ★ **片方欠けると無音で欠測する** |
| 信頼 | ⚠️ 我々の DLL が **Word / Chrome / VS Code すべてに常駐**。コード署名必須・EDR 誤検知・**我々のクラッシュが被験者の全アプリを巻き添え** |
| 倫理 | ⚠️ **被験者の日常業務の入力方式を研究ツールで置換する** → IRB 説明事項の大幅増 |

★ **UIPI は TIP 案の障壁ではない**（TIP のロードは TSF マネージャが行う）。⚠️ 障壁は上記 4 つである。

### 7.4 ★★★ TSF より良い手段が見つかった — **`EVENT_OBJECT_TEXTEDIT_CONVERSIONTARGETCHANGED` (0x8030)**

★ 逐語:「**The conversion target within an IME composition has changed.
The conversion target is the subset of the IME composition which is actively selected as the target for
user-initiated conversions.**」

| ★ なぜ現行より良いか | 詳細 |
|---|---|
| **意味的に一段深い** | ⚠️ 現行の 3 定数（0x8027-0x8029）は「**IME ウィンドウの表示 / 非表示 / 移動**」＝ 候補窓の UI 挙動しか見ていない。★ 0x8030 は **composition 内部の変換対象文節の移動**である |
| ★★★ **Cognitive Friction に直結** | ★ **文節区切りの調整（←→ での変換対象移動）＝「うまく変換できていない＝迷い」の直接的な現れ**。候補窓の開閉より情報量が大きい |
| ★ **content-free が構造的** | `WinEventProc(hook, event, hwnd, idObject, idChild, dwEventThread, dwmsEventTime)` —— ⚠️ **引数に文字列が 1 つも無い** |
| ★ 実装コスト | ★ ほぼゼロ（既存 `SetWinEventHook` の範囲拡張 ＋ `match` アーム 1 本） |

⚠️★★★ **ただし採用前に潰すべき前提が 3 つある**:

| # | ⚠️ 前提 | ★ 確認方法 |
|---|---|---|
| 1 | ⚠️★★★ **発火主体は IME ではなく *アプリ側の UIA プロバイダ*** —— 逐語「required to be raised by **Microsoft UI Automation elements supporting the TextEdit pattern**」。★ **「どの IME か」ではなく「被験者がどのアプリのどの入力欄を使うか」に依存する** | ★ Microsoft 自身が指示している —— 「Prior to using these events, client applications should use **Accessible Event Watcher** to verify」→ **`accevent.exe`（Windows SDK 同梱）で実測** |
| 2 | ⚠️ **0x8030 は 0x8029 と連続していない**（間に 0x802A-0x802F） | ★ 範囲を `0x8027..=0x8030` に広げてコールバックで弾くか、**フックをもう 1 本**張る |
| 3 | ⚠️★★★ **`WINEVENT_SKIPOWNPROCESS` との相互作用が未確認** —— ★ G1 の入力は **GSE 自身の画面**で行われる。⚠️ WebView2 は別プロセスで走る**はず**だが、**確認していない**。★ もし自プロセス扱いなら**イベントが 1 件も来ない** | ⚠️ **実機確認が必須**（★ これは**今回直した IME 修正が G1 で効くか**にも同じく掛かる） |

⚠️★ **UIA の TextEdit パターンは採らない** —— ★ `TextEditTextChanged` は payload に
逐語「**Data is the finalized string of the completed composition**」＝ **確定文字列が流れ込む**。
★ `ConversionTargetChanged` だけ使うなら WinEvent 版と等価で、**WinEvent の方が軽い**。

### 7.5 ★★★ macOS — **アプリを問わずに変換を知らせる公開の通知は見つかっていない**（⚠️ 2026-10-05 訂正）

> ⚠️★★★ **2026-10-05 訂正**（IME 論文のタスク `.steering/20260927-ime-observation-paper-eval-design/decisions.md` 判断 151・153
> 〔枝 `docs/ime-manuscript-outline`・この訂正の時点で main に未 merge・番号は merge の前に確かめ直す〕・
> 本訂正は `.steering/20261005-macos-ax-marked-text-correction/`）: 旧見出しは「**公開 API が存在しない**（★ 全数確認）」、
> 旧版の表の 1 行目は「Accessibility の全定数 … 135 個を全数確認し … *ゼロ*」だった。
> ⚠️ **数えたのは C（Carbon）の定数だけで、AppKit の定数を見ていなかった。** AppKit には変換中の範囲の属性と、
> 変換の開始・終了の通知がある（下の表の 2 行目）。→ ★ **言えるのは「アプリを問わずに変換を知らせる公開の通知は見つかっていない」まで**
> （候補窓はウィンドウ一覧のポーリングで一部見えるが、通知ではなく、変換前は出ない —— 下の表の「候補ウィンドウの検知」）。
> アプリが用意する経路はある（WebKit のソースは出す）。⚠️ **設計の結論（GSE は macOS では打鍵から推す）は変えていない**（変えるかは研究者）。

| 調査対象 | ★ 結果 |
|---|---|
| **Accessibility の C（Carbon）の定数** | ★ **属性 101 個 ＋ パラメータ付き 9 個 ＋ 通知 25 個 = 135 個に、marked text / composition / 入力方式の状態を表すものは無い**（2026-10-05 に Apple の文書の JSON で数え直して同じ数・該当なし） |
| ⚠️★★★ **Accessibility の AppKit の定数**（2026-10-05 に追加） | ★ **属性 131 個・パラメータ付き 18 個・通知 42 個**（各一覧の `init(rawValue:)` を除く）。★ **`NSAccessibility.Attribute` に `textInputMarkedRangeAttribute`（変換中の範囲）、`NSAccessibility.Notification` に `NSAccessibilityTextInputMarkingSessionBegan` / `…Ended`（変換の開始・終了）がある**（Objective-C の名は `NSAccessibilityTextInputMarkedRangeAttribute`・`NSAccessibilityTextInputMarkingSessionBeganNotification` / `…EndedNotification`。3 つとも各頁の JSON の `introducedAt` が macOS 10.6・説明の文は無い）。⚠️ 外から受ける側は C の `AXObserver`（対象のプロセスごとに作る・Accessibility の権限が要る）で、C の定数一覧に無いことは C から受けられないことを意味しない。出典: <https://developer.apple.com/documentation/appkit/nsaccessibility-swift.struct/attribute> と <https://developer.apple.com/documentation/appkit/nsaccessibility-swift.struct/notification>（IME 論文の枝で `docs/references.md` [V224]・[V225] に登録） |
| ★ **WebKit**（2026-10-05 に追加） | ★ **ソースは出す**（commit `1a5a134d14845e9bf54a67049a36a2585e62897c`・同 [V206]）。`Source/WebCore/accessibility/AXObjectCache.cpp` 3692〜3719 行の `onTextCompositionChange` が変換の開始・終了で `AXNotification::TextCompositionBegan` / `…Ended` を投げ（`HAVE(INLINE_PREDICTIONS)` の条件つき。`Source/WTF/wtf/PlatformHave.h` 1326〜1331 行が `PLATFORM(MAC)` で 1 にする・呼ぶのは `Source/WebCore/editing/Editor.cpp`）、`accessibility/mac/AXObjectCacheMac.mm` 361〜366 行がそれを上の 2 つの通知に写し、375 行が **userInfo なし（`nil`）** で投げる。`WebAccessibilityObjectWrapperMac.mm` 2290〜2295 行が変換中の範囲を `NSRange`（位置と長さ）で返す。⚠️ **実機で別のプロセスが受け取れるかは確かめていない**。⚠️ **終了の通知が確定・取消・フォーカスの喪失を区別するか、通知の遅れは未確認**。⚠️ **アプリの Accessibility の実装が出すものなので、出すかはアプリしだい**（AppKit の `NSTextView`・Chromium 系〔Chrome・Electron〕は未確認）。⚠️ **content-free は 3 つに分けて評価する**（2 巡目のレビューで直した）—— (i) **通知の中身**: 文字列を運ばない（WebKit は userInfo なし）。開始・終了の時刻だけなら通知で足りる。(ii) **範囲の属性**: 位置と長さで、文字数の量になる（`data-privacy` は文字数を原則持たない）。(iii) **受ける側の実装**: 通知は要素を渡すので、同じ要素から文字列を返す属性（`kAXValueAttribute`・`kAXStringForRangeParameterizedAttribute`・`kAXAttributedStringForRangeParameterizedAttribute`）も呼べてしまう。→ 採るなら（研究者の判断・新しいチャネルは別 ADR が先）、通知だけか範囲まで読むかを決め、文字列を返す属性を**呼ばない**と能力で書く必要がある |
| **`NSTextInputClient`** | ★ **対象アプリのビューが実装する in-process なプロトコル**。外部プロセスが問い合わせる公開 API は無い（★ 外へ知らせる経路は上の AppKit の Accessibility） |
| **Input Method Kit** | ⚠️ **Windows の TIP と構造が逆** —— macOS の input method は**独立プロセス**で `NSConnection` 経由。逐語「**The only client in OS X v10.5 is the Text Services Manager.**」→ ★ **「対象プロセスに入り込む」という迂回路すら存在しない** |
| **候補ウィンドウの検知** | ★ `kCGWindowLayer` / `kCGWindowOwnerPID` は **Screen Recording 権限なしで取れる**（⚠️ `kCGWindowName` だけが gated）。⚠️ **しかし (i) 通知が無くポーリング専用、(ii) 変換前（ローマ字入力中・下線のみ）は候補窓が出ない**＝ ★ **GSE が最も欲しい「かな入力中」を取り逃す** |
| `TISCopyCurrentKeyboardInputSource` | ★ 返るのは**入力ソース識別子（IME on/off）**まで。⚠️ composition ではない（★ 前提は正しかった）。⚠️ **Apple 公式ドキュメントは削除済みでヘッダのみ** |

### 7.6 ⚠️★★★ 非対称は **解消できない**。★ ただし「下に合わせる」のは誤り

> ⚠️ **2026-10-05 訂正（§7.5）**: ここで言う非対称は ★ **アプリを問わない通知**の非対称である
> （Windows は入力方式の窓のイベント 0x8027〜0x8029〔と cloak〕がある・macOS は調べた範囲に無い）。
> ⚠️ **アプリが用意する経路は両 OS にある** —— Windows は UIA の TextEdit パターンの変換対象の変化（§7.4 の 0x8030）、
> macOS は AppKit の Accessibility の変換中の範囲と開始・終了の通知（§7.5）。どちらもアプリしだいなので、下の結論は変わらない
> （⚠️ 下の本文の「0x8027-0x8030」のうち 0x8030 はアプリしだいの側で、結論を支えるのは 0x8027〜0x8029 と cloak）。

★ **理由**: Windows の 0x8027-0x8030 を捨てて macOS のヒューリスティックに揃えると、
⚠️ **取得可能な客観信号を自ら破棄して推定精度の上限を下げる**。
★ GSE が重視する品質特性は **「正確性（認知状態推定の精度、誤判定の最小化）」**（`agent-shared.md`）であり、正面から反する。

★ **正しい形（★ 設計提案。⚠️ 一次資料で決まる話ではないので ADR で裁く）**:

> ### ★★★ 「**推定器は下に揃え、較正と評価は上を使う**」

| 層 | ★ 方針 | ⚠️ なぜ |
|---|---|---|
| **推定器（HMM）の入力** | ★ **両 OS で同一に保つ**（＝この層だけ「下に合わせる」） | ⚠️ OS で割ると**放出行列が OS 依存**になり、**Replay-as-Truth の byte-equal 回帰が OS で割れて背骨が折れる**。★ `FeatSnapshot` スキーマも `HMM_VERSION` も割らない |
| **composition シグナル** | ★ **別レイヤの共変量 / 外部ラベル**として扱う（＝ここで「上を使う」） | ★ 推定器を変えないので**回帰に影響しない** |
| ★★★ **最も筋の良い使い方** | ⚠️ **Windows で得た客観ラベルに対し、macOS の keycode ヒューリスティックの感度 / 特異度を測る** | ★★★ **非対称を「macOS を良くする材料」に転化する** |
| **NDJSON スキーマ** | ★ **両 OS 共通にし、macOS では該当フィールドを `null`** | ⚠️ `emit_schema` の drift 検知と `gse-dataset` 整合を保つ。★ **OS ごとに別スキーマにしない** |

### 7.7 ★ 本セッションでの扱い — ⚠️ **0x8030 は *追加しない*。研究者判断へ送る**

| ★ 判断 | 理由 |
|---|---|
| ⚠️ **今回は追加しない** | ★ **新しい信号＝記録仕様の変更**（`capabilities`・ADR-013 D1）であり、今回直した IME 定数の「**意図した挙動の回復**」とは質が違う。⚠️ **かつ §7.4 の前提 3 件が未確認**（特に `accevent.exe` 実測と `SKIPOWNPROCESS`）。★ **未検証の信号を収集開始前に入れるのは、入れないより悪い** |
| ⚠️★★ **ただしトレードオフを隠さない** | ★ **いまは収集開始前**であり、⚠️ **追加するなら今しかない**（★ 収集が始まれば `preregistration.md §3.6` で回復不能）。→ ⚠️ **見送ると G1 は 0x8030 を持たないまま確定する。** ★ これは**研究者が決めるべき二択**である |
| ★ 前提を潰す手順は決まっている | ① `accevent.exe` で被験者の実使用アプリ（★ **G1 の入力画面を含む**）が 0x8030 を出すか実測 → ② `SKIPOWNPROCESS` と WebView2 のプロセス関係を実測 → ③ 出るなら範囲拡張 ＋ `capabilities` へ追加 |
