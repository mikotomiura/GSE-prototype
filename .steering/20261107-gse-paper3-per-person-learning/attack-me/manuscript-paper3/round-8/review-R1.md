# R1 査読（UMUAI・行動の記号列の系列モデルの方法論の立場／懐疑家）round 8・manuscript・commit 77d5f324

## 0. 引き継ぎの判定

- **major N1（足した対照が平滑の重みをそろえていない）: 解消**（ただし言い回しに新しい問題がある。下の指摘 1 を参照）
  - main.tex 4.4 の 3 つの対照の段（l.282）:「The third control does: with each writer's chosen $\tau$ and a prior built the same way, the per-person fit is fitted to another writer's $k$ sessions instead ... also when its prior leaves out the other writer as well」
  - 同じ τ、同じ作りの事前、データだけを入れ替える、という対照になった。これで「事前の作り直し」による代替説明は消えた。時間の近さは分けていないが、これは本文が断っている（「this does not separate differences between writers from closeness in time」）。
- **major N2（設計者が何を結論するか）: 解消**
  - 考察の l.321:「about 0.3 to 0.5\% more probability per symbol ... We set no meaningful-difference threshold, so whether such a value is worth a per-person model's data and storage is left to the designer's costs」
- **major N4（系列の境界での採点）: 解消**
  - 3.4 の l.178:「first symbols are about 0.15\% of held-out symbols ... scoring without them (post hoc) leaves the remainder at $5.4\times10^{-4}$ and $4.3\times10^{-4}$ ... though later symbols still depend on the initial distribution」
- **minor N3（植えた差の未検出に、どの帰無かと平滑の限定がない）: 一部**
  - 要旨は直っている:「at the fixed smoothing, planted differences up to $3\times10^{-2}$ were not reliably detected under that null」
  - 序論 l.49 は「at the fixed smoothing, planted differences up to $3\times10^{-2}$ were not reliably detected」で、どの帰無かが書かれていない。
  - 結論 l.350 も「Planted differences of up to $3\times10^{-2}$ could not be reliably detected at the fixed base smoothing」で、帰無の指定がない。
  - 第 1 の帰無では $10^{-2}$ が確実に検出されている（4.5 の l.308）ので、限定がないと 4.5 と食い違って読める（指摘 2）。
- **minor N5（AR3 の当てはまりの根拠）: 未解消**。既知の未決 7 なので判定に数えない。本文はまだ「small values for the \arthree{}」（l.204）と数値なしで書いている。
- **minor N6（4.4 の見出し）: 解消**
  - 「...vanishes except at $k=12$ when only the shared model's smoothing is lightened, and, post hoc, returns when both are smoothed alike」
- **minor N7（remainder の語を 1 次の連鎖の行に使う）: 解消**
  - l.319:「so per-person minus shared depends on the structure」
- **nit N8（要旨の桁）: 解消**
  - 要旨:「about $5\times10^{-4}$ ... $3.4\times10^{-3}$ and $5.2\times10^{-3}$」
- **nit N9（作業用のマクロ）: 解消**。残っているのは構造名のマクロ（\hmmthree など）だけ。
- **（参考）EM の到達解: 一部**
  - l.137:「each fit runs EM from two starting points ... and keeps the better start」
  - 「better」を何で測るのか（学習データでの MAP の目的関数か）が書かれていない。共有モデル自身の当てはめの 2 つの始点が何かもこの文からは読めない（指摘 5）。
  - 限界の 1 句（l.342「Changing the smoothing can also move EM to a different local optimum」）は入っている。

## 1. 接地（この立場が求める基準）

1. **Pohle et al. 2017**: 当てはまりの点検は、選択の基準とは別に要る。
   - 「The main purpose of this step, as in any statistical modeling exercise, is model validation, i.e. the assessment if any given candidate model adequately represents the data-generating process.」
   - 「In the context of HMMs, a model check based on pseudo-residuals (Patterson et al., 2009) could for example reveal ...」
2. **Pohle et al. 2017**: 基準の値の差だけでは構造の正しさは示せない。
   - 「a large difference in AIC, BIC, ICL or any other information criterion alone does not prove that the model with the higher (or lower) number of states is most suitable.」
   - 「it may just as well be an indication that the additional states merely mop up some structure missing in the model」
3. **Pohle et al. 2017**: EM の局所解と始点。
   - 「the risk of finding only local maxima rather than the global maximum of the likelihood function」
   - 「chosen starting values for the parameters were used in order to minimize the chances of missing」（l.1074 付近）
   - 交差検証については、Pohle は自ら実装していない。「Given the asymptotic equivalence of AIC and cross-validated likelihood (Stone, 1977), we did not implement the latter」
