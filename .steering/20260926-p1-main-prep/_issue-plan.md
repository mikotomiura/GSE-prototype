# issue plan — D. P1 本体の準備（器とテスト）

> ★ 分解は **Opus**（`issue-slicing` Skill・`docs/loop-engineering.md` のモデル割当）。前段の grill の裁定は `decisions.md` 判断 1〜15（研究者）・16〜20（分解時）。
> ★ 実行は **別セッション**（`/clear` の後）。モード C: `bash scripts/loop-run.sh .steering/20260926-p1-main-prep`（base = `feat/p1-main-prep`）。
> ⚠️ **issue ファイルだけを読んで実行が成立すること**が契約。各 issue は背景・一次の場所・禁止を自分で持つ。

## 1. issue 一覧

| id | 題 | 言語 | verify_level | Dependencies |
|---|---|---|---|---|
| **001** | 軸ごとの上下界の結合器（v1.1 規則 (a)〜(c)） | Python | `recheck` | — |
| **002** | 3 極の読み込み ＋ PG-1 分布集計（構造の保証） | Python | `recheck` | 001 |
| **003** | episode 表の DuckDB（規則 (e)） | Python | `recheck` | 002 |
| **004** | 探索格子の実行器（27 ＋ 4）・規則 (d)・3 極スクリプトの `--set` パススルー | Python / sh | `recheck` | 003 |
| **005** | nested CV の fold と metric 表（選択はしない） | Python | `recheck` | 004 |
| **006** | 再現の雛形と 1 コマンド再現（PG-1 の手前で止まる） | sh / md | `parse` | 005 |
| **007** | P1-G: `--feature-config` の `id` / `version` の検証 | Rust | `recheck` | — |
| **008** | #8: `feat` 行 0 本で `T1a` を `null`・旧検査の張り直し | Rust / sh | `recheck` | 007 |
| **009** | P1-A: 凍結既定で restop を測る統合テスト | Rust | `parse` | — |
| **010** | ADR-030 補訂 3（#8 と P1-F の記録） | docs | `parse` | 008 |

### ⚠️ `verify_level` の選別根拠（基準 5）

> ★ **実行時の是正（2026-09-26・判断 23）**: 下の `recheck` の 7 本は、watchdog が acceptance を回せず verdict を出せない（`blockers.md` B-1）ため、実行時に **`parse` へ落とした**。選別の趣旨（研究の契約を再検証する）は、メインの clean な検証用 worktree での acceptance 再実行が担う。

- **`recheck`**: 研究の契約（事前宣言 v1.1 の読み方の規則・PG-1 の規律・探索の手続き）を**コードで固定する** issue（001〜005）／ security（007）／ criterion の出力を変える（008）。
- **`parse`**: 雛形とスクリプトの結線（006）・既存挙動を変えないテストの追加（009）・文書（010）。

## 2. 依存 DAG（循環なし）

```
Python:  001 ─▶ 002 ─▶ 003 ─▶ 004 ─▶ 005 ─▶ 006
Rust:    007 ─▶ 008 ─▶ 010
         009（独立）
```

- ★ **最長 chain = 6 段**（001 → … → 006）。直列時の総 attempt 見積り: 6 × `max_attempts` 6 = 最大 36。
- ⚠️ Python の鎖が長いのは、**すべての Python issue が `ci.yml` の同じ step にモジュール名を足す**から（`check-tests-are-wired.sh` はモジュール名で見るので、discover の 1 行では配線にならない・`decisions.md` 判断 17）。
  データの流れとしても 002（読み込み層）→ 003 / 004 → 005 → 006 の順は要る。

### ★ ウェーブ（`parallel: 2`）

| ウェーブ | issue | 根拠 |
|---|---|---|
| W1 | **001 ‖ 007** | Python（`scripts/`・`ci.yml`）と Rust（`replay.rs`）で交差なし |
| W2 | **002 ‖ 008** | 同上。⚠️ 008 は cargo の既存テストの期待値を変えるが、002 の worktree は Rust を触らない |
| W3 | **003 ‖ 009** | 009 は新規の統合テスト 1 本だけ |
| W4 | **004 ‖ 010** | 010 は docs だけ |
| W5 | 005 | |
| W6 | 006 | |

## 3. Allowed Files 交差表

### 3.1 各 issue の集合（自分の `00X-acceptance.sh` は省く）

