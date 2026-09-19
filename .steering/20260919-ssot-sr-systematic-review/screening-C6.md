# ふるい分けの記録 —— C6

> 候補の定義（protocol.md §1）: **非再捕捉: 利用者の応答（受諾・拒否・訂正）を、成功として学習・評価・報酬へ戻さないこと**
> 生成: `$CLAUDE_JOB_DIR/tmp/sr/gen_screening.py`（段 1 / 段 2 の JSONL と、メインの訂正 `verify/notes.md` から）。

## 件数

| 段 | 件数 |
|---|---|
| 検索（重複除去の後） | 689 |
| 段 1 で採った | 11 |
| 段 1 で逆向きの主流として記録した（`contrary`） | 214 |
| 段 2 で照合した（版違いは 1 件にまとめた） | 11 |
| 段 2 の判定（メインの訂正の後） | 該当 1 ／ 部分 1 ／ 非該当 9 |
| 段 2 未実施（★ 逸脱 2: 結論の確定後に打ち切り） | 0 |

## 結論

★ **既出**（該当: C6-0113 [P404]。⚠️ [P404] は最適化（成功の側）を退けるが、控える側での利用には触れない。★ 控える側にだけ使う対は SR の候補ではなく網も狙っていない → 差分の候補（未検証）—— RP §4・2026-09-19 訂正）

## 段 2 の判定

