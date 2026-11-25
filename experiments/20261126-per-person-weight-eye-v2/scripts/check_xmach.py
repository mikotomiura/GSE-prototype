"""P-XMACH: 2 台の selftest.json の記号の列の SHA-256 と、Python・numpy の版が一致するか。合わなければ止める（決定的な検査）。"""
import json
import sys


def main():
    a, b, out = sys.argv[1], sys.argv[2], sys.argv[3]
    A, B = json.load(open(a))["P-XMACH"], json.load(open(b))["P-XMACH"]
    ok = A["sha256"] == B["sha256"] and A["python"] == B["python"] and A["numpy"] == B["numpy"]
    json.dump(dict(a=A, b=B, ok=ok), open(out, "w"), indent=1)
    if not ok:
        sys.exit("P-XMACH が赤: %r / %r" % (A, B))
    print("P-XMACH 緑: %s（Python %s・numpy %s）" % (A["sha256"][:12], A["python"], A["numpy"]))


if __name__ == "__main__":
    main()
