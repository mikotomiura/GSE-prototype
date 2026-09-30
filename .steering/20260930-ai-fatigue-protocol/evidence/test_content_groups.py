"""content_groups.py の分類（design.md §7.6）の陽性・陰性の検査。ネットワークに出ない。"""
import unittest

import content_groups as G


class TestClassify(unittest.TestCase):
    def test_review_by_title_only(self):
        self.assertEqual(G.classify("AI fatigue: a scoping review", "students randomized")["group"], "レビュー等")
        self.assertEqual(G.classify("Corrigendum to X", "")["group"], "レビュー等")
        # 抄録の review の語ではレビューにしない（題名だけで見る）
        self.assertEqual(G.classify("AI use and burnout", "we review the literature; nurses; survey")["kind"], "一次研究")

    def test_priority_order_on_each_axis(self):
        g = G.classify("Ambient AI scribes", "A randomized trial of 238 physicians using ambient AI scribes and a survey")
        self.assertEqual((g["pop"], g["ai"], g["design"]), ("医療者", "記録支援・下書き", "無作為化"))
        g = G.classify("ChatGPT and burnout", "A cross-sectional survey of 500 university students using ChatGPT")
        self.assertEqual((g["pop"], g["ai"], g["design"]), ("学生・学習者", "生成 AI・対話", "横断調査"))

    def test_word_boundaries(self):
        # "said" や "maintain" の中の ai・AI に当てない
        self.assertEqual(G.classify("x", "They said it would maintain the pace")["ai"], "不明")
        self.assertEqual(G.classify("x", "employees and AI adoption")["ai"], "AI 一般・導入")
        # "users" は当てるが "reuse" には当てない
        self.assertEqual(G.classify("x", "reuse of tools")["pop"], "不明")

    def test_statistical_predict_is_not_decision_support(self):
        # 判断 6: 「AI awareness predicts exhaustion」は意思決定支援の AI ではない
        g = G.classify("x", "AI awareness positively predicts emotional exhaustion among employees")
        self.assertEqual(g["ai"], "AI 一般・導入")
        self.assertEqual(G.classify("x", "a sepsis early warning system")["ai"], "意思決定支援・警報・予測")
        self.assertEqual(G.classify("x", "a risk prediction model deployed to nurses")["ai"], "意思決定支援・警報・予測")

    def test_presurvey_postsurvey_is_comparison(self):
        g = G.classify("x", "clinicians completed the presurvey and postsurvey; survey analysis cohort")
        self.assertEqual(g["design"], "比較（非無作為化・前後）")

    def test_unknown_when_nothing_matches(self):
        g = G.classify("Something", "")
        self.assertEqual(g["group"], "不明｜不明｜不明")


if __name__ == "__main__":
    unittest.main()
