#!/usr/bin/env python3
"""Step 2 — 表現層の平滑化（時定数 >= 60 秒）。依存は **標準ライブラリのみ**。

なぜ要るか（`media-expression-spec.md` §1.2–§1.3 / D21）:

    1Hz の離散サンプルを、そのまま音量 / 密度 / 帯域幅に当てる
          -> 毎秒、値が階段状に飛ぶ
          -> その段差が振幅のオンセットになる
          -> ★ オンセットは聴覚ストリームを分節する [P64] = ISE の条件そのもの

★★ 本モジュールが数値で固定するのは 2 点である（`spec` §1.3「耳で判断せず数値で固定する」）:

  (1) 時定数 tau >= 60 s  -> 状態の波を **0.001-0.02 Hz** に置く
      = 禁止帯（4 Hz 付近が最悪・0.5-20 Hz / 15-70 Hz）から **2-3 桁下**。
      ★ 書き方は「緩慢だから安全」ではなく **「禁止帯から離れているから安全」**。
  (2) ★ 1Hz の**階段そのもの**を消す
      -> 零次ホールド（ZOH）の階段は、**1 Hz の整数倍の「両脇」に側帯波を作る**。
         信号成分 f_sig に対して **k*1Hz +- f_sig** に線が立つ。
         つまり **4 Hz のすぐ隣（実測 3.995 / 4.005 Hz）に実エネルギーが乗る**。
         ★ これが本当の危険であって、「状態がゆっくり動くこと」は危険ではない。
         **--selftest がこれを実測で示す。**

      ⚠️★★ **「ちょうど k*1 Hz に線が立つ」と書いてはならない**——そこは ZOH の sinc の
         **零点**であり、逆に**エネルギーがほぼ無い**（実測 1.9e-17）。
         初稿はここを取り違えており、selftest が誤りを検出したので訂正した。
         **見るべきは整数倍そのものではなく、その両脇の側帯波である。**

★★★ 帰結: 平滑化は **1Hz 側ではなくレンダ側（フレーム/オーディオレート）で回す**。
     1Hz スナップショットは *目標値* を与えるだけで、出力は毎フレーム連続的にそこへ向かう。
     「1 秒ごとに値が変わる」形ではなく「1 秒ごとに次の値へ滑らかに向かう」形にする（spec §1.2）。

⚠️ dt は 1.000 s 固定ではない —— 実測で **2.691 s** のギャップが存在した
   (`src-tauri/tests/fixtures/phase1_ime_heavy.ndjson` を replay した結果・2026-08-11)。
   固定 alpha の EWMA は、サンプルが飛ぶと実効時定数が変わってしまう。
   -> ★ 本実装は **alpha = 1 - exp(-dt/tau)** として dt を毎回見る。tau は dt に依らず一定になる。

使い方:

    python expr_smooth.py --selftest              # 数値検算（PASS/FAIL）
    python expr_smooth.py <in.csv> <out.csv> [--tau 60 --fps 60 --columns ewma_x,ewma_y,p_stuck]

⚠️ 本モジュールは **GSE 本体を一切変更しない**。`gse-replay` の出力を読むだけ（D5）。
"""

from __future__ import annotations

import argparse
import cmath
import csv
import math
import os
import sys

# ---------------------------------------------------------------------------
# 版の刻印（`design.md` §4.4 / spec §5 要件 4）
#   「値は適応してよい。写し方と意味は版で凍結する。」
#   ⚠️ pilot 実施中はこの版を動かさない。動かすなら版を上げる。
# ---------------------------------------------------------------------------
EXPR_VERSION = "0.3.0-step4"

# 時定数の下限（秒）。spec §1.3 が要求する値。これを下回る設定は拒否する。
TAU_MIN_S = 60.0

# ★ 1 レンダサンプルあたりの最大変化量の上限（フルスケール比）。
#   これを超えると段差がオンセットとして聞こえうる = spec §1.2 が言う「本当の危険」。
#   ⚠️★★ tau だけ守っても fps が低ければ段差は大きくなる（tau=60 でも fps=1 なら 2.5e-03 = 基準の 2.5 倍）。
#     → **tau と fps の両方を検証する**。片方だけガードするのは守っているつもりの空回りである。
MAX_STEP_PER_FRAME = 1.0e-3

# ★★ 離席とみなすギャップの既定値 [s]。
#   ⚠️ **発明した数値ではない** —— production の `src-tauri/src/analysis/intervention.rs:15`
#      `const AWAY_IDLE_MS: u64 = 180_000;` に接地させている
#      （`probe_scheduler.rs:153` も「intervention.rs AWAY_IDLE_MS と一致」と明記）。
#   ★ 実データで判明: Phase1 の実セッションでは、経過時間の **42–71% が離席ギャップ**だった
#     （P010: 2455 s 中 1749 s = 71% / P011: 1890 s 中 788 s = 42%・最大ギャップ 994 s）。
#     ここを跨いで平滑化すると、**本人が居ない間のフレームを捏造する**
#     （実測: P010 で 147,329 フレーム中 104,940 = 71% が離席中・16.5 MB）。
AWAY_GAP_S = 180.0

# ★ 出力側が使う予約列。--columns にこれらを渡すと出力ヘッダが二重になり、
#   DictReader の後勝ちで segment ID が入力値に潰される（実測）。out_cols の生成元と同じ集合にする。
RESERVED_COLUMNS = frozenset({"t_rel_s", "segment", "expr_version"})


def dt_nominal_of(fps: float) -> float:
    """レンダ周期 [s]。fps<=0 は validate_render_rate 側で弾く。"""
    return 1.0 / fps if fps > 0 else float("inf")

