# 次セッション開始プロンプト — **v0.1.31 を切って配布物を差し替え、送信 timeout を決める**

> ★ このファイルの「===」以下をコピペして開始する。
> ⚠️ **macOS 実機で始めること**（★ Gatekeeper と自動起動の確認が残っている）。
> ⚠️ 前セッションから `/clear` して**新セッション**で始めること。
> ★ モデル: **Sonnet** で足りる（⚠️ §2 の timeout は設計判断なので **Opus** 推奨）。

---

===

## §0 ⚠️★★★ 最初に固定すること

### 0-1. ⚠️ このメモを一次資料にしない

★ 前セッション（2026-08-30）は、引き継ぎメモの記述を**4 か所で訂正**した。
⚠️ **このメモも同じ確率で間違っている。** 数字と手順は**必ず自分で確かめ直す**。

★ 前回訂正した 4 件（★ 同じ轍を踏まないための実例）:

| # | メモの記述 | ⚠️ 実体 |
|---|---|---|
| 1 | 「`Cargo.lock` に `0.1.29` が **2 箇所**」 | ★ 2 件目は無関係な第三者クレート **`schannel`** の同名バージョン。⚠️ 両方置換したら lock が壊れる |
| 2 | 「`Probe scheduler thread started` が**出ていない**こと」 | ⚠️ **O1 でも必ず出る**。正しい条件は「NDJSON に `probe_assignment` **型**の行が 0」 |
| 3 | 「制約は 2 つ（`MAX_BYTES` と timeout）」 | ⚠️ **3 つ**。Apps Script の実行時間上限 **6 分 = 360 秒**（★ Google 公式クォータ・repo 内に記述 0 件） |
| 4 | 「D-7 は**一時停止 → 削除**の順」 | ⚠️★★★ **O1 では逆**。止めるとローテートできず**必ず失敗する**。★ 実際に 2 回踏んだ |

### 0-2. ★ 現状（⚠️ この表も「書かれた時点の値」）

```bash
git log --oneline -3                                    # ★ main の位置を確認
gh pr view 132 --json state,mergeStateStatus            # ★ マージ済みか / CI が緑か
gh release view v0.1.30 --json assets -q '.assets[].name'
bash scripts/check-o1-release-readiness.sh              # ★ 前回 18 / 1
git tag --contains 7a062cc                              # ★ v0.1.30 が返るはず
```

### 0-3. ✅ 前セッションで済んでいること（★ 作り直さない）

| 何 | 状態 |
|---|---|
| タグ `v0.1.30` | ✅ O1 実装を含む**初**のリリース。dmg (aarch64) / exe / tools が揃っている |
| 配布物 `O1_実施用_{macOS,Windows}.zip` | ✅ 新ゲート全通過。★ 実体を `strings` で自己検算済み（`o1.mode`=5 / `gse_o1_`=1 / `--o1`=3。⚠️ 前回は全部 0 だった） |
| Drive 配置 | ✅ 2 本とも `fileSize` 一致を API で照合。★ 旧 `o1_submit.json`（旧 secret・`anyone`）も削除済み |
| `SHARED_SECRET` | ✅ **両側**ローテート済み（送信側=Claude / 受信側=研究者・`checkSubmitConfig()` 緑） |
| §1-D 通し確認 | ✅ **D-7（削除）まで成功**。⚠️ 残るは**自動起動**のみ（下記 §1-C） |
| UI 欠陥 3 件 ＋ 0600 欠陥 ＋ 削除 UI 改善 | ✅ 修正済み・**PR #132**（⚠️ 状態を確認すること） |

⚠️ **G1 の zip は触っていない**（mtime / sha256 とも不変を確認済み）。★ 今後も触らないこと。

---

## §1 ★ やること（★ この順で）

### A. ⚠️★★★ PR #132 をマージして **v0.1.31** を切る

1. `gh pr checks 132` が緑であることを確認 → マージ
2. バージョンを上げる。⚠️ **`cargo check` まで含めて 4 か所**:

```
package.json                 "version": "0.1.30" → "0.1.31"
src-tauri/tauri.conf.json    "version": "0.1.30" → "0.1.31"
src-tauri/Cargo.toml         version = "0.1.30"  → version = "0.1.31"
src-tauri/Cargo.lock         ★ cargo check が gse-next の 1 行だけ追随する
```

⚠️★ **走査して「直すもの / 残すもの」を目で分けること**:

```bash
git ls-files -z | xargs -0 grep -nF "0.1.30" | grep -v '^\.steering/' | grep -v '^docs/'
```

★ `make-common-app-zip.sh` / `check-o1-release-readiness.sh` に出る**過去バージョンは
事故の記録としてのコメント**なので**書き換えない**（★ 履歴が消える）。

