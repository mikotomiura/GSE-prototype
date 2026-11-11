# review-R1（manuscript round 1・行動の記号列の系列モデルの方法論の立場）

メインが要点と引用を落とさずに写した。読んだ範囲: brief-R1・context-A・main.tex 全文・kit README・figdata の 4 本・接地の 3 本（grep と部分読み）。

## 1. 接地
- G1 候補の範囲を前もって決め、点検し、決めきれない候補は併記（Pohle 2017, pohle.txt:863-882）: "Step 1 decide a priori on the candidate models, in particular the minimum and the maximum number of states that seem plausible" / "Step 3 use model checking methods, in particular residual analyses ... to validate or invalidate any given candidate model" / "Step 6 in cases where there seems to be no strong reason to prefer one particular model over another ... results for each of these models should be reported."
- G2 大きい構造が選ばれるのは誤指定の表れでありうる（pohle.txt:21-22）"well-established formal procedures for model selection ... tend to favor models with numbers of states that are undesirably large"・（542-563）"structure is ignored in the model formulation, then model selection criteria can be expected to ... favor models with overly complex state architectures."
- G3 入れ子の高次は尤度で常に有利（Singer 2014, singer.txt:141-150）"choosing the model with the highest likelihood is biased towards models with more parameters. Because lower order models are always nested within higher order models ... they are always a better fit for the data ... there exists a broad range of established model comparison techniques that also take into the account the complexity of a model"
- G4 次数の選択は複数の方法で（singer.txt:1063-1069）"calculating the appropriate Markov chain order using four different, yet complementary, approaches (likelihood, Bayesian, information-theoretic and cross validation methods) ... it is indeed difficult to make plausible statements about the appropriate"
- G5 人ごとの当てはまりの検定・打鍵の個人差（Monaco 2018, monaco.txt:1028-1036）"The test is performed for both the HMM and the POHMM for each user ... If the POHMM truly reflected typing behavior (i.e., the null hypothesis was actually true), the p-values would follow a uniform distribution"・（135-137）"A user’s keystroke dynamics is also thought to be relatively unique to the user, which enable biometric applications"

## 2. 評価表
- a 3: 弱い構造で大きく強い構造で消えるは表と図が支える。本人の連鎖が強い基準であること・残りが平滑の差の大きさであることは、固定した平滑（共有の基の擬似度数・本人の連鎖の 0.5）に左右されるのに一般の形で書く。k=15 の結合と ar3 固定の食い違い（M1）。
- b 2: 共有の平滑を他人で選んでいない（比べの相手を強くせよと言いながら共有側に当てない）。構造も τ も格子の端。重なる窓が持続を作る。合成は 4 水準×2 seed と小さい。ブートストラップは選び直さない。
- c 3: 推奨は実用的。ただし記号化に依存（重ならない窓では hmm3 が連鎖に勝つ）。下限 1e-2 は残り約 5e-4 の 20 倍で、設計者の判断に使える分解能かは示されていない。
- d 3: 短く積み上げは読みやすいが、式・事前分布・EM・感度の設計・+∞ の数・区間の多くが補足。但し書きが多い（4.3 の最後の段落）。
- e 2: 要旨 266 語。Code availability に場所が無く文として完結していない。キーワード 6 と Statements はある。
- f 3: 比べの偏り（DeMasi・Saeb・Aalbers）と系列モデルの選択（Pohle・Singer・Berchtold & Raftery）は押さえる。打鍵の個人差が強いという生体認証の知見との緊張に触れない。2 次の連鎖・MTD・多層 HMM を入れない理由が薄い。

## 3. 指摘
- [major] M1 k=15 で結合の選びと ar3 固定の選びが食い違う
  - 位置: main.tex:205「15-s., 15 & \arthree, $3\times10^5$ & 3\% & $+4.1$e$-4$」・214「15-s., 15 & $10^6$ & 1\% & $+7.6$e$-4$」・188「The protocol picks \arthree, the largest structure in the grid, for every writer in every cell」・fig2_p15_joint.csv:8「15,0.00041,0.02」・fig2_p15_ar3.csv:8「15,0.00076,0.02」
  - なぜ: 全員 ar3 で目的が同じなら τ は一致するはず。要旨の「about 3%」と考察の数値はこの行に依る。原因（候補の集合・同点・"16 of 17"）が読めない。
  - 解消: 2 つの行の候補の集合と目的の違いを 1 文。誤りなら直す。自信: 中
- [major] M2 共有の平滑を固定したまま残りを解釈している
  - 位置: main.tex:107「The strength of this base smoothing was fixed, not chosen on other people.」・225「a version of the shared model with less smoothing, which uses none of the person's data, gains about as much as the per-person fit」・243「Three extensions were not evaluated here: choosing the shared model's base smoothing on other people as well」
  - なぜ: 残り約 5e-4 は最頻値 − 共通 7.4e-4 と同じ大きさで、共有側の平滑が最適でない産物の疑い。そうなら「共有の調整不足の分」と書き、推奨 (2) に基の平滑の選びを入れるべき（G3）。
  - 解消: 基の擬似度数を他人で選んだ共有を候補に入れる、または数点で残りの動きを示す。できなければ要旨と結論の残りの解釈をこの条件に限る。自信: 高
