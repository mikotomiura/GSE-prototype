# review R3（manuscript round 4・事前登録・同等性の検定・機械学習の再現性・メインが要約して保存）

推奨: **minor**。接地: Lakens 2017（"equivalence bounds are prespecified ... the abstract should also include the equivalence bounds"・"we can conclude equivalence for a specific operationalization of a hypothesis ... Confounds can underlie observed equivalent effects."・"Researchers should report effect size estimates in addition to hypothesis tests."）・Kapoor & Narayanan 2023（"The burden of proof ... is on the researcher making the scientific claims"・"cannot be verified in the absence of computational reproducibility"・"the test set is drawn from the distribution of scientific interest"・"uncertainty quantification are important steps towards reproducibility"）から逐語。評価 a4・b4・c3・d3・e4・f4。confirm_holdout.json・explore_round3.json・explore_positive_control_v2.json と照らした範囲で一致。

引き継ぎの判定: M1 解消／M2 解消（並列 7 の初回の不一致は estimator/README 77-80 にだけあり原因は状況だけ → 下の m5。本文に書く必要はない）／m3 解消／m4 解消／m5 一部（弱まったが X17 の文が読み方を越える → 下の m1）／m6 解消／m7 解消（括弧の数え方 → nit）／n1・n2 解消。

指摘:
- [major] 結論と考察の主文が登録の但し書きを落とす: conclusion 4-5・discussion 4-5 の主文に偽同等率の但し書きが無い。limitations 24-25 は「the preregistration requires this qualification in the main sentence wherever it appears, including the abstract」と書き、事前登録（prereg-draft.en.md:18）は "This qualification is not dropped in the paper's abstract either"。→ 結論と考察の主文に但し書きを付ける（勧める）か、限界の「wherever it appears」を守っている範囲に改める。自信 高。
- [minor] X17 の解釈文が事前の読み方「間 → 値だけ」を越え、s − u > 30 s の 118 行（どちらにも入らない・3,426 + 1,057 ≠ 4,554）を書いていない。→ 結果は値だけ、帰属は条件の外の解釈と断って考察に 1 回、118 行の扱いを補足 S2 か括弧に。自信 高。
- [minor] 尺度の床と天井の記述が片側: results 189-190 は φ3・φ5 を天井の側（35%・17%）で書くが、u で φ5 の床 53.7%・φ3 の床 32.3%。要旨は「floor」だけ。→ 4 成分の u と u − 30 s の床と天井を補足に表で、本文は数で守れる言い方に、要旨は「at their floor or ceiling」に。自信 高。
- [minor] 陽性対照の表が条件の水準の一部（×1.05・×1.2・r = 0.02・0.1 を落とす）でそのことを書かない。同じ JSON で摩擦の軸の水準（ewma_x）は r = 0.1 で 0.598（0.591–0.607）と帯を越えるのに 30 秒の変化は 0.530 — 推定器が鈍いのか差を取る構成が鈍いのかを分ける材料を出していない。→ 補足に全水準 × 4 量 × 対照の 2 版の表、本文の表題に「selected rows」、考察に差と水準の応答の違いを 1 文。自信 高。
- [minor] 推定器の門の初回（並列 7）の 9 件の不一致の原因が確かめられていない（estimator/README 77-80）。→ README に「cause not established」と書くか、差の中身を 1 行。本文は変えなくてよい。自信 中。
- [minor] 回し直しのバイト一致は著者の 1 環境（macOS arm64）。→ 本文に環境を添え、README に一致しないとき確かめるものを 1 行。自信 中。
- [nit] Materials の「three of which (...)」の括弧が 2 項目に読める。自信 高。
- [nit] conditions-summary.md の round 3 の確かめの節だけ最初のコミットの時刻が日付止まり。→ gse-commits.tsv の時刻を。自信 高。

読めなかった範囲: kapoor の 740 行目以降・references.bib・papers の README・逸脱・notes と conditions の原文（要約で読んだ）・多くの JSON・文献の記録・事前登録の 41 行目以降・組版した PDF。注入の疑い: なし。
