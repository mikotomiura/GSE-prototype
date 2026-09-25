# 設計

> ★ 裁定は `decisions.md` 判断 1〜15。⚠️ **本書は「どう作るか」だけを書く**（★ 何を作るかは `requirement.md`）。
> ⚠️ 本書の実装設計の論点は**研究者に上げない**（★ 実装フェーズの持ち物 —— 判断 12 の分担）。

## ⚠️★★★ 先に見つかった制約（★ 一次で実測・2026-09-21）

### (1) `--features` の collector は **release を捨てている** → 極 M+ は新しい収集経路が要る

★ `bin/replay.rs::collect_key_events`（`:2439-2455`）逐語:

```rust
if let ReplayEvent::Key { t, vk, category, press } = ev {
    if press { … out.push(KeyPress { timestamp: t, vk: resolved_vk }) … }
}
```

→ ⚠️★★★ **`press == false`（離上）の行は 1 本も残らない。**
★ `KeyPress`（`metrics.rs:186`）も `timestamp` と `vk` しか持たない。

⚠️ ところが ADR-030 D3 は逐語「★ 復元できる: `key` 行は press と release の**両方**が出る
→ ★ 修飾キーの押下区間は `key` 行だけから復元できる（新計器ゼロ）」と書いている。
→ ★ **計器は足りているが、`--features` の収集経路が落としている。**

★ **採る形**: `KeyPress` を**変えない**（⚠️ `metrics.rs` は HMM 経路と共有なので、
変えると `--metrics` / `--snapshot` の全経路に波及する）。代わりに
**`collect_modifier_intervals(session_path) -> Vec<(u64, u64)>`** を `bin/replay.rs` に足す
（★ `collect_all_feat_timestamps` / `collect_all_ime_shadow_events` と同じ形 ＝ 専用 DTO ＋ 1 パス）。

### (2) 押下区間は **カウント方式**で作る（⚠️ press/release の対応づけをしない）

⚠️ `category:"modifier"` は **14 種のうちの 1 つ**で、`Ctrl` と `Shift` と `Win` を**区別しない**
（`anonymize.rs` の `KeyCategory::from_vk`: `0x10 | 0x11 | 0x12 | 0x5B | 0x5C | 0xA0..=0xA5`）。
→ ⚠️ `Ctrl+Shift+X` のような**入れ子**では、どの release がどの press に対応するかが**原理的に読めない**。

★ **規則**: `modifier` の press で `depth += 1`、release で `depth -= 1`（⚠️ **0 未満へは下げない**）。
**`depth > 0` の極大区間**を押下区間とする。
- ⚠️ 観測区間の右端に達しても `depth > 0` のままなら、**そこで閉じる**（打ち切り。★ `t0 <= b` と対称）。
- ⚠️ 孤立した release（`depth == 0` で来たもの）は**区間を作らない**（★ 0 にクランプ）。件数だけ `warn`。

### (3) 極 B / 極 M+ の適用可否は **判定の根拠が非対称**である（★ 理由を明記する）

| 極 | 判定 | ★ 根拠 |
|---|---|---|
| **極 B**（ポインタ） | 封筒の `provenance.capabilities` に **`pointer_bin` があるか** | ★ `schema/current.json:349` 逐語「★ 『行が無い＝活動が無かった』と読んでよい（⚠️ ただし `capabilities` に `pointer_bin` がある場合に限る。無ければ『計器が無かった』である）」。→ ★ **宣言があれば 0 行は「活動が無かった」＝ applicable**（極 B = 極 A になるが、それは*所見*である） |
| **極 M+**（修飾キー） | 入力に **`category:"modifier"` の `key` 行が 1 本でもあるか** | ⚠️ **修飾キーの計器を表す `capabilities` 項目が無い**（`capabilities.rs::unconditional()` は `"key"` を挙げるだけ・実測）。⚠️ **OS も読めない**（`meta` に `os` が無い）。→ ★ 行の有無で代替する（判断 13。★ 過剰拒否だが**幅は 1 ms も変わらない**） |

