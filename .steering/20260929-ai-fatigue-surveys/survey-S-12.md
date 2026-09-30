# S-12 日本語の文献・日本の対象者の研究 —— 検索記録と書誌（事実）

> 検索日: 2026-09-29（日本時間。日本語の検索 21:12・抄録ふるい 21:17〜21:19・英語の検索 21:21。各 JSON の executed）。手順は `design.md` §1（検索の前に固定）。
> ★ このファイルは事実だけを書く（検索記録・書誌・抄録や本文に書いてあること）。判定に関わる記述は別のファイル（`survey-S-12-ai-judgments.md`）にある。
> ⚠️ 件数は検索の範囲を示す目安で、PRISMA の件数ではない。
> 生の結果（書誌だけ）: `evidence/S-12/s12_ja_results_2026-09-29.json`・`s12_abstract_filter_2026-09-29.json`・`s12_abstract_filter_body_2026-09-29.json`・`s12_en_results_2026-09-29.json`。スクリプト: `evidence/S-12/*.py`。

## 1. 何を探したか

日本語で書かれた研究、または日本の対象者を扱った研究のうち、AI を利用・監督・評価する人の疲労（燃え尽き・消耗を含む）を定義・測定・質的に分析したもの。

## 2. 検索記録

### 2.1 日本語の情報源

| 情報源 | 欄 | 語の組 | 実行した検索の数 | 1 件以上当たった検索 | 総件数の和 | 題名ふるいの通過 |
|---|---|---|---|---|---|---|
| J-STAGE | 題名（`article`） | AI の語 6 × 疲労の語 7 | 42 | 1（`AI 疲労` 14 件） | 14 | 10 |
| J-STAGE | 抄録（`abst`） | 同上 | 42 | 9 | 25 | 1 |
| J-STAGE | 題名 | 狭い AI の語 4 × 負担の語 2 | 8 | 2 | 3 | 0 |
| J-STAGE | 抄録 | 同上 | 8 | 8 | 156 | 0 |
| J-STAGE | 題名 | 英語の AI の語 5 × 英語の疲労の語 4 | 20 | 1 | 1 | 1 |
| J-STAGE | 抄録 | 同上 | 20 | 5 | 16 | 2 |
| CiNii Research（all） | 題名 | `(AI OR 人工知能 OR ChatGPT OR 大規模言語モデル OR LLM OR チャットボット) (疲労 OR 疲れ OR 疲弊 OR 燃え尽き OR バーンアウト OR 消耗 OR テクノストレス)` | 1 | 1 | 54 | 31 |
| CiNii Research（all） | 題名 | `(生成AI OR ChatGPT OR 大規模言語モデル OR LLM) (負担 OR 負荷)` | 1 | 1 | 24 | 0 |
| CiNii Research（all） | 題名 | `("generative AI" OR ChatGPT OR "large language model" OR "artificial intelligence" OR chatbot) (fatigue OR burnout OR exhaustion OR technostress)` | 1 | 1 | 19 | 18 |
| CiNii Research（KAKEN の研究課題） | 題名 | 上の 3 本 | 3 | 3 | 9・2・2 | 11（重複を除く前。英語の組の 2 件は日本語の組の 9 件と重なる。負担の語の組の 2 件は通過していない） |
| 国立国会図書館サーチ | 題名 | AI の語 6 × 疲労の語 7 | 42 | 9 | 132 | 30 |

- AI の語: `AI`・`人工知能`・`ChatGPT`・`大規模言語モデル`・`LLM`・`チャットボット`。疲労の語: `疲労`・`疲れ`・`疲弊`・`燃え尽き`・`バーンアウト`・`消耗`・`テクノストレス`。狭い AI の語: `生成AI`・`ChatGPT`・`大規模言語モデル`・`LLM`。負担の語: `負担`・`負荷`。英語: `generative AI`・`ChatGPT`・`large language model`・`artificial intelligence`・`chatbot` × `fatigue`・`burnout`・`exhaustion`・`technostress`。
- J-STAGE で 1 件以上当たった検索（欄・語・件数）: 題名 `AI 疲労` 14 ／ 抄録 `AI 疲労` 12・`AI 疲れ` 4・`AI 疲弊` 1・`人工知能 疲労` 2・`人工知能 疲れ` 2・`人工知能 疲弊` 1・`大規模言語モデル 疲れ` 1・`LLM 疲労` 1・`LLM 疲れ` 1 ／ 題名 `生成AI 負荷` 1・`LLM 負荷` 2 ／ 抄録 `生成AI 負担` 48・`生成AI 負荷` 12・`ChatGPT 負担` 11・`ChatGPT 負荷` 2・`大規模言語モデル 負担` 28・`大規模言語モデル 負荷` 15・`LLM 負担` 24・`LLM 負荷` 16 ／ 題名 `large language model exhaustion` 1 ／ 抄録 `ChatGPT fatigue` 1・`large language model fatigue` 3・`large language model exhaustion` 2・`artificial intelligence fatigue` 7・`artificial intelligence exhaustion` 3。ほかの組は 0 件。
- ★ 比較のため件数だけ記録した J-STAGE の全文（`text`）の検索: `AI 疲労` 9,066 件・`生成AI 疲労` 201 件（題名・抄録に限った上の件数との差は、本文中の語の一致による）。
- J-STAGE の欄は中間一致で、`AI` は英単語の一部や合金の表記（`AI合金`）にも当たる。国立国会図書館サーチの題名の検索は、`AI` を読みの「アイ」（例: 「愛に疲れて」）にも当てた。

