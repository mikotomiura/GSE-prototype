# paper-reviewer 報告（attack-me・stage `prereg`・round 1・立場: BRM の、メタサイエンスと統計の方法論の査読者）

対象物: `C:\GSE-prototype\papers\ime-observation\experiment\preregistration.md`（下書き・未凍結）。原稿がまだ無いことは欠陥として扱っていません。

## 1. 接地（この立場が論文に求める基準・逐語）

- **G1 精度で n を決めるなら、幅の根拠を推論の目標に結びつける**（Lakens 2022, lakens2022.txt:693-697）
  "The only aspect a researcher needs to justify for a sample size justification based on accuracy is the desired width of the confidence interval with respect to their inferential goal, and their assumption about the population standard deviation of the measure."
- **G2 資源の制約で n を決めるなら、その n で情報が得られるかを評価する**（Lakens 2022, :316-318、表 :436-437 の右列）
  "The challenge is to evaluate whether collecting N observations is worthwhile."
  "Report and interpret the width of the confidence interval. What will an estimate with this much uncertainty be useful for?"
- **G3 二つの値を見分けることが目標なら、それは検定である**（Lakens 2022, :747-752）
  "If the goal is indeed to get an effect size estimate that is precise enough so that two effects can be differentiated with high probability, the inferential goal is actually a hypothesis test, which requires designing a study with sufficient power to reject effects"
- **G4 除外は網羅的に書き、標本の計画は「何度も回して一番良い回を出す」余地を塞ぐ**（Wicherts et al. 2016, wicherts2016.txt:465-469, :509-512）
  "an ideal preregistration specifically and precisely describes which types of participants will be excluded from the analyses, and also explicates that the stated rules of exclusion will be the only ones that will be used to discard participants (it should be exhaustive)."
  "The sampling plan should also preclude the researcher to conduct a particular study multiple times, and only present the "best" study"
  表 1（:216, :228-230）: "A1 Choosing between different options of dealing with incomplete or missing data on ad hoc grounds" / "A15 Choosing inference criteria (e.g., Bayes factors, alpha level, sidedness of the test, corrections for multiple testing)"
- **G5 指標の測り方まで固定する**（Wicherts 2016, :429-435）
  "even specifying the measure (say, the Rosenberg Self-Esteem Scale) that is to be used as primary outcome is not specific and precise enough to avoid p-hacking during analyses, because often the scores on such measures can be computed in different ad hoc ways."
- **G6 ICC の型・設計・解釈**（Koo & Li 2016, koo2016.txt:52, :427, :543, :483）
  "The best practice of reporting ICC should include software information, "model," "type," and "definition" selections."
  "We should use the 2-way mixed-effects model if the selected raters are the only raters of interest."
  "the 95% confident interval of the ICC estimate (not the ICC estimate itself) should be used as the basis to evaluate the level of reliability"
  "researchers should try to obtain at least 30 heterogeneous samples"
  （逐語の注: 原文の合字 "ﬁ" は "fi" に直して写しました）

## 2. 評価表

