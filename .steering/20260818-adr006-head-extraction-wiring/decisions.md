# 重要な設計判断

grill 実施日: 2026-08-18（`/start-task` → `grilling` skill・Opus）

---

## D-0: Phase1 は収集打ち切りで終了 → 凍結解除

- **判断日時**: 2026-08-18
- **背景**: `docs/adr/README.md` は「すべて Phase1 完了 + 研究者承認が前提。凍結対象
  （`schema_dto.rs` / `schema/current.json` / `engine.rs` HMM_VERSION / `intervention.rs` 閾値 /
  `probe_scheduler.rs` / `App.tsx` argumentative lock / `preregistration-v0.3.md`）は
  Phase1 完了まで変更禁止」と定めていた。ADR-006 Migration step 1 も「Phase1 完了 + verdict 確定を待つ」。
  一方 `experiments/20260731-phase1-calibration-analysis/notes.md` §5① は「収集継続（最優先）」と書いており、
  **文書上は Phase1 未完了に見えた**。
- **選択肢**:
  - A: notes.md の記述どおり Phase1 継続中とみなし、engine には触らない
  - B: 収集を打ち切って Phase1 を終了扱いにし、凍結を解除する
- **採用**: **B**（研究者判断・2026-08-18）
- **理由**: 収集を打ち切る判断が下されたため。GATE3 = `DataInsufficient` が確定値として残る。
- **トレードオフ**: GATE3（モデルゲート）は母数 n=1 のまま確証エビデンスにならずに終わる。
  PreReg-4 の「全員 >0.55」は判定されないまま Phase2 へ持ち越す。
- **影響範囲**: `notes.md` §5① の「収集継続」記述は現状と食い違うため要更新。
  `docs/adr/README.md` の凍結注記も要更新。
- **見直しタイミング**: Phase2 の設計時に、GATE3 を再度どう満たすかを決める必要がある。

---

## D-1: 2a と 2b を別コミットに分ける

- **判断日時**: 2026-08-18
- **背景**: ADR-006 Migration の逐語「抽出は動作非変更＝HMM_VERSION 不変、配線は挙動変更＝
  HMM_VERSION bump。**両者を混ぜて 1 コミットにしない**」。
- **選択肢**:
  - A: 1 タスク 1 コミットでまとめて実装する
  - B: 2a（byte-equal）を先に緑にしてから 2b（bump）を積む
- **採用**: **B**
- **理由**: 2a の acceptance が byte-equal である以上、2b の挙動変更と混ぜると
  「意図した差分」と「リファクタの事故」を切り分けられなくなる。ADR 逐語どおり。
- **トレードオフ**: コミットが 2 つに増え、レビューが 2 回になる。
- **影響範囲**: tasklist の分割単位。
- **見直しタイミング**: なし（ADR 逐語）。

---

## D-2: 2b に Coding head v0（β のみ）を含める

- **判断日時**: 2026-08-18
- **背景**: head が Writing しか無い状態で `task_kind` → head を配線しても、表は
  「全 4 variant → Writing」の 1 行になり挙動はゼロ変化。それでは
  `research-positioning.md §9` A-Q3 解除条件②「`task_kind`→β 配線」は**実質未達**のまま。
- **選択肢**:
  - A: Writing head 抽出だけで止め、Coding head は Epic 4 で
  - B: Coding head v0（現 β_coding を初期シードとして所有・coding イベントは無し）を 2b に含める
- **採用**: **B**（研究者判断）
- **理由**: ADR-006 下位決定 #3 が既に「Coding head は現 β_coding を初期シードとして継承」と
  決めており、β 部分だけなら Epic 4 の本体（accept/reject/test/revert）を待たずに実装できる。
  これで §8 が名指しした交絡（日本語コメントを書く coder が IME on で誤って β_writing）が実際に消える。
- **トレードオフ**: Coding head の主信号（coding イベント）が無いため、Coding 側の推定は
  「弱い補助である打鍵 β だけ」で走る。ADR-006 #3 自身がその位置づけを認めている。
- **影響範囲**: `HMM_VERSION` bump が必要になる（D-4）。ゴールデン追加が必要になる（D-5）。
- **見直しタイミング**: Epic 4 で coding イベントを入れたとき、β の重みを再チューニングする。

---

