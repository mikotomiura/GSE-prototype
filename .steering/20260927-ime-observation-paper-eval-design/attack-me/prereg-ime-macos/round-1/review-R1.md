# BRM 査読者役（打鍵・反応時刻の測定具を外部基準で検証してきた伝統の立場／下位人格: 懐疑家）: 事前登録の下書き（macOS の 2 セル）の査読・round 1

対象: `C:\GSE-prototype\papers\ime-observation\experiment\preregistration.md`（d0cf4343）
**推奨: major（直して再査読）。** fatal は無い。major が 5 件ある。

---

## 1. 接地: この立場が論文に求める基準（逐語）

- **C1 外部の時計で自分の環境を検証し、区間を書く**（Plant, 2016, l.290–294）
  "In closing I would propose that researchers self-validate their own timing accuracy using external chronometry (e.g., … using a Black Box ToolKit or oscilloscope) and state confidence intervals on publication."
- **C2 理想化した入力と単純な台本での検証は、現場を代表しない**（Plant, 2016, l.165–169, 297–298）
  - "benchmarking various experiment generators using idealized equipment and simplified scripts is counterproductive, lulls researchers into a false sense of security, and is unrepresentative of what they do and may achieve in the field."
  - "Generalization across apparently similar hardware types or categories of study is folly."
- **C3 ソフト自身は、ほかの層が入れた誤差を知りえない（基準は測定と独立であるべき）**（Plant, 2016, l.190–194）
  "the software or script being run can know nothing of the errors introduced by the hardware, rendering engine, or plug-in. It, just like the experimenter, will blindly act on and report the timings given without question."
- **C4 合成入力は実際の打鍵列を模すべきで、OS の中間層の影響は未知として扱う**（Pinet et al., 2017）
  - l.121–127: "A limitation of this approach is that their manipulation involved fixed intervals and a single button. A crucial and original feature of the present study is the use of three distinct keys from the keyboard, and the generation of variable delays between keys, just as it happens in actual experiments involving sequence production."
  - l.114–115: "The impact of this intermediate layer of software on keyboard chronometry is not known."
- **C5 一定の誤差（accuracy）とばらつき（precision）を分けて報告する**（Bridges et al., 2020, l.30–35）
  - "Precision refers to the trial-to-trial variability of the measures: the jitter of the timing measurement or its "variable error". Accuracy refers to the "constant error" of a measurement"
  - "A variable error (poor precision) cannot be corrected afterwards"
- **C6 1 台での値はおおむね最良の場合であり、研究ごとの検証の代わりにならない**（Bridges et al., 2020, l.286, 379, 389）
  - "the variance we measured in that single machine is likely to be small compared with the variance between machines."
  - "It is very important to note that the timings measured here represent something approaching a best-case scenario."
  - "Papers such as this one, which report "best case" timing performance, should not be used in lieu of study-specific validation and testing."

---

## 2. 評価表

