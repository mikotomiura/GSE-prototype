# 設計（v2・/reimagine で作り直した案）

v1 を読まない Opus のエージェントが requirement.md・decisions.md・前の試験のコードだけから作った案（2026-11-06）。numpy の挙動の 2 点（区間の linear が ±∞ で NaN・和 0 の行が 0/0 で NaN）は Mac の numpy 2.5.2 で確かめた。

## 1 実装のやり方

- 新しいディレクトリ `experiments/20261106-tau-mode-candidate/` に、前の試験の `.gitattributes`・`SEED`（2026110401）・run.sh・mutate.sh・scripts/ を写す。前の試験のディレクトリは変えない。他の実験への相対パスは兄弟のディレクトリからそのまま通る。
- conditions.md は「tau-extend から変える所だけ」。SEED と一緒に、コードを変える前にコミットする。
- run.sh: `PREV` は tau-extend、`RAW` は `tau_mode_candidate_writer_values`、provenance の `git status` の対象は新しいパス。

### 最頻値
- S̄ は `ml.fit_pool_excl` が既に返す。`hmm2.mode_of(kind, sbar)` を足す。和が正の行は `X / X.sum(...)` と同じ演算（ビットまで同じ）。和が 0 の行の扱いは下の「未決」。
- `em_writer` で `res["mode"][name] = ev.ll_zero(mode_of(kind, sb))`。k に依らないので構造ごとに 1 回。乱数は引かない。折り目は作らない（判断 2）。`rk["self"]` には入れない（前の試験と同じ鍵を保つ）。
- 選ぶ行（`TAU_KEYS`・`em_values`・`joint_values`・`joint_cands`・`select_cv` の候補）は一字も変えない。最頻値は `MODE = "mode"` で、`summarize_em` の行 `tau_mode`（固定の行）と相手にだけ出す。
- 相手: `OPPS` の末尾に `mode_same`。`em_rows` で `other = results[w]["em"]["mode"][name][j]`、行の τ が MODE なら `me` も同じ所から取る。すべての行（τ 固定・τ 他人・τ 本人 CV・2 段の 2 種・K 本人 CV）に入る（判断 3）。
- 判断 5 の a は行 `tau_<τ>` × 相手 `mode_same`、b は行 `tau_mode` × 相手 `pool_same`。書き手ごとに a + b = 本人 − 共通 を selftest で確かめる。

### −∞ の扱い
- `hmm2.forward` は、ある時刻で全状態の放出が 0 だと c = 0（log は −∞）、alpha = 0/0 = NaN になり、以後の c も NaN になる（同じ系列の中だけ）。何もしないと平均は −∞ ではなく NaN になる。
- `hmm2.pred_logprob_zero`: errstate の下で `forward` を呼び、系列ごとにマスク内で最初に c = 0 の時刻 t0 を探し、t0 から後のマスク内を −∞ にする。t0 より前に NaN か +∞ があれば例外。`forward`・`pred_logprob` は変えない（本人・共通・r1 の値はビットまで同じ）。
- 押下のある記号の量の定義は下の「未決」。
- 集計: `q` は `inverted_cdf`（補間しない）なので ±∞ で正しい。`better_share` も定まる。`np.median` は同じ符号の ∞ と有限なら ∞、+∞ と −∞ が混ざると NaN。行 `tau_mode` は −∞ か有限、相手 `mode_same` は +∞ か有限なので、混ざるのは行 `tau_mode` × 相手 `mode_same` だけで、これは 0.0 と決め打ちする（τ = ∞ と共通の差と同じ扱い）。混ざったら例外。
- `boot_median`: `np.quantile(meds, 0.025)` の linear は ±∞ で NaN（確かめた）。`meds` がすべて有限なら今の式のまま、∞ があれば `inverted_cdf` で区間を出し `ci_method` の印を付ける。`idx` はどちらでも同じように引く（乱数の流れを分けない）。
- 人数: `delta_stats` に `n_neg_inf`・`n_pos_inf`（伏せないセルでいつも出す）。セルの外に −∞ の原因（頭の記号 H・記号の組 C・記号 B）の人数の欄。
- JSON: `enc` で +∞ を "+inf"、−∞ を "-inf"、NaN は例外。`allow_nan=False` で summary・selftest・書き手ごとの値を書く。

### 共通の母数の保存（判断 6）
- `$DATA_DIR/landscape/tau_mode_candidate_pool_params.<データ>.npz`（repo の中を指したら止める）。`np.savez`（pickle なし）。鍵は `full/<構造>/<母数>`・`excl/<書き手の通し番号>/<構造>/<母数>`・`sbar/…`・`meta`。書き手の ID は書かない。
- `np.savez` は ZIP の時刻が毎回変わるので、provenance にはファイルの SHA-256 と中身のハッシュ（鍵・dtype・shape・bytes）の両方を記す。

### P-REPRO
- `repro_check.py` を、前の試験の summary の葉をすべて辿る比べに変える（数は相対 1e-9、文字列・真偽・None は一致、辞書は前の側の鍵だけ）。全行 × 既存の 4 相手、選ばれた τ・構造・位置、`pool_minus_r1`、`diag`、`n_train`・`n_eval`、`pool_*_diag`、`four_tuple` を照らす。
- 照らさない: `ci`（delta_stats の呼び出しが増え乱数の位置がずれる）・`seconds`・`run_id`・新しい行と相手。HP Z2 でだけ回す門。出すのは照らした数・外れた数・最大の差・外れた節の名前（パネルより上）だけ。

