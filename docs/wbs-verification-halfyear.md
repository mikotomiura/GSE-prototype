# GSE ユーザー検証 マイルストーン & WBS（半年版）

> **この md について**: `GSE_マイルストーン_WBS_半年版_v2.docx（⚠️ **2026-09-01: 本リポジトリには未収録**。研究者ローカル保管。★ SSOT は本 md）`（2026-06-22・統合元:
> codex-review v0.4 / 検証フェーズ設計企画書 / GSE_v2 概要 / テスター向け資料）を **忠実に markdown 化**した
> SSOT。以後の改訂は本 md を正とし、.docx は歴史資料として残す。文献番号 `[n]` は本書内の参考文献節を指す
> （中央書誌は `docs/references.md` の P/V 名前空間。本書 [1][2][3] ≈ [V1][V2]+ESM系、[5]=[V5] 等）。
>
> ⚠️ **Post-Phase1 の改訂は §改訂予定（提案・未承認）に分離**した。本体（§0–§7）は Phase1 の凍結契約
> （`docs/preregistration-v0.3.md`・PreReg-1..8 / GATE1–3）を**一切変更しない**。改訂は Phase1 完了 +
> Epic 0（リポジトリ実態調査）後に承認を経て本体へ昇格する。

## 2026-10-31 改訂: 少人数の前提での組み替え（研究者決定）

> 根拠は `.steering/20261031-gse-small-n-research-design/decisions.md` 判断 1〜16 と `docs/research-positioning.md` §1 冒頭の改訂ブロック。
> 本体（§0〜§7）は Phase 1 の凍結契約を含む履歴として残す。M0〜M2（Phase 1）は変えない。
> M3（AB/BA）・M4（MRT）と §改訂予定の Phase 2・3 は、採択後の検証については下の流れに置き換える。

- **人数**: 採択後は研究者本人を含めて 3〜5 名。主張は個人ごとの効果と、事例をまたいだ再現まで。MRT は集団の効果の設計で、3〜5 名には使わない。
- **介入**: 本体の介入は招待（身体回帰の機会）。Nudge は本体で出さない（ADR-040）。
- **週の割り当て**: 1 人あたりの期間は採択前のシミュレーションで見積もるので、ここでは置かない（未踏の期間に収まるかは未確認）。

| 段 | 中身 | 前提・成果 |
|---|---|---|
| A0 採択前の準備 | 研究者本人の記録で詰まりの件数を数える（`gse-replay`）／シミュレーションで期間と検出できる効果を見積もる（ADEMP の様式・系列相関と効果の型の幅で感度を示す）／合成の打鍵で推定器の動作を確かめる | 人のデータを新たに集めない。合成は動作確認に限る |
| A1 実装 | Nudge の既定の無効化（ADR-040 D1）／招待に `friction_rising` の契機と無作為の時刻の条件を足す（ADR-040 D4）／通常のモードで招待が出る配線（今は EH3 モードだけ）／新しい契機を `gse-replay` で再現できるようにする | `/start-task` から別タスク。ゴールデンの非回帰 |
| A2 事前登録と審査の準備 | `friction_rising` の値・腕ごとのトリガーと分母と時刻の原点・副のアウトカムの限界・割付の単位と反復数・2 段目へ進む人の選び方・統制課題での AI の答えの経路・感度分析を、データを見る前に書く／審査の計画と同意文 | 採択後すぐ審査に出せるようにする |
| B0 審査 | 未踏の担当 PM の所属大学で審査を出す道を探る | 規程（PM が研究責任者になる必要など）は未確認 |
| B1 1 段目（統制課題） | 招待を {推定器 / 頻度を合わせた無作為 / なし} に、各人の中でセッション（またはブロック）ごとに無作為に割り付け、1 人あたり多数のセッションを取る。全員の結果を報告する | 主: `receipt_free_resumption`（ADR-024）・副: ウィンドウを離れずに再開したか |
| B2 2 段目（自然作業） | 1 段目で効果が見えた人だけ、切り替え時点を人ごとに無作為にずらす多重ベースライン。進む人の選び方は事前登録で決める | 1 段目で効果が見えた人に限った、事例をまたいだ再現 |
| B3 L0 の判定 | 自然作業の長い記録を時間順に調整と評価に分けて C-index で判定 | 同じラベルを調整と評価に使わない |
| B4 総括 | 個人ごとの効果と事例をまたいだ再現として報告／MhD を上げる条件（ADR-019 D3・約 50 セッション）を満たすかの判定 | 満たせば `friction_rising` の中身をハザードへ差し替える（次の検証期間から） |