## D-3: Coding head v0 も backspace ペナルティの IME gate を持つ

- **判断日時**: 2026-08-18
- **背景**: 現行 `engine.rs:367` は `apply_backspace_penalty = pending && !ime_open`。
  ADR-006 はこの gate を「Writing 固有」と書いているが、**Coding 側の扱いを書いていない**。
- **選択肢**:
  - A: Coding head も同じ gate を持つ（IME on の間は BS ペナルティを抑止）
  - B: gate なしで常に適用（coding の BS は「書き直し＝摩擦」だから拾う）
  - C: Coding head v0 は BS ペナルティを持たない
- **採用**: **A**
- **理由**: 2b の目的は β の取り違えを直すことであって BS 挙動を変えることではない。変更面を最小に保つ。
  日本語コメントを打つ coder の IME 変換修正を誤ペナルティしない、という現行 gate の利点もそのまま残る。
- **トレードオフ**: coding における「書き直し＝摩擦」を IME on の間は拾えない。
- **影響範囲**: `engine.rs` の backspace ペナルティ経路。
- **見直しタイミング**: Epic 4 で coding イベント（revert / diff-review）が入り、
  「書き直し」を別シグナルで取れるようになったとき。

---

## D-4: `HMM_VERSION` は `0.4.0`（MINOR）+ SemVer 定義の穴を埋める

- **判断日時**: 2026-08-18
- **背景**: `engine.rs:36-40` の SemVer 定義は
  「MAJOR = 既存セッションログの確率列が大幅に変わる / MINOR = 確率列は動くが同じラベル付けになる範囲 /
  PATCH = ログ形式のみ（数値挙動不変）」と、**すべて「既存ログ」基準**で書かれている。
  今回は既存ログが全て `argumentative` なので確率列が 1 ビットも動かず、変わるのは
  **まだ存在しない `vibe_coding`** だけ。→ 3 つのどれにも素直に当てはまらない。
- **選択肢**:
  - A: `0.4.0`（MINOR）+ engine.rs のコメントに定義を 1 行足す
  - B: `1.0.0`（MAJOR）— vibe_coding では状態優勢の逆転が起き得るため安全側
  - C: `0.3.1`（PATCH）— 既存ログに対する数値挙動は不変
- **採用**: **A**
- **理由**: 既存ログの確率列は変わらないので MAJOR の定義には当たらない。一方 bump しない
  （あるいは PATCH に留める）と「同一版で 2 挙動」になり、`gse-replay` の版検証が意味を失う。
  定義に穴がある以上、**定義そのものを直してから bump する**のが筋。
- **トレードオフ**: `0.4.0` は「確率列は動くが同じラベル付け」を含意するが、vibe_coding では
  ラベル付けが変わり得る。この含意のズレは engine.rs コメントの追記で明示する。
- **影響範囲**: `engine.rs:45` / SemVer コメント / `logger.rs` の meta 行 / `glossary.md:157`
  （「現行 `0.3.0`」の記述）/ `docs/wbs-verification-halfyear.md:232`。
- **見直しタイミング**: Coding head を実データで再チューニングするとき（Epic 4）。

---

## D-5: 2b でゴールデン `vibe_coding_ime_mixed` を新規追加する

- **判断日時**: 2026-08-18
- **背景**: 既存ゴールデン 4 本（`minimal` / `phase1_ime_heavy` / `category_coverage` / `deep_silence`）は
  すべて argumentative 相当なので、**2b でも byte-equal のまま**。つまり ADR-006 Migration step 4 が
  要求する「ゴールデン再生成 → 差分が意図通りか記録」の**差分が存在しない**。
  このまま進めると vibe_coding 経路は回帰保護ゼロで生まれる。
- **選択肢**:
  - A: `tests/fixtures/vibe_coding_ime_mixed.ndjson` + snapshot を新規追加（4 → 5 本）
  - B: engine の単体テストだけで担保する
  - C: vibe_coding + creative の 2 本追加（4 → 6 本）
- **採用**: **A**
- **理由**: 「IME on/off が混在する vibe_coding セッションで β が切り替わらない」ことを
  パイプライン全体（features → engine → loop_step）で固定できる。既存 4 本の byte-equal は
  「無関係な副作用が無いこと」の証明として使い、新規 1 本が「意図した差分」を担う。
  Creative は Writing head へ流す（D-6）＝挙動が現行と同一なので、既存 4 本が実質そのゴールデンになる。
