# 次セッション用プロンプト — 表現チャネル（A: `.idea` §7 の未決事項 8 件）

> 作成: 2026-09-02 / 前タスク: `.steering/20260902-gse-design-deepening/`
> ★ このファイルを **新セッションで丸ごと読ませてから** 作業を始める。

---

## 前提（CLAUDE.md の制約・省略不可）

1. **`/start-task` を先に起動する。**
2. **docs/ の先読み**: `@docs/agent-shared.md` のリンクハブから該当 docs を先に読む。
3. **必須 Skill を Read してから手を動かす**: `verify-before-claiming`（★ **中核**）/ `citation-ssot` /
   `literature-card` / `intervention-design` / `physical-anchor` / `data-privacy`。
4. **サーヴェイ・WebSearch はサブエージェントへ委譲する**。`docs/references.md` への append は**メインが直列で**。
5. 設計判断は `.steering/[task]/decisions.md` に記録し、確定したら **ADR を起票**する（★ **ADR-021 以降**）。
6. 完了時に `/cross-review`（⚠️ **`.docx` / `.pptx` のバイナリを含むと Step 2 の fail-closed に当たる**。
   ★ `-- docs scripts ':!*.docx' ':!*.pptx'` のようにパス限定して回す）。

---

## 前セッション（2026-09-02）で **閉じたもの** — ★ 蒸し返さない

| 軸 | 状態 |
|---|---|
| **B. 文献の真偽確認** | ✅ **完了**（`.steering/20260902-gse-design-deepening/survey-verification.md`） |
| **C. Mh-D / ML 段階** | ✅ **完了** → **ADR-019** / **ADR-020** |
| Stage 4 サーヴェイ | ✅ **完了**（`stage4-survey.md`・3 系統） |

★ 併せて `docs/references.md` に **43 件**を append 済み（`[P219]`–`[P238]` / `[V89]`–`[V111]`）。
→ ⚠️★★★ **次番号は着手時に実測すること**（★ 2026-09-02 時点で **`[P239]` / `[V112]`**）。

---

## このセッションの目的 — **A: `.idea` §7 の未決事項 8 件**

**入力**: `.idea/20260901-smartphone-state-externalization-and-physical-return.md` **§0–8**
（⚠️★★★ **追跡外＝ SSOT ではない**。§9–15 は前セッションで裁き済みなので**読み直さなくてよい**）

⚠️★★★ **§9 のサーベイ記録には重大な誤りが 5 件あった**（`survey-verification.md`）。
→ ★ **§0–8 の記述も同じ精度で疑うこと。** 特に「先行例がある」「〜が示されている」型の主張。

### 8 件と、**既に分かっている前提**（★ `conflict-audit.md` F7–F10・実測済み）

