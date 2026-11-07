# review R2（manuscript round 5・教育データの予測・検出の評価の実務・メインが要約して保存）

推奨: **minor**。接地: Gardner & Brooks 2018（"Clearly describe or document methods for statistical algorithm and hyperparameter selection"・"Drawing inferences about which model may be "best" based on a simple sample average or the observed rankings is inappropriate"・"Averages are also susceptible to outliers"）・Pelánek 2015（"the AUC metric should not be used (as the only metric)"・"lack any discussion of the specific purpose of described models"・"To be important, differences between models should either have impact on student practice or lead to interpretable and actionable results."）から逐語。評価 a4・b4・c3・d3・e4・f4。主の値・閾値の表・学習器・差の区間・X18 は出どころと一致。

引き継ぎの判定: 1 解消（ただし貢献が薄くなった → M1）／2 解消（向きの扱いが新しい問題 → M2）／3 一部（「same category」が何を指すか → N2）／4 解消／5 解消／6 一部（-29 語・補足の重複 → N3）／7 解消／8 解消／9 対象外／10 解消。

指摘:
- [major] M1 読者が持ち帰れる比べの基準が本文に無い。データの中に、同じ相手に対して打鍵だけの単純な量と標準の学習器でも AUC は約 0.54–0.57（区間の下限は 0.55 前後）・単独の量の水準は 0.443–0.446 という値がある。→ 貢献の段か考察に「この相手に対する打鍵だけの比べの目安」として 1〜2 文（地位を明記・新しい主張は足さない）。自信 中。
- [major] M2 要旨・序論・結論の「0.05--0.08」は信号の向きを固定した比べでだけ成り立つ。向きを問わないと LR 約 0.055、GB 約 0.027〜0.029。本文は GB の向きなしの差を書かない。→ どちらの比べ方の値かを明記し（例「0.05--0.08 in their designed direction (about 0.03--0.06 ignoring direction)」）、results に GB の向きなしの差を足す。自信 高。
- [major] M3 引用している版 0.2.0 に X18 の条件と結果が無い。README の表に round4-checks の行が無く、conditions-summary.md の冒頭の節の順の説明が末尾の round-4 の節と合わない。→ X18 を含む版を出して DOI を差し替え、README と要約を直す。自信 中。
- [minor] m1 閾値の表を区間なしで「no separation」と読む（conclusion 6-8・discussion 15）。→ 区間を足すか、「differed by 0.7 and −0.3 points (no interval was registered)」と値の言い方に。自信 中。
- [minor] m2 公開物で探索の数値（要旨の 0.05–0.08 や陽性対照）を回し直す入口が README に無い（取り置きの確認だけ）。→ 探索ごとの実行の 1 行（入力・seed・出力）を README に。自信 中。
- [minor] m3 results 14-16 の事後の 0.025 の記述は補足（supplement 318-319）にもあり、本文から外せる。自信 中。
- [nit] N1 相互参照: design 53「the holdout gave 0.505 and 0.500 (Section~\ref{sec:res-main})」は感度の小節、supplement 442「(Section~\ref{sec:res-bounds})」は sec:res-learners が正しい。自信 高。
- [nit] N2 discussion 40「fell in the same category [C-D]」→「was also equivalent, but as a [C-D] quantity it does not enter the decision」。
- [nit] N3 補足 383 と 402-406 の「about as concentrated as the holdout」の重複。自信 高。
- [nit] N4 data 57-58 の「nevertheless」が何に対する逆接か読めない。

読めなかった範囲: gardner の後半・confirm_holdout.json の後半・事前登録の多く・逸脱・notes と conditions の原文・多くの探索の JSON・references.bib・papers の README・文献の記録。注入の疑い: なし。
