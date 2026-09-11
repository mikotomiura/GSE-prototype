# 一次資料メモ (1) 推論パイプラインの計算過程

> 出典はすべて `src-tauri/src/` 配下のコード実測 (2026-09-04)。スライド本文はこの値だけを根拠にする。
> ⚠️ `.claude/skills/hmm-analysis/SKILL.md` と `parameter-reference.md` の α 値・沈黙閾値・
> ヒステリシス係数は**コードと一致していない**。コード側が正。

## データフロー (型と次元)

```
OS フック  hook_windows.rs:684-704 / hook_macos.rs:437-455
  └ InputEvent { vk_code:u32, timestamp:u64(ms), is_press, is_repeat, is_backspace, is_paste }
                                                             features.rs:3-15
  │ mpsc channel
  ▼ LoopInput::Key                                           loop_step.rs:104-114
  ├ is_feature_key(vk) ゲート                                loop_step.rs:275 / key_gate.rs:47-61
  ▼ VecDeque<InputEvent> 容量 600 (= 実質 ~300 打)           features.rs:71-94 / lib.rs:3355
  ▼ calculate_features()  窓 = [last_ts - 30_000, last_ts]   features.rs:97-255
    Features { f1,f3,f4,f5,f6: f64, keys,bs_keys: u64 }      features.rs:19-44
  ▼ head.latent_axes(&Features, ime_open) -> (f64, f64)      heads/writing.rs:100-131
  ▼ EWMA                                                      engine.rs:386-398 / 518-530
  ▼ 量子化 5x5 -> obs: usize (0..=24, 25=ペナルティ)          engine.rs:401-409
  ▼ Forward Algorithm  A:[f64;9] B:[f64;78] pi:[f64;3]       engine.rs:426-447
  ▼ ヒステリシス EMA -> display_probs:[f64;3]                engine.rs:459-474 / 594-607
  ▼ FeatSnapshot (17 フィールド)                             loop_step.rs:133-194, 441-460
  ▼ LogEntry::Feat -> NDJSON                                 lib.rs:3437-
```

★ 本番 (lib.rs 分析スレッド) と `gse-replay` は**同じ `loop_step::step()`** を通る
(loop_step.rs:1-13 / lib.rs:3426 / bin/replay.rs:1787)。

## 特徴量 (F2 は欠番)

共通の窓: `cutoff = last_ts.saturating_sub(30_000)` (features.rs:104)。
⚠️ `last_ts` は**バッファ最後のイベント時刻**であって `now` ではない (features.rs:102)。

| ID | コード上の名 | 定義 | 実装 |
|---|---|---|---|
| F1 | f1_flight_time_median | release→次 press の中央値。is_repeat 除外、2000 ms 以上は外れ値除外 | features.rs:121-156 |
| F3 | f3_correction_rate | (BS+Del 押下数)/(窓内全キー押下数) | features.rs:163-170 |
| F4 | f4_burst_length | 間隔 < 200 ms で連結したチャンクの平均長 | features.rs:172-209 |
| F5 | f5_pause_count | 連続 press 時刻の差が >= 2000 ms の回数 | features.rs:211-222 |
| F6 | f6_pause_after_del_rate | (先頭が BS/Del かつ次 press まで >=2000 ms のペア数)/(窓内 BS/Del 数) | features.rs:224-242 |
| — | keys / bs_keys | Tier 0 = 記録のみ。HMM にも X/Y にも流れない | features.rs:31-43, 250-253 |

正規化 `phi(x, beta) = clamp((x - beta) / (kappa * beta), 0.0, 1.0)`、**kappa = 2.0**
(features.rs:63-69)。beta で 0、3*beta で 1 に飽和。

## EWMA / ヒステリシス EMA の alpha (実値)

| 用途 | alpha | 場所 |
|---|---|---|
| 潜在軸 EWMA (通常 update) | 0.3 | engine.rs:383-397 |
| 潜在軸 EWMA (沈黙 update_silence) | 0.15 (s<15s) / 0.18 (15<=s<25) / 0.25 (s>=25) | engine.rs:509-515 |
| ヒステリシス EMA (display_probs 通常) | 0.40 | engine.rs:459, 467 |
| ヒステリシス EMA (BS ペナルティ時) | 0.60 | engine.rs:459 |

⚠️ engine.rs:19-25 に「IEEE 754 で 1.0-0.3 != 0.7 になるため alpha を定数抽出しない」というポリシー。

## 2 軸射影 (Writing / Coding とも同一式。beta だけ違う)

heads/writing.rs:126-129 / heads/coding.rs:72-75

```
X (Cognitive Friction)    = clamp( 0.30*phi(F3) + 0.25*phi(F6) + 0.25*phi(F1) + 0.20*phi(F5), 0, 1 )
Y (Productive Engagement) = clamp( 0.40*phi(F4) + 0.35*(1-phi(F1)) + 0.25*(1-phi(F5)), 0, 1 )
```
重み合計はどちらも 1.0。

### beta ベースラインの実値

