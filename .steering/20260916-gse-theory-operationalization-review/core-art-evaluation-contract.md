# CORE-ART 評価契約 v0.1

> Status: pre-SSOT evaluation draft / 2026-09-17
>
> 本書は `CORE-ART` を反証可能にする作業契約であり、美的価値、好み、理解度を一つの総合点へ畳まない。artifact、採用尺度、codebook、数値 margin は未確定である。

## 1. 命題と理論的親

**命題**: 実践経路から表現を形成した生成作品が、画面外行為の意味づけと達成認定を意図的に終えることは、故障や未完成ではなく作品の終端形式になりうる。

- 理論的親: `TH-MTP`
- 下位理論: `SUB-PGP`、`SUB-SWM`
- 主担当命題: `GR-C3/C5`、`GR-H1/H2/H5/H6/H10`
- 副担当: `GR-C2/C4`、`GR-H3/H4` の作品上・知覚上の証拠
- `GR-H5` は gaming と作品条件を主要判定し、実装上の non-recapture は CORE-CS を参照する。

## 2. 含む範囲と含まない範囲

### 含む

- 同じ終点に至る異なる実践経路が形式差として残ること
- 表示が状態計、装飾、人格・能力・健康の診断でなく、セッション固有の実践肖像として読まれること
- invitation、開口、終端、failure が作品上でどう弁別されるか
- termination が欠損や故障でなく形式上の出来事として成立するか
- 任意の意味形成と義務的な解読・第二作業の分離
- gaming、自己量化的読解、cross-session linkability
- 本人の self-relatedness と outsider の linkability の分離

### 含まない

- 美しい、好ましい、抽象的、分かりやすいことだけで作品成立とすること
- 実装上の Semantic Stop を知覚評価だけで証明すること
- 画面外で歩いた、回復した、成功した、身体へ戻ったと認定すること
- `EH2` 本人試視を `EH3` 外部形成的評価として数えること
- ML 推定精度、介入効果、判断品質を作品成立の代用にすること
- Digital Nature 全体との整合を本契約だけで判定すること

## 3. 観測単位、対象、証拠階梯

| 項目 | 契約 |
|---|---|
| artifact 単位 | `mapping version x fixed replay trace x rendered artifact` |
| 知覚単位 | `participant x artifact pair/order x construct` |
| linkability 単位 | `observer or model x artifact pair x session identity` |
| 主対象 | 想定利用者。外部 observer は本人の self-relatedness と別標本または別 task で扱う |
| `EH0` | 作品定義、比較、反例、codebook の概念監査 |
| `EH1` | deterministic replay、path manipulation、Semantic Stop 実装証拠への参照 |
| `EH2` | 作者・開発者本人の feasibility と計器監査 |
| `EH3` | 外部形成的 think-aloud、認知インタビュー、反例収集 |
| `EH4` | randomized artifact comparison、forced choice、事前固定 codebook |
| `EH5` | 複数セッションでの gaming、linkability、自己量化的読解、持続性 |

## 4. 条件と対照

| ID | 条件 | 固定するもの | 分離する概念 |
|---|---|---|---|
| `ART-C0` | 状態 widget / 数値表示 | 同じ trace と終点 | 状態計 |
| `ART-C1` | 経路を使わない装飾的抽象表示 | palette、画面占有、運動量 | 装飾 vs portrait |
| `ART-C2` | 経路依存 Practice Portrait | trace、mapping version | path dependence / portraitness |
| `ART-C3` | Portrait + Immanent Aperture | portrait base | invitation / opening |
| `ART-C4` | Portrait + 見かけ上の終了 | end cue | expressed stop without semantic stop |
| `ART-C5` | Portrait + 監査可能な Semantic Stop | end cue と説明量 | termination-as-form + implementation reference |
| `ART-C6` | failure / timeout 表示 | trace と表示量 | intentional termination / failure |

### 経路操作

最低限、次の二組を固定 replay trace として作る。

