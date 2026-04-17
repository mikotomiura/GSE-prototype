# 設計 (v1 — 退避版)

## 実装アプローチ

`.claude/commands/finish-task.md` に **Step 2.5: Schema parity check (tier-3
workflow guard)** を新設し、以下 3 段で動作させる:

```
Step 2.5
  │
  ├─(a) Detection : 当該タスクで schema_dto.rs が touch されたか判定
  │     - 未コミット差分: git diff HEAD -- src-tauri/src/schema_dto.rs
  │     - タスク関連コミット: git log --grep="Refs: <taskdir>" --name-only -- <path>
  │     非空のとき → (b) へ / 空のとき → skip で Step 3 へ
  │
  ├─(b) Dataset resolve : GSE_DATASET / DATASET_ROOT / 既定パスを順に試す
  │     - $GSE_DATASET → $DATASET_ROOT → C:\gse-dataset (Win) / ~/gse-dataset (mac)
  │     見つからない → 停止し DATASET_ROOT 設定手順を提示
  │
  └─(c) Helper invoke :
          python scripts/check_schema_parity.py \
              --dataset "$RESOLVED" --machine-readable
          stdout 最終行 `HELPER_EXITCODE=<n>` を抽出して判定:
            0 → parity OK 一行報告 → Step 3 へ
           1 → drift    helper 出力を Claude が要約 + 修復手順 → 停止
           2 → proto missing → emit_schema 手順 → 停止
           3 → dataset missing → cp 手順 → 停止
           4 → usage   → 引数確認 → 停止
```

### 3 つの tier で drift を多段 catch する設計

- **tier-1**: CI `check` ジョブ = repo 内 drift (schema_dto.rs → current.json)
- **tier-2**: `scripts/sync-all.*` Step 0 = バッチ同期時の cross-repo drift
  (0795fb6 / 前タスク)
- **tier-3**: `/finish-task` Step 2.5 = **タスク閉じ時の cross-repo drift (本タスク)**

本タスクの加入により、schema_dto.rs を touch したタスクは「クローズ前に
gse-dataset 側も更新する」動作が **必ず** 実行される。tier-2 と重複するが、
tier-3 は発生時刻が早く修復タイミングが良い (「今このタスクの commit 範囲で
直せる」状態で検出する)。tier-2 は "既に閉じたタスクの drift" を遅れて catch
するセーフティネットとして残る。

### 条件実行 (unconditional にしない) 理由

unconditional 案 (毎回 helper 呼出し) も検討したが棄却:

- **DATASET_ROOT 不在で全タスクが壊れる**: gse-dataset を clone していない
  環境 (例: リモート作業、CI、初回クローン後) では `EXIT_USAGE=4` で
  finish-task が固まる。schema に無関係なドキュメント修正タスク等まで
  巻き添えになる。
- **conditional なら無関係タスクは skip**: GSE_DATASET 未設定でも
  schema 変更がないタスクは素通りできる。変更があるタスクだけが強制される。
- **cost 根拠**: 条件判定 (git diff + git log) は ~50ms。helper 起動
  (~100ms) と合わせても差分はわずかだが、不在時の UX 破綻コストが大きい。

### 検出ロジックの設計

#### (a-1) 未コミット差分

```bash
git diff HEAD -- src-tauri/src/schema_dto.rs
```

出力が非空なら touch 済み。staged / unstaged を区別せず両方を拾う。

#### (a-2) タスク関連の既コミット

main ブランチ開発スタイル (feature branch 前提にしない) のため、
"このタスクの commit" を特定するには `Refs:` コミットメッセージを grep する:

```bash
TASK_DIR=".steering/20260417-finish-task-schema-check"
git log --all --grep="Refs: ${TASK_DIR}" --name-only -- src-tauri/src/schema_dto.rs
```

`--all` を付けることで feature branch 移行した場合にも動作する。
`--name-only` は非空/空の判定を簡潔にするため。

非空なら touch 済み。(a-1) か (a-2) のどちらかが非空なら helper を呼ぶ。

**前提**: CLAUDE.md のコミットメッセージ規約で `Refs: .steering/<taskdir>/`
が必須になっている。この規約が守られる限り grep は正確に当たる。規約違反
コミットを作った場合は検出漏れするが、それは別問題 (規約違反の是正で
対応)。