- **トレードオフ**: ゴールデンが 1 本増え、以後の HMM 変更時の再生成コストが上がる。
- **影響範囲**: `bin/replay.rs:2916` の `cases` 配列 / `tests/fixtures/` / `tests/snapshots/`。
- **見直しタイミング**: Coding head に coding イベントが入るとき、fixture を作り直す。

---

## D-6: Creative は Writing head へ流し、`head_id` を刻む

- **判断日時**: 2026-08-18
- **背景**: ADR-006 下位決定 #3 は「**Creative は打鍵 β を持たせない**。打鍵希薄で無音＝idle と
  区別できず打鍵 β は原理的に不適。feasibility のみ（Epic 6）」と決めている。
  しかし**代替の head がまだ無い**ため、「持たせない」を字義どおり実装すると
  Creative セッションでは推論が出せなくなる。
- **選択肢**:
  - A: Writing head へ流すが、出力に `head_id`（例 `writing_fallback`）を刻んで後から分離可能にする
  - B: 推論を出さない（head 未定義）。#3 に忠実だが `evidence_quality` 未実装のため
       UI・logger 側に分岐追加が必要で変更面が広がる
  - C: Writing head へ流す（印なし・最小）
  - D: Creative head v0 を T2（編集/タイムラインイベント）込みで作る
- **採用**: **A**
- **理由**: 挙動は現行維持（ゴールデンへの影響ゼロ）でありながら、「適合していない head で
  採点されたセッション」を事後に分離できる。C は分離できず、B は本タスクの射程（analysis 層）を
  超えて UI/logger に波及する。D は T2 拡張が別タスク（D-7）である以上、今は取れない。
- **トレードオフ**: ADR-006 #3 の「打鍵 β を持たせない」から**実質的に逸脱する**。
  この逸脱は ADR-006 に明記して残す（口頭で済ませない）。
- **影響範囲**: head 選択テーブル / `FeatSnapshot` または推論出力への `head_id` 追加（additive）。
- **見直しタイミング**: Epic 6 で Creative の feasibility を評価するとき。
  `head_id` で分離した Creative セッションがその一次データになる。

---

## D-6b: `β_coding` → `β_writing_latin` の改名を波及**させない**箇所

- **判断日時**: 2026-08-18（code-reviewer 指摘を受けて明文化）
- **背景**: 改名すると repo 内の旧名参照をどこまで直すかが問題になる。
- **直した**（生きた現行仕様を語る文書・コード）:
  - `src-tauri/src/analysis/heads/writing.rs`（定義そのもの）
  - `docs/glossary.md` / `docs/repository-structure.md`
  - `docs/architecture/personalization-and-online-learning.md:120`
  - `.claude/skills/hmm-analysis/SKILL.md`（engine 編集時の必須参照なので放置すると次の担当者が旧名で探す）
- **直さない**:
  - ⚠️ `experiments/20260801-signal-diagnostics/constants.json:14` の `BETA_CODING_F1` —
    **凍結された実験アーティファクト**。`reproducibility-discipline` により、過去の実験が
    どの定数で走ったかの記録は書き換えない。
  - `docs/adr/ADR-006-task-kind-beta-wiring.md` 本文の旧名言及 — **決定時点の記述**であり、
    ADR は決定の記録なので遡及改変しない（実施記録は追記で足す）。
  - `docs/design-history.md` 等の履歴文書。

---

## D-6c: `DomainInferenceHead::latent_axes` を `&self` にする（cross-review で意見が割れた点）

- **判断日時**: 2026-08-18
- **背景**: `/cross-review` で **Claude (code-reviewer) と Codex の結論が逆**になった。
  - **Codex**: `latent_axes(&self, ...)` + `Arc<dyn ...>` は「将来 per-session EWMA で β を更新」と
    相性が悪い。状態を持つ head は内部可変性へ逃げる必要があり、thread-safety / lock 粒度 /
    session 分離が曖昧になる。2b 以降で設計負債化しやすい。
  - **Claude**: `Arc<dyn>` はむしろ将来性で優位。`&self` のまま内部可変性で対応でき、
    `&'static dyn` にしていたらその道が塞がる。generics 化は型パラメータが `lib.rs` の
    Tauri `State`・スレッド起動・`loop_step` へ伝播し、挙動不変コミットの範囲を桁違いに広げる。
