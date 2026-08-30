# 次セッション開始プロンプト — **O1 のリリースを切って配布物を作り直す**

> ★ このファイルの「===」以下をコピペして開始する。
> ⚠️ **macOS 実機で始めること**（★ 通し確認まで進むため）。
> ⚠️ 前セッションから `/clear` して**新セッション**で始めること。
> ★ モデル: **Sonnet** で足りる（⚠️ secret ローテートの可否判断が絡むときは Opus）。

---

===

## §0 ⚠️★★★ 最初に固定すること

### 0-1. ★ 前セッション (2026-08-30) で何が分かったか

> ⚠️★★★ **`v0.1.29` で作った O1 の配布物は「O1 を知らないビルド」だった。**
> ★ 引き継ぎメモ (`next-session-prompt-o1-macos-distribution.md`) の
> 「最新タグ `v0.1.29` を使え」は、**タグの新しさだけを見て機能の有無を見ていなかった**。

実測（★ 自分でも確かめ直すこと）:

| 検査 | 当時の結果 |
|---|---|
| `git ls-tree v0.1.29 src-tauri/src/o1.rs` | ⚠️ **空**（O1 実装は 08-27 の `7a062cc`） |
| `git tag --contains 7a062cc` | ⚠️ **空** ＝ O1 を含むリリースが 1 つも無い |
| 配布バイナリの `strings` | `o1.mode` **0** / `gse_o1_` **0** / `--o1` **0** |
| 起動して実測 | ファイル名が `gse_*`／⚠️ **`Probe scheduler thread started`**（ランダムプローブ復活） |

⚠️ **署名も実行ビットも `o1.mode` も正常**で、配布物としては完全に正常に見えた。
→ ★ **ゲート化済み**なので、いまは同じ物を作ろうとすると止まる:

```
[make-common-app-zip] ✗ ★ v0.1.29 に src-tauri/src/o1.rs がありません = **O1 を知らないビルド**です。
```

### 0-2. ★ 機械が状態を持っている（⚠️ この数字も「書かれた時点の値」）

```bash
bash scripts/check-o1-release-readiness.sh            # ★ 通過 17 / 未達 2
bash scripts/check-o1-release-readiness.sh --selftest # ★ 43 / 0
bash scripts/check-shell-portability.sh               # ★ 7 / 0（走査 58 本）
bash scripts/sync_session_o1_guard_test.sh            # ★ 13 / 0（⚠️ Desktop 5.1 未検証）
bash experiments/20260801-controlled-friction-task/make-common-app-zip.sh --selftest    # ★ 19 / 0
bash experiments/20260801-controlled-friction-task/初回セットアップ_mac.sh --selftest   # ★ 12 項目
```

⚠️★★ **未達 2 件は「直せなかった」のではなく「この順でしか消せない」**:

1. ⚠️ O1 実装を含むリリースタグが無い → **§1 でこれを解消する**
2. ⚠️ 送信 timeout が未実測 → ★ **1 の後でないと実施しても意味が無い**
   （`gse-submit` に `--o1` が無く、O1 の規則で包むこと自体ができない）

⚠️ `README` / `docs` / 本メモを一次資料にしない。★ 実体とゲートで確かめる。

### 0-3. ✅ 前セッションで済んでいること（★ 作り直さない）

| 何 | 状態 |
|---|---|
| PR #130 | ⚠️ **状態を確認すること**（マージ済みか / CI が緑か） |
| `初回セットアップ_mac.sh` のマーカー決め打ち | ✅ 修正済み（O1 で `OK:` を実機確認） |
| ゲートを「実体に対して」回す | ✅ 追加済み（陽性対照つき） |
| O1 実装の有無を検査（タグ＋実体） | ✅ 追加済み（macOS / Windows 両方） |
| 移植性ゲートの非 ASCII 無言除外 | ✅ 修正済み（56 → 58 本） |
| 実 secret の散文混入検査 | ✅ 追加済み |
| 権限ゲート | ✅ `deny` は `chmod -R` / `sudo` のみ。`rm -rf` 等は `ask`。`git`/`gh` は allow |

---

## §1 ★ やること

### A. ⚠️★★★ **新しいタグを切る**（★ これが全ての前提）