⚠️★★★ **この非対称を封筒に書く** —— 判定の根拠が違うことを出力自身が持つ
（★ 理由コードを `no_pointer_capability` / `no_modifier_rows` と**別の語**にする）。

---

## 実装アプローチ

### 全体の並び（⚠️ 順序制約がある）

```
【1】事前宣言文書 ＋ 凍結 JSON ＋ 一致検査       ← ★ 本セッションの対話（研究者の承認 → 凍結）
        │  ⚠️ 逐語「事前宣言文書を作るときに CLI 注入を作る（★ 値より先に作らない）」
        ▼
【2】CLI 注入（凍結 JSON を既定 ＋ --feature-config ＋ --set）
        │
        ├──▶ 【3a】T1a の 30 秒窓（★ 独立。`features.rs` の命名リファクタが先）
        ├──▶ 【3b】極の器（--pole ＋ 封筒 config ＋ applicable 判定）
        │         ├──▶ 【3c】極 B（pointer_bin collector ＋ 抑制区間）
        │         └──▶ 【3d】極 M+（modifier collector ＋ 挿入系の写像）
        ├──▶ 【4】削除幅の制約（★ 独立。`lib.rs` / `redaction.rs` / UI 文言）
        ├──▶ 【5】IME 頻度カウンタ（★ 【3b】の後。onset 行にフラグ）
        └──▶ 【6】起票 21（★ 多 onset の計算量の門。⚠️ 【3c】【3d】の後 —— 3 極で 3 倍になるため）
                    │
                    ▼
                 【7】ADR-030 補訂 2（★ すべての実装形が決まってから）
```

### 【1】事前宣言文書 ＋ 凍結 JSON

- **文書**: `docs/preregistration-p1-episode.md`（新設・判断 2）
  - §0 位置づけ（⚠️ `preregistration-v0.3.md` との違いを冒頭に書く）
  - §1 **運用値**（7 項目・判断 9 / 14）
  - §2 **探索空間・選択 metric・seed・budget・split**（★ 判断 15 —— **草案 → 研究者承認 → 凍結**）
  - §3 読み方の規律（⚠️ 運用値と探索の選択結果が食い違ったときの扱い・判断 1）
  - §4 既知の代償（★ `warmup_count = 100` で短いセッションの yield が落ちる 等）
- **凍結 JSON**: `src-tauri/prereg/p1-episode.json`
  （★ `src-tauri/schema/current.json` と同じ置き方に揃える）
  - ⚠️ **`include_str!` でバイナリに埋め込む** —— ★ 実行時のパス解決に依存せず、
    `provenance.tool_version` と 1 対 1 になる（★ 再現性が上がる）。
  - ★ 同じファイルが **repo のテキストとして**も残るので、文書との一致を検査できる。
- **一致検査**: `scripts/check_prereg_parity.py`（★ `scripts/check_schema_parity.py` と同じ作法）
  - 文書 §1 の表から `(キー, 値)` を抜き、JSON と **byte 単位で**突き合わせる。
  - ⚠️ **陽性対照を持つ** —— 片方を変異させたら**赤になる**ことを検査自身が確かめる
    （★ `feedback_acceptance_self_test` / 起票 23 の教訓 3）。

### 【2】CLI 注入

- `--feature-config <path>`: 凍結 JSON と**同じ schema** の外部ファイルを読む。
- `--set <key>=<value>`: 1 値だけ上書き（★ 繰り返し可）。
  - ⚠️ **未知のキー・型不一致・範囲外は `Err` で止める**（★ fail-closed。⚠️ 黙って無視しない）。
  - ★ 範囲の検査は凍結 JSON の §2 探索空間ではなく**型と物理的な下限**で行う
    （⚠️ 探索空間の外を禁じると感度分析ができなくなる）。
