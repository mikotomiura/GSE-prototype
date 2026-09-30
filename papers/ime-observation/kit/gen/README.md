# kit/gen — scenario generator

Produces a trial plan `plan/1` (schema in [`../formats/FORMATS.md`](../formats/FORMATS.md)) for one cell,
from `corpus/1` (phrases and readings) and the OS-specific **key procedures** (`recipes.json`). The
executor reads only this plan when sending input.

| File | Content |
|---|---|
| `generate_plan.py` | Generation, validation (`--validate`), duration estimation (`--estimate`), and the selftest |
| `romaji.py` | Hiragana-to-key-sequence conversion (one deterministic table). Try it with `--keys 'がっこう'` |
| `recipes.json` | The procedure data (OS x scenario) and the kana layout used by one scenario |

Python standard library only. Every check runs as `python3 <file> --selftest` (fast default, a few
seconds at most).

## Usage

```sh
# Build a plan (byte-identical for the same input, seed, machine, and Python version).
python3 generate_plan.py --corpus corpus.jsonl --recipes recipes.json --config config.json \
    --os macos --seed 20260928 --out plan.jsonl

# Validate a plan (violations are printed to standard error with line numbers; exit 1).
python3 generate_plan.py --validate plan.jsonl

# Duration (seconds) for one cell. The final line is a single number.
# If --corpus is omitted, an assumed reading length is used instead.
python3 generate_plan.py --estimate --config config.json --recipes recipes.json --os macos [--corpus corpus.jsonl]
```

Exit codes: 0 = success / 1 = `--validate` found a violation / 2 = usage error, or an input (config,
corpus, or recipes) could not be read.

## Configuration keys

`config.json` describes one cell. Production values are not yet fixed (speed, think time, and n will be
added with a citation when the protocol is frozen). This tool only reads the file; the key names below are
authoritative. A key starting with `_` is treated as a note and ignored.

| Key | Type | Default | Meaning |
|---|---|---|---|
| `n_per_cell_scenario_speed` | integer >= 1 | 75 | Trials per scenario-speed cell |
| `block_size` | integer >= 1 | 25 | Trials per block (the last block may hold fewer) |
| `scenarios` | array | every scenario enabled by default in recipes | Enabled scenarios (`S1`-`S15`). A scenario with no procedure for the OS (e.g. `S11` on windows) is skipped. `S11` assumes live conversion is on, so it must be explicitly excluded from `scenarios` in a cell where live conversion is off (the implicit default, when `scenarios` is omitted, includes `S11` on macOS) |
| `speeds` | object | required | `slow` / `mid` / `fast`, each with `iki_median_ms` (> 0) and `iki_sigma` (>= 0). Key interval is log-normal |
| `key_hold_ms` | integer >= 1 | required | Time from key-down to key-up |
| `think_ms` | `{min, max}` | required | Think time (log-uniform). Used wherever the procedure has `pause: think` |
| `cand_index_max` / `nav_count_max` | integer >= 0 | required | Upper bound on the candidate index / arrow-key count |
| `inter_trial_ms` | integer >= 0 | required | Written to the trial row's `gap_before_ms` |
| `marker` / `marker_gap_ms` | array of keynames / integer | required | Written directly to the block row |
| `reset_ime_every_block` | boolean | required | Written to the block row's `reset_ime` |
| `assumed_reading_len` | integer >= 2 | 12 | Reading length assumed by `--estimate` when `--corpus` is omitted |
| `kana_len_min` / `kana_len_max` | integer | 4 / 8 | Length range for the synthetic kana strings used by one scenario |

The `config_sha256` / `recipes_sha256` / `corpus_sha256` fields in the `plan/1` header are the SHA-256 of
the **byte contents** of the config, `--recipes`, and `--corpus` files (computed by the CLI). They tie each
plan to the exact version of the procedures and stimuli it was built from, since the recipes may be revised
after a calibration pilot.

