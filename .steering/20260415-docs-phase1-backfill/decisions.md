# Decisions — Docs Phase 1 Backfill

## D1: 追記主体、セクション番号の再採番は行わない

### 背景
docs/ の既存構成は Phase 0 時点でよく整理されており、Phase 1 追加分を割り込ませるためにセクション番号を再採番すると diff が膨らみレビューしづらい。

### 決着
各 doc の「自然な挿入箇所」に追記:
- `repository-structure.md`: ツリー内の該当位置に `[NEW Phase 1]` 注記付きで挿入、§責務セクションに新規サブセクション追加
- `functional-design.md`: 機能 6 の直後に機能 7 (Ground Truth) を追加、UC-4 の直後に UC-GT1〜3 を追加
- `architecture.md`: §4.7 (沈黙 3 状態) を §4.10 に繰り下げ、§4.7〜4.9 に Phase 1 コンポーネント 3 件を挿入。データフローはフロー 3〜5 を追加
- `glossary.md`: ドメイン用語 / 技術用語の既存表に末尾追加
- `development-guidelines.md §3`: 範囲区分表に 2 行追加、gse-replay サブコマンドの使い分けサブセクションを追加
- `README.md` / `README.ja.md`: 「Session Replay CLI」直後に「Real-time Ground Truth Labeling」「Cross-device dataset repo」サブセクションを追加、既存「Post-session Ground-Truth Labeling」は (Legacy) と明示

## D2: glossary の列挙は既存の機能分類順を踏襲

### 背景
既存 glossary は「ドメイン用語 / 技術用語 / 略語 / 禁止用語」の順。アルファベット順ではない。

### 決着
機能分類順を維持。Phase 1 用語は「ドメイン用語」末尾 (Ground Truth / UserLabel) と「技術用語」末尾 (FeatSnapshot 以下 8 項目) に追加。

## D3: architecture.md にはテキスト中心で記述、Mermaid を新規導入しない

### 背景
既存 architecture.md は ASCII 図 + 表中心、Mermaid 未使用。新規導入すると表現スタイルが不整合になる。

### 決着
既存スタイル (ASCII 依存方向図 + 番号付きステップ) を踏襲。`repository-structure.md §4` の依存方向図に schema_dto を追記、`architecture.md §5` にデータフロー 3, 4, 5 を番号付きで追加。

## D4: README.md と README.ja.md の記述粒度を揃える

### 背景
README.md (英語) と README.ja.md (日本語) で既存セクションの粒度が揃っており、Phase 1 追記でもそれを維持しないと片方だけ古くなる。

### 決着
同じ 3 段構成 (Real-time GT + Cross-device dataset + Legacy Post-session) を両言語で追加。コマンド例は同一、説明文は自然な母語表現に調整。

## D5: CLAUDE.md は既存の §データ repo 連携で十分、追加しない

### 背景
CLAUDE.md は Claude Code がセッション開始時に自動読み込むポインタ指示書であり、詳細は docs/ で管理する設計。既に 1 セクションあり、追加情報は docs/ 側に配置する方が責務分離が健全。

### 決着
CLAUDE.md は無変更。詳細は `docs/development-guidelines.md §10` と本タスクで追記した `docs/functional-design.md §機能 7` / `docs/architecture.md §4.7〜4.9` でカバー。

## 保守性への配慮

- 新規用語が 8 ファイル (CLAUDE + README×2 + docs/5) 全てに最低 1 回現れることを grep で検証
- Phase 2a 着手時に本 backfill を参照 → schema_dto / metrics / gse-dataset の文脈を即座に復元可能