| 観点 | 点 | 所見 |
|---|---|---|
| a 主張と根拠の一致 | 3 | 目的（l.28–29）は「input method's own state」との一致と書く。しかし基準は、1 つの参照アプリが受けた NSTextInputClient の呼び出しを研究者の規則で組み立てた区間である。その参照アプリは左の文脈を持たず、入力は合成である。問 4 の推奨は、打鍵の時間に情報が無い合成データから導かれ、人の記録へ持ち出せない（M1）。 |
| b 方法の穴 | 2 | 妥当性への脅威の節が無い。次の 3 つが手当ても限界の明記も無い。(i) 20 秒以上の区間が recall の分母に入る（M3）。(ii) 観測器の仕様から決まる誤り（S6 が閉じない、句読点で閉じる、など）が他の層へ漏れる（M4）。(iii) 問 4 の時間特徴が設計上ゼロ情報である（M1）。 |
| c 持ち帰れるもの | 3 | 層別の一致と、ハッシュで固めた道具一式は有用。ただし BRM の読者が最初に求める打鍵 1 つずつの時刻の忠実度（遅れ・ばらつき・到達率）が問いに無い（m8）。問 4 の推奨は誤用されやすい。 |
| d 簡潔さと構成 | 4 | 節の立て方は明快。ただし次の点が粗い。pilot-macos.md と 1 試行の時間・所要時間が食い違う（m3）。同じ区間を与える 2 つの定義で全解析を繰り返す（n2）。節の参照が 1 か所誤っている（n1）。 |
| e 規程への適合 | 4 | J6・J7（n の基準と精度）、J8（思考時間は探索扱い）、J9（除外を事前に固定）は満たす。J4（生データ）は、パイロットの生ログの寄託が「検査の後」の条件つきで未確約（m11）。 |
| f 先行研究の位置づけ | 2 | 速度の根拠（Dhakal et al.）のほかに、時刻の検証の伝統（外部の時計・量子化）と、書字の打鍵記録の先行の道具への言及が無い。基準をソフトの層に置く選択を、外部の時計を使う伝統に対して位置づけていない（m12）。 |
| g 固定の十分さ | 3 | ハッシュ・タグ・除外・ブートストラップの単位はよく固まっている。穴は次のとおり。20 秒以上の区間の扱い（M3）。K=1000 で判定規則が機能しない、セルごとの判定が食い違ったときの扱い（M2）。実行順と学習の持ち越し（m4）。予期しない焦点の喪失（m5）。OS の版の扱い（m10）。 |

---

## 3. 指摘の一覧（重い順）

### M1 [major] 問 4（文字の復元）の推奨は、打鍵間隔が打ったキーと無関係な合成データから決めるので、人の記録の公開の粒度には持ち出せない
- **位置と引用**
  - preregistration.md §3.3: 「**Key intervals**: log-normal, with medians of 480 ms (slow), 240 ms (middle) and 120 ms (fast) and a log-scale standard deviation of 0.3.」「The spread is a design choice that makes intervals vary; it is not estimated from data.」
  - §6.7: 「The recommended granularity for publishing logs is, at each K, the most detailed feature sets that are near chance」
  - kit\e2\README.md l.57–59: 「An interval shorter than `PAUSE_MS` (600 ms) is treated as typing jitter and ignored, because the law of inter-key intervals does not depend on the phrase.」
  - 同 l.125–126: 「the timing feature of this attack compares only long pauses, whose length is drawn independently of the phrase」
- **なぜ問題か**
  - 計画の打鍵間隔は、キーの組（2 字の連なり）と独立に同じ分布から引かれる。人の打鍵では、間隔そのものが 2 字の連なりの正体を漏らす。
  - したがって `all`・`no_runs`・`bin1s` など時間を含む特徴集合の正答率は、この設計では時間の通路の漏れを原理的に測れない。
  - それなのに §6.7 は「公開する記録の粒度」を推奨し、事前登録で唯一の判定にしている。偶然近くと出ても、それは時間の情報を作らなかったからであり、人の記録で時刻を公開してよい根拠にはならない。
  - 接地: Plant 2016 「benchmarking … using idealized equipment and simplified scripts is counterproductive, lulls researchers into a false sense of security」。Pinet 2017 「the generation of variable delays between keys, just as it happens in actual experiments」。
- **解消の条件**（どれか 1 つ）
  - (a) 推奨の範囲を「打鍵間隔がキーと独立な合成入力の下での、件数と並びの構造の漏れ」に限ると明記する。そのうえで、時間を含む特徴集合を推奨の対象から外す（または「この設計では判定できない」と事前に書く）。
  - (b) 推奨という判定をやめ、推定だけにする。
  - (c) 2 字の連なりに依存する間隔の生成（出典つき）を事前登録に加える。
- **自信**: 高

### M2 [major] K=1000 では「偶然近く」の規則が、真に偶然の攻撃者をおよそ 8 割の確率で「偶然近くでない」と判定する
- **位置と引用**
  - §6.7: 「The accuracy of a feature set is **near chance** at a given K when the upper end of its 95% Wilson interval is at most 2/K.」
  - 同: 「Run on the observation logs of each cell separately」
