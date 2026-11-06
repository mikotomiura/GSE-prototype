# verdict（manuscript round 1・対象 草稿 v1 commit 18fd94f0）

## 1. 判定: major revision（E が「直してから回す」・R1・R2・R3 も major）

有効な査読 4 本（R1・R2・R3・E。接地はどれも 2 本以上〔E は一次＋1 本〕から逐語で抜き出せた）。Codex major（既知の未決 16 件を添えた・16 件は round 5 の逐語が tmp と一緒に消えていたので、外枠 v6 の限界と保留の論点から組み直した＝逸脱）。初回の manuscript round。

## 2. 一致した指摘（分母 = 有効な査読 4 本。Codex は別枠）

| # | 指摘 | 一致 | Codex | 裏取り |
|---|---|---|---|---|
| A | 推定器・replay・推定の行・コードの公開が未決で、取り置きの値を外から再現できない（係数の数値も本文と補足に無い） | R1・R2・R3・E（4/4） | 既知の未決 7 と重なる | 真（abstract の置き字・discussion Materials・limitations） |
| B | 推定器に陽性対照が無く、同等が計器の弱まりと区別できないのに、題名 "did not anticipate" と結論が否定を推定器の性質として言う | R1・R2・R3・E（4/4） | 既知の未決 4 と重なる | 真（limitations・discussion (c)・data の 53.7%） |
| C | 但し書きの繰り返しと要旨の重さ（較正の括弧 6 か所・床 5 か所・帯 4 か所） | R1・R2・R3・E（4/4） | 1 項目（d） | 真（ngram の 76 件と同じ並び）。ただし抄録と序論の第 1 文の括弧は P0 の約束 |
| D | 題名・貢献の文の言い方が推定量より強い（"did not distinguish" は 3/4 が 0.5 を外す〔Lakens の Scenario C〕・"did not anticipate"） | R1・R3・E（3/4） | — | 真（results の表の脚注・discussion「three combinations were statistically different」） |
| E | JEDM の「単なる適用を超える」要素（比べの分析・手順の検出力の実例）が弱い。学習器と推定器の信号を比べていない | R1・R2・E（3/4） | — | 真（results「We did not compare the learners with the estimator's signals.」） |
| F | 結論の「秒単位の契機の根拠が無い」は検定した u の時点を超える（休止の後の情報・発火の規則は別） | R2（1/4）＋R1 の minor（基準率） | 3 と一致 | 真（conclusion・abstract・discussion の 2 段目） |
| G | 「揃えた」ものの説明の食い違い（序論・限界の block は誤り）と、統計量がセルの中の全組を数える（約 156 組/停滞）ことが書かれていない | R1・R2（2/4）＋監査 2-3・3-1 | 1 と一致 | 真（design は課題をまたぎ block は 60 s の除外だけ・外枠の「区切り」を block と訳した私の誤り） |
| H | 較正（実効 97/312）は取り置き（50.5/139）より重みが散らばった集団で行った。500 回の引きの実効の書き手の分布を示す | R2・R3（2/4） | — | 真（補足 S6 の文）。分布は計算していない |
| I | 打鍵から情動・苦闘を検出する系統の先行（Bixler・D'Mello・Epp など）が無い | R1・R2（2/4） | — | 真（references.bib に 0 件）。具体の文献は未照合 |
| J | 生成 AI の申告の "in all sections" と未確定の注記 | R1・R2・R3・E（4/4・nit） | — | 真 |
| K | 見た書き手の人数（319・312・316・341）の内訳が無い | R2・R3（2/4・nit） | — | 真 |

