# 設計 (v2)

## 実装アプローチ

`.claude/commands/finish-task.md` の **既存 Step 3 (レビュー+テスト) に
schema parity check を統合** する。新しい Step 番号は作らない。

### なぜ新設 Step ではなく Step 3 統合か

Step 3 は現行でも「回帰検証」の性質を持つ (review-changes + test-runner)。
schema parity check は本質的に **cross-repo の回帰検査** であり、
test-runner が repo 内で担っている責務の延長にある。独立 Step にすると:

- 「Step 2.5」のような小数 Step 番号が導入されフロー可読性が下がる
- parity check と test-runner が別 Step になり、「検査」概念が分散する
- 将来 tier-1 (CI) 失敗時の check を finish に足すなら同じ Step に集約したい

Step 3 に「並列で走る検査の 1 つ」として追加する方が概念整合性が高い。

### 3 つの検査を並列に走らせる Step 3

```
Step 3 (並列実行)
  ├─ review-changes            (code-reviewer + security-checker)
  ├─ test-runner               (cargo test / unittest)
  └─ schema-parity-check       (NEW — 本タスク)
           │
           └─ git diff で schema 関連ファイル touch 検出 → 非空なら helper 起動
```

並列にすることで:
- 体感レイテンシは最大要素 (review-changes) に支配される
- schema check の ~100ms は完全に隠れる
- 3 つすべてが成功しないと Step 4 (コミット提案) に進めない

### 検出ロジック: git diff 1 本化

v1 (退避版) は `git diff HEAD` + `git log --grep="Refs:"` の 2 段で、
コミットメッセージ規約 (`Refs: .steering/<taskdir>/`) に依存していた。
v2 は **git diff のみで検出を完結** させる:

```bash
# 未コミット + 未 push コミットをまとめて 1 発で拾う
MERGE_BASE=$(git merge-base HEAD origin/main 2>/dev/null || true)
if [ -n "$MERGE_BASE" ]; then
    CHANGED=$(git diff "$MERGE_BASE" --name-only -- \
        src-tauri/src/schema_dto.rs \
        src-tauri/schema/current.json)
else
    # shallow clone / offline / origin 不在: drift 見逃し回避のため
    # helper を unconditional に呼ぶ縮退動作に倒す
    CHANGED="__fallback__"
fi
```

- `merge-base HEAD origin/main` は feature branch でも main 直 commit でも
  「main から今までに加えた変更の起点」を返す。
- 対象ファイルは schema_dto.rs **と** current.json の両方を含める:
  - schema_dto.rs のみ変更 → `emit_schema` 忘れ (tier-1 が catch すべきだが保険)
  - current.json のみ変更 → 手動編集 (禁止運用の検出)
  - 両方変更 → typical case
- **shallow clone / offline fallback**: v2 初稿では `echo HEAD` に
  fallback していたが、impact-analyzer HIGH 指摘 (drift 見逃しリスク) を
  受けて sentinel `__fallback__` に変更。fallback 時は helper を
  unconditional 呼び出しする (false positive で ~100ms かかるのみ)。

**コミット規約違反への耐性**: v1 は `Refs: grep` 失敗で検出漏れしたが、
v2 は git tree そのものを見るためコミットメッセージの書式に非依存。

### helper を single source of truth として扱う

v1 は DATASET_ROOT resolution を finish-task.md 側で書いていたが、
v2 は **helper に全部任せる**:

```bash
# 環境変数 resolution は優先順位だけ明示して helper を叩く
DATASET=${GSE_DATASET:-${DATASET_ROOT:-}}
if [ -z "$DATASET" ]; then
    case "$(uname -s)" in
        MINGW*|CYGWIN*|MSYS*) DATASET="C:/gse-dataset" ;;
        *)                     DATASET="$HOME/gse-dataset" ;;
    esac
fi

# python3 優先・なければ python で fallback (sync-all.sh と同じ流儀)
if command -v python3 >/dev/null 2>&1; then
    python3 scripts/check_schema_parity.py --dataset "$DATASET"
else
    python scripts/check_schema_parity.py --dataset "$DATASET"
fi
parity_rc=$?
```

- DATASET_ROOT 不在・dataset schema 不在・prototype schema 不在は
  すべて helper が exit 2/3/4 で報告する (0795fb6 契約)
