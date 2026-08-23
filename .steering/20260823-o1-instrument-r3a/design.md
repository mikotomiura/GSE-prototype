# design — O1 計器 (R3-a) と区間指定削除 UI

## ★ 全体方針

★ **ADR-014 / ADR-016 の既決を実装するだけ**である。設計の分岐は残っていない。
⚠️ 唯一の設計判断は「**macOS のテンキー・修飾キーをどう扱うか**」（下記 D-A）で、
★ これは **replay の要求から強制される**（恣意的な選択ではない）。

---

## T1. 区間指定削除 UI（ADR-014 D7 の 3 点セット）

### ★ 置き場所

| 何 | どこ | ⚠️ なぜ |
|---|---|---|
| 純粋な判定・書き換え | ★ **新規 `src-tauri/src/redaction.rs`** | ⚠️ OS API を 1 つも呼ばない（`architecture-rules`）。★ 単体テスト可能 |
| IPC | `lib.rs` の `#[tauri::command]` | ★ 既存の作法に合わせる |
| UI | `src/components/Dashboard.tsx` | ★ 被験者が普段見る画面 |

### ★ 削除の意味

```
delete_time_range(from_ms, to_ms)
  → セッションディレクトリ（logger::session_log_dir()）の gse_*.ndjson を走査
  → 各行の時刻 t（/ session_start / session_end）が [from, to] に入る行を落とす
  → ⚠️ 一時ファイルへ書いて rename（★ 途中で落ちても原本を壊さない）
  → ★ 台帳へ「消した事実」を 1 行 append
```

- ⚠️★★★ **理由を聞かない**（引数に理由を持たない・UI にも入力欄を置かない）。
- ⚠️ **いま書いているファイルは触らない** —— ★ `get_session_file` が返す現行パスを除外し、
  UI に「⚠️ 現在記録中のファイルは対象外。止めてから消す」と出す。
  → ★ **一時停止 → 削除** の順を UI が強制する。

### ⚠️★★★ 台帳（「消した事実」を残す）

- ★ 置き場所: **セッションディレクトリの `redaction_ledger.jsonl`**
- ⚠️★★★ **拡張子を `.ndjson` にしない** —— ★ `reconcile.rs:189` が `gse_*.ndjson` を拾うため
  （★ 接頭辞でも弾かれるが、**二重に**外す）。
- ★ 記録するのは **「消した」ことだけ**:
  `{"requested_at":<ms>,"from":<ms>,"to":<ms>,"files_touched":<n>,"lines_removed":<n>}`
  ⚠️ **何を消したか（行の内容・種別の内訳）は書かない。**

### ★ 3 点セットの残り 2 つ

| # | 要件 | ★ 実装 |
|---|---|---|
| i | 稼働中インジケータ | ★ Dashboard に常設の記録状態バッジ（★ **止まっているときは明示的に「記録していません」**） |
| ii | 即時の一時停止 | ★ `set_recording_paused(bool)` —— **フックの送信点**と**ロガーの書き出し点**の両方で止める |

⚠️ **一時停止は「信号が無い」と区別できなければならない**（ADR-013 D1 の趣旨）。
→ ★ 一時停止の**遷移時に marker 行**を書く（`{"type":"recording_pause","t":..,"paused":..}`）。
⚠️ ★ 再開時は `reset_signal` を立てて **特徴量バッファを捨てる**（★ 停止をまたいだ flight time を作らない）。

---

## T2. ゲート分割（ADR-016 D8）

### ★★★ 置き場所の決定 —— ⚠️ **`is_feature_key` は `loop_step::step()` に置く**

★ 実測（2026-08-23）: **`gse-replay` は本番と同じ `loop_step::step()` を通る**
（`replay.rs` の `ReplayEvent::Key` → `step(.., LoopInput::Key(event), ..)`）。
→ ★★★ **`step()` に 1 か所ゲートを置けば、本番と replay の両方に同時に効く。**
⚠️ ADR-016 D8 の「replay 側にも同じゲートを置く」は**構造的に満たされる**（★ 2 か所に書かない）。

```
[hook]   is_observed_key(vk)  ← input/hook_{windows,macos}.rs（OS 固有）
            ↓ channel（InputEvent）
[分析]   loop_step::step()
            ├ out.key = Some(KeyRecord{..})        ★ 常に（→ logger → category 量子化）
            └ if is_feature_key(vk) { extractor.process_event(); register_keystroke(); }
```

### ★ `is_feature_key` の定義（`analysis/key_gate.rs` 新規・OS 非依存）

⚠️★★★ **現行 Windows `is_typing_key` と 1 バイトも違わない集合**にする:
`0x41..=0x5A | 0x30..=0x39 | 0x60..=0x6F | 0xBA..=0xC0 | 0xDB..=0xDF | 0x08 | 0x0D | 0x20 | 0x09 | 0x2E`

