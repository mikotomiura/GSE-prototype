# Offline replay capability matrix — 現行 schema だけで T0/T1 をどこまで作れるか

- **作成**: 2026-09-21（`.steering/20260921-capability-matrix/`）
- **出所**: `ADR-032 D5` 逐語「★ **GSE の現行 schema だけで T0/T1 のどこまで offline replay できるか
  capability matrix を作る**」（★ `ADR-032 §Migration` の **M7**）
- **実証範囲**: `.steering/20260914-mhd-feature-offline-tiers/decisions.md` **判断 5（採用 A）** ——
  **現行 schema の静的分析 ＋ 既存 fixture での実測 replay ＋ 起票 6 の既測結果の引用**
- **見直しタイミング**: ★ **O1 の実データが届いたとき**（判断 5）

---

## ⚠️★★★ 最初に固定する —— この表が **主張していないこと**

| # | ★ この表が言うこと | ⚠️ この表が言わないこと |
|---|---|---|
| 1 | ★ **現行の NDJSON schema と `feat_offline/` の実装で、いま何が出ているか** | ⚠️ その量が **妥当** であること（★ criterion validity は O1 の仕事） |
| 2 | ★ **合成 fixture 上で実際に replay して確かめた結果** | ⚠️★★★ **実データでもそうなること**（★ **O1 は未配布で実データが 1 本も無い**） |
| 3 | ★ 作れないもの・粒度が足りないものを**名指しする** | ⚠️ 足すべきフィールドを**決めること**（★ 裁定は別文書） |
| 4 | ★ OS とライブ変換設定で**壊れ方が違う**こと | ⚠️ どちらが「正しい」か（★ 両方とも実装どおりに動いている） |

⚠️★★★ **すべての判定は「合成 fixture 上の判定」である。**
★ 実データでの再判定が要る項目には **`要再判定`** と書いた（→ §6）。

---

## 1. 読み方

### 1.1 判定の 3 値（`ADR-032 D5` 逐語）

| 判定 | 意味 | ★ 次に何をするか（`ADR-032 D5` の表） |
|---|---|---|
| ✅ **作れる** | 現行 schema に送出元があり、`feat_offline/` が実際に値を出している | ★ **schema を足さない**（⚠️ `T1b` として `gse-replay` に入れる） |
| ❌ **作れない** | 現行 schema に **送出元が無い** | ★ **別 ADR を起こす**（⚠️ 門は中身で分かれる → §7） |
| ⚠️ **粒度が足りない** | 行は出るが、**意味が壊れている / 単位が合っていない** | 同上（★ ただし「足す」以外に「読み方を凍結する」解もある） |

### 1.2 Tier の呼び名（`docs/glossary.md` の「Tier のブロック名」）

`T0`=activity ／ `T1a`=dispersion ／ `T1b`=boundary ／
`T1c`=**削除と挿入の遷移の形**（⚠️ 旧「revision topology」は**呼び名として使わない** —— ADR-030 補訂 1 項目 9）／
`T1d`=restart ／ `Q`=evidence quality。

⚠️ **`T2`（cross-channel）は本表の対象外** —— ★ `ADR-032 D3`（② 元 app 回帰は**解かない**）と
**D4**（③ domain-local events は**内容未定義のため不採**）が**裁定済み**である。

---

## 2. ⚠️★★★ 層別の軸 —— そして **層を識別できない**という事実

`ADR-032 D5` は「**`OS × ライブ変換設定` で層別する**（⚠️ 1 つの表に畳まない）」と命じている。
★ 層は 3 つになる:

| 層 | 中身 |
|---|---|
| **W** | Windows |
| **M-off** | macOS ／ ライブ変換 **OFF** |
| **M-on** | macOS ／ ライブ変換 **ON**（⚠️★★★ **macOS の既定**） |

### ⚠️★★★ ところが **解析時に層を割り当てられない**（★ 本表の最大の発見）

★ 2026-09-21 に一次で確かめた:

| 何 | 実測 |
|---|---|
| `meta` 行が持つ環境情報 | `app_version` / `capabilities` / `g1_mode` / `hmm_version` / `keyboard_layout` / `o1_mode` / `session_start` / `session_end` の **8 つだけ**（`src-tauri/schema/current.json`） |
| ライブ変換の状態 | ⚠️ **1 フィールドも無い** |
| OS 由来の設定ファイル | ⚠️ 起票 6 逐語「`defaults` には **`LiveConversion` のキーが全 domain に存在しない**（既定値のまま）ので、★ **設定ファイルからは判定できない**。UI か挙動で見るしかない」 |

