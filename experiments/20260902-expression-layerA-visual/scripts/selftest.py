#!/usr/bin/env python3
"""selftest.py — layerA.config.json と player/layerA.html の整合を機械検査する。

⚠️★★★ この検査は「危険でないと言えない」ことしか示さない。
   ★ 表現が読めるかどうかは、試視でしか分からない。

⚠️ `verify-before-claiming` ルール 5b: 検査自体を 3 状態（正常 / 不在 / 壊れ）で試すこと。
   → 本スクリプトは `--selfcheck` で「壊れた config を作って赤になるか」を実測する。
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

FAILS: list[str] = []
OKS: list[str] = []

# ⚠️★★★ Windows の既定 stdout は cp932 で、`–`（U+2013）等が UnicodeEncodeError で落ちる。
#    ★ 2026-09-02 に実測して踏んだ。★ 検査が「赤」ではなく「例外」で死ぬのが最悪なので、先に潰す。
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass


def check(name: str, ok: bool, detail: str = "") -> None:
    (OKS if ok else FAILS).append(f"{name} :: {detail}")
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f"  ({detail})" if detail else ""))


def run(cfg_path: Path, html_path: Path) -> None:
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    html = html_path.read_text(encoding="utf-8")

    # --- 1. invitation の符号が [P85] の帯域内か ---------------------------
    f = cfg["invitation"]["frequency_hz"]
    check("invitation の周波数が 1–3 Hz 帯（[P85] G4）", 1.0 <= f <= 3.0, f"{f} Hz")

    amp = cfg["invitation"]["amplitude_deg_peak_to_peak"]
    check("invitation の振幅が ~1°（[P85] G3）", 0.5 <= amp <= 2.0, f"{amp} deg")

    check("anchored（travelling を使わないと宣言している・[P85] G7）",
          cfg["invitation"].get("anchored") is True, str(cfg["invitation"].get("anchored")))

    # ★ 曖昧さを黙って解消していないこと（★ 記録が残っているか）
    check("⚠️ 振幅の片/全の曖昧さを config に記録している",
          "peak-to-peak" in cfg["invitation"].get("amplitude_convention_note", ""),
          "amplitude_convention_note")

    # --- 2. 段数が A-5 の安全域内か ---------------------------------------
    levels = [k for k in cfg["levels"]]
    check("1 目盛りの段数が安全域 5 以内（A-5・[P252]）", len(levels) <= 5, f"{len(levels)} 段: {levels}")

    # --- 3. A-1: 提示が 2 秒以内 ------------------------------------------
    ms = cfg["stimulus"]["stimulus_ms"]
    check("提示が設計上限 2 秒以内（A-1・[P253]）", ms <= 2000, f"{ms} ms")

    check("マスクを置いている（★ 残像による事後読解を潰す）",
          cfg["stimulus"]["mask_ms"] > 0, f"{cfg['stimulus']['mask_ms']} ms")

    # --- 4. ⚠️★★★ 層 0 が空白でない（C4 / §3.5.3） -----------------------
    l0 = cfg["levels"]["layer0"]
    check("⚠️★★★ 層 0 に図が無い（＝系が何も言っていない）", l0["has_figure"] is False, str(l0))
    check("⚠️★★★ 層 0 を空白で表さない（地は在る・C4）",
          cfg["field"]["ground_marks"] > 0, f"ground_marks={cfg['field']['ground_marks']}")

    # --- 5. stuck が「疎」であって「荒れ」でないこと（[P101]） --------------
    occ = {k: v.get("occupancy", 0.0) for k, v in cfg["levels"].items()}
    check("stuck が最も疎（★ 罰ではなく疎として描く・[P101]）",
          occ["stuck"] < occ["stable"] and occ["stuck"] < occ["friction_rising"], str(occ))

    # ★ friction_rising は占有ではなく散らばりで stable と分かれる（★ 2 次元を混ぜない）
    sc = {k: v.get("scatter_px", 0.0) for k, v in cfg["levels"].items()}
    check("friction_rising は占有ではなく散らばりで stable と分かれる",
          occ["friction_rising"] == occ["stable"] and sc["friction_rising"] > sc["stable"], str(sc))

    # --- 6. ⚠️★★★ A-6: 色を主符号にしていない --------------------------
    check("既定テーマが mono（★ A-6・⚠️ かつ iOS はロック画面を強制 monochrome にする）",
          cfg["render"]["default_theme"] == "mono", cfg["render"]["default_theme"])

    # ★ 全テーマの ink/bg 輝度差が揃っているか（★ 配色がデータを担っていないことの必要条件）
    def lum(hexs: str) -> float:
        r, g, b = (int(hexs[i:i + 2], 16) for i in (1, 3, 5))
        return 0.2126 * r + 0.7152 * g + 0.0722 * b

    # ⚠️★★★ 2026-09-02: **この検査は最初 存在しなかった。**
    #    ★ Python 側は輝度差しか見ておらず、mono の bg が `#101215`（R≠G≠B ＝ 青みがかった灰）
    #      であることを **緑のまま見逃した**。★ ブラウザで画素を実測して初めて出た。
    #    → ★ 実物で見つかった欠陥に対して、機械側にも同じ検査を置く
    #      （`verify-before-claiming` ルール 6「主張を書いたら検査を一緒に置く」）。
    def is_gray(hexs: str) -> bool:
        r, g, b = (int(hexs[i:i + 2], 16) for i in (1, 3, 5))
        return r == g == b

    mono = cfg["render"]["themes"]["mono"]
    check("⚠️★★★ mono テーマが真のグレースケール（R=G=B）",
          is_gray(mono["ink"]) and is_gray(mono["bg"]), f"ink={mono['ink']} bg={mono['bg']}")

    contrasts = {k: abs(lum(v["ink"]) - lum(v["bg"])) for k, v in cfg["render"]["themes"].items()}
    spread = max(contrasts.values()) - min(contrasts.values())
    check("配色テーマの輝度差が揃っている（★ 色がデータを担わない必要条件）",
          spread < 12.0, f"輝度差 {({k: round(v, 1) for k, v in contrasts.items()})} / 幅 {spread:.1f}")

    # --- 7. blind 構成が均衡しているか -----------------------------------
    comp = cfg["blind_test"]["composition"]
    check("盲検の内訳が 4 状態で均衡", len(set(comp.values())) == 1, str(comp))
    check("チャンス水準が 4 択と整合", abs(cfg["blind_test"]["chance_level_4way"] - 0.25) < 1e-9,
          str(cfg["blind_test"]["chance_level_4way"]))
    check("⚠️ 途中で正誤を出さない", cfg["blind_test"]["feedback_during"] is False, "")

    # --- 8. catch trial があるか（§7-4） ----------------------------------
    t = cfg["transition_test"]
    check("遷移ブロックに catch がある（§7-4）", t["catch_trials"] > 0, f"{t['catch_trials']} / {t['trials']}")
    check("catch が全体の 1/4 以上ある", t["catch_trials"] / t["trials"] >= 0.25,
          f"{t['catch_trials']}/{t['trials']}")

    # --- 8a2. ⚠️★★★ 遷移対（★ 2026-09-08: config へ移した）----------------------
    #   ⚠️ 旧構成は trials 16 / catch 6 ＝ 変化 10 を 6 対に配り、
    #     **`layer0 ↔ stable`（E-7 に直接効く対）だけが n=1** だった（★ 実測）。
    pairs = t.get("change_pairs")
    check("★ 遷移対の一覧が config にある（★ SSOT・機械で検算するため）",
          isinstance(pairs, list) and len(pairs) >= 2 and all(len(x) == 2 for x in pairs),
          f"{len(pairs) if isinstance(pairs, list) else '—'} 対")
    if isinstance(pairs, list) and pairs:
        n_change = t["trials"] - t["catch_trials"]
        check("⚠️★★★ 変化試行が遷移対で割り切れる（★ E-7 の対が単発にならない）",
              n_change % len(pairs) == 0 and n_change // len(pairs) >= 2,
              f"変化 {n_change} / {len(pairs)} 対 = 1 対あたり {n_change / len(pairs):.2f}")
        flat = {lv for pr in pairs for lv in pr}
        unknown = flat - set(cfg["levels"])
        check("★ 遷移対が levels に存在する状態だけを使っている", not unknown, f"未知: {unknown}" if unknown else "OK")
        check("★ 遷移対に E-7 の対（層 0 ↔ stable）が入っている",
              ["layer0", "stable"] in [list(x) for x in pairs]
              and ["stable", "layer0"] in [list(x) for x in pairs], "")

    # --- 8b. ★ 周辺視ブロック（A-4）------------------------------------------
    #   ⚠️★★★ 2026-09-08 追加。★ 本ブロックは 2026-09-02 版では **未実装（config に枠だけ）** だった。
    pt = cfg["peripheral_test"]
    need_keys = ["order_seed", "trials", "control_center_trials", "eccentricity_deg",
                 "positions", "stimulus_ms", "variant"]
    missing = [k for k in need_keys if k not in pt]
    check("★ 周辺視ブロックの設定が揃っている", not missing,
          f"不足: {missing}" if missing else ", ".join(need_keys))

    # ★ [P85] の運動優位は偏心 7°–52° の結果。★ 帯の内側に取る（⚠️ 再現が目的ではないが、外へ出ない）
    check("★ 偏心が [P85] の実測帯（7°–52°）の内側",
          7.0 <= pt["eccentricity_deg"] <= 52.0, f"{pt['eccentricity_deg']} deg")

    # ⚠️★★★ 中心対照が無いと「偏心のせい」と「短い提示のせい」を分けられない
    check("⚠️★★★ 周辺視に中心対照がある（★ 偏心と提示時間の交絡を分ける）",
          pt.get("control_center_trials", 0) > 0, f"中心対照 {pt.get('control_center_trials')} 件")

    nlev = len(cfg["levels"])
    check("★ 周辺視の内訳が 4 状態で割り切れる",
          pt["trials"] % nlev == 0 and pt["control_center_trials"] % nlev == 0,
          f"偏心 {pt['trials']} / 中心 {pt['control_center_trials']} / 状態 {nlev}")

    # ⚠️★★★ 両腕の n が違うと、真に差があっても Wilson CI が原理的にほぼ重なる
    #    （★ 実測: 4/16 → [10.2%, 49.5%] vs 6/8 → [40.9%, 92.9%]）。
    check("⚠️★★★ 周辺視の 2 腕（偏心 / 中心対照）の n が揃っている",
          pt.get("control_center_trials") == pt.get("trials"),
          f"偏心 {pt.get('trials')} / 中心 {pt.get('control_center_trials')}")

    check("★ 周辺視の提示が中心視ブロックより短い（★ 視線が届く前に打ち切る設計）",
          pt["stimulus_ms"] < cfg["stimulus"]["stimulus_ms"],
          f"{pt['stimulus_ms']} ms < {cfg['stimulus']['stimulus_ms']} ms")

    # ⚠️★★★ 一次の裏づけが無いことを config 自身が言っているか（★ 黙って数値を置かない）
    check("⚠️★★★ 周辺視の提示時間に『一次の裏づけは無い』と明記している",
          "一次の裏づけは無い" in pt.get("stimulus_ms_note", "")
          and "固視は検証していない" in pt.get("stimulus_ms_note", ""), "stimulus_ms_note")

    check("★ 周辺視の位置が複数あり左右にランダム化される（⚠️ 先読み固視を防ぐ）",
          isinstance(pt.get("positions"), list) and len(pt["positions"]) >= 2, str(pt.get("positions")))

    check("★ 周辺視は variant = natural 固定（★ 極性は 1b / 1b' が測る）",
          pt.get("variant") == "natural", str(pt.get("variant")))

    # --- 9. ⚠️ HTML 側との整合 -------------------------------------------
    check("HTML が config を fetch している（★ 既定値で黙って走らない）",
          'fetch("../layerA.config.json"' in html, "")
    check("⚠️ fetch 失敗時に停止する（★ フォールバックで別条件を走らせない）",
          "既定値では走りません" in html, "")
    # ⚠️ 2026-09-03: 旧実装は `html.replace("CAL.pxPerDeg", "CAL.pxPerDeg")` という
    #   自分自身への no-op 置換で、何も意味していなかった（★ `code-reviewer` MEDIUM 指摘）。
    check("HTML が較正ゲートを持つ（★ 視角 1° は較正なしに意味を持たない）",
          "btn-cal-apply" in html and "CAL.pxPerDeg" in html, "")

    # ★ 写像の人間可読な説明が別ファイルへ分離されているか（★ `code-reviewer` HIGH 指摘）
    notes = cfg_path.parent / "layerA.mapping-notes.json"
    check("★ 写像の人間可読な説明が別ファイルへ分離されている",
          notes.exists() and "note" not in cfg["levels"]["stable"], str(notes.name))
    check("★ 説明を unseal() で初めて fetch する（★ 起動時に読まない）",
          'fetch("../layerA.mapping-notes.json"' in html
          and html.index("async function unseal") < html.index('fetch("../layerA.mapping-notes.json"'), "")
    check("⚠️★★★ 「技術的な封印ではない」と明記している（★ 誤解を防ぐ）",
          "技術的な封印ではない" in html, "")

    # ★ 出題順が level × variant で均衡しているか（★ HIGH 指摘の再発防止）
    #   ⚠️ JS の実装を Python から直接は回せないので、**均衡を保証する実装であること**を検査する。
    check("⚠️★★★ 出題順が level ごとに variant を層別割当している",
          "vShuffled" in html and "この level の中で variant を均等に作る" in html, "")
    check("★ ページ内検査が level × variant の均衡を検算している",
          "level × variant が均衡している" in html, "")
    # ⚠️★★★ 2026-09-08: 旧検査「drawField が mix を乗算している」は **撤去した**。
    #   ★ 理由: `mix` による重ね塗り自体をやめた（→ 不透明オフスクリーンの合成）。
    #   ★ 後継は下の「遷移が不透明オフスクリーンの合成である」＋ページ内の catch 不変性検査。
    #   ⚠️ **検査を消すときは、後継を明記する**（★ 黙って減らさない）。
    check("★ drawField が合成係数を持たない（★ 重ね塗りをやめた後継実装である）",
          "0.45 * mix" not in html and "function drawField(ctx, field, tSec, invitation, W, H) {" in html, "")
    # ★ 中止後の再開で結果配列がクリアされるか
    #   ⚠️★★★ 2026-09-08: **4 ブロックすべてが同じ関数を通ること**を見る
    #     （★ 旧実装は 1b だけで、1a / 2 は「中止が無いから露出していなかった」だけだった）。
    check("★ 中止後の再開で前回の途中結果を破棄する（★ 全ブロック）",
          "function discardNotice" in html and "arr.length = 0;" in html
          and html.count("discardNotice(") >= 5, f"discardNotice 参照 {html.count('discardNotice(')} 箇所")

    # ⚠️★★★ 中止ボタンが試行中に押せる位置にあるか（★ 2026-09-08・ブラウザ実測に基づく）
    #   ★ 旧実装の `btn-bt-abort` は §3 の通常フローにあり、オーバーレイの下 ＋ ビューポート外で
    #     **到達不能**だった。★ かつ 1a / 2 には中止そのものが無かった。
    #   ⚠️ 語としての `btn-bt-abort` は**由来の説明として残す**（★ 消すと「なぜ移したか」が消える）。
    #      → ★ 検査するのは **要素と参照が無いこと**である（★ コメントは対象外）。
    dead_abort = ['id="btn-bt-abort"', '$("btn-bt-abort")']
    alive = [t for t in dead_abort if t in html]
    check("⚠️★★★ 中止ボタンがオーバーレイの中にある（★ 旧 btn-bt-abort の要素・参照が無い）",
          not alive and 'ab.id = "ovl-abort"' in html and ".ovl-abort" in html,
          f"残存: {alive}" if alive else "ovl-abort")
    missing_abort = [n for n in ("frAbort", "btAbort", "trAbort", "perAbort")
                     if f", {n})" not in html]
    check("⚠️★★★ 4 ブロックすべてが overlayOn に中止関数を渡している（★ 1a / 2 の非対称を解消）",
          not missing_abort, f"未接続: {missing_abort}" if missing_abort else "1a / 1b / 2 / 3")
    # ⚠️★★★ オーバーレイの所有者を追跡しているか（★ `security-checker` M-2）
    #    ★ 無いと ① `blockRunning()` が 1a を見落とし、② `overlayOff` が他ブロックの
    #      中止ボタンを id で消す。→ ★ **足したばかりの「1a に中止がある」が静かに壊れる。**
    check("⚠️★★★ オーバーレイの所有者を追跡し、他ブロックの片付けを拒む",
          "let activeOverlay = null;" in html
          and "if (activeOverlay !== null && activeOverlay !== boxId) return;" in html, "")
    check("⚠️★★★ blockRunning がブロック 1a（＝ オーバーレイ）も数える",
          "function blockRunning() { return !!(bt || tr || per || activeOverlay); }" in html, "")
    check("★ ページ内検査が『他ブロックのオーバーレイを壊さない』を対照つきで見ている",
          "overlayOff が他ブロックのオーバーレイを壊さない" in html, "")

    check("★ ページ内検査が中止ボタンの hit-test を対照つきで見ている",
          "hit-test できる" in html and "elementFromPoint" in html, "")

    # ★ 破棄・中止の告知の宛先（★ 1b' が 1b の欄に出ない・F7 / 判断 4）
    check("⚠️★★★ 中止の告知が 1b / 1b' で別の欄に出る（★ 宛先をハードコードしない）",
          "function logAbort(msg, taught)" in html
          and '$(taught ? "bt2-state" : "bt-state")' in html, "")

    # ★ 周辺視ブロックの実装（★ 固視点 / 左右ランダム化 / 実施可否ゲート）
    check("★ 同じ id が重複していない（★ stagewrap は class へ）",
          'id="stagewrap"' not in html and html.count('class="stagewrap"') == 3, "")

    check("★ 周辺視ブロックが実装されている（固視点・偏心・実施可否ゲート）",
          'id="per-fix"' in html and "function perGeometry" in html
          and "function buildPerOrder" in html and 'id="stage-per"' in html, "")
    check("⚠️★★★ 偏心が画面に入らないときブロックを開かない（★ 黙って縮めない）",
          "偏心を黙って縮めて走らせません" in html and "btn-per-start" in html, "")
    # ⚠️★★★ 刺激を描く前に可視にすると、**空の矩形が 1 フレーム先に出て空間的な先行手掛かりになる**
    #    （★ 2026-09-08 にブラウザで位相機械を回して気づいた。★ それまで機械検査は緑だった）。
    mm = re.search(r'per\.phase = "stim"; per\.t0 = performance\.now\(\);'
                   r'(.*?)\$\("per-stage"\)\.style\.visibility = "visible";', html, re.S)
    check("⚠️★★★ 周辺視は【描いてから】可視にする（★ 空の矩形が先行手掛かりにならない）",
          bool(mm) and "drawField(" in mm.group(1),
          "ITI→刺激の遷移で drawField が visibility より前にある" if mm else "⚠️ 遷移が見つからない")

    check("★ 周辺視の出題順が seed でシャッフルされる（⚠️ 先読み固視を防ぐ）",
          "for (const c of shuffle(cells, rng))" in html
          and "for (const iv of shuffle(cells, rng))" in html, "")
    check("★ ページ内検査が周辺視の件数と variant 固定を検算している",
          "level × 条件（偏心 / 中心対照）の件数が config どおり" in html
          and "variant が natural 固定" in html, "")

    # ⚠️★★★ 2026-09-08（★ `code-reviewer` HIGH 指摘）——
    #   ★ 件数の検査は **構成上どの seed でも緑**（＝ 空回り）だった。
    #   → ★ 危険なのは *交差* であり、しかも **本番 seed 1 本では偶然の均衡と区別できない**。
    check("⚠️★★★ ページ内検査が交差の偏りを **複数 seed** で検算している",
          "50 seed で検算" in html and "const crossDev = " in html
          and "左右 × invitation" in html and "variant × invitation" in html, "")
    check("⚠️★★★ invitation を variant の中で層別に振っている（★ 位置で決めない）",
          "const flip = ((lvIdx + vids.indexOf(v)) % 2) === 0;" in html
          and "(c % 2 === 1) === flip" in html, "")
    check("⚠️★★★ 周辺視は（左右 × invitation）の組を作ってからシャッフルする",
          "for (const ps of P.positions) for (const iv of [true, false]) cross.push" in html, "")

    # ⚠️★★★ 遷移の合成（★ HIGH 1 / HIGH 2 の回帰）
    check("⚠️★★★ 遷移が不透明オフスクリーンの合成である（★ 重ね塗りしない）",
          "function trOffscreen" in html and "function trCompose(" in html
          and "mix" not in html.split("function drawField")[1].split("\n}")[0], "")
    # ⚠️★★★ 合成の形そのものを文字列で固定する。
    #    ★ 理由: **ページ内検査（catch の不変性）は Python からは走らせられない** ——
    #      `--selfcheck` の HTML 壊しは Python 側の検査でしか赤にならないので、
    #      ★ **壊し方に対応する検査を Python 側にも 1 本置く**必要がある。
    check("⚠️★★★ 合成が『A を不透明で置いてから B を k で重ねる』形である",
          "ctx.globalAlpha = 1; ctx.drawImage(cA, 0, 0);" in html
          and "ctx.globalAlpha = k; ctx.drawImage(cB, 0, 0);" in html, "")

    # ⚠️★★★ **検査が本番と同じ経路を通ること。**★ 別経路だと「検査は緑・本番は壊れている」が起きる。
    check("⚠️★★★ 合成は本番も機械検算も同じ関数（trCompose）を通る",
          html.count("trCompose(") >= 3 and "trCompose(ctx, fA, fB, k, el / 1000, W, H);" in html
          and "trCompose(o, fA, fB, k, 0, W, H);" in html, "")
    check("⚠️★★★ 変化試行の fB が fA と同じ seed（★ 地で答えられない）",
          "const fB = it.change ? buildField(it.trialSeed, it.to, it.variant, W, H) : fA;" in html, "")
    check("★ ページ内検査が catch の不変性と地の一致を対照つきで見ている",
          "catch 試行が合成係数によらず不変" in html
          and "変化試行で地が一致し、図だけが変わる" in html
          and "遷移対ごとの件数が均衡している" in html, "")

    # ⚠️ 検査自身が CFG を壊したまま終わらないこと
    check("⚠️★★★ 機械検算が CFG の壊しを try/finally で戻す",
          html.count("} finally {") >= 4 and "機械検算が CFG を元に戻して終わっている" in html, "")

    # ⚠️ 固視点が提示中は両条件とも隠れる（★ 対照の対称性）
    check("⚠️★★★ 周辺視の固視点が提示中は両条件とも隠れる（★ 中心条件だけ覆われない）",
          '$("per-fix").style.visibility = "hidden";' in html
          and '$("per-fix").style.visibility = "visible";' in html, "")

    # ⚠️ 較正が最初のブロック開始で確定する
    check("⚠️★★★ 較正が最初のブロック開始で確定する（★ 途中で条件が変わらない）",
          "function lockCalibration" in html and html.count("lockCalibration();") >= 4, "")

    # ⚠️ 試行ごとに実施可否を確かめる（★ 窓は試行中にも縮む）
    check("⚠️★★★ 周辺視が試行ごとに実施可否を確かめる（★ 画面外で流れない）",
          "if (!perGeometry().ok) {" in html and html.count("perGeometry()") >= 4, "")

    # ⚠️ 書き出しに窓と偏心の幾何が残る（★ env.md の宣言と揃える）
    check("⚠️★★★ 書き出しに窓と偏心の幾何が残る（★ 開かなかったのか読めなかったのかを分ける）",
          "viewport: { innerWidth:" in html and "peripheral_geometry:" in html, "")

    # ⚠️ ブロック 3 が「教示後（本人）」であることが記録に残る
    check("⚠️★★★ 周辺視が『教示後（本人）』だと記録・結果・limitations に出る",
          "taught: true," in html and "ブロック 3 は「教示後（本人）」である" in html
          and "PS-Q5 の『他者が読める上限』の材料には使えない" in html, "")
    check("⚠️ 遷移ブロックの variant 固定が『仕様』として明記されている（★ 判断 3-B）",
          "`variant` は `natural` に固定する（＝ 仕様である）" in html, "")
    # ★ ブロック 1a の露出に上限と順序シャッフルがあるか
    check("⚠️ ブロック 1a の提示順をシャッフルし、総露出に上限を置いている",
          "FR_MAX_MS" in html and "const order = shuffle(LEVELS.map" in html, "")
    # ★ 実行条件パネル（★ 2026-09-03 追加）
    check("★ invitation の符号を UI で選べる（★ 既定 aperture = ADR-022 D1）",
          'id="sel-inv"' in html and 'INV_CODING = "aperture";' in html, "")
    check("⚠️★★★ 事前露出の申告欄があり、結果の limitations に刻まれる",
          'id="chk-exposed"' in html and "prior_exposure" in html
          and "ブロック 1b（未教示）は無効" in html, "")

    check("⚠️★★★ 写像がブロック 1b まで封印される（C7）",
          "sealed" in html and "unseal" in html, "")
    check("⚠️ C7 を明文で持っている（事前に『読めますか』と聞かない）",
          "読めますか" in html, "")

    # --- 10. ⚠️ 禁止語が「被験者が見る文言」に出ていないか -------------------
    #    ★ ADR-018 D3 が禁じるのは **UI・表現層・ログ** の語であって、
    #      研究者向けの方法論注記ではない。
    #    ⚠️★★★ 2026-09-02: 最初は HTML 全文を grep して 2 件拾ったが、実体は
    #      (a) 「その合格*スコア*は ISO 9186-1 本文に存在しない」という**警告文**、
    #      (b) 検査自身の名前、の 2 つだった。
    #      → ★ **検査を弱めるのではなく、対象を「被験者が見る文言」へ精密化した。**
    #      ★ 全文 grep に戻すと (a) を消すことになり、消してはいけないものが消える。
    def participant_facing(src: str) -> str:
        """被験者が実際に読む文字列だけを集める。"""
        chunks: list[str] = []
        # 状態のラベル（LEVEL_JA）
        m = re.search(r"const LEVEL_JA = \{(.*?)\n\};", src, re.S)
        if m:
            chunks.append(m.group(1))
        # 強制選択のボタン文言
        chunks += re.findall(r'class="choice"[^>]*>([^<]*)<', src)
        # ⚠️★★★ 2026-09-08: **`per` を足した。**★ 足さないと周辺視ブロックの文言が
        #    禁止語検査の外に落ちる（＝ 検査が新しいブロックを見ていない）。
        chunks += re.findall(r'\$\("(?:fr|bt|tr|per)-hint"\)\.textContent = "([^"]*)"', src)
        # 応答欄の設問文（<p class="note"> のうち ① ② で始まるもの）
        chunks += re.findall(r'<p class="note">([①②][^<]*)<', src)
        # オンボーディングで見せる文言
        for key in ("ob-inv", "ob-nodata"):
            chunks += re.findall(rf'\$\("{key}"\)\.innerHTML =\s*(.*?);\n', src, re.S)
        return " ".join(chunks)

    facing = participant_facing(html)
    check("★ 被験者が見る文言を抽出できている（★ 空なら検査が空振りしている）",
          len(facing) > 200, f"{len(facing)} 文字")
    # ⚠️★★★ 新しいブロックの文言が抽出に入っているか（★ 検査が新ブロックを見ていない事故を防ぐ）
    check("★ 抽出が周辺視ブロックの文言まで届いている",
          "中央の" in facing, "per-hint の文言")

    forbidden_hard = ["達成", "完了", "クリア", "スコア", "ポイント", "ランキング", "%", "残り"]
    hits = [w for w in forbidden_hard if w in facing]
    check("⚠️ 被験者が見る文言に達成・順位・数値の語が無い（ADR-018 D3 / D3 の『数値・順位・達成度を出さない』）",
          not hits, f"検出: {hits}" if hits else "なし")

    # ★ 併せて「警告文が消えていないこと」を検査する（★ 上の精密化で守るべきもの）
    check("⚠️★★★ ページ内の禁止語検査が 4 ブロックの『箱』を走査する（★ canvas 単独では空）",
          'const boxes = ["fr-box", "bt-box", "tr-box", "per-box"];' in html
          and "空の箱" in html, "")

    check("★ ISO 9186 の合格スコア否認が UI に残っている（★ 精密化で消していないこと）",
          "ISO 9186-1 本文に存在しない" in html, "")

    # ⚠️ glossary 禁止用語（限定資源モデルの語彙）
    banned_glossary = ["認知リソース", "リソースの補充", "消耗", "回復した"]
    ghits = [w for w in banned_glossary if w in html or w in json.dumps(cfg, ensure_ascii=False)]
    check("⚠️★★★ 限定資源モデルの語彙を使っていない（glossary 禁止用語）",
          not ghits, f"検出: {ghits}" if ghits else "なし")

    # --- 10b. ⚠️★★★ HTML 内の JS が構文として通るか ----------------------
    #    ★ 2026-09-03 追加。⚠️ **編集で構文エラーを入れたのが 2 回目だったので置いた。**
    #      1 回目: コメントの `*/` を重ねた → `REC is not defined`
    #      2 回目: 単引用符の中に `1b'` を書いた → `SyntaxError: Unexpected number`
    #    ⚠️★★★ **どちらもブラウザで開くまで分からなかった。**
    #      ★ Python 側は文字列 grep しかしていないので、**壊れた JS でも緑のまま通っていた。**
    #    → ★ `verify-before-claiming` ルール 6: 主張のとなりに検査を置く。
    m = re.search(r"<script>(.*?)</script>", html, re.S)
    if not m:
        check("⚠️★★★ HTML 内の JS を抽出できた", False, "<script> ブロックが見つからない")
    elif (node_exe := shutil.which("node")) is None:
        # ⚠️ node が無いことを「緑」にしない。★ 検査できなかったことを明示する。
        check("⚠️ HTML 内の JS が構文として通る（★ node 不在でスキップ）", False,
              "node が見つからない → ★ 構文検査を実行できていない")
    else:
        with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as fh:
            fh.write(m.group(1))
            js = Path(fh.name)
        try:
            # ★ `--check` は実行せずに構文だけを見る
            # ⚠️ 名前ではなく **`shutil.which` が返した絶対パス**で起動する
            #    （★ Windows の CreateProcess は探索順に **カレントディレクトリ**を含むので、
            #      ★ 実行した場所に `node.exe` が置かれていると、そちらが動く）。
            #    ★ `--selfcheck` は `run()` を 19 回回すので、起動回数も相応に増えている。
            r = subprocess.run([node_exe, "--check", str(js)], capture_output=True, text=True)
            detail = "OK" if r.returncode == 0 else (r.stderr.strip().splitlines() or ["?"])[0][:160]
            check("⚠️★★★ HTML 内の JS が構文として通る（node --check）", r.returncode == 0, detail)
        finally:
            js.unlink(missing_ok=True)

    # --- 11. ★ 再現性: seed が config に固定されているか -------------------
    check("出題順の seed が config にある（reproducibility ルール 2）",
          isinstance(cfg["blind_test"].get("order_seed"), int), str(cfg["blind_test"].get("order_seed")))
    check("HMM_VERSION が刻まれている（reproducibility ルール 3）",
          bool(cfg.get("hmm_version")), str(cfg.get("hmm_version")))


# ⚠️★★★ HTML 側の壊し方（★ 2026-09-08 追加）。
#    ★ config の壊し（下の selfcheck）は **HTML 側の検査を 1 つも赤にしない** ——
#      ★ つまり「HTML を見ている検査が空回りしていないか」は別に潰す必要がある。
#    ★ 各行の主張: **この壊し方をしたら、この検査が赤になる。**
#    (ラベル, 置換前, 置換後, 赤になるべき検査に含まれる語)
HTML_MUTATIONS: list[tuple[str, str, str, str]] = [
    ("旧 btn-bt-abort を復活させる",
     '<button id="btn-bt-start"',
     '<button id="btn-bt-abort" disabled>中止する</button><button id="btn-bt-start"',
     "旧 btn-bt-abort の要素・参照が無い"),
    ("ブロック 3 の中止を外す", ", perAbort);", ");", "4 ブロックすべてが overlayOn に中止関数"),
    ("ブロック 1a の中止を外す", ", frAbort);", ");", "4 ブロックすべてが overlayOn に中止関数"),
    ("logAbort の宛先をハードコードへ戻す",
     'function logAbort(msg, taught) {\n  const el = $(taught ? "bt2-state" : "bt-state");',
     'function logAbort(msg) {\n  const el = $("bt-state");',
     "中止の告知が 1b / 1b\' で別の欄"),
    ("固視点を消す", 'id="per-fix"', 'id="per-fixX"', "周辺視ブロックが実装されている"),
    ("実施可否ゲートの文言を消す", "偏心を黙って縮めて走らせません", "偏心を縮めて走ります", "黙って縮めない"),
    ("周辺視の出題順のシャッフルを外す", "for (const c of shuffle(cells, rng))", "for (const c of cells)",
     "出題順が seed でシャッフル"),
    ("周辺視の hint を抽出できない形にする",
     '$("per-hint").textContent = "★ 中央の ＋ を見続けてください";',
     '$("per-hint").innerHTML = "★ 中央の ＋ を見続けてください";',
     "抽出が周辺視ブロックの文言まで届いている"),
    ("ページ内の hit-test 検査を消す", "hit-test できる", "hit-test-was-here", "hit-test を対照つき"),
    ("遷移の合成を『1-k で重ねる』旧型へ戻す（＝ catch が明滅する）",
     "ctx.globalAlpha = 1; ctx.drawImage(cA, 0, 0);",
     "ctx.globalAlpha = 1 - k; ctx.drawImage(cA, 0, 0);",
     "A を不透明で置いてから B を k で重ねる"),
    ("遷移の fB を別 seed へ戻す（＝ 地が総入れ替わりする）",
     "const fB = it.change ? buildField(it.trialSeed, it.to, it.variant, W, H) : fA;",
     "const fB = it.change ? buildField(it.trialSeed + 3, it.to, it.variant, W, H) : fA;",
     "変化試行の fB が fA と同じ seed"),
    ("invitation を位置で決める形へ戻す（＝ variant と交絡しうる）",
     "const flip = ((lvIdx + vids.indexOf(v)) % 2) === 0;", "const flip = true;",
     "invitation を variant の中で層別"),
    ("周辺視の（左右 × invitation）の組を崩す",
     "for (const ps of P.positions) for (const iv of [true, false]) cross.push({ pos: ps, inv: iv });",
     "for (const ps of P.positions) cross.push({ pos: ps, inv: true }, { pos: ps, inv: false });",
     "（左右 × invitation）の組を作ってから"),
    ("禁止語検査を canvas 単独の走査へ戻す",
     'const boxes = ["fr-box", "bt-box", "tr-box", "per-box"];',
     'const boxes = ["stage-fr", "stage-bt", "stage-tr", "stage-per"];',
     "4 ブロックの『箱』を走査"),
    # ⚠️ 置換後の語が置換前を **部分文字列として含む** と、検査は緑のままになる
    #    （★ 2026-09-08 に実測: `function lockCalibrationX` は `function lockCalibration` を含む）。
    #    → ★ **呼び出し側を消す**形にした。
    ("較正のロックを外す", "lockCalibration();", "/* ロックしない */;",
     "較正が最初のブロック開始で確定"),
    ("overlayOff の他人ガードを外す",
     "if (activeOverlay !== null && activeOverlay !== boxId) return;", "",
     "他ブロックの片付けを拒む"),
    ("blockRunning から activeOverlay を外す",
     "return !!(bt || tr || per || activeOverlay);", "return !!(bt || tr || per);",
     "blockRunning がブロック 1a"),
    ("周辺視で【可視にしてから描く】順序へ戻す",
     '''drawField(ctx, field, 0, it.invitation, W, H);
        $("per-stage").style.visibility = "visible";''',
     '''$("per-stage").style.visibility = "visible";
        drawField(ctx, field, 0, it.invitation, W, H);''',
     "描いてから】可視にする"),
]


def _run_quiet(cfg_path: Path, html_path: Path) -> None:
    """★ 出力を捨てて run() を回し、FAILS / OKS だけを残す。"""
    import contextlib
    import io
    FAILS.clear()
    OKS.clear()
    with contextlib.redirect_stdout(io.StringIO()):
        try:
            run(cfg_path, html_path)
        except Exception as e:                      # noqa: BLE001
            FAILS.append(f"例外 :: {e}")


def selfcheck_html(here: Path) -> int:
    """⚠️★★★ HTML を壊して、**狙った検査が**赤になることを実測する。"""
    print("== selfcheck / HTML（★ HTML を見ている検査が効いていることの検査） ==")
    cfg_path = here / "layerA.config.json"
    html = (here / "player" / "layerA.html").read_text(encoding="utf-8")
    hit = 0
    for label, old, new, expect in HTML_MUTATIONS:
        if old not in html:
            print(f"  [FAIL] 壊し: {label} → ⚠️ 置換対象が HTML に無い（★ 壊せていない）")
            continue
        with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as fh:
            fh.write(html.replace(old, new))
            ph = Path(fh.name)
        try:
            _run_quiet(cfg_path, ph)
        finally:
            # ⚠️ `_run_quiet` は Exception を握るが、KeyboardInterrupt / SystemExit は抜ける。
            #    ★ 同ファイルの `node --check` 側と作法を揃える。
            ph.unlink(missing_ok=True)
        caught = [f for f in FAILS if expect in f]
        hit += bool(caught)
        print(f"  [{'PASS' if caught else 'FAIL'}] 壊し: {label} → 赤 {len(FAILS)} 件"
              + ("" if caught else f" ⚠️ 期待した検査が赤にならなかった: {expect}"))
    print(f"selfcheck / HTML: {hit} / {len(HTML_MUTATIONS)} の壊しを検出")
    return 0 if hit == len(HTML_MUTATIONS) else 1


def selfcheck() -> int:
    """⚠️★★★ ルール 5b: 検査自体を壊して赤になることを実測する。"""
    print("== selfcheck（★ 検査が効いていることの検査） ==")
    here = Path(__file__).resolve().parent.parent
    cfg = json.loads((here / "layerA.config.json").read_text(encoding="utf-8"))
    html = (here / "player" / "layerA.html").read_text(encoding="utf-8")

    import tempfile
    broke = 0
    # ★ 壊し方 1: 周波数を帯域外へ
    for mutate, label in [
        (lambda c: c["invitation"].update(frequency_hz=9.0), "周波数を 9 Hz にする"),
        (lambda c: c["stimulus"].update(stimulus_ms=6000), "提示を 6 秒にする"),
        (lambda c: c["levels"]["layer0"].update(has_figure=True), "層 0 に図を持たせる"),
        (lambda c: c["field"].update(ground_marks=0), "地の粒を 0 にする"),
        (lambda c: c["transition_test"].update(catch_trials=0), "catch を 0 にする"),
        (lambda c: c["render"].update(default_theme="warm"), "既定テーマを色付きにする"),
        # ★ 2026-09-08 追加（★ 周辺視ブロック）
        (lambda c: c["peripheral_test"].update(control_center_trials=0), "周辺視の中心対照を外す"),
        (lambda c: c["peripheral_test"].update(eccentricity_deg=2.0), "偏心を [P85] の帯の外にする"),
    ]:
        import copy
        c = copy.deepcopy(cfg)
        mutate(c)
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as fh:
            json.dump(c, fh, ensure_ascii=False)
            p = Path(fh.name)
        FAILS.clear(); OKS.clear()
        import io, contextlib
        with contextlib.redirect_stdout(io.StringIO()):
            try:
                run(p, here / "player" / "layerA.html")
            except Exception:
                pass
        p.unlink(missing_ok=True)
        detected = len(FAILS) > 0
        broke += detected
        print(f"  [{'PASS' if detected else 'FAIL'}] 壊し: {label} → 赤 {len(FAILS)} 件")
    print(f"selfcheck: {broke} / 8 の壊しを検出")
    # ⚠️★★★ HTML 側も続けて潰す（★ config の壊しは HTML 側の検査を 1 つも赤にしない）
    rc_html = selfcheck_html(here)
    return 0 if (broke == 8 and rc_html == 0) else 1


def main() -> int:
    if "--selfcheck" in sys.argv:
        return selfcheck()
    cfg_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent / "layerA.config.json"
    html_path = Path(sys.argv[2]) if len(sys.argv) > 2 else cfg_path.parent / "player" / "layerA.html"
    print(f"== selftest: {cfg_path.name} / {html_path.name} ==")
    run(cfg_path, html_path)
    print(f"\n結果: {len(OKS)} PASS / {len(FAILS)} FAIL")
    if FAILS:
        print("\n⚠️ FAIL:")
        for f in FAILS:
            print("  - " + f)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
