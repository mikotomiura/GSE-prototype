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
    cal = json.load(open(os.path.join(out, "calibration.json")))
    plan = json.load(open(os.path.join(out, "plan.json")))
    # 計画（前の 27 本は plan.json・追記の 6 本は plan_add.json）ごとに、複製の集合が完全に一致し（余り・欠け・重複）、
    # seed とコードのハッシュが計画と揃うか（Codex の指摘 1・2026-11-11 の追記で 2 群に）
    if plan.get("seed") is None or plan.get("code_hash") is None:
        sys.exit("plan.json に seed かコードのハッシュが無い")
    plans = [plan]
    pa = os.path.join(out, "plan_add.json")
    if os.path.exists(pa):
        plan_add = json.load(open(pa))
        if (not plan_add.get("p_rerep") or plan_add.get("base_code_hash") != plan.get("code_hash")
                or plan_add.get("seed") != plan.get("seed") or plan_add.get("code_hash") is None):
            sys.exit("plan_add.json の P-REREP が通っていないか、前の計画の seed・ハッシュと合わない")
        rows_add = {r["no"]: r for r in plan_add["rows"]}
        bad_rows = [R["rep"]["no"] for R in reps if R["rep"]["no"] in rows_add and R["rep"] != rows_add[R["rep"]["no"]]]
        if bad_rows or sorted(rows_add) != sorted(plan_add["kept"]):
            sys.exit("足した複製の行が plan_add.json の rows と違う: %r" % bad_rows)
        plans.append(plan_add)
    nos = [R["rep"]["no"] for R in reps]
    if len(nos) != len(set(nos)) or sorted(nos) != sorted(n for pl in plans for n in pl["kept"]):
        sys.exit("複製の番号が計画の kept と一致しない: 複製 %r" % sorted(nos))
    for pl in plans:
        hs_pl = {(R.get("seed"), R.get("code_hash")) for R in reps if R["rep"]["no"] in pl["kept"]}
        if hs_pl != {(pl.get("seed"), pl.get("code_hash"))}:
            sys.exit("複製の seed かコードのハッシュが計画と揃っていない: %r" % hs_pl)
    if (cal.get("seed"), cal.get("code_hash")) != (plan.get("seed"), plan.get("code_hash")):
        sys.exit("calibration.json の seed・コードのハッシュが前の計画と違う")
    hs = {(R.get("seed"), R.get("code_hash")) for R in reps}
    S = AN.summarize(reps)
    S["code_hash"] = next(iter(hs))[1] if len(hs) == 1 else sorted(h for _, h in hs)
    if len(plans) > 1:
        S["plan_add"] = plans[1]
    S["run_ids"] = sorted({R.get("run_id") for R in reps if R.get("run_id")})
    S["run_id"] = run_id
    S["calibration"] = cal
    S["plan"] = plan
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