→ ⚠️★★★ **`M-off` と `M-on` は、受け取った NDJSON からは区別できない。**
★ しかも **実装の出力は ON / OFF で完全に同一**である（起票 6 実測・4 行 `true,false,true,false`）。
→ ★★★ **層別は「概念として分ける」ことはできるが、「データを分ける」ことはできない。**

⚠️ これは表の**読み方そのもの**に効く: ★ macOS のセッションは
**`M-on` の壊れ方を負っている可能性を常に持つ**（★ ON が既定なので、むしろそれが既定の条件である）。
→ ★ 本表では macOS の行を **`M-on` 側の最悪値で読む**ことを既定にし、`M-off` は参考として併記する。

---

## 3. 表 A — `T0` / `T1a`（層で壊れない Tier）

★ `T0` と `T1a` は **`key` 行と `paste` 行だけ**から作る。
⚠️ したがって **IME のライブ変換設定では壊れない**。★ 層で違うのは **修飾キーの扱い**だけである（→ 3.3）。

| `.idea/survey §6.1` の候補 | 実装フィールド | **W** | **M-off** | **M-on** | 根拠 |
|---|---|---|---|---|---|
| keys | `activity.keys` | ✅ | ✅ | ✅ | `feat_offline/activity.rs` |
| delete | `activity.deletes` | ✅ | ✅ | ✅ | 同上 |
| paste | `activity.pastes` | ✅ | ✅ | ✅ | `paste` 行（`external_paste_chars`） |
| mean IKI | `activity.mean_iki_ms` | ✅ | ✅ | ✅ | ⚠️ 間隔が無い tick は `null`（0 で埋めない） |
| 単純 pause | `activity.pauses` | ✅ | ✅ | ✅ | `features.rs::PAUSE_THRESHOLD_MS` を再利用 |
| **net production** | `activity.net_production` | ✅ | ⚠️ **粒度が足りない** | ⚠️ **粒度が足りない** | ★ **3.3 を参照** |
| p50 / p90 / max | `dispersion.pause_p50_ms` ほか | ✅ | ✅ | ✅ | `feat_offline/dispersion.rs` |
| CV | `dispersion.iki_cv` | ✅ | ✅ | ✅ | 同上 |
| **混合成分** | —— | ❌ | ❌ | ❌ | ★ **実装が無い**（`dispersion.rs` に該当フィールド無し） |
| **本人の task/phase baseline からの surprise** | `dispersion.surprise` | ⚠️ **粒度が足りない** | ⚠️ | ⚠️ | ★ **3.2 を参照** |

### 3.1 ⚠️ 前提: **`feat` 行だけのセッションからは 1 行も作れない**（★ 実測）

★ `--features` の tick グリッドの**原点は入力チャネル（press / paste / `ime_shadow`）だけ**で決まる
（`feat_offline/mod.rs` の「tick への帰属規則」）。

★ 2026-09-21 の実測（`tests/fixtures/phase1_ime_heavy.ndjson`）:

```text
行種内訳: feat 96 / ime_state 6 / user_label 6 / meta 2 / session_start 1   (★ key 0 / paste 0)
$ gse-replay tests/fixtures/phase1_ime_heavy.ndjson --features
→ rows = 0        (⚠️ observed_intervals は 1 区間・約 95 秒あるのに)
```

→ ⚠️★★★ **`feat` 行（＝ 推論結果）が 96 本あっても、生の入力が無ければ Tier は 1 行も作れない。**
★ これは「replay できる」の**前提条件**であり、層に依らない。

### 3.2 ⚠️ `surprise` は **task/phase baseline ではない**

★ `.idea/survey §6.1` の候補は逐語「**本人の task/phase baseline からの surprise**」である。
⚠️ 実装（`dispersion.rs` の `SessionIkiBaseline`）が取るのは **セッション全体の IKI baseline** であり、
★ **task 別・phase 別ではない**。
→ ⚠️ **粒度が足りない**（★ `session_meta.task_kind` は行として在るので、**分けること自体は将来できる**）。

