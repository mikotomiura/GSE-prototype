# 次セッション開始プロンプト — **O1 の実配備（★ 研究者の手作業が主役）**

> ★ このファイルの「===」以下をコピペして開始する。
> ⚠️ 前セッションから `/clear` して**新セッション**で始めること。
> ★ モデル: **Opus**（⚠️ 被験者向け文面の承認と、実測値からの timeout 判断が混ざる）。

---

===

## §0 ⚠️★★★ 最初に固定すること

### 0-1. ★ **機械が状態を持っている。文書を信じる前にこれを走らせる**

```bash
bash scripts/check-o1-release-readiness.sh            # ★ 通過 13 / 未達 1 のはず
bash scripts/check-o1-release-readiness.sh --selftest  # ★ 27/27 のはず
cd experiments/20260801-controlled-friction-task && bash make-common-app-zip.sh --selftest  # ★ 16/16
```

⚠️★★★ **ゲートは今も赤いのが正しい**（2026-08-28 夜の時点で **通過 13 / 未達 1**）。
★ 残り 1 件は **送信 timeout の実測**であり、⚠️ **受け口のデプロイ（B-1）に依存する**。

### 0-2. ⚠️ **未解決の一覧はここ 1 か所にある**

> `.steering/20260828-o1-gate-closeout-and-deployment/open-issues.md`

★ 引き継ぎメモは毎回書き換わるので、⚠️ **消えた項目と直った項目の区別がつかなくなる**。
→ ★ 上のファイルが単一の場所である。⚠️ **本メモを一次資料にしない。**

### 0-3. ⚠️★★★ **繰り返してはいけない誤り**

- 2026-08-27: dev が `Form_G1/README.md` の**古い記述だけ**を見て 2 件を**誤報した**。
- 2026-08-28 夜: ⚠️ **AI が「改行コードが未報告の欠陥だ」と書いたが誤りだった** ——
  `.gitattributes` に `*.bat text eol=crlf` が既にあり、⚠️ **作業ツリーの写しが古かっただけ**
  （★ `decisions.md` 判断 4 に訂正を残してある）。
- → ⚠️ **外界の状態はゲートか実物で、コードの挙動は一次資料（`.rs` / `.gs` / `.gitattributes`）で。**

### 0-4. ✅ **2026-08-28 夜に完了したもの**（★ 作り直さない）

| 何 | 状態 |
|---|---|
| **E-1** 削除後の案内の O1 分岐 | ✅ `RecordingControls.tsx`（⚠️ **実機クリックは未実施** → §3） |
| **A-1** O1 の liveness | ✅ `liveness::tray_starved` ＋ `O1_LIVENESS_TRAY_AFTER_MS = 30 分`（★ ログ 30 秒 / 再設置 120 秒は据え置き・5 テスト） |
| **A-2** ゲートの検査 | ✅ 「実測の記録 ＋ コードの修正」の**両方**を要求（⚠️ 数字の書き換えでは緑にならない） |
| **F-12** CI | ✅ `cargo test --features package`（★ 実測: 付けないと `reconcile::` が **0 件**） |
| **E-4 / E-5** 配布物 | ✅ launcher の BOM ／ 同梱物の `MANIFEST` 単一化（検査 2 件追加） |
| ゲート selftest | ✅ **22 → 27 件** |

---

## §1 ★ やること（⚠️ **順序に依存がある**）

| 順 | 何 | 誰が | 依存 |
|---|---|---|---|
| **1** | **B-1** 受け口（GAS `doPost`）のデプロイ | ⚠️ **研究者だけ** | 無し |
| **2** | **B-2b** 配布フォルダを作る（`O1_APP_DOWNLOAD_URL`） | ⚠️ 研究者 | 無し |
| **3** | **B-2** フォーム 2 本 | ⚠️ 研究者 | 2 |
| **4** | **A-2** 1 日ぶんの実サイズで通し確認 → timeout を決める | ★ 研究者と AI | **1** |
| **5** | **C** README 2 本の承認 → **D** macOS で配布物 | ⚠️ 研究者 | 2 |
| **6** | **B-4** 削除 UI の実機クリック | ⚠️ 研究者が操作 | 無し（★ いつでもできる） |

> ### ★ **手順の正本は 1 つのファイルにまとまっている**
>
> `.steering/20260828-o1-gate-closeout-and-deployment/deployment-runbook.md`
>
> ★ 研究者から渡された Drive の ID（受け取り先 / メイン / フォーム集約先）を差し込んである。
> ⚠️ **配布フォルダだけはまだ存在しない**（★ 受け取り先を配布に転用しないこと ——
> 「リンクを知る全員が閲覧可」にするので、**他の被験者のセッションファイルが見える**）。

