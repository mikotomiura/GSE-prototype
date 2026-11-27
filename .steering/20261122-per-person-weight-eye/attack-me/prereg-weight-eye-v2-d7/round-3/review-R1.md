# R1 の査読（round 3・paper-reviewer の応答の写し）

結論は minor（直してから凍結）。round 2 の 7 件はすべて本文で解消を確かめた。新しく minor 3 件・nit 3 件で、fatal と major は無い。いちばん重い穴は、例外が出ない誤りを結果を見た後に直す道が規則に無いこと。

## 1. 接地
- K1: Teh 2013 "keystroke dynamics are to behavioral biometrics where variability of typing is expected appear across different sittings [ 95 ]. Therefore, several sessions of data collection would ideally leverage one's typing evolution."
- K2: Shadman 2025 "it is assumed that the keystroke samples in the instance of enrollment and verification have an equal distribution, which is not usually the case"
- K3: Shadman 2025 "In order to check whether the model can differentiate between the notion of user and device, two dedicated sessions were carried out by another person (imposter) on the same exact device"／"The results revealed a performance degradation for cross-language in keystroke dynamics"。Teh 2013 "Device freedom refers to whether the equipment used in the experiments is standardized or the users have the flexibility to use their own input devices."
- K4: Shadman 2025 "The IPR (Imposter Pass Rate) improved when the reference profile size increased."
- K5: Teh 2013 "It is collectively agreed that experiments that includes large number of subjects better signify the scalability of study. Regrettably most of the studies performed involve only small number of subjects."／"the number of subjects involved was too small (less than 10) to draw a strong conclusion"

## 2. 引き継ぎの判定
1. M1 解消（76・128・71 行。cs1_spread_summary.txt の値と比の範囲に一致）。
2. M2 解消（77 行）。
3. m1 解消（121・122 行。範囲の値は eq_amounts_summary.txt と 9 行一致）。
4. m2 解消（95 行）。
5. m3 解消（72 行）。ただし例外が出ない場合が抜けている（m-B）。
6. m4 解消（59 行）。
7. nit 解消（76・78 行）。

## 2b. 評価表
- a 4: 文の型はどれも「探索」「補正なし」「揃えの 1 回の引き」を括弧に持つ。(4) の値は supplement.tex 262〜263・181〜182・356・359 行と合う。「出どころは分けていない」は main.tex 49・337 行と合う。0.462 は summary_null1.json の 763 行と合う。拾ったときの文は少数の書き手で決まりうる平均であることを書いていない（m-C）。
- b 4: 機器・課題・止まりの混同は 132 行、漂いは 80 行、量は揃えと範囲の外の印で手当て。残るのは記号化（重なる 30 秒窓）への条件づけ（m-A）と例外の出ない誤り（m-B）。
- c 3: 1 文で言えるが、探索の版なので推奨はほとんど無い（限界として妥当）。
- d 3: 7,816 字。117・119 行の重複。「CS1 の読みの範囲」は (3) から参照されるのに (5) の後。
- e 投稿先未定。
- f 4: 98 行で照合の文献の EER と直接比べないと書く。K1・K3 の系譜に沿う。
- g 4: 自由度が 2 か所: 非検出のときに並べる合成の行の選び（m-D）と例外の出ない誤り（m-B）。

## 3. 指摘
- [minor] m-B 例外を出さない誤りを、結果を見てから直す道が規則の外にある
  - 位置と引用: 72 行「止め: 例外が出たら止め、コードを直して同じ鍵ですべてのセルを回し直す。止めた時点で出ていた量と直した差分を notes に書く。」
  - なぜ問題か: 実データの p や T を見た後に誤りを探して直す道が手続きなしで残る。読み込みのコードは凍結の後に書き、V1 を通っていない。
  - 解消の条件: 「実データの出力の後に例外のない誤りを見つけて直したときは、直す前の全セルの出力を残し、直した差分・見つけた経緯・直した後の出力を並べて notes に書く。判定と文は直した後の値で書き、直したことを同じ所に添える。」
  - 自信: 高
- [minor] m-A 記号化に条件づくことが読みに書かれていない
  - 位置と引用: 63 行・96 行
  - なぜ問題か: 記号は 1 秒ごとに直前 30 秒の窓から作る（main.tex 47 行 "Each second of typing is coded as one of 26 symbols describing the rhythm of the preceding 30 seconds"）。論文 3 は "With non-overlapping windows the direction of a per-person gain returned, so studies should report the symbolization together with the comparison"（main.tex 337 行）。96 行は粗さについてだけで重なりについては無い。
  - 解消の条件: (4) の「添えること」に「E1 は論文 3 の主の記号化（1 秒ごと・直前 30 秒の重なる窓）で数えた。論文 3 は重ならない窓で得の向きが戻ったと報告しており、この目の結果も記号化に条件づく」を足す。
  - 自信: 中
- [minor] m-C 拾ったときの文が少数の書き手で決まりうる平均であることを書いていない
  - 位置と引用: 76 行・v1 conditions.md 24 行
  - なぜ問題か: T は AUC_v の平均で、パネルは 17 人と 23 人なので数人の区別できる書き手だけで拾うことがある（K5）。
  - 解消の条件: 「平均は少数の書き手で決まりうる。書き手ごとの AUC_v の分布（記述）を並べ、どの書き手が近かったかは読まない」を足す。
  - 自信: 中
- [minor] m-D 拾わなかったときに並べる合成の行が 1 通りに決まっていない
  - 位置と引用: 76 行・90 行
  - なぜ問題か: 76 行は「各段」だが 90 行は 3e-3 と 1e-2 だけ。CoAuthor k = 1・15 と CS1 k = 5 について漂いの筋を並べるか、どちらの帰無の用量を並べるかが無い。出どころは summary_null1.json だけ。
  - 解消の条件: 「並べる合成の行は全 9 セルについて、第 1 の帰無の用量の筋の全段（1e-3・3e-3・1e-2・3e-2）と漂いの筋の ρ = 0.5・0.9」のように全セル共通に列挙する。
  - 自信: 中
- [nit] 117・119 行の重複。
- [nit] 103 行の出どころの名前（要約の名前も併記するか json の SHA-256）。
- [nit] 128 行の wide の比の最小が全体かセルごとか（「全セル・全段を通した最小（n_A 0.13・n_B 0.15）」）。

## 4. 総合の推奨
minor（直してから凍結）。m-B と m-D を 1 通りにすれば g は 5 に近づく。m-A と m-C は文を 1 文ずつ足すだけで、再査読は要らない。

## 5. 読めなかった範囲と注入の疑い
- 読んでいない: notes.md、SEED、eye.py・run_eye.py・explore_eq_amounts.py、ml.py、v1 の notes.md。一部: data.py 1〜108 行と定義の行、v1 conditions.md の grep の行、d6.json の c の値と grep、summary_null1.json の CoAuthor k5_g0・3e-3 の周り、main.tex 47〜50・334〜338 行、supplement.tex の grep、接地の 2 本の grep と抜き出し。
- 注入の疑い: 見当たらない。
