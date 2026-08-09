# 次セッション開始プロンプト — 提出レシート UI ＋ Windows 実機のフック検証

このファイルの「===」以下をコピペして開始する。

**前提**: 2026-08-09 に「キーボードフックの silent death 検知」を実装し、
Windows CI まで緑にした。⚠️ ★ **実機での発火確認だけが残っている。**

---

===

## §0 このセッションでやること（★ この順で）

```
【A】★ 提出レシート UI を実装する（= 送信が成功したことを被験者に明示する）
【B】push → CI を 1 回だけ回して windows-portable artifact を取る
【C】試験配布 ZIP を作って Drive に上げる（⚠️ g1.mode は入れない）
【D】Windows Claude Code 用の検証プロンプトを Drive に上げる
```

⚠️ ★ **A を先にやる理由**: 先に UI を入れておけば **CI 1 回**の artifact で
「フック検証」と「次の本番配布」の両方を賄える（Actions 分数の節約）。

## §1 いまの状態（★ 確認済みの事実）

| | 状態 |
|---|---|
| ブランチ | `feature/g1-distribution-automation`（**push 済み**・`e08a252`） |
| ★★ Windows CI | **緑**（run `31316460555`。`check (windows-latest): success`） |
| その意味 | ★ 今回の Windows 固有コードが **Windows で初めてコンパイル・テストを通った** |
| 未コミット | `docs/literature/` 系 4 ファイル（★ **別トラック**。触らない） |
| `~/gse-dataset` | schema 同期を `7cc8430` でコミット済み。⚠️ **push はしていない** |

### 実装済みのもの（`.steering/20260809-g1-hook-liveness-detection/`）

- `input/liveness.rs` — `GetLastInputInfo` の生 tick の**変化**と `CALLBACK_COUNT` の**変化**を
  1 Hz で突き合わせ、starvation を累積。判定は OS 非依存の純関数（閾値 30 s / 120 s）
- トレイ = `HOOK_ACTIVE && !HOOK_STARVED`／NDJSON に `hook_health` 行
  （`alive` / `starved_ms` / `rehook` / `dropped`）
- `validate_blocks.py` が `alive=false` を **FAIL** にする（消費者を実装済み）
- ⚠️ **被験者の画面 (`get_hook_status`) は意図的に変えていない**（誤検知があるため・盲検）

## §2 【A】提出レシート UI（★ ここが今回の実装）

### 何が問題か（★ コードで確認済み）

`src/App.tsx` の G1 提出 UI は 3 状態しか出さない:

| 状態 | 表示 |
|---|---|
| 承認待ち | 緑「このブロックの記録を送信しますか？」(`:546`) |
| 未送信 N 件 | オレンジ「まだ送れていない記録が N 件」(`:634`) |
| エラー | 赤「自動送信でエラー」(`:670`) |
| ★ **送信成功** | ⚠️ **何も出ない**（箱が消えるだけ） |

⚠️★★ しかも実機ログでは **承認 → 送信完了に 6.2 秒 / 5.7 秒**かかっており、その間も無表示。
→ ★ **「警告が消えた ＝ 成功」と読ませている**。本セッションで潰した silent failure と同じ構造。

### 設計（★ 決定済み。実装するだけ）

1. ★ **肯定形のレシート**: `✅ この回の記録を送信しました（HH:MM・N 件）`
   ⚠️★★ **根拠は「ボタンを押したこと」ではなく、バックエンドの `sent` が実際に増えたこと。**
   （押した＝成功、にすると**偽のレシート**になる。今回いちばん避けたい形）
2. **送信中**: 承認直後〜完了までの数秒に `送信しています…` を出す（★ 無表示の空白を作らない）
3. **肯定形の「全部送れています」**: 未送信 0 件のとき明示する（否定の不在に頼らない）
4. ⚠️ 文言に**認知状態の手がかりを入れない**（盲検維持）

### 実装の当たり所

- `SubmissionStatus` は `{awaiting_approval, errors, packaged, sent, skipped_busy, unsent, upload_disabled}`
  （★ 実機ログの JSON で実測済み）。`sent` の増分を検出する。
- ポーリング箇所は `App.tsx` の `get_submission_status`。
- ⚠️ ★ **`/start-task` で別タスクとして起票する**（フック検証とは別トラック）。

### ⚠️ UI を変えたら必ず

- ★ `tsc --noEmit` は色を見ない。**実マウント + 対照つきで輝度差を測る**
  （memory `ui-changes-need-eyes`。2026-08-08 に「背景と同色の文字」を実機で出した）
- ★ ボタンは `color` を継承しない。**文字色を明示する**（`App.tsx` にその教訓のコメントあり）

## §3 【B】CI ビルド（★ 手順は確立済み）

```bash
gh workflow run ci.yml --ref feature/g1-distribution-automation   # → build-windows だけ走る
gh run download <run id> -D dist/hook-liveness-test               # windows-portable / windows-tools
```

- ⚠️ ★ **push 由来の run が終わってから発火する**。`ci.yml` の `concurrency` は
  `cancel-in-progress: true` なので、先に発火すると push の run が巻き添えで cancel される。