- **採用**: **`&self` + `Arc<dyn>` のまま**（Claude 側）
- **理由**: 既存の `CognitiveStateEngine` が既に `Arc<Mutex<_>>` の塊で、
  `update(&self, ...)` という共有ハンドル型である。head だけ `&mut self` にしても
  engine 側で結局 Mutex を通ることになり、Codex が懸念する「内部可変性へ逃げる」状態は
  **head を `&mut` にしても解消しない**。2a は挙動不変コミットなので、
  境界の形を今変える理由がない。
- **トレードオフ**: per-session β 適応（`personalization-and-online-learning.md`）を入れる段で、
  head 内の可変状態の lock 粒度を設計し直す必要が残る。Codex の指摘はその時点で有効になる。
- **見直しタイミング**: ADR-008（オンライン学習の境界）を実装するとき。

---

## D-7: T2 観測空間拡張は別タスク

- **判断日時**: 2026-08-18
- **背景**: `docs/research-positioning.md:537-547` の段別表で **T2 =
  「アプリ切替回数 / ポインタ動態 / 編集イベント」**。`§9` A-Q3 の解除条件②
  「`task_kind` → β 配線」がまさに本タスクなので、2b が終われば T2 の門の片方が開く。
  （もう片方の「B-a プール倍率の実数」は研究者「現時点では分からない」のまま未了。）
- **選択肢**:
  - A: 2b 完了後の別タスク
  - B: 収集の配線だけ先にやる（NDJSON へ additive に記録・推論には使わない）
  - C: 本タスクに含める（Creative head v0 まで）
- **採用**: **A**
- **理由**: T2 は **input 層（OS フック）の新規実装**で、analysis 層に閉じた 2a/2b とは
  触るファイルが完全に別。混ぜると 2a の byte-equal による切り分けが効かなくなる。
  また Win / mac 両方のフック実装が要り、タスクが大きく膨らむ。
- **トレードオフ**: T2 の ablation を回すためのデータが溜まり始めるのが 1 タスク分遅れる。
- **影響範囲**: 次タスクの起点。`research-positioning.md §8` T2 行 / `input/` 層。
- **見直しタイミング**: 2b マージ直後。

---

## D-8: `DomainInferenceHead` のみ trait 化する（`DomainAdapter` は Epic 4/5）

- **判断日時**: 2026-08-18
- **背景**: ADR-002（Proposed）は `DomainAdapter`（`adapter_id` / `task_kind` / `ingest` /
  `feature_snapshot` / `privacy_audit`）と `DomainInferenceHead`（`head_id` / `infer`）の
  2 つの trait を立てると書いている。
- **選択肢**:
  - A: `DomainInferenceHead`（`infer`）のみ実装。`DomainAdapter` は Epic 4/5
  - B: ADR-002 逐語どおり両方立てる
  - C: trait を立てず具体型 + enum 分岐
- **採用**: **A**
- **理由**: 今回の 2 head（Writing / Coding v0）は**同じ `Features` を消費する**ので
  `ingest` を分ける必要が無い。`DomainAdapter` は input 層に食い込み、実装者が 1 つしか無い
  状態で境界の形を固定することになる。`DomainInferenceHead` の方は Coding head v0 の追加で
  実装者が 2 つになるため、抽象化の根拠が実際に立つ。
- **トレードオフ**: ADR-002 の Migration 逐語からの部分的な逸脱。→ ADR-002 に明記して昇格する。
- **影響範囲**: ADR-002 のステータス（Proposed → **Accepted**、trait 範囲を明記）。
- **見直しタイミング**: Epic 4 で Coding Adapter を observe-only で入れるとき。

---

## D-9: `App.tsx` の argumentative lock は本タスクの射程外

- **判断日時**: 2026-08-18
- **背景**: lock を外さない限り実運用では `vibe_coding` セッションが発生せず、2b は
  「配線されているが実データでは効かない」状態になる。
- **選択肢**:
  - A: 別タスク（Phase2 の運用設計とセット）
  - B: 本タスクで外す
  - C: デバッグビルドだけ外す
