#!/usr/bin/env python3
"""収集済みログの `meta.capabilities` を**機械判定**する前処理ゲート (ADR-013 Migration 4)。

## ⚠️★★★ なぜこれがコードなのか

ADR-013 自身の診断は逐語で「**規約は書いてあったのに適用しなかった**」である。
★ 「計器がコホートを跨げなかった」失敗は既に **2 件**起きている:

1. `keys` / `bs_keys` の配線は 2026-08-16。Phase1 ログはそれ以前なので**存在しない**。
2. `hook_health` / `starved_ms` は Phase1 コホート (63 ファイル) に **1 行も無い**
   (記録は 2026-07-04〜07-24、`liveness.rs` の追加は 2026-08-09 = **収集の 16 日後**)。

→ ⚠️ **人が適用し忘れられる形のままでは 3 件目が起きる。**
★ だから「対象ログの行種を数える」を**人の手順ではなくコード**にする。

## ★ 判定表 (ADR-013 D1 ＋ 2026-08-19 に追加した第 3 群)

| 宣言 | 該当行の数 | 結論 |
|---|---|---|
| `unconditional` | 0 行 | ★ **SIGNAL_ABSENT** — 測れて、無かった |
| `unconditional` | ≥1 行 | PRESENT |
| `threshold_gated` | 0 行 | ⚠️ **UNDECIDABLE** — 閾値未達と区別できない |
| `config_gated` | 0 行 | ⚠️★★★ **UNDECIDABLE** — 設定で送出元ごと止まっていた可能性 |
| どの群にも無い | 0 行 | ⚠️ **INSTRUMENT_ABSENT** — 計器が無かった (★ 過去 2 件はここ) |
| どの群にも無い | ≥1 行 | ⚠️ **DECLARATION_BUG** — 宣言のバグ → `app_version` で追跡する |
| ⚠️ `capabilities` キー自体が無い (旧ログ) | 0 行 | ⚠️ **INSTRUMENT_ABSENT** に倒す |
| ⚠️ `capabilities` キー自体が無い (旧ログ) | ≥1 行 | PRESENT (★ 目の前にあるのだから読める。⚠️ ただし『無い場合』は解釈できない) |

⚠️ **`hmm_version` では代用できない** —— HMM の版であって「何を記録できるか」ではない。

## ⚠️★★ コホートを跨ぐときの追加検査

★ 複数ファイルを渡したとき、**ファイルごとに宣言が食い違っていたら `MIXED`** にする。
⚠️ これこそが過去 2 件の失敗様式そのもの (「一部のファイルには計器があった」)。
→ ★ 平均を取る前に**止める**。

## 使い方

```bash
# 解析の前処理の先頭で (★ run.sh の Step 0)
PYTHONUTF8=1 python scripts/capabilities_gate.py <dir-or-files> --require key --require starve_window

# 空振り検査 (⚠️ 検査自身が常に緑でないことを確かめる)
PYTHONUTF8=1 python scripts/capabilities_gate.py --self-test
```

Python から:

```python
from capabilities_gate import preflight
report = preflight(paths, required=["key", "starve_window"])   # 誤読しうるなら例外
```

## exit code

| code | 意味 |
|---|---|
| 0 | ★ すべての要求行種が **読める** (PRESENT または SIGNAL_ABSENT) |
| 2 | 使い方の誤り / 入力が無い |
| 3 | ⚠️ **UNDECIDABLE** — 0 行を「無かった」と読んではいけない |
| 4 | ⚠️ **INSTRUMENT_ABSENT** — そのコホートには計器が無い |
| 5 | ⚠️ **DECLARATION_BUG** — 宣言に無い行種が実在する |
| 6 | ⚠️ **MIXED** — コホート内で宣言が食い違う |

⚠️ `--allow-undecidable` を付けると 3 を警告に落とす (★ 解析が「判定不能」を明示的に
受け入れる場合のみ。**既定では止まる**)。

## ⚠️ プライバシー

★ 本スクリプトは **`type` フィールドと `meta` 行しか読まない**。
⚠️ キーストローク内容は NDJSON に元々無いが、それ以外の値も一切出力しない
(`data-privacy` / `docs/development-guidelines.md §10.4`)。

⚠️★★★ **ファイル名は `--json` に出さない** (security-checker HIGH・2026-08-21)。
★ 実データのファイル名は **擬似 ID ＋ セッション開始時刻そのもの**であり
(実測: `P010_gse_20260629_073659.ndjson`)、`--json` の出力は
`experiments/*/results/capabilities.json` として **コミットされうる**
(`.gitignore` は `results/*.json` を塞いでいない)。
→ ★ JSON には**不可逆な `file_id`** だけを出し、実名は
**端末表示 (`render`) にだけ**出す。`--json` 指定時、本文は **stderr** へ回す。

| 出力先 | 実ファイル名 | `file_id` |
|---|---|---|
| stdout (`--json`・**保存される**) | ⚠️ **出さない** | ★ 出す |
| 端末表示 (`render`) | ★ 出す (混在時のみ) | ★ 出す |
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple

# --- 判定結果 -----------------------------------------------------------------

PRESENT = "PRESENT"
SIGNAL_ABSENT = "SIGNAL_ABSENT"
UNDECIDABLE = "UNDECIDABLE"
INSTRUMENT_ABSENT = "INSTRUMENT_ABSENT"
DECLARATION_BUG = "DECLARATION_BUG"
MIXED = "MIXED"

#: ★ 群の名前。`src-tauri/src/capabilities.rs` が書き出すキーと一致させる。
GROUPS = ("unconditional", "threshold_gated", "config_gated")

#: ⚠️ 0 行を「信号が無かった」と読んでよいのは **この群だけ**である。
DECIDABLE_WHEN_EMPTY = ("unconditional",)

#: ⚠️★★★ `capabilities` キー自体が無い旧ログを表す番兵。
#: ★ 「宣言はあるが載っていない」(`None`) と**別物として扱う**ため、値を分ける。
LEGACY = "<legacy>"

EXIT_OK = 0
EXIT_USAGE = 2
EXIT_UNDECIDABLE = 3
EXIT_INSTRUMENT_ABSENT = 4
EXIT_DECLARATION_BUG = 5
EXIT_MIXED = 6

#: ★ verdict → exit code。⚠️ **数が大きいほど重い**という順序に意味は持たせない
#: (呼び出し側が `if code:` で止まればよい)。
_EXIT_FOR = {
    UNDECIDABLE: EXIT_UNDECIDABLE,
    INSTRUMENT_ABSENT: EXIT_INSTRUMENT_ABSENT,
    DECLARATION_BUG: EXIT_DECLARATION_BUG,
    MIXED: EXIT_MIXED,
}


class CapabilitiesGateError(RuntimeError):
    """⚠️ 解析が **0 行を誤読しうる**ときに送出する。★ 握り潰さないこと。"""

    def __init__(self, report: "Report") -> None:
        super().__init__(report.summary())
        self.report = report


# --- 1 ファイルの読み取り ------------------------------------------------------


class FileFacts:
    """1 ファイルから読み取った**宣言**と**行種の数**。★ 値は一切持ち出さない。"""

    def __init__(self, path: Path) -> None:
        self.path = path
        #: ⚠️ `None` = `capabilities` キー自体が無い (旧ログ)。★ `{}` とは意味が違う。
        self.declared: Optional[Dict[str, Set[str]]] = None
        self.counts: Dict[str, int] = {}
        self.app_version: Optional[str] = None
        self.malformed_lines = 0

    def group_of(self, line_type: str) -> Optional[str]:
        """`line_type` が属する群。

        - 群名 (`"unconditional"` など): その群に宣言されている
        - [`LEGACY`]: ⚠️ **`capabilities` キー自体が無い**旧ログ (宣言という概念が無い)
        - `None`: ★ 宣言はあるが、この行種は**どの群にも無い**

        ⚠️★★★ **旧ログと「宣言はあるが載っていない」を混ぜてはならない。**
        ★ 前者は「この時代には自己記述が無かった」、後者は「このビルドは記録しない」
        であり、**行が実在したときの読み方が逆になる** (前者は普通に読める / 後者は宣言のバグ)。
        """
        if self.declared is None:
            return LEGACY
        for g in GROUPS:
            if line_type in self.declared.get(g, set()):
                return g
        return None


def read_file(path: Path) -> FileFacts:
    """NDJSON を 1 本読み、宣言と行種の数だけを取り出す。

    ⚠️ 読めなかったら [`MissingInputError`] に倒す (★ 黙って 0 行にしない)。
    ⚠️★ 例外文には **`path.name` しか入れない** —— ★ 素の `OSError` は
    `C:\\Users\\<name>\\...\\P0xx\\...` という**絶対パス**を出し、
    ログを貼る運用で識別子が漏れる (security-checker LOW・2026-08-21)。
    """
    facts = FileFacts(path)
    try:
        # ⚠️ 不正バイト 1 個で `UnicodeDecodeError` を投げない。★ その行は
        #   `malformed_lines` として数え、**判定は続ける**（読めない = 0 行、にしない）。
        handle = path.open("r", encoding="utf-8", errors="replace")
    except OSError as e:
        raise MissingInputError(
            f"読み取れないファイルがあります: {path.name} ({e.__class__.__name__})"
        ) from None
    with handle as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                facts.malformed_lines += 1
                continue
            if not isinstance(row, dict):
                facts.malformed_lines += 1
                continue
            line_type = row.get("type")
            if not isinstance(line_type, str):
                facts.malformed_lines += 1
                continue
            facts.counts[line_type] = facts.counts.get(line_type, 0) + 1
            if line_type != "meta":
                continue
            # ★ `meta` は開始/終了の 2 行出る。宣言を持つのは**開始側**である。
            if facts.app_version is None and isinstance(row.get("app_version"), str):
                facts.app_version = row["app_version"]
            caps = row.get("capabilities")
            if isinstance(caps, dict) and facts.declared is None:
                facts.declared = {
                    g: set(caps.get(g) or []) for g in GROUPS if isinstance(caps.get(g), list)
                }
    return facts


# --- コホート単位の判定 --------------------------------------------------------


class Verdict:
    def __init__(self, line_type: str) -> None:
        self.line_type = line_type
        self.verdict = PRESENT
        self.rows = 0
        self.groups: Set[Optional[str]] = set()
        self.note = ""

    def as_dict(self) -> dict:
        return {
            "line_type": self.line_type,
            "verdict": self.verdict,
            "rows": self.rows,
            "declared_as": sorted(g or "<undeclared>" for g in self.groups),
            "note": self.note,
        }


class Report:
    def __init__(self, files: Sequence[FileFacts], verdicts: Sequence[Verdict]) -> None:
        self.files = list(files)
        self.verdicts = list(verdicts)

    def worst_exit(self, allow_undecidable: bool = False) -> int:
        code = EXIT_OK
        for v in self.verdicts:
            if v.verdict == UNDECIDABLE and allow_undecidable:
                continue
            code = max(code, _EXIT_FOR.get(v.verdict, EXIT_OK))
        return code

    def summary(self) -> str:
        # ⚠️★★★ **入力ゼロを「読める」と言わない** (security-checker MEDIUM・2026-08-21)。
        #   ★ 以前は verdicts が空 → bad が空 → 「すべての要求行種が読める」を返していた。
        #   ⚠️ `except CapabilitiesGateError as e: log(str(e))` した解析は、
        #     **入力ゼロの失敗を緑として記録する** —— ★ 本ゲートが防ごうとしている誤読が、
        #     ゲート自身のエラーパスに残っていた。
        if not self.files:
            return (
                "capabilities gate: ⚠️ 対象の .ndjson が 1 本も無い "
                "(★ 判定は 1 つも行われていない。『読める』ではない)"
            )
        bad = [v for v in self.verdicts if v.verdict not in (PRESENT, SIGNAL_ABSENT)]
        if not bad:
            return "capabilities gate: すべての要求行種が読める"
        return "capabilities gate: " + " / ".join(
            f"{v.line_type}={v.verdict}({v.rows} 行)" for v in bad
        )

    def as_dict(self) -> dict:
        """機械可読な報告。⚠️★★★ **ファイル名を出さない**。

        ## ⚠️ なぜ名前を落とすか (security-checker HIGH・2026-08-21)

        ★ 実データのファイル名は **擬似 ID ＋ セッション開始時刻そのもの**である
        (実測: `P010_gse_20260629_073659.ndjson` ＝ 秒精度の UTC)。
        ⚠️ そして本メソッドの出力は `experiments/_template/run.sh` が
        `results/capabilities.json` へ**保存する** ——
        ★ `.gitignore` は `experiments/**/*.ndjson` などを塞ぐが
        **`results/*.json` は対象外**（「集計 JSON はコミット可」と明記されている）。

        → ⚠️★★★ そのままだと「**各参加者がいつ打鍵していたか**の全リスト」が
        コミットされ、⚠️ **本 repo は一時 public にする運用がある**。

        ★ したがって **発生源で落とす**。`.gitignore` に足す対処は採らない ——
        ⚠️ テンプレはコピーされるので、**新しい実験ディレクトリごとに漏れる**。

        ★ 人が該当ファイルを探すための実名は [`render`]（**端末表示のみ**）に出す。
        `file_id` は両方に出るので**突き合わせられる**。
        """
        return {
            "files": [
                {
                    # ★ 不可逆な短縮ハッシュ。⚠️ 名前そのものは出さない。
                    "file_id": file_id_of(f.path),
                    "app_version": f.app_version,
                    "declares_capabilities": f.declared is not None,
                    "malformed_lines": f.malformed_lines,
                }
                for f in self.files
            ],
            "verdicts": [v.as_dict() for v in self.verdicts],
        }


def judge(files: Sequence[FileFacts], required: Iterable[str]) -> Report:
    """★ 判定の**唯一の式**。⚠️ ここに分岐を足したら判定表 (docstring) も同時に直す。

    ⚠️ `files` が空なら**判定を作らない**（★ 素の `StopIteration` を投げない。
    公開関数として呼ばれうる・code-reviewer MEDIUM）。
    ★ 「0 本のコホートは判定不能」は [`Report.summary`] が言う。
    """
    if not files:
        return Report([], [])
    verdicts: List[Verdict] = []
    for line_type in required:
        v = Verdict(line_type)
        v.rows = sum(f.counts.get(line_type, 0) for f in files)
        v.groups = {f.group_of(line_type) for f in files}

        if len(v.groups) > 1:
            # ⚠️★★★ コホート内で宣言が食い違う = 過去 2 件の失敗様式そのもの。
            #   ★ 平均を取る前に止める。
            v.verdict = MIXED
            v.note = (
                "コホート内でファイルごとに宣言が違う。"
                "★ 一部のファイルにだけ計器がある状態で集計してはならない"
            )
            verdicts.append(v)
            continue

        group = next(iter(v.groups))
        if group == LEGACY:
            # ⚠️★★★ **旧ログ**: `capabilities` キー自体が無い (自己記述より前の時代)。
            #   ★ 行が実在するなら**それは読める** —— 目の前にあるのだから。
            #   ⚠️ しかし 0 行のときは「計器が無かった」と「信号が無かった」を
            #     **区別する材料がどこにも無い** → 安全側 (計器が無かった) に倒す。
            if v.rows > 0:
                v.verdict = PRESENT
                v.note = (
                    "⚠️ capabilities を持たない旧ログだが、行は実在する。"
                    "★ ただし『無い場合』の解釈はこのコホートではできない"
                )
            else:
                v.verdict = INSTRUMENT_ABSENT
                v.note = (
                    "⚠️ capabilities を持たない旧ログ。"
                    "★ 計器が無かったのか信号が無かったのか**区別できない**ので"
                    "『計器が無かった』に倒す (ADR-013)"
                )
        elif group is None:
            # ★ 宣言はある。しかしこの行種はどの群にも無い。
            if v.rows > 0:
                v.verdict = DECLARATION_BUG
                v.note = "宣言に無い行種が実在する。★ app_version で追跡すること"
            else:
                v.verdict = INSTRUMENT_ABSENT
                v.note = (
                    "このビルドはこの行種を記録しない。"
                    "⚠️ 0 行を『信号が無かった』と読んではならない"
                )
        elif v.rows > 0:
            v.verdict = PRESENT
            v.note = f"宣言: {group}"
        elif group in DECIDABLE_WHEN_EMPTY:
            v.verdict = SIGNAL_ABSENT
            v.note = "★ 測れて、無かった"
        else:
            v.verdict = UNDECIDABLE
            v.note = (
                f"宣言: {group}。"
                "⚠️ 閾値未達 / 設定停止と区別できないので『無かった』と結論できない"
            )
        verdicts.append(v)
    return Report(files, verdicts)


def file_id_of(path: Path) -> str:
    """ファイル名の**不可逆な**短縮 ID。★ 端末表示と JSON を突き合わせるためだけに使う。"""
    return hashlib.sha256(path.name.encode("utf-8")).hexdigest()[:8]


class MissingInputError(RuntimeError):
    """⚠️★★★ 渡された入力が存在しない。★ **黙って捨てない**（fail-closed）。"""


def collect_paths(inputs: Sequence[str]) -> List[Path]:
    """ファイル / ディレクトリの混在を受け付け、`*.ndjson` を集める。

    ## ⚠️★★★ 存在しない入力は**黙って捨てない** (security-checker MEDIUM・2026-08-21)

    ★ 以前は `if is_dir() … elif exists() …` で **else が無かった**。
    → ⚠️ タイポや未マウントのパスを渡すと**その 1 本が消え、残りだけで判定して exit 0** になる。
    ⚠️★★★ **コホートが揃っていることを担保するゲートが、コホートの縮小を検知できない**
    ——本ゲートの存在理由そのものが崩れる。
    """
    out: List[Path] = []
    missing: List[str] = []
    for raw in inputs:
        p = Path(raw)
        if p.is_dir():
            out.extend(sorted(p.rglob("*.ndjson")))
        elif p.exists():
            out.append(p)
        else:
            missing.append(raw)
    if missing:
        raise MissingInputError(
            "入力が見つかりません: "
            + ", ".join(missing)
            + " ★ コホートが縮んだまま判定しないため、ここで止める"
        )
    return out


def preflight(
    inputs: Sequence[str],
    required: Sequence[str],
    allow_undecidable: bool = False,
) -> Report:
    """★ **解析スクリプトの 1 行目で呼ぶ**入口。誤読しうるなら例外を投げる。

    ⚠️ 戻り値を無視してもよいが、例外は握り潰さないこと ——
    握り潰した瞬間に ADR-013 が防ごうとした失敗が戻る。
    """
    # ⚠️ `MissingInputError` はそのまま伝播させる —— ★ 「入力が無い」と
    #   「入力はあるが読み方が危うい」は**別の失敗**であり、混ぜると原因が消える。
    paths = collect_paths(inputs)
    if not paths:
        raise CapabilitiesGateError(Report([], []))
    files = [read_file(p) for p in paths]
    report = judge(files, required)
    if report.worst_exit(allow_undecidable) != EXIT_OK:
        raise CapabilitiesGateError(report)
    # ⚠️★★ **黙って通さない** (code-reviewer MEDIUM・2026-08-21)。
    #   ★ CLI は `render()` に ⚠️ 行を出すが、Python API から呼ぶと
    #     `allow_undecidable=True` は**完全に無音**だった —— docstring の
    #     「警告に落とす」が実装されていなかった。
    #   ⚠️ 無音だと「判定不能を受け入れた」ことが `notes.md` に書かれないまま結論が出る。
    undecidable = [v.line_type for v in report.verdicts if v.verdict == UNDECIDABLE]
    if undecidable:
        print(
            "⚠️★★★ capabilities gate: 判定不能を明示的に受け入れました: "
            + ", ".join(undecidable)
            + " ★ notes.md の結論は『無かった』ではなく**『判定不能』**と書くこと。",
            file=sys.stderr,
        )
    return report


# --- 表示 ---------------------------------------------------------------------


def render(report: Report) -> str:
    """人が読む報告。★ **端末表示専用**である。

    ⚠️★★★ ここには**実ファイル名を出す**（人が該当ファイルを探せないと使えないため）が、
    ★ [`Report.as_dict`]（＝ `--json`・保存される側）には**出さない**。
    → `--json` を付けたときは本文を **stderr** へ出し、保存されるのは JSON だけにする
    （[`main`] を見よ）。⚠️ **本文をコミットする先へリダイレクトしないこと。**
    """
    lines: List[str] = []
    lines.append(f"--- 対象 {len(report.files)} ファイル ---")
    versions = sorted({f.app_version or "<none>" for f in report.files})
    declared = sum(1 for f in report.files if f.declared is not None)
    lines.append(f"  app_version: {', '.join(versions)}")
    lines.append(f"  capabilities を宣言しているファイル: {declared}/{len(report.files)}")
    if declared not in (0, len(report.files)):
        lines.append(
            "  ⚠️★★★ 宣言のあるファイルと無いファイルが混在している "
            "(★ 旧ビルドと新ビルドが同じコホートに入っている)"
        )
        # ★ 混在しているときだけ、どれが旧ビルドかを名前で示す（端末のみ）。
        #   ⚠️ これが無いと 63 ファイルの中から探せない。
        for f in report.files:
            if f.declared is None:
                lines.append(f"      旧: {f.path.name}  [file_id={file_id_of(f.path)}]")
    malformed = sum(f.malformed_lines for f in report.files)
    if malformed:
        lines.append(f"  ⚠️ 解釈できなかった行: {malformed}")
    lines.append("--- 判定 ---")
    for v in report.verdicts:
        mark = "  " if v.verdict in (PRESENT, SIGNAL_ABSENT) else "⚠️"
        lines.append(
            f"{mark} {v.line_type:22s} {v.verdict:18s} {v.rows:6d} 行  "
            f"[{', '.join(sorted(g or '<undeclared>' for g in v.groups))}]"
        )
        if v.note:
            lines.append(f"     {v.note}")
    return "\n".join(lines)


# --- 空振り検査 (--self-test) --------------------------------------------------

_META_NEW = (
    '{"type":"meta","session_start":1,"hmm_version":"0.4.0","app_version":"0.1.27",'
    '"capabilities":{"unconditional":["key","feat"],'
    '"threshold_gated":["hook_health","starve_window"],'
    '"config_gated":["probe_assignment"]}}'
)
_META_OLD = '{"type":"meta","session_start":1,"hmm_version":"0.3.0"}'


def _write(tmp: Path, name: str, lines: Sequence[str]) -> Path:
    p = tmp / name
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return p


def self_test() -> int:
    """⚠️ **検査自身が空振りしていないか**を確かめる (★ `check_vignettes.py` と同じ流儀)。

    ★ 判定表の 6 行すべてについて、**期待した verdict が出ること**を固定する。
    ⚠️ ここが常に緑を返すようになったら、本ゲートは「守っているつもり」に化ける。
    """
    import tempfile

    failures: List[str] = []
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)

        def verdict_of(files: Sequence[Path], line_type: str) -> str:
            facts = [read_file(p) for p in files]
            return judge(facts, [line_type]).verdicts[0].verdict

        # ① unconditional + 0 行 → SIGNAL_ABSENT
        a = _write(tmp, "a.ndjson", [_META_NEW, '{"type":"feat","t":1}'])
        if verdict_of([a], "key") != SIGNAL_ABSENT:
            failures.append("① unconditional の 0 行が SIGNAL_ABSENT にならない")

        # ② unconditional + 1 行 → PRESENT
        if verdict_of([a], "feat") != PRESENT:
            failures.append("② unconditional の 1 行が PRESENT にならない")

        # ③ threshold_gated + 0 行 → UNDECIDABLE (⚠️ 本ゲートの中心)
        if verdict_of([a], "starve_window") != UNDECIDABLE:
            failures.append("③ threshold_gated の 0 行が UNDECIDABLE にならない")

        # ④ config_gated + 0 行 → UNDECIDABLE
        if verdict_of([a], "probe_assignment") != UNDECIDABLE:
            failures.append("④ config_gated の 0 行が UNDECIDABLE にならない")

        # ⑤ 宣言に無い + 0 行 → INSTRUMENT_ABSENT (★ 過去 2 件の失敗)
        if verdict_of([a], "ime_shadow") != INSTRUMENT_ABSENT:
            failures.append("⑤ 未宣言の 0 行が INSTRUMENT_ABSENT にならない")

        # ⑥ 宣言に無い + 1 行 → DECLARATION_BUG
        b = _write(tmp, "b.ndjson", [_META_NEW, '{"type":"ime_shadow","t":1}'])
        if verdict_of([b], "ime_shadow") != DECLARATION_BUG:
            failures.append("⑥ 未宣言なのに実在する行が DECLARATION_BUG にならない")

        # ⑦ ⚠️ 旧ログ (capabilities キーが無い) → INSTRUMENT_ABSENT に倒す
        old = _write(tmp, "old.ndjson", [_META_OLD, '{"type":"key","t":1}'])
        if verdict_of([old], "starve_window") != INSTRUMENT_ABSENT:
            failures.append("⑦ 旧ログの 0 行が INSTRUMENT_ABSENT に倒れない")

        # ⑦b ⚠️★★★ 旧ログでも**行が実在すれば** PRESENT (★ DECLARATION_BUG にしない)。
        #     ⚠️ ここを間違えると、Phase1 の 63 ファイルが丸ごと「宣言のバグ」に化ける。
        if verdict_of([old], "key") != PRESENT:
            failures.append("⑦b 旧ログの実在する行が PRESENT にならない")

        # ⑧ ⚠️★★★ 新旧が混在したコホート → MIXED (★ 平均を取る前に止める)
        if verdict_of([a, old], "starve_window") != MIXED:
            failures.append("⑧ 新旧混在コホートが MIXED にならない")

        # ⑧b ⚠️ 「旧ログ」と「宣言はあるが載っていない」も **混ぜない**。
        #     ★ どちらも group が無い状態に見えるが、行が実在したときの読み方が逆である。
        if verdict_of([a, old], "ime_shadow") != MIXED:
            failures.append("⑧b 旧ログと未宣言ビルドの混在が MIXED にならない")

        # ⑨ ★ 正常系では exit 0 になること (⚠️ 常に赤なら検査として無意味)
        facts = [read_file(a)]
        if judge(facts, ["feat", "key"]).worst_exit() != EXIT_OK:
            failures.append("⑨ 読める行種だけを要求したのに赤になった")

        # ⑩ ⚠️ `--allow-undecidable` が UNDECIDABLE **だけ**を落とすこと。
        r = judge([read_file(a)], ["starve_window", "ime_shadow"])
        if r.worst_exit(allow_undecidable=True) != EXIT_INSTRUMENT_ABSENT:
            failures.append("⑩ allow-undecidable が INSTRUMENT_ABSENT まで見逃している")

        # ⑪ ⚠️★★★ 存在しない入力を**黙って捨てない** (fail-closed)。
        try:
            collect_paths([str(tmp / "does-not-exist.ndjson")])
            failures.append("⑪ 存在しない入力が黙って捨てられている (コホートが縮む)")
        except MissingInputError:
            pass

        # ⑫ ⚠️★★★ `--json` に**ファイル名を出さない** (擬似 ID × 打鍵時刻が漏れる)。
        payload = judge([read_file(a)], ["feat"]).as_dict()
        blob = json.dumps(payload, ensure_ascii=False)
        if a.name in blob or "path" in payload["files"][0]:
            failures.append("⑫ JSON にファイル名が出ている (コミットされると識別子が漏れる)")
        if len(payload["files"][0].get("file_id", "")) != 8:
            failures.append("⑫ file_id が出ていない (端末表示と突き合わせられない)")

        # ⑬ ⚠️ **入力ゼロを「読める」と言わない** (エラーパスの誤読)。
        #    ★ 比べるのは「緑の文言と一致しないこと」であって、部分文字列ではない
        #      (⚠️ 赤の文言にも説明として『読める』の語が入るため)。
        if Report([], []).summary() == Report(
            [read_file(a)], judge([read_file(a)], ["feat"]).verdicts
        ).summary():
            failures.append("⑬ 入力ゼロの失敗が、緑と同じ文言で報告されている")

    if failures:
        for f in failures:
            print(f"NG self-test: {f}", file=sys.stderr)
        return 1
    print(
        "OK self-test: 判定表の 6 行 + 旧ログ + 混在 + 正常系 "
        "+ 入力欠落の fail-closed + JSON の匿名化 が、いずれも期待どおり分岐する"
    )
    return 0


# --- CLI ----------------------------------------------------------------------


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="収集済みログの capabilities を機械判定する前処理ゲート (ADR-013)",
    )
    parser.add_argument("inputs", nargs="*", help="NDJSON ファイル、またはそれを含むディレクトリ")
    parser.add_argument(
        "--require",
        action="append",
        default=[],
        metavar="LINE_TYPE",
        help="解析が読む行種 (複数指定可)。★ 0 行を誤読しうるなら赤にする",
    )
    parser.add_argument(
        "--allow-undecidable",
        action="store_true",
        help="⚠️ UNDECIDABLE を警告に落とす (★ 解析が明示的に受け入れる場合のみ)",
    )
    parser.add_argument("--json", action="store_true", help="機械可読な JSON で出す")
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="⚠️ 検査自身が空振りしていないか確かめる",
    )
    args = parser.parse_args(argv)

    if args.self_test:
        return self_test()

    if not args.inputs or not args.require:
        parser.print_usage(sys.stderr)
        print(
            "⚠️ 入力と --require の両方が要る。★ 『何を読むか』を宣言しない解析は検査できない。",
            file=sys.stderr,
        )
        return EXIT_USAGE

    # ⚠️★ `meta` は**どの群にも載せない**設計である (`capabilities.rs`: その行が
    #   宣言そのものを運ぶので、自分を宣言しない)。★ そのまま `--require meta` すると
    #   `DECLARATION_BUG` になり、⚠️ **判定表の読み違いに見える**。→ 先に断る。
    if "meta" in args.require:
        print(
            "⚠️ `--require meta` は使えません。★ `meta` 行は宣言そのものを運ぶので、"
            "どの群にも載っていません (capabilities.rs の設計)。"
            "meta の有無は `declares_capabilities` で分かります。",
            file=sys.stderr,
        )
        return EXIT_USAGE

    try:
        paths = collect_paths(args.inputs)
        files = [read_file(p) for p in paths]
    except MissingInputError as e:
        # ⚠️ 黙って縮んだコホートで判定しない (fail-closed)。
        print(f"⚠️★★★ {e}", file=sys.stderr)
        return EXIT_USAGE
    if not paths:
        print("⚠️ 対象の .ndjson が 1 本も見つからない", file=sys.stderr)
        return EXIT_USAGE

    report = judge(files, args.require)
    if args.json:
        # ⚠️★★★ **人が読む本文は stderr へ**。★ 保存されるのは JSON だけにする
        #   (`render` には実ファイル名が入るので、コミットされる先へ流さない)。
        print(render(report), file=sys.stderr)
        print(json.dumps(report.as_dict(), ensure_ascii=False, indent=2))
    else:
        print(render(report))

    code = report.worst_exit(args.allow_undecidable)
    if code != EXIT_OK:
        print(f"\n⚠️★★★ {report.summary()}", file=sys.stderr)
        print(
            "★ 0 行を『信号が無かった』と読んではならない (ADR-013 D1)。"
            "解析を止めるか、結論の書き方を『判定不能』に変えること。",
            file=sys.stderr,
        )
    return code


if __name__ == "__main__":
    sys.exit(main())
