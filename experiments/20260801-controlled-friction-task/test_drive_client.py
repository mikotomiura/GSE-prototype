#!/usr/bin/env python3
"""偽 Drive API での単体テスト。

★ ここの本丸は「**照合が赤なら共有まで進まない**」（`decisions.md` D-4）と
「**止められる**」（D-7）である。⚠️ 順序が逆だと fail-open になる。

⚠️★ **陽性対照を必ず対で置く。** 「共有されなかった」を主張するテストは、
   同じ仕掛けで「共有される」ことも見せないと、
   ★ 「そもそも処理が動いていないだけ」と区別できない
   (memory: silent-failure-in-guard-scripts / browser-verification §2.0)。

⚠️★ **偽 API の忠実性そのものがテスト対象である。** 2026-08-16 のレビューで、
   偽 API が `trashed` とページングを模擬していなかったため、
   `drive_client.py` の該当分岐を**消しても全部緑**になることが分かった。
   → `FakeDrive` は `trashed` を持ち、`q` の `trashed = false` を解釈し、
     `pageSize` / `nextPageToken` でページングする。

実行:
    ~/.venvs/gse-provision/bin/python -m pytest test_drive_client.py -q
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

import pytest

from drive_client import DriveClient, DriveError, FOLDER_MIME
import provision_core as pc

GOOGLE_DOC_MIME = "application/vnd.google-apps.document"


class FakeApiError(RuntimeError):
    """★ 失敗注入用。⚠️ 実 API の例外型に依存しないための独自型。"""


# ============================================================ 偽 Drive API

class _Call:
    def __init__(self, fn):
        self._fn = fn

    def execute(self):
        return self._fn()


class _Files:
    def __init__(self, d):
        self.d = d

    def list(self, q, fields, pageSize=None, pageToken=None, supportsAllDrives=False):
        return _Call(lambda: self.d._list(q, pageSize, pageToken))

    def create(self, body, fields, media_body=None, supportsAllDrives=False):
        return _Call(lambda: self.d._create(body, media_body))

    def update(self, fileId, body, fields=None, supportsAllDrives=False):
        return _Call(lambda: self.d._update(fileId, body))


class _Perms:
    def __init__(self, d):
        self.d = d

    def create(self, fileId, body, fields, sendNotificationEmail=False,
               supportsAllDrives=False):
        return _Call(lambda: self.d._perm_create(fileId, body))

    def list(self, fileId, fields, pageSize=None, pageToken=None,
             supportsAllDrives=False):
        return _Call(lambda: self.d._perm_list(fileId, pageSize, pageToken))

    def delete(self, fileId, permissionId, supportsAllDrives=False):
        return _Call(lambda: self.d._perm_delete(fileId, permissionId))


class FakeDrive:
    """★ Drive の最小の振る舞い。⚠️ spike の「外れた側」と失敗を再現するスイッチを持つ。

    - `convert_html=True`   … 上げた HTML が Google 形式に変換される（spike-4 が否のとき）
    - `return_sha=False`    … `sha256Checksum` が返らない（spike-5 が否のとき）
    - `force_discovery=True`… `allowFileDiscovery` が **True** で作られてしまう（fail-open）
    - `corrupt`             … {name: 実際に格納する bytes} で「化けた」を再現する
    - `page_size`           … ★ ページングを実際に起こす
    - `fail_upload_after`   … N 回目のアップロードで例外（★ 部分アップロード）
    - `fail_perm_create`    … 共有設定だけ失敗
    - `undeletable_perms`   … 外せない権限 ID（継承された共有を模す）
    """

    def __init__(self, convert_html=False, return_sha=True, force_discovery=False,
                 corrupt: dict[str, bytes] | None = None, page_size: int | None = None,
                 fail_upload_after: int | None = None, fail_perm_create=False,
                 undeletable_perms: set[str] | None = None,
                 perm_page_size: int | None = None):
        self.perm_page_size = perm_page_size
        self.store: dict[str, dict] = {}
        self.perms: dict[str, list[dict]] = {}
        self._n = 0
        self.convert_html = convert_html
        self.return_sha = return_sha
        self.force_discovery = force_discovery
        self.corrupt = corrupt or {}
        self.page_size = page_size
        self.fail_upload_after = fail_upload_after
        self.fail_perm_create = fail_perm_create
        self.undeletable_perms = undeletable_perms or set()
        self.uploads = 0

    # -- helpers ---------------------------------------------------------
    def _id(self, prefix="f"):
        self._n += 1
        return f"{prefix}{self._n}"

    def files(self):
        return _Files(self)

    def permissions(self):
        return _Perms(self)

    def seed_folder(self, parent_id: str, name: str) -> str:
        fid = self._id("dir")
        self.store[fid] = {"id": fid, "name": name, "mimeType": FOLDER_MIME,
                           "parents": [parent_id], "trashed": False, "_seq": self._n}
        self.perms[fid] = [{"id": "owner", "type": "user", "role": "owner"}]
        return fid

    def seed_file(self, parent_id: str, name: str, data: bytes,
                  mime="text/html", trashed=False) -> str:
        fid = self._id()
        self.store[fid] = {
            "id": fid, "name": name, "mimeType": mime, "parents": [parent_id],
            "size": str(len(data)),
            "sha256Checksum": hashlib.sha256(data).hexdigest(),
            "trashed": trashed, "_seq": self._n,
        }
        return fid

    def names_in(self, parent_id: str, include_trashed=False) -> list[str]:
        return sorted(f["name"] for f in self.store.values()
                      if parent_id in f.get("parents", [])
                      and (include_trashed or not f.get("trashed")))

    def share_link(self, file_id, role="reader", discovery=False, ptype="anyone",
                   pid=None):
        """★ テスト側から「既に共有されている」状態を作る。"""
        self.perms.setdefault(file_id, []).append({
            "id": pid or self._id("p"), "type": ptype, "role": role,
            "allowFileDiscovery": discovery if ptype == "anyone" else None,
        })

    # -- API -------------------------------------------------------------
    def _list(self, q, page_size=None, page_token=None):
        m = re.search(r"'([^']+)' in parents", q)
        parent = m.group(1)
        want_untrashed = "trashed = false" in q

        rows = []
        for f in self.store.values():
            if parent not in f.get("parents", []):
                continue
            # ⚠️★ クエリの trashed 条件を **実際に解釈する**。
            #    模擬しないと drive_client 側の条件を消しても緑になる。
            if want_untrashed and f.get("trashed"):
                continue
            out = {"id": f["id"], "name": f["name"], "mimeType": f["mimeType"],
                   "trashed": f.get("trashed", False)}
            if "size" in f:
                out["size"] = f["size"]
            if self.return_sha and "sha256Checksum" in f:
                out["sha256Checksum"] = f["sha256Checksum"]
            rows.append(out)

        # ⚠️★ **ID 順に並べない。** 偽 API の ID は `dir1` / `f2` の形なので、
        #    ID 順だとフォルダが必ずファイルより先に来る。★ その偏りがあると
        #    「フォルダを優先して選ぶ」実装を消しても差が出ず、変異が素通りする
        #    （2026-08-16 に実測）。→ **作った順**で返す（実 Drive も ID 順ではない）。
        rows.sort(key=lambda r: self.store[r["id"]]["_seq"])
        # ★ ページング。⚠️ 模擬しないと nextPageToken ループを消しても緑になる。
        size = self.page_size or page_size or 1000
        start = int(page_token) if page_token else 0
        page = rows[start:start + size]
        resp = {"files": page}
        if start + size < len(rows):
            resp["nextPageToken"] = str(start + size)
        return resp

    def _create(self, body, media):
        is_folder = body.get("mimeType") == FOLDER_MIME
        if media is not None:
            self.uploads += 1
            if self.fail_upload_after is not None and self.uploads > self.fail_upload_after:
                raise FakeApiError(f"upload failed (injected) for {body['name']}")
        fid = self._id("dir" if is_folder else "f")
        rec = {"id": fid, "name": body["name"], "mimeType": body.get("mimeType", ""),
               "parents": body.get("parents", []), "trashed": False, "_seq": self._n}
        if media is not None:
            data = self.corrupt.get(body["name"], media["data"])
            if self.convert_html:
                # ★ Google 形式に変換された = size が消える（`verify-drive-upload.py` の判定）
                rec["mimeType"] = GOOGLE_DOC_MIME
            else:
                rec["size"] = str(len(data))
                rec["sha256Checksum"] = hashlib.sha256(data).hexdigest()
        self.store[fid] = rec
        if is_folder:
            self.perms[fid] = [{"id": "owner", "type": "user", "role": "owner"}]
        return {"id": fid}

    def _update(self, fileId, body):
        """★ ゴミ箱へ入れる。⚠️ 完全削除ではないので store から消さない。"""
        if "trashed" in body:
            self.store[fileId]["trashed"] = bool(body["trashed"])
        return {"id": fileId}

    def _perm_create(self, fileId, body):
        if self.fail_perm_create:
            raise FakeApiError("permissions.create failed (injected)")
        pid = self._id("p")
        self.perms.setdefault(fileId, []).append({
            "id": pid, "type": body["type"], "role": body["role"],
            "allowFileDiscovery": True if self.force_discovery
            else body.get("allowFileDiscovery"),
        })
        return {"id": pid}

    def _perm_list(self, fileId, page_size=None, page_token=None):
        """★ 権限もページングする。⚠️ 模擬しないと `list_permissions` の
        ページングループを消しても緑になる（2026-08-16 の cross-review 指摘）。"""
        rows = list(self.perms.get(fileId, []))
        size = self.perm_page_size or page_size or 100
        start = int(page_token) if page_token else 0
        page = rows[start:start + size]
        resp = {"permissions": page}
        if start + size < len(rows):
            resp["nextPageToken"] = str(start + size)
        return resp

    def _perm_delete(self, fileId, permissionId):
        if permissionId in self.undeletable_perms:
            raise FakeApiError(f"cannot delete permission {permissionId} (injected)")
        self.perms[fileId] = [p for p in self.perms.get(fileId, [])
                              if p["id"] != permissionId]
        return {}

    # -- 検査補助 ---------------------------------------------------------
    def anyone_perms(self, file_id):
        return [p for p in self.perms.get(file_id, []) if p["type"] == "anyone"]

    def non_owner_perms(self, file_id):
        return [p for p in self.perms.get(file_id, []) if p["role"] != "owner"]


def fake_media(path: Path):
    """★ `MediaFileUpload` の代わり。⚠️ テストが googleapiclient を要求しないようにする。"""
    return {"data": path.read_bytes()}


# ============================================================ フィクスチャ

def make_pages(tmp_path: Path, n: int = 3, subject: str = "PILOT-spike") -> Path:
    d = tmp_path / subject
    d.mkdir(parents=True, exist_ok=True)
    for i in range(1, n + 1):
        (d / f"block{i:02d}.html").write_text(
            f"<!doctype html><title>block{i:02d}</title><p>課題 {i}</p>\n",
            encoding="utf-8",
        )
    return d


def run(client, local_dir, desired=pc.SHARE, parent="PARENT", subject="PILOT-spike"):
    return pc.reconcile_subject(client, parent, subject, local_dir, desired,
                                media_factory=fake_media)


def kinds(client):
    return [x.split()[0] for x in client.log]


# ============================================================ テスト

# ---------- 1. 幸せな道（★ これが陽性対照になる） ----------

def test_happy_path_uploads_then_shares(tmp_path):
    """★ 正常系: 3 枚上がり、照合が緑で、共有される。

    ⚠️ このテストが緑でないと、下の「共有されない」系のテストは何も証明しない。
    """
    d = make_pages(tmp_path)
    fake = FakeDrive()
    c = DriveClient(service=fake)

    r = run(c, d)

    assert r.state == "ok"
    assert r.shared is True
    assert r.distributable is True
    assert fake.names_in(r.folder_id) == ["block01.html", "block02.html", "block03.html"]
    assert fake.anyone_perms(r.folder_id) == [
        {"id": "p5", "type": "anyone", "role": "reader", "allowFileDiscovery": False}
    ]

    k = kinds(c)
    assert "share" in k, "★ 陽性対照が壊れている（共有まで到達していない）"
    assert k.index("share") > max(i for i, x in enumerate(k) if x == "upload")


def test_idempotent_second_run_writes_nothing(tmp_path):
    """★ 既に正しい状態なら **書き込み 0 回**（冪等）。

    ⚠️ `design.md` は「API 呼び出し 0 回」と書いているが、現状を知るには読む必要がある。
    → ★ ここで縛るのは **writes == 0** である。
    """
    d = make_pages(tmp_path)
    fake = FakeDrive()

    first = DriveClient(service=fake)
    assert run(first, d).distributable is True
    assert first.writes > 0  # ★ 1 回目は書いている（対照）

    second = DriveClient(service=fake)
    r = run(second, d)

    assert r.distributable is True
    assert second.writes == 0, f"⚠️ 2 回目に書き込みが起きた: {second.log}"
    assert second.reads > 0  # ★ 読みはしている（＝ 空回りではない）


# ---------- 2. ★ 本丸: 照合が赤なら共有しない ----------

def test_corrupted_upload_is_not_shared(tmp_path):
    """⚠️★ 上げた中身が化けたら、**共有まで進まない**（D-4 の本丸）。"""
    d = make_pages(tmp_path)
    broken = (d / "block02.html").read_bytes()[:-10]
    fake = FakeDrive(corrupt={"block02.html": broken})
    c = DriveClient(service=fake)

    r = run(c, d)

    assert r.state == "verify_failed"
    assert r.shared is False
    assert r.distributable is False
    assert any("byte 不一致" in p for p in r.problems), r.problems
    assert "share" not in kinds(c), f"⚠️★ 照合が赤なのに共有した: {c.log}"


def test_conversion_to_google_type_is_not_shared(tmp_path):
    """⚠️ Google 形式に変換されたら（size が消えたら）赤。★ spike-4 が否だった場合。"""
    d = make_pages(tmp_path)
    c = DriveClient(service=FakeDrive(convert_html=True))
    r = run(c, d)
    assert r.state == "verify_failed" and r.shared is False
    assert any("変換された" in p for p in r.problems), r.problems
    assert "share" not in kinds(c)


def test_sha_mismatch_with_same_size_is_caught(tmp_path):
    """⚠️★ **byte 数が同じで中身が違う**壊れ方を捕まえる（spike-5 の値打ち）。"""
    d = make_pages(tmp_path)
    original = (d / "block02.html").read_bytes()
    same_len = bytes(b ^ 0x01 for b in original)
    assert len(same_len) == len(original)  # ★ 前提の確認

    c = DriveClient(service=FakeDrive(corrupt={"block02.html": same_len}))
    r = run(c, d)

    assert r.state == "verify_failed" and r.shared is False
    assert any("SHA 不一致" in p for p in r.problems), r.problems


def test_missing_checksum_is_now_fail_closed(tmp_path):
    """⚠️★ `sha256Checksum` が返らない環境は **赤** にする（2026-08-16 に方針変更）。

    ★ 初版は「素通りする」ことを陰性対照として固定していたが、
      spike-5 で「返る」と実測した以上、返らないのは**想定外**である。
      ⚠️ 「黙って照合が弱くなる」ほうが危険（`allowFileDiscovery` の三値と同じ思想）。
    """
    d = make_pages(tmp_path)
    c = DriveClient(service=FakeDrive(return_sha=False))
    r = run(c, d)

    assert r.state == "verify_failed"
    assert r.shared is False
    assert any("SHA 未返却" in p for p in r.problems), r.problems
    assert "share" not in kinds(c)


# ---------- 3. ★ 許可リスト（陰性対照） ----------

@pytest.mark.parametrize("intruder", ["g1-submit.json", "pubkey.txt", ".DS_Store"])
def test_allowlist_rejects_non_pages_without_touching_drive(tmp_path, intruder):
    """⚠️★ 課題ページ以外が混ざっていたら、**Drive を 1 回も叩かずに**落ちる。"""
    d = make_pages(tmp_path)
    (d / intruder).write_text("secret", encoding="utf-8")
    fake = FakeDrive()
    c = DriveClient(service=fake)

    with pytest.raises(pc.ProvisionError) as e:
        run(c, d)

    assert intruder in str(e.value)
    assert c.reads == 0 and c.writes == 0, \
        f"⚠️★ 許可リストで落ちる前に Drive を叩いている: {c.log}"
    assert fake.store == {}


def test_symlink_is_rejected_even_with_a_valid_name(tmp_path):
    """⚠️★ 名前が blockNN.html でも **symlink は弾く**。

    ★ `is_file()` はリンク先を辿るので、名前だけの検査では
      `block03.html -> token.json` が通り、**秘密が公開フォルダへ上がる**
      （2026-08-16 に実測で再現した）。
    """
    d = make_pages(tmp_path, n=2)
    # ⚠️★ 変数名を `secret` にしない。★ `scripts/secrets-filter.sh` の
    #    `(password|passwd|secret|...)[:=]` に一致し、**Codex レビューがブロックされる**
    #    （2026-08-16 の /cross-review で実際に止まった。中身はダミーなのに）。
    link_target = tmp_path / "OUT-OF-ALLOWLIST.txt"
    link_target.write_text("許可リスト外の中身", encoding="utf-8")
    (d / "block03.html").symlink_to(link_target)

    c = DriveClient(service=FakeDrive())
    with pytest.raises(pc.ProvisionError) as e:
        run(c, d)
    assert "シンボリックリンク" in str(e.value)
    assert c.reads == 0 and c.writes == 0


def test_allowlist_accepts_only_pages(tmp_path):
    """★ 陽性対照: 侵入者が居なければ通る（＝ 上のテストが常に赤を返す仕掛けではない）。"""
    d = make_pages(tmp_path)
    assert run(DriveClient(service=FakeDrive()), d).distributable is True


# ---------- 4. ⚠️★ 共有の形（fail-open の番人） ----------

def test_discoverable_share_is_not_recorded_as_shared(tmp_path):
    """⚠️★ `allowFileDiscovery=true` になったら「共有済み」と記録しない。"""
    d = make_pages(tmp_path)
    c = DriveClient(service=FakeDrive(force_discovery=True))
    r = run(c, d)

    assert r.state == "verify_failed"
    assert r.shared is False and r.distributable is False
    assert any("検索可能" in p for p in r.problems), r.problems


@pytest.mark.parametrize("role,discovery,word", [
    ("reader", True, "検索可能"),      # ★ 一般公開（検索から辿れる）
    ("writer", False, "書き換え"),     # ★ 誰でも書き換えられる
])
def test_preexisting_bad_share_is_removed_not_coexisted(tmp_path, role, discovery, word):
    """⚠️★★ **既にある悪い共有**を、良い共有と**併存させない**。

    ★ 2026-08-16 のレビューで見つかった CRITICAL。厳格述語 (`is_link_reader`) を
      「露出しているか」の判定に流用していたため、悪い権限は「未共有」に見え、
      良い権限を足して **併存したまま `distributable=True`** になっていた（実測で再現）。
    """
    d = make_pages(tmp_path, n=2)
    fake = FakeDrive()
    fid = fake.seed_folder("PARENT", "PILOT-spike")
    fake.share_link(fid, role=role, discovery=discovery, pid="bad")

    c = DriveClient(service=fake)
    r = run(c, d)

    # ★ 悪い権限は外されている
    assert not [p for p in fake.perms[fid] if p["id"] == "bad"], \
        f"⚠️★ 悪い権限が残っている: {fake.perms[fid]}"
    # ★ 結果として配れる状態になっているなら、悪い権限が 0 件であること
    if r.distributable:
        assert all(p["role"] == "owner" or
                   (p["type"] == "anyone" and p["role"] == "reader"
                    and p["allowFileDiscovery"] is False)
                   for p in fake.perms[fid]), fake.perms[fid]
    else:
        assert any(word in p for p in r.problems), r.problems


def test_bad_share_is_removed_even_when_content_is_already_correct(tmp_path):
    """⚠️★★ **中身が既に正しい**のに悪い共有が付いている状態を直せること。

    ★ これが CRITICAL を固定する本命のテストである。中身が正しいと差し替え経路を通らないので、
      「悪い共有をまず外す」処理だけが唯一の逃げ道になる。
    ⚠️ 中身が違う状態で試すと、差し替え経路が悪い権限を外してしまい、
      **本命の処理を消しても緑になる**（2026-08-16 の変異テストで実測）。
    """
    d = make_pages(tmp_path, n=2)
    fake = FakeDrive()
    fid = fake.seed_folder("PARENT", "PILOT-spike")
    for p in sorted(d.glob("block*.html")):        # ★ 中身は既に正しい
        fake.seed_file(fid, p.name, p.read_bytes())
    fake.share_link(fid, role="reader", discovery=True, pid="bad")

    c = DriveClient(service=fake)
    r = run(c, d)

    assert not [p for p in fake.perms[fid] if p["id"] == "bad"], \
        f"⚠️★ 検索可能な共有が残ったまま: {fake.perms[fid]}"
    assert "unshare" in kinds(c), f"★ 外していない: {c.log}"
    # ★ 収束すること（⚠️ 外さないと毎周回 verify_failed のまま直らない）
    assert r.distributable is True, r.problems


def test_proper_share_is_removed_before_replacing_content(tmp_path):
    """⚠️★ **正しい共有**が付いた状態で中身を差し替えるときも、先に共有を外す。

    ★ design.md「更新の順序」の本命。⚠️ 「消す → 上げる」の窓で
      被験者が**欠けたブロック集合**を見ないための保証。
    ★ 悪い共有ではなく**正しい共有**で試すこと。悪い共有だと別の処理が外してしまい、
      この順序を消しても緑になる（2026-08-16 の変異テストで実測）。
    """
    d = make_pages(tmp_path, n=2)
    fake = FakeDrive()
    fid = fake.seed_folder("PARENT", "PILOT-spike")
    fake.seed_file(fid, "block01.html", b"<html>old</html>")   # ★ 中身が違う
    fake.share_link(fid, role="reader", discovery=False)       # ★ 共有は正しい形

    c = DriveClient(service=fake)
    r = run(c, d)

    k = kinds(c)
    assert "unshare" in k, f"⚠️★ 正しい共有のときに外していない: {c.log}"
    writes = [i for i, x in enumerate(k) if x in ("trash", "upload")]
    assert writes, c.log
    assert k.index("unshare") < min(writes), \
        f"⚠️★ 差し替えより先に共有を外していない: {c.log}"
    assert r.distributable is True, r.problems


def test_anyone_permission_without_discovery_field_is_a_problem(tmp_path):
    """⚠️★ `allowFileDiscovery` が **返ってこない** `anyone` 権限を合格にしない。

    ★ 三値（True/False/None）で持つ意味はここにある。⚠️ None を False と読み替えると、
      検索可能かどうか分からない共有を「安全だ」と決めつけることになる。
    """
    d = make_pages(tmp_path, n=2)
    fake = FakeDrive()
    fid = fake.seed_folder("PARENT", "PILOT-spike")
    for p in sorted(d.glob("block*.html")):
        fake.seed_file(fid, p.name, p.read_bytes())
    # ★ allowFileDiscovery キーが無い anyone/reader（API が返さなかった状態）
    fake.perms[fid].append({"id": "nodisc", "type": "anyone", "role": "reader"})

    c = DriveClient(service=fake)
    r = run(c, d)

    assert not [p for p in fake.perms[fid] if p["id"] == "nodisc"], \
        f"⚠️★ 判別できない共有が残ったまま: {fake.perms[fid]}"
    # ★ 外したあと**正しく再共有されて収束する**ことまで見る
    #   （⚠️ 外すだけで終わると、毎周回 verify_failed のまま直らない）
    assert r.distributable is True, r.problems


def test_bad_share_is_removed_before_replacing_content(tmp_path):
    """⚠️★ 悪い共有が付いたまま**差し替えに入らない**（D-4 の窓）。"""
    d = make_pages(tmp_path, n=2)
    fake = FakeDrive()
    fid = fake.seed_folder("PARENT", "PILOT-spike")
    fake.seed_file(fid, "block01.html", b"<html>old</html>")  # ★ 中身が違う = 差し替えが要る
    fake.share_link(fid, role="reader", discovery=True, pid="bad")

    c = DriveClient(service=fake)
    run(c, d)

    k = kinds(c)
    assert "unshare" in k, f"★ 共有を外していない: {c.log}"
    writes = [i for i, x in enumerate(k) if x in ("trash", "upload")]
    assert writes, c.log
    assert k.index("unshare") < min(writes), \
        f"⚠️★ 差し替えより先に共有を外していない: {c.log}"


def test_share_also_removes_bad_sharing_on_children(tmp_path):
    """⚠️★★ **子ファイルに直接付いた悪い共有**も外す（`_stop` 側と対）。

    ★ 2026-08-16 の cross-review 指摘。`_stop` は子まで見ているのに `_share` は
      フォルダ自身の権限しか見ていなかった。⚠️ そのため
      「`block01.html` 1 枚だけ第三者が書き換えられる」状態が、
      収束器を何周しても直らないまま `distributable=True` と報告された。
    """
    d = make_pages(tmp_path, n=2)
    fake = FakeDrive()
    fid = fake.seed_folder("PARENT", "PILOT-spike")
    child_ids = {}
    for p in sorted(d.glob("block*.html")):        # ★ 中身は既に正しい
        child_ids[p.name] = fake.seed_file(fid, p.name, p.read_bytes())
    # ⚠️ 1 枚だけに「誰でも書き換えられる」直接権限が付いている
    fake.share_link(child_ids["block01.html"], role="writer", discovery=False, pid="cbad")

    c = DriveClient(service=fake)
    r = run(c, d)

    assert fake.non_owner_perms(child_ids["block01.html"]) == [], \
        f"⚠️★ 子の悪い共有が残ったまま: {fake.perms[child_ids['block01.html']]}"
    assert r.distributable is True, r.problems


def test_inherited_good_share_on_child_is_not_touched(tmp_path):
    """⚠️★★ 子の掃除で、**フォルダから継承した正しい共有**まで消しにいかないこと。

    ★ 2026-08-16 の cross-review で**両者一致**の指摘。子に `unshare_all`（owner 以外を全部）
      を使うと、継承ぶんまで削除対象になる。⚠️ 継承権限は子の側からは消せないので
      `permissions.delete` が失敗し、★ **正当な配布が「外せませんでした」で止まる**。
    → `unshare_problems`（悪い形だけ狙う）で、継承ぶんには触れない。

    ここでは「継承ぶん」を **消せない権限** として模擬する。
    """
    d = make_pages(tmp_path, n=1)
    fake = FakeDrive(undeletable_perms={"inherited"})
    fid = fake.seed_folder("PARENT", "PILOT-spike")
    ch = fake.seed_file(fid, "block01.html", (d / "block01.html").read_bytes())
    # ★ フォルダから継承した「正しい」共有（消せない）
    fake.share_link(ch, role="reader", discovery=False, pid="inherited")
    # ⚠️ それに加えて、直接付いた「悪い」共有
    fake.share_link(ch, role="writer", discovery=False, pid="direct_bad")
    fake.share_link(fid, role="reader", discovery=False)

    c = DriveClient(service=fake)
    r = run(c, d)

    ids = {p["id"] for p in fake.perms[ch]}
    assert "direct_bad" not in ids, f"⚠️ 悪い直接権限が残った: {fake.perms[ch]}"
    assert "inherited" in ids, f"⚠️★ 継承ぶんまで消しにいった: {fake.perms[ch]}"
    assert r.distributable is True, r.problems


def test_child_public_share_is_removed_when_folder_is_not_shared(tmp_path):
    """⚠️★★ 親が未共有なら、子の `anyone/reader` は**継承ではなく直接の公開**として外す。

    ★ 2026-08-16 の追加レビュー指摘。「継承かもしれないから残す」を**親を見ずに**
      無条件でやっていたため、⚠️ 親は未共有なのに `block01.html` 1 枚だけが
      world-readable のまま、**掃除もされず報告にも出ない**状態が残った（実測で再現）。
    """
    d = make_pages(tmp_path, n=1)
    fake = FakeDrive()
    fid = fake.seed_folder("PARENT", "PILOT-spike")          # ★ 親は未共有
    ch = fake.seed_file(fid, "block01.html", (d / "block01.html").read_bytes())
    fake.share_link(ch, role="reader", discovery=False, pid="direct_public")

    c = DriveClient(service=fake)
    r = run(c, d)

    assert not [p for p in fake.perms[ch] if p["id"] == "direct_public"], \
        f"⚠️★ 親が未共有なのに子の公開が残った: {fake.perms[ch]}"
    assert r.distributable is True, r.problems


def test_extra_file_is_unshared_before_being_trashed(tmp_path):
    """⚠️★ 余分をゴミ箱へ入れる前に **共有を外す**。

    ★ ゴミ箱は権限を消さない。⚠️ 外さずに送ると「ゴミ箱にあるが world-readable」＝
      **復元すれば再公開**の物が残り、しかも `verify` の対象から消えるので
      収束器は二度と掃除しない（2026-08-16 のレビュー指摘・実測）。

    ⚠️★ **親を共有済みにしておくこと。** 親が未共有だと `_clean_child_shares` が
      先に同じ権限を外してしまい、★ この防御を消しても緑になる（＝ 別の防御に隠れる）。
      2026-08-16 の変異テストで実測した。
    """
    d = make_pages(tmp_path, n=1)
    fake = FakeDrive()
    fid = fake.seed_folder("PARENT", "PILOT-spike")
    fake.seed_file(fid, "block01.html", (d / "block01.html").read_bytes())
    stray = fake.seed_file(fid, "block09.html", b"<html>other subject</html>")
    # ★ 親は既に正しく共有されている → 子の anyone/reader は「継承かもしれない」と
    #   見逃される。⚠️ だからゴミ箱へ送る直前に外す処理だけが頼りになる。
    fake.share_link(fid, role="reader", discovery=False)
    fake.share_link(stray, role="reader", discovery=False, pid="stray_public")

    c = DriveClient(service=fake)
    r = run(c, d)

    assert r.distributable is True, r.problems
    assert fake.store[stray]["trashed"] is True
    assert fake.non_owner_perms(stray) == [], \
        f"⚠️★ ゴミ箱に入れたが公開が残っている（復元すれば再公開）: {fake.perms[stray]}"


def test_stop_prefers_the_folder_over_a_same_named_file(tmp_path):
    """⚠️ 同名の**ファイル**とフォルダが並んでいたら、`folder_id` はフォルダ側を返す。"""
    d = make_pages(tmp_path, n=1)
    fake = FakeDrive()
    fake.seed_file("PARENT", "PILOT-spike", b"not a folder")
    fid = fake.seed_folder("PARENT", "PILOT-spike")
    fake.share_link(fid, role="reader", discovery=False)

    c = DriveClient(service=fake)
    r = run(c, d, desired=pc.STOP)

    assert r.folder_id == fid, f"★ フォルダでない物を folder_id にした: {r.folder_id}"


def test_stop_always_reports_its_coverage_limit(tmp_path):
    """★ `drive.file` の「見えない子は外せない」限界を **結果に載せる**。

    ⚠️ docstring に書くだけでは運用者に届かない。
    ★ `problems`（赤の理由）ではなく `notes` に置く — 混ぜると呼び出し側が
      「成功＋注記」と「本当の失敗」を区別できない。
    """
    d = make_pages(tmp_path, n=1)
    fake = FakeDrive()
    run(DriveClient(service=fake), d)

    c = DriveClient(service=fake)
    r = run(c, d, desired=pc.STOP)

    assert r.state == "stopped"
    assert any("見えない" in n for n in r.notes), r.notes
    assert r.problems == [], "⚠️ 注記を problems に混ぜている"

    # ★ 陽性対照: フォルダが無いときは注記も付かない（＝ 常に付ける実装ではない）
    empty = run(DriveClient(service=FakeDrive()), d, desired=pc.STOP)
    assert empty.state == "absent" and empty.notes == []


def test_anyone_owner_is_not_treated_as_owner(tmp_path):
    """⚠️★ `type=anyone, role=owner` を「owner だから安全」と読まない。

    ★ 最も広い述語 `is_exposed` の逃げ道を、到達性が不明でも塞ぐ。
    """
    from drive_client import Permission
    p = Permission(id="x", type="anyone", role="owner", allow_file_discovery=None)
    assert p.is_owner is False
    assert p.problem() is not None


def test_repeated_page_token_does_not_hang(tmp_path):
    """⚠️★ 同じ `nextPageToken` が返り続けても**無限ループしない**。

    ★ 偽 API で実測すると 2 秒で 130,494 回読んで止まらなかった。
      ⚠️ VPS 常駐 (Stage 2) では「静かにハングして D-7 の緊急停止が二度と走らない」
      という、この設計が最も嫌う失敗形になる。
    """
    fake = FakeDrive()
    fid = fake.seed_folder("PARENT", "PILOT-spike")

    original = fake._list

    def stuck_list(q, page_size=None, page_token=None):
        resp = original(q, page_size, page_token)
        # ★ 常に同じトークンを返す（⚠️ 偽 API が解釈できる形にしておく。
        #    解釈できない値だとガードより先に偽 API 側が落ち、何を検証したか分からなくなる）
        resp["nextPageToken"] = "0"
        return resp

    fake._list = stuck_list
    c = DriveClient(service=fake)
    with pytest.raises(DriveError) as e:
        c.list_children(fid)
    assert "nextPageToken" in str(e.value)


def test_bad_permission_on_second_page_is_found(tmp_path):
    """⚠️★ 権限が 2 ページに跨っても、**2 ページ目の悪い共有**を見つける。

    ★ 2026-08-16 の cross-review 指摘。`list_children` はページングしているのに
      `list_permissions` は 1 回しか呼んでおらず、`nextPageToken` を要求してすらいなかった。
      ⚠️ 「露出していない」と誤報告する経路＝ D-7（止める）に直結する穴。
    """
    d = make_pages(tmp_path, n=1)
    fake = FakeDrive(perm_page_size=2)          # ★ 2 件ずつ返す
    fid = fake.seed_folder("PARENT", "PILOT-spike")
    fake.seed_file(fid, "block01.html", (d / "block01.html").read_bytes())
    fake.share_link(fid, role="reader", ptype="user", pid="p_a")
    fake.share_link(fid, role="reader", ptype="user", pid="p_b")
    # ⚠️ 3 件目 = 2 ページ目に、検索可能（＝一般公開）の共有が隠れている
    fake.share_link(fid, role="reader", discovery=True, pid="hidden_bad")

    c = DriveClient(service=fake)
    assert len(c.list_permissions(fid)) == 4, "★ 全ページ読めていない（owner 含めて 4 件）"

    r = run(c, d)
    assert not [p for p in fake.perms[fid] if p["id"] == "hidden_bad"], \
        f"⚠️★ 2 ページ目の一般公開を見落とした: {fake.perms[fid]}"
    assert r.distributable is True, r.problems


def test_share_stops_when_child_permission_cannot_be_removed(tmp_path):
    """⚠️ 子の権限が外せないなら、**共有せずに止める**。"""
    d = make_pages(tmp_path, n=1)
    fake = FakeDrive(undeletable_perms={"cstuck"})
    fid = fake.seed_folder("PARENT", "PILOT-spike")
    ch = fake.seed_file(fid, "block01.html", (d / "block01.html").read_bytes())
    fake.share_link(ch, role="writer", pid="cstuck")

    c = DriveClient(service=fake)
    r = run(c, d)

    assert r.distributable is False
    assert any("block01.html" in p for p in r.problems), r.problems


def test_undeletable_permission_stops_instead_of_sharing(tmp_path):
    """⚠️★ 外せない権限（継承など）があったら、**共有せずに止める**。"""
    d = make_pages(tmp_path, n=2)
    fake = FakeDrive(undeletable_perms={"stuck"})
    fid = fake.seed_folder("PARENT", "PILOT-spike")
    fake.share_link(fid, role="writer", pid="stuck")

    c = DriveClient(service=fake)
    r = run(c, d)

    assert r.distributable is False
    assert any("外せません" in p for p in r.problems), r.problems


# ---------- 5. ⚠️★ 「止める」（D-7・共有する側と対） ----------

def test_stop_removes_sharing(tmp_path):
    """⚠️★ 撤回フラグが立った P-ID は **共有が外れた状態へ寄る**。"""
    d = make_pages(tmp_path)
    fake = FakeDrive()

    shared = DriveClient(service=fake)
    r1 = run(shared, d)
    assert r1.shared is True  # ★ 対照: いったん本当に共有されている

    stopper = DriveClient(service=fake)
    r2 = run(stopper, d, desired=pc.STOP)

    assert r2.state == "stopped"
    assert r2.shared is False and r2.distributable is False
    assert fake.non_owner_perms(r1.folder_id) == []


def test_stop_also_removes_user_permissions(tmp_path):
    """⚠️★ `type=user`（誤って個別共有した相手）も外す。

    ★ 初版は `type=anyone` だけを外して「止めた」と名乗っていた。
      design.md の代替案が `type=user` 個別共有なので、⚠️ この経路が入った瞬間に
      「撤回したのに届いている」になる。
    """
    d = make_pages(tmp_path, n=2)
    fake = FakeDrive()
    fid = fake.seed_folder("PARENT", "PILOT-spike")
    fake.share_link(fid, role="reader", ptype="user", pid="someone")

    c = DriveClient(service=fake)
    r = run(c, d, desired=pc.STOP)

    assert r.state == "stopped"
    assert fake.non_owner_perms(fid) == [], fake.perms[fid]


def test_stop_also_removes_sharing_on_children(tmp_path):
    """⚠️★ フォルダ配下の**個別ファイル**に付いた共有も外す。

    ★ 外さないと、STOP 後も**そのファイルは公開されたまま**なのに
      `state=stopped` を返してしまう（フォルダしか読み返していなかったため）。
    """
    d = make_pages(tmp_path, n=2)
    fake = FakeDrive()
    fid = fake.seed_folder("PARENT", "PILOT-spike")
    child = fake.seed_file(fid, "block01.html", b"<html>x</html>")
    fake.share_link(child, role="reader", discovery=False)
    fake.share_link(fid, role="reader", discovery=False)

    c = DriveClient(service=fake)
    r = run(c, d, desired=pc.STOP)

    assert r.state == "stopped", r.problems
    assert fake.non_owner_perms(child) == [], fake.perms[child]


def test_stop_handles_duplicate_folders(tmp_path):
    """⚠️★★ 同名フォルダが 2 つあっても **両方から共有を外す**。

    ★ spike-1 (2026-08-16) で「`drive.file` は手作業で作られた同名フォルダを
      見落として二重に作る」ことが分かっている。⚠️ つまり重複は**例外ではなく
      起こると分かっている状態**であり、ここで落ちると**一切止められない**。
    """
    d = make_pages(tmp_path, n=2)
    fake = FakeDrive()
    a = fake.seed_folder("PARENT", "PILOT-spike")
    b = fake.seed_folder("PARENT", "PILOT-spike")
    fake.share_link(a, role="reader", discovery=False)
    fake.share_link(b, role="reader", discovery=True)

    c = DriveClient(service=fake)
    r = run(c, d, desired=pc.STOP)

    assert fake.non_owner_perms(a) == [], fake.perms[a]
    assert fake.non_owner_perms(b) == [], fake.perms[b]
    assert r.state == "stop_failed"           # ★ 曖昧さは隠さない
    assert any("2 個" in p for p in r.problems), r.problems


def test_share_refuses_when_duplicate_folders(tmp_path):
    """⚠️ 配る側は逆に **止まる**（どちらに上げるか決められないため）。★ STOP と非対称でよい。"""
    d = make_pages(tmp_path, n=1)
    fake = FakeDrive()
    fake.seed_folder("PARENT", "PILOT-spike")
    fake.seed_folder("PARENT", "PILOT-spike")
    with pytest.raises(DriveError) as e:
        run(DriveClient(service=fake), d)
    assert "2 個" in str(e.value)


def test_stop_is_idempotent(tmp_path):
    d = make_pages(tmp_path)
    fake = FakeDrive()
    run(DriveClient(service=fake), d)
    run(DriveClient(service=fake), d, desired=pc.STOP)

    again = DriveClient(service=fake)
    r = run(again, d, desired=pc.STOP)
    assert r.state == "stopped"
    assert again.writes == 0, f"⚠️ 既に止まっているのに書き込んだ: {again.log}"


def test_stop_on_absent_folder_is_not_an_error(tmp_path):
    d = make_pages(tmp_path)
    c = DriveClient(service=FakeDrive())
    r = run(c, d, desired=pc.STOP)
    assert r.state == "absent" and r.shared is False


# ---------- 6. ⚠️★ 失敗注入（設計書のテスト戦略にあって未実装だった） ----------

def test_partial_upload_leaves_nothing_shared(tmp_path):
    """⚠️★ 途中でアップロードが失敗したら、**共有が残っていない**こと。

    ★ 「削除成功 → アップロード失敗」の窓で被験者が欠けたブロック集合を見ないための保証。
    """
    d = make_pages(tmp_path, n=4)
    fake = FakeDrive(fail_upload_after=2)
    c = DriveClient(service=fake)

    with pytest.raises(Exception):
        run(c, d)

    folders = [f for f in fake.store.values() if f["mimeType"] == FOLDER_MIME]
    assert folders
    for f in folders:
        assert fake.non_owner_perms(f["id"]) == [], \
            f"⚠️★ 失敗したのに共有が残っている: {fake.perms[f['id']]}"


def test_recovers_on_next_round_after_upload_failure(tmp_path):
    """★ 次の周回で回復する（⚠️ 収束器なので途中で落ちても寄れること）。"""
    d = make_pages(tmp_path, n=4)
    fake = FakeDrive(fail_upload_after=2)
    with pytest.raises(Exception):
        run(DriveClient(service=fake), d)

    fake.fail_upload_after = None          # ★ 障害が去った
    c = DriveClient(service=fake)
    r = run(c, d)

    assert r.distributable is True, r.problems
    assert fake.names_in(r.folder_id) == [f"block{i:02d}.html" for i in range(1, 5)]


def test_permission_failure_leaves_nothing_shared(tmp_path):
    """⚠️ 共有設定だけ失敗したとき、**何も共有されていない**こと。

    ⚠️★ 初版はアサーションを `with pytest.raises(...)` の **中** に書いていた。
      例外は代入の時点で飛ぶので、★ 後続の `assert` には**絶対に到達しない**
      （＝ 何も証明していないテストだった）。2026-08-16 の cross-review 指摘。
    → アサーションは必ず `with` の **外** に置く。
    """
    d = make_pages(tmp_path, n=2)
    fake = FakeDrive(fail_perm_create=True)
    c = DriveClient(service=fake)

    with pytest.raises(FakeApiError):
        run(c, d)

    folders = [f for f in fake.store.values() if f["mimeType"] == FOLDER_MIME]
    assert folders, "★ フォルダすら作られていないなら、この検査は空回りしている"
    for f in folders:
        assert fake.non_owner_perms(f["id"]) == [], \
            f"⚠️★ 共有に失敗したのに権限が残っている: {fake.perms[f['id']]}"


# ---------- 7. ⚠️★ 偽 API の忠実性（ゴミ箱・ページング） ----------

def test_trashed_files_are_not_counted_as_present(tmp_path):
    """⚠️★ ゴミ箱の残骸を「まだある」と読まない。

    ★ このテストが無いと `drive_client` の `trashed = false` を消しても緑になる
      （2026-08-16 のレビューで実測された穴）。
    """
    d = make_pages(tmp_path, n=2)
    fake = FakeDrive()
    fid = fake.seed_folder("PARENT", "PILOT-spike")
    # ⚠️★ ゴミ箱の中身は手元と**違う**ものにする。
    #    ★ 正しい中身を入れると、見えても見えなくても結果が同じになり、
    #      ゴミ箱条件を消しても緑になる（2026-08-16 の変異テストで実測）。
    fake.seed_file(fid, "block01.html", "<html>ゴミ箱の古い版</html>".encode("utf-8"),
                   trashed=True)

    c = DriveClient(service=fake)
    r = run(c, d)

    assert r.distributable is True, r.problems
    live = [f for f in fake.store.values()
            if fid in f.get("parents", []) and not f["trashed"]]
    assert sorted(f["name"] for f in live) == ["block01.html", "block02.html"]
    # ★ ゴミ箱の物は触られていない（＝ 見えていない）
    trashed = [f for f in fake.store.values()
               if fid in f.get("parents", []) and f["trashed"]]
    assert len(trashed) == 1


def test_trash_does_not_destroy_the_file(tmp_path):
    """⚠️★ 余分は**ゴミ箱へ**入れる（完全削除しない）。★ 取り返しを残す。"""
    d = make_pages(tmp_path, n=1)
    fake = FakeDrive()
    fid = fake.seed_folder("PARENT", "PILOT-spike")
    stray = fake.seed_file(fid, "block09.html", b"<html>other</html>")

    c = DriveClient(service=fake)
    r = run(c, d)

    assert r.distributable is True
    assert stray in fake.store, "⚠️★ 完全削除された（取り返しがつかない）"
    assert fake.store[stray]["trashed"] is True
    assert "trash" in kinds(c)


def test_listing_spans_multiple_pages(tmp_path):
    """⚠️★ 一覧が 2 ページに跨っても全件返る。

    ★ このテストが無いと `nextPageToken` ループを消しても緑になる。
      ⚠️ 打ち切ると verify が「欠落」と誤判定し、**既にある物を再アップロードして重複を作る**。
    """
    d = make_pages(tmp_path, n=5)
    fake = FakeDrive(page_size=2)          # ★ 5 件を 2 件ずつ = 3 ページ
    fid = fake.seed_folder("PARENT", "PILOT-spike")
    for p in sorted(d.glob("block*.html")):
        fake.seed_file(fid, p.name, p.read_bytes())

    c = DriveClient(service=fake)
    assert len(c.list_children(fid)) == 5

    r = run(c, d)
    assert r.distributable is True
    assert c.writes == 1, f"⚠️★ 既にある物を上げ直している（＝一覧が打ち切られた）: {c.log}"


# ---------- 8. ★ 入力そのものの検査 ----------

@pytest.mark.parametrize("bad", ["../../P099", "P99", "PILOT-../x", "", "p015", "P015 "])
def test_subject_name_is_validated(tmp_path, bad):
    """⚠️★ 被験者 ID の形を Python 側でも検査する（shell 版と同じ規則）。

    ★ 検査が無いと `subject="../../P099"` がフォルダ名になり、
      `provision.py` が `pages/<subject>` を組み立てた瞬間にパストラバーサルへ昇格する。
    """
    d = make_pages(tmp_path, n=1)
    c = DriveClient(service=FakeDrive())
    with pytest.raises(pc.ProvisionError) as e:
        run(c, d, subject=bad)
    assert "被験者 ID" in str(e.value)
    assert c.reads == 0 and c.writes == 0


@pytest.mark.parametrize("good", ["P015", "P001", "PILOT-win", "PILOT-spike"])
def test_valid_subject_names_pass(tmp_path, good):
    """★ 陽性対照: 正しい形は通る（＝ 上の検査が全部弾く空回りではない）。"""
    d = make_pages(tmp_path, n=1, subject=good)
    assert run(DriveClient(service=FakeDrive()), d, subject=good).distributable is True


def test_folder_id_is_validated_before_going_into_the_query(tmp_path):
    """⚠️★ クエリに素で埋める ID を検査する。

    ★ 実測: `parent_id="X' or name contains 'a"` で q が壊れ、**意図より広い一覧**が返る。
      ⚠️ その広い集合に対して差し替え・ゴミ箱送りが走る。
    """
    d = make_pages(tmp_path, n=1)
    c = DriveClient(service=FakeDrive())
    with pytest.raises(DriveError) as e:
        run(c, d, parent="X' or name contains 'a")
    assert "形が不正" in str(e.value)


def test_same_named_file_is_not_treated_as_folder(tmp_path):
    """⚠️ 親の下に P-ID と同名の **ファイル** があったら、フォルダとして扱わない。"""
    d = make_pages(tmp_path, n=1)
    fake = FakeDrive()
    fake.seed_file("PARENT", "PILOT-spike", b"not a folder")
    with pytest.raises(DriveError) as e:
        run(DriveClient(service=fake), d)
    assert "フォルダではありません" in str(e.value)


def test_subfolder_inside_subject_folder_stops_instead_of_deleting(tmp_path):
    """⚠️★ 被験者フォルダの下にフォルダがあったら、**消さずに止める**。

    ★ 研究者が置いた `提出物/` や被験者がアップロードした物を、
      配下ごと取り返しなく消さないため。
    """
    d = make_pages(tmp_path, n=1)
    fake = FakeDrive()
    fid = fake.seed_folder("PARENT", "PILOT-spike")
    sub = fake.seed_folder(fid, "提出物")
    fake.seed_file(sub, "大事なもの.txt", b"keep me")

    c = DriveClient(service=fake)
    r = run(c, d)

    assert r.distributable is False
    assert any("フォルダがあります" in p for p in r.problems), r.problems
    assert fake.store[sub]["trashed"] is False, "⚠️★ フォルダを消した"


def test_empty_directory_is_refused(tmp_path):
    d = tmp_path / "PILOT-spike"
    d.mkdir()
    c = DriveClient(service=FakeDrive())
    with pytest.raises(pc.ProvisionError):
        run(c, d)
    assert c.reads == 0 and c.writes == 0


def test_bad_desired_state_is_refused(tmp_path):
    d = make_pages(tmp_path, n=1)
    with pytest.raises(pc.ProvisionError):
        run(DriveClient(service=FakeDrive()), d, desired="publish")


# ---------- 9. ★ verify() 単体 ----------

def test_verify_reports_extra_and_missing():
    """★ ⚠️ `verify-drive-upload.py` と同じ語で問題を出す。"""
    from drive_client import DriveFile
    manifest = {"block01.html": (10, "a" * 64), "block02.html": (20, "b" * 64)}
    listing = [
        DriveFile(id="1", name="block01.html", mime_type="text/html", size=10,
                  sha256="a" * 64),
        DriveFile(id="9", name="pubkey.txt", mime_type="text/plain", size=5,
                  sha256="c" * 64),
    ]
    problems = pc.verify(manifest, listing)
    assert any("欠落" in p and "block02.html" in p for p in problems)
    assert any("余分" in p and "pubkey.txt" in p for p in problems)


def test_log_does_not_contain_full_folder_ids():
    """⚠️★ folder ID は共有リンクそのもの（capability URL）。ログに丸ごと載せない。

    ★ 実 Drive の ID の長さで試す（2026-08-16 に実測した実物は 33 文字）。
      ⚠️ 偽 API の短い ID (`dir1`) で試すと、切り詰めが効いていなくても通ってしまう。
    """
    fake = FakeDrive()
    real_len_id = "1Y3ABCDEFGHIJKLMNOPQRSTUVWXYZ0123"   # ★ 33 文字（実物と同じ長さ）
    assert len(real_len_id) == 33
    fake.perms[real_len_id] = [{"id": "owner", "type": "user", "role": "owner"}]
    fake.store[real_len_id] = {"id": real_len_id, "name": "PILOT-spike",
                               "mimeType": FOLDER_MIME, "parents": ["PARENT"],
                               "trashed": False, "_seq": 0}

    c = DriveClient(service=fake)
    c.share_link_reader(real_len_id)
    c.trash_file(real_len_id)
    c.create_folder(real_len_id, "PILOT-spike")

    joined = " ".join(c.log)
    assert real_len_id not in joined, c.log
    assert "…" in joined, c.log
