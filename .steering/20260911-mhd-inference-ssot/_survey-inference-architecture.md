# 調査結果: MhD 推論アーキテクチャ（`.idea` 9/10×2 + 9/11）と docs 側の受け皿

> 調査日: 2026-09-11 / 対象: `.idea/20260910-mhd-criterion-*`, `20260910-mhd-feature-*`, `20260911-mhd-growth-*`
> ⚠️ これは `.idea` の**抽出**であって SSOT ではない。昇格時は既存 ADR と逐条照合すること。
> ★ 日付順: 09-10 criterion → 09-10 survey（criterion を監査）→ 09-11 roadmap（両方を統合）

## ★ 到達点の骨格（この 3 本が最終的に何を提案しているか）

MhD は「打鍵から 3 状態（Flow / Incubation / Stuck）を当てる分類器」という当初像から完全に離れ、
**「本文を保存しない content-free な作業行動から、近い将来の 3 つの競合転帰
（自己回復 `recovery` / 外部化 `externalized` / 離脱 `left_observation`、いずれも起きなければ
`still_stalled`）を、時間分離した予測として、打ち切りを含む離散時間の生存解析枠組みで推定する」**
という一貫した提案に収斂している。

推定は**複雑さで昇格しない**。固定 baseline → criterion 直結 → 個人・タスク適応 → 時系列 の順で、
各段の昇格は calibration・上下界の安定・future-session 改善・退化検査という**測れる量**でゲートされ、
効果量の点推定（+X%）は使わない。

学習は**三つの時間**と**三つの出力**を厳格に分離し、hyperparameter は
offline global tuning → Empirical-Bayes → per-user online（shadow 限定）の順でしか解禁しない。
個人化は「各人に別モデルを作る」方向を**明示的に拒否**し、共有 feature schema ＋ global prior ＋
縮約された個人係数（I0）を初期の正とする。

特徴量は「打鍵の平均速度」から **「境界に条件づけた pause × revision topology × restart shape」**
という時間的作法へ焦点を移す。すべての新特徴・新モデルは
**O1（候補発見・モデル勝負にしない）→ feature/criterion freeze（事前登録）→ G-next（統制環境での反証・
既存 G1 は変更しない）→ O-holdout（前向き外的妥当性）**という順序でしか確証段階に進めない。
**abstention と calibration は全段に横断**し、「不確実なら `none` へ退く」ことを弱さでなく設計の中核とする。

## 1. 段別のモデル（`roadmap §2`・ADR-019 D1 の表をほぼ逐語で再利用）

⚠️★★★ **`M1〜M4` は ADR-021 D11 が撤回済み。実体名で呼ぶ。** 下表は対応のため旧呼称を併記する。

| 段（実体名） | 推定できるもの | 主モデル | 必要証拠 | 失敗時の縮退先 |
|---|---|---|---|---|
| **固定 baseline**（旧 M1） | activity、friction 候補、writing state proxy | rule + 現行 HMM | 計器健全性、replay parity、境界特徴 coverage | proxy として残し意味主張を縮小 |
| **criterion 直結**（旧 M2） | 自己回復・外部化・離脱の未来 risk | **cause-specific discrete-time hazard** / **regularized multinomial** | episode 成立、CIF calibration、上下界安定 | criterion / 観測設計へ戻る |
| **個人・タスク適応**（旧 M3） | person / task 別 risk と不確実性 | **partial pooling** / **hierarchical logistic** | future-session 改善、符号安定性、task transfer | global model へ縮退 |
| **時系列**（旧 M4） | topology・duration・change dynamics | **HSMM**、**ROCKET 系**、**landmark 更新** | 同一 holdout で前段を越え、退化しない | 前段を正として維持 |

`survey §5.3` の**推奨モデル順**:
① prevalence / last-value / 固定 rule → ② multinomial logistic / GAM →
③ cause-specific discrete-time hazard → ④ random effect / partial pooling を持つ階層 hazard →
⑤ HMM / HSMM（特徴生成 or 比較モデル）→ ⑥ landmark dynamic prediction →
⑦ RF / XGBoost・TCN / LSTM（**上記を越えた場合だけ残す**）

