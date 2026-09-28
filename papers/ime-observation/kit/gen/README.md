# kit/gen — シナリオ生成器

`corpus/1`（句と読み）と OS ごとの**キーの手順**（`recipes.json`）から、1 セル分の試行計画 `plan/1`
（形式は [`../formats/FORMATS.md`](../formats/FORMATS.md)）を出す。実行器はこの計画だけを見て送出する。

| ファイル | 中身 |
|---|---|
| `generate_plan.py` | 生成・検査（`--validate`）・所要時間の見積もり（`--estimate`）・selftest |
| `romaji.py` | ひらがな → ローマ字のキー列（決定的な 1 つの表）。`--keys 'がっこう'` で確かめられる |
| `recipes.json` | **手順のデータ**（OS × シナリオ）と、S12 のかな配列 |

Python 標準ライブラリだけで動く。どの検査も `python3 <file> --selftest`（速い既定・数秒以内）。

## 使い方

```sh
# 計画を作る（同じ入力・同じ seed で、同じ機械・同じ Python ならバイト一致）
python3 generate_plan.py --corpus corpus.jsonl --recipes recipes.json --config config.json \
    --os macos --seed 20260928 --out plan.jsonl

# 計画を検査する（違反は行番号つきで stderr に出て exit 1。値は出さない）
python3 generate_plan.py --validate plan.jsonl

# 1 セルの所要時間（秒）。最後の行が数 1 つだけ。--corpus が無ければ読みの長さを仮定する
python3 generate_plan.py --estimate --config config.json --recipes recipes.json --os macos [--corpus corpus.jsonl]
```

Exit: 0 = 成功 ／ 1 = `--validate` が違反を見つけた ／ 2 = 使い方の誤り・入力（設定・コーパス・recipes）が読めない。

## 設定のキー

`config.json` は 1 セル分の設定。本番の値は決めていない（速さ・思考の間・n は実験の凍結で出典つきで入れる）。
ここでは**読むだけ**で、名前はこのとおり。`_` で始まるキーはメモとして無視する。

| キー | 型 | 既定 | 意味 |
|---|---|---|---|
| `n_per_cell_scenario_speed` | 整数 ≥ 1 | 75 | シナリオ × 速さごとの試行数 |
| `block_size` | 整数 ≥ 1 | 25 | 1 ブロックの試行数（最後のブロックは端数） |
| `scenarios` | 配列 | recipes の既定で有効なもの | 有効なシナリオ（`S1`〜`S15`）。OS に手順が無いもの（例: windows の `S11`）は飛ばす |
| `speeds` | オブジェクト | 必須 | `slow` / `mid` / `fast` それぞれ `iki_median_ms`（> 0）と `iki_sigma`（≥ 0）。キー間隔は対数正規 |
| `key_hold_ms` | 整数 ≥ 1 | 必須 | 押してから離すまで |
| `think_ms` | `{min, max}` | 必須 | 思考の間（対数一様）。手順の `pause: think` に使う |
| `cand_index_max` / `nav_count_max` | 整数 ≥ 0 | 必須 | 候補番号・矢印の回数の上限 |
| `inter_trial_ms` | 整数 ≥ 0 | 必須 | 試行行の `gap_before_ms` に書く |
| `marker` / `marker_gap_ms` | keyname の配列 / 整数 | 必須 | ブロック行にそのまま書く |
| `reset_ime_every_block` | 真偽値 | 必須 | ブロック行の `reset_ime` |
| `assumed_reading_len` | 整数 ≥ 2 | 12 | `--estimate` で `--corpus` が無いときの読みの長さ |
| `kana_len_min` / `kana_len_max` | 整数 | 4 / 8 | S12 の合成かな列の長さ |

`plan/1` のヘッダの `config_sha256` は、設定ファイルの**バイト列**の SHA-256（CLI が計算する）。

## 生成の規則

- **ブロックは速さで揃える**（1 ブロック = 1 つの速さ）。速さごとに試行を seed で並べ替えて `block_size` ずつに区切り、
  ブロックの並びも seed で並べ替える。ブロックの中の試行順（シナリオの並び）も seed で決まる。
  - ブロック数は「速さごとの `ceil(シナリオ数 × n / block_size)` の合計」。シナリオ数 × n が `block_size` の倍数なら
    `ceil(件数 / block_size)` と一致する。倍数でないと速さごとに端数のブロックができ、その分だけ増える。