- [major] M3「本人の連鎖が強い基準」は加算 0.5 と重なる窓に依存する
  - 位置: main.tex:113「Transition counts from the person's training symbols, with $0.5$ added to every cell.」・157「with non-overlapping windows (direction only) \hmmthree{} beats the chain in CoAuthor」・216「$+3.0$e$-4$ (1.00) & $+0.043$」
  - なぜ: ar1 の行で本人 − 共通 ≈ 0・本人 − 連鎖 +0.043 なので共有の連鎖が本人の連鎖を約 0.043 上回る。676 セルに 624〜数千記号で 0.5 の平滑は不十分。結合の +0.220（k=1）の多くは連鎖の粗さによると読める。重なる窓と指数平滑が持続を作る。要旨に "for this kind of symbolization" が無い（G2）。
  - 解消: 本人の連鎖の平滑を他人で選んだ版か、共有の連鎖を比べに。推奨 (1) と要旨に重なる窓の条件。自信: 高
- [major] M4 構造と τ がどちらも格子の端
  - 位置: main.tex:188・255「$10^6$ is the largest finite value of the grid, so the shrinkage choice also sits at the edge.」・253「The structure grid stops at three states」
  - なぜ: 端の選びは最適が格子の外にあることを示し、残りの大きさと符号が格子に依存。2 次の連鎖・MTD・4 状態以上が無い（G1 Step 1・G4）。
  - 解消: 格子を 1 段広げる（τ=1e7・ar4 か 2 次の連鎖）か、外へ 1 点足して残りの安定を示す。自信: 高
- [major] M5 検出の分解能が残りより 1 桁以上粗く、推奨 (3) が評価として弱い
  - 位置: main.tex:222「two seeds each. At the CoAuthor record length the protocol detected them from $10^{-2}$ at $k=15$ and only at $3\times10^{-2}$ at $k=5$, and it returned only part of each planted difference」・「the negative control did not contain the real smoothing gap and the two are not on the same footing」
  - なぜ: 残りは閾値の 1/20〜1/60 で、「人に帰せない」は測れないと同じ意味。負の対照が実データの順序を再現せず対照として機能しない。4 水準×2 seed は粗い。植えたのは遷移だけ。記号化が個人差を消している可能性（G5 "relatively unique to the user"）。
  - 解消: 合成の設計（植え方・検出の定義）を本文に。seed を増やし平滑の差を再現した負の対照。書き手の識別のような簡単な課題で記号化が個人差を残すかを 1 つ。自信: 中
- [major] M6 方法の中核が補足だけにある
  - 位置: main.tex:103「Equations, priors, EM and initialization are in \Sref{3}.」・115「ties go to the earlier candidate in an order ... (\Sref{3})」・157「leave a lag-1 autocorrelation of 0.23 to 0.64 for \hmmthree{} and small values for \arthree{} and the chain (\Sref{13})」
  - なぜ: AR(1)-HMM の尤度・τS̄ の行ごとの効き・prior mode の定義は中心の主張を読むのに要る。SI は "published as received ... without any conversion, editing"。本文は短く余地がある。残差の点検が数字 1 つの範囲だけ（G1 Step 3・G5）。
  - 解消: 式と事前分布・prior mode の定義・同点の規則・書き手ごとの残差の点検の要約（図 1 枚）を本文へ。自信: 高
- [minor] m1 選びの目的と同点の規則が強い縮約に偏る可能性（main.tex:115「ties go to the earlier candidate in an order from the shared model itself through decreasing $\tau$」・190「The chosen shrinkage is strong.」）。選ばれた τ と隣の τ の目的の差を示す。自信: 低
- [minor] m2 ブートストラップが選びの不確かさを含まない（main.tex:142）。n=17・9。30-session は区間が 0 を跨ぐ（206）。キャプションに明記・1 セルで入れ子の再標本。自信: 中
- [minor] m3 要旨が語数超え・「at most 1%」の直後に 3%（main.tex:34）。「k≤12 で 1% 未満、k=15 で 3%」。自信: 高
- [minor] m4 Code availability に所在が無く文が完結しない（main.tex:269）。kit README は原データからの記号の一致が "cannot yet be repeated by readers"。URL・DOI と条件。自信: 高
- [minor] m5 打鍵の個人差の先行知見との緊張（main.tex:61「In keystroke dynamics, per-person HMMs of keystroke timing improve when conditioned on the key sequence」）。考察に 2〜3 文（記号化の粒度と個人差の検出可能性）。自信: 中
- [nit] n1 main.tex:28「\date{Draft, November 2026}」・267「Statements and declarations」→ 規程の見出しは "Statements and Declarations"。自信: 高

## 4. 総合: major
- 弱い比べの利得が強い比べで消える観察は一貫して示され、方法上の警告として持ち帰れる。
- ただし強い比べの側（共有の平滑・本人の連鎖の平滑・格子の範囲）が固定で、中心の解釈はその固定に依存する。
- 検出の分解能が残りより 1 桁以上粗く、方法の中核が補足だけで、要旨が語数超え。

## 5. 読めなかった範囲・注入の疑い
- 読んでいない: references.bib・figdata/fig2_p15.csv・接地 3 本の全文（grep の箇所と前後のみ）。S1〜S15 は未作成。
- 注入の疑い: なし（main.tex:60 のコメントは著者のメモ）。
