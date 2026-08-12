#!/usr/bin/env python3
"""層 2（粒子）＋ 層 0 の自律変異の静的検査 — Step 4。

★ このスクリプトが守るのは「音が良いか」ではない（それは耳が決める）。
   守るのは **仕様に接地した約束が実体とずれていないこと** である:

     1. `EXPR_VERSION` が 3 箇所（expr_smooth.py / step4.config.json / Step 3 の layer0.config.json）で一致
     2. 基音が spec §2 の 55–110 Hz 帯から出ていないこと / 倍音が整数次だけであること
     3. ★ 分離案のレートが禁止帯（0.5–20 Hz / 15–70 Hz）に入っていないこと
     4. ★ A 案が状態帯（0.001–0.02 Hz）より 1 桁以上遅いこと（S3-D13 の A 案の定義）
     5. ★ B / C 案が振幅を動かしていないこと（次元で分ける = tilt のみ）
     6. ★ 粒子率の下限 100 grains/s が守られ、かつ **下限を割った候補が実在する**こと
        （引き継ぎ §4a: 下限を割った状態も作って聴かせる = 検査の逆検査と同じ思想）
     7. ★ 表現層の平滑化 τ >= 60 s（spec §1.3・交渉不可）
     8. ★ 盲検の設計が自己整合し、閾値の二項確率が 0.05 未満であること（★ コメントを信じず計算する）
     9. ★★★ [P71] 要件 1（止められる・音量を変えられる）が player に実在すること
    10. ★★★ **S4-D8**: 層 0 のコアが layer0.html と一致していること（2 実装になっていないこと）
    11. Worklet が seed 固定であること（Math.random() を使っていないこと）
    12. player が窓なし DFT を持たず、外部リソースを読まず、alert() を使わないこと

★ `--selftest` は上記の検査そのものを**壊した状態で走らせ、赤くなることを確かめる**
   （`verify-before-claiming` ルール 5b）。
   ⚠️ **このタスク系列で silent pass は 4 回出ている**（S0-D14 の 3 件 ＋ Step 3 の音量スライダ検査）。
   ★ Step 3 の 1 件は「[P71] の交渉不可要件を守るはずの検査が、要件を消しても緑だった」形である。
      → 本ファイルでは **id を厳密一致で書く**（`id="vol"` を正規表現で緩く探さない）。

依存は標準ライブラリのみ（S0-D8 / S4-D7 の方針を踏襲）。
"""

from __future__ import annotations

import argparse
import copy
import json
import math
import re
import sys
from fractions import Fraction
from pathlib import Path

# ⚠️★ Windows のコンソールは cp932 で、`—`(U+2014) や `⚠`(U+26A0) を符号化できない。
#     実測: 何もしないと本文を 1 行出した時点で UnicodeEncodeError で落ちる。
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(errors="backslashreplace")
    except (AttributeError, OSError):
        pass

# ---------------------------------------------------------------------------
# 一次資料の位置（相対で解決する。★ 絶対パスを書かない）
# ---------------------------------------------------------------------------
HERE = Path(__file__).resolve().parent
EXP_DIR = HERE.parent
REPO = EXP_DIR.parent.parent
CONFIG_PATH = EXP_DIR / "step4.config.json"
PLAYER_PATH = EXP_DIR / "player" / "step4.html"
WORKLET_PATH = EXP_DIR / "player" / "grain-processor.js"
SEED_PATH = EXP_DIR / "SEED"
EXPR_SMOOTH_PATH = (
    REPO / ".steering" / "20260811-expression-prototype-step0" / "scripts" / "expr_smooth.py"
)
# ★ S4-D8: 層 0 のコアの比較対象（Step 3 の実体）
STEP3_PLAYER_PATH = (
    REPO / "experiments" / "20260812-expression-layer0-drone" / "player" / "layer0.html"
)
STEP3_CONFIG_PATH = REPO / "experiments" / "20260812-expression-layer0-drone" / "layer0.config.json"

# spec の逐語から取った拘束（★ ここを緩める変更は spec の改訂を伴う）
BAND_HZ = (55.0, 110.0)
FORBIDDEN_MOD_BANDS = ((0.5, 20.0), (15.0, 70.0))
STATE_WAVE_BAND = (0.001, 0.02)
KNOWN_LAWS = {"1/n", "1/n^2"}
GRAIN_FLOOR = 100.0          # spec §2 層 2
TAU_MIN_S = 60.0             # spec §1.3（交渉不可）
LISTEN_S = 600.0             # S3-D3: 試聴 10 分
REPEAT_MARGIN = 5.0
PREV_VERSION = "0.2.0-step3"  # Step 3 の版。ここから上がっていなければならない

# ★★★ S4-D8: 層 0 のコアとして「逐語複製であること」を要求する関数群。
#     ⚠️ allDriftRates は step4 側に存在しない（config の形が違うため allPlanRates を使う）。
#        ★ 「無いから外した」ではなく「別物だから比較しない」と書いておく。
LAYER0_CORE_FUNCS = [
    "maxPartials",
    "partialAmps",
    "buildGraph",
    "startAll",
    "hannAmplitude",
    "decimate",
    "sincGain",
    "steadyPart",
]
LAYER0_CORE_CONSTS = ["dbToLinDev"]


class Fail(Exception):
    """検査の失敗（1 行メッセージで報告し exit 2 にする）。"""


# ---------------------------------------------------------------------------
# 補助
# ---------------------------------------------------------------------------
def strip_js_comments(s: str) -> str:
    """JS のコメントと文字列外の空白を潰す（★ 比較を字面の揺れに強くする）。"""
    s = re.sub(r"/\*.*?\*/", " ", s, flags=re.S)
    s = re.sub(r"(^|[^:])//[^\n]*", r"\1", s)
    return re.sub(r"\s+", " ", s).strip()


def extract_function(text: str, name: str) -> str:
    """`function NAME(...) { ... }` を波括弧の対応で切り出す。★ 正規表現で終端を推測しない。"""
    m = re.search(r"\bfunction\s+" + re.escape(name) + r"\s*\(", text)
    if not m:
        raise Fail(f"関数 {name}() が見つからない")
    i = text.index("{", m.end() - 1)
    depth, j = 0, i
    while j < len(text):
        if text[j] == "{":
            depth += 1
        elif text[j] == "}":
            depth -= 1
            if depth == 0:
                return text[m.start(): j + 1]
        j += 1
    raise Fail(f"関数 {name}() の波括弧が閉じていない")


def extract_const(text: str, name: str) -> str:
    m = re.search(r"\bconst\s+" + re.escape(name) + r"\s*=\s*[^;]+;", text)
    if not m:
        raise Fail(f"定数 {name} が見つからない")
    return m.group(0)


def read_expr_version(text: str) -> str:
    """expr_smooth.py の EXPR_VERSION 定数を読む（import しない = 副作用を持ち込まない）。"""
    m = re.search(r'^EXPR_VERSION\s*=\s*"([^"]+)"', text, re.MULTILINE)
    if not m:
        raise Fail("expr_smooth.py から EXPR_VERSION 定数を読めない")
    return m.group(1)


def in_band(x: float, lo: float, hi: float) -> bool:
    return lo <= x <= hi


def repeat_period_s(rates: list[float]) -> float:
    """複数正弦の和の反復周期 = 1/gcd(周波数)。★ コメントを信じず Fraction で計算する。"""
    if not rates:
        return math.inf
    fr = [Fraction(str(r)).limit_denominator(10**9) for r in rates]
    g = fr[0]
    for f in fr[1:]:
        g = Fraction(math.gcd(g.numerator * f.denominator, f.numerator * g.denominator),
                     g.denominator * f.denominator)
    return float(1 / g) if g > 0 else math.inf


def binom_tail(k: int, n: int, p: float) -> float:
    """P(X >= k) for X~Bin(n, p)。★ 閾値の主張を計算で裏づける（コメントを信じない）。"""
    return sum(math.comb(n, i) * p**i * (1 - p) ** (n - i) for i in range(k, n + 1))


def load_sources():
    cfg_text = CONFIG_PATH.read_text(encoding="utf-8")
    cfg = json.loads(cfg_text)
    html = PLAYER_PATH.read_text(encoding="utf-8")
    worklet = WORKLET_PATH.read_text(encoding="utf-8")
    py_ver = read_expr_version(EXPR_SMOOTH_PATH.read_text(encoding="utf-8"))
    step3_html = STEP3_PLAYER_PATH.read_text(encoding="utf-8")
    step3_ver = json.loads(STEP3_CONFIG_PATH.read_text(encoding="utf-8"))["expr_version"]
    seed_text = SEED_PATH.read_text(encoding="utf-8") if SEED_PATH.exists() else ""
    return cfg, cfg_text, html, worklet, py_ver, step3_html, step3_ver, seed_text


