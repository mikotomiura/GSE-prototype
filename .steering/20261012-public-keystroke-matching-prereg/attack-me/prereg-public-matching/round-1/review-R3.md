# 査読 R3（プライバシーの評価の指標の方法論と、事前登録・再現性の立場）stage prereg・round 1

## 1. 接地
- G1 敵の模型。Wagner & Eckhoff（wagner2015.txt:206-207）「To allow for a better interpretation of the outcome of privacy metrics, studies should always include a detailed description of the used adversary model.」／ :197-198「evaluating a PET with a weak adversary model can lead to an overestimation of privacy.」
- G2 事前の知識。:1610-1611「if the adversary happens to have relevant prior knowledge, the privacy level indicated by k is no longer accurate.」
- G3 複数の出力。:1577「Instead of fixing a single output measure for a scenario, we recommend to measure several different outputs.」／ :1590-1591「we recommend to select metrics that reflect the average case, the distribution of privacy values, and the worst case.」
- G4 実装の検証。:1689「we therefore recommend to consider selecting metrics for which a validated implementation exists.」
- G5 Nosek et al.（nosek2018.txt:96）「In prediction, the problem of forking paths is avoided because the analytic pipeline is specified before observing the data.」／ :99「That commitment is usually accomplished by posting the analysis plan to an independent registry such as https://clinicaltrials.gov/ or https://osf.io/ .」
- G6 :115「An effective preregistration will account for any loss of blinding and what impact that could have on the reported results.」／ :111「Another method is to preregister a decision tree. The decision tree defines the sequence of tests and decision rules at each stage of the sequence.」

## 2. 評価表
| 軸 | 点 | 所見 |
|---|---|---|
| a | 4 | 主張を自分で縛っている（:25・:183）。主要表は攻撃者の最大で楽観に偏る（指摘 7） |
| b | 2 | 揃えのコードが文と合わない・候補の末尾がただ・窓の正解が A2 依存・閉じた世界の仮定が無い |
| c | 4 | R1 と候補の加工を同じ攻撃者・同じ N で並べる表は公開する側に実用的。有用性も出す |
| d | 4 | 表で固定して読みやすい。ENJA15 の節は薄く `romaji_table.py` に寄りかかる |
| e | 3 | 倫理の材料はあるが「superficial application domain」を避ける脅威の筋書きが無い。攻撃手順の公開を「論文の段で決める」（:179）は open science の節で説明が要る |
| f | 3 | R5〜R7 は抄録の名前から当方の定義（:87）。先行の指標（順位・エントロピー）に触れない |
| g | 2 | 版の固定・検査・逸脱はよい。n の根拠と分岐・揃えの組・経路が無いときの扱い・乱数の細部・登録先が未固定 |

## 3. 指摘
1. [major] 揃えの組の集合が文（:108「組は p, q ∈ {1, 2, 3}」）とコード（align.py:8「ORDER = ((1, 1), (2, 1), (1, 2), (3, 1), (1, 3))」）で違う。同点の規則（align.py:3-5）も文に無い。解消: 組を列挙・同点の規則を書く・`max_group` を組の一覧に。自信 高。
2. [major] 全文の照合で候補の本文の末尾が費用なしで余る（:112「記録の最後まで使う」・align.py:4「the text may end early.」）。経路が無いとき（align.py:45-46 ValueError）の扱いが無い。解消: 残りの区間の費用を決める・∞ の扱い・全候補 ∞ の規則。自信 高。
3. [major] 窓の正解（:125）を A2 の揃えで決め、A2 と評価の基準が循環。解消: 攻撃者から独立した基準（A1 の組み立て直しの位置・検査の 3 で一致した書き手）か、偏りを診断で報告。自信 中。
4. [major] 敵の模型（閉じた世界・候補の集合の出どころ・現実の害）が無い（:121-122・:183）。CFP の superficial の逐語。G1・G2。解消: 敵の模型の節・Wagner の分類・閉じた世界を結論の限定に・開いた世界の診断（正解を抜いたときの最小費用の分布）。自信 高。
5. [major] n の根拠と足りないときの分岐が無い（:114 の 125 人・:123 の N・:133 の ENJA15）。課題ごとの人数が書かれていない。解消: [V264] の課題ごとの人数・成り立たないときの規則・k = 50 が作れない記録の扱い。G6。自信 高。
6. [minor] 出力が正答率だけ。解消: top-5・平均の逆順位・書き手ごとの分布（分位点）を副次で固定。G3。自信 中。
7. [minor] 攻撃者の最大による上向きの偏りが区間に入っていない（:160・:130）。解消: ブートストラップの各回の中で最大を取る、または oracle の包絡と固定の攻撃者を区別。自信 中。
8. [minor] 凍結の時刻を第三者が確かめられない（:3）。解消: OSF の registration・Zenodo の DOI に凍結の版を置く。G5。自信 高。
9. [minor] 乱数・道具の版が再計算できるほど固定されていない（:131・:100）。解消: 種の導出の擬似コード・用途名の列挙・SudachiPy と辞書と `romaji_table.py` の版を config に。G4。自信 高。
10. [minor] 除外の規則が 50 語だけ（:37・:67）。欠けた記録・一致しない記録の扱いが無い。解消: 明記。G6。自信 中。
11. [nit] 「記録を使わない予測」が記録の押下の数を使う（:164 と :129）。解消: 「総長だけの攻撃者」と改名。自信 高。
12. [nit] λ = 8 の出どころが無い（:108）。解消: 決め方と出どころを 1 行・感度を副次で。G6。自信 中。

## 4. 総合の推奨: major
- 版の固定・取得の後の検査・結論の限定・全セルの報告はよく、立て直しは不要。
- 揃えの組・候補の末尾・窓の正解は主要な数を直接動かすので凍結の前に直す。
- n の分岐と敵の模型が無く、データを見た後の分岐と PoPETs の範囲の判定に穴が残る。

## 5. 読めなかった範囲・注入
- 読んでいない: 書誌の本体・`.steering/` の decisions.md と下書き・`romaji_table.py`・`synthetic_logs.py`（未作成）・align.py 以外の前の実測。
- wagner2015.txt は :195-224 と :1570-1689 を通読、他は grep。nosek2018.txt は :95-134 を通読、他は grep。
- 注入の疑い: 無し。
