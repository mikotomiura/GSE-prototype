# RQ E サーヴェイ報告: 写像規則の層 と 許容条件の層 の「二層接続」に先行はあるか

## 1. 動機

★ 本ラウンドは前ラウンド (RQ: 表現変換理論) からの **持ち越し課題** である。前ラウンドで「既存の写像代数 (Grammar of Graphics / Vega-Lite composition algebra / AVD) はすべて graphical integrity 型 (忠実性) の条件しか持たない」「許容条件の *内容* (断定しない/罰として描かない等) は Gaver・Bodner & Prelec・Barrass & Vickers に先行がある」という 2 点が確定した。残った唯一の新規性候補は **「写像規則の層」と「許容条件の層」を明示的に分離した二層構造そのもの** であり、本ラウンドはこれを可視化・ソニフィケーション・他分野 (PL理論・OS設計・AI安全性・行動変容技術) を跨いで検証した。

## 2. 検証状態

- 探索 angle: (a)(b)(c)(d)(e) の 5 系統 + メインから追加供与された 1 件 (Roddy & Bridges 2020 の判定)。
- ソース数: 21 件を登録候補として記録 (一次全文確認 4 件: Draco 2019 / Hydra 1975 / Mohammad 2022 Ethics Sheet / Roddy & Bridges 2020 AAM。残りは二次資料水準または産業文書)。
- claim 数: 7 件 (A〜G)。confirmed 6 件 (3-0 が 5 件、2-1 が 1 件)、否決 4 件 (0-3 が 3 件、1-2 が 1 件)。

## 3. gate 判定 (要点先出し)

| 下位問い | 温度 |
|---|---|
| (a) 可視化/ソニフィケーションで写像仕様と制約判定を分離した枠組みがあるか | **確定・存在する** (Draco が最も明示的。ソニフィケーションでは概念止まりで不成立) |
| (b) Draco 型の制約は有効性型か規範型か | **確定・有効性型** (expressiveness = 表現可能性の妥当性、soft constraint = 知覚実験由来の効果性選好。規範的内容ゼロ) |
| (c) 他分野に同型の構造 (生成層 + 直交する許容判定層) があるか | **確定して存在する** が、GSE の内容 (自己向け・心理的節度) と一致する例は **判定不能に近い PLAUSIBLE BUT UNPROVEN** |
| (d) アンビエント表現・行動変容技術で設計ガイドラインを生成規則と別の層として "形式化" した例 | **見つからず** (ドキュメント/チェックリスト止まりが最良で、計算的に直交適用される層は不在。ただし条件を落とすと埋まる — §8 の表) |
| (e) 反証 (分離が実は成立しない/有害だった) | **確定・複数の独立した反証が収束** |

## 4. ★★★ Draco (および同型の制約ベース枠組み) の一次判定

`docs/references.md` には未登録。以下は `C:/Users/johnd/AppData/Local/Temp/claude/C--GSE-prototype/6ac75a36-e681-44fa-9f35-58298165bdac/scratchpad/pdfs/draco2019.pdf` (Moritz, Wang, Nelson, Lin, Smith, Howe, Heer, *"Formalizing Visualization Design Knowledge as Constraints: Actionable and Extensible Models in Draco"*, IEEE TVCG 25(1):438–448, 2019, `doi:10.1109/TVCG.2018.2865240`) を pypdf で全文抽出し、逐語で判定した結果 (**一次確認済み**)。

> "We present Draco, a formal model that represents visualizations as sets of logical facts and represents design guidelines as a collection of hard and soft constraints over these facts. [...] To represent design knowledge, we contribute a set of extensible constraints that can encode **expressiveness criteria** [37], **preference rules validated in perception experiments**, and general visualization design best practices."

> "Hard constraints must be satisﬁed (e.g., shape encodings cannot express quantitative values), whereas soft constraints express a preference (e.g., temporal values should use the x-axis by default)."

> Fig.3 のキャプション: "Draco eliminates **ill-formed or non-expressive** speciﬁcations using hard constraints and encodes **preferences** using soft constraints."

**判定**: hard constraint は「その視覚言語がデータを正しく (過不足なく) 表現できるか」という **表現可能性 = 忠実性系の妥当性判定**、soft constraint は「知覚実験で検証された、より速く/正確に読めるかという **効果性の選好**」である。索引語も *"Index Terms—Automated Visualization Design, **Perceptual Effectiveness**, Constraints, ..."* と明記されている。**規範的 (してはならない) 制約は現行モデルに存在しない。**