### ⚠️★★★ D-A: macOS のテンキー・修飾キーは **観測集合に入れない**（★ replay から強制される）

| キー | Win | mac | ⚠️ 理由 |
|---|---|---|---|
| 修飾 (Shift/Ctrl/Alt) | ★ **観測する** | ❌ **できない** | ★ mac の tap は **`KeyDown`/`KeyUp` のみ**（`hook_macos.rs`）。修飾は `FlagsChanged` で来る。⚠️ mask に足すと `LAST_KEY_MS` / IME 状態機械へ波及し**特徴量経路に触れる** |
| F1–F12 / Esc / 矢印 | ★ 観測する | ★ **観測する** | ★ `macos_vk_to_vk` に明示写像があり、写像先は `is_feature_key` の**外** |
| **テンキー** | ★ 観測する（従来どおり特徴量にも入る） | ❌ **入れない** | ⚠️★★★ **`macos_vk_to_vk` の既定が `other => other as u32` の素通し**であり、mac のテンキー `0x52`(Keypad0) は **`0x52` = `VK_R`（英字！）** に化ける。★ 明示写像を足して `0x60..=0x6F` にすると **`is_feature_key` の中**に入り、⚠️ **macOS の特徴量が変わる**（= `HMM_VERSION` bump）。→ ★ **どちらの道も塞がっているので入れない** |

★ **これは D-14 が「広げる / 広げないのどちらに決めても、決めた状態を対のテストで固定すること」と
書いた分岐であり、⚠️ 本タスクは「広げない」を選んで対のテストで固定する。**
→ ⚠️ **同意文書 注 A の「テンキー」は Windows でのみ真**。★ 研究者へ返す（T5）。

### ★ acceptance

- `HMM_VERSION` = `0.5.0`（着手時実測）のまま
- ゴールデン byte-equal（★ 旧 fixture は新カテゴリを含まないので、ゲート分割の影響を受けない）
- **schema 変更ゼロ**（★ `category` は `{"type":"string"}`・enum 制約なし）
- ⚠️ **ドロップの実測**（`EVENTS_DROPPED`）

---

## T3. R3-a 計器

### ★ 新しい NDJSON 行種（⚠️ 段 1 の凍結表の中だけ）

| 行種 | 内容 | ★ 出所 |
|---|---|---|
| `focus_transition` | `{"type":"focus_transition","t":<ms>}` ⚠️ **時刻のみ** | ADR-014 D4 L-c |
| `pointer_bin` | `{"type":"pointer_bin","t":<ms>,"move":<q>,"buttons":<n>,"wheel":<n>}` ★ 1 秒ビン・量子化スカラ・**ゼロ抑制** | ADR-014 D4 L-b |
| `secure_input` | `{"type":"secure_input","t":<ms>,"on":<bool>}` ⚠️ **macOS のみ** | ADR-014 D4 |
| `meta.keyboard_layout` | ★ セッション開始時に **1 回だけ**・識別子のみ | ADR-014 D4 |

⚠️★★★ **HWND / PID / 座標 / アプリ識別子を 1 バイトも出さない。**

### ★ 取得手段

| | Windows | macOS |
|---|---|---|
| L-c | ★ **3 本目の `SetWinEventHook`**（`EVENT_SYSTEM_FOREGROUND` = 0x0003 単独） | `NSWorkspace.didActivateApplicationNotification` |
| L-b | ★ **Raw Input**（`RIDEV_INPUTSINK` + `GetRawInputBuffer`・**マウスのみ**）⚠️ `WH_MOUSE_LL` は採らない | ★ **別 tap**（既存 tap に相乗りしない） |
| layout | `GetKeyboardLayoutNameW` | `TISCopyCurrentKeyboardLayoutInputSource` |
| secure | — | `IsSecureEventInputEnabled()` |

⚠️★★★ **`ToUnicodeEx` / `UCKeyTranslate` を呼ばない。**

### ★ capabilities への自己刻印

- `focus_transition` / `pointer_bin` → ⚠️ **`config_gated`**（★ O1 モードでのみ動くため。
  「0 行 = 判定不能」が正しい読み）
- `secure_input` → ⚠️ **macOS のみ**（`#[cfg]` を反映）

---

## ⚠️ テスト戦略

- ★ **純関数に落として `cargo test`**（フック本体は実機でしか動かない・既存の作法と同じ）
- ⚠️★★★ **両 OS に対のテスト** —— `is_observed_key` / `is_feature_key` / `macos_vk_to_vk` の
  テンキー・修飾キーの扱いを `#[cfg(target_os = ...)]` で**対**にする
- ★ ゴールデン: `gse-replay --snapshot` で byte-equal