## 2 合成の対照と変異

前の 17 対照と変異（m1〜m3・m6〜m8・m11〜m15）は引き継ぐ。足す:

| 対照 | 通る条件 | 名指しの変異 |
|---|---|---|
| P-MODE | P-POOL の合成で、tau_mode が `ll_zero(mode_of(w を除く共通の S̄))` とちょうど一致し、w を除く共通の評価・全員の共通の S̄ の最頻値とは一致しない | m16 全員の共通の S̄ から作る・m17 w を除く共通の母数を使う |
| P-LIMIT | P-AR (A) の合成で、書き手ごとの \|本人(τ) − 最頻値\| の中央値が τ ∈ {10^5, 3×10^5, 10^6} で増えず、10^6 で \|本人 − 共通\| の中央値より小さい（数値は合成で測ってから置く） | m17 |
| P-AB | 書き手ごとに a + b = 本人 − 共通 が 1e-12。`mode_same` は書き手ごとの差 | m21 中央値どうしの差 |
| P-NEGINF | 記号 25 を書き手 0 の評価の単位（頭 1 本・途中の組 1 つ）にだけ入れた合成で、書き手 0 の最頻値が −∞（NaN でない）、他は有限、`n_*_inf` が手で数えた値と一致、中央値・四分位が並べた値と一致、tau_mode × mode_same が 0、summary に NaN が 0 個、`allow_nan=False` で書ける | m18 ガードの無い `pred_logprob`・m19 −∞ の書き手を集計の前に捨てる |
| P-INFCI | ∞ を含む値の `boot_median` が NaN を返さず、すべて有限なら前の式と同じ値 | m20 ガードの無い linear |
| P-NOSEL | 最頻値にとても良い値を持たせても選びが変わらない | m22 最頻値を τ 他人の候補に足す |
| P-SAME | 合成の書き手 3 人で、tau-extend の `em_writer`（`same_old.py` が別のプロセスで回す）と今回の `em_writer` の `self`・`fold`・`pool`・`r1`・`diag` がちょうど一致 | m23 最頻値の評価の前に rng から 1 回引く |
| P-SAVE | 書いて読み戻すと全鍵が `array_equal` で dtype も一致、2 回書いて中身のハッシュが一致、書く前後で `pools` がビットまで同じ | m24 float32 で書く |

NaN を `enc` の例外で落とすと終了コードが 1 で変異の門（3）にならないので、P-NEGINF では NaN を数えて `passed=false` を返す。本計算では同じ所で例外にする。

## 3 変更するファイル（すべて新しいディレクトリの中）

conditions.md（新）・scripts/hmm2.py（`mode_of`・`pred_logprob_zero`）・scripts/ml.py・scripts/selftest.py（8 対照）・scripts/same_old.py（新・subset_old.py を写して OLD を tau-extend に）・scripts/repro_check.py・scripts/check_mutations.py・mutate.sh・run.sh・scripts/report.py（"-inf" と a・b の表・足した列は作らない）・scripts/timing.py。

## 4 リスク

1. 押下のある量の −∞ の定義と、和 0 の行の扱いは判断 4 が直接決めていない（未決）。
2. AR の H（頭の記号）は共通の中で系列の数しか無いので 0 が多く出るおそれ（推測）。中央値そのものが ±∞ になれば形 5 に落ちる。値を見た後に床を入れない。
3. 前の試験と一致しなくなる道（`rk["self"]` に鍵を足す・rng を引く・∞ が無いのに区間の式を変える・`OPPS` の途中に足す）は P-SAME と P-REPRO で捕まえる。
4. 時間はほぼ増えない見込み（評価の前向き 1 回 × 構造・相手 1 つ分の区間）。timing.py で測る。
5. P-REPRO は HP Z2 の numpy 2.4.4 でしか通らない。P-INFCI は HP Z2 でも回る。
6. a と b の中央値は足し算にならない。表で並べるだけにする。

## 未決だった 2 点（研究者が決めた・判断 8・9）

- 和 0 の行（前の記号 j が他の書き手に一度も出ない C の行）は一様（1/26）を置く。行の中の 0 のセル（和は正）は −∞ のまま。和 0 の行に当たった書き手の人数を出す。
- 押下のある記号の量は、全記号の量が −∞ の書き手では −∞ とする（どこかに確率 0 の記号があれば両方 −∞）。`pred_logprob_zero` の t0 から後を −∞ にする作りはそのままで、押下の量は「全記号が −∞ なら −∞」で上書きする。

## 設計判断の履歴
- 実行回数: 1 回目
- 採用: v2
- 根拠: v1 には本計算で NaN を生む道が 2 つ残っていた（区間の linear・和 0 の行。Mac の numpy 2.5.2 で確かめた）。v2 はそれを塞ぎ、前の試験との一致を Mac の合成でも確かめられる（研究者が選んだ・2026-11-06）。
