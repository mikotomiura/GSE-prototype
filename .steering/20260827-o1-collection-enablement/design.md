# 設計 — O1 の計器を「収集できる形」にする

> ★ 一次資料で実測した事実にだけ接地する (`verify-before-claiming`)。
> 行番号は 2026-08-27 の HEAD (`a6583e5`) 時点。

## 0. 実測した前提 (★ すべてコードで確認・2026-08-27)

| # | 事実 | 出所 |
|---|---|---|
| P1 | 分析スレッドは `session_active` が false のあいだ入力を**捨てる** (`while rx.try_recv().is_ok() {}`) | `lib.rs:2712-2719` |
| P2 | 非打鍵チャネル (focus / pointer / secure_input) は**門を通っていない** | `lib.rs:3138-3196` |
| P3 | `tray::measure_state(false, _) == Stopped` → 逐語「GSE — 停止中（記録していません）」 | `tray.rs:45-60` |
| P4 | `liveness::step` は `!session_active` で `starved_ms` を **0 に落とす** | `input/liveness.rs:88-92` |
| P5 | `decide_start_action` は非 G1 で `NotG1` → **ローテートしない** | `g1.rs:376-380` |
| P6 | `write_meta_end` (`session_end`) は **Rotate / BlockEnd / End** の 3 経路だけ | `logger.rs:1862,1877,1933` |
| P7 | `is_closed_g1_session` は `session_end` **かつ `g1_mode`** を要求 | `reconcile.rs:205-228` |
| P8 | 送信は `approved_unsent_age_files` (`.age.ok` 必須) だけを送る | `reconcile.rs:367-370` |
| P9 | `redact_dir` は `gse_*.ndjson` だけを書き換え、`.age` は**対象外** | `redaction.rs:172-181` |
| P10 | 制御エントリ (`Rotate`/`BlockEnd`/`End`) は `line_type()==None` で**一時停止ゲートを常に通る** | `logger.rs:1502-1508` |
| P11 | probe scheduler は `SESSION_START_MS == 0` のあいだ**スケジューラを作らない** | `lib.rs:3740-3746` |
| P12 | `INTERVENTION_ENABLED` の既定は **`true`** | `lib.rs:102` |
| P13 | replay は `session_start` **0 本**を許す (落ちるのは「相異なる `task_kind` が 2 つ」と「宣言つきで `session_start` が 2 本以上」) | `bin/replay.rs:1740-1762` |
| P14 | `RECORDING_PAUSED` は葉モジュールの Atomic で誰からでも読める | `recording.rs:38-50` |

## A. O1 モードのマーカー — 新モジュール `src-tauri/src/o1.rs`

★ `g1.rs` の 2 経路を**そのまま写す**:

- **マーカー**: 実行ファイルを包むフォルダの **`o1.mode`**
- **環境変数**: **`GSE_O1_MODE=1`** (`"1"` 完全一致のみ・`g1::g1_enabled_by_env` と同じ厳しさ)

★ 階層数の解決は **`g1::exe_to_folder_levels()` / `g1::folder_up()` を再利用する**。
⚠️ 複製すると macOS のバンドル階層が変わったとき片方だけ直り、**無音で失敗する**。
(★ `architecture-rules` ルール 1 の禁止対象は「層をまたぐ直接依存」であり、
`g1` / `o1` は同層の純判定モジュールである。)

### ⚠️★★★ G1 との相互排他

```rust
pub fn resolve(g1: Option<G1Source>, o1: Option<O1Source>) -> Option<O1Source>
```

★ **G1 が立っていたら O1 を無条件に落とす** (`tracing::error!` で必ず残す)。
理由: G1 は `preregistration.md §3.6` がブロックの事後除外を禁じており **取り返しがつかない**。
⚠️ 起動そのものは止めない (G1 の実施を潰すほうが害が大きい・`g1.rs` の先例と同じ倒し方)。
→ **純関数なので両 OS 上で検算できる**。テストで固定する。

### ★ モード保持

`o1.rs` 内の `OnceLock<Option<O1Source>>` に **起動時 1 回だけ**入れる (`g1.rs` と同じ流儀)。
⚠️ lib.rs 側に置かないのは **`logger::default_log_path()` が読む**ためである
(`logger` → `lib` の逆依存を作らない)。

## B. 常時収集

### B-1. 分析スレッドの門 (`lib.rs:2712`)

```rust
pub fn analysis_gate_open(o1_mode: bool, session_active: bool) -> bool { o1_mode || session_active }
```

⚠️ **非 O1 では `session_active` そのもの**なので G1 / Phase1 は 1 バイトも変わらない。

### B-2. 稼働中インジケータ (`tray.rs` / `liveness`)

```rust
pub fn recording_active(o1_mode: bool, session_active: bool, paused: bool) -> bool {
    if o1_mode { !paused } else { session_active }
}
```

