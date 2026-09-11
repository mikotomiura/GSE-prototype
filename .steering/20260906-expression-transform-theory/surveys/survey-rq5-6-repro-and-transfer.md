# サーヴェイ 1 ラウンド: RQ-1(生成的表現の再現可能性) / RQ-2(横展開の反証)

日付: 2026-09-06
実行方式: `/literature-review` Step 2〜4 のみ（Step 0/1 はユーザー指定で確定済み、Step 5〜8 は本ラウンド対象外
= **docs/references.md・docs/literature/_index.md は編集していない。登録候補の報告のみ**）。
RQ-1 と RQ-2 を独立フォークで並列実行。

---

## 重複潰し（着手前・両 RQ 共通で実施）

`docs/references.md`（P1–P275, V1–V124）を以下のキーワードで grep 済み:
`generative art / creative coding / procedural / determinis / random seed / golden output / byte-equal /
bit-exact / MLOps / reproducibility crisis / Art Blocks / NetLogo / agent-based model / sonification /
domain-transfer / cross-domain / domain-independent / portable mapping / generaliz / 領域固有 / 一般化でき /
移植 / did not transfer / failed to generalize / domain-specific / Model-Based Sonification / Grammar of
Graphics / Vega-Lite / design guideline / Hermann / auditory display`

- RQ-1 に直接重複する既出はゼロ。隣接のみ: **[V102]** Kapoor & Narayanan 2023 *Patterns*（ML の
  reproducibility crisis＝データ漏洩の話であり、生成的・確率的出力の決定論的固定の話ではない。重複ではない）。
- RQ-2 に直接重複する既出はゼロ。隣接のみ: **[P54]**（ambient display 分類論）・**[P59]**（連続ソニフィケーション
  vs 視覚アラート、モダリティ横断でない）・**[P232]** GLOBEM（ML モデルの汎化不全であり表現規則の移植ではない）・
  **[P240]**（無関係）・**[P183]**（Reflective Design、無関係）。

---

# RQ-1: 生成的表現の再現可能性

## (1) 下位問いごとのエビデンス温度

- **(a) generative art/creative coding の決定論・seed 実践論**: **PLAUSIBLE BUT UNPROVEN** — 実践（Art Blocks
  のオンチェーン版固定、Samila、p5.js コミュニティ）は厚く内的に一貫するが、**査読された実証研究はゼロ**。
- **(b) 研究ソフト再現性規約の確率的出力への適用**: **確定** — mlf-core が査読済み一次証拠でビット単位再現を
  複数モデルで達成。ただし ACM artifact badging は「許容誤差内」を標準とし GSE の byte-equal より緩い。
- **(c) 反証（生成的出力の再現ができなかった/無意味化した報告）**: **確定** — Bethard(2022)・floating-point
  非結合性論文(Shanmugavelu et al. 2024)・Grimm et al.(2025) の 3 本が独立に、査読済みかつ定量的に
  「seed/コード/版を固定しても再現は破綻しうる」を示す。

## (2) 登録候補の出典一覧

