# 一次資料メモ (4) 主張の境界・禁止用語・検査規則・引ける番号

## `scripts/check_doc_lexicon.py` の正確な規則（実測）

**検査対象 5 本**（★ `.pptx.md` も入っている）:
`GSE_proposal.docx.md` / `GSE技術設計書.docx.md` / `GSE検証レポート.docx.md` /
`GSE参考文献.docx.md` / **`GSE設計スライド.pptx.md`**
＋ SSOT 2 本: `docs/glossary.md` / `.claude/skills/physical-anchor/SKILL.md`

| # | 正規表現 | 対象 | 履歴免除 |
|---|---|---|---|
| 1 | `Lv[ ]?[1-4]` | MITOU + SSOT | あり |
| 2 | `完了条件\|完了判定\|達成条件\|クリア条件\|completed\|achieved` | MITOU のみ | あり |
| 3 | `[⚠★]` | MITOU のみ | ⚠️ **なし（無条件で違反）** |
| 4 | `一方向に消耗させ\|最大の強みである\|不便益 ?HCI ?である\|不便益を測定可能` | MITOU のみ | あり |

**履歴免除語**（同じ行にあれば違反にしない）:
`廃止 / 旧称 / 旧版 / 旧義 / 旧文 / 削除済 / 全削除 / に削除 / に失効 / 使わない / 違反 / 逐語 / ~~ /
2026年度提案 / 取り下げ / 置かない / 置かず / 課さない / 課さず / 判定しない / 判定せず /
存在しない / 解釈しない / 外した / 外れた / 持たない / 実装しない / 書かない / 使わず`

★ したがって「完了判定を**置かない**」はそのまま書ける（`置かない` が免除語）。
⚠️ ★ / ⚠️ は**免除が効かない**ので、スライド本文に 1 文字も入れない。

⚠️★★★ 2026-09-04 に追加された `missing()`: 対象が 1 本でも無ければ
「違反なし」ではなく **検査が成立していない**として exit 1 になる。

## `scripts/check_citations.py` の正確な規則（実測）

- SSOT は **`docs/references.md`**。走査ルートは **`docs/` と `experiments/`**
  （⚠️ `.steering/` は見ない＝本メモの `[Pn]` は検査されない）。
- 拾うパターンは **`[Pn]` / `[Vn]` だけ**（`CITE = re.compile(r'\[([PV])(\d+)\]')`）。
  → ★ **未踏文書の素の `[n]`（`[11]` 等）は検査対象外**。
- 検査項目: 未登録参照 / 同一名前空間内の key 重複 / tombstone の引用 / 欠番 / 件数。
- ⚠️★★★ **重複検出は 1 回で全件出ない。「違反なし」まで是正→再実行を繰り返す。**

⚠️★★★ **スライドに `[Pn]` / `[Vn]` を書いてはいけない。**
未踏文書の `[n]` は『GSE参考文献』の通し番号で、`docs/references.md` とは**別体系**。

## 未踏参考文献の番号（`GSE参考文献.docx.md` 実測）

**79 件。番号は 1〜83。⚠️ 欠番は 36 / 37 / 38 / 50。番号は再利用しない。**

★ 本タスクで使う見込みのもの:

| [n] | 内容 |
|---|---|
| [1] | Kapur (2008) Productive Failure |
| [3][4][5] | 不便益（平岡 2021 / 荒木ら 2015 / 川上 2012） |
| [11] | Park (2024) スマホ打鍵で MCI 判別 AUC 0.88 / Flight Time r=−0.491 |
| [12] | Mehta ら (2025) 打鍵の仕方だけから LLM 支援を検出 |
| [13] | Giancardo ら (2015) AUC 0.93 / 0.91。逐語「タイプされたテキストの内容や言語によらず」 |
| [14] | Züger ら (2017) FlowLight（12 か国 449 名・中断 −46%） |
| [15] | Meyer ら (2017) 開発者の作業実態 |
| [16] | Shrestha ら (2022) Pausing While Programming |
| [41] | CMU (2018) keystroke dynamics による個人内ストレス分類（PhD thesis） |
| [42] | Qian ら (2021) Micro-Randomized Trial |
| [46] | Poreba & Sobernig (2026) 中断可能性予測の**再現失敗** |
| **[51]** | **Dhakal ら (2018) 136M keystrokes ※ ベースライン β の母集団中央値の出所** |
| **[52]** | **Rabiner (1989) HMM チュートリアル** |
| [53] | Microsoft（Windows Integrity Mechanism Design / TSF Reference / IME and TSF Accessibility）※ §3.3 訂正の根拠 |
| [72] | Freihaut & Göritz (2024) N=179×14日=10,760。**特徴を足すと帰無モデルより下がった**「overfitting on random noise」 |
| [73] | Freihaut & Göritz (2021) N=994。**マウス軌跡画像化 CNN 回帰の R² −5.22〜−1.10** |
| [74] | Koldijk ら (2018) SWELL。10 分割 90.03% vs **LOSO 58.89%**（多数決 61.76% を下回る）。mental effort r=0.8221 → LOSO 0.0343。被験者 ID を足すと 0.9410 |
| [75] | Christodoulou ら (2019) 71 研究 282 比較。**低バイアス 145 比較で logit(AUC) の差 0.00** |
| [76] | Kuvar ら (2023) PRISMA 42 研究。「multimodal models do not present a clear edge」 |
| [77] | Varoquaux (2018) 「**±10% for 100 samples**」※ 昇格判定から「+3%」を外した根拠 |
| [78] | Hammerla & Plötz (2015) 「**adjacent segments are not statistically independent**」※ Decision Episode 単位で数える根拠 |
| [79] | Middlehurst ら (2024) Bake off redux。**MultiROCKET+Hydra と HIVE-COTEv2 が有意に最良。深層は上位 2 手法に入っていない** |
| [80] | Dempster ら (2020) ROCKET「random convolutional kernels achieve state-of-the-art accuracy」 |
| [81] | Ghosh ら (2017) TapSense。個人化 AUROC 84%（SD 6%）/ 打鍵のみ個人化 71%（SD 11%）/ **被験者跨ぎ 71% だが SD 19%** |
| [82] | Maglio & Campbell (2000) 周辺情報の代償。主課題の低下は最良でも 26%、連続では 43% |
| **[83]** | **Uto ら (2020) 窓幅 30 秒・ステップ 10 秒の移動窓 + HMM で執筆過程（最良 9 状態）。被験者 72 名・総打鍵 184,916。※「打鍵と HMM で執筆過程を推定すること自体は本提案の新規性ではない」。※ IME を一語も扱っていない** |

⚠️★★★ **未踏参考文献に無いもの**（＝スライドで番号を付けて引けない）:
`[P161]` TypeNet 疲労 / `[P221]` stress LOSO ρ / `[P222]` / `[P226]` mind wandering κ /
`[P225]` / `[P231]` / `[V59]` Allison / `[V61]` / `[V94]` / `[V96]` / `[V100]`（※ [78] が同一文献）/
`[V103]` / `[P250]`。
→ ★ **番号を新設せず、番号なしで事実だけ書くか、番号のある近い文献に置き換える。**

## `docs/glossary.md` の禁止用語（スライドで踏みやすいもの）

| 禁止 | 代わりに |
|---|---|
| **「不便益 HCI である」/「不便益を測定可能にした」** | 「不便益を**設計思想として引く**」 |
| **「認知状態を捉えた」** | 「行動プロキシが主観的摩擦・前進と**個人内で順序一致した**」 |
| **段階呼称 `Lv1`〜`Lv4`** | 実体名（Nudge / Physical Anchor） |
| **「段階的介入」** | ⚠️ Wall が消え Physical Anchor が完了条件を持たなくなった結果、**強度が単調に上がる「段」の構造は現存しない** |
| **Wall / Zen Timer / Monk Mode / Early Unlock** | 削除済（ADR-015） |
| **Mh-D 内部の `L1`〜`L4`（層番号の新設）** | 既存の 7 層 `Layer 0`–`Layer 7` |
| 「認知体力」「作業持続プロファイル」「負荷応答プロファイル」 | 新設しない（ADR-020 D2 / ADR-019 D7） |
| `Stage 1〜4` / `M1〜M4` | 実体名（固定 baseline / criterion 直結 / 個人・タスク適応 / 時系列） |

★ 「**現行で稼働するのは Nudge のみ**で、**不便を担う Physical Anchor は未実装**」。

## 実装状況の安全な定式（★ そのまま使う）

| 対象 | ★ 安全な書き方 | ⚠️ 書いてはいけない |
|---|---|---|
| Physical Anchor | 「**未実装**。設計は ADR-018 で確定（完了条件を置かない）」 | 「段階的介入の第 3 段」「Lv3/Lv4」 |
| 表現チャネル | 「**本体アプリ未配線のプロトタイプ段階**。層 0 / 層 2 / 層 A の試作と ABX 実験は実在」 | 「実装済み」／「未実装」の一語 |
| セキュア入力 | 「**検出は macOS のみ実装済み。Windows は計器が無い。抑止の配線はどちらの OS にもない**」 | 「送出元が無い」（macOS にはある） |
| ONNX / Flutter | 「**昇格判定を通った場合にのみ検討する経路**。依存もモデルも学習スクリプトも存在しない」 | 「採用している」 |
| 介入 | 「**現時点で稼働している介入は Nudge のみ**」 | 「4 段階介入」「Wall」 |
| 個人ベースラインの凍結 | 「**評価設計上の契約（PreReg-5）とオフライン解析の holdout 分割**」 | 「アプリ実行時に個人 β を学習・凍結する」（**未実装**） |
| 主張 | 「確証するのは **L0 だけ**」 | 「認知状態を捉えた」 |