- **封筒 `config` の追加**:

  | キー | 中身 |
  |---|---|
  | `prereg_id` | 凍結 JSON の `id`（例 `"p1-episode"`） |
  | `prereg_version` | 凍結 JSON の `version` |
  | `prereg_sha256_prefix` | 埋め込んだ JSON の SHA-256 先頭 16 桁 |
  | `config_source` | `"frozen"` / `"file"` |
  | `overrides` | ⚠️ **既定から外れたキーと値の配列**（★ 空なら `[]`）。→ 事前登録から外れた出力が自己申告する |
  | `t1a_window_ms` | 【3a】 |
  | `theta_estimator` | `"nearest_rank"`（★ 判断 14） |
  | `pole` / `pole_applicable` / `pole_not_applicable_reason` | 【3b】 |

### 【3a】`T1a` の 30 秒ローリング窓

1. **命名リファクタが先**: `features.rs:129` の `last_ts.saturating_sub(30_000)` の `30_000` を
   `pub const FEATURE_WINDOW_MS: u64 = 30_000;` にする（★ 判断 7 と同じ型のリファクタ）。
   ⚠️ **振る舞いを変えない**ことを既存テストで確かめてから次へ進む。
2. `dispersion.rs` の pause 収集を **`[t − t1a_window_ms, t]`** に広げる（★ 因果的・1 行 1 tick は不変）。
3. ⚠️★★★ **窓は観測区間をまたがない** —— ★ これで **起票 11 が閉じる**:
   起票 11 は「`T1a` も `extract_pause_resumptions` を素通しで使うので、削除後の NDJSON では
   削除区間の前後が 1 本の巨大 pause として接続され、その長さが `pause_max_ms` に出る」と書いた。
   ★ 窓を観測区間の内側に限れば、穴をまたぐ pause が入らない。
   ⚠️ **原因ラベルは作らない**（★ 起票 11 の逐語「原因ラベルを作る方向で直さない」・ADR-030 却下 9）。
   ★ θ の標本規則（補訂 1 項目 1-5）と**同じ規律**になる。
4. ⚠️ **`003-acceptance.sh` の「3 値が同値」を固定する検査を先に書き換える**（★ 起票 7 の申し送り）。
   → 新しい検査は「**30 秒窓に 2 本以上の pause が入る fixture で `p50 != max` になる**」。
   ⚠️ ★ **その fixture を作るのが AC の本体**である（★ 同値のままなら窓が効いていない）。
5. ⚠️ `surprise` と `pause_max_ms` の共線性（起票 7 の併記）は**本タスクでは直さない**。
   ★ 窓が広がると共線性は弱まるはずだが、⚠️ **実測していないので断定しない**。→ 補訂 2 に注記だけ残す。

### 【3b】極の器

- `StallOnsetConfig` に `pole: Pole`（`enum Pole { Baseline, PointerB, ModifierMPlus }`）を足す。
  ⚠️ **enum である**ことが Cartesian を構造的に禁じる（判断 3）。
- `StallOnsetInputs` に `pointer_active_ts: &[u64]` と `modifier_intervals: &[(u64, u64)]` を足す。
  ★ `analysis/` は OS に触らないまま（`bin/replay.rs` が NDJSON から作る）。
- ⚠️ **`provenance.observed_intervals` は極で変わる** —— ★ 極 B では抑制区間を除いた
  **実際に評価した区間**を出す。⚠️ 起票 20 (a) の目的（打ち切りまでの追跡時間 `b − o`）から見ても
  「実際に評価した区間」が正しい。→ ★ フィールド名は変えず、**doc に「極によって変わる」と書く**。

### 【3c】極 B（ポインタ）

- `collect_pointer_bin_timestamps(session_path) -> Result<Vec<u64>, String>`
  （★ `collect_all_feat_timestamps` と同じ形・`t` だけ読む。⚠️ `moved` / `buttons` / `wheel` は**読まない**
  —— ★ ゼロ抑制されているので**行の存在＝活動あり**であり、値は要らない）。