1 人だけの指摘（裏取り）:
- R1 [major] 停滞の平叙の定義「no character input for 30 s or more」が操作的定義と合わない（条件 A が立ってからさらに θ のあいだ正味の産出が無いことが要り、実効の最短はおよそ 30 s + θ）。→ 真（定義から: 事前登録 A1「It is an onset only when condition A stays true from s to t0」。休止の中の文字の入力は窓に +1 を入れ条件 A を偽に戻すので、削除の無い休止では G(u) ≥ t0 − u）。design「θ only fixes when a stall starts」も誤り。実効の長さの分布は数えていない。
- R1 [major] 構成概念と序論の動機（助けが要る瞬間）の結びつき・停滞の 47% は休止の中に出来事 → 真（data の値）。
- R1 [minor] CS1 2021 年版の有効な書き手 13.35 を報告していない → 真（explore_cs1_2021.json）。
- R1 [minor] 契機としての無用さは基準率から、同等は順位から、と分ける → 設計の判断（採否は研究者）。
- R2 [major] 要旨と序論が漏れの後の確認であることを伝えない（P10 "not written as a test of a prediction that could fail"）→ 真（限界の 1 文だけ）。
- R2 [minor] 閾値の表の 2 値 → 真（5.3→5.2・中央値の対照 4.6→4.5）。私の転記の誤り。
- R2 [minor] "the rise in an unmatched comparison was not replicated" の rise が何を指すか → 真（登録の定型の言い方。何の比べかを足す）。
- R2 [minor] 学習器の書き方が控えめ → 設計の判断（P0 は学習器を記述にとどめる）。
- R3 [major] 帯の "conservatively" は向きが逆（広い帯は同等と言いやすい） → 真（事前登録 P2 の語を写した。論文では「広め」と書く）。
- R3 [minor] "the same procedure applied without change" は CoAuthor（つなぎ直し・AI の出来事の除外・X6 で付録 F の文言から外れた）と KLiCKe（層なし）について言い過ぎ → 真。
- R3 [minor] 取り置きが前の分析の前に引かれた裏付け → 真（本文に無い）。事実は前の CS1 の俯瞰（条件 f888305b・D4）が一覧を読み飛ばし「集計の入力に一覧の書き手が 1 人も無いことを確かめる」と定めていた。S1 に 1 文。
- R3 [minor] 学習器の再標本で重複した書き手の分け方 → 真（本文に無い）。事前登録 P8 "Copies are grouped by the original writer into the same split, and pairs are built within copies." を S5 に写す。Codex 4 と一致。
- R3 [minor] 要旨の学習器の文に「比べていない」が無い → 真（監査 1-2 と一致）。
- R3 [minor] 種の幅の値がどの走りか → 真（S3 に 1 句）。
- E [minor] 細部を補足へ（表 1・較正の細部・学習器の門の経緯と感度・脚注の 0.025・考察の向きの小節・図 1 の 11 行）／考察の締め・結果の最初の段落 → 設計の判断（「移す」で解消）。

監査だけ（どれも真）: 1-1 抄録の含意の文にコードを渡すことが無い／1-3 序論の期待の根拠に付録 D の換算が無い（判断 32 (2)）／1-4 P11 の約束（start.json と結果の OSF の時刻をローカルのコミットと並べる）が S1 で半分／2-1 序論に床の文（外枠の置き場の規則に反する。ただし R の「重複」とも一致）／2-2 "the only dataset for which an unopened holdout existed" は誤り（CoAuthor の 18 人・CS1 2021 年版の 13 人も開けていない。外枠は「事前登録した取り置きが CS1 にだけある」）／2-4 5.1 の水準と差の対比の文／3-2 "opened once"・"run on the holdout once" と S1 の 2 回の計算の開始／3-3 requirement.md の呼び方が判断 33 の前／3-4 序論の作文の値の参照先が sec:res-explore（正しくは sec:res-main）／3-5 補足の表の Δx 上限 0.504→0.503（JSON 0.503495）・表 1 の Other「0.1%」は「0.1% 未満」に近い値（0.11% を数え直す）。

Codex だけ: 2 [major] 観測の端（課題の末尾・30 分の区切り・replay の削り）での打ち切りの扱いと除外の件数 → 真（本文に無い。長い停滞ほど除かれうる）／5 [minor] 新規性の調べの監査可能性（索引・検索日・検索式・選定の基準・判定の主体） → 真（S9 に足す）。

## 3. 直す順

