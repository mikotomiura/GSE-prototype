"""判定（auto-context-segmentation）。

サブコマンド:
    synth  合成の記録で、境界とまとまりを基準どおりに拾えるかを見る（終了コードで返す）。
    real   実データ（人ごとの複数ファイル）で、人ごとの判定（使える／使えない／判定できない）を出す。

基準はすべて `criteria.json`、解析の引数は `config.json` から読む。
`criteria.json` は実データを処理するより前のコミットに入れる（requirement.md の受け入れ条件）。

NDJSON から直接読むのは `session_meta`（task_kind と時刻）・`activity_label`（区分と時刻）・
`feat`（時刻と p_flow / p_inc / p_stuck）の 3 行種だけで、打鍵の行は読まない。打鍵の量は `--features` の封筒から読む。
記録・封筒・結果は外部（Codex を含む）へ送らない。
"""

from __future__ import annotations

import argparse
import json
import math
import os
import subprocess
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import acs_core as core  # noqa: E402

REPO = HERE.parent.parent


def load_json(name: str) -> dict:
    return json.loads((HERE / name).read_text(encoding="utf-8"))


def load_config() -> dict:
    """`config.json` に、種を `SEED` から足して返す（種の置き場は `SEED` の 1 か所だけ）。"""
    cfg = load_json("config.json")
    if "seed" in cfg:
        raise SystemExit("config.json に seed を置かない（SEED の 1 か所から読む）")
    cfg["seed"] = int((HERE / "SEED").read_text(encoding="utf-8").strip())
    return cfg


# 実データ由来の出力に付ける共有禁止の印（`scripts/check_no_feature_output.sh` の is_marker が拾う形）。
SHARING_MARKER = {
    "gse_dataset": "prohibited",
    "reason": "experiments/20261121-auto-context-segmentation の実データ由来の中間成果物（区間の一覧を含み、abs_segments.json は絶対時刻を含む）",
    "rule": "docs/glossary.md 特徴行",
}