### 2.2 ふるい（事前に固定した正規表現・`design.md` §1.4）

- 取得した記録（重複を除く前）: J-STAGE 215・CiNii Research 110・国立国会図書館サーチ 132。
- **題名ふるい**（題名に AI の語と疲労の語の両方）を通った記録と、**抄録ふるい**（J-STAGE の抄録の欄で当たり、題名ふるいを通らなかった 145 件の抄録に同じ正規表現を当てた）を通った記録を合わせ、題名で重複を除くと **75 件**（3 節）。
  - 抄録ふるい: 145 件のうち 139 件は論文ページの `<meta name="abstract">` から、6 件は本文側の抄録の枠から抄録を取った（`decisions.md` 判断 2）。通過は 17＋5 = 22 件。
- 負担の語（`負担`・`負荷`）の組で当たった記録（J-STAGE の抄録 156 件・CiNii 24 件）は、題名・抄録に疲労の語が無く、ふるいを 1 件も通らなかった。題名からは、生成 AI や LLM を教育・医療・業務の支援に使い、作業の負担を減らすことを目的に掲げた報告が多い（例: 採点・所見文・問題作成・記録の支援）。

### 2.3 英語の情報源（日本の対象者）

| 情報源 | 欄 | 検索式 | 総件数 | 状態 |
|---|---|---|---|---|
| Europe PMC | 題名・抄録＋所属 | `TITLE_ABS:("generative AI" OR ChatGPT OR "large language model" OR "artificial intelligence" OR chatbot) AND TITLE_ABS:(fatigue OR burnout OR exhaustion OR technostress) AND (TITLE_ABS:(Japan OR Japanese) OR AFF:Japan)` | 22 | 取得済み |
| Europe PMC | 題名・抄録 | 上から `OR AFF:Japan` を外した式 | 11 | 取得済み |
| Semantic Scholar | 一括検索（題名・抄録） | `("generative AI" \| ChatGPT \| "large language model" \| "artificial intelligence" \| chatbot) + (fatigue \| burnout \| exhaustion \| technostress) + (Japan \| Japanese)` | 25 | 取得済み |
| OpenAlex | `search` | `(… AI の語 …) AND (… 疲労の語 …) AND (Japan OR Japanese)` | — | ⚠️ 使えなかった（HTTP 503・「匿名の検索を止めている」という応答。21:40 に再試行しても同じ） |

- 3 本の和から DOI で重複を除くと 39 件。題名・抄録を読み、日本の対象者か、AI の利用と疲労の両方を扱うかを 4 節に書いた。

### 2.4 検索しなかった・できなかった情報源

| 情報源 | 理由 |
|---|---|
| 医中誌 Web | 有料（機関の契約が要る） |
| 情報処理学会 電子図書館（情報学広場） | スクリプトで検索する口が無い |
| Google Scholar | 自動取得を利用規約で禁じている |
| 学会の予稿で J-STAGE・CiNii に無いもの（ヒューマンインタフェースシンポジウム・日本産業衛生学会の抄録集など） | 公開の検索口が無い、または未確認 |
| CiNii Research の抄録の欄（`description`） | `all` で 0 件を返した（抄録の欄の検索は J-STAGE で行った） |
| OpenAlex | 2.3 のとおり |

## 3. ふるいを通った日本語の情報源の記録（75 件）

### 3.1 題名・抄録が合金・材料・構造物の疲労を示すもの（30 件）