| モデル | なぜ使うか | 何と比較するか |
|---|---|---|
| cause-specific discrete-time hazard | 打ち切り・競合事象を時間分離して扱える。**通常 HMM の持続時間 = 幾何分布という暗黙仮定を回避** | prevalence / last-value / rule、regularized multinomial |
| regularized multinomial | より単純な代替。時間依存性を落とした比較 baseline | cause-specific hazard に対する下位互換チェック |
| partial pooling / hierarchical logistic | 個人・task 差を「水準」でなく**写像係数の縮約**として表現し、少数ラベルでの過学習を防ぐ | global main effect（縮退先） |
| HSMM | 持続時間そのものが重要なら HMM より理論適合的（幾何分布仮定を外せる） | 通常 HMM、ROCKET 系 |
| ROCKET 系 | 非学習ランダム畳み込み特徴 + 線形分類器。**ADR-019 D5 が UCR 等の一次証拠で第一候補と裁定済み** | HSMM、深層系列（TCN/GRU は比較のみで主役ではない） |
| landmark model | 時点更新型の動的予測。任意の予測時点から再計算できる | 階層 hazard を「越えるか」の判定対象 |

## 2. 昇格判定表（`roadmap §4`・全 9 行）

| 境界 | 問い | 主な判定量 |
|---|---|---|
| WP1→WP2 | criterion 候補は自然作業で十分発生するか | episode yield、base rate、missingness |
| WP2→WP3 | label を時間リークなく再生成できるか | replay 一致、評定一致、時間分離 |
| 固定 baseline→criterion 直結 | 未来転帰を校正して予測できるか | CIF calibration、Brier、上下界 |
| criterion 直結→個人・タスク適応 | 個人 / task 適応に再現可能な価値があるか | future-session 改善、符号安定、worst-group |
| I0→I1 | 疎性が過学習を減らすか | selection stability、calibration、effective df |
| I1→I2 | 個人 subset が階層係数を越えるか | nested future holdout、bootstrap 再現率 |
| 個人適応→時系列 | 系列モデルに固有の増分があるか | block ablation、退化検査、計算量 |
| Estimate→Decision | risk が介入判断に使えるか | decision curve、HIR、abstention |
| Decision→Intervention | 介入に因果的利益があるか | MRT proximal effect、harm、burden |

⚠️ 昇格は不可逆でない（drift / calibration 崩壊 / OS・IME 変更 / schema 変更で rollback）。

## 3. abstention と calibration

- **`Q`（evidence quality）Tier** は状態特徴ではなく、**欠測を 0 として入力せず推論の抑制・abstention に使う**（`survey §6.1`）
- 評価指標（`survey §5.5`）: 結果別 time-dependent AUROC / AUPRC / PPV、Horizon 別 CIF、
  calibration intercept / slope / reliability curve、**IPCW Brier score**、
  **abstention coverage と selective risk**、person / task / device / IME 別 worst-group、
  T0→T1→T2 の block ablation
- ⚠️ **「conformal」という語は 3 本のどこにも出現しない。** ADR-019 が既に接地した
  conformal outlier testing `[V66]` との明示的接続は**していない**（未確認扱い）

## 4. 学習・更新の規約

### 三つの時間（`roadmap §1.2`）

| 時間 | 更新してよいもの | 主張 |
|---|---|---|
| O1 discovery | 候補特徴、検索空間、episode 定義案 | **探索のみ** |
| training / adaptation | global model、過去 session profile、縮約係数 | 凍結した規則で更新 |
| evaluation | 原則固定。予測後更新は探索的 prequential のみ | 確証は cold-start / past-session-adapted |

### 三つの出力を混ぜない（`roadmap §1.3`）

- **MhD estimate**: 将来転帰 risk、uncertainty、evidence quality
- **Decision**: Need、Opportunity、harm cost から `none/defer/invitation`
- **Practice Trace**: 経路固有の表現素材。⚠️ **予測精度の証拠ではない**

### Hyperparameter 管理（`roadmap §5`）

**tuning 対象**: window / Horizon / period width、regularization と shrinkage、
baseline hazard の形と link、abstention / decision threshold、kernel 数・duration・state 数候補

⚠️★★★ **tuning してはいけないもの（5 項目）**:
1. holdout を見た後の criterion 定義
2. outcome を増やすための episode 境界
3. 個人ごとの都合のよい評価 metric
4. post-intervention だけで学ぶ utility
5. **state の意味を結果を見て命名すること**

**registry（各 run で保存する 11 項目）**:
`dataset_version` / `episode_schema_version` / `feature_schema_version` / `split_manifest` /
`search_space` / `search_budget` / `seed` / `selected_parameters` / `profile_cutoff_time` /
`model_version` / `calibration_version`

### auto-tuning の三分割（`roadmap WP6`）

