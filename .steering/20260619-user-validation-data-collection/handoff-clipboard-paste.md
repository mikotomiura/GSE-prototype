# 次セッション開始プロンプト — punch list #2: クリップボード/ペースト計測

> `feedback_handoff_prompt_in_steering` 方針に従い、CLAUDE.md 制約込みで固定。
> participant-id Part 1-3 (PR #13/#14/#15) は main マージ済。これは
> `.steering/20260619-user-validation-data-collection/decisions.md` punch list #2。
> **新規 `/start-task` で着手 (clipboard 計測は logger/hook/schema 領域・別 PR)。**

---

## 解決する問題 (背景)

(a) AI依存度指標 (decisions.md D4) のため、**ペーストイベントの回数**を NDJSON に記録したい。
**クリップボードの中身 (テキスト) は絶対に記録しない** (D4 + data-privacy Skill 直撃)。
捕捉漏れは取り返せない (記録されないセッションの (a) データは永久に失われる) ため、実データ
収集を始める前にこの捕捉側変更を入れる。

## スコープ (候補設計 — 承認は次セッションでユーザーから取る)

- **検出方式 (privacy-safe 候補)**: 既存キーボードフックで **Ctrl+V (Windows) / Cmd+V (macOS)**
  を「ペーストイベント」として検出する。OS クリップボード API を読まない = 中身に一切触れない。
  これが D4 (回数のみ)・data-privacy (中身禁止) と最も整合。代替 (クリップボード変更監視) は
  中身アクセスの誘惑と権限増を招くため非推奨 — 設計段階で比較し決める。
- **NDJSON への記録**: `src-tauri/src/schema_dto.rs` の `LogEntryDto` (tagged enum, L29) に
  ペーストイベント variant を足す or 既存イベントにカウンタを足す。文字内容フィールドは作らない。
- **対象ファイル想定**: `input/hook.rs` / `hook_windows.rs` / `hook_macos.rs` (Ctrl+V/Cmd+V 検出・
  Atomic フラグ)、`schema_dto.rs` (DTO)、`logger.rs` (NDJSON 書き出し)、`bin/replay.rs` (新イベント
  を gse-replay が parse できること)。
- **スコープ外**: (a) 指標の算出ロジック (punch list #5)、anonymize/package (#3/#4)、
  features/HMM への組み込み (本タスクは「記録」まで。特徴量利用は別途)。

## 必須プロトコル (CLAUDE.md 準拠 — この順で)

1. **コマンド選定**: `/start-task` で `.steering/[YYYYMMDD]-clipboard-paste-count/` 作成 → `/add-feature`。
2. **docs 先読み**: `@docs/agent-shared.md` リンクハブから architecture (スレッド/データフロー)・
   repository-structure (input/ vs analysis/ 境界) を先読み。
3. **Skill 参照 (必須)**: `data-privacy` (logger/hook・中身記録禁止の確認) / `hook-constraints`
   (フックコールバック内 Atomic 操作・ブロッキング禁止) / `rust-standards` / `architecture-rules`
   (input/ に OS 依存を閉じ、analysis/ に漏らさない) / `intervention-design` は不要。
4. **サブエージェント委譲**: `file-finder` / `impact-analyzer` で既存イベント記録フロー
   (`InputEvent`→channel→logger NDJSON) と Ctrl/Cmd キー検出箇所・`LogEntryDto` 参照箇所を調査。
5. **実装後 `code-reviewer` + `security-checker` を並列起動** (logger/hook 変更は security-checker
   必須、焦点 = **クリップボード中身が一切ログ/メモリに残らないこと**・VK 検出のみであること)。
6. **`/cross-review`**: jq 不在なら Codex 系統 skip → Claude 単独へ縮退し **skip 理由を完了報告に明記**
   (既知制約: 本機は jq 未導入)。

## スキーマ変更に伴う必須手順 (重要 — 取りこぼし注意)

NDJSON スキーマ (`schema_dto.rs`) を変えるため、以下を必ず実施:

- `cargo run --bin emit_schema > src-tauri/schema/current.json` で再生成 → diff が意図どおりか確認。
- **gse-dataset 側 `schema/current.json` にコピーして同期** (tier-1 CI / tier-2 sync-all Step 0 /
  tier-3 finish-task parity が drift を検出する)。
- **既知の前提**: 2026-06-19 時点で `C:\gse-dataset\schema\current.json` は既に prototype 側より
  **古い (probe_assignment/realtime_label/session_meta/vignette_response variant 欠落)**。本タスクの
  schema 同期はこの既存ドリフトも一緒に解消することになる。コピー後に
  `python scripts/check_schema_parity.py --dataset C:/gse-dataset` が exit 0 (緑) を確認。
- **ゴールデン snapshot**: ペーストイベントを features/HMM に**まだ使わない**なら `FeatSnapshot` は
  不変のはず → `gse-replay --snapshot` byte-equal を確認。万一変わるなら `HMM_VERSION` bump +
  ゴールデン再生成 + 差分理由を `.steering/` に記録 (development-guidelines §3)。
- gse-replay が新イベント variant で panic しないこと (fixture に 1 行足して確認)。

## 検証ゲート

- `cargo test --workspace` 緑 / `gse-replay --snapshot` byte-equal / `emit_schema` 再生成 + dataset
  コピー後 parity 緑。
- 手動確認 (実機): Ctrl+V/Cmd+V でペーストイベントが NDJSON に出る・**中身は出ない**こと。
  `input/` の OS フックは実機手動確認 (development-guidelines §3)。
- code-reviewer / security-checker の CRITICAL/HIGH なし。

## 制約

- `tracing` のみ (`println!`/`eprintln!` 禁止)、`anyhow::Result`、`any` 不使用、`winapi` 禁止。
- フックコールバック内は Atomic + channel send のみ (ブロッキング禁止、hook-constraints)。
- `analysis/` で OS API を直接呼ばない (OS 依存は `input/` に閉じる)。
- **クリップボードの中身を読む/保持する/ログするコードを一切書かない** (data-privacy 最優先)。
- `.steering/` 記録を省略しない。`/finish-task` まで完遂。

## 受け入れ条件

- Ctrl+V (Win) / Cmd+V (mac) でペーストイベントが NDJSON に回数として記録される。
- クリップボード中身はメモリにもログにも一切残らない (security-checker で確認)。
- `schema_dto.rs` 変更 → `emit_schema` 再生成 → gse-dataset 同期 → parity 緑。
- `cargo test --workspace` green / `gse-replay --snapshot` byte-equal (features 未利用前提) /
  gse-replay が新イベントを parse できる。
- code-reviewer / security-checker CRITICAL/HIGH なし。

---

## 貼り付け用プロンプト (新セッションで /clear 後に投入)

```
.steering/20260619-user-validation-data-collection/handoff-clipboard-paste.md に従い、
punch list #2 (クリップボード/ペーストイベントの回数を NDJSON に記録、中身は記録しない) を
実装してください。

着手前に: /start-task で .steering/[今日]-clipboard-paste-count/ を作成 → /add-feature。
decisions.md D4 (回数のみ・中身禁止) と data-privacy / hook-constraints Skill を読む。

候補設計 (承認は会話で取る): 既存キーボードフックで Ctrl+V (Win) / Cmd+V (mac) を
ペーストイベントとして検出 (OS クリップボード API を読まない=中身に触れない)。
schema_dto.rs の LogEntryDto に variant 追加 → logger が NDJSON へ回数記録。
スコープ外: (a)指標算出(#5)・anonymize/package(#3#4)・features/HMM 組み込み。

CLAUDE.md 準拠で: /start-task → /add-feature → data-privacy/hook-constraints/rust-standards/
architecture-rules 参照 → file-finder/impact-analyzer で調査 → 実装 → code-reviewer +
security-checker 並列 (焦点=クリップボード中身が一切残らないこと) → /cross-review
(jq 不在なら Claude 単独へ縮退・skip 理由明記) → finish-task。

schema 変更手順 (必須): emit_schema 再生成 → src-tauri/schema/current.json → gse-dataset 側へ
コピー → check_schema_parity.py 緑。注: 現状 C:\gse-dataset の schema は既に古い
(probe_assignment/realtime_label/session_meta/vignette_response 欠落) ので一緒に解消する。
ゴールデンは features 未利用なら byte-equal のはず (gse-replay --snapshot で確認)。

制約: tracing のみ・anyhow・any 禁止・フックは Atomic+channel のみ (ブロッキング禁止)・
analysis/ で OS API 直呼び禁止・クリップボード中身を読む/保持する/ログするコードを書かない。
```