- ★ ビンは**終端時刻**なので、1 行 `t` が覆うのは `(t − 1000, t]`（`pointer_bin.rs` の doc）。
- **抑制区間** = 覆う区間の**極大連続**。
- **合成**: 観測区間から抑制区間を除いた**評価区間**を作り、各評価区間で
  (i) 条件 A の直前状態を `false` に戻し、(ii) 頭の `W` を評価せず、(iii) θ の標本も
  その区間内の隣接 press 対だけを使う（★ 補訂 1 項目 1-2 / 1-3 / 1-5 と**同じ規則**）。
  → ⚠️ **新しい機構を 1 つも作らない**（判断 7）。

### 【3d】極 M+（修飾キー）

- `collect_modifier_intervals` は上記 (1)(2) のとおり。
- 極 M+ では、**押下区間の中の press を `key_net_delta` の +1 から外す**。
  ⚠️ **−1（backspace / delete）は外さない** —— ★ ADR-030 D3 の逐語は
  「**修飾キーが押されている間の *文字キー* は挿入系に数えない**」であり、削除系には触れていない。
  ⚠️ 外すと `Ctrl+Backspace`（単語削除）が消えて `net` が上振れし、**逆向きの系統誤差**が入る。
- ⚠️ **`revision`（`T1c`）も挿入系の写像を使う**。→ ★ 極 M+ で `revision` が変わるか実装時に確かめ、
  変わるなら**極ごとに出る**ことを doc に書く（⚠️ 補訂 1 項目 7 は `r` / `s'` にしか触れていない）。

### 【4】削除幅の制約（判断 8）

- `MIN_REDACTION_WIDTH_MS: u64 = 60_000`（★ 現行 UI が作りうる最小幅 ＝ `datetime-local` の分単位）。
- `lib.rs::delete_time_range` は `to_ms - from_ms < MIN_REDACTION_WIDTH_MS` のとき
  **`to_ms = from_ms + MIN_REDACTION_WIDTH_MS` へ広げる**（★ 終端側へ）。
  - ★ 終端側にする理由: `from_ms` は被験者が「**ここから**消したい」と言った点なので動かさない。
  - ⚠️ 対称に広げると**指定していない過去**が消える。
  - ★ 現行 UI からは到達不能な防御的経路である（★ 幅は常に 60,000 の倍数）。
- **検査 2 本**:
  1. `MIN_REDACTION_WIDTH_MS > StallOnsetConfig::default().hole_gap_ms` を固定する単体テスト。
     ⚠️ **陽性対照**: 定数を逆転させたら**赤になる**ことを変異で確かめる（★ 補訂 1 fixture (xvii)）。
  2. 最小幅未満の区間を渡すと**広がって消える**ことの単体テスト。
- ⚠️ **UI 文言と `docs/o1-deletion-ledger.md` に「広げる」旨を書く** —— ★ 被験者向け文書は契約である。

### 【5】IME 頻度カウンタ（補訂 1 項目 4）

- `StallOnset` に `ime_overlap: Option<bool>`（★ onset 行だけ埋まる。他は `None` —— 既存 4 フィールドと揃える）。
- 判定: onset の `[s, t0]` が `ime_shadow` 行の `[t − dwell_ms, t]` と**重なるか**。
- ⚠️ **抑制はしない**（★ 判断 25 #7 のまま）。数えるだけである。
- ⚠️ **偏りを文書に書く**: (i) macOS の `dwell_ms` は 1 変換分とは限らない
  (ii) **20 秒を超えた変換は行が出ない**（両 OS 共通）→ ★ **頻度は下限として読む**。

### 【6】起票 21（計算量の門）

- `008-acceptance.sh` の AC18 / AC18b は **onset が 1 本**しか立たないので `R` に比例する経路を素通りさせる。
- ★ **多 onset の入力**（★ 停滞と短い産出を交互に並べ、`θ_person` を満たす沈黙を多数作る）で
  20 秒の門を張り直す。⚠️ **`R` が実際に増えていることを検査自身が確かめる**
  （★ 「onset がちょうど 1 つ」を要求していた旧 AC18 の逆）。
