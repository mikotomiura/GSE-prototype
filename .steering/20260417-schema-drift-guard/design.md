# 設計 (v2)

## 実装アプローチ

schema parity check の実ロジックを **Python スクリプトに一元化**し、
`sync-all.ps1` と `sync-all.sh` はその Python スクリプトを呼ぶだけに
留める。

```
  sync-all.ps1 ──┐
                  ├──> python scripts/check_schema_parity.py --dataset $DATASET_ROOT
  sync-all.sh ──┘            │
                              ▼
                  diff・修復手順提示・exit code
```

### なぜ Python 化するのか

- **ロジック重複の排除**: ps1 と sh の 2 言語で同じアルゴリズムを書くと、
  いずれ片方だけ修正されてズレる。1 ヶ所に集約すれば drift しない。
- **gse-dataset 側に既に Python 依存**: `validate_schema.py` が
  `$DATASET_ROOT/scripts/` に既存であり、Python 実行環境はセットアップ済。
  新規依存を足さない。
- **比較アルゴリズムの柔軟性**: 「単純バイト一致」「JSON 意味同値」「特定
  キーだけ比較」などの方針切替を shell で書くと破綻する。Python なら
  `json.load` + `==` で意味同値を素直に書ける。
- **ドリフト時の diff 出力の質**: `difflib.unified_diff` が shell の
  `diff` コマンドより可搬性が高く、出力が安定する。

### 比較の粒度: 「意味同値」を採用

byte-equal ではなく **`json.load` 後のオブジェクト同値** を採用する。
理由:

- schema ファイルは機械生成だが、**改行コード (CRLF/LF) や末尾 newline は
  環境差で揺れる**。Windows チェックアウト時の `core.autocrlf` が最大の
  要因。これを「ドリフト」と報告すると false positive が多発し、pre-flight
  が形骸化する恐れ。
- JSON の意味同値で比較すれば、スキーマ定義としての実質的な drift だけを
  検出できる。キー順序の揺れも許容する (`sort_keys=True` で正規化してから比較)。
- **注意**: CI が担う tier-1 (schema_dto.rs → current.json) の byte-equal
  drift 検知とは別レイヤ。本タスクの pre-flight は「JSON 意味論として
  2 ファイルが等価か」にフォーカスする。

### スクリプトの契約

```
$ python scripts/check_schema_parity.py --dataset <path>

Exit codes:
  0 = schemas match (JSON semantic equal)
  1 = drift detected (両ファイル存在するが内容が異なる)
  2 = src-tauri/schema/current.json 不在
  3 = $DATASET_ROOT/schema/current.json 不在
  4 = invalid arguments / I/O error
```

drift 時の stdout:

```
[check_schema_parity] DRIFT detected between:
  A: src-tauri/schema/current.json
  B: <DATASET_ROOT>/schema/current.json

First differences (unified diff, first 30 lines):
  <difflib output>

Missing variants in B: ime_shadow, review_marker
Extra variants in B: (none)

To fix (typical case: B is stale after schema_dto.rs update):
  cd src-tauri && cargo run --bin emit_schema > schema/current.json
  cp src-tauri/schema/current.json <DATASET_ROOT>/schema/current.json
  (then commit both sides)
```

「missing / extra variants」の分析を入れることで、どの方向のドリフトか
人間が即理解できる。

## 変更対象

### 修正するファイル

- `scripts/sync-all.ps1` — 先頭付近に `python scripts/check_schema_parity.py
  --dataset $DatasetRoot` 呼び出しを追加。exit != 0 なら script 自体も exit。
- `scripts/sync-all.sh` — 同上。`python` / `python3` の両方を試す
  フォールバックを持たせる (`command -v python3 || command -v python`)。
- `docs/development-guidelines.md` §10.3 — pre-flight ヘルパー の存在と
  契約 (exit code 意味) を追記。§10.2 にはバッチ同期が helper を呼ぶ点を
  1 行追記。

### 新規作成するファイル

- `scripts/check_schema_parity.py` — 本タスクの中核。~60 行想定。
  - 引数パース (`argparse`)
  - 両 JSON の `json.load` + `sort_keys=True` による正規化
  - `difflib.unified_diff` でドリフト時の diff
  - variant enum 抽出・差分分析 (JSON schema の "enum" フィールド走査)

### 削除するファイル

- なし

## 影響範囲

- **通常ケース**: Python 起動 + JSON load = ~100ms 程度。体感変化なし。
- **Python 未セットアップ環境**: 現状 `validate_schema.py` を動かしている
  環境では必ず利用可。新たな依存増加なし。
- **初回 (gse-dataset/schema/ 不在)**: exit 3 を shell が拾って
  修復手順を表示し停止。
- **docs 更新**: §10.2 / §10.3 への追記のみ。他ドキュメントは無影響。

## 既存パターンとの整合性

- `scripts/check_schema_parity.py` のコード規約: gse-dataset の
  `validate_schema.py` と同じスタイル (shebang `#!/usr/bin/env python3`、
  `argparse` / `pathlib` / `sys.exit` のイディオム)。
