#!/usr/bin/env python3
"""Drive API v3 の薄いラッパ。

★ ここは **Drive を叩くことだけ** を担う。「何を上げてよいか」「どの順でやるか」は
`provision_core.py` が持つ。⚠️ 判断をここに混ぜない（テストできる形が崩れる）。

設計の SSOT: `.steering/20260807-vps-provisioning-automation/design.md`
spike:        `.steering/20260816-provision-spikes/`

⚠️★ 使うスコープは `drive.file` **のみ**（非機微）。
   「このアプリが作った・開いたファイルだけ」に限られるので、
   資格情報が漏れても研究者の Drive 全体は読まれない（2026-08-16 に実測）。

★ `service` は注入する。⚠️ ここで資格情報を読みに行かない
  （偽 API での単体テストが成立しなくなるため）。

## ⚠️★★ 共有の述語は 2 つある（2026-08-16 のレビューで直した最重要点）

初版は `is_link_shared`（＝ **正しく**共有されているか）1 つしか持たず、
それを「**露出しているか**」の判定にも流用していた。⚠️ 結果、
`allowFileDiscovery=true` や `anyone/writer` のような**間違った形の共有**は
「未共有」に見え、

  1. 差し替えの前に**共有が外されない**（D-4 の窓が開く）
  2. 良い権限を足すと**悪い権限と併存したまま「配ってよい」**と判定される

の 2 つが同時に起きた（実測で再現）。→ ★ **役割で述語を分ける**:

| 述語 | 意味 | 使う場所 |
|---|---|---|
| `is_link_shared` | **厳格**: 「リンクを知っている全員（閲覧者）」が付いているか | 「配ってよいか」の記録 |
| `is_exposed` | **広い**: owner 以外の権限が 1 つでもあるか | 差し替え前の判定・STOP の読み返し |
| `sharing_problems` | 悪い形の共有の一覧 | 止める理由の説明 |

⚠️ **迷ったら広い側に倒す。** 「露出しているかもしれない」を「していない」と読むと fail-open になる。
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from pathlib import Path

FOLDER_MIME = "application/vnd.google-apps.folder"
HTML_MIME = "text/html"

# ★ list で必ず要求するフィールド。
#   ⚠️ `size` は Google 形式に変換されると **消える**。消えていること自体が
#      「別物になった」の証拠なので、黙って補わない（`verify-drive-upload.py` と同じ扱い）。
#   ★ `sha256Checksum` は 2026-08-16 の spike-5 で **返ることを実測**した。
LIST_FIELDS = "files(id,name,mimeType,size,sha256Checksum,trashed),nextPageToken"

# ⚠️★ Drive のクエリに素で埋める値を検査する。
#   実測: `parent_id="X' or name contains 'a"` を渡すと q が壊れ、
#   **意図より広い一覧**が返る（＝ 削除・差し替えがその広い集合に及ぶ）。
#   ★ Drive の file ID は英数と `-` `_` のみ。`root` は別名として認める。
_ID_RE = re.compile(r"^[A-Za-z0-9_-]+$")

# ⚠️★ ページングの安全装置。同じ `nextPageToken` が返り続けると**無限ループ**する
#   （偽 API で実測: 2 秒で 130,494 回読んだ）。★ 攻撃者が誘発できる経路は無いが、
#   VPS 常駐 (Stage 2) では「静かにハングして D-7 の緊急停止が二度と走らない」という、
#   この設計が最も嫌う失敗形になる。→ 同一トークンで落とし、ページ数にも上限を置く。
_MAX_PAGES = 200


def _next_page(resp: dict, seen: set[str], what: str) -> str | None:
    token = resp.get("nextPageToken")
    if not token:
        return None
    if token in seen:
        raise DriveError(
            f"⚠️★ {what}: 同じ nextPageToken が繰り返し返りました。"
            "★ 無限ループを避けるため止めます"
        )
    if len(seen) >= _MAX_PAGES:
        raise DriveError(
            f"⚠️★ {what}: ページ数が上限 ({_MAX_PAGES}) を超えました。★ 止めます"
        )
    seen.add(token)
    return token


class DriveError(RuntimeError):
    """Drive 側の想定外。⚠️ 握りつぶさず呼び出し元へ伝播させる。"""


def _check_id(file_id: str, what: str = "file_id") -> str:
    if not isinstance(file_id, str) or not _ID_RE.fullmatch(file_id):
        raise DriveError(
            f"⚠️★ {what} の形が不正です: {file_id!r}"
            "（★ Drive の ID は英数と - _ のみ。クエリに埋める前に止めます）"
        )
    return file_id


@dataclass
class DriveFile:
    """list が返す 1 件。★ 生 dict を持ち回らないための最小の型。"""

    id: str
    name: str
    mime_type: str
    size: int | None
    sha256: str | None
    trashed: bool = False

    @property
    def is_folder(self) -> bool:
        return self.mime_type == FOLDER_MIME

    @property
    def converted_to_google_type(self) -> bool:
        """★ Google 形式に変換されてしまったか。

        ⚠️ 判定は「`size` が無い」で行う（`verify-drive-upload.py` と同じ）。
        ★ mimeType だけを見ない: 変換の有無は **中身が別物になったか** の話であり、
          サイズの消失がその一次的な証拠である。
        """
        return not self.is_folder and self.size is None

    @classmethod
    def from_api(cls, raw: dict) -> "DriveFile":
        size = raw.get("size")
        return cls(
            id=raw["id"],
            name=raw.get("name", ""),
            mime_type=raw.get("mimeType", ""),
            size=int(size) if size is not None else None,
            sha256=raw.get("sha256Checksum"),
            trashed=bool(raw.get("trashed", False)),
        )


@dataclass
class Permission:
    id: str
    type: str
    role: str
    # ⚠️★ API が返さないことがあるので **三値** で持つ (True / False / None)。
    #   ★ None を False と読み替えない。「読み返して確かめる」が成立しなくなる。
    allow_file_discovery: bool | None = None

    @classmethod
    def from_api(cls, raw: dict) -> "Permission":
        return cls(
            id=raw["id"],
            type=raw.get("type", ""),
            role=raw.get("role", ""),
            allow_file_discovery=raw.get("allowFileDiscovery"),
        )

    @property
    def is_owner(self) -> bool:
        """⚠️★ `role` だけでなく `type` も見る。

        ★ `role` だけだと `type=anyone, role=owner` が「owner だから安全」と読まれ、
        **最も広い述語 `is_exposed` の逃げ道**になる（2026-08-16 のレビュー指摘）。
        ⚠️ Drive v3 でその組み合わせを作れるかは未確認だが、
        ★ **fail-open 側の逃げ道は到達性が不明でも塞ぐ**。
        """
        return self.type == "user" and self.role == "owner"

    @property
    def is_link_reader(self) -> bool:
        """★ **厳格側**: 「リンクを知っている全員（閲覧者）」であることの判定。

        ⚠️ `allow_file_discovery` が **False であることを要求する**。
        ★ None（API が返さなかった）を合格にしない — 暗黙の既定に fail-open 側を委ねない。
        """
        return (
            self.type == "anyone"
            and self.role == "reader"
            and self.allow_file_discovery is False
        )

    def problem(self) -> str | None:
        """⚠️ この権限が「配ってよい状態」を壊しているなら、その説明を返す。

        ★ owner は正常。厳格条件を満たす `anyone/reader` も正常。それ以外は全部問題。
        """
        if self.is_owner or self.is_link_reader:
            return None
        if self.type == "anyone" and self.allow_file_discovery is not False:
            return (
                f"⚠️★ 検索可能な共有が付いています (id={self.id}, role={self.role}, "
                f"allowFileDiscovery={self.allow_file_discovery})。"
                "★ これは一般公開であり、全被験者の割付が検索から辿れます"
            )
        if self.type == "anyone":
            return (
                f"⚠️★ 閲覧者以外の一般共有が付いています (id={self.id}, role={self.role})。"
                "★ リンクを知る全員が課題ページを書き換えられます"
            )
        return (
            f"⚠️ owner 以外の権限が付いています (id={self.id}, type={self.type}, "
            f"role={self.role})。★ 誰に配られているかを人が確かめてください"
        )


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


@dataclass
class DriveClient:
    """★ googleapiclient の `service` を注入して使う薄いラッパ。

    ⚠️ 呼び出し回数を数える (`reads` / `writes`)。理由は 2 つ:
      1. 収束器の冪等（既に正しい状態なら **書き込み 0 回**）をテストで縛るため
      2. クォータを測るときの実測値になるため

    ★ `design.md` は冪等の条件を「API 呼び出しが 0 回」と書いているが、
      ⚠️ **現状を知るには読まなければならない**ので、厳密には
      「**書き込み**が 0 回」である。ここではその通りに数える。
    """

    service: object
    reads: int = 0
    writes: int = 0
    # ★ 何をしたかの記録。⚠️ 完了報告で「操作した」と言う根拠にする。
    #   ⚠️★ ID は共有リンクそのもの（capability URL）なので **先頭 6 文字に切る**。
    log: list[str] = field(default_factory=list)

    @staticmethod
    def _short(file_id: str) -> str:
        """⚠️★ folder ID は `https://drive.google.com/drive/folders/<id>` そのもの。

        ★ ログや steering に丸ごと載ると、一時 public のタイミングで
        課題ページが誰でも開ける。→ 先頭だけ残す。
        """
        return f"{file_id[:6]}…" if len(file_id) > 6 else file_id

    # ------------------------------------------------------------------ 読み

    def list_children(self, folder_id: str) -> list[DriveFile]:
        """★ ゴミ箱に入っていない直下の子だけを返す。

        ⚠️ `trashed=false` を **クエリに書く**。ゴミ箱の残骸を「まだある」と読むと、
        ★ 消したはずのページを「上がっている」と誤判定する。
        ⚠️ クエリを信用せず、返ってきた側でも `trashed` を落とす（二重の網）。
        """
        _check_id(folder_id, "folder_id")
        out: list[DriveFile] = []
        page_token = None
        seen: set[str] = set()
        while True:
            self.reads += 1
            resp = (
                self.service.files()
                .list(
                    q=f"'{folder_id}' in parents and trashed = false",
                    fields=LIST_FIELDS,
                    pageSize=1000,
                    pageToken=page_token,
                    supportsAllDrives=False,
                )
                .execute()
            )
            for raw in resp.get("files", []):
                f = DriveFile.from_api(raw)
                if not f.trashed:
                    out.append(f)
            page_token = _next_page(resp, seen, "files.list")
            if not page_token:
                break
        return out

    def find_children(self, parent_id: str, name: str) -> list[DriveFile]:
        """★ 名前が一致する子を **すべて** 返す。

        ⚠️★ 同名は実際に起こりうる: `drive.file` は「アプリが作っていない物」が
        見えないので、手作業で作られた同名フォルダを見落として二重に作る
        （2026-08-16 に実測した非対称）。→ 曖昧さを**隠さずに返す**。
        """
        return [f for f in self.list_children(parent_id) if f.name == name]

    def find_child_folder(self, parent_id: str, name: str) -> DriveFile | None:
        """★ 名前でフォルダを 1 つだけ引く。⚠️ 曖昧なら **選ばずに落とす**。

        Drive は同名を許すので、黙って先頭を取ると
        ⚠️ 「どっちに上げたか分からないフォルダ」が静かに増える。
        ⚠️ 同名の **ファイル**（フォルダでない物）も拒否する。
        """
        matches = self.find_children(parent_id, name)
        if not matches:
            return None
        if len(matches) > 1:
            raise DriveError(
                f"'{name}' が親 {self._short(parent_id)} の下に {len(matches)} 個あります。"
                "★ どれに上げるべきか決められないので止めます（Drive の画面で整理してください）"
            )
        only = matches[0]
        if not only.is_folder:
            raise DriveError(
                f"'{name}' はフォルダではありません (mimeType={only.mime_type})。"
                "★ 同名のファイルをフォルダとして扱わないために止めます"
            )
        return only

    def list_permissions(self, file_id: str) -> list[Permission]:
        """★ 権限を **全ページ** 返す。

        ⚠️★ 2026-08-16 の cross-review 指摘。初版はページングが無く、
        `nextPageToken` をフィールドに要求してすらいなかった。
        ★ `list_children` は明示的にループしているのに対称性が崩れていた。
        → 権限が 1 ページを超えると、**2 ページ目以降の悪い共有を見落とし**、
          `is_exposed` / `sharing_problems` / `unshare_all` が
          ⚠️「露出していない」と誤って報告する（D-7 の「止める」に直結する穴）。
        """
        _check_id(file_id, "file_id")
        out: list[Permission] = []
        page_token = None
        seen: set[str] = set()
        while True:
            self.reads += 1
            resp = (
                self.service.permissions()
                .list(
                    fileId=file_id,
                    fields=("permissions(id,type,role,allowFileDiscovery),"
                            "nextPageToken"),
                    pageSize=100,
                    pageToken=page_token,
                    supportsAllDrives=False,
                )
                .execute()
            )
            out.extend(Permission.from_api(p) for p in resp.get("permissions", []))
            page_token = _next_page(resp, seen, "permissions.list")
            if not page_token:
                break
        return out

    def is_link_shared(self, file_id: str) -> bool:
        """★ **厳格側**: 「リンクを知っている全員（閲覧者）」が付いているか。

        ⚠️ これは「露出していないか」の判定に使ってはならない（冒頭の表を参照）。
        """
        return any(p.is_link_reader for p in self.list_permissions(file_id))

    def is_exposed(self, file_id: str) -> bool:
        """★ **広い側**: owner 以外の権限が 1 つでもあるか。

        ⚠️ 差し替え前に共有を外すかどうか・STOP が完了したかどうかは **こちら**で見る。
        """
        return any(not p.is_owner for p in self.list_permissions(file_id))

    def sharing_problems(self, file_id: str) -> list[str]:
        """⚠️ 「配ってよい状態」を壊している権限の説明を全部返す（空なら健全）。"""
        return [msg for p in self.list_permissions(file_id)
                if (msg := p.problem()) is not None]

    # ------------------------------------------------------------- 書き（作る）

    def create_folder(self, parent_id: str, name: str) -> str:
        _check_id(parent_id, "parent_id")
        self.writes += 1
        self.log.append(f"create_folder parent={self._short(parent_id)} name={name}")
        resp = (
            self.service.files()
            .create(
                body={"name": name, "mimeType": FOLDER_MIME, "parents": [parent_id]},
                fields="id",
                supportsAllDrives=False,
            )
            .execute()
        )
        return resp["id"]

    def upload_html(self, parent_id: str, path: Path, media_factory=None) -> str:
        """★ HTML を **text/html のまま** 上げる。

        ⚠️ `media_factory` は注入できるようにしてある（偽 API のテストで
        `MediaFileUpload` の実体を要求しないため）。
        """
        _check_id(parent_id, "parent_id")
        media = (media_factory or _default_media)(path)
        self.writes += 1
        self.log.append(f"upload parent={self._short(parent_id)} name={path.name}")
        resp = (
            self.service.files()
            .create(
                body={"name": path.name, "parents": [parent_id], "mimeType": HTML_MIME},
                media_body=media,
                fields="id",
                supportsAllDrives=False,
            )
            .execute()
        )
        return resp["id"]

    def trash_file(self, file_id: str) -> None:
        """⚠️★ **ゴミ箱へ入れる**（完全削除しない）。

        ★ `files.delete` は Drive v3 では **ゴミ箱を経由せず即座に消し、
        対象がフォルダなら配下ごと消える**。⚠️ 手作業版 (Drive MCP) には削除ツールが
        そもそも無かったので、これは自動化が新しく持ち込む破壊力である。
        → `design.md`「Drive の更新・削除は取り返しがつきにくいので窓を作らない」に
          合わせ、**取り返しが効く形**にする。
        """
        _check_id(file_id, "file_id")
        self.writes += 1
        self.log.append(f"trash {self._short(file_id)}")
        self.service.files().update(
            fileId=file_id, body={"trashed": True}, fields="id",
            supportsAllDrives=False,
        ).execute()

    # ------------------------------------------------------------- 書き（共有）

    def share_link_reader(self, file_id: str) -> str:
        """★ 「リンクを知っている全員（閲覧者）」にする。

        ⚠️★ `allowFileDiscovery=False` を **明示** する。
        Drive v3 の既定は False だが、★ fail-open 側の性質を API の暗黙既定に依存させない。
        True になれば検索可能＝一般公開になり、⚠️ 全被験者の割付が検索から辿れる。
        """
        _check_id(file_id, "file_id")
        self.writes += 1
        self.log.append(f"share {self._short(file_id)}")
        resp = (
            self.service.permissions()
            .create(
                fileId=file_id,
                body={"type": "anyone", "role": "reader", "allowFileDiscovery": False},
                fields="id",
                sendNotificationEmail=False,
                supportsAllDrives=False,
            )
            .execute()
        )
        return resp["id"]

    def _delete_perms(self, file_id: str, targets: list[Permission]
                      ) -> tuple[int, list[str]]:
        removed = 0
        stuck: list[str] = []
        for p in targets:
            self.writes += 1
            self.log.append(f"unshare {self._short(file_id)} perm={p.id}")
            try:
                self.service.permissions().delete(
                    fileId=file_id, permissionId=p.id, supportsAllDrives=False
                ).execute()
                removed += 1
            except Exception as e:  # noqa: BLE001 — API 例外の型は環境で変わる
                stuck.append(
                    f"⚠️★ 権限を外せませんでした (id={p.id}, type={p.type}, "
                    f"role={p.role}): {type(e).__name__}. "
                    "★ 継承された共有かもしれません。人が Drive の画面で確認してください"
                )
        return removed, stuck

    def unshare_all(self, file_id: str) -> tuple[int, list[str]]:
        """★ owner 以外の権限を **すべて** 外す。(外した数, 外せなかった説明) を返す。

        ⚠️ これは同意撤回・緊急停止・実施終了のための経路である
        (`decisions.md` D-7)。★ 「共有する」側と対で必ずテストする。

        ⚠️★ 初版は `type == "anyone"` だけを外していた。
        `type=user` / `group`（誤って個別共有した相手）が残っていても
        「止めた」と名乗ってしまうので、**owner 以外を全部**対象にする。
        ★ 継承などで消せない権限は、握りつぶさず **説明として返す**。

        ⚠️★ **子ファイルにこれを使わない。** Drive はフォルダの共有を子へ継承させ、
        継承された権限は子の側からは削除できない。★ 子には `unshare_problems` を使う。
        """
        _check_id(file_id, "file_id")
        targets = [p for p in self.list_permissions(file_id) if not p.is_owner]
        return self._delete_perms(file_id, targets)

    def unshare_problems(self, file_id: str, keep_link_reader: bool = True
                         ) -> tuple[int, list[str]]:
        """★ **問題のある権限だけ** を外す。

        ⚠️★ 2026-08-16 の cross-review 指摘。子ファイルに `unshare_all` を使うと、
        **フォルダから継承した正しい共有まで削除対象**になる。
        ★ 継承された権限は子の側からは消せないので `permissions.delete` が失敗し、
        ⚠️ **正当な配布が「外せませんでした」で止まる**。
        → 子の掃除はこちらを使い、**悪い形の権限だけ**を狙って外す。

        ⚠️★★ `keep_link_reader` は **親が実際に共有されているときだけ True** にすること
        （2026-08-16 の追加レビュー指摘）。★ 親を見ずに無条件で見逃すと、
        **親が未共有なのに子 1 枚だけが直接公開されている**状態が、
        ⚠️ 掃除もされず報告にも出ないまま残る（実測で再現）。
        ★ 親に同じ形の権限が現存するときだけ「継承かもしれない」と言える。
        My Drive では `permissionDetails` で継承を判別できないので、
        **親との突き合わせがこの環境で可能な最良の近似**である。
        """
        _check_id(file_id, "file_id")
        targets = []
        for p in self.list_permissions(file_id):
            if p.is_owner:
                continue
            if p.problem() is not None:
                targets.append(p)
            elif not keep_link_reader and p.is_link_reader:
                # ⚠️ 親が共有していないなら、これは継承ではなく **直接の公開** である。
                targets.append(p)
        return self._delete_perms(file_id, targets)


def _default_media(path: Path):
    """★ 本番経路。⚠️ import を関数内に置き、テストが googleapiclient を要求しないようにする。"""
    from googleapiclient.http import MediaFileUpload

    return MediaFileUpload(str(path), mimetype=HTML_MIME, resumable=False)