1. **Offline global tuning**: O1 discovery 内の grouped nested CV。**採用**
2. **Empirical-Bayes tuning**: 縮約強度や prior を参加者間で学ぶ。**個人適応段の候補**
3. **Per-user online tuning**: 実運用中に window / feature / threshold を探索。⚠️ **後期 shadow 限定**。
   予測後更新の prequential 順序・探索 budget・parameter bound・rollback・drift detector を事前固定し、
   champion / challenger の shadow 比較のみ（**本番 decision へ直結させない**）

## 5. 個人化（WP5）

| 段 | 方法 | 位置づけ |
|---|---|---|
| **I0** | 共有特徴、個人別縮約係数 | **初期の正** |
| **I1** | group lasso / hierarchical shrinkage / ARD 等で集団と個人偏差を疎にする | 主候補 |
| **I2** | 十分な過去 episode を持つ人だけ、限定候補から個人別 feature subset を選ぶ | 後期・探索 |

★ **I2 の解禁条件は固定件数で決めない。** O1 の base rate、特徴相関、events-per-parameter、
bootstrap stability を使った **simulation** で必要 episode 数を定め、**開始前に凍結**する。

### feature importance の四層（`roadmap §6`）

| 種類 | 問い | 方法 |
|---|---|---|
| Population importance | 全体で役立つか | block ablation、grouped permutation |
| Conditional importance | 他特徴を持った上で役立つか | drop-column、正則化係数、conditional permutation |
| Personal relevance | この人で写像が異なるか | posterior user deviation、future-session stability |
| Decision importance | action を変えるほど重要か | decision curve、threshold crossing、HIR 差 |

⚠️ SHAP 等はモデル内説明補助であり、**因果・特徴採否の単独根拠にしない**。

## 6. 特徴量 Tier（`survey §6.1` が `criterion §2.1` を 1 日遅れで精緻化）

| Tier | 内容 | 具体特徴 |
|---|---|---|
| T0 | 基本 activity | keys、delete、paste、mean IKI、単純 pause、net production |
| T1a | 分布・個人相対 | p50/p90/max、CV、混合成分、**本人 task/phase baseline からの surprise** |
| T1b | **境界** | 直前/直後 key category、Space/Enter/punctuation、**IME composition/commit** |
| T1c | **revision topology** | delete run 長、rewrite、再削除、**loop depth**、undo/redo 往復、局所 recurrence |
| T1d | **restart** | pause 後の生成/削除/移動、再停止時間、安定生成時間、rhythm 回復 |
| T2 | cross-channel | focus loss/return、元 app 回帰、navigation-to-edit lag、build/test 等抽象 event |
| **Q** | **evidence quality** | capability、missingness reason、logger/IME health、observability mask |

- **boundary-conditioned pause**(T1b): pause の「長さ」でなく **「位置」**（語/文/段落境界、IME 変換境界）を分類
- **IME content-free state machine**(T1b 横断):
  `idle → composing → converting_or_selecting → committed|abandoned|unobservable → post_commit_revision|stable_continuation`
  候補特徴 = composition duration、内部 delete、commit latency、commit-to-next gap、retry 数、
  commit 直後の削除、abandon 候補、通常 rhythm への回復時間、本人 baseline からの偏差。
  ⚠️ **候補語・window title は保存しない**

★ **第一仮説**（`criterion §3.3` / `survey §3.2` 共通）:
**revision topology × boundary-conditioned pause × restart shape × person-relative surprise** の組合せ検証。
単独特徴でなく **episode 内の接続**を見る。

## 7. 既存 SSOT との差分

