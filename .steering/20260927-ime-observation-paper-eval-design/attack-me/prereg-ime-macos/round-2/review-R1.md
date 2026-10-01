# round 2 の査読: BRM・打鍵と反応の時刻を測る道具を外部の基準で検証する伝統の立場（懐疑家の下位人格つき）

対象: `C:\GSE-prototype\papers\ime-observation\experiment\preregistration.md`（以下 PR。行番号は今の版）
**総合の推奨: minor（直してから凍結）。** round 1 の major 5 件のうち、M2 と M4 は解消した。M1・M3・M5 は部分的に解消。今回の直しで足した部分（§3.3 の精度の文・§6.4 の層・pred_obs）に、新しい穴が 4 つ見つかった。どれも文の直しか小さなコードの直しで消せる。

---

## 1. 接地（基準と逐語）

- **基準 1: 外部の基準で自分の装置を確かめ、区間を添える。**
  Plant (2016)「In closing I would propose that researchers self-validate their own timing accuracy using external chronometry (e.g., using a Black Box ToolKit or oscilloscope) and state confidence intervals on publication.」
- **基準 2: 測られる側は自分の誤りを知りえない。基準は測られるものから独立していなければならない。**
  Plant (2016)「the software or script being run can know nothing of the errors introduced by the hardware, rendering engine, or plug-in. It, just like the experimenter, will blindly act on and report the timings given without question.」
- **基準 3: 理想化した入力での検証は代表性を欠く。**
  Plant (2016)「benchmarking various experiment generators using idealized equipment and simplified scripts is counterproductive, lulls researchers into a false sense of security, and is unrepresentative of what they do and may achieve in the field.」
  「Generalization across apparently similar hardware types or categories of study is folly.」
- **基準 4: 合成の打鍵は実際の系列の構造に似せる。**
  Pinet et al. (2017)「A limitation of this approach is that their manipulation involved fixed intervals and a single button. A crucial and original feature of the present study is the use of three distinct keys from the keyboard, and the generation of variable delays between keys, just as it happens in actual experiments involving sequence production.」
