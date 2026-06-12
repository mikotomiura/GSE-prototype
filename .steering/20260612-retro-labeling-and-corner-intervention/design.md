# design.md — 事後ラベリング v0.2 レビュー＋具体設計／コーナー段階介入 UI

> 本書は 3 部構成。
> **Part A**: v0.2 の厳密レビュー(敵対的)。
> **Part B**: レビューを反映した具体設計(スキーマ・解析・事前登録・kill 基準)。
> **Part C**: コーナー段階介入 UI の再設計。
> レビュー観点は GSE 自身の検証哲学(HIR を最重要安全指標とする・defer を第一級扱い)に整合させている。

---

# Part A. 厳密レビュー — v0.2 はどこで折れるか

v0.2 は方法論的に**非常によく書けている**(報告バイアス・選択バイアス・後知恵バイアスへの自覚、ランダム対照区間、二系統ラベル、事前登録志向)。その上で、検証フェーズに進む前に潰すべき**構造的弱点が 6 件**ある。深刻度順。

## A-1 [HIGH] 波形のみの cued recall は、Van Gog の手法の前提を外している

**指摘**: v0.2 §3 は Van Gog らの cued retrospective reporting を根拠にする。だが原法の「手がかり(cue)」は**被験者が実際に見ていた刺激そのもの**(視線リプレイ＝実画面)である。v0.2 の cue は**打鍵波形のみ**(本文非表示。プライバシー境界)。打鍵リズムの形状が当時のエピソード記憶(「何に詰まっていたか」)を喚起するという経験的裏付けは無い。原法の妥当性をそのまま継承できない。

**根拠**: 想起の手がかりは「何を書いていたか」(意味内容)に強く依存する。波形は意味を剥いだ抽象表現で、想起トリガーとして弱い。弱い cue の下では、被験者は**記憶ではなく波形を「読んで」逆算**する(スパイクが多い→詰まっていた、と推論)。これは A-5(循環論法)の直接の入口になる。

**推奨修正**:
- 本文を出さずに想起強度を上げる**非内容アンカー**を足す: 時刻(壁時計)・アプリ切替マーカー・スクロール/離席イベント・(任意で)段落境界の打鍵密度のみ。意味は出さず時間軸の足場だけ与える。
- スモークで**想起精度そのものを実測**する: 較正ブリッジ(リアルタイム申告)との一致率を、波形 cue 条件で必ず取り、「波形だけで想起できているか」を数値化してから本採用する。

## A-2 [HIGH/MED] 二軸スケールは「主観の縮退」を解く保証が無い(モデルの幾何 ≠ 主観の幾何)

**指摘**: §3.2 は「モデルが 2 軸射影で判別する以上、主観も 2 軸で取れば直接照合できる」とする。これは**計算上の 2 次元分解**(X=摩擦, Y=没入)と**主観の現象学的次元数**を混同している。多くの人にとって「詰まり」と「前進」は単一の「うまくいっている感」軸の裏表で、独立に内省できる保証は無い。

**根拠**: もし大半の被験者で Q1, Q2 が r≈−0.9 に縮退すれば、「2 軸の幾何」という主張の前提が消える(実質 1 軸)。Incubation(摩擦高×前進高)が**内省的に報告可能な状態**である根拠は提示されていない。Incubation は機能的にしか定義できない可能性がある。v0.2 §11 はこのリスクを「個別被験者への教示失敗」として事後対処にしているが、これは**多数で起きたら設計の前提崩壊**であり、個別救済では済まない。

**推奨修正**:
- Q1–Q2 の独立性を**事前登録仮説**にする: 区間を統制した被験者内偏相関で検定。縮退(|r|>0.8)が過半数被験者で出たら、「2 軸主張は支持されず」と**撤回**する(教示再施行で救済しない)。
- 較正用に少数被験者で「1 軸(F/I/S 三択)」併取し、2 軸が三択より分離良という主張を**直接対比**する。

## A-3 [HIGH] ランダム対照区間で「見逃し率(Recall 下限)」は、この n では統計的に空