---

26週・Phase 0–3 全体実施計画 / X1・配線・ラベル収集を起点に。

---

## 0. 本書の基礎と前提

本書はアップロード 4 資料を統合し、6ヶ月（26週）を想定したユーザー検証のマイルストーンと WBS を確定する。
設計思想（X/Y 分離・blind 較正・本文非保存・defer 第一級化）は既出資料を踏襲し、本書は「いつ・誰が・何を・
どの順で・どの基準で」を実行可能な粒度に落とす。半年という期間は、ESM 研究で較正の長期化が回答率を下げ
脱落を生むことが知られるため [1][2][3]、各フェーズに緩衝週とローリング運用を設けて余裕を持たせる前提で配分する。

- **実装状態（デッキより確定）**: v2 は Tauri 2.0 で Windows/macOS 動作実装済み。行動シグナル層・作業状態推定層・
  介入機会判定層・介入ポリシー層の 4 層が実装境界と一致し、Need（p_stuck）と Opportunity を分離評価、defer を
  NDJSON に記録。gse-replay（--metrics/--intervention/--calibration）、gse-cohort、JSON Schema の CI drift 検知が
  整備済み。MhD は Stage 1（ルールベース HMM）が現在地。
- **層と検証記号の対応（確定）**: Need 層（p_stuck）の妥当性＝X1＝Phase 1、Opportunity 層（いま介入してよいか）の
  妥当性＝X2＝Phase 3、介入の受容と効果＝Y＝Phase 2。
- **ローカルリポジトリについて**: 実値（gse-cohort の判定境界、プローブ設定、介入ポリシー定数など）はコミット
  6fec546（2026-06-20）時点のソースで確認し、コードに無い運用値は検証設計（企画書／codex-review v0.4、
  いずれも 2026-06-22）で補って §7 に反映。Stage 2 昇格判定・AB/BA ブロック長・MRT 割付比はコード・設計 doc とも
  未確定で §7 に明記。

---

## 1. 合否基準の統合（PreReg 3ゲート + 二段ライン）

テスター向け資料の 3 ゲート事前登録基準を正とし、ラベル収集の二段階閾値とプール分離をこれに統合する。

| ゲート | 問い | 通過基準（事前凍結） | 不合格時 |
|---|---|---|---|
| **GATE 1 尺度理解** | Q1/Q2 を正しく取れるか | 例題 8問中 6問以上 かつ 8割以上 | 教示を作り直し再施行 |
| **GATE 2 測定法** | 回答が集まるか | 回答率 ≥80% / 中央値 ≤10秒 / 有効プローブ ≥20件/人 | ラベル方式を再設計 |
| **GATE 3 モデル** | 推定が申告の順序に沿うか | 方向付き順序 C-index 中央値 ≥0.65（全員 >0.55） | 特徴・モデルを差し戻し |

| ライン | 閾値 | 到達フェーズ | 意味 |
|---|---|---|---|
| 最小ライン | 有効プローブ ≥20件/人（GATE 2） | Phase 1 単独 | Kill 判定可能・Phase 2 進出資格 |
| 目標ライン | ≥40件/人・Q1/Q2 各々の高低両端 8件以上 | Phase 1〜3 通算 | 個人内 C-index の信頼区間が実用的に縮小 |

- **プール分離**: Phase 1 の blind 較正で集めた `calibration_blind` ラベルと、Phase 2/3 の介入可視環境で集める
  `post_intervention` ラベルは性質が異なるため合算しない。`label_pool` タグで区別し、X1 判定には
  `calibration_blind` のみを用いる。`post_intervention` は介入下のモデル監視と事後的母数拡大に使う。

