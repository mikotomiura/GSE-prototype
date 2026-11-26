# 設計（v2・/reimagine）

前提: requirement.md と decisions.md の判断 1〜6、ADR-051 の D3・D5・決めずに残すもの 2 は変えない。design-v1.md と design.md は開いていない。行番号は worktree `/Users/johnd/GSE-prototype-hm-desk` の 2026-11-15 時点のもの。推測は「推測」と書く。

## 0. この案の骨子

1. Rust の純粋なモジュールを 1 つ新しく作る（`analysis/handmark/desk.rs`）。ここが窓の切り方・日の境・種と t0・A の特徴・B の状態の特徴・T1・T2・画素を描くためのフレームの列を決める。IO と漏れの注入は bin（`replay.rs`）だけに置く。製品の写像のコードには 1 行も足さない。
2. 窓の表（NDJSON）と、画素のためのフレームの列（バイナリ）は別の出力にする。フレームの列はパイプで node に流して画素の特徴にする。大きな中間ファイルは残さない。
3. B の 2 つ（状態から・画素から）は、対象の合わせ方（ADR-051 D3）と同じ「両方が満たすときだけ満たす」で判定に入れる。そうすれば α を分けずに済む。今後どちらを使うかは、合成の陽性対照で見つけられた漏れの強さで決める（決めずに残すもの 2 を閉じる）。
4. 予測器の柔軟さの差が AUC の差に混ざる問題は、A を多尺度にして厚くし、2 つの診断（B_perm・A2）で大きさを測る。どちらも判定には入れない。

## 1. Rust 側: `gse-replay --handmark-windows`

### 1.1 入口
- 書き方: `gse-replay <s1.ndjson>... --handmark-windows --utc-offset-secs N --table <assignment.json> --table-sha <sha file> [--labels recorded|recomputed] [--frames <path|->] [--inject-stuck L]`
- 作り方は `--probes`・`--day-questions` に合わせる（`replay.rs:2041-2090` の `run_s1_replay`）。複数のファイルを `s1_replay::parse_file`・`order_inputs` で読む。排他の一覧（`replay.rs:1819-1840`）と usage（`replay.rs:2093-`）に足す。
- 表は `assignment::load_from_bytes` で SHA-256 を照らす。合わなければ Err で止める（fail-closed）。
- 出力（stdout）の 1 行目はヘッダ。`mode`・`desk_version="hm-desk-1"`・`hmm_version` の集合・入力のファイル名・`table_sha256`・`inject`・定数の一覧を載せる。2 行目からは窓 1 つに 1 行。キーの順は固定し、f64 は Rust の最短表現で書く（決定的）。

### 1.2 日と区間（segment）
- 日は `eh3::local_day(t, offset)`（`eh3.rs:353`・4:00 区切り）。オフセットは 1 つに固定する（`--day-questions` と同じ扱い）。日の境は `s1_replay::day_cutoff_ms`（`s1_replay.rs:1808`）。
- 区間は「状態を作り直す単位」で、ライブで `Stage::new` が呼ばれる場面に合わせる。ライブでは、窓を開いたときと日付の変わり目に作り直す（`handmark_driver.rs:388-398`・`449-458`）。
  - 後期で `handmark_day.stage_starts` がある日: その時刻を t0 にする。行は日ごとに最後のものを採る（schema の `handmark_day` の説明どおり）。`t0_source=recorded`。
  - それ以外（前期のすべての日と、行が無い日）: t0 は「セッションの始まり（最初の `meta.session_start`）」と「その日の 4:00」のうち遅い方にする。`t0_source=rule`。
  - 区間の終わりは、次の t0・セッションの終わり・日の境のうち最も早いもの。
- 種は全部の日で `assignment::draw_seed(table_sha256, day)`（`assignment.rs:179-184`）。ライブもこの式を使う（`handmark_store.rs:422-426`）。したがって前期の種も、新しい手順を作らずライブと同じ関数で決まる。後期の行に `draw_seed` があれば照らし、違う日は除いて数を出す。

