# Export to the public repository

This note and `export.internal.py` are internal: they are never exported (their names have the
internal form), so the public repository does not contain the exporter.

`export.internal.py` writes the public form of this directory to a new location. The public repository starts
from that output with a fresh history. The script uses only the Python standard library. It calls
git only to check that a source inside a git work tree is committed (see the procedure below).

```
python3 kit/export/export.internal.py --out DIR [--allow-missing-license] [--style-check PATH]
                                      [--also-user NAME ...] [--also-home PATH ...]
python3 kit/export/export.internal.py --selftest
```

The source is the directory two levels above `kit/export/`. `--out` must name a path that does not
exist, whose parent directory exists (it is not created), and that lies outside the source; an
existing path is never overwritten. The output is written to a sibling directory (same parent, a name that
starts with a dot) and is renamed to `--out` only after the manifest check and the check of the writing
rules have passed; if the export is refused, that directory is removed, so nothing that looks finished is
left behind.

Exit code: 0 = exported; 1 = refused because of the content (a private value was found, a
manifest does not match its files, a string literal has no translation); 2 = usage error, missing
license text, or unreadable or unsafe input (a link that leaves the source, a binary file, a file
with the name of a secret, a source that is not committed, an ignore file that differs from the
exclusion rules, an output path inside the git work tree of the source, a checker of the writing
rules that is missing or fails), or an unexpected failure (only the type of the error is printed).

## Publication procedure

1. Place the official texts as `LICENSE-CODE` (Apache-2.0) and `LICENSE-DATA` (CC BY 4.0) in the
   root of this directory. The script stops with exit code 2 if either is missing.
2. Fill in the author names and affiliations in `CITATION.cff` and `.zenodo.json`. The script warns
   while a `TODO` placeholder remains. Commit the result.
3. Make a fresh clone of the commit to release and run the export from that clone. Inside a git
   work tree the script exports only files that are tracked and equal to the committed version; it
   stops with exit code 2 and lists the offending files when a file it would export is untracked,
   changed or deleted. A fresh clone also guarantees that the same commit yields the same bytes
   on every machine.
4. Run `export.internal.py --out DIR`, and pass the values of both development machines: every
   `--also-user` (login name) and every `--also-home` (home directory) of the other machine, in
   addition to the ones the script reads from the machine that runs it (its host name is read too).
   Also pass the host name of the other development machine with `--also-user` (the host name of the machine
   that runs the export is read by the script, but `localhost` is never searched for).
   Make the public repository on macOS or Linux. A checkout or export written on Windows does not
   carry the executable bit, so the shell scripts (the files that start with `#!`, optional blanks and
   `/`) would lose it; on Windows run `git update-index --chmod=+x <file>` for each of them before the
   first commit.
   The output is byte-identical for the same source on any machine.
   The last step of the export runs the checker of the writing rules of published files
   (`_style_check.py`) on the output: forbidden words, internal numbers, relation words and Japanese
   prose. The checker is found in the git work tree of the source, or given with `--style-check PATH`;
   if it cannot be found or fails, the export stops with exit code 2 and the output is removed; a
   violation stops it with exit code 1 (only the file, line and kind are printed). When the source is
   inside a git work tree, the checker must itself be tracked in the git work tree that holds it, equal to
   HEAD and free of an `assume-unchanged` or `skip-worktree` mark (a checker outside git stops the
   export with exit code 2), so that one commit yields one verdict.
5. Commit `DIR` on top of the history of the public repository (next section) and tag the release. The
   DOI of the release is reserved beforehand in a draft of the archive service and is already in
   `CITATION.cff` and the manuscript; the archive of the tag is uploaded to that draft, which is then published.

## History of the public repository

The public repository does not carry the history of the working repository. Its history is, in order:
the export of the macOS freezing tag (made with that tag's own exporter and `--allow-missing-license`, so that
the list of its files has the SHA-256 that the registration gives), tagged `ime-observation-prereg-macos`; the
export of the Windows freezing tag, made in the same way, tagged `ime-observation-prereg-windows`; a commit that
adds only `manuscript/outline.md` as it stood before the results were analysed; and the release. The author date
of each of the first three commits is the date of the working commit it comes from, and the message names that
commit. Scripts that start with `#!` are given the executable bit in the index.

`--allow-missing-license` is not for publication. It is for trial exports and for building the
measurement logger (next section); the script says so at the top of its output.

