# 設計 —— D. P1 本体の準備（器とテスト）

## アプローチ

実データが無い（G1・O1 とも未開始・判断 1）ので、**実データが届いた日に 1 コマンドずつで回せる器**を、合成 fixture で緑になる形で作る。
Loop（モード C）で 10 本の issue に分けて回す（`_issue-plan.md`）。

```
<ndjson-root>/<P-ID>/<session>.ndjson
   │  run-features-all-poles.sh（既存・004 で `-- --set` を足す）
   ▼
<features>/<P-ID>/<session>/{baseline,pointer_b,modifier_m_plus}.json   ← 封筒（共有禁止・repo の外）
   │  p1_features_io.py（002・読み込み層・fail-closed）
   ├─▶ p1_pg1_distribution.py（002）── PG-1 に渡す「分布だけ」   ← 既定の p1-repro.sh はここ＋DB で止まる
   ├─▶ build_p1_episode_db.py（003）── episodes_t0 / episodes_retrospective（規則 (e)）
   └─▶ [PG-1 が宣言されたら] p1_run_grid.py（004・27＋4・規則 (d)）─▶ p1_select.py（005・fold × 一式 × 極の metric 表）
p1_bounds.py（001）: 軸ごとの上下界（規則 (a)〜(c)）。G2 ができたら差し込む
```

Rust 側は独立に 3 本: 007（P1-G）・008（#8・`T1a` の非対称）・009（P1-A）。010 が ADR-030 補訂 3 に記録する。

## 変更対象

`_issue-plan.md` §3.1 を参照（issue ごとの Allowed Files が SSOT）。

## 変更しないもの

- `docs/preregistration-p1-episode.md`・`src-tauri/prereg/p1-episode.json`（凍結）
- `HMM_VERSION`・`src-tauri/schema/current.json`・fixture 本体・ゴールデン
- `gse-replay` の CLI の契約（P1-F は「変えない」・判断 7）

## テスト戦略

| 層 | 何で | どこ |
|---|---|---|
| 規則の固定 | unittest（合成の封筒を tempfile に作る） | `scripts/tests/test_p1_*.py`（CI に配線） |
| 実物との接続 | 各 acceptance の E2E（repo の合成 fixture → 実物の `gse-replay` → 3 極スクリプト → Python） | `issues/00X-acceptance.sh` |
| 検査の検査 | 変異（001: `not_computable` の幅を 0 にする）・陰性対照（002: 極の欠け・007: 不正 id・009: 再停止なし） | 同上 |
| Rust | `cargo test --workspace`・ゴールデン再生・clippy | verify |
| 最終 | merge 前にメインが clean な checkout で全 acceptance（P1-H 未是正のため） | `/finish-task` |

## 検証（完了時）

`requirement.md` の受け入れ条件どおり。

## 実装結果（2026-09-26・実行セッション）

- **モード C・全 10 本 `issue_done`**（W1: 001 ‖ 007 → W2: 002 ‖ 008 → 003 ‖ 010 → 004 → 005 → 006。009 は基盤確認で先行）。
  ⚠️ 計画（`_issue-plan.md` §2）と違い 010 を 003 と並列にした（依存は 008 だけ・Allowed Files も交差しない）。
- **設計どおり**: 変更対象・変更しないもの（凍結 JSON・schema・fixture・ゴールデン・`Cargo.toml`）は計画のまま。凍結物・schema・fixture・snapshot・`Cargo.*` の `git diff main` は空。
- **実行時に変えたもの**（`decisions.md` 判断 23〜25・`blockers.md` B-1 / B-2）:
  - `verify_level: recheck` の 7 本を `parse` に落とした（watchdog が acceptance を回せず verdict を出せない基盤の故障・起票候補 P1-L）。acceptance は「loop-run の verify」と「メインの clean な検証用 worktree での再実行」の 2 段で残した。
  - `004-acceptance.sh` の「Rust 不変」検査の基準を `main` → base に直した（分解の欠陥・強さは不変）。
  - 「`feat` 行 0 本の fixture」は 11 本ではなく **7 本**（JSON で数えた値）に訂正した。
- **統合先端 `4617bbe1` の検証**（clean な検証用 worktree・全 rc=0）: acceptance 10 本 ＋ 過去 3 本 ＋ `check-tests-are-wired.sh` ／ `cargo test --workspace` ／ ゴールデン再生 ／ python `test_p1_*` 56 件 ／ `cargo check --all-targets` ／ clippy `-D warnings` ／ `cargo fmt --check` ／ schema drift ／ shell-portability ／ no-feature-output。
- **008 の AC6**（O1 の実ログが `feat` 行を持つか）はコードの経路で確認した（`issues/008.md` の Execution Result）。実データは開いていない。
