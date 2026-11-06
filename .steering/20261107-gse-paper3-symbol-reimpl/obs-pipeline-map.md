# obs 経路の洗い出し（GSE-prototype-paper3・読むだけ）

略: E=experiments/、A=src-tauri/src/analysis/、R=src-tauri/src/bin/replay.rs。行番号は読んだ時点のもの。

## 0. 結論の要点

- 最終の obs は **1 回目の replay（既定モード・フラグなし）** の出力から取る。2 回目の `--features` の出力は onsets / observed_intervals 用で、obs には使わない。
- obs = f(打鍵の時刻列, 各打鍵の category, セッション開始時刻 t0)。HMM の確率（p_flow 等）は obs に影響しない。
- 実効の設定は固定: task_kind なし → Writing head、ime_open は常に false → β は「Latin」の組、BS 罰は有効。

## 1. 入口と変換の段

### 1a. CoAuthor（E/20261103-coauthor-per-person/scripts/build_obs.py）
- main (:76-): メタデータ CSV から session_id→worker_id。zip の jsonl を session_id でソートし、`old/sessions.json` にある通し番号だけを処理（:80-95）。
- one() (:30-): zip から 1 本取り出し → `convert.convert(src, nd, ev_p, DWELL=100)`（:41）→ presses = key 行のうち press==True（:44）→ presses<2 なら捨てる（:46）。
- 1 回目 replay: `replay nd`（フラグなし・:50）の stdout が feat.json。
- add_feat.py → `withfeat.ndjson`（:55）→ 2 回目 `replay wf --features`（:56）。
- 出力 rec["feat"] は **feat.json（1 回目）** から `[timestamp,p_flow,p_inc,p_stuck,ewma_x,ewma_y,obs,alpha]`（:69-70）。onsets・observed_intervals だけ 2 回目（d）から。

### 1b. 変換 convert.py（E/20261031-coauthor-pre-request-signal/scripts/convert.py）
- jsonl を (eventTimestamp, eventNum) でソート（:55）。**t0 = 最初の行の eventTimestamp（種類を問わない。suggestion や API 挿入も含む）**（:56）。
- 打鍵に数える（eventSource=="user" のみ・:66 付近）:
  - text-insert で挿入文字がちょうど 1 文字 → `char_category(c)`。複数文字は捨てる。
  - text-delete → "backspace"。cursor-* → "navigation"。
- suggestion* と API 起源の挿入は打鍵列に入れない。
- char_category（:30-44）: `c.isalpha()`→alphabetic、`c.isdigit()`→numeric、" "→space、"\n"→enter、"\t"→tab、`.` `,`→sentence_punctuation、PUNCT 集合→punctuation、その他→other。**Python の Unicode 判定（isalpha/isdigit）に依存**。
- 離しの合成: 押下 t_i に対し rel_i = min(t_i+100, max(t_i, t_{i+1}-1))（最後の打鍵は t+100）。出力順は press_i, release_i の繰り返し（:95-100）。
- NDJSON: `meta{session_start:t0,hmm_version:"0.5.0"}` / `session_start{t:t0}` / key{t,category,press}（vk なし）。

### 1c. add_feat.py（E/20261031-.../scripts/add_feat.py）
- 1 回目の出力の KEYS（f1,f3,f4,f5,f6,p_*,raw_*,ewma_*,obs,alpha,keys,bs_keys）を `type:"feat", t=timestamp` 行にして NDJSON に混ぜ、(t, key先) で並べ直す。
- 目的: `--features` が **feat 行の t**（1 Hz tick の存在時刻）から observed_intervals（穴の検出）を作るため（R:3285-3352 `collect_all_feat_timestamps` は t しか読まない。feat_offline/stall_onset.observed_intervals(&feat_ts, hole_gap_ms) R:2371）。feat 行の中身（obs 等）は 2 回目で推定に入らない（ReplayEvent::Feat は timestamp()==None で ordered から除外・R:1270 付近）。
- つまり replay を 2 回通す理由 = 「1 回目は feat 行（tick の時刻）を作る。2 回目は feat 行を入力に要る `--features`（stall onset）を回す」。obs の値は 1 回目だけで決まる。