| 論点 | 判定 | 詳細 |
|---|---|---|
| 段構造・モデル候補（HSMM/ROCKET/hazard/partial pooling） | **既に書かれている** | `roadmap §2` は ADR-019 D1 の表をほぼ逐語で再利用。ADR-019 D5 とも整合 |
| 4 カテゴリ競合事象 | **既に書かれている** | ADR-009 D2・`personalization-and-online-learning.md §3.3` と用語が完全一致 |
| 上下界（G2）の設計 | **既に書かれている** | ADR-009 D2 を前提として踏襲 |
| boundary keys の採用 | **既に書かれている（拡張）** | `personalization-and-online-learning.md §5.2` が 2026-08-15 に「弁別の前提条件」へ格上げ済み（`[P121]` κ=0.363 等・ADR-019 D6 と同一根拠） |
| **revision topology / restart shape / IME state machine の Tier 名・状態機械としての定式化** | **書かれていない** | ⚠️ 既存 Tier 0/1/2 は「**収集済みか否か**」の軸、`.idea` の T1a-d は「**認知的作業の型**」の軸。**同名だが軸が違う** |
| feature importance 四層・registry 11 項目・auto-tuning 三分割 | **書かれていない** | `personalization-and-online-learning.md`・ADR-008/009 に該当節なし（grep で不在確認済み） |
| ⚠️★★★ **I0/I1/I2 個人別 feature selection** | **食い違っている** | ★ **ADR-008 D8** は「③どの信号が効くかの癖には**専用の特徴選択機構を作らない**（1 人あたりラベル 20〜100 件では確実に過学習するため、②の係数の大きさとして吸収させる）」と明記。**WP5 の I2「個人別 feature subset を選ぶ」はこの『専用機構』に該当しうる。** I0/I1 は D8 の精神と両立するが、**I2 は正面から衝突する** |
| **registry 11 項目 vs ADR-008 D5 の pinning リスト** | **食い違っている（部分重複・非整合）** | 目的は近い（replay 再現性）が語彙が違う。`seed`↔`random_seed`、`profile_version`/`initial_profile_state`/`update_rule_version` は roadmap 側に無く、`dataset_version`/`split_manifest` は ADR-008 側に無い。**統合時に一本化が必要** |
| G1 の位置づけ | **既に書かれている** | ADR-009 D7 の反証ゲート。`criterion §7.3` の G-next は G1 を変更せず**別試験**として設計しており矛盾しない |

## 8. docs 側の受け皿（別調査）

⚠️★★★ **「Layer 4（推定層）」全体を専用に扱う設計文書は存在しない。**

| 文書 | 担当層 | 粒度 |
|---|---|---|
| `gse-v2-overview.md §2` | 7 層 `Layer 0`–`Layer 7` の定義（SSOT） | 層の名前と入出力の一行説明のみ |
| `domain-adapter-boundary.md` | Layer 0–3 ＋ **末尾に「Layer 3-4」節** | `WorkStateEstimate` 構造体案・`DomainInferenceHead` trait 案（**シグネチャのみ**） |
| `intervention-decision-engine.md` | Layer 5–7 | Opportunity/Receptivity/Decision の enum・実測付き |
| **`personalization-and-online-learning.md`（1401 行・Proposed）** | **「Layer 3-4 拡張」** | ★ **最も推定器の内部に踏み込んだ文書**。`self_directed_recovery_risk` という新軸 1 本に限定して、離散時間競合リスク・person-period 多項ロジスティック・stateless baseline・採用ゲートまで詳述 |
| `task-adaptation-and-scope-gating.md` | Layer 3-4 の隣接 | 検出器の構造（B-1〜B-5）・conformal outlier testing への接地 |

- 現行実装（HMM・β・Forward Algorithm）の設計根拠は `docs/architecture/` に**無い**。
  ADR-001 と `hmm-analysis`/`ml-workflow` Skill と `engine.rs` のコードコメントに**分散**している。
- ★ **昇格先の推奨: 新規ファイルではなく `personalization-and-online-learning.md` への追記・統合。**
  新規ファイルを作ると内容が重複し、どちらが正か曖昧になる。

## 9. 実装の現在地（2026-09-11 実測）

- **`engine.rs`（`HMM_VERSION = "0.5.0"`）**: 3×3 遷移行列・3×26 放出行列（78 要素）は
  **全て `// TUNE:` コメント付きの手書きリテラル**。`update()` は Forward Algorithm 1 ステップ
  （正規化のみ、**Baum-Welch 等の学習ステップは無し**）。EWMA（α=0.3 通常 / 0.15–0.25 サイレンス）と
  ヒステリシス層（α=0.40/0.60）も定数。
- **`features.rs`**: F1=Flight Time 中央値、F3=修正率(BS+Del/全キー)、F4=バースト長(FT<200ms 連続の平均文字数)、
  F5=ポーズ回数(≥2s 無入力)、F6=削除後停止率(BS/Del 直後 ≥2s 停止の割合)。
  ⚠️ **全て境界（語・文の区切り）非依存**の打鍵タイミング / BS 派生量のみ。
- **`heads/`**: `mod.rs` が `TaskDomain`（Writing/WritingFallback/Coding）→ `HeadId` のルーティング表。
  `BETA_WRITING_*` / `BETA_WRITING_LATIN_*` / `BETA_CODING_*` は**いずれも母集団定数のハードコード**。
- ⚠️★★★ **学習しているコードは 0 行。** `train(` / `.fit(` / `gradient` / `optimizer` / `linfa` /
  `smartcore` を `src-tauri/src/` 全体で検索し **0 件**。
  → **ADR-008 の「現行は学習が一箇所も無い・β は母集団定数ハードコード」は 2026-09-11 現在もそのまま正しい。**