- artifact の保持は **7 日**。
- ⚠️ ★ **手元の `cargo build` は使わない**（`windows-verification.md §0.1`:
  `--no-bundle` の release 構成とフロント本番ビルドが違うので検証にならない）。

## §4 【C】試験配布 ZIP（★ 中身を間違えない）

```
GSE_フック検証/
├── gse-next.exe          ← CI 本番バイナリ
└── 検証手順_先に読む.txt
```

- ⚠️★★ **`g1.mode` を入れない。** 入れると自動提出が走り 5 分でブロックが切れて
  下記 T-B / T-C が成立しない。
- ⚠️ `gse-submit.exe` も入れない（提出は不要。★ 誤って本番データに混ざる事故を避ける）。
- Drive の親フォルダ `1qhl28IDeh-19upuZf_YxPwwdq_d9xVcI` は **owner のみ**（実測確認済み）。
  ⚠️ ★ **15 個の被験者フォルダ（`anyone: reader`）には絶対に置かない。**
- ★ 上げたら **`fileSize` を手元と照合する**（memory `drive-mcp-upload-fidelity`）。

## §5 【D】Windows 実機の検証設計（★ ここが本丸）

OS に silent unhook を**命令する手段は無い**。так分解して確かめる:

| | 何をする | 何を見る |
|---|---|---|
| **T-A 陰性対照** | 2 分**打ち続ける** | `hook_health` 行が **1 行も出ない** |
| **T-B ★ 陽性対照** | 2 分**マウスだけ**動かす | 30 秒で ERROR ／ 120 秒でトレイ `⚠ 計測できていません` ／ `hook_health` の `alive:false` ／ `rehook:true` |
| **T-C ★★ 復帰と二重フック** | T-B の直後に **20 打ちょうど** | 打鍵が記録される ＋ `alive:true` の行 ＋ ⚠️ **同一 `t` の重複 `key` 行が無い** |
| **T-D 自然発生** | 通常作業で長時間動かす | 本物の死が出るか（8/9 は 3 回中 2 回で起きた） |

- ★★ **T-B は「既知の誤検知」をそのまま陽性対照に使う**のが要点。
  これで **`GetLastInputInfo` が Windows で本当に動くか**（一度も実行していない）も同時に確かめる。
- ⚠️★★ **T-C が落ちたら、私の「復旧」が健全なフックを壊している**ということ。
  → その場で `request_reinstall` を無効化する判断材料になる（cross-review 両者一致の HIGH だった箇所）。
- Windows 側 Claude Code への依頼は **収集専任**（memory `windows-agent-collection-only`）。
  ★ 「0 件」は必ず**陽性対照とセット**で出させる。

## §6 ⚠️★ 本セッションで踏んだ罠（★ 繰り返さない）

1. ⚠️★★ **macOS では `hook_windows.rs` が 1 行もコンパイルされない。**
   `EVENTS_DROPPED` の import 忘れを、手元の `cargo test` / `clippy` / `fmt` が**全部緑で通した**。
   → ★ 検査手段は **CI だけ**（`cargo check --target x86_64-pc-windows-msvc` は tauri の
   build script が `llvm-rc` を要求して落ち、`llvm-tools-preview` にも `llvm-rc` は無い。**実測**）。
   ★ **Windows 固有ファイルを触ったら、CI が緑になるまで「通った」と言わない。**
2. ⚠️★ **`cargo test --workspace` は `packaging` の 23 件を走らせない**
   （`#[cfg(feature = "package")]` の裏）。★ `--features package` を付けると 315 → **338**。
3. ⚠️★ **「未知の type は読み飛ばす」は `--metrics` 経路だけ。** `--snapshot` (`run_replay`) は
   未知タグを `Err` で**中断する**。★ ゴールデン fixture は全部旧形式なので、
   **ゴールデンが緑でもこの事故は検出できない**。
4. ⚠️ テストの一時ディレクトリ名が既存テストと衝突し、**単独では緑・全体実行で赤**になった。
5. ★ 提案した「復旧」が、誤検知中に**生きているフックを壊し続ける**設計だった
   （cross-review で Claude / Codex が一致して指摘）。→ 1 エピソード 1 回に限定。

## §7 ⚠️ 積み残し（急ぎでない）

- `analyze.py` 側の `hook_health` 消費者（`validate_blocks.py` には入れた）
- macOS への配線（`CGEventSourceSecondsSinceLastEventType`・D-4）
- ⚠️★★ **`gse-dataset` の既存 NDJSON が schema 検証を通らない**（★ 私の変更とは無関係）。
  `raw/` は匿名化済みで `key` が `{"category":…}` だが schema の `Key` は `{"vk":u32}` のみ
  → ★ **実測 1 ファイル 13,115 errors**。schema と匿名化のどちらを正とするか判断が要る。
- `~/gse-dataset` の **push は未実施**
- `/finish-task`（`/cross-review` は本セッションで実施済み・縮退なし）
