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
from itertools import combinations
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

# ★★★ 2026-08-14 `/cross-review`（HIGH）——**混入検査を連結で素通りしていた実セッション名**。
#   ⚠️★★★ 混入検査が見るのは**組み立て済みの文字列**だけなので、
#     `"Pnnn" + "_gse_" + "<年月日>_<時分秒>"` の形で書くと **1 バイトも引っかからない。**
#   ⚠️★★★ その形で **実在の識別子が 4 箇所**（run.sh / notes.md / data.md / 検査自身の変異見本）に
#     入っており、⚠️ **本 diff を `/cross-review` に掛けた時点で外部 LLM へ送信された。**
#   ★ 連結そのものは要る（★ 書かないと自己走査が自分の変異データに反応して赤くなる）。
#   → ★ **要るのは連結を消すことではなく「連結しても架空名しか置けない」ことの強制**である。
#     ★ 見本は**この 1 か所だけ**で作り、`_fixtures_hide_no_real_session` が実測で縛る。
# ⚠️ 架空名の条件: (a) `sess` パターン（年 20xx）に**当たること**——当たらないと変異が赤くならない、
#   (b) 実在しえないこと（★ 参加者 999 / 2000-01-01 00:00:00。★ 実データは 2026 年）。
FAKE_SESSION = "P999" + "_gse_" + "20000101_000000"


def _concat_src(sess: str, joiner: str = " + ") -> str:
    """★ セッション名を「連結で書かれた Python ソース」の表記へ組み立て直す。

    ⚠️★★ meta 変異の見本を**リテラルで書けない**ため必要になる ——
    リテラルで書くと `_fixtures_hide_no_real_session` が**自分自身に反応して常に赤くなる**
    （★ この系列で何度も踏んだ「検査が自分の変異データを見ている」型）。

    ★ `joiner` を `" "` にすると **暗黙連結**（`"a" "b"`・`+` 無し）の形になる
      —— ⚠️ 2026-08-14 の `/cross-review` が **これが 2 層とも素通りする**ことを実測した形である。
    """
    q = '"'
    return q + sess[:4] + q + joiner + q + sess[4:9] + q + joiner + q + sess[9:] + q

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


def js_eval_simple(expr: str, env: dict):
    """JS の **三項式 / `===` / `!==` / 文字列リテラル / 識別子 / 括弧** だけを評価する。

    ★★★ 目的（2026-08-14・`code-reviewer` 指摘）: 「上下の均衡」の検査が
    **実装を 1 行も見ずに config だけを見ていた**。★ `to` を常に "B" にする変異でも全部緑だった。
    → ★ **実装のソースから式を取り出して、実際に評価する。**

    ⚠️ わざと非常に狭い文法しか受け付けない。★ 想定外の形は **黙って通さず例外にする**
    （★ 「読めなかったので緑」は、この repo が何度も踏んでいる silent pass そのもの）。
    """
    s = expr.strip()

    def parse(t: str):
        t = t.strip()
        # ★ 三項（★ 最も外側の `?` を、括弧の深さ 0 で探す）
        depth = 0
        for i, ch in enumerate(t):
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
            elif ch == "?" and depth == 0:
                d2 = 0
                for j in range(i + 1, len(t)):
                    c2 = t[j]
                    if c2 == "(":
                        d2 += 1
                    elif c2 == ")":
                        d2 -= 1
                    elif c2 == "?" and d2 == 0:
                        raise ValueError("入れ子の三項が同じ深さにある: " + t)
                    elif c2 == ":" and d2 == 0:
                        return ("?:", parse(t[:i]), parse(t[i + 1:j]), parse(t[j + 1:]))
                raise ValueError("三項の `:` が見つからない: " + t)
        if t.startswith("(") and t.endswith(")"):
            return parse(t[1:-1])
        m = re.match(r"^(.+?)(===|!==)(.+)$", t)
        if m:
            return ("cmp", m.group(2), parse(m.group(1)), parse(m.group(3)))
        m = re.match(r'^"([^"]*)"$|^\'([^\']*)\'$', t)
        if m:
            return ("lit", m.group(1) if m.group(1) is not None else m.group(2))
        if re.match(r"^[A-Za-z_$][\w$]*$", t):
            return ("var", t)
        raise ValueError("読めない部分式: " + t)

    def ev(node):
        k = node[0]
        if k == "lit":
            return node[1]
        if k == "var":
            if node[1] not in env:
                raise ValueError("未知の変数: " + node[1])
            return env[node[1]]
        if k == "cmp":
            a, b = ev(node[2]), ev(node[3])
            return (a == b) if node[1] == "===" else (a != b)
        if k == "?:":
            return ev(node[2]) if ev(node[1]) else ev(node[3])
        raise ValueError("読めない節: " + str(node))

    return ev(parse(s))


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
    # ★★★ 2026-08-14: 混入検査の走査対象（★ **ここで 1 回だけ読む**）。
    #   ⚠️★★★ 検査の中で直接 read_text すると **meta 変異で壊せない**ので、
    #     「検査を書いたら壊して赤くなることを実測する」が原理的にできなくなる。
    #   ★ 実際 `run.sh` の実セッション名は 1 日以上、どの検査にも見られていなかった。
    extra = {}
    for name in ("run.sh", "notes.md", "data.md"):
        p = EXP_DIR / name
        extra[name] = p.read_text(encoding="utf-8") if p.exists() else None
    extra["step4_selftest.py"] = Path(__file__).read_text(encoding="utf-8")
    return cfg, cfg_text, html, worklet, py_ver, step3_html, step3_ver, seed_text, extra


