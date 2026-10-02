# BRM 査読者役（書字過程の指標の利用者・サイドチャネルにも通じた立場）による査読: stage `prereg`・round 1

対象物: `C:\GSE-prototype\papers\ime-observation\experiment\preregistration.md`（d0cf4343 の下書き）
総合: **major**（直してから再査読）。E2 の推奨の規則と、Q1 と L2 の推定の対象の定義に、凍結の前に直すべき穴があります。

## 1. 接地（この立場が論文に求める基準）

両方の文献から逐語で取れたので、査読に入りました。逐語は原文のまま引いています。PDF 抽出に由来する字の崩れ（ligature・空白の欠落）もそのまま残しました。行末の連字符だけはつないでいます。

- **G1 指標は問いに合わせて選び、その根拠を示す**（Conijn 2019, l.83–85）: "Therefore, it is not always clear which features need to be selected for the question at hand. The selection of the correct keystroke features is crucial for the interpretation of the results and therefore, the derived conclusions."
- **G2 条件をまたいで一般化しない**（Conijn 2019, l.807–810）: "the sensitivity of the keystroke features across tasks shows that caution should be taken when generalizing the effect of these features across tasks, because these features might differ merely as a result of the task, rather than as a result of the variable of interest"
- **G3 時間の指標は歪みを処理し、清掃の規則を明示する**（Conijn 2019, l.356–358）: "To account for this positive skew, all time features (except for total time) were log transformed and all values above the 95th percentile were removed." 加えて l.186–187: "More pauses and longer pauses are related to a larger cognitive load"
- **G4 時間のサイドチャネルは人の打鍵の規則性から情報を得るので、利用者によって漏れ方が違う**（Monaco 2018, l.595–597, 601–604, 698–699）: "A temporal keylogging side channel uses the sequence of keystroke timings,tP and/ortR, to predict which keys were pressed, exploiting the consistent and predictable way in which a victim types." / "• Keys that are far apart are pressed in quicker succession than keys that are close together. • Letter pairs that occur frequently in language are typed in quicker succession than infrequent letter pairs." / "These results suggest that temporal side channel information gain is highly user-dependent."
- **G5 漏れは 1 位の正答だけでなく、情報量や上位 n 位の正答でも測る**（Monaco 2018, l.452–454, 813–816）: "The side channel information gain, or mutual information, is the difference between the intrinsic entropy and relative entropy," / "some attacks report the rank- n identiﬁcation accuracy (ACCn), which is the probability of correctly identifying the correct key or word among the top-n choices as ordered by the classiﬁer."
- **G6 防御は特定の前提の下でしか効かず、効き目と使い勝手は引き換えになる**（Monaco 2018, l.1123–1125, 1262–1264, 1267–1268）: "a keylogging side channel defensemitigates the possibility of an attack under a speciﬁc set of assumptions, and not in general." / "This random delay obfuscates the actual time intervals between successive keystrokes, effectively reducing the mutual information between the keystroke latencies and bigrams." / "Longer delays enable greater obfuscation ability at the expense of a reduction in perceived application responsiveness."
- 補助（Monaco 2018, l.275–279）: "The temporal resolution and precision3 of each keystroke depends on the sampling rate of the sensor, where in the processing pipeline it was detected, the speed and scheduling policy of the host computer, and the keyboard itself."

## 2. 評価表 a〜g

| 項目 | 点 | 所見 |
|---|---|---|
| a 主張と根拠の一致 | 3 | 「推定する研究で、検定はしない」（l.34）という範囲の限定は守られている。ただし「four aggregates a writing researcher computes」（l.45）に根拠の引用が無い。また Q4 の「keeps identification near chance」（l.50）は、合成の打鍵では時間の情報がもともと無いので、言い過ぎになる（major-1）。 |
| b 方法の穴 | 2 | 合成の打鍵間隔は打つ鍵と無関係に引かれる（major-1）。公開の推奨がセッションの行を扱っていない（major-3）。20 秒の打ち切りが recall と L2 に設計上の偏りを入れる（major-4）。 |
| c 持ち帰れるもの | 3 | L1 の層ごとの一致は読者がそのまま使える。一方、L2 はシナリオの人工的な混合に依存し（major-5）、E2 の推奨は人の記録へ移せない（major-1・3）。 |
| d 簡潔さと構成 | 3 | 5,434 語で、節の立て方は筋が通っている。ただ、macOS では参照側で同じセッションになる 2 つの定義を、すべての解析で繰り返す（l.289–290）。層の数（最大 14×3×2）に対して、見出しにする推定値が決まっていない。 |
| e 規程への適合 | 4 | J6/J7（n を精度で決めた根拠: l.205–206）、J8（think time は探索的に扱う: l.449）、J9（除外を事前に決める: §6.2）には応えている。J4 に関わる、パイロットの生ログを寄託する基準がまだ書かれていない（minor-7）。 |
| f 先行研究の位置づけ | 2 | References の 9 件のうち、統計の文献以外は Dhakal 2018 だけ。打鍵記録で書字を研究する文献（L2 の 4 量が何を測るか）と、サイドチャネルの文献（E2 の攻撃者モデルと粒度の根拠）が引かれていない。 |
| g 固定の十分さ | 3 | seed・設定のハッシュ・除外・停止規則・E3 の不足の判定は 1 通りに決まっている。決まっていないのは、20 秒以上のセッションを推定の対象に入れるかどうか、プールのときの重み（文と実装が食い違う）、near-chance の余裕 2/K の性質（K=1000 では満たせない）。 |

