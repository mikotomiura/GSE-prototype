# 文献カード: 論文 2 の外枠の attack-me round 1 で一致した「最も近い先行が無い」への追いかけ

- **トピック**: stall-shape-paper2-round1-priors
- **日付**: 2026-11-07
- **作業記録**: `.steering/20261107-paper2-outline/`（判断 7・verdict の I）
- **用途**: 新しさの文と関連研究の柱を書き直す前の確かめ。gate 判定ではない。

## 検証状態

- 3 角度（A1 CS1 の打鍵・編集のログの休止と作業時間の閾値／A2 学習分析・EDM・教育測定で定義を振った研究／A3 作文の休止の閾値の恣意性への既存の答え）を Sonnet のサブエージェント 3 本で並列に探した。反証の角度（「既に同じことをした研究」）を各々に含めた。Semantic Scholar は 429、OpenAlex は後半に枠が戻った。
- メインが一次で照合したもの: 登録した 14 本の書誌（Crossref・Zenodo）と、各 1 つの逐語（抄録は Crossref か OpenAlex、[V476] と [V483] は本文の PDF を grep）。[V439]（Koutcheme ら 2026・論文 1 の作業で登録済み）は抄録を OpenAlex で、本文の 4 か所を ACM の頁で照合した。
- 登録しなかったもの（逐語を照合できない・格が低い）: Fancsali ら 2020 AIED（二次の複製でしか読めない）・Evans ら 2016・Khalil & Ebner 2014（定義を並べた研究か確かめられない）・Van Waes & Leijten 2015・Wengelin 2006・Guo ら 2018・Guo ら 2019・Barkaoui 2019・Alves ら 2008・Révész ら 2019（抄録まで・閾値を振る分析かは未確認）・Rosenqvist 2015（学士論文）。

## 要点を先に

| 角度 | 温度 | 一言 |
|---|---|---|
| A1 CS1 の打鍵の閾値 | 近い先行あり | 同じ公開データの系統で、休止の境界（750 ms・2 秒・15 秒）の置き方が試験得点との関連を左右することを示した複製の研究がある（[V439]）。作業時間の閾値は 5 分〜1 時間と乱立し問題視されている（[V476]）。どれも停滞のラベルの定義の空間を振ってデータの間の比べや同じ人の中の構造を見てはいない |
| A2 EDM・教育測定の multiverse | 近い先行あり | EDM で予測モデルの multiverse（[V482]）、wheel spinning の 2 つの定義で率が大きく違い一致が 5 割未満（[V483]）、PISA の尺度化の specification curve で国の平均の揺れが標本の誤差と同じほど（[V481]）。出来事の定義でデータの間の率の比べ・同じ人の中の過分散・時刻の一致を見たものは見つからない |
| A3 休止の閾値への答え | 近い先行あり（答えの系統は厚い） | 恣意性への答えは混合モデル（[V484]・[V485]・[V486]・[V487]）・個人化・状態モデル（[V488]）の 3 系統。[V488] は編集の切れ目の閾値を格子で振る感度の確かめをしている。閾値を並べて群の差や比べが動くことを示した研究は見つからない |

→ 新しさの文は「停滞のラベルの定義の空間（窓・θ・止まりの条件・区間の切り方）を 4 つの公開データで同じ検出器で振り、データの間の比べ・同じ人の中の過分散・時刻の一致が動き、長さの揺れの形が残ることを並べた研究は、探した範囲（本カードと前の 2 枚）で見つからなかった」に限る。命題（定義で結論が動く）は [V468]・[V472]・[V481]・[V482]・[V483]・[V439] で既出。関連研究の柱 2 は「恣意性への 3 つの答え（混合モデル・個人化・状態モデル）と、定義の幅を報告する道」に組み替える（R1 の指摘）。

---

### カード 1: CS1 の打鍵では、閾値の置き方で結論が変わることが既に指摘されている **[検証済・抄録]** [V439] [V475] [V476] [V477] [V478]