### 1.3 窓
- 長さは 30 秒（ADR-051 D3 で固定）。区間の中で、UTC の 30 秒の格子にそろえて切る。区間をまたぐ窓と、`t0 + 30 s` より前に始まる窓は捨てる。捨てる理由は、状態が 0 から立ち上がる間（`irreg` は 10 s・場は 8 s）を混ぜないため。
- 次の窓は除き、理由ごとの数を出す。
  - (a) `recording_pause` の区間に重なる窓
  - (b) 窓の中の feat の行が 25 本未満の窓（区間の削除の穴もここで落ちる）
  - (c) 離席の候補: 窓の始まりの時点で最後の打鍵から `AWAY_IDLE_MS = 180 s` 以上たっていて、窓の中に打鍵も `pointer_bin` も無い窓（`intervention.rs:18`）
- 30 秒の窓の疑わしさ: 隣り合う窓は相関する。これは日のブロックの引き直しで吸収する（窓の単位の引き直しはしない）。長さを変える案は採らない（ADR で固定）。

### 1.4 T1・T2（推定はどこから読むか）
- 主は記録の feat を読む（`--labels recorded`）。当てる対象は「その日に系が実際に出した判断」で、HMM の版が変わった日もその日の判断のまま使う。日ごとの `hmm_version` は列に残す。
- `--labels recomputed` は key の行から `loop_step::step` を回し直す（`replay.rs:4172` の `run_replay` の流れを関数に分けて再利用）。合成の入力には feat が無いので、こちらを使う。
  - 記録で回すときは両方を出し、T1 の一致率が 0.95 未満なら本計算の前に止める（整合の門）。
- T1 = 窓の中の feat の `p_stuck` の平均 ≥ 0.60。
  - 閾値 0.60 は既存の 3 つの判定で一致している: `TRIGGER_P_STUCK`（`invitation.rs:43`）・`NUDGE_NEED_THRESHOLD`（`intervention.rs:3`）・`p_stuck_trigger`（`metrics.rs:166`）。
  - 副として「窓の 30 秒すべてで ≥ 0.60」も出す。これは招待の契機（`TRIGGER_HOLD_MS`・`invitation.rs:45`）と同じ形。報告だけで判定には使わない。陽性が少なくなるため（推測）。
- T2 = 窓の中の (`p_flow`, `p_inc`, `p_stuck`) の平均の argmax（判断 3）。同点のときは flow < inc < stuck の順で後のものを採る。
  - 列は `t2_target_*` として差し替えられる形にし、推定器か `level` ができたら列を足す。

### 1.5 A の特徴（許した情報だけ）
- 入力は打鍵の時刻（`key` の press の時刻だけ・`category` は読まない）と `pointer_bin`。手跡に入る打鍵と同じ集合になる（`lib.rs:5771-5775`。一時停止中は送らず、記録にも残らない）。
- 窓の終わり e から過去 10・30・60 s で次を作る（log1p も含む・約 22 次元）。
  - 打鍵の数
  - 打鍵の間隔の中央値・CV・p90（30 s）
  - 60 s の中の最長の間隔（上限 60 s）
  - e での最後の打鍵からの時間
  - 2 s 以上の止まりの数
  - 200 ms 未満の続き（バースト）の数と平均の長さ
  - `moved` の代表値（`trace_replay.rs:30` の `REP_PT`）の和（10・30 s）
  - 動いた秒の数
  - `buttons`・`wheel` の和
- 注意: `p_stuck` は修正率 F3 と削除の後の止まり F6 を通して、キーの種類にも依る（`features.rs:63-70`）。A にはキーの種類が無いので、T1 の A の AUC は 1 に届かなくてよい。届かない分は「写像が運びうる余地」ではない。写像もキーの種類を受け取らない（`state.rs:3`）。

### 1.6 B の状態の特徴と、フレームの列
- 区間ごとに 1 回だけ流して計算する（入れ子にしない）。
  - 状態: `Stage::new(seed, t0)` に打鍵を入れ、標本の時刻 τ で `advance_to(τ − LIVE_LAG_MS)`（`replay_live` の意味・`state.rs:256-262`）。
  - ポインタ: `Synth::new(bins, seed, t0, seg_end)` を `TraceField::step` に入れ、`step` が返す波紋（`trace.rs:209`）を拾う。`replay_trace` は波紋を捨てる（`trace_replay.rs:217-231`）ので、使わない。どちらも pub のままで、既存のコードは変えない。
