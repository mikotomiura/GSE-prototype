# 次セッション開始プロンプト — **macOS 実機での O1 配布物と通し確認**

> ★ このファイルの「===」以下をコピペして開始する。
> ⚠️ **macOS 実機で始めること。** ★ Windows では 1 行も検算できない。
> ⚠️ 前セッションから `/clear` して**新セッション**で始めること。
> ★ モデル: **Sonnet** で足りる（⚠️ ただし README 文面の承認が絡むときは Opus）。

---

===

## §0 ⚠️★★★ 最初に固定すること

### 0-1. ★ 機械が状態を持っている

```bash
bash scripts/check-o1-release-readiness.sh            # ★ 通過 12 / 未達 2 のはず
bash experiments/20260801-controlled-friction-task/make-common-app-zip.sh --selftest   # ★ 14/14
```

⚠️ `README` / `docs` / 本メモを一次資料にしない。★ 実体とゲートで確かめる。

### 0-2. ⚠️★★★ **このセッションの前提と依存**

★ `make-common-app-zip.sh` は**冒頭で送信先の設定を検証して止まる**（実測・`:80-92`）:

```
endpoint が https://script.google.com/macros/s/ で始まり /exec で終わること
secret が 24 文字以上あること
```

→ ⚠️★★★ **本番の配布物は「受け口のデプロイ (B-1)」が終わるまで作れない。**
（★ B-1 は `next-session-prompt-o1-gate-closeout-and-deployment.md` §1-B-1）

★ **ただし「macOS で動くか」の検算だけなら、いま進められる**（→ §1-C）。
⚠️ その zip は**絶対に配らない**。

### 0-3. ✅ **前セッションで済んでいること**（★ 作り直さない）

| 何 | 状態 |
|---|---|
| `make-common-app-zip.sh --mode g1\|o1` | ✅ 実装済み。⚠️ **既定 g1 の経路は不変** |
| O1 用 README 2 本 | ✅ ある。⚠️ **`【ドラフト・未承認】`**（★ 承認は別途） |
| `launch-o1-windows.bat` | ✅ ある（★ macOS では使わない） |
| モード分岐・README 文言の検査 | ✅ `--selftest` **14/14** |
| ⚠️ **macOS 実機での実行** | ⚠️★★★ **1 度も走らせていない**（★ 本セッションの主題） |

---

## §1 ★ やること

### A. ★ 前提コマンドと素材の確認（⚠️ 足りないまま進めない）

```bash
for c in ditto hdiutil codesign zip python3 gh git; do
  printf '%-10s ' "$c"; command -v "$c" || echo "❌ 無い"
done
```

★ `gh` は `gh auth status` も見る（⚠️ リリース資産の取得に要る）。

### B. ⚠️★★★ **`--tag` を必ず明示する**（★ 既定が古い）

⚠️ **実測（2026-08-28）**:

- `make-common-app-zip.sh` の既定 `TAG="v0.1.24"`
- ★ 実在する最新タグは **`v0.1.29`**、その release 資産に
  **`gse-next_0.1.29_aarch64.dmg`** がある

→ ★ **O1 では `--tag v0.1.29`（またはそのとき最新のタグ）を明示的に渡す。**

> ⚠️★★★ **既定値 `v0.1.24` を書き換えないこと。**
> ★ G1 は**実施中**であり、既定を変えると **G1 の配布物のビルドが黙って変わる**。
> ★ 変えるなら G1 の実施が切れたときに、`.steering` に根拠を残して行う。

⚠️★★ **dmg は `aarch64` のみ**である（★ 上の資産名）。
→ ⚠️ **Intel Mac の被験者には配れるものが無い。**
★ 対象者に Intel Mac がいるなら、(a) universal / x86_64 のビルドを足す
(b) その人は Windows で参加してもらう —— の**どちらかを研究者が決める**（★ 起票）。

### C. ★ **検算ラン**（⚠️ 受け口のデプロイ前でもここまでは進む）

★ 形だけ整えたダミー設定を作る（⚠️ **repo の中に置かない**・`.gitignore` の外に出さない）:

```bash
cat > /tmp/o1-dryrun-submit.json <<'JSON'
{
  "endpoint": "https://script.google.com/macros/s/DRYRUN_NOT_A_REAL_DEPLOYMENT/exec",
  "secret": "dryrun-secret-not-real-000000000000"
}
JSON

cd experiments/20260801-controlled-friction-task
./make-common-app-zip.sh --mode o1 --tag v0.1.29 --config /tmp/o1-dryrun-submit.json
```

★ **これで確かめられること**（⚠️ ここが本セッションの主目的）:

| # | 何 | ★ スクリプトのどこが見るか |
|---|---|---|
| 1 | dmg がマウントでき、`gse-next.app` の**署名が壊れていない** | `codesign --verify --strict` |
| 2 | `.app` をフォルダへ取り出しても**署名が生きている** | 取り出し後にもう一度 verify |
| 3 | zip 化 → 展開後も**実行ビットが落ちない** | `[ -x .../Contents/MacOS/gse-next ]` |
| 4 | ★ **`o1.mode` が入り `g1.mode` が入っていない** | マーカーの排他検査 |
| 5 | `初回セットアップ_mac.sh` が**展開後も自己検査に通る** | `--selftest` を 2 回 |
| 6 | README が**被験者を守る文言**を落としていない | 共通 4 語 ＋ O1 固有 5 語 |
| 7 | ★ **Windows zip の中身**（マーカー / launcher / README / 必須ファイル） | namelist 検査 |
| 8 | `__MACOSX` / `.DS_Store` が混ざっていない | 両 zip |

⚠️★★★ **確かめられないこと**（★ 隠さない）:

- ⚠️ **送信は 1 度もしていない**（★ endpoint がダミー）。★ 転送路の検証は §1-E-4。
- ⚠️ `.app` が**実際に起動するか**は zip 検査では分からない → §1-D。

⚠️ 終わったら `rm -f /tmp/o1-dryrun-submit.json` と `dist/_common/O1_実施用_*` を消す。
★ **ダミー設定の入った zip を Drive に上げない。**

### D. ★ **macOS 実機での通し確認**（⚠️ ここが本命。★ 研究者が操作する）

★ **配布物そのものから**始めること（⚠️ `cargo run` で代用しない。
それでは Gatekeeper もマーカーも検証できない）。

1. `O1_実施用_macOS.zip` を展開し、フォルダをデスクトップへ置く
2. ⚠️ **README の【1】どおりに** 初回セットアップを実行する
   （★ ターミナルに `bash ` と打ち、`初回セットアップ_mac.sh` をドラッグ）
   - ★ 「OK: 準備できました…」が出るか
   - ⚠️ 出ないなら **README の手順が実機と食い違っている**（→ §1-F）
3. `gse-next.app` をダブルクリック
   - ★ **「キーボードの入力の監視」の許可**を求められる → 許可 → 終了 → 再起動
   - ⚠️ ★ **TCC は Input Monitoring → Accessibility のフォールバックがある**。
     どちらを許可したかを記録する（`docs/agent-shared.md` 技術的制約 6）
4. ⚠️★★★ **O1 モードで動いているか**を実体で確かめる:
   - ★ 画面に**記録中の印**が出ている（⚠️ 出ていなければ記録していない）
   - ★ 「開始する」を**押していないのに** `key` 行が出る
   - ★ NDJSON の `meta` 行に `"o1_mode":"marker"` がある（⚠️ `"env"` ではない）
   - ★ ファイル名が `gse_o1_*` になっている
   - ⚠️ **`intervention_enabled` が false**（★ O1 で介入 OFF）
5. ★ **宣言 4 択**を選び直す → ローテートして新ファイルに `session_meta` が入るか
6. ★ **「すぐ止める」** → `recording_pause` が出て、止めているあいだ `feat` 行が 0 になるか
7. ⚠️★★★ **「この時間帯の記録を消す」**（★ 全 OS を通じて**いまだ未実施**）
   - ⚠️ ★ **一時停止 → 削除**の順で操作すること
   - ★ **E-1 の不具合**（削除後の案内が O1 で逆を指す）が踏めるのはここである
     （→ `next-session-prompt-o1-gate-closeout-and-deployment.md` §1-E-1）
   - ★ `redaction_ledger.jsonl` が生成されるかを確認する
8. ★ **自動起動の登録**（README 【3】）
   - ⚠️ システム設定 → 一般 → **ログイン項目と機能拡張** → 「ログイン時に開く」の ＋
   - ⚠️★ **項目名は macOS のバージョンで変わる。** 実機の表示と README を突き合わせる（→ §1-F）
   - ★ 再起動して**本当に自動で立ち上がるか**まで見る（⚠️ 登録できた ≠ 起動する）

### E. ★ 受け口が立ったあとにやること（⚠️ B-1 完了後）

1. 本物の `g1-submit.json`（endpoint ＋ secret）で `--mode o1` を回し直す
2. ★ 展開したフォルダの `g1-submit.json` が**本物**になっていることを目で見る
   （⚠️ ファイル名は `g1-` のままで正しい。★ 中身で行き先が決まる）
3. ★ **48 時間の猶予**の挙動: 送信されないことを確かめる（⚠️ `packaged:0` / `upload_disabled`）
4. ⚠️★★★ **1 日ぶんの実サイズで通し確認**（★ `GSE_O1_Submit.gs` 配備手順 8）
   - ★ これが `A-2 送信 timeout` の**実測**そのものである
   - ⚠️ 実測なしに `reconcile.rs` の `from_secs(180)` を書き換えない
     （★ ゲートは `grep from_secs(180)` なので**数字を変えるだけで緑になる**）