### 3.3 ⚠️★★★ `net_production` は **macOS で系統的に過大**（★ 層が効く唯一の `T0` 項目）

★ `ADR-030 D3` の規則は逐語「**修飾キーが押されている間の文字キーは挿入系に数えない**」。
⚠️ ところが macOS では**修飾キーが 1 行も届かない**（★ `hook_macos.rs` 逐語
「**修飾キーは macOS では届かない**（★ tap の mask が `KeyDown`/`KeyUp` だけ）。★ **届かないので観測集合にも入れない。**」）。

→ ★★★ **macOS では `Cmd+Z` / `Cmd+X` / `Cmd+A` / `Cmd+S` が「挿入系の産出 +1」として数えられる**（起票 19）。
⚠️ 差し引けるのは **`Cmd+V` だけ**（★ `paste` 行が別に出るため）。

- ★ **W**: 規則を実行できる（`GetAsyncKeyState(VK_CONTROL)`）→ ✅
- ⚠️ **M-off / M-on**: **規則が実行できない** → ⚠️ **粒度が足りない**
- ★ **是正の予定**: `ADR-032 D9`（`key` 行に `Ctrl`/`Cmd` 押下の 1 ビット）。
  ⚠️ **本表の時点では未実装**（★ `ADR-032` は **Proposed**・`M5` は Accepted 後）。

---

## 4. 表 B — `T1b`（境界）: ★ **ここで層が割れる**

| `.idea/survey §6.1` の候補 | 実装フィールド | **W** | **M-off** | **M-on** | 根拠 |
|---|---|---|---|---|---|
| 直前 / 直後 key category | `boundary.prev_cat_counts` / `next_cat_counts` | ✅ | ✅ | ✅ | `feat_offline/boundary.rs` |
| Space / Enter / punctuation | `boundary.space` / `enter` / `sentence_punctuation` | ✅ | ✅ | ✅ | 同上 |
| **IME composition / commit** | `boundary.ime_dwell_ms` / `ime_nav` / `ime_abandon` | ⚠️ **粒度が足りない** ＋ ❌ **丸ごと出ないことがある** | ⚠️ **粒度が足りない** | ⚠️★★★ **粒度が足りない（意味が壊れる）** | ★ **4.1 〜 4.3** |

### 4.1 ⚠️★★★ `ime_shadow` の **駆動源が OS で違う**（★ `input/ime_compose.rs` モジュール doc 逐語）

|  | **Windows** | **macOS** |
|---|---|---|
| `dwell_ms` の由来 | **窓イベント**（`EVENT_OBJECT_IME_*` / DWM cloak） | ★ **打鍵**（最初の英数字キー 〜 終端キー） |
| `nav` / `abandon` | 打鍵推論 | 打鍵推論（★ **同型**） |
| **1 行になる変換** | 候補ウィンドウが出たもの | ★ かな入力の**一区切りすべて**（⚠️ Space を一度も押さなくても 1 行） |
| `nav` を数える区間 | `IME_ACTIVE` 中 | ★ 変換セッション全体 |
| `abandon` に入るもの | 候補表示中の ESC | ★ 候補を出さずに捨てた ESC も入る |

→ ⚠️★★★ 逐語「**`abandon` 率を OS 間で直接比べてはならない**」。
★ `ADR-032 D6` はこれを**解析上の制約として凍結**した（⚠️ 同じ macOS の**設定間**でも比べない）。

### 4.2 ❌ **Windows では `ime_shadow` が丸ごと出ないことがある**（★ 実機計測）

★ `capabilities.rs` 逐語（2026-08-22 の実機計測 `examples/ime_winevent_probe.rs`）:

> ⚠️★★★ **`EVENT_OBJECT_IME_SHOW/HIDE/CHANGE`(0x8027-0x8029) が 60 秒間 1 件も飛ばない**
> —— 同じ時間に `TEXTSELECTIONCHANGED` 298 件・`VALUECHANGE` 246 件・`CREATE`/`DESTROY` 各 680 件が飛んでおり、
> **日本語入力は確かに行われていた**。

→ ★ だから `ime_shadow` は `capabilities` 上 **`config_gated`** に置かれている
（⚠️ **0 行は「信号が無かった」ではなく「判定不能」**）。
★ cloak/uncloak 経路のフォールバックはあるが、⚠️ **環境（IME / アプリ）次第で 0 行になりうる**。