- major（研究者の判断が要る）:
  - B 推定器の陽性対照: 案 (i) 見た書き手で、停滞の側の打鍵の時間・訂正を既知の量だけずらして推定器に通し、2 信号の AUC が帯を越えて動くかを見る（条件を先にコミット・[探索]）。案 (ii) 題名・抄録・結論を「この入力の上で、u の時点の 30 秒の変化は」に限り、計器の弱まりを主な解釈の候補として序論から書く。
  - A 公開: 推定器・replay・変換・推定の行（投稿の条件・判断 31 の未決）。
  - E 比べの要素: 学習器と推定器の信号を同じ組・同じ統計量で並べる記述を足すか、手順の部品の位置づけを弱めるか。
- major（文の直し）: D 題名と貢献の文を「帯の内にあった」の型・要旨に下向きの 1 句／F 結論・要旨・考察を「u までの 30 秒の変化」に限る／R1 停滞の平叙の定義を操作的定義に合わせ、design の θ の文を直し、実効の長さの分布（u から onset・u から再開）を数える（条件を先にコミット）／G block を削り全組を数える定義と重みの帰結を design に／R2 漏れの後の確認を要旨と序論に 1 句／C 但し書きを限界にまとめ、抄録と序論は P0 の第 1 文の括弧と床の第 2 文（抄録だけ）に絞る（序論の床の文を外す）。
- minor: 監査 2-2（確認の柱の理由）・3-2（完走 1 回）・3-4（参照）・1-1・1-2・1-3・1-4／R3 conservatively・without change・取り置きの裏付け・fold の分け方・種の幅／R1 2021 年版の有効な書き手・構成概念の段・基準率の分け方／R2 閾値の 2 値・rise の中身・漏れ／H 較正の実効の書き手の分布（計算）／I 情動の検出の先行（文献のラウンド）／Codex 2 観測の端・5 新規性の調べ／E 細部を補足へ・結果の最初の段落・考察の締め／5.1 の水準と差の対比を外す。
- nit: J 申告・K 人数の内訳・3-5 の数値・requirement.md。

## 4. 意図の監査役
- 意図にあって対象物に無い: 1-1〜1-4。
- 漂流: 2-1（序論の床）・2-2（確認の柱の理由が事実と違う）・2-3（block）・2-4（水準と差の対比）。2-2 と 2-3 は外枠から英語へ移すときの私の誤り。
- 4b. 編集者 E: 直してから回す（一般化の要素・推定器の陽性対照・公開・但し書きの重複・抄録の結論）。→ 判定は major 以上。
- 4c. 本文の分量: 6,262 語（texcount -inc -sum -merge・8 節）。前回なし（初回の manuscript）。測った版 18fd94f0。

## 5. 逸脱・注入
- 応答 5 本と Codex は secrets-filter を通り、絶対パスは含まない。応答はメインが縮めて tmp に置いた（外枠の round と同じ）。依頼文はファイルの絶対パスで渡した。
- Codex に添えた既知の未決 16 件は round 5 の逐語ではなく組み直したもの（round 5 の tmp を消していたため）。
- 接地の引用の照合は下の 6 に書く。
- 注入の疑い: なし。

## 6. 接地の引用の照合（査読者ごとに 1 件以上）
（メインが tmp/sources/ を grep して記入する）
- 本文で空白を詰めて逐語の一致を確かめた: R1 roeser2025「operationalised within the statistical models」・guo2020「relatively simple heuristics」／R2 gardner2018「number of data points should be separable」・pelanek2015「lead to interpretable and actionable results」／R3 lakens2017「statistically different from zero and statistically equivalent」・kapoor2023「Computational reproducibility of a finding refers to sharing the complete code」（「constitutes leakage」は 2 段組みの行の混ざりで断片「Nonindependence between train and test samples constitutes」まで一致）／E mensh2017「Focus on a single message」・jedm_about「extend beyond mere application」。捏造は見つからなかった。

## 7. 研究者に問うこと
- B 推定器の陽性対照（案 i 計算を足す / 案 ii 主張を入力に限る）。
- A 公開の場所（投稿の条件）。
- E 比べの要素（学習器と推定器の信号を同じ組で並べる記述を足すか）。
- 上の直す一覧の承認。次の round を回すか（初回の manuscript で major。Step 5 の基準では直して次の round）。