- shell 側は既存の `$EXIT_OK=0 / $EXIT_CARGO=1 / $EXIT_GIT=3 /
  $EXIT_PRECONDITION=4` パターンを尊重し、新しいコードは使わず helper の
  exit code をそのまま shell の exit code として流す。
- PS 5.1 quirk: §10.2.1 に記載された「Python コマンド呼出しの流儀」を
  既存 `sync-session.ps1:131` が使っているのと同じ `& python <script> <args>`
  形式を採用。

## テスト戦略

スクリプト向け自動テストは project 上存在しない。そこで **Python helper
単体に unittest を付ける** 方針:

- `scripts/tests/test_check_schema_parity.py` — `tmp_path` を使って
  - 一致ケース → exit 0
  - 意味同値だが改行だけ違う → exit 0 (false positive しない)
  - enum 片側に variant 追加 → exit 1 + missing variant に名前が載る
  - src-tauri 側ファイル不在 → exit 2
  - dataset 側ファイル不在 → exit 3
- `python -m unittest scripts.tests.test_check_schema_parity` をローカル回帰として走らせる

shell 側の回帰テストは手動:
- 通常 dry-run
- 一時的にドリフトを作って dry-run → exit code 観察
- `$DATASET_ROOT/schema/current.json` を rename して dry-run → exit 3 観察

## ロールバック計画

- `check_schema_parity.py` の追加 + sync-all への呼び出し追加は同一 commit。
  問題があれば 1 revert で完全に戻せる。
- 既存の sync-all は helper を呼ぶ 1 行 + exit chain の数行のみ変化なので、
  revert 後も既存ロジックはそのまま動く。

## 実装時の注意

- `check_schema_parity.py` は `#!/usr/bin/env python3` と **UTF-8 固定**で
  書く。Windows 日本語環境で `encoding='utf-8'` 指定を `open()` に明示しないと
  CP932 で読み込み例外になる。
- Python から stderr に書く場合 PS5.1 は warning 扱いしないが、exit code を
  尊重して shell 側で判定する (`$LASTEXITCODE` は §10.2.1 の消費問題があるので
  ps1 側で helper 実行直後に cache する)。
- difflib 出力は長くなりがちなので **最初 30 行でクリップ**し、「続きは手動
  diff で」とメッセージに含める。

## 設計判断の履歴
- 実行回数: 1 回目
- 採用: v2 (Python helper 集約案)
- 根拠: v1 が生み出す「ps1/sh 2 言語同期」構造は、本タスクが防ごうと
  している "2 ヶ所同期忘れ" 問題と同型の再帰を生む。v2 は helper 集約で
  この再帰を断ち、かつ Windows BOM/CRLF 誤検出リスクも排除できる。
  詳細な比較は design-comparison.md を参照。

## 実装時の判明事項 (2026-04-17 記録)

### PS 5.1 quirk が予想より深刻

当初 `& python ...; $LASTEXITCODE` で済むと想定したが、
`.ps1 -File` invocation + `[CmdletBinding()]` の組合せで以下を実測:

- `$LASTEXITCODE` が null 化する (`-Command` 経由なら取得可)
- `$parityOutput = & python ... | Out-String` の結果が空になる
- `@(& python ... 2>&1)` の配列キャプチャで stderr が欠ける
- `"$var arg"` の unquoted interpolation で変数が null 化 (`"$var"` とクオート必須)
- `Write-Host` による **pre-access** を挟まないと interpolation が再発

最終形は helper 側に `--machine-readable` を追加し、
**stdout 最終行**に `HELPER_EXITCODE=<n>` (0..4) を出力する契約を導入。
ps1 は `@(& python "$x" "$y" --machine-readable 2>&1)` で配列キャプチャ →
regex で `HELPER_EXITCODE=(\d+)` を抽出して shell の exit に渡す。
stderr ではなく **stdout** に出す理由: `[CmdletBinding()]` 下で stderr が
ErrorRecord に変換されて `2>&1` でも pipe 回収できない事象があるため。

### bash 側の set -e quirk

`if ! cmd; then rc=$?` は then ブロック内で `$?` が 0 に化ける (bash の
挙動)。実装当初これを踏んで drift 時に shell exit=0 となり誤動作した。
正解は `cmd || rc=$?` 形式。sync-all.sh の Step 2 の `if/else` 形は
if 条件内で set -e がサスペンドされる規則で正常動作するが、将来回帰を
防ぐためコメントで明記した (reviewer HIGH #2)。

### helper の強化ポイント (reviewer/security 指摘反映)

- `_collect_type_enums` を再帰→スタックイテレートに変更
  (深い schema での RecursionError 回避)
- `"type": {"const": "..."}` 形式のタグ (単一 variant serde タグ) にも対応
- JSON parse error と I/O error を別メッセージで報告 (どのファイルが壊れたか明示)
- テスト追加: invalid JSON / UTF-8 BOM / const-tag variant / sentinel 検証 (計 12 ケース)

### 動作確認サマリ

| shell | normal | drift | missing |
|---|---|---|---|
| PowerShell (sync-all.ps1) | exit 0 | exit 1 | exit 3 |
| bash (sync-all.sh) | exit 0 | exit 1 | exit 3 |
| Python unittest | 12/12 PASS | — | — |
