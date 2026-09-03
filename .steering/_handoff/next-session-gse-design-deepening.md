# 次セッション用プロンプト — GSE 設計の深掘り（表現チャネル → 身体回帰 → Mh-D 再定義）

> 作成: 2026-09-02 / 前タスク: `.steering/20260901-mitou-doc-split/`
> ★ このファイルを **新セッションで丸ごと読ませてから** 作業を始める。

---

## 前提（CLAUDE.md の制約・省略不可）

1. **`/start-task` を先に起動する。** 該当コマンドを使わずに作業を始めない。
2. **docs/ の先読み**: `@docs/agent-shared.md` のリンクハブから該当 docs を先に読む。
3. **必須 Skill を Read してから手を動かす**: 本タスクでは
   `verify-before-claiming`（★ **本タスクの中核**）/ `citation-ssot`（`[Pn]`/`[Vn]` の append-only）/
   `literature-card`（落合フォーマット）/ `intervention-design` / `physical-anchor` /
   `hmm-analysis` / `ml-workflow`（§12–15 を扱うため）。
4. **サーヴェイ・WebSearch はサブエージェントへ委譲する**（メインで抱えない）。
   `docs/references.md` への append は **メインが直列で**行う（並列 append は採番が壊れる）。
5. **設計判断は `.steering/[task]/decisions.md` に記録する。** 確定したら **ADR を起票する**。
6. 完了時に `/cross-review` を実行（`-- <paths>` でパス限定）。

---

## このタスクの目的

★ **議論して設計を固める。** そのうえで、固まった内容で**未踏提出資料を更新する。**

⚠️ **順序を守ること** —— 先に提出資料を書き換えない。
★ **議論 → 検証 → 設計確定（ADR）→ 提出資料へ反映**、の順である。

---

## 入力 — GPT との議論をまとめた `.idea` ファイル

**`.idea/20260901-smartphone-state-externalization-and-physical-return.md`（814 行）**

⚠️★★★ **これは GPT との大まかな議論の記録であって、検証済みの設計ではない。**
★ 本タスクの前半は「**ここに書かれていることの真偽を確かめる**」ことである。

### 中身の構成

| 節 | 内容 | 本タスクでの扱い |
|---|---|---|
| §0–8 | スマートフォン表現の設計案 ＋ 身体回帰への接続 ＋ **未決事項 8 件**（§7） | ★ **議論して詰める**（下記 A） |
| §9 | **関連文献サーベイ（5 系統）** | ⚠️★★★ **真偽の確認が必要**（下記 B） |
| §10 | 中心仮説 ＋ **未検証領域 6 件** ＋ 次の形成的評価 5 件 | ★ 検証後に research-positioning へ還元 |
| §11 | **Mh-D の真意の再整理**（共通枠組み vs 個人適応 / オンライン学習 / 「認知体力」） | ★ **議論して詰める**（下記 C） |
| §12–14 | **4 段階 ML / HMM の見直し案**（現行 HMM の評価・7 つの改善案・最終判断） | ★ **議論して詰める**（下記 C） |
| §15 | **Mh-D を L1〜L4 として説明する案 ＋ M1〜M4 のモデル昇華** | ★ **議論して詰める**（下記 C） |

---

## A. 詰めるべき未決事項（§7 逐語・8 件）

- スマートフォンの第一媒体を **ロック画面 / ホーム画面 / 専用アプリ**のどれにするか
- 表現を**本人だけに見せるか、他者にも見える状態を許容するか**
- **4 イベントの表現意味**を固定する範囲と、本人が変更できる範囲
- `intervention_active` を表現イベントとして扱うか、**介入専用のイベントに分けるか**
- 表現から Physical Anchor の選択肢を出す**具体的な境界**
- Physical Anchor を **PC から起動するのか、スマートフォン側で本人が選択するのか**
- **双方向通信を許可する場合**のデータ境界と同意粒度
- 表現の可読性・自己状態の俯瞰・自律性を測る**最小プロトコル**

⚠️ **既存の確定事項と衝突していないかを必ず先に確認する**:
- **ADR-017**（表現チャネルの境界。D2 の契約 4 フィールド `level` / `seq` / `emitted_at` / **`epoch`**、
  D3 **PC → スマホの一方向・inbound を作らない**、D4 の S1–S6、D5 **音声の自動開始は範囲外**、
  D7 単独アームで headline 評価しない、D10 **身体活動センシングの恒久除外**）
- **ADR-018**（**系は開始も完了も判定しない** / 閾値・タイマー・カウントダウンを置かない /
  D5 評価量は **招待の受容 ＋ 機会保存の行動指標**）
- `docs/architecture/expression-channel.md`（表現チャネルの SSOT）
- ⚠️ **「双方向通信」は ADR-017 D3 と正面から衝突する。** 変えるなら**新規 ADR が要る**。

---

## B. ⚠️★★★ 文献サーベイの真偽確認（本タスクで最も重要）

