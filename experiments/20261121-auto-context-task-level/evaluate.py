"""判定（auto-context-task-level・2 段目）。

サブコマンド:
    synth  合成の記録で、作業の境界とまとまりを基準どおりに拾えるかを見る（不合格は終了コード 3）。
    real   人ごとの判定（使える／使えない／判定できない）を出す。合成の人に作業の記録を付けて回すと、
           照合の経路の確かめになる（run.sh Step 2b）。

判定に使うのは v2（`act_hmm.py`）だけ。v1（`act_window.py`）は記述として並べる（判断 7）。
基準は `criteria.json`、解析の引数は `config.json`（1 段目の値は 1 段目の `config.json` と `SEED`）。
記録・封筒・作業の記録・コミットの一覧・結果は外部（Codex を含む）へ送らない。
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
import unicodedata
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import act_hmm as hm  # noqa: E402
import act_window  # noqa: E402
import stage1  # noqa: E402

core = stage1.core
IDLE = core.IDLE

SHARING_MARKER = {
    "gse_dataset": "prohibited",
    "reason": "experiments/20261121-auto-context-task-level の実データ由来の中間成果物（区間の一覧・作業の記録との照合を含む）",
    "rule": "docs/glossary.md 特徴行",
}
PERSON_ID_RE = re.compile(r"[A-Za-z0-9_-]{1,64}")
TZ = ZoneInfo("Asia/Tokyo")


def load_json(path: Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def load_config() -> dict:
    cfg = load_json(HERE / "config.json")
    if "seed" in cfg:
        raise SystemExit("config.json に seed を置かない（SEED の 1 か所から読む）")
    cfg["seed"] = int((HERE / "SEED").read_text(encoding="utf-8").strip())
    if not cfg["pseudo"] > 0:
        raise SystemExit("config.json の pseudo は正にする（0 だと出力の確率が 0 になり前向きの尺度で 0 割りが起きる）")
    return cfg


def dumps(x) -> str:
    return stage1.ev1.dumps(x)


# ---------------------------------------------------------------------------
# 2 段目の当てはめ
# ---------------------------------------------------------------------------

def _sequences(p: stage1.Person, cfg: dict, lo: int = 0, hi: int | None = None) -> tuple[list[hm.Seq], int]:
    # 観測は 1 段目の平滑化の後の様式の名前を、同じ様式の連なりにまとめたもの（判断 9）。
    raw = p.res.labels
    m = len(raw)
    hi = m if hi is None else hi
    win = p.win
    known_idle = win.idle & ~win.unknown_mask()
    reset = hm.reset_points(known_idle, p.seams, stage1.stage1_config()["window_s"], cfg["reset_idle_s"])
    reset = reset.copy()
    reset[lo] = True
    sl = slice(lo, hi)
    seqs = hm.build_run_sequences(raw[sl], raw[sl] == IDLE, reset[sl])
    for s in seqs:
        s.index = s.index + lo
        s.members = [mm + lo for mm in s.members]
    n_sym = int(raw[raw != IDLE].max()) + 1 if (raw != IDLE).any() else 1
    return seqs, n_sym


def fit_v2(p: stage1.Person, cfg: dict, seed: int) -> dict:
    seqs, n_sym = _sequences(p, cfg)
    m = len(p.res.raw_labels)
    if not seqs:
        return {"labels": np.full(m, hm.MISSING, dtype=int), "k": 0, "n_symbols": n_sym, "emis": None}
    h = hm.select_hmm(seqs, n_sym, cfg["k_max"], hm.stay_prob(cfg["mean_stay_runs"]), seed,
                      cfg["n_init"], cfg["pseudo"])
    return {"labels": hm.decode(seqs, h, m), "k": h.k, "n_symbols": n_sym, "emis": h.emis.round(3).tolist()}


def stability_ari(p: stage1.Person, cfg: dict, seed: int) -> float:
    """観測のある窓を時間で半分に分け、前半で学んだモデルと後半だけで学んだモデルで後半を復号した列の ARI。"""
    obs_idx = np.flatnonzero(p.res.labels != IDLE)
    if len(obs_idx) < 2 * cfg["stability_min_obs_per_half"]:
        return math.nan
    cut = int(obs_idx[len(obs_idx) // 2])
    m = len(p.res.raw_labels)
    first, n_sym = _sequences(p, cfg, 0, cut)
    second, _ = _sequences(p, cfg, cut, m)
    ps = hm.stay_prob(cfg["mean_stay_runs"])
    h1 = hm.select_hmm(first, n_sym, cfg["k_max"], ps, seed, cfg["n_init"], cfg["pseudo"])
    h2 = hm.select_hmm(second, n_sym, cfg["k_max"], ps, seed + 1, cfg["n_init"], cfg["pseudo"])
    l1 = hm.decode(second, h1, m)
    l2 = hm.decode(second, h2, m)
    mask = l1 != hm.MISSING
    return core.ari(l1[mask], l2[mask])


def boundaries(lab: np.ndarray, starts: np.ndarray) -> list[int]:
    """観測のある窓だけを並べ、前の観測の窓と名前が変わった窓の開始時刻。"""
    idx = np.flatnonzero(lab != hm.MISSING)
    return [int(starts[idx[i]]) for i in range(1, len(idx)) if lab[idx[i]] != lab[idx[i - 1]]]


# ---------------------------------------------------------------------------
# 照合の材料を窓へ写す
# ---------------------------------------------------------------------------

class DiaryError(SystemExit):
    pass


def _norm(x: str) -> str:
    return unicodedata.normalize("NFKC", x).strip()


def parse_diary_md(path: Path, pcs: dict[str, str]) -> dict:
    """`work/diary.md` の表を読む。行は「時刻・作業・PC・後で」。日付は `## YYYY-MM-DD` で始まる見出し。

    黙って誤らないよう、読めない行は止める（code-reviewer HIGH・判断 16）。
    - `##` で始まる行は、日付で始まらなければ止める（後ろに曜日などが付くのはよい）。
    - 表の行は、見出しの行・区切りの行・全部が空の行を飛ばす。それ以外で時刻が読めない・作業が空・
      PC が `pcs`（NFKC で正規化して小文字にした名前 → 正式の名前）に無い行は止める。
    - 全角の数字やコロンは NFKC で半角に直してから読む。
    """
    entries = []
    day = None
    for no, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), start=1):
        if line.startswith("##"):
            m = re.match(r"^##\s+(\d{4}-\d{2}-\d{2})", _norm(line))
            if not m:
                raise DiaryError(f"作業の記録 {no} 行目: 見出しが日付（YYYY-MM-DD）で始まっていない")
            day = m.group(1)
            continue
        if not line.lstrip().startswith("|"):
            continue
        cells = [_norm(c) for c in line.strip().strip("|").split("|")]
        if all(c == "" for c in cells) or cells[0] == "時刻" or re.fullmatch(r"[-:\s]+", "".join(cells)):
            continue
        if day is None:
            raise DiaryError(f"作業の記録 {no} 行目: 日付の見出しより前に表の行がある")
        if len(cells) < 3 or not re.fullmatch(r"\d{1,2}:\d{2}", cells[0]):
            raise DiaryError(f"作業の記録 {no} 行目: 時刻（HH:MM）が読めない")
        if cells[1] == "":
            raise DiaryError(f"作業の記録 {no} 行目: 作業が空")
        pc = pcs.get(cells[2].lower())
        if pc is None:
            raise DiaryError(f"作業の記録 {no} 行目: PC が許す名前（{sorted(set(pcs.values()))}）に無い")
        t = datetime.strptime(f"{day} {cells[0]}", "%Y-%m-%d %H:%M").replace(tzinfo=TZ)
        entries.append({"start_ms": int(t.timestamp() * 1000), "task": cells[1], "pc": pc,
                        "late": bool(len(cells) > 3 and cells[3])})
    entries.sort(key=lambda e: e["start_ms"])
    return {"entries": entries, "end_ms": None}


def diary_pcs(cfg: dict) -> dict[str, str]:
    return {_norm(k).lower(): v for v, names in cfg["diary_pcs"].items() for k in [v, *names]}


def load_diary(path: Path | None, cfg: dict) -> dict | None:
    if path is None:
        return None
    return parse_diary_md(path, diary_pcs(cfg)) if Path(path).suffix == ".md" else load_json(path)


def diary_label(entry: dict, rule: str) -> str | None:
    """作業の記録の 1 行から照合の名前を作る。

    - `task_or_outside`（主・判断 15）: Mac 以外の PC の行を「（Mac の外）」1 つにまとめる。
    - `mac_only`（記述・判断 16）: Mac 以外の行は照合に入れない（None）。「Mac にいるかどうか」だけで差が出る
      交絡を外して見るため。
    - `task`: 作業名のまま。
    PC が「なし」（離席・休憩・食事）の行は、どの形でも照合に入れない（None・行の終わりの印としてだけ使う・判断 17）。
    """
    if entry["pc"] == "なし":
        return None
    if rule == "task":
        return entry["task"]
    if rule == "task_or_outside":
        return entry["task"] if entry["pc"] == "Mac" else "（Mac の外）"
    if rule == "mac_only":
        return entry["task"] if entry["pc"] == "Mac" else None
    raise ValueError(rule)


def per_window_diary(win, diary: dict | None, rule: str, entry_end: str = "next_entry") -> tuple[list, list, list]:
    """窓の中点を含む記録の行の名前・PC・ブロックの番号（記録の範囲の外は None）。

    行はその次の行の始まりまで続く（`entry_end="day_end"` なら、その行の日の 24 時でも切る）。ブロックは、照合の名前が同じ行が続くところを 1 つにしたもの
    （帰無分布で入れ替える単位。無操作で列が切れてもブロックは切らない・判断 12）。
    """
    m = len(win.start_ms)
    if diary is None or not diary["entries"]:
        return [None] * m, [None] * m, [None] * m
    ent = diary["entries"]
    starts = np.array([e["start_ms"] for e in ent])
    # 最後の行の終わり: 明示が無ければ、最後の行の日の終わり（記録した最後の日の 24 時）まで。
    end = diary.get("end_ms")
    if end is None:
        last = datetime.fromtimestamp(ent[-1]["start_ms"] / 1000, tz=TZ)
        end = int(last.replace(hour=23, minute=59, second=59).timestamp() * 1000) + 1000
    if entry_end not in ("next_entry", "day_end"):
        raise ValueError(entry_end)
    day_end = [int(datetime.fromtimestamp(e["start_ms"] / 1000, tz=TZ).replace(hour=23, minute=59, second=59)
                   .timestamp() * 1000) + 1000 for e in ent]
    ent_block = []
    for j, e in enumerate(ent):
        # 日の 24 時で切るときは、日をまたいだら同じ名前でも別のブロックにする（間に記録の無い時間がある）。
        same = (j > 0 and diary_label(ent[j - 1], rule) == diary_label(e, rule)
                and not (entry_end == "day_end" and day_end[j - 1] != day_end[j]))
        ent_block.append(ent_block[-1] if same else (ent_block[-1] + 1 if ent_block else 0))
    labels, pcs, blocks = [], [], []
    for s0, e0 in zip(win.start_ms, win.end_ms):
        mid = (int(s0) + int(e0)) // 2
        j = int(np.searchsorted(starts, mid, side="right")) - 1
        lab = diary_label(ent[j], rule) if j >= 0 else None
        if j < 0 or mid >= end or lab is None or (entry_end == "day_end" and mid >= day_end[j]):
            labels.append(None)
            pcs.append(None)
            blocks.append(None)
        else:
            labels.append(lab)
            pcs.append(ent[j]["pc"])
            blocks.append(ent_block[j])
    return labels, pcs, blocks


def per_window_commits(win, commits: dict | None, half_window_s: int) -> list:
    """窓の中点の前後 `half_window_s` 秒に入るコミットの単位の多数（無ければ None・同数は名前の順で先）。"""
    m = len(win.start_ms)
    if commits is None or not commits["commits"]:
        return [None] * m
    cs = sorted(commits["commits"], key=lambda c: c["t_ms"])
    ts = np.array([c["t_ms"] for c in cs])
    out = []
    for s0, e0 in zip(win.start_ms, win.end_ms):
        mid = (int(s0) + int(e0)) // 2
        lo = int(np.searchsorted(ts, mid - half_window_s * 1000, side="left"))
        hi = int(np.searchsorted(ts, mid + half_window_s * 1000, side="right"))
        if lo >= hi:
            out.append(None)
            continue
        units: dict[str, int] = {}
        for c in cs[lo:hi]:
            units[c["unit"]] = units.get(c["unit"], 0) + 1
        out.append(sorted(units.items(), key=lambda kv: (-kv[1], kv[0]))[0][0])
    return out


def compare(lab: np.ndarray, ref: list, seams: np.ndarray, crit: dict, seed: int,
            ref_blocks: list | None = None) -> dict:
    """作業の名前と照合の名前のブロックの入れ替えの p（1 段目の判断 14・15 の方式）。

    比べるのは、作業の名前があり（観測のある窓）照合の名前もある窓。ブロックは、照合の名前が続く区間
    （ファイルの継ぎ目か、名前の変化か、比べる窓の飛びで新しいブロック）。
    """
    refa = np.array([r if r is not None else "" for r in ref], dtype=object)
    mask = (lab != hm.MISSING) & (refa != "")
    out = {"windows": int(mask.sum()), "values": {}, "blocks": 0, "testable": False, "nmi": math.nan,
           "p": math.nan, "p_achievable": math.nan}
    if not mask.any():
        return out
    vals, counts = np.unique(refa[mask].astype(str), return_counts=True)
    out["values"] = {str(v): int(c) for v, c in zip(vals, counts)}
    idx = np.flatnonzero(mask)
    if ref_blocks is not None:
        # 作業の記録: ブロックは記録の行（同じ名前が続く行）。ファイルの継ぎ目でも切らない（判断 12）。
        _, blocks = np.unique(np.array([ref_blocks[i] for i in idx]), return_inverse=True)
    else:
        blocks = np.zeros(len(idx), dtype=int)
        for t in range(1, len(idx)):
            i, j = idx[t - 1], idx[t]
            new = refa[i] != refa[j] or bool(seams[i + 1:j + 1].any())
            blocks[t] = blocks[t - 1] + (1 if new else 0)
    out["blocks"] = int(blocks[-1] + 1)
    r = refa[mask].astype(str)
    testable = sum(c >= crit["ref_min_windows_per_value"] for c in counts) >= 2
    if testable:
        _, pa = core.block_permutation_pvalue(r, r, blocks, crit["n_perm"], np.random.default_rng(seed))
        out["p_achievable"] = pa
        testable = not math.isnan(pa) and pa < crit["ref_p_max"]
    out["testable"] = bool(testable)
    if testable:
        out["nmi"], out["p"] = core.block_permutation_pvalue(lab[mask], r, blocks, crit["n_perm"],
                                                             np.random.default_rng(seed + 7))
    else:
        out["nmi"] = core.nmi(lab[mask], r)
    return out


def mutual_info(a: np.ndarray, b: np.ndarray) -> float:
    """相互情報量（nats・度数からそのまま求める。少ない度数では上に偏る）。"""
    c = core._contingency(np.asarray(a), np.asarray(b))
    n = c.sum()
    if n == 0:
        return math.nan
    pj = c / n
    pa, pb = pj.sum(axis=1), pj.sum(axis=0)
    nz = pj > 0
    return float((pj[nz] * np.log(pj[nz] / np.outer(pa, pb)[nz])).sum())


def detectable_runs(mi: float, max_len: int = 10_000) -> float:
    """作業 2 つが交互に来るとき、BIC のまとめで作業が見える長さの目安（作業 1 つあたりの連なりの数）。

    作業 1 つを分けて得る尤度は おおよそ L * mi、切り替えを表すコストは 乗り換え log(L) と滞在 約 1（nats）。
    L * mi >= log(L) + 1 を満たす最小の L を返す。BIC の罰と作業が 3 つ以上のときの乗り換えを入れていないので、
    楽観的な下限である（これより短い作業は見えない。これより長くても見えるとは限らない・判断 11・12）。
    合成の陽性（1.5〜3 時間）ではこの下限 9 に対し作業 1 つが 11.5 連なりで、v2 は作業を見つけられなかった。
    """
    if not mi or math.isnan(mi) or mi <= 0:
        return math.inf
    for L in range(1, max_len + 1):
        if L * mi >= math.log(L) + 1:
            return float(L)
    return math.inf


def within_day_pvalue(labels: np.ndarray, ref: np.ndarray, blocks: np.ndarray, days: np.ndarray, n_perm: int,
                      rng: np.random.Generator) -> float:
    """ブロックに付いた `ref` の値を、同じ日のブロックの間でだけ入れ替えた帰無分布に対する NMI の片側 p。"""
    obs = core.nmi(labels, ref)
    nb = int(blocks.max()) + 1
    val = np.empty(nb, dtype=object)
    bday = np.empty(nb, dtype=object)
    for b in range(nb):
        idx = np.flatnonzero(blocks == b)
        val[b] = ref[idx[0]]
        bday[b] = days[idx[0]]
    groups = [np.flatnonzero(bday == d) for d in sorted(set(bday.tolist()))]
    ge = 0
    for _ in range(n_perm):
        perm = val.copy()
        for g in groups:
            perm[g] = val[rng.permutation(g)]
        if core.nmi(labels, perm[blocks].astype(str)) >= obs - 1e-12:
            ge += 1
    return (1 + ge) / (1 + n_perm)


def premise(p: stage1.Person, cfg: dict, d_lab: list, d_blk: list, crit: dict, seed: int) -> dict:
    """主の問い: 作業の記録で区切った作業ごとに、様式の連なりの出方が違うか（判断 11）。

    単位は様式の連なり（`_sequences` と同じ作り方）。連なりの作業名は、連なりの最初の窓の記録の名前。
    ブロックは記録の行（同じ名前が続く行・`per_window_diary`）。無操作で列が切れても切らない（判断 12）。
    帰無分布はブロックに付いた作業名の入れ替え。届く p の下限も確かめる（1 段目の判断 14・15）。
    """
    seqs, _ = _sequences(p, cfg)
    styles, names, blocks, days = [], [], [], []
    for s in seqs:
        for o, mem in zip(s.obs, s.members):
            nm = d_lab[int(mem[0])]
            if nm is None:
                continue
            styles.append(int(o))
            names.append(nm)
            blocks.append(d_blk[int(mem[0])])
            days.append(datetime.fromtimestamp(int(p.win.start_ms[int(mem[0])]) / 1000, tz=TZ).date().isoformat())
    out = {"runs": len(styles), "values": {}, "blocks": 0, "testable": False, "nmi": math.nan, "p": math.nan,
           "p_achievable": math.nan, "mi_nats_per_run": math.nan, "detectable_runs_lower_bound": None,
           "median_task_runs": math.nan, "per_task_styles": {}, "p_within_day": math.nan}
    if not styles:
        return out
    styles_a, names_a, blocks_a = np.array(styles), np.array(names, dtype=object).astype(str), np.array(blocks)
    _, blocks_a = np.unique(blocks_a, return_inverse=True)
    vals, counts = np.unique(names_a, return_counts=True)
    out["values"] = {str(v): int(c) for v, c in zip(vals, counts)}
    out["blocks"] = int(blocks_a.max() + 1)
    out["per_task_styles"] = {str(v): np.bincount(styles_a[names_a == v], minlength=int(styles_a.max()) + 1).tolist()
                              for v in vals}
    out["median_task_runs"] = float(np.median(np.bincount(blocks_a)))
    mi = mutual_info(styles_a, names_a)
    out["mi_nats_per_run"] = mi
    dl = detectable_runs(mi)
    # inf（相互情報量が 0 か、上限の長さでも届かない）は JSON にできないので null にする（「届かない」の意味）。
    out["detectable_runs_lower_bound"] = None if math.isinf(dl) else dl
    testable = sum(c >= crit["premise_min_runs_per_value"] for c in counts) >= 2
    if testable:
        _, pa = core.block_permutation_pvalue(names_a, names_a, blocks_a, crit["n_perm"], np.random.default_rng(seed))
        out["p_achievable"] = pa
        testable = not math.isnan(pa) and pa < crit["ref_p_max"]
    out["testable"] = bool(testable)
    if testable:
        out["nmi"], out["p"] = core.block_permutation_pvalue(styles_a, names_a, blocks_a, crit["n_perm"],
                                                             np.random.default_rng(seed + 11))
        # 感度（記述・判断 16）: 日の中だけで入れ替える。様式と作業の両方に日ごとの流れがあると、全体の入れ替えの
        # p は小さく出うる（記録は無作為化されていない）。ブロックの日はブロックの最初の連なりの日。
        out["p_within_day"] = within_day_pvalue(styles_a, names_a, blocks_a, np.array(days), crit["n_perm"],
                                                np.random.default_rng(seed + 13))
    else:
        out["nmi"] = core.nmi(styles_a, names_a)
    if not out["testable"]:
        out["verdict"] = "undecidable"
    else:
        out["verdict"] = "differs" if out["p"] < crit["ref_p_max"] else "not_shown"
    return out


def identifier_estimate(lab: np.ndarray, diary_labels: list, diary_pcs: list) -> dict:
    """同じ作業の名前に入ったのに記録の作業名が違う窓の割合（判断 4）。PC が Mac か外かで分ける。

    作業の名前ごとに、記録の作業名の多数を「その名前の作業」とし、それと違う窓を「混ざった窓」と数える。
    Mac の上で混ざった窓はアプリの識別子で分かれうる。Mac の外の窓は識別子では分かれない。
    """
    rows = [(int(l), d, pc) for l, d, pc in zip(lab, diary_labels, diary_pcs) if l != hm.MISSING and d is not None]
    if not rows:
        return {"windows": 0}
    major: dict[int, str] = {}
    for l in {r[0] for r in rows}:
        names = [r[1] for r in rows if r[0] == l]
        major[l] = sorted(set(names), key=lambda n: (-names.count(n), n))[0]
    mixed = [r for r in rows if r[1] != major[r[0]]]
    on_mac = [r for r in mixed if r[2] == "Mac"]
    return {"windows": len(rows), "mixed": len(mixed), "mixed_on_mac": len(on_mac),
            "mixed_outside_mac": len(mixed) - len(on_mac),
            "mixed_frac": len(mixed) / len(rows), "mixed_on_mac_frac": len(on_mac) / len(rows)}


# ---------------------------------------------------------------------------
# 人ごとの判定
# ---------------------------------------------------------------------------

def evaluate_person(pid: str, files: list[Path], work: Path, cfg: dict, crit: dict, diary_path: Path | None,
                    commits_path: Path | None) -> dict:
    seed = cfg["seed"]
    p = stage1.load_person(pid, files, work)
    v2 = fit_v2(p, cfg, seed)
    lab = v2["labels"]
    m = len(lab)
    win = p.win
    durations = (win.end_ms - win.start_ms) / 1000.0
    names = hm.name_states(lab, durations)
    cfg1 = stage1.stage1_config()
    v1 = act_window.run(p.res.raw_labels, p.seams, v2["n_symbols"], cfg1, cfg, seed)

    # 循環の検査: 様式の写し（1 段目の平滑化の後の様式の名前と同じか）・状態の写し
    sm = p.res.labels
    smask = (lab != hm.MISSING) & (sm != IDLE)
    style_copy = core.ari(lab[smask], sm[smask]) if smask.sum() >= 2 else math.nan
    st = np.array([s if s is not None else -9 for s in p.state])

    diary = load_diary(diary_path, cfg)
    d_lab, d_pc, d_blk = per_window_diary(win, diary, cfg["diary_label_rule"], cfg["diary_entry_end"])
    m_lab, _, m_blk = per_window_diary(win, diary, "mac_only", cfg["diary_entry_end"])
    # 相対時刻のファイル由来の窓は、置き直した時刻が実時刻ではないので、実時刻で当てる照合に入れない（判断 16）。
    d_lab = [None if r else x for x, r in zip(d_lab, p.relative)]
    d_pc = [None if r else x for x, r in zip(d_pc, p.relative)]
    m_lab = [None if r else x for x, r in zip(m_lab, p.relative)]
    commits = load_json(commits_path) if commits_path else None
    c_lab = per_window_commits(win, commits, cfg["commit_half_window_s"])
    c_lab = [None if r else x for x, r in zip(c_lab, p.relative)]

    diary_cmp = compare(lab, d_lab, p.seams, crit, seed, d_blk)
    diary_cmp_v1 = compare(v1["labels"], d_lab, p.seams, crit, seed, d_blk)
    commit_cmp = compare(lab, c_lab, p.seams, crit, seed)
    decl_cmp = compare(lab, p.decl, p.seams, crit, seed)

    # 状態の写し: 作業の記録と同じ窓の上で、推定状態との NMI が作業の記録との NMI 以上なら落とす。
    d_arr = np.array([d if d is not None else "" for d in d_lab], dtype=object)
    common = (lab != hm.MISSING) & (d_arr != "") & (st != -9)
    state_nmi_common = core.nmi(lab[common], st[common]) if common.sum() >= 2 else math.nan
    diary_nmi_common = core.nmi(lab[common], d_arr[common].astype(str)) if common.sum() >= 2 else math.nan

    prem = premise(p, cfg, d_lab, d_blk, crit, seed)
    prem_mac = premise(p, cfg, m_lab, m_blk, crit, seed)
    stab = stability_ari(p, cfg, seed)

    failed: list[str] = []
    undecided: list[str] = []
    if math.isnan(stab):
        undecided.append("stability")
    elif stab < crit["stability_ari_min"]:
        failed.append("stability")
    if math.isnan(style_copy):
        undecided.append("style_copy")
    elif style_copy >= crit["style_copy_ari_max"]:
        failed.append("style_copy")
    if not diary_cmp["testable"]:
        undecided.append("diary")
    else:
        if diary_cmp["p"] >= crit["ref_p_max"]:
            failed.append("diary")
        if math.isnan(state_nmi_common):
            undecided.append("state_copy")
        elif state_nmi_common >= diary_nmi_common:
            failed.append("state_copy")
    verdict = "not_usable" if failed else ("undecidable" if undecided else "usable")

    return {
        "person": pid,
        "files": len(files),
        "windows": m,
        "observed_windows": int((lab != hm.MISSING).sum()),
        "relative_time_files": p.relative_files,
        "overlap_dropped_active_windows": p.overlap["dropped_active_windows"],
        "stage1_k": p.res.gmm_k,
        "k": v2["k"],
        "emission": v2["emis"],
        "names": {names[v]: float(durations[lab == v].sum()) for v in sorted(set(lab.tolist()))},
        "boundaries": len(boundaries(lab, win.start_ms)),
        "stability_ari": stab,
        "style_copy_ari": style_copy,
        "state_nmi_on_diary_windows": state_nmi_common,
        "diary_nmi_on_common_windows": diary_nmi_common,
        "diary": diary_cmp,
        "commits": commit_cmp,
        "declaration": decl_cmp,
        "v1": {"k": v1["k"], "task_windows": v1["task_windows"], "few_task_windows": v1["few_task_windows"],
               "diary": diary_cmp_v1,
               "ari_with_v2": core.ari(v1["labels"][lab != hm.MISSING], lab[lab != hm.MISSING])
               if (lab != hm.MISSING).sum() >= 2 else math.nan},
        "identifier_estimate": identifier_estimate(lab, d_lab, d_pc),
        "premise": prem,
        "premise_mac_only": prem_mac,
        "premise_verdict": prem.get("verdict", "undecidable"),
        "verdict": verdict,
        "failed": failed,
        "undecidable": undecided,
    }


# ---------------------------------------------------------------------------
# synth
# ---------------------------------------------------------------------------

def synth_scores(d: Path, work: Path, cfg: dict) -> dict:
    files = [Path(f) for f in load_json(d / "files.json")]
    truth = load_json(d / "truth.json")
    p = stage1.load_person("synth", files, work)
    v2 = fit_v2(p, cfg, cfg["seed"])
    lab = v2["labels"]
    win = p.win
    mids = (win.start_ms + win.end_ms) // 2
    blocks = truth["blocks"]
    true_task = np.array([next((b["task"] for b in blocks if b["start_ms"] <= t < b["end_ms"]), "") for t in mids],
                         dtype=object)
    obs = lab != hm.MISSING
    truth_bnd = [b["start_ms"] for b in blocks[1:]]
    tol = cfg["synth_boundary_tol_s"] * 1000
    _, recall, f1 = core.boundary_f1(boundaries(lab, win.start_ms), truth_bnd, tol)
    v1 = act_window.run(p.res.raw_labels, p.seams, v2["n_symbols"], stage1.stage1_config(), cfg, cfg["seed"])
    sm = p.res.labels
    smask = obs & (sm != IDLE)
    return {
        "stage1_k": p.res.gmm_k,
        "k": v2["k"],
        "emission": v2["emis"],
        "boundary_f1": f1,
        "boundary_recall": recall,
        "ari": core.ari(lab[obs], true_task[obs].astype(str)) if obs.any() else math.nan,
        "style_copy_ari": core.ari(lab[smask], sm[smask]) if smask.sum() >= 2 else math.nan,
        "v1": {"k": v1["k"],
               "ari": core.ari(v1["labels"][obs], true_task[obs].astype(str)) if obs.any() else math.nan,
               "boundary_f1": core.boundary_f1(boundaries(v1["labels"], win.start_ms), truth_bnd, tol)[2]},
    }


def cmd_synth(a: argparse.Namespace) -> int:
    cfg = load_config()
    crit = load_json(HERE / "criteria.json")["synthetic"]
    sc = synth_scores(a.dir, a.work, cfg)
    if a.criteria == "positive":
        ok = (sc["k"] >= crit["positive_min_k"] and sc["boundary_f1"] >= crit["boundary_f1_min"]
              and sc["ari"] >= crit["ari_min"])
    else:
        ok = sc["k"] <= crit["negative_max_k"]
    sc["criteria"] = a.criteria
    sc["replay"] = stage1.ev1.replay_label()
    sc["pass"] = bool(ok)
    print(dumps(sc))
    return 0 if ok else 3


def cmd_real(a: argparse.Namespace) -> int:
    cfg = load_config()
    crit = load_json(HERE / "criteria.json")["real"]
    # 合成のときは work/synth/<seed>/ を --work に渡すので、実験の work/ の配下であればよい（security-checker LOW）。
    if not a.work.resolve().is_relative_to((HERE / "work").resolve()):
        raise SystemExit("--work は実験の work/ の配下に置く（実データ由来の中間成果物を追跡対象の場所に書かない）")
    if not a.out.resolve().is_relative_to(a.work.resolve()):
        raise SystemExit("--out は --work の配下に置く（照合の結果を追跡対象の場所に書かない）")
    people = load_json(a.people)
    out = []
    for p in people:
        if not PERSON_ID_RE.fullmatch(str(p["id"])):
            raise SystemExit(f"id は英数字・_・- の 64 字以内にする: {p['id']!r}")
        r = evaluate_person(p["id"], [Path(f) for f in p["files"]], a.work, cfg, crit,
                            Path(p["diary"]) if p.get("diary") else None,
                            Path(p["commits"]) if p.get("commits") else None)
        out.append(r)
        print(f'{r["person"]}: premise={r["premise_verdict"]} v2={r["verdict"]} '
              f'(failed: {r["failed"] or "-"}; undecidable: {r["undecidable"] or "-"})')
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(dumps({"sharing": SHARING_MARKER, "replay": stage1.ev1.replay_label(), "people": out}) + "\n",
                     encoding="utf-8")
    if a.expect:
        want = load_json(a.expect)
        # {id: {"premise": ..., "v2": ...}}（書いた方だけを見る）
        got = {r["person"]: {"premise": r["premise_verdict"], "v2": r["verdict"]} for r in out}
        bad = {k: (v, got.get(k)) for k, v in want.items()
               if k not in got or any(got[k][f] != x for f, x in v.items())}
        if bad:
            print(f"NG: 期待した判定と違う: {bad}", file=sys.stderr)
            return 3
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("synth")
    s.add_argument("--dir", required=True, type=Path, help="gen_synth_task.py の --out-dir")
    s.add_argument("--criteria", required=True, choices=["positive", "negative"])
    s.add_argument("--work", required=True, type=Path)
    r = sub.add_parser("real")
    r.add_argument("--people", required=True, type=Path,
                   help="[{id, files:[...], diary?, commits?}] の JSON（実パスを含むのでコミットしない）")
    r.add_argument("--work", required=True, type=Path)
    r.add_argument("--out", required=True, type=Path)
    r.add_argument("--expect", type=Path, help="{id: {premise?, v2?}} の JSON。違えば終了コード 3（合成の照合の経路の確かめ用）")
    a = ap.parse_args()
    return cmd_synth(a) if a.cmd == "synth" else cmd_real(a)


if __name__ == "__main__":
    raise SystemExit(main())