題名に `AI合金`・`AI2024-T4`・`A1押出し材`・`A7075-T6`・`クリープ疲労`・`床版`・`疲労破壊`・`疲労き裂`・`fatigue fracture`・`fatigue life` などを含み、材料・構造物の疲労を扱うもの。代表: 「AI合金溶湯鍛造材の疲労強度に及ぼす微視組織の影響」（日本機械学会論文集 A 編, 2000）、「時効硬化AI合金の疲労強度に及ぼすプラズマ酸化処理の影響」（日本機械学会九州支部講演論文集, 2013）、「ＡＩ画像分析による反応性骨材使用ＲＣ床版の疲労劣化検知に関する研究」（構造工学論文集 A, 2021）、「セラミックス複合材の熱疲労試験のためのレーザー照射条件を提案するAIの開発」（応用物理学会学術講演会講演予稿集, 2022）、「赤外線サーモグラフィを用いたAI合金異材摩擦攪拌接合接手の疲労限度推定」（軽金属溶接, 2026）ほか。
次もここに数えた: 抄録ふるいを通った「溶接ビード形状の応力集中係数・応力勾配の自動推定」（日本船舶海洋工学会講演会論文集, 2025）・「ダクタイル鋳鉄管の鋳肌検査」（材料, 2024／MATERIALS TRANSACTIONS, 2026 の 2 件。抄録は検査員の疲労で判定が不安定になると述べる）・「農道用アスファルト舗装のわだち掘れ」（2005。抄録の `AI` は米国アスファルト協会の略）・「AI-Hip cementless stem 有限要素モデル」（2009）／CiNii の英語の組から入った 3 件（Artificial intelligence-assisted fatigue fracture recognition, 2022・A hybrid approach … fatigue life of belt grinding, 2023・Early damage detection of fatigue failure for RC deck slabs, 2021）／KAKEN の研究課題 2 件（疲労破損事例データベースの構築と破壊予防診断AIシステムの開発・疲労損傷を『誘導して見抜く』：SMAとAIによる大規模施設のための長寿命構造体の開発）。一覧は `evidence/S-12/` の JSON にある。

### 3.2 AI が人の疲労・燃え尽きを測る・検知する道具として題名・抄録に書かれているもの（13 件）

| 年 | 題名 | 収録先・種別 | 読んだ範囲 | 書いてあること |
|---|---|---|---|---|
| 2026 | 筋・軟部組織の滑走性から筋疲労度を判定するAIシステムの構築 | デサントスポーツ科学 doi:10.57488/descente.47.0_155 | 題名 | 筋疲労度を判定する AI システムの構築 |
| 2025 | AI音声解析を用いたバーンアウト検知の可能性と持続的な働き方に関する検討 | 蓮花寺佛教研究所 紀要 | 題名 | 音声解析 AI によるバーンアウトの検知 |
| 2025 | AIによるドライバーの疲労・眠気検知技術 | 検査技術（商業誌の記事） | 題名 | 運転者の疲労・眠気を検知する AI ソフトウェアの紹介 |
| 2025 | Few-Shot Optimization for Sensor Data Using Large Language Models: A Case Study on Fatigue Detection | Sensors doi:10.3390/s25113324（同じ題名の記録がもう 1 件・機関リポジトリ） | 抄録（2026-09-30） | 加速度データからの疲労の検知の課題に、LLM の few-shot の例の選び方（ユークリッド距離の絞り込みと LLM による文脈の関連の順位づけ）を当てた。マクロ F1 は 69.13±10.71%（無作為の選び方 59.30%・距離だけ 67.61%） |
| 2024 | Improving Fatigue Detection with Feature Engineering on Physical Activity Accelerometer Data Using Large Language Models | Int J Activity and Behavior Computing doi:10.60401/ijabc.18 | 題名 | 加速度データと LLM による疲労検知 |
| 2021 | Design and rationale of an intelligent algorithm to detect burnout in healthcare workers … (BRUCEE-LI) | Indian Heart Journal doi:10.1016/j.ihj.2020.11.145 | 抄録（2026-09-30） | 研究の計画。北インドの 4 施設の医療者 900 名以上（予定）の横断の観察研究で、燃え尽きを Mini Z で測り、心電図から燃え尽きを予測する畳み込みニューラルネットワークのモデルを作る |
| 2026 | Inferring Emotion Words in Occupational Fatalities Using a Large Language Model | ISASE 2026 doi:10.5057/isase.2026-C000057 | 抄録 | 労働災害の記述から LLM で感情語を推定し、「疲労」などの 9 区分に集計 |
| — | KAKEN: AI瞳孔計測システムを用いた医師の身体的・精神的疲労度評価 | 研究課題 | 題名・概要 | 瞳孔計測 AI で外科医の疲労度を評価するシステムの開発 |
| — | KAKEN: AI瞳孔計測を活用した看護師の疲労の客観的評価と労働環境改善モデルの構築 | 研究課題 | 題名 | 同上（看護師） |
| — | KAKEN: 顎関節症ならびに疲労愁訴を伴う疾患における，AIを用いた筋疲労の定量評価 | 研究課題 | 題名・概要 | AI による筋疲労の定量評価 |
| — | KAKEN: 超音波エコー動画で筋疲労度を判定するAI動画判定システムの開発 | 研究課題 | 題名 | 筋疲労度を判定する AI |
| — | KAKEN: AIを用いた操船者の肉体的疲労を対象とした遠隔アラームシステム | 研究課題 | 題名 | 操船者の肉体的疲労を AI で検知する警報 |
| — | KAKEN: 因果推論と生成AIで切り拓く子育てバーンアウト・周産期うつ予防 | 研究課題 | 題名 | 子育てのバーンアウトの予防に生成 AI を用いる |