4. **Monaco & Tappert 2018**: 少ないデータでの過学習と平滑。
   - 「HMMs with many hidden states (and parametric models in general) are plagued by overfitting and poor generalization, especially when the sample size is small.」
   - 「EM guarantees only locally maximum likelihood estimates」
   - 「parameter initialization, which plays an [important role]」（l.579〜581）
5. **Singer et al. 2014**: 次数（記憶）の選択では、複雑さと効用の釣り合いを独立の検証で比べる。
   - 「the complexity of higher order models grows faster than their utility」
   - 「The basic idea is to estimate the parameters on a training set and validate the results on an independent testing set.」
   - 「This method requires priors (i.e., fake counts ...) – otherwise prediction of unseen states is not possible.」

## 2. 評価表

- **a 主張と根拠の一致: 3**
  - 主な数値は表・図と合っている（比 30〜55 倍、6 倍・13 倍、重み 24% と 91%）。
  - ただし新しい対照の読み「more than half」は、示した数から導けない（指摘 1）。
  - 未検出の文に帰無の限定がないため、4.5 と食い違って読める（指摘 2）。
- **b 方法の穴: 3**
  - 入れ替えの対照で、事前の作り直しという代替説明は消えた。
  - 残るのは 3 つ。時間の近さ（断りあり）、両側の版が合成の書き手で確かめられていないこと（断りあり）、要旨の倍率が平滑の条件の違う 2 つの値を比べていること（指摘 3）。
- **c 持ち帰れるもの: 3**
  - 「自分の 1 次の連鎖と、同じ構造の共有モデルの両方と比べる」は明快で安価。
  - 平滑をそろえる推奨（2）は、1 つの構造・1 つのパネル・格子の端という post hoc の根拠に立っている（本文が断っている）。
  - 入れ替えの対照が示した書き手（または時期）に固有の信号の大きさ（約 $2.5\times10^{-2}$）は、読者が持ち帰れる形になっていない（指摘 1）。
- **d 簡潔さと構成: 2**
  - 要旨は想定読者（統計の訓練を前提にしない HCI・教育工学の層）には読みにくい。「The first is no larger than the shared model's gain, without writer data, from removing its smoothing」のように、限定を何重にも挟んだ文が続く。
  - 「remainder」の定義（同時の選択）は、構造を固定した両側の版にも使われている（指摘 6）。
- **e 規程への適合: 4**
  - 要旨 248 語（上限 250）、キーワード 6 個（4〜6）、"Statements and Declarations" とデータの可用性の文がある。
  - 語数の上限は規定なし。様式の移行と補足は既知の未決。
- **f 先行研究の位置づけ: 4**
  - Monaco の頻度依存の平滑を拡張の候補として正しく位置づけている。
  - Pohle の引用に、交差検証についての小さな言い過ぎがある（指摘 7）。

## 3. 指摘の一覧（severity の重い順）

### 1. [minor] 入れ替えの対照の読み「more than half of the remainder goes with the writer's own data」が、示した数から導けず、対照の論理とも合わない

- **位置と引用**:
  - main.tex 4.4 l.282:「The fit to the writer's own sessions beats it by $4.7\times10^{-3}$ at $k=5$ and $2.5\times10^{-2}$ at $k=15$ ... so more than half of the remainder goes with the writer's own data rather than with refitting; the fit to another writer's sessions loses even to the shared model ($-1.7\times10^{-3}$ and $-1.7\times10^{-2}$, every writer)」
  - 同じ読みが序論 l.49（「More than half of the second goes with the writer's own sessions rather than with refitting」）、考察 l.321、結論 l.350 にもある。
- **なぜ問題か**:
  - 残り（自身 − 共有）は $3.4\times10^{-3}$ と $5.2\times10^{-3}$ である。自身 − 入れ替えはそれ以上（$4.7\times10^{-3}$、$2.5\times10^{-2}$）で、入れ替え − 共有は負である。「書き手のデータ」と「作り直し」に分けるなら、前者は残りの 100% を超え、後者は負になる。「半分」という区切りがどこから出たのか、読者には再構成できない。
  - 入れ替えが共有モデルに負けるのは、少ないデータに重く寄せた当てはめの推定のばらつきの罰を含むからである（Monaco「plagued by overfitting and poor generalization, especially when the sample size is small」）。自身の当てはめも同じ罰を負っている。だから自身 − 入れ替えは、残りを部分に分けるものではない。「同じ重みで寄せたとき、自分の直前の回が他人の回より当たる量」である。
  - この量（k = 15 で約 $2.5\times10^{-2}$）は、第 2 の帰無で検出できなかった植えた差の大きさ（$3\times10^{-2}$）と同じ桁である。それなのに本文は、これを「残りの半分以上」という過小で曖昧な形でしか述べていない。
