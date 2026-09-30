"""S-11 の語形・一般の構成概念の語と、S-09 の枠組みの機械のふるい（design.md §1.2・§2.3・2026-09-30 18:05 に固定）。

★ 判定ではない。題名＋抄録に当てて、当たった語の文字列と記号だけを返す（抄録の文は返さない）。
検査は test_screen.py（`python -m unittest test_screen` を、このディレクトリで実行）。
"""
import re

I = re.I

AIW = (r"(?:gen(?:erative)?[\s-]*AI|GenAI|(?<![A-Za-z])AI(?![A-Za-z])|artificial[\s-]+intelligence|ChatGPT|"
       r"(?<![A-Za-z])GPT(?![A-Za-z])|(?<![A-Za-z])LLMs?(?![A-Za-z])|large[\s-]+language[\s-]+models?|chat[\s-]?bots?|"
       r"conversational[\s-]+agents?)")
FAT = r"(?:fatigue|burn-?out|exhaustion|weariness|tiredness)"

# S-11 語形（design.md §1.2）
TERMS = {
    "N1": re.compile(AIW + r"(?:[\s-]+(?:induced|related|driven|based|use|usage|interaction|assisted|tools?|technology))?"
                     r"[\s-]+" + FAT, I),
    "N2": re.compile(FAT + r"[\s-]+(?:from|with|of|toward|towards|to|caused[\s-]+by|due[\s-]+to|related[\s-]+to|induced[\s-]+by|"
                     r"associated[\s-]+with)[\s-]+(?:(?:the|using|interacting[\s-]+with)[\s-]+)?(?:(?:use|usage|overuse)[\s-]+of[\s-]+)?"
                     + AIW, I),
    "N3": re.compile(r"prompt(?:ing)?[\s-]+fatigue", I),
    "N4": re.compile(r"(?:AI|ＡＩ|生成\s*AI|人工知能|ChatGPT|LLM|チャットボット)\s*(?:による|への|の)?\s*(?:疲れ|疲労|燃え尽き|バーンアウト|疲弊)|"
                     r"プロンプト疲れ", I),
    "N5": re.compile(AIW + r"(?:[\s-]+(?:induced|related))?[\s-]+(?:techno-?stress|stressors?|stress|anxiety|overload)", I),
}
USES_TERM = ("N1", "N2", "N3", "N4")  # 語を使う記録（N5 だけの記録は入れない）

# 一般の構成概念の語（design.md §1.2・数えるだけ）
GENERAL = {
    "燃え尽き": re.compile(r"burn-?out", I),
    "情動的消耗": re.compile(r"emotional[\s-]+exhaustion", I),
    "消耗": re.compile(r"exhaust(?:ion|ed)", I),
    "精神的・認知的疲労": re.compile(r"(?:mental|cognitive)[\s-]+fatigue", I),
    "決定疲れ": re.compile(r"decision[\s-]+fatigue", I),
    "疲労": re.compile(r"fatigued?", I),
    "テクノストレス": re.compile(r"techno-?stress", I),
    "認知負荷": re.compile(r"cognitive[\s-]+(?:load|overload)", I),
    "情報過多": re.compile(r"information[\s-]+overload", I),
    "負担（strain）": re.compile(r"(?<![A-Za-z])strain(?![A-Za-z])", I),
    "作業負荷": re.compile(r"workload|NASA[\s-]*TLX", I),
    "疲れ": re.compile(r"tired(?:ness)?", I),
}