### 1d. CS1 2021（E/20261104-coauthor-ml-improve/scripts/build_cs1_obs.py → E/20261104-cs1-landscape/scripts/build_cs1.py）
- build_cs1_obs.py: bc.map_2021 を差し替え（X-Metadata が "Choose Lookup Item" / "... Replace" に完全一致する X-Action を ("ev","lookup-accept") にするだけ・obs には無関係）。bc.one を自前の one() に差し替え、feat を 8 列で残す（:72-74）。
- build_cs1.read_units（:121-）: CSV を行ごとに map_2021（:93-）で分類。キー化されるのは:
  - X-Keystroke の X-Metadata が 1 文字 → char_category
  - X-Action: NAV_2021（Left/Right/Up/Down/Home/End/PageUp/PageDown）→navigation、KEY_2021（Backspace→backspace、Delete→delete、Enter→enter、Tab→tab、Escape→escape、Paste/Copy/Cut/Undefined→other）
  - それ以外の X-Action は ev。1 文字以外の X-Keystroke は count（捨てる）。
  - 時刻 = `int(float(ClientTimestamp))`、同時刻の並びは EventID。
- split_blocks（:149-）: 隣り合う出来事（key と ev を合わせて）の差が ≥1,800,000 ms で課題を作業のまとまり（block）に切る。
- one()（build_cs1_obs.py:39-）:
  - block ごとに presses = key のみ。presses<2 の block は捨てる。
  - block ごとに NDJSON（t0 = **その block の最初の press の時刻**）を書き、**block ごとに 1 回目 replay（新しい engine・新しい状態）**。feat を連結（all_feat）。
  - 全 block の press を連結して 1 本の NDJSON（all_keys）を書き、all_feat を add_feat に渡し、`--features` を 1 回（onsets 用）。span が長すぎると "time span too large"（feat_offline/mod.rs:395・上限 MAX_FEATURE_TICKS=1,000,000 tick・R:67）で除外。
  - **CS1 の obs は block 単位の replay の結果の連結**（block 間で EWMA・罰・窓は持ち越さない）。CoAuthor はセッション 1 本通し。
- key_rows（build_cs1.py:168-）の離しの規則は convert.py と同じ（DWELL=100）。

## 2. replay 本体（既定モード）

- R:2678 `run_replay(path)` → R:2689 `serde_json::to_string_pretty(&snapshots)` が stdout の JSON 配列（FeatSnapshot）。他のモードフラグが無いときの経路。
- run_replay（R:4016-4286）:
  1. 全行を ReplayEvent にパース。**未知の type があれば Err で中断**（R:1125 の注）。
  2. t0 = Meta.session_start → SessionStart.t → 最初の timestamp()（R:4060-4080）。
  3. session_meta 行があれば task_kind→TaskDomain（logger.rs:114-126。Argumentative/Correspondence→Writing、Creative/Other→WritingFallback、VibeCoding→Coding）。**なければ Writing**（R:4125）。今回の NDJSON に session_meta は無い → Writing。
  4. timestamp() が Some の行だけを残して `sort_by_key`（**安定ソート**・R:4146）。対象は meta / session_start / key / ime_state だけ。feat・paste・各種記録行は除外。
  5. `AnalysisState::new(t0, 600)`（R:4149）、`CognitiveStateEngine::new_for_domain(domain)`。ime_open=false で開始。ime_state 行が無いので変わらない。
  6. 各イベントの前に `while state.next_engine_update_ms <= ev_ms { step(None, tick_ms) }`（R:4161）。**tick ≤ イベント時刻の tick を、そのイベントより先に処理する**（同時刻なら tick が先）。
  7. SessionStart は `state.reset(t, 600)`（R:4222）。engine は reset しない。
  8. Key: `resolve_key_vk(vk, category)`（R:1532）→ category→代表 VK（R:1499-1530）。→ `InputEvent{vk_code, is_press, is_repeat:false, is_backspace: vk==0x08||0x2E}`（R:4246 付近）→ `step(Some(Key), t)`。
  9. 最後のイベントの後に tick は進めない（末尾の沈黙行は出ない）。

### category→代表 VK→特徴量に流れるか（R:1499-1530, key_gate.rs:5-16）
| category | 代表 VK | 特徴量キー? |
|---|---|---|
| alphabetic | 0x41 | 流れる |
| numeric | 0x30 | 流れる |
| punctuation | 0xBA | 流れる |
| sentence_punctuation | 0xBE | 流れる |
| tab | 0x09 | 流れる |
| backspace | 0x08 | 流れる（is_backspace） |
| delete | 0x2E | 流れる（is_backspace=true。CS1 の Delete は BS と同じ扱い） |
| space / enter | 0x20 / 0x0D | 流れる |
| navigation 0x25, escape 0x1B, other 0x07, modifier 0x10, function 0x70 | | **流れない**（打鍵の列にも窓にも罰にも入らない） |
- 未知 category は skip（件数のみ warn）。

