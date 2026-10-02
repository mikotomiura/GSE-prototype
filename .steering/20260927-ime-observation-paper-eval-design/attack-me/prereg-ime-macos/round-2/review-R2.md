# paper-reviewer 報告: BRM の査読者役（打鍵記録を使う書字研究の利用者で、公開時のサイドチャネルにも通じた立場）・stage `prereg`・round 2

対象物: `C:\GSE-prototype\papers\ime-observation\experiment\preregistration.md`（context-A が示す版）

**総合の推奨は major です。** ただし直しは文の修正で済むものが多く、再査読は §6.2・§6.4・§6.7・§6.8 と、パイロットの生ログの預けの文に絞れます。

---

## 1. 接地（査読の前に、2 本の文献から基準を逐語で抜き出した）

**C1. 指標の選び方は、問いと解釈に直結している必要がある**
- Conijn et al. 2019: "The selection of the correct keystroke features is crucial for the interpretation of the results and therefore, the derived conclusions."
- この基準で見ること: L2 の集計量と公開の粒度が、書字研究の指標を支えられるか。

**C2. 書字の指標は、秒以下から数秒の休止と、その位置に依存する**
- Conijn: "frequencies are extracted, such as the number of IKIs between 0.5–1.0 s, 1.0–1.5 s, 1.5–2.0 s, 2.0–3.0 s, and > 3.0 s"
- Conijn: "written language bursts are often operationalized as sequences of text production (keystrokes) without an IKI longer than two seconds"
- Conijn: "Pauses before words are considered to reflect planning, retrieving, verifying, or editing processes, while pauses within words are considered to be related to typing skills"
- この基準で見ること: 1 秒のビンは、人の記録では言語の単位に結びついた休止を残す。逆に、それより粗い粒度では書字の指標が消える。

**C3. 条件で値が動く量を、別の条件へ一般化しない。時間の量は歪んでいる**
- Conijn: "caution should be taken when generalizing the effect of these features across tasks, because these features might differ merely as a result of the task"
- Conijn: "To account for this positive skew, all time features (except for total time) were log transformed"

**C4. 防御は前提の下でだけ効く。解像度を下げることは難読化（obfuscation）の一種である**
- Monaco 2018: "a keylogging side channel defense mitigates the possibility of an attack under a specific set of assumptions, and not in general."
- Monaco: "Obfuscation can be achieved by increasing background noise or decreasing the sensor resolution."

**C5. 時間のチャネルから漏れる量は、人と打鍵の速さで変わる**
- Monaco: "These results suggest that temporal side channel information gain is highly user-dependent."
- Monaco: "information gain could vary with different users based on different typing speeds and styles"

---

## 2. 引き継ぎの判定（carryover-R2.md の 16 件）