## Building the measurement logger

The standalone logger embeds `kit/logger/manifest.json` at build time and writes the SHA-256 of that
file into the header of every log (`manifest_sha256`). The export rewrites the manifests, so a
logger built from the development tree records a value that appears nowhere in the public
repository. Loggers used for the pilot and for the measurements are therefore built from the
exported tree, and the `manifest_sha256` of a log equals the SHA-256 of the published
`kit/logger/manifest.json`. Because the license text does not change the logger bytes, such a build
may come from an export made with `--allow-missing-license`.

For this reason the output of two exports of the same source must be identical on every machine:
line endings are LF, files are written in sorted order, and nothing depends on the time or on the
machine that runs the export.

## What is left out

Everything the ignore file of this directory excludes: build products (`target/`, `.build/`,
`__pycache__/`), raw logs (`*.jsonl`, `*.ndjson`, `runs/`, `sealed/`, `experiment/raw/`), archives
(`*.jsonl.*`, `*.ndjson.*`, `*.zip`, `*.tar`, `*.tar.gz`, `*.tgz`, `*.zst`), virtual environments, and the
outputs of a LaTeX build run by hand (`*.aux`, `*.blg`, `*.bbl`, `*.out`, `*.toc`, `*.synctex.gz`). The ignore
file also lists `*.log`, which is not left out: a log has the name of a secret and stops the export (next
section), so remove it from the source. Names are compared without regard to case, and the script stops (exit
code 2) if the ignore file does not list exactly the rules it implements.
Corpus files `kit/corpus/data/*.jsonl` are kept. In addition, every file with `.internal.` in its
name (internal notes and the translation table) and `.DS_Store` are left out. The aggregate results
under `experiment/results/` are kept because the results section of the paper rests on them.

## What is changed

* Text files are written with LF line endings.
* For every file that a logger manifest pins as a whole, and for every marked excerpt of a file
  (the lines between `// @excerpt-begin ID` and `// @excerpt-end ID`), the Rust comments are
  removed and a one-line English header is added to whole files. String literals that contain
  non-ASCII characters are replaced by the English literals of the translation table
  (`kit/export/translations.internal.json`). The export stops if a literal has no entry or an entry
  matches nothing. A replacement must be ASCII, of the same literal kind, and must keep the format
  placeholders of the original in the same order. The excerpt markers are kept.
* Each manifest keeps only `kind`, `id`, `path`, `symbol`, `sha256` and `reason` per entry and the
  `entries` list at the top level. Every checksum is computed again from the exported bytes.
  `python3 kit/logger/check_manifest.py --self` verifies the result and is run by the export.

## What stops the export

Before the scan, the script stops with exit code 2 (nothing is skipped silently) when the source
holds a file whose name looks like a secret (`.env`, `.env.*`, `*.env`, `*.pem`, `*.key`, `*.ppk`,
`*.asc`, `*age-identity*`, `*.agekey`, `*.age`, `*token*.json`, `*token*.txt`, `*.token`,
`credentials*.json`, `credentials`, `client_secret*`, `*secret*`, `key.txt`, `id_rsa*`,
`id_ed25519*`, `id_ecdsa*`, `id_dsa*`, `.netrc`, `_netrc`, `.npmrc`, `.pypirc`, `.git-credentials`,
`g1-submit*.json`, `o1_submit*.json`, `*.log`; case-insensitive; the directory names `.ssh`, `.gnupg`, `.aws`, `.docker`, `.kube` and `.pgpass`
are matched too, and the whole set applies to directory names as well as file names; rename the file or
directory if the name matched by chance), a file whose content carries the signature of a secret (the head of an age secret key,
the begin line of a PEM or PGP private key, a GitHub / GitLab token head, the shape of an AWS access key
id (long-term or temporary), an Anthropic or OpenAI key head, the shape of a Google API key, a Slack
token head; the check runs on the source and again on the converted output, and each line is also
checked with its escapes decoded; the text is never printed), a file of a kind that the checker of
the writing rules does not read (the file must have the extension `.py`, `.rs`, `.sh`, `.md`,
`.json`, `.toml`, `.swift`, `.txt`, `.cff`, `.tex` or `.bib`, or be named `.gitignore`, `SEED`, `Cargo.lock`,
`LICENSE-CODE` or `LICENSE-DATA`; under `kit/corpus/data/` only the `*.jsonl` files directly in it;
add the kind to the checker or leave the file out), a name that holds the word `internal` in
another form than `.internal.` (a word that no letter touches, in any case, as in `notes_internal.md`,
`internal2.md` or `notes(internal).md`, or `Internal` right after a lower-case letter, as in
`notesInternal.md`; `internals` and `international` pass; rename it), an unreadable directory, or a link that leaves the
source (a symbolic link, or on Windows a junction or any other reparse point).