- **なぜ問題か**（計算は私の手元の概算で、要確認）
  - live on のセルの数え上げ対象は 3,150 − S12 の 225 = 2,925 試行。K=1000 で真に偶然（p=0.001）なら、正解数はおよそ Poisson(2.9) に従う。
  - Wilson の上端が 0.002 以下になるのは x≤1 のときだけ（x=1 で約 0.00193、x=2 で約 0.00249）。P(x≤1) は約 0.21。
  - つまり時間を消した `counts_only` ですら、真に偶然でも約 79% の確率で「偶然近くでない」になる。そのうえ報告値は粗い側の最大値を取るので、上へ偏る（closed_set.py l.749–751 自身がそう書く）。
  - したがって K=1000 の推奨は「推奨なし」になりやすい。しかも理由は漏れではなく n である。live off のセルは n≈2,700 でさらに厳しい。
  - 2 つのセルの判定が食い違ったときの扱いも書かれていない。
- **解消の条件**: 判定規則の特性（真に偶然のときに偶然近くと判定する確率）を K ごと・セルごとの n で計算して記載し、それが十分高くなる余裕に改める（例: K ごとに n から導いた閾値、または絶対の余裕）。セルの判定が食い違ったときは保守側（どちらでも偶然近くの集合の共通部分）を採ると事前に書く。
- **自信**: 高（算術）。中（実際の n は除外で減る）。

### M3 [major] 20 秒以上の区間が検出（問 1）と文章ごとの集計（問 3）の分母に入り、打ち切りの検査は観測器と違う時計の起点で 20 秒を判定する
- **位置と引用**
  - §1.1: 「A session that reaches 20 seconds is cut off and produces no row.」
  - §4.3: 「A session is reported as lasting 20 seconds or more when its duration reaches 20,000 ms.」
  - §6.4: 「Reported per stratum: recall (pairs over sessions), precision (pairs over rows), split rate, merge rate, miss rate and false-positive rate」
  - §6.5: 「the specified behaviour is zero for both.」
- **実装で確かめたこと**
  - match.py には打ち切りの限度による除外が無い。
  - l1.py の truncation_check は、長い区間を「the sessions that entered the matching (pairs, split, merge, miss)」の中で数える。つまり長い区間は照合に入り、見逃し（miss）として recall を下げる。
  - l2.py にも限度の扱いが無い。
- **なぜ問題か**
  - (1) 仕様どおりの「行を出さない」が、検出の失敗と同じ箱で数えられる。S13 はすべて 21 秒を超えるので、recall は設計上 0 になる。
  - 遅い層では、読みが 6〜30 字（中央値 16）、打鍵間隔の中央値が 480 ms、思考時間が 0.2〜20 s の対数一様分布なので、思考を含む場面のかなりの割合が 20 秒を超える（概算で 2〜3 割）。長い読みなら S3 でも超える。recall はこの層で構造的に上限を持つ。
  - (2) 観測器の dwell は「最初の英数字キー」から「最初の終端キー」までである（ime_compose.rs l.120「最初の英数字キー 〜 終端キー までの時間」）。基準の区間は最初の set_marked から最後の確定まで。live on では 2 回目の Return の後である。20 秒の線が両側で違う所に引かれるので、境界近くでは定義のずれから「仕様違反」や見逃しが出る。
  - (3) 問 3 の文章ごとの集計では、基準の側だけが長い区間を数える。打ち切りの効果と観測の誤差が分けられない。
- **解消の条件**
  - 分母の扱いを事前に 1 つに決める。推奨: 送信の記録（oracle）から観測器の仕様上の期間（最初の英字キーの送信から最初の終端キーの送信まで）を決定的に計算する。それが 20 秒以上の試行は recall・miss・precision の主たる分母から外し、別に報告する。境界の帯（例: 19〜21 秒）も別に数える。
  - 打ち切りの検査（§6.5）も、この oracle 由来の期間で定義する。
  - 問 3 は「長い区間を含む」「含まない」の 2 通りで偏りを報告すると事前に書く。
- **自信**: 高