1. PR #130 を main へマージする（⚠️ CI が緑であること）
2. バージョンを上げる。⚠️ **3 ファイル同時**（★ 片方だけだと dmg 名がずれる）:

```
package.json                 "version": "0.1.29"  →  "0.1.30"
src-tauri/tauri.conf.json    "version": "0.1.29"  →  "0.1.30"
src-tauri/Cargo.toml         version = "0.1.29"   →  version = "0.1.30"
```
   ★ `Cargo.lock` も更新される（`cargo check` を 1 回回す）。
3. タグを切って push:

```bash
git tag v0.1.30 && git push origin v0.1.30
```

> ★ **CI の実測（2026-08-30）**:
> - `build-macos` は `runs-on: [self-hosted, gse-mac]` = **この MacBook Air**（当時 online）
> - `build-windows` はタグ時 `windows-latest`（GitHub hosted）
> - runner 一覧: `macbook-air-m-arm64` / `g-gear-win-x64` がどちらも **online** だった
> - ⚠️ 直近 run は全部 success ＝ ★ memory の「private だと即 fail」は**当時起きていなかった**
>   （`build-ci-and-pilot-distribution`。★ 分数が尽きたら一時 public 化の運用がある）

4. ⚠️ **release 資産に dmg と exe が揃ったことを確かめる**:

```bash
gh release view v0.1.30 --json assets -q '.assets[].name'
```

⚠️★★ **dmg は `aarch64` のみ**である。→ ⚠️ **Intel Mac の被験者には配れるものが無い。**
★ 対象者に Intel Mac がいるなら (a) universal / x86_64 を足す (b) Windows で参加してもらう
—— の**どちらかを研究者が決める**（★ 前セッションから継続の未決事項）。

### B. ⚠️★★ `SHARED_SECRET` をローテートする（★ やるなら A と同時が最も安い）

> ★ **いまローテートするコストは実質ゼロ**である:
> O1 を含むリリースが無かったので、⚠️ **被験者の手元に有効な secret を持つ配布物が 1 つも無い**。
> ★ あとからだと全被験者の差し替えになる。

**⚠️ ローテートの理由（★ 研究者が判断する材料。強制ではない）**:
- ⚠️ 配布フォルダに `o1_submit.json` が **`anyone` 公開で生置き**されている（★ 研究者が意図して置いたもの）
- ⚠️ 2026-08-30 に **dev が `.steering/` に実 secret の先頭 45 文字を貼った**
  （未追跡のうちに削除・履歴未混入を確認済み。★ ゲート化済み）
- ★ 現行値は低エントロピーの手打ち文字列（60 文字）

**実害の範囲（★ `GSE_O1_Submit.gs` を読んで確定済み・推測ではない）**:
- ⚠️ **読み出しは不可能**（`doGet` は `use POST` を返すだけ。`doPost` は Drive から読まない。
  `saveWithoutOverwriting_` が上書きを構造的に禁止）→ ★ **被験者への約束は破られていない**
- ⚠️★★★ **書き込みは完全にできる**（`secretMatches_` は共有シークレット一致のみで認可）:
  - ★ **データ捏造** — `pubkey.txt` は配布物に同梱＝公開情報。任意の NDJSON を暗号化して
    通る名前で POST でき、⚠️ **研究者が復号でき、被験者に帰属して見える偽データ**が着地する
  - ★ **可用性** — 1 POST 48 MB。反復でクォータを枯渇させると「その日は永久に届かない」

**手順**（⚠️ 2 か所を**同時に**変える。片方だけだと送信が全部落ちる）:

| どこ | 何 |
|---|---|
| 受信側 | Apps Script `GSE_O1_Submit` の**スクリプト プロパティ** `SHARED_SECRET` |
| 送信側 | ローカル `Form_O1/o1_submit.json` の `secret`（⚠️ `.gitignore:100` 済み） |

```bash
openssl rand -base64 32     # ★ 新しい値を作る（⚠️ 手打ちの文字列にしない）
```

★ 変えたら `checkSubmitConfig()` を回して緑を確かめる。

### C. ★ 配布物を作り直す

```bash
cd experiments/20260801-controlled-friction-task
./make-common-app-zip.sh --mode o1 --tag v0.1.30 --config ../../Form_O1/o1_submit.json
```

