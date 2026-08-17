# タスクリスト — Windows self-hosted ＋ 30 秒フォールバック

## ⚠️★★★ 2026-08-16 追記 — 実施状況（★ G-GEAR 本体のセッションで実測）

> ★ 起点は `issue-windows-selfhosted-ci-never-activated.md`（macOS 側セッションが起票）:
> **「条件分岐は正しく動いているが、`gse-win` ランナーも PAT も無いので判定は毎回 `hosted` に落ちており、
> self-hosted 経路は一度も実行されていない」**。★ 実測で再現した（secrets が exit 0 で `total_count: 0`）。

| 手順 | 状態 |
|---|---|
| ランナーの展開（`C:\actions-runner`） | ★ **完了**（v2.336.0・103,253,740 bytes ＝ リリース資産と一致。★ 2026-08-16 時点でも最新版） |
| 手順 1: `gse-win` の登録 | ★ **完了** —— `g-gear-win-x64` **online** / labels `self-hosted,Windows,X64,gse-win` |
| サービス化 | ★ **完了** —— `actions.runner.mikotomiura-GSE-prototype.g-gear-win-x64` が **Running / StartType: Automatic**（★ 再起動後も自動復帰） |
| 手順 2: `RUNNER_STATUS_TOKEN` | ★ **完了**（fine-grained PAT・`GSE-prototype` のみ・Administration=Read-only・期限つき） |
| ★★★ **検査 A（陽性）** | ★ **合格**（PR #103・run 31966988032） |
| ★★★ **検査 B（fallback・本命）** | ★ **合格**（同 run の再実行・下記） |

### ★★★ 検査 B の結果（2026-08-16）—— ⚠️ **issue §3 が「誤読の危険」と名指しした部分**

★ 手順: **`Stop-Service`** でランナーを止め、GitHub 側が `offline` になったのを確認してから再実行した。

★ `decide-win-runner` の実出力（逐語）:

```
##[notice]gse-win did not come online within 30s -> hosted (fallback)
resolved runs-on = ["windows-latest"]
```

★★★ **`RUNNER_STATUS_TOKEN is unset` ではない** —— ⚠️ **ここが検査 B の有効性そのもの**。

★ **所要時間で 30 秒ポーリングが走ったことを裏づけた**（★ 実測）:

| 時刻 | 出来事 |
|---|---|
| `19:37:31.717` | `Probe self-hosted Windows runner` 開始 |
| `19:37:59.435` | `did not come online within 30s -> hosted (fallback)` |
| **差** | ★★★ **約 27.7 秒**（`5 秒 × 6 回` ＋ API 往復 と整合） |

⚠️★★★ **issue の指摘「30 秒ポーリングのコードは 1 行も実行されていない」は、これで初めて解消した。**
★ 以前の「hosted で走って緑」は **トークン未設定による即 return** であり、
**フォールバック機構を検証していなかった**（＝陽性対照の無い検査を合格と誤読していた）。

### ★★★ 検査 A の結果（2026-08-16・run 31966988032）

★ `decide-win-runner` の実出力（逐語）:

```
resolved runs-on = ["self-hosted","gse-win"]
```

★ `check (gse-win-selfhosted, x86_64-pc-windows-msvc)` = **success**。全 8 ステップが G-GEAR 上で緑:

| ステップ | 結果 |
|---|---|
| `actions/checkout@v4` | success |
| `dtolnay/rust-toolchain@stable`（rustc **1.97.1** を導入） | success |
| `Swatinem/rust-cache@v2` | success |
| **`Cargo build (x86_64-pc-windows-msvc)`** | ★ **success** |
| **`Cargo test --workspace`** | ★ **success** |
| **`Snapshot regression (gse-replay --snapshot)`** | ★ **success** |
| **`Schema drift check`**（`shell: bash`） | ★ **success** |

→ ★★★ **issue の核心「self-hosted 経路は一度も実行されていない」は解消した。**
⚠️ **ただしそこに至るまでに 3 つの前提不足を踏んだ**（下記の落とし穴 1〜3）。
★ **1 発では通らなかったことを記録に残す** —— 「登録すれば動く」ではない。