| 定数群 | F1(ms) | F3 | F4(chars) | F5 | F6 | 場所 |
|---|---|---|---|---|---|---|
| beta_writing (IME on) | 100.0 | 0.10 | 2.5 | 1.0 | 0.12 | writing.rs:22-26 |
| beta_writing_latin (IME off) | 150.0 | 0.06 | 5.0 | 2.0 | 0.08 | writing.rs:33-37 |
| beta_coding (v0) | 150.0 | 0.06 | 5.0 | 2.0 | 0.08 | coding.rs:36-40 |

Writing head は `ime_open` で beta を切替 (writing.rs:100-117)。Coding head は `ime_open` を**使わない**
(coding.rs:64。日本語コメントで IME が開いてもドメインは coding のまま)。

### 摩擦フロア (2 系統。閾値が違うのは意図的な分離)

- (a) TransitionPath (バッファに実データ有 + 2 秒以上沈黙) loop_step.rs:374-408
  - `silence >= 2.0` で `F5 += silence_secs / 2.0`
  - `silence >= 8.0` で摩擦フロア: onset 8s / ramp 30s / **線形**。
    文脈あり `time_scale = clamp((s-8)/30,0,1)`, `f6_floor = ctx.F6*ts`, `f3_floor = ctx.F3*ts`
    文脈なし `f6_floor = clamp((s-8)/30)`, `f3_floor = clamp((s-10)/40)`、s>=10 で floor 0.15 / 0.20
- (b) SilencePath (バッファ空) features.rs:271-334
  - `silence < 2.0` -> None。`F1 = 2000.0` / `F4 = 0.0` / `F5 = s/2.0`
  - 文脈あり: onset 2s / ramp 30s / **非線形** `F3 = ctx3 + ts*(1-ctx3)*ctx3` (F6 も同形)
  - 文脈なし: `F6 = clamp((s-10)/40)` floor 0.15 / `F3 = clamp((s-15)/50)` floor 0.20

Silence-break protection: 10 秒超の沈黙後は **3 打鍵連続**で初めて復帰とみなす (loop_step.rs:287-305)。

### バックスペースペナルティ

- 閾値 `BACKSPACE_PENALTY_THRESHOLD = 14` (engine.rs:78。IME の正常な変換修正は通常 8-12 連打)
- 1Hz ゲートの**外側**で全打鍵カウント (engine.rs:334-343 / loop_step.rs:309)
- gate は `!ime_open` (writing.rs:139-141 / coding.rs:86-88)
- 発動時 `obs = 25` に強制 (engine.rs:407-409)、ヒステリシス alpha を 0.60 へ
- ⚠️ `update_silence()` では**ペナルティを一切適用しない** (engine.rs:536)

## 量子化 (obs = 0..25) — engine.rs:400-409

```
x_bin = (x * 5.0).floor().min(4.0)   // 0..4
y_bin = (y * 5.0).floor().min(4.0)   // 0..4
obs   = x_bin * 5 + y_bin            // 0..24
if apply_backspace_penalty { obs = 25 }
```
境界: [0,0.2)->0 / [0.2,0.4)->1 / [0.4,0.6)->2 / [0.6,0.8)->3 / [0.8,1.0]->4。X が上位桁。

## HMM

- 状態: `CognitiveState { Flow, Incubation, Stuck }` = index 0/1/2 (engine.rs:92-97)
- 初期事前 `INITIAL_PROBS = [0.80, 0.15, 0.05]` (engine.rs:65)
- 潜在軸 EWMA 初期値 `INITIAL_AXES_EWMA = (0.1, 0.8)` (engine.rs:71)
- 遷移行列 A (engine.rs:172、行和 1.0 をテストで固定 engine.rs:646-654)

|  | ->Flow | ->Incubation | ->Stuck |
|---|---|---|---|
| Flow | 0.75 | 0.17 | 0.08 |
| Incubation | 0.12 | 0.80 | 0.08 |
| Stuck | 0.06 | 0.18 | 0.76 |

根拠コメント: Flow escape time 1/(1-0.75)=4s / Incubation 0.80 = Sio & Ormerod 2009 /
Stuck 0.76 = Hall et al. 2024 (engine.rs:163-171)

- 放出行列 B: `[f64; 78]` = 3 states x 26 bins、index `j*26 + obs` (engine.rs:110, 434)。
  全ビンに最小値 0.01 を組み込み済み。行は正規化されていない (engine.rs:193-241)。

| state | x=0 (y=0..4) | x=1 | x=2 | x=3 | x=4 | penalty(25) |
|---|---|---|---|---|---|---|
| Flow | .01 .02 .08 .12 .14 | .01 .02 .08 .12 .13 | .01 .01 .02 .01 .08 | .01 x5 | .01 x5 | 0.01 |
| Incubation | .15 .10 .04 .03 .02 | .14 .08 .04 .03 .02 | .10 .08 .03 .02 .01 | .05 .04 .01 .01 .01 | .04 .03 .01 .01 .01 | 0.01 |
| Stuck | .01 x5 | .01 x5 | .02 .04 .04 .05 .01 | .10 .16 .05 .07 .01 | .16 .22 .12 .05 .02 | 0.99 |

ペナルティビンの Stuck:Flow 比は **99 倍** (engine.rs:194-196)。

