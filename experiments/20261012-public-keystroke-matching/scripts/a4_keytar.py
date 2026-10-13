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
- full text: the letter, digit and space presses (shortcuts excluded) of the active rows, in chunks covering 20 record
  segments (check6_keytar.chunks); windows: the same on the rows of each window of the main computation (the valid
  true windows of matching.true_window_starts and the starts of matching.pick_window_starts, keyed 'k:start index');
- generation: the artifact's defaults (check6_keytar.GEN, max_new_tokens 50: decision 56), one user turn without
  earlier turns; the first returned sequence is decoded and cut as in the artifact's evaluate_key.py; the chunk
  reconstructions are joined with one space; a chunk without an interval gives an empty string; identical inputs of
  one writer are generated once.
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
        text = self.tok.decode(out.sequences[0], skip_special_tokens=True)
        del out
        self.torch.cuda.empty_cache()
        return text.split("assistant")[-1].strip("\n|>")


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


def out_path(out_dir, prompt, writer):
    if not re.fullmatch(r"[A-Za-z0-9_-]+", writer) or not re.fullmatch(r"[A-Z]+", prompt):
        raise SystemExit("unexpected ID or prompt format (the ID is not printed)")
    return os.path.join(out_dir, "%s__%s.json" % (prompt, writer))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--summary", required=True)
    ap.add_argument("--limit", type=int, default=0, help="stop after this many writers (0: all)")
    args = ap.parse_args()
    seed = seeds.read_seed()
    os.makedirs(args.out_dir, exist_ok=True)
    sample = sample_writers(args.root, seed)
    gen = Generator(args.model) if MUTATE != "dry" else Generator.__new__(Generator)
    stats = {"writers_total": len(sample), "writers_done_before": 0, "writers_done_now": 0, "generated": 0,
             "reused": 0, "seconds": 0.0, "chunks_full": 0, "chunks_windows": 0}
    t0 = time.time()
    for n, w in enumerate(sample):
        path = out_path(args.out_dir, w.prompt, w.writer)
        if os.path.exists(path):
            stats["writers_done_before"] += 1
            continue
        if args.limit and stats["writers_done_now"] >= args.limit:
            break
        load_klicke.fill_rows(w)
        rows = corpus.active_rows(w.rows)
        w.rows = []
        inputs = writer_inputs(rows, w.text, seed, w.prompt, w.writer)
        cache, rec = {}, {}
        for v, d in inputs.items():
            stats["chunks_full"] += len(d["full"])
            stats["chunks_windows"] += sum(len(c) for c in d["windows"].values())
            rec[v] = {"full": reconstruct(d["full"], gen, cache, stats),
                      "windows": {key: reconstruct(c, gen, cache, stats) for key, c in d["windows"].items()}}
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump({"prompt": w.prompt, "writer": w.writer, "variants": rec}, f, ensure_ascii=False)
        os.replace(tmp, path)
        stats["writers_done_now"] += 1
        print("writer %d/%d done (%.0f s so far)" % (n + 1, len(sample), time.time() - t0), flush=True)
    stats["seconds"] = round(stats["seconds"], 1)
    stats["wall_seconds"] = round(time.time() - t0, 1)
    stats["generation"] = {k: v for k, v in K.GEN.items() if k not in ("output_scores", "return_dict_in_generate")}
    stats["input"] = {"prompt": K.PROMPT, "cap_ms": K.CAP, "chunk_segments": K.CHUNK_SEGMENTS, "earlier_turns": 0,
                      "variants": sorted(VARIANTS), "ks": list(KS), "compared": "first returned sequence"}
    with open(args.summary, "w", encoding="utf-8", newline="\n") as f:
        json.dump(stats, f, indent=1, sort_keys=True)
        f.write("\n")


if __name__ == "__main__":
    main()