# ---------------------------------------------------------------------------
# 検査本体
# ---------------------------------------------------------------------------
def build_checks(cfg, cfg_text, html, worklet, py_ver, step3_html, step3_ver, seed_text):
    checks: list[tuple[str, callable]] = []

    def add(name):
        def deco(fn):
            checks.append((name, fn))
            return fn
        return deco

    plans = cfg["separation_plans"]["options"]
    L2 = cfg["layer2"]
    ST = cfg["selftest"]
    BT = cfg["blind_test"]

    # ---- 版 ---------------------------------------------------------------
    @add("EXPR_VERSION が expr_smooth.py と step4.config.json で一致する")
    def _():
        if cfg["expr_version"] != py_ver:
            raise Fail(f"config={cfg['expr_version']} / expr_smooth.py={py_ver}")

    @add("EXPR_VERSION が Step 3 の layer0.config.json とも一致する（S4-D3 の追随）")
    def _():
        if step3_ver != py_ver:
            raise Fail(
                f"Step 3 の layer0.config.json={step3_ver} / expr_smooth.py={py_ver}。"
                " S4-D3 は『SSOT を上げたら Step 3 の config も追随させる』と決めている"
            )

    @add("EXPR_VERSION が Step 3 の版から上がっている（層 2 を足したので）")
    def _():
        if py_ver == PREV_VERSION:
            raise Fail(f"層 2 を足したのに EXPR_VERSION が {PREV_VERSION} のまま（S4-D3）")

    # ---- 層 0（spec §2） ---------------------------------------------------
    @add("基音が spec §2 の 55–110 Hz 帯に収まっている")
    def _():
        for o in cfg["candidates"]["base_hz"]["options"]:
            if not in_band(o["hz"], *BAND_HZ):
                raise Fail(f"{o['id']} の {o['hz']} Hz が 55–110 Hz 帯の外")

    @add("減衰則が既知のもの（整数次のみ・非調和成分を持ち込まない）")
    def _():
        for o in cfg["candidates"]["decay_law"]["options"]:
            if o["law"] not in KNOWN_LAWS:
                raise Fail(f"{o['id']} の law={o['law']} が既知のものでない（{sorted(KNOWN_LAWS)}）")
            if not isinstance(o["partials"], int) or o["partials"] < 1:
                raise Fail(f"{o['id']} の partials が正整数でない")

    @add("★ B5: 3 つの減衰則が全部そろっている（1/n / 1/n² / 低次のみ）")
    def _():
        ids = {o["id"] for o in cfg["candidates"]["decay_law"]["options"]}
        missing = {"inv_n", "inv_n2", "low_only"} - ids
        if missing:
            raise Fail(f"B5 の聴き比べに要る候補が無い: {sorted(missing)}（S3-D14）")

    # ---- 分離案（S3-D13） --------------------------------------------------
    @add("★ 分離案のレートが禁止帯（0.5–20 Hz / 15–70 Hz）に入っていない")
    def _():
        for p in plans:
            for r in p.get("rates_hz", []):
                for lo, hi in FORBIDDEN_MOD_BANDS:
                    if in_band(r, lo, hi):
                        raise Fail(f"{p['id']} の {r} Hz が禁止帯 {lo}–{hi} Hz に入っている")

    @add("★ A 案が状態帯（0.001–0.02 Hz）より 1 桁以上遅い（S3-D13 の A 案の定義）")
    def _():
        a = next((p for p in plans if p["id"] == "plan_a"), None)
        if a is None:
            raise Fail("plan_a が無い")
        limit = STATE_WAVE_BAND[0] / 2.0  # 状態帯の下端 0.001 Hz の 1/2 = 0.0005 Hz
        for r in a.get("rates_hz", []):
            if r > limit:
                raise Fail(
                    f"plan_a の {r} Hz が {limit} Hz より速い。"
                    " A 案は『状態帯より 1 桁以上遅く』が定義（S3-D13）"
                )

    @add("★ B / C 案が振幅を動かしていない（次元で分ける = 音色のみ）")
    def _():
        for pid in ("plan_b", "plan_c"):
            p = next((x for x in plans if x["id"] == pid), None)
            if p is None:
                raise Fail(f"{pid} が無い")
            if p["dimension"] != "tilt":
                raise Fail(f"{pid} の dimension={p['dimension']} が tilt でない")
            if p.get("depth_db", 0) != 0:
                raise Fail(
                    f"{pid} の depth_db={p['depth_db']} が 0 でない。"
                    " ★ 振幅も動かすなら『次元で分ける』ではなくなる"
                )
            if not p.get("tilt_depth", 0) > 0:
                raise Fail(f"{pid} の tilt_depth が 0（音色が動かない = 案として成立しない）")

    @add("★ C 案が A 案と同じだけ遅い（『両方』の定義）")
    def _():
        a = next(x for x in plans if x["id"] == "plan_a")
        c = next(x for x in plans if x["id"] == "plan_c")
        if sorted(c.get("rates_hz", [])) != sorted(a.get("rates_hz", [])):
            raise Fail(
                f"plan_c の rates={c.get('rates_hz')} が plan_a の {a.get('rates_hz')} と違う。"
                " C 案は『遅くしたうえで次元も分ける』（S3-D13）"
            )

    @add("★ 分離案の反復周期が試聴時間より十分長い（★ コメントを信じず Fraction で計算する）")
    def _():
        for p in plans:
            rates = p.get("rates_hz", [])
            if not rates:
                continue
            if len(rates) < 2:
                raise Fail(
                    f"{p['id']} が単一正弦。★ 単一だと『周期的な強弱』そのもので spec §2 の禁止事項に当たる"
                )
            per = repeat_period_s(rates)
            if per < LISTEN_S * REPEAT_MARGIN:
                raise Fail(
                    f"{p['id']} の反復周期 {per:.0f} s が試聴 {LISTEN_S:.0f} s の"
                    f" {REPEAT_MARGIN} 倍未満"
                )

    @add("★ 自律変異を持つ案には spec_compliant=false の印が付いている")
    def _():
        for p in plans:
            has_drift = bool(p.get("rates_hz")) and p["dimension"] != "none"
            if has_drift and p.get("spec_compliant") is not False:
                raise Fail(
                    f"{p['id']} は自律変異を持つのに spec_compliant={p.get('spec_compliant')}。"
                    " ★ 逸脱の印を消さない（S3-D10 と同じ扱い）"
                )
            if not has_drift and p.get("spec_compliant") is not True:
                raise Fail(f"{p['id']} は自律変異が無いのに spec_compliant が true でない")

    @add("★ 対照（自律変異なし）が用意されている")
    def _():
        n = next((p for p in plans if p["dimension"] == "none"), None)
        if n is None:
            raise Fail("自律変異なしの対照が無い。★ 対照が無いと『装置が壊れている』を切り分けられない")

    # ---- 層 2（spec §2 / §9-6） -------------------------------------------
    @add("★ 粒子率の下限が spec §2 の 100 grains/s である")
    def _():
        if float(cfg["spec_anchors"]["grain_rate_floor_per_s"]) != GRAIN_FLOOR:
            raise Fail(f"下限が {cfg['spec_anchors']['grain_rate_floor_per_s']}（spec §2 は 100）")
        if float(L2["rate_min_per_s"]) < GRAIN_FLOOR:
            raise Fail(
                f"データマッピングの下端 {L2['rate_min_per_s']} が下限 {GRAIN_FLOOR} を割っている。"
                " ★ 状態が下がっただけで分節側へ落ちてはならない"
            )

    @add("★ 下限を割った候補が実在する（引き継ぎ §4a: 逆検査と同じ思想）")
    def _():
        below = [r for r in L2["below_floor_presets_per_s"] if r < GRAIN_FLOOR]
        if len(below) < 2:
            raise Fail(
                f"下限割れの候補が {len(below)} 個しかない。"
                " ★ 下限が守られていることは、下限を割ってみせることでしか耳に示せない"
            )
        if GRAIN_FLOOR not in [float(r) for r in L2["below_floor_presets_per_s"]]:
            raise Fail("下限そのもの（100 grains/s）の候補が無い（比較の基準が消える）")

    @add("★ 粒の重なりが 1 枚を下回らない（下限では）")
    def _():
        overlap = GRAIN_FLOOR * L2["grain_ms"] / 1000.0
        if overlap < 1.0:
            raise Fail(
                f"下限 {GRAIN_FLOOR} grains/s × 粒長 {L2['grain_ms']} ms で重なり {overlap:.2f} 枚。"
                " ★ 1 を割ると粒間に無音が生じ、それ自体が分節になる"
            )

    @add("★ 粒の帯域が Nyquist を大きく下回る（実時間 48 kHz / 検算 8 kHz の両方）")
    def _():
        top = L2["center_hz"] * (2 ** (L2["spread_cents"] / 1200.0))
        for sr in (48000.0, float(ST["sample_rate_hz"])):
            if top > sr / 2 * 0.9:
                raise Fail(f"粒の上端 {top:.0f} Hz が {sr:.0f} Hz の Nyquist に近すぎる")

    @add("Worklet の同時発音上限が最大粒子率を賄える")
    def _():
        m = re.search(r"const\s+MAX_VOICES\s*=\s*(\d+)", worklet)
        if not m:
            raise Fail("grain-processor.js の MAX_VOICES を読めない")
        need = L2["rate_max_per_s"] * L2["grain_ms"] / 1000.0
        if int(m.group(1)) < need * 4:
            raise Fail(f"MAX_VOICES={m.group(1)} が必要数 {need:.0f} の 4 倍未満（落粒の恐れ）")

    @add("★ Worklet が seed 固定である（Math.random() を使っていない）")
    def _():
        # ⚠️★ コメントを剥がしてから見る —— 剥がさないと
        #    「Math.random() を使わない」という**注記そのもの**に反応して赤くなる（実測で踏んだ）。
        #    ★ 検査が自分の説明文に反応する形は、silent pass の裏返しである。
        if "Math.random" in strip_js_comments(worklet):
            raise Fail(
                "grain-processor.js が Math.random() を使っている。"
                " ★ グラニュラー合成は乱数を使うので seed を固定する（D18 / S3-D15）"
            )
        if "mulberry32" not in worklet:
            raise Fail("seed 固定 PRNG（mulberry32）が無い")

    @add("★★★ Worklet がゲインを二重に持たない（実測で無音を作った形）")
    def _():
        # ⚠️★★★ 2026-08-12 の実測: Worklet 内部に既定 0 の `gain` AudioParam があり、
        #   player は外部 GainNode だけを設定していたため **層 2 が RMS 0 の完全な無音**になった。
        #   ★ 静的検査 56 件が全部緑のまま通り、捕まえたのは陽性対照だけだった。
        #   → ★ **音量の制御点は 1 つ**（外部 GainNode）。Worklet に戻さない。
        m = re.search(r"parameterDescriptors\(\)\s*\{.*?\n\s*\}", worklet, re.S)
        if not m:
            raise Fail("parameterDescriptors が読めない")
        names = set(re.findall(r'name:\s*"(\w+)"', m.group(0)))
        if "gain" in names:
            raise Fail(
                "Worklet が gain AudioParam を持っている。★ 外部 GainNode と二重になり、"
                "片方だけ設定すると無音のまま検査が緑になる（2026-08-12 に実測）"
            )
        if names != {"rate"}:
            raise Fail(f"parameterDescriptors が {sorted(names)}。★ rate だけにする")

    @add("★★★ player が『層が両方とも鳴っているか』を対照つきで測る検査を持つ")
    def _():
        body = strip_js_comments(html)
        # ⚠️★ 部分一致で探さない —— `renderRmsGone` でも通ってしまう（meta 検査が実測で捕まえた）。
        #    ★ **定義と呼び出しの両方**を要求する（Step 3 の音量スライダ silent pass と同じ緩さ）。
        if "function renderRms(" not in body:
            raise Fail("層ごとの RMS を測る renderRms() の定義が無い")
        if "renderRms({" not in body:
            raise Fail("renderRms() が呼ばれていない（定義だけあって使われていない）")
        if "層 0 単体 RMS" not in html or "層 2 単体 RMS" not in html:
            raise Fail(
                "層 0 単体と層 2 単体を**両方**測っていない。"
                " ★ 片方だけでは『無音』と『測定が死んでいる』を区別できない"
            )

    @add("★ Worklet が Hann 窓を掛けている（粒頭にクリックを立てない）")
    def _():
        body = strip_js_comments(worklet)
        if "0.5 - 0.5 * Math.cos(2 * Math.PI * p)" not in body:
            raise Fail("Hann 窓の式が見つからない。★ 端点が 0 でない窓はオンセットを作る")

    @add("★ Worklet が発火間隔にジッタを入れている（等間隔は『拍』そのもの）")
    def _():
        if not (0.1 <= float(L2.get("jitter", 0)) <= 1.0):
            raise Fail(f"jitter={L2.get('jitter')} が 0.1–1.0 の外（等間隔は spec §2 の禁止事項）")
        if "this.jitter" not in worklet:
            raise Fail("Worklet がジッタを使っていない")

    @add("★ player と Worklet の processor 名が一致する")
    def _():
        if 'registerProcessor("grain-processor"' not in worklet:
            raise Fail("grain-processor.js が registerProcessor('grain-processor') を呼んでいない")
        if 'new AudioWorkletNode(ctx, "grain-processor"' not in html:
            raise Fail("player が grain-processor を生成していない")

    @add("★ SEED ファイルに config と同じ実際の seed が書かれている")
    def _():
        if not seed_text.strip():
            raise Fail("SEED ファイルが無い/空（reproducibility-discipline ルール 2）")
        nums = {int(x) for x in re.findall(r"\b(\d{4,})\b", seed_text)}
        for key, val in (("layer2.seed", L2["seed"]), ("blind_test.order_seed", BT["order_seed"])):
            if int(val) not in nums:
                raise Fail(f"SEED に {key}={val} が書かれていない（★ 実際の seed を書く）")

    # ---- 平滑化（spec §1.3・交渉不可） -------------------------------------
    @add("★ 表現層の平滑化 τ >= 60 s（spec §1.3・交渉不可）")
    def _():
        if float(cfg["mapping"]["tau_s"]) < TAU_MIN_S:
            raise Fail(f"tau_s={cfg['mapping']['tau_s']} が下限 {TAU_MIN_S} を割っている")
        if float(cfg["spec_anchors"]["tau_min_s"]) != TAU_MIN_S:
            raise Fail("spec_anchors.tau_min_s が 60 でない")

    @add("★★★ 合成注入の遷移が raised-cosine で、トライアル内に完全到達する")
    def _():
        # ⚠️★ S4-D5 は一次遅れと決めたが、レビューで欠点が出て raised-cosine に替えた。
        #    ★ 「緩めた」のではない —— 一次遅れは t=0 で傾きが最大（導関数に角がある）のに対し
        #      raised-cosine は始端・終端の傾きが 0 で、spec §2 の「✗ オンセット」に対して厳しい。
        #      かつ transition_s で**完全に到達する**ので catch トライアルに残留が漏れない。
        body = strip_js_comments(html)
        if "0.5 - 0.5 * Math.cos(Math.PI * u)" not in body:
            raise Fail("raised-cosine の遷移が player に無い")
        tr = float(cfg["mapping"]["transition_s"])
        if tr < TAU_MIN_S:
            raise Fail(f"transition_s={tr} が spec §1.3 の下限 {TAU_MIN_S} を割っている")
        if tr > float(BT["trial_seconds"]):
            raise Fail(
                f"transition_s={tr} が trial_seconds={BT['trial_seconds']} より長い。"
                " ★ トライアル内に到達しないと残留が次へ漏れ、catch が『何も動かない』でなくなる"
            )
        # ★ 帯域も同じ検査の中で計算しておく（★ コメントを信じない）。
        #   ⚠️ これは上の tau_min から**含意される**ので単独の検査にはしない
        #     （単独にすると「原理的に赤にできない検査」= 空回りが 1 件増える）。
        f = 1.0 / tr
        for lo, hi in FORBIDDEN_MOD_BANDS:
            if in_band(f, lo, hi):
                raise Fail(f"遷移の帯域 {f:.4f} Hz が禁止帯 {lo}–{hi} Hz に入っている")
        if f > STATE_WAVE_BAND[1]:
            raise Fail(f"遷移の帯域 {f:.4f} Hz が状態の波の上限 {STATE_WAVE_BAND[1]} Hz を超えている")

    @add("★ 盲検の振幅が往復とも同じである（1 回目だけ半分にならない）")
    def _():
        d2 = float(BT["layer2_step_scale"])
        if not 0 < d2 <= 1.0:
            raise Fail(f"layer2_step_scale={d2} が (0, 1] の外")
        body = strip_js_comments(html)
        # ★ config のキーが player から**実際に参照されている**ことを要求する
        #   （以前 layer2_step_scale はどこからも読まれていなかった＝設定が効かない状態だった）
        # ⚠️★ 「どこかに出てくる」では足りない —— ★ **トライアルの刺激を決める場所で**参照されていること。
        #    （meta 検査が実測で捕まえた: 初期化側に残っていると片方を消しても緑になる）
        nt = strip_js_comments(extract_function(html, "nextTrial"))
        for key in ("layer0_step_scale", "layer2_step_scale"):
            if ("BT." + key) not in nt:
                raise Fail(f"config の {key} が nextTrial() から参照されていない（設定が効かない）")
        if "0.5 - d2 / 2" not in body or "0.5 + d2 / 2" not in body:
            raise Fail("層 2 のトグルが中央対称になっていない")
        # ⚠️★★★ 字面だけを見ても足りない —— 式が対称でも **静止点が中央だと 1 回目だけ半分**になる
        #    （実測で踏んだ: deltas = [0.35, -0.7, 0.7, -0.7]）。★ **列を実際に回して確かめる。**
        m = re.search(r"trL2 = new Transition\(CFG\.mapping\.transition_s,\s*([^)]+)\)", html)
        if not m:
            raise Fail("trL2 の初期化が読めない")
        init_src = m.group(1).strip()
        if "0.5" == init_src:
            raise Fail("層 2 の静止点が中央 0.5 になっている（1 回目のトライアルだけ変化量が半分になる）")
        v = 0.5 - d2 / 2 if "layer2_step_scale / 2" in init_src else None
        if v is None:
            raise Fail(f"層 2 の静止点 '{init_src}' を検査できない（式を変えたら検査も直す）")
        deltas = []
        for _ in range(4):
            nv = 0.5 - d2 / 2 if v > 0.5 else 0.5 + d2 / 2
            deltas.append(round(abs(nv - v), 6)); v = nv
        if len(set(deltas)) != 1:
            raise Fail(f"往復の変化量が揃っていない: {deltas}（案の比較にバイアスが入る）")

    @add("★★★ 見本モードが層 2 を実際に握る（no-op になっていない）")
    def _():
        # ⚠️★ レビューが実測で見つけた欠陥: `currentRate()` の条件に demoActive が無く、
        #    見本の「状態を変える」が**完全な no-op** だった（UI は「変えました」と表示していた）。
        seg = strip_js_comments(extract_function(html, "currentRate"))
        if "demoActive" not in seg:
            raise Fail("currentRate() が demoActive を見ていない（見本の層 2 が no-op になる）")
        demo = strip_js_comments(extract_function(html, "demo"))
        if "demoActive = true" not in demo:
            raise Fail("demo() が demoActive を立てていない（見本の層 2 が no-op になる）")
        if "trL2.set(" not in demo:
            raise Fail("demo() が層 2 の遷移器を動かしていない")

    @add("★★★ 粒子率の書き手が 1 つである（データ駆動の自動化を消さない）")
    def _():
        # ⚠️★ レビューが実測で見つけた欠陥: control() がデータ駆動中も cancelScheduledValues() を
        #    打ち、scheduleAhead() が積んだ自動化を 50 ms ごとに全消ししていた。
        #    ★ 粒子率が定数に張り付き、B8（系統 A/B）と B3（carry/restart）が測れなかった。
        seg = strip_js_comments(extract_function(html, "control"))
        if "isDataDriven()" not in seg:
            raise Fail("control() がデータ駆動中かを見ていない（自動化を全消しする）")
        if "!isDataDriven()" not in seg:
            raise Fail("control() がデータ駆動中に粒子率を書かない形になっていない")

    @add("★★★ transport が再入で壊れない（[P71] 止められること）")
    def _():
        body = strip_js_comments(html)
        seg = strip_js_comments(extract_function(html, "play"))
        if "playing || starting" not in seg:
            raise Fail("play() に再入ガードが無い（2 回押すと AudioContext が 2 つ生き、止められなくなる）")
        seg2 = strip_js_comments(extract_function(html, "stop"))
        if "dyingCtx" not in seg2 or "ctx === dyingCtx" not in seg2:
            raise Fail("stop() の後片付けが閉じる対象を固定していない（新しい ctx を閉じうる）")

    @add("★★★ フェードイン中でも音量が効く（[P71] 音量を変えられること）")
    def _():
        # ⚠️★ 予約済みランプを打ち切らないと、スライダを動かしても数秒後に必ず元へ戻る。
        i = html.find('$("vol").addEventListener("input"')
        if i < 0:
            raise Fail("音量ハンドラが見つからない")
        seg = strip_js_comments(html[i:i + 1400])
        # ⚠️★ 「文字列が在るか」だけでは弱い —— if ガードを false にしても本文中に残ってしまう
        #    （meta 検査が実測で捕まえた）。★ **ガードと呼び出しの両方**を要求する。
        for need in ("if (g.cancelAndHoldAtTime)", "g.cancelAndHoldAtTime(now)",
                     "cancelScheduledValues(now)"):
            if need not in seg:
                raise Fail(f"音量変更が予約済みのフェードインランプを打ち切っていない（{need} が無い）")

    @add("★ 盲検中に刺激を決める UI が固定される")
    def _():
        body = strip_js_comments(html)
        if "function lockUI(" not in body:
            raise Fail("lockUI() が無い（盲検中に案を変えられてしまう）")
        if "lockUI(true)" not in body or "lockUI(false)" not in body:
            raise Fail("lockUI() の掛け外しが揃っていない")
        if "bt.running ? optById(CFG.separation_plans.options, bt.plan)" not in body:
            raise Fail("盲検中の深さ適用が bt.plan で固定されていない")

    @add("★ 検証専用の傾斜レートが実時間グラフに入らない")
    def _():
        body = strip_js_comments(html)
        if "function allPlanRates(includeProbe)" not in body:
            raise Fail("allPlanRates() が検証用レートを分けていない")
        seg = strip_js_comments(extract_function(html, "startAudio"))
        if "allPlanRates(true)" in seg:
            raise Fail("実時間再生に検証専用レートが入っている（config の記述と実体がずれる）")
        # ★ それでも万一入った場合に備え、検証用レートも禁止帯検査の対象にする
        for lo, hi in FORBIDDEN_MOD_BANDS:
            if in_band(float(ST["tilt_probe_rate_hz"]), lo, hi):
                raise Fail(f"tilt_probe_rate_hz が禁止帯 {lo}–{hi} Hz に入っている")

    @add("★ 系統 A/B の切替が CSV に反映される")
    def _():
        body = strip_js_comments(html)
        if "function reparseCsv(" not in body or "reparseCsv()" not in body:
            raise Fail("系統を切り替えても CSV を読み直していない（前の列が鳴り続ける）")
        if "_gapCache = null" not in body:
            raise Fail("CSV 読み直し時に _gapCache を捨てていない（行数が同じ別ファイルで誤る）")

    @add("系統 A / 系統 B が両方ある（spec §3）")
    def _():
        ids = {p["id"] for p in cfg["mapping"]["pathways"]}
        if ids != {"A", "B"}:
            raise Fail(f"pathways={sorted(ids)}。★ A と B の両方を作って聴き比べる（spec §3）")
        b = next(p for p in cfg["mapping"]["pathways"] if p["id"] == "B")
        if b["column"] not in {"f1", "f3", "f4", "f5", "f6"}:
            raise Fail(
                f"系統 B の列 {b['column']} が f1–f6 でない。"
                " ★ 系統 B は HMM の前段の観測量でなければ GATE3 と無関係にならない（S4-D6）"
            )
        a = next(p for p in cfg["mapping"]["pathways"] if p["id"] == "A")
        if a["column"] not in {"ewma_x", "ewma_y", "p_flow", "p_inc", "p_stuck"}:
            raise Fail(f"系統 A の列 {a['column']} が推定経由の量でない")

    @add("★ B3: 離席復帰の 2 案があり、既定が carry のまま（既定を勝手に反転させない・S3-D6）")
    def _():
        gb = cfg["mapping"]["gap_behavior"]
        ids = {o["id"] for o in gb["options"]}
        if ids != {"carry", "restart"}:
            raise Fail(f"gap_behavior の候補が {sorted(ids)}")
        if gb["default"] != "carry":
            raise Fail("既定が carry でない。★ S0-D11 の実装（値を持ち越す）を既定として残す")

    # ---- 盲検（S4-D4） -----------------------------------------------------
    @add("★ 盲検の内訳が総数と一致し、catch が含まれている")
    def _():
        comp = BT["composition"]
        total = comp["layer0"] + comp["layer2"] + comp["catch"]
        if total != BT["trials_per_plan"]:
            raise Fail(f"内訳の合計 {total} != trials_per_plan {BT['trials_per_plan']}")
        if comp["catch"] < 1:
            raise Fail("catch が 0。★ 『いつも何か変わったと答える』応答バイアスを検出できない")
        if comp["layer0"] != comp["layer2"]:
            raise Fail(
                f"層 0 {comp['layer0']} 回 / 層 2 {comp['layer2']} 回で偏っている。"
                " ★ 偏ると『多いほうに答える』だけで正答率が上がる"
            )

    @add("★ 採点対象が catch を除いた数と一致する")
    def _():
        comp = BT["composition"]
        if BT["scored_trials"] != comp["layer0"] + comp["layer2"]:
            raise Fail(
                f"scored_trials={BT['scored_trials']} が層 0+層 2 = "
                f"{comp['layer0'] + comp['layer2']} と違う（catch は採点しない）"
            )

    @add("★ 閾値の二項確率が 0.05 未満である（★ コメントを信じず計算する）")
    def _():
        k, n = BT["pass_threshold_correct"], BT["scored_trials"]
        if k > n:
            raise Fail(f"閾値 {k} が採点数 {n} を超えている")
        p = binom_tail(k, n, 0.5)
        if p >= 0.05:
            raise Fail(f"閾値 {k}/{n} の片側 p={p:.4f} が 0.05 以上（案を残す根拠にならない）")

    @add("★ トライアル長が平滑化の時定数以上である（短いと『届いていない』と混ざる）")
    def _():
        if float(BT["trial_seconds"]) < float(cfg["mapping"]["tau_s"]):
            raise Fail(
                f"trial_seconds={BT['trial_seconds']} が tau_s={cfg['mapping']['tau_s']} 未満。"
                " ★ 1 時定数（63% 到達）を待たずに問うと『案が悪い』と『まだ届いていない』が区別できない"
            )

    @add("★ 回答に『わからない』がある（強制的に当てずっぽうをさせない）")
    def _():
        ids = {c["id"] for c in BT["choices"]}
        if ids != {"layer0", "layer2", "unsure"}:
            raise Fail(f"choices={sorted(ids)}。★ layer0 / layer2 / unsure の 3 択（S4-D4）")

    @add("★ player が途中で正誤を出さない（盲検が壊れない）")
    def _():
        body = strip_js_comments(html)
        m = re.search(r"function answer\(choice\)\s*\{.*?\n\}", html, re.S)
        if not m:
            raise Fail("answer() が見つからない")
        seg = strip_js_comments(m.group(0))
        for bad in ("正解", "不正解", "correct ?", "pass", "fail"):
            if bad in seg:
                raise Fail(f"answer() が正誤らしき文字列 '{bad}' を出している（★ 最後まで出さない）")
        if "finishBlind" not in body:
            raise Fail("結果をまとめて出す finishBlind() が無い")

    # ---- [P71] 要件 1（交渉不可） ------------------------------------------
    # ⚠️★★★ Step 3 でここが silent pass を出した（id を緩い正規表現で探していたため、
    #   id="vol-gone" に書き換えても緑のままだった）。★ 厳密一致で書く。
    @add("★★★ [P71] 停止ボタンが player に実在する（交渉不可）")
    def _():
        if 'id="btn-stop"' not in html:
            raise Fail('id="btn-stop" が player に無い（spec §5 要件 1 は交渉不可）')
        if 'addEventListener("click", stop)' not in strip_js_comments(html):
            raise Fail("停止ボタンに stop() が結線されていない")

    @add("★★★ [P71] 音量スライダが player に実在する（交渉不可）")
    def _():
        if 'id="vol"' not in html:
            raise Fail('id="vol" が player に無い（spec §5 要件 1 は交渉不可）')
        if 'type="range"' not in html:
            raise Fail("音量が range 入力になっていない")
        if "$(\"vol\").addEventListener(\"input\"" not in strip_js_comments(html):
            raise Fail("音量スライダに input ハンドラが結線されていない")

    @add("★ 停止がランプ経由である（即時 stop() でオンセットを作らない）")
    def _():
        seg = extract_function(html, "stop")
        if "exponentialRampToValueAtTime" not in seg:
            raise Fail("stop() にランプが無い（spec §2 ✗オンセットを停止時に作る）")

    @add("★ 音量変更が段差にならない（setTargetAtTime を使う）")
    def _():
        i = html.find('$("vol").addEventListener("input"')
        if i < 0:
            raise Fail("音量ハンドラが見つからない")
        seg = strip_js_comments(html[i:i + 1400])
        if "setTargetAtTime(volTarget" not in seg:
            raise Fail("音量変更が setTargetAtTime を通っていない")
        if "volume_time_constant_s" not in seg:
            raise Fail("音量の時定数が config から来ていない")

    # ---- S4-D8: 層 0 の 2 実装防止 ----------------------------------------
    @add("★★★ S4-D8: 層 0 のコアが layer0.html と一致している（2 実装になっていない）")
    def _():
        diffs = []
        for name in LAYER0_CORE_FUNCS:
            a = strip_js_comments(extract_function(html, name))
            b = strip_js_comments(extract_function(step3_html, name))
            if a != b:
                diffs.append(name)
        for name in LAYER0_CORE_CONSTS:
            a = strip_js_comments(extract_const(html, name))
            b = strip_js_comments(extract_const(step3_html, name))
            if a != b:
                diffs.append(name)
        if diffs:
            raise Fail(
                f"層 0 のコアが Step 3 と乖離している: {diffs}。"
                " ★ 赤を消すために比較対象を減らさない。Step 3 側にも同じ変更を入れる（S4-D8）"
            )

    @add("★ S4-D8 の比較対象が痩せていない（検査自体の空回り防止）")
    def _():
        if len(LAYER0_CORE_FUNCS) + len(LAYER0_CORE_CONSTS) < 9:
            raise Fail("比較対象が 9 個未満。★ 検査を通すために対象を削っていないか")
        if "buildGraph" not in LAYER0_CORE_FUNCS:
            raise Fail("音を作る本体 buildGraph が比較対象に入っていない")
        if "LAYER0-CORE:BEGIN" not in html or "LAYER0-CORE:END" not in html:
            raise Fail("player に LAYER0-CORE 区画の印が無い（編集者への警告が消えている）")

    # ---- 検算の健全性（S0-D8 / Step 3 の失敗の再来防止） -------------------
    @add("検算の分解能が probe 線の間隔を分離できる（Hann の主ローブ幅で見る）")
    def _():
        lines = sorted(ST["probe_lines_hz"])
        if len(lines) < 2:
            raise Fail("probe_lines_hz が 2 本未満")
        gap = min(b - a for a, b in zip(lines, lines[1:]))
        # ★ Step 3 は Rayleigh（gap >= 1/T）で見ていたが、★ **窓は Hann である**。
        #   Hann の主ローブは片側 2/T あるので、隣の線が主ローブに入らないためには gap >= 2/T が要る。
        #   ⚠️ 本 config はちょうど gap·T = 2.0（0.005 Hz × 400 s）＝ **境界そのもの**なので、
        #     ★ 浮動小数の丸めで落ちないよう相対誤差だけ許す（基準は緩めていない）。
        bins = gap * ST["render_seconds"]
        if bins < 2.0 - 1e-9:
            raise Fail(
                f"probe 線の間隔 {gap:.5f} Hz は分解能 {1.0/ST['render_seconds']:.5f} Hz の"
                f" {bins:.2f} 倍しかない（Hann の主ローブに埋まる。>= 2.0 が要る）"
            )

    @add("★ 包絡の間引き後 Nyquist が最大の参照線を上回る（Step 3 の『測定不能を数字で出した』失敗の再来防止）")
    def _():
        env_fs = ST["sample_rate_hz"] / ST["env_decim"]
        top = max(ST["reference_lines_hz"])
        if env_fs / 2 <= top:
            raise Fail(
                f"包絡レート {env_fs} Hz の Nyquist {env_fs/2} Hz が参照線 {top} Hz 以下。"
                " ★ 測れない周波数に数字を出すことになる"
            )

    @add("★ 間引きの sinc 補正が全参照線で信用できる（零点で割らない）")
    def _():
        for f in list(ST["reference_lines_hz"]) + list(ST["probe_lines_hz"]):
            a = math.pi * f * ST["env_decim"] / ST["sample_rate_hz"]
            g = 1.0 if a == 0 else math.sin(a) / a
            if abs(g) < ST["sinc_min"]:
                raise Fail(f"{f} Hz の sinc 補正 {g:.3f} が下限 {ST['sinc_min']} 未満（零点に近い）")

    @add("★ 包絡検波器のカットオフが粒子率の線より上にある（測っているつもりで落とさない）")
    def _():
        fc = ST["env_alpha_fast"] * ST["sample_rate_hz"] / (2 * math.pi)
        need = max(L2["below_floor_presets_per_s"])
        if fc < need:
            raise Fail(f"fast 検波器のカットオフ {fc:.0f} Hz が最大粒子率 {need} Hz より下")
        fc_s = ST["env_alpha_slow"] * ST["sample_rate_hz"] / (2 * math.pi)
        if fc_s < ST["tilt_probe_rate_hz"] * 2:
            raise Fail(f"slow 検波器のカットオフ {fc_s:.2f} Hz が傾斜プローブに対して低すぎる")

    @add("★ 傾斜プローブが『実レートではない』と明示されている")
    def _():
        why = " ".join(ST.get("_tilt_probe_why", []))
        if "実レート" not in why or "機構" not in why:
            raise Fail("_tilt_probe_why が実レートでないことを明示していない（★ 測ったと誤読される）")
        if ST["tilt_probe_rate_hz"] < 4.0 / ST["render_seconds"]:
            raise Fail("傾斜プローブがレンダ長で分解できない（主ローブに埋まる）")

    @add("判定閾値が S0-D7 の基準（-60 dB）から緩められていない")
    def _():
        if float(ST["pass_threshold_db"]) > -60.0:
            raise Fail(f"pass_threshold_db={ST['pass_threshold_db']} が -60 dB より緩い")

    @add("★ 陽性対照が状態の波の帯域に置かれている")
    def _():
        f = ST["positive_control_hz"]
        if not in_band(f, *STATE_WAVE_BAND):
            raise Fail(f"陽性対照 {f} Hz が状態帯 {STATE_WAVE_BAND} の外")

    @add("player が窓なし DFT を持っていない（S0-D8）")
    def _():
        body = strip_js_comments(html)
        if "hannAmplitude" not in body:
            raise Fail("Hann 窓付き DFT が無い")
        if re.search(r"function\s+\w*[Nn]oWindow", body) or "window: false" in body:
            raise Fail("窓なし DFT らしき経路がある（S0-D8: 符号が逆になる）")

    @add("★ 逆検査（4 Hz 注入）が player に実在する")
    def _():
        if "sabotage" not in html or 'id="btn-sabotage"' not in html:
            raise Fail("逆検査のボタン/経路が無い。★ 検査が空回りしていないことを示せない")

    # ---- 一般（player の衛生） ---------------------------------------------
    @add("player が外部リソースを読まない")
    def _():
        for pat, what in (
            (r"<script[^>]+\bsrc\s*=", "script[src]"),
            (r"<link[^>]+\bhref\s*=", "link[href]"),
            (r"<img\b", "img"),
            (r"<iframe\b", "iframe"),
            (r"https?://(?!127\.0\.0\.1)", "外部 URL"),
        ):
            if re.search(pat, html, re.I):
                raise Fail(f"player に {what} がある（外部送信境界を増やさない）")

    @add("player が alert() を使わない（モーダルはページも自動検証も固める）")
    def _():
        if re.search(r"(^|[^.\w])alert\s*\(", strip_js_comments(html)):
            raise Fail("alert( がある")

    @add("★ 素の await ctx.resume() を待たない（Step 3 で無言で固まった形）")
    def _():
        body = strip_js_comments(html)
        if "Promise.race([ctx.resume()" not in body:
            raise Fail("ctx.resume() が打ち切り付きで待たれていない（S3 の実測: 無期限に固まる）")

    @add("★ AudioWorklet の読み込み失敗を握り潰さない")
    def _():
        body = strip_js_comments(html)
        if "AudioWorklet" not in body or "showTransportError" not in body:
            raise Fail("Worklet の読み込み失敗を画面に出す経路が無い")
        seg = extract_function(html, "startAudio")
        if "ensureWorklet" not in seg or "catch" not in seg:
            raise Fail("startAudio() が Worklet 読み込みの失敗を捕まえていない")
        if "showTransportError" not in seg:
            raise Fail("Worklet 読み込みの失敗が画面に出ない（無言で固まる）")

    @add("player に絶対パス / ユーザー名が混入していない")
    def _():
        for pat in (r"[A-Za-z]:\\\\", r"[A-Za-z]:/Users/", r"/home/[a-z]", r"johnd"):
            if re.search(pat, html) or re.search(pat, worklet):
                raise Fail(f"絶対パス/ユーザー名らしき文字列 {pat} がある")

    @add("★ config が『非周期』と書いていない（有理比なので数学的には必ず反復する）")
    def _():
        if "非周期" in cfg_text:
            raise Fail("config に『非周期』がある。★ 『試聴時間内では繰り返さない』までしか言えない")

    @add("★ 実物音の引用が無い（S3-D14 の禁止を維持）")
    def _():
        body = strip_js_comments(html) + " " + strip_js_comments(worklet)
        for bad in ("decodeAudioData", "createBufferSource", "new Audio(", "fetch(\"http"):
            if bad in body:
                raise Fail(f"外部音源の読み込みらしき経路 {bad} がある（spec §2 ✗実物音の引用）")

    @add("★ paste を落としたことが config に明記されている（S4-D6）")
    def _():
        b = next(p for p in cfg["mapping"]["pathways"] if p["id"] == "B")
        if "paste" not in json.dumps(b, ensure_ascii=False):
            raise Fail("系統 B に paste を落とした旨の注記が無い（★ 満たしていないことを明示する）")

    # ---- 層 2 の作り直し（S4-D12・2026-08-12） ------------------------------
    RW = cfg.get("layer2_rework")

    @add("★ 層 2 作り直しの 3 軸がそろっている（音色 / 密度の写し方 / 密度の幅）")
    def _():
        if not RW:
            raise Fail("layer2_rework が無い")
        for k in ("timbre", "density_cue", "density_span"):
            opts = RW.get(k, {}).get("options")
            if not opts:
                raise Fail(f"{k} の options が無い")
            if len(opts) < 2:
                raise Fail(f"{k} の候補が {len(opts)} 個しかない（比べられない）")

    @add("★ 既定が現行のまま（対照を残す）")
    def _():
        d = RW["defaults"]
        if d != {"timbre": "t_current", "density_cue": "c_texture", "density_span": "s_current"}:
            raise Fail(f"既定が現行でない: {d}。★ 前回の音と比べられなくなる")
        t0 = next(o for o in RW["timbre"]["options"] if o["id"] == "t_current")
        for a, b in (("grain_ms", "grain_ms"), ("center_hz", "center_hz"),
                     ("spread_cents", "spread_cents")):
            if abs(t0[a] - L2[b]) > 1e-9:
                raise Fail(f"対照 t_current が layer2 の実値とずれている: {a} {t0[a]} != {L2[b]}")

    @add("★★ 密度の幅候補が下限 100 grains/s を守っている（[P64]・動かさない）")
    def _():
        floor = cfg["spec_anchors"]["grain_rate_floor_per_s"]
        for o in RW["density_span"]["options"]:
            if o["rate_min_per_s"] < floor:
                raise Fail(f"{o['id']} の下限 {o['rate_min_per_s']} < {floor}")
            if o["rate_max_per_s"] <= o["rate_min_per_s"]:
                raise Fail(f"{o['id']} の上限が下限以下")

    @add("★★ 候補切替の一次遅れが禁止帯より 1 桁以上下（切替自体を変調にしない）")
    def _():
        tau = RW["morph_s"]
        f = 1.0 / (2.0 * math.pi * tau)          # 一次遅れの実効カットオフ
        if f >= 0.05:
            raise Fail(f"morph_s={tau}s → {f:.4f} Hz。禁止帯下端 0.5 Hz の 1/10 (0.05 Hz) 以上")

    @add("★★ 粒の重なりが 1 枚を下回らない（全候補 × 全 span の下限で）")
    def _():
        for t in RW["timbre"]["options"]:
            for s in RW["density_span"]["options"]:
                ov = s["rate_min_per_s"] * t["grain_ms"] / 1000.0
                if ov < 1.0:
                    raise Fail(f"{t['id']}×{s['id']} で重なり {ov:.2f} 枚 < 1（粒間に無音＝分節）")

    @add("★ 全候補の粒の帯域が Nyquist を下回る（実時間 48 kHz / 検算 8 kHz）")
    def _():
        for t in RW["timbre"]["options"]:
            hi = t["center_hz"] * (2.0 ** (t["spread_cents"] / 1200.0))
            for sr in (48000.0, cfg["selftest"].get("offline_sample_rate_hz", 8000.0)):
                if hi >= sr / 2.0:
                    raise Fail(f"{t['id']} の上端 {hi:.0f} Hz が {sr/2:.0f} Hz 以上")

    @add("★★ 音色候補の fact に書いた主ローブ幅・帯域が算術と一致する（doc の drift 防止）")
    def _():
        for t in RW["timbre"]["options"]:
            lobe = 4000.0 / t["grain_ms"]                       # Hann 主ローブ幅 = 4/T
            lo = t["center_hz"] * 2.0 ** (-t["spread_cents"] / 1200.0)
            hi = t["center_hz"] * 2.0 ** (t["spread_cents"] / 1200.0)
            f = t["fact"]
            for want in (f"{round(lobe)} Hz", f"{round(lo)}–{round(hi)} Hz"):
                if want not in f:
                    raise Fail(f"{t['id']} の fact に『{want}』が無い: {f}")

    @add("★★ 密度手がかりの fact に書いた振幅比が overlap^(0.5-exp) と一致する")
    def _():
        span = next(o for o in RW["density_span"]["options"] if o["id"] == "s_current")
        ratio_overlap = span["rate_max_per_s"] / span["rate_min_per_s"]
        for c in RW["density_cue"]["options"]:
            r = ratio_overlap ** (0.5 - c["density_norm_exp"])
            if c["density_norm_exp"] == 0.5:
                if "ほぼ不変" not in c["fact"]:
                    raise Fail("c_texture の fact が『ほぼ不変』と言っていない")
            elif f"{r:.2f}" not in c["fact"] and f"{r:.1f}" not in c["fact"]:
                raise Fail(f"{c['id']}: 期待比 {r:.2f} が fact に無い: {c['fact']}")

    @add("★★★ processor が目標値と現在値を分け、段差でなくランプで移る")
    def _():
        if "this.tgt" not in worklet:
            raise Fail("processor に目標値 this.tgt が無い（段差で切り替わる）")
        if "morphS" not in worklet:
            raise Fail("processor に morphS が無い")
        # ★ 一次遅れの本体（ブロックごとに寄せる）が実在すること
        if "this.tgt.grainSec - this.grainSec" not in worklet:
            raise Fail("grainSec を目標値へ寄せる処理が無い")
        if "this.tgt.normExp - this.normExp" not in worklet:
            raise Fail("normExp を目標値へ寄せる処理が無い（レベル跳ねの原因）")

    @add("★★★ processor の set が未知/不正な鍵を黙って無視しない")
    def _():
        if '"set"' not in worklet:
            raise Fail("processor に set コマンドが無い")
        # ⚠️★ 部分一致だけで見ると `_unknown` へ改名しても素通りする（2026-08-12 の meta で実測）。
        #   ★ **鍵を集める式**と**応答に載せる式**の両方を固定する。
        if "const unknown = Object.keys(p).filter" not in worklet:
            raise Fail("未知の鍵を集める式が無い（黙って無視する形に戻っている）")
        if 'ack: "set", unknown' not in worklet:
            raise Fail("set の応答に unknown を載せていない（黙って落ちる候補が緑になる）")
        if "rejected: bad" not in worklet:
            raise Fail("set の応答に rejected を載せていない")
        if "logLine(\"⚠️ 層 2 の set が一部通っていない" not in html:
            raise Fail("player が set の不通過を握り潰している")

    @add("★★ player が『いま効いている値』を processor から受け取って出す（目標値ではない）")
    def _():
        # ⚠️★ `e.data.cur` の部分一致だけだと、条件を `if (false)` に潰しても
        #   本文中の `e.data.cur.grainMs` が残って素通りする（2026-08-12 の meta で実測）。
        if "if (e.data.cur) {" not in html:
            raise Fail("player が processor の cur を読んでいない（受け取りが潰されている）")
        for el in ("l2-cur-grain", "l2-cur-center", "l2-cur-spread", "l2-cur-norm"):
            if el not in html:
                raise Fail(f"表示要素 {el} が無い")

    @add("★★ player が起動時から選択中の候補で層 2 を作る（既定で作って寄せない）")
    def _():
        if 'grainMs: reworkOpt("timbre").grain_ms' not in html:
            raise Fail("attachLayer2 が config 既定で作っている（候補の音を最初から聴けない）")
        if 'densityNormExp: reworkOpt("dcue").density_norm_exp' not in html:
            raise Fail("attachLayer2 が密度手がかりの選択を無視している")

    @add("★★ 粒子率の幅が『密度の幅』候補から来る（config 直読みが残っていない）")
    def _():
        if "rateMin() + v * (rateMax() - rateMin())" not in html:
            raise Fail("currentRate が候補の幅を使っていない")
        if "L2.rate_min_per_s + v * (L2.rate_max_per_s" in html:
            raise Fail("currentRate に config 直読みの古い式が残っている")

    return checks


