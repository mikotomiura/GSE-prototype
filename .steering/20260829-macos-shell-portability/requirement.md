# macOS 実機で O1 配布ゲートを正しく測れるようにする（bash 3.2 / BSD od 移植性）

## 背景

`.steering/_handoff/next-session-prompt-o1-macos-distribution.md` は「macOS 実機で O1 の
配布物を作り、通し確認する」ことを次セッションの主題としている。そのメモは §0-1 で
**機械の状態**を次のように書いていた:

| ゲート | メモの記載 | ★ macOS 実機での実測（2026-08-29） |
|---|---|---|
| `scripts/check-o1-release-readiness.sh` | 通過 16 / 未達 1 | ⚠️ **通過 15 / 未達 2** |
| `make-common-app-zip.sh --selftest` | 14/14 | ⚠️ **通過 16 / 失敗 1**（項目数も違う） |

★ メモと実体が食い違ったので一次資料まで降りたところ、**差分の 3 件はすべて
「macOS でだけ壊れる」移植性の欠陥**であり、⚠️ **うち 1 件は本番コードの欠陥**だった。

### ★ 実測で確定した 3 件

#### (1) ⚠️★★★ `scripts/sync-session.sh:161` — O1 ガードが `exit 4` を返せない（**本番コードの欠陥**）

```
$ bash scripts/sync-session.sh /tmp/…/gse_o1_20260828_120000.ndjson --no-commit
scripts/sync-session.sh: line 161: why?: unbound variable
exit=1
```

★ 当該行は `echo "… 同期しません（$why）" >&2` で、⚠️ **`$why` の直後が全角 `）`**。
★ **macOS 標準の bash 3.2 は多バイト文字を変数名の一部として読む**ため、
`why<byte>` という存在しない変数になり、`set -u` のもとで落ちる。最小再現:

```bash
$ printf 'set -u\nv=OK\necho "A: $v）"\n' > /tmp/mb.sh && /bin/bash /tmp/mb.sh
/tmp/mb.sh: line 3: v?: unbound variable   # rc=1
```

⚠️ 結果として **`exit 4`（O1 を弾いた）に到達できず `exit 1`（cargo 失敗）を返す**。
★ 同期そのものは非 0 で止まる（fail-closed）ので**被験者データの流出には至らない**が、
⚠️ **exit code の契約が壊れており、ガードの検査 6 件が全部赤**になっている。

#### (2) `scripts/sync_session_o1_guard_test.sh:96` ほか — 検査側が同型で死ぬ

`line 96: rc?: unbound variable` で **テストが途中で終了**し、
⚠️ 以降のケース（境界・陽性対照・PowerShell 実装との突き合わせ）が**1 件も走っていない**。

#### (3) `make-common-app-zip.sh` `bom_crlf_ok` — BOM 検査が macOS で常に不成立（**偽陽性**）

```
$ head -c 3 launch-g1-windows.bat | od -An -tx1
           ef  bb  bf
$ … | grep -q 'ef bb bf' && echo MATCH || echo "NO MATCH"
NO MATCH
```

★ **macOS(BSD) の `od -An -tx1` はバイト間を 2 スペースで区切る**（GNU coreutils は 1）。
→ `grep 'ef bb bf'` が **macOS では必ず外れる**。⚠️ launcher の実体は
**BOM(`ef bb bf`) ＋ 全行 CRLF（CR=LF=109 / 62）で正常**であり、赤は**測定器側の誤り**。
⚠️★ しかも BOM 検査が常に false を返すため、隣の**陽性対照（壊した複製を捕まえる）まで
自動的に緑**になり、空回りを検出できない状態だった。

### ★ この 3 件が意味すること

⚠️★★★ **配布の可否を判定する 2 つのゲートが、macOS では正しく測れていない。**
★ ハンドオフメモが指示する作業（本番 zip の作成・実機通し確認）は、
**ゲートが真実を返すようになってから**でなければ「緑だから配ってよい」と言えない。

★ さらに `experiments/20260801-controlled-friction-task/prepare-subjects.sh:234` には

```
#   `$DRIVE（` は `DRIVE（` という別の（存在しない）変数になり、`set -u` で落ちる（実測）。
```

