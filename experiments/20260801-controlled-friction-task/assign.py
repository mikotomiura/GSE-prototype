#!/usr/bin/env python3
"""被験者ごとの割付（配置 A/B・題材↔条件・ブロック順）を SEED から決定的に生成する。

出典（凍結・**本スクリプトは変更しない**）:
  preregistration.md §2.3  ブロック構成 [1]=copy / [2..9]=G1(HI4 LO4) / [10]=copy
  preregistration.md §2.7  題材↔条件の被験者間 counterbalance（配置 A / B）
  SEED                     BLOCK_ORDER_SEED（G1 の 8 ブロックのみ対象。copy は位置固定）

使い方:
    python3 assign.py --subject P015           # 印刷用の表
    python3 assign.py --subject P015 --json    # 機械可読（解析入力）
    python3 assign.py --selftest               # 自己検証

★ 実験者は条件を選ばない。この表を記録用紙へ **一方向に転記する**（protocol.md §2.3）。
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import random
import re
import sys

N_TOPICS = 8                 # §2.7: 本番は 8 題材 × 2 版
N_G1_BLOCKS = 8              # §2.3: HI4 / LO4
BLOCK_LAYOUT_COPY = (1, 10)  # §2.3: copy は先頭・末尾に位置固定（無作為化しない）

# §2.7 の配置。A / B で題材↔条件の対応が反転する。
ARRANGEMENTS = {
    "A": {"HI": [1, 2, 3, 4], "LO": [5, 6, 7, 8]},
    "B": {"HI": [5, 6, 7, 8], "LO": [1, 2, 3, 4]},
}


def read_seed(path: pathlib.Path) -> int:
    m = re.search(r"BLOCK_ORDER_SEED\s*=\s*(\d+)", path.read_text(encoding="utf-8"))
    if not m:
        raise SystemExit(f"[NG] {path} に BLOCK_ORDER_SEED が無い")
    return int(m.group(1))


def subject_number(subject: str) -> int:
    m = re.fullmatch(r"P(\d+)", subject)
    if not m:
        raise SystemExit(f"[NG] 被験者 ID は P + 数字の形であること (実際: {subject!r})")
    return int(m.group(1))


def arrangement_for(subject: str) -> str:
    """§2.7: 被験者番号順に A / B を交互に割り付ける。実験者が選ばない。"""
    return "A" if subject_number(subject) % 2 == 1 else "B"


def rng_for(seed: int, subject: str) -> random.Random:
    """seed と被験者 ID から決定的に RNG を作る（プラットフォーム非依存）。"""
    h = hashlib.sha256(f"{seed}:{subject}".encode("utf-8")).hexdigest()
    return random.Random(int(h[:16], 16))


def condition_sequence(rng: random.Random) -> list[str]:
    """§2.3: ABBA 型で釣り合わせた上で系列を無作為化した HI4/LO4 の並び。

    実装: 8 ブロックを 4 つの隣接ペアに分け、各ペアを (HI,LO) か (LO,HI) にする。
    ★ **ちょうど 2 ペアずつ**にすることでペア内の位置が釣り合う（= ABBA 型の釣り合わせ）。
    そのうえでペアの並び順を無作為化する。

    この構成が満たすもの:
      - HI 4 / LO 4（並べ替え検定の C(8,4)=70 の前提）
      - 同条件が 3 連続以上並ばない → 疲労・練習の効果が片側条件に偏りにくい
      - 隣接ペアの少なくとも 4 組が**異条件**になる
        → 操作チェック（§2.6・強制比較）の分母が必ず確保される
    """
    orientations = ["HI_FIRST"] * 2 + ["LO_FIRST"] * 2
    rng.shuffle(orientations)
    pairs = [("HI", "LO") if o == "HI_FIRST" else ("LO", "HI") for o in orientations]
    rng.shuffle(pairs)
    seq = [c for pair in pairs for c in pair]
    assert seq.count("HI") == 4 and seq.count("LO") == 4
    return seq


def assign(subject: str, seed: int) -> dict:
    arr = arrangement_for(subject)
    rng = rng_for(seed, subject)
    conds = condition_sequence(rng)

    pools = {c: list(ARRANGEMENTS[arr][c]) for c in ("HI", "LO")}
    for c in pools:
        rng.shuffle(pools[c])

    blocks: list[dict] = []
    cursor = {"HI": 0, "LO": 0}
    g1_index = 0
    for block_no in range(1, N_G1_BLOCKS + len(BLOCK_LAYOUT_COPY) + 1):
        if block_no in BLOCK_LAYOUT_COPY:
            blocks.append({
                "block": block_no,
                "condition": "copy",
                "topic_id": "copy",
                "material": "materials/copy.md",
                "manipulation_check": False,
            })
            continue
        cond = conds[g1_index]
        g1_index += 1
        topic = pools[cond][cursor[cond]]
        cursor[cond] += 1
        blocks.append({
            "block": block_no,
            "condition": cond,
            "topic_id": f"topic{topic:02d}",
            "material": f"materials/topic{topic:02d}_{cond.lower()}.md",
            # §2.6: 強制比較は G1 ブロック 3〜9 の直後のみ（copy と G1 の最初には聞かない）
            "manipulation_check": 3 <= block_no <= 9,
        })

    return {
        "subject": subject,
        "seed": seed,
        "arrangement": arr,
        "arrangement_note": "A: topic01-04=HI / topic05-08=LO,  B: topic05-08=HI / topic01-04=LO (preregistration.md 2.7)",
        "condition_sequence_g1": conds,
        "blocks": blocks,
        "frozen_sources": ["preregistration.md 2.3", "preregistration.md 2.7", "SEED"],
    }


def validate_pilot_topic(topic: int) -> None:
    """★ P-1 の題材番号は 1..N_TOPICS でなければならない。

    範囲外を黙って受けると `materials/topic09_hi.md` のような**存在しないパス**を
    割付表に出してしまい、当日「封筒に入れる紙が無い」形でしか露見しない。
    """
    if not 1 <= topic <= N_TOPICS:
        raise ValueError(
            f"--pilot-topic は 1..{N_TOPICS} であること (指定: {topic})。"
            f" 本番用の課題文は topic01..topic{N_TOPICS:02d} しか無い (§2.7)"
        )


def pilot_subject(label: str | None) -> str:
    """★ P-1 の被験者 ID。`validate_blocks.py` は **ファイル名 == subject** を要求する
    （`blocks/<subject>.json`）ので、P-1 を複数回回すときはここを分けないと
    **割付ファイルが上書きされる**か、ファイル名不一致で赤くなる。
    """
    if label is None:
        return "PILOT"
    if not re.fullmatch(r"[A-Za-z0-9]{1,8}", label):
        raise ValueError(
            f"--pilot-label は英数字 1..8 文字であること (指定: {label!r})。"
            " ファイル名 blocks/PILOT-<label>.json になるため"
        )
    return f"PILOT-{label}"


def pilot_assign(seed: int, topic: int = 1, label: str | None = None) -> dict:
    """★ パイロット段階 P-1 の縮小セッション（copy / LO / HI / copy の 4 ブロック）。

    ⚠️ **これは確証デザインではない。** 確証デザインは 10 ブロック（copy + G1 8 + copy）であり、
    8 題材が要る（§2.7）。パイロット段階 P-1 の目的は
      (i) 5 分ブロックで**両条件とも**十分な打鍵が出るか（§2.9 の適格性ゲートの実効性）
      (ii) 課題文と手順が機能するか
    の 2 点だけであり、**判定を一切行わない**（§2.8）。
    したがって並べ替え検定も操作チェックも走らせない（C(2,1)=2 では p<0.05 に到達できない）。

    ★ `topic` は P-1 を**複数回**回すときに変える（研究者判断 2026-08-03 = G-4）。
    2 回目で同じ題材を使うと、被験者は 1 回目で HI / LO の両方を書き終えており
    **内容を完全に知った状態**になる。P-1 の目的は打鍵量の測定なので、
    それでは「5 分で十分な打鍵が出るか」の答えが**速く書けるほうへ歪む**。
    ⚠️ ★ `rng_for` のキーは `"PILOT"` のまま変えない。
    → 題材を変えても **LO / HI の提示順は変わらない**（`--pilot` 単独の出力は後方互換）。
      P-1 は判定しないので順序効果を統制する必要が無く、
      むしろ**順序を両回で揃えるほうが 2 回の比較を素直にする**。
    """
    validate_pilot_topic(topic)
    subject = pilot_subject(label)
    # ★ rng のキーは label に依らず "PILOT" 固定（提示順を両回で揃える・後方互換）
    rng = rng_for(seed, "PILOT")
    order = ["LO", "HI"]
    rng.shuffle(order)
    blocks = [{"block": 1, "condition": "copy", "topic_id": "copy",
               "material": "materials/copy.md", "manipulation_check": False}]
    for i, cond in enumerate(order, start=2):
        blocks.append({
            "block": i,
            "condition": cond,
            "topic_id": f"topic{topic:02d}",
            "material": f"materials/topic{topic:02d}_{cond.lower()}.md",
            "manipulation_check": False,
        })
    blocks.append({"block": 4, "condition": "copy", "topic_id": "copy",
                   "material": "materials/copy.md", "manipulation_check": False})
    return {
        "subject": subject,
        "seed": seed,
        "stage": "P-1",
        "pilot_topic": topic,
        "confirmatory": False,
        "arrangement": None,
        "warning": "NOT the confirmatory design. 4 blocks, 1 topic, no verdict. See preregistration.md 2.8.",
        "known_violations_of_the_confirmatory_design": [
            "the SAME topic is shown in BOTH conditions to the same person, which 2.7 forbids in the confirmatory design (the second block is contaminated by familiarity). Acceptable ONLY because P-1 makes no verdict and only measures keystroke yield.",
            "C(2,1)=2 permutations cannot reach p<0.05, so no test is run",
            "the forced-comparison chain (2.6) does not exist with a single HI/LO pair",
        ],
        "purposes": [
            "keystroke yield in BOTH conditions (feeds the 2.9 eligibility gate)",
            "do the materials and the procedure work",
        ],
        "blocks": blocks,
        "frozen_sources": ["preregistration.md 2.8"],
    }


def render(a: dict) -> str:
    out = []
    if a.get("confirmatory") is False:
        out += [
            "=" * 72,
            "★ パイロット段階 P-1（縮小セッション・**確証デザインではない**）",
            "   4 ブロック / 1 題材 / 判定を行わない（preregistration.md §2.8）",
            "   このデータを確証標本に入れないこと。",
            "   ⚠️ 同じ題材を HI と LO の両方で出す（2 本目は内容を知っている）。",
            "      確証デザインでは §2.7 が禁じる形であり、P-1 が判定しないから許される。",
            "=" * 72,
            "",
        ]
    out += [
        f"被験者 ID : {a['subject']}",
        f"配置       : {a['arrangement']}   ({a.get('arrangement_note', '-')})",
        f"seed       : {a['seed']}  (SEED / BLOCK_ORDER_SEED)",
        "",
        " #  | 条件 | 題材ID   | 課題文                        | 強制比較",
        "----+------+----------+-------------------------------+---------",
    ]
    for b in a["blocks"]:
        out.append(f" {b['block']:2d} | {b['condition']:4s} | {b['topic_id']:8s} | "
                   f"{b['material']:29s} | {'○' if b['manipulation_check'] else '−'}")
    out += [
        "",
        "★ この表を記録用紙へ **一方向に転記する**（protocol.md §2.2 / §2.3）。",
        "★ 封筒の外面にはブロック番号と題材 ID **だけ**を書く。条件は書かない（protocol.md §5）。",
    ]
    return "\n".join(out)


def selftest(seed: int) -> int:
    fails: list[str] = []
    subjects = [f"P{n:03d}" for n in range(15, 25)]
    per_subject = {s: assign(s, seed) for s in subjects}

    for s, a in per_subject.items():
        g1 = [b for b in a["blocks"] if b["condition"] in ("HI", "LO")]
        conds = [b["condition"] for b in g1]
        topics = [b["topic_id"] for b in g1]

        if len(a["blocks"]) != 10:
            fails.append(f"{s}: ブロックが 10 個でない")
        if [b["block"] for b in a["blocks"] if b["condition"] == "copy"] != list(BLOCK_LAYOUT_COPY):
            fails.append(f"{s}: copy が先頭・末尾に固定されていない (§2.3)")
        if conds.count("HI") != 4 or conds.count("LO") != 4:
            fails.append(f"{s}: HI4/LO4 でない -> {conds}")
        if len(set(topics)) != N_TOPICS:
            fails.append(f"{s}: 題材が重複している -> {topics}")
        # §2.7: 題材↔条件は配置どおり
        want = ARRANGEMENTS[a["arrangement"]]
        for b in g1:
            num = int(b["topic_id"][-2:])
            if num not in want[b["condition"]]:
                fails.append(f"{s}: 配置 {a['arrangement']} で {b['topic_id']} が {b['condition']} になっている")
        # 同条件の 3 連続が無い（ABBA 釣り合わせの目的）
        for i in range(len(conds) - 2):
            if conds[i] == conds[i + 1] == conds[i + 2]:
                fails.append(f"{s}: 同条件が 3 連続 -> {conds}")
        # §2.6: 強制比較 7 回、うち異条件ペアが 1 つ以上（分母が空にならない）
        checks = [b for b in a["blocks"] if b["manipulation_check"]]
        if len(checks) != 7:
            fails.append(f"{s}: 強制比較が 7 回でない -> {len(checks)}")
        cross = sum(1 for i in range(1, 8) if conds[i] != conds[i - 1])
        if cross < 1:
            fails.append(f"{s}: 異条件の隣接ペアが 0（操作チェックの分母が空）-> {conds}")
        if any(not blk["material"].startswith("materials/") for blk in a["blocks"]):
            fails.append(f"{s}: 課題文パスが materials/ 配下でない")

    # --pilot: 縮小版が確証デザインと取り違えられない形で出ること
    p = pilot_assign(seed)
    if p["confirmatory"] is not False:
        fails.append("pilot: confirmatory=False が立っていない（確証デザインと誤認されうる）")
    if [b["condition"] for b in p["blocks"]].count("copy") != 2:
        fails.append("pilot: copy ブロックが 2 個でない")
    if sorted(b["condition"] for b in p["blocks"] if b["condition"] != "copy") != ["HI", "LO"]:
        fails.append("pilot: HI / LO が 1 個ずつでない")
    if any(b["manipulation_check"] for b in p["blocks"]):
        fails.append("pilot: 強制比較は縮小版では取らない（比較の鎖が成立しない）")

    # ★ --pilot-topic（G-4）: 題材を変えても順序は変わらず、材料パスだけが変わること
    p2 = pilot_assign(seed, 2)
    if {b["topic_id"] for b in p2["blocks"] if b["condition"] != "copy"} != {"topic02"}:
        fails.append("pilot: --pilot-topic 2 が topic02 を指していない")
    if any(b["material"] != f"materials/{b['topic_id']}_{b['condition'].lower()}.md"
           for b in p2["blocks"] if b["condition"] != "copy"):
        fails.append("pilot: --pilot-topic 2 の課題文パスが題材/条件と一致しない")
    if [b["condition"] for b in p2["blocks"]] != [b["condition"] for b in p["blocks"]]:
        fails.append("pilot: 題材を変えたら条件の順序まで変わった"
                     "（rng_for のキーは 'PILOT' 固定であること = --pilot 単独の後方互換）")
    if p["pilot_topic"] != 1 or p2["pilot_topic"] != 2:
        fails.append("pilot: pilot_topic が割付ファイルに記録されていない"
                     "（どの回がどの題材だったか後から分からなくなる）")
    # ★ 範囲外は黙って通さない（存在しない materials/topicNN を割付表に出さない）
    for bad in (0, N_TOPICS + 1, -1):
        try:
            pilot_assign(seed, bad)
        except ValueError:
            pass
        else:
            fails.append(f"pilot: --pilot-topic {bad} が拒否されない（存在しない課題文を指す）")

    # ★ --pilot-label（G-1）: validate_blocks.py は「ファイル名 == subject」を要求するので、
    #   P-1 を複数回回すなら subject が分かれていなければ割付ファイルを置けない
    if p["subject"] != "PILOT":
        fails.append("pilot: label 未指定なら subject は 'PILOT'（後方互換）")
    labeled = pilot_assign(seed, 2, "mac")
    if labeled["subject"] != "PILOT-mac":
        fails.append(f"pilot: --pilot-label mac の subject が PILOT-mac でない -> {labeled['subject']}")
    if [b["condition"] for b in labeled["blocks"]] != [b["condition"] for b in p["blocks"]]:
        fails.append("pilot: label を付けたら条件の順序まで変わった（rng キーは 'PILOT' 固定であること）")
    for bad_label in ("", "with space", "toolonglabel", "P/015"):
        try:
            pilot_assign(seed, 1, bad_label)
        except ValueError:
            pass
        else:
            fails.append(f"pilot: --pilot-label {bad_label!r} が拒否されない"
                         "（ファイル名になるので英数字に限る）")

    # 決定性: 同じ入力なら同じ出力
    if assign("P015", seed) != per_subject["P015"]:
        fails.append("決定的でない（同じ seed / 被験者で結果が変わる）")

    # §2.7: 配置 A と B で条件が反転している
    a_arr = {s for s, a in per_subject.items() if a["arrangement"] == "A"}
    b_arr = {s for s, a in per_subject.items() if a["arrangement"] == "B"}
    if not a_arr or not b_arr:
        fails.append("配置 A / B のどちらかが 0 人（counterbalance が成立しない）")
    if abs(len(a_arr) - len(b_arr)) > 1:
        fails.append(f"配置の人数が偏っている A={len(a_arr)} B={len(b_arr)}")

    # 被験者が違えば系列も違う（同じ順序を全員に配らない）
    seqs = {tuple(a["condition_sequence_g1"]) for a in per_subject.values()}
    if len(seqs) < 2:
        fails.append("全被験者の条件系列が同一（無作為化が効いていない）")

    if fails:
        print("[NG] selftest 失敗:")
        for f in fails:
            print(f"  - {f}")
        return 1
    print(f"[OK] assign.py selftest 緑 ({len(subjects)} 名分・配置 A={len(a_arr)} B={len(b_arr)})")
    return 0


def main() -> int:
    here = pathlib.Path(__file__).resolve().parent
    ap = argparse.ArgumentParser()
    ap.add_argument("--subject", help="被験者 ID (例: P015)")
    ap.add_argument("--pilot", action="store_true",
                    help="パイロット段階 P-1 の縮小セッション（4 ブロック・確証デザインではない）")
    ap.add_argument("--pilot-label", metavar="LABEL",
                    help="P-1 を複数回回すときの識別子（例: win / mac）。"
                         "被験者 ID が PILOT-<LABEL> になり、割付は blocks/PILOT-<LABEL>.json に置く"
                         "（★ validate_blocks.py はファイル名 == subject を要求する）")
    ap.add_argument("--pilot-topic", type=int, default=1, metavar="N",
                    help=f"P-1 で使う題材番号 1..{N_TOPICS}（既定 1）。"
                         "★ P-1 を 2 回以上回すときは回ごとに変える"
                         "（同じ題材だと 2 回目は内容既知になり打鍵量の測定が歪む）")
    ap.add_argument("--seed-file", default=str(here / "SEED"))
    ap.add_argument("--json", action="store_true", help="機械可読な JSON を出す")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()

    seed = read_seed(pathlib.Path(a.seed_file))
    if a.selftest:
        return selftest(seed)
    # ★ --pilot と --subject の同時指定を黙って優先解決しない（/cross-review 2026-08-03）。
    #   下の分岐は --pilot を先に見るので、--subject の値が**捨てられたことに気づけない**。
    #   このプロジェクトの一貫方針は「黙って無視すると事故になる」である。
    if a.pilot and a.subject:
        ap.error("--pilot と --subject は同時に指定できない。"
                 "P-1（縮小セッション）と確証デザインは別物である（preregistration.md §2.8）")
        return 2
    if a.pilot:
        try:
            result = pilot_assign(seed, a.pilot_topic, a.pilot_label)
        except ValueError as e:
            ap.error(str(e))
            return 2
    elif a.subject:
        # ★ --pilot-topic / --pilot-label は P-1 専用。確証デザインの題材は §2.7 の配置 A/B が
        #   決めるので実験者が選べない。黙って無視すると「指定したのに効かない」事故になる。
        if a.pilot_topic != 1:
            ap.error("--pilot-topic は --pilot と併用する。確証デザインの題材は "
                     "§2.7 の配置 (A/B) が決めるので実験者は選べない")
            return 2
        if a.pilot_label is not None:
            ap.error("--pilot-label は --pilot と併用する（確証標本の被験者 ID は "
                     "Phase1 のロスターが唯一の採番元・protocol.md §2.0）")
            return 2
        result = assign(a.subject, seed)
    else:
        ap.error("--subject / --pilot / --selftest のいずれかが要る")
        return 2
    if a.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(render(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
