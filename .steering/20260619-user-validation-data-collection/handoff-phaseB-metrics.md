# 次セッション開始プロンプト — Phase B: v0.4 アウトカム指標算出 (gse-replay --metrics)

> `feedback_handoff_prompt_in_steering` 方針に従い、CLAUDE.md 制約込みで固定。
> 親ロードマップ: WBS v2 (`wbs_検証用docs/GSE_マイルストーン_WBS_半年版_v2.docx` §4.0 M0 0.10 / §4.3 M3) +
> codex-review v0.4 §4.1/4.2。決定根拠: `.steering/20260623-capture-schema-freeze/decisions.md` (CD1-CD10)。
> **⚠️ 旧 `handoff-ab-metrics.md` / `roadmap-xy.md` Phase B の (b)=diff量÷総打鍵 は廃止済 (本書が後継)。**
> **新規 `/start-task` で着手。ブランチは下記「前提」に従い main 基点で別 PR。**

## なぜ Phase B が次か

`capture-schema-freeze` (PR, commit `0043380`) で **捕捉 (不可逆) は完了**: `external_paste_chars` /
`intervention_response`(dismiss_reason) / `condition` / `label_pool` が NDJSON に残るようになった。
次は捕捉済みデータから **(a)AI依存度・(b)自力解決率の指標を算出**する解析側 (WBS 0.10 + §4.1)。
これは WBS M3 (Phase 2 Y 価値検証) の主指標 (`paste_after_stuck_rate` / `self_recovery_without_paste` /
`manual_contribution_ratio` / `blind_quality_score`) のうち**自動算出できるもの**を `gse-replay --metrics`
に載せる。指標算出は捕捉と違い**後から再計算可能**だが、パイロット前にパイプラインを通しておくと
M1 スモークで指標の妥当性を検証できる。

## スコープ

### 含むもの — `gse-replay --metrics` (+ `--json`) の拡張
捕捉済み NDJSON (key / paste.external_paste_chars / feat.p_stuck / intervention_response) から算出:
- **(b) 自力解決率 (v0.4 §4.2)**:
  - `manual_contribution_ratio = manual_insert_chars / (manual_insert_chars + external_paste_chars)`
  - `productive_manual_recovery_rate` = Stuck 候補後 5 分以内に external paste なしで net_diff が正進行した割合
- **(a) AI依存度 (v0.4 §4.1)**: `external_paste_count` / `large_paste_rate` / `paste_after_stuck_rate` /
  `self_recovery_without_paste`。`paste_count_per_hour` は補助指標 (Ctrl+V 回数は降格)。
- `manual_insert_chars` は**既存 `key` イベント列から導出** (文字生成キー − backspace。新規捕捉不要)。
- 出力は `metrics.json` (共有アーティファクト, gse-dataset `metrics/P*/<os>/`)。**数値のみ・本文なし**。

### 含まないもの
- NDJSON schema 変更 (本タスクは算出のみ。**emit_schema/parity 不要**)。
- `blind_quality_score` (第三者ブラインド評価=人手・運用、WBS 0.13)。
- `source_role` (paste 元の内外分類=capture-schema-freeze で後置・設計フォーク、WBS 0.9 残)。
- (c) 自己効力感・NASA-TLX (アンケート)。DuckDB join (WBS C/§6)。features/HMM 組み込み。
- AB/BA・MRT の割付実装 (condition の a/b/nudge/defer 配線。別タスク)。

## 要承認の設計判断 (会話承認 — 研究設計フォーク)

1. **`productive_manual_recovery_rate` の厳密定義 (必須・複数案 → `/reimagine` 推奨)**:
   - **「Stuck 候補」のトリガ**は何か: (i) `p_stuck` が閾値超え / (ii) `user_label=stuck` / (iii) 介入発火
     (`intervention_decision.action!=none`) / (iv) probe Q1 高。v0.4 は明言せず → 要決定。
   - **「net_diff が正進行」**の定義: net_diff = 文字生成キー − backspace の純増 (content-free 代理)。
     window=5 分・「正方向」のしきい値。
   - **「external paste なし」**判定: 5 分窓内に paste 行が無いこと。