### ★ G-GEAR の前提（★ 「self-hosted には開発環境が無い」への回答・実測）

| 前提 | 実測 |
|---|---|
| Rust | **1.94.1** / host target `x86_64-pc-windows-msvc`（installed） |
| MSVC | **Visual Studio Build Tools 2026** 17.14（`VC.Tools.x86.x64`） |
| bash / git | Git Bash あり（★ `check` の schema drift ステップが `shell: bash`） |
| ディスク | 空き 624G |

⚠️ **サービスの既定アカウントは `NT AUTHORITY` の `NETWORK SERVICE`** で、ユーザー `johnd` とは別プロファイルになる。
★ Rust は `dtolnay/rust-toolchain` がジョブ内で入れるので通るはずだが、
**リンカで落ちたら `--windowslogonaccount` で `johnd` に変える**。

### ⚠️★★★ 実際に踏んだ落とし穴 — **サービスは「システム PATH」しか見ない**

★ 検査 A の初回で **`check (gse-win-selfhosted)` が failure** になった。逐語:

```
##[error]bash: command not found
```

★ 発生箇所は `dtolnay/rust-toolchain`（`shell: bash` を使う）。★ 原因は PATH:

| 実測 | 値 |
|---|---|
| システム PATH の Git | **`C:\Program Files\Git\cmd` のみ**（⚠️ ここに `bash.exe` は**無い**） |
| `bash.exe` の実体 | `C:\Program Files\Git\bin\bash.exe` ／ `...\usr\bin\bash.exe` |
| ユーザー PATH の Git | ★ **空**（＝対話シェルで bash が見えていたのは別経路） |

→ ★★★ **サービスは `NETWORK SERVICE` なのでユーザー PATH を見ない。**
★ 対話シェルで `where bash` が通ることは、**サービスから見えることの証拠にならない**。

★ **対処（管理者 PowerShell）**:

```powershell
$p = [Environment]::GetEnvironmentVariable('Path','Machine')
if ($p -notlike '*C:\Program Files\Git\bin*') {
  [Environment]::SetEnvironmentVariable('Path', $p.TrimEnd(';') + ';C:\Program Files\Git\bin', 'Machine')
}
Restart-Service actions.runner.mikotomiura-GSE-prototype.g-gear-win-x64
```

⚠️★★★ **`C:\Program Files\Git\usr\bin` を PATH に足してはならない** ——
中に `find.exe` / `sort.exe` / `link.exe` / `tar.exe` / `echo.exe` があり、
**Windows 標準コマンドを上書きして他のビルドを壊す**。★ 足すのは `bin`（`bash.exe` / `git.exe` / `sh.exe` の 3 つだけ）。

★ **なお hosted の `windows-latest` は `C:\Program Files\Git\bin` を PATH に持っている**ので、
この追加は **hosted に合わせる**という意味でもある。

### ⚠️★★★ 落とし穴 2 — **PowerShell の実行ポリシーが `Restricted`**

★ bash を直した次の再実行で、今度は `Cargo build` が落ちた。逐語:

```
File C:\actions-runner\_work\_temp\<uuid>.ps1 cannot be loaded because running scripts is disabled on this system
    + FullyQualifiedErrorId : UnauthorizedAccess
```

★ **GitHub Actions は Windows で `shell:` 未指定のステップを生成 `.ps1` として実行する**ので、
`Cargo build` / `Cargo test` / `Snapshot regression` が**まとめて落ちる**
（★ `Schema drift check` だけは `shell: bash` なので影響を受けない）。

