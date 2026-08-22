# ⚠️★★★ サーヴェイ中に見つかった既存計器の欠陥 — **2 件・いずれも一次資料で確認済み**

> 2026-08-22 / `.steering/20260821-workspace-behavior-triage/`
> ⚠️★★★ **2026-08-22 更新: 欠陥 1 は *修正済み*。**（★ 研究者指示「G1 自体でも影響が出るなら直しましょう」）
> ★ **確証標本 0/3 名 ＝ 収集開始前**だったので `preregistration.md §3.6` の回復不能問題は発生しない。
> ⚠️ **欠陥 2 は直していない**（★ G1 に影響しないため・R3 の課題）。詳細は本文末尾。
>
> ★ 発見経路: `survey-input-channels.md` のための subagent サーヴェイ。⚠️ **本タスクの目的外の副産物**であり、
> ★ **私自身が一次資料（`windows` crate 実体ソース）で再確認した**（`verify-before-claiming`）。

---

## 欠陥 1 ⚠️★★★ WinEvent の IME 定数が **別のイベントを指している**（Windows）

### ★ 確認した事実（⚠️ 推測ではない）

`src-tauri/src/input/hook_windows.rs:172-175`:

```rust
// IME WinEvent constants (winuser.h, Windows 8+)
const EVENT_OBJECT_IME_CHANGE: u32 = 0x8016;
const EVENT_OBJECT_IME_SHOW: u32 = 0x8017;
const EVENT_OBJECT_IME_HIDE: u32 = 0x8018;
```

★ `windows-0.58.0` の生成バインディング（`src/Windows/Win32/UI/WindowsAndMessaging/mod.rs`）を**直接 grep して確認**:

| repo の定数 | repo の値 | ★ **正しい値** | ⚠️ **repo の値が実際に指すもの** |
|---|---|---|---|
| `EVENT_OBJECT_IME_CHANGE` | `0x8016` | **`0x8029`**（32809・mod.rs:3691） | ⚠️ **`EVENT_SYSTEM_ARRANGMENTPREVIEW`**（32790・mod.rs:3713） |
| `EVENT_OBJECT_IME_SHOW` | `0x8017` | **`0x8027`**（32807・mod.rs:3693） | ⚠️ **`EVENT_OBJECT_CLOAKED`**（32791・mod.rs:3674） |
| `EVENT_OBJECT_IME_HIDE` | `0x8018` | **`0x8028`**（32808・mod.rs:3692） | ⚠️ **`EVENT_OBJECT_UNCLOAKED`**（32792・mod.rs:3708） |

→ ★ `hook_windows.rs:315-322` の
`SetWinEventHook(EVENT_OBJECT_IME_CHANGE, EVENT_OBJECT_IME_HIDE, ...)` ＝ **`(0x8016, 0x8018)`** は、
⚠️★★★ **IME ではなく「アレンジプレビュー / ウィンドウのクローク・アンクローク」を購読している。**

### ⚠️★★★ 影響範囲（★ 書き手を全部数えて特定した）

`grep -rn "IME_OPEN.store\|IME_ACTIVE.store" src-tauri/src/input/*.rs` の結果:

| Atomic | 書き手 | ⚠️ 影響 |
|---|---|---|
| **`IME_OPEN`** | ① WinEvent コールバック（⚠️ 誤定数）/ ② `ime_open_after_release(vk_code)`（★ **VK_DBE_HIRAGANA の key-up**・正常）/ ③ **`ime_windows.rs` のポーリング**（`current_state`・正常） | ⚠️ **誤った書き手が 1 つ混ざるが、正常な書き手が 2 つある** → ★ **全損ではない。ただしウィンドウのクローク時に偽の `true` が入る** |
| ⚠️★★★ **`IME_ACTIVE`**（変換中フラグ） | ⚠️★★★ **`true` を書くのは WinEvent コールバックの 1 か所だけ**（`hook_windows.rs:209`）。`ime_windows.rs` は **`false` しか書かない** | ⚠️★★★ **`IME_ACTIVE = true` が「実際の IME 変換」で立つ経路が存在しない。** 代わりに**ウィンドウのクローク／アンクローク／アレンジプレビュー**で立つ |
| `IME_COMPOSITION_START_MS` / `IME_CANDIDATE_NAV_COUNT` | 同コールバック（`:216-223`） | ⚠️ **変換セッションの開始時刻が、IME と無関係なイベントで初期化される** |