## 3. step()（A/loop_step.rs:221-463）

### 3.1 キー処理（:231-312）
- `out.key` を立てる → `engine.get_paused()` なら return（replay では常に false）。
- `is_feature_key(vk)` が真のときだけ（:275）: `extractor.process_event(event)`（リングバッファ容量 600 イベント＝press+release 合算。満杯なら先頭を捨てる・features.rs:129-134）。
- press のとき（:287-310）:
  - 非リピート（replay は常に非リピート。Windows ビルドは :238-247 で pressed_keys による再検出が入るが、今回の入力は release が必ず次の press より前なので発火しない）:
    - elapsed = now − last_event_time_ms。elapsed > 10,000 なら presses_since_silence += 1、**≥3 で** last_event_time_ms = now・カウンタ 0・pre_silence_features = None。elapsed ≤ 10,000 なら last_event_time_ms = now・カウンタ 0。
  - `engine.register_keystroke(event.is_backspace)`（:309）。
- release は窓に入るが last_event_time_ms も streak も触らない。
- ImeActivate は no-op（:313-327）。replay の入力には ime_state 行が無い。

### 3.2 1 Hz ゲート（:331-419）
- `now_ms < next_engine_update_ms` なら return。通ったら `next += 1000`、`next < now` なら `next = now + 1000`（replay では tick が next と一致するので後者は起きない）。
- 初期 next = t0（`new` と `SessionStart` の `reset`）。**tick は t0, t0+1000, t0+2000, … の格子**。CoAuthor の t0 は **最初の生の出来事（種類不問）**、CS1 の t0 は **block の最初の press**。
- Meta 行の処理時に tick(t0) が走り、SessionStart の reset が next を t0 に戻す。結果、最初のキーの前に tick(t0) が再度走るが feat は出ない（f1==0 かつ silence 0 → skip）。
- silence_secs = (now − last_event_time_ms)/1000.0（f64）。last_event_time_ms の初期値は t0。
- `features = extractor.calculate_features()`（窓は 4 節）。
- 経路の分岐（:368-419。順に評価）:
  1. **TypingPath**: `f1 > 0.0 && silence_secs < 2.0` → `pre_silence_features = Some(features)`（:371）→ `engine.update(&features, ime_open)`。
  2. **TransitionPath**: `f1 > 0.0`（かつ silence ≥ 2）→ `f5 += silence_secs/2.0`（:379）。silence ≥ 8 なら f3/f6 の底上げ:
     - pre_silence_features あり: time_scale = clamp((silence−8)/30, 0, 1)。f6 = max(f6, clamp(ctx.f6,0,1)*time_scale)、f3 = max(f3, clamp(ctx.f3,0,1)*time_scale)（:388-394）。
     - なし: f6_floor = clamp((s−8)/30); f3_floor = clamp((s−10)/40); s ≥ 10 なら f6_floor=max(.,0.15)、f3_floor=max(.,0.20)（:397-404）。
     - → `engine.update_silence(&features, ime_open, silence_secs)`。
  3. **SilencePath**: `f1 == 0`（バッファ空、または有効なフライトタイムが 1 つも無い）かつ silence ≥ 2.0 → `make_silence_observation`（features.rs:311-374）→ `update_silence`。
     - f1=2000.0、f4=0.0、f5=silence/2.0。
     - ctx（pre_silence_features）あり: ts=clamp((s−2)/30,0,1); f3=clamp(f3c+ts*(1−f3c)*f3c)、f6 も同形（f3c,f6c は ctx を [0,1] にクランプ）。
     - ctx なし: f6=(s≥10 ? max(clamp((s−10)/40),0.15) : clamp((s−10)/40))、f3=(s≥10 ? max(clamp((s−15)/50),0.20) : clamp((s−15)/50))。
  4. それ以外（f1==0 かつ silence<2）→ **feat 行なしで return**（行が出ない条件）。
- feat 行の obs/alpha/ewma/raw は diag から（:436-439）。diag が None のときは 0,0,0,0,0,0.0 だが、上の 3 経路では `update` の None 条件（paused / f1≤0 かつ罰なし）に当たらないので実質起きない。
- feat 行が出る条件: 上の 1-3 のどれか。出ない条件: 4、ゲート未達、paused。IME の候補中の停止（paused）は 2026-08-23 に live 側で外れ、replay は ImeActivate を見ない。実質存在しない（今回の入力は ime_state なし）。

## 4. 特徴量（A/features.rs）