### 4.3 ⚠️★★★ `M-on`（macOS の既定）は **意味が壊れる**（起票 6・2026-09-12 実機）

| ライブ変換 | ESC 1 回 | ESC 2 回 |
|---|---|---|
| **OFF** | 合成が消える ＝ **放棄** | （もう合成が無い） |
| **ON（★ 既定）** | ⚠️★★★ **読みに戻るだけ。合成は続く** | 合成が消える ＝ 放棄 |

⚠️ 実装は **ON / OFF のどちらでも「最初の ESC で `abandon=true`」**を出す。
→ ★★★ **1 回の確定が `放棄 1 ＋ 確定 1` の 2 行に割れる**（★ 起票 6 の実測表）。

→ ⚠️ 帰結は 2 つ:
1. ★ **`abandon` は放棄率として読めない**（`ADR-032 D6`）。
2. ⚠️★★★ **`ime_shadow` の行数が「変換回数」の代理にならない**（★ 分母が割れる）。
   → ★ `dwell_ms` の分布も割れる。

### 4.4 ⚠️ macOS の `dwell_ms` は **1 変換とは限らない**（起票 7・★ 直せない限界）

★ 終端を観測できない確定（**マウスで候補をクリック** / **数字キーで確定**）は
⚠️ **次の変換と合算される**（`dwell_ms` が 2 つ以上の変換を覆う）。
★ 20 秒を超えた変換は `MAX_SESSION_MS` で打ち切り、⚠️ **行を出さない**。
⚠️ 時計の巻き戻しで **`dwell_ms == 0`** の行が出る（★ 解析側は実測値として扱わない）。

### 4.5 ⚠️ `ime_state` は **offline Tier が読んでいない**

★ 2026-09-21 に grep で実測: `feat_offline/` に `ime_state` の参照は **0 件**。
★ `ime_state{t, on, active}` は `gse-replay` の **HMM 再実行経路**（`step()` の `ime_open` 引数）でだけ使われる。
→ ⚠️ 「IME の on/active は記録されている」ことは **`T1b` の材料になっていない**。

---

## 5. 表 C — `T1c`（削除と挿入の遷移の形） / `T1d`（restart） / `Q`

| Tier | `.idea/survey §6.1` の候補 | 実装フィールド | **W** | **M-off** | **M-on** |
|---|---|---|---|---|---|
| T1c | delete run | `revision.delete_run_max` / `delete_runs` | ✅ | ✅ | ✅ |
| T1c | rewrite | `revision.del_to_ins_transitions` | ✅ | ✅ | ✅ |
| T1c | 再削除 | `revision.delete_runs_after_first_in_burst` | ✅ | ✅ | ✅ |
| T1c | loop depth | `revision.di_alternations_max` | ✅ | ✅ | ✅ |
| T1c | 局所 recurrence | `revision.category_bigram_repeat_rate` | ✅ | ✅ | ✅ |
| T1c | **undo / redo 往復** | —— | ❌ **作れない** | ❌ | ❌ |
| T1d | pause 後の生成 / 削除 / 移動 | `restart.post_t0_inserts` / `post_t0_deletes` / `post_t0_navigations` | ✅ | ✅ | ✅ |
| T1d | 再停止時間 | `restart.restop_ms` | ✅ | ✅ | ✅ |
| T1d | 安定生成時間 | `restart.stable_generation_ms` | ✅ | ✅ | ✅ |
| T1d | **rhythm 回復** | —— | ❌ **作れない** | ❌ | ❌ |
| Q | capability | `quality.missing_reasons` の `capability_undeclared` ＋ 封筒の `provenance.capabilities` | ✅ | ✅ | ✅ |
| Q | missingness reason | `quality.missing_reasons` | ✅ | ✅ | ✅ |
| Q | logger health | `quality.hook_health` | ✅ | ✅ | ✅ |
| Q | **IME health** | —— | ⚠️ **粒度が足りない** | ⚠️ | ⚠️ |
| Q | observability mask | `quality.observability_mask{feat, hook}` | ✅ | ✅ | ✅ |

### 5.1 ❌ `undo` / `redo` は **現行 schema に送出元が無い**

