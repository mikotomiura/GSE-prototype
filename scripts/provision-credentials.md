# 課題ページ配布自動化 — 資格情報の取り方と置き場

⚠️★ **このファイルに秘密そのものを書かない。** 置き場と手順だけを書く。
`client_secret.json` / `token.json` は **repo の外**（`~/.config/gse-provision/`）にある。

- 設計の SSOT: `.steering/20260807-vps-provisioning-automation/`（D-2 / D-8）
- spike の記録: `.steering/20260816-provision-spikes/`
- ★ 本文は **2026-08-16 に実際に通した手順**である（画面から書き起こした。記憶で書いていない）

---

## 0. 置き場（★ 先に決める。⚠️ `.gitignore` は最後の網であって置き場ではない）

```
~/.config/gse-provision/        0700
├── client_secret.json          0600  … Cloud Console からダウンロードした物（名前を変えて置く）
├── token.json                  0600  … 初回認可で得るリフレッシュトークン
└── token-issued.json           0600  … ★ 発行時刻の記録（spike-3 の時計）
```

⚠️★ 本リポジトリは Actions 分数の都合で **一時 public にする運用がある**ので、
追跡下に秘密を置くと `g1-submit.json` と同型の事故になる。→ **repo の外に置く。**

★ `.gitignore` にも網は張ってある（2026-08-16 に `git check-ignore` で実測。
`token.json` / `client_secret_*.json` / `credentials.json` / `my_token.json` / `.env.local` /
`experiments/…/token.json` がすべて IGNORED。**陽性対照**として `README.md` / `src/main.tsx` /
`NOTIGNORED.json` が追跡対象のままであることも確認した ＝ 検査が空回りしていない）。

---

## 1. Python 環境

⚠️ この Mac の `python3` は Homebrew 3.14（PEP 668 externally-managed）なので、
素の `pip install` は弾かれる（実測）。★ venv を **repo の外**に作る。

```bash
python3 -m venv ~/.venvs/gse-provision
~/.venvs/gse-provision/bin/python -m pip install -r scripts/requirements-dev.txt
```

バージョンは `scripts/requirements-dev.txt` に固定してある
（`google-api-python-client` / `google-auth-oauthlib` / `pytest`）。

---

## 2. Google Cloud Console（★ 2026-08-16 に通した順）

⚠️ 既存プロジェクト（例: "Default Gemini Project"）の設定を変更しない。**新しく作る。**

1. **プロジェクト作成** — `console.cloud.google.com/projectcreate`
   - 名前 / ID: `gse-provision` ／ 親リソース: **組織なし**
2. **Drive API を有効化** — `console.cloud.google.com/apis/library/drive.googleapis.com`
   - ★ 合格判定は「ステータス: **有効**」＋「API を無効にする」ボタンが出ること
3. **Google Auth Platform を構成** — `console.cloud.google.com/auth/overview` →「開始」
   - アプリ名: `GSE provisioning`／サポートメール・連絡先: 研究者本人
   - 対象: **外部**（⚠️ 「内部」は個人 Gmail では `disabled`。Workspace 専用）
   - ⚠️ 最後に「Google API サービス: ユーザーデータに関するポリシーに同意します」の
     チェックがある。★ **これは研究者本人が押す**（規約への承諾）
4. **スコープ** — `console.cloud.google.com/auth/scopes` →「スコープを追加または削除」
   - フィルタに `https://www.googleapis.com/auth/drive.file` を入れて 1 行だけ選ぶ → Save
   - ★ **合格判定は「保存しました」ではなく、表の中身を数えること**:
     非機密 = `drive.file` の **1 件のみ** / 機密性の高い = 0 件 / 制限付き = 0 件
   - ⚠️★ **実測**: Console 自身が `drive.file` を「**非機密のスコープ**」に分類した
5. **OAuth クライアント** — `console.cloud.google.com/auth/clients/create`
   - 種類: **デスクトップ アプリ**／名前: `gse-provision-cli`
   - ⚠️ 画面に「設定が有効になるまで **5 分から数時間**かかることがあります」と出る。
     ★ 直後の認可が失敗しても、それだけで「否」と判定しない
   - ⚠️★ 作成直後のダイアログを**閉じる前に**「JSON をダウンロード」する
     （閉じるとシークレットを表示・ダウンロードできなくなる、と警告が出る）
