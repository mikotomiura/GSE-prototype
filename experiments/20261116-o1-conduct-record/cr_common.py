"""共通: 人ごとの本の読み込み・repo に入れる版（R7）。

n4 の pausestall の public・round_count を、コードを変えずに包んで使う（import した時点で差し替わる。R3 も
この包みを通して回す）:
- 件数の丸めを「半分以上は切り上げ」にする（Python の round は偶数側に丸め、50 を 0 にする）
- 件数のキーの許可リストを足す
- 丸める前に伏せる: 停滞の割合を伏せる型（分母が 20 未満）では兄弟の差と区間も伏せ、無作為の窓は割合だけを残す
- 全体を丸めた後に粗くする: 割合（キー ratio）は小数 2 桁、率（キーが per_ を含み _h で終わる）と share を含むキーは
  有効数字 2 桁、AUC・差・区間は小数 3 桁。自分のキーに規則が無い子（by_person・min・max・記号・閾値）は親のキーの規則を引き継ぐ。
  規則の無い小数（分位・SD・比・θ・混合の母数）は有効数字 3 桁。出さないキー（版の種類の数・無作為の窓の数）を落とす
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "../20261103-o1-n4-pause-stall"))
sys.path.insert(0, os.path.join(HERE, "../20261102-stall-decomposition"))
sys.path.insert(0, os.path.join(HERE, "../20261102-stall-decomposition/o1"))
sys.path.insert(0, os.path.join(HERE, "../20261101-klicke-early-stall-trigger/scripts"))
import pausestall as ps  # noqa: E402

H = 3_600_000
# R7: 件数のキー（丸める）。n4 の許可リストに足す
EXTRA_COUNT_KEYS = {"total", "max_day_number", "missing_day_numbers", "duplicated_day_numbers", "calendar_days",
                    "files_zero_obs", "files_no_focus", "files_used", "stalls_onsets", "stalls_used", "controls_used",
                    "pairs", "files_with_stalls", "days_with_stalls", "boot_failures", "excl_u_ge_s", "excl_short_gap",
                    "excl_early", "excl_no_feat", "excl_no_interval", "excl_no_control", "excl_dup_u", "stalls_typed",
                    "random_windows", "days_used"}
ps.COUNT_KEYS |= EXTRA_COUNT_KEYS
DROP_KEYS = {"app_version_kinds", "random_windows", "total", "secure_input"}
# 公開の版では出さない: 版の数は期間の目安・無作為の窓の数は停滞の数 × 10・行の型の総数は率で割ると観測時間が戻る・
# secure_input の行は macOS だけが出すので OS が分かる（判断 12）
THREE_KEYS = {"auc_K", "auc_KN", "delta_auc", "diff"}
THREE_PARENTS = {"signal_auc", "ci95", "diff_ci95", "K", "KN", "delta"}


def round_half_up(v):
    """件数・本数: 50 未満は 5 単位、50 以上は 100 単位。半分以上は切り上げ。"""
    step = 5 if v < 50 else 100
    return int(math.floor(v / step + 0.5) * step)


def sig2(x):
    if x == 0 or not math.isfinite(x):
        return x
    return round(x, 1 - int(math.floor(math.log10(abs(x)))))


def sig3(x):
    if x == 0 or not math.isfinite(x):
        return x
    return round(x, 2 - int(math.floor(math.log10(abs(x)))))


def rule(key):
    """キーの名前から粗さの規則を決める。"""
    if key is None:
        return None
    if key == "ratio":
        return "dp2"
    if ("per_" in key and key.endswith("_h")) or "share" in key:
        return "sig2"
    if key in THREE_KEYS or key in THREE_PARENTS:
        return "dp3"
    return None


def coarsen(x, key=None, parent=None):
    if isinstance(x, dict):
        out = {}
        for k, v in x.items():
            if k in DROP_KEYS:
                continue
            if k == "ratio" and key == "files_with_rows":
                continue  # 分母（本数）を共有する割合が並ぶと本数が 1 通りに戻る（判断 12）
            ck = k if rule(k) else (key if rule(key) else k)  # 自分のキーに規則が無い子は親の規則を引き継ぐ
            out[k] = coarsen(v, ck, key)
        return out
    if isinstance(x, list):
        return [coarsen(v, key, parent) for v in x]
    if isinstance(x, bool) or not isinstance(x, float):
        return x
    r = rule(key) or ("dp3" if parent in THREE_PARENTS else None)
    if r == "dp2":
        return round(x, 2)
    if r == "sig2":
        return sig2(x)
    if r == "dp3":
        return round(x, 3)
    return sig3(x)  # 規則の無い小数（分位・SD・比・θ・混合の母数）は有効数字 3 桁


def mask_small(x):
    """丸める前に: 停滞の割合を伏せる型（分母が MIN_DEN 未満）では、兄弟の差と区間も伏せる。無作為の窓は割合だけ残す。"""
    if isinstance(x, dict):
        out = {k: mask_small(v) for k, v in x.items()}
        st = out.get("stall")
        if isinstance(st, dict) and "diff" in out and isinstance(st.get("den"), int) and st["den"] < ps.MIN_DEN:
            out["diff"] = None
            out["diff_ci95"] = None
        if isinstance(out.get("random"), dict) and "ratio" in out["random"]:
            out["random"] = {"ratio": out["random"]["ratio"]}  # 数と分母は出さない（分母は停滞の数 × 10）
        return out
    if isinstance(x, list):
        return [mask_small(v) for v in x]
    return x


_orig_public = ps.public


def public(x, key=None, parent=None):
    # 一番外の呼び出しでだけ伏せて粗くする（n4 の public は自分を名前で再帰に呼ぶので、内側はそのまま通す）
    if key is None and parent is None:
        return coarsen(_orig_public(mask_small(x)))
    return _orig_public(x, key, parent)


ps.round_count = round_half_up
ps.public = public


def ci95(xs):
    """百分位の 95% 区間（R4・R5 で共通）。下の端は切り捨て、上の端は切り上げの位置。"""
    if not xs:
        return None
    s = sorted(xs)
    return [round(s[int(0.025 * (len(s) - 1))], 4), round(s[int(math.ceil(0.975 * (len(s) - 1)))], 4)]


def load_people(work):
    """files.json から {記号: [(row, inter, extra)]}。中間と平文の SHA-256 を照らす。"""
    table = json.load(open(os.path.join(work, "files.json")))
    out = {}
    for pid, p in table["people"].items():
        rows = []
        for f in p["files"]:
            try:
                d = json.load(open(f["inter"]))
                x = json.load(open(f["extra"]))
            except (OSError, ValueError, KeyError):
                sys.exit(f"中間が読めない（人 {p['symbol']}）")
            if d["input_sha256"] != f["plain_sha256"] or x["plain_sha256"] != f["plain_sha256"]:
                sys.exit(f"中間と平文の SHA-256 が合わない（人 {p['symbol']}）")
            rows.append((f, d, x))
        out[p["symbol"]] = rows
    return table, out


def obs_ms(d):
    return sum(iv["b_ms"] - iv["a_ms"] for iv in d["observed_intervals"])


def write_public(res, work, name, out, table):
    """丸めない版を repo の外へ、丸めた版を repo へ。漏れがあれば止める。"""
    json.dump(res, open(os.path.join(work, name + ".full.json"), "w"), indent=1, ensure_ascii=False)
    text = json.dumps(ps.public(res), indent=1, ensure_ascii=False)
    vers = {str(f.get(k)) for p in table["people"].values() for f in p["files"] for k in ("app_version", "hmm_version")}
    lk = ps.leaks(text, table["people"], vers)
    if lk:
        sys.exit("公開用の出力に漏れ: " + "・".join(lk))
    open(out, "w").write(text)


def run_r3(work, seed, out):
    """R3: n4 の pausestall.run を、この包み（丸めと粗さ）を通して回す。"""
    ps.run(work, seed, out)


if __name__ == "__main__" and len(sys.argv) == 5 and sys.argv[1] == "--r3":
    run_r3(*sys.argv[2:])
