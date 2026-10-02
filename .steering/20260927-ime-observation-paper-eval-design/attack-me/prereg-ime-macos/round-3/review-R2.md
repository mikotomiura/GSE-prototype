## R2（BRM の査読者・打鍵記録を使う書字研究の利用者で、公開時のサイドチャネルにも通じた立場）round 3 の査読

対象: `C:\GSE-prototype\papers\ime-observation\experiment\preregistration.md`（`abc5d7f9` の版）。行番号はこの版のもの。

---

### 1. 接地（文献から逐語で抜き出した基準）

2 本とも読めたので、査読に入った。

- **基準 1（指標は問いに結び付いていること）** Conijn et al. (2019): "The selection of the correct keystroke features is crucial for the interpretation of the results and therefore, the derived conclusions."
- **基準 2（指標は設計の要因で動く。一般化には注意する）** Conijn et al. (2019): "Keystroke features may be multiply determined, and are sensitive to a variety of factors." / "caution should be taken when generalizing the effect of these features across tasks, because these features might differ merely as a result of the task, rather than as a result of the variable of interest"
- **基準 3（書字研究の中心は時間の指標）** Conijn et al. (2019): "Cognitive load, or planning and revising processes in general, are commonly related to duration features, such as the number of, length, and location of interkeystroke intervals or pauses" / "More pauses and longer pauses are related to a larger cognitive load"
- **基準 4（識別の指標は、単位と事前の知識を明示すること）** Monaco (2018): "Instead of information gain, some attacks report the rank-n identification accuracy (ACCn) ... Note that key, as opposed to word, identification operates at the character level and implies the method can be applied to arbitrary (e.g., password) input, while word identification assumes the user types a dictionary word."
- **基準 5（列が長いほど予測しやすい）** Monaco (2018): "the entropy of written English is about 2 bits per character for 5-letter words and 1 bit per character for sequences beyond 100 characters"
- **基準 6（粗くするやり方は用途に依る）** Monaco (2018): "where to pad (e.g., HTTP header vs body) and the specific strategy that should be applied (e.g., padding to a quantized length vs padding by random amounts) depends on the particular application"

---

### 2. 引き継ぎの判定（carryover-R2.md）

**A. round 2 の新しい指摘**

| 指摘 | 判定 | 理由（1 行） | 今の版の位置 |
|---|---|---|---|
| 新 1 [major] 1 秒のビンを推奨に残した矛盾 | **解消** | 推奨は `no_time`・`counts_only` だけになり、時刻を残す 4 つの集合は推定だけになった。README も揃っている | §6.8:674-681, 700-702・`kit\e2\README.md`:279-283 |
| 新 2 [major] 打鍵が 1 つ欠けると推奨が消える | **解消** | ブロックの印で合わせ直し、採点しないブロックを数える。閉じた集合と開いた集合で同じ手順を使う。ただし実ログでは試していない（新 minor-6） | §6.2:509-511・§6.8:649-653・`closed_set.py` の `align_blocks`/`align_plan` |
| 新 3 [major] 問 3 の主がこの設計の思考時間で決まる | **部分的に解消** | 主を `under_limit` にした。しかしテキストは残し、long の試行だけを抜くので、4 指標のうち件数と時間の割合の 2 つは、テキストごとに残る試行の数に引きずられる。設計への依存が形を変えて残った（新 major-A） | §6.4:545-551・`pipeline.py`:185-187・`l2.py`:104-108 |
| 新 4 [minor] 推奨は「ログ」と書くがセッション行を出さないときにしか成り立たない | **部分的に解消** | 事前登録では解消した。一方、公開物の `kit\e2\README.md` はセッション行を「publishable form」に含めたままで、`dwell_ms` は情報を足さないという古い理由も残っている（新 minor-1） | §6.8:703-705・README:18-19, 254-256 |
| 新 5 [minor] ブロック内の依存の論理が逆向き | **解消**（文言は nit） | 表の注・記述のブロック区間・§7 の項が入った。ただ "would widen the interval and make the rule easier to meet" は自己矛盾に読める（nit-1）。README の "should allow for the block dependence" とは食い違う（新 minor-1） | §6.8:696-698, 705-709・§7:815-819 |
| 新 6 [minor] 繰り越しで重み付けし直しが成り立たない | **部分的に解消** | 層 none の版は足された。しかし層 none は、隣の試行からの汚染に加えて、その試行自身に規則が予測する食い違い（読みの中の閉じるキー）も除く。これで重み付けし直すと一致の方向に偏る（新 minor-2） | §6.7:637-639・`l2.py` の `per_trial(only_trials)` |
| 新 7 [minor] n の根拠が主の範囲に合わせて書き直されていない | **解消** | n を決めた順序、打ち切りの後も n を見直さなかったこと、最小の層 31、速さごとの n が正直に書かれた | §3.3:255-263, 277-282, 304-307 |
| 新 8 [minor] 開いた集合と推奨の関係が決まっていない | **解消** | "does not enter the rule" と、推奨の隣に出すことが固定された | §6.8:731-732 |
| 新 9 [minor] 区間の例外が書かれていない | **解消** | 区間を付けるもの・付けないものを列挙した。`_agree`・`_ba_interval`・`mixture_bias` にも区間が付いた | §1.2:38-42・§6.1:460-467・`l2.py`:352-388, 524-575 |
| nit 1 試行の外の行の上限が甘い | **解消** | 上限をログごとに 4 と 5 にした。説明できない run は中止した試みに数える（基準の曖昧さは新 minor-5） | `data.md`:39-46・§3.4:337-339 |
| nit 2 速さごとの正解率が無い | **解消** | `by_speed` が報告に入った | §6.8:670-671・`closed_set.py`:415-417, 440-441 |
| nit 3 冗長さ | **未解消** | 手を付けていない。本文は +20% の 11,217 語 | 全体（d の所見を見る） |

