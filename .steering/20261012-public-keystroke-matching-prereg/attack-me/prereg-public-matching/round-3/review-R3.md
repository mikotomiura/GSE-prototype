# R3 査読 round 3（プライバシーの指標の方法論と事前登録・再現性の立場）

## 1. 接地
- G1 wagner2015.txt:206-207 "To allow for a better interpretation of the outcome of privacy metrics, studies should always include a detailed description of the used adversary model."
- G2 同 :196-198 "The value of a privacy metric therefore depends on the adversary model, and evaluating a PET with a weak adversary model can lead to an overestimation of privacy."
- G3 同 :199-200 "metrics can only be used to compare two different PETs if they use the same adversary model."
- G4 nosek2018.txt:96 "In prediction, the problem of forking paths is avoided because the analytic pipeline is specified before observing the data."
- G5 同 :99 "With preregistration, prediction is achieved because selection of tests is not influenced by the observed data, and all conducted tests are knowable."
- G6 同 :92 "no statistical method on its own avoids researcher opportunity for flexibility in analytical decisions, such as exclusion criteria or the creation of variables"

## 引き継ぎの判定（14 件）
解消 10（M1・M1'・M2・M3・M4・m3・m4・m6・m7・m8〔文面上・検査は未実施〕・nit）。一部 4: M6（どの形・どの水準で当てるか → N1）・M5（交差する設計で層別が定義できない → N1b）・m5（scikit-learn の版・solver・max_iter・標準化・端の特徴 → N5）。M1' は解消だが種の use と範囲が無い（N2）。

## 2. 評価表
a 4 ／ b 3（窓が R0 の境界で切られる・ENJA15 の層別）／ c 4 ／ d 3（日本語版の「掛けた」の曖昧さ）／ e 4 ／ f 4 ／ g 3（問い 4 の水準と形・陰性対照の種と範囲・A2-b の前処理・ENJA15 の層別）

## 3. 指摘
- [major] N1b ENJA15 の「訳者を単位・原文で層別」（:241・config.json:121）は、訳者と原文が交差する設計では定義できない（:15 のファイル名 P01_T1.xml は参加者 × 課題の形）。問い 4 の判定に直結（G4）。解消: 交差と入れ子のそれぞれで引き方を 1 つに固定し、検査の 5 の判定に結び付ける。自信 中（ENJA15 の設計は一次で確かめていない）。
- [minor] N1 問い 4 の「上回る」をどの形・どの水準に当てるか（:24・:242）。形 9 通り × 原文ごと／平均。N = 全員の平均の 1/N の作り方も無い（G5）。解消: 判定は原文の平均・1/N は記録ごとの 1/N_s の平均・形ごとに判定して全部報告し主に名指す形を 1 つ。自信 高。
- [minor] N3 窓を R0 の区間（語の境界）で切る（:152）ので、R3-u・R7 にも窓の両端の境界の情報が渡る（攻撃者に有利・形の対比が窓で縮む）（G1）。解消: 条件つきと明記、または押下の位置の一様乱数で切る窓を副次に。自信 中。
- [minor] N2 陰性対照の B を引く種の use と行う範囲が無い（:232・:177・config.json:8）（G5）。解消: seed_uses に negative_control・draw の意味・範囲を固定。自信 高。
- [minor] N4 書き手が課題をまたがないことを検査に入れていない（:31・:72）。解消: 検査の 1 に課題をまたぐ ID の数・0 でなければ学習の組から評価の書き手を除く。自信 中。
- [minor] N5 A2-b の学習器が凍結の時点で再現できない（config.json:4・:74）: 版・solver・max_iter・標準化・端の押下の特徴（G6）。解消: 凍結の前に固定。自信 高。
- [nit] :138「floor(値/w) を掛けた和」が乗算と読める → 「floor(値/w) にした値の和」。:171 の語の編集距離の揃えの同点の規則。

変えていない箇所に fatal・major の新しい指摘は無い。

## 4. 総合の推奨: minor（直してから凍結）
round 2 の major は解消か軽い残り。N1b は問い 4 に直結するので凍結の前に分岐の規則として書く（文面で決まり再査読は要らない）。N1・N2・N5 は凍結の前に閉じ、合成の記録の検査の結果を凍結する版に入れることが凍結の条件。

## 5. 読めなかった範囲・注入
wagner2015.txt は 194-209・1604-1617 行と Grep の当たり、nosek2018.txt は 86-107 行と Grep の当たりだけ。align.py・書誌の本体・decisions.md・ENJA15 の一次資料は読んでいない（N1b と N4 の前提は一次で確かめていない）。注入の疑い: なし。