★ **`EVENT_OBJECT_CLOAKED` / `UNCLOAKED` が発火する場面**: 仮想デスクトップの切替、ウィンドウの最小化、
UWP アプリのサスペンド等。⚠️ **日常操作で普通に起きる。**

### ⚠️ 影響しないと確認できたもの

| 何 | ★ なぜ影響しないか |
|---|---|
| **ADR-012 Stage 0（`C_write` / θ）** | ★ 入力は **`hook_health` / `starved_ms`**（`liveness.rs` 由来）であり、IME を一切使わない |
| **`keys` / `bs_keys`（Tier 0）** | ★ `is_typing_key` 経由の打鍵カウント。IME 非依存 |
| **`paste` 検知** | ★ VK+`GetAsyncKeyState` 経由（⚠️ ただし**欠陥 2** が別途かかる） |

### ⚠️ 影響しうるもの（★ 断定しない。実ログの照合が要る）

- `ime_state` / `ime_shadow` 行、`ime_dwell_med`
- ⚠️ **β の選択**（`ime_open` で `β_writing` / `β_writing_latin` を切り替える・ADR-006 下位決定 #2）
- ⚠️ BS ペナルティ gate（`!ime_open` 紐付け・ADR-006 D-3）

⚠️★★★ **「だから G1 のデータが壊れている」とは断定しない。** ★ `IME_OPEN` には正常な書き手が 2 つあり、
**実効の劣化度は実ログでしか分からない**。⚠️ ただし **`IME_ACTIVE` については「正しく立つ経路が無い」ことが
コード上確定している**。

### ⚠️ 修正が単純でない理由（★ 定数だけ直すと壊れる）

★ 正しい値では **`IME_CHANGE(0x8029) > IME_HIDE(0x8028)`** となり、
`SetWinEventHook(eventMin=IME_CHANGE, eventMax=IME_HIDE)` は **空レンジ**になる。
→ ★ **`SetWinEventHook(EVENT_OBJECT_IME_SHOW /*0x8027*/, EVENT_OBJECT_IME_CHANGE /*0x8029*/, ...)` へ
min/max ごと直す**必要がある。

★ **再発防止**: 自前 `const` を消して
`windows::Win32::UI::WindowsAndMessaging::{EVENT_OBJECT_IME_SHOW, EVENT_OBJECT_IME_HIDE, EVENT_OBJECT_IME_CHANGE}`
を import する（★ 3 つとも `windows` 0.58 に存在することを確認済み）。
⚠️ **feature 追加は不要**（`Win32_UI_WindowsAndMessaging` は既に有効）。

---

## 欠陥 2 ⚠️★★ フックコールバック内の `GetAsyncKeyState` を Microsoft が明示的に否定している（Windows）

### ★ 一次資料

`hook_windows.rs:530-535` は Ctrl+V 検出のためコールバック内で `GetAsyncKeyState(0x11)` を呼ぶ。
⚠️ [LowLevelKeyboardProc] の Note 逐語:

> When this callback function is called in response to a change in the state of a key, the callback function is called
> before the asynchronous state of the key is updated. Consequently, **the asynchronous state of the key cannot be
> determined by calling GetAsyncKeyState from within the callback function.**

さらに [GetAsyncKeyState] は戻り値 0（＝「押されていない」と区別が付かない）になる条件を挙げている:

> - The current desktop is not the active desktop.
> - **UI Privilege Isolation (UIPI) prevents the calling thread from accessing the foreground thread.**

### ⚠️ 実害

