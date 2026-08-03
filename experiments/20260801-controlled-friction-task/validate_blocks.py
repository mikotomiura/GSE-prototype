#!/usr/bin/env python3
"""★ 割付ファイル（`blocks/P0xx.json`）の**転記ミスだけ**を検出する。

なぜ要るか（`.steering/20260803-g1-pilot-readiness/design.md`）:
  `protocol.md §1` は「1 ブロック = 1 セッション」を選んだ決め手を **失敗の可視性** に置いた——

      (b) の失敗は沈黙して間違った結果を出すが、(a) の失敗はファイルが無いという形で必ず露見する。

  ところが**その思想が転記工程に及んでいなかった**。課題文には `validate_materials.py` があるのに、
  割付表 → 記録用紙 → `blocks/P0xx.json` の経路には検証が 1 つも無く、`analyze.py` は
  「不正な被験者を解析から外す」程度で**転記ミスを積極的に捕まえない**。本スクリプトはその穴を塞ぐ。

★ **このスクリプトは判定に一切関与しない。**
  - 除外しない・しきい値を持たない・被験者を落とさない（`preregistration.md §2.9 / §3.6` に触れない）
  - 適格性ゲート（≥100 打鍵）も分離の判定も `analyze.py` の責務であり、こちらは触らない
  - ★ **条件ラベル（HI / LO）を画面に出さない**。P-1 は研究者本人が被験者であり、
    検証のたびに条件が見えると盲検が更に崩れる。不一致は「ブロック 5 が割付と違う」とだけ言う
  - ★ **NDJSON のファイル名を出力しない**（名前にセッション日時が入る・`blocks/README.md`）

使い方:
    python3 validate_blocks.py                          # blocks/ を全件検査
    python3 validate_blocks.py --dataset ~/gse-dataset  # NDJSON の実在と probe 行 0 も検査
    python3 validate_blocks.py --selftest               # 自己検証

依存は標準ライブラリのみ（`analyze.py` と同じ方針）。
"""
from __future__ import annotations

import argparse
import contextlib
import io
import json
import pathlib
import sys
import tempfile

import assign

# §2.3: ブロック構成。copy は先頭・末尾に位置固定。
N_BLOCKS_CONFIRMATORY = 10
COPY_BLOCKS = (1, 10)
N_HI = N_LO = 4
# §2.6: 強制比較は G1 ブロック 3〜9 の直後のみ（計 7 回）。
MCHECK_BLOCKS = tuple(range(3, 10))

# §2.2 / §4.3: 課題文が要求する産出量。★ これは**判定基準ではない**（`§3` は打鍵のみ）。
REQUESTED_CHARS = (300, 400)
# ★ 転記ミスの疑いを立てる幅。産出が少ない/多いこと自体は正常でありうるので、
#   ここは「人が書いた 5 分ぶんの文字数として桁が違う」水準に置く（例: 35 と 350 の取り違え）。
PLAUSIBLE_CHARS = (150, 800)

# ★ B-1（`preregistration.md §2.6`）の客観検証。G1 のログにこれらの行があってはならない。
FORBIDDEN_LINE_TYPES = ("probe_assignment", "probe_triggered", "realtime_label")


class Report:
    """FAIL / WARN / NOTE を貯めて最後にまとめて出す（1 件目で止めない）。"""

    def __init__(self) -> None:
        self.fails: list[str] = []
        self.warns: list[str] = []
        self.notes: list[str] = []

    def fail(self, msg: str) -> None:
        self.fails.append(msg)

    def warn(self, msg: str) -> None:
        self.warns.append(msg)

    def note(self, msg: str) -> None:
        self.notes.append(msg)

    def merge(self, other: "Report") -> None:
        self.fails += other.fails
        self.warns += other.warns
        self.notes += other.notes

    @property
    def ok(self) -> bool:
        return not self.fails


