# 決定記録 — O1 計器の実装 (R3-a) と区間指定削除 UI（2026-08-23）

> ★ 前提と既決は `.steering/20260823-o1-nonkeystroke-gap-and-prereg/decisions.md`（D-1〜D-22）。
> ⚠️ ここには **本タスクで新たに下した判断と、実測で分かった事実** だけを書く。

---

## D-A: ⚠️★★★ **macOS のテンキー・修飾キーは観測集合に入れない**（★ replay から強制される）

★ D-14 は「**広げる / 広げないのどちらに決めても、決めた状態を対のテストで固定すること**」と書いた。
→ ★ **本タスクは「広げない」を選んだ。⚠️ ただし恣意的な選択ではなく、次の 2 つで塞がっている。**

| キー | ⚠️ どちらの道も塞がっている理由 |
|---|---|
| **テンキー** | ① 素通し（`macos_vk_to_vk` の既定 `other => other as u32`）だと `kVK_ANSI_Keypad0`(0x52) が **`0x52` = `VK_R`（英字！）** に化け、⚠️ **`is_feature_key` の中**に入る ／ ② 明示写像で `0x60..=0x6F` にしても **やはり `is_feature_key` の中** → ★★★ **どちらでも macOS の特徴量が変わる（= `HMM_VERSION` bump）** |
| **修飾キー** | ⚠️ mac の tap は **`KeyDown`/`KeyUp` のみ**で、修飾は `FlagsChanged` で来る。★ mask に足すと `handle_event` が送信の**前**に触る `LAST_KEY_MS` と IME 状態機械へ波及し、**沈黙検出（＝ 特徴量経路）に触れる** |

- ★ **なぜ「replay から強制される」と言えるのか**: ADR-016 D8 の「併せてやること 1」は
  **replay 側にも同じ `is_feature_key` を置け**と要求する。⚠️ replay は `category` から
  **代表 VK へ逆写像**するだけで **OS の文脈を持たない** → ★ `is_feature_key` は
  **OS 非依存な単一集合**でなければならない。
  → ⚠️★★★ **したがって「mac だけテンキーを特徴量から外す」という逃げ道が原理的に無い。**
- ★ 固定したテスト（**両 OS に対**）:
  - Win: `hook_windows.rs::numpad_is_observed_and_is_a_feature_key_on_windows`
  - mac: `hook_macos.rs::numpad_is_not_observed_on_macos` / `modifiers_are_not_observed_on_macos`
  - **両 OS で走る**: `key_gate.rs::macos_numpad_cannot_be_observed_because_both_mappings_land_inside_the_feature_set`
    （⚠️ mac 側のテストは Windows では 1 行も走らないので、**判断の理由**を OS 非依存側に置いた）
- ⚠️★★★ **同意文書 注 A の「テンキー」は Windows でのみ真である。** → ★ T5 で研究者へ返す。

---

## D-B: ★★★ `is_feature_key` は **`loop_step::step()` に置く**（★ replay 側に書き足さない）

- ★ **実測**: `gse-replay` は本番と**同じ `loop_step::step()`** を通る
  （`replay.rs` の `ReplayEvent::Key` → `step(.., LoopInput::Key(event), ..)`）。
- → ★★★ **1 か所置けば本番と replay の両方に同時に効く。**
  ⚠️ ADR-016 D8 の「replay 側にも同じゲートを置く」は **2 か所に書くこと**ではなく
  **replay にも効かせること**が要件であり、★ **構造的に満たした**（2 つの真実を作らない）。
- ⚠️ **1Hz ゲートへ `return` しない** —— ★ 観測専用キーで早期 return すると
  そのティックの feat 発火が 1 回遅れる。⚠️ それは「特徴量に流さない」ではなく
  **「出力のタイミングを変える」**であり、約束（特徴量は 1 バイトも変わらない）を破る。

---

## D-C: ⚠️★★★ **ADR-016 D8 の acceptance の前提が 1 つ誤っていた**（★ 実測で判明・訂正）

> ADR-016 D8 の表 逐語:「**ゴールデン byte-equal** | ★ ゴールデンは**旧 fixture（新カテゴリを含まない）**」

- ⚠️★★★ **この前提は偽であった。** ★ `tests/fixtures/category_coverage.ndjson` は
  **生 `vk` で 16(VK_SHIFT) / 27(Escape) / 37(VK_LEFT) / 112(F1) を含む**
  （★ 2026-08-23 に repo 内の全 fixture を機械的に走査して確認。⚠️ **含むのはこの 1 本だけ**）。