**指摘**: §3.3/§6.3 は対照区間(2–3/session)中の Stuck 域申告比率から Recall 下限を推定するとする。だが対照区間は定義上「非顕著」=Stuck がそもそも稀な領域。見逃し Stuck の基準率が数%なら、4 名×10 session×3 区間=120 区間でも期待ヒットは数件で、Recall 推定の信頼区間はほぼ全域に広がる。**「Recall 下限を出した」と数値を主張できる検出力が無い**。

**根拠**: 二項分布。基準率 p≈0.05, n=120 → 期待 6 件、95%CI ≒ [2%,11%]。検出器の Recall を語れる精度ではない。

**推奨修正**:
- 対照区間を**層化**して、境界近傍(顕著未満だが特徴がやや立っている)を意図的に多めに引く。または
- 対照区間の目的を**定量 Recall 推定から、定性的「重大見逃しがあるか」の探索**に格下げし、Recall の数値主張を撤回する(過大主張の方が審査で脆い)。
- どうしても数値が欲しいなら、必要 session 数を**事前に power 計算**し、足りないなら「下限の点推定は出さない」と明記。

## A-4 [HIGH] LOUO-CV は「個人化モデル」を「汎化」で測る自己矛盾、かつ n=4 で分散不安定

**指摘**: §7 は被験者内 z 正規化・個人別 β を強調する一方、§12 で LOUO-CV(Leave-One-User-Out)を主検証にする。個人化モデルを**ユーザー横断汎化**で評価するのは評価対象の取り違え。held-out ユーザーには個人化ベースラインが無いので、測っているのは設計意図と別物。

**根拠**: 個人化モデルの正しい CV 粒度は**Leave-One-Session-Out(被験者内)**。LOUO は「個人化を捨てたときの汎化」を測るので、z 正規化・個人別 β と両立しない。加えて n=4 では各 fold の指標=1 ユーザーの値で、CV 平均は 4 個のばらつく点の平均にすぎず分散推定が不安定。

**推奨修正**:
- 主 CV を**被験者内 Leave-One-Session-Out**へ。ユーザー別に指標を併記。
- 横断 LOUO は**探索扱い**に降格。
- n=3–5 は**仮説検定でなく効果量推定**のフェーズだと明記(スモークの正しい立て付け)。

## A-5 [HIGH・最深] 主観×モデル相関を「核の妥当性検証」とするのは循環論法になりうる

**指摘**: §6.3 主分析は モデル射影 (X,Y) と主観 (Q1,Q2) の相関を「2 軸射影は主観と対応するか=核の妥当性」の最重要検証とする。しかし**両者は同一打鍵列の関数**。X は特徴(修正率・休止…)から作る。主観は**その特徴で描いた波形を見せて**「どれだけ詰まっていたか」を聞いて作る。被験者が波形を読んで逆算する分だけ、X↔Q1 は**構成上**相関する。高い相関が「モデルが真の認知状態を捉えた」のか「被験者とモデルが同じスパイクを見ただけ」なのか**識別不能**。

**根拠**: cue=特徴由来波形(A-1)。confound-free なのは**較正ブリッジ(リアルタイム申告=波形を見ずに付けた)**だけ。v0.2 はこれを「1–2 session・較正専用・主分析から除外」と最小化しているが、**因果が逆**。波形を見ずに付けたラベルこそ核検証の本丸。

**推奨修正**:
- 較正ブリッジ条件を**主分析に昇格**(少なくとも confound-free 相関は較正条件で測る)。
- 偏相関で「**表示波形特徴を統制してもなお** Q1 が X と相関するか」を検定。残差相関が消えるなら、相関は波形読みのアーティファクト。
- 想起 cue を時間軸のみ(特徴非由来)にする条件を一つ作り、特徴由来 cue 条件と相関を比較。

## A-6 [HIGH・認識論] 「どちらに転んでも成果」は反証不能設計に堕している