1. **同じ終点・異なる経路**: 最終量、長さ、主要 summary を揃え、時間順序、revision、pause topology だけを変える。
2. **異なる終点・類似経路**: 経路形状を近づけ、最終量を変える。

これに endpoint-only rendering を加え、経路情報の追加価値と最終量依存を分離する。実データを用いる必要はなく、初期 artifact は合成 fixture を正とする。

## 5. 構成概念と観測可能量

| 構成概念 | 作業定義 | 非該当例 | 観測可能量 | 主要失敗 |
|---|---|---|---|---|
| path distinguishability | 終点を揃えても異なる経路が形式差として識別される | 色 seed の違いだけ | forced-choice accuracy、confidence、差異記述 code | endpoint-only と同等 |
| path dependence | artifact の重要な形式特性が経路操作で系統的に変わる | trace を使わない random animation | pre-registered visual feature change、ablation | 経路を除いても説明力不変 |
| portraitness | 装飾でなく、ある実践の時間的関係を示すものとして読まれる | wallpaper、meter、status icon | category choice、理由 code | decoration / widget が主要読解 |
| self-relatedness | 本人が人格でなく当該 session の実践との関係を認める | 「自分の性格そのもの」 | session-specific item、free description | essentialist self claim |
| session-specificity | 別 session / 別人へ無差別に当てはまらない | Barnum 的な一般文 | own-session matching、counterfactual matching | cross-session genericity |
| non-diagnosticity | 人格、能力、健康、真の内面の診断として主に読まれない | 「集中力が低い人」 | diagnostic / essentialist code rate | 診断読解が widget と同等以上 |
| termination-as-form | end cue が故障でなく、作品が何かを終える出来事として読まれる | spinner 消失、通信断 | termination / failure forced choice、理由 code | 説明を読んだ時だけ成立 |
| work completeness | 未完成・欠落でなく、一つの作品単位として終わったと読まれる | 画像 loading 失敗 | completeness item と open-ended rationale | completion と好みの混同 |
| invitation discrimination | invitation が命令、報酬、唯一の正解行動に見えない | dismissable command | invitation / command choice、obligation | 実質的命令として読まれる |
| interpretation burden | 任意解釈が義務的な解読や第二作業にならない | 正解意味を探させる puzzle | interpretation time、recheck、second-work item | task disruption / repeated checking |
| ambiguity dose | 対応規則の開示量と候補解釈幅 | 単なる低画質 | low / medium / high manipulation check | dose が成立しない |
| gaming | 望ましい表示を得るため入力を変える意図・行動 | 好奇心による一度の探索 | strategy choice、attempt rate、trace distortion | nonreward 条件でも悪化 |
| linkability | 複数 session artifact から同一人を結びつけられる程度 | 当該 session の本人性 | cross-session matching、attack AUC / accuracy | 事前上限超過 |
| self-quantification reading | 数値非表示でも成績、改善、序列として読むこと | 形態差の記述 | score / rank / improvement code | 主要読解が自己採点 |

各構成概念は別々に報告する。好み、美しさ、理解度、completeness、portraitness を合算しない。

## 6. 測定時点と観測窓

| 時点 | 測定 |
|---|---|
| artifact 前 | 作品・生成芸術・自己追跡への familiarity、可視化 literacy、privacy concern |
| first exposure | category choice、termination / failure choice。説明前に取る |
| controlled comparison 後 | path forced choice、portraitness、non-diagnosticity、burden |
| explanation 後 | 説明依存性、non-recapture / support の理解。説明前 outcome と分ける |
| block 後 | free description、second-work、surveillance、self-quantification |
| delayed / multi-session | linkability、gaming、意味の固定化、持続性 |

形成的 think-aloud は first-exposure outcome を変えるため、本試行 outcome と同じ trial で混ぜない。

## 7. 主要・副次評価と算出規則

### 7.1 主要 family