2. **`large_paste_rate` / `paste_after_stuck_rate` の閾値**: 「large」= external_paste_chars が何文字以上か。
   「after_stuck」= stuck 候補後何秒以内の paste か。
3. **`metrics.json` のフィールド命名と後方互換**: 既存 metrics 出力 (混同行列/F1 等) に追加する形。
   gse-dataset の既存 `metrics/P*/` 利用側を壊さないこと (新フィールド追加のみ)。

## 必須プロトコル (CLAUDE.md 準拠 — この順で)

1. `/start-task` で `.steering/[今日]-outcome-metrics/` 作成 → (定義が重いので `/reimagine` 検討) → `/add-feature`。
2. **docs 先読み**: WBS §4.0(0.10)/§4.3(M3) / v0.4 §4.1・§4.2 / `development-guidelines §3`(Replay-as-Truth)・
   §10(data repo) / `capture-schema-freeze/decisions.md`(CD1 external_paste_chars の意味, CD5 同期読み)。
3. **Skill 参照 (必須)**: `data-privacy` (metrics.json に中身を出さない=数値のみ) /
   `architecture-rules` (replay は bin・analysis 層の純粋関数) / `rust-standards` /
   指標を analysis モジュールに置くなら `hmm-analysis` 周辺は読むが engine は触らない。
4. **サブエージェント委譲**: `file-finder`/`impact-analyzer` で `bin/replay.rs` の
   `compute_session_metrics` / `collect_logged_feats` / `collect_user_labels` / `--metrics` 経路 /
   `--json` 出力 / 既存 metrics fixture・golden を調査。
5. **実装後 `code-reviewer` + `security-checker` を並列** (焦点 = metrics.json に**中身・キーストローク内容が
   一切出ず数値のみ**・除算のゼロ割安全・しきい値の根拠コメント)。
6. **`/cross-review` (Claude ∥ Codex)**: **jq は導入済** (`~/.local/bin/jq.exe`, 1.8.2) で
   **両系統が動く** (`project_codex_review_needs_jq` は解消)。予算/機密ゲートのみ確認。

## 前提 (ブランチ — 重要)

- **先に `feature/capture-schema-freeze` (commit `0043380`) を main へマージ**し、更新後 main から切る。
  本タスクは `external_paste_chars` / `intervention_response` / `condition`・`label_pool` が main に
  在ることが前提 (未マージだと metrics が新フィールドを読めない)。**main 直コミットしない・別 PR**。

## 検証ゲート

- `cargo test --workspace` 緑 (新 metrics の純粋関数テスト: manual_insert_chars 導出・比率のゼロ割・
  recovery 判定の境界。`compute_session_metrics` 拡張の単体テスト)。
- **Replay-as-Truth**: 新 metrics を含む golden fixture + `--metrics --json` 出力の固定値スナップショット
  を追加し回帰保護。`--snapshot` (FeatSnapshot) は不変のはず (features 不触) → byte-equal。
- **schema parity は不要** (NDJSON schema 不変)。`emit_schema` diff が出たら触りすぎ → 見直す。
- `gse-replay --metrics` が新フィールド欠落の旧 NDJSON でも panic しない (external_paste_chars=null 耐性)。
- code-reviewer / security-checker CRITICAL/HIGH なし。`/cross-review` 両系統で HIGH なし。

## 制約

- `tracing`/`anyhow`/`any` 禁止・`winapi` 禁止・`analysis/` は OS 非依存・LogEntry 変換は analysis 外。
- **metrics.json に中身 (キーストローク/クリップボード/成果物テキスト) を一切入れない** (数値のみ・data-privacy)。
- ゼロ割・空セッション・paste/key ゼロ件を安全に扱う (NaN を出さない・定義済みの既定値)。
- `.steering/` 記録を省略しない。`/finish-task` まで完遂。別 PR・main 基点。