★ 2026-09-30: 表の DOI は CiNii Research・J-STAGE の書誌の記録（`evidence/S-12/s12_ja_results_2026-09-29.json`）から足した。Few-Shot と BRUCEE-LI は抄録を取り直して「書いてあること」を足した（repo の外に置いた）。

### 3.3 AI の導入で人の疲労・負担を減らすことを題名・抄録に掲げたもの（6 件）

| 年 | 題名 | 収録先・種別 | 読んだ範囲 | 書いてあること |
|---|---|---|---|---|
| 2026 | 医学教育分野別評価における大規模言語モデルによる判定の量的・質的検証：役割分離に向けた探索的検討 | 医学教育 57(3) doi:10.11307/mededjapan.57.3_195 | 抄録 | 分野別評価の「評価疲れ」への対応として、LLM による評価基準への適合性の判定を人間の判定と比べた（Gwet の AC2 = 0.91）。抄録は、疲労を測ったとは書いていない |
| — | Dataset and Prompts for "Utility of Large Language Models in Medical Education Accreditation: Human-in-the-loop Evaluation Process for Mitigating Evaluation Exhaustion" | Zenodo（データセット）doi:10.5281/zenodo.19479135 | 題名 | 上の論文のデータとプロンプト（と題名から読める） |
| 2024 | 現場を疲弊させる目視検査のすべてをMR空間で支える人間中心型の外観検査AIシステム | 機関リポジトリ（CiNii の種別は Article） | 題名 | 目視検査を支援する AI システム |
| 2022 | 医師の燃え尽きを防ぐ：臨床現場を救うAI活用（医療情報サイト「時事メディカル」より） | 厚生福祉（記事の転載） | 題名 | 医師の燃え尽きを防ぐための AI の活用 |
| 2025 | 店主の右腕AI からあげ!ごっち 唐揚げ店の経営「判断疲れ」支える生成AI | 日経トップリーダー（商業誌の記事） | 題名 | 飲食店の経営者の「判断疲れ」を生成 AI が支える事例 |
| — | KAKEN: 疲労軽減を狙った小型船舶スカイフックキャビンの操作性を回復するAI×VR | 研究課題 | 題名 | 小型船舶のキャビンでの疲労の軽減と、操作性の回復に AI と VR を用いる |

### 3.4 AI と疲労・疲れの語を題名・抄録に含み、上の 3 区分と 3.5 に入らないもの（20 件）