# ---------------------------------------------------------------------------
# 1. 構成（§2.3）
# ---------------------------------------------------------------------------
def check_structure(spec: dict, r: Report) -> None:
    subject = spec.get("subject", "?")
    blocks = spec.get("blocks")
    if not isinstance(blocks, list) or not blocks:
        r.fail(f"{subject}: blocks が無い/空")
        return

    numbers = [b.get("block") for b in blocks]
    if spec.get("confirmatory") is False:
        # パイロット P-1（§2.8）: 4 ブロック・copy / G1 / G1 / copy。判定も操作チェックも無い。
        if numbers != [1, 2, 3, 4]:
            r.fail(f"{subject}: パイロット P-1 のブロック番号は 1..4 であること (実際: {numbers})")
        return

    if numbers != list(range(1, N_BLOCKS_CONFIRMATORY + 1)):
        r.fail(f"{subject}: ブロック番号は 1..{N_BLOCKS_CONFIRMATORY} が過不足なく並ぶこと "
               f"(実際: {numbers})")
        return

    by_no = {b["block"]: b for b in blocks}
    for n in COPY_BLOCKS:
        if by_no[n].get("condition") != "copy":
            r.fail(f"{subject}: ブロック {n} は copy でなければならない (§2.3・位置固定)")
    g1 = [by_no[n].get("condition") for n in range(2, 10)]
    if g1.count("HI") != N_HI or g1.count("LO") != N_LO:
        # ★ 個々の条件は出さない。数だけ言う（HI/LO の並びが見えると盲検が崩れる）。
        r.fail(f"{subject}: G1 の 8 ブロックは HI {N_HI} / LO {N_LO} でなければならない "
               f"(実際: HI {g1.count('HI')} / LO {g1.count('LO')})。"
               f"C(8,4)=70 という並べ替えの前提が壊れる (§2.3)")


# ---------------------------------------------------------------------------
# 2. 割付との一致（★ assign.py から再生成して突き合わせる）
# ---------------------------------------------------------------------------
def check_against_assignment(spec: dict, seed: int, r: Report) -> None:
    """★ 記録用紙経由の転記が `assign.py` の決定的出力と一致するかを検査する。

    `protocol.md §2.3-1` は「転記は 1 方向だけ（`assign.py` → 記録用紙）」と定めている。
    ここでは**逆方向に再構成するのではなく、同じ入力から再生成して突き合わせる**。
    """
    subject = spec.get("subject", "?")
    if spec.get("confirmatory") is False:
        # P-1 は題材 1 本を両条件で出す既知の逸脱（§2.8）。順序は seed 由来なので再生成で照合できる。
        try:
            topic = int(str(spec["blocks"][1].get("topic_id", "topic01")).removeprefix("topic"))
        except (ValueError, KeyError, IndexError):
            r.fail(f"{subject}: パイロットの題材 ID が読めない")
            return
        expected = assign.pilot_assign(seed, topic=topic)
    else:
        if spec.get("seed") != seed:
            r.fail(f"{subject}: 割付ファイルの seed が SEED と違う "
                   f"(ファイル={spec.get('seed')} / SEED={seed})。"
                   f"別の seed で作った割付表を転記した可能性がある")
            return
        try:
            expected = assign.assign(subject, seed)
        except SystemExit as e:
            r.fail(f"{subject}: 割付を再生成できない ({e})")
            return
        if spec.get("arrangement") != expected["arrangement"]:
            r.fail(f"{subject}: 配置 (A/B) が割付と違う。配置は被験者番号から決まり実験者は選べない (§2.7)")

    exp_by_no = {b["block"]: b for b in expected["blocks"]}
    for b in spec["blocks"]:
        n = b.get("block")
        e = exp_by_no.get(n)
        if e is None:
            continue
        # ★ 値は出さない。どの列が食い違ったかだけを言う（HI/LO・課題文名が見えると盲検が崩れる）。
        for key, label in (("condition", "条件"), ("topic_id", "題材 ID"), ("material", "課題文")):
            if b.get(key) != e[key]:
                r.fail(f"{subject}: ブロック {n} の{label}が割付と一致しない。"
                       f"`python3 assign.py --subject {subject}` を再生成して転記し直すこと")
        if b.get("manipulation_check") != e["manipulation_check"]:
            r.fail(f"{subject}: ブロック {n} の manipulation_check フラグが割付と一致しない (§2.6)")


