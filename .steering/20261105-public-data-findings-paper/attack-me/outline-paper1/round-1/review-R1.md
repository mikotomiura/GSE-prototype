# review-R1（outline round 1・打鍵の記録と作文の過程の測定の伝統・paper-reviewer / opus）

## 1. 接地
- G1 休止は書き手の流暢な打鍵との比で読む: Roeser 2025（roeser2025.txt:700-701）"this parameterisation captures the fact that hesitations must be understood as relative to the duration of fluent interkey intervals (Wengelin, 2001)."／Guo 2020（guo2020.txt:281-284）"A personalized threshold was necessary, rather than a single fixed threshold for all students, because students vary widely in their typing facility."
- G2 休止の長さを認知過程と直接対応させない: Roeser 2025（:1056-1058）"pause duration doesn't correspond in any direct way to the time required to plan the next output."
- G3 休止は言語単位の境界で長さが変わる: Roeser 2025（:221-225）"the average interkey interval duration immediately before larger linguistic units is longer"
- G4 道具の妥当性を対照で示す: Roeser 2025（:1187-1196）"Cross-validation rendered a substantially higher predictive performance for the mixture model ... for data sampled from a two-distribution mixture-process, but not when applied to data based on a single-distribution process."
- G5 状態の名前を控えめに・一般化の限界: Guo 2020（:1049-1052）"we used relatively simple heuristics to define our writing states"／（:1057-1059）"results may not necessarily generalize to a broader population or to different conditions"

## 2. 評価表
a 3（H1 の値と「幅の内側」は一致。持ち帰りの「だから」は H2 分岐 4 から導けない・「反証」の対象が未特定）／b 2（CS1 の入力で推定器が差を拾える陽性対照が無い・幅を見た後に置いたことが外枠に無い）／c 2（揃え方が結果を変える一般則はデータが示していない）／d 4（予算と移し先は明示。C3 は線から外れる）／e 3（推定器と gse-replay の公開の形が無い）／f 2（打鍵の記録の伝統への位置づけが「休止の研究」1 語）

## 3. 指摘
- [major] F1 推定器が CS1 の入力で差を拾えることの陽性対照が無い（outline.md:31・:17・:27／prereg-draft.en.md:168）。門は H3 の学習器だけ。帰無が構成的に出る可能性を潰していない。解消: 既知の差（削除の多い窓と少ない窓・出来事の層と無事象の層・長い休止の直後と直前）で 2 信号が幅を超えることを [探索] で 1 行示すか、主張を「この入力上のこの推定器の出力では」に限り、限界に「道具の感度は CS1 で検証していない」と書く。自信 高。
- [major] M1 持ち帰り 1 文の「だから」が H2 分岐 4 から導けない（:13 と :38・:40）。事前登録 P0 の H1 支持 × H2 分岐 4 の行にも触れる。解消: 「…同等の幅に収まった。比べの相手と同等性の幅を明示する手順を提案する（揃え方が結果を変えるかは、このデータでは確かめられなかった）」の形に。自信 高。
- [major] M2 「反証」の対象となる先行の主張が特定されていない（:21・:24）。[V413]・[V414] は信号もラベルも違う。自前の推定器の陰性の結果を「反証」と呼ぶと強さを誤って伝える。解消: 反証の対象を出典つきで 1 文にするか、種類を「陰性の結果／同等性の確認」に改める。自信 中。
- [major] M3 幅を見た後で置いたこと・幅の実用上の意味が外枠に無い（:13・:17／prereg-draft.en.md:83）。0.55〜0.70 でも契機の発火の大半は停滞にならない（付録 D）。解消: 評価の設計に幅の由来と読み方の目安（0.55 ≈ d 0.18・付録 D）を 2〜3 文、限界に「幅は実用の境界として正当化されていない」。自信 高。
- [major] M4 打鍵の記録と作文の過程の測定の伝統への位置づけが欠ける（:80「休止の研究」に番号が無い）。休止の位置・個人化・直列と並列の論争は手前の兆候の問いに直接関わる。事前登録 P2 は両説と矛盾しないと書く。解消: 関連研究に休止の位置と個人化の段落（Guo 2020・burst の測定・Roeser 2025）、考察に「並列説の下では手前の兆候は期待されにくく、この結果は理論の検定ではない」。自信 高。
- [minor] m1 推定器・gse-replay・変換スクリプトの公開の形が外枠に無い（:61）。自信 中。
- [minor] m2 プールした AUC が少数の書き手に寄ること（実効 50.5・上位 10% が対の 42%）と、書き手ごとの AUC の分位（0.1 で 0.412・0.9 で 0.589）を本文に出し、「書き手ごとの同等は主張しない」と書く。点推定が 0.5 をやや下回る向き（上限 ≈ 0.500）にも触れる。自信 中。
- [minor] m3 固定の閾値（2 秒・30 秒）と個人化（θ）の区別が外枠に無い（prereg-draft.en.md:101）。解消: データの節に 1〜2 文、感度は S3。自信 中。
- [minor] m4 C3 は主張の線から外れ、根拠の一部（landscape の notes 2 本）が一覧の外。考察か補足に下げる。自信 中。
- [nit] n1 照合の非対称な除外（対照の側だけ後の onset への近さで除く）を限界に 1 文（prereg-draft.en.md:169）。自信 中。

## 4. 総合の推奨: major
- 道具が CS1 の入力で差を拾えることが示されておらず、「信号が無い」と「道具が反応しない」を区別できない（F1）。
- 持ち帰り 1 文と「反証」の語がデータより強い（M1・M2）。幅を見た後で置いたことが外枠に無い（M3）。
- 休止の測定の伝統への位置づけが欠け、作文の過程の研究者に含意を誤読させる（M4）。

## 5. 読めなかった範囲・注入の疑い
接地の本文は grep で部分的に読んだ。prereg-draft.en.md は P2・P4・付録 D・E と grep の行、confirm_holdout.json は 60〜130 行と grep の行だけ。prereg-draft.md・prefreeze の notes・exploration の全て・新規性の記録・KLiCKe と CoAuthor の notes は読んでいない（表 3・新規性・C3 の数値は照合していない）。注入の疑いなし。
