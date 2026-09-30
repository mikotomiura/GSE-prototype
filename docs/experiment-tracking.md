# 実験記録・再現性規約

科学的実験は `experiments/<YYYYMMDD>-<exp-name>/` に記録する（`.steering/` の作業記録とは別系統）。
GSE の実験は主に (a) 較正スモーク（criterion label と MhD 二軸出力の妥当性＝X1）、(b) 介入の受容・効果
検証（AB/BA＝Y、MRT＝X2）、(c) MhD パラメータ（Stage 1 HMM）チューニング/ablation、
(d) v0.4 アウトカム指標の閾値感度分析、である。再現性の単一真実源は本ファイル。
検証の全体設計（X1/X2/Y 三層・GATE1–3・26 週 M0–M5）は `docs/research-positioning.md` §5/§6 と
ユーザー検証 v0.4 設計 / 半年版 WBS を参照。方法論の出典は `docs/references.md` の V 名前空間 [V1][V4] 等。
論文用の実験は `papers/<paper>/experiment/` に置いてよい。その場合も本規約（SEED / env.md / data.md / run.sh / notes.md）に従う（`.steering/20260927-ime-observation-paper-eval-design/decisions.md` 判断 21）。

## 検証方法論アンカー（X1/X2/Y を取り違えない）

- **MhD 内部 X/Y**（Cognitive Friction / Productive Engagement）と **検証 X/Y**（推論妥当性 / システム価値）は別物。
  実験の `notes.md` には**どちらの X/Y か**を明記する。
- **三層分離** [v0.4§1]: X1=推論妥当性（Phase 1b, blind, C-index）/ X2=介入機会妥当性（Phase 3, MRT）/ Y=システム価値（Phase 2, AB/BA）。混ぜない。
- **推定〜介入の層を取り違えない**（research-positioning §0 の層構造表）: **L0 軸**（MhD X/Y・C-index で検証＝確証の核）/ **L1 Stuck**（`p_stuck`＝MhD の非線形出力・C-index は直接検証しない・self-marker＋行動アウトカムで探索）/ **L2 Need**（`p_stuck` 閾値の介入要否決定・判断性能は `intervention_eval.rs` の HIR/Precision/STALL-recall/閾値 sweep で評価）。**`p_stuck` は L0 の検証対象ではない**ことを `notes.md` に明記。L1/L2 は探索的で Go/Kill ゲートに載せない。
- **label_pool 分離**: `calibration_blind`（Phase 1 blind 較正）と `post_intervention`（Phase 2/3 介入下）は**合算しない**。
  X1 判定には `calibration_blind` のみ。`label_pool` タグで区別。
- **3 ゲート（事前凍結・後出し禁止、PreReg-1/2-3/4 に対応）**: GATE1 尺度理解（8 問中 6 問以上・**現行スモークでは延期**＝比較条件段で発効、X1 鎖は GATE2 起点）→ GATE2 測定法（回答率 ≥80% / latency 中央値 ≤10s / 有効 ≥20 件/人）→ GATE3 モデル（C-index 中央値 ≥0.65 & 全員 >0.55、PreReg-4 で凍結した事前登録値）。
- **因果デザイン**: 単純な導入前後比較は禁止（タスク慣れ・締切・意識変化が交絡）。Y は **AB/BA クロスオーバー**（順序効果相殺）、X2 は **MRT**（介入候補時点の micro-randomize）[V4]。
- **Y の交絡と追加アウトカム（指摘 D）**: `paste_after_stuck_rate` 低下は**自力解決とは限らず**、課題放棄・別デバイス/別アプリへの計測外移行・検索など非ペースト依存・新規性/実験者効果でも動く。
  依存低下を放棄と取り違えないため **完了率・放棄率・時間超過・外部支援の自己申告**を併報し、**washout・実験者盲検・カウンターバランス**で軽減する。
- **前向き holdout・MNAR 範囲報告**を凍結手順とする。無回答は MNAR 上下限を併報し被験者除外しない。

## `.steering/` との責務分離

- `.steering/<date>-<task>/` — **実装作業**の記録（requirement / design / tasklist）。コード変更の文脈。
- `experiments/<date>-<exp>/` — **科学的実験**の記録（仮説・データ・結果・再現手順）。研究主張の根拠。
- 混同しない: 「Nudge のバグ修正」は `.steering/`、「介入 ON/OFF で自力回復率を比較」は `experiments/`。

## ディレクトリ規約

```
experiments/<YYYYMMDD>-<exp-name>/
├── config.(yaml|json)   — 全ハイパーパラメータ（HMM 閾値・α・β・ゲート定数 等）
├── SEED                 — 乱数 seed（固定。プローブ時点抽選等に使う場合）
├── data.md              — 入力 NDJSON の version/hash と被験者/OS（gse-dataset の commit hash で固定）
├── env.md               — 環境固定（Cargo.lock / rustc version / OS、Python 使用時は requirements.txt 等）
├── run.sh               — 実行コマンド（gse-replay / gse-cohort の起点。再現のエントリ）
│                          ⚠️★★★ **Step 0 は `scripts/capabilities_gate.py`**（ADR-013 Migration 4）
├── results/             — 生成物（metrics.json / calib.json / cohort.json / segments.txt 等）
├── metrics.json         — 主要指標（gse-dataset の metrics/P*/<os>/ へ置く共有値と同一）
└── notes.md             — 所感・逸脱・気づき + 下記リンク
```