- Forward (engine.rs:421-447):
  `new[j] = ( sum_i old[i]*A[i][j] ) * B[j][obs]` -> sum で正規化。sum<=0 なら前回確率を維持。
- ヒステリシス: `display[i] = a_h*new[i] + (1-a_h)*display[i]` (a_h = 0.40 / ペナルティ時 0.60) 後に再正規化。
  `get_current_state()` が返すのは **display_probs**。
- **`HMM_VERSION = "0.5.0"`** (engine.rs:58、テスト engine.rs:818-820)。
  0.5.0 = 「IME による推論の一時停止をやめた」(2026-08-23)。実データ fixture `phase1_ime_heavy` が
  6 -> 98 スナップショットに増えた ＝ 旧挙動は推論窓の 94% を潰していた。

## ゲート

- 1Hz: `ENGINE_TICK_MS = 1000` (loop_step.rs:40)。`if now_ms < next_engine_update_ms { return }`
  (loop_step.rs:332-334)。**絶対時刻ベース増分**で累積ドリフト防止 (loop_step.rs:338-341)。
- `key_gate.rs::is_feature_key` が通す集合: A-Z / 0-9 / テンキー / OEM 記号 / BS / Enter / Space / Tab / Del。
  止めるもの: 修飾キー・ナビゲーション・Esc・F1-F12。
  ★ **ゲートに落ちたキーも NDJSON には残る** (loop_step.rs:249-253)。
  ★ ゲートで `return` しない理由: return すると feat の発火が 1 tick 遅れる (loop_step.rs:271-274)。
- ★ `key_gate` を `analysis/` に置いた理由: 本番と replay が同じ `step()` を通るので 1 か所で両方に効く。

## 沈黙 3 経路 (loop_step.rs:366-419)

| 経路 | 条件 | 関数 | alpha |
|---|---|---|---|
| TypingPath | F1>0 かつ silence<2.0 | engine.update() | 0.3 |
| TransitionPath | F1>0 かつ silence>=2.0 | 摩擦フロア適用後 engine.update_silence() | 0.15/0.18/0.25 |
| SilencePath | F1==0 かつ make_silence_observation が Some | 合成観測で update_silence() | 同上 |
| skip | silence<2.0 かつ F1==0 | 何もせず return (feat 行が出ない) | — |

## FeatSnapshot (17 フィールド) — 定義の正本は analysis/loop_step.rs:133-194

`timestamp` / `f1 f3 f4 f5 f6` (経路後の log_features) / `p_flow p_inc p_stuck` (display_probs) /
`raw_x raw_y` / `ewma_x ewma_y` / `obs` / `alpha` / `keys` / `bs_keys`。
⚠️ `schema_dto.rs` にあるのは NDJSON 検証用 DTO (obs を u64、keys/bs_keys を Option<u64> に緩めている)。
⚠️ engine が None を返した tick は raw_*/ewma_*/obs/alpha が全て 0。
⚠️ keys/bs_keys は推論に一切使われない (テスト `engine_output_is_invariant_to_tier0_key_counts` で契約化)。

## ドメインヘッド (ADR-006)

```
TaskKind (logger.rs:69-74)        TaskDomain (heads/mod.rs:53-63)   head
  argumentative  ┐
  correspondence ┴──────────────► Writing          ──► WritingHead::new()      "writing"
  creative       ───────────────► WritingFallback  ──► WritingHead::fallback() "writing_fallback"
  vibe_coding    ───────────────► Coding           ──► CodingHeadV0::new()     "coding_v0"
```
- 変換の唯一の実装: `impl From<TaskKind> for TaskDomain` (**logger.rs:108-121**)。1 本しか置かない理由は
  logger.rs:96-107「2 箇所に書くと本番とリプレイの head 選択がずれる」。
- ルーティング `head_for()` (heads/mod.rs:125-131、`_ =>` を書かず網羅性をコンパイラに強制)
- trait `DomainInferenceHead { head_id(), latent_axes(&Features, ime_open), applies_backspace_penalty(ime_open) }`
  (heads/mod.rs:137-156。**デフォルト実装を置かない**)
- engine 側は `Arc<Mutex<Arc<dyn DomainInferenceHead>>>` (engine.rs:139)。`task_kind` が `start_session` の
  **後**に届くため構築時固定にできない。1 tick で head を取るのは 1 回だけ (engine.rs:374-376)。
- `task_kind` は**宣言**、`ime_open` は**観測**で役割が直交 (heads/mod.rs:5-14)。
- writing / coding の実装差は **beta の選び方だけ** (式も BS gate も同一)。
  `WritingFallback` は数値挙動が Writing と完全に同一で `head_id` だけ違う。

## ⚠️ スライドで「生きた経路」として描いてはいけないもの

- `LoopInput::ImeActivate` は空実装 (loop_step.rs:313-327)。IME による `set_paused` は 2026-08-23 に撤去済み
  (engine.rs:810-816)。→ `is_paused` 分岐は実運用では発火しない。
- `InputEvent.is_paste` は FeatureExtractor が読まないので FeatSnapshot に影響しない (features.rs:10-14)。