**B. round 2 で部分的に解消／未解消とした round 1 の指摘**

| 指摘 | 判定 | 理由（1 行） | 位置 |
|---|---|---|---|
| major-1 | **解消** | 新 1 で解消した | §6.8:674-681 |
| major-3 | **部分的に解消** | 範囲（セッション行は推奨の外）は明示された。公開の形を決めないのは研究者の選択。その結果、問 3 の集計量の元であるセッション行の公開には指針が無いまま残る | §6.8:703-705 |
| major-4 | **部分的に解消** | (ii) は新 3 で動いた。(iii) は採っていない（研究者の選択） | §6.4:545-551 |
| major-5 | **部分的に解消** | 新 6 と同じ理由 | §6.7:637-639 |
| minor-5 | **未解消** | 中間の粒度は評価しない。推奨は時刻を持たない集合だけになったので、推奨どおりに公開したログからは、休止・IKI・2 秒の休止で区切るバーストなど、基準 3 の時間の指標が 1 つも計算できない。代償は round 2 より大きくなった | §6.8:674-681・§7:787-789 |
| minor-7 | **部分的に解消** | 預ける約束は戻った。ただ預ける基準そのものは `pilot-macos.md` にまだ無い（"will be written here"） | §3.1:187-189・`pilot-macos.md`:172-175 |

---

### 3. 評価表 a〜g