# ---------------------------------------------------------------------------
# 実行
# ---------------------------------------------------------------------------
def run_checks(args_tuple, verbose=True) -> tuple[int, int]:
    npass = nfail = 0
    for name, fn in build_checks(*args_tuple):
        try:
            fn()
            npass += 1
            if verbose:
                print(f"  ok    {name}")
        except Fail as e:
            nfail += 1
            print(f"  FAIL  {name}\n          -> {e}")
    return npass, nfail


def first_failure(args_tuple) -> str | None:
    """壊した状態で最初に落ちた検査を「名前 :: 失敗メッセージ」で返す（meta 検査用）。

    ⚠️ **名前だけを返してはならない**——1 つの検査が複数の理由で落ちうるので、
    「期待した理由で落ちたか」を確かめられなくなる（S0-D14 が踏んだ形の再来）。
    """
    for name, fn in build_checks(*args_tuple):
        try:
            fn()
        except Fail as e:
            return f"{name} :: {e}"
    return None


def meta_checks() -> int:
    """★ 壊し方 → 赤くなるべき検査（部分一致）。検査自体が空回りしていないことを実測する。"""
    base = load_sources()
    cfg0, cfg_text0, html0, wk0, py0, s3html0, s3ver0, seed0 = base

    def mut_cfg(fn):
        c = copy.deepcopy(cfg0)
        fn(c)
        return (c, json.dumps(c, ensure_ascii=False), html0, wk0, py0, s3html0, s3ver0, seed0)

    def mut_html(old, new):
        return (cfg0, cfg_text0, html0.replace(old, new), wk0, py0, s3html0, s3ver0, seed0)

    def mut_wk(old, new):
        return (cfg0, cfg_text0, html0, wk0.replace(old, new), py0, s3html0, s3ver0, seed0)

    def plan(c, pid):
        return next(p for p in c["separation_plans"]["options"] if p["id"] == pid)

    cases: list[tuple[str, tuple, str]] = [
        ("版を config 側だけずらす",
         mut_cfg(lambda c: c.update(expr_version="9.9.9-bogus")), "expr_smooth.py"),
        ("Step 3 の config を追随させ忘れる",
         (cfg0, cfg_text0, html0, wk0, py0, s3html0, "0.2.0-step3", seed0), "追随"),
        # ⚠️ 3 箇所すべてを据え置く。★ 1 箇所だけ戻すと**先に一致検査が落ちる**ので
        #    「上がっているか」の検査を試したことにならない（実測で踏んだ）。
        ("版を 3 箇所とも Step 3 のまま据え置く",
         ({**copy.deepcopy(cfg0), "expr_version": PREV_VERSION},
          cfg_text0, html0, wk0, PREV_VERSION, s3html0, PREV_VERSION, seed0),
         "Step 3 の版から上がっている"),
        ("基音を帯の外（130 Hz）にする",
         mut_cfg(lambda c: c["candidates"]["base_hz"]["options"][0].update(hz=130.0)),
         "55–110 Hz 帯"),
        ("減衰則から low_only を消す（B5 が測れなくなる）",
         mut_cfg(lambda c: c["candidates"]["decay_law"]["options"].pop()), "B5"),
        ("非調和な減衰則を足す",
         mut_cfg(lambda c: c["candidates"]["decay_law"]["options"].append(
             {"id": "x", "law": "1/n^1.5", "partials": 8, "label": "x"})), "既知のもの"),
        ("A 案のレートを 4 Hz（最悪の帯域）にする",
         mut_cfg(lambda c: plan(c, "plan_a").update(rates_hz=[4.0, 4.1])), "禁止帯"),
        ("A 案を状態帯の中（0.005 Hz）へ戻す",
         mut_cfg(lambda c: plan(c, "plan_a").update(rates_hz=[0.005, 0.0031])), "より速い"),
        ("B 案に振幅も持たせる（次元が分かれなくなる）",
         mut_cfg(lambda c: plan(c, "plan_b").update(depth_db=1.5)), "次元で分ける"),
        ("B 案の tilt_depth を 0 にする",
         mut_cfg(lambda c: plan(c, "plan_b").update(tilt_depth=0.0)), "tilt_depth"),
        ("C 案のレートを A 案と違うものにする",
         mut_cfg(lambda c: plan(c, "plan_c").update(rates_hz=[0.005, 0.0031])), "両方"),
        # ⚠️ plan_a を単一にすると先に「C 案が A 案と同じだけ遅い」が落ちるので plan_b を壊す
        ("分離案を単一正弦にする",
         mut_cfg(lambda c: plan(c, "plan_b").update(rates_hz=[0.005])), "単一正弦"),
        ("逸脱の印（spec_compliant=false）を消す",
         mut_cfg(lambda c: plan(c, "plan_a").update(spec_compliant=True)), "逸脱の印"),
        ("対照（自律変異なし）を消す",
         mut_cfg(lambda c: c["separation_plans"]["options"].remove(plan(c, "none"))), "対照"),
        ("データマッピングの下端を下限割れにする",
         mut_cfg(lambda c: c["layer2"].update(rate_min_per_s=50.0)), "下限"),
        ("下限割れの候補を消す（逆検査ができなくなる）",
         mut_cfg(lambda c: c["layer2"].update(below_floor_presets_per_s=[100, 200])), "下限割れ"),
        ("粒長を 5 ms にして重なりを 1 枚未満にする",
         mut_cfg(lambda c: c["layer2"].update(grain_ms=5.0)), "重なり"),
        ("τ を 30 s に緩める",
         mut_cfg(lambda c: c["mapping"].update(tau_s=30.0)), "下限"),
        ("系統 B を推定経由の列に差し替える",
         mut_cfg(lambda c: c["mapping"]["pathways"][1].update(column="p_stuck")), "前段の観測量"),
        ("離席復帰の既定を restart に反転させる",
         mut_cfg(lambda c: c["mapping"]["gap_behavior"].update(default="restart")), "carry"),
        ("catch を 0 にする",
         mut_cfg(lambda c: (c["blind_test"]["composition"].update(catch=0),
                            c["blind_test"].update(trials_per_plan=8))), "catch"),
        ("層 0 と層 2 の出題数を偏らせる",
         mut_cfg(lambda c: (c["blind_test"]["composition"].update(layer0=6, layer2=2))), "偏っている"),
        ("閾値を 5/8 に緩める（有意でなくなる）",
         mut_cfg(lambda c: c["blind_test"].update(pass_threshold_correct=5)), "0.05 以上"),
        ("トライアルを 20 s に縮める",
         mut_cfg(lambda c: c["blind_test"].update(trial_seconds=20.0)), "trial_seconds"),
        ("『わからない』を選択肢から消す",
         mut_cfg(lambda c: c["blind_test"]["choices"].pop()), "3 択"),
        ("包絡の間引きを Step 3 の 40 に戻す（粒子率が測れなくなる）",
         mut_cfg(lambda c: c["selftest"].update(env_decim=40)), "Nyquist"),
        ("fast 検波器のカットオフを下げる",
         mut_cfg(lambda c: c["selftest"].update(env_alpha_fast=0.002)), "検波器"),
        ("判定閾値を -40 dB へ緩める",
         mut_cfg(lambda c: c["selftest"].update(pass_threshold_db=-40.0)), "-60 dB"),
        ("レンダ時間を 100 s に縮めて分解能を粗くする",
         mut_cfg(lambda c: c["selftest"].update(render_seconds=100)), "分解能"),
        ("陽性対照を状態帯の外へ出す",
         mut_cfg(lambda c: c["selftest"].update(positive_control_hz=1.0)), "陽性対照"),
        ("傾斜プローブの注記から『実レート』を消す",
         mut_cfg(lambda c: c["selftest"].update(_tilt_probe_why=["ただの注記"])), "実レート"),
        ("config に『非周期』と書く",
         (cfg0, cfg_text0 + "\n非周期\n", html0, wk0, py0, s3html0, s3ver0, seed0), "非周期"),
        ("系統 B の paste 注記を消す",
         mut_cfg(lambda c: c["mapping"]["pathways"][1].pop("_paste_missing")), "paste"),
        ("★ player から停止ボタンを消す",
         mut_html('id="btn-stop"', 'id="btn-gone"'), "btn-stop"),
        ("★ 音量スライダの id を変える（Step 3 の silent pass と同じ壊し方）",
         mut_html('id="vol"', 'id="vol-gone"'), "vol"),
        ("stop() からランプを消す",
         mut_html("graph.master.gain.exponentialRampToValueAtTime(0.0001, now + f);",
                  "graph.master.gain.value = 0;"), "ランプ"),
        ("音量変更を段差にする",
         mut_html("g.setTargetAtTime(volTarget, now,", "g.setValueAtTime(volTarget,"),
         "setTargetAtTime"),
        ("★ 層 0 のコアを書き換える（S4-D8）",
         mut_html('osc.type = "sine";                       // ★ 正弦のみ',
                  'osc.type = "sawtooth";                   // ★ 正弦のみ'), "乖離"),
        ("LAYER0-CORE の印を消す",
         mut_html("LAYER0-CORE:BEGIN", "removed"), "LAYER0-CORE"),
        ("ctx.resume() を素で待つ",
         mut_html("Promise.race([ctx.resume()", "await0([ctx.resume()"), "打ち切り"),
        ("alert() を足す",
         mut_html("function volLinear()", "function _x(){alert(1)}\nfunction volLinear()"), "alert"),
        ("外部スクリプトを読み込む",
         mut_html("<script>\n\"use strict\";", '<script src="https://x/y.js"></script>\n<script>\n"use strict";'),
         "script[src]"),
        ("逆検査のボタンを消す",
         mut_html('id="btn-sabotage"', 'id="btn-none"'), "逆検査"),
        ("外部音源を読む経路を足す",
         mut_html("function volLinear()", "function _y(){ctx.decodeAudioData(0)}\nfunction volLinear()"),
         "実物音"),
        ("★ Worklet に Math.random() を入れる",
         mut_wk("this.rnd = mulberry32(o.seed || 1);", "this.rnd = Math.random;"), "Math.random"),
        ("★ Worklet にゲインの AudioParam を戻す（無音を作った形）",
         mut_wk('{ name: "rate", defaultValue: 100, minValue: 0, maxValue: 2000, automationRate: "a-rate" },',
                '{ name: "rate", defaultValue: 100, minValue: 0, maxValue: 2000, automationRate: "a-rate" },\n'
                '      { name: "gain", defaultValue: 0.0, minValue: 0, maxValue: 1, automationRate: "a-rate" },'),
         "二重"),
        ("★ 層 2 単体の RMS 検査を player から消す",
         mut_html("層 2 単体 RMS ", "けした "), "両方"),
        ("renderRms() を消す",
         mut_html("async function renderRms(", "async function renderRmsGone("), "renderRms"),
        ("Worklet の Hann 窓を矩形にする",
         mut_wk("0.5 - 0.5 * Math.cos(2 * Math.PI * p)", "1.0"), "Hann"),
        ("Worklet の同時発音上限を絞る",
         mut_wk("const MAX_VOICES = 2048;", "const MAX_VOICES = 8;"), "MAX_VOICES"),
        ("processor 名をずらす",
         mut_wk('registerProcessor("grain-processor"', 'registerProcessor("other"'), "registerProcessor"),
        # ---- ★ レビューで見つかった 6 件の HIGH に対応する検査の meta ----
        ("★ 見本の層 2 を no-op に戻す（demoActive を落とす）",
         mut_html("if (bt.running || demoActive || $(\"l2-map\").checked) {",
                  "if (bt.running || $(\"l2-map\").checked) {"), "no-op"),
        ("★ 制御ループがデータ駆動中も粒子率を書く形に戻す",
         mut_html("if (graph.grain && !isDataDriven()) {", "if (graph.grain) {"), "データ駆動"),
        ("★ play() の再入ガードを外す",
         mut_html("if (playing || starting) return;", "if (playing) return;"), "再入ガード"),
        ("★ stop() の後片付けを ctx 固定でなくする",
         mut_html("if (ctx === dyingCtx) {", "if (true) {"), "固定"),
        ("★ 音量変更から打ち切りを外す",
         mut_html("if (g.cancelAndHoldAtTime) {", "if (false) {"), "打ち切"),
        ("★ 遷移を raised-cosine でなくする",
         mut_html("0.5 - 0.5 * Math.cos(Math.PI * u)", "u"), "raised-cosine"),
        ("★ 遷移がトライアルに収まらない長さにする",
         mut_cfg(lambda c: c["mapping"].update(transition_s=120.0)), "trial_seconds"),
        ("★ 盲検の振幅を非対称に戻す（式）",
         mut_html("trL2.set(trL2.to > 0.5 ? 0.5 - d2 / 2 : 0.5 + d2 / 2);",
                  "trL2.set(trL2.to > 0.5 ? 0.15 : 0.85);"), "中央対称"),
        ("★ 層 2 の静止点を中央 0.5 に戻す（1 回目だけ半分になる形）",
         mut_html("trL2 = new Transition(CFG.mapping.transition_s, 0.5 - CFG.blind_test.layer2_step_scale / 2);",
                  "trL2 = new Transition(CFG.mapping.transition_s, 0.5);"), "静止点"),
        ("★ layer2_step_scale を参照しない形に戻す",
         mut_html("const d0 = BT.layer0_step_scale, d2 = BT.layer2_step_scale;",
                  "const d0 = BT.layer0_step_scale, d2 = 0.7;"), "参照されていない"),
        ("★ 盲検中の UI 固定を外す",
         mut_html("  lockUI(true);", "  /* lockUI 外した */"), "掛け外し"),
        ("★ 盲検中の深さを選択中の案で決める形に戻す",
         mut_html("const p = bt.running ? optById(CFG.separation_plans.options, bt.plan) : planOpt();",
                  "const p = planOpt();"), "bt.plan"),
        ("★ 検証専用レートを実時間グラフに入れる",
         # ⚠️ 実時間側（startAudio 内）の 1 箇所だけを差し替える。
         #    ★ 検算側の allPlanRates(true) は残す（そちらは正しい呼び方である）
         (cfg0, cfg_text0,
          html0.replace("allRates: allPlanRates(),", "allRates: allPlanRates(true),", 1),
          wk0, py0, s3html0, s3ver0, seed0),
         "実時間再生に検証専用レート"),
        ("★ 系統切替で CSV を読み直さない形に戻す",
         mut_html("async function reparseCsv(", "async function reparseGone("), "読み直していない"),
        ("SEED から seed を消す",
         (cfg0, cfg_text0, html0, wk0, py0, s3html0, s3ver0, "seed なし"), "SEED"),

        # ---- 層 2 の作り直し（S4-D12） ------------------------------------
        ("★ 既定を新候補にして対照を失う",
         mut_cfg(lambda c: c["layer2_rework"]["defaults"].update(timbre="t_low_long")),
         "既定が現行でない"),
        ("★ 対照 t_current を layer2 の実値からずらす",
         mut_cfg(lambda c: next(o for o in c["layer2_rework"]["timbre"]["options"]
                                if o["id"] == "t_current").update(center_hz=441.0)),
         "対照 t_current が layer2 の実値とずれている"),
        ("★★ 密度の幅の下限を 100 grains/s より下げる",
         mut_cfg(lambda c: next(o for o in c["layer2_rework"]["density_span"]["options"]
                                if o["id"] == "s_wide").update(rate_min_per_s=60.0)),
         "下限"),
        ("★★ 候補切替を速くして禁止帯に近づける（morph_s 1 s）",
         mut_cfg(lambda c: c["layer2_rework"].update(morph_s=1.0)), "禁止帯下端"),
        ("★ 粒長を短くして重なりを 1 枚未満にする",
         mut_cfg(lambda c: next(o for o in c["layer2_rework"]["timbre"]["options"]
                                if o["id"] == "t_high_air").update(grain_ms=5.0)),
         "重なり"),
        ("★★ 音色 fact の数値だけをずらす（doc の drift）",
         mut_cfg(lambda c: next(o for o in c["layer2_rework"]["timbre"]["options"]
                                if o["id"] == "t_low_long").update(fact="主ローブ幅 99 Hz / 帯域 1–2 Hz")),
         "fact に"),
        ("★★ 密度手がかり fact の比だけをずらす",
         mut_cfg(lambda c: next(o for o in c["layer2_rework"]["density_cue"]["options"]
                                if o["id"] == "c_level").update(fact="振幅比 約 9.9 倍")),
         "期待比"),
        ("★★★ processor の目標値を消して段差で切り替える形に戻す",
         mut_wk("this.tgt.normExp - this.normExp", "0 - 0"), "normExp を目標値へ寄せる"),
        ("★★★ processor の set が未知の鍵を黙って無視する形に戻す",
         mut_wk("const unknown = Object.keys(p)", "const _unknown = Object.keys(p)"),
         "未知の鍵を集める式"),
        ("★★★ set の応答から unknown を落とす（集めるが返さない）",
         mut_wk('ack: "set", unknown', 'ack: "set", _dropped'), "unknown を載せていない"),
        ("★★ player が set の不通過を握り潰す形に戻す",
         mut_html('logLine("⚠️ 層 2 の set が一部通っていない', 'void("'), "握り潰している"),
        ("★★ 層 2 を config 既定で作ってから寄せる形に戻す",
         mut_html('grainMs: reworkOpt("timbre").grain_ms', "grainMs: L2.grain_ms"),
         "config 既定で作っている"),
        ("★★ currentRate に config 直読みの古い式を戻す",
         mut_html("return rateMin() + v * (rateMax() - rateMin());",
                  "return L2.rate_min_per_s + v * (L2.rate_max_per_s - L2.rate_min_per_s);"),
         "候補の幅を使っていない"),
        ("★ 『いま効いている値』の受け取りを消す",
         mut_html("if (e.data.cur) {", "if (false) {"), "cur を読んでいない"),
    ]

    print("== meta 検査（★ 検査を壊して赤くなることの確認） ==")
    npass = nfail = 0
    for label, mutated, expect in cases:
        got = first_failure(mutated)
        if got is None:
            nfail += 1
            print(f"  FAIL  {label}\n          -> 壊したのに全部緑のまま（★ silent pass）")
        elif expect not in got:
            nfail += 1
            print(f"  FAIL  {label}\n          -> 期待 '{expect}' を含まない別の理由で落ちた: {got}")
        else:
            npass += 1
            print(f"  ok    {label}  ->  {got.split(' :: ')[0]}")

    # ★ 検査自体が空回りしていないか（FAIL が 1 件も出ない構成になっていないか）
    if first_failure(base) is not None:
        nfail += 1
        print("  FAIL  ★ 壊していない素の状態で既に赤い（meta 検査の前提が崩れている）")
    print(f"\nmeta: {npass} ok / {nfail} fail")
    return 0 if nfail == 0 else 2


def main() -> int:
    ap = argparse.ArgumentParser(description="Step 4（層 2 粒子）の静的検査")
    ap.add_argument("--selftest", action="store_true",
                    help="★ 検査自体を壊して赤くなることを確かめる（ルール 5b）")
    args = ap.parse_args()

    base = load_sources()
    cfg = base[0]
    print(f"step4 静的検査 — EXPR_VERSION(py)={base[4]} / config={cfg['expr_version']}"
          f" / step3={base[6]}")
    npass, nfail = run_checks(base)
    print(f"\n検査: {npass} ok / {nfail} fail")
    rc = 0 if nfail == 0 else 2
    if args.selftest:
        print()
        rc = meta_checks() or rc
    return rc


if __name__ == "__main__":
    sys.exit(main())
