# `.idea` 20260901 と既存確定事項の衝突監査（メイン自身の一次確認）

- 日付: 2026-09-02
- 方法: `.idea` の各主張について、**既存 ADR / SSOT docs / コードを実測**して照合した。
  記憶・過去の会話は根拠に使っていない（`verify-before-claiming`）。

---

## F1. ★★★ §15 の `L1〜L4` は**既存の層番号 3 系統と衝突する**

`.idea` §15.2 は「Mh-D 内部アーキテクチャを L1〜L4 と呼ぶ」と提案する。
しかし repo には **既に 3 つの層番号体系**があり、いずれも L1/L2 を別の意味で使っている。

| # | 既存体系 | 出典（実測） | L1 / L2 の意味 |
|---|---|---|---|
| ① | **7 層アーキテクチャ `[0]`–`[7]`** | `docs/architecture/gse-v2-overview.md` §2 | L1 = Domain Event Adapter / L2 = Privacy Boundary + Event Envelope |
| ② | **MhD / Need の層番号** | `docs/glossary.md` L14・L217 逐語「`p_stuck` は **MhD（L1）が計算する**」「**Need 層（L2）**が `stuck_likelihood` として閾値消費する」 | L1 = MhD 全体 / L2 = Need 層 |
| ③ | **表現層の 層 0–3** | `docs/glossary.md`（**18 箇所**）/ `docs/architecture/expression-channel.md`（9 箇所） | 層 0 = 状態に応答しない常在の基層 |

★ ① は `domain-adapter-boundary.md`（Layer 0-3）/ `intervention-decision-engine.md`（Layer 5-7）/
`personalization-and-online-learning.md`（Layer 3-4 拡張）/ `ADR-009`（Layer 4/5）が**全部この番号で書かれている**。

**`.idea` §15.2 の L1〜L4 を ① に重ねると:**

| `.idea` の L | 実体 | 既存の対応 |
|---|---|---|
| L1 Observation Representation | content-free イベント → 特徴・episode・観測可能性 | **既存 Layer 1–3** |
| L2 Momentary Work-State | friction / engagement / stuck / recovery_risk / uncertainty | **既存 Layer 4** |
| L3 Personal / Domain Adaptation | 個人・タスク適応 | **既存 Layer 3-4 拡張**（ADR-008 / ADR-009 / `personalization-*.md`） |
| L4 Longitudinal Profile | 複数セッションの長期プロファイル | ★ **新規（既存に対応なし）** |

→ ★ **新規性があるのは L4 だけであり、L1–L3 は既存 Layer 1–4 の別名である。**
→ ⚠️ **番号を新設すると 4 系統目になり、`docs/` 全体で L2 が 3 通りの意味を持つ。**

## F2. ★★★ §14.4 ② の「recovery を競合リスクとして扱う」は **ADR-009 D2 で 2026-08-01 に既決**

`.idea` は**新しい改善案として**提示しているが、ADR-009 D2 の逐語と**カテゴリが完全一致**する:

> `self_directed_recovery` = **離散時間の time-to-event 観測**である。… 幅 Δ の期 k = 1,2,… ごとに
> 次の 4 択を記録する: `recovery` / `externalized`（paste）/ `left_observation`（focus 喪失・アプリ切替）/ `still_stalled`。

さらに ADR-009 D2 は `.idea` より**先に進んでいる**:
- **H をラベル定義から外し、意思決定層の読み出しパラメータにした**（`.idea` §14.2 は `recovery_risk(H)` を出力に持たせたまま）
- **`left_observation` を「競合と真の打ち切りの混合」とし、両極端で上下界を取る**（新 G2）
- **点推定として測れると主張しない**という主張範囲の縮小を明記
- ★ stateless baseline を「正」とし、潜在状態を持つ候補を対抗馬に置く（D3）

→ ★ **`.idea` §14.4 ② に新規性は無い。** ただし `.idea` §14.4 ② が
「**離席やセッション終了を自動的に『回復失敗』とラベル付けしない**」と書いている点は ADR-009 と同旨で、**再確認として有効**。

## F3. ★★★ §14.4 ③ / ⑥（abstention・`evidence_quality`・`scope_fit`）は **ADR-010 で既決**

ADR-010 D1 逐語: 「走っている head が `scope_fit` を計算し、`WorkStateEstimate` の `evidence_quality` を
単調に減衰させ `uncertainty` を上げる」「`evidence_quality` 低下 → `none`/`defer`」。

★ しかも ADR-010 は `.idea` より**理論的に細かい**:
- **ambiguity rejection（境界近傍）と novelty rejection（分布外）を分ける**文献分類に接地
- `uncertainty` ＝ ambiguity / `evidence_quality` ＝ novelty に対応させ、
  ★ **`scope_fit` を `uncertainty` に足し込んで 1 本にしない**と明記