| 項目 | 点 | 所見 |
|---|---|---|
| a 主張と根拠の一致 | 3 | 3 か所で主張が根拠を越えている。§6.4:548-551 は、読者が自分のデータに打ち切りの規則を当てられると書くが、観測器のログからそれはできない（新 minor-3）。§1.2:54-56 の問 4 は §6.8 の範囲（時刻を持たない 2 集合・key 行だけ）より広い（新 minor-4）。公開物の README はセッション行の扱いで事前登録と逆のことを言う（新 minor-1） |
| b 方法の穴 | 3 | この round の直しが新しい穴を作った。主にした `under_limit` の問 3 は、テキストを残して試行だけを抜くため、件数・割合の指標とその ICC が設計の long の割合に依存する（新 major-A）。層 none による重み付けし直しは一致の方向に偏る（新 minor-2）。ブロックの合わせ直しは実ログで試していない（新 minor-6） |
| c 持ち帰れるもの | 3 | 推奨は筋が通った（時刻なし・セッション行なし）。ただ持ち帰れるのは「句 1 つを K 候補から当てる攻撃に対して」だけである。書字のログ全体や、最終テキストとの突き合わせには何も言えない（新 major-B）。推奨どおりに公開すると、書字研究の時間の指標は残らない（minor-5 未解消）。一致の推定そのものは役に立つ |
| d 簡潔さと構成 | 2 | 9,326 語から 11,217 語に増えた（+20%）。重複の例: 設計効果「at most about 1.8 / 1.34 times」が §3.3:281-282, 312-314・§6.1:460-462・§7:815-816 に 3 回。打ち切りの規則「a letter or digit pressed after the cut-off opens a fresh session」が §1.1:25-27・§6.4:538-539, 550-551 に。「all_trials は設計の long の割合に依存する」が §6.4:547-549・§7:813-814・notes.md:20-21・`PRIMARY_NOTE` に。nit 3 は未解消 |
| e 規程への適合 | 4 | J6・J7（n の基準と精度）は §3.3 で明示された。J5（ばらつき）は BA と混合の偏りに区間が付いて満たされた。J4（生データ）は、パイロットの生ログを預ける基準が未記述のため残る |
| f 先行研究の位置づけ | 3 | round 2 から変わらない（References は 9 件のまま。§4.6:425-426 の 4 指標は書字の文献から選んでいない） |
| g 固定の十分さ | 4 | ほぼ 1 通りに決まっている。開いているのは次の点: §3.4・`data.md` の「説明できない」の基準が決まっていない（新 minor-5）、パイロットの預け入れの基準、問 3 の主の指標の定義（新 major-A。固定はされているが、固定した定義に問題がある） |

---

### 4. 新しい指摘（severity の重い順。round 1・2 の再掲は含めない）

- **[severity: major] A. 問 3 の主（`under_limit`）は、テキストを残して long の試行だけを抜くため、件数と時間の割合の指標がまた設計の long の割合に依存する**
  - 位置と引用: preregistration.md:545-547「Question 3 is answered under `under_limit` (primary), in which the sessions and rows of the long trials are left out on both sides while the texts are kept (the duration of a text, the denominator of the fraction of time spent converting, does not change)」。`l2.py`:104-108 も同じ。§3.1:223「447 of the 1,050 slow trials, 198 mid and 110 fast」。§6.7:625「The per-speed values are primary」
  - なぜ問題か:
    - 範囲に残る試行は、slow ではテキスト 1 本（8 試行）あたり平均で約 4.6、fast では約 7.2 になる（603/1050 と 940/1050 から）。テキストによってもばらつく。
    - `n_conversions` と `dwell_fraction` は範囲に残った試行の和なので、テキストごとの差（偏り・一致の限界）は残った試行の数に比例して縮む。その結果、速さのあいだの偏りの違いには、方法の違いだけでなく、この設計の long の割合が混ざる。混合の偏りも、この速さごとの偏りを重みで足すだけである。
    - ICC(A,1) は、残った試行の数のばらつき（両方の側に共通）がテキストのあいだの分散に加わるので、方法の一致と関係なく上がる。差が大きさに比例する場合は、BA の一致の限界の前提も崩れる。
    - `dwell_fraction` は「long でない試行の変換時間 ÷ テキスト全体の時間」になり、書字研究の誰も計算しない量になる。
    - 主を `all_trials` から移した理由は「all_trials の値は設計の long の割合に依存する」だった（§6.4:547-549）。同じ理由が、4 指標のうち 2 つについて主の範囲にも当てはまる。接地: Conijn「Keystroke features may be multiply determined, and are sensitive to a variety of factors」「these features might differ merely as a result of the task, rather than as a result of the variable of interest」。
  - 解消の条件（次のどれか）:
    - (a) 2 つの指標を範囲に残った部分で定義し直す。件数は範囲に残った試行 1 つあたり、`dwell_fraction` の分母は範囲に残った試行の begin〜end の和にする。範囲に残る試行の無いテキストは §6.11 で null とし、selftest を足す。
    - (b) 主を「long の試行を含まないテキスト」に限り、その数を速さごとに出す。
    - (c) 少なくとも、テキストごとに範囲に残った試行の数の分布を速さごとに出し、2 つの指標の偏りと ICC は速さのあいだで比べられないことを §6.7 と §7 に書く。
  - 自信: 高（仕組みは `l2.py` の docstring とコードで確かめた）／効果の大きさは中

