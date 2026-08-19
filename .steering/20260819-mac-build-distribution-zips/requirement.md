# v0.1.27 の配布 zip を Mac で作る

## 背景

2026-08-19 に G1 をリブートし、計器 (ADR-013) と運用 (G-1 二度押し) を直して `v0.1.27` を
リリースした。⚠️ **被験者に配るアプリを入れ替えないと、新しい計器は 1 行も効かない。**

⚠️★ `v0.1.26` のまま配ってはならない。v0.1.26 は既に配布済みであり、そのまま配ると
**同じ `app_version` を名乗る 2 つの異なる能力セット**が生まれ、`app_version` を刻んだ意味が消える
(ADR-013 の動機そのものの再生産)。

引き継ぎ: `.steering/_handoff/next-session-prompt-mac-build-distribution-zips.md`

## ゴール

★ 全員共通の配布 zip を 2 つ作り、**配る物そのもの**を実測で検査する。

| 成果物 | 中身 |
|---|---|
| `dist/_common/G1_実施用_macOS.zip` | `gse-next.app` を入れた**フォルダ**の zip (⚠️ dmg ではない) |
| `dist/_common/G1_実施用_Windows.zip` | `gse-next.exe` / `gse-submit.exe` / `launch-g1-windows.bat` / `pubkey.txt` |

## スコープ

### 含むもの
- `make-common-app-zip.sh --tag v0.1.27` の実行
- 引き継ぎ §3 の 4 項目の実測 (zip 中身 / `app_version` / G-1 二度押し / `starve_window`)
- 結果の記録

### 含まないもの
- ⚠️ Drive へのアップロード (**人の判断**。スクリプトも私も上げない)
- 被験者 1 人ぶんの配布物 (`make-distribution.sh <ID>`。課題ページは共通側に入れない・D-1)
- 電子同意フォームの実物への反映と突合 (`_handoff/next-session-prompt-post-reboot-collection-gate.md`)

## 受け入れ条件

1. 両 zip がスクリプトの機械検査を全て通って生成されること
2. `G1_実施用_macOS.zip` に `gse-next.app` があり `.dmg` が無いこと
3. 実際に起動して NDJSON の `meta` 行が `app_version = 0.1.27` であること
4. G-1 (実行中の「開始する」再押下) で**前ファイルが閉じ、新ファイルができる**こと
   (⚠️ 1 ファイルに `session_start` が 2 本入らないこと)
5. `starve_window` は**出れば** `win_ms` が 60000 前後であること
   (⚠️ 出ないこと自体は異常ではない)