| 年 | 題名 | 収録先・種別 | 読んだ範囲 | 書いてあること |
|---|---|---|---|---|
| 2026 | インタビュー 生成AIの「それっぽい嘘」に疲弊するアカデミア | 公研（雑誌のインタビュー記事） | 題名 | 生成 AI のもっともらしい嘘（題の語）への対応で研究者側が疲弊している、という題のインタビュー。本文は未入手 |
| 2025 | 偽情報・誤情報がむしばむ自律性 | 人工知能学会全国大会論文集 | 抄録 | 関係的自律論から、偽情報・誤情報の広がる情報環境が個人の自律性に与える影響を論じ、「精査疲れ」への対策の必要を主張する（理論的な発表。データの収集は抄録に無い） |
| 2023 | Perplexity・ChatGPT・BingChat 生成AIは優秀で疲れを知らない素晴らしいツール | 授業力&学級経営力（教員向けの雑誌） | 題名 | 生成 AI を「疲れを知らない」道具として紹介 |
| 2022 | インタビュー AIロボと能を舞う：自己をつくる疲労と忘却 | マーケティングホライズン | 題名 | 能楽師へのインタビュー |
| 2024 | 総合健診における人工知能への期待 | 総合健診 | 抄録 | 健診での AI の活用を展望。「機械は疲れることなく」計算を繰り返せる、と述べる |
| 2018 | 人工知能と報道倫理：「フェイクニュース」を中心として | 人工知能学会全国大会論文集 | 抄録 | 「疲れを知らない」AI による偽情報の量産のおそれを論じる |
| 2018 | 健診・人間ドックにおける多職種連携（パネルディスカッション） | 総合健診 | 抄録 | 医療者の疲弊と、人工知能の導入を含む社会環境の変化を論じる |
| 2021 | 自動化した機械操作に対する人間の信頼推定 | ロボティクス・メカトロニクス講演会講演概要集 | 抄録 | 自動化との共有制御での人の信頼（特に不信）を定量的に推定し、不信は自動操作への介入として観察されたと報告。抄録は冒頭で、AI とロボットが人の疲労を軽くしうると述べる |
| 2026 | 生成AIによる観光行動の質的シミュレーションと調査手法の検討 | 日本地理学会発表要旨集 | 抄録 | 生成 AI で観光客の行動を模擬。「スキー後の疲労」は模擬された観光客の判断の要因 |
| 2021 | Al デジタル顔はめパネルを用いた観光プロモーションの提案 | 観光と情報 | 抄録 | 旅行者の「旅行計画疲れ」を背景にした観光プロモーションの提案 |
| 2026 | 長勤を夜勤期間に組み込んだ昼夜遷移の少ない交代制勤務が看護師の睡眠の質に及ぼす影響 | 看護理工学会誌 | 抄録 | 看護師の交代制勤務と睡眠の質・疲労（主観的な睡眠の質と疲労に有意差なし）。抄録の末尾の問答で、勤務表を人工知能で自動作成する技術が今後必要だと述べる |
| 2013 | 認知症の人の情動理解基盤技術とコミュニケーション支援への応用 | 人工知能学会全国大会論文集 | 抄録 | ケアの現場が個別のコミュニケーションに疲弊することを背景に、情動理解の技術を述べる |
| 2024 | 内容分析手法を用いた形態素解析と構文分析及び共起分析の提案 | 日本予防理学療法学会 抄録集 | 抄録 | 仕事と腰痛のツイートの共起分析（「疲労」は抽出された語） |
| 2013 | 足部アーチサポートを目的とした機能靴下の効果 | 理学療法学 Supplement | 抄録 | 立ち仕事の女性の足の疲労と機能靴下 |
| 2013 | 走行疲労に伴う下腿筋活動と足部アーチの関係 | 関東甲信越ブロック理学療法士学会 | 抄録 | 走行による筋の疲労 |
| 2003 | ヒト脳研究を視野に入れた分子プローブ概念の構築と展開 | 反応と合成の進歩シンポジウム | 抄録 | 脳科学の課題として疲労と人工知能を並べて挙げる |
| 2026 | 大規模言語モデル駆動型エージェントによるWebスクレイピング攻撃に対する…資源枯渇による非対称防御 | 人工知能学会全国大会論文集 | 題名 | 計算資源の枯渇（exhaustion）による防御 |
| 2022 | Deterministic and probabilistic wind speed forecasting … | SEATUC J Sci Eng | 抄録 | 風速の予測。「exhaustion」は化石燃料の枯渇 |
| 2019 | Development of Practical Artificial Intelligence System for Drug Discovery … | J Biol Macromol | 抄録 | 創薬。「exhaustion」は従来の標的の枯渇 |
| 2020 | COVID-19 and the New Technologies of Organizing: Digital Exhaust, Digital Footprints, and Artificial Intelligence … | J Management Studies | 題名 | 「digital exhaust」はデジタルの痕跡（データ）の意味 |

### 3.5 CiNii Research の英語の組で当たった、日本の対象者か未確認の英語論文（本節は 3.1〜3.4 と別に数える）

CiNii Research の英語の組（19 件）には、日本の研究機関に限らない英語論文が入っていた。題名に AI の語と疲労の語を含み、上の区分に入らない次の 6 件は、抄録で対象者の国を確かめた（Dizon ほか 2025 は 4.1、ほかの 5 件は 4.2）。

| 年 | 題名 | 収録先 | DOI |
|---|---|---|---|
| 2025 | Technostress and English Language Learning in the Age of Generative AI | The EuroCALL Review | 10.4995/eurocall.2025.23851 |
| 2025 | Privacy fatigue and its effects on ChatGPT acceptance among undergraduate students: is privacy dead? | Education and Information Technologies | 10.1007/s10639-024-13198-6 |
| 2024 | Artificial Intelligence and Radiologist Burnout | JAMA Network Open | 10.1001/jamanetworkopen.2024.48714 |
| 2024 | Ambient artificial intelligence scribes: physician burnout and perspectives on usability and documentation burden | JAMIA | 10.1093/jamia/ocae295 |
| 2024 | Compulsive ChatGPT usage, anxiety, burnout, and sleep disturbance: A serial mediation model based on stimulus-organism-response perspective | Acta Psychologica | 10.1016/j.actpsy.2024.104622 |
| 2023 | AI to the rescue: Exploring the potential of ChatGPT as a teacher ally for workload relief and burnout prevention | Research and Practice in Technology Enhanced Learning | 10.58459/rptel.2024.19023 |

## 4. 英語で書かれた記録（日本の対象者）

### 4.1 日本の対象者で、AI の利用と疲労・燃え尽き・テクノストレスの両方を扱うもの