> GATE1–3 ↔ PreReg-1..8 対応の SSOT は `docs/preregistration-v0.3.md`。現行スモークは GATE1 を延期し
> GATE2 起点（詳細は `docs/glossary.md` ゲート対応行）。

---

## 2. マイルストーン（26週）

各 M は前段の Go なしに次段へ進まない関門。週は W1（Phase 1a 着手週）起点の相対表記、絶対日付は着手時に確定。

| M | 名称 | 完了条件 (Exit Criteria) | 目安 |
|---|---|---|---|
| M0 | 検証基盤フリーズ | プローブ機構・IMEログ・NDJSONスキーマ(label_pool)・blind UI・gse-replay/cohort が CI 通過、PreReg 凍結 | W0(準備) |
| M1 | Phase 1a 完了 | n=3–5 で配線・IME健全・ラベル産出レート実測、GATE1/GATE2 通過、目標ライン閾値を確定 | W3 末 |
| M2 | Phase 1b 完了（X1） | n=5–10、calibration_blind で GATE3 go または少なくとも not-kill | W9 末 |
| M3 | Phase 2 完了（Y） | AB/BA で介入の受容と効果（paste/self-recovery/品質/TLX）を報告 | W17 末 |
| M4 | Phase 3 完了（X2） | MRT で nudge/defer 割付の近接アウトカム差、Opportunity 妥当性を判定 | W24 末 |
| M5 | 通算再推定 & 総括 | 目標ライン到達者で X1 再推定、Stage 2 昇格判定、全フェーズ統合レポート | W26 末 |

- **クリティカルパス**: M0 → M1 → M2 が必須直列経路。M0 のプローブ機構と IME ログ健全性が崩れていると M1 以降の
  全データが無効化するため最優先。M2 が not-kill を満たさなければ M3/M4 へ進まず、特徴量定義・IME ログ・ラベル UI・
  対象タスクの見直しへ差し戻す。半年版では M2 後に 1 週、M3 後に 1 週の緩衝を確保。

---

## 3. スケジュール（ガント概観・26週）

Phase 1b 6週・Phase 2 8週・Phase 3 9週はいずれも上限で、最小ライン到達者から順次次フェーズへ送るローリング運用に
よりフェーズは部分的に重なりうる。期間設定は ESM の長期化リスク [1][2][3] を踏まえた余裕配分。

| タスク | 週(アクティブ) |
|---|---|
| M0 検証基盤フリーズ | W1 |
| Phase 1a スモーク+レート | W1–W3 |
| M1 判定 | W3 |
| Phase 1b X1 較正 | W4–W9 |
| M2 判定/差し戻し緩衝 | W9–W10 |
| Phase 2 AB/BA 価値 | W10–W17 |
| M3 判定/緩衝 | W17–W18 |
| Phase 3 MRT 介入機会 | W16–W24（Phase2 と一部重複） |
| ラベル継続収集(別プール) | W10–W24 |
| M5 通算再推定+総括 | W25–W26 |

- **月の目安**: 1ヶ月目＝基盤+Phase 1a、2ヶ月目＝Phase 1b 較正、3ヶ月目＝Phase 1b 判定+Phase 2 前半、
  4ヶ月目＝Phase 2 後半+Phase 3 立上げ、5ヶ月目＝Phase 3 本体、6ヶ月目＝Phase 3 完了+通算再推定+総括。

---

## 4. WBS（作業分解構成）

各フェーズを成果物単位に分解。担当は個人開発前提で「自分」を既定とし、外部依存（参加者・PM・倫理/保護者同意）は明示。

### 4.0 M0：検証基盤フリーズ（W0）