| 項目 | 点 | 所見 |
|---|---|---|
| a 主張と根拠の一致 | 3 | 「推定だけで検定はしない」という枠組みは全体で守られている（L34-36）。ただし Q3 は "do four aggregates … agree"（L45-47）と可否を問う形なのに、判定の基準が無い。さらに Q1 の「検出」は、仕様どおりの 20 秒の打ち切りと混ざってしまう（指摘 M1）。 |
| b 方法の穴 | 2 | 遅い速度（480 ms）はパイロットで試していない。この速度では、20 秒を超えるセッションが多く出ると見込まれる。それなのに、recall の分母と per-text の比較の扱いが決まっていない（M1）。E2 の「near chance」の規則は K によって効き方がまったく違い、K=1000 では偶然の水準の攻撃でもほとんど通らない（M2）。 |
| c 持ち帰れるもの | 4 | 層ごとの一致の推定、公開してよい粒度の推奨、手順と道具の一式は、BRM の読者がそのまま使える（J1）。M1 が直らないと、遅い層の数値は解釈できない。 |
| d 簡潔さと構成 | 4 | 5,434 語で、節の立て方は OSF の型に近く読みやすい。§6.4 と §6.7 は 1 段落が密で、規則を数式か箇条に分けるとよい。 |
| e 規程への適合 | 3 | J6 は形の上では満たしている（"chosen so that each run fits in one night"）。J7 は 1 例を示しただけ。J5 では kappa と Bland-Altman の LoA に区間が無い。J8 は満たす（思考時間との依存を探索と明記している）。J9 は除外を事前に書いているが、網羅性の宣言が無い。J2/J4: パイロットの生ログを預けるときの基準がまだ書かれていない（pilot-macos.md:165-176）。 |
| f 先行研究の位置づけ | 3 | 引いているのは方法の文献 9 件だけ。日本語の打鍵記録が IME を考慮する必要がある、という動機（L14-15）に引用が 1 件も無い。事前登録なので致命的ではないが、ICC の型の選び方（Koo）の根拠は弱い。 |
| g 固定の十分さ | 3 | コマンド・シード・GT の規則・解析の設定は 1 通りに固定されていて良い。一方で、20 秒以上のセッションの分母、E2 の判定を 2 セルでどう合わせるか、pooled の重み（本文とコードが食い違う）、計画ファイルのハッシュ、各種の不測時の分岐が決まっていない。凍結のハッシュがカバーするのは 3 ファイルだけ。 |

## 3. 指摘の一覧

- [severity: major] M1. 仕様どおりの 20 秒の打ち切りが、検出（Q1）と per-text の一致（Q3）に混ざる。遅い速度ではそれが大量に起きると見込まれるのに、どう扱うかが決まっていない
  - 位置と引用:
    - preregistration.md:25-26「A session that reaches 20 seconds is cut off and produces no row.」
    - :339「recall (pairs over sessions)」
    - :207「medians of 480 ms (slow), 240 ms (middle) and 120 ms (fast)」
    - :161-162 パイロットは「key-interval medians of 300, 200 and 120 ms」
    - :104-105 think time は「between 0.2 and 20 seconds」
    - :273 per-text の「number of conversions (sessions or rows)」
  - なぜ問題か:
    - コード（match.py:63「recall = pairs / ground truth」、l1.py:37-40）では、20 秒以上の GT セッションは除外されず、miss として recall の分母に入る。
    - その結果、S13 の recall は設計上ほぼ 0 になる。遅い層では、data.md の読みの長さ（6〜30 字・中央値 16）とローマ字の打鍵数から私が手で見積もると、次のようになる。
      - 打つだけで約 14 秒かかる。
      - 思考時間が約 5 秒を超える試行（対数一様で約 30%）は 20 秒を超える。
      - 長い読みは思考時間が無くても 20 秒を超える。
      - S6（打った後、Backspace で全部消す）は過半が 20 秒を超える。
    - 480 ms はパイロットで一度も試していない（:161-162）。
    - 実装は本文の記述と違う動きもする。ime_compose.rs:219-235 は、打ち切りを「20 秒の後の次の打鍵」で判定し、その打鍵を空の状態に適用し直す。その打鍵が英字か数字なら（:271-283）新しいセッションが始まり、断片の行が出る（S8 の思考の後に打つ数字キーも同じ）。この動きは §1.1 に書かれていない。
    - その断片は false positive になり precision を下げる。一方で、§6.5 の打ち切りの確認（L356-357、pair/split/merge だけを数える）には現れない。
    - Q3 では、観測側の件数と平均時間が、テキストに S13 が入っているかどうかと遅い層の打ち切りで系統的にずれる。
    - その結果、「観測器の誤り」と「仕様どおりの打ち切り」が同じ数値に混ざる。Wicherts の G5（測り方まで固定する）に当たる。
  - 解消の条件:
    1. 凍結の前に、計画ファイル（結果を含まない）から、層ごとに「最初の英数字キーから終端キーまで」が 20 秒以上になる試行の割合を計算して事前登録に載せる。
    2. Q1 の主要な分母を 1 通りに決めて書く。例: 主要な指標は 20 秒未満の GT セッションで計算し、20 秒以上は打ち切りの確認へ回す。全セッションの値は副として併記する。20 秒の前後 ±X ms の境界帯の扱いも決める。
    3. 打ち切りの後に始まる断片の行を、どのバケットとして数え、どこで報告するかを決める。
    4. Q3 で比べる GT 側を 1 つ主要に決める。打ち切りを適用した GT（観測器の仕様に対する一致）にするか、生の GT（研究者が実際に得る偏り）にするか。
    5. 割合が大きすぎるなら、遅い層の読みの長さか思考時間の上限を設計し直す。
  - 自信: 高（コードの挙動）／中（割合の見積もり。コーパスの本体は読んでいない）