★ `key` 行は `KeyCategory`（**14 種**）に量子化されており、⚠️ `Z` / `Y` を識別できない。
★ 解禁の裁定は **`ADR-032 D1`**（★ `paste` と同型の別行種として additive に足す）だが、
⚠️ **ADR-032 は Proposed** で、★ **`M5`（実装）は Accepted 後**である。
→ ★ したがって本表の時点では **❌ 作れない**。

⚠️ ★ ただし `ADR-032 Context-3` 逐語のとおり、**修飾キー併用打鍵の *存在と時刻* は Windows では既に取れている**
（`key` 行の press/release から復元できる）。★ 取れていないのは「その文字キーが `Z` / `Y` か」だけである。
⚠️ **macOS では存在すら取れない**（→ 3.3）。

### 5.2 ❌ 「rhythm 回復」は **操作定義が無い**

★ `restart` は `post_t0_*` / `restop_ms` / `stable_generation_ms` /
`stable_generation_net_presses` / `resumption_count` の **7 フィールド**を持つが、
⚠️ 「**通常 rhythm への回復時間**」に当たるフィールドは無い。
→ ★ これは **schema の不足ではなく定義の不在**である（⚠️ 「何をもって通常 rhythm とするか」が未定義）。
★ `ADR-009` の `ContextBuilder` は **Proposed かつ未実装**（★ 2026-09-21 に `grep -rn progress_proxy src-tauri/src/` で再確認済み）。

### 5.3 ⚠️ `Q` の「IME health」だけが粒度不足

★ `hook_health{alive, starved_ms, rehook, dropped_delta}` は**キーボードフックの健全性**である。
⚠️ **`ime_shadow` が出ていないのが「変換が無かった」からか「計器が効いていない」からか**は、
★ `capabilities` の `config_gated` 宣言で**「判定不能」と読む**ことしかできない（→ 4.2）。
→ ⚠️ **tick 単位の IME 可観測性マスクは無い**（★ `observability_mask` は `feat` と `hook` の 2 つだけ）。

---

## 6. `.idea/survey §6.3` の **IME 優先候補 9 個**（★ `ADR-032 D5` の本題）

★ §6.3 逐語の優先候補: **composition duration / 内部 delete / commit latency / commit-to-next gap /
retry 数 / commit 直後の削除 / abandon 候補 / 通常 rhythm への回復時間 / 本人 baseline からの偏差**。

### 6.1 ⚠️★★★ 先に固定する —— **合成中の打鍵は `key` 行として出ている**（★ 2026-09-21 に一次で確認）

★ `ADR-032 Context-2(b)` は「作れる見込み」と書いたが、**その前提を一次で確かめていなかった**。
★ 本表で確かめた:

| 何 | 実測（一次） |
|---|---|
| Escape は記録されるか | ✅ **両 OS で記録される** —— W: `hook_windows.rs::is_observed_key` に `0x1B` ／ M: `hook_macos.rs::is_observed_key` に `0x35`（→ `0x1B` へ写像） |
| 匿名化後も残るか | ✅ `KeyCategory::from_vk(0x1B) => Escape`（`anonymize.rs`）。★ `"escape"` として `key` 行に出る |
| Backspace は | ✅ `0x08 => Backspace`（★ 独立カテゴリ。`Other` に畳まれない） |
| ⚠️ **合成中の Backspace はセッションを閉じるか** | ★ **閉じない** —— `ime_compose.rs` 逐語「Backspace — 候補表示から抜けてインライン編集へ戻る。⚠️ **セッションは続く**」 |
| Space は | ✅ `0x20 => Space`。★ macOS では Space が `active = true`（＝ **変換の開始**）を立てる |
| `feat_offline` は `category` を読めるか | ✅ `replay.rs` の `key` DTO は `vk` と `category` の **両対応**（逐語「replay は **両対応**で同じ特徴量を再計算する」） |

→ ★★★ **`ime_shadow` の区間 `[t − dwell_ms, t]` と `key` 行を突き合わせれば、
合成中の Backspace・Space・Escape を *区間へ帰属させられる*。**
⚠️ ただし **区間の端の精度**（→ #4 の但し書き）と **M-on の分裂**（→ 4.3）が乗る。

### 6.2 判定表

