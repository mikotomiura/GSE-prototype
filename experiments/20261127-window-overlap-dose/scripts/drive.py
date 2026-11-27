"""駆動（conditions D3）: S13 の fit.py の run()・residual.py の run() を、列の読み込みだけを load_dose に差し替えて回す。
足す量（M・D_s・ρ_h・頭を除く採点）は extra.py。

使い方:
  python3 -I drive.py fit      <col> <work> <sidecar> <seed> <out_dir> <raw_dir> <jobs> [--run-id ID]
  python3 -I drive.py residual <col> <work> <sidecar> <seed> <out_dir> <raw_dir> [--run-id ID]
  python3 -I drive.py extra    <col> <work> <sidecar> <seed> <out_dir> <raw_dir> [--run-id ID]
出力の名は S13 のまま（<out_dir>/parts/fit.coauthor.<col>.json など・<raw_dir>/unsmoothed_residual_*.coauthor.<col>.*）。
raw_dir は repo の外（$DATA_DIR/landscape/window_overlap_raw）。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # -I では自分のディレクトリが入らない
import swap  # noqa: E402,F401  ここで "load" が load_dose に替わる（spawn の子でも先頭で実行される）
from swap import F, R, load_dose  # noqa: E402


def main(argv):
    run_id = None
    if "--run-id" in argv:
        i = argv.index("--run-id")
        run_id = argv[i + 1]
        argv = argv[:i] + argv[i + 2:]
    mode, col = argv[0], argv[1]
    load_dose.parse(col)
    if mode == "fit":
        work, side, seed, out, raw, jobs = argv[2:8]
        F.run("coauthor", col, work, side, int(seed), out, raw, int(jobs), run_id)
        return 0
    work, side, seed, out, raw = argv[2:7]
    if mode == "residual":
        return R.run("coauthor", col, work, side, int(seed), out, raw, run_id)
    if mode == "extra":
        import extra
        return extra.run(col, work, side, int(seed), out, raw, run_id)
    raise SystemExit("mode は fit・residual・extra")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
