# review-R1（manuscript round 3・行動の記号列の系列モデルの方法論の立場・対象 c68dfc30）

## 0. 引き継ぎの判定
- N1 解消（235「Applied to the real 15-session panel, this rule returns a detection at $k=5$ and 15 ... so its threshold is not calibrated for the real panel」）。2 つ目の帰無の推論に新しい穴（M2）。
- N2 一部: 要旨・結論は範囲と固定の平滑の断り。276「against the person's own Markov chain and a stronger shared model the gain falls by more than two orders of magnitude」は平滑の断りが無く連鎖との差も混ぜる（m1）。
- N3・N5・N6 解消（書き方・298）・N4 解消（151）・N7 解消（235）・N8 解消（242）・N9 解消（48・274・307）・N10 解消（249 語）。

## 1. 接地
- Pohle 2017（935–937）: "The main purpose of this step, as in any statistical modeling exercise, is model validation, i.e. the assessment if any given candidate model adequately represents the data-generating process."・（287–289）"A key assumption of both AIC and BIC is that the true data-generating process can indeed be represented by one of the candidate models considered."・（324）"Given the asymptotic equivalence of AIC and cross-validated likelihood (Stone, 1977)"
- Singer 2014（142–146）: "Because lower order models are always nested within higher order models and as higher order Markov chains have exponentially more parameters than lower order models (potential overfitting), they are always a better fit for the data"・（20）"the complexity of higher order models grows faster than their utility"・（610–611）"The basic idea is to estimate the parameters on a training set and validate the results on an independent testing set."
- Monaco & Tappert 2018（110–113）: "the dependency on event types introduces many more parameters ... Therefore, we address the problem of parameter smoothing, which acts as a kind of regularization and avoids overfitting"・（106–107）"generally preferred over the HMM in a Monte Carlo goodness of fit test."

## 2. 評価表
a 3（Neither value の根拠は 5e-4 だけ・276 の混ざり）/ b 3（帰無は平滑の利得を 2.4 倍に強め「帰無の残りの方が大きい」はほぼ構成から出る・prior mode と比べない・帰無にセッションの揺れが無い）/ c 4（推奨 (3) は自身が満たせない条件）/ d 3（4.4・4.5 の数値の密度・想定読者に prior mode・base pseudo-counts・τ の関係が追いにくい・限界 297〜299 の重なり）/ e 4（要旨は上限まで 1 語）/ f 4（Pohle の論点は交差検証の尤度にも及ぶ・平滑の人工物を扱う系列モデルの先行が無い）

