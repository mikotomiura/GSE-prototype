# §2 稼働コスト実測 — Windows 実機ログ (2026-09-09 16:16 〜 09-10 00:16 JST)

ビルド: commit `22538ccb5654c6e55a6ac0327cf7ece3b2f9dfd9`（`npm run tauri build -- --no-bundle`
で作成。判断3。現HEAD `8146f08` と build-relevant path 上等価）の `src-tauri/target/release/gse-next.exe`
（同フォルダに `o1.mode` を配置）。実測データの詳細な解析経過は
`experiments/20260903-o1-runtime-cost/notes.md`（2026-09-10 追記節）に記録。ここでは実機ログの
生証跡のみを残す。

## B-0 ビルド確認

- build-relevant path 最終変更コミット: `1301a34`（2026-09-08 16:44:42）
- バイナリ mtime: 2026-09-09 15:06（上記より新しい → 再ビルド不要と判断）
- `22538cc`（2026-09-08 18:03:32）は `1301a34` より新しく、`1301a34`〜現HEAD `8146f08` 間に
  build-relevant path の変更なし（`git log` で確認済み）→ バイナリは現HEADと等価
- 起動目視確認: ユーザー回答「正常表示（問題なし）」（devUrl エラーなし）

## B-1 スモーク

1回目（GSE 未起動のまま実行）: 全列 0 → **手順の誤り**。引き継ぎメモ B-1 の bash 例に
「GSE を起動した状態で」の記述が抜けていた。一次資料 `README.md` の「★ 0. まず 1 分のスモーク
（⚠️ GSE を起動した状態で・8 列に実値が出るか確かめる）」に従い GSE を起動して再実行。

2回目（GSE 起動済みで実行）: 列数 8、`cpu_pct`(1.5〜3.1%) / `rss_kb`(37220〜37252 kb) /
`threads`(43〜45) すべて非ゼロ → 測定器 正常。結果は破棄済み（`rm -rf results/with-gse`）。

## B-2 本番 8時間

| 手順 | 時刻 (JST) | 備考 |
|---|---|---|
| GSE 未起動確認 | 16:15 頃 | `tasklist` に無し |
| サンプラ先行起動 | 16:15:14 (`meta.json` `started_utc=2026-09-09T07:15:14Z`) | `nohup bash run.sh with-gse &` |
| 基線サンプル 3 行 | 16:15:14 / 16:15:45 / 16:16:15 | 全列 0（GSE 不在の陰性対照） |
| GSE 起動（バイナリ直叩き） | **16:16:41**（`gse-app.log` 実測: `07:16:30.569Z` UTC = 16:16:30.569 JST） | PID 27160 |
| 8時間経過・サンプラ自動終了 | `finished_utc=2026-09-09T15:15:40Z` = 00:15:40 JST | `duration_s=28800`（8h ちょうど） |

- サンプル数: 907 行（全体）／ 903 行（GSE 在中、判定対象）／ 3 行（起動前基線・全列 0）
- 8時間の間、1時間おきに Claude Code の `ScheduleWakeup` で生存確認（計 7 回）。
  いずれも GSE プロセス生存・`samples.tsv` 増加を確認、異常なし。

## `gse-app.log` 実測（測定窓 `07:16:30〜15:20` UTC）

- ERROR/WARN は計 3 行のみ（`O1 MODE ENABLED` の定型 WARN を除く）:
  1. `07:16:30.792` 起動直後: `O1 orphan sweep: closed Some("gse_o1_20260909_071328.ndjson")`
     （B-1 スモーク時に `taskkill` で終了させた孤児を回収。§1 で確定済みの経路と一致・想定内）
  2. 同時刻: `O1 orphan sweep finished closed=1 failed=0`
  3. `07:18:46.830` **ERROR keyboard hook may be dead**: `starved_ms=30000` →
     `07:18:56.833`（10秒後）に `INFO keyboard hook is delivering events again` で回復。
     ⚠️ 起動から約2分後の**単発**のフック飢餓（30秒）。8時間中これ1回のみ、以降再発なし。
     macOS の CGEventTap 失効（memory `macos-tap-idle-away-probe-bug`）とは別機構
     （Windows は `WH_KEYBOARD_LL` + liveness 監視）。原因は未特定（本タスクはコード変更なしの
     検証タスクのため、深掘りは別タスクに起票）。

