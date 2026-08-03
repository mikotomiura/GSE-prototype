# 次セッション開始プロンプト — recovery risk 軸の理論裏付けと具体化

このファイルの「===」以下をコピペして開始する。

**前提**: 本タスクも**コード変更ゼロ**。凍結対象には触れない。
モデルは **Opus**（定式化の妥当性判断・文献の敵対的検証を含むため）。

---

===

**このタスクの本体は「文書を磨くこと」ではない。**
前セッションで `.idea` 2 本を `docs/architecture/personalization-and-online-learning.md`（919 行）＋
ADR-008/009 へ統合したが、**その中に「自前の推論で書いた・文献接地がゼロ」の箇所が 3 つ残っている**。
うち 1 つは**定式化そのものが間違っている可能性**がある。これを潰すのが今回の主目的。

文書の可読性改善（節整理・重複削除）は**優先度が最も低い**。データが無いまま論証を厚くすると
`gse-v2-overview.md §5`（エビデンスの温度）が最も警戒する「美しく論証されているが未検証」に落ちる。

## §0 前セッションで確定済み（**再度問わない**）

`.steering/20260801-architecture-consolidation/decisions.md`（判断 1〜11）に全て記録済み。要点:

1. **X 軸 = `self_directed_recovery_risk`** へ再定義（ADR-009 D1）。
   **旧 X（Cognitive Friction）は「確証の核」から「比較用 baseline・歴史的説明」へ格下げ**（D1b）。
   ただし削除しない・`p_stuck` は Phase 2b まで現行のまま介入を駆動する。
2. **潜在状態の数は決めない**（D3）。stateless baseline が「正」、状態モデルは
   **採用ゲート（勝ち幅＋退化検出）**を通ったときだけ採用する候補（D4）。
   **Receptivity は Layer 5**（ADR-007 維持）。
3. **online EM は Phase 4 へ降格**（D6）。理由は「重い」ではなく**前提 3 つが未充足で評価不能**。
4. **個人化は抑制方向のみ**（ADR-008 D7）。提示形式・文面の個人化は採らない（[V40]）。
   **contextual bandit のアームも「出す/出さない/待つ/強度」に限る**。
5. **PreReg-5 との両立基準は「情報の出所」**（ADR-008 D4）。「測定器の一部だから」という
   レトリックは**採らない**と決めた。
6. **ADR-006 は無変更**。新 ADR が「head の所有物を β から {criterion, 写像係数, profile} へ拡張」する（D3）。
7. **ステータスは 3 本とも Proposed**。Accepted への昇格条件は **G2 通過**（P1 で recovery ラベルが
   実際に取れること）。
8. **H-X1d は提案のみ**。`research-positioning.md §5` は**触らない**（研究者確認必須節）。
9. **ラベルは 3 チャネル**（L-A 行動由来 ★主 / L-B 状態 criterion / L-C 介入アウトカム）。

## まず読む（着手前・この順）

1. `docs/architecture/personalization-and-online-learning.md` — **今回の主対象**。特に
   **§3.3-3.4（recovery ラベルと打ち切り）/ §4.4 Phase C / §2.6（新規性）/ §7.2（PreReg-5）**
2. `docs/adr/ADR-008-online-learning-boundary.md` / `ADR-009-recovery-risk-axis-and-latent-state.md`
3. `docs/literature/20260801-behavioral-economics-and-online-personalization.md`
   — **§やり残し 1〜5 が今回の RQ の出所**。⚠️ このカードは**敵対的検証を通していない abstract 水準**で、
   過去ラウンドのカードと**同列に扱ってはいけない**
4. `.steering/20260801-architecture-consolidation/decisions.md` — 判断 1〜11（なぜそうしたか）
5. Skill: `citation-ssot`（必須）/ `literature-card`（必須）/ `reproducibility-discipline`（T2 で使う）

## 本体 T1 — 理論裏付け（`/literature-review` 1 ラウンド）

### ★ RQ-1（最重要・**定式化の誤りの可能性**）: recovery ラベルは survival object ではないか

現状の設計はこうなっている:

- `self_directed_recovery` = 「stall onset から **H 分以内**に、外部化を挟まず progress_proxy が回復したか」の**二値**
- 推定器 = `p_recovery = sigmoid(bias + w·context)`（§4.4 Phase C）
- **打ち切りが存在する**（focus 喪失・アプリ切替で「観測外で解決して戻った」を区別できない・§3.4）

**打ち切りのある「回復までの時間」は、本来 survival analysis の対象である。**
二値ロジスティックで扱うと (i) 打ち切り区間を捨てるか誤って 0 に倒すことになり、
(ii) **H の選び方が結果を左右する**（H は事前凍結すると決めたが、任意性そのものは消えていない）。

