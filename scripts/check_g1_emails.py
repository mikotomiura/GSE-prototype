#!/usr/bin/env python3
"""★ G1 の受付メールが `preregistration.md §2.12`（第 7 版）の開示範囲を守っているか検査する。

第 7 版は「**課題の題材（分野）と型を事前の連絡に書かない**」と凍結した
（当日その場で画面提示するので教える必要が無い。§2.13）。
⚠️ ★ 一度は「分野を書く」と決めて第 6 版で実装し、第 7 版で撤回した経緯がある。
   **書き戻されたら赤にする**のがこの検査の役目である。
⚠️ ★ 事前案内メールは 2026-08-03 に廃止した（日時・場所は研究者が手書きで連絡する）。
   検査対象は**受付メール 1 通**である。

### ★ node で実際に関数を呼ぶ

正規表現で「未定義の定数を参照していないか」を見る検査を一度書いて**撤回した**
（文字列リテラルやプロパティアクセスと区別できず誤検出 20 件）。
代わりに **GAS のグローバルをスタブして本文生成関数を実際に呼ぶ**。
これなら `ReferenceError`（実例: `G1_TOPIC_TITLES` の残存参照）を確実に捕まえられ、
誤検出も出ない。⚠️ `node --check` は構文しか見ないので、これの代わりにはならない。

使い方:
    python3 scripts/check_g1_emails.py
"""

from __future__ import annotations

import json
import pathlib
import re
import subprocess
import sys
import tempfile

REPO = pathlib.Path(__file__).resolve().parent.parent
GAS = REPO / "Form_G1" / "GSE_G1_Form_Builder.gs"
MATERIALS = REPO / "experiments" / "20260801-controlled-friction-task" / "materials"

# GAS のグローバルを最小限スタブして、本文生成関数だけを評価する。
HARNESS = r"""
var PropertiesService = { getScriptProperties: function () { return { getProperty: function () { return null; },
  setProperty: function () {} }; } };
var SpreadsheetApp = { openById: function () { throw new Error("not used"); } };
var FormApp = { openById: function () { throw new Error("not used"); },
  ItemType: {}, PageNavigationType: {} };
var Logger = { log: function () {} };
var MailApp = { sendEmail: function () {} };
var GmailApp = { createDraft: function () {} };
var ScriptApp = { getProjectTriggers: function () { return []; } };
var Session = { getScriptTimeZone: function () { return "Asia/Tokyo"; } };
var Utilities = { formatDate: function () { return "2026-01-01"; } };
var UrlFetchApp = { fetch: function () { throw new Error("not used"); } };
__GAS_SOURCE__
// ★ 実際に呼ぶ。未定義参照があればここで ReferenceError になる。
var out = { ackSubject: g1RegisterAckSubject_(), ack: g1RegisterAckBody_("P999") };
var thanks = (function () {
  // sendThankYouEmail は本文を組み立ててから送るので、下書き経路を通して例外が出ないか見る。
  try { G1_CONTACT = G1_CONTACT || "（テスト）"; sendThankYouEmail("P999", "t@example.com"); return "ok"; }
  catch (e) { return "ERROR: " + e.message; }
})();
out.thanks = thanks;
console.log(JSON.stringify(out));
"""


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



def check_consent_question_names() -> list[str]:
    """★ G1-C の設問タイトルが「フォーム構築」と「回答取得」で共有されているか。

    ⚠️ G1-C はそのまま参加登録として使う（提出で P-ID 採番 + 受付メール）。
    設問タイトルを片方だけ変えると、提出されても氏名やメールが取れず
    **黙って発番が止まる**（例外も出ないので気づけない）。
    → 定数 Q_C_* が定義され、buildConsentForm と g1ConsentAnswers_ の両方で
      参照されていることを見る。
    """
    text = GAS.read_text(encoding="utf-8")
    defined = set(re.findall(r"var (Q_C_\w+) = ", text))
    if not defined:
        return ["Q_C_* 定数が無い（設問タイトルがハードコードに戻っている疑い）"]

    def body_of(fn: str) -> str:
        m = re.search(r"^function " + fn + r"\b.*?(?=^function )", text, re.S | re.M)
        return m.group(0) if m else ""

    build = body_of("buildConsentForm")
    parse = body_of("g1ConsentAnswers_")
    if not build or not parse:
        return ["buildConsentForm / g1ConsentAnswers_ が見つからない"]

    out = []
    for c in sorted(defined):
        in_build = c in build
        in_parse = c in parse
        if in_build and not in_parse:
            out.append(f"{c} はフォームには出るが回答取得で使われていない（取りこぼす）")
        if in_parse and not in_build:
            out.append(f"{c} は回答取得で使うがフォームに設問が無い（常に空になる）")
    # ★ 検査が空回りしていないこと: 少なくとも氏名とメールは両方で使われているはず
    for must in ("Q_C_NAME", "Q_C_EMAIL"):
        if must not in defined:
            out.append(f"{must} が定義されていない（採番に必要）")
    return out