3. タグを切って push → CI 完走を待つ（★ 前回 `build-macos` は self-hosted の順番待ちで
   合計 40 分ほどかかった）

```bash
git tag v0.1.31 && git push origin v0.1.31
gh release view v0.1.31 --json assets -q '.assets[].name'   # ★ dmg と exe が揃うこと
```

⚠️ **タグ push では `check` / `frontend-check` が走らない**（`if` がタグを除外している）。
→ ★ **テストは PR の段階で緑にしておくこと。**

### B. ★ 配布物を作り直して Drive を差し替える

```bash
cd experiments/20260801-controlled-friction-task
./make-common-app-zip.sh --mode o1 --tag v0.1.31 --config ../../Form_O1/o1_submit.json
```

⚠️ `--config` は省略不可（★ 既定は G1 の設定なので、黙って G1 の受け口へ飛ぶ配布物ができる）。
⚠️ 作ったら **G1 の zip が作り直されていないこと**を mtime ＋ sha256 で確認する。

★ **⚠️ ゲートを鵜呑みにせず、実体を自分で検算する**（★ 前回これで前々回の事故が見えた）:

```bash
unzip -q O1_実施用_macOS.zip -d /tmp/verify && cd /tmp/verify
BIN=$(find . -name gse-next -path '*MacOS*'); for p in o1.mode gse_o1_ GSE_O1_MODE; do
  printf '%-14s %s\n' "$p" "$(strings "$BIN" | grep -c -- "$p")"; done
printf '%-14s %s\n' gse_next_lib "$(strings "$BIN" | grep -c gse_next_lib)"   # ★ 陽性対照
```

**Drive 差し替え**（★ 研究者が D&D。⚠️ Claude はアップロードできない）:

- フォルダ `GSE_ユーザー検証_O1_アプリダウンロードリンク` (`1ovS4L7mAETukMAYxuO7nZkNznFAXILob`)
- ⚠️ **古い zip を先に消す**（★ 同名でも別ファイルとして 2 本並ぶ）
- ★ 置いたら Drive API で `fileSize` を照合する（`mcp__claude_ai_Google_Drive__search_files` で
  `parentId = '1ovS4L7mAETukMAYxuO7nZkNznFAXILob'`）

### C. ★ 実機で残りを確認する（⚠️ 配布物そのものから）

★ **§1-D で残っているのは 1 つだけ**:

- [ ] **自動起動の登録**（README 【3】）→ ⚠️ **再起動して本当に自動で立ち上がるか**まで見る

★ v0.1.31 の配布物で、修正した 3 点が**画面から消えていること**も目視する:

- [ ] 「較正モード」→ **「記録のみ」**になり、「画面の問いに回答してください」が**出ない**
- [ ] 「🔴 今とても詰まっている」が**出ない**
- [ ] 「セッション終了」が**出ない**（★ 終了はトレイの「GSE を終了」から）
- [ ] 削除パネルを開くと、**失敗する前に**「★ 記録を止めずに、このまま消せます」が出る

⚠️★★ **機械検査はこれらを 1 つも捕まえない。** ★ 画面を見ること
（memory `ui-changes-need-eyes`）。

### D. ⚠️ README の承認（★ ここが `--selftest` の最後の 1 件）

⚠️★★ **【1】の Gatekeeper だけ、まだ 1 度も踏まれていない。**
★ ローカル展開では `com.apple.quarantine` が付かないため、**Drive から実際に落とす**必要がある。

1. Drive の `O1_実施用_macOS.zip` を **ブラウザで**ダウンロード → 展開 → `gse-next.app` をダブルクリック
2. 出たダイアログの文言を確認する
   - ★ 現行 README は **B 型「"gse-next" は壊れているため開けません」**を前提にしている
   - ⚠️ A 型（「開発元を確認できないため開けません」）だったら README を直す
3. 【3】「システム設定 → 一般 → **ログイン項目と機能拡張**」が、この macOS の版の表記と合っているか

★ 承認できたら（⚠️ **3 つを同じコミットで**）:

```
1. dist-readme-macos-o1.txt / dist-readme-windows-o1.txt の 1 行目「【ドラフト・未承認】」を消す
2. make-common-app-zip.sh --selftest の「ドラフト表示の検査」を外す
3. --selftest を回して 19 件 → 18 件に減ることを確認（★ 検査語の消し忘れの対照）
```

⚠️★ **README を直したら zip を作り直す**（★ README は zip に焼き込まれている）。
→ ⚠️ **B と D は同じ 1 回のビルドにまとめること**（★ Drive 差し替えを 2 回やらない）。

---

