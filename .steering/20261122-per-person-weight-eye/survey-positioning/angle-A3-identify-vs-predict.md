# angle A3: 見分け（識別）と予測・個人化の得の乖離（Q2）

調査日 2026-11-23。WebSearch（標準モード）・OpenAlex API・Crossref API・WebFetch。PMC と Nature は WebFetch が reCAPTCHA / リダイレクトで止まったため、抄録は OpenAlex の再構成テキストで読んだ（本文は未読）。DOI は OpenAlex が返したもので、ブラウザでは開いていない（以下「API 照合のみ」）。

## 結論（先に）

- 乖離を「識別（fingerprinting）と予測」の言葉で明示した研究は 1 つ見つかった（Mantwill 2022・fMRI）。ただし比べているのは「識別に効く特徴」と「行動の予測に効く特徴」の重なりで、「同じ人のモデルを作ると予測が良くなるか」ではない。この研究の問い（本人の A が本人の B に近いか vs 本人モデルの尤度の得）とは軸が違う。
- 「識別できれば個人化の得も大きい」と示した研究は 0 件。「個人化の得は識別可能性と対応する」と測った研究も 0 件（検索式は下の「0 件の検索」）。
- 個人化の要否を「予測の得」でなく「個人差の検出」で判定する枠組みは近い先例がある（Suriyakumar 2022 の BoP は得の側・Chang 2021 は異質性の置換検定・Chaibub Neto 2017 は識別の置換検定）。いずれも打鍵や尤度の入れ替え検定ではない。
- したがって新しさは減らないが、「分野をまたいで先例が無い」とは言えない。神経画像に近い先例があるので、位置づけは「別の対象（生成系列の遷移表）・別の量（個人化の得との同一記録での対比）」と限って書くのが安全。

## 文献（7 件）

### 1. Mantwill, Gell, Krohn & Finke (2022) — 最重要（近いが違う）
- 書誌: Mantwill M., Gell M., Krohn S., Finke C. "Brain connectivity fingerprinting and behavioural prediction rest on distinct functional systems of the human connectome." *Communications Biology* 5(1):261, 2022. DOI 10.1038/s42003-022-03185-3（API 照合のみ。プレプリント版 10.1101/2021.02.07.429922 も Crossref にあり）。
- 読んだ範囲: 抄録（OpenAlex）。本文未読。
- 引用: "Our analysis revealed a substantial divergence between discriminatory and predictive connectivity signatures on all levels of network organisation." / "These results demonstrate that participant identification and behavioural prediction involve highly distinct functional systems of the human connectome. The present study thus calls into question the direct functional relevance of connectome fingerprints."
- N と設計: HCP 系の大規模 fMRI 集団（人数は抄録に無く未確認）。接続（edge）単位で識別に効く接続と、行動予測に効く接続の分布を比べた。
- Q2: 近いが違う（乖離の明示例。ただし「同じ人のモデルで得る予測の得」ではなく、特徴の重なりの乖離）。この研究が「乖離は新規」と書くなら、これを先例として挙げて差を述べる必要がある。
- references.md: 無い（`s42003` は P72 の別論文のみ）。

### 2. Finn & Rosenberg (2021)
- 書誌: Finn E.S., Rosenberg M.D. "Beyond fingerprinting: Choosing predictive connectomes over reliable connectomes." *NeuroImage* 239:118254, 2021. DOI 10.1016/j.neuroimage.2021.118254（API 照合のみ）。
- 読んだ範囲: 抄録のみ。
- 引用: "we should use behavior prediction as our benchmark rather than optimize reliability for its own sake."
- 設計: 意見論文。
- Q2: 近いが違う（識別の信頼性より予測を基準にせよ、という立場。「識別できても予測に効くとは限らない」の理論側の裏づけ）。支持の側だが、実測ではない。
- references.md: 無い。