- finish-task.md 側で事前存在チェックをしない → ロジック重複を排除
- helper のエラーメッセージに修復コマンド例が入っている (tier-2 と同じ)
- **`--machine-readable` は付けない**: sentinel 形式は PS 5.1 invocation の
  `$LASTEXITCODE` 消失問題への迂回であり (§10.3.1)、Claude Code の Bash
  tool は直接 bash を呼ぶため `parity_rc=$?` で素直に exit code が取得
  できる。sync-all.sh:68-84 と同じ `|| parity_rc=$?` パターンを踏襲する。

### 失敗時の提示方法: 生出力を尊重

v1 は「Claude が helper 出力を要約して修復手順を再提示」だったが、
v2 は **helper の stdout/stderr をそのままユーザーに見せる**。理由:

- helper は既に整形済みの修復手順を持つ
  (`To fix: cd src-tauri && cargo run --bin emit_schema ...`)
- Claude による再要約は (a) 情報欠落リスク (b) 翻訳揺れリスク
- tier-2 (`sync-all.*` Step 0) と **同一の UX** を tier-3 でも提供することで
  ユーザーが同じメンタルモデルで対処できる

Claude は「helper が停止を指示した」という 1 文と「→ /finish-task は
中断」宣言を添えるだけで十分。

### DATASET_ROOT 未設定の扱いを明確化

要件 §受け入れ条件 で「未設定/不在時の挙動」を確定する必要がある:

| 状況 | v2 の振る舞い |
|---|---|
| DATASET_ROOT 解決 OK + schema touch あり + parity OK | 緑で通過 |
| DATASET_ROOT 解決 OK + schema touch あり + drift | 停止・helper 出力表示 |
| DATASET_ROOT 解決 OK + schema touch なし | skip (helper 呼ばない) |
| DATASET_ROOT 解決 NG + schema touch あり | helper が exit 3 → 停止・cp 手順表示 |
| DATASET_ROOT 解決 NG + schema touch なし | skip (helper 呼ばない) |

方針は「**schema を触ったなら DATASET_ROOT は必須**、触ってないなら無視」。
これで無関係タスクが DATASET_ROOT 未設定で壊れる問題を回避する。

## 変更対象

### 修正するファイル

- `.claude/commands/finish-task.md` — Step 3 に schema-parity-check を追加
  (~25 行追記)。frontmatter `allowed-tools` に `Bash(python *)` と
  `Bash(python3 *)` を追加 (`Bash(git *)` は既存で広いので git diff /
  merge-base は別途追加不要)
- `docs/development-guidelines.md` — §10.3.1 「呼出し」欄に `/finish-task`
  Step 3 からも呼ばれる旨を 1-2 行追記 (impact-analyzer HIGH 指摘)
- `.claude/commands/add-feature.md` / `fix-bug.md` / `refactor.md` — 末尾の
  `/finish-task を実行する` 直後に「schema parity check で停止する場合あり」
  を 1 行注記 (impact-analyzer 指摘: 利用者が「なぜ途中で止まるか」を理解
  できるよう予告)

### 新規作成するファイル

- なし (helper は 0795fb6 で完成済み)

### 削除するファイル

- なし

## 影響範囲

- **無関係タスクの /finish-task**: Step 3 で `git diff` が空 → helper 呼ばず
  スキップ。追加コスト ~20ms。
- **schema 変更タスクの /finish-task**: helper 起動 (~100ms) + 並列実行で
  隠れる。parity OK なら 1 行報告、drift なら helper 出力表示 + 停止。
- **gse-dataset 未 clone + schema 非 touch タスク**: 影響なし。
- **gse-dataset 未 clone + schema touch タスク**: helper が exit 3 で停止 +
  gse-dataset clone 手順を表示 (これが正しい挙動)。
- **docs**: `docs/development-guidelines.md` §10.3 / §10.3.1 に 「finish-task
  でも parity が走る」旨を 2-3 行追記。

## 既存パターンとの整合性

- **Step 3 並列実行の思想**: 現行の `.claude/commands/finish-task.md`
  の "レビューとテスト（並列）" 文脈を維持・拡張する
- **helper 呼出し方式**: `sync-all.sh:68-84` の python3/python fallback +
  `parity_rc=$?` キャプチャをそのまま再利用
