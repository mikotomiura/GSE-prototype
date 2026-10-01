# Data

The raw run directories are never committed to git. Each one is deposited in a data repository and is
recorded here with the SHA-256 of its deposited archive.

## Run directories used by `run.sh`

`run.sh` reads the lines of the form `- run_dir: PATH  manifest_sha256: HEX` below (a relative path is relative
to this file; `HEX` is the SHA-256 of that run directory's `run.json`, 64 lowercase hexadecimal digits). The
analysis stops when the hash is missing or differs. Lines inside HTML comments and code fences are not read.
Add one line per run directory after the data has been retrieved from the deposit and unpacked. Runs whose
manifest says `aborted` are left out by the pipeline and are counted in the results. The labels that were
used are printed when the analysis ends.

<!-- - run_dir: /path/to/an/unpacked/run-directory  manifest_sha256: 0000000000000000000000000000000000000000000000000000000000000000 -->

## Deposits

| Cell label | Deposit location | SHA-256 of the archive | Date deposited |
|---|---|---|---|
| (to be filled in) | (to be filled in) | (to be filled in) | (to be filled in) |

## Deposit procedure

1. Deposit only `run.json` and the four logs of a run directory: `plan.jsonl`, `oracle.jsonl`,
   `gt.jsonl` and `obs.jsonl`. A log that an aborted run recorded with a null hash need not exist.
2. Do not deposit the `*.stderr.txt` files or `runner.error.txt`. They stay on the measuring machine.
3. On the measuring machine, bundle the files with
   `python3 kit/analysis/pipeline.py --pack <run-dir> --out <archive.zip> [--also-user NAME ...] [--also-home PATH ...]`.
   Pass the login name and the home directory of the measuring machine with `--also-user` and `--also-home`
   (each may be given more than once). The command refuses, with exit status 1 and without writing the
   archive, a run in which any of the five files contains an absolute path (a drive letter, a UNC path,
   `/Users/`, `/home/`, `/Volumes/`, an MSYS drive path such as `/c/`), the home directory, the repository
   path, a login name, or content in the ground-truth or observation log; it exits with status 2 when a log
   no longer matches the hash recorded in `run.json`. Only paths that begin with `~` or `<repo>`, and
   relative paths, are allowed. It never overwrites an existing archive, writes the files in a fixed order
   with fixed times so that packing twice gives the same bytes, checks the contents of the archive again,
   and prints the archive's SHA-256.
4. Before packing, check that no row of either log is without a press the executor sent: in the delivery report
   of the run (`results/e1_delivery.json`, or `python3 kit/analysis/delivery.py` on the run directory),
   `excess_rows` over all presses must be 0 for the observation and for the reference, and `rows_outside_trials`
   must not exceed the presses made outside the trials that each log records: four marker presses per block for
   the observation, which does not record the kana key, and four marker presses and one kana press per block for
   the reference. A run that does not meet this is not deposited until the extra rows are explained, and the
   finding is reported; a run whose extra rows cannot be explained counts as an aborted attempt and is not
   analysed (section 3.4 of the pre-registration).
5. Record the printed SHA-256 in the table above, together with the hash of `run.json`
   (`manifest_sha256` in the line of the list above).
6. Deposit that archive, unchanged. `python3 kit/analysis/pipeline.py --check-deposit <run-dir> ...` runs the
   same check on unpacked directories without writing an archive.

## Machine that ran the deposit check

Record, for every archive, the machine on which `--pack` was run and the values that were passed. The check
finds only the values it is given (see the docstring of `pipeline.py` for what it cannot find).

| Cell label | Machine (operating system, host role) | `--also-user` values | `--also-home` values | Date checked |
|---|---|---|---|---|
| (to be filled in) | (to be filled in) | (to be filled in) | (to be filled in) | (to be filled in) |

## Phrase corpus

`kit/corpus/data/phrases.jsonl` is the phrase corpus read by the scenario generator. It was built once with
`kit/corpus/build_corpus.py`; later runs read only this file and no longer depend on the dictionary.

| Item | Value |
|---|---|
| `--seed` | 1 |
| `--per-work` | 150 |
| `--min-reading` | 6 (default) |
| `--max-reading` | 30 (default) |
| SHA-256 of `phrases.jsonl` | `c8f890cb4d0848bf04e6d7d95efe4e4d3dfd02a23eb1c7f103344f14d13e4620` |
| Tokenizer and dictionary | `SudachiPy==0.7.0`, `sudachidict-core==20260723.1` (pinned in `kit/corpus/requirements.txt`) |
| Phrases | 1,800 (150 from each of 12 works; reading length 6 to 30, median 16) |
| Date built | 2026-09-30 |

Building twice from the same inputs gave byte-identical output.

### Source works

All works are in the public domain and were obtained from Aozora Bunko (https://www.aozora.gr.jp/) as the
ruby-annotated text files in modern orthography (new character forms and modern kana usage). Each archive
holds one `.txt` file, which was renamed to `<work_id>.txt` before the build. The SHA-256 is that of the
downloaded archive.

| `work_id` | Author | Title | Aozora work ID | Text file | SHA-256 of the archive |
|---|---|---|---|---|---|
| `akutagawa_kappa` | Akutagawa Ryunosuke | Kappa | 000069 | `cards/000879/files/69_ruby_1321.zip` | `8daf7b994cebd17dff5a5447fd18d0408a153855ea821b9bec138ee3e68a49e9` |
| `dazai_ningen_shikkaku` | Dazai Osamu | Ningen Shikkaku | 000301 | `cards/000035/files/301_ruby_5915.zip` | `fb37d694f86687f9e84e26643804fa84b4346895f5f56a90dd8843a12e2bc9c8` |
| `dazai_shayo` | Dazai Osamu | Shayo | 001565 | `cards/000035/files/1565_ruby_8220.zip` | `712a759c175c7341bb2916f747f95d0d900923b353d511001ad677b7411eabc8` |
| `hayashi_horoki` | Hayashi Fumiko | Horoki (first edition) | 045649 | `cards/000291/files/45649_ruby_26492.zip` | `179eaee1bd51bfc1987daf16f293d6819083759ba5db0ffc95307f060b988947` |
| `miyazawa_ginga_tetsudo` | Miyazawa Kenji | Ginga Tetsudo no Yoru | 000456 | `cards/000081/files/456_ruby_145.zip` | `8bc90c0c7f97e069d02c4783ce905fa7b959cf60a74df816aeccf94079555076` |
| `nakaya_yuki` | Nakaya Ukichiro | Yuki | 052468 | `cards/001569/files/52468_ruby_49668.zip` | `2d7b144a0f219e8b8e0e861745deba270a37246108fab6271854d4e7653db848` |
| `oda_meoto_zenzai` | Oda Sakunosuke | Meoto Zenzai | 000545 | `cards/000040/files/545_ruby_33101.zip` | `4a88e427c77bcebe21b04bc49aa6cf57e381f618caf7c945a4cc98b42347b89d` |
| `okamoto_hanshichi_01` | Okamoto Kido | Hanshichi Torimonocho 01: Ofumi no Tamashii | 001293 | `cards/000082/files/1293_ruby_5382.zip` | `f409f1374648dbb29d91d50960f95d35e6f94eee14c3a01aa3044f2190f3452e` |
| `sakaguchi_darakuron` | Sakaguchi Ango | Darakuron | 042620 | `cards/001095/files/42620_ruby_21051.zip` | `82db555d429391899b8110b2416739825689596b5196ff5fa3fe87f05abcec40` |
| `soseki_botchan` | Natsume Soseki | Botchan | 000752 | `cards/000148/files/752_ruby_2438.zip` | `53c4d86033d0e4590c0354df5fec2709820ef21c09fa402826ff33376ec21228` |
| `soseki_kokoro` | Natsume Soseki | Kokoro | 000773 | `cards/000148/files/773_ruby_5968.zip` | `c55d7bf6c7cc5bd960ce291949f38cae9ba6a672a6142c3b9e1a9f5a159fa4c4` |
| `terada_kaki_no_tane` | Terada Torahiko | Kaki no Tane | 001684 | `cards/000042/files/1684_ruby_11273.zip` | `ce6792f93e0b98a747b9dd452e4bdb8519b3439975bf68f06c9c605dae747c54` |

The works mix novels, essays and a critical essay so that the corpus is not drawn from a single style.
Text file paths are relative to `https://www.aozora.gr.jp/`.

### Readings

A spot check of 40 randomly drawn phrases found the readings to be valid hiragana key sequences; a few
differ from the reading the author intended (for example, a less common kanji compound read by its
components). This does not affect the accuracy evaluation, which only needs a valid key sequence, and the
reconstruction evaluation uses the typed reading as its ground truth. Nine readings occur twice under
different `phrase_id` values.
