# ADR-008: オンライン学習の境界（PersonalizationStore / OnlineUpdater / ContextBuilder）

- **ステータス**: **Proposed**（方向合意）。確定は実装時（Phase1 完了後・Epic 2 以降）。ADR-009 と一体で読む。
- **日付**: 2026-08-01
- **関連**: `docs/architecture/personalization-and-online-learning.md §7/§9`・ADR-002（domain-local inference）/
  ADR-005（envelope versioning）/ ADR-006（task_kind→head・β 所有）/ ADR-009（新軸と潜在状態）
- **昇格元**: `.idea/20260801-architecture-signal-and-online-learning.md` §3-B/§3-C/§4/§5 ＋
  `.idea/20260801-behavioral-context-online-latent-ml-design.md` §0/§4.2/§6/§7（`.idea` は追跡外・SSOT ではない）

## Context

Phase1 較正の実測（`experiments/20260731-phase1-calibration-analysis/`・
`experiments/20260801-signal-diagnostics/`）が 2 つの構造的事実を示した。

1. **個人差は平均水準でなく写像係数に出る**。各特徴量の被験者間分散比 ICC(1) は概ね 0.05–0.30 で
   不確実性が大きい（5 名・LOO 範囲 0.050–0.302）一方、`keys→Q2` の個人内 C-index は
   4 名で 0.60–0.68・**P014 だけ 0.368** と符号が反転する。
   → **個人適応すべきは β（切片）ではなく写像の係数**である。
   > ⚠️ `.idea` の 0.060/0.055/0.159/0.156 は **ICC ではなく η²** だった（PR #83 で特定）。
   > 本 ADR は点推定を根拠にしない（縮約強度は交差検証で選ぶ）。
   > さらに Codex 指摘: 「個人差」が実は**作業種別差**の可能性があり、粗いコンテキスト層で層別化が要る。
2. **現行は学習が一箇所も無い**。β は母集団定数ハードコード、遷移行列(3×3)・放出行列(3×26) も全て手書き定数
   ＝「HMM の形をしたルールベース」（`engine.rs`）。

一方、オンライン学習の導入は本プロジェクトの 3 つの既存契約と衝突しうる:

- **PreReg-5**（凍結）: 「評価期間中の閾値・パラメータ調整は**禁止**」（forking paths 排除）
- **Replay-as-Truth**: golden の **byte-equal 一致**がテストの背骨。セッションを跨ぐ状態は決定性を壊す
- **ADR-006**: β は head 所有と確定済み。所有物を広げるのか、別物として扱うのか

`.idea` doc#2 は `PersonalizationStore` / `OnlineUpdater` / `ContextBuilder` の 3 部品を提案したが、
既存 7 層との対応も、上の 3 契約との整合も明文化されていなかった。

## Decision

### D1. オンライン更新の対象を層で限定する

| 層 | オンライン更新 | 方針 |
|---|---|---|
| 瞬間状態（state probability） | **必須** | 固定構造上の Bayesian filtering。**構造は動かさない** |
| 個人・タスク基準（正規化） | **採用** | EWMA / robust quantile（P² 系）/ decayed counts。O(1) メモリ |
| 個人・タスク**写像係数** | **採用** | 低次元の階層ロジスティック。`δ_user_task` は L2 縮約 or 対角共分散の Bayesian update |
| 介入の効用 | **採用** | 二値フィードバック（helpful/unhelpful）＋近接行動アウトカムによる保守的更新 |
| **潜在状態の意味・構造** | **原則固定** | オフライン検証 → model version bump → golden 再生成（ADR-009） |
| 特徴表現・大規模モデル | **採用しない** | 常時オンラインでは扱わない。Deep model / embedding / online ONNX training は初期スコープ外 |

**縮約強度を ICC の点推定に紐づけない**。`δ_user_task_phase` の強度は**交差検証で選ぶ**。

### D2. 新規部品は 3 つに限る（既存 7 層を置き換えない）

| 部品 | 責務 | 既存層 |
|---|---|---|
| `ContextBuilder` | Decision Episode と `ContextSnapshot` を作る（収集単位を raw event から episode へ） | Layer 3 の内側 |
| `PersonalizationStore` | `user × task_kind × phase` の profile を**ローカル保持**（外部送信しない） | Layer 3-4 に付随・head 所有 |
| `OnlineUpdater` | **profile と介入効用のみ**を更新する。状態構造は更新しない | Layer 4/7 に付随 |

doc#2 の `OutcomeRecorder` は既存 Layer 7（`metrics.rs`/`intervention_eval.rs`）、
`InterventionPolicy` は既存 Layer 6（`intervention.rs`）に相当し、**新規部品ではない**。

### D3. ADR-006 は改訂せず、本 ADR が拡張する

ADR-006（Accepted）の枠組み C を**前提として**、head の所有物を
**β から `{criterion（目的変数）, 写像係数, 個人 profile}` へ広げる**。
ADR-006 のファイルは変更しない。

### D4. PreReg-5 との両立基準 = 「情報の出所」

「正規化層は測定器の一部だから適応してよい」という**レトリックは採らない**。基準はこうする:

> **評価期間のデータが 1 バイトも推定に入らないなら PreReg-5 と両立する。入るなら破る。**

| Replay モード | PreReg-5 |
|---|---|
| `cold_start`（global prior のみ） | 両立 |
| `past_session_adapted`（評価開始**前**に凍結した profile を固定） | 両立（凍結時点を前向きに宣言） |
| `within_session_adaptive`（session 内の更新を逐次再現） | **破る** → **探索的結果としてのみ報告** |

