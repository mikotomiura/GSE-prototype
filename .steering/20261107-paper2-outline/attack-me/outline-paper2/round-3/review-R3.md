# review-R3（outline round 3）
接地: Hoffmann ら 2021 "the traditional confidence interval ... which only takes into account sampling uncertainty, is inadequate in capturing the true uncertainty in the estimate."・"select the final analysis strategy based on the 'nicest' result: a smaller p -value, an effect in the 'desired' direction ... This 'selective reporting' can lead to a substantial overestimation"・"statistical inference within exploratory analyses should be interpreted with great caution"・"(4) report the results of alternative analysis strategies ... (5) acknowledge the inherent uncertainty in your findings (6) publish all research code, data and material"・Kapoor & Narayanan 2023 "computational reproducibility (the lack of availability of code, data, and computing environment to reproduce the exact results reported in the paper)"・"leakage can result from a difference between the distribution of the test set and the distribution of scientific interest."
carryover 8 件: 7 件解消・M1 は一部（新しい機構の主張が入った）。不採用 2 件は釣り合う。
評価表: a 2・b 3・c 3・d 4・e 4・f 3。
指摘:
- [major] M-A 主張の要の機構が事後の [記述] の 0.93 に乗り、先に置いた読み方の結論（符号の入れ替わりが残る）が脇に置かれた（Hoffmann の 'nicest' result・exploratory）。解消: 機構の部分を [記述] の強さに・強さを範囲（確立）と機構（探索的）に分ける・先に置いた読み方の結論を 4.1 に逐語で。自信 高
- [major] M-B 0.93 は独立の証拠にならない（偏相関が小さいことの言い換え）。流暢さは得点と 0.62 で成果物の側の量かもしれず、固定は媒介や同じ構成概念の除去かもしれない。分母の共有による機械的な結合も切り分けていない。解消: 0.93 を独立の根拠に数えない・流暢さを「停滞の率と重なる量」として扱う理由・限界 6・推奨 1 を弱める。自信 中
- [major] M-C 機構の新しさが外枠の引く Guo ら 2020 と衝突（固定の閾値が遅さを含むことは先行の論拠）。解消: 新しさを対象（定義の空間で関連の範囲を区間つきで出した）に限る・機構は「Guo ら 2020 の論拠を定義の空間で数で確かめた」。自信 高
- [minor] m-1 固定後は「縮む」でなく多数が正に寄る（中央値 +0.058・+0.038）。解消: 中央値と族ごとの正負。自信 高
- [minor] m-2 0.93 が名前つきの集計の出力に無く、相関の種類も無い。解消: スクリプトにし JSON に名前つきで・S3。自信 中
- [minor] m-3 C4 の「残る」はどのデータでも起きやすい形の可能性・推奨 3 の一般化。解消: 何なら変わりえたかを書く・推奨 3 を CS1 の 2 データに限る。自信 中
- [minor] m-4 「4 倍」は 0 に近い基準に対する比（基準の区間の両端で 2.7〜7.4 倍）。解消: 差か範囲で。自信 中
- [nit] n-1 基準の定義が KLiCKe の得点を見て決まったかを 3.2 に 1 文。自信 低
総合: major（範囲は確立・機構は探索的と分ければ計算を足さずに minor の見込み）。
読めなかった範囲: 条件 3 つ・results の多く・カード 3 枚・round1_extra の中身。注入なし。