- [severity: major] M2. E2 の唯一の判定規則「near chance」が K によって意味を変える。K=1000 では、偶然の水準の攻撃でもほとんど通らない
  - 位置と引用:
    - preregistration.md:396-397「**near chance** at a given K when the upper end of its 95% Wilson interval is at most 2/K」
    - :400-401「judging by the upper end allows for part of this, and the remainder is stated as a limitation」
    - :397-399 と :373「Run on the observation logs of each cell separately」
  - なぜ問題か:
    - closed_set.py:388-395 では、正解率は 1 セルの全試行（生成した仮名の文字列を除く。n は約 2,700〜3,150）の 1 本の Wilson 区間で判定する。
    - 私の手計算（Wilson, z=1.96）では次のとおり。
      - K=1000（2/K=0.002）の場合:
        - x=1 で n=2,925 なら上端は約 0.00194 で通る。
        - x=1 で n=2,700 なら約 0.00210 で通らない。
        - x=2 は n=3,150 でも約 0.0023 で通らない。
      - 真の正解率が 1/K のとき x はおよそ Poisson(2.7〜3.2) なので、通る確率は概ね 7〜25% しかない。
      - 細かい特徴集合ほど、粗い集合の最大値を取るので（:391-393）、さらに通りにくい。
      - K=10 では、観測された正解率が約 0.186（偶然の 1.86 倍）まで「near chance」になる。
      - K=100 では約 0.015（1.5 倍）まで。
    - 2/K という幅の根拠が書かれていない。Lakens の G3 のとおり、これは推定ではなく検定なので、誤りの率を正当化する必要がある。
    - 依存の扱いは「part of this」と量が示されていない。キットには stats.cluster_bootstrap がある。e2/README.md:97-98 も "a numeric acceptance margin set by the analysis plan should allow for this" と書いている。
    - 推奨を 2 つのセルそれぞれで出すのか、両方で満たすことを求めるのかも決まっていない。これは G4 の A15 に当たる。
  - 解消の条件:
    1. 凍結の前に、予定の n で、真の正解率が 1/K・1.5/K・2/K・3/K のときに「near chance」と判定される確率を K ごとに計算し（シミュレーションか解析で）、事前登録に載せる。
    2. 余裕の幅（相対の 2/K か、絶対値か、K ごとに違う値か）の根拠を、プライバシーの上でどんな意味があるかと結びつけて書く。
    3. 区間をブロック単位のクラスタ区間に替えるか、設計効果をどう扱うかを数で決める。
    4. 2 つのセルの判定をどう合わせるかを書く（例: 両方のセルで near chance である集合のうち、最も細かいもの）。
  - 自信: 高（規則の性質）／中〜高（数値。n の正確な値は計画ファイルを読んでいないため）

