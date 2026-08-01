# 次セッション開始プロンプト — `.idea` 2 本を単一の設計へ統合し ADR-008/009 を起票する

このファイルの「===」以下をコピペして開始する。

**前提**: 本タスクは**コード変更ゼロ**の設計・文書タスク。凍結対象には触れない。
モデルは **Opus**（設計判断・やり直しが効かない）。

---

===

`.idea/20260801-architecture-signal-and-online-learning.md`（以下 **doc#1**）と
`.idea/20260801-behavioral-context-online-latent-ml-design.md`（以下 **doc#2**）を精査し、
既存の v2 アーキテクチャ SSOT に接地させて **単一の設計**へ統合する。

## §0 前セッションで確定済み（再度問わない）

ユーザー承認済みの 2 点:

1. **成果物の形 = 統合設計文書 + ADR-008/009**。
   `docs/architecture/` に統合設計文書を 1 本立て、決定事項を ADR-008
   （個人適応・介入効用・online latent state の境界）と ADR-009 に切り出す。
   `.idea` は gitignore・追跡外なので **SSOT にしない**。コード変更ゼロ（Epic 1 と同じ形）。
   *理由*: ADR だけだと「なぜその決定に至ったか」の文脈（段階実装計画・評価指標・
   ContextSnapshot の具体形）が入りきらない。

2. **X 軸の扱い = 両立させる**。
   doc#2 の再定義（`self_directed_recovery_risk`）を採りつつ、doc#1 §7.3 優先1 の
   統制タスク実験を「**再定義後の軸に対しても必要な反証ゲート**」として設計文書に組み込む。
   *理由*: 軸を別の量に書き換えても「打鍵由来の content-free イベントで分離できるか」は
   未検証のまま。設計は今進め、実験は凍結解除後の最初のタスクに置く。

## まず読む（着手前・この順）

1. `docs/architecture/gse-v2-overview.md` — **アーキテクチャ SSOT**（7 層・Epic ロードマップ・
   エビデンスの温度）。統合先はここ。
2. `docs/architecture/domain-adapter-boundary.md` — Layer 0-3 詳細（`EventEnvelope` /
   `DomainAdapter` / `WorkStateEstimate` / `DomainInferenceHead` の trait 案）
3. `docs/architecture/intervention-decision-engine.md` — Layer 5-7 詳細（Opportunity /
   Receptivity / Decision Engine / 現行閾値）
4. `docs/adr/README.md` と ADR-001〜007（**ADR-006 は前セッションで読了**。
   残り 6 本は未読）
5. `.idea` doc#1 / doc#2（**両方とも前セッションで読了**。下の §不一致表がその要約）
6. `docs/research-positioning.md`（§5 仮説 H-X1 / §8 成功基準・**未読**）
7. `docs/preregistration-v0.3.md`（**凍結**・PreReg-5 の文面を確認する目的で・未読）
8. Skill: `citation-ssot`（外部文献を引くため必須。doc#2 は外部 URL を 9 本引いており
   `docs/references.md` への `[Pn]`/`[Vn]` 登録が要る）/ `architecture-rules` / `git-workflow`

## 統合の本体 = 2 本の間の不一致を裁定すること

そのまま merge すると「両論併記だが何も決まっていない文書」になる。
前セッションで洗い出した実質的な食い違いは **6 件**:

| # | 論点 | doc#1 | doc#2 | 前セッションの裁定 |
|---|---|---|---|---|
| 1 | **X 軸** | §7.3 優先1「X 軸そのものを疑え。統制タスクで先に棄却/確認」= 実験で殺す | §0「`self_directed_recovery_risk` へ再定義」= 設計で作り直す | **両立**（§0-2・確定） |
| 2 | **online EM** | §3-D「**本命候補**」 | §0/§8「初期実装の中心ではない」→ **Phase 4 へ降格** | **未裁定**。doc#2 が doc#1 を上書きしている。ADR にするなら「なぜ本命を降格したか」が Decision 本体 |
| 3 | **ラベル計器** | §7.3 優先2「リッカート廃止 → 強制比較 / イベント直後プローブ」 | §5「helpful/unhelpful の binary feedback（KTO 的）」 | **未裁定**。別物か統合か。`probe_scheduler.rs` は凍結対象 |
| 4 | **PreReg-5 衝突** | §5-a「"正規化層は測定器の一部"は詭弁ではないか」= 未解決 | §6.1 replay 3 モードで部分回答・§11-6 で**まだ未解決** | **未裁定**。prereg 改訂の要否に直結 |
| 5 | **ADR-006 との関係** | §3-C「head が持つものを β だけでなく criterion と写像係数まで**広げる拡張**」 | §3.2「ADR-002/006 の方針を**引き継ぐ**」 | **未裁定**。ADR-006 の拡張か新 ADR か |
| 6 | **潜在状態の定義 ★前セッション終盤に発見** | （明示なし） | §4.1 の 4 状態 = `Progress / Stagnation / ExternalizationPressure / **Receptivity**` | **未裁定**。既存 SSOT の `WorkStateEstimate`（friction/stuck_likelihood/engagement/incubation_like_pause/flow_like_continuation + uncertainty + evidence_quality）と**別体系**。さらに **doc#2 は Receptivity を潜在状態に置くが、既存 SSOT では Receptivity は Layer 5（Opportunity 側）で ADR-007 が「分解維持」を採択済み** — 同じ語が別の層にある |