- **conformal outlier testing の特殊形**として接地 [V66]
- コード側にも到達済み: `src-tauri/src/analysis/heads/mod.rs` 逐語
  「`WorkStateEstimate` (`uncertainty` / `evidence_quality` 必須)」

→ ★ **`.idea` の「abstention を正式な推論出力にする」は既に契約に入っている。**
⚠️ 唯一の新規は **`insufficient_evidence` という *名前付きの出力値*** を作るかどうかだが、
ADR-010 D1 は逐語で「`NullHead` / `UnknownHead` を作らない」と決めており、**同じ轍を踏む危険がある**。

## F4. §14.4 ⑤（予測・介入・長期評価の学習分離）は **ADR-008 D1 / D4 で既決**

ADR-008 D1 の表が更新対象を層で限定し、D4 が
「**評価期間のデータが 1 バイトも推定に入らないなら PreReg-5 と両立する**」という会計基準を確定済み。
`.idea` §12.5 の表は ADR-008 D1 の表とほぼ同内容（★ `.idea` の方が粗い）。

## F5. ★★★ §14.2 の「新しい Stage 1〜4」は、**未踏提出資料が意図的に降ろした 4 段構成を復活させる**

実測（`docs/mitou_submission/mitou_pptx/…設計スライド.pptx.md` L206–L223）:

| Stage | モデル | 位置 |
|---|---|---|
| 1 | ルールベース ＋ HMM | **現在地。正（デフォルト）** |
| 2 | ロジスティック回帰（L2） | データ未達。Phase C で判断 |
| 3 | 勾配ブースティング | **主目標から外す** |
| 4 | 1D-CNN / TCN | **同上** |

★ スライドは「**Stage 3/4 を主目標から外した理由**」に **1 枚を割いて**いる:
「2026 年度版は Stage 4 までのロードマップを主要な技術的売りにしていた」
「**データが無いのに段を上げることは、この分野で最も再現性を壊す行為である**」。

→ ⚠️★★★ **`.idea` §14.2 の新 4 段（成熟段階としての Stage 1–4）を提出資料に入れると、
このスライドと正面から衝突する**。名前を変えた 4 段の再導入に読まれる危険がある。

## F6. ★★★ 「認知体力」は **`docs/glossary.md` の禁止用語に直撃する**

実測（`docs/glossary.md` 禁止用語表）:

> **認知リソースの消耗 / 回復 / リソースの補充**（Physical Anchor・休憩・自然曝露の文脈でのみ禁止）
> → 代替: **関与の低下 / 関与の再開**
> 理由: 限定資源モデル（ego depletion）の語彙であり、**その枠組みは死亡が確認済み**
> （[P199] RRR k=23・N=2,141 で d=0.04 / [P200] 事前登録 k=36・N=3,531 で d=0.06 / [P201] PEESE b=0.003）。
> ⚠️ **注意回復理論（ART）は限定資源モデルそのもの**であり、**事前登録された ART の検定は 5 本すべて null**（[P193]–[P197]）。

3 点を指摘する:

1. ★ **「体力」は貯蔵量メタファそのもの**である（減る・尽きる・回復する）。
   禁止された「消耗 / 回復 / 補充」と**同じ枠組みの語**であり、2026-09-01 に落としたばかりの語彙への逆戻りになる。
2. ⚠️ `.idea` §11.3 が提案する代替語「**負荷応答と回復のプロファイル**」は、**それ自体が禁止語「回復」を含む**。
   glossary の例外は既存指標名（`自力回復率` / `productive_manual_recovery_rate` / `打鍵再開`）**だけ**である。
3. ⚠️ **`.idea` 自身が語の危険を自認している** —— §15.5 逐語
   「介入に反応しなかった人を『**認知体力が低い**』と誤って学習しない」。
   ★ **人物評価（trait）に読める語を、内部構成概念にすら置かない方が安全**である。

★ 実測: **`認知体力` は `docs/` / `.claude/` / `src-tauri/src` / `src` に 1 件も存在しない**（まだ入っていない）。

## F7. ★★★ §7 の「双方向通信」は **ADR-017 D3 と正面衝突**（却下済み・条件付きで再検討可）

ADR-017 Alternatives 表の逐語:

> ★ **双方向イベント**（inbound の「歩いた」二値も作る） → 却下。
> **完了条件が「時間・往復」なのでセンサ量が要らず**、**PC が既に離席候補区間＋復帰を content-free に観測している**。
> ⚠️ かつ `data-privacy` の位置情報の空白が即ブロッカーになる。
> → ★ **D9 の条件が満たされたら再検討可**（★ **恒久否決ではない**）。