- 標本の時刻は窓の中で 1 秒ごとの 30 点 τ_s。それぞれ τ_s と τ_s − 250 ms の 2 枚を描く（動きを測るため）。
- B_state（約 13 次元）
  - `speed` の平均・最大・最後・SD
  - `irreg` の平均・最大・最後
  - 窓の中の Δ`phase`
  - 場の |bend| の平均・最大、|pull| の平均、0 でないマスの割合
  - 窓の中の波紋の数
  - `drift`・`layout_seed`・`phase` の生の値は入れない。`drift` は入力に依らない経過時間（`state.rs:228`・`HandmarkStage.tsx:10`）で、入れると「経過時間の漏れ」が系の判断の漏れに混ざる。`layout_seed` は日で一定で、1 日ずつ抜く検証では意味を持たない。
- フレームの列（`--frames`）: little endian のバイナリで、1 枚ごとに次を書く。
  - `window_id u32`・`τ u64`・`speed, irreg, phase, drift f64`・`layout_seed u32`
  - 場の有無の印。有れば 480 個の f32。
  - 生きている波紋（開始から 1.6 s 未満）の数と、(x, y f32・経過 ms u16)
  - 場の cells を外へ書く関数は desk.rs だけに置く。`TraceState` に Serialize を付けない約束（ADR-050 D3・`trace.rs:9-11`）は崩さない。
- 画面との近似: 画面は届いた状態へ 250 ms かけて寄せる。机上はその時刻の状態をそのまま使う（寄せは省く）。限界に書く。

### 1.7 決定性
- 時計・HashMap の反復順・並列に頼らない。区間・窓・行は時刻の昇順。
- 次をテストで縛る（§7）: 同じ入力から表とフレームの列がバイト単位で同じになること。流し方が `replay_live`・`replay_trace` を τ ごとに呼んだ結果とビット単位で一致すること。

## 2. 漏れの注入（判断 4・机上だけ）

- 場所: `replay.rs` の中の関数 `inject_stuck(s: StageState, p: f64, lam: f64) -> StageState` 1 つ。lib の `analysis/` には置かない。
- 式: `speed' = (1−λ)·speed + λ·0.6·p`、`irreg' = (1−λ)·irreg + λ·p`。p は τ 以前で最後の feat の `p_stuck`（因果的）。0.6 は描画で風が最大になる速さ（`HandmarkStage.tsx:47` の `FULL_WIND_SPEED`）。
- 当てるのは、フレームの列と B_state を作る直前の状態だけ。`Stage` の積分（`phase`）には戻さない。画面への影響は草の風の強さ（`wind`）と、`irreg` を通した突風に出る。
- λ ∈ {0, 0.05, 0.1, 0.2, 0.4, 0.8}。λ = 0 は入力のビット列のまま通す（テストで縛る）。
- 製品に入らないことの確かめ: lib の中に `inject` の語が無いことを、`architecture-rules` の流儀の grep テスト（`tests/`）で縛る。

## 3. 描画の純関数への切り出し

- 新しい `src/components/handmarkStageDraw.ts`（React・Tauri・`performance` を import しない）。
  - `type Ctx2D = Pick<CanvasRenderingContext2D, ...>` の部分型（beginPath・lineTo・arc・ellipse・quadraticCurveTo・fill・stroke・clearRect・globalAlpha・fillStyle・strokeStyle・lineWidth）
  - `buildWorld(layoutSeed, W, H): World`（`HandmarkStage.tsx:145-174` を移す）
  - `drawFrame(ctx, world, view{W,H,S}, shown, field, ripples, nowMs, calm)`（`228-319` の fog・drawNature・ring・drawRipples と、`89-124` の noise・fbm を移す）
- `HandmarkStage.tsx` に残すもの: イベントの受け取り、from/to の寄せ（`355-366`）、requestAnimationFrame、resize と dpr、`prefers-reduced-motion` から calm への変換。`drawFrame` は今の描画の順のまま呼ぶ。
- node の canvas の依存は実験のディレクトリに閉じる。`experiments/20261115-handmark-leak-desk/package.json` と `package-lock.json` で `@napi-rs/canvas` の版を固定する（Skia で、ネイティブのビルドは要らない）。アプリの `package.json` の依存は増やさない。
  - node 22 は .ts の型を除いて読む（`scripts/handmark-stage-trace.test.mjs:2` と同じ）ので、`pixels.mjs` は `src/components/handmarkStageDraw.ts` を直接 import できる。