- `tray::current_state` の第 1 引数をこれに差し替える。
  ⚠️ **`measure_state` / `measure_label` / `measure_title` は 1 文字も変えない**
  → `tray_labels_never_leak_cognitive_state` は緑のまま。
- ⚠️ **非 O1 で `paused` を見に行かない**のは、Phase1 の表示挙動を変えないためである
  (現行は一時停止中でも「計測中」と出る。★ 直したくなるが、それは別タスク)。

### B-3. `liveness` の `starved_ms` (事前登録 §7 E1 の実装 acceptance)

★ `liveness::step` の `session_active` 引数に **`recording_active(...)` を渡す**。
→ ⚠️ O1 では `session_active` が永久に false なので、渡さないと
**`starved_ms` が常に 0 = フック死を永久に検出できない** (mac の `CGEventTap` 失効が無検出になる)。
★ 一時停止中は数えない (打鍵が来なくて当たり前・現行の「非計測中は数えない」と同じ理屈)。
→ **テストで固定する。**

### B-4. 介入 (判断 O1-5)

`run()` で O1 なら `INTERVENTION_ENABLED.store(false)`。
⚠️ 既定が `true` (P12) なので**何もしなければ出る**。宣言経路も常に `false` を書く。

### ★ probe (★ 判断ではなく帰結として記録する)

O1 では `start_session` を通らないので `SESSION_START_MS` は 0 のまま
→ **プローブは構造的に発火しない** (P11)。
⚠️ 本タスクでは probe に手を入れない。
★ 将来 O1 で宣言に session_start を持たせるなら**別途研究者判断が要る**。

## C. 宣言 UI

### C-1. backend `declare_task_kind(task_kind)` (新 IPC)

★ **1 アクションで 3 つ** (判断 4b-1)。⚠️ **順序が意味を持つ**:

1. `TaskKind::parse` で検証 (未知値は `Err`)
2. **`LogEntry::Rotate` を先に送る** — ⚠️ 先に `SessionMeta` を書くと
   **宣言が旧ファイルに落ち、新ファイルが未宣言になる** (意味が逆になる)
3. 新ファイルへ `LogEntry::SessionMeta { task_kind, intervention_enabled: false, .. }`
4. `engine.reset()` + 分析スレッドの reset シグナル
   (N-3: 新ファイル先頭 30 秒が前ファイルに依存しない)
5. `engine.set_domain(domain)` — ⚠️ **ログ送信に成功した後**
   (`record_session_meta` が security-checker 指摘で採った順序と同じ)

⚠️ **`record_session_meta` には手を触れない** (Phase1 / G1 の経路を汚さない)。

ローテート方針は **`o1::decide_declaration_action(o1_mode, g1_mode)` (純関数)** が決める。
⚠️ 引き継ぎは「`decide_start_action` に O1 の枝を足す」と書いていたが、
★ **`decide_start_action` は `start_session` 専用の経路**であり、O1 は `start_session` を通らない。
G1 の enum と関数に O1 の引数を通すと **G1 の分岐が O1 を知る**ことになり §4-1
「分岐はすべて O1 モードの中に閉じる」に反する。→ **判定は `o1.rs` に置く**
(実質は同じ: ローテートする / G1 のブロック数は数えない)。

### C-2. 未宣言 = 行の不在 (判断 4b-3)

- O1 では App.tsx が **`record_session_meta` を呼ばない**。
- `DECLARED_TASK_KIND: Mutex<Option<TaskKind>>` を持ち、`get_recording_status` で返す。
- ⚠️ 未宣言のあいだ `session_meta` 行は **1 本も出ない**。

### C-3. frontend

- `get_o1_mode` を追加 (`get_g1_mode` の鏡像)。
- **O1 では start 画面を飛ばす** (`isStarted` 初期値 true)。
  ⚠️ 押させると `record_session_meta` が走り、未宣言を表せない (判断 4b-3 の破れ)。
- `Dashboard` へ **`calibrationMode={true}`** を渡す (O1 のとき)。
  ★ 自然作業中に推定状態が見えると被験者の行動が変わる
  (`preregistration.md §2.12` の盲検と同じ趣旨)。
- `RecordingControls` に 1 行足す: 「**記録中 · 作業の種類: ○○**」/ 未宣言は「**未設定**」。
  ★ 同意文書 §2 逐語「そこを押すと、次の 4 つから選べます」に合わせ、
  **その行から 4 択を開ける**。
- ラベルは **「論述 / 通信文 / デザイン・映像・制作作業 / vibe coding」**、
  `creative` には補足「（図面・動画編集・3D など、文字をあまり打たない作業）」(判断 O1-3)。
  ⚠️ **新 enum 値は足さない**。

## D. 日次ローテート ＋ 48 時間の猶予