6. **公開ステータスを本番へ** — `console.cloud.google.com/auth/audience` →「アプリを公開」
   - ⚠️★ **取り返しの効きにくい操作なので、押す前に研究者の確認を取る**
   - ★ **実測 (2026-08-16)**: 確認ダイアログは出ず、**審査 (verification) を求められなかった**。
     スコープが非機密のみだったため。ボタンは「テストに戻る」に変わる
   - ★ なぜ本番にするか: Stage 2（VPS 常駐の収束器）は長命なリフレッシュトークンが前提。
     テスト中のままだと寿命が短く、Stage 2 の可否を判断できない

### 置き場へ移す

```bash
mkdir -p ~/.config/gse-provision && chmod 700 ~/.config/gse-provision
mv ~/Downloads/client_secret_*.apps.googleusercontent.com.json \
   ~/.config/gse-provision/client_secret.json
chmod 600 ~/.config/gse-provision/client_secret.json
```

★ 中身の確認は **構造だけ**行う（⚠️ 値を画面に出さない）:
トップレベルキーが `installed`（= デスクトップアプリ）／`redirect_uris` が `["http://localhost"]`。

---

## 3. 初回認可（★ ここで spike-3 の時計が始まる）

⚠️ ブラウザの同意画面は**別ウィンドウ**に出る。自動化からは操作できないので、
★ **研究者本人が押す**。

1. アカウントを選ぶ
2. ⚠️ 「このアプリは Google で確認されていません」が出る（審査を通していない本番アプリ）
   → 「詳細」→「(アプリ名)（安全ではないページ）に移動」
3. ★ 権限が「**Google ドライブの特定のファイルの表示、編集、作成、削除**」**1 つだけ**で
   あることを確かめてから「続行」
   ⚠️ それ以外が並んでいたら**押さない**。スコープ設定がずれている証拠

`token.json` は **明示したパスにだけ**書く。

⚠️★ **設計書の訂正 (2026-08-16 実測)**: `.steering/20260807-…/design.md` は
「google-auth の `InstalledAppFlow` は **既定で cwd に `token.json` を書く**」としていたが、
★ これは **公式サンプルコードの挙動であってライブラリの挙動ではない**。
`InstalledAppFlow` 自身はファイルを書かない（追跡下のディレクトリを cwd にして実行し、
`token.json` が生まれないことを実測した）。
→ ⚠️ ただし **結論は変えない**: 書き先は常に明示し、置き場は repo の外に固定する。
  「既定に頼らない」という規律は `allowFileDiscovery` と同じ理由で守る。

---

## ⚠️★ `provision.py` を書くときに必ず入れる門（★ 網ではなく門）

2026-08-16 のセキュリティレビューの指摘。`.gitignore` は**最後の網**であって、
★ 網に穴があれば秘密は追跡下に入る（実際、`authorized_user.json` / `creds.json` /
`service_account.json` / `*.pickle` / `.venv/` に穴があり、同日に塞いだ）。

→ ★ **起動時に、資格情報のパスが repo の中なら落ちる**検査を入れること:

```python
repo_root = Path(__file__).resolve().parents[2]      # ★ 実際の階層に合わせる
cred = Path(cred_path).resolve()
if cred.is_relative_to(repo_root):
    raise SystemExit(
        f"⚠️★ 資格情報が repo の中にあります: {cred}\n"
        "    ★ ~/.config/gse-provision/ へ移してください（一時 public 運用があるため）"
    )
```

⚠️ ★ **folder ID をログ・完了報告・`.steering/` に丸ごと書かない。**
`anyone-with-link` 共有下では `https://drive.google.com/drive/folders/<id>` が
**それ自体アクセス権**（capability URL）である。★ `DriveClient` は既にログで
先頭 6 文字に切っている（`_short`）。CLI の出力も同じ規律にすること。

## 4. 失効したとき

★ `token.json` を消して 3 をやり直す。⚠️ 黙って共有せずに進まない
（`provision.py` は失効を**検出して止まる**設計・`design.md` spike-3）。

⚠️ 退路は消していない: Drive API が使えないときは
`experiments/20260801-controlled-friction-task/prepare-subjects.sh` ＋ 手作業で配れる（D-5）。