# ---------------------------------------------------------------------------
# 3. NDJSON ファイル名（重複・欠落）
# ---------------------------------------------------------------------------
def check_files(spec: dict, seen: dict[str, str], r: Report) -> None:
    subject = spec.get("subject", "?")
    local: dict[str, int] = {}
    for b in spec["blocks"]:
        n = b.get("block")
        f = b.get("file")
        if not f:
            r.fail(f"{subject}: ブロック {n} に file が無い。記録用紙の NDJSON 名を書き足すこと "
                   f"(protocol.md §2.2)")
            continue
        if not isinstance(f, str) or not f.endswith(".ndjson"):
            r.fail(f"{subject}: ブロック {n} の file が NDJSON 名の形をしていない")
            continue
        if f in local:
            # ★ 名前そのものは出さない（セッション日時が入る）。ブロック番号だけで指す。
            r.fail(f"{subject}: ブロック {n} と {local[f]} が**同じ NDJSON** を指している。"
                   f"1 ブロック = 1 セッション (protocol.md §1) に反する")
        else:
            local[f] = n
        owner = seen.get(f)
        if owner is not None and owner != subject:
            r.fail(f"{subject}: ブロック {n} の NDJSON が {owner} でも使われている (被験者間の取り違え)")
        seen[f] = subject


# ---------------------------------------------------------------------------
# 4. 操作チェックの回答（§2.6）
# ---------------------------------------------------------------------------
def check_manipulation_answers(spec: dict, r: Report) -> None:
    subject = spec.get("subject", "?")
    answers = spec.get("manipulation_check_answers")

    if spec.get("confirmatory") is False:
        # ★ §2.8: P-1 では強制比較の鎖が成立しないので**取らない**。あったら転記の取り違えである。
        if answers:
            r.fail(f"{subject}: パイロット P-1 に manipulation_check_answers がある。"
                   f"§2.8 は「HI/LO の対が 1 組しかないので操作チェックを取らない」と定めている")
        return

    if answers is None:
        r.note(f"{subject}: manipulation_check_answers が未記入 "
               f"(実施後に 7 件書き足す。`forms_to_blocks.py` が自動生成する)")
        return
    if not isinstance(answers, list):
        r.fail(f"{subject}: manipulation_check_answers がリストでない")
        return

    got = [a.get("block") for a in answers]
    if got != list(MCHECK_BLOCKS):
        r.fail(f"{subject}: 強制比較はブロック {MCHECK_BLOCKS[0]}〜{MCHECK_BLOCKS[-1]} の "
               f"{len(MCHECK_BLOCKS)} 件（順序どおり）であること (§2.6・実際: {got})")

    by_no = {b["block"]: b for b in spec["blocks"]}
    for a in answers:
        n, harder = a.get("block"), a.get("harder")
        if n not in by_no:
            r.fail(f"{subject}: 強制比較の block={n} が割付に無い")
            continue
        # ★ 強制比較は「直前のブロック」と「その 1 つ前」の二択（§2.6・protocol.md §3.1）。
        if harder not in (n - 1, n):
            r.fail(f"{subject}: ブロック {n} の強制比較の回答が二択の外にある "
                   f"(harder は {n - 1} か {n} のいずれか・実際: {harder})")
        if by_no.get(n - 1, {}).get("condition") == "copy":
            r.fail(f"{subject}: ブロック {n} の強制比較が copy ブロックと比較されている。"
                   f"§2.6 は「copy には聞かない・鎖は G1 の 8 ブロック内で閉じる」と定めている")


# ---------------------------------------------------------------------------
# 5. 産出文字数（★ 警告のみ。除外しない）
# ---------------------------------------------------------------------------
def check_produced_chars(spec: dict, r: Report) -> None:
    subject = spec.get("subject", "?")
    for b in spec["blocks"]:
        n, v = b.get("block"), b.get("produced_chars")
        if v is None:
            r.note(f"{subject}: ブロック {n} の produced_chars が未記入 "
                   f"(§3.5 の報告義務。記入パッドの文字数を書き写す)")
            continue
        if not isinstance(v, int) or isinstance(v, bool) or v < 0:
            r.fail(f"{subject}: ブロック {n} の produced_chars が非負整数でない (実際: {v!r})")
            continue
        if b.get("condition") == "copy":
            continue  # copy は「5 分で書ける分だけ」なので範囲の概念が無い（§4.3）
        lo, hi = PLAUSIBLE_CHARS
        if not (lo <= v <= hi):
            # ★ WARN であって除外ではない。§3.6 は「ブロックを事後に除外しない」と凍結している。
            r.warn(f"{subject}: ブロック {n} の produced_chars={v} は "
                   f"5 分の産出として桁が外れている。**転記ミスを疑う**（除外はしない・§3.6）")
        elif not (REQUESTED_CHARS[0] <= v <= REQUESTED_CHARS[1]):
            r.note(f"{subject}: ブロック {n} の produced_chars={v} は課題の要求 "
                   f"{REQUESTED_CHARS[0]}〜{REQUESTED_CHARS[1]} 字の外（正常でありうる。§3.5 で報告する）")


