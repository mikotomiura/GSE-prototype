"""A4 (preregistration, "Attackers"): reconstructions of the KeyTAR model for the 500 writers of the main tables.
Run in the KeyTAR venv (env.md), not the venv of the main computation. Writes the reconstructions to local files
under raw/ (never versioned, never printed, never read by a person or sent anywhere) and a summary of counts and
times only. The matching (normalised edit distance to the candidates) is done by the main computation
(evaluate.py), on the same draws as the other attackers.

    ~/.venvs/pkm-keytar/Scripts/python -I scripts/a4_keytar.py --root raw/klicke/extracted/WritingTask \
        --model raw/keytar/extracted/data_artifact/data/key_ground_truth_olmo --out-dir raw/derived/a4 \
        --summary results/a4_generation.json

Fixed before any matching value (notes.md, "Implementation choices: A4"):
- writers: the 500 writers of eval_sample, after exclusion (the computation of run_main.py); in (prompt, ID) order;
  a writer whose file is complete is skipped (the run can be resumed);
- input variants: the press times of R0, R1, R2 and R3 are the same (key 't0'); R3-t(w) floors them (keys 't10',
  't100', 't1000', as form_R3t);
- a chunk without an interval is dropped (check6_keytar.chunks), so it adds nothing to the joined reconstruction;
- full text: the letter, digit and space presses (shortcuts excluded) of the active rows, in chunks covering 20 record
  segments (check6_keytar.chunks); windows: the same on the rows of each window of the main computation (the valid
  true windows of matching.true_window_starts and the starts of matching.pick_window_starts, keyed 'k:start index');
- generation: the artifact's defaults (check6_keytar.GEN, max_new_tokens 50: decision 56), one user turn without
  earlier turns; the generated tokens of the first returned sequence are decoded (the artifact's evaluate_key.py
  decodes the whole sequence and keeps what follows the last "assistant", which also cuts a reconstruction that
  contains that word; codex review) and stripped of "\n|>" as there; the chunk
  reconstructions are joined with one space; identical inputs of one writer are generated once;
- each file carries the fingerprint of the generation (checkpoint, code hashes, settings); a resumed run refuses a
  file with another fingerprint and generates an unreadable or incomplete file again; writes are flushed to disk
  before the rename; the summary adds the counts and times of earlier attempts (reviews of 2026-10-13).
"""
import argparse
import json
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import check6_keytar as K  # noqa: E402  (sets HF_HUB_OFFLINE and TRANSFORMERS_OFFLINE)
import corpus  # noqa: E402
import load_klicke  # noqa: E402
import matching  # noqa: E402
import seeds  # noqa: E402

VARIANTS = {"t0": None, "t10": 10, "t100": 100, "t1000": 1000}
KS = (5, 10, 20, 50)
MUTATE = os.environ.get("A4_MUTATE", "")