**指摘**: §1.2/§5.2/§6.3 で繰り返される「分離しても成果/しなくても成果」「一致しても乖離しても発表価値」は、**あらゆる結末を事前に成功と枠付け**しており、間違いうる余地が無い=何も検証していない。フェイルセーフは研究の堅牢化に有効だが、ここでは**kill 基準の不在**と結びついて反証可能性を消している。

**根拠**: 妥当な検証は「これが起きたらシステムは**失敗**」という結末を事前に名指す。Phase 2a には Go/No-Go(Stuck precision≥0.6)があるのに、ラベリング設計自体には停止条件が無い。

**推奨修正**: 各「どちらでも成果」ペアに、**「興味深い null」と「アプローチが効いていない」を分ける事前登録閾値**を付す。最低一つの大域 kill を置く。例:
- 「confound-free 条件で X↔Q1 の |r|<0.3 なら、核主張(打鍵→認知状態)は不支持。Phase 2 に進まない。」
- 「過半被験者で Q1–Q2 が縮退(|r|>0.8)なら 2 軸主張を撤回。」

## A-7 以下、Med/Low(設計に効くもの)

- **[MED] 直後性ルールが skip バイアスを生む**: 「終了直後のみ・skip=ラベルなし」は、**最も疲れている回(難しい/長い/詰まった回)ほど skip** され、ラベル集合が易しい session に偏る → P3 が攻撃する Flow 過剰を**離脱経由で再導入**。修正: skip と session 特徴の相関を監視。較正ブリッジで妥当性確認した上で短い猶予窓(例 30 分以内)を許容検討。
- **[MED] 機能ラベル定義「スモークで一度だけ見直し許容」は forking paths**: §6.1 で凍結と言いつつ §11 で 1 回の調整を許す。その 1 自由度が「効く定義探し」そのもの。修正: 調整するなら**確証分析に入らない tuning split** 上だけで行い、定義 version を記録。
- **[MED] S0(task_kind)はセッション粒度で、P4(同一文書内の停滞異質性)を構造的に解けない**: §5.3 は S0 を「最強の文脈特徴」とするが、申告は session 開始時 1 回。文書途中の論証→伝達の切替を捉えない。P4 が問う**セッション内**異質性には届かない。修正: 限界として明記、または軽量な mid-session re-declare を任意提供。
- **[LOW] 沈黙支配は主トラックにも一部当てはまる**: §8.2-4 は vibe coding の沈黙問題を coding 固有として隔離するが、IME 変換中の語彙選択沈黙が多い日本語長文も同様に cued recall の信頼性が下がる。完全隔離は楽観的。
- **[LOW] プライバシーとラベル品質のトレードオフが未定量**: 本文非表示は境界として正しいが、それが想起精度を**どれだけ**下げるかは未測定。A-1 の実測でここも埋まる。

## A-8 codex 独立レビューとの照合(相互検証)

別 LLM(codex)に同設計書を**独立に**敵対的レビューさせた結果、上位指摘がほぼ一致した(循環論法・Recall 算出不能・n 水増し・cued recall 未検証・反証不能・二軸独立性)。**2 系統が独立に同じ欠陥に収束**したことは、これらが文体上の難癖でなく構造的欠陥である強い傍証。codex 固有の鋭い追加を本書に取り込む:

- **[一番鋭い framing] 波形が 4 役を兼任**: 同一の打鍵波形が「①測定対象(X,Y の素)」「②想起の手がかり(cue)」「③ラベル判断材料(被験者が見るもの)」「④機能ラベルの素」を**全部兼ねている**。A-1/A-5 はこの 1 文に集約される。**測定法の独立性が無い**のが病巣。
- **[A-3 を更に厳しく]** 顕著区間も「重要度順に上限 6 個へ間引く」(§3.4)ため、TP/FN の**母数(分母)が復元不能**。対照区間が足りないという量の問題以前に、**Recall を定義する包含確率・固定区間長・区間母集団が未定義**で、重み付き Recall すら計算できない。
- **[統計手法]** 1–5 の順序尺度を z 化して Pearson/Spearman は不適切。反復測定の非独立性(同一被験者の窓は自己相関)も無視。→ **順序ロジット混合モデル(参加者/セッションを変量効果)**へ(B-6 に反映)。
- **[欠測が MNAR]** 「覚えていない」や skip は状態依存(Flow/平穏は記憶に残りにくい、難回ほど疲れて skip)で **MNAR**。チェック欄を設けても偏りは消えない。欠測感度分析と除外基準の事前登録が要る(B-7 に反映)。
- **codex の結論**: 現段階で防御可能な主張は「**事後ラベリング UI の探索的スモークテスト**」まで。「核の妥当性」「Recall 下限」「被験者間一般化」を主張するには、**まず測定法を独立した較正研究で成立**させる必要がある。本書 Part B もこの順序(較正先行)に同意する。