唯一 GSE 的な語彙に近づくのは §7.2 の展望節のみである:

> "Draco might also explain those violations and why they matter, to teach students or visualization designers about best practices, help them spot (intentionally or unintentionally) **misleading visualizations**, critique visualizations, ..."

これは **未実装の将来拡張の一文** であり (「could」「might」という叙法、現行の ASP 制約セットには存在しない)、かつ「教育用スペルチェッカー」という用途であって、「本人の内的状態の表現に対する節度」という GSE の許容条件とは対象も内容も別物である。

**結論: Draco は (a) の意味で「写像仕様 + 制約判定」の二層分離を極めて明示的に実装している (3-0 confirmed) が、(b) の意味でその制約は一貫して有効性型であり、GSE が求める規範型の許容条件を一切含まない (3-0 confirmed)。したがって Draco は GSE の新規性を消さない。** ただし **(a) の「二層分離という操作それ自体」は可視化分野で 2019 年時点で確立済みの手法であり、GSE がこの操作パターンを発明したとは書けない** — この点は §7 の結論で扱う。

### 参考: 姉妹分野 (ソニフィケーション) での「層」の扱い

メインから供与された一次資料 (Roddy, S. & Bridges, B., *"Mapping for meaning: the embodied sonification listening model and its implications for the mapping problem in sonic information design"*, Journal on Multimodal User Interfaces 14(2):143–151, 2020, `doi:10.1007/s12193-020-00318-y`, Ulster University 機関リポジトリの Author Accepted Manuscript を一次確認) を自分でも通読し、独立に 3 票判定した。

逐語 (§3.1):
> "Sonification designers are broadly aware that they must work within the limits of human perception and that **psychoacoustic constraints** have a very large impact on how we represent data to a listener using sound. Furthermore, [...] we must account for the **cognitive constraints** of the listener [...]. Embodied cognition suggests that there is both **another layer of constraints** for which we must account and another layer of possibilities that we can exploit in the design of effective sonification..."

**票1 (内的妥当性)**: 逐語は正確、文脈もメイン供与のものと一致。confirmed。
**票2 (類推妥当性)**: この「層」は psychoacoustic → cognitive → embodied という **知覚・認知的な到達可能性/解釈可能性の制約の積み増し** であり、写像戦略の設計プロセス**の内部で**考慮される一枚岩の設計上の考慮事項として書かれている (直後で ESLM という単一モデルに統合される)。GSE が求めるのは「写像規則」と「それとは独立に、生成された表現を審査する層」の **アーキテクチャ上の分離** であるが、ESLM にはこの分離がない — 制約は「意味を汲み取れるか」という有効性型であり、「その意味を本人にどう返してよいか」という規範型ではない。reject (この claim を「二層分離の先行例」として支持する用途では)。
**票3 (頑健性)**: 論文自身が "This is a theoretical paper" と明言し、全文で `empirical` が 0 回、実装・検証が一切ない。理論的一提案の域を出ない。reject。

**結論: 0-3 で否決。ESLM の「another layer of constraints」は RQ E が問う二層分離には該当しない。** メインの暫定読み (該当しない) と一致する。これは (a) の判定において「可視化では二層分離が確立しているが、ソニフィケーションでは (少なくとも本論文単体では) 未成立」という非対称性の追加証拠になる。

## 5. カード (落合フォーマット、6 項目)

### [検証済 3-0] Draco: 制約ベース可視化推薦の形式化
1. **どんなもの**: 可視化設計知識を ASP 上の hard/soft constraint として形式化し、Vega-Lite 仕様の探索・ランキングに使う。
2. **先行研究と比べてどこがすごい**: APT/Show Me の expressiveness/effectiveness を、拡張可能・学習可能な制約集合として一般化した。
3. **技術・手法の肝**: hard constraint (妥当性の enumeration) と soft constraint (学習された重み付き選好コスト) の分離。Clingo で解を探索。
4. **どう有効と検証したか**: CompassQL の再実装 + 知覚実験データからの learning-to-rank で重み学習。
5. **議論はあるか**: 著者ら自身が「'optimal' は "correct" な設計を意味しない」と明言 — 効果性の相対順位付けであって規範的正否ではない。
6. **次に読むべき論文**: Draco 2 (Yang et al. 2023)、Visual Analytics for Understanding Draco's Knowledge Base (Schmidt et al. 2023)。

