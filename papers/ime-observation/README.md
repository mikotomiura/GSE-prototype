# Logging Japanese IME conversion without recording text: Observability limits, a cross-platform logger, and a synthetic-input validation

This repository holds the artifacts of a single paper on observing Japanese IME conversion without
recording its text: the limits of observability, a cross-platform standalone logger, and a
synthetic-input validation. Raw logs are not committed to the repository; they are deposited
separately, and their locations and SHA-256 digests are recorded in `experiment/data.md` (macOS) and
`experiment/data.windows.md` (Windows). Commands in the documents of this repository are run from its root.

## Identifiers

- Code, materials and analysis scripts (this repository, release `v1.0.0`): DOI
  [10.5281/zenodo.23183441](https://doi.org/10.5281/zenodo.23183441). `CITATION.cff` gives the citation.
- Records of the validation (the dataset, with its datasheet): DOI
  [10.5281/zenodo.23183438](https://doi.org/10.5281/zenodo.23183438).
- Pre-registration on OSF Registries: macOS cells, https://osf.io/9nh7r (DOI 10.17605/OSF.IO/9NH7R); Windows
  addendum, https://osf.io/4jwzn (DOI 10.17605/OSF.IO/4JWZN).

## History of this repository

The repository does not carry the history of the working repository in which the study was developed. Its history
is, in order:

1. the files exported from the freezing commit of the macOS cells, tagged `ime-observation-prereg-macos`;
2. the files exported from the freezing commit of the Windows addendum, tagged `ime-observation-prereg-windows`;
3. a commit that adds only `manuscript/outline.md` as it stood before the results were analysed;
4. the release, tagged `v1.0.0`.

The first three commits carry the date of the working commit they come from, and their messages name it. The
licence texts, this file's identifiers and the line-end rules of `.gitattributes` are added in the release.

### Recomputing the lists of the freezing tags

Section 9 of the pre-registration defines the list of the files exported from a freezing commit: one line per file,
with the relative path, a space and the SHA-256 of the file, sorted by the bytes of the path, each line ended by LF.
The registrations give the SHA-256 of these lists: `29b183ba245939ad82d9fa2d7db26e1a18520e2966f4aa9ec74478a4e51e6c49`
(98 files, `ime-observation-prereg-macos`) and `f61af353301e1370ac27c4a7425e8c2eb32991df9f7a2a765a26948da87787b7`
(108 files, `ime-observation-prereg-windows`). The two tagged commits hold no `.gitattributes`, so take their files
without line-end conversion:

```bash
mkdir /tmp/freeze && git -c core.autocrlf=false archive ime-observation-prereg-macos | tar -x -C /tmp/freeze
python3 - /tmp/freeze <<'EOF'
import hashlib, os, sys
root = sys.argv[1]
rows = sorted((os.path.relpath(os.path.join(d, n), root).replace(os.sep, "/").encode("utf-8"),
               hashlib.sha256(open(os.path.join(d, n), "rb").read()).hexdigest())
              for d, _, names in os.walk(root) for n in names)
text = b"".join(p + b" " + h.encode("ascii") + b"\n" for p, h in rows)
print(hashlib.sha256(text).hexdigest(), len(rows))
EOF
```

With `core.autocrlf=true` (the default of Git for Windows) the archive is written with CRLF line ends and the list
does not match.

## Layout

| Directory | Role |
|---|---|
| `kit/` | The reproducible toolset (log formats, generator, emitter, reference input field, standalone logger, analysis). |
| `experiment/` | Experiment records (SEED / env.md / data.md / data.windows.md / run.sh / notes.md). Raw logs are not stored here (`experiment/raw/` is ignored); the deposit location and its SHA-256 are recorded in `data.md` (macOS) and `data.windows.md` (Windows). |
| `manuscript/` | The manuscript. |

## License

Split by kind, not by directory.

- Code (source in `.py` / `.sh` / `.swift` / `.rs`, etc.): Apache-2.0
- Data (including the phrases and readings in `kit/corpus/data/`) and documents (`*.md`, the
  records under `experiment/`, `manuscript/`): CC BY 4.0

The full texts are `LICENSE-CODE` (Apache License 2.0) and `LICENSE-DATA` (Creative Commons Attribution 4.0
International).

## Components

The kit is made of the following components; the logger's own README (`kit/logger/README.md`) is the entry point for
using the logger.

| Directory | Contents |
|---|---|
| `kit/formats/` | Log-format contracts and their validators |
| `kit/corpus/` | Aozora Bunko phrases and their readings |
| `kit/gen/` | Scenario generator |
| `kit/emit/` | Emitter (synthetic key dispatch and the oracle) |
| `kit/run/` | Single-cell orchestration |
| `kit/refinput-macos/` / `kit/refinput-windows/` | Reference input field |
| `kit/logger/` | Standalone logger |
| `kit/pilot/` | Calibration pilot tooling |
| `kit/analysis/` | Ground-truth assembly, matching, L1, L2, pipeline |
| `kit/e2/` / `kit/e3/` | Leakage evaluation / execution cost |

## Verification

```bash
bash kit/check.sh              # run every selftest under kit/ (a no-op counts as red)
bash kit/check.sh --compile    # py_compile every .py under kit/
bash kit/check.sh --self-test  # this entry point's own negative controls
```

- Only the `.py` files under `kit/` that carry the `# kit: selftest` marker comment are run with
  `--selftest` (unmarked helper modules are only compiled).
- The entry point runs on every verify and on every acceptance check, so **selftests are written to
  be fast by default** (under 30 seconds each; exceeding that triggers a warning). Heavy checks are
  split into something like `--selftest --full` and are not run by default.
- The log-format contract is [`kit/formats/FORMATS.md`](kit/formats/FORMATS.md). The **shape** of
  `gt` and `obs` rows (string values fit an enumeration or regular expression, and there are no
  unknown keys or escapes) is verified mechanically by `kit/formats/validate_logs.py`. The meaning
  of integer values, version strings, and `manifest_sha256` is out of scope; keeping the log
  content-free is the producing side's responsibility (writing only kind, length, and time), as
  described in FORMATS.md's "Scope of guarantee".
- The marker is written as a comment where **the entire line reads `# kit: selftest`** (a marker
  inside a string literal is not picked up).
