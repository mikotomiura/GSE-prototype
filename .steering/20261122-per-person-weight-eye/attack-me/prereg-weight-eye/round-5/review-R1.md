# R1 査読 round 5（打鍵の生体認証の立場）

## 接地
- Teh 2013 "More importantly keystroke dynamics are to behavioral biometrics where variability of typing is expected appear across different sittings"／"Therefore, several sessions of data collection would ideally leverage one's typing evolution."／Shadman 2025 "There was at least a one-day gap between successive sessions to reflect the temporal variation in typing of the subjects."
- Teh 2013 "If keystroke template remains unaccustomed to the gradually shift of typing pattern over time, system accuracy will be degraded over time."
- Teh 2013 "Compliment neglected information in earlier reviews [ 6 – 8 ], such as data acquisition methods, experimental settings, template retraining, outlier handling, and feature quality control."
- Shadman 2025 "Using an individual threshold was better than using a global threshold for computing the EER"／"the consequences of some other factors like differing amounts of samples needed to develop the model, individual or global threshold, the database size, etc."
- Teh 2013 "Genuine and Imposter Samples Data collected will eventually be used for performance evaluation."／"Development of homemade dataset may cater to individual experimental needs; however, experiment result cross-comparison between different methodologies employed may not be conclusive."／"A sample size of at least 100 or more should be an initial aim."

## 引き継ぎの判定
1・2・4〜7 解消（門の検出力・分散の比・λ_ρ を検算）／3 一部（添えると決めた g1 が漂いの筋で働かない・指摘 1）

## 評価表
a 4／b 4（指摘 1・2・3）／c 3／d 3（乱数の鍵の全体を 1 か所で引けない）／e 投稿先未定／f 3（閉じた集合の評価・指摘 4）／g 4（指摘 3・1）

## 新しい指摘
- 1 [minor] 漂いの筋の g1 は作りの上でほぼ 0 になり、ρ ごとの対数の空間の振幅を測れない（安定した差 0・draw_D の期待値が C0・当てる側と評価の側を独立に空回し）。解消: 漂いの筋だけ別の量を事前に定義（(i) 同じ E の道の中で当てる側と評価の側を分ける、または (ii) 単位ごとの 1 状態の表と m0 の表の間の対数の空間の偏差〔π で重みを付けた行ごとの KL の中央値〕）。今の g1 が漂いでほぼ 0 になることを 1 文。自信 高。
- 2 [minor] 間を空けたセルの基準を通ると「分けられた」という肯定の主張になるのに検出力が無い。500 複製で 34 以下なら通るので、真の率 8% でも約 18%、7% なら約 40% で通る。解消: 7%・8%・10% で通る確率を書き「この作りの漂いで偽陽性の膨らみを検出しなかった」に言い換える、または上側の信頼限界の基準に変える。自信 中。
- 3 [minor] CS1 の長さが系列ごとか単位ごとか曖昧（sens の SHAPES は cs1 が nseq=2・L=(5000, 8000) で系列ごと・synth.py L26・L158）。解消: CS1 は系列ごとに引き 1 単位は 2 系列と明記、U{2500…10000} と r_w の掛け方も系列ごとと書く。自信 高。
- 4 [nit] 評価はパネルの中の閉じた集合で、登録外の他人は使っていないことを限界として 1 文。自信 中。
- 5 [nit] 振幅を揃えた漂いは λ_ρ ≤ 1 から ρ ≈ 0.93 までしか作れない。より遅い漂いと分けていない理由として 1 文。自信 高。

## 総合の推奨
minor（直してから凍結）。引き継ぎの 7 件のうち 6 件が解消。残りは定義と文の直しで閉じ、設計の組み直しは要らない。

## 読めなかった範囲
SEED、sens の conditions.md・notes.md・pinned.py・calibration.json、ten・nfs の記録、data.py・ml.py・hmm2.py、supplement.tex、接地の全文。ハッシュ・ml.non_eval・論文 3 の数は照合していない。注入の疑いなし。