| family | 主要評価 | 副次評価 | 判定単位 |
|---|---|---|---|
| Path | 同終点・異経路 forced-choice と endpoint-only 増分 | confidence、自由記述 | `GR-H1` |
| Portrait | portrait / decoration / widget category と session-specificity | self-relatedness、completeness | RG-4 / `GR-H2` |
| Non-diagnostic | diagnostic / essentialist code rate | surveillance、authority | `GR-H2` |
| Termination | intentional termination / failure discrimination | work completeness、説明依存 | `GR-C4`, `GR-H3` の知覚証拠 |
| Burden | second-work formation、interpretation burden | time、recheck、task disruption | `GR-H10` |
| Gaming / privacy | gaming rate、cross-session linkability | self-quantification reading | `GR-H5/H6` |

多重性の扱い、最小差、非劣性幅は EH3 後かつ EH4 前に family ごとに固定する。作品成立を一つの omnibus score で判定しない。

### 7.2 定性評価

free description は最低限、次を複数選択可能な codebook で二重 coding する。

- `portrait-session`
- `portrait-personality`
- `status-meter`
- `diagnosis-health`
- `diagnosis-ability`
- `decoration`
- `invitation-open`
- `command-obligation`
- `intentional-ending`
- `failure-timeout`
- `reward-score-rank`
- `optional-interpretation`
- `required-decoding`
- `unclassifiable`

codebook は EH3 で反例を追加し、EH4 前に凍結する。二重 coding、一致度、adjudication、negative case を残す。理論に有利な発言だけを抜粋しない。

## 8. 操作確認

- `ART-C0` が実際に状態 / 数値表示として読まれる。
- `ART-C1` が path input を一切使わない。
- `ART-C2` の render が同じ trace と seed で決定論的に再現する。
- path manipulation が endpoint summary を変えていない。
- ambiguity low / medium / high が説明量、label specificity、候補解釈幅で分離する。
- `ART-C4` と `ART-C5` の visual ending を揃え、違いを裏側の停止有無だけにした比較を持つ。
- `ART-C6` の failure cue が実際に failure と知覚される。
- Semantic Stop の成立は CORE-CS EH1 の結果で確認し、参加者回答を代用しない。

## 9. 交絡、媒介、効果修飾

| 種類 | 候補 | 扱い |
|---|---|---|
| 交絡 | order、learning、trace salience、palette、motion、display size、説明量 | randomization、counterbalance、artifact matching |
| participant | art familiarity、visualization literacy、privacy concern、AI / self-tracking experience | 割付前測定。過剰調整しない |
| 媒介 | path noticing、termination perception、self-relatedness | 主要条件差で無条件調整しない |
| 効果修飾 | familiarity、need for closure、ambiguity tolerance、accessibility need | interaction と区間推定。標本不足は unresolved |

## 10. 欠測

| 欠測 | 規則 |
|---|---|
| artifact render failure | 技術欠測。failure 読解へ混ぜない |
| condition not noticed | 観測された知覚結果。自動除外しない |
| `unclassifiable` | 有効な outcome。誤答や portrait に再分類しない |
| free-text refusal | 選択的無応答。量的項目だけで定性成功を補完しない |
| accessibility failure | 技術 / 手続欠測を記録し、好みの低さにしない |
| no gaming opportunity | 構造的未定義。gaming=0 としない |
| no repeated session | linkability 未試験。privacy 成功としない |

## 11. 支持、縮小、棄却、未解決

| 判定 | 条件 |
|---|---|
| 支持候補 | Path、Portrait、Non-diagnostic、Termination、Burden の各 gate が成立し、CORE-CS の実装監査、および既存 EVAL-NCC v0.1 の `C3`・minimum support・non-abandonment・actual-harm rejection を通過する。この契約では `GR-H4/H9/H11/H12` を再定義しない |
| 縮小 | path / portrait は成立するが termination が成立しない場合は Practice Portrait 技法へ縮小。termination は成立するが既存 open work / interactive art との差分が残らない場合は GSE 固有技法へ縮小 |
| 棄却 | 最終量だけで同等、状態計・装飾・診断が主要読解、終端が failure と弁別不能、又は採用予定 dose で義務的解読・第二作業・gaming・linkability が許容幅を超える |
| 未解決 | artifact、codebook、尺度、dose、margin、標本が未固定、又は interval が支持・棄却の双方へ届かない |

