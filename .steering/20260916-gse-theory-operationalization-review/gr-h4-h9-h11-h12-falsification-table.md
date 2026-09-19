# GR-H4 / GR-H9 / GR-H11 / GR-H12 反証表 v0.1

> Status: pre-SSOT falsification draft / 2026-09-17
>
> 本表は有利な結果だけを拾わないための判定契約である。数値マージンと標本数は未確定であり、`EH3` 後かつ `EH4` 割付前に固定する。結果カテゴリは `支持候補 / 縮小 / 棄却 / 未解決` の四つとし、帰無仮説を棄却できなかったことを支持に読み替えない。

## 1. 横断表

| 命題 | 対象比較・操作 | 主要評価量 | 品質・安全 gate | 主要交絡・効果修飾 | 支持候補 | 縮小 | 棄却 | 未解決 |
|---|---|---|---|---|---|---|---|---|
| `GR-H4` 招待と命令 | `C3` Semantic Stop + no duty + minimum support 対 `C1` 命令 + receipt | 応答義務、罪悪感、不利益予期 | 選択肢分布の極端な集中と早期離脱が許容幅内。実際の不利益ゼロ | 実験者期待、社会的望ましさ、通知慣れ、課題切迫性 | 三主要量の事前指定 gate が改善し、品質・支援 gate を通過 | 義務感だけ改善する等、効果が一部概念に限られる | 拒否・無応答が圧力・再要求・評価低下へ結びつく、または一つの行為へ実質誘導 | CI が最小差を跨ぐ、分岐 probe が成立しない |
| `GR-H9` 負担転嫁と返権 | `C3` 対 `C2` Semantic Stop + residual duty、加えて `C4` negligent relinquishment | interaction burden、verification burden、応答義務 | 判断品質・支援到達可能性の非劣性、誤受容・無検証依存の上限、C3/C4 弁別 | 実際の支援需要、課題失敗、良心性、一般不安、アクセシビリティ需要 | burden gate 改善と全 quality/reliance/non-abandonment gate 通過 | 負担低減はあるが対象が限定、または処理構造の記述に留める | 負担が下がらない、品質・支援が許容幅外、誤受容/UVR が増える、C3 が C4 と弁別不能 | 欠測感度で結論が反転、非劣性 CI が不精確 |
| `GR-H11` 生産的摩擦 | 独立ミニ実験 `zero / light / heavy friction` | 誤受容、無検証依存、判断品質 | interaction burden、verification burden、完了率、時間、複雑性が許容範囲 | NFC、事前知識、friction preference、AI 信頼、item 難度 | light が zero より reliance を改善し、品質非劣性か改善、burden 上限内。heavy 優位は要求しない | 特定 item / 高 NFC 層だけで成立し、対象範囲を限定 | 摩擦が検証を改善せず burden だけ増加、または品質・公平性を悪化 | 操作強度が分離しない、CI が実用差を跨ぐ |
| `GR-H12` AI 疲労推定の分離 | 介入比較ではなく測定境界監査。完全 AFS は baseline / delayed outcome、短時間 burden は別尺度 | 構成概念の弁別、増分妥当性、校正 | AFS を瞬間状態・短縮版・介入入力にしない。群間校正を要求 | 一般疲労、作業量、時間帯、AI 利用量、technostress | 測定役割が分離され、研究用予測を行う場合のみ外部標本で増分妥当性と校正が成立 | 行動予測を棄却し AFS を外部自己報告だけに留める | content-free trace から診断・介入入力へ使用、独自項目を AFS と称する、校正不成立を無視 | 翻訳妥当性・独立標本・検出力不足 |

> ★ **2026-09-19（理論レビュー 判断 1 #14 = J-7）**: GR-H11 は **TH-GR の境界条件として保留する**。★ **GSE の研究計画（月次・研究ゲート）には入れない**（客観正答つき課題の摩擦ミニ実験は GSE の計画外）。§4 の設計は参照用に残す。
> ★ **2026-09-19（J-16）**: `C1`（命令＋完了確認）・`C4` を含む比較は研究用の別計器の中でだけ行う（GSE 本体・O1 に入れない）。

## 2. GR-H4 詳細契約

### 操作

- `C1`: 行為を命令形で示し、明示の受諾・拒否または完了確認を求める。
- `C3`: 行為を選択肢として提示し、反応を要求せず、expiry 後に意味認定と応答要求を終え、minimum support を残す。
- `C0`: 無招待を自然経過の補助対照とする。

表示量、視認性、提示時間、基礎情報は可能な限り揃える。命令条件だけ情報が多い、または target だけ目立たないという比較にしない。

### 判定順

