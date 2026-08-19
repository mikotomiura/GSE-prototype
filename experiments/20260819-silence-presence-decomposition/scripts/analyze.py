#!/usr/bin/env python
"""L3: 離散時間ハザードによる ablation。

## ⚠️★★★ なぜ「per-bin の時間依存 Brier」が主指標なのか（先読みの排除）

`presence_state(t)` は**時変**である。ギャップ開始時点で `CIF(H)` を予測しようとすると、
**将来の presence を知っている必要があり、情報の先読みになる。**

→ ★ 主指標は **person-period（10 秒ビン）ごとのハザード予測の Brier score** にする。
各ビンで使うのは「そのビンの開始時刻までに観測済みの情報」だけなので、
**先読みが構造的に起こらない**。これは
`personalization-and-online-learning.md §8.1` が名指しした「**時間依存 Brier score**」そのものであり、
同節の「⚠️ 単一の二値 C-index を主指標にしない」にも従う。

★ `CIF(H)` は **30 秒ランドマーク**（presence を 30 秒時点の値で固定）で別途出し、較正に使う。

## 比較（`preregistration.md §4.4`・[V83] の要求）

    基線(a) 多数派 / 周辺ハザード（共変量なし）
    基線(b) T0     = 時間区分 + 直前 30 秒の打鍵統計
    提案    T0 + presence

## 打ち切りの上下界（`§4.6`・G2 と同じ様式）

    下界 … セッション終了で切れたギャップを**独立打ち切り**として扱う
    上界 … 同を**再開しなかった**（競合イベント）として地平まで y=0 で延長する
"""

from __future__ import annotations

import argparse
import json

import numpy as np

TIME_PIECE_NAMES = ("p_30_120", "p_120_180", "p_180_inf")


def sigmoid(z):
    out = np.empty_like(z)
    pos = z >= 0
    out[pos] = 1.0 / (1.0 + np.exp(-z[pos]))
    ez = np.exp(z[~pos])
    out[~pos] = ez / (1.0 + ez)
    return out


def fit_logistic(X: np.ndarray, y: np.ndarray, iters: int = 60, diag: dict | None = None):
    """IRLS。★ **正則化を入れない**（`preregistration.md §4.2`）。

    共線性は `lstsq`（最小ノルム解）で吸収する。罰則を足すと事前登録に反する。
    """
    n, d = X.shape
    beta = np.zeros(d)
    last_delta = float("nan")
    last_rank = -1
    it = -1
    for it in range(iters):
        eta = X @ beta
        p = sigmoid(eta)
        w = np.clip(p * (1.0 - p), 1e-8, None)
        z = eta + (y - p) / w
        sw = np.sqrt(w)
        new, _res, last_rank, _sv = np.linalg.lstsq(X * sw[:, None], z * sw, rcond=None)
        if not np.all(np.isfinite(new)):
            if diag is not None:
                diag["converged"] = False
                diag["nonfinite"] = True
            break
        last_delta = np.max(np.abs(new - beta))
        if last_delta < 1e-9:
            beta = new
            break
        beta = new
    else:
        # ★ for が break せずに終わった = 反復上限で打ち切った
        if diag is not None:
            diag["converged"] = False
    if diag is not None:
        diag.setdefault("converged", True)
        diag["iters"] = it + 1
        diag["max_delta"] = float(last_delta)
        diag["beta_absmax"] = float(np.max(np.abs(beta))) if beta.size else 0.0
        diag["rank"] = int(last_rank)
        diag["n_cols"] = int(d)
    return beta


