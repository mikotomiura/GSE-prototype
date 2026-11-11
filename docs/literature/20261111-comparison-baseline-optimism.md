# 文献カード: 比べの相手が弱いと個人化は良く見える —— 論文 3 の T4（打鍵からのユーザーモデリングと cold-start）

- **トピック**: comparison-baseline-optimism
- **日付**: 2026-11-11
- **作業記録**: `.steering/20261111-gse-paper3-round3-computations/`（attack-me round 3 の T4）
- **用途**: 論文 3 の新規性の文と関連研究の根拠（gate 判定ではない）。結果を段 1 の候補の採否や ADR-047 の根拠にしない。

## 動機

round 3 の T4: 打鍵からのユーザーモデリングと cold-start（いつ本人のモデルに切り替えるか）の文献が未調査のまま、外枠に新規性の文があった。探索の記録は `.steering/20261111-gse-paper3-round3-computations/survey-t4-keystroke-usermodel-coldstart.md`（サブエージェントの報告の写し・未検証）。ここでは、そのうち新規性の文に効く 3 本を本文で確かめた。

## 検証状態

- 本文を読んだ: [V535]（PLoS の全文）・[V536]（Microsoft Research の PDF の全文）。[V537] は出版版の本文が取れず、OSF のプレプリント版の本文と出版版の抄録で確かめた（数値は抄録とプレプリントで一致）。読んだのはサブエージェント（Sonnet）で、逐語を持ち帰った。メインは逐語の照合をしていない。
- 既登録: [P270] Uto ら 2020（学習者と時間に依存する HMM・30 秒窓の打鍵の特徴量）。以前に本文を読んだ記録はあるが、評価の設計（同じ書き手の後の区間での予測・本人の連鎖や共通との比べ）は記録に無い。今回は UEC のリポジトリが保守中で本文が取れず、抄録だけ。**評価の設計は未確認**。[P221] Naegelin ら 2025（打鍵とマウスと心拍でストレス・個人のモデルが本人の平均のダミーに勝たない）は既登録で、プレプリント。
- 3 票の判定は回していない（新規性の文の周辺の先例として引くだけ）。

## 要点

| 問い | 温度 | 一言 |
|---|---|---|
| 比べの相手しだいで個人化の見え方が変わるという論点は既出か | 既出（2 研究・本文） | 気分とストレスで、集団の基準と比べると楽観に偏る（[V535]）。全員のモデルが本人の平均に負ける（[V536]） |
| いつ本人のモデルに切り替えるか（cold-start） | 場面しだい | 30 日を過ぎて個人のモデルが hybrid を上回った（[V536]）。全員のモデルが本人のモデルを上回った（[V537]） |
| 打鍵の記号列の 1 人ごとの系列のモデルを、本人の 1 次のマルコフ・構造と縮みを他人で選んだ共通・その最頻値と比べた研究 | 見つからなかった | 最も近いのは [P270]（打鍵の 30 秒窓に学習者依存の HMM）。評価の設計は未確認 |

---

### カード 1: 集団の基準と比べると楽観に偏る **[本文]** [V535]

1. **どんなもの？** スマホの GPS の特徴量から日ごとの気分とストレスを予測する研究の、比べの相手を問うた研究。StudentLife（15 人）と MIT Friends and Family（31 人）。
2. **先行研究と比べてどこがすごい？** 逐語: "it is possible to explain over 80% of the variance of some mood measures in the population by simply guessing that each patient has their own average mood—the patient-specific baseline."。文献の約 77% が本人の基準を無視した比べを使う。
3. **技術や手法の肝はどこ？** 本人の平均（"The personal baseline always guesses that each individual is at a constant state, but that state can differ between individuals."）を相手に置き、"user lift"（本人の基準の誤差 − モデルの誤差）を個人ごとに出す。
4. **どうやって有効だと検証した？** 逐語: "Our algorithms are much better than the population baseline and population models. They are not, however, lower than the personal baselines."。user lift は 6 行とも 0 前後か負。
5. **議論はあるか？** 相手は本人の平均（定数）で、1 次のマルコフでも、構造と縮みを他人で選んだ共通でもない。対象は日ごとのスカラーで、系列のモデルではない。論文 3 の「比べの相手で見え方が変わる」は、この論点の先例の上に置く。
6. **次に読むべき論文は？** 著者が文献レビューで挙げた、個人ごとの順位の検定を報告した研究。

### カード 2: 全員のモデルは本人の平均に負け、個人のモデルは 30 日を過ぎて上回る **[本文]** [V536]

1. **どんなもの？** 32 人・2 か月のスマホの利用のログ（SMS・メール・通話・アプリ・Web・位置）から日ごとの気分（pleasure・activeness）を推定する MoodScope。
2. **先行研究と比べてどこがすごい？** 全員のモデル 66%、個人のモデル 2 か月で 93%（Abstract）。単純な基準 3 つを並べ、本人の平均（Model A）が 73% で全員のモデルより良い（"Of these methods, the average mood method works best, with an average MSE of 0.242 and accuracy of 73%, performing only slightly better than our all-user model."）。
3. **技術や手法の肝はどこ？** hybrid は本人の学習データの残差を優先する重み付きの重回帰で、重みは MSE を最小にする格子の探索で決める。
4. **どうやって有効だと検証した？** §5.3.5 の逐語: "even with only 10 days of personalized training data, the hybrid model has higher MSE accuracy than the incremental personalized by 31% and the all-user model by 6%. After 30 days, the personalized model outperforms the hybrid model and can be used with greater than 75% accuracy."
5. **議論はあるか？** 本人の平均の基準は 2 か月分の履歴を使う（著者の注記）ので、10 日の hybrid と条件が違う。系列のモデルでも、構造を他人で選ぶ手順でもない。cold-start の時期の例として引く。
6. **次に読むべき論文は？** 同じ時期の個人化と一般化の比べ（Rozet ら 2019 など）。

### カード 3: 全員のモデルが本人のモデルを上回る **[プレプリント本文と出版版の抄録]** [V537]

1. **どんなもの？** 摂食障害とアルコール使用障害の患者 120 人の EMA（12 か月・7 回のバースト）から、過食・飲酒・多量飲酒を予測する。elastic net・入れ子の交差検証・AUC。
2. **先行研究と比べてどこがすごい？** 抄録の逐語: "The person-specific models had a median AUC of 0.61, 0.80, and 0.85 for BE, alcohol use, and BD respectively, while the pooled models had a median AUC of 0.70, 0.90, and 0.93."
3. **技術や手法の肝はどこ？** 全員のモデルは全員の学習分で学び、各人のテスト分で測る。
4. **どうやって有効だと検証した？** プレプリントの考察: 全員のモデルが上回るのは多くの先行と同じ向きで、理由は観測数と均質さ（"group-level methods lend themselves well to samples that are homogenous (i.e., with a low inter-individual variability)"）。
5. **議論はあるか？** 打鍵でも系列のモデルでもない。本人の単純な基準や部分的なプールは比べていない。出版版の本文は確かめていない。
6. **次に読むべき論文は？** Rozet ら 2019（個人のモデルは観測が増えると全員のモデルに並ぶ）・Soyster ら 2021。

## 否決・保留

- [P270] Uto ら 2020 の評価の設計は未確認（本文が取れなかった）。新規性の文では「最も近い先行」として名前を挙げるだけにし、その評価の設計について書かない。本文が取れたら確かめる（外枠の Open items）。