→ **`discrete-time hazard model`（離散時間ハザード / person-period ロジスティック）の方が
正しい定式化ではないか**を文献で確認する。正しければ:

- `§4.4 Phase C` の式を書き換える
- `§3.3` のラベル定義を「二値」から「イベント時刻＋打ち切り指示子」へ改める
- **ADR-009 D2 の改訂が要る**（Proposed なので改訂可能）
- 副次的な利得: **H の任意性が消え、打ち切りを捨てずに使える**

⚠️ **これは「文献で飾る」話ではなく、間違っていたら設計を直す話**である。最優先で扱うこと。

### RQ-2: `self_directed_recovery_risk` に対応する先行研究はあるか（**新規性主張の裏付け**）

`§2.6` は新規性を「ラベル供給の構造的解決（行動由来 criterion）」と「閉ループ較正」に置いたが、
**現時点で文献に接地していない**。探すのは:

- **content-free / メタデータのみの行動ログから「自力での回復・立て直し」を予測する**系の研究
- 知識労働・執筆・プログラミングの**中断と再開（resumption）**の研究（interruption research に近縁）
- 「介入せずに待てば戻るか」を予測して介入を抑制した先行例

→ **不在が確認できればそれ自体が貢献**（RQ-2 のときと同じ well-calibrated negative の扱い）。
その場合は「空白である」ことをカードに明記し、`§2.6` にその旨を書く。
**「見つからなかった＝新規」と短絡しない**。探索の範囲と限界を書くこと。

### RQ-3: オンライン学習と事前登録（forking paths）の両立

`ADR-008 D4`（評価期間のデータが 1 バイトも入らないなら両立する）は**私の推論であり文献接地がゼロ**。

- test-time adaptation / prequential (interleaved test-then-train) evaluation の評価規約
- 適応的臨床試験（adaptive design）の事前登録実務
- ML の online evaluation で「いつの時点の情報を使ってよいか」を規定した先行例

→ 既存の規約があれば D4 をそれに接地させる。無ければ「自前基準である」と明記する。

### T1 の作法（厳守）

- **`citation-ssot`**: 次番号は **`[P33]` / `[V59]`** から。append-only・renumber 禁止・
  重複キーは DOI/arXiv/正規化 URL・書誌未確定は `provisional`・**捏造しない**。
- **`literature-card`**: 落合フォーマット 6 項目でカードを作り `docs/literature/_index.md` に追記。
- **検証水準を明記する**: 前ラウンド（20260801）は abstract 水準だった。今回どこまで確認したかを
  カード冒頭に書き、**過去の deep-research ラウンドと同列に見せない**。
- ⚠️ **[V55]（DOI 無し）/ [V56]（preprint）は `provisional` のまま**。昇格するなら全文確認してから。

## 本体 T2 — 具体化（コード変更ゼロでできる範囲）

### T2-a: G1 統制タスク実験の設計

凍結解除後の**最初のタスク**（`§8.2` G1 / ADR-009 D7）。設計だけ先に書く。
`experiments/<YYYYMMDD>-controlled-friction-task/` に `reproducibility-discipline` の規約で置く。

- 高摩擦を誘発する短い統制タスクの具体（何を書かせるか・時間・難度操作）
- 同一人物内で低摩擦/高摩擦条件を交互に取る割付
- **分離できたと言える基準を事前に宣言する**（事後に決めない）
- 打鍵由来の content-free イベントだけで判定する（プローブは検証用の従）

⚠️ **実施はしない**。設計まで。被験者募集も行わない。

### T2-b: Tier 0 配線の具体設計

`§5.2` の Tier 0（**新規収集ゼロ**で効く層）を additive schema としてどう入れるか。

- `paste` は既に `{"type":"paste","t":..,"external_paste_chars":N}` として**別レコードで記録済みだが
  `feat` 行に入っておらず推論に一切使われていない**（`logger.rs:408`）
- `keys` / `bs_rate` / `ime_dwell_med` も同様
- → `feat` 行への additive 追加案と、`emit_schema` diff の想定、gse-dataset 側の schema parity への影響

⚠️ **`schema_dto.rs` は凍結対象。設計メモまで。コードは書かない。**

## 制約（厳守）

- **凍結対象に触れない**（Phase1 完了まで）: `schema_dto.rs` / `schema/current.json` /
  `engine.rs` HMM_VERSION / `loop_step.rs` / `intervention.rs` 定数 / `probe_scheduler.rs` /
  `App.tsx` argumentative lock / `preregistration-v0.3.md`
