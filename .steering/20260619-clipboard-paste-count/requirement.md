# clipboard-paste-count — ペーストイベント回数の NDJSON 記録

## 背景

AI 依存度指標 (decisions.md D4) のため、**ペーストイベントの回数** を NDJSON に記録したい。
AI 生成コードの貼り付けは「外部からの解の流入」であり、生産的苦闘 (struggle) の中断指標になりうる。
捕捉漏れは取り返せない (記録されないセッションの (a) データは永久に失われる) ため、実データ
収集を始める前にこの捕捉側変更を入れる。

**クリップボードの中身 (テキスト) は絶対に記録しない** (D4 + data-privacy Skill 直撃)。

参照: `.steering/20260619-user-validation-data-collection/decisions.md` punch list #2 / D4。
参照 handoff: `.steering/20260619-user-validation-data-collection/handoff-clipboard-paste.md`。

## ゴール

Ctrl+V (Windows) / Cmd+V (macOS) を既存キーボードフックで「ペーストイベント」として検出し、
NDJSON に **回数として** 記録する。OS クリップボード API は読まない = 中身に一切触れない。

## スコープ

### 含むもの
- 既存キーボードフックでの Ctrl+V / Cmd+V 検出 (Atomic + channel、ブロッキング禁止)
- `schema_dto.rs` `LogEntryDto` へのペーストイベント variant 追加 (文字内容フィールドなし)
- `logger.rs` での NDJSON 書き出し
- `bin/replay.rs` (gse-replay) が新イベントを parse でき panic しないこと
- schema 同期 (emit_schema 再生成 → src-tauri/schema/current.json → gse-dataset コピー → parity 緑)

### 含まないもの
- (a) AI 依存度指標の算出ロジック (punch list #5)
- anonymize / package 機能 (#3 / #4)
- features / HMM へのペーストイベント組み込み (本タスクは「記録」まで)

## 受け入れ条件

- [ ] Ctrl+V (Win) / Cmd+V (mac) でペーストイベントが NDJSON に回数として記録される
- [ ] クリップボード中身はメモリにもログにも一切残らない (security-checker で確認)
- [ ] `schema_dto.rs` 変更 → `emit_schema` 再生成 → gse-dataset 同期 → parity 緑
- [ ] `cargo test --workspace` green
- [ ] `gse-replay --snapshot` byte-equal (features 未利用前提)
- [ ] gse-replay が新イベントを parse できる (fixture に 1 行追加して確認)
- [ ] code-reviewer / security-checker CRITICAL/HIGH なし

## 関連ドキュメント

- docs/architecture.md (スレッドモデル / データフロー: input/ → channel → logger)
- docs/repository-structure.md (input/ vs analysis/ 境界)
- docs/development-guidelines.md §3 (Replay-as-Truth) / §10 (data repo)
- Skill: data-privacy / hook-constraints / rust-standards / architecture-rules

## 運用メモ

- /reimagine 適用: No (検出方式は handoff で privacy-safe 候補 = VK 検出に確定済み。
  代替のクリップボード変更監視は中身アクセス誘惑 + 権限増のため非推奨と既に比較済み。
  ただし最終的な検出方式の採用はユーザー承認を会話で取る)
- 理由: 設計空間は handoff で既に絞り込み済み。複数案のゼロベース再生成は不要。