- **並列起動の書き方**: `review-changes.md:22-29` の「以下を並列で起動する:」
  + 箇条書きパターンに合わせる
- **失敗時 UX**: helper 出力を生で見せる方針を tier-2 と統一
- **env resolution**: memory「gse-dataset layout」の GSE_DATASET → fallback
  の順を踏襲 (logger と同じ優先順位)

## テスト戦略

マークダウン workflow なのでコードテスト不可。3 ケースの手動回帰:

### 必須回帰

1. **dogfood (skip)**: 本タスクの /finish-task 実走で、Step 3 内 parity
   check が「schema 非 touch → skip」と表示されること
2. **positive (green)**: schema_dto.rs に無害な diff (末尾コメント追加 →
   emit_schema 再生成 → gse-dataset へも copy) を作って /finish-task →
   parity OK 一行報告が出ること (テスト後 revert)
3. **negative (stop)**: gse-dataset/schema/current.json を一時的に古い
   内容へ戻した状態で /finish-task → 停止 + helper 出力表示 (テスト後 revert)

### 副次確認

- `origin/main` 不在環境 (shallow clone 等) で `merge-base` fallback が
  動作すること (dry-run で `HEAD` fallback が走ることを echo で確認)
- allowed-tools 指定漏れで Bash 拒否が起きないこと (初回実行時に確認)

### 何をテストしないか

- DATASET_ROOT の 4 fallback パターンは helper が 0795fb6 で網羅済み
  (12 unittest で cover) → finish-task 側で再検証しない
- helper の exit code 0/1/2/3/4 の挙動は 0795fb6 の回帰で担保済み

## ロールバック計画

- 変更は `.claude/commands/finish-task.md` の 1 ファイル。
  `git revert <sha>` で tier-2 までの状態に戻る。
- helper 本体と sync-all.* は無変更 → tier-2 drift 検出は継続稼働。

## 実装上の注意

- frontmatter `allowed-tools`:
  - 現行: `Read, Write, Edit, Bash(git *), Task`
  - 追加要: `Bash(python *)` を許可範囲に含める
  - `Bash(git *)` は既に広いため `git diff` / `git merge-base` は別途不要
- Claude に叩かせる shell は **1 ブロック** にまとめる
  (subshell 回避・PowerShell 5.1 quirk 再発防止)
- parity check が失敗 (exit != 0) したら Claude は **Step 4 (commit 提案)
  に進まない** ことを Step 3 本文に明示
- Step 3 のサブタスクを箇条書きにし、「parity check のスキップ条件」を
  明文化 (ユーザーが "なぜ skip されたか" を後で確認できる)

## v1 との対比 (参考)

- 検出: v1 は 2 段 (git diff + git log --grep)・v2 は 1 段 (git diff のみ)
- 配置: v1 は新設 Step 2.5・v2 は既存 Step 3 統合
- DATASET resolver: v1 が finish-task 側で実装・v2 は helper に移譲
- 失敗時: v1 は Claude 再要約・v2 は helper 出力生表示
- コミット規約依存: v1 あり (Refs: grep)・v2 なし
- 追加行数: v1 ~40 行・v2 ~20 行

## 未決事項

- Step 3 に合流させるか、やはり独立 Step (v1 流) にするか — v2 では
  統合案を推すが、ワークフロー UX 観点で独立の方が読みやすい可能性あり。
  hybrid として「Step 3 の後半ブロックに `#### 3.1 Parity check` のような
  サブ見出しで入れる」も選択肢。
- docs/development-guidelines.md への tier 対応表追記は本タスクに含めるか、
  別 commit にするか (小さいので同時が素直)。

## 設計判断の履歴
- 実行回数: 1 回目
- 採用: v2 (Step 3 統合・git diff 1 段検出・helper 移譲・生出力)
- 根拠:
  1. 検出の堅牢性: v2 は git tree 直接参照でコミット規約違反に耐性あり。
     v1 の `Refs: grep` 依存は、本タスクが防ごうとしている「運用ミス起因
     の drift」と同型の再帰を生むため NG。前タスク (schema-drift-guard)
     の reimagine で ps1/sh 2 言語同期問題が v2 として解決された経緯と
     一貫する判断。
  2. DRY: DATASET_ROOT resolution の二重実装を排除できる (finish-task.md
     + helper の片方のみ更新されたときに drift する古典的アンチパターンを
     避ける)。
  3. UX 統一: tier-2 (sync-all Step 0) と tier-3 (finish) で helper 生出力
     が同一になり、ユーザーのメンタルモデルが一貫する。
  4. 変更規模: 追加行数が約半分 (~20 行 vs ~40 行)・レビュー負荷が軽い。
  詳細な比較は design-comparison.md を参照。