| 指摘 | 判定 | 理由（1 行） | 今の版の位置 |
|---|---|---|---|
| major-1 | 部分的に解消 | ms の集合は推奨から外し、推定だけの報告にした。だが 1 秒のビンを残した理由が、この設計では確かめられない（新しい指摘 1）。 | §6.8 第 4 段落（l.609-615）・§7 "The input is synthetic" |
| major-2 | 解消 | K=1000 を判定から外し、判定の通る確率の表を事前に載せた。K=10 と 100 の両方を要するので K=100 が実際の関門になる。 | §6.8 l.617-635 |
| major-3 | 部分的に解消 | セッションの行を対象外と明記した。だが推奨の文は今も「ログを公開するときの粒度」と書いている（新しい指摘 4）。 | §6.8 l.588-589・l.632-633 |
| major-4 | 部分的に解消 | (i) under_limit を主の範囲とし、範囲は送出の記録から決める。(ii) 問 3 は全試行を主、under_limit を副にした。(iii) 偏りの分解と、中央値か対数の変換時間はどちらも無い。 | §4.5・§6.4・§6.6・§7 |
| major-5 | 部分的に解消 | シナリオ × 速さごとの試行ごとの差を、ブロックのブートストラップつきで出すようにした。だが繰り越しの汚染があるので、読者の混合で重み付けし直せない（新しい指摘 6）。 | §6.7 第 2 段落（l.578-581）・`l2.py` の per_trial |
| minor-1 | 解消 | 送出の遅れ、両方向の到達、行の遅れ、打鍵間隔の誤差を報告する。物理キーの経路には主張しないと明記した。時刻の量子化は、間隔の誤差の分布に現れる。 | §6.3 第 2 段落・§7 |
| minor-2 | 解消 | 問 3 を "might compute" に改め、文献から選んだ量ではないと明記した。 | §1.2 問 3・§4.6 最後の文 |
| minor-3 | 解消 | プールの値を「件数の和」と書いた（実装と一致）。 | §6.1 第 1 段落 |
| minor-4 | 解消 | 割合の精度の表、連続量の精度の式、E2 の通る確率の表を足した。プールの割合の区間は「不確かさの下限」と読むと明記した（主の範囲で n が減る点は新しい指摘 7）。 | §3.3・§6.1・§6.8 |
| minor-5 | 未解消 | 中間の粒度も、粒度ごとに計算できる書字の指標の表も無い。新しい指摘 1 で推奨が時刻の無い集合だけになると、時刻の指標が全部失われるので、この欠けはさらに重くなる（C2）。 | §6.8 |
| minor-6 | 解消 | 送った打鍵の無い行（excess）と、試行の外の行を、預ける前に検査するようにした（欠けた打鍵は検査しない。新しい指摘 2 と nit 1）。 | `data.md`:39-43 |
| minor-7 | 未解消 | `pilot-macos.md`:170-171 は今も "will be written here"。しかも事前登録から、パイロットの生ログを預けるという文が落ちた（後退。J4 "including all relevant raw data"）。 | §3.1・`pilot-macos.md` "Raw logs" |
| minor-8 | 解消 | 3,150 × 13.6 s ≈ 11.9 h、2,925 × 13.8 s ≈ 11.2 h で数字が合う。パイロットの 11.2 / 11.4 s も、パイロットの間隔での推定と区別して書いた。 | §3.3 l.246-250・`pilot-macos.md`:149, 158 |
| nit（2 つの定義） | 解消 | `macos_def` が解析の定義、`all` は同じセッションかの確認だけと書いた。 | §5 第 2 段落 |
| nit（bootstrap の回数） | 解消 | open set も `--bootstrap 2000` に揃えた。 | §6.8 open set のコマンド |
| nit（non-zero duration） | 解消 | `dwell_ms` が 0 でない行で計算すると書き直した。 | §4.6 |

内訳: 解消 10、部分的に解消 4、未解消 2。

---

## 3. 評価表

| 観点 | 点 | 所見 |
|---|---|---|
| a 主張と根拠の一致 | 3 | 全体の主張は控えめで良い（§6.1 は評価の語を禁じ、§6.8 は "the results hold for these attacks" と書く）。だが、1 秒のビンを推奨すること（指摘 1）、「ログ」の公開粒度と書くこと（指摘 4）、上端で判定すれば依存を一部吸収できるという文（指摘 5）の 3 か所は、根拠を超えている。 |
| b 方法の穴 | 3 | 打鍵が 1 つ欠けると E2 の推奨が丸ごと消える（指摘 2）。問 3 の主の値は、この設計の思考時間の分布で決まる（指摘 3）。重み付けし直しは繰り越しで成り立たない（指摘 6）。 |
| c 持ち帰れるもの | 3 | 仕様の範囲の中での一致、配送の報告、試行ごとの差は、読者に使える。だが推奨の粒度で書字の指標が残るかは分からない（minor-5）。L2 の主の値は、読者の作業へ持ち出せない。 |
| d 簡潔さと構成 | 3 | 打ち切りの説明が約 10 か所（§1.1, §1.2, §2.3, §3.1, §3.3, §4.3, §4.5, §6.2, §6.4, §6.6, §7）に繰り返される。配送の説明が 4 か所（§1.2, §2.2, §6.3, §7）、合成の間隔がキーによらないことが 3 か所（§3.3, §6.8, §7）。どれも 1 か所に置いて参照で足りる。一方で「読者が何を持ち帰るか」の短い一覧はどこにも無い。足された表 5 つは必要なもの。 |
| e 規程への適合 | 3 | J3（OSF・Open Practices）は満たす。J9（除外を事前に決める）も Q1〜Q3 では満たす。J4 は、パイロットの生ログを預ける文が落ちたので満たさない（minor-7）。J5 は、区間を付けない連続量が §1.2 の文と食い違う（指摘 9）。J6/J7 は、主の範囲の n の根拠が書き直されていない（指摘 7）。 |
| f 先行研究の位置づけ | 3 | 引用は打鍵の間隔の Dhakal だけ。4 つの集計量は「文献の総説から選んでいない」と正直に書いた。だが 1 秒のビンと 2/K の余裕に、書字の休止のしきい値（C2）も、解像度を下げる難読化（C4）も参照していない。 |
| g 固定の十分さ | 4 | 範囲、比較、主の量、照合、除外、n の表、停止の規則、near chance の規則と通る確率は、1 通りに決まった。残るのは 4 点: E2 に除外を当てるか、open set と推奨の関係（指摘 8）、問 3 がどの比較で計算されるかの文（指摘 3）、区間を付けない量の例外（指摘 9）。 |