主結果は `cold_start` または事前凍結した `past_session_adapted` で出す。

### D5. 学習状態は versioned / serializable な明示入力にする

```text
model_version, profile_version, initial_profile_state, update_rule_version, random_seed
```

replay で pin できることを**設計の必須条件**とする（後付けは非常に高くつく）。
acceptance に次を含める: 初期状態 / 更新順序 / 時刻窓 / 欠損イベント / バージョン移行 / 浮動小数差 /
途中クラッシュ後再開 / **状態スナップショットの schema migration テスト**。

### D6. 閉ループ対策は無作為化だけに頼らない

decision point での小さな無作為化に加えて、**post-intervention window を学習から分離**し、
**propensity をログに残し**、**policy 更新と causal evaluation を分離**する
（探索用ポリシーと評価用ポリシーを分ける）。MRT/JITAI の構成要素分離
（decision point / tailoring variables / intervention options / decision rules / proximal / distal outcomes）を採る。

### D7. 個人化は「抑制方向」にのみ使う

介入の**提示形式・文面・強度を個人化して説得力を上げる**方向は採らない
（ナッジ assistance 系は出版バイアス補正後 d≈0.01・BF01≈9）。
個人化するのは **いつ出さないか（timing・抑制）と 強度の上限** に限る。
詳細と根拠は `personalization-and-online-learning.md §6.2`。

> ★ **contextual bandit の行動空間もこの制約に従う**。将来 `linear Thompson sampling` 等へ拡張する場合
> （`personalization-and-online-learning.md §4.4` Phase D）、アームは
> `no_action / defer / light_nudge / strong_intervention` の**出す・出さない・待つ・強度**に限る。
> **提示バリエーション（文面・形式）をアームにしない**——それは [V40] が否定した領域を
> bandit で探索することに等しい。

### D8. 個人の癖は 3 種類に分け、③には専用機構を作らない

① 水準の癖（個人基準・ICC(1) 概ね 0.05–0.30 と**小さい**）/ ② **写像の癖（★本命**・`keys→Q2` で
P014 だけ 0.368 と符号が反転）/ ③ どの信号が効くかの癖、に分ける。
①は EWMA + robust quantile、②は `δ_user_task` の partial pooling で扱い、
**③には専用の特徴選択機構を作らない**（1 人あたりラベル 20〜100 件では確実に過学習するため、②の係数の
大きさとして吸収させる）。
「この人が何を重視するか」は **`λ_user_task`（割り込まれる損失の重さ）と `δ_user_task`（どの行動が
回復失敗を予告するか）の 2 つに集約**し、個人パラメータをむやみに増やさない。
詳細は `personalization-and-online-learning.md §7.6`。

## Alternatives

- **オンライン学習を入れない（現状維持）**: 母集団 β のままでは §Context-1 の符号反転を扱えず、
  per-user 較正が不可避である以上（`research-positioning §8`）いずれ必要になる。却下。
- **全層をオンライン化する（潜在構造も online EM で更新）**: replay 決定性と PreReg-5 を両方破り、
  label switching / semantic drift で状態の意味が漂流する。→ **ADR-009 で Phase 4 へ降格**。
- **ADR-006 を改訂して所有物を広げる**: β（母集団定数・オフライン決定）と写像係数・profile
  （オンライン更新される個人状態）は**制約が違う**。同じ ADR に混ぜると
  「head の所有物」という一語で異なる制約が塗り潰され、2026-07-24 の研究者判断の範囲も判別できなくなる。却下。
- **「正規化層は測定器の一部」で PreReg-5 を回避する**: 層の名前は forking paths の有無を決めない。
  詭弁である。D4 の情報基準に置き換える。
- **profile をクラウド同期する**: `data-privacy` の外部送信禁止に反する。ローカル保持のみ。

## Consequences

- `PersonalizationStore` の**永続化にはユーザー同意と削除 UI が要る**（未解決・実装前に必須）。
  `data-privacy` Skill の拡張対象。
- replay に 3 モードが増え、golden の本数と検証コストが増える。
  ただし D5 を最初に入れないと後付けコストの方が高い。
- 1 人あたりの保存量は raw log でなく baseline 統計 / decayed transition counts / 数十次元以下の係数 /
  対角共分散 / version・更新回数・最終更新時刻に抑えられる。更新はイベント単位 O(d)、
  状態 filter は O(1) 相当。**ONNX / PyTorch の常時実行は不要**。
  → `ml-workflow` Skill の「Python 学習 → ONNX 推論」前提は、この方向では当てはまらない
  （Rust 内完結）。**Skill の改訂が要る可能性がある**（Phase1 完了後に判断）。
- 本 ADR は**コード変更ゼロ**。凍結対象（`engine.rs`/`schema_dto.rs`/`intervention.rs` 定数/
  `probe_scheduler.rs`/`preregistration-v0.3.md`）に一切触れない。

## Migration

1. Phase1 完了 + 研究者承認まで**着手しない**（凍結）。
2. **P1（観測と参照点）**: `ContextBuilder` と `PersonalizationStore` の baseline 更新のみ。
   現行 X を置換せず並走させる。`emit_schema` の additive 差分を確認し `.steering/` に記録。
3. **P2（個人化 recovery model）**: `OnlineUpdater` を写像係数へ。D4 の 3 モードを分離評価。
   subject-level / task-level / session-level split を必須にする。
4. **P3（介入効用）**: D6 を配線。propensity ログと proximal outcome の固定。
5. D5 の pinning チェックリストは **P1 の時点で全項目を acceptance に入れる**（後付けしない）。