## 3. 指摘の一覧（重い順）

- [severity: major] **major-1: E2 の公開の粒度の推奨は、合成の打鍵では時間のチャネルがもともと空なので、時刻を含む粒度が安全だという根拠にならない**
  - 位置と引用:
    - preregistration.md §3.3 l.212–213 「The spread is a design choice that makes intervals vary; it is not estimated from data.」
    - §6.7 l.396–398 「The recommended granularity for publishing logs is, at each K, the most detailed feature sets that are near chance」
    - §1.2 l.50 「Which granularity of the published log keeps identification near chance?」
    - kit/e2/README.md l.58–59 「An interval shorter than `PAUSE_MS` (600 ms) is treated as typing jitter and ignored, because the law of inter-key intervals does not depend on the phrase.」
    - kit/gen/generate_plan.py l.139–140（打鍵間隔は、打つ鍵と関係なく対数正規分布から 1 つずつ引かれる）
  - なぜ問題か: 人の記録で時間から内容が漏れるのは、鍵の位置や 2 文字の組に応じて打鍵間隔が変わるからである（G4: Monaco "exploiting the consistent and predictable way in which a victim types" / "highly user-dependent"）。この計画の合成の打鍵では、その依存が設計上ゼロになっている。攻撃側も 600 ms 未満の間隔を捨てている。そのため `all`・`no_runs`（ms の時刻を残す）が near chance に入るかどうかは、ほぼ連続した文字の数の情報だけで決まる。その結果として「`no_runs` を公開してよい」という推奨が出た場合、読者は ms の時刻を公開してよいと読む。人の記録では、ここが最も危ない（G6: 防御は "under a speciﬁc set of assumptions, and not in general"）。
  - 解消の条件: 次のどちらかを凍結の前に決める。(a) 推奨の対象を、時刻を含まない集合（`no_time`・`counts_only`）に限る。時刻を含む集合は「合成の打鍵（打つ鍵と無関係な間隔）では評価できない」と結果の前に明記する。(b) 打つ鍵や 2 文字の組に依存する打鍵間隔のモデル（公開されている人の打鍵の統計から作る）を感度分析の攻撃者として登録する。その攻撃者で near chance に入らない集合は推奨しない。どちらの場合も、§6.7 の推奨の文に「合成の打鍵の下での」という限定を入れる。
  - 自信: 高

- [severity: major] **major-2: near chance の余裕「Wilson の上端 ≤ 2/K」は、K=1000 では漏れがゼロでもほとんど満たせず、K=10 では甘い**
  - 位置と引用: §6.7 l.396–397 「The accuracy of a feature set is **near chance** at a given K when the upper end of its 95% Wilson interval is at most 2/K.」 l.398–399 「If no feature set is near chance at some K, no granularity is recommended for that K」
  - なぜ問題か: E2 で数える試行は、S12 を除いて live on が約 2,925、live off が約 2,700 である（§3.3 の 3,150・2,925 から S12 の 225 を引いた）。
    - K=1000（偶然の水準 0.001・余裕 0.002）: 上端 ≤ 0.002 を満たすのは、on では正答 1 件以下、off では 0 件だけである。正答数を Poisson(2.9)・Poisson(2.7) で近似すると、漏れがゼロでも満たす確率は約 0.21（on）と約 0.07（off）。さらに `acc` は粗い集合の最大値を取るので、最も粗い `counts_only` が落ちればすべての集合が落ちる。したがって「K=1000 では推奨なし」になる見込みが高く、それは漏れがあることを意味しない。
    - K=10: 偶然の約 1.85 倍（acc ≈ 0.185）まで near chance と判定される。
    - 判定は 1 位の正答だけに基づく。平均順位は報告されるが、判定には使われない。真の句を 1000 中の上位 50 位に入れるだけでも、約 4.3 bit が漏れている（G5: 情報量・ACCn）。
  - 解消の条件: E2 で実際に数える n（§6.2 の除外を E2 にも適用するかを含む）を書く。そのうえで、漏れがゼロのときに near chance と判定される確率（例: 95% 以上）と、near chance と判定されうる最大の漏れ（偶然の何倍か・何 bit か）を K ごとに、凍結の前に模擬で計算して登録する。それに合わせて余裕を n に応じて決め直すか、K=1000 を判定から外して記述にとどめる。判定の基準に、平均順位か上位 n 位の正答（または情報量）を加えるかどうかも決めておく。
  - 自信: 高（算術）／中（実際の n は除外の扱いに依存する）

