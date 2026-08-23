# 次セッション開始プロンプト（**macOS 実機**）— O1 計器の mac 側実装と実機確認

> ★ このファイルの「===」以下をコピペして開始する。
> ⚠️★★★ **本セッションは macOS の実機でしか実行できない。** Windows では 1 行も検証できない。
> ★ **実装セッションである。**⚠️ `/start-task` を**必ず先に**起動する（CLAUDE.md 行動規範 1）。
> ★ モデル: **設計判断は Opus / 実装は Sonnet**。
> - **前セッション（Windows 実装）**: `.steering/20260823-o1-instrument-r3a/`
> - **その前（設計）**: `.steering/20260823-o1-nonkeystroke-gap-and-prereg/`

---

===

## §0 ⚠️★★★ 最初に固定すること

### 0-1. ⚠️★★★ **実装より先に「同時稼働の実機確認」をやる。落ちたら実装しない**

★ **ADR-016 D9 の前提 1 が macOS だけ未了である**（Windows は 2026-08-23 に実測で閉じた）。
⚠️ 逐語:「**どれか欠けたら重ねない**」「⚠️ **前提 1 が落ちたら `§9.5` の案 α（同一被験者・別時点）へ降りる**（★ 降りたら降りたことを記録する）」。

→ ★★★ **順序は T1（実機確認）→ T2（実装）である。⚠️ 逆にしない。**
★ 理由: **確認で落ちれば設計（コホートを完全に重ねる）ごと作り直しになり、実装が無駄になる。**

### 0-2. ⚠️ **1 バイトも変えないもの**

- ⚠️★★★ **`HMM_VERSION`** —— ★ **着手時に `grep -n 'HMM_VERSION: &str' src-tauri/src/analysis/engine.rs` で実測して控える**
  （⚠️ **docs の値を信じない**。2026-08-23 時点の現行値は `0.5.0`）
- ⚠️★★★ **`analysis/key_gate.rs` の `is_feature_key`** —— ★ **特徴量へ流す集合**の単一情報源。
  ⚠️ **1 ビットでも変えたら `HMM_VERSION` bump の話になる**
- ⚠️★★★ **`docs/architecture/workspace-behavior-observation.md §2.1`（段 1）** —— **凍結済み**。候補チャネルを 1 本も足さない
- ⚠️ **ADR-009 D2 の 4 択と役割カテゴリの順序** / **G1 の事前登録** / **ADR-012 D7 制約 4**
- ⚠️★★★ **G1 被験者へ新ビルドを配らない**（★ `scripts/make-distribution.sh` / `make-common-app-zip.sh` を走らせない）

### 0-3. ⚠️★★★ **macOS でだけ効く「触ってはいけない場所」**

★ Windows 側の実装で**塞がっていることが分かった経路**である（`.steering/20260823-o1-instrument-r3a/decisions.md` **D-A**）:

| ⚠️ 触ってはいけない | ★ なぜ |
|---|---|
| **`hook_macos.rs` の tap の event mask に `FlagsChanged` を足すこと** | ⚠️★★★ `handle_event` は**送信の前**に `LAST_KEY_MS` を更新し IME 状態機械を触る（`hook_macos.rs:360` 付近）。★ `LAST_KEY_MS` は `liveness` → `starved_ms` → **沈黙検出**へ流れる ＝ **特徴量経路に触れる** |
| **`macos_vk_to_vk` にテンキーの写像を足すこと** | ⚠️★★★ 写像先 `0x60..=0x6F` は **`is_feature_key` の中**である。★ 素通し（既定 `other => other as u32`）にしても `kVK_ANSI_Keypad0`(0x52) が **`VK_R`（英字）** に化けて**やはり中**に入る。→ ★ **どちらの道も特徴量が変わる** |
| **`is_observed_key`（`hook_macos.rs:171`）の集合を広げること** | ★ 2026-08-23 に **Esc / 矢印 / F1–F12 だけ**を足して確定済み。⚠️ **修飾キーとテンキーは意図的に入れていない**（上記 2 行）。★ 対のテストが 4 本張ってある |

