"""A4 with a CPU fallback for the chunks that do not fit on the GPU (deviation D3, notes.md; decision of 2026-10-18).

Runs scripts/a4_keytar.py unchanged (its main(), its inputs, its fingerprint) with one difference: when the GPU runs
out of memory on a chunk, the same chunk is generated again on the CPU with the same checkpoint and the same
generation settings (check6_keytar.GEN), and the generation goes on. Every chunk at least as long (in intervals) as
the shortest chunk that ran out of memory goes to the CPU directly (a longer input needs more memory, so it would run
out too; this saves the slow attempt on the GPU). The CPU model is loaded for each fallback and freed afterwards, so
it does not hold memory between the fallbacks.

This file is not in FINGERPRINT_FILES: the records keep the fingerprint of the generation (the same inputs and
settings), and the chunks generated on the CPU are listed, with counts, hashes and times only, in
raw/derived_a4_cpu_fallback.jsonl (one line per chunk: the time, the process, the SHA-256 of the chunk, the number of
intervals and of input tokens, the seconds, the reason). The SHA-256 is of the chunk as a4_keytar.writer_inputs
builds it (the intervals joined by spaces), so recomputing the inputs after the generation finds the writers whose
records hold a chunk generated on the CPU. A CPU generation that fails (out of host memory) stops the run with exit 3
instead of restarting it on the same chunk again and again (review of 2026-10-18).

    ~/.venvs/pkm-keytar/Scripts/python -I scripts/a4_keytar_cpu_fallback.py --root ... (the arguments of a4_keytar.py)
"""
import gc
import hashlib
import json
import os
import sys
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import a4_keytar as A  # noqa: E402
import check6_keytar as K  # noqa: E402

FALLBACK_LOG = os.path.join(HERE, "..", "raw", "derived_a4_cpu_fallback.jsonl")
HEARTBEAT = 600  # seconds between the "still running" lines of a CPU generation (the watcher reads a silent log as a stall)


def chunk_sha256(intervals):
    return hashlib.sha256(" ".join(map(str, intervals)).encode("ascii")).hexdigest()


def log_chunk(intervals, tokens, sec, reason, error=None):
    row = {"time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "pid": os.getpid(),
           "chunk_sha256": chunk_sha256(intervals), "intervals": len(intervals), "tokens": tokens,
           "seconds": round(sec, 1), "reason": reason}
    if error:
        row["error"] = error  # the exception's type name only
    with open(FALLBACK_LOG, "a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(row) + "\n")


class FallbackGenerator(A.Generator):
    def __init__(self, model_dir):
        super().__init__(model_dir)
        self.model_dir = model_dir
        self.cpu_from = None  # the shortest chunk (in intervals) that ran out of memory on the GPU

    def __call__(self, intervals):
        if self.cpu_from is not None and len(intervals) >= self.cpu_from:
            return self._cpu(intervals, "direct: at least as long as a chunk that ran out of GPU memory")
        oom = False
        try:
            return super().__call__(intervals)
        except self.torch.OutOfMemoryError:
            oom = True  # handled outside the except block, so that the traceback's GPU tensors are freed first
        if oom:
            gc.collect()
            self.torch.cuda.empty_cache()
            self.cpu_from = len(intervals) if self.cpu_from is None else min(self.cpu_from, len(intervals))
            return self._cpu(intervals, "after out of GPU memory")

    def _cpu(self, intervals, reason):
        from transformers import AutoModelForCausalLM
        t = time.time()
        print("cpu fallback: a chunk of %d intervals (%s)" % (len(intervals), reason), flush=True)
        K.verify_checkpoint(self.model_dir)  # the .bin is read again hours after the check at start (exit 3 if changed)
        msgs = [{"role": "user", "content": K.PROMPT + " ".join(map(str, intervals))}]
        x = self.tok.apply_chat_template(msgs, tokenize=True, add_generation_prompt=True, return_tensors="pt")
        tokens = int(x.shape[1])
        stop = threading.Event()

        def beat():
            while not stop.wait(HEARTBEAT):
                print("cpu fallback running (%.0f s)" % (time.time() - t), flush=True)

        threading.Thread(target=beat, daemon=True).start()
        try:
            model = AutoModelForCausalLM.from_pretrained(self.model_dir, device_map="cpu", local_files_only=True,
                                                         trust_remote_code=False, use_safetensors=False).eval()
            with self.torch.no_grad():
                out = model.generate(x, **K.GEN)
        except (MemoryError, RuntimeError) as e:
            stop.set()
            log_chunk(intervals, tokens, time.time() - t, reason + "; cpu failed", type(e).__name__)
            print("cpu fallback failed (%s): stopping, a restart would fail on the same chunk" % type(e).__name__,
                  flush=True)
            sys.exit(A.PERMANENT)
        stop.set()
        text = self.tok.decode(out.sequences[0][x.shape[1]:], skip_special_tokens=True)
        del out, model, x
        gc.collect()
        sec = time.time() - t
        log_chunk(intervals, tokens, sec, reason)
        print("cpu fallback done (%.0f s)" % sec, flush=True)
        return text.strip("\n|>")


if __name__ == "__main__":
    if A.MUTATE:
        # the mutation tests run scripts/a4_keytar.py; the fallback log is under raw/ whatever --out-dir is
        print("A4_MUTATE is set: use scripts/a4_keytar.py", flush=True)
        sys.exit(A.PERMANENT)
    A.Generator = FallbackGenerator
    A.main()