def variant_rows(rows, w):
    if w is None:
        return rows
    return [dict(r, down_time=(r["down_time"] // w) * w) for r in rows]


def writer_inputs(rows, text, seed, prompt, writer):
    """{variant: {'full': [chunk intervals], 'windows': {'k:si': [chunk intervals]}}} for one writer."""
    final, origins = corpus.replay_origins(rows)
    words_final = re.findall(r"[A-Za-z0-9]+", final)
    words_dist = re.findall(r"[A-Za-z0-9]+", text)
    wins = {}
    for k in KS:
        valid, _ = matching.true_window_starts(rows, final, origins, words_final, words_dist, k)
        if not valid:
            continue
        for si in matching.pick_window_starts(seed, prompt, writer, k, valid):
            wins["%d:%d" % (k, si)] = valid[si][0]
    out = {}
    for name, w in VARIANTS.items():
        vr = variant_rows(rows, w)
        out[name] = {"full": K.chunks(vr), "windows": {key: K.chunks(vr[a:b + 1]) for key, (a, b) in wins.items()}}
    return out


def sample_writers(root, seed, per_prompt=125):
    """The writers of eval_sample after exclusion, as run_main.py: active rows, text with \\r\\n -> \\n, exclusion."""
    writers, _ = load_klicke.load(root)
    by_prompt = {}
    for w in writers:
        load_klicke.fill_rows(w)
        w.rows = corpus.active_rows(w.rows)
        w.text = (w.text or "").replace("\r\n", "\n")
        if not corpus.exclusion_reason(w):
            by_prompt.setdefault(w.prompt, {})[w.writer] = w
        w.rows = []
    sample = matching.eval_sample(seed, {p: list(v) for p, v in by_prompt.items()}, per_prompt)
    return [by_prompt[p][wid] for p in sorted(sample) for wid in sample[p]]


class Generator:
    def __init__(self, model_dir):
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
        K.verify_checkpoint(model_dir)
        self.torch = torch
        self.tok = AutoTokenizer.from_pretrained(model_dir, local_files_only=True, trust_remote_code=False)
        self.model = AutoModelForCausalLM.from_pretrained(model_dir, device_map="auto", local_files_only=True,
                                                          trust_remote_code=False, use_safetensors=False).eval()

    def __call__(self, intervals):
        if MUTATE == "dry":
            return " ".join("x" * min(5, 1 + v % 5) for v in intervals[:8])
        msgs = [{"role": "user", "content": K.PROMPT + " ".join(map(str, intervals))}]
        x = self.tok.apply_chat_template(msgs, tokenize=True, add_generation_prompt=True,
                                         return_tensors="pt").to("cuda:0")
        with self.torch.no_grad():
            out = self.model.generate(x, **K.GEN)
        text = self.tok.decode(out.sequences[0][x.shape[1]:], skip_special_tokens=True)
        del out
        self.torch.cuda.empty_cache()
        return text.strip("\n|>")


def reconstruct(chunks, gen, cache, stats):
    parts = []
    for c in chunks:
        if not c:
            parts.append("")
            continue
        key = tuple(c)
        if key not in cache:
            t = time.time()
            cache[key] = gen(c)
            stats["generated"] += 1
            stats["seconds"] += time.time() - t
        else:
            stats["reused"] += 1
        parts.append(cache[key])
    return " ".join(parts)


def _sha_file(path):
    import hashlib
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


# the code that decides the inputs and the generation; the SEED decides the sample and the windows
FINGERPRINT_FILES = ("a4_keytar.py", "check6_keytar.py", "corpus.py", "matching.py", "seeds.py", "synthetic_logs.py",
                     "load_klicke.py", "align_ext.py", "align.py")


def fingerprint():
    """What a file was generated with: the checkpoint, the hashes of the code and the SEED, the settings and the input
    rules. A file with another fingerprint is not reused (generation) and not matched (evaluate.load_a4)."""
    return {"checkpoint": K.CHECKPOINT_SHA256["pytorch_model.bin"],
            "code_sha256": {n: _sha_file(os.path.join(HERE, n)) for n in FINGERPRINT_FILES},
            "seed_sha256": _sha_file(os.path.join(HERE, "..", "SEED")), "dry": MUTATE == "dry",
            "generation": {k: v for k, v in K.GEN.items() if k not in ("output_scores", "return_dict_in_generate")},
            "variants": sorted(VARIANTS), "ks": list(KS), "cap_ms": K.CAP, "chunk_segments": K.CHUNK_SEGMENTS}


def source_hashes(w):
    """SHA-256 of the writer's log file and of the text (after \\r\\n -> \\n); the log is None without a file."""
    import hashlib
    p = w.extra.get("log_path")
    return {"log_sha256": _sha_file(p) if p else None,
            "text_sha256": hashlib.sha256((w.text or "").encode("utf-8")).hexdigest()}


def check_record(d, fp, prompt, writer, src=None):
    """The reason a stored record is not usable, or None. Shared by the generation (resume) and evaluate.load_a4:
    owner, fingerprint, source hashes (when given), and the structure (every variant with a string 'full' and a
    dict of strings 'windows' with the same keys in every variant)."""
    if not isinstance(d, dict):
        return "not an object"
    if d.get("prompt") != prompt or d.get("writer") != writer:
        return "another writer"
    if d.get("fingerprint") != fp:
        return "fingerprint"
    if src is not None and d.get("source") != src:
        return "source"
    v = d.get("variants")
    if not isinstance(v, dict) or sorted(v) != sorted(VARIANTS):
        return "variants"
    keys = None
    for x in v.values():
        if not isinstance(x, dict) or not isinstance(x.get("full"), str) or not isinstance(x.get("windows"), dict):
            return "structure"
        if not all(isinstance(t, str) for t in x["windows"].values()):
            return "structure"
        if keys is not None and sorted(x["windows"]) != keys:
            return "window keys"
        keys = sorted(x["windows"])
    if not isinstance(d.get("stats"), dict):
        return "stats"
    return None


PERMANENT = 3  # exit code of a stop that a restart cannot cure (a4_run_resumable.sh stops on it)


def complete(path, fp, w, src):
    """True when the stored record is usable. An unreadable or malformed file (a write cut by a power loss) is removed
    and generated again; a file of another generation or source stops the run (exit PERMANENT)."""
    if not os.path.exists(path):
        return False
    try:
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
    except (ValueError, OSError):
        os.remove(path)
        return False
    why = check_record(d, fp, w.prompt, w.writer, src)
    if why in ("fingerprint", "source", "another writer"):
        print("a file of another generation or input is in --out-dir (%s); move it away" % why, flush=True)
        sys.exit(PERMANENT)
    if why:
        os.remove(path)
        return False
    return True


def out_path(out_dir, prompt, writer):
    if not re.fullmatch(r"[A-Za-z0-9_-]+", writer) or not re.fullmatch(r"[A-Za-z0-9]+", prompt):
        print("unexpected ID or prompt format (the ID is not printed)", flush=True)
        sys.exit(PERMANENT)
    return os.path.join(out_dir, "%s__%s.json" % (prompt, writer))


def under(path, root):
    a, b = os.path.realpath(path), os.path.realpath(root)
    try:
        return os.path.commonpath([a, b]) == b
    except ValueError:  # another drive
        return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--summary", required=True)
    ap.add_argument("--limit", type=int, default=0, help="stop after this many writers (0: all)")
    args = ap.parse_args()
    seed = seeds.read_seed()
    if MUTATE and under(args.out_dir, os.path.join(HERE, "..", "raw")):
        print("A4_MUTATE is set: refusing to write under raw/", flush=True)
        sys.exit(PERMANENT)
    os.makedirs(args.out_dir, exist_ok=True)
    for name in os.listdir(args.out_dir):
        if name.endswith(".tmp"):
            os.remove(os.path.join(args.out_dir, name))
    sample = sample_writers(args.root, seed)
    gen = Generator(args.model) if MUTATE != "dry" else Generator.__new__(Generator)
    t0 = time.time()
    fp = fingerprint()
    done_now = 0
    for n, w in enumerate(sample):
        path = out_path(args.out_dir, w.prompt, w.writer)
        src = source_hashes(w)
        if complete(path, fp, w, src):
            continue
        if args.limit and done_now >= args.limit:
            break
        load_klicke.fill_rows(w)
        rows = corpus.active_rows(w.rows)
        w.rows = []
        inputs = writer_inputs(rows, w.text, seed, w.prompt, w.writer)
        stats = {"generated": 0, "reused": 0, "seconds": 0.0, "chunks_full": 0, "chunks_windows": 0}
        cache, rec = {}, {}
        for v, d in inputs.items():
            stats["chunks_full"] += len(d["full"])
            stats["chunks_windows"] += sum(len(c) for c in d["windows"].values())
            rec[v] = {"full": reconstruct(d["full"], gen, cache, stats),
                      "windows": {key: reconstruct(c, gen, cache, stats) for key, c in d["windows"].items()}}
        stats["seconds"] = round(stats["seconds"], 1)
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump({"prompt": w.prompt, "writer": w.writer, "fingerprint": fp, "source": src, "stats": stats,
                       "variants": rec}, f, ensure_ascii=False)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
        done_now += 1
        print("writer %d/%d done (%.0f s so far)" % (n + 1, len(sample), time.time() - t0), flush=True)
    # the summary sums the stats stored with each writer (so a crash of an attempt loses nothing)
    tot = {"writers_total": len(sample), "writers_with_file": 0, "generated": 0, "reused": 0, "seconds": 0.0,
           "chunks_full": 0, "chunks_windows": 0}
    for w in sample:
        path = out_path(args.out_dir, w.prompt, w.writer)
        if not os.path.exists(path):
            continue
        with open(path, encoding="utf-8") as f:
            st = json.load(f).get("stats") or {}
        tot["writers_with_file"] += 1
        for key in ("generated", "reused", "seconds", "chunks_full", "chunks_windows"):
            tot[key] += st.get(key, 0)
    tot["seconds"] = round(tot["seconds"], 1)
    tot["seconds_per_writer"] = round(tot["seconds"] / tot["writers_with_file"], 1) if tot["writers_with_file"] else None
    tot["fingerprint"] = fp
    tot["input"] = {"prompt": K.PROMPT, "cap_ms": K.CAP, "chunk_segments": K.CHUNK_SEGMENTS, "earlier_turns": 0,
                    "variants": sorted(VARIANTS), "ks": list(KS), "compared": "first returned sequence"}
    with open(args.summary, "w", encoding="utf-8", newline="\n") as f:
        json.dump(tot, f, indent=1, sort_keys=True)
        f.write("\n")


if __name__ == "__main__":
    main()