# 禁止帯（Hz）。spec §1.1。
FORBIDDEN_PEAK_HZ = 4.0          # fluctuation strength のピーク。ISE を 70 例中 63 例予測した予測子
FORBIDDEN_BAND_HZ = (0.5, 20.0)  # fluctuation strength の定義域
ROUGHNESS_BAND_HZ = (15.0, 70.0) # roughness が立ち上がり 70 Hz で最大


class ExprSmoother:
    """dt を見る一次遅れ（one-pole low-pass）。

    y[k] = y[k-1] + (1 - exp(-dt/tau)) * (target - y[k-1])

    ★ dt を毎回見るので、レンダレートを変えても・入力が飛んでも **tau は一定**である。
    ★ 一次遅れはオーバーシュートしない（目標を越えない）ので、
      「行き過ぎて戻る」形の余計な変動を作らない。
    """

    def __init__(self, tau_s: float = TAU_MIN_S, initial: float | None = None):
        if tau_s < TAU_MIN_S:
            raise ValueError(
                f"tau={tau_s}s は下限 {TAU_MIN_S}s を下回る。"
                " spec §1.3 が要求する時定数を満たさない（禁止帯に近づく）。"
            )
        self.tau_s = float(tau_s)
        self.value = initial
        self.max_step = 0.0  # 1 レンダサンプルあたりの最大変化量（オンセット性の指標）

    def update(self, target: float, dt_s: float) -> float:
        if self.value is None:
            # 初期値は最初の目標に合わせる（起動時に大きなランプを作らない）
            self.value = float(target)
            return self.value
        if dt_s <= 0.0:
            return self.value
        alpha = 1.0 - math.exp(-dt_s / self.tau_s)
        delta = alpha * (float(target) - self.value)
        self.value += delta
        self.max_step = max(self.max_step, abs(delta))
        return self.value

    @staticmethod
    def validate_render_rate(tau_s: float, fps: float) -> None:
        """★ レンダレートが「段差 < MAX_STEP_PER_FRAME」を満たすか検証する。

        フルスケール跳躍（0 -> 1）のとき、1 フレームの変化は 1 - exp(-1/(fps*tau)) である。
        ⚠️ tau だけ守っても fps が低いと段差が基準を超える（実測: tau=60/fps=1 で 2.523e-03）。
        """
        if fps <= 0.0:
            raise ValueError(f"fps={fps} は正の値でなければならない")
        step = 1.0 - math.exp(-1.0 / (fps * tau_s))
        if step >= MAX_STEP_PER_FRAME:
            fps_min = -1.0 / (tau_s * math.log(1.0 - MAX_STEP_PER_FRAME))
            raise ValueError(
                f"fps={fps} / tau={tau_s}s ではフルスケール跳躍時の 1 フレーム変化が "
                f"{step:.3e} となり、上限 {MAX_STEP_PER_FRAME:.0e} を超える"
                f"（段差がオンセットとして聞こえうる・spec §1.2）。"
                f" tau={tau_s}s なら fps >= {fps_min:.1f} が要る。"
            )

    def cutoff_hz(self) -> float:
        """-3 dB カットオフ周波数 f_c = 1 / (2*pi*tau)。"""
        return 1.0 / (2.0 * math.pi * self.tau_s)

    def response_db(self, freq_hz: float) -> float:
        """周波数 freq_hz における振幅応答 [dB]（解析解）。

        |H(f)| = 1 / sqrt(1 + (2*pi*f*tau)^2)
        """
        mag = 1.0 / math.sqrt(1.0 + (2.0 * math.pi * freq_hz * self.tau_s) ** 2)
        return 20.0 * math.log10(mag)


# ---------------------------------------------------------------------------
# 検算の道具（numpy を使わない。必要なのは「特定の周波数の振幅」だけなので DFT を直接書く）
# ---------------------------------------------------------------------------
def dft_magnitude(
    signal: list[float], fs_hz: float, freq_hz: float, window: bool = True
) -> float:
    """signal（サンプリング周波数 fs_hz）の freq_hz 成分の片側振幅。

    FFT は要らない。見たい周波数が数点しかないので O(N) の直接評価で足りる。

    ⚠️★★★ **window=False にしてはならない（既定で Hann 窓を掛ける）。**
    表現層の信号は低域に非常に強い成分を持つ（状態の波は 0.001-0.02 Hz）ため、
    **窓を掛けないと低域からの漏れが -80 dB 帯を埋め尽くし、測定が逆の符号を出す。**

    ★ 実測（2026-08-11）——同じ信号の 4.0 Hz 成分:

        窓なし: 階段 1.86e-17 / 平滑後 4.46e-05  -> 「平滑化すると増える」という誤結論
        Hann  : 階段 2.68e-06 / 平滑後 1.79e-09  -> -63.5 dB（解析解 -63.6 dB と一致）

    **窓を入れた測定だけが解析解と一致する。** Step 6（音そのものの変調スペクトル）でも同じ罠がある。
    """
    n = len(signal)
    # ★ n<3 を弾く。対称 Hann は n=1 で (n-1)=0 のゼロ除算、n=2 で両端が 0 になり
    #   コヒーレントゲイン cg=0 → /cg でゼロ除算になる（両方とも実測で確認）。
    #   ⚠️ この関数は Step 6（音そのものの変調スペクトル）でも再利用する前提なので、
    #      「現状の呼び出し元では踏まない」で放置しない。
    if n < 3:
        return 0.0
    mean = sum(signal) / n
    if window:
        # Hann 窓 + コヒーレントゲイン補正（振幅を保つ）
        win = [0.5 - 0.5 * math.cos(2.0 * math.pi * i / (n - 1)) for i in range(n)]
        cg = sum(win) / n
    else:
        win = [1.0] * n
        cg = 1.0
    w = -2j * cmath.pi * freq_hz / fs_hz
    acc = 0j
    for i, x in enumerate(signal):
        acc += (x - mean) * win[i] * cmath.exp(w * i)
    return abs(acc) / n * 2.0 / cg  # 片側振幅