★ **雛形は `experiments/_template/`**（`run.sh` / `README.md`）。新しい実験はここをコピーして始める。

⚠️★★★ **`run.sh` の Step 0 (`capabilities_gate.py`) を消さないこと。**
「収集済み信号を使う解析は、最初に `capabilities` を機械判定する」という規約を、
★ **人の手順ではなくコード**にしたものである（判定表と使い方の SSOT は
`docs/development-guidelines.md §10.5`）。
⚠️ ADR-013 自身の診断は逐語で「**規約は書いてあったのに適用しなかった**」であり、
★ 「計器がコホートを跨げなかった」失敗は既に **2 件**起きている。

`notes.md` に必須リンク:
- **検証する仮説**: `docs/research-positioning.md` §5 の H? へのリンク
- **事前登録**: 該当する `docs/preregistration-v0.3.md` の PreReg-? 番号
- **借用した手法の出典**: `[n]`（`docs/references.md`）

## GSE 固有の再現性アンカー

- **HMM 挙動の固定**: `HMM_VERSION` (SemVer) を config と NDJSON meta 行に埋め込む。
  挙動を変えたら bump → ゴールデン再生成 → 差分の意図を `.steering/` に記録（agent-shared.md テスト方針）。
- **Replay-as-Truth**: 回帰は `gse-replay --snapshot` の byte-equal 一致で保護。実験の入力 NDJSON は
  gse-dataset の commit hash で固定し、`data.md` に記す（NDJSON 生ログは本リポジトリにコミットしない）。
- **集約のみ共有**: 共有アーティファクトは `gse-replay --metrics --json` / `--calibration --json` /
  `gse-cohort` の**集計 JSON のみ**。キーストローク内容・生 NDJSON は外部送信しない（data-privacy SSOT）。
- **本文非保存の徹底**: キーストローク内容・クリップボード本文・ウィンドウタイトルを保存しない [V5][V7]。
  paste は count ではなく source_role / external_paste_chars / large_paste_rate / paste_after_stuck_rate で構造化。
- **データ分離・暗号化（運用）**: Google Form の氏名/メール/同意と Dropbox のログは `participant_id` でのみ結合し、
  対応表は共有フォルダに置かない [V15][V16]。提出ログはアップロード前にローカルで age(X25519) 暗号化（gse-package CLI）[V17]。
- **凍結純関数**: 較正ゲート（`measurement_gate` / `model_gate`）と閾値定数は `calibration_eval` を
  唯一の真実源とし、実験ごとに再実装しない。

## 再現性チェックリスト

- [ ] seed を固定したか（時点抽選等のランダム要素がある場合）
- [ ] 入力データを version 管理（gse-dataset commit hash / NDJSON hash）したか
- [ ] 環境を lockfile（Cargo.lock 等）で固定し env.md から参照したか
- [ ] `run.sh` / `scripts/repro.sh` で 1 コマンド再現できるか
- [ ] HMM_VERSION を config と結果に刻んだか
- [ ] 結果が research-positioning.md の仮説（§5 H?）と PreReg 番号に対応づいているか
- [ ] ⚠️★★★ **前処理の先頭で `capabilities_gate.py` を通したか**（ADR-013）。
      ★ 0 行を「信号が無かった」と読んでいないか。`--allow-undecidable` を使ったなら、
      `notes.md` の結論を「無かった」ではなく**「判定不能」**と書いたか

## scripts/repro.sh の方針

代表実験（較正コホート 1 本）を 1 コマンドで再走できるエントリポイントを置く。
既存の `scripts/run-calibration-cohort.sh`（`raw/P*/` → `gse-replay --calibration` →
`metrics/Pxxx/<os>/*.calib.json` → `gse-cohort`）が事実上の repro 経路であり、
`scripts/repro.sh` はこれを実験ディレクトリの config で薄くラップする想定（中身は実験追加時に実装）。

## pilot 提出の来歴台帳（ビルドバージョンカット）

ラベル収量・確証適格性は**取得ビルドの来歴**に依存するため、提出をビルド段ごとに格付けする
（`preregistration-v0.3.md` のバージョンカット宣言 2026-06-28 と対応）。確証 (GATE2/GATE3) には
**M0 凍結ビルド (confirmatory)** のデータのみ供する。

| 提出 | ビルド | HMM | 格付け | 実測 | 用途 |
|---|---|---|---|---|---|
| P006 | 0.3.0 release | 0.3.0 | researcher test | 8.1分・発火0・有効0件 | 配線/IME/UI 確認のみ（確証に不可） |
| P007 | 0.3.0 release | 0.3.0 | shakedown | 37.2分・発火3@7.0/28.4/37.2・有効3件・self-marker 0・21分 drought | M1 shakedown（確証に不可）。**M0 で confirmatory 再走** |

- **不適格の原因**（M0 で是正済）: probe 枯渇バグ（PR#56）／較正レート過小（M0 較正 ProbeConfig）／
  self-marker 未使用（M0 導線・教示）／提出が CLI 手打ち（M0 ラッパー）／`.age` 名 実名漏れ（M0 受領リネーム）。
- **M0 凍結後の再走**: P007 を confirmatory として再取得し `calibration_blind` プールで GATE2→GATE3 判定。
  release 版データは確証プールに混ぜない（`label_pool` と本台帳の格付けで分離）。
- 生 NDJSON / `.age` 中身はコミットしない（data-privacy）。本台帳は集計・来歴メタのみ。
