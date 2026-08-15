# ゴールデン再生成の記録（Replay-as-Truth 規約）

> ★ 規約: `docs/development-guidelines.md` §3 ／ `tier0-wiring-design.md` §6。
> **golden 再生成の差分が「新フィールドの追加のみ」でないなら、どこかで推論に混入している。**

## 再生成の手順（1 コマンドで再現できる形）

```bash
cd src-tauri
for g in minimal phase1_ime_heavy category_coverage deep_silence; do
  cargo run --quiet --bin gse-replay -- tests/fixtures/$g.ndjson > tests/snapshots/$g.json
done
# 検証
for g in minimal phase1_ime_heavy category_coverage deep_silence; do
  cargo run --quiet --bin gse-replay -- tests/fixtures/$g.ndjson --snapshot tests/snapshots/$g.json
done
```

## 実測結果（2026-08-16）

| golden | 行数 | 判定 | `keys` が正の行 | `max(keys)` | `max(bs_keys)` |
|---|---|---|---|---|---|
| `minimal` | 15 | ★ 追加のみ | 15/15 | 9 | 1 |
| `phase1_ime_heavy` | 6 | ★ 追加のみ | 0/6 | 0 | 0 |
| `category_coverage` | 2 | ★ 追加のみ | 2/2 | 9 | 0 |
| `deep_silence` | 51 | ★ 追加のみ | 51/51 | 12 | 2 |

### ★ 検証方法（目視ではなく機械判定）

行数一致 ＋ **既存キーの値を `repr()` 比較**（`0.0` と `-0.0`、`int`/`float` の差も検出する）
＋ 追加キーが `{keys, bs_keys}` **ちょうど**であること ＋ 削除キーがゼロであること、を
4 本すべての全行に対して照合した。

```
minimal              rows= 15 OK (added only: keys/bs_keys)
phase1_ime_heavy     rows=  6 OK (added only: keys/bs_keys)
category_coverage    rows=  2 OK (added only: keys/bs_keys)
deep_silence         rows= 51 OK (added only: keys/bs_keys)
RESULT: ALL ADDITIVE-ONLY
```

★ **`p_flow` / `p_inc` / `p_stuck` / `raw_x` / `raw_y` / `ewma_x` / `ewma_y` / `obs` / `f1`〜`f6` は
1 ビットも動いていない。** → ★ 「記録と推論の分離」の契約は保たれている。

### ★ `git diff` 側の裏取り

`git diff -U0 tests/snapshots/` の**削除行は 4 種類しか無い**:

```
-    "alpha": 0.15
-    "alpha": 0.18
-    "alpha": 0.25
-    "alpha": 0.3
```

★ これらは **末尾フィールドが `alpha` から `bs_keys` に変わったことによるカンマ付与**であり、
追加行側に `"alpha": N,` として同じ値で再出現している（`+` 行の種類は
`"alpha": N,` / `"keys": N,` / `"bs_keys": N` の 3 種類のみ）。

## ⚠️ `phase1_ime_heavy` が全行 `keys=0` である理由（★ 一次で確認済み・配線の不具合ではない）

★ このフィクスチャは **`key` イベントを 1 件も含まない**（実測: `meta`×2 / `ime_state`×6 /
`session_start`×1 / `feat`×96 / `user_label`×6、**key press = 0**）。
★ 打鍵が無いのだから `keys=0` が正しい。

## ⚠️★★★ golden が示した最重要の事実 — **沈黙中は `keys` が凍結してくり返される**

★ `deep_silence` の `keys` / `bs_keys` の推移（★ 値が変わった行だけ）:

```
t=1000000001000 keys=4  bs=0  f1=150.0
t=1000000002000 keys=6  bs=1  f1=150.0
t=1000000005000 keys=9  bs=2  f1=150.0
t=1000000008000 keys=12 bs=2  f1=150.0
（★ 以降 t=1000000051000 まで 44 行、keys=12 / bs_keys=2 のまま不変）
```

⚠️★★★ **窓の右端は「最後の打鍵時刻」であって行の `t` ではない。**
（`features.rs`: `cutoff = last_ts.saturating_sub(30_000)`。★ `last_ts` はバッファ最後の
イベント時刻。★ `extractor.reset()` は IME pause 遷移でしか呼ばれない）

→ ★★★ **`keys` を feat 行をまたいで足し上げてはいけない。** 同じ打鍵を数十回二重計上する。
→ ★ 意味の正本は `analysis/loop_step.rs` の `FeatSnapshot::keys` の doc。
  解析者向けの記述は `docs/development-guidelines.md §10.3.2`。

## ⚠️ ついでに判明した既存コメントの誤り（★ 本タスクの変更とは無関係）

★ `src/bin/replay.rs` の golden 一覧コメントは「`deep_silence` は … **SilencePath**
（`make_silence_observation`）**の両方を踏む**」としていたが、⚠️ **踏んでいない**。

| golden | `f1` の値集合 | 経路 |
|---|---|---|
| `deep_silence` | **`[150.0]`** | ★ **全 51 行 TransitionPath** |
| `minimal` | `[140.0]` | TypingPath / TransitionPath |
| `category_coverage` | `[120.0]` | 同上 |
| `phase1_ime_heavy` | **`[2000.0]`** | ★ SilencePath |

★ 上の「窓が最後の打鍵に追従する」性質が理由。→ ★ **コメントを実測に訂正した**（挙動は不変）。

## ⚠️ 記録しておく既知の性質（★ 本タスクで作った制約ではなく、既存の窓を継承したもの）

★ **IME ポーズ中（`engine.get_paused()`）の打鍵は `FeatureExtractor` に入らない**
（`loop_step.rs` のイベント処理で `return` する）。★ したがって `keys` / `bs_keys` も
**IME 変換中の打鍵を数えない**。

- ⚠️ これは F1〜F6 が既に持っている性質を `keys` がそのまま継承したものであり、
  **本タスクで新たに導入した制約ではない**。
- ⚠️★ ただし **日本語入力主体のセッションでは `progress_proxy` が系統的に過小になる**。
  ★ 将来 `progress_proxy` を目的変数に使う実装は、この過小評価を明示的に扱うこと
  （★ 窓の定義を変えると特徴量が変わる＝ HMM 挙動が変わるので、**本タスクでは触らない**）。

## `HMM_VERSION`

★ `src-tauri/src/analysis/engine.rs:45` — `pub const HMM_VERSION: &str = "0.3.0";` のまま。
★ `engine.rs` は `git diff` で **1 行も変更されていない**。