`GR-H10` の dose-limit 判定と、採用する artifact / dose の適格性は分ける。high ambiguity が medium より second-work、recheck、abandonment anxiety を増やす場合は H10 の支持候補であり、high 条件を採用すべきことを意味しない。負担増がなく単調有益モデルが残る場合は H10 を棄却する。一方、実際に採用予定の dose で義務的解読・第二作業が許容幅を超える場合は、その artifact / dose を縮小又は棄却する。

## 12. 代替説明と最強の反例

| 代替説明 / 反例 | 契約上の応答 |
|---|---|
| 単なる美しい抽象表示 | `ART-C1` と portrait / decoration code を置く |
| endpoint の差を見ているだけ | 同終点・異経路と異終点・類似経路を交差させる |
| 説明を読んだから終端に見える | first exposure を説明前に測る |
| 状態ラベルを隠した status meter | diagnostic / meter / self-quantification code を分離する |
| 曖昧なので何でも当てはまる | session matching と counterfactual artifact を使う |
| 本人には関係するが他者にも追跡可能 | self-relatedness と outsider linkability を別々に測る |
| 非数値でも望ましい形を gaming する | explicit strategy と repeated-session behavior を測る |
| 終端表現は成立するが裏側は動く | CORE-CS の EH1 gate 不通過として Semantic Stop 主張を棄却する |
| 既存 open work / data portrait で十分 | 独立理論を主張せず GSE 固有の結合技法へ縮小する |

## 13. 主張禁止線

- 好み、美しさ、驚き、抽象性を portraitness や termination-as-form と同一視しない。
- 本人試視を外部形成的証拠にしない。
- 参加者が終端を理解したことを処理停止の証拠にしない。
- path classification の成功を本人性、作品性、非診断性の証拠にしない。
- 画面外の身体、歩行、回復、成功を artifact から認定しない。
- linkability を測らず session-local privacy を主張しない。
- `ART-C5` 未実装の段階で Semantic Stop を含む作品が成立したと主張しない。

## 14. 現在地と未解決

現在地は `EH0 / defined` である。Practice Portrait、Immanent Aperture、Semantic Stop を一体化した比較 artifact と外部形成的評価は未実施であり、現行の表現設計や本人メモを `EH3` として数えない。

未解決は次である。

1. deterministic replay artifact と endpoint-matched trace set。
2. portraitness / diagnostic reading / termination-as-form の認知インタビュー用項目。
3. 定性 codebook の反例と二重 coding 手順。
4. ambiguity dose と second-work の操作。
5. gaming opportunity と cross-session linkability attack model。
6. 既存 art-HCI 操作化を借りられる範囲と GSE への外挿限界。

## 15. 限定サーヴェイと引用射程

検索日: 2026-09-17。gpt-5.5 / xhigh の調査担当が ACM、DOI、Nature、Oxford、MIT Media Lab、artist / museum の一次公開元を検索し、主担当が DOI、公式抄録、研究設計、ローカル引用射程を再照合した。主な検索式は `generative art Boden Edmonds DOI`、`open work DOI`、`data portraits MIT`、`autographic visualization`、`ambiguity as a resource DOI`、`reflective design DOI`、`withdrawal termination as art`、`personal quantification DOI`、`path linkability DOI` である。

