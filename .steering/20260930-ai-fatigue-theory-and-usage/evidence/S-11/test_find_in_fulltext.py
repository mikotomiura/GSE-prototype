"""find_in_fulltext.docx_text の端（合成した XML・ファイルもネットワークも使わない・decisions.md 判断 15）。

使い方: このディレクトリで `python -m unittest test_find_in_fulltext`
"""
import unittest

import find_in_fulltext as T

NS = 'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"'


def doc(body):
    return f'<w:document {NS}><w:body>{body}</w:body></w:document>'.encode("utf-8")


class DocxTextTest(unittest.TestCase):
    def test_run_split_word_is_joined(self):
        x = doc('<w:p><w:r><w:t>AI fat</w:t></w:r><w:r><w:rPr><w:b/></w:rPr><w:t>igue</w:t></w:r></w:p>')
        self.assertEqual(T.docx_text(x), "AI fatigue")

    def test_tab_and_break_are_spaces(self):
        x = doc('<w:p><w:r><w:t>prompt</w:t><w:tab/><w:t>fatigue</w:t><w:br/><w:t>next</w:t><w:cr/><w:t>end</w:t></w:r></w:p>')
        self.assertEqual(T.docx_text(x), "prompt fatigue next end")

    def test_nested_paragraph_does_not_drop_outer_text(self):
        x = doc('<w:p><w:r><w:t>before</w:t></w:r><w:r><w:pict><w:txbxContent><w:p><w:r><w:t>inbox</w:t></w:r></w:p>'
                '</w:txbxContent></w:pict></w:r><w:r><w:t> AFTER prompt fatigue</w:t></w:r></w:p>')
        self.assertEqual(T.docx_text(x).split("\n"), ["before AFTER prompt fatigue", "inbox"])

    def test_self_closing_text_element(self):
        x = doc('<w:p><w:r><w:t xml:space="preserve"/></w:r><w:r><w:t>word</w:t></w:r></w:p>')
        self.assertEqual(T.docx_text(x), "word")

    def test_table_cells_are_separate_lines(self):
        x = doc('<w:tbl><w:tr><w:tc><w:p><w:r><w:t>cell1</w:t></w:r></w:p></w:tc>'
                '<w:tc><w:p><w:r><w:t>cell2</w:t></w:r></w:p></w:tc></w:tr></w:tbl>')
        self.assertEqual(T.docx_text(x), "cell1\ncell2")

    def test_entities_are_unescaped(self):
        x = doc('<w:p><w:r><w:t>A &amp; B &lt; C</w:t></w:r></w:p>')
        self.assertEqual(T.docx_text(x), "A & B < C")


if __name__ == "__main__":
    unittest.main()