- ⚠️ 両極で 3 実行になるので、**門は 1 極あたり**で置く（★ 3 倍を門に織り込まない）。

### 【7】ADR-030 補訂 2

- 冒頭に**何を上書きし何を規範へ上げるかの表**を置く（★ 補訂 1 と同じ作法）。
- 補訂 1 の「補訂しないもの（範囲外）」のうち **D9（壁時計）以外をすべて閉じる**（判断 11）。
- ⚠️ **本文は 1 文字も書き換えない**。

---

## 変更対象

### 修正するファイル

- `src-tauri/src/bin/replay.rs` — 引数（`--pole` / `--feature-config` / `--set`）・封筒 `config` の拡張・
  collector 2 本の追加・凍結 JSON の埋め込み
- `src-tauri/src/analysis/feat_offline/mod.rs` — `StallOnsetInputs` に 2 入力・`key_net_delta` の極分岐
- `src-tauri/src/analysis/feat_offline/stall_onset.rs` — `Pole` / 評価区間の合成 / `theta_sample_n` / `ime_overlap`
- `src-tauri/src/analysis/feat_offline/dispersion.rs` — 30 秒ローリング窓
- `src-tauri/src/analysis/features.rs` — `30_000` の `pub const` 化（★ 振る舞いは変えない）
- `src-tauri/src/lib.rs` — `delete_time_range` の最小幅
- `src-tauri/src/redaction.rs` — 最小幅の定数（★ 置き場は実装時に決める）
- `src/components/RecordingControls.tsx` — 文言（「広げて消す」）
- `docs/o1-deletion-ledger.md` — 同上
- `docs/adr/ADR-030-stall-onset-and-decision-episode.md` — **補訂 2**（末尾に追記）
- `docs/preregistration-v0.3.md` — 新文書へのリンク 1 行
- `docs/agent-shared.md` — リンクハブに 1 行
- `docs/verification-runbook.md` — 3 極を回す手順
- `.steering/20260914-mhd-feature-offline-tiers/blockers.md` — 起票 7 / 11 / 12 / 13 / 14 / 15 / 16 / 21 に
  **✅ 是正済み**を追記（⚠️ 起票本文は書き換えない）
- `src-tauri/tests/.../003-acceptance.sh` / `008-acceptance.sh`（★ 実パスは実装時に確かめる）

### 新規作成するファイル

- `docs/preregistration-p1-episode.md` — 事前宣言文書
- `src-tauri/prereg/p1-episode.json` — 凍結 JSON（**値の SSOT**）
- `scripts/check_prereg_parity.py` — 文書↔JSON の一致検査（★ 陽性対照つき）
- `scripts/run-features-all-poles.sh` — **3 極を必ず回す**（判断 3 のトレードオフ「実行漏れ」への手当て）
- fixture: 30 秒窓で `p50 != max` になるもの ／ 多 onset のもの ／ 修飾キー押下区間を持つもの ／
  `pointer_bin` を持つもの

## 影響範囲

