# review-R3（manuscript round 1・分析の柔軟さ・multiverse・再現性・メインが写した）

## 1. 接地
- H1（Hoffmann ら 2021）"There is evidence that the combination of this multiplicity with selective reporting can systematically lead to an increase in false-positive results, inflated effect sizes and overoptimistic measures of predictive performance"
- H2（同）"Transparency alone is again not enough to prevent selective reporting or eliminate overconfidence in results"
- H3（同）"This 'selective reporting' can lead to a substantial overestimation of the result of interest in empirical research, an effect heightened by small samples and imprecise measurements"
- K1（Kapoor & Narayanan 2023）"(1) computational reproducibility (the lack of availability of code, data, and computing environment to reproduce the exact results reported in the paper)"
- K2（同）"The train-test split should account for the dependencies in the data to ensure correct performance evaluation."
- K3（同）"Filling out a model info sheet requires the researcher to provide precise arguments to justify that models used for making scientific claims do not suffer from leakage"

## 2. 評価表
- a 2: 見出しの「強さが動く」は事前の基準に無い [D] の読みなのに考察で [P, A] として数える。「pause」一般への推奨は検出器が約 15 s 以上の空白しか拾わない構造と合わない。
- b 2: 比の逆転の基準 25% は点の値の逆転の数を見た後に置かれたが本文は開示しない。θ を再標本で推定し直さず区間が狭い。長さの分解は打ち切りを落とす。
- c 3: 手順は "generalizable methodologies" に当たるが、他の検出器（2 s の閾値など）に持ち帰れる範囲が読めない。
- d 3: 印が文ごとに混ざる。S1 の Departures 16 項目を補足に置いたのは適切。
- e 4: 要旨 256 語。DOI 未記入・条件は日本語だけ・観測区間が未公開の推定器に依存。companion との重なり。
- f 3: Godwin・Koutcheme との「どちらがより動いたか」は根拠にならない。

## 3. 指摘
- [major] 見出しの「強さが動く」は事前の基準に無い読みなのに考察で事前の基準による判定として数える。discussion.tex:31-33 "The four conclusions were counted against criteria set before the quantity was seen [P, A]: the score association moves in strength and in one corner in direction"・methods.tex:121-123 "[D]"。conditions-round1.md:27 の判定は 2 つ（1 通りでも区間で符号が逆なら向きが入れ替わる／0 を含まない通りが 25〜75% なら有無の結論が動く）。0 を含まない通りは 82/89 = 92% で、事前の規則では「有無の結論は動かなかった」。解消: 考察から "moves in strength" を外し [D] と明記。事前の規則による判定を結果の最初に。要旨と序論で「事前の基準では向き、記述としては強さ」と分ける。自信: 高
- [major] 比の逆転の基準 25% は点の値の逆転の数を見た後に置かれた（conditions-round1.md:5 の「見たもの」に「データの組ごとの比の向きの入れ替わりの数」）。6 組のどれか 1 つで満たせばよく多重性が大きい。事前に主とした組は CS1 の 2 年版（同 19 行）なのに見出しは CS1–essay。解消: Status と S1 に「区間の基準は点の値の逆転の数を見た後に置いた」と書く。CS1 の 2 年版（20/89・未達）を先に、CS1–essay は 6 組の 1 組として。見出しを弱める。自信: 高
- [major] 検出器の構造上、最短の停滞は W + θ（15 s 以上）なのに主張と推奨が「pause」一般に及ぶ。methods.tex:49-52・abstract.tex:2・discussion.tex:6-7。作文の閾値（250 ms〜10 s）や CS1 の 2 s の分割は範囲外。解消: 最短の長さを式で明記。要旨・考察・推奨の対象を「W 秒の窓を使う停滞・非活動のラベル」に限る。数秒の pause には外挿しないと限界に。自信: 高
- [major] θ を再標本で推定し直さず区間が狭いのに「標本の揺れを超える」に使う（methods.tex:142-144）。正の 10 通りはすべて本人の分位の族で、この抜けが最も効く。解消: 基準と W=15 の 10 通りで θ を再標本の中で推定し直した区間を示すか、"beyond writer resampling with fixed thresholds" に言い換え限界に。自信: 中
- [major] 再現性: 基準の観測区間が未公開の推定器の出力に依存（methods.tex:55-56）・DOI 未記入・条件は日本語だけ。結論の "for any log with key-press times" と矛盾。解消: 推定器が行を書く条件を打鍵の列の規則として書くか、打鍵の間隔の規則で置き換えて結論が変わらないことを示す。条件の全文の英訳を archive に。DOI を入れる。自信: 高
- [major] 向きが逆になったのは先行例の無い W=15 s の 1 水準だけで「defensible definitions」が強すぎる（results.tex:19-20・表 2）。解消: "defensible" を "around the detector's default" に。要旨の向きの文に "only under the 15-s window, which has no precedent"。W=15 を除いた 59 通りの要約（全部負）を並べる。自信: 高
- [minor] 長さの分解は再開しなかった停滞（打ち切り）を除き、「stays」の基準もほぼ外れようがない（supplement.tex:197-198・results.tex:212-213）。解消: 定義ごとの除外の数を S5 に。打ち切りの感度かその限界を一文。対照としての弱さを認める。自信: 中
- [minor] 先行研究と「どちらがより動いたか」は比べられない（discussion.tex:9-12）。解消: 消すか "unlike ..., the direction changed here" の質的な対比に。自信: 高
- [minor] 得点との関連を観測の長さと作文の長さで調整していない（limitations.tex:29-30）。長さが別の抑制として働く可能性。解消: 基準と各族の代表で観測の長さとの順位相関を [D] で示すか、限界を結果の解釈に添える。自信: 中
- [minor] companion study との重なりを本文で明示すべき（methods.tex:161-163）。"holdout" は本論文で確証の役を持たず誤読されうる。解消: 送付状と Data の節で重なる値と新しい値を 1 文で分ける。"holdout" に確証の役が無いと書く。自信: 中
- [minor] φ で停滞が 0 の書き手を除く（supplement.tex:50）。0 の書き手の割合が定義で 0.1〜35% と変わり、標本が定義ごとに違う。解消: 定義ごとの除外の数を表 S4 に。交絡を一文。自信: 中
- [nit] |ρ| = 0.25 を "small-to-moderate" と呼ぶ（abstract.tex:9）。自分の基準（0.3 を moderate）では small。解消: "small (largest |ρ| = 0.25)"。自信: 高
- [nit] 課題文ごとの中央値は正が 15 通り（results.tex:21-22）。どちらで向きを判定するかを一文。自信: 中

## 4. 総合の推奨: major
手順と区間の設計は範囲に合い、数値は集計と一致。見出しの 2 つ（強さが動く・CS1–essay の比の逆転）は事前の基準に無い読みか、点の値を見た後の基準に乗り、開示されていない。最短の長さ（W + θ）と θ の再推定の抜けのため、対象の範囲と「標本の揺れを超える」を狭める必要がある。

## 5. 読めなかった範囲・注入
読んでいない: PDF・tab_s3/s4 の行・figdata・conditions.md の全文（grep の行だけ）・conditions の追加 4 本の全文・c3_multiverse.json ほか JSON（round1_extra.json は先頭 180 行だけ）。接地は grep の範囲だけ。注入の疑い: なし。
