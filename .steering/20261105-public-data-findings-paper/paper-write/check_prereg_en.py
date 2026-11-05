"""事前登録の英語版と日本語版の機械の照合（付録 E の (1)）。

両方のファイルから、数値・SHA-256 とコミット（16 進の 7 桁以上）・バッククォートのコードの名・文献の鍵 [Vnnn]・
不等号の記号を節（P0〜P11・付録 A〜F・用語）ごとに抜き出して比べる。日本語の数の単位（億・万）は英語の表記に直して比べる。
使い方: python3 -I check_prereg_en.py <日本語版> <英語版>（食い違いが無ければ終了コード 0）。
"""
import re
import sys
from collections import Counter

JA_HEAD = re.compile(r"^## (P\d+|付録 [A-F]|用語)")
EN_HEAD = re.compile(r"^## (P\d+|Appendix [A-F]|Terms)")
EN2JA = {"Terms": "用語", **{f"Appendix {c}": f"付録 {c}" for c in "ABCDEF"}}
HEX = re.compile(r"\b(?=[0-9a-f]*[a-f])[0-9a-f]{7,64}\b")  # 英字を含む 16 進だけ（数字だけの数は数として比べる）
CODE = re.compile(r"`([^`]+)`")
VKEY = re.compile(r"\[V\d+\]")
SYM = re.compile(r"[≥≤±]|(?<=[\s\w])[<>](?=\s)")  # 差し込み口の <…> は数えない
NUM = re.compile(r"(?<![0-9A-Za-z_.])[−-]?\d+(?:,\d{3})*(?:\.\d+)?")  # 符号を保つ。日本語の文字に接した数も取る


def ja_units(text):
    # 数え方の数（1 つ・2 段目・3 つ目・2 通り など）は英語では語になるので比べない
    text = re.sub(r"\d+ ?(つ目|つ|段目|段|番目|か所|通り|本)", " ", text)
    text = re.sub(r"1 ?分あたり", "分あたり", text)  # 英語では per minute
    # 1.68 億 → 168000000、1,342 万 → 13420000 の形に直す（英語版は million で書く）
    text = re.sub(r"(\d+(?:\.\d+)?) ?億", lambda m: str(round(float(m.group(1)) * 1e8)), text)
    return re.sub(r"(\d+(?:,\d{3})*(?:\.\d+)?) ?万", lambda m: str(round(float(m.group(1).replace(",", "")) * 1e4)), text)


def en_units(text):
    text = re.sub(r"\b(one|two|three|four|five|first|second|third)\b", " ", text)
    return re.sub(r"(\d+(?:\.\d+)?) million", lambda m: str(round(float(m.group(1)) * 1e6)), text)


def sections(path, head, norm):
    out, cur = {}, "head"
    for line in open(path, encoding="utf-8"):
        m = head.match(line)
        if m:
            cur = norm(m.group(1))
        out.setdefault(cur, []).append(line)
    return {k: "".join(v) for k, v in out.items()}


PLACEHOLDER = re.compile(r"<(?! )[^<>\n]+?>")  # 差し込み口（<信号・ε>・<OSF URL> など）。不等号の「< 0.5」は空白が続くので当たらない


def items(text, units):
    # コードの名・16 進・文献の鍵は正規化の前の原文から取る
    codes = [c for c in CODE.findall(text) if not re.search(r"[ぁ-んァ-ヶ一-龯]|<[^>]*>", c)]  # 差し込み口を含むコードの名は訳してよい
    hexes, vkeys = HEX.findall(text), VKEY.findall(text)
    t = units(PLACEHOLDER.sub(" ", CODE.sub(" ", text)))
    nums = [n.replace(",", "").replace("−", "-") for n in NUM.findall(HEX.sub(" ", t))]
    return {"hex": Counter(hexes), "code": Counter(codes), "vkey": Counter(vkeys),
            "sym": Counter(SYM.findall(t)), "num": Counter(nums)}


def main(ja_path, en_path):
    ja = sections(ja_path, JA_HEAD, lambda k: k)
    en = sections(en_path, EN_HEAD, lambda k: EN2JA.get(k, k))
    bad = 0
    keys = sorted(set(ja) | set(en))
    for k in keys:
        if k not in ja or k not in en:
            print(f"節が片方にしかない: {k}")
            bad += 1
            continue
        a, b = items(ja[k], ja_units), items(en[k], en_units)
        for kind in ("hex", "code", "vkey", "sym", "num"):
            if kind == "num":
                # 小数・符号つき・10 以上の数は出現の回数で、1 桁の整数（数え方や分岐の番号で日英の回数が自然に違う）は集合で比べる
                small = lambda c: Counter({x: 1 for x in c if re.fullmatch(r"\d", x)})  # noqa: E731
                big = lambda c: Counter({x: n for x, n in c.items() if not re.fullmatch(r"\d", x)})  # noqa: E731
                miss = (big(a[kind]) - big(b[kind])) + (small(a[kind]) - small(b[kind]))
                extra = (big(b[kind]) - big(a[kind])) + (small(b[kind]) - small(a[kind]))
            else:
                miss, extra = a[kind] - b[kind], b[kind] - a[kind]  # 出現の回数で比べる
            if k == "用語" and kind == "num":
                extra = Counter()  # 英語版の用語の節には対訳の表があり、数を足すことがある（日本語版にだけある数は食い違いのまま）
            if miss or extra:
                print(f"{k} {kind}: 日本語版にだけ {sorted(miss.elements())} / 英語版にだけ {sorted(extra.elements())}")
                bad += 1
    print("一致" if not bad else f"食い違い {bad} 件")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