# ---------------------------------------------------------------------------
# 検査本体
# ---------------------------------------------------------------------------
def build_checks(cfg, cfg_text, html, worklet, py_ver, step3_html, step3_ver, seed_text, extra):
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

    @add("player / config に絶対パス・ユーザー名が混入していない")
    def _():
        # ⚠️★★★ 2026-08-13（security-checker の指摘 ＋ 実測）に **検出漏れを直した**。
        #   ★ 旧パターン `[A-Za-z]:\\\\` は **バックスラッシュ 2 個**を要求していたので、
        #     散文中の普通の Windows パス（`C:\GSE-prototype\...`）に当たらなかった。
        #   ★ 旧パターンは `/Users/<name>`（macOS の home 形式）も 1 つも見ていなかった。
        #   ★ 実測: 6 形式のうち **旧は 4 つを取り逃し、新は 6/6 検出・対照 6 件で誤検出 0**。
        #
        # ⚠️★ **ユーザー名をハードコードしない**（旧実装は実ユーザー名を直接持っていた）——
        #   (a) それ自体がリポジトリにユーザー名を残すことになり、
        #   (b) **別マシン / 別ユーザー名では検査が空回りする**（★ 指摘された事故シナリオそのもの）。
        #   → ★ **home パスの「形」で見る** ＋ 実行中のユーザー名を実行時に引く。
        # ⚠️★★★ 2026-08-14（security-checker の指摘 ＋ 実測）に **走査範囲**を広げた。
        #   ★ 旧実装が見ていたのは **player / worklet / config の 3 つだけ**だった。
        #   ⚠️★★★ その外に **実セッション名が 2 件**あった（`run.sh` のコメント・`830758c` で混入）——
        #     ★ しかも **同じ run.sh の中で「セッション名は repo に書かない」と宣言していた。**
        #   → ★ **事故が起きた当のファイルを見ていない検査は、何も守っていない。**
        #     （★ `browser-verification` の「この検査はどちら側を見ているか」と同じ問い）
        # ---- PII-PATTERNS:BEGIN ----（⚠️ 自己走査ではこの区間を外す。★ 目印の実在も検査する）
        pats = [
            r"(?<![A-Za-z])[A-Za-z]:[\\/]",              # ★ C:\… / C:/… （★ 直前が英字なら http**s**:// 等なので除外）
            r"(?<![A-Za-z])/(Users|home)/[A-Za-z]",      # ★ /Users/<name> / /home/<name>
            r"(?<![A-Za-z])AppData[\\/]",                # ★ Windows のユーザー領域
        ]
        # ★★★ 実セッション名（擬似 ID ＋ **打鍵開始日時**）。★ data.md が repo に書かないと宣言している。
        #   ★ 架空名は `_00000000_` 形式にする約束なので、**年が 20xx で始まるものだけ**を拾う。
        sess = r"P\d{3}_gse_20\d{6}_\d{6}"
        # ★ 実行中のユーザー名（★ ハードコードしないので macOS / CI でもそのまま効く）
        me = None
        try:
            cand = Path.home().name
            if cand and len(cand) >= 3 and cand.lower() not in ("root", "user", "home", "users"):
                me = re.escape(cand)
        except Exception:
            pass   # ★ home が引けない環境では形の検査だけで走らせる（★ 黙って緑にはしない）
        # ---- PII-PATTERNS:END ----
        pats.append(sess)
        if me:
            pats.append(me)
        # ★★ 高信号だけの組（★ 説明文に**正当に**出てくる形は除く）——
        #   ⚠️ notes / data / 検査自身には「取り逃していた形」の**見本**が散文として載っている
        #     （★ 例: 2026-08-13 の検出漏れの表）。★ そこに絶対パスの形を当てると誤検出になる。
        #   ★ しかし **実セッション名と実ユーザー名は、どの文書にも正当な出番が無い。**
        strict_only = [sess] + ([me] if me else [])
        # ⚠️ 既知の誤検出の形: JS の `{a:/re/}` のように **空白なしで `:` の直後に `/`** が来る書き方。
        #   ★ 誤検出は「うるさいだけ」で人が 10 秒で直せる。★ 見逃しは実害が出る。★ 誤検出側に倒す。
        targets = [("player", html, pats), ("worklet", worklet, pats), ("config", cfg_text, pats)]
        for name in ("run.sh", "notes.md", "data.md"):
            text = extra.get(name)
            if text is None:
                raise Fail(f"{name} が無い（★ 走査対象が黙って消えると検査が空回りする）")
            # ★ run.sh は**実行されるコード**なので全パターン。notes / data は散文なので高信号だけ。
            targets.append((name, text, pats if name == "run.sh" else strict_only))
        # ★★★ **検査自身も走査する** —— ⚠️ 2026-08-13 の事故は
        #   「旧実装（＝この検査自身）が実ユーザー名を直接持っていた」形だった。
        #   ⚠️★ ただし上の正規表現リテラルと meta 変異の**架空**パスに自己反応するので、
        #     ★ 高信号だけを当て、さらにパターン定義区間を外す。
        self_text = extra["step4_selftest.py"]
        b, e = self_text.find("# ---- PII-PATTERNS:BEGIN ----"), self_text.find("# ---- PII-PATTERNS:END ----")
        if b < 0 or e < 0:
            raise Fail("自己走査の除外区間の目印が実在しない（★ 除外が no-op になり、自分の正規表現に反応する）")
        targets.append(("step4_selftest.py", self_text[:b] + self_text[e:], strict_only))
        for label, text, use in targets:
            for pat in use:
                m = re.search(pat, text)
                if m:
                    ctx = text[max(0, m.start() - 40):m.start() + 40].replace("\n", " ")
                    raise Fail(f"{label} に絶対パス/ユーザー名/実セッション名らしき文字列がある（{pat}）: …{ctx}…")

    @add("★★★ 検査自身が『連結』で実セッション名を隠し持っていない（2026-08-14 `/cross-review` HIGH）")
    def _():
        # ⚠️★★★ **上の混入検査は組み立て済みの文字列しか見ない。**
        #   ★ `"Pnnn" + "_gse_" + "<年月日>_<時分秒>"` の形で書くと **1 バイトも引っかからない。**
        #   ⚠️★★★ 実際にこの形で **実在の識別子が 4 箇所**に入っており、
        #     ⚠️ **`/cross-review` の diff に乗って外部 LLM へ送信された**（2026-08-14・実害が出た）。
        #   ⚠️ **これは「うっかり」ではなく検査の構造的な穴である** ——
        #     ★ 連結は「自己走査に反応させない」ために**意図的に**使っている書き方なので、
        #     ★ 同じ書き方をすれば**誰でも・いつでも**素通りできた。
        # → ★ **連結を畳んでからもう一度当てる。** ★ 残ってよいのは `FAKE_SESSION` だけ。
        # ⚠️ 誤検出側に倒す（★ 上の検査と同じ方針）—— 畳むことで無関係な隣接文字列が
        #   繋がって当たることはありうるが、★ **見逃しの実害の方が大きい。**
        self_text = extra["step4_selftest.py"]
        b, e = self_text.find("# ---- PII-PATTERNS:BEGIN ----"), self_text.find("# ---- PII-PATTERNS:END ----")
        if b < 0 or e < 0:
            raise Fail("自己走査の除外区間の目印が実在しない（★ 上の検査と同じ前提が壊れている）")
        scan = self_text[:b] + self_text[e:]
        # ★ `"a" + "b"` → `"ab"`（★ 空白・改行を跨ぐ連結も畳む）
        # ⚠️★★★ 2026-08-14 `/cross-review`（HIGH）—— **`+` を必須にしていたのが穴だった。**
        #   ★ Python は `"a" "b"`（**暗黙連結**）も合法で、しかも**改行を跨げる**。
        #   ⚠️ 実測: 暗黙連結は (a) この畳み込みを素通りし、(b) `secrets-filter.sh` も
        #     **awk が行単位**なので改行で分けると素通りする ＝ **2 層とも突破された。**
        #   → ★ `+` を**省略可能**にする。★ 陰性対照 5 件（`print("a", "b")` / `{"k": "v"}` /
        #     `f("x") + g("y")` / `["p", "q"]` / `"a" + str(n) + "b"`）で**誤結合しない**ことを実測した
        #     （★ 区切りに `,` `:` や識別子が入る形は畳まれない）。
        # ⚠️ **これでも塞げない形は残る**: `"".join([...])` / `%` 書式 / f-string / `chr()` 連結。
        #   ★ 既知の限界として S5C-D12 に明記した（★ 「塞いだ」と書かない）。
        folded = re.sub(r'"\s*\+?\s*"', "", scan)
        for m in re.finditer(r"P\d{3}_gse_20\d{6}_\d{6}", folded):
            got = m.group(0)
            if got != FAKE_SESSION:
                # ⚠️★ **実名を出力に書かない**（★ ここで出すと今度はログと端末へ漏れる）。
                raise Fail(
                    "検査自身が連結で実セッション名らしき文字列を隠し持っている"
                    f"（先頭 {got[:4]}…・{len(got)} 文字）。★ 見本は FAKE_SESSION だけを使うこと")

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

    # -----------------------------------------------------------------------
    # ★★★ Step 5（2026-08-13・S5-D1〜S5-D6）— 層 0 の音量つまみ
    #
    # ⚠️★★★ S4-D15: Step 4 では実装欠陥が 4 件出て、**4 件とも機械検査 79 件が全部緑のまま
    #   素通りした**。共通原因は「検査が実装の内部を見ていて、**測定の妥当性**を見ていない」こと。
    #   → ★ 以下は「set が実装されているか」ではなく **「その測定が何かを測れる条件になっているか」**
    #      を検査対象にする。
    # -----------------------------------------------------------------------
    L0G = cfg.get("layer0_gain")

    @add("★★★ 層 0 の音量軸が config に実在し、既定が『現行のまま』である")
    def _():
        if not L0G:
            raise Fail("layer0_gain 軸が config に無い（S5-D1）")
        opts = L0G["options"]
        d = next((o for o in opts if o["id"] == L0G["default"]), None)
        if d is None:
            raise Fail(f"既定 {L0G['default']} が候補に無い")
        if d["gain"] != 1.0:
            raise Fail(
                f"既定 {d['id']} の gain={d['gain']}。★ 既定は 1.0 でなければならない —— "
                "既定で音が変わると Step 4 の実測が再現できなくなる（S5-D7 / S5-D8）"
            )

    @add("★★★ 対照が実在する: 倍率 1.0（現行）と 0（層 0 なし）の両方がある")
    def _():
        gains = {o["gain"] for o in L0G["options"]}
        missing = {1.0, 0.0} - gains
        if missing:
            raise Fail(
                f"層 0 の音量候補に {sorted(missing)} が無い。"
                "★ 『層 0 が原因である』を示すには **層 0 を取り去った条件**が要る"
                "（browser-verification §2.0 の対照）"
            )

    @add("★ 層 0 の音量候補が 0..1 の範囲にあり、id が重複していない")
    def _():
        seen = set()
        for o in L0G["options"]:
            g = o["gain"]
            if not isinstance(g, (int, float)) or not (0.0 <= g <= 1.0):
                raise Fail(f"{o['id']} の gain={g} が 0..1 の外（★ 1 を超えるとヘッドルームを壊す）")
            if o["id"] in seen:
                raise Fail(f"id {o['id']} が重複している")
            seen.add(o["id"])

    @add("★★★ 予測コントラストが『予測である』と config に明記されている（実測と混ぜない）")
    def _():
        # ⚠️★ 最初は layer0_gain 全体を 1 本の文字列にして探したが、**素通りした**（実測）——
        #   同じ語が個々の候補の fact にもあるため、断り書きを消しても緑のままだった。
        #   → ★ **断り書きが住む場所を名指しで検査する。**
        note = " ".join(L0G.get("_predicted_contrast_note", []))
        if "予測であって実測ではない" not in note:
            raise Fail(
                "predicted_db を置きながら _predicted_contrast_note に"
                "『予測であって実測ではない』と書いていない。★ 予測を実測欄に書かせない歯止めが無い"
            )
        if not any("predicted_db" in o for o in L0G["options"]):
            raise Fail("predicted_db を持つ候補が 1 つも無い（断り書きの対象が存在しない）")
        # ★ player が予測値を **判定や計算に使っていない**こと（表示だけ）
        if "predicted_db" in html and "pd[span]" not in html:
            raise Fail("player が predicted_db を表示以外で使っている疑い")

    @add("★★★ S5-D5: 実時間で expr.gain を書くのが applyLayer0Gain() だけである")
    def _():
        body = strip_js_comments(html)
        # ⚠️★ 「`graph.expr.gain.method(` を数える」形では **素通りした**（実測）——
        #   ★ 実装は `const p = graph.expr.gain;` と束ねてから書くので 0 件に見えた。
        #   → ★ **`.value` 読み以外の出現をすべて「書き込みうる参照」として数える。**
        refs = [m for m in re.finditer(r"graph\.expr\.gain(\.\w+)?(\s*=[^=])?", body)]
        # ★ `.value` の **読み** だけを除外する。⚠️ `.value = ` は代入なので書き手である
        #   （レビュー実測: `graph.expr.gain.value = 1;` を control() に足しても緑だった）
        writable = [m.group(0) for m in refs if not (m.group(1) == ".value" and not m.group(2))]
        if len(writable) != 1:
            raise Fail(
                f"graph.expr.gain への書き込みうる参照が {len(writable)} 箇所ある（{writable}）。"
                "★ 書き手は applyLayer0Gain() の 1 つだけにする（S5-D5・H2 と同じ形）"
            )
        fn = strip_js_comments(extract_function(html, "applyLayer0Gain"))
        if "graph.expr.gain" not in fn:
            raise Fail("applyLayer0Gain() が graph.expr.gain を触っていない")

    @add("★★★ BF-5: 起動時の適用が `playing = true` より **後** にある（前だと完全な no-op）")
    def _():
        # ⚠️★★★ 2026-08-13 に実際に踏んだ欠陥（BF-5）——
        #   `applyLayer0Gain` は `if (!playing || !graph) return;` で始まるので、
        #   `playing = true` より前に呼ぶと **1 命令も実行されない**。
        #   ★ 層 0 の倍率には control() のような周期的な書き手が居ないので、
        #     **停止 → 再生のたびに倍率 1.0 のまま鳴り続ける**（記録と実音が食い違う）。
        #   ⚠️ 「呼んでいるか」を見る検査では捕まらない。★ **位置**を見る。
        fn = strip_js_comments(extract_function(html, "startAudio"))
        iCall, iFlag = fn.find("applyLayer0Gain(true)"), fn.find("playing = true")
        if iCall < 0:
            raise Fail("startAudio が applyLayer0Gain(true) を呼んでいない（選択が再生をまたがない）")
        if iFlag < 0:
            raise Fail("startAudio に playing = true が見つからない（検査の前提が崩れている）")
        if iCall < iFlag:
            raise Fail(
                "applyLayer0Gain(true) が playing = true より前にある。"
                "★ 早期 return で **完全な no-op** になる（BF-5）"
            )
        if "if (!playing" not in strip_js_comments(extract_function(html, "applyLayer0Gain")):
            raise Fail("applyLayer0Gain の早期 return が消えた（この検査の前提が変わった）")

    @add("★★★ 目標倍率と実効倍率の一致を **実行時に**確かめてから測る（静的検査では届かない層）")
    def _():
        body = strip_js_comments(html)
        mism = strip_js_comments(extract_function(html, "layer0GainMismatch"))
        if "graph.expr.gain.value" not in mism or "layer0GainOpt().gain" not in mism:
            raise Fail("layer0GainMismatch が目標と実効を突き合わせていない")
        cal = strip_js_comments(extract_function(html, "abxCalibrate"))
        if "layer0GainMismatch()" not in cal:
            raise Fail(
                "abxCalibrate が実効倍率を確かめずに測っている。"
                "★ 『呼んだはず』の倍率で測ると、記録と実音が食い違う（BF-5）"
            )

    @add("★★★ master の落ち着き（フェードイン / 音量操作）も『到達待ち』に入っている")
    def _():
        rem = strip_js_comments(extract_function(html, "calRemainMs"))
        if "masterSettleUntil" not in rem:
            raise Fail(
                "calRemainMs が masterSettleUntil を見ていない。"
                "★ フェードイン中に①を押すと **A だけ小さいレベルで測られ比が化ける**"
            )
        st = strip_js_comments(extract_function(html, "startAudio"))
        if "masterSettleUntil" not in st:
            raise Fail("startAudio がフェードインぶんの待ちを設定していない")

    @add("★★ 盲検は開始時に凍結した条件だけを読む（途中で軸を触られても結果が消えない）")
    def _():
        st = strip_js_comments(extract_function(html, "abxBlindStart"))
        if "ratio: abx.ratio" not in st or "ratioCond: { ...abx.ratioCond }" not in st:
            raise Fail("abxBlindStart が比と条件を凍結していない")
        if "lockUI(true)" not in st:
            raise Fail("盲検中に軸をロックしていない（刺激を途中で変えられる）")
        fin = strip_js_comments(extract_function(html, "abxBlindFinish"))
        if "abx.ratio" in fin:
            raise Fail(
                "abxBlindFinish が live の abx.ratio を読んでいる。"
                "★ 盲検中に条件を変えられると null になり、TypeError で結果が丸ごと消える"
            )
        inv = strip_js_comments(extract_function(html, "invalidateAbxRatio"))
        # ★ 2026-08-13: 中止は `abxBlindStop()` の **単一経路**に集約した（AB-D2・レビュー実測）。
        #   ★ ここは「中止しているか」を見る。★ 実際に手放しているかは stop 側の検査が見る。
        if "abxBlindStop(" not in inv and "abx.blind" not in inv:
            raise Fail("invalidateAbxRatio が走行中の盲検を中止していない")
        stp = strip_js_comments(extract_function(html, "abxBlindStop"))
        if not re.search(r"abx\.blind\s*=\s*null", stp):
            raise Fail("abxBlindStop が abx.blind を手放していない（中止が効かない）")

    @add("★★ 盲検中に触れる軸が lockUI に全部入っている")
    def _():
        lk = strip_js_comments(extract_function(html, "lockUI"))
        for ax in ("ax-l0gain", "ax-timbre", "ax-dcue", "ax-dspan"):
            if ax not in lk:
                raise Fail(f"{ax} が lockUI に入っていない（盲検中に刺激を変えられる）")

    @add("★★ 瞬時 A/B の結果に保存経路がある（層 0 の倍率が記録として残る）")
    def _():
        body = strip_js_comments(html)
        if "function exportAbx(" not in body or 'id="btn-abx-export"' not in html:
            raise Fail(
                "abx.lastResult の保存経路が無い。"
                "★ exportBlind() は分離案（B7）用で層 0 の倍率を含まない —— 閾値の記録が残らない"
            )
        ex = strip_js_comments(extract_function(html, "exportAbx"))
        if "abx.lastResult" not in ex:
            raise Fail("exportAbx が abx.lastResult を保存していない")

    # ---- ★★★ 盲検の提示手順（2026-08-13・AB-D1〜AB-D6）------------------
    #
    # ⚠️★★★ 既存の検査 103 件は、**3 件の交絡を全部緑のまま素通りさせた。**
    #   ★ 理由（AB-D0）: 既存の検査はすべて **「1 トライアルの中」または「刺激の作り方」**を見ており、
    #     ⚠️ **「トライアルとトライアルの間」と「同じ聴き手が繰り返すこと」を見る検査が 1 件も無かった。**
    #   → ★ 以下は **試行の系列（順序・持ち越し・反復）** を検査対象にする。

    ABX_BLIND = cfg["layer2_rework"]["abx"]["blind"]

    @add("★★★ AB-D1: 盲検の出題 seed が config に固定されていない（毎回同じ順を出さない）")
    def _():
        # ⚠️★★★ 実際に踏んだ形: order_seed が固定定数だったので buildAbxOrder が
        #   **毎回まったく同じ順**を返し（実測で 3 回とも同一）、研究者が 5 倍率ぶん
        #   同じ順を聴くことになっていた。★ 後の倍率ほど正答が上がる ＝ 閾値が高い倍率側に見える。
        if "order_seed" in ABX_BLIND:
            raise Fail(
                "layer2_rework.abx.blind.order_seed が復活している。"
                "★ 固定 seed だと同じ聴き手が繰り返すあいだ毎回同じ出題順になる（AB-D1）"
            )
        if "_order_seed_removed_why" not in ABX_BLIND:
            raise Fail("order_seed を消した理由が config に残っていない（★ 戻される）")

    @add("★★★ AB-D1: 出題順の seed を毎回引き、引いた値を結果に残している")
    def _():
        body = strip_js_comments(html)
        if "function drawOrderSeed(" not in body:
            raise Fail("drawOrderSeed() が無い（seed を引き直す経路が存在しない）")
        st = strip_js_comments(extract_function(html, "abxBlindStart"))
        if not re.search(r"const\s+orderSeed\s*=\s*drawOrderSeed\(\)", st):
            raise Fail("abxBlindStart が seed を引き直していない")
        if re.search(r"buildAbxOrder\(\s*B\.order_seed", st):
            raise Fail("abxBlindStart がまだ config の固定 seed を使っている")
        if not re.search(r"buildAbxOrder\(\s*orderSeed", st):
            raise Fail("buildAbxOrder に引き直した seed を渡していない")
        # ⚠️★★★ 引いた値を **abx.blind に載せる**ところが抜けると `order_seed: undefined` になる
        #   （★ レビュー実測: `orderSeed,` を落としても緑だった）。
        # ⚠️★★★ 最初の直しも **まだ空回りしていた**（meta が捕まえた）——
        #   `buildAbxOrder(orderSeed,` が同じ関数に在るので `orderSeed\s*,` が当たってしまう。
        #   → ★ **`abx.blind = { … }` のリテラルの中だけ**を見る。
        #   ★ 波括弧を対応させて取り出す（★ `{ ...abx.ratioCond }` が入れ子になっているので
        #     非貪欲な正規表現では最初の `}` で切れる）。
        i = st.find("abx.blind = {")
        if i < 0:
            raise Fail("abx.blind の生成リテラルが読めない")
        j, depth = st.index("{", i), 0
        for k in range(j, len(st)):
            if st[k] == "{":
                depth += 1
            elif st[k] == "}":
                depth -= 1
                if depth == 0:
                    break
        obj = st[j:k + 1]
        if not re.search(r"(?<![A-Za-z])orderSeed\s*[,:]", obj):
            raise Fail("引いた seed を abx.blind に載せていない（結果が order_seed: undefined になる）")
        # ★★ 引いても**記録しなければ再現できない**。★ ここが AB-D1 の肝である
        fin = strip_js_comments(extract_function(html, "abxBlindFinish"))
        if not re.search(r"order_seed:\s*bl\.orderSeed", fin):
            raise Fail(
                "結果の order_seed が bl.orderSeed を指していない。"
                "★ 毎回引き直すなら、実際に使った値を記録しないと出題順を再構成できない（AB-D1）"
            )

    @add("★★★ S5C-D1: 準備区間と 1 区間目で状態を **1 つも動かさない**（AB-D10 の漏れの経路を消す）")
    def _():
        # ⚠️★★★ ここまでに 3 回間違えている（★ 経緯を消さない）:
        #   初版  リセット無し        → 持ち越しの跳びが 1 区間目の中で鳴る
        #   AB-D2 リセットを準備区間へ → 跳びが「直前が diff のときだけ」鳴り、真値が漏れる
        #   AB-D7 乱数 carry を挟む    → **跳びの回数の偶奇**が入場状態を一意に決める
        # ★★★ S5C-D1（A′）: 準備区間から **状態変化そのもの**を無くす。
        #   ★ 経路が存在しないので、偶奇も向きも大きさも問えない。
        nx = strip_js_comments(extract_function(html, "abxBlindNext"))
        m_prep = re.search(r'abxPhase\(\s*bl\s*,\s*"prep"\s*,', nx)
        m_i1 = re.search(r'abxPhase\(\s*bl\s*,\s*"i1"\s*,', nx)
        m_i2 = re.search(r'abxPhase\(\s*bl\s*,\s*"i2"\s*,', nx)
        if not (m_prep and m_i1 and m_i2):
            raise Fail(
                "abxBlindNext に prep / i1 / i2 の 3 相がそろっていない（"
                f"prep={bool(m_prep)} i1={bool(m_i1)} i2={bool(m_i2)}）"
            )
        if not (m_prep.start() < m_i1.start() < m_i2.start()):
            raise Fail("prep → i1 → i2 の順になっていない")
        # ★★★ **本体**: 先頭〜1 区間目の待ちが終わるまでに、状態を変える呼び出しが 1 つも無いこと。
        #   ⚠️ 「abxSet が無い」ではなく **位置**で見る（BF-5 の教訓）——
        #     採点区間より後ろにあるのは正しいので、前半だけを切り出して見る。
        # ★ 関数の**宣言行**を外す（★ 外さないと自分の名前 `abxBlindNext(` を呼び出しと誤読する）
        head = nx[nx.index("{"):m_i1.end()]
        # ⚠️★★★ 「`abxSet*` が無い」だけでは足りない（`code-reviewer` 実測）——
        #   ★ `hiddenReset()` のような **ヘルパ経由**なら素通りする。
        #   → ★ **呼んでよいものを列挙し、それ以外の呼び出しを落とす**（★ 足すときに必ず人が見る形）。
        #   ★ 足してよいのは **状態を書かない純粋な getter** だけ。⚠️ 足すときは実装を読んで確かめる。
        allowed = {"abxPhase", "abxBlindFinish", "$", "Object", "Math", "if", "for", "while",
                   "switch", "catch", "return", "await", "typeof",
                   "abxSideSeconds", "abxPrepSeconds", "abxTrOpt", "abxOpt"}
        for m_call in re.finditer(r"\b([A-Za-z_$][\w$]*)\s*\(", head):
            if m_call.group(1) not in allowed:
                raise Fail(
                    f"準備区間 / 1 区間目で `{m_call.group(1)}()` を呼んでいる。"
                    "★ ここで状態を動かすと、その向きと回数が入場状態＝直前トライアルの真値を運ぶ（AB-D10）。"
                    "★ 状態を変えないと言えるなら、この検査の allowed に足すこと"
                )
        # ★ 直接代入で状態を動かす形も落とす（★ 呼び出しだけを見ると素通りする）
        if re.search(r"\babx\.(state|tr|active)\s*=", head):
            raise Fail("準備区間 / 1 区間目で abx の状態を直接書き換えている")

    @add("★★★ S5C-D1: 1 区間目と 2 区間目の長さが **真値に依らない**（時間の手がかりを作らない）")
    def _():
        # ⚠️★★★ `code-reviewer` 実測: `abxPhase(bl, "i2", ms + (kind === "diff" ? 500 : 0), …)` で
        #   **123 件が全部緑**だった。★ 長さが真値で変わると、耳を使わずに答えが出る。
        nx = strip_js_comments(extract_function(html, "abxBlindNext"))
        args = {}
        for ph in ("i1", "i2"):
            m = re.search(r'abxPhase\(\s*bl\s*,\s*"' + ph + r'"\s*,\s*([^,]+),', nx)
            if not m:
                raise Fail(f"{ph} の長さの引数が読めない")
            args[ph] = m.group(1).strip()
        if args["i1"] != args["i2"]:
            raise Fail(f"1 区間目と 2 区間目の長さが違う式で書かれている（{args['i1']} / {args['i2']}）")
        m = re.search(r"const\s+" + re.escape(args["i1"]) + r"\s*=\s*([^;]+);", nx)
        if not m:
            raise Fail(f"長さ `{args['i1']}` の定義が abxBlindNext に無い（★ 真値に依らないことを確かめられない）")
        for bad in ("kind", "truth", "order"):
            if re.search(r"\b" + bad + r"\b", m.group(1)):
                raise Fail(f"区間の長さが真値から作られている（{m.group(1).strip()}）")
        # ★ 準備区間も同じ（★ 相の長さで真値が分かってはならない）
        m_prep = re.search(r'abxPhase\(\s*bl\s*,\s*"prep"\s*,\s*([^,]+),', nx)
        for bad in ("kind", "truth", "order"):
            if m_prep and re.search(r"\b" + bad + r"\b", m_prep.group(1)):
                raise Fail(f"準備区間の長さが真値から作られている（{m_prep.group(1).strip()}）")

    @add("★★★ S5C-D3: 盲検中に **提示条件を画面へ書かない**（★ 真値が読めてしまう経路）")
    def _():
        # ⚠️★★★ 2026-08-14（`code-reviewer` が実測で発見）——
        #   `abx-now` は盲検パネルの中の可視要素で、`abxApply()` が `${abx.state} へ…` を書いていた。
        #   ★ `abxSet(to)` は 2 区間目の頭で呼ばれるので、**diff なら表示が変わり same なら変わらない。**
        #   ⚠️★★★ AB-D3 は「境目は**画面表示だけ**で示す」＝ **聴き手が画面を見る前提**である。
        #   ★ 跳びの知覚が要らず**読むだけで分かる**ので、AB-D10 より重い。
        ap = strip_js_comments(extract_function(html, "abxApply"))
        m = re.search(r'\$\(\s*"abx-now"\s*\)\.textContent\s*=\s*([^;]+);', ap)
        if not m:
            raise Fail("abxApply が abx-now に何を書くか読めない（★ 形が変わったら検査し直す）")
        assign = m.group(1)
        if not re.search(r"\babx\.blind\b", assign):
            raise Fail(
                "盲検中かどうかを見ずに abx-now を書いている。"
                "★ 2 区間目の頭で表示が変われば diff、変わらなければ same と読めてしまう（S5C-D3）"
            )
        # ★ 盲検中の枝に状態が混ざっていないこと（★ 分岐を足しただけでは足りない）
        blind_branch = assign.split("?")[1].split(":")[0] if "?" in assign else assign
        for bad in ("abx.state", "abxValue", "abxOpt"):
            if bad in blind_branch:
                raise Fail(f"盲検中の表示に {bad} が混ざっている（★ 伏せたことにならない）")

    @add("★★★ S5C-D6: レベルが動かない写し方では **明示的な承知が要る**（★ 同じ取り違えが 2 回起きた）")
    def _():
        # ⚠️★★★ 2026-08-13（S5-26）と 2026-08-14（本 Step）の **2 回とも**、
        #   「ページを再読込したら `dcue` が既定（質感のみ）へ戻っていた」形で測ってしまい、
        #   ★ **測り終えて結果 JSON を読むまで気づかなかった**（★ 合計 10 分ぶんの試聴が無駄になった）。
        #   ⚠️★★★ S5-D2 の「手順で塞げるものを実装で塞ぎに行かない」は、
        #     ★ **手順で 2 回とも防げなかった**という実績に負ける（`verify-before-claiming` ルール 3）。
        st = strip_js_comments(extract_function(html, "abxBlindStart"))
        if 'id="abx-texture-ack"' not in html:
            raise Fail("承知の印（abx-texture-ack）が画面に無い")
        m = re.search(r"if\s*\(\s*!\s*contrastMeasurable\s*\)\s*\{", st)
        if not m:
            raise Fail("contrastMeasurable が false のときの枝が読めない")
        # ★ 中括弧の対応で枝を切り出す（★ 行頭の空白に依存する正規表現は形が変わると黙って外れる）
        depth, end = 0, None
        for k in range(m.end() - 1, len(st)):
            if st[k] == "{":
                depth += 1
            elif st[k] == "}":
                depth -= 1
                if depth == 0:
                    end = k
                    break
        if end is None:
            raise Fail("contrastMeasurable の枝の終わりが見つからない")
        branch = st[m.end():end]
        if "abx-texture-ack" not in branch:
            raise Fail("レベルが動かない写し方でも、承知の印を見ずに盲検が始まる（S5C-D6）")
        if not re.search(r"\breturn\s*;", branch):
            raise Fail("承知の印が無いときに **止めていない**（★ 警告だけでは 2 回とも防げなかった）")
        # ★★ 測っている条件を、盲検のあいだずっと画面に出す（★ 走行中に見えなければ意味がない）
        if not re.search(r"condTag:", st):
            raise Fail("条件の札を開始時に凍結していない")
        ph = strip_js_comments(extract_function(html, "abxPhase"))
        if "condTag" not in ph:
            raise Fail("盲検の画面に条件の札を出していない（★ 終わってからでは遅い）")

    @add("★★★ S5C-D4: 開始状態が **1 つの変数から**作られ、乱数で引かれる")
    def _():
        # ⚠️★★★ `code-reviewer` 実測: `state: "A"` / `initialState: "A"` / `abxSetInstant("A")` の
        #   3 つが独立したリテラルだったので、**記録だけを "B" に変えても全部緑**だった（記録が嘘になる）。
        # ⚠️ 固定 "A" は聴き手に**既知の錨**を 2 つ与える（1 回目の diff は必ず上向き / 終状態も必ず "A"）。
        st = strip_js_comments(extract_function(html, "abxBlindStart"))
        m = re.search(r"const\s+initialState\s*=\s*([^;]+);", st)
        if not m:
            raise Fail("開始状態を 1 つの変数に置いていない（3 箇所に書くと記録だけ嘘になりうる）")
        if "drawOrderSeed" not in m.group(1) and "random" not in m.group(1).lower():
            raise Fail(f"開始状態が乱数で引かれていない（{m.group(1).strip()}）")
        # ⚠️★ `initialState\b` だけでは足りない —— `initialState: "A"` と書かれても `\b` は成立し、
        #   ★ **記録だけが嘘になる形が緑で通る**（★ meta で実測した）。→ ★ 短縮記法であることを要求する。
        if not re.search(r"state:\s*initialState\s*,\s*initialState(?!\s*:)", st):
            raise Fail("bl.state と bl.initialState が同じ変数から作られていない")
        if not re.search(r"abxSetInstant\(\s*initialState\s*\)", st):
            raise Fail("実際に鳴らす開始状態が initialState から作られていない（記録と提示がずれる）")

    @add("★★★ S5C-D1: 2 区間目の状態が **1 区間目の状態から** 決まる（終点をリテラルで固定しない）")
    def _():
        # ⚠️★★★ AB-D10 の恒等式は「**終点が固定**」から出ていた ——
        #   ★ 始点と終点が固定なら、跳びの回数の偶奇は経路によらない不変量になる。
        #   → ★ 終点をリテラル（"A" / "B"）で書いた瞬間に漏れが復活する。
        nx = strip_js_comments(extract_function(html, "abxBlindNext"))
        # ⚠️★★ 引数**そのもの**がリテラルの場合だけを見ると足りない ——
        #   ★ `abxSet(kind === "diff" ? "B" : "A")` は「終点が真値だけで決まる」旧設計そのものなのに、
        #     第 1 引数はリテラルではないので素通りする（★ meta で実測した）。
        #   → ★ **引数リストのどこかに状態リテラルがあれば落とす。**
        lit = re.search(r"\babxSet\w*\s*\([^)]*[\"'][AB][\"']", nx)
        if lit:
            raise Fail(
                "2 区間目の状態をリテラルで指定している"
                f"（{nx[lit.start():lit.end() + 8]!r}）。"
                "★ 終点が固定されると跳びの偶奇＝入場状態という AB-D10 の恒等式が復活する"
            )
        if not re.search(r"const\s+from\s*=\s*bl\.state\s*;", nx):
            raise Fail("1 区間目の状態が bl.state（持ち越した到達点）から来ていない")
        m = re.search(r"const\s+to\s*=\s*([^;]+);", nx)
        if not m:
            raise Fail("2 区間目の状態の決め方が読めない")
        expr = m.group(1)
        if "from" not in expr:
            raise Fail(f"2 区間目の状態が 1 区間目の状態を見ていない（{expr.strip()}）")
        if "kind" not in expr:
            raise Fail(f"2 区間目の状態が真値を見ていない（{expr.strip()}）")
        if not re.search(r"\babxSet\s*\(\s*to\s*\)", nx):
            raise Fail("2 区間目の切替が abxSet(to)（遷移時間を守る側）になっていない")
        # ★★★ 持ち越し —— ★ 更新しないと 1 区間目の基準が固定に戻り、A′ が丸ごと無効になる
        m_keep = re.search(r"\bbl\.state\s*=\s*to\s*;", nx)
        if not m_keep:
            raise Fail(
                "到達点を次のトライアルへ持ち越していない（bl.state = to が無い）。"
                "★ 持ち越さないと 1 区間目が毎回同じ状態になり、終点が固定＝AB-D10 に戻る"
            )
        # ⚠️★★★ **条件分岐の中に入れると 2 回目以降が持ち越さない**のに、行は残るので緑になる
        #   （★ AB-D2 のときに実測した silent pass とまったく同じ形。★ meta で再実測した）。
        if re.search(r"\bif\s*\([^)]*\)\s*\{?[^;{}]*$", nx[:m_keep.start()]):
            raise Fail(
                "到達点の持ち越しが条件分岐の中にある。★ 毎トライアル無条件に走らないと、"
                "2 回目以降が固定の基準に戻り持ち越していないのと同じになる"
            )

    @add("★★★ S5C-D1: 遷移を持たない切替（abxSetInstant）の呼び出し元が **開始状態の定義 1 箇所だけ**")
    def _():
        body = strip_js_comments(html)
        if "function abxSetInstant(" not in body:
            raise Fail("abxSetInstant() が無い")
        fn = strip_js_comments(extract_function(html, "abxSetInstant"))
        if not re.search(r"dur:\s*0", fn):
            raise Fail("abxSetInstant が即座になっていない（dur: 0 が無い）")
        # ⚠️★★★ トライアルの中で呼ぶと、(a) 準備区間に跳びが戻る（AB-D10 が復活）か、
        #   (b) 採点区間で遷移時間という本題の独立変数が黙って無効になる。
        nx = strip_js_comments(extract_function(html, "abxBlindNext"))
        if "abxSetInstant" in nx:
            raise Fail(
                "abxBlindNext が abxSetInstant を呼んでいる。"
                "★ トライアルの中に遷移 0 の切替があると、跳びが戻るか遷移時間が無効になる（S5C-D1）"
            )
        # ★ 呼び出し元の**数**で見る（★ 「どこかに 1 つある」では、増えたことに気づけない）
        uses = re.findall(r"\babxSetInstant\s*\(", body)
        if len(uses) != 2:      # ★ 定義 1 ＋ 呼び出し 1
            raise Fail(
                f"abxSetInstant の出現が {len(uses)} 箇所ある（★ 定義 1 ＋ 呼び出し 1 = 2 が正）。"
                "★ 呼び出し元が増えると、どこで跳びが起きるかを追えなくなる"
            )
        st = strip_js_comments(extract_function(html, "abxBlindStart"))
        if not re.search(r"abxSetInstant\(\s*initialState\s*\)", st):
            raise Fail(
                "盲検の開始状態を定義していない。"
                "★ ①は測り終えたあと状態を元へ戻すので、②の入口の状態は不定である"
            )

    @add("★★★ S5C-D1: 上向き diff と下向き diff が **均衡する**（★ 実装の式を取り出して全通り評価する）")
    def _():
        # ⚠️★★★ 2026-08-14（`code-reviewer` 実測）: **旧版は config の trials しか見ていなかった。**
        #   ★ `to` を常に "B" にする変異（＝交互性が完全に壊れる）でも **123 件が全部緑**だった。
        #   → ★ **実装のソースから `to` の式を取り出し、(from, kind) の 4 通りで実際に評価する。**
        nx = strip_js_comments(extract_function(html, "abxBlindNext"))
        m = re.search(r"const\s+to\s*=\s*([^;]+);", nx)
        if not m:
            raise Fail("2 区間目の状態の式が読めない")
        expr = m.group(1)
        for frm in ("A", "B"):
            other = "B" if frm == "A" else "A"
            try:
                same_to = js_eval_simple(expr, {"from": frm, "kind": "same"})
                diff_to = js_eval_simple(expr, {"from": frm, "kind": "diff"})
            except ValueError as e:
                raise Fail(f"2 区間目の式を評価できない（{expr.strip()}）: {e}")
            if same_to != frm:
                raise Fail(f"same なのに状態が変わる（from={frm} → {same_to}）")
            if diff_to != other:
                raise Fail(
                    f"diff なのに反転していない（from={frm} → {diff_to}・{other} が正）。"
                    "★ 交互に反転しないと上下の均衡が成立しない"
                )
        # ★ ここまでで「diff のたびに必ず反転する」ことが実装から確かめられた。
        #   ★ その上で **いま config に書かれている trials で不変量が成立するか**を全通り列挙する。
        n = ABX_BLIND["trials"]
        if not isinstance(n, int) or not (2 <= n <= 16):
            # ⚠️ 全列挙は組合せ爆発する（trials=24 で 270 万通り）。★ 上限を置いて**黙って重くしない**
            raise Fail(f"trials={n} は全通り列挙の範囲外（2..16）。★ 上限を上げるなら列挙をやめる")
        half = n // 2                      # ★ buildAbxOrder の Math.floor(n / 2) と同じ
        if not re.search(r"const\s+half\s*=\s*Math\.floor\(\s*n\s*/\s*2\s*\)\s*;",
                         strip_js_comments(extract_function(html, "buildAbxOrder"))):
            raise Fail("buildAbxOrder の diff 個数の式が `Math.floor(n / 2)` でない（検査側の half とずれる）")
        if half == 0:
            raise Fail(f"diff が 1 回も出ない（trials={n}）")
        for start in ("A", "B"):           # ★ 開始状態は乱数なので両方で確かめる（S5C-D4）
            for pos in combinations(range(n), half):
                hot, s, up, down = set(pos), start, 0, 0
                for i in range(n):
                    kind = "diff" if i in hot else "same"
                    nxt = js_eval_simple(expr, {"from": s, "kind": kind})
                    if kind == "diff":
                        if s == "A":
                            up += 1
                        else:
                            down += 1
                    s = nxt
                if up != down or s != start:
                    raise Fail(
                        f"上向き / 下向きの diff が均衡しない（trials={n} / 開始 {start} / "
                        f"diff の位置 {pos} で 上 {up} 回・下 {down} 回・終状態 {s}）。"
                        "★ diff の回数が偶数でないと成立しない"
                    )

    @add("★★★ S5C-D5: 方向の均衡を **実際に提示した列から数え直して**結果に残す")
    def _():
        # ⚠️★★★ 上の検査は「実装の式」を見ている。★ こちらは「その run で実際に何を提示したか」。
        #   ★ 静的検査と実測記録の 2 枚にする（★ S5-D11「記録と照合は同じ定義から作る」）。
        fin = strip_js_comments(extract_function(html, "abxBlindFinish"))
        if not re.search(r"bl\.timing", fin):
            raise Fail("方向の均衡を bl.timing（実際に提示した列）から数えていない")
        for need, why in ((r"from\s*===\s*\"A\"\s*&&\s*t\.to\s*===\s*\"B\"", "上向きを数えていない"),
                          (r"from\s*===\s*\"B\"\s*&&\s*t\.to\s*===\s*\"A\"", "下向きを数えていない")):
            if not re.search(need, fin):
                raise Fail(why)
        if not re.search(r"direction_balance:\s*bl\.directionBalance", fin):
            raise Fail("方向の均衡を結果 JSON に残していない（事後に検算できない）")
        if not re.search(r"ok:\s*up\s*===\s*down", fin):
            raise Fail("上向き = 下向き を判定していない")
        if not re.search(r"directionBalance\.ok\s*\?", fin):
            raise Fail("方向が均衡していないことを画面に出していない（★ 壊れた提示が黙って通る）")

    @add("★★ S5C-D1: protocol が新手順の値で、**旧手順の値が実行経路に残っていない**")
    def _():
        # ⚠️★★★ 値を据え置くと、**測り直した結果と旧手順の結果が JSON 上で区別できなくなる。**
        #   ★ 本 Step は「同じ刺激量を別の手順で測り直す」ことが主題なので、これは致命的である。
        fin = strip_js_comments(extract_function(html, "abxBlindFinish"))
        m = re.search(r'protocol:\s*"([^"]+)"', fin)
        if not m:
            raise Fail("結果に protocol が入っていない（どの手順で測ったか分からなくなる）")
        if m.group(1) != "3phase-noreset-v2":
            raise Fail(f"protocol が新手順の値になっていない（{m.group(1)}）")
        if "3phase-prep-v1" in strip_js_comments(html):
            raise Fail("旧手順の protocol 値が実行経路に残っている（記録が取り違えられる）")
        # ★ 事後に方向の均衡を検算できる形で残っていること（★ AC-4 を記録側から支える）
        nx = strip_js_comments(extract_function(html, "abxBlindNext"))
        if not (re.search(r"\bt\.from\s*=\s*from\s*;", nx) and re.search(r"\bt\.to\s*=\s*to\s*;", nx)):
            raise Fail("各トライアルの 1 区間目 / 2 区間目の状態を記録していない（from / to）")
        if not re.search(r"initial_state:\s*bl\.initialState", fin):
            raise Fail("開始状態を結果に残していない（状態列を復元できない）")

    @add("★★★ AB-D2 / AB-D7: 準備区間の長さが実装の式から出ていて、跳びの減衰より十分長い")
    def _():
        if "prep_seconds" not in ABX_BLIND:
            raise Fail("blind.prep_seconds が config に無い（AB-D2）")
        if not (ABX_BLIND["prep_seconds"] > 0):
            raise Fail(f"prep_seconds が 0 以下（{ABX_BLIND['prep_seconds']}）")
        body = strip_js_comments(html)
        if "function abxPrepSeconds(" not in body:
            raise Fail("abxPrepSeconds() が無い")
        fn = strip_js_comments(extract_function(html, "abxPrepSeconds"))
        # ⚠️★★★ 旧版の検査は **恒真だった**（レビュー実測）——
        #   `want = max(prep, sec+2); if want < sec+2` は max の定義上ぜったいに真にならない。
        #   ★ **仕様の式を再実装して自分と比べていた**ので、実装が何であっても緑だった。
        #   → ★ **実装のソースから式を取り出して**判定する。
        m = re.search(r"return\s+Math\.max\(\s*B\.prep_seconds\s*,\s*([0-9.]+)\s*\)\s*;", fn)
        if not m:
            raise Fail(
                "abxPrepSeconds が `Math.max(B.prep_seconds, <床>)` の形になっていない: "
                + fn.strip().splitlines()[-2:][0].strip()
            )
        floor = float(m.group(1))
        # ⚠️★★★ 2026-08-14（S5C-D1）で **準備区間の役割が変わった**（★ 経緯を消さない）:
        #   旧: 跳びの跡を捨てる場所 → ★ 床の根拠は「実測 700 ms の 2 倍」だった。
        #   新: 状態を動かさないので **跡が無い** → ★ 床の根拠は「境目として知覚できる長さ」。
        #   ⚠️★ ただし **1 回目だけは例外** —— ②の開始時の `abxSetInstant(initialState)` が
        #     フル振幅の瞬時の跳びを作り、その跡が 1 回目の準備区間に入る（`code-reviewer` 指摘）。
        #     → ★ **1 回目の跡を収めるためにも、床は跳びの減衰 0.7 s の 2 倍以上を保つ。**
        #   ⚠️ 旧版にあった「2 段に割ると…」の条件は **2 段構成が消えたので削除した**
        #     （★ 効いていない条件を「効いている」と記録に残さない）。
        if floor < 1.4:
            raise Fail(f"準備区間の床が短すぎる（{floor} s）。★ 開始時の跳びの減衰は実測 0.7 s")
        eff = max(ABX_BLIND["prep_seconds"], floor)
        if eff < 1.4:
            raise Fail(f"準備区間の実効値が {eff} s しかない（★ 1 回目の跳びの跡が 1 区間目へ漏れる）")

    @add("★★★ AB-D2: 3 つの相が画面に出る（『何と比べるか』が聴き手に決まる）")
    def _():
        # ⚠️★★★ 研究者の申告: 「最初の第一回目は何と比較すればよいのかわからない」。
        #   ★ same のトライアルは 8 秒間まったくの無変化で、境目の印が音にも画面にも無かった。
        nx = strip_js_comments(extract_function(html, "abxBlindNext"))
        for label in ("準備中", "1 区間目", "2 区間目"):
            if label not in nx:
                raise Fail(f"相の表示『{label}』が abxBlindNext に無い（AB-D2 / AB-D3）")
        ph = strip_js_comments(extract_function(html, "abxPhase"))
        if "abx-blind-state" not in ph:
            raise Fail("abxPhase が画面に相を書いていない")
        # ⚠️★★★ レビュー実測の silent pass: textContent から `${label}` を落としても緑だった
        #   （★ 相の名前が画面に出ない ＝ 研究者の元の申告が再発する）。
        if not re.search(r'"abx-blind-state"\s*\)\s*\.textContent\s*=\s*[^;]*\blabel\b', ph):
            raise Fail("abxPhase が相の名前（label）を画面に書いていない")
        # ★ 残り秒を出す（★ 境目がいつ来るかが分からないと 1 区間目/2 区間目の区別が付かない）
        # ⚠️★★★ 「`phaseEndsAt` が本文にあるか」で見たら **silent pass だった**（meta が捕まえた）——
        #   ★ 代入 `bl.phaseEndsAt = ...` が同じ関数に居るので、**表示を消しても緑**になる。
        #   → ★ **「残りを計算していること」と「それを画面に書いていること」を別々に見る。**
        if not re.search(r"\bleft\s*=\s*Math\.max\(\s*0\s*,\s*bl\.phaseEndsAt", ph):
            raise Fail("abxPhase が残り時間を計算していない（境目の時刻が聴き手に分からない）")
        if not re.search(r'"abx-blind-state"\s*\)\s*\.textContent\s*=\s*[^;]*\bleft\b', ph):
            raise Fail("abxPhase が残り時間を画面に書いていない（計算しても出さなければ同じ）")

    @add("★★★ AB-D3: 盲検の提示に **音の印を足していない**（測っている差に別の差を混ぜない）")
    def _():
        # ★ 無音やビープを足すと「密度差を聞き分けた」のか「印の前後を聞き分けた」のかが混ざる。
        for name in ("abxBlindNext", "abxPhase"):
            fn = strip_js_comments(extract_function(html, name))
            for bad in ("createOscillator", "createBufferSource", "createNoise", "AudioBufferSource"):
                if bad in fn:
                    raise Fail(f"{name} が音を作っている（{bad}）。★ 境目は画面表示だけで示す（AB-D3）")
            # ★ master を落として無音区間を作る形も禁じる
            if re.search(r"master\.gain[^;]*0\s*[,)]", fn):
                raise Fail(f"{name} が master を落として無音区間を作っている（AB-D3）")

    @add("★★★ AB-D2: 相が state() に出る（跳びが準備区間に落ちたことを外から実測できる）")
    def _():
        # ⚠️★ 出さないと AC-1 / AC-4 を測れない。★ 「検査できる形で作る」を後付けにしない（S5-D11）
        body = strip_js_comments(html)
        m = re.search(r"blind:\s*abx\.blind\s*\?\s*\{(.*?)\}\s*:\s*null", body, re.S)
        if not m:
            raise Fail("state() が abx.blind を出していない")
        blk = m.group(1)
        # ⚠️★★★ 「`phase` が入っているか」で見たら **silent pass だった**（meta が捕まえた）——
        #   ★ `phaseLeftMs` が `phase` を**部分文字列として含む**ので、`phase:` を消しても緑になる。
        #   → ★ **鍵は「鍵として」照合する**（`名前:` の形で見る）。
        for key, src in (("phase", "abx.blind.phase"),
                         ("phaseLeftMs", None),
                         ("orderSeed", "abx.blind.orderSeed")):
            if not re.search(r"(?<![A-Za-z])" + key + r"\s*:", blk):
                raise Fail(f"state().abx.blind に {key} が無い（外から相を実測できない）")
            if src and src not in blk:
                raise Fail(f"state().abx.blind の {key} が {src} を指していない")

    @add("★★ AB-D2: 回答相以外の回答を受け付けない（ボタンを隠すだけを門番にしない）")
    def _():
        ans = strip_js_comments(extract_function(html, "abxAnswer"))
        m_gate = re.search(r'bl\.phase\s*!==\s*"answer"', ans)
        if not m_gate:
            raise Fail(
                "abxAnswer が相を確かめていない。"
                "★ ボタンの hidden だけが門番だと、相の外から回答が入りうる（S5-D6 と同じ型）"
            )
        # ⚠️★★★ レビュー実測の silent pass: 門番を `results.push` の **後ろ**へ動かしても
        #   文字列は在るので緑だった。★ 位置で見る（BF-5 の教訓）。
        m_push = re.search(r"bl\.results\.push\(", ans)
        if m_push and m_gate.start() > m_push.start():
            raise Fail("相の確認が結果の記録より後ろにある（★ 門番が空回りする）")

    @add("★★★ AB-D9: 『この dB を刺激の大きさと読んでよいか』が判定され、結果に残る")
    def _():
        # ⚠️★★★ 2026-08-13 に実際に踏んだ **穴 6**: BF-2 のゲートは **対照条件だけ**に効いていた。
        #   ★ abx_density × c_texture で盲検が走り、`measured_db: 0.247` が
        #     「コントラスト」として記録された。⚠️ c_texture は density_norm_exp = 0.5 ＝
        #     **エネルギー保存**で、**密度は変わるがレベルは変わらない。**
        #   → ★ BF-2 が「差が無いのに測った」なら、これは「差はあるが計器が見ていないのに
        #     計器の値を刺激の大きさとして記録した」。★ 向きが逆の同じ過ち。
        st = strip_js_comments(extract_function(html, "abxBlindStart"))
        if "density_norm_exp" not in st:
            raise Fail(
                "盲検の開始時に『レベルに出る写し方か』を見ていない。"
                "★ 判定は id ではなく density_norm_exp（設計上の正規化指数）から出す（AB-D9）"
            )
        if not re.search(r'abxOpt\(\)\.id === "abx_density"[^;]*levelBearing', st):
            raise Fail("abx_density で『レベルに出るのに比が小さい』条件を断っていない（AB-D9）")
        fin = strip_js_comments(extract_function(html, "abxBlindFinish"))
        # ⚠️★★ Codex 指摘: 対照条件（abx_level）は密度の写し方に関係なく measured_db が刺激量である。
        #   ★ 入れ忘れると `abx_level` × `c_texture` で false と誤記録される。
        if not re.search(r'contrastMeasurable\s*=\s*abxOpt\(\)\.id === "abx_level"', st):
            raise Fail(
                "contrastMeasurable が対照条件（abx_level）を見ていない。"
                "★ abx_level は比をマスタゲインに直接掛けるので、写し方に関係なく刺激量である（AB-D9）"
            )
        if not re.search(r"contrast_measurable:\s*bl\.contrastMeasurable", fin):
            raise Fail(
                "結果に contrast_measurable が残らない。"
                "★ 無いと『0.25 dB だったから読めなかった』と逆向きに誤読される（AB-D9）"
            )
        if "contrast_note" not in fin:
            raise Fail("contrast_measurable の意味を書いた注記が結果に無い")
        # ★ config 側: 判定の根拠になる density_norm_exp が全候補にあること
        for o in cfg["layer2_rework"]["density_cue"]["options"]:
            if "density_norm_exp" not in o:
                raise Fail(f"density_cue {o['id']} に density_norm_exp が無い（判定の根拠が消える）")

    @add("★★★ AB-D2: 盲検を中止する経路が **UI から到達できる**（安全機構を到達不能にしない）")
    def _():
        # ⚠️★★★ レビュー実測: `abx.blind = null` を書くのは invalidateAbxRatio だけで、
        #   その呼び出し元 4 つは **lockUI(true) で disabled になる**ラジオの onChange だった。
        #   ★ つまり盲検中は中止が原理的に発火せず、★ abxPhase の戻り値ガードは一度も走らない。
        #   ⚠️ tr_60 の 8 回は約 25 分あり、**止める手段が F5 しか無かった。**
        body = strip_js_comments(html)
        if "function abxBlindStop(" not in body:
            raise Fail("中止の単一経路 abxBlindStop() が無い")
        if 'id="btn-abx-stop"' not in html:
            raise Fail("中止ボタンが UI に無い（★ 中止経路が UI から到達できない）")
        if not re.search(r'"btn-abx-stop"\s*\)\s*\.addEventListener', body):
            raise Fail("中止ボタンが配線されていない")
        lk = strip_js_comments(extract_function(html, "lockUI"))
        # ★ 中止ボタンだけはロックの対象外（★ ロックすると止められない）
        if not re.search(r'"btn-abx-stop"\s*\)\s*\.disabled\s*=\s*!lock', lk):
            raise Fail("中止ボタンが lockUI で無効化されている（★ 止める手段が消える）")
        # ★ 「止める」でも盲検が中止されること（★ B7 だけ中止していた）
        stp = strip_js_comments(extract_function(html, "stop"))
        if "abxBlindStop(" not in stp:
            raise Fail(
                "stop() が瞬時 A/B の盲検を中止していない。"
                "★ 相は進み続け、**無音のまま回答が集まって正常に見える結果 JSON が書かれる**（BF-2 と同じ形）"
            )
        # ★ 相の待ちが「再生中か」も見ること
        ph = strip_js_comments(extract_function(html, "abxPhase"))
        if "playing" not in ph:
            raise Fail("abxPhase が再生中かを見ていない（停止しても相が進む）")

    @add("★★★ AB-D2: 盲検中は A/B の手動ボタンと①がロックされる（試行を書き換えられない）")
    def _():
        # ⚠️★★★ レビュー実測: btn-abx-a / -b / -off / -blind が lockUI に入っておらず、
        #   ★ `B` を 1 区間目で押せば **same の試行が事実上 diff になる**。記録も棄却もされない。
        #   ★ ax-l0gain が Step 4 から漏れていたのと同じ形。
        lk = strip_js_comments(extract_function(html, "lockUI"))
        for bid in ("btn-abx-a", "btn-abx-b", "btn-abx-off", "btn-abx-blind", "btn-abx-cal"):
            if f'"{bid}"' not in lk:
                raise Fail(f"{bid} が lockUI に入っていない（盲検中に刺激を書き換えられる）")
        # ★ ②の再入も断る（★ 進行中の列が無警告で捨てられる）
        st = strip_js_comments(extract_function(html, "abxBlindStart"))
        if not re.search(r"if\s*\(\s*abx\.blind\s*\)", st):
            raise Fail("abxBlindStart に再入ガードが無い（★ 進行中の列がデータごと消える）")

    @add("★★★ AB-D2: 盲検が終わったら abx.blind を手放す（①が二度と押せなくならない）")
    def _():
        # ⚠️★★★ レビュー実測: `cal.disabled = … || !!abx.blind` が 250 ms ごとに走るので、
        #   終了時に abx.blind を残すと **①が二度と押せなくなる**。
        #   ★ AB-D5 の「同じ条件で①を 3 回連続測る」がそもそも実行できない状態だった。
        fin = strip_js_comments(extract_function(html, "abxBlindFinish"))
        if not re.search(r"abx\.blind\s*=\s*null", fin):
            raise Fail(
                "abxBlindFinish が abx.blind を手放していない。"
                "★ describeLayer0Gain の cal.disabled が !!abx.blind を見るので①が押せなくなる"
            )

    @add("★★ AB-D5: 結果に版と時刻が残る（修正前後・測定時刻を取り違えない）")
    def _():
        fin = strip_js_comments(extract_function(html, "abxBlindFinish"))
        for key in ("protocol:", "started_at:", "finished_at:", "timing:"):
            if key not in fin:
                raise Fail(f"結果に {key} が無い（★ AB-D5 の時刻仮説を事後に検証できない）")
        # ⚠️★ 提示の時間構造そのもの（★ 修正前後の結果を取り違えないための鍵）
        for key, src in (("prep_seconds", "bl.prepSec"), ("seconds_per_side", "bl.sideSec")):
            if not re.search(key + r":\s*" + re.escape(src), fin):
                raise Fail(f"結果の {key} が {src} を指していない（★ 提示の時間構造が残らない）")
        ex = strip_js_comments(extract_function(html, "exportAbx"))
        if "stamp" not in ex:
            raise Fail("保存名に時刻が入っていない（★ 測り直しが同名になり上書きしうる）")

    @add("★★ AB-D2: 提示の相の長さが **凍結値**から出る（記録と提示が食い違わない）")
    def _():
        # ⚠️★ live 参照（abxSideSeconds()）だと、ロックが 1 つ外れた瞬間に
        #   JSON の prep_seconds / seconds_per_side と実際の提示が食い違う。
        nx = strip_js_comments(extract_function(html, "abxBlindNext"))
        if "abxSideSeconds()" in nx or "abxPrepSeconds()" in nx:
            raise Fail("abxBlindNext が相の長さを live 参照している（★ 記録は凍結値なので食い違う）")
        if "bl.sideSec" not in nx or "bl.prepSec" not in nx:
            raise Fail("abxBlindNext が凍結値（bl.sideSec / bl.prepSec）を使っていない")

    @add("★★ AB-D2: 所要時間の表示が準備区間を含んでいる（見積もりだけ古いまま残さない）")
    def _():
        d = strip_js_comments(extract_function(html, "describeRework"))
        # ⚠️★★★ 「本文に abxPrepSeconds() があるか」で見たら **silent pass だった**（meta が捕まえた）——
        #   ★ 同じ関数の**別の行**（fact の文言）が呼んでいるので、**見積もりから外しても緑**になる。
        #   → ★ **見積もりの式そのもの**を見る。
        m = re.search(r"\bmins\s*=\s*([^;]+);", d)
        if not m:
            raise Fail("所要時間の見積もり（mins）が describeRework に無い")
        if "abxPrepSeconds()" not in m.group(1):
            raise Fail(
                f"所要時間の見積もりに準備区間が入っていない（mins = {m.group(1).strip()}）。"
                "★ 1 トライアルは 3 相になった（AB-D2）"
            )

    @add("★★ AB-D2: 中止が相の途中でも効く（中止したのに次のトライアルが始まらない）")
    def _():
        ph = strip_js_comments(extract_function(html, "abxPhase"))
        # ⚠️★★★ 「本文に abx.blind !== bl があるか」で見たら **silent pass だった**（meta が捕まえた）——
        #   ★ 表示用 tick の中の同じ式が残るので、**戻り値を `return true;` にしても緑**になる。
        #   → ★ **呼び出し側が見るもの（戻り値）を名指しで見る。**
        # ★ 生存判定は `live()` の 1 か所から作る（★ 戻り値と表示 tick を同じ定義から出す・S5-D11）
        m_live = re.search(r"const\s+live\s*=\s*\(\)\s*=>\s*([^;]+);", ph)
        if not m_live:
            raise Fail("abxPhase に生存判定 live() が無い")
        expr = m_live.group(1)
        if "abx.blind === bl" not in expr:
            raise Fail(f"live() が中止（abx.blind = null）を見ていない: {expr.strip()}")
        if "playing" not in expr:
            raise Fail(f"live() が再生中かを見ていない: {expr.strip()}（★ 停止しても相が進む）")
        if not re.search(r"return\s+live\(\)\s*;", ph):
            raise Fail(
                "abxPhase の戻り値が live() になっていない。"
                "★ 呼び出し側は戻り値でしか中止を知れない"
            )
        if not re.search(r"if\s*\(\s*!live\(\)\s*\)\s*return", ph):
            raise Fail("abxPhase の表示 tick が中止後も画面を書き換えうる")
        nx = strip_js_comments(extract_function(html, "abxBlindNext"))
        if nx.count("if (!await abxPhase(") < 3:
            raise Fail(
                "abxBlindNext が abxPhase の戻り値を見ていない相がある。"
                "★ 中止しても残りの相が走り、次のトライアルが始まる"
            )

    @add("★★★ BF-6: 層 2 が粒を出していないまま測らせない（無音で盲検を回さない）")
    def _():
        body = strip_js_comments(html)
        w = strip_js_comments(extract_function(html, "layer2Status"))
        if "lastGrainStats" not in w and "_l2Watch" not in w:
            raise Fail("layer2Status が Worklet の実測カウンタを見ていない")
        upd = strip_js_comments(extract_function(html, "updateL2Watch"))
        # ★ 累積平均をそのまま使うと「昔たくさん出した」で緑になる。★ 微分していること
        if "_l2Watch.n" not in upd or "_l2Watch.t" not in upd:
            raise Fail(
                "updateL2Watch が累積カウンタを微分していない。"
                "★ grainsEmitted/seconds は **累積平均**なので、止まっていても当分は大きいまま"
            )
        cal = strip_js_comments(extract_function(html, "abxCalibrate"))
        if "layer2Status()" not in cal:
            raise Fail(
                "abxCalibrate が層 2 の実体を確かめずに測っている。"
                "★ 無音のまま測ると『差が無い』という結果だけが出る（BF-2 と同じ形）"
            )
        # ⚠️★★★ cross-review の HIGH: **「まだ分からない」を安全側に数えていないか。**
        #   ★ 実際に踏んだ形 —— `em !== null && em < 20` と書いたため、
        #     観測が確立していない 2〜4 秒の窓でガードが素通りしていた。
        if 'ls.state !== "ok"' not in cal:
            raise Fail(
                "層 2 の判定が『ok 以外は断る』になっていない。"
                "★ 未観測（unknown）を通す書き方だと、BF-6 を防ぐ機構自体に BF-6 と同じ穴が開く"
            )
        stt = strip_js_comments(extract_function(html, "layer2Status"))
        for st_name in ('"unknown"', '"silent"', '"off"', '"ok"'):
            if st_name not in stt:
                raise Fail(f"layer2Status が {st_name} を区別していない")

    @add("★★ 層 2 の観測が tick から更新されている")
    def _():
        if "updateL2Watch()" not in strip_js_comments(extract_function(html, "tick")):
            raise Fail("tick が層 2 の実体を更新していない（観測が更新されない）")

    @add("★★ 条件を変えたら『保存できる直前の結果』も道連れにする（古い結果を今のものと誤読させない）")
    def _():
        inv = strip_js_comments(extract_function(html, "invalidateAbxRatio"))
        if "abx.lastResult = null" not in inv or "btn-abx-export" not in inv:
            raise Fail(
                "invalidateAbxRatio が直前の結果と保存ボタンを片付けていない。"
                "★ 条件を変えた後も『いま保存できる = いまの条件の結果』と誤読されうる"
            )

    @add("★★ 実データ駆動中は①を測らない（比が実データ由来の値になる）")
    def _():
        cal = strip_js_comments(extract_function(html, "abxCalibrate"))
        if "isDataDriven()" not in cal:
            raise Fail(
                "abxCalibrate がデータ駆動中かを見ていない。"
                "★ 粒子率の書き手が CSV 側になり、measured_ratio が実データ由来になる（data-privacy）"
            )

    @add("★★★ S5-D4: buildGraph（LAYER0-CORE）に層 0 の音量つまみを埋め込んでいない")
    def _():
        fn = extract_function(html, "buildGraph")
        for bad in ("layer0GainOpt", "l0gain", "sel.l0"):
            if bad in fn:
                raise Fail(
                    f"buildGraph に {bad} が入っている。★ LAYER0-CORE は layer0.html との"
                    "逐語一致を保つ必要がある（S4-D8）"
                )

    @add("★★ つまみが段差でなく raised-cosine で移る（spec §2 ✗オンセット）")
    def _():
        fn = strip_js_comments(extract_function(html, "applyLayer0Gain"))
        if "setValueCurveAtTime" not in fn:
            raise Fail("つまみが setValueCurveAtTime を使っていない（段差になっている疑い）")
        if "0.5 - 0.5 * Math.cos" not in fn:
            raise Fail("raised-cosine の式が無い（端点の傾きが 0 でない曲線を使っている）")
        if "exponentialRampToValueAtTime" in fn:
            raise Fail(
                "exponentialRamp を使っている。★ **0 に到達できない**ので l0_off（倍率 0）が作れない"
            )
        if "CFG.envelope.glide_s" not in fn:
            raise Fail("切替の所要が envelope.glide_s から来ていない（他の候補切替と揃っていない）")

    @add("★★★ BF-3 と同じ形を塞ぐ: 校正が『切替の到達』を待つ")
    def _():
        cal = strip_js_comments(extract_function(html, "abxCalibrate"))
        # ⚠️★ 「`calRemainMs()` が本文のどこかにあるか」では **素通りした**（実測）——
        #   完了時の再チェックにも同じ呼び出しがあるので、**入口の門を消しても緑**だった。
        #   → ★ **入口の門そのもの**を名指しで見る。
        if "const rem = calRemainMs();" not in cal:
            raise Fail(
                "abxCalibrate の入口に calRemainMs() の門が無い。"
                "★ ランプ / morph の途中を端点として測る（2026-08-13 に実際に踏んだ BF-3）"
            )
        rem = strip_js_comments(extract_function(html, "calRemainMs"))
        for need in ("l0RampRemainMs", "l2MorphUntil"):
            if need not in rem:
                raise Fail(f"calRemainMs が {need} を見ていない（片方の待ちが抜ける）")

    @add("★★★ 層 2 側の morph も『到達待ち』の対象になっている（BF-3 の層 2 版）")
    def _():
        body = strip_js_comments(html)
        for fname in ("applyTimbre", "applyDensityCue"):
            fn = strip_js_comments(extract_function(html, fname))
            if "markL2Morph()" not in fn:
                raise Fail(f"{fname}() が markL2Morph() を呼んでいない（morph 途中を校正しうる）")
        mk = strip_js_comments(extract_function(html, "markL2Morph"))
        if "morph_s" not in mk:
            raise Fail("markL2Morph が morph_s を使っていない（待ち時間が実体と無関係）")

    @add("★★★ 条件を変えたら比が無効になる（前の倍率の比で盲検を始めさせない）")
    def _():
        body = strip_js_comments(html)
        inv = strip_js_comments(extract_function(html, "invalidateAbxRatio"))
        if "abx.ratio = null" not in inv:
            raise Fail("invalidateAbxRatio が比を消していない")
        if 'btn-abx-blind' not in inv:
            raise Fail("invalidateAbxRatio が盲検ボタンを無効化していない")
        # ★ 比が変わる 4 軸すべてから呼ばれていること
        # ⚠️★ 正規表現で `[^;]*?;` と書いたら **コールバック内の最初の `;` で切れて素通りした**（実測）。
        #   → ★ `radioGroup(` で分割し、**その呼び出しの本文そのもの**を見る。
        chunks = body.split("radioGroup(")[1:]
        for key in ("l0gain", "timbre", "dcue", "dspan"):
            hit = [c for c in chunks if f', "{key}",' in c.split("radioGroup(")[0]]
            if len(hit) != 1:
                raise Fail(f"軸 {key} の radioGroup 呼び出しが一意に見つからない（{len(hit)} 件）")
            if "invalidateAbxRatio" not in hit[0]:
                raise Fail(
                    f"軸 {key} を変えても比が無効化されない。"
                    "★ 別条件で測った比のまま盲検を始められてしまう（BF-2 と同じ形）"
                )

    @add("★★★ 比を測った条件と提示条件の一致を、盲検の開始時に実測している（門番を 2 枚にする）")
    def _():
        st = strip_js_comments(extract_function(html, "abxBlindStart"))
        if "abx.ratioCond" not in st:
            raise Fail("abxBlindStart が『比を測ったときの条件』を照合していない")
        # ⚠️★★★ cross-review の HIGH: **記録側と照合側が同じ定義から作られているか**。
        #   ★ 実際に踏んだ形 —— 記録は 7 鍵なのに照合は 4 鍵しか見ておらず、
        #     `l2-on` を外して盲検を始めると **全トライアルが無音**になるのに検出できなかった。
        cal = strip_js_comments(extract_function(html, "abxCalibrate"))
        if "currentAbxCond()" not in st or "currentAbxCond()" not in cal:
            raise Fail(
                "比の条件を記録する側と照合する側が同じ定義（currentAbxCond）を使っていない。"
                "★ 片方に鍵を足し忘れると、無音の条件で盲検が始まる（BF-2 の再発）"
            )
        cond = strip_js_comments(extract_function(html, "currentAbxCond"))
        for key in ("l2on", "map", "plan", "l0gain", "timbre", "dcue", "dspan"):
            if key not in cond:
                raise Fail(f"currentAbxCond が {key} を含んでいない（比を変えうる軸の取りこぼし）")
        # ⚠️★ `drift.length` の存在だけを見ていたら **`const drift = [];` に置き換えても緑**だった（実測）。
        #   ★ **比較そのもの**が実在することを見る（分岐の外殻ではなく中身）。
        if "rc[k] !== nowCond[k]" not in st:
            raise Fail("条件のずれを実際に比較していない（分岐はあるが中身が空回りしている）")
        if "drift.length" not in st:
            raise Fail("条件のずれを検出して止める分岐が無い")
        cal = strip_js_comments(extract_function(html, "abxCalibrate"))
        if "abx.ratioCond =" not in cal:
            raise Fail("abxCalibrate が測定時の条件を記録していない（照合の相手が存在しない）")

    @add("★★★ 盲検の結果に層 0 の倍率が残る（★ 本 Step の独立変数）")
    def _():
        fin = strip_js_comments(extract_function(html, "abxBlindFinish"))
        for need in ("layer0_gain", "layer0_gain_value"):
            if need not in fin:
                raise Fail(
                    f"結果 JSON に {need} が入らない。"
                    "★ どのコントラストで測った点数かが事後に特定できなくなる"
                )
        st = strip_js_comments(extract_function(html, "abxBlindStart"))
        if "l0gain: sel.l0gain" not in st:
            raise Fail("盲検の開始時に層 0 の倍率を固定していない（途中で触られると記録がずれる）")

    @add("★★ 既に効いている 3 点が層 0 の追加で空回りしていない（均衡 / 対照の差 / ピーク）")
    def _():
        body = strip_js_comments(html)
        # BF-4: 出題の均衡
        ordfn = strip_js_comments(extract_function(html, "buildAbxOrder"))
        if 'i < half ? "diff" : "same"' not in ordfn:
            raise Fail("出題の均衡が壊れている（BF-4）")
        # BF-2: 対照に差が無ければ始めない
        st = strip_js_comments(extract_function(html, "abxBlindStart"))
        if "Math.abs(db) < 0.5" not in st:
            raise Fail("対照の差ゼロを弾く分岐が消えている（BF-2）")
        # BF-1: ピークを見ている
        if "function samplePeak(" not in body or "clipWindows" not in body:
            raise Fail("ピーク / クリップの計器が消えている（BF-1）")

    @add("★★ __step4 が層 0 の『目標値』と『いま効いている値』を分けて出す")
    def _():
        body = strip_js_comments(html)
        if "layer0Gain: {" not in body:
            raise Fail("__step4.state() に layer0Gain が無い（外から実測できない）")
        if "graph.expr.gain.value" not in body:
            raise Fail("いま効いている値を AudioParam から読んでいない（目標値だけを出している）")

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
    cfg0, cfg_text0, html0, wk0, py0, s3html0, s3ver0, seed0, extra0 = base

    def mut_cfg(fn):
        c = copy.deepcopy(cfg0)
        fn(c)
        return (c, json.dumps(c, ensure_ascii=False), html0, wk0, py0, s3html0, s3ver0, seed0, extra0)

    def mut_html(old, new):
        return (cfg0, cfg_text0, html0.replace(old, new), wk0, py0, s3html0, s3ver0, seed0, extra0)

    def mut_wk(old, new):
        return (cfg0, cfg_text0, html0, wk0.replace(old, new), py0, s3html0, s3ver0, seed0, extra0)

    def mut_file(name, old, new):
        """★ 混入検査の走査対象（run.sh / notes.md / data.md / 検査自身）を壊す。

        ⚠️★★★ この helper が無いと、**走査対象を増やしても「壊して赤くなるか」を実測できない。**
        ★ 2026-08-14 に `run.sh` の実セッション名が 1 日以上見つからなかったのは、
          まさに「その範囲を見る検査が無い」状態だったからである。
        """
        e = dict(extra0)
        if e.get(name) is None:
            raise SystemExit(f"meta: 走査対象 {name} が読めていない")
        e[name] = e[name].replace(old, new) if old else e[name] + new
        return (cfg0, cfg_text0, html0, wk0, py0, s3html0, s3ver0, seed0, e)

    def mut_both(old, new):
        """★ step4.html と layer0.html に **同じ**変更を入れる。

        ⚠️★ LAYER0-CORE を片側だけ壊すと **S4-D8 の一致検査が先に発火する**ので、
        ★ その先にある検査（例: S5-D4「つまみをコアに埋め込まない」）を試したことにならない。
        → ★ 両側を揃えて壊し、**一致していても駄目なもの**を検査できていることを確かめる。
        """
        return (cfg0, cfg_text0, html0.replace(old, new), wk0, py0,
                s3html0.replace(old, new), s3ver0, seed0, extra0)

    def plan(c, pid):
        return next(p for p in c["separation_plans"]["options"] if p["id"] == pid)

    cases: list[tuple[str, tuple, str]] = [
        ("版を config 側だけずらす",
         mut_cfg(lambda c: c.update(expr_version="9.9.9-bogus")), "expr_smooth.py"),
        ("Step 3 の config を追随させ忘れる",
         (cfg0, cfg_text0, html0, wk0, py0, s3html0, "0.2.0-step3", seed0, extra0), "追随"),
        # ⚠️ 3 箇所すべてを据え置く。★ 1 箇所だけ戻すと**先に一致検査が落ちる**ので
        #    「上がっているか」の検査を試したことにならない（実測で踏んだ）。
        ("版を 3 箇所とも Step 3 のまま据え置く",
         ({**copy.deepcopy(cfg0), "expr_version": PREV_VERSION},
          cfg_text0, html0, wk0, PREV_VERSION, s3html0, PREV_VERSION, seed0, extra0),
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
         (cfg0, cfg_text0 + "\n非周期\n", html0, wk0, py0, s3html0, s3ver0, seed0, extra0), "非周期"),
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
          wk0, py0, s3html0, s3ver0, seed0, extra0),
         "実時間再生に検証専用レート"),
        ("★ 系統切替で CSV を読み直さない形に戻す",
         mut_html("async function reparseCsv(", "async function reparseGone("), "読み直していない"),
        ("SEED から seed を消す",
         (cfg0, cfg_text0, html0, wk0, py0, s3html0, s3ver0, "seed なし", extra0), "SEED"),

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

        # ---- ★★★ Step 5（層 0 の音量つまみ）------------------------------
        ("★★★ 層 0 の既定を 0.5 にする（既定で音が変わる）",
         mut_cfg(lambda c: c["layer0_gain"].update(default="l0_half")), "既定は 1.0"),
        ("★★★ 層 0 の候補から 0（対照）を消す",
         mut_cfg(lambda c: c["layer0_gain"].__setitem__(
             "options", [o for o in c["layer0_gain"]["options"] if o["gain"] != 0.0])),
         "層 0 を取り去った条件"),
        ("★ 層 0 の候補に 1 を超える倍率を足す",
         mut_cfg(lambda c: c["layer0_gain"]["options"].append(
             {"id": "l0_boost", "gain": 1.5, "label": "x", "fact": "x"})), "0..1 の外"),
        ("★★★ 『予測であって実測ではない』の断り書きを消す",
         mut_cfg(lambda c: c["layer0_gain"].__setitem__(
             "_predicted_contrast_note", ["★ 予測です"])), "予測を実測欄に書かせない"),
        ("★★★ expr.gain の書き手を 2 つにする",
         mut_html("  applyLayer0Gain(true);",
                  "  applyLayer0Gain(true); graph.expr.gain.setValueAtTime(1, now);"),
         "書き手は applyLayer0Gain"),
        ("★★ つまみを段差（setValueAtTime 一発）に変える",
         mut_html("    p.setValueCurveAtTime(curve, now, dur);",
                  "    p.setValueAtTime(to, now);"), "setValueCurveAtTime を使っていない"),
        ("★★ つまみの raised-cosine を線形に変える",
         mut_html("      const w = 0.5 - 0.5 * Math.cos(Math.PI * (i / (N - 1)));   // ★ raised-cosine",
                  "      const w = i / (N - 1);"), "raised-cosine の式が無い"),
        ("★★★ 校正が切替の到達を待たなくなる（BF-3 を戻す）",
         mut_html("  const rem = calRemainMs();\n  if (rem > 0) {",
                  "  const rem = 0;\n  if (rem > 0) {"), "入口に calRemainMs() の門が無い"),
        ("★★★ calRemainMs が層 2 の morph を見なくなる",
         mut_html("                  Math.max(0, l2MorphUntil - now),", "                  0,"),
         "l2MorphUntil を見ていない"),
        ("★★★ applyDensityCue が morph の到達を記録しない",
         mut_html("    densityNormExp: reworkOpt(\"dcue\").density_norm_exp } });\n  markL2Morph();",
                  "    densityNormExp: reworkOpt(\"dcue\").density_norm_exp } });"),
         "markL2Morph() を呼んでいない"),
        ("★★★ 層 0 を変えても比が無効化されない（別条件の比で盲検を始められる）",
         mut_html('(o) => { invalidateAbxRatio("層 0 の音量を " + o.label + " に変えた");\n'
                  "                      applyLayer0Gain(); describeLayer0Gain(); }",
                  "(o) => { applyLayer0Gain(); describeLayer0Gain(); }"), "比が無効化されない"),
        # ---- ★★★ BF-5（起動時の no-op）とその周辺 ----------------------
        ("★★★ BF-5: 起動時の適用を playing = true より前へ戻す（完全な no-op になる）",
         mut_html("  applyPlan(); applyRate();\n  playing = true; startedAt = performance.now();",
                  "  applyPlan(); applyRate();\n  applyLayer0Gain(true);\n"
                  "  playing = true; startedAt = performance.now();"),
         "完全な no-op"),
        ("★★★ 実行時の『目標 vs 実効』照合を外す",
         mut_html("  const mm = layer0GainMismatch();\n  if (mm) {",
                  "  const mm = null;\n  if (mm) {"), "実効倍率を確かめずに測っている"),
        ("★★★ control() に 2 人目の書き手を足す（.value 代入）",
         mut_html("  samplePeak();", "  graph.expr.gain.value = 1;\n  samplePeak();"),
         "書き手は applyLayer0Gain"),
        ("★★★ master の落ち着きを待たなくする（フェードイン中に測れてしまう）",
         mut_html("                  Math.max(0, masterSettleUntil - now));",
                  "                  0);"), "masterSettleUntil を見ていない"),
        ("★★ 盲検が live の比を読むように戻す（途中で条件を変えると結果が消える）",
         mut_html("  const blRatio = bl.ratio, blDb = 20 * Math.log10(blRatio);",
                  "  const blRatio = abx.ratio, blDb = 20 * Math.log10(abx.ratio);"),
         "live の abx.ratio を読んでいる"),
        ("★★ lockUI から層 0 の軸を外す（盲検中にレベルを変えられる）",
         mut_html('"ax-l0gain", "ax-timbre", "ax-dcue", "ax-dspan"', '"ax-timbre", "ax-dcue", "ax-dspan"'),
         "ax-l0gain が lockUI に入っていない"),
        ("★★ A/B の保存経路を消す（閾値の記録が残らない）",
         mut_html("function exportAbx(", "function exportAbxGone("), "保存経路が無い"),
        ("★★ データ駆動中でも①を測れるようにする",
         mut_html("  if (isDataDriven()) {", "  if (false) {"), "データ駆動中かを見ていない"),
        ("★★★ BF-6: 無音の層 2 でも①を測れるようにする",
         mut_html("  const ls = layer2Status();", "  const ls = { state: 'ok' };"),
         "層 2 の実体を確かめずに測っている"),
        # ---- ★★★ cross-review（Claude ＋ Codex 一致）の HIGH 2 件 -----------
        ("★★★ 照合を 4 鍵だけに戻す（l2-on を外して盲検を始められる＝全トライアル無音）",
         mut_html("  const nowCond = currentAbxCond();   // ★ 記録側と同じ定義（7 鍵すべてを照合する）",
                  "  const nowCond = { l0gain: sel.l0gain, timbre: sel.timbre,"
                  " dcue: sel.dcue, dspan: sel.dspan };"),
         "同じ定義（currentAbxCond）を使っていない"),
        ("★★★ currentAbxCond から l2on を落とす（無音条件が検出されなくなる）",
         mut_html("           map: $(\"l2-map\").checked, l2on: $(\"l2-on\").checked, plan: sel.plan };",
                  "           map: $(\"l2-map\").checked, plan: sel.plan };"),
         "currentAbxCond が l2on を含んでいない"),
        ("★★★ 未観測（unknown）を素通りさせる（BF-6 ガードに同じ穴を開ける）",
         mut_html('  if (ls.state !== "ok") {', '  if (ls.state === "silent") {'),
         "『ok 以外は断る』になっていない"),
        ("★★ 条件変更で直前の結果を片付けない",
         mut_html("  if (abx.lastResult) { abx.lastResult = null;"
                  ' $("btn-abx-export").disabled = true; }', ""),
         "直前の結果と保存ボタンを片付けていない"),
        ("★★★ BF-6: 層 2 の観測を累積平均のまま使う（止まっても当分は大きいまま）",
         mut_html("  if (dt > 1.5) _l2Watch = { t, n, rate: (n - _l2Watch.n) / dt };",
                  "  if (dt > 1.5) _l2Watch = { t, n, rate: lastGrainStats.rate };"),
         "累積カウンタを微分していない"),
        ("★★★ 盲検の開始時に条件の一致を照合しない（門番を 1 枚に減らす）",
         mut_html("  const drift = Object.keys(nowCond).filter((k) => rc[k] !== nowCond[k]);",
                  "  const drift = [];"), "実際に比較していない"),
        ("★★★ 結果 JSON から層 0 の倍率を落とす",
         mut_html("    layer0_gain: bl.l0gain, layer0_gain_value: bl.l0gainValue,", ""),
         "事後に特定できなくなる"),
        ("★★ __step4 から層 0 の実効値を落とす",
         mut_html("      layer0Gain: {", "      layer0GainRemoved: {"), "layer0Gain が無い"),
        # ⚠️★ 片側だけ壊すと S4-D8 の一致検査が先に発火して S5-D4 を試せない（実測）。
        #   → ★ **両側に同じ変更**を入れ、「一致していてもコアに埋め込んではならない」ことを検査する
        ("★★★ buildGraph につまみを埋め込む（★ Step 3 側にも同じ変更を入れて一致は保つ）",
         mut_both("  const expr   = ctx.createGain(); expr.gain.value = 1;",
                  "  const expr   = ctx.createGain(); expr.gain.value = layer0GainOpt().gain;"),
         "LAYER0-CORE"),
        # ---- ★★★ 盲検の提示手順（AB-D1〜AB-D6）------------------------------
        #
        # ⚠️★★★ AB-D0: この 3 件は **既存の検査 103 件を全部緑のまま素通り**した。
        #   ★ 以下は「壊し方」を **系列の側**（順序・持ち越し・反復）から与える。
        ("★★★ AB-D1: 固定 order_seed を config に戻す（毎回同じ出題順に戻る）",
         mut_cfg(lambda c: c["layer2_rework"]["abx"]["blind"].update(order_seed=20260813)),
         "order_seed が復活している"),
        ("★★★ AB-D1: order_seed を消した理由を config から消す（次の人が戻す）",
         mut_cfg(lambda c: c["layer2_rework"]["abx"]["blind"].pop("_order_seed_removed_why")),
         "消した理由が config に残っていない"),
        ("★★★ AB-D1: seed を引き直さず固定値に戻す",
         mut_html("  const orderSeed = drawOrderSeed();", "  const orderSeed = 20260813;"),
         "seed を引き直していない"),
        ("★★★ AB-D1: 引いた seed を結果に残さない（出題順が再構成できなくなる）",
         mut_html("    order_seed: bl.orderSeed,", ""), "bl.orderSeed を指していない"),
        # ⚠️★★★ **本命の変異**: 交絡そのものを戻す。
        # ---- ★★★ S5C-D1（A′）: 準備区間から状態変化を消したことの変異 ------------
        #
        # ⚠️★★★ 上の 3 版（初版 / AB-D2 / AB-D7）はすべて「跳びをどこへ置くか」の変異だった。
        #   ★ A′ は **跳びを置かない**ので、変異の形も「跳びを 1 つ足す」に変わる。
        ("★★★ S5C-D1: 準備区間に跳びを 1 つ戻す（向きと偶奇が入場状態を運ぶ＝AB-D10 の再発）",
         mut_html('  if (!await abxPhase(bl, "prep", bl.prepSec * 1000, "準備中（まだ判定しません）")) return;',
                  '  abxSetInstant("A");\n'
                  '  if (!await abxPhase(bl, "prep", bl.prepSec * 1000, "準備中（まだ判定しません）")) return;'),
         "準備区間 / 1 区間目で `abxSetInstant()` を呼んでいる"),
        ("★★★ S5C-D1: 切替を 1 区間目より前へ動かす（採点区間が両方 2 区間目の状態になる）",
         mut_html('  if (!await abxPhase(bl, "i1", ms, "1 区間目")) return;\n'
                  "  abxSet(to);",
                  "  abxSet(to);\n"
                  '  if (!await abxPhase(bl, "i1", ms, "1 区間目")) return;'),
         "準備区間 / 1 区間目で `abxSet()` を呼んでいる"),
        ("★★★ S5C-D1: 到達点を持ち越さない（1 区間目が毎回同じ状態に戻り、終点が固定される）",
         mut_html("  bl.state = to;", ""), "持ち越していない"),
        ("★★★ S5C-D1: 1 区間目の状態を固定に戻す（AB-D10 の恒等式が復活する）",
         mut_html("  const from = bl.state;", '  const from = "A";'),
         "bl.state（持ち越した到達点）から来ていない"),
        ("★★★ S5C-D1: 2 区間目の状態をリテラルで書く（終点固定＝跳びの偶奇が入場状態になる）",
         mut_html("  abxSet(to);", '  abxSet(kind === "diff" ? "B" : "A");'),
         "リテラルで指定している"),
        ("★★★ S5C-D1: 開始状態の定義を消す（②の入口の状態が不定になり、状態列が復元できない）",
         mut_html("  abxSetInstant(initialState);\n  lockUI(true);", "  lockUI(true);"),
         "実際に鳴らす開始状態が initialState から作られていない"),
        ("★★★ S5C-D1: 各トライアルの from / to を記録しない（方向の均衡を事後に検算できない）",
         mut_html("  t.from = from; t.to = to;", ""), "状態を記録していない"),
        ("★★★ S5C-D1: 開始状態を結果に残さない（状態列が復元できない）",
         mut_html("    initial_state: bl.initialState,\n", ""), "開始状態を結果に残していない"),
        ("★★ AB-D2: prep_seconds を config から消す",
         mut_cfg(lambda c: c["layer2_rework"]["abx"]["blind"].pop("prep_seconds")),
         "prep_seconds が config に無い"),
        ("★★★ AB-D2: 相の表示から『2 区間目』を落とす（境目が分からなくなる）",
         mut_html('"2 区間目")) return;', '"")) return;'), "2 区間目"),
        ("★★★ AB-D2: 残り秒を出さない（境目がいつ来るか分からない）",
         mut_html("    const left = Math.max(0, bl.phaseEndsAt - performance.now());\n"
                  "    $(\"abx-blind-state\").textContent = `${head} — ${label}（あと ${(left / 1000).toFixed(1)} 秒）`;",
                  "    $(\"abx-blind-state\").textContent = `${head} — ${label}`;"),
         "残り時間を計算していない"),
        ("★★★ AB-D3: 境目にビープを足す（測っている差に別の差を混ぜる）",
         mut_html("  tick();\n  const iv = setInterval(tick, 100);",
                  "  ctx.createOscillator().start();\n  tick();\n  const iv = setInterval(tick, 100);"),
         "音を作っている"),
        ("★★★ AB-D2: state() から相を落とす（跳びの落ち先を外から実測できなくなる）",
         mut_html("                                  phase: abx.blind.phase,", ""), "phase が無い"),
        ("★★ AB-D2: 回答相の確認を外す（相の外から回答が入る）",
         mut_html('  if (bl.phase !== "answer") return;', ""), "相を確かめていない"),
        ("★★ AB-D2: 所要時間の見積もりから準備区間を落とす",
         mut_html("  const mins = (B.trials * (abxPrepSeconds() + abxSideSeconds() * 2)) / 60;",
                  "  const mins = (B.trials * abxSideSeconds() * 2) / 60;"),
         "準備区間が入っていない"),
        ("★★ AB-D2: 中止の確認を外す（中止しても次のトライアルが始まる）",
         mut_html("  return live();", "  return true;"), "戻り値が live() になっていない"),
        ("★★ AB-D2: 中止後も表示 tick が画面を書き換える",
         mut_html("    if (!live()) return;\n", ""), "中止後も画面を書き換えうる"),
        # ---- ★★★ 絶対パス検査の検出漏れ（security-checker 指摘・2026-08-13）------
        # ⚠️★★★ **旧パターンはこの 4 形式を取り逃していた**（実測）。
        #   ★ 「検査を直した」と言うなら、**取り逃していた形そのもの**で赤くなることを実測する。
        # ⚠️★ アンカーは **LAYER0-CORE の外**に取る（★ 中に入れると S4-D8 の一致検査が先に発火し、
        #   目的の検査を試したことにならない —— S5-8 で実測した形）。
        #   ⚠️★★ 最初 `<!-- LAYER0-CORE:BEGIN` を使ったら **実在しない文字列**だったので置換が no-op になり、
        #   ★ **silent pass を自分で作った**（meta が捕まえた）。★ アンカーの実在も確かめること。
        ("★★★ 散文中の Windows パスを player に混ぜる（旧パターンは取り逃した）",
         mut_html('<p class="note" id="abx-result">',
                  "<!-- out C:" + "\\" + "GSE-out" + "\\" + 'x.json -->\n  <p class="note" id="abx-result">'),
         "player に絶対パス/ユーザー名/実セッション名"),
        ("★★★ 別ユーザー名の Windows パスを混ぜる（ハードコード名では捕まらない）",
         mut_html('<p class="note" id="abx-result">',
                  "<!-- C:" + "\\" + "Users" + "\\" + "alice" + "\\" + 'x -->\n  <p class="note" id="abx-result">'),
         "player に絶対パス/ユーザー名/実セッション名"),
        ("★★★ macOS の home パスを混ぜる（旧パターンに /Users/ の形が無かった）",
         mut_html('<p class="note" id="abx-result">',
                  '<!-- /Users/someone/Documents/x -->\n  <p class="note" id="abx-result">'),
         "player に絶対パス/ユーザー名/実セッション名"),
        ("★★★ config 側に絶対パスを混ぜる（旧実装は config を 1 バイトも見ていなかった）",
         mut_cfg(lambda c: c["layer2_rework"]["abx"]["blind"].__setitem__(
             "_out_dir", "C:/GSE-out/results")),
         "config に絶対パス"),
        # ---- ★★★ 走査範囲を広げたことの実測（security-checker 指摘・2026-08-14）--------
        # ⚠️★★★ **run.sh に実セッション名が 2 件あり、1 日以上どの検査にも見られていなかった。**
        #   ★ 旧実装が見ていたのは player / worklet / config の 3 つだけ。
        #   → ★ 「事故が起きた当のファイルを見ていない検査は、何も守っていない。」
        # ⚠️★★★ **見本は必ず連結で作る。** ★ そのまま書くと
        #   「検査自身の走査」が自分の変異データに反応して赤くなる（★ 実測で 1 回踏んだ）。
        #   ★ 既存の絶対パスの変異が `"C:" + "\\" + …` と書いてあるのと同じ理由・同じ形。
        # ⚠️★★★ 2026-08-14 `/cross-review`（HIGH）—— ★ ここには **実在の識別子**が入っていた。
        #   ★ 連結なので混入検査は 1 バイトも見ておらず、**外部 LLM へそのまま出た。**
        #   → ★ 見本は `FAKE_SESSION`（架空・1 か所定義）だけを使う。
        #     ★ 「連結しても架空名しか置けない」は `_fixtures_hide_no_real_session` が実測で縛る。
        ("★★★ run.sh に実セッション名を戻す（★ 実際に混入していた形そのもの）",
         mut_file("run.sh", "# ---------------------------------------------------------------------------\ncmd_data()",
                  "# 例: " + FAKE_SESSION + "\ncmd_data()"),
         "run.sh に絶対パス/ユーザー名/実セッション名"),
        ("★★★ run.sh に絶対パスを混ぜる（★ run.sh は実行されるコードなので全パターンを当てる）",
         mut_file("run.sh", 'PY="${PYTHON:-python}"', 'PY="C:/Python/python.exe"'),
         "run.sh に絶対パス"),
        ("★★★ notes.md に実セッション名を混ぜる（★ 散文でも実名は正当な出番が無い）",
         mut_file("notes.md", "", "\n★ 素材: " + FAKE_SESSION + "\n"),
         "notes.md に絶対パス/ユーザー名/実セッション名"),
        ("★★★ data.md に実セッション名を混ぜる（★ 「パスを書かない」と宣言している当のファイル）",
         mut_file("data.md", "", "\n★ 対象: " + FAKE_SESSION + "\n"),
         "data.md に絶対パス/ユーザー名/実セッション名"),
        ("★★★ 検査自身に実セッション名を混ぜる（★ 2026-08-13 の事故と同じ形）",
         mut_file("step4_selftest.py", "", "\n# 例: " + FAKE_SESSION + "\n"),
         "step4_selftest.py に絶対パス/ユーザー名/実セッション名"),
        # ⚠️★★★ 2026-08-14 `/cross-review`（HIGH）の再発検査 ——
        #   ★ **上の 4 件は「組み立て済み」の形しか試していなかった。**
        #   ★ 実際に事故った形は **連結（`"P010" + "_gse_" + "…"`）** であり、
        #     ⚠️ **その形は 4 件の変異のどれでも赤くならなかった。**
        # ⚠️★★ 見本を**リテラルで書かない**（★ 書くと新しい検査が自分自身に反応して常に赤くなる）。
        #   → ★ `FAKE_SESSION` から**実行時に**作り、連結の**ソース表記**へ組み立て直す。
        ("★★★ 検査自身に『連結で隠した』実セッション名を混ぜる（★ 実際に外部送信された形）",
         mut_file("step4_selftest.py", "",
                  "\n# 例: " + _concat_src(FAKE_SESSION.replace("P999", "P123").replace("20000101", "20260101")) + "\n"),
         "検査自身が連結で実セッション名らしき文字列を隠し持っている"),
        # ⚠️★★★ 2026-08-14 `/cross-review`（HIGH）—— ★ **暗黙連結（`+` 無し）で書いた形**。
        #   ★ 旧実装（`+` 必須）はこれを素通りし、`secrets-filter.sh` も改行で分ければ素通りした。
        ("★★★ 検査自身に『暗黙連結（+ 無し）で隠した』実セッション名を混ぜる",
         mut_file("step4_selftest.py", "",
                  "\n# 例: " + _concat_src(
                      FAKE_SESSION.replace("P999", "P456").replace("20000101", "20260202"),
                      joiner=" ") + "\n"),
         "検査自身が連結で実セッション名らしき文字列を隠し持っている"),
        ("★★★ 自己走査の除外区間の目印を消す（★ 除外が no-op になり自分の正規表現に反応する）",
         mut_file("step4_selftest.py", "# ---- PII-PATTERNS:END ----", "# ---- (removed) ----"),
         "除外区間の目印が実在しない"),
        ("★★★ 走査対象を 1 つ黙って消す（★ 対象が消えたのに緑のまま、を作らない）",
         mut_file("run.sh", "", "") if False else
         (cfg0, cfg_text0, html0, wk0, py0, s3html0, s3ver0, seed0,
          {**extra0, "data.md": None}),
         "data.md が無い"),
        # ---- ★★★ code-reviewer が実測で見つけた silent pass 7 件（2026-08-13）--------
        # ⚠️★★★ **7 件とも「壊しても緑」だった。** ★ 直した検査が本当に赤くなることをここで実測する。
        ("★★★ M1: 引いた seed を abx.blind に載せない（order_seed が undefined になる）",
         mut_html("                orderSeed,\n", ""), "abx.blind に載せていない"),
        ("★★★ M2: 準備区間の床を 0 にする（AB-D6 の後継が丸ごと無効化される）",
         mut_html("  return Math.max(B.prep_seconds, 2.0);", "  return Math.max(B.prep_seconds, 0);"),
         "準備区間の床が短すぎる"),
        ("★★★ M3: 相の名前を画面から落とす（研究者の元の申告が再発する）",
         mut_html("`${head} — ${label}（あと ${(left / 1000).toFixed(1)} 秒）`",
                  "`${head}（あと ${(left / 1000).toFixed(1)} 秒）`"),
         "相の名前（label）を画面に書いていない"),
        ("★★★ M4: 提示の時間構造を結果から落とす",
         mut_html("    prep_seconds: bl.prepSec, seconds_per_side: bl.sideSec,", ""),
         "prep_seconds が bl.prepSec を指していない"),
        ("★★★ M5: 持ち越しを 1 回目だけにする（2 回目以降が固定の基準に戻る・行は残る）",
         mut_html("  bl.state = to;", "  if (bl.i === 0) bl.state = to;"),
         "条件分岐の中にある"),
        ("★★★ M6: 記録する seed を固定値にする（記録が嘘になる）",
         mut_html("    order_seed: bl.orderSeed,", "    order_seed: 20260813,"),
         "bl.orderSeed を指していない"),
        ("★★★ M7: 相の門番を結果の記録より後ろへ動かす（門番が空回りする）",
         mut_html('  if (bl.phase !== "answer") return;\n  const truth = bl.order[bl.i];\n'
                  "  bl.results.push({ index: bl.i, truth, answer: ans, correct: truth === ans });",
                  "  const truth = bl.order[bl.i];\n"
                  "  bl.results.push({ index: bl.i, truth, answer: ans, correct: truth === ans });\n"
                  '  if (bl.phase !== "answer") return;'),
         "結果の記録より後ろ"),
        # ---- ★★★ AB-D7（真値の漏れ）と中止経路 -----------------------------------
        ("★★★ S5C-D1: 2 区間目の切替を即座にする（遷移時間という独立変数が黙って無効になる）",
         mut_html("  abxSet(to);", "  abxSetInstant(to);"),
         "abxSet(to)（遷移時間を守る側）になっていない"),
        ("★★★ S5C-D1: trials を 10 にする（diff が 5 回＝奇数になり、上下の均衡が崩れる）",
         mut_cfg(lambda c: c["layer2_rework"]["abx"]["blind"].update(trials=10)),
         "均衡しない"),
        # ---- ★★★ code-reviewer が実測で見つけた穴（2026-08-14）------------------------
        # ⚠️★★★ **下の 6 件はすべて「123 件が全部緑のまま」通っていた形である。**
        ("★★★ HIGH: 2 区間目の状態を交互にしない（★ 式の形は保ったまま不変量だけ壊す）",
         mut_html('  const to = kind === "diff" ? (from === "A" ? "B" : "A") : from;',
                  '  const to = kind === "diff" ? (from === "B" ? "B" : "B") : from;'),
         "diff なのに反転していない"),
        ("★★★ HIGH: 盲検中も abx-now に状態を書く（★ 真値が読むだけで分かる）",
         mut_html('  $("abx-now").textContent = abx.blind\n    ? "盲検中（★ 提示条件は伏せています）"\n    : (abx.active',
                  '  $("abx-now").textContent = (abx.active'),
         "盲検中かどうかを見ずに"),
        ("★★★ HIGH: 盲検中の表示に状態を混ぜる（★ 分岐を足しただけでは足りない）",
         mut_html('    ? "盲検中（★ 提示条件は伏せています）"', "    ? `盲検中 ${abx.state}`"),
         "伏せたことにならない"),
        ("★★★ MEDIUM: 区間の長さを真値で変える（★ 耳を使わずに答えが出る）",
         mut_html('  const ms = bl.sideSec * 1000;',
                  '  const ms = bl.sideSec * 1000 + (kind === "diff" ? 500 : 0);'),
         "区間の長さが真値から作られている"),
        ("★★★ MEDIUM: 開始状態を固定に戻す（★ 1 回目の diff が必ず上向きになる錨）",
         mut_html('  const initialState = drawOrderSeed() % 2 === 0 ? "A" : "B";',
                  '  const initialState = "A";'),
         "開始状態が乱数で引かれていない"),
        ("★★★ MEDIUM: 記録する開始状態だけを別リテラルにする（★ 記録が嘘になる）",
         mut_html("                state: initialState, initialState,",
                  '                state: initialState, initialState: "A",'),
         "同じ変数から作られていない"),
        ("★★★ MEDIUM: 準備区間の状態変更をヘルパ経由にする（★ abxSet* を探すだけでは素通り）",
         mut_html("  const from = bl.state;", "  hiddenReset();\n  const from = bl.state;"),
         "を呼んでいる"),
        ("★★★ S5C-D6: 承知の印を見ずに始める（★ 2026-08-13 と 08-14 に実際に起きた取り違え）",
         mut_html('    if (!$("abx-texture-ack").checked) {', "    if (false) {"),
         "承知の印を見ずに盲検が始まる"),
        ("★★★ S5C-D6: 承知が無くても止めずに続ける（★ 警告だけでは 2 回とも防げなかった）",
         mut_html('      $("abx-result").textContent = msg; logLine(msg); return;\n    }\n    logLine(`⚠️★★★ 密度の写し方',
                  '      $("abx-result").textContent = msg; logLine(msg);\n    }\n    logLine(`⚠️★★★ 密度の写し方'),
         "止めていない"),
        ("★★★ S5C-D6: 条件の札を盲検の画面から落とす（★ 走行中に条件が見えなくなる）",
         mut_html("  const head = `${bl.i + 1} / ${bl.order.length} 回目［${bl.condTag}］`;",
                  "  const head = `${bl.i + 1} / ${bl.order.length} 回目`;"),
         "条件の札を出していない"),
        ("★★★ S5C-D5: 方向の均衡を結果に残さない（★ 提示が壊れても事後に分からない）",
         mut_html("    direction_balance: bl.directionBalance,\n", ""),
         "結果 JSON に残していない"),
        ("★★★ S5C-D5: 方向が均衡していないことを画面に出さない（★ 壊れた提示が黙って通る）",
         mut_html("    (bl.directionBalance.ok ? \"\"", '    (true ? ""'),
         "画面に出していない"),
        ("★★★ 中止ボタンを lockUI で無効化する（25 分の盲検を止める手段が消える）",
         mut_html('  $("btn-abx-stop").disabled = !lock;', '  $("btn-abx-stop").disabled = lock;'),
         "中止ボタンが lockUI で無効化"),
        ("★★★ stop() が盲検を中止しない（無音のまま回答が集まる・BF-2 と同じ形）",
         mut_html('  abxBlindStop("再生が止められたため中止しました");', ""),
         "stop() が瞬時 A/B の盲検を中止していない"),
        ("★★★ A/B の手動ボタンを lockUI から外す（same の試行を diff に書き換えられる）",
         mut_html('   "btn-abx-cal", "btn-abx-a", "btn-abx-b", "btn-abx-off", "btn-abx-blind"]',
                  '   "btn-abx-cal"]'),
         "lockUI に入っていない"),
        ("★★★ ②の再入ガードを外す（進行中の列がデータごと消える）",
         mut_html("  if (abx.blind) { logLine(\"⚠️ 盲検は実行中です（★ 中止するなら「盲検を中止」）\"); return; }", ""),
         "再入ガードが無い"),
        ("★★★ 終了時に abx.blind を残す（①が二度と押せなくなる）",
         mut_html("  abx.blind = null;\n}\n\n/**\n * ★★★ 瞬時 A/B の結果を保存する（Step 5）。",
                  "}\n\n/**\n * ★★★ 瞬時 A/B の結果を保存する（Step 5）。"),
         "abx.blind を手放していない"),
        ("★★ 結果から時刻を落とす（AB-D5 の時刻仮説を検証できなくなる）",
         mut_html("    protocol: \"3phase-noreset-v2\", started_at: bl.startedAt,\n", ""),
         "protocol が入っていない"),
        ("★★★ S5C-D1: protocol を旧手順の値のままにする（測り直しと旧記録が JSON 上で区別できない）",
         mut_html('    protocol: "3phase-noreset-v2", started_at: bl.startedAt,',
                  '    protocol: "3phase-prep-v1", started_at: bl.startedAt,'),
         "protocol が新手順の値になっていない"),
        ("★★ 相の長さを live 参照に戻す（記録と提示が食い違う）",
         mut_html("  const ms = bl.sideSec * 1000;", "  const ms = abxSideSeconds() * 1000;"),
         "live 参照している"),
        # ---- ★★★ AB-D9（穴 6・2026-08-13 に研究者の run で露出）------------------
        ("★★★ AB-D9: レベルに出る写し方でも比が小さいまま走らせる（刺激そのものが小さい条件）",
         mut_html('  if (abxOpt().id === "abx_density" && levelBearing && Math.abs(db) < 0.5) {',
                  "  if (false) {"), "条件を断っていない"),
        ("★★★ AB-D9: 判定を density_norm_exp ではなく id で書く（config と実装がずれる）",
         mut_html("  const dnx = reworkOpt(\"dcue\").density_norm_exp;",
                  '  const dnx = reworkOpt("dcue").id === "c_texture" ? 0.5 : 0;'),
         "density_norm_exp（設計上の正規化指数）から出す"),
        ("★★★ AB-D9: contrast_measurable を結果から落とす（逆向きの誤読が起きる）",
         mut_html("    contrast_measurable: bl.contrastMeasurable,", ""),
         "contrast_measurable が残らない"),
        ("★★★ AB-D9: 対照条件（abx_level）を判定から落とす（Codex 指摘）",
         mut_html('  const contrastMeasurable = abxOpt().id === "abx_level" ? true : levelBearing;',
                  "  const contrastMeasurable = levelBearing;"),
         "対照条件（abx_level）を見ていない"),
        # ---- ★ AC-6 の完全化（★ 専用の変異が無かった 2 件・cross-review 指摘）--------
        ("★★ 中止の単一経路が abx.blind を手放さない",
         mut_html("  abx.blind = null;               // ★ 進行中の abxPhase はこれを見て false を返す",
                  "  // (removed)"), "abxBlindStop が abx.blind を手放していない"),
        ("★★ 残り秒を計算はするが画面に書かない（★ 単独では一度も発火実績が無かった）",
         mut_html('    $("abx-blind-state").textContent = `${head} — ${label}（あと ${(left / 1000).toFixed(1)} 秒）`;',
                  '    $("abx-blind-state").textContent = `${head} — ${label}`;'),
         "残り時間を画面に書いていない"),
        # ⚠️★ 「config から density_norm_exp を落とす」変異は **入れていない** ——
        #   ★ 既存の振幅比の検査（`ratio_overlap ** (0.5 - density_norm_exp)`）が
        #     **KeyError でクラッシュ**し、Fail ではなく例外になるため meta の型に乗らない。
        #   ★ 保護そのものは効いている（★ クラッシュも exit≠0 なので赤になる）。
        #   ⚠️ **「変異が無い＝検査されていない」ではないことを、ここに書いて残す。**
        ("★★ abxPhase が再生中かを見なくなる（停止しても相が進む）",
         mut_html("  const live = () => abx.blind === bl && playing;",
                  "  const live = () => abx.blind === bl;"),
         "再生中かを見ていない"),
    ]

    print("== meta 検査（★ 検査を壊して赤くなることの確認） ==")
    npass = nfail = 0
    want_len = len(base)
    for label, mutated, expect in cases:
        # ⚠️★★ 変異は生タプルでも書けるので、**要素数がずれたまま気づかない**ことがある
        #   （★ 2026-08-14 に走査対象を 1 つ足したとき、5 箇所で実際にずれた）。
        #   ★ TypeError で落ちると **どの変異が原因か分からない**ので、ここで名指しする。
        if len(mutated) != want_len:
            raise SystemExit(
                f"meta: 変異「{label}」の要素数が {len(mutated)}（★ {want_len} が正）。"
                "★ load_sources() に足したものを、この変異にも渡すこと")
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
