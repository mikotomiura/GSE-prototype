# 次セッション開始プロンプト — `.idea` 2 本を単一の設計へ統合し ADR-008/009 を起票する

このファイルの「===」以下をコピペして開始する。

**前提**: 本タスクは**コード変更ゼロ**の設計・文書タスク。凍結対象には触れない。
モデルは **Opus**（設計判断・やり直しが効かない）。

---

===

**このタスクは「2 本を merge する」作業ではない。** doc#2 は方向性の質は高いが SSOT の
要件を満たしておらず、そのまま昇格させると `[V40]` との矛盾と 4 状態の定式化の破綻が
SSOT に入り込む。**§SSOT 昇格の前提が満たされていない を必ず読み、前提を潰してから統合する。**

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
| 6 | **潜在状態の定義 ★最重要** | （明示なし） | §4.1 の 4 状態 = `Progress / Stagnation / ExternalizationPressure / **Receptivity**` | **未裁定**。既存 SSOT の `WorkStateEstimate`（friction/stuck_likelihood/engagement/incubation_like_pause/flow_like_continuation + uncertainty + evidence_quality）と**別体系**。さらに **doc#2 は Receptivity を潜在状態に置くが、既存 SSOT では Receptivity は Layer 5（Opportunity 側）で ADR-007 が「分解維持」を採択済み** — 同じ語が別の層にある。→ **層跨ぎ以外にも定式化の破綻が 5 点ある。下の §SSOT-(A) を必ず読むこと** |

**#6 が最も危険**。放置すると「Layer 4 の Receptivity」と「Layer 5 の Receptivity」が並立し、
ADR-007 の決定が静かに無効になる。用語の SSOT は `docs/glossary.md`。

---

## §SSOT 昇格の前提が満たされていない ★着手順序に影響・前セッション終盤の精査結果

**「統合する」より先に「昇格の前提を満たす」作業が要る。**
doc#2 は方向性と自己抑制（§2.3 の棄却リスト = personality inference / 完全な IRL /
social norm を明示的に棄却）は質が高いが、**そのまま SSOT へ昇格させてはいけない**。
前セッションで確認した具体的な不備は 3 層ある。

### (A) 4 状態の定式化そのものが破綻している（#6 の深掘り）

`Progress / Stagnation / ExternalizationPressure / Receptivity`（doc#2 §4.1）の問題:

1. **categorical な潜在状態の前提を満たさない**。§4.1 は
   `z_t ~ p(z_t | z_(t-1), context_t, head)` と書いており**相互排他**を主張するが、
   Receptivity は Progress と排他ではない（前進しながら受容的でありうる）。
   4 つは 1 つの潜在次元の分割になっていない。
2. **Receptivity は観測の放出元ではない**。その入力（cooldown / daily_cap /
   recent_dismiss / time-of-day）は**システム状態と履歴**であって潜在状態からの
   放出ではない。HMM の状態に置くと放出モデルが書けない。
3. **ExternalizationPressure は「状態」でなく「傾向」で、§0 と機能が重複し循環している**。
   §0 は X 軸を `self_directed_recovery_risk` と定義し、§4.1 は別に
   `recovery_t ~ p(recovery_t | z_t, ...)` を置く。外部化圧力が状態でそこから回復確率を
   出すのか、回復確率が軸なのかが決まっていない。
4. **既存 `WorkStateEstimate`（連続 proxy 5 つ）への写像が未定義**。
   `self_directed_recovery_risk` はそもそも `WorkStateEstimate` に無いフィールド。
5. **「4」の根拠がない**。Phase1 の 3 状態は「HMM の形をしたルールベース」（doc#1 §2-3）で
   手で選んだ状態だった。3 → 4 にしただけでは同じ轍。doc#1 §4.3 は「教師なし学習は
   クラスタを作るが Stuck は作らない」と警告したが、**状態を固定しても識別可能になる
   わけではなく、失敗が「ラベルの入れ替わり」から「データ中の何にも対応しない状態」へ
   移るだけ**。§9 の評価指標にも「状態が退化していないか」の検査がない。

