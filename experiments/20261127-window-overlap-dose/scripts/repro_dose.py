"""端の再現の門（conditions V1・P-REPRO-U・P-REPRO-N）: 列 A1 を S13 の u、列 A30 を S13 の n（どちらも CoAuthor）と照らす。

照らす葉: S13 の results/summary.json の columns.<u|n>.coauthor の
- fit.em（P15 の k = 1・5・15 × 4 構造 × τ 固定の 9 行・τ 他人 × 相手 r1・同じ構造の共有 × 全記号・押下のある記号の中央値・四分位・
  良い側の割合・人数・伏せ、共有 − r1、選ばれた τ と区分、診断、ジョイント（他人）と選ばれた構造・τ、人数・学習と評価の記号の数）
- fit.pool_full_diag（全員の共有の診断）
- residual（残差の集計）
数は相対 1e-9、文字列・真偽・None は一致（S13 の repro_check.py の Acc をそのまま使う）。区間（ci）・時間・run_id は照らさない。
出すのは照らした数・外れた数・最大の差・外れた節の名前だけ。

使い方: python3 -I repro_dose.py <この試験の summary.json> <S13 の summary.json> <out.json> <A1|A30>
返り値: 0 = すべて一致・3 = 外れた葉がある（または照らす葉が 0）。
"""
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
S13 = os.path.realpath(os.path.join(HERE, "../../20261107-unsmoothed-residual-check/scripts"))
spec = importlib.util.spec_from_file_location("repro13", os.path.join(S13, "repro_check.py"))
R13 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(R13)
PAIR = {"A1": "u", "A30": "n"}


def compare(new, old, col):
    A = R13.Acc()
    o = old["columns"][PAIR[col]]["coauthor"]
    n = new["columns"].get(col, {})
    get = lambda d, *p: R13.get(d, *p)  # noqa: E731
    A.walk(o["fit"]["em"], get(n, "fit", "em"), "%s/fit/em" % col)
    A.walk(o["fit"]["pool_full_diag"], get(n, "fit", "pool_full_diag"), "%s/fit/pool_full_diag" % col)
    A.walk(o["residual"], get(n, "residual"), "%s/residual" % col)
    return dict(column=col, against="S13/" + PAIR[col], leaves=A.leaves, mismatched=A.bad, max_rel_diff=A.worst,
                tolerance_rel=R13.REL, mismatched_sections=sorted(A.sections))


def main(argv):
    new, old = json.load(open(argv[0], encoding="utf-8")), json.load(open(argv[1], encoding="utf-8"))
    r = compare(new, old, argv[3])
    r["passed"] = r["leaves"] > 0 and r["mismatched"] == 0
    json.dump(r, open(argv[2], "w"), indent=1)
    print(json.dumps(r))
    return 0 if r["passed"] else 3


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