> **総評**: v0.2 は「バイアスに自覚的な良い設計」だが、**波形が測定対象・想起手がかり・判断材料・機能ラベルの 4 役を兼ねる**ため測定法の独立性が無く、(1) cue が弱い・(2) 主観と特徴が同一由来・(3) フェイルセーフが反証不能化、が連鎖して**「核の妥当性検証」という最重要主張を内側から空洞化**している。**現段階の正しい立て付けは「探索的スモーク+測定法較正研究」であり、確証的 GT 収集を名乗らない**こと。Part B はこの順序に直す最小差分。

---

# Part B. 具体設計 — v0.2 を検証可能にする最小差分

v0.2 を破棄せず、A の指摘を塞ぐ**追加・置換のみ**で実装可能な形に落とす。

## B-1 想起条件を 3 つに分け、confound を識別可能にする(A-1/A-5 対応)

ラベル取得を**条件**として明示分離し、`retro_label` に `cue_condition` を持たせる:

| 条件 | cue(手がかり) | 取得タイミング | 役割 |
|---|---|---|---|
| `feature_waveform` | 打鍵波形(現行案) | 終了直後 | 量を稼ぐ主データ。ただし confound あり |
| `temporal_only` | 時刻・アプリ切替・離席のみ(特徴非由来) | 終了直後 | 波形読みアーティファクトの統制対照 |
| `realtime_bridge` | cue 無し(その場ホットキー) | セッション中(較正回のみ) | **confound-free。核検証の本丸** |

**主分析の再定義**: X↔Q1 相関は `realtime_bridge` と `temporal_only` を主、`feature_waveform` を補助とする。偏相関(表示特徴を統制)を必ず併報。

## B-2 事前登録 kill / Go-NoGo 基準(A-6 対応)

スモーク開始前に固定・文書化(`docs/` に登録):

```
[PreReg-1] 核主張ゲート:
  confound-free 条件(realtime_bridge ∪ temporal_only)で
  spearman(X, Q1) の被験者内中央値 |r| >= 0.30 を満たさなければ
  → Phase 2 に進まない(核は不支持)。

[PreReg-2] 二軸主張ゲート:
  被験者の過半で partial-corr(Q1, Q2 | segment) の |r| > 0.80 なら
  → 二軸の幾何主張を撤回し、単軸(総合うまくいき度)へ縮約して報告。

[PreReg-3] Recall 主張ゲート:
  対照区間ヒット総数 < 10 なら Recall 下限の点推定を出さない
  (定性所見のみ)。

[PreReg-4] 機能ラベル定義:
  N秒・打鍵量閾値は tuning split(全データの 20%、確証分析に入れない)
  でのみ 1 度調整可。definition_version で前後を記録。

[PreReg-5] 欠測(MNAR)感度分析:
  欠測率の区間種別・特徴量別分析、dont_remember の状態依存性検定、
  除外基準と感度分析の手順を事前登録。欠測 > 30% の被験者は確証分析から除外。
```

> **立て付けの明示(最重要)**: 上記ゲートを通すまで、本サブシステムは「**確証的 GT 収集**」を名乗らない。スモークの正当な主張は「①ラベリング UI の操作可能性確認」「②測定法(波形 cue vs 時刻 cue vs リアルタイム)の較正研究」までとする(codex 結論と一致)。較正で測定法が成立して初めて Recall・被験者間一般化を語る。