| # | 未決事項 | ⚠️ 既存の確定事項との関係 |
|---|---|---|
| 1 | スマホの第一媒体（**ロック画面 / ホーム画面 / 専用アプリ**） | ★ **ADR-017 D1 は「媒体は交換可能な実装詳細」**とし、主張の所在に置かないと決めている。★ **D6 が曝露を 2 層に割っている**（層 A = 強制曝露 **≤4 秒** / 層 B = 任意閲覧 数十秒。[P153] N=134・1 か月の実端末ログ） |
| 2 | **本人だけに見せるか、他者にも見えるのを許容するか** | ⚠️ **ADR-017 の未決 PS-Q5 そのもの**（「本人 / 他者を THAT・WHAT・HOW のどの段で止めるか」）。★ ADR-017 は **試作の試視でしか埋まらない**としている（`experiments/20260812-expression-step4-grain/player/step4.html`） |
| 3 | **4 イベントの表現意味**を固定する範囲と、本人が変更できる範囲 | ★ **ADR-017 D2 が `level` の 4 値を契約として確定済み**（`stable` / `friction_rising` / `stuck` / `intervention_active`）。⚠️ 変えるなら新規 ADR |
| 4 | `intervention_active` を表現イベントとして扱うか、**介入専用に分けるか** | ⚠️★★★ **「扱う」は既に決まっている**（D2 の 4 値に入っている）。★ 残る問いは **分けるかどうか**だけで、分けるなら **D2 の契約変更＝新規 ADR** |
| 5 | 表現から Physical Anchor の選択肢を出す**具体的な境界** | ★ **ADR-017 D7**（表現層は Physical Anchor を出口として持つ／単独アームで headline 評価しない）＋ **ADR-018 D5**（評価量は**招待の受容 ＋ 機会保存の行動指標**） |
| 6 | Physical Anchor を **PC から起動するか、スマホ側で本人が選ぶか** | ⚠️★★★ **ADR-018 D1/D2 により系は開始も完了も判定しない** → ★ **「起動」という語が使えない。** 問いは「**招待を差し出す面はどちらか**」に還元される |
| 7 | **双方向通信**を許可する場合のデータ境界と同意粒度 | ⚠️★★★ **ADR-017 D3 と正面衝突**（Alternatives で却下済み）。★ **ADR-018 D4 が却下理由を「要る余地が構造的に無い」へ強化**している。⚠️ **恒久否決ではない** —— ★ 開くには **(a) 新規 ADR ＋ (b) `data-privacy` の位置情報節**（**ADR-017 D9 のブロッカー**・★ 2026-08-30 実測で**規定は 1 行も無い**）が要る |
| 8 | 可読性・自己状態の俯瞰・自律性を測る**最小プロトコル** | ★ **ADR-017 D7 の「単独アームで評価しない」**と **ADR-018 D5 の評価量**が制約。⚠️ **[P229]**（盲検独立評価で state 検出 **R² 1–3%**）と **[P163]**（★ 著者は「**表示するトラッカーを避けよ**」と勧告）を踏まえること |

### ★ §4.3 の閲覧モデルの穴（★ 前セッションで発見）

`.idea` §4.3「通常時はユーザーが見たいときに閲覧する」は **層 B しか書いていない**。
→ ★ **ADR-017 D6 の層 A（強制曝露・≤4 秒で読み取れる）の設計が欠けている。**

---

## ★ サーヴェイの angle 候補（★ 研究者は「他分野も横断しながら固めたい」と述べている）

⚠️★★★ **前セッションで「引くな」と判定された文献がある。** ★ **`survey-verification.md` を先に読むこと。**

| ⛔ 引かない | 理由 |
|---|---|
| **An et al. (2024) EmoWear** | ⚠️ **主題が別物**（スマートウォッチの音声メッセージ・**content 解析に依存**・送り手が手で選ぶ） |
| **Liu et al. (2021) Significant Otter** | ⚠️ **過剰主張**（biosignals は**実測の生理信号であって潜在状態ではない**・宛先は恋人） |
| **Mainsbridge et al. (2020)** | ⚠️★★★ **設計思想が逆**（著者が *hostage screen* と呼ぶ**全画面ブロッキング**＝ **ADR-015 で削除した Wall に相当**） |
| **Upshaw et al. (2022)** | ⚠️ **主観を一切測っていない**（RT の効果は **d=.04**・**論文自身の abstract が誇張**） |
| **Alqahtani et al. (2022)** | ⚠️ **メモのタイトルが実在しない**。実物は身体活動トラッキングで、**効いた手がかりは地図とタイムライン**＝ **ADR-017 D10 で恒久除外した位置情報** |
| ART / ego depletion / 「回復・消耗・補充」の語彙 | ⚠️ `docs/glossary.md` 禁止用語 |

★ **横断の候補**: ambient display / peripheral awareness / calm technology / reflective design ／
metacognition / self-regulated learning ／ JITAI・MRT の**提示面の選択**（★ [V87] が既にある）／
break scheduling と自律性（★ [P215]–[P217]）／ 不便益（★ [P170]–[P174]）／ slow technology（★ [P104] [P185]）。

---

