#!/usr/bin/env python3
"""提出文書と設計語彙の回帰検査。

なぜ要るか: 2026-08-31 の /cross-review で、ADR-018 D7 が廃止した段階呼称 Lv1-4 が
3 ファイル (技術設計書 5.2 の表 / physical-anchor SKILL.md / glossary.md) に
取り残されていた。人手の grep では「履歴記述として正当な残存」と
「更新漏れ」を区別できず見落とす。ここでは行単位の許可パターンで両者を分ける。

使い方:
    PYTHONUTF8=1 python scripts/check_doc_lexicon.py
終了コード: 0 = 違反なし / 1 = 違反あり
"""
import os
import re
import sys
import unicodedata

MITOU = [
    'docs/mitou_submission/mitou_docs/[提案プロジェクト詳細資料]GSE_proposal.docx.md',
    'docs/mitou_submission/mitou_docs/[提案プロジェクト補足資料]GSE技術設計書.docx.md',
    # ★ 2026-09-02: 分割で増えた 3 本も検査対象に入れる（⚠️ 入れないと禁止用語が素通りする）
    'docs/mitou_submission/mitou_docs/[提案プロジェクト補足資料]GSE検証レポート.docx.md',
    'docs/mitou_submission/mitou_docs/[提案プロジェクト補足資料]GSE参考文献.docx.md',
    'docs/mitou_submission/mitou_pptx/[提案プロジェクト補足資料]GSE設計スライド.pptx.md',
]
SSOT = ['docs/glossary.md', '.claude/skills/physical-anchor/SKILL.md']

# 履歴・規則・逐語引用としての言及は違反にしない。
# (a) 履歴・規則・逐語引用としての言及、(b) 否定形での言及 は違反にしない。
#     例:「完了判定を置かない」は ADR-018 に *従った* 記述であって違反ではない。
HISTORICAL = re.compile(
    r'廃止|旧称|旧版|旧義|旧文|削除済|全削除|に削除|に失効|使わない|'
    r'違反|逐語|~~|2026年度提案|2026 年度提案|取り下げ|'
    # 否定形 (これらが同じ行にあれば、禁止語は「やらないこと」として書かれている)
    r'置かない|置かず|課さない|課さず|判定しない|判定せず|存在しない|'
    r'解釈しない|外した|外れた|持たない|実装しない|書かない|使わず'
)

def scan(paths, pattern, label, allow_historical=True):
    hits = []
    for path in paths:
        lines = open(path, encoding='utf-8').read().split('\n')
        for i, line in enumerate(lines, 1):
            if not pattern.search(line):
                continue
            if allow_historical and HISTORICAL.search(line):
                continue
            hits.append((path, i, label, line.strip()[:90]))
    return hits

def missing(paths):
    """検査対象の不在を列挙する。

    ⚠️★★★ 2026-09-04 追加。旧版は `FileNotFoundError` を `[warn]` にして読み飛ばしており、
    ★ **対象が 1 本も無くても `=== 違反なし ===` / exit 0 になった**（実測）。
    → ⚠️ 実際にこれを踏んだ: ブランチが切り替わって `docs/mitou_submission/` が無い状態で
    回し、**緑だと誤読した**。★ 対象の不在は「違反なし」ではなく **検査の空回り**である。
    """
    return [p for p in paths if not os.path.exists(p)]


UI_ROOT = 'src'
JAPANESE = re.compile('[぀-ヿ一-鿿]')
# 境界は英字・片仮名で取る。`\b` は Python の Unicode の \w で「Flowの」の境界を作らず見逃す
# (2026-11-05 のレビューで実測)。片仮名の前後を見るのは「ワークフロー」「スタックトレース」を拾わないため。
KATA = 'ァ-ヶー'
STATE_NAMES = re.compile(
    r'(?<![A-Za-z])(Flow|Incubation|Stuck)(?![A-Za-z])'
    r'|(?<![' + KATA + r'])(フロー|インキュベーション|スタック)(?![' + KATA + r'])'
    r'|推定状態'
)
BLOCK_COMMENT = re.compile(r'/\*.*?\*/', re.S)
LINE_COMMENT = re.compile(r'(?<!:)//[^\n]*')

# 毎回の実行で先に通す対照 (外れたら検査が成立していない)。
UI_CONTROLS_HIT = [
    "'推定状態 (Flow / Incubation / Stuck) は表示していません。'",
    '<p>いまはFlowの状態です</p>',
    "'状態はStuckです'",
    "'状態はＳｔｕｃｋです'",
    "'フロー状態です'",
]
UI_CONTROLS_MISS = [
    "'推定の結果は表示していません。'",
    '<label>Flow</label>',
    "return 'Stuck';",
    "'ワークフローを開始'",
    "'スタックトレースを送る'",
    "{/* 推定状態 (Flow) はコメント */}",
    "// 推定状態 Stuck はコメント",
]