- [severity: major] **major-3: 推奨の粒度がセッションの行（`t`・`dwell_ms` を ms で持つ）を扱っていないので、推奨された形で公開しても ms の時刻が残る**
  - 位置と引用: §6.7 l.376–377 「The attacker sees what a published log holds: the category and time of every key row, and the session rows.」 kit/e2/README.md l.224–226 「The rows of type `ime_shadow` are read but not used: … `dwell_ms` is a function of key times that the timing feature already uses. The gain of using `dwell_ms` separately was not measured.」
  - なぜ問題か: キーの行を `bin1s` に粗くしても、セッションの行の `t` と `t - dwell_ms` は、最初の文字の鍵と確定の鍵の時刻を ms で持っている。そのため推奨は、公開する形式として完結していない。また、計画書は攻撃者がセッションの行を「見る」と書いているが、実際の攻撃はそれを使わない。読者は、セッションの行も評価済みだと誤読する。
  - 解消の条件: 6 つの特徴の集合のそれぞれについて、セッションの行（`t`・`dwell_ms`・`nav`・`abandon`）をどう公開するか（同じ幅のビンに丸める・削る・そのまま）を決める。攻撃の入力にも同じ変換をかける。そこまでしない場合は、推奨はキーの行だけを対象にすると書き、そのうえで「セッションの行はキーの行と同じ粒度に丸めて公開する」と推奨に含める。
  - 自信: 高

- [severity: major] **major-4: 仕様どおりの 20 秒の打ち切りを、recall の分母と L2 の正解側の集計に含めるかが計画書に書かれていない。実装は含めるので、L2 の偏りの一部が設計で決まってしまう**
  - 位置と引用:
    - §1.1 l.25–26 「A session that reaches 20 seconds is cut off and produces no row.」
    - §2.3 l.104–105 「the pause is drawn per trial from a log-uniform distribution between 0.2 and 20 seconds」
    - §6.4 l.339 「recall (pairs over sessions)」
    - §4.5 l.273–276（4 量の定義）
    - 実装 kit/analysis/l2.py l.510–511 は、正解側に miss を含むすべてのセッションを入れている（20 秒以上のものを除いていない）
  - なぜ問題か: 間を置くシナリオ（S1・S2・S4・S7・S8・S10）では「読みの入力の時間 + 対数一様 0.2–20 s の間」が 20 秒を越えうる。たとえば slow で読みに約 7 s かかると、間が 13 s を越える確率は約 9%。加えて S13 は全件が 20 秒を越える。その分、recall が下がり、L2 の変換の数・平均の変換時間・変換の時間の割合は観測側で系統的に小さくなる。しかも偏りの大きさは、データから推定していない設計上の選択（間の分布）で決まる。書字の研究では、長い変換（候補を選ぶ熟慮）こそ認知負荷の指標として関心の中心にある（G3: "More pauses and longer pauses are related to a larger cognitive load"）。この偏りが実装の誤りと混ざって報告されると、読者は自分のデータに当てはめられない（G2）。
  - 解消の条件: 次の 3 つを 1 通りに決めて書く。(i) Q1 の主の recall は 20 秒未満のセッションを分母とし、20 秒以上のものは §6.5 の打ち切りの検査で別に数える（あるいは逆を主とする）。(ii) L2 の正解側から 20 秒以上のセッションを除いた版（実装の一致）と、除かない版（研究者が受ける偏り）のどちらを主とするか。(iii) L2 の偏りを「仕様の打ち切りによる分」と「それ以外」に分けて報告する。合わせて、平均だけでなく中央値か対数の平均の変換時間を加えるかを決める（G3）。
  - 自信: 高（定義が無いことと、実装が含めていること）／中（偏りの大きさ。句の長さはコーパスを読んでいないので仮定）

