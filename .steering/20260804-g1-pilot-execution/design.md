# 設計 — G1 パイロット P-1 の前日準備

## 実装アプローチ

**「決まったことを実体に反映する」だけ**。事前登録の判定基準（`§3.1〜§3.6`）には一切触れない。
変更は 3 種類に分かれる:

1. **実装の穴を塞ぐ**（`assign.py --pilot-topic`）— 2 端末実施の決定（G-1/G-4）が要求する
2. **文書と実体のズレを消す**（Z-1 / Z-2 / Z-4）— 当日そのまま追うと事故になるもの
3. **当日の手作業を減らす**（launcher / 記録用紙 / `env.md` 記入枠）

### ★ 本ラウンドで実測して分かったこと（一次資料・`verify-before-claiming`）

| # | 検証したこと | 結果 |
|---|---|---|
| **V-1** | `gh release view v0.1.22` のアセット | ★ **5 件**（`gse-next.exe` / `*.dmg` / `gse-submit.exe` / `gse-unpack` / `gse-unpack.exe`）。引き継ぎの「9 件」は古い |
| **V-2** | `v0.1.21..v0.1.22` のアプリコード差分 | ★ **kill switch（`GSE_DISABLE_PROBES`）と回帰テスト追加のみ**。計測・HMM・UI は無変更。`HMM_VERSION = "0.3.0"` 据え置き |
| **V-3** | 週セレクタの既定値（`App.tsx:119`） | ★ `week1_blind` が既定。**起動後に触らなければ第 1 週（blind 較正）** |
| **V-4** | macOS で `VAR=1 open -a App` が環境変数を渡すか | ★ **渡る**。テスト用 .app を作って実測（`open --env` でも直接実行でも渡る）。⚠️ ただし **`ps eww` では検証できない**（macOS は他プロセスの環境を出さない。`PATH` すら見えない）ので、その手法で「渡っていない」と結論してはならない |
| **V-5** | `tauri.conf.json` の `productName` | ★ **`gse-next`**。`protocol.md §1.1` の `open -a GSE` / `GSE.exe` は**起動しない名前**（Z-4） |
| **V-6** | `validate_blocks.py` のパイロット判定 | `confirmatory is False` を見ており **subject 名に依存しない**。`blocks/*.json` を glob するのでファイル名は自由 |
| **V-7** | `bash run.sh` | 変更前の時点で **GREEN**（資材・自己検証・kill switch 挙動テストを含む） |

## 変更対象

### 修正するファイル

- `experiments/20260801-controlled-friction-task/assign.py`
  — `--pilot-topic N`（既定 1・範囲 1..8）を追加し、既存の `pilot_assign(seed, topic)` を CLI に露出する。
  `--pilot-topic` は `--pilot` と併用時のみ有効（単独指定はエラー）。`--selftest` に検査を追加。
  ★ **`rng_for(seed, "PILOT")` のキーは変えない** → `--pilot` 単独の出力は **byte 互換**を保つ。
- `experiments/20260801-controlled-friction-task/protocol.md`
  — **Z-2**: `§6` の当日チェックリストを「P-1（4 ブロック）」と「確証（10 ブロック）」に分け、
    ★ **P-1 では強制比較を取らない**（`§2.8`）を明記する。
  — **Z-4**: `§1.1` の起動コマンドを `gse-next` に直し、
    ★ **既に起動していると `open -a` は新プロセスを作らない**（＝環境変数が適用されない）ことと、
    launcher を使う手順を書く。
  — `§5` に「P-1 を 2 端末 × 2 題材で回す」運用（G-1/G-4）を追記する。
- `experiments/20260801-controlled-friction-task/env.md`
  — P-1 の記入枠（HMM_VERSION / OS / ビルドタグ / `GSE_DISABLE_PROBES` / 題材）を 2 回分用意する。
- `experiments/20260801-controlled-friction-task/notes.md`
  — P-1 の節を起こし、G-1〜G-4 と Z-1〜Z-4 を記録する。
- `experiments/20260801-controlled-friction-task/make-handouts.sh`
  — P-1 用の記録用紙を `handouts/` に生成する（既存の md→docx 経路に 1 本足す）。
- `.steering/_handoff/next-session-prompt-g1-pilot-execution.md`
  — **Z-1**: `T-1` を 5 アセット・portable exe の実体に直す。`T-2` のアプリ名を直す。
    `§2` に「P-1 では G1-M を取らない」を追記する。

### 新規作成するファイル

