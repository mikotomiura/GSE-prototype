"""統計の変異（stats.MUT）を 1 つずつ入れ、名指しした対照が赤になることを確かめる。合成のデータだけ。

  m1: A と B を入れ替える（A に見た目を入れる）        → P-LEAK（漏れを入れて満たさない）が赤
  m2: 日でなく窓の単位で引き直す                        → P-DAY（日の引き直しで欠ける割合）が赤
  m4: 切片も罰する                                      → P-GRAD（勾配が 0）が赤
  m3: 天井を差と別の合格の経路にする                    → 等価に近い（A の AUC の 5% 点が 0.95 を超えると差の上限は
                                                         ほぼ 1 − AUC(A) < δ なので、判定がほとんど変わらない）。
                                                         verdict.with_ceiling の単体の検査で縛り、ここでは数えない。
赤は名指しした対照（メッセージの頭の P-…:）が赤になったときだけ数える。
終了コード: すべての変異が赤なら 0、どれかが緑（素通り）なら 3、変異なしで赤なら 4。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import selftest as T  # noqa: E402
import stats as S  # noqa: E402

PLAN = {"m1": ("P-LEAK", T.test_analysis_controls), "m2": ("P-DAY", T.test_day_bootstrap),
        "m4": ("P-GRAD", T.test_logistic)}


def run(fn, mut):
    S.MUT.clear()
    S.MUT.update(mut)
    T.FAILS.clear()
    fn()
    out = list(T.FAILS)
    S.MUT.clear()
    T.FAILS.clear()
    return out


def main():
    rc = 0
    for m, (name, fn) in PLAN.items():
        if run(fn, set()):
            print(f"{name}: 変異なしで赤")
            sys.exit(4)
        fails = run(fn, {m})
        named = [f for f in fails if f.startswith(name + ":")]
        if named:
            print(f"{m} → {name}: 赤（{len(named)} 件・ほかの赤 {len(fails) - len(named)} 件）")
        else:
            # 名指しした対照が赤にならなければ、ほかの検査が赤でも素通りと数える
            print(f"{m} → {name}: 緑（素通り・ほかの赤 {len(fails)} 件）")
            rc = 3
    sys.exit(rc)


if __name__ == "__main__":
    main()