# ---------------------------------------------------------------------------
# 6. NDJSON 側（--dataset 指定時のみ）
# ---------------------------------------------------------------------------
def scan_ndjson(path: pathlib.Path) -> dict[str, int]:
    """行種別ごとの件数を数える。★ 中身（打鍵の内容・時刻）は一切見ない。"""
    counts: dict[str, int] = {}
    with path.open(encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if not line.strip():
                continue
            try:
                t = json.loads(line).get("type")
            except Exception:
                counts["_malformed"] = counts.get("_malformed", 0) + 1
                continue
            if isinstance(t, str):
                counts[t] = counts.get(t, 0) + 1
    return counts


def check_dataset(spec: dict, dataset: pathlib.Path, r: Report) -> None:
    subject = spec.get("subject", "?")
    for b in spec["blocks"]:
        n, f = b.get("block"), b.get("file")
        if not f:
            continue
        p = dataset / "raw" / subject / f
        if not p.is_file():
            r.fail(f"{subject}: ブロック {n} の NDJSON が dataset に無い "
                   f"({dataset}/raw/{subject}/ を確認する)")
            continue
        counts = scan_ndjson(p)
        # ★ B-1 の客観検証（`preregistration.md §2.6 / §5.4`）。
        #   env フラグを立て忘れると**ここで必ず露見する**。自己申告に頼らない。
        for t in FORBIDDEN_LINE_TYPES:
            if counts.get(t, 0):
                r.fail(f"{subject}: ブロック {n} に {t} 行が {counts[t]} 件ある。"
                       f"§2.6 は「アプリ内プローブを使わない」と凍結している。"
                       f"GSE_DISABLE_PROBES=1 を立てずに実施した疑いがある")
        if counts.get("_malformed"):
            r.warn(f"{subject}: ブロック {n} に壊れた行が {counts['_malformed']} 件ある")
        # ★ INFO: FS-B の可用性（§5.1）。ime_shadow が 0 なら ime_dwell_med が定数になる。
        r.note(f"{subject}: ブロック {n}  key={counts.get('key', 0)} "
               f"feat={counts.get('feat', 0)} ime_shadow={counts.get('ime_shadow', 0)} "
               f"paste={counts.get('paste', 0)}")


# ---------------------------------------------------------------------------
# 実行
# ---------------------------------------------------------------------------
def validate_spec(spec: dict, seed: int, seen: dict[str, str],
                  dataset: pathlib.Path | None) -> Report:
    r = Report()
    subject = spec.get("subject")
    if not isinstance(subject, str) or not subject:
        r.fail("subject が無い")
        return r
    check_structure(spec, r)
    if not r.ok:
        return r  # 構成が壊れているなら以降の照合は意味を持たない
    check_against_assignment(spec, seed, r)
    check_files(spec, seen, r)
    check_manipulation_answers(spec, r)
    check_produced_chars(spec, r)
    if dataset is not None:
        check_dataset(spec, dataset, r)
    return r


def run(blocks_dir: pathlib.Path, seed: int, dataset: pathlib.Path | None) -> int:
    paths = sorted(p for p in blocks_dir.glob("*.json"))
    print(f"[blocks] {blocks_dir}")
    if not paths:
        print("  [note] 割付ファイルが 1 件も無い = **まだデータを取っていない**（事前登録どおり）")
        print("  [note] 実施後: python3 assign.py --subject P0xx --json > blocks/P0xx.json")
        return 0

    total = Report()
    seen: dict[str, str] = {}
    for p in paths:
        try:
            spec = json.loads(p.read_text(encoding="utf-8"))
        except Exception as e:
            total.fail(f"{p.name}: JSON として読めない ({e})")
            continue
        if spec.get("subject") != p.stem:
            total.fail(f"{p.name}: ファイル名と subject が一致しない (subject={spec.get('subject')!r})")
        total.merge(validate_spec(spec, seed, seen, dataset))

    print(f"  {len(paths)} 件を検査した")
    for m in total.notes:
        print(f"  [note] {m}")
    for m in total.warns:
        print(f"  [WARN] {m}")
    for m in total.fails:
        print(f"  [FAIL] {m}")
    print()
    if total.fails:
        print(f"[NG] 転記ミスの疑い {len(total.fails)} 件。★ 割付表から転記し直すこと。")
        print("     ⚠️ これは**除外の判断ではない**。ブロックも被験者も落とさない (§3.6)。")
        return 1
    print(f"[OK] 転記の整合性に問題なし（警告 {len(total.warns)} 件）")
    return 0


# ---------------------------------------------------------------------------
# 自己検証
# ---------------------------------------------------------------------------
def _write(dirpath: pathlib.Path, spec: dict) -> None:
    (dirpath / f"{spec['subject']}.json").write_text(
        json.dumps(spec, ensure_ascii=False), encoding="utf-8")


def _good_spec(seed: int, subject: str = "P015") -> dict:
    spec = assign.assign(subject, seed)
    for i, b in enumerate(spec["blocks"], start=1):
        b["file"] = f"{subject}_session_{i:02d}.ndjson"
        b["produced_chars"] = 120 if b["condition"] == "copy" else 350
    by_no = {b["block"]: b for b in spec["blocks"]}
    # 「直前のほうが詰まった」を一貫して選んだ回答（内容は検査対象でない・形だけ使う）
    spec["manipulation_check_answers"] = [{"block": n, "harder": n} for n in MCHECK_BLOCKS]
    assert by_no[1]["condition"] == "copy"
    return spec


def selftest() -> int:
    here = pathlib.Path(__file__).resolve().parent
    seed = assign.read_seed(here / "SEED")
    fails: list[str] = []

    def case(name: str, mutate, expect_fail: bool) -> None:
        spec = _good_spec(seed)
        mutate(spec)
        r = validate_spec(spec, seed, {}, None)
        if r.ok == expect_fail:
            fails.append(f"{name}: 期待 {'FAIL' if expect_fail else 'PASS'} だが "
                         f"{'PASS' if r.ok else 'FAIL: ' + r.fails[0]}")

    case("正常系", lambda s: None, expect_fail=False)
    case("ブロック欠落", lambda s: s["blocks"].pop(), expect_fail=True)
    case("copy 位置ずれ", lambda s: s["blocks"][0].update(condition="HI"), expect_fail=True)
    case("条件の取り違え",
         lambda s: s["blocks"][1].update(condition=("LO" if s["blocks"][1]["condition"] == "HI" else "HI")),
         expect_fail=True)
    case("題材の取り違え", lambda s: s["blocks"][2].update(topic_id="topic99"), expect_fail=True)
    case("課題文パスの取り違え", lambda s: s["blocks"][3].update(material="materials/copy.md"),
         expect_fail=True)
    case("配置の取り違え", lambda s: s.update(arrangement=("B" if s["arrangement"] == "A" else "A")),
         expect_fail=True)
    case("seed 違い", lambda s: s.update(seed=s["seed"] + 1), expect_fail=True)
    case("NDJSON 名の重複",
         lambda s: s["blocks"][2].update(file=s["blocks"][1]["file"]), expect_fail=True)
    case("NDJSON 名の欠落", lambda s: s["blocks"][4].pop("file"), expect_fail=True)
    case("強制比較が 6 件", lambda s: s["manipulation_check_answers"].pop(), expect_fail=True)
    case("強制比較が二択の外",
         lambda s: s["manipulation_check_answers"][0].update(harder=1), expect_fail=True)
    case("produced_chars が非整数", lambda s: s["blocks"][1].update(produced_chars="350"),
         expect_fail=True)

    # ★ WARN は FAIL にしない（除外の判断をしないことの回帰テスト・§3.6）
    spec = _good_spec(seed)
    spec["blocks"][1]["produced_chars"] = 12
    r = validate_spec(spec, seed, {}, None)
    if not r.ok or not r.warns:
        fails.append("桁外れの produced_chars は WARN であって FAIL ではないこと (§3.6)")

    # ★ 未記入は NOTE（実施前の状態を赤にしない）
    spec = _good_spec(seed)
    for b in spec["blocks"]:
        b.pop("produced_chars", None)
    spec.pop("manipulation_check_answers")
    r = validate_spec(spec, seed, {}, None)
    if not r.ok:
        fails.append("未記入 (produced_chars / 操作チェック) は FAIL にしないこと")

    # ★ パイロット P-1 は 4 ブロック・操作チェック無しが正
    pilot = assign.pilot_assign(seed)
    for i, b in enumerate(pilot["blocks"], start=1):
        b["file"] = f"PILOT_session_{i:02d}.ndjson"
    r = validate_spec(pilot, seed, {}, None)
    if not r.ok:
        fails.append(f"パイロット P-1 の正常系が FAIL になった: {r.fails[0]}")
    pilot["manipulation_check_answers"] = [{"block": 3, "harder": 3}]
    r = validate_spec(pilot, seed, {}, None)
    if r.ok:
        fails.append("パイロットに操作チェック回答があれば FAIL にすること (§2.8)")

    # ★ 被験者間で同じ NDJSON を指したら FAIL
    with tempfile.TemporaryDirectory() as td:
        d = pathlib.Path(td)
        a, b = _good_spec(seed, "P015"), _good_spec(seed, "P016")
        b["blocks"][0]["file"] = a["blocks"][0]["file"]
        _write(d, a)
        _write(d, b)
        # run() は人向けに印字するので、selftest の出力に混ぜない（緑の中に [NG] が出ると紛らわしい）。
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = run(d, seed, None)
        if rc == 0:
            fails.append("被験者間で NDJSON 名が重複したら NG を返すこと")

    # ★ 禁止行（プローブ）の検出 — B-1 の客観検証
    with tempfile.TemporaryDirectory() as td:
        d = pathlib.Path(td)
        spec = _good_spec(seed)
        raw = d / "raw" / spec["subject"]
        raw.mkdir(parents=True)
        for blk in spec["blocks"]:
            (raw / blk["file"]).write_text('{"type":"key","t":1,"press":true}\n', encoding="utf-8")
        r = validate_spec(spec, seed, {}, d)
        if not r.ok:
            fails.append(f"probe 行が無いログを FAIL にしてはならない: {r.fails[0]}")
        (raw / spec["blocks"][3]["file"]).write_text(
            '{"type":"key","t":1,"press":true}\n{"type":"probe_assignment","probe_id":"x"}\n',
            encoding="utf-8")
        r = validate_spec(spec, seed, {}, d)
        if r.ok or not any("probe_assignment" in m for m in r.fails):
            fails.append("probe_assignment 行があれば FAIL にすること (§2.6 / B-1)")

    if fails:
        print("[NG] validate_blocks.py --selftest 失敗:")
        for f in fails:
            print(f"  - {f}")
        return 1
    print("[OK] validate_blocks.py --selftest 緑")
    return 0


def main() -> int:
    here = pathlib.Path(__file__).resolve().parent
    ap = argparse.ArgumentParser()
    ap.add_argument("--blocks-dir", default=str(here / "blocks"))
    ap.add_argument("--seed-file", default=str(here / "SEED"))
    ap.add_argument("--dataset", default=None,
                    help="指定すると NDJSON の実在と probe 行 0 も検査する (例: ~/gse-dataset)")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()

    if a.selftest:
        return selftest()

    seed = assign.read_seed(pathlib.Path(a.seed_file))
    dataset = pathlib.Path(a.dataset).expanduser() if a.dataset else None
    if dataset is not None and not dataset.is_dir():
        print(f"[NG] dataset が無い: {dataset}")
        return 1
    return run(pathlib.Path(a.blocks_dir), seed, dataset)


if __name__ == "__main__":
    sys.exit(main())
