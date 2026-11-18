# 言い換えた後の点検（paper-write Step 3b・manuscript round 4 の直し・判断 30・31）

対象: d6587f21 → round 4 の直しの版（この記録と同じコミット）で言い換えた・足した文の全部。照らした先は 3.3・3.4 の定義、補足（未作成の分は outline.md の「Moved to the supplement」と末尾の移した文の一覧）、実験の conditions と notes（20261112-selection-split-and-smoothing・20261113-null-from-shared）。観点は r3 と同じ: 地位＝分析の地位（計画 / 探索 / post hoc / not prespecified）の印、量＝著者が組んだ量と文献の指標の区別、定義＝自分たちの定義にだけ成り立つ性質を一般化していないか、規則＝判定の規則を点推定・日常語に崩していないか。

| 位置 | 言い換え・足した文（要旨） | 地位 | 量 | 定義 | 規則 | 結果 |
|---|---|---|---|---|---|---|
| 要旨 1 文目 | Whether a per-person model looks worthwhile depends on what it is compared with | — | — | 一般の問いとして書く | — | 可 |
| 要旨 2 文目 | coded per second over overlapping 30-second windows（26 symbols を外した） | exploratory を保持 | — | 重なる窓の範囲を保持 | — | 可（26 は序論 3 段に在る） |
| 要旨 4 文目 | 約 5e-4 が固定の平滑で among writers with 20 or more sessions・over two orders of magnitude below that gain | 計画 | — | 15-session に限った（監査役 1-3(b)）。that gain は 0.19（k = 5）で、同じ k の 5.5e-4 と比べて約 340 倍なので文は真 | — | 可 |
| 要旨 5 文目 | Two checks came after seeing results | 2 つの post hoc の括弧を 1 つにまとめた（判断 30 C） | — | — | — | 可 |
| 要旨 6 文目 | 合成の書き手が similar remainder relative to the improvement from removing the shared model's smoothing（not prespecified） | not prespecified を足した（監査役 2-1） | 比は著者の量 | 「平滑を外したときの改善」= 3.3 の smoothing effect の平易な言い換え。最頻値は基の平滑を外した共通の数え | — | 可 |
| 要旨 7 文目 | smoothing chosen on other writers (the grid's lightest) を両側に → 3 to 7e-3 from five training sessions on | 「Two checks came after」の 2 つ目 | — | 他人で選んだ平滑と明記（監査役 2-9）・k ≥ 5 に限った（Y5。k = 1〜3 は 5.2e-4〜2.0e-3） | — | 可 |
| 要旨 末尾 | For overlapping-window symbols, studies ... | — | — | 範囲の語（判断 30 C）。逆転は入れない（判断 27） | — | 可 |
| 序論 3 段 | 0.01 nats は better model が平均で約 1% 多い確率を与える（尤度比）・約 1% 低い perplexity。図 1 を先に引く | — | 一般の換算（exp(0.01) ≈ 1.01・幾何平均） | — | — | 可（R2 の尤度比・Y7） |
| 序論 4 段 | 3e-3〜7e-3 from five training sessions on・smoothing chosen on other writers, the lightest in the grid | post hoc の印あり | — | Y5・監査役 2-9 | — | 可 |
| 序論 4 段 | 合成で similar remainder relative to what removing the shared model's smoothing improves | post hoc | — | smoothing effect の平易な言い換え | — | 可 |
| 序論 4 段 | the finding rests on one dataset, CoAuthor, and one symbolization | — | — | 未定義の the positive instance を外した（Y8） | — | 可 |
| 関連 | AR(1)-HMM → AR-HMM | — | — | 語の統一（Y2・item 1） | — | 可 |
| 図 1 題 | Each model, of whichever structure | — | — | 例を構造に限らない（R3 n3） | — | 可 |
| 3.3 Prior mode | 最頻値は基の平滑を外した共通の数え。その共通に対する中央値の優位を smoothing effect と呼ぶ | 候補でない・勧めないを保持 | 著者が名付けた量 | 141 の「normalized S̄ without the base smoothing」と一致。「その平滑だけの費用」は最頻値と共通の違いが基の平滑だけであることに拠る | — | 可 |
| 3.3 Choice | joint では報告する 本人 − own chain に楽観が同じく乗るが、0 で切れない | — | — | Codex 1。0 で切れるのは構造を固定した行（共通そのものが選ばれると差が 0）だけ | — | 可 |
| 3.4 | no meaningful-difference threshold（the detection threshold は別） | — | — | threshold の 2 義を分けた（監査役 3-3） | — | 可 |
| 3.6 | first null と命名・replicate = 1 つの種の合成のパネル・negative controls = g = 0 の replicate | 事前の規則を保持 | — | E N6 | — | 可 |
| 3.6 | 2 つ目の帰無の倍率は smoothing effect が 3 種とも正の中で 7.4e-4 に最も近い | post hoc | — | 旧文「prior mode beat the shared model ... that gain」と同じ内容を smoothing effect の語で | — | 可 |
| 4.2 | 重ならない窓は値を外し、向き（17/17 at k = 15）だけ・値は S13 | — | — | 「向きだけ読む」の規則と合わせた（監査役 2-6・R1 N6）。gain の語を外した | 規則を大きさに崩さない | 可 |
| 4.3 | Per-person minus own chain is +0.220 ...（gains を外した） | — | — | Y2 | — | 可 |
| 4.3 | per-person advantage does not survive（\arthree の τ = 0） | — | — | gain は 3-state HMM の定義に限る | — | 可 |
| 4.4 二分 | 格子の拡張と少数の負の組の文を S16 へ | — | — | — | — | 可（E N7・S16 に既に在る値と、格子の拡張の 1 文を outline 末尾に足した） |
| 4.4 両側 | a remainder at α = 0.03 returns・+5.2e-4（k = 1）と 3.4e-3〜6.7e-3（k ≥ 5）・12〜17 of 17 favour・その割合は証拠でない | post hoc | — | 4.4 と 4.5 の the remainder の取り違えを避けて α = 0.03 の値と限った（監査役 3-2） | 割合を証拠にしない断りを Table 2 と同じく（Y9） | 可 |
| 4.4 両側 | The remainder at the fixed smoothing thus vanishes only when the two sides are smoothed differently | post hoc | — | 旧「not explained by the shared model's smoothing alone」を弱めた（R3 m2）。この確かめが書き手のデータと当て直しの他の効きを分けないことを保持 | — | 可 |
| 4.4 両側 | 最大は不安定な k = 12・0.03 は格子の最下・より軽い平滑はより大きいかも・合成で確かめていない | post hoc | — | — | — | 可 |
| 4.4 最頻値 | smoothing effect が平滑への依存を直に示す・最頻値は共通に +7.4e-4・本人（最頻値に書き手のデータを足したもの）は τ = 10^6 で最頻値に中央値で負ける | 計画の確かめ | — | R1 N3 の含意（足すと負ける）を 1 句。確率 0 の 2 人の扱いは S9（outline 末尾に既に在る） | — | 可 |
| 表 3 題 | 二分で正のまま、両側の当て直しで戻る。α = 0.03 の値の地位は 4.4 を参照 | post hoc 列を保持 | — | 主語のねじれを直した（R2）。但し書きの繰り返しを節の参照に（Y4） | — | 可 |
| 4.5 見出し | relative to their smoothing effect | post hoc（本文） | — | smoothing gain → smoothing effect | — | 可 |
| 4.5 | 閾 1.8e-3（他の陰性対照 10 種で超えたのは 0） | post hoc | — | FA' = 0（notes 28〜33 行） | 規則の語のまま（Y6） | 照合はサブエージェント |
| 4.5 | 比: 合成 0.6〜1.0（閾は約 1.0）・実データ 0.55〜0.97（not prespecified） | not prespecified | 比は著者の量 | 閾 ÷ 帰無の smoothing effect = 1.82e-3 / 1.76e-3 ≈ 1.03 | 判定を比の尺度でも示した（R3 m3）。比の規則を新たに作らない（閾は事前の規則のまま） | 照合はサブエージェント |
| 4.5 | arises → can arise | post hoc | — | 監査役 2-7 | — | 可 |
| 4.5 | 植えた差の書き手も大半が τ = 10^6（873・783 of 935）・3e-2 の最も低い種が k = 5 で −9.8e-4・強い縮みの下では植えた差が残りを上げるとは限らない・比は差のある場合で見ていない | not prespecified | — | 判断 30 B。notes 55〜56 行の「植えた差の行の混ぜが帰無の平滑の効きを打ち消す向きに働くことがある」を、機序を断定せず「上げるとは限らない」に留めた | — | 照合はサブエージェント |
| 考察 1 段 | 発見を冒頭に（弱い比べ 0.19 対 強い比べ 5e-4・k = 5 と 15 で 2 桁以上）・What is new を Relation から移した | — | — | 「2 桁」に k を添えた（R3 m1）。重なる窓に限った | — | 可（判断 30 A・E N10） |
| 考察 2 段 | 決定は固定の平滑での出力（15-session で 0.06〜3%・CS1 は共通そのもの）。推奨 (2) の版では全員に格子の中の τ・残り 3.4e-3〜6.7e-3（post hoc・15-session だけ） | post hoc の印あり | — | 判断 30 A | — | 可 |
| 考察 2 段 | 共通に替えて失うのは固定の平滑で約 5e-4、軽い平滑で最大約 7e-3（合成で確かめていない） | — | — | 「費用を省ける」を外した（Codex 3・Y1） | — | 可 |
| 考察 2 段 | 3e-2 までは 15-session で 2 つ目の帰無の下で確実に検出されない・閾が高すぎるかもしれない | post hoc | — | CS1 から切った（監査役 2-3）・閾の行き過ぎを 1 句（監査役 1-2） | 規則の語のまま | 可 |
| 考察 Relation | 重ならない窓は向き（every writer at k = 15）・may keep an advantage | — | — | gain の語を外した | 規則を大きさに崩さない | 可 |
| 考察 established | choosing and reporting on different writers が変えなかった・楽観が出る余地は小さい | — | — | 「does not come from」を弱めた（R2・監査役 2-4） | — | 可 |
| 考察 established | 平滑の確かめは here, 両側に当てたときだけ読みを変えた・両側は (post hoc) | post hoc の位置を両側の版に（R1 N4） | — | only の一般化を here に限った（監査役 2-5） | — | 可 |
| 推奨 | two practices changed the reading here・(2) に post hoc・1 構造 1 パネル・倍率は格子の端 | post hoc | — | Y3 | — | 可 |
| 推奨 | 最頻値を勧めない文を削った（3.3 に 1 回） | — | — | Y4 | — | 可 |
| 限界 | smoothing effect の語・帰無は 1 つのモデルから生む（植えた遷移の他に記録の形や話題の差がない）・drift の向きはその形による | post hoc | — | R1 N9・Codex 4 | — | 可 |
| 限界 | 構造の補償と合成の確かめの規則の文・連鎖の選び直しに対する縮約の行・30-session は 9 人・開始点の項目を外した | — | — | 3.4・3.6・表 1 に在る / outline 末尾へ（E N7・Y4） | — | 可 |
| 結論 | 弱い構造の共通に対する gain（0.19）は多くを語らない・強い比べで約 5e-4・合成で同程度（smoothing effect に対して）・固定の平滑で 15-session は強く縮めた当てはめ、CS1 は共通そのもの・替えて失うのは約 5e-4、両側の平滑で最大約 7e-3（合成で確かめていない）・3e-2 まで検出されない（結果を見た後の帰無・閾は高すぎるかも）・重ならない窓では HMM3 が選ばれ共通に勝つ | post hoc の印（added after seeing results） | — | 15-session に限った（there） | 規則の語のまま | 可（判断 30 A） |
| 表 2・図 3 | 15-s. → 15-session・図 3 (b) の題を own chain に | — | — | Y7・item 4 | — | 可 |

使わなかった直し: E N5（図 1 に中心の仕組みを入れる）は、図の範囲を判断 27 の 4 で研究者が決めたので今回は変えない。題の「what remains of the gain」（監査役 3-5）は軽微として残した。R1 N7（要旨で格子の拡張に印を付ける）は 3.4 の規則（post hoc は最後の 2 つに付ける）と要旨冒頭の exploratory で覆うと読み、変えない。R1 N12（自己相関の値）は既知の未決 7 のまま。
