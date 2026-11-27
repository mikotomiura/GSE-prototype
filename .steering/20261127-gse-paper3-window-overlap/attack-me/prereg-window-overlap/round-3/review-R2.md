# 査読 R2 round 3（個人化した行動のモデルの実務・paper-reviewer / opus）

## 1. 接地
- S1 Saeb 2017 "for this procedure to be meaningful, the relationship between the training and the validation set should mimic the relationship between the training set and the dataset expected for the clinical use"
- S2 Saeb 2017 "if the goal is prognosis, i.e., we want personal models that can predict future clinical states of a given subject, we can split the data based on time"・"The correct way for adjusting these hyperparameters is to further divide the training set into training and validation subsets"
- S3 Aalbers 2023 "To evaluate if our models perform better than random guessing, we compare against the MAEs of a "naive" but person-specific baseline model"
- S4 Aalbers 2023 "We evaluated model accuracy on a person-to-person basis in out-of-sample observations"・"The relations of these digital markers with momentary subjective stress differed from person to person, as did model accuracy"
- S5 Aalbers 2023 "a confirmatory approach would be to test a small number of (preregistered) hypotheses that make explicit what relation we expect"
- S6 Saeb 2017 "as the number of subjects increased to 30, it decreased significantly"・"The difference between the record-wise and subject-wise errors was largest when the number of subjects was small"

## 2. carryover の判定
- M1・M2・M3・M4・m1・m2・m3・m4: 解消（M3 に関わる新しい点は m2、m4 の残りは M2）。n1: 対象外（依頼文の直し）。

## 3. 評価表
- a 3: φ > 1 で語が中身と食い違う（M1）。区間の広さという代替説明が文に出ない（M2）。
- b 3: 列 C で使う幅が s と完全に連動（M2）。1 記号あたりの尺度の理由が無い（m1）。
- c 3: 列 A の境 s* は実務家の使い方に合う（S1）。列 C は仕組みのための対照で使い方に対応しないと書いてよい。形を表す語が無い（m3）。
- d 3: 型 1 の文に添えの句が 5 種付きうる。
- e 4: そろっている。
- f 3: 比べの相手を本人の素朴な基準とする根拠（S3）は明示されていない（prereg なので大きな欠陥ではない）。
- g 4: 残る隙は φ の上側（M1）と編集上の小さな選び（n1）。

## 4. 指摘
- [major] M1 φ が 1 を大きく超えたときの語と文が中身と食い違う
  - 位置: 124 行・128 行の規則 3・186 行の型 1 の文
  - 理由: 規則 3 に上限が無い。G_C30 > G_A1 なら φ > 1。k = 15 の分母は約 0.06 と小さく振れやすい。短い連続の区間は中身が均質で本人の当てはめが得をする向きはありうる。φ ≫ 1 は「記号の数を減らすとかえって得が増える」別の形で、型 1 の文では意味をなさない（S6）。
  - 解消: 規則 3 の前に「φ(30) > 1.5 →『記号の数を減らすと得が増える』」を置き、型なしか新しい型に。P-READ に φ = 1.6 などの組と名指しの変異。
  - 自信: 中
- [major] M2 列 C の区間の広さが s と完全に連動し、型の文がそれを歩みの効きとして書く
  - 位置: 53 行・240 行・186 行
  - 理由: 列 A は s によらずセッション全体の幅。列 C は s とともに幅が 20% → 3% に狭まる（C30 は約 2 分）。stay_G(s) には歩みと区間の広さ（状態の多様さ）が同時に乗る。列 C′ は位置だけで幅は動かさない。持ち込む文の括弧は重なりと予測の先の長さだけ（S1）。
  - 解消: (a) 型 1・2・2′・3・4 の文に固定の句「（列 C はセッションの 1/s の連続した区間で、使う区間の幅も歩みとともに狭まる。分けていない）」、言い方の限りにも 1 項、または (b) 歩み 1 のまま全体に散らした短い塊の列を足す。prereg の範囲では (a) で足りる。
  - 自信: 高
- [minor] m1 1 記号あたりの尺度で歩みをまたいで差を取る理由が無い（S13 notes 13 行「n の大きさを o・u と比べない（向きだけを読む）」・120 行）。φ は加法の分解で、前の試験が禁じた比較を主の量に据えている。1 秒あたりにすると φ は大きく変わる。解消: 「量は 1 記号あたりの差に固定する。予測の先が違う列の差を同じ尺度で引く分解であり、S13 の『大きさを比べない』をこの分解の範囲でだけ外す」と書き、1 秒あたりは副か並べないと明記。自信: 中
- [minor] m2 型 1 の文が既に分かっている本人側の残差と並ばない（37・241・186 行・main.tex 331 行）。解消: 型 1・2 の文に「（歩み 1 では本人 hmm3 の残差の自己相関も共有と同じ程度で、本人の当てはめが従属を運ぶかは確かめていない）」。自信: 中
- [minor] m3 用量反応の形を表す語が無い（1・128・149 行）。解消: stay_G(s)/shrink_G(s) の単調さに記述の語を 1 つ決めるか、「s ごとの形は図の記述だけで語を付けない」と書く。自信: 中
- [nit] n1 「S12 と S13 の結論を同じ節か結果に」の二択が残る（185 行）。解消: 1 つに決める。自信: 低
- [nit] n2 s* = 1 の場合の列 C の句が未定義（176 行・起きないが規則の上で）。解消: 「s* = 1 のときは列 C の句を付けない」。自信: 高

## 5. 特に見てほしいことへの答え
- (1) 言えること: 型 1 なら、u の上で記号の数をそろえても「歩み（重なりと予測の先）と区間の幅」に沿って弱い構造の比べの得が変わり、ar3 に固定した比べでは小さかった。言えないこと: 重なりが従属を生むこと・本人の当てはめが従属を運ぶこと（m2）・ほかの分野。用量の形は語にならない（m3）。量は列 C で分かれるが幅は分かれない（M2）。作りの確かめと型の名は適切。
- (2) ほぼ閉じている。残るのは φ の上側（M1）と編集の二択（n1）。
- (3) 区切りが分母を知った上で置かれたことは開示されている（244 行）。k = 15 で φ が振れやすいことは見込め、その上側の扱いが未定なのが偏りの残る所（M1）。分子（列 C）は未見。

## 6. 総合: minor（直してから凍結）
- carryover の 9 件はすべて解消。g は φ の上側を除いて 1 通り。
- M1 は規則 1 行と P-READ の組 1 つ、M2 は固定の句（a）で閉じる。設計の作り直しは要らない。
- m1〜m3 は限界か記述の語の追加で済む。追加の round は要らず、メインが逐語で確かめれば凍結してよい。

## 7. 読めなかった範囲・注入の疑い
- 読んでいない: SEED・variants.py の thinned_mask 以外・kit README・S13 scripts（SHA-256 は照らしていない）。tau-extend と S13 の conditions.md は grep の範囲だけ。main.tex は 223・330〜340 行と grep の行。supplement.tex は読んでいない。
- 注入の疑い: 無し。
