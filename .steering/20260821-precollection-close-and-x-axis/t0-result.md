# T-0 実測 — `starve_window` の陽性対照 (2026-08-21)

⚠️ **生 NDJSON は repo に置かない** (`data-privacy`)。★ 以下は**値だけ**の転記である。

## ★ 結果: **発火した** (⚠️ 初観測)

★ これで `20260819-g1-reboot-and-instrument-fix/code-review.md` の最後の 1 行
「⚠️ **`starve_window` の実発火は依然として未観測**」が**閉じた**。

## ★ 実行条件

| 項目 | 値 |
|---|---|
| 実行日時 | 2026-08-21 03:30:35 〜 03:31:58 (JST)・**83 秒** |
| `meta.g1_mode` | ⚠️★★★ **`"marker"`** ＝ **配布形と同じ経路** (env フォールバックではない) |
| `meta.app_version` | **`0.1.27`** (★ 収集開始の前提条件 #1 と同じビルド) |
| `meta.hmm_version` | `0.4.0` |
| OS | Windows 11 |
| 操作 | ★ 打鍵 → **マウスのみ数秒** → キー 1 打、を **5 回**繰り返し、そのまま 60 秒窓を閉じた |

⚠️ ★ ファイル名は `gse_20260820_183006` だが、これは **UTC 由来**である
(`logger.rs:2151 chrono_like_filename()` に「簡易実装のためタイムゾーンは UTC」と明記)。
★ JST の 03:30 は UTC の前日 18:30 —— **ファイル名と `t` は 9 時間ずれて見える**。
⚠️ **既知・仕様であって不具合ではない**が、日付でブロックを突き合わせる解析は
**ファイル名ではなく `t` を見る**こと。

## ★ 実測値

### `starve_window` — **1 行**

| `t` (session_start からの相対) | `win_ms` | `n_lt30` | `sum_lt30_ms` | 1 本あたり |
|---|---|---|---|---|
| **+59.1 s** | **60000** | **3** | 21000 | 7000 ms |

### `hook_health` — **0 行** (★ 対照)

★ **0 行が正しい。** 各エピソードは 7 秒前後で、`log_after_ms = 30_000` に一度も達していない。
→ ⚠️ **2 トラックが閾値できれいに分割されている**ことの実測でもある
(micro 帯は `starve_window`、30 秒以上は `hook_health`)。

### `meta.capabilities` (ADR-013 D1 の自己記述)

| 群 | 値 |
|---|---|
| `unconditional` | `feat` / `ime_shadow` / `ime_state` / `key` / `paste` / `review_marker` / `session_meta` / `session_start` / `user_label` / `vignette_response` |
| ★ `threshold_gated` | **`hook_health` / `starve_window`** |
| `config_gated` | `probe_assignment` / `realtime_label` / `intervention_decision` / `intervention_response` |

### 行種の内訳 (★ 参考)

`key` 312 / `feat` 80 / `ime_shadow` 10 / `ime_state` 8 / `meta` 2 /
`session_start` 1 / `session_meta` 1 / **`starve_window` 1** / `realtime_label` 1

## ★ 受け入れ条件の判定

- [x] NDJSON に `{"type":"starve_window",...}` が **1 行以上**出た → **1 行**
- [x] `n_lt30` が繰り返した回数とおおむね一致する → **3 / 5 回**。
      ⚠️ **下側に偏るのは仕様** (所見 B: 1 Hz 分解能なので 1 秒未満のエピソードは原理的に見えない)。
      ★ 受け入れ幅 3〜5 の下端で合格。
- [x] `win_ms` が 60000 前後 → **60000 ちょうど** (★ 1 秒 tick が揃った ＝ 公称と実測が一致した窓)
- [x] ⚠️ `hook_health` の意味論が変わっていない → **0 行** (30 秒に達していないので期待どおり)
- [x] ⚠️ 生 NDJSON を repo に置かない → 本ファイルは**値のみ**

## ⚠️★★★ この観測が確立したこと (★ 目的に照らす)

`starve_window` は `capabilities.threshold_gated` に属するので、
★ **0 行は「判定不能」としか読めない** —— つまり**計器が壊れていても気づけない**。

→ ★ **配線の鎖が両端まで通っていることを実測で確認した**:

```
フック → CALLBACK_COUNT → liveness::step → MicroStarveWindow::tick
  → LogEntry::StarveWindow → logger → NDJSON の 1 行     ★ 全段通過
```

→ ⚠️ **新コホートで 0 行だったときに「条件未達」と読んでよい根拠ができた**
(★ 以前は「計器不良」と区別できなかった)。

## ⚠️ 副産物として気づいた点 (★ 直さない・`blockers.md` へ)

- ⚠️★★ **G1 モードなのに `realtime_label` が 1 行出た** (`source: "self_marker"`)。
  → `capabilities.rs` の `CONFIG_GATED` は `realtime_label` を
  「G1 実施中は常に止まる」と説明しているが、★ **self-marker 経路は止まっていない**。
  ⚠️ 詳細と「直さない理由」は `blockers.md` を見よ。