### 3. Byrge & Kennedy (2019, 2020)
- 書誌: (a) Byrge L.A., Kennedy D.P. "High-accuracy individual identification using a 'thin slice' of the functional connectome." *Network Neuroscience* 3(2):363–383, 2019. DOI 10.1162/netn_a_00068. (b) Byrge L.A., Kennedy D.P. "Accurate prediction of individual subject identity and task, but not autism diagnosis, from functional connectomes." *Human Brain Mapping* 41(9):2249–2262, 2020. DOI 10.1002/hbm.24943（API 照合のみ）。
- 読んだ範囲: 抄録のみ。
- 引用 (a): "as few as 40 out of 64,620 functional connections—was sufficient to uniquely identify individuals." / "no specific connections or even specific networks were necessary for iden[tification]"（抄録が途中で切れている）。(b) は題が主張そのもの（識別は高精度・診断は不可）。
- N と設計: (a) HCP 約 3,300 スキャンの split-half ＋独立の再現標本。(b) ASD と対照・最大 2 時間/人の複数セッション（人数は未確認）。
- Q2: 近いが違う。識別は「ごく少数の特徴」で足りるため、識別の高さは個人差の「予測に効く量」を示さない、という例。
- references.md: 無い。

### 4. Sasse et al. (2023) — 反証の側（識別と予測が同じ条件で両方高い）
- 書誌: Sasse L., Larabi D.I., Omidvarnia A., Jung K., Hoffstaedter F. ほか "Intermediately synchronised brain states optimise trade-off between subject specificity and predictive capacity." *Communications Biology* 6(1):705, 2023. DOI 10.1038/s42003-023-05073-w（API 照合のみ。著者は OpenAlex の先頭 5 名のみ確認）。
- 読んだ範囲: 抄録のみ。
- 引用: "time points of lower and intermediate co-fluctuation levels provide overall highest subject specificity as well as highest predictive capacity of individual-level phenotypes."
- 設計: fMRI の時点ごとの FC を共変動の高さで層別し、識別（subject specificity）と表現型予測（機械学習）を同じデータで比べた。
- Q2: 反証の側（識別と予測が同じ層で同時に最大になる）。題に "trade-off" とあるが抄録の結論は両方が高い層の存在。人の間の予測（個人化の得ではない）である点は変わらない。
- references.md: 無い。

### 5. Chaibub Neto et al. (2017/2019) — 識別が予測を水増しする
- 書誌: Chaibub Neto E., Pratap A., Perumal T.M., Tummalacherla M., Bot B.M. "Learning Disease vs Participant Signatures: a permutation test approach to detect identity confounding in machine learning diagnostic applications." arXiv:1712.03120, 2017（のち npj Digital Medicine 2019 に載った可能性があるが未確認）。
- 読んだ範囲: 抄録（OpenAlex）。
- 引用: "'subject identity confounding' caused by the classifier's ability to identify subjects, instead of recognizing disease."
- 設計: 記録単位の分割と人単位の分割の比較・識別の混入を調べる置換検定を 2 種提案。
- Q2/Q3: 近いが違う。「分類器が人を見分けること」と「本来の目的の予測」を分けて検定する先例（Q3 の置換の妥当性にも効く）。ただし向きは「識別の混入は予測の見かけの精度を上げる」で、この研究の「識別できるが個人化の得が小さい」とは逆の向きの乖離。これを踏まえて関連する Saeb 2017 [V98]・Little 2017 [V99] は登録済み（本論文自体は未登録）。
- references.md: 本論文は無い。Saeb [V98]・Little [V99] は有る。

### 6. Suriyakumar, Ghassemi & Ustun (2022/2023) — 個人化の要否を得で判定
- 書誌: Suriyakumar V.M., Ghassemi M., Ustun B. "When Personalization Harms: Reconsidering the Use of Group Attributes in Prediction." arXiv:2206.02058, 2022（ICML 2023 採択と記憶しているが未確認）。
- 読んだ範囲: 抄録のみ。
- 引用: "models that are personalized with group attributes can reduce performance at a group level." / 抄録の別の文で、群ごとに「tailored gain」を保証する条件（"collective preference guarantees"）を提案。
- 設計: 臨床予測タスクでの実証研究。人単位ではなく属性の群単位。
- Q2: 近いが違う。個人化の要否を得（BoP）の検定で判定する側の先例。識別可能性との対比はしていない。
- references.md: 無い。