| id | Allowed Files |
|---|---|
| 001 | `scripts/p1_bounds.py`, `scripts/tests/test_p1_bounds.py`, `.github/workflows/ci.yml` |
| 002 | `scripts/p1_features_io.py`, `scripts/p1_pg1_distribution.py`, `scripts/tests/test_p1_pg1_distribution.py`, `.github/workflows/ci.yml` |
| 003 | `scripts/build_p1_episode_db.py`, `scripts/tests/test_p1_episode_db.py`, `.github/workflows/ci.yml` |
| 004 | `scripts/p1_run_grid.py`, `scripts/tests/test_p1_run_grid.py`, `scripts/run-features-all-poles.sh`, `docs/verification-runbook.md`, `.github/workflows/ci.yml` |
| 005 | `scripts/p1_select.py`, `scripts/tests/test_p1_select.py`, `.github/workflows/ci.yml` |
| 006 | `scripts/p1-repro.sh`, `scripts/p1-repro-test.sh`, `scripts/templates/p1-experiment/README.md`, `docs/verification-runbook.md`, `.github/workflows/ci.yml` |
| 007 | `src-tauri/src/bin/replay.rs` |
| 008 | `src-tauri/src/analysis/feat_offline/dispersion.rs`, `src-tauri/src/analysis/feat_offline/mod.rs`, `src-tauri/src/bin/replay.rs`（test のみ）, **過去** `20260914-mhd-feature-offline-tiers/issues/003-acceptance.sh`, **過去** `20260921-p1-prereg-cli-poles/issues/003-acceptance.sh` |
| 009 | `src-tauri/tests/p1_restart_default_config.rs` |
| 010 | `docs/adr/ADR-030-stall-onset-and-decision-episode.md`, `docs/adr/README.md` |

### 3.2 交差（`∅` = 並列可）

|  | 001 | 002 | 003 | 004 | 005 | 006 | 007 | 008 | 009 | 010 |
|---|---|---|---|---|---|---|---|---|---|---|
| **001** | — | ci | ci | ci | ci | ci | ∅ | ∅ | ∅ | ∅ |
| **002** | ci | — | ci | ci | ci | ci | ∅ | ∅ | ∅ | ∅ |
| **003** | ci | ci | — | ci | ci | ci | ∅ | ∅ | ∅ | ∅ |
| **004** | ci | ci | ci | — | ci | ci・runbook | ∅ | ∅ | ∅ | ∅ |
| **005** | ci | ci | ci | ci | — | ci | ∅ | ∅ | ∅ | ∅ |
| **006** | ci | ci | ci | ci・runbook | ci | — | ∅ | ∅ | ∅ | ∅ |
| **007** | ∅ | ∅ | ∅ | ∅ | ∅ | ∅ | — | replay.rs | ∅ | ∅ |
| **008** | ∅ | ∅ | ∅ | ∅ | ∅ | ∅ | replay.rs | — | ∅ | ∅ |
| **009** | ∅ | ∅ | ∅ | ∅ | ∅ | ∅ | ∅ | ∅ | — | ∅ |
| **010** | ∅ | ∅ | ∅ | ∅ | ∅ | ∅ | ∅ | ∅ | ∅ | — |

## 4. ⚠️ 実行セッションへの申し送り（issue に書いた前提の再掲だけ・新しい前提は無い）

- ★ **004 の acceptance は前タスクの `008-acceptance.sh` を呼ぶ**（`run-features-all-poles.sh` の後方互換）。⚠️ 起票 P1-H（verify が他の issue の門を回さない）は未是正なので、**merge 前にメインが全 acceptance を clean な checkout で回す**。
- ★ **008 の acceptance は `main` の `gse-replay` を別 worktree で build する**（出力の byte 比較）。初回は数分かかる。
- ★ 002〜006 の acceptance は **repo の合成 fixture** を `run-features-all-poles.sh` に通す E2E を含む（出力は `mktemp -d`・repo の外）。⚠️ 実データは使わない。
- ⚠️ Python は `python`（3.11）を使う。`python3` は Windows では Store のスタブになりうる（acceptance は `PYTHON` → `python` → `python3` の順で拾う）。

## 5. 自己検査（issue-slicing の締め）

- [x] 各 issue を単体 merge しても base が壊れない（新規ファイル中心・既存の変更は後方互換か期待値の直しで、各 acceptance が旧検査を回す）
- [x] 各 AC に対応する test 名を今書けた（各 issue の AC 表）
- [x] Allowed Files 交差表を作り、並列の組を根拠つきで示した（§3）
- [x] DAG に循環なし・最長 6 段（§2）
- [x] recheck を基準 5 で選別した（7 本 recheck・3 本 parse。全部 parse ではない）
- [x] AC の書けない「リファクタだけ」の issue は無い
- [x] pin 済み verify の前提を変える issue: 001 が最初の `test_p1_*` を足す（それまで discover は 0 件で緑）。008 は cargo の期待値を変えるが、自分の verify の中で閉じる → W1 / W2 に置いた
- [x] test / lint が無条件に緑になる issue（006 の雛形・010 の docs）にも `acceptance.sh` を書いた（全 10 本）
