"""漏れの検査（ADR-051 D3・ADR-056 D4）の B′ を、漏れの机上の道具の stats.py にそのまま渡す。

gse-replay --handmark-windows --stopped の窓の表は、窓ごとに b_state（13）と b_stopped（9）を持つ。ここでは
b_state を b_state + b_stopped（22）に置き換えた写しを作るだけで、統計（stats.py）は書き換えない。
画素は overlay.mjs windows の出力（止まりの層を重ねた B_pixel′）を --pixels に渡す。

  python leak_prime.py <w.ndjson> <out_w.ndjson>
"""
import json
import sys


def main(argv):
    src, dst = argv
    n = 0
    with open(src, encoding="utf-8") as f, open(dst, "w", encoding="utf-8", newline="\n") as g:
        for line in f:
            r = json.loads(line)
            kind = r.get("kind")
            if kind == "header":
                names = r.get("b_stopped_names")
                if not names or "stopped" not in r:
                    raise SystemExit("窓の表に止まりの層が無い（--stopped で作る）")
                r["b_state_names"] = list(r["b_state_names"]) + [f"stopped_{x}" for x in names]
                r["b_prime"] = True
            elif kind != "summary":
                b = r.pop("b_stopped", None)
                if not isinstance(b, list) or len(b) != 9:
                    raise SystemExit(f"窓 {r.get('id')} に b_stopped が無い")
                r["b_state"] = list(r["b_state"]) + b
                n += 1
            g.write(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n")
    print(json.dumps({"windows": n}))


if __name__ == "__main__":
    main(sys.argv[1:])
