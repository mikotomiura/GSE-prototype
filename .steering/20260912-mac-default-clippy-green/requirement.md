# requirement — mac で default features の clippy を緑にする (F-4 の前提)

## 背景

`next-session-mac-default-clippy.md` (PR #198・`docs/handoff-f1-f5-results`) の指示による。

- ★ CI の clippy は `ci.yml` の **1 箇所だけ**で、**`--features package` 付き**である。
  → ⚠️ **default features のみの clippy は CI に存在しない。**
- ★ Windows 実機は default features で **exit 0** を実測済み (2026-09-12)。
- ⚠️ **mac 実機は未検証**だった。mac セッションが測ったのは
  `--all-targets --features package --target aarch64-apple-darwin` であって、
  `--features package` を外した形ではない。
- ⚠️ ローカル `stop-check.sh` は default features で回るが **WARN を出すだけでブロックしない**
  → ★ mac 側で警告が出ていても誰も気づかない構造だった。

## ゴール (受け入れ条件)

- ★ `cd src-tauri && cargo clippy --all-targets -- -D warnings` が **exit 0**。
  ⚠️ **件数を受け入れ条件にしない** (clippy は lib が落ちた時点で止まるため)。
- ★ `--features package` 側 (CI と同じスコープ) に **退行が無い**こと。
- ★ ゴールデン (`gse-replay --snapshot`) が byte-equal、schema が byte-equal。
- ★ 完了報告に **「mac の default features clippy は exit 0」と明記**する
  (⚠️ これが F-4 の着手条件になる)。

## スコープ外 (やらないこと)

- ⚠️ **CI への追加 (F-4) はしない。** ★ Windows 側セッションの仕事である (手順 4)。
- ⚠️ `HMM_VERSION` は bump しない。
- ⚠️ F-3 (`stop-check.sh` に `--features package` を足すか) の**判断はしない**。
  ★ 本タスクは判断材料 (mac の実測コスト) を提供するだけ (§3・任意)。
- ⚠️ 蒸し返さない: toolchain 固定 / 固定先 1.98.1 / MSRV 1.88 / codex 予算上限
  (★ `20260912-r2-r5-decisions/decisions.md` で決着済み)。

## 運用メモ

- /reimagine 適用: **No**
- 理由: 設計判断を伴わない検証タスク。実装案の比較が発生しない
  (★ 実際、コード変更は 0 行で完了した)。
