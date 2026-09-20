#!/usr/bin/env python3
"""★ G1 のメールが `preregistration.md §2.12`（第 11 版）を守っているか検査する。

⚠️ ★ **第 11 版で事前開示を撤回した（2026-08-08）。** 課題は事前に読むものではなく、
   **当日その場で取り掛かるもの**である。課題ページはゲート付きで、
   「課題を表示して始める」を押すまで中身が出ない。
   → メールは (1) 撤回後の文言であること、(2) ゲートの言い方をしていること、の両方を要求する。
   ⚠️ ★ **撤回は抑止であって保証ではない**（押せば読める）。だから §2.12-3 / -4 / -6 は残る。

★ 撤回後も **メール本文** には次を書かない（第 7/8 版から不変）:
   - 題材名 … ★ 並べた順序が **提示順**（§2.12 が伏せると宣言した項目）を示唆しうる
   - 課題の型 / 条件名（HI / LO）/ 難易度の示唆 / 仮説 / 判定基準 / 「摩擦」

⚠️ ★ 検査対象は **3 本**である: 受付メールの 2 分岐（課題ページが用意済み / 未用意）と
   課題ページメール。⚠️ ★ 2026-08-08 まで **受付メールは未用意側しか呼んでいなかった**ので、
   被験者が実際に受け取る本文はこの検査を一度も通っていなかった。
   片方だけ見ると、もう片方に書き戻されても緑になる（第 7 版で実際にそう設計した理由）。

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
import os
import pathlib
import re
import subprocess
import sys
import tempfile

REPO = pathlib.Path(__file__).resolve().parent.parent
# ★ 検査対象は通常 repo の .gs である。⚠️ `G1_GAS_PATH` で差し替えられるのは
#   **この検査自体が空回りしていないか**を試すため（scripts/tests/test_check_g1_emails.py が、
#   コピーを壊して「赤くなること」を確かめる）。★ 本番の実行では設定しない。
GAS = pathlib.Path(os.environ.get("G1_GAS_PATH") or REPO / "Form_G1" / "GSE_G1_Form_Builder.gs")
MATERIALS = REPO / "experiments" / "20260801-controlled-friction-task" / "materials"

# GAS のグローバルを最小限スタブして、本文生成関数だけを評価する。
HARNESS = r"""
// ★★ 2026-08-08: 短縮 URL の**両方の分岐**を試せるようにする。
//   ⚠️ 既定は null（＝短縮なし＝生の URL に落ちる側）。__MODE__ が "1" のときだけ
//      SHORTURL_* に短縮を返す。★ 片方だけ試すと、もう片方が壊れても緑になる。
//   ★★ 2026-08-08 追加: フォームの回答 URL は **3 段**に落ちる（g1FormLink_）。
//      短縮 → publishedUrl → フォーム ID から組み立て。⚠️ ★ 3 段あるなら 3 段とも試す。
//      "2" = publishedUrl だけがある状態（＝短縮をまだ作っていない実運用の初期状態）。
var __MODE__ = "__SHORTMODE__";
var PropertiesService = { getScriptProperties: function () { return {
  getProperty: function (k) {
    k = String(k);
    // ★ キーごとに違う値を返す（同じ値だと M と S の取り違えを検査できない）。
    if (__MODE__ === "1" && k.indexOf("SHORTURL_") === 0) {
      return "https://x.gd/SHORT-" + k.slice("SHORTURL_".length);
    }
    if (__MODE__ === "2" && k.indexOf("FORMURL_") === 0) {
      return JSON.stringify({
        publishedUrl: "https://docs.google.com/forms/d/e/PUBLISHED-" +
          k.slice("FORMURL_".length) + "/viewform",
        editUrl: "", title: "", label: "",
      });
    }
    return null;
  },
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
// ⚠️★ 受付メールには**分岐が 2 本ある**（課題ページが用意済みか否か）。2026-08-08 まで
//    ここは未用意側しか呼んでおらず、★ **被験者が実際に受け取る側**（用意済み）の本文は
//    この検査を一度も通っていなかった。→ 両方を同じ基準で見る。
out.ackWithMaterials = g1RegisterAckBody_("P999", "https://example.com/folder");
// ★★ 課題ページのメール。⚠️ 受付メールと**同じ基準**で見る。
//    片方だけ検査すると、もう片方に題材名が書き戻されても緑になる（第 7 版の教訓）。
out.materialsSubject = g1MaterialsSubject_();
out.materials = g1MaterialsBody_("P999", "https://example.com/x");
// ⚠️★★★ **被験者に実際に届く形**（`g1PlainBody_` を通したもの）を測る（2026-09-01）。
//   ★ MailApp は text/plain なので、`**強調**` は装飾にならず記号のまま見える。
//   ⚠️ 生の本文だけを検査していたので、この欠陥は 34〜44 個あっても緑のままだった。
out.ackSent = g1PlainBody_(out.ack);
out.ackWithMaterialsSent = g1PlainBody_(out.ackWithMaterials);
out.materialsSent = g1PlainBody_(out.materials);
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
    out = [
        f'列 "{r}" の参照が RUN_HEADER に無い（列名を変えたら参照側も直す）'
        for r in sorted(set(referenced))
        if r not in headers
    ]

    # ★★ 2026-08-08: 移行表と列幅も**ヘッダ名で引く**ので、同じ落とし穴がある。
    #   ⚠️ 綴りがずれても例外は出ない。★ 「静かに何もしない」だけである
    #      （列幅なら見た目が崩れるだけだが、移行表なら**列が直らないまま緑**になる）。
    for name, pattern in (
        ("列幅 (styleRunTab_ の WIDTHS)", r"var\s+WIDTHS\s*=\s*\{(.*?)\}\s*;"),
        ("移行の改名 (RUN_MIGRATION_RENAMES)", r"var\s+RUN_MIGRATION_RENAMES\s*=\s*\[(.*?)\]\s*;"),
        ("移行の追加 (RUN_MIGRATION_ADDS)", r"var\s+RUN_MIGRATION_ADDS\s*=\s*\[(.*?)\]\s*;"),
        ("移行の値 (RUN_MIGRATION_VALUES)", r"var\s+RUN_MIGRATION_VALUES\s*=\s*\[(.*?)\]\s*;"),
    ):
        m2 = re.search(pattern, text, re.S)
        if not m2:
            out.append(f"{name} が見つからない（検査が空回りしている疑い）")
            continue
        block = m2.group(1)
        if name.startswith("列幅"):
            # WIDTHS はすべて実在の列であること（★ 逆に、全列に幅があることも見る）
            keys = re.findall(r'"([^"]+)"\s*:', block)
            out += [f'列幅 "{k}" が RUN_HEADER に無い（改名の取り残し）' for k in keys if k not in headers]
            out += [f'列 "{h}" の幅が WIDTHS に無い（新しい列を足したら幅も足す）'
                    for h in headers if h not in keys]
        elif "改名" in name:
            # ★ 改名の **右側**（新しい名前）は RUN_HEADER に在るはず。左側（旧名）は在ってはならない。
            for old, new in re.findall(r'\[\s*"([^"]+)"\s*,\s*"([^"]+)"\s*\]', block):
                if new not in headers:
                    out.append(f'移行の改名先 "{new}" が RUN_HEADER に無い')
                if old in headers:
                    out.append(f'移行の改名元 "{old}" が RUN_HEADER に残っている（改名し忘れ）')
        else:
            for k in re.findall(r'(?:name|col|after)\s*:\s*"([^"]+)"', block):
                if k not in headers:
                    out.append(f'{name} が参照する列 "{k}" が RUN_HEADER に無い')

    # ★ 削除した列が、コードのどこかで参照されたまま残っていないか。
    m3 = re.search(r"var\s+RUN_MIGRATION_DROPS\s*=\s*\[(.*?)\]\s*;", text, re.S)
    if not m3:
        out.append("移行の削除 (RUN_MIGRATION_DROPS) が見つからない（検査が空回りしている疑い）")
    else:
        for dropped in re.findall(r'"([^"]+)"', m3.group(1)):
            if dropped in headers:
                out.append(f'削除したはずの列 "{dropped}" が RUN_HEADER に残っている')
            if f'runCol_("{dropped}")' in text:
                out.append(f'削除した列 "{dropped}" を runCol_ が参照している（実行時に例外になる）')
    return out



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


def gas_constants(*names: str) -> dict[str, str]:
    """★ .gs の `var NAME = "…";` を読む（検査側にハードコードを増やさないため）。"""
    text = GAS.read_text(encoding="utf-8")
    out = {}
    for n in names:
        m = re.search(r"var\s+" + re.escape(n) + r'\s*=\s*"([^"]+)"', text)
        if m:
            out[n] = m.group(1)
    return out


def run_gas(short_mode: str = "0") -> dict:
    src = GAS.read_text(encoding="utf-8")
    with tempfile.TemporaryDirectory() as td:
        js = pathlib.Path(td) / "harness.js"
        js.write_text(
            HARNESS.replace("__GAS_SOURCE__", src).replace("__SHORTMODE__", short_mode),
            encoding="utf-8",
        )
        # ⚠️★ `encoding="utf-8"` を明示する（2026-09-20 実測）。★ `text=True` だけだと
        #   **実行環境の既定エンコーディング**でデコードするので、Windows（cp932）では
        #   node が出す日本語のメール本文で `UnicodeDecodeError` が読み取りスレッド内で起き、
        #   ⚠️ `r.stdout` が `None` のまま返って `AttributeError` でスクリプトごと落ちる。
        #   → ★ 上位の `run.sh` には **`[FAIL] 受付メールが §2.12 の開示範囲から外れている`**
        #     と出る（⚠️ **開示範囲は正しいのに赤くなる**）。
        r = subprocess.run(["node", str(js)], capture_output=True, encoding="utf-8")
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
        print("[NG] node が無いのでメール本文の検査ができない（飛ばさずに赤にする）")
        return 1

    fails: list[str] = list(check_run_columns()) + list(check_consent_question_names())

    res = run_gas()
    # ★ 受付メールと事前資料メールの**両方**を同じ基準で見る（§2.12 第 8 版）。
    #   ⚠️ 片方だけ検査すると、もう片方に題材が書き戻されても緑になる。
    bodies = {
        "受付メール(未用意)": res["ack"],
        "受付メール(用意済み)": res["ackWithMaterials"],
        "課題ページメール": res["materials"],
    }

    if res.get("thanks") != "ok":
        fails.append(f"sendThankYouEmail が失敗する: {res.get('thanks')}")

    # ★ 本命: 題材名が**メール本文**に載っていないこと。
    #   ⚠️ ★ 第 8 版で課題文そのものは事前開示に変わったが、**開示はリンク先**で行う。
    #      メール本文に題材名を並べると、並べた順序が **提示順**を示唆しうる。
    #      §2.12（第 8 版）は提示順を「開示しない」側に残しているので、この検査は**維持する**。
    for label, b in bodies.items():
        for t in topic_titles():
            if t in b:
                fails.append(f'題材名 "{t}" が{label}に載っている（§2.12 は開示しないと凍結）')

    # ★ 課題の型もメール本文には書かない（同上・リンク先で読ませる）
    for label, b in bodies.items():
        for token in ("資料が 1 本", "資料が 3 本", "資料 1 本の要約", "資料 3 本の統合", "統合"):
            if token in b:
                fails.append(f'課題の型を示す表現 "{token}" が{label}にある（§2.12）')

    # ★ 条件名・構成概念
    # ⚠️★ 2026-08-08: "HI" / "LO" は **2 文字の英大文字**なので、本文に載る **URL の不透明な ID**
    #    と衝突する（実測: フォーム ID `…7ZSVMHIA` の末尾が "HI" に当たって赤くなった）。
    #    ★ 条件名は**散文**に書かれていないかを見たいので、URL を除いてから検査する。
    #    ⚠️ 除くのは URL だけである（散文中の "HI 条件" は今までどおり捕まる）。
    for label, b in bodies.items():
        prose = re.sub(r"https?://\S+", " ", b)
        for token in ("HI", "LO", "摩擦", "仮説", "判定基準"):
            if token in prose:
                fails.append(f'"{token}" が{label}にある（§2.12 / protocol.md §4.3）')

    # ★★ 紙署名は 2026-08-03 に廃止した（D-1(a)）。G1-C の回答が同意の正本である。
    #   ⚠️ この検査を足した理由: **実動作で初めて見つかったバグだから**である。
    #   受付メールに「当日、説明・同意文書に署名をお願いします」が残っており、
    #   §2.12 の開示範囲だけを見ていた既存の検査は**緑のまま通していた**。
    #   ⚠️ 文言を戻すと protocol.md §4.1-1 / consent.md / Form_G1/README.md と食い違う。
    for label, b in bodies.items():
        if "署名" in b:
            fails.append(
                f'"署名" が{label}にある。★ 紙署名は廃止した（D-1(a)）。'
                "同意の正本は G1-C の回答である（protocol.md §4.1-1）"
            )

    # ★★ 第 11 版（2026-08-08）: 事前開示を**撤回した**。
    #   ⚠️ ★ 撤回前の文言は「目を通しておいて構いません」と「開いて始めないでください」を
    #      同じ段落に並べており、被験者から見て**どうすればよいか決まらなかった**。
    #   ★ 文言が戻ってきたら赤にする。⚠️ この検査が無いと、戻っても誰も気づかない
    #      （既存の検査はどれも「題材が漏れていないか」しか見ていない）。
    WITHDRAWN_PHRASES = (
        "目を通しておいて",
        "読まずに当日",
        "事前資料",
        "事前にお送りした",
        "お読みいただく資料",
        "開いた時点から時間を計り",
        "開いて始めてしまわないで",
    )
    for label, b in bodies.items():
        for phrase in WITHDRAWN_PHRASES:
            if phrase in b:
                fails.append(
                    f'"{phrase}" が{label}にある。'
                    "★ 事前開示は §2.12 第 11 版で撤回した（当日その場で取り掛かる）"
                )
    # ⚠️★★★ **被験者に届く本文に Markdown の `**` が残っていないこと**（2026-09-01 追加）。
    #   ★ `MailApp.sendEmail` は text/plain なので `**強調**` は装飾にならず記号のまま見える。
    #   ⚠️ 実測（修正前）: 受付メール 34 / 44 個、課題ページメール 18 個。
    #   ★ 検査は **生の本文ではなく、送信経路（`g1PlainBody_`）を通した形**を見る
    #     —— ⚠️ 生を見ていたから今まで緑だった。
    for label, key in (("受付メール(未用意)", "ackSent"),
                       ("受付メール(用意済み)", "ackWithMaterialsSent"),
                       ("課題ページメール", "materialsSent")):
        n = res[key].count("**")
        if n:
            fails.append(f"{label}: 被験者に届く本文に `**` が {n} 個残っている（text/plain では記号のまま見える）")
    # ★ 陰性対照: 記号を落としても中身の語が消えていないこと（⚠️ 全部消す実装でも緑にしない）
    if "ダウンロード" not in res["ackSent"]:
        fails.append("★ 陰性対照が壊れた: 受付メールから「ダウンロード」が消えている（落としすぎ）")

    for label, subject in (("受付メール", res["ackSubject"]),
                           ("課題ページメール", res["materialsSubject"])):
        for phrase in ("事前資料", "お読みいただく"):
            if phrase in subject:
                fails.append(f'"{phrase}" が{label}の**件名**にある（§2.12 第 11 版）')

    # ★ 検査が空回りしていないこと: 本文がちゃんと生成されている
    #   ★★ ゲートの言い方をメールにも要求する（2026-08-08）。
    #      ⚠️ ページ側だけゲートにしてメールが黙っていると、被験者は
    #      「開いたら始まる」と思ったままになる。★ **ページと文面を同じ検査で縛る。**
    GATE_MUST = ("課題を表示して始める", "当日まで押さないで")
    must_by_label = {
        "受付メール(未用意)": ("参加者ID", "5 分", "300〜400 字", "書き写し"),
        "受付メール(用意済み)": ("参加者ID", "5 分", "300〜400 字", "書き写し", "https://")
        + GATE_MUST,
        # ★ 課題ページメールが「リンクを渡す」「架空である」「準備の量で評価しない」
        #   の 3 点を落としていないか（§2.12-4）。★ 併せてゲートの言い方も要求する。
        "課題ページメール": ("参加者ID", "https://", "架空", "評価することはありません")
        + GATE_MUST,
    }
    for label, b in bodies.items():
        if len(b) < 200:
            fails.append(f"{label}の本文が短すぎる（{len(b)} 文字）。生成に失敗している疑い")
        for must in must_by_label.get(label, ()):
            if must not in b:
                fails.append(f'{label}に必要な案内 "{must}" が無い')

    # ★★ 第 13 版（2026-08-08・preregistration.md §2.14）: **初回起動は研究者が同席する。**
    #   ⚠️ ★ きっかけは実測である。macOS は Finder のダブルクリックに対して
    #      「壊れているため開けません」を出し、★ **この型には「このまま開く」が無い**。
    #      → 被験者は自力で開けない。⚠️ 旧文はそれを知らずに
    #        「★ 早めにお願いします」「当日その場だと時間がかかります」と
    #        **できないことを依頼していた**（開けずに不安にさせるだけだった）。
    #   ★ 文言が戻ってきたら赤にする。⚠️ この検査が無いと、戻っても誰も気づかない。
    SELF_LAUNCH_PHRASES = (
        "早めにお願いします",
        "当日その場だと",
        "許可の後に開き直しが必要",
    )
    for label, b in bodies.items():
        for phrase in SELF_LAUNCH_PHRASES:
            if phrase in b:
                fails.append(
                    f'"{phrase}" が{label}にある。'
                    "★ 第 13 版で初回起動は研究者同席に変えた（§2.14）。"
                    "被験者は自力で開けないので、自力起動を促す文言は置かない"
                )
    # ★ 逆側も縛る: 同席することと「壊れていない」ことを**必ず**言う。
    #   ⚠️ 言わないと、被験者は「壊れているため開けません」を見て
    #      ★ **ゴミ箱に入れてしまう**（取り返しがつかない）。
    ATTENDED_MUST = ("研究者と一緒に", "壊れていません", "ゴミ箱に入れないで")
    for label in ("受付メール(未用意)", "受付メール(用意済み)"):
        for must in ATTENDED_MUST:
            if must not in bodies[label]:
                fails.append(
                    f'{label}に "{must}" が無い。'
                    "★ 第 13 版（§2.14）: 初回起動は同席であること、"
                    "「壊れている」表示は故障ではないこと、ゴミ箱に入れないことを必ず書く"
                )

    # ★★★ 2026-08-08 新設: **G1-M / G1-S へたどり着けること**。
    #   ⚠️ ★ これが無かったせいで、受付メール・README・blockNN.html のどこにも
    #      リンクが無い状態が **P009 の実施まで気づかれなかった**（G1-M 回答数 = 0）。
    #      ★ 機械検査・文書検査がすべて緑でも、被験者が完走できるとは限らない。
    #   ⚠️ ★ **リンクの有無だけを見ない。** 位置づけ（いつ・何回・どう開くか）が
    #      書かれていることまで見る。リンクだけ貼っても被験者は使い分けられない。
    fid = gas_constants("FORM_ID_MCHECK", "FORM_ID_SURVEY")
    for k in ("FORM_ID_MCHECK", "FORM_ID_SURVEY"):
        if k not in fid:
            fails.append(f"{k} を .gs から読めない（検査が空回りしている疑い）")
    ROUTING_MUST = (
        "参加登録・ご同意",          # (1) が済んでいること
        "3 回目〜9 回目",            # (2) いつ
        "計 7 回",                   # (2) 何回
        "ブロック番号",              # ★ フォーム側の呼び方との橋渡し（§2.6 の設問は凍結）
        "別のタブ",                  # ★ protocol.md §3.1b（記入画面を切り替えない）
        "1 回だけ",                  # (2) 二重送信しない / (3) 1 回
        "10 回すべてが終わったあと",  # (3) いつ
    )
    for label in ("受付メール(未用意)", "受付メール(用意済み)"):
        b = bodies[label]
        for must in ROUTING_MUST:
            if must not in b:
                fails.append(
                    f'{label}に "{must}" が無い。'
                    "★ 3 つのフォームの位置づけ（いつ・何回・どう開くか）を書く"
                )
        # ★ リンクそのもの。⚠️ 短縮もプロパティも無いとき（= この検査の既定モード）は
        #   フォーム ID から組み立てた URL になる。★ **空にならないこと**が要件である。
        for name, key in (("G1-M", "FORM_ID_MCHECK"), ("G1-S", "FORM_ID_SURVEY")):
            if fid.get(key) and fid[key] not in b:
                fails.append(
                    f"{label}に {name} のリンクが無い。"
                    "★ 在宅の被験者はここからしかフォームに到達できない"
                )

    # ★★ 2026-08-08: 短縮 URL の**両分岐**を検査する（研究者要望で導入）。
    #   ⚠️ 上の bodies は短縮なし（フォールバック側）である。★ そちらは生の URL が出ること、
    #      短縮ありのときは**短縮が出ること**を、それぞれ確かめる。
    #   ⚠️ 片方だけ見ると、もう片方が壊れても緑になる。
    for label in ("受付メール(用意済み)", "課題ページメール"):
        if "https://example.com" not in bodies[label]:
            fails.append(
                f"{label}: 短縮が無いときに生の URL へフォールバックしていない。"
                "★ 短縮できなくてもリンクは配られなければならない"
            )
    short = run_gas("1")
    short_bodies = {
        "受付メール(未用意)": short["ack"],
        "受付メール(用意済み)": short["ackWithMaterials"],
    }
    for label, b in short_bodies.items():
        if "https://x.gd/SHORT" not in b:
            fails.append(
                f"{label}: 短縮 URL があるのに本文へ反映されていない"
                "（★ g1ShortOr_ を通していない箇所がある）"
            )
    # ★ 用意済みの分岐では、短縮が出るなら**生の Drive URL は出ない**こと（二重掲載の防止）
    if "https://example.com/folder" in short["ackWithMaterials"]:
        fails.append(
            "受付メール(用意済み): 短縮があるのに生の URL も残っている"
            "（★ どちらを開けばよいか分からなくなる）"
        )
    # ★★ フォームの回答 URL は 3 段（短縮 → publishedUrl → ID から組み立て）。
    #   ⚠️ ★ **3 段あるなら 3 段とも試す。** 1 段でも空を返すと導線が消える。
    #   ★ M と S で**別の値**を返すスタブにしてあるので、取り違え（両方 M など）も捕まる。
    for label in ("受付メール(未用意)", "受付メール(用意済み)"):
        for name, key in (("G1-M", "G1_MCHECK"), ("G1-S", "G1_SURVEY")):
            if "https://x.gd/SHORT-" + key not in short_bodies[label]:
                fails.append(f"{label}: {name} の**短縮**が本文に出ていない（g1ShortOr_ / g1FormLink_）")
    published = run_gas("2")
    for label, b in (("受付メール(未用意)", published["ack"]),
                     ("受付メール(用意済み)", published["ackWithMaterials"])):
        for name, key in (("G1-M", "G1_MCHECK"), ("G1-S", "G1_SURVEY")):
            if "PUBLISHED-" + key not in b:
                fails.append(
                    f"{label}: 短縮が無いとき {name} が **publishedUrl** に落ちていない"
                    "（★ 3 段のうち 2 段目が壊れている）"
                )

    if fails:
        print("[NG] メールが §2.12（第 11 版）の開示範囲・撤回後の文言から外れている")
        for f in fails:
            print(f"  - {f}")
        return 1
    print("[OK] 受付メール(2 分岐)・課題ページメールは §2.12（第 11 版）を守っている")
    print("     G1 実施トラッキングの列参照・G1-C の設問名も一致している")
    print(f"     題材名 {len(topic_titles())} 件・課題の型・条件名のいずれも本文に無い")
    return 0


if __name__ == "__main__":
    sys.exit(main())
