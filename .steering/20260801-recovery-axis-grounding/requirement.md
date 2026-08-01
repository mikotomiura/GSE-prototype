# recovery risk 軸の理論裏付けと具体化

## 背景

前セッション（`.steering/20260801-architecture-consolidation/`）で `.idea` 2 本を
`docs/architecture/personalization-and-online-learning.md` ＋ ADR-008 / ADR-009 へ統合したが、
その中に **「自前の推論で書いた・文献接地がゼロ」の箇所が 3 つ**残っている。
うち 1 つ（RQ-1）は **定式化そのものが間違っている可能性**がある。

引き継ぎ: `.steering/_handoff/next-session-prompt-recovery-axis-grounding.md`

### RQ-1（★最重要・定式化の誤りの可能性）

`self_directed_recovery` は現状「stall onset から H 分以内に回復したか」の**二値**ラベルで、
推定器は `p_recovery = sigmoid(bias + w·context)`（§4.4 Phase C）。しかし **打ち切りが存在する**
（§3.4: focus 喪失・アプリ切替で「観測外で解決して戻った」を区別できない）。

打ち切りのある「回復までの時間」は本来 **survival object** であり、二値ロジスティックで扱うと
(i) 打ち切り区間を捨てるか誤って 0 に倒す、(ii) H の選び方が結果を左右する（H は事前凍結すると
決めたが任意性そのものは消えていない）。

さらに GSE 固有の疑い: focus 喪失・アプリ切替は**独立な打ち切りではなく、観測外の外部化
（＝解決して戻ってきた）＝競合イベント**である可能性が高い。そうであれば標準の生存解析が
前提とする**非情報打ち切り仮定も破れており**、competing risks（cause-specific hazard）が正しい形になる。

### RQ-2（新規性主張の裏付け）

`§2.6` は新規性を「ラベル供給の構造的解決（行動由来 criterion）」と「閉ループ較正」に置いたが、
**現時点で文献に接地していない**（文献カード 20260801 §やり残し 4）。

### RQ-3（オンライン学習と事前登録の両立）

`ADR-008 D4`（評価期間のデータが 1 バイトも入らないなら両立する）は**自前の推論であり文献接地がゼロ**
（同 §やり残し 5）。

## ゴール

1. **RQ-1 を文献で判定し、判定基準に従って設計を直す**（またはそのままとする理由を記録する）。
2. RQ-2 / RQ-3 を 1 ラウンドの `/literature-review` で扱い、**不在は不在として**記録する。
3. G1 統制タスク実験（T2-a）と Tier 0 配線（T2-b）を**設計まで**具体化する。

## ★ 事前に固定した判定基準（grill・結果を見る前に確定・2026-08-01）

### RQ-1 の判定基準 — 方法論的正しさで判定する

> **(a)** 打ち切りのある離散時間 time-to-event の標準形が **person-period ロジスティック
> （離散時間ハザード）** であることを方法論文献で確認でき、**かつ**
> **(b)** GSE の設計に打ち切りが**構造的に**存在することが示せる
>
> → **満たせば `§3.3` / `§4.4 Phase C` / `ADR-009 D2` を改訂する。**
> → 満たさなければ二値のまま維持し、**その理由を `decisions.md` に記録する**。

**GSE データでの勝ち幅は要求しない**（新軸のデータは 1 件も無く、要求すると永久に書き換えられない
＝判定基準として機能しないため）。これは §4.3 の潜在状態モデル採用ゲート（勝ち幅を要求する）とは
**別の判定である**: あちらは「複雑な推定器を採るか」、こちらは「目的変数の数学的対象を正しく置くか」。

### RQ-1 のスコープ — 競合イベントまで踏み込む

「離散時間ハザードか否か」に加えて、focus 喪失・アプリ切替が**独立打ち切りか競合イベントか**を
文献で確認し、competing risks（cause-specific hazard）が正しければ **D2 をそこまで改訂する**。

### 検証水準

| RQ | 水準 |
|---|---|
| **RQ-1** | **厳格**: 原典 / 教科書の該当章まで確認し、3 票の敵対的検証を通す |
| RQ-2 | 標準（`/literature-review` の手続き。探索の範囲と限界を明記し、不在も結論とする） |
| RQ-3 | 標準（同上） |

カード冒頭に **RQ ごとの検証水準**を明記し、前ラウンド（abstract 水準）と混同させない。

## スコープ

### 含むもの
- RQ-1 / RQ-2 / RQ-3 の文献ラウンド 1 回（`/literature-review`）
- RQ-1 の判定結果に応じた `§3.3` / `§4.4 Phase C` / `ADR-009 D2` の改訂
- `docs/references.md`（`[P33]` / `[V59]` から append-only）・文献カード・`_index.md`
- T2-a: G1 統制タスク実験の**設計**（`experiments/` 配下・`reproducibility-discipline` 規約）
- T2-b: Tier 0 配線の **additive schema 設計メモ**

### 含まないもの
- **コード変更**（本タスクはコード変更ゼロ）
- G1 統制タスク実験の**実施**・被験者募集
- Tier 0 配線の**実装**（`schema_dto.rs` は凍結対象）
- ADR-008 / ADR-009 の Accepted 昇格（条件は G2 通過）
- `research-positioning.md §5` の変更（研究者確認必須節。H-X1d は提案のまま）
- `docs/adr/ADR-001`〜`ADR-007` の変更
- 文書の全面リライト（RQ-1 の結果で必要になった箇所だけ直す）
- Loop Engineering の追加作業（別トラック）

### 凍結対象（触れない）
`schema_dto.rs` / `schema/current.json` / `engine.rs` HMM_VERSION / `loop_step.rs` /
`intervention.rs` 定数 / `probe_scheduler.rs` / `App.tsx` argumentative lock /
`preregistration-v0.3.md`

## 受け入れ条件

- [ ] RQ-1 が**判定基準に照らして**判定され、判定と根拠が `decisions.md` に記録されている
- [ ] 判定が「書き換える」なら `§3.3` / `§4.4 Phase C` / `ADR-009 D2` が改訂されている
- [ ] 文献カードが `docs/literature/20260801-*` として生成され、RQ ごとの検証水準が冒頭にある
- [ ] `docs/references.md` に `[P33]` / `[V59]` 以降で append-only 登録されている（renumber なし・捏造ゼロ）
- [ ] `docs/literature/_index.md` に 1 行追記されている
- [ ] RQ-2 で**不在が結論なら「不在」と書かれている**（「見つからなかった＝新規」と短絡していない）
- [ ] T2-a の実験設計が `experiments/` 配下に置かれ、**分離できたと言える基準が事前宣言**されている
- [ ] T2-b の Tier 0 配線設計メモが書かれている（コードは書いていない）
- [ ] コード変更ゼロ・凍結対象に触れていない

## 関連ドキュメント

- `docs/architecture/personalization-and-online-learning.md`（主対象・§2.6 / §3.3-3.4 / §4.4 / §5.2 / §7.2 / §8.2）
- `docs/adr/ADR-008-online-learning-boundary.md` / `ADR-009-recovery-risk-axis-and-latent-state.md`
- `docs/literature/20260801-behavioral-economics-and-online-personalization.md`（§やり残し 1〜5 が今回の RQ の出所）
- `.steering/20260801-architecture-consolidation/decisions.md`（判断 1〜11）
- `docs/references.md`（次番号 `[P33]` / `[V59]`）
- Skill: `citation-ssot` / `literature-card` / `reproducibility-discipline`
