"""複製の結果 → summary.json と tables.md（conditions.md D4・D7）。合成の値だけ。

使い方: python3 -I sens_report.py <results_dir> [--run-id ID]
"""
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import analysis as AN  # noqa: E402


def f(x, d=4):
    if x is None:
        return "—"
    return ("%+.2e" % x) if abs(x) < 1e-2 and x != 0 else ("%+.*f" % (d, x))


def main():
    argv = sys.argv[1:]
    run_id = None
    if "--run-id" in argv:
        i = argv.index("--run-id"); run_id = argv[i + 1]; argv = argv[:i] + argv[i + 2:]
    out = argv[0]
    reps = [json.load(open(p)) for p in sorted(glob.glob(os.path.join(out, "replicates", "*.json")))]
    S = AN.summarize(reps)
    S["run_id"] = run_id
    S["calibration"] = json.load(open(os.path.join(out, "calibration.json")))
    S["plan"] = json.load(open(os.path.join(out, "plan.json")))
    json.dump(S, open(os.path.join(out, "summary.json"), "w"), indent=1)
    L = ["# 感度の合成の表（合成の値だけ・実データではない）", "",
         "主の量 = 2 段（他人）の本人 − 同じ構造の共通（1 記号あたりの対数尤度・全記号）。良 = > 0 の割合。g = 真の本人の利得。", "",
         "| 筋 | 形 | 真 K | g* | 種 | k | λ | 主の量 中央値 [四分位] | 良 | 本人 − r1 | g 中央値 | 回収 | 選ばれた構造 | 選ばれた τ |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for c in S["cells"]:
        m = c["main"]
        L.append("| %s | %s | %d | %g | %d | %s | %.4f | %s [%s, %s] | %.2f | %s | %s | %s | %s | %s |" % (
            c["strand"], c["shape"], c["K"], c["g_target"], c["seed"], c["k"], c["lam"], f(m["median"]), f(m["q25"]),
            f(m["q75"]), m["better_share"], f(c["vs_r1"]["median"]), f(c["g"]["median"]),
            "—" if c["recovery"] is None else "%.2f" % c["recovery"],
            " ".join("%s:%d" % kv for kv in sorted(c["chosen_struct"].items())),
            " ".join("%s:%d" % kv for kv in sorted(c["chosen_tau"].items(), key=lambda kv: float(kv[0])))))
    L += ["", "## 読み（D7 の機械の当て）", "", "```", json.dumps(S["readings"], indent=1, ensure_ascii=False), "```"]
    open(os.path.join(out, "tables.md"), "w").write("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