★ さらに **ADR-018 D4 が却下理由を一段強くしている**:
「完了判定を置かない ＝ **センサが寄与しうる判定が存在しない**」＝「要る余地が**構造的に**無い」（再燃しない）。

→ ⚠️★★★ **inbound を開くには (a) 新規 ADR ＋ (b) `data-privacy` の位置情報節（ADR-017 D9 のブロッカー）が要る。**

## F8. §7 の「Physical Anchor を PC から起動するか / スマホ側で選ぶか」は **語の問題に還元される**

ADR-018 D1 / D2 により **系は開始も完了も判定しない**ので、どちらの答えでも「**起動**」という語は使えない。
残る本当の問いは「**招待（invitation）を差し出す面はどちらか**」である。

## F9. §7 の `intervention_active` の扱いは **ADR-017 D2 で既に契約に入っている**

ADR-017 D2 の契約表: `level` = `stable` / `friction_rising` / `stuck` / `intervention_active`（**4 値のみ**）。
→ ★ 「表現イベントとして扱うか」は**既に「扱う」で確定済み**。
⚠️ 「介入専用のイベントに分けるか」は **D2 の 4 値契約の変更**にあたり、新規 ADR が要る。

## F10. §4.3 の閲覧モデルは **ADR-017 D6（2 層）を知らずに書かれている**

ADR-017 D6: 層 A（**強制曝露・≤4 秒で読み取れる**）と 層 B（**任意閲覧・数十秒**）を**別に設計する**。
[P153] 実端末ログ（N=134・1 か月）= 1 日約 40 回の 2–4 秒 ＋ 約 30 回の数十秒。
→ ★ `.idea` §4.3「通常時はユーザーが見たいときに閲覧する」は**層 B のみを書いている**。層 A の設計が欠けている。

---

## F11. §14.4 ④（観測特徴と推論特徴の分離）も **ADR-008 D1 + ADR-012 で既決**

ADR-008 D1 逐語（ADR-012 が引用）: 「**何を集めるか（superset）は dev / 研究者が決める。ML に委譲できない**」
「**superset を決めずに『全部集めてから学習器に選ばせる』もやらない**」。
★ ADR-012 はその「**どう決めるか**」まで埋めている —— 採否は **限界寄与(c) ≥ δ かつ null 超過**。
★ ADR-011 §5 は「収集済みの信号を推論へ流す」ことを **G1 判定に紐づけている**。

## F12. §14.4 ①（時間スケールの分離）は **event / episode / session まで既決。`profile` だけが新規**

- **episode**: `Decision Episode`（`personalization-and-online-learning.md §3.1` / ADR-008 D2 の `ContextBuilder`）
- **読み出し粒度**: `task-adaptation-and-scope-gating.md §3.4` 逐語「**推定は streaming・読み出しは Decision Episode**」
- ★ **`profile`（数日〜数週間）だけが既存に対応を持たない。**

---

## 総括（★ 一次確認後に 1 度修正した）

★ **`.idea` §14.4 の「改善案」7 件のうち、6 件（①の一部・②・③・④・⑤・⑥）は既に ADR で決まっている。**

| `.idea` §14.4 | 既決か | 既決の出所 |
|---|---|---|
| ① 時間スケールの分離 | **一部既決** | `Decision Episode`（personalization §3.1 / ADR-008 D2）。★ **`profile` のみ新規** |
| ② recovery を競合リスクに | **既決** | **ADR-009 D2**（4 カテゴリ逐語一致・2026-08-01） |
| ③ 不確実性と観測可能性を分ける | **既決** | **ADR-010 D1**（`uncertainty`＝ambiguity / `evidence_quality`＝novelty） |
| ④ 観測特徴と推論特徴の分離 | **既決** | **ADR-008 D1 ＋ ADR-012**（限界寄与 ≥ δ かつ null 超過） |
| ⑤ 予測・介入・長期評価の学習分離 | **既決** | **ADR-008 D1 / D4** |
| ⑥ abstention を出力契約に | **既決** | **ADR-010 D1**（conformal outlier testing [V66] に接地） |
| ⑦ 評価指標を accuracy 中心から変える | **部分既決** | ADR-009 の反証ゲート G2 等。★ **calibration / Brier / 時間依存 AUC の明示は薄い** |

→ ★★★ **真に新しいのは実質 1 点に収束する: 「複数セッションにまたがる長期プロファイル層（`.idea` の L4 / `profile` 時間スケール）」。**
⚠️ **そしてそれは、`.idea` 自身が「認知体力」と呼びたがっている当のものであり、F6 の禁止用語問題に直撃する。**

★ **この構造が本タスクの中心的な発見である** —— `.idea` §12–15 の大半は「既決の再発見」であり、
**新規に裁くべき設計判断は「長期プロファイル層を置くか、置くなら何と呼ぶか」の 1 点**に絞られる。