| 年 | 書誌 | 対象・国 | デザイン | 疲労などの測り方 | 著者が報告した結果 | 読んだ範囲 |
|---|---|---|---|---|---|---|
| 2026 | AI-Echo RCT: Artificial Intelligence-Based Automated Echocardiographic Analysis and the Workflow of Sonographers: A Randomized Crossover Trial. *J Am Heart Assoc*. doi:10.1161/jaha.125.045637（UMIN000053259） | 日本の単一施設（所属は順天堂大学）の超音波検査技師 4 名・患者 585 名 | 日ごとの無作為化クロスオーバー（AI の日 / 手作業の日・38 日） | 副次評価項目: 各勤務日の終わりに、その日の心エコー業務で感じた精神的疲労・身体的疲労を 1 項目ずつ 5 件法で回答（補足資料の Table S3。項目は AI に触れない。ほかに業務の複雑さの 1 項目） | 精神的疲労は AI の日に低い（4.1±1.1 対 4.7±0.6, P=0.039）。身体的疲労（4.0±0.9 対 4.5±0.8, P=0.088）。AI の日は 1 日あたりの検査数が多い（16.7 対 14.1） | 本文（PMC）・補足資料 |
| 2025 | Effects of Long-Term Chatbot System Use on Healthcare Professionals' Professional Identity Formation and Stress: A Small-Scale Comparative Study. *Cureus*. doi:10.7759/cureus.80373 | 日本の看護師・理学療法士 8 名（所属は広島大学） | 無作為に 2 群（利用 4・非利用 4）に分け、約 9 か月追跡（介入の前後とウォッシュアウト後に評価） | 公衆衛生協会ストレスチェックリスト短縮版（PHRF-SCL）の「疲労・身体反応」下位尺度 | 追跡後の群間比較（本文の Table 3）で、疲労・身体反応は利用群が低い（5.5±1.3 対 7.5±0.6, P=0.043, d=0.72）。ベースラインでは差なし。★ 抄録は同じ比較の値を「疲労・身体反応 4.5±0.6 対 7.8±1.3」と書いており、Table 3 では 4.5±0.6 対 7.8±1.3 は「不安・不確実さ」の値である | 本文（PMC） |
| 2025 | Dizon G, Gold J, Barnes R. Technostress and English Language Learning in the Age of Generative AI. *The EuroCALL Review* 32(2). doi:10.4995/eurocall.2025.23851 | 日本の 2 大学の英語学習者 100 名 | 質問紙の混合法 | 生成 AI を使った英語学習でのストレス・使いにくさ・侵入の感覚・いら立ち・複雑さを問う 5 項目（5 件法）と自由記述 3 問（付録）。疲労・消耗を問う項目は無い（burnout の語は先行研究の紹介にだけ出る） | 量的には高いテクノストレスは示されず、自由記述では AI の出力の正確さへの心配が述べられた | 本文（出版社の PDF） |
| 2025 | Crafting TBL Prompts for Classroom Activities that Support Self-Directed Learning in ESP Courses: Medical English Course Example. *JALT PanSIG Journal*. doi:10.37546/jaltpansigj11.1-6 | 日本の大学の医学英語の授業 | 授業実践の報告 | テクノストレスと認知負荷を減らすことを目的に掲げるが、抄録に測定の記述は無い（授業の観察） | — | 抄録 |
| 2026 | ImNavi 試験の計画: Exploring the Impact of an Artificial Intelligence-Based Intraoperative Image Navigation System in Laparoscopic Surgery on Clinical Outcomes: A Protocol … *Eur Surg Res*. doi:10.1159/000549894（2024 年の medRxiv 版 doi:10.1101/2024.08.05.24310603 もある） | 日本の 3 施設（国立がん研究センター東病院ほか）の腹腔鏡下大腸手術 | 多施設の無作為化比較試験の**計画**（AI の術中画像ナビゲーションの使用・不使用を 1:1） | 副次評価項目の 1 つに「主執刀医の術後の疲労」 | 結果はまだ無い（計画の論文） | 抄録 |

★ 日本の対象者で、AI の利用と作業負荷を測ったもの（疲労の尺度ではない）。検索で当たったのではなく、4.2 の Cureus 2026（doi:10.7759/cureus.109247）の参考文献 8 から辿った。

| 年 | 書誌 | 対象・国 | デザイン | 測り方 | 著者が報告した結果 | 読んだ範囲 |
|---|---|---|---|---|---|---|
| 2025 | Omon K, Sasaki T, Koshiro R, Fuchigami T, Hamashima M. Effects of Introducing Generative AI in Rehabilitation Clinical Documentation. *Cureus*. doi:10.7759/cureus.81313 | 大阪の医療法人のリハビリテーション職 12 名 | 前後比較（従来の記録の期間と、生成 AI を使う期間） | NASA-TLX（作業負荷）・記録の時間・記録の質 | 記録の時間に差なし。生成 AI の期間は NASA-TLX の時間的圧迫の得点が低く、記録の質の評価点が上回った | 抄録 |