⚠️ **これらを「未実装だから足そう」と読まないこと。★ 決めて、テストで固定した状態である。**

### 0-4. ⚠️ 禁止語規約（形成的トラック）

★ 利得を主張する語を使わない。⚠️ 検査は
`grep -nE '効果があ|精度が上が|有効性' <本タスクの成果物>` で行う（★ ヒット 0 が条件）。

---

## §1 ★ ここまでの到達点（★ 2026-08-23 / Windows 実機で実測済み）

| # | 何 | Windows | macOS |
|---|---|---|---|
| 1 | **ゲート分割**（`is_observed_key` / `is_feature_key`） | ✅ 実装・テスト済み | ✅ **実装済み**（Esc / 矢印 / F キーのみ） |
| 2 | **区間指定削除 UI / 一時停止 / 稼働中インジケータ** | ✅ 実装済み（**OS 非依存**） | ✅ **そのまま動く**（⚠️ 実機確認は未） |
| 3 | **L-c フォーカス遷移** | ✅ 実装・実機で設置確認 | ❌ **未実装**（スタブ） |
| 4 | **L-b ポインタ（1 秒ビン）** | ✅ 実装・実機で設置確認 | ❌ **未実装**（スタブ） |
| 5 | **`secure_input`** | — （★ Windows に該当 API 無し） | ❌ **未実装**（★ 行種・schema・writer は**用意済み**） |
| 6 | **キーボードレイアウト識別子** | ✅ `meta` に `"keyboard_layout":"00000411"` を実測 | ❌ **未実装** |
| 7 | **`capabilities` の自己刻印** | ✅ `config_gated` に `focus_transition`/`pointer_bin` | ✅ **「計器が無い」と正しく自己申告中** |
| 8 | **ドロップの実測** | ✅ **0 件**（≈279 events/s を 15 秒） | ❌ 未 |
| 9 | **同時稼働の実機確認**（ADR-016 D9 前提 1） | ✅ **閉じた**（`hook_calls` 1630/1630） | ❌ ★★★ **未 ← 本セッションの最優先** |

★ **OS 非依存の器はすべて出来ている。** ⚠️ mac に無いのは **`input/observe_macos.rs` の中身だけ**である。

---

## §2 ★★★ 本セッションでやること（★ この順で）

### T0. ★ `/start-task` で `.steering/[YYYYMMDD]-o1-macos-instrument/` を作る

- [ ] ⚠️ **着手時の `HMM_VERSION` を grep で実測して控える**

### T1. ★★★ **同時稼働の実機確認**（⚠️ **実装より先**・ADR-016 D9 前提 1）

> ★ Windows 版の probe と証拠: `.steering/20260823-o1-nonkeystroke-gap-and-prereg/probe-concurrent-hooks.md`

- [ ] ⚠️★★★ **`CGEventTap` を 2 プロセスで同時に張れるか**を実機で確かめる
      （★ 一方は GSE 本体、もう一方は使い捨て probe）
- [ ] ★ **使い捨て probe は scratchpad に作る。⚠️ repo に置かない**（ADR-012 D7 の作法）
- [ ] ⚠️★★★ **probe は「数だけ数える計器」にする** —— ★ Windows 版と同じ作法:
      **VK を読まない / 文字を触らない / 座標を読まない**。★ 数えるのは
      `tap 設置の成否` / `callback 到達数` / `KeyDown 数` の 3 つだけ
- [ ] ★ **合成入力と実入力の両方**で回す（⚠️ Windows 版は実入力ラウンドが `signal_absent` で空振りした）
- [ ] ⚠️★★ **`ScrollWheel` / `MouseMoved` の別 tap も同時に張れるか**を併せて見る
      （★ T2 の L-b がこれに依存する）
- **判定**
  - ✅ **両プロセスの計数が一致** → ★ T2 へ進む
  - ❌ **落ちた** → ⚠️★★★ **T2 をやらない。** `§9.5` の**案 α（同一被験者・別時点）へ降り、
    降りたことを ADR-016 と `.steering/` に記録して終える**

### T2. ★★★ **`observe_macos.rs` の実装**（★ T1 が ✅ のときだけ）