1. **どんなもの？** Koutcheme ら（[V439]）は公開の CS1 の打鍵データ 5 学期で、打鍵の速さ（流暢さ）と止まる頻度（ためらい）を試験得点に結びつけた複製の研究。Hart ら（[V475]・[V476]）と Edwards ら（[V477]）は無活動の時間から作業中の確率を出すモデル。Shrestha ら（[V478]）は休止の長さの帯ごとの頻度と成績。
2. **先行研究と比べてどこがすごい？** [V439] 抄録の逐語 *"Hesitation behaved differently: students who paused more often at chunk boundaries scored lower even after accounting for their typing speed and general pausing."*本文（2026-11-07 にメインが ACM の全文の頁を Chrome で開いて照合）の逐語: *"We keep 750 ms as the dividing line, although it was not chosen on cognitive grounds"*・*"A median restricted to 10–750 ms therefore ignores more than half of the E and H transitions of a typical student."*・*"Their 750 ms window removed the longer pauses."*・*"For H, the association is clearest for pauses of 2 to 15 s, which Shrestha et al. [26] relate to thinking about the code locally (r = −0.21, p =.001). The estimate for brief stops is weaker and not significant (r = −0.09, p =.396)."*。境界の置き方で関連の強さが変わることを示すが、向きの入れ替わりは示していない（どちらも負）。統制の前後: 本文の逐語 *"We therefore control for both A fluency and A hesitation. With these controls, students who pause more often at boundaries still score lower. The association is significant for E (r = −0.15 [ − 0.26, − 0.04], p =.043)."*（2026-11-07 にメインが照合）。2 秒で分けた感度の値はこの直後の "Sensitivity." の段落にあり、統制が掛かるかは明示されていない。[V476] 序論の逐語 *"For years, ad hoc thresholds were used, which ranged from five minutes to one hour"*。[V475] 抄録の逐語 *"a simple 5-minute threshold of inactivity is a reasonable estimate for whether a student is on-task or not"*。
3. **技術や手法の肝はどこ？** 閾値を自己申告で接地する（[V475]・[V477]）か、境界を変えた感度を並べる（[V439]）。
4. **どうやって有効だと検証した？** 交差検証の誤差・複数学期での相関。
5. **議論はあるか？** 論文 2 との違い: 見ているのは試験得点との関連や作業時間の推定で、停滞のラベルの定義の空間を振ってデータの間の比べや同じ人の中の構造を見てはいない。[V475] の 5 分は論文 2 の区間の切り方（押下の空白 5 分）の根拠に使える。
6. **次に読むべき論文は？** [V439] の本文の §5.2 以降（未読）。Leinonen らの 750 ms の原典（未特定）。

### カード 2: EDM と教育測定で、定義と分析の選択を振る研究は既にある **[検証済・抄録・本文]** [V479] [V480] [V481] [V482] [V483]

1. **どんなもの？** multiverse（[V479]）と specification curve（[V480]）の原典。教育測定では PISA の尺度化の選択を振った specification curve（[V481]）。EDM では学生の成功の予測モデルの multiverse（[V482]）と、wheel spinning の 2 つの定義の比べ（[V483]）。
2. **先行研究と比べてどこがすごい？** [V481] 抄録の逐語 *"model uncertainty had almost the same impact on variability in the country means as sampling errors due to the sampling of students"*。[V483] 本文の逐語 *"The agreement on wheel spinning is generally less than 50%."*。[V482] 抄録の逐語 *"we advocate for a multiverse approach in student success modeling"*。
3. **技術や手法の肝はどこ？** 擁護できる選択を掛け合わせて全部回し、結論の揺れを標本の揺れと並べる（[V481]）。
4. **どうやって有効だと検証した？** 国の平均の揺れの分解（[V481]）・予測の性能と公平性の揺れ（[V482]）・2 つの定義のラベルの率と一致（[V483]）。
5. **議論はあるか？** [V483] は論文 2 の C2（率が近くても時刻が違う）に最も近い型だが、定義は 2 つで、率そのものが大きく違う場合の一致を見ている。[V481] は「定義の揺れを標本の揺れと並べる」という R2・R3 の指摘の手本になる。
6. **次に読むべき論文は？** Fancsali ら 2020 AIED（wheel spinning の定義の未熟さ・一次で未照合）。

### カード 3: 休止の閾値の恣意性には 3 つの答えの系統がある **[検証済・抄録]** [V484] [V485] [V486] [V487] [V488]

1. **どんなもの？** 混合モデル（[V484]・[V485]・[V486]・[V487]）、閾値を使わない状態モデル（[V488]）。
2. **先行研究と比べてどこがすごい？** [V484] 抄録の逐語 *"mixture models fit pause duration data better than unimodal central tendency statistics"*。[V487] 抄録の逐語 *"Traditionally, arbitrary pause thresholds that are universally applied to all writers have been established to differentiate between cognitive and non-cognitive pauses."*。[V488] 抄録の逐語 *"yet much evidence is still analyzed through fixed pause cut-offs or isolated process measures"*。
3. **技術や手法の肝はどこ？** 閾値を 1 つに決める代わりに、分布の成分か状態で休止を分ける。[V486] では成分の数自体が書き手で 3 か 4 に分かれる。
4. **どうやって有効だと検証した？** 当てはまりの比べ（[V484]・[V486]）。
5. **議論はあるか？** 論文 2 は閾値を推定し直す答えではなく、閾値を 1 つに決めたときにどの結論が動くかを示す道で、3 つの答えを使う研究にも「答えの選び方で結論が動くか」を問える。[V488] は自分の操作の閾値を格子で振る感度を本文で報告しており、論文 2 の推奨の先例になる。
6. **次に読むべき論文は？** Van Waes & Leijten 2015 と Wengelin 2006 の本文（閾値を並べた分析の有無）。

## 否決リスト

1. 「停滞・休止の定義を振って結論が動くことを示した教育の研究は無い」0-3: [V439]（CS1 の打鍵の境界）・[V483]（wheel spinning の定義）・[V481]（尺度化）がある。

## 本ラウンドのやり残し

Fancsali ら 2020 の一次。Van Waes & Leijten 2015・Wengelin 2006・Barkaoui 2019 の本文。
- Semantic Scholar が使えず、セッション・gaming・engagement の定義を振る研究の網羅は弱い。