§9 は **GPT が出した 5 系統のサーベイ**である。§346 逐語:

> この節は設計検討用のサーベイ記録であり、提出資料の確定参考文献一覧ではない。

⚠️★★★ **そのまま信じてはならない。** ★ **2026-09-01 のセッションで、同種のサーベイ記録に
実際の誤りが 3 件見つかっている**（一次に当たって初めて判明した）:

| 実例 | 何が違ったか |
|---|---|
| Grobelny et al. (2024) | ⚠️ **主題が「画面上の自然映像の実験」ではなかった**（実際は快楽的ソーシャルメディア利用。自然は比較条件） |
| Matthews et al. (2023) | ⚠️ **筆頭著者が別人**（Gerald ではなく **Julian** Matthews） |
| Bell et al. (2025) | ⚠️ **「約 30 分が *最適曝露時間*」は誤読**（実際は「自然と非自然の *差* が最大になる点」） |

→ ★ **必ず一次資料に降りること。** サブエージェントに次を要求する:
1. **DOI を Crossref / PubMed の raw JSON で検算**する（★ WebFetch の要約経由にしない）
2. **abstract の逐語**を取る。⚠️ **本文にしか無い数値は「本文より」と明示**する
3. ⚠️ **主題そのものが記述と合っているか**を見る（★ Grobelny の型の誤りはこれで見つかった）
4. **取れなかったものは「未取得」と書く**（★ 推測で埋めない）
5. ⚠️ **GSE に不利な結果・著者自身の留保を必ず併記**する

★ 確認が済んだものだけ `docs/references.md` に append する（**次番号は着手時に実測すること**。
2026-09-01 時点では `[P219]` / `[V89]`）。

### ⛔ 引用してはいけないもの（★ 既知・`.steering/20260830-mitou-2027-proposal-slimming/survey-notes.md` 末尾）

- **Alter et al. (2007) の disfluent font 効果** —— Meyer et al. (2015) が 17 実験・N=7,367 で否定
- **METR arXiv:2507.09089 の 19% を現在の事実として** —— 著者自身が historical と宣言
- **Kosmyna et al. "Your Brain on ChatGPT"** —— 本文冒頭に *"Preprint, under review"*
- **Fisher et al. (2015) を「主観と実測の乖離」の証拠として** —— 客観指標が 1 つも無い
- **Kruger & Dunning (1999) を「人は自己評価できない」証拠として** —— Nuhfer et al. (2017) が r=.60
- ⚠️★★★ **ART（注意回復理論）を Physical Anchor の理論基盤として** —— **限定資源モデルであり、
  事前登録された検定は 5 本すべて null**（2026-09-01 に `research-positioning.md` から外した）
- ⚠️ **「回復」「消耗」「リソースの補充」の語彙**（`docs/glossary.md` 禁止用語。→「関与の再開」）

---

## C. Mh-D / ML 段階の再定義（§11–15）

★ **ここが提出資料に最も効く。** 現行の未踏文書は **Stage 1〜4** で書いてあるが、
`.idea` §15 は **L1〜L4（内部レイヤー）と M1〜M4（モデル昇華）を分ける**案を出している。

⚠️ **確認すべき既存の確定事項**:
- **ADR-001**（HMM を writing baseline とする）/ **ADR-002**（domain-local inference）/
  **ADR-006**（`task_kind` → domain head。★ **2026-08-18 に配線済み**・`HMM_VERSION 0.5.0`）/
  **ADR-008**（オンライン学習の境界）/ **ADR-009**（recovery risk 軸と潜在状態）
- `docs/architecture/personalization-and-online-learning.md`（★ ADR-008 / 009 の設計文書）
- `docs/architecture/domain-adapter-boundary.md` / `intervention-decision-engine.md`
- ⚠️ **現行の実装**: `src-tauri/src/analysis/engine.rs` / `heads/` / `intervention.rs`

⚠️★★★ **「認知体力」という語を新設するなら、`docs/glossary.md` の禁止用語と衝突しないか必ず確認する。**
★ §11.3 は「内部の長期構成概念として扱う」としているが、**限定資源モデルの語彙に戻っていないか**を見ること
（★ 2026-09-01 に ego depletion / ART を落としたばかりである）。

---

## 進め方（★ この順序で）

1. **`/start-task`** で作業記録を作る
2. **`.idea` の全文を読む**（814 行）★ メインが読む。要約させない
3. **B（文献の真偽確認）をサブエージェント並列で回す** —— ★ 5 系統を分割して投げる
4. ⚠️ **結果をメインが検算する**（★ サブエージェントの報告も一次ではない。
   2026-09-01 は code-reviewer が**メイン自身の誤りを 1 件**見つけた）
5. **A と C を研究者と議論して詰める** —— ★ **`AskUserQuestion` で選択肢を出す**。
   ⚠️ **勝手に決めない**（CLAUDE.md 禁止事項「曖昧な指示に対して推測で実装しない」）