- `experiments/20260801-controlled-friction-task/launch-g1-macos.command`
  — ★ 既存インスタンスを `osascript -e 'quit app "gse-next"'` で確実に終了 → 1 秒待つ →
    `GSE_DISABLE_PROBES=1 open -a gse-next`。★ **10 回のうち 1 回抜ける**手打ちを構造的に排除する。
- `experiments/20260801-controlled-friction-task/launch-g1-windows.bat`
  — `set GSE_DISABLE_PROBES=1` → `start "" gse-next.exe`。
    ⚠️ **BOM ＋ CRLF ＋ `chcp 65001` を日本語より前**に置く（Phase1 の launcher 文字化けの再発防止）。
- `experiments/20260801-controlled-friction-task/record-sheet-pilot.md`
  — P-1 用の記録用紙（**4 ブロック版**・強制比較欄なし）。`make-handouts.sh` が .docx にする。
- `.steering/20260804-g1-pilot-execution/decisions.md` — G-1〜G-4 と Z-1〜Z-4 の根拠。

### 生成するが**コミットしないもの**

- `blocks/PILOT-win.json`（topic01）/ `blocks/PILOT-mac.json`（topic02）
  — `blocks/.gitignore` 済み。★ **NDJSON も CSV も repo に置かない**。

## 影響範囲

| 変更 | 影響 | 対処 |
|---|---|---|
| `assign.py` に引数追加 | `run.sh` の `assign.py --selftest`、`validate_blocks.py` の割付再生成 | ★ `--pilot` 単独の出力を変えないので既存経路は不変。`run.sh` を再実行して GREEN を確認する |
| `protocol.md` の章立て変更 | `run.sh` が protocol の節を grep している可能性 | ★ `run.sh` を再実行して確認する（節を消さず**追加**する方針） |
| launcher 追加 | 無し（新規ファイル） | — |
| ⚠️ **アプリのコード** | ★ **変更しない**。`v0.1.22` のバイナリで回す | `run.sh` の「未コミット変更が無い」検査が守る |

## 既存パターンとの整合性

- `assign.py` の CLI は `argparse` ＋ `--selftest` 内蔵。**同じ形に足す**（新しい検証系を作らない）。
- 決定性: 割付は `SEED` から決まる。★ **`rng_for` のキーを変えない**ことでこの性質を保つ。
- 配布物は「`.md` が真実源 → `make-handouts.sh` が `.docx` を生成（`.gitignore`）」。
  ★ 記録用紙も**同じ経路**に乗せる（片方だけ直すとズレる）。
- launcher は `scripts/` ではなく **実験ディレクトリ配下**に置く。G1 実施専用であり、
  `scripts/` の被験者配布物（Phase1 系）と混ざると配り間違える。

## ★ 未決の論点（研究者判断が要る）

**P-1 を 2 回回す順序と間隔。** 推奨は次のとおり:

1. **Windows（topic01）を先**。★ `ime_dwell_med` が取れる設計どおりの 14 特徴で、
   まず「5 分で十分な打鍵が出るか」の**主たる答え**を取る。
2. **macOS（topic02）は同日なら 60 分以上空ける**か、**翌日**にする。
   ⚠️ P-1 の目的は打鍵量の測定なので、連続実施の疲労は測定を歪める。
3. どちらの回も `env.md` に **OS・題材・実施順**を記録する（`§5.1-4` の報告義務）。

## テスト戦略

- **自己検証**: `assign.py --selftest`（`--pilot-topic` の範囲外・`--pilot` 非併用・topic=1 の後方互換）
- **統合**: `bash run.sh` が GREEN のまま（変更前が GREEN であることは V-7 で実測済み）
- **転記検証**: `blocks/PILOT-win.json` / `PILOT-mac.json` を置いて `python3 validate_blocks.py` が緑
- ⚠️ **E2E（実機）は当日**。`GSE_DISABLE_PROBES` が本当に効いたかは
  ★ **実施後に `validate_blocks.py --dataset` が `probe_assignment` 行 0 で検査する**（自己申告にしない）
- ❌ アプリのビルド・`cargo test` は走らせない（**コードを変えないため**）

## ロールバック計画

- すべて `.md` / `.py` / launcher の追加であり、**アプリのバイナリに触れない**ので
  `git checkout -- experiments/ .steering/` で完全に戻る。
- `assign.py` は `--pilot` 単独の出力が byte 互換なので、**戻しても既存の割付は再現する**。
