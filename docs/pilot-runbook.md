# M1 パイロット (Y 側) 運用ランブック — データ収集→分析パイプライン

> 対象: M1 パイロット (n=3-5) で被験者から匿名化セッションを受領し、metrics + survey を
> `participant_id × phase` で結合して `cross_section` を出すまでの **end-to-end 運用手順**。
> X 側の対応物は `docs/calibration-smoke-runbook.md`。設計判断は
> `.steering/20260624-pilot-pipeline-runbook/decisions.md` (D-PP1..5) /
> `.steering/20260624-transfer-pipeline/decisions.md` (D1..7) を参照。
>
> **散歩介入は Phase 1 では WoZ (Wizard-of-Oz)** — 歩数/移動の実計測コードは作らない (D8)。
> Wall の散歩文言は出る前提で、受容性は post survey の自己申告で拾う。

データの流れ:

```
[被験者端末]                               [研究者端末]                         [分析]
raw NDJSON                                 P###_x.age (受領)
  │ gse-package (匿名化 + age 暗号化)         │ gse-unpack (age 復号)
  ▼                                          ▼
P###_x.age ──Dropbox File Request──────▶   匿名化 NDJSON
                                             │ sync-session --no-commit
                                             ▼
                                           metrics/P###/<os>/*.metrics.json
                                             │ gen_sessions_manifest + phase 手記入
                                             ▼ + survey/P###.csv
                                           sessions.csv
                                             │ build_analysis_db.py (#6)
                                             ▼
                                           cross_section (pre/post 横断)
```

---

## 0. 前提・プライバシー (厳守)

- **git-bash 必須** (Windows)。helper / hook はすべて bash 前提。
- **プライバシー (data-privacy / §10 / decisions.md D1)**:
  - キーストローク**内容**・生 NDJSON・**復号後の平文 NDJSON**・**age 秘密鍵**は本リポにも
    gse-dataset にもコミットしない / 外部送信しない。端末ローカル保持。
  - 共有してよいのは gse-dataset の `metrics/*.metrics.json` (集計値) と `survey/*.csv`
    (数値尺度のみ) と `cohort/` 判定 JSON だけ。
  - 実名↔P-ID 対応表は **repo 外**で研究者が管理する。
  - `analysis.db` は使い捨て (再生成可能)。コミットしない。
- **保存先**: `GSE_DATASET` を gse-dataset に向ける (永続化推奨)。
  ```bash
  # PowerShell (User 環境変数として永続化)
  [Environment]::SetEnvironmentVariable('GSE_DATASET', 'C:\gse-dataset', 'User')
  ```

---

## 1. ビルド (研究者 / 被験者配布パッケージ作成者)

被験者配布用と研究者用の 2 つの CLI は `package` feature でビルドする (age 依存は default の
Tauri 本体に載らない)。

```bash
cd src-tauri
# 被験者に配る暗号化 CLI
cargo build --release --features package --bin gse-package
# 研究者用の復号 / 鍵生成 CLI
cargo build --release --features package --bin gse-unpack
cd ..
# 生成物: src-tauri/target/release/gse-package(.exe) / gse-unpack(.exe)
```

---

## 2. 研究者: age 鍵ペアの準備 (パイロット開始前に 1 回)

`gse-unpack --keygen` で X25519 鍵ペアを作る。**公開鍵だけ**を被験者配布パッケージに同梱し、
**秘密鍵は研究者端末の repo 外**に保管する (ゼロ知識保管: 研究者だけが復号できる)。

```bash
# 秘密鍵は repo 外 (既定: ~/.gse/age-identity.txt)。公開鍵が stdout に出る。
./src-tauri/target/release/gse-unpack --keygen --out ~/.gse/age-identity.txt
# 出力例:
#   age public key (give to participants as --recipient):
#   age1qz...          ← この公開鍵を被験者配布パッケージ (pubkey.txt) に入れる
#   secret key written to: ~/.gse/age-identity.txt (KEEP SECRET, not in repo)
```

- 公開鍵 (`age1...`) を `pubkey.txt` に保存し、`gse-package` exe と一緒に被験者へ配る (公開鍵は
  配布安全)。
