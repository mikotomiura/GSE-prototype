#!/usr/bin/env python3
"""★ G1: 課題の分野が「文書」と「メール実装」でズレていないかを機械検査する。

`preregistration.md §2.12-1` は **課題の分野を事前案内メールで開示する**と凍結した。
その文面を作るのは `Form_G1/GSE_G1_Form_Builder.gs` の `G1_TOPIC_TITLES` だが、
真実源は `materials/topicNN_*.md` の front matter `title:` である。

⚠️ ★ **同じ事実を 2 か所に持っている**ので、片方だけ直すと必ずズレる。
このプロジェクトは「文書だけ改訂して実装が追随しない」事故を繰り返しており
（`.steering/20260802-g1-execution-prep/decisions.md` E-6 / E-7、`notes.md` 第 5 版の教訓）、
**約束を書いたらその約束自体を検査する**ことにしている。本スクリプトはその検査である。

ズレると何が起きるか: 被験者に送った分野と、当日配る課題文の分野が食い違う。
`§2.12` の「事前に開示する」という凍結を、**実際には守れていない**ことになる。

使い方:
    python3 scripts/check_g1_topic_titles.py          # 検査（exit 1 でズレ）
"""

from __future__ import annotations

import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
MATERIALS = REPO / "experiments" / "20260801-controlled-friction-task" / "materials"
GAS = REPO / "Form_G1" / "GSE_G1_Form_Builder.gs"
N_TOPICS = 8


def titles_from_materials() -> list[str]:
    """materials/topicNN_lo.md の front matter `title:` を NN 順に返す。"""
    out: list[str] = []
    for n in range(1, N_TOPICS + 1):
        p = MATERIALS / f"topic{n:02d}_lo.md"
        if not p.is_file():
            raise SystemExit(f"[NG] {p} が無い")
        m = re.search(r"^title:\s*(.+?)\s*$", p.read_text(encoding="utf-8"), re.M)
        if not m:
            raise SystemExit(f"[NG] {p.name} に front matter の title: が無い")
        out.append(m.group(1))

        # ★ hi 版が同じ題材（同じ title）であることも見る。§2.7-1 は「同じ NN の lo/hi は
        #   同じ題材」を要求しており、ここがズレると分野の開示自体が意味を失う。
        ph = MATERIALS / f"topic{n:02d}_hi.md"
        if ph.is_file():
            mh = re.search(r"^title:\s*(.+?)\s*$", ph.read_text(encoding="utf-8"), re.M)
            if mh and mh.group(1) != m.group(1):
                raise SystemExit(
                    f"[NG] topic{n:02d}: lo と hi で title が違う "
                    f"(lo={m.group(1)!r} / hi={mh.group(1)!r})。§2.7-1 は同じ題材であることを要求する"
                )
    return out


def titles_from_gas() -> list[str]:
    """`G1_TOPIC_TITLES = [...]` の中身を宣言順に返す。"""
    if not GAS.is_file():
        raise SystemExit(f"[NG] {GAS} が無い")
    text = GAS.read_text(encoding="utf-8")
    m = re.search(r"var\s+G1_TOPIC_TITLES\s*=\s*\[(.*?)\]\s*;", text, re.S)
    if not m:
        raise SystemExit(
            "[NG] Form_G1/GSE_G1_Form_Builder.gs に G1_TOPIC_TITLES が見つからない。"
            "★ §2.12-1 は分野を事前開示すると凍結しているので、実装が消えていたら赤にする"
        )
    return re.findall(r'"([^"]+)"', m.group(1))


def check_run_columns() -> list[str]:
    """★ `runCol_("...")` が参照する列名が `RUN_HEADER` に実在するかを静的に検査する。

    GAS は実行するまで例外が出ないので、列名のタイポは **管理シートを作る当日**まで露見しない。
    第 6 版で列を 2 つ足したとき、ハードコードした列番号が全部ズレた（静かに間違う形だった）ので
    ヘッダ名参照に変えた。その参照が正しいことは、ここで見るしかない。
    """
    text = GAS.read_text(encoding="utf-8")
    m = re.search(r"var\s+RUN_HEADER\s*=\s*\[(.*?)\]\s*;", text, re.S)
    if not m:
        return ["Form_G1 に RUN_HEADER が見つからない"]
    headers = re.findall(r'"([^"]+)"', m.group(1))
    # ★ 直接の runCol_("...") と、applyRunValidation_ 内の薄い wrapper apply("...", [...]) の両方を拾う。
    #   ⚠️ 最初 runCol_ だけを見ていたため、列名にタイポを入れても緑のままだった
    #      （= 検査が空回りしていた）。空回りしていないことを実測してから固定すること。
    referenced = re.findall(r'(?:runCol_|apply)\(\s*"([^"]+)"', text)
    if not referenced:
        return ["列名の参照が 1 つも見つからない（検査が空回りしている疑い）"]
    return [
        f'列 "{r}" の参照が RUN_HEADER に無い（列名を変えたら参照側も直す）'
        for r in sorted(set(referenced))
        if r not in headers
    ]


def main() -> int:
    mats = titles_from_materials()
    gas = titles_from_gas()

    col_errors = check_run_columns()
    if col_errors:
        print("[NG] ★ G1 実施トラッキングの列参照が壊れている")
        for e in col_errors:
            print(f"  - {e}")
        return 1

    if mats == gas:
        print(f"[OK] 課題の分野が一致している（{len(mats)} 件）")
        print("     materials/topicNN_*.md の title == Form_G1 の G1_TOPIC_TITLES")
        return 0

    print("[NG] ★ 課題の分野がズレている（事前案内メールと当日の課題文が食い違う）")
    print(f"  materials ({len(mats)} 件): {mats}")
    print(f"  Form_G1   ({len(gas)} 件): {gas}")
    for i in range(max(len(mats), len(gas))):
        a = mats[i] if i < len(mats) else "(無し)"
        b = gas[i] if i < len(gas) else "(無し)"
        if a != b:
            print(f"  - topic{i + 1:02d}: materials={a!r} / Form_G1={b!r}")
    print()
    print("  ★ 真実源は materials/ 側である。Form_G1 の G1_TOPIC_TITLES を合わせること。")
    print("  ⚠️ 被験者に送った分野と当日配る課題文が違うと、§2.12 の『事前に開示する』を守れていない。")
    return 1


if __name__ == "__main__":
    sys.exit(main())