6. **確定したものを ADR に起票する**（★ ADR-019 以降。既存 ADR の本文は書き換えない）
7. **`docs/` の SSOT を更新**（`expression-channel.md` / `research-positioning.md` / `glossary.md` ほか）
8. ★ **最後に未踏提出資料へ反映**（下記）

---

## D. 未踏提出資料への反映（★ 最後にやる）

★ **2026-09-02 に構成が変わっている。** 場所と生成器を間違えないこと。

```
docs/mitou_submission/
├── README.md          ← ★ 運用の SSOT。先に読む
├── mitou_docs/        ← .docx 出力（4 本）: 詳細資料 / 技術設計書 / 検証レポート / 参考文献
└── mitou_pptx/        ← .pptx 出力（1 本）: 設計スライド
```

| 文書 | 更新の観点 |
|---|---|
| **設計スライド**（`.pptx.md`） | ★ A / C の結論を全体像として |
| **技術設計書**（`.docx.md`） | ★ **厳密な定義と契約だけ**。L1〜L4 / M1〜M4 を採るならここ |
| **検証レポート**（`.docx.md`） | ★ §10 の未検証領域 6 件と形成的評価 5 件 |
| **参考文献**（`.docx.md`） | ★ B で**確認が済んだものだけ**。⚠️ 番号は恒久・**欠番 36-38 / 50 を埋めない** |
| **詳細資料**（`.docx.md`） | ⚠️★★★ **10 ページ規約を超過中**（下記） |

### ⚠️ 注意 4 点

1. ⚠️★★★ **詳細資料は約 10.7 ページで、10 ページ規約を超過している**（未解決）。
   ★ **足すなら同量を削るか、補足資料 4 本のどれかへ移すこと。**
2. ⚠️★★★ **提出文書に `★` / `⚠️` を使わない。** `scripts/check_doc_lexicon.py` が機械検出する
   （★ 2026-09-02 に 5 本すべてを検査対象に入れた。それまで 3 本が素通りしていた）。
3. **再生成は拡張子で分かれる**:
   ```bash
   for f in docs/mitou_submission/mitou_docs/*.docx.md; do
     PYTHONUTF8=1 python scripts/md2docx.py "$f" "${f%.md}" --unescape
   done
   for f in docs/mitou_submission/mitou_pptx/*.pptx.md; do
     PYTHONUTF8=1 python scripts/md2pptx.py "$f" "${f%.md}" --unescape
   done
   ```
4. ⚠️ **`.pptx` は `---` で 1 枚に割れる。** 1 枚 150〜300 字が目安（★ 400 字超は表スライドのみ）。

---

## 触ってはいけないもの

- ⚠️ **`docs/preregistration-v0.3.md`** —— **凍結文書**。ずれは記録として残す
- ⚠️ **過去 ADR の本文**（ADR-001〜018）—— 改訂は**新規 ADR の追補**で行う（ADR-012 / ADR-018 の先例）
- ⚠️ **`.steering/` の過去の記録** —— 書かれた時点の事実である（旧パス参照も直さない）
- ⚠️ **`docs/design-history.{md,ja.md}`** —— 履歴文書
- ⚠️ **`src-tauri/` / `src/`** —— ★ **本タスクは設計の議論であり、コード変更は想定しない**
  （★ 変更が要る結論になったら、**別タスク・別ブランチ**に切る）

---

## ★ 未マージのブランチ（着手前に確認する）

2026-09-02 時点で **4 本が `main` へ未マージ**である。⚠️ **議論の前提が変わるので先に状態を見ること。**

| ブランチ | 内容 |
|---|---|
| `docs/research-positioning-fix` | ART / ego depletion を落とし「関与の再開」へ。references `[P192]`–`[P218]` を append |
| `docs/runbook-wall-cleanup` | 削除済み Wall に依存する runbook 手順の除去 |
| `docs/stale-sweep` | docs 全体の陳腐化一掃（138 件）。★ **`agent-shared.md` の一行説明も直っている** |
| `docs/mitou-doc-split` | ★ **未踏提出資料の 5 本化 ＋ `mitou_submission/` への再編**（本タスクの D が前提にする） |

---

## 横断してほしい他分野（研究者の要望）

★ 研究者は「**他分野も横断しながら固めたい**」と述べている。★ サーベイの angle 候補:

- **HCI / CSCW**: ambient display / peripheral awareness / calm technology / reflective design
- **認知科学・心理学**: metacognition / self-regulated learning / effort-based decision making
  （⚠️ **限定資源モデルには戻らない**）
- **臨床・行動医学**: JITAI / micro-randomized trial / behavioral activation の prompt 設計
- **人間工学 / 労働科学**: break scheduling / 自律性と回復（★ [P215]–[P217] が既にある）
- **ML**: uncertainty quantification / abstention / calibration / conformal prediction
  （★ §14 の abstention 案に直結する）
- **デザイン学**: 不便益（★ 既に [P170]–[P174]）/ slow technology / ambiguity as a resource
