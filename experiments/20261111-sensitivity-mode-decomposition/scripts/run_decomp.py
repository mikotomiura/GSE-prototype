"""本計算（conditions.md D1〜D5）: sens の CoAuthor の 20 複製を作り直して最頻値を測り、分解と読みを出す。合成の値だけ。

使い方: python3 -I run_decomp.py <sens_results_dir> <out_dir> <jobs> [--run-id ID] [--only 0,1]
出力: <out_dir>/replicates/<番号>.json（作り直しの書き手ごとの値）・summary.json・tables.md。
門: P-REPRO（pool と g が sens の JSON とビットまで同じ）・P-SAME（2 段の c の中央値が sens の summary と同じ）。外れれば止める。
"""
import glob
import hashlib
import json
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import decomp as DC  # noqa: E402
import pinned2  # noqa: E402
from pinned2 import SY  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))


def code_hash():
    h = hashlib.sha256()
    for p in sorted(glob.glob(os.path.join(HERE, "*.py"))):
        h.update(os.path.basename(p).encode() + open(p, "rb").read())
    for f, v in sorted(pinned2.hashes().items()):
        h.update((f + v).encode())
    return h.hexdigest()


def enc(x):
    """±∞ を文字列に（JSON を厳密に保つ）。"""
    if isinstance(x, float) and not np.isfinite(x):
        if np.isnan(x):
            raise ValueError("NaN を書こうとした")
        return "+inf" if x > 0 else "-inf"
    if isinstance(x, dict):
        return {str(k): enc(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [enc(v) for v in x]
    if isinstance(x, (np.floating,)):
        return enc(float(x))
    if isinstance(x, (np.integer,)):
        return int(x)
    if isinstance(x, (np.bool_,)):
        return bool(x)
    return x


def dec(x):
    if x == "+inf":
        return np.inf
    if x == "-inf":
        return -np.inf
    if isinstance(x, dict):
        return {k: dec(v) for k, v in x.items()}
    if isinstance(x, list):
        return [dec(v) for v in x]
    return x


def load_sens(d):
    reps = {}
    kept = json.load(open(os.path.join(d, "plan.json")))["kept"]  # 前の 27 本だけ（追記の 27〜32 は CS1 で、別のコードのハッシュ）
    for no in kept:
        p = os.path.join(d, "replicates", "%02d.json" % no)
        R = json.load(open(p))
        if R.get("seed") != pinned2.REP_SEED or R.get("code_hash") != pinned2.REP_CODE_HASH:
            sys.exit("sens の複製 %s の seed かコードのハッシュが条件の値と違う" % p)
        reps[R["rep"]["no"]] = R
    cal = json.load(open(os.path.join(d, "calibration.json")))
    if cal.get("seed") != pinned2.REP_SEED or cal.get("code_hash") != pinned2.REP_CODE_HASH:
        sys.exit("sens の calibration.json の seed かコードのハッシュが条件の値と違う")
    summ = json.load(open(os.path.join(d, "summary.json")))
    return reps, {int(k): v for k, v in cal["cal"].items()}, summ


def check_repro(R, M):
    if len(M) != len(R["writers"]):  # レビュー LOW 6
        return [("人数", len(M), len(R["writers"]))]
    bad = []
    for w, (Wr, m) in enumerate(zip(R["writers"], M)):
        if Wr["g"] != m["g"] or Wr["n_eval"] != m["n_eval"]:
            bad.append((w, "g/n_eval"))
        for s, v in Wr["pool"].items():
            if v != m["pool"][s]:
                bad.append((w, s))
    return bad


def main():
    argv = sys.argv[1:]
    run_id, only = None, None
    if "--run-id" in argv:
        i = argv.index("--run-id"); run_id = argv[i + 1]; argv = argv[:i] + argv[i + 2:]
    if "--only" in argv:
        i = argv.index("--only"); only = [int(x) for x in argv[i + 1].split(",")]; argv = argv[:i] + argv[i + 2:]
    sens, out, jobs = argv[0], argv[1], int(argv[2])
    os.makedirs(os.path.join(out, "replicates"), exist_ok=True)
    seed = pinned2.REP_SEED
    ch = code_hash()
    reps, cal, summ = load_sens(sens)
    nos = sorted(n for n, R in reps.items() if R["rep"]["shape"] == "coauthor")
    if only is not None:
        nos = [n for n in nos if n in only]
    if only is None and nos != list(range(13)) + list(range(20, 27)):  # D1 の 20 本（レビュー LOW 7）
        sys.exit("CoAuthor の複製の番号が D1 の 20 本と違う: %r" % nos)
    m0s = {K: SY.make_m0(K, seed) for K in (3, 5)}
    pairs, timing, reused = [], {}, []
    t_start = time.time()
    for i, no in enumerate(nos):
        R = reps[no]
        p = os.path.join(out, "replicates", "%02d.json" % no)
        if os.path.exists(p):
            old = dec(json.load(open(p)))
            if (old.get("code_hash") != ch or old.get("rep") != R["rep"] or old.get("sens_run_id") != R.get("run_id")
                    or old.get("pool_full_diag") != R["pool_full_diag"]):
                sys.exit("作り直しの %02d のコードのハッシュ・行・sens の run_id・診断が今回と違う（消してからやり直す）" % no)
            M = old["writers"]
            reused.append(no)
        else:
            t0 = time.time()
            M, diag = DC.rebuild(R["rep"], cal, m0s, seed, jobs)
            if diag != R["pool_full_diag"]:
                sys.exit("P-REPRO: 全員の共通の診断が sens と違う（複製 %02d）" % no)
            sec = time.time() - t0
            json.dump(enc(dict(rep=R["rep"], run_id=run_id, code_hash=ch, sens_run_id=R.get("run_id"), writers=M,
                               pool_full_diag=diag, seconds=sec)), open(p, "w"))
            print("複製 %02d（%s）%.0f 秒" % (no, R["rep"]["strand"], sec), flush=True)
            if i == 0 and only is None:  # V2: 最初の複製の時間 × 本数で見積もり、24 時間を超えるなら止める（レビュー MEDIUM 3）
                est = sec * len(nos) / 3600
                print("見積もり %.1f 時間" % est, flush=True)
                if est > 24:
                    sys.exit("見積もりが %.1f 時間で 24 時間を超える。止めて研究者に聞く" % est)
        bad = check_repro(R, M)  # 再開の道でも当てる（レビュー MEDIUM 4）
        if bad:
            sys.exit("P-REPRO が外れた（複製 %02d・%d 件・例 %r）。止めて研究者に聞く" % (no, len(bad), bad[:3]))
        timing[no] = json.load(open(p))["seconds"]
        pairs.append((R, M))
    S = DC.summarize(pairs)
    # P-SAME: 2 段の c の中央値が sens の summary の主の量と同じ
    ref = {(c["no"], c["k"]): c["main"]["median"] for c in summ["cells"]}
    diff = [(c["no"], c["k"]) for c in S["cells"] if c["two_stage"]["c"]["median"] != ref[(c["no"], c["k"])]]
    if diff:
        sys.exit("P-SAME が外れた: %r" % diff[:5])
    S.update(run_id=run_id, code_hash=ch, seed=seed, sens_code_hash=pinned2.REP_CODE_HASH, p_same="ok",
             replicates=nos, reused=reused, seconds=timing, wall_seconds=time.time() - t_start,
             sens_summary_sha256=hashlib.sha256(open(os.path.join(sens, "summary.json"), "rb").read()).hexdigest())
    for c in S["cells"]:  # 書き手ごとの合成の値は replicates/ に置き、summary には集計だけ
        c["two_stage"].pop("values")
        for s in DC.ROW_SUB:
            c["tau_1e6"][s].pop("values")
    json.dump(enc(S), open(os.path.join(out, "summary.json"), "w"), indent=1, ensure_ascii=False)
    write_tables(S, os.path.join(out, "tables.md"))


def f(x):
    if x is None:
        return "—"
    if isinstance(x, float) and not np.isfinite(x):
        return "+∞" if x > 0 else "−∞"
    return ("%+.2e" % x) if x != 0 else "0"


def write_tables(S, path):
    L = ["# 感度の合成の最頻値の分解（合成の値だけ・実データではない）", "",
         "a = 本人 − 最頻値・b = 最頻値 − 共通・c = 本人 − 共通（1 記号あたり・書き手ごとの差の中央値）。良 = a > 0 の割合。",
         "形は 2 段（他人）の行（conditions.md D4）。副は τ = 10^6 の ar1・ar2・ar3 の形。", "",
         "| 筋 | 真 K | g* | 種 | k | a 中央値 | 良 | b 中央値 | c 中央値 | ±∞（a の +∞） | τ = ∞ | 形（読んだ所） | 副の形 ar1/ar2/ar3 | 最頻値 −∞ の人数 ar1/ar2/ar3 |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for c in S["cells"]:
        t = c["two_stage"]
        L.append("| %s | %d | %g | %d | %s | %s | %.2f | %s | %s | %d | %d | %s（%s） | %s | %s |" % (
            c["strand"], c["K"], c["g_target"], c["seed"], c["k"], f(t["a"]["median"]), t["a"]["better_share"],
            f(t["b"]["median"]), f(t["c"]["median"]), t["a"]["pos_inf"], t["n_inf"], c["form"], c["form_src"],
            "/".join(c["forms_1e6"][s] for s in DC.ROW_SUB), "/".join(str(c["mode_neg_inf"][s]) for s in DC.ROW_SUB)))
    dist = [c for c in S["cells"] if "planted_a" in c]
    if dist:
        L += ["", "## 分布の筋（埋めた書き手と埋めていない書き手の a）", "", "| 種 | k | 埋めた a 中央値（n） | 埋めていない a 中央値（n） |", "|---|---|---|---|"]
        for c in dist:
            L.append("| %d | %s | %s（%d） | %s（%d） |" % (c["seed"], c["k"], f(c["planted_a"]["median"]), c["planted_a"]["n"],
                                                         f(c["unplanted_a"]["median"]), c["unplanted_a"]["n"]))
    L += ["", "## 読み（D5 の機械の当て）", "", "```", json.dumps(enc(S["readings"]), indent=1, ensure_ascii=False), "```"]
    open(path, "w").write("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