## B-3 CV 粒度の是正(A-4 対応)

- **主**: 被験者内 Leave-One-Session-Out。被験者別に HIR / Stuck precision / X↔Q1 を併記。
- **探索**: 横断 LOUO(個人化を外した汎化の感触)。
- スモークは効果量推定フェーズと明記。検定力の主張をしない。

## B-4 対照区間の層化(A-3 対応)

`segment_origin` を 3 値へ拡張:

| origin | 抽出 | 目的 |
|---|---|---|
| `salient` | 既存(長沈黙・修正クラスタ・ペナルティビン) | Precision 検証 |
| `random_control` | 完全無作為 | 分布の偏り緩和 |
| `borderline_control` | 顕著閾値の直下(特徴がやや立つ非顕著) | 見逃し推定の検出力確保 |

UI 上は 3 種を**区別表示しない**(アンカリング回避、v0.2 §3.3 維持)。

## B-5 NDJSON スキーマ拡張(既存 `schema_dto.rs` / CI drift と整合)

既存 `LogEntryDto` の tagged enum に**新バリアントを追加**する形(全て数値・カテゴリのみ、本文・タイトル・選択文字列を含まない=プライバシー境界維持)。`emit_schema` 再生成 → `schema/current.json` 更新 → CI drift 緑、までを 1 タスクにする。

```rust
// schema_dto.rs / logger.rs LogEntry へ同期追加するバリアント案

/// セッション開始宣言(v0.2 §9)
SessionMeta {
    track: TrackDto,            // main | exploratory
    task_kind: TaskKindDto,     // argumentative | correspondence | creative | vibe_coding
    monk_mode: bool,
    intervention_enabled: bool, // exploratory は false
},

/// 介入却下(v0.2 §4) — Part C のコーナー却下 UI と共有
InterventionDismiss {
    intervention_id: String,
    dismiss_kind: DismissKindDto, // not_stuck | let_me_struggle | silent
    level: InterventionActionDto, // どの段でも却下を記録(nudge/wall)
    latency_ms: u64,
},

/// 事後ラベル(v0.2 §9 改訂 + B-1 cue 条件)
RetroLabel {
    segment_id: String,
    segment_origin: SegmentOriginDto, // salient | random_control | borderline_control(UI 非露出)
    cue_condition: CueConditionDto,   // feature_waveform | temporal_only | realtime_bridge
    q1_friction: Option<u8>,          // 1..=5、dont_remember 時 None
    q2_progress: Option<u8>,
    dont_remember: bool,
    stuck_kind: Option<StuckKindDto>, // q1_friction>=4 のときのみ Some
    labeled_at: u64,
    session_ended_at: u64,            // 直後性検証(labeled_at - session_ended_at)
},

/// 機能ラベル(オフライン算出・主トラックのみ)
FunctionalLabel {
    segment_id: String,
    definition_version: String,
    label: FunctionalLabelDto, // productive_pause | unproductive_pause | active
},

/// 探索トラック AI 参照(v0.2 §9 新設、内容非保存)
AiReference {
    kind: AiRefKindDto,    // paste
    paste_len_chars: u32,  // 文字数のみ
    pre_silence_ms: u64,
    post_burst_keys: u32,
},
```

付随 enum(`TrackDto`, `TaskKindDto`, `DismissKindDto`, `SegmentOriginDto`, `CueConditionDto`, `StuckKindDto`, `FunctionalLabelDto`, `AiRefKindDto`)も snake_case で追加。`schema_dto.rs` 冒頭の運用注記どおり **LogEntry 本体と DTO を同期**し、drift check を通す。

> 注: `Meta` の排他制約と同様、`RetroLabel` の「`dont_remember==true` ⇒ q1/q2==None」「`q1_friction>=4` ⇒ stuck_kind==Some」は schemars では緩く表現されるため、**producer 側(ラベリング UI/書き込み層)で不変条件を強制**し、検証は外部 JSON Logic で補う(schema_dto.rs の既存方針に倣う)。