**GSE への含意**: Draco は「写像+判定層」の分離を提示するが、判定層の中身は忠実性/効果性であり、GSE の許容条件 (自己向け節度) とは種類が違う。GSE が主張できるのは「同じアーキテクチャ操作を、別の内容の判定層に対して行った」という点に限られる。

### [検証済 3-0] Hydra: Policy/Mechanism Separation (1975)
1. **どんなもの**: OS カーネルを「mechanism のみ」に限定し、資源配分の「policy」をユーザレベルへ追い出す設計原則。
2. **先行研究と比べてどこがすごい**: 「何ができるか」と「何をすべきか」を初めて明示的な設計原則として分離した古典。
3. **技術・手法の肝**: scheduling/paging/protection の 3 例で mechanism ↔ policy の境界を実演。
4. **どう有効と検証したか**: C.mmp 上の実装 + 3 メカニズムのケーススタディ。
5. **議論はあるか**: ★ 著者ら自身が逐語で認めている: "it is impractical to invoke such programs each time a policy decision is required. Thus, **we compromise**." さらに: "Clearly, then, **the kernel is not devoid of policy**, yet the policy/mechanism distinction does not break down". Summary でも "although **not all policies are possible**... several known shortcomings have been identified" と明記。
6. **次に読むべき論文**: Infokernel (Arpaci-Dusseau et al. 2003) — 「policy/mechanism は連続体であり離散的分離は成立しない」と正面から批判。

**GSE への含意**: 「生成層と判定層を分離する」という *操作そのもの* は 1975 年に確立された一般原則であり、GSE 独自の発明ではない。同時に、この原始文献自身が「完全な分離は妥協であり漏れる」と認めている点は、GSE が二層を設計する際の反証的な留保材料になる。

### [検証済 3-0] Mohammad (2022) Ethics Sheet for AER
1. **どんなもの**: 自動感情認識/感情分析タスクについて、50 項目の倫理的考慮を列挙した「シート」。Datasheets for Datasets / Model Cards と同系統の文書実践。
2. **先行研究と比べてどこがすごい**: AI Ethics と Emotion Recognition の知見を単一タスク粒度で体系化した最初期の例。
3. **技術・手法の肝**: 「シート」は設計前に参照するチェックリストであり、モダリティ・タスク定式化・データセット・影響の 4 セクション。
4. **どう有効と検証したか**: 実証なし (規範的統合論文)。著者自身「単一の権威あるシートを作ることが目的ではない」と明言。
5. **議論はあるか**: 全文 grep で `back to the`, `self-track`, `feedback to the user` 等の「本人向けフィードバック」表現は **0 件**。想定読者は「研究者・エンジニア・規制当局」であり、GSE が扱う「推定した本人自身にどう返すか」という場面は対象外。
6. **次に読むべき論文**: Datasheets for Datasets (Gebru et al.)、Model Cards (Mitchell et al.)。

**GSE への含意**: 感情認識倫理の最有力文献ですら、「本人向けの表現の節度」を主題化しておらず、かつ形態も「実行時に直交適用される計算層」ではなく「設計前のドキュメント」である。GSE の位置 (自己向け・実行時の判定層) はここでも空いている。

### [検証済 2-1] NeMo Guardrails / Constitutional AI: 生成に直交する規範層 (留保: 対象読者が違う)
1. **どんなもの**: NeMo Guardrails は Colang で書いた "rails" (トピック/実行/モデレーション) を LLM 生成の前後に挿入するランタイム層。Constitutional AI は「憲法」(原則リスト) による自己批判・改訂を生成モデルから分離する。
2. **先行研究と比べてどこがすごい**: 規範的判定 (何を言ってよいか) を生成プロセスから明示的に切り出し、独立に差し替え可能にした。
3. **技術・手法の肝**: input rails → 生成 → output rails という直交構造 (NeMo)。Constitutional AI は helpfulness (人間ラベル) と harmlessness (AI 自己評価) を別プロセス化。
4. **どう有効と検証したか**: NeMo は arXiv デモ論文でトイ実装評価。Constitutional AI は RLHF ベンチマークで harmlessness/helpfulness を計測。
5. **議論はあるか**: ★ 反証あり — "Bypassing OpenAI's Guardrails" 等の研究は、生成器と判定器が同一基盤 (同種のモデル) を共有する場合、両者が同時に破られる "self-policing" 脆弱性を報告 (SoK: Evaluating Jailbreak Guardrails, arXiv:2506.10597 ほか)。分離は名目上のものに留まりうる。
6. **次に読むべき論文**: SoK: Evaluating Jailbreak Guardrails for LLMs。

