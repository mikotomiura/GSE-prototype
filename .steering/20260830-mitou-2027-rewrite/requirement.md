# 未踏 2027 提出文書（2 本）の書き直し

> 入口: `.steering/_handoff/next-session-prompt-mitou-2027-rewrite.md`

## 背景

`docs/mitou_docs/` にある 2 文書は **2026 年度未踏で提出した版**であり、
その後の 1 年で **主張・実装・設計判断のすべてが動いた**。放置すると、
提出文書と repo の SSOT が別のことを言っている状態になる。

⚠️★★★ **実測された食い違い（2026-08-30 時点）**:

| # | 2026 版の記述 | ★ 現状 |
|---|---|---|
| 1 | Lv1 Nudge → Lv2 Ambient Fade → Lv3 Thought Scaffold → **Lv4 The Wall** / **Monk Mode** | ⚠️ **Wall / Zen Timer / Monk Mode は 2026-08-23 に全削除**（ADR-015 D1/D2）。★ 稼働は **Lv1 Nudge のみ**、Lv3/Lv4 は未実装 |
| 2 | **6 特徴量**で **FLOW / INCUBATION / STUCK の 3 状態を推定** | ⚠️ 現行は **5 特徴量**（F2 除外・`features.rs` 実測）。⚠️★★★ かつ `research-positioning.md` §1 が **「F/I/S 三値分類は claim しない」**と明記 |
| 3 | Outdoor 条件で **GPS・加速度センサ**により散歩を検証 | ⚠️★★★ **ADR-017 D10 が身体活動センシングを本体から恒久除外**（PM-D11 の「測ってよい」を取り下げ） |
| 4 | **8 分間の歩行で発散的思考が 60% 向上** | ⚠️ micro-break のメタ解析（22 標本 / N=2,335）で **成績は全体 null（d=.16, p=.116）／認知負荷の高い課題では d=−.09** [P162]。★ **歩行に特化した推定値は存在しない** |
| 5 | 学術的貢献の第一 = **3 クラス分類の実証** | ⚠️ **降ろした主張**。★ 確証核は **L0（X/Y 二軸）の順序妥当性（C-index ≥ 0.65）**のみ |
| 6 | **不便益を HCI の設計原理として統合した事例はない** | ⚠️★★★ **認定条件 1（益は不便だからこそ＝労力）を現行実装が満たさない** [P170] → ★ **「設計思想として引く」と書く**（`glossary.md` 禁止用語） |
| 7 | フェイルセーフの発動条件が **3 クラス Macro F1 < 0.5** | ⚠️ 凍結済みの合否契約は **GATE1–3 / PreReg-1〜8** |
| 8 | （記載なし） | ★★★ **Phase1 が `DataInsufficient`（GATE3 未判定）で収集打ち切りになった**（2026-08-18） |
| 9 | （記載なし） | ★ **表現チャネル**（ADR-017 / `expression-channel.md`）が第 2 の柱として立った |
| 10 | 2026 年度前提の年度表記 | ★ 2027 年度へ（★ 金額・期間は同形で確定済み） |

技術設計書側にも同型の食い違いが **7 件**（§5 4 段階 / §6.2 GPS+FFT / §1.4 比較表 /
§3.1 の 6 特徴量 11 箇所 / §4.4 Stage 昇格 / §10 予備的知見 / §8 月次マイルストーン）。

## ゴール

⚠️★★★ **改訂幅は「今回の SSOT に全面的に合わせる」**（研究者決定・2026-08-30）——
**事実誤りの修正に留めず、主張・骨子・ロードマップまで 2026-08-30 時点の SSOT に一致させる。**

「完了」の条件:

1. ★ `docs/mitou_docs/` の 2 文書が **2027 年度提出版**として書き上がっている。
2. ★ **機械検査が緑**である（下記「受け入れ条件」の検査コマンドが全部通る）。
3. ★ 主張の温度が `docs/research-positioning.md` / `docs/glossary.md` 禁止用語と矛盾しない。

## スコープ

### 含むもの

- `docs/mitou_docs/[提案プロジェクト詳細資料]GSE_proposal.docx.md` の全面改訂
  （⚠️ **見出し構造 1〜8 ＋ 参考文献を変えない** —— フォーマット指定があるため）
- `docs/mitou_docs/[提案プロジェクト補足資料]GSE技術設計書.docx.md` の全面改訂
  （★ **フォーマットも含めて自由に変えてよい**）