## 実装時の判明事項 (2026-04-17 記録)

### code-reviewer / security-checker 反映

Step 7 レビューで HIGH 3 件 + MEDIUM 4 件を検出。すべて本タスクで消化
(memory「Tech debt: now not backlog」)。

#### HIGH #1: 検出ロジックの unstaged 取りこぼしバグ (最重要)

初稿 v2 は `git diff "$BASE" --name-only` 1 段のみで検出していた。これは
**commit 済み変更のみ** を拾い、**未 stage 編集** を見逃す silent skip
バグを持っていた。/finish-task は commit **直前** に走るため、このケース
こそ最もあり得る運用パスであり、本タスクが防ごうとしている drift シナリオの
一部を素通りさせる欠陥だった。

修正: 3 つの範囲の union を取る検出に変更:
```bash
BASE=$(git merge-base HEAD origin/main 2>/dev/null || true)
SKIP=1
[ -n "$BASE" ] && [ -n "$(git diff "$BASE"  --name-only -- $SCHEMA_PATHS)" ] && SKIP=0
                   [ -n "$(git diff          --name-only -- $SCHEMA_PATHS)" ] && SKIP=0  # unstaged
                   [ -n "$(git diff --cached --name-only -- $SCHEMA_PATHS)" ] && SKIP=0  # staged
[ -z "$BASE" ] && SKIP=0  # shallow clone fallback: unconditional invoke
```

#### HIGH #2: early exit 撤廃 (スタイル堅牢化)

`exit 0` / `exit "$parity_rc"` が 3 箇所に散らばっており、将来 block が
別スクリプトに source される / 他コマンドと `&&` で繋がれる運用に
変わった時に予期せぬ親殺しを起こすリスクあり。`rc` 変数一本化 + 末尾
`exit "$rc"` の 1 箇所に集約した。

#### HIGH #3: `Bash(python *)` glob 絞り込み

frontmatter を `Bash(python scripts/check_schema_parity.py*)` /
`Bash(python3 scripts/check_schema_parity.py*)` にスクリプトパスで
限定。最小権限原則に従う (settings.local.json は変更せず、frontmatter
レベルで絞る)。

#### MEDIUM 対応

- MEDIUM #1 (3 重複注記): add-feature / fix-bug / refactor の注記を
  2 行に短縮し、詳細は §10.3.1 に集約 (SSOT 化)
- MEDIUM #2 (DATASET 既定不在時 WARN): fallback 採用後に
  `[ ! -d "$DATASET" ]` チェックを入れ、WARN メッセージ出力
- MEDIUM #3 (`__fallback__` sentinel 撤廃): `SKIP` boolean 変数に分離
  (HIGH #1 修正と同時に解決)
- MEDIUM #4 (docs indent 誤読): Windows/macOS python 行を
  tier-2/tier-3 の外 (親レベル) に移動し、共通前提として明示

### security-checker 判定

問題なし (LOW 1 件のみ: `Bash(python *)` glob が既存設定と同粒度で
拡大なし — HIGH #3 対応で更に絞り込んだため解消)。

### 動作確認サマリ (dry-run)

| ケース | 結果 | 備考 |
|---|---|---|
| dogfood skip (本タスク schema 非 touch) | SKIP=1 | BASE=e05cb19 正常解決 |
| positive (helper 起動 + parity OK) | parity_rc=0 | `[check_schema_parity] OK: schemas in sync (7369 bytes)` |
| negative (dataset 不在) | parity_rc=3 | `[check_schema_parity] FAIL: dataset schema not found` + cp 修復手順 |
| shallow clone fallback | SKIP=0 (unconditional) | BASE=[] → unconditional invoke 経路 |
| unstaged detection (HIGH #1) | 構造検証 OK | `git diff --name-only -- <path>` の 2 系統追加で拾う |