## B-6 解析パイプライン(gse-replay 拡張)

- `gse-replay --metrics` に `retro_label` 取り込みを追加。区間単位で (X,Y,Q1,Q2) を結合し、`cue_condition` 別に出力。
- **統計手法(codex A-8 反映)**: 1–5 を z 化した Pearson でなく、**順序ロジット混合モデル**(`Q1 ~ X + (1|participant) + (1|session)`)で X の効果を推定。被験者内偏差と絶対水準を分離。被験者別に係数と CI を併記し、平均値だけを語らない。相関ベースの図示は探索目的に限定。
- 既存 `intervention_eval`(HIR/DC/Burden)はそのまま。`intervention_dismiss` の `dismiss_kind` 内訳(✕/⏸/無言)と「⏸率」を独立指標として metrics.json に追加(v0.2 §6.3 末尾)。
- z 正規化は被験者内(metrics.json 集約時)。生 NDJSON は repo に置かず metrics のみ共有(既存ルール維持)。

## B-7 直後性と欠測(A-7 + codex MNAR 反映)

- `session_ended_at` と `labeled_at` の差を必ず記録し、**skip と session 特徴(長さ・平均 p_stuck)の相関を monitor 指標化**。
- スモークは全 session 必須を維持しつつ、較正ブリッジで「直後 vs 30 分以内」の一致率を測ってから、フィールドの緩和方針を決める(v0.2 §11 を実測駆動に変える)。
- **MNAR 対策**: 「提示した全区間」「未回答理由(skip/dont_remember)」「回答所要時間」を残し、欠測率を**区間種別・特徴量別に分析**。`dont_remember` が Flow/平穏区間に偏る MNAR を想定し、**欠測感度分析と除外基準を事前登録**(PreReg-5 として追加)。`dont_remember` を中間値 3 で代用しない方針(v0.2 §3.2)は維持。

## B-8 包含確率の事前定義(codex A-3/#2 反映 — Recall を定義可能にする)

Recall を語るなら、スモーク前に**区間母集団・検出陽性/陰性の定義・固定区間長・各層の包含確率**を凍結し、**層化確率標本として重み付き Recall**(参加者クラスタ CI 付き)を推定する。顕著区間の「上限 6 個間引き」(v0.2 §3.4)は分母を壊すので、間引くなら**間引き後の包含確率を記録**して重み補正する。PreReg-3 をこの定義込みに拡張。

---

# Part C. コーナー段階介入 UI 再設計 — 「ひょこっと companion」

## C-1 現状と要望の対応

**現状**(既存コード):
- Nudge: `Overlay.tsx` の `.nudge-card` が右から `translateX(120%)→0` でスライドイン(=既に「右からひょこっと」に近い)。
- Wall: `.wall-layer` が**全画面ブロック**(`setIgnoreCursorEvents(false)` でクリック遮断)+ "Time to Move!" + QR。これが要望の「大胆なグラフィック(霧)」に相当。
- QR/散歩導線: `wall_server.rs` が QR(SVG data URL)+ スマホ 2 分 Zen Timer + `/shake`・`/unlock` を**既に実装済み**。

**要望の本質**: 全画面 Wall を廃し、**右下コーナーで段階的にひょこっと出る一連の companion** に置換。最終段で右下に散歩 QR をひょこっと出す。JS/CSS でモダンに。

## C-2 設計上の最重要トレードオフ(先に明示)

全画面 Wall の価値は美観ではなく**不便益(forcing function)**: 物理的に作業を止めるからユーザーは席を立つ。これを「無視できる右下トースト」にすると、**介入が容易に無視され不便益が消える**恐れがある。

→ **解決方針: 「ソフト Wall」**。ハード全画面ブロックは捨てるが、最終段だけは**軽いコスト**を残す:
- 画面端の**淡いビネット(縁取りの減光)**。本文の上に霧をかけない(=要望の「霧をやめる」を満たす)。コンテンツは見えるまま、周辺視野だけ落とす。
- Wall 中の**打鍵警告**(既存 `showTypingWarning`)は維持。打てるが「今は手を止める時」と知らせる。
- クリックは**遮断しない**(`setIgnoreCursorEvents(true)` のまま)。コーナーカードと却下ボタンのみ操作対象。
- 不便益は「**散歩 QR を出す/スキャンする**」という能動的コミットに移す。Monk Mode と却下(✕/⏸)で**常にユーザーが裁定権**を持つ(v0.2 §5.3 と整合)。