★ **昇格プロセス（管理者権限の VSCode / ターミナル等）が前面にあるとき、GSE が非昇格なら
`GetAsyncKeyState` は 0 を返し、Ctrl+V が「ペーストでない」と静かに誤分類される。**
⚠️ **ログには何も残らない。**

★ `external_paste_chars` は **`(b) 自力解決率**（`docs/preregistration-v0.3.md` / v0.4 §4.2）の構成要素なので、
⚠️ **欠測が系統的（昇格アプリ使用者に偏る）**である点が問題になる。

⚠️★ **既存コメント（`:524-528`）は「ブロッキングしないから hook-constraints に抵触しない」と書いており、
それ自体は正しい。** ★ 見落としているのは**別の理由**（doc の否定と UIPI）である。

### ★ 代替（★ 一次資料で裏付くもの）

| 手段 | 根拠 |
|---|---|
| ★ **フック自身のイベント列で修飾キーを追跡** | WH_KEYBOARD_LL は VK_CONTROL(0x11)/VK_LCONTROL(0xA2)/VK_RCONTROL(0xA3) の down/up を必ず見る（★ 自分がグローバルフックだから） |
| ★ Alt に限れば **`KBDLLHOOKSTRUCT.flags & LLKHF_ALTDOWN`(0x20)** | ★ **構造体に同梱**。API 呼び出しゼロ |
| ⚠️ `GetKeyboardState` は**代替にならない** | [GetKeyboardState] Remarks: 状態は「スレッドが**自分のメッセージキューからキーボードメッセージを取り出したとき**」にしか変わらない。★ GSE のフックスレッドは取り出さない → **永久に初期状態** |

⚠️ **既知の弱点**（★ 既存コメント `:525-527` が正しく指摘している）: フォーカスがプロセスを跨ぐ瞬間に
up を取りこぼし、Atomic が「押しっぱなし」で固着しうる。
→ ★ **緩和案**: **`EVENT_SYSTEM_FOREGROUND`(0x0003) の WinEvent で修飾キー Atomic を全クリアする**。
★ WinEvent は既に張っているので追加コストはほぼゼロで、`GetAsyncKeyState` の UIPI 失敗経路も踏まない。
⚠️ **これは欠陥 1 の修正と同じ箇所を触るので、まとめて直すのが自然である。**

---

## ★★★ 欠陥 1 は **修正した**（2026-08-22・研究者指示）

> **研究者指示（逐語）**: 「既存計器の結果に関してだが、**G1自体でも影響が出るなら直しましょう**。」

### ★ 「G1 に影響が出るか」の判定 — ⚠️ **出る**（★ 連鎖を最後まで追った）

```
WinEvent(誤定数) → IME_OPEN.store(true)        hook_windows.rs:210
  → lib.rs:2681 IME_OPEN.load()
  → loop_step.rs:348 engine.update(&features, ime_open)
  → head.latent_axes(features, ime_open)        engine.rs:381
  → raw_x / raw_y → obs → p_flow / p_inc / p_stuck
