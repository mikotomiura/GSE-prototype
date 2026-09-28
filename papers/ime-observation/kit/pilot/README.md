# kit/pilot — 較正パイロットの道具

較正パイロットは、**実測の前に**計器そのもの（正解・入力・時計）が正しいことを確かめ、正解の定義（変換の開始・確定・
取消・候補窓）を実機の呼び出し列で決めるための予行である。Apple も Microsoft も、入力メソッドがテキスト入力欄を
呼ぶ順序を文書にしていないので、順序は実機で見て決める。ここの 4 本の道具は、その材料を出す。

| 道具 | 何を出すか | 入力 |
|---|---|---|
| `call_types.py` | 試行ごとの**呼び出し列の型**（例 `set_marked+ → insert_text`）の、シナリオ × src ごとの件数と、1 試行の実時間（中央値・95 パーセンタイル） | gt・oracle・plan |
| `clock_sync.py` | ブロックごとの**同期マーカー**から、oracle・gt・観測の**時刻差の分布とドリフト** | oracle・（gt）・（keys-only の観測）・マーカーの仕様 |
| `reach.py` | 合成入力が**観測部のフックに届くか**（試行ごとの「送った押下」と「届いた key 行」の比較） | oracle・keys-only の観測 |
| `seal_obs.py` | 単体ロガーの出力から `meta` 行と `key` 行だけを取り出し、元のファイルを**封印**する | 単体ロガーの出力 |

Python 標準ライブラリだけ。各ファイルに `--selftest`（目印 `# kit: selftest`）があり、`bash kit/check.sh` が回す。

## ⚠️ 境界: パイロットは ImeShadow を見ない

パイロットは精度の実測ではない。プロトコルを凍結する前に、観測部の ImeShadow の値を見て、それに合わせて
正解の定義やシナリオを直すと、後の精度の評価が循環する（見てから決めた定義で測ることになる）。だから:

- パイロットの解析は ImeShadow の行を**見ない・数えない・突き合わせない**。使うのは観測側の `key` 行（category と
  press と時刻）だけである。
- 単体ロガーの出力は、**解析より前に**、まず `seal_obs.py` に通す。以後の解析は keys-out だけを読む。
- `call_types.py` / `clock_sync.py` / `reach.py` は、ImeShadow の行を読む記述を**持たない**。観測側の入力に
  `meta` と `key` 以外の行が 1 行でもあれば、内容に触れず拒否する（封印していないファイルを渡した事故を止める）。
- `seal_obs.py` は**許可リスト**で書かれている（残す種類だけを名指し、捨てる種類を名指さない）。捨てた行の
  行数・値・行番号・種類を、標準出力・`seal.json`・エラーメッセージのどこにも出さない。
- ⚠️ 封印したファイルを**開く**道具は作らない。開けてよいのは、プロトコルを凍結した後の解析パイプラインだけ。
- ⚠️ 元のバイト数は `seal.json` に記録する（プロトコルが求める）。keys-out のバイト数との差から、捨てた行の
  **バイト数の合計**は逆算できる（行数・値は分からない）。この粗い量を許容するかは、プロトコルの側で決める。

## 手順（macOS と Windows の較正パイロットで、この順に使う）

1. **参照入力欄だけ**を動かして S1〜S15 を各数回流し、gt（呼び出し列）と oracle（送った押下）を記録する。
   Windows は IMM 互換と TSF の両経路を記録する。
   同時に単体ロガーも走らせ、obs を出させる（ImeShadow を含んでよい。人は開かない）。
2. **すぐに封印する**:
   ```bash
   python3 kit/pilot/seal_obs.py --obs obs.jsonl --keys-out obs.keys.jsonl --sealed-dir sealed/
   ```
   `obs.jsonl` は `sealed/` へ移り（元の場所からは消える）、`sealed/seal.json` に元の SHA-256・バイト数・封印時刻が残る。
   `obs.keys.jsonl` は `obs/1` の検査器（`kit/formats/validate_logs.py --kind obs`）を通る。
   keys-out が既にある・封印先に同名のファイルか `seal.json` が既にあるときは、何も動かさずに止まる。
3. **呼び出し列の型**を数える:
   ```bash
   python3 kit/pilot/call_types.py --gt gt.jsonl --oracle oracle.jsonl --plan plan.jsonl --out call_types.json
   ```
   Windows は経路ごとの gt で 2 回回し、出力の `types` を並べて、両経路が同じ区間を返すかを見る（食い違えばそれ自体を報告する）。
4. **フックへの到達**を確かめる（観測側は keys-only）:
   ```bash
   python3 kit/pilot/reach.py --oracle oracle.jsonl --obs-keys obs.keys.jsonl --out reach.json
   ```
5. **時計の対応**を出す:
   ```bash
   python3 kit/pilot/clock_sync.py --oracle oracle.jsonl --gt gt.jsonl --obs-keys obs.keys.jsonl \
       --marker marker.json --out clock_sync.json
   ```

出力の JSON は実験の記録に置いてよい。生ログ（gt・oracle・plan・obs・封印したファイル）は git に入れない。

## 出力の読み方

### `call_types.py`