### M4 [major] 観測器の推論規則から決まる誤りと、実装・計時の誤りを分ける解析が無い。S6 の区間は次の試行へ漏れ、その試行の層を汚す
- **位置と引用**
  - §1.1: 「backspace and arrow keys keep the session open.」
  - §2.3 の表: 「| S6 | Type the reading, Backspace once per kana typed (delete everything) |」
  - §6.2: 「Observation rows are assigned to the trial they overlap most and are excluded with that trial.」
  - ime_compose.rs l.297: 「// Backspace — 候補表示から抜けてインライン編集へ戻る。⚠️ セッションは続く。」
  - 同 l.316: 「// その他 (Tab / 記号 / ファンクションキー) — IME の自動確定にあたる。」
- **なぜ問題か**
  - S6 では入力法が中身を全部消して取り消しても、観測器には閉じる手がかりが無い。区間は 1 秒後の次の試行の打鍵へそのまま続く（区切りの印の矢印も nav に入る）。
  - その結果、次の試行の場面（無作為な順序なので全場面）に、伸びた dwell、誤った abandon・nav、併合、見逃しが入る。
  - 基準の側の持ち越しは carry_over として除外するのに、観測の側の持ち越しは帰属の規則も診断も無い。
  - 同じ仕組みで、次も規則から予測できる誤りである。
    - 読みの中の「、」「。」「ー」（comma・period・minus は「その他」）で区間が途中で閉じる。
    - S10 の Tab で、思考の前に閉じる。
    - S12 で「ほ・ね・る」のキーで閉じる。
  - 層別の値は、刺激の文字の構成（コーパス）と場面の前後関係の混合になり、何の精度かが読めない。
  - 接地: Pinet 2017 「The impact of this intermediate layer of software on keyboard chronometry is not known.」
- **解消の条件**
  - 「仕様が予測する行」を事前登録の参照として加える。oracle の送信キー列に観測器の状態機械（`step` と同じ規則）を当てて、予測される行を作る。
  - そのうえで (i) 基準 対 仕様の予測（推論規則の妥当性）と、(ii) 仕様の予測 対 実際の観測（取りこぼし・計時・実装の忠実度）の 2 段で報告すると書く。
  - 観測の行が 2 試行にまたがる場合の帰属（前の試行に帰す、または両方を別の箱で数える）を定める。
  - 読みに「終端に当たるキー」を含む試行かどうかの診断の分割を事前に書く。
- **自信**: 中（ime_compose.rs の規則から推論した。macOS の駆動層 hook_macos は読める範囲の外で、読んでいない）

### M5 [major] 基準の妥当性と、合成入力の代表性の限界を書く節が無い。基準の組み立て方への感度の解析も無い
- **位置と引用**
  - §1.1: 「This study estimates how closely those rows agree with the input method's own state, recorded at the same time by a reference input field, under scripted input whose intent is known.」
  - §2.2: 「It empties its text after every commit, so that no trial sees the text of an earlier one.」
  - §3.3: 「The generator never overlaps two presses」
  - §4.3: 「The outcome of a session is the reason it finally closed; a session whose head was committed this way and whose rest was cancelled is a cancellation.」
  - §5: 「On the reference side of a macOS cell they hold the same sessions.」
- **なぜ問題か**: 基準は「入力法の状態」そのものではない。次の選択の積である。
  - (a) 1 つの最小の参照アプリ（左の文脈なし。実アプリでは、ライブ変換の自動確定も予測候補も文脈に依存しうる）
  - (b) 自動確定を 50 ms の窓で畳むかどうか、最終の理由を結果とするか、という研究者の構成の規則（パイロットでは、畳まない規則なら 126 試行中 40 試行が分割される）
  - (c) 合成入力。CGEventPost で送り、修飾のフラグを上書きする（kit\emit\README.md l.58–61）。キーの重なり（ロールオーバー）が無く、押下時間は 60 ms で固定、物理キーボードの経路を通らない。
  - (d) マウスによる候補の確定（S9）は評価しない。観測器はこれを次の変換と合算する（ime_compose.rs l.54–59）。
  - (e) 1 台・1 版の macOS と入力法。
  - 「macos_def と all の 2 定義で繰り返す」は、macOS では同じ区間なので感度の解析にならない。
  - 基準と観測の時刻はどちらも同じ機械のソフトの時計である。外部の時計ではない。
  - 接地: Plant 2016 「the software or script being run can know nothing of the errors introduced by the hardware」「Generalization across apparently similar hardware types or categories of study is folly.」。Bridges 2020 「something approaching a best-case scenario」。
