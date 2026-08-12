#!/usr/bin/env python3
"""層 0（基層）の静的検査 — Step 3。

★ このスクリプトが守るのは「音が良いか」ではない（それは耳が決める）。
   守るのは **仕様に接地した約束が実体とずれていないこと** である:

     1. `EXPR_VERSION` が 2 箇所（expr_smooth.py の定数 / layer0.config.json）で一致すること
     2. 基音が spec §2 の 55–110 Hz 帯から出ていないこと
     3. 倍音が整数次だけであること（非調和成分を持ち込む設定が無いこと）
     4. ★ ゆらぎの周波数が禁止帯（0.5–20 Hz / 15–70 Hz）に入っていないこと
     5. ★ ゆらぎの反復周期が試聴時間より十分長いこと（★ コメントを信じず計算する）
     6. ★ spec 準拠の候補が既定であること（逸脱側を既定にしていないこと）
     7. ★ [P71] 要件 1（止められる・音量を変えられる）が player に実在すること
     8. 検算の分解能が probe 線の間隔を分離できること
     9. player が窓なし DFT を持っていないこと（S0-D8）
    10. player に絶対パス / ユーザー名が混入していないこと

★ `--selftest` は上記の検査そのものを**壊した状態で走らせ、赤くなることを確かめる**
   （`verify-before-claiming` ルール 5b。このタスク系列で silent pass は 3 回出ている）。

依存は標準ライブラリのみ（S0-D8 の方針を踏襲）。
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
#     ★ 文字を避ける運用にはしない（メッセージが痩せる）。符号化できない字だけ逃がす。
#     引き継ぎ §5 落とし穴 11（PowerShell に日本語を入れない）と同じ罠の別経路である。
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(errors="backslashreplace")
    except (AttributeError, OSError):  # パイプ/リダイレクト先が reconfigure を持たない場合
        pass

# ---------------------------------------------------------------------------
# 一次資料の位置（相対で解決する。★ 絶対パスを書かない）
# ---------------------------------------------------------------------------
HERE = Path(__file__).resolve().parent
EXP_DIR = HERE.parent
REPO = EXP_DIR.parent.parent
CONFIG_PATH = EXP_DIR / "layer0.config.json"
PLAYER_PATH = EXP_DIR / "player" / "layer0.html"
EXPR_SMOOTH_PATH = (
    REPO / ".steering" / "20260811-expression-prototype-step0" / "scripts" / "expr_smooth.py"
)

# spec §2 / §1.1 の逐語から取った拘束（★ ここを緩める変更は spec の改訂を伴う）
BAND_HZ = (55.0, 110.0)
FORBIDDEN_MOD_BANDS = ((0.5, 20.0), (15.0, 70.0))
KNOWN_LAWS = {"1/n", "1/n^2"}
# S3-D3: 試聴時間 10 分。ゆらぎの反復周期はこれより十分長くなければならない
LISTEN_S = 600.0
REPEAT_MARGIN = 5.0


class Fail(Exception):
    """検査の失敗（1 行メッセージで報告し exit 2 にする）。"""


# ---------------------------------------------------------------------------
# 補助
# ---------------------------------------------------------------------------
def read_expr_version_from_py(text: str) -> str:
    """expr_smooth.py の EXPR_VERSION 定数を読む（import しない = 副作用を持ち込まない）。"""
    m = re.search(r'^EXPR_VERSION\s*=\s*"([^"]+)"', text, re.MULTILINE)
    if not m:
        raise Fail("expr_smooth.py から EXPR_VERSION 定数を読めない")
    return m.group(1)


def repeat_period_s(rates_hz: list[float]) -> float:
    """複数の正弦波の和が厳密に反復する周期 [s]。

    ★ 「通約できないから非周期」と書かないための計算。
    浮動小数の比は常に有理数なので、和は必ずどこかで反復する。
    各 rate を有理数にし、その **最大公約数（周波数）** の逆数が反復周期である。
    """
    if not rates_hz:
        return math.inf
    fr = [Fraction(r).limit_denominator(10**9) for r in rates_hz]
    g = fr[0]
    for f in fr[1:]:
        # Fraction の gcd: gcd(分子)/lcm(分母)
        g = Fraction(math.gcd(g.numerator, f.numerator),
                     (g.denominator * f.denominator) // math.gcd(g.denominator, f.denominator))
    if g == 0:
        return math.inf
    return float(1 / g)


def strip_js_comments(text: str) -> str:
    """JS/HTML からコメントを落とす（★ コードの検査がコメントの文言に引っかからないように）。

    ⚠️ **必要になった理由を残す**: 当初 `window=false` を素朴に grep していたところ、
    「window=false は用意しない」という **禁止を書いたコメント自身が FAIL を出した**（実測）。
    ★ ここで検査を緩めると「窓なし DFT を本当に持ち込んだ場合」も見逃す。**検査ではなく精度を直す。**

    文字列リテラル（' " `）の中の `//` はコメントにしない（`'ws://x'` を守るため）。
    ⚠️ 正規表現リテラル中の `//` は扱えない（本 player には存在しないことを確認済み）。
    """
    out, i, n = [], 0, len(text)
    quote = None
    while i < n:
        c = text[i]
        if quote:
            out.append(c)
            if c == "\\" and i + 1 < n:
                out.append(text[i + 1]); i += 2; continue
            if c == quote:
                quote = None
            i += 1
            continue
        if c in "'\"`":
            quote = c; out.append(c); i += 1; continue
        if c == "/" and i + 1 < n and text[i + 1] == "/":
            while i < n and text[i] != "\n":
                i += 1
            continue
        if c == "/" and i + 1 < n and text[i + 1] == "*":
            j = text.find("*/", i + 2)
            i = n if j < 0 else j + 2
            continue
        if c == "<" and text.startswith("<!--", i):
            j = text.find("-->", i)
            i = n if j < 0 else j + 3
            continue
        out.append(c); i += 1
    return "".join(out)


def claims_aperiodic(text: str) -> str | None:
    """『非周期』を **主張として** 書いていないか。

    ⚠️ 「『非周期』と書いてはならない」という **禁止の文言自体**は許す
    （素朴な部分一致だと、警告を書いた本人が赤くなる。実測でそうなった）。
    """
    for m in re.finditer(r"非周期", text):
        ctx = text[max(0, m.start() - 40): m.end() + 40]
        if re.search(r"書いてはならない|書かない|書いてはいけない|と書かない|ではない", ctx):
            continue
        return ctx.strip()
    return None


def in_forbidden(f: float) -> tuple[float, float] | None:
    for lo, hi in FORBIDDEN_MOD_BANDS:
        if lo <= f <= hi:
            return (lo, hi)
    return None


# ---------------------------------------------------------------------------
# 検査本体 — (名前, 実行関数) の列。各関数は失敗時に Fail を投げる
# ---------------------------------------------------------------------------
def build_checks(cfg: dict, cfg_text: str, html: str, py_ver: str):
    # ★ コードを見る検査はコメントを落としてから見る（禁止を書いたコメントで赤くならないように）
    code = strip_js_comments(html)
    checks: list[tuple[str, callable]] = []

    def add(name):
        def deco(fn):
            checks.append((name, fn))
            return fn
        return deco

    # --- 1. 版の一致 -------------------------------------------------------
    @add("EXPR_VERSION が expr_smooth.py と config で一致する")
    def _():
        c = cfg.get("expr_version")
        if c != py_ver:
            raise Fail(f"版がずれている: expr_smooth.py={py_ver!r} / config={c!r}")

    @add("EXPR_VERSION が Step 2 の版から上がっている（音を足したので）")
    def _():
        if cfg.get("expr_version") == "0.1.0-step2":
            raise Fail("音を足したのに EXPR_VERSION が 0.1.0-step2 のまま（引き継ぎ §4）")

    @add("HMM_VERSION が刻まれている")
    def _():
        if not cfg.get("hmm_version"):
            raise Fail("config に hmm_version が無い（reproducibility-discipline ルール 3）")

    # --- 2. 基音が spec §2 の帯から出ていない -----------------------------
    @add("基音がすべて 55–110 Hz 帯に入っている（spec §2）")
    def _():
        for o in cfg["candidates"]["base_hz"]["options"]:
            if not (BAND_HZ[0] <= o["hz"] <= BAND_HZ[1]):
                raise Fail(f"基音 {o['id']}={o['hz']} Hz が {BAND_HZ} の外")

    @add("基音の既定が実在する id を指している")
    def _():
        ids = {o["id"] for o in cfg["candidates"]["base_hz"]["options"]}
        if cfg["candidates"]["base_hz"]["default"] not in ids:
            raise Fail("base_hz.default が候補に無い id を指している")

    # --- 3. 倍音は整数次のみ ----------------------------------------------
    @add("倍音の減衰則が既知のものだけ（非調和成分を持ち込まない）")
    def _():
        for o in cfg["candidates"]["decay_law"]["options"]:
            if o["law"] not in KNOWN_LAWS:
                raise Fail(f"未知の減衰則 {o['law']!r}（spec §2 は整数次倍音のみ）")
            n = o["partials"]
            if not isinstance(n, int) or n < 1:
                raise Fail(f"partials が正の整数でない: {n!r}")

    @add("最高次倍音が Nyquist を大きく下回る（44.1 kHz 想定）")
    def _():
        fmax = max(o["hz"] for o in cfg["candidates"]["base_hz"]["options"])
        nmax = max(o["partials"] for o in cfg["candidates"]["decay_law"]["options"])
        top = fmax * nmax
        if top > 44100 / 2 * 0.5:
            raise Fail(f"最高次 {top:.0f} Hz が高すぎる（折り返しの危険）")

    # --- 4. ゆらぎが禁止帯に入っていない ----------------------------------
    @add("ゆらぎの周波数が禁止帯（0.5–20 / 15–70 Hz）に入っていない")
    def _():
        for o in cfg["candidates"]["drift"]["options"]:
            for r in o.get("rates_hz", []) or []:
                band = in_forbidden(r)
                if band is not None:
                    raise Fail(f"ゆらぎ {r} Hz が禁止帯 {band} に入っている（§1.1・[P69][P65]）")

    @add("ゆらぎが状態の波の帯域（0.001–0.02 Hz）に収まっている")
    def _():
        for o in cfg["candidates"]["drift"]["options"]:
            for r in o.get("rates_hz", []) or []:
                if not (0.001 <= r <= 0.02):
                    raise Fail(f"ゆらぎ {r} Hz が §1.1 の 0.001–0.02 Hz から外れている")

    # --- 5. 反復周期を「計算して」検査する（★ コメントを信じない） ---------
    @add("ゆらぎの反復周期が試聴 10 分の 5 倍以上（★ 計算で確かめる）")
    def _():
        for o in cfg["candidates"]["drift"]["options"]:
            rates = o.get("rates_hz", []) or []
            if not rates:
                continue
            T = repeat_period_s(rates)
            if T < LISTEN_S * REPEAT_MARGIN:
                raise Fail(
                    f"候補 {o['id']} の反復周期 {T:.0f} s が短い"
                    f"（試聴 {LISTEN_S:.0f} s の {REPEAT_MARGIN:.0f} 倍 = "
                    f"{LISTEN_S * REPEAT_MARGIN:.0f} s 以上が要る）"
                )

    @add("★ 『非周期』と主張していない（有理比なので必ず反復する）")
    def _():
        ctx = claims_aperiodic(cfg_text)
        if ctx:
            raise Fail(f"config が『非周期』と主張している。有理比の和は必ず反復する（S3-D10）: …{ctx}…")

    # --- 6. 逸脱側を既定にしていない --------------------------------------
    @add("★ spec §2 準拠の候補が既定である（逸脱側を既定にしない・S3-D10）")
    def _():
        opts = cfg["candidates"]["drift"]["options"]
        dflt = cfg["candidates"]["drift"]["default"]
        chosen = next((o for o in opts if o["id"] == dflt), None)
        if chosen is None:
            raise Fail("drift.default が候補に無い id を指している")
        if chosen.get("spec_compliant") is not True:
            raise Fail(f"既定 {dflt!r} が spec §2 非準拠。準拠側を既定にすること")

    @add("★ spec 非準拠の候補に spec_compliant=false が明示されている")
    def _():
        for o in cfg["candidates"]["drift"]["options"]:
            has_drift = bool(o.get("rates_hz")) and float(o.get("depth_db", 0)) > 0
            if has_drift and o.get("spec_compliant") is not False:
                raise Fail(
                    f"候補 {o['id']} はゆらぎを持つのに spec_compliant=false が無い"
                    "（spec §2『層 0 は動かさない』からの逸脱を隠さない）"
                )

    # --- 7. [P71] 要件 1 が player に実在する -----------------------------
    @add("★ [P71] 要件 1: 停止ボタンが player に実在する（交渉不可）")
    def _():
        if 'id="btn-stop"' not in html:
            raise Fail("player に停止ボタン (#btn-stop) が無い（spec §5 要件 1・交渉不可）")

    @add("★ [P71] 要件 1: 音量スライダが player に実在する（交渉不可）")
    def _():
        # ⚠️ 属性の引用符の有無に依存しない（当初 type=range 決め打ちで偽陽性が出た。実測）
        # ⚠️★★ id は **末尾まで**一致させる。当初 id=["\']?vol["\']? としていたため
        #      **`id="vol-gone"` が通り、スライダを消しても検査が緑のままだった**（meta 検査が実測で検出）。
        #      ★ これが「検査を書いたら壊した状態で試す」（ルール 5b）が拾った本物の silent pass である。
        if not re.search(
            r'<input[^>]*type=(["\'])range\1[^>]*id=(["\'])vol\2'
            r'|<input[^>]*type=range[^>\s]*[^>]*id=vol(?=[\s>])', html
        ):
            raise Fail("player に音量スライダ (#vol) が無い（spec §5 要件 1・交渉不可）")

    @add("★ 停止がランプ経由である（即時 stop() でクリックを作らない）")
    def _():
        m = re.search(r"async function stop\(\)\s*\{(.*?)\n\}", code, re.S)
        if not m:
            raise Fail("player に stop() が見つからない")
        body = m.group(1)
        if "exponentialRampToValueAtTime" not in body:
            raise Fail("stop() がランプを使っていない（急に切るとオンセットが出る・spec §2）")

    @add("★ 再生開始が resume() を無期限に待たない（無言で固まらない）")
    def _():
        # ⚠️ ブラウザ実地確認で判明（2026-08-12）: 素の `await ctx.resume()` は
        #    ユーザ操作を伴わないと Promise が解決せず、play() がそこで止まる。
        #    ボタンは押せるまま・エラーも出ない＝「押しても何も起きない」に見える。
        m = re.search(r"async function play\(\)\s*\{(.*?)\n\}", code, re.S)
        if not m:
            raise Fail("player に play() が見つからない")
        body = m.group(1)
        if re.search(r"await\s+ctx\.resume\(\)\s*;", body):
            raise Fail("play() が ctx.resume() を無期限に待っている（自動再生ブロック時に無言で固まる）")
        if 'ctx.state !== "running"' not in body:
            raise Fail("play() が resume 後の状態を確かめていない")

    @add("★ player が alert()/confirm()/prompt() を使っていない（モーダルはページを止める）")
    def _():
        for kw in ("alert(", "confirm(", "prompt("):
            if re.search(r"(?<![\w.])" + re.escape(kw), code):
                raise Fail(f"player が {kw[:-1]}() を使っている。ページ内表示にすること")

    @add("★ 立ち上げがフェードインである（アタックを作らない）")
    def _():
        m = re.search(r"async function play\(\)\s*\{(.*?)\n\}", code, re.S)
        if not m:
            raise Fail("player に play() が見つからない")
        if "fade_in_s" not in m.group(1):
            raise Fail("play() がフェードインしていない（spec §2 ✗オンセット）")

    # --- 8. 検算の分解能 ---------------------------------------------------
    @add("検算の分解能が probe 線の間隔を分離できる")
    def _():
        st = cfg["selftest"]
        lines = sorted(st["probe_lines_hz"])
        if len(lines) < 2:
            raise Fail("probe_lines_hz が 2 本未満")
        gap = min(b - a for a, b in zip(lines, lines[1:]))
        res = 1.0 / st["render_seconds"]
        if res > gap:
            raise Fail(
                f"分解能 {res:.5f} Hz が probe 間隔 {gap:.5f} Hz より粗い"
                f"（render_seconds >= {1.0 / gap:.0f} が要る）"
            )

    @add("検算の判定閾値が S0-D7 の基準（-60 dB）より緩くない")
    def _():
        thr = cfg["selftest"]["pass_threshold_db"]
        if thr > -60.0:
            raise Fail(f"判定閾値 {thr} dB が S0-D7 の -60 dB より緩い（後付けで緩めない）")

    @add("probe 線が 4 Hz 近傍を含む（最悪の帯域を測っている）")
    def _():
        if not any(abs(f - 4.0) < 0.5 for f in cfg["selftest"]["probe_lines_hz"]):
            raise Fail("probe_lines_hz に 4 Hz 近傍が無い（§1.1 で最悪の帯域）")

    # --- 9. 窓なし DFT を持っていない（S0-D8） ----------------------------
    @add("★ player が窓なし DFT を持っていない（S0-D8: 符号が逆になる）")
    def _():
        if re.search(r"window\s*[:=]\s*false", code) or "noWindow" in code:
            raise Fail("player に窓なし DFT の経路がある（S0-D8 が禁じている）")
        if "hannAmplitude" not in code:
            raise Fail("player に Hann 窓付き DFT (hannAmplitude) が無い")

    @add("★ player が逆検査（4 Hz 注入）を持っている（ルール 5b）")
    def _():
        if "sabotage" not in code:
            raise Fail("player に逆検査モードが無い（検査が空回りしていないかを確かめられない）")

    # --- 10. 混入検査 ------------------------------------------------------
    @add("player / config に絶対パス・ユーザー名が混入していない")
    def _():
        for name, text in (("player", html), ("config", cfg_text)):
            if re.search(r"[A-Za-z]:[\\/]Users[\\/]", text):
                raise Fail(f"{name} に Windows の絶対パスが混入している")
            if re.search(r"/(?:home|Users)/[A-Za-z0-9._-]+/", text):
                raise Fail(f"{name} に POSIX の絶対パスが混入している")

    @add("★ player が実データを外部へ送る経路を持っていない（data-privacy / D5）")
    def _():
        # fetch は設定ファイル（相対パス）以外に使わない
        for m in re.finditer(r"fetch\(\s*([\"'])(.*?)\1", code):
            url = m.group(2)
            if not url.startswith("../") and not url.startswith("./"):
                raise Fail(f"player が相対パス以外を fetch している: {url!r}")
        for kw in ("XMLHttpRequest", "WebSocket", "sendBeacon", "EventSource"):
            if kw in code:
                raise Fail(f"player に外部送信の手段がある: {kw}（D5・外部送信境界を増やさない）")

    # --- Step 3b の範囲 ----------------------------------------------------
    @add("Step 3b が既定で無効（層 0 は状態に応答させない）")
    def _():
        if cfg["step3b"].get("enabled_by_default") is not False:
            raise Fail("step3b が既定で有効になっている（spec §7 Step 3『状態に応答させない』）")

    @add("Step 3b の深さが『聴こえない程度』に収まっている（<= 1.0 dB）")
    def _():
        d = float(cfg["step3b"]["depth_db"])
        if not (0.0 < d <= 1.0):
            raise Fail(f"step3b.depth_db={d} dB が範囲外（引き継ぎ §3b『聴こえない程度に』）")

    @add("Step 3b が音色・音高でなくゲインに乗る（player 実装の確認）")
    def _():
        if "graph.expr.gain" not in code:
            raise Fail("player が Step 3b をゲイン以外に当てている可能性がある")
        if re.search(r"function scheduleAhead[\s\S]{0,2500}?osc\w*\.frequency", code):
            raise Fail("Step 3b の経路が音高を動かしている（spec §2 ✗音高のステップ）")

    @add("離席復帰の 2 案が両方そろっている（S3-D6 は耳で決める）")
    def _():
        ids = {o["id"] for o in cfg["step3b"]["gap_behavior"]["options"]}
        if {"carry", "restart"} - ids:
            raise Fail(f"離席復帰の候補が足りない: {sorted(ids)}（carry / restart の両方が要る）")
        if cfg["step3b"]["gap_behavior"]["default"] != "carry":
            raise Fail("既定が carry でない（S0-D11 の現行実装を勝手に反転させない）")

    return checks


# ---------------------------------------------------------------------------
# 実行
# ---------------------------------------------------------------------------
def load_sources() -> tuple[dict, str, str, str]:
    for p in (CONFIG_PATH, PLAYER_PATH, EXPR_SMOOTH_PATH):
        if not p.exists():
            raise Fail(f"必要なファイルが無い: {p}")
    cfg_text = CONFIG_PATH.read_text(encoding="utf-8")
    try:
        cfg = json.loads(cfg_text)
    except json.JSONDecodeError as e:
        raise Fail(f"layer0.config.json を解釈できない: {e}") from e
    html = PLAYER_PATH.read_text(encoding="utf-8")
    py_ver = read_expr_version_from_py(EXPR_SMOOTH_PATH.read_text(encoding="utf-8"))
    return cfg, cfg_text, html, py_ver


def run_checks(cfg, cfg_text, html, py_ver, verbose=True) -> tuple[int, int]:
    checks = build_checks(cfg, cfg_text, html, py_ver)
    npass = nfail = 0
    for name, fn in checks:
        try:
            fn()
        except Fail as e:
            nfail += 1
            if verbose:
                print(f"  FAIL  {name}\n        -> {e}")
        else:
            npass += 1
            if verbose:
                print(f"  ok    {name}")
    return npass, nfail


def first_failure(cfg, cfg_text, html, py_ver) -> str | None:
    """壊した状態で最初に落ちた検査を「名前 :: 失敗メッセージ」で返す（meta 検査用）。

    ⚠️ **名前だけを返してはならない**——1 つの検査が複数の理由で落ちうるので、
    「期待した理由で落ちたか」を確かめられなくなる（S0-D14 が踏んだ形の再来）。
    """
    for name, fn in build_checks(cfg, cfg_text, html, py_ver):
        try:
            fn()
        except Fail as e:
            return f"{name} :: {e}"
    return None


# ---------------------------------------------------------------------------
# ★ meta 検査（ルール 5b）— 検査を壊した状態で走らせ、赤くなることを確かめる
# ---------------------------------------------------------------------------
def meta_checks() -> int:
    """壊し方 → 赤くなるべき検査名（部分一致）。"""
    cfg0, cfg_text0, html0, py_ver0 = load_sources()

    def mut_cfg(fn):
        c = copy.deepcopy(cfg0)
        fn(c)
        return c, json.dumps(c, ensure_ascii=False), html0, py_ver0

    def drift_slow(c):
        return next(o for o in c["candidates"]["drift"]["options"] if o.get("rates_hz"))

    cases: list[tuple[str, tuple, str]] = [
        ("版を config 側だけずらす",
         mut_cfg(lambda c: c.update(expr_version="9.9.9-bogus")), "EXPR_VERSION が expr_smooth.py"),
        ("版を Step 2 のまま据え置く",
         (lambda: (lambda c: (c, json.dumps(c, ensure_ascii=False), html0, "0.1.0-step2"))(
             {**copy.deepcopy(cfg0), "expr_version": "0.1.0-step2"}))(),
         "Step 2 の版から上がっている"),
        ("基音を帯の外（130 Hz）にする",
         mut_cfg(lambda c: c["candidates"]["base_hz"]["options"][0].update(hz=130.0)),
         "55–110 Hz 帯"),
        ("ゆらぎを 4 Hz（最悪の帯域）にする",
         mut_cfg(lambda c: drift_slow(c).update(rates_hz=[4.0, 4.1])), "禁止帯"),
        ("ゆらぎを単一正弦にして反復周期を縮める",
         mut_cfg(lambda c: drift_slow(c).update(rates_hz=[0.005])), "反復周期"),
        ("逸脱側（ゆらぎ有）を既定にする",
         mut_cfg(lambda c: c["candidates"]["drift"].update(default="slow")), "既定である"),
        ("逸脱の印（spec_compliant=false）を消す",
         mut_cfg(lambda c: drift_slow(c).update(spec_compliant=True)), "spec_compliant=false"),
        ("非調和な減衰則を足す",
         mut_cfg(lambda c: c["candidates"]["decay_law"]["options"].append(
             {"id": "x", "law": "1/n^1.5", "partials": 8, "label": "x"})), "既知のもの"),
        ("判定閾値を -40 dB へ緩める",
         mut_cfg(lambda c: c["selftest"].update(pass_threshold_db=-40.0)), "S0-D7 の基準"),
        ("レンダ時間を 100 s に縮めて分解能を粗くする",
         mut_cfg(lambda c: c["selftest"].update(render_seconds=100)), "分解能"),
        ("Step 3b を既定で有効にする",
         mut_cfg(lambda c: c["step3b"].update(enabled_by_default=True)), "既定で無効"),
        ("Step 3b の深さを 6 dB にする",
         mut_cfg(lambda c: c["step3b"].update(depth_db=6.0)), "聴こえない程度"),
        ("離席復帰の既定を restart に反転させる",
         mut_cfg(lambda c: c["step3b"]["gap_behavior"].update(default="restart")), "離席復帰の 2 案"),
        ("config に『非周期』と書く",
         (cfg0, cfg_text0 + "\n非周期\n", html0, py_ver0), "非周期"),
        ("player から停止ボタンを消す",
         (cfg0, cfg_text0, html0.replace('id="btn-stop"', 'id="btn-gone"'), py_ver0),
         "停止ボタン"),
        ("player から音量スライダを消す",
         (cfg0, cfg_text0, html0.replace('id="vol"', 'id="vol-gone"'), py_ver0),
         "音量スライダ"),
        ("player の stop() からランプを消す",
         (cfg0, cfg_text0,
          re.sub(r"(async function stop\(\)\s*\{)", r"\1\n  // ramp removed",
                 html0.replace("graph.master.gain.exponentialRampToValueAtTime(0.0001, now + f);",
                               "graph.srcs.forEach((s) => s.stop());")), py_ver0),
         "ランプ"),
        ("play() を素の await ctx.resume() に戻す",
         (cfg0, cfg_text0,
          html0.replace("await Promise.race([ctx.resume(), new Promise((r) => setTimeout(r, 1200))]);",
                        "await ctx.resume();"), py_ver0),
         "無期限に待っている"),
        ("player に alert() を持ち込む",
         (cfg0, cfg_text0,
          html0 + "\n<script>function f(){ alert('x'); }</script>", py_ver0),
         "alert() を使っている"),
        ("player から Hann 窓付き DFT を消す",
         (cfg0, cfg_text0, html0.replace("hannAmplitude", "dftMagnitude"), py_ver0),
         "Hann 窓付き DFT (hannAmplitude) が無い"),
        ("player に窓なし DFT の経路を持ち込む",
         (cfg0, cfg_text0, html0 + "\n<script>const o = { window: false };</script>", py_ver0),
         "窓なし DFT の経路がある"),
        ("player から逆検査を消す",
         (cfg0, cfg_text0, html0.replace("sabotage", "sab0tage"), py_ver0), "逆検査"),
        ("player に WebSocket を持ち込む",
         (cfg0, cfg_text0, html0 + "\n<script>new WebSocket('ws://x');</script>", py_ver0),
         "外部送信の手段"),
        ("player に絶対パスを混入させる",
         (cfg0, cfg_text0, html0 + "\n<!-- C:/Users/someone/x -->", py_ver0), "絶対パス"),
    ]

    print("★ meta 検査 — 検査を壊した状態で走らせ、赤くなることを確かめる（ルール 5b）")
    npass = nfail = 0
    for label, args, expect in cases:
        got = first_failure(*args)
        if got is None:
            nfail += 1
            print(f"  FAIL  {label}\n        -> 壊したのに全検査が PASS した（★ 検査が空回りしている）")
        elif expect not in got:
            nfail += 1
            print(f"  FAIL  {label}\n        -> 落ちた検査が違う: 期待 {expect!r} / 実際 {got!r}")
        else:
            npass += 1
            print(f"  ok    {label}  -> 「{got}」が赤くなった")

    # ★ meta 検査そのものが空回りしていないか: 壊していない状態では 1 件も落ちないこと
    got = first_failure(cfg0, cfg_text0, html0, py_ver0)
    if got is None:
        npass += 1
        print("  ok    壊していない状態では 1 件も落ちない（偽陽性が無い）")
    else:
        nfail += 1
        print(f"  FAIL  壊していない状態で「{got}」が落ちた（偽陽性）")

    print(f"\nmeta: {npass} ok / {nfail} fail")
    return 0 if nfail == 0 else 2


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--selftest", action="store_true",
                    help="★ 検査自体を壊した状態で走らせ、赤くなることを確かめる（ルール 5b）")
    args = ap.parse_args()

    try:
        cfg, cfg_text, html, py_ver = load_sources()
    except Fail as e:
        print(f"error: {e}", file=sys.stderr)
        return 2

    print(f"layer0 静的検査 — EXPR_VERSION(py)={py_ver} / config={cfg.get('expr_version')}")
    npass, nfail = run_checks(cfg, cfg_text, html, py_ver)
    print(f"\n{npass} ok / {nfail} fail")

    rc = 0 if nfail == 0 else 2
    if args.selftest:
        print()
        rc = meta_checks() or rc
    return rc


if __name__ == "__main__":
    sys.exit(main())