- **時刻**: `at_ms` は試行の先頭からの相対で、最初のキーが 0。各キーは押下（`down: true`）と離し（`down: false`・
  `key_hold_ms` 後）の 2 ステップで、直列に並べる（次の押下は前の離しより後）。
  キー間隔は「押下から次の押下まで」で、`key_hold_ms + 1` を下限にする。
- **思考の間・固定の間**: 手順の `pause` は、その前のキーの押下から次のキーの押下までの間を**置き換える**（足さない）。
  試行の最初と最後にある間は無視する。`think_ms` は試行行に、使った値（使わない手順は 0）を書く。
- **句の選び方**: シナリオごとに句を並べ替えて順に使い、尽きたら並べ直す。S12 は、かな配列だけで読みが書ける句を優先して
  使い、足りなければ seed 固定の**合成かな列**（`phrase_id` が `kana-` で始まる）で埋める。合成かな列の読みは
  `kana_layout` の逆引きで `steps` から復元できる。
- **乱数**: `random.Random` の `random()` だけを使う（版で変わりうる `shuffle` / `choice` は使わない）。
  試行ごとの乱数は `(seed, trial_id)` から決まる（`trial_rng`）。だから `build_trial` に同じ句・同じ `trial_rng` を渡すと、
  CLI が書いた計画の該当行と一致する。
  ⚠️ 浮動小数点の演算は OS の数学ライブラリに依るので、バイト一致を保証するのは同じ機械・同じ Python での再生成まで。
  別の OS で計画を作り直さず、作った計画のファイルを配る。

## 公開している関数（他の部品が import する）

```python
build_trial(phrase, scenario, speed, os_name, recipes, config, rng, trial_id, block_id) -> dict   # plan/1 の試行行 1 つ
load_recipes(path) -> dict
```

ほかに `trial_rng(seed, trial_id)`・`load_corpus(path)`・`normalize_config(config)`・`plan_rows(...)`・
`render_plan(rows)`・`validate_plan(data)` がある。`phrase` は `corpus/1` の句の行（`phrase_id`・`reading` が要る）。

## recipes.json の書き方

`os.<macos|windows>.<S1〜S15>` に `steps`（手順）と `intent`（意図の既定値）を書く。**パイロットの後に直すのは
このデータだけ**で、コードは触らない。直したら `--selftest` と `--validate` を回す（書式の誤りは読み込みで止まる）。

`steps` の要素:

| 要素 | 意味 |
|---|---|
| `{"type_reading": true}` | 読みを打つ。`"part": "first_half"` で前半だけ（S10）、`"input": "kana"` でかな配列（S12） |
| `{"key": "space"}` | キーを 1 回。`keyname` は FORMATS.md の列挙 |
| `{"repeat": "space", "times": "cand_index+1"}` | キーを繰り返す。`times` は整数か `cand_index+1` / `nav_count` / `reading_len` |
| `{"digit": "cand_index+1"}` | 数字キー（1〜9 番の候補を選ぶ） |
| `{"pause": "think"}` | 思考の間 |
| `{"pause_ms": 21000}` | 固定の間（ms） |

そのほかの項目:

- `params`: 試行ごとに抽選する値。`{"cand_index": {"min": 1, "max": "cand_index_max", "cap": 8}}` のように書く
  （`max` は整数か設定のキー名、`cap` は上限の頭打ち）。`intent` から `{"$param": "cand_index"}` で参照する。
- `intent`: `plan/1` の 8 キーをすべて書く（値は `FORMATS.md` の表）。
- `default_enabled`: `false` だと `scenarios` を省略したときに出ない（S9 は手順が未定義で、明示しても止まる）。
- `reading_len`: `{"min": 2}` のように、そのシナリオで使う読みの長さの範囲。
- `kana_layout`: S12 用。`keyname` → 打てるかな（JIS かな配列で `keyname` だけで打てるもの）。

## 限界と未確定

- ⚠️ 既定の手順（ESC の回数・予測候補のキー・IME の ON / OFF のキーなど）は**仮説**。OS・IME で違い、較正パイロットで直る見込み。
- ⚠️ `romaji.py` の綴り（`ん` = `nn`、促音は子音を重ねる、拗音の綴りなど）も、実際の IME がどう解釈するかは実機で確かめる。
  表を直すと、逆写像の一意性の selftest がすぐ赤で知らせる。
- 本番の速さ・思考の間・n は未確定。`--estimate` は設定と recipes の**通り**に試算するだけで、
  IME のリセットや前面化の時間は含まない。