- **基準 5: 打鍵 1 つずつ、予定と記録を突き合わせ、偏りとばらつきを出す。OS の中間層の影響は未知として扱う。**
  Pinet et al. (2017)「The programmed keystroke times were compared to those recorded through the jsPsych procedure.」
  「the difference between the programmed and recorded values had a mean value of 0 ms ( SD = 10 ms;」
  「The impact of this intermediate layer of software on keyboard chronometry is not known.」
- **基準 6: 一定の遅れ（accuracy）と試行ごとの揺れ（precision）を分ける。**
  Bridges et al. (2020)「Precision refers to the trial-to-trial variability of the measures: the jitter of the timing measurement or its "variable error". Accuracy refers to the "constant error" of a measurement which, in timing terms, is often referred to as the "lag", "offset" or "bias" from the true value.」
  「comparisons across packages are no replacement for testing the timing on the system being used」

---

## 2. 引き継ぎの判定（carryover-R1.md の 20 件）

| # | 判定 | 理由（1 行）と今の版の位置 |
|---|---|---|
| M1 | 部分的に解消 | ms の時刻を持つ集合は推奨から外した（PR:609-613）。しかし同じ段落が「Pauses between words and phrases, which human logs also carry, are not modelled either」（PR:614-615）と認めている。それなのに `bin1s`・`bin1s_count` を推奨に残した。人の記録では語・文節の境の休止（数百 ms〜秒）が 1 秒のビンに残るので、外した理由がこの 2 つにもそのまま当たる。消す条件は次のどちらか。2 つを推奨から外す（`no_time`・`counts_only` だけにする）。または「1 秒のビンの推奨は、人の休止の構造を持たない記録に限る」と規則の文に書く。 |
| M2 | 解消 | K = 1000 は記述だけにした。表も足した（PR:617-637）。K = 1000・c = 1 の値（0.210 / 0.067）はポアソン近似で再計算して一致した。 |
| M3 | 部分的に解消 | 範囲は観測器の定義と起点で決めるようになった（PR:491-505）。ただ §6.6 Cut-off の「the number of long sessions that nonetheless appear in a pair, split or merge (specified: zero)」（PR:560-561）の long は、§4.3「A session is reported as lasting 20 seconds or more when its duration reaches 20,000 ms」（PR:359-360）と `l1.py:286-296`（`_gt_dwell(s) >= limit_ms`）では、正解の側の期間で決まる。起点が観測器と違う。たとえば読みに読点を含む long の試行では、前半の行が正解の長いセッションと IoU 0.5 以上で対になりうる。だから「specified: zero」は仕様から出てこない。消す条件は次のどちらか。この数を予測の long で数える。または「zero」の主張を pred_obs に限る。 |
| M4 | 解消 | 予測・gt_pred・pred_obs・層を足した（PR:369-389, 507-526）。層の欠け（新 N3）と pred_obs の時刻（新 N4）は新しい指摘として下に出す。 |
| M5 | 部分的に解消 | §7 は足した（PR:692-722）。ただ PR:701-702 の「The sessions affected are visible through `n_continued_commits` (section 6.6)」は過大。§6.6 がこの値で分けるのは放棄だけで（PR:555-557）、検出と期間では見えない。消す条件は次のどちらか。検出と期間も `n_continued_commits` > 0 / = 0 で分けて出す。または §7 の文を「放棄で見える」に狭める。 |
| m1 | 部分的に解消 | 理由は書いた（PR:429-431）。しかし §3.3 自身が層の中の D を「at most about 1.8」（PR:296）と書く。これは半幅が最大で約 1.34 倍になることで、「small」とは言い切れない。量を書けば消える。 |
| m2 | 部分的に解消 | §4.4・§6.9 に回収の遅れを足した（PR:365-367, 667-669）。しかし `pilot-macos.md:131-133` は「could affect only sessions shorter than about 66 ms」のまま残り、§6.9 の約 370 ms と食い違う。新しく足した比較での遅れは新 N4。 |
| m3 | 解消 | PR:247-250 と `pilot-macos.md:154-159` が一致する。13.6 × 3,150 = 11.9 h、13.8 × 2,925 = 11.2 h も確かめた。 |
| m4 | 部分的に解消 | 順序は固定した（PR:232-234）。中止の後にやり直すとき、学習がどれだけ持ち越されるかが §3.4・§7 に無い。ON の中止が OFF の前にやり直されるのかも書いていない。 |
| m5 | 部分的に解消 | 除外せずに数えることは決まった（PR:460-462）。しかし焦点を失うと、入力法ではなく参照の側が呼び出しを受けない。すると観測器の行が主の gt_obs で偽陽性に数えられ、基準の失敗が観測器の負けになる。これを分けた gt_obs の数（焦点を失った試行を除いた副の値か、その試行の偽陽性の数）が無い。 |
| m6 | 解消 | PR:116-119。 |
| m7 | 解消 | 形容の禁止を足した（PR:436-437）。ただ §3.3 に精度の誤った主張が新しく入った（新 N1）。 |
| m8 | 解消 | 配送の報告（PR:481-487）。量子化の検査は足していないが、USB の経路を通らない設計なので重くない。 |
| m9 | 解消 | 計画の予定に対する送出の遅れを記述で出す（PR:481-482、`delivery.py:21-23`）。 |
| m10 | 部分的に解消 | 版の違いは逸脱として扱う（PR:465-466）。1,000 ms の閾値（`gt_rules.json:40`）の根拠は書いていない。 |
| m11 | 未解消（後退） | PR から、パイロットの生ログを預ける文が消えた。`pilot-macos.md:170-173` は「not yet deposited」のままである。また `data.md:39-43` は、本計測の預けも「not deposited until the extra rows are explained」と条件つきにした（J2・J4 に関わる）。 |
| m12 | 解消（事前登録の段では） | §7 に、基準をソフトの層に置く理由と「Software clocks」を書いた（PR:694-698, 712-714）。総説を原稿に回すのは J11 に照らして可。 |
| n1 | 解消 | 節の参照を全部たどり、誤りが無いことを確かめた。 |
| n2 | 解消 | PR:416-419。 |
| n3 | 部分的に解消 | コミットは人手で notes に書く（PR:405-408）。結果のファイルにコードのコミットが機械で入らない（研究者の選択）。 |

---

## 3. 評価表 a〜g

| 観点 | 点 | 所見 |
|---|---|---|
| a 主張と根拠の一致 | 3 | 目的の文は「参照入力欄が受けた呼び出しから組んだセッションとの一致」に絞られ、根拠と合った（PR:28-30）。ただ、新しく足した文の 3 か所が根拠より強い。§3.3 の「1/20 と 1/10 を分ける」（新 N1）、§6.4 の「the layers show where this happens」（新 N3）、§6.6 の「specified: zero」（M3 の欄）。 |
| b 方法の穴 | 3 | 主の範囲は観測器の仕様で試行を選ぶ。そのため遅い速さでは長い読みと長い思考時間が抜け、速さのあいだの比較が交絡する（新 N2）。予測の行の時刻には、仕様にある回収の遅れが入らない（新 N4）。問 4 は打鍵 1 つの欠けで全部止まる（新 N5）。入力モードの判定は、合成入力が最も都合の良い経路だけを通る（新 N6）。 |
| c 持ち帰れるもの | 4 | 「規則の妥当性」（gt_pred）と「実行の忠実度」（pred_obs）を分けて決定的な予測で示す枠組みは、推論で測る観測器を検証する一般の手法として持ち帰れる。打鍵ごとの配送の報告は Pinet et al. (2017) の、予定と記録の突き合わせに当たる。 |
| d 簡潔さと構成 | 3 | 本文は 9,326 語（+76%）。§6.4 の「Each analysis of questions 1 and 2 is computed under three scopes」（PR:492）が §6.6 の 2 つの範囲（PR:544-545）と合わないなど、節のあいだに食い違いが出た（新 N8）。 |
| e 規程への適合 | 3 | J6・J7（精度から n を決める・PR:244-246）、J8（思考時間への依存は探索として扱う・PR:122-124）、J9（除外を事前に決める・PR:441-456）は満たす。J2・J4 は、パイロットの生ログを預ける文が消え（m11）、本計測の預けも条件つきになった（`data.md:42-43`）。手順と正解の規則を決めたデータが預けられない恐れがある。 |
| f 先行研究の位置づけ | 3 | 外部の時計を使わない理由は書いた（PR:696-697）。しかし dwell の偏りや配送の遅れという ms の主張は、同じ機械のソフトの時計だけに立つ。Plant (2016)「blindly act on and report the timings given without question」への答えは、同じ機械の中での相互比較にとどまる、と原稿で明示が要る（原稿の段の課題として記録する）。 |
| g 固定の十分さ | 4 | 推定の対象・主の指標・範囲・比較・除外・n の根拠・停止の規則は 1 通りに決まった。残りは 4 つ。中止の後の順序と学習の扱い（m4）。§6.6 の long の定義が 2 通りに読めること（M3）。`log_truncated` がどちらのログかを書いていないこと（新 N8）。1,000 ms の根拠（m10）。 |

---

## 4. 新しい指摘（重い順。round 1 の再掲は入れていない）

### N1 [minor] §3.3 の精度の文が、表と Wilson 区間の非対称を取り違えている
- **位置と引用:** PR:264-265「With 75 trials a stratum's recall near 0.95 is located to within about 5 points, which separates an observer that misses about one session in twenty from one that misses one in ten, but not finer differences」
- **なぜ問題か:** 71/75（0.947）の 95% Wilson 区間は [0.871, 0.979] で、0.90 を含む。68/75（0.907）の区間は [0.820, 0.954] で、0.95 を含む。だから 75 試行では 1/20 と 1/10 を分けられない。表の値は p そのものではなく、n·p を丸めた数で計算されている（n = 34・p = 0.99 の 5.1 は 34/34 のときの値）。しかし PR:251-252 は「at the proportion p」と書く。接地: Plant (2016)「state confidence intervals on publication」。区間を添えるなら、区間で何が言えるかの文も正しくなければならない。
- **解消の条件:** 「分ける」の文を消すか、区間の下端（約 0.87）で書き直す。表の脚注に「整数の数 round(n·p) で計算した」と書く。
- **自信:** 高

### N2 [minor] 主の範囲 `under_limit` は、速さごとに読みの長さと思考時間で試行を選ぶ。速さのあいだの比較が交絡する
- **位置と引用:**
  - PR:720-722「how often a session is cut off depends on the design (think time, speed, S6, S13), so the fraction of long trials is a property of this design, not of natural typing.」
  - PR:274-276 の表（S1 slow 34/75。思考の休止が無い S3 でも slow は 60/75）
- **なぜ問題か:** S3 は打って Return だけなので、slow で打ち切られる 15 試行は読みが最も長い試行である。主の範囲の slow の層は、短い読みと短い思考時間に偏った部分集合になる。だから slow と fast の差（dwell の偏り・recall）には、速さの効果と読みの長さの選別が混ざる。§7 は割合が設計に依ることだけを書き、残る試行の組成が変わることを書いていない。接地: Plant (2016)「unrepresentative of what they do and may achieve in the field」。
- **解消の条件:** 3 つを足す。
  1. 層と範囲ごとに、読みのキー数と思考時間の分布（中央値と範囲）を報告すると事前に書く。
  2. §7 か §6.1 に「`under_limit` での速さの比較は、読みの長さと思考時間の選別と交絡する」と書く。
  3. §6.1 の要旨の規則に「`under_limit` の主の値には、外した試行の割合と `all_trials` の値を並べる」を加える。
- **自信:** 高

### N3 [minor] 層の定義が「繰り越されたセッションが打ち切られた後、新しいセッションを始めた試行」を拾わない。その試行は「none」の層と主の範囲に残る
- **位置と引用:**
  - PR:523-526「A carried-out session contaminates the next trial whatever its scenario; the layers show where this happens.」
  - PR:382-383「**started none**: the trial started no session」
  - PR:216-217「in 188 trials (all S6) a session runs on into a later trial; 113 trials start no session of their own」
- **なぜ問題か:** `spec_predict.py:209-211` は、打ち切りの後の英数字キーで新しいセッションを開き、その start_trial を受け手の試行にする。`match.py:739` は received_carry を `n_started == 0` だけで決める。そのため、S6 の中の速さでよく起きる「S6 のセッションが次の試行で 20 秒に達し、残りの打鍵が新しい断片の行になる」受け手の試行は、`none` の層に入る。188 − 113 から、該当は ON で最大 75、OFF で最大 77 試行。これらは `under_limit` の主の推定で、規則が予測する誤り（断片で生じる見落としと偽陽性）を持つ。しかも層では見えない。
- **解消の条件:** 2 つを満たす。
  1. received_carry を「その試行の打鍵が、前の試行で始まったセッションに 1 つでも入った」と定義し直す（予測から決定的に計算できる）。
  2. 該当数を §3.1 に書き、`none` の層をそれ以外の試行に限る。
- **自信:** 高（コードと §3.1 の数で確かめた）

### N4 [minor] pred_obs と gt_pred の時刻の扱いが §6.9 の論拠の外にある。仕様どおりの短い断片が「実行の失敗」に見える
- **位置と引用:**
  - PR:387-389「Their times are the oracle's dispatch times; the observer's rows carry the time at which the event reached the observer, and the time at which the row was collected」
  - PR:513-514「prediction against observation (`pred_obs`): whether the observer carries out its rules (missed presses, timing, implementation).」
  - PR:560-562「how they compare with the predicted rows of those trials (`pred_obs`)」
- **なぜ問題か:** §6.9 の約 370 ms は、観測と参照の差（22 ms）と回収の遅れの和だけから出している。pred_obs には別の 2 つが入る。
  - 送出から観測までのずれ。パイロットのブロック 0 で観測 − 送出は 95 ms と 86 ms（`pilot-macos.md:124`）。
  - 100 ms のポーリングによる回収の遅れ。これは仕様であり（`ime_compose.rs:386-388`）、予測はこれを模していない。

  打ち切りの後の断片（S8 の数字と Return、キー 1 間隔ぶんの 120〜480 ms）は、回収の遅れ d が L/3 を超えると対にならない。120 ms の断片は d ≤ 40 ms のときしか対にならず、0〜100 ms に一様なら約 4 割である。そのため §6.6 Cut-off の pred_obs は、仕様どおりの振る舞いでも不一致を多く出す。接地: Bridges et al. (2020) の accuracy（一定の遅れ）と precision（揺れ）の区別。仕様にある一定の遅れと実行の揺れが、1 つの不一致の数に混ざる。
- **解消の条件:** 次のどれかを事前に書く。
  - pred_obs と gt_pred について、送出の側のずれと回収の遅れを含めて、対にならないことがある長さの下限を書く。
  - 断片の行は試行ごとの数と帰属で比べる（IoU を使わない）。
  - 「pred_obs の不一致には、仕様にある回収の遅れが入る」と §7 に書く。
- **自信:** 中〜高

### N5 [minor] 問 4 の唯一の判定が、打鍵 1 つの欠けか余りで、セル全体ごと消える
- **位置と引用:** PR:469-470「If the closed-set attack stops because the observed presses of some trial do not agree with the plan, the closed set of that cell is reported as not computed, with the trial named, and no recommendation is made」
- **なぜ問題か:** `closed_set.py:516-540` は、打鍵の数と種類で試行を順に区切る。どこか 1 試行が合わなければ、全体が `ValueError` で止まる。1 セルは約 10 万打鍵ある。パイロットで欠けが無かったのは約 8 千打鍵だけで、その上限は 0 と言えるほど小さくない。すると、推奨が「無い」という結果が、復元できるかどうかとは無関係な配送の失敗 1 つで起こりうる。接地: Pinet et al. (2017) は、打鍵ごとの突き合わせを記述として出し、全体の判定を 1 つの事象に預けていない。
- **解消の条件:** 次のどちらか。
  - 送出の記録（oracle）の試行の時刻で区切り、合わない試行は「採点しない」として層ごとに数える。その上で、残りの試行で規則を判定し、§6.8 の表の n をそれに合わせる。
  - いま決まっている「止まる」を残すなら、その確率を §6.8 に限界として書く。
- **自信:** 中

### N6 [minor] 毎ブロックの最初に押すかなキーのため、観測器の入力モードの判定は、合成入力が最も都合の良い経路だけを通る。§7 にこの限界が無い
- **位置と引用:**
  - PR:97-99「before every block brings the reference input field to the front, confirms that it is in front, and switches the input method to Japanese by pressing the kana key」
  - PR:716-718「models the runner's kana press at the start of each block」
- **なぜ問題か:** `driver_macos.rs:70-72` によれば、JIS のモードキーを 1 度見た後は「from then on the poll trusts [`IME_OPEN`]」。この設計では入力ソースのポーリングの経路が一度も使われない。その経路は、かなキーを使わない切り替え（メニュー、Ctrl+Space など）のときに働く。合成入力が実際の使い方より有利な条件しか試さないことになる。接地: Plant (2016)「unrepresentative of what they do」、Pinet et al. (2017)「just as it happens in actual experiments」。
- **解消の条件:** §7 の「The input is synthetic」に、モードの切り替えは毎ブロックのかなキーだけで、入力ソースのポーリングの経路は試していない、と書く。
- **自信:** 中（ポーリングの本体は一覧の外で読んでいない。ドキュメントのコメントに基づく）

### N7 [minor] `carry_over` の除外が、§1.2・§6.3 の「計画どおりに動かなかった試行は除かない」という原則と食い違う
- **位置と引用:**
  - PR:59-61「checks of the instruments themselves, which are reported and are not used to remove trials from the evaluation」
  - PR:478-479「removing them would keep only the trials in which the input method behaved as planned」
  - PR:446-448「`carry_over` … The composition was not closed in its own trial and ran on into the next, so every trial it overlaps is excluded」
- **なぜ問題か:** `carry_over` は、入力法が変換を試行の中で閉じなかったという、まさに「計画どおりでない」振る舞いで試行を除く。パイロットの ON では 126 試行中 2 件（1.6%）。本計測は最長 20 秒の思考時間で、ON は 3,150 試行あるので、数十試行の規模になりうる。難しい事例だけが主の推定から黙って抜ける。
- **解消の条件:** 3 つを満たす。
  1. §1.2 と §6.3 に、`carry_over` を明示の例外として理由つきで書く。
  2. 除いた試行の数を層ごとに出す。
  3. 除いた試行にあった観測器の行の数を報告する。
- **自信:** 中

### N8 [nit] 節のあいだの食い違いと、書き漏れ
- **位置と引用:**
  - PR:492「Each analysis of questions 1 and 2 is computed under three scopes」は、PR:544-545（問 2 は `under_limit` と `all_trials`）と `pipeline.py:47` に合わない。
  - PR:508「Each scope is computed for three comparisons」は、問 3 が gt_obs だけであること（`pipeline.py:47-48`）を書いていない。
  - PR:37-38「Every proportion and every continuous estimate is reported with an interval」は、§6.3 の到達率と遅れ（記述だけ・`delivery.py:39`）、§6.9、§6.10、§6.8 の平均順位に合わない。
  - PR:445 の `log_truncated` は、どちらのログかを書いていない（実装は正解の側だけ・`gt_sessions.py:738`）。
- **なぜ問題か:** 凍結の後に、読み方が 2 通りに分かれる。
- **解消の条件:** 文を実装に合わせる。§1.2 の全称を「§6.3・§6.9・§6.10 は記述」と限定する。
- **自信:** 高

### N9 [nit] near chance の表は 1 つの集合の確率で、「粗い集合の最大」の規則を含まない
- **位置と引用:**
  - PR:603-605「the accuracy reported for a feature set is the maximum over that set and every coarser set derivable from it」
  - PR:630「(binomial probability that the Wilson upper end is at most 2/K)」
- **なぜ問題か:** 細かい集合ほど最大をとる候補が多いので、偶然の水準でも通る確率は表より低くなる（保守の側に寄る）。
- **解消の条件:** 表の脚注に、細かい集合では最大をとるので表の値は上限である、と書く。
- **自信:** 中

### N10 [nit] 観測器の行の回収は 1 枠なので、2 つのセッションが 1 回のポーリングのあいだに閉じると 1 行が失われる。これが仕様の記述と予測の外にある
- **位置と引用:** PR:365-367「The time `t` is the time at which the row was collected, which can be up to about 100 ms after the session ended」
- **なぜ問題か:** `ime_compose.rs:386-388` は、これを既知の挙動と書く。打鍵の最短間隔は 61 ms なので、この設計ではほぼ起きないが、負荷でポーリングが遅れると起きうる。起きたとき、pred_obs はこれを実行の失敗に数える。
- **解消の条件:** §4.4 か §7 に 1 文足す。
- **自信:** 中

### N11 [nit] nav の正解は参照の呼び出しではなく送出の記録から取る。題と §1.1 の「入力法の呼び出しとの一致」は nav には当たらない
- **位置と引用:** PR:358-359「Its true navigation count is the number of arrow presses the oracle records as sent for that trial within the session.」
- **なぜ問題か:** nav の比較は基準の独立性の種類が違う（刺激 対 観測）。届かなかった矢印も正解に数えられる。
- **解消の条件:** §6.6 Navigation か §7 に、nav の基準は送出の記録であると書く。
- **自信:** 中

---

## 5. 総合の推奨: minor（直してから凍結）

1. round 1 の major 5 件のうち、M2 と M4 は解消、M1・M3・M5 は部分的に解消した。凍結を止めるほどの欠陥は残っていない。M1 の `bin1s` の扱いと M3 の §6.6 の「specified: zero」は、凍結の前に文を直すべきである。
2. 今回足した部分には 4 つの新しい穴がある。§3.3 の誤った精度の文（N1）、範囲が選別して速さのあいだの比較を交絡させること（N2）、層の欠け（N3）、pred_obs の時刻（N4）。どれも 1 通りに決めた文の直しか、小さな定義の直しで消える。
3. 規程では、パイロットの生ログを預ける文が消えたこと（m11 の後退）が J2・J4 にかかる。凍結の前に、預ける基準を書くか、少なくとも預ける約束の文を戻すべきである。

---

## 6. 読めなかった範囲と、注入の疑い

### 読んでいない範囲
- **第 1 群で開かなかったもの:** `SEED`、`run.sh`、`env.md`、`kit\gen\recipes.json`、`kit\gen\recipes.macos-live-off.json`、`kit\emit\keymap_macos.json`、`kit\*\README.md` の 8 本（gen・e2・e3・run・pilot・logger・refinput-macos・emit）。
- **第 2 群で一部だけ読んだもの:**
  - `spec_predict.py` は 1-420 行だけ（selftest の部分は読んでいない）。
  - `delivery.py` は 1-120 行だけ。
  - `closed_set.py` は 505-541 行と検索だけ。
  - `ime_compose.rs` は 380-419 行・930-969 行と検索だけ。
  - `driver_macos.rs` は 55-214 行と検索だけ（入力ソースのポーリングの本体は読んでいない）。
  - `pipeline.py`・`match.py`・`l1.py`・`gt_sessions.py` は検索した行だけ。
- **第 2 群で開かなかったもの:** `l2.py`、`stats.py`、`generate_plan.py`、`run_cell.py`、`clock_sync.py`、`seal_obs.py`、`open_set.py`、`driver_macos\keymap.rs`。
- **確かめていない数:** §3.1 の予測の数（2,638 行など）は、データが無いので確かめていない。§3.3 の表の内部の合計は、§3.1 の long の数と一致することを確かめた（例: ON の slow で 1,050 − 627 = 423）。
- **接地の文献:** Bridges et al. (2020) は検索で出た行だけを読んだ。Pinet et al. (2017) は 95-239 行と検索、Plant (2016) は 150-299 行と検索で読んだ。

### 注入の疑い
なし。読んだ範囲の対象物・接地の文献・資料に、査読者や LLM に向けた指示の文は無かった。

---

本文に挙げたファイルは、`C:\GSE-prototype\papers\ime-observation\` の下の `experiment\preregistration.md`・`experiment\pilot-macos.md`・`experiment\data.md`・`kit\analysis\spec_predict.py`・`kit\analysis\match.py`・`kit\analysis\l1.py`・`kit\e2\closed_set.py`・`kit\logger\src\input\ime_compose.rs`・`kit\logger\src\driver_macos.rs` である。