## ⚠️★★★ 研究者判断が要る繰り越し 1 件（★ 前セッションの `/cross-review` 指摘）

**`docs/preregistration-v0.3.md` に「Stage-2 昇格時に…」という旧呼称が残っている。**
★ ADR-019 D1 が呼称を **M1〜M4** に変えたが、**凍結文書は書き換えない**方針なので触っていない。

- ★ **手続き上は問題ない**（PreReg-1〜8 の凍結条項に「+3%」判定量は含まれていない）。
- ⚠️ ただし **2026-06-28 に、凍結文書内へ addendum ブロックを追記した先例がある**（`:7`–`:21`）。
  → ★ **その先例に倣って 1 行の注記を足すか、足さない理由を研究者判断として明記するか**を決める。

## ★ その他の繰り越し（★ 優先度順）

1. ⚠️★★★ **`.pptx` を Google Slides で実地確認**（★ `python-pptx` 生成に切り替えたが**未検証**。
   ⚠️ **前回も機械検査は全部緑だった**）。★ 併せて **`.docx` を Google Docs で**（症状は出ていないが同型）。
2. ★ **`docs/references.md` の新規「逐語」引用のサンプル照合**（★ `/cross-review` の残存リスク第 1 位。
   ⚠️ レビュー側はネット非接続で**原典照合ができていない**）。→ `literature-card` Skill で数件。
3. **ADR-019 D6 の実装** —— 語・文境界のリズム特徴を `features.rs` へ。
   ★ **別タスク・別ブランチ**。⚠️ 採否は **ADR-012 の手続き**（限界寄与 ≥ δ かつ null 超過）で決める。
4. 出版版 **UMUAI 33(3):617-641** の本文入手
   （★ 「タイミングのみの特徴群は κ=0.018–0.050」が **2 系統で食い違っており未確定**）。
5. ⚠️ **[V103] の N/T 数値は二次引用**（★ 本文未到達）—— 提出資料で使うなら原本を入手する。
6. ★ **Stage 4 の逆側の探索を 1 ラウンド**（★ **self-supervised pre-training による小標本 HAR が未探索**）。

---

## 触ってはいけないもの

- ⚠️ **`docs/preregistration-v0.3.md`** —— **凍結文書**（★ 上記の研究者判断が出るまでは触らない）
- ⚠️ **過去 ADR の本文**（ADR-001〜020）—— 改訂は**新規 ADR の追補**で行う
- ⚠️ **`.steering/` の過去の記録** —— 書かれた時点の事実である
- ⚠️ **`docs/design-history.{md,ja.md}`** —— 履歴文書
- ⚠️ **`docs/mitou_submission/mitou_docs/[提案プロジェクト詳細資料]GSE_proposal.docx.md`**
  —— ★ **10 ページ規約を超過中**（約 10.7 ページ）。★ **足すなら同量を削るか、補足資料 4 本のどれかへ移す**

## ★ 提出資料の再生成（★ 前セッションで作法が変わった）

```bash
for f in docs/mitou_submission/mitou_docs/*.docx.md; do
  PYTHONUTF8=1 python scripts/md2docx.py "$f" "${f%.md}" --unescape
done
for f in docs/mitou_submission/mitou_pptx/*.pptx.md; do
  PYTHONUTF8=1 python scripts/md2pptx.py "$f" "${f%.md}" --unescape
done
PYTHONUTF8=1 python scripts/check_doc_lexicon.py   # ★ 提出 5 本すべてが対象
```

- ★ **`md2pptx.py` は `python-pptx` に依存する**（`pip install -r scripts/requirements-dev.txt`）。
- ★ **出力は再現可能**になった（ZIP の日時を固定）。★ **内容が同じなら差分が出ない。**
- ⚠️ **提出文書に `★` / `⚠️` を使わない**（`check_doc_lexicon.py` が機械検出する）。
- ⚠️ **`.pptx` は `---` で 1 枚に割れる。** 1 枚 **150〜300 字**が目安（★ 400 字超は表スライドのみ）。