- 画素の特徴（`scripts/pixels.mjs`）
  - 描く大きさ: 320 × 200・dpr 1・背景は不透明な灰色 #808080 と合成する。窓は透明で、壁紙に依らないようにするため。
  - 1 枚ごとに輝度を 16 × 10 のマスで平均して L とする。動きは M = |L(τ) − L(τ−250)|。
  - 窓のベクトル: mean_s M（160）と mean_s L（160）、それに 5 つのスカラー（全体の動きの平均・最大・SD、下の 40%（草）と上（粒・霧）の動き）。
  - 320 次元のほうは、統計の側で学習の折り目の中だけで PCA にかけ、k = 12 に縮める。k ∈ {4, 24} は報告だけにする。
- 疑わしい前提: mean L は日ごとの配置（種）で大きく変わる。配置は 1 日ずつ抜く検証では雑音になり、B の AUC を下げる。つまり「満たす」の側に倒れる。動き M とスカラーを入れるのはこのためで、合成の陽性対照で検出力を確かめる（§6）。
- 確かめ方
  - `scripts/handmark-stage-draw.test.mjs`: 呼び出しを記録する偽の ctx で、同じ入力から同じ呼び出しの列が出ること（決定性）と、Math.random・performance・Date が無いこと（grep）を確かめる。`package.json` の `test:handmark` に足す。
  - 画面の見た目は、受け入れ条件どおり、アプリを動かして切り出しの前後を目で比べる。
  - 実験の selftest に、固定の入力で描いた画素の SHA-256 の golden を置く（同じ Mac・同じ版の上で）。

## 4. 統計（`scripts/stats.py`・numpy だけ）

- 環境: 過去の実験と同じ自作の Newton 法（`experiments/20261104-coauthor-ml-improve/scripts/logit.py`）。依存は requirements.txt で numpy の版を固定するだけ。
- 予測器: L2 罰つきのロジスティック。切片は罰さない。特徴は学習の折り目で標準化する。
  - λ ∈ {0.01, 0.1, 1, 10, 100} を、学習の日の中の 1 日ずつ抜く検証の対数損失で選ぶ。A と B に同じ手順を使う。
  - T2 は 3 つの一対他で、それぞれ同じ手順を回す。
- 外の交差検証: 1 日ずつ抜く。予測した値を全部の窓について固定する。
- AUC: Mann–Whitney（同点は 0.5）。引き直した日を合わせて計算する（片方のクラスしか無い日も落とさない）。T2 は 3 つの一対他の AUC の平均（マクロ AUC）。
- 区間: 日のブロックで R = 2000 回引き直す（SEED から）。それぞれで AUC(B) − AUC(A) と AUC(A) を出し、両側 90% のパーセンタイル（5% 点と 95% 点）を取る。
- 3 値（δ = 0.05）
  - 上限 < δ なら「満たす」。
  - 下限 > δ なら「満たさない」。
  - それ以外は「判定不能」。
  - 天井: AUC(A) の 5% 点 > 0.95 で、かつ差の上限 < δ なら「満たす（天井）」（ADR-051 D3 のとおり）。
- B の 2 つ: 対象ごとに (B_state, B_pix) をそれぞれ判定し、対象の合わせ方と同じ規則で 1 つにする（両方満たす→満たす、どちらか満たさない→満たさない、それ以外→判定不能）。そのうえで T1・T2 を合わせ、主と感度分析を ADR の表で合わせる。表は純関数として全部のセルを単体テストで縛る。
- 柔軟さの診断（判定に入れない・報告だけ）
  - B_perm: 見た目の特徴だけを、同じ日の中で窓の間で並べ替える。差は 0 以下に出るはず。この差が、次元が増えた分の過学習の大きさになる。
  - A2: A に、上位 8 つの特徴の 2 乗と組の積を足す。AUC(A2) が AUC(B) に近ければ、B の上積みは許した情報の柔軟な要約にすぎないと読む。