## 受け入れ条件

- `gse-replay --metrics --json` が (a)(b) 指標 (manual_contribution_ratio / productive_manual_recovery_rate /
  external_paste_count / large_paste_rate / paste_after_stuck_rate / self_recovery_without_paste) を出力。
- manual_insert_chars が key 列から content-free に導出される。external_paste_chars (capture 済) を分母に使用。
- golden metrics スナップショットで回帰保護。`cargo test --workspace` 緑・`--snapshot` byte-equal。
- metrics.json に数値のみ・本文非混入。code-reviewer/security-checker/cross-review で CRITICAL/HIGH なし。

---

## 貼り付け用プロンプト (新セッションで /clear 後に投入)

```
.steering/20260619-user-validation-data-collection/handoff-phaseB-metrics.md に従い、
Phase B (v0.4 アウトカム指標算出) を実装してください。capture-schema-freeze で捕捉した
external_paste_chars 等から、gse-replay --metrics に (a)AI依存度・(b)自力解決率を載せるタスクです。

着手前に: 先に PR feature/capture-schema-freeze (commit 0043380) を main へマージし、更新後 main から
別ブランチを切る (main 直コミット不可)。/start-task で .steering/[今日]-outcome-metrics/ を作成 →
productive_manual_recovery_rate の定義が重いので /reimagine 検討 → /add-feature。
WBS §4.0(0.10)/§4.3 と v0.4 §4.1/§4.2、capture-schema-freeze/decisions.md(CD1/CD5)、
development-guidelines §3(Replay-as-Truth)、data-privacy / architecture-rules / rust-standards Skill を読む。

スコープ (gse-replay --metrics 拡張・算出のみ):
(b) manual_contribution_ratio = manual_insert_chars/(manual_insert_chars+external_paste_chars)、
    productive_manual_recovery_rate = Stuck 候補後5分以内に external paste なしで net_diff 正進行の割合。
(a) external_paste_count / large_paste_rate / paste_after_stuck_rate / self_recovery_without_paste
    (paste_count_per_hour は補助)。manual_insert_chars は既存 key 列から導出 (新規捕捉なし)。
    出力は metrics.json (共有物・数値のみ・本文なし)。
スコープ外: NDJSON schema 変更(=emit_schema/parity 不要)・blind_quality_score(人手)・source_role・
(c)アンケート・DuckDB join・AB/BA・MRT 割付・features/HMM 組み込み。

要承認の設計 (会話で承認、①は /reimagine 推奨): ①productive_manual_recovery_rate の厳密定義
(Stuck 候補トリガ = p_stuck閾値/user_label/介入発火 のどれか、net_diff 正進行・5分窓・external paste なし
の定義) ②large/after_stuck の閾値 ③metrics.json フィールド命名と後方互換(追加のみ)。

CLAUDE.md 準拠で: /start-task → (/reimagine) → /add-feature → 上記 Skill 参照 →
file-finder/impact-analyzer で bin/replay.rs の compute_session_metrics / collect_logged_feats /
collect_user_labels / --metrics・--json 経路 / 既存 metrics golden を調査 → 実装 →
code-reviewer + security-checker 並列 (焦点=metrics.json に中身が出ず数値のみ・ゼロ割安全) →
/cross-review (jq 導入済 ~/.local/bin/jq.exe で Claude∥Codex 両系統可) → finish-task。

検証: cargo test --workspace 緑・新 metrics の golden スナップショット回帰・--snapshot byte-equal
(features 不触)・schema parity 不要(NDJSON 不変)・旧 NDJSON(external_paste_chars 欠落)で panic しない。
制約: tracing/anyhow/any禁止/winapi禁止・analysis は OS非依存・metrics.json に中身を入れない(数値のみ)・
ゼロ割/空セッションで NaN を出さない・.steering 記録必須・別PR・main 基点。
```