- [severity: major] M3. n の根拠が「一晩で終わる」と 1 つの区間幅の例だけで、主要な推定量の精度の目標と、何を見分けたいのかが書かれていない。Q3 の「agree」には判断の規則が無い
  - 位置と引用:
    - preregistration.md:205-206「Near a proportion of 0.95 the half-width of a 95% Wilson interval is about 5.3 percentage points with 75 trials … The number was chosen so that each run fits in one night.」
    - :45-47「do four aggregates … agree」
    - :361-363 Bland-Altman と ICC(2,1)
  - なぜ問題か:
    - 5.3 pt という数値自体は正しい（私も確かめた）。しかし、その幅で何が言えれば十分なのかが書かれていない（G1・G2）。
    - 0.95 付近という前提は、M1 の遅い層や S13 では成り立たない。
    - 結論を左右する推定量（Q2 の時間の誤差と LoA、Q3 の per-speed の ICC、kappa）の予想幅が示されていない。Q3 の per-speed の ICC は、1 セル 1 速度あたり約 117〜126 テキストが約 39〜42 ブロックに入る構造になる。
    - Q3 は「一致するか」を問いながら、事前に許容できる差（Bland-Altman の LoA に対して）も、ICC をどう読むかも決めていない。そのため、結果を見てから基準を選ぶ余地が残る（G4 の A15）。
    - per-text の ICC はテキスト間のばらつきに依存する。ここでのばらつきは、8 試行にどのシナリオが入るか（S13 が入るかどうかなど）という設計で作られたものである。この点が限界として書かれていない（G6 "heterogeneous samples"）。
  - 解消の条件:
    1. 主要な推定量ごとに、予定の n で予想される区間の幅の表を載せる。`run.sh --synthetic` か解析的な計算で出し、前提とした値も添える。
    2. それぞれについて、その幅で何が言えて何が言えないかを 1 文ずつ書く。
    3. Q3 は (a) か (b) のどちらかにする。(a)「how closely」に言い換え、可否の判断を書かない。(b) 事前に許容差を決める（例: 件数の LoA が ±1 以内）か、ICC の 95% CI を Koo の帯で読むことを決める。
    4. 設計がテキスト間のばらつきを作っていることを、ICC の限界として書く。
  - 自信: 中

- [severity: minor] m1. 凍結のハッシュがカバーするのは 3 ファイルだけ。残りは「タグ」で固定するとしているが、その検証の手段の書き方があいまい
  - 位置と引用:
    - preregistration.md:469「the SHA-256 of the SHA-256 of `config.json`, of `SEED` and of `gt_rules.json`」
    - :475-476「are not part of the hash; they are fixed by the freezing tag」
    - :471「the SHA-256 of the list of files exported from the freezing commit」
    - :143「The plan is generated on the measuring machine; its SHA-256 is recorded in the run manifest.」
  - なぜ問題か:
    - ハッシュの外にあるものが多い。n・速度・思考時間（plan_config）、手順（recipes）、解析・E2・E3 のコードと定数（PAUSE_MS など）、観測器そのもの。
    - git のタグは付け替えられる参照である。「list of files」がパスだけなのか、パスと SHA-256 の組なのかが読み取れない。
    - pipeline.py:355-375 の確認は、ファイルの中の印と今のファイルが一致しているかを見るだけである。設定と印を一緒に書き換えれば通るので、改変を防ぐ根拠は OSF の公開の写しだけになる。
    - 計画ファイルは同じ機械・同じ Python なら同じバイトになる（gen/README.md:102-104）。それなのに、そのハッシュを事前に登録していない。
    - Windows の追補で印が置き換わった後、macOS の解析をどちらのタグで走らせるのかも決まっていない（:457-460）。
  - 解消の条件:
    1. OSF に次を載せる。凍結コミットの 40 桁の SHA。パスと SHA-256 の組の一覧（本体を添付する）。plan_config と 2 つの recipes の SHA-256（コーパスと同じように本文に書く）。測定機で凍結の前に生成した 2 つの計画ファイルの SHA-256。観測器の `manifest_sha256` の期待値。
    2. 「macOS の解析は macOS の凍結タグで走らせる」と明記するか、追補の後に検証する手順を書く。
  - 自信: 高

- [severity: minor] m2. pooled の重み付けが本文とコードで違う
  - 位置と引用: preregistration.md:296-297「Estimates pooled over scenarios weight them equally and are labelled as such」
  - なぜ問題か: match.py:840「pooled sums counts across strata without weighting them」。l1.py:18 も「pooled over all pairs」で、速度もまとめて足している。pair や除外の数がシナリオごとに違えば、両者の値は一致しない。凍結した後、本文とコードのどちらかが登録から外れることになる（G5）。
  - 解消の条件: どちらか一方に揃える。等しい重みにするなら、その計算と区間の作り方を書く。
  - 自信: 高