### 4.2 日本の対象者ではない、または AI の利用者の疲労を扱わないもの（英語の情報源 39 件と 3.5 の 6 件から）

| 書誌 | 抄録・本文に書いてあること |
|---|---|
| Wu Y. 2026. Profiles and transitions of psychological adaptation in AI-assisted Japanese language learning. *Front Psychol*. doi:10.3389/fpsyg.2026.1837484 | 対象は中国本土の公立大学で日本語を学ぶ学生 457 名（日本の対象者ではない）。3 時点の縦断調査。テクノストレス（技術ストレス要因の尺度 22 項目を「AI を使った日本語学習」に向けて書き換え）と、学習の燃え尽き（MBI-SS 15 項目・第 3 時点のみ）を測った |
| Cureus 2026. Implementation of an AI-Assisted Workflow for Rehabilitation Discharge Summary Creation … doi:10.7759/cureus.109247 | 京都の病院のリハビリテーション部門の前後比較。測ったのは記録の作成時間・使いやすさ（SUS）・幻覚（hallucination）と記載漏れの評価で、疲労・燃え尽き・負担感の尺度は本文に無い（燃え尽きは背景の記述だけ） |
| BMC Nursing 2025. Emotional analysis of operating room nurses in acute care hospitals in Japan: insights using ChatGPT. doi:10.1186/s12912-024-02655-9（と Research Square の前刷り doi:10.21203/rs.3.rs-4505331/v1） | 日本の手術室看護師 10 名への面接を、ChatGPT と研究者が分析した。ChatGPT は分析の道具で、看護師が AI を使ったわけではない。★ 抄録（2026-09-30）: 目的に「燃え尽きと離職につながる要因を明らかにする」を掲げる。前刷りも同じ 10 名・同じ期間（2023-02〜2024-02） |
| J Sleep Res 2026. A Participatory AI Driven Shift-Scheduling Application for Improving Sleep Among Shift-Working Caregivers. doi:10.1111/jsr.70144 | 介護職 35 名のクロスオーバー介入。AI が作った勤務表と手作業の勤務表を比べ、睡眠を指輪型の計測器で測った。★ 抄録（2026-09-30）: 勤務表の改善の必要（逆回りの交代を避けるなど）は、職業上の疲労の相談から導いた。深い睡眠とレム睡眠が介入の条件で多かった |
| Sensors 2025. Context-Aware Alerting in Elderly Care Facilities … LLM Reasoning with Rule-Based Logic. doi:10.3390/s25216560 | 介護施設の通知を LLM で絞る仕組み。測ったのは通知の量と判定の精度で、看護職の疲労は測っていない。★ 抄録（2026-09-30）: 目的に「アラーム疲労を減らす」を掲げる。入居者 28 名・看護職 4 名・7 日の実地の実験で、通知の量は 27.5% になった |
| RAMS 2026. Human Reliability Analysis for Repetitive Tasks … Human-AI Teaming. doi:10.1109/RAMS50514.2026.11424510 | 日本の原子力施設の点検の事例で、反復作業の認知的疲労を人間信頼性解析でモデル化。★ 抄録（2026-09-30）: Phoenix の手法で、繰り返しによる認知的疲労と注意の逸れが人の過誤の確率に及ぼす影響を扱い、反復作業への AI による解決の可能性と課題を論じる |
| BMJ Open 2023. Effect of multimodal comprehensive communication skills training with video analysis by artificial intelligence for physicians on acute geriatric care … doi:10.1136/bmjopen-2022-065477 | 日本（所属は東京医療センター）の医師へのコミュニケーション技能の研修。AI は研修の前後の面接の動画を分析する道具で、副次評価項目に医師の燃え尽きの得点がある |
| Liu H ほか 2024. Artificial Intelligence and Radiologist Burnout. *JAMA Netw Open*. doi:10.1001/jamanetworkopen.2024.48714 | 中国の放射線科医の調査（日本の対象者ではない） |
| Duong CD ほか 2024. Compulsive ChatGPT usage, anxiety, burnout, and sleep disturbance … *Acta Psychologica*. doi:10.1016/j.actpsy.2024.104622 | ベトナムの ChatGPT の利用者 2,602 名の横断調査（構造方程式モデリング・日本の対象者ではない）。強迫的な ChatGPT の利用 → 不安・燃え尽き → 睡眠障害の経路 |
| Chung J, Kwon H 2025. Privacy fatigue and its effects on ChatGPT acceptance … *Educ Inf Technol*. doi:10.1007/s10639-024-13198-6 | 韓国の大学生の調査（日本の対象者ではない） |
| Hashem R ほか 2023. AI to the rescue … *RPTEL*. doi:10.58459/rptel.2024.19023 | 中等学校の教員の負担軽減と燃え尽きの予防に ChatGPT が役立つかを調べた。抄録は UAE の AI 統合の目標に触れる（日本の対象者ではない） |
| Shah SJ ほか 2024. Ambient AI scribes … *JAMIA*. doi:10.1093/jamia/ocae295 | 米国（Stanford Health Care）の医師 48 名（日本の対象者ではない） |
| そのほか 25 件 | 日本の語が別の文脈（例: アニメ・橋梁・日本の有害事象データベース）で出るもの、AI が道具として疲労・燃え尽きを検知・予測するもの、総説・論説など。一覧は `evidence/S-12/s12_en_results_2026-09-29.json` |