## NDJSON 実測

- 対象ファイル: `gse_o1_20260909_071630.ndjson`（Birth: `2026-09-09 16:16:30.792` JST =
  `07:16:30.792` UTC、`stat` で実測）
- 開始スナップショット (`ndjson-size-start.tsv`, 16:15:14 JST 時点) にこのファイルは**存在しない**
  （Birth がスナップショットの76秒後なので当然）→ 「run 中にゼロから書かれた」前提が
  ファイルシステムの Birth time という一次資料で確認できた。
- 終了時サイズ (`ndjson-size.tsv`, mtime `1788966938` = 8h 経過時点): **7,039,739 bytes**
- 8.00h で 6.71 MB → **20.14 MB/日に外挿**（判定閾値 < 30MB を満たす。詳細は notes.md）

## §2 完了時点の GSE プロセス

- 8時間経過後（00:20 時点）も GSE プロセスは生存中（PID 27160、研究者が通常使用を継続）。
  本タスクの指示に「8時間後に落とす」の明記はないため、起動したまま完了処理へ進む。

## ⚠️★★★ 結果ディレクトリ名の衝突事故（発覚・復旧済み）

`run.sh with-gse` を実行すると結果は `results/with-gse/` に書かれるが、このディレクトリは
**macOS 2回目実測（2026-09-05）の `meta.json` / `finished_utc` が git 管理下に置かれたまま**
だった（`samples.tsv` 等の実データファイルは `.gitignore` 対象でこの Windows 機のローカルには
元々存在しなかった）。`run.sh` の「既存結果を上書きしない」ガードは `samples.tsv` の有無だけを
チェックするため発火せず、8時間本番の集計後に **macOS 2回目の `meta.json`/`finished_utc` を
Windows の値で上書きしてしまっていた**（`git status` で `M` として発覚）。

### 復旧手順（実施済み）

1. 上書き後の Windows 値（`meta.json`/`finished_utc`）を確認・退避
2. `mkdir results/with-gse-20260909-windows/` を作成
3. Windows実測の `samples.tsv` / `ndjson-size.tsv` / `ndjson-size-start.tsv` /
   `summarize-output.txt`（未追跡ファイル）を新ディレクトリへ `mv`
4. Windows値の `meta.json`/`finished_utc` を新ディレクトリへコピー
5. `git checkout -- results/with-gse/meta.json results/with-gse/finished_utc` で
   macOS 2回目の値を復元（`git diff` で完全一致を確認）
6. `python3 scripts/summarize.py with-gse-20260909-windows` で再集計し、
   移動前と同一の数値（CPU平均2.06%等）が出ることを確認（下記参照）

### 復旧後の `git status`（結果ディレクトリ部分）

```
（変更なし）           results/with-gse/meta.json         ← macOS 2回目の値に復元
（変更なし）           results/with-gse/finished_utc       ← 同上
??                     results/with-gse-20260909-windows/  ← Windows実測（新規）
```

★ macOS 2回目の生データ（`samples.tsv` 等）はそもそも `.gitignore` でこのローカルには
存在しなかった（別マシンのローカルにのみ存在し、`notes.md` の解析結果としてのみ本 repo に
残っている）ため、**今回の事故で実データが失われたわけではない**（`meta.json`/`finished_utc`
という 2 個の小さいメタファイルが一時的に上書きされ、`git checkout` で復元できた）。

## 集計コマンドの文字化け対処

`python3 scripts/summarize.py` を素で実行すると Windows コンソール既定エンコード (cp932) が
絵文字 (⚠️) を出力できず `UnicodeEncodeError` で落ちる。`PYTHONIOENCODING=utf-8` を付けて実行すると
正常に完走する（★ コード変更ではなく実行時環境変数での回避。今後 Windows で summarize.py を
使う際の再現性メモとして残す）。