## Generation rules

- **Blocks are homogeneous in speed** (one block = one speed). Trials for each speed are ordered by the
  seed and cut into chunks of `block_size`; the order of blocks is also permuted by the seed. The order of
  trials (the scenario sequence) within a block is likewise seed-determined.
  - The number of blocks is the sum, over each speed, of `ceil(number of scenarios x n / block_size)`. When
    the scenario count times n is a multiple of `block_size`, this equals `ceil(trial count / block_size)`;
    otherwise each speed contributes a partial block, increasing the total.
- **Timing**: `at_ms` is relative to the start of the trial, with the first key at 0. Each key is two
  steps, a press (`down: true`) and a release (`down: false`, after `key_hold_ms`), placed strictly in
  sequence (the next press follows the previous release). The key interval, measured from one press to the
  next, is floored at `key_hold_ms + 1`.
- **Think time and fixed pauses**: a `pause` step in the procedure **replaces** (does not add to) the
  interval from the previous key's press to the next key's press. A pause at the very start or end of a
  trial is ignored. `think_ms` is written to the trial row with the value actually used (0 for a procedure
  that never pauses).
- **Phrase selection**: phrases are drawn per scenario, cycling through a shuffled order and reshuffling
  once exhausted. One scenario draws only from phrases that can be typed on the kana layout, falling back,
  once those run out, to a seed-determined **synthetic kana string** (`phrase_id` starting with `kana-`).
  The reading of a synthetic kana string can be recovered from its `steps` through the inverse of
  `kana_layout` (see `typed_reading`).
  The `kana-N` numbering is a running count **local to that plan file** (restarting at 1 on every call to
  `plan_rows`): `kana-3` in one plan and `kana-3` in another (a different seed or corpus) need not be the
  same phrase, so **do not match on `phrase_id` across plans**. The reading actually typed should always be
  recovered from the trial itself, via `typed_reading(trial, recipes)`.
  A `corpus/1` input passed via `--corpus` may not itself contain a `phrase_id` starting with `kana-`
  (`load_corpus` rejects it, so it cannot collide with a generator-produced synthetic kana string's id).
- **`reading_len` is not the same as what was actually typed**: the trial row's `reading_len` is the
  **length of the phrase's reading** (the character count of `reading` in `corpus/1`), not the length of
  what was typed with the keys (one scenario types only the first half; another types a synthetic kana
  string). To recover the reading (in hiragana) that was actually typed, use
  `typed_reading(trial, recipes)`.
- **When to bump `GENERATOR_VERSION`**: bump it whenever the meaning of `romaji.py`'s table (spelling) or
  of `recipes.json` (the procedures, the default `intent` values, or the `kana_layout` mapping) changes.
  The header's `generator_version` records which version of the generator's interpretation a plan was built
  under (the recipes' and corpus's own versions are tracked separately, through `recipes_sha256` and
  `corpus_sha256`).
- **Randomness**: only `random.Random`'s `random()` is used (never `shuffle` / `choice`, whose behavior can
  change across Python versions). Each trial's random state is derived from `(seed, trial_id)`
  (`trial_rng`), so calling `build_trial` with the same phrase and the same `trial_rng` reproduces the
  matching row of a plan the CLI wrote.
  Floating-point arithmetic depends on the platform's math library, so byte-identical output is only
  guaranteed when regenerating on the same machine and the same Python version. A plan built on one OS is
  distributed as a file rather than rebuilt on another.

## Public functions (importable by other components)

```python
build_trial(phrase, scenario, speed, os_name, recipes, config, rng, trial_id, block_id) -> dict   # one plan/1 trial row
load_recipes(path) -> dict
typed_reading(trial, recipes) -> str   # the reading (in hiragana) actually typed for this trial row
```

