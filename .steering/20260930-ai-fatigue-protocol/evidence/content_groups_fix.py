"""内容の群の、メインの確かめ（design.md §7.6 (a)(b)）で直した値を当てる。

(a) どれかの軸が不明の 52 件を、題名・抄録・要点・DB の欄で読んで直した（分からないものは不明のまま）。
(b) 無作為の 30 件（seed 20260930）で誤りと分かったもの（SAMPLE_FIX）。
使い方: python content_groups_fix.py dedup/content_groups_2026-09-30_v2.json dedup/content_groups_2026-09-30_final.json
"""
import datetime
import json
import sys

REVIEW = dict(kind="レビュー等", pop="—", ai="—", design="—", group="レビュー等")
# 鍵: (軸の直し, 根拠)
FIX = {
    "AF002": (dict(pop="消費者・一般の利用者", design="横断調査"), "DB の研究情報: 生成 AI 利用者・横断質問紙"),
    "AF003": (dict(ai="生成 AI・対話", design="横断調査"), "DB の研究情報: 生成 AI・質問紙調査"),
    "AF004": (dict(design="横断調査"), "DB の研究情報: 横断質問紙"),
    "AF013": (REVIEW, "DB の分類: 既存レビュー"),
    "AF020": (dict(pop="消費者・一般の利用者"), "DB の研究情報: 実験参加者"),
    "AF026": (REVIEW, "DB の分類: 尺度・理論"),
    "AF027": (REVIEW, "DB の分類: 尺度・理論"),
    "AF028": (REVIEW, "DB の分類: 尺度・理論"),
    "AF029": (REVIEW, "DB の分類: 尺度・理論"),
    "S02-04": (dict(design="横断調査"), "要点: 調査・N=197"),
    "S04-13": (dict(pop="医療者"), "抄録: 医療の職場の 597 名"),
    "S04-41": (dict(design="比較（非無作為化・前後）"), "要点: 前後"),
    "S04-43": (dict(design="実験・模擬"), "要点: 模擬の比較"),
    "S04-46": (dict(design="比較（非無作為化・前後）"), "要点: 前後（3 か月）"),
    "S04-53": (dict(design="比較（非無作為化・前後）"), "要点: 試行の前後"),
    "S04-67": (dict(design="比較（非無作為化・前後）"), "要点: 後ろ向きの前後"),
    "S04-74": (dict(design="無作為化"), "要点: 2 回の外来の枠で順を無作為に割り付けた交代"),
    "S04-84": (dict(pop="医療者"), "抄録: AI 支援の内視鏡（使うのは内視鏡医）"),
    "S05-03": (dict(pop="消費者・一般の利用者"), "抄録: 実験の参加者"),
    "S05-05": (dict(ai="AI 一般・導入"), "抄録: 機械学習の自律エージェント"),
    "S12-01": (dict(pop="医療者"), "要点: 超音波検査技師"),
    "S12-10": (dict(design="比較（非無作為化・前後）"), "要点: 前後比較"),
    "S12-15": (dict(pop="働く人（医療・教育の外）"), "要点: 原子力施設の点検の作業"),
    "S12-21": (dict(pop="教員・研究者"), "要点: 医学教育の分野別評価（評価する人）"),
    "S13-19": (dict(pop="教員・研究者"), "題名: 学校長"),
    "S14-10": (dict(design="横断調査"), "要点: 横断"),
    "S14-11": (dict(design="横断調査"), "要点: 横断・PROCESS"),
    "S14-19": (dict(pop="働く人（医療・教育の外）"), "要点: 部下"),
    "S14-21": (dict(design="縦断"), "要点: 3 時点の対応のある調査"),
    "S14-25": (dict(design="横断調査"), "要点: 横断"),
    "S14-26": (dict(pop="働く人（医療・教育の外）"), "要点: 越境 EC の従事者"),
    "S14-27": (dict(design="横断調査"), "要点: 横断"),
    "S14-38": (dict(pop="医療者"), "要点: 心理療法士"),
    "S15-07": (dict(design="横断調査"), "要点: 横断・機械学習の予測"),
    "S15-10": (dict(pop="消費者・一般の利用者"), "要点: 一般の参加者"),
    "S15-21": (dict(pop="消費者・一般の利用者", ai="生成 AI・対話"), "抄録: 母親・ChatGPT（記録支援ではない）"),
}
SAMPLE_FIX = {
    # (b) 無作為の 30 件（seed 20260930）のうち、誤りと分かった 10 件（3 軸とも正しかったのは 20 件）
    "AF025": (REVIEW, "DB の分類: 尺度・理論（機械は題名で一次研究とし、AI を記録支援とした）"),
    "S04-37": (dict(kind="一次研究", pop="学生・学習者", ai="AI 一般・導入", design="横断調査"),
               "要点: N 251 の一次研究（題名の framework でレビュー等にしていた）"),
    "S04-60": (dict(design="比較（非無作為化・前後）"), "要点: 2 つの道具の交差（対照なし）"),
    "S04-76": (dict(design="比較（非無作為化・前後）"), "要点: 前向きの観察で AI あり・なしの受診を比べた"),
    "S05-07": (dict(ai="意思決定支援・警報・予測", design="質的"), "抄録: 胸部 X 線の優先づけの AI・導入前後の面接（質的）"),
    "S12-07": (dict(design="横断調査"), "抄録: cross-sectional study・questionnaire survey"),
    "S13-11": (dict(ai="意思決定支援・警報・予測"), "抄録: 診断の意思決定への AI の統合"),
    "S14-05": (dict(ai="意思決定支援・警報・予測"), "抄録: AI-DSS（記録の提案は定義の一部）"),
    "S14-13": (dict(design="横断調査"), "要点: 横断・SmartPLS"),
    "S14-37": (dict(design="比較（非無作為化・前後）"), "要点: 単群の試験（前後）"),
}


def apply(groups, fixes):
    out, log = {}, []
    for k, v in groups.items():
        v = dict(v)
        if k in fixes:
            ch, why = fixes[k]
            v.update(ch)
            if v["kind"] == "一次研究":
                v["group"] = f"{v['pop']}｜{v['ai']}｜{v['design']}"
            v["fixed_by_main"] = why
            log.append(k)
        out[k] = v
    return out, log


def main(src, dst):
    d = json.load(open(src, encoding="utf-8"))
    groups, log = apply(d["groups"], {**FIX, **SAMPLE_FIX})
    with open(dst, "x", encoding="utf-8", newline="\n") as f:
        json.dump(dict(executed=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat(timespec="seconds"),
                       source=src, rule="design.md §7.6・判断 6", n_fixed=len(log), groups=groups), f, ensure_ascii=False, indent=1)
        f.write("\n")
    print("直した", len(log), "不明を含む", sum(1 for v in groups.values() if "不明" in v["group"]))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
