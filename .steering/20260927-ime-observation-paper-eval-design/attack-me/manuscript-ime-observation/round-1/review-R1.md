# 査読報告: 計時の道具の検証と方法比較（一致の解析）の立場の査読者／懐疑家（stage manuscript・round 1）

対象: `C:\GSE-prototype\papers\ime-observation\manuscript\` の原稿（main.tex と sections・generated・supplement）。値は組んだ PDF のテキスト（`...\round-1\tmp\rendered\main.txt`）と `generated\*.tex` で確かめた。

---

## 1. 接地（この立場が論文に求める基準・逐語）

- **G1 外部の基準で自分の道具を確かめ、信頼区間を添える**: Plant (2016)「The sobering fact of the matter is that without using external chronometry there would be little chance of noting that stimuli had been presented for double the amount of time!」／「I would propose that researchers self-validate their own timing accuracy using external chronometry (e.g., using a Black Box ToolKit or oscilloscope) and state confidence intervals on publication.」
- **G2 理想化した入力は実地を代表しない**: Plant (2016)「benchmarking various experiment generators using idealized equipment and simplified scripts is counterproductive, lulls researchers into a false sense of security, and is unrepresentative of what they do and may achieve in the field.」／Pinet et al. (2017)「A limitation of this approach is that their manipulation involved fixed intervals and a single button. A crucial and original feature of the present study is the use of three distinct keys from the keyboard, and the generation of variable delays between keys, just as it happens in actual experiments involving sequence production.」
- **G3 物理の経路の精度と、背景の負荷を報告する**: Pinet et al. (2017)「Standard keyboards are connected through USB ports sampled at a rate of 125 Hz (i.e., every 8 ms).」／「This confirms that we should not expect a precision higher than 8 ms on actual IKI measurements.」／「the delay between programmed and recorded responses is probably a mixed result of the load of ongoing programs running in the OS」
- **G4 差の分布（正規性・大きさとの関係）を確かめてから一致の限界を読む**: Giavarina (2015)「Normal distribution of the differences must always be verified, for example by drawing a histogram. If this is skewed or has very long tails the assumption of normality may not be valid.」／「It is important to evaluate the differences at different magnitudes of the measured variable.」
- **G5 許容の限界は前もって、目的に照らして決める（決めるのは利用者）**: Giavarina (2015)「The B&A plot method only defines the intervals of agreements, it does not say whether those limits are acceptable or not. Acceptable limits must be defined a priori, based on clinical necessity, biological considerations or other goals.」／Plant (2016)「Determining the levels of accuracy needed in a given experiment, or research area, is solely the responsibility of the researcher」
- **G6 相関に似た指標は試料の広がりで決まる**: Giavarina (2015)「A high correlation for any two methods designed to measure the same property could thus, in itself just be a sign that one has chosen a widespread sample.」

---

## 2. 評価表

| 項目 | 点 | 所見 |
|---|---|---|
| a 主張と根拠の一致 | 3 | 事前登録・逸脱・停止規則の開示は丁寧で、「外部の基準ではない」ことも各所で認めている。一方で、結論と序論が Windows で働く経路を「窓のイベント」と言い切っている（経路は特定していないと書いた §4.4 や、§3.2 の観察と食い違う）。表 4 は Windows の変換を「Yes」と書いているが、分割の割合が 0.97 に達する。§5.8 は「値はすべて結果ファイルから」と書くが、手で写した値がある。§6.3 と §5.3 では macOS の定義が食い違う。 |
| b 方法の穴 | 3 | 凍結・盲検・予測による分解・ブロックを単位とするブートストラップは、この分野の水準より上。穴は次のとおり。(i) dwell の差の裾が非常に重いのに、パラメトリックな一致の限界だけで要約している（G4）。(ii) ICC が退化している欄がある（G6）。(iii) Windows では構成概念が違うのに IoU 0.5 の照合を使っており、「検出できなかった」と「短く検出した・分割した」が分けられない。(iv) 合成入力の代表性に穴がある（かな配列、壁時計と NTP、注入の経路）（G2）。 |
| c 持ち帰れるもの | 2 | キット・データセット・予測という枠組みは価値が高い。しかし要旨と結論の数値（層の区間の範囲。全試行の範囲は 6 か所が 0.000–1.000）からは、読者が一致の典型を読み取れない。下端を決めている層（macOS は S6・S10、Windows は S1・S2・S8 の fast）と、その機構も本文で説明されない。 |
| d 簡潔さと構成 | 2 | 約 21,100 語・66 頁・表 18（うち横向き 10）。同じ断り書きの繰り返しが外枠の段から減っていない（引き継ぎ 16）。Discussion の節が無いので、結果の解釈と先行研究との照合を置く場所が無い。 |
| e 規程への適合 | 3 | 要旨は 249 語（上限 250）、Declarations の見出し、References の直前の Open Practices Statement は満たす。満たさない点: タイトル頁に責任著者の住所と電話が無い。データセットとコードのリリースが参考文献の一覧に無い（データの引用の規程）。投稿時の確認にある "effect size" の語が本文に無い。二重の行間と右上の頁番号は確かめられない（抽出したテキストでは頁番号が頁末にある）。 |
| f 先行研究の位置づけ | 3 | 記録器の比較表と計時の検証の節（§2.4）はよく揃っている。ただし結果を先行の検証（Pinet の 8 ms の量子化、hybrid logger）と照らす場所が無い。一致の方法は Bland & Altman (1986) だけを引いており、差が正規でないときの扱い（Giavarina の文献表にある Bland & Altman 1999 など）に触れていない。 |

---

## 2b. 引き継ぎの判定（外枠 R1・round 2 → 原稿）

| # | 判定 | 根拠（原稿の位置と逐語） |
|---|---|---|
| 1 | 解消 | main.tex:109-113「the scope set aside … of trials, and carry-over between trials excluded … over all trials recall spanned …」、conclusions.tex:18-22 も同じ規則。⚠️ ただし規則に従った結果、新しい穴ができた（下の M1） |
| 2 | 解消 | main.tex:102-103「over the strata keeping at least 30 trials in the primary scope」と「(strata left out: …)」。⚠️ 外した理由が混ざっている（m9） |
| 3 | 解消 | recommendations.tex:32-37「it reads the reference side only and does not estimate the logger's agreement. Re-estimating the agreement requires the registered plan in full … no shorter registered check exists for macOS.」 |
| 4 | 解消 | related.tex:91-95「because its question is agreement with the calls that an application receives from the input method, which no external device observes」、method.tex:62-65 と脚注 64-65 |
| 5 | 解消 | method.tex:255-260「the $i$-th row was paired with the $i$-th press … from 20~ms before its start to 300~ms after its end」、table-key-timing.tex の caption「The times are whole milliseconds」 |
| 6 | **未解消** | 原稿のどの .tex にも "effect size" の語が無い（Grep で確かめた）。→ m8 |
| 7 | 解消 | method.tex:181-184「Outside S6 and S13 the smallest holds 31 trials on macOS and 32 on Windows … S6 … keeps as few as 3 trials at the slow speed on macOS and 30 on Windows」 |
| 8 | **未解消** | results-agreement.tex:18-20「the process that ran it was ended while the machine was short of memory」。試行 1 を止めたのが誰か・何か、試行 2 の間に計測機で何が動いていたかは書かれていない。→ m5 |
| 9 | 一部 | 限界は足された（limitations.tex:17-18「They hold for an unknown mixture of the logger's two paths」）。安全弁のテスト（`main.rs`）は名指されていない。→ n1 |
| 10 | 一部 | 定義は書かれた（method.tex:279-281「Their differences combine the offsets of the processes' clocks with the delays of the paths」）。KT1 の遅れとの関係（マーカーの「observation minus executor」は KT1 の遅れと同じ量）は書かれていない。→ m7 |
| 11 | 一部 | declarations.tex:53-54 は「the figures of the records … are copied from the run records」と 2 つの写し元に分けた。しかし method.tex:336-338 は「Every result value in this article is copied from the result files by a script」のまま。→ m6 |
| 12 | 解消 | 表 9（generated/table-reference.tex）に、不一致の種類・届き方・焦点の喪失・マーカーの時刻差がある |
| 13 | 解消 | observability.tex:63-65「on a Windows~11 machine whose build was not recorded … (an observation made in August 2026)」 |
| 14 | 解消 | related.tex:95-97「is read together with their figures for the physical part」、limitations.tex:35-38。（数値を引けばなお良い。n3） |
| 15 | 解消 | method.tex:249-250「no check is used to exclude trials or to adjust values」、limitations.tex:64-66「the runs analysed can be selected for the absence of such errors」 |
| 16 | **未解消** | 20 s の打ち切りが logger.tex:77, 89-94, 132（表 3）、method.tex:157, 295-297、recommendations.tex:17-20、limitations.tex:43-44 で述べ直されている。プールした Wilson 区間の断りは method.tex:186-187, 327-328、results-agreement.tex:152-153、limitations.tex:58-59 の 4 か所（外枠では 2 か所だった）。→ m14 |

---

## 3. 指摘の一覧（重い順）

- [severity: major] 要旨と結論の「層の区間の範囲」は、設計上決まっている値か、規則が予め不一致を指定した層で決まっており、一致の典型を伝えない
  - 位置と引用: main.tex:111-113「over all trials recall spanned \rv{macos-standard-live-off.all.recall.range} and …」（組むと 6 か所がすべて「0.000–1.000」。rendered p.1）。main.tex:103-105「the Wilson intervals of recall spanned 0.280–1.000 and 0.301–1.000」（rendered p.1）。results-agreement.tex:139-145 と conclusions.tex:20-28, 38-40 も同じ。
  - なぜ問題か: 全試行の範囲は S13（打ち切りを越えるように設計した場面）の recall 0 があるので、データを取る前から 0.000 で始まることが決まっている。主の範囲の下端は、macOS の live off では S6 fast（0.386 [0.280, 0.503]、detection-strata.tex:112）と S10 mid・fast（0.500・0.493、:120-121）で決まる。どちらも登録 §6.4 が「Disagreements that the rules predict (for example the session of S6 kept open by Backspace …, the session of S10 closed by Tab …)」と予め挙げた不一致である。他の層の大半は recall 0.89–1.00。プールすると主の範囲で 0.896、全試行で 0.689（values.tex）。打ち切りの代償（約 0.2）も典型の値も、要旨からは読めない。規程の「BRM readers want practical solutions」に対して、要旨は情報を運ばない数を約 40 語ぶん載せている。
  - 解消の条件: (1) 範囲の下端を決めた層とその理由（規則が予め指定した不一致か）を、要旨と §6.3 に評価語なしで書く。場面名は推定値ではないので、外枠の規則とも矛盾しない。(2) 登録 §6.1 が「labelled as pooled」とすることを許すプールの推定値（主の範囲と全試行）を、要旨か結論に添える。(3) 全試行の範囲が設計上 0 から始まることを本文で 1 文断る。外枠の規則（登録の外）から離れる部分は、Open Practices Statement で開示する。
  - 自信: 高

- [severity: major] dwell の差の裾が非常に重いのに、パラメトリックな一致の限界で要約している。正規性の確認も、大きさとの関係を見る図も無い
  - 位置と引用: method.tex:312-313「summarised by its median absolute value and by the Bland--Altman bias and 95\% limits of agreement」。table-session.tex:10「$-$427 [$-$561, $-$300] & $-$3,236 … & 2,382 … & 36 [32, 41]」（macOS live off・slow: 中央絶対差 36 ms に対し、一致の限界は −3.2〜+2.4 s）。Figure 3（fig-dwell）は層ごとの偏りと限界だけ。
  - なぜ問題か: 中央絶対差が数十 ms で、標準偏差が約 1.4 s。大半の対は数十 ms で一致し、一部が秒の単位で外れている混合である。bias ± 1.96 SD は、そのどちらも表さない。読者は「dwell は ±2 s ずれる」と誤読するか、外れの機構を見落とす。Giavarina「Normal distribution of the differences must always be verified … If this is skewed or has very long tails the assumption of normality may not be valid.」／「It is important to evaluate the differences at different magnitudes of the measured variable.」
  - 解消の条件: 探索的と標識して、セルごとに差の分布（ヒストグラムか ECDF）を示す。百分位で求めた 2.5／97.5 の限界を出す。閾値を置かない記述として、±100 ms・±1 s に入る割合を示す。差を平均の長さに対して描いた Bland–Altman の散布図を少なくとも補遺に置く。秒の単位の外れがどの場面から来るか（予測の層を使う）を本文で 1 段落書く。
  - 自信: 高

- [severity: major] Windows の照合（IoU 0.5 の 1 対 1）は構成概念の違いを「見逃し」として数え、表 4 の「変換を計算できる」は根拠を越えている
  - 位置と引用: logger.tex:157「Conversions and their duration & Yes & Yes & Detection and duration」。detection-strata.tex:1067「S1 & fast & … & 0.571 [0.455, 0.681]」、:1068「S2 & slow & 42 & 42 & 82 & 1.000 … & 0.512 … & 0.952」、:1086「S8 & slow & … & 0.969」（分割の割合）。dwell の偏りは −550〜−1,006 ms（table-session.tex:16-18）。
  - なぜ問題か: 窓が出ている区間は、合成の区間の一部分であることが系統的に予想される。そのため IoU 0.5 を下回った対は、検出したが短かった場合でも「miss と false positive」に数えられる。recall が slow から fast で 0.97 から 0.53–0.57 に落ちるのが窓の検出の失敗なのか、重なりの割合の問題なのかを、主の解析は区別できない。slow の S2・S8 では合成 1 つあたり行がほぼ 2 つあり、研究者が数える「変換の回数」は窓の出現の回数である（per-text の conversions per trial の偏りは +0.17、table-text-agreement.tex:34）。
  - 解消の条件: 探索的な感度分析を加える。(a) 参照の合成と少しでも重なる行が 1 つ以上ある割合。(b) 包含で照合したときの recall。(c) 合成 1 つあたりの行の数の分布。表 4 の Windows の欄は「窓の出現（1 つの合成が複数の行になる。分割は場面と速さで最大 …）」に書き換える。
  - 自信: 高（構成と数値）／中（機構の解釈）

- [severity: major] ICC(A,1) に退化した値と、設計で決まる値が混じっており、表のままでは「一致しない」と誤読される
  - 位置と引用: table-text-agreement.tex:10「Conversions per trial & slow & 117 & 0.034 … & 0.000 [$-$0.000, 0.000]」（macOS live off の 3 速度と、Windows の slow・mid も同じ）。:19-21 Fraction of time converting は ICC 0.000–0.003。results-text.tex:10-12「the ICC relates the variation between texts to the total variation, so it also depends on how much the texts of this design differ」。
  - なぜ問題か: live off では計画との不一致が 0 件（table-reference.tex:12）なので、主の範囲の各試行は参照の会話をちょうど 1 つ持ち、参照の「変換の回数」は文の間で一定である。分母の文間の分散がほぼ 0 なので ICC は定義上 0 になり、狭い区間が付くことで精密な「一致なし」に見える。時間の割合のほうも、試行ごとに独立に引いた思考時間を 8 試行で平均するので、文の間の差が小さい設計である。Giavarina「A high correlation … could thus, in itself just be a sign that one has chosen a widespread sample」の裏返しにあたる。
  - 解消の条件: 各 ICC の横に、参照の文間の SD（または文間の分散の成分）を示す。参照が一定の欄は、ICC を値でなく「参照の分散が 0 のため解釈できない」と理由つきで示す（登録 §6.7 の「An interval is withheld, with the reason, when its statistic is undefined」の趣旨を値にも及ぼす）。§7 で、これらの欄は一致の限界で読むと明記する。
  - 自信: 高

- [severity: major] 結論と序論が、Windows で働いた経路を「窓のイベント」と言い切っている
  - 位置と引用: conclusions.tex:8-11「Windows offers events of the input method's windows that carry no text, which the logger follows … that the Windows route works was established only for the input method measured」。introduction.tex:32-33「Windows offers the window events of the input method」。一方で logger.tex:105-107「which path drove the measured input method was not determined」と observability.tex:63-65「the window events of the input method did not arrive」。
  - なぜ問題か: 測った入力方式について原稿が持つ観察は、むしろ窓のイベントが届かず、隠蔽（cloak）の経路で追うことを示す。結論はその逆を確立済みのように読ませる。また、20 s 以上続いた参照の会話が 605 あるのに 20 s 以上の行が 0 であること（results-agreement.tex:185-199）は、窓のイベントの経路の仕様（打ち切りなし・25 s の安全弁）と合わない。その含意は書かれていない。
  - 解消の条件: 結論と序論を「two routes (window events and cloaking); which drove the measured input method was not determined」に直す。20 s 以上の行が無いことが、どちらの経路の仕様と整合するかを、断定せずに 1 文書く。
  - 自信: 高（矛盾）／中（20 s の推論）

- [severity: major] Discussion が無く、不一致の機構や先行の検証との照合が本文のどこにも無い。分量に対して持ち帰れるものが少ない
  - 位置と引用: main.tex:127-140（節は Results → Dataset → Recommendations → Limitations → Conclusions）。results-agreement.tex:163-164「No arithmetic relation between the three comparisons is claimed.」
  - なぜ問題か: gt_pred が gt_obs とほぼ同じで、pred_obs が 0.85–1.00 である（results-agreement.tex:155-163）。これは「記録器は規則どおりに動き、参照との不一致の大半は規則（構成概念）から来る」ことを示す、この設計のいちばん持ち帰れる事実だが、本文は数を並べるだけである。macOS の S12（かな配列）の分割、Windows の速さに伴う recall の低下、dwell の秒単位の外れの機構も説明されない。KT1 の 1 ms を Pinet の「not expect a precision higher than 8 ms on actual IKI measurements」と照らす場所も無い。評価語を避けることと、機構を説明することは両立する。
  - 解消の条件: 短い Discussion（2〜3 段落）を置く。(1) 予測による分解で不一致の出どころを、層の表（補遺）を引いて書く。(2) 規則が予め指定した不一致と、予期しなかった不一致を分ける。(3) KT1 と dwell の誤差を、物理の経路の既知の誤差（G3）と書字研究の分析の尺度に照らして記述する（判定はしない）。そのぶん繰り返しの断りを削る（m14）。
  - 自信: 中

- [severity: minor] macOS の「解析の定義」が §5.3 と §6.3 で食い違う
  - 位置と引用: method.tex:100-101「the ground truth was formed under the definition of the cell's system: on macOS every session」。results-agreement.tex:172-173「On macOS the definition of the analysis (the sessions that showed a candidate window) and the definition that keeps every session held the same sessions」
  - なぜ問題か: macOS の参照は候補の窓を記録しない（§5.3 の記録項目に無い）。§6.3 の括弧は Windows の定義である。
  - 解消の条件: §6.3 を「On macOS the definition of the analysis is every session, so the two coincide by construction」などに直す。
  - 自信: 高

- [severity: minor] Windows では 2 つの定義が別の会話の集合を持つが、その差の大きさと、共通の定義での推定値が本文に無い
  - 位置と引用: results-agreement.tex:173-175「On Windows they did not … the estimates above are those of the definition of the analysis」。method.tex:104-105「whether the two definitions hold the same sessions is reported per cell」
  - なぜ問題か: 「同じでなかった」だけでは、主の推定値が定義の選び方にどれだけ敏感かを判断できない。
  - 解消の条件: 候補の要素が無かった会話の数と、共通の定義での recall・precision（プール）を 1 文で示す（表は補遺）。
  - 自信: 中

- [severity: minor] かな配列では記号のキーで打つかな（濁点 ゛ を含む）がすべて会話を閉じる。原稿はローマ字の場合しか書かず、S12 の文字の集合も示していない
  - 位置と引用: logger.tex:73-75「The minus, comma and period keys, which in Romaji input type a long-vowel mark, a comma and a full stop inside a reading, close a session」。limitations.tex:41-43。method.tex:158-159「the kana strings of S12, typed with the kana keyboard layout, had four to eight characters」。ソースの ime_compose.rs:316-317「// その他 (Tab / 記号 / ファンクションキー) — IME の自動確定にあたる。 _ => finish(prev, false, now_ms),」。結果は detection-strata.tex:122-124（S12 の precision 0.713–0.775、分割 0.147–0.213）。
  - なぜ問題か: JIS のかな配列では @・[・;・:・]・/・^ などのキーでかな（濁点・半濁点を含む）を打つ。登録 §4.5 が挙げるのは ho・ne・ru だけである。S12 の文字列が自然なかな入力の文字の頻度を代表しなければ、S12 の一致は実地を代表しない（G2）。
  - 解消の条件: §4.3 と §12 に「かな配列では記号のキーで打つ文字ごとに会話が分かれる」と書く。S12 の生成に使った文字の集合と、記号のキーを含む割合を示す。
  - 自信: 高（規則）／中（影響の大きさ）

- [severity: minor] キー行の時刻をいつ取ったか（イベントの時刻か、コールバックで読んだ壁時計か）と、検証で NTP を止めた条件の代表性が書かれていない
  - 位置と引用: logger.tex:18-19「a row with the time on the wall clock in whole milliseconds」。method.tex:42-43「with automatic updates, network time synchronisation … turned off」。ソースの driver_macos.rs:114「SystemTime::now()」
  - なぜ問題か: KT1 が何を検証したかは、時刻を打つ点で決まる（登録 §4.5 は「the time at which the event reached the observer」と書くが、原稿には無い）。実地では NTP が動くので、壁時計の行の間隔は時刻の調整の影響を受けうる。検証はその条件を外している（G2）。
  - 解消の条件: §4.1 に、時刻を読む点と時計の種類を 1 文で書く。§12 に、NTP を止めた検証と実地の違いを書く。
  - 自信: 中

- [severity: minor] 注入したイベントの経路は「ソフトウェアの部分」のすべてではない
  - 位置と引用: related.tex:95-96「The timing of the key rows that this study reports covers the software part of the path that the validations above measured from the key to the record」
  - なぜ問題か: SendInput や CGEventPost で注入したイベントは、HID の処理と OS の入力処理の一部を通らない。先行の検証（Pinet）が測った区間のうちソフトウェアの部分を、全部覆うわけではない（G3）。
  - 解消の条件: 「from the point of injection to the row」に狭める。記録器が注入したイベントを物理のイベントと同じように扱うか（Windows の注入の印を見ないか）を 1 文書く。
  - 自信: 中

- [severity: minor] 試行 1 を止めたもの、メモリ不足の原因、試行 2 の間の背景の負荷が報告されていない（引き継ぎ 8）
  - 位置と引用: results-agreement.tex:18-20「when the process that ran it was ended while the machine was short of memory」
  - なぜ問題か: Pinet「the delay … is probably a mixed result of the load of ongoing programs running in the OS」。8 GB の機械でメモリが足りなくなった原因が分からなければ、試行 2 の遅れ（最大 140.83 ms）と入力方式のふるまいへの影響を読めない。
  - 解消の条件: 誰が・何が止めたか、試行 2 の間に動いていたプロセス（分かる範囲）、分からなければ「記録していない」と書く。
  - 自信: 高

- [severity: minor] 「値はすべて結果ファイルから」が言い過ぎ（引き継ぎ 11）
  - 位置と引用: method.tex:336-338「Every result value in this article is copied from the result files by a script」。手で写した値の例: results-agreement.tex:18「about 21 minutes」、:27「for 2.7~s」、method.tex:41「39 of 39」、method.tex:209-211
  - なぜ問題か: Declarations（declarations.tex:53-54）の 2 つの写し元と矛盾する。
  - 解消の条件: §5.8 を Declarations と同じく 2 つの写し元に分けて書く。
  - 自信: 高

- [severity: minor] マーカーの時刻差と KT1 の関係が書かれていない（引き継ぎ 10）
  - 位置と引用: method.tex:278-283「Marker times.」の段。results-agreement.tex:96-107
  - なぜ問題か: 記録器から実行器を引いた値（中央 1 ms、範囲 0〜97）は、KT1 の遅れ（中央 1.0、最大 95）と同じ量を別の打鍵で測ったもの。読者は 2 つを別の結果と読む。
  - 解消の条件: 1 文で関係を書く（同じ定義で、マーカーは KT1 の部分集合）。
  - 自信: 高

- [severity: minor] 規程の "effect size" の語が無い（引き継ぎ 6）
  - 位置と引用: 原稿の .tex に該当なし。規程「the manuscript includes appropriate measures of variability, effect size, and (when relevant) statistical power」
  - なぜ問題か: 投稿時の確認の項目に、どれが当たるかの対応が本文に無い。
  - 解消の条件: §5.8 に「the bias, the limits of agreement, kappa and ICC are the effect sizes of this study」と 1 文書く。
  - 自信: 高

- [severity: minor] 要旨の「strata left out」は、30 試行に満たない層・値の無い層・設計で範囲に入らない S13 を区別していない
  - 位置と引用: main.tex:106-108「(strata left out: \rv{…recall.strata.left} and …」（組むと「4 and 6」）
  - なぜ問題か: 外枠の規則は「(strata with fewer trials or no value)」と理由を持っている。macOS live on の 6 のうち 3 は S13（範囲に試行が無い）。
  - 解消の条件: 本文の §6.3 で内訳を書く（要旨は語数の都合でそのままでもよい）。
  - 自信: 中

- [severity: minor] 許容の限界を設けないことの帰結（利用者が自分の目的で前もって決める）を、推奨として書いていない
  - 位置と引用: method.tex:330-331「No threshold of adequate agreement was set」。recommendations.tex:7「The recommendations below set no threshold of adequate agreement.」
  - なぜ問題か: Giavarina「Acceptable limits must be defined a priori」と Plant「Determining the levels of accuracy needed … is solely the responsibility of the researcher」によれば、閾値を置かないのは正当である。ただしその場合、利用者がどう決めて、データセットでどう確かめるかを示すのが実用の要件になる。
  - 解消の条件: 推奨に 1 項を足す。「自分の解析の尺度（例: 休止の閾値）で許容の限界を前もって決め、補遺の層の値かデータセットで照らす」。
  - 自信: 中

- [severity: minor] 規程の不適合: タイトル頁に責任著者の住所と電話が無い
  - 位置と引用: main.tex:86-87（コメント）「The postal address and the telephone number of the corresponding author are given in the submission system only.」。規程「The title page must include … the corresponding author's address, telephone number, and e-mail address.」
  - なぜ問題か: 規程は投稿システムでなく、タイトル頁に載せることを求めている。
  - 解消の条件: タイトル頁（または別添のタイトル頁）に住所と電話を載せる。
  - 自信: 高

- [severity: minor] 規程の不適合: データセットとコードのリリースが参考文献の一覧に無い
  - 位置と引用: references.bib はデータの項目が事前登録の 2 件だけ（:6-21）。declarations.tex:28「deposited in Zenodo under the persistent identifier \tbd{DOI of the dataset}」、:35
  - なぜ問題か: 規程「Data citations should include a persistent identifier (such as a DOI), should be included in the reference list using the minimum information recommended by DataCite」。`\tbd` を埋めても、本文中に DOI が載るだけである。
  - 解消の条件: データセットとリリースを、DataCite の最小情報で参考文献に入れ、本文から引く。
  - 自信: 高

- [severity: minor] 繰り返しが減っていない（引き継ぎ 16）
  - 位置と引用: 上の 2b の #16 の位置。加えて「values of the two systems are not set against each other」の類いが §3.5・§6 冒頭・§7・Figure 4 の caption・§11(a)・§13 にある。
  - なぜ問題か: 約 21,100 語のうち、断り書きの重複が多い。
  - 解消の条件: 定義と断りは 1 回にして、他は参照にする。浮いた分量を Discussion（上の major）に回す。
  - 自信: 中

- [severity: minor] 書式（二重の行間・頁番号を右上）の確認
  - 位置と引用: main.tex:5「\documentclass[pdflatex,sn-apa]{sn-jnl}」。rendered の各頁で頁番号が頁末にある（例: main.txt:33「1」）
  - なぜ問題か: 規程「All manuscripts are to be double spaced and have 1” margins with page numbers in the upper right corner of each page.」
  - 解消の条件: 投稿用に二重の行間・1 インチの余白・右上の頁番号にする。
  - 自信: 低（PDF の体裁は見ていない）

- [severity: nit] n1 安全弁の実装とテスト（`main.rs`）を Code availability か §4.4 の脚注で名指す（引き継ぎ 9 の残り）。自信: 中
- [severity: nit] n2 KT1 の表に、|interval error| が 8 ms を超えた数（または割合）を加え、平均に区間を添える（Plant「state confidence intervals on publication」）。最大 ±94 ms の裾が IKI の解析に効くかを、読者が判断できるようにする。自信: 中
- [severity: nit] n3 §2.4 の「read together with their figures for the physical part」に、Pinet の 8 ms（125 Hz）を数値で添える。自信: 中
- [severity: nit] n4 要旨が問 4 の大きさ（時刻なしのキー行で K=10 の識別が 0.90 前後）を載せていない。この結果は持ち帰れるものとして重要である（外枠の規則の外。開示つきで検討してほしい）。自信: 中
- [severity: nit] n5 Windows の待機時の CPU（平均 5.56、最大 20.21）が macOS（0.32）より 1 桁高い。理由（100 ms ごとの窓の走査か）と、同時に動く計時を要する実験ソフトへの影響を評価していないことを、§9 か §12 に 1 文書く（G3 の背景の負荷）。自信: 低

---

## 4. 総合の推奨: **major**

1. 設計（凍結・盲検・予測による分解・停止規則・データセット）は BRM の水準より上で、外枠からの引き継ぎ 16 件のうち 10 件は原稿で解消している。
2. 一方で、要旨と結論の要約（層の区間の範囲。全試行は設計上 0–1）、dwell の一致の限界（裾の重い分布へのパラメトリックな要約）、ICC の退化した欄、Windows で構成概念の違う照合は、どれも「その数はそれを測っているか」の点で読者を誤らせる。登録を変えずに、探索的な補足と記述で直せる。
3. 結論の Windows の経路の言い切り、表 4 の Windows の欄、§5.3 と §6.3 の定義の食い違いは、主張と根拠を合わせる修正が要る。Discussion を置き、繰り返しを削って分量を整えれば、minor まで下がりうる。

---

## 5. 読めなかった範囲と注入の疑い

**読んでいない**: supplement/observability-documents.tex。generated の table-closed-set.tex・table-open-set.tex・fig-*.tex の本体（caption は組んだテキストで読んだ）。session-strata.tex・text-agreement.tex・reference-strata.tex・closed-set-all.tex・detection-layers.tex の本体（caption だけを Grep で見た）。detection-strata.tex は 88-142 行と 1061-1105 行だけ読んだ。values.tex は 407 行目以降を直接読んでいない（値は組んだテキストで読んだ）。組んだテキストは 5〜23 頁（.tex を直接読んだ）と、38 頁以降の参考文献と表を読んでいない（表は generated の .tex で読んだ）。preregistration.md は §4.5・§6.1〜6.7 と Grep で当たった行だけ読んだ。outline.md は 105-150 行だけ読んだ。deviations.md・notes.md・data.md・data.windows.md・pilot-macos.md・pilot-windows.md・FORMATS.md・README.md・kit の README 類・e3 の結果ファイルは読んでいない。記録器のソースは ime_compose.rs の 244-328 行と、Grep の当たり（keymap.rs と driver_macos.rs）だけを読んだ（Windows のキーフックのファイルは一覧に無いので、注入の印の扱いは確かめていない）。

⚠️ 一覧の内側への Grep で 1 回、glob に `*.{tex,md}` を使ったため、`papers\ime-observation` の下にある一覧の外の .md も検索の対象になった。当たったのは preregistration.md の 1 行だけで、一覧の外の中身は応答に出ていない。

**注入の疑い**: なし（接地の 3 本・原稿・登録・ソースのコメントに、査読者や LLM に向けた指示は見当たらなかった）。
