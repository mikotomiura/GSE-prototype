"""枝ごとの reflog から、コミットした時刻と作業の単位の名前だけを書き出す（auto-context-task-level・判断 6・13）。

- 読むのは reflog の時刻と見出しの種類（`commit` かどうか）だけ。コミットの内容・メッセージ・ファイルは読まない。
- 単位: 「repo の名前@枝の名前」。worktree はほぼ枝ごとに切っているので、worktree の単位とほぼ同じになる。
  主のチェックアウトで枝を切り替えても、枝の reflog はその枝のコミットだけを持つ（判断 13）。
- 消した枝と他の PC のコミットは入らない（reflog が無い）。
- 出力は `work/`（コミットしない・外部へ送らない）。枝の名前を含むため。

使い方:
    python3 -I git_commits.py --root ~ --since 2026-10-09 --out work/commits.json
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

TZ = ZoneInfo("Asia/Tokyo")
COMMIT_RE = re.compile(r"^commit( \((amend|initial)\))?:")


def git(args: list[str]) -> str:
    return subprocess.run(["git", *args], capture_output=True, text=True, check=True).stdout


def find_repos(root: Path, depth: int) -> set[Path]:
    """`root` の下（深さ `depth` まで）の .git を探し、共通の git ディレクトリで束ねる。"""
    out: set[Path] = set()
    for d in range(1, depth + 1):
        for dot_git in root.glob("/".join(["*"] * d) + "/.git"):
            if "Library" in dot_git.parts:
                continue
            try:
                common = git(["-C", str(dot_git.parent), "rev-parse", "--path-format=absolute", "--git-common-dir"]).strip()
            except subprocess.CalledProcessError:
                continue
            out.add(Path(common))
    return out


def branches(common: Path) -> list[str]:
    txt = git(["--git-dir", str(common), "for-each-ref", "--format=%(refname:short)", "refs/heads"])
    return [b for b in txt.splitlines() if b]


def reflog(common: Path, branch: str) -> list[tuple[int, str]]:
    """(unix 秒, 見出し) を古い順に。"""
    try:
        txt = git(["--git-dir", str(common), "reflog", "show", "--date=unix", "--format=%gd%x09%gs",
                   f"refs/heads/{branch}"])
    except subprocess.CalledProcessError:
        return []
    out = []
    for line in txt.splitlines():
        sel, _, subj = line.partition("\t")
        m = re.search(r"@\{(\d+)\}", sel)
        if m:
            out.append((int(m.group(1)), subj))
    return sorted(out)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True, type=Path)
    ap.add_argument("--depth", type=int, default=2)
    ap.add_argument("--since", required=True, help="YYYY-MM-DD（Asia/Tokyo）")
    ap.add_argument("--out", required=True, type=Path)
    a = ap.parse_args()
    since = int(datetime.strptime(a.since, "%Y-%m-%d").replace(tzinfo=TZ).timestamp())
    commits = []
    per_unit: dict[str, int] = {}
    for common in sorted(find_repos(a.root.expanduser(), a.depth)):
        repo = common.parent.name if common.name == ".git" else common.name
        for br in branches(common):
            unit = f"{repo}@{br}"
            for t, subj in reflog(common, br):
                if not COMMIT_RE.match(subj) or t < since:
                    continue
                commits.append({"t_ms": t * 1000, "unit": unit})
                per_unit[unit] = per_unit.get(unit, 0) + 1
    commits.sort(key=lambda c: c["t_ms"])
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps({"since": a.since, "commits": commits}, ensure_ascii=False, indent=1) + "\n",
                     encoding="utf-8")
    print(f"commits: {len(commits)}  units: {len(per_unit)}")


if __name__ == "__main__":
    main()