- ★ 旧コードでは replay がゲート無しで**それらを特徴量に流していた**
  （⚠️ 本番のフックは落としていたので、**本番と replay が既に食い違っていた**＝ D8 が塞ごうとした穴そのもの）。
- → ★ **`tests/snapshots/category_coverage.json` を 1 本だけ再生成した。**
  差分は `f4 9.0→8.0` / `raw_y 0.76→0.72` / `ewma_y 0.746→0.734` / `keys 9→8`（**2 スナップショット中 1 件**）。
- ⚠️★★★ **`HMM_VERSION` は bump しない。** ★ 理由:
  **本番の特徴量経路は 1 ビットも変わっていない** —— 旧フックは非特徴量キーを 1 件も送っておらず、
  ⚠️ **実ログに 16/27/37/112 を含むものは存在しえない**（★ 実 fixture 11 本を走査して 0 件を確認）。
  → ★ 変わったのは **「実ログには現れない合成 fixture の replay 結果」**だけである。
- ★ **実 fixture 由来のゴールデン 5 本は byte-equal のまま**
  （`minimal` / `deep_silence` / `argumentative_ime_mixed` / `phase1_ime_heavy` / `vibe_coding_ime_mixed`）。

---

## D-D: ★ 一時停止は **ロガーの書き出し点**で止める。⚠️ 判断は **ストリーム内の行**で進める

- ★ **どこで止めるか**: フックの送信点ではなく **ロガーの書き出し点**。
  ⚠️ フックで止めると分析スレッドから見て**沈黙と区別が付かず**、`starved_ms` / 介入判定が
  「離席した」と誤解する。★ 被験者への約束は逐語「**すぐ止める**」＝ **ファイルに 1 バイトも書かない**こと。
- ⚠️★★★ **グローバル Atomic を読む形は壊れていた（テストで再現して直した）**:
  ★ `recording::is_paused()` をロガー側で読むと、**キューに積まれた順序**と
  **フラグが切り替わる時刻**がずれ、⚠️ **停止中に積まれた行が、取り出す前に再開すると書かれてしまう**。
  → ★ **ストリーム内の `RecordingPause` 行で状態を進める**形に変えた（順序が定義上ずれない）。
  ★ グローバル Atomic は **UI の稼働中インジケータ専用**に降格した。
- ★ 通すのは `recording_pause` と `meta` だけ（`recording::is_writable_while_paused`）。
  ⚠️ 判断は **`LogEntry::line_type()` の 1 か所**に閉じた（★ 19 個の match 腕に散らさない）。

---

## D-E: ★ 台帳は **`.jsonl`** にする（⚠️ `.ndjson` にしない）

- ⚠️★★★ `reconcile.rs` は `gse_*.ndjson` を**提出候補**として拾う。
  → ★ 台帳を `.ndjson` にすると **削除を要求した事実そのものが研究者へ渡る**ことになり、
  ⚠️ 「理由を聞かない」の趣旨が**裏から破れる**。
- ★ 接頭辞（`gse_`）でも弾かれるが、**拡張子でも外して二重に**した。
- ★ 台帳に書くのは **5 つの数だけ**（`requested_at` / `from` / `to` / `files_touched` / `lines_removed`）。
  ⚠️ **何を消したかは書かない**（★ 書いた瞬間、消した区間の内容が台帳に復活する）。

---

## D-F: ⚠️★★★ **macOS の O1 計器は「明示的なスタブ」にした**（★ 実装しなかった理由を記録する）

| # | 理由 |
|---|---|
| 1 | ⚠️★★★ **本機（Windows）では macOS の FFI を 1 行も型検査できない。** ★ `rustup target add aarch64-apple-darwin` → `cargo check --target` を**実際に試して失敗を確認した**（`objc2-exception-helper` の build script が Objective-C コンパイラを要求）。★ 追加した target は**検証後に削除して環境を元に戻した** |
| 2 | ⚠️ 検証されていない FFI を `input/` に置くと **macOS CI が落ちる**か、さらに悪く **黙って動かない計器**になる |
| 3 | ★ **ADR-013 D1 が「計器が無い」を正当な状態として設計に入れている** —— `FOCUS_AVAILABLE` / `POINTER_AVAILABLE` を `false` にすれば、macOS のログは **「測っていない」と自己申告**する。⚠️ 0 行を「信号が無かった」と誤読されない |
| 4 | ⚠️ **ADR-016 D9 の前提 1（mac の tap 2 系統の実機確認）が未了**である。★ 確認で落ちれば作り直しになる |

