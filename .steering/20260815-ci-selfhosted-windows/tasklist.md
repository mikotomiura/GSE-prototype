# タスクリスト — Windows self-hosted ＋ 30 秒フォールバック

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

## テスト（★ ローカル検証は完了 / ⚠️ 実 CI は未実施）

- [x] YAML parse OK ／ `bash -n` rc=0 ／ `decide` と `check` の `if` が一致
- [x] ★ 陽性: ランナー online → self-hosted（attempt 1）
- [x] ★ 陰性: 未登録 → 30 秒後に hosted
- [x] ★ fail-safe: PAT 未設定 → 即 hosted
- [ ] ⚠️ **実 PR で self-hosted 側が拾うこと**
- [ ] ⚠️★★★ **ランナーを落とした状態の PR で 30 秒後に hosted へ落ちること**（★ 本命の検査）

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
.\svc.cmd status
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
- [ ] ⚠️★★★ **検査 B（本命）**: `.\svc.cmd stop` でランナーを止めてから PR を更新 →
      `decide-win-runner` が **30 秒後に** `-> hosted (fallback)` を出し、`windows-latest` で走る
- [ ] ★ 検査 B のあと `.\svc.cmd start` で戻す

## レビュー

- [ ] ★ `code-reviewer` + `security-checker` を並列起動（⚠️ **secret / PAT 権限の妥当性を見てもらう**）
- [ ] ⚠️ `/cross-review`（★ 入力は `ci.yml` の diff のみ）

## 完了処理

- [ ] ★ 検査 A / B の結果を `decisions.md` に記録
- [ ] `/finish-task`
