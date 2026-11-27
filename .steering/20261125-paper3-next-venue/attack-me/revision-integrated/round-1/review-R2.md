# review-R2（個人化した行動のモデルの実務・TMLR・round 1）

総合: major。読んだもの: brief-R2・context-A・aalbers・saeb の全文・main.tex 全文・supplement.tex 560 行〜末尾（S13 末尾と S14）。supplement 1〜559 行・figdata・kit README は読んでいない。注入の疑い: なし。

## 1. 接地
- G1（Aalbers 2023）"To evaluate if our models perform better than random guessing, we compare against the MAEs of a “naive” but person-specific baseline model. This “naive” baseline model always predicts an individual's average level of stress."
- G2（Aalbers 2023）"However, these models are not highly accurate, as they often do not outperform a person-specific baseline."
- G3（Aalbers 2023）"Confirmatory research is required to test the robustness of (1) the relation between stress and the potential digital markers identified here and (2) the interindividual variability in this relation."
- G4（Saeb 2017）"for this procedure to be meaningful, the relationship between the training and the validation set should mimic the relationship between the training set and the dataset expected for the clinical use." ／ "if the goal is prognosis , i.e., we want personal models that can predict future clinical states of a given subject, we can split the data based on time"
- G5（Saeb 2017）"Subject identification, which we know to be relatively easy, thus replaces disease recognition, which we know to be hard."
- G6（Saeb 2017）"The correct way for adjusting these hyperparameters is to further divide the training set into training and validation subsets, and then minimize the prediction error on those validation subsets rather than on the whole dataset."

## 2. 評価表
a 3（主の主張は表で支えられる。325 行の 1 文は S14 の限定 2 つ〔頻度だけの基準線がほぼ同じ T・drift と分けられない〕を落とす）／b 3（時間の分割は G4、他の書き手での選びは G6 に合う。取り分けた 30% を使わず探索のまま。主の手順は 3e-2 も確実に検出しないのに S14 は 1e-3 で 0.844 の率で検出し、感度の違いが論じられない）／c 3（本人の連鎖の検査は使える。一言は「HMM3 がこの記号化に合わない」に近く個人化の知見として薄い。見分けられるのに予測が良くならない食い違いが最も一般化できる洞察になりうるが書かれていない）／d 2（造語が多い・要旨が詰まる・S14 は密な散文）／e 3（範囲に入る。題が context-A と main.tex で違う）／f 3（弱い比べの教訓は先行研究に近い。系列モデルに特有の仕組みが深められていない）

## 3. 指摘
- [major] 本文の S14 の 1 文が頻度だけの基準線と drift の限定を落とす
  - 位置と引用: main.tex:325 "In an exploratory check with its reading committed before the data were read (\Sref{14}), in the same CoAuthor records at $k=5$ and in the space of one-state transition tables, a writer's training units ranked on the panel average closer to the writer's held-out units than other writers' training units did."／supplement.tex:585–589 の T と baseline T（0.912/0.941・0.982/0.982・0.996/0.989・0.963/0.960・0.960/0.941）／supplement.tex:576 "Synthetic drift between units ($\rho=0.9$) was detected in all four gap cells, so no cell separates stable differences from closeness in time."
  - なぜ問題か: 本文だけ読むと書き手に固有の遷移の型が見つかったと読める。順位はほぼ周辺の頻度で説明がつき、時間の近さと分けられない。"Neither remainder could be attributed ..." の直後で反証めいて読まれる。G5 の型。
  - 解消の条件: 325 行に「頻度だけでもほぼ同じ順位（baseline T）」と「時間の近さと分けられない（drift）」を足し、"in symbol frequencies and one-state transition tables alike" のように遷移に固有と読めない形にする。
  - 自信: 高
- [major] S14 は "lack sufficient depth" に答えていない。深さの候補（識別できるのに予測は良くならない）を本文が扱わない
  - 位置と引用: supplement.tex:603 "Neither result is used to deny or support the other"／main.tex:302 "No planted level up to $3\times10^{-2}$ was reliably detected (at most 3 of 10 seeds)"／supplement.tex:576 "0.844, 0.998, 1.0 and 1.0 under the second (500 replications each)"
  - なぜ問題か: 仕組み（なぜ利得が消えるか）を深めず、論点を 2 つ増やした（見分けられるのに予測は良くならない・主の手順の感度が S14 より桁で低い）。後者は「帰せられない」が書き手について言うのか手順が鈍いだけかを左右する。G2 の型（相関するが基準線に勝たない）を言葉にしていない。
  - 解消の条件: 考察に 1 段（凍結した読みは変えず本文の記述として）: (i) 書き手は頻度と遷移の順位で高い率で見分けられる (ii) 主の手順はそれを予測の利得に変えない (iii) 感度が桁で違う（S10 と S14）ので「帰せられない」は手順の感度の限界として読む。しないなら本文の 1 文を削り S14 を補足に留める。
  - 自信: 中（S14 と S10 の尺度が同じことは S14 の文面からだけ）
- [major] 取り分けた 30% の書き手が使われず全体が探索のまま
  - 位置と引用: main.tex:116 "Before any analysis, 30\% of each dataset's writers were set aside at random and not read (\Sref{2})."／main.tex:177 "The study consists of four analyses designed one after another and thirteen later checks"
  - 解消の条件: 取り分けの目的を本文に書く。可能なら凍結した最終の手順を 1 度だけ当てて確認として報告。人数が足りないなら数で書き、将来の確認のために残したと明記。
  - 自信: 中
- [major] 見出しの「30 倍以上」は別々の共有モデルに対する差を比べている
  - 位置と引用: main.tex:52 "the per-person gain shown by a same-structure comparison is more than thirtyfold larger than the remainder against a stronger comparison"
  - なぜ問題か: 利得は HMM3 の共有、残りは AR-HMM3 の共有に対する差で分母が違う。比は HMM3 の合わなさについて多くを語る。
  - 解消の条件: 同じ基準（本人の連鎖か共有の AR-HMM3）に対する各モデルの差を 1 行で並べる、または比を「構造を合わせたときの残り」と言い換える。
  - 自信: 中
- [minor] baseline T を並べるだけでは本文の読者には足りない（補足の中では筋が通る）。解消: 本文で事実を 1 文、補足の表の直下に記述の数（例「CoAuthor の各セルで 0.03 以内」）。自信: 中
- [minor] 本文の主な比べに本人の 0 次（頻度）の基準線が無い（main.tex:149）。解消: S11 か表 3 に本人の頻度モデルとの差を 1 行。数を変えない方針と衝突するなら限界に書く。自信: 低
- [minor] 造語が多い（main.tex:145–147 prior mode・smoothing effect、182 shared-only / symmetric refit）。解消: 結果の各節の頭に平易な 1 文、造語を 3〜4 個に絞る。自信: 中
- [nit] 題が context-A と main.tex:29 で違う。自信: 高

## 4. 著者の問いへの答え
1. 補足の中では足りる、本文では足りない。2. 確認の主張に読まれる恐れは小さい（"exploratory" とある）。書き手に固有の遷移の差の証拠として読まれる恐れが大きい。3. 今の置き方では論点を増やしただけ。

## 5. 推奨: major
主の主張は数で支えられ開示は誠実。深さの不足は解消されず、S14 は本文で限定なしに引かれる。30% の取り分けを使わず、比の分母が違う。
