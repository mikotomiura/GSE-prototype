# 次セッション開始プロンプト — Phase A3: 成果物スナップショット機構 (案A 前提)

> 🚫🚫 **SUPERSEDED / 廃止 (2026-06-24)** 🚫🚫
> 本 handoff は STALE な `roadmap-xy.md` §3 に基づく**誤り**。`decisions.md` D7 SUPERSEDED
> (2026-06-23 codex-review v0.4 §4.2) により **A3「成果物スナップショット/diff量」は廃止**。
> (b) 自力解決率は `manual_contribution_ratio` / `productive_manual_recovery_rate` という
> **キーストローク・カウンタ**で算出され (捕捉=#18 / 算出=#19 実装済)、成果物・diff量・暗号化保存は**不要**。
> **このタスクは実施しないこと。** 詳細は memory `project-a3-artifact-superseded` と D7。
> （以下は廃止前の記述。歴史的経緯としてのみ残す。）

---

> `feedback_handoff_prompt_in_steering` 方針に従い、CLAUDE.md 制約込みで固定。
> 親ロードマップ: `roadmap-xy.md` §2 支配原則 + §3 Phase A(A3) + §4 推奨パス + §5.3 取得法フォーク。
> 先行タスク: A1 paste(#18 凍結)/ A2 介入応答(#20)/ Phase B 指標(#19)。いずれも main マージ済
> (A2=PR #20 はマージ確認後に基点とする)。
> **新規 `/start-task` で着手。main 基点で別ブランチ・別 PR。main 直コミット禁止。**

## なぜ Phase A3 が次か

`roadmap-xy.md` §2 = **「捕捉(capture) は 算出(analysis) より前」**。パイロットで録り損ねた信号は永久に
失われる。現状マップ(§1)で唯一残る**不可逆の捕捉ギャップ**が A3:

- **成果物 (作業のアウトプット) を session 単位で保存する機構が存在しない** (§1 表「捕捉機構が存在しない」)。
- Phase B の **(b) 指標 = diff量 ÷ 総打鍵数 (+ Mehta KS[11] 補助)** は diff量を成果物から取る前提 (案A)。
  outcome-metrics(#19) は paste 由来の `manual_contribution_ratio` までは算出するが、**diff量の供給源 (A3) が
  無い**ため (b) の中核が埋まらない。
- A1(paste)・A2(介入応答) は閉じた。A3 を閉じればパイロットの捕捉完全性が揃う。

## スコープ

### 含むもの — 成果物スナップショット機構 (捕捉のみ)
- **session start / end で作業対象 (成果物) を保存**する:
  - coding track = 作業ディレクトリの **git snapshot / diff** (リポジトリ差分)。
  - 文章 track = **テキスト保存** (対象の文章ファイル/領域)。
- **中身 (raw 成果物) は raw NDJSON と同様 暗号化してローカルのみ**に保持 (外部送信しない)。
- **metrics には数値 diff量 だけ**を出す (`metrics.json` に整数/数値、本文は出さない)。
- session ⇔ 成果物 の紐付け (session ID / timestamp keyed パス)。

### 含まないもの
- (b) 指標の最終算出ロジック自体 (Phase B 側。A3 は diff量の供給=捕捉に専念)。
- anonymize / package / DuckDB join (Phase C。§3)。
- Physical Anchor / 散歩 (Phase E)。X 強化 context_beacon (Phase D)。
- features/HMM・engine の変更 (`--snapshot` byte-equal を保つ)。

## 要承認の研究設計フォーク (着手前に詰める — §5.3。/reimagine + AskUserQuestion 推奨)

A3 は**被験者端末での暗号化**という不可逆なプライバシー姿勢を確定するため、コード前に必ず決める:

1. **track別 取得法**:
   - coding = (i) git 作業ディレクトリ前提で `git diff`/snapshot を取る か (ii) git 非依存でファイルツリー
     スナップショットを取る か。対象ディレクトリの指定方法 (session 開始時に track と共に宣言?)。
   - 文章 = どの対象を取るか (ファイルパス指定 / エディタ連携 / 手動エクスポート)。アプリ非依存性。
2. **session ⇔ 成果物 紐付け**: session ID の発番 (既存 SessionMeta/SessionStart timestamp を使うか新規 ID か)、
   start/end の 2 スナップショットの対応付け、保存パス命名 (`raw/P000/` 配下に session keyed で置くか)。
3. **暗号化フロー**: Phase C の `package-session` が **age 暗号化**を使う方針 (§3)。A3 の raw 成果物も age に
   揃えるか。鍵管理 (被験者端末でどう鍵を持つ/配るか)、暗号化のタイミング (capture 時 即暗号化)。
4. **diff量 の算出地点 (重要)**: raw 成果物は暗号化ローカルのみ。よって **diff量 (数値) を誰がいつ計算するか**:
   (i) capture 時に被験者端末で start↔end の diff量を計算し metrics に数値だけ出す (raw は暗号化保存) か、
   (ii) Phase C のパイプラインで復号して計算するか。data-privacy 上は (i) が「数値のみ外に出す」と整合。
5. **後方互換 / schema**: NDJSON に新イベント (例 `artifact_snapshot` の参照/ハッシュ/diff量) を足すなら
   `schema_dto.rs` 変更 → `emit_schema` 再生成 + gse-dataset parity 必須。`Option`/新 variant で後方互換 (CD4)。
   `HMM_VERSION` は不変 (features 不触)。

## 必須プロトコル (CLAUDE.md 準拠 — この順で)

1. `/start-task` で `.steering/[今日]-artifact-snapshot/` 作成 → **設計フォークが重く不可逆**なので
   `/reimagine`(プラン段階) + 上記 5 フォークを **AskUserQuestion で確定** → `/add-feature`。
2. **docs 先読み**: `roadmap-xy.md` §2/§3(A3)/§4/§5.3 / `handoff-ab-metrics.md`(=(b)指標と diff量の使われ方) /
   `development-guidelines.md` §3(Replay-as-Truth)・§9(schema drift)・§10(data repo・暗号化ローカル) /
   `functional-design.md`(Y(b) 成果物) / 既存 `decisions.md`(capture-freeze CD1/CD4/CD6 暗号化・arboard 等)。
3. **Skill 参照 (必須)**: `data-privacy`(**最重要** — ML rule3 匿名化/暗号化/opt-in・本文非記録・外部送信禁止・
   暗号化ローカル) / `architecture-rules`(取得層と analysis 層の分離・OS 依存は input/ + sensors に隔離) /
   `rust-standards` / schema を変えるなら整合確認。暗号化方式は Phase C 方針 (age) と揃える。
4. **サブエージェント委譲**: `file-finder`/`impact-analyzer` で logger の default_log_path / SessionMeta /
   SessionStart / End・GSE_DATASET 解決・既存 metrics.json 生成経路 (gse-replay --metrics)・暗号化に使えそうな
   既存依存 (Cargo.toml) を調査。
5. **実装後 `code-reviewer` + `security-checker` を並列** (焦点 = **成果物本文が NDJSON/metrics に漏れない**・
   暗号化が正しく適用され平文が残らない・鍵の扱い・外部送信ゼロ・session 紐付けの正しさ・後方互換)。
6. **`/cross-review` (Claude ∥ Codex)**: jq 導入済 (`~/.local/bin/jq.exe`)。予算/機密ゲートのみ確認。
   **成果物の平文・diff 内容を Codex 入力に含めない** (NDJSON 生ログ・本文の外部送信禁止)。
7. **`/finish-task`**: schema を変えたら schema parity check (tier-3 guard) が gse-dataset 整合を検証。
   **drift 検出時は commit せず停止**し修復。

## 前提 (ブランチ — 重要)

- **main に A2 (PR #20) がマージ済**であることを確認後、更新 main から `feature/artifact-snapshot` を切る。
  **main 直コミットしない・別 PR**。
- 未コミットの `.codex/budget.json` / `MEMO` / `wbs_検証用docs/` / 旧 handoff はステージしない (据え置き)。
- **gse-dataset の schema 同期**: A2 で `C:/gse-dataset/schema/current.json` を同期したが push は安全ゲートで
  保留 (別リポ main 直 push)。A3 着手前に dataset 側の取り込み (branch+PR or 承認 push) を解消しておく。

## 検証ゲート

- `cargo test --workspace` 緑 (成果物取得・暗号化・diff量算出・紐付けの純粋関数テスト。平文非残留の read-back)。
- **`--snapshot` byte-equal 不変** (features/engine 不触)。
- schema を変えたら **`emit_schema` parity + gse-dataset parity 緑** (実走必須)。旧 NDJSON で gse-replay panic しない。
- **平文非漏洩**: NDJSON / metrics.json に成果物本文・テキスト・コード片が一切出ない (数値/ハッシュ/カテゴリのみ)。
- code-reviewer / security-checker / `/cross-review` で CRITICAL/HIGH なし。

## 制約

- `tracing`/`anyhow`/`any` 禁止・`winapi` 禁止・`analysis/` は OS 非依存 (取得の OS 依存は input/+sensors に隔離)。
- **成果物の本文・コード・文章を NDJSON/metrics に一切入れない** (暗号化 raw はローカルのみ・metrics は数値のみ)。
- **リアルタイム外部送信禁止** (data-privacy ルール2)。被験者同意・匿名化・バッチのみ (ルール3)。
- `.steering/` 記録を省略しない。`/finish-task` まで完遂。別 PR・main 基点。

## 受け入れ条件

- session start/end で成果物が track 別に取得され、**暗号化ローカル保存**される。
- **diff量 (数値) が metrics に出力**され、Phase B の (b) 指標が供給を受けられる。
- NDJSON/metrics に本文非混入。`--snapshot` byte-equal。schema 変更時 parity 緑・`cargo test --workspace` 緑。
- code-reviewer/security-checker/cross-review で CRITICAL/HIGH なし。

## 並行 (非コーディング・あなたの実機作業)

- **A1 paste 実機確認**: Win/mac 実機で Ctrl+V/Cmd+V の `external_paste_chars` 発火を手動確認 (CI 不可・§6)。
  A3 とは独立に進められる。

---

## 貼り付け用プロンプト (新セッションで /clear 後に投入)

```
.steering/20260619-user-validation-data-collection/handoff-phaseA3-artifact-snapshot.md に従い、
Phase A3 (成果物スナップショット機構・案A 前提) を実装してください。捕捉の不可逆性 (roadmap-xy §2) により、
パイロット前に閉じるべき最後の捕捉ギャップで、Phase B の (b) diff量指標が依存します。

現状: 成果物を session 単位で保存する機構が存在しない (roadmap §1)。A1(paste #18)・A2(介入応答 #20)・
Phase B 指標(#19) はマージ済。A3 は session start/end で作業対象 (coding=git snapshot/diff、文章=テキスト) を
取得し、中身は暗号化ローカルのみ、metrics には数値 diff量 だけを出す。

着手前に: main に PR #20 がマージ済か確認し、更新 main から feature/artifact-snapshot を切る (main 直コミット
不可)。A3 は被験者端末での暗号化という不可逆なプライバシー姿勢を確定するため、コード前に設計フォークを詰める:
/start-task で .steering/[今日]-artifact-snapshot/ 作成 → /reimagine + AskUserQuestion で §5.3 の 5 フォーク
(①track別取得法 ②session⇔成果物紐付け ③暗号化フロー=age と揃えるか/鍵管理 ④diff量の算出地点=被験者端末で
数値だけ出すか ⑤schema 変更の要否と後方互換) を確定 → /add-feature。

docs 先読み: roadmap-xy §2/§3(A3)/§4/§5.3、handoff-ab-metrics.md、development-guidelines §3/§9/§10、
functional-design.md(Y(b))、capture-freeze decisions.md(CD1/CD4/CD6 暗号化)。Skill は data-privacy(最重要・
暗号化/匿名化/本文非記録/外部送信禁止) / architecture-rules / rust-standards を参照。

スコープ (捕捉のみ): 成果物の取得+暗号化ローカル保存、session 紐付け、metrics への数値 diff量 出力。
スコープ外: (b)指標の最終算出ロジック・anonymize/package/DuckDB(Phase C)・Physical Anchor(E)・X 強化(D)・
features/HMM 変更。

CLAUDE.md 準拠で: /start-task → /reimagine + AskUserQuestion(5フォーク) → /add-feature → 上記 Skill 参照 →
file-finder/impact-analyzer で logger(default_log_path/SessionMeta/SessionStart/End/GSE_DATASET)・
metrics.json 生成経路(gse-replay --metrics)・暗号化に使える既存依存(Cargo.toml) を調査 → 実装 →
code-reviewer + security-checker 並列 (焦点=成果物本文の NDJSON/metrics 非漏洩・暗号化で平文非残留・鍵の扱い・
外部送信ゼロ・後方互換) → /cross-review (成果物平文を Codex 入力に含めない) → finish-task (schema 変更時は
parity 実走必須・drift で停止)。

検証: cargo test --workspace 緑・--snapshot byte-equal(features 不触)・schema 変更時 emit_schema parity 緑・
旧 NDJSON で panic しない・NDJSON/metrics に本文非混入(数値/ハッシュ/カテゴリのみ)。制約: tracing/anyhow/any
禁止・winapi 禁止・analysis OS 非依存・リアルタイム外部送信禁止・暗号化ローカルのみ・.steering 記録必須・
別PR・main 基点。着手前に gse-dataset の schema 同期 push 保留を解消しておくこと。
```
