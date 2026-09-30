"""screen.py の正規表現の陽性・陰性（design.md §1.2・§2.3 の例文）。

使い方: このディレクトリで `python -m unittest test_screen`
"""
import unittest

import screen as S


class TermsTest(unittest.TestCase):
    POS = {
        "AI fatigue": "N1", "AI-induced fatigue": "N1", "generative AI fatigue": "N1", "GenAI fatigue": "N1",
        "ChatGPT fatigue": "N1", "LLM burnout": "N1", "AI use fatigue": "N1", "artificial intelligence exhaustion": "N1",
        "fatigue from using ChatGPT": "N2", "burnout caused by generative AI": "N2", "fatigue toward AI": "N2",
        "exhaustion due to the use of AI": "N2",
        "prompt fatigue": "N3", "prompting fatigue": "N3",
        "AI 疲れ": "N4", "生成AIによる疲労": "N4", "プロンプト疲れ": "N4", "人工知能への疲弊": "N4",
        "AI anxiety": "N5", "AI-induced technostress": "N5", "AI stressors": "N5",
    }
    NEG = ["said fatigue", "fatigue assessment", "Thai fatigue", "AI adoption and burnout", "fatigue of workers",
           "promptly fatigued", "the email fatigue", "fatigue detection using machine learning"]

    def test_positive(self):
        for text, key in self.POS.items():
            with self.subTest(text=text):
                self.assertIn(key, S.terms(text), f"{text!r} に {key} が当たらない")

    def test_negative(self):
        for text in self.NEG:
            with self.subTest(text=text):
                self.assertFalse(S.uses_term(S.terms(text)), f"{text!r} が語を使う記録に当たった: {S.terms(text)}")

    def test_n5_alone_is_not_use(self):
        self.assertFalse(S.uses_term(S.terms("AI anxiety and AI-induced technostress")))

    def test_hit_strings_only(self):
        # 返すのは当たった語の文字列だけ（抄録の文を返さない）
        h = S.terms("Students reported AI fatigue after long sessions.")
        self.assertEqual(h, {"N1": ["AI fatigue"]})


class GeneralTest(unittest.TestCase):
    def test_general(self):
        g = S.general("Emotional exhaustion and burn-out; NASA-TLX workload; information overload; job strain; tired.")
        for k in ["情動的消耗", "消耗", "燃え尽き", "作業負荷", "情報過多", "負担（strain）", "疲れ"]:
            self.assertIn(k, g)

    def test_strain_word(self):
        self.assertNotIn("負担（strain）", S.general("constrained restrain"))


class FrameworksTest(unittest.TestCase):
    POS = {
        "job demands-resources model": "F-JDR", "JD-R": "F-JDR", "Job Demands–Resources": "F-JDR",
        "conservation of resources theory": "F-COR", "COR theory": "F-COR",
        "technostress creators": "F-TS", "techno-overload": "F-TS",
        "cognitive load theory": "F-CLT", "stressor-strain-outcome": "F-SSO", "SSO framework": "F-SSO",
        "transactional model of stress": "F-TMS", "challenge-hindrance stressors": "F-TMS",
        "self-determination theory": "F-SDT", "ego depletion": "F-EGO", "strength model": "F-EGO",
        "stimulus-organism-response": "F-SOR", "S-O-R model": "F-SOR", "effort-recovery model": "F-ER",
        "effort-reward imbalance": "F-ER", "person-environment fit": "F-PEF", "opportunity cost": "F-OC",
        "passive fatigue": "F-AP", "vigilance decrement": "F-AP", "automation bias": "F-AUT",
        "technology acceptance model": "F-ACC", "UTAUT": "F-ACC", "information overload": "F-IO",
    }
    NEG = {
        "COR": "F-COR", "TAMPA": "F-ACC", "self-organizing response": "F-SOR", "include cltx": "F-CLT",
        "resourceful people": "F-EGO", "cognitive load": "F-CLT", "technology use": "F-ACC", "sensor": "F-SOR",
    }

    def test_positive(self):
        for text, key in self.POS.items():
            with self.subTest(text=text):
                self.assertIn(key, S.frameworks(text))

    def test_negative(self):
        for text, key in self.NEG.items():
            with self.subTest(text=text):
                self.assertNotIn(key, S.frameworks(text))


class SentencesTest(unittest.TestCase):
    def test_cue(self):
        text = "Background text here. AI fatigue is defined as a state of weariness. We measured AI fatigue weekly."
        self.assertEqual(S.cue_sentences(text), [(1, True), (2, False)])


if __name__ == "__main__":
    unittest.main()