```

⚠️★★★ **さらに悪い性質が 2 つある**（★ 本セッションで実測）:

| # | 性質 | 出所 |
|---|---|---|
| 1 | ⚠️★★★ **`IME_OPEN` は片方向ラッチ**。cloak(0x8017) で `true` になるが、**uncloak(0x8018) の枝は `IME_ACTIVE` しか落とさず `IME_OPEN` を戻さない** | `hook_windows.rs:238-249` |
| 2 | ⚠️★★★ **ポーリングが訂正できない**。IMM 経路は **`last_state != current_state` のときしか `store` しない**ので、IMM の読みが変わらない限り誤った `IME_OPEN` は上書きされない。⚠️ fallback 経路に至っては **`IME_OPEN` を読み戻して log に流すだけ** | `ime_windows.rs:246-251` / `:261-268` |

→ ⚠️ 背景の UWP サスペンド等で一度 latch すると、**英数キーを押すまで `β_writing` に固定**され、
**BS ペナルティ gate（`!ime_open`）も無効化されたまま**になる。
★ **ADR-006 下位決定 #2（`β_writing_latin`）が機能しない。**

### ★★★ タイミング — **収集開始前だった**（★ これが決め手）

| 事実 | 出所 |
|---|---|
| ★ **確証標本 0/3 名** | `experiments/20260801-controlled-friction-task/data.md:3-5` |
| ★ 直前タスクが「**収集開始前**の実装を閉じ」を目的にしていた | `.steering/20260821-precollection-close-and-x-axis/requirement.md:1,17` |

→ ★★★ **`preregistration.md §3.6`（ブロックの事後除外の禁止）による回復不能問題は発生しない。**
⚠️ **収集が始まったら直せなくなる。今が唯一のタイミングだった。**

### ★ 修正内容（`src-tauri/src/input/hook_windows.rs`）

| # | 変更 |
|---|---|
| 1 | ★ **自前 `const` を削除**し、`windows::Win32::UI::WindowsAndMessaging::{EVENT_OBJECT_IME_SHOW, EVENT_OBJECT_IME_HIDE, EVENT_OBJECT_IME_CHANGE}` を **import**（★ **再発防止** —— 手書き値を置かない） |
| 2 | ⚠️★★★ `SetWinEventHook` の範囲を **`(IME_SHOW 0x8027, IME_CHANGE 0x8029)`** へ。★ 旧コードの `(CHANGE, HIDE)` をそのまま正しい値へ差し替えると **`0x8029 > 0x8028` の空レンジ**になり **1 件も届かなくなる** |
| 3 | ★ **回帰テスト 2 本**を追加（定数の値を固定 ＋ 範囲が 3 つとも覆うことを固定） |

⚠️ **`win_event_callback` の中身は 1 行も変えていない**（`hook-constraints` Win-1: コールバック内は Atomic ＋ `try_send` のみ —— ★ 追加操作ゼロ）。

### ★ 検証結果（★ 実測・推測なし）

| 検査 | 結果 |
|---|---|
| `cargo check --lib` | ✅ **exit 0** |
| `cargo test --workspace` | ✅ **exit 0**（lib 440 ＋ replay 29 ＋ integration 1 = **470 passed**。★ 新規 2 本を含む） |
| ★★★ **ゴールデン** | ✅ **`OK: 15 snapshots match` — byte-equal**。⚠️ **入力層の修正なのでリプレイ出力は変わらない**という設計上の予測どおり |
| `HMM_VERSION` | ✅ **`0.4.0` のまま**（★ bump 不要） |
| `cargo fmt --check` | ✅ **exit 0** |
| ⚠️ `cargo clippy -- -D warnings` | ⚠️ 29 件（⚠️ **すべて pre-existing**）。★ `hook_windows.rs:152` の 1 件は **`classify_ime_nav_key`＝ 私の diff に含まれない**（`git diff \| grep` で確認）。★ **CI は clippy を実行していない**（`.github/workflows/ci.yml` に記述なし） |

### ⚠️ 欠陥 2（`GetAsyncKeyState`）は **直していない**（★ 意図的）

★ **G1 に影響しないから**である: G1 は **GSE 自身の入力画面**（**非昇格**）で行われるので、
⚠️ **UIPI（呼び出しスレッドが前面スレッドへアクセスできない）が発生しない**。
→ ★ 欠陥 2 は **R3（実業務・昇格アプリ混在）の課題**として残す。

⚠️★ **ADR-014 D4 の実装時に、`EVENT_SYSTEM_FOREGROUND` の WinEvent で修飾キー Atomic を全クリアする案と
まとめて直すのが自然である**（★ 同じ箇所を触る）。

### ⚠️★★★ 修正後に残る **未確認事項 1 件**（★ TSF 調査の副産物・2026-08-22）

> ⚠️ **これは「定数を直せば G1 で効く」という前提そのものに掛かる。**

★ `SetWinEventHook` には **`WINEVENT_SKIPOWNPROCESS`** が付いている（`hook_windows.rs:322`）。
⚠️ **G1 の入力は GSE 自身の画面で行われる。**

| 分岐 | ⚠️ 帰結 |
|---|---|
| ★ WebView2 が**別プロセス**で走る（★ そのはず） | ★ `SKIPOWNPROCESS` に当たらず、**修正は G1 で効く** |
| ⚠️ 自プロセス扱いになる | ⚠️★★★ **IME イベントが 1 件も来ない** —— ★ 定数を直しても `IME_ACTIVE` は立たない |

→ ⚠️★★★ **実機確認が必須**（★ `accevent.exe`（Windows SDK 同梱）または実起動ログで
`ime_state` の `active` が日本語変換中に `true` になるかを見る）。
★ **収集開始前に確認すること。**

⚠️★ **同じ確認が `EVENT_OBJECT_TEXTEDIT_CONVERSIONTARGETCHANGED`(0x8030) の採否にも掛かる**
（`survey-input-channels.md §7.4` 前提 3）。→ ★ **1 回の実機確認で 2 つの問いが同時に閉じる。**

---

### ⚠️★★ 研究者への申し送り — **配布のタイミング**

★ 修正は**被験者が実際に走らせるビルドに入らないと意味が無い**。
⚠️ 現在 `tauri.conf.json` は **`0.1.27`**、最新タグも **`v0.1.27`**、Mac 側が **v0.1.28** を準備中。
→ ★ **この修正を v0.1.28 に載せるか、載せ損ねたら v0.1.29 を出すかの判断が要る。**
⚠️ **収集開始前に配布が完了している必要がある。**

---

## ★ 本セッションでの扱い（⚠️ 欠陥 2 は実装しない）

| # | 事項 | ★ 扱い |
|---|---|---|
| 1 | ⚠️★★★ **計器は 2026-08-21 に凍結。G1 は収集中** | ★ **修正は研究者判断**。⚠️ `preregistration.md §3.6` がブロックの事後除外を禁じているため、**収集開始後の記録仕様変更は回復不能**（ADR-012 D7 の理由と同じ構造） |
| 2 | ★ **ADR-013 リブートの先例がある** | ⚠️ 2026-08-19 に G1 を**リブート**し、**停止期間を ADR-013 の実装窓にした**。★ **同型の判断が可能**（⚠️ ただしコストは研究者が負う） |
| 3 | ⚠️ **Stage 0 は影響を受けない** | ★ `hook_health` / `starved_ms` は IME 非依存 → **Stage 0 は予定どおり進められる** |
| 4 | ★ **実ログでの確認方法** | ⚠️ G1 ログの `ime_state` / `ime_shadow` 行を、被験者の実際の日本語入力と突き合わせる。★ **`IME_ACTIVE` は「正しく立つ経路が無い」ことがコード上確定しているので、`ime_shadow` が 0 行 or 異常なら本欠陥が原因である可能性が高い** |

⚠️★★ **`personalization §5.2` に既に記録されている症状との関係は *断定しない***
（「`ime_dwell_med` … P012・P014 は `ime_shadow` 自体がゼロ＝被験者の 4 割で欠測」）。
★ 被験者の OS が Windows か macOS か、本欠陥が原因かは**本セッションでは確認していない**。

---

## Sources（★ 一次資料）

- ローカル crate 実体: `~/.cargo/registry/src/*/windows-0.58.0/src/Windows/Win32/UI/WindowsAndMessaging/mod.rs`
  （3674 / 3691 / 3692 / 3693 / 3706 / 3708 / 3713 行を直接 grep）
- ローカル実装: `src-tauri/src/input/hook_windows.rs`（172-175 / 198-223 / 315-322 / 505-560 行）/ `ime_windows.rs`
- [LowLevelKeyboardProc callback function](https://learn.microsoft.com/en-us/windows/win32/winmsg/lowlevelkeyboardproc)
- [GetAsyncKeyState (winuser.h)](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-getasynckeystate)
- [GetKeyboardState (winuser.h)](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-getkeyboardstate)
- [Event Constants (Winuser.h)](https://learn.microsoft.com/en-us/windows/win32/winauto/event-constants)
