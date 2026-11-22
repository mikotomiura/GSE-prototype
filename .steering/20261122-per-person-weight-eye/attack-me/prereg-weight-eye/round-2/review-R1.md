# R1 査読 round 2（打鍵の生体認証の立場）

## 接地
- Teh 2013 "sample collection can be divided into several sessions over a period of time, thereby not only reducing the initial load but also reflecting typing variability"／Shadman 2025 "There was at least a one-day gap between successive sessions to reflect the temporal variation in typing of the subjects."
- Teh 2013 "the greater number of samples collected the more accurate and conclusive a test result can be from statistical point of view."／Shadman 2025 "The authors also considered the consequences of some other factors like differing amounts of samples needed to develop the model, individual or global threshold, the database size, etc."
- Shadman 2025 "Using an individual threshold was better than using a global threshold for computing the EER because an individual threshold is a value specific to a user"
- Teh 2013 "Keystroke dynamics biometrics are subdomain of behavioral biometrics that have the possibility of evolvement over time."
- Teh 2013 "experiment result cross-comparison between different methodologies employed may not be conclusive."／Shadman 2025 "Shared research benchmarks are necessary to truly understand the strengths and limitations of each algorithm and compare them fairly and reliably."
- Teh 2013 "there may be a concern that the result obtained under such control setting may not reflect real world scenario."

## 引き継ぎの判定
1 解消／2 一部（長さは単位ごとに独立で、書き手ごとに続く量の差が無い。揺れの筋は選びにも門にも入らない）／3 解消／4 解消（揺れの筋の差なしは門の対象外）／5〜10 解消

## 評価表
a 4／b 3（N1・N2・N5）／c 4／d 4／e 投稿先未定／f 3（FAR・FRR・EER との対応が無い）／g 4（N4・N3）

## 新しい指摘
- N1 [major] 名札の置換の帰無は、書き手ごとに続く記録の量の差があると交換可能でなくなるのに、合成はその状況を作らないので D6 の門で見つけられない。D4「単位の長さは U{300, …, 1000}」は単位ごとに独立。本人の表の S からの離れ方と列の点数の分かれやすさがどちらも量に依存し、書き手の間で相関するとずれが出る（E3 で特に）。解消: 書き手ごとに長さの尺度を 1 回引く差なしの筋を D6 の門に入れる、量を揃えた層の中で入れ替える、または少なくとも「読まないこと」に書く。自信 中。
- N2 [major] 揺れの筋が選びにも門にも入らない。揺れ 0 で最もよく拾う案が揺れのもとで最も弱いことはありうる。解消: 揺れの筋の g = 0 を D6 の門に明記（CoAuthor の 3 つの k）。選びに入れるか、入れない理由と、選んだ案の揺れの検出力が他より 0.03 以上低いときの書き方を D6 に事前に書く。自信 高。
- N3 [minor] D7(3) の間を空けた対照に合成の門がどう当たるかが未定。CoAuthor k = 15・CS1 k = 5 では空ける余地が無い。解消: 空けられる (k, 空き) の組をいま書き、合成で計算して同じ門をかける、または空けたセルは同じ規則の門を通したものだけを読むと書く。自信 高。
- N4 [minor] V1 が赤で研究者に問うた後の分岐。解消: 直してよいのは実装の誤りだけで D1〜D5 の定義は変えない。新しい code_hash で V1 と変異をはじめから回し、記録を残す。定義を変えるなら新しい版として凍結し直す。自信 高。
- N5 [minor] CS1 のパネル外（3 単位・H = 1）で `ml.non_eval`（ml.py:75）により最後の 1 単位が S から落ち、本文の「評価でない単位」とずれる。解消: S に入る単位を明記し、論文 3 の作りに合わせて決め、小さな検査で数を確かめる。自信 高。
- N6 [nit] FAR・FRR・EER（真の書き手と他人の点数を混ぜた EER）を記述の量に 1 つ足す。自信 中。

## 総合の推奨
minor（直してから凍結）。round 1 の 10 件中 9 件が解消。残るのは記録の量（N1）と揺れ（N2）で、筋を 1 つ足すか門の対象を書き足せば塞がる。N1 を量を揃えた置換で塞ぐなら帰無の定義が変わるので、その部分だけ見直す。

## 読めなかった範囲
SEED、sens の conditions.md・notes.md・synth.py・pinned.py・calibration.json、ten・nfs の記録、hmm2.py、supplement.tex。接地は grep と部分の読み。注入の疑いなし。