- **解消の条件**
  - 妥当性への脅威と限界の節を足し、(a)〜(e) をそれぞれ「手当て」か「限界（主張の範囲をこう限る）」として書く。
  - 目的の文を「参照の入力欄が受けた入力法の呼び出しから、§4.3 の規則で組み立てた区間との一致」に改める。
  - 畳まない規則（`gt_rules.example.json` の mac_nstic）による問 1・2 の再解析を、事前に指定した感度の解析として加える。
  - 物理キーの経路の遅れと量子化には一切触れない、と明記する。
- **自信**: 中〜高

### m1 [minor] 割合には Wilson 区間（独立を仮定）を使い、連続量には「ブロック内の試行は状態を共有する」としてブロック単位のブートストラップを使う。同じ根拠に対して扱いが割れている
- **位置と引用**: §6.1 「Proportions carry 95% Wilson intervals (Wilson, 1927). Continuous measures carry 95% percentile bootstrap intervals … that resample whole blocks …, because trials in one block share the state of the input method.」
- **なぜ問題か**
  - 依存の根拠は割合にもそのまま当てはまる。
  - 学習を戻さないので、ブロックを越えた依存もある。M4 の漏れは隣り合う試行の依存を作る。
  - 1 層の 75 試行は約 42 ブロックに散るので、層内の設計効果は小さいかもしれない。ただし主たる指標（recall・precision）だけ独立を仮定する理由を書いていない。
- **解消の条件**: 割合にもブロック単位のブートストラップの区間を併記する（または設計効果を報告する）と書く。あるいは Wilson を使う理由を書く。
- **自信**: 中

### m2 [minor] 観測の行の時刻 `t` は回収された時刻であり、最大 100 ms の遅れが入る。「ずれは最大 22 ms」という論拠はこれを含まない
- **位置と引用**
  - §4.4: 「A session row's interval is `[t - dwell_ms, t]` on the wall clock. No offset is added at either end」
  - §6.8: 「(in the pilot the largest difference between the observation and the reference was 22 ms)」
  - match.py l.15–19: 「The ime_shadow row's t is the time the entry was drained, not necessarily the moment the composition ended … (for a lag uniformly distributed over 0-100 ms, -50)」
- **なぜ問題か**
  - 22 ms は区切りの印のキー行で測った値で、区間の行の回収の遅れ（0〜100 ms の変動する誤差）を含まない。
  - 照合で効くのは両者の和である。重なりの判定（ずれ ≤ 区間の長さの 1/3）が効く短い区間の層では、この遅れが見逃しと誤検出に化ける。
  - パイロットのブロック 0 に約 100 ms のずれがあった理由も書かれていない（pilot-macos.md l.124–127）。
  - 接地: Bridges 2020 「A variable error (poor precision) cannot be corrected afterwards」
- **解消の条件**
  - §6.8 に回収の遅れを書く。補正しない理由を、回収の遅れと時計のずれの和で述べ直す。
  - 補正あり（例: −50 ms）の照合を感度の解析として事前に指定する。
  - ブロックのずれが閾値（例: 50 ms）を超えたときの扱いを決める。
- **自信**: 高（コードの docstring で確認した）

### m3 [minor] 所要時間と 1 試行の時間が pilot-macos.md と食い違う
- **位置と引用**
  - preregistration.md §3.3: 「The generator estimates 11.9 and 11.2 hours per run (13.6 and 13.8 seconds per trial …) … close to the generator's estimate for the pilot's key intervals (11.2 and 11.4 seconds).」
  - pilot-macos.md l.148–149: 「For the measurement settings (below), the generator's estimate (`generate_plan.py --estimate`) is 11.2 s per trial with live conversion on and 11.4 s with it off.」
  - 同 l.153–154: 「One macOS cell then takes about 9.8 hours with live conversion on and 9.3 hours with it off.」
