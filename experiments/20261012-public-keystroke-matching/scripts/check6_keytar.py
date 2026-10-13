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
  followed by the intervals separated by spaces, as in the "messages" of the released training dataset
  key_ground_truth (the raw jsonl in raw_data.zip separates them by commas; the model was trained on spaces). These input details are for this
  timing check and are settled when A4 is written.
- Generation: the defaults of the artifact's scripts/eval/evaluate_key.py (GEN below), float32 as loaded there.
  max_new_tokens = 50 is shorter than a 20-segment chunk needs (the artifact's sentences have 37 to 58
  characters), so the measured time underestimates the time of a full reconstruction of a chunk.
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
# the checkpoint files read by from_pretrained (data.md): verified before loading, offline (security review)
CHECKPOINT_SHA256 = {
    "pytorch_model.bin": "d09f06db0f3dbaebf28a6a80e4d4651629dbf8ca3d20bc6d5656ee5d13f7144f",
    "config.json": "e23765bc5707b77d56cec9f61ec89c5bf1bbcd73a97d820216834a346d5c4ee9",
    "generation_config.json": "b5869df64082766f4c2e8165436f2b9ca4f8313f4cdeacfdf9216ec5dc2330b5",
    "special_tokens_map.json": "a6188c1e366f8ed715e60ff39c46a8c500fc33508e2affeb23e8c547c5853193",
    "tokenizer.json": "ff3f2a2fc3b88f6f8504650e2ebb8e018bc4206a90eb41f1a9ff351e02e44ff9",
    "tokenizer_config.json": "24bd0934b2eb00d90a2f40b8f1c66284c3d96070d26cb9d12a6b21c8522007df"}
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"


def verify_checkpoint(model_dir):
    import hashlib
    if not os.path.isdir(model_dir):
        raise SystemExit("--model must be a local directory")
    for name, want in CHECKPOINT_SHA256.items():
        h = hashlib.sha256()
        with open(os.path.join(model_dir, name), "rb") as f:
            for b in iter(lambda: f.read(1 << 24), b""):
                h.update(b)
        if h.hexdigest() != want:
            print("SHA-256 of %s differs from data.md" % name, flush=True)
            sys.exit(3)  # a4_keytar.PERMANENT
    # another weight file in the folder would be loaded instead of the verified .bin (safetensors first): refuse
    extra = [f for f in os.listdir(model_dir) if f not in CHECKPOINT_SHA256 and f != "convert.sh"]
    if extra:
        raise SystemExit("unverified files in the checkpoint folder: %d" % len(extra))
    with open(os.path.join(model_dir, "config.json"), encoding="utf-8") as f:
        if "auto_map" in json.load(f):
            raise SystemExit("config.json asks for remote code")


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

    verify_checkpoint(args.model)
    t0 = time.time()
    tok = AutoTokenizer.from_pretrained(args.model, local_files_only=True, trust_remote_code=False)
    model = AutoModelForCausalLM.from_pretrained(args.model, device_map="auto", local_files_only=True,
                                                 trust_remote_code=False, use_safetensors=False).eval()
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
