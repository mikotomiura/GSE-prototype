"""R7 の検査: 件数の丸め（半分以上は切り上げ）・割合と率と AUC の粗さ・出さないキー・漏れの走査。"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cr_common as cm  # noqa: E402

assert [cm.ps.round_count(v) for v in (46, 50, 14, 32, 250, 149, 2)] == [45, 100, 15, 30, 300, 100, 0]
pub = cm.ps.public({"total": 137, "stalls_used": 23, "pairs": 1234, "missing_day_numbers": 3, "per_obs_h": 12.345,
                    "obs_h": 123.4, "auc_K": 0.54321, "app_version_kinds": 2,
                    "files_with_rows": {"num": 23, "den": 37, "ratio": 0.6216},
                    "ci95": {"K": [0.51234, 0.59876]}, "signal_auc": {"d_p_stuck": 0.50049},
                    "C0": {"pooled_per_h": 7.4321}, "by_class": {"x": {"diff": 0.12345, "diff_ci95": [0.01234, 0.2]}}})
assert "total" not in pub and pub["stalls_used"] == 25 and pub["pairs"] == 1200 and pub["missing_day_numbers"] == 5, pub
assert pub["per_obs_h"] == 12.0 and pub["obs_h"] == 120 and pub["auc_K"] == 0.543, pub
assert "app_version_kinds" not in pub
assert pub["files_with_rows"] == {"num": 25, "den": 35}, pub["files_with_rows"]  # 割合は出さない
assert pub["ci95"]["K"] == [0.512, 0.599] and pub["signal_auc"]["d_p_stuck"] == 0.5, pub
assert pub["C0"]["pooled_per_h"] == 7.4 and pub["by_class"]["x"] == {"diff": 0.123, "diff_ci95": [0.012, 0.2]}, pub
# n4 の人の間の表: 親のキーの規則を子（by_person・min・max）に引き継ぐ。share を含むキーは有効数字 2 桁
pub = cm.ps.public({"between_people": {"C0_pooled_per_h": {"by_person": {"A": 7.4321, "B": 9.8765}, "min": 7.4321,
                                                           "max": 9.8765, "max_over_min": 1.3289},
                                       "C0_share_long_or_censored": {"by_person": {"A": 0.12345}}},
                    "share_longer_than_s": {"2": 0.123456}})
bp = pub["between_people"]
assert bp["C0_pooled_per_h"]["by_person"] == {"A": 7.4, "B": 9.9} and bp["C0_pooled_per_h"]["min"] == 7.4, bp
assert bp["C0_pooled_per_h"]["max_over_min"] == 1.3 and bp["C0_share_long_or_censored"]["by_person"]["A"] == 0.12, bp
assert pub["share_longer_than_s"]["2"] == 0.12, pub
# 手前の窓: 停滞の分母が 20 未満なら差と区間も伏せる。無作為の窓は割合だけ・数は出さない
pw = cm.ps.public({"random_windows": 180, "by_class": {
    "focus": {"stall": {"num": 3, "den": 18, "ratio": 0.1667}, "random": {"num": 20, "den": 180, "ratio": 0.1111},
              "diff": 0.0556, "diff_ci95": [0.01, 0.1]},
    "silence": {"stall": {"num": 10, "den": 40, "ratio": 0.25}, "random": {"num": 80, "den": 400, "ratio": 0.2},
                "diff": 0.05, "diff_ci95": [0.0123, 0.1]}}})
assert "random_windows" not in pw, pw
f, sl = pw["by_class"]["focus"], pw["by_class"]["silence"]
assert f["stall"]["ratio"] is None and f["diff"] is None and f["diff_ci95"] is None and f["random"] == {"ratio": 0.11}, f
assert sl["diff"] == 0.05 and sl["diff_ci95"] == [0.012, 0.1] and sl["random"] == {"ratio": 0.2}, sl
# 規則の無い小数は有効数字 3 桁（SD・比・分位）。整数はそのまま
z = cm.ps.public({"sd_ratio": 1.23456, "q0.5": 0.0123456, "theta_ms": 31234, "mu_log10_ms": 3.98765,
                  "delta_auc": 0.012345})
assert z == {"sd_ratio": 1.23, "q0.5": 0.0123, "theta_ms": 31234, "mu_log10_ms": 3.99, "delta_auc": 0.012}, z  # AUC は小数 3 桁
# 行の型の表: 総数と secure_input を出さない（率と、本のある数だけ）
rw = cm.ps.public({"rows": {"key_press": {"total": 36712, "per_obs_h": 830.4, "files_with_rows": {"num": 31, "den": 32, "ratio": 0.9688}},
                            "secure_input": {"total": 0, "per_obs_h": 0.0, "files_with_rows": {"num": 0, "den": 32, "ratio": 0.0}}}})
assert rw == {"rows": {"key_press": {"per_obs_h": 830.0, "files_with_rows": {"num": 30, "den": 30}}}}, rw
assert cm.ps.leaks('{"x": "P006"}', {"P006": {}}, set()) == ["P-ID"]
print("cr_common test ok")