- **コード変更ゼロ**
- **`research-positioning.md §5` を変更しない**（研究者確認必須節。H-X1d は提案のまま）
- **`docs/adr/ADR-001`〜`ADR-007` を変更しない**（ADR-006 の再検討はスコープ外）
- **過大主張の禁止**: `gse-v2-overview.md §5`。**文献が見つからないことを「新規である」の証明にしない**
- **`.idea/` は昇格済み**。2 本とも冒頭に「→ 昇格済み・是正点」ヘッダがある。
  **`.idea` 本文を新たな SSOT 入力として使わない**（是正前の記述が残っているため）

## やらないこと（スコープ外）

- G1 統制タスク実験の**実施**（設計まで）
- Tier 0 配線の**実装**（設計メモまで）
- ADR-008/009 の Accepted 昇格（条件は G2 通過）
- 文書の全面リライト。**RQ-1 の結果で必要になった箇所だけ直す**
- Loop Engineering の追加作業（別トラック。下記「現在の状態」参照）

## 進め方

1. `/start-task` で grill → `.steering/[YYYYMMDD]-recovery-axis-grounding/` を作る。
   grill のゴールは「**RQ-1 の判定基準**（どうなったら定式化を書き換えるか）を先に決めること」。
2. **RQ-1 を最初にやる**。RQ-2/RQ-3 より先。定式化が変わるなら他の作業のやり直しが発生するため。
3. `/literature-review` で 1 ラウンド。**主張を書くたびに `citation-ssot` で採番**する
   （書き終えてからだと本文と噛み合わない — 前セッションの教訓）。
4. RQ-1 の結果が「書き換えるべき」なら、`§3.3` / `§4.4 Phase C` / `ADR-009 D2` を改訂し、
   `decisions.md` に判断として記録する。
5. T2 は T1 の後。時間が足りなければ T2-a だけでもよい（G1 は凍結解除後の最初のタスクなので）。
6. 完了時に `/finish-task`。
   **⚠️ `.codex/budget.json` の日次予算超過が続いていれば `/cross-review` は skip し、理由を完了報告に明記する**
   （2026-08-01 時点 363,718/200,000）。日付が変われば復活している可能性があるので**呼ぶ前に必ず確認**。

## 現在の状態（2026-08-01 セッション終了時点）

- ブランチ `docs/handoff-architecture-consolidation`。
- **⚠️ 43 ファイルが未コミットのまま終わっている可能性がある**。開始時に `git status` を確認し、
  未コミットなら**先にコミットする**。内訳は 2 系統で、**混ぜてコミットしない**:
  - **今回のアーキテクチャ統合分**: `docs/architecture/personalization-and-online-learning.md` /
    `docs/adr/ADR-008,009` / `docs/literature/20260801-*` / `docs/{references,glossary,adr/README}.md` /
    `docs/architecture/{gse-v2-overview,domain-adapter-boundary,intervention-decision-engine}.md` /
    `docs/literature/_index.md` / `.steering/20260801-architecture-consolidation/`
  - **ユーザーの Loop Engineering 導入分**（別トラック・30 ファイル前後）:
    `docs/loop-engineering.md` / `.claude/{commands,agents,hooks,skills}/loop-*` / `scripts/loop-*.sh` /
    `.steering/_template/loop-*` / `CLAUDE.md` / `docs/agent-shared.md` / `.claude/settings.json` 等
  - → **`git add -A` / `git commit -a` を使わない。必ずパス指定。**
- **Loop Engineering の状態**（別トラック・今回のスコープ外だが把握しておくこと）:
  - 構築 L0–L7 は完了・`/verify-loop-setup` は HEALTHY。固定名成果物 15/15・Stop hook 登録・
    実行ビット・`bash -n` は独立再検証済み。
  - **⚠️ 一度も実行していない**（`_loop-events.jsonl` / `_loop-board.md` がリポジトリに存在しない）。
    レポートの推奨アクション 3「最も安い issue 1 本を `parallel=1` で C モードから試す」が未実施。
    **構築完了 ≠ 動作確認済み**。
  - LOW 指摘 1 件未対応: `.claude/agents/loop-watchdog.md` に呼び出し元
    （`loop-issue` / `loop-worker`）の明記が無い。
- **ユーザー検証フェーズの判断は保留中**: Phase1 = GATE2 pass / GATE3 **DataInsufficient**
  （GATE3 母数に乗ったのは 5 名中 1 名のみ）。**そのまま M3 Phase2 へは進めない**という整理を前セッションで
  提示済み。`docs/wbs-verification-halfyear.md §改訂予定`（Phase 1.5 挿入・Phase2 の 3 分割・
  Gate D/S/H 追加）は**提案・未承認**。**承認は研究者判断**であり、本タスクでは扱わない。
- `docs/references.md` の末尾は `[P32]` / `[V58]`。次番号は `[P33]` / `[V59]`。