**GSE への含意**: 制約の *内容* (規範的・してはならない) は GSE に最も近い。しかし対象読者が「不特定多数への任意テキスト生成」であり、GSE の「推定した本人自身に、その人の内的状態を返す」という一人称的な場面ではない。票2 (類推妥当性) は 2-1 (1 票は「対象の違いは大きいが、'生成に対して規範層を直交適用する' という構造それ自体の先行としては十分」として confirmed、1 票は「対象・利害関係者構造が違いすぎ、GSE への転用は無理筋」として反対) — 留保付き confirmed として記録する。

## 6. 登録候補一覧

| 仮key | 出典 | 分離しているもの | 制約の種類 | 1 行の意味 | 確認水準 |
|---|---|---|---|---|---|
| draco2019 | Moritz et al., TVCG 25(1):438–448, 2019, doi:10.1109/TVCG.2018.2865240 | Vega-Lite写像仕様(ASP facts) / hard+soft constraint | 有効性 (表現可能性+知覚効果性) | 可視化知識をASP制約として形式化し二層分離を明示実装 | **一次確認済み** |
| draco2-2023 | Yang et al., IEEE VIS 2023, arXiv:2308.14247 | 同上を拡張 | 有効性 | Dracoの知識ベースを可視分析可能に拡張 | 二次資料水準 |
| apt1986 | Mackinlay, ACM TOG 5(2):110–141, 1986, doi:10.1145/22949.22950 | composition algebra / expressiveness+effectiveness criteria | 表現可能性(妥当性)+知覚効率(有効性) | 可視化を文としてとらえ言語の妥当性と効果性を分離 | 二次資料水準 |
| showme2007 | Mackinlay, Hanrahan, Stolte, TVCG 13(6):1137–1144, 2007, doi:10.1109/TVCG.2007.70594 | VizQL仕様 / automatic presentation rules(importance ordering) | 有効性 | Tableauへ自動プレゼンテーションを統合、UX重視 | 二次資料水準 |
| voyager2015 | Wongsuphasawat et al., TVCG 2015, doi:10.1109/TVCG.2015.2467191 | 部分仕様 / 推薦ランキング | 有効性 | ファセット閲覧型の可視化推薦 | 二次資料水準 |
| hydra1975 | Levin, Cohen, Corwin, Pollack, Wulf, SOSP 1975, pp.132–140, doi:10.1145/800213.806531 | kernel mechanism / user-level policy | 資源配分方針(効率・公平性、規範ではない) | policy/mechanism分離を設計原則として提示、かつ自ら漏れを認める | **一次確認済み** |
| infokernel2003 | Arpaci-Dusseau et al., SOSP 2003, doi:10.1145/945445.945455 | (批判対象) policy/mechanism | 同上への批判 | 分離は連続体であり離散的境界は成立しないと主張 | 二次資料水準 |
| opa-doc | Open Policy Agent / Rego 公式文書 (openpolicyagent.org, 産業文書・査読なし) | アプリロジック(実行) / Regoポリシー(PDP) | 規範的(認可の可否) だが対象は行為許可 | policy-as-codeの現代的PDP/PEP分離 | 二次資料水準・grey literature |
| nemo2023 | Rebedea et al., EMNLP 2023 Demo, arXiv:2310.10501 | LLM生成 / Colang rails(トピック・実行・モデレーション) | 規範的(禁止トピック・安全性) | ランタイムで生成に直交する規範層を挿入 | 二次資料水準 |
| constitutionalai2022 | Bai et al., arXiv:2212.08073, 2022 | 生成モデル / 憲法(原則リスト)による自己批判評価 | 規範的(無害性) | 憲法をhuman-feedbackから独立させたharmlessness学習 | 二次資料水準 |
| liquidtypes2008 | Rondon, Kawaguchi, Jhala, PLDI 2008, doi:10.1145/1375581.1375602 | 型(実装) / 論理述語refinement(検証条件) | 正当性(安全性証明、規範ではない) | SMTベースの精緻化型で仕様と実装を分離 | 二次資料水準 |
| refinement2026 | Bovel, arXiv:2605.08369 | (反証寄り) refinement層を型検査器へ再統合する潮流 | 正当性 | 「別レイヤーとしての精緻化」から統合への回帰 | 二次資料水準 |
| mohammad2022 | Mohammad, Computational Linguistics 48(2):239–278, 2022, doi:10.1162/coli_a_00433, arXiv:2109.08256 | AER構築実践 / 倫理シート(ドキュメント) | 規範的(50項目) だが本人向けフィードバック場面は対象外 | 感情認識タスクの倫理チェックリスト、計算層ではない | **一次確認済み** |
| vsd-friedman | Friedman et al., UW CSE Tech Report 02-12-01, 2002 ほか | conceptual/empirical/technical investigations (意図的に非モジュール) | 規範的(価値) | 価値を別レイヤーとして切り離さない設計論を明示的に主張 | 二次資料水準 |
| darkpatterns-gray2018 | Gray, Kou, Battles, Hoggatt, Toombs, CHI 2018, doi:10.1145/3173574.3174108 | UI生成 / 事後的タクソノミー(5類型) | 規範的(操作性の倫理類型) | ダークパターンの人手分類、生成層への直交適用ではない | 二次資料水準 |
| darkpatterns-mathur2019 | Mathur et al., PACM HCI (CSCW) 3, Art.81, 2019, arXiv:1907.07032 | 同上、大規模クロール分析 | 規範的 | 11K ECサイトの実証的ダークパターン分類 | 二次資料水準 |
| aidui2023 | "AidUI", arXiv:2303.06782, 2023 | UI生成 / CV/MLベースの自動検出器 | 規範的(操作的パターン検出) | 検出は計算的・直交適用に近いが対象は他者向けEC UI | 二次資料水準 |
| pousmanstasko2006 | Pousman & Stasko, AVI 2006, pp.67–74, doi:10.1145/1133265.1133277 | (否決) アンビエント表示のタクソノミー | N/A | 分類記述であり判定層ではない | 二次資料水準・**否決** |
| froehlich2010 | Froehlich, Findlater, Landay, CHI 2010, pp.1999–2008, doi:10.1145/1753326.1753629 | (否決) エコフィードバック設計原則 | N/A | 設計時ガイドライン集、実行時の判定層ではない | 二次資料水準・**否決** |
| sok-jailbreak2025 | "SoK: Evaluating Jailbreak Guardrails for LLMs", arXiv:2506.10597 | (反証) guardrails層の実効的独立性 | 規範的判定の頑健性への反証 | 敵対的圧力下でrails/生成の分離が崩れる | 二次資料水準 |
| roddybridges2020 | Roddy & Bridges, J. Multimodal User Interfaces 14(2):143–151, 2020, doi:10.1007/s12193-020-00318-y | (否決・単一層) 写像設計プロセス内の知覚/認知/身体化制約 | 有効性(解釈可能性) | 「another layer of constraints」は直交する規範層ではない | **一次確認済み (AAM版・post-peer-review pre-copyedit)** |