- **採用**: **A**
- **理由**: コードは 1 行だが、被験者が任意の `task_kind` を選べるようにするには Phase2 の
  募集・教示・条件割付の運用設計が要る。研究運用は 1 行では済まない。
  2b は「lock を外した瞬間に効く」状態で置いておく。
- **トレードオフ**: 2b の実効性が Phase2 の運用設計まで保留される。
  テスト fixture は手書きできるので実装・検証には支障しない。
- **影響範囲**: 次々タスクの起点。
- **見直しタイミング**: Phase2 の被験者募集設計に着手するとき。

---

## D-10（記録のみ・本タスクでは実装しない）: Wall の扱いは「保留」が repo の記録である

- **判断日時**: 2026-08-18（**事実の訂正記録**）
- **背景**: 引き継ぎ `.steering/_handoff/next-session-prompt-task-kind-beta-wiring.md` §3 は
  「**研究者は Wall を廃止したが、リポジトリが追随していない**」と書いているが、
  **出典が無く、repo の記録と逆である**。
- **repo にある研究者決定**（`.steering/20260816-survey-synthesis-and-design/theme-a-claim-scope.md:179`・
  **A-Q6 / 2026-08-16**）:
  > 決定済み（研究者）= 「粒度が粗い」と明記するに留める。**主軸から外すかは表現層
  > PM-Q1〜Q7（700 行・承認待ちで凍結）の解除とセットで後日。**
- **引き継ぎ §3 の出所と思われるもの**: `.idea/20260806-media-self-reflection-and-behavioral-intervention.md`
  §3.3「主たる不便介入を Lv2 Wall から Lv3/Lv4 散歩へ移す」（2026-08-07 追加）。
  同メモは理由を思想でなく**証拠の質**に置いている
  （`[V40]` structure 系 = inconclusive vs `[P47]` 散歩 = +1,029.99 歩/勤務日・GRADE high certainty）。
  ただし同メモ自身が「**Phase 1 の凍結には影響しない / 書き換えが必要なのは
  `research-positioning §4` と `§5`、Phase 2 の改訂範囲（今やる作業ではない）**」と書いている。
- **同メモ §3.4 の警告（決定的）**: 「サリエンスの段階化と、不便（コスト）の段階化は別の軸である」。
  Wall を外して段階を表現層に担わせると、GSE は `[V40]` の
  **structure 系（唯一 inconclusive = 未否定）から information 系（d=0.00・BF01=33.84）へ移動する**。
  → **Wall 単独では決められない。「不便を Lv3/Lv4 散歩が担う」ところまで込みで決める必要がある。**
- **本タスクでの扱い**: **コードも docs も一切触らない**（Out）。A-Q6 の「保留」が現在の決定。
- **実装上の実測（削除を検討する将来のために記録）**:
  - `bin/replay.rs:150-156` は `intervention_decision` / `intervention_response` 行を
    `serde_json::Value` の catch-all で受けて中身をデシリアライズしない。`deny_unknown_fields` は無し。
    → **`action="wall"` / `wall_accum_ms` を型から消しても既存 Phase1 ログは読める**
    （消してはいけないのは行の**トップレベル type タグ**。`hook_health` で踏んだ前例が `replay.rs:157-164`）
  - `docs/preregistration-v0.3.md` に Wall の言及は **0 件** → 事前登録契約は壊れない
  - ゴールデン fixtures に wall 行は **0 件** → byte-equal は壊れない
  - ⚠️ **本当の重さは削除工数でなく研究指標の再定義**: `intervention_eval.rs:56,65,89` の
    **ACT/HOLD 二値化が `Act = {Nudge, Wall}`** で、HIR / DC / Burden がこれに乗っている
  - ⚠️ `intervention.rs:339-356` の `decide()` は Wall 分岐が Nudge より**先に評価される
    単一 if-elif カスケード** → 分岐を削るだけで Nudge/Defer の閾値境界の意味が変わる
  - `gse-v2-overview.md:91` は既に「Wall は v2 Core の必須機能でなく高リスクの実験介入」、
    `wbs-verification-halfyear.md` M4 は既に「Wall / Physical Anchor を別実験に分離」と記述済み
- **見直しタイミング**: PM-Q1〜Q7（表現層）の承認が解除されたとき。