### D-1. ファイル名で O1 を表す (⚠️ schema を変えないための選択)

★ O1 のセッションは **`gse_o1_<ts>.ndjson`** という名前で開く
(`logger::default_log_path` / `next_session_path`)。

⚠️★★★ **本来は `meta` 行に `o1_mode` を刻むほうが強い** (`g1_mode` の先例・事後検証ができる)。
★ しかしそれは `schema_dto.rs` → `schema/current.json` の変更を伴い、
**§0-3「1 バイトも変えない」と gse-dataset の parity 更新**に直撃する。
→ ★ **本セッションでは schema を変えない**。⚠️ **研究者へ返す論点として `decisions.md` に残す。**

★ ファイル名でも失敗様式は同じく fail-loud である:
マーカーが外れれば `gse_<ts>.ndjson` になり、**提出候補から外れて研究者に届かない** (無音では増えない)。

### D-2. 日次ローテート

`o1::should_rotate_daily(opened_at_ms, now_ms) -> bool` (純関数・`ROTATE_AFTER_MS = 24h`)。
60 秒ごとに見るスレッドを **O1 のときだけ**起こす。

⚠️ **ローカル深夜 0 時にしない理由**: ローカル時刻の取得は OS 呼び出しが要り
(`chrono` 非依存・`logger::chrono_like_filename` は **UTC 近似**)、
UTC 深夜は JST 09:00 = **就業時間の真ん中**である。
→ ★ 「ファイルを開いてから 24 時間」なら **1 日 1 本**が保証され、TZ の曖昧さが無い。

★ ローテート時は **宣言変更と同じ 3 点**を行う (`session_meta` は宣言済みのときだけ再掲する)。
⚠️ reset しないと新ファイル先頭 30 秒が前ファイルに依存する (N-3) ので、日次でも reset する。

### D-3. O1 の「閉じた」述語と 48 時間の猶予

```rust
pub fn closed_o1_sessions(dir: &Path, now_ms: u64, grace_ms: u64) -> Vec<PathBuf>
```

- `gse_o1_*.ndjson` である
- `meta.session_end` を持つ (= もう書かれない)
- ⚠️ `g1_mode` を**持たない**
- `has_any_data_row`
- ★ **`now_ms - session_end >= grace_ms`**

⚠️★★★ **猶予は「包む前」に効かせる。** `.age` を作ってしまうと
`redact_dir` は `.age` を触らない (P9) ので、**48 時間より前に包むと削除保証が崩れる**
(＝ ADR-014 判断 3 の根拠 3 が崩れる)。

`O1_SUBMIT_GRACE_MS = 48h`。⚠️ **恣意的な値である** (repo に無い数字) ことを定数コメントに書く。

### D-4. 承認ゲート

★ O1 は `unsent_age_files` (承認不要) を送る。⚠️ G1 は `approved_unsent_age_files` のまま。
理由: 同意文書 §5 逐語「**48 時間おいてから暗号化して自動的に研究者へ送ります**」。
毎日確認ボタンを押させると**その逐語が嘘になる** (§0-1 の失敗 #3)。
⚠️ `.age.ok` が防いでいた「同意手続きを経ていない人が起動する」経路は、
★ O1 でも**配布フォルダのマーカー (`o1.mode`) が同じ役割**を担う。→ `decisions.md` に残す。

### D-5. `reconcile` の分岐

`ReconcileOptions` に `mode: CollectionMode { G1, O1 }` を足す (既定 `G1` = 現行と同一)。
`gse-submit --o1` で切り替え、`lib.rs` が O1 のときだけ付ける。

## テスト戦略

| 対象 | どこで | 何を固定するか |
|---|---|---|
| A | `o1.rs` unit | env の厳しさ / マーカー優先 / **G1 と同時に立たない** / 両 OS の階層 |
| B-1 | `o1.rs` unit | `analysis_gate_open` の真理値表 (⚠️ 非 O1 は `session_active` と同値) |
| B-2/3 | `o1.rs` unit + `tray.rs` unit | `recording_active` の真理値表 / **O1 で `starved_ms` が進む** |
| C | `o1.rs` unit | `decide_declaration_action` (O1 だけ Rotate・G1 と排他) |
| C | frontend | ラベル 4 値と補足文言 (`tsc` + 目視) |
| D | `o1.rs` unit | `should_rotate_daily` (境界 / 時計巻き戻し) |
| D | `reconcile.rs` unit | **猶予中は候補にならない / 猶予後に候補になる / 猶予中に消せる** |
| 回帰 | `gse-replay` | ゴールデン byte-equal (`HMM_VERSION` 不変の証拠) |
| 回帰 | `emit_schema` | `schema/current.json` と byte-equal |

⚠️ **両 OS に対のテストを置く** — `exe_to_folder_levels` は `#[cfg]` 非依存の純関数として検算する。
