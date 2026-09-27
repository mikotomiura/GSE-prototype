# issue 計画 — 依存 DAG と Allowed Files 交差表

> `issue-slicing` skill（Opus・2026-09-27）で分解。grill の出力は `requirement.md` / `decisions.md`。
> 実行モードは **C**（`_loop-config.json.mode = "C"`・研究者裁定）。

## 依存 DAG

```
ウェーブ 1（並列可能・Allowed Files 交差ゼロ）
  001  validate_blocks.py の未完了マーカー          [parse]
  002  analyze.py の n 未達ゲート ＋ 登録k/解析m     [recheck]
  004  T3 構築仕様書                                 [parse]
  005  consent 差分案（実ファイル不変）              [recheck]
        │      │      │
        └──────┴──────┘（001 / 002 / 004 の成果を検査 [9] と参照が指す）
ウェーブ 2
  003  G1 削除保証台帳 ＋ ゲート検査 [9]            [recheck]
```

- **循環なし**（依存は 003 → {001, 002, 004} の一方向のみ。005 は完全独立）。
- **最長 chain = 2 段**（直列時の総 attempt 見積り: 2 × `max_attempts` 6 = 最大 12 attempt）。
- ⚠️ `parallel` は **1**（直列）に pin してある。理由: 003 以外は並列可能だが、
  ★ **モード C をこのタスクで初めて Python 系の verify で回す**ので、
  `docs/loop-engineering.md` 逐語「新しい実行モードを初めて使う時は、最も安い issue 1 本を
  `parallel=1` で回して基盤を検証する」に従う。基盤が緑なら `parallel` を上げてよい。
- ★ **最初に回すのは 004**（最も安い・文書のみ・pin 済み verify の前提に触らない）。
  ⚠️ `--issues 004` で 1 本だけ回して基盤を確かめてから残りへ進む。

## Allowed Files 交差表

| | 001 | 002 | 003 | 004 | 005 |
|---|---|---|---|---|---|
| **001** `validate_blocks.py`, `protocol.md` | — | ∅ | ∅ | ∅ | ∅ |
| **002** `analyze.py`, `config.json` | ∅ | — | ∅ | ∅ | ∅ |
| **003** `docs/g1-deletion-ledger.md`, `docs/o1-deletion-ledger.md`, `docs/agent-shared.md`, `scripts/check-g1-collection-readiness.sh` | ∅ | ∅ | — | ∅ | ∅ |
| **004** `docs/person-lifecycle-ledger-template.md` | ∅ | ∅ | ∅ | — | ∅ |
| **005** `.steering/20260927-precondition8-t3-and-consent/consent-diff-proposal.md` | ∅ | ∅ | ∅ | ∅ | — |

★ **交差はゼロ**（∅ = 共通要素なし）。したがって基準 3 の意味では 5 本すべて並列可能で、
003 の直列化は**ファイルの交差ではなく「参照先の実体が要る」ため**である（`## Dependencies` に明記）。

### ⚠️ 交差を避けるために意図した配置（★ 後から崩さないこと）

| 判断 | 理由 |
|---|---|
| `docs/agent-shared.md`（リンクハブ）を **003 が 2 文書ぶん一括**で足す | ★ 003 と 004 の両方が 1 行ずつ足すと**同一ファイルが交差**して並列不可になる |
| 005 の Allowed Files を**提案ファイル 1 本**に閉じる | ⚠️★★★ 被験者向け文書（契約）を Loop が書き換える経路を**構造的に**無くす。★ 反映は研究者 |
| 001 が `protocol.md` を持つ / 005 は持たない | ★ 005 は**提案のみ**なので実ファイルを要求しない。→ `protocol.md` の交差が起きない |
| 002 が `config.json` を持つ | ★ 門の鍵（`recruitment_closed`）と読む側（`analyze.py`）は**1 issue に収める**（縦切り） |

## verify_level の選別（基準 5）

| issue | level | 根拠 |
|---|---|---|
| 001 | `parse` | 報告のみ。AC は selftest の exit code で完全に言える |
| **002** | **`recheck`** | ⚠️ **データ判定ロジック**（optional stopping の門を緩める方向の変更）＋ 事前登録の契約に触る |
| **003** | **`recheck`** | ⚠️ **同意の履行（削除保証）** ＋ 収集開始ゲートを変える |
| 004 | `parse` | 文書のみ。AC は grep で完全に言える |
| **005** | **`recheck`** | ⚠️ **被験者向け文書（契約）** に関わる。★ AC2「実ファイル不変」を客観で再確認させる |

★ recheck は 3 / 5 件（⚠️ 全部 parse にしていない）。

## 分解の締めの自己検査

- [x] 各 issue を単体 merge しても main が壊れないか
      → 001/002 は後方互換（キー無しで従来挙動）／003/004/005 は追加のみ。★ すべて単独で merge 可能。
- [x] 各 AC に対応する test 名 / コマンドを「今」書けるか → 5 本すべて AC 表に記載済み。
- [x] Allowed Files 交差表を作ったか → 上表（交差ゼロ）。
- [x] DAG に循環がないか・最長 chain は何段か → 循環なし・**2 段**。
- [x] recheck を基準 5 で選別したか → 3 件（002 / 003 / 005）。
- [x] AC が書けない「リファクタするだけ」の issue を作っていないか → 無い。
- [x] pin 済み verify の前提を変える issue を最初の単独ウェーブに置いたか
      → ★ `verify.test` は 2 本の `--selftest`。**それを書き換える 001 / 002 がウェーブ 1** に在る。
- [x] test/lint が無条件に緑になる issue に `acceptance.sh` を書いたか
      → ★ **5 本すべてに `00X-acceptance.sh` を置いた**（003/004/005 は verify が無条件に緑になるため必須）。

## ⚠️ 実行前に確認すること（★ モード C の 3 条件・`docs/loop-engineering.md`）

1. **events を書くのは `loop-run.sh` だけ** → worker に書かせない。
2. **AC の検証コマンドが `verify` / `acceptance` に載っているか** → ★ 5 本すべて `acceptance` に載せた。
3. **verify がベースラインで緑** → ✅ 2026-09-27 に実測（下記）。

```
python3 .../validate_blocks.py --selftest   → exit 0
python3 .../analyze.py --selftest           → exit 0
python3 -m py_compile （2 ファイル）        → exit 0
bash -n scripts/check-g1-collection-readiness.sh → exit 0
```

⚠️ `bash scripts/check-g1-collection-readiness.sh`（`--selftest` 無し）は
**未達 3 件で exit 非 0 になりうる**ので `verify` に入れていない（★ `ci_command` 側で `--selftest` を回す）。

## 起動

⚠️ 第 1 引数は **task ディレクトリのパス**である（★ task 名ではない。`loop-run.sh:12` 逐語
「使い方: bash scripts/loop-run.sh <task-dir> [--parallel N] [--issues 001,002] [--dry-run]」）。

```bash
# ★ 基盤検証: 最も安い 1 本だけ
bash scripts/loop-run.sh .steering/20260927-precondition8-t3-and-consent --issues 004
# 緑なら残り（003 は依存が満たされてから自動で回る）
bash scripts/loop-run.sh .steering/20260927-precondition8-t3-and-consent
```

⚠️★★★ **`/clear` して新セッションで実行を始める**（分解セッションの前提を持ち込まない）。