- ★ **先例がある**: `sensors_macos.rs`（CoreMotion を「stub (not available)」と明記して置いている）。
- ★ 実装に必要な API は `observe_macos.rs` の冒頭に**調査済みの形で列挙**した。

---

## D-G: ⚠️★★★ **`keyboard_layout` はロガー起動より *前* に解決しないと meta に載らない**（★ 実機で踏んだ）

- ★ 初版は `init_hook` の後に `set_keyboard_layout_id` を呼んでいた。
  ⚠️ **`meta`(session_start) はロガースレッドが起動直後に書く**ので**間に合わなかった**
  （★ 実機の NDJSON で `keyboard_layout` が欠けているのを確認）。
- → ★ `log_channel.start(..)` の**直前**へ移した。⚠️ 修正後の実機ログで
  `"keyboard_layout":"00000411"` が meta に載ることを確認した。
- ★ **教訓**: 「`OnceLock` に入れれば読まれる」は**順序を確かめない限り言えない**。

---

## D-H: ⚠️ **`anyhow` はこの repo の依存に無い**（★ `agent-shared.md` の記述と食い違う）

- ⚠️ `docs/agent-shared.md` / `rust-standards` は「エラーは `anyhow::Result`」と書くが、
  ★ **`src-tauri/Cargo.toml` に `anyhow` の行が無い**（2026-08-23 実測）。
  `overlay_panel.rs` が逐語「このリポジトリは anyhow を依存に持たず `Result<_,String>`/`tauri::Result`」と明記。
- → ★ **実装に合わせた**（`redaction.rs` は `Result<T, String>`）。⚠️ 依存を増やさない。
- ★ `data-privacy` Skill の「関連 Skill」欄の記述だけ訂正した。⚠️ `agent-shared.md` 本体は本タスクでは触っていない（★ 研究者/dev 判断で直す）。

---

## D-I: ★ **既存の schema drift を 1 件見つけて直した**（⚠️ 本タスクとは無関係）

- ★ `emit_schema` を回すと **`monk_mode` が消える**差分が出た。
  ⚠️ `schema_dto.rs` は commit `845d7ca`（Wall / Monk Mode 全削除）で `monk_mode` を落としていたが、
  **`schema/current.json` が再生成されていなかった**。
- → ★ 本タスクの再生成でついでに解消した。⚠️ **CI の drift check が拾う状態だった**。

---

## D-J: ⚠️★★★ **D6 の穴は「届かない」ではなく「*argumentative* として届く」だった**（★ 実測・研究者へ返す）

> ★ 引き継ぎ T3 の項目:「⚠️ **D6 の穴**: `start_session` 無し経路で `task_kind` が届かない」

- ★ **実測して読み替えが要ることが分かった**（`src/App.tsx`）:
  `record_session_meta` は **`start_session` の直後に必ず呼ばれる**（★ 失敗したら Dashboard へ進まない）。
  → ⚠️ **`session_meta` 行は必ず出る。** 「届かない」のではない。
- ⚠️★★★ **問題は届く値のほうである** —— ★ `App.tsx` の `taskKind` は
  **論述固定（判断 5 の lock）**なので、O1 の自然作業が **`task_kind:"argumentative"` /
  `head_id:"writing"` として記録される**。
  → ★ **「黙って混ざる」よりも悪い —— 積極的に誤ったラベルが付く。**
- ⚠️ **本タスクでは直さない。** ★ 直すには **判断 5（lock 解除）と 判断 4（宣言 UI の文言）**が要り、
  どちらも引き継ぎ §5 で**スコープ外**である。→ ★ **T5 で研究者へ返す。**
- ⚠️ **IPC 契約変更（`start_session` に `task_kind` を持たせる）は行わなかった** ——
  ★ 宣言 UI が無い状態で足しても**呼ぶ者がいない死んだ経路**になり、
  CLAUDE.md 禁止事項「曖昧な指示に対して推測で実装しない」に触れる。

---

## D-K: ★ 実機で確かめたこと / ⚠️ 確かめられなかったこと（★ 2026-08-23・Windows 11）

### ✅ 確かめたこと