- ★ 両文書の **参考文献リストの再構成**（★ 2 文書独自の番号体系。`docs/references.md` は動かさない）
- ★ `.steering/20260830-mitou-2027-rewrite/decisions.md` に判断を記録

### 含まないもの

- ⚠️ **`.docx` への書き戻し** —— ★ 必要になった時点で python-docx ＋ UTF-8 で別作業
  （★ memory: 表セルに注意）
- ⚠️ **`docs/` 側 SSOT の改訂** —— ★ 本タスクは SSOT を **参照する側**であって書き換える側ではない
  （⚠️ 未踏文書の主張が `docs/` と食い違ってはならないが、直す方向は **未踏文書 → SSOT** である）
- ⚠️ **`docs/references.md` への新規登録** —— ★ 未踏文書は独自番号体系であり、
  **未踏文書の中で番号を振り直しても `references.md` は動かさない**（`citation-ssot` の規約）
- ⚠️ **コード変更** —— ★ `src-tauri/**` / `src/**` の差分ゼロ
- ⚠️ **2026 版の git 取り込み** —— ★ 研究者決定（2026-08-30）: **未追跡のまま書き換える**

## 受け入れ条件

- [ ] 提案書の見出しが **1〜8 ＋ 参考文献** の構造を保っている（`grep -c '^# '` で検算）
- [ ] 両文書に **`Wall` / `Monk Mode` / `Zen Timer` / `Early Unlock` が現行機能として登場しない**
      （★ 履歴記述としての言及は可・機械検査は「削除済み」の文脈語との共起で見る）
- [ ] 両文書に **`6特徴量` / `6つの特徴量` / `3クラス分類` / `3状態を推定` が主張として登場しない**
- [ ] 両文書に **`GPS` / `歩数` / `加速度` が本体の完了条件として登場しない**（★ 形成的トラックの言及は可）
- [ ] 両文書に **「不便益 HCI である」「不便益を測定可能にした」が登場しない**（`glossary.md` 禁止用語）
- [ ] **Phase1 の `DataInsufficient`** が両文書に書かれている（★ 研究者決定: 前面に出す）
- [ ] **表現チャネル**（ADR-017）が両文書に書かれている（⚠️ `de-risk 先行` の温度で）
- [ ] 提案書の予算が **9ヶ月 / 2,646,000円 = 2,100円/時 × 約1,260時間** のまま
- [ ] スケジュールが **Phase1 打ち切り後の実態（G1 / O1 / Phase 1.5）**に接地している
- [ ] `PYTHONUTF8=1 python scripts/check_citations.py` が **違反なし**
      （★ `docs/` 側を汚していないことの検算）
- [ ] `git status` で `src-tauri/` / `src/` に差分が無い

## 関連ドキュメント

| SSOT | 何のために読むか |
|---|---|
| `docs/research-positioning.md` | ★ **主張の SSOT**（§1 / §4 / §5 / §7 / §8 / §9 は 2026-08-30 に全面改訂） |
| `docs/adr/ADR-015-wall-removal.md` | ⚠️ Lv2 Wall / Zen Timer / Monk Mode の全削除 |
| `docs/adr/ADR-017-expression-channel-boundary.md` | ★ 表現チャネルの境界（D1–D10） |
| `docs/architecture/expression-channel.md` | ★ 表現チャネルの設計 SSOT |
| `docs/preregistration-v0.3.md` | ⚠️ 凍結された合否契約（PreReg-1〜8 / GATE1–3） |
| `docs/wbs-verification-halfyear.md` | ★ 26 週マイルストーン・Gate D/S/H（§改訂予定は**提案・未承認**） |
| `docs/glossary.md` | ⚠️ **禁止用語** |
| `.steering/20260830-expression-channel-ssot/decisions.md` | ★ EC-D1〜EC-D10 |
| `experiments/20260731-phase1-calibration-analysis/notes.md` | ★ **Phase1 の実測**（★ 2027 版の最大の材料） |
| `experiments/20260801-controlled-friction-task/README.md` | ★ **G1 の現況**（★ 次の一手） |
| `docs/literature/_index.md` | ★ サーヴェイ 4 ラウンドの結論 |

## 運用メモ

- **/reimagine 適用: No**
- 理由: ★ 本タスクは **既に確定した SSOT へ文書を合わせる**作業であり、
  設計判断そのものは `ADR-015` / `ADR-017` / `research-positioning.md` で既に裁かれている。
  ⚠️ 複数案が考えられる箇所（主役の置き方 / Phase1 の出し方）は
  **2026-08-30 に研究者へ直接確認して確定済み**（`decisions.md` D1 / D2）。