- 窓: `last_ts` = **バッファ末尾のイベント時刻**（now ではない）、cutoff = last_ts.saturating_sub(30,000)、`timestamp >= cutoff` のイベント（:142-151）。FEATURE_WINDOW_MS=30,000（:41）、PAUSE_THRESHOLD_MS=2,000（:26）。
  - 沈黙中も窓は動かない（末尾が変わらない）→ f1,f3,f4 は同じ値が繰り返される。f5 だけ TransitionPath で加算される。
  - バッファは時間では evict されない（容量 600 のみ）。release も 1 イベントに数える。
- F1（:161-196）: リピートを除き、press のとき last_release が Some かつ `press.t >= rel` なら ft = press.t − rel、`ft < 2000.0` だけ採用。**中央値**（偶数は (a[n/2−1]+a[n/2])/2.0、昇順ソート）。空なら 0.0。
  - 合成した離しの規則から、隣接する press の差 g に対し ft = g−100（g≥101）、1（1≤g≤100）、0（g=0）。
  - **ft=0 だけの窓は f1=0 → SilencePath 側に落ちる**。
- F3（:199-210）: 窓の press 数（リピート含む）のうち is_backspace の割合。total=0 なら 0.0。
- F4（:214-249）: リピート除外で press を走査。last_release との差（saturating_sub）が < 200 なら current_burst+=1、そうでなければ前の burst を push して 1 から。f4 = burst 長の整数和 / burst 数（f64）。
- F5（:252-262）: press 時刻列の隣接差 ≥ 2000 の個数（f64）。
- F6（:265-282）: 窓の BS の press 数 del_count>0 なら、「BS の press の直後の press までの差 ≥ 2000」の数 / del_count。
- keys / bs_keys は記録のみ（推論に使われない・loop_step.rs:171-175 のテストで保証）。
- 正規化: `phi(x, β) = clamp((x−β)/(2.0*β), 0, 1)`、β≤0 なら 0.0（features.rs:103-109。KAPPA=2.0）。

## 5. x・y・EWMA・obs（A/engine.rs と A/heads/writing.rs）

### 5.1 head と β（今回は `WritingHead::new()`・ime_open=false → LATIN の組）
- writing.rs:33-37: F1=150.0、F3=0.06、F4=5.0、F5=2.0、F6=0.08（ime_open=true なら :22-26 の 100.0/0.10/2.5/1.0/0.12。今回は使われない）。
- heads/coding.rs:36-40 は Latin と同じ値。式も同じ。コーディング head でも obs は同じになる（Writing head の ime_open=false と同値）。WritingFallback（Creative/Other）も数値は Writing と同じ。
- x（writing.rs:126）: `(0.30*phi3 + 0.25*phi6 + 0.25*phi1 + 0.20*phi5).clamp(0.0,1.0)`（左から加算）。
- y（writing.rs:129）: `(0.40*phi4 + 0.35*(1.0-phi1) + 0.25*(1.0-phi5)).clamp(0.0,1.0)`。
- 罰の gate: `applies_backspace_penalty(ime_open) = !ime_open`（writing.rs:139）→ 今回は常に真。

### 5.2 EWMA（engine.rs）
- 初期値 `INITIAL_AXES_EWMA = (0.1, 0.8)`（:72）。engine は 1 ファイルにつき 1 個で、**x と y の EWMA は update と update_silence で共有**。
- `update`（TypingPath・:356-495）: α=0.3 固定。`ewma.0 = 0.3*raw_x + 0.7*ewma.0`（:389。**0.7 はリテラル。1.0−0.3 ではない**）。alpha を 0.3 と記録（:493）。
- `update_silence`（Transition / Silence・:504-606）: α は silence_secs で選ぶ（:520-526）: ≥25.0 → 0.25、≥15.0 → 0.18、それ以外 → 0.15。`ewma = alpha*raw + (1.0-alpha)*ewma`（:531-532）。記録する alpha も同じ値。
- bin: `x_bin = (x*5.0).floor().min(4.0) as usize`、y も同様、`obs = x_bin*5 + y_bin`（:402-404, :543-545）。obs ∈ 0..24。Rust の `as usize` は負値・NaN を 0 に飽和。
- 配置: obs = x_bin*5 + y_bin（x が行・y が列）。