**代案（決め打ちではなく設計セッションで裁定する候補）**:
潜在状態は**相互排他で放出が分かれる作業モード**に限る
（例: `Progressing / Stalled / Externalizing` — それぞれ打鍵継続 / 無音・修正ループ /
外部化イベントと放出が対応する）。その上で:
- `self_directed_recovery_risk` = Layer 4 の**出力**（`WorkStateEstimate` の additive な
  新フィールド・ADR-005）
- `ExternalizationPressure` = 状態でなく recovery risk の構成要素
- `Receptivity` = Layer 5 に戻す（ADR-007 の分解維持を維持）

### (B) 行動経済学の接地に、装飾的な箇所と SSOT 同士の矛盾がある

**良い部分（そのまま活かす）**: §2.3 の棄却リスト。§2.1-D の
「ユーザーの ambiguity aversion を測るのでなく**モデル自身の不確実性**を保存する」
という転換。**MRT/JITAI（§5・§6.2）の使い方は正確で、閉ループ評価の設計として
そのまま SSOT 品質**（decision point / proximal outcome / 無作為化 / propensity ログ）。

**直さないと昇格できない部分**:

1. **★ §2.1-F（選択アーキテクチャ・個人化ナッジ）が `[V40]` と正面衝突する**。
   `gse-v2-overview.md` §5 と `references.md [V40]` は
   「ナッジ assistance 系（GSE Lv1 Nudge 近似）は d=0.22 → **補正後 0.01**（BF01≈9）」
   「Motivation Generator を標準実装しない」と書いている。doc#2 §2.1-F は個人化ナッジ
   （どの形式・強度・タイミングで出すか）を採用候補に置きながら **[V40] に一言も触れていない**。
   `.idea` の中なら私見で済むが、**昇格すると SSOT 同士が矛盾する**。
   → 採否を決め直す。採るなら「なぜ補正後 d≈0.01 の領域に投資するのか」の説明が要る。
2. **A・D・E は行動経済学が無くても導ける**（A の非対称コスト = 標準的な cost-sensitive
   decision theory / D = 既存 SSOT が既に要求している uncertainty gating・
   `domain-adapter-boundary.md §原則` / E = Markov count）。
   SSOT にすると「理論に接地している」と読まれるので**装飾的な引用は危険**。
   未踏 PM 向けにはむしろ逆効果になりうる（「prospect theory を引いているが
   実装は非対称損失だけ」と見られる）。**引用を落とすか、借りている内容を正確に書く**。
3. **§2.1-C は「研究例がある」と書いて引用が無い**。採番するか削除するかの二択。
4. **KTO の引用が技術的な働きをしていない**。借りているのは「非対称効用つき binary
   feedback からの学習」で KTO 固有ではない。KTO は参照モデル + KL 制約を持つ
   LLM alignment 手法で、GSE には参照モデルも logits も無い。§5 の
   `utility = gain - λ·cost` は素の非対称損失。**「KTO 的」と名乗ると読み手が KTO を
   期待して、はるかに単純なものを見つける**。落とすか記述し直す。

### (C) 引用規約に従っていない — 現状 0/9

doc#2 の外部引用 9 本（KTO / Tversky-Kahneman 1991 / CPT-RL / Intertemporal Choice /
Personalized Nudging / MRT×2 / Habit Formation ML / Savage Axioms）は
**1 本も `docs/references.md` に登録されていない**（前セッションで機械確認済み）。
doc#2 は素の markdown リンク + §12 参照リストの形式だが、`citation-ssot` は
inline `[n]` + append-only 登録 + DOI/arXiv/正規化 URL を重複キーとすることを要求する。
→ **9 本すべて採番が必要**。既存の `[V40]` `[P21]` `[V43]` との整合チェックも同時に。

### (D) 「PreReg を変更しない」と「X 軸を再定義する」の緊張

doc#2 は冒頭で「Phase1/v0.3 の確証結果や PreReg を変更するものではない」と言いながら
§0 で X 軸を再定義している。X 軸の再定義は `research-positioning §5` の
**H-X1（L0 軸の測定妥当性）の対象を変える**。
→ 「H-X1 は旧 X 軸に対する仮説であり、新軸には新しい仮説番号が要る」ことを明示しないと、
旧仮説の検証結果が新軸に流用されて読まれる。