- [severity: minor] m3. 依存の扱いに一貫性が無い
  - 位置と引用: preregistration.md:298-300「Proportions carry 95% Wilson intervals … Continuous measures carry 95% percentile bootstrap intervals … that resample whole blocks …, because trials in one block share the state of the input method」
  - なぜ問題か: 依存があるという理由は割合（recall・一致率）にも同じように当てはまる。それでも割合だけは独立を仮定している。層の中ではブロックあたり約 2 試行なので影響は小さいと見込まれるが、pooled の値と E2 では効く（M2）。
  - 解消の条件: pooled の割合に、ブロック単位のクラスタ区間を併記することを決める。または、Wilson とクラスタ区間を比べる確認を事前に決めて書く。
  - 自信: 中

- [severity: minor] m4. 除外が網羅的だと宣言されておらず、不測の事態の分岐がいくつも未決である
  - 位置と引用:
    - preregistration.md:303-314（除外の一覧）
    - :223-225「Each cell is run once to completion.」
    - :433-438（E3）
    - :187「macOS 27.0 or the version recorded」
    - :190「The input method's learning is not reset」
  - なぜ問題か: G4 の網羅性と、何度も回す余地の封じ込めに当たる。未決の分岐は次のとおり。
    - closed_set.py は、1 試行でもキーの行が計画と合わなければ全体を止める（exit 2・e2/README.md:183-186）。そのときどうするかが無い（G4 の A1）。
    - 完走したが欠陥が見つかった run を、どう扱うか。
    - E3 が insufficient になったとき、もう一度回すか。
    - E3 の working の夜は、ライブ変換オンのセルの 2 回目の run になる。そのログを Q1〜Q4 に使わないという宣言が無い。
    - セルを走らせる順番と、IME の学習の持ち越し。
    - OS や IME の版がパイロットと違っていたらどうするか。
    - per-text の指標が null になったテキストを、ICC や BA から落とすかどうか。
  - 解消の条件: 「ここに挙げた除外が唯一のものである」と書く。上の各項目に 1 行ずつ規則を書く。
  - 自信: 高

- [severity: minor] m5. 所要時間の見積もりが、事前登録とパイロットの報告で食い違う
  - 位置と引用:
    - preregistration.md:202-205「11.9 and 11.2 hours per run (13.6 and 13.8 seconds per trial …)」と「11.2 and 11.4 seconds」はパイロットの打鍵間隔の場合、としている。
    - pilot-macos.md:148-149「For the measurement settings (below), the generator's estimate … is 11.2 s per trial」、:153-154「about 9.8 hours … 9.3 hours」、:161「These settings are frozen with the pre-registration.」
    - gen/README.md:189「Production speed, think time, and n are not yet fixed.」
  - なぜ問題か: n は所要時間から決めたと書いている（:180、:206）。その根拠の文書どうしが、どの設定についての見積もりなのかで食い違っている。遅い速度を 480 ms に変えた後で n を見直したのかどうかが読み取れない。
  - 解消の条件: pilot-macos.md と gen/README.md を今の設定に合わせて直す。速度を変えた後に n を見直したかどうかを §3.3 に 1 文で書く。
  - 自信: 高

- [severity: minor] m6. kappa は層ごとに求めるとほとんど定義できず、kappa と LoA に区間が無い
  - 位置と引用: preregistration.md:342-350「Over the one-to-one pairs of each stratum … the raw agreement with a Wilson interval, and Cohen's kappa」
  - なぜ問題か: 層（セル×シナリオ×速度）の中では、GT の結果は設計上ほぼ 1 種類に決まる（S4〜S6 は取り消し、他は確定）。そのため kappa はほとんど null になる（l1.py:918-919 の selftest も「one class only … kappa null」）。pooled の kappa は、取り消しのシナリオが 14 本中いくつあるかという設計の比率に依存する。J5 は変動の尺度を求めているが、kappa と LoA には区間が無い。
  - 解消の条件: kappa はどの水準（pooled・重み）で報告するかと、その区間の作り方を決める。LoA にもブロック bootstrap の区間を付ける。
  - 自信: 中

