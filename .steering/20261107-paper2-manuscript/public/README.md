# What moves with the pause definition and the adjustment

Code, conditions and aggregate results of the manuscript *What moves with the pause definition and the adjustment: a
multiverse diagnostic of pause and stall labels in keystroke logs* (Mikoto Miura, submitted to the Journal of
Educational Data Mining). [日本語](README.ja.md)

Archive: [10.5281/zenodo.24047695](https://doi.org/10.5281/zenodo.24047695)

![Stall rate and essay score across 90 definitions](docs/media/score.svg)

A window-based stall detector was applied to four keystroke datasets released for research (two editions of an
introductory programming course, CS1 2019 and CS1 2021; the KLiCKe essay corpus; the CoAuthor corpus of writing with
model suggestions). Its window, threshold, stop condition and segmentation were varied over 89 definitions around a
baseline, and a fixed-threshold pause detector (18 definitions, and 18 with a writer quantile as a control) was added.
Each conclusion is reported with an interval from resampling writers. The figure shows one of them: the correlation of
the stall rate with the holistic essay score is negative for most definitions and positive only where a 15-s window
meets a writer-quantile threshold (a), and given essay length no definition is negative (b).

## Contents

| Path | What it holds |
|---|---|
| `experiments/20261107-stall-shape-multiverse/scripts/` | The detector, the 90 definitions and every computation of the paper |
| `experiments/20261107-stall-shape-multiverse/results/` | Aggregate results per definition (JSON) |
| `experiments/20261107-stall-shape-multiverse/conditions*.md` | The conditions committed before each computation, in Japanese (redacted copies, see `REDACTED.md`) |
| `experiments/20261107-stall-shape-multiverse/conditions-summary-en.md` | English summary of the conditions, in the order of Supplement S1 |
| `experiments/20261107-stall-shape-multiverse/notes.md` | The record of each computation and its reading (Japanese, redacted) |
| `experiments/20261103-stall-candidates-c1c2c6/candidates.py` | The two definitions of the original module that the scripts use, copied verbatim |
| `experiments/2026110{1,4}-*/scripts/`, `experiments/20261031-*/scripts/` | Conversion scripts of the datasets, byte-identical to those of the companion archive |
| `paper/` | The LaTeX sources of the manuscript and supplement; `paper/figdata/` holds the figure data (per definition) |
| `tools/verify.py` | Checks that the archive holds no raw data, per-writer table, identifier, secret or local path |
| `tools/readme_media.py` | Draws the figure above from `paper/figdata/score.csv` |

## What is not here

- The datasets. KLiCKe and CoAuthor are public; the CS1 files are released by their authors on request, and for CS1
  only aggregate values are published, by agreement with the data authors.
- Per-writer values, writer identifiers and the intermediate files (they stay outside the repository).
- The working files with observation intervals, which come from the estimator of the companion study. Building them
  needs the companion archive, [10.5281/zenodo.24026278](https://doi.org/10.5281/zenodo.24026278) (estimator,
  conversion and replay); the companion manuscript is available as a preprint,
  [10.5281/zenodo.24026330](https://doi.org/10.5281/zenodo.24026330).
- The author's internal working notes. In the Japanese conditions and notes, references to them were replaced by
  `[internal reference removed]`; `REDACTED.md` lists the SHA-256 of each original file and the number of references
  removed.

## Reproducing

1. Build the working files with the companion archive (its README describes the conversion of each dataset and the
   replay of the estimator).
2. With Python 3, NumPy, SciPy and statsmodels (versions in `experiments/20261107-stall-shape-multiverse/env.md`; `PY`
   defaults to `$DATA_DIR/venv-paper2/bin/python`):

   ```
   export DATA_DIR=/path/outside/this/repo PY=/path/to/python3
   bash experiments/20261107-stall-shape-multiverse/run.sh
   ```

   `run.sh` runs the self-tests, the mutation checks and the primary computation. The added computations (Supplement
   S1, orders 2–11) are run by the scripts named in each condition, with the same seed (`SEED`). The scripts stop if a
   check fails (for example, if the detector does not reproduce the stored onsets).
3. `python3 -I tools/verify.py` checks the archive itself.

Every computation ran under a condition committed to the author's version control before it ran. These are not
third-party registrations; their order is shown by the repository, not by an independent time stamp
(`source-commit.txt` gives the commit the archive was assembled from).

## License

Code: MIT or Apache-2.0 (`LICENSE-MIT`, `LICENSE-APACHE`). Text, results and figures: CC BY 4.0 (`LICENSE-docs`).

## Citation

See `CITATION.cff`.
