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