| 一次資料 | 研究設計 / 対象・N | 操作 / 評価量 | 借りる定義 | 借りない主張 / GSE 外挿限界 |
|---|---|---|---|---|
| Boden & Edmonds (2009), [doi:10.1080/14626260902867915](https://doi.org/10.1080/14626260902867915) | generative art の理論分類 / N/A | category と locus of creativity | 規則・自律系、形式生成の分類 | 終端、返権、portraitness は扱わない |
| Eco, “from *The Open Work* (1962),” 2021 reader chapter, [doi:10.7312/hayo18620-025](https://doi.org/10.7312/hayo18620-025) | 美学理論 / N/A | 作品構造と解釈の開放性 | 構造を持つ open interpretation | 曖昧なら burden が下がるとは言えない |
| Donath et al., [Data Portraits](https://www.media.mit.edu/publications/data-portraits/) | 作品 / 概念 / N/A | 蓄積データの portrait 化、privacy / control / aesthetics | 顔でなくデータから portrait を構成する系譜 | session-local / non-diagnostic を導かない |
| Offenhuber (2019), [arXiv:1907.05454](https://arxiv.org/abs/1907.05454) | visualization theory / N/A | 物質的 trace の生成・可視化・解釈 | trace、registration、data-generation circumstance の legibility | GSE は推論媒介なので autographic そのものとは呼ばない |
| Gaver, Beaver & Benford (2003), [doi:10.1145/642611.642653](https://doi.org/10.1145/642611.642653) | design theory / cases / N/A | information / context / relationship ambiguity | ambiguity を設計資源として分類する | 善性、最適 dose、低 burden を保証しない |
| Sengers et al. (2005), [doi:10.1145/1094562.1094569](https://doi.org/10.1145/1094562.1094569) | critical HCI / design principles / N/A | reflective design principles | 技術を最終権威にせず reflection の条件を問う | 省察が実際に起きた証拠にはならない |
| Höök (2009), [doi:10.1098/rstb.2009.0202](https://doi.org/10.1098/rstb.2009.0202) | affective-loop case synthesis / small cases | open surfaces、appropriation、reflection | 利用者側の意味形成 | GSE が emotion / body を読めるとは言えない |
| Etkin (2016), [doi:10.1093/jcr/ucv095](https://doi.org/10.1093/jcr/ucv095) | 6 experiments | measurement 有無、activity、enjoyment | measurement-reactivity / self-quantification の警告 | 数値禁止や non-recapture の効果を直接支持しない |
| Consolvo et al. (2008), UbiFit Garden, [doi:10.1145/1357054.1357335](https://doi.org/10.1145/1357054.1357335) | 3-week field trial、N=12 | garden wallpaper + activity sensing、activity / use response | glanceable ambient display の比較先 | goal、growth、測定を含むため非報酬・非回収の証拠にしない |
| de Montjoye et al. (2013), [doi:10.1038/srep01376](https://doi.org/10.1038/srep01376) | 1.5 million mobility users / 15 months | trace resolution と re-identification uniqueness | 粗い path にも linkability が残る attack-model | mobility の再識別率を GSE portrait へ移植しない |
| Cage, [*4'33"* at MoMA](https://www.moma.org/collection/works/163616); Hsieh, [artist archive](https://www.tehchinghsieh.net/artworks); Lozano, [*General Strike Piece*](https://blanton.emuseum.com/objects/6889/general-strike-piece) | artwork / score / archive / N/A | silence、duration、withdrawal の authored rule | absence / withdrawal が形式になりうる存在証明 | HCI の低負担、支援到達、Semantic Stop 実装を示さない |

### 引用射程の裁定

- open work は構造ある開放性であり、「意味が曖昧なら良い」という単調仮説ではない。
- data portrait は蓄積・表象の系譜であり、session-locality、non-diagnosticity、non-recapture を保証しない。
- autographic visualization は物質的 trace の epistemic relation を扱う。GSE の inferred portrait はそのまま同一分類へ入らない。
- UbiFit 等の ambient display は goal / reward / self-tracking を含むため、GSE の非報酬型 portrait の支持証拠ではない。
- withdrawal / silence の作品は termination-as-form の先行を示すが、処理停止、支援、負担の evidence ではない。
- mobility trace の再識別は path linkability の危険を示すが、GSE 固有の攻撃成功率は独自に測る必要がある。

したがって既存研究から直接借りられるのは、generative process、open interpretation、data portrait、trace legibility、ambiguity、withdrawal as form の各部品までである。経路依存 portrait、監査可能な Semantic Stop、非診断性、非回収、任意解釈の結合は、GSE の artifact comparison で独立に検査する。
