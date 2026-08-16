#!/usr/bin/env python3
"""課題ページを被験者別フォルダへ用意する **判断** の部分。

★ Drive を叩くのは `drive_client.py`。ここは「何を上げてよいか」「どの順でやるか」だけを持つ。
⚠️ この分離があるので、**偽 API で順序をテストできる**。

設計の SSOT: `.steering/20260807-vps-provisioning-automation/`
  - D-4 … ★ 照合が緑になるまで共有しない（⚠️ 順序を逆にしない）
  - D-7 … ★ desired state に「非共有」を表現できるようにする（同意撤回の担保）
  - design.md「更新の順序」… ⚠️ 共有を外す → 差し替える → 照合する → 共有し直す

⚠️★ **`provision.py`（CLI・assign/build との結線）はまだ書かない。**
   spike-1 で「`drive.file` は作れるが見えない」ことが分かり、
   親フォルダの持ち方を決め直す必要があるため
   （`.steering/20260816-provision-spikes/spike-results.md` の選択肢 A/B/C）。

## ⚠️★ 2026-08-16 のレビューで直した点

1. **露出の判定に厳格述語を流用していた** → `is_exposed` / `sharing_problems` を使う
   （悪い形の共有が「未共有」に見え、外されないまま差し替え・併存したまま緑になった）
2. **STOP が `type=anyone` の、しかもフォルダ本体しか外していなかった**
   → owner 以外を全部・**子まで**外す。名乗る前に読み返す
3. **STOP が同名重複で例外になり、一切止められなかった**
   → ⚠️ 重複は spike-1 で「起こると分かっている状態」。STOP は**全部から外す**
4. **完全削除していた** → ゴミ箱へ（`trash_file`）。⚠️ フォルダは消さずに止める
5. **被験者 ID を検査していなかった**（shell 版は検査している）
6. **symlink が許可リストを通っていた**（名前だけ見ていたため）
7. **`sha256Checksum` が None のとき黙って弱くなっていた** → spike-5 が「可」なので fail-closed
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from drive_client import DriveClient, DriveFile, Permission, sha256_of

# ★ 上げてよいのは課題ページ **だけ**（`decisions.md` D-1）。
#   ⚠️ `prepare-subjects.sh` / `make-upload-manifest.sh` が
#      `block*.html` に絞っているのと同じ規律を Python 側にも置く。
#   ⚠️ `\d` は Unicode 数字（`block٠١.html`）に一致してしまうので `[0-9]` を使う。
ALLOWED_NAME = re.compile(r"^block[0-9]{2}\.html$")

# ⚠️★ 被験者 ID の形。`make-upload-manifest.sh:54-62` と **同じ形**にする。
#   ★ 検査が無いと `subject="../../P099"` がそのまま Drive のフォルダ名になり、
#     さらに `provision.py` が `pages/<subject>` を組み立てた瞬間に
#     パストラバーサルへ昇格する（実測で通ることを確認した）。
SUBJECT_NAME = re.compile(r"^(P[0-9]{3}|PILOT-[A-Za-z0-9_]+)$")

# ★ desired state は 2 値だけ（`decisions.md` D-7）。
#   ⚠️ 「止める」を表現できない収束器で共有を管理してはならない。
SHARE = "share"
STOP = "stop"


class ProvisionError(RuntimeError):
    """⚠️ 配ってはいけない状態。★ 呼び出し元は **URL を出さない**。"""


@dataclass
class Result:
    subject: str
    state: str  # "ok" | "verify_failed" | "stopped" | "stop_failed" | "absent"
    shared: bool
    problems: list[str] = field(default_factory=list)
    folder_id: str | None = None
    # ⚠️★ 「注意書き」は `problems`（＝ 赤の理由）と**別のチャネル**に置く。
    #    ★ 相乗りさせると、呼び出し側が `if r.problems: 赤` と書いたときに
    #      「成功＋注記」と「本当の失敗」を区別できなくなる（2026-08-16 のレビュー指摘）。
    notes: list[str] = field(default_factory=list)

    @property
    def distributable(self) -> bool:
        """★ この結果で URL を配ってよいか。⚠️ 共有済みかつ問題なしのときだけ。"""
        return self.state == "ok" and self.shared and not self.problems


# --------------------------------------------------------------------- 手元

def build_local_manifest(local_dir: Path) -> dict[str, tuple[int, str]]:
    """手元の {name: (bytes, sha256)} を作る。

    ⚠️★ **許可リストに 1 つでも外れた物があれば、その場で落とす。**
    ★ 「block*.html だけ拾って残りは無視」にしない — 無視は
      `g1-submit.json`（共有シークレット）や `pubkey.txt` が
      **黙って混ざる経路**をそのまま残すことになる（`design.md` の 4）。
    """
    if not local_dir.is_dir():
        raise ProvisionError(f"課題ページのディレクトリがありません: {local_dir}")

    entries = sorted(p for p in local_dir.iterdir())
    manifest: dict[str, tuple[int, str]] = {}
    for p in entries:
        # ⚠️★ symlink を **先に** 弾く。`is_file()` はリンク先を辿るので、
        #    `block03.html -> ~/.config/gse-provision/token.json` のような
        #    リンクが名前だけの検査を通り抜け、★ 秘密が公開フォルダへ上がる
        #    （2026-08-16 に実測で再現した）。
        if p.is_symlink():
            raise ProvisionError(
                f"⚠️★ シンボリックリンクがあります: {p.name}\n"
                "    ★ 名前が blockNN.html でも、リンク先が何かは分かりません。"
                "実体のファイルだけを置いてください。"
            )
        if not p.is_file():
            raise ProvisionError(
                f"⚠️ ファイル以外が入っています: {p.name}（★ 課題ページだけを置いてください）"
            )
        if not ALLOWED_NAME.fullmatch(p.name):
            raise ProvisionError(
                f"⚠️★ 許可リストに無いファイルがあります: {p.name}\n"
                f"    ★ 上げてよいのは blockNN.html だけです（decisions.md D-1）。\n"
                f"    ⚠️ macOS の .DS_Store もここで止まります。消してから再実行してください。"
            )
        manifest[p.name] = (p.stat().st_size, sha256_of(p))

    if not manifest:
        raise ProvisionError(
            f"⚠️ {local_dir} に課題ページが 1 枚もありません"
            "（★ 上げる物が無いのに「用意できた」ことにしない）"
        )
    return manifest


# --------------------------------------------------------------------- 照合

def verify(manifest: dict[str, tuple[int, str]], listing: list[DriveFile]) -> list[str]:
    """手元と Drive を突き合わせ、問題を**全部**返す（空なら緑）。

    ★ `verify-drive-upload.py` の判定をそのまま写す（⚠️ 手続きを 2 つにしない）。
      欠落 / 変換された / byte 不一致 / 余分 は同じ扱い。

    ⚠️★ **参照実装より厳しくしている点が 3 つある**（`verify-drive-upload.py` にも注記済み）:
      1. 同名の重複を赤にする（参照実装は dict で潰れて最後が勝つ＝素通り）
      2. `sha256Checksum` が返るなら **中身まで**見る（byte 数が同じで中身が違う壊れ方を捕まえる）
      3. ★ `sha256Checksum` が **返らない場合も赤**にする。
         ⚠️ spike-5 (2026-08-16) で「返る」と実測した以上、返らないのは想定外であり、
         「黙って照合が弱くなる」ほうが危険（`allowFileDiscovery` の三値と同じ思想）。
    """
    problems: list[str] = []

    by_name: dict[str, list[DriveFile]] = {}
    for f in listing:
        by_name.setdefault(f.name, []).append(f)

    for name, (size, sha) in sorted(manifest.items()):
        found = by_name.get(name)
        if not found:
            problems.append(f"欠落: {name}（Drive に無い）")
            continue
        if len(found) > 1:
            problems.append(
                f"重複: {name} が Drive に {len(found)} 件（★ どれが正か決められない）"
            )
            continue
        f = found[0]
        if f.converted_to_google_type:
            problems.append(
                f"変換された: {name}（size が無い = Google 形式に変換されている）"
            )
            continue
        if f.size != size:
            problems.append(
                f"byte 不一致: {name} 手元={size} Drive={f.size} 差={(f.size or 0) - size:+d}"
            )
            continue
        if f.sha256 is None:
            problems.append(
                f"⚠️★ SHA 未返却: {name}（sha256Checksum が返らない。"
                "★ spike-5 では返ると実測済みなので想定外。byte だけで配らない）"
            )
            continue
        if f.sha256 != sha:
            # ★ ここが byte 照合では原理的に捕まらない壊れ方（長さが同じで中身が違う）。
            problems.append(f"SHA 不一致: {name}（byte 数は同じだが中身が違う）")

    for name in sorted(by_name):
        if name not in manifest:
            problems.append(
                f"余分: {name}（手元に無い。⚠️ 別の被験者のページが紛れていないか）"
            )

    return problems


def _perm_problems(perms: list[Permission]) -> list[str]:
    return [msg for p in perms if (msg := p.problem()) is not None]


def _exposed(perms: list[Permission]) -> bool:
    return any(not p.is_owner for p in perms)


def _properly_shared(perms: list[Permission]) -> bool:
    return any(p.is_link_reader for p in perms)


# ------------------------------------------------------------------ 収束器

def reconcile_subject(
    client: DriveClient,
    parent_id: str,
    subject: str,
    local_dir: Path,
    desired: str,
    media_factory=None,
) -> Result:
    """1 人ぶんを desired state へ寄せる。

    ⚠️★ 守っている順序（`design.md`「更新の順序」）:

        共有を外す → 差し替える → 照合する → 共有し直す

    ★ 「消す → 上げる」の順だと、**削除成功 → アップロード失敗**の窓で
      被験者が**欠けたブロック集合**を見られる。だから差し替えの前に共有を外す。
    """
    if desired not in (SHARE, STOP):
        raise ProvisionError(f"desired は {SHARE!r} か {STOP!r} だけです: {desired!r}")
    if not SUBJECT_NAME.fullmatch(subject or ""):
        raise ProvisionError(
            f"⚠️★ 被験者 ID の形が違います: {subject!r}"
            "（★ P015 か PILOT-win のような形だけを認めます。"
            "make-upload-manifest.sh と同じ規則です）"
        )

    if desired == STOP:
        return _stop(client, parent_id, subject)
    return _share(client, parent_id, subject, local_dir, media_factory)


# ------------------------------------------------------------ 「止める」(D-7)

def _stop(client: DriveClient, parent_id: str, subject: str) -> Result:
    """⚠️★ 同意撤回・緊急停止・実施終了。**外す方向には曖昧さがあっても倒す。**

    ★ `find_child_folder` を使わない。同名が 2 つあるとき例外で落ちると
    **一切止められない**が、⚠️ 同名重複は spike-1 で「起こると分かっている状態」である
    （`drive.file` は手作業で作られた同名フォルダを見落として二重に作る）。
    → **一致する全部から外す。**

    ⚠️★ **保証範囲の限界**: `drive.file` では「アプリが作っていない子」は見えないので、
    ★ **見えない子に付いた共有は原理的に外せない**。それを `problems` に明示する。
    """
    matches = client.find_children(parent_id, subject)
    if not matches:
        return Result(subject, state="absent", shared=False)

    problems: list[str] = []
    if len(matches) > 1:
        problems.append(
            f"⚠️★ '{subject}' が {len(matches)} 個あります。全部から共有を外しましたが、"
            "★ どれが正かは人が判断してください（spike-1 の重複問題）"
        )

    for f in matches:
        _, stuck = client.unshare_all(f.id)
        problems.extend(stuck)
        if f.is_folder:
            for child in client.list_children(f.id):
                _, s2 = client.unshare_all(child.id)
                problems.extend(s2)
                if client.is_exposed(child.id):
                    problems.append(
                        f"⚠️★ 子 '{child.name}' の共有が外れていません（読み返しで確認）"
                    )
        # ★ 読み返し（⚠️ 広い述語で見る。厳格側だと「悪い共有が残っている」を見逃す）
        if client.is_exposed(f.id):
            problems.append(
                f"⚠️★ '{subject}' の共有が外れていません（読み返しで確認）"
            )

    # ★ フォルダを優先して返す（⚠️ `find_children` は同名の**ファイル**も返しうる）。
    folders = [f for f in matches if f.is_folder]
    folder_id = (folders or matches)[0].id
    if not folders:
        problems.append(
            f"⚠️ '{subject}' に一致したのはフォルダではありませんでした"
            "（★ 共有は外しましたが、想定と違う物です）"
        )

    # ⚠️★ **保証範囲を常に添える。** `drive.file` では「アプリが作っていない子」が
    #    見えないので、★ 見えない子に付いた共有は**原理的に外せない**。
    #    docstring に書くだけだと運用者に届かないので、結果に 1 行載せる。
    #    ⚠️ ただし `problems`（＝ 赤の理由）ではなく `notes` に置く
    #      （成功時の注記と本当の失敗を呼び出し側が区別できるように）。
    #    ★ 成功・失敗の**両方**に付ける（片方だけだと非対称で読み違える）。
    note = (
        "★ 注記: `drive.file` スコープでは**このアプリが作っていない子は見えない**ため、"
        "見えない子に付いた共有は外せていない可能性があります。"
        "⚠️ 完全に止めるには Drive の画面でも確認してください"
    )

    if problems:
        # ⚠️ 外しきれていない可能性があるので **"stopped" を名乗らない**。
        return Result(subject, state="stop_failed", shared=False,
                      problems=problems, folder_id=folder_id, notes=[note])

    return Result(subject, state="stopped", shared=False, folder_id=folder_id,
                  notes=[note])


# ------------------------------------------------------------ 「配る」(D-4)

def _share(client, parent_id, subject, local_dir, media_factory) -> Result:
    # ★ 1. 許可リスト。⚠️ ここで落ちたら **Drive を 1 回も叩かない**。
    manifest = build_local_manifest(local_dir)

    folder = client.find_child_folder(parent_id, subject)
    if folder is None:
        folder_id = client.create_folder(parent_id, subject)
    else:
        folder_id = folder.id

    perms = client.list_permissions(folder_id)
    bad = _perm_problems(perms)

    # ★ 2. ⚠️ 悪い形の共有が付いていたら、**何よりも先に外す**（fail-closed）。
    #    ★ ここが 2026-08-16 のレビューで見つかった穴。悪い共有を「未共有」と読むと、
    #      良い共有を足して**併存したまま緑**になる。
    if bad:
        _, stuck = client.unshare_all(folder_id)
        if stuck:
            return Result(subject, state="verify_failed", shared=False,
                          problems=bad + stuck, folder_id=folder_id)
        perms = client.list_permissions(folder_id)
        if _exposed(perms):
            return Result(
                subject, state="verify_failed", shared=False, folder_id=folder_id,
                problems=bad + ["⚠️★ 不正な共有を外したのに、読み返すとまだ露出しています"],
            )

    listing = client.list_children(folder_id)

    # ★ 2b. ⚠️ 子ファイルに **直接** 付いた共有も見る（`_stop` と対称にする）。
    child_bad = _clean_child_shares(client, listing, perms)
    if child_bad:
        return Result(subject, state="verify_failed", shared=False,
                      problems=child_bad, folder_id=folder_id)

    problems = verify(manifest, listing)

    # ★ 3. 既に正しい状態なら **書き込みを 1 回もしない**（冪等）。
    if not problems and not bad and _properly_shared(perms):
        return Result(subject, state="ok", shared=True, folder_id=folder_id)

    # ★ 4. 中身を直す必要があるなら、⚠️ **先に共有を外す**（露出は広い述語で見る）。
    if problems and _exposed(perms):
        _, stuck = client.unshare_all(folder_id)
        if stuck:
            return Result(subject, state="verify_failed", shared=False,
                          problems=problems + stuck, folder_id=folder_id)
        perms = client.list_permissions(folder_id)
        if _exposed(perms):
            # ⚠️ 外れたことを確かめてからでないと差し替えに入らない。
            return Result(
                subject, state="verify_failed", shared=False, folder_id=folder_id,
                problems=problems + ["⚠️★ 差し替え前に共有を外せませんでした"],
            )

    if problems:
        blockers = _replace_content(client, folder_id, local_dir, manifest, listing,
                                    media_factory)
        if blockers:
            # ⚠️ 人が見るべき物（フォルダ等）があるので、勝手に消さずに止める。
            return Result(subject, state="verify_failed", shared=False,
                          problems=blockers, folder_id=folder_id)
        listing = client.list_children(folder_id)
        problems = verify(manifest, listing)

    # ★ 5. ⚠️ 照合が赤なら **共有しないで返す**（D-4 の本丸）。
    if problems:
        return Result(subject, state="verify_failed", shared=False,
                      problems=problems, folder_id=folder_id)

    # ★ 6. 緑のときだけ共有し、⚠️ **読み返して**確かめる。
    perms = client.list_permissions(folder_id)
    if not _properly_shared(perms):
        client.share_link_reader(folder_id)
        perms = client.list_permissions(folder_id)

    after_bad = _perm_problems(perms)
    if not _properly_shared(perms) or after_bad:
        # ⚠️★ 「共有した」ではなく「正しい形で共有できた」ことを要求する。
        return Result(
            subject, state="verify_failed", shared=False, folder_id=folder_id,
            problems=after_bad or [
                "共有を設定したが、読み返して「リンクを知っている全員（閲覧者）」を"
                "確認できませんでした"
            ],
        )

    return Result(subject, state="ok", shared=True, folder_id=folder_id)


def _clean_child_shares(client: DriveClient, listing: list[DriveFile],
                        folder_perms: list[Permission]) -> list[str]:
    """⚠️★ 子ファイルに **直接** 付いた共有を外す。外しきれなければ説明を返す。

    ★ 2026-08-16 の cross-review 指摘。`_stop` は子まで見ているのに `_share` は
      **フォルダ自身の権限しか見ていなかった**。⚠️ 見ないと、
      過去のバグ版・手作業・別ツール経由で `block03.html` 1 枚だけに
      `type=user, role=writer` が付いているような状態が、
      ★ **収束器を何周しても直らないまま「配ってよい」と報告される**。

    ⚠️★★ **`unshare_all` を使わない。** Drive はフォルダの共有を子へ継承させ、
    ★ 継承された権限は子の側からは削除できない。⚠️ `unshare_all` は owner 以外を
    全部消しにいくので、**フォルダから継承した正しい共有まで削除対象**になり、
    `permissions.delete` が失敗して ★ **正当な配布が止まる**（2026-08-16 の cross-review
    で両者一致の指摘。初版の docstring は「フォルダを先に外せ」と書いていたが、
    ⚠️ フォルダが**正しく共有済み**の経路ではそもそも外さないので前提が成立しなかった）。
    → `unshare_problems` で **悪い形の権限だけ**を狙って外す。

    ⚠️★★ **見逃しは親の実状態に条件づける**（2026-08-16 の追加レビュー指摘）。
    ★ 「継承かもしれないから残す」と言えるのは、**親に同じ形の権限が現存するとき**だけ。
    ⚠️ 親を見ずに無条件で見逃すと、次の 2 つが**掃除もされず報告にも出ないまま**残る（実測）:
      A. 親は未共有なのに、`block01.html` 1 枚だけが直接 `anyone/reader` で公開されている
      B. ゴミ箱へ送った余分ファイルに公開が残る（★ ゴミ箱は権限を消さない＝復元すれば再公開）

    ⚠️ クォータ: 問題のある子では `permissions.list` が最大 **3 回**
       （判定 → 外す → 読み返し）。★ 問題が無ければ 1 回。
       15 人 × 10 枚 = 150〜450 回/周。収束器の周期を決めるときに勘定に入れること。
    """
    # ★ 親が「正しく共有されている」ときだけ、子の同じ形の権限を継承として見逃す。
    folder_shared = _properly_shared(folder_perms)

    problems: list[str] = []
    for ch in listing:
        perms = client.list_permissions(ch.id)
        targets = [p for p in perms if not p.is_owner and p.problem() is not None]
        if not folder_shared:
            targets += [p for p in perms if p.is_link_reader]
        if not targets:
            continue
        _, stuck = client.unshare_problems(ch.id, keep_link_reader=folder_shared)
        problems.extend(f"[{ch.name}] {m}" for m in stuck)
        if not stuck:
            after = client.list_permissions(ch.id)
            left = [p for p in after if not p.is_owner and p.problem() is not None]
            if not folder_shared:
                left += [p for p in after if p.is_link_reader]
            problems.extend(
                f"[{ch.name}] ⚠️★ 個別の共有が外れていません (id={p.id}, type={p.type}, "
                f"role={p.role})" for p in left
            )
    return problems


def _replace_content(client, folder_id, local_dir, manifest, listing,
                     media_factory) -> list[str]:
    """★ 余分をゴミ箱へ入れ、足りない/違う物を上げ直す。⚠️ 共有は触らない。

    戻り値は「⚠️ 自動で触ってはいけない物」の説明（空なら進んでよい）。

    ⚠️★ **フォルダは消さない。** 被験者フォルダの下に研究者が置いた `提出物/` や
    被験者がアップロードした物があったとき、★ 配下ごと消えるのは取り返しがつかない。
    → 見つけたら**止めて人に返す**（許可リストと同じ発想）。
    """
    by_name: dict[str, list[DriveFile]] = {}
    for f in listing:
        by_name.setdefault(f.name, []).append(f)

    blockers: list[str] = []
    for name, files in sorted(by_name.items()):
        for f in files:
            if f.is_folder:
                blockers.append(
                    f"⚠️★ 被験者フォルダの下にフォルダがあります: '{name}'。"
                    "★ 自動では消しません（配下ごと失われるため）。人が確認してください"
                )
    if blockers:
        return blockers

    # 余分・重複はゴミ箱へ。
    # ⚠️★ **先に共有を外してから**入れる（2026-08-16 のレビュー指摘）。
    #    ★ ゴミ箱は権限を消さないので、外さずに送ると
    #      「ゴミ箱にあるが world-readable のまま」＝ 復元すれば再公開の物が残る。
    #    ⚠️ しかも `verify` の対象から消えるので、収束器は二度と掃除しない。
    for name, files in sorted(by_name.items()):
        if name in manifest and len(files) <= 1:
            continue
        for f in files:
            _, stuck = client.unshare_all(f.id)
            if stuck:
                blockers.extend(f"[{name}] {m}" for m in stuck)
                continue
            client.trash_file(f.id)
    if blockers:
        return blockers

    for name, (size, sha) in sorted(manifest.items()):
        files = by_name.get(name, [])
        ok = (
            len(files) == 1
            and not files[0].converted_to_google_type
            and files[0].size == size
            and files[0].sha256 == sha
        )
        if ok:
            continue
        if len(files) == 1:
            client.trash_file(files[0].id)
        client.upload_html(folder_id, local_dir / name, media_factory=media_factory)
    return []