★ **対処（管理者 PowerShell）**:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope LocalMachine -Force
```

★ **`LocalMachine` にするのが要点** —— サービスアカウント（`NETWORK SERVICE`）に効かせる必要があり、
`CurrentUser` では対話ユーザーにしか効かない。
★ `RemoteSigned` を採る理由: runner が `_temp` に生成する `.ps1` は**ローカル扱いなので通り**、
ダウンロードしたスクリプトには署名を要求する。⚠️ `Bypass` は緩すぎるので採らない。

### ⚠️★★ 落とし穴 3 — **`Get-/Set-ExecutionPolicy` 自体が壊れている機がある**

★ この機では `Microsoft.PowerShell.Security` モジュールの import が失敗する（実測）:

```
TypeData "System.Security.AccessControl.ObjectSecurity" にエラーがあります: メンバー AuditToString は既に存在します
```

⚠️ **`Get-ExecutionPolicy` / `Set-ExecutionPolicy` はこのモジュールに属する**ので、
**「コマンドが見つかりません」で無反応に見える**。★ 確認は**レジストリプロバイダ**で行う:

```powershell
(Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\PowerShell\1\ShellIds\Microsoft.PowerShell' -Name ExecutionPolicy).ExecutionPolicy
```

⚠️★★★ **さらに `reg query "HKLM\..."` を bash から叩いてはいけない** ——
バックスラッシュがエスケープで壊れて**構文エラーになり、それを「値が無い」と読み違える**
（★ 2026-08-16 に実際にやり、「未設定」と誤報告した）。★ **失敗を「不在」と読まない。**

---

## 調査（★ 完了）

- [x] ★ 現行 `ci.yml` の self-hosted 構成を一次で読む（mac は `gse-mac` で移行済み）
- [x] ★ 登録済みランナーを実測（**`macbook-air-m-arm64` の 1 台のみ**・`gse-win` は未登録）
- [x] ⚠️ `timeout-minutes` がキュー待ちに効かないことを確認
- [x] ⚠️ offline 時は **24〜48 時間滞留**することを確認
- [x] ⚠️ `GITHUB_TOKEN` でランナー一覧を取得できないことを確認
- [x] ★ repo が **PRIVATE** であることを確認（fork PR のリスク評価）
- [x] ★ ランナー最新版 **v2.336.0**（mac と同版）を確認
- [x] ★ G-GEAR の実機スペックを実測（**Ryzen 7 9700X 8C/16T / 31.1 GB**）

## 実装（★ 完了・コミット済み）

- [x] `decide-win-runner` ジョブを追加（`d28d295`）
- [x] `check` の `runs-on` を動的解決へ（`d28d295`）
- [x] `build-windows` を hosted のまま残す理由を明記（`d28d295`）
- [x] ⚠️ **Surface Pro → G-GEAR の訂正**（`099155d`・研究者の指摘）

## テスト（★ ローカル検証 ＋ ★ **実 CI の検査 A / B とも完了**・2026-08-16）

- [x] YAML parse OK ／ `bash -n` rc=0 ／ `decide` と `check` の `if` が一致
- [x] ★ 陽性: ランナー online → self-hosted（attempt 1）
- [x] ★ 陰性: 未登録 → 30 秒後に hosted
- [x] ★ fail-safe: PAT 未設定 → 即 hosted
- [x] ★ **実 PR で self-hosted 側が拾うこと** → **合格**（run 31966988032・PR #103）
- [x] ⚠️★★★ **ランナーを落とした状態の PR で 30 秒後に hosted へ落ちること**（★ 本命の検査）
      → **合格**（約 27.7 秒で `did not come online within 30s -> hosted (fallback)`）

---

## ⚠️★★★ ここから研究者の手が要る（★ 私は実行しない）

> ★ 理由: **(a) GitHub への登録＝外向きの操作**、**(b) Windows サービスの導入＝要 admin**、
> **(c) PAT は秘密情報**。★ いずれも `!` で研究者が実行する。

### 手順 1: `gse-win` ランナーを G-GEAR に登録する

★ **管理者権限の PowerShell** で実行する（★ サービス導入に要る）。

```powershell
# 1-1. 登録トークンを取る（★ 有効 1 時間）
gh api -X POST repos/mikotomiura/GSE-prototype/actions/runners/registration-token -q .token

# 1-2. 展開（★ repo の外に置く。★ v2.336.0 = mac 側と同版）
mkdir C:\actions-runner; cd C:\actions-runner
Invoke-WebRequest -Uri https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-win-x64-2.336.0.zip -OutFile runner.zip
Expand-Archive -Path runner.zip -DestinationPath . -Force

# 1-3. 設定（★ <TOKEN> は 1-1 の出力に差し替える）
#     ★ --labels gse-win が要（ci.yml がこのラベルで探す）
#     ★ --runasservice で Windows サービス化 → 再起動後に自動で online へ戻る
.\config.cmd --url https://github.com/mikotomiura/GSE-prototype `
             --token <TOKEN> `
             --name g-gear-win-x64 `
             --labels gse-win `
             --unattended --runasservice

# 1-4. 確認
#  ⚠️★★★ 2026-08-16 訂正: **v2.336.0 の Windows パッケージに `svc.cmd` は存在しない**
#     （bin/ にあるのは svc.sh 系の Unix 用テンプレートのみ）。★ サービス名は .service に入る。
Get-Content .service     # -> actions.runner.mikotomiura-GSE-prototype.g-gear-win-x64
Get-Service actions.runner.mikotomiura-GSE-prototype.g-gear-win-x64
gh api repos/mikotomiura/GSE-prototype/actions/runners -q '.runners[] | "\(.name) \(.status) \([.labels[].name]|join(","))"'
```

> ★ **`--runasservice` が効くと、G-GEAR を落として立ち上げ直しても自動で online に戻る。**
> ⚠️ **落ちている間だけ hosted に逃げる**、というのが本タスクの狙いどおりの状態。

### 手順 2: PAT を作り secret に置く

1. ★ **fine-grained PAT** を作る（★ 権限を最小にする）:
   - Repository access: **Only select repositories → `mikotomiura/GSE-prototype`**
   - Repository permissions: **Administration = Read-only**（⚠️ **Read で足りる。Write を付けない**）
   - Expiration: ★ **期限を付ける**（⚠️ 無期限にしない）
2. ★ secret に置く:

```powershell
gh secret set RUNNER_STATUS_TOKEN --repo mikotomiura/GSE-prototype
# → プロンプトに PAT を貼る

# 確認（★ 値は出ない。名前だけ）
gh secret list --repo mikotomiura/GSE-prototype
```

> ⚠️★★★ **secret を置くまでは、workflow は常に hosted へ落ちる**（fail-safe）。
> ★ **CI が壊れることはない**ので、手順 1 と 2 の順序はどちらでもよい。

### 手順 3: 実 CI で検査する

⚠️★★★ **現ブランチ `docs/media-sound-modality-survey` では CI が発火しない**
（★ `push` のトリガは `[main, "feature/*"]`）。→ ★ **main への PR を出すこと**（`pull_request: [main]` で発火）。

```powershell
# ★ push は deny されているので研究者が実行する
git push -u origin docs/media-sound-modality-survey
gh pr create --base main --title "chore(ci): Windows check を self-hosted へ（30 秒フォールバック付き）" --fill
```

- [ ] ★ **検査 A（陽性）**: ランナー online の状態で PR → `decide-win-runner` のログに
      `gse-win runner is online` が出て、`check (gse-win-selfhosted)` が **self-hosted で走る**
- [ ] ⚠️★★★ **検査 B（本命）**: **`Stop-Service actions.runner.mikotomiura-GSE-prototype.g-gear-win-x64`**
      （⚠️ **要 admin**・★ `svc.cmd` は存在しない）でランナーを止めてから PR を更新 →
      `decide-win-runner` が **30 秒後に** `-> hosted (fallback)` を出し、`windows-latest` で走る
      ★ ⚠️ **`RUNNER_STATUS_TOKEN is unset` が出ていたら検査 B は無効**（別の理由で落ちている）
- [ ] ★ 検査 B のあと **`Start-Service actions.runner.mikotomiura-GSE-prototype.g-gear-win-x64`**（要 admin）で戻す

## レビュー

- [ ] ★ `code-reviewer` + `security-checker` を並列起動（⚠️ **secret / PAT 権限の妥当性を見てもらう**）
- [ ] ⚠️ `/cross-review`（★ 入力は `ci.yml` の diff のみ）

## 完了処理

- [ ] ★ 検査 A / B の結果を `decisions.md` に記録
- [ ] `/finish-task`
