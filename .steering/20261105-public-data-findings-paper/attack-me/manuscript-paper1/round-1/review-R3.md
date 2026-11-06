# review-R3（manuscript round 1・事前登録・同等性の検定・再現性の査読者・応答をメインが保存）

総合: major。注入の疑い: なし。数値は confirm_holdout.json・seed_spread.json と照らし一致。読んでいない: references.bib（grep のみ）・README・deviation-1・notes 2 本・探索の JSON 5 本・文献の記録 2 本・prereg の大部分（P0・A2・C1 の一部と grep）・confirm_holdout.json の 180 行以降（H3 の grep を除く）・kapoor2023 は grep と 331–380 行。

## 接地
- L1 Lakens 2017: "an upper and lower equivalence bound is specified based on the smallest effect size of interest"
- L2 同: "it is expected that equivalence bounds are prespecified ... When in the abstract of an article, authors conclude an effect is “statistically equivalent,” the abstract should also include the equivalence bounds that are used to draw this conclusion."
- L3 同: "Effects can be statistically different from zero and statistically equivalent (Scenario C) when the 90% CI exclude the equivalence bounds and the 95% CI exclude zero."
- L4 同: "An additional nonstatistical challenge in interpreting equivalence concerns the issue of whether an experiment was performed competently"
- L5 同: "the extremely large equivalence bounds will make it clear they can at best reject extremely large effects"
- K1 Kapoor & Narayanan 2023: "Computational reproducibility of a finding refers to sharing the complete code and data needed to reproduce the findings reported in a paper exactly."
- K2 同: "Nonindependence between train and test samples constitutes leakage ... train and test samples come from the same people or units."
- K3 同: "how the test set matches the distribution about which the scientific claims are made"

## 評価表
a 3（題名 "did not anticipate" と貢献の文 "did not distinguish" が強い・3/4 は 0.5 より有意に下〔Scenario C〕・要旨に下向きが無い）／b 3（較正は実効 97/312・取り置きは 50.5/139・推定器の陽性対照なし・帯の根拠は後の換算だけ・学習器の再標本で重複した書き手の fold の割り方が書かれていない）／c 3（手順は再利用できるが公開が未定・害は示していないと本文が書く）／d 3（要旨が重い・データの節に結果の数値・序論に主の結果を再掲）／e 3（コードが置き字・申告の all sections・Replicability）／f 4（網羅的で正確・探索の範囲を開示）

## 指摘
- [major] 題名と貢献の文が、0.5 より下への有意な差を「区別しなかった」と書く: main.tex「did not anticipate code-writing stalls」・introduction「did not distinguish the run-up to a stall from the run-up to a short pause」・results「three of the four intervals exclude 0.5」・discussion「three combinations were statistically different from 0.5 in the downward direction and equivalent」。L3。解消: 題名と貢献の文を「帯 [0.45, 0.55] の内にあった」の型に、要旨に「点推定は 0.5 よりわずかに下（3/4 は 0.5 を外す）」を 1 句。自信 高。
- [major] 推定器が差を検出できたかを確かめていないのに題名と要旨が否定を推定器の性質として書く（limitations・discussion「cannot be told apart from (c)」・abstract「The signals gave no basis for a seconds-scale trigger」・data の 53.7%）。L4。解消: (i) 既知の差を打鍵の流れに埋め込み推定器の差が帯を超えて回収されるかの陽性対照を探索で、または (ii) 題名と要旨に「測りの感度は確かめていない」と明記し "on this reconstructed input" に限る。自信 高。
- [major] 誤って同等とする割合の較正は取り置きより重みの集中が弱い集団で行った（補足「97 of 312 ... 50.5 of 139」・design「We then drew 138 writers」）。解消: 500 回の引きの実効の書き手の分布を報告し取り置きの 50.5 の位置を示す・外れていれば実効の数で層別した率を探索で。自信 中。
- [major] 帯の「conservatively」は向きが逆で SESOI の根拠も無い（design「was set conservatively after we had seen」・limitations「it is not justified as a practical boundary」）。広い帯は同等と言いやすい側。結論は後付けの換算に依る。L1・L5。解消: "conservatively" を削るか「広め（同等と言いやすい側）」と書く・換算を帯の解釈の根拠として前置きしそれが帯を決めた後の [D] であると同じ文に。自信 高。
- [major] 計算の再現性が投稿時点で未成立（abstract・discussion Materials・limitations）。K1・JEDM Replicability。解消: 推定の行と評価のコードを公開し、README に表の 4 値の再計算を書く。自信 高。
- [minor] 「the same procedure applied without change」は CoAuthor と KLiCKe について言い過ぎ（CoAuthor はつなぎ直しと AI の出来事の除外・X6 は付録 F の文言から外れる・X7 で橋渡しを直した・KLiCKe は層なしで境界の型も違う）。解消:「同じ統計量と判定の規則を、データごとの境界と層の定義で当てた（CoAuthor は精度不足）」。自信 高。
- [minor] 取り置きが「before any analysis」に引かれた裏付けが本文に無い（写し方の規則は前の CS1 の分析で決めた・取り置きの種も 20261104）。解消: 前の分析が取り置きを引いた後に除いて行われたことを 1 文と証拠を補足に。自信 中。
- [minor] 学習器の区間で、重複した書き手を fold にどう割ったか書かれていない（補足「Five folds by writer; ... the interval resamples writers and refits」・点推定が区間の上端に寄る 0.567〔0.5497–0.578〕）。K2。解消: 元の書き手の ID で割ったことを明記・上端に寄る理由を 1 文。自信 中。
- [minor] 要旨の学習器の文が主の結論と緊張（abstract「Learners ... could not exclude the upper side of the band. The signals gave no basis」・比べていない）。解消: 「学習器と推定器の信号は比べていない」と添えるか本文へ移す。自信 中。
- [minor] 種の幅の地位 [C-D] がどの走りの値か見えない（探索の X5 で取り置きを開いた後に別に計算）。解消: 補足に「確認の走りの後、条件を先にコミットして別に計算した」。自信 中。
- [nit] 見た書き手の数（319・312・341）の差の説明が無い。補足に 1 文。自信 高。
- [nit] 生成 AI の申告の節の指定と to be confirmed の注記。自信 中。