---

## 4. 新しい指摘（重い順。round 1 の指摘の再掲は入れていない）

- **[severity: major] 1 秒のビンの集合を推奨に残したことが、ms の集合を外した理由そのものと矛盾する**
  - 位置と引用: preregistration.md §6.8 l.612-615「The recommendation considers only the sets that keep no time or times in 1-second bins (`bin1s`, `bin1s_count`, `no_time`, `counts_only`), in which intervals between particular keys, of the order of tens of milliseconds, do not survive. Pauses between words and phrases, which human logs also carry, are not modelled either (section 7).」
  - なぜ問題か:
    - ms の集合を外した理由は、合成の間隔がキーによらないので、時間のチャネルが作りからして空だということだった（l.609-612）。
    - 1 秒のビンが人の記録に残すのは、2 字の組の間隔ではない。残るのは、語や句の境の 1 秒以上の休止と、ビンごとの英字の数である（`bin1s` は英字の連続の長さを残す）。この 2 つが合わさると、読みの区切りが分かる。
    - その情報も、この設計では作りから空である。間隔はキーによらずに引かれ、思考時間は句によらない。さらに攻撃は 600 ms 未満を捨て、ビン 1 つ分を割り引く。
    - だから `bin1s` と `bin1s_count` が near chance になっても、ms の集合と同じく、人の記録へ持ち出せない。これに対し、`no_time` と `counts_only` の区分の並びは時刻によらないので、人の記録へ持ち出しやすい。
    - 接地: Conijn「Pauses before words are considered to reflect planning…」「…without an IKI longer than two seconds」。Monaco「…under a specific set of assumptions, and not in general.」
  - 解消の条件: 次のどちらか。
    - (a) 推奨の対象を `no_time` と `counts_only` に限り、`bin1s` と `bin1s_count` は ms の集合と同じく推定だけを報告する。
    - (b) 語や文節の境に休止を置く合成の条件（分布を事前に決める）を足し、そこで 1 秒のビンを確かめてから推奨の対象にする。
  - 自信: 高（論理）／中（漏れる量）

- **[severity: major] 打鍵が 1 つ欠けるだけで、E2 の推奨が丸ごと消え、立て直す規則が無い**
  - 位置と引用: §6.2 l.469-470「If the closed-set attack stops because the observed presses of some trial do not agree with the plan, the closed set of that cell is reported as not computed, with the trial named, and no recommendation is made (section 6.8).」。実装は `kit\e2\closed_set.py`:980「one missing press stops the run instead of shifting later trials (exit 2)」、`kit\e2\open_set.py`:70-71「the assignment is refused when the counts or the number of alphabetic keys differ」。
  - なぜ問題か:
    - 推奨には 2 つのセルの両方が要る。1 つのセルは一晩で数万打鍵を送る。
    - パイロットでは、入力モードのキー以外に欠けた打鍵は約 8,000 打鍵中 0 だった。この数では、打鍵あたりの欠けの率の 95% 上限は約 4×10⁻⁴ にしかならず、セルあたり 2 桁の欠けを否定できない。
    - `data.md` の手順 4 は余分な行だけを検査し、欠けた打鍵は検査しない。§3.4 がやり直すのは中止された run だけ。open set が止まる場合は §6.2 に書かれていない。
    - つまり、この研究で唯一の判定が、1 回の取りこぼしで成り立たなくなる。
  - 解消の条件: 次の 3 つを事前に決める。
    - 預ける前に、配送の報告で、入力モード以外のキーの到達を確かめる。
    - 欠けがあったときの規則を 1 つに決める（例: §3.4 でセルをやり直す。またはブロックの印で合わせ直し、そのブロックの試行を除いて件数を報告する）。
    - open set にも同じ規則を当て、それで E2 の n（2,925 / 2,700）と通る確率の表がどう変わるかを書く。
  - 自信: 中