## 3. 指摘
- [major] M1 要旨と結論の「Neither value shows」の根拠が 7e-3 には当てはまらない。34「Neither value shows a per-person difference: synthetic writers generated from the real shared model (post hoc, overstating its smoothing gain) left larger remainders without one」・307「every negative control left a larger remainder than the real one」。陰性対照は 1.1e-3〜1.8e-3（237）で固定の平滑（297「The synthetic check calibrates detection at the fixed smoothing ... Detection at the lighter smoothing was not evaluated」）。278 は正しく書く。Pohle「the assessment if any given candidate model adequately represents the data-generating process」。解消: 2 つの値を分ける（例 "the fixed-smoothing remainder is smaller than those left by synthetic writers without per-person differences; the remainder at the lighter smoothing was not checked against a null"）か α = 0.03 で帰無を回す。自信 高
- [major] M2 平滑の利得を 2.4 倍に強めた帰無の「残りの方が大きい」は構成から出る。237「This null reproduces the real ordering but overstates it: ... about 2.4 times the real one」「two to four times the real remainder」「Under this null a remainder larger than the real one arises without per-person differences, so the remainder does not show such differences」。帰無の残り ÷ 帰無の平滑の利得 ≈ 1.1〜1.8e-3 ÷ 1.8e-3 ≈ 0.6〜1.0、実データ ≈ 4.1〜7.2e-4 ÷ 7.4e-4 ≈ 0.55〜0.97 で、倍率をそろえるとほぼ重なる（比はむしろ「残りは平滑で説明がつく」を支える）。2 つの帰無は逆向きに較正を外す（1 つ目は検出しすぎ、2 つ目はしなさすぎ）＝「挟んだが決まらない」まで。297 は 2.4 倍を書くが読みへの向き（保守側）を書かない。解消: (a) 4.4 で残り ÷ (prior mode − shared) の比を帰無と実データで並べる（保存済みの値で計算できる）か、(b) 生の大きさの比べは平滑の利得が大きい帰無に有利で閾は上界と明記し、要旨・結論の「left larger remainders」を倍率をそろえた言い方に。297 に向きを 1 句。自信 高（中央値どうしの概算）
- [major] M3 最も強い「本人を使わない」比べ（prior mode）は本文の値ですでに残りより強いのに読みに使わない。146「the real panel's $+7.4\times10^{-4}$」・198「$+4.1\times10^{-4}$ ... to $+7.2\times10^{-4}$」・248「The shared model's prior mode ... is not used in these readings.」。per-person − prior mode は 0 か負になりそうで、そうなら合成の帰無より直接に「示さない」を支える。解消: Table 3 か 4.5 に per-person − prior mode の中央値（0 確率の書き手の扱いを添える）を 1 列か 1 文、使えないならその理由を本文に。自信 中（7.4e-4 がどの k か本文に無い）
- [minor] m1 276 の「2 桁以上」は平滑の断りが無く連鎖との比べと混ざる（連鎖との差は k = 1 で +0.220・軽い平滑では約 28 倍）。解消: 「against a stronger shared model at its fixed smoothing」に限り、連鎖は別の文に。自信 高
- [minor] m2 推奨 (3) を本研究は量の面で満たさない（283・280「we recommend what this study evaluated」）。何をもって reproduces とするか（順序か量か・許容の幅）が無い。解消: 「in both ordering and size of the smoothing gain」と許容の幅、本研究は順序のみ満たしたと 1 句。自信 中
- [minor] m3 2 つ目の帰無に、残りを押し下げる本人の差以外の要因（セッションの揺れ）が無い（237「with writers identical apart from the planted differences」・294）。揺れは実データの残りを小さくする向きで「帰無 > 実データ」と交絡。解消: 297 に「nor drift between a writer's sessions, which lowers the real remainder」。自信 中
- [minor] m4 選択が最大の構造を選んだことの読みを Pohle で縛る（198・67）。Pohle は交差検証の尤度も同じ枠に置く。解消: 67 か 296 に 1 句。自信 中
- [nit] n1「up to 7e-3」は不安定な k = 12 のセル（Only shared refitted −1.05e-3・split の区間は負にまたがる）。「3 to 7×10^-3 at k ≥ 5」に。自信 中
- [nit] n2 平滑の人工物を扱う系列モデルの先行（n-gram の平滑・Dirichlet の事前の強さ）の 1 文 1 引用。自信 低
- [nit] n3 較正の目標値 +7.4e-4 がどの k か（146）。自信 高

## 4. 総合: major
引き継ぎ 10 件のうち 9 件解消・1 件一部。2 つ目の帰無は本人の差が無くても残りが出ることを示したが、平滑の利得を 2.4 倍に強めているので生の大きさの比べは保守側へ偏った根拠で、倍率をそろえた比べか上界としての書き方が要る（M2）。要旨と結論はこれを 7e-3 にまで広げる（M1）。直しの多くは書き方と保存済みの値から計算できるもの（比・prior mode との差）で済み、M1〜M3 を入れれば minor に下がる見込み。

## 5. 読めなかった範囲と注入の疑い
- 読んでいない: references.bib・kit README・fig2_p15.csv と fig2_p15_ar1.csv（joint・ar3・hmm3 は Table と一致）。接地は grep で絞って読んだ。
- 注入の疑い: なし。