def zero_order_hold(targets: list[float], hold_s: float, fs_hz: float) -> list[float]:
    """★ 「1Hz サンプルをそのまま当てる」= 零次ホールドの階段を作る（比較対象・危険な側）。"""
    per = max(1, int(round(hold_s * fs_hz)))
    out: list[float] = []
    for t in targets:
        out.extend([t] * per)
    return out


def smoothed_from_targets(
    targets: list[float], hold_s: float, fs_hz: float, tau_s: float
) -> tuple[list[float], ExprSmoother]:
    """★ 目標値を保持しつつ、**レンダレートで**連続的に追従させる（安全な側）。"""
    sm = ExprSmoother(tau_s=tau_s, initial=targets[0] if targets else 0.0)
    dt = 1.0 / fs_hz
    per = max(1, int(round(hold_s * fs_hz)))
    out: list[float] = []
    for t in targets:
        for _ in range(per):
            out.append(sm.update(t, dt))
    return out, sm


# ---------------------------------------------------------------------------
# selftest
# ---------------------------------------------------------------------------
def selftest() -> int:
    passed = 0
    failed = 0

    def ok(msg: str) -> None:
        nonlocal passed
        passed += 1
        print(f"  [PASS] {msg}")

    def bad(msg: str) -> None:
        nonlocal failed
        failed += 1
        print(f"  [FAIL] {msg}")

    print(f"EXPR_VERSION = {EXPR_VERSION}")

    print("\n== 1. 時定数の定義どおりか（t=tau で 63.2% に達する） ==")
    for fps in (30.0, 60.0, 240.0):
        sm = ExprSmoother(tau_s=60.0, initial=0.0)
        dt = 1.0 / fps
        steps = int(round(60.0 * fps))
        for _ in range(steps):
            sm.update(1.0, dt)
        expected = 1.0 - math.exp(-1.0)
        err = abs(sm.value - expected)
        if err < 1e-3:
            ok(f"fps={fps:6.1f}: t=tau で {sm.value:.5f}（理論 {expected:.5f}, 誤差 {err:.2e}）")
        else:
            bad(f"fps={fps:6.1f}: {sm.value:.5f} != {expected:.5f}（誤差 {err:.2e}）")

    print("\n== 2. ★ dt が不規則でも時定数が変わらない（実測 2.691 s のギャップ対策） ==")
    # 同じ 60 秒を「均一 1 s 刻み」と「1.0/2.691 s の混在」で進め、到達点を比べる
    sm_uniform = ExprSmoother(tau_s=60.0, initial=0.0)
    t = 0.0
    while t < 60.0 - 1e-9:
        step = min(1.0, 60.0 - t)
        sm_uniform.update(1.0, step)
        t += step
    sm_irregular = ExprSmoother(tau_s=60.0, initial=0.0)
    t = 0.0
    pattern = [1.0, 2.691, 1.0, 1.0, 2.691]
    i = 0
    while t < 60.0 - 1e-9:
        step = min(pattern[i % len(pattern)], 60.0 - t)
        sm_irregular.update(1.0, step)
        t += step
        i += 1
    diff = abs(sm_uniform.value - sm_irregular.value)
    if diff < 1e-9:
        ok(f"均一 {sm_uniform.value:.9f} vs 不規則 {sm_irregular.value:.9f}（差 {diff:.2e}）")
    else:
        bad(f"dt によって到達点が変わった（差 {diff:.2e}）")

    print("\n== 3. 禁止帯の減衰（解析解 |H(f)| = 1/sqrt(1+(2*pi*f*tau)^2)） ==")
    sm = ExprSmoother(tau_s=60.0)
    fc = sm.cutoff_hz()
    print(f"  tau=60s -> f_c = {fc:.6f} Hz  (1/tau = {1/60.0:.6f} Hz)")
    if fc < FORBIDDEN_BAND_HZ[0] / 100.0:
        ok(f"f_c={fc:.6f} Hz は禁止帯下端 {FORBIDDEN_BAND_HZ[0]} Hz の 1/100 未満")
    else:
        bad(f"f_c={fc:.6f} Hz が禁止帯に近すぎる")
    # ★ 判定基準は周波数ごとに変える（理由を明記する。後付けで緩めない）:
    #   - 4 Hz（fluctuation strength のピーク＝実害が最大の点）: <= -60 dB
    #   - 帯の端（0.5 / 20 / 70 Hz）: <= -40 dB
    #     ⚠ 0.5 Hz は **入力側の Nyquist そのもの**である（推論ゲートが 1Hz なので
    #       信号は 0.5 Hz より速く動けない・spec §1.2）。つまり 0.5 Hz は
    #       「入力が原理的に到達できない上限」であり、ここに -60 dB を要求する意味は薄い。
    for f, limit_db, why in (
        (FORBIDDEN_PEAK_HZ, -60.0, "ピーク（実害最大）"),
        (FORBIDDEN_BAND_HZ[0], -40.0, "帯の下端＝入力の Nyquist"),
        (FORBIDDEN_BAND_HZ[1], -40.0, "帯の上端"),
        (ROUGHNESS_BAND_HZ[1], -40.0, "roughness 最大点"),
    ):
        db = sm.response_db(f)
        if db <= limit_db:
            ok(f"{f:5.1f} Hz の減衰 {db:7.1f} dB (<= {limit_db:.0f} dB / {why})")
        else:
            bad(f"{f:5.1f} Hz の減衰 {db:7.1f} dB が基準 {limit_db:.0f} dB に不足")

    print("\n== 4. ★★ 1Hz 階段は 4 Hz の「隣」に実エネルギーを乗せる（実測） ==")
    # 状態がゆっくり動く様子を模した目標列。
    # ★ これは **合成信号** である（実セッションのデータではない）。
    #   検算の対象は「階段が作るスペクトル」であって、データの中身ではない。
    f_sig = 0.005  # 状態の波（0.001-0.02 Hz の帯域に置く・spec §1.1）
    targets = [0.5 + 0.4 * math.sin(2.0 * math.pi * f_sig * k) for k in range(300)]
    fs = 200.0
    naive = zero_order_hold(targets, hold_s=1.0, fs_hz=fs)
    smooth, _ = smoothed_from_targets(targets, hold_s=1.0, fs_hz=fs, tau_s=60.0)

    # ★ 見るのは整数倍そのものではなく **側帯波 k*1Hz +- f_sig**。
    #   整数倍ちょうどは ZOH の sinc の零点なので、そこで測ると何も見えない。
    peak = FORBIDDEN_PEAK_HZ
    for f in (peak - f_sig, peak + f_sig):
        m_naive = dft_magnitude(naive, fs, f)
        m_smooth = dft_magnitude(smooth, fs, f)
        ratio_db = 20.0 * math.log10(m_smooth / m_naive)
        analytic = ExprSmoother(tau_s=60.0).response_db(f)
        print(
            f"  {f:6.3f} Hz : 階段 {m_naive:.3e} / 平滑後 {m_smooth:.3e}"
            f" = {ratio_db:7.1f} dB （解析解 {analytic:.1f} dB）"
        )
        if m_naive > 1e-5:
            ok(f"★ 階段は {f:.3f} Hz に実エネルギーを持つ（{m_naive:.3e}）= 危険の実証")
        else:
            bad(f"階段の {f:.3f} Hz 成分が小さすぎる（検査が空回りしている疑い）")
        if ratio_db <= -60.0:
            ok(f"★ 平滑化で {f:.3f} Hz が {ratio_db:.1f} dB 下がる")
        else:
            bad(f"平滑化後も {f:.3f} Hz が残る（{ratio_db:.1f} dB）")
        # ★ 実測が解析解と一致することを要求する（どちらかが壊れたら気づける）
        if abs(ratio_db - analytic) <= 1.0:
            ok(f"  実測 {ratio_db:.1f} dB が解析解 {analytic:.1f} dB と一致（±1 dB）")
        else:
            bad(f"  実測 {ratio_db:.1f} dB と解析解 {analytic:.1f} dB が食い違う")

    # ⚠ 整数倍ちょうどは零点であることも固定しておく（初稿の誤りの再発防止）
    m_at_peak = dft_magnitude(naive, fs, peak)
    m_at_side = dft_magnitude(naive, fs, peak - f_sig)
    if m_at_peak < m_at_side / 10.0:
        ok(f"★ {peak} Hz ちょうどは ZOH の零点（{m_at_peak:.3e} << 側帯波 {m_at_side:.3e}）")
    else:
        bad(f"{peak} Hz ちょうどに零点が無い（前提が崩れている）")

    print("\n== 5. ★ 時間領域: 段差そのもの（spec が言う「本当の危険」） ==")
    step_naive = max(abs(naive[i + 1] - naive[i]) for i in range(len(naive) - 1))
    step_smooth = max(abs(smooth[i + 1] - smooth[i]) for i in range(len(smooth) - 1))
    ratio = step_naive / step_smooth
    print(f"  1 サンプル間の最大段差: 階段 {step_naive:.4e} / 平滑後 {step_smooth:.4e}")
    if ratio >= 100.0:
        ok(f"★ 段差が {ratio:.0f} 倍（{20 * math.log10(ratio):.1f} dB）小さくなる")
    else:
        bad(f"段差の低減が {ratio:.1f} 倍しかない")

    print("\n== 6. 1 レンダサンプルあたりの最大変化量（オンセット性） ==")
    # 最悪ケース: 0 -> 1 の飛び。1 フレームでどれだけ動くか。
    for fps in (60.0, 200.0):
        sm3 = ExprSmoother(tau_s=60.0, initial=0.0)
        sm3.update(1.0, 1.0 / fps)
        step_frac = sm3.value
        if step_frac < 1e-3:
            ok(f"fps={fps:5.1f}: フルスケール跳躍でも 1 フレーム {step_frac:.3e}（< 1e-3）")
        else:
            bad(f"fps={fps:5.1f}: 1 フレームで {step_frac:.3e} 動く（段差が大きい）")

    print("\n== 7. ★★ 本番経路（smooth_csv / CLI）を実際に通す ==")
    # ⚠️ §1-6 は解析核だけを検査していて、TouchDesigner に実際に渡る CSV 経路を 1 度も通っていなかった。
    #   保証（段差 < 1e-3・時刻の単調増加・重複なし）は**本番経路で**成り立たなければ意味がない。
    import tempfile

    with tempfile.TemporaryDirectory() as td:
        src_csv = os.path.join(td, "in.csv")
        dst_csv = os.path.join(td, "out.csv")
        # 不規則 dt（実測の 2.691 s ギャップを含む）を持つ合成 CSV
        times = [0.0, 1.0, 2.0, 4.691, 5.691, 6.691]
        with open(src_csv, "w", encoding="utf-8", newline="\n") as fh:
            w = csv.writer(fh, lineterminator="\n")
            w.writerow(["t_rel_s", "ewma_x", "dt_s"])
            for k, t in enumerate(times):
                w.writerow([t, 0.1 + 0.05 * k, "" if k == 0 else round(t - times[k - 1], 3)])

        rc = smooth_csv(src_csv, dst_csv, tau_s=60.0, fps=60.0, columns=["ewma_x"])
        if rc == 0:
            ok("smooth_csv が正常終了した")
        else:
            bad(f"smooth_csv が rc={rc}")

        with open(dst_csv, encoding="utf-8", newline="") as fh:
            out_rows = list(csv.DictReader(fh))
        ts = [float(r["t_rel_s"]) for r in out_rows]
        if out_rows:
            ok(f"フレームが書かれた（{len(out_rows)} 行）")
        else:
            bad("フレームが 0 行")
        if len(ts) == len(set(ts)):
            ok("t_rel_s に重複が無い")
        else:
            bad(f"t_rel_s に重複が {len(ts) - len(set(ts))} 件")
        if all(ts[i + 1] > ts[i] for i in range(len(ts) - 1)):
            ok("t_rel_s が厳密単調増加")
        else:
            bad("t_rel_s が単調増加でない")
        # ★ 出力時刻の終端が入力の終端と一致すること（dt_eff を使っているかの検査）
        if abs(ts[-1] - times[-1]) < 1e-6:
            ok(f"出力の終端 {ts[-1]} が入力の終端 {times[-1]} と一致（時間軸が 1 系統）")
        else:
            bad(f"終端がずれている: 出力 {ts[-1]} vs 入力 {times[-1]}")
        vals = [float(r["ewma_x_smooth"]) for r in out_rows]
        worst = max(abs(vals[i + 1] - vals[i]) for i in range(len(vals) - 1))
        if worst < MAX_STEP_PER_FRAME:
            ok(f"本番経路の最大段差 {worst:.3e} < {MAX_STEP_PER_FRAME:.0e}")
        else:
            bad(f"本番経路の最大段差 {worst:.3e} が上限を超えた")
        if out_rows and out_rows[0].get("expr_version") == EXPR_VERSION:
            ok(f"出力 CSV に EXPR_VERSION が刻まれている（{EXPR_VERSION}）")
        else:
            bad("出力 CSV に EXPR_VERSION が無い")

        # ★ 異常入力を 3 通り拒否できるか（正常だけ試して満足しない・ルール 5b）
        for label, kwargs in (
            ("fps が低すぎる（段差が上限超え）", dict(tau_s=60.0, fps=1.0, columns=["ewma_x"])),
            ("fps=0", dict(tau_s=60.0, fps=0.0, columns=["ewma_x"])),
            ("空欄を含む列 dt_s を指定", dict(tau_s=60.0, fps=60.0, columns=["dt_s"])),
        ):
            try:
                smooth_csv(src_csv, os.path.join(td, "x.csv"), **kwargs)
                bad(f"{label} が拒否されなかった")
            except ValueError:
                ok(f"{label} は ValueError で拒否された")

        # ★ 時刻の逆行を拒否するか
        bad_csv = os.path.join(td, "bad.csv")
        with open(bad_csv, "w", encoding="utf-8", newline="\n") as fh:
            w = csv.writer(fh, lineterminator="\n")
            w.writerow(["t_rel_s", "ewma_x"])
            for t, v in ((0.0, 0.1), (2.0, 0.2), (1.0, 0.3)):
                w.writerow([t, v])
        try:
            smooth_csv(bad_csv, os.path.join(td, "y.csv"), tau_s=60.0, fps=60.0, columns=["ewma_x"])
            bad("時刻の逆行が拒否されなかった")
        except ValueError:
            ok("時刻の逆行は ValueError で拒否された")

        # ★ 入力と出力が同一パスなら拒否するか
        try:
            smooth_csv(src_csv, src_csv, tau_s=60.0, fps=60.0, columns=["ewma_x"])
            bad("src == dst が拒否されなかった")
        except ValueError:
            ok("src == dst は ValueError で拒否された")

        # ★★ 2 回目のレビューで見つかった穴を検査に落とす（同じ形を二度通さない）
        # (1) NaN / inf —— max(0.0, nan) == 0.0 なので段差ガードが 0.0 を報告して素通りしていた
        for label, val in (("nan", "nan"), ("inf", "inf")):
            nan_csv = os.path.join(td, f"{label}.csv")
            with open(nan_csv, "w", encoding="utf-8", newline="\n") as fh:
                w = csv.writer(fh, lineterminator="\n")
                w.writerow(["t_rel_s", "ewma_x"])
                for t in (0.0, 1.0, 2.0):
                    w.writerow([t, val])
            try:
                smooth_csv(nan_csv, os.path.join(td, f"{label}o.csv"), tau_s=60.0, fps=60.0,
                           columns=["ewma_x"])
                bad(f"★ {label} が拒否されなかった（段差ガードが 0.0 を報告して素通りする）")
            except ValueError:
                ok(f"★ {label} は ValueError で拒否された")
        # 前提の再確認: Python の max(0.0, nan) は 0.0 である（この仕様が穴の原因だった）
        if max(0.0, float("nan")) == 0.0:
            ok("前提確認: max(0.0, nan) == 0.0（だから入口で弾く必要がある）")
        else:
            bad("max(0.0, nan) の挙動が想定と違う（検査の前提が崩れている）")

        # (2) 予約列 —— segment / expr_version を --columns に渡せてしまい ID が潰れていた
        for col in ("segment", "expr_version", "t_rel_s"):
            try:
                smooth_csv(src_csv, os.path.join(td, "rz.csv"), tau_s=60.0, fps=60.0, columns=[col])
                bad(f"予約列 {col} が拒否されなかった")
            except ValueError:
                ok(f"予約列 {col} は ValueError で拒否された")

        # (3) max_gap_s —— 0 を渡すと全行が個別 segment になり「生の階段」が出ていた
        for bad_gap in (0.0, -1.0, 1.0 / 60.0):
            try:
                smooth_csv(src_csv, os.path.join(td, "gz.csv"), tau_s=60.0, fps=60.0,
                           columns=["ewma_x"], max_gap_s=bad_gap)
                bad(f"max_gap_s={bad_gap} が拒否されなかった（生の階段が出る）")
            except ValueError:
                ok(f"max_gap_s={bad_gap:g} は ValueError で拒否された")

        # (4) 検証に失敗したら **出力を残さない**（stdout は成功・stderr は失敗、という状態を作らない）
        leftover_src = os.path.join(td, "leftover.csv")
        with open(leftover_src, "w", encoding="utf-8", newline="\n") as fh:
            w = csv.writer(fh, lineterminator="\n")
            w.writerow(["t_rel_s", "ewma_x"])
            for t, v in ((0.0, "0.1"), (1.0, "0.2"), (2.0, "xyz")):
                w.writerow([t, v])
        leftover_dst = os.path.join(td, "leftover_out.csv")
        try:
            smooth_csv(leftover_src, leftover_dst, tau_s=60.0, fps=60.0, columns=["ewma_x"])
            bad("非数値の行が拒否されなかった")
        except ValueError:
            if os.path.exists(leftover_dst):
                bad("★ 失敗したのに出力 CSV が残っている")
            else:
                ok("★ 失敗時に出力 CSV を残さない")

    print("\n== 7b. ★★ 離席ギャップを跨いで平滑化しないか（実データで判明した問題） ==")
    with tempfile.TemporaryDirectory() as td:
        gap_csv = os.path.join(td, "gap.csv")
        out_csv = os.path.join(td, "gapout.csv")
        # 実データ (P010) の形を模す: 1 s 刻み -> 994 s の離席 -> また 1 s 刻み
        times = [0.0, 1.0, 2.0, 3.0, 997.0, 998.0, 999.0]
        with open(gap_csv, "w", encoding="utf-8", newline="\n") as fh:
            w = csv.writer(fh, lineterminator="\n")
            w.writerow(["t_rel_s", "ewma_x"])
            for k, t in enumerate(times):
                w.writerow([t, 0.1 + 0.05 * k])

        smooth_csv(gap_csv, out_csv, tau_s=60.0, fps=60.0, columns=["ewma_x"], max_gap_s=AWAY_GAP_S)
        with open(out_csv, encoding="utf-8", newline="") as fh:
            grows = list(csv.DictReader(fh))
        segs = sorted({int(r["segment"]) for r in grows})
        # 跨いでいたら 994 s * 60 fps ≈ 59,640 フレーム増える
        if len(grows) < 1000:
            ok(f"離席中のフレームを生成していない（{len(grows)} 行。跨いだら約 59,640 行増える）")
        else:
            bad(f"離席を跨いでフレームを生成している（{len(grows)} 行）")
        if segs == [0, 1]:
            ok(f"segment が分割されている: {segs}")
        else:
            bad(f"segment が期待どおりでない: {segs}")
        # ★ 値は持ち越す = 復帰時にオンセットを作らない
        vals = [float(r["ewma_x_smooth"]) for r in grows]
        jump = max(abs(vals[i + 1] - vals[i]) for i in range(len(vals) - 1))
        if jump < MAX_STEP_PER_FRAME:
            ok(f"復帰時に段差を作っていない（最大 {jump:.3e} < {MAX_STEP_PER_FRAME:.0e}）")
        else:
            bad(f"復帰時に段差 {jump:.3e} が出た（オンセットになる）")
        # ★ 閾値を上げれば跨ぐこと（＝この分岐が実際に効いていること）も確かめる
        out2 = os.path.join(td, "gapout2.csv")
        smooth_csv(gap_csv, out2, tau_s=60.0, fps=60.0, columns=["ewma_x"], max_gap_s=2000.0)
        with open(out2, encoding="utf-8", newline="") as fh:
            n2 = sum(1 for _ in csv.DictReader(fh))
        if n2 > len(grows) * 10:
            ok(f"閾値を上げると跨ぐ（{len(grows)} -> {n2} 行）＝分岐が実際に効いている")
        else:
            bad(f"閾値を上げても挙動が変わらない（{len(grows)} -> {n2} 行・分岐が空回り）")

    print("\n== 8. dft_magnitude の短い信号（ゼロ除算しないか） ==")
    for n in (0, 1, 2, 3):
        try:
            dft_magnitude([1.0] * n, 10.0, 1.0)
            ok(f"n={n} で例外が出ない")
        except Exception as exc:  # noqa: BLE001 - 検査なので広く捕まえる
            bad(f"n={n} で {type(exc).__name__}: {exc}")

    print("\n== 9. 下限ガードが効くか（tau < 60 を拒否する） ==")
    try:
        ExprSmoother(tau_s=59.9)
        bad("tau=59.9 が通ってしまった（ガードが空回り）")
    except ValueError:
        ok("tau=59.9 は ValueError で拒否された")
    try:
        ExprSmoother(tau_s=60.0)
        ok("tau=60.0 は通る")
    except ValueError:
        bad("tau=60.0 が拒否された（下限の境界が誤り）")

    print(f"\n== 結果 ==\n  PASS={passed}  FAIL={failed}")
    if passed + failed == 0:
        print("  [FAIL] 検査が 1 件も実行されていない（空回り）")
        return 1
    return 0 if failed == 0 else 1


