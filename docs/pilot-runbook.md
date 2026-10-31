# M1 パイロット (Y 側) 運用ランブック — データ収集→分析パイプライン

> 対象: M1 パイロット (n=3-5) で被験者から匿名化セッションを受領し、metrics + survey を
> `participant_id × phase` で結合して `cross_section` を出すまでの **end-to-end 運用手順**。
> X 側の対応物は `docs/calibration-smoke-runbook.md`。設計判断は
> `.steering/20260624-pilot-pipeline-runbook/decisions.md` (D-PP1..5) /
> `.steering/20260624-transfer-pipeline/decisions.md` (D1..7) を参照。
>
> **散歩介入は Phase 1 では WoZ (Wizard-of-Oz)** — 歩数/移動の実計測コードは作らない (D8)。
>
> ---
>
> ## ⚠️★★★ 本文書の現在の状態 (2026-09-01)
>
> | 節 | 状態 |
> |---|---|
> | **§受領 (`.age` の復号・P### リネーム・metrics 結合)** | ★ **現行で生きている。** `scripts/install-researcher-tools.sh:138` が install 完了時に本節を案内しており、**O1 (継続的自然作業収集) が produce する `.age` も同じ手順で受ける** (`docs/o1-deletion-ledger.md` §4) |
> | **被験者の実施手順 (Step 1 の介入まわり)** | ⚠️★★★ **Wall 依存部分は失効した** —— 下記 Step 1 参照 |
> | **M1 パイロット (n=3-5) 固有の運用** | ★ **過去フェーズ。** 履歴として残す |
>
> ⚠️★★★ **旧文はここに「Wall の散歩文言は出る前提で、受容性は post survey の自己申告で拾う」と書いていたが、
> Wall は ADR-015 (2026-08-23) で削除済みであり、この前提は成立しない。**
> ★ **WoZ という方式自体 (D8) は不変** —— ⚠️ **変わったのは「何が散歩を promptするか」である。**
> ★ 現行で稼働する介入は **無い**（Nudge は ADR-040 D1 で既定で無効・2026-10-31。招待は EH3 モードでだけ動く）。**Physical Anchor は未実装**である
> (かつ ADR-018 D1 で完了条件を持たない「方向づけ」に改められた)。
> → ★ **散歩の prompt を出すなら研究者が口頭・書面で行う (＝ WoZ の本来の形)。**

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

★ **1 コマンドで workspace の `bin/` に install する**（2026-08-03 で経路を統一）:

```bash
bash scripts/install-researcher-tools.sh          # gse-unpack を bin/ へ
bash scripts/install-researcher-tools.sh --check  # 入っているかだけ確認
```

- ★ **配置後に `--help` を実行して動くことまで確認する**（署名・実行権限・アーキ違いをここで捕まえる）。
- ⚠️ `bin/` は `.gitignore` 済み。**バイナリをコミットしない**（本リポジトリは一時 public にする運用がある）。
- `gse-package`（被験者向け手動版）も要るなら `--with-package` を付ける。
  ⚠️ ★ **通常は不要**——`gse-package` は Phase1 で誰も使わず、配布もしなくなった。

<details>
<summary>手で叩く場合（スクリプトを使わないとき）</summary>

```bash
cd src-tauri
cargo build --release --features package --bin gse-unpack
cd ..
# 生成物: src-tauri/target/release/gse-unpack(.exe)
```
⚠️ `src-tauri/target/` は `cargo clean` や toolchain 更新で消える。手順書に書くパスとしては
`bin/` のほうが安定する。
</details>

---

## 2. 研究者: age 鍵ペアの準備 (パイロット開始前に 1 回)

`gse-unpack --keygen` で X25519 鍵ペアを作る。**公開鍵だけ**を被験者配布パッケージに同梱し、
**秘密鍵は研究者端末の repo 外**に保管する (ゼロ知識保管: 研究者だけが復号できる)。

```bash
# 秘密鍵は repo 外 (既定: ~/.gse/age-identity.txt)。公開鍵が stdout に出る。
./bin/gse-unpack --keygen --out ~/.gse/age-identity.txt
# 出力例:
#   age public key (give to participants as --recipient):
#   age1qz...          ← この公開鍵を被験者配布パッケージ (pubkey.txt) に入れる
#   secret key written to: ~/.gse/age-identity.txt (KEEP SECRET, not in repo)
```

- 公開鍵 (`age1...`) を `pubkey.txt` に保存する（公開鍵は配布して安全）。
  - ★ **macOS**: `.app` の Resources に内蔵される（CI が同梱を assert する）。個別配布は不要。
  - ★ **Windows**: `gse-next.exe` / `gse-submit.exe` / `提出する_win.bat` と**同じフォルダ**に置いて配る。
  - `gse-submit` は同梱 `pubkey.txt` を自動で recipient に使う。
- **公開鍵の取り違え防止**: 初回セッション同席時に、配布 `pubkey.txt` の `age1...` 文字列が研究者手元の
  keygen 出力と一致することを目視確認する (gse-submit は鍵ピンニングしないため、配布フォルダの
  `pubkey.txt` がすり替わると暗号化先が変わる。中身は匿名化済だが宛先誤りを防ぐ・security review LOW)。
- **秘密鍵ファイルは絶対にコミット/共有しない**。`.gitignore` に `*age-identity*` / `*.agekey` を
  登録済 (多層防御)。Windows では共有フォルダ・Dropbox 同期下に置かない。

### 2.1 配布パッケージの作成 (★混入チェック必須)

被験者に配る zip は **配布専用の空フォルダに必要物だけをコピー**して作る。`~/.gse/` を含む
フォルダごと固めると、秘密鍵 (`age-identity.txt`) や端末固有の `participant_id` まで巻き込むため厳禁。

**入れてよいもの (これだけ)**:
- Windows: `gse-next.exe` (portable) + `gse-package.exe` + `pubkey.txt`
- macOS:   `gse-next_*_aarch64.dmg` + `gse-package` + `pubkey.txt`

**絶対に入れないもの**:
- `~/.gse/age-identity.txt` — age 秘密鍵 (全データ復号可・致命的)
- `~/.gse/participant_id` — 端末固有の自動生成ID。被験者が使うとアプリ内ログIDが**あなたのID**で
  記録され混線する (解決優先順で永続化値が最優先のため。`logger.rs`)
- `.gse/` フォルダそのもの・`*.agekey`・GSE_DATASET 配下のセッションログ(`gse_*.ndjson`)

**作成後チェック (固めた zip を必ず検証)**:
```bash
# 配布 zip を展開したフォルダで、危険物が混入していないか確認
find . \( -name 'age-identity.txt' -o -name 'participant_id' -o -name '*.agekey' -o -name '.gse' \) -print
#   → 何も出力されなければ OK。1 つでも出たら削除して作り直す。
#   特に age-identity.txt が出た場合は鍵漏洩 → 鍵ペアを作り直して再配布する。
```

---

## 3. 被験者手順 (3 ステップ — 非技術者向け)

> 配布物 (★ 2026-08-03 に整理。Phase1 の実績に合わせて最小化した):
> - **macOS**: `.dmg` **のみ**。提出ツール (`gse-submit`) と `pubkey.txt` は `.app` に内蔵されており、
>   アプリ内提出 (方法1) だけで完結する。⚠️ **`提出する_mac.command` 経路は廃止した**。
> - **Windows**: `gse-next.exe` (portable) + `gse-submit.exe` + **`提出する_win.bat`** + `pubkey.txt`
>   を**同じフォルダ**に置く。アプリ内提出 (方法1) が正規で、bat はフォールバック。
>
> ⚠️ ★ **`gse-package(.exe)` は配布しない** (Phase1 で誰も使わずに完了したため)。
> 研究者が手元で必要なときは `bash scripts/install-researcher-tools.sh --with-package` で作れる。
> Python / age CLI のインストールは不要。

### Step 1 — セッション収集
- いつも通りアプリを起動して作業する。**介入を有効** (`interventionEnabled=true`) で、
  **Nudge (画面隅の問いかけ) が出たら、従っても無視してもよい**
  (★ Nudge は非ブロックで自動消失する。作業を止めない)。
- **散歩 (WoZ)**: ★ **研究者からの案内 (口頭・書面) があったら、実際に席を立って少し歩く。**
  歩数計などは不要 — 後で post アンケートに「歩いたか / 戻れたか / 受容できたか」を答えるだけ。
  > ⚠️★★★ **2026-09-01 訂正 —— 旧文は「Wall が出たら案内文に従う」「Wall に『席を立って歩く』旨が
  > 出たら」と書いていたが、Wall は ADR-015 (2026-08-23) で削除済みであり *永久に発火しない*。**
  > ★ **被験者向け文書は契約であり、発火しない指示を残すと被験者が待ち続ける。**
  > ★ WoZ の方式 (既決 D8) は不変で、**prompt の出し手がアプリから研究者に移っただけ**である。
- セッション終了すると `raw/P000/gse_YYYYMMDD_HHMMSS.ndjson` が生成される (起動ログの
  `resolved_log_dir` で場所を確認)。

### Step 2 — 匿名化 + 暗号化 (ダブルクリック・推奨)
- 配布フォルダの **`提出する`** をダブルクリックするだけ。`gse-submit` が
  (1) `~/Documents/GSE-sessions/` の**最新 `gse_*.ndjson` を自動検出**し、
  (2) キー内容を category へ匿名化し (本文非保存)、(3) 研究者の公開鍵で暗号化して
  `~/Documents/GSE-submissions/P###_gse_YYYYMMDD_HHMMSS.age` を出す。
  - **P### はアプリが記録した `~/.gse/participant_id` を自動使用**（手打ち不要・取り違え防止）。
  - **元の生 NDJSON は送らない。** `.age` は研究者の秘密鍵でしか開けない暗号塊。
- 手動が必要なときのみ（上級者）:
  ```bash
  gse-package --input <raw.ndjson> --participant P003 --recipient pubkey.txt
  # → P003_gse_YYYYMMDD_HHMMSS.age が同じフォルダに出る
  ```

### Step 3 — Dropbox File Request で提出
- 研究者が用意した **Dropbox File Request URL** を開き、`P003_*.age` を **ドラッグ&ドロップ**するだけ。
  - (File Request は受領者(研究者)だけが中身を見られ、提出者同士は互いのファイルを見られない。)
- ⚠ **提出者名の入力を求められたら P### を入れる (実名禁止)**。Dropbox File Request は投稿者名を
  ファイル名に付与しうるため、実名を入れると `.age` ファイル名に実名が残る (中身は匿名化済だが
  ファイル名で漏れる)。研究者側でも §4.1 で受領時に P### へリネームして二重に防ぐ (data-privacy)。
- `.age` は暗号化済なので転送経路は信用不要 (D6)。生 NDJSON は手元に残し、提出しない。

---

## 4. 研究者手順 (受領 → cross_section)

受領した各 `P###_*.age` について以下を回す。`GSE_DATASET` は gse-dataset を指す前提。

### 4.1 復号 (`.age` → 匿名化 NDJSON)

**受領直後に実名リネーム (T3・data-privacy)**: Dropbox File Request は投稿者名をファイル名へ付与
しうるため、受領 `.age` 名に実名が残ることがある（例 `P006_gse_..._mikoto miura.age`）。`gse-unpack`
の出力名は入力 `.age` のステムを踏襲するので、**復号前に `P###_gse_YYYYMMDD_HHMMSS.age` の正規形へ
リネーム**して実名を除去する（中身は匿名化済だがファイル名の実名を断つ）。

```bash
# 例: 受領名から実名を剥がして正規形へ。<P###> と日時は受領ファイルから読む。
mv "P006_gse_20260624_101500_mikoto miura.age" P006_gse_20260624_101500.age
# 復号。出力は匿名化 NDJSON (P###_*.ndjson)。--out 省略時は .age と同じフォルダ。
./bin/gse-unpack --input P006_gse_20260624_101500.age --identity ~/.gse/age-identity.txt --out ./inbox
# → ./inbox/P006_gse_20260624_101500.ndjson (匿名化済・category 形式)
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