⚠️ 4.2 の国の記述は、抄録と著者の所属（Europe PMC・Crossref・Semantic Scholar）で確かめた（Liu 2024 = 中国・Duong 2024 = ベトナム・Chung 2025 = 韓国・Shah 2024 = 米国・Hashem 2023 = 抄録の記述だけ）。本文は読んでいない。

### 4.3 4.2 の「そのほか 25 件」から、1 件ずつの行に起こしたもの（2026-09-30）

★ 2026-09-30 に、25 件の抄録を取り直して読み、AI が人の疲労を検知・分類する研究の 2 件を 1 件ずつの行にした（残りの 23 件の内訳は `../20260930-ai-fatigue-candidates-appraisal/decisions.md` 判断 3）。抄録は repo の外に置いた。

| 書誌 | 抄録に書いてあること |
|---|---|
| Han J, Qian K, Song M ほか 2020. An Early Study on Intelligent Analysis of Speech under COVID-19: Severity, Sleep Quality, Fatigue, and Anxiety. arXiv（Europe PMC の前刷りの記録 PPR268625・DOI の記録なし） | COVID-19 と診断された患者の音声から、病気の重さ・睡眠の質・疲労・不安の 4 つの面を自動で分類するモデルを作った（2 種の音響特徴量とサポートベクターマシン）。病気の重さの推定の平均の正解率は .69 |
| Qian K, Schmitt M, Zheng H ほか 2021. Computer Audition for Fighting the SARS-CoV-2 Corona Crisis: Introducing the Multitask Speech Corpus for COVID-19. *IEEE Internet of Things Journal*. doi:10.1109/jiot.2021.3067605 | 武漢の COVID-19 の患者 51 名の音声の資料を作り、睡眠の質・疲労・不安の 3 区分の分類の課題を定めて、従来の機械学習と深層学習の基準値を示した |

## 5. KAKEN の研究課題（CiNii Research の projects で当たった 11 件）

3.2 の 6 件（AI が疲労・燃え尽きを測る・検知する、または子育てのバーンアウトの予防に生成 AI を使う）・3.3 の 1 件（スカイフックキャビン）・3.1 の 2 件（疲労破損事例データベース・SMA と AI の長寿命構造体）のほか、負担の語の組で当たった次の 2 件（題名ふるいは通っていない）。

| 題名 | 研究代表者 | 当たった組 |
|---|---|---|
| 大規模言語モデルを用いた介護スタッフの作業負荷予測と最適人員配置システムの開発 | 軽部 幸起 | 狭い AI の語 × 負担の語 |
| 生成AI活用による教員の授業負担軽減に関する実証的研究 | 山本 堅一 | 狭い AI の語 × 負担の語 |

## 6. 数のまとめ

- 日本語の情報源: 実行した検索 188 本（J-STAGE 140・CiNii Research 6・国立国会図書館サーチ 42。J-STAGE の全文の比較 2 本を除く）→ 取得 457 件（重複を除く前）→ ふるいの通過 75 件（重複を除いた後）＝ 材料・構造物 30／AI が人の疲労を測る・検知する道具 13／AI で疲労・負担を減らすことを掲げる 6／そのほか 20／CiNii の英語の組の英語論文 6（3.5）。
- 英語の情報源（日本の対象者）: 検索 4 本（うち OpenAlex の 1 本は使えなかった）→ 39 件（重複を除いた後）→ 日本の対象者で、AI の利用と疲労・燃え尽き・テクノストレスの両方を扱うもの 5 件（4.1・計画の論文 1 件を含む）。ほかに引用から辿った 1 件（作業負荷）。
- 日本語で書かれ、題名または抄録に「AI を使う人の疲労を測った」と書いてある記録: 0 件（ふるいを通った 75 件の題名・抄録の範囲。3.3 の雑誌の記事などは題名だけを読んだ。本文は読んでいない）。