⚠️★ **`--config` を省略できない**（★ 省略すると die する。既定は G1 の設定で、
黙って G1 の受け口へ飛ぶ配布物ができるため）。

★ 通れば次が機械で保証される（⚠️ 前回はここが 1 つも無かった）:
- タグに `o1.rs` がある / 実体に `o1.mode`・`gse_o1_`・`GSE_O1_MODE`・`--o1` がある（両 OS）
- **配布物そのもの**で初回セットアップが `OK:`（★ O1 の文言で）
- `o1.mode` あり・`g1.mode` なし / 署名 / 実行ビット / README 文言 / `__MACOSX` 不在

⚠️ 作ったら **G1 の zip が作り直されていないこと**をタイムスタンプで確認する。

### D. ★ macOS 実機での通し確認（⚠️ 前回ここで止まった）

★ **配布物そのものから**始める（⚠️ `cargo run` で代用しない）。

1. zip を展開してデスクトップへ
2. README 【1】どおりに初回セットアップ → ★ **`OK: 準備できました（O1 モード）…`** が出るか
3. `gse-next.app` をダブルクリック
   - ⚠️ TCC は前回**既に許可済み**だった（`input_monitoring=true accessibility=true`）
   - ★ 新しいバイナリなので**再度求められる可能性がある**。どちらを許可したか記録する
4. ⚠️★★★ **O1 モードで動いているか実体で確かめる**:
   - ★ ファイル名が **`gse_o1_*`**（⚠️ 前回はここが `gse_*` だった）
   - ⚠️ `gse-app.log` に **`Probe scheduler thread started` が出ていない**こと
   - ★ 画面のすみに **「記録中 · 作業の種類: …」**（`RecordingControls.tsx`）
   - ★ 「開始する」を押していないのに `key` 行が出る
   - ⚠️ `intervention_enabled` が false
5. ★ 宣言 4 択を選び直す → ローテートして新ファイルに `session_meta` が入るか
6. ★ 「すぐ止める」→ `recording_pause` が出て、止めているあいだ `feat` 行が 0 になるか
7. ⚠️★★★ **「この時間帯の記録を消す」**（★ 全 OS を通じて**いまだ未実施**）
   - ⚠️ **一時停止 → 削除**の順で操作する
   - ★ E-1 の不具合（削除後の案内が O1 で逆を指す）が踏めるのはここ
   - ★ `redaction_ledger.jsonl` が生成されるか
8. ★ 自動起動の登録（README 【3】）→ ⚠️ 再起動して**本当に自動で立ち上がるか**まで見る

### E. ⚠️★★★ 送信 timeout の実測（★ ゲート最後の赤）

1. ★ 48 時間の猶予: 送信されないことを確かめる（⚠️ `packaged:0` / `upload_disabled`）
2. ⚠️ **1 日ぶんの実サイズで通し確認**（`GSE_O1_Submit.gs` 配備手順 8）
3. ⚠️ 実測なしに `reconcile.rs` の `from_secs(180)` を書き換えない
   （★ ゲートは記録票とコードの**両方**を要求するので、数字だけ変えても緑にならない）

### F. ★ 配布フォルダを整える（⚠️ 受付メールは既にこの URL を案内している）

⚠️★★ **現状 zip が 1 本も入っていない**（実測 2026-08-30）。中身は `o1_submit.json` 1 件だけ。
→ ★ 登録した被験者は **P-ID だけ受け取ってアプリを入手できない**。

- フォルダ: `GSE_ユーザー検証_O1_アプリダウンロードリンク`
  (`1ovS4L7mAETukMAYxuO7nZkNznFAXILob`・共有 = `anyone` / reader)
- ★ zip 2 本を置く → ⚠️ **実際にリンクを開いて 2 本見えることを確かめる**
- ⚠️ `o1_submit.json` を残すかは研究者判断（★ 端末側は `g1-submit.json` を読むので**機能上は不要**）

### G. ★ README の文言を実機に合わせる（⚠️ 承認が要る）

⚠️★★ `dist-readme-macos-o1.txt` の手順は、⚠️ **【1】の Gatekeeper だけまだ 1 度も踏まれていない**
（★ ローカル展開では `com.apple.quarantine` が付かない。→ **Drive から実際に落として**確かめる）。