> これは「強制」から「**摩擦のある招待**」への移行。GSE の `defer` 第一級扱い・「守るべき苦闘か助けるべきデッドループか」をユーザーに返す哲学と整合する。要望どおり大胆グラフィックを捨てつつ、不便益を能動コミットへ移し替える。

## C-3 エスカレーション・ラダー(全て右下アンカー)

`InterventionDecision.action` と need/accum を、**1 つのコーナー companion の状態遷移**にマップする:

| 段 | トリガー(既存ロジック流用) | 右下の見え方 | コスト | 却下 |
|---|---|---|---|---|
| S0 待機 | none / defer | 何も出さない(任意で 6px の常駐ステータスドット) | 0 | — |
| S1 Peek | `action==nudge` | 小カードが**ひょこっと**せり上がる(spring)。「ひと呼吸。」自動で引っ込む | 0(クリック透過) | 放置で消滅=silent |
| S2 Expand | nudge が持続/再来(need 上昇) | 同じカードがその場で**展開**。文言+却下2択 `✕ 詰まってない`/`⏸ 今はもがきたい` | 0 | ✕ / ⏸ / 放置 |
| S3 Walk-QR | `action==wall`(need≥0.70 持続×accum、opportunity、非 Monk) | カードが**散歩カード**に morph。QR を**ひょこっと**展開 + 画面端ビネット + 打鍵警告 | ソフト(ビネット/警告のみ。ブロックしない) | ✕ / ⏸ で撤退、Monk で恒久 off |
| S→0 退避 | p_stuck 低下 / `/unlock` / 却下 | カードが**ひょこっと引っ込む**(retract) | — | — |

- 段はすべて**可逆**。生産的打鍵が戻れば(p_stuck↓)カードは retract。
- S3 の QR は既存 `start_wall_server` の `WallServerInfo.qr_svg` をそのまま使う(Rust 側変更最小)。スマホ側 Zen Timer → 散歩(Physical Anchor Lv3/Lv4 の歩数/距離達成へ接続可能)。
- **却下 UI = v0.2 §4 のデータ源**。`✕/⏸/silent` を `InterventionDismiss` に記録(B-5)。UI と研究データが**同一コンポーネント**で一致。

## C-4 コンポーネント構成(実装インタフェース案)

`Overlay.tsx` を**全画面 wall-layer 廃止 → コーナー companion 化**:

```
src/components/intervention/
  CornerCompanion.tsx     // 右下アンカーの単一コンテナ。stage を受けて遷移
  stages/
    PeekCard.tsx          // S1: せり上がる小カード
    PauseCard.tsx         // S2: 展開 + 却下2択(✕/⏸)
    WalkCard.tsx          // S3: QR + 「散歩」導線(WallServerInfo を表示)
  EdgeVignette.tsx        // S3 のソフト減光(全画面 fixed, pointer-events:none)
  useInterventionStage.ts // InterventionDecision → stage 変換 + 可逆遷移 + dismiss 発火
```

- `stage: 'idle'|'peek'|'expand'|'walk'` を `InterventionDecision.action` + `wall_accum_ms` から導出(閾値判定はフロントに持たせず、Rust の decision を素直に写像 ← gse-v2-redesign の実装境界「Frontend は表示のみ」を順守)。
- 却下時: `invoke("record_intervention_dismiss", { kind, level, latency_ms })` → Rust `record_dismiss`(既存)+ `InterventionDismiss` ログ(新規)。`dismiss_kind` を受けて cooldown を出し分け(⏸ は同種を長め: v0.2 §4.2)。
- クリック透過は**常に true**(S3 でも遮断しない)。QR と却下ボタンだけ `pointer-events:auto` の島にする。