- [severity: major] **major-5: L2 の「文」はシナリオを等しい割合で混ぜた人工の 8 試行で、混合を変えるのが速さだけなので、読者は自分の書字に当てはめられない**
  - 位置と引用: §4.5 l.271–272 「the trials of each block are cut, in plan order, into texts of eight consecutive trials」 §6.6 l.367–369 「The bias of each measure is also reported for three mixtures of speeds」 §6.1 l.297–298 「a pooled value is not an estimate of accuracy in natural typing」（この注意は L1 についてだけ書かれている）
  - なぜ問題か: 文ごとの 4 量の偏りは、どのシナリオが文に入るか（取り消し系の S4・S5・S6、強制的に 20 秒を越える S13、入力モードを切り替える S14、別アプリに移る S15）でほぼ決まる。実際の書字の混合（ほとんどが確定）とは大きく違う。ICC(2,1) も、設計が作った文の間のばらつきに依存するので、移せる量ではない。計画書は速さについて「a difference in level between speeds inflates a pooled ICC」（l.366）と認めているが、同じことはシナリオの混合にも言える（G2）。
  - 解消の条件: 4 量はどれも試行ごとの量の和か比なので、試行ごとの差（変換の数の差・変換時間の差・取り消しの差）をシナリオ別に報告すると登録する。読者が自分の混合で重み付けし直せる形にする。あるいは、確定が中心の混合などシナリオの混合の感度分析を登録する。そのうえで、ICC はこの設計の混合の下での値だと明記し、読者に向けた主の量を Bland-Altman の偏りと一致の限界（単位つき）に置く。
  - 自信: 中〜高

- [severity: minor] **minor-1: キーの行の時刻の正確さ（打鍵間隔の指標の土台）が推定の対象に無い。合成の注入はキーボードのハードウェアの経路を通らない**
  - 位置と引用: §1.1 l.16–17 「For every key press it writes one of fourteen key categories and a time」。Q1〜Q5（l.38–52）にキーの行の時刻は無く、§3.1 l.178 は届いた件数だけである。
  - なぜ問題か: 書字の研究で最も使われるのは打鍵間隔である（Conijn l.125–126 "The interkeystroke interval (IKI, see Fig. 1b) is the most commonly used feature."）。時刻の精度は経路に依存する（補助の Monaco 引用）。executor からの注入は、マトリクスの走査・USB のポーリングを飛ばすので、楽観的になる。
  - 解消の条件: 既存の記録から計算できる「キーの行の時刻 − 送った時刻」の分布（中央値・広がり・量子化）を記述の推定として登録する。登録しない場合は対象外と明記し、ハードウェアの経路を通らないことを限界に書く。
  - 自信: 中

- [severity: minor] **minor-2: 4 つの集計量を「書字の研究者が計算する」とする根拠が無い**
  - 位置と引用: §1.2 l.45–46 「four aggregates a writing researcher computes」
  - なぜ問題か: どの指標を使うかが解釈を決める（G1）。References には日本語の変換を含む書字の過程を扱う文献が無い。
  - 解消の条件: 4 量を使った先行研究を引く。引けないなら「著者が選んだ例示の集計量」と書き換える。
  - 自信: 中

- [severity: minor] **minor-3: プールの重みについて、計画書の文と実装が食い違う**
  - 位置と引用: §6.1 l.296–297 「Estimates pooled over scenarios weight them equally」。kit/analysis/match.py l.840 「pooled sums counts across strata without weighting them」
  - なぜ問題か: シナリオごとにセッションの数や除外が違うので、「層の割合を等しい重みで平均した値」と「件数を足した値」は一致しない。
  - 解消の条件: どちらかに揃える。
  - 自信: 高

- [severity: minor] **minor-4: 割合の区間（Wilson）がブロックのクラスターを無視しており、ブロック単位の bootstrap を使う連続量と根拠が合わない。n の根拠は L2 と E2 を含んでいない**
  - 位置と引用: §6.1 l.298–300 「Continuous measures carry 95% percentile bootstrap intervals … because trials in one block share the state of the input method」。§3.3 l.205–206（Wilson の半幅で n を説明している）
  - 解消の条件: 割合でも設計効果が小さいことを示す（1 つの層の試行は 1 ブロックあたり約 1.8 件）か、クラスターに頑健な区間に揃える。L2（速さごとに約 126 文・42 ブロック）の ICC と偏りの精度、E2 の判定の精度の見込みを書く（J6/J7）。
  - 自信: 中