- `by_scenario.<S>.types` = 型の文字列 → 件数（多い順）。型は呼び出しの名前を「 → 」でつなぎ、同じものが 2 回以上
  続くと「+」に畳む。`do_command` は `cmd`、`notify` は `imn`、`ui_*` は `ui_kind` を「[…]」で添える。
- 同じシナリオで型が**割れる**なら、正解の定義はその割れ方を受け止められる形にする（取消と確定の区別・候補窓の
  有無など）。1 つの型に揃うなら、その型が定義の根拠になる。
- `duration_ms` = 1 試行の実時間（oracle の `trial_begin` から `trial_end`）。実測全体の所要時間と n の見直しに使う。
- `unassigned_events` が多いなら、時計が合っていない（`--clock` を変える・`--pre-ms` / `--tail-ms` を広げる）か、
  試行の間に呼び出しが来ている。`planned_not_run` は、計画にあって oracle に無い試行の数。

### `reach.py`

- `reach_rate` = Σ min(送った, 届いた) / Σ 送った。`diff_distribution` は試行ごとの（届いた − 送った）の分布で、
  0 ばかりなら全部届いている。負の値の試行が並ぶなら、その数だけ取りこぼしている（`per_trial` で試行を探せる）。
- 擬似キー（`mouse_click` / `focus_away` / `focus_back`）は実キーではなく `key` 行を作らないので数えない（`--ignore-keys` で変えられる）。
  ⚠️ 観測部が観測しないキー（GSE の macOS は観測対象の外のキーを `key` 行に出さない）を送ると、
  「届かなかった」に見える。それも到達率の結果である（どのキーが届かないかは、試行の型から読む）。
- `outside_trials_rows` = どの試行の区間にも入らない `key` 行（ブロック頭のマーカーのキーがここに入る）。

### `clock_sync.py`

マーカーの仕様（JSON）:

```json
{"oracle_keys": ["f13", "f14", "f15"], "gt_vks": [105, 107, 113], "obs_categories": ["function", "function", "function"], "max_gap_ms": 150}
```

- マーカーのキーは**観測側の `key` 行に出る**こと・**IME の状態を変えない**ことが要る（観測部が観測しないキーは
  `key` 行に出ないので、マーカーにならない）。3 つの並びの先頭は、同じ押下に対応させる。
- 観測側の `key` 行は category（14 種）だけなので、マーカーは「category の並び ＋ 間隔」で見つける。並びが
  途切れずに続き、隣り合う間隔が `max_gap_ms` 以下の箇所だけを拾う（間隔は gt が単調時計・観測が壁時計）。
- ブロックへの対応づけは、oracle の先頭のキーの時刻の前後 `--window-ms`（既定 3000）以内で最も近い出現を、
  一対一で割り当てる。**見つからなかったブロックは `missing` に出る**（黙って捨てない）。どのブロックにも
  対応しない出現は `unmatched_occurrences`。時計のずれが窓を超えると全部見つからないので、窓を広げる。
- 差 = 各側の先頭のキーの時刻 − oracle の先頭のキーの時刻（ms）。⚠️ **遅延（送出から記録までの時間）と時計の
  ずれは分けられない**（差にはその和が出る）。ブロックをまたいで変わらないなら遅延＋一定のずれ、ブロック番号
  （時間）とともに動くならドリフト。
- 各差に、中央値・最小・最大・`offset_at_start_ms`（最初のブロックの時刻での当てはめ値）・`drift_ms_per_hour`
  （oracle のマーカーの時刻に対する最小二乗の傾き）・`residual_max_ms`（当てはめ直線からの最大のずれ）・ブロックごとの値がある。
  ブロックが 2 つ未満なら `drift_ms_per_hour` は `null`。
- `gt_minus_oracle_mono` は単調時計の差。観測側は壁時計（Unix ms）だけを持つので、観測の差は壁時計だけ。
  壁時計と単調時計のどちらが gt と oracle で揃っているかは、この 2 つの差を見て決める。

### `seal_obs.py`

- 標準出力: 封印した名前・元の SHA-256・バイト数・残した key 行の数・keys-out と `seal.json` の場所。
- keys-out の `meta` 行は、ヘッダのキーと、`capabilities` の名前のうち `key` だけを残して作り直す（ImeShadow の名前が
  meta にも残らない）。`key` 行は元のまま。
- 読めない行・1 行目が `meta` でない・`meta` が 2 つ以上あるファイルは、何も動かさずに拒否する（exit 1）。

## 終了コード

| 道具 | 0 | 1 | 2 |
|---|---|---|---|
| `call_types.py` | 出した | 完結した試行が 1 つも無い | 入力が読めない・使い方の誤り |
| `clock_sync.py` | 出した | oracle にマーカーの揃ったブロックが無い・指定した側で 1 ブロックも見つからない | 同上 |
| `reach.py` | 集計した | 集計できる送信が 1 つも無い | 同上 |
| `seal_obs.py` | 封印した | 拒否（元のファイルは動かさない） | 使い方の誤り |

空振りを緑にしない（測るものが 1 つも無いときは 1 を返す）。一部のブロック・試行が欠けているだけなら 0 で、
欠けた分は出力の `missing` / `trials_incomplete` などに出る。
