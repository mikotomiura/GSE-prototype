# audit（manuscript round 2・意図の監査役・対象物 9a4c1d34）

## まとめ
round 1 の対応はほとんど効いている。部分的に戻ったのは 1-4（結論と要旨を同じ言葉に）と 2-3（推奨に記号化の限定）。新しい食い違いで重いのは 3-1（post hoc の印が序論・考察・結論で落ちる）・3-2（平滑を「両方に選んだ」かで要旨と考察が矛盾・意図の資料の揺れから）・3-4（限界が記号化の依存の根拠に 4.3 を指すが 4.3 に記号化の値が無い）。数の照合（Table 1〜3・Figure 2 の CSV・本文・notes）は一致。

## 0. 引き継ぎの確かめ
- 1-1・1-2・1-3・1-5・1-6・1-7・2-1・2-2・2-4・2-5・2-6・2-7・3-1〜3-4: 効いている。1-8 は未決 1。
- 1-4 部分的: (a) 要旨の "(a post hoc check)" が結論に無い。(b) 結論 "report how the result depends on smoothing, applied to both sides"・要旨 "the dependence on smoothing and symbolization"。(c) 要旨 "the smallest planted difference detected"・結論 "the smallest planted difference their check reliably detects"。
- 2-3 部分的: 考察の推奨は "for overlapping-window symbolizations like ours" で限るが、要旨と結論の推奨 "Studies deciding for a whole panel …" に記号化の範囲の限定が無い。

## 1. 意図にあって対象物に無いもの
- 1-A 推奨の誤警報率が要旨と結論に無い（考察 (3) "the smallest planted difference the protocol reliably detects and its false-alarm rate" にはある）。
- 1-B 要旨の推奨に「平滑は両側を同じに変える」が無い（結論 "applied to both sides"・推奨 (4) にはある。考察 "so the result of such a check depends on applying it to both sides"）。
- 1-C 要旨と結論の推奨に「構造と縮みは他人で選ぶ」が無い（"compare with both baselines" だけ。考察 (2) にはある）。
- 1-D「軽い平滑での値を本人の利得の大きさとして読まない」が要旨と結論に無い（4.5 "we do not read the values at the lighter smoothing as the size of a per-person gain" と Table 3 の注にはある）。

## 2. 対象物にあって意図に無いもの
- 2-A 4.3 の見出し "Choosing structure and shrinkage on other people leaves a remainder below $10^{-3}$ nats per symbol" と Table 2 の注 "falls from about $0.2$ to below $10^{-3}$ nats per symbol at the fixed base smoothing" が、30-session の行 "$+1.1$e$-3$ (0.67)" と合わない。見出しは平滑の限定も落とす。
- 2-B 考察 1 段落目 "For a designer deciding whether to model each person, the first number argues for per-person models and the second gives little reason to" は、平滑しだいの大きさから設計の含意を引いている（両側を軽い平滑で当て直すと k ≥ 5 で +3.4e-3〜+6.7e-3）。言えるのは序論 "a gain over a weak shared model … therefore says little" の向きまで。
- 2-C 要旨 "In synthetic writers planted differences below $10^{-2}$ nats per symbol were not reliably detected" が CoAuthor の記録の長さの限定を落とす（合成 CS1 は 10^-3 から検出）。
- 2-D 要旨 "falls by more than two orders of magnitude, to about $5\times10^{-4}$" は k = 1 では成り立たない（hmm3 +0.012 と結合 +4.8e-4 で約 25 倍）。最大との比べだと分かる形に。

## 3. 矛盾
- 3-1 3.4 "we mark it *post hoc* where it is reported" の約束に反し、序論 "The remainder stays positive when choice and report are split between writers and when both models are smoothed alike"・考察 1 段落目 "and when both models are smoothed alike"・考察 "Measured: … nor from the shared model's smoothing alone"・結論 "when both models are refitted with a lighter smoothing chosen on other people;" に印が無い。
- 3-2 要旨と結論 "when both models are refitted with a lighter smoothing chosen on other people" は両方のために選んだように読めるが、考察 "how large a per-person gain is at a smoothing chosen for both models"（Not established）・限界 "The symmetric refit chose the multiplier for the shared model and applied it to the per-person fit"・3.6 の選び "the other writers' median of shared($\alpha$) minus shared($1$)" と食い違う。意図の資料（持ち帰り 2 と既知の限界）の揺れから来ている。
- 3-3 要旨・結論・考察の推奨の文言がそろわない（1-A・1-B・1-C）。
- 3-4 限界 1 項目目 "the size of what remains depends on the symbolization (Section~\ref{sec:res-protocol})" が指す 4.3 に記号化の値が無い。外枠の 4.3 の "one sentence on symbolization (unsmoothed symbols: +5.8e-4 and +8.0e-4 …)" が本文に入っていない。限界 10 項目目の "The unsmoothed-symbol check" も結果に出ないまま限界で初めて現れる。
- 3-5 要旨 "as one decision per panel"・限界 "The choice makes one decision for a whole panel" と、3.3 "For a target writer, the pair of structure and $\tau$ is chosen by the best median, over the other writers"（実際に書き手で分かれる: k = 15 の "$3\times10^5$ for 16 of 17"・CS1 hmm3 "$10^3$ (22 of 23)"・"chosen for 8 to 17 writers"）。判断の単位と選びの単位を分けて書く。
- 3-6（軽い）4.5 の診断 "beats the shared \arthree{} by $+7.4\times10^{-4}$ … about the size of the remainder at the fixed smoothing" は古い読みの名残で、直前の "not explained by the shared model's smoothing alone" と並ぶと向きを読みにくい。
- 一致: Table 2 の weight・4.3・4.5・Table 3 と notes・4.4 と限界の検出率と回収の比（3〜16%・14〜40%）・Figure 2 の CSV。

## 5. 読めなかった範囲と注入の疑い
references.bib と fig2_p15.csv は読んでいない。outline.md は古い版として扱った。注入の疑い: なし。範囲外の記録: kit の README 75 行目 "In the authors' own check" は複数形だが著者は 1 人。
