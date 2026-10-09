"""Sample images of the round 2 grammars (no criterion): the final image of each main configuration and of
the positive controls and the oracles for two sessions, so that the researcher can see what was tested. E1-8 is not drawn in
round 2 (design 3.7).

Usage: render_samples.py <config.json> <SEED> <work dir> <out dir>
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

import checks
import portrait as pt


def to_png(img: np.ndarray, path: Path, scale: int = 2) -> None:
    arr = (np.clip(img, 0, 1) * 255).astype(np.uint8)
    im = Image.fromarray(arr)
    im = im.resize((im.width * scale, im.height * scale), Image.NEAREST)
    im.save(path, optimize=True)


def main() -> int:
    cfg = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    seed = int(Path(sys.argv[2]).read_text().strip())
    work, out = Path(sys.argv[3]), Path(sys.argv[4])
    (out / "samples").mkdir(parents=True, exist_ok=True)
    manifest = {m["sid"]: m for m in json.loads((work / "sessions.json").read_text(encoding="utf-8"))}
    C = checks.configs(cfg)
    for sid in ("P000", "P001"):
        sess = pt.load_session(work, manifest[sid])
        for c in C["main"] + [C["pc1"], C["pc2"]] + C["orc"]:
            r = pt.run(sess, c, cfg, seed, False, True)
            to_png(r["final"], out / "samples" / f"synth-{sid}-{c.name}.png")
    print("rendered samples")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
