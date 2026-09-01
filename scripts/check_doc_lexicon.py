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
        try:
            lines = open(path, encoding='utf-8').read().split('\n')
        except FileNotFoundError:
            print('  [warn] not found: %s' % path)
            continue
        for i, line in enumerate(lines, 1):
            if not pattern.search(line):
                continue
            if allow_historical and HISTORICAL.search(line):
                continue
            hits.append((path, i, label, line.strip()[:90]))
    return hits

def main():
    violations = []

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

    if not violations:
        print('=== 違反なし ===')
        return 0

    print('=== 違反 %d 件 ===' % len(violations))
    for path, line_no, label, text in violations:
        print('  %s:%d' % (path, line_no))
        print('    [%s] %s' % (label, text))
    print()
    print('履歴記述として正当な場合は、その行に「廃止」「旧称」「削除済」「逐語」等を含めること。')
    return 1

if __name__ == '__main__':
    sys.exit(main())