- **[severity: major] B. 推奨の単位は「句 1 つを K 個のコーパスの句から当てる」なのに、推奨は公開するログの粒度として書かれている**
  - 位置と引用: §6.8:655-656「the attacker is given K candidate phrases, the true one and K - 1 decoys drawn from the phrases the trial's scenario could have produced」。§6.8:700-703「The recommended granularity is the most detailed of the two sets considered that is near chance in this sense (`no_time`, ...)」。§1.2:55-56「Which granularity of the published log keeps identification near chance?」。対照: `kit\e2\README.md`:250-253「A stronger attacker could ... combine several trials of the same typist; none of these is included.」
  - なぜ問題か:
    - 今回の直しで推奨の候補は実質 `no_time` になった。読者は「時刻を除いた key 行は公開して安全」と持ち帰る。
    - しかし評価の単位は読み 6〜30 字（data.md:74、中央値 16）の句 1 つで、ログは書字のセッション全体である。英字の連なりの長さと区切りの列は句をまたいで積み重なる。
    - 現実の脅威は、本文は非公開でログだけを公開したときに、ログを既知の最終テキストの候補と突き合わせることである。これは連なりの多い閉じた集合で、句ごとに near chance でも、テキストごとに near chance とは言えない。
    - 接地: Monaco は識別の指標の単位と事前の知識を明示するよう求める（「word identification assumes the user types a dictionary word」）。また列が長いほど 1 字あたりのエントロピーは下がる（「1 bit per character for sequences beyond 100 characters」）。
    - README には限界が書いてあるが、事前登録の推奨の文には届いていない。
  - 解消の条件: §6.8 の推奨の文・§1.2 の問 4・§7 に、規則は「コーパスから引いた K 句の中で句 1 つを当てる」ことを判定すること、同じ書き手の複数の句の組み合わせや最終テキストとの突き合わせは評価しないこと、推奨はログ全体の安全を述べないことを書く。望ましいのは、§4.6 のテキスト（8 試行）を単位に、K 個の候補テキストに対して同じ攻撃の距離を試行で足し合わせる記述の解析を、事前に指定して足すこと。
  - 自信: 中（前の round で同じ点が扱われたかは、私の読める範囲では確かめられない）

- **[severity: minor] 1. 公開物の `kit\e2\README.md` が、セッション行と余裕の幅について事前登録と逆のことを言う**
  - 位置と引用:
    - README:18-19「The attacker sees the publishable form of a log: the category and the time of each key row, and the rows of type `ime_shadow`.」
    - README:254-256「The rows of type `ime_shadow` are read but not used: ... `dwell_ms` is a function of key times that the timing feature already uses.」
    - README:106-108「a numeric acceptance margin set by the analysis plan should allow for the block dependence」（272-273 も同じ）
    - 対して事前登録 §6.8:703-705「the session rows carry their times and durations in milliseconds, were not given to the attacks, and could undo the coarsening of the key rows」。§6.8:683-684 の規則は Wilson の上端そのままで、依存の分を見込まない。
  - なぜ問題か: キットを読む読者は、`no_time` の key 行に `ime_shadow` 行（ms の時刻と長さを持つ）を添えた形を「publishable form」として評価済みと受け取りうる。`no_time` の下では、`dwell_ms` は「すでに使われている」key の時刻を補うのではなく、消した時刻を戻す。基準 6（粗くするやり方は用途に依る）に照らすと、公開の形の記述が 2 か所で食い違うのは実務上いちばん危ない。
  - 解消の条件: README の「publishable form」を「key rows」に直す。254-256 の理由を事前登録の文に置き換える。余裕の幅について、事前登録の規則は依存を見込まず、ブロックの区間は記述であると書く。
  - 自信: 高