def build_rows(gaps: list[dict], cfg: dict, bound: str, admin_censor_ms=None) -> dict:
    """ギャップ列 -> person-period 行列。

    ビン k は絶対ギャップ時刻 `[gap_min + k*bin, gap_min + (k+1)*bin)` を表す。
    ★ リスク集合は `gap_min`（30 秒）から始まる = **遅延エントリ**。
      30 秒未満で終わったギャップはそもそもコホートに入らないので、
      ここから始めないと「30 秒生き延びた」という条件付けを二重に効かせてしまう。
    """
    bin_ms = int(cfg["bin_ms"])
    gap_min = int(cfg["gap_min_ms"])
    pieces = [int(v) for v in cfg["time_pieces_ms"]]  # [30000, 120000, 180000]
    horizon_max = int(cfg["horizon_secondary_ms"])
    if admin_censor_ms is not None:
        horizon_max = min(horizon_max, int(admin_censor_ms))

    feats, ys, pids, times, gidx = [], [], [], [], []

    for gi, g in enumerate(gaps):
        dur = int(g["duration_ms"])
        end_ms = dur
        administrative = False
        if admin_censor_ms is not None and dur > admin_censor_ms:
            end_ms = admin_censor_ms
            event = False
            administrative = True   # ★ 行政的打ち切り（装置介入の手前で切った）
        else:
            event = bool(g["event"])

        # ⚠️★★★ **上界の延長は「自然打ち切り」にのみ適用する**（code-reviewer HIGH）。
        #   事前登録 §4.6 は逐語で「**セッション終了で切れたギャップ**」に限定している。
        #   ★ 行政的打ち切りにも延長すると、「300 秒で再開した」という**観測と矛盾する**
        #   y=0 行を地平まで捏造することになる。
        if bound == "upper" and not event and not administrative:
            end_ms = max(end_ms, horizon_max)

        k = 0
        while True:
            t_lo = gap_min + k * bin_ms
            t_hi = t_lo + bin_ms
            if t_lo >= horizon_max:
                break
            if t_lo >= end_ms:
                break

            if event and t_lo < dur <= t_hi:
                y = 1.0
            else:
                y = 0.0
            # 下界: 打ち切りビンが部分観測なら捨てる
            if (not event) and t_hi > end_ms:
                break

            piece = [0.0, 0.0, 0.0]
            if t_lo < pieces[1]:
                piece[0] = 1.0
            elif t_lo < pieces[2]:
                piece[1] = 1.0
            else:
                piece[2] = 1.0

            suspect = 1.0 if (g["suspect_at_ms"] is not None and t_lo >= g["suspect_at_ms"]) else 0.0
            down = 1.0 if (g["down_at_ms"] is not None and t_lo >= g["down_at_ms"]) else 0.0

            feats.append(
                piece
                + [
                    float(g["t0_keys"]),
                    float(g["t0_bs_rate"]),
                    float(g["t0_iki_med_ms"]),
                    float(g["t0_burst_len"]),
                    float(g["t0_pause_count"]),
                    # ★ 欠測の指示変数（HIGH-7）。0 が「無限に速い打鍵」に化けるのを防ぐ。
                    float(g.get("t0_iki_missing", 0.0)),
                    float(g.get("t0_burst_missing", 0.0)),
                    suspect,
                    down,
                ]
            )
            ys.append(y)
            pids.append(g["pid"])
            times.append(t_lo)
            gidx.append(gi)

            if y == 1.0:
                break
            k += 1

    # ⚠️★★★ **`duration == gap_min` ちょうどのギャップは person-period 行を 1 本も生まない**
    #   （★ 両者一致の指摘: code-reviewer LOW + codex cross-review 中）。
    #   ★ リスク集合が 30 秒から始まる**遅延エントリ**なので、30 秒ちょうどのギャップは
    #   エントリ直後にイベントが起き、**露出がゼロ**である。→ 統計的にはこれが正しい。
    #   ⚠️ しかし L1（`n_gaps`）はそれを数えるので **L1 と L3 のコホートが 1 件ずれる**。
    # → ★ 凍結済みのコホート定義（`preregistration.md §2`「30 秒以上」）は**変えず**、
    #   **ずれを数えて報告する**（黙って落とさない）。
    contributing = len(set(gidx))
    zero_exposure = len(gaps) - contributing

    return {
        "n_gaps_in": len(gaps),
        "n_gaps_contributing_rows": contributing,
        "n_gaps_zero_exposure": zero_exposure,
        "X": np.asarray(feats, dtype=float) if feats else np.zeros((0, 12)),
        "y": np.asarray(ys, dtype=float),
        "pid": np.asarray(pids),
        "t": np.asarray(times, dtype=float),
        "gap": np.asarray(gidx, dtype=int),
    }