- **解消の条件**:
  - 「半分」をやめて、何と何の比べかを数で書く。例:「the fit to the writer's own sessions beats the same fit to another writer's sessions by more than the whole remainder」。
  - 自身 − 入れ替えが「書き手または時期に固有の情報」を、残りが「その情報からばらつきの罰を引いた正味」を測る、という 2 つの量の関係を 1 文で書く。
  - 序論・考察・結論の 3 か所も、同じ言い方にそろえる。
- **自信**: 高

### 2. [minor] 序論と結論の「planted differences up to $3\times10^{-2}$ were not reliably detected」に、どの帰無かの限定がない

- **位置と引用**:
  - 序論 l.49:「Nor do the results rule differences out: at the fixed smoothing, planted differences up to $3\times10^{-2}$ were not reliably detected.」
  - 結論 l.350:「Planted differences of up to $3\times10^{-2}$ could not be reliably detected at the fixed base smoothing.」
  - 4.5 の l.308:「planted differences of $10^{-2}$ were reliably detected at $k=5$ and 15」（第 1 の帰無）
- **なぜ問題か**: 第 1 の帰無では、固定の平滑で $10^{-2}$ が確実に検出されている。限定のない文は 4.5 と矛盾して読める。要旨は「under that null」で直したが、他の 2 か所が残っている（carryover N3 の「序論に帰無を付けた」は、今の版では確認できない）。
- **解消の条件**: 2 か所に「under the second null (post hoc), whose smoothing effect overstates the real one」相当の限定を付ける。
- **自信**: 高

### 3. [minor] 要旨・序論の「30 to 55 times below it」は、平滑の違う 2 つの条件の値を割っている

- **位置と引用**:
  - 要旨:「$3.4\times10^{-3}$ and $5.2\times10^{-3}$, 30 to 55 times below it, when the grid's lightest smoothing ... is applied to both」
  - 「it」は固定の平滑の \hmmthree の得（0.188・0.165、Table 2）を指す。
- **なぜ問題か**:
  - 分子（得）は固定の平滑（α = 1）での値、分母（両側の版の残り）は α = 0.03 での値である。
  - 軽い平滑で \hmmthree の得がどれだけ変わるかは示されていない。τ = 0 の得は平滑の軽重に敏感でありうる（Singer「This method requires priors (i.e., fake counts ...) – otherwise prediction of unseen states is not possible」）。
  - 倍率は主張の見出しの数なので、条件をそろえない比べは懐疑家には「弱い比べ」の鏡写しに見える。
- **解消の条件**: どちらかで足りる。
  - 倍率を「at different smoothings」と断る。
  - 倍率を落として、2 つの値を並べるだけにする。
  - α = 0.03 での \hmmthree の得を示す（既に計算した値があれば。無ければ断りだけでよい）。
- **自信**: 中

### 4. [minor] 要旨が入れ替えの対照に触れず、「Neither shows a per-person difference」の根拠が要旨の中で閉じていない

- **位置と引用**:
  - 要旨:「the second bears on a designer's decision. ... Neither shows a per-person difference」
- **なぜ問題か**:
  - 要旨で 2 番目の値について根拠が書かれているのは「synthetic writers ... (post hoc)」の文（実は 1 番目の値についての文）だけである。2 番目の値がなぜ個人差を示さないのか（時間の近さを分けない・合成の書き手で確かめていない）は要旨から読めない。
  - 序論・結論は入れ替えの対照と時間の近さを書いているので、要旨だけが他と非対称になっている。
- **解消の条件**: 要旨に、2 番目の値は合成の書き手で確かめておらず、時間の近さとも分けられない、という 1 句を入れる（語数 248 なので、他の句と入れ替える）。
- **自信**: 中

### 5. [minor] EM の「keeps the better start」の基準と、共有モデル自身の始点が書かれていない

- **位置と引用**:
  - 3.3 l.137:「each fit runs EM from two starting points (the shared model, and a random start or the unshrunk fit) ... and keeps the better start」