⚠️ **現行スライドの「セキュア入力欄での記録抑止: スキーマ項目はあるが送出元が無い」は不正確**
（macOS には送出元がある）。

## 主張の層構造（research-positioning.md:28-36・降ろしてはいけない）

| 層 | 何を計算するか | 実装 | 検証対象 | 確証/探索 |
|---|---|---|---|---|
| **L0: MhD 軸** | 5 特徴量 → X (Cognitive Friction) / Y (Productive Engagement) | `engine.rs` | probe Q1/Q2 との個人内順序一致（C-index・GATE3） | **確証** |
| L1: Stuck | X/Y → `p_stuck` | HMM | self-marker ＋ 行動アウトカム | 探索 |
| L2: Need | 閾値＋抑制による介入要否の決定 | `intervention.rs` | 混同行列・HIR・Precision・STALL-recall | 探索 |
| L2': Opportunity | 小休止・cooldown 等のタイミング判定 | `intervention.rs` | 近接アウトカム（micro-randomization） | 探索 |

⚠️ **`p_stuck` は「Need 層が焚く」値ではなく「MhD (L1) が計算する」値**。
L0 の C-index は `p_stuck` そのものを検証しない。

## 技術設計書の目次（★ スライドが「証明を委託」できる先。実在する項目のみ）

```
0. 本書の読み方 —— 何を主張し、何を主張しないか
1. 設計哲学 / 2. アーキテクチャ全体図
3. Sensing Layer
   3.1 5特徴量（30秒ローリングウィンドウ）
   3.2 入力モード別ベースラインと変換候補の抑制
   3.3 IME Composition Analysis と、2026年度版の技術的訂正
   3.4 content-free 制約 —— 何を記録し、何を記録しないか
   3.5 ドメイン別ヘッド（Domain Inference Head）
4. Inference Layer: MhD Core
   4.1 潜在二軸への射影
   4.2 HMM と p_stuck
   4.3 プロトタイプ実装で解決した課題
   4.4 criterion 直結 への昇格判定 —— 判定量そのものを作り直した
       ### 判定ヘッドの損失関数
   4.5 段の軸を「モデルの複雑さ」から「推定対象と根拠」へ変えた
5. Decision Layer: Need / Opportunity 分離と介入
   5.1 Need と Opportunity を分ける / 5.2 現行の介入レパートリー
   5.3 削除した介入とその理由 / 5.4 Physical Anchor（未実装・第2の柱）
   5.5 介入判断の評価設計
6. Expression Channel
   6.1〜6.7（境界クラスの契約 = 6.3 / 曝露予算 = 6.4 / セキュリティ最小要件 = 6.6）
7. 検証設計 / 8. フォールバック戦略（撤退設計） / 9. 技術スタックと開発環境
10. Phase1（較正データ収集）の実測 / 11. 参考文献
```

★ 委託先として実在するのは上記の節番号のみ。⚠️ **存在しない節へ委託すると嘘になる。**

## ★★★ 図の PNG 書き出し —— 既存 4 枚の作り方を復元した（2026-09-04）

⚠️ **どの文書にも書かれていなかった**が、実測で確定した:

```bash
"/c/Program Files/LibreOffice/program/soffice.exe" --headless \
  --convert-to 'png:draw_png_Export:{"PixelWidth":{"type":"long","value":W},"PixelHeight":{"type":"long","value":H}}' \
  --outdir <dir> <file>.svg
```
★ `W` / `H` は **SVG の `viewBox` と同じ値**にする。

★ 検証: `gse-architecture.svg` をこの手順で書き出すと、コミット済みの
`gse-architecture.png` と **md5 が完全一致した**（`661e8a91f4e9fa8ad43c605992c68086`）。
→ ★ 新規figure も同じ手順で作れば既存 4 枚と体裁がそろう。

⚠️ **PyMuPDF (`fitz`) で SVG を書き出してはいけない** —— 開けるが、
**`ー`（長音）のグリフが落ち、text-anchor の解釈も違って文字が枠からはみ出す**（2026-09-04 実測）。

⚠️ `scripts/md2docx.py --selftest` が `figures/` の全 `.png`/`.svg` 対の**寸法一致**を検査する。
→ ★ 片方だけ更新すると落ちる。