## 7. 否決リスト

- **Pousman & Stasko (2006) を「アンビエント表示における生成規則と別の判定層」の先行例とする主張** — 0-3 否決。理由: taxonomy は事後的な分類記述であり、生成過程に適用される許容条件的判定ではない。Weiser の calm technology からの「分離」も研究アプローチの相違であって二層アーキテクチャではない。
- **Froehlich et al. (2010) のエコフィードバック設計原則を「規範層の形式化」とする主張** — 0-3 否決。理由: 33 件の原則は設計時チェックリストであり実行時に計算的に適用される層ではない。また「罪悪感を煽らない」という個別規範が Froehlich 自身の文書に明記されているかは本ラウンドで一次確認できず、実証研究 (guilt/pride の効果測定) との混同に留まった。
- **OPA/Rego 型 PDP/PEP 分離だけで GSE の二層接続の新規性が消えるとする強い主張** — 1-2 で否決 (留保)。理由: 分離の一般構造は同型だが、対象 (行為の許可/拒否) と内容 (アクセス制御規則) が GSE (自己向け内的状態表現の心理的節度) と異なりすぎるとする票が 2 対 1 で優勢。
- **Roddy & Bridges (2020) ESLM の "another layer of constraints" を二層分離の先行例とする主張** — 0-3 否決 (§4 参照)。単一プロセス内部の知覚・認知的制約の積み増しであり、直交する規範層ではない。理論のみで実証ゼロ (`empirical` 0 件)。

## 8. 結論

**判定: (ii) 部分的に先行がある。**

**埋まっている部分**: 「写像・生成の規則を記述する層」と「その結果を判定する別の層」を明示的に分離するという **一般的な構造上の操作** は、GSE の発明ではない。可視化分野では Draco (2019) がまさにこの分離を ASP hard/soft constraint として実装済みであり (§4)、より広く見れば OS 設計の policy/mechanism separation (Hydra, 1975) という 50 年前の一般原則の一事例に過ぎない。AI 安全性分野の guardrails/Constitutional AI も同型の構造を持つ (§5)。したがって「二層に分ける」という操作それ自体を GSE の新規性として主張することはできない。

