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
normalized against a fixed reference value, and two weighted sums give a raw friction
value x and a raw fluency value y. These are smoothed exponentially (weight 0.3 while
typing; 0.15, 0.18 or 0.25 during pauses, by pause length) and mapped to a 5 x 5 grid,
giving symbols 0 to 24. Symbol 25 replaces the grid symbol at the first typing second after
a run of 14 or more consecutive deletions. During pauses the features are replaced by
pause-dependent values, so a symbol is still emitted every second. Navigation, escape and
other non-typing keys are ignored.

Floating-point expressions are evaluated in a fixed order, so the output, including x and y,
is reproducible bit for bit.

## Input contract

`symbolize(t0, presses)` expects non-negative integer times in milliseconds, presses sorted
by time (ties keep their order), and categories from `constants.json`. Other time values,
unsorted input and unknown categories raise `ValueError`. Presses before `t0` are discarded, as in the original
implementation. One row is produced for every second from `t0` to the last event (pauses of
2 s or more included), so the run time grows with the time span of a recording.

## Checks

- `python3 selftest.py` runs unit checks of the adapters and the symbolizer and then the
  conformance check.
- `python3 conformance/check.py` symbolizes 300 synthetic key-press sequences
  (`conformance/data/inputs.json.gz`, regenerated from seed 20261107 by
  `conformance/generate_inputs.py`) and compares every row, with x and y bit for bit, with
  the expected traces (`conformance/data/expected.json.gz`) produced by the original
  implementation used in the paper. The synthetic sequences contain no human data.
- On the two datasets, the symbols of every CoAuthor session (1,157 sessions, 775,907 rows)
  and of every CS1 2021 assignment with at least two key presses (177 assignments,
  2,794,277 rows) were identical to those of the original implementation, including the
  bits of x and y. That comparison used the raw datasets and is not part of this kit.

## Requirements

Python 3 with the standard library only. The character categories use Python's Unicode
predicates (`str.isalpha`, `str.isdigit`); the checks were run with Python 3.14.4
(Unicode 16.0.0).