D = r"[\s-]*[-–]?[\s-]*"
# S-09 枠組み（design.md §2.3）
FRAMEWORKS = {
    "F-JDR": re.compile(r"job[\s-]+demands?[\s-]*(?:and[\s-]*|[-–]\s*)?resources?|(?<![A-Za-z])JD-?R(?![A-Za-z])", I),
    "F-COR": re.compile(r"conservation[\s-]+of[\s-]+resources?|(?<![A-Za-z])COR[\s-]+(?:theory|model)", I),
    "F-TS": re.compile(r"techno-?stress|techno-?stressors?|techno-?(?:overload|invasion|complexity|insecurity|uncertainty)", I),
    "F-CLT": re.compile(r"cognitive[\s-]+load[\s-]+theory|(?<![A-Za-z])CLT(?![A-Za-z])", I),
    "F-SSO": re.compile(r"stressor" + D + r"strain" + D + r"outcomes?|(?<![A-Za-z])SSO(?![A-Za-z])", I),
    "F-TMS": re.compile(r"transactional[\s-]+(?:model|theory)|Lazarus|cognitive[\s-]+appraisal|challenge" + D + r"hindrance", I),
    "F-SDT": re.compile(r"self-determination[\s-]+theory|(?<![A-Za-z])SDT(?![A-Za-z])", I),
    "F-EGO": re.compile(r"ego[\s-]*depletion|strength[\s-]+model|self-control[\s-]+resources?|limited[\s-]+resources?", I),
    "F-SOR": re.compile(r"stimulus" + D + r"organism" + D + r"response|(?<![A-Za-z])S-?O-?R(?![A-Za-z])", I),
    "F-ER": re.compile(r"effort" + D + r"recovery|effort" + D + r"reward[\s-]+imbalance", I),
    "F-PEF": re.compile(r"person" + D + r"(?:environment|job|technology)[\s-]+fit|(?<![A-Za-z])P-?E[\s-]+fit", I),
    "F-OC": re.compile(r"opportunity[\s-]+costs?|motivational[\s-]+control|compensatory[\s-]+control", I),
    "F-AP": re.compile(r"passive[\s-]+fatigue|active[\s-]+fatigue|underload|vigilance[\s-]+decrement", I),
    "F-AUT": re.compile(r"automation[\s-]+(?:bias|complacency)|complacency", I),
    "F-ACC": re.compile(r"technology[\s-]+acceptance[\s-]+model|(?<![A-Za-z])TAM(?![A-Za-z])|UTAUT|uses[\s-]+and[\s-]+gratifications?", I),
    "F-IO": re.compile(r"information[\s-]+overload", I),
}

# 意味を与える文の手がかり（design.md §1.3・印は目安で、決めるのはメイン）
CUES = re.compile(r"defined as|define[sd]?\b|refers? to|conceptuali[sz]|is a (?:state|condition|form|phenomenon|syndrome)|"
                  r"characteri[sz]ed|describ(?:es|ed) as|denot|termed|known as|i\.e\.|dimensions?|components?|comprising|"
                  r"consist(?:s|ing)? of|manifest", I)


def _hits(table, text):
    out = {}
    for key, rx in table.items():
        found = sorted({re.sub(r"\s+", " ", m.group(0)).strip() for m in rx.finditer(text or "")})
        if found:
            out[key] = found
    return out


def terms(text):
    """語形（N1〜N5）の当たり: {記号: [当たった文字列]}。"""
    return _hits(TERMS, text)


def general(text):
    """一般の構成概念の語の当たり: {語の区分: [当たった文字列]}。"""
    return _hits(GENERAL, text)


def frameworks(text):
    """枠組みの当たり: {記号: [当たった文字列]}。"""
    return _hits(FRAMEWORKS, text)


def uses_term(hits):
    return any(k in hits for k in USES_TERM)


def sentences(text):
    """文に分ける（英語は . ? ! の後の空白、日本語は 。で区切る）。"""
    parts = re.split(r"(?<=[.?!])\s+(?=[A-Z0-9\"“(])|(?<=。)", text or "")
    return [p.strip() for p in parts if p and p.strip()]


def cue_sentences(text):
    """語形（N1〜N4）を含む文と、その文に手がかりの語があるか: [(文の番号, 手がかりあり)]。文そのものは返さない。"""
    out = []
    for i, s in enumerate(sentences(text)):
        if uses_term(terms(s)):
            out.append((i, bool(CUES.search(s))))
    return out
