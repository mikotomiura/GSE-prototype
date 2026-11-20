# requirement —— 論文 3 の補足資料 S1〜S16 と本文の削り

## 背景
attack-me は round 10（minor）で閉じた（`.steering/20261107-gse-paper3-per-person-learning/attack-me/manuscript-paper3/round-10/verdict.md`）。本文は 8,059 語で、自分で置いた予算 6,800 語を 1,259 語超える。本文は `\Sref{n}` で S1〜S16 を指すが、補足資料はまだ無い（S6・S10・S11 は欠番）。引き継ぎ: `.steering/_handoff/next-session-gse-paper3-supplement-and-trim.md`。

## ゴール
1. 補足資料を本文と別のファイルで作る（UMUAI の SI は受け取ったまま出る）。中身は outline.md 末尾の移した文・本文の `\Sref` の参照先・各 experiments/ の notes と集計値。書き手ごとの値は出さない。
2. 本文の細部を補足へ移し、序論〜結論を 6,800 語に寄せる（足すより移す）。
3. 補足の節番号を本文の初出の順に振り直す（欠番なし）。
4. 表 3 の区間が四分位と同じ値になることの扱いを決める。
5. 移した後に数値の照合（Opus・読むだけ）を通し、length-log に語数を書く。
6. 投稿前の既知の未決（round-10/context-A.md の 1〜16）を確かめる。

## 受け入れ条件
- 本文の序論〜結論が `texcount -inc -sub=section` で 6,800 語前後（±100）。要旨は 250 語以下。組んで警告 0。
- 補足は組めて、本文の全ての `\Sref` の参照先がある。欠番が無い。
- 判断 43・44 で本文に残すと決めたもの（決定に関わる値・個人差の定義・決定の問いと科学の問いの区別・入れ替えの対照の結論の範囲）と、判断 37 C・round 7 Y5（EM の初期化と収束の 1 文・先頭の記号の採点の規則）が本文に残る。
- 数値の照合で誤り 0。
- papers/ に GSE の名前・内部のパス・判断の番号を書かない。
