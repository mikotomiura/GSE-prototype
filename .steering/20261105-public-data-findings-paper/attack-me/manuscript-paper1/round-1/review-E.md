# review-E（manuscript round 1・編集者の役・応答をメインが保存）

判定: 直してから回す。読んだ: brief-E・context-A・jedm_about（全文）・mensh2017（Rule 1〜9）・本文と必須の節。補足は読んでいない。注入の疑い: なし。

## 接地
- B1 JEDM: "Accepted submissions should extend beyond mere application and must include elements that contribute to broader knowledge, such as generalizable methodologies or comparative analyses." / "Research should not focus solely on application but must demonstrate how the findings can be generalized or applied across different educational contexts."
- B2 JEDM: "All submissions should present their methodologies and findings in a way that ensures replicability by other researchers. This includes clear descriptions of the data, tools, and procedures used." / "Are the presentation, organization and length satisfactory?"
- B3 Mensh Rule 1: "Focus on a single message; papers that simultaneously focus on multiple contributions tend to be less convincing about each and are therefore less memorable."
- B4 Rule 4: "Only the central idea of the paper should be touched upon multiple times. Otherwise, each subject should be covered in only one place in order to minimize the number of subject changes."
- B5 Rule 5・8: "highlights how this conclusion moves the broader field forward" / "describes how the paper advances the field by providing new opportunities"

## 1 文
言える（手で係数を決めた推定器の 2 信号の 30 秒の変化は CS1 の取り置きで停滞の手前と停滞にならない短い休止の手前を区別しなかった・事前の帯の中。手順を発火の仕組みを作る人に出す）。ただし推定器が誰のもので、なぜ読者が気にすべきかが最初の 2 頁に無い（intro「The signals we test come from a keystroke state estimator」・data「The designer named the states」・出典の引用なし・intro「for estimators of the same type, the result is one instance」）。

## 指摘
- [major] mere application を越える条件を何で満たすかが弱い（intro の部品の段・results「We did not compare the learners with the estimator's signals.」・results「do not contrast it with the unmatched one」）。手順は「他のデータで動いた」だけ。解消: (i) 手順を貢献にするなら既存の検出器・学習器に当て、揃えあり・なしで結論が変わるかを示す比べを足す、(ii) 否定の結果を貢献にするならこの型の推定器が EDM で使われる・使われうる根拠を序論の 2 頁に置く。自信 高。
- [major] 否定の結果が計器の弱まりと区別できないと本文が自認（discussion「The equivalence cannot be told apart from (c)」・limitations「the positive-control gate was applied only to the learners」・data「none of them reached the estimator as key presses」・合成の離し）。Mensh Rule 7 "verify that a method for measurement is valid in the system under study"。解消: 推定器の信号に既知の差を入れる陽性対照を足し結果の最初に置くか、題名と抄録の「did not anticipate」を「この入力では区別しなかった」に下げる。自信 中〜高。
- [major] 再現性の条件が未決（discussion Materials「is to be settled before submission」・limitations「cannot be reproduced from outside」・abstract「[repository to be added before submission]」）。解消: 投稿前に推定器と replay の公開を決め URL を抄録に。自信 高。
- [major] 同じ但し書きが何度も出る: 偽の同等の率 6 か所（abstract・intro・design・discussion・limitations・conclusion）・床 5 か所・帯の事後と 0.01 4 か所・計器の弱まり 2・停滞は stuck でない 2・この推定器とこの入力 3・地位のラベルが結果の文のほぼ全部。解消: 限界にまとめ抄録と序論は 1 句、序論の最後の段落を Rule 6 の型に、ラベルは表と図と節の頭だけ。自信 高。
- [major] 抄録の結論が一般論（abstract「should be checked against a band set in advance on held-out writers」・discussion「our data do not show the harm of omitting the check」）。解消: 確かめたことと分野の次の一歩を分け、後者に根拠の範囲。自信 中。
- [minor] 補足へ移せる細部: 表 1（写し方）と休止の中身の割合・較正の手順の細部・学習器の門の差し替えの経緯・学習器の感度・表の注の 0.025 の帯と考察「The direction below 0.5」・図 1 の 11 行を主と感度 2〜3 行に。Rule 3 "most details of our activities are extraneous"。自信 中。
- [minor] 考察が貢献で締まらない（6 小節・最初の段落の大半が「It does not mean that」・最後が Materials）。解消: Calibration と Reporting をまとめ、最後に「この手順が開くこと」の段落、Materials は宣言かデータ利用の節へ。自信 中。
- [minor] 結果の最初の段落が取り組み方を要約しない（「The holdout gave 4,554 stalls」から始まる）。Rule 7。自信 中。
- [nit] 生成 AI の申告に未確定のコメント（declarations「The tools and sections are to be confirmed by the author before submission.」）。
- [nit] 匿名化しない版（main.tex に著者名と ORCID）。匿名化は任意なので決めるだけ。