## C-5 モダン JS/CSS の演出方針

依存追加なし(プレーン React + CSS)で「ひょこっと」を作る:

- **せり上がり(peek)**: `@keyframes` の spring 風 cubic-bezier。
  ```css
  .companion {
    position: fixed; right: 24px; bottom: 24px;
    transform: translateY(140%);
    transition: transform .5s cubic-bezier(.22,1.2,.36,1); /* overshoot=ひょこっと */
  }
  .companion[data-stage="peek"],
  .companion[data-stage="expand"],
  .companion[data-stage="walk"] { transform: translateY(0); }
  .companion[data-stage="idle"] { transform: translateY(140%); }
  ```
- **素材感**: `backdrop-filter: blur(12px)` のガラス質カード、`border:1px solid rgba(255,255,255,.12)`、淡いグラデ縁、`box-shadow` で浮遊。ダーク基調(既存スマホ HTML の `#0f172a`/`#4ade80` とトーンを合わせる)。
- **QR 展開**: カード高さを `grid-template-rows 0fr→1fr` で滑らかに展開(reflow なしのモダン技法)。QR は `scale(.8)→1` + fade。
- **ソフトビネット(霧の代替)**: 全画面 `fixed`・`pointer-events:none`・`box-shadow: inset 0 0 180px 60px rgba(8,11,22,.55)` の縁取り減光。中央のコンテンツは曇らせない=「霧をやめる」要望を満たす。
- **アクセシビリティ**: `@media (prefers-reduced-motion: reduce)` で overshoot を無効化し fade のみ。スクリーンリーダ向けに `role="status"`/`aria-live="polite"`。
- **状態色**: peek=中立(slate)、expand=注意(amber)、walk=行動(green)。色で段を伝える(C-3 と一致)。

## C-6 既存資産の再利用と変更点

| 資産 | 変更 |
|---|---|
| `wall_server.rs`(QR/Zen Timer/`/shake`/`/unlock`) | **変更ほぼ不要**。S3 で `start_wall_server` を呼び、`qr_svg` をコーナーカードに出す |
| `setIgnoreCursorEvents` | **常に true**(現行 wall 時の false 化を撤廃) |
| `.wall-layer`(全画面) | **削除**。`WalkCard` + `EdgeVignette` に置換 |
| `showTypingWarning` | 維持。S3 のみ表示 |
| `record_intervention_dismiss` | `dismiss_kind`/`level`/`latency_ms` を受けるよう拡張 + `InterventionDismiss` ログ |
| `intervention.rs` 閾値 | **変更なし**(UI 再設計は decision 出力の写像のみ)。⏸ 却下時の cooldown 延長だけ後続検討 |
| glossary | 「Wall(Lv2)=全画面ロック」の定義を「ソフト Wall=コーナー散歩カード+ソフトビネット(非ブロック)」へ改訂。`intervention-design` Skill のルール 1/7(クリックブロック前提)も同期更新が必要 |

> ⚠ **要承認の設計判断**: 「ハード全画面ブロックを完全に捨てる」かどうかは不便益の根幹に関わる。C-2 のソフト Wall を既定案とするが、Lv2 だけハードブロックを残す折衷(S3 を `walk-soft` と `walk-hard` の 2 モードにし Monk/設定で選択)も可能。ユーザー判断を仰ぐ(tasklist 参照)。

---

# 付録. 検証フェーズ前チェックリスト(本設計の Go 条件)

- [ ] PreReg-1..4 を `docs/` に登録・凍結したか
- [ ] 3 つの cue 条件をスキーマ・UI・解析に通したか
- [ ] CV を被験者内 LOSO 主・LOUO 探索に直したか
- [ ] 対照区間を 3 層化したか
- [ ] schema drift(emit_schema→current.json)が緑か
- [ ] コーナー UI が不便益喪失トレードオフを明示し、Monk/却下で裁定権を保持しているか
- [ ] プライバシー境界(本文・タイトル・選択文字列 非保存)を全新規ログで維持したか
