# 文献カード インデックス

`/literature-review` (Phase 7) が生成する落合フォーマットのカード一覧。新トピックごとに追記される。
`docs/references.md` に研究者本人の 2 書誌（理論 P1–P18 / 方法論 V1–V29）を統合登録済み（一意 41 本）。
落合フォーマット精読カードは下表のトピック単位で作成済み。

| 日付 | トピック | ファイル | カード数 | 「やり残し」要約 |
|---|---|---|---|---|
| 2026-06-28 | probe-timing-interruptibility | [20260628-probe-timing-interruptibility.md](20260628-probe-timing-interruptibility.md) | 5 | HCI は timing を「介入の快適化（opportune moment）」へ最適化、ESM は「無偏測定（signal-contingent + stratified）」を確立。両者を同一システムで層分離（L0 較正=stratified random / L2' 介入=opportunity 合わせ）する規約が空白＝GSE の差分 |
| 2026-06-28 | calibration-sampling-density | [20260628-calibration-sampling-density.md](20260628-calibration-sampling-density.md) | 5 | ESM 標準=6/日だが「総回数は compliance に無相関・頻度↔期間トレードオフ」[V25][V26]＝較正は構造化セッション内の高密度・短時間で収量を稼げる。GATE2 ≥20 は単一事例最小~15–18[V28]と信頼性理想~70–100[V27]の間の floor として妥当。収量律速は密度でなく提出摩擦[V29]＝T2/T4 投資の根拠。self-marker(event-contingent)は率不可測[V24]＝probe 主・self-marker 従 |
| 2026-06-29 | task-type-writing-struggle | [20260629-task-type-writing-struggle.md](20260629-task-type-writing-struggle.md) | 3 | 「停滞の質はタスク種別で異なる」を理論接地 [P16][P17][P18]: 論述=knowledge-transforming=作業記憶高負荷=濃い停滞 vs 物語/通信文=knowledge-telling=浅い停滞。GSE の4分類 enum は ad-hoc で telling↔transforming 軸での再定義・経験的検証が空白＝Phase1 は論述に絞り（信号最濃・writing β 整合・交絡統制・検出力最大）、タスク別停滞分析は Phase2 送り |
| 2026-07-03 | intervention-content-and-ml-grounding | [20260703-intervention-content-and-ml-grounding.md](20260703-intervention-content-and-ml-grounding.md) | 18 | RQ1: Nudge 中身はメタ認知質問形 (g=0.50 検証済) + 選択肢提供 (言語フレーミングは null)、ただし目標整合が前提 (大規模 null RCT) → if-then 意図設定と組む。RQ2: ポーズ**位置** (境界キー VK で本文非保存移植可) + 個人化閾値 (median×N) が Opportunity の次の特徴。RQ3: universal marker 不在 = within-person 必須 (GSE 方針を強く支持)、Stage2 は logistic+RF 2アーム、Transformer は Stage3 以降。RQ4: Lv1=System2/Lv2=System1 の機構切替、弱 lockout+Early Unlock は実証上の最良受容点 (現行設計一致)、Zen Timer 2分は性能回復根拠なし (well-being 用)・Lv3/4 が性能回復役。改善提案 22 件を実装可能性で振り分け、references 登録候補 23 件 |

| 2026-07-23 | activation-layer-and-self-tracking-evidence | [20260723-activation-layer-and-self-tracking-evidence.md](20260723-activation-layer-and-self-tracking-evidence.md) | 8 | RQ1 活性化層=**条件付き採用**: if-then は頑健に非ゼロだが小さい（d=.36→補正後 **d=.15**）、GSE のセル（online .31/field .27/行動変容 .27）はすべて下限側。UI 制約は `rehearse but do not persist`（記録すると .44→.31、詳細化で .46→.24、常時表示は不可）、テンプレ選択は可（p=.62、2-1）。**最重要: 実行意図は動機を作らない**（目標意図に条件づけ・Koestner 主効果ゼロ）＝Phase1 の需要の薄さには効かず、needs ベース選抜が筋。RQ2 自己追跡=**継続利用の主柱には非推奨**（ネガ枠のみ有効 0.634・**撤去2週で消失** -0.473・客観 null で主観のみ）。⚠️ **RQ3 (AI へ逃げる瞬間の friction)・RQ4・RQ5 (フォーカスアプリの天井) は検証済み証拠ゼロ＝探索未完遂**（予算枯渇）。[P19] d=0.65 は 0-3 否決され [P21] に上書き |

| 2026-07-24 | friction-retention-and-overreliance-evidence | [20260724-friction-retention-and-overreliance-evidence.md](20260724-friction-retention-and-overreliance-evidence.md) | 10 | **パートA (生産的苦闘)**: 摩擦の学習効果は成果指標で符号が変わる (概念 g=0.36 / 手続き g=-0.03 null / 低学年で反転 [P27])、効果源は遅延でなく後段 consolidation [P28]＝GSE は前半のみ実装し後半欠落。→「摩擦が能力を育てる」は主張不可、「自力解決の機会を保存」に限定 (パートC)。**パートB (Gate D)**: DSCT 効果天井 g=0.47 (脆弱基盤 [V39])、ナッジは補正後 d≈0 で structure系(Wall)のみ未否定 [V40]、30日継続率 中央値 3.3% [V41]・登録経路が支配 (44 vs 4日 [V42])、「出さない判断」+行動指標 receptivity の先行例 [V43]、one sec 効果源は dismiss-first で friction でない [V33訂正]、摩擦は agency 回復を伴わない [V44]。⚠️**RQ-2 (agentic coding 過信) / RQ-3 (accountability) は3ラウンド通じ確定証拠ゼロ＝判定不能** |

> 各カードは docs/literature/<YYYYMMDD>-<topic-slug>.md。
> 出典は docs/references.md に append-only で登録される（citation-ssot skill 経由、P/V 名前空間）。
> 精読の起点候補（references.md より）:
> - 理論の核: [P12] Kapur Productive Failure, [P6] Kawakami&Naito 不便益, [P9] Bjork desirable difficulties
> - 身体性: [P2] Bratman nature/rumination, [P8] Oppezzo&Schwartz walking, [P10] Kaplan ART, [P14] Raichle DMN
> - キーストローク: [P7] Park MCI, [P11] Mehta LLM-keystroke, [V7] Condrey typing-authorship
> - 方法論: [V1] Pejovic ESM, [V4] Qian MRT, [V3] Dziak/Nahum-Shani tailoring, [V5] Crotti Hylog(IME)
