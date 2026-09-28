# 研究者の手順 — O1 受け取りフォルダの P-ID 分け（2026-09-28）

⚠️ **O1 を配る前に行う。** 関数セレクタは表示を信用しない（押す直前に読み直す）。

1. **台帳のプロジェクト**（`GSE_O1_ledger` 等）に新しい `Form_O1/GSE_O1_Ledger.gs` を貼って保存 → リロードして実体を確認。
   `o1LedgerCheck()` を実行し、エラーなく「O1 の形 / 対象外 / 走査の所要」が出ることを確かめる（読み取りのみ）。
2. **受け口のプロジェクト**（`GSE_O1_submit`）に新しい `Form_O1/GSE_O1_Submit.gs` を貼って保存 → リロードして実体を確認。
   `checkSubmitConfig()` で `✅`。⚠️ 初回の実行で **権限の再承認**を求められる可能性がある（`createFolder`・`LockService`）。
   「デプロイを管理」→ 既存デプロイを編集 → **新バージョン**（⚠️ `/exec` URL を変えない）。
3. **合成ファイルで 1 本通す**（⚠️ 実験用の P-ID `P999`）。★ シークレットはコマンドラインに書かず、
   手元の `Form_O1/o1_submit.json`（git 対象外）から読む（シェル履歴・プロセス一覧に残さない）:
   ```bash
   python3 - <<'PY'
   import json, base64, urllib.request
   c = json.load(open("Form_O1/o1_submit.json"))
   body = json.dumps({"secret": c["secret"], "name": "P999_o1day01_gse_o1_20260928_120000.age",
                      "b64": base64.b64encode(b"synthetic-p999").decode()}).encode()
   req = urllib.request.Request(c["endpoint"], data=body, headers={"Content-Type": "application/json"})
   print(urllib.request.urlopen(req, timeout=120).read().decode())
   PY
   ```
   → `{"ok":true,"saved":"P999_o1day01_…","duplicate":false,…}` が返ること。受け取りフォルダに `P999/` ができ、
   その中に入ること。**直下に入らないこと。**
4. 台帳で `o1LedgerRun()` を 1 回 → 「O1 受領台帳」に 1 行増えること。
5. 片付け: `P999/` フォルダをごみ箱へ → **その直後に `o1LedgerCheck()`** を実行し、P999 のファイルが数えられていないこと
   （★ 実 Drive で「ごみ箱のフォルダを列挙が返すか／中のファイルが `isTrashed` になるか」の裏を取る。偽物では決め打ち）。
   → ごみ箱から完全に削除。台帳の該当行は A-14 の tombstone（P-ID・ファイル名・日番号・開始を空・形式 `削除済`）。
   「O1 途絶」は次の実行で消える。
6. 運用: 「O1 途絶」のバナーや通知に **「走査打切り」が続けて出たら**、受け取りフォルダに見覚えのない P-ID フォルダ・空フォルダが
   大量にできていないかを見る（シークレットが漏れた兆候）。片付けたうえでシークレットの入れ替えを検討する。
