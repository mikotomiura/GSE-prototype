"""E1-8 candidates (no criterion) and sample images of the provisional grammars.

E1-8: three ways of returning to the ground at the end of a session (design 3.7):
  fade  - the shape fades to the ground over 30 s
  seed  - the shape folds into one small mark at its centroid
  none  - nothing happens at the end; the next session simply starts from the ground
Each candidate is written as a strip of frames. The samples show the final image of each
generator configuration for two sessions, so that the researcher can see what was tested.

Usage: render_e18.py <config.json> <SEED> <work dir> <out dir>
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


def strip(frames: list[np.ndarray], gap: int = 6) -> np.ndarray:
    h, w = frames[0].shape[:2]
    out = np.ones((h, len(frames) * w + (len(frames) - 1) * gap, 3), dtype=np.float32)
    for i, f in enumerate(frames):
        out[:, i * (w + gap) : i * (w + gap) + w] = f
    return out


def main() -> int:
    cfg = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    seed = int(Path(sys.argv[2]).read_text().strip())
    work, out = Path(sys.argv[3]), Path(sys.argv[4])
    (out / "e18").mkdir(parents=True, exist_ok=True)
    (out / "samples").mkdir(parents=True, exist_ok=True)
    manifest = {m["sid"]: m for m in json.loads((work / "sessions.json").read_text(encoding="utf-8"))}
    C = checks.configs(cfg)
    ground = np.asarray(cfg["canvas"]["ground"], dtype=np.float32)
    for sid in ("P000", "P001"):
        sess = pt.load_session(work, manifest[sid])
        for c in C["base6"]:
            r = pt.run(sess, c, cfg, seed, False, True)
            to_png(r["final"], out / "samples" / f"{sid}-{c.name}.png")
        final = pt.run(sess, C["base6"][2], cfg, seed, False, True)["final"]  # ordinal-none
        g = np.empty_like(final)
        g[:] = ground
        fade = [final + (g - final) * k for k in (0.0, 1 / 3, 2 / 3, 1.0)]
        dev = pt.deviation(final, ground)
        mask = dev > cfg["canvas"]["coverage_eps"]
        seed_frames = [final]
        if mask.any():
            w = dev * mask
            h_, w_ = final.shape[:2]
            cx = float((w.sum(axis=0) * np.arange(w_)).sum() / w.sum())
            cy = float((w.sum(axis=1) * np.arange(h_)).sum() / w.sum())
            col = final[mask].mean(axis=0)
            for scale in (0.5, 0.2):
                content = final - ground
                from scipy import ndimage
                z = np.stack([ndimage.affine_transform(content[..., ch], np.diag([1 / scale, 1 / scale]),
                                                       offset=[cy - cy / scale, cx - cx / scale], order=1,
                                                       mode="constant", cval=0.0) for ch in range(3)], axis=2)
                seed_frames.append(ground + z)
            gen = pt.Generator("ordinal", "none", cfg, 1)
            gen._blob(cx, cy, 4.0, col.astype(np.float32), 0.8)
            seed_frames.append(gen.base.copy())
        none = [final, final, g]
        to_png(strip(fade), out / "e18" / f"{sid}-fade.png", 1)
        to_png(strip(seed_frames), out / "e18" / f"{sid}-seed.png", 1)
        to_png(strip(none), out / "e18" / f"{sid}-none.png", 1)
    print("rendered E1-8 candidates and samples")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
