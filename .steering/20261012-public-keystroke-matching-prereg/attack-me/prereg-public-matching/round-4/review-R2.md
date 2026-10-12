# R2 査読 round 4（作文の過程の研究の立場）

## 1. 接地
- klicke2025.txt:707-711 "The mean length of the string of actions delineated by an insertion or deletion exceeding 2 seconds and is measured in characters."
- conijn2019.txt:146-148 "written language bursts are often operationalized as sequences of text production (keystrokes) without an IKI longer than two seconds and without a revision and without an insertion away from the leading edge"
- klicke2025.txt:746-748 "The standard deviation of the production rates for the 10 intervals in each writing process in relation to a task maximum."
- klicke2025.txt:678-683 "we first removed the inactive periods at the beginning ... and the end of the processes ... We then analyzed the truncated logfiles (in .idfx formats) using Inputlog 9.0"
- klicke2025.txt:685-687 "To limit the inclusion of variables to those that are generalizable and facilitate the comparison of keystroke activities among writers, only keystroke measures based on means, proportions, or ratios were selected"
- conijn2019.txt:808-810 "caution should be taken when generalizing the effect of these features across tasks, because these features might differ merely as a result of the task"

## 2. 引き継ぎの判定
解消: major（式。小さな残り m1）・検査 7（新しい穴 m3・m4）・「○」と R3-t・比の分母 0・語の間の休止（nit n1）。一部: 図の縦軸（config:95 の `summary.figure` が "computable metrics" のまま → m2）・「照合と同じ抽出」（config の `utility` に `sample` が 2 回 → m2）。

## 3. 評価表
a 4（task maximum の正規化は課題内の順位相関に効かないことが書かれていない・m5）／ b 3（R0 の削除の長さの単位 m6・正規化の分母 m5）／ c 4 ／ d 3（config の重複キーと食い違い m2）／ e 4 ／ f 4 ／ g 3（検査 7 の種と再検査の手順 m3・m4・重複キー m2）

## 4. 指摘（fatal・major は無し）
- [minor] m6 R0 の「削除の平均の長さ」（config.json:108「R0: mean deleted length from text_change of Remove/Cut and Replace」）は、押下ごとのイベントなら 1 字に寄り、近似（連なり）と単位が違う。Table 5（:728-729）"The mean number of characters deleted in one deletion activity." 解消: R0 も連続した Remove/Cut の連なりの削除字数の平均に。自信 中（粒度は検査 2）。
- [minor] m5 task maximum の分母が形ごとに違い比 (b) を歪める・課題内の順位相関には効かない・「全書き手」の範囲が無い（prereg:188・config:112）。解消: 分母を R0 の task maximum に固定するか、比 (b) は割る前の SD で出す・範囲を明記。自信 高。
- [minor] m3 検査 7 の 50 人の種の use が無い（config:8）・KLiCKe §4.1 の Inputlog の計算は 400 人の部分集合（:674 "Four hundred data entries were sampled"）。解消: `use` = `check7`・「Inputlog の値がある書き手の中から 50 人」・満たないときの扱い。自信 高／中。
- [minor] m4 検査 7 で式を直す手順が開いている（prereg:78）。同じ 50 人で合わせ込みになる。解消: 直す回数の上限・別の種の 50 人で再確認、または再検査しないと明記。自信 中。
- [minor] m2 config の重複キー（:116・:119 の `sample`）と図の縦軸の 2 通り（:95「computable metrics」・:121「fixed set of 10 metrics」）。解消: 分けるか消す・:95 を :121 に揃える。自信 高。
- [minor] m1 R-burst の「2 秒」が config:104 に無い（prereg:188 にはある）。解消: config に書く。自信 高。
- [nit] n1 「字」に区切りが含まれ、語の中・語の間の休止の境目があいまい（config:101・:106・:107）。解消: 語の中は英数字 → 英数字、語の間は区切り → 次の英数字、英字 → 区切りの扱いを書く。

## 5. 総合の推奨: minor（直してから凍結・再査読は要らない）
変えた箇所にも変えていない箇所にも fatal・major は無い。

## 6. 読めなかった範囲・注入
data.md・README.md・SEED・align.py は読んでいない。接地の本文は Grep の節と KLiCKe:670-752・Conijn:140-154・:800-819 だけ。注入の疑い: なし。