- **[severity: major] 問 3 の主の値は、この設計の思考時間の分布で決まる量になる。§6.4 の理由が §7 と矛盾し、比較の書き方も実装と合わない**
  - 位置と引用:
    - §6.4 l.503-504「Question 3 is answered under `all_trials` (primary), because the aggregates a researcher computes include the long sessions」
    - §7 l.721-722「how often a session is cut off depends on the design (think time, speed, S6, S13), so the fraction of long trials is a property of this design, not of natural typing.」
    - §3.1 l.216「423 of the 1,050 slow trials」
    - §6.4 l.508-509「Each scope is computed for three comparisons, with the same matching and the same measures」に対し、`kit\analysis\pipeline.py`:47-48 は「level 2 for gt_obs under all_trials and under_limit」
  - なぜ問題か:
    - ライブ変換ありの slow では、約 40% の試行のセッションが仕様どおり行を持たない。だから主の値（変換の数、平均の変換時間、変換に費やす時間の割合の偏り）は、ほぼ 0.2〜20 s の対数一様という設計の選択で決まる。読者はそれを「観測器の集計の偏り」として引用してしまう。
    - 速さの混合（§6.7）も、速さと打ち切りの率（slow 40%・mid 15%・fast 9%）を交絡させる。
    - §7 の最後の項目は問 1・問 2 の含意しか書かず、問 3 の主の値への含意を書いていない。
    - 接地: Conijn「caution should be taken when generalizing…」
    - （major-4 の (iii) の再掲ではない。新しく足した文同士の矛盾と、文と実装の食い違いを指している。）
  - 解消の条件: 次のどちらかと、比較の文の直し。
    - (a) 問 3 の主を `under_limit` にする。打ち切りの分は「20 s 以上のセッションは必ず行を持たず、その後の打鍵は断片の行になる」という決定的な規則として示し、読者が自分のセッションの長さの分布に当てられるようにする。
    - (b) `all_trials` を主のまま残すなら、その値は「この思考時間の分布の下での値」と明記する。そのうえで L2 を `gt_pred` でも計算する（パイプラインはすでに `gt_pred` の照合を作っている）。こうすると、仕様が生む偏りが `gt_obs` の隣に並ぶ。
    - どちらの場合も、§6.4 に、問 3 がどの比較で計算されるかを書く。
  - 自信: 中

- **[severity: minor] 推奨の文は「ログ」の公開の粒度と書いているが、セッションの行を出さないときにしか成り立たない**
  - 位置と引用: §6.8 l.632-633「The recommended granularity for publishing logs is the most detailed feature sets that are near chance」。同 l.588-589「the session rows are outside the scope of the recommendation below」。
  - なぜ問題か:
    - セッションの行は `t` と `dwell_ms` を ms で持つ。`t − dwell_ms` は最初の英字の打鍵にほぼ等しく、`t` は閉じるキーに近い（収集の遅れは 100 ms 以下）。だから行を一緒に出すと、`bin1s` や `no_time` の key 行でも、セッションごとに 2 点の ms の時刻が戻る。
    - 人の記録では、`dwell_ms` は英字の数 × 打鍵間隔 + 思考時間に近い。だから `counts_only` や `bin1s_count` で消した読みの長さも、`dwell_ms` から戻る。
    - `kit\e2\README.md`:224-226 自身も「The gain of using `dwell_ms` separately was not measured.」と書いている。接地: Monaco C4。
  - 解消の条件: 推奨を「セッションの行を公開しない場合の、key 行の粒度」と書く。そのうえで「セッションの行を公開する形は評価しておらず、key 行を粗くした効果を打ち消しうる」と明記する。
  - 自信: 高

