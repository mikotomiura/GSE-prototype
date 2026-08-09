# 次セッション開始プロンプト — G1 配布の自動化（研究者の手作業を減らす）

このファイルの「===」以下をコピペして開始する。

**前提**: 2026-08-07 に **v0.1.23 のリリースまで完了**した。
★ 梱包 (`make-distribution.sh`) は**もうある**。⚠️ **作り直さない。**
残っているのは **Drive への配置とメール送信**の自動化である。

---

===

## §0 このセッションでやること

★ **研究者が手でやっている 2 か所**を自動化してよいか検討し、決めたら実装する。

```
G1-C 提出 → onG1ConsentSubmit（★ 自動）
              ├ P-ID 採番（Phase1 ロスター・LockService で衝突防止）
              ├ 「G1 実施トラッキング」に行追加
              └ 📧 受付メール（★ P-ID は入る。⚠️ ダウンロードリンクは入っていない）
   ↓
⚠️【手作業 1】python3 assign.py --subject P0XX && python3 validate_blocks.py
⚠️【手作業 2】./make-distribution.sh P0XX both     ← ★ これは自動化済み
⚠️【手作業 3】Drive へ上げて共有リンクを作る       ← ★ 今回の主目標
⚠️【手作業 4】sendTaskMaterialsEmail(pid, email, url) を Apps Script で実行 ← ★ 今回の主目標
```

★ **最初に読むもの（この順）**:

1. `experiments/20260801-controlled-friction-task/make-distribution.sh`
   （★ 冒頭コメントに「**やらないこと**」を 3 つ書いてある。⚠️ 蒸し返さない）
2. `Form_G1/GSE_G1_Form_Builder.gs` の `onG1ConsentSubmit` / `sendTaskMaterialsEmail` /
   `g1RegisterAckBody_`（★ **1262 行付近のコメントが「登録時にリンクを送れない理由」**）
3. `.idea/短縮版リンク集.md` の `[G1 配布物のダウンロード]`（⚠️ **gitignore 済み**）

## §1 いまの状態（★ 2026-08-07 実測）

- `main` = マージ済み（PR #90）。**リリース `v0.1.23` 公開済み**
  （`gse-next.exe` / `gse-submit.exe` / `gse-next_0.1.23_aarch64.dmg` / `gse-unpack(.exe)`）
- ★ **梱包は 1 コマンドで通る**（`PILOT-win both` で実走確認）:
  ```bash
  cd experiments/20260801-controlled-friction-task
  ./make-distribution.sh <被験者ID> both        # → dist/<ID>/G1_実施用_{Windows,macOS}/
  ```
  ★ fail-closed ガード 4 本が **rc=1 で止まることを実測済み**
  （割付なし / 自動送信を含まないタグ / 壊れた `g1-submit.json` / 設定ファイル不在）
- 配布リンク（既存・手動で作ったもの）: `.idea/短縮版リンク集.md` を見ること

## §2 ★ 決めるべきこと（実装前に）

| # | 論点 | ⚠️ 注意 |
|---|---|---|
| **A** | Drive のどこに置くか（例 `Gate/G1/配布/<P-ID>/`） | ★ 既存の `Gate/G1/G1_実施用_{Windows,macOS}` は **P-1 用の共通フォルダ**。被験者別にするなら別の階層にする |
| **B** | 共有範囲（リンクを知っている全員 / 個別に招待） | ⚠️★★ **配布フォルダには `g1-submit.json`（共有シークレット）が入る**。「リンクを知っている全員」は実質公開に近い |
| **C** | 短縮 URL を作るか | ★ `setXgdKey()` の仕組みが既にある（`Form_G1/README.md` 末尾）。⚠️ 短縮すると**中身の差し替えに追随する**か要確認 |
| **D** | メール送信を自動にするか | ★ `sendTaskMaterialsEmail(pid, email, url)` は**すでにある**（本文生成・送信・「課題文リンク送信日」記録まで）。⚠️ `G1_AUTO_SEND=false` なら下書き止まり |
| **E** | どこから叩くか（ローカル bash / Apps Script / 両方） | ⚠️ ★ **Apps Script の関数セレクタは自動操作を受け付けない**（4 回試して 4 回失敗・実測）。人が押す前提の設計にする |

## §3 ⚠️★★ 設計の制約（★ 蒸し返さないこと）

1. ★ **割付 (`assign.py`) を梱包・アップロードのついでに走らせない。**
   seed を使う科学的な行為であり、⚠️ 取り違えると「同じ人に 2 通りの割付」が黙って生まれる。
   `make-distribution.sh` は**意図的に**割付を作らず、無ければ止めて手順を出す。