## §2 ⚠️★★★ 送信 timeout（★ ゲート最後の赤・要 Opus）

### 2-1. ★ ブロックは外れている

⚠️ 前回まで「`SHARED_SECRET` 未更新」で実施できなかったが、**2026-08-30 に両側そろった**。
→ ★ **いつでも測れる。**

### 2-2. ⚠️★★★ 測る前に読むこと —— **制約は 3 つある**

| # | 制約 | 値 | 出所 |
|---|---|---|---|
| 1 | 受け口の本文上限 | 48 MB（base64 64 MB） | `Form_O1/GSE_O1_Submit.gs:151` |
| 2 | 送信側 timeout | **180 秒固定** | `src-tauri/src/reconcile.rs:697`（`HttpUploader::new`） |
| 3 | ⚠️★★★ **Apps Script の実行時間上限** | **6 分 = 360 秒 / 実行** | Google 公式クォータ（★ repo 内に記述 **0 件**・2026-08-30 に確認） |

★ **3 が効くと「待つ時間を伸ばす」は解にならない。**
⚠️ `doPost` は base64 デコード（48MB）＋ `DriveApp` 保存を行い、それは 360 秒に算入される。
→ ⚠️ クライアント側を 900 秒にしても、**サーバが 360 秒で殺されるなら届かない**。

⚠️ ★ **未確認**: 転送時間そのものが 360 秒に算入されるか（★ 公式表からは決まらない）。
→ **実測でしか決まらない。**

### 2-3. ★ 圧縮が無いので **24 時間待つ必要は無い**（★ 自分でも確かめ直すこと）

```bash
grep -nE "flate2|zstd|gzip|brotli|deflate" src-tauri/Cargo.toml   # ★ 0 件
grep -rniE "compress|flate2|zstd" src-tauri/src/bin/package.rs    # ★ 0 件（91 行）
```

★ パイプラインに圧縮が無い＝**バイト数がそのまま転送量**。
→ ⚠️ 既存 NDJSON を連結して 18MB にすれば、**転送時間の測定として等価**である。

⚠️★ **何にパイロットが要り、何に要らないか**:

| | パイロット |
|---|---|
| 24MB が N 秒で送り切れるか | ❌ 不要（合成で可） |
| 上限 48MB でも通るか | ❌ 不要（★ むしろ合成でしか作れない） |
| ⚠️ **1 日ぶんのサイズの分布** | ✅ 要る（★ 18MB は **n=1** の外挿） |
| ⚠️ **被験者側の回線** | ✅ 要る（★ timeout は**被験者の端末**で効く） |

### 2-4. ⚠️ 案の比較（★ `.steering/20260830-o1-release-and-rebuild/decisions.md` D-3 に表がある）

| | A: 固定値を大きく | B: サイズ比例＋下限/上限 | C: 運ぶ量を小さく |
|---|---|---|---|
| `MAX_BYTES` 追従 | ❌ | ✅ | ✅ |
| ⚠️ **サーバ 360 秒への対処** | ❌ **できない** | △ 上限を 360 秒側に置ける | ✅ **本質的に対処** |
| コスト | 最小 | 小（`RequestBuilder::timeout` で可） | ⚠️ 中〜大（ADR に触る） |

★ 現時点の推奨は **B を土台に、上限を 3 から導く**。⚠️ ただし **C を捨てない**。
⚠️ これは**設計変更**なので、`/reimagine` で案を比較してから実装すること。

### 2-5. ★ ゲートが緑になる条件（⚠️ **両方**が要る）

1. `experiments/20260801-controlled-friction-task/o1-upload-timeout-measurement.md` の
   `<!-- gate:o1-upload-timeout -->` 直後のブロックで:
   - `- 状態: **実測済み**`
   - 実測日 / 送信バイト数(base64後) / 所要時間(Drive保存を含む) / 実効スループット / 採用した timeout
   - ⚠️ **すべて数字を 1 つ以上含むこと**
2. `src-tauri/src/reconcile.rs` から **`from_secs(180)` が消えている**

⚠️★★★ **数字を書き換えるだけで緑にしない。** ★ ゲート自身がそう書いている。

⚠️ ★ `.idea/issue.md` に手順書があるが（`.gitignore:58`・repo に入らない）、
**期待値「17/0」は古い**。★ 正しくは検査項目が増えているので、走らせて実数を見ること。

---

## §3 ⚠️ 積み残し（★ 別タスクで起こす）

★ 詳細は `.steering/20260830-o1-release-and-rebuild/followups.md`。