- **[severity: minor] ブロック内の依存についての論理が逆向きで、通る確率の表も前提を書いていない**
  - 位置と引用: §6.8 l.635-637「The Wilson interval treats trials as independent although trials of one block share context; judging by the upper end allows for part of this, and the remainder is stated as a limitation.」
  - なぜ問題か:
    - ブロック内に依存があると、本当の区間は広くなる。すると Wilson の上端は低すぎ、near chance と判定されやすくなる。安全側の規則としては、甘くなる方向である。
    - 表（l.621-628）は独立な 1 つの推定を前提にしている。だが `acc` は、自分と、そこから導ける最大 4 つの集合の最大値である。
    - 「limitation として書く」とあるが、§7 にその項目は無い。
  - 解消の条件: 次の 3 つ。
    - 上端を、`stats.py` のブロックのブートストラップで出す（open set ではすでに使っている）。または推定した設計効果で区間を広げる。
    - 表の前提（独立・最大値でない）と、ずれの向きを書く。
    - §7 に項目を足す。
  - 自信: 中

- **[severity: minor] 試行ごとの差を使った重み付けし直しが、繰り越しのために成り立たない**
  - 位置と引用: §6.7 l.579-581「So that a reader can weight the scenarios differently, three per-trial differences (observation minus ground truth) are also reported per scenario and speed」。§6.4 l.525-526「A carried-out session contaminates the next trial whatever its scenario」。§3.1 l.217「113 trials start no session of their own (they follow an S6 trial)」。
  - なぜ問題か:
    - `l2.py` は観測の行を、重なりが最大の試行に割り当てる（`attach_trials`）。だから S6 から繰り越した行は、次の試行（シナリオは任意）の差に入る。
    - その結果、あるシナリオの差には、この設計での S6 の率で決まる汚染が含まれる。読者が自分の混合で重み付けし直しても、この汚染は残る。
  - 解消の条件: 試行ごとの差を、予測の層「3 つのどれでもない」（および `under_limit`）に限って出し、重み付けし直しが成り立つのはその層だけと明記する。汚染された層の差は別に出す。
  - 自信: 中

- **[severity: minor] n の根拠が、主の範囲に合わせて書き直されていない**
  - 位置と引用: §3.3 l.264-265「With 75 trials a stratum's recall near 0.95 is located to within about 5 points」。同じ節の表は、主の範囲で S1・S2・S4・S7・S8 の slow が 34〜44（約 ±8〜9 点）、S6 の slow が 3 / 5 と示している。
  - なぜ問題か: 問 1・問 2 の主の推定は `under_limit` で行う。だから「75 試行で ±5 点」という精度の目標は、slow の層の約 3 分の 1 で満たされない。この不足を受け入れるのかが書かれていない（J6・J7）。表の 34 の行を「S1 の最小」とした理由も無く、もっと小さい層がある。
  - 解消の条件: 主の範囲で実際に得る層ごとの精度を、n の根拠として書く。そのうえで、次のどれを選ぶかを明記する: 受け入れる / slow の n を増やす / S13 以外の思考時間の幅を狭める。
  - 自信: 高

- **[severity: minor] open set の結果が、推奨とどう関わるか決まっていない**
  - 位置と引用: §6.8 l.639-641「The attacker sees only the categories of the key presses … searches for the kana string that the romanisation would spell with exactly the observed letter keys」。推奨は closed set だけで決める（l.631-635）。
  - なぜ問題か:
    - open set の攻撃が使う情報は、`no_time` が残す英字の連続の長さそのものである（`open_set.py`:11-15）。`--length-info count` は、連続の長さを消した場合に当たる。
    - だから closed set で `no_time` が near chance になり、open set で `gain_vs_shuffled` が正になると、読者は 2 つの食い違う結論を受け取る。
  - 解消の条件: 次のどちらかを事前に決める。推奨の表に、同じ情報の下での open set の `gain_vs_shuffled` を並べる。または、K1 で下端が 0 を超える集合は推奨しないなどの規則を置く。
  - 自信: 中

- **[severity: minor] 「連続量にはすべて区間を付ける」という文に、例外が書かれていない**
  - 位置と引用: §1.2 l.37-38「Every proportion and every continuous estimate is reported with an interval」
  - なぜ問題か: 次の量には区間が付かない。
    - 速さの混合ごとの偏り（§6.7 l.574-576。`l2.py` の `mixture_bias` は点だけを返す）
    - 問 5 の要約値（§6.10）
    - 配送の数値（§6.3）
    - 時計の差（§6.9）

    特に混合ごとの偏りは「混合で動くか」を見るためのもので、区間が無いと読み過ぎを招く（J5）。
  - 解消の条件: 例外を一覧にするか、混合ごとの偏りにブロックのブートストラップの区間を付ける。
  - 自信: 高