> ★ 置き場所は既にある: `src-tauri/src/input/observe_macos.rs`（**現在は明示的なスタブ**）。
> ★ 実装すべき関数と定数は**すべて宣言済み**で、⚠️ **中身を入れるだけ**である。

- [ ] **`keyboard_layout_id()`** —— ★ **既存の FFI パターンをほぼそのまま使える**
      （`src-tauri/src/input/ime_macos.rs:130-195`: `#[link(name = "Carbon")]` +
      `TISGetInputSourceProperty(.., kTISPropertyInputSourceID)` + `dispatch_sync_f` でメインキューへ）
      - ⚠️★★★ **ADR-014 D4 が指定しているのは `TISCopyCurrentKeyboardLayoutInputSource`** であり、
        既存コードの `TISCopyCurrentKeyboardInputSource`（＝ **入力ソース = IME**）とは**別 API** である。
        ★ 欲しいのは**物理配列**（`com.apple.keylayout.US` 等）なので **Layout 版**を使う
      - ⚠️★★★ **`UCKeyTranslate` を呼ばない**（★ 呼んだ瞬間に**入力文字がプロセス内に出現する**）
      - ⚠️ `dispatch_sync_f` は**メインスレッドから呼ばない**（デッドロック・技術的制約 5）
- [ ] **`secure_input_enabled()`** —— `IsSecureEventInputEnabled()`（Carbon・`#[link]` 1 行）
      - ★ 1Hz で確認し、**変化したときだけ** `LogEntry::SecureInput { timestamp, on }` を送る
      - ⚠️ 送出元を作ったら **`capabilities.rs` の 2 か所を必ず直す**（下記 T3）
- [ ] **`FOCUS_AVAILABLE` / L-c フォーカス遷移** ——
      `NSWorkspace.didActivateApplicationNotification`（★ **TCC 不要**）
      - ⚠️★★★ **通知オブジェクトから `bundleIdentifier` を読まない。** ★ 送るのは
        **`u64` の時刻 1 個だけ**（`FOCUS_TX` の型がそれしか運べない形にしてある）
      - ⚠️ ウィンドウ通し番号・distinct 数も**擬似識別子**なので数えない
- [ ] **`POINTER_AVAILABLE` / L-b ポインタ** —— ⚠️★★★ **既存 tap とは *別 tap*** に
      `MouseMoved` / `*Dragged` / `ScrollWheel`
      - ⚠️★★★ **既存の打鍵 tap に相乗りさせない**（★ 相乗りすると**打鍵観測を巻き込んで失効する**）
      - ★ 量子化は **`analysis/pointer_bin.rs` をそのまま使う**（`PointerAccum::add_move` /
        `add_button_press` / `add_wheel` → `close(now_ms)`）。⚠️ **自前で数を作らない**
      - ★ **1 秒固定ビン・ゼロ抑制**（`PointerBin::is_empty()` が true なら送らない）
      - ⚠️ **座標を取らない** —— ★ `CGEvent` から取るのは
        `kCGMouseEventDeltaX` / `kCGMouseEventDeltaY`（**相対**）であり、
        ⚠️ `CGEventGetLocation` は**呼ばない**
- [ ] ⚠️ **`CGEventTapIsEnabled` の定期確認**（★ O1 は数日〜数週間走る。
      `sleep/wake` / `lock/unlock` で**無通知失効する実例がある**。⚠️ **tap が 2 系統になると 2 倍起きうる**）

### T3. ★★★ **宣言と実装を一致させる**（⚠️ 忘れると「過大申告」か「過小申告」になる）

- [ ] `capabilities.rs` の **`declaration_partitions_known_line_types`** の `emitterless` から
      **実装した行種を外す**（★ 現在は macOS 側に
      `["ime_shadow", "secure_input", "focus_transition", "pointer_bin"]` が並んでいる）
- [ ] `config_gated()` の **`SECURE_INPUT_AVAILABLE` を見て `secure_input` を push** する
      （★ コメントに「実装したらここで push すること」と書いてある）
- [ ] ⚠️★★★ **`cargo test` が「宣言と `#[cfg]` の食い違い」を機械的に落とす**ので、
      ★ **テストが赤いまま進めない**