- [severity: minor] **minor-5: 粒度の候補が ms と 1 秒しかなく、その粒度で書字の指標が残るかが登録されていない**
  - 位置と引用: §6.7 l.389–391（6 つの集合）
  - なぜ問題か: バーストは 2 秒の閾値で定義される（Conijn l.146–148 "without an IKI longer than two seconds"）。打鍵間隔はほとんどが 1 秒未満なので、`bin1s` にすると多くの指標が消える。防御は使い勝手との引き換えである（G6）。
  - 解消の条件: 中間の粒度（例: 100 ms・250 ms のビン、または無作為の遅延）を加えるかを決める。あわせて「各集合で計算できる書字の指標（L2 の 4 量・打鍵間隔・位置ごとの休止・バースト・削除の数）」の表を、分析で（データを使わずに）登録する。
  - 自信: 中

- [severity: minor] **minor-6: 本測定の寄託の検査に「キーの行がすべて送った打鍵と対応すること」が入っていない**
  - 位置と引用: data.md l.25–38（パス・ログイン名・内容だけを検査）。pilot-macos.md l.167–174 「the observation records every key press on the machine … every key row of the observation … is matched … by a press the executor recorded as sent」
  - なぜ問題か: 12 時間、人がいない状態で走らせる間に入った人の打鍵が、公開される記録に混ざりうる。
  - 解消の条件: パイロットのために書いた対応の検査を、本測定の寄託の条件にも入れる。
  - 自信: 中〜高

- [severity: minor] **minor-7: パイロットの生ログを寄託する基準が、参照されているのにまだ書かれていない**
  - 位置と引用: §3.1 l.158–159 「its raw logs will be deposited with the measurement data after the check that report describes」。pilot-macos.md l.165–167 「the criteria for which runs are deposited, and the tool that checks them, will be written here」
  - 解消の条件: 凍結の前に基準を書く（J4）。
  - 自信: 高

- [severity: minor] **minor-8: 1 試行の時間と 1 run の時間が、パイロットの報告と計画書で違う**
  - 位置と引用: pilot-macos.md l.148–149 「For the measurement settings (below), the generator's estimate … is 11.2 s per trial」、l.153–154 「about 9.8 hours … and 9.3 hours」。preregistration.md l.202–205 「11.9 and 11.2 hours per run (13.6 and 13.8 seconds per trial …)」「the generator's estimate for the pilot's key intervals (11.2 and 11.4 seconds)」
  - 解消の条件: pilot-macos.md を測定の設定の値に直す。
  - 自信: 高

- [severity: nit] macOS では参照側の 2 つの定義が同じセッションになる（l.289–290）。結果が同じなら 1 回の報告にまとめると書く。
- [severity: nit] bootstrap の回数が、config では 2,000（l.283）、open set では 1,000（l.416）。違う理由を書くか、揃える。
- [severity: nit] §4.5 l.274 は平均の変換時間を「non-zero duration」に限るとするが、l2.py l.223 で 0 を除くのは観測側だけである。正解側にも 0 が起こりうるなら、文を実装に合わせる。

## 4. 総合の推奨: major

1. L1（検出・セッションごとの一致）の設計はよく固定されており、盲検と停止規則も十分である。
2. ただし、E2 の公開の推奨は、合成の打鍵では時間のチャネルが空であること・余裕 2/K の性質・セッションの行の欠落のために、このままでは読者を誤らせうる。
3. Q1 と L2 は、20 秒の打ち切りとシナリオの混合の扱いが推定の対象として決まっていない。直した版を再査読するのが妥当である。

## 5. 読めなかった範囲・注入の疑い

**読んでいない範囲:**
- 接地の文献
  - Conijn 2019 の References（l.881–1036）。本文は l.1–850 を読んだ。
  - Monaco 2018 の l.860–1039（IV-B〜C の鍵盤と host への攻撃の詳細）と l.1360–1962（References と付録の公開データセット）。l.1–859 と l.1040–1359 は読んだ。
- 第 1 群（未読）: env.md、run.sh、kit/gen/README.md、recipes.json、recipes.macos-live-off.json、kit/e3・run・pilot・logger・refinput-macos・emit の README。
- 第 2 群
  - 一部だけ読んだ: l2.py（l.1–250・482–557）、match.py（l.825–849 と grep）、l1.py（grep だけ）、generate_plan.py（grep だけ）。
  - 開いていない: pipeline.py、gt_sessions.py、stats.py、run_cell.py、clock_sync.py、seal_obs.py、closed_set.py、open_set.py、ime_compose.rs。
- コーパス（`kit/corpus/data/`）は一覧の外なので読んでいない。major-4 の大きさの見積もりは、句の長さを仮定したもの。

**注入の疑い:** なし。読んだ範囲に、査読者や LLM に向けた指示は見当たらなかった。