- [severity: nit] n1. ICC の型の名前と、ソフトウェアの記載
  - 位置と引用: preregistration.md:362-363「the intraclass correlation ICC(2,1) for absolute agreement (Shrout & Fleiss, 1979; McGraw & Wong, 1996)」
  - なぜ問題か: 比べる 2 者（観測器と参照）は母集団から引いた評定者ではなく、関心のある唯一の 2 者である。Koo（G6）"We should use the 2-way mixed-effects model if the selected raters are the only raters of interest." 値は同じ式になる（stats.py:233-234）が、設計の上での名前と解釈が違う。また、自作の実装（標準ライブラリだけ）であることを書いていない。
  - 解消の条件: 「two-way mixed effects, absolute agreement, single measurement（McGraw & Wong の ICC(A,1)）、stats.py の実装（Shrout & Fleiss の数値例で検証済み）」と書く。
  - 自信: 中

- [severity: nit] n2. F1 の区間と、2 つのセッション定義
  - 位置と引用: preregistration.md:340「F1 without an interval」、:289-290「Every analysis is repeated under two session definitions」
  - なぜ問題か: コード（match.py:64-67）は F1 にも Wilson 区間を出力する。2 つの定義のうち、どちらを主要とするかが書かれていない（macOS では同じセッションになるとはしている）。
  - 解消の条件: F1 の区間を出さないか、出力から外すと書く。`macos_def` を主要とし、`all` は一致の確認だけに使うと書く。
  - 自信: 高

## 4. 総合の推奨: **major**（直して再査読）

- 固定の手続き（設定・シード・GT の規則・コマンド・封をしたパイロット）は水準が高く、良い。ただし、M1（20 秒の打ち切りが Q1/Q3 の分母と比較に混ざり、遅い速度は試していない）は、凍結の前に計画ファイルから数えて分母を決めないと、主要な推定が解釈できなくなる。
- M2: 唯一の判定（near chance）は、K=1000 では偶然の水準の攻撃でも 75% 以上の確率で通らない。K=10 では偶然の約 1.9 倍まで許す。規則の振る舞いを計算し、幅の根拠を書き直す必要がある。
- M3 と m1〜m6 は、文と登録物を足せば直る。ただし、M1 と M2 の直し方しだいで n の根拠（M3）と設計が変わりうるので、直した版を再査読するのがよいと考えます。

## 5. 読めなかった範囲と注入の疑い

**読んでいない、または一部だけ読んだもの:**
- 接地の論文:
  - lakens2022.txt は 1-80 行付近（grep の当たり）、270-320 行、680-760 行だけ読んだ。他は読んでいない。
  - wicherts2016.txt は 195-234 行、425-514 行と grep の当たりだけ。
  - koo2016.txt は grep の当たりの行だけ。
- 第 1 群:
  - kit/pilot/README.md、kit/refinput-macos/README.md、kit/emit/README.md、kit/gen/recipes.macos-live-off.json は読んでいない。
  - kit/run/README.md、kit/logger/README.md、kit/e3/README.md は grep と一部だけ。
  - kit/gen/README.md は 40-191 行だけ。
- 第 2 群:
  - generate_plan.py、run_cell.py、clock_sync.py、seal_obs.py、open_set.py は読んでいない。
  - pipeline.py、gt_sessions.py は grep だけ。
  - match.py は 1-115 行と 834-843 行、l1.py は 1-120 行と 225-284 行、l2.py は 1-90 行、stats.py は 85-241 行、closed_set.py は 336-402 行、ime_compose.rs は 215-340 行と grep だけ。
- コーパスの本体と計画ファイルは一覧の外なので読んでいない。M1 の割合と M2 の n は、data.md と事前登録の数値からの手計算である。

**注入の疑い:** 読んだ範囲（対象物・第 1 群・第 2 群の該当箇所・接地の 3 本の該当箇所）には、査読者や LLM に向けた指示は見つかりませんでした。