# ---------------------------------------------------------------------------
def smooth_csv(
    src: str,
    dst: str,
    tau_s: float,
    fps: float,
    columns: list[str],
    max_gap_s: float = AWAY_GAP_S,
) -> int:
    # ★ tau と fps の**両方**を先に検証する（片方だけのガードは空回り）
    ExprSmoother.validate_render_rate(tau_s, fps)

    if os.path.realpath(src) == os.path.realpath(dst):
        raise ValueError(f"入力と出力が同じファイルである: {src}（入力を破壊するので拒否する）")

    with open(src, "r", encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    if not rows:
        raise ValueError(f"{src}: 行が 0 件")
    if len(rows) < 2:
        # ★ 1 行だと先頭行が初期値に消費されてフレームが 0 になる。
        #   「ヘッダだけ書いて exit 0」は成功に見える失敗なので拒否する。
        raise ValueError(
            f"{src}: データ行が {len(rows)} 件しかない。"
            " 先頭行は平滑器の初期値に使うので、平滑化には 2 行以上が要る。"
        )

    if "t_rel_s" not in rows[0]:
        raise ValueError(f"{src}: 列 t_rel_s が無い（snapshot_to_csv.py の出力を渡すこと）")
    missing = [c for c in columns if c not in rows[0]]
    if missing:
        raise ValueError(f"{src}: 指定された列が無い: {missing}")
    # ★ 予約列との衝突を拒否する。
    #   ⚠️ 初版は `t_rel_s` しか見ておらず、**新設した `segment` / `expr_version` が無防備**だった。
    #     `--columns segment` を通すと出力ヘッダが `...,segment,expr_version,segment_smooth,segment`
    #     となり、**DictReader は後勝ちなので segment ID が入力値で潰れる**（実測）。
    #     自分の出力を再投入すると起きる。→ 出力列の生成元と同じ集合で判定する。
    bad_cols = sorted(set(c for c in columns if c in RESERVED_COLUMNS))
    if bad_cols:
        raise ValueError(f"--columns に予約列は指定できない: {bad_cols}（予約: {sorted(RESERVED_COLUMNS)}）")
    dupes = sorted(set(c for c in columns if columns.count(c) > 1))
    if dupes:
        raise ValueError(f"--columns に重複がある: {dupes}")

    # ★ max_gap_s の検証。⚠️ 無検証だと `--max-gap-s 0` が通り、1Hz の全行が個別 segment になって
    #   **出力が 1 サンプル 1 フレームの生の階段**（= spec §1.2 の「本当の危険」そのもの）になる。
    #   それでも「最大段差 OK」と出て exit 0 だった（実測）。tau/fps を検証したのと同じ理由でここも要る。
    if max_gap_s <= dt_nominal_of(fps):
        raise ValueError(
            f"max_gap_s={max_gap_s} はレンダ周期 {dt_nominal_of(fps):.6g}s 以下である。"
            " 全サンプルが個別 segment になり、平滑化が無効化される（生の階段が出る）。"
        )

    def num(row_index: int, col: str) -> float:
        raw = rows[row_index][col]
        try:
            v = float(raw)
        except (TypeError, ValueError):
            raise ValueError(
                f"{src}: 列 {col} の {row_index + 1} 行目が数値でない: {raw!r}"
                " （dt_s のように空欄を含む列は平滑化できない）"
            ) from None
        # ⚠️★★★ NaN / inf を弾く。float() は "nan" / "inf" を**受理してしまう**。
        #   NaN が 1 度混じると self.value は永久に NaN になり、さらに Python では
        #   **max(0.0, nan) == 0.0** なので `max_step` が 0.0 のまま残り、
        #   「実測の最大段差」ガードが **0.000e+00 < 1e-03 : OK** と報告して全損出力を通す。
        #   ★ 本モジュールが潰そうとしている silent pass そのものなので、入口で落とす
        #     (2 回目のレビューで発見・実測で確認)。
        if not math.isfinite(v):
            raise ValueError(f"{src}: 列 {col} の {row_index + 1} 行目が有限値でない: {raw!r}")
        return v

    # ⚠️★★ 入力時刻の厳密単調増加を先に検証する。
    #   `span = max(t_target - prev_t, dt_nominal)` は下限で潰すので、
    #   **重複・逆行した時刻を「最低 dt 経過した」という架空の時間に化けさせてしまう**。
    #   → 壊れた入力ほど滑らかに見える、という最悪の隠蔽になるので、ここで落とす。
    #   ★ どちらの時刻を正とするかの設計判断（S0-D10）: **`t_rel_s` を単一の真実とする**。
    #     `snapshot_to_csv.py` が出す `dt_s` 列は**人間が読むための注記**であって、
    #     平滑化は `t_rel_s` の差分から `span` を再計算する（2 系統の時刻を持たない）。
    for i in range(1, len(rows)):
        t_prev, t_cur = num(i - 1, "t_rel_s"), num(i, "t_rel_s")
        if t_cur <= t_prev:
            raise ValueError(
                f"{src}: t_rel_s が単調増加でない（{i} 行目 {t_prev} -> {i + 1} 行目 {t_cur}）。"
                " 重複・逆行した時刻は架空の経過時間に化けるので拒否する。"
            )

    smoothers = {c: ExprSmoother(tau_s=tau_s, initial=num(0, c)) for c in columns}
    dt_nominal = 1.0 / fps
    out_cols = ["t_rel_s", "segment", "expr_version"] + [f"{c}_smooth" for c in columns] + columns

    n_frames = 0
    segment = 0
    n_gaps = 0
    gap_total = 0.0
    emitted_segments: set[int] = set()
    # ⚠️★ 一時ファイルに書いてから os.replace() で差し替える。
    #   初版は dst に直接書いていたので、**後段のガードで落ちても壊れた CSV が残り**、
    #   しかも stdout には "wrote ..." と出ていた（stdout は成功・stderr は失敗と言う状態・実測）。
    tmp = dst + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
        writer = csv.DictWriter(fh, fieldnames=out_cols, lineterminator="\n")
        writer.writeheader()
        # 先頭行は smoother の初期値として既に使ったので、フレームは出さずに時刻の起点にする
        # （出すと 2 行目の最初のフレームと t_rel_s が重複する）。
        prev_t = num(0, "t_rel_s")
        for i in range(1, len(rows)):
            t_target = num(i, "t_rel_s")
            gap = t_target - prev_t
            # ⚠️★★ 離席ギャップを跨いで平滑化しない（S0-D11）。
            #   跨ぐと「本人が居ない間のフレーム」を捏造することになる
            #   （実データ実測: P010 は経過の 71% が離席・生成フレームの 71% が捏造だった）。
            #   → フレームを出さずに segment を切り、時刻だけ飛ばす。
            #   ★ 平滑器の**値は持ち越す**（リセットするとオンセット＝分節を自分で作ってしまう [P64]）。
            #     ⚠️ 復帰時に「前の状態から続ける」か「無音から立ち上げる」かは**表現の設計判断**であり、
            #        ここでは決めない（Step 3 で耳で決める。`decisions.md` S0-D11 の未決として記録）。
            # ★ 境界は production に合わせて **>=**（`intervention.rs:339` は `idle_ms >= AWAY_IDLE_MS`）。
            #   `>` だとちょうど 180.000 s を跨いでしまい、接地の主張と実装がずれる。
            if gap >= max_gap_s:
                segment += 1
                n_gaps += 1
                gap_total += gap
                prev_t = t_target
                # 復帰直後の 1 サンプル分だけは通常のレートで追従させる
                dt_eff = dt_nominal
                for c in columns:
                    smoothers[c].update(num(i, c), dt_eff)
                rec = {"t_rel_s": round(t_target, 4), "segment": segment, "expr_version": EXPR_VERSION}
                emitted_segments.add(segment)
                for c in columns:
                    rec[f"{c}_smooth"] = round(smoothers[c].value, 8)
                    rec[c] = rows[i][c]
                writer.writerow(rec)
                n_frames += 1
                continue
            # ★ 目標が変わる区間をレンダレートで刻む（1Hz でジャンプさせない）
            span = max(gap, dt_nominal)
            steps = max(1, int(round(span * fps)))
            # ⚠️★ 平滑器に渡す dt は **実際に刻んだ幅** でなければならない。
            #   固定 1/fps を渡すと「出力時刻の進み」と「平滑器内部時間の進み」がずれる
            #   （実測: 不規則 dt の CSV で 6.691 s に対し 6.683 s = 約 0.1% のずれ）。
            #   本モジュールの中核の主張は「dt を毎回見るので tau は一定」なので、ここは実効値を渡す。
            dt_eff = span / steps
            for s in range(steps):
                t = prev_t + (s + 1) * dt_eff
                rec = {"t_rel_s": round(t, 4), "segment": segment, "expr_version": EXPR_VERSION}
                emitted_segments.add(segment)
                for c in columns:
                    rec[f"{c}_smooth"] = round(smoothers[c].update(num(i, c), dt_eff), 8)
                    rec[c] = rows[i][c]
                writer.writerow(rec)
                n_frames += 1
            prev_t = t_target

    if n_frames == 0:
        raise ValueError(f"{dst}: フレームが 1 つも書かれなかった（入力を確認すること）")

    worst_pre = max((smoothers[c].max_step for c in columns), default=0.0)
    if worst_pre >= MAX_STEP_PER_FRAME:
        # ★ 差し替える前に落とす（壊れた CSV を dst に置かない）
        raise ValueError(
            f"実測の 1 フレーム最大変化 {worst_pre:.3e} が上限 {MAX_STEP_PER_FRAME:.0e} を超えた"
        )
    os.replace(tmp, dst)   # ★ ここで初めて dst が現れる

    print(f"wrote {dst}: {n_frames} frames @ {fps} fps, tau={tau_s}s, EXPR_VERSION={EXPR_VERSION}")
    if n_gaps:
        # ★ 落としたものを黙って落とさない（no silent caps）
        print(
            f"  ★ 離席ギャップ (> {max_gap_s:g}s) を {n_gaps} 件・計 {gap_total:.0f}s 跨いだ:"
            f" segment を {len(emitted_segments)} 個に分割し、その間のフレームは生成していない"
            f"（生成していたら約 {int(gap_total * fps):,} フレーム増えていた）"
        )
    for c in columns:
        print(f"  {c}: 1 フレームあたり最大変化 {smoothers[c].max_step:.3e}")
    print(f"  最大段差 {worst_pre:.3e} < 上限 {MAX_STEP_PER_FRAME:.0e} : OK")
    return 0


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("src", nargs="?", help="snapshot_to_csv.py が書いた CSV")
    ap.add_argument("dst", nargs="?", help="出力 CSV")
    ap.add_argument("--tau", type=float, default=TAU_MIN_S, help=f"時定数 [s]（下限 {TAU_MIN_S}）")
    ap.add_argument("--fps", type=float, default=60.0, help="レンダレート [Hz]")
    ap.add_argument("--columns", default="ewma_x,ewma_y,p_stuck", help="平滑化する列（カンマ区切り）")
    ap.add_argument(
        "--max-gap-s",
        type=float,
        default=AWAY_GAP_S,
        help=f"これを超える間隔は離席とみなし跨いで平滑化しない [s]（既定 {AWAY_GAP_S:g} = production の AWAY_IDLE_MS）",
    )
    ap.add_argument("--selftest", action="store_true", help="数値検算だけ実行する")
    args = ap.parse_args(argv[1:])

    if args.selftest:
        return selftest()
    if not args.src or not args.dst:
        ap.print_help()
        return 2
    # ★ 生のトレースバックを出さず、1 行のメッセージ + exit 2 にする
    #   （利用者に「何を直せばよいか」を返す。tau/fps のガードもここを通る）
    try:
        return smooth_csv(
            args.src, args.dst, args.tau, args.fps, args.columns.split(","), args.max_gap_s
        )
    except (ValueError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        # ★ 中断した書きかけを残さない
        try:
            os.unlink(args.dst + ".tmp")
        except OSError:
            pass
        return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