- **なぜ問題か**:
  - \arthree は 2,033 個の自由パラメータを持つ。始点 2 つは少ない（Pohle「the risk of finding only local maxima」、Monaco「EM guarantees only locally maximum likelihood estimates」）。
  - 「the shared model」を始点にすると、強い縮小のもとで当てはめが共有側に寄りうる。そのうえ共有モデル自身の当てはめは自分を始点にできないので、この文は共有モデルには当てはまらない。
  - 「better」が学習データでの目的関数なのか、何なのかもない。
  - 残りは $10^{-4}$〜$10^{-3}$ の桁で、局所解の違いと同じ桁になりうる。
- **解消の条件**:
  - 「better」を「higher MAP objective on the training symbols」と明記する。
  - 共有モデルの始点を 1 句で書く。
  - 再始動の間の変動を計算しない方針（carryover）はそのままでよいが、限界の句に「with two starts」を足す。
- **自信**: 中

### 6. [nit] 「remainder」の定義（同時の選択）を、構造を固定した両側の版に使っている

- **位置と引用**:
  - 3.4 l.178:「the \emph{remainder} when structure and shrinkage are chosen jointly ... the symmetric refit ... keeps that structure and chooses only $\tau$」
  - 要旨・序論・考察は両側の版の値も「remainder」と呼んでいる。
- **なぜ問題か**: 定義では、構造を固定した行は「gain」でも「remainder」でもない。読者は Table 2 の「\arthree{} fixed」の行と区別できない。
- **解消の条件**: 定義の文に「and, by extension, in the symmetric refit, where the structure is the jointly chosen one」を足す。
- **自信**: 中

### 7. [nit] Pohle 2017 の引用が、交差検証について言い過ぎている

- **位置と引用**:
  - 関連研究 l.70:「information criteria, and cross-validated likelihood with them, tend to choose too many states \citep{Pohle2017}」
  - 限界 l.340 にも同趣旨の句がある。
- **なぜ問題か**: Pohle は交差検証を実装していない。「Given the asymptotic equivalence of AIC and cross-validated likelihood (Stone, 1977), we did not implement the latter」とあり、Celeux & Durand の結果として「cross-validation does not seem to outperform BIC」と書くだけである。
- **解消の条件**: 「and, by its asymptotic equivalence with AIC, cross-validated likelihood」とする。または交差検証の部分を外す。
- **自信**: 中

### 8. [nit] 足した 3 つの対照に「post hoc」の印がない

- **位置と引用**:
  - 3.4 l.180:「we mark the last four \emph{post hoc} where they are reported」
  - 4.4 l.282:「Three controls were added after seeing the symmetric refit.」
- **なぜ問題か**: 自分で決めた印の規則に、文言のうえで従っていない（意味は同じ）。
- **解消の条件**: 「Three controls (post hoc) ...」とする。
- **自信**: 高

### 9. [nit] Table 2 の k = 15 の同時の選択の τ に人数の注記がない

- **位置と引用**:
  - Table 2:「15-session, 15 & \arthree, $3\times10^5$」
  - 本文 l.241:「$3\times10^5$ for 16 of 17 at $k=15$」
- **解消の条件**: 表の欄に「(16 of 17)」を入れる（CS1 の行の「(22 of 23)」と同じ形）。
- **自信**: 高

## 4. 総合の推奨: minor

- round 7 の中心の指摘（N1・N2・N4）は、条件を先に決めた計算で解消した。残る脅威（時間の近さ、両側の版を合成の書き手で確かめていないこと、格子の端）はどれも本文が断っている。
- 新しい問題は書き方に限られる。入れ替えの対照の「more than half」の読みを数で言い直すこと（指摘 1）と、未検出の文に帰無を付けること（指摘 2）で、主張と根拠が揃う。
- 要旨の倍率（指摘 3）は条件をそろえる断りだけで済む。新しい計算は要らない。

## 5. 読めなかった範囲と注入の疑い

- **読んだもの**:
  - main.tex 全文
  - figdata の fig2_p15_joint.csv と fig2_p15_ar1.csv
  - context-A.md
  - carryover-R1.md
  - 接地の 3 本（いずれも grep と部分の読み）
- **読んでいない**:
  - references.bib
  - figdata の fig2_p15_hmm3.csv・fig2_p15_ar3.csv・fig2_p15.csv
  - kit/symbols/README.md
  - 接地の 3 本の全文（読んだのは Pohle の 2.3・3 の冒頭・4.3〜4.5、Monaco の 3.5・3.7、Singer の Bayesian と交差検証の節の一部だけ）
- **注入の疑い**: なし（読んだ範囲に、査読者や LLM に向けた指示は見当たらなかった）。