1. 操作確認: C1 が命令・応答要求として、C3 が任意・再アクセス可能として理解されたか。
2. 主要: 応答義務、罪悪感、不利益予期の事前指定した intersection gate。
3. ガード: 選択肢分布の集中、早期離脱、支援到達可能性、判断品質。
4. 分岐: 明示の受諾・保留・拒否・見逃し・無応答の分布を報告するが、望ましい正解分岐を置かない。

`C3` の応答率が低いこと自体は支持ではない。低応答と同時に放置不安または支援失敗が高ければ放置的返還である。

## 3. GR-H9 詳細契約

### 二重台帳の操作

| 条件 | 意味認定・達成認定 | 応答・検証要求 | minimum support |
|---|---|---|---|
| C2 | 停止 | 残る | あり |
| C3 | 停止 | 終了 | あり |
| C4 | 停止 | 終了 | 欠く |

C2 対 C3 が残存義務の効果、C3 対 C4 が非放棄性の効果を担う。C2/C3/C4 を一つの「停止あり」群にまとめない。

### 共同 gate

- **改善が必要**: task-specific interaction burden または verification burden、および応答義務。
- **悪化させてはいけない**: 判断品質、支援到達可能性、誤受容、無検証依存。
- **弁別が必要**: C3 は C4 より support probe 成功が高く、放置不安が低い。

罪悪感だけの改善、主タスク再開だけの改善、自己報告 burden だけの改善は支持に足りない。

## 4. GR-H11 独立ミニ実験

### 4.1 課題

低リスクで、客観的正答があり、同じ情報から安価に検証できる decision task を使う。候補は、短い表・規則・証拠カードを照合して二択または多択を決める課題である。創作物の質、人格、健康、法務・医療判断は初回課題に使わない。

各参加者に正しい AI 提案と誤った AI 提案を事前固定比率で提示する。誤りは item 難度ともっともらしさを pilot で揃え、条件間で同じ item pool を counterbalance する。AI の正答率は参加者に虚偽説明せず、研究上必要な範囲で開示方針を倫理審査前に固定する。

### 4.2 摩擦の三水準

| 水準 | 操作 | 固定するもの |
|---|---|---|
| `zero` | AI 提案を即時表示し、最終回答を一操作で確定できる。証拠閲覧は任意 | 提案内容、証拠、最終回答選択肢 |
| `light` | AI 提案を見る前に独立した暫定回答を一度選び、提案表示後にそのまま又は変更して確定する | zero と同じ情報。追加は独立初答の一操作だけ |
| `heavy` | 独立初答に加え、提案表示後に証拠カードを一枚以上開き、提案を支持／反証する根拠カテゴリを選んでから確定する | light と同じ情報。自由記述は要求せず、構造化された二段確認 |

時間待ちだけ、情報追加、警告色、説明量増加を摩擦と混ぜない。heavy にだけ新しい正解情報を与えない。各操作の完遂イベント、時間、知覚複雑性を manipulation check とする。

### 4.3 評価量

| 種類 | 評価量 |
|---|---|
| Co-primary | 誤提案時の誤受容率、全 item の判断品質 |
| Key secondary | 全 verification-eligible item あたりの無検証依存リスク、誤答からの訂正、正答から誤答への変更、校正。採用条件付き UVR は補助値 |
| Burden | interaction burden、verification burden、知覚複雑性、完了時間、dropout / skip |
| Effect modifiers | Need for Cognition、事前知識、friction preference、AI 信頼傾向、item 難度 |

### 4.4 判定

light を採用候補とするのは、zero に対して誤受容または `UVR_risk` が事前指定した最小差以上改善し、判断品質が非劣性を満たし、burden と完了率が許容範囲内の場合だけである。heavy が light より良いことは命題の必要条件ではない。

以下は失敗である。

- heavy ほど検証イベントは増えるが、誤受容も判断品質も改善しない。
- light/heavy が正しい AI 提案まで拒否させ、全体品質を落とす。
- 利得が高 NFC 層にのみ集中し、低 NFC 層の burden または誤受容が悪化する。
- dropout を除くと効果が現れる completer-only パターン。
- 摩擦による所要時間を測っていないのに「効率との交換」と主張する。

### 4.5 P127/V37 から借りる範囲

借りるのは、cognitive forcing が過依存を減らしうる一方、複雑性・選好・NFC による異質性を伴いうるという設計上の存在証明である。GSE の最適水準、時間コスト、一般的な mental demand 増加、再現性は同文献から確定しない。

## 5. GR-H12 詳細契約

### 5.1 測定役割

| 測定 | 許可する用途 | 禁止する用途 |
|---|---|---|
| 完全な 15 項目 AI Fatigue Scale | AI を日常的に使う対象集団の baseline 傾向共変量、十分な遅延を置いた追跡 outcome | 瞬間状態、短時間 block manipulation check、介入 trigger |
| task-specific burden items | block 直後の interaction / verification burden | AI Fatigue Scale または短縮版という名称 |
| content-free 行動痕跡 | 独立標本・外部 outcome に対する探索的予測 | AI 疲労の診断、本人への表示、介入入力 |