- **秘密鍵ファイルは絶対にコミット/共有しない**。`.gitignore` に `*age-identity*` / `*.agekey` を
  登録済 (多層防御)。Windows では共有フォルダ・Dropbox 同期下に置かない。

---

## 3. 被験者手順 (3 ステップ — 非技術者向け)

> 配布物: `gse` 本体アプリ + `gse-package(.exe)` + `pubkey.txt` (研究者公開鍵)。
> Python / age CLI のインストールは不要。

### Step 1 — セッション収集
- いつも通りアプリを起動して作業する。**介入を有効** (`interventionEnabled=true`) で、
  Wall が出たら案内文に従う。
- **散歩 (WoZ)**: Wall に「席を立って歩く」旨が出たら、**実際に席を立って少し歩く**。
  歩数計などは不要 — 後で post アンケートに「歩いたか / 戻れたか / 受容できたか」を答えるだけ。
- セッション終了すると `raw/P000/gse_YYYYMMDD_HHMMSS.ndjson` が生成される (起動ログの
  `resolved_log_dir` で場所を確認)。

### Step 2 — 匿名化 + 暗号化 (1 コマンド)
```bash
# <参加者番号> は研究者から割り当てられた P### を使う
gse-package --input <raw.ndjson> --participant P003 --recipient pubkey.txt
# → P003_gse_YYYYMMDD_HHMMSS.age が同じフォルダに出る
```
- このコマンドは (1) キー内容を category へ匿名化し、(2) 研究者の公開鍵で暗号化する。
  **元の生 NDJSON は送らない。** `.age` は研究者の秘密鍵でしか開けない暗号塊。

### Step 3 — Dropbox File Request で提出
- 研究者が用意した **Dropbox File Request URL** を開き、`P003_*.age` を **ドラッグ&ドロップ**するだけ。
  - (File Request は受領者(研究者)だけが中身を見られ、提出者同士は互いのファイルを見られない。)
- `.age` は暗号化済なので転送経路は信用不要 (D6)。生 NDJSON は手元に残し、提出しない。

---

## 4. 研究者手順 (受領 → cross_section)

受領した各 `P###_*.age` について以下を回す。`GSE_DATASET` は gse-dataset を指す前提。

### 4.1 復号 (`.age` → 匿名化 NDJSON)
```bash
# 復号。出力は匿名化 NDJSON (P###_*.ndjson)。--out 省略時は .age と同じフォルダ。
gse-unpack --input P003_gse_20260624_101500.age --identity ~/.gse/age-identity.txt --out ./inbox
# → ./inbox/P003_gse_20260624_101500.ndjson (匿名化済・category 形式)
```
> 復号後の平文 NDJSON は**ローカルのみ**。gse-dataset / 本 repo にコミットしない (data-privacy)。
> raw `"vk"` が残っていれば gse-unpack が件数を WARN する (匿名化漏れの早期検知)。

### 4.2 metrics 化 (sync-session)
匿名化 NDJSON を `gse-replay --metrics` に通して `metrics/P###/<os>/*.metrics.json` を作る。
復号ファイルは `raw/<PID>/` 構造の外にあるので、PID は `GSE_PID` で明示する。

```bash
# Windows
pwsh -NoProfile -File scripts/sync-session.ps1 `
    -SessionPath .\inbox\P003_gse_20260624_101500.ndjson -ParticipantId P003
# macOS/Linux
GSE_PID=P003 ./scripts/sync-session.sh ./inbox/P003_gse_20260624_101500.ndjson
```
- 出力: `$GSE_DATASET/metrics/P003/<os>/P003_gse_20260624_101500.metrics.json`。
- 複数本まとめて回すなら `scripts/sync-all.{sh,ps1}` も使える (raw 構造前提)。

### 4.3 survey CSV の配置
- 各被験者の Google Form 由来データを `$GSE_DATASET/survey/P###.csv` に置く
  (1 ファイル束ね `survey/all.csv` でも可。`build_analysis_db.py` は `survey/*.csv` を結合)。
- スキーマとテンプレートは **`scripts/templates/survey-template.csv` / `scripts/templates/README.md`**。
  最小列: `participant_id, phase, gse_total, nasa_tlx_total` + **D8 WoZ 列** (post のみ):
  `walk_done` (0/1), `returned_to_work` (1-5), `inconvenience_benefit_accepted` (1-5)。