## 10. 用語の衝突状況

| 系統 | 使用箇所 | L1/L2 等の意味 |
|---|---|---|
| ① 7 層 `Layer 0`–`Layer 7` | `gse-v2-overview.md §2`（SSOT）ほか | L1=Domain Event Adapter / L2=Privacy Boundary |
| ② `glossary.md` の MhD 項 | 逐語「`p_stuck` は **MhD（L1）** が計算し **Need 層（L2）** が閾値消費」 | L1=MhD 全体 / L2=Need 層 |
| ③ 表現層の「層 0–3」 | `glossary.md` 18 箇所 / `expression-channel.md` 9 箇所 | 層 0=状態に応答しない常在基層 |
| ④ O1 の `L0`/`L1`/`L2`、`L-A`〜`L-C`、`L-a`〜`L-d` | `glossary.md` O1 項 | L0=X/Y 二軸 / L1=Stuck / L2=Need 判断性能 |
| `.idea` が提案した MhD 内部の `L1〜L4` | `.idea/20260901` | ⚠️ **却下済み**（ADR-019 D2）。4 系統目になり `L2` が 3 通りの意味を持つため |
| モデル成熟 `M1〜M4`（ADR-019） | 5 ファイル 7 箇所 | ⚠️ **撤回済み**（ADR-021 D11） |
| WBS マイルストーン `M0〜M5` | `wbs-verification-halfyear.md §2`、`research-positioning.md §6`、`experiment-tracking.md`、`pilot-runbook.md`（**文書タイトル**）、`preregistration-v0.3.md`（**凍結文書**） | M0=検証基盤フリーズ / M1=Phase1a 完了 / … / M5=通算再推定＆総括 |

★ ADR-021 D11 の裁定根拠: **浸透量の非対称**（WBS の M0〜M5 は凍結文書含め広く浸透、
モデル成熟の M1〜M4 は 7 箇所のみ）→ モデル成熟側を撤回。
WBS 側の改名は「凍結文書 `preregistration-v0.3.md` に及ぶ」ため却下案として明記されている。

## 11. SSOT 化の可否判定

| 項目 | 区分 | 追記先 / 新規 ADR |
|---|---|---|
| 段別モデル候補の具体名と昇格判定表 | **A** | `gse-v2-overview.md` または ADR-019 への補遺（既存決定の詳細化なので新規 ADR 不要） |
| 三つの時間・三つの出力を混ぜない規律 | **A** | `personalization-and-online-learning.md §7.2`（PreReg-5 節）へ追記 |
| hyperparameter tuning 対象 / **禁止リスト** | **A** | `personalization-and-online-learning.md §6` または新設の「hyperparameter 規約」節 |
| registry 11 項目 | **B** | ⚠️ **ADR-008 D5 の pinning リストとの統合が先**。統合後に ADR-008 への追補 |
| auto-tuning: offline global | **A** | WP0 段階で直ちに規約化可 |
| auto-tuning: per-user online | **B** | ⚠️ ADR-008 D8 との整合を取ってから凍結 |
| WP5 **I0** | **A** | 既に ADR-008 D1/D8 の枠組みと一致。追記のみ |
| WP5 **I1** | **B** | O1 の episode 量・events-per-parameter が判明するまで採否は凍結。方針自体は A 相当 |
| ⚠️★★★ WP5 **I2** | **B（要 ADR 改訂）** | **ADR-008 D8 と正面衝突**。新規 ADR で D8 を明示的に部分改訂（「専用機構を作らない」→「O1 実測に基づく解禁条件付きで再検討可」）しない限り SSOT 化できない |
| feature importance 四層 | **A** | `personalization-and-online-learning.md §8.1`（評価指標節）へ追記 |
| Tier T0/T1a-d/T2/Q・revision topology・boundary pause・restart shape・IME state machine | **C**（仮説としての記述は A） | O1 の実データで coverage・欠測率・feasibility が出るまで確定できない |
| criterion / censoring / 競合事象の定義 | 既に Accepted 相当（ADR-009） | 変更不要 |
| G-next / O-holdout の正式名称・事前登録 | **B** | `roadmap §11` 自身が「ADR 化前の未決」と明記。O1 完了後に ADR 化 |
| IME content-free state machine の実装 | **D** | 実装物。feasibility 試験が先 |

## 未確認事項

- `personalization-and-online-learning.md §11`（未解決事項・1250 行以降/全 1401 行中 150 行未読）は未反映
- conformal abstention との接続、`ime_nav` / `ime_abandon` の現況