**#6 が最も危険**。放置すると「Layer 4 の Receptivity」と「Layer 5 の Receptivity」が並立し、
ADR-007 の決定が静かに無効になる。用語の SSOT は `docs/glossary.md`。

## 既存 SSOT との対応（前セッションで確認済み・再調査不要）

doc#2 §7 の実装境界案は、既存 v2 の 7 層と**ほぼ対応している**:

```
doc#2:  DomainAdapter → EventEnvelope → ContextBuilder → DomainInferenceHead
        → PersonalizationStore → InterventionPolicy → OutcomeRecorder → OnlineUpdater
既存:   [1]Adapter → [2]Envelope → [3]domain features → [4]WorkStateProxy
        → [5]Opportunity/Receptivity → [6]DecisionEngine → [7]Outcome&Harm
```

**doc#2 が持ち込む真に新しい部品は 3 つだけ**:
- `PersonalizationStore`（user × task_kind × phase の profile をローカル保持）
- `OnlineUpdater`（profile と介入効用**のみ**を更新）
- `ContextBuilder` / Decision Episode（収集単位を raw event から episode へ）

→ **ADR-008 の本体はこの 3 つの境界**と見てよい。`OutcomeRecorder` は既存 Layer 7 に相当。

## 前セッションの成果が入力を 1 つ壊している ★必ず反映する

doc#1 §3-B は「**ICC が 0.06〜0.16 と低いことは強めに縮約すべき根拠になる**」と書き、
doc#2 §4.2 の partial pooling の強さがそれに乗っている。

しかし `.idea` の 0.060/0.055/0.159/0.156 は **ICC ではなく η² = SSB/SST** だった
（PR #83 で特定・`experiments/20260801-signal-diagnostics/notes.md` §2-C）。
正しい **ICC(1) は 0.080/0.073/0.204/0.200**、LOO 範囲 0.050–0.302。

→ **方向（個人差は小さい → 個人適応は写像係数側）は変わらないが、縮約の根拠としては弱くなる**。
統合文書では点推定でなく「概ね 0.05–0.30、被験者 5 名で不確実性大」と書き、
`.idea` の 4 値は引かない。加えて Codex 指摘（doc#1 §9-4）の
「"個人差" と解釈したものが実は作業種別差かもしれない」を併記して温度を保つ。

## 制約（厳守）

- **凍結対象には触れない**（Phase1 完了まで変更禁止）:
  `schema_dto.rs` / `schema/current.json` / `engine.rs` HMM_VERSION / `loop_step.rs` /
  `intervention.rs` 定数 / `probe_scheduler.rs` / `App.tsx` argumentative lock /
  `preregistration-v0.3.md`。
  → PreReg-5 の衝突（#4）は「**新バージョンで何を変えるべきか**」のメモまで。実改訂はしない。
- **コード変更ゼロ**。Epic 1（ADR 群）と同じ形。
- **過大主張の禁止**: `gse-v2-overview.md` §5「エビデンスの温度」に従う。
  doc#2 は行動経済学の概念を多く採るが、**ユーザーの性格特性を推定する設計にしない**
  （doc#2 §2.3 が既に personality inference を棄却している。この線を統合文書でも維持する）。
- `.idea` は追跡外。統合文書ができたら `.idea` 側には「→ docs/architecture/… へ昇格」とだけ書く。

## やらないこと（スコープ外）

- 統制タスク実験（doc#1 §7.3 優先1）の**実施**。設計文書に反証ゲートとして書くところまで。
- `probe_scheduler.rs` のラベル計器の**実装**。凍結対象。
- Epic 2 以降の実装着手。
- ADR-006 の再検討（Accepted・下位決定 #2/#3 も確定済み）。**拡張の要否**だけ #5 で判断する。

## 進め方

1. `/start-task` で grill → `.steering/[YYYYMMDD]-architecture-consolidation/` を作る。
   grill では上の**未裁定 5 件（#2〜#6）を閉じる**ことを目標にする。
2. **`/reimagine` を適用する**（CLAUDE.md: アーキテクチャ判断・複数案がある設計）。
   特に #6（潜在状態の定義）は 4 状態案と既存 `WorkStateEstimate` の 2 案があるので、
   初回案を破棄して再生成した案と比較する価値が高い。
3. 設計の第二意見が要れば `codex-consult`。
   **⚠️ `.codex/budget.json` が日次上限を超過している**（2026-08-01 時点 363,718/200,000）。
   呼ぶ前に必ず残量を確認すること。
4. 完了時に `/finish-task`（`/cross-review` = TASK-POST 含む）。

## 現在の状態

- ブランチ `main` / コミット `ac093fb`（PR #83 マージ済み）。
- **ユーザーの Loop Engineering 導入作業が未コミットで並行している**（30 ファイル前後）。
  → **`git add` は必ずパス指定**。`git add -A` / `git commit -a` を使わない。
- `docs/adr/` は ADR-001〜007 + README が存在。`docs/architecture/` は 3 本。
  （前セッションで一度「空」に見えたのは作業ディレクトリの誤りで、実際は存在する）