| # | 候補 | **W** | **M-off** | **M-on** | ★ 根拠 / ⚠️ 但し書き |
|---|---|---|---|---|---|
| 1 | composition duration | ⚠️ 粒度が足りない **`要再判定`** | ⚠️ 粒度が足りない | ⚠️★★★ 粒度が足りない | ★ `ime_shadow.dwell_ms` が在る。⚠️ W = 候補窓が出た変換だけ・**0 行になりうる**（4.2）／ M = **1 行が複数変換を覆う**（4.4）／ M-on = **1 確定が 2 行に割れる**（4.3） |
| 2 | **composition 内部の delete** | ⚠️ 粒度が足りない **`要再判定`** | ⚠️ 粒度が足りない **`要再判定`** | ⚠️★★★ 粒度が足りない | ★★★ **`ADR-032 D5` の見立て（「今期は持たない」）より一段良い** —— ★ 6.1 のとおり **合成中の Backspace は `key` 行に出ており、区間へ帰属させられる**。⚠️ **新フィールドは要らない**。⚠️ ただし**データで作ってはいない**（★ `ime_shadow` を持つ fixture が 1 本 2 行しかない） |
| 3 | **commit latency**（変換開始 → 確定の分離） | ⚠️ 粒度が足りない | ⚠️ 粒度が足りない | ❌ **構成概念が成立しない** | ★ M-off では **区間内の最初の `space`** が変換開始の代理になる（`ime_compose.rs` が Space で `active` を立てる）。⚠️★★★ **M-on では Space を押さずに変換が進む**ので、★ **「変換開始」という離散的な時点が存在しない**（起票 6）。⚠️ W は `dwell_ms` 自体が候補窓の寿命なので、★ **開始の代理が別物**になる |
| 4 | commit-to-next gap | ⚠️ 粒度が足りない **`要再判定`** | ⚠️ | ⚠️ | ★ `ime_shadow.t` ＋ 次の `key` 行で作れる（`ADR-032 Context-2(b)`）。⚠️★★★ **`t` は確定時刻ではない** —— W は **IME Monitor スレッドの `SystemTime::now()`**（★ `sleep(100ms)` のポーリング）であり、★ **誤差 ≤ 100ms が gap に乗る**。⚠️ M は終端キーの時刻なので誤差は小さいが、★ **終端を観測できない確定がある**（4.4） |
| 5 | retry 数 | ⚠️ 粒度が足りない | ⚠️ | ⚠️ | ★ `ime_shadow.nav` が**代理になりうる**（`ADR-032 Context-2(b)`）。⚠️ 母数が OS で違う（4.1）ので **回数の意味が層をまたいで一致しない**。★ 区間内の `navigation` カテゴリ打鍵からも数えられるが、⚠️ **同じ矢印キーが候補選択か本文移動かを区別できない** |
| 6 | commit 直後の削除 | ⚠️ 粒度が足りない **`要再判定`** | ⚠️ | ⚠️ | ★ `ime_shadow.t` の**直後**の `key`(`backspace`) で作れる。⚠️ #4 と同じ時刻精度の制約 ／ ⚠️ M-on では**「確定」の同定自体が割れる**（4.3） |
| 7 | abandon 候補 | ⚠️ 粒度が足りない | ⚠️ 粒度が足りない | ❌ **意味が壊れる** | ⚠️★★★ `ADR-032 D6` が「**`abandon` を放棄率として読まない**」を凍結した。★ M-on では**確定操作が放棄として立つ**（起票 6）。★ **6.3 を参照** —— ⚠️ ESC の生の回数は別に取れる |
| 8 | 通常 rhythm への回復時間 | ❌ **作れない** | ❌ | ❌ | ★ **定義が無い**（→ 5.2）。⚠️ **schema の不足ではない**（★ 足しても解けない） |
| 9 | 本人 baseline からの偏差 | ⚠️ 粒度が足りない | ⚠️ | ⚠️ | ★ `dispersion.surprise` が在るが **セッション全体 baseline**（→ 3.2）。⚠️ **IME 量に対する baseline は実装が無い**（★ 作るのは集計の仕事で、schema の仕事ではない） |

→ ★★★ **9 個の内訳**: ✅ 作れる **0 個** ／ ❌ 作れない **1 個**（#8）＋ **層限定の ❌ 2 件**（#3 / #7 の M-on）
／ ⚠️ 粒度が足りない **8 個**。
⚠️★★★ **「schema にフィールドを足さないと作れない」ものは 1 つも無かった。**
★ 足りないのは **(a) 区間の端の精度**（W の 100ms ／ M の観測できない終端）と
**(b) M-on で構成概念そのものが崩れること**であり、⚠️ **どちらもフィールド追加では解けない。**