という **同じ罠を過去に踏んだ実測コメントが既にあった**。⚠️ にもかかわらず
**その 1 箇所しか直されておらず、リポジトリ全体では 17 箇所残っていた**。
★ memory `name-lookup-only-works-within-one-source` と同型（1 つの真実源の中でしか効かない対策）。

## ゴール

⚠️★ **macOS 実機で 2 つのゲートが「実体どおりの結果」を返す状態にする。**

1. `sync-session.sh` の O1 ガードが macOS でも **`exit 4`** を返す
2. `sync_session_o1_guard_test.sh` が **最後まで走り切る**（途中で死なない）
3. `make-common-app-zip.sh --selftest` の BOM 検査が **実体を測る**（macOS/GNU 両方で）
4. ★ 同型の欠陥が **再び入らない検査**を置く（1 箇所直して終わりにしない）
5. ★ ダミー設定で `--mode o1` の**検算ラン**を通し、8 項目を実測する

## スコープ

### 含むもの
- ★ bash 3.2 で壊れる `$var` ＋ 多バイト文字を **リポジトリ全体で** `${var}` へ直す（17 箇所）
- ★ `bom_crlf_ok` の BOM 検査を **BSD/GNU 両対応**に直す
- ★ 移植性の回帰検査を新規に置き、`check-o1-release-readiness.sh` から呼ぶ
  （⚠️ 陽性対照つき。★ 検査自体が空回りしないことを固定する）
- ★ **ダミー設定**での `--mode o1` 検算ラン（⚠️ 送信は一切しない）

### 含まないもの
- ⚠️ **本番 zip の作成**（`Form_O1/o1_submit.json` を使う経路）→ 次セッション
- ⚠️ **macOS 実機の通し確認**（§1-D の 8 手順・研究者が操作）→ 次セッション
- ⚠️ **Drive 配布フォルダへの配置**・**送信 timeout の実測**（§1-E-4）→ 次セッション
- ⚠️ README の `【ドラフト・未承認】` 解除（★ 実機で手順を踏んでからでないと承認できない）
- ⚠️ `TAG` 既定値 `v0.1.24` の書き換え（★ G1 実施中のため触らない）

## 受け入れ条件

- [ ] `bash scripts/sync_session_o1_guard_test.sh` が **最後まで走り**、O1 の 6 ケースが緑
- [ ] `bash scripts/sync-session.sh <gse_o1_*.ndjson> --no-commit` が **exit 4**
- [ ] ★ 通常セッションは弾かれない（**exit 4 以外**＝ ガードを通り抜けた証拠）
- [ ] `make-common-app-zip.sh --selftest` の launcher バイト形式が緑、かつ**陽性対照も緑**
- [ ] ★ 移植性検査が **0 件**を返し、⚠️ **わざと壊した複製では赤になる**（陽性対照）
- [ ] `check-o1-release-readiness.sh` の未達が **「送信 timeout 未実測」1 件のみ**になる
- [ ] ★ `--mode o1 --tag v0.1.29 --config <ダミー>` の検算ランが通り、8 項目を実測できる

## 関連ドキュメント

- `.steering/_handoff/next-session-prompt-o1-macos-distribution.md`（本タスクの発端）
- `docs/agent-shared.md` CI / 運用上の注意（★ 「Hook はすべて bash 前提」）
- `docs/o1-deletion-ledger.md` §4（★ O1 ガードが守っている約束）
- memory `silent-failure-in-guard-scripts` / `measurement-instrument-false-positives`
- memory `name-lookup-only-works-within-one-source`

## 運用メモ

- /reimagine 適用: **No**
- 理由: ★ 3 件とも**真因が実測で特定済み**（bash 3.2 の変数名パース / BSD od の区切り幅）で、
  直し方が一意（`${var}` 化 / 空白除去して比較）。⚠️ 設計上の選択肢が割れる余地が無い。
- スコープの確定: 研究者の回答（2026-08-29）
  - ★ 本セッションは「**非互換修正 ＋ 検算ランまで**」。本番 zip と実機操作は次セッション
  - ★ Intel Mac の被験者は「**いない / Apple Silicon のみ**」→ aarch64 のみで進める
