# Keystroke symbolization

This kit turns a keystroke log into one symbol per second, the sequence that the per-person
models in the paper are fitted to. It uses only the time and the category of each key press;
no characters or text are read into the symbolizer.

## Layers

1. **Adapters** (`adapters/`): raw data to a list of key presses `(t_ms, category)`.
   - `coauthor.py`: one CoAuthor session log (Lee, Liang and Yang, CHI 2022).
   - `cs1_2021.py`: the rows of one (student, assignment) of the CS1 keystroke data, 2021
     release (Edwards, Hart and Shrestha, Journal of Educational Data Mining, 2023), split
     into work blocks at gaps of 30 minutes or more.
   - `categories.py`: the category of one typed character.
2. **Symbolizer** (`symbolizer.py`): key presses to rows `(t_ms, x, y, symbol, alpha, path)`.
3. **Constants** (`constants.json`): every numeric value used by the symbolizer.

## What the symbolizer does

A synthetic release is added 100 ms after each press (earlier if the next press comes
sooner). Every second, five features are computed over the key events of the last 30 s:
the median flight time, the share of deletions, the mean burst length, the number of pauses
of 2 s or more, and the share of deletions followed by such a pause. Each feature is
normalized against a fixed reference value, and two weighted sums give two raw composite
values x and y (not read as states). These are smoothed exponentially (weight 0.3 while
typing; 0.15, 0.18 or 0.25 during pauses, by pause length) and mapped to a 5 x 5 grid,
giving symbols 0 to 24. Symbol 25 replaces the grid symbol at the first typing second after
a run of 14 or more consecutive deletions. During pauses the features are replaced by
pause-dependent values, so a symbol is still emitted every second. Navigation, escape and
other non-typing keys are ignored.

Floating-point expressions are evaluated in a fixed order, so the output, including x and y,
is reproducible bit for bit.

## Variants without smoothing and without overlapping windows

`variants.py` derives two further columns from the same rows, for checking how much of the
dependence between consecutive symbols the symbolization itself produces.

- **u (unsmoothed)**: the grid symbol of the raw values `x_raw` and `y_raw` of the same tick, before
  the exponential smoothing, with the same 5 x 5 grid. A row whose symbol is the deletion-run symbol
  (25) keeps 25. The rows are the same as those of the symbols (same times, same number).
- **n (non-overlapping)**: within one recording (a CoAuthor session or a CS1 work block), with `s`
  the time of the first row, only the rows at `s + 30 s * j` (j = 1, 2, ...) are kept, using their
  u symbols. The 30 s windows of the kept rows do not overlap. When no row exists at such a time,
  that j is skipped.

`variant_rows(t0, presses)` returns `(t_ms, o, u, x_raw, y_raw, x, y, alpha, path)`, where `o`,
`x`, `y`, `alpha` and `path` are the values returned by `symbolize` for the same input.
`thinned_mask(times)` returns the rows of column n for the row times of one recording. The symbolizer
keeps the raw values of the last tick in the attribute `last_raw`; this does not change its rows.

Both variants still carry memory across windows: during pauses, the features depend on the time
since the last press and on the context of the preceding typing. Column n is therefore not free
of every source of dependence between symbols.

## Input contract

`symbolize(t0, presses)` expects non-negative integer times in milliseconds, presses sorted
by time (ties keep their order), and categories from `constants.json`. Other time values,
unsorted input and unknown categories raise `ValueError`. Presses before `t0` are discarded, as in the original
implementation. One row is produced for every second from `t0` to the last event (pauses of
2 s or more included), so the run time grows with the time span of a recording.

## Checks

- `python3 selftest.py` runs unit checks of the adapters, the symbolizer and the variants (the
  rows of `variant_rows` equal those of `symbolize` on the 300 synthetic cases, bit for bit) and then
  the conformance check.
- `python3 conformance/check.py` symbolizes 300 synthetic key-press sequences
  (`conformance/data/inputs.json.gz`, regenerated from seed 20261107 by
  `conformance/generate_inputs.py`) and compares every row, with x and y bit for bit, with
  the expected traces (`conformance/data/expected.json.gz`) produced by the original
  implementation used in the paper. The synthetic sequences contain no human data.
- In the author's own check on the raw datasets, the symbols of every CoAuthor session
  (1,157 sessions, 775,907 rows) and of every CS1 2021 assignment with at least two key
  presses (177 assignments, 2,794,277 rows) were identical to those of the original
  implementation, including the bits of x and y. That check used the raw datasets and is not
  part of this kit. Readers can repeat its outcome with the per-record hashes below.

## Per-record hashes

`hashes/coauthor_sha256.csv` and `hashes/cs1_2021_sha256.csv` give, for each of these sessions
and assignments, the number of rows and two SHA-256 hashes: one of the symbols and one of the
rows with x and y written bit for bit (`hashes/hashes.py` defines both). Records are keyed by the
datasets' public identifiers (the CoAuthor session id; the CS1 SubjectID and AssignmentID). The
column `in_analysis` marks the 875 CoAuthor sessions with a single observed interval, which the
analyses use; CS1 uses all 177 assignments. The lists contain hashes only: no symbols, no
per-writer values and no text. With the public data downloaded:

```
cd hashes
python3 -I hashes.py check coauthor <path to the CoAuthor archive .zip> coauthor_sha256.csv
python3 -I hashes.py check cs1 <path to keystrokes.csv of the 2021 release> cs1_2021_sha256.csv
```

Each prints the number of records and of mismatches and exits with 1 if any record differs.
The hashes were produced by running this kit on the raw data and match the hashes of the symbol
sequences read by the analysis code.

## Requirements

Python 3 with the standard library only. The character categories use Python's Unicode
predicates (`str.isalpha`, `str.isdigit`); the checks were run with Python 3.14.4
(Unicode 16.0.0).