# 列の並び: 0-2 = 時間区分 / 3-9 = T0(+欠測指示) / 10-11 = presence
COL_TIME = [0, 1, 2]
COL_T0 = [3, 4, 5, 6, 7, 8, 9]   # ★ 末尾 2 本は欠測の指示変数（HIGH-7）
COL_PRES = [10, 11]


def design(X: np.ndarray, model: str) -> np.ndarray:
    """★ 切片は時間区分ダミー 3 本が担う（3 本で完全被覆なので別に立てない）。"""
    if model == "marginal":
        return np.ones((X.shape[0], 1))
    if model == "t0":
        cols = COL_TIME + COL_T0
    elif model == "t0_presence":
        cols = COL_TIME + COL_T0 + COL_PRES
    else:
        raise ValueError(model)
    return X[:, cols]


def standardize(tr: np.ndarray, te: np.ndarray):
    """★ 訓練 fold の平均・分散で中心化する。

    ⚠️ **これは「場当たりの尺度変換」ではない** —— 罰則なしロジスティック回帰の予測は
    説明変数のアフィン変換に対して**不変**であり、数値条件を整えるためだけの操作である。
    ダミー変数（0/1）は変換しない。
    """
    out_tr, out_te = tr.copy(), te.copy()
    for j in range(tr.shape[1]):
        col = tr[:, j]
        if np.all((col == 0) | (col == 1)):
            continue
        mu = col.mean()
        sd = col.std()
        if sd < 1e-12:
            sd = 1.0
        out_tr[:, j] = (col - mu) / sd
        out_te[:, j] = (te[:, j] - mu) / sd
    return out_tr, out_te


def brier(p: np.ndarray, y: np.ndarray) -> float:
    return float(np.mean((p - y) ** 2)) if len(y) else float("nan")


def loso(rows: dict, horizon_ms: int) -> dict:
    """leave-one-subject-out。★ 参加者ごとの値を潰さずに全部返す。"""
    pids = sorted(set(rows["pid"].tolist()))
    per_pid = {}
    for held in pids:
        te_mask = rows["pid"] == held
        tr_mask = ~te_mask
        if tr_mask.sum() == 0 or te_mask.sum() == 0:
            continue
        # ★ 評価は地平内のビンだけ
        ev_mask = te_mask & (rows["t"] < horizon_ms)
        if ev_mask.sum() == 0:
            continue

        res = {}
        diags = {}
        for model in ("marginal", "t0", "t0_presence"):
            Xtr = design(rows["X"][tr_mask], model)
            Xte = design(rows["X"][ev_mask], model)
            Xtr, Xte = standardize(Xtr, Xte)
            d0 = {}
            beta = fit_logistic(Xtr, rows["y"][tr_mask], diag=d0)
            p = sigmoid(Xte @ beta)
            res[model] = brier(p, rows["y"][ev_mask])
            diags[model] = d0
        res["fit_diagnostics"] = diags

        # ★ [V83] 逐語の「多数派分類器」= 常に多数派クラスを出す硬い基線
        maj = 1.0 if rows["y"][tr_mask].mean() > 0.5 else 0.0
        res["hard_majority"] = brier(
            np.full(int(ev_mask.sum()), maj), rows["y"][ev_mask]
        )
        res["n_bins"] = int(ev_mask.sum())
        res["event_rate"] = float(rows["y"][ev_mask].mean())
        per_pid[held] = res

    def agg(key):
        vals = [v[key] for v in per_pid.values() if np.isfinite(v[key])]
        return float(np.mean(vals)) if vals else float("nan")

    deltas_vs_t0 = {
        p: per_pid[p]["t0"] - per_pid[p]["t0_presence"] for p in per_pid
    }  # ★ 正 = presence を足して Brier が下がった = 改善
    deltas_vs_marginal = {p: per_pid[p]["marginal"] - per_pid[p]["t0_presence"] for p in per_pid}

    return {
        "per_participant": per_pid,
        "mean_brier": {
            k: agg(k) for k in ("marginal", "t0", "t0_presence", "hard_majority")
        },
        "delta_vs_t0": deltas_vs_t0,
        "delta_vs_t0_mean": float(np.mean(list(deltas_vs_t0.values()))) if deltas_vs_t0 else float("nan"),
        "delta_vs_t0_n_positive": int(sum(1 for v in deltas_vs_t0.values() if v > 0)),
        "delta_vs_marginal_mean": (
            float(np.mean(list(deltas_vs_marginal.values()))) if deltas_vs_marginal else float("nan")
        ),
        "n_participants": len(per_pid),
        # ⚠️★ 非収束・ランク落ちを黙って通さない（code-reviewer MEDIUM）
        "any_nonconverged": any(
            not d.get("converged", True)
            for v in per_pid.values()
            for d in v.get("fit_diagnostics", {}).values()
        ),
        "any_rank_deficient": any(
            d.get("rank", -1) >= 0 and d.get("rank", 0) < d.get("n_cols", 0)
            for v in per_pid.values()
            for d in v.get("fit_diagnostics", {}).values()
        ),
    }


