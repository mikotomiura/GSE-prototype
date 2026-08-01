#!/usr/bin/env python3
"""Rust ソースから φ / β / X・Y 合成重みを抽出して config へ書き出す。

**Python 側で定数をハードコードしない**ための層。ハードコードすると
`engine.rs` を変えたときに診断結果が黙ってずれる (二重定義の drift)。
抽出に失敗したら非ゼロ終了する (fail-closed)。

使い方: extract_constants.py <repo_root> <out_config.json>
"""
import json
import re
import sys
from pathlib import Path

ENGINE = "src-tauri/src/analysis/engine.rs"
FEATURES = "src-tauri/src/analysis/features.rs"


def die(msg):
    print(f"[extract_constants] FAILED: {msg}", file=sys.stderr)
    sys.exit(1)


def read(root, rel):
    p = Path(root) / rel
    if not p.is_file():
        die(f"{rel} が見つからない (repo_root={root})")
    return p.read_text(encoding="utf-8")


_PLAIN_FLOAT = re.compile(r"^[0-9]+(\.[0-9]+)?$")


def grab_float(src, pattern, what):
    """`= <値>;` の値部分を丸ごと取ってから厳格に検証する。

    `([0-9.]+)` のような前方一致で取ると **静かに違う値を返す**:
    `= 1_000.0;` → `1.0` / `= 1.0e-1;` → `1.0` を「成功」として拾ってしまう。
    二重定義 drift を止める層が、いちばん危険な種類の静かな失敗を持つことになる。
    """
    m = re.search(pattern, src)
    if not m:
        die(f"{what} を抽出できない — 正規表現 {pattern!r} が一致しない。"
            " Rust 側の書き方が変わった可能性があるので抽出器を更新すること")
    raw = m.group(1).strip()
    if not _PLAIN_FLOAT.match(raw):
        die(f"{what} の値 {raw!r} が単純な 10 進表記でない"
            " (アンダースコア区切り・指数表記・型サフィックス等)。"
            " 誤った値を静かに採用しないため中止する。抽出器を更新すること")
    return float(raw)


def main():
    if len(sys.argv) != 3:
        die("usage: extract_constants.py <repo_root> <out_config.json>")
    root, out = sys.argv[1], sys.argv[2]

    feats_src = read(root, FEATURES)
    engine_src = read(root, ENGINE)

    kappa = grab_float(feats_src, r"const KAPPA:\s*f64\s*=\s*([^;]+);", "KAPPA")

    # phi の式そのものが期待形か確認する。式が変わったら Python の再実装が無効になる。
    if not re.search(r"\(\(x - beta\) / \(KAPPA \* beta\)\)\.clamp\(0\.0, 1\.0\)", feats_src):
        die("phi() の式が期待形 ((x-beta)/(KAPPA*beta)).clamp(0,1) と違う。"
            " Python 側の再実装を更新すること")

    beta = {}
    for ctx in ("WRITING", "CODING"):
        for f in ("F1", "F3", "F4", "F5", "F6"):
            key = f"BETA_{ctx}_{f}"
            beta[key] = grab_float(
                engine_src, rf"const {key}:\s*f64\s*=\s*([^;]+);", key
            )

    # X = 0.30*phi3 + 0.25*phi6 + 0.25*phi1 + 0.20*phi5
    mx = re.search(
        r"let x = \(([0-9.]+) \* phi3 \+ ([0-9.]+) \* phi6 \+ ([0-9.]+) \* phi1 \+ ([0-9.]+) \* phi5\)",
        engine_src,
    )
    if not mx:
        die("X 合成式を抽出できない (engine.rs の `let x = (...)` の形が変わった)")
    wx = {
        "phi3": float(mx.group(1)),
        "phi6": float(mx.group(2)),
        "phi1": float(mx.group(3)),
        "phi5": float(mx.group(4)),
    }

    # Y = 0.40*phi4 + 0.35*(1-phi1) + 0.25*(1-phi5)
    my = re.search(
        r"let y = \(([0-9.]+) \* phi4 \+ ([0-9.]+) \* \(1\.0 - phi1\) \+ ([0-9.]+) \* \(1\.0 - phi5\)\)",
        engine_src,
    )
    if not my:
        die("Y 合成式を抽出できない (engine.rs の `let y = (...)` の形が変わった)")
    wy = {
        "phi4": float(my.group(1)),
        "one_minus_phi1": float(my.group(2)),
        "one_minus_phi5": float(my.group(3)),
    }

    for name, w in (("X", wx), ("Y", wy)):
        s = sum(w.values())
        if abs(s - 1.0) > 1e-9:
            die(f"{name} の重み合計が 1.0 でない ({s})。engine.rs のコメントの前提が崩れている")

    cfg = {
        "_note": "このファイルは extract_constants.py が Rust ソースから生成する。手で編集しない。",
        "source": {"engine": ENGINE, "features": FEATURES},
        "kappa": kappa,
        "beta": beta,
        "weights_x": wx,
        "weights_y": wy,
    }
    Path(out).write_text(json.dumps(cfg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"[extract_constants] OK: KAPPA={kappa} beta={len(beta)}件 -> {out}")


if __name__ == "__main__":
    main()