### DATASET_ROOT 解決の優先順位

memory「gse-dataset layout」より `$GSE_DATASET` が第一候補。
fallback 順:

1. `$GSE_DATASET` (logger 側で既に使われている env)
2. `$DATASET_ROOT` (sync-all.ps1 が使う env・第 2 候補として互換)
3. platform 既定:
   - Windows: `C:\gse-dataset`
   - macOS: `$HOME/gse-dataset`
4. いずれも存在しない → 停止して設定手順を提示

実装上は `.claude/commands/finish-task.md` から Claude Code に上記を試行
させるだけで OK (プロセス env + ファイル存在チェック)。

### HELPER_EXITCODE のパース方式

helper は `--machine-readable` 付けると stdout 最終行に
`HELPER_EXITCODE=<n>` を emit する (前タスクで確立した契約)。

Claude Code から shell 実行する場合:
- stdout を Bash tool で受け取る
- 最終行を正規表現 `HELPER_EXITCODE=(\d+)` で抽出
- `$?` (process exit code) も追加確認 (防御的冗長)

centinel 形式を使う理由は §10.3.1 に既述 (PS 5.1 quirk 由来)。ここでは
Git Bash / WSL / macOS bash からの呼出しが主だが、同じ契約を踏襲することで
tier-2 と tier-3 で helper の振る舞い変動を作らない。

## 変更対象

### 修正するファイル

- `.claude/commands/finish-task.md` — Step 2.5 新設 (~40 行追記)
  - allowed-tools に `Bash(python *)` を追加する必要があるか確認
    (既存の `Bash(git *)` と並べる)

### 新規作成するファイル

- なし (helper は 0795fb6 で完成済み・再利用する)

### 削除するファイル

- なし

## 影響範囲

- **通常タスク (schema_dto.rs 非 touch)**: Step 2.5 で git diff / log を
  確認するのみ。~50ms 追加。helper は呼ばない。
- **schema 変更タスク**: helper 起動。parity OK なら 1 行報告。drift なら
  停止 + 修復手順提示。誤検出 false positive は helper の 12 unittest で
  担保済み。
- **gse-dataset 未 clone 環境**: schema_dto.rs を触らないタスクは影響なし。
  触ったタスクのみ「DATASET_ROOT 未設定」で停止 (これは正しい挙動)。
- **docs 更新**: `docs/development-guidelines.md` §10.3 に tier-3 の存在を
  追記 (1-2 行・テスト戦略セクションで判断)。

## 既存パターンとの整合性

- helper 契約・sentinel 形式: 前タスク (0795fb6) のまま変更なし
- `Refs: .steering/<taskdir>/` grep: CLAUDE.md コミット規約に準拠
- DATASET_ROOT fallback: logger.rs の `$GSE_DATASET` 解決ロジックと同順
- Step 2.5 番号採用: 既存 Step 1-5 を壊さない挿入位置
  (Step 2.5 が読みにくければ Step 3 を「レビュー・テスト・parity check」
  として統合する案もあり — design レビュー時に検討)

## テスト戦略

マークダウン workflow ファイルのためコード単体テストは不要。
代わりに以下の手動回帰を `tasklist.md` に列挙。

(詳細は tasklist.md 参照)

## ロールバック計画

- 変更は `.claude/commands/finish-task.md` の 1 ファイルのみ。
  `git revert <sha>` で即座に従来フローに戻せる。
- tier-2 runtime guard は無変更のため、revert しても drift 検出能力が
  tier-2 (=0795fb6 の状態) まで下がるのみ。

## 実装上の注意

- `.claude/commands/finish-task.md` の frontmatter `allowed-tools` に
  `Bash(python *)` が含まれるか確認。未含有なら追加する
- Step 2.5 の文章は Claude 向けに「何を確認し、出力をどう解釈し、何を
  ユーザーに提示するか」を明示
- Windows/macOS 両対応: `scripts/check_schema_parity.py` の呼出し

## 未決事項

- Step 2.5 ではなく Step 3 に統合する案
- docs/development-guidelines.md §10.3 への tier-3 追記