def frontend_sources():
    paths = []
    for dirpath, _dirs, files in os.walk(UI_ROOT):
        for name in files:
            if name.endswith(('.ts', '.tsx')):
                paths.append(os.path.join(dirpath, name))
    return sorted(paths)


def blank_comments(src):
    """コメントを同じ行数の空行に置き換える (行番号を保つ)。"""
    keep_lines = lambda m: '\n' * m.group(0).count('\n')
    return LINE_COMMENT.sub('', BLOCK_COMMENT.sub(keep_lines, src))


def ui_line_violates(line):
    line = unicodedata.normalize('NFKC', line)
    return bool(JAPANESE.search(line) and STATE_NAMES.search(line))


def ui_controls_fail():
    """対照が期待どおりに当たる・外れるかを確かめ、外れたものを返す。"""
    bad = [c for c in UI_CONTROLS_HIT if not any(ui_line_violates(l) for l in blank_comments(c).split('\n'))]
    bad += [c for c in UI_CONTROLS_MISS if any(ui_line_violates(l) for l in blank_comments(c).split('\n'))]
    return bad


def scan_ui_text(paths):
    """日本語を含む行 (被験者向けの文) に 3 状態の名前があれば違反。

    英語だけの行 (開発ビルドだけで出る確率の帯のラベル・`return 'Flow'`) は拾わない。
    コメントは地の文の直し (ADR-046 Migration 5) の対象で、ここでは見ない。

    既知の限界 (検査が甘くなる向き。.steering/20261105-dashboard-state-names/decisions.md 判断 4):
    - 文字列の中の `/*` から次の `*/` まで、`:` の直後でない `//` から行末までもコメントとして消す。
    - 判定は 1 行ずつなので、日本語と名前が別の行に分かれた文は拾わない。
    - 対象は src/ の ts・tsx だけ。Rust の文字列 (トレイは tray.rs のテストが守る)・
      index.html・tauri.conf.json・CSS は見ない。
    """
    hits = []
    label = '被験者向けの文の状態名 (ADR-046 D1)'
    for path in paths:
        code = blank_comments(open(path, encoding='utf-8').read())
        for i, line in enumerate(code.split('\n'), 1):
            if ui_line_violates(line):
                hits.append((path, i, label, line.strip()[:90]))
    return hits


def main():
    violations = []

    gone = missing(MITOU + SSOT)
    if gone:
        print('=== 検査が成立していない: 対象 %d 本が見つからない ===' % len(gone))
        for p in gone:
            print('  [missing] %s' % p)
        print()
        print('★ ブランチ / 作業ディレクトリを確かめること（★ 不在は「違反なし」ではない）。')
        return 1


    # 1) 段階呼称 Lv1-4 (ADR-018 D7)
    violations += scan(MITOU + SSOT, re.compile(r'Lv[ ]?[1-4]'), '段階呼称 Lv1-4 (ADR-018 D7)')

    # 2) Physical Anchor の完了判定語 (ADR-018 D1/D3)
    pa_judge = re.compile(r'完了条件|完了判定|達成条件|クリア条件|completed|achieved')
    violations += scan(MITOU, pa_judge, 'Physical Anchor の完了判定語 (ADR-018 D1/D3)')

    # 3) 提出文書に装飾記号を残さない (研究者指示 2026-08-31)
    marks = re.compile('[' + '⚠' + '★' + ']')
    violations += scan(MITOU, marks, '装飾記号 (提出文書では使わない)', allow_historical=False)

    # 4) 撤回済みの主張 (survey 2026-08-31)
    retracted = re.compile(r'一方向に消耗させ|最大の強みである|不便益 ?HCI ?である|不便益を測定可能')
    violations += scan(MITOU, retracted, '撤回済みの主張')

    # 5) 被験者が見る日本語の文に 3 状態の名前と「推定状態」を出さない (ADR-046 D1)
    ui_files = frontend_sources()
    if not ui_files:
        print('=== 検査が成立していない: src/ に ts・tsx が 1 本も無い ===')
        return 1
    bad_controls = ui_controls_fail()
    if bad_controls:
        print('=== 検査が成立していない: 検査 5 の対照が期待と違う ===')
        for c in bad_controls:
            print('  [control] %s' % c)
        return 1
    violations += scan_ui_text(ui_files)

    if not violations:
        print('=== 違反なし ===')
        return 0

    print('=== 違反 %d 件 ===' % len(violations))
    for path, line_no, label, text in violations:
        print('  %s:%d' % (path, line_no))
        print('    [%s] %s' % (label, text))
    print()
    print('履歴記述として正当な場合は、その行に「廃止」「旧称」「削除済」「逐語」等を含めること。')
    print('（検査 5 の被験者向けの文には、この許可は効かない。）')
    return 1

if __name__ == '__main__':
    sys.exit(main())