- **なぜ問題か**: 11.2 s が「本番の設定」の推定なのか「パイロットの間隔」の推定なのか、2 文書で逆である。n の根拠（「一晩に収まる」）は所要時間に依存する。
- **解消の条件**: 一次の値（`--estimate` の出力）で片方へ揃え、どちらが古かったかを記録する。
- **自信**: 高

### m4 [minor] 学習を戻さないのに、セルと E3 の実行順を固定していない。E3 の working の夜は本番と同じ計画を流す
- **位置と引用**
  - §3.2: 「The input method's learning is not reset: no method of resetting it was found, and the plans request no reset.」
  - §6.9: 「`working` (the observer runs while the runner plays the plan of the cell with live conversion on)」
  - §3.4: 「the cell is run again from the start with the same plan, in a new run directory, up to three attempts.」
- **なぜ問題か**
  - 予測候補（S10）・候補の順（S2・S8）・ライブ変換の結果は学習に依存しうる。
  - live on・live off・E3 の順や、中止の後の再実行（中止までに同じ語句を学習済み）によって、基準の側の入力法の挙動が変わる。
- **解消の条件**
  - 順序を固定して書く（例: live on → live off → E3 idle → E3 working）。
  - E3 は本番の後に回すか、別の seed の計画を使う。
  - 中止の後の再実行では、学習の持ち越しを限界として報告すると書く。
- **自信**: 中

### m5 [minor] 前面の確認はブロックの前だけである。ブロックの途中で焦点を失ったときの除外の規則が無い
- **位置と引用**
  - §2.2: 「A run is aborted if the front-window check fails or if either program stops.」
  - §6.2: 「Not excluded: trials in which the input method did not do what the plan intended」
- **なぜ問題か**
  - 通知などでブロックの途中に焦点が移ると、キーは別のアプリへ行く。基準の区間は無いのに、全体を見る観測器は行を出す。これが観測器の誤検出として数えられる。
  - この場合は基準そのものの欠落である。参照の入力欄は focus_out を記録する（refinput-macos\README.md l.94）ので、検出できる。
- **解消の条件**: S15 以外での予定外の focus_out を含む試行を除外の理由（例: `focus_lost`）として事前に足し、数を報告すると書く。
- **自信**: 中

### m6 [minor] live on のセルでは S3 と S11 が同じ手順であり、S3 の名前（変換せずに確定）が成り立たない
- **位置と引用**
  - §2.3 の表: 「| S3 | Type the reading, Return (commit without conversion) |」「| S11 | Type the reading, Return (live conversion converts without Space) |」
  - recipes.json: macOS の S3 と S11 は、どちらも steps が `[{"type_reading": true}, {"key": "enter"}]` で、intent も同じ。
  - §6.1: 「Estimates pooled over scenarios weight them equally」
- **なぜ問題か**: 同じ手順が 2 層になり、場面を等しく重みづけた集計で 2 倍の重みになる。2 つのセルの比較（探索）でも S3 の意味が変わる。
- **解消の条件**: live on では S3 と S11 が同じ手順だと明記する。集計の重みをどう扱うか（1 つにまとめる、または注記する）を事前に書く。
- **自信**: 高

### m7 [minor] 解釈の基準が事前に無い。notes.md は「有益とみなす精度」が事前登録に書いてあると言うが、無い
- **位置と引用**
  - preregistration.md §1.2: 「The study estimates; it tests no hypothesis. Every estimate is reported with an interval, and none is turned into a pass or fail decision」
  - notes.md l.5–6: 「the precision that counts as informative are stated in `preregistration.md`.」
- **なぜ問題か**
  - 推定に徹するのは正当である（J7）。しかし本文で「よく一致した」と書く基準が後付けになる危険がある。
  - 接地: Plant 2016 「Determining the levels of accuracy needed in a given experiment, or research area, is solely the responsibility of the researcher」
- **解消の条件**: 次のどちらかにする。そのうえで notes.md の文を事実に合わせる。
  - (a) 参照の値（例: 書字研究で意味のある dwell の差）を出典つきで事前に置く。
  - (b) 要旨と結論では層ごとの区間の範囲だけを書き、適否の形容をしないと事前に約束する。
- **自信**: 中