- グレインは **(participant_id, phase) で一意**。重複すると build が exit 4 で止まる。
- **PII 列禁止** (実名/メール/電話/住所等)。列名に PII トークンがあると build が exit 6 で止まる。

### 4.4 sessions.csv 生成 + phase 記入
どの session が pre / post かは研究設計依存なので、ヘルパが行を吐き、phase は手記入する (D-PP3)。

```bash
python scripts/gen_sessions_manifest.py --dataset "$GSE_DATASET"
# → $GSE_DATASET/sessions.csv (participant_id,session_id,os,phase) を生成。phase 列は空。
```
- 生成された `sessions.csv` を開き、各行の **`phase` 列に `pre` か `post`** を記入する。
- 再実行しても**記入済みの phase は保全マージ**される (上書きしない)。metrics が消えた行は除外。

### 4.5 分析 DB 構築 (cross_section)
```bash
python scripts/build_analysis_db.py --dataset "$GSE_DATASET" --out analysis.db \
    --export-dir out/ --format csv
# → analysis.db (使い捨て) + out/cross_section.csv
```
- `cross_section` は `(participant_id, phase)` グレイン。`has_metrics` / `has_survey` フラグで
  「データ無し」と「実測ゼロ」を区別する (#19 の outcome=None 思想)。
- これで pre/post の (a) AI 依存 / (b) 自己解決 metrics と (c) GSE 自己効力感・WoZ 受容を
  横断して見られる。統計解析・効果量推定は Phase F 本体 (本 runbook 範囲外)。

---

## 5. 通し統合スモーク (結線が壊れていないかの検証)

実データ無しで全段 (package→unpack→metrics→sessions.csv→cross_section) を 1 コマンド検証できる。
パイプラインのスクリプトを変更したら回す。**cargo + python + duckdb のみ** (age CLI 不要)。

```bash
pip install -r scripts/requirements-dev.txt   # 初回のみ (duckdb)
./scripts/pilot-smoke.sh
# → ... PASS ✅  end-to-end: package → unpack → metrics → sessions.csv → cross_section (N row(s))
```
一時資材 (鍵・平文・age・DB) は mktemp 下で完結し終了時に消える。

---

## 6. トラブルシュート

| 症状 | 対処 |
|---|---|
| `gse-unpack: age decrypt failed (wrong key?)` | `--identity` が暗号化に使った公開鍵と対の秘密鍵か確認。被験者に配った `pubkey.txt` と同じ鍵ペアか。 |
| 復号 NDJSON で `WARNING: ... raw "vk"` | 被験者が匿名化前ログを誤って暗号化した可能性。共有せず、被験者に gse-package 経由で再生成依頼。 |
| `build_analysis_db ... exit 6 (PRIVACY GUARD)` | survey CSV の列名に PII トークン。列をリネーム/削除 (数値尺度 + P-ID/phase のみ)。 |
| `build_analysis_db ... duplicate (participant_id, phase)` | 同じ (P-ID, pre/post) が survey に重複。de-dup する。 |
| `gen_sessions_manifest ... no sessions found` | 先に 4.2 (sync-session) で metrics を作る。`--dataset` が gse-dataset ルートか確認。 |
| metrics の os が想定と違う | sync-session は実行 OS でラベルする。Windows は ps1 (=windows)、git-bash の sh は環境依存。`--output-dir` で明示可。 |
| `gse-package: no 'age1...' public key found` | `--recipient` に渡した `pubkey.txt` に `age1...` 行が無い。keygen 出力の公開鍵行を保存し直す。 |

---

## 7. プライバシー要点 (再掲・チェックリスト)

- [ ] age **秘密鍵**は repo 外・未コミット (`.gitignore` 登録済)。共有/同期フォルダに置かない。
- [ ] 復号後の **平文 NDJSON** を gse-dataset / 本 repo にコミットしない。共有は `metrics.json` のみ。
- [ ] survey CSV は **数値尺度 + P-ID/phase のみ**。PII 列なし。
- [ ] 実名↔P-ID 対応表は repo 外。
- [ ] `analysis.db` / `cross_section.*` (個票) はコミットしない (使い捨て)。