def topic_titles() -> list[str]:
    out = []
    for p in sorted(MATERIALS.glob("topic*_lo.md")):
        m = re.search(r"^title:\s*(.+?)\s*$", p.read_text(encoding="utf-8"), re.M)
        if m:
            out.append(m.group(1))
    return out


def run_gas() -> dict:
    src = GAS.read_text(encoding="utf-8")
    with tempfile.TemporaryDirectory() as td:
        js = pathlib.Path(td) / "harness.js"
        js.write_text(HARNESS.replace("__GAS_SOURCE__", src), encoding="utf-8")
        r = subprocess.run(["node", str(js)], capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(
            "[NG] ★ .gs を評価できない（GAS 実行時にも同じエラーになる）\n"
            + (r.stderr.strip()[:1500] or "(stderr なし)")
        )
    return json.loads(r.stdout.strip().splitlines()[-1])


def main() -> int:
    if not GAS.is_file():
        print(f"[NG] {GAS} が無い")
        return 1
    try:
        subprocess.run(["node", "--version"], capture_output=True, check=True)
    except Exception:
        # ⚠️ 外部コマンド不在で黙って緑にしない（silent-failure-in-guard-scripts）。
        print("[NG] node が無いので事前案内メールの検査ができない（飛ばさずに赤にする）")
        return 1

    fails: list[str] = list(check_run_columns()) + list(check_consent_question_names())

    res = run_gas()
    # ★ 事前案内メールと受付メールの**両方**を同じ基準で見る。
    #   片方だけ検査すると、もう片方に題材が書き戻されても緑になる。
    bodies = {"受付メール": res["ack"]}

    if res.get("thanks") != "ok":
        fails.append(f"sendThankYouEmail が失敗する: {res.get('thanks')}")

    # ★ 本命: 題材名が本文に載っていないこと（第 7 版 §2.12）
    for label, b in bodies.items():
        for t in topic_titles():
            if t in b:
                fails.append(f'題材名 "{t}" が{label}に載っている（§2.12 は開示しないと凍結）')

    # ★ 課題の型も開示しない
    for label, b in bodies.items():
        for token in ("資料が 1 本", "資料が 3 本", "資料 1 本の要約", "資料 3 本の統合", "統合"):
            if token in b:
                fails.append(f'課題の型を示す表現 "{token}" が{label}にある（§2.12）')

    # ★ 条件名・構成概念
    for label, b in bodies.items():
        for token in ("HI", "LO", "摩擦", "仮説", "判定基準"):
            if token in b:
                fails.append(f'"{token}" が{label}にある（§2.12 / protocol.md §4.3）')

    # ★ 検査が空回りしていないこと: 本文がちゃんと生成されている
    for label, b in bodies.items():
        if len(b) < 200:
            fails.append(f"{label}の本文が短すぎる（{len(b)} 文字）。生成に失敗している疑い")
        for must in ("参加者ID", "5 分", "300〜400 字", "書き写し"):
            if must not in b:
                fails.append(f'{label}に必要な案内 "{must}" が無い')

    if fails:
        print("[NG] 受付メールが §2.12 の開示範囲から外れている")
        for f in fails:
            print(f"  - {f}")
        return 1
    print("[OK] 受付メールは §2.12（第 7 版）の開示範囲を守っている")
    print("     G1 実施トラッキングの列参照・G1-C の設問名も一致している")
    print(f"     題材名 {len(topic_titles())} 件・課題の型・条件名のいずれも本文に無い")
    return 0


if __name__ == "__main__":
    sys.exit(main())