### T4. ⚠️ **両 OS に対のテスト**（★ 既に 4 本ある。壊さない・足す）

- [ ] ★ 既存（`hook_macos.rs`）: `observed_key_covers_the_frozen_typing_set` /
      `escape_arrows_and_function_keys_are_observed_but_never_features` /
      `numpad_is_not_observed_on_macos` / `modifiers_are_not_observed_on_macos`
- [ ] ★ 足すもの: **ポインタの変換が座標を持たないこと** /
      **`secure_input` の遷移でしか行が出ないこと**（★ 純関数に落として `cargo test` で固定する）
- ⚠️ **フック本体は実機でしか動かない。** ★ テストするのは**判断だけ**である（既存の作法）

### T5. ★ 実機の総合確認

- [ ] **ドロップの実測**（★ Windows は 0 件）—— `EVENTS_DROPPED` / `hook_health` の `dropped_delta`
- [ ] ⚠️★★★ **`pointer_bin` / `focus_transition` の行が実際に出ること**
      （★ Windows 側では**端末がアイドルで確認できなかった**残件。⚠️ **マウスを動かし、
      アプリを切り替えながら**走らせること）
      ```bash
      cd src-tauri
      GSE_DATASET=/tmp/gse-o1-check cargo run --bin gse-next &
      # ★ 20 秒ほどマウスを動かし、別アプリへ切り替えて戻る
      grep -c pointer_bin      /tmp/gse-o1-check/raw/*/*.ndjson
      grep -c focus_transition /tmp/gse-o1-check/raw/*/*.ndjson
      ```
- [ ] **`meta` に `keyboard_layout` が載ること**
      （⚠️★★★ **ロガーを起こす *前* に解決しないと間に合わない** —— ★ Windows で実際に踏んだ。
      `lib.rs` の `log_channel.start(..)` の**直前**に置いてある）
- [ ] **区間指定削除 UI / 一時停止 / インジケータ**が mac で動くこと（★ OS 非依存だが未確認）
- [ ] ⚠️ **長時間の安定性**（★ 可能なら数時間走らせて tap の失効を見る）

---

## §3 ★ 読むもの（★ ゼロから考えない）

| 何 | なぜ |
|---|---|
| `.steering/20260823-o1-instrument-r3a/decisions.md` | ★ **D-A（mac の非対称）/ D-F（なぜスタブにしたか）/ D-K（Windows で何を実測したか）/ D-M（絶対座標モードの落とし穴）** |
| `src-tauri/src/input/observe_windows.rs` | ★ **対になる実装の全体像**（★ 1 本の専用スレッドで WinEvent + Raw Input + 1 秒ビン） |
| `src-tauri/src/input/observe_macos.rs` | ★ 冒頭に **必要な API と理由が調査済みの形で列挙**してある |
| `src-tauri/src/input/ime_macos.rs:130-195` | ★ **Carbon FFI + `dispatch_sync_f` の既存パターン**（★ そのまま真似できる） |
| `docs/adr/ADR-016-…md` **D8 / D9** | ★ ゲート分割と**前提 3 件** |
| `docs/adr/ADR-014-…md` **D4 / D4b / 判断 4 の追補** | ★ 段 1 の凍結表・禁止表・**配布境界** |
| `.steering/20260823-o1-nonkeystroke-gap-and-prereg/probe-concurrent-hooks.md` | ★ **Windows 版 probe の作法**（⚠️ mac 版もこの水準で） |
| `.steering/20260821-workspace-behavior-triage/survey-input-channels.md` | ★ 取得手段の実測サーヴェイ（**mac 側の一次資料**） |
| Skill: `hook-constraints` / `rust-standards` / `architecture-rules` / `data-privacy` | ⚠️ **手を動かす前に Read する**（★ `data-privacy` は **ルール 6 / 7 が 2026-08-23 に増えている**） |

---

## §4 ⚠️ 落とし穴（★ mac 固有・実測で分かっているもの）

