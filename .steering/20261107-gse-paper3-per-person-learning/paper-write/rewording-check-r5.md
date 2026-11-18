# 言い換えた後の点検（paper-write Step 3b・manuscript round 5 の直し・判断 32）

対象: cc30d57f → round 5 の直しの版（この記録と同じコミット）で言い換えた・足した文の全部。照らした先は 3.3・3.4 の定義、補足（未作成の分は outline.md の「Moved to the supplement」と末尾の移した文の一覧）、実験の notes と集計（20261112-selection-split-and-smoothing の sym_summary.json・sym_tables.md、20261113-null-from-shared）。観点は r4 と同じ: 地位＝分析の地位（計画 / 探索 / post hoc / not prespecified）の印、量＝著者が組んだ量と文献の指標の区別、定義＝自分たちの定義にだけ成り立つ性質を一般化していないか、規則＝判定の規則を点推定・日常語に崩していないか。

| 位置 | 言い換え・足した文（要旨） | 地位 | 量 | 定義 | 規則 | 結果 |
|---|---|---|---|---|---|---|
| 要旨 4 文目 | over two orders of magnitude below that gain at five and fifteen training sessions | 計画 | — | k を限った（R1 m2・R3 m1）。0.188/5.5e-4・0.165/4.1e-4 で 2 桁以上 | — | 可 |
| 要旨 5 文目 | The candidate grids were extended, and two checks added, after seeing results | 結果を見た後の 4 つの変更を覆う（判断 32 C・Y2） | — | 3.4 の 4 つ（格子 2 つ・確かめ 2 つ）と一致 | — | 可 |
| 要旨 6 文目 | relative to the effect of the shared model's smoothing（not prespecified）・planted differences | not prespecified を保持 | 比は著者の量 | 「improvement」を中立の語に（監査役 2-2）。3e-2 は植えた差（監査役 2-4・R3 m-5） | — | 可 |
| 要旨 8 文目 | CS1 ... at the fixed smoothing | — | — | CS1 は両側の当て直しをしていない（R1 m3・監査役 3-6） | — | 可 |
| 要旨 末尾 | 「a null matching ... not achieved」の節を外した | — | — | 推奨 (3)(4) は本文に残る（判断 32 C） | — | 可。要旨 248 語 |
| 序論 2 段 | In sequence models the concern is sharper: 同じ構造の共通は自然な比べだが、構造が連続する記号の依存を運べないとき弱い | — | — | 領域に特有の空白の 1 文（E m4）。4.2 の「cannot carry the dependence」と同じ語 | — | 可 |
| 序論 3 段 | perplexity の平易な定義（the average number of equally likely next symbols the model leaves open） | — | 一般の定義 | exp(エントロピー)＝等確率の選択肢の数 | — | 可（E m2） |
| 序論 4 段 | 帰無に post hoc、比に a ratio not prespecified | 2 つの地位を分けた（監査役 3-4） | — | — | — | 可 |
| 関連 | idiographic (person-by-person)・DIC の展開・The DIC comparison is made within the data used for fitting | — | — | 70 行が交差検証の尤度まで一括していた（Codex 4） | — | 可 |
| 3.3 Choice 2 段 | 楽観の経路（標的の非 held-out 単位が他人の共通に入る）・共通が選ばれた書き手の差は 0・選ばれた本人の当てはめは標的で負けうる・joint の差には 0 を与える候補が無い | — | — | Codex 2。旧文の「cut off at zero from below」は書き手ごとには正しかったが、報告の差全体の下限と読めた | — | 可 |
| 3.3 Rows | main row を外し、shared chain を shared 1-state AR-HMM に | — | — | 1 概念 1 語（E m2） | — | 可 |
| 3.4 定義 | remainder に「対称の当て直しでは構造を 3-state AR-HMM に固定（その panel の joint choice が全セルで選ぶ構造）」 | — | — | 判断 32 D。Table 2 の joint choice は全セルで 3-state AR-HMM（235） | — | 可 |
| 3.6 | full protocol → joint choice・閾の確率の注を限界へ | 事前の規則を保持 | — | 1 概念 1 語 | 規則の語のまま | 可 |
| 4.2 | 大きさの文（does not fall by two orders of magnitude）を外し、記号が約 1/30 でパラメータの多い構造は推定しにくいので逆転はデータの量も映しうる・合成で確かめていない | — | — | 判断 32 B。向きだけ読む規則と合わせた | 規則を大きさに崩さない | 照合はサブエージェント（パラメータの数） |
| 4.3 見出し | at the fixed smoothing | — | — | 監査役 2-5 | — | 可 |
| 4.3 | per-person fit beats the shared model only under strong shrinkage（advantage を外した） | — | — | 1 概念 1 語（Y4） | — | 可 |
| 表 2 題 | per-person minus shared が gain 約 0.2 から remainder 1e-3 未満へ・割合の断りは 4.3 を参照 | — | — | gain と remainder の定義どおり（3-state HMM 固定の行と joint の行） | 割合を証拠にしない断りを 1 か所に（Y9） | 可 |
| 4.4 見出し | post hoc を両側の版に | post hoc | — | R3 n-2 | — | 可 |
| 4.4 二分 | most choices sit at the edge of a grid | — | — | 判断 31 の注意（k = 15 で 758/2,000 組が格子の中）。旧「nearly every writer's choice ... both grids」を弱めた | — | 可 |
| 4.4 両側 | τ は 10^2〜3×10^5（格子の中・固定の平滑のとき以下）・In the settings reported ... vanished only when ...・両側の版は構造も固定 | post hoc | — | 判断 32 D・E。τ の領域は sym_summary.json の chosen_tau_region（7 つの k で 17 人とも inside）と ml.py の定義（100〜300,000） | — | 照合はサブエージェント |
| 4.4 最頻値 | 確率 0 の 2 人の断りを S9 へ | — | — | outline 末尾に記録 | — | 可 |
| 4.5 | 873 of 935 at k = 5 と 783 of 935 at k = 15（植えた水準と陰性対照をまとめて）・CS1 の理由を S15 へ | not prespecified | — | R1 n1 | — | 照合はサブエージェント |
| 考察 1 段 | What is new を序論と同じ形に（自然な比べ＝同じ弱い構造の共通が示す gain は、他人で選んだ強い比べの remainder よりはるかに大きい） | — | — | 弱さの所在を構造に（E m5・監査役 2-6） | — | 可 |
| 考察 2 段 | 確かめた／確かめていないの段を決定の段の前へ。片側だけでは消え、両側では 6〜13 倍で戻った。どちらの平滑の残りも差を示すかは確かめていない。30-session は帰無でも両側でも確かめていない | post hoc の印あり | — | Y5（317 の論理）・R3 m-3 | — | 照合はサブエージェント（6〜13 倍・39%・区間） |
| 考察 3 段 | 決定は記号化に依る。植えた差の書き手も大半が同じ強い縮みなので選択だけでは要否を示さない。5e-4 は本人のデータの価値ではない（共通の平滑を軽くするだけで +1.6e-3・最頻値 +7.4e-4）。決定に関わる比べは両側の版（τ は 10^2〜3×10^5・重みは固定のとき以上・3.4e-3 / 5.2e-3） | post hoc の印あり | — | 判断 32 A・E・R2 m3・監査役 1-2・2-7（as recommendation (2) asks を外し「構造を固定して」と書いた） | — | 照合はサブエージェント |
| 考察 Relation | 先行の 3 文献を 1 文に・重ならない窓の向きはデータの量も映しうる・keep a gain | — | — | Y3 | 規則を大きさに崩さない | 可 |
| 限界 1 項 | 発見は CoAuthor、CS1 は境界の例 | — | — | 序論と合わせた（R2 nit） | — | 可 |
| 限界 帰無の項 | 記号を生成モデルから直に作り、窓と平滑を通していない・閾の確率の注・CS1 の 2 種と 5/17 は S15 へ | post hoc | — | Codex 1 | — | 可 |
| 限界 平滑の項 | 対称の当て直しの τ は「格子の中」としかまとめていない | — | — | 判断 32 E（書き手ごとの値は開かない） | — | 可 |
| 結論 | 5e-4 は共通の平滑を軽くするだけで得る量より小さいので本人のデータの価値ではない・両側で 3.4e-3〜5.2e-3（post hoc）・3e-2 は固定の平滑で・重なる窓に限る（重ならない窓は記号もはるかに少なく、HMM3 が選ばれ gain の向きを保つ）・記号化を比べと一緒に報告する | post hoc の印あり | — | 判断 32 A・B。up to 7e-3（不安定な k = 12）を外した（R2） | 規則の語のまま | 照合はサブエージェント |
| Code availability | 確かめの列挙を S12 へ | — | — | E m3 | — | 可 |

使わなかった直し: E N5（図 1 の範囲・判断 27 の 4 のまま）・題の「what remains of the gain」（判断 31）・R1 m4（自己相関の値・既知の未決 7）。中央値を本文に出す（判断 32 B で却下）。