**埋まっていない部分**: 調査した範囲では、この二層分離を **(1) 判定層の内容が有効性/忠実性/他者向け安全性ではなく「推定された本人の内的状態を本人自身に返す際の心理的節度」であり、かつ (2) その判定層が生成過程に対して実行時に直交適用される計算可能な層として実装されている** という **両条件を満たす例** は見つからなかった。近い候補はいずれかの条件で外れる: Draco/APT/Show Me/Vega-Lite は (1) で外れる (有効性型)。NeMo Guardrails/Constitutional AI/OPA は (1) の規範性は満たすが対象が「自己向け」ではなく「他者向け」で外れる。Ethics Sheet/VSD/dark patterns taxonomy は内容は近いが (2) で外れる (ドキュメント/事後分類であり実行時の直交層ではない)。むしろ VSD は意図的に層のモジュール分離を否定している。

**この残余ギャップが「先行ゼロ」の誤った確定に陥っていないことを示すため、条件を 1 つずつ落とした表を示す** (rule 0-5 の要求に沿い、部分先行の場合にも適用):

| 落とす条件 | 埋まるか | 埋める例 |
|---|---|---|
| (なし・全条件) | 埋まらない | — |
| (1) 内容が規範型でなくてよい (有効性型でも可) とする | **埋まる** | Draco (§4)、APT/Show Me |
| (2) 対象が自己向けでなくてよい (他者向けでも可) とする | **埋まる** | NeMo Guardrails、Constitutional AI、OPA/Rego |
| (3) 実行時の計算層でなくてよい (設計時ドキュメントでも可) とする | **埋まる** | Mohammad (2022) Ethics Sheet、VSD、dark patterns taxonomy |
| (4) 二層の「分離」自体を問わず、単一プロセス内の考慮でもよいとする | **埋まる** | Roddy & Bridges (2020) ESLM |
| (5) 実証は不要 (理論提案のみでよい) とする | 変化なし (上記の分岐は (1)(2)(3) で決まり実証の有無は独立) | — |

→ **空白は (1)(2)(3) の "組み合わせ" によって作られている**のであり、単一条件のせいではない。したがって「GSE の許容条件層の位置づけ」が新規性を持ちうるとすれば、それは「二層分離」という操作の発明にではなく、**この特定の 3 条件 (規範型内容 × 自己向け対象 × 実行時直交層) の組み合わせを埋めた点** に限定される、という記述が最も正確である。

**代わりに何が残るか**: GSE が独自性を主張できる範囲は狭くなった。(i) 「二層に分ける」という設計操作自体は既知。(ii) 許容条件の *内容* も前ラウンドで Gaver/Bodner & Prelec/Barrass & Vickers に先行がある。残るのは **「その内容を、その対象 (自己向け) に対して、その実装形態 (生成に直交する実行時層) で接続した」という具体的な統合そのもの**である。これは理論的新規性としては弱いが、**工学的コントリビューション (何を組み合わせてどう実装したか)** として書くのが誠実な位置づけになる。

## 9. やり残し

- (c) の NeMo Guardrails / Constitutional AI について、一次全文を未確認 (要旨・二次資料水準に留まる)。特に Constitutional AI の "harmlessness" 原則リストの逐語に GSE の許容条件と重なる項目 (誇張・断定・操作の禁止等) がないか、一次で確認する価値がある。
- OPA/Rego は査読論文ではなく産業文書のため、`docs/references.md` への登録可否をメイン判断が必要 (grey literature の扱い規約次第)。
- VSD (Friedman et al.) の「非モジュール化」主張は要約止まり。原論文 (UW CSE Tech Report 02-12-01 または Value Sensitive Design and Information Systems 章) を一次で確認し、「モジュール分離を明示的に拒否した」という逐語を取ることが望ましい。
- Froehlich et al. (2010) のエコフィードバック原則が「罪悪感を煽らない」ことに触れているか未確認 (§7 で否決した理由の一部)。一次を取れば (d) の判定が変わる可能性がある。
- 本ラウンドは (d) で「見つからず」寄りの結論になったが、対象を「行動変容技術」に広げず「デジタルウェルビーイング (screen time nudge)」や「持続可能性ナッジの倫理層」等、まだ触っていない angle が残っている。