| # | 何 | 重さ |
|---|---|---|
| 1 | ⚠️★★ **O1 運用管理シートの実装** —— 器は存在するが**中身が空**。`O1_MGMT_SHEET_ID` の実装がゼロ（★ 研究者判断 2026-08-30 で別タスク化）。ID = `1zmZvuuGUpOwv-xQg_H9zwKJNR0Ow9oaYNEUJf0j61Jw`。⚠️ `PHASE1_MGMT_SHEET_ID` を**転用しない**（★ 2 か所採番になる） | 中 |
| 2 | ⚠️★★ **キーボードフックの飢餓** —— 35 分で **13 回**発生（★ 1 回は `starved_ms=120340`）。打鍵自体は 1794 行記録できていたが、⚠️ 被験者環境で頻発すると欠測になる。★ memory `macos-tap-idle-away-probe-bug` と同型か | 中 |
| 3 | ⚠️ **プローブ抑止ゲートに O1 が入っていない**（`lib.rs:4419` の `disabled_by_g1 = g1_mode()`）。★ 現状は `start_session` が呼ばれないことに依存した**偶然の防御**で、⚠️ 番兵 warn も O1 では出ない | 小 |
| 4 | ⚠️ **`SHARED_SECRET` の残余リスク** —— secret は zip に焼き込まれ、その zip は `anyone` 公開に置かれる。★ **「被験者から隠す秘密」ではない**。構造的に直すには参加者ごとの資格情報が要る | 要判断 |
| 5 | ⚠️ Intel Mac の被験者（★ 2026-08-30 に**保留**と判断・対象者確定後） | 保留 |
| 6 | ⚠️ `sync-session.ps1` の O1 ガードを **Windows PowerShell 5.1** で検証 | 小 |
| 7 | ⚠️ `sync-all.sh` がガードより前に O1 の生 NDJSON を作業ツリーへコピーする | 小 |
| 8 | ⚠️ `/cross-review` の Codex が secrets-filter で自己ブロックする（★ `--ack-filtered` で再実行可） | 小 |

---

## §4 ★ 完了報告に必ず書くこと

- [ ] 使ったタグ名と release 資産の一覧
- [ ] `--mode o1` の**実行結果を貼る**（★ 新ゲートが全部通ったか）
- [ ] ⚠️ 配布物の実体を**自分で検算した数値**（★ ゲートの緑を根拠にしない）
- [ ] Drive を差し替えたか。★ **古い zip を消したか**
- [ ] ⚠️ **自動起動を再起動まで確認したか**（★ 未実施ならそう書く）
- [ ] ⚠️ **Gatekeeper のダイアログを実際に踏んだか**（★ Drive から落としたか）／文言は A 型か B 型か
- [ ] README を直したなら、**検査語も直したか**・`--selftest` が 1 件減ったか
- [ ] ⚠️ 修正した UI 3 件が**画面から消えていることを目視したか**
- [ ] ⚠️ **外界に触った操作**（Drive / 送信 / デプロイ / タグ push）を列挙する
- [ ] `bash scripts/check-o1-release-readiness.sh` の結果（通過 N / 未達 M）

---

## ⚠️★★★ 本セッションの作業規約（★ CLAUDE.md より・省略しない）

1. **`.steering/[YYYYMMDD]-[task-name]/`** に `requirement.md` / `design.md` / `tasklist.md` を必ず作る。
2. **必須 Skill を読んでから手を動かす**: ★ `verify-before-claiming` ／ `data-privacy` ／
   `hook-constraints` ／ `git-workflow`。⚠️ ブラウザを使うなら `browser-verification`。
3. **サブエージェントに委譲する**: レビュー = `code-reviewer` ＋ `security-checker` を**並列**。
4. **`/cross-review`（Codex）は各タスク完了時に必須。** ⚠️ ブロックされたら skip 理由を明記。
5. ⚠️ **テストは `src-tauri/` から実行する**（★ repo 直下に `Cargo.toml` は無い）。
6. ⚠️★★ **「緑だから正しい」と書かない。** 実機で操作していないことを操作したと書かない。

> ⚠️★★★ **前セッションの教訓（★ これが本メモの核心）**:
>
> **機械検査が全部緑でも、画面を見るまで何も分からない。**
> ★ 2026-08-30 に見つけた 5 件（UI 欠陥 3 / 0600 の欠落 / 削除 UI の案内）は、
> ⚠️ **配布ゲート 19/19・`--selftest` 19/0 が緑のまま素通りしていた**。
> 見つかったのは、研究者がスクリーンショットを撮り、実際にボタンを押したからである。
>
> ★ そして **`ls -l` の 1 行**（`-rw-r--r--`）が、
> 同意文書 §7 の削除機能がプライバシーを緩めていたことを暴いた。
> ⚠️ **対照を並べて見ること。** 1 つのファイルだけ見ていたら気づかなかった。