- **[severity: nit] 試行の外の行の上限が、観測のログには甘すぎる**
  - 位置と引用: `C:\GSE-prototype\papers\ime-observation\experiment\data.md`:42「four marker presses and one kana press per block」
  - なぜ問題か: 観測器は入力モードのキー（かな）を記録しない（§6.3）。だから観測のログの上限は 1 ブロック 4 行のはずで、5 行を許すと、説明のつかない行が 1 ブロックに 1 つずつ（1 run で最大 126 行）検査を通る。
  - 解消の条件: 上限をログごとに分けて書く。
  - 自信: 中

- **[severity: nit] near chance の判定が、速さを混ぜたプールの正解率だけで行われる**
  - 位置と引用: §6.8 l.605-606「Reported: the accuracy with its Wilson interval, … and the accuracy per scenario.」（速さごとの正解率が無い）
  - なぜ問題か: 漏れる量は、人と打鍵の速さで変わる（Monaco C5）。§6.1 自身も、プールの値は自然な入力を代表しないと書いている。
  - 解消の条件: 速さごとの正解率を記述として報告する。あるいは、判定をプールの値で行う理由を 1 文書く。
  - 自信: 中

- **[severity: nit] 冗長さ**
  - 位置と引用: 打ち切りの理由が §1.1 から §7 まで約 10 か所で繰り返される（例: §7 l.720-722 と §6.4 l.491-505）。
  - なぜ問題か: 実務の読者が「何に使えるか」を探すとき、同じ説明を何度も読まされる。
  - 解消の条件: 打ち切り・配送・合成の間隔の説明を、それぞれ 1 か所に置いて参照にする。§1.2 に「読者が持ち帰るもの」（主の量 3〜4 個と公開の推奨の条件）を 5 行で置く。
  - 自信: 中

---

## 5. 総合の推奨: **major**（直して再査読。ただし再査読の範囲は §6.2・§6.4・§6.7・§6.8 と、パイロットの生ログの預けの文に絞れる）

1. round 1 の 16 件のうち、解消 10、部分的に解消 4（major-1・3・4・5）、未解消 2（minor-5・7。minor-7 は事前登録の文が落ちた後退を含む）。固定の十分さは大きく進んだ。
2. この研究で唯一の判定である E2 の公開の推奨に、直しで新しい穴が入った。1 秒のビンの推奨は自分の理由と矛盾し、打鍵 1 つの欠けで推奨が消え、依存の論理が逆向きで、「ログ」の推奨がセッションの行の扱いを越えて書かれている。
3. 問 3 の主の値は、この設計の思考時間の分布で決まる量になる。読者の重み付けし直しも、繰り越しで成り立たない。どれも、凍結の前に文と規則で直せる。

---

## 6. 読めなかった範囲と、注入の疑い

**読んでいない（一覧にあるが開いていない）ファイル:**
- `plan_config.macos.json`・`gt_rules.json`・`SEED`・`run.sh`・`notes.md`・`env.md`
- `kit\gen\README.md`・`recipes.json`・`recipes.macos-live-off.json`・`kit\emit\keymap_macos.json`
- `kit\e3\README.md`・`kit\run\README.md`・`kit\pilot\README.md`・`kit\logger\README.md`・`kit\refinput-macos\README.md`・`kit\emit\README.md`
- コード: `gt_sessions.py`・`match.py`・`l1.py`・`stats.py`・`spec_predict.py`・`generate_plan.py`・`run_cell.py`・`clock_sync.py`・`seal_obs.py`・`ime_compose.rs`・`driver_macos.rs`・`keymap.rs`

**一部だけ読んだもの:**
- `pipeline.py`: l.38-57 と grep だけ
- `delivery.py`: grep だけ
- `closed_set.py`: grep だけ
- `open_set.py`: l.1-75 と grep だけ
- `l2.py`: l.896-1348（selftest）を読んでいない
- `pilot-macos.md`: l.166-184 と grep だけ
- Conijn: l.872 以降（参考文献）を読んでいない
- Monaco: l.860-1120（攻撃の各節の後半）と l.1360 以降（参考文献・付録）を読んでいない

このため、§4.5 の予測の規則が観測器のソースと一致するか（selftest の主張）、キーマップ、実行器の時計の検査は確かめていません。

**注入の疑い:** なし。読んだ範囲に、査読者や LLM に向けた指示はありませんでした。
