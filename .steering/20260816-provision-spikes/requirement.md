# 課題ページ配布自動化 — 実装前の spike を実測で潰す

⚠️ ★ **このタスクは「未検証の前提を実測する」ことに限る。** Stage 1 の本実装
(`provision.py`) は spike の結果を見てから別タスクで行う。

## 背景

`.steering/20260807-vps-provisioning-automation/` で配布自動化の**設計は完了している**
(`tasklist.md` §1 が全て `[x]`)。同 `design.md` は、実装に入る前に潰すべき
**未検証の前提を spike-1〜4 として列挙**し、⚠️「ここは推測のまま実装に入らない」と書いている。

★ 2026-08-16 時点の実測（このセッションで確認）:

| 前提 | 実測 |
|---|---|
| `~/.config/gse-provision/`（資格情報の置き場） | **無い** |
| `provision.py` / `drive_client.py` / `scripts/provision-credentials.md` | **どれも無い** |
| `googleapiclient` / `google_auth_oauthlib` | **未インストール** |
| G1 の状態 | `blocks/` に P001–P020、`results/` は空 = **実施中で提出待ち** |

⚠️ G1 実施中なので `decisions.md` D-6（自動化を G1 本番に差し込まない）が生きている。
★ このタスクは**本番の親フォルダに一切触れない**。

## ゴール

spike-1〜5 の全てについて、⚠️「たぶん / はず」ではなく **実測値と実測日**で可否が言えること。
その副産物として `drive_client.py`（薄い Drive API ラッパ）の初版が残ること。

| # | 確かめること | 外れたときの行き先 |
|---|---|---|
| spike-1 | `drive.file` スコープで、**アプリが作っていない既存フォルダの下に**子フォルダを作れるか | ★ 代替へ切り替えて**続行**（親もアプリに作らせる） |
| spike-2 | `permissions.create(type=anyone, role=reader)` が個人 Gmail で通るか | ⚠️ **止めて相談**（匿名性の設計に触る。`data-privacy` を先に読む） |
| spike-3 | リフレッシュトークンが何日もつか（★ 公開状態「本番」で測る） | ⚠️ **止めて相談**（Stage 2 の前提が崩れる） |
| spike-4 | 上げた HTML が `text/html` のままか（Google 形式に変換されないか） | ★ 現行設計のまま**続行** |
| spike-5 | ★ **`files.list` が `sha256Checksum` を返すか**（追加） | ★ 現行設計（byte 数照合）のまま**続行** |

★ spike-5 を足す理由: `design.md` は「Drive の一覧は `fileSize` しか返さない」を前提に
⚠️「byte 一致は同一の証明ではない」という限界を自認している。しかしその実測は Drive **MCP**
でのものであり、Drive **API v3** は未検証である。`verify-drive-upload.py` の manifest は
**3 列目に既に SHA-256 を持っている**ので、返るなら照合をハッシュ一致へ格上げできる。

## Done（★ 観測可能な形で）

- [ ] `spike-results.md` の spike-1〜5 が全て「可 / 否 + 実測値 + 実測日」で埋まっている
      （⚠️「たぶん」「はず」「〜のはず」を 1 つも含まない）
- [ ] `~/.venvs/gse-provision/bin/python -m pytest` が **exit 0**
      （`drive_client.py` の偽 API 単体テスト。⚠️ **陽性対照込み** — 全部止めるガードが緑にならないこと）
- [ ] 秘密が追跡下に無い: `git ls-files | grep -E 'token|client_secret|credentials'` が **0 件**
- [ ] 後始末が済んでいる: 捨てフォルダを Drive から削除・`PILOT-spike` の `blocks/` `pages/` を削除
- [ ] ⚠️ **本番に触れていないことの証拠**: `git status` に `dist/_drive/` と `blocks/P0*.json` が
      現れない ＋ 本番の親フォルダの子フォルダ数が spike 前後で不変

## Stop（★ 止めて相談する）

- spike-2 が否 / spike-3 で短命判明（上表）
- ⚠️ Cloud Console で**取り返しのつきにくい操作の直前**（公開状態の変更・スコープ追加・
  既存プロジェクトの設定変更）。★ 私が押す前に必ず確認を取る
- ⚠️ 捨てフォルダ以外のフォルダに書き込み/共有変更が必要になったとき

## スコープ

### 含むもの
- OAuth クライアントの作成（★ 公開状態は最初から「本番」）と `~/.config/gse-provision/` への配置
- `scripts/provision-credentials.md`（⚠️ **秘密そのものは置かない**。取り方と置き場だけ）
- `drive_client.py` 初版 ＋ 偽 API の単体テスト
- `scripts/requirements-dev.txt` への依存追記（★ 既存規約どおりバージョン固定）
- 捨てフォルダでの spike-1〜5 実走と後始末

### 含まないもの
- ⚠️ `provision.py`（Stage 1 本体）— spike の結果を見てから別タスク
- ⚠️ VPS / 収束器 / systemd（Stage 2）
- ⚠️ **G1 本番の配布物**（`dist/_drive/` / 本番の親フォルダ / `blocks/P0*.json`）
- ⚠️ `prepare-subjects.sh` などの手作業版の変更（D-5 で残すと決めている）
- ⚠️ GAS (`Form_G1/`) の変更（D-3 の④で「1 行も変えない」）
- ⚠️ `preregistration.md` / `schema_dto.rs` の変更

## grill で確定した分岐（★ 詳細は decisions.md）

| 分岐 | 確定 |
|---|---|
| OAuth 同意画面の公開状態 | ★ 最初から「本番」（S-1） |
| spike で上げる中身 | ★ `assign.py --pilot --pilot-label spike` で `PILOT-spike` を生成（S-2） |
| spike を通すコード | ★ `drive_client.py` の初版として残す（S-3） |
| spike-5 の追加 | ★ 追加する（S-4） |
| Python 依存の置き場 | ★ `~/.venvs/gse-provision`（S-5） |
| Console 作業 | ★ `claude-in-chrome` で私が操作・あなたが画面で確認（S-6） |

## 関連ドキュメント

- `.steering/20260807-vps-provisioning-automation/` — **設計の SSOT**（design.md / decisions.md D-1〜D-8）
- `experiments/20260801-controlled-friction-task/verify-drive-upload.py` — ★ 照合ロジックの参照実装
- `experiments/20260801-controlled-friction-task/prepare-subjects.sh` — ★ 手作業版（退路・D-5）
- `.claude/skills/data-privacy/SKILL.md` — spike-2 が否のときに先に読む
- `.claude/skills/browser-verification/SKILL.md` — Console 操作の前に読む

## 運用メモ
- /reimagine 適用: **No**
- 理由: このタスクは未検証の前提を実測するだけで、設計判断は `20260807-vps-provisioning-automation`
  側で完了している。外れたときの代替も `design.md` に既に書かれており、複数実装案の比較ではない。