### 7. Chang et al. (2021) — 異質性の置換検定（Q2 の観点 2）
- 書誌: Chang C., Jaki T., Sadiq M.S., Kuhlemeier A., Feaster D.J. "A permutation test for assessing the presence of individual differences in treatment effects." *Statistical Methods in Medical Research* 30(11):2369–2381, 2021. DOI 10.1177/09622802211033640（API 照合のみ）。
- 読んだ範囲: 抄録のみ。
- 引用: "a permutation test is proposed to establish if significant heterogeneity is present given the covariates and predictive model or algorithm used for predicted individual treatment effects."
- 設計: 個別の治療効果の予測に基づく異質性の置換検定・シミュレーションで第 1 種の誤り率を確認。
- Q2/Q3: 近いが違う。個人差の「検出」を予測の得とは別の量で置換検定する先例（治療効果の文脈）。人の名札の入れ替えによる検定の先例ではない。
- references.md: 無い。

## 追加で見つけたが採らなかった・弱いもの

- Cornelis et al. (2026, ICLR) "When Machine Learning Gets Personal: Evaluating Prediction and Explanation." arXiv:2502.02786。抄録に「予測は変わらないのに説明可能性が変わりうる」とあり、個人化の効果が量により乖離するという近い話だが、識別ではない。抄録のみ・補助。
- Li & Washington (2024) *JMIR AI* 3:e52171（WESAD で個人化 約 95% vs 汎用 約 67%）。個人化の得が大きい例。識別との比較は無い。人内の分割による見かけの得（Saeb/Little の問題）の疑いがあり、Q2 では使わない。
- Fisher et al. (2018) [V108]・Molenaar [V107] は登録済み（個人内の構造は個人間から導けないという理論側）。再収集しない。
- Hedge らの reliability paradox（Rouder & Haaf 2019 は OpenAlex で見えたが抄録なし）。「頑健な群の効果と個人差の信頼性が別」という近い主張。本論文は未読のため推奨しない。要るなら原典 Hedge, Powell & Sumner (2018) を別途確認。

## 0 件の検索（検索式 × ソース）

- 「identification accuracy versus personalization/adaptation gain」「speaker identification accuracy does not predict speaker adaptation gain」: WebSearch で 0 件（音声の聴取者の話者適応の個人差の論文が出たが、モデルの話者適応ではない）。OpenAlex の "speaker recognition versus speaker adaptation gain correlation i-vector adaptation" も 0 件（話者認識の一般論文のみ）。
- 「personalization gain correlates with user identifiability / distinctiveness」: WebSearch で 0 件（BehaVR・WristPrint など識別のみの研究）。
- 「wearable ... highly identifiable yet personalized model little improvement」: WebSearch で 0 件（出たのは個人化が大きく勝つ Li & Washington のみ）。
- 打鍵（keystroke dynamics）で識別と個人化モデルの得を両方測った研究: 今回の検索では 0 件（A3 の範囲では打鍵に絞った検索を回していない。Q1 の angle の結果と合わせて判断してほしい）。
- 推薦の個人化・歩容・言語モデルの個人化: 今回は検索していない（未実施）。ここは穴。
- 「識別できる個人差があれば個人化の得も大きい」と示した研究: 上のすべてで 0 件。ただし 0 件は「無い」の証明ではなく、神経画像以外は検索の幅が狭い。

## 未読・未確認

- 全件とも本文は未読（抄録のみ）。PMC は reCAPTCHA、Nature はリダイレクトで WebFetch が止まった。
- Mantwill 2022 の N、Sasse 2023 の著者の全員、Suriyakumar の採択先は未確認。
- Chaibub Neto の査読版の有無は未確認。