- **[severity: minor] 2. 層 none の試行ごとの差で重み付けし直すと、一致の方向に偏る**
  - 位置と引用: §6.7:637-639「reported twice: over every trial of the scope, and over the trials of the scope in none of the layers of section 6.4, for which reweighting to another mix of scenarios is meant.」。§3.1:226「113 trials send the minus, comma or period key (76 of them are S12 trials, in which these keys type ho, ne and ru)」
  - なぜ問題か:
    - 重み付けし直しのために除くべきなのは、隣の試行とのあいだの汚染（`carried out` と `received carry`。行の重なりが最大の試行に割り当てるので、両方を除く必要がある）である。
    - `closing key in reading` は、その試行自身の読みに由来する、規則が予測する食い違いである。自然な日本語の入力でも、読みに「ー」「、」「。」が入るたびに起きる。これを除いた値で重み付けし直すと、自然な入力より一致がよく見える。
    - S12 の層 none は「ほ・ね・る」を含まないかなの列だけ（S12 の約 3 分の 1 を除く）で、内容で選んだ部分集合になる。
  - 解消の条件: `carried out`・`received carry` だけを除く版を足し、重み付けし直しにはそれを使うと書く。または、層 none の版はこの理由で一致の方向に偏り、S12 などの値はそのシナリオを代表しないと §6.7 と §7 に書く。
  - 自信: 高（仕組み）／大きさは中

- **[severity: minor] 3. 「読者は自分のデータに打ち切りの規則を当てられる」は、観測器のログだけでは成り立たない**
  - 位置と引用: §6.4:548-551「the effect of the cut-off on a researcher's aggregates follows from the rule itself, which a reader can apply to the lengths of the sessions in their own data: a session of 20 seconds or more has no row」
  - なぜ問題か:
    - 打ち切られたセッションには行が無い。macOS では入力モードの切り替えも記録されない（§6.8:645「input-mode switches are not recorded on macOS」）。そのため、観測器のログしか持たない読者には、どの英字の連なりが打ち切られたセッションだったのか、何件あったのかが分からない。
    - 失われるのは 20 秒以上の変換、つまり候補を長く迷った変換である。基準 3（「More pauses and longer pauses are related to a larger cognitive load」）に照らすと、書字研究が最も知りたい部分にあたる。
  - 解消の条件: 文を「読者は、変換が 20 秒以上続く割合を別の情報源から見積もる必要がある」と直し、§7 の打ち切りの項に足す。key 行から推し量る手がかり（行の区間に入らない英字の連なり）を示すなら、入力モードが分からない限り、英語入力と区別できないことも書く。
  - 自信: 高

- **[severity: minor] 4. §1.2 の問 4 が §6.8 の範囲より広い**
  - 位置と引用: §1.2:54-56「Given only a published log, ... Which granularity of the published log keeps identification near chance?」。対して §6.8:680-681「The recommendation considers only the two sets that keep no time」、703「the key rows of a log published without its session rows」
  - なぜ問題か: 問いの文だけを読む読者（要旨を書く段で最も効く）は、時刻を含む粒度の中から選ぶ研究だと受け取る。
  - 解消の条件: 問 4 を「時刻を持たない key 行の 2 つの粒度のうち、句の識別を near chance に保つのはどれか」と、§6.8 の範囲に合わせる（major-B の単位も含めて）。
  - 自信: 高

- **[severity: minor] 5. 中止に数える「説明できない余分な行」の基準が事前に決まっていない**
  - 位置と引用: §3.4:338-339「or when one of its logs holds a row without a press the executor sent that cannot be explained」。data.md:44-46「A run that does not meet this is not deposited until the extra rows are explained ... a run whose extra rows cannot be explained counts as an aborted attempt」
  - なぜ問題か: やり直しの判断を、ログ（配送の報告）を見た後に、基準の無い「説明」で行う余地がある。停止規則に研究者の自由度が残る。やり直しは入力法の学習も加える（§7:792-793）。
  - 解消の条件: 説明として認める理由を閉じた一覧で先に書く（または「上限を超える行が 1 つでもあれば中止」とする）。判断した人と日時を、一致の解析の前に記録すると書く。
  - 自信: 中