def _jsonable(x):
    """nan を null にする（NaN は JSON ではなく、読み手（jq の版など）によって読めない）。"""
    if isinstance(x, float) and math.isnan(x):
        return None
    if isinstance(x, dict):
        return {k: _jsonable(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_jsonable(v) for v in x]
    return x


def dumps(x) -> str:
    return json.dumps(_jsonable(x), ensure_ascii=False, indent=2, allow_nan=False)


# 提出物の匿名化（`anonymize.rs`）は時刻を「ファイルの開始からの相対 ms」に直す。相対のファイルは
# 名前の記録の時刻の順に並べ、前のファイルの終わりから RELATIVE_GAP_MS 空けて置き直す（decisions.md 判断 18）。
RELATIVE_EPOCH_LIMIT_MS = 10**12  # これより小さい時刻は相対（絶対 epoch ms なら 2001 年以降は 10^12 を超える）
RELATIVE_GAP_MS = 3_600_000
STAMP_RE = __import__("re").compile(r"gse_o1_(\d{8}_\d{6})")


def file_order_key(path: Path) -> tuple:
    m = STAMP_RE.search(path.name)
    return (m.group(1) if m else "", path.name)


def shift_windows(w: core.Windows, offset: int) -> core.Windows:
    return core.Windows(w.start_ms + offset, w.end_ms + offset, w.X, w.idle, w.unknown_mask())


def shift_side(side: dict, offset: int) -> dict:
    return {"decl": [(t + offset, k) for t, k in side["decl"]],
            # activity_label の recall_window_* は匿名化で相対化されず絶対時刻のまま残っている
            # （ABSOLUTE_TIME_FIELDS に無い・decisions.md 判断 18）。相対のファイルでは時刻が揃わないので使わない。
            "labels": [],
            "feats": [(t + offset, s) for t, s in side["feats"]]}


PERSON_ID_RE = __import__("re").compile(r"[A-Za-z0-9_-]{1,64}")  # fullmatch で使う（$ は末尾の改行を通す）
TYPE_RE = __import__("re").compile(r'"type"\s*:\s*"(session_meta|activity_label|feat)"')


def replay_bin() -> list[str]:
    exe = os.environ.get("GSE_REPLAY")
    if exe:
        return [exe]
    return ["cargo", "run", "--quiet", "--manifest-path", str(REPO / "src-tauri" / "Cargo.toml"),
            "--bin", "gse-replay", "--"]


def replay_label() -> list[str]:
    """出力に刻む gse-replay の名前。フルパスはユーザー名を含むので、実行ファイルの名前だけにする。"""
    return [Path(x).name if os.sep in x else x for x in replay_bin()]


def run_features(ndjson: Path, out_json: Path) -> None:
    out_json.parent.mkdir(parents=True, exist_ok=True)
    with out_json.open("w", encoding="utf-8") as fh:
        subprocess.run([*replay_bin(), str(ndjson), "--features"], stdout=fh, check=True)


def read_side(ndjson: Path) -> dict:
    """打鍵以外の 3 行種だけを読む（type を見てから、要るフィールドだけを取り出す）。"""
    decl: list[tuple[int, str | None]] = []
    labels: list[tuple[int, int, str]] = []
    feats: list[tuple[int, int]] = []
    unreadable = 0
    with ndjson.open(encoding="utf-8") as fh:
        for line in fh:
            # 打鍵の行は json.loads しない。3 行種の印がある行だけを読む。
            if not TYPE_RE.search(line):
                continue
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                unreadable += 1
                continue
            ty = d.get("type")
            if ty == "session_meta":
                decl.append((int(d.get("ts", 0)), d.get("task_kind")))
            elif ty == "activity_label" and d.get("answered") and not d.get("debug"):
                a0, b0, cat = d.get("recall_window_start_ms"), d.get("recall_window_end_ms"), d.get("category")
                if isinstance(a0, int) and isinstance(b0, int) and cat is not None:
                    labels.append((a0, b0, str(cat)))
                else:
                    unreadable += 1
            elif ty == "feat":
                ps = [d.get("p_flow"), d.get("p_inc"), d.get("p_stuck")]
                if all(isinstance(x, (int, float)) for x in ps):
                    feats.append((int(d["t"]), int(np.argmax(ps))))
    if unreadable:
        print(f"read_side: {unreadable} 行を JSON として読めず飛ばした", file=sys.stderr)
    return {"decl": sorted(decl), "labels": labels, "feats": sorted(feats)}


def per_window_decl(win: core.Windows, decl: list[tuple[int, str | None]]) -> list[str | None]:
    out: list[str | None] = []
    for s in win.start_ms:
        cur = None
        for ts, kind in decl:
            if ts <= s:
                cur = kind
        out.append(cur)
    return out


def per_window_state(win: core.Windows, feats: list[tuple[int, int]]) -> list[int | None]:
    ts = np.array([f[0] for f in feats], dtype=np.int64)
    st = np.array([f[1] for f in feats], dtype=int)
    out: list[int | None] = []
    for s, e in zip(win.start_ms, win.end_ms):
        sel = st[(ts >= s) & (ts < e)]
        out.append(int(np.bincount(sel).argmax()) if sel.size else None)
    return out


def per_window_activity(win: core.Windows, labels: list[tuple[int, int, str]]) -> list[str | None]:
    out: list[str | None] = []
    for s, e in zip(win.start_ms, win.end_ms):
        hit = [c for (a, b, c) in labels if a < e and s < b]
        out.append(hit[-1] if hit else None)
    return out


# ---------------------------------------------------------------------------
# synth
# ---------------------------------------------------------------------------

def synth_scores(ndjson: Path, truth_path: Path, work: Path, cfg: dict, seed: int) -> dict:
    env = work / (ndjson.stem + ".features.json")
    run_features(ndjson, env)
    win = core.make_windows(core.load_envelope(env), cfg["window_s"])
    res = core.segment_person(win, cfg, seed)
    truth = json.loads(truth_path.read_text(encoding="utf-8"))
    segs = truth["segments"]
    mids = (win.start_ms + win.end_ms) // 2
    true_ctx = []
    for m in mids:
        c = next((s["context"] for s in segs if s["start_ms"] <= m < s["end_ms"]), "idle")
        true_ctx.append(c)
    true_ctx = np.array(true_ctx)
    active = (res.labels != core.IDLE) & (true_ctx != "idle")
    truth_bnd = [s["start_ms"] for s in segs[1:]]
    _, recall, f1 = core.boundary_f1(res.boundaries_ms, truth_bnd, cfg["window_s"] * 1000)
    kinds = sorted({int(v) for v in res.labels if v != core.IDLE})
    return {
        "file": ndjson.name,
        "k": res.gmm_k,
        "label_kinds_after_smoothing": len(kinds),
        "boundary_f1": f1,
        "boundary_recall": recall,
        "ari": core.ari(res.labels[active], true_ctx[active]) if active.any() else math.nan,
        "absorbed_runs": res.absorbed_runs,
        "kept_features": res.kept_features,
    }


def cmd_synth(a: argparse.Namespace) -> int:
    cfg, crit = load_config(), load_json("criteria.json")["synthetic"]
    sc = synth_scores(a.ndjson, a.truth, a.work, cfg, cfg["seed"])
    if a.criteria == "positive":
        # 境界の F1 と ARI だけだと、文脈が 1 種類の記録でも通る（無操作の強制の境界は必ず当たり、
        # 1 種類どうしの ARI は 1）。切り替えを見つけたことを種類の数で要求する（判断 12）。
        ok = (sc["boundary_f1"] >= crit["boundary_f1_min"] and sc["ari"] >= crit["ari_min"]
              and sc["label_kinds_after_smoothing"] >= crit["positive_min_label_kinds"])
    else:
        ok = sc["label_kinds_after_smoothing"] <= crit["negative_max_label_kinds"]
    sc["criteria"] = a.criteria
    sc["replay"] = replay_label()
    sc["pass"] = bool(ok)
    print(dumps(sc))
    # 不合格は 3（例外による終了の 1 と区別する。run.sh は 3 と pass:false の両方を見る・cross-review HIGH）。
    return 0 if ok else 3


# ---------------------------------------------------------------------------
# real
# ---------------------------------------------------------------------------

def _fit_transform(X: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    med = np.nanmedian(X, axis=0)
    Xf = np.where(np.isnan(X), med, X)
    mu, sd = Xf.mean(axis=0), Xf.std(axis=0)
    return med, mu, sd


def _apply(X: np.ndarray, med: np.ndarray, mu: np.ndarray, sd: np.ndarray, keep: np.ndarray) -> np.ndarray:
    Xf = np.where(np.isnan(X), med, X)
    return (Xf[:, keep] - mu[keep]) / sd[keep]


def stability_ari(win: core.Windows, cfg: dict, seed: int) -> float:
    """前半で学んだまとめを後半に当てはめ、後半だけで学んだまとめと比べた ARI（無操作の窓は除く）。

    比べるのは平滑化の前の混合ガウスのまとまりである（平滑化はまとまりの再現性とは別の段なので入れない）。
    列は、前半・後半のどちらでも中央値が有限で分散が 0 でない列だけを使う（本体の `standardize` より
    少し厳しい: 片方の半分で値が一定の列は、もう片方に当てはめられないため）。
    """
    X = win.X[~win.idle]
    n = X.shape[0]
    if n < 2 * cfg["stability_min_windows_per_half"]:
        return math.nan
    first, second = X[: n // 2], X[n // 2:]
    out = []
    for part in (first, second):
        med, mu, sd = _fit_transform(part)
        out.append((med, mu, sd))
    keep = np.array([j for j in range(X.shape[1])
                     if all(np.isfinite(o[0][j]) and o[2][j] > 1e-9 for o in out)], dtype=int)
    if keep.size == 0:
        return math.nan
    g1 = core.select_gmm(_apply(first, *out[0], keep), cfg["k_max"], seed, cfg["n_init"], cfg["var_floor"])
    g2 = core.select_gmm(_apply(second, *out[1], keep), cfg["k_max"], seed + 1, cfg["n_init"], cfg["var_floor"])
    l1, _ = core.predict(_apply(second, *out[0], keep), g1)
    l2, _ = core.predict(_apply(second, *out[1], keep), g2)
    return core.ari(l1, l2)


def quantity_only_ari(win: core.Windows, res: core.Result, cfg: dict, seed: int,
                      axes: str = "quantity") -> float:
    """一部の軸だけでまとめ直したものと、全部の軸でのまとまり（平滑化前）の ARI。

    `axes="quantity"` は量の軸（打鍵の率・ポインタの割合）だけ、`axes="non_quantity"` はそれ以外の軸だけ。
    """
    names = (core.QUANTITY_FEATURES if axes == "quantity"
             else [f for f in core.FEATURE_NAMES if f not in core.QUANTITY_FEATURES])
    cols = [core.FEATURE_NAMES.index(f) for f in names]
    active = ~win.idle
    Xs, keep = core.standardize(win.X[active][:, cols])
    if Xs.shape[1] == 0 or Xs.shape[0] < 2:
        return math.nan
    g = core.select_gmm(Xs, cfg["k_max"], seed, cfg["n_init"], cfg["var_floor"])
    lab, _ = core.predict(Xs, g)
    return core.ari(lab, res.raw_labels[active])


def evaluate_person(pid: str, files: list[Path], work: Path, cfg: dict, crit: dict) -> dict:
    seed = cfg["seed"]
    parts = []
    relative_files = 0
    cursor = None  # 相対のファイルを置く位置（前のファイルの終わり）
    for f in sorted(files, key=file_order_key):
        env = work / pid / (f.stem + ".features.json")
        try:
            run_features(f, env)
            w = core.make_windows(core.load_envelope(env), cfg["window_s"])
        finally:
            # 封筒は入力の約 4 倍の大きさになる（1.7 GB の入力で約 7 GB）。窓に集めたら消す
            # （ディスクを守るため・共有しない中間成果物を残さないため）。
            env.unlink(missing_ok=True)
        side = read_side(f)
        if len(w.start_ms) and int(w.start_ms[0]) < RELATIVE_EPOCH_LIMIT_MS:
            relative_files += 1
            offset = (cursor + RELATIVE_GAP_MS if cursor is not None else RELATIVE_EPOCH_LIMIT_MS) - int(w.start_ms[0])
            w, side = shift_windows(w, offset), shift_side(side, offset)
        if len(w.end_ms):
            cursor = int(w.end_ms[-1]) if cursor is None else max(cursor, int(w.end_ms[-1]))
        parts.append((w, per_window_decl(w, side["decl"]), per_window_state(w, side["feats"]),
                      per_window_activity(w, side["labels"])))
    # 窓ごとの付帯情報は窓の開始時刻で引き直す（concat_windows が並べ替えと落としを行うため）。
    side_by_start: dict[int, tuple] = {}
    for w, d, st, ac in parts:
        for i, s0 in enumerate(w.start_ms):
            side_by_start[int(s0)] = (d[i], st[i], ac[i])
    win, seams, overlap = core.concat_windows([w for w, *_ in parts])
    decl_all = [side_by_start[int(s0)][0] for s0 in win.start_ms]
    state_all = [side_by_start[int(s0)][1] for s0 in win.start_ms]
    act_all = [side_by_start[int(s0)][2] for s0 in win.start_ms]
    res = core.segment_person(win, cfg, seed, seams)
    lab = res.labels
    active = lab != core.IDLE

    # 推定状態（循環の検査）
    st = np.array([v if v is not None else -9 for v in state_all])
    has_state = st != -9

    # 宣言との照合。判定には平滑化の前のまとまり（raw_labels）を使う。平滑化の壁にはファイルの継ぎ目が
    # 入っており、O1 では継ぎ目 = 宣言の切り替えなので、平滑化の後のラベルは帰無分布より有利になりうる
    # （decisions.md 判断 13）。平滑化の後の NMI は記述として並べる。
    raw = res.raw_labels
    decl = np.array([d if d is not None else "" for d in decl_all], dtype=object)
    mask = active & (decl != "")
    vals, counts = np.unique(decl[mask].astype(str), return_counts=True) if mask.any() else ([], [])
    # ブロック = ファイルの中で同じ宣言が続く区間（ファイルの継ぎ目か宣言の変化で新しいブロック）。
    block_all = np.zeros(len(decl), dtype=int)
    for i in range(1, len(decl)):
        block_all[i] = block_all[i - 1] + (1 if (seams[i] or decl[i] != decl[i - 1]) else 0)
    decl_testable = sum(c >= crit["decl_min_windows_per_value"] for c in counts) >= 2
    rng = np.random.default_rng(seed)
    decl_nmi = decl_p = decl_nmi_smoothed = state_nmi_common = decl_nmi_common = math.nan
    decl_p_achievable = math.nan
    if decl_testable:
        # 宣言を宣言自身と照合したときの p（一致が完全でも届く下限）。区切りが少ないと巡回でずらしても
        # 同じ並びが出て、完全に一致していても有意にならない。届かない人は判定できない（判断 14）。
        _, decl_p_achievable = core.block_permutation_pvalue(
            decl[mask].astype(str), decl[mask].astype(str), block_all[mask], crit["n_perm"],
            np.random.default_rng(seed))
        decl_testable = not math.isnan(decl_p_achievable) and decl_p_achievable < crit["decl_p_max"]
    if decl_testable:
        decl_nmi, decl_p = core.block_permutation_pvalue(
            raw[mask], decl[mask].astype(str), block_all[mask], crit["n_perm"], rng)
        decl_nmi_smoothed = core.nmi(lab[mask], decl[mask].astype(str))
        common = mask & has_state
        if common.sum() >= 2:
            # 状態との比較は宣言と同じ窓の上で（NMI は部分集合と値の数に依存する）。
            state_nmi_common = core.nmi(raw[common], st[common])
            decl_nmi_common = core.nmi(raw[common], decl[common].astype(str))
    smask = active & has_state
    state_nmi = core.nmi(raw[smask], st[smask]) if smask.any() else math.nan

    # 循環の検査（量の軸）・本人の中での再現性
    q_ari = quantity_only_ari(win, res, cfg, seed, "quantity")
    nq_ari = quantity_only_ari(win, res, cfg, seed, "non_quantity")
    stab = stability_ari(win, cfg, seed)

    # activity_label（記述のみ・判定には使わない）
    act = np.array([a if a is not None else "" for a in act_all], dtype=object)
    amask = active & (act != "")
    act_nmi = core.nmi(raw[amask], act[amask].astype(str)) if amask.sum() >= 2 else math.nan

    # 判定: どれか 1 つでも基準に落ちたら「使えない」、落ちたものが無く測れないものがあれば
    # 「判定できない」、全部測れて全部通ったら「使える」（decisions.md 判断 13）。
    failed: list[str] = []
    undecided: list[str] = []
    if math.isnan(stab):
        undecided.append("stability")
    elif stab < crit["stability_ari_min"]:
        failed.append("stability")
    # 量だけで再現でき、かつ量以外の軸だけでは再現できないときだけ「打鍵の多さで割れただけ」（判断 14）。
    if math.isnan(q_ari):
        undecided.append("quantity_only")
    elif (q_ari >= crit["quantity_only_ari_max"]
          and (math.isnan(nq_ari) or nq_ari < crit["non_quantity_ari_min"])):
        failed.append("quantity_only")
    if not decl_testable or math.isnan(decl_p):
        undecided.append("declaration")
    else:
        if decl_p >= crit["decl_p_max"]:
            failed.append("declaration")
        # 状態の写しの検査も必須。推定状態が無い（feat 行の p_* が読めない）なら判定できない（cross-review・判断 22）。
        if math.isnan(state_nmi_common):
            undecided.append("state_copy")
        elif state_nmi_common >= decl_nmi_common:
            failed.append("state_copy")
    verdict = "not_usable" if failed else ("undecidable" if undecided else "usable")

    durations = (win.end_ms - win.start_ms) / 1000.0
    return {
        "person": pid,
        "files": len(files),
        "windows": int(len(lab)),
        "relative_time_files": relative_files,
        "overlap_dropped_windows": overlap["dropped_windows"],
        "overlap_dropped_active_windows": overlap["dropped_active_windows"],
        "active_windows": int(active.sum()),
        "k": res.gmm_k,
        "names": {res.names[v]: float(durations[lab == v].sum()) for v in sorted(set(lab.tolist()))},
        "boundaries": len(res.boundaries_ms),
        "absorbed_runs": res.absorbed_runs,
        "kept_features": res.kept_features,
        "stability_ari": stab,
        "quantity_only_ari": q_ari,
        "non_quantity_ari": nq_ari,
        "state_nmi": state_nmi,
        "state_nmi_on_declared_windows": state_nmi_common,
        "decl_testable": bool(decl_testable),
        "decl_values": {str(v): int(c) for v, c in zip(vals, counts)},
        "decl_blocks": int(len(np.unique(block_all[mask]))) if mask.any() else 0,
        "decl_nmi": decl_nmi,
        "decl_nmi_after_smoothing": decl_nmi_smoothed,
        "decl_p": decl_p,
        "decl_p_achievable": decl_p_achievable,
        "activity_label_nmi": act_nmi,
        "verdict": verdict,
        "failed": failed,
        "undecidable": undecided,
        # 区間の一覧。時刻はその人の最初の窓からの相対 ms にする（絶対時刻を出さない・security-checker MEDIUM）。
        "_abs_segments": [
            {"start_ms": int(win.start_ms[i]), "end_ms": int(win.end_ms[j - 1]), "name": res.names[int(lab[i])],
             "mean": {n: (None if np.isnan(v) else round(float(v), 2)) for n, v in
                      zip(core.FEATURE_NAMES, np.nanmean(win.X[i:j], axis=0))} if lab[i] != core.IDLE else None}
            for i, j in _runs_of(lab, seams)
        ] if pid in ABS_SEGMENTS_FOR else None,
        "_segments": [
            {"start_rel_ms": int(win.start_ms[i] - win.start_ms[0]), "name": res.names[int(lab[i])]}
            for i in range(len(lab)) if i == 0 or lab[i] != lab[i - 1] or seams[i]
        ],
    }


# 絶対時刻つきの区間の一覧を出す人（研究者本人の振り返り用・decisions.md 判断 19）。cmd_real が --abs-segments-for で埋める。
ABS_SEGMENTS_FOR: set[str] = set()


def _runs_of(lab: np.ndarray, seams: np.ndarray) -> list[tuple[int, int]]:
    out, s0 = [], 0
    for i in range(1, len(lab) + 1):
        if i == len(lab) or lab[i] != lab[s0] or seams[i]:
            out.append((s0, i))
            s0 = i
    return out


def cmd_real(a: argparse.Namespace) -> int:
    ABS_SEGMENTS_FOR.update(a.abs_segments_for)
    if a.abs_segments_for and not a.out.resolve().is_relative_to(a.work.resolve()):
        raise SystemExit("--abs-segments-for を使うときは --out を --work の配下に置く（絶対時刻を追跡対象の場所に書かない）")
    cfg, crit = load_config(), load_json("criteria.json")["real"]
    people = json.loads(a.people.read_text(encoding="utf-8"))
    unknown = sorted(set(a.abs_segments_for) - {str(p["id"]) for p in people})
    if unknown:
        raise SystemExit(f"--abs-segments-for に人の一覧に無い id がある: {unknown}")
    out = []
    for p in people:
        if not PERSON_ID_RE.fullmatch(str(p["id"])):
            raise SystemExit(f"id は英数字・_・- の 64 字以内にする（パスに使うため）: {p['id']!r}")
        files = sorted(Path(f) for f in p["files"])
        try:
            r = evaluate_person(p["id"], files, a.work, cfg, crit)
        except ValueError as e:
            # 窓の重なりが落としきれない（3 本以上の連鎖など）。全員を止めず、その人を判定できないにする。
            print(f"{p['id']}: {e}", file=sys.stderr)
            r = {"person": p["id"], "files": len(files), "verdict": "undecidable", "failed": [],
                 "undecidable": ["windows_overlap"], "relative_time_files": 0, "_abs_segments": None}
        abs_segments = r.pop("_abs_segments")
        if abs_segments is not None:
            if r["relative_time_files"]:
                # 相対時刻のファイル（O1 の提出物）を置き直した時刻は実時刻ではない。振り返りに使えないので出さない。
                raise SystemExit(f"{p['id']}: 相対時刻のファイルが {r['relative_time_files']} 本あるので、絶対時刻の一覧は出さない")
            ap = a.work / str(p["id"]) / "abs_segments.json"
            ap.parent.mkdir(parents=True, exist_ok=True)
            ap.write_text(dumps({"sharing": SHARING_MARKER, "person": p["id"], "segments": abs_segments}) + "\n",
                          encoding="utf-8")
        out.append(r)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    doc = {"sharing": SHARING_MARKER, "replay": replay_label(), "people": out}
    a.out.write_text(dumps(doc) + "\n", encoding="utf-8")
    for r in out:
        print(f'{r["person"]}: {r["verdict"]} (failed: {r["failed"] or "-"}; undecidable: {r["undecidable"] or "-"})')
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("synth")
    s.add_argument("--ndjson", required=True, type=Path)
    s.add_argument("--truth", required=True, type=Path)
    s.add_argument("--criteria", required=True, choices=["positive", "negative"])
    s.add_argument("--work", required=True, type=Path)
    r = sub.add_parser("real")
    r.add_argument("--people", required=True, type=Path,
                   help="[{id, files:[...]}] の JSON（実ファイルのパスを含むのでコミットしない）")
    r.add_argument("--work", required=True, type=Path)
    r.add_argument("--out", required=True, type=Path)
    r.add_argument("--abs-segments-for", nargs="*", default=[],
                   help="絶対時刻つきの区間の一覧を出す id（研究者本人の振り返り用。出力は work/ に置きコミットしない）")
    a = ap.parse_args()
    return cmd_synth(a) if a.cmd == "synth" else cmd_real(a)


if __name__ == "__main__":
    raise SystemExit(main())