- 【1】Gatekeeper のダイアログ文言（★ 現行は B 型「壊れているため開けません」を前提）
- 【3】「システム設定 → 一般 → ログイン項目と機能拡張」（⚠️ macOS の版で表示が変わる）

★ 承認できたら:
1. 両 README の 1 行目 `【ドラフト・未承認】` を消す
2. `make-common-app-zip.sh --selftest` の「ドラフト表示の検査」を外す
3. ⚠️ `--selftest` を回して **1 件減る**ことを確かめる

---

## §2 ⚠️ 積み残し（★ 本セッションの主題ではないが忘れない）

| # | 何 | いつ |
|---|---|---|
| 1 | ⚠️ `sync-session.ps1` の O1 ガードを **Windows PowerShell 5.1 (Desktop)** で検証 | ★ Windows 作業のついでに `bash scripts/sync_session_o1_guard_test.sh` |
| 2 | ⚠️ `sync-all.sh` が **ガードより前に O1 の生 NDJSON を作業ツリーへコピー**する | ★ `.ps1` と対で直す（Windows で検証できるとき） |
| 3 | ⚠️ Intel Mac の被験者への対応（universal ビルド or Windows 参加） | ★ 対象者が確定したら |
| 4 | ⚠️ `/cross-review` の Codex が **secrets-filter で自己ブロック**する | ★ 目視同意のうえ `--ack-filtered` で再実行できる |
| 5 | ⚠️ G1 の配布フォルダに裸の `g1-submit.json` が無いか（Drive 側は未確認） | ★ 見るだけ（G1 は実施中でローテートは高コスト） |

---

## §3 ★ 完了報告に必ず書くこと

- [ ] ★ 使った**タグ名**（⚠️ 既定の `v0.1.24` を使っていないこと）と release 資産の一覧
- [ ] ★ `--mode o1` の**実行結果を貼る**（⚠️ 新ゲートが全部通ったか）
- [ ] ⚠️ `SHARED_SECRET` をローテートしたか。★ したなら**受信側と送信側の両方**を変えたか
- [ ] ★ §1-D で **どこまで実際に操作したか**（⚠️ 「動くはず」と書かない）
- [ ] ⚠️★★★ **D-7（この時間帯の記録を消す）を実施したか**。★ 未実施ならそう書く
- [ ] ⚠️ **Gatekeeper ダイアログを再現したか**（★ Drive から落としたか）
- [ ] ★ README を直したなら、**検査語も直したか**
- [ ] ⚠️ **外界に触った操作**（Drive への配置 / 送信 / デプロイ / タグ push）を列挙する
- [ ] ★ `bash scripts/check-o1-release-readiness.sh` の結果（通過 N / 未達 M）

---

## ⚠️★★★ 本セッションの作業規約（★ CLAUDE.md より抜粋・省略しない）

1. **`.steering/[YYYYMMDD]-[task-name]/`** に `requirement.md` / `design.md` / `tasklist.md` を必ず作る。
2. **必須 Skill を読んでから手を動かす**:
   - ★ `verify-before-claiming` —— **事実を断定する前**（「動くはず」「不要」「壊れる」）
   - `hook-constraints` / `data-privacy` / `git-workflow`
3. **サブエージェントに委譲する**: レビュー=`code-reviewer` ＋ `security-checker` を**並列**。
4. **`/cross-review`（Codex）は各タスク完了時に必須。** ⚠️ ブロックされたら skip 理由を明記。
5. ⚠️ **テストは `src-tauri/` から実行する**（★ repo 直下に `Cargo.toml` は無い）。
6. ⚠️★★ **「緑だから正しい」と書かない。** ★ 実機で操作していないことを操作したと書かない。

> ⚠️★★★ **前セッションの教訓（★ これが本メモの核心）**:
> 「ゲートが全部緑」は「配布物が動く」を意味しない。
> ★ 検査が **自前 fixture の中でだけ緑**になっていないかを、常に疑うこと。
> ⚠️ **対照値を検査対象の中に書くと自己参照で空回りする**（★ 前回 2 回踏んだ）。
