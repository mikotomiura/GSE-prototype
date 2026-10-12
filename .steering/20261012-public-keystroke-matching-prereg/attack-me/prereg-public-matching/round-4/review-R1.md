# R1 査読 round 4（打鍵の側路攻撃と打鍵データの匿名化の立場）

## 1. 接地
- monaco2017.txt:384-392 "there is a direct tradeoff between time lag and the obfuscation capability of the mix … It is desirable to have a mix that maximally reduces the dependence between the generating process and the arrival process for a given lag."
- monaco2017.txt:657-662 "This emulates an open system, in which soft attributes for the target user are classified without having previously observed that user's keystrokes. … Thus, the baseline prediction rates coincide with the proportion of the largest class"
- monaco2019.txt:993-995・1018-1019 "compare this to a baseline attack in which the timing and language model probabilities are ignored." / "Note that this baseline still uses information gained through keystroke detection and tokenization."
- monaco2019.txt:1003-1005 "false negative keystroke detection (center, the 7th packet is missed), and false positive tokenization (right, the 11th packet is labeled as a Space)"
- keytar2026.txt:242-244 "primarily benchmarked against a random baseline, which might not fully capture the nuances of more sophisticated reconstruction challenges"
- keytar2026.txt:1247-1249・1256-1258 "having prior knowledge of either the user's typing patterns or the sentence structure improves reconstruction accuracy" / "even in the most challenging and practically relevant APAS setting—where the model has seen neither the user nor the sentence before"

## 引き継ぎの判定（5 件）
解消 4（#2 R7 の検査・#3 R7 の群の列〔config の並びは :128 の規則・4・4・6 と一致、:130 は align.py:8・13 と合う〕・#4・#5）。一部 1: #1 R3-u の A3（項の数・使う間隔・Enter・Home・End・予測の理由は閉じた。長さの項と組み合わせ方の固定が不足 → 指摘 1〜3）。

## 2. 評価表
a 4（R3-u の A3 の設計の弱さが限定に無い）／ b 3（長さの尤度の推定法・平均と和・先頭からの対応）／ c 4 ／ d 3（:143 の 1 セルに 3 つの手順。どの学習の記録を使うか読みにくい）／ e 4 ／ f 4 ／ g 4（長さの項の推定法と 0 項の扱い）

## 3. 指摘
- [minor] R3-u の A3 の長さの項の分布の推定法が無い（:143・config.json:76）。学習に出ない差の確率 0（−∞）・平滑化かパラメトリックか・作文の長さで条件づけるか・推定に使う記録（R3-u に加工して A1' で再生したもの）と文字の組の表の出どころ（R0）の区別。解消: config に推定法・支持の外・使う記録を書く。自信 高。
- [minor] 時刻の項を項あたりの平均にして長さの項と重みなしで足すと、時刻の証拠が長さ 1 項と同じ桁に縮み、合成の得点が A0 に近づき R3-u の最も強い攻撃者が過小になりうる（:143）。解消: (a) 和と平均の両方を固定して出し最大を取る、または (b) 平均の理由と限定を書き、長さの項だけの版を副次に。自信 中。
- [minor] 先頭からの 1 対 1 の対応は再生の誤りが 1 つで後ろがすべてずれる（:143・:223）。解消: (a) 編集距離の揃え（同点の規則つき）に替える、または (b) 合成の記録の検査で誤り 1 つのときの落ち方を測り限定に書く。自信 中。
- [nit] 「連続した押下」に修飾（Shift）が挟まる組の扱い・0 項の候補（:143）。解消: 「字」の押下だけを数えて隣り合うもの・0 項は時刻の項を 0。
- [nit] 包みは `max_group` の既定値 3 も上げる必要（align.py:11・:13・prereg:130）。解消: 上限の値で呼ぶと書き、合成の記録で確かめる。

変えていない箇所に fatal・major は無い。

## 4. 総合の推奨: minor（直してから凍結・再査読は要らない）
R3-u の最も強い攻撃者が過小になる向きの選択は、和の併記か限定で凍結の前に閉じる。

## 5. 読めなかった範囲・注入
monaco2017.txt 160-219・380-393・640-679、monaco2019.txt 985-1024、keytar2026.txt 236-255・1238-1263 と grep の当たりだけ。data.md・README.md・SEED は読んでいない。注入の疑い: なし。