### 6.3 ⚠️★★★ `esc_count`（ADR-032 未決 ⑤）は **現行 schema で既に取れる**

★ 起票 6 の対処案 2 は逐語「ESC を**終端にせず** `esc_count` として数え、放棄の判定を解析側へ委ねる
（⚠️ schema にフィールド追加 ＝ ADR-005 の additive versioning）」だった。

⚠️★★★ **フィールド追加は要らない。** ★ 2026-09-21 に一次で確かめた:

- ★ ESC は **両 OS で `key` 行として記録される**（6.1 の表）。
- ★ 匿名化後も **`category: "escape"`** として残る（⚠️ `Other` に畳まれない）。
- → ★★★ **`esc_count` ＝ 窓内の `key` 行のうち `category == "escape"` かつ `press == true` の件数**。
  ⚠️ **`ime_shadow` の区間に依存しないので、M-on で区間が割れても数は壊れない。**

★ これは `ADR-032 D6` が却下した 2 案（ESC 2 回で閉じる / `esc_count` 化）の**うち後者を、
schema を動かさずに満たす**ことを意味する。
⚠️ ただし **`ime_shadow.abandon` の意味は直らない**（★ D6 の凍結はそのまま要る）。

⚠️ **1 件だけ fixture に実在する**: `category_coverage.ndjson` が `vk: 27` を 2 件持つ（★ 2026-09-21 実測）。
★ 他の 14 本には 1 件も無い → **`要再判定`**（⚠️ 実データでの出現頻度は未知）。

---

## 7. 根拠 —— ⚠️★★★ **実証の土台がどれだけ薄いか**

### 7.1 fixture の実測（2026-09-21・`src-tauri/tests/fixtures/*.ndjson` **15 本**）

⚠️★★★ **`ime_shadow` を持つ fixture は 1 本だけ（`instrument_rich`・2 行）である。**

| fixture | key | paste | **ime_shadow** | ime_state | feat | hook_health |
|---|---|---|---|---|---|---|
| `instrument_rich` | 48 | 1 | **2** | 5 | 0 | 2 |
| `argumentative_ime_mixed` | 244 | 0 | **0** | 3 | 0 | 0 |
| `vibe_coding_ime_mixed` | 244 | 0 | **0** | 3 | 0 | 0 |
| `phase1_ime_heavy` | 0 | 0 | **0** | 6 | 96 | 0 |
| `stall_onset_observed` | 706 | 0 | 0 | 0 | 220 | 0 |
| `minimal` / `minimal.anon` | 26 | 1 | 0 | 1 | 0 | 0 |
| （他 8 本） | … | … | **0** | … | … | 0 |

⚠️★★★ **名前に反して `*_ime_mixed` / `phase1_ime_heavy` は `ime_shadow` を 1 行も持たない**
（★ 持っているのは `ime_state` だけで、⚠️ それは `feat_offline` が**読まない** —— 4.5）。

★ 併せて **`focus_transition` / `pointer_bin` / `secure_input` / `starve_window` / `recording_pause` は
15 本すべてで 0 行**である。

### 7.2 `--features` の非 null 率（★ 実測）

- `restart` の 7 フィールドが非 null になるのは `stall_onset_observed` だけ（**2 / 220 行**）。
  ★ そのうち `restop_ms` は **1 / 220** —— ⚠️ もう 1 件は**右側打ち切り**である。
- `hook_health` が非 null なのは `instrument_rich` だけ（**2 / 15 行**）。
- `boundary.ime_*` が非ゼロなのは `instrument_rich` だけ（**dwell 2 / nav 2 / abandon 1**）。

### 7.3 ⚠️★★★ したがって **`要再判定` の範囲**

★ 本表の IME 行（表 B ＋ §6 の 9 個）は、**合成 fixture 2 行の上での判定**である。
→ ⚠️ **「粒度が足りない」は実データで確かめ直すまで確定ではない。**
★ 次の 6 つは **O1 の実データが届いたときに必ず再判定する**:

1. #1 composition duration —— ★ 実際の `dwell_ms` 分布（⚠️ W で 0 行になる頻度も）
2. #2 composition 内部の delete —— ★ **導出は示したが、データで作っていない**
   （⚠️ `ime_shadow` を持つ fixture が **1 本 2 行**しかない）
3. #4 commit-to-next gap —— ★ **100ms 量子化が実データの gap 分布に対して無視できるか**
4. #6 commit 直後の削除 —— ★ 同上 ＋ M-on の分裂の実頻度
5. `esc_count` —— ★ **実データでの出現頻度**（⚠️ 15 本中 1 本に 2 件しか無い）
6. ⚠️ **W で `ime_shadow` が 0 行になる被験者の割合**（★ 4.2 の実機計測は **1 台・60 秒**）

---

## 8. この表が閉じるもの / 閉じないもの

### ★ 閉じるもの

- ★ `ADR-032 D5` が要求した **`OS × ライブ変換設定` の層別 3 値判定**（→ §3〜§6）。
- ★ `.idea/survey §6.3` の 9 候補に **すべて判定が付いた**（→ 6.2）。
- ★★★ **「schema にフィールドを足さないと作れない」ものは 9 個の中に 1 つも無い**（→ 6.2）。
- ★★★ **`esc_count`（未決 ⑤）は現行 schema で既に取れる**（→ 6.3）。⚠️ 追加は要らない。
- ★★★ **層を識別できない**という設計上の事実（→ §2）。
  ⚠️ **これは `ADR-032 D5` が想定していなかった制約である。**

### ⚠️ 閉じないもの（★ 隠さない）

- ⚠️ **実データでの妥当性**（★ O1 未配布。判定はすべて**合成 fixture 上**）。
- ⚠️ **#2 / #4 / #6 は「導出を示した」までで、データで作っていない**（★ `要再判定`）。
- ⚠️ **M-on で構成概念が崩れること**（#3 / #7）は、★ **フィールドを足しても解けない**。
  → ⚠️ 解けるとすれば「**ライブ変換の状態を層の識別子として記録する**」形だが、
  ★ それは `ADR-014 D4` の禁止表・`ADR-032 D2` の門に**当てる必要がある**（⚠️ 本表は裁定しない）。
- ⚠️ **裁定そのもの**（未決 ④ / ⑤ ／ `M11` 単独キー用の門）—— ★ 本表は**材料までである**。

---

## 9. 関連

| 文書 | 何が書いてあるか |
|---|---|
| ★ **`docs/adr/ADR-036-ime-capability-arbitration-and-single-key-gate.md`** | ★★★ **本表を受けた裁定**（**D1** ④ は schema を足さない ／ **D2** `esc_count` は派生量 ／ **D3** 単独キー用の門 ／ **D5** `F5` は通らない） |
| `docs/adr/ADR-032-instrument-change-arbitration.md` | **D5**（本表の発注）／ **D6**（`abandon` の凍結）／ **D2**（修飾キー併用の 9 条件）／ **M7 / M11** |
| `docs/adr/ADR-030-stall-onset-and-decision-episode.md` | **D3**（産出の計算規則）／ **D10**（Tier 枠と投資順序） |
| `.steering/20260911-outcome-arbitration-and-o1-preflight/blockers.md` | **起票 6**（macOS ライブ変換の実機実測）／ **起票 7**（`dwell_ms` が複数変換を覆う） |
| `.steering/20260914-instrument-change-arbitration/blockers.md` | **起票 19**（macOS で修飾キーが届かない）／ **起票 21**（単独キー用の門が無い） |
| `src-tauri/src/input/ime_compose.rs` | ★ OS 非対称の一次（モジュール doc の 2 つの表） |
| `src-tauri/src/capabilities.rs` | ★ `config_gated` の理由（⚠️ 0 行は判定不能） |
| `src-tauri/src/analysis/feat_offline/` | ★ 実装の一次（7 モジュール） |

★ 先行研究の対比: ⚠️ **content-full な keylogger は IME 変換過程を記録できている**
（Translog-II は `Type="IME"` / `IMEtext` を残す [P359]、ENJA15 の生ログでも確認されている [P360]）。
★ GSE が持たないのは **能力ではなく content-free 制約の帰結**である
（⚠️ [P273] の公開データは content-full の統制翻訳データであり、★ **GSE の criterion validity は示せない**）。
