# PreReg-1 尺度理解ゲート — 教示文・ビネット・採点器の再設計

## 背景

### 引き継ぎの前提が誤っていた (本タスク冒頭で一次確認)

`.steering/_handoff/next-session-prompt-prereg1-scale-instructions.md` §0 は
「**通過率 0.00 ＝ 1 人も通っていない**」「これは Phase1 が `inconclusive` になった第一原因」
と書いていたが、**一次資料はそう言っていない**。

| 一次資料 | 逐語 / 実測 |
|---|---|
| `experiments/20260731-phase1-calibration-analysis/results/metrics_P0{10,11,12,13,14}_macos_*.calib.json` | 5 名**全員**が `"vignette": {"total": 0, "matched": 0, "passed": false}` |
| `src-tauri/src/analysis/calibration_eval.rs:924` | `passed: matched >= VIGNETTE_PASS_MIN` — **`total > 0` のガードが無い**。未実施が自動的に `false` になる |
| `src-tauri/src/analysis/cohort.rs:271-281` | `vignette_total` は**被験者数**であって回答数ではない。5 名 × 0 回答でも `total>0` が成立し `pass_fraction=0.0` になる |
| `docs/research-positioning.md:397` | 「GATE1 尺度理解（例題 8 問中 6 問以上、PreReg-1）は**現行スモークのスコープでは延期**」 |
| `docs/calibration-smoke-runbook.md:99` | 「尺度理解テスト (ビネット) は現行最小スコープでは**延期**」 |
| `experiments/.../notes.md:77-80` | 既に「**成立しない自動判定のアーティファクト**であり、実質的な判定根拠ではない」と結論済み |

→ **PreReg-1 は一度も施行されていない。** したがって
「不合格時は教示文を作り直して再施行する」という PreReg-1 の条項は**発動していない**。
引き継ぎ §0 が挙げていた「事前登録がそう指示している」という根拠は**使えない**。

### それでもこのタスクが必要な理由 (根拠は別にある)

`experiments/.../notes.md:127-129` 逐語:

> **これは straight-lining / 尺度未使用であり、PreReg-1 (尺度理解ゲート) が本来捕捉するはずだった
> 失敗モード**だが、PreReg-1 は延期されているため検出されないまま本収集に入っている。

実測 (`notes.md` §4):

| 被験者 | 有効回答 n | Q1 の分布 | 相異なる Q1 値 |
|---|---|---|---|
| P012 | 35 | 1:1 **3:34** | **2** (97% が "3") |
| P013 | 7 | **1:7** | **1** (完全に一定) |
| P014 | 34 | **1:16 3:18** | **2** (中間値なし) |
| P010 | 103 | 2:2 3:59 4:41 5:1 | 4 (中央 2 値に 97%) |

→ 5 名中 2 名で C-index が**数学的に算出不能**になり、GATE3 母数が 1 名に落ちた。
**GATE1 が延期されていたコストが顕在化した**というのが notes.md の結論であり、本タスクの根拠。

GATE1 は「延期」であって「不要」ではない。**まだ発効前**なので、いま器を直しても
forking paths には当たらない (発効後は凍結される)。

### 施行前に判明した器の欠陥 (一次確認済み)

| # | 欠陥 | 場所 |
|---|---|---|
| **F1** | スライダー初期値が **Q1=3 / Q2=3** で、`inferQuadrant` は **3 を必ず不一致**に落とす。→ **両スライダーを一度も動かさなかった被験者は機械的に 0/8**。「操作しなかった」と「3 を選んだ」が分離できない | `VignetteTest.tsx:47-48` / `:30-40` |
| **F2** | 教示文が **2 文しかなく、1–5 の刻みの意味がどこにも定義されていない**。アンカーは両端のみ | `VignetteTest.tsx:131-134` / `:146-147` |
| **F3** | 8 ビネット**すべて**が Q1/Q2 のアンカー語（「前に進まない」「前進している感覚はある」等）を**逐語で含む**。→ 尺度を理解していなくても**文字列マッチングで解ける** | `VignetteTest.tsx:18-26` |
| **F4** | 提示順が固定 `v1..v8` で、**同一象限が連続する** (v1,v2=flow / v3,v4=stuck / …)。→ 2 問目は 1 問目の答えを写せる | `VignetteTest.tsx:17-26` |
| **F5** | `vignette_response` は `q1/q2/expected_quadrant` のみ記録。**所要時間もスライダー操作有無も残らない**。→ 「読まずに次へ」と「読んで迷って中央」を事後分離できない (PreReg-7 は probe には所要時間保存を課しているのに、ビネットには無い) | `logger.rs:594-612` |
| **F6** | **未実施が「不合格」に化ける** (上記 `calibration_eval.rs:924` / `cohort.rs:271-281`) | 同左 |