### 5.3 罰の記号 25
- 閾値 `BACKSPACE_PENALTY_THRESHOLD = 14`（:79）。
- `register_keystroke(is_backspace)`（:335-344）: BS（0x08 / 0x2E）の press（**リピート含む**）で streak += 1、新しい streak ≥ 14 なら `has_pending_penalty = true`。BS 以外の **特徴量キー**の press で streak = 0（ナビゲーション等の非特徴量キーは streak に触れない・ゲートの内側のため）。
- **pending は streak が 0 に戻っても残る**。消費されるのは `update()`（TypingPath）の中だけ: `pending = has_pending_penalty.swap(false)`（:379）。`apply = pending && head.applies_backspace_penalty(ime_open)`（:380）。
  - gate が偽でも swap で消費される（今回は gate が真）。
  - `update_silence`（Transition / Silence）は pending に触れない → 次の TypingPath tick まで持ち越す（秒をまたぐ）。
- apply が真のとき: **x,y の EWMA は通常どおり更新（α=0.3）、obs だけ 25 に上書き**（:408-410）。alpha は 0.3。
- `update()` の早期 return: f1≤0 かつ pending なし（:363-367）。TypingPath は f1>0 なので実質効かない。
- `update_silence` の obs は 0..24 のみ（罰なし・:547 のコメント）。

### 5.4 obs に効かないもの
- 遷移行列・放出行列・current_state_probs・display_probs（ヒステリシス α=0.40/0.60）・`p_flow/p_inc/p_stuck`（engine.rs:163-242, :413-495, :583-596）。obs の計算より後の処理で、obs へは戻らない。
- keys / bs_keys、`HMM_VERSION`（meta の hmm_version は不一致なら warn するだけ・R:4090 付近）、ime_state / paste / pointer 等の記録行（ordered から除外）。
- 乱数: なし。時計: なし（時刻は NDJSON の t のみ）。

## 6. 書き直しで再現が難しい所

1. **tick の格子と順序**: tick = t0 + k*1000（t0 は CoAuthor=最初の生の出来事、CS1=block の最初の press）。同時刻では tick → イベントの順。最後のイベントの後に tick を足さない。Meta 行で 1 度 tick が走り SessionStart の reset が next を t0 に戻す（出力には出ないが状態は更新されない＝skip なので実害なし）。入力は stable sort 必須（同時刻の press→release→次の press の順）。
2. **状態の持ち越し**: axes_ewma は初期 (0.1,0.8) から、TypingPath と update_silence で同じ値を共有。pre_silence_features は TypingPath のたびに上書き、長い沈黙からの復帰（>10s 後に 3 打）で None。pending penalty は update_silence を通っても残り、次の TypingPath で消費。
3. **浮動小数の式の形**: `0.3*raw + 0.7*prev`（0.7 リテラル）と `a*raw + (1.0-a)*prev`（a=0.15/0.18/0.25）は別物。x,y の重みの加算順（左から）、phi の `(x−β)/(2.0*β)`、中央値の偶数時 `(a+b)/2.0`、silence_secs = ms を f64 にして /1000.0、`f5 += silence_secs/2.0`。bin 境界（x*5 の floor）は丸め 1 ULP で 1 つずれうる。エンジンの確率の加算順は obs に関係しないので無視してよい。
4. **窓とバッファの癖**: 窓の右端は最後のバッファ事象（release も含む）、時間 evict なし、容量 600 イベント（press+release で実質 300 打）でも古い側が落ちる。ft=0 ばかり・単発打鍵のときは f1=0 で SilencePath または行なし。飽和ではなく「f1==0」で分岐する点。release の合成規則が ft（g−100 / 1 / 0）と burst（gap<300）を決める。
5. **入力の仕分け**: category→特徴量キー可否の表（navigation / other / escape は完全に無視）、Delete=BS 扱い、CS1 は block ごとに engine を作り直す（持ち越しなし）、CoAuthor の char_category は Python の Unicode 判定（isalpha / isdigit）、1 文字挿入のみ採用・複数文字は捨てる。

## 7. 読んでいない所

- `feat_offline/`（stall_onset の onsets / observed_intervals の中身）は obs に関係しないので読んでいない（t だけ使うことのみ確認）。
- `anonymize.rs` は from_vk の写像（Python 側の category は replay が代表 VK へ逆写像するので、from_vk そのものは replay 経路に入らない）の一部しか読んでいない。
- Windows ビルドの `is_repeat` 再検出（:238-247）は、今回の入力では発火しないことを論理で確認したのみ（実行していない）。
- `cargo test`・replay の実行はしていない。ゴールデンとの突き合わせは未実施。
- `E/20261104-cs1-landscape/` の他スクリプト、`E/20261102-public-data-landscape/scripts/build_coauthor.py` は読んでいない（build_obs.py の docstring にある元の手順）。