- 入れ子の引き直し（ADR-051 D3 限界 3）: 引き直したそれぞれの標本で、1 日ずつ抜く検証をやり直す。同じ元の日の写しは一緒に抜く。λ は主の解析で選んだ値に固定して計算を抑える。
- 引き直しの方式の選び方（記録を開く前に固定）: 合成の入力の λ = 0 で、日数 D ∈ {10, 20, 30} について、それぞれ 50 組のデータを作る。母集団の真の差は 200 日の独立した合成で出す。固定の予測の方式で、90% 区間が真の差を含む割合が、どの D でも 0.85 以上なら固定の方式を主にする。そうでなければ入れ子を主にする。実測で 2 時間を超えたら判断 6 で研究者に聞く。

## 5. conditions.md に固定する条件（案）

1. クラスの最小の数: 対象のクラスごとに、合わせた日で窓が 50 以上あり、かつそのクラスを含む日が 3 日以上。T2 は 3 つのカテゴリすべてに課す。満たさない対象は「判定不能」。3 日の条件があれば、1 日を抜いた学習の集合からクラスが欠けることは起きない。万一起きたら「判定不能」。
2. 日の最小の数: 有効な窓が 20 以上の日が 8 日以上。足りなければ全体を「判定不能」。
3. 引き直しの標本でクラスが欠けたとき: その標本を落として数を出す。落とした標本が 5% を超えたら「判定不能」。
4. T1・T2 の定義（§1.4）、ラベルの元（記録の feat・回し直しとの一致 0.95 の門）、窓の除外（§1.3）。
5. 前期の種と t0（§1.2）: `draw_seed(table_sha256, day)` と、`max(session_start, 4:00)` の規則。
6. 感度分析の日: 割付が `late_first` か `on` の日で、次をすべて満たす日。
   - 切っていた区間（`toggles` から復元）に重なる窓は除く。
   - 残った窓が、その日の有効な窓の 50% 以上ある。
   - `visible_ms / shown_ms ≥ 0.5`。
   - `overflow` が偽で、区間の削除で `toggles`・`stage_starts` が消えていない（前後の行で数が減った日は除く）。
   - 切った時間が長い日は、この 50% の規則で落とす。
7. 引き直しの方式とその選び方（§4）、R = 2000（入れ子は 500）、λ の格子、PCA の k = 12、描く大きさ、標本を 1 Hz で 2 枚ずつ取ること。予備: 計算が 2 時間を超えるなら 0.5 Hz に下げる（下げたときは記録を開く前に書き直す）。
8. 本人の記録では、窓の表とフレームは repo の外に置く。Claude は summary.json だけを読む（ADR-052 D4）。

## 6. 合成の入力と対照の段階

- 生成器（`scripts/synth.py`・種つき）: 潜在の状態（流れる・温める・詰まる）を、分の単位のマルコフ連鎖で動かす。
  - 状態ごとに、打鍵の間隔の分布・止まり・Backspace と Delete の割合・削除の後の止まり・`pointer_bin` の量と押下を変える。
  - 「詰まる」の差の一部は、キーの種類にだけ出るようにする（A に入らない情報で `p_stuck` が動くように）。こうしないと、注入しても A を超える情報が乗らず、陽性対照が働かない。
  - 出力: `meta` 行（`hmm_version`・`s1_mode`）・`key` 行（category・press と release）・`pointer_bin` 行。20 日 × 1 日 2 セッション × 90 分。割付の表は `assignment::generate` で作る。
  - 人の記録は使わない。
- 段階
  - S0: 単体テスト（Rust・TS・Python）
  - S1: oracle の陽性。`p_stuck` をそのまま B の列に足すと「満たさない」になること（描画を通さずに統計の部分だけを確かめる）。
  - S2: 陰性。λ = 0 の 20 組で、「満たさない」が 1 組以下であること。
  - S3: 段階をつけた陽性。λ ごとに 20 組を回し、B_state と B_pix のそれぞれについて、80% 以上の組で「満たさない」が出る最小の λ を報告する。小さい方の B を以後の主にする（決めずに残すもの 2 を閉じる）。
  - S4: 診断（B_perm・A2・種を変えたときの画素の特徴の揺れ・画素の特徴から経過時間を当てられるかの R²）。
  - S5: 引き直しの方式の比べ（§4）
- mutate.sh（過去の実験の作法）: 次のどれか 1 つでも、名指しの対照の結果を変えなければ止める。
  - A と B を入れ替える
  - 日のブロックを窓の単位にする
  - 天井の条件の片方を外す
  - 合わせ方の表の 1 つのセルを変える