## ゴール

**PreReg-1 を「初回施行できる状態」にする。** 具体的には、施行すれば
`notes.md` §4 で実測された straight-lining を**実際に捕捉でき**、かつ
理解している被験者を**中心化傾向だけで落とさない**器を用意する。

## スコープ

### 含むもの
- 教示文の再設計 (1–5 の刻みの定義 / 二軸の直交性 / 中点の扱い)
- 8 ビネット文面の再設計 (アンカー語の逐語ヒントを除去・提示順の是正)
- 採点器の是正 (`inferQuadrant` 相当 / スライダー初期値 / 未実施と不合格の分離)
- `vignette_response` の記録項目追加 (所要時間・操作有無)
- `empirical-prompt-tuning` による教示文の実測検証 (一致率で反復改善)
- 上記に対応する Rust / TypeScript のテスト
- `research-positioning.md` / `notes.md` への「通過率 0.00 = 未実施」の訂正反映

### 含まないもの
- ⚠️ **合格条件 (8 問中 6 問以上・被験者の 80% 以上) の変更** — **凍結。触らない**
- **施行計画** (誰に・いつ当てるか) — 研究者判断で今回は決めない。器だけ作る
- プローブ本体 (`probe_scheduler` / 較正プローブのレート) の変更 — Phase1 凍結対象
- HMM / 特徴量の変更

## 受け入れ条件

- [ ] AC-1: 未実施 (`total == 0`) が「不合格」と区別される。`cohort_verdict` の `decision_reason` が
      「未達」ではなく「未実施」を出す。**H0 が偽のとき赤になる**テストが両方向に存在する
- [ ] AC-2: スライダーが初期値を持たず、両軸を操作するまで先に進めない。
      「操作しなかった」が「3 を選んだ」に化けない
- [ ] AC-3: 採点器が中心化傾向 (片軸のみ 3) を一律に落とさない。かつ **(3,3) を 8 問続けた
      straight-lining は確実に落ちる**。両方向のテストがある
- [ ] AC-4: 8 ビネットの場面文に Q1/Q2 のアンカー語およびその明白な同義語が**含まれない**
      (機械検査で検証)
- [ ] AC-5: 提示順で同一象限が連続しない。順序は決定論的 (再現性)
- [ ] AC-6: `vignette_response` に所要時間・操作有無が記録され、`emit_schema` と
      `schema/current.json` が byte-equal で整合する
- [ ] AC-7: `empirical-prompt-tuning` で、教示文のみを渡した実行者の想定象限一致率を実測し、
      改善が頭打ちになるまで反復した記録が残る
- [ ] AC-8: `cargo test --workspace` / `gse-replay` ゴールデン 4 本 / `tsc` が緑
- [ ] AC-9: 合格条件 6/8・80% が**変わっていない**ことを diff で確認できる

## 関連ドキュメント

- `docs/preregistration-v0.3.md` §1 PreReg-1 (凍結された合否条件)
- `docs/research-positioning.md` §5 (GATE1 延期の記述) / §8 (方法論的限界)
- `docs/calibration-smoke-runbook.md` §3.1 / §3.3
- `experiments/20260731-phase1-calibration-analysis/notes.md` §4 / §5②
- `.steering/20260816-survey-synthesis-and-design/synthesis.md` §2 (法則 L1 / L5)
- `docs/literature/20260815-desk-behavior-stagnation-inference.md` ([V83] 3 脅威)

## 運用メモ

- /reimagine 適用: **No**
- 理由: 変更対象は既存の測定器 1 個 (教示文 + ビネット + 採点関数) であり、
  複数のアーキテクチャ案が競合する局面ではない。設計の妥当性は `empirical-prompt-tuning` の
  **実測**で決める (案の比較ではなく一致率で決める) ため、破壊と構築より実測ループが効く。
