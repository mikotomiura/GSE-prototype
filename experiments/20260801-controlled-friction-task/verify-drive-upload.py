#!/usr/bin/env python3
"""Drive に上げた課題ページを、手元の manifest と **byte 数で** 突き合わせる。

★ これは「上げた気になっている」のを防ぐ番人である。
  Drive MCP の `textContent` 送信は中身次第でバイトが化ける既知問題があり
  (memory: drive-mcp-upload-fidelity、エスケープ列を含む HTML で 44B 欠損を実測)、
  ⚠️ **更新・削除のツールが無い**ので、壊れたまま配ると取り返しがつかない。

使い方:
    ./verify-drive-upload.py dist/<ID>/_upload/manifest.tsv <drive-listing.json>

`<drive-listing.json>` は Drive MCP の search_files
(`parentId = '<被験者フォルダID>'`) の出力をそのまま保存したもの。

終了コード:
    0 … 全件一致
    1 … 1 件でも不一致 / 欠落 / 余分がある  ← ★ このときリンクを配らない

⚠️ ★ **byte 一致は同一の証明ではない。** 長さが同じで中身が違う壊れ方は捕まらない。
   ここが捕まえるのは「欠損・混入・上げ忘れ・別人のファイル」である。
   中身まで確かめたいときは Drive からダウンロードして SHA-256 を突き合わせること
   (manifest の 3 列目に入れてある)。
"""

import json
import sys


def load_manifest(path):
    """manifest.tsv → {name: (bytes, sha256)}"""
    out = {}
    with open(path, encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, 1):
            line = line.rstrip("\n")
            if not line:
                continue
            parts = line.split("\t")
            if len(parts) != 3:
                sys.exit(f"✗ manifest の {lineno} 行目が 3 列ではありません: {line!r}")
            name, size, sha = parts
            try:
                out[name] = (int(size), sha)
            except ValueError:
                sys.exit(f"✗ manifest の {lineno} 行目の byte 数が数値ではありません: {size!r}")
    if not out:
        sys.exit("✗ manifest が空です（★ 上げる物が無いのに上げたことにしない）")
    return out


def load_listing(path):
    """search_files の出力 JSON → {title: bytes}

    ⚠️ ★ `fileSize` が **無い** ファイルがありうる (Google 形式に変換されると消える)。
       これは「変換されてしまった = 別物になった」ということなので、
       黙って飛ばさず **不一致として扱う**。
    """
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    files = data.get("files", data if isinstance(data, list) else [])
    out = {}
    for f in files:
        title = f.get("title", "")
        if "fileSize" in f:
            out[title] = int(f["fileSize"])
        else:
            # ★ 変換された = mimeType が Google 形式になっている。サイズが無い。
            out[title] = None
    return out


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    manifest = load_manifest(sys.argv[1])
    listing = load_listing(sys.argv[2])

    problems = []
    for name, (size, _sha) in sorted(manifest.items()):
        if name not in listing:
            problems.append(f"欠落: {name}（Drive に無い）")
            continue
        actual = listing[name]
        if actual is None:
            problems.append(
                f"変換された: {name}（fileSize が無い = Google 形式に変換されている。"
                "★ disableConversionToGoogleType を付け忘れている）"
            )
        elif actual != size:
            problems.append(f"byte 不一致: {name} 手元={size} Drive={actual} 差={actual - size:+d}")

    # ★ 余分も止める。別の被験者のページが紛れていたら**割付を取り違えて配る**ことになる。
    for name in sorted(listing):
        if name not in manifest:
            problems.append(f"余分: {name}（manifest に無い。⚠️ 別の被験者のページが紛れていないか）")

    if problems:
        print("✗ 照合できませんでした:")
        for p in problems:
            print(f"    {p}")
        print()
        print("⚠️ ★ このフォルダの URL を配らないでください。")
        print("   Drive MCP には更新・削除が無いので、直すには Drive の画面で消してから上げ直します。")
        return 1

    total = sum(size for size, _ in manifest.values())
    print(f"✅ 照合できました: {len(manifest)} 件 / 合計 {total} B")
    print("   ⚠️ byte 一致は同一の証明ではない。中身まで見るなら SHA-256 を突き合わせること。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