### F. ★ README の文言を実機に合わせる（⚠️ 承認が要る）

⚠️★★ **`dist-readme-macos-o1.txt` の手順は、実機で 1 度も踏まれていない。**
★ とくに次の 2 つは macOS のバージョンで表示が変わる:

- 【1】の Gatekeeper のダイアログ文言（★ 現行は B 型「壊れているため開けません」を前提）
- 【3】の「システム設定 → 一般 → ログイン項目と機能拡張」

→ ★ 食い違ったら **README を実機に合わせて直す**。
⚠️★ そのとき `make-common-app-zip.sh` の検査語も一緒に見ること
（★ `README_MUST_COMMON` / `README_MUST_O1` は配列。⚠️ 文言だけ直すと検査が空振りする）。

★ 承認できたら:
1. 両 README の 1 行目 `【ドラフト・未承認】` を消す
2. `make-common-app-zip.sh --selftest` の項目 8（ドラフト表示の検査）を外す
3. ⚠️ `--selftest` を回して **13/13 になる**ことを確かめる（★ 1 件減る）

---

## §2 ⚠️ 注意（★ macOS 固有）

| # | 何 | ★ 根拠 |
|---|---|---|
| 1 | ⚠️ **macOS の配布物に `pubkey.txt` と `gse-submit` は単体で入らない** | ★ `tauri.conf.json:28` が `resources/pubkey.txt` をバンドルし、macOS バンドラが `--features package` の全 `[[bin]]` を `Contents/MacOS/` へコピーする。→ ★ README の同梱物一覧に書かない（**2026-08-28 に一度書いて直した**） |
| 2 | ⚠️ `analysis/` は OS 非依存だが、**`input/` は実機でしか確かめられない** | `docs/agent-shared.md` テスト方針 |
| 3 | ⚠️ **`hook_windows.rs` は macOS で 1 行もコンパイルされない**。逆に `#[cfg]` の無いテストは相手 OS でも走る | 2026-08-10 に Windows CI が赤くなった実測 |
| 4 | ⚠️ **`dispatch_sync_f` をメインスレッドから呼ばない**（デッドロック） | 技術的制約 5 |
| 5 | ⚠️ Drive はパーミッションを保存しない。★ **zip で配る**理由がこれ | 2026-08-07 実測 |
| 6 | ⚠️ `ditto` の zip は **Windows 向けに使わない**（UTF-8 フラグが立たず日本語名が化ける） | 2026-08-07 実測 |

---

## §3 ★ 完了報告に必ず書くこと

- [ ] ★ `make-common-app-zip.sh --mode o1` の**実行結果を貼る**（⚠️ 検算ランか本番かを明記）
- [ ] ⚠️ **ダミー設定で回したなら、その zip を配っていない**ことを明記する
- [ ] ★ §1-D の通し確認で **どこまで実際に操作したか**（⚠️ 「動くはず」と書かない）
- [ ] ⚠️★★★ **B-4（この時間帯の記録を消す）を実施したか**。★ 未実施ならそう書く
- [ ] ★ README を直したなら、**検査語も直したか**
- [ ] ⚠️ 使った **タグ名**（★ 既定の `v0.1.24` を使っていないこと）
- [ ] ⚠️ **外界に触った操作**（Drive への配置 / 送信 / デプロイ）を列挙する
- [ ] ★ `bash scripts/check-o1-release-readiness.sh` の結果（通過 N / 未達 M）

---

## ⚠️★★★ 本セッションの作業規約（★ CLAUDE.md より抜粋・省略しない）

1. **`.steering/[YYYYMMDD]-[task-name]/`** に `requirement.md` / `design.md` / `tasklist.md` を必ず作る。
   ★ 作成は `/start-task`、最終化は `/finish-task`。
2. **必須 Skill を読んでから手を動かす**:
   - ★ `verify-before-claiming` —— **事実を断定する前**（「動くはず」「不要」「壊れる」）
   - `hook-constraints` —— `CGEventTap` / TCC / GCD に触るとき
   - `data-privacy` —— 削除 UI・同意文書の約束に触れるとき
   - `git-workflow` —— コミット・`.steering/` 記録
3. **サブエージェントに委譲する**: レビュー=`code-reviewer` ＋ `security-checker` を**並列**。
4. **`/cross-review`（Codex）は各タスク完了時に必須。**
5. ⚠️ **テストは `src-tauri/` から実行する**（★ repo 直下に `Cargo.toml` は無い）:
   ```bash
   cd src-tauri && cargo test --features package --workspace
   ```
6. ⚠️ Hook はすべて bash 前提。
7. ⚠️★★ **「緑だから正しい」と書かない。** ★ 実機で操作していないことを操作したと書かない。