`typed_reading` takes one `plan/1` trial row (the return value of `build_trial`, or a row read back from a
plan file) and the return value of `load_recipes`, and reconstructs what was typed by reading only the
`down: true` keys in `steps` (romaji input through `romaji.from_keys`; the kana-input scenario through the
inverse of `recipes.kana_layout`). The typed reading ends at the first key that scenario does not use for
typing the reading. An ordinary scenario returns the full phrase reading, one scenario returns only the
first half, and another returns the synthetic kana string as-is. This is distinct from `reading_len` (the
phrase's reading length); the two should not be confused.

Also exported: `trial_rng(seed, trial_id)`, `load_corpus(path)`, `normalize_config(config)`,
`plan_rows(...)`, `render_plan(rows)`, `validate_plan(data)`. `phrase` is one phrase row from `corpus/1`
(needs `phrase_id` and `reading`).

## Writing recipes.json

`os.<macos|windows>.<S1-S15>` holds `steps` (the procedure) and `intent` (the default interpretation).
**Only this data should be edited after a calibration pilot**; the code should not need to change. After
editing, run `--selftest` and `--validate` (a malformed entry stops at load time).

Elements of `steps`:

| Element | Meaning |
|---|---|
| `{"type_reading": true}` | Type the reading. `"part": "first_half"` types only the first half; `"input": "kana"` types via the kana layout |
| `{"key": "space"}` | One key press. `keyname` follows the enumeration in FORMATS.md |
| `{"repeat": "space", "times": "cand_index+1"}` | Repeat a key. `times` is an integer or one of `cand_index+1` / `nav_count` / `reading_len` |
| `{"digit": "cand_index+1"}` | A digit key (selecting candidate 1-9) |
| `{"pause": "think"}` | A think pause |
| `{"pause_ms": 21000}` | A fixed pause (ms) |

Other entries:

- `params`: values drawn per trial, e.g. `{"cand_index": {"min": 1, "max": "cand_index_max", "cap": 8}}`
  (`max` is an integer or a config key name; `cap` is an upper clamp). Referenced from `intent` via
  `{"$param": "cand_index"}`.
- `intent`: must set all 8 `plan/1` keys (values follow the table in `FORMATS.md`).
- `default_enabled`: when `false`, the scenario is left out unless `scenarios` names it explicitly (one
  scenario has no defined procedure, so naming it explicitly still stops the run).
- `reading_len`: the reading-length range this scenario draws from, e.g. `{"min": 2}`.
- `kana_layout`: for the kana-input scenario. Maps `keyname` to the kana it types (restricted to keys that
  type a kana directly on the JIS kana layout).

## Limitations and open questions

- The macOS procedures were revised after the first calibration pilot (macOS 27, the standard Japanese input
  method, live conversion on). There, after a conversion, a Return in the candidate window only picks the
  candidate and a second Return commits; a digit pick is likewise followed by Return; and each Escape steps the live
  conversion back one stage (converted text, then kana, then the romaji spelling), so cancelling before a
  conversion takes up to three; the procedure presses four, since an extra Escape outside a composition only reaches
  the field as a command. The same behaviour was seen with keys
  typed by hand, so it belongs to the input method, not to the synthetic events. A cell with live conversion off
  has not been piloted and may need its own recipes file (`--recipes`), since an extra Return there would insert
  a line break.
- The default procedures (number of Escape presses, the predictive-candidate key, the IME on/off keys, and
  similar details) are **hypotheses** that are expected to vary by OS and IME and to be revised after a
  calibration pilot.
- Whether `romaji.py`'s spelling conventions (`ん` as `nn`, a doubled consonant for the small `っ`, the
  spelling of contracted sounds, and so on) match how a real IME interprets them can only be confirmed on
  real hardware. Editing the table immediately shows up as a failure in the reverse-mapping uniqueness
  check of the selftest.
- Production speed, think time, and n are not yet fixed. `--estimate` computes a duration strictly from the
  config and recipes as written; it does not include IME reset time or window-activation time.
