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
import sys
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
    # ★ クロスフェードが乗算になっているか
    check("★ drawField が mix を乗算している（⚠️ 絶対代入でない）",
          "0.45 * mix" in html and "1.0 * mix" in html, "")
    # ★ 中止後の再開で結果配列がクリアされるか
    check("★ 中止後の再開で前回の途中結果を破棄する",
          "arr.length = 0;" in html, "")
    # ★ ブロック 1a の露出に上限と順序シャッフルがあるか
    check("⚠️ ブロック 1a の提示順をシャッフルし、総露出に上限を置いている",
          "FR_MAX_MS" in html and "const order = shuffle(LEVELS.map" in html, "")
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
        chunks += re.findall(r'\$\("(?:fr|bt|tr)-hint"\)\.textContent = "([^"]*)"', src)
        # 応答欄の設問文（<p class="note"> のうち ① ② で始まるもの）
        chunks += re.findall(r'<p class="note">([①②][^<]*)<', src)
        # オンボーディングで見せる文言
        for key in ("ob-inv", "ob-nodata"):
            chunks += re.findall(rf'\$\("{key}"\)\.innerHTML =\s*(.*?);\n', src, re.S)
        return " ".join(chunks)

    facing = participant_facing(html)
    check("★ 被験者が見る文言を抽出できている（★ 空なら検査が空振りしている）",
          len(facing) > 200, f"{len(facing)} 文字")

    forbidden_hard = ["達成", "完了", "クリア", "スコア", "ポイント", "ランキング", "%", "残り"]
    hits = [w for w in forbidden_hard if w in facing]
    check("⚠️ 被験者が見る文言に達成・順位・数値の語が無い（ADR-018 D3 / D3 の『数値・順位・達成度を出さない』）",
          not hits, f"検出: {hits}" if hits else "なし")

    # ★ 併せて「警告文が消えていないこと」を検査する（★ 上の精密化で守るべきもの）
    check("★ ISO 9186 の合格スコア否認が UI に残っている（★ 精密化で消していないこと）",
          "ISO 9186-1 本文に存在しない" in html, "")

    # ⚠️ glossary 禁止用語（限定資源モデルの語彙）
    banned_glossary = ["認知リソース", "リソースの補充", "消耗", "回復した"]
    ghits = [w for w in banned_glossary if w in html or w in json.dumps(cfg, ensure_ascii=False)]
    check("⚠️★★★ 限定資源モデルの語彙を使っていない（glossary 禁止用語）",
          not ghits, f"検出: {ghits}" if ghits else "なし")

    # --- 11. ★ 再現性: seed が config に固定されているか -------------------
    check("出題順の seed が config にある（reproducibility ルール 2）",
          isinstance(cfg["blind_test"].get("order_seed"), int), str(cfg["blind_test"].get("order_seed")))
    check("HMM_VERSION が刻まれている（reproducibility ルール 3）",
          bool(cfg.get("hmm_version")), str(cfg.get("hmm_version")))


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
    print(f"selfcheck: {broke} / 6 の壊しを検出")
    return 0 if broke == 6 else 1


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