## 7. テスト・変更するファイル・限界

### テスト
- Rust（`desk.rs` の単体テストと `replay.rs` の引数のテスト）
  - 同じ入力から表とフレームの列がバイト単位で同じ
  - 流した状態が `replay_live(..., τ)` とビット単位で一致する（乱数の打鍵で性質のテスト）
  - 流した場が `replay_trace(..., τ)` と一致し、波紋が `step` の返す値と一致する
  - 窓の境（格子・区間をまたぐ窓・立ち上がりの 30 s）
  - 日の境（4:00 の前後と UTC のオフセット）
  - `stage_starts` があるときとないときの t0
  - 種が `draw_seed` と等しい
  - 除外の 3 つの理由
  - T1 が 0.60 ちょうどのときと、T2 が同点のとき
  - λ = 0 の注入がビットを変えない
  - 他のモードとの排他
- TS: §3 のテスト。tsc。
- Python: AUC を総当たりの組で計算した値と照らす。Newton 法を既知の解と照らす。引き直しが SEED で再現する。3 値・天井・合わせ方の表を全部のセルで確かめる。selftest は run.sh の頭で回す。
- 全体: `cargo test --workspace`・clippy・emit_schema の一致（行種は足さないので schema は変わらない）・/cross-review。

### 変更するファイル
- 新しく作る: `src-tauri/src/analysis/handmark/desk.rs`
- 変える: `src-tauri/src/analysis/handmark/mod.rs`、`src-tauri/src/bin/replay.rs`（モード・注入・フレームの書き出し・`run_replay` の分割）
- 描画: `src/components/handmarkStageDraw.ts`（新しく）、`src/components/HandmarkStage.tsx`、`scripts/handmark-stage-draw.test.mjs`（新しく）、`package.json`（テストのスクリプトだけ）
- 実験: `experiments/20261115-handmark-leak-desk/` の中に run.sh・SEED・conditions.md・env.md・notes.md・mutate.sh・requirements.txt・package.json と package-lock.json・`scripts/{synth.py, stats.py, verdict.py, selftest.py, controls.py, timing.py, pixels.mjs}`
- conditions.md は本人の記録を開く前に、先にコミットする。

### 限界
- 再生の契約の近似: ポインタは 1 秒の量から作り、位置は種で決めた疑似の値。画面の 250 ms・32 ms の寄せは省く。node の Skia は WebKit と画素が一致しない（判断 2）。
- 注入は `speed` と `irreg` にだけ入れる。ほかの経路の漏れに対する検出力は測っていない。
- 合成の生成器が人の打鍵に似ているかは確かめていない。引き直しの方式の選び方は、生成器の仮定に依る。
- A を厚くしても、柔軟さの差を完全には除けない。B_perm と A2 は大きさを示すだけ。
- 窓の数と IME の間の feat の欠け、1 Hz で 2 枚の描画の計算時間は推測で、合成で実測してから確かめる。
- `drift` を B_state から外したので、画素に残る経過時間の情報は S4 の R² で確かめるだけになる。
- 判断 3 の読み替え（T2 = HMM の 3 状態の最大）は、事前登録の改訂へ渡す。

### Critical Files for Implementation
- /Users/johnd/GSE-prototype-hm-desk/src-tauri/src/bin/replay.rs
- /Users/johnd/GSE-prototype-hm-desk/src-tauri/src/analysis/handmark/state.rs
- /Users/johnd/GSE-prototype-hm-desk/src-tauri/src/analysis/handmark/trace_replay.rs（と trace.rs）
- /Users/johnd/GSE-prototype-hm-desk/src-tauri/src/analysis/handmark/assignment.rs
- /Users/johnd/GSE-prototype-hm-desk/src/components/HandmarkStage.tsx

## 設計判断の履歴
- 実行回数: 1 回目（2026-11-15）
- 採用: v2
- 根拠: 研究者が選んだ。v1 の陽性対照は合成の差が全部打鍵の時刻に出て、注入した漏れが A を超えにくい。v2 は当てる対象を系が実際に出した判断（記録の feat）にし、t0 をライブに合わせ、経過時間を特徴から外す（design-comparison.md）。条件の数値は conditions.md を書くときに確かめる。