### (E) doc#2 の最大の長所が本人に過小評価されている（統合時に前面に出す）

`self_directed_recovery_risk` は **行動から自己ラベル付けできる**軸である。
旧 X 軸は主観プローブ依存で、**Phase1 はまさにそこで死んだ**（probe 枯渇・
P013 の straight-lining・GATE3 DataInsufficient）。
つまり doc#2 は**ラベル供給の構造問題に対する答え**になっているが、doc#2 自身は
それを強調していない。統合設計ではこれを主要な採用根拠として前面に出す。

**ただし** `progress_proxy` の operational definition は §11-2 で
「本文なしでどう検証するか」が未解決と自認されている。
**目的変数の定義が未確定のまま軸を再定義するのは順序が逆**なので、ここを先に閉じる。

### 昇格の前提条件（チェックリスト）

- [ ] (A) 4 状態を定式化し直す（相互排他性 / 放出モデル / `WorkStateEstimate` への写像 /
      状態数の根拠 / 退化検出を評価指標に追加）
- [ ] (B-1) §2.1-F を `[V40]` と突き合わせて採否を決め直す
- [ ] (B-2) A・D・E の装飾的な引用を落とすか、借りている内容を正確に記述し直す
- [ ] (B-3) §2.1-C の無引用主張を採番するか削除する
- [ ] (B-4) KTO の引用を落とすか、借りているものを正確に記述し直す
- [ ] (C) 外部 9 本を `[Pn]`/`[Vn]` で採番し `references.md` に登録（`citation-ssot`）
- [ ] (D) H-X1 と新軸の関係を明示する（新仮説番号の要否）
- [ ] (E) `progress_proxy` の operational definition を閉じる

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

**着手順序に注意: 「2 本を統合する」より先に「昇格の前提を満たす」。**
doc#2 をそのまま昇格させると、(B-1) の `[V40]` 衝突と (A) の 4 状態の破綻が
**SSOT の中に入り込む**。統合作業は前提条件を潰した後の仕上げに過ぎない。

1. `/start-task` で grill → `.steering/[YYYYMMDD]-architecture-consolidation/` を作る。
   grill の目標は 2 つ:
   - 上の**未裁定 5 件（#2〜#6）を閉じる**
   - **§SSOT 昇格の前提条件 8 項目**の扱いを決める（今回閉じる / Deferred として ADR に
     「未解決」で載せる / スコープ外に落とす、のどれか）
2. **`/reimagine` を適用する**（CLAUDE.md: アーキテクチャ判断・複数案がある設計）。
   特に #6（潜在状態の定義）は「doc#2 の 4 状態」「既存 `WorkStateEstimate` の連続 proxy」
   「§SSOT-(A) の 3 モード代案」の 3 案があるので、初回案を破棄して再生成した案と
   比較する価値が高い。**ここは ADR-008 の中心なので手を抜かない。**
3. **`citation-ssot` は後回しにしない**。外部 9 本の採番（§SSOT-(C)）は文章を書き終えて
   からだと本文の主張と噛み合わなくなる。主張を書くたびに採番する。
4. 設計の第二意見が要れば `codex-consult`。
   **⚠️ `.codex/budget.json` が日次上限を超過している**（2026-08-01 時点 363,718/200,000）。
   呼ぶ前に必ず残量を確認すること。
5. 完了時に `/finish-task`（`/cross-review` = TASK-POST 含む）。

## 現在の状態

- ブランチ `main` / コミット `ac093fb`（PR #83 マージ済み）。
- **ユーザーの Loop Engineering 導入作業が未コミットで並行している**（30 ファイル前後）。
  → **`git add` は必ずパス指定**。`git add -A` / `git commit -a` を使わない。
- `docs/adr/` は ADR-001〜007 + README が存在。`docs/architecture/` は 3 本。
  （前セッションで一度「空」に見えたのは作業ディレクトリの誤りで、実際は存在する）