## §2 ⚠️★★ A-2 の閉じ方（★ ここだけ手順が特殊）

1. `experiments/20260801-controlled-friction-task/o1-upload-timeout-measurement.md` を開く。
2. ★ **1 日ぶんの実サイズ**で送り、⚠️ **Drive 保存時間を含めて**測る。
3. `<!-- gate:o1-upload-timeout -->` 直下の 6 行を埋める（★「状態」を **実測済み** に）。
4. `src-tauri/src/reconcile.rs` の timeout を「採用した timeout」に直す。
5. `bash scripts/check-o1-release-readiness.sh` → ★ **通過 14 / 未達 0**。

⚠️★★★ **数字だけ書き換えて緑にしないこと。**
★ ゲートは記録票とコードの**両方**を見るので、片方だけでは赤のままである
（★ `--selftest` の「コードだけ直しても赤になる」がそれを測っている）。

## §3 ⚠️ 残っている検証

- [ ] ⚠️ **B-4「この時間帯の記録を消す」の実機クリック** — ★ **いまだ未実施**
      （★ 検算: `redaction_ledger.jsonl` が生成されていない ＝ 削除 UI は 1 度も使われていない）
      ```
      GSE_O1_MODE=1 GSE_DATASET=<スクラッチ> ./src-tauri/target/debug/gse-next.exe
      ```
      ⚠️ **debug ビルドは `devUrl` を見る**ので、先に `npm run dev`（ポート 1420）を上げること。
      ⚠️★ **E-1 の直しはこの経路で踏める。★ 一時停止 → 削除 の順で操作し、
      案内が「記録を再開する」に変わっていることと `redaction_ledger.jsonl` を見る。**
- [ ] ⚠️ **macOS 実機での `make-common-app-zip.sh --mode o1`**
      （★ 別引き継ぎ `next-session-prompt-o1-macos-distribution.md`・⚠️ `--tag v0.1.29` を明示）
- [ ] ⚠️ **受け口の 1 日ぶり実サイズでの通し確認**（→ §2）

## §4 ★ git / CI の状態（⚠️ 引き継ぎ時点で実測）

- ブランチ **`feature/o1-deployment-infra`**
- ⚠️★★ **CI は本変更に対して未実行**（★ push していない）。
  ⚠️ **`.github/workflows/ci.yml` を変更している**ので、⚠️ push して初めて
  `--features package` を足した `cargo test` が緑かどうかが分かる。
  ★ 手元では `cd src-tauri && cargo test --features package --workspace` = **562 passed / 0 failed**。
- ⚠️ **PR は未作成**（★ `main` へのマージは研究者判断）。

### ⚠️★★★ **外界にはまだ何もしていない**

| 何 | 状態 |
|---|---|
| Apps Script への貼り付け・デプロイ・トリガ設置 | ⚠️ **未実施**（0 件） |
| Google フォームの作成 | ⚠️ **未実施** |
| Drive のフォルダ作成・共有設定の変更 | ⚠️ **未実施**（★ ID を受け取っただけ） |
| メール送信 | ⚠️ **0 通** |
| ブラウザ操作（Claude in Chrome） | ⚠️ **1 回も使っていない** |
| gse-dataset への push | ⚠️ **0 件** |

---

## ⚠️★★★ 本セッションの作業規約（★ CLAUDE.md より抜粋・省略しない）

1. **`.steering/[YYYYMMDD]-[task-name]/`** に `requirement.md` / `design.md` / `tasklist.md` を必ず作る
   （★ `/start-task` → `/finish-task`）。
2. **該当するスラッシュコマンドを必ず先に起動する**。
3. **必須 Skill を読んでから手を動かす**: `verify-before-claiming` /
   `browser-verification`（★ `mcp__claude-in-chrome__*` を使う最初の 1 回で必ず）/
   `data-privacy` / `rust-standards` / `git-workflow`。
4. **サブエージェントに委譲する**（レビューは `code-reviewer` ＋ `security-checker` を**並列**）。
5. **`/cross-review`（Codex）は各タスク完了時に必須**（★ 差分が大きいと fail-closed するので
   `run-codex-review.sh <range> -- <paths>` で絞る）。
6. ⚠️ **テストは `src-tauri/` から**、★ **`--features package` を付けて**実行する。
7. ⚠️ Hook は bash 前提。Windows では **git-bash**。
8. ⚠️★★ **「緑だから正しい」と書かない。** ★ 検査を壊して赤になることを確かめる。