2. ★ **アプリを手元でビルドしない。** 配るのは CI のリリース成果物だけ
   （署名・entitlements の後処理が CI と揃わない）。
3. ⚠️★ **登録時点ではリンクを送れない。** 割付がまだ無いうえ、
   メール本文に題材名を書くと**提示順を示唆する**（`preregistration.md §2.12`）。
   → ★ 「受付メール」と「事前資料メール」を **2 便に分けてある**のは意図である。
4. ⚠️★ **外部へ上げる操作は既定 dry-run にする。** 一度上げたものは取り消せない。
5. ⚠️ ★ `g1-submit.json` を追跡ファイル・public な場所に置かない。

## §4 ★ 使えそうな材料

- `mcp__claude_ai_Google_Drive__*`（`create_file` / `search_files` / `get_file_permissions`）
  ⚠️★ **`drive-mcp-upload-fidelity` の既知問題**: `textContent` 送信は中身次第でバイトが化ける
  （エスケープ列を含む HTML で **44B 欠損を実測**）。★ 上げたら `fileSize` を照合すること。
  ⚠️ **更新・削除ができない**ので、壊すと重複が残る。→ ★ **バイナリ (exe/dmg) を MCP で
  上げてよいかは要検証**。ダメなら `rclone` / ブラウザ手動 / `gh` 以外の経路を検討する。
- `scripts/make-participant-zip.sh`（Windows 解凍で日本語名が化けない zip を作る）
- `Form_G1/GSE_G1_Form_Builder.gs` の `sendTaskMaterialsEmail` / `g1EnsureRunRow_`

## §5 ⚠️ まだ残っている「研究者の手作業」（★ 本タスクとは別）

1. ⚠️★★ **G1-C の余分な同意項目 1 件を消す**（★ **実施前に必須**）
   - `migrateConsentForm()` の parity 結果: **不足 0 / 順序ズレ 0 / ⚠️ 余分 1**
   - 余分は **D-14 で置き換えたはずの旧文言**（「…自動送信される…」）。
     ★ いま実フォームには**矛盾する 2 つの同意文が並んでいる**。
   - ★ 消してよい根拠: `incident-20260807-g1c-rebuild.md` §2 に
     「レコード 3 件は残存。⚠️ **全項目が「回答なし」= 答えと設問の紐付けが失われた**」と実測がある
     → **旧項目に紐づく有効な同意回答は無い**。
   - ★ 手順: **Google フォームの編集画面**でその 1 問だけ削除 →
     Apps Script で `checkConsentFormParity()` → `✅ G1-C はコードと一致している`
     （★ `f6a415d` でログに出るようにしたので、⚠️ `GSE_Gate1` に最新の `.gs` を貼り直すこと）
   - ⚠️ **`setupG1Forms()` を実行しない**
2. **B-3**: `measureSaveTiming()` を受け口プロジェクトで 1 回実行し、
   `gas-measurements.md §3` の「未実測」を消す
3. **未実測**: 端末 → 実エンドポイントの通し確認 / **Windows 実機**での動作確認

## §6 ⚠️ 環境の罠（★ 先に読む）

| 罠 | 中身 |
|---|---|
| ⚠️★★ `git push` / `gh pr merge` は **deny** | `.claude/settings.json` の `permissions.deny`。★ ユーザに `! git push` を打ってもらう |
| ⚠️★★ `~/.cargo/bin/cargo` が壊れている | 実体は `~/.rustup/toolchains/stable-aarch64-apple-darwin/bin/cargo`。PATH に足さないと `run.sh` の cargo ゲートが素通りする |
| repo 直下の `cargo test` は空振り | `Cargo.toml` は `src-tauri/` |
| ⚠️ **Bash の cwd が持ち越される** | ★ 2026-08-07 に踏んだ。**絶対パスで書く** |
| ⚠️★★ Apps Script の関数セレクタ | **自動操作を受け付けない**。★ 保存も通っていないことがある → リロードして実体で確かめる |
| ⚠️★ `strings \| grep -q` | grep が即終了 → strings が SIGPIPE → `pipefail` が **偽陰性**を作る。★ `grep -c` を使う（2026-08-07 に実測で踏んだ） |

## §7 ⚠️★ やらないこと

- ★ `make-distribution.sh` を作り直さない（fail-closed ガード 4 本は実測済み）
- ★ 割付を梱包・アップロードに巻き込まない（§3-1）
- ⚠️ ★ `preregistration.md §3.1/§3.2/§3.4/§3.5/§3.6` を変更しない
- ⚠️ ★ `schema_dto.rs` を変えない
- ⚠️ ★ 受付メールに題材名・提示順を書き戻さない（`§2.12`・`check_g1_emails.py` が検査する）