def run_block(gaps, cfg, admin_censor_ms, horizons: dict) -> dict:
    out = {}
    for bound in ("lower", "upper"):
        rows = build_rows(gaps, cfg, bound, admin_censor_ms=admin_censor_ms)
        out[bound] = {
            "n_rows": int(rows["X"].shape[0]),
            "n_events": int(rows["y"].sum()),
            "n_gaps_in": rows["n_gaps_in"],
            "n_gaps_contributing_rows": rows["n_gaps_contributing_rows"],
            # ⚠️ 露出ゼロ（`duration == gap_min` ちょうど）= L1 と L3 のコホート差
            "n_gaps_zero_exposure": rows["n_gaps_zero_exposure"],
        }
        for hname, hms in horizons.items():
            out[bound][hname] = loso(rows, hms) if rows["X"].shape[0] else None
    return out


def judge(payload: dict, cfg: dict) -> dict:
    """★ `preregistration.md §6` の 3 条件を**機械判定**する。

    ⚠️ 手作業で読むと、都合のよい方を選べてしまう。→ 事前登録の文言をそのままコードにする。
    """
    def delta(block, bound, hname):
        b = block.get(bound, {}).get(hname)
        return b["delta_vs_t0_mean"] if b else None

    lo = delta(payload["main"], "lower", "H_primary_3min")
    up = delta(payload["main"], "upper", "H_primary_3min")
    sens_lo = delta(payload["sensitivity_admin_censor_120s"], "lower", "H_sens_120s")
    sens_up = delta(payload["sensitivity_admin_censor_120s"], "upper", "H_sens_120s")

    c1 = lo is not None and lo > 0                       # T0 より改善（主 H）
    c2 = (lo is not None and up is not None
          and (lo > 0) == (up > 0))                      # 上下界で符号一致
    c3 = (sens_lo is not None and sens_lo > 0
          and sens_up is not None and sens_up > 0)       # 120 秒副解析でも残る

    return {
        "criterion_1_beats_t0_at_primary_H": c1,
        "criterion_2_bounds_agree_in_sign": c2,
        "criterion_3_survives_admin_censor": c3,
        "information_found": bool(c1 and c2 and c3),
        "note": (
            "preregistration.md §6 の 3 条件を機械判定。"
            "1 つでも欠けたら『情報があった』と書かない。"
        ),
        "deltas": {"main_lower": lo, "main_upper": up,
                   "sens_lower": sens_lo, "sens_upper": sens_up},
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--extract", required=True)
    ap.add_argument("--config", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    with open(args.extract, encoding="utf-8") as fh:
        data = json.load(fh)
    with open(args.config, encoding="utf-8") as fh:
        cfg = json.load(fh)

    all_gaps = data["gaps"]
    # ⚠️★★★ **計器の無いギャップを L3 に投入しない**（code-reviewer HIGH）。
    #   suspect/down が None → 共変量 0 = **「presence が無かった」**という嘘になる。
    #   ★ Stop は全滅時しか効かないので、**計器あり/なしが混在するコホート**
    #   （G1 + 旧ログ）では修正前と同じ嘘が復活する。→ 部分集合に絞る。
    gaps = [g for g in all_gaps if g.get("presence_observable")]
    n_dropped_unobservable = len(all_gaps) - len(gaps)
    n_suspect = sum(1 for g in gaps if g["suspect_at_ms"] is not None)

    payload = {
        "schema": "silence-presence-analyze/v1",
        "hmm_version": cfg.get("hmm_version"),
        "input_manifest": data["input_manifest"],
        "n_gaps": len(all_gaps),
        "n_gaps_l3_eligible": len(gaps),
        "n_gaps_with_suspect": n_suspect,
        "n_gaps_rehook": sum(1 for g in gaps if g["rehook"]),
        "stop": None,
    }

    # --- Stop 条件（`preregistration.md §7`・実データを見る前に凍結済み） -------
    n_observable = len(gaps)
    payload["n_gaps_presence_observable"] = n_observable
    payload["n_gaps_excluded_unobservable"] = n_dropped_unobservable

    # ★ 分岐は「計器が無い」を**最初に**見る。⚠️ 順序を誤ると
    #   「ギャップが少ない」で先に止まり、原因が計器不在だと分からなくなる。
    if n_observable == 0:
        # ⚠️★★★ **「presence が観測されなかった」と「計器が無い」は別物である。**
        #   後者を前者として報告すると、「入力皆無だった」という**存在しない所見**を作る。
        payload["stop"] = (
            "⚠️ 計器が無い: 対象ログに `hook_health` 行が 1 行も存在しない"
            f"（presence が観測可能なギャップ = {n_observable} / {len(all_gaps)}）。"
            "★ これは『presence が無かった』ではなく『測る器がまだ無かった』である。"
            "→ L3 を出さない。L1/L2 の沈黙時間は **unknown** として集計される。"
        )
        payload["stop_kind"] = "instrument_absent"
    elif n_observable < int(cfg["stop_min_gaps"]):
        payload["stop"] = (
            f"計器のあるギャップが {n_observable} 個 < {cfg['stop_min_gaps']}。"
            "L3 を出さず「測れなかった」を結論にする。"
        )
        payload["stop_kind"] = "too_few_gaps"
    elif n_suspect < int(cfg["stop_min_suspect_gaps"]):
        payload["stop"] = (
            f"Suspect 行を持つギャップが {n_suspect} 個 < {cfg['stop_min_suspect_gaps']}。"
            "L3 を出さず L1/L2 の記述のみとする。"
        )
        payload["stop_kind"] = "too_few_suspect"

    if payload["stop"] is None:
        horizons = {
            "H_primary_3min": int(cfg["horizon_primary_ms"]),
            "H_secondary_10min": int(cfg["horizon_secondary_ms"]),
        }
        payload["main"] = run_block(gaps, cfg, None, horizons)
        # ★ 副解析（必須）: 装置が介入する 120 秒で行政的打ち切り
        payload["sensitivity_admin_censor_120s"] = run_block(
            gaps, cfg, int(cfg["admin_censor_ms"]), {"H_sens_120s": int(cfg["admin_censor_ms"])}
        )
        payload["verdict"] = judge(payload, cfg)

    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2, sort_keys=True, default=float)
        fh.write("\n")

    if payload["stop"]:
        print(f"STOP: {payload['stop']}")
    else:
        m = payload["main"]["lower"]["H_primary_3min"]
        print(
            f"L3 (下界・H=3min): brier marginal={m['mean_brier']['marginal']:.5f} "
            f"t0={m['mean_brier']['t0']:.5f} t0+presence={m['mean_brier']['t0_presence']:.5f} "
            f"Δ(t0 - t0+presence)={m['delta_vs_t0_mean']:+.5f} "
            f"positive={m['delta_vs_t0_n_positive']}/{m['n_participants']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