### m8 [minor] 打鍵 1 つずつの忠実度（到達率、送信に対する遅れとばらつき、間隔の誤差、量子化）が、本番の問いに無い
- **位置と引用**
  - §3.1（パイロットだけ）: 「the fraction of sent key presses that produced a key row in the observation」
  - clock_sync.py l.23–24: 「Latency (the time from sending to recording) and clock offset cannot be separated」
- **なぜ問題か**
  - 観測器は打鍵ごとの時刻を公開の記録に書き、問 4 もそれを使う。書字の研究者は、そこから打鍵間隔を計算するはずである。
  - BRM のこの伝統では、打鍵の間隔の一定の誤差とばらつきの報告が最初に求められる。データ（oracle と key 行）はすでに揃っている。
  - 接地: Pinet 2017 「Our measure of primary interest, IKIs, was unbiased, showing a mean error of 0 ms.」および量子化の解析。Bridges 2020（C5）。
- **解消の条件**
  - 本番のすべての実行で次を報告すると事前に書く。到達率（両方向）。key 行 − 送信の時刻の分布（ブロックの中央値を引いた残差のばらつき）。打鍵間隔の誤差の平均・SD。時刻の量子化の検査。
  - 送信は外部の時計ではなく、物理キーに対しては主張しないと明記する。
- **自信**: 中

### m9 [minor] 送信側（executor）の計画の再現度を報告する計画が無い
- **位置と引用**: kit\emit\README.md l.56–57 「the steps after one are sent later than the plan says, and consecutive steps may follow each other back to back until the schedule is caught up.」
- **なぜ問題か**
  - S15 の焦点の切り替えの後に、Return が間隔ゼロで続きうる。速度の水準は計画の値で定義され、実際の間隔は検証されない。
  - 12 時間の実行中に送信の時刻が遅れたかを示す指標も無い。
- **解消の条件**: 速度ごとの実際の打鍵間隔（oracle 由来）の分布と、計画からの遅れが閾値を超えた試行の数を報告すると書く。必要なら診断の除外も書く。
- **自信**: 中

### m10 [minor] OS の版は「27.0 または env.md の値」で、版が変わったときの扱いが無い。時計の跳びの閾値 1,000 ms の根拠も無い
- **位置と引用**
  - §3.2: 「(Apple Silicon, macOS 27.0 or the version recorded in `experiment/env.md`, JIS keyboard, Romaji input)」
  - §6.2: 「disagree by more than 1,000 ms」
- **なぜ問題か**
  - 基準の規則（50 ms の窓、Return を 2 回）は 27.0 の入力法で較正した。版が違えば規則の前提が崩れうる。
  - 1,000 ms 未満の時計の段差は検出されず、dwell の誤差に直接入る。
- **解消の条件**
  - 版が違えば、基準の側だけのパイロット（seal したまま）をやり直すか、逸脱として記録すると書く。
  - 閾値の根拠を書くか、小さくする。基準の側の長さは単調な時計で計算する、と書く手もある。
- **自信**: 中

### m11 [minor] パイロットの生ログの寄託が「検査の後」の条件つきである
- **位置と引用**
  - §3.1: 「its raw logs will be deposited with the measurement data after the check that report describes.」
  - pilot-macos.md l.165–166: 「Before they are, the criteria for which runs are deposited, and the tool that checks them, will be written here.」
- **なぜ問題か**: 規則を決めた根拠のデータである。J4（「including all relevant raw data」）と照らすと、寄託しないことになる可能性が残る。
- **解消の条件**: 寄託の基準を凍結の前に書く。寄託できない実行は、数と理由を報告すると約束する。
- **自信**: 中

### m12 [minor] 先行研究の位置づけ
- **位置と引用**: References は 9 件で、すべて統計の手法か速度の出典（§References）。
- **なぜ問題か**: 時刻の検証の伝統（外部の時計、キーボードの量子化）と、書字の打鍵記録の道具に対して、この研究が基準をソフトの層に置く選択を位置づけていない。BRM の読者がまず問う点である。
- **解消の条件**: 事前登録では、基準の選択の理由と、外部の時計を使わない限界を 1 段落で書けば足りる。
- **自信**: 中