| ID | 作業 | 成果物 | 依存/メモ |
|---|---|---|---|
| 0.1 | ランダム時点プローブ機構（申告前30秒の時間隔離） | probe / probe_valid 判定 | |
| 0.2 | blind ダッシュボード化（推定・確率を非表示） | calibration UI | 較正の必須条件 |
| 0.3 | IME ログ健全性（composition/confirmation/candidate_retry/確定間隔） | 健全性検査スクリプト | 本文非保存 [5] |
| 0.4 | NDJSON スキーマ確定 + label_pool タグ | JSON Schema / CI drift | gse-dataset 連携 |
| 0.5 | gse-replay --calibration / gse-cohort の C-index・両端集計対応 | 集計 JSON 仕様 | GATE3 算出 |
| 0.6 | PreReg 文書凍結（3ゲート・合否ライン） | 事前登録 doc | 後出し変更禁止 |
| 0.7 | データ分離（Form氏名↔P-ID対応表の物理隔離） | 運用手順書 | [15][16][17] |
| 0.8 | dismiss 理由 UI（4択: 詰まってない／今はもがきたい／閉じる／無言）の実装とログ化 | dismiss_reason フィールド | Need 誤りと Opportunity 誤りの分離に必須 [v0.4§9] |
| 0.9 | paste ログ構造化（source_role／external_paste_chars／large_paste_rate／paste_after_stuck_rate、本文・タイトル非保存） | 拡張 paste スキーマ | 現状は回数のみ。Ctrl+V回数は補助指標へ降格 [v0.4§4.1] |
| 0.10 | 自力解決メトリクス（manual_contribution_ratio／pflow_exit_manual_gain_rate）を gse-replay --metrics に追加 | metrics 拡張 | diff／総打鍵比は廃止 [v0.4§4.2] |
| 0.11 | session metadata に condition を追加（blind-calibration／A\|B／nudge\|defer） | condition フィールド | task_kind は実装済み [v0.4§9] |
| 0.12 | 前向き holdout・MNAR 範囲報告の手続き凍結（PreReg 化） | 解析手順書 | gse-replay --holdout／MNAR を運用手順として凍結 [v0.4§1] |
| 0.13 | 第三者ブラインド品質評価の運用設計（評価者に条件 A/B・GSE 有無・AI 使用量を伏せ、論理／独自／完成度／可読性を5段階） | 評価ルーブリック | blind_quality_score [v0.4§4.2] |
| 0.14 | 事後アンケート設計（task-specific self-efficacy 主・一般性自己効力感 副・NASA-TLX short・helpfulness／annoyance／next-week willingness） | Google Form 雛形 | 一般性のみでは検出感度不足 [v0.4§4.3/4.4] |
| 0.15 | Dropbox 運用確定（File Request の期限／パスワード／提出者 ID 命名、アップロード前ローカル age(X25519) 暗号化（gse-package CLI）、公開時 participant_id 再発番） | 運用手順書（0.7 拡張） | [v0.4§6][16][17] |
| 0.16 | Go/No-Go 事前登録の拡張（X1 3ゲートに加え Y Go/No-Go・Physical Anchor Go/No-Go を凍結） | PreReg 追補（0.6 拡張） | [v0.4§8] |

### 4.1 M1：Phase 1a スモーク兼レート測定（W1–W3, n=3–5）

