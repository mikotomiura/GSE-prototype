# What moves with the pause definition and the adjustment: a multiverse diagnostic of pause and stall labels in keystroke logs

This directory holds the manuscript of a study that applies one stall detector to four public keystroke datasets (two
editions of an introductory programming course, an essay corpus and a corpus of writing with model suggestions),
varies its window, threshold, stop condition and segmentation over 89 definitions around a baseline, adds a
fixed-threshold pause detector, and reports which conclusions drawn from the labels move across definitions and
adjustments and which stay.

- `manuscript/`: the LaTeX sources for the Journal of Educational Data Mining (`BUILD.md` says how to build them). The
  files under `manuscript/figdata/` and `manuscript/appendix/tab_*.tex` hold aggregate values by definition and are
  generated from the aggregate result files; they contain no per-writer values.

The public data are not redistributed here. The code, the conditions and the aggregate results are archived at
https://doi.org/10.5281/zenodo.24047695 (https://github.com/mikotomiura/stall-shape-multiverse).