### n1 [nit] 節の参照の誤り
- **位置と引用**: §1.2 「which decides which log granularity is recommended (section 6.6)」
- **なぜ問題か**: 推奨を決めるのは §6.7 で、§6.6 は問 3 である。
- **解消の条件**: 6.7 に直す。
- **自信**: 高

### n2 [nit] macOS では同じ区間を与える 2 つの定義で全解析を繰り返す
- **位置と引用**: §5 「Every analysis is repeated under two session definitions … On the reference side of a macOS cell they hold the same sessions.」
- **なぜ問題か**: 結果の表が 2 倍になるだけで、情報が増えない。
- **解消の条件**: macOS では 1 つだけ報告し、もう 1 つは一致の確認に留めると書く。
- **自信**: 中

### n3 [nit] 解析コードの同一性は、タグに頼るだけで機械では照合しない
- **位置と引用**: §5 「The analysis code is fixed by the tag of the freezing commit.」
- **なぜ問題か**: 凍結のハッシュは config・SEED・gt_rules だけを覆う。実行時のコードがタグと同じかは、run.sh の検査に入っていない。
- **解消の条件**: 結果のファイルに解析のコミットと dirty の有無を記録し、タグと照合すると書く。
- **自信**: 低（pipeline.py を全部は読んでいない）

---

## 4. 総合の推奨: **major（直して再査読）**

- 事前登録で唯一の判定（問 4 の公開の粒度）が、時間の情報を作らない合成入力と、K=1000 では偶然でも通らない規則の上に立っている。このまま凍結すると判定が使えない（M1・M2）。
- 主たる指標の分母に、仕様どおりの打ち切りと、観測器の規則から決まる漏れ（S6 など）が混ざる。層ごとの値が「何の精度か」を事前に 1 通りに決められていない（M3・M4）。
- 基準は「入力法の状態」そのものではなく、1 つの参照アプリと構成の規則と合成入力の積である。妥当性への脅威の節と、規則への感度の解析を足せば、凍結してよい水準に届く（M5）。固定の仕組み（ハッシュ・タグ・封印・除外）自体は丁寧で、立て直しは要らない。

---

## 5. 読めなかった範囲と、注入の疑い

### 読んでいない（または一部だけ読んだ）
- 第 2 群のコードは次の箇所だけ開いた。
  - match.py: 冒頭の docstring と limit の grep
  - l1.py: 1〜300 行
  - gt_sessions.py・stats.py・l2.py: grep のみ
  - closed_set.py: 20〜90 行と 740〜760 行
  - run_cell.py: grep のみ
  - clock_sync.py: 冒頭のみ
  - ime_compose.rs: 1〜440 行と、テスト名の grep
- 全く読んでいない: pipeline.py の本体、generate_plan.py、seal_obs.py、open_set.py。
- 第 1 群のうち `kit\pilot\README.md` は読んでいない。
- macOS の駆動層（hook_macos.rs）は一覧の外なので読んでいない。M4 の S6 の挙動は ime_compose.rs の規則からの推論である。
- bridges2020.txt の References は原文で省略されている。
- context-B.md・他の round・`.steering\` のほかのファイルは、指示どおり読んでいない。

### 注入の疑い
なし（接地の 3 本・対象物・読んだ設定とコードの中に、査読者や LLM に向けた指示は見当たらなかった）。

### 関連ファイル（絶対パス）
- C:\GSE-prototype\papers\ime-observation\experiment\preregistration.md
- C:\GSE-prototype\papers\ime-observation\experiment\pilot-macos.md
- C:\GSE-prototype\papers\ime-observation\experiment\notes.md
- C:\GSE-prototype\papers\ime-observation\kit\gen\recipes.json
- C:\GSE-prototype\papers\ime-observation\kit\e2\README.md
- C:\GSE-prototype\papers\ime-observation\kit\analysis\match.py
- C:\GSE-prototype\papers\ime-observation\kit\analysis\l1.py
- C:\GSE-prototype\papers\ime-observation\kit\logger\src\input\ime_compose.rs
- C:\GSE-prototype\papers\ime-observation\kit\emit\README.md
- C:\GSE-prototype\papers\ime-observation\kit\refinput-macos\README.md