Inside a git work tree the script also stops when git cannot be run or reports no repository while a
`.git` (a directory or a file) exists in the source or above it (a source under a `.git` is never
exported without the check), when the translation table is not tracked or differs from the
commit (a deleted tracked table too) or is a link, when a file it would export (or the table) carries an `assume-unchanged` or
`skip-worktree` mark in the index, and when a tracked file that is not excluded was not collected.

The scan runs on all exported text after the changes above, and on every relative file name
(reported as line 0). Each line is checked as written and again with its JSON and string escapes
decoded. A finding is reported as a file name, a line number and a kind; the matched text is never
printed. The script also verifies that the copied ranges of the pinned sources contain only ASCII
characters.

* A participant identifier (the letter P and three digits, not adjoining a letter or digit, so
  that the identifier is found inside a longer name joined by an underscore; inside brackets too,
  as in `[P017]`, and in file names), an e-mail address (the one exception is the address of the corresponding
  author, which the article prints; it is fixed in the script as `PUBLIC_EMAILS` and passes only as a whole
  address), the name of the private dataset repository, a session
  name of the private recordings, and the private working directories.
* The words that name the private project, the name of its source directory, and two internal
  marker symbols (not applied to the `.jsonl` files directly in `kit/corpus/data/`; other files there are checked).
* Values of the machine that runs the export: the home directory, the repository root, the
  login name and the host name (three characters or more; the part of the host name before the first
  dot is taken too; `localhost` is never searched for). `--also-home` and `--also-user` add the values of other
  machines (`--also-user` with fewer than three characters is a usage error). These values are
  found wherever they occur, with no boundary on the left. Every spelling of a path is checked: forward and backward slashes, doubled backslashes,
  and the `/c/...` form of a drive path.
* An absolute path that names a user. A path token starts with `/`, a backslash, a drive letter
  such as `C:` or `file:` and runs to the next space, quote, angle bracket, `|`, `*` or `?`
  (prefixes such as `file://`, the extended-length prefix of Windows and `/mnt/c/` are part of
  it). A colon does not join a name, so a path after `host:` and the path of a URL are tokens too. When a component of the token is `Users` or `home` (any case), the whole next component
  (not cut at a punctuation mark, non-ASCII characters included, only a trailing `.,;:)` dropped;
  every run of separator characters before it, of either kind and mixed or not, and every component that is
  a single dot are skipped) is the name. The path that follows a `-I`, `-L` or `-F` compiler flag (after
  the start of the line, a blank, a quote or `=`) is checked as a token too. In the path of an `http` or
  `https` URL only a drive-letter form (`/C:/Users/name`) counts as a user path; the `/users/<id>` or
  `/home/<x>` of a web address does not. A relative path such as `./Users/y` or `kit/home/x` is not a token. The only names
  that pass are these fictional ones, fixed in the script and not
  extendable by an option: `alice`, `alice2`, `bob`, `carol`, `dave`, `erin`, `gina`, `harry`,
  `YAMADA~1` and `name`. A prefix without a name (`/Users/` alone) also passes.

## Continuous integration of the public repository

The public repository runs `bash kit/check.sh` (the selftests of the tools that are exported; this exporter is not one of them)
and `python3 kit/logger/check_manifest.py --self`.

## Known false alarms and forms that are not caught

* The secret-name patterns are broad on purpose, so a harmless name can match: `tokenizer_notes.txt`
  (`*token*.txt`), `secret-sharing.md` (`*secret*`), and the public signature file of a release
  (`*.asc`). The export stops with exit code 2 and asks for a rename; nothing is skipped silently.
* A path with a space in it (`C:\Documents and Settings\<name>`) is cut at the space by the token
  rule, so its user name is not seen. This form is not handled; do not put such a path in a published file.
* A host name that is a common word (other than `localhost`) is searched for like any other value and
  stops the export when it occurs as a word; rename the host or reword the text.