1. ⚠️★★★ **`FlagsChanged` を tap の mask に足すと特徴量経路に触れる**（§0-3）
2. ⚠️★★★ **`macos_vk_to_vk` の既定は素通し**（`other => other as u32`）——
   ★ **mac の keycode が Windows VK として解釈される**。新しい keycode を観測集合に入れるなら
   **必ず明示写像を足し、写像先が `is_feature_key` の外であることをテストで確かめる**
3. ⚠️★★ **`dispatch_sync_f` をメインスレッドから呼ぶとデッドロックする**（技術的制約 5）
4. ⚠️★★ **TCC 権限のフォールバックチェーン**（Input Monitoring → Accessibility）を壊さない（制約 6）
5. ⚠️★★★ **`CGEventTap` は無通知で失効する**（`sleep/wake` / `lock/unlock`）。
   ★ 既存 tap は `TapDisabledByTimeout` / `TapDisabledByUserInput` を**作り直さず即再有効化**している。
   ⚠️ **新しい tap にも同じ手当てが要る**
6. ⚠️★ **`Cargo.toml` は repo 直下に無い**（`src-tauri/` にある）。`cd src-tauri` するか `--manifest-path`
7. ⚠️★ **`| tail` にパイプすると `$?` が tail のものになる** → リダイレクトしてから `echo $?`
8. ⚠️★★ **`.rs` への Write は guard が `println!` を文字列一致で弾く**（★ **コメント内でも弾かれる**）
9. ⚠️★★ **`#[cfg]` の無いテストは相手側の OS でも走る** —— ★ `hook_windows.rs` は
   **macOS では 1 行もコンパイルされない**ので、⚠️ **mac で `cargo test` が緑でも Windows 側は保証されない**
10. ⚠️★★★ **`anyhow` はこの repo の依存に無い**（★ `docs/agent-shared.md` の記述と食い違う）。
    ★ `Result<_, String>` / `tauri::Result` を使う（`overlay_panel.rs` に明記）

---

## §5 ⚠️ 本セッションで扱わないもの

- ⚠️ **推論への配線（段 3）** —— ★ **ADR-011 D4「読む実装は G1 判定後」**は不変。
  ★ 現状 **新チャネルを読む本番コードは 0 件**（2026-08-23 実測）であり、**その状態を保つ**
- ⚠️ **役割カテゴリ** —— ADR-009 D2 の順序（「G2 が落ちてから」）
- ⚠️ **R3-b（タスク種別ごと）/ 宣言 UI** —— ★ 研究者判断 4 待ち
- ⚠️ **`is_feature_key` の変更**（★ 変えるなら別 ADR ＋ `HMM_VERSION` bump の議論）
- ⚠️ **6 段階 ablation の事前宣言** / **スマホ表現チャネル / Physical Anchor**

---

## §6 ★ 完了報告に必ず書くこと

- [ ] ★ **T1（同時稼働の実機確認）を実装より先にやったこと**と、**その結果**
      （⚠️ 落ちたなら **案 α へ降りたこと**を明記する）
- [ ] ⚠️ **`HMM_VERSION` が着手前の値のままであること**（★ 着手時に grep で実測して控える）
- [ ] ⚠️ **`is_feature_key` を 1 ビットも変えていないこと**
- [ ] ⚠️ **ゴールデンが byte-equal であること**（★ 6 本。⚠️ `cd src-tauri` して回す）
- [ ] ⚠️ **`check_schema_parity.py` が緑であること**
- [ ] ⚠️ **`capabilities` の宣言と実装が一致していること**（★ `cargo test` が機械的に見る）
- [ ] ⚠️ **段 1 にチャネルを 1 本も足していないこと**
- [ ] ⚠️ **G1 へ新ビルドを配っていないこと**
- [ ] ⚠️ **ドロップの実測値**（★ Windows は 0 件）
- [ ] ⚠️★★★ **`pointer_bin` / `focus_transition` の行が実際に出たこと**（★ Windows 側の残件）
- [ ] ⚠️ **両 OS の対テストを壊していないこと**
- [ ] ⚠️ **禁止語 grep の結果**
- [ ] ⚠️ **やらなかったこと / 落としたもの**を明示（★ 「全部できた」と言わない）
