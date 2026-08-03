# G1 パイロット P-1 の実施（前日準備 → 2 端末 × 2 題材で実施）

## 背景

G1 統制タスク実験は事前登録 **第 5 版で凍結**され、`bash run.sh` は GREEN、リリースタグ
`v0.1.22` も打ち終わっている。**しかしデータは 1 件も無い**。前ラウンド
（`.steering/20260803-g1-pilot-readiness/`）で実施を止めていた blocker（B-1 プローブ発火 /
B-2 判定の封印 / B-3 ブロックの区切り / B-5 入力先）はすべて決着済みで、
★ **残っているのは「実際に回す」ことだけ**である。

本ラウンドの調査で、引き継ぎ文書と実体の間に **3 つのズレ**が見つかった:

| # | ズレ | 実体（一次資料で確認） |
|---|---|---|
| **Z-1** | 引き継ぎ `T-1` が「**9 アセットすべて公開済み**」「Windows: `gse-next_0.1.22_x64-setup.exe`」と書いている | ★ 実際は **5 アセット**。`f3785ae`（main HEAD）で NSIS インストーラ・`gse-package(.exe)`・mac 単体 `gse-submit` を配布から外し、**公開済み v0.1.22 からも削除済み**。`gh release view v0.1.22` で実測確認。Windows は **portable の `gse-next.exe`** |
| **Z-2** | `protocol.md §6` の当日チェックリストが 10 ブロック（確証デザイン）用で、「強制比較を 1 問取る」を含む | ★ `preregistration.md §2.8` は **P-1 では操作チェックを取らない**と凍結している（HI/LO の対が 1 組しかなく比較の鎖が成立しない）。`assign.py --pilot` の出力も全ブロック `manipulation_check: False`。**チェックリストをそのまま追うと事前登録違反になる** |
| **Z-3** | `assign.py` の `pilot_assign(seed, topic=1)` は `topic` 引数を持つが **CLI から渡せない** | P-1 を 2 端末で回す決定（下記）により、**同じ題材を 2 回書くことになり打鍵量の測定が壊れる**（2 回目は内容既知で速く書ける） |

## ゴール

**2026-08-04 に P-1 を Windows / macOS の 2 端末で回せる状態を、前日（08-03）中に作り切る。**
実施そのもの（当日の運用）と、その後の n 凍結は次ラウンド。

### 本ラウンドで確定した研究者判断（2026-08-03）

| # | 判断 | 内容 |
|---|---|---|
| **G-1** | 実施端末 | ★ **Windows / macOS の両方で 1 回ずつ**回す（P-1 を 2 回実施） |
| **G-2** | フォーム | ★ **G1-C ＋ G1-S の両方を流す**（本番と同じ導線を通し、配備を検証する）。⚠️ **G1-M は取らない**（§2.8） |
| **G-3** | 今日の範囲 | ★ **前日準備を全部やる**（実施は §5-1 により最短 08-04） |
| **G-4** | 題材 | ★ **2 回目（macOS）は `topic02`** に分ける。`assign.py` に `--pilot-topic N`（既定 1）を追加する |

## スコープ

### 含むもの

- **Z-3 の是正**: `assign.py` に `--pilot-topic` を追加（`pilot_assign` の既存引数を CLI に露出する）
- **Z-1 / Z-2 の是正**: 引き継ぎ・`protocol.md` を実体に合わせる（★ **判定基準には触れない**）
- P-1 の割付ファイル生成（`blocks/PILOT-win.json` / `blocks/PILOT-mac.json`・**コミットしない**）
- ★ `GSE_DISABLE_PROBES=1` を固定する **launcher**（macOS `.command` / Windows `.bat`）
- P-1 用の**記録用紙**（4 ブロック版）と `env.md` の記入枠
- `.steering/` と `notes.md` への記録

### 含まないもの

- ❌ **`preregistration.md §3.1 / §3.2 / §3.4 / §3.5 / §3.6` の変更**（判定基準は凍結）
- ❌ **確証標本の n の凍結**（`§2.4` により P-1 の**後**。次ラウンド）
- ❌ **確証実施**（`ADR-009 D7` により Phase1 の凍結解除後）
- ❌ **GAS の実行そのもの**（Apps Script エディタでの `setupG1Forms()` は研究者の手作業）
- ❌ 課題文の印刷・封入・端末へのバイナリ導入（研究者の物理作業。手順書は作る）
- ❌ アプリのコード変更（`v0.1.22` のバイナリで回す。★ ビルドを変えない）

## 受け入れ条件

- [ ] `python3 assign.py --pilot --pilot-topic 2` が `topic02` の割付を出す
- [ ] `python3 assign.py --selftest` が緑（`--pilot-topic` の後方互換を含む）
- [ ] `bash run.sh` が **GREEN のまま**
- [ ] `python3 validate_blocks.py` が緑（`blocks/PILOT-win.json` / `PILOT-mac.json` を置いた状態）
- [ ] 引き継ぎ `T-1` が実体（5 アセット・portable exe）を指している
- [ ] `protocol.md` に「★ P-1 では強制比較を取らない」が明記され、当日チェックリストが P-1 と確証で分かれている
- [ ] launcher が両 OS 分あり、`GSE_DISABLE_PROBES=1` を手打ちしなくてよい
- [ ] ★ `blocks/*.json` と NDJSON を**コミットしていない**
- [ ] ★ 成果物にセッション**時刻**・氏名・メール・所属が出ていない（日付までは可）

## 関連ドキュメント

- `experiments/20260801-controlled-friction-task/preregistration.md` §2.4 / §2.6 / §2.8 / §2.10 / §2.11 / §5.4（★ **凍結。優先する**）
- 同 `protocol.md`（当日の台本）／ `notes.md` ／ `env.md` ／ `data.md` B-4
- `.steering/20260803-g1-pilot-readiness/decisions.md` F-1〜F-8（決着の根拠）
- `Form_G1/README.md`（フォーム配備・P-ID を Phase1 と共有する帰結）
- `docs/participant-setup-guide.md` / `docs/pilot-runbook.md`（配布 5 アセットの実体）

## 運用メモ

- **/reimagine 適用: No**
- 理由: 設計判断は本ラウンドで研究者が 4 件（G-1〜G-4）確定済み。残りは
  「決まったことを実体に反映する」作業であり、複数案が競合する箇所が無い。
  ★ ただし `assign.py` の変更は**事前登録の凍結に触れない範囲**であることを
  `decisions.md` で明示的に論証する。
