# G1 — アプリのログをファイルに残す（在宅の被験者の失敗を追えるようにする）

## 背景

`.steering/_handoff/next-session-prompt-g1-remaining-verification.md` §3 の【B】。

- `lib.rs:1214-1224` は「⚠️ 詳細は**ローカルのログにだけ**残す」と書いている。
  画面には定型文だけを出し、参加者 ID とセッション日時を含む子プロセスの stderr は
  `tracing::error!` に回している。
- ところが `tracing_subscriber::fmt::init()`（`lib.rs:1943`）は **stdout に書くだけ**である。
  Finder からダブルクリックで起動した `.app` の stdout は**どこにも繋がっていない**
  （前セッションで unified log 41,012 行を検索して 0 行）。
- ⚠️ ★ つまり「ローカルのログにだけ残す」という設計は**成立していない**。
  詳細はどこにも残らず、画面の定型文だけが残る。
- ⚠️ ★ preregistration 第 13 版で研究者は**初回起動に同席したあと離れる**。
  その後に起きた失敗（自動提出の失敗・権限の失効・二重起動）は**原因が追えない**。

## ゴール

被験者の端末で、アプリが吐いた診断情報が**ファイルとして残っている**こと。
研究者が後からそのファイルを読めば、
「何時に何が起きて、なぜ提出が失敗したか」が分かること。

## スコープ

### 含むもの
- `tracing` の出力先にファイルを足す（stdout は開発のため残す）
- 書き込みが**打鍵フックを止めない**こと（`hook-constraints`）
- ファイルが**無限に伸びない**こと（サイズ上限＋世代交代）
- ⚠️ 保留中の follow-up: `writing-pad.html` の `beforeunload` に `started` を足す
  （§5-1。生成物を作り直す機会に入れる、という約束だった）
- 端末に残るテスト状態の後片付け（`~/.gse/g1_participant_id` / `~/Desktop/G1_実施用_macOS`）

### 含まないもの
- ⚠️ **ログの外部送信**（`data-privacy` ルール 2 の判断が要る。今回はローカル保存のみ）
- ⚠️ **配布物の作り直し**（`make-common-app-zip.sh` は**タグ付き GitHub Release** の
  dmg/exe を落としてくる設計。タグ push は deny・CI 実行は研究者の操作）
- 【A】Windows 新品端末の初回起動（実機が要る。★ 本タスクで exe が変わるので**やり直し**になる）

## 受け入れ条件

- [ ] `cargo test --workspace` が緑（`src-tauri/` から実行）
- [ ] ゴールデン回帰（`gse-replay --snapshot`）が緑
- [ ] ⚠️ ★ 「ファイルに落ちる」ことを**実測**する（テストで書けることと、
      Finder 起動の `.app` で落ちることは別。少なくともバイナリを走らせて確かめる）
- [ ] ★ 書き込み先が**打鍵フックのコールバックから同期 I/O にならない**こと（コードで示す）
- [ ] ★ ログに**文字内容が入らない**こと（`data-privacy` ルール 1。VK は可・文字は不可）
- [ ] `writing-pad.html` の `beforeunload` が「開始後は未入力でも警告する」ようになり、
      `build_task_pages.py` の検査が緑・生成済み `blockNN.html` も作り直されている
- [ ] 後片付け 2 件が済み、消したものが記録に残っている

## 関連ドキュメント

- `.steering/_handoff/next-session-prompt-g1-remaining-verification.md` §3〜§5
- `.claude/skills/data-privacy/SKILL.md`（ルール 1 / ルール 2）
- `.claude/skills/hook-constraints/SKILL.md`（コールバック内でブロッキング禁止）
- `experiments/20260801-controlled-friction-task/windows-verification.md` §3
- `docs/development-guidelines.md` §3（テスト方針）

## 運用メモ

- /reimagine 適用: No
- 理由: 引き継ぎメモで「修正はファイル出力」と方向が確定しており、
  アーキテクチャ判断ではなく既存の `LogChannel` パターンの適用である。