| 何 | ★ 実測値 |
|---|---|
| 3 本目の WinEvent フックの設置 | ✅ `O1: foreground transition hook installed` |
| Raw Input（`RIDEV_INPUTSINK`・マウスのみ）の登録 | ✅ `O1: raw mouse input registered (INPUTSINK)` |
| キーボードレイアウト | ✅ `meta` に `"keyboard_layout":"00000411"` |
| `capabilities` の自己刻印 | ✅ `config_gated` に `focus_transition` / `pointer_bin`、`unconditional` に `recording_pause` |
| ⚠️★★★ **ドロップの実測** | ✅ **0 件** —— ★ 修飾キー（`VK_LCONTROL`/`VK_RCONTROL`）を **4182 イベント / 15 秒（≈279 events/s）** 注入して `EVENTS_DROPPED` の報告行がゼロ |
| ★ 注入が本当にフックへ届いていたか | ✅ **1630/1630 完全一致**（独立プローブの `hook_calls` = 注入数）。⚠️ **GSE と同時に 2 プロセスが `WH_KEYBOARD_LL` を張れている**ことも再確認 |

### ⚠️ 確かめられなかったこと

| # | ⚠️ 何 | ★ なぜ |
|---|---|---|
| 1 | **`pointer_bin` / `focus_transition` の行が実際に出ること** | ★ 測定中、端末が**完全にアイドル**だった（独立プローブの `raw_mouse=0` で確認）。⚠️ **ゼロ抑制と `WINEVENT_SKIPOWNPROCESS` が正しく効いている状態**であって、故障ではない。→ ★ **マウスを動かし・ウィンドウを切り替えながら 10 秒走らせれば確認できる**（手順は `tasklist.md`） |
| 2 | **macOS 側の型検査** | ⚠️ 本機では不可（D-F）。→ ★ **macOS CI に委ねる** |
| 3 | **実入力ラウンドの probe 取り直し**（T4） | ⚠️ **人が実際に打鍵する**必要がある（★ 合成入力では `LLKHF_INJECTED` が付き、「実入力」の確認にならない） |

- ★ **`unsafe` の検証**: `GetRawInputBuffer` の並びを歩く部分（⚠️ `NEXTRAWINPUTBLOCK` の
  桁合わせを誤ると**領域外読み**）を `accumulate_from_buffer` として**切り出し**、
  ★ **手で組んだバッファ**で歩き方を固定するテストを置いた
  （`accumulate_walks_the_buffer_with_qword_alignment` / `non_mouse_records_are_ignored`）。
  → ★ 実機のマウス操作でしか踏めない `unsafe` を、決定論的に検査できる形にした。

---

## D-M: ⚠️★★★ **ADR-014 D4 の「構造的に安全」には例外がある**（★ 自己レビューで発見・実装で塞いだ）

> ADR-014 D4 逐語:「Win: **Raw Input** …… ★ **`RAWMOUSE` に絶対座標フィールドが
> そもそも存在しない**（構造的に安全）」

- ⚠️★★★ **これは相対モードの device に限って正しい。**
  ★ `RAWMOUSE.usFlags` に **`MOUSE_MOVE_ABSOLUTE`(0x01)** が立つ device
  （**RDP セッション / 一部の VM / 一部のタブレット**）では、
  **`lLastX`/`lLastY` は相対移動量ではなく正規化された絶対座標**である。
- ⚠️ そのまま `|x|+|y|` を足すと **(a) 位置由来の値になり (b) 常に最大バケット(7)へ張り付く**。
  → ★ **段 1 の禁止表（絶対座標を持たない）に実質的に触れる。**
- ★ **決定**: 絶対モードの record は **移動量として数えない**（⚠️ ボタン / ホイールは数える）。
  - ⚠️ **前回位置との差を取る形にはしない** —— ★ それは「座標を持たない」という性質を
    **構造**から**方針**へ格下げする。★ D4 は構造で守ることを選んでいる。
  - ⚠️ **代償**: 絶対モードの端末では `moved` が常に 0 になる。
    ★ ただし O1 の対象は**被験者の実機（Surface Pro 8 + Type Cover = 相対モード）**であり、
    RDP 越しの作業は想定に無い。→ ★ **研究者へ返す**（★ 想定が変わるなら再検討が要る）。
- ★ 固定したテスト: `observe_windows.rs::absolute_mode_records_do_not_contribute_movement`
- ⚠️ **ADR-014 D4 の本文は書き換えていない**（★ 凍結物に触れない方針）。→ ★ 研究者判断で追記するかを残す。

---

## D-L: ⚠️ **サブエージェントによるレビューは実行していない**（★ セッション指示による）

- ★ CLAUDE.md 行動規範 4 / memory は `code-reviewer` + `security-checker` の並列起動を求めるが、
  ⚠️ **本セッションのシステム指示が「ユーザーが要求しない限り Agent tool を呼ばない」と明示している**。
  → ★ **指示に従い、自己レビューに置き換えた**（⚠️ 完了報告に明記する）。
- ⚠️ 同じ理由で **`/cross-review`（Codex）も未実行**である。