| ID | 作業 | 成果物 | Exit |
|---|---|---|---|
| 1.1 | 募集・スクリーニング（タイピング流暢性＋データ commitment の二層基準） | Google Form / P-ID | |
| 1.2 | GATE 1：尺度理解テスト（例題8問） | 通過者リスト | 6/8 かつ 8割 |
| 1.3 | 常駐計測（普段どおり執筆/コーディング） | raw/P00x/*.ndjson | |
| 1.4 | IME・配線健全性確認 | 健全性レポート | 破綻ゼロ |
| 1.5 | ラベル産出レート & Q1/Q2 分布の実測 → 目標ライン確定 | レート実測値 | 40件/両端8件の再調整 |
| 1.6 | GATE 2：測定法ゲート | go/kill 判定 | 回答率80%等 |

### 4.2 M2：Phase 1b X1 推論妥当性（W4–W9, n=5–10, blind）

| ID | 作業 | 成果物 | Exit |
|---|---|---|---|
| 2.1 | blind 較正（ランダムプローブで Q1/Q2 収集） | calibration_blind ラベル | 最小20件/人 |
| 2.2 | gse-replay --calibration で個人内 C-index | P別 calib.json | |
| 2.3 | gse-cohort で被験者横断判定 | cohort 判定 JSON | go/kill/inconclusive |
| 2.4 | GATE 3：方向付き順序 C-index | X1 判定 | 中央値≥0.65/全員>0.55 |
| 2.5 | not-kill 時のみ Phase 2 設計確定 / kill 時は差し戻し | 判定レポート | 分岐点 |

### 4.3 M3：Phase 2 Y 価値検証（W10–W17, AB/BA）

| ID | 作業 | 成果物 | メモ |
|---|---|---|---|
| 3.1 | AB/BA 割付（半数 A→B、半数 B→A） | 割付表 | 順序効果の相殺 |
| 3.2 | A=介入なし / B=介入あり の交互運用 | 条件別ログ | Physical Anchor は opt-in（⚠️ **2026-09-01: 旧「強Wall/」を削除** — ADR-015 D1）|
| 3.3 | 主指標：external_paste_count, paste_after_stuck_rate, pflow_exit_without_receipt, 第三者ブラインド品質 | 効果指標 | ⚠️ 2026-09-19: 本行は ADR-024 D1 より前の記述。行動指標の主要アウトカムは `receipt_free_resumption`、併記義務は ADR-024 D6。H-Y の主の凍結は 0.16 |
| 3.4 | 副指標：task self-efficacy, NASA-TLX, helpfulness, annoyance | 受容指標 | [10][11r] |
| 3.5 | Physical Anchor：**招待の受容** / **下流の機会保存指標**（`paste_after_stuck_rate` / `pflow_exit_without_receipt` / `manual_contribution_ratio`）/ 安全 を層別評価（⚠️★★★ **2026-09-01 訂正: 旧「実行/効果」は ADR-018 D5 が評価量から降ろした。系は実行も完了も判定しない**）| Anchor 受容レポート | 夜間Outdoor無効 [8][9] |
| 3.6 | post_intervention ラベルを別プールで継続収集 | monitoring データ | X1合算しない |

### 4.4 M4：Phase 3 X2 介入機会妥当性（W16–W24, MRT）

| ID | 作業 | 成果物 | メモ |
|---|---|---|---|
| 4.1 | 介入候補時点の micro-randomize（例 70% nudge / 30% defer） | 割付ログ | [3r][4] |
| 4.2 | 近接アウトカム（2分/5分後の手動復帰・paste回避・dismiss・frustration） | proximal outcome | |
| 4.3 | Opportunity 特徴（idle_ms・修正率・バースト長・削除後停止率）の寄与分析 | tailoring 分析 | [3r2] |
| 4.4 | HIR/Precision/DC/Burden の反実仮想評価 | 介入品質レポート | HIR最重要 |

### 4.5 M5：通算再推定と総括（W25–W26）

- 目標ライン到達者で `calibration_blind` を主に X1 を再推定、信頼区間を更新。
- Stage 2（ロジスティック回帰）昇格判定：約50セッション＋3%以上 の Go/No-Go を確認、未達なら Stage 1 を正とする
  （オッカムの剃刀）。
- Phase 1–3 を貫く統合レポート（X1 妥当性・Y 受容と効果・X2 介入機会妥当性）を作成。

---

## 5. 工数とリソース配分の目安

個人開発前提。半年を通して開発作業と運用作業が並走する。

| 期間 | 開発比重 | 運用比重 | 主作業 |
|---|---|---|---|
| 1ヶ月目 | 高 | 低 | 基盤フリーズ・スモーク立上げ |
| 2–3ヶ月目 | 中 | 高 | Phase 1b 較正運用・X1 判定 |
| 4–5ヶ月目 | 中 | 高 | Phase 2/3 運用・指標算出 |
| 6ヶ月目 | 低 | 中 | 通算再推定・Stage判定・総括 |

---

## 6. リスクと対応

| リスク | 影響 | 対応 |
|---|---|---|
| IME ログ破綻 | Phase 1 全データ無効 | M0/M1 で最優先検査、破綻時は Phase 1b 未着手 [5] |
| ラベル未達(脱落) | C-index 判定不能 | n を厚く確保、4週で打ち切り、未達者は参考分析のみ [1][3] |
| 両端の偏り | C-index 計算不能 | M1 で分布実測、偏れば対象タスクを変更 |
| blind 崩れ | criterion label 汚染 | Phase 1 は推定非表示厳守、以降は別プール化 |
| 過介入(Phase2/3) | UX毀損・離脱 | cooldown/daily cap/recent dismiss/defer を既定で有効 |
| 対応表流出 | 個人特定 | Form氏名とログを同一場所に置かない、P-IDのみ結合 [15] |
| スケジュール遅延 | 半年超過 | 各M後に緩衝週、ローリング運用でフェーズ重複を許容 |

---

## 7. 着手前に確定すべき項目（要確認）

確定状況を 3 区分：【実装準拠】＝コードで確定（コミット 6fec546／2026-06-20 時点）、【設計確定→要実装】＝
検証設計（2026-06-22）で確定だがコード未実装、【未確定】＝どの設計 doc・コードにも確定値がなく仮置き。

- **【実装準拠】プローブ出現頻度**: 実装に固定の「1セッション上限」は無く、ProbeConfig 既定値（probe_scheduler.rs）で
  rolling thinning する：発火率 λ=2回/30分、最小発火間隔 8分（gap_min_ms）、cap=直近30分窓に最大2件
  （cap_window_ms=30分／cap_count=2）、idle≥3分(180秒)は棄却、セッション開始後31秒はウォームアップ非発火。
  実効上限は「30分あたり最大2件」。M1 で回答負担と実レートを見て λ／cap を調整する。
- **【設計確定（仮置き）／実装は最小ラインのみ】目標ライン「40件・両端8件」**: 検証フェーズ設計企画書§3.3 の
  Phase 1b 終了条件として定義済み（主条件＝有効プローブ ≥40点、副条件＝Q1高側/低側・Q2上位/下位 各8点、
  安全弁＝最大4週）。ただし「40点・両端8点は確定値でなく ESM 典型60点からの目安、Phase 1a 実測で確定」と明記。
  コード側の保証は最小ライン＝有効プローブ20件/人（VALID_PROBES_MIN=20）と PreReg-5（評価≥6・ランダムプローブ≥16）、
  回答率≥0.80・中央応答≤10秒のみで、40件・両端8件はコード未実装。
- **【未確定（AB/BA 構成は設計確定）】AB/BA ブロック長**: 構成は設計確定（半数 A→B・半数 B→A、A＝ログのみ／
  B＝**Nudge のみ**、Physical Anchor は opt-in・未実装 —— 2026-11-03 注: この「未実装」は古い。PC 側の招待は EH3 モードで実装済み、散歩の促進とその計測は行わず、身体回帰の後は離席候補明けの作業上の状態（打鍵の再開と受領の有無・フォーカスの遷移・ポインタ）で見る〔2026-11-03 研究者の言・ADR-024・ADR-023 D4・ADR-016〕）。⚠️★★★ **2026-09-01 訂正: 旧「Lv1–2 介入、Lv3–4 は opt-in」は Wall 削除（ADR-015 D1）と段階呼称廃止（ADR-018 D7）で二重に失効。**「1ブロック＝何セッションで条件切替か」はどの設計 doc にも未定義・コード未実装。
- **【未確定（現ポリシーは実装準拠）】Phase 3 の nudge/defer 割付（70/30）**: 設計 doc 上も「例：70/30」の例示どまり、
  最小介入機会数の定義なし。MRT の micro-randomization はコード未実装。現状の intervention.rs は決定論ポリシー：
  Nudge need≥0.60、Opportunity しきい値 nudge≥0.35、Nudge cooldown 10分・
  daily cap 6、recent dismiss 20分、idle≥180秒で介入全停止（実測 2026-09-01: `intervention.rs:3-12`）。
  ⚠️★★★ **2026-09-01 訂正 —— 旧文の Wall 系 3 群（need≥0.70 累積30秒 / opp≥0.45 / cooldown 60分・daily cap 1）は
  存在しない定数である**（ADR-015 D1 が「Wall 閾値 6 種」ごと削除した）。
  ★ **Nudge 側の 5 定数は実測と一致していた**ので、そこは変えていない。
- **【設計確定→要実装】夜間 Outdoor 無効化と未成年の保護者同意**: 検証設計で確定（22:00–6:00 は Physical Anchor の
  Outdoor を無効化し Indoor へ縮退、未成年は保護者同意と安全な実施条件を別途）。コード未実装。被験者 ID は
  P000＝開発者本人／P001–P005＝外部、同意は汎用オプトイン＋匿名化のみ整備済み。
- **【実装準拠】gse-cohort の判定境界**（cohort.rs cohort_verdict、優先順）: (1) 主指標被験者ゼロ→DataInsufficient、
  (2) 提示ランダムプローブ0件→DataInsufficient、(3) PreReg-1 ビネット通過率<0.80→Inconclusive、
  (4) PreReg-2 測定法 Kill（全体回答率<0.80 または 2人以上<0.70）→Kill、(5) PreReg-5 充足被験者ゼロ→DataInsufficient、
  (6) モデルゲート：充足被験者が一部のみなら Go 昇格させず Inconclusive。モデルゲートは Go＝C-index中央値≥0.65 かつ
  全員>0.55、Kill＝中央値≤0.55 または 2人以上≤0.50、いずれも満たさなければ Inconclusive。
- **【実装なし→要確定】Stage 2 昇格判定**: リポジトリに未実装（現状 Stage 1 ルールベース HMM、**HMM_VERSION=0.5.0**。⚠️ **2026-09-01 訂正: 旧文は 0.4.0**。実測 `engine.rs:58`）。
  「約50セッション・+3%」はデッキの参考値どまりで、M5 の昇格判定として別途定義・実装・適用が必要。

---

## 参考文献（本書内番号）

> 中央書誌は `docs/references.md`（P/V 名前空間）。以下は .docx 原文の番号を保持したもの。

- [1] Pejovic, V. et al. (2015). Mobile-Based Experience Sampling for Behaviour Research. arXiv:1508.03725
- [2] Sahu, N. K. et al. (2025). Real-World Receptivity to Adaptive Mental Health Interventions. arXiv:2508.02817
- [3] Compliance and Retention With the ESM Over the Continuum of Severe Mental Disorders: Meta-Analysis. PMC6925392
- [3r] Dziak, J. J. & Nahum-Shani, I. (2025). Constructing Evidence-Based Tailoring Variables for Adaptive Interventions. arXiv:2506.03054
- [4] Qian, T. et al. (2021). The Micro-Randomized Trial for Developing Digital Interventions. arXiv:2107.03544
- [5] Crotti, R. et al. (2026). Hylog: A Hybrid Approach to Logging Text Production in Non-alphabetic Scripts. arXiv:2601.17753
- [8] Oppezzo, M. & Schwartz, D. L. (2014). Give your ideas some legs. J. Exp. Psychol. LMC 40(4):1142. doi:10.1037/a0036577
- [9] Bratman, G. N. et al. (2015). Nature experience reduces rumination... PNAS 112(28):8567. doi:10.1073/pnas.1510459112
- [10] Schwarzer, R. & Jerusalem, M. (1995). Generalized Self-Efficacy Scale.
- [11] Collins, G. S. et al. (2016). Sample size considerations for the external validation of a multivariable prognostic model. Stat. Med. 35:214.
- [11r] Hart, S. G. & Staveland, L. E. (1988). Development of NASA-TLX.
- [12] Jinks, R. C. et al. (2015). Discrimination-based sample size calculations for prognostic models for time-to-event data. PMC4603804.
- [15] Google Workspace Help — How Google protects your organization's security and privacy.
- [16] Dropbox Help — How to create and manage Dropbox file requests.
- [17] Dropbox Help — Dropbox account safety.

---

## 改訂予定（Post-Phase1・提案・未承認）

> ⚠️ **本節は提案であり、本体（§0–§7）には未反映**。反映の前提は (1) Phase1 完了、(2) Epic 0（リポジトリ実態調査）、
> (3) 研究者承認、(4) `GSE_Post_Phase1_Improvement_Design_v0.1.md` の docs/ SSOT 昇格。
> **`docs/preregistration-v0.3.md` の凍結（PreReg-1..8・GATE1–3 の合否基準）は改訂対象外**——変えるのは
> 「Phase1.5 以降にどのゲートを新設し、どの段でどのビルドのデータを使うか」の**追加**のみで、
> Phase1 の合否基準そのものには触れない（forking paths 排除。6/28 バージョンカット宣言と同じ境界の引き方）。

### 改訂の根拠

- Phase1 の参加動機の弱さ・タスク不一致・需要と研究負担の混同（`GSE_Post_Phase1_Improvement_Design_v0.1.md` §1）。
- 理論接地を「機会保存」に確定（`docs/research-positioning.md` §1・2026-07-24）。学習効果は将来トラックへ分離。
- deep-research 3ラウンドの実証判定（`docs/literature/20260723-*` / `20260724-*`）:
  Gate D の桁が確定（30日継続率 中央値 3.3% [V41]、登録経路が支配 44 vs 4日 [V42]）、
  ナッジ・実行意図は出版バイアス補正で縮小 [V40][P21]、`none`/`defer` 第一級化に実証的先行例 [V43]。

### マイルストーンの改訂案（本体 §2 の差分）

| 現行 | 改訂後 | 変更の性質 |
|---|---|---|
| M0–M2（基盤・Phase1a・Phase1b） | **変更なし**（Phase1 closeout として凍結） | — |
| — | **M2.5 Phase 1.5 Task Ecology & Demand Discovery**（新規・6–10名・通常作業・原則介入なし・半構造化インタビュー） | **挿入** |
| M3 Phase2 Y 価値 (AB/BA) | **Phase 2A Adapter Feasibility (Gate S) / 2B Domain-local X1 / 2C Y Value Test** に分割 | **1→3 に分割** |
| M4 Phase3 X2 (MRT) | 維持。**Physical Anchor を別実験に分離**（⚠️ **2026-09-01: 旧案の「Wall /」は ADR-015 D1 で削除済みにつき分離対象から外す**）| スコープ分割 |
| M5 通算再推定・総括 | 維持 + **Phase 4 Cross-domain Transfer** を末尾追加 | 追加 |

### ゲート体系の拡張案（本体 §1 の追加・PreReg は不変）

現行 GATE1–3 に加え、**Phase 1.5 以降にのみ適用される新規ゲート**を追加（Phase1 には遡及しない）:

- **Gate D（Demand・新規）**: 自発的初回/再利用・7日以内再利用・next-week willingness・研究参加外での利用意向。
  ⚠️ 継続率の閾値は in-the-wild ベンチ（30日継続率 中央値 3.3% [V41]・継続中央値 5.5日 [V42]）を**桁の prior**
  として設定し、試験由来のコンプライアンス前提で高く置かない。効果量を閾値に直接代入しない。
- **Gate S（Sensing・新規）**: イベント取得成功率・欠損率・OS/アプリ差・遅延・CPU/メモリ・内容漏洩ゼロ・replay 可否。
- **Gate H（Harm・新規・拒否権）**: annoyance・tension・autonomy loss・false-positive cost・emergency unlock・
  interruption・early exit・perceived surveillance。**Gate H が悪化した場合、X1 が Go でも介入機能は Go としない**
  （＝ゲート依存が従来の X1 単線から分岐する）。

### 判断が必要な点（本体昇格前に決める）

- Phase 1.5 挿入で後段が押す。半年枠維持ならスコープ縮小、スコープ維持なら期間延長（研究者判断）。
  推奨は **Phase 2C（Y 価値）を後送りし Phase 2A/2B を優先**（需要・タスク適合の未確認のまま介入価値を測っても
  解釈困難なため）。
- Accountability Extension（改善設計書 §1.3/§4）と Agentic Coding Adapter B の proxy 妥当性（§3.3）は
  **deep-research 3ラウンドで確定証拠ゼロ**＝現時点でエビデンスに基づけない。専用サーヴェイの後に採否を決める。
