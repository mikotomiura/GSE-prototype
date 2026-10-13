"""Check 6: the inference time and the GPU memory of the KeyTAR model (A4) on one writer drawn with the seed.
The reconstructions are neither written nor printed and no matching value is computed. Run in the KeyTAR venv
(env.md), not the venv of the main computation.

    ~/.venvs/pkm-keytar/Scripts/python -I scripts/check6_keytar.py --root raw/klicke/extracted/WritingTask \
        --model raw/keytar/extracted/data_artifact/data/key_ground_truth_olmo --out results/check6_keytar.json

- Writer: the writers after exclusion sorted by (prompt, ID); index drawn by seeds.rng(SEED, "eval_sample", draw =
  "check6") (an existing seed use; the preregistration does not name one for this check).
- Input (as fixed for A4, R0 of that writer): the intervals between consecutive letter, digit and space presses
  (shortcuts excluded), in chunks covering 20 record segments; integer ms, capped at 1023 as in the released
  training data; one user turn without earlier turns: "Translate the Time intervals to Keystrokes.\nTime intervals: "
  followed by the intervals separated by spaces (the released training data). These input details are for this
  timing check and are settled when A4 is written.
- Generation: the defaults of the artifact's scripts/eval/evaluate_key.py (GEN below), float32 as loaded there.
"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import corpus  # noqa: E402
import load_klicke  # noqa: E402
import seeds  # noqa: E402
from synthetic_logs import category, segment_rows, shortcut_flags  # noqa: E402

GEN = dict(max_new_tokens=50, output_scores=True, return_dict_in_generate=True, no_repeat_ngram_size=2, top_k=50,
           num_beam_groups=16, num_beams=64, diversity_penalty=0.8, num_return_sequences=50, do_sample=False,
           temperature=1.0, top_p=1.0, repetition_penalty=1.0)
PROMPT = "Translate the Time intervals to Keystrokes.\nTime intervals: "
CAP = 1023
CHUNK_SEGMENTS = 20


def chunks(rows):
    cats = [category(r["down_event"]) for r in rows]
    sc = shortcut_flags(cats)
    seg_of_row = {}
    for si, (a, b) in enumerate(segment_rows(cats)):
        for r in range(a, b + 1):
            seg_of_row[r] = si
    out = {}
    for i, c in enumerate(cats):
        if sc[i] or c not in ("letter", "digit", "space") or i not in seg_of_row:
            continue
        out.setdefault(seg_of_row[i] // CHUNK_SEGMENTS, []).append(rows[i]["down_time"])
    res = []
    for k in sorted(out):
        t = out[k]
        res.append([min(CAP, max(0, int(round(b - a)))) for a, b in zip(t, t[1:])])
    return [c for c in res if c]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    import numpy as np
    import torch
    import transformers
    from transformers import AutoModelForCausalLM, AutoTokenizer

    writers, _ = load_klicke.load(args.root)
    kept = []
    for w in writers:  # the rows are dropped after the exclusion check (memory) and read again for the drawn one
        load_klicke.fill_rows(w)
        w.rows = corpus.active_rows(w.rows)
        w.text = (w.text or "").replace("\r\n", "\n")
        if not corpus.exclusion_reason(w):
            kept.append(w)
        w.rows = []
    kept.sort(key=lambda w: (w.prompt, w.writer))
    seed = seeds.read_seed()
    idx = int(seeds.rng(seed, "eval_sample", "", "", "", "", "check6").integers(len(kept)))
    w = load_klicke.fill_rows(kept[idx])
    ch = chunks(corpus.active_rows(w.rows))
    del writers, kept, w

    t0 = time.time()
    tok = AutoTokenizer.from_pretrained(args.model)
    model = AutoModelForCausalLM.from_pretrained(args.model, device_map="auto").eval()
    load_s = time.time() - t0
    torch.cuda.reset_peak_memory_stats()
    times, in_tokens = [], []
    for c in ch:
        msgs = [{"role": "user", "content": PROMPT + " ".join(map(str, c))}]
        x = tok.apply_chat_template(msgs, tokenize=True, add_generation_prompt=True, return_tensors="pt").to("cuda:0")
        in_tokens.append(int(x.shape[1]))
        torch.cuda.synchronize()
        t = time.time()
        with torch.no_grad():
            out = model.generate(x, **GEN)
        torch.cuda.synchronize()
        times.append(time.time() - t)
        del out  # the reconstructions are not read
        torch.cuda.empty_cache()
    res = {"torch": torch.__version__, "cuda": torch.version.cuda, "transformers": transformers.__version__,
           "gpu": torch.cuda.get_device_name(0), "dtype": str(next(model.parameters()).dtype),
           "model_load_seconds": round(load_s, 1), "chunks": len(ch),
           "intervals_per_chunk": [len(c) for c in ch], "input_tokens_per_chunk": in_tokens,
           "seconds_per_chunk": [round(s, 2) for s in times], "seconds_total": round(sum(times), 1),
           "seconds_per_chunk_median": round(float(np.median(times)), 2) if times else None,
           "peak_memory_allocated_gib": round(torch.cuda.max_memory_allocated() / 2 ** 30, 2),
           "peak_memory_reserved_gib": round(torch.cuda.max_memory_reserved() / 2 ** 30, 2),
           "generation": {k: v for k, v in GEN.items() if k not in ("output_scores", "return_dict_in_generate")},
           "input": {"prompt": PROMPT, "cap_ms": CAP, "chunk_segments": CHUNK_SEGMENTS, "earlier_turns": 0}}
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(json.dumps({k: v for k, v in res.items() if k not in ("intervals_per_chunk", "input_tokens_per_chunk",
                                                                 "seconds_per_chunk")}))


if __name__ == "__main__":
    main()