- **[severity: minor] 6. ブロックの全か無かの合わせ直しは、実ログで一度も試していない**
  - 位置と引用: §6.8:649-650「A block whose observed presses do not agree with the plan (a press missing, added or changed) is not scored」。pilot-macos.md:142-143「Every press of a key the observation records produced a row」（数えただけで、区分の並びは比べていない）。§3.1:216-217「no text-recoverability ... analysis was run on pilot data」
  - なぜ問題か: 1 ブロックは約 25 試行で、区分の並びが 1 つでも食い違えばブロックごと捨てる。系統的な区分の違い（キーの対応表の 1 つの誤り）があると、大半のブロックが採点されず、推奨が出ない。これまで確かめたのは selftest の合成データだけである。
  - 解消の条件: パイロットですでに読んだ key 行に、攻撃をせずに `align_plan` だけを流し、採点されたブロックの割合を §3.1 に報告する（セッション行には触れない）。流さないなら、流していないと書く。
  - 自信: 中

- **[severity: nit] 1. 依存の文が自己矛盾に読める**
  - 位置と引用: §6.8:705-706「Dependence within a block would widen the interval and make the rule easier to meet」（§7:817 も同じ趣旨）
  - なぜ問題か: 区間が広がれば上端は上がり、規則は満たしにくくなる。言いたいのは「真の不確かさが Wilson の区間より広くなるので、Wilson の区間を読む規則は、本来より満たしやすい」だが、文はその逆にも読める。
  - 解消の条件: 上の言い換えのように、どの区間が広がり、どの規則が満たしやすくなるのかを書き分ける。
  - 自信: 高

---

### 5. 総合の推奨: **major**（直して再査読）

1. round 2 の major 3 件のうち 2 件は解消した。しかし新 3 は直しの過程で、問 3 の主の推定の対象（件数・割合の指標と ICC）を、また設計の long の割合に依存する形で定義した（新 major-A）。主の推定の定義なので、凍結の前にもう一度見たい。
2. E2 の推奨は時刻を持たない 2 集合に絞られて筋が通った。一方で、単位が句 1 つであることがどこにも書かれておらず、読者はログ全体の安全として持ち帰る（新 major-B）。公開物の README もセッション行について逆のことを言う（新 minor-1）。
3. どちらも直し方ははっきりしている（定義の書き直しと selftest、範囲の文、README の整合）。直した後の再査読は §6.4・§6.7・§6.8・`l2.py` の `aggregate`・README に絞ってよい。

---

### 6. 読めなかった範囲と注入の疑い

**読んでいない**:
- 事前登録の §2（80-181 行。round 3 で変わっていない節）
- `plan_config.macos.json`・`config.json`・`SEED`・`run.sh`・`env.md`
- `kit\gen`・`kit\e3`・`kit\run`・`kit\pilot`・`kit\logger`・`kit\emit` の README、`recipes*.json`・`keymap_macos.json`
- `pilot-macos.md` の 1-99 行
- コードの `gt_sessions.py`・`l1.py`・`stats.py`・`delivery.py`・`generate_plan.py`・`run_cell.py`・`clock_sync.py`・`seal_obs.py`・Rust の 3 ファイル

**一部だけ読んだ**:
- `spec_predict.py`: `summarise_trials` だけ
- `match.py`: `layer_none_trials` の箇所だけ
- `open_set.py`: grep だけ
- `closed_set.py`: 356-464 行と 549-763 行
- `pipeline.py`: 180-200 行と 590-740 行
- `l2.py`: 1-150 行と 300-838 行（`text_layout`・`aggregate` の本体は docstring だけ）
- `refinput-macos\README.md`・`gt_rules.json`: 変わった文だけ
- 接地の 2 本: 基準の箇所を grep と部分の読みで当たり、全文は読んでいない

**注入の疑い**: なし（読んだ範囲に、査読者や LLM に向けた指示は見当たらなかった）。