日本語版は翻訳・逆翻訳、認知インタビュー、因子構造の確認を経るまで確立尺度と呼ばない。

### 5.2 研究用予測を行う場合

1. baseline、時間帯、一般疲労、作業量、AI 利用量を先に入れた基準モデルを固定する。
2. content-free feature の追加増分を holdout で評価する。
3. discrimination だけでなく calibration-in-the-large、calibration slope、群別誤差を報告する。
4. task/session/person split を明示し、同一人物 leakage を避ける。
5. 失敗時は予測研究を棄却し、AFS を自己報告 outcome に留める。

相関が高くても、短時間行動痕跡と回顧的傾向尺度が同一構成概念になったとは判断しない。逆に増分妥当性がなくても TH-GR 全体を棄却せず、「AI fatigue を行動予測へ接続する派生仮説」を棄却する。

## 6. マージン決定表

| 評価量 | 効果方向 | マージン型 | 決定主体・材料 | 現状 |
|---|---|---|---|---|
| 応答義務 / guilt / penalty | C3 が低い | 最小優越差 | EH3 認知インタビュー、尺度信頼性、対象利用者の実用差判断 | unresolved |
| 判断品質 | C3/light が低下しすぎない | 非劣性 `delta_DQ` | 課題損失、専門家判断、blind pilot 分布 | unresolved |
| 誤受容 | 増加しない、GR-H11 では低下 | 絶対 risk difference `delta_EA` | 誤り一件の損失、低リスク課題の許容件数 | unresolved |
| 無検証依存 | 増加しない | 絶対 risk difference `delta_UVR` | verification-required item のリスク分類 | unresolved |
| 支援到達可能性 | C3 が低下しすぎない | 非劣性 `delta_SA` + 実装最低率 | 到達不能一件の損失、手順・時間基準 | unresolved |
| burden / complexity | light/heavy が増えすぎない | superiority または上限 | 完了時間、離脱、主観尺度の practical difference | unresolved |

マージンを標本サイズが収まる値へ緩めない。複数候補のうち結果が有利なものを事後採用しない。

## 7. 敵対的レビュー

| 攻撃仮説 | 本契約の防御 | 残る弱点 |
|---|---|---|
| 低罪悪感は支援放棄の結果にすぎない | C4 negative control、支援到達可能性、放置不安を同時判定 | C4 の倫理的・知覚的な強さ |
| 無応答者を除けば効果が良く見える | IAS と欠測 bounds、completer-only 禁止 | SEL の MNAR 仮定は検証不能 |
| 摩擦は情報を増やしたから効いただけ | 三条件で情報を固定し、操作回数だけ変える | perceived information は完全には統制できない |
| 検証回数を増やしただけで品質は上がっていない | EA/DQ を co-primary、burden を同時 gate | task-specific な正答の外的妥当性 |
| guilt 項目が obligation を言い換えただけ | 二項目ずつ分け、認知インタビューと因子弁別を要求 | 小標本では弁別困難 |
| 支援到達可能性 probe が支援需要を人工的に作る | 実需要と標準 probe を別評価 | probe 学習が後続機会へ影響 |
| AI Fatigue Scale を都合よく短縮している | 完全尺度と task burden を名称・時点・用途で分離 | 日本語版の妥当化が未了 |
| 再開を成功としている | 競合転帰の一つとして扱い、回復・遵守と呼ばない | 外部化チャネルの観測範囲 |

## 8. 文書間整合チェック

- 8 構成概念の定義は `measurement-dictionary.md` を参照し、本表で別定義を作らない。
- IAS、条件 C0-C4、分岐、競合転帰、欠測は `eval-ncc-analysis-contract.md` と一致する。
- 因果順序と調整禁止変数は `eval-ncc-dag.md` に従う。
- GR-H11 は EVAL-NCC の付記ではなく独立ミニ実験である。
- GR-H12 は AI fatigue を GSE の潜在状態、瞬間状態、介入入力へ変えない。
- EH1 実装、EH2 本人、EH3 外部形成、EH4 統制比較を同一証拠として数えない。
- `negligent relinquishment` は設計上の負の比較条件であり、formal negative-control exposure / outcome ではない。

## 9. 次の限定調査

広い survey は行わず、次の不足セルに限る。

1. guilt / obligation / anticipated penalty / abandonment の既存項目と弁別妥当性。
2. 支援到達可能性を access、availability、help-seeking efficacy からどう借りるか。
3. principal stratification と competing outcomes を opportunity-level randomized design へ適用する一次方法論。
4. NFC と friction preference の日本語尺度・利用許諾。

調査が未了でも本表の未解決を埋めた体にせず、数値マージンと尺度採用を保留する。
