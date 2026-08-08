# 後片付けの記録 (2026-08-08)

★ 消す前に何があったかをそのまま残す (ユーザー承認: g1_participant_id / Desktop フォルダ の 2 件)。

## ⚠️★ 消す前に見つけたこと — テスト用アプリが 3 時間動き続けていた

```
  PID STARTED                           TIME COMMAND
84943 Sat Aug  8 15:04:59 2026     157:55.39 /Users/johnd/Desktop/G1_実施用_macOS/gse-next.app/Contents/MacOS/gse-next
```

- `windows-verification.md §4-1`（× で閉じてもプロセスが残る）が **macOS でも起きていた**。
  ★ §4-1 は Windows でしか観測していなかったが、⚠️ **overlay 窓が残る限り死なない**という
  原因はプラットフォーム非依存 (`lib.rs` が `WebviewWindowBuilder` で 2 つ目の窓を作り、
  `CloseRequested` / `ExitRequested` を捌いていない) なので、macOS でも同じことが起きる。
- CPU 157 分 / 実時間 180 分 = ★ **1 コアの ~87% を焼き続けていた**。
- `g1_mode:"marker"` のまま研究者自身の打鍵を記録していた:
```
-rw-------@ 1 johnd  staff    198 Aug  8 14:30 /Users/johnd/Documents/GSE-sessions/gse_20260808_053019.ndjson
-rw-------@ 1 johnd  staff   4445 Aug  8 15:04 /Users/johnd/Documents/GSE-sessions/gse_20260808_060345.ndjson
-rw-------@ 1 johnd  staff  80353 Aug  8 18:06 /Users/johnd/Documents/GSE-sessions/gse_20260808_060459.ndjson
```
- ⚠️ ★ セッション NDJSON は **消していない** (承認外)。研究者判断で処理すること。
  P009 はロスターで 除外 済みだが、`gse_20260808_060459.ndjson` は
  **被験者の実施ではなく研究者の通常作業 3 時間ぶん**である。

## 1. ~/.gse/g1_participant_id

```
-rw-r--r--@ 1 johnd  staff  5 Aug  8 15:05 /Users/johnd/.gse/g1_participant_id
中身: P009
```

## 2. ~/Desktop/G1_実施用_macOS

```
~/Desktop/G1_実施用_macOS
~/Desktop/G1_実施用_macOS/gse-next.app
~/Desktop/G1_実施用_macOS/.DS_Store
~/Desktop/G1_実施用_macOS/README_先に読む.txt
~/Desktop/G1_実施用_macOS/g1.mode
~/Desktop/G1_実施用_macOS/初回セットアップ_mac.sh
~/Desktop/G1_実施用_macOS/G1課題文_P009
~/Desktop/G1_実施用_macOS/g1-submit.json
~/Desktop/G1_実施用_macOS/G1課題文_P009/block02.html
~/Desktop/G1_実施用_macOS/G1課題文_P009/block03.html
~/Desktop/G1_実施用_macOS/G1課題文_P009/block04.html
~/Desktop/G1_実施用_macOS/G1課題文_P009/block08.html
~/Desktop/G1_実施用_macOS/G1課題文_P009/block09.html
~/Desktop/G1_実施用_macOS/G1課題文_P009/block05.html
~/Desktop/G1_実施用_macOS/G1課題文_P009/block06.html
~/Desktop/G1_実施用_macOS/G1課題文_P009/block10.html
~/Desktop/G1_実施用_macOS/G1課題文_P009/block07.html
~/Desktop/G1_実施用_macOS/G1課題文_P009/block01.html
--- 合計サイズ ---
 27M	/Users/johnd/Desktop/G1_実施用_macOS
```