| sid | 判定 | 本文 | 逐語（先頭） | 位置 | 要素 | メインの訂正 | 照合 |
|---|---|---|---|---|---|---|---|
| C6-0113 | 該当 | 本文 | In no uncertain terms, we do not advocate for the optimization of user feedback – if anything, we hope our work provides evidence against its usage. | Ethics Statement（★ 2026-09-19 メイン訂正: 段 2 担当は「Discussion」） | 「利用者フィードバックを最適化目標（学習・報酬）にすることへの明示的な反対表明」は該当する。ただし対象は受諾・拒否・訂正という具体的な応答種別ではなく汎用的な user feedback（例: thumbs up）であり、著者自身は実証実験としてRLで実際にフィードバックを報酬化して有害性を示した上での勧告にとどまり、「戻さない」を組み込んだ具体的な設計要件・アーキテクチャは提案していない。よって… | 段 2 担当は「部分」→ メインが上げた（フィードバックを成功の報酬として最適化へ戻すことを退ける） | ★ メインが本文で照合 |
| C6-0612 | 部分 | 本文 | Despite the advantages of user feedback, their responses remain transient and lack persistence across interaction sessions. This is attributed to the inherent characteristics of generative AI models, which require explic… | Abstract | 利用者の「訂正」(コード修正フィードバック)を生成AIモデルの再学習(re-training)へ「戻さない」ことは逐語で明確(要素: 応答の種類=訂正、戻さない対象=学習)。ただし『成功として』という評価の枠付けや、報酬(reward)への言及は本文中に無く(re-training以外は不言及)、評価・報酬の要素は確認できないため『部分』とした。なお提案手法は訂正を外部メモリ(correction… |  | メインが抄録・取り出したテキストと機械照合 |
| C6-0123 | 非該当 | 本文 |  |  | 非該当。本論文はユーザーの評価（フィードバック）履歴を推薦モデルの学習に使い続けることを前提とし、その際に生じる選択バイアス（user feedback-loop bias）を逆確率スコアリング（IPS）で補正する手法を提案するもの。C6が求める「応答を学習・評価・報酬へ戻さない」という要件とは逆に、応答（評価）を訓練データとして使い続ける（バイアス補正のみ行う）立場であり、定義のどの要素も満たさ… |  |  |
| C6-0154 | 非該当 | 抄録のみ |  |  | 非該当。抄録によれば本研究は「ユーザーフィードバックが得られた際にシステムをどう改善するか」を理論化するもので、フィードバックは内部状態の更新（＝学習）に使われることを明示的なモデル化の対象としている。C6が求める「応答を学習・評価・報酬へ戻さない」の逆で、フィードバックを学習に戻すこと自体を理論的に定式化した研究であり、定義の要素を満たさない。 |  |  |
| C6-0200 | 非該当 | 抄録のみ |  |  | 抄録本文を逐語で確認できなかったため要素の逐語照合はできない。ただし題名（Personalized ranking with pairwise Factorization Machines）および二次情報（implicit feedbackを取り込んでpairwise ranking学習するモデル提案、との要約）から、応答（暗黙的フィードバック）を学習に用いる一般的な推薦システム研究であり、C6（… |  |  |
| C6-0229 | 非該当 | 本文 |  |  | 非該当。本論文はレビュー/展望論文で、服薬・介入アドヒアランスを支援するスマートリマインダーシステムの将来像を論じている。むしろ利用者の行動データ（エンゲージメント記録）を機械学習モデルの訓練に用いて将来のアドヒアランス低下を予測・予防する方向性を明示的に推奨しており、C6が求める「応答を学習に戻さない」の要素はどこにも現れない。 |  |  |
| C6-0244 | 非該当 | 本文 |  |  | 非該当。本論文は生理指標（心拍変動の低下）でトリガーする1分間の短時間JITAI（介入）の効果を検証するマイクロランダム化試験であり、利用者の応答（受諾・拒否・訂正）を成功シグナルとして学習・報酬に戻すか戻さないかという論点そのものを扱っていない。プロンプトの「回答済み/無視/中断」の割合は結果として報告されるが、それを次回以降のトリガー判定の学習信号として使う/使わない設計方針への言及はない。 |  |  |
| C6-0402 | 非該当 | 本文 |  |  | デジタルメンタルヘルス介入への利用者エンゲージメントの障壁・促進要因を質的に整理した系統的レビューであり、適応系・自動化系が利用者の応答を学習・評価・報酬へ戻す/戻さないというML的な設計判断そのものは本文中に一切登場しない。C6の定義要素(応答を成功として学習・評価・報酬へ戻さない、という設計上の非対称性)を確かめる記述が無いため非該当。 |  |  |
| C6-0449 | 非該当 | 抄録のみ |  |  | OpenAlex/Semantic Scholar とも is_oa=false・abstract 欠落で、出版社(Springer)PDF は認証壁でブロックされ、著者ホームページ(dis.shef.ac.uk)も名前解決不能で入手できなかった(規定の6回試行を使い切り)。題名「Design and evaluation of systems to support interaction cap… |  |  |
| C6-0619 | 非該当 | 本文 |  |  | 本文は推薦システムにおける強化学習(Q学習)・文脈的バンディットの設計論文であり、C6が禁じる『利用者応答を成功として学習・評価・報酬へ戻す』設計をむしろ正面から採用・評価している。C6の定義に当たる逐語(戻さないことの主張)は本文中に見当たらず非該当。 |  |  |
| C6-0683 | 非該当 | 抄録のみ |  |  | 入力データに抄録が無く、DOI も付与されていない(2005年 HCII proceedings, CD-ROM収録の可能性が高い)。academia.edu 版は認証要求で403、Wayback Machine のスナップショットにもPDFリンクなし、Semantic Scholar 検索は429で失敗するなど、規定の6回試行を使い切っても原文・抄録のいずれも入手できなかった。題名『Facili… |  |  |

## 段 1 で採った全件

| sid | 年 | 題名 | DOI | 採った理由 | 段 2 |
|---|---|---|---|---|---|
| C6-0113 | 2024 | On Targeted Manipulation and Deception when Optimizing LLMs for User Feedback | 10.48550/arxiv.2411.02306 | 利用者フィードバックを報酬として最適化するLLMが操作的/欺瞞的挙動を学習するリスクを実証し、応答を成功信号として学習に戻すこと自体の害を論じており候補に直接関わる | 照合 |
| C6-0123 | 2021 | Correcting the User Feedback-Loop Bias for Recommendation Systems | 10.48550/arxiv.2109.06037 | 推薦アルゴリズムが利用者の評価履歴(フィードバック)に依存しすぎることで生じる『フィードバックループバイアス』を名指しで問題化しており、候補(非再捕捉)の論点に直接関わるため本文確認が必要 | 照合 |
| C6-0154 | 2024 | A Theory of Learning with Competing Objectives and User Feedback | 10.1007/978-3-031-63735-3_2 | 抄録なし、題名からは方向性不明(競合目的とユーザフィードバックの学習理論)。判定困難のため採る | 照合 |
| C6-0200 | 2016 | Personalized ranking with pairwise Factorization Machines | 10.1016/j.neucom.2016.05.074 | 抄録なし、題名からフィードバック捕捉の方向性が読み取れず判定困難のため採る | 照合 |
| C6-0229 | 2023 | New opportunities for the early detection and treatment of cognitive decline: adherence challenges and the pro… | 10.1186/s44247-023-00008-1 | 認知機能低下検出のための文脈適応型リマインダ・介入システムに言及し対象領域に合致。応答の扱いは抄録から不明のため迷い採る | 照合 |
| C6-0244 | 2025 | Effectiveness of 2 Just-in-Time Adaptive Interventions for Reducing Stress and Stabilizing Cardiac Autonomic F… | 10.2196/69582 | JITAI(適応的介入)のマイクロランダム化試験で対象系に合致。過去応答を次回介入に用いない設計に触れる可能性があり判定に迷うため採る | 照合 |
| C6-0402 | 2021 | Barriers to and Facilitators of User Engagement With Digital Mental Health Interventions: Systematic Review | 10.2196/24387 | デジタルメンタルヘルス介入(DMHI)へのユーザーエンゲージメント(受諾・継続利用を含む)の障壁と促進要因を扱うシステマティックレビューであり、対話的・自動化介入系を対象に応答の扱いを論じている可能性があるため、段2精査のため採る | 照合 |
| C6-0449 | 2007 | Design and evaluation of systems to support interaction capture and retrieval | 10.1007/s00779-007-0146-3 | インタラクション捕捉・検索を支援する系の設計評価(題名のみ、抄録なし)。「capture」の語義が候補と重なる可能性があり段2判定に委ねる。 | 照合 |
| C6-0612 | 2024 | Rethinking AI code generation: a one-shot correction approach based on user feedback | 10.1007/s10515-024-00451-y | 再学習を伴わずユーザー訂正フィードバックを都度利用する設計を明示的に検討しており、学習への再捕捉を避ける非再捕捉の主張に部分的に関連しうる | 照合 |
| C6-0619 | 2018 | Explicit or implicit feedback? engagement or satisfaction?: a field experiment on machine-learning-based recom… | 10.1145/3167132.3167275 | 推薦系における明示的/暗黙的フィードバックとエンゲージメント/満足度の対比を論じており、応答を成功指標として扱うことの妥当性を批判的に検討しうる(抄録なし・迷ったら採る) | 照合 |
| C6-0683 | 2005 | Facilitating user feedback in the design of a novel joke generation system for people with severe communicatio… |  | 重度コミュニケーション障害者向け生成系でのユーザーフィードバック活用法を扱っており、応答の扱い方に関わりうる(抄録なし・迷ったら採る) | 照合 |

## 逆向きの主流の例（段 1 の `contrary`・先頭 8 件）

- C6-0001（2016）VBPR: Visual Bayesian Personalized Ranking from Implicit Feedback —— 暗黙的フィードバックを協調フィルタリング/推薦モデルの学習信号として用いる提案で、候補と逆向き
- C6-0002（2007）Search Engines that Learn from Implicit Feedback —— 検索クリック等の暗黙的フィードバックをランキング学習に用いる提案で、候補と逆向き
- C6-0003（2016）Product-Based Neural Networks for User Response Prediction —— クリック等のユーザー応答をラベルとして学習するユーザー応答予測モデルの提案で、候補と逆向き
- C6-0004（2008）Semi-Supervised Clustering with User Feedback —— 利用者フィードバックを制約として取り込みクラスタリングを改善する提案で、候補と逆向き
- C6-0005（2018）Unbiased offline recommender evaluation for missing-not-at-random implicit feedback —— 暗黙的フィードバックの欠測バイアスを補正しつつ評価にそのまま用いる前提で、非再捕捉の主張ではない
- C6-0006（2014）Adaptive Bayesian personalized ranking for heterogeneous implicit feedbacks —— 暗黙的フィードバックを協調フィルタリング/推薦モデルの学習信号として用いる提案で、候補と逆向き(題名のみで判定)
- C6-0007（2013）Exploiting user feedback to learn to rank answers in q&a forums —— Q&Aフォーラムで利用者フィードバックを回答ランキング学習に用いる提案で、候補と逆向き
- C6-0008（2005）Evaluating implicit feedback models using searcher simulations —— 検索クリック等の暗黙的フィードバックをランキング学習に用いる提案で、候補と逆向き