| 何 | 影響 | 対処 |
|---|---|---|
| `--features` の**行の形** | ★ `stall_onset` に `theta_sample_n` / `ime_overlap` が**増える** | ⚠️ 既存 acceptance はキー集合を見るものがある → **同時に更新**する |
| `--features` の**封筒** | `config` のキーが増える | ★ 追加のみ。既存キーは変えない |
| `provenance.observed_intervals` | ⚠️ **極 B で変わる** | ★ doc に明記。極は `config.pole` から読める |
| ゴールデン（`--snapshot`） | ⚠️ **影響しない** | ★ `--features` は `features.rs` / `engine.rs` を経由しない独立経路（D1・`replay.rs:1290` 逐語）。⚠️ `features.rs` の**命名リファクタは振る舞いを変えない**ので、ゴールデンが動いたらリファクタが失敗している |
| `HMM_VERSION` | ⚠️ **bump しない** | ★ 上と同じ理由。⚠️ ただし `features.rs` を触るので、**ゴールデン 15 本が byte-equal であること**を毎 issue で確かめる |
| schema parity | ⚠️ **影響しない** | ★ `schema_dto.rs` を触らない（⚠️ 触るなら `emit_schema` と gse-dataset 側を同時に） |
| `--metrics` / `--snapshot` / `--calibration` | ⚠️ **影響しない** | ★ `KeyPress` を変えない（上記 (1)） |
| 実行時間 | ⚠️ collector が 2 本増え、**極ごとに 3 回**回す | ★ 起票 21 の門を 1 極あたりで置く |

## 既存パターンとの整合性

- collector: `collect_all_feat_timestamps` / `collect_all_ime_shadow_events`（**専用 DTO ＋ 1 パス ＋
  形の合わない行は捨てて件数だけ `warn`**）に揃える。⚠️ **0 に畳まない**。
- 封筒: `FeatureConfigDto::from_stall_onset_config` の形を保ち、**設定と結果を同じ箱に入れない**
  （⚠️ `theta_person_ms` / `theta_sample_n` は**行**が持つ・ADR-030 D4）。
- 一致検査: `scripts/check_schema_parity.py` の作法。
- 定数: ⚠️ **`analysis/` に新しい数値定数を置かない**（★ 上限値は `bin/replay.rs` が所有する既存規律）。

## テスト戦略

- **単体テスト**（`cargo test --workspace`・`src-tauri/` から実行）:
  - 押下区間のカウント方式（入れ子 / 孤立 release / 閉じない押下）
  - 抑制区間の合成（★ 観測区間と抑制区間の境界がちょうど一致する場合）
  - 30 秒窓で `p50 != max` になること（⚠️ **同値のままなら窓が効いていない**）
  - `--set` の fail-closed（未知キー / 型不一致 / 範囲外）
  - 最小幅の**陽性対照**（定数を逆転させたら赤）
  - 極 M+ が `−1` を外さないこと（⚠️ `Ctrl+Backspace` の陰性対照）
- **acceptance**（`00X-acceptance.sh`）: 各 issue の AC に 1 対 1 で対応させる。
- **回帰**: ゴールデン 15 本が **byte-equal**（★ `gse-replay --snapshot`）。
- ⚠️★★★ **「検査の検査」5 点を必ず通す**（★ 起票 23 のセッションで 3 件がテスト緑のまま潜んだ）:
  1. `$( )` の中の `die` / `exit` は**サブシェルしか抜けない** → fail-closed が fail-open に化ける
  2. `grep -c … || echo 0` は **"0" を 2 行**出す → `[` が壊れてガードが素通りする
  3. 変異ガードは「元の形が消えた」だけでは足りない → **src に 1 件 / mut に 0 件**を両方見る
  4. ⚠️ **判定式が常に真になっていないか** —— ★ **ok と ng の両枝が実際に取られるか**を変異で確かめる
  5. ⚠️ 語で一致させるときは「**その語が別の理由でも出ないか**」を確かめる → **die メッセージの固有の語**で固定する
- ⚠️ **「準備できなかった」が出たら、検査が飛んでいないかを必ず確かめる**。

## ロールバック計画

- 各 issue は **1 論理単位 1 コミット**・`[type]([scope]): [説明]` ＋ `Refs:`。
  → 問題が出たら **その issue のコミットだけ revert** できる。
- ⚠️★★★ **凍結 JSON と文書は例外** —— ★ 凍結は**不可逆**なので、revert ではなく
  **新しい版を切って理由を書く**（★ `preregistration-v0.3.md` の凍結規約と同じ作法）。
- ⚠️ `docs/adr/` の補訂 2 も**書き換えない**（★ 誤りが見つかったら補訂 3 を足す）。