| # | key 候補 | N | 設計 | 効果量・主張 | 1 行の意味 | namespace/状態 |
|---|---|---|---|---|---|---|
| 1 | Art Blocks Protocol Docs（`docs.artblocks.io`） | 該当なし | プロトコル仕様書（実践・非査読） | オンチェーン 32byte ハッシュを seed に注入、依存ライブラリ(p5.js v1.0.0等)もオンチェーン固定 | GSE の seed固定+版凍結と構造的に同型の実践だが査読なし | V / provisional |
| 2 | Samila (Sabouri et al. 2025, arXiv:2504.04298) | 該当なし | ツール論文 | 逐語 "regeneration nearly impossible without both [seeds]"／自ら "not supported by rigorous statistical analysis" と明記 | seed 保存失念が再現不能に直結する運用リスクの自己申告 | V / provisional |
| 3 | p5.js GitHub Issue #3691 | 該当なし | コミュニティ・バグ報告 | `randomSeed()` 近接値でPRNG初期値がほぼ同じに丸まる | 「同一seed→同一出力」は保てても PRNG 品質が悪いと多様性の目的で無意味化しうる | V / provisional |
| 4 | **mlf-core** (Heumos et al. 2023, *Bioinformatics* 39(4):btad164, DOI:10.1093/bioinformatics/btad164) | 3モデル(TensorFlow CNN, PyTorch U-Net N=131スキャン, XGBoost)+追加1、各N=5–10実行 | 査読済み・決定論化フレームワーク | "Only the deterministic setup ... achieved fully deterministic results on all tested infrastructures"／同一論文内でXGBoost複数GPU・Dask分散は非決定的と明記／決定論化のコスト有意(p=.001〜.014) | (b)の核: 確率的MLへ再現性規約を適用しビット一致を達成した査読実例。ただし「全アルゴリズムには拡張できない」対称性を内包 | V / active |
| 5 | Shanmugavelu et al. 2024, floating-point non-associativity (SC'24 CORRECTNESS workshop, arXiv:2408.05148) | 複数HPC/DLカーネル実装比較 | 査読済みワークショップ論文 | GPU/最適化アルゴリズムでは実行順序差でビット単位一致が構造的に破綻。bit-exactは「計算順序を厳密制御できる限定環境のみ」 | seed固定は必要条件だが十分条件ではないという一般原則(GSEはCPU単一プロセスで直撃は受けにくいが原則は借用可) | V / active |
| 6 | ACM Artifact Review and Badging（公式ポリシー、casrai.org経由で複数独立ソース文言一致確認） | 該当なし | 業界標準ポリシー | "obtain the paper's main results ... within an accepted tolerance for the type of experiment" | 計算科学の標準的再現性バッジは許容誤差前提。GSEのbyte-equalは業界標準より厳格な選択 | V / provisional(ACM一次403で未直接確認) |
| 7 | Engel & Hellar 2015–16, *Electronic Media Review* Vol.4（AIC） | 該当なし | 概念論文（業界誌・非査読） | "scientists seek ... 'to get the same answer'" vs "art conservators seek to reproduce the viewer's experience" | 美術保存分野の計算再現性輸入は目的が「鑑賞者体験」でGSEのbyte-equal型とは異なる | V / provisional(一次未取得・要約経由) |
| 8 | **Grimm et al. 2025 (online 2024-12-06), *Ecological Modelling* 511:110967, DOI:10.1016/j.ecolmodel.2024.110967**（CC BY 2.5, 一次PDFをpypdfで全文確認） | **18モデル**（生態学異分野横断）、再現所要2–12日(平均5日) | 査読済み・ODD/NetLogoでの独立再実装研究 | "For 15 of the 18 models ... reproduced; for two ... only partial ... and for one ... replication failed"／失敗要因内訳: パラメータ欠落4・範囲欠落1・方程式/ルール欠落6・スケジューリング欠落1 | (c)の最良の定量的反証: アルゴリズム的出力の再現はコード/seedがあってもモデル記述欠落だけで破綻しうる | V / active |
| 9 | **Bethard, S. 2022, "We need to talk about random seeds", arXiv:2210.13393**（ACL投稿だが正式査読情報未確認） | ACL Anthology論文85本の分析 | メタ分析的レビュー | "fixing the random seed does not guarantee replicability. ... tensorflow library has a history of producing different results given the same random seeds, especially on GPUs"／riskyな使用 48/85=56.5% | (c)の最直接反証: 「seed固定で再現性を主張する」多数派実践そのものをriskyと名指し | V / provisional(査読状況未確認) |

## (3) 否決リスト

| Claim | 票 | 否決理由 |
|---|---|---|
| 「分散検証ネットワークでの知覚ハッシュ合意により生成AIの出力再現性が確認できる」(Kim et al. 2023, arXiv:2307.01898) | **0-3** | 測定対象が構成概念として別物（多数決合意 vs 決定論的byte-equal一致）。用語一致に釣られた誤導リスク |
| 「ブラウザ非同期実行が並列シミュレーション再現性を損なう」(RepliCore, Anqing Chen 2026, arXiv:2607.02529) | **1-2** | 単著・査読未確認・要約から定量データ未確認。原理自体は他の頑健なソース(#5, #9)で既に支持済みのため単独では採用しない |

## (4) 結論

GSE の「seed 固定 + 版凍結 + byte-equal 回帰検査」を表現層へ適用する提案は **(b)(c) で強く接地できる**
（mlf-core が確率的計算過程への適用実例、Bethard・floating-point論文・Grimm et al. の3本が「固定だけでは
不十分」を独立に定量化）。**(a) は実践は厚いが査読実証はゼロ**（PLAUSIBLE BUT UNPROVENのまま、ゼロをゼロと
明記）。設計への含意: 「seed 固定は必要条件だが十分条件ではない」——PRNG品質・並列/GPU非決定性・モデル記述
（design.md等）の完全性、の3点を前提に組み込むべき。ACM の許容誤差規約と対比すると、GSE の byte-equal は
意図的に業界標準より厳格な選択であると自覚的に書くべき。

---

# RQ-2: 横展開の反証

## (1) 下位問いごとのエビデンス温度

- **(a) 可視化・ソニフィケーションのマッピング規則がドメイン移植で破綻した報告**: **確定（限定的）** —
  Walker & Kramer(2000) が同一音響パラメータでも概念的データ次元ごとに極性・スケーリング指数が変わり事前
  推測不可能なことを実験的に実証。ただしGSEが問う「時系列→表現」レベルではなく隣接領域からの類推。
- **(b) 「領域固有だった/一般化できなかった」と結論した研究**: **確定（1件、直接的）＋PLAUSIBLE BUT
  UNPROVEN（分野傍証）** — CcNav(2020) が同一データ型を共有する隣接ドメインへの可視化移植ですら
  「新規設計に近づいた」と著者自身が明記。Dubus & Bresin(2013) の系統的レビューはソニフィケーション分野が
  汎用方法論を欠き評価もほぼ行っていないことを示す間接証拠。
- **(c) 成功例**: **確定だがGSEへの外挿は弱い** — Vega-Lite/Grammar of Graphicsはチャート仕様の構文レベル
  では汎用化に成功しているが、GSEが問う意味づけレベルの構成規則とは抽象化レイヤーが違い、その成功例自体に
  GoFish(2026) が限界を指摘。

**「該当研究ゼロ」には丸めていない**: GSEが問う正確な設定（時系列データの表現構成規則を別データ領域へ移した
直接実証）自体は判定不能（該当研究ゼロ）。隣接領域（音響マッピングの心理物理学的較正・可視化デザインスタディ
の移植）では反証事例が確定している、という形で温度を分けて報告。

## (2) 登録候補の出典一覧

| # | key候補 | N/設計 | 効果量・主張 | 1行の意味 | namespace/状態 |
|---|---|---|---|---|---|
| 1 | Munzner, T. 2009, "A Nested Model for Visualization Design and Validation", IEEE TVCG 15(6):921-928, DOI:10.1109/TVCG.2009.111（一次PDFをpypdfで確認） | 概念/方法論論文 | 4層独立: domain problem→abstraction→encoding→algorithm、"an upstream error inevitably cascades to all downstream levels"、"wrong problem/abstraction/encoding/algorithm" | 移植の理論的反証圧力の枠組み（下位層検証は上位層=対象領域の妥当性を保証しない） | P / active |
| 2 | Walker, B. N., Kramer, G. & Lane, D. M. 2000, "Psychophysical Scaling of Sonification Mappings", Proc. ICAD 2000（一次PDFをpypdfで確認、DOIなし） | Exp1 N=11（matching cue, 4データ次元×2表示次元）、Exp2は条件毎N=12–16程度 | 温度→周波数指数+0.71(sd=0.02)、他次元は符号・大きさとも異なる。"the actual slopes of the lines cannot be guessed" | 同一音響パラメータでも概念的データ次元ごとに極性/スケーリングの再較正が必要、事前推測不可 | P / active |
| 3 | **Devkota, S. et al. 2020, "CcNav: Understanding Compiler Optimizations in Binary Code", IEEE TVCG (Proc. VIS 2020), DOI:10.1109/TVCG.2020.3030357**（一次PDF arXiv:2009.00956著者版をpypdfで確認） | デザインスタディ、N=1ケース（少数領域エキスパート、著者1名が3ヶ月常駐） | "Transferability ... was beneficial, but more limited than expected"／"we found the process more similar to a new design"／同一データ型(CFG・逆アセンブリ)でもタスク/目的が違うと移植破綻 | RQ-2(b)への最も直接的な一次反証: 同一データ型を共有する隣接ドメインでも移植は新規設計に近づく | P / active |
| 4 | Dubus, G. & Bresin, R. 2013, "A Systematic Review of Mapping Strategies for the Sonification of Physical Quantities", PLOS ONE 8(12):e82491, DOI:10.1371/journal.pone.0082491 | 系統的レビュー、179論文/60プロジェクト（739件DBから） | "evaluation of sonification mappings is performed only in a marginal proportion of publications"(約6.1%) | 分野は汎用方法論を欠き検証も薄い(移植可能性の間接的反証=検証不在の証拠) | P / active |
| 5 | Satyanarayan, A. et al. 2017, "Vega-Lite: A Grammar of Interactive Graphics", IEEE TVCG 23(1):341-350, DOI:10.1109/TVCG.2016.2599030 | 採用実績（事実、一次全文未取得） | 任意データ列・チャートタイプへ構成可能なエンコーディング＋合成代数、広範な採用 | (c)成功例だが「チャート仕様構文」レベルの汎用性でGSEの「データ→状態推定→表現」の意味づけレベルとは抽象化レイヤーが異なり類推弱い | P / provisional(一次未取得) |
| 6 | Pollock, J. & Satyanarayan, A., "GoFish: A Grammar of More Graphics!", IEEE TVCG (Proc. VIS'25, 2026-01公開)（DOI未確認、一次未取得） | 一次未取得 | "the resultant design space has surprising limitations, inconsistencies, and cliffs — even seemingly simple charts like mosaics, waffles, and ribbons fall out of scope" | #5の成功主張を割り引く材料 | P / provisional(DOI未確認) |

**未採用（原典未特定・登録候補に含めない）**: 「専門家マッピングは練習で領域差が消える」（weather→health
ドメイン）という趣旨のWebSearch要約がヒットしたが原典を特定・逐語確認できず、捏造回避のため不採用。
Model-Based Sonification (Hermann系) の「ドメイン非依存」主張も一次確認（`noah.nrw` PDF）がタイムアウトし
未取得のため登録候補に含めず、本文中で「未実証の設計上の主張」とのみ言及。

## (3) 否決リスト

| Claim | 票 | 否決理由 |
|---|---|---|
| 「sonification mappings created by an expert for one domain generalize with practice to a different domain」 | 未評価(一次未確定のため三票に進めず) | 原典特定不能。捏造回避のため除外 |
| 「GLOBEM(Xu et al. 2022, [P232]既出)はマッピング/表現規則の領域移植不全を示す」 | **1-2** | [P232]はMLモデルの汎化不全(アルゴリズムが新データセットで性能低下)であり、RQ-2が問う「デザインの構成規則」の移植とは対象が異なる |
| 「Vega-Lite/Grammar of Graphicsの成功はGSEの『構成規則は移植可能』を支持する」 | **1-2** | 汎用性が「チャート仕様の構文」レベルであり、GSEが問う「データ→認知状態推定→表現」の意味づけレベルの構成規則とは抽象化レイヤーが異なり類推として弱すぎる |

## (4) 結論

GSEが問う正確な形（時系列データの表現構成規則を別データ領域へ移した直接実証）の研究は**見つからなかった
（判定不能）**。しかし隣接領域には反証圧力のある一次証拠が複数ある: Walker & Kramer(2000)が同一音響パラ
メータでも概念的データ次元ごとに極性・スケーリング指数が異なり事前推測不可能なことを実験的に示し、
CcNav(Devkota et al. 2020)は**同一データ型を共有する隣接ドメインへの視覚化移植ですら「新規設計に近い」
ものになった**ことを具体的に報告し、Munzner(2009)の4層モデルは「エンコーディングの検証は対象領域の問題
認識・抽象化の妥当性を保証しない」という理論的根拠を与える。一方Dubus & Bresin(2013)の系統的レビューは
ソニフィケーション分野全体が「マッピング妥当性検証をほとんど行っていない」ことを示し、「一般化できることが
実証されている」わけでもない。成功例のVega-Lite/Grammar of Graphicsは「チャート仕様の構文」レベルの汎用性
であり、GSEの「データ→状態推定→表現」の意味づけレベルの構成規則とは層が異なるため対称性のために報告する
が強い支持としては採用しない。**総合すると、RQ-2はGSE側の「構成規則は移植可能」という楽観的主張に対して
中立〜やや反証寄り**——直接反証はないが、隣接領域の具体的失敗事例(CcNav)と移植可能性側の実証不足
(Dubus&Bresinのレビュー、Vega-Lite類推の弱さ)が「移植可能性は無条件に仮定できない」という慎重さを支持する。

---

## 次ラウンドへの申し送り（`_index.md`「やり残し」相当・本ラウンドでは書き込まない）

- RQ-1: Model-Based Sonificationの「ドメイン非依存」主張と対をなす、GSE表現層固有の生成規則設計に対する
  先行例（もしあれば）は未探索。ACM artifact badgingの一次（acm.orgが403）の直接確認が必要。
- RQ-2: `noah.nrw`のMBS一次PDF取得、GoFish(2026)のDOI確定、weather/health domain mapping claimの原典特定
  （3回試みて失敗）。